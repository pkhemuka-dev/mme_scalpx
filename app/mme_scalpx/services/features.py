from __future__ import annotations

"""
app/mme_scalpx/services/features.py

Freeze-grade provider-aware feature publisher for ScalpX MME family build.

Ownership
---------
This module OWNS:
- deterministic feature publication for the live/replay feature lane
- stable ``family_features`` publication for downstream strategy consumers
- stable ``family_surfaces`` publication for richer audit / doctrine consumption
- provider-aware active/Dhan snapshot consumption
- common futures, option, cross-option, strike ladder, OI-wall, regime, and
  tradability surfaces
- fan-out into the five feature-family surface modules:
  MIST, MISB, MISC, MISR, MISO
- Redis feature hash / feature stream publication
- feature heartbeat and feature error publication

This module DOES NOT own:
- raw feed ingestion
- provider selection or failover policy
- strategy decisions
- doctrine state machines
- cooldowns / re-entry mutation
- broker execution truth
- risk truth mutation
- order placement

Frozen laws
-----------
- Features publish facts and support surfaces only.
- Price action and futures flow remain trigger truth.
- OI wall / strike ladder context is slow-context quality surface only.
- OI wall context may become a veto / quality input downstream; it is not an
  entry trigger here.
- No doctrine-leaf entry logic lives in this file.
- No silent provider fallback is performed here. Provider truth is consumed as
  published.
"""

import contextlib
import copy
import importlib
import json
import logging
import math
import time
from dataclasses import dataclass
from typing import Any, Final, Mapping, MutableMapping, Sequence

from app.mme_scalpx.core import models as M
from app.mme_scalpx.core import names as N
from app.mme_scalpx.core import redisx as RX

try:
    from app.mme_scalpx.core.settings import get_settings
except Exception:  # pragma: no cover
    get_settings = None  # type: ignore[assignment]


LOGGER = logging.getLogger("app.mme_scalpx.services.features")


# =============================================================================
# Constants
# =============================================================================

EPSILON: Final[float] = 1e-8

DEFAULT_POLL_INTERVAL_MS: Final[int] = 100
DEFAULT_HEARTBEAT_TTL_MS: Final[int] = 15_000
DEFAULT_HEARTBEAT_REFRESH_MS: Final[int] = 5_000
DEFAULT_STREAM_MAXLEN: Final[int] = 10_000

DEFAULT_PREMIUM_FLOOR: Final[float] = 40.0
DEFAULT_TARGET_POINTS: Final[float] = 5.0
DEFAULT_STOP_POINTS: Final[float] = 4.0
DEFAULT_FUTURES_STALE_MS: Final[float] = 1_000.0
DEFAULT_OPTION_STALE_MS: Final[float] = 1_200.0
DEFAULT_CONTEXT_STALE_MS: Final[float] = 5_000.0
DEFAULT_SYNC_MAX_MS: Final[float] = 300.0
DEFAULT_PACKET_GAP_HARD_MS: Final[float] = 1_000.0

DEFAULT_REGIME_LOWVOL_RATIO_MAX: Final[float] = 0.80
DEFAULT_REGIME_FAST_RATIO_MIN: Final[float] = 1.50

DEFAULT_OI_WALL_STRONG_MIN: Final[float] = 0.62
DEFAULT_OI_WALL_NEAR_STRIKES: Final[float] = 1.0

REGIME_LOWVOL: Final[str] = "LOWVOL"
REGIME_NORMAL: Final[str] = "NORMAL"
REGIME_FAST: Final[str] = "FAST"
REGIME_UNKNOWN: Final[str] = "UNKNOWN"

FAMILY_ORDER: Final[tuple[str, ...]] = (
    N.STRATEGY_FAMILY_MIST,
    N.STRATEGY_FAMILY_MISB,
    N.STRATEGY_FAMILY_MISC,
    N.STRATEGY_FAMILY_MISR,
    N.STRATEGY_FAMILY_MISO,
)

CLASSIC_FAMILIES: Final[tuple[str, ...]] = (
    N.STRATEGY_FAMILY_MIST,
    N.STRATEGY_FAMILY_MISB,
    N.STRATEGY_FAMILY_MISC,
    N.STRATEGY_FAMILY_MISR,
)

BRANCHES: Final[tuple[str, ...]] = (
    N.BRANCH_CALL,
    N.BRANCH_PUT,
)

BRANCH_TO_SIDE: Final[dict[str, str]] = {
    N.BRANCH_CALL: N.SIDE_CALL,
    N.BRANCH_PUT: N.SIDE_PUT,
}

SIDE_TO_BRANCH: Final[dict[str, str]] = {
    N.SIDE_CALL: N.BRANCH_CALL,
    N.SIDE_PUT: N.BRANCH_PUT,
}

FAMILY_TO_SURFACE_MODULE: Final[dict[str, str]] = {
    N.STRATEGY_FAMILY_MIST: "app.mme_scalpx.services.feature_family.mist_surface",
    N.STRATEGY_FAMILY_MISB: "app.mme_scalpx.services.feature_family.misb_surface",
    N.STRATEGY_FAMILY_MISC: "app.mme_scalpx.services.feature_family.misc_surface",
    N.STRATEGY_FAMILY_MISR: "app.mme_scalpx.services.feature_family.misr_surface",
    N.STRATEGY_FAMILY_MISO: "app.mme_scalpx.services.feature_family.miso_surface",
}

_SHARED_MODULE_PATHS: Final[dict[str, str]] = {
    "common": "app.mme_scalpx.services.feature_family.common",
    "contracts": "app.mme_scalpx.services.feature_family.contracts",
    "futures_core": "app.mme_scalpx.services.feature_family.futures_core",
    "option_core": "app.mme_scalpx.services.feature_family.option_core",
    "tradability": "app.mme_scalpx.services.feature_family.tradability",
    "regime": "app.mme_scalpx.services.feature_family.regime",
    "strike_selection": "app.mme_scalpx.services.feature_family.strike_selection",
}

_PROVIDER_ALLOWED_STATUSES: Final[tuple[str, ...]] = (
    N.PROVIDER_STATUS_HEALTHY,
    N.PROVIDER_STATUS_DEGRADED,
    N.PROVIDER_STATUS_STALE,
)

_PROVIDER_ALLOWED_IDS: Final[tuple[str, ...]] = (
    N.PROVIDER_ZERODHA,
    N.PROVIDER_DHAN,
)


# =============================================================================
# Exceptions
# =============================================================================


class FeatureSurfaceError(RuntimeError):
    """Raised when feature-surface publication cannot be completed safely."""


# =============================================================================
# Small helpers
# =============================================================================


def _name(name: str, default: Any = None) -> Any:
    return getattr(N, name, default)


def _json_dumps(value: Any) -> str:
    return json.dumps(
        _jsonable(value),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        allow_nan=False,
    )


def _json_loads_or(value: Any, default: Any) -> Any:
    if value is None:
        return default
    if isinstance(value, (dict, list, tuple)):
        return value
    text = _safe_str(value)
    if not text:
        return default
    try:
        return json.loads(text)
    except Exception:
        return default


def _jsonable(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if math.isfinite(value):
            return value
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(v) for v in value]
    if hasattr(value, "to_dict"):
        with contextlib.suppress(Exception):
            return _jsonable(value.to_dict())
    if hasattr(value, "__dict__"):
        return _jsonable(vars(value))
    return str(value)


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, bytes):
        with contextlib.suppress(Exception):
            return value.decode("utf-8").strip()
        return default
    text = str(value).strip()
    return text if text else default


def _safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = _safe_str(value).lower()
    if text in {"1", "true", "yes", "y", "on", "ok", "healthy"}:
        return True
    if text in {"0", "false", "no", "n", "off", "none", "null"}:
        return False
    return default


def _safe_int(value: Any, default: int = 0) -> int:
    if isinstance(value, bool) or value is None:
        return default
    try:
        text = _safe_str(value)
        if not text:
            return default
        return int(float(text))
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    if isinstance(value, bool) or value is None:
        return default
    try:
        text = _safe_str(value)
        if not text:
            return default
        number = float(text)
    except Exception:
        return default
    if not math.isfinite(number):
        return default
    return float(number)


def _safe_float_or_none(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        text = _safe_str(value)
        if not text:
            return None
        number = float(text)
    except Exception:
        return None
    if not math.isfinite(number):
        return None
    return float(number)


def _ratio(numer: float, denom: float, default: float = 0.0) -> float:
    if abs(denom) <= EPSILON:
        return default
    return numer / denom


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _coalesce(*values: Any) -> Any:
    for value in values:
        if value not in (None, ""):
            return value
    return None


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    if hasattr(value, "to_dict"):
        with contextlib.suppress(Exception):
            out = value.to_dict()
            if isinstance(out, Mapping):
                return out
    if hasattr(value, "__dict__"):
        return vars(value)
    return {}


def _nested_get(root: Any, *path: str, default: Any = None) -> Any:
    current = root
    for key in path:
        if current is None:
            return default
        if isinstance(current, Mapping):
            current = current.get(key)
        else:
            current = getattr(current, key, None)
    return default if current is None else current


def _pick(mapping: Mapping[str, Any] | None, *keys: str, default: Any = None) -> Any:
    if not isinstance(mapping, Mapping):
        return default
    for key in keys:
        if key in mapping and mapping[key] not in (None, ""):
            return mapping[key]
    return default


def _decode_hash(raw: Mapping[Any, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in raw.items():
        out[_safe_str(key)] = _decode_value(value)
    return out


def _decode_value(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _clean_hash(raw: Mapping[Any, Any]) -> dict[str, Any]:
    decoded = _decode_hash(raw)
    cleaned: dict[str, Any] = {}
    for key, value in decoded.items():
        text = _safe_str(value)
        if text in {"", "None", "none", "null", "NULL"}:
            cleaned[key] = None
            continue
        if (text.startswith("{") and text.endswith("}")) or (
            text.startswith("[") and text.endswith("]")
        ):
            cleaned[key] = _json_loads_or(text, text)
            continue
        cleaned[key] = value
    return cleaned


def _provider_id(value: Any, default: str = N.PROVIDER_ZERODHA) -> str:
    text = _safe_str(value, default)
    return text if text in _PROVIDER_ALLOWED_IDS else default


def _provider_status(value: Any, default: str = N.PROVIDER_STATUS_STALE) -> str:
    text = _safe_str(value, default)
    return text if text in _PROVIDER_ALLOWED_STATUSES else default


def _runtime_mode(value: Any, default: str) -> str:
    text = _safe_str(value, default)
    return text if text else default


def _surface_key(family_id: str, branch_id: str) -> str:
    return f"{family_id.lower()}_{branch_id.lower()}"


def _deep_patch_existing(target: MutableMapping[str, Any], patch: Mapping[str, Any]) -> None:
    for key, value in patch.items():
        if key not in target:
            continue
        if isinstance(target[key], MutableMapping) and isinstance(value, Mapping):
            _deep_patch_existing(target[key], value)
        else:
            target[key] = value


def _load_module(path: str) -> Any | None:
    try:
        return importlib.import_module(path)
    except Exception as exc:
        LOGGER.warning("feature_family_module_unavailable module=%s error=%s", path, exc)
        return None


def _call_first(
    module: Any | None,
    function_names: Sequence[str],
    *args: Any,
    **kwargs: Any,
) -> Any | None:
    if module is None:
        return None
    for name in function_names:
        func = getattr(module, name, None)
        if not callable(func):
            continue
        try:
            return func(*args, **kwargs)
        except TypeError:
            with contextlib.suppress(Exception):
                return func(*args)
        except Exception as exc:
            LOGGER.warning(
                "feature_family_function_failed module=%s function=%s error=%s",
                getattr(module, "__name__", "unknown"),
                name,
                exc,
            )
            return None
    return None


# =============================================================================
# Snapshot views
# =============================================================================


@dataclass(frozen=True, slots=True)
class SnapshotFrameView:
    kind: str
    futures: Mapping[str, Any]
    selected_option: Mapping[str, Any]
    dhan_context: Mapping[str, Any]
    ts_event_ns: int | None
    ts_recv_ns: int | None
    provider_id: str | None
    valid: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "futures": dict(self.futures),
            "selected_option": dict(self.selected_option),
            "dhan_context": dict(self.dhan_context),
            "ts_event_ns": self.ts_event_ns,
            "ts_recv_ns": self.ts_recv_ns,
            "provider_id": self.provider_id,
            "valid": self.valid,
            "reason": self.reason,
        }


# =============================================================================
# Redis snapshot reader
# =============================================================================


class SnapshotReader:
    def __init__(self, redis_client: Any):
        self.redis = redis_client

    def read_hash(self, key: str) -> dict[str, Any]:
        if not key:
            return {}
        try:
            raw = self.redis.hgetall(key)
        except Exception:
            return {}
        return _clean_hash(raw or {})

    def read_provider_runtime(self) -> M.ProviderRuntimeState | Mapping[str, Any] | None:
        payload = self.read_hash(N.HASH_STATE_PROVIDER_RUNTIME)
        if not payload:
            return None
        return self._model_or_mapping(M.ProviderRuntimeState, payload)

    def read_dhan_context(self) -> M.DhanContextState | Mapping[str, Any] | None:
        payload = self.read_hash(N.HASH_STATE_DHAN_CONTEXT)
        if not payload:
            return None
        return self._model_or_mapping(M.DhanContextState, payload)

    def read_active_frame(
        self,
        dhan_context: M.DhanContextState | Mapping[str, Any] | None = None,
    ) -> SnapshotFrameView | None:
        fut = self.read_hash(N.HASH_STATE_SNAPSHOT_MME_FUT_ACTIVE)
        if not fut:
            fut = self.read_hash(N.HASH_STATE_SNAPSHOT_MME_FUT)

        opt = self.read_hash(N.HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ACTIVE)
        if not opt:
            opt = self.read_hash(N.HASH_STATE_SNAPSHOT_MME_OPT_SELECTED)

        return self._frame_view(
            kind="active",
            futures=fut,
            selected_option=opt,
            dhan_context=_as_mapping(dhan_context),
        )

    def read_dhan_frame(
        self,
        dhan_context: M.DhanContextState | Mapping[str, Any] | None = None,
    ) -> SnapshotFrameView | None:
        fut = self.read_hash(N.HASH_STATE_SNAPSHOT_MME_FUT_DHAN)
        opt = self.read_hash(N.HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_DHAN)
        return self._frame_view(
            kind="dhan",
            futures=fut,
            selected_option=opt,
            dhan_context=_as_mapping(dhan_context),
        )

    @staticmethod
    def _model_or_mapping(model_cls: Any, payload: Mapping[str, Any]) -> Any:
        if hasattr(model_cls, "from_mapping"):
            with contextlib.suppress(Exception):
                return model_cls.from_mapping(payload)
        if hasattr(model_cls, "from_dict"):
            with contextlib.suppress(Exception):
                return model_cls.from_dict(payload)
        with contextlib.suppress(Exception):
            return model_cls(**payload)
        return dict(payload)

    @staticmethod
    def _frame_view(
        *,
        kind: str,
        futures: Mapping[str, Any],
        selected_option: Mapping[str, Any],
        dhan_context: Mapping[str, Any],
    ) -> SnapshotFrameView | None:
        if not futures and not selected_option and not dhan_context:
            return None

        ts_values = [
            _safe_int(_pick(futures, "ts_event_ns", "event_ts_ns"), 0),
            _safe_int(_pick(selected_option, "ts_event_ns", "event_ts_ns"), 0),
        ]
        ts_event_ns = max([v for v in ts_values if v > 0], default=0) or None

        recv_values = [
            _safe_int(_pick(futures, "ts_recv_ns", "recv_ts_ns"), 0),
            _safe_int(_pick(selected_option, "ts_recv_ns", "recv_ts_ns"), 0),
        ]
        ts_recv_ns = max([v for v in recv_values if v > 0], default=0) or None

        provider_id = _safe_str(
            _coalesce(
                _pick(selected_option, "provider_id"),
                _pick(futures, "provider_id"),
                _pick(dhan_context, "provider_id"),
            )
        ) or None

        has_price = (
            _safe_float(_pick(futures, "ltp", "last_price"), 0.0) > 0.0
            or _safe_float(_pick(selected_option, "ltp", "last_price"), 0.0) > 0.0
        )
        valid = has_price or bool(dhan_context)
        reason = "OK" if valid else "EMPTY"

        return SnapshotFrameView(
            kind=kind,
            futures=dict(futures),
            selected_option=dict(selected_option),
            dhan_context=dict(dhan_context),
            ts_event_ns=ts_event_ns,
            ts_recv_ns=ts_recv_ns,
            provider_id=provider_id,
            valid=valid,
            reason=reason,
        )


# =============================================================================
# Feature engine
# =============================================================================


class FeatureEngine:
    def __init__(self, *, redis_client: Any, logger: logging.Logger | None = None):
        self.redis = redis_client
        self.log = logger or LOGGER
        self.reader = SnapshotReader(redis_client)
        self.modules = {name: _load_module(path) for name, path in _SHARED_MODULE_PATHS.items()}
        self.family_modules = {
            family: _load_module(path) for family, path in FAMILY_TO_SURFACE_MODULE.items()
        }

    def build_payload(self, *, now_ns: int | None = None) -> dict[str, Any]:
        generated_at_ns = int(now_ns or time.time_ns())

        provider_runtime_obj = self.reader.read_provider_runtime()
        dhan_context_obj = self.reader.read_dhan_context()
        provider_runtime = self._provider_runtime_mapping(provider_runtime_obj)
        dhan_context = _as_mapping(dhan_context_obj)

        active_frame = self.reader.read_active_frame(dhan_context_obj)
        dhan_frame = self.reader.read_dhan_frame(dhan_context_obj)

        active_futures = dict(active_frame.futures) if active_frame else {}
        active_selected = dict(active_frame.selected_option) if active_frame else {}
        dhan_futures = dict(dhan_frame.futures) if dhan_frame else {}
        dhan_selected = dict(dhan_frame.selected_option) if dhan_frame else {}

        shared_core = self._build_shared_core(
            generated_at_ns=generated_at_ns,
            provider_runtime=provider_runtime,
            dhan_context=dhan_context,
            active_frame=active_frame,
            dhan_frame=dhan_frame,
            active_futures=active_futures,
            active_selected=active_selected,
            dhan_futures=dhan_futures,
            dhan_selected=dhan_selected,
        )

        family_surfaces = self._build_family_surfaces(
            generated_at_ns=generated_at_ns,
            provider_runtime=provider_runtime,
            shared_core=shared_core,
        )

        family_features = self._build_family_features(
            generated_at_ns=generated_at_ns,
            active_frame=active_frame,
            dhan_frame=dhan_frame,
            provider_runtime=provider_runtime,
            shared_core=shared_core,
            family_surfaces=family_surfaces,
        )

        family_frames = self._build_family_frames(
            generated_at_ns=generated_at_ns,
            provider_runtime=provider_runtime,
            family_surfaces=family_surfaces,
            family_features=family_features,
        )

        feature_state = self._build_feature_state(
            generated_at_ns=generated_at_ns,
            active_frame=active_frame,
            shared_core=shared_core,
            family_features=family_features,
        )

        return {
            "schema_version": _name("DEFAULT_SCHEMA_VERSION", 1),
            "service": N.SERVICE_FEATURES,
            "generated_at_ns": generated_at_ns,
            "frame_id": f"features-{generated_at_ns}",
            "frame_ts_ns": generated_at_ns,
            "ts_event_ns": generated_at_ns,
            "frame_valid": bool(_nested_get(family_features, "snapshot", "valid", default=False)),
            "warmup_complete": bool(
                _nested_get(family_features, "stage_flags", "warmup_complete", default=False)
            ),
            "family_features": family_features,
            "family_surfaces": family_surfaces,
            "family_frames": {key: _object_to_dict(value) for key, value in family_frames.items()},
            "feature_state": feature_state,
            "provider_runtime": provider_runtime,
            "shared_core": shared_core,
            "explain": {
                "ownership": "features_only",
                "oi_wall_law": "context_quality_surface_not_trigger",
                "strategy_decision_logic_present": False,
                "provider_failover_policy_present": False,
            },
        }

    def _provider_runtime_mapping(
        self,
        value: M.ProviderRuntimeState | Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        mapping = dict(_as_mapping(value))

        active_fut = _provider_id(
            _coalesce(
                _pick(mapping, "active_futures_provider_id"),
                _pick(mapping, "active_future_provider_id"),
                _pick(mapping, "futures_provider_id"),
            ),
            default=N.PROVIDER_ZERODHA,
        )
        active_opt = _provider_id(
            _coalesce(
                _pick(mapping, "active_selected_option_provider_id"),
                _pick(mapping, "selected_option_provider_id"),
                _pick(mapping, "option_provider_id"),
            ),
            default=active_fut,
        )
        context_provider_raw = _coalesce(
            _pick(mapping, "active_option_context_provider_id"),
            _pick(mapping, "option_context_provider_id"),
            _pick(mapping, "context_provider_id"),
        )
        context_provider = (
            _provider_id(context_provider_raw, default=N.PROVIDER_DHAN)
            if context_provider_raw not in (None, "")
            else None
        )

        execution_provider_raw = _coalesce(
            _pick(mapping, "active_execution_provider_id"),
            _pick(mapping, "execution_provider_id"),
            _pick(mapping, "execution_primary_provider_id"),
        )
        fallback_execution_raw = _coalesce(
            _pick(mapping, "fallback_execution_provider_id"),
            _pick(mapping, "execution_fallback_provider_id"),
        )

        futures_status = _provider_status(
            _coalesce(
                _pick(mapping, "futures_provider_status"),
                _pick(mapping, "active_futures_provider_status"),
                _pick(mapping, "futures_status"),
            )
        )
        selected_status = _provider_status(
            _coalesce(
                _pick(mapping, "selected_option_provider_status"),
                _pick(mapping, "active_selected_option_provider_status"),
                _pick(mapping, "selected_option_status"),
            )
        )
        context_status_raw = _coalesce(
            _pick(mapping, "option_context_provider_status"),
            _pick(mapping, "active_option_context_provider_status"),
            _pick(mapping, "context_status"),
        )
        context_status = (
            _provider_status(context_status_raw)
            if context_status_raw not in (None, "")
            else None
        )
        execution_status_raw = _coalesce(
            _pick(mapping, "execution_provider_status"),
            _pick(mapping, "execution_primary_status"),
            _pick(mapping, "active_execution_provider_status"),
        )

        family_runtime_mode = _runtime_mode(
            _pick(mapping, "family_runtime_mode"),
            _name("FAMILY_RUNTIME_MODE_OBSERVE_ONLY", "observe_only"),
        )

        return {
            "active_futures_provider_id": active_fut,
            "active_selected_option_provider_id": active_opt,
            "active_option_context_provider_id": context_provider,
            "active_execution_provider_id": (
                _provider_id(execution_provider_raw, default=N.PROVIDER_ZERODHA)
                if execution_provider_raw not in (None, "")
                else None
            ),
            "fallback_execution_provider_id": (
                _provider_id(fallback_execution_raw, default=N.PROVIDER_DHAN)
                if fallback_execution_raw not in (None, "")
                else None
            ),
            "provider_runtime_mode": _safe_str(
                _pick(mapping, "provider_runtime_mode", "runtime_mode"),
                "NORMAL",
            ),
            "family_runtime_mode": family_runtime_mode,
            "futures_provider_status": futures_status,
            "selected_option_provider_status": selected_status,
            "option_context_provider_status": context_status,
            "execution_provider_status": (
                _provider_status(execution_status_raw)
                if execution_status_raw not in (None, "")
                else None
            ),
            "raw": mapping,
        }

    def _build_shared_core(
        self,
        *,
        generated_at_ns: int,
        provider_runtime: Mapping[str, Any],
        dhan_context: Mapping[str, Any],
        active_frame: SnapshotFrameView | None,
        dhan_frame: SnapshotFrameView | None,
        active_futures: Mapping[str, Any],
        active_selected: Mapping[str, Any],
        dhan_futures: Mapping[str, Any],
        dhan_selected: Mapping[str, Any],
    ) -> dict[str, Any]:
        futures_core = self.modules.get("futures_core")
        option_core = self.modules.get("option_core")
        tradability = self.modules.get("tradability")
        regime_module = self.modules.get("regime")
        strike_module = self.modules.get("strike_selection")

        active_futures_surface = (
            _call_first(
                futures_core,
                ("build_active_futures_surface", "build_futures_surface"),
                active_futures,
                provider_runtime=provider_runtime,
                now_ns=generated_at_ns,
            )
            or self._fallback_futures_surface(
                active_futures,
                role="active_futures",
                provider_id=provider_runtime["active_futures_provider_id"],
            )
        )

        dhan_futures_surface = (
            _call_first(
                futures_core,
                ("build_dhan_futures_surface", "build_futures_surface"),
                dhan_futures,
                provider_runtime=provider_runtime,
                now_ns=generated_at_ns,
            )
            or self._fallback_futures_surface(
                dhan_futures,
                role="dhan_futures",
                provider_id=N.PROVIDER_DHAN,
            )
        )

        active_option_surface = (
            _call_first(
                option_core,
                ("build_selected_option_surface", "build_option_surface"),
                active_selected,
                provider_runtime=provider_runtime,
                now_ns=generated_at_ns,
            )
            or self._fallback_option_surface(
                active_selected,
                role="active_selected_option",
                provider_id=provider_runtime["active_selected_option_provider_id"],
            )
        )

        dhan_option_surface = (
            _call_first(
                option_core,
                ("build_dhan_selected_option_surface", "build_option_surface"),
                dhan_selected,
                provider_runtime=provider_runtime,
                now_ns=generated_at_ns,
            )
            or self._fallback_option_surface(
                dhan_selected,
                role="dhan_selected_option",
                provider_id=N.PROVIDER_DHAN,
            )
        )

        call_option_surface, put_option_surface = self._split_option_surfaces(
            active_option_surface=active_option_surface,
            dhan_option_surface=dhan_option_surface,
            dhan_context=dhan_context,
        )

        cross_futures_surface = (
            _call_first(
                futures_core,
                ("build_cross_futures_surface",),
                active_futures_surface,
                dhan_futures_surface,
                provider_runtime=provider_runtime,
            )
            or self._fallback_cross_futures_surface(active_futures_surface, dhan_futures_surface)
        )

        cross_option_surface = self._build_cross_option_context(
            call_surface=call_option_surface,
            put_surface=put_option_surface,
            selected_surface=active_option_surface,
            dhan_context=dhan_context,
        )

        strike_context = (
            _call_first(
                strike_module,
                (
                    "build_family_strike_selection_surface",
                    "build_strike_selection_surface",
                    "build_strike_context_surface",
                    "build_oi_wall_surface",
                    "build_strike_ladder_surface",
                ),
                dhan_context,
                selected_option=active_option_surface,
                call_option=call_option_surface,
                put_option=put_option_surface,
                futures=active_futures_surface,
                now_ns=generated_at_ns,
            )
            or self._fallback_strike_context(
                dhan_context=dhan_context,
                selected_option=active_option_surface,
                call_option=call_option_surface,
                put_option=put_option_surface,
                futures=active_futures_surface,
            )
        )

        regime_surface = (
            _call_first(
                regime_module,
                ("build_regime_bundle", "build_regime_surface"),
                futures_surface=active_futures_surface,
                call_surface=call_option_surface,
                put_surface=put_option_surface,
                cross_option=cross_option_surface,
                now_ns=generated_at_ns,
            )
            or self._fallback_regime_surface(active_futures_surface, cross_option_surface)
        )

        classic_mode_surface = (
            _call_first(
                regime_module,
                ("build_classic_runtime_mode_surface",),
                provider_runtime=provider_runtime,
                regime_surface=regime_surface,
                dhan_context=dhan_context,
                now_ns=generated_at_ns,
            )
            or self._fallback_classic_mode_surface(provider_runtime)
        )

        miso_mode_surface = (
            _call_first(
                regime_module,
                ("build_miso_runtime_mode_surface",),
                provider_runtime=provider_runtime,
                dhan_context=dhan_context,
                futures_surface=dhan_futures_surface,
                option_surface=dhan_option_surface,
                now_ns=generated_at_ns,
            )
            or self._fallback_miso_mode_surface(provider_runtime, dhan_context, dhan_futures_surface, dhan_option_surface)
        )

        futures_liquidity_surface = (
            _call_first(
                tradability,
                ("build_futures_liquidity_surface",),
                active_futures_surface,
                regime_surface=regime_surface,
            )
            or self._fallback_futures_liquidity(active_futures_surface)
        )

        call_tradability = (
            _call_first(
                tradability,
                ("build_classic_option_tradability_surface",),
                call_option_surface,
                side=N.SIDE_CALL,
                regime_surface=regime_surface,
                runtime_mode=classic_mode_surface.get("mode"),
            )
            or self._fallback_option_tradability(call_option_surface, side=N.SIDE_CALL)
        )

        put_tradability = (
            _call_first(
                tradability,
                ("build_classic_option_tradability_surface",),
                put_option_surface,
                side=N.SIDE_PUT,
                regime_surface=regime_surface,
                runtime_mode=classic_mode_surface.get("mode"),
            )
            or self._fallback_option_tradability(put_option_surface, side=N.SIDE_PUT)
        )

        miso_call_tradability = (
            _call_first(
                tradability,
                ("build_miso_option_tradability_surface",),
                call_option_surface,
                side=N.SIDE_CALL,
                runtime_mode=miso_mode_surface.get("mode"),
            )
            or self._fallback_option_tradability(call_option_surface, side=N.SIDE_CALL)
        )

        miso_put_tradability = (
            _call_first(
                tradability,
                ("build_miso_option_tradability_surface",),
                put_option_surface,
                side=N.SIDE_PUT,
                runtime_mode=miso_mode_surface.get("mode"),
            )
            or self._fallback_option_tradability(put_option_surface, side=N.SIDE_PUT)
        )

        return {
            "generated_at_ns": generated_at_ns,
            "provider_runtime": dict(provider_runtime),
            "snapshot": self._snapshot_summary(
                generated_at_ns=generated_at_ns,
                active_frame=active_frame,
                dhan_frame=dhan_frame,
            ),
            "futures": {
                "active": dict(active_futures_surface),
                "dhan": dict(dhan_futures_surface),
                "cross": dict(cross_futures_surface),
                "liquidity": dict(futures_liquidity_surface),
            },
            "options": {
                "selected": dict(active_option_surface),
                "dhan_selected": dict(dhan_option_surface),
                "call": dict(call_option_surface),
                "put": dict(put_option_surface),
                "cross_option": dict(cross_option_surface),
            },
            "strike_selection": dict(strike_context),
            "oi_wall_context": dict(_as_mapping(strike_context).get("oi_wall_context", strike_context)),
            "regime": dict(regime_surface),
            "runtime_modes": {
                "classic": dict(classic_mode_surface),
                "miso": dict(miso_mode_surface),
            },
            "tradability": {
                "futures": dict(futures_liquidity_surface),
                "classic_call": dict(call_tradability),
                "classic_put": dict(put_tradability),
                "miso_call": dict(miso_call_tradability),
                "miso_put": dict(miso_put_tradability),
            },
            "dhan_context": dict(dhan_context),
        }

    def _build_family_surfaces(
        self,
        *,
        generated_at_ns: int,
        provider_runtime: Mapping[str, Any],
        shared_core: Mapping[str, Any],
    ) -> dict[str, Any]:
        families: dict[str, Any] = {}
        surfaces_by_branch: dict[str, Any] = {}

        for family_id in FAMILY_ORDER:
            module = self.family_modules.get(family_id)
            family_payload = self._build_one_family_surface(
                family_id=family_id,
                module=module,
                generated_at_ns=generated_at_ns,
                provider_runtime=provider_runtime,
                shared_core=shared_core,
            )
            families[family_id] = family_payload
            for branch_id in BRANCHES:
                branch_payload = (
                    _nested_get(family_payload, "branches", branch_id)
                    or _nested_get(family_payload, "branch_surfaces", branch_id)
                    or _nested_get(family_payload, f"{branch_id.lower()}_branch")
                    or self._fallback_branch_surface(
                        family_id=family_id,
                        branch_id=branch_id,
                        shared_core=shared_core,
                    )
                )
                surfaces_by_branch[_surface_key(family_id, branch_id)] = dict(_as_mapping(branch_payload))

        return {
            "schema_version": _name("DEFAULT_SCHEMA_VERSION", 1),
            "surface_version": "feature-family-surfaces-v1",
            "service": N.SERVICE_FEATURES,
            "generated_at_ns": generated_at_ns,
            "provider_runtime": dict(provider_runtime),
            "shared_core": dict(shared_core),
            "families": families,
            "surfaces_by_branch": surfaces_by_branch,
            "contract_adapter_status": {
                "common_loaded": self.modules.get("common") is not None,
                "contracts_loaded": self.modules.get("contracts") is not None,
                "shared_core_modules_loaded": {
                    key: value is not None for key, value in self.modules.items()
                },
                "family_modules_loaded": {
                    key: value is not None for key, value in self.family_modules.items()
                },
            },
        }

    def _build_one_family_surface(
        self,
        *,
        family_id: str,
        module: Any | None,
        generated_at_ns: int,
        provider_runtime: Mapping[str, Any],
        shared_core: Mapping[str, Any],
    ) -> dict[str, Any]:
        call_branch = self._build_family_branch_surface(
            family_id=family_id,
            branch_id=N.BRANCH_CALL,
            module=module,
            shared_core=shared_core,
        )
        put_branch = self._build_family_branch_surface(
            family_id=family_id,
            branch_id=N.BRANCH_PUT,
            module=module,
            shared_core=shared_core,
        )

        if family_id == N.STRATEGY_FAMILY_MISO:
            built = _call_first(
                module,
                ("build_miso_family_surface", "build_family_surface"),
                provider_runtime=provider_runtime,
                shared_core=shared_core,
                call_support=call_branch,
                put_support=put_branch,
                now_ns=generated_at_ns,
            )
        else:
            suffix = family_id.lower()
            built = _call_first(
                module,
                (f"build_{suffix}_family_surface", "build_family_surface"),
                provider_runtime=provider_runtime,
                shared_core=shared_core,
                call_branch=call_branch,
                put_branch=put_branch,
                now_ns=generated_at_ns,
            )

        if isinstance(built, Mapping):
            payload = dict(built)
        else:
            payload = {
                "family_id": family_id,
                "eligible": bool(call_branch.get("eligible") or put_branch.get("eligible")),
                "runtime_mode": self._runtime_mode_for_family(family_id, shared_core),
                "branches": {
                    N.BRANCH_CALL: call_branch,
                    N.BRANCH_PUT: put_branch,
                },
                "source": "features_fallback_adapter",
            }

        payload.setdefault("family_id", family_id)
        payload.setdefault("eligible", bool(call_branch.get("eligible") or put_branch.get("eligible")))
        payload.setdefault("runtime_mode", self._runtime_mode_for_family(family_id, shared_core))
        payload.setdefault(
            "branches",
            {
                N.BRANCH_CALL: call_branch,
                N.BRANCH_PUT: put_branch,
            },
        )

        if family_id == N.STRATEGY_FAMILY_MISO:
            payload.setdefault("mode", self._runtime_mode_for_family(family_id, shared_core))
            payload.setdefault("chain_context_ready", bool(_nested_get(shared_core, "strike_selection", "chain_context_ready", default=False)))
            payload.setdefault("selected_side", _nested_get(shared_core, "options", "selected", "side", default=None))
            payload.setdefault("selected_strike", _nested_get(shared_core, "options", "selected", "strike", default=None))
            payload.setdefault("shadow_call_strike", _nested_get(shared_core, "strike_selection", "shadow_call_strike", default=None))
            payload.setdefault("shadow_put_strike", _nested_get(shared_core, "strike_selection", "shadow_put_strike", default=None))
            payload.setdefault("call_support", call_branch)
            payload.setdefault("put_support", put_branch)

        return dict(payload)

    def _build_family_branch_surface(
        self,
        *,
        family_id: str,
        branch_id: str,
        module: Any | None,
        shared_core: Mapping[str, Any],
    ) -> dict[str, Any]:
        side = BRANCH_TO_SIDE[branch_id]
        family_lc = family_id.lower()

        if family_id == N.STRATEGY_FAMILY_MISO:
            built = _call_first(
                module,
                (
                    "build_miso_side_surface",
                    "build_miso_branch_surface",
                    "build_miso_side_support_surface",
                    "build_branch_surface",
                ),
                branch_id=branch_id,
                side=side,
                shared_core=shared_core,
            )
        else:
            built = _call_first(
                module,
                (f"build_{family_lc}_branch_surface", "build_branch_surface"),
                branch_id=branch_id,
                side=side,
                shared_core=shared_core,
            )

        if isinstance(built, Mapping):
            payload = dict(built)
        else:
            payload = self._fallback_branch_surface(
                family_id=family_id,
                branch_id=branch_id,
                shared_core=shared_core,
            )

        payload.setdefault("family_id", family_id)
        payload.setdefault("branch_id", branch_id)
        payload.setdefault("side", side)
        payload.setdefault("runtime_mode", self._runtime_mode_for_family(family_id, shared_core))
        payload.setdefault("eligible", self._fallback_branch_eligible(payload, shared_core))
        payload.setdefault("source", "feature_family_module" if built is not None else "features_fallback_adapter")
        payload.setdefault("oi_wall_context", self._side_oi_wall(side, shared_core))
        payload.setdefault("cross_option_context", dict(_nested_get(shared_core, "options", "cross_option", default={})))
        payload.setdefault("tradability", self._tradability_for_family_branch(family_id, branch_id, shared_core))
        payload.setdefault("futures_features", dict(_nested_get(shared_core, "futures", "active", default={})))
        payload.setdefault("option_features", self._option_for_branch(branch_id, shared_core))
        return dict(payload)

    def _build_family_features(
        self,
        *,
        generated_at_ns: int,
        active_frame: SnapshotFrameView | None,
        dhan_frame: SnapshotFrameView | None,
        provider_runtime: Mapping[str, Any],
        shared_core: Mapping[str, Any],
        family_surfaces: Mapping[str, Any],
    ) -> dict[str, Any]:
        common_module = self.modules.get("common")
        contracts_module = self.modules.get("contracts")

        if common_module is not None and callable(getattr(common_module, "build_family_features_payload", None)):
            payload = common_module.build_family_features_payload(generated_at_ns=generated_at_ns)
        elif contracts_module is not None and callable(getattr(contracts_module, "build_empty_family_features_payload", None)):
            payload = contracts_module.build_empty_family_features_payload(generated_at_ns=generated_at_ns)
        else:
            payload = self._fallback_family_features_template(generated_at_ns)

        payload = copy.deepcopy(payload)
        payload["generated_at_ns"] = generated_at_ns
        payload["service"] = N.SERVICE_FEATURES

        snapshot_patch = self._snapshot_contract_patch(
            generated_at_ns=generated_at_ns,
            active_frame=active_frame,
            dhan_frame=dhan_frame,
            shared_core=shared_core,
        )
        provider_patch = self._provider_runtime_contract_patch(provider_runtime)
        common_patch = self._common_contract_patch(shared_core)
        stage_patch = self._stage_flags_contract_patch(snapshot_patch, common_patch, shared_core)
        families_patch = self._families_contract_patch(family_surfaces, shared_core)

        _deep_patch_existing(payload["snapshot"], snapshot_patch)
        _deep_patch_existing(payload["provider_runtime"], provider_patch)
        _deep_patch_existing(payload["common"], common_patch)
        _deep_patch_existing(payload["stage_flags"], stage_patch)
        _deep_patch_existing(payload["families"], families_patch)

        market_patch = self._market_contract_patch(shared_core)
        if "market" in payload and isinstance(payload["market"], MutableMapping):
            _deep_patch_existing(payload["market"], market_patch)

        if contracts_module is not None:
            validator = getattr(contracts_module, "validate_family_features_payload", None)
            if callable(validator):
                validator(payload)

            publishable_validator = getattr(
                contracts_module,
                "validate_publishable_family_features_payload",
                None,
            )
            if callable(publishable_validator):
                try:
                    publishable_validator(payload)
                except Exception as exc:
                    self.log.warning("family_features_publishable_validation_deferred error=%s", exc)

        return payload

    def _build_family_frames(
        self,
        *,
        generated_at_ns: int,
        provider_runtime: Mapping[str, Any],
        family_surfaces: Mapping[str, Any],
        family_features: Mapping[str, Any],
    ) -> dict[str, Any]:
        frames: dict[str, Any] = {}
        surfaces_by_branch = _nested_get(family_surfaces, "surfaces_by_branch", default={})
        for family_id in FAMILY_ORDER:
            for branch_id in BRANCHES:
                key = _surface_key(family_id, branch_id)
                surface = dict(_as_mapping(_nested_get(surfaces_by_branch, key, default={})))
                side = BRANCH_TO_SIDE[branch_id]
                option = dict(_as_mapping(surface.get("option_features")))
                tradability = dict(_as_mapping(surface.get("tradability")))
                frames[key] = {
                    "frame_id": f"{key}-{generated_at_ns}",
                    "frame_ts_ns": generated_at_ns,
                    "family_id": family_id,
                    "branch_id": branch_id,
                    "side": side,
                    "strategy_runtime_mode": surface.get(
                        "runtime_mode",
                        self._runtime_mode_for_family(
                            family_id,
                            _nested_get(family_surfaces, "shared_core", default={}),
                        ),
                    ),
                    "family_runtime_mode": provider_runtime.get("family_runtime_mode"),
                    "active_futures_provider_id": provider_runtime.get("active_futures_provider_id"),
                    "active_selected_option_provider_id": provider_runtime.get("active_selected_option_provider_id"),
                    "active_option_context_provider_id": provider_runtime.get("active_option_context_provider_id"),
                    "instrument_key": option.get("instrument_key"),
                    "instrument_token": option.get("instrument_token"),
                    "option_symbol": option.get("trading_symbol") or option.get("symbol"),
                    "strike": option.get("strike"),
                    "entry_mode": option.get("entry_mode") or N.ENTRY_MODE_UNKNOWN,
                    "option_price": option.get("ltp"),
                    "tick_size": option.get("tick_size") or 0.05,
                    "depth_total": option.get("depth_total"),
                    "spread_ratio": option.get("spread_ratio"),
                    "response_efficiency": option.get("response_efficiency"),
                    "target_points": DEFAULT_TARGET_POINTS,
                    "stop_points": DEFAULT_STOP_POINTS,
                    "eligible": bool(surface.get("eligible")),
                    "tradability_ok": bool(tradability.get("entry_pass") or tradability.get("tradability_ok")),
                    "regime": _nested_get(family_features, "common", "regime", default=REGIME_UNKNOWN),
                    "surface": surface,
                }
        return frames

    def _build_feature_state(
        self,
        *,
        generated_at_ns: int,
        active_frame: SnapshotFrameView | None,
        shared_core: Mapping[str, Any],
        family_features: Mapping[str, Any],
    ) -> dict[str, Any]:
        active_futures = dict(_nested_get(shared_core, "futures", "active", default={}))
        selected = dict(_nested_get(shared_core, "options", "selected", default={}))
        return {
            "frame_id": f"feature-state-{generated_at_ns}",
            "frame_ts_ns": generated_at_ns,
            "ts_event_ns": active_frame.ts_event_ns if active_frame else generated_at_ns,
            "instrument_key": active_futures.get("instrument_key") or N.IK_MME_FUT,
            "selection_version": selected.get("selection_version") or active_futures.get("selection_version") or "mme-selection-v1",
            "frame_valid": bool(_nested_get(family_features, "snapshot", "valid", default=False)),
            "warmup_complete": bool(_nested_get(family_features, "stage_flags", "warmup_complete", default=False)),
            "regime": _nested_get(family_features, "common", "regime", default=REGIME_UNKNOWN),
            "strategy_runtime_mode_classic": _nested_get(
                family_features,
                "common",
                "strategy_runtime_mode_classic",
                default=None,
            ),
            "strategy_runtime_mode_miso": _nested_get(
                family_features,
                "common",
                "strategy_runtime_mode_miso",
                default=None,
            ),
        }

    # ------------------------------------------------------------------
    # Fallback shared core builders
    # ------------------------------------------------------------------

    def _fallback_futures_surface(
        self,
        source: Mapping[str, Any],
        *,
        role: str,
        provider_id: str,
    ) -> dict[str, Any]:
        bid = _safe_float(_pick(source, "bid", "best_bid"), 0.0)
        ask = _safe_float(_pick(source, "ask", "best_ask"), 0.0)
        ltp = _safe_float(_pick(source, "ltp", "last_price", "price"), 0.0)
        bid_qty = _safe_float(_pick(source, "bid_qty", "best_bid_qty", "bq"), 0.0)
        ask_qty = _safe_float(_pick(source, "ask_qty", "best_ask_qty", "aq"), 0.0)
        bids, asks = self._depth_lists(source)
        depth_bid_total = sum(_safe_float(row.get("quantity"), 0.0) for row in bids) or bid_qty
        depth_ask_total = sum(_safe_float(row.get("quantity"), 0.0) for row in asks) or ask_qty
        spread = max(0.0, ask - bid) if ask > 0 and bid > 0 else 0.0
        mid = (bid + ask) / 2.0 if bid > 0 and ask > 0 else ltp
        spread_ratio = _ratio(spread, max(0.05, mid * 0.0001), 999.0) if mid > 0 else 999.0
        ofi = _ratio(depth_bid_total - depth_ask_total, depth_bid_total + depth_ask_total, 0.0)
        weighted_ofi = 0.5 + (ofi / 2.0)
        delta_3 = _safe_float(_pick(source, "delta_3", "ltp_delta_3", "price_delta_3"), 0.0)
        velocity = abs(_safe_float(_pick(source, "velocity", "velocity_points"), delta_3))
        velocity_ratio = _safe_float(_pick(source, "velocity_ratio", "vel_ratio"), 0.0)
        if velocity_ratio <= 0.0:
            velocity_ratio = _clamp(velocity / max(0.25, spread or 0.25), 0.0, 5.0)
        volume_norm = _safe_float(_pick(source, "volume_norm", "normalized_volume"), 1.0)
        event_rate_ratio = _safe_float(_pick(source, "event_rate_ratio", "event_rate_spike_ratio"), 1.0)
        vwap = _safe_float(_pick(source, "vwap"), ltp)
        vwap_distance = ltp - vwap if ltp > 0 and vwap > 0 else 0.0

        return {
            "role": role,
            "provider_id": provider_id,
            "instrument_key": _safe_str(_pick(source, "instrument_key"), N.IK_MME_FUT),
            "instrument_token": _safe_str(_pick(source, "instrument_token")),
            "trading_symbol": _safe_str(_pick(source, "trading_symbol", "symbol")),
            "ltp": ltp,
            "bid": bid,
            "ask": ask,
            "mid": mid,
            "spread": spread,
            "spread_ratio": spread_ratio,
            "bid_qty": bid_qty,
            "ask_qty": ask_qty,
            "depth_bid_total": depth_bid_total,
            "depth_ask_total": depth_ask_total,
            "depth_total": depth_bid_total + depth_ask_total,
            "weighted_ofi": weighted_ofi,
            "weighted_ofi_persist": weighted_ofi,
            "nof": ofi,
            "delta_3": delta_3,
            "velocity": velocity,
            "velocity_ratio": velocity_ratio,
            "volume_norm": volume_norm,
            "event_rate_ratio": event_rate_ratio,
            "vwap": vwap,
            "vwap_distance": vwap_distance,
            "ts_event_ns": _safe_int(_pick(source, "ts_event_ns"), 0) or None,
            "ts_recv_ns": _safe_int(_pick(source, "ts_recv_ns"), 0) or None,
            "tick_validity": _safe_str(_pick(source, "tick_validity"), "UNKNOWN"),
            "valid": ltp > 0.0,
            "source": "features_fallback_futures_surface",
        }

    def _fallback_option_surface(
        self,
        source: Mapping[str, Any],
        *,
        role: str,
        provider_id: str,
    ) -> dict[str, Any]:
        bid = _safe_float(_pick(source, "bid", "best_bid"), 0.0)
        ask = _safe_float(_pick(source, "ask", "best_ask"), 0.0)
        ltp = _safe_float(_pick(source, "ltp", "last_price", "price"), 0.0)
        bid_qty = _safe_float(_pick(source, "bid_qty", "best_bid_qty", "bq"), 0.0)
        ask_qty = _safe_float(_pick(source, "ask_qty", "best_ask_qty", "aq"), 0.0)
        bids, asks = self._depth_lists(source)
        depth_bid_total = sum(_safe_float(row.get("quantity"), 0.0) for row in bids) or bid_qty
        depth_ask_total = sum(_safe_float(row.get("quantity"), 0.0) for row in asks) or ask_qty
        spread = max(0.0, ask - bid) if ask > 0 and bid > 0 else 0.0
        mid = (bid + ask) / 2.0 if bid > 0 and ask > 0 else ltp
        spread_ratio = _ratio(spread, max(0.05, mid * 0.001), 999.0) if mid > 0 else 999.0
        response_efficiency = _safe_float(_pick(source, "response_efficiency", "response_eff"), 0.0)
        if response_efficiency <= 0.0 and ltp > 0:
            response_efficiency = _clamp(abs(_safe_float(_pick(source, "delta_3"), 0.0)) / max(ltp, 1.0), 0.0, 1.0)
        oi = _safe_float(_pick(source, "oi", "open_interest"), 0.0)
        volume = _safe_float(_pick(source, "volume"), 0.0)
        side = self._normalize_side(_pick(source, "option_side", "side", "right"))
        strike = _safe_float_or_none(_pick(source, "strike", "strike_price"))

        return {
            "role": role,
            "provider_id": provider_id,
            "instrument_key": _safe_str(_pick(source, "instrument_key")),
            "instrument_token": _safe_str(_pick(source, "instrument_token")),
            "trading_symbol": _safe_str(_pick(source, "trading_symbol", "symbol")),
            "side": side,
            "option_side": side,
            "strike": strike,
            "expiry": _safe_str(_pick(source, "expiry")),
            "ltp": ltp,
            "bid": bid,
            "ask": ask,
            "mid": mid,
            "spread": spread,
            "spread_ratio": spread_ratio,
            "bid_qty": bid_qty,
            "ask_qty": ask_qty,
            "depth_bid_total": depth_bid_total,
            "depth_ask_total": depth_ask_total,
            "depth_total": depth_bid_total + depth_ask_total,
            "response_efficiency": response_efficiency,
            "impact_fraction": _ratio(_safe_float(_pick(source, "last_qty"), 0.0), max(depth_ask_total, depth_bid_total, 1.0), 0.0),
            "delta_3": _safe_float(_pick(source, "delta_3", "ltp_delta_3", "price_delta_3"), 0.0),
            "velocity_ratio": _safe_float(_pick(source, "velocity_ratio", "vel_ratio"), 0.0),
            "weighted_ofi": _clamp(0.5 + _ratio(depth_bid_total - depth_ask_total, depth_bid_total + depth_ask_total, 0.0) / 2.0, 0.0, 1.0),
            "weighted_ofi_persist": _clamp(0.5 + _ratio(depth_bid_total - depth_ask_total, depth_bid_total + depth_ask_total, 0.0) / 2.0, 0.0, 1.0),
            "oi": oi,
            "volume": volume,
            "iv": _safe_float_or_none(_pick(source, "iv", "implied_volatility")),
            "tick_size": _safe_float(_pick(source, "tick_size"), 0.05),
            "entry_mode": _safe_str(_pick(source, "entry_mode"), N.ENTRY_MODE_UNKNOWN),
            "ts_event_ns": _safe_int(_pick(source, "ts_event_ns"), 0) or None,
            "ts_recv_ns": _safe_int(_pick(source, "ts_recv_ns"), 0) or None,
            "tick_validity": _safe_str(_pick(source, "tick_validity"), "UNKNOWN"),
            "valid": ltp > 0.0 and side in (N.SIDE_CALL, N.SIDE_PUT),
            "source": "features_fallback_option_surface",
        }

    def _split_option_surfaces(
        self,
        *,
        active_option_surface: Mapping[str, Any],
        dhan_option_surface: Mapping[str, Any],
        dhan_context: Mapping[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        selected_side = _safe_str(active_option_surface.get("side"))
        dhan_side = _safe_str(dhan_option_surface.get("side"))

        empty_call = self._fallback_option_surface({}, role="call_context", provider_id="")
        empty_call["side"] = N.SIDE_CALL
        empty_call["option_side"] = N.SIDE_CALL
        empty_put = self._fallback_option_surface({}, role="put_context", provider_id="")
        empty_put["side"] = N.SIDE_PUT
        empty_put["option_side"] = N.SIDE_PUT

        call_surface = dict(empty_call)
        put_surface = dict(empty_put)

        if selected_side == N.SIDE_CALL:
            call_surface.update(active_option_surface)
        elif selected_side == N.SIDE_PUT:
            put_surface.update(active_option_surface)

        if dhan_side == N.SIDE_CALL and not call_surface.get("valid"):
            call_surface.update(dhan_option_surface)
        elif dhan_side == N.SIDE_PUT and not put_surface.get("valid"):
            put_surface.update(dhan_option_surface)

        call_ctx = self._extract_context_side_option(dhan_context, N.SIDE_CALL)
        put_ctx = self._extract_context_side_option(dhan_context, N.SIDE_PUT)
        if call_ctx:
            call_surface.update({k: v for k, v in call_ctx.items() if v not in (None, "")})
            call_surface["side"] = N.SIDE_CALL
            call_surface["option_side"] = N.SIDE_CALL
        if put_ctx:
            put_surface.update({k: v for k, v in put_ctx.items() if v not in (None, "")})
            put_surface["side"] = N.SIDE_PUT
            put_surface["option_side"] = N.SIDE_PUT

        return call_surface, put_surface

    def _fallback_cross_futures_surface(
        self,
        active: Mapping[str, Any],
        dhan: Mapping[str, Any],
    ) -> dict[str, Any]:
        active_ltp = _safe_float(active.get("ltp"), 0.0)
        dhan_ltp = _safe_float(dhan.get("ltp"), 0.0)
        diff = active_ltp - dhan_ltp if active_ltp > 0 and dhan_ltp > 0 else 0.0
        return {
            "active_ltp": active_ltp,
            "dhan_ltp": dhan_ltp,
            "ltp_diff": diff,
            "ltp_diff_abs": abs(diff),
            "providers_aligned": abs(diff) <= max(1.0, active_ltp * 0.0002) if active_ltp and dhan_ltp else False,
            "active_valid": bool(active.get("valid")),
            "dhan_valid": bool(dhan.get("valid")),
        }

    def _build_cross_option_context(
        self,
        *,
        call_surface: Mapping[str, Any],
        put_surface: Mapping[str, Any],
        selected_surface: Mapping[str, Any],
        dhan_context: Mapping[str, Any],
    ) -> dict[str, Any]:
        call_ltp = _safe_float(call_surface.get("ltp"), 0.0)
        put_ltp = _safe_float(put_surface.get("ltp"), 0.0)
        call_oi = _safe_float(call_surface.get("oi"), 0.0)
        put_oi = _safe_float(put_surface.get("oi"), 0.0)
        call_depth = _safe_float(call_surface.get("depth_total"), 0.0)
        put_depth = _safe_float(put_surface.get("depth_total"), 0.0)
        premium_bias = "CALL" if call_ltp > put_ltp else ("PUT" if put_ltp > call_ltp else "NEUTRAL")
        oi_bias = "CALL_RESISTANCE" if call_oi > put_oi else ("PUT_SUPPORT" if put_oi > call_oi else "NEUTRAL")

        return {
            "selected_side": _safe_str(selected_surface.get("side")),
            "call_ltp": call_ltp,
            "put_ltp": put_ltp,
            "call_strike": call_surface.get("strike"),
            "put_strike": put_surface.get("strike"),
            "call_oi": call_oi,
            "put_oi": put_oi,
            "call_depth_total": call_depth,
            "put_depth_total": put_depth,
            "premium_ratio_call_put": _ratio(call_ltp, put_ltp, 0.0),
            "oi_ratio_call_put": _ratio(call_oi, put_oi, 0.0),
            "depth_ratio_call_put": _ratio(call_depth, put_depth, 0.0),
            "premium_bias": premium_bias,
            "oi_bias": _safe_str(_pick(dhan_context, "oi_bias"), oi_bias),
            "cross_option_ready": call_ltp > 0.0 or put_ltp > 0.0 or bool(dhan_context),
            "source": "features_cross_option_context",
        }

    def _fallback_strike_context(
        self,
        *,
        dhan_context: Mapping[str, Any],
        selected_option: Mapping[str, Any],
        call_option: Mapping[str, Any],
        put_option: Mapping[str, Any],
        futures: Mapping[str, Any],
    ) -> dict[str, Any]:
        ladder = self._extract_strike_ladder(dhan_context)
        fut_ltp = _safe_float(futures.get("ltp"), 0.0)
        selected_strike = _safe_float_or_none(selected_option.get("strike"))
        atm_strike = _safe_float_or_none(
            _coalesce(
                _pick(dhan_context, "atm_strike", "underlying_atm"),
                selected_strike,
                call_option.get("strike"),
                put_option.get("strike"),
            )
        )

        call_wall = self._nearest_oi_wall(
            ladder=ladder,
            side=N.SIDE_CALL,
            reference=fut_ltp or atm_strike or selected_strike,
        )
        put_wall = self._nearest_oi_wall(
            ladder=ladder,
            side=N.SIDE_PUT,
            reference=fut_ltp or atm_strike or selected_strike,
        )

        call_wall_strength = _safe_float(call_wall.get("wall_strength"), 0.0)
        put_wall_strength = _safe_float(put_wall.get("wall_strength"), 0.0)
        oi_bias = "NEUTRAL"
        if call_wall_strength > put_wall_strength + 0.05:
            oi_bias = "CALL_WALL_DOMINANT"
        elif put_wall_strength > call_wall_strength + 0.05:
            oi_bias = "PUT_WALL_DOMINANT"

        return {
            "chain_context_ready": bool(ladder or dhan_context),
            "atm_strike": atm_strike,
            "selected_strike": selected_strike,
            "shadow_call_strike": call_option.get("strike"),
            "shadow_put_strike": put_option.get("strike"),
            "ladder": ladder,
            "ladder_size": len(ladder),
            "nearest_call_oi_resistance": call_wall,
            "nearest_put_oi_support": put_wall,
            "nearest_call_oi_resistance_strike": call_wall.get("strike"),
            "nearest_put_oi_support_strike": put_wall.get("strike"),
            "oi_bias": _safe_str(_pick(dhan_context, "oi_bias"), oi_bias),
            "call_wall_strength": call_wall_strength,
            "put_wall_strength": put_wall_strength,
            "oi_wall_context": {
                "call": call_wall,
                "put": put_wall,
                "oi_bias": _safe_str(_pick(dhan_context, "oi_bias"), oi_bias),
                "law": "slow_context_quality_surface_not_trigger",
            },
            "source": "features_fallback_strike_context",
        }

    def _fallback_regime_surface(
        self,
        futures_surface: Mapping[str, Any],
        cross_option: Mapping[str, Any],
    ) -> dict[str, Any]:
        velocity_ratio = _safe_float(futures_surface.get("velocity_ratio"), 0.0)
        event_rate_ratio = _safe_float(futures_surface.get("event_rate_ratio"), 1.0)
        volume_norm = _safe_float(futures_surface.get("volume_norm"), 1.0)
        score = max(velocity_ratio, event_rate_ratio, volume_norm)

        if score >= DEFAULT_REGIME_FAST_RATIO_MIN:
            regime = REGIME_FAST
            reason = "fast_ratio"
        elif score <= DEFAULT_REGIME_LOWVOL_RATIO_MAX:
            regime = REGIME_LOWVOL
            reason = "lowvol_ratio"
        else:
            regime = REGIME_NORMAL
            reason = "normal_ratio"

        return {
            "regime": regime,
            "regime_reason": reason,
            "velocity_ratio": velocity_ratio,
            "event_rate_ratio": event_rate_ratio,
            "volume_norm": volume_norm,
            "cross_option_ready": bool(cross_option.get("cross_option_ready")),
            "source": "features_fallback_regime_surface",
        }

    def _fallback_classic_mode_surface(self, provider_runtime: Mapping[str, Any]) -> dict[str, Any]:
        mode = (
            N.STRATEGY_RUNTIME_MODE_NORMAL
            if (
                provider_runtime.get("active_futures_provider_id") in _PROVIDER_ALLOWED_IDS
                and provider_runtime.get("active_selected_option_provider_id") in _PROVIDER_ALLOWED_IDS
                and provider_runtime.get("futures_provider_status") == N.PROVIDER_STATUS_HEALTHY
                and provider_runtime.get("selected_option_provider_status") == N.PROVIDER_STATUS_HEALTHY
            )
            else N.STRATEGY_RUNTIME_MODE_DHAN_DEGRADED
        )
        return {
            "mode": mode,
            "strategy_runtime_mode": mode,
            "classic_provider_ready": mode == N.STRATEGY_RUNTIME_MODE_NORMAL,
            "source": "features_fallback_classic_mode_surface",
        }

    def _fallback_miso_mode_surface(
        self,
        provider_runtime: Mapping[str, Any],
        dhan_context: Mapping[str, Any],
        dhan_futures_surface: Mapping[str, Any],
        dhan_option_surface: Mapping[str, Any],
    ) -> dict[str, Any]:
        dhan_ready = bool(dhan_context) and (
            bool(dhan_futures_surface.get("valid")) or bool(dhan_option_surface.get("valid"))
        )
        depth20_ready = bool(
            _pick(dhan_context, "depth20_ready", "top20_ready", default=False)
        )
        if not dhan_ready:
            mode = N.STRATEGY_RUNTIME_MODE_DISABLED
        elif depth20_ready:
            mode = N.STRATEGY_RUNTIME_MODE_DEPTH20_ENHANCED
        else:
            mode = N.STRATEGY_RUNTIME_MODE_BASE_5DEPTH
        return {
            "mode": mode,
            "strategy_runtime_mode": mode,
            "miso_provider_ready": dhan_ready,
            "depth20_ready": depth20_ready,
            "source": "features_fallback_miso_mode_surface",
        }

    def _fallback_futures_liquidity(self, futures_surface: Mapping[str, Any]) -> dict[str, Any]:
        spread_ratio = _safe_float(futures_surface.get("spread_ratio"), 999.0)
        depth_total = _safe_float(futures_surface.get("depth_total"), 0.0)
        liquidity_pass = spread_ratio <= 1.80 and depth_total >= 1.0
        return {
            "liquidity_pass": liquidity_pass,
            "spread_ratio": spread_ratio,
            "depth_total": depth_total,
            "blocked_reason": "" if liquidity_pass else "futures_liquidity",
        }

    def _fallback_option_tradability(
        self,
        option_surface: Mapping[str, Any],
        *,
        side: str,
    ) -> dict[str, Any]:
        ltp = _safe_float(option_surface.get("ltp"), 0.0)
        spread_ratio = _safe_float(option_surface.get("spread_ratio"), 999.0)
        depth_total = _safe_float(option_surface.get("depth_total"), 0.0)
        crossed = (
            _safe_float(option_surface.get("bid"), 0.0) > 0
            and _safe_float(option_surface.get("ask"), 0.0) > 0
            and _safe_float(option_surface.get("bid"), 0.0) > _safe_float(option_surface.get("ask"), 0.0)
        )
        stale = False
        entry_pass = ltp >= DEFAULT_PREMIUM_FLOOR and spread_ratio <= 1.80 and depth_total > 0 and not crossed
        reason = ""
        if ltp <= 0:
            reason = "missing_ltp"
        elif ltp < DEFAULT_PREMIUM_FLOOR:
            reason = "premium_floor"
        elif crossed:
            reason = "crossed_book"
        elif spread_ratio > 1.80:
            reason = "spread"
        elif depth_total <= 0:
            reason = "depth"
        return {
            "side": side,
            "entry_pass": entry_pass,
            "tradability_ok": entry_pass,
            "blocked_reason": reason,
            "ltp": ltp,
            "spread_ratio": spread_ratio,
            "depth_total": depth_total,
            "crossed_book": crossed,
            "stale": stale,
        }

    # ------------------------------------------------------------------
    # Contract patches
    # ------------------------------------------------------------------

    def _snapshot_summary(
        self,
        *,
        generated_at_ns: int,
        active_frame: SnapshotFrameView | None,
        dhan_frame: SnapshotFrameView | None,
    ) -> dict[str, Any]:
        active_ts = active_frame.ts_event_ns if active_frame else None
        dhan_ts = dhan_frame.ts_event_ns if dhan_frame else None
        samples_seen = int(bool(active_frame)) + int(bool(dhan_frame))
        sync_ok = True
        skew_ms = None
        if active_ts and dhan_ts:
            skew_ms = abs(active_ts - dhan_ts) / 1_000_000.0
            sync_ok = skew_ms <= DEFAULT_SYNC_MAX_MS
        valid = bool(active_frame and active_frame.valid)
        return {
            "valid": valid,
            "validity": "OK" if valid else "UNAVAILABLE",
            "sync_ok": sync_ok,
            "freshness_ok": valid,
            "packet_gap_ok": True,
            "warmup_ok": samples_seen > 0,
            "active_snapshot_ns": active_ts,
            "futures_snapshot_ns": active_ts,
            "selected_option_snapshot_ns": active_ts,
            "dhan_futures_snapshot_ns": dhan_ts,
            "dhan_option_snapshot_ns": dhan_ts,
            "max_member_age_ms": None,
            "fut_opt_skew_ms": skew_ms,
            "hard_packet_gap_ms": DEFAULT_PACKET_GAP_HARD_MS,
            "samples_seen": max(1, samples_seen),
        }

    def _snapshot_contract_patch(
        self,
        *,
        generated_at_ns: int,
        active_frame: SnapshotFrameView | None,
        dhan_frame: SnapshotFrameView | None,
        shared_core: Mapping[str, Any],
    ) -> dict[str, Any]:
        return dict(_nested_get(shared_core, "snapshot", default={})) or self._snapshot_summary(
            generated_at_ns=generated_at_ns,
            active_frame=active_frame,
            dhan_frame=dhan_frame,
        )

    def _provider_runtime_contract_patch(self, provider_runtime: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "active_futures_provider_id": provider_runtime.get("active_futures_provider_id"),
            "active_selected_option_provider_id": provider_runtime.get("active_selected_option_provider_id"),
            "active_option_context_provider_id": provider_runtime.get("active_option_context_provider_id"),
            "active_execution_provider_id": provider_runtime.get("active_execution_provider_id"),
            "fallback_execution_provider_id": provider_runtime.get("fallback_execution_provider_id"),
            "provider_runtime_mode": provider_runtime.get("provider_runtime_mode"),
            "family_runtime_mode": provider_runtime.get("family_runtime_mode"),
            "futures_provider_status": provider_runtime.get("futures_provider_status"),
            "selected_option_provider_status": provider_runtime.get("selected_option_provider_status"),
            "option_context_provider_status": provider_runtime.get("option_context_provider_status"),
            "execution_provider_status": provider_runtime.get("execution_provider_status"),
        }

    def _market_contract_patch(self, shared_core: Mapping[str, Any]) -> dict[str, Any]:
        futures = dict(_nested_get(shared_core, "futures", "active", default={}))
        selected = dict(_nested_get(shared_core, "options", "selected", default={}))
        return {
            "underlying_symbol": "NIFTY",
            "futures_instrument_key": futures.get("instrument_key") or N.IK_MME_FUT,
            "selected_option_instrument_key": selected.get("instrument_key"),
            "selected_option_side": selected.get("side"),
            "selected_option_strike": selected.get("strike"),
            "selected_option_ltp": selected.get("ltp"),
        }

    def _common_contract_patch(self, shared_core: Mapping[str, Any]) -> dict[str, Any]:
        futures = dict(_nested_get(shared_core, "futures", "active", default={}))
        call = dict(_nested_get(shared_core, "options", "call", default={}))
        put = dict(_nested_get(shared_core, "options", "put", default={}))
        selected = dict(_nested_get(shared_core, "options", "selected", default={}))
        cross_option = dict(_nested_get(shared_core, "options", "cross_option", default={}))
        regime = dict(_nested_get(shared_core, "regime", default={}))
        runtime_modes = dict(_nested_get(shared_core, "runtime_modes", default={}))
        trad = dict(_nested_get(shared_core, "tradability", default={}))
        call_trad = dict(trad.get("classic_call", {}))
        put_trad = dict(trad.get("classic_put", {}))
        futures_liq = dict(trad.get("futures", {}))

        selected_trad = call_trad if selected.get("side") == N.SIDE_CALL else put_trad

        return {
            "regime": _safe_str(regime.get("regime"), REGIME_UNKNOWN),
            "strategy_runtime_mode_classic": _safe_str(
                _nested_get(runtime_modes, "classic", "mode"),
                N.STRATEGY_RUNTIME_MODE_DHAN_DEGRADED,
            ),
            "strategy_runtime_mode_miso": _safe_str(
                _nested_get(runtime_modes, "miso", "mode"),
                N.STRATEGY_RUNTIME_MODE_DISABLED,
            ),
            "futures": {
                "ltp": futures.get("ltp"),
                "spread_ratio": futures.get("spread_ratio"),
                "depth_total": futures.get("depth_total"),
                "velocity_ratio": futures.get("velocity_ratio"),
                "weighted_ofi": futures.get("weighted_ofi"),
                "weighted_ofi_persist": futures.get("weighted_ofi_persist"),
                "nof": futures.get("nof"),
                "vwap_distance": futures.get("vwap_distance"),
                "liquidity_ok": bool(futures_liq.get("liquidity_pass")),
            },
            "call": {
                "ltp": call.get("ltp"),
                "strike": call.get("strike"),
                "spread_ratio": call.get("spread_ratio"),
                "depth_total": call.get("depth_total"),
                "response_efficiency": call.get("response_efficiency"),
                "tradability_ok": bool(call_trad.get("entry_pass") or call_trad.get("tradability_ok")),
            },
            "put": {
                "ltp": put.get("ltp"),
                "strike": put.get("strike"),
                "spread_ratio": put.get("spread_ratio"),
                "depth_total": put.get("depth_total"),
                "response_efficiency": put.get("response_efficiency"),
                "tradability_ok": bool(put_trad.get("entry_pass") or put_trad.get("tradability_ok")),
            },
            "selected_option": {
                "side": selected.get("side"),
                "instrument_key": selected.get("instrument_key"),
                "instrument_token": selected.get("instrument_token"),
                "strike": selected.get("strike"),
                "ltp": selected.get("ltp"),
                "spread_ratio": selected.get("spread_ratio"),
                "depth_total": selected.get("depth_total"),
                "response_efficiency": selected.get("response_efficiency"),
                "tradability_ok": bool(selected_trad.get("entry_pass") or selected_trad.get("tradability_ok")),
            },
            "cross_option": {
                "call_ltp": cross_option.get("call_ltp"),
                "put_ltp": cross_option.get("put_ltp"),
                "call_oi": cross_option.get("call_oi"),
                "put_oi": cross_option.get("put_oi"),
                "premium_bias": cross_option.get("premium_bias"),
                "oi_bias": cross_option.get("oi_bias"),
                "cross_option_ready": bool(cross_option.get("cross_option_ready")),
            },
            "economics": {
                "premium_floor_ok": _safe_float(selected.get("ltp"), 0.0) >= DEFAULT_PREMIUM_FLOOR,
                "economic_viability_ok": bool(selected_trad.get("entry_pass") or selected_trad.get("tradability_ok")),
                "target_points": DEFAULT_TARGET_POINTS,
                "stop_points": DEFAULT_STOP_POINTS,
            },
            "signals": {
                "futures_contradiction_flag": False,
                "queue_reload_veto_flag": False,
            },
        }

    def _stage_flags_contract_patch(
        self,
        snapshot_patch: Mapping[str, Any],
        common_patch: Mapping[str, Any],
        shared_core: Mapping[str, Any],
    ) -> dict[str, Any]:
        selected = dict(_nested_get(common_patch, "selected_option", default={}))
        futures = dict(_nested_get(common_patch, "futures", default={}))
        data_valid = bool(snapshot_patch.get("valid"))
        data_quality_ok = bool(snapshot_patch.get("sync_ok")) and bool(snapshot_patch.get("packet_gap_ok"))
        warmup_complete = int(snapshot_patch.get("samples_seen") or 0) >= 1
        return {
            "data_valid": data_valid,
            "data_quality_ok": data_quality_ok,
            "session_eligible": True,
            "warmup_complete": warmup_complete,
            "regime_ready": _safe_str(common_patch.get("regime")) in {
                REGIME_LOWVOL,
                REGIME_NORMAL,
                REGIME_FAST,
                REGIME_UNKNOWN,
            },
            "provider_ready_classic": bool(futures.get("liquidity_ok")),
            "provider_ready_miso": _safe_str(
                _nested_get(shared_core, "runtime_modes", "miso", "mode"),
                N.STRATEGY_RUNTIME_MODE_DISABLED,
            )
            != N.STRATEGY_RUNTIME_MODE_DISABLED,
            "selected_option_present": bool(selected.get("side")) and _safe_float(selected.get("ltp"), 0.0) > 0.0,
            "cross_option_context_ready": bool(
                _nested_get(shared_core, "options", "cross_option", "cross_option_ready", default=False)
            ),
            "oi_wall_context_ready": bool(
                _nested_get(shared_core, "strike_selection", "chain_context_ready", default=False)
            ),
            "risk_veto_active": False,
            "reconciliation_lock_active": False,
            "active_position_present": False,
        }

    def _families_contract_patch(
        self,
        family_surfaces: Mapping[str, Any],
        shared_core: Mapping[str, Any],
    ) -> dict[str, Any]:
        families = dict(_nested_get(family_surfaces, "families", default={}))
        patch: dict[str, Any] = {}

        for family_id in FAMILY_ORDER:
            fam = dict(_as_mapping(families.get(family_id)))
            call = dict(_as_mapping(_nested_get(fam, "branches", N.BRANCH_CALL, default={})))
            put = dict(_as_mapping(_nested_get(fam, "branches", N.BRANCH_PUT, default={})))

            if family_id == N.STRATEGY_FAMILY_MISO:
                patch[family_id] = {
                    "eligible": bool(fam.get("eligible")),
                    "mode": fam.get("mode") or fam.get("runtime_mode") or self._runtime_mode_for_family(family_id, shared_core),
                    "chain_context_ready": bool(
                        fam.get("chain_context_ready")
                        or _nested_get(shared_core, "strike_selection", "chain_context_ready", default=False)
                    ),
                    "selected_side": fam.get("selected_side") or _nested_get(shared_core, "options", "selected", "side", default=None),
                    "selected_strike": fam.get("selected_strike") or _nested_get(shared_core, "options", "selected", "strike", default=None),
                    "shadow_call_strike": fam.get("shadow_call_strike") or _nested_get(shared_core, "strike_selection", "shadow_call_strike", default=None),
                    "shadow_put_strike": fam.get("shadow_put_strike") or _nested_get(shared_core, "strike_selection", "shadow_put_strike", default=None),
                    "call_support": self._bool_support_patch(call),
                    "put_support": self._bool_support_patch(put),
                }
            elif family_id == N.STRATEGY_FAMILY_MISR:
                patch[family_id] = {
                    "eligible": bool(fam.get("eligible")),
                    "active_zone": self._misr_active_zone_patch(fam, shared_core),
                    "call_branch": self._bool_support_patch(call),
                    "put_branch": self._bool_support_patch(put),
                }
            else:
                patch[family_id] = {
                    "eligible": bool(fam.get("eligible")),
                    "call_branch": self._bool_support_patch(call),
                    "put_branch": self._bool_support_patch(put),
                }

        return patch

    @staticmethod
    def _bool_support_patch(surface: Mapping[str, Any]) -> dict[str, Any]:
        return {
            key: bool(value)
            for key, value in surface.items()
            if isinstance(value, bool)
        }

    @staticmethod
    def _misr_active_zone_patch(
        family_surface: Mapping[str, Any],
        shared_core: Mapping[str, Any],
    ) -> dict[str, Any]:
        zone = dict(_as_mapping(family_surface.get("active_zone")))
        return {
            "zone_id": zone.get("zone_id"),
            "zone_type": zone.get("zone_type"),
            "zone_price": zone.get("zone_price"),
            "quality_score": zone.get("quality_score"),
            "valid": bool(zone.get("valid")),
        }

    def _fallback_family_features_template(self, generated_at_ns: int) -> dict[str, Any]:
        return {
            "schema_version": _name("DEFAULT_SCHEMA_VERSION", 1),
            "service": N.SERVICE_FEATURES,
            "family_features_version": "1.1",
            "generated_at_ns": generated_at_ns,
            "snapshot": {},
            "provider_runtime": {},
            "market": {},
            "common": {},
            "stage_flags": {},
            "families": {family_id: {} for family_id in FAMILY_ORDER},
        }

    # ------------------------------------------------------------------
    # Utility extraction helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _object_to_snapshot_member(value: Mapping[str, Any]) -> Mapping[str, Any]:
        return value

    def _depth_lists(self, source: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        bids_raw = _json_loads_or(_pick(source, "bids", "depth_bids"), [])
        asks_raw = _json_loads_or(_pick(source, "asks", "depth_asks"), [])
        return self._normalize_depth_rows(bids_raw), self._normalize_depth_rows(asks_raw)

    @staticmethod
    def _normalize_depth_rows(value: Any) -> list[dict[str, Any]]:
        rows = value if isinstance(value, list) else []
        out: list[dict[str, Any]] = []
        for row in rows:
            mapping = _as_mapping(row)
            if not mapping:
                continue
            out.append(
                {
                    "price": _safe_float(_pick(mapping, "price", "p"), 0.0),
                    "quantity": _safe_float(_pick(mapping, "quantity", "qty", "q"), 0.0),
                    "orders": _safe_int(_pick(mapping, "orders", "order_count"), 0),
                }
            )
        return out

    def _extract_context_side_option(
        self,
        dhan_context: Mapping[str, Any],
        side: str,
    ) -> dict[str, Any]:
        candidates: list[Any] = []
        for key in (
            "selected_call",
            "call",
            "ce",
            "call_context",
            "selected_ce",
        ):
            if side == N.SIDE_CALL:
                candidates.append(dhan_context.get(key))
        for key in (
            "selected_put",
            "put",
            "pe",
            "put_context",
            "selected_pe",
        ):
            if side == N.SIDE_PUT:
                candidates.append(dhan_context.get(key))

        ladder = self._extract_strike_ladder(dhan_context)
        if ladder:
            side_rows = [row for row in ladder if row.get("side") == side]
            if side_rows:
                candidates.append(max(side_rows, key=lambda row: _safe_float(row.get("oi"), 0.0)))

        for candidate in candidates:
            mapping = dict(_as_mapping(candidate))
            if mapping:
                return self._fallback_option_surface(
                    mapping,
                    role=f"context_{side.lower()}",
                    provider_id=N.PROVIDER_DHAN,
                )
        return {}

    def _extract_strike_ladder(self, dhan_context: Mapping[str, Any]) -> list[dict[str, Any]]:
        raw_candidates = [
            dhan_context.get("strike_ladder"),
            dhan_context.get("ladder"),
            dhan_context.get("chain"),
            dhan_context.get("option_chain"),
            dhan_context.get("records"),
            dhan_context.get("data"),
        ]

        rows: list[Any] = []
        for raw in raw_candidates:
            parsed = _json_loads_or(raw, raw)
            if isinstance(parsed, list):
                rows = parsed
                break
            if isinstance(parsed, Mapping):
                for key in ("data", "records", "items", "ladder", "chain"):
                    nested = parsed.get(key)
                    nested_parsed = _json_loads_or(nested, nested)
                    if isinstance(nested_parsed, list):
                        rows = nested_parsed
                        break
            if rows:
                break

        out: list[dict[str, Any]] = []
        for row in rows:
            mapping = dict(_as_mapping(row))
            if not mapping:
                continue

            strike = _safe_float_or_none(_pick(mapping, "strike", "strike_price"))
            if strike is None:
                continue

            row_side = self._normalize_side(_pick(mapping, "side", "option_side", "right"))
            if row_side in (N.SIDE_CALL, N.SIDE_PUT):
                out.append(self._ladder_row(mapping, strike=strike, side=row_side))
                continue

            call_payload = _as_mapping(_pick(mapping, "call", "ce", "CE"))
            put_payload = _as_mapping(_pick(mapping, "put", "pe", "PE"))
            if call_payload:
                merged = dict(mapping)
                merged.update(call_payload)
                out.append(self._ladder_row(merged, strike=strike, side=N.SIDE_CALL))
            if put_payload:
                merged = dict(mapping)
                merged.update(put_payload)
                out.append(self._ladder_row(merged, strike=strike, side=N.SIDE_PUT))

        out.sort(key=lambda item: (float(item["strike"]), item["side"]))
        return out

    @staticmethod
    def _ladder_row(mapping: Mapping[str, Any], *, strike: float, side: str) -> dict[str, Any]:
        bid = _safe_float(_pick(mapping, "bid", "best_bid"), 0.0)
        ask = _safe_float(_pick(mapping, "ask", "best_ask"), 0.0)
        ltp = _safe_float(_pick(mapping, "ltp", "last_price"), 0.0)
        oi = _safe_float(_pick(mapping, "oi", "open_interest"), 0.0)
        volume = _safe_float(_pick(mapping, "volume"), 0.0)
        return {
            "strike": strike,
            "side": side,
            "ltp": ltp,
            "bid": bid,
            "ask": ask,
            "spread": max(0.0, ask - bid) if ask > 0 and bid > 0 else 0.0,
            "oi": oi,
            "oi_change": _safe_float(_pick(mapping, "oi_change", "change_oi"), 0.0),
            "volume": volume,
            "iv": _safe_float_or_none(_pick(mapping, "iv", "implied_volatility")),
            "instrument_key": _safe_str(_pick(mapping, "instrument_key")),
            "instrument_token": _safe_str(_pick(mapping, "instrument_token")),
            "trading_symbol": _safe_str(_pick(mapping, "trading_symbol", "symbol")),
        }

    def _nearest_oi_wall(
        self,
        *,
        ladder: Sequence[Mapping[str, Any]],
        side: str,
        reference: float | None,
    ) -> dict[str, Any]:
        candidates = [dict(row) for row in ladder if row.get("side") == side]
        if not candidates:
            return {
                "side": side,
                "strike": None,
                "distance_points": None,
                "distance_strikes": None,
                "wall_strength": 0.0,
                "near_wall": False,
                "strong_wall": False,
            }

        if reference is None or reference <= 0:
            best = max(candidates, key=lambda row: _safe_float(row.get("oi"), 0.0))
        else:
            directional = [
                row
                for row in candidates
                if (
                    (_safe_float(row.get("strike"), 0.0) >= reference)
                    if side == N.SIDE_CALL
                    else (_safe_float(row.get("strike"), 0.0) <= reference)
                )
            ]
            pool = directional or candidates
            best = min(
                pool,
                key=lambda row: (
                    abs(_safe_float(row.get("strike"), 0.0) - reference),
                    -_safe_float(row.get("oi"), 0.0),
                ),
            )

        max_oi = max((_safe_float(row.get("oi"), 0.0) for row in candidates), default=0.0)
        strike = _safe_float_or_none(best.get("strike"))
        distance_points = abs((strike or 0.0) - reference) if strike is not None and reference else None
        strike_step = self._infer_strike_step(candidates)
        distance_strikes = (
            _ratio(float(distance_points), strike_step, 0.0)
            if distance_points is not None and strike_step > 0
            else None
        )
        strength = _ratio(_safe_float(best.get("oi"), 0.0), max_oi, 0.0)

        return {
            "side": side,
            "strike": strike,
            "distance_points": distance_points,
            "distance_strikes": distance_strikes,
            "wall_strength": _clamp(strength, 0.0, 1.0),
            "near_wall": distance_strikes is not None and distance_strikes <= DEFAULT_OI_WALL_NEAR_STRIKES,
            "strong_wall": strength >= DEFAULT_OI_WALL_STRONG_MIN,
            "oi": _safe_float(best.get("oi"), 0.0),
            "volume": _safe_float(best.get("volume"), 0.0),
        }

    @staticmethod
    def _infer_strike_step(rows: Sequence[Mapping[str, Any]]) -> float:
        strikes = sorted({_safe_float(row.get("strike"), 0.0) for row in rows if _safe_float(row.get("strike"), 0.0) > 0})
        diffs = [b - a for a, b in zip(strikes, strikes[1:]) if b - a > 0]
        return min(diffs) if diffs else 50.0

    @staticmethod
    def _normalize_side(value: Any) -> str | None:
        text = _safe_str(value).upper()
        if text in {"CALL", "CE", "C", N.SIDE_CALL}:
            return N.SIDE_CALL
        if text in {"PUT", "PE", "P", N.SIDE_PUT}:
            return N.SIDE_PUT
        return None

    def _runtime_mode_for_family(self, family_id: str, shared_core: Mapping[str, Any]) -> str:
        if family_id == N.STRATEGY_FAMILY_MISO:
            return _safe_str(
                _nested_get(shared_core, "runtime_modes", "miso", "mode"),
                N.STRATEGY_RUNTIME_MODE_DISABLED,
            )
        return _safe_str(
            _nested_get(shared_core, "runtime_modes", "classic", "mode"),
            N.STRATEGY_RUNTIME_MODE_DHAN_DEGRADED,
        )

    def _tradability_for_family_branch(
        self,
        family_id: str,
        branch_id: str,
        shared_core: Mapping[str, Any],
    ) -> dict[str, Any]:
        prefix = "miso" if family_id == N.STRATEGY_FAMILY_MISO else "classic"
        key = f"{prefix}_{'call' if branch_id == N.BRANCH_CALL else 'put'}"
        return dict(_nested_get(shared_core, "tradability", key, default={}))

    def _option_for_branch(
        self,
        branch_id: str,
        shared_core: Mapping[str, Any],
    ) -> dict[str, Any]:
        key = "call" if branch_id == N.BRANCH_CALL else "put"
        return dict(_nested_get(shared_core, "options", key, default={}))

    def _side_oi_wall(self, side: str, shared_core: Mapping[str, Any]) -> dict[str, Any]:
        key = "call" if side == N.SIDE_CALL else "put"
        return dict(_nested_get(shared_core, "oi_wall_context", key, default={}))

    def _fallback_branch_surface(
        self,
        *,
        family_id: str,
        branch_id: str,
        shared_core: Mapping[str, Any],
    ) -> dict[str, Any]:
        option = self._option_for_branch(branch_id, shared_core)
        tradability = self._tradability_for_family_branch(family_id, branch_id, shared_core)
        futures = dict(_nested_get(shared_core, "futures", "active", default={}))
        regime = dict(_nested_get(shared_core, "regime", default={}))
        oi_wall = self._side_oi_wall(BRANCH_TO_SIDE[branch_id], shared_core)
        eligible = bool(
            futures.get("valid")
            and (tradability.get("entry_pass") or tradability.get("tradability_ok"))
            and _safe_str(regime.get("regime"), REGIME_UNKNOWN) != REGIME_UNKNOWN
        )
        return {
            "family_id": family_id,
            "branch_id": branch_id,
            "side": BRANCH_TO_SIDE[branch_id],
            "runtime_mode": self._runtime_mode_for_family(family_id, shared_core),
            "eligible": eligible,
            "futures_features": futures,
            "option_features": option,
            "tradability": tradability,
            "regime_surface": regime,
            "oi_wall_context": oi_wall,
            "cross_option_context": dict(_nested_get(shared_core, "options", "cross_option", default={})),
            "surface_kind": f"{family_id.lower()}_feature_support",
            "source": "features_fallback_branch_surface",
        }

    @staticmethod
    def _fallback_branch_eligible(
        payload: Mapping[str, Any],
        shared_core: Mapping[str, Any],
    ) -> bool:
        if "eligible" in payload:
            return bool(payload.get("eligible"))
        tradability = dict(_as_mapping(payload.get("tradability")))
        return bool(tradability.get("entry_pass") or tradability.get("tradability_ok"))


# =============================================================================
# Service
# =============================================================================


class FeaturesService:
    def __init__(
        self,
        *,
        redis_client: Any,
        clock: Any,
        shutdown: Any,
        instance_id: str,
        settings: Any = None,
        logger: logging.Logger | None = None,
    ):
        self.redis = redis_client
        self.clock = clock
        self.shutdown = shutdown
        self.instance_id = instance_id
        self.settings = settings
        self.log = logger or LOGGER
        self.engine = FeatureEngine(redis_client=redis_client, logger=self.log)
        self.poll_interval_ms = _safe_int(
            _nested_get(settings, "runtime", "features_poll_interval_ms", default=None),
            DEFAULT_POLL_INTERVAL_MS,
        )
        self.heartbeat_ttl_ms = _safe_int(
            _nested_get(settings, "runtime", "heartbeat_ttl_ms", default=None),
            DEFAULT_HEARTBEAT_TTL_MS,
        )
        self.heartbeat_refresh_ms = DEFAULT_HEARTBEAT_REFRESH_MS
        self._last_heartbeat_ns = 0

    @property
    def poll_interval_s(self) -> float:
        return max(0.01, self.poll_interval_ms / 1000.0)

    def _now_ns(self) -> int:
        for name in ("now_ns", "time_ns"):
            func = getattr(self.clock, name, None)
            if callable(func):
                with contextlib.suppress(Exception):
                    return int(func())
        return time.time_ns()

    def run_once(self) -> dict[str, Any]:
        payload = self.engine.build_payload(now_ns=self._now_ns())
        self.publish_payload(payload)
        return payload

    def publish_payload(self, payload: Mapping[str, Any]) -> None:
        family_features = dict(_nested_get(payload, "family_features", default={}))
        family_surfaces = dict(_nested_get(payload, "family_surfaces", default={}))
        family_frames = dict(_nested_get(payload, "family_frames", default={}))
        feature_state = dict(_nested_get(payload, "feature_state", default={}))

        selected = _nested_get(family_features, "common", "selected_option", default={})
        provider_runtime = _nested_get(family_features, "provider_runtime", default={})

        hash_payload = {
            "frame_id": payload.get("frame_id"),
            "frame_ts_ns": payload.get("frame_ts_ns"),
            "ts_event_ns": payload.get("ts_event_ns"),
            "frame_valid": int(bool(payload.get("frame_valid"))),
            "warmup_complete": int(bool(payload.get("warmup_complete"))),
            "system_state": N.STATE_SCANNING if payload.get("frame_valid") else N.STATE_DISABLED,
            "selection_version": _safe_str(_nested_get(selected, "selection_version"), "mme-family-selection-v1"),
            "instrument_key": _safe_str(_nested_get(selected, "instrument_key"), ""),
            "strategy_mode": N.STRATEGY_AUTO,
            "strategy_family_id": "FAMILY",
            "branch_id": "",
            "doctrine_id": "",
            "family_runtime_mode": _safe_str(
                _nested_get(provider_runtime, "family_runtime_mode"),
                _name("FAMILY_RUNTIME_MODE_OBSERVE_ONLY", "observe_only"),
            ),
            "strategy_runtime_mode": _safe_str(
                _nested_get(family_features, "common", "strategy_runtime_mode_classic"),
                N.STRATEGY_RUNTIME_MODE_DHAN_DEGRADED,
            ),
            "family_features_version": _safe_str(
                family_features.get("family_features_version"),
                "unknown",
            ),
            "family_features_json": _json_dumps(family_features),
            "family_surfaces_json": _json_dumps(family_surfaces),
            "family_frames_json": _json_dumps(family_frames),
            "feature_state_json": _json_dumps(feature_state),
            "payload_json": _json_dumps(payload),
            "explain": _json_dumps(payload.get("explain", {})),
        }

        stream_payload = {
            "schema_version": _safe_int(payload.get("schema_version"), 1),
            "service": N.SERVICE_FEATURES,
            "frame_id": hash_payload["frame_id"],
            "frame_ts_ns": hash_payload["frame_ts_ns"],
            "family_features_version": hash_payload["family_features_version"],
            "family_features_json": hash_payload["family_features_json"],
            "family_surfaces_json": hash_payload["family_surfaces_json"],
        }

        self.redis.hset(N.HASH_STATE_FEATURES_MME_FUT, mapping=hash_payload)
        self.redis.xadd(
            N.STREAM_FEATURES_MME,
            fields=stream_payload,
            maxlen=DEFAULT_STREAM_MAXLEN,
            approximate=True,
        )

        with contextlib.suppress(Exception):
            self.redis.hset(
                N.HASH_STATE_BASELINES_MME_FUT,
                mapping={
                    "frame_ts_ns": payload.get("frame_ts_ns"),
                    "regime": _safe_str(_nested_get(family_features, "common", "regime"), REGIME_UNKNOWN),
                    "family_features_version": hash_payload["family_features_version"],
                },
            )

        with contextlib.suppress(Exception):
            self.redis.hset(
                N.HASH_STATE_OPTION_CONFIRM,
                mapping={
                    "frame_ts_ns": payload.get("frame_ts_ns"),
                    "selected_option_json": _json_dumps(selected),
                    "cross_option_json": _json_dumps(
                        _nested_get(family_features, "common", "cross_option", default={})
                    ),
                },
            )

    def _publish_health(self, *, status: str, detail: str) -> None:
        now_ns = self._now_ns()
        payload = {
            "service": N.SERVICE_FEATURES,
            "instance_id": self.instance_id,
            "status": status,
            "detail": detail,
            "ts_ns": now_ns,
        }
        self.redis.hset(N.KEY_HEALTH_FEATURES, mapping=payload)
        with contextlib.suppress(Exception):
            self.redis.pexpire(N.KEY_HEALTH_FEATURES, self.heartbeat_ttl_ms)
        with contextlib.suppress(Exception):
            self.redis.xadd(
                N.STREAM_SYSTEM_HEALTH,
                fields=payload,
                maxlen=DEFAULT_STREAM_MAXLEN,
                approximate=True,
            )
        self._last_heartbeat_ns = now_ns

    def publish_error(self, *, where: str, exc: BaseException) -> None:
        payload = {
            "service": N.SERVICE_FEATURES,
            "instance_id": self.instance_id,
            "where": where,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "ts_ns": self._now_ns(),
        }
        with contextlib.suppress(Exception):
            self.redis.xadd(
                N.STREAM_SYSTEM_ERRORS,
                fields=payload,
                maxlen=DEFAULT_STREAM_MAXLEN,
                approximate=True,
            )

    def start(self) -> int:
        self.log.info("features_service_started instance_id=%s", self.instance_id)
        self._publish_health(status=N.HEALTH_STATUS_WARN, detail="features_starting")

        try:
            while not self.shutdown.is_set():
                status = N.HEALTH_STATUS_OK
                detail = "features_ok"
                try:
                    self.run_once()
                except Exception as exc:
                    self.log.exception("features_service_loop_error")
                    self.publish_error(where="features_service_loop_error", exc=exc)
                    status = N.HEALTH_STATUS_ERROR
                    detail = f"loop_error:{type(exc).__name__}"

                now_ns = self._now_ns()
                if now_ns - self._last_heartbeat_ns >= self.heartbeat_refresh_ms * 1_000_000:
                    with contextlib.suppress(Exception):
                        self._publish_health(status=status, detail=detail)

                self.shutdown.wait(self.poll_interval_s)
        finally:
            with contextlib.suppress(Exception):
                self._publish_health(status=N.HEALTH_STATUS_WARN, detail="features_stopping")

        self.log.info("features_service_stopped")
        return 0


# =============================================================================
# Compatibility aliases / proof helpers
# =============================================================================


FeatureService = FeaturesService


def _object_to_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "to_dict"):
        with contextlib.suppress(Exception):
            out = value.to_dict()
            if isinstance(out, Mapping):
                return dict(out)
    if hasattr(value, "__dict__"):
        return dict(vars(value))
    return {"value": _jsonable(value)}


def _load_provider_runtime_state(redis_client: Any) -> M.ProviderRuntimeState | Mapping[str, Any] | None:
    return SnapshotReader(redis_client).read_provider_runtime()


def _load_dhan_context_state(redis_client: Any) -> M.DhanContextState | Mapping[str, Any] | None:
    return SnapshotReader(redis_client).read_dhan_context()


def _load_snapshot_state(
    redis_client: Any,
    *,
    kind: str = "active",
    dhan_context: M.DhanContextState | Mapping[str, Any] | None = None,
) -> SnapshotFrameView | None:
    reader = SnapshotReader(redis_client)
    if kind.lower() == "dhan":
        return reader.read_dhan_frame(dhan_context)
    return reader.read_active_frame(dhan_context)


# =============================================================================
# Entrypoint
# =============================================================================


def run(context: Any) -> int:
    settings = getattr(context, "settings", None)
    if settings is None and callable(get_settings):
        settings = get_settings()

    redis_runtime = getattr(context, "redis", None)
    if redis_runtime is None:
        raise RuntimeError("features requires context.redis")
    redis_client = redis_runtime.sync if hasattr(redis_runtime, "sync") else redis_runtime

    shutdown = getattr(context, "shutdown", None)
    clock = getattr(context, "clock", None)
    instance_id = _safe_str(getattr(context, "instance_id", ""))

    if shutdown is None:
        raise RuntimeError("features requires context.shutdown")
    if clock is None:
        raise RuntimeError("features requires context.clock")
    if not instance_id:
        raise RuntimeError("features requires context.instance_id")

    service = FeaturesService(
        redis_client=redis_client,
        clock=clock,
        shutdown=shutdown,
        instance_id=instance_id,
        settings=settings,
        logger=LOGGER,
    )
    return service.start()


__all__ = [
    "FeatureEngine",
    "FeatureService",
    "FeaturesService",
    "SnapshotFrameView",
    "SnapshotReader",
    "_load_dhan_context_state",
    "_load_provider_runtime_state",
    "_load_snapshot_state",
    "run",
]
