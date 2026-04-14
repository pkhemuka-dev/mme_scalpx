"""
app/mme_scalpx/core/clock.py

Canonical clock and market-session abstractions for the ScalpX MME project.

Purpose
-------
This module owns:
- the canonical time interface for live and replay modes
- wall time vs monotonic time separation
- deterministic replay clock progression
- IST market-session helpers
- common time conversion utilities used across the system
- explicit process-global clock lifecycle management

This module does NOT own:
- runtime settings loading
- strategy logic
- exchange holiday calendars
- Redis naming contracts
- serialization / transport envelope logic
- startup composition

Core design rules
-----------------
- Use wall time for Redis-visible timestamps, event timestamps, health payloads,
  logs, and stream envelopes.
- Use monotonic time for elapsed checks, deadlines, cooldowns, stale detection,
  lock refresh, and timeout logic.
- Replay progression must be explicit and deterministic.
- The process-global clock must be initialized by main.py.
- Market session helpers are timezone-aware and based on IST.
- Holiday-specific closure logic should be layered elsewhere if needed.

Important replay rule
---------------------
ReplayClock.sleep() is ONLY for optional real-world throttling. It never
advances logical replay time. Replay time must move only through explicit
advance_* or set_* operations controlled by the replay driver.

Timing contract
---------------
- Canonical transport and system time unit is epoch nanoseconds.
- Millisecond and second helpers are derived convenience helpers only.
- Field names outside this module should use explicit unit suffixes such as
  *_ns or *_ms.
"""

from __future__ import annotations

import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime, time as dtime, timedelta, timezone
from typing import Final
from zoneinfo import ZoneInfo

from .validators import require, require_bool, require_float, require_int

# ============================================================================
# Time constants
# ============================================================================

UTC: Final[timezone] = timezone.utc
IST: Final[ZoneInfo] = ZoneInfo("Asia/Kolkata")
EPOCH_UTC: Final[datetime] = datetime(1970, 1, 1, tzinfo=UTC)

NS_PER_US: Final[int] = 1_000
US_PER_MS: Final[int] = 1_000
NS_PER_MS: Final[int] = 1_000_000
MS_PER_SEC: Final[int] = 1_000
NS_PER_SEC: Final[int] = 1_000_000_000
SEC_PER_MIN: Final[int] = 60
MIN_PER_HOUR: Final[int] = 60
HOUR_PER_DAY: Final[int] = 24

DEFAULT_ENTRY_CUTOFF_MINUTES_BEFORE_CLOSE: Final[int] = 15
DEFAULT_MANAGEMENT_ONLY_MINUTES_BEFORE_CLOSE: Final[int] = 5

MARKET_PHASE_CLOSED: Final[str] = "CLOSED"
MARKET_PHASE_PRE_OPEN: Final[str] = "PRE_OPEN"
MARKET_PHASE_REGULAR: Final[str] = "REGULAR"
MARKET_PHASE_ENTRY_BLOCKED: Final[str] = "ENTRY_BLOCKED"
MARKET_PHASE_MANAGEMENT_ONLY: Final[str] = "MANAGEMENT_ONLY"
MARKET_PHASE_POST_CLOSE: Final[str] = "POST_CLOSE"


# ============================================================================
# Exceptions
# ============================================================================


class ClockError(ValueError):
    """Base error for clock-related failures."""


class InvalidTimestampError(ClockError):
    """Raised when a timestamp or datetime value is invalid."""


class ReplayClockError(ClockError):
    """Raised when replay clock progression or state is invalid."""


class ClockInitializationError(ClockError):
    """Raised when the process-global clock lifecycle is used incorrectly."""


# ============================================================================
# Local validator wrappers
# Keeps ClockError as the module-facing exception contract.
# ============================================================================


def _wrap_validation(error_cls: type[Exception], fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as exc:  # pragma: no cover - defensive wrapper
        if isinstance(exc, error_cls):
            raise
        raise error_cls(str(exc)) from exc


def _require(condition: bool, message: str) -> None:
    _wrap_validation(ClockError, require, condition, message)


def _require_bool(value: bool, *, field_name: str) -> bool:
    return _wrap_validation(ClockError, require_bool, value, field_name=field_name)


def _require_int(
    value: int,
    *,
    field_name: str,
    min_value: int | None = None,
) -> int:
    return _wrap_validation(
        ClockError,
        require_int,
        value,
        field_name=field_name,
        min_value=min_value,
    )


def _require_non_negative_int(value: int, *, field_name: str) -> int:
    return _require_int(value, field_name=field_name, min_value=0)


def _require_positive_int(value: int, *, field_name: str) -> int:
    return _require_int(value, field_name=field_name, min_value=1)


def _require_float(
    value: float | int,
    *,
    field_name: str,
    min_value: float | None = None,
    strictly_positive: bool = False,
) -> float:
    return _wrap_validation(
        ClockError,
        require_float,
        value,
        field_name=field_name,
        min_value=min_value,
        strictly_positive=strictly_positive,
    )


def _require_non_negative_float(value: float | int, *, field_name: str) -> float:
    return _require_float(value, field_name=field_name, min_value=0.0)


def _require_positive_float(value: float | int, *, field_name: str) -> float:
    return _require_float(value, field_name=field_name, strictly_positive=True)


def _require_date(value: date, *, field_name: str) -> date:
    if not isinstance(value, date):
        raise ClockError(f"{field_name} must be date, got {type(value).__name__}")
    return value


def _require_time(value: dtime, *, field_name: str) -> dtime:
    if not isinstance(value, dtime):
        raise ClockError(f"{field_name} must be datetime.time, got {type(value).__name__}")
    return value


def _require_timezone_aware_datetime(value: datetime, *, field_name: str) -> datetime:
    if not isinstance(value, datetime):
        raise InvalidTimestampError(
            f"{field_name} must be datetime, got {type(value).__name__}"
        )
    if value.tzinfo is None or value.utcoffset() is None:
        raise InvalidTimestampError(f"{field_name} must be timezone-aware")
    return value


def _require_ist_datetime(value: datetime, *, field_name: str) -> datetime:
    return _require_timezone_aware_datetime(value, field_name=field_name).astimezone(IST)


# ============================================================================
# Conversion helpers
# ============================================================================


def ns_to_us(value_ns: int) -> int:
    return _require_non_negative_int(value_ns, field_name="value_ns") // NS_PER_US


def ns_to_ms(value_ns: int) -> int:
    return _require_non_negative_int(value_ns, field_name="value_ns") // NS_PER_MS


def us_to_ns(value_us: int) -> int:
    return _require_non_negative_int(value_us, field_name="value_us") * NS_PER_US


def ms_to_ns(value_ms: int) -> int:
    return _require_non_negative_int(value_ms, field_name="value_ms") * NS_PER_MS


def sec_to_ms(value_sec: int | float) -> int:
    value = _require_non_negative_float(value_sec, field_name="value_sec")
    return int(value * MS_PER_SEC)


def sec_to_ns(value_sec: int | float) -> int:
    value = _require_non_negative_float(value_sec, field_name="value_sec")
    return int(value * NS_PER_SEC)


def ms_to_sec(value_ms: int) -> float:
    return _require_non_negative_int(value_ms, field_name="value_ms") / MS_PER_SEC


def ns_to_sec(value_ns: int) -> float:
    return _require_non_negative_int(value_ns, field_name="value_ns") / NS_PER_SEC


def aware_datetime_to_epoch_ns(value: datetime) -> int:
    dt = _require_timezone_aware_datetime(value, field_name="value").astimezone(UTC)
    delta = dt - EPOCH_UTC
    return (
        (
            delta.days * HOUR_PER_DAY * MIN_PER_HOUR * SEC_PER_MIN
            + delta.seconds
        )
        * NS_PER_SEC
        + delta.microseconds * NS_PER_US
    )


def aware_datetime_to_epoch_ms(value: datetime) -> int:
    return ns_to_ms(aware_datetime_to_epoch_ns(value))


def epoch_ns_to_utc_datetime(value_ns: int) -> datetime:
    checked = _require_non_negative_int(value_ns, field_name="value_ns")
    seconds, nanos = divmod(checked, NS_PER_SEC)
    microseconds = nanos // NS_PER_US
    return datetime.fromtimestamp(seconds, tz=UTC).replace(microsecond=microseconds)


def epoch_ns_to_ist_datetime(value_ns: int) -> datetime:
    return epoch_ns_to_utc_datetime(value_ns).astimezone(IST)


def utc_now_datetime() -> datetime:
    return datetime.now(tz=UTC)


def ist_now_datetime() -> datetime:
    return datetime.now(tz=IST)


def combine_ist(trading_date_ist: date, wall_clock_time_ist: dtime) -> datetime:
    _require_date(trading_date_ist, field_name="trading_date_ist")
    _require_time(wall_clock_time_ist, field_name="wall_clock_time_ist")
    return datetime.combine(trading_date_ist, wall_clock_time_ist, tzinfo=IST)


# ============================================================================
# Clock snapshot
# ============================================================================


@dataclass(frozen=True, slots=True)
class ClockSnapshot:
    """
    Atomic snapshot of both wall and monotonic time.

    Fields
    ------
    wall_time_ns:
        Epoch nanoseconds for external/system-visible timestamps.
    monotonic_ns:
        Monotonic nanoseconds for elapsed/deadline calculations.
    """

    wall_time_ns: int
    monotonic_ns: int

    def __post_init__(self) -> None:
        _require_non_negative_int(self.wall_time_ns, field_name="wall_time_ns")
        _require_non_negative_int(self.monotonic_ns, field_name="monotonic_ns")

    @property
    def wall_time_ms(self) -> int:
        return ns_to_ms(self.wall_time_ns)

    @property
    def wall_time_utc(self) -> datetime:
        return epoch_ns_to_utc_datetime(self.wall_time_ns)

    @property
    def wall_time_ist(self) -> datetime:
        return epoch_ns_to_ist_datetime(self.wall_time_ns)


# ============================================================================
# Base clock contract
# ============================================================================


class BaseClock(ABC):
    """Canonical clock interface for live and replay modes."""

    @property
    @abstractmethod
    def is_replay(self) -> bool:
        """Return True only for replay clocks."""

    @property
    def is_live(self) -> bool:
        return not self.is_replay

    @abstractmethod
    def now(self) -> ClockSnapshot:
        """Return an atomic snapshot of wall and monotonic time."""

    @abstractmethod
    def sleep(self, seconds: float) -> None:
        """
        Sleep in real time.

        LiveClock.sleep() sleeps normally.
        ReplayClock.sleep() only throttles real execution and never advances
        logical replay time.
        """

    def wall_time_ns(self) -> int:
        return self.now().wall_time_ns

    def monotonic_ns(self) -> int:
        return self.now().monotonic_ns

    def wall_time_ms(self) -> int:
        return self.now().wall_time_ms

    def wall_time_utc(self) -> datetime:
        return self.now().wall_time_utc

    def wall_time_ist(self) -> datetime:
        return self.now().wall_time_ist

    def elapsed_ns_since(self, monotonic_start_ns: int) -> int:
        start = _require_non_negative_int(
            monotonic_start_ns,
            field_name="monotonic_start_ns",
        )
        now_ns = self.monotonic_ns()
        if now_ns < start:
            raise ClockError(
                f"current monotonic_ns {now_ns} is behind start {start}"
            )
        return now_ns - start

    def elapsed_ms_since(self, monotonic_start_ns: int) -> int:
        return ns_to_ms(self.elapsed_ns_since(monotonic_start_ns))

    def elapsed_sec_since(self, monotonic_start_ns: int) -> float:
        return ns_to_sec(self.elapsed_ns_since(monotonic_start_ns))

    def deadline_passed(self, monotonic_deadline_ns: int) -> bool:
        deadline = _require_non_negative_int(
            monotonic_deadline_ns,
            field_name="monotonic_deadline_ns",
        )
        return self.monotonic_ns() >= deadline

    def monotonic_deadline_after_ns(self, delta_ns: int) -> int:
        delta = _require_non_negative_int(delta_ns, field_name="delta_ns")
        return self.monotonic_ns() + delta

    def monotonic_deadline_after_ms(self, delta_ms: int) -> int:
        delta = _require_non_negative_int(delta_ms, field_name="delta_ms")
        return self.monotonic_ns() + ms_to_ns(delta)

    def monotonic_deadline_after_sec(self, delta_sec: int | float) -> int:
        delta = _require_non_negative_float(delta_sec, field_name="delta_sec")
        return self.monotonic_ns() + sec_to_ns(delta)


# ============================================================================
# Live clock
# ============================================================================


class LiveClock(BaseClock):
    """Clock backed by system wall and monotonic time."""

    @property
    def is_replay(self) -> bool:
        return False

    def now(self) -> ClockSnapshot:
        return ClockSnapshot(
            wall_time_ns=time.time_ns(),
            monotonic_ns=time.monotonic_ns(),
        )

    def sleep(self, seconds: float) -> None:
        delay = _require_non_negative_float(seconds, field_name="seconds")
        if delay == 0.0:
            return
        time.sleep(delay)


# ============================================================================
# Replay clock
# ============================================================================


class ReplayClock(BaseClock):
    """
    Deterministic replay clock.

    Logical replay time is advanced explicitly by the replay driver.
    Real sleeping is optional and only used to throttle execution speed.
    """

    def __init__(
        self,
        *,
        start_wall_time_ns: int,
        start_monotonic_ns: int = 0,
        replay_speed: float = 1.0,
        sleep_floor_ms: int = 0,
        strict_monotonicity: bool = True,
    ) -> None:
        self._wall_time_ns = _require_non_negative_int(
            start_wall_time_ns,
            field_name="start_wall_time_ns",
        )
        self._monotonic_ns = _require_non_negative_int(
            start_monotonic_ns,
            field_name="start_monotonic_ns",
        )
        self._replay_speed = _require_positive_float(
            replay_speed,
            field_name="replay_speed",
        )
        self._sleep_floor_ms = _require_non_negative_int(
            sleep_floor_ms,
            field_name="sleep_floor_ms",
        )
        self._strict_monotonicity = _require_bool(
            strict_monotonicity,
            field_name="strict_monotonicity",
        )
        self._lock = threading.RLock()

    @property
    def is_replay(self) -> bool:
        return True

    @property
    def replay_speed(self) -> float:
        return self._replay_speed

    @property
    def sleep_floor_ms(self) -> int:
        return self._sleep_floor_ms

    @property
    def strict_monotonicity(self) -> bool:
        return self._strict_monotonicity

    def now(self) -> ClockSnapshot:
        with self._lock:
            return ClockSnapshot(
                wall_time_ns=self._wall_time_ns,
                monotonic_ns=self._monotonic_ns,
            )

    def sleep(self, seconds: float) -> None:
        """
        Optionally throttle real-world execution.

        This does NOT advance logical replay time.
        """
        delay = _require_non_negative_float(seconds, field_name="seconds")
        if delay == 0.0 and self._sleep_floor_ms == 0:
            return

        effective_delay = max(delay, ms_to_sec(self._sleep_floor_ms))
        throttled_delay = effective_delay / self._replay_speed
        if throttled_delay > 0.0:
            time.sleep(throttled_delay)

    def set_wall_time_ns(self, wall_time_ns: int) -> int:
        target = _require_non_negative_int(wall_time_ns, field_name="wall_time_ns")
        with self._lock:
            if target < self._wall_time_ns:
                if self._strict_monotonicity:
                    raise ReplayClockError(
                        "replay wall time cannot move backward in strict mode: "
                        f"current={self._wall_time_ns}, target={target}"
                    )
                return self._wall_time_ns

            delta = target - self._wall_time_ns
            self._wall_time_ns = target
            self._monotonic_ns += delta
            return self._wall_time_ns

    def set_monotonic_ns(self, monotonic_ns: int) -> int:
        target = _require_non_negative_int(monotonic_ns, field_name="monotonic_ns")
        with self._lock:
            if target < self._monotonic_ns:
                if self._strict_monotonicity:
                    raise ReplayClockError(
                        "replay monotonic time cannot move backward in strict mode: "
                        f"current={self._monotonic_ns}, target={target}"
                    )
                return self._monotonic_ns

            self._monotonic_ns = target
            return self._monotonic_ns

    def set_both_ns(self, *, wall_time_ns: int, monotonic_ns: int) -> ClockSnapshot:
        target_wall = _require_non_negative_int(
            wall_time_ns,
            field_name="wall_time_ns",
        )
        target_mono = _require_non_negative_int(
            monotonic_ns,
            field_name="monotonic_ns",
        )

        with self._lock:
            if self._strict_monotonicity:
                if target_wall < self._wall_time_ns:
                    raise ReplayClockError(
                        "replay wall time cannot move backward in strict mode: "
                        f"current={self._wall_time_ns}, target={target_wall}"
                    )
                if target_mono < self._monotonic_ns:
                    raise ReplayClockError(
                        "replay monotonic time cannot move backward in strict mode: "
                        f"current={self._monotonic_ns}, target={target_mono}"
                    )
            else:
                if target_wall < self._wall_time_ns or target_mono < self._monotonic_ns:
                    return ClockSnapshot(
                        wall_time_ns=self._wall_time_ns,
                        monotonic_ns=self._monotonic_ns,
                    )

            self._wall_time_ns = target_wall
            self._monotonic_ns = target_mono
            return ClockSnapshot(
                wall_time_ns=self._wall_time_ns,
                monotonic_ns=self._monotonic_ns,
            )

    def advance_wall_time_ns(self, delta_ns: int) -> int:
        delta = _require_non_negative_int(delta_ns, field_name="delta_ns")
        with self._lock:
            self._wall_time_ns += delta
            self._monotonic_ns += delta
            return self._wall_time_ns

    def advance_monotonic_ns(self, delta_ns: int) -> int:
        delta = _require_non_negative_int(delta_ns, field_name="delta_ns")
        with self._lock:
            self._monotonic_ns += delta
            return self._monotonic_ns

    def advance_both_ns(self, delta_ns: int) -> ClockSnapshot:
        delta = _require_non_negative_int(delta_ns, field_name="delta_ns")
        with self._lock:
            self._wall_time_ns += delta
            self._monotonic_ns += delta
            return ClockSnapshot(
                wall_time_ns=self._wall_time_ns,
                monotonic_ns=self._monotonic_ns,
            )

    def advance_to_wall_time_ns(self, target_wall_time_ns: int) -> ClockSnapshot:
        target = _require_non_negative_int(
            target_wall_time_ns,
            field_name="target_wall_time_ns",
        )
        with self._lock:
            if target < self._wall_time_ns:
                if self._strict_monotonicity:
                    raise ReplayClockError(
                        "replay wall time cannot move backward in strict mode: "
                        f"current={self._wall_time_ns}, target={target}"
                    )
                return ClockSnapshot(
                    wall_time_ns=self._wall_time_ns,
                    monotonic_ns=self._monotonic_ns,
                )

            delta = target - self._wall_time_ns
            self._wall_time_ns = target
            self._monotonic_ns += delta
            return ClockSnapshot(
                wall_time_ns=self._wall_time_ns,
                monotonic_ns=self._monotonic_ns,
            )

    def advance_to_event_time_ns(self, event_time_ns: int) -> ClockSnapshot:
        """
        Alias for advance_to_wall_time_ns().

        Useful when replay drivers advance from event timestamps.
        """
        return self.advance_to_wall_time_ns(event_time_ns)


# ============================================================================
# Market-session helpers
# ============================================================================


@dataclass(frozen=True, slots=True)
class MarketSessionWindow:
    """
    Generic weekday market session definition in IST.

    This represents a weekday session shape and intentionally does not encode
    holiday-specific closure logic.
    """

    open_time_ist: dtime
    close_time_ist: dtime
    entry_cutoff_minutes_before_close: int = DEFAULT_ENTRY_CUTOFF_MINUTES_BEFORE_CLOSE
    management_only_minutes_before_close: int = (
        DEFAULT_MANAGEMENT_ONLY_MINUTES_BEFORE_CLOSE
    )

    def validate(self) -> None:
        _require_time(self.open_time_ist, field_name="open_time_ist")
        _require_time(self.close_time_ist, field_name="close_time_ist")
        _require_non_negative_int(
            self.entry_cutoff_minutes_before_close,
            field_name="entry_cutoff_minutes_before_close",
        )
        _require_non_negative_int(
            self.management_only_minutes_before_close,
            field_name="management_only_minutes_before_close",
        )

        open_minutes = self.open_time_ist.hour * MIN_PER_HOUR + self.open_time_ist.minute
        close_minutes = (
            self.close_time_ist.hour * MIN_PER_HOUR + self.close_time_ist.minute
        )
        _require(
            close_minutes > open_minutes,
            "close_time_ist must be after open_time_ist",
        )
        _require(
            self.entry_cutoff_minutes_before_close
            >= self.management_only_minutes_before_close,
            "entry_cutoff_minutes_before_close must be >= management_only_minutes_before_close",
        )

        entry_cutoff_dt = datetime.combine(
            date(2000, 1, 1),
            self.close_time_ist,
            tzinfo=IST,
        ) - timedelta(minutes=self.entry_cutoff_minutes_before_close)
        management_only_dt = datetime.combine(
            date(2000, 1, 1),
            self.close_time_ist,
            tzinfo=IST,
        ) - timedelta(minutes=self.management_only_minutes_before_close)
        open_dt = datetime.combine(date(2000, 1, 1), self.open_time_ist, tzinfo=IST)

        _require(
            entry_cutoff_dt >= open_dt,
            "entry cutoff cannot be before market open",
        )
        _require(
            management_only_dt >= open_dt,
            "management-only cutoff cannot be before market open",
        )


@dataclass(frozen=True, slots=True)
class SessionBounds:
    trading_date_ist: date
    open_dt_ist: datetime
    entry_cutoff_dt_ist: datetime
    management_only_dt_ist: datetime
    close_dt_ist: datetime

    def __post_init__(self) -> None:
        _require_date(self.trading_date_ist, field_name="trading_date_ist")
        open_dt = _require_ist_datetime(self.open_dt_ist, field_name="open_dt_ist")
        entry_cutoff_dt = _require_ist_datetime(
            self.entry_cutoff_dt_ist,
            field_name="entry_cutoff_dt_ist",
        )
        management_only_dt = _require_ist_datetime(
            self.management_only_dt_ist,
            field_name="management_only_dt_ist",
        )
        close_dt = _require_ist_datetime(self.close_dt_ist, field_name="close_dt_ist")

        _require(
            open_dt.date() == self.trading_date_ist,
            "open_dt_ist date must match trading_date_ist",
        )
        _require(
            close_dt.date() == self.trading_date_ist,
            "close_dt_ist date must match trading_date_ist",
        )
        _require(
            open_dt <= entry_cutoff_dt <= management_only_dt <= close_dt,
            "session bounds must satisfy open <= entry_cutoff <= management_only <= close",
        )


DEFAULT_NSE_SESSION: Final[MarketSessionWindow] = MarketSessionWindow(
    open_time_ist=dtime(hour=9, minute=15),
    close_time_ist=dtime(hour=15, minute=30),
    entry_cutoff_minutes_before_close=DEFAULT_ENTRY_CUTOFF_MINUTES_BEFORE_CLOSE,
    management_only_minutes_before_close=DEFAULT_MANAGEMENT_ONLY_MINUTES_BEFORE_CLOSE,
)


def is_weekend(trading_date_ist: date) -> bool:
    dt = _require_date(trading_date_ist, field_name="trading_date_ist")
    return dt.weekday() >= 5


def next_weekday(trading_date_ist: date) -> date:
    current = _require_date(trading_date_ist, field_name="trading_date_ist")
    next_date = current + timedelta(days=1)
    while is_weekend(next_date):
        next_date += timedelta(days=1)
    return next_date


def session_bounds_for_date(
    trading_date_ist: date,
    *,
    session: MarketSessionWindow = DEFAULT_NSE_SESSION,
) -> SessionBounds:
    session.validate()
    trade_date = _require_date(trading_date_ist, field_name="trading_date_ist")

    open_dt_ist = combine_ist(trade_date, session.open_time_ist)
    close_dt_ist = combine_ist(trade_date, session.close_time_ist)
    entry_cutoff_dt_ist = close_dt_ist - timedelta(
        minutes=session.entry_cutoff_minutes_before_close
    )
    management_only_dt_ist = close_dt_ist - timedelta(
        minutes=session.management_only_minutes_before_close
    )

    return SessionBounds(
        trading_date_ist=trade_date,
        open_dt_ist=open_dt_ist,
        entry_cutoff_dt_ist=entry_cutoff_dt_ist,
        management_only_dt_ist=management_only_dt_ist,
        close_dt_ist=close_dt_ist,
    )


def market_phase_from_ist_datetime(
    dt_ist: datetime,
    *,
    session: MarketSessionWindow = DEFAULT_NSE_SESSION,
) -> str:
    dt = _require_ist_datetime(dt_ist, field_name="dt_ist")

    if is_weekend(dt.date()):
        return MARKET_PHASE_CLOSED

    bounds = session_bounds_for_date(dt.date(), session=session)

    if dt < bounds.open_dt_ist:
        return MARKET_PHASE_PRE_OPEN
    if dt >= bounds.close_dt_ist:
        return MARKET_PHASE_POST_CLOSE
    if dt >= bounds.management_only_dt_ist:
        return MARKET_PHASE_MANAGEMENT_ONLY
    if dt >= bounds.entry_cutoff_dt_ist:
        return MARKET_PHASE_ENTRY_BLOCKED
    return MARKET_PHASE_REGULAR


def is_regular_market_session_open(
    dt_ist: datetime,
    *,
    session: MarketSessionWindow = DEFAULT_NSE_SESSION,
) -> bool:
    return market_phase_from_ist_datetime(dt_ist, session=session) in {
        MARKET_PHASE_REGULAR,
        MARKET_PHASE_ENTRY_BLOCKED,
        MARKET_PHASE_MANAGEMENT_ONLY,
    }


def can_enter_new_positions(
    dt_ist: datetime,
    *,
    session: MarketSessionWindow = DEFAULT_NSE_SESSION,
) -> bool:
    return market_phase_from_ist_datetime(dt_ist, session=session) == MARKET_PHASE_REGULAR


def is_management_only_phase(
    dt_ist: datetime,
    *,
    session: MarketSessionWindow = DEFAULT_NSE_SESSION,
) -> bool:
    return (
        market_phase_from_ist_datetime(dt_ist, session=session)
        == MARKET_PHASE_MANAGEMENT_ONLY
    )


def next_regular_open_ist(
    dt_ist: datetime,
    *,
    session: MarketSessionWindow = DEFAULT_NSE_SESSION,
) -> datetime:
    dt = _require_ist_datetime(dt_ist, field_name="dt_ist")
    session.validate()

    if not is_weekend(dt.date()):
        bounds_today = session_bounds_for_date(dt.date(), session=session)
        if dt < bounds_today.open_dt_ist:
            return bounds_today.open_dt_ist

    next_date = next_weekday(dt.date())
    return session_bounds_for_date(next_date, session=session).open_dt_ist


def seconds_until_next_regular_open(
    *,
    from_dt_ist: datetime | None = None,
    session: MarketSessionWindow = DEFAULT_NSE_SESSION,
) -> float:
    current = ist_now_datetime() if from_dt_ist is None else from_dt_ist
    current_ist = _require_ist_datetime(current, field_name="from_dt_ist")
    target = next_regular_open_ist(current_ist, session=session)
    delta = target - current_ist
    return max(0.0, delta.total_seconds())


# ============================================================================
# Process-global/default clock lifecycle
# ============================================================================


class _ClockProxy(BaseClock):
    """
    Lazy proxy for the process-global clock.

    This allows callers to import CLOCK safely before main.py initialization,
    while still enforcing explicit initialization through init_clock()/set_clock().
    """

    @property
    def is_replay(self) -> bool:
        return get_clock().is_replay

    def now(self) -> ClockSnapshot:
        return get_clock().now()

    def sleep(self, seconds: float) -> None:
        get_clock().sleep(seconds)


_CLOCK_LOCK: Final[threading.RLock] = threading.RLock()
_CLOCK_INSTANCE: BaseClock | None = None


def set_clock(clock: BaseClock) -> BaseClock:
    if not isinstance(clock, BaseClock):
        raise ClockInitializationError(
            f"clock must be BaseClock, got {type(clock).__name__}"
        )

    global _CLOCK_INSTANCE
    with _CLOCK_LOCK:
        _CLOCK_INSTANCE = clock
        return _CLOCK_INSTANCE


def get_clock() -> BaseClock:
    with _CLOCK_LOCK:
        if _CLOCK_INSTANCE is None:
            raise ClockInitializationError(
                "global clock is not initialized. "
                "Call init_clock(), init_live_clock(), or init_replay_clock() first."
            )
        return _CLOCK_INSTANCE


def clear_clock() -> None:
    global _CLOCK_INSTANCE
    with _CLOCK_LOCK:
        _CLOCK_INSTANCE = None


def init_clock(clock: BaseClock) -> BaseClock:
    """Initialize the process-global clock from an explicit clock instance."""
    return set_clock(clock)


# ============================================================================
# Clock factories / bootstrap helpers
# Parameter-driven only. No settings access is allowed here.
# main.py owns runtime mode selection and replay configuration resolution.
# ============================================================================


def make_live_clock() -> LiveClock:
    return LiveClock()


def make_replay_clock(
    *,
    start_wall_time_ns: int,
    start_monotonic_ns: int = 0,
    replay_speed: float = 1.0,
    sleep_floor_ms: int = 0,
    strict_monotonicity: bool = True,
) -> ReplayClock:
    return ReplayClock(
        start_wall_time_ns=start_wall_time_ns,
        start_monotonic_ns=start_monotonic_ns,
        replay_speed=replay_speed,
        sleep_floor_ms=sleep_floor_ms,
        strict_monotonicity=strict_monotonicity,
    )


def init_live_clock() -> LiveClock:
    clock = make_live_clock()
    set_clock(clock)
    return clock


def init_replay_clock(
    *,
    start_wall_time_ns: int,
    start_monotonic_ns: int = 0,
    replay_speed: float = 1.0,
    sleep_floor_ms: int = 0,
    strict_monotonicity: bool = True,
) -> ReplayClock:
    clock = make_replay_clock(
        start_wall_time_ns=start_wall_time_ns,
        start_monotonic_ns=start_monotonic_ns,
        replay_speed=replay_speed,
        sleep_floor_ms=sleep_floor_ms,
        strict_monotonicity=strict_monotonicity,
    )
    set_clock(clock)
    return clock


def build_clock(
    *,
    replay: bool,
    replay_start_wall_time_ns: int | None = None,
    replay_start_monotonic_ns: int = 0,
    replay_speed: float = 1.0,
    sleep_floor_ms: int = 0,
    strict_monotonicity: bool = True,
) -> BaseClock:
    """
    Canonical project clock factory.

    This function is intentionally parameter-driven only.
    Runtime settings must be loaded by main.py and passed in explicitly.

    Behavior
    --------
    - replay=False returns LiveClock.
    - replay=True returns ReplayClock and requires replay_start_wall_time_ns.
    """
    use_replay = _require_bool(replay, field_name="replay")

    if not use_replay:
        return make_live_clock()

    if replay_start_wall_time_ns is None:
        raise ReplayClockError(
            "replay_start_wall_time_ns is required when building a replay clock"
        )

    return make_replay_clock(
        start_wall_time_ns=replay_start_wall_time_ns,
        start_monotonic_ns=replay_start_monotonic_ns,
        replay_speed=replay_speed,
        sleep_floor_ms=sleep_floor_ms,
        strict_monotonicity=strict_monotonicity,
    )


CLOCK: Final[BaseClock] = _ClockProxy()


__all__ = [
    "BaseClock",
    "CLOCK",
    "ClockError",
    "ClockInitializationError",
    "ClockSnapshot",
    "DEFAULT_ENTRY_CUTOFF_MINUTES_BEFORE_CLOSE",
    "DEFAULT_MANAGEMENT_ONLY_MINUTES_BEFORE_CLOSE",
    "DEFAULT_NSE_SESSION",
    "EPOCH_UTC",
    "HOUR_PER_DAY",
    "IST",
    "InvalidTimestampError",
    "LiveClock",
    "MARKET_PHASE_CLOSED",
    "MARKET_PHASE_ENTRY_BLOCKED",
    "MARKET_PHASE_MANAGEMENT_ONLY",
    "MARKET_PHASE_POST_CLOSE",
    "MARKET_PHASE_PRE_OPEN",
    "MARKET_PHASE_REGULAR",
    "MIN_PER_HOUR",
    "MS_PER_SEC",
    "MarketSessionWindow",
    "NS_PER_MS",
    "NS_PER_SEC",
    "NS_PER_US",
    "ReplayClock",
    "ReplayClockError",
    "SEC_PER_MIN",
    "SessionBounds",
    "US_PER_MS",
    "UTC",
    "aware_datetime_to_epoch_ms",
    "aware_datetime_to_epoch_ns",
    "build_clock",
    "can_enter_new_positions",
    "clear_clock",
    "combine_ist",
    "epoch_ns_to_ist_datetime",
    "epoch_ns_to_utc_datetime",
    "get_clock",
    "init_clock",
    "init_live_clock",
    "init_replay_clock",
    "is_management_only_phase",
    "is_regular_market_session_open",
    "is_weekend",
    "ist_now_datetime",
    "make_live_clock",
    "make_replay_clock",
    "market_phase_from_ist_datetime",
    "ms_to_ns",
    "ms_to_sec",
    "next_regular_open_ist",
    "next_weekday",
    "ns_to_ms",
    "ns_to_sec",
    "ns_to_us",
    "sec_to_ms",
    "sec_to_ns",
    "seconds_until_next_regular_open",
    "session_bounds_for_date",
    "set_clock",
    "us_to_ns",
    "utc_now_datetime",
]