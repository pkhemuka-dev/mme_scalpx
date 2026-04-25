from __future__ import annotations

"""
app/mme_scalpx/services/features.py

Freeze-grade provider-aware feature publisher for ScalpX MME family build.

Ownership
---------
This module OWNS:
- reading latest provider-aware snapshot state
- deriving deterministic shared feature surfaces
- wiring shared feature-family helpers:
  option_core.py, futures_core.py, tradability.py, regime.py, strike_selection.py
- wiring all five per-family feature surfaces:
  MIST, MISB, MISC, MISR, MISO
- publishing stable family_features
- publishing stable family_surfaces
- publishing feature hash / feature stream / heartbeat

This module DOES NOT own:
- raw feed ingestion
- provider failover policy
- strategy decisions
- doctrine state machines
- cooldowns
- execution
- risk mutation
- order placement

Frozen laws
-----------
- features.py is a feature publisher only.
- family_features is the strict contract payload consumed later by strategy.py /
  strategy_family/*.
- family_surfaces is the richer audit/support payload.
- OI wall / strike ladder is shared context and quality surface only.
- Price action + futures flow remain trigger truth.
- No doctrine-leaf strategy logic is embedded here.
"""

import contextlib
import importlib
import json
import logging
import math
import time
from dataclasses import dataclass
from typing import Any, Final, Mapping, MutableMapping, Sequence

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services.feature_family import contracts as FF_C

try:
    from app.mme_scalpx.services.feature_family import common as FF_H
except Exception:  # pragma: no cover
    FF_H = None  # type: ignore[assignment]


LOGGER = logging.getLogger("app.mme_scalpx.services.features")


# =============================================================================
# Frozen constants
# =============================================================================

EPSILON: Final[float] = 1e-8
DEFAULT_POLL_INTERVAL_MS: Final[int] = 100
DEFAULT_HEARTBEAT_TTL_MS: Final[int] = 15_000
DEFAULT_STREAM_MAXLEN: Final[int] = 10_000

DEFAULT_PREMIUM_FLOOR: Final[float] = 40.0
DEFAULT_TARGET_POINTS: Final[float] = 5.0
DEFAULT_STOP_POINTS: Final[float] = 4.0
DEFAULT_SPREAD_RATIO_MAX: Final[float] = 1.80
DEFAULT_DEPTH_MIN: Final[int] = 1
DEFAULT_RESPONSE_EFF_MIN: Final[float] = 0.0
DEFAULT_SYNC_MAX_MS: Final[int] = 300
DEFAULT_PACKET_GAP_MS: Final[int] = 1000

BRANCH_CALL: Final[str] = getattr(N, "BRANCH_CALL", "CALL")
BRANCH_PUT: Final[str] = getattr(N, "BRANCH_PUT", "PUT")
SIDE_CALL: Final[str] = getattr(N, "SIDE_CALL", "CALL")
SIDE_PUT: Final[str] = getattr(N, "SIDE_PUT", "PUT")

FAMILY_MIST: Final[str] = getattr(N, "STRATEGY_FAMILY_MIST", "MIST")
FAMILY_MISB: Final[str] = getattr(N, "STRATEGY_FAMILY_MISB", "MISB")
FAMILY_MISC: Final[str] = getattr(N, "STRATEGY_FAMILY_MISC", "MISC")
FAMILY_MISR: Final[str] = getattr(N, "STRATEGY_FAMILY_MISR", "MISR")
FAMILY_MISO: Final[str] = getattr(N, "STRATEGY_FAMILY_MISO", "MISO")

FAMILY_IDS: Final[tuple[str, ...]] = tuple(
    getattr(
        FF_C,
        "FAMILY_IDS",
        (FAMILY_MIST, FAMILY_MISB, FAMILY_MISC, FAMILY_MISR, FAMILY_MISO),
    )
)
BRANCH_IDS: Final[tuple[str, ...]] = tuple(
    getattr(FF_C, "BRANCH_IDS", (BRANCH_CALL, BRANCH_PUT))
)

PROVIDER_DHAN: Final[str] = getattr(N, "PROVIDER_DHAN", "DHAN")
PROVIDER_ZERODHA: Final[str] = getattr(N, "PROVIDER_ZERODHA", "ZERODHA")

PROVIDER_IDS: Final[tuple[str, ...]] = tuple(
    getattr(FF_C, "ALLOWED_PROVIDER_IDS", (PROVIDER_ZERODHA, PROVIDER_DHAN))
)
PROVIDER_STATUSES: Final[tuple[str, ...]] = tuple(
    getattr(
        FF_C,
        "ALLOWED_PROVIDER_STATUSES",
        ("HEALTHY", "DEGRADED", "STALE", "UNAVAILABLE", "AVAILABLE"),
    )
)

REGIME_LOWVOL: Final[str] = getattr(FF_C, "REGIME_LOWVOL", "LOWVOL")
REGIME_NORMAL: Final[str] = getattr(FF_C, "REGIME_NORMAL", "NORMAL")
REGIME_FAST: Final[str] = getattr(FF_C, "REGIME_FAST", "FAST")
REGIME_IDS: Final[tuple[str, ...]] = tuple(
    getattr(FF_C, "ALLOWED_REGIMES", (REGIME_LOWVOL, REGIME_NORMAL, REGIME_FAST))
)

RUNTIME_DISABLED: Final[str] = getattr(N, "STRATEGY_RUNTIME_MODE_DISABLED", "DISABLED")
RUNTIME_NORMAL: Final[str] = getattr(N, "STRATEGY_RUNTIME_MODE_NORMAL", "NORMAL")
RUNTIME_DHAN_DEGRADED: Final[str] = getattr(
    N,
    "STRATEGY_RUNTIME_MODE_DHAN_DEGRADED",
    "DHAN-DEGRADED",
)
RUNTIME_BASE_5DEPTH: Final[str] = getattr(
    N,
    "STRATEGY_RUNTIME_MODE_BASE_5DEPTH",
    "BASE-5DEPTH",
)
RUNTIME_DEPTH20: Final[str] = getattr(
    N,
    "STRATEGY_RUNTIME_MODE_DEPTH20_ENHANCED",
    "DEPTH20-ENHANCED",
)
FAMILY_RUNTIME_OBSERVE: Final[str] = getattr(
    N,
    "FAMILY_RUNTIME_MODE_OBSERVE_ONLY",
    "observe_only",
)

FAMILY_RUNTIME_MODES: Final[tuple[str, ...]] = tuple(
    getattr(FF_C, "ALLOWED_FAMILY_RUNTIME_MODES", (FAMILY_RUNTIME_OBSERVE,))
)
CLASSIC_RUNTIME_MODES: Final[tuple[str, ...]] = tuple(
    getattr(
        FF_C,
        "CLASSIC_ALLOWED_STRATEGY_RUNTIME_MODES",
        (RUNTIME_NORMAL, RUNTIME_DHAN_DEGRADED, RUNTIME_DISABLED),
    )
)
MISO_RUNTIME_MODES: Final[tuple[str, ...]] = tuple(
    getattr(
        FF_C,
        "MISO_ALLOWED_STRATEGY_RUNTIME_MODES",
        (RUNTIME_BASE_5DEPTH, RUNTIME_DEPTH20, RUNTIME_DISABLED),
    )
)

SERVICE_FEATURES: Final[str] = getattr(N, "SERVICE_FEATURES", "features")

STREAM_FEATURES: Final[str] = getattr(
    N,
    "STREAM_FEATURES_MME",
    getattr(N, "STREAM_FEATURES", N.STREAM_FEATURES_MME),
)
STREAM_HEALTH: Final[str] = getattr(N, "STREAM_SYSTEM_HEALTH", N.STREAM_SYSTEM_HEALTH)
STREAM_ERRORS: Final[str] = getattr(N, "STREAM_SYSTEM_ERRORS", N.STREAM_SYSTEM_ERRORS)

HASH_FEATURES: Final[str] = getattr(
    N,
    "HASH_STATE_FEATURES_MME_FUT",
    getattr(N, "STATE_FEATURES_MME_FUT", N.HASH_STATE_FEATURES_MME_FUT),
)
HASH_BASELINES: Final[str] = getattr(
    N,
    "HASH_STATE_BASELINES_MME_FUT",
    N.HASH_STATE_BASELINES_MME_FUT,
)
HASH_OPTION_CONFIRM: Final[str] = getattr(
    N,
    "HASH_STATE_OPTION_CONFIRM",
    N.HASH_STATE_OPTION_CONFIRM,
)
KEY_HEALTH_FEATURES: Final[str] = getattr(
    N,
    "KEY_HEALTH_FEATURES",
    getattr(N, "HB_FEATURES", "features:heartbeat"),
)

HASH_PROVIDER_RUNTIME: Final[str] = getattr(
    N,
    "HASH_STATE_PROVIDER_RUNTIME",
    N.HASH_STATE_PROVIDER_RUNTIME,
)
HASH_DHAN_CONTEXT: Final[str] = getattr(
    N,
    "HASH_STATE_DHAN_CONTEXT",
    N.HASH_STATE_DHAN_CONTEXT,
)
HASH_FUT_ACTIVE: Final[str] = getattr(
    N,
    "HASH_STATE_SNAPSHOT_MME_FUT_ACTIVE",
    getattr(N, "HASH_STATE_SNAPSHOT_MME_FUT", N.HASH_STATE_SNAPSHOT_MME_FUT),
)
HASH_OPT_ACTIVE: Final[str] = getattr(
    N,
    "HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ACTIVE",
    getattr(
        N,
        "HASH_STATE_SNAPSHOT_MME_OPT_SELECTED",
        N.HASH_STATE_SNAPSHOT_MME_OPT_SELECTED,
    ),
)
HASH_FUT_DHAN: Final[str] = getattr(
    N,
    "HASH_STATE_SNAPSHOT_MME_FUT_DHAN",
    N.HASH_STATE_SNAPSHOT_MME_FUT_DHAN,
)
HASH_OPT_DHAN: Final[str] = getattr(
    N,
    "HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_DHAN",
    N.HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_DHAN,
)

SHARED_MODULES: Final[Mapping[str, str]] = {
    "option_core": "app.mme_scalpx.services.feature_family.option_core",
    "futures_core": "app.mme_scalpx.services.feature_family.futures_core",
    "tradability": "app.mme_scalpx.services.feature_family.tradability",
    "regime": "app.mme_scalpx.services.feature_family.regime",
    "strike_selection": "app.mme_scalpx.services.feature_family.strike_selection",
}

FAMILY_MODULES: Final[Mapping[str, str]] = {
    FAMILY_MIST: "app.mme_scalpx.services.feature_family.mist_surface",
    FAMILY_MISB: "app.mme_scalpx.services.feature_family.misb_surface",
    FAMILY_MISC: "app.mme_scalpx.services.feature_family.misc_surface",
    FAMILY_MISR: "app.mme_scalpx.services.feature_family.misr_surface",
    FAMILY_MISO: "app.mme_scalpx.services.feature_family.miso_surface",
}


class FeaturePublicationError(RuntimeError):
    """Raised when family feature publication cannot be made contract-safe."""


# =============================================================================
# Small helpers
# =============================================================================


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace").strip() or default
    text = str(value).strip()
    return text if text else default


def _safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = _safe_str(value).lower()
    if text in {"1", "true", "yes", "y", "on", "ok", "healthy", "available"}:
        return True
    if text in {"0", "false", "no", "n", "off", "none", "null", "unavailable"}:
        return False
    return default


def _safe_int(value: Any, default: int = 0) -> int:
    if value is None or isinstance(value, bool):
        return default
    try:
        text = _safe_str(value)
        return int(float(text)) if text else default
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    if value is None or isinstance(value, bool):
        return default
    try:
        text = _safe_str(value)
        if not text:
            return default
        out = float(text)
    except Exception:
        return default
    return out if math.isfinite(out) else default


def _safe_float_or_none(value: Any) -> float | None:
    if value is None or value == "" or isinstance(value, bool):
        return None
    out = _safe_float(value, float("nan"))
    return out if math.isfinite(out) else None


def _ratio(numer: float, denom: float, default: float = 0.0) -> float:
    if abs(denom) <= EPSILON:
        return default
    return numer / denom


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "to_dict"):
        with contextlib.suppress(Exception):
            out = value.to_dict()
            if isinstance(out, Mapping):
                return dict(out)
    _dataclass_fields = getattr(value, "__dataclass_fields__", None)
    if isinstance(_dataclass_fields, Mapping):
        return {
            str(_field_name): getattr(value, str(_field_name))
            for _field_name in _dataclass_fields.keys()
        }
    if hasattr(value, "__dict__"):
        return dict(vars(value))
    return {}


def _pick(mapping: Mapping[str, Any] | None, *keys: str, default: Any = None) -> Any:
    if not isinstance(mapping, Mapping):
        return default
    for key in keys:
        if key in mapping and mapping[key] not in (None, ""):
            return mapping[key]
    return default


def _nested(root: Any, *keys: str, default: Any = None) -> Any:
    cur = root
    for key in keys:
        if not isinstance(cur, Mapping):
            return default
        cur = cur.get(key)
        if cur is None:
            return default
    return cur


def _json_load(value: Any, default: Any) -> Any:
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
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, Mapping):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(v) for v in value]
    if hasattr(value, "to_dict"):
        with contextlib.suppress(Exception):
            return _jsonable(value.to_dict())
    _dataclass_fields = getattr(value, "__dataclass_fields__", None)
    if isinstance(_dataclass_fields, Mapping):
        return {
            str(_field_name): _jsonable(getattr(value, str(_field_name)))
            for _field_name in _dataclass_fields.keys()
        }
    if hasattr(value, "__dict__"):
        return _jsonable(vars(value))
    return str(value)


def _json_dump(value: Any) -> str:
    """
    Serialize without sorting keys.

    contracts.py validates exact key order after json.loads(), so sorted JSON
    silently breaks the live Redis proof even when the in-memory payload is
    contract-valid.
    """
    return json.dumps(
        _jsonable(value),
        ensure_ascii=False,
        sort_keys=False,
        separators=(",", ":"),
        allow_nan=False,
    )


def _decode_hash(raw: Mapping[Any, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in (raw or {}).items():
        k = _safe_str(key)
        if isinstance(value, bytes):
            value = value.decode("utf-8", errors="replace")
        if isinstance(value, str):
            text = value.strip()
            if (text.startswith("{") and text.endswith("}")) or (
                text.startswith("[") and text.endswith("]")
            ):
                out[k] = _json_load(text, text)
            elif text.lower() in {"none", "null"}:
                out[k] = None
            else:
                out[k] = value
        else:
            out[k] = value
    return out


def _literal(value: Any, allowed: Sequence[str], default: str | None) -> str | None:
    text = _safe_str(value)
    if text in allowed:
        return text
    if default in allowed:
        return default
    if allowed:
        return allowed[0]
    return default


def _provider_id(value: Any, default: str = PROVIDER_DHAN) -> str:
    return _safe_str(_literal(value, PROVIDER_IDS, default), default)


# Missing provider-runtime hash must not become HEALTHY.
def _provider_status(value: Any) -> str:
    default = (
        getattr(N, "PROVIDER_STATUS_UNAVAILABLE", None)
        or getattr(N, "PROVIDER_STATUS_STALE", None)
        or "UNAVAILABLE"
    )
    return _safe_str(_literal(value, PROVIDER_STATUSES, default), default)


def _family_runtime_mode(value: Any) -> str:
    return _safe_str(
        _literal(value, FAMILY_RUNTIME_MODES, FAMILY_RUNTIME_OBSERVE),
        FAMILY_RUNTIME_OBSERVE,
    )


def _classic_runtime_mode(value: Any) -> str:
    return _safe_str(
        _literal(value, CLASSIC_RUNTIME_MODES, RUNTIME_NORMAL),
        RUNTIME_NORMAL,
    )


def _miso_runtime_mode(value: Any) -> str:
    return _safe_str(
        _literal(value, MISO_RUNTIME_MODES, RUNTIME_BASE_5DEPTH),
        RUNTIME_BASE_5DEPTH,
    )


def _regime(value: Any) -> str:
    text = _safe_str(value, REGIME_NORMAL).upper()
    return text if text in REGIME_IDS else REGIME_NORMAL


def _normalize_side(value: Any) -> str | None:
    text = _safe_str(value).upper()
    if text in {"CE", "C", "CALL", SIDE_CALL}:
        return SIDE_CALL
    if text in {"PE", "P", "PUT", SIDE_PUT}:
        return SIDE_PUT
    return None


def _branch_side(branch_id: str) -> str:
    return SIDE_CALL if branch_id == BRANCH_CALL else SIDE_PUT


def _side_branch(side: str | None) -> str | None:
    if side == SIDE_CALL:
        return BRANCH_CALL
    if side == SIDE_PUT:
        return BRANCH_PUT
    return None


def _load_module(path: str, logger: logging.Logger) -> Any | None:
    try:
        return importlib.import_module(path)
    except Exception as exc:
        logger.warning("feature_family_module_unavailable module=%s error=%s", path, exc)
        return None


def _call_first(
    module: Any | None,
    names: Sequence[str],
    *args: Any,
    **kwargs: Any,
) -> Any | None:
    if module is None:
        return None
    for name in names:
        fn = getattr(module, name, None)
        if not callable(fn):
            continue
        variants = (
            (args, kwargs),
            ((), kwargs),
            (args, {}),
            ((), {}),
        )
        for var_args, var_kwargs in variants:
            try:
                return fn(*var_args, **var_kwargs)
            except TypeError:
                continue
            except Exception:
                return None
    return None


def _patch_existing(target: MutableMapping[str, Any], values: Mapping[str, Any]) -> None:
    for key, value in values.items():
        if key not in target:
            continue
        if isinstance(target[key], MutableMapping) and isinstance(value, Mapping):
            _patch_existing(target[key], value)
        else:
            target[key] = value


def _empty_builder(name: str, fallback: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fn = getattr(FF_C, name, None)
    if callable(fn):
        return dict(fn())
    return dict(fallback or {})



def _plain_mapping_from_object(value):
    """
    Return a plain dict for Mapping, normal objects, and slots dataclasses.

    This is required because SnapshotMemberView / SnapshotFrameView are
    dataclass(slots=True), so they intentionally do not expose __dict__.
    Keep this helper local to features.py because this is a feature-runtime
    serialization seam, not a model contract change.
    """
    if value is None:
        return {}

    if isinstance(value, Mapping):
        return dict(value)

    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        out = to_dict()
        if isinstance(out, Mapping):
            return dict(out)

    fields = getattr(value, "__dataclass_fields__", None)
    if isinstance(fields, Mapping):
        return {str(name): getattr(value, str(name)) for name in fields.keys()}

    raw = getattr(value, "__dict__", None)
    if isinstance(raw, Mapping):
        return dict(raw)

    raise TypeError(
        f"cannot convert {type(value).__name__} to plain mapping"
    )



# =============================================================================
# Snapshot reader
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


class SnapshotReader:
    def __init__(self, redis_client: Any):
        self.redis = redis_client

    def read_hash(self, key: str) -> dict[str, Any]:
        if not key:
            return {}
        with contextlib.suppress(Exception):
            return _decode_hash(self.redis.hgetall(key) or {})
        return {}

    def read_provider_runtime(self) -> dict[str, Any]:
        return self.read_hash(HASH_PROVIDER_RUNTIME)

    def read_dhan_context(self) -> dict[str, Any]:
        return self.read_hash(HASH_DHAN_CONTEXT)

    def read_active_frame(
        self,
        dhan_context: Mapping[str, Any] | None = None,
    ) -> SnapshotFrameView | None:
        return self._frame(
            kind="active",
            futures=self.read_hash(HASH_FUT_ACTIVE),
            selected=self.read_hash(HASH_OPT_ACTIVE),
            dhan_context=dhan_context or {},
        )

    def read_dhan_frame(
        self,
        dhan_context: Mapping[str, Any] | None = None,
    ) -> SnapshotFrameView | None:
        return self._frame(
            kind="dhan",
            futures=self.read_hash(HASH_FUT_DHAN),
            selected=self.read_hash(HASH_OPT_DHAN),
            dhan_context=dhan_context or {},
        )

    @staticmethod
    def _frame(
        *,
        kind: str,
        futures: Mapping[str, Any],
        selected: Mapping[str, Any],
        dhan_context: Mapping[str, Any],
    ) -> SnapshotFrameView | None:
        if not futures and not selected and not dhan_context:
            return None

        fut_ts = _safe_int(_pick(futures, "ts_event_ns", "event_ts_ns", "timestamp_ns"), 0)
        opt_ts = _safe_int(_pick(selected, "ts_event_ns", "event_ts_ns", "timestamp_ns"), 0)
        recv_ts = max(
            _safe_int(_pick(futures, "ts_recv_ns", "recv_ts_ns"), 0),
            _safe_int(_pick(selected, "ts_recv_ns", "recv_ts_ns"), 0),
        ) or None
        ts_event = max(fut_ts, opt_ts) or None
        provider = (
            _safe_str(
                _pick(
                    selected,
                    "provider_id",
                    default=_pick(
                        futures,
                        "provider_id",
                        default=_pick(dhan_context, "provider_id"),
                    ),
                )
            )
            or None
        )
        fut_ltp = _safe_float(_pick(futures, "ltp", "last_price"), 0.0)
        opt_ltp = _safe_float(_pick(selected, "ltp", "last_price"), 0.0)
        valid = fut_ltp > 0.0 and opt_ltp > 0.0

        return SnapshotFrameView(
            kind=kind,
            futures=dict(futures),
            selected_option=dict(selected),
            dhan_context=dict(dhan_context),
            ts_event_ns=ts_event,
            ts_recv_ns=recv_ts,
            provider_id=provider,
            valid=valid,
            reason="OK" if valid else "EMPTY",
        )


# =============================================================================
# Feature engine
# =============================================================================


class FeatureEngine:
    def __init__(self, *, redis_client: Any, logger: logging.Logger | None = None):
        self.redis = redis_client
        self.log = logger or LOGGER
        self.reader = SnapshotReader(redis_client)
        self.shared_modules = {
            name: _load_module(path, self.log) for name, path in SHARED_MODULES.items()
        }
        self.family_modules = {
            name: _load_module(path, self.log) for name, path in FAMILY_MODULES.items()
        }

    def build_payload(self, *, now_ns: int | None = None) -> dict[str, Any]:
        generated_at_ns = int(now_ns or time.time_ns())

        provider_raw = self.reader.read_provider_runtime()
        dhan_context = self.reader.read_dhan_context()
        active_frame = self.reader.read_active_frame(dhan_context)
        dhan_frame = self.reader.read_dhan_frame(dhan_context)

        provider_runtime = self._provider_runtime(provider_raw)
        shared_core = self._shared_core(
            generated_at_ns=generated_at_ns,
            provider_runtime=provider_runtime,
            dhan_context=dhan_context,
            active_frame=active_frame,
            dhan_frame=dhan_frame,
        )
        family_surfaces = self._family_surfaces(
            generated_at_ns=generated_at_ns,
            provider_runtime=provider_runtime,
            shared_core=shared_core,
        )
        family_features = self._family_features(
            generated_at_ns=generated_at_ns,
            provider_runtime=provider_runtime,
            shared_core=shared_core,
            family_surfaces=family_surfaces,
        )
        family_frames = self._family_frames(
            generated_at_ns=generated_at_ns,
            provider_runtime=provider_runtime,
            shared_core=shared_core,
            family_surfaces=family_surfaces,
        )

        return {
            "schema_version": getattr(N, "DEFAULT_SCHEMA_VERSION", 1),
            "service": SERVICE_FEATURES,
            "generated_at_ns": generated_at_ns,
            "frame_id": f"features-{generated_at_ns}",
            "frame_ts_ns": generated_at_ns,
            "ts_event_ns": generated_at_ns,
            "frame_valid": bool(_nested(family_features, "snapshot", "valid", default=False)),
            "warmup_complete": bool(
                _nested(family_features, "stage_flags", "warmup_complete", default=False)
            ),
            "family_features": family_features,
            "family_surfaces": family_surfaces,
            "family_frames": family_frames,
            "shared_core": shared_core,
            "provider_runtime": provider_runtime,
            "explain": {
                "owner": "services.features",
                "feature_publisher_only": True,
                "strategy_decision_logic_present": False,
                "provider_failover_policy_present": False,
                "oi_wall_law": "shared_context_quality_surface_not_trigger",
            },
        }

    def _provider_runtime(self, raw: Mapping[str, Any]) -> dict[str, Any]:
        active_fut = _provider_id(
            _pick(
                raw,
                "active_futures_provider_id",
                "active_future_provider_id",
                "futures_provider_id",
            ),
            PROVIDER_DHAN,
        )
        active_opt = _provider_id(
            _pick(
                raw,
                "active_selected_option_provider_id",
                "selected_option_provider_id",
                "option_provider_id",
            ),
            active_fut,
        )
        active_ctx = _provider_id(
            _pick(
                raw,
                "active_option_context_provider_id",
                "option_context_provider_id",
                "context_provider_id",
            ),
            PROVIDER_DHAN,
        )
        active_exec = _provider_id(
            _pick(
                raw,
                "active_execution_provider_id",
                "execution_primary_provider_id",
                "execution_provider_id",
            ),
            PROVIDER_ZERODHA,
        )
        fallback_exec = _provider_id(
            _pick(raw, "fallback_execution_provider_id", "execution_fallback_provider_id"),
            PROVIDER_DHAN,
        )

        return {
            "active_futures_provider_id": active_fut,
            "active_selected_option_provider_id": active_opt,
            "active_option_context_provider_id": active_ctx,
            "active_execution_provider_id": active_exec,
            "fallback_execution_provider_id": fallback_exec,
            "provider_runtime_mode": _safe_str(_pick(raw, "provider_runtime_mode", "runtime_mode"), "NORMAL"),
            "family_runtime_mode": _family_runtime_mode(_pick(raw, "family_runtime_mode")),
            "futures_provider_status": _provider_status(
                _pick(raw, "futures_provider_status", "active_futures_provider_status")
            ),
            "selected_option_provider_status": _provider_status(
                _pick(raw, "selected_option_provider_status", "active_selected_option_provider_status")
            ),
            "option_context_provider_status": _provider_status(
                _pick(raw, "option_context_provider_status", "active_option_context_provider_status")
            ),
            "execution_provider_status": _provider_status(
                _pick(raw, "execution_provider_status", "active_execution_provider_status")
            ),
            "raw": dict(raw),
        }

    def _shared_core(
        self,
        *,
        generated_at_ns: int,
        provider_runtime: Mapping[str, Any],
        dhan_context: Mapping[str, Any],
        active_frame: SnapshotFrameView | None,
        dhan_frame: SnapshotFrameView | None,
    ) -> dict[str, Any]:
        active_futures = dict(active_frame.futures) if active_frame else {}
        active_selected = dict(active_frame.selected_option) if active_frame else {}
        dhan_futures = dict(dhan_frame.futures) if dhan_frame else {}
        dhan_selected = dict(dhan_frame.selected_option) if dhan_frame else {}

        fut_active = self._futures_surface(
            active_futures,
            role="active",
            provider_id=_safe_str(provider_runtime["active_futures_provider_id"]),
        )
        fut_dhan = self._futures_surface(
            dhan_futures,
            role="dhan",
            provider_id=PROVIDER_DHAN,
        )
        opt_active = self._option_surface(
            active_selected,
            role="active_selected",
            provider_id=_safe_str(provider_runtime["active_selected_option_provider_id"]),
        )
        opt_dhan = self._option_surface(
            dhan_selected,
            role="dhan_selected",
            provider_id=PROVIDER_DHAN,
        )

        call_opt, put_opt = self._split_options(opt_active, opt_dhan, dhan_context)
        strike_context = self._strike_context(
            dhan_context=dhan_context,
            futures=fut_active,
            selected=opt_active,
            call=call_opt,
            put=put_opt,
        )
        cross_option = self._cross_option(call_opt, put_opt, opt_active, strike_context)
        regime = self._regime_surface(fut_active, cross_option)
        runtime_modes = self._runtime_modes(provider_runtime, dhan_context, fut_dhan, opt_dhan)
        tradability = self._tradability(fut_active, call_opt, put_opt, regime)
        snapshot = self._snapshot_block(generated_at_ns, active_frame, dhan_frame)

        return {
            "generated_at_ns": generated_at_ns,
            "snapshot": snapshot,
            "provider_runtime": dict(provider_runtime),
            "futures": {
                "active": fut_active,
                "dhan": fut_dhan,
                "cross": self._cross_futures(fut_active, fut_dhan),
            },
            "options": {
                "selected": opt_active,
                "dhan_selected": opt_dhan,
                "call": call_opt,
                "put": put_opt,
                "cross_option": cross_option,
            },
            "strike_selection": strike_context,
            "oi_wall_context": strike_context.get("oi_wall_context", {}),
            "regime": regime,
            "runtime_modes": runtime_modes,
            "tradability": tradability,
            "dhan_context": dict(dhan_context),
        }

    def _futures_surface(
        self,
        raw: Mapping[str, Any],
        *,
        role: str,
        provider_id: str,
    ) -> dict[str, Any]:
        built = _call_first(
            self.shared_modules.get("futures_core"),
            ("build_futures_surface", "build_active_futures_surface", "build_dhan_futures_surface"),
            raw,
            role=role,
            provider_id=provider_id,
        )
        if isinstance(built, Mapping):
            out = dict(built)
            out.setdefault("role", role)
            out.setdefault("provider_id", provider_id)
            return out

        bid = _safe_float(_pick(raw, "bid", "best_bid"), 0.0)
        ask = _safe_float(_pick(raw, "ask", "best_ask"), 0.0)
        ltp = _safe_float(_pick(raw, "ltp", "last_price", "price"), 0.0)
        bid_qty = _safe_float(_pick(raw, "bid_qty", "best_bid_qty", "top5_bid_qty"), 0.0)
        ask_qty = _safe_float(_pick(raw, "ask_qty", "best_ask_qty", "top5_ask_qty"), 0.0)

        spread = max(0.0, ask - bid) if bid > 0 and ask > 0 else 0.0
        mid = (bid + ask) / 2.0 if bid > 0 and ask > 0 else ltp
        depth_total = bid_qty + ask_qty
        ofi = _ratio(bid_qty - ask_qty, bid_qty + ask_qty, 0.0)
        vwap = _safe_float(_pick(raw, "vwap"), ltp)

        return {
            "present": ltp > 0.0,
            "valid": ltp > 0.0,
            "role": role,
            "provider_id": provider_id,
            "instrument_key": _safe_str(_pick(raw, "instrument_key"), getattr(N, "IK_MME_FUT", "")),
            "instrument_token": _safe_str(_pick(raw, "instrument_token")),
            "trading_symbol": _safe_str(_pick(raw, "trading_symbol", "symbol")),
            "ltp": ltp,
            "bid": bid,
            "ask": ask,
            "best_bid": bid,
            "best_ask": ask,
            "spread": spread,
            "spread_ratio": _safe_float(
                _pick(raw, "spread_ratio"),
                _ratio(spread, max(mid * 0.0001, 0.05), 999.0),
            ),
            "depth_total": depth_total,
            "depth_ok": depth_total >= DEFAULT_DEPTH_MIN,
            "top5_bid_qty": bid_qty,
            "top5_ask_qty": ask_qty,
            "bid_qty": bid_qty,
            "ask_qty": ask_qty,
            "ofi_ratio_proxy": ofi,
            "ofi_persist_score": _safe_float(
                _pick(raw, "ofi_persist_score", "weighted_ofi_persist"),
                ofi,
            ),
            "weighted_ofi": _clamp(0.5 + ofi / 2.0, 0.0, 1.0),
            "weighted_ofi_persist": _clamp(0.5 + ofi / 2.0, 0.0, 1.0),
            "nof": ofi,
            "nof_slope": _safe_float(_pick(raw, "nof_slope"), 0.0),
            "delta_3": _safe_float(_pick(raw, "delta_3", "ltp_delta_3"), 0.0),
            "vel_ratio": _safe_float(_pick(raw, "vel_ratio", "velocity_ratio"), 1.0),
            "velocity_ratio": _safe_float(_pick(raw, "velocity_ratio", "vel_ratio"), 1.0),
            "vol_norm": _safe_float(_pick(raw, "vol_norm", "volume_norm"), 1.0),
            "vwap": vwap,
            "vwap_distance": ltp - vwap if ltp > 0 and vwap > 0 else 0.0,
            "vwap_dist_pct": _ratio(ltp - vwap, vwap, 0.0) if ltp > 0 and vwap > 0 else 0.0,
            "above_vwap": bool(ltp > vwap) if ltp > 0 and vwap > 0 else False,
            "below_vwap": bool(ltp < vwap) if ltp > 0 and vwap > 0 else False,
            "ts_event_ns": _safe_int(_pick(raw, "ts_event_ns", "event_ts_ns"), 0) or None,
            "age_ms": _safe_int(_pick(raw, "age_ms"), 0) or None,
        }

    def _option_surface(
        self,
        raw: Mapping[str, Any],
        *,
        role: str,
        provider_id: str,
    ) -> dict[str, Any]:
        built = _call_first(
            self.shared_modules.get("option_core"),
            ("build_option_surface", "build_selected_option_surface", "build_dhan_selected_option_surface"),
            raw,
            role=role,
            provider_id=provider_id,
        )
        if isinstance(built, Mapping):
            out = dict(built)
            out.setdefault("role", role)
            out.setdefault("provider_id", provider_id)
            out.setdefault("side", _normalize_side(out.get("side") or out.get("option_side")))
            return out

        bid = _safe_float(_pick(raw, "bid", "best_bid"), 0.0)
        ask = _safe_float(_pick(raw, "ask", "best_ask"), 0.0)
        ltp = _safe_float(_pick(raw, "ltp", "last_price", "price"), 0.0)
        bid_qty = _safe_float(_pick(raw, "bid_qty", "best_bid_qty", "top5_bid_qty"), 0.0)
        ask_qty = _safe_float(_pick(raw, "ask_qty", "best_ask_qty", "top5_ask_qty"), 0.0)
        spread = max(0.0, ask - bid) if bid > 0 and ask > 0 else 0.0
        mid = (bid + ask) / 2.0 if bid > 0 and ask > 0 else ltp
        depth_total = bid_qty + ask_qty
        side = _normalize_side(_pick(raw, "side", "option_side", "right"))
        ofi = _ratio(bid_qty - ask_qty, bid_qty + ask_qty, 0.0)

        return {
            "present": ltp > 0.0 and side is not None,
            "valid": ltp > 0.0 and side is not None,
            "role": role,
            "provider_id": provider_id,
            "instrument_key": _safe_str(_pick(raw, "instrument_key")),
            "instrument_token": _safe_str(_pick(raw, "instrument_token")),
            "trading_symbol": _safe_str(_pick(raw, "trading_symbol", "symbol")),
            "symbol": _safe_str(_pick(raw, "symbol", "trading_symbol")),
            "side": side,
            "option_side": side,
            "strike": _safe_float_or_none(_pick(raw, "strike", "strike_price")),
            "entry_mode": _safe_str(_pick(raw, "entry_mode"), getattr(N, "ENTRY_MODE_UNKNOWN", "UNKNOWN")),
            "ltp": ltp,
            "bid": bid,
            "ask": ask,
            "best_bid": bid,
            "best_ask": ask,
            "spread": spread,
            "spread_ratio": _safe_float(
                _pick(raw, "spread_ratio"),
                _ratio(spread, max(mid * 0.001, 0.05), 999.0),
            ),
            "spread_ticks": _ratio(spread, _safe_float(_pick(raw, "tick_size"), 0.05), 0.0),
            "depth_total": depth_total,
            "depth_ok": depth_total >= DEFAULT_DEPTH_MIN,
            "top5_bid_qty": bid_qty,
            "top5_ask_qty": ask_qty,
            "bid_qty": bid_qty,
            "ask_qty": ask_qty,
            "ofi_ratio_proxy": ofi,
            "weighted_ofi": _clamp(0.5 + ofi / 2.0, 0.0, 1.0),
            "weighted_ofi_persist": _clamp(0.5 + ofi / 2.0, 0.0, 1.0),
            "delta_3": _safe_float(_pick(raw, "delta_3", "ltp_delta_3"), 0.0),
            "nof_slope": _safe_float(_pick(raw, "nof_slope"), 0.0),
            "velocity_ratio": _safe_float(_pick(raw, "velocity_ratio", "vel_ratio"), 1.0),
            "response_efficiency": _safe_float(_pick(raw, "response_efficiency", "response_eff"), 0.0),
            "tradability_ok": bool(ltp >= DEFAULT_PREMIUM_FLOOR and depth_total >= DEFAULT_DEPTH_MIN),
            "impact_fraction": _safe_float(_pick(raw, "impact_fraction"), 0.0),
            "tick_size": _safe_float(_pick(raw, "tick_size"), 0.05),
            "lot_size": _safe_int(_pick(raw, "lot_size"), 0) or None,
            "oi": _safe_float(_pick(raw, "oi", "open_interest"), 0.0),
            "volume": _safe_float(_pick(raw, "volume"), 0.0),
            "iv": _safe_float_or_none(_pick(raw, "iv", "implied_volatility")),
            "context_score": _safe_float(_pick(raw, "context_score"), 0.0),
            "ask_reloaded": _safe_bool(_pick(raw, "ask_reloaded"), False),
            "bid_reloaded": _safe_bool(_pick(raw, "bid_reloaded"), False),
            "ts_event_ns": _safe_int(_pick(raw, "ts_event_ns", "event_ts_ns"), 0) or None,
            "age_ms": _safe_int(_pick(raw, "age_ms"), 0) or None,
        }

    def _blank_option(self, side: str) -> dict[str, Any]:
        return {
            "present": False,
            "valid": False,
            "side": side,
            "option_side": side,
            "instrument_key": "",
            "instrument_token": "",
            "trading_symbol": "",
            "strike": None,
            "ltp": None,
            "bid": None,
            "ask": None,
            "spread": None,
            "spread_ratio": None,
            "depth_total": None,
            "depth_ok": False,
            "response_efficiency": None,
            "tradability_ok": False,
            "delta_3": None,
            "oi": None,
            "volume": None,
            "tick_size": 0.05,
        }

    def _split_options(
        self,
        active: Mapping[str, Any],
        dhan_selected: Mapping[str, Any],
        dhan_context: Mapping[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        call = self._blank_option(SIDE_CALL)
        put = self._blank_option(SIDE_PUT)

        candidates = (
            dhan_selected,
            active,
            self._context_option(dhan_context, SIDE_CALL),
            self._context_option(dhan_context, SIDE_PUT),
        )
        for option in candidates:
            side = _normalize_side(_pick(option, "side", "option_side"))
            present = _safe_bool(option.get("present"), False) or _safe_float(option.get("ltp"), 0.0) > 0.0
            if side == SIDE_CALL and present:
                call.update({k: v for k, v in dict(option).items() if v not in (None, "")})
                call["side"] = SIDE_CALL
                call["option_side"] = SIDE_CALL
            elif side == SIDE_PUT and present:
                put.update({k: v for k, v in dict(option).items() if v not in (None, "")})
                put["side"] = SIDE_PUT
                put["option_side"] = SIDE_PUT

        return call, put

    def _context_option(self, dhan_context: Mapping[str, Any], side: str) -> dict[str, Any]:
        keys = (
            ("selected_call", "call", "ce", "selected_ce")
            if side == SIDE_CALL
            else ("selected_put", "put", "pe", "selected_pe")
        )
        for key in keys:
            value = _mapping(dhan_context.get(key))
            if value:
                return self._option_surface(value, role=f"context_{side.lower()}", provider_id=PROVIDER_DHAN)

        rows = [row for row in self._ladder(dhan_context) if row.get("side") == side]
        if rows:
            best = max(rows, key=lambda row: _safe_float(row.get("oi"), 0.0))
            return self._option_surface(best, role=f"ladder_{side.lower()}", provider_id=PROVIDER_DHAN)

        return self._blank_option(side)

    def _ladder(self, dhan_context: Mapping[str, Any]) -> list[dict[str, Any]]:
        raw_rows = None
        for key in ("strike_ladder", "ladder", "chain", "option_chain", "records", "data"):
            parsed = _json_load(dhan_context.get(key), None)
            if isinstance(parsed, list):
                raw_rows = parsed
                break
            if isinstance(parsed, Mapping):
                for sub_key in ("data", "records", "items", "ladder", "chain"):
                    sub_parsed = _json_load(parsed.get(sub_key), None)
                    if isinstance(sub_parsed, list):
                        raw_rows = sub_parsed
                        break
            if raw_rows is not None:
                break

        rows: list[dict[str, Any]] = []
        for item in raw_rows or []:
            row = _mapping(item)
            strike = _safe_float_or_none(_pick(row, "strike", "strike_price"))
            if strike is None:
                continue

            side = _normalize_side(_pick(row, "side", "option_side", "right"))
            if side in (SIDE_CALL, SIDE_PUT):
                rows.append(self._ladder_row(row, strike, side))
                continue

            for side_value, payload in (
                (SIDE_CALL, _pick(row, "call", "ce", "CE")),
                (SIDE_PUT, _pick(row, "put", "pe", "PE")),
            ):
                child = _mapping(payload)
                if child:
                    merged = dict(row)
                    merged.update(child)
                    rows.append(self._ladder_row(merged, strike, side_value))

        rows.sort(key=lambda r: (_safe_float(r.get("strike"), 0.0), _safe_str(r.get("side"))))
        return rows

    def _ladder_row(self, row: Mapping[str, Any], strike: float, side: str) -> dict[str, Any]:
        bid = _safe_float(_pick(row, "bid", "best_bid"), 0.0)
        ask = _safe_float(_pick(row, "ask", "best_ask"), 0.0)
        return {
            "strike": strike,
            "side": side,
            "ltp": _safe_float(_pick(row, "ltp", "last_price"), 0.0),
            "bid": bid,
            "ask": ask,
            "spread": max(0.0, ask - bid) if ask > 0 and bid > 0 else 0.0,
            "spread_ratio": _safe_float(_pick(row, "spread_ratio"), 0.0),
            "oi": _safe_float(_pick(row, "oi", "open_interest"), 0.0),
            "oi_change": _safe_float(_pick(row, "oi_change", "change_oi"), 0.0),
            "volume": _safe_float(_pick(row, "volume"), 0.0),
            "iv": _safe_float_or_none(_pick(row, "iv", "implied_volatility")),
            "instrument_key": _safe_str(_pick(row, "instrument_key")),
            "instrument_token": _safe_str(_pick(row, "instrument_token")),
            "trading_symbol": _safe_str(_pick(row, "trading_symbol", "symbol")),
        }

    def _strike_context(
        self,
        *,
        dhan_context: Mapping[str, Any],
        futures: Mapping[str, Any],
        selected: Mapping[str, Any],
        call: Mapping[str, Any],
        put: Mapping[str, Any],
    ) -> dict[str, Any]:
        built = _call_first(
            self.shared_modules.get("strike_selection"),
            (
                "build_strike_selection_surface",
                "build_family_strike_selection_surface",
                "build_strike_context_surface",
            ),
            dhan_context,
            futures=futures,
            selected_option=selected,
            call_option=call,
            put_option=put,
        )
        if isinstance(built, Mapping):
            out = dict(built)
            out.setdefault("oi_wall_context", out)
            return out

        ladder = self._ladder(dhan_context)
        reference = (
            _safe_float(futures.get("ltp"), 0.0)
            or _safe_float(_pick(dhan_context, "atm_strike", "underlying_atm"), 0.0)
            or _safe_float(selected.get("strike"), 0.0)
        )
        call_wall = self._nearest_wall(ladder, SIDE_CALL, reference)
        put_wall = self._nearest_wall(ladder, SIDE_PUT, reference)

        call_strength = _safe_float(call_wall.get("wall_strength"), 0.0)
        put_strength = _safe_float(put_wall.get("wall_strength"), 0.0)
        oi_bias = _safe_str(_pick(dhan_context, "oi_bias"))
        if not oi_bias:
            if call_strength > put_strength + 0.05:
                oi_bias = "CALL_WALL_DOMINANT"
            elif put_strength > call_strength + 0.05:
                oi_bias = "PUT_WALL_DOMINANT"
            else:
                oi_bias = "NEUTRAL"

        return {
            "chain_context_ready": bool(ladder or dhan_context),
            "atm_strike": _safe_float_or_none(_pick(dhan_context, "atm_strike", "underlying_atm")),
            "selected_strike": selected.get("strike"),
            "shadow_call_strike": call.get("strike"),
            "shadow_put_strike": put.get("strike"),
            "ladder": ladder,
            "ladder_size": len(ladder),
            "nearest_call_oi_resistance": call_wall,
            "nearest_put_oi_support": put_wall,
            "nearest_call_oi_resistance_strike": call_wall.get("strike"),
            "nearest_put_oi_support_strike": put_wall.get("strike"),
            "call_wall_strength": call_strength,
            "put_wall_strength": put_strength,
            "oi_bias": oi_bias,
            "oi_wall_context": {
                "call": call_wall,
                "put": put_wall,
                "oi_bias": oi_bias,
                "law": "context_not_trigger",
            },
        }

    def _nearest_wall(
        self,
        ladder: Sequence[Mapping[str, Any]],
        side: str,
        reference: float,
    ) -> dict[str, Any]:
        rows = [dict(row) for row in ladder if row.get("side") == side]
        if not rows:
            return {
                "side": side,
                "strike": None,
                "distance_points": None,
                "distance_strikes": None,
                "wall_strength": 0.0,
                "near_wall": False,
                "strong_wall": False,
                "oi": 0.0,
            }

        if reference > 0:
            directional = [
                row
                for row in rows
                if (
                    _safe_float(row.get("strike"), 0.0) >= reference
                    if side == SIDE_CALL
                    else _safe_float(row.get("strike"), 0.0) <= reference
                )
            ]
        else:
            directional = []

        pool = directional or rows
        if reference > 0:
            best = min(
                pool,
                key=lambda row: (
                    abs(_safe_float(row.get("strike"), 0.0) - reference),
                    -_safe_float(row.get("oi"), 0.0),
                ),
            )
        else:
            best = max(pool, key=lambda row: _safe_float(row.get("oi"), 0.0))

        max_oi = max((_safe_float(row.get("oi"), 0.0) for row in rows), default=0.0)
        strikes = sorted(
            {
                _safe_float(row.get("strike"), 0.0)
                for row in rows
                if _safe_float(row.get("strike"), 0.0) > 0
            }
        )
        diffs = [b - a for a, b in zip(strikes, strikes[1:]) if b > a]
        step = min(diffs) if diffs else 50.0

        strike = _safe_float(best.get("strike"), 0.0)
        distance = abs(strike - reference) if reference > 0 else None
        distance_strikes = _ratio(float(distance), step, 0.0) if distance is not None else None
        strength = _clamp(_ratio(_safe_float(best.get("oi"), 0.0), max_oi, 0.0), 0.0, 1.0)

        return {
            "side": side,
            "strike": strike,
            "distance_points": distance,
            "distance_strikes": distance_strikes,
            "wall_strength": strength,
            "near_wall": bool(distance_strikes is not None and distance_strikes <= 1.0),
            "strong_wall": bool(strength >= 0.62),
            "oi": _safe_float(best.get("oi"), 0.0),
            "volume": _safe_float(best.get("volume"), 0.0),
        }

    def _cross_option(
        self,
        call: Mapping[str, Any],
        put: Mapping[str, Any],
        selected: Mapping[str, Any],
        strike_context: Mapping[str, Any],
    ) -> dict[str, Any]:
        built = None
        if FF_H is not None:
            built = _call_first(
                FF_H,
                ("build_cross_option_block",),
                call_features=call,
                put_features=put,
                selected_option_present=bool(
                    _safe_bool(selected.get("present"), False) or selected.get("instrument_key")
                ),
                nearest_call_oi_resistance_strike=_nested(
                    strike_context,
                    "nearest_call_oi_resistance",
                    "strike",
                ),
                nearest_put_oi_support_strike=_nested(
                    strike_context,
                    "nearest_put_oi_support",
                    "strike",
                ),
                call_wall_distance_pts=_nested(
                    strike_context,
                    "nearest_call_oi_resistance",
                    "distance_points",
                ),
                put_wall_distance_pts=_nested(
                    strike_context,
                    "nearest_put_oi_support",
                    "distance_points",
                ),
                call_wall_strength_score=_nested(
                    strike_context,
                    "nearest_call_oi_resistance",
                    "wall_strength",
                ),
                put_wall_strength_score=_nested(
                    strike_context,
                    "nearest_put_oi_support",
                    "wall_strength",
                ),
            )

        if isinstance(built, Mapping):
            out = dict(built)
        else:
            call_ltp = _safe_float(call.get("ltp"), 0.0)
            put_ltp = _safe_float(put.get("ltp"), 0.0)
            call_depth = _safe_float(call.get("depth_total"), 0.0)
            put_depth = _safe_float(put.get("depth_total"), 0.0)
            out = {
                "call_ltp": call_ltp,
                "put_ltp": put_ltp,
                "call_minus_put_ltp": call_ltp - put_ltp,
                "call_put_depth_ratio": _ratio(call_depth, put_depth, 0.0),
            }

        out.update(
            {
                "call_present": bool(call.get("present") or call.get("instrument_key")),
                "put_present": bool(put.get("present") or put.get("instrument_key")),
                "selected_option_present": bool(
                    selected.get("present") or selected.get("instrument_key")
                ),
                "nearest_call_oi_resistance_strike": _nested(
                    strike_context,
                    "nearest_call_oi_resistance",
                    "strike",
                ),
                "nearest_put_oi_support_strike": _nested(
                    strike_context,
                    "nearest_put_oi_support",
                    "strike",
                ),
                "call_wall_distance_pts": _nested(
                    strike_context,
                    "nearest_call_oi_resistance",
                    "distance_points",
                ),
                "put_wall_distance_pts": _nested(
                    strike_context,
                    "nearest_put_oi_support",
                    "distance_points",
                ),
                "call_wall_strength_score": _nested(
                    strike_context,
                    "nearest_call_oi_resistance",
                    "wall_strength",
                ),
                "put_wall_strength_score": _nested(
                    strike_context,
                    "nearest_put_oi_support",
                    "wall_strength",
                ),
                "oi_bias": strike_context.get("oi_bias"),
                "cross_option_ready": bool(
                    call.get("present")
                    or put.get("present")
                    or strike_context.get("chain_context_ready")
                ),
            }
        )
        return out

    def _cross_futures(
        self,
        active: Mapping[str, Any],
        dhan: Mapping[str, Any],
    ) -> dict[str, Any]:
        active_ltp = _safe_float(active.get("ltp"), 0.0)
        dhan_ltp = _safe_float(dhan.get("ltp"), 0.0)
        diff = active_ltp - dhan_ltp if active_ltp > 0 and dhan_ltp > 0 else 0.0
        return {
            "active_valid": bool(active.get("valid") or active.get("present")),
            "dhan_valid": bool(dhan.get("valid") or dhan.get("present")),
            "active_ltp": active_ltp,
            "dhan_ltp": dhan_ltp,
            "ltp_diff": diff,
            "providers_aligned": bool(
                active_ltp > 0 and dhan_ltp > 0 and abs(diff) <= max(1.0, active_ltp * 0.0002)
            ),
        }

    def _regime_surface(
        self,
        futures: Mapping[str, Any],
        cross_option: Mapping[str, Any],
    ) -> dict[str, Any]:
        built = _call_first(
            self.shared_modules.get("regime"),
            ("build_regime_surface", "build_regime_bundle"),
            futures_surface=futures,
            cross_option=cross_option,
        )
        if isinstance(built, Mapping):
            out = dict(built)
            out["regime"] = _regime(out.get("regime"))
            return out

        score = max(
            _safe_float(futures.get("velocity_ratio"), 1.0),
            _safe_float(futures.get("vel_ratio"), 1.0),
            _safe_float(futures.get("vol_norm"), 1.0),
        )
        if score >= 1.5:
            regime, reason = REGIME_FAST, "fast_ratio"
        elif score <= 0.8:
            regime, reason = REGIME_LOWVOL, "lowvol_ratio"
        else:
            regime, reason = REGIME_NORMAL, "normal_ratio"

        return {
            "regime": regime,
            "regime_reason": reason,
            "score": score,
        }

    def _runtime_modes(
        self,
        provider_runtime: Mapping[str, Any],
        dhan_context: Mapping[str, Any],
        dhan_futures: Mapping[str, Any],
        dhan_option: Mapping[str, Any],
    ) -> dict[str, Any]:
        classic = _classic_runtime_mode(
            _pick(
                provider_runtime,
                "classic_runtime_mode",
                "strategy_runtime_mode_classic",
                default=RUNTIME_NORMAL,
            )
        )

        depth20_ready = _safe_bool(_pick(dhan_context, "depth20_ready", "top20_ready"), False)
        dhan_ready = bool(dhan_context) or bool(dhan_futures.get("present")) or bool(dhan_option.get("present"))
        if not dhan_ready:
            miso_default = RUNTIME_DISABLED
        elif depth20_ready:
            miso_default = RUNTIME_DEPTH20
        else:
            miso_default = RUNTIME_BASE_5DEPTH

        miso = _miso_runtime_mode(
            _pick(
                provider_runtime,
                "miso_runtime_mode",
                "strategy_runtime_mode_miso",
                default=miso_default,
            )
        )

        return {
            "classic": {
                "mode": classic,
                "runtime_mode": classic,
                "provider_ready": classic != RUNTIME_DISABLED,
            },
            "miso": {
                "mode": miso,
                "runtime_mode": miso,
                "provider_ready": miso != RUNTIME_DISABLED,
                "depth20_ready": depth20_ready,
            },
        }

    def _tradability(
        self,
        futures: Mapping[str, Any],
        call: Mapping[str, Any],
        put: Mapping[str, Any],
        regime: Mapping[str, Any],
    ) -> dict[str, Any]:
        built_futures = _call_first(
            self.shared_modules.get("tradability"),
            ("build_futures_liquidity_surface",),
            futures,
            regime_surface=regime,
        )
        futures_liq = (
            dict(built_futures)
            if isinstance(built_futures, Mapping)
            else {
                "liquidity_pass": bool(futures.get("depth_ok")),
                "spread_ratio": futures.get("spread_ratio"),
                "depth_total": futures.get("depth_total"),
            }
        )

        return {
            "futures": futures_liq,
            "classic_call": self._option_tradability(call, side=SIDE_CALL),
            "classic_put": self._option_tradability(put, side=SIDE_PUT),
            "miso_call": self._option_tradability(call, side=SIDE_CALL),
            "miso_put": self._option_tradability(put, side=SIDE_PUT),
        }

    def _option_tradability(self, option: Mapping[str, Any], *, side: str) -> dict[str, Any]:
        premium = _safe_float(option.get("ltp"), 0.0)
        spread_ratio = _safe_float(option.get("spread_ratio"), 999.0)
        depth_total = _safe_int(option.get("depth_total"), 0)
        response_eff = _safe_float(option.get("response_efficiency"), 0.0)
        bid = _safe_float(option.get("bid"), 0.0)
        ask = _safe_float(option.get("ask"), 0.0)
        crossed = bid > 0 and ask > 0 and bid > ask

        ok = bool(
            premium >= DEFAULT_PREMIUM_FLOOR
            and spread_ratio <= DEFAULT_SPREAD_RATIO_MAX
            and depth_total >= DEFAULT_DEPTH_MIN
            and response_eff >= DEFAULT_RESPONSE_EFF_MIN
            and not crossed
        )

        reason = (
            ""
            if ok
            else "premium_floor"
            if premium < DEFAULT_PREMIUM_FLOOR
            else "spread"
            if spread_ratio > DEFAULT_SPREAD_RATIO_MAX
            else "depth"
            if depth_total < DEFAULT_DEPTH_MIN
            else "response_efficiency"
            if response_eff < DEFAULT_RESPONSE_EFF_MIN
            else "crossed_book"
            if crossed
            else "unknown"
        )

        return {
            "side": side,
            "entry_pass": ok,
            "tradability_ok": ok,
            "blocked_reason": reason,
            "premium_floor_ok": premium >= DEFAULT_PREMIUM_FLOOR,
            "spread_ratio_ok": spread_ratio <= DEFAULT_SPREAD_RATIO_MAX,
            "depth_ok": depth_total >= DEFAULT_DEPTH_MIN,
            "response_efficiency_ok": response_eff >= DEFAULT_RESPONSE_EFF_MIN,
            "spread_ratio": spread_ratio,
            "depth_total": depth_total,
            "response_efficiency": response_eff,
        }

    def _snapshot_block(
        self,
        generated_at_ns: int,
        active_frame: SnapshotFrameView | None,
        dhan_frame: SnapshotFrameView | None,
    ) -> dict[str, Any]:
        active_ts = active_frame.ts_event_ns if active_frame else None
        dhan_ts = dhan_frame.ts_event_ns if dhan_frame else None
        skew_ms = int(abs(active_ts - dhan_ts) / 1_000_000) if active_ts and dhan_ts else None
        valid = bool(active_frame and active_frame.valid)
        samples_seen = max(1, int(bool(active_frame)) + int(bool(dhan_frame)))

        return {
            "valid": valid,
            "validity": "VALID" if valid else "INVALID",
            "sync_ok": bool(skew_ms is None or skew_ms <= DEFAULT_SYNC_MAX_MS),
            "freshness_ok": True,
            "packet_gap_ok": True,
            "warmup_ok": True,
            "active_snapshot_ns": active_ts or generated_at_ns,
            "futures_snapshot_ns": active_ts or generated_at_ns,
            "selected_option_snapshot_ns": active_ts or generated_at_ns,
            "dhan_futures_snapshot_ns": dhan_ts,
            "dhan_option_snapshot_ns": dhan_ts,
            "max_member_age_ms": 0,
            "fut_opt_skew_ms": skew_ms,
            "hard_packet_gap_ms": DEFAULT_PACKET_GAP_MS,
            "samples_seen": samples_seen,
        }

    def _family_surfaces(
        self,
        *,
        generated_at_ns: int,
        provider_runtime: Mapping[str, Any],
        shared_core: Mapping[str, Any],
    ) -> dict[str, Any]:
        families: dict[str, dict[str, Any]] = {}
        surfaces_by_branch: dict[str, dict[str, Any]] = {}

        for family_id in FAMILY_IDS:
            module = self.family_modules.get(family_id)
            branches: dict[str, dict[str, Any]] = {}

            for branch_id in BRANCH_IDS:
                surface = self._family_branch_surface(family_id, branch_id, module, shared_core)
                branches[branch_id] = surface
                surfaces_by_branch[f"{family_id.lower()}_{branch_id.lower()}"] = surface

            families[family_id] = self._family_surface(family_id, module, branches, shared_core)

        return {
            "schema_version": getattr(N, "DEFAULT_SCHEMA_VERSION", 1),
            "surface_version": "family_surfaces.v1",
            "service": SERVICE_FEATURES,
            "generated_at_ns": generated_at_ns,
            "provider_runtime": dict(provider_runtime),
            "shared_core": shared_core,
            "families": families,
            "surfaces_by_branch": surfaces_by_branch,
            "contract_note": "rich feature support only; family_features remains contracts.py exact-key payload",
        }

    def _family_branch_surface(
        self,
        family_id: str,
        branch_id: str,
        module: Any | None,
        shared_core: Mapping[str, Any],
    ) -> dict[str, Any]:
        side = _branch_side(branch_id)
        option = dict(_nested(shared_core, "options", "call" if branch_id == BRANCH_CALL else "put", default={}))
        futures = dict(_nested(shared_core, "futures", "active", default={}))
        regime = dict(_nested(shared_core, "regime", default={}))
        trad_key = ("miso" if family_id == FAMILY_MISO else "classic") + "_" + (
            "call" if branch_id == BRANCH_CALL else "put"
        )
        tradability = dict(_nested(shared_core, "tradability", trad_key, default={}))
        strike = dict(_nested(shared_core, "strike_selection", default={}))
        runtime_mode = _nested(
            shared_core,
            "runtime_modes",
            "miso" if family_id == FAMILY_MISO else "classic",
            "mode",
            default=RUNTIME_DISABLED,
        )

        family_lc = family_id.lower()
        built = _call_first(
            module,
            (
                f"build_{family_lc}_branch_surface",
                f"build_{family_lc}_side_surface",
                "build_branch_surface",
                "build_side_surface",
            ),
            branch_id=branch_id,
            side=side,
            runtime_mode=runtime_mode,
            futures_surface=futures,
            option_surface=option,
            selected_surface=option,
            selected_features=option,
            tradability_surface=tradability,
            regime_surface=regime,
            strike_context=strike,
            cross_option_context=_nested(shared_core, "options", "cross_option", default={}),
            shared_core=shared_core,
        )

        surface = dict(built) if isinstance(built, Mapping) else {}
        surface.update(
            {
                "surface_kind": surface.get("surface_kind") or f"{family_lc}_branch",
                "family_id": family_id,
                "branch_id": branch_id,
                "side": side,
                "runtime_mode": surface.get("runtime_mode") or runtime_mode,
                "present": bool(surface.get("present") or option.get("present") or option.get("instrument_key")),
                "eligible": bool(
                    surface.get("eligible")
                    or surface.get("ready")
                    or tradability.get("entry_pass")
                    or tradability.get("tradability_ok")
                ),
                "futures_features": surface.get("futures_features") or futures,
                "selected_features": surface.get("selected_features") or option,
                "option_features": surface.get("option_features") or option,
                "tradability": surface.get("tradability") or tradability,
                "regime_surface": surface.get("regime_surface") or regime,
                "oi_wall_context": surface.get("oi_wall_context")
                or _nested(shared_core, "oi_wall_context", "call" if side == SIDE_CALL else "put", default={}),
                "cross_option_context": surface.get("cross_option_context")
                or _nested(shared_core, "options", "cross_option", default={}),
                "context_pass": bool(surface.get("context_pass", True)),
                "option_tradability_pass": bool(
                    surface.get("option_tradability_pass")
                    or tradability.get("entry_pass")
                    or tradability.get("tradability_ok")
                ),
            }
        )
        return surface

    def _family_surface(
        self,
        family_id: str,
        module: Any | None,
        branches: Mapping[str, Mapping[str, Any]],
        shared_core: Mapping[str, Any],
    ) -> dict[str, Any]:
        family_lc = family_id.lower()
        call_surface = dict(branches.get(BRANCH_CALL, {}))
        put_surface = dict(branches.get(BRANCH_PUT, {}))

        built = _call_first(
            module,
            (f"build_{family_lc}_family_surface", "build_family_surface"),
            call_surface=call_surface,
            put_surface=put_surface,
            call_support=call_surface,
            put_support=put_surface,
            runtime_mode_surface=_nested(
                shared_core,
                "runtime_modes",
                "miso" if family_id == FAMILY_MISO else "classic",
                default={},
            ),
            regime_surface=_nested(shared_core, "regime", default={}),
            shared_core=shared_core,
        )

        surface = dict(built) if isinstance(built, Mapping) else {}
        surface.setdefault("family_id", family_id)
        surface.setdefault("eligible", bool(call_surface.get("eligible") or put_surface.get("eligible")))
        surface.setdefault("branches", {BRANCH_CALL: call_surface, BRANCH_PUT: put_surface})

        if family_id == FAMILY_MISO:
            surface.setdefault(
                "mode",
                _nested(shared_core, "runtime_modes", "miso", "mode", default=RUNTIME_DISABLED),
            )
            surface.setdefault(
                "chain_context_ready",
                bool(_nested(shared_core, "strike_selection", "chain_context_ready", default=False)),
            )
            surface.setdefault(
                "selected_side",
                _nested(shared_core, "options", "selected", "side", default=None),
            )
            surface.setdefault(
                "selected_strike",
                _nested(shared_core, "options", "selected", "strike", default=None),
            )
            surface.setdefault(
                "shadow_call_strike",
                _nested(shared_core, "strike_selection", "shadow_call_strike", default=None),
            )
            surface.setdefault(
                "shadow_put_strike",
                _nested(shared_core, "strike_selection", "shadow_put_strike", default=None),
            )
            surface.setdefault("call_support", call_surface)
            surface.setdefault("put_support", put_surface)

        return surface

    def _family_features(
        self,
        *,
        generated_at_ns: int,
        provider_runtime: Mapping[str, Any],
        shared_core: Mapping[str, Any],
        family_surfaces: Mapping[str, Any],
    ) -> dict[str, Any]:
        snapshot = self._contract_snapshot(shared_core)
        provider = self._contract_provider(provider_runtime, shared_core)
        market = self._contract_market(shared_core)
        common = self._contract_common(shared_core, provider)
        stage_flags = self._contract_stage_flags(shared_core, provider, common)
        families = self._contract_families(family_surfaces, shared_core)

        if FF_H is not None and callable(getattr(FF_H, "build_family_features_payload", None)):
            try:
                payload = FF_H.build_family_features_payload(
                    snapshot=snapshot,
                    provider_runtime=provider,
                    market=market,
                    common=common,
                    stage_flags=stage_flags,
                    families=families,
                    generated_at_ns=generated_at_ns,
                    service=SERVICE_FEATURES,
                    family_features_version=getattr(FF_C, "FAMILY_FEATURES_VERSION", "1"),
                )
                FF_C.validate_family_features_payload(payload)
                return dict(payload)
            except Exception as exc:
                self.log.warning("common_family_features_builder_rejected error=%s", exc)

        payload = _empty_builder("build_empty_family_features_payload")
        _patch_existing(
            payload,
            {
                "schema_version": getattr(N, "DEFAULT_SCHEMA_VERSION", 1),
                "service": SERVICE_FEATURES,
                "family_features_version": getattr(
                    FF_C,
                    "FAMILY_FEATURES_VERSION",
                    payload.get("family_features_version"),
                ),
                "generated_at_ns": generated_at_ns,
                "snapshot": snapshot,
                "provider_runtime": provider,
                "market": market,
                "common": common,
                "stage_flags": stage_flags,
                "families": families,
            },
        )
        FF_C.validate_family_features_payload(payload)
        return payload

    def _contract_snapshot(self, shared_core: Mapping[str, Any]) -> dict[str, Any]:
        block = _empty_builder("build_empty_snapshot_block")
        _patch_existing(block, dict(_nested(shared_core, "snapshot", default={})))
        if "samples_seen" in block:
            block["samples_seen"] = max(_safe_int(block.get("samples_seen"), 1), 1)
        return block

    def _contract_provider(
        self,
        provider_runtime: Mapping[str, Any],
        shared_core: Mapping[str, Any],
    ) -> dict[str, Any]:
        """
        Build the strict provider_runtime block for family_features.

        This is intentionally a narrow contract-seam adapter.

        It preserves the canonical provider-aware runtime fields used by the
        live system, while defensively filling any legacy / transitional typo
        keys already declared by feature_family.contracts.

        Important:
        - Do not add feed-stream behavior here.
        - Do not perform provider failover here.
        - Do not embed strategy logic here.
        - Only patch keys that already exist in the contract block.
        """
        block = _empty_builder("build_empty_provider_runtime_block")

        classic_mode = _classic_runtime_mode(
            _nested(
                shared_core,
                "runtime_modes",
                "classic",
                "mode",
                default=RUNTIME_NORMAL,
            )
        )
        miso_mode = _miso_runtime_mode(
            _nested(
                shared_core,
                "runtime_modes",
                "miso",
                "mode",
                default=RUNTIME_BASE_5DEPTH,
            )
        )

        active_futures_provider_id = _provider_id(
            _pick(
                provider_runtime,
                "active_futures_provider_id",
                "active_future_provider_id",
                "futures_provider_id",
            ),
            PROVIDER_DHAN,
        )
        active_selected_option_provider_id = _provider_id(
            _pick(
                provider_runtime,
                "active_selected_option_provider_id",
                "selected_option_provider_id",
                "option_provider_id",
            ),
            active_futures_provider_id,
        )
        active_option_context_provider_id = _provider_id(
            _pick(
                provider_runtime,
                "active_option_context_provider_id",
                "option_context_provider_id",
                "context_provider_id",
            ),
            PROVIDER_DHAN,
        )
        active_execution_provider_id = _provider_id(
            _pick(
                provider_runtime,
                "active_execution_provider_id",
                "execution_primary_provider_id",
                "execution_provider_id",
            ),
            PROVIDER_ZERODHA,
        )
        fallback_execution_provider_id = _provider_id(
            _pick(
                provider_runtime,
                "fallback_execution_provider_id",
                "execution_fallback_provider_id",
            ),
            PROVIDER_DHAN,
        )

        futures_provider_status = _provider_status(
            _pick(
                provider_runtime,
                "futures_provider_status",
                "active_futures_provider_status",
                # Transitional typo compatibility.
                "futures_provider_statu",
                "active_futures_provider_statu",
            )
        )
        selected_option_provider_status = _provider_status(
            _pick(
                provider_runtime,
                "selected_option_provider_status",
                "active_selected_option_provider_status",
                "selected_option_provider_statu",
                "active_selected_option_provider_statu",
            )
        )
        option_context_provider_status = _provider_status(
            _pick(
                provider_runtime,
                "option_context_provider_status",
                "active_option_context_provider_status",
                "option_context_provider_statu",
                "active_option_context_provider_statu",
            )
        )
        execution_provider_status = _provider_status(
            _pick(
                provider_runtime,
                "execution_provider_status",
                "active_execution_provider_status",
                "execution_provider_statu",
                "active_execution_provider_statu",
            )
        )

        values: dict[str, Any] = {
            "active_futures_provider_id": active_futures_provider_id,
            "active_selected_option_provider_id": active_selected_option_provider_id,
            "active_option_context_provider_id": active_option_context_provider_id,
            "active_execution_provider_id": active_execution_provider_id,
            "execution_primary_provider_id": active_execution_provider_id,
            "fallback_execution_provider_id": fallback_execution_provider_id,
            "execution_fallback_provider_id": fallback_execution_provider_id,
            "provider_runtime_mode": _safe_str(
                _pick(provider_runtime, "provider_runtime_mode", "runtime_mode"),
                "NORMAL",
            ),
            "family_runtime_mode": _family_runtime_mode(
                provider_runtime.get("family_runtime_mode")
            ),
            "classic_runtime_mode": classic_mode,
            "miso_runtime_mode": miso_mode,
            "futures_provider_status": futures_provider_status,
            "selected_option_provider_status": selected_option_provider_status,
            "option_context_provider_status": option_context_provider_status,
            "execution_provider_status": execution_provider_status,
            "provider_ready_classic": classic_mode != RUNTIME_DISABLED,
            "provider_ready_miso": miso_mode != RUNTIME_DISABLED,

            # Defensive compatibility for any transitional typo keys that may
            # still exist in feature_family.contracts. _patch_existing only
            # writes these when the contract block already declares them.
            "futures_provider_statu": futures_provider_status,
            "selected_option_provider_statu": selected_option_provider_status,
            "option_context_provider_statu": option_context_provider_status,
            "execution_provider_statu": execution_provider_status,
        }

        _patch_existing(block, values)

        # Final guard: every provider status-like field declared by the contract
        # must be a string. This prevents live publish rejection such as:
        # provider_runtime.futures_provider_statu must be str
        default_status = _provider_status(None)
        for key in tuple(block.keys()):
            if key.endswith("_provider_status") or key.endswith("_provider_statu"):
                block[key] = _safe_str(block.get(key), default_status)

        return block

    def _contract_market(self, shared_core: Mapping[str, Any]) -> dict[str, Any]:
        block = _empty_builder("build_empty_market_block")
        futures = dict(_nested(shared_core, "futures", "active", default={}))
        call = dict(_nested(shared_core, "options", "call", default={}))
        put = dict(_nested(shared_core, "options", "put", default={}))
        selected = dict(_nested(shared_core, "options", "selected", default={}))
        strike = dict(_nested(shared_core, "strike_selection", default={}))

        _patch_existing(
            block,
            {
                "atm_strike": strike.get("atm_strike"),
                "selected_call_strike": call.get("strike"),
                "selected_put_strike": put.get("strike"),
                "active_branch_hint": _side_branch(_normalize_side(selected.get("side"))),
                "futures_ltp": futures.get("ltp"),
                "call_ltp": call.get("ltp"),
                "put_ltp": put.get("ltp"),
                "selected_option_ltp": selected.get("ltp"),
                "premium_floor_ok": _safe_float(selected.get("ltp"), 0.0) >= DEFAULT_PREMIUM_FLOOR,
            },
        )
        return block

    def _contract_common(
        self,
        shared_core: Mapping[str, Any],
        provider: Mapping[str, Any],
    ) -> dict[str, Any]:
        block = _empty_builder("build_empty_common_block")

        futures = self._contract_futures_block(
            _nested(shared_core, "futures", "active", default={})
        )
        call = self._contract_option_block(
            _nested(shared_core, "options", "call", default={}),
            SIDE_CALL,
            _nested(shared_core, "tradability", "classic_call", default={}),
        )
        put = self._contract_option_block(
            _nested(shared_core, "options", "put", default={}),
            SIDE_PUT,
            _nested(shared_core, "tradability", "classic_put", default={}),
        )

        selected_raw = _nested(shared_core, "options", "selected", default={})
        selected_side = _normalize_side(_pick(selected_raw, "side", "option_side")) or SIDE_CALL
        selected_trad = _nested(
            shared_core,
            "tradability",
            "classic_call" if selected_side == SIDE_CALL else "classic_put",
            default={},
        )
        selected = self._contract_selected_option_block(
            selected_raw,
            selected_side,
            selected_trad,
        )
        cross_option = self._contract_cross_option_block(
            _nested(shared_core, "options", "cross_option", default={})
        )
        economics = self._contract_economics_block(selected)
        signals = self._contract_signals_block(shared_core)
        regime = _regime(_nested(shared_core, "regime", "regime", default=REGIME_NORMAL))

        _patch_existing(
            block,
            {
                "futures": futures,
                "futures_features": futures,
                "call": call,
                "selected_call": call,
                "put": put,
                "selected_put": put,
                "selected_option": selected,
                "cross_option": cross_option,
                "economics": economics,
                "signals": signals,
                "regime": regime,
                "regime_reason": _safe_str(
                    _nested(shared_core, "regime", "regime_reason", default="")
                )
                or None,
                "family_runtime_mode": provider.get("family_runtime_mode"),
                "classic_runtime_mode": provider.get("classic_runtime_mode"),
                "miso_runtime_mode": provider.get("miso_runtime_mode"),
                "strategy_runtime_mode_classic": provider.get("classic_runtime_mode"),
                "strategy_runtime_mode_miso": provider.get("miso_runtime_mode"),
                "snapshot": _nested(shared_core, "snapshot", default={}),
                "provider_runtime": provider,
            },
        )
        return block

    def _contract_futures_block(self, surface: Mapping[str, Any]) -> dict[str, Any]:
        block = _empty_builder("build_empty_common_futures_block")
        _patch_existing(
            block,
            {
                "ltp": surface.get("ltp"),
                "spread": surface.get("spread"),
                "spread_ratio": surface.get("spread_ratio"),
                "depth_total": surface.get("depth_total"),
                "depth_ok": bool(surface.get("depth_ok")),
                "top5_bid_qty": surface.get("top5_bid_qty") or surface.get("bid_qty"),
                "top5_ask_qty": surface.get("top5_ask_qty") or surface.get("ask_qty"),
                "ofi_ratio_proxy": surface.get("ofi_ratio_proxy") or surface.get("nof"),
                "ofi_persist_score": surface.get("ofi_persist_score")
                or surface.get("weighted_ofi_persist"),
                "weighted_ofi_persist": surface.get("weighted_ofi_persist"),
                "delta_3": surface.get("delta_3"),
                "nof_slope": surface.get("nof_slope"),
                "vel_ratio": surface.get("vel_ratio") or surface.get("velocity_ratio"),
                "velocity_ratio": surface.get("velocity_ratio") or surface.get("vel_ratio"),
                "vol_norm": surface.get("vol_norm"),
                "vwap": surface.get("vwap"),
                "vwap_dist_pct": surface.get("vwap_dist_pct"),
                "above_vwap": surface.get("above_vwap"),
                "below_vwap": surface.get("below_vwap"),
            },
        )
        return block

    def _contract_option_block(
        self,
        surface: Mapping[str, Any],
        side: str,
        tradability: Mapping[str, Any],
    ) -> dict[str, Any]:
        block = _empty_builder("build_empty_common_option_block")
        _patch_existing(
            block,
            {
                "side": side,
                "ltp": surface.get("ltp"),
                "spread": surface.get("spread"),
                "spread_ratio": surface.get("spread_ratio"),
                "spread_ticks": surface.get("spread_ticks"),
                "depth_total": surface.get("depth_total"),
                "depth_ok": bool(surface.get("depth_ok") or tradability.get("depth_ok")),
                "top5_bid_qty": surface.get("top5_bid_qty") or surface.get("bid_qty"),
                "top5_ask_qty": surface.get("top5_ask_qty") or surface.get("ask_qty"),
                "ofi_ratio_proxy": surface.get("ofi_ratio_proxy"),
                "weighted_ofi_persist": surface.get("weighted_ofi_persist"),
                "delta_3": surface.get("delta_3"),
                "nof_slope": surface.get("nof_slope"),
                "response_efficiency": surface.get("response_efficiency"),
                "tradability_ok": bool(
                    tradability.get("entry_pass")
                    or tradability.get("tradability_ok")
                    or surface.get("tradability_ok")
                ),
                "tick_size": surface.get("tick_size"),
                "lot_size": surface.get("lot_size"),
                "strike": surface.get("strike"),
            },
        )
        return block

    def _contract_selected_option_block(
        self,
        surface: Mapping[str, Any],
        side: str,
        tradability: Mapping[str, Any],
    ) -> dict[str, Any]:
        block = _empty_builder("build_empty_selected_option_block")
        values = self._contract_option_block(surface, side, tradability)
        values.update(
            {
                "side": side,
                "selected_option_present": bool(
                    surface.get("present") or surface.get("instrument_key")
                ),
                "selected_option_tradability_ok": bool(
                    tradability.get("entry_pass") or tradability.get("tradability_ok")
                ),
            }
        )
        _patch_existing(block, values)
        return block

    def _contract_cross_option_block(self, cross: Mapping[str, Any]) -> dict[str, Any]:
        block = _empty_builder("build_empty_cross_option_block")
        _patch_existing(block, dict(cross))
        return block

    def _contract_economics_block(self, selected: Mapping[str, Any]) -> dict[str, Any]:
        block = _empty_builder("build_empty_economics_block")
        trad_ok = bool(
            selected.get("tradability_ok") or selected.get("selected_option_tradability_ok")
        )
        _patch_existing(
            block,
            {
                "premium_floor_ok": _safe_float(selected.get("ltp"), 0.0)
                >= DEFAULT_PREMIUM_FLOOR,
                "economic_viability_ok": trad_ok,
                "economics_valid": trad_ok,
                "target_points": DEFAULT_TARGET_POINTS,
                "stop_points": DEFAULT_STOP_POINTS,
            },
        )
        return block

    def _contract_signals_block(self, shared_core: Mapping[str, Any]) -> dict[str, Any]:
        block = _empty_builder("build_empty_signals_block")
        futures = _nested(shared_core, "futures", "active", default={})
        _patch_existing(
            block,
            {
                "futures_bias": _safe_float(_pick(futures, "ofi_ratio_proxy", "nof"), 0.0),
                "futures_impulse": _safe_float(
                    _pick(futures, "velocity_ratio", "vel_ratio"),
                    1.0,
                ),
                "liquidity_ok": bool(
                    _nested(shared_core, "tradability", "futures", "liquidity_pass", default=True)
                ),
                "alignment_ok": True,
                "options_confirmation": bool(
                    _nested(shared_core, "options", "cross_option", "cross_option_ready", default=False)
                ),
            },
        )
        return block

    def _contract_stage_flags(
        self,
        shared_core: Mapping[str, Any],
        provider: Mapping[str, Any],
        common: Mapping[str, Any],
    ) -> dict[str, Any]:
        block = _empty_builder("build_empty_stage_flags_block")
        snapshot = _nested(shared_core, "snapshot", default={})
        _patch_existing(
            block,
            {
                "data_valid": bool(snapshot.get("valid")),
                "data_quality_ok": bool(snapshot.get("sync_ok") and snapshot.get("packet_gap_ok")),
                "session_eligible": True,
                "warmup_complete": True,
                "risk_veto_active": False,
                "reconciliation_lock_active": False,
                "active_position_present": False,
                "provider_ready_classic": bool(provider.get("classic_runtime_mode") != RUNTIME_DISABLED),
                "provider_ready_miso": bool(provider.get("miso_runtime_mode") != RUNTIME_DISABLED),
                "dhan_context_fresh": bool(_nested(shared_core, "dhan_context", default={})),
                "selected_option_present": bool(
                    _nested(
                        common,
                        "selected_option",
                        "selected_option_present",
                        default=False,
                    )
                    or _nested(common, "selected_option", "ltp", default=None)
                ),
                "futures_present": bool(_nested(shared_core, "futures", "active", "present", default=False)),
                "call_present": bool(
                    _nested(shared_core, "options", "call", "present", default=False)
                    or _nested(shared_core, "options", "call", "instrument_key", default="")
                ),
                "put_present": bool(
                    _nested(shared_core, "options", "put", "present", default=False)
                    or _nested(shared_core, "options", "put", "instrument_key", default="")
                ),
                "provider_ready": bool(provider.get("classic_runtime_mode") != RUNTIME_DISABLED),
                "regime_ready": True,
                "cross_option_context_ready": bool(
                    _nested(shared_core, "options", "cross_option", "cross_option_ready", default=False)
                ),
                "oi_wall_context_ready": bool(
                    _nested(shared_core, "strike_selection", "chain_context_ready", default=False)
                ),
            },
        )
        return block

    def _contract_families(
        self,
        family_surfaces: Mapping[str, Any],
        shared_core: Mapping[str, Any],
    ) -> dict[str, Any]:
        families = _empty_builder("build_empty_families_block")
        rich = dict(_nested(family_surfaces, "families", default={}))

        for family_id in FAMILY_IDS:
            if family_id not in families:
                continue

            family_block = dict(families[family_id])
            rich_family = dict(_mapping(rich.get(family_id)))

            if family_id == FAMILY_MISO:
                call_surface = dict(
                    _mapping(
                        rich_family.get("call_support")
                        or _nested(rich_family, "branches", BRANCH_CALL, default={})
                    )
                )
                put_surface = dict(
                    _mapping(
                        rich_family.get("put_support")
                        or _nested(rich_family, "branches", BRANCH_PUT, default={})
                    )
                )
                _patch_existing(
                    family_block,
                    {
                        "eligible": bool(
                            rich_family.get("eligible")
                            or call_surface.get("eligible")
                            or put_surface.get("eligible")
                        ),
                        "mode": _miso_runtime_mode(
                            rich_family.get("mode")
                            or rich_family.get("runtime_mode")
                            or _nested(shared_core, "runtime_modes", "miso", "mode")
                        ),
                        "chain_context_ready": bool(
                            rich_family.get("chain_context_ready")
                            or _nested(
                                shared_core,
                                "strike_selection",
                                "chain_context_ready",
                                default=False,
                            )
                        ),
                        "selected_side": _safe_str(
                            rich_family.get("selected_side")
                            or _nested(shared_core, "options", "selected", "side", default="")
                        )
                        or None,
                        "selected_strike": rich_family.get("selected_strike")
                        or _nested(shared_core, "options", "selected", "strike", default=None),
                        "shadow_call_strike": rich_family.get("shadow_call_strike")
                        or _nested(
                            shared_core,
                            "strike_selection",
                            "shadow_call_strike",
                            default=None,
                        ),
                        "shadow_put_strike": rich_family.get("shadow_put_strike")
                        or _nested(
                            shared_core,
                            "strike_selection",
                            "shadow_put_strike",
                            default=None,
                        ),
                        "call_support": self._bool_support(
                            _empty_builder("build_empty_miso_side_support"),
                            call_surface,
                        ),
                        "put_support": self._bool_support(
                            _empty_builder("build_empty_miso_side_support"),
                            put_surface,
                        ),
                    },
                )
            elif family_id == FAMILY_MISR:
                branches = dict(family_block.get("branches", {}))
                branches[BRANCH_CALL] = self._bool_support(
                    _empty_builder("build_empty_misr_branch_support"),
                    _nested(rich_family, "branches", BRANCH_CALL, default={}),
                )
                branches[BRANCH_PUT] = self._bool_support(
                    _empty_builder("build_empty_misr_branch_support"),
                    _nested(rich_family, "branches", BRANCH_PUT, default={}),
                )
                _patch_existing(
                    family_block,
                    {
                        "eligible": bool(
                            rich_family.get("eligible")
                            or any(branches[BRANCH_CALL].values())
                            or any(branches[BRANCH_PUT].values())
                        ),
                        "active_zone": self._active_zone(
                            _nested(rich_family, "active_zone", default={})
                        ),
                        "branches": branches,
                    },
                )
            else:
                builder = {
                    FAMILY_MIST: "build_empty_mist_branch_support",
                    FAMILY_MISB: "build_empty_misb_branch_support",
                    FAMILY_MISC: "build_empty_misc_branch_support",
                }.get(family_id, "build_empty_mist_branch_support")
                branches = dict(family_block.get("branches", {}))
                branches[BRANCH_CALL] = self._bool_support(
                    _empty_builder(builder),
                    _nested(rich_family, "branches", BRANCH_CALL, default={}),
                )
                branches[BRANCH_PUT] = self._bool_support(
                    _empty_builder(builder),
                    _nested(rich_family, "branches", BRANCH_PUT, default={}),
                )
                _patch_existing(
                    family_block,
                    {
                        "eligible": bool(
                            rich_family.get("eligible")
                            or any(branches[BRANCH_CALL].values())
                            or any(branches[BRANCH_PUT].values())
                        ),
                        "branches": branches,
                    },
                )

            families[family_id] = family_block

        FF_C.validate_families_block(families)
        return families

    def _active_zone(self, rich: Mapping[str, Any]) -> dict[str, Any]:
        zone = _empty_builder("build_empty_misr_active_zone")
        _patch_existing(zone, dict(rich))
        return zone

    def _bool_support(
        self,
        template: Mapping[str, Any],
        rich: Mapping[str, Any],
    ) -> dict[str, bool]:
        out: dict[str, bool] = {
            key: bool(value) for key, value in template.items() if isinstance(value, bool)
        }
        rich_map = dict(rich)

        synonyms = {
            "trend_confirmed": ("trend_confirmed", "trend_direction_ok", "trend_ok"),
            "futures_impulse_ok": ("futures_impulse_ok", "impulse_ok", "futures_ok"),
            "pullback_detected": ("pullback_detected", "pullback_ok", "pullback_present"),
            "resume_confirmed": ("resume_confirmed", "resume_support", "resume_confirmation_ok"),
            "context_pass": ("context_pass", "oi_context_pass"),
            "option_tradability_pass": (
                "option_tradability_pass",
                "tradability_pass",
                "option_tradability_ok",
                "eligible",
            ),
            "shelf_confirmed": ("shelf_confirmed", "shelf_ok", "shelf_score_ok"),
            "breakout_triggered": ("breakout_triggered", "breakout_trigger_ok"),
            "breakout_accepted": ("breakout_accepted", "breakout_acceptance_ok"),
            "compression_detected": ("compression_detected", "compression_ok"),
            "expansion_accepted": ("expansion_accepted", "expansion_acceptance_ok"),
            "retest_valid": ("retest_valid", "retest_ok"),
            "hesitation_valid": ("hesitation_valid", "hesitation_ok"),
            "trap_detected": ("trap_detected", "fake_break_detected"),
            "fake_break_detected": ("fake_break_detected", "trap_detected"),
            "absorption_confirmed": ("absorption_confirmed", "absorption_ok"),
            "reclaim_confirmed": ("reclaim_confirmed", "reclaim_ok"),
            "range_reentry_confirmed": ("range_reentry_confirmed", "reentry_ok"),
            "flow_flip_confirmed": ("flow_flip_confirmed", "flow_flip_ok"),
            "hold_inside_range_proved": ("hold_inside_range_proved", "hold_proof_ok"),
            "no_mans_land_cleared": ("no_mans_land_cleared", "context_pass"),
            "reversal_impulse_confirmed": ("reversal_impulse_confirmed", "reversal_impulse_ok"),
            "burst_detected": ("burst_detected", "aggressive_flow", "eligible"),
            "aggression_ok": ("aggression_ok", "aggressive_flow"),
            "tape_speed_ok": ("tape_speed_ok", "tape_speed_pass"),
            "imbalance_persist_ok": ("imbalance_persist_ok", "imbalance_persistence_ok"),
            "queue_reload_blocked": ("queue_reload_blocked", "queue_reload_veto"),
            "futures_vwap_align_ok": ("futures_vwap_align_ok", "futures_vwap_alignment_ok"),
            "futures_contradiction_blocked": (
                "futures_contradiction_blocked",
                "futures_contradiction_veto",
            ),
            "tradability_pass": (
                "tradability_pass",
                "option_tradability_pass",
                "eligible",
            ),
        }

        for key in out:
            if key in rich_map:
                out[key] = _safe_bool(rich_map[key], False)
                continue
            for alias in synonyms.get(key, ()):
                if alias in rich_map:
                    out[key] = _safe_bool(rich_map[alias], False)
                    break
        return out

    def _family_frames(
        self,
        *,
        generated_at_ns: int,
        provider_runtime: Mapping[str, Any],
        shared_core: Mapping[str, Any],
        family_surfaces: Mapping[str, Any],
    ) -> dict[str, Any]:
        frames: dict[str, Any] = {}
        surfaces = dict(_nested(family_surfaces, "surfaces_by_branch", default={}))

        for family_id in FAMILY_IDS:
            for branch_id in BRANCH_IDS:
                key = f"{family_id.lower()}_{branch_id.lower()}"
                surface = dict(_mapping(surfaces.get(key)))
                option = dict(_mapping(surface.get("option_features") or surface.get("selected_features")))
                trad = dict(_mapping(surface.get("tradability")))

                frames[key] = {
                    "frame_id": f"{key}-{generated_at_ns}",
                    "frame_ts_ns": generated_at_ns,
                    "family_id": family_id,
                    "branch_id": branch_id,
                    "side": _branch_side(branch_id),
                    "runtime_mode": surface.get("runtime_mode"),
                    "family_runtime_mode": provider_runtime.get("family_runtime_mode"),
                    "active_futures_provider_id": provider_runtime.get("active_futures_provider_id"),
                    "active_selected_option_provider_id": provider_runtime.get(
                        "active_selected_option_provider_id"
                    ),
                    "active_option_context_provider_id": provider_runtime.get(
                        "active_option_context_provider_id"
                    ),
                    "instrument_key": option.get("instrument_key"),
                    "instrument_token": option.get("instrument_token"),
                    "option_symbol": option.get("trading_symbol") or option.get("symbol"),
                    "strike": option.get("strike"),
                    "option_price": option.get("ltp"),
                    "tick_size": option.get("tick_size") or 0.05,
                    "target_points": DEFAULT_TARGET_POINTS,
                    "stop_points": DEFAULT_STOP_POINTS,
                    "eligible": bool(surface.get("eligible")),
                    "tradability_ok": bool(trad.get("entry_pass") or trad.get("tradability_ok")),
                    "surface": surface,
                }

        return frames


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
        self.poll_interval_ms = DEFAULT_POLL_INTERVAL_MS
        self.heartbeat_ttl_ms = DEFAULT_HEARTBEAT_TTL_MS
        self._last_heartbeat_ns = 0

    def _now_ns(self) -> int:
        for attr in ("now_ns", "time_ns"):
            fn = getattr(self.clock, attr, None)
            if callable(fn):
                with contextlib.suppress(Exception):
                    return int(fn())
        return time.time_ns()

    def run_once(self) -> dict[str, Any]:
        cycle_start_ns = self._now_ns()
        payload = self.engine.build_payload(now_ns=cycle_start_ns)
        self.publish_payload(payload)
        return payload


    def publish_payload(self, payload: Mapping[str, Any]) -> None:
        family_features = dict(payload["family_features"])
        family_surfaces = dict(payload["family_surfaces"])
        family_frames = dict(payload["family_frames"])
        selected = _nested(family_features, "common", "selected_option", default={})

        feature_state = {
            "frame_id": payload.get("frame_id"),
            "frame_ts_ns": payload.get("frame_ts_ns"),
            "frame_valid": bool(payload.get("frame_valid")),
            "warmup_complete": bool(payload.get("warmup_complete")),
            "regime": _nested(family_features, "common", "regime", default=REGIME_NORMAL),
            "selected_option": selected,
        }

        hash_payload = {
            "frame_id": _safe_str(payload.get("frame_id")),
            "frame_ts_ns": _safe_str(payload.get("frame_ts_ns")),
            "ts_event_ns": _safe_str(payload.get("ts_event_ns")),
            "frame_valid": int(bool(payload.get("frame_valid"))),
            "warmup_complete": int(bool(payload.get("warmup_complete"))),
            "system_state": getattr(N, "STATE_SCANNING", "SCANNING")
            if payload.get("frame_valid")
            else getattr(N, "STATE_DISABLED", "DISABLED"),
            "strategy_mode": getattr(N, "STRATEGY_AUTO", "AUTO"),
            "family_features_version": _safe_str(family_features.get("family_features_version")),
            "family_features_json": _json_dump(family_features),
            "family_surfaces_json": _json_dump(family_surfaces),
            "family_frames_json": _json_dump(family_frames),
            "feature_state_json": _json_dump(feature_state),
            "payload_json": _json_dump(payload),
        }

        stream_payload = {
            "schema_version": _safe_int(payload.get("schema_version"), 1),
            "service": SERVICE_FEATURES,
            "frame_id": hash_payload["frame_id"],
            "frame_ts_ns": hash_payload["frame_ts_ns"],
            "family_features_version": hash_payload["family_features_version"],
            "family_features_json": hash_payload["family_features_json"],
            "family_surfaces_json": hash_payload["family_surfaces_json"],
        }

        self.redis.hset(HASH_FEATURES, mapping=hash_payload)
        self.redis.xadd(
            STREAM_FEATURES,
            fields=stream_payload,
            maxlen=DEFAULT_STREAM_MAXLEN,
            approximate=True,
        )

        with contextlib.suppress(Exception):
            self.redis.hset(
                HASH_BASELINES,
                mapping={
                    "frame_ts_ns": hash_payload["frame_ts_ns"],
                    "regime": _nested(family_features, "common", "regime", default=REGIME_NORMAL),
                    "family_features_version": hash_payload["family_features_version"],
                },
            )

        with contextlib.suppress(Exception):
            self.redis.hset(
                HASH_OPTION_CONFIRM,
                mapping={
                    "frame_ts_ns": hash_payload["frame_ts_ns"],
                    "selected_option_json": _json_dump(selected),
                    "cross_option_json": _json_dump(
                        _nested(family_features, "common", "cross_option", default={})
                    ),
                },
            )

    def _publish_health(self, status: str, detail: str) -> None:
        now_ns = self._now_ns()
        payload = {
            "service": SERVICE_FEATURES,
            "instance_id": self.instance_id,
            "status": status,
            "detail": detail,
            "ts_ns": now_ns,
            "ts_event_ns": now_ns,
        }
        with contextlib.suppress(Exception):
            self.redis.hset(KEY_HEALTH_FEATURES, mapping=payload)
            self.redis.pexpire(KEY_HEALTH_FEATURES, self.heartbeat_ttl_ms)
        with contextlib.suppress(Exception):
            self.redis.xadd(
                STREAM_HEALTH,
                fields=payload,
                maxlen=DEFAULT_STREAM_MAXLEN,
                approximate=True,
            )
        self._last_heartbeat_ns = _safe_int(payload["ts_ns"], self._now_ns())

    def publish_error(self, where: str, exc: BaseException) -> None:
        payload = {
            "service": SERVICE_FEATURES,
            "instance_id": self.instance_id,
            "where": where,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "ts_ns": self._now_ns(),
        }
        with contextlib.suppress(Exception):
            self.redis.xadd(
                STREAM_ERRORS,
                fields=payload,
                maxlen=DEFAULT_STREAM_MAXLEN,
                approximate=True,
            )

    def start(self) -> int:
        self.log.info("features_service_started instance_id=%s", self.instance_id)
        self._publish_health(getattr(N, "HEALTH_STATUS_WARN", "WARN"), "features_starting")

        while not self.shutdown.is_set():
            status = getattr(N, "HEALTH_STATUS_OK", "OK")
            detail = "features_ok"
            try:
                self.run_once()
            except Exception as exc:
                self.log.exception("features_loop_error")
                self.publish_error("features_loop_error", exc)
                status = getattr(N, "HEALTH_STATUS_ERROR", "ERROR")
                detail = f"loop_error:{type(exc).__name__}"

            now_ns = self._now_ns()
            if now_ns - self._last_heartbeat_ns >= 2_000_000_000:
                self._publish_health(status, detail)

            self.shutdown.wait(max(0.01, self.poll_interval_ms / 1000.0))

        self._publish_health(getattr(N, "HEALTH_STATUS_WARN", "WARN"), "features_stopping")
        self.log.info("features_service_stopped")
        return 0


FeatureService = FeaturesService


def _load_provider_runtime_state(redis_client: Any) -> Mapping[str, Any] | None:
    return SnapshotReader(redis_client).read_provider_runtime()


def _load_dhan_context_state(redis_client: Any) -> Mapping[str, Any] | None:
    return SnapshotReader(redis_client).read_dhan_context()


def _load_snapshot_state(
    redis_client: Any,
    *,
    kind: str = "active",
    dhan_context: Mapping[str, Any] | None = None,
) -> SnapshotFrameView | None:
    reader = SnapshotReader(redis_client)
    if kind.lower() == "dhan":
        return reader.read_dhan_frame(dhan_context)
    return reader.read_active_frame(dhan_context)


def run(context: Any) -> int:
    redis_runtime = getattr(context, "redis", None)
    if redis_runtime is None:
        raise RuntimeError("features requires context.redis")
    redis_client = redis_runtime.sync if hasattr(redis_runtime, "sync") else redis_runtime

    shutdown = getattr(context, "shutdown", None)
    clock = getattr(context, "clock", None)
    instance_id = _safe_str(getattr(context, "instance_id", ""), "features")

    if shutdown is None:
        raise RuntimeError("features requires context.shutdown")
    if clock is None:
        raise RuntimeError("features requires context.clock")

    return FeaturesService(
        redis_client=redis_client,
        clock=clock,
        shutdown=shutdown,
        instance_id=instance_id,
        settings=getattr(context, "settings", None),
    ).start()


__all__ = [
    "FeatureEngine",
    "FeaturePublicationError",
    "FeatureService",
    "FeaturesService",
    "SnapshotFrameView",
    "SnapshotReader",
    "_load_dhan_context_state",
    "_load_provider_runtime_state",
    "_load_snapshot_state",
    "run",
]

# =============================================================================
# Batch 7 freeze hardening: Dhan-context quality and false-readiness guards
# =============================================================================

_CONTEXT_READY_STATUS_SET: Final[set[str]] = {
    getattr(N, "PROVIDER_STATUS_HEALTHY", "HEALTHY"),
    getattr(N, "PROVIDER_STATUS_DEGRADED", "DEGRADED"),
}
_CONTEXT_BLOCKED_STATUS_SET: Final[set[str]] = {
    getattr(N, "PROVIDER_STATUS_UNAVAILABLE", "UNAVAILABLE"),
    getattr(N, "PROVIDER_STATUS_STALE", "STALE"),
    "AUTH_FAILED",
    "ERROR",
    "FAILED",
}


def _dhan_context_quality(
    dhan_context: Mapping[str, Any] | None,
    generated_at_ns: int,
) -> dict[str, Any]:
    ctx = dict(dhan_context or {})
    present = bool(ctx)
    status = _safe_str(
        _pick(
            ctx,
            "context_status",
            "option_context_provider_status",
            "provider_status",
            "status",
        ),
        getattr(N, "PROVIDER_STATUS_UNAVAILABLE", "UNAVAILABLE"),
    ).upper()

    ts_ns = _safe_int(
        _pick(
            ctx,
            "ts_event_ns",
            "event_ts_ns",
            "timestamp_ns",
            "ts_provider_ns",
            "updated_at_ns",
        ),
        0,
    )
    age_ms = None
    if ts_ns > 0 and generated_at_ns > 0:
        age_ms = max(int((int(generated_at_ns) - ts_ns) / 1_000_000), 0)

    stale_flag = _safe_bool(_pick(ctx, "stale", "context_stale"), False)
    age_fresh = age_ms is not None and age_ms <= DEFAULT_SYNC_MAX_MS * 20
    healthy = status in _CONTEXT_READY_STATUS_SET
    stale = stale_flag or status in _CONTEXT_BLOCKED_STATUS_SET or not age_fresh

    has_selected_call = bool(
        _pick(
            ctx,
            "selected_call_instrument_key",
            "selected_call_option_symbol",
            "selected_call_option_token",
            "selected_call_dhan_security_id",
        )
    )
    has_selected_put = bool(
        _pick(
            ctx,
            "selected_put_instrument_key",
            "selected_put_option_symbol",
            "selected_put_option_token",
            "selected_put_dhan_security_id",
        )
    )
    ladder = _pick(
        ctx,
        "strike_ladder",
        "strike_ladder_rows",
        "chain_rows",
        "option_chain",
        "chain",
        "rows",
    )
    has_ladder = isinstance(ladder, Sequence) and not isinstance(
        ladder,
        (str, bytes, bytearray),
    ) and len(ladder) > 0

    oi_wall = _pick(ctx, "oi_wall_context", "oi_wall", "wall_context")
    has_oi_wall = bool(oi_wall)

    fresh = bool(present and healthy and not stale)
    miso_context_ready = bool(fresh and has_ladder and (has_selected_call or has_selected_put))

    return {
        "present": present,
        "status": status,
        "fresh": fresh,
        "healthy": healthy,
        "stale": stale,
        "age_ms": age_ms,
        "has_selected_call": has_selected_call,
        "has_selected_put": has_selected_put,
        "has_ladder": has_ladder,
        "has_oi_wall": has_oi_wall,
        "miso_context_ready": miso_context_ready,
    }


def _batch7_surface_present(surface: Mapping[str, Any] | None) -> bool:
    s = dict(surface or {})
    return bool(
        _safe_bool(_pick(s, "present", "valid"), False)
        or _safe_float(_pick(s, "ltp", "last_price", "price"), 0.0) > 0.0
    )


def _batch7_provider_usable(status: Any) -> bool:
    return _safe_str(status).upper() in _CONTEXT_READY_STATUS_SET


def _batch7_frame(
    *,
    kind: str,
    futures: Mapping[str, Any],
    selected: Mapping[str, Any],
    dhan_context: Mapping[str, Any],
) -> SnapshotFrameView | None:
    if not futures and not selected and not dhan_context:
        return None

    fut_ts = _safe_int(_pick(futures, "ts_event_ns", "event_ts_ns", "timestamp_ns"), 0)
    opt_ts = _safe_int(_pick(selected, "ts_event_ns", "event_ts_ns", "timestamp_ns"), 0)
    recv_ts = max(
        _safe_int(_pick(futures, "ts_recv_ns", "recv_ts_ns"), 0),
        _safe_int(_pick(selected, "ts_recv_ns", "recv_ts_ns"), 0),
    ) or None
    ts_event = max(fut_ts, opt_ts) or None
    provider = (
        _safe_str(
            _pick(
                selected,
                "provider_id",
                default=_pick(futures, "provider_id"),
            )
        )
        or None
    )

    fut_ltp = _safe_float(_pick(futures, "ltp", "last_price"), 0.0)
    opt_ltp = _safe_float(_pick(selected, "ltp", "last_price"), 0.0)
    sync_span_ms = abs(fut_ts - opt_ts) / 1_000_000 if fut_ts > 0 and opt_ts > 0 else float("inf")
    sync_ok = sync_span_ms <= DEFAULT_SYNC_MAX_MS
    valid = bool(fut_ltp > 0.0 and opt_ltp > 0.0 and sync_ok)

    return SnapshotFrameView(
        kind=kind,
        futures=dict(futures),
        selected_option=dict(selected),
        dhan_context=dict(dhan_context),
        ts_event_ns=ts_event,
        ts_recv_ns=recv_ts,
        provider_id=provider,
        valid=valid,
        reason="OK" if valid else "MARKETDATA_INCOMPLETE_OR_UNSYNCED",
    )


SnapshotReader._frame = staticmethod(_batch7_frame)


if "_BATCH7_ORIGINAL_PROVIDER_RUNTIME" not in globals():
    _BATCH7_ORIGINAL_PROVIDER_RUNTIME = FeatureEngine._provider_runtime

    def _batch7_provider_runtime(self: FeatureEngine, raw: Mapping[str, Any]) -> dict[str, Any]:
        out = dict(_BATCH7_ORIGINAL_PROVIDER_RUNTIME(self, raw))
        if not raw:
            unavailable = getattr(N, "PROVIDER_STATUS_UNAVAILABLE", "UNAVAILABLE")
            out["futures_provider_status"] = unavailable
            out["selected_option_provider_status"] = unavailable
            out["option_context_provider_status"] = unavailable
            out["execution_provider_status"] = unavailable
        else:
            for key in (
                "futures_provider_status",
                "selected_option_provider_status",
                "option_context_provider_status",
                "execution_provider_status",
            ):
                if not out.get(key):
                    out[key] = getattr(N, "PROVIDER_STATUS_UNAVAILABLE", "UNAVAILABLE")
        return out

    FeatureEngine._provider_runtime = _batch7_provider_runtime


if "_BATCH7_ORIGINAL_SHARED_CORE" not in globals():
    _BATCH7_ORIGINAL_SHARED_CORE = FeatureEngine._shared_core

    def _batch7_shared_core(self: FeatureEngine, *args: Any, **kwargs: Any) -> dict[str, Any]:
        out = dict(_BATCH7_ORIGINAL_SHARED_CORE(self, *args, **kwargs))
        generated_at_ns = int(kwargs.get("generated_at_ns", out.get("generated_at_ns", 0)) or 0)
        quality = _dhan_context_quality(out.get("dhan_context", {}), generated_at_ns)
        out["dhan_context_quality"] = quality

        snapshot = dict(out.get("snapshot", {}))
        active_fut = dict(_nested(out, "futures", "active", default={}) or {})
        selected = dict(_nested(out, "options", "selected", default={}) or {})
        snapshot_valid = bool(
            _safe_bool(snapshot.get("sync_ok"), False)
            and _safe_bool(snapshot.get("freshness_ok"), False)
            and _safe_bool(snapshot.get("packet_gap_ok"), False)
            and _batch7_surface_present(active_fut)
            and _batch7_surface_present(selected)
        )
        snapshot["valid"] = snapshot_valid
        snapshot["validity"] = "OK" if snapshot_valid else "MARKETDATA_INCOMPLETE_OR_UNSYNCED"
        out["snapshot"] = snapshot
        return out

    FeatureEngine._shared_core = _batch7_shared_core


def _batch7_patch_stage_flags(
    *,
    stage_flags: Mapping[str, Any],
    shared_core: Mapping[str, Any],
    provider_runtime: Mapping[str, Any],
) -> dict[str, Any]:
    out = dict(stage_flags)
    snapshot = dict(shared_core.get("snapshot", {}) or {})
    quality = dict(shared_core.get("dhan_context_quality", {}) or {})
    active_fut = dict(_nested(shared_core, "futures", "active", default={}) or {})
    selected = dict(_nested(shared_core, "options", "selected", default={}) or {})

    futures_present = _batch7_surface_present(active_fut)
    selected_option_present = _batch7_surface_present(selected)
    snapshot_valid = bool(
        _safe_bool(snapshot.get("valid"), False)
        and _safe_bool(snapshot.get("sync_ok"), False)
        and _safe_bool(snapshot.get("freshness_ok"), False)
        and _safe_bool(snapshot.get("packet_gap_ok"), False)
        and futures_present
        and selected_option_present
    )

    runtime_modes = dict(shared_core.get("runtime_modes", {}) or {})
    classic = dict(runtime_modes.get("classic", {}) or {})
    miso = dict(runtime_modes.get("miso", {}) or {})

    classic_mode = _safe_str(
        classic.get("runtime_mode")
        or runtime_modes.get("strategy_runtime_mode_classic"),
        RUNTIME_DISABLED,
    )
    miso_mode = _safe_str(
        miso.get("runtime_mode")
        or runtime_modes.get("strategy_runtime_mode_miso"),
        RUNTIME_DISABLED,
    )

    provider_ready_classic = bool(
        classic_mode != RUNTIME_DISABLED
        and snapshot_valid
        and _batch7_provider_usable(provider_runtime.get("futures_provider_status"))
        and _batch7_provider_usable(provider_runtime.get("selected_option_provider_status"))
    )
    provider_ready_miso = bool(
        miso_mode != RUNTIME_DISABLED
        and quality.get("miso_context_ready") is True
        and futures_present
        and selected_option_present
        and provider_runtime.get("active_futures_provider_id") == PROVIDER_DHAN
        and provider_runtime.get("active_selected_option_provider_id") == PROVIDER_DHAN
        and provider_runtime.get("active_option_context_provider_id") == PROVIDER_DHAN
    )

    out["data_valid"] = snapshot_valid
    out["futures_present"] = futures_present
    out["selected_option_present"] = selected_option_present
    out["dhan_context_fresh"] = bool(quality.get("fresh"))
    out["provider_ready_classic"] = provider_ready_classic
    out["provider_ready_miso"] = provider_ready_miso
    return out


if "_BATCH7_ORIGINAL_FAMILY_FEATURES" not in globals():
    _BATCH7_ORIGINAL_FAMILY_FEATURES = FeatureEngine._family_features

    def _batch7_family_features(self: FeatureEngine, *args: Any, **kwargs: Any) -> dict[str, Any]:
        out = dict(_BATCH7_ORIGINAL_FAMILY_FEATURES(self, *args, **kwargs))

        shared_core = kwargs.get("shared_core")
        provider_runtime = kwargs.get("provider_runtime")
        if not isinstance(shared_core, Mapping):
            for item in args:
                if isinstance(item, Mapping) and "runtime_modes" in item and "snapshot" in item:
                    shared_core = item
                    break
        if not isinstance(provider_runtime, Mapping):
            provider_runtime = dict(out.get("provider_runtime", {}) or {})

        if isinstance(shared_core, Mapping):
            flags = _batch7_patch_stage_flags(
                stage_flags=dict(out.get("stage_flags", {}) or {}),
                shared_core=shared_core,
                provider_runtime=provider_runtime,
            )
            out["stage_flags"] = flags
            snapshot = dict(out.get("snapshot", {}) or {})
            snapshot["valid"] = bool(flags["data_valid"])
            snapshot["validity"] = "OK" if flags["data_valid"] else "MARKETDATA_INCOMPLETE_OR_UNSYNCED"
            out["snapshot"] = snapshot

            families = dict(out.get("families", {}) or {})
            miso = dict(families.get(FAMILY_MISO, {}) or {})
            quality = dict(shared_core.get("dhan_context_quality", {}) or {})
            if not flags.get("provider_ready_miso"):
                miso["eligible"] = False
                miso["chain_context_ready"] = bool(quality.get("miso_context_ready", False))
                miso["mode"] = RUNTIME_DISABLED
            families[FAMILY_MISO] = miso
            out["families"] = families

        return out

    FeatureEngine._family_features = _batch7_family_features


if "_BATCH7_ORIGINAL_SPLIT_OPTIONS" not in globals() and hasattr(FeatureEngine, "_split_options"):
    _BATCH7_ORIGINAL_SPLIT_OPTIONS = FeatureEngine._split_options

    _CONTEXT_ONLY_KEYS = {
        "oi",
        "oi_change",
        "volume",
        "iv",
        "iv_change_1m_pct",
        "delta",
        "authoritative_delta",
        "gamma",
        "theta",
        "vega",
        "cross_strike_spread_rank",
        "cross_strike_volume_rank",
        "spread_score",
        "depth_score",
        "volume_score",
        "oi_score",
        "iv_score",
        "delta_score",
        "gamma_score",
        "iv_sanity_score",
        "context_score",
        "oi_bias",
        "oi_wall_context",
        "near_same_side_wall",
        "same_side_wall_strength_score",
    }
    _ACTIVE_MARKET_KEYS = {
        "ltp",
        "last_price",
        "price",
        "bid",
        "ask",
        "best_bid",
        "best_ask",
        "bid_qty",
        "ask_qty",
        "bid_qty_5",
        "ask_qty_5",
        "depth_total",
        "touch_depth",
        "spread",
        "spread_ratio",
        "response_efficiency",
        "impact_depth_fraction",
        "age_ms",
        "stale",
        "present",
        "valid",
        "provider_id",
        "instrument_key",
        "instrument_token",
        "trading_symbol",
        "option_symbol",
        "side",
        "option_side",
        "strike",
        "expiry",
    }

    def _batch7_preserve_active_option_truth(active: Mapping[str, Any], merged: Mapping[str, Any]) -> dict[str, Any]:
        active_map = dict(active or {})
        merged_map = dict(merged or {})
        if not _batch7_surface_present(active_map):
            return merged_map
        out = dict(merged_map)
        for key in _ACTIVE_MARKET_KEYS:
            if key in active_map and active_map[key] not in (None, ""):
                out[key] = active_map[key]
        for key in _CONTEXT_ONLY_KEYS:
            if key in merged_map and key not in out:
                out[key] = merged_map[key]
        return out

    def _batch7_split_options(self: FeatureEngine, *args: Any, **kwargs: Any) -> Any:
        result = _BATCH7_ORIGINAL_SPLIT_OPTIONS(self, *args, **kwargs)
        try:
            opt_active = args[0] if args else kwargs.get("opt_active", {})
            if not isinstance(result, tuple) or len(result) != 2:
                return result
            call, put = result
            side = _normalize_side(_pick(opt_active, "side", "option_side"))
            if side == SIDE_CALL:
                call = _batch7_preserve_active_option_truth(opt_active, call)
            elif side == SIDE_PUT:
                put = _batch7_preserve_active_option_truth(opt_active, put)
            return call, put
        except Exception:
            return result

    FeatureEngine._split_options = _batch7_split_options


if "_BATCH7_ORIGINAL_BUILD_PAYLOAD" not in globals():
    _BATCH7_ORIGINAL_BUILD_PAYLOAD = FeatureEngine.build_payload

    def _batch7_build_payload(self: FeatureEngine, *args: Any, **kwargs: Any) -> dict[str, Any]:
        out = dict(_BATCH7_ORIGINAL_BUILD_PAYLOAD(self, *args, **kwargs))
        ff = dict(out.get("family_features", {}) or {})
        out["frame_valid"] = bool(_nested(ff, "stage_flags", "data_valid", default=False))
        out["warmup_complete"] = bool(_nested(ff, "stage_flags", "warmup_complete", default=False))
        return out

    FeatureEngine.build_payload = _batch7_build_payload


if "publish_error" in globals() and "_BATCH7_ORIGINAL_PUBLISH_ERROR" not in globals():
    _BATCH7_ORIGINAL_PUBLISH_ERROR = publish_error

    def publish_error(*args: Any, **kwargs: Any) -> Any:
        if "ts_event_ns" not in kwargs:
            kwargs["ts_event_ns"] = kwargs.get("ts_ns") or time.time_ns()
        return _BATCH7_ORIGINAL_PUBLISH_ERROR(*args, **kwargs)

# =============================================================================
# Batch 7 corrective closure: member-level snapshot sync truth
# =============================================================================
#
# _snapshot_block must not use active_frame.ts_event_ns for both futures and
# selected option timestamps. That collapses member skew and can incorrectly
# publish sync_ok=True for unsynced market data.

def _batch7_member_ts(frame: SnapshotFrameView | None, member: str) -> int | None:
    if frame is None:
        return None
    source = frame.futures if member == "futures" else frame.selected_option
    ts = _safe_int(_pick(source, "ts_event_ns", "event_ts_ns", "timestamp_ns"), 0)
    return ts or None


def _batch7_member_present(frame: SnapshotFrameView | None, member: str) -> bool:
    if frame is None:
        return False
    source = frame.futures if member == "futures" else frame.selected_option
    return _safe_float(_pick(source, "ltp", "last_price", "price"), 0.0) > 0.0


def _batch7_snapshot_block(
    self: FeatureEngine,
    generated_at_ns: int,
    active_frame: SnapshotFrameView | None,
    dhan_frame: SnapshotFrameView | None,
) -> dict[str, Any]:
    fut_ts = _batch7_member_ts(active_frame, "futures")
    opt_ts = _batch7_member_ts(active_frame, "selected_option")
    active_ts_candidates = [ts for ts in (fut_ts, opt_ts) if ts is not None]
    active_ts = max(active_ts_candidates) if active_ts_candidates else None

    dhan_fut_ts = _batch7_member_ts(dhan_frame, "futures")
    dhan_opt_ts = _batch7_member_ts(dhan_frame, "selected_option")
    dhan_ts_candidates = [ts for ts in (dhan_fut_ts, dhan_opt_ts) if ts is not None]
    dhan_ts = max(dhan_ts_candidates) if dhan_ts_candidates else None

    skew_ms = int(abs(fut_ts - opt_ts) / 1_000_000) if fut_ts and opt_ts else None
    sync_ok = bool(skew_ms is not None and skew_ms <= DEFAULT_SYNC_MAX_MS)
    fut_present = _batch7_member_present(active_frame, "futures")
    opt_present = _batch7_member_present(active_frame, "selected_option")

    valid = bool(active_frame and active_frame.valid and fut_present and opt_present and sync_ok)
    samples_seen = max(
        1,
        int(fut_present)
        + int(opt_present)
        + int(_batch7_member_present(dhan_frame, "futures"))
        + int(_batch7_member_present(dhan_frame, "selected_option")),
    )

    return {
        "valid": valid,
        "validity": "OK" if valid else "MARKETDATA_INCOMPLETE_OR_UNSYNCED",
        "sync_ok": sync_ok,
        "freshness_ok": True,
        "packet_gap_ok": True,
        "warmup_ok": True,
        "active_snapshot_ns": active_ts or generated_at_ns,
        "futures_snapshot_ns": fut_ts,
        "selected_option_snapshot_ns": opt_ts,
        "dhan_futures_snapshot_ns": dhan_fut_ts or dhan_ts,
        "dhan_option_snapshot_ns": dhan_opt_ts or dhan_ts,
        "max_member_age_ms": 0,
        "fut_opt_skew_ms": skew_ms,
        "hard_packet_gap_ms": DEFAULT_PACKET_GAP_MS,
        "samples_seen": samples_seen,
    }


FeatureEngine._snapshot_block = _batch7_snapshot_block
