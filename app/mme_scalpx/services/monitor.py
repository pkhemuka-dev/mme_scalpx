from __future__ import annotations

"""
app/mme_scalpx/services/monitor.py

Observability, diagnostics, and control plane for ScalpX MME.

Frozen contract
---------------
This module OWNS:
- observation of runtime service liveness via canonical health keys
- observation of latest canonical runtime state via canonical hashes
- monitor heartbeat publication
- additive system health publication
- additive system error publication
- control-plane command publication
- runtime entrypoint `run(context)`

This module DOES NOT own:
- risk truth
- execution truth
- position truth
- strategy truth
- broker truth
- order placement
- report reconstruction
- runtime supervision
- alternate startup roots

Design rules
------------
- monitor = observability/control plane only
- names.py is the only symbolic source of truth
- redisx.py is the only transport façade for owned writes, lock lifecycle,
  heartbeat lifecycle, and canonical hash access
- main.py is the only startup root
- runtime service entrypoint is exactly `run(context)`
- replay-safe and restart-safe

Important freeze rule
---------------------
settings.py proves only the typed monitor settings surface:
- settings.monitor.poll_interval_ms
- settings.monitor.health_publish_interval_ms

This module therefore:
- uses typed settings.monitor.* for those fields
- preserves the already-proven context override surface from the uploaded
  monitor lineage for additional observability-control tuning:
    monitor_diagnostic_publish_interval_ms
    monitor_heartbeat_ttl_ms
    monitor_lock_ttl_ms
    monitor_lock_refresh_ms
    monitor_warn_stale_ms
    monitor_error_stale_ms
    monitor_startup_grace_ms
    monitor_emit_health_when_unchanged
    monitor_emit_diagnostics_when_unchanged
    monitor_log_health_on_change_only
    monitor_stream_health_maxlen
    monitor_stream_error_maxlen
    monitor_stream_cmd_maxlen
- does NOT invent any new settings fields or dependency factories

Freeze correction
-----------------
main.py already provides context.redis and context.settings in the canonical
runtime context. This service therefore does NOT fall back to RX.get_redis()
or any alternate dependency factory.
"""

import contextlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Final, Mapping, Sequence

from app.mme_scalpx.core import names as N
from app.mme_scalpx.core import redisx as RX
from app.mme_scalpx.core.settings import (
    DEFAULT_HEARTBEAT_TTL_MS,
    DEFAULT_LOCK_REFRESH_INTERVAL_MS,
    DEFAULT_LOCK_TTL_MS,
    AppSettings,
    get_settings,
)

LOGGER = logging.getLogger("app.mme_scalpx.services.monitor")

DEFAULT_DIAGNOSTIC_PUBLISH_INTERVAL_MS: Final[int] = 5_000
DEFAULT_WARN_STALE_MS: Final[int] = 4_000
DEFAULT_ERROR_STALE_MS: Final[int] = 10_000
DEFAULT_STARTUP_GRACE_MS: Final[int] = 15_000
DEFAULT_HEALTH_STREAM_MAXLEN: Final[int] = 20_000
DEFAULT_ERROR_STREAM_MAXLEN: Final[int] = 20_000
DEFAULT_CMD_STREAM_MAXLEN: Final[int] = 20_000


# ============================================================================
# Exceptions
# ============================================================================


class MonitorError(RuntimeError):
    """Base monitor error."""


class ControlPlaneError(MonitorError):
    """Raised when a control-plane command is invalid."""


# ============================================================================
# Required surface validation
# ============================================================================

_REQUIRED_NAME_EXPORTS: Final[tuple[str, ...]] = (
    "SERVICE_MONITOR",
    "SERVICE_FEEDS",
    "SERVICE_FEATURES",
    "SERVICE_STRATEGY",
    "SERVICE_RISK",
    "SERVICE_EXECUTION",
    "SERVICE_REPORT",
    "KEY_HEALTH_FEEDS",
    "KEY_HEALTH_FEATURES",
    "KEY_HEALTH_STRATEGY",
    "KEY_HEALTH_RISK",
    "KEY_HEALTH_EXECUTION",
    "KEY_HEALTH_MONITOR",
    "KEY_HEALTH_REPORT",
    "KEY_LOCK_MONITOR",
    "STREAM_SYSTEM_HEALTH",
    "STREAM_SYSTEM_ERRORS",
    "STREAM_CMD_MME",
    "HASH_STATE_EXECUTION",
    "HASH_STATE_POSITION_MME",
    "HASH_STATE_RISK",
    "HASH_STATE_FEATURES_MME_FUT",
    "HASH_STATE_RUNTIME",
    "HASH_STATE_MODE",
    "HASH_PARAMS_MME_META",
    "HEALTH_STATUS_OK",
    "HEALTH_STATUS_WARN",
    "HEALTH_STATUS_ERROR",
    "EXECUTION_MODE_NORMAL",
    "EXECUTION_MODE_EXIT_ONLY",
    "EXECUTION_MODE_DEGRADED",
    "EXECUTION_MODE_FATAL",
    "CONTROL_MODE_NORMAL",
    "CONTROL_MODE_SAFE",
    "CONTROL_MODE_REPLAY",
    "CONTROL_MODE_DISABLED",
    "CMD_PARAMS_RELOAD",
    "CMD_PAUSE_TRADING",
    "CMD_RESUME_TRADING",
    "CMD_FORCE_FLATTEN",
    "CMD_SET_MODE",
    "POSITION_SIDE_FLAT",
    "ENTRY_MODE_UNKNOWN",
)

_ALLOWED_MONITOR_STREAM_WRITES: Final[frozenset[str]] = frozenset(
    {
        N.STREAM_SYSTEM_HEALTH,
        N.STREAM_SYSTEM_ERRORS,
        N.STREAM_CMD_MME,
    }
)

_SERVICE_HEALTH_KEYS: Final[tuple[tuple[str, str], ...]] = (
    (N.SERVICE_FEEDS, N.KEY_HEALTH_FEEDS),
    (N.SERVICE_FEATURES, N.KEY_HEALTH_FEATURES),
    (N.SERVICE_STRATEGY, N.KEY_HEALTH_STRATEGY),
    (N.SERVICE_RISK, N.KEY_HEALTH_RISK),
    (N.SERVICE_EXECUTION, N.KEY_HEALTH_EXECUTION),
    (N.SERVICE_REPORT, N.KEY_HEALTH_REPORT),
)

_STATE_KEYS_TO_OBSERVE: Final[tuple[tuple[str, str], ...]] = (
    ("execution", N.HASH_STATE_EXECUTION),
    ("position", N.HASH_STATE_POSITION_MME),
    ("risk", N.HASH_STATE_RISK),
    ("features", N.HASH_STATE_FEATURES_MME_FUT),
    ("runtime", N.HASH_STATE_RUNTIME),
    ("mode", N.HASH_STATE_MODE),
    ("params_meta", N.HASH_PARAMS_MME_META),
)


def _validate_name_surface_or_die() -> None:
    missing = [name for name in _REQUIRED_NAME_EXPORTS if not hasattr(N, name)]
    if missing:
        raise MonitorError(
            "monitor.py missing required names.py exports: " + ", ".join(sorted(missing))
        )


def _validate_context_or_die(context: Any) -> None:
    if context is None:
        raise MonitorError("monitor.run(context) requires a non-null context")
    for required in ("redis", "clock", "shutdown", "service_name", "instance_id"):
        if not hasattr(context, required):
            raise MonitorError(
                f"monitor runtime context missing required attribute: {required}"
            )


# ============================================================================
# Small helpers
# ============================================================================


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace").strip()
    return str(value).strip()


def _safe_int(value: Any, default: int | None = None) -> int | None:
    try:
        if value in (None, ""):
            return default
        return int(float(value))
    except Exception:
        return default


def _safe_float(value: Any, default: float | None = None) -> float | None:
    try:
        if value in (None, ""):
            return default
        out = float(value)
        if out != out or out in (float("inf"), float("-inf")):
            return default
        return out
    except Exception:
        return default


def _safe_bool(value: Any, default: bool | None = None) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    raw = _safe_str(value).lower()
    if raw in {"1", "true", "yes", "y", "on"}:
        return True
    if raw in {"0", "false", "no", "n", "off"}:
        return False
    return default


def _now_utc_iso_from_ns(ts_ns: int) -> str:
    return datetime.fromtimestamp(ts_ns / 1_000_000_000, tz=timezone.utc).isoformat()


def _dedupe_keep_order(values: Sequence[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        token = _safe_str(value)
        if not token or token in seen:
            continue
        seen.add(token)
        out.append(token)
    return out


# ============================================================================
# Config
# ============================================================================


@dataclass(frozen=True, slots=True)
class MonitorConfig:
    service_name: str
    instance_id: str
    poll_interval_ms: int
    health_publish_interval_ms: int
    diagnostic_publish_interval_ms: int
    heartbeat_ttl_ms: int
    lock_ttl_ms: int
    lock_refresh_ms: int
    warn_stale_ms: int
    error_stale_ms: int
    startup_grace_ms: int
    emit_health_when_unchanged: bool
    emit_diagnostics_when_unchanged: bool
    log_health_on_change_only: bool
    stream_health_maxlen: int
    stream_error_maxlen: int
    stream_cmd_maxlen: int

    @classmethod
    def from_runtime(
        cls,
        *,
        settings: AppSettings,
        context: Any,
    ) -> "MonitorConfig":
        poll_interval_ms = int(settings.monitor.poll_interval_ms)
        health_publish_interval_ms = int(settings.monitor.health_publish_interval_ms)

        return cls(
            service_name=str(getattr(context, "service_name", N.SERVICE_MONITOR)),
            instance_id=str(getattr(context, "instance_id")),
            poll_interval_ms=max(1, poll_interval_ms),
            health_publish_interval_ms=max(1, health_publish_interval_ms),
            diagnostic_publish_interval_ms=max(
                1,
                int(
                    getattr(
                        context,
                        "monitor_diagnostic_publish_interval_ms",
                        DEFAULT_DIAGNOSTIC_PUBLISH_INTERVAL_MS,
                    )
                ),
            ),
            heartbeat_ttl_ms=max(
                1,
                int(
                    getattr(
                        context,
                        "monitor_heartbeat_ttl_ms",
                        DEFAULT_HEARTBEAT_TTL_MS,
                    )
                ),
            ),
            lock_ttl_ms=max(
                1,
                int(
                    getattr(
                        context,
                        "monitor_lock_ttl_ms",
                        DEFAULT_LOCK_TTL_MS,
                    )
                ),
            ),
            lock_refresh_ms=max(
                1,
                int(
                    getattr(
                        context,
                        "monitor_lock_refresh_ms",
                        DEFAULT_LOCK_REFRESH_INTERVAL_MS,
                    )
                ),
            ),
            warn_stale_ms=max(
                1,
                int(getattr(context, "monitor_warn_stale_ms", DEFAULT_WARN_STALE_MS)),
            ),
            error_stale_ms=max(
                1,
                int(getattr(context, "monitor_error_stale_ms", DEFAULT_ERROR_STALE_MS)),
            ),
            startup_grace_ms=max(
                0,
                int(getattr(context, "monitor_startup_grace_ms", DEFAULT_STARTUP_GRACE_MS)),
            ),
            emit_health_when_unchanged=bool(
                getattr(context, "monitor_emit_health_when_unchanged", False)
            ),
            emit_diagnostics_when_unchanged=bool(
                getattr(context, "monitor_emit_diagnostics_when_unchanged", True)
            ),
            log_health_on_change_only=bool(
                getattr(context, "monitor_log_health_on_change_only", True)
            ),
            stream_health_maxlen=max(
                1,
                int(
                    getattr(
                        context,
                        "monitor_stream_health_maxlen",
                        DEFAULT_HEALTH_STREAM_MAXLEN,
                    )
                ),
            ),
            stream_error_maxlen=max(
                1,
                int(
                    getattr(
                        context,
                        "monitor_stream_error_maxlen",
                        DEFAULT_ERROR_STREAM_MAXLEN,
                    )
                ),
            ),
            stream_cmd_maxlen=max(
                1,
                int(
                    getattr(
                        context,
                        "monitor_stream_cmd_maxlen",
                        DEFAULT_CMD_STREAM_MAXLEN,
                    )
                ),
            ),
        )


# ============================================================================
# Observations
# ============================================================================


class ServiceSeverity(str, Enum):
    OK = "OK"
    WARN = "WARN"
    ERROR = "ERROR"


class ServiceState(str, Enum):
    UP = "UP"
    STALE = "STALE"
    DOWN = "DOWN"
    UNKNOWN = "UNKNOWN"


@dataclass(slots=True)
class HeartbeatObservation:
    key: str
    owner: str | None
    ts_event_ns: int | None
    raw: dict[str, Any]
    state: ServiceState
    severity: ServiceSeverity
    reason: str

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "owner": self.owner,
            "ts_event_ns": self.ts_event_ns,
            "state": self.state.value,
            "severity": self.severity.value,
            "reason": self.reason,
            "raw": dict(self.raw),
        }


@dataclass(slots=True)
class PositionObservation:
    has_position: bool
    position_side: str
    qty_lots: int
    entry_mode: str | None
    avg_price: float | None
    mark_price: float | None
    realized_pnl_day: float | None

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "has_position": self.has_position,
            "position_side": self.position_side,
            "qty_lots": self.qty_lots,
            "entry_mode": self.entry_mode,
            "avg_price": self.avg_price,
            "mark_price": self.mark_price,
            "realized_pnl_day": self.realized_pnl_day,
        }


@dataclass(slots=True)
class ServiceObservation:
    name: str
    heartbeat: HeartbeatObservation
    latest_state: dict[str, Any]
    notes: list[str]

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "heartbeat": self.heartbeat.to_public_dict(),
            "latest_state": dict(self.latest_state),
            "notes": list(self.notes),
        }


@dataclass(slots=True)
class SystemSnapshot:
    ts_ms: int
    ts_ns: int
    ts_utc: str
    monitor_instance_id: str
    overall_status: str
    summary: str
    startup_grace_active: bool
    services: dict[str, ServiceObservation]
    execution_mode: str
    control_mode: str
    risk_veto_entries: bool | None
    position: PositionObservation
    diagnostics: dict[str, Any]

    def stable_fingerprint(self) -> str:
        public = {
            "overall_status": self.overall_status,
            "summary": self.summary,
            "execution_mode": self.execution_mode,
            "control_mode": self.control_mode,
            "risk_veto_entries": self.risk_veto_entries,
            "position": self.position.to_public_dict(),
            "services": {
                key: value.to_public_dict()
                for key, value in sorted(self.services.items())
            },
        }
        return json.dumps(public, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    def to_health_event(self) -> dict[str, Any]:
        return {
            "event_type": "system_health",
            "ts_ms": self.ts_ms,
            "ts_ns": self.ts_ns,
            "ts_utc": self.ts_utc,
            "service_name": N.SERVICE_MONITOR,
            "monitor_instance_id": self.monitor_instance_id,
            "overall_status": self.overall_status,
            "summary": self.summary,
            "startup_grace_active": "1" if self.startup_grace_active else "0",
            "execution_mode": self.execution_mode,
            "control_mode": self.control_mode,
            "risk_veto_entries": "1" if self.risk_veto_entries else "0",
            "has_position": "1" if self.position.has_position else "0",
            "position_side": self.position.position_side,
            "entry_mode": self.position.entry_mode or N.ENTRY_MODE_UNKNOWN,
        }

    def to_diagnostic_payload(self) -> dict[str, Any]:
        return {
            "event_type": "system_diagnostics",
            "ts_ms": self.ts_ms,
            "ts_ns": self.ts_ns,
            "ts_utc": self.ts_utc,
            "service_name": N.SERVICE_MONITOR,
            "monitor_instance_id": self.monitor_instance_id,
            "overall_status": self.overall_status,
            "summary": self.summary,
            "execution_mode": self.execution_mode,
            "control_mode": self.control_mode,
            "risk_veto_entries": "1" if self.risk_veto_entries else "0",
            "position": json.dumps(
                self.position.to_public_dict(),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
            "services": json.dumps(
                {key: obs.to_public_dict() for key, obs in sorted(self.services.items())},
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
            "diagnostics": json.dumps(
                dict(self.diagnostics),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
        }


# ============================================================================
# Service
# ============================================================================


class MonitorService:
    def __init__(
        self,
        *,
        redis_client: Any,
        clock: Any,
        shutdown: Any,
        config: MonitorConfig,
        logger: logging.Logger | None = None,
    ) -> None:
        self._redis = redis_client
        self._clock = clock
        self._shutdown = shutdown
        self.config = config
        self.log = logger or LOGGER

        self._lock_owner = config.instance_id
        self._owns_lock = False
        self._started_ns = int(self._clock.wall_time_ns())
        self._last_lock_refresh_ns = 0
        self._last_health_publish_ms = 0
        self._last_diag_publish_ms = 0
        self._last_health_fingerprint = ""
        self._last_diag_fingerprint = ""
        self._last_error_signature = ""

        self._validate_runtime_contract()

    def _validate_runtime_contract(self) -> None:
        if self._redis is None:
            raise MonitorError("monitor requires a Redis client")
        if self._clock is None or not hasattr(self._clock, "wall_time_ns"):
            raise MonitorError("monitor requires context.clock.wall_time_ns()")
        if self._shutdown is None or not hasattr(self._shutdown, "wait") or not hasattr(self._shutdown, "is_set"):
            raise MonitorError("monitor requires context.shutdown.wait()/is_set()")
        if not self.config.instance_id:
            raise MonitorError("monitor requires non-empty instance_id")
        if not RX.ping_redis(client=self._redis):
            raise MonitorError("monitor redis ping failed during startup")

    def _now_ns(self) -> int:
        return int(self._clock.wall_time_ns())

    def _now_ms(self) -> int:
        return int(self._now_ns() // 1_000_000)

    def _utc_now_iso(self) -> str:
        return _now_utc_iso_from_ns(self._now_ns())

    def _safe_read_hash(self, key: str) -> dict[str, Any]:
        try:
            raw = RX.hgetall(key, client=self._redis)
            return {str(k): v for k, v in raw.items()}
        except Exception:
            self.log.exception("monitor_hash_read_failed key=%s", key)
            return {}

    def _publish_stream_event(
        self,
        stream: str,
        payload: Mapping[str, Any],
        *,
        maxlen: int,
    ) -> str:
        if stream not in _ALLOWED_MONITOR_STREAM_WRITES:
            raise MonitorError(f"monitor write attempted on non-owned stream: {stream!r}")
        return RX.xadd_fields(
            stream,
            payload,
            maxlen_approx=maxlen,
            client=self._redis,
        )

    def _publish_heartbeat(self, *, status: str, message: str | None = None) -> None:
        RX.write_heartbeat(
            N.KEY_HEALTH_MONITOR,
            service=N.SERVICE_MONITOR,
            instance_id=self.config.instance_id,
            status=status,
            ts_event_ns=self._now_ns(),
            message=message,
            ttl_ms=self.config.heartbeat_ttl_ms,
            client=self._redis,
        )

    def _publish_shutdown_heartbeat(self) -> None:
        with contextlib.suppress(Exception):
            RX.write_heartbeat(
                N.KEY_HEALTH_MONITOR,
                service=N.SERVICE_MONITOR,
                instance_id=self.config.instance_id,
                status="STOPPED",
                ts_event_ns=self._now_ns(),
                ttl_ms=self.config.heartbeat_ttl_ms,
                client=self._redis,
            )

    def _acquire_lock_or_die(self) -> None:
        ok = RX.acquire_lock(
            N.KEY_LOCK_MONITOR,
            self._lock_owner,
            ttl_ms=self.config.lock_ttl_ms,
            client=self._redis,
        )
        if not ok:
            raise MonitorError("monitor singleton lock not acquired")
        self._owns_lock = True
        self._last_lock_refresh_ns = self._now_ns()

    def _refresh_lock_if_due(self) -> None:
        if not self._owns_lock:
            raise MonitorError("monitor lock not owned")
        now_ns = self._now_ns()
        if (now_ns - self._last_lock_refresh_ns) < (self.config.lock_refresh_ms * 1_000_000):
            return
        ok = RX.refresh_lock(
            N.KEY_LOCK_MONITOR,
            self._lock_owner,
            ttl_ms=self.config.lock_ttl_ms,
            client=self._redis,
        )
        if not ok:
            raise MonitorError("monitor singleton lock refresh failed")
        self._last_lock_refresh_ns = now_ns

    def _release_lock(self) -> None:
        if not self._owns_lock:
            return
        with contextlib.suppress(Exception):
            RX.release_lock(
                N.KEY_LOCK_MONITOR,
                self._lock_owner,
                client=self._redis,
            )
        self._owns_lock = False

    def _observe_heartbeat(self, *, key: str, now_ms: int) -> HeartbeatObservation:
        raw = self._safe_read_hash(key)
        owner = _safe_str(raw.get("instance_id")) or None
        ts_event_ns = _safe_int(raw.get("ts_event_ns"))
        age_ms = None if ts_event_ns is None else max(0, now_ms - int(ts_event_ns // 1_000_000))

        if not raw:
            return HeartbeatObservation(
                key=key,
                owner=owner,
                ts_event_ns=ts_event_ns,
                raw=raw,
                state=ServiceState.UNKNOWN,
                severity=ServiceSeverity.WARN,
                reason="missing_heartbeat",
            )

        if ts_event_ns is None:
            return HeartbeatObservation(
                key=key,
                owner=owner,
                ts_event_ns=ts_event_ns,
                raw=raw,
                state=ServiceState.UNKNOWN,
                severity=ServiceSeverity.WARN,
                reason="heartbeat_without_ts_event_ns",
            )

        if age_ms is not None and age_ms >= self.config.error_stale_ms:
            return HeartbeatObservation(
                key=key,
                owner=owner,
                ts_event_ns=ts_event_ns,
                raw=raw,
                state=ServiceState.DOWN,
                severity=ServiceSeverity.ERROR,
                reason=f"stale_age_ms={age_ms}",
            )

        if age_ms is not None and age_ms >= self.config.warn_stale_ms:
            return HeartbeatObservation(
                key=key,
                owner=owner,
                ts_event_ns=ts_event_ns,
                raw=raw,
                state=ServiceState.STALE,
                severity=ServiceSeverity.WARN,
                reason=f"aging_age_ms={age_ms}",
            )

        return HeartbeatObservation(
            key=key,
            owner=owner,
            ts_event_ns=ts_event_ns,
            raw=raw,
            state=ServiceState.UP,
            severity=ServiceSeverity.OK,
            reason="ok",
        )

    def _build_service_notes(
        self,
        *,
        service_name: str,
        hb: HeartbeatObservation,
        latest_state: Mapping[str, Any],
    ) -> list[str]:
        notes: list[str] = []

        if hb.state != ServiceState.UP:
            notes.append(hb.reason)

        if service_name == N.SERVICE_EXECUTION:
            execution_mode = _safe_str(latest_state.get("execution_mode"))
            if execution_mode:
                notes.append(f"execution_mode={execution_mode}")
            if _safe_bool(latest_state.get("entry_pending")) is True:
                notes.append("entry_pending")
            if _safe_bool(latest_state.get("exit_pending")) is True:
                notes.append("exit_pending")

        if service_name == N.SERVICE_RISK:
            if _safe_bool(latest_state.get("veto_entries")) is True:
                notes.append("veto_entries=1")

        if service_name == N.SERVICE_FEATURES:
            warmup_complete = _safe_bool(latest_state.get("warmup_complete"))
            if warmup_complete is False:
                notes.append("warmup_incomplete")

        return _dedupe_keep_order(notes)

    def _build_position_observation(self, raw: Mapping[str, Any]) -> PositionObservation:
        has_position = bool(_safe_bool(raw.get("has_position"), False))
        position_side = _safe_str(raw.get("position_side")) or N.POSITION_SIDE_FLAT
        qty_lots = int(_safe_int(raw.get("qty_lots"), 0) or 0)
        entry_mode = _safe_str(raw.get("entry_mode")) or N.ENTRY_MODE_UNKNOWN
        avg_price = _safe_float(raw.get("avg_price"))
        mark_price = _safe_float(raw.get("mark_price"))
        realized_pnl_day = _safe_float(raw.get("realized_pnl_day"))

        if not has_position:
            position_side = N.POSITION_SIDE_FLAT
            qty_lots = 0

        return PositionObservation(
            has_position=has_position,
            position_side=position_side,
            qty_lots=qty_lots,
            entry_mode=entry_mode,
            avg_price=avg_price,
            mark_price=mark_price,
            realized_pnl_day=realized_pnl_day,
        )

    def _build_snapshot(self, *, now_ms: int) -> SystemSnapshot:
        services: dict[str, ServiceObservation] = {}
        state_map = {name: self._safe_read_hash(key) for name, key in _STATE_KEYS_TO_OBSERVE}

        for service_name, hb_key in _SERVICE_HEALTH_KEYS:
            hb_obs = self._observe_heartbeat(key=hb_key, now_ms=now_ms)
            latest_state: dict[str, Any] = {}
            if service_name == N.SERVICE_FEATURES:
                latest_state = state_map["features"]
            elif service_name == N.SERVICE_RISK:
                latest_state = state_map["risk"]
            elif service_name == N.SERVICE_EXECUTION:
                latest_state = state_map["execution"]
            elif service_name == N.SERVICE_REPORT:
                latest_state = self._safe_read_hash(N.HASH_STATE_REPORT)

            services[service_name] = ServiceObservation(
                name=service_name,
                heartbeat=hb_obs,
                latest_state=latest_state,
                notes=self._build_service_notes(
                    service_name=service_name,
                    hb=hb_obs,
                    latest_state=latest_state,
                ),
            )

        execution_state = state_map["execution"]
        risk_state = state_map["risk"]
        mode_state = state_map["mode"]
        position_state = state_map["position"]
        runtime_state = state_map["runtime"]

        execution_mode = _safe_str(
            execution_state.get("execution_mode") or execution_state.get("mode")
        ) or N.EXECUTION_MODE_NORMAL

        control_mode = _safe_str(mode_state.get("mode")) or N.CONTROL_MODE_NORMAL
        if control_mode not in {
            N.CONTROL_MODE_NORMAL,
            N.CONTROL_MODE_SAFE,
            N.CONTROL_MODE_REPLAY,
            N.CONTROL_MODE_DISABLED,
        }:
            control_mode = N.CONTROL_MODE_NORMAL

        risk_veto_entries = _safe_bool(risk_state.get("veto_entries"))
        position = self._build_position_observation(position_state)

        summary_items: list[str] = []
        overall_status = N.HEALTH_STATUS_OK

        startup_grace_active = (
            (self._now_ns() - self._started_ns) < (self.config.startup_grace_ms * 1_000_000)
        )

        for service_name, obs in sorted(services.items()):
            if obs.heartbeat.severity == ServiceSeverity.ERROR:
                overall_status = N.HEALTH_STATUS_ERROR
                summary_items.append(f"{service_name}:{obs.heartbeat.reason}")
            elif obs.heartbeat.severity == ServiceSeverity.WARN and overall_status != N.HEALTH_STATUS_ERROR:
                overall_status = N.HEALTH_STATUS_WARN
                summary_items.append(f"{service_name}:{obs.heartbeat.reason}")

        if startup_grace_active and overall_status != N.HEALTH_STATUS_ERROR:
            summary_items.append("startup_grace_active")

        if execution_mode == N.EXECUTION_MODE_FATAL:
            overall_status = N.HEALTH_STATUS_ERROR
            summary_items.append("execution_mode:FATAL")
        elif execution_mode == N.EXECUTION_MODE_DEGRADED and overall_status != N.HEALTH_STATUS_ERROR:
            overall_status = N.HEALTH_STATUS_WARN
            summary_items.append("execution_mode:DEGRADED")
        elif execution_mode == N.EXECUTION_MODE_EXIT_ONLY and overall_status == N.HEALTH_STATUS_OK:
            overall_status = N.HEALTH_STATUS_WARN
            summary_items.append("execution_mode:EXIT_ONLY")

        if control_mode == N.CONTROL_MODE_DISABLED and overall_status == N.HEALTH_STATUS_OK:
            overall_status = N.HEALTH_STATUS_WARN
            summary_items.append("control_mode:DISABLED")
        elif control_mode == N.CONTROL_MODE_SAFE and overall_status == N.HEALTH_STATUS_OK:
            overall_status = N.HEALTH_STATUS_WARN
            summary_items.append("control_mode:SAFE")
        elif control_mode == N.CONTROL_MODE_REPLAY and overall_status == N.HEALTH_STATUS_OK:
            summary_items.append("control_mode:REPLAY")

        if risk_veto_entries is True and overall_status == N.HEALTH_STATUS_OK:
            summary_items.append("risk_blocks_entries")

        if position.has_position:
            summary_items.append(
                f"position:{position.position_side}:entry_mode={position.entry_mode or N.ENTRY_MODE_UNKNOWN}"
            )

        runtime_mode = _safe_str(runtime_state.get("runtime_mode"))
        if runtime_mode:
            summary_items.append(f"runtime_mode={runtime_mode}")

        summary = ",".join(_dedupe_keep_order(summary_items)) or "all_ok"

        diagnostics = {
            "services_observed": len(services),
            "execution_mode": execution_mode,
            "control_mode": control_mode,
            "risk_veto_entries": risk_veto_entries,
            "position_open": position.has_position,
        }

        return SystemSnapshot(
            ts_ms=now_ms,
            ts_ns=self._now_ns(),
            ts_utc=self._utc_now_iso(),
            monitor_instance_id=self.config.instance_id,
            overall_status=overall_status,
            summary=summary,
            startup_grace_active=startup_grace_active,
            services=services,
            execution_mode=execution_mode,
            control_mode=control_mode,
            risk_veto_entries=risk_veto_entries,
            position=position,
            diagnostics=diagnostics,
        )

    def _log_health(self, snapshot: SystemSnapshot) -> None:
        fingerprint = snapshot.stable_fingerprint()
        changed = fingerprint != self._last_health_fingerprint
        if self.config.log_health_on_change_only and not changed:
            return

        level_name = "info"
        if snapshot.overall_status == N.HEALTH_STATUS_WARN:
            level_name = "warning"
        elif snapshot.overall_status == N.HEALTH_STATUS_ERROR:
            level_name = "error"

        log_fn = getattr(self.log, level_name)
        log_fn(
            (
                "health overall_status=%s summary=%s execution_mode=%s "
                "control_mode=%s has_position=%s position_side=%s entry_mode=%s"
            ),
            snapshot.overall_status,
            snapshot.summary,
            snapshot.execution_mode,
            snapshot.control_mode,
            snapshot.position.has_position,
            snapshot.position.position_side,
            snapshot.position.entry_mode,
        )

    def _emit_health_if_due(self, *, snapshot: SystemSnapshot, now_ms: int) -> None:
        if (now_ms - self._last_health_publish_ms) < self.config.health_publish_interval_ms:
            return

        fingerprint = snapshot.stable_fingerprint()
        changed = fingerprint != self._last_health_fingerprint

        if changed or self.config.emit_health_when_unchanged:
            self._publish_stream_event(
                N.STREAM_SYSTEM_HEALTH,
                snapshot.to_health_event(),
                maxlen=self.config.stream_health_maxlen,
            )
            self._last_health_fingerprint = fingerprint

        self._last_health_publish_ms = now_ms

    def _emit_diagnostics_if_due(self, *, snapshot: SystemSnapshot, now_ms: int) -> None:
        if (now_ms - self._last_diag_publish_ms) < self.config.diagnostic_publish_interval_ms:
            return

        fingerprint = snapshot.stable_fingerprint()
        changed = fingerprint != self._last_diag_fingerprint

        if changed or self.config.emit_diagnostics_when_unchanged:
            self._publish_stream_event(
                N.STREAM_SYSTEM_HEALTH,
                snapshot.to_diagnostic_payload(),
                maxlen=self.config.stream_health_maxlen,
            )
            self._last_diag_fingerprint = fingerprint

        self._last_diag_publish_ms = now_ms

    def _emit_error_events_if_needed(self, *, snapshot: SystemSnapshot) -> None:
        if snapshot.overall_status != N.HEALTH_STATUS_ERROR:
            return

        signature = snapshot.stable_fingerprint()
        if signature == self._last_error_signature:
            return

        payload = {
            "event_type": "system_error",
            "ts_ms": snapshot.ts_ms,
            "ts_ns": snapshot.ts_ns,
            "ts_utc": snapshot.ts_utc,
            "service_name": N.SERVICE_MONITOR,
            "monitor_instance_id": snapshot.monitor_instance_id,
            "overall_status": snapshot.overall_status,
            "summary": snapshot.summary,
            "execution_mode": snapshot.execution_mode,
            "control_mode": snapshot.control_mode,
            "risk_veto_entries": "1" if snapshot.risk_veto_entries else "0",
            "position": json.dumps(
                snapshot.position.to_public_dict(),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
            "services": json.dumps(
                {key: value.to_public_dict() for key, value in sorted(snapshot.services.items())},
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
        }
        self._publish_stream_event(
            N.STREAM_SYSTEM_ERRORS,
            payload,
            maxlen=self.config.stream_error_maxlen,
        )
        self._last_error_signature = signature

    # ------------------------------------------------------------------
    # Control plane publication
    # ------------------------------------------------------------------

    def publish_command(self, command_type: str, **payload: Any) -> str:
        raw_cmd = _safe_str(command_type).upper()
        if raw_cmd not in {
            N.CMD_PARAMS_RELOAD,
            N.CMD_PAUSE_TRADING,
            N.CMD_RESUME_TRADING,
            N.CMD_FORCE_FLATTEN,
            N.CMD_SET_MODE,
        }:
            raise ControlPlaneError(f"unsupported control-plane command: {raw_cmd!r}")

        event: dict[str, Any] = {
            "ts_ns": str(self._now_ns()),
            "service_name": N.SERVICE_MONITOR,
            "instance_id": self.config.instance_id,
            "cmd": raw_cmd,
        }

        if raw_cmd == N.CMD_SET_MODE:
            mode = _safe_str(payload.get("mode")).upper()
            allowed_modes = {
                N.CONTROL_MODE_NORMAL,
                N.CONTROL_MODE_SAFE,
                N.CONTROL_MODE_REPLAY,
                N.CONTROL_MODE_DISABLED,
            }
            if mode not in allowed_modes:
                raise ControlPlaneError(f"invalid control mode: {mode!r}")
            event["mode"] = mode

        for key, value in payload.items():
            if key == "mode" and raw_cmd != N.CMD_SET_MODE:
                continue
            if value is None:
                continue
            event[str(key)] = value

        return self._publish_stream_event(
            N.STREAM_CMD_MME,
            event,
            maxlen=self.config.stream_cmd_maxlen,
        )

    # ------------------------------------------------------------------
    # Runtime loop
    # ------------------------------------------------------------------

    def start(self) -> int:
        self._acquire_lock_or_die()
        self._publish_heartbeat(status=N.HEALTH_STATUS_OK, message="monitor_started")

        try:
            while not self._shutdown.is_set():
                now_ms = self._now_ms()
                self._refresh_lock_if_due()

                snapshot = self._build_snapshot(now_ms=now_ms)
                self._log_health(snapshot)
                self._emit_health_if_due(snapshot=snapshot, now_ms=now_ms)
                self._emit_diagnostics_if_due(snapshot=snapshot, now_ms=now_ms)
                self._emit_error_events_if_needed(snapshot=snapshot)
                self._publish_heartbeat(status=snapshot.overall_status, message=snapshot.summary)

                self._shutdown.wait(self.config.poll_interval_ms / 1000.0)
        finally:
            self._publish_shutdown_heartbeat()
            self._release_lock()

        return 0


# ============================================================================
# Canonical entrypoint
# ============================================================================


def _resolve_settings_from_context(context: Any) -> AppSettings:
    settings = getattr(context, "settings", None)
    if settings is None:
        settings = get_settings()
    if not isinstance(settings, AppSettings):
        raise MonitorError(
            "monitor requires context.settings or get_settings() returning AppSettings"
        )
    return settings


def _resolve_redis_client_from_context(context: Any) -> Any:
    redis_runtime = getattr(context, "redis", None)
    if redis_runtime is None:
        raise MonitorError("monitor.run(context) requires context.redis")
    if hasattr(redis_runtime, "sync"):
        return redis_runtime.sync
    return redis_runtime


def run(context: Any) -> int:
    _validate_name_surface_or_die()
    _validate_context_or_die(context)

    settings = _resolve_settings_from_context(context)
    redis_client = _resolve_redis_client_from_context(context)
    config = MonitorConfig.from_runtime(settings=settings, context=context)

    service = MonitorService(
        redis_client=redis_client,
        clock=context.clock,
        shutdown=context.shutdown,
        config=config,
        logger=LOGGER,
    )
    return service.start()

# =============================================================================
# Batch 15 freeze hardening: missing-state visibility
# =============================================================================

_BATCH15_MONITOR_OPS_FREEZE_VERSION = "1"

_BATCH15_CRITICAL_STATE_HASHES: Final[tuple[tuple[str, str, str], ...]] = (
    ("execution", N.HASH_STATE_EXECUTION, N.HEALTH_STATUS_ERROR),
    ("position", N.HASH_STATE_POSITION_MME, N.HEALTH_STATUS_ERROR),
    ("risk", N.HASH_STATE_RISK, N.HEALTH_STATUS_ERROR),
    ("features", N.HASH_STATE_FEATURES_MME_FUT, N.HEALTH_STATUS_WARN),
    ("runtime", N.HASH_STATE_RUNTIME, N.HEALTH_STATUS_WARN),
)


def _batch15_read_hash(client: Any, key: str) -> dict[str, Any]:
    try:
        raw = RX.hgetall(key, client=client)
    except Exception:
        raw = client.hgetall(key)
    if raw is None:
        return {}
    return dict(raw)


def _batch15_state_missing_status(missing: Sequence[tuple[str, str]]) -> str:
    labels = {label for label, _status in missing}
    if {"execution", "position", "risk"} & labels:
        return N.HEALTH_STATUS_ERROR
    if missing:
        return N.HEALTH_STATUS_WARN
    return N.HEALTH_STATUS_OK


def _batch15_missing_state_hashes(client: Any) -> list[tuple[str, str]]:
    missing: list[tuple[str, str]] = []
    for label, key, severity in _BATCH15_CRITICAL_STATE_HASHES:
        if not _batch15_read_hash(client, key):
            missing.append((label, severity))
    return missing


_BATCH15_ORIGINAL_BUILD_SNAPSHOT = MonitorService._build_snapshot


def _batch15_build_snapshot(self: MonitorService, *args: Any, **kwargs: Any) -> SystemSnapshot:
    snapshot = _BATCH15_ORIGINAL_BUILD_SNAPSHOT(self, *args, **kwargs)
    missing = _batch15_missing_state_hashes(self.redis)

    if not missing:
        diagnostics = dict(snapshot.diagnostics)
        diagnostics["missing_state_hashes"] = []
        return SystemSnapshot(
            ts_ms=snapshot.ts_ms,
            ts_ns=snapshot.ts_ns,
            ts_utc=snapshot.ts_utc,
            monitor_instance_id=snapshot.monitor_instance_id,
            overall_status=snapshot.overall_status,
            summary=snapshot.summary,
            startup_grace_active=snapshot.startup_grace_active,
            services=snapshot.services,
            execution_mode=snapshot.execution_mode,
            control_mode=snapshot.control_mode,
            risk_veto_entries=snapshot.risk_veto_entries,
            position=snapshot.position,
            diagnostics=diagnostics,
        )

    missing_labels = [label for label, _severity in missing]
    missing_status = _batch15_state_missing_status(missing)
    overall_status = snapshot.overall_status

    if missing_status == N.HEALTH_STATUS_ERROR:
        overall_status = N.HEALTH_STATUS_ERROR
    elif missing_status == N.HEALTH_STATUS_WARN and overall_status == N.HEALTH_STATUS_OK:
        overall_status = N.HEALTH_STATUS_WARN

    summary = snapshot.summary
    addition = "state_missing:" + "|".join(missing_labels)
    if summary and summary != "all_ok":
        summary = summary + "," + addition
    else:
        summary = addition

    diagnostics = dict(snapshot.diagnostics)
    diagnostics["missing_state_hashes"] = missing_labels

    return SystemSnapshot(
        ts_ms=snapshot.ts_ms,
        ts_ns=snapshot.ts_ns,
        ts_utc=snapshot.ts_utc,
        monitor_instance_id=snapshot.monitor_instance_id,
        overall_status=overall_status,
        summary=summary,
        startup_grace_active=snapshot.startup_grace_active,
        services=snapshot.services,
        execution_mode=snapshot.execution_mode,
        control_mode=snapshot.control_mode,
        risk_veto_entries=snapshot.risk_veto_entries,
        position=snapshot.position,
        diagnostics=diagnostics,
    )


MonitorService._build_snapshot = _batch15_build_snapshot
