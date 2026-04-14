from __future__ import annotations

"""
app/mme_scalpx/services/risk.py

Independent risk governance layer for ScalpX MME.

Frozen contract
---------------
This module OWNS:
- canonical risk state publication
- canonical risk heartbeat publication
- deterministic entry-veto governance
- realized day PnL tracking from canonical trades ledger
- risk-owned governance command handling from the frozen command surface
- runtime entrypoint run(context)

This module DOES NOT own:
- fills
- orders
- execution truth
- position truth
- strategy signal generation
- startup / composition logic
- alternate runtime roots

Design rules
------------
- risk may block entries, never exits
- execution remains sole position truth
- names.py is the only symbolic source of truth
- redisx.py is the only transport façade
- main.py is the only startup root
- runtime entrypoint is exactly run(context)
- replay-safe and restart-safe

Important freeze rule
---------------------
settings.py does NOT define a typed risk settings section.

This module therefore:
- uses only proven global settings surfaces from settings.py where applicable
- preserves the already-proven risk_* context override surface from the uploaded
  risk lineage:
    risk_timezone_name
    risk_start_hhmm
    risk_end_hhmm
    risk_daily_loss_limit
    risk_cooldown_seconds_after_loss
    risk_max_consecutive_losses
    risk_stale_heartbeat_seconds
    risk_state_publish_interval_seconds
    risk_ledger_block_ms
    risk_command_block_ms
    risk_heartbeat_ttl_ms
    risk_heartbeat_refresh_ms
    risk_require_upstream_heartbeats
    risk_require_execution_healthy
    risk_require_broker_connected
    risk_allow_entry_outside_window
    risk_max_new_lots_default
    risk_max_trades_per_day
- does NOT invent any new typed settings family or dependency factories

Compatibility rule
------------------
The published HASH_STATE_RISK fields remain compatible with existing readers:
- strategy.py reads:
    veto_entries
    degraded_only
    force_flatten
    stale
    cooldown_until_ns
    reason_code
- execution.py reads:
    veto_entries
    max_new_lots
"""

import contextlib
import logging
from dataclasses import dataclass
from datetime import date, datetime, time as dt_time
from typing import Any, Final, Mapping
from zoneinfo import ZoneInfo

from app.mme_scalpx.core import names as N
from app.mme_scalpx.core import redisx as RX
from app.mme_scalpx.core.settings import DEFAULT_HEARTBEAT_TTL_MS, AppSettings, get_settings

LOGGER = logging.getLogger("app.mme_scalpx.services.risk")

DEFAULT_RISK_TIMEZONE_NAME: Final[str] = "Asia/Kolkata"
DEFAULT_RISK_START_HHMM: Final[str] = "09:15"
DEFAULT_RISK_END_HHMM: Final[str] = "15:30"
DEFAULT_RISK_DAILY_LOSS_LIMIT: Final[float] = 1000.0
DEFAULT_RISK_COOLDOWN_SECONDS_AFTER_LOSS: Final[float] = 4.0
DEFAULT_RISK_MAX_CONSECUTIVE_LOSSES: Final[int] = 0
DEFAULT_RISK_STALE_HEARTBEAT_SECONDS: Final[float] = 10.0
DEFAULT_RISK_STATE_PUBLISH_INTERVAL_SECONDS: Final[float] = 0.25
DEFAULT_RISK_LEDGER_BLOCK_MS: Final[int] = 200
DEFAULT_RISK_COMMAND_BLOCK_MS: Final[int] = 1
DEFAULT_RISK_HEARTBEAT_REFRESH_MS: Final[int] = 3_000
DEFAULT_RISK_REQUIRE_UPSTREAM_HEARTBEATS: Final[bool] = True
DEFAULT_RISK_REQUIRE_EXECUTION_HEALTHY: Final[bool] = True
DEFAULT_RISK_REQUIRE_BROKER_CONNECTED: Final[bool] = False
DEFAULT_RISK_ALLOW_ENTRY_OUTSIDE_WINDOW: Final[bool] = False
DEFAULT_RISK_MAX_NEW_LOTS_DEFAULT: Final[int] = 1
DEFAULT_RISK_MAX_TRADES_PER_DAY: Final[int] = 0

DEFAULT_HEALTH_STREAM_MAXLEN: Final[int] = 10_000
DEFAULT_ERROR_STREAM_MAXLEN: Final[int] = 10_000


# =============================================================================
# Exceptions
# =============================================================================


class RiskError(RuntimeError):
    """Base risk governance error."""


class RiskConfigError(RiskError):
    """Raised when runtime config or context is invalid."""


class RiskContractError(RiskError):
    """Raised when incoming stream/state payloads violate the contract."""


# =============================================================================
# Required surface validation
# =============================================================================

_REQUIRED_NAME_EXPORTS: Final[tuple[str, ...]] = (
    "SERVICE_RISK",
    "STREAM_TRADES_LEDGER",
    "STREAM_CMD_MME",
    "STREAM_SYSTEM_HEALTH",
    "STREAM_SYSTEM_ERRORS",
    "HASH_STATE_RISK",
    "HASH_STATE_EXECUTION",
    "HASH_STATE_POSITION_MME",
    "KEY_HEALTH_RISK",
    "KEY_HEALTH_FEATURES",
    "KEY_HEALTH_STRATEGY",
    "KEY_HEALTH_EXECUTION",
    "GROUP_RISK",
    "CMD_PARAMS_RELOAD",
    "CMD_PAUSE_TRADING",
    "CMD_RESUME_TRADING",
    "CMD_FORCE_FLATTEN",
    "CMD_SET_MODE",
    "CONTROL_MODE_NORMAL",
    "CONTROL_MODE_SAFE",
    "CONTROL_MODE_REPLAY",
    "CONTROL_MODE_DISABLED",
    "HEALTH_STATUS_OK",
    "HEALTH_STATUS_WARN",
    "HEALTH_STATUS_ERROR",
    "EXECUTION_MODE_NORMAL",
    "EXECUTION_MODE_EXIT_ONLY",
    "EXECUTION_MODE_DEGRADED",
    "EXECUTION_MODE_FATAL",
    "POSITION_SIDE_FLAT",
    "ENTRY_MODE_UNKNOWN",
)


def _validate_name_surface_or_die() -> None:
    missing = [name for name in _REQUIRED_NAME_EXPORTS if not hasattr(N, name)]
    if missing:
        raise RiskConfigError(
            "risk.py missing required names.py exports: " + ", ".join(sorted(missing))
        )


# =============================================================================
# Small helpers
# =============================================================================


def _as_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def _safe_str(value: Any, default: str = "") -> str:
    out = _as_str(value).strip()
    return out if out else default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value in (None, ""):
            return default
        return int(float(value))
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(value)
    except Exception:
        return default


def _safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    raw = _as_str(value).strip().lower()
    if raw in {"1", "true", "yes", "y", "on"}:
        return True
    if raw in {"0", "false", "no", "n", "off"}:
        return False
    return default


def _decode_mapping(raw: Mapping[Any, Any]) -> dict[str, str]:
    return {_as_str(k): _as_str(v) for k, v in raw.items()}


def _status_to_health(mode: str) -> str:
    if mode == N.EXECUTION_MODE_FATAL:
        return N.HEALTH_STATUS_ERROR
    if mode in {N.EXECUTION_MODE_DEGRADED, N.EXECUTION_MODE_EXIT_ONLY}:
        return N.HEALTH_STATUS_WARN
    return N.HEALTH_STATUS_OK


def _parse_hhmm(value: str, *, field_name: str) -> dt_time:
    raw = _safe_str(value)
    if not raw:
        raise RiskConfigError(f"{field_name} must be HH:MM")
    try:
        hh, mm = raw.split(":")
        return dt_time(hour=int(hh), minute=int(mm))
    except Exception as exc:
        raise RiskConfigError(f"{field_name} must be HH:MM, got {value!r}") from exc


# =============================================================================
# Config / state models
# =============================================================================


@dataclass(frozen=True, slots=True)
class TradingWindow:
    start: dt_time
    end: dt_time

    def contains(self, ts_ns: int, tz: ZoneInfo) -> bool:
        local_dt = datetime.fromtimestamp(ts_ns / 1_000_000_000, tz=tz)
        local_t = local_dt.time()
        return self.start <= local_t < self.end


@dataclass(frozen=True, slots=True)
class RiskThresholds:
    daily_loss_limit: float
    cooldown_seconds_after_loss: float
    max_consecutive_losses: int
    stale_heartbeat_seconds: float
    state_publish_interval_seconds: float
    ledger_block_ms: int
    command_block_ms: int
    heartbeat_ttl_ms: int
    heartbeat_refresh_ms: int
    require_upstream_heartbeats: bool
    require_execution_healthy: bool
    require_broker_connected: bool
    allow_entry_outside_window: bool
    max_new_lots_default: int
    max_trades_per_day: int

    @classmethod
    def from_context(cls, context: Any) -> "RiskThresholds":
        return cls(
            daily_loss_limit=float(
                getattr(context, "risk_daily_loss_limit", DEFAULT_RISK_DAILY_LOSS_LIMIT)
            ),
            cooldown_seconds_after_loss=float(
                getattr(
                    context,
                    "risk_cooldown_seconds_after_loss",
                    DEFAULT_RISK_COOLDOWN_SECONDS_AFTER_LOSS,
                )
            ),
            max_consecutive_losses=int(
                getattr(
                    context,
                    "risk_max_consecutive_losses",
                    DEFAULT_RISK_MAX_CONSECUTIVE_LOSSES,
                )
            ),
            stale_heartbeat_seconds=float(
                getattr(
                    context,
                    "risk_stale_heartbeat_seconds",
                    DEFAULT_RISK_STALE_HEARTBEAT_SECONDS,
                )
            ),
            state_publish_interval_seconds=float(
                getattr(
                    context,
                    "risk_state_publish_interval_seconds",
                    DEFAULT_RISK_STATE_PUBLISH_INTERVAL_SECONDS,
                )
            ),
            ledger_block_ms=int(
                getattr(context, "risk_ledger_block_ms", DEFAULT_RISK_LEDGER_BLOCK_MS)
            ),
            command_block_ms=int(
                getattr(context, "risk_command_block_ms", DEFAULT_RISK_COMMAND_BLOCK_MS)
            ),
            heartbeat_ttl_ms=int(
                getattr(context, "risk_heartbeat_ttl_ms", int(DEFAULT_HEARTBEAT_TTL_MS))
            ),
            heartbeat_refresh_ms=int(
                getattr(
                    context,
                    "risk_heartbeat_refresh_ms",
                    DEFAULT_RISK_HEARTBEAT_REFRESH_MS,
                )
            ),
            require_upstream_heartbeats=bool(
                getattr(
                    context,
                    "risk_require_upstream_heartbeats",
                    DEFAULT_RISK_REQUIRE_UPSTREAM_HEARTBEATS,
                )
            ),
            require_execution_healthy=bool(
                getattr(
                    context,
                    "risk_require_execution_healthy",
                    DEFAULT_RISK_REQUIRE_EXECUTION_HEALTHY,
                )
            ),
            require_broker_connected=bool(
                getattr(
                    context,
                    "risk_require_broker_connected",
                    DEFAULT_RISK_REQUIRE_BROKER_CONNECTED,
                )
            ),
            allow_entry_outside_window=bool(
                getattr(
                    context,
                    "risk_allow_entry_outside_window",
                    DEFAULT_RISK_ALLOW_ENTRY_OUTSIDE_WINDOW,
                )
            ),
            max_new_lots_default=int(
                getattr(
                    context,
                    "risk_max_new_lots_default",
                    DEFAULT_RISK_MAX_NEW_LOTS_DEFAULT,
                )
            ),
            max_trades_per_day=int(
                getattr(
                    context,
                    "risk_max_trades_per_day",
                    DEFAULT_RISK_MAX_TRADES_PER_DAY,
                )
            ),
        )

    def validate(self) -> None:
        if self.daily_loss_limit <= 0.0:
            raise RiskConfigError("risk_daily_loss_limit must be > 0")
        if self.cooldown_seconds_after_loss < 0.0:
            raise RiskConfigError("risk_cooldown_seconds_after_loss must be >= 0")
        if self.max_consecutive_losses < 0:
            raise RiskConfigError("risk_max_consecutive_losses must be >= 0")
        if self.stale_heartbeat_seconds <= 0.0:
            raise RiskConfigError("risk_stale_heartbeat_seconds must be > 0")
        if self.state_publish_interval_seconds <= 0.0:
            raise RiskConfigError("risk_state_publish_interval_seconds must be > 0")
        if self.ledger_block_ms < 0:
            raise RiskConfigError("risk_ledger_block_ms must be >= 0")
        if self.command_block_ms < 0:
            raise RiskConfigError("risk_command_block_ms must be >= 0")
        if self.heartbeat_ttl_ms <= 0:
            raise RiskConfigError("risk_heartbeat_ttl_ms must be > 0")
        if self.heartbeat_refresh_ms <= 0:
            raise RiskConfigError("risk_heartbeat_refresh_ms must be > 0")
        if self.max_new_lots_default < 0:
            raise RiskConfigError("risk_max_new_lots_default must be >= 0")
        if self.max_trades_per_day < 0:
            raise RiskConfigError("risk_max_trades_per_day must be >= 0")


@dataclass(frozen=True, slots=True)
class RiskConfig:
    service_name: str
    instance_id: str
    consumer_name: str
    timezone_name: str
    trading_window: TradingWindow
    thresholds: RiskThresholds
    replay_mode: bool

    @classmethod
    def from_context(cls, context: Any) -> "RiskConfig":
        settings = getattr(context, "settings", None) or get_settings()
        if not isinstance(settings, AppSettings):
            raise RiskConfigError(
                "risk requires context.settings or get_settings() returning AppSettings"
            )

        timezone_name = _safe_str(
            getattr(context, "risk_timezone_name", DEFAULT_RISK_TIMEZONE_NAME)
        )
        start_hhmm = _safe_str(
            getattr(context, "risk_start_hhmm", DEFAULT_RISK_START_HHMM)
        )
        end_hhmm = _safe_str(
            getattr(context, "risk_end_hhmm", DEFAULT_RISK_END_HHMM)
        )

        cfg = cls(
            service_name=str(getattr(context, "service_name", N.SERVICE_RISK)),
            instance_id=str(getattr(context, "instance_id", "")),
            consumer_name=str(getattr(context, "consumer_name", "")),
            timezone_name=timezone_name,
            trading_window=TradingWindow(
                start=_parse_hhmm(start_hhmm, field_name="risk_start_hhmm"),
                end=_parse_hhmm(end_hhmm, field_name="risk_end_hhmm"),
            ),
            thresholds=RiskThresholds.from_context(context),
            replay_mode=bool(getattr(context, "is_replay", settings.runtime.is_replay)),
        )
        cfg.thresholds.validate()

        if not cfg.instance_id:
            raise RiskConfigError("risk requires non-empty instance_id")
        if not cfg.consumer_name:
            raise RiskConfigError("risk requires non-empty consumer_name")
        return cfg


@dataclass(slots=True)
class DailyRiskLedger:
    trading_day: str
    realized_pnl: float = 0.0
    loss_count: int = 0
    win_count: int = 0
    consecutive_losses: int = 0
    trades_today: int = 0
    last_trade_id: str = ""
    last_trade_stream_id: str = "0-0"
    last_trade_ts_ns: int = 0

    def reset_for_day(self, trading_day: str) -> None:
        self.trading_day = trading_day
        self.realized_pnl = 0.0
        self.loss_count = 0
        self.win_count = 0
        self.consecutive_losses = 0
        self.trades_today = 0
        self.last_trade_id = ""
        self.last_trade_stream_id = "0-0"
        self.last_trade_ts_ns = 0


@dataclass(slots=True)
class RiskRuntimeState:
    control_mode: str = N.CONTROL_MODE_NORMAL
    manual_pause: bool = False
    manual_pause_reason: str = ""
    force_flatten_requested: bool = False
    params_reload_requested: bool = False
    veto_entries: bool = False
    veto_reason: str = ""
    broker_connected: bool = True
    execution_healthy: bool = True
    upstream_healthy: bool = True
    trading_window_ok: bool = True
    position_open: bool = False
    cooldown_until_ns: int = 0
    updated_at_ns: int = 0
    last_state_publish_ns: int = 0
    last_heartbeat_ns: int = 0

    def cooldown_active(self, now_ns: int) -> bool:
        return now_ns < self.cooldown_until_ns

    def set_cooldown_until(self, until_ns: int) -> None:
        if until_ns > self.cooldown_until_ns:
            self.cooldown_until_ns = until_ns


# =============================================================================
# Risk service
# =============================================================================


class RiskService:
    def __init__(
        self,
        *,
        redis_client: Any,
        clock: Any,
        shutdown: Any,
        config: RiskConfig,
        logger: logging.Logger | None = None,
    ) -> None:
        self.redis = redis_client
        self.clock = clock
        self.shutdown = shutdown
        self.cfg = config
        self.log = logger or LOGGER
        self.tz = ZoneInfo(config.timezone_name)

        self.runtime = RiskRuntimeState()
        self.ledger = DailyRiskLedger(
            trading_day=self._current_trading_day(self.now_ns())
        )

        self._validate_runtime_contract()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> int:
        self._bootstrap()
        try:
            self._run_forever()
        finally:
            self._publish_shutdown_heartbeat()
        return 0

    def _bootstrap(self) -> None:
        RX.ensure_consumer_group(
            N.STREAM_TRADES_LEDGER,
            N.GROUP_RISK,
            start_id=RX.DEFAULT_GROUP_START_ID,
            mkstream=True,
            client=self.redis,
        )
        RX.ensure_consumer_group(
            N.STREAM_CMD_MME,
            N.GROUP_RISK,
            start_id=RX.DEFAULT_GROUP_START_ID,
            mkstream=True,
            client=self.redis,
        )

        now_ns = self.now_ns()
        self.runtime.updated_at_ns = now_ns
        self._refresh_dependency_state(now_ns)
        self._recompute_veto(now_ns)
        self._publish_state(now_ns, force=True)
        self._publish_heartbeat(now_ns, force=True)
        self._publish_health_event(
            status=N.HEALTH_STATUS_OK,
            event="risk_bootstrap_complete",
            detail="risk_initialized",
            ts_ns=now_ns,
        )

    def _run_forever(self) -> None:
        while not self.shutdown.is_set():
            now_ns = self.now_ns()
            self._roll_trading_day_if_needed(now_ns)

            progressed = False
            progressed = self._process_trade_ledger(now_ns) or progressed
            progressed = self._process_control_commands(now_ns) or progressed

            self._refresh_dependency_state(now_ns)
            self._recompute_veto(now_ns)
            self._publish_state(now_ns, force=progressed)
            self._publish_heartbeat(now_ns, force=progressed)

            if not progressed:
                sleep_s = max(
                    self.cfg.thresholds.state_publish_interval_seconds,
                    0.05,
                )
                self.shutdown.wait(sleep_s)

    def _validate_runtime_contract(self) -> None:
        if self.redis is None:
            raise RiskConfigError("risk requires redis client")
        if self.clock is None or not hasattr(self.clock, "wall_time_ns"):
            raise RiskConfigError("risk requires context.clock.wall_time_ns()")
        if self.shutdown is None or not hasattr(self.shutdown, "is_set") or not hasattr(self.shutdown, "wait"):
            raise RiskConfigError("risk requires context.shutdown.is_set()/wait()")
        if not self.cfg.instance_id:
            raise RiskConfigError("risk requires non-empty instance_id")
        if not self.cfg.consumer_name:
            raise RiskConfigError("risk requires non-empty consumer_name")
        if not RX.ping_redis(client=self.redis):
            raise RiskConfigError("risk redis ping failed during startup")

    # ------------------------------------------------------------------
    # Time / session helpers
    # ------------------------------------------------------------------

    def now_ns(self) -> int:
        return int(self.clock.wall_time_ns())

    def _current_trading_day(self, ts_ns: int) -> str:
        local_dt = datetime.fromtimestamp(ts_ns / 1_000_000_000, tz=self.tz)
        return local_dt.date().isoformat()

    def _roll_trading_day_if_needed(self, now_ns: int) -> None:
        trading_day = self._current_trading_day(now_ns)
        if trading_day != self.ledger.trading_day:
            self.ledger.reset_for_day(trading_day)
            self.runtime.cooldown_until_ns = 0
            self.runtime.force_flatten_requested = False
            self.runtime.params_reload_requested = False

    # ------------------------------------------------------------------
    # Redis reads
    # ------------------------------------------------------------------

    def _read_execution_state(self) -> dict[str, str]:
        return _decode_mapping(RX.hgetall(N.HASH_STATE_EXECUTION, client=self.redis))

    def _read_position_state(self) -> dict[str, str]:
        return _decode_mapping(RX.hgetall(N.HASH_STATE_POSITION_MME, client=self.redis))

    def _read_heartbeat(self, key: str) -> dict[str, str]:
        return _decode_mapping(RX.hgetall(key, client=self.redis))

    def _heartbeat_fresh(self, key: str, now_ns: int) -> bool:
        raw = self._read_heartbeat(key)
        if not raw:
            return False
        ts_event_ns = _safe_int(raw.get("ts_event_ns"), 0)
        if ts_event_ns <= 0:
            return False
        age_ns = max(0, now_ns - ts_event_ns)
        return age_ns < int(self.cfg.thresholds.stale_heartbeat_seconds * 1_000_000_000)

    # ------------------------------------------------------------------
    # Dependency refresh / veto logic
    # ------------------------------------------------------------------

    def _refresh_dependency_state(self, now_ns: int) -> None:
        exec_state = self._read_execution_state()
        pos_state = self._read_position_state()

        execution_mode = _safe_str(
            exec_state.get("execution_mode"),
            N.EXECUTION_MODE_NORMAL,
        )
        self.runtime.execution_healthy = execution_mode not in {
            N.EXECUTION_MODE_FATAL,
            N.EXECUTION_MODE_DEGRADED,
        }
        self.runtime.broker_connected = not _safe_bool(
            exec_state.get("broker_degraded"),
            False,
        )

        has_position = _safe_bool(pos_state.get("has_position"), False)
        position_side = _safe_str(pos_state.get("position_side"), N.POSITION_SIDE_FLAT)
        self.runtime.position_open = bool(has_position and position_side != N.POSITION_SIDE_FLAT)

        features_fresh = self._heartbeat_fresh(N.KEY_HEALTH_FEATURES, now_ns)
        strategy_fresh = self._heartbeat_fresh(N.KEY_HEALTH_STRATEGY, now_ns)
        execution_fresh = self._heartbeat_fresh(N.KEY_HEALTH_EXECUTION, now_ns)
        self.runtime.upstream_healthy = features_fresh and strategy_fresh and execution_fresh
        self.runtime.trading_window_ok = self.cfg.thresholds.allow_entry_outside_window or self.cfg.trading_window.contains(
            now_ns,
            self.tz,
        )
        self.runtime.updated_at_ns = now_ns

    def _recompute_veto(self, now_ns: int) -> None:
        veto_entries = False
        veto_reason = ""

        if self.runtime.control_mode == N.CONTROL_MODE_DISABLED:
            veto_entries = True
            veto_reason = "control_mode_disabled"
        elif self.runtime.control_mode == N.CONTROL_MODE_SAFE:
            veto_entries = True
            veto_reason = "control_mode_safe"
        elif self.runtime.manual_pause:
            veto_entries = True
            veto_reason = self.runtime.manual_pause_reason or "manual_pause"
        elif self.runtime.cooldown_active(now_ns):
            veto_entries = True
            veto_reason = "cooldown_active"
        elif self.ledger.realized_pnl <= (-1.0 * self.cfg.thresholds.daily_loss_limit):
            veto_entries = True
            veto_reason = "daily_loss_limit_hit"
        elif (
            self.cfg.thresholds.max_consecutive_losses > 0
            and self.ledger.consecutive_losses >= self.cfg.thresholds.max_consecutive_losses
        ):
            veto_entries = True
            veto_reason = "max_consecutive_losses_hit"
        elif (
            self.cfg.thresholds.max_trades_per_day > 0
            and self.ledger.trades_today >= self.cfg.thresholds.max_trades_per_day
        ):
            veto_entries = True
            veto_reason = "max_trades_per_day_hit"
        elif not self.runtime.trading_window_ok:
            veto_entries = True
            veto_reason = "outside_trading_window"
        elif self.cfg.thresholds.require_execution_healthy and not self.runtime.execution_healthy:
            veto_entries = True
            veto_reason = "execution_unhealthy"
        elif self.cfg.thresholds.require_upstream_heartbeats and not self.runtime.upstream_healthy:
            veto_entries = True
            veto_reason = "upstream_heartbeat_stale"
        elif self.cfg.thresholds.require_broker_connected and not self.runtime.broker_connected:
            veto_entries = True
            veto_reason = "broker_disconnected"

        self.runtime.veto_entries = veto_entries
        self.runtime.veto_reason = veto_reason

    # ------------------------------------------------------------------
    # Stream consumption
    # ------------------------------------------------------------------

    def _process_trade_ledger(self, now_ns: int) -> bool:
        results = RX.xreadgroup(
            N.GROUP_RISK,
            self.cfg.consumer_name,
            {N.STREAM_TRADES_LEDGER: RX.STREAM_ID_NEW_ONLY},
            count=10,
            block_ms=self.cfg.thresholds.ledger_block_ms,
            client=self.redis,
        )
        progressed = False

        for stream_name, entries in results:
            if stream_name != N.STREAM_TRADES_LEDGER:
                continue

            for message_id, fields in entries:
                self._apply_trade_ledger(fields, stream_id=message_id, now_ns=now_ns)
                RX.xack(
                    N.STREAM_TRADES_LEDGER,
                    N.GROUP_RISK,
                    [message_id],
                    client=self.redis,
                )
                progressed = True

        return progressed

    def _apply_trade_ledger(
        self,
        fields: Mapping[str, Any],
        *,
        stream_id: str,
        now_ns: int,
    ) -> None:
        payload = _decode_mapping(fields)
        event_type = _safe_str(payload.get("event_type")).upper()
        if event_type not in {"ENTRY_FILL", "EXIT_FILL"}:
            return

        if event_type == "ENTRY_FILL":
            self.ledger.trades_today += 1
            self.ledger.last_trade_id = _safe_str(payload.get("decision_id"))
            self.ledger.last_trade_stream_id = stream_id
            self.ledger.last_trade_ts_ns = _safe_int(
                payload.get("ts_ns"),
                now_ns,
            )
            return

        realized_pnl = _safe_float(
            payload.get("pnl") or payload.get("realized_pnl") or payload.get("net_pnl"),
            0.0,
        )
        self.ledger.realized_pnl += realized_pnl
        self.ledger.last_trade_id = _safe_str(payload.get("decision_id"))
        self.ledger.last_trade_stream_id = stream_id
        self.ledger.last_trade_ts_ns = _safe_int(
            payload.get("ts_ns"),
            now_ns,
        )

        if realized_pnl < 0.0:
            self.ledger.loss_count += 1
            self.ledger.consecutive_losses += 1
            cooldown_ns = int(self.cfg.thresholds.cooldown_seconds_after_loss * 1_000_000_000)
            if cooldown_ns > 0:
                self.runtime.set_cooldown_until(now_ns + cooldown_ns)
        elif realized_pnl > 0.0:
            self.ledger.win_count += 1
            self.ledger.consecutive_losses = 0
        else:
            self.ledger.consecutive_losses = 0

    def _process_control_commands(self, now_ns: int) -> bool:
        results = RX.xreadgroup(
            N.GROUP_RISK,
            self.cfg.consumer_name,
            {N.STREAM_CMD_MME: RX.STREAM_ID_NEW_ONLY},
            count=10,
            block_ms=self.cfg.thresholds.command_block_ms,
            client=self.redis,
        )
        progressed = False

        for stream_name, entries in results:
            if stream_name != N.STREAM_CMD_MME:
                continue

            for message_id, fields in entries:
                self._apply_command(fields, now_ns=now_ns)
                RX.xack(
                    N.STREAM_CMD_MME,
                    N.GROUP_RISK,
                    [message_id],
                    client=self.redis,
                )
                progressed = True

        return progressed

    def _apply_command(self, fields: Mapping[str, Any], *, now_ns: int) -> None:
        payload = _decode_mapping(fields)
        cmd = _safe_str(payload.get("cmd")).upper()
        if not cmd:
            raise RiskContractError("command payload missing cmd")

        if cmd == N.CMD_PARAMS_RELOAD:
            self.runtime.params_reload_requested = True
            return

        if cmd == N.CMD_PAUSE_TRADING:
            self.runtime.manual_pause = True
            self.runtime.manual_pause_reason = _safe_str(
                payload.get("reason"),
                "manual_pause",
            )
            return

        if cmd == N.CMD_RESUME_TRADING:
            self.runtime.manual_pause = False
            self.runtime.manual_pause_reason = ""
            if self.runtime.control_mode == N.CONTROL_MODE_NORMAL:
                self.runtime.force_flatten_requested = False
            return

        if cmd == N.CMD_FORCE_FLATTEN:
            self.runtime.force_flatten_requested = True
            return

        if cmd == N.CMD_SET_MODE:
            mode = _safe_str(payload.get("mode")).upper()
            allowed_modes = {
                N.CONTROL_MODE_NORMAL,
                N.CONTROL_MODE_SAFE,
                N.CONTROL_MODE_REPLAY,
                N.CONTROL_MODE_DISABLED,
            }
            if mode not in allowed_modes:
                raise RiskContractError(f"invalid control mode: {mode!r}")

            self.runtime.control_mode = mode
            if mode == N.CONTROL_MODE_NORMAL:
                self.runtime.manual_pause = False
                self.runtime.manual_pause_reason = ""
            elif mode == N.CONTROL_MODE_SAFE:
                self.runtime.manual_pause = True
                self.runtime.manual_pause_reason = "control_mode_safe"
            elif mode == N.CONTROL_MODE_DISABLED:
                self.runtime.manual_pause = True
                self.runtime.manual_pause_reason = "control_mode_disabled"
                self.runtime.force_flatten_requested = True
            return

    # ------------------------------------------------------------------
    # Publishing
    # ------------------------------------------------------------------

    def _build_snapshot(self, now_ns: int) -> dict[str, str]:
        stale_cutoff_ns = int(self.cfg.thresholds.stale_heartbeat_seconds * 1_000_000_000)
        stale = (now_ns - self.runtime.updated_at_ns) > stale_cutoff_ns
        max_new_lots = (
            0 if self.runtime.veto_entries else self.cfg.thresholds.max_new_lots_default
        )

        daily_stop_hit = self.ledger.realized_pnl <= (-1.0 * self.cfg.thresholds.daily_loss_limit)
        max_loss_hit = (
            self.cfg.thresholds.max_consecutive_losses > 0
            and self.ledger.consecutive_losses >= self.cfg.thresholds.max_consecutive_losses
        )
        max_trades_hit = (
            self.cfg.thresholds.max_trades_per_day > 0
            and self.ledger.trades_today >= self.cfg.thresholds.max_trades_per_day
        )

        reason_code = self.runtime.veto_reason
        reason_message = self.runtime.veto_reason

        return {
            "ts_ns": str(now_ns),
            "control_mode": self.runtime.control_mode,
            "mode": self.runtime.control_mode,
            "veto_entries": "1" if self.runtime.veto_entries else "0",
            "degraded_only": "0",
            "force_flatten": "1" if self.runtime.force_flatten_requested else "0",
            "allow_exits": "1",
            "manual_pause": "1" if self.runtime.manual_pause else "0",
            "manual_pause_reason": self.runtime.manual_pause_reason,
            "trading_window_ok": "1" if self.runtime.trading_window_ok else "0",
            "execution_healthy": "1" if self.runtime.execution_healthy else "0",
            "upstream_healthy": "1" if self.runtime.upstream_healthy else "0",
            "broker_connected": "1" if self.runtime.broker_connected else "0",
            "cooldown_until_ns": str(self.runtime.cooldown_until_ns),
            "cooldown_active": "1" if self.runtime.cooldown_active(now_ns) else "0",
            "day_realized_pnl": str(self.ledger.realized_pnl),
            "trades_today": str(self.ledger.trades_today),
            "day_loss_count": str(self.ledger.loss_count),
            "day_win_count": str(self.ledger.win_count),
            "consecutive_losses": str(self.ledger.consecutive_losses),
            "trading_day": self.ledger.trading_day,
            "stale": "1" if stale else "0",
            "risk_heartbeat_stale": "1" if stale else "0",
            "daily_stop_hit": "1" if daily_stop_hit else "0",
            "max_loss_hit": "1" if max_loss_hit else "0",
            "max_trades_hit": "1" if max_trades_hit else "0",
            "max_new_lots": str(max_new_lots),
            "params_reload_requested": "1" if self.runtime.params_reload_requested else "0",
            "reason_code": reason_code,
            "reason_message": reason_message,
            "last_update_ns": str(now_ns),
        }

    def _publish_state(self, now_ns: int, *, force: bool) -> None:
        interval_ns = int(self.cfg.thresholds.state_publish_interval_seconds * 1_000_000_000)
        if not force and (now_ns - self.runtime.last_state_publish_ns) < interval_ns:
            return

        RX.write_hash_fields(
            N.HASH_STATE_RISK,
            self._build_snapshot(now_ns),
            client=self.redis,
        )
        self.runtime.last_state_publish_ns = now_ns

    def _publish_heartbeat(self, now_ns: int, *, force: bool) -> None:
        interval_ns = int(self.cfg.thresholds.heartbeat_refresh_ms * 1_000_000)
        if not force and (now_ns - self.runtime.last_heartbeat_ns) < interval_ns:
            return

        RX.write_heartbeat(
            N.KEY_HEALTH_RISK,
            service=N.SERVICE_RISK,
            instance_id=self.cfg.instance_id,
            status=_status_to_health(
                N.EXECUTION_MODE_EXIT_ONLY if self.runtime.veto_entries else N.EXECUTION_MODE_NORMAL
            ),
            ts_event_ns=now_ns,
            message=self.runtime.veto_reason or "ok",
            ttl_ms=self.cfg.thresholds.heartbeat_ttl_ms,
            client=self.redis,
        )
        self.runtime.last_heartbeat_ns = now_ns

    def _publish_health_event(
        self,
        *,
        status: str,
        event: str,
        detail: str,
        ts_ns: int,
    ) -> None:
        RX.xadd_fields(
            N.STREAM_SYSTEM_HEALTH,
            {
                "event_type": event,
                "service_name": N.SERVICE_RISK,
                "instance_id": self.cfg.instance_id,
                "status": status,
                "detail": detail,
                "ts_ns": str(ts_ns),
            },
            maxlen_approx=DEFAULT_HEALTH_STREAM_MAXLEN,
            client=self.redis,
        )

    def _publish_error_event(
        self,
        *,
        event: str,
        detail: str,
        ts_ns: int,
    ) -> None:
        RX.xadd_fields(
            N.STREAM_SYSTEM_ERRORS,
            {
                "event_type": event,
                "service_name": N.SERVICE_RISK,
                "instance_id": self.cfg.instance_id,
                "detail": detail,
                "ts_ns": str(ts_ns),
            },
            maxlen_approx=DEFAULT_ERROR_STREAM_MAXLEN,
            client=self.redis,
        )

    def _publish_shutdown_heartbeat(self) -> None:
        with contextlib.suppress(Exception):
            RX.write_heartbeat(
                N.KEY_HEALTH_RISK,
                service=N.SERVICE_RISK,
                instance_id=self.cfg.instance_id,
                status="STOPPED",
                ts_event_ns=self.now_ns(),
                ttl_ms=self.cfg.thresholds.heartbeat_ttl_ms,
                client=self.redis,
            )


# =============================================================================
# Canonical entrypoint
# =============================================================================


def run(context: Any) -> int:
    _validate_name_surface_or_die()

    if context is None:
        raise RiskConfigError("risk.run(context) requires non-null context")

    redis_runtime = getattr(context, "redis", None)
    redis_client = redis_runtime.sync if redis_runtime is not None and hasattr(redis_runtime, "sync") else RX.get_redis()

    clock = getattr(context, "clock", None)
    shutdown = getattr(context, "shutdown", None)
    if clock is None:
        raise RiskConfigError("risk requires context.clock")
    if shutdown is None:
        raise RiskConfigError("risk requires context.shutdown")

    cfg = RiskConfig.from_context(context)

    service = RiskService(
        redis_client=redis_client,
        clock=clock,
        shutdown=shutdown,
        config=cfg,
        logger=LOGGER,
    )
    return service.start()