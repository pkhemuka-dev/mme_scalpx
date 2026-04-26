from __future__ import annotations
from app.mme_scalpx.services.feature_family import option_core as _batch25kj_option_core
from app.mme_scalpx.services.feature_family import option_core as _batch25ki_option_core
from app.mme_scalpx.services.feature_family import option_core as _batch25kg_option_core

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
# Batch 25K shared-builder ABI audit
# =============================================================================

FEATURE_BUILDER_ABI_AUDIT: dict[str, int] = {
    "futures_core_builder_used": 0,
    "option_core_builder_used": 0,
    "strike_ladder_builder_used": 0,
    "classic_strike_builder_used": 0,
    "miso_strike_builder_used": 0,
    "regime_builder_used": 0,
    "tradability_builder_used": 0,
    "fallback_builder_count": 0,
    "call_first_typeerror_count": 0,
    "exact_builder_exception_count": 0,
}


def _builder_abi_audit_reset() -> None:
    for key in FEATURE_BUILDER_ABI_AUDIT:
        FEATURE_BUILDER_ABI_AUDIT[key] = 0


def _builder_abi_mark(key: str, count: int = 1) -> None:
    FEATURE_BUILDER_ABI_AUDIT[key] = int(FEATURE_BUILDER_ABI_AUDIT.get(key, 0)) + int(count)


def _builder_abi_audit_snapshot() -> dict[str, int]:
    return dict(FEATURE_BUILDER_ABI_AUDIT)


def _call_exact_builder(
    module: Any | None,
    function_name: str,
    *,
    audit_key: str,
    fallback_allowed: bool = True,
    **kwargs: Any,
) -> Any | None:
    if module is None:
        if fallback_allowed:
            _builder_abi_mark("fallback_builder_count")
        return None

    fn = getattr(module, function_name, None)
    if not callable(fn):
        if fallback_allowed:
            _builder_abi_mark("fallback_builder_count")
        return None

    try:
        out = fn(**kwargs)
        _builder_abi_mark(audit_key)
        return out
    except TypeError as exc:
        _builder_abi_mark("exact_builder_exception_count")
        if fallback_allowed:
            _builder_abi_mark("fallback_builder_count")
        LOGGER.warning(
            "shared_builder_abi_typeerror builder=%s kwargs=%s error=%s",
            function_name,
            sorted(kwargs.keys()),
            exc,
        )
        return None
    except Exception as exc:
        _builder_abi_mark("exact_builder_exception_count")
        if fallback_allowed:
            _builder_abi_mark("fallback_builder_count")
        LOGGER.warning(
            "shared_builder_abi_exception builder=%s error=%s",
            function_name,
            exc,
        )
        return None


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
    getattr(N, "HB_FEATURES", N.KEY_COMPAT_FEATURES_HEARTBEAT),
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


def _optional_provider_id(value: Any) -> str | None:
    """
    Provider ID parser with no silent fallback.

    Do not use _provider_id() in provider-runtime repair paths because _literal()
    intentionally falls back to the first allowed value when no default is allowed.
    For Batch 25H, missing provider identity must remain None and become an
    explicit unavailable provider surface, not DHAN/ZERODHA by accident.
    """

    text = _safe_str(value)
    return text if text in PROVIDER_IDS else None


def _provider_failover_mode(value: Any) -> str:
    allowed = tuple(getattr(N, "ALLOWED_PROVIDER_FAILOVER_MODES", ()))
    default = getattr(N, "PROVIDER_FAILOVER_MODE_MANUAL", "MANUAL")
    text = _safe_str(value)
    return text if text in allowed else default


def _provider_override_mode(value: Any) -> str:
    allowed = tuple(getattr(N, "ALLOWED_PROVIDER_OVERRIDE_MODES", ()))
    default = getattr(N, "PROVIDER_OVERRIDE_MODE_AUTO", "AUTO")
    text = _safe_str(value)
    return text if text in allowed else default


def _provider_transition_reason(value: Any) -> str:
    allowed = tuple(getattr(N, "ALLOWED_PROVIDER_TRANSITION_REASONS", ()))
    default = getattr(N, "PROVIDER_TRANSITION_REASON_BOOTSTRAP", "BOOTSTRAP")
    text = _safe_str(value)
    return text if text in allowed else default


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
            except TypeError as exc:
                _builder_abi_mark("call_first_typeerror_count")
                LOGGER.warning(
                    "optional_call_first_typeerror function=%s args=%s kwargs=%s error=%s",
                    name,
                    len(var_args),
                    sorted(var_kwargs.keys()),
                    exc,
                )
                continue
            except Exception as exc:
                LOGGER.warning("optional_call_first_exception function=%s error=%s", name, exc)
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



# =============================================================================
# Batch 25I — feed snapshot JSON/raw-surface adapter helpers
# =============================================================================

_FEED_SNAPSHOT_JSON_KEYS: Final[tuple[str, ...]] = (
    "future_json",
    "selected_call_json",
    "selected_put_json",
    "ce_atm_json",
    "ce_atm1_json",
    "pe_atm_json",
    "pe_atm1_json",
)

_FEED_FUTURE_JSON_KEYS: Final[tuple[str, ...]] = (
    "future_json",
    "futures_json",
    "selected_future_json",
    "underlying_json",
)

_FEED_CALL_JSON_KEYS: Final[tuple[str, ...]] = (
    "selected_call_json",
    "ce_atm_json",
    "ce_atm1_json",
    "call_json",
    "selected_ce_json",
)

_FEED_PUT_JSON_KEYS: Final[tuple[str, ...]] = (
    "selected_put_json",
    "pe_atm_json",
    "pe_atm1_json",
    "put_json",
    "selected_pe_json",
)


def _feed_json_load(value: Any) -> Any:
    if isinstance(value, (bytes, bytearray)):
        try:
            value = value.decode("utf-8")
        except Exception:
            return value
    if isinstance(value, str):
        text = value.strip()
        if not text or text.lower() in {"null", "none"}:
            return None
        try:
            return json.loads(text)
        except Exception:
            return value
    return value


def _feed_mapping(value: Any) -> dict[str, Any]:
    parsed = _feed_json_load(value)
    if isinstance(parsed, Mapping):
        return dict(parsed)
    return {}


def _feed_side(value: Any) -> str | None:
    text = _safe_str(value).upper()
    if text in {"CALL", "CE", "C"} or text.endswith("CE"):
        return "CALL"
    if text in {"PUT", "PE", "P"} or text.endswith("PE"):
        return "PUT"
    return None


def _feed_first_member(raw: Mapping[str, Any], keys: Sequence[str]) -> tuple[str | None, dict[str, Any]]:
    for key in keys:
        member = _feed_mapping(raw.get(key))
        if member:
            return key, member
    return None, {}


def _feed_merge_member(raw: Mapping[str, Any], member: Mapping[str, Any]) -> dict[str, Any]:
    merged = dict(raw)
    for key in _FEED_SNAPSHOT_JSON_KEYS:
        merged.pop(key, None)
    merged.update(dict(member))
    return merged


def _feed_depth_qty(row: Mapping[str, Any], side: str) -> float:
    if side == "bid":
        return _safe_float(
            _pick(row, "bid_qty_5", "top5_bid_qty", "bid_qty", "best_bid_qty"),
            0.0,
        )
    return _safe_float(
        _pick(row, "ask_qty_5", "top5_ask_qty", "ask_qty", "best_ask_qty"),
        0.0,
    )


def _feed_best_price(row: Mapping[str, Any], side: str) -> float:
    if side == "bid":
        return _safe_float(_pick(row, "best_bid", "bid", "bid_price"), 0.0)
    return _safe_float(_pick(row, "best_ask", "ask", "ask_price"), 0.0)


def _feed_ltp(row: Mapping[str, Any]) -> float:
    return _safe_float(_pick(row, "ltp", "last_price", "price", "last_traded_price"), 0.0)


def _feed_token(row: Mapping[str, Any]) -> str:
    return _safe_str(
        _pick(
            row,
            "instrument_token",
            "option_token",
            "token",
            "security_id",
            "securityId",
        )
    )


def _feed_instrument_key(row: Mapping[str, Any]) -> str:
    return _safe_str(
        _pick(
            row,
            "instrument_key",
            "instrumentKey",
            "instrument_id",
            "option_instrument_key",
        )
    ) or _feed_token(row)


def _feed_trading_symbol(row: Mapping[str, Any]) -> str:
    return _safe_str(
        _pick(
            row,
            "trading_symbol",
            "tradingsymbol",
            "option_symbol",
            "symbol",
        )
    )


def _feed_provider_id(row: Mapping[str, Any], default: Any = None) -> str:
    return _safe_str(_pick(row, "provider_id", "provider", default=default))





def _batch26f_misr_event_context(shared_core: Mapping[str, Any], branch_id: str) -> dict[str, Any]:
    """Read MISR branch event timestamps from explicit shared state only."""
    family = "MISR"
    branch_key = f"misr_{str(branch_id).lower()}"

    sources = (
        _nested(shared_core, "misr", "event_state", branch_id, default={}),
        _nested(shared_core, "misr", "event_state", branch_key, default={}),
        _nested(shared_core, "family_state", family, branch_id, default={}),
        _nested(shared_core, "family_state", family, branch_key, default={}),
        _nested(shared_core, "family_state", "misr", branch_id, default={}),
        _nested(shared_core, "runtime_state", family, branch_id, default={}),
        _nested(shared_core, "trap_events", branch_id, default={}),
    )

    merged: dict[str, Any] = {}
    for source in sources:
        if isinstance(source, Mapping):
            merged.update(source)

    return {
        "fake_break_start_ts_ms": int(_safe_float(
            merged.get("fake_break_start_ts_ms")
            or merged.get("trap_event_start_ts_ms")
            or merged.get("break_start_ts_ms"),
            0.0,
        )) or None,
        "fake_break_extreme_ts_ms": int(_safe_float(
            merged.get("fake_break_extreme_ts_ms")
            or merged.get("trap_event_extreme_ts_ms")
            or merged.get("break_extreme_ts_ms"),
            0.0,
        )) or None,
        "hold_proof_elapsed_sec": _safe_float(
            merged.get("hold_proof_elapsed_sec")
            or merged.get("hold_elapsed_sec"),
            0.0,
        ),
    }


def _batch26f_misr_zone_registry_from_sources(
    *,
    shared_core: Mapping[str, Any],
    futures_surface: Mapping[str, Any],
) -> tuple[dict[str, Any], ...]:
    try:
        from app.mme_scalpx.services.feature_family.misr_zones import (
            build_deterministic_misr_zone_registry,
        )
    except Exception:
        return ()

    try:
        return build_deterministic_misr_zone_registry(
            shared_core=shared_core,
            futures_surface=futures_surface,
        )
    except Exception:
        return ()



def _batch26g_miso_microstructure_option_surface(
    *,
    shared_core: Mapping[str, Any],
    branch_id: str,
    option_surface: Mapping[str, Any],
) -> dict[str, Any]:
    """Merge explicit MISO microstructure buffers into branch option surface.

    This is read-only enrichment of already-produced surfaces. Missing buffers
    remain missing, and MISO fails closed in miso_surface.py.
    """
    branch_key = "call" if branch_id == BRANCH_CALL else "put"
    out = dict(option_surface or {})
    selected = dict(_nested(out, "selected_features", default={}) or {})
    raw = dict(_nested(selected, "raw", default={}) or {})

    sources = (
        _nested(shared_core, "miso_microstructure", branch_id, default={}),
        _nested(shared_core, "miso_microstructure", branch_key, default={}),
        _nested(shared_core, "microstructure", "miso", branch_id, default={}),
        _nested(shared_core, "microstructure", "miso", branch_key, default={}),
        _nested(shared_core, "options", branch_key, "microstructure", default={}),
        _nested(shared_core, "options", branch_key, "selected_features", "microstructure", default={}),
        _nested(shared_core, "options", branch_key, "selected_features", "raw", default={}),
    )

    for source in sources:
        if not isinstance(source, Mapping):
            continue
        for key in (
            "recent_ticks",
            "trade_ticks",
            "tick_buffer",
            "ticks",
            "recent_trade_ticks",
            "ask_reloaded",
            "bid_reloaded",
            "queue_reload_veto",
        ):
            if key in source and key not in selected:
                selected[key] = source.get(key)
            if key in source and key not in raw:
                raw[key] = source.get(key)

    selected["raw"] = raw
    out["selected_features"] = selected

    shadow = dict(_nested(out, "shadow_features", default={}) or {})
    shadow_sources = (
        _nested(shared_core, "miso_shadow_microstructure", branch_id, default={}),
        _nested(shared_core, "miso_shadow_microstructure", branch_key, default={}),
        _nested(shared_core, "microstructure", "miso_shadow", branch_id, default={}),
        _nested(shared_core, "microstructure", "miso_shadow", branch_key, default={}),
        _nested(shared_core, "options", branch_key, "shadow_features", default={}),
        _nested(shared_core, "options", branch_key, "shadow_surface", "live", default={}),
    )
    for source in shadow_sources:
        if isinstance(source, Mapping):
            shadow.update(source)
    out["shadow_features"] = shadow

    return out

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
        """
        Normalize provider runtime from feeds.py canonical hash shape.

        Batch 25H law:
        - consume canonical ProviderRuntimeState.to_dict() keys first
        - preserve old active_* compatibility keys for existing consumers
        - never convert missing provider identities into DHAN/ZERODHA
        - missing/stale status becomes explicit UNAVAILABLE, not HEALTHY
        """

        raw_map = dict(raw or {})

        futures_provider = _optional_provider_id(
            _pick(
                raw_map,
                "futures_marketdata_provider_id",
                "active_futures_provider_id",
                "active_future_provider_id",
                "futures_provider_id",
            )
        )
        selected_option_provider = _optional_provider_id(
            _pick(
                raw_map,
                "selected_option_marketdata_provider_id",
                "active_selected_option_provider_id",
                "selected_option_provider_id",
                "option_provider_id",
            )
        )
        option_context_provider = _optional_provider_id(
            _pick(
                raw_map,
                "option_context_provider_id",
                "active_option_context_provider_id",
                "context_provider_id",
            )
        )
        execution_primary_provider = _optional_provider_id(
            _pick(
                raw_map,
                "execution_primary_provider_id",
                "active_execution_provider_id",
                "execution_provider_id",
            )
        )
        execution_fallback_provider = _optional_provider_id(
            _pick(
                raw_map,
                "execution_fallback_provider_id",
                "fallback_execution_provider_id",
            )
        )

        futures_status = _provider_status(
            _pick(
                raw_map,
                "futures_marketdata_status",
                "futures_provider_status",
                "active_futures_provider_status",
                "futures_provider_statu",
                "active_futures_provider_statu",
            )
        )
        selected_option_status = _provider_status(
            _pick(
                raw_map,
                "selected_option_marketdata_status",
                "selected_option_provider_status",
                "active_selected_option_provider_status",
                "selected_option_provider_statu",
                "active_selected_option_provider_statu",
            )
        )
        option_context_status = _provider_status(
            _pick(
                raw_map,
                "option_context_status",
                "option_context_provider_status",
                "active_option_context_provider_status",
                "option_context_provider_statu",
                "active_option_context_provider_statu",
            )
        )
        execution_primary_status = _provider_status(
            _pick(
                raw_map,
                "execution_primary_status",
                "execution_provider_status",
                "active_execution_provider_status",
                "execution_provider_statu",
                "active_execution_provider_statu",
            )
        )
        execution_fallback_status = _provider_status(
            _pick(
                raw_map,
                "execution_fallback_status",
                "fallback_execution_provider_status",
            )
        )

        family_runtime_mode = _family_runtime_mode(raw_map.get("family_runtime_mode"))

        return {
            # Canonical Batch 25G keys.
            "futures_marketdata_provider_id": futures_provider,
            "selected_option_marketdata_provider_id": selected_option_provider,
            "option_context_provider_id": option_context_provider,
            "execution_primary_provider_id": execution_primary_provider,
            "execution_fallback_provider_id": execution_fallback_provider,
            "futures_marketdata_status": futures_status,
            "selected_option_marketdata_status": selected_option_status,
            "option_context_status": option_context_status,
            "execution_primary_status": execution_primary_status,
            "execution_fallback_status": execution_fallback_status,
            "family_runtime_mode": family_runtime_mode,
            "failover_mode": _provider_failover_mode(raw_map.get("failover_mode")),
            "override_mode": _provider_override_mode(raw_map.get("override_mode")),
            "transition_reason": _provider_transition_reason(raw_map.get("transition_reason")),
            "provider_transition_seq": _safe_int(raw_map.get("provider_transition_seq"), 0),
            "failover_active": _safe_bool(raw_map.get("failover_active"), False),
            "pending_failover": _safe_bool(raw_map.get("pending_failover"), False),

            # Compatibility keys still consumed by current feature/strategy-family code.
            "active_futures_provider_id": futures_provider,
            "active_selected_option_provider_id": selected_option_provider,
            "active_option_context_provider_id": option_context_provider,
            "active_execution_provider_id": execution_primary_provider,
            "fallback_execution_provider_id": execution_fallback_provider,
            "provider_runtime_mode": (
                _safe_str(_pick(raw_map, "provider_runtime_mode", "runtime_mode"))
                or None
            ),
            "futures_provider_status": futures_status,
            "selected_option_provider_status": selected_option_status,
            "option_context_provider_status": option_context_status,
            "execution_provider_status": execution_primary_status,

            # Raw retained only for audit/debug. It is not a contract source.
            "raw": raw_map,
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
            "builder_abi_audit": _builder_abi_audit_snapshot(),
        }

    def _futures_surface(
        self,
        raw: Mapping[str, Any],
        *,
        role: str,
        provider_id: str,
    ) -> dict[str, Any]:
        surface_raw = (
            _flatten_snapshot_member_for_futures_surface(raw, role=role, provider_id=provider_id)
            if "_flatten_snapshot_member_for_futures_surface" in globals()
            else dict(raw or {})
        )

        runtime_mode = _safe_str(_pick(surface_raw, "runtime_mode"), RUNTIME_NORMAL)
        source_label = "dhan_futures" if role == "dhan" else "active_futures"
        role_label = (
            "miso_alignment_veto_truth"
            if role == "dhan"
            else "classic_directional_truth"
        )

        built = _call_exact_builder(
            self.shared_modules.get("futures_core"),
            "build_futures_surface",
            audit_key="futures_core_builder_used",
            futures_surface=surface_raw,
            runtime_mode=runtime_mode,
            source_label=source_label,
            role_label=role_label,
            provider_id=provider_id,
        )
        if isinstance(built, Mapping):
            out = dict(built)
            out.setdefault("role", role)
            out.setdefault("provider_id", provider_id)
            out.setdefault("source_label", source_label)
            out.setdefault("role_label", role_label)
            return out

        bid = _safe_float(_pick(surface_raw, "bid", "best_bid"), 0.0)
        ask = _safe_float(_pick(surface_raw, "ask", "best_ask"), 0.0)
        ltp = _safe_float(_pick(surface_raw, "ltp", "last_price", "price"), 0.0)
        bid_qty = _safe_float(
            _pick(surface_raw, "bid_qty", "best_bid_qty", "top5_bid_qty", "bid_qty_5"),
            0.0,
        )
        ask_qty = _safe_float(
            _pick(surface_raw, "ask_qty", "best_ask_qty", "top5_ask_qty", "ask_qty_5"),
            0.0,
        )

        spread = max(0.0, ask - bid) if bid > 0 and ask > 0 else 0.0
        mid = (bid + ask) / 2.0 if bid > 0 and ask > 0 else ltp
        depth_total = bid_qty + ask_qty
        ofi = _ratio(bid_qty - ask_qty, bid_qty + ask_qty, 0.0)
        vwap = _safe_float(_pick(surface_raw, "vwap"), ltp)

        return {
            "present": ltp > 0.0,
            "valid": ltp > 0.0,
            "role": role,
            "provider_id": provider_id,
            "instrument_key": _safe_str(_pick(surface_raw, "instrument_key"), getattr(N, "IK_MME_FUT", "")),
            "instrument_token": _safe_str(_pick(surface_raw, "instrument_token")),
            "trading_symbol": _safe_str(_pick(surface_raw, "trading_symbol", "symbol")),
            "ltp": ltp,
            "bid": bid,
            "ask": ask,
            "best_bid": bid,
            "best_ask": ask,
            "spread": spread,
            "spread_ratio": _safe_float(
                _pick(surface_raw, "spread_ratio"),
                _ratio(spread, max(mid * 0.0001, 0.05), 999.0),
            ),
            "depth_total": depth_total,
            "touch_depth": depth_total,
            "depth_ok": depth_total >= DEFAULT_DEPTH_MIN,
            "top5_bid_qty": bid_qty,
            "top5_ask_qty": ask_qty,
            "bid_qty": bid_qty,
            "ask_qty": ask_qty,
            "bid_qty_5": bid_qty,
            "ask_qty_5": ask_qty,
            "ofi_ratio_proxy": ofi,
            "ofi_persist_score": _safe_float(
                _pick(surface_raw, "ofi_persist_score", "weighted_ofi_persist"),
                ofi,
            ),
            "weighted_ofi": _clamp(0.5 + ofi / 2.0, 0.0, 1.0),
            "weighted_ofi_persist": _clamp(0.5 + ofi / 2.0, 0.0, 1.0),
            "nof": ofi,
            "nof_slope": _safe_float(_pick(surface_raw, "nof_slope"), 0.0),
            "delta_3": _safe_float(_pick(surface_raw, "delta_3", "ltp_delta_3"), 0.0),
            "vel_ratio": _safe_float(_pick(surface_raw, "vel_ratio", "velocity_ratio"), 1.0),
            "velocity_ratio": _safe_float(_pick(surface_raw, "velocity_ratio", "vel_ratio"), 1.0),
            "vol_norm": _safe_float(_pick(surface_raw, "vol_norm", "volume_norm"), 1.0),
            "volume_norm": _safe_float(_pick(surface_raw, "volume_norm", "vol_norm"), 1.0),
            "vwap": vwap,
            "vwap_distance": ltp - vwap if ltp > 0 and vwap > 0 else 0.0,
            "vwap_dist_pct": _ratio(ltp - vwap, vwap, 0.0) if ltp > 0 and vwap > 0 else 0.0,
            "above_vwap": bool(ltp > vwap) if ltp > 0 and vwap > 0 else False,
            "below_vwap": bool(ltp < vwap) if ltp > 0 and vwap > 0 else False,
            "ts_event_ns": _safe_int(_pick(surface_raw, "ts_event_ns", "event_ts_ns"), 0) or None,
            "age_ms": _safe_int(_pick(surface_raw, "age_ms"), 0) or None,
        }

    def _option_surface(
        self,
        raw: Mapping[str, Any],
        *,
        role: str,
        provider_id: str,
    ) -> dict[str, Any]:
        """
        Batch 25K-I source-anchored repair.

        This is the actual FeatureEngine._option_surface method. It must call
        option_core.build_live_option_surface through the exact shared-builder
        ABI path for both CALL and PUT surfaces.

        Required ABI:
            option_core.build_live_option_surface(
                side=...,
                live_source=...,
                provider_id=...,
                strike=...,
                instrument_key=...,
                instrument_token=...
            )
        """

        raw_map = dict(raw or {})

        role_hint = _safe_str(role)
        symbol_hint = _safe_str(
            _pick(raw_map, "option_symbol", "trading_symbol", "symbol", "instrument_key", "instrument_token")
        )

        inferred_side = _normalize_side(_pick(raw_map, "side", "option_side", "right", "branch_id"))

        if inferred_side not in (SIDE_CALL, SIDE_PUT):
            probe = f"{role_hint} {symbol_hint}".upper()
            if "PUT" in probe or " PE" in f" {probe} " or probe.endswith("PE") or "_PE" in probe or "-PE" in probe:
                inferred_side = SIDE_PUT
            elif "CALL" in probe or " CE" in f" {probe} " or probe.endswith("CE") or "_CE" in probe or "-CE" in probe:
                inferred_side = SIDE_CALL

        surface_raw = (
            _flatten_snapshot_member_for_option_surface(
                raw_map,
                side=inferred_side,
                role=role,
                provider_id=provider_id,
            )
            if "_flatten_snapshot_member_for_option_surface" in globals()
            else raw_map
        )

        side = _normalize_side(_pick(surface_raw, "side", "option_side", "right", "branch_id"))

        if side not in (SIDE_CALL, SIDE_PUT):
            probe = f"{role_hint} {symbol_hint} {_safe_str(_pick(surface_raw, 'option_symbol', 'trading_symbol', 'symbol', 'instrument_key', 'instrument_token'))}".upper()
            if "PUT" in probe or " PE" in f" {probe} " or probe.endswith("PE") or "_PE" in probe or "-PE" in probe:
                side = SIDE_PUT
            elif "CALL" in probe or " CE" in f" {probe} " or probe.endswith("CE") or "_CE" in probe or "-CE" in probe:
                side = SIDE_CALL

        side_text = _safe_str(side).upper()
        side_call_text = _safe_str(SIDE_CALL).upper()
        side_put_text = _safe_str(SIDE_PUT).upper()

        builder_side = ""
        if side_text in {side_call_text, "CALL", "CE", "C"}:
            builder_side = SIDE_CALL
        elif side_text in {side_put_text, "PUT", "PE", "P"}:
            builder_side = SIDE_PUT

        built = None

        if builder_side in (SIDE_CALL, SIDE_PUT):
            option_core_module = None
            try:
                option_core_module = self.shared_modules.get("option_core")
            except Exception:
                option_core_module = None

            if option_core_module is None:
                option_core_module = _batch25ki_option_core

            built = _call_exact_builder(
                option_core_module,
                "build_live_option_surface",
                audit_key="option_core_builder_used",
                fallback_allowed=False,
                side=builder_side,
                live_source=surface_raw,
                provider_id=provider_id,
                strike=_pick(surface_raw, "strike", "strike_price"),
                instrument_key=_safe_str(_pick(surface_raw, "instrument_key")),
                instrument_token=_safe_str(_pick(surface_raw, "instrument_token", "token")),
            )

        if isinstance(built, Mapping):
            out = dict(built)
            out.setdefault("role", role)
            out.setdefault("provider_id", provider_id)
            out.setdefault("side", builder_side or side)
            out.setdefault("option_side", builder_side or side)
            out.setdefault("instrument_key", _safe_str(_pick(surface_raw, "instrument_key")))
            out.setdefault("instrument_token", _safe_str(_pick(surface_raw, "instrument_token", "token")))
            out.setdefault("option_symbol", _safe_str(_pick(surface_raw, "option_symbol", "trading_symbol", "symbol")))
            out.setdefault("strike", _safe_float(_pick(surface_raw, "strike", "strike_price"), 0.0))
            return out

        bid = _safe_float(_pick(surface_raw, "bid", "best_bid"), 0.0)
        ask = _safe_float(_pick(surface_raw, "ask", "best_ask"), 0.0)
        ltp = _safe_float(_pick(surface_raw, "ltp", "last_price", "price"), 0.0)
        bid_qty = _safe_float(
            _pick(surface_raw, "bid_qty", "best_bid_qty", "top5_bid_qty", "bid_qty_5"),
            0.0,
        )
        ask_qty = _safe_float(
            _pick(surface_raw, "ask_qty", "best_ask_qty", "top5_ask_qty", "ask_qty_5"),
            0.0,
        )

        spread = max(0.0, ask - bid) if bid > 0 and ask > 0 else 0.0
        mid = (bid + ask) / 2.0 if bid > 0 and ask > 0 else ltp
        depth_total = bid_qty + ask_qty
        ofi = _ratio(bid_qty - ask_qty, bid_qty + ask_qty, 0.0)
        strike = _safe_float(_pick(surface_raw, "strike", "strike_price"), 0.0)

        return {
            "present": ltp > 0.0,
            "valid": ltp > 0.0,
            "role": role,
            "provider_id": provider_id,
            "side": builder_side or side,
            "option_side": builder_side or side,
            "instrument_key": _safe_str(_pick(surface_raw, "instrument_key")),
            "instrument_token": _safe_str(_pick(surface_raw, "instrument_token", "token")),
            "trading_symbol": _safe_str(_pick(surface_raw, "trading_symbol", "symbol")),
            "option_symbol": _safe_str(_pick(surface_raw, "option_symbol", "trading_symbol", "symbol")),
            "strike": strike,
            "ltp": ltp,
            "bid": bid,
            "ask": ask,
            "best_bid": bid,
            "best_ask": ask,
            "spread": spread,
            "spread_ratio": _safe_float(
                _pick(surface_raw, "spread_ratio"),
                _ratio(spread, max(mid * 0.0001, 0.05), 999.0),
            ),
            "depth_total": depth_total,
            "touch_depth": depth_total,
            "top5_bid_qty": bid_qty,
            "top5_ask_qty": ask_qty,
            "bid_qty": bid_qty,
            "ask_qty": ask_qty,
            "bid_qty_5": bid_qty,
            "ask_qty_5": ask_qty,
            "weighted_ofi": _clamp(0.5 + ofi / 2.0, 0.0, 1.0),
            "weighted_ofi_persist": _safe_float(
                _pick(surface_raw, "weighted_ofi_persist", "ofi_persist_score"),
                _clamp(0.5 + ofi / 2.0, 0.0, 1.0),
            ),
            "ofi_ratio_proxy": ofi,
            "delta_3": _safe_float(_pick(surface_raw, "delta_3", "ltp_delta_3"), 0.0),
            "velocity_ratio": _safe_float(_pick(surface_raw, "velocity_ratio", "vel_ratio"), 1.0),
            "vel_ratio": _safe_float(_pick(surface_raw, "vel_ratio", "velocity_ratio"), 1.0),
            "response_efficiency": _safe_float(
                _pick(surface_raw, "response_efficiency", "response_eff"),
                0.0,
            ),
            "impact_depth_fraction_one_lot": _safe_float(
                _pick(surface_raw, "impact_depth_fraction_one_lot", "impact_depth_fraction", "impact_fraction"),
                0.0,
            ),
            "entry_mode": _safe_str(_pick(surface_raw, "entry_mode")),
            "tick_size": _safe_float(_pick(surface_raw, "tick_size"), 0.05),
            "lot_size": _safe_int(_pick(surface_raw, "lot_size"), 0),
            "ts_event_ns": _safe_int(_pick(surface_raw, "ts_event_ns", "event_ts_ns"), 0) or None,
            "age_ms": _safe_int(_pick(surface_raw, "age_ms"), 0) or None,
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
        option_frame: Mapping[str, Any] | None,
        *args: Any,
        **kwargs: Any,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """
        Batch 25I side-specific selected option splitter.

        CALL prefers selected_call_json -> ce_atm_json -> ce_atm1_json.
        PUT prefers selected_put_json -> pe_atm_json -> pe_atm1_json.
        """

        raw_map = dict(option_frame or {})

        call_surface = self._option_surface(
            raw_map,
            side="CALL",
            role="SELECTED_CALL",
            provider_id=_feed_provider_id(raw_map),
        )
        put_surface = self._option_surface(
            raw_map,
            side="PUT",
            role="SELECTED_PUT",
            provider_id=_feed_provider_id(raw_map),
        )

        return call_surface, put_surface

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
        for key in (
            "option_chain_ladder_json",
            "strike_ladder_json",
            "option_chain_ladder",
            "strike_ladder",
            "strike_ladder_rows",
            "chain_rows",
            "option_chain",
            "chain",
            "rows",
            "ladder",
            "records",
            "data",
        ):
            parsed = _json_load(dhan_context.get(key), None)
            if isinstance(parsed, list):
                raw_rows = parsed
                break
            if isinstance(parsed, Mapping):
                for sub_key in ("data", "records", "items", "rows", "ladder", "chain", "chain_rows"):
                    sub_parsed = _json_load(parsed.get(sub_key), None)
                    if isinstance(sub_parsed, list):
                        raw_rows = sub_parsed
                        break
            if raw_rows is not None:
                break

        rows: list[dict[str, Any]] = []
        for item in raw_rows or []:
            row = _mapping(item)
            metadata = _mapping(row.get("metadata"))
            if metadata:
                merged = dict(metadata)
                merged.update(row)
                row = merged

            strike = _safe_float_or_none(_pick(row, "strike", "strike_price", "strikePrice"))
            if strike is None:
                continue

            side = _normalize_side(_pick(row, "side", "option_side", "right", "option_type"))
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
            "ltp": _safe_float(_pick(row, "ltp", "last_price", "price"), 0.0),
            "bid": bid,
            "ask": ask,
            "best_bid": bid,
            "best_ask": ask,
            "bid_qty_5": _safe_float(_pick(row, "bid_qty_5", "top5_bid_qty", "bid_qty", "best_bid_qty"), 0.0),
            "ask_qty_5": _safe_float(_pick(row, "ask_qty_5", "top5_ask_qty", "ask_qty", "best_ask_qty"), 0.0),
            "spread": max(0.0, ask - bid) if ask > 0 and bid > 0 else 0.0,
            "spread_ratio": _safe_float(_pick(row, "spread_ratio"), 0.0),
            "oi": _safe_float(_pick(row, "oi", "open_interest"), 0.0),
            "oi_change": _safe_float(_pick(row, "oi_change", "change_oi"), 0.0),
            "volume": _safe_float(_pick(row, "volume"), 0.0),
            "iv": _safe_float_or_none(_pick(row, "iv", "implied_volatility")),
            "delta": _safe_float_or_none(_pick(row, "delta", "option_delta")),
            "score": _safe_float_or_none(_pick(row, "score", "strike_score", "rank_score")),
            "provider_id": _safe_str(_pick(row, "provider_id")),
            "ts_event_ns": _safe_int(_pick(row, "ts_event_ns", "event_ts_ns", "timestamp_ns"), 0) or None,
            "instrument_key": _safe_str(_pick(row, "instrument_key")),
            "instrument_token": _safe_str(_pick(row, "instrument_token", "token")),
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
        module = self.shared_modules.get("strike_selection")

        ladder_surface = _call_exact_builder(
            module,
            "build_strike_ladder_surface",
            audit_key="strike_ladder_builder_used",
            dhan_context=dhan_context,
            futures_features=futures,
            selected_features=selected,
        )
        oi_wall_summary = _call_exact_builder(
            module,
            "build_oi_wall_summary",
            audit_key="strike_ladder_builder_used",
            fallback_allowed=False,
            dhan_context=dhan_context,
            futures_features=futures,
            selected_features=selected,
        )

        classic_call = _call_exact_builder(
            module,
            "build_classic_strike_surface",
            audit_key="classic_strike_builder_used",
            dhan_context=dhan_context,
            side=SIDE_CALL,
            futures_features=futures,
            selected_features=call,
        )
        classic_put = _call_exact_builder(
            module,
            "build_classic_strike_surface",
            audit_key="classic_strike_builder_used",
            fallback_allowed=False,
            dhan_context=dhan_context,
            side=SIDE_PUT,
            futures_features=futures,
            selected_features=put,
        )

        miso_call = _call_exact_builder(
            module,
            "build_miso_strike_surface",
            audit_key="miso_strike_builder_used",
            dhan_context=dhan_context,
            side=SIDE_CALL,
            futures_features=futures,
            selected_features=call,
        )
        miso_put = _call_exact_builder(
            module,
            "build_miso_strike_surface",
            audit_key="miso_strike_builder_used",
            fallback_allowed=False,
            dhan_context=dhan_context,
            side=SIDE_PUT,
            futures_features=futures,
            selected_features=put,
        )

        if isinstance(ladder_surface, Mapping):
            ladder_rows = []
            for container_key in ("calls", "puts", "rows", "ladder"):
                value = ladder_surface.get(container_key)
                if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
                    ladder_rows.extend(dict(row) for row in value if isinstance(row, Mapping))
            ladder = ladder_rows or self._ladder(dhan_context)
        else:
            ladder = self._ladder(dhan_context)

        wall_summary = dict(oi_wall_summary) if isinstance(oi_wall_summary, Mapping) else {}
        call_wall = dict(wall_summary.get("call_wall") or {}) if wall_summary else {}
        put_wall = dict(wall_summary.get("put_wall") or {}) if wall_summary else {}

        if not call_wall or not put_wall:
            reference = (
                _safe_float(futures.get("ltp"), 0.0)
                or _safe_float(_pick(dhan_context, "atm_strike", "underlying_atm"), 0.0)
                or _safe_float(selected.get("strike"), 0.0)
            )
            call_wall = call_wall or self._nearest_wall(ladder, SIDE_CALL, reference)
            put_wall = put_wall or self._nearest_wall(ladder, SIDE_PUT, reference)

        call_strength = _safe_float(
            _pick(call_wall, "wall_strength_score", "wall_strength"),
            0.0,
        )
        put_strength = _safe_float(
            _pick(put_wall, "wall_strength_score", "wall_strength"),
            0.0,
        )
        oi_bias = _safe_str(_pick(wall_summary, "oi_bias", dhan_context.get("oi_bias")))
        if not oi_bias:
            if call_strength > put_strength + 0.05:
                oi_bias = "CALL_WALL_DOMINANT"
            elif put_strength > call_strength + 0.05:
                oi_bias = "PUT_WALL_DOMINANT"
            else:
                oi_bias = "NEUTRAL"

        return {
            "chain_context_ready": bool(ladder or dhan_context),
            "atm_strike": _safe_float_or_none(
                _pick(wall_summary, "atm_reference_strike", dhan_context.get("atm_strike"), dhan_context.get("underlying_atm"))
            ),
            "selected_strike": selected.get("strike"),
            "shadow_call_strike": call.get("strike"),
            "shadow_put_strike": put.get("strike"),
            "ladder": ladder,
            "ladder_size": len(ladder),
            "ladder_surface": dict(ladder_surface) if isinstance(ladder_surface, Mapping) else {},
            "classic_call": dict(classic_call) if isinstance(classic_call, Mapping) else {},
            "classic_put": dict(classic_put) if isinstance(classic_put, Mapping) else {},
            "miso_call": dict(miso_call) if isinstance(miso_call, Mapping) else {},
            "miso_put": dict(miso_put) if isinstance(miso_put, Mapping) else {},
            "nearest_call_oi_resistance": call_wall,
            "nearest_put_oi_support": put_wall,
            "nearest_call_oi_resistance_strike": _pick(call_wall, "strike"),
            "nearest_put_oi_support_strike": _pick(put_wall, "strike"),
            "call_wall_strength": call_strength,
            "put_wall_strength": put_strength,
            "oi_bias": oi_bias,
            "oi_wall_context": {
                "call": call_wall,
                "put": put_wall,
                "summary": wall_summary,
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
        built = _call_exact_builder(
            self.shared_modules.get("regime"),
            "build_regime_surface",
            audit_key="regime_builder_used",
            futures_surface=futures,
        )
        if isinstance(built, Mapping):
            out = dict(built)
            out["regime"] = _regime(out.get("regime"))
            out.setdefault("cross_option_ready", bool(cross_option.get("cross_option_ready")))
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
        module = self.shared_modules.get("tradability")
        regime_id = _regime(regime.get("regime"))

        futures_liq_built = _call_exact_builder(
            module,
            "build_futures_liquidity_surface",
            audit_key="tradability_builder_used",
            futures_surface=futures,
        )
        futures_liq = (
            dict(futures_liq_built)
            if isinstance(futures_liq_built, Mapping)
            else {
                "liquidity_pass": bool(futures.get("depth_ok")),
                "spread_ratio": futures.get("spread_ratio"),
                "depth_total": futures.get("depth_total"),
            }
        )

        classic_call_built = _call_exact_builder(
            module,
            "build_classic_option_tradability_surface",
            audit_key="tradability_builder_used",
            branch_id=BRANCH_CALL,
            option_surface=call,
            regime=regime_id,
            runtime_mode=RUNTIME_NORMAL,
            selection_label="classic_call",
        )
        classic_put_built = _call_exact_builder(
            module,
            "build_classic_option_tradability_surface",
            audit_key="tradability_builder_used",
            fallback_allowed=False,
            branch_id=BRANCH_PUT,
            option_surface=put,
            regime=regime_id,
            runtime_mode=RUNTIME_NORMAL,
            selection_label="classic_put",
        )
        miso_call_built = _call_exact_builder(
            module,
            "build_miso_option_tradability_surface",
            audit_key="tradability_builder_used",
            option_surface=call,
            futures_surface=futures,
            runtime_mode=RUNTIME_BASE_5DEPTH,
        )
        miso_put_built = _call_exact_builder(
            module,
            "build_miso_option_tradability_surface",
            audit_key="tradability_builder_used",
            fallback_allowed=False,
            option_surface=put,
            futures_surface=futures,
            runtime_mode=RUNTIME_BASE_5DEPTH,
        )

        return {
            "futures": futures_liq,
            "classic_call": dict(classic_call_built) if isinstance(classic_call_built, Mapping) else self._option_tradability(call, side=SIDE_CALL),
            "classic_put": dict(classic_put_built) if isinstance(classic_put_built, Mapping) else self._option_tradability(put, side=SIDE_PUT),
            "miso_call": dict(miso_call_built) if isinstance(miso_call_built, Mapping) else self._option_tradability(call, side=SIDE_CALL),
            "miso_put": dict(miso_put_built) if isinstance(miso_put_built, Mapping) else self._option_tradability(put, side=SIDE_PUT),
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

    def _branch_runtime_mode_surface(
        self,
        family_id: str,
        shared_core: Mapping[str, Any],
    ) -> dict[str, Any]:
        mode_key = "miso" if family_id == FAMILY_MISO else "classic"
        surface = dict(_nested(shared_core, "runtime_modes", mode_key, default={}))
        mode = _safe_str(_pick(surface, "runtime_mode", "mode"), RUNTIME_DISABLED)
        surface.setdefault("mode", mode)
        surface.setdefault("runtime_mode", mode)
        surface.setdefault("provider_ready", mode != RUNTIME_DISABLED)
        return surface

    def _branch_futures_surface(
        self,
        family_id: str,
        shared_core: Mapping[str, Any],
    ) -> dict[str, Any]:
        # MISO is Dhan-context enhanced. Provider doctrine alignment remains 25N,
        # so this batch uses Dhan futures when present and active futures as
        # explicit fallback only to keep the service-path surface rich.
        if family_id == FAMILY_MISO:
            dhan = dict(_nested(shared_core, "futures", "dhan", default={}))
            if dhan.get("present") or dhan.get("valid") or dhan.get("ltp"):
                return dhan
        return dict(_nested(shared_core, "futures", "active", default={}))

    def _branch_option_surface(
        self,
        branch_id: str,
        shared_core: Mapping[str, Any],
    ) -> dict[str, Any]:
        branch_key = "call" if branch_id == BRANCH_CALL else "put"
        return dict(_nested(shared_core, "options", branch_key, default={}))

    def _branch_fallback_option_surface(
        self,
        family_id: str,
        branch_id: str,
        shared_core: Mapping[str, Any],
    ) -> dict[str, Any]:
        # MISO branch builder does not accept fallback_option_surface.
        if family_id == FAMILY_MISO:
            return {}
        opposite_key = "put" if branch_id == BRANCH_CALL else "call"
        fallback = dict(_nested(shared_core, "options", opposite_key, default={}))
        if fallback.get("present") or fallback.get("instrument_key"):
            return fallback
        return {}

    def _branch_strike_surface(
        self,
        family_id: str,
        branch_id: str,
        shared_core: Mapping[str, Any],
    ) -> dict[str, Any]:
        strike = dict(_nested(shared_core, "strike_selection", default={}))
        branch_key = "call" if branch_id == BRANCH_CALL else "put"

        if family_id == FAMILY_MISO:
            specific_key = f"miso_{branch_key}"
        else:
            specific_key = f"classic_{branch_key}"

        specific = dict(strike.get(specific_key) or {})
        out = dict(specific)
        out.setdefault("source_surface_key", specific_key)
        out.setdefault("family_id", family_id)
        out.setdefault("branch_id", branch_id)
        out.setdefault("side", _branch_side(branch_id))
        out.setdefault("ladder", strike.get("ladder", []))
        out.setdefault("ladder_size", strike.get("ladder_size", 0))
        out.setdefault("ladder_surface", strike.get("ladder_surface", {}))
        out.setdefault("oi_wall_context", strike.get("oi_wall_context", {}))
        out.setdefault(
            "nearest_call_oi_resistance",
            strike.get("nearest_call_oi_resistance", {}),
        )
        out.setdefault(
            "nearest_put_oi_support",
            strike.get("nearest_put_oi_support", {}),
        )
        out.setdefault(
            "nearest_call_oi_resistance_strike",
            strike.get("nearest_call_oi_resistance_strike"),
        )
        out.setdefault(
            "nearest_put_oi_support_strike",
            strike.get("nearest_put_oi_support_strike"),
        )
        out.setdefault("call_wall_strength", strike.get("call_wall_strength"))
        out.setdefault("put_wall_strength", strike.get("put_wall_strength"))
        out.setdefault("oi_bias", strike.get("oi_bias"))
        out.setdefault("chain_context_ready", strike.get("chain_context_ready"))
        return out

    def _branch_tradability_surface(
        self,
        family_id: str,
        branch_id: str,
        shared_core: Mapping[str, Any],
    ) -> dict[str, Any]:
        branch_key = "call" if branch_id == BRANCH_CALL else "put"
        prefix = "miso" if family_id == FAMILY_MISO else "classic"
        key = f"{prefix}_{branch_key}"
        surface = dict(_nested(shared_core, "tradability", key, default={}))
        surface.setdefault("source_surface_key", key)
        surface.setdefault("family_id", family_id)
        surface.setdefault("branch_id", branch_id)
        surface.setdefault("side", _branch_side(branch_id))
        return surface

    def _family_thresholds(
        self,
        family_id: str,
        shared_core: Mapping[str, Any],
    ) -> dict[str, Any]:
        thresholds = dict(_nested(shared_core, "thresholds", family_id, default={}))
        thresholds.setdefault("family_id", family_id)
        return thresholds

    def _family_provider_ready(
        self,
        family_id: str,
        branch_id: str,
        provider_runtime: Mapping[str, Any],
        shared_core: Mapping[str, Any],
    ) -> bool:
        runtime_surface = self._branch_runtime_mode_surface(family_id, shared_core)
        option_surface = self._branch_option_surface(branch_id, shared_core)
        futures_surface = self._branch_futures_surface(family_id, shared_core)

        runtime_ready = bool(runtime_surface.get("provider_ready"))
        option_ready = bool(option_surface.get("present") or option_surface.get("instrument_key"))
        futures_ready = bool(futures_surface.get("present") or futures_surface.get("valid") or futures_surface.get("ltp"))

        if family_id == FAMILY_MISO:
            context_ready = bool(_nested(shared_core, "context_quality", "miso_context_ready", default=False))
            # 25N will finalize strict provider doctrine. 25L only blocks missing
            # surfaces from pretending to be ready.
            return bool(runtime_ready and option_ready and futures_ready and context_ready)

        return bool(runtime_ready and option_ready and futures_ready)

    def _misr_zone_registry_surface(
        self,
        module: Any | None,
        futures_surface: Mapping[str, Any],
        shared_core: Mapping[str, Any],
    ) -> dict[str, Any]:
        if module is None or not callable(getattr(module, "build_misr_zone_registry_surface", None)):
            return {}

        zones = _nested(shared_core, "misr", "zone_registry", default=[])
        if not zones:
            zones = _nested(shared_core, "zone_registry", default=[])
        if not zones:
            zones = _batch26f_misr_zone_registry_from_sources(
                shared_core=shared_core,
                futures_surface=futures_surface,
            )

        built = _call_exact_builder(
            module,
            "build_misr_zone_registry_surface",
            audit_key="family_zone_registry_builder_used",
            fallback_allowed=False,
            zone_registry=zones,
            futures_surface=futures_surface,
            thresholds={},
        )
        return dict(built) if isinstance(built, Mapping) else {}

    def _call_family_branch_builder(
        self,
        family_id: str,
        branch_id: str,
        module: Any | None,
        shared_core: Mapping[str, Any],
        provider_runtime: Mapping[str, Any],
    ) -> dict[str, Any]:
        family_lc = family_id.lower()
        futures_surface = self._branch_futures_surface(family_id, shared_core)
        option_surface = self._branch_option_surface(branch_id, shared_core)
        if family_id == FAMILY_MISO:
            option_surface = _batch26g_miso_microstructure_option_surface(
                shared_core=shared_core,
                branch_id=branch_id,
                option_surface=option_surface,
            )
        strike_surface = self._branch_strike_surface(family_id, branch_id, shared_core)
        tradability_surface = self._branch_tradability_surface(family_id, branch_id, shared_core)
        regime_surface = dict(_nested(shared_core, "regime", default={}))
        runtime_mode_surface = self._branch_runtime_mode_surface(family_id, shared_core)
        thresholds = self._family_thresholds(family_id, shared_core)
        provider_ready = self._family_provider_ready(
            family_id,
            branch_id,
            provider_runtime,
            shared_core,
        )

        kwargs: dict[str, Any] = {
            "branch_id": branch_id,
            "futures_surface": futures_surface,
            "option_surface": option_surface,
            "strike_surface": strike_surface,
            "tradability_surface": tradability_surface,
            "regime_surface": regime_surface,
            "runtime_mode_surface": runtime_mode_surface,
            "thresholds": thresholds,
            "provider_ready": provider_ready,
        }

        if family_id != FAMILY_MISO:
            kwargs["fallback_option_surface"] = self._branch_fallback_option_surface(
                family_id,
                branch_id,
                shared_core,
            )

        if family_id == FAMILY_MISC:
            kwargs.update(_batch26e_misc_state_context(shared_core, branch_id))

        if family_id == FAMILY_MISR:
            kwargs.update(_batch26f_misr_event_context(shared_core, branch_id))
            kwargs["zone_registry_surface"] = self._misr_zone_registry_surface(
                module,
                futures_surface,
                shared_core,
            )

        built = _call_exact_builder(
            module,
            f"build_{family_lc}_branch_surface",
            audit_key="family_branch_builder_used",
            fallback_allowed=False,
            **kwargs,
        )

        surface = dict(built) if isinstance(built, Mapping) else {}
        if not surface:
            _builder_abi_mark("family_branch_builder_missing_surface")

        return surface

    def _call_family_root_builder(
        self,
        family_id: str,
        module: Any | None,
        branches: Mapping[str, Mapping[str, Any]],
        shared_core: Mapping[str, Any],
    ) -> dict[str, Any]:
        family_lc = family_id.lower()
        call_surface = dict(branches.get(BRANCH_CALL, {}))
        put_surface = dict(branches.get(BRANCH_PUT, {}))
        futures_surface = self._branch_futures_surface(family_id, shared_core)

        kwargs: dict[str, Any] = {
            "call_surface": call_surface,
            "put_surface": put_surface,
            "runtime_mode_surface": self._branch_runtime_mode_surface(family_id, shared_core),
            "regime_surface": dict(_nested(shared_core, "regime", default={})),
        }


        if family_id == FAMILY_MISR:
            kwargs["zone_registry_surface"] = self._misr_zone_registry_surface(
                module,
                futures_surface,
                shared_core,
            )

        built = _call_exact_builder(
            module,
            f"build_{family_lc}_family_surface",
            audit_key="family_root_builder_used",
            fallback_allowed=False,
            **kwargs,
        )

        surface = dict(built) if isinstance(built, Mapping) else {}
        if not surface:
            _builder_abi_mark("family_root_builder_missing_surface")

        return surface


    def _family_surface(
        self,
        family_id: str,
        module: Any | None,
        branches: Mapping[str, Mapping[str, Any]],
        shared_core: Mapping[str, Any],
    ) -> dict[str, Any]:
        call_surface = dict(branches.get(BRANCH_CALL, {}))
        put_surface = dict(branches.get(BRANCH_PUT, {}))

        surface = self._call_family_root_builder(family_id, module, branches, shared_core)

        surface.setdefault("family_id", family_id)
        surface.setdefault("surface_kind", f"{family_id.lower()}_family")
        surface.setdefault("eligible", bool(call_surface.get("eligible") or put_surface.get("eligible")))
        surface.setdefault("branches", {BRANCH_CALL: call_surface, BRANCH_PUT: put_surface})
        surface.setdefault("call", call_surface)
        surface.setdefault("put", put_surface)
        surface.setdefault(
            "runtime_mode_surface",
            self._branch_runtime_mode_surface(family_id, shared_core),
        )
        surface.setdefault("regime_surface", dict(_nested(shared_core, "regime", default={})))
        surface.setdefault("rich_surface", True)

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

        Batch 25H repairs the producer/consumer seam:
        - canonical provider keys are preserved from feeds.py ProviderRuntimeState
        - compatibility active_* keys mirror the canonical values
        - provider status aliases mirror canonical status values
        - missing provider identity remains None; missing status becomes UNAVAILABLE
        - this method does not select providers or perform failover
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

        futures_provider = _optional_provider_id(
            _pick(
                provider_runtime,
                "futures_marketdata_provider_id",
                "active_futures_provider_id",
                "active_future_provider_id",
                "futures_provider_id",
            )
        )
        selected_option_provider = _optional_provider_id(
            _pick(
                provider_runtime,
                "selected_option_marketdata_provider_id",
                "active_selected_option_provider_id",
                "selected_option_provider_id",
                "option_provider_id",
            )
        )
        option_context_provider = _optional_provider_id(
            _pick(
                provider_runtime,
                "option_context_provider_id",
                "active_option_context_provider_id",
                "context_provider_id",
            )
        )
        execution_primary_provider = _optional_provider_id(
            _pick(
                provider_runtime,
                "execution_primary_provider_id",
                "active_execution_provider_id",
                "execution_provider_id",
            )
        )
        execution_fallback_provider = _optional_provider_id(
            _pick(
                provider_runtime,
                "execution_fallback_provider_id",
                "fallback_execution_provider_id",
            )
        )

        futures_status = _provider_status(
            _pick(provider_runtime, "futures_marketdata_status", "futures_provider_status")
        )
        selected_option_status = _provider_status(
            _pick(
                provider_runtime,
                "selected_option_marketdata_status",
                "selected_option_provider_status",
            )
        )
        option_context_status = _provider_status(
            _pick(provider_runtime, "option_context_status", "option_context_provider_status")
        )
        execution_primary_status = _provider_status(
            _pick(provider_runtime, "execution_primary_status", "execution_provider_status")
        )
        execution_fallback_status = _provider_status(
            _pick(provider_runtime, "execution_fallback_status", "fallback_execution_provider_status")
        )

        values: dict[str, Any] = {
            # Canonical Batch 25G keys.
            "futures_marketdata_provider_id": futures_provider,
            "selected_option_marketdata_provider_id": selected_option_provider,
            "option_context_provider_id": option_context_provider,
            "execution_primary_provider_id": execution_primary_provider,
            "execution_fallback_provider_id": execution_fallback_provider,
            "futures_marketdata_status": futures_status,
            "selected_option_marketdata_status": selected_option_status,
            "option_context_status": option_context_status,
            "execution_primary_status": execution_primary_status,
            "execution_fallback_status": execution_fallback_status,
            "family_runtime_mode": _family_runtime_mode(
                provider_runtime.get("family_runtime_mode")
            ),
            "failover_mode": _provider_failover_mode(provider_runtime.get("failover_mode")),
            "override_mode": _provider_override_mode(provider_runtime.get("override_mode")),
            "transition_reason": _provider_transition_reason(
                provider_runtime.get("transition_reason")
            ),
            "provider_transition_seq": _safe_int(
                provider_runtime.get("provider_transition_seq"),
                0,
            ),
            "failover_active": _safe_bool(provider_runtime.get("failover_active"), False),
            "pending_failover": _safe_bool(provider_runtime.get("pending_failover"), False),

            # Compatibility keys.
            "active_futures_provider_id": futures_provider,
            "active_selected_option_provider_id": selected_option_provider,
            "active_option_context_provider_id": option_context_provider,
            "active_execution_provider_id": execution_primary_provider,
            "fallback_execution_provider_id": execution_fallback_provider,
            "provider_runtime_mode": (
                _safe_str(_pick(provider_runtime, "provider_runtime_mode", "runtime_mode"))
                or None
            ),
            "futures_provider_status": futures_status,
            "selected_option_provider_status": selected_option_status,
            "option_context_provider_status": option_context_status,
            "execution_provider_status": execution_primary_status,

            # Existing mode/readiness fields are retained only if the contract block has them.
            "classic_runtime_mode": classic_mode,
            "miso_runtime_mode": miso_mode,
            "provider_ready_classic": classic_mode != RUNTIME_DISABLED,
            "provider_ready_miso": _batch26c_miso_provider_ready(
                provider_runtime,
                miso_mode=miso_mode,
                futures_present=True,
                selected_option_present=True,
                dhan_context_ready=True,
                dhan_context_fresh=True,
            ),

            # Transitional typo compatibility only if previous contracts still declare it.
            "futures_provider_statu": futures_status,
            "selected_option_provider_statu": selected_option_status,
            "option_context_provider_statu": option_context_status,
            "execution_provider_statu": execution_primary_status,
        }

        _patch_existing(block, values)

        for key in tuple(block.keys()):
            if key.endswith("_provider_status") or key.endswith("_marketdata_status") or key.endswith("_status"):
                if "status" in key:
                    block[key] = _provider_status(block.get(key))
            if key.endswith("_provider_id") or key.endswith("_provider"):
                if block.get(key) == "":
                    block[key] = None

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
                "provider_ready_miso": _batch26c_miso_provider_ready(
                    provider,
                    miso_mode=provider.get("miso_runtime_mode"),
                    futures_present=bool(_nested(shared_core, "futures", "active", "present", default=False)),
                    selected_option_present=bool(
                        _nested(common, "selected_option", "selected_option_present", default=False)
                        or _nested(common, "selected_option", "ltp", default=None)
                    ),
                    dhan_context_ready=bool(
                        _nested(shared_core, "dhan_context_quality", "miso_context_ready", default=False)
                        or _nested(shared_core, "dhan_context", default={})
                    ),
                    dhan_context_fresh=bool(
                        _nested(shared_core, "dhan_context_quality", "fresh", default=False)
                        or _nested(shared_core, "dhan_context", default={})
                    ),
                ),
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

                call_support = self._canonical_support(
                    family_id,
                    _empty_builder("build_empty_miso_side_support"),
                    call_surface,
                )
                put_support = self._canonical_support(
                    family_id,
                    _empty_builder("build_empty_miso_side_support"),
                    put_surface,
                )

                _patch_existing(
                    family_block,
                    {
                        "eligible": bool(
                            self._family_branch_eligible(family_id, call_support)
                            or self._family_branch_eligible(family_id, put_support)
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
                        "call_support": call_support,
                        "put_support": put_support,
                    },
                )

            elif family_id == FAMILY_MISR:
                branches = dict(family_block.get("branches", {}))
                active_zone = self._active_zone(_nested(rich_family, "active_zone", default={}))
                active_zone_valid = self._active_zone_valid(active_zone, rich_family)

                call_support = self._canonical_support(
                    family_id,
                    _empty_builder("build_empty_misr_branch_support"),
                    _nested(rich_family, "branches", BRANCH_CALL, default={}),
                    extra={"active_zone_valid": active_zone_valid},
                )
                put_support = self._canonical_support(
                    family_id,
                    _empty_builder("build_empty_misr_branch_support"),
                    _nested(rich_family, "branches", BRANCH_PUT, default={}),
                    extra={"active_zone_valid": active_zone_valid},
                )

                branches[BRANCH_CALL] = call_support
                branches[BRANCH_PUT] = put_support

                _patch_existing(
                    family_block,
                    {
                        "eligible": bool(
                            self._family_branch_eligible(family_id, call_support)
                            or self._family_branch_eligible(family_id, put_support)
                        ),
                        "active_zone": active_zone,
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
                call_support = self._canonical_support(
                    family_id,
                    _empty_builder(builder),
                    _nested(rich_family, "branches", BRANCH_CALL, default={}),
                )
                put_support = self._canonical_support(
                    family_id,
                    _empty_builder(builder),
                    _nested(rich_family, "branches", BRANCH_PUT, default={}),
                )

                branches[BRANCH_CALL] = call_support
                branches[BRANCH_PUT] = put_support

                _patch_existing(
                    family_block,
                    {
                        "eligible": bool(
                            self._family_branch_eligible(family_id, call_support)
                            or self._family_branch_eligible(family_id, put_support)
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

    def _canonical_support(
        self,
        family_id: str,
        template: Mapping[str, Any],
        rich: Mapping[str, Any],
        *,
        extra: Mapping[str, Any] | None = None,
    ) -> dict[str, bool]:
        out: dict[str, bool] = {
            key: bool(value) for key, value in template.items() if isinstance(value, bool)
        }
        rich_map = dict(_mapping(rich))
        if extra:
            rich_map.update(dict(extra))

        alias_map = getattr(FF_C, "FAMILY_SUPPORT_ALIAS_MAP", {})
        inverted_alias_map = getattr(FF_C, "FAMILY_SUPPORT_INVERTED_ALIAS_MAP", {})

        family_aliases = dict(alias_map.get(family_id, {})) if isinstance(alias_map, Mapping) else {}
        family_inverted_aliases = (
            dict(inverted_alias_map.get(family_id, {}))
            if isinstance(inverted_alias_map, Mapping)
            else {}
        )

        for canonical_key in out:
            if canonical_key in rich_map:
                out[canonical_key] = _safe_bool(rich_map[canonical_key], False)
                continue

            for alias in family_aliases.get(canonical_key, ()):
                if alias in rich_map:
                    out[canonical_key] = _safe_bool(rich_map[alias], False)
                    break

            if out[canonical_key]:
                continue

            for alias in family_inverted_aliases.get(canonical_key, ()):
                if alias in rich_map:
                    out[canonical_key] = not _safe_bool(rich_map[alias], False)
                    break

        return out

    def _bool_support(
        self,
        template: Mapping[str, Any],
        rich: Mapping[str, Any],
    ) -> dict[str, bool]:
        # Compatibility wrapper retained for older tests only. Runtime code uses
        # _canonical_support(family_id, ...) so aliases and negative flags are
        # family-specific.
        out: dict[str, bool] = {
            key: bool(value) for key, value in template.items() if isinstance(value, bool)
        }
        rich_map = dict(_mapping(rich))
        for key in out:
            if key in rich_map:
                out[key] = _safe_bool(rich_map[key], False)
        return out

    def _active_zone_valid(
        self,
        active_zone: Mapping[str, Any],
        rich_family: Mapping[str, Any],
    ) -> bool:
        zone = dict(_mapping(active_zone))
        rich = dict(_mapping(rich_family))
        return bool(
            rich.get("active_zone_valid")
            or zone.get("zone_id")
            or zone.get("zone_type")
            or _safe_float(zone.get("quality_score"), 0.0) > 0.0
        )

    def _family_branch_eligible(
        self,
        family_id: str,
        support: Mapping[str, Any],
    ) -> bool:
        values = dict(_mapping(support))

        if family_id == FAMILY_MIST:
            return bool(
                values.get("trend_confirmed")
                and values.get("futures_impulse_ok")
                and values.get("pullback_detected")
                and values.get("resume_confirmed")
                and values.get("option_tradability_pass")
            )

        if family_id == FAMILY_MISB:
            return bool(
                values.get("shelf_confirmed")
                and values.get("breakout_triggered")
                and values.get("breakout_accepted")
                and values.get("option_tradability_pass")
            )

        if family_id == FAMILY_MISC:
            return bool(
                values.get("compression_detected")
                and values.get("directional_breakout_triggered")
                and values.get("expansion_accepted")
                and values.get("retest_monitor_active")
                and values.get("resume_confirmed")
                and values.get("option_tradability_pass")
            )

        if family_id == FAMILY_MISR:
            return bool(
                values.get("active_zone_valid")
                and values.get("fake_break_triggered")
                and values.get("absorption_pass")
                and values.get("range_reentry_confirmed")
                and values.get("flow_flip_confirmed")
                and values.get("hold_inside_range_proved")
                and values.get("no_mans_land_cleared")
                and values.get("reversal_impulse_confirmed")
                and values.get("option_tradability_pass")
            )

        if family_id == FAMILY_MISO:
            return bool(
                values.get("burst_detected")
                and values.get("aggression_ok")
                and values.get("tape_speed_ok")
                and values.get("imbalance_persist_ok")
                and not values.get("queue_reload_blocked")
                and values.get("futures_vwap_align_ok")
                and not values.get("futures_contradiction_blocked")
                and values.get("tradability_pass")
            )

        return False

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
            "option_context_status",
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
            "last_update_ns",
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
            "selected_call_context_json",
        )
    )
    has_selected_put = bool(
        _pick(
            ctx,
            "selected_put_instrument_key",
            "selected_put_option_symbol",
            "selected_put_option_token",
            "selected_put_dhan_security_id",
            "selected_put_context_json",
        )
    )

    ladder = None
    for key in (
        "option_chain_ladder_json",
        "strike_ladder_json",
        "strike_ladder",
        "strike_ladder_rows",
        "chain_rows",
        "option_chain",
        "chain",
        "rows",
        "ladder",
    ):
        parsed = _json_load(ctx.get(key), None)
        if isinstance(parsed, list):
            ladder = parsed
            break
        if isinstance(parsed, Mapping):
            parsed_rows = _json_load(_pick(parsed, "rows", "data", "records", "chain_rows"), None)
            if isinstance(parsed_rows, list):
                ladder = parsed_rows
                break

    has_ladder = isinstance(ladder, Sequence) and not isinstance(
        ladder,
        (str, bytes, bytearray),
    ) and len(ladder) > 0

    oi_wall = _json_load(_pick(ctx, "oi_wall_summary_json", "oi_wall_context", "oi_wall", "wall_context"), None)
    has_oi_wall = bool(oi_wall)

    fresh = bool(present and healthy and not stale)
    miso_context_ready = bool(fresh and has_ladder and has_oi_wall and (has_selected_call or has_selected_put))

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


def _batch26e_misc_state_context(shared_core: Mapping[str, Any], branch_id: str) -> dict[str, Any]:
    """Read optional MISC event/timing state from shared surfaces."""
    state = (
        _nested(shared_core, "misc_state", branch_id, default={})
        or _nested(shared_core, "family_state", "MISC", branch_id, default={})
        or _nested(shared_core, "family_state", "misc", branch_id, default={})
        or _nested(shared_core, "runtime_state", "MISC", branch_id, default={})
        or {}
    )
    state = state if isinstance(state, Mapping) else {}
    return {
        "compression_event_id": _safe_str(state.get("compression_event_id")) or None,
        "breakout_event_id": _safe_str(state.get("breakout_event_id")) or None,
        "retest_monitor_started_ts_ms": int(_safe_float(state.get("retest_monitor_started_ts_ms"), 0.0)) or None,
        "retest_elapsed_sec": _safe_float(state.get("retest_elapsed_sec"), 0.0),
        "hesitation_elapsed_sec": _safe_float(state.get("hesitation_elapsed_sec"), 0.0),
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



# ============================================================================
# Batch 26C MISO provider-readiness authority
# ============================================================================

def _batch26c_provider_id(value: Any) -> str:
    return _safe_str(value).strip().upper()


def _batch26c_provider_status_ready(value: Any) -> bool:
    if "_batch25h_provider_ready_status" in globals():
        try:
            return bool(_batch25h_provider_ready_status(value))  # type: ignore[name-defined]
        except Exception:
            pass
    if "_batch7_provider_usable" in globals():
        try:
            return bool(_batch7_provider_usable(value))  # type: ignore[name-defined]
        except Exception:
            pass

    status = _safe_str(value).strip().upper()
    return status in {"OK", "WARN", "HEALTHY", "AVAILABLE", "READY", "CURRENT", "1", "TRUE"}


def _batch26c_miso_dhan_futures_required(provider_runtime: Mapping[str, Any]) -> bool:
    explicit = (
        provider_runtime.get("miso_requires_dhan_futures")
        or provider_runtime.get("miso_require_dhan_futures")
        or provider_runtime.get("miso_dhan_futures_required")
        or provider_runtime.get("dhan_futures_required_for_miso")
        or provider_runtime.get("miso_dhan_futures_rollout_enabled")
    )
    if explicit is not None:
        return _safe_bool(explicit, False)

    rollout_mode = _safe_str(
        provider_runtime.get("miso_futures_rollout_mode")
        or provider_runtime.get("miso_provider_rollout_mode")
        or provider_runtime.get("provider_rollout_mode")
    ).strip().upper().replace("_", "-")
    return rollout_mode in {
        "DHAN-FUTURES",
        "DHAN-FUTURES-ONLY",
        "MISO-DHAN-FUTURES",
        "REQUIRE-DHAN-FUTURES",
    }


def _batch26c_miso_provider_ready(
    provider_runtime: Mapping[str, Any],
    *,
    miso_mode: Any,
    futures_present: bool = True,
    selected_option_present: bool = True,
    dhan_context_ready: bool = True,
    dhan_context_fresh: bool = True,
) -> bool:
    """Authoritative MISO provider-readiness law."""
    mode = _safe_str(miso_mode).strip().upper().replace("_", "-")
    disabled = _safe_str(RUNTIME_DISABLED).strip().upper().replace("_", "-")
    if not mode or mode == disabled:
        return False

    futures_provider = _batch26c_provider_id(
        provider_runtime.get("active_futures_provider_id")
        or provider_runtime.get("futures_marketdata_provider_id")
        or provider_runtime.get("futures_provider_id")
    )
    selected_provider = _batch26c_provider_id(
        provider_runtime.get("active_selected_option_provider_id")
        or provider_runtime.get("selected_option_marketdata_provider_id")
        or provider_runtime.get("selected_option_provider_id")
    )
    context_provider = _batch26c_provider_id(
        provider_runtime.get("active_option_context_provider_id")
        or provider_runtime.get("option_context_provider_id")
    )

    futures_status = (
        provider_runtime.get("futures_provider_status")
        or provider_runtime.get("futures_marketdata_status")
        or provider_runtime.get("active_futures_provider_status")
    )
    selected_status = (
        provider_runtime.get("selected_option_provider_status")
        or provider_runtime.get("selected_option_marketdata_status")
        or provider_runtime.get("active_selected_option_provider_status")
    )
    context_status = (
        provider_runtime.get("option_context_provider_status")
        or provider_runtime.get("option_context_status")
        or provider_runtime.get("active_option_context_provider_status")
    )

    futures_allowed = {
        getattr(N, "PROVIDER_ZERODHA", "ZERODHA"),
        getattr(N, "PROVIDER_DHAN", "DHAN"),
    }
    futures_ok = (
        futures_present
        and futures_provider in futures_allowed
        and _batch26c_provider_status_ready(futures_status)
    )

    if _batch26c_miso_dhan_futures_required(provider_runtime):
        futures_ok = (
            futures_present
            and futures_provider == getattr(N, "PROVIDER_DHAN", "DHAN")
            and _batch26c_provider_status_ready(futures_status)
        )

    selected_ok = (
        selected_option_present
        and selected_provider == getattr(N, "PROVIDER_DHAN", "DHAN")
        and _batch26c_provider_status_ready(selected_status)
    )
    context_ok = (
        dhan_context_ready
        and dhan_context_fresh
        and context_provider == getattr(N, "PROVIDER_DHAN", "DHAN")
        and _batch26c_provider_status_ready(context_status)
    )

    return bool(futures_ok and selected_ok and context_ok)



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
    provider_ready_miso = _batch26c_miso_provider_ready(
        provider_runtime,
        miso_mode=miso_mode,
        futures_present=futures_present,
        selected_option_present=selected_option_present,
        dhan_context_ready=bool(quality.get("miso_context_ready") is True),
        dhan_context_fresh=bool(quality.get("fresh")),
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


# ============================================================================
# Batch 25H provider-runtime producer/consumer repair
# ============================================================================
#
# Purpose
# -------
# Normalize provider runtime from the Batch 25G canonical contract fields and
# derive compatibility aliases for existing consumers.
#
# This patch does not:
# - select/fail over providers
# - promote strategies
# - arm execution
# - change feed or broker I/O
#
# Missing required provider-runtime signals become explicit blockers.

_BATCH25H_ORIGINAL_PROVIDER_RUNTIME = FeatureEngine._provider_runtime
_BATCH25H_ORIGINAL_CONTRACT_PROVIDER = FeatureEngine._contract_provider

_BATCH25H_CANONICAL_TO_COMPAT = {
    "futures_marketdata_provider_id": "active_futures_provider_id",
    "selected_option_marketdata_provider_id": "active_selected_option_provider_id",
    "option_context_provider_id": "active_option_context_provider_id",
    "execution_primary_provider_id": "active_execution_provider_id",
    "execution_fallback_provider_id": "fallback_execution_provider_id",
    "futures_marketdata_status": "futures_provider_status",
    "selected_option_marketdata_status": "selected_option_provider_status",
    "option_context_status": "option_context_provider_status",
    "execution_primary_status": "execution_provider_status",
}

_BATCH25H_CANONICAL_ALIASES = {
    "futures_marketdata_provider_id": (
        "active_futures_provider_id",
        "active_future_provider_id",
        "futures_provider_id",
    ),
    "selected_option_marketdata_provider_id": (
        "active_selected_option_provider_id",
        "selected_option_provider_id",
        "option_provider_id",
    ),
    "option_context_provider_id": (
        "active_option_context_provider_id",
        "option_context_provider_id",
        "context_provider_id",
    ),
    "execution_primary_provider_id": (
        "active_execution_provider_id",
        "execution_primary_provider_id",
        "execution_provider_id",
    ),
    "execution_fallback_provider_id": (
        "fallback_execution_provider_id",
        "execution_fallback_provider_id",
    ),
    "futures_marketdata_status": (
        "futures_provider_status",
        "active_futures_provider_status",
        "futures_provider_statu",
        "active_futures_provider_statu",
    ),
    "selected_option_marketdata_status": (
        "selected_option_provider_status",
        "active_selected_option_provider_status",
        "selected_option_provider_statu",
        "active_selected_option_provider_statu",
    ),
    "option_context_status": (
        "option_context_provider_status",
        "active_option_context_provider_status",
        "option_context_provider_statu",
        "active_option_context_provider_statu",
    ),
    "execution_primary_status": (
        "execution_provider_status",
        "active_execution_provider_status",
        "execution_provider_statu",
        "active_execution_provider_statu",
    ),
    "execution_fallback_status": (
        "execution_fallback_provider_status",
        "fallback_execution_provider_status",
    ),
}


def _batch25h_pick(mapping: Mapping[str, Any] | None, *keys: str, default: Any = None) -> Any:
    source = dict(mapping or {})
    for key in keys:
        value = source.get(key)
        if value not in (None, ""):
            return value
    return default


def _batch25h_str_or_none(value: Any) -> str | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    return text or None


def _batch25h_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value in (None, ""):
        return default
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return default


def _batch25h_int(value: Any, default: int = 0) -> int:
    if value in (None, ""):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _batch25h_status(value: Any) -> str:
    text = _batch25h_str_or_none(value)
    if text is None:
        return getattr(N, "PROVIDER_STATUS_UNAVAILABLE", "UNAVAILABLE")
    return text


def _batch25h_provider_ready_status(status: Any) -> bool:
    value = str(status or "").strip().upper()
    return value in {
        "OK",
        "READY",
        "HEALTHY",
        "DEGRADED",
        "LIVE",
        "AVAILABLE",
    }


def _batch25h_canonical_provider_runtime(raw: Mapping[str, Any] | None) -> dict[str, Any]:
    source = dict(raw or {})
    missing: list[str] = []

    def canonical_value(key: str) -> str | None:
        aliases = _BATCH25H_CANONICAL_ALIASES.get(key, ())
        value = _batch25h_str_or_none(_batch25h_pick(source, key, *aliases))
        if value is None:
            missing.append(key)
        return value

    def canonical_status(key: str) -> str:
        aliases = _BATCH25H_CANONICAL_ALIASES.get(key, ())
        value = _batch25h_pick(source, key, *aliases)
        if value in (None, ""):
            missing.append(key)
        return _batch25h_status(value)

    family_runtime_mode = _batch25h_str_or_none(
        _batch25h_pick(
            source,
            "family_runtime_mode",
            default=getattr(N, "FAMILY_RUNTIME_MODE_OBSERVE_ONLY", "observe_only"),
        )
    ) or getattr(N, "FAMILY_RUNTIME_MODE_OBSERVE_ONLY", "observe_only")

    out: dict[str, Any] = {
        "futures_marketdata_provider_id": canonical_value("futures_marketdata_provider_id"),
        "selected_option_marketdata_provider_id": canonical_value("selected_option_marketdata_provider_id"),
        "option_context_provider_id": canonical_value("option_context_provider_id"),
        "execution_primary_provider_id": canonical_value("execution_primary_provider_id"),
        "execution_fallback_provider_id": canonical_value("execution_fallback_provider_id"),
        "futures_marketdata_status": canonical_status("futures_marketdata_status"),
        "selected_option_marketdata_status": canonical_status("selected_option_marketdata_status"),
        "option_context_status": canonical_status("option_context_status"),
        "execution_primary_status": canonical_status("execution_primary_status"),
        "execution_fallback_status": canonical_status("execution_fallback_status"),
        "family_runtime_mode": family_runtime_mode,
        "failover_mode": _batch25h_str_or_none(_batch25h_pick(source, "failover_mode")) or "",
        "override_mode": _batch25h_str_or_none(_batch25h_pick(source, "override_mode")) or "",
        "transition_reason": _batch25h_str_or_none(_batch25h_pick(source, "transition_reason")) or "",
        "provider_transition_seq": _batch25h_int(_batch25h_pick(source, "provider_transition_seq"), 0),
        "failover_active": _batch25h_bool(_batch25h_pick(source, "failover_active"), False),
        "pending_failover": _batch25h_bool(_batch25h_pick(source, "pending_failover"), False),
    }

    for canonical, compat in _BATCH25H_CANONICAL_TO_COMPAT.items():
        out[compat] = out.get(canonical)

    out["provider_runtime_mode"] = (
        _batch25h_str_or_none(_batch25h_pick(source, "provider_runtime_mode", "runtime_mode"))
        or None
    )

    classic_ready = bool(
        out.get("futures_marketdata_provider_id")
        and out.get("selected_option_marketdata_provider_id")
        and _batch25h_provider_ready_status(out.get("futures_marketdata_status"))
        and _batch25h_provider_ready_status(out.get("selected_option_marketdata_status"))
    )

    futures_provider_ok = bool(
        out.get("futures_marketdata_provider_id") in {
            getattr(N, "PROVIDER_ZERODHA", "ZERODHA"),
            getattr(N, "PROVIDER_DHAN", "DHAN"),
        }
        and _batch25h_provider_ready_status(out.get("futures_marketdata_status"))
    )
    if _batch26c_miso_dhan_futures_required(out):
        futures_provider_ok = bool(
            out.get("futures_marketdata_provider_id") == getattr(N, "PROVIDER_DHAN", "DHAN")
            and _batch25h_provider_ready_status(out.get("futures_marketdata_status"))
        )

    miso_ready = bool(
        futures_provider_ok
        and out.get("selected_option_marketdata_provider_id") == getattr(N, "PROVIDER_DHAN", "DHAN")
        and _batch25h_provider_ready_status(out.get("selected_option_marketdata_status"))
        and out.get("option_context_provider_id") == getattr(N, "PROVIDER_DHAN", "DHAN")
        and _batch25h_provider_ready_status(out.get("option_context_status"))
    )

    out["provider_ready_classic"] = classic_ready
    out["provider_ready_miso"] = miso_ready
    out["provider_runtime_blocked"] = bool(missing)
    out["provider_runtime_missing_keys"] = tuple(dict.fromkeys(missing))
    out["provider_runtime_block_reason"] = (
        "missing_required_provider_runtime_keys:" + ",".join(out["provider_runtime_missing_keys"])
        if missing
        else ""
    )

    # Preserve original raw keys under no new authority. Canonical keys above win.
    for key, value in source.items():
        out.setdefault(key, value)

    return out


def _batch25h_provider_runtime(self: FeatureEngine, raw: Mapping[str, Any]) -> dict[str, Any]:
    return _batch25h_canonical_provider_runtime(raw)


def _batch25h_contract_provider(
    self: FeatureEngine,
    provider_runtime: Mapping[str, Any],
    shared_core: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {}
    try:
        original = _BATCH25H_ORIGINAL_CONTRACT_PROVIDER(self, provider_runtime, shared_core)
        if isinstance(original, Mapping):
            base.update(dict(original))
    except Exception as exc:
        base["provider_runtime_original_error"] = str(exc)

    canonical = _batch25h_canonical_provider_runtime({**dict(base), **dict(provider_runtime)})
    out = dict(base)
    out.update(canonical)

    return out


FeatureEngine._provider_runtime = _batch25h_provider_runtime
FeatureEngine._contract_provider = _batch25h_contract_provider


# ============================================================================
# Batch 25H-C final provider-runtime method binding
# ============================================================================

_BATCH25HC_CANONICAL_TO_COMPAT = {
    "futures_marketdata_provider_id": "active_futures_provider_id",
    "selected_option_marketdata_provider_id": "active_selected_option_provider_id",
    "option_context_provider_id": "active_option_context_provider_id",
    "execution_primary_provider_id": "active_execution_provider_id",
    "execution_fallback_provider_id": "fallback_execution_provider_id",
    "futures_marketdata_status": "futures_provider_status",
    "selected_option_marketdata_status": "selected_option_provider_status",
    "option_context_status": "option_context_provider_status",
    "execution_primary_status": "execution_provider_status",
    "execution_fallback_status": "execution_fallback_provider_status",
}

_BATCH25HC_ALIASES = {
    "futures_marketdata_provider_id": (
        "active_futures_provider_id",
        "active_future_provider_id",
        "futures_provider_id",
    ),
    "selected_option_marketdata_provider_id": (
        "active_selected_option_provider_id",
        "selected_option_provider_id",
        "option_provider_id",
    ),
    "option_context_provider_id": (
        "active_option_context_provider_id",
        "context_provider_id",
    ),
    "execution_primary_provider_id": (
        "active_execution_provider_id",
        "execution_provider_id",
    ),
    "execution_fallback_provider_id": (
        "fallback_execution_provider_id",
    ),
    "futures_marketdata_status": (
        "futures_provider_status",
        "active_futures_provider_status",
        "futures_provider_statu",
    ),
    "selected_option_marketdata_status": (
        "selected_option_provider_status",
        "active_selected_option_provider_status",
        "selected_option_provider_statu",
    ),
    "option_context_status": (
        "option_context_provider_status",
        "active_option_context_provider_status",
        "option_context_provider_statu",
    ),
    "execution_primary_status": (
        "execution_provider_status",
        "active_execution_provider_status",
        "execution_provider_statu",
    ),
    "execution_fallback_status": (
        "execution_fallback_provider_status",
        "fallback_execution_provider_status",
    ),
}


def _batch25hc_pick(source: Mapping[str, Any], key: str) -> Any:
    keys = (key, *_BATCH25HC_ALIASES.get(key, ()))
    for candidate in keys:
        value = source.get(candidate)
        if value not in (None, ""):
            return value
    return None


def _batch25hc_text_or_none(value: Any) -> str | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    return text or None


def _batch25hc_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value in (None, ""):
        return default
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return default


def _batch25hc_int(value: Any, default: int = 0) -> int:
    if value in (None, ""):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _batch25hc_unavailable() -> str:
    return getattr(N, "PROVIDER_STATUS_UNAVAILABLE", "UNAVAILABLE")


def _batch25hc_status(value: Any) -> str:
    return _batch25hc_text_or_none(value) or _batch25hc_unavailable()


def _batch25hc_ready_status(value: Any) -> bool:
    return str(value or "").strip().upper() in {
        "OK",
        "READY",
        "HEALTHY",
        "DEGRADED",
        "LIVE",
        "AVAILABLE",
    }


def _batch25hc_provider_runtime_from_raw(raw: Mapping[str, Any] | None) -> dict[str, Any]:
    source = dict(raw or {})
    missing: list[str] = []

    def required_text(key: str) -> str | None:
        value = _batch25hc_text_or_none(_batch25hc_pick(source, key))
        if value is None:
            missing.append(key)
        return value

    def required_status(key: str) -> str:
        raw_value = _batch25hc_pick(source, key)
        if raw_value in (None, ""):
            missing.append(key)
        return _batch25hc_status(raw_value)

    out: dict[str, Any] = {
        "futures_marketdata_provider_id": required_text("futures_marketdata_provider_id"),
        "selected_option_marketdata_provider_id": required_text("selected_option_marketdata_provider_id"),
        "option_context_provider_id": required_text("option_context_provider_id"),
        "execution_primary_provider_id": required_text("execution_primary_provider_id"),
        "execution_fallback_provider_id": required_text("execution_fallback_provider_id"),
        "futures_marketdata_status": required_status("futures_marketdata_status"),
        "selected_option_marketdata_status": required_status("selected_option_marketdata_status"),
        "option_context_status": required_status("option_context_status"),
        "execution_primary_status": required_status("execution_primary_status"),
        "execution_fallback_status": required_status("execution_fallback_status"),
        "family_runtime_mode": (
            _batch25hc_text_or_none(source.get("family_runtime_mode"))
            or getattr(N, "FAMILY_RUNTIME_MODE_OBSERVE_ONLY", "observe_only")
        ),
        "failover_mode": (
            _batch25hc_text_or_none(source.get("failover_mode"))
            or getattr(N, "PROVIDER_FAILOVER_MODE_MANUAL", "MANUAL")
        ),
        "override_mode": (
            _batch25hc_text_or_none(source.get("override_mode"))
            or getattr(N, "PROVIDER_OVERRIDE_MODE_AUTO", "AUTO")
        ),
        "transition_reason": (
            _batch25hc_text_or_none(source.get("transition_reason"))
            or getattr(N, "PROVIDER_TRANSITION_REASON_BOOTSTRAP", "BOOTSTRAP")
        ),
        "provider_transition_seq": _batch25hc_int(source.get("provider_transition_seq"), 0),
        "failover_active": _batch25hc_bool(source.get("failover_active"), False),
        "pending_failover": _batch25hc_bool(source.get("pending_failover"), False),
    }

    for canonical, compat in _BATCH25HC_CANONICAL_TO_COMPAT.items():
        out[compat] = out.get(canonical)

    out["provider_runtime_mode"] = _batch25hc_text_or_none(source.get("provider_runtime_mode"))

    classic_ready = bool(
        out["futures_marketdata_provider_id"]
        and out["selected_option_marketdata_provider_id"]
        and _batch25hc_ready_status(out["futures_marketdata_status"])
        and _batch25hc_ready_status(out["selected_option_marketdata_status"])
    )

    miso_ready = bool(
        classic_ready
        and out["option_context_provider_id"]
        and _batch25hc_ready_status(out["option_context_status"])
    )

    out["provider_ready_classic"] = classic_ready
    out["provider_ready_miso"] = miso_ready
    out["provider_runtime_missing_keys"] = tuple(dict.fromkeys(missing))
    out["provider_runtime_blocked"] = bool(out["provider_runtime_missing_keys"])
    out["provider_runtime_block_reason"] = (
        "missing_required_provider_runtime_keys:" + ",".join(out["provider_runtime_missing_keys"])
        if out["provider_runtime_missing_keys"]
        else ""
    )

    for key, value in source.items():
        out.setdefault(key, value)

    return out


def _batch25hc_provider_runtime(self: FeatureEngine, raw: Mapping[str, Any]) -> dict[str, Any]:
    return _batch25hc_provider_runtime_from_raw(raw)


def _batch25hc_contract_provider(
    self: FeatureEngine,
    provider_runtime: Mapping[str, Any],
    shared_core: Mapping[str, Any],
) -> dict[str, Any]:
    return _batch25hc_provider_runtime_from_raw(provider_runtime)


FeatureEngine._provider_runtime = _batch25hc_provider_runtime
FeatureEngine._contract_provider = _batch25hc_contract_provider


# Batch 25L corrective — option surface keyword ABI compatibility
#
# Some older Batch-7 wrapper assignments may leave FeatureEngine._option_surface
# with a positional-only ABI. Batch 25I/25L service path calls it with
# side=/role=/provider_id=. This final wrapper preserves the previous
# implementation when it accepts the keyword ABI and falls back only for the
# unexpected-keyword case.
_BATCH25L_PREV_OPTION_SURFACE = FeatureEngine._option_surface


def _batch25l_option_surface_kw_compat(
    self: FeatureEngine,
    raw: Mapping[str, Any] | None = None,
    *args: Any,
    side: str | None = None,
    role: str | None = None,
    provider_id: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Batch 25K-J runtime-wrapper repair.

    This function is the effective runtime FeatureEngine._option_surface after
    Batch25L monkeypatching. It must also exercise the shared option_core
    builder ABI, otherwise the class-method repair is bypassed.

    Required ABI:
        option_core.build_live_option_surface(
            side=...,
            live_source=...,
            provider_id=...,
            strike=...,
            instrument_key=...,
            instrument_token=...
        )
    """

    raw_map = dict(raw or {})

    def _resolve_side(surface: Mapping[str, Any], member_key: str | None = None) -> str:
        direct = _feed_side(
            side
            or kwargs.get("option_side")
            or kwargs.get("side")
            or surface.get("side")
            or surface.get("option_side")
            or surface.get("right")
            or surface.get("option_type")
        )
        if direct in {"CALL", "PUT"}:
            return direct

        probe = " ".join(
            str(x or "")
            for x in (
                role,
                member_key,
                surface.get("role"),
                surface.get("instrument_key"),
                surface.get("instrument_token"),
                surface.get("trading_symbol"),
                surface.get("option_symbol"),
                surface.get("symbol"),
            )
        ).upper()

        if "PUT" in probe or " PE" in f" {probe} " or probe.endswith("PE") or "_PE" in probe or "-PE" in probe:
            return "PUT"
        if "CALL" in probe or " CE" in f" {probe} " or probe.endswith("CE") or "_CE" in probe or "-CE" in probe:
            return "CALL"
        return ""

    def _builder_preview(surface: Mapping[str, Any], *, resolved_side: str, resolved_provider_id: str) -> dict[str, Any] | None:
        if resolved_side not in {"CALL", "PUT"}:
            return None

        option_core_module = None
        try:
            option_core_module = self.shared_modules.get("option_core")
        except Exception:
            option_core_module = None

        if option_core_module is None:
            option_core_module = _batch25kj_option_core

        built = _call_exact_builder(
            option_core_module,
            "build_live_option_surface",
            audit_key="option_core_builder_used",
            fallback_allowed=False,
            side=resolved_side,
            live_source=surface,
            provider_id=resolved_provider_id,
            strike=_pick(surface, "strike", "strike_price", "strikePrice"),
            instrument_key=_feed_instrument_key(surface),
            instrument_token=_feed_token(surface),
        )

        if not isinstance(built, Mapping):
            return None

        out = dict(built)
        out.setdefault("present", True)
        out.setdefault("valid", True)
        out.setdefault("side", resolved_side)
        out.setdefault("option_side", resolved_side)
        out.setdefault("role", role or _safe_str(_pick(surface, "role"), "SELECTED_OPTION"))
        out.setdefault("provider_id", resolved_provider_id)
        out.setdefault("instrument_key", _feed_instrument_key(surface))
        out.setdefault("instrument_token", _feed_token(surface))
        out.setdefault("option_token", _feed_token(surface))
        out.setdefault("trading_symbol", _feed_trading_symbol(surface))
        out.setdefault("option_symbol", _feed_trading_symbol(surface))
        out.setdefault("strike", _safe_float_or_none(_pick(surface, "strike", "strike_price", "strikePrice")))
        out.setdefault("raw", surface)
        return out

    # First, try the previous option-surface implementation. If it returns a
    # usable surface, still route the returned surface through the exact shared
    # option_core builder so the ABI proof observes the real builder path.
    try:
        previous = _BATCH25L_PREV_OPTION_SURFACE(
            self,
            raw,
            *args,
            side=side,
            role=role,
            provider_id=provider_id,
            **kwargs,
        )
        previous_map = dict(previous) if isinstance(previous, Mapping) else {}
        if previous_map:
            resolved_side = _resolve_side(previous_map)
            resolved_provider_id = _feed_provider_id(previous_map, provider_id)
            built = _builder_preview(
                previous_map,
                resolved_side=resolved_side,
                resolved_provider_id=resolved_provider_id,
            )
            if isinstance(built, Mapping):
                return built
            return previous_map
    except TypeError as exc:
        message = str(exc)
        unexpected_kw = (
            "unexpected keyword argument 'side'" in message
            or "unexpected keyword argument 'role'" in message
            or "unexpected keyword argument 'provider_id'" in message
        )
        if not unexpected_kw:
            raise

    requested_side = _feed_side(
        side
        or kwargs.get("option_side")
        or kwargs.get("side")
        or raw_map.get("side")
        or raw_map.get("option_side")
    )

    if requested_side == "CALL":
        member_key, member = _feed_first_member(raw_map, _FEED_CALL_JSON_KEYS)
    elif requested_side == "PUT":
        member_key, member = _feed_first_member(raw_map, _FEED_PUT_JSON_KEYS)
    else:
        member_key, member = _feed_first_member(
            raw_map,
            (*_FEED_CALL_JSON_KEYS, *_FEED_PUT_JSON_KEYS),
        )

    surface = _feed_merge_member(raw_map, member) if member else raw_map
    resolved_side = (
        requested_side
        or _resolve_side(surface, member_key)
        or ("CALL" if member_key in _FEED_CALL_JSON_KEYS else "PUT" if member_key in _FEED_PUT_JSON_KEYS else "")
    )

    resolved_provider_id = _feed_provider_id(surface, provider_id)

    built = _builder_preview(
        surface,
        resolved_side=resolved_side,
        resolved_provider_id=resolved_provider_id,
    )
    if isinstance(built, Mapping):
        return built

    bid = _feed_best_price(surface, "bid")
    ask = _feed_best_price(surface, "ask")
    bid_qty_5 = _feed_depth_qty(surface, "bid")
    ask_qty_5 = _feed_depth_qty(surface, "ask")
    ltp = _feed_ltp(surface)
    depth_total = bid_qty_5 + ask_qty_5
    spread = max(0.0, ask - bid) if ask > 0.0 and bid > 0.0 else 0.0
    strike = _safe_float_or_none(_pick(surface, "strike", "strike_price", "strikePrice"))

    present = bool(ltp > 0.0 or bid > 0.0 or ask > 0.0 or depth_total > 0.0)
    valid = bool(present and resolved_side in {"CALL", "PUT"} and strike is not None)

    return {
        "present": present,
        "valid": valid,
        "side": resolved_side,
        "option_side": resolved_side,
        "role": role or _safe_str(_pick(surface, "role"), "SELECTED_OPTION"),
        "provider_id": resolved_provider_id,
        "instrument_key": _feed_instrument_key(surface),
        "instrument_token": _feed_token(surface),
        "option_token": _feed_token(surface),
        "trading_symbol": _feed_trading_symbol(surface),
        "option_symbol": _feed_trading_symbol(surface),
        "strike": strike,
        "ltp": ltp,
        "best_bid": bid,
        "best_ask": ask,
        "bid": bid,
        "ask": ask,
        "bid_qty": bid_qty_5,
        "ask_qty": ask_qty_5,
        "bid_qty_5": bid_qty_5,
        "ask_qty_5": ask_qty_5,
        "depth_total": depth_total,
        "spread": spread,
        "spread_ratio": _safe_float(_pick(surface, "spread_ratio"), 0.0),
        "volume": _safe_float(_pick(surface, "volume", "traded_volume"), 0.0),
        "oi": _safe_float(_pick(surface, "oi", "open_interest"), 0.0),
        "oi_change": _safe_float(_pick(surface, "oi_change", "change_oi"), 0.0),
        "iv": _safe_float_or_none(_pick(surface, "iv", "implied_volatility")),
        "delta": _safe_float_or_none(_pick(surface, "delta", "option_delta")),
        "tradability_ok": bool(valid and ltp > 0.0 and bid > 0.0 and ask > 0.0 and depth_total > 0.0),
        "ts_event_ns": _safe_int(_pick(surface, "ts_event_ns", "event_ts_ns", "timestamp_ns"), 0),
        "source_member_key": member_key,
        "raw": surface,
    }


FeatureEngine._option_surface = _batch25l_option_surface_kw_compat


# Batch 25L corrective 3 — futures surface feed-json compatibility
#
# Later wrapper assignments may route FeatureEngine._futures_surface through an
# older fallback path that ignores future_json and bid_qty_5/ask_qty_5. This
# final wrapper preserves the previous implementation when it correctly consumes
# feed-shaped futures, and repairs only the feed-json/depth-loss case.
_BATCH25L_PREV_FUTURES_SURFACE = FeatureEngine._futures_surface


def _batch25l_futures_surface_feed_json_compat(
    self: FeatureEngine,
    raw: Mapping[str, Any] | None = None,
    *args: Any,
    role: str | None = None,
    provider_id: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    raw_map = dict(raw or {})

    result: dict[str, Any] = {}
    try:
        prev = _BATCH25L_PREV_FUTURES_SURFACE(
            self,
            raw,
            *args,
            role=role,
            provider_id=provider_id,
            **kwargs,
        )
        result = dict(prev) if isinstance(prev, Mapping) else {}
    except TypeError as exc:
        message = str(exc)
        unexpected_kw = (
            "unexpected keyword argument 'role'" in message
            or "unexpected keyword argument 'provider_id'" in message
        )
        if not unexpected_kw:
            raise

    has_feed_future_json = any(bool(raw_map.get(key)) for key in _FEED_FUTURE_JSON_KEYS)
    previous_depth = _safe_float(result.get("depth_total"), 0.0)
    previous_source = _safe_str(result.get("source_member_key"))

    if result and not has_feed_future_json:
        return result

    if result and has_feed_future_json and previous_depth > 0.0 and previous_source:
        return result

    member_key, member = _feed_first_member(raw_map, _FEED_FUTURE_JSON_KEYS)
    surface = _feed_merge_member(raw_map, member) if member else raw_map

    bid = _feed_best_price(surface, "bid")
    ask = _feed_best_price(surface, "ask")
    bid_qty_5 = _feed_depth_qty(surface, "bid")
    ask_qty_5 = _feed_depth_qty(surface, "ask")
    ltp = _feed_ltp(surface)
    depth_total = bid_qty_5 + ask_qty_5

    present = bool(ltp > 0.0 or bid > 0.0 or ask > 0.0 or depth_total > 0.0)
    valid = bool(present and depth_total > 0.0)

    repaired = {
        "present": present,
        "valid": valid,
        "role": role or _safe_str(_pick(surface, "role"), "FUTURE"),
        "provider_id": _feed_provider_id(surface, provider_id),
        "instrument_key": _feed_instrument_key(surface),
        "instrument_token": _feed_token(surface),
        "trading_symbol": _feed_trading_symbol(surface),
        "ltp": ltp,
        "best_bid": bid,
        "best_ask": ask,
        "bid": bid,
        "ask": ask,
        "bid_qty": bid_qty_5,
        "ask_qty": ask_qty_5,
        "bid_qty_5": bid_qty_5,
        "ask_qty_5": ask_qty_5,
        "depth_total": depth_total,
        "spread": max(0.0, ask - bid) if ask > 0.0 and bid > 0.0 else 0.0,
        "volume": _safe_float(_pick(surface, "volume", "traded_volume"), 0.0),
        "ts_event_ns": _safe_int(_pick(surface, "ts_event_ns", "event_ts_ns", "timestamp_ns"), 0),
        "source_member_key": member_key,
        "raw": surface,
    }

    # Preserve any additional non-conflicting fields from the previous surface.
    for key, value in result.items():
        repaired.setdefault(key, value)

    return repaired


FeatureEngine._futures_surface = _batch25l_futures_surface_feed_json_compat


# Batch 25L corrective 4B — restore family branch and surfaces
#
# Prior 25L patch/rebind order left FeatureEngine without _family_branch_surface,
# while build_payload() still requires _family_surfaces(). This restores the
# service-path branch/root/surfaces bindings explicitly. No provider selection,
# strategy promotion, risk, execution, broker, or Redis ownership behavior is changed.

def _batch25l_family_branch_surface_restored(
    self: FeatureEngine,
    family_id: str,
    branch_id: str,
    module: Any | None,
    shared_core: Mapping[str, Any],
    *,
    provider_runtime: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    side = _branch_side(branch_id)
    option = self._branch_option_surface(branch_id, shared_core)
    futures = self._branch_futures_surface(family_id, shared_core)
    regime = dict(_nested(shared_core, "regime", default={}))
    tradability = self._branch_tradability_surface(family_id, branch_id, shared_core)
    strike = self._branch_strike_surface(family_id, branch_id, shared_core)
    runtime_surface = self._branch_runtime_mode_surface(family_id, shared_core)
    runtime_mode = _safe_str(_pick(runtime_surface, "runtime_mode", "mode"), RUNTIME_DISABLED)

    surface = self._call_family_branch_builder(
        family_id,
        branch_id,
        module,
        shared_core,
        provider_runtime or {},
    )
    surface = dict(surface) if isinstance(surface, Mapping) else {}

    family_lc = family_id.lower()
    surface.update(
        {
            "surface_kind": surface.get("surface_kind") or f"{family_lc}_branch",
            "family_id": family_id,
            "branch_id": branch_id,
            "side": side,
            "runtime_mode": surface.get("runtime_mode") or runtime_mode,
            "runtime_mode_surface": surface.get("runtime_mode_surface") or runtime_surface,
            "present": bool(
                surface.get("present")
                or option.get("present")
                or option.get("instrument_key")
            ),
            "futures_features": surface.get("futures_features") or futures,
            "selected_features": surface.get("selected_features") or option,
            "option_features": surface.get("option_features") or option,
            "strike_surface": surface.get("strike_surface") or strike,
            "tradability": surface.get("tradability") or tradability,
            "tradability_surface": surface.get("tradability_surface") or tradability,
            "regime_surface": surface.get("regime_surface") or regime,
            "oi_wall_context": surface.get("oi_wall_context")
            or strike.get("oi_wall_context")
            or _nested(
                shared_core,
                "oi_wall_context",
                "call" if side == SIDE_CALL else "put",
                default={},
            ),
            "cross_option_context": surface.get("cross_option_context")
            or _nested(shared_core, "options", "cross_option", default={}),
            "provider_ready": bool(
                surface.get("provider_ready")
                if "provider_ready" in surface
                else self._family_provider_ready(
                    family_id,
                    branch_id,
                    provider_runtime or {},
                    shared_core,
                )
            ),
        }
    )

    # 25M owns canonical eligibility truth. 25L only proves rich service-path surfaces.
    surface.setdefault("eligible", bool(surface.get("branch_ready") or surface.get("ready")))
    surface.setdefault("rich_surface", True)
    return surface


def _batch25l_family_surface_restored(
    self: FeatureEngine,
    family_id: str,
    module: Any | None,
    branches: Mapping[str, Mapping[str, Any]],
    shared_core: Mapping[str, Any],
) -> dict[str, Any]:
    call_surface = dict(branches.get(BRANCH_CALL, {}))
    put_surface = dict(branches.get(BRANCH_PUT, {}))

    surface = self._call_family_root_builder(
        family_id,
        module,
        branches,
        shared_core,
    )
    surface = dict(surface) if isinstance(surface, Mapping) else {}

    surface.setdefault("family_id", family_id)
    surface.setdefault("surface_kind", f"{family_id.lower()}_family")
    surface.setdefault("eligible", bool(call_surface.get("eligible") or put_surface.get("eligible")))
    surface.setdefault("branches", {BRANCH_CALL: call_surface, BRANCH_PUT: put_surface})
    surface.setdefault("call", call_surface)
    surface.setdefault("put", put_surface)
    surface.setdefault(
        "runtime_mode_surface",
        self._branch_runtime_mode_surface(family_id, shared_core),
    )
    surface.setdefault("regime_surface", dict(_nested(shared_core, "regime", default={})))
    surface.setdefault("rich_surface", True)

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


def _batch25l_family_surfaces_restored(
    self: FeatureEngine,
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
            branch_surface = self._family_branch_surface(
                family_id,
                branch_id,
                module,
                shared_core,
                provider_runtime=provider_runtime,
            )
            branch_surface = dict(branch_surface) if isinstance(branch_surface, Mapping) else {}
            branches[branch_id] = branch_surface
            surfaces_by_branch[f"{family_id.lower()}_{branch_id.lower()}"] = branch_surface

        root_surface = self._family_surface(
            family_id,
            module,
            branches,
            shared_core,
        )
        families[family_id] = dict(root_surface) if isinstance(root_surface, Mapping) else {}

    return {
        "schema_version": getattr(N, "DEFAULT_SCHEMA_VERSION", 1),
        "surface_version": "family_surfaces.v25l",
        "service": SERVICE_FEATURES,
        "generated_at_ns": generated_at_ns,
        "provider_runtime": dict(provider_runtime),
        "shared_core": shared_core,
        "families": families,
        "surfaces_by_branch": surfaces_by_branch,
        "builder_abi_audit": _builder_abi_audit_snapshot(),
        "contract_note": "rich feature support only; family_features remains contracts.py exact-key payload",
    }


FeatureEngine._family_branch_surface = _batch25l_family_branch_surface_restored
FeatureEngine._family_surface = _batch25l_family_surface_restored
FeatureEngine._family_surfaces = _batch25l_family_surfaces_restored


# Batch 25L corrective 5 — normalize branch surface_kind
#
# Family branch builders may return generic surface_kind values such as "mist".
# The service-path contract needs branch surfaces to expose a branch-specific
# kind, e.g. "mist_branch", while retaining the original builder label for audit.
_BATCH25L_PREV_FAMILY_BRANCH_SURFACE = FeatureEngine._family_branch_surface


def _batch25l_family_branch_surface_kind_normalized(
    self: FeatureEngine,
    family_id: str,
    branch_id: str,
    module: Any | None,
    shared_core: Mapping[str, Any],
    *,
    provider_runtime: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    surface = _BATCH25L_PREV_FAMILY_BRANCH_SURFACE(
        self,
        family_id,
        branch_id,
        module,
        shared_core,
        provider_runtime=provider_runtime,
    )
    out = dict(surface) if isinstance(surface, Mapping) else {}

    expected_kind = f"{family_id.lower()}_branch"
    existing_kind = _safe_str(out.get("surface_kind"))

    if existing_kind and existing_kind != expected_kind:
        out.setdefault("builder_surface_kind", existing_kind)

    out["surface_kind"] = expected_kind
    out["family_id"] = family_id
    out["branch_id"] = branch_id
    out["side"] = _branch_side(branch_id)
    out["rich_surface"] = True

    return out


FeatureEngine._family_branch_surface = _batch25l_family_branch_surface_kind_normalized


# Batch 25M corrective 2 — branch-strict canonical family support
#
# MISR active_zone_valid is a root/context truth, but it must not make an
# inactive sibling branch look partially active. The branch gets active_zone_valid
# only when that branch also carries at least one branch-local setup signal.
# MISC proof also now covers hesitation_ok -> hesitation_valid.

def _batch25m_branch_has_any_setup_signal(
    family_id: str,
    rich: Mapping[str, Any],
) -> bool:
    rich_map = dict(_mapping(rich))
    if not rich_map:
        return False

    alias_map = getattr(FF_C, "FAMILY_SUPPORT_ALIAS_MAP", {})
    inverted_alias_map = getattr(FF_C, "FAMILY_SUPPORT_INVERTED_ALIAS_MAP", {})

    family_aliases = dict(alias_map.get(family_id, {})) if isinstance(alias_map, Mapping) else {}
    family_inverted_aliases = (
        dict(inverted_alias_map.get(family_id, {}))
        if isinstance(inverted_alias_map, Mapping)
        else {}
    )

    candidate_keys: set[str] = set()
    for canonical_key, aliases in family_aliases.items():
        if canonical_key != "context_pass":
            candidate_keys.add(canonical_key)
            candidate_keys.update(str(alias) for alias in aliases)

    for canonical_key, aliases in family_inverted_aliases.items():
        candidate_keys.add(canonical_key)
        candidate_keys.update(str(alias) for alias in aliases)

    # Do not let active_zone_valid alone mark both MISR branches active when it
    # was injected from root active_zone. Branch-local trap/reentry/proof signals
    # must also exist.
    if family_id == FAMILY_MISR:
        candidate_keys.discard("active_zone_valid")
        candidate_keys.discard("zone_valid")
        candidate_keys.discard("active_zone_ready")

    return any(_safe_bool(rich_map.get(key), False) for key in candidate_keys if key in rich_map)


def _batch25m_contract_families_branch_strict(
    self: FeatureEngine,
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

            call_support = self._canonical_support(
                family_id,
                _empty_builder("build_empty_miso_side_support"),
                call_surface,
            )
            put_support = self._canonical_support(
                family_id,
                _empty_builder("build_empty_miso_side_support"),
                put_surface,
            )

            _patch_existing(
                family_block,
                {
                    "eligible": bool(
                        self._family_branch_eligible(family_id, call_support)
                        or self._family_branch_eligible(family_id, put_support)
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
                    "call_support": call_support,
                    "put_support": put_support,
                },
            )

        elif family_id == FAMILY_MISR:
            branches = dict(family_block.get("branches", {}))
            active_zone = self._active_zone(_nested(rich_family, "active_zone", default={}))
            active_zone_valid = self._active_zone_valid(active_zone, rich_family)

            call_rich = dict(_mapping(_nested(rich_family, "branches", BRANCH_CALL, default={})))
            put_rich = dict(_mapping(_nested(rich_family, "branches", BRANCH_PUT, default={})))

            call_support = self._canonical_support(
                family_id,
                _empty_builder("build_empty_misr_branch_support"),
                call_rich,
                extra={
                    "active_zone_valid": bool(
                        active_zone_valid
                        and _batch25m_branch_has_any_setup_signal(family_id, call_rich)
                    )
                },
            )
            put_support = self._canonical_support(
                family_id,
                _empty_builder("build_empty_misr_branch_support"),
                put_rich,
                extra={
                    "active_zone_valid": bool(
                        active_zone_valid
                        and _batch25m_branch_has_any_setup_signal(family_id, put_rich)
                    )
                },
            )

            branches[BRANCH_CALL] = call_support
            branches[BRANCH_PUT] = put_support

            _patch_existing(
                family_block,
                {
                    "eligible": bool(
                        self._family_branch_eligible(family_id, call_support)
                        or self._family_branch_eligible(family_id, put_support)
                    ),
                    "active_zone": active_zone,
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
            call_support = self._canonical_support(
                family_id,
                _empty_builder(builder),
                _nested(rich_family, "branches", BRANCH_CALL, default={}),
            )
            put_support = self._canonical_support(
                family_id,
                _empty_builder(builder),
                _nested(rich_family, "branches", BRANCH_PUT, default={}),
            )

            branches[BRANCH_CALL] = call_support
            branches[BRANCH_PUT] = put_support

            _patch_existing(
                family_block,
                {
                    "eligible": bool(
                        self._family_branch_eligible(family_id, call_support)
                        or self._family_branch_eligible(family_id, put_support)
                    ),
                    "branches": branches,
                },
            )

        families[family_id] = family_block

    FF_C.validate_families_block(families)
    return families


FeatureEngine._contract_families = _batch25m_contract_families_branch_strict


# ============================================================================
# Batch 26H — final effective FeatureEngine family-surface consolidation
# ============================================================================
#
# Final binding after older Batch-25/26 wrapper assignments. It captures the
# current effective methods, preserves earlier functional fixes, and normalizes
# final runtime output into one Batch 26H family-surface contract.

_BATCH26H_PREV_FAMILY_BRANCH_SURFACE = FeatureEngine._family_branch_surface
_BATCH26H_PREV_FAMILY_SURFACE = FeatureEngine._family_surface
_BATCH26H_PREV_FAMILY_SURFACES = FeatureEngine._family_surfaces


def _batch26h_expected_branch_surface_kind(family_id: str) -> str:
    return f"{str(family_id).strip().lower()}_branch"


def _batch26h_expected_family_surface_kind(family_id: str) -> str:
    return f"{str(family_id).strip().lower()}_family"


def _batch26h_finalize_branch_surface(
    *,
    family_id: str,
    branch_id: str,
    surface: Mapping[str, Any],
) -> dict[str, Any]:
    out = dict(surface) if isinstance(surface, Mapping) else {}

    expected_kind = _batch26h_expected_branch_surface_kind(family_id)
    existing_kind = _safe_str(out.get("surface_kind"))

    if existing_kind and existing_kind != expected_kind:
        out.setdefault("builder_surface_kind", existing_kind)

    out["surface_kind"] = expected_kind
    out["family_id"] = family_id
    out["branch_id"] = branch_id
    out["side"] = _branch_side(branch_id)
    out["rich_surface"] = True
    return out


def _batch26h_finalize_family_surface(
    *,
    family_id: str,
    surface: Mapping[str, Any],
    branches: Mapping[str, Mapping[str, Any]],
    shared_core: Mapping[str, Any],
    engine: FeatureEngine,
) -> dict[str, Any]:
    call_surface = _batch26h_finalize_branch_surface(
        family_id=family_id,
        branch_id=BRANCH_CALL,
        surface=branches.get(BRANCH_CALL, {}),
    )
    put_surface = _batch26h_finalize_branch_surface(
        family_id=family_id,
        branch_id=BRANCH_PUT,
        surface=branches.get(BRANCH_PUT, {}),
    )

    out = dict(surface) if isinstance(surface, Mapping) else {}
    expected_kind = _batch26h_expected_family_surface_kind(family_id)
    existing_kind = _safe_str(out.get("surface_kind"))

    if existing_kind and existing_kind != expected_kind:
        out.setdefault("builder_surface_kind", existing_kind)

    out["surface_kind"] = expected_kind
    out["family_id"] = family_id
    out["branches"] = {BRANCH_CALL: call_surface, BRANCH_PUT: put_surface}
    out["call"] = call_surface
    out["put"] = put_surface
    out["eligible"] = bool(call_surface.get("eligible") or put_surface.get("eligible"))
    out.setdefault(
        "runtime_mode_surface",
        engine._branch_runtime_mode_surface(family_id, shared_core),
    )
    out.setdefault("regime_surface", dict(_nested(shared_core, "regime", default={})))
    out["rich_surface"] = True
    return out


def _batch26h_final_family_branch_surface(
    self: FeatureEngine,
    family_id: str,
    branch_id: str,
    module: Any | None,
    shared_core: Mapping[str, Any],
    *,
    provider_runtime: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    surface = _BATCH26H_PREV_FAMILY_BRANCH_SURFACE(
        self,
        family_id,
        branch_id,
        module,
        shared_core,
        provider_runtime=provider_runtime,
    )
    return _batch26h_finalize_branch_surface(
        family_id=family_id,
        branch_id=branch_id,
        surface=surface,
    )


def _batch26h_final_family_surface(
    self: FeatureEngine,
    family_id: str,
    module: Any | None,
    branches: Mapping[str, Mapping[str, Any]],
    shared_core: Mapping[str, Any],
) -> dict[str, Any]:
    normalized_branches = {
        BRANCH_CALL: _batch26h_finalize_branch_surface(
            family_id=family_id,
            branch_id=BRANCH_CALL,
            surface=branches.get(BRANCH_CALL, {}),
        ),
        BRANCH_PUT: _batch26h_finalize_branch_surface(
            family_id=family_id,
            branch_id=BRANCH_PUT,
            surface=branches.get(BRANCH_PUT, {}),
        ),
    }

    surface = _BATCH26H_PREV_FAMILY_SURFACE(
        self,
        family_id,
        module,
        normalized_branches,
        shared_core,
    )
    return _batch26h_finalize_family_surface(
        family_id=family_id,
        surface=surface,
        branches=normalized_branches,
        shared_core=shared_core,
        engine=self,
    )


def _batch26h_final_family_surfaces(
    self: FeatureEngine,
    *,
    generated_at_ns: int,
    provider_runtime: Mapping[str, Any],
    shared_core: Mapping[str, Any],
) -> dict[str, Any]:
    raw = _BATCH26H_PREV_FAMILY_SURFACES(
        self,
        generated_at_ns=generated_at_ns,
        provider_runtime=provider_runtime,
        shared_core=shared_core,
    )
    out = dict(raw) if isinstance(raw, Mapping) else {}

    families_in = dict(out.get("families", {}))
    surfaces_by_branch_in = dict(out.get("surfaces_by_branch", {}))

    families: dict[str, dict[str, Any]] = {}
    surfaces_by_branch: dict[str, dict[str, Any]] = {}

    for family_id in FAMILY_IDS:
        family_map = dict(families_in.get(family_id, {}))
        branch_source = family_map.get("branches", {})
        branch_source = branch_source if isinstance(branch_source, Mapping) else {}

        call_key = f"{family_id.lower()}_{BRANCH_CALL.lower()}"
        put_key = f"{family_id.lower()}_{BRANCH_PUT.lower()}"

        call_branch = dict(branch_source.get(BRANCH_CALL) or surfaces_by_branch_in.get(call_key) or {})
        put_branch = dict(branch_source.get(BRANCH_PUT) or surfaces_by_branch_in.get(put_key) or {})

        branches = {
            BRANCH_CALL: _batch26h_finalize_branch_surface(
                family_id=family_id,
                branch_id=BRANCH_CALL,
                surface=call_branch,
            ),
            BRANCH_PUT: _batch26h_finalize_branch_surface(
                family_id=family_id,
                branch_id=BRANCH_PUT,
                surface=put_branch,
            ),
        }

        family = _batch26h_finalize_family_surface(
            family_id=family_id,
            surface=family_map,
            branches=branches,
            shared_core=shared_core,
            engine=self,
        )
        families[family_id] = family
        surfaces_by_branch[call_key] = branches[BRANCH_CALL]
        surfaces_by_branch[put_key] = branches[BRANCH_PUT]

    out["schema_version"] = out.get("schema_version", getattr(N, "DEFAULT_SCHEMA_VERSION", 1))
    out["surface_version"] = "family_surfaces.v26h"
    out["service"] = out.get("service", SERVICE_FEATURES)
    out["generated_at_ns"] = out.get("generated_at_ns", generated_at_ns)
    out["provider_runtime"] = dict(out.get("provider_runtime", provider_runtime))
    out["shared_core"] = out.get("shared_core", shared_core)
    out["families"] = families
    out["surfaces_by_branch"] = surfaces_by_branch
    out["builder_abi_audit"] = out.get("builder_abi_audit", _builder_abi_audit_snapshot())
    out["contract_note"] = out.get(
        "contract_note",
        "Batch26H consolidated final family-surface contract; strategy remains HOLD/report-only.",
    )

    try:
        if FF_C is not None and callable(getattr(FF_C, "validate_batch26h_surface_kinds", None)):
            FF_C.validate_batch26h_surface_kinds(out)
    except Exception as exc:
        raise FeatureComputationError(f"Batch26H surface-kind validation failed: {exc}") from exc

    return out


FeatureEngine._family_branch_surface = _batch26h_final_family_branch_surface
FeatureEngine._family_surface = _batch26h_final_family_surface
FeatureEngine._family_surfaces = _batch26h_final_family_surfaces

