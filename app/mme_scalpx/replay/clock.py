"""
app/mme_scalpx/replay/clock.py

Freeze-grade replay clock layer for the MME-ScalpX Permanent Replay &
Validation Framework.

Clock responsibilities
----------------------
This module owns:
- centralized replay time ownership
- deterministic replay time progression
- replay speed mode control
- pause / resume / step semantics
- replay clock state serialization helpers

This module does not own:
- dataset discovery/loading
- replay selection policy
- replay execution orchestration
- topology truth
- payload injection
- doctrine logic
- live runtime mutation

Design rules
------------
- replay time must be centrally owned here
- clock progression must be explicit and auditable
- identical input timestamps + identical controls must yield identical replay time
- no hidden use of wall clock for replay decisioning
- pause / step must be deterministic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Sequence

from .modes import ReplaySpeedMode


class ReplayClockError(RuntimeError):
    """Base exception for replay clock failures."""


class ReplayClockValidationError(ReplayClockError):
    """Raised when replay clock inputs or state transitions are invalid."""


@dataclass(frozen=True, slots=True)
class ReplayClockConfig:
    """
    Immutable replay clock configuration.
    """

    speed_mode: ReplaySpeedMode
    start_time: str
    allow_breakpoint_mode: bool = True
    default_step_delta_ms: int = 1
    max_forward_jump_ms: int | None = None


@dataclass(frozen=True, slots=True)
class ReplayClockSnapshot:
    """
    Canonical serialized replay clock state.
    """

    speed_mode: str
    current_time: str
    is_paused: bool
    tick_count: int
    step_count: int
    last_event_time: str | None
    notes: tuple[str, ...] = field(default_factory=tuple)


class ReplayClock:
    """
    Freeze-grade replay clock.
    """

    def __init__(self, config: ReplayClockConfig) -> None:
        _validate_config(config)

        self._config = config
        self._current_time = _parse_iso_datetime(config.start_time)
        self._speed_mode = config.speed_mode
        self._is_paused = config.speed_mode is ReplaySpeedMode.PAUSED
        self._tick_count = 0
        self._step_count = 0
        self._last_event_time: datetime | None = None
        self._notes: list[str] = []

    @property
    def config(self) -> ReplayClockConfig:
        return self._config

    @property
    def speed_mode(self) -> ReplaySpeedMode:
        return self._speed_mode

    @property
    def current_time(self) -> str:
        return _to_iso_z(self._current_time)

    @property
    def is_paused(self) -> bool:
        return self._is_paused

    @property
    def tick_count(self) -> int:
        return self._tick_count

    @property
    def step_count(self) -> int:
        return self._step_count

    @property
    def last_event_time(self) -> str | None:
        return _to_iso_z(self._last_event_time) if self._last_event_time else None

    def snapshot(self, *, notes: Sequence[str] = ()) -> ReplayClockSnapshot:
        return ReplayClockSnapshot(
            speed_mode=self._speed_mode.value,
            current_time=_to_iso_z(self._current_time),
            is_paused=self._is_paused,
            tick_count=self._tick_count,
            step_count=self._step_count,
            last_event_time=self.last_event_time,
            notes=tuple(notes) + tuple(self._notes),
        )

    def set_speed_mode(self, speed_mode: ReplaySpeedMode) -> None:
        if speed_mode is ReplaySpeedMode.BREAKPOINT and not self._config.allow_breakpoint_mode:
            raise ReplayClockValidationError("breakpoint mode is disabled by config")

        self._speed_mode = speed_mode
        self._is_paused = speed_mode is ReplaySpeedMode.PAUSED

    def pause(self) -> None:
        self._speed_mode = ReplaySpeedMode.PAUSED
        self._is_paused = True

    def resume(self, *, speed_mode: ReplaySpeedMode | None = None) -> None:
        next_mode = speed_mode or ReplaySpeedMode.ACCELERATED
        if next_mode is ReplaySpeedMode.PAUSED:
            raise ReplayClockValidationError("resume() requires a non-paused speed mode")
        if next_mode is ReplaySpeedMode.BREAKPOINT and not self._config.allow_breakpoint_mode:
            raise ReplayClockValidationError("breakpoint mode is disabled by config")

        self._speed_mode = next_mode
        self._is_paused = False

    def advance_to_event_time(self, event_time: str) -> str:
        if self._is_paused:
            raise ReplayClockValidationError("cannot advance clock while paused")

        event_dt = _parse_iso_datetime(event_time)
        if event_dt < self._current_time:
            raise ReplayClockValidationError(
                f"event_time must be >= current replay time; "
                f"got event_time={_to_iso_z(event_dt)} current_time={_to_iso_z(self._current_time)}"
            )

        delta_ms = int((event_dt - self._current_time).total_seconds() * 1000)
        if self._config.max_forward_jump_ms is not None:
            if delta_ms > self._config.max_forward_jump_ms:
                raise ReplayClockValidationError(
                    f"event_time jump exceeds max_forward_jump_ms={self._config.max_forward_jump_ms}"
                )

        self._current_time = event_dt
        self._last_event_time = event_dt
        self._tick_count += 1
        return _to_iso_z(self._current_time)

    def step(self, *, delta_ms: int | None = None) -> str:
        step_ms = delta_ms if delta_ms is not None else self._config.default_step_delta_ms
        if step_ms <= 0:
            raise ReplayClockValidationError(f"step delta must be > 0, got {step_ms}")

        if self._config.max_forward_jump_ms is not None and step_ms > self._config.max_forward_jump_ms:
            raise ReplayClockValidationError(
                f"step delta exceeds max_forward_jump_ms={self._config.max_forward_jump_ms}"
            )

        self._current_time = self._current_time + timedelta(milliseconds=step_ms)
        self._step_count += 1
        self._tick_count += 1
        return _to_iso_z(self._current_time)

    def sync_if_needed(self, event_time: str) -> str:
        return self.advance_to_event_time(event_time)

    def record_note(self, note: str) -> None:
        if not isinstance(note, str) or not note.strip():
            raise ReplayClockValidationError(f"clock note must be non-empty string, got {note!r}")
        self._notes.append(note)


def replay_clock_snapshot_to_dict(snapshot: ReplayClockSnapshot) -> dict[str, Any]:
    return {
        "speed_mode": snapshot.speed_mode,
        "current_time": snapshot.current_time,
        "is_paused": snapshot.is_paused,
        "tick_count": snapshot.tick_count,
        "step_count": snapshot.step_count,
        "last_event_time": snapshot.last_event_time,
        "notes": list(snapshot.notes),
    }


def _validate_config(config: ReplayClockConfig) -> None:
    _ = _parse_iso_datetime(config.start_time)

    if config.default_step_delta_ms <= 0:
        raise ReplayClockValidationError(
            f"default_step_delta_ms must be > 0, got {config.default_step_delta_ms}"
        )

    if config.max_forward_jump_ms is not None and config.max_forward_jump_ms <= 0:
        raise ReplayClockValidationError(
            f"max_forward_jump_ms must be > 0 when set, got {config.max_forward_jump_ms}"
        )

    if config.speed_mode is ReplaySpeedMode.BREAKPOINT and not config.allow_breakpoint_mode:
        raise ReplayClockValidationError("breakpoint mode is disabled by config")


def _parse_iso_datetime(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ReplayClockValidationError(f"datetime must be non-empty ISO string, got {value!r}")

    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        dt = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ReplayClockValidationError(
            f"datetime must be ISO-8601 compatible, got {value!r}"
        ) from exc

    if dt.tzinfo is None:
        raise ReplayClockValidationError(
            f"datetime must be timezone-aware, got naive value {value!r}"
        )

    return dt.astimezone(timezone.utc)


def _to_iso_z(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


__all__ = [
    "ReplayClockError",
    "ReplayClockValidationError",
    "ReplayClockConfig",
    "ReplayClockSnapshot",
    "ReplayClock",
    "replay_clock_snapshot_to_dict",
]
