from __future__ import annotations

"""
app/mme_scalpx/services/strategy.py

Freeze-grade HOLD-only family_features consumer bridge for ScalpX MME.

Purpose
-------
This module is the first strategy-side bridge after the feature payload seam.

It OWNS:
- reading latest feature payload from HASH_STATE_FEATURES_MME_FUT
- parsing family_features_json / family_surfaces_json / family_frames_json
- validating family_features against feature_family/contracts.py
- building a deterministic strategy consumer view
- publishing HOLD-only diagnostic decisions to STREAM_DECISIONS_MME
- strategy heartbeat / strategy errors

It DOES NOT own yet:
- MIST/MISB/MISC/MISR/MISO doctrine-leaf entry logic
- arbitration
- cooldown routing
- entry/exit decision generation
- broker execution
- order placement
- risk mutation
- provider failover

Frozen bridge law
-----------------
Doctrine leaves may be observed through the activation bridge in report-only /
dry-run mode, but strategy.py must still emit HOLD only until explicit future
arming changes the service contract. Candidate promotion is not live here.
"""

import contextlib
import json
import logging
import math
import time
from dataclasses import dataclass
from typing import Any, Final, Mapping, MutableMapping

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services.feature_family import contracts as FF_C
from app.mme_scalpx.services.strategy_family import activation as SF_ACT


LOGGER = logging.getLogger("app.mme_scalpx.services.strategy")


# =============================================================================
# Constants
# =============================================================================

SERVICE_STRATEGY: Final[str] = getattr(N, "SERVICE_STRATEGY", "strategy")
SERVICE_FEATURES: Final[str] = getattr(N, "SERVICE_FEATURES", "features")

STREAM_DECISIONS: Final[str] = getattr(
    N,
    "STREAM_DECISIONS_MME",
    getattr(N, "STREAM_DECISIONS", N.STREAM_DECISIONS_MME),
)
STREAM_HEALTH: Final[str] = getattr(N, "STREAM_SYSTEM_HEALTH", N.STREAM_SYSTEM_HEALTH)
STREAM_ERRORS: Final[str] = getattr(N, "STREAM_SYSTEM_ERRORS", N.STREAM_SYSTEM_ERRORS)

HASH_FEATURES: Final[str] = getattr(
    N,
    "HASH_STATE_FEATURES_MME_FUT",
    getattr(N, "STATE_FEATURES_MME_FUT", N.HASH_STATE_FEATURES_MME_FUT),
)

KEY_HEALTH_STRATEGY: Final[str] = getattr(
    N,
    "KEY_HEALTH_STRATEGY",
    getattr(N, "HB_STRATEGY", "strategy:heartbeat"),
)

ACTION_HOLD: Final[str] = getattr(N, "ACTION_HOLD", "HOLD")
STATE_SCANNING: Final[str] = getattr(N, "STATE_SCANNING", "SCANNING")
STATE_DISABLED: Final[str] = getattr(N, "STATE_DISABLED", "DISABLED")

DEFAULT_POLL_INTERVAL_MS: Final[int] = 150
DEFAULT_HEARTBEAT_TTL_MS: Final[int] = 15_000
DEFAULT_STREAM_MAXLEN: Final[int] = 10_000

FAMILY_IDS: Final[tuple[str, ...]] = tuple(FF_C.FAMILY_IDS)
BRANCH_IDS: Final[tuple[str, ...]] = tuple(FF_C.BRANCH_IDS)

ACTIVATION_REPORT_MODE: Final[str] = SF_ACT.ACTIVATION_MODE_DRY_RUN
ACTIVATION_REPORT_ONLY: Final[bool] = True
ACTIVATION_ALLOW_CANDIDATE_PROMOTION: Final[bool] = False


class StrategyBridgeError(RuntimeError):
    """Raised when strategy consumer bridge cannot safely consume features."""


# =============================================================================
# Helpers
# =============================================================================


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace").strip() or default
    text = str(value).strip()
    return text if text else default


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


def _decode_hash(raw: Mapping[Any, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in (raw or {}).items():
        k = _safe_str(key)
        if isinstance(value, bytes):
            value = value.decode("utf-8", errors="replace")
        out[k] = value
    return out


def _json_load(value: Any, *, field_name: str) -> Any:
    if isinstance(value, (dict, list, tuple)):
        return value
    text = _safe_str(value)
    if not text:
        raise StrategyBridgeError(f"{field_name} is empty")
    try:
        return json.loads(text)
    except Exception as exc:
        raise StrategyBridgeError(f"{field_name} invalid json: {exc}") from exc


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
    if hasattr(value, "__dict__"):
        return _jsonable(vars(value))
    return str(value)


def _json_dump(value: Any) -> str:
    return json.dumps(
        _jsonable(value),
        ensure_ascii=False,
        sort_keys=False,
        separators=(",", ":"),
        allow_nan=False,
    )


def _redis_stream_fields(payload: Mapping[str, Any]) -> dict[str, Any]:
    """
    Convert strategy decision payload into Redis XADD-safe fields.

    Execution consumes decisions through payload_json. During the HOLD-only
    family bridge phase we also keep flattened fields for operator visibility,
    but payload_json is the canonical execution contract.

    Redis-py rejects None values in XADD mappings, so flattened fields convert
    None to an empty string. The JSON payload keeps normal JSON null semantics.
    """
    raw = dict(payload)

    out: dict[str, Any] = {
        "payload_json": _json_dump(raw),
    }

    for key, value in raw.items():
        field = str(key)

        # payload_json above is canonical. Do not allow an incoming flat field
        # to replace the canonical encoded payload.
        if field == "payload_json":
            continue

        if value is None:
            out[field] = ""
        elif isinstance(value, (dict, list, tuple)):
            out[field] = _json_dump(value)
        elif isinstance(value, bool):
            out[field] = "1" if value else "0"
        else:
            out[field] = value

    return out


def _validate_hold_decision_for_publish(decision: Mapping[str, Any]) -> None:
    """
    Enforce the frozen Batch 10 strategy.py law before Redis publication.

    strategy.py is a HOLD-only consumer bridge in this lane. Even if a future
    activation/report module observes candidates, this service may not publish
    promoted ENTER/EXIT decisions until a later explicit arming contract changes
    this file and its proofs.
    """

    action = _safe_str(decision.get("action"), ACTION_HOLD)
    if action != ACTION_HOLD:
        raise StrategyBridgeError(
            f"strategy.py HOLD-only bridge refused non-HOLD action: {action!r}"
        )

    qty = _safe_int(decision.get("qty"), 0)
    if qty != 0:
        raise StrategyBridgeError(
            f"strategy.py HOLD-only bridge refused non-zero qty: {qty!r}"
        )

    if not _safe_bool(decision.get("hold_only"), False):
        raise StrategyBridgeError("strategy.py HOLD-only bridge requires hold_only=1")

    if not _safe_bool(decision.get("activation_report_only"), False):
        raise StrategyBridgeError(
            "strategy.py HOLD-only bridge requires activation_report_only=1"
        )

    activation_action = _safe_str(decision.get("activation_action"), ACTION_HOLD)
    if activation_action != ACTION_HOLD:
        raise StrategyBridgeError(
            "strategy.py HOLD-only bridge refused non-HOLD activation_action: "
            f"{activation_action!r}"
        )

    if _safe_bool(decision.get("activation_promoted"), False):
        raise StrategyBridgeError(
            "strategy.py HOLD-only bridge refused activation_promoted truthy"
        )

    if _safe_bool(decision.get("activation_safe_to_promote"), False):
        raise StrategyBridgeError(
            "strategy.py HOLD-only bridge refused activation_safe_to_promote truthy"
        )

    if _safe_bool(decision.get("live_orders_allowed"), False):
        raise StrategyBridgeError(
            "strategy.py HOLD-only bridge refused live_orders_allowed truthy"
        )


def _validate_decision_stream_fields(
    *,
    decision: Mapping[str, Any],
    fields: Mapping[str, Any],
) -> None:
    """
    Prove flat fields and canonical payload_json cannot drift.

    execution.py consumes payload_json as canonical. The strategy publisher must
    therefore ensure that payload_json.action and payload_json.qty preserve the
    HOLD-only contract and agree with the flat operator-visible fields.
    """

    payload = _mapping(_json_load(fields.get("payload_json"), field_name="payload_json"))

    payload_action = _safe_str(payload.get("action"), "")
    flat_action = _safe_str(fields.get("action"), "")
    if payload_action != ACTION_HOLD or flat_action != ACTION_HOLD:
        raise StrategyBridgeError(
            "strategy.py refused decision stream action mismatch: "
            f"payload_action={payload_action!r}, flat_action={flat_action!r}"
        )

    payload_qty = _safe_int(payload.get("qty"), -1)
    flat_qty = _safe_int(fields.get("qty"), -1)
    if payload_qty != 0 or flat_qty != 0:
        raise StrategyBridgeError(
            "strategy.py refused decision stream qty mismatch: "
            f"payload_qty={payload_qty!r}, flat_qty={flat_qty!r}"
        )

    # Re-run the semantic guard on the decoded canonical payload, not only on
    # the original in-memory mapping.
    _validate_hold_decision_for_publish(payload)


def _nested(root: Any, *keys: str, default: Any = None) -> Any:
    current = root
    for key in keys:
        if not isinstance(current, Mapping):
            return default
        current = current.get(key)
        if current is None:
            return default
    return current


def _mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "to_dict"):
        with contextlib.suppress(Exception):
            out = value.to_dict()
            if isinstance(out, Mapping):
                return dict(out)
    if hasattr(value, "__dict__"):
        return dict(vars(value))
    return {}


def _now_ns_from_clock(clock: Any) -> int:
    for attr in ("now_ns", "time_ns"):
        fn = getattr(clock, attr, None)
        if callable(fn):
            with contextlib.suppress(Exception):
                return int(fn())
    return time.time_ns()


# =============================================================================
# Consumer data structures
# =============================================================================


@dataclass(frozen=True, slots=True)
class FamilyBranchConsumerFrame:
    key: str
    family_id: str
    branch_id: str
    side: str | None
    eligible: bool
    tradability_ok: bool
    instrument_key: str | None
    instrument_token: str | None
    option_symbol: str | None
    strike: float | None
    option_price: float | None

    @classmethod
    def from_mapping(cls, key: str, value: Mapping[str, Any]) -> FamilyBranchConsumerFrame:
        return cls(
            key=key,
            family_id=_safe_str(value.get("family_id")),
            branch_id=_safe_str(value.get("branch_id")),
            side=_safe_str(value.get("side")) or None,
            eligible=_safe_bool(value.get("eligible"), False),
            tradability_ok=_safe_bool(value.get("tradability_ok"), False),
            instrument_key=_safe_str(value.get("instrument_key")) or None,
            instrument_token=_safe_str(value.get("instrument_token")) or None,
            option_symbol=_safe_str(value.get("option_symbol")) or None,
            strike=(
                _safe_float(value.get("strike"))
                if value.get("strike") not in (None, "")
                else None
            ),
            option_price=(
                _safe_float(value.get("option_price"))
                if value.get("option_price") not in (None, "")
                else None
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "family_id": self.family_id,
            "branch_id": self.branch_id,
            "side": self.side,
            "eligible": self.eligible,
            "tradability_ok": self.tradability_ok,
            "instrument_key": self.instrument_key,
            "instrument_token": self.instrument_token,
            "option_symbol": self.option_symbol,
            "strike": self.strike,
            "option_price": self.option_price,
        }


@dataclass(frozen=True, slots=True)
class StrategyFamilyConsumerView:
    view_version: str
    frame_id: str
    frame_ts_ns: int
    features_generated_at_ns: int
    safe_to_consume: bool
    hold_only: bool
    action: str
    reason: str
    data_valid: bool
    warmup_complete: bool
    provider_ready_classic: bool
    provider_ready_miso: bool
    regime: str | None
    provider_runtime: Mapping[str, Any]
    stage_flags: Mapping[str, Any]
    common: Mapping[str, Any]
    market: Mapping[str, Any]
    family_status: Mapping[str, Any]
    family_surfaces: Mapping[str, Any]
    family_frames: Mapping[str, Any]
    branch_frames: Mapping[str, FamilyBranchConsumerFrame]

    def to_dict(self) -> dict[str, Any]:
        return {
            "view_version": self.view_version,
            "frame_id": self.frame_id,
            "frame_ts_ns": self.frame_ts_ns,
            "features_generated_at_ns": self.features_generated_at_ns,
            "safe_to_consume": self.safe_to_consume,
            "hold_only": self.hold_only,
            "action": self.action,
            "reason": self.reason,
            "data_valid": self.data_valid,
            "warmup_complete": self.warmup_complete,
            "provider_ready_classic": self.provider_ready_classic,
            "provider_ready_miso": self.provider_ready_miso,
            "regime": self.regime,
            "provider_runtime": dict(self.provider_runtime),
            "stage_flags": dict(self.stage_flags),
            "common": dict(self.common),
            "market": dict(self.market),
            "family_status": dict(self.family_status),
            "family_surfaces": dict(self.family_surfaces),
            "family_frames": dict(self.family_frames),
            "branch_frames": {
                key: frame.to_dict() for key, frame in self.branch_frames.items()
            },
        }


@dataclass(frozen=True, slots=True)
class FeaturePayloadBundle:
    source_hash_key: str
    raw_hash: Mapping[str, Any]
    family_features: Mapping[str, Any]
    family_surfaces: Mapping[str, Any]
    family_frames: Mapping[str, Any]
    payload: Mapping[str, Any]

    @property
    def feature_frame_id(self) -> str:
        return _safe_str(self.raw_hash.get("frame_id")) or _safe_str(self.payload.get("frame_id"))

    @property
    def feature_frame_ts_ns(self) -> int:
        return _safe_int(self.raw_hash.get("frame_ts_ns"), _safe_int(self.payload.get("frame_ts_ns"), 0))


# =============================================================================
# Consumer bridge
# =============================================================================


class StrategyFamilyConsumerBridge:
    """
    Read, validate and reduce feature payload into strategy-consumable view.

    This bridge deliberately does not evaluate doctrine leaves.
    """

    def __init__(self, *, redis_client: Any, logger: logging.Logger | None = None):
        self.redis = redis_client
        self.log = logger or LOGGER
        self.activation_config = SF_ACT.StrategyFamilyActivationConfig(
            activation_mode=ACTIVATION_REPORT_MODE,
            allow_candidate_promotion=ACTIVATION_ALLOW_CANDIDATE_PROMOTION,
            allow_live_orders=False,
            require_hold_only_view=True,
            require_safe_to_consume=True,
            require_data_valid=True,
            require_warmup_complete=True,
            min_candidate_score=0.0,
            max_candidates=10,
            enabled_families=FAMILY_IDS,
            enabled_branches=BRANCH_IDS,
        )

    def read_feature_bundle(self) -> FeaturePayloadBundle:
        try:
            raw_result = self.redis.hgetall(HASH_FEATURES) or {}
        except Exception as exc:
            raise StrategyBridgeError(
                f"feature hash read failed: {HASH_FEATURES}: {exc}"
            ) from exc

        raw = _decode_hash(raw_result)
        if not raw:
            raise StrategyBridgeError(f"feature hash is empty: {HASH_FEATURES}")

        # Do not suppress JSON/schema errors here. A malformed features hash is
        # materially different from an empty hash and must be visible in proofs,
        # logs, and system:error stream.
        return self._bundle_from_hash(raw)

    def _bundle_from_hash(self, raw: Mapping[str, Any]) -> FeaturePayloadBundle:
        family_features = _mapping(
            _json_load(raw.get("family_features_json"), field_name="family_features_json")
        )
        family_surfaces = _mapping(
            _json_load(raw.get("family_surfaces_json", "{}"), field_name="family_surfaces_json")
        )
        family_frames = _mapping(
            _json_load(raw.get("family_frames_json", "{}"), field_name="family_frames_json")
        )
        payload_raw = raw.get("payload_json")
        payload = _mapping(_json_load(payload_raw, field_name="payload_json")) if payload_raw else {}

        FF_C.validate_family_features_payload(family_features)

        self._validate_surfaces(family_surfaces)
        self._validate_frames(family_frames)

        return FeaturePayloadBundle(
            source_hash_key=HASH_FEATURES,
            raw_hash=dict(raw),
            family_features=family_features,
            family_surfaces=family_surfaces,
            family_frames=family_frames,
            payload=payload,
        )

    def _validate_surfaces(self, family_surfaces: Mapping[str, Any]) -> None:
        families = _mapping(family_surfaces.get("families"))
        missing = [family_id for family_id in FAMILY_IDS if family_id not in families]
        if missing:
            raise StrategyBridgeError(f"family_surfaces missing families: {missing}")

        by_branch = _mapping(family_surfaces.get("surfaces_by_branch"))
        missing_branches: list[str] = []
        for family_id in FAMILY_IDS:
            for branch_id in BRANCH_IDS:
                key = f"{family_id.lower()}_{branch_id.lower()}"
                if key not in by_branch:
                    missing_branches.append(key)

        if missing_branches:
            raise StrategyBridgeError(f"family_surfaces missing branch surfaces: {missing_branches}")

    def _validate_frames(self, family_frames: Mapping[str, Any]) -> None:
        missing: list[str] = []
        for family_id in FAMILY_IDS:
            for branch_id in BRANCH_IDS:
                key = f"{family_id.lower()}_{branch_id.lower()}"
                if key not in family_frames:
                    missing.append(key)
        if missing:
            raise StrategyBridgeError(f"family_frames missing branch frames: {missing}")

    def build_consumer_view(
        self,
        bundle: FeaturePayloadBundle,
        *,
        now_ns: int,
    ) -> StrategyFamilyConsumerView:
        family_features = bundle.family_features
        family_surfaces = bundle.family_surfaces
        family_frames = bundle.family_frames

        stage_flags = _mapping(family_features["stage_flags"])
        provider_runtime = _mapping(family_features["provider_runtime"])
        common = _mapping(family_features["common"])
        market = _mapping(family_features["market"])
        families = _mapping(family_features["families"])

        family_status: dict[str, Any] = {}
        for family_id in FAMILY_IDS:
            contract_payload = _mapping(families.get(family_id))
            surface_payload = _mapping(_nested(family_surfaces, "families", family_id, default={}))

            family_status[family_id] = {
                "family_present": family_id in families,
                "contract_eligible": _safe_bool(contract_payload.get("eligible"), False),
                "surface_eligible": _safe_bool(surface_payload.get("eligible"), False),
                "surface_keys": tuple(surface_payload.keys()),
                "contract_keys": tuple(contract_payload.keys()),
            }

        branch_views: dict[str, FamilyBranchConsumerFrame] = {}
        for family_id in FAMILY_IDS:
            for branch_id in BRANCH_IDS:
                key = f"{family_id.lower()}_{branch_id.lower()}"
                branch_views[key] = FamilyBranchConsumerFrame.from_mapping(
                    key,
                    _mapping(family_frames[key]),
                )

        data_valid = _safe_bool(stage_flags.get("data_valid"), False)
        warmup_complete = _safe_bool(stage_flags.get("warmup_complete"), False)
        provider_ready_classic = _safe_bool(stage_flags.get("provider_ready_classic"), False)
        provider_ready_miso = _safe_bool(stage_flags.get("provider_ready_miso"), False)

        safe_to_consume = bool(
            family_features
            and family_surfaces
            and family_frames
            and stage_flags
            and provider_runtime
            and common
            and market
            and family_status
            and branch_views
        )

        return StrategyFamilyConsumerView(
            view_version="strategy-family-consumer-view.v1",
            frame_id=f"strategy-view-{now_ns}",
            frame_ts_ns=now_ns,
            features_generated_at_ns=_safe_int(family_features.get("generated_at_ns"), 0),
            safe_to_consume=safe_to_consume,
            hold_only=True,
            action=ACTION_HOLD,
            reason="hold_only_family_features_consumer_bridge",
            data_valid=data_valid,
            warmup_complete=warmup_complete,
            provider_ready_classic=provider_ready_classic,
            provider_ready_miso=provider_ready_miso,
            regime=_safe_str(common.get("regime")) or None,
            provider_runtime=provider_runtime,
            stage_flags=stage_flags,
            common=common,
            market=market,
            family_status=family_status,
            family_surfaces=family_surfaces,
            family_frames=family_frames,
            branch_frames=branch_views,
        )

    def build_activation_report(
        self,
        view: StrategyFamilyConsumerView,
        *,
        now_ns: int,
    ) -> dict[str, Any]:
        """
        Build report-only activation bridge output.

        Safety invariant:
        - strategy.py still emits HOLD
        - qty remains 0
        - no broker/execution call is possible here
        - any unexpected activation promotion is forcibly downgraded to report-only
        """
        try:
            activation_decision = SF_ACT.build_activation_decision(
                view,
                config=self.activation_config,
            )
            report = _mapping(activation_decision.to_dict())
        except Exception as exc:
            self.log.exception("strategy_activation_report_error")
            report = {
                "activation_mode": ACTIVATION_REPORT_MODE,
                "action": ACTION_HOLD,
                "hold": True,
                "promoted": False,
                "safe_to_promote": False,
                "reason": "activation_report_error",
                "error_type": type(exc).__name__,
                "error": str(exc),
                "selected": None,
                "candidates": [],
                "blocked": [],
                "no_signal": [],
            }

        # Hard report-only clamp. Even if future activation.py changes, this
        # strategy bridge remains HOLD until strategy.py is explicitly armed.
        observed_action = _safe_str(report.get("action"), ACTION_HOLD)
        observed_promoted = _safe_bool(report.get("promoted"), False)
        observed_safe_to_promote = _safe_bool(report.get("safe_to_promote"), False)

        if (
            observed_action != ACTION_HOLD
            or observed_promoted
            or observed_safe_to_promote
        ):
            report["observed_action_before_strategy_clamp"] = observed_action
            report["observed_promoted_before_strategy_clamp"] = observed_promoted
            report["observed_safe_to_promote_before_strategy_clamp"] = observed_safe_to_promote
            report["strategy_clamp"] = "forced_hold_report_only"
            report["action"] = ACTION_HOLD
            report["hold"] = True
            report["promoted"] = False
            report["safe_to_promote"] = False

        report["strategy_report_only"] = True
        report["strategy_ts_ns"] = now_ns
        report["live_orders_allowed"] = False
        return report

    def build_hold_decision(
        self,
        view: StrategyFamilyConsumerView,
        *,
        now_ns: int,
    ) -> dict[str, Any]:
        """
        Build HOLD-only strategy decision.

        This shape is intentionally conservative and diagnostic-rich. Execution
        must ignore HOLD for order placement.
        """
        selected_option = (
            _mapping(view.common.get("selected_option"))
            or _mapping(view.common.get("selected_call"))
            or _mapping(view.common.get("selected_put"))
        )

        activation_report = self.build_activation_report(view, now_ns=now_ns)
        activation_selected = _mapping(activation_report.get("selected"))
        activation_candidates = activation_report.get("candidates")
        activation_candidate_count = (
            len(activation_candidates)
            if isinstance(activation_candidates, list)
            else 0
        )

        decision_id = f"strategy-hold-{now_ns}"

        return {
            "schema_version": getattr(N, "DEFAULT_SCHEMA_VERSION", 1),
            "service": SERVICE_STRATEGY,
            "decision_id": decision_id,
            "ts_ns": now_ns,
            "ts_event_ns": now_ns,
            "action": ACTION_HOLD,
            "side": getattr(N, "POSITION_SIDE_FLAT", "FLAT"),
            "branch_id": "",
            "strategy_family_id": "",
            "doctrine_id": "",
            "instrument_key": _safe_str(selected_option.get("instrument_key")),
            "instrument_token": _safe_str(selected_option.get("instrument_token")),
            "option_symbol": _safe_str(selected_option.get("option_symbol")),
            "strike": selected_option.get("strike"),
            "qty": 0,
            "price": selected_option.get("ltp"),
            "order_type": "",
            "reason": view.reason,
            "confidence": 0.0,
            "hold_only": 1,
            "activation_bridge_enabled": 1,
            "activation_report_only": 1,
            "activation_mode": _safe_str(activation_report.get("activation_mode"), ACTIVATION_REPORT_MODE),
            "activation_action": ACTION_HOLD,
            "activation_observed_action": _safe_str(
                activation_report.get("observed_action_before_strategy_clamp"),
                _safe_str(activation_report.get("action"), ACTION_HOLD),
            ),
            "activation_promoted": 0,
            "activation_safe_to_promote": 0,
            "activation_reason": _safe_str(activation_report.get("reason")),
            "activation_selected_family_id": _safe_str(activation_selected.get("family_id")),
            "activation_selected_branch_id": _safe_str(activation_selected.get("branch_id")),
            "activation_selected_action": _safe_str(activation_selected.get("action")),
            "activation_selected_score": activation_selected.get("score"),
            "activation_candidate_count": activation_candidate_count,
            "safe_to_consume": int(view.safe_to_consume),
            "data_valid": int(view.data_valid),
            "warmup_complete": int(view.warmup_complete),
            "provider_ready_classic": int(view.provider_ready_classic),
            "provider_ready_miso": int(view.provider_ready_miso),
            "regime": view.regime or "",
            "features_generated_at_ns": view.features_generated_at_ns,
            "consumer_view_json": _json_dump(view.to_dict()),
            "activation_report_json": _json_dump(activation_report),
            "diagnostics_json": _json_dump(
                {
                    "bridge": "strategy_family_consumer_bridge",
                    "hold_only": True,
                    "activation_bridge_report_only": True,
                    "activation_mode": _safe_str(activation_report.get("activation_mode"), ACTIVATION_REPORT_MODE),
                    "activation_reason": _safe_str(activation_report.get("reason")),
                    "activation_selected_family_id": _safe_str(activation_selected.get("family_id")),
                    "activation_selected_branch_id": _safe_str(activation_selected.get("branch_id")),
                    "activation_candidate_count": activation_candidate_count,
                    "doctrine_leaves_observed": True,
                    "doctrine_leaves_active": False,
                    "broker_side_effects_allowed": False,
                    "live_orders_allowed": False,
                    "families": tuple(view.family_status.keys()),
                    "branch_frame_count": len(view.branch_frames),
                }
            ),
        }


# =============================================================================
# Service
# =============================================================================


class StrategyService:
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
        self.bridge = StrategyFamilyConsumerBridge(redis_client=redis_client, logger=self.log)
        self.poll_interval_ms = DEFAULT_POLL_INTERVAL_MS
        self.heartbeat_ttl_ms = DEFAULT_HEARTBEAT_TTL_MS
        self._last_heartbeat_ns = 0

    def _now_ns(self) -> int:
        return _now_ns_from_clock(self.clock)

    def run_once(self) -> dict[str, Any]:
        now_ns = self._now_ns()
        bundle = self.bridge.read_feature_bundle()
        view = self.bridge.build_consumer_view(bundle, now_ns=now_ns)
        decision = self.bridge.build_hold_decision(view, now_ns=now_ns)
        self.publish_decision(decision)
        return decision

    def publish_decision(self, decision: Mapping[str, Any]) -> None:
        _validate_hold_decision_for_publish(decision)
        fields = _redis_stream_fields(decision)
        _validate_decision_stream_fields(decision=decision, fields=fields)
        self.redis.xadd(
            STREAM_DECISIONS,
            fields=fields,
            maxlen=DEFAULT_STREAM_MAXLEN,
            approximate=True,
        )


    def _publish_health(self, status: str, detail: str) -> None:
        now_ns = self._now_ns()
        payload = {
            "service": SERVICE_STRATEGY,
            "instance_id": self.instance_id,
            "status": status,
            "detail": detail,
            "ts_ns": now_ns,
            "ts_event_ns": now_ns,
        }
        with contextlib.suppress(Exception):
            self.redis.hset(KEY_HEALTH_STRATEGY, mapping=payload)
            self.redis.pexpire(KEY_HEALTH_STRATEGY, self.heartbeat_ttl_ms)
        with contextlib.suppress(Exception):
            self.redis.xadd(
                STREAM_HEALTH,
                fields=payload,
                maxlen=DEFAULT_STREAM_MAXLEN,
                approximate=True,
            )
        self._last_heartbeat_ns = now_ns

    def publish_error(self, *, where: str, exc: BaseException) -> None:
        now_ns = self._now_ns()
        payload = {
            "service": SERVICE_STRATEGY,
            "instance_id": self.instance_id,
            "where": where,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "ts_ns": now_ns,
            "ts_event_ns": now_ns,
        }
        with contextlib.suppress(Exception):
            self.redis.xadd(
                STREAM_ERRORS,
                fields=payload,
                maxlen=DEFAULT_STREAM_MAXLEN,
                approximate=True,
            )

    def start(self) -> int:
        self.log.info("strategy_service_started instance_id=%s", self.instance_id)
        self._publish_health(getattr(N, "HEALTH_STATUS_WARN", "WARN"), "strategy_starting_hold_bridge")

        while not self.shutdown.is_set():
            status = getattr(N, "HEALTH_STATUS_OK", "OK")
            detail = "strategy_hold_bridge_ok"

            try:
                self.run_once()
            except Exception as exc:
                self.log.exception("strategy_hold_bridge_loop_error")
                self.publish_error(where="strategy_hold_bridge_loop_error", exc=exc)
                status = getattr(N, "HEALTH_STATUS_ERROR", "ERROR")
                detail = f"loop_error:{type(exc).__name__}"

            now_ns = self._now_ns()
            if now_ns - self._last_heartbeat_ns >= 2_000_000_000:
                self._publish_health(status, detail)

            self.shutdown.wait(max(0.01, self.poll_interval_ms / 1000.0))

        self._publish_health(getattr(N, "HEALTH_STATUS_WARN", "WARN"), "strategy_stopping")
        self.log.info("strategy_service_stopped")
        return 0


StrategyFamilyBridge = StrategyFamilyConsumerBridge


def read_family_feature_bundle(redis_client: Any) -> FeaturePayloadBundle:
    return StrategyFamilyConsumerBridge(redis_client=redis_client).read_feature_bundle()


def build_strategy_consumer_view(
    *,
    family_features: Mapping[str, Any],
    family_surfaces: Mapping[str, Any],
    family_frames: Mapping[str, Any],
    now_ns: int,
) -> StrategyFamilyConsumerView:
    FF_C.validate_family_features_payload(family_features)

    dummy_bundle = FeaturePayloadBundle(
        source_hash_key="<memory>",
        raw_hash={},
        family_features=family_features,
        family_surfaces=family_surfaces,
        family_frames=family_frames,
        payload={},
    )

    class _MemoryBridge(StrategyFamilyConsumerBridge):
        def __init__(self) -> None:
            pass

    bridge = _MemoryBridge()
    bridge._validate_surfaces(family_surfaces)
    bridge._validate_frames(family_frames)
    return bridge.build_consumer_view(dummy_bundle, now_ns=now_ns)


def run(context: Any) -> int:
    redis_runtime = getattr(context, "redis", None)
    if redis_runtime is None:
        raise RuntimeError("strategy requires context.redis")
    redis_client = redis_runtime.sync if hasattr(redis_runtime, "sync") else redis_runtime

    shutdown = getattr(context, "shutdown", None)
    clock = getattr(context, "clock", None)
    instance_id = _safe_str(getattr(context, "instance_id", ""), "strategy")

    if shutdown is None:
        raise RuntimeError("strategy requires context.shutdown")
    if clock is None:
        raise RuntimeError("strategy requires context.clock")

    return StrategyService(
        redis_client=redis_client,
        clock=clock,
        shutdown=shutdown,
        instance_id=instance_id,
        settings=getattr(context, "settings", None),
        logger=LOGGER,
    ).start()


__all__ = [
    "FeaturePayloadBundle",
    "FamilyBranchConsumerFrame",
    "StrategyBridgeError",
    "StrategyFamilyBridge",
    "StrategyFamilyConsumerBridge",
    "StrategyFamilyConsumerView",
    "StrategyService",
    "ACTIVATION_REPORT_MODE",
    "ACTIVATION_REPORT_ONLY",
    "build_strategy_consumer_view",
    "read_family_feature_bundle",
    "run",
]
