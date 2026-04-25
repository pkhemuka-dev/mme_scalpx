from __future__ import annotations

"""
app/mme_scalpx/services/strategy_family/mist.py

Freeze-grade MIST doctrine leaf evaluator for ScalpX MME.

Purpose
-------
This module OWNS:
- pure MIST CALL/PUT candidate evaluation from the already-built strategy
  consumer view / family feature surfaces
- deterministic no-signal / blocked / candidate result construction
- MIST-specific trend-pullback-resume support checks

This module DOES NOT own:
- Redis reads or writes
- feature computation
- strategy service publication
- broker calls
- execution mutation
- risk mutation
- cooldown mutation
- order placement

Frozen MIST identity
--------------------
MIST is the trend / pullback / resume member of the MIS family.

It is:
- futures-led
- option-confirmed
- Dhan-enhanced
- degraded-safe
- intraday-only
- short-hold
- single-position compatible
- 5-point first-target oriented

This leaf evaluates candidate support only. It does not publish decisions.
"""

import math
from dataclasses import dataclass, field
from typing import Any, Final, Mapping, Sequence

from app.mme_scalpx.core import names as N


FAMILY_ID: Final[str] = getattr(N, "STRATEGY_FAMILY_MIST", "MIST")
DOCTRINE_ID: Final[str] = getattr(N, "DOCTRINE_MIST", "MIST")
BRANCH_CALL: Final[str] = getattr(N, "BRANCH_CALL", "CALL")
BRANCH_PUT: Final[str] = getattr(N, "BRANCH_PUT", "PUT")
SIDE_CALL: Final[str] = getattr(N, "SIDE_CALL", "CALL")
SIDE_PUT: Final[str] = getattr(N, "SIDE_PUT", "PUT")

ACTION_ENTER_CALL: Final[str] = getattr(N, "ACTION_ENTER_CALL", "ENTER_CALL")
ACTION_ENTER_PUT: Final[str] = getattr(N, "ACTION_ENTER_PUT", "ENTER_PUT")
ACTION_HOLD: Final[str] = getattr(N, "ACTION_HOLD", "HOLD")

RUNTIME_DISABLED: Final[str] = getattr(N, "STRATEGY_RUNTIME_MODE_DISABLED", "DISABLED")
RUNTIME_NORMAL: Final[str] = getattr(N, "STRATEGY_RUNTIME_MODE_NORMAL", "NORMAL")
RUNTIME_DHAN_DEGRADED: Final[str] = getattr(
    N,
    "STRATEGY_RUNTIME_MODE_DHAN_DEGRADED",
    "DHAN-DEGRADED",
)

ENTRY_MODE_ATM: Final[str] = getattr(N, "ENTRY_MODE_ATM", "ATM")
ENTRY_MODE_ATM1: Final[str] = getattr(N, "ENTRY_MODE_ATM1", "ATM1")
ENTRY_MODE_UNKNOWN: Final[str] = getattr(N, "ENTRY_MODE_UNKNOWN", "UNKNOWN")

REGIME_LOWVOL: Final[str] = "LOWVOL"
REGIME_NORMAL: Final[str] = "NORMAL"
REGIME_FAST: Final[str] = "FAST"

SUPPORTED_BRANCHES: Final[tuple[str, str]] = (BRANCH_CALL, BRANCH_PUT)

TARGET_POINTS: Final[float] = 5.0
HARD_STOP_POINTS: Final[float] = 4.0
DEFAULT_TICK_SIZE: Final[float] = 0.05

MIN_SCORE_NORMAL: Final[float] = 0.54
MIN_SCORE_FAST: Final[float] = 0.58
MIN_SCORE_LOWVOL: Final[float] = 0.62

MIN_FUTURES_IMPULSE: Final[float] = 0.52
MIN_OPTION_CONFIRMATION: Final[float] = 0.50
MIN_CONTEXT_SCORE: Final[float] = 0.45

OI_WALL_VETO_DISTANCE_STRIKES: Final[float] = 0.75
OI_WALL_STRONG_MIN: Final[float] = 0.72


# =============================================================================
# Small helpers
# =============================================================================


def safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace").strip() or default
    text = str(value).strip()
    return text if text else default


def safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = safe_str(value).lower()
    if text in {"1", "true", "yes", "y", "on", "ok", "pass", "passed", "available"}:
        return True
    if text in {"0", "false", "no", "n", "off", "fail", "failed", "none", "null"}:
        return False
    return default


def safe_float(value: Any, default: float = 0.0) -> float:
    if value is None or isinstance(value, bool):
        return default
    try:
        text = safe_str(value)
        if not text:
            return default
        out = float(text)
    except Exception:
        return default
    return out if math.isfinite(out) else default


def safe_int(value: Any, default: int = 0) -> int:
    if value is None or isinstance(value, bool):
        return default
    try:
        text = safe_str(value)
        if not text:
            return default
        return int(float(text))
    except Exception:
        return default


def as_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "to_dict"):
        try:
            out = value.to_dict()
            if isinstance(out, Mapping):
                return dict(out)
        except Exception:
            pass
    if hasattr(value, "__dict__"):
        return dict(vars(value))
    return {}


def nested(root: Any, *path: str, default: Any = None) -> Any:
    cur = root
    for key in path:
        if not isinstance(cur, Mapping):
            return default
        cur = cur.get(key)
        if cur is None:
            return default
    return cur


def normalize_branch(value: Any) -> str | None:
    text = safe_str(value).upper()
    if text in {"CALL", "CE", "C", BRANCH_CALL}:
        return BRANCH_CALL
    if text in {"PUT", "PE", "P", BRANCH_PUT}:
        return BRANCH_PUT
    return None


def side_for_branch(branch_id: str) -> str:
    return SIDE_CALL if branch_id == BRANCH_CALL else SIDE_PUT


def action_for_branch(branch_id: str) -> str:
    return ACTION_ENTER_CALL if branch_id == BRANCH_CALL else ACTION_ENTER_PUT


def normalize_regime(value: Any) -> str:
    text = safe_str(value, REGIME_NORMAL).upper()
    if text in {REGIME_LOWVOL, REGIME_NORMAL, REGIME_FAST}:
        return text
    return REGIME_NORMAL


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def bool_any(mapping: Mapping[str, Any], keys: Sequence[str]) -> bool:
    return any(safe_bool(mapping.get(key), False) for key in keys)


def float_any(mapping: Mapping[str, Any], keys: Sequence[str], default: float = 0.0) -> float:
    for key in keys:
        if key in mapping and mapping[key] not in (None, ""):
            return safe_float(mapping[key], default)
    return default


def mapping_any(mapping: Mapping[str, Any], keys: Sequence[str]) -> dict[str, Any]:
    for key in keys:
        child = as_mapping(mapping.get(key))
        if child:
            return child
    return {}


# =============================================================================
# Result contracts
# =============================================================================


@dataclass(frozen=True, slots=True)
class MistBlocker:
    code: str
    message: str
    severity: str = "BLOCK"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class MistCandidate:
    family_id: str
    doctrine_id: str
    branch_id: str
    side: str
    action: str
    score: float
    priority: float
    instrument_key: str | None
    instrument_token: str | None
    option_symbol: str | None
    strike: float | None
    option_price: float | None
    target_points: float = TARGET_POINTS
    stop_points: float = HARD_STOP_POINTS
    tick_size: float = DEFAULT_TICK_SIZE
    quantity_lots_hint: int | None = None
    setup_kind: str = "MIST_TREND_PULLBACK_RESUME"
    source_event_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "family_id": self.family_id,
            "doctrine_id": self.doctrine_id,
            "branch_id": self.branch_id,
            "side": self.side,
            "action": self.action,
            "score": self.score,
            "priority": self.priority,
            "instrument_key": self.instrument_key,
            "instrument_token": self.instrument_token,
            "option_symbol": self.option_symbol,
            "strike": self.strike,
            "option_price": self.option_price,
            "target_points": self.target_points,
            "stop_points": self.stop_points,
            "tick_size": self.tick_size,
            "quantity_lots_hint": self.quantity_lots_hint,
            "setup_kind": self.setup_kind,
            "source_event_id": self.source_event_id,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class MistEvaluationResult:
    family_id: str
    doctrine_id: str
    branch_id: str | None
    action: str
    is_candidate: bool
    is_blocked: bool
    candidate: MistCandidate | None = None
    blocker: MistBlocker | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def is_no_signal(self) -> bool:
        return not self.is_candidate and not self.is_blocked

    def to_dict(self) -> dict[str, Any]:
        return {
            "family_id": self.family_id,
            "doctrine_id": self.doctrine_id,
            "branch_id": self.branch_id,
            "action": self.action,
            "is_candidate": self.is_candidate,
            "is_blocked": self.is_blocked,
            "is_no_signal": self.is_no_signal,
            "candidate": self.candidate.to_dict() if self.candidate else None,
            "blocker": self.blocker.to_dict() if self.blocker else None,
            "metadata": dict(self.metadata),
        }


def no_signal_result(
    *,
    branch_id: str | None,
    reason: str,
    metadata: Mapping[str, Any] | None = None,
) -> MistEvaluationResult:
    return MistEvaluationResult(
        family_id=FAMILY_ID,
        doctrine_id=DOCTRINE_ID,
        branch_id=branch_id,
        action=ACTION_HOLD,
        is_candidate=False,
        is_blocked=False,
        candidate=None,
        blocker=None,
        metadata={"reason": reason, **dict(metadata or {})},
    )


def blocked_result(
    *,
    branch_id: str | None,
    code: str,
    message: str,
    metadata: Mapping[str, Any] | None = None,
) -> MistEvaluationResult:
    return MistEvaluationResult(
        family_id=FAMILY_ID,
        doctrine_id=DOCTRINE_ID,
        branch_id=branch_id,
        action=ACTION_HOLD,
        is_candidate=False,
        is_blocked=True,
        candidate=None,
        blocker=MistBlocker(
            code=code,
            message=message,
            metadata=dict(metadata or {}),
        ),
        metadata={"reason": code, **dict(metadata or {})},
    )


def candidate_result(candidate: MistCandidate) -> MistEvaluationResult:
    return MistEvaluationResult(
        family_id=FAMILY_ID,
        doctrine_id=DOCTRINE_ID,
        branch_id=candidate.branch_id,
        action=candidate.action,
        is_candidate=True,
        is_blocked=False,
        candidate=candidate,
        blocker=None,
        metadata={"reason": "mist_candidate_ready"},
    )


# =============================================================================
# View normalization
# =============================================================================


def consumer_view_to_mapping(view: Any) -> dict[str, Any]:
    mapping = as_mapping(view)
    if mapping:
        return mapping

    out: dict[str, Any] = {}
    for attr in (
        "safe_to_consume",
        "hold_only",
        "data_valid",
        "warmup_complete",
        "provider_ready_classic",
        "provider_ready_miso",
        "regime",
        "provider_runtime",
        "stage_flags",
        "common",
        "market",
        "family_status",
        "branch_frames",
    ):
        if hasattr(view, attr):
            value = getattr(view, attr)
            if attr == "branch_frames" and isinstance(value, Mapping):
                out[attr] = {
                    key: as_mapping(frame) if not isinstance(frame, Mapping) else dict(frame)
                    for key, frame in value.items()
                }
            else:
                out[attr] = value
    return out


def frame_to_mapping(frame: Any) -> dict[str, Any]:
    mapping = as_mapping(frame)
    if mapping:
        return mapping
    out: dict[str, Any] = {}
    for attr in (
        "key",
        "family_id",
        "branch_id",
        "side",
        "eligible",
        "tradability_ok",
        "instrument_key",
        "instrument_token",
        "option_symbol",
        "strike",
        "option_price",
    ):
        if hasattr(frame, attr):
            out[attr] = getattr(frame, attr)
    return out


def branch_frame_key(branch_id: str) -> str:
    return f"{FAMILY_ID.lower()}_{branch_id.lower()}"


def extract_branch_frame(view: Mapping[str, Any], branch_id: str) -> dict[str, Any]:
    frames = as_mapping(view.get("branch_frames"))
    frame = frames.get(branch_frame_key(branch_id))
    return frame_to_mapping(frame)


def extract_family_surface(view: Mapping[str, Any], branch_id: str) -> dict[str, Any]:
    surfaces = as_mapping(view.get("family_surfaces"))
    if surfaces:
        by_branch = as_mapping(surfaces.get("surfaces_by_branch"))
        surface = as_mapping(by_branch.get(branch_frame_key(branch_id)))
        if surface:
            return surface
        family = as_mapping(nested(surfaces, "families", FAMILY_ID, default={}))
        surface = as_mapping(nested(family, "branches", branch_id, default={}))
        if surface:
            return surface

    family_status = as_mapping(view.get("family_status"))
    status = as_mapping(family_status.get(FAMILY_ID))
    return status


def extract_common(view: Mapping[str, Any]) -> dict[str, Any]:
    return as_mapping(view.get("common"))


def extract_stage_flags(view: Mapping[str, Any]) -> dict[str, Any]:
    return as_mapping(view.get("stage_flags"))


def extract_provider_runtime(view: Mapping[str, Any]) -> dict[str, Any]:
    return as_mapping(view.get("provider_runtime"))


# =============================================================================
# MIST doctrine scoring
# =============================================================================


def runtime_mode(view: Mapping[str, Any]) -> str:
    common = extract_common(view)
    provider_runtime = extract_provider_runtime(view)
    text = (
        safe_str(common.get("strategy_runtime_mode_classic"))
        or safe_str(common.get("classic_runtime_mode"))
        or safe_str(provider_runtime.get("classic_runtime_mode"))
        or RUNTIME_NORMAL
    )
    return text


def selected_option(view: Mapping[str, Any], branch_id: str) -> dict[str, Any]:
    common = extract_common(view)
    selected = as_mapping(common.get("selected_option"))
    branch_side = side_for_branch(branch_id)

    if safe_str(selected.get("side")).upper() == branch_side:
        return selected

    if branch_id == BRANCH_CALL:
        return as_mapping(common.get("call")) or as_mapping(common.get("selected_call"))
    return as_mapping(common.get("put")) or as_mapping(common.get("selected_put"))


def futures_block(view: Mapping[str, Any]) -> dict[str, Any]:
    common = extract_common(view)
    return (
        as_mapping(common.get("futures"))
        or as_mapping(common.get("futures_features"))
        or {}
    )


def trend_direction_ok(view: Mapping[str, Any], branch_id: str, surface: Mapping[str, Any]) -> bool:
    if bool_any(surface, ("trend_direction_ok", "trend_confirmed", "trend_ok")):
        return True

    fut = futures_block(view)
    ofi = float_any(fut, ("ofi_ratio_proxy", "nof", "nof_slope", "weighted_ofi_persist"), 0.0)
    delta_3 = float_any(fut, ("delta_3",), 0.0)
    above_vwap = safe_bool(fut.get("above_vwap"), False)
    below_vwap = safe_bool(fut.get("below_vwap"), False)

    if branch_id == BRANCH_CALL:
        return bool(ofi >= 0.0 and delta_3 >= 0.0 and (above_vwap or delta_3 > 0.0))
    return bool(ofi <= 0.0 and delta_3 <= 0.0 and (below_vwap or delta_3 < 0.0))


def futures_impulse_score(view: Mapping[str, Any], surface: Mapping[str, Any]) -> float:
    if "futures_impulse_score" in surface:
        return clamp(safe_float(surface["futures_impulse_score"], 0.0), 0.0, 1.0)

    fut = futures_block(view)
    velocity = float_any(fut, ("velocity_ratio", "vel_ratio"), 1.0)
    vol_norm = float_any(fut, ("vol_norm", "volume_norm"), 1.0)
    ofi_abs = abs(float_any(fut, ("ofi_ratio_proxy", "nof", "nof_slope"), 0.0))
    return clamp((velocity - 0.80) / 1.20 * 0.45 + (vol_norm - 0.80) / 1.20 * 0.25 + ofi_abs * 0.30, 0.0, 1.0)


def option_confirmation_score(
    view: Mapping[str, Any],
    branch_id: str,
    surface: Mapping[str, Any],
    frame: Mapping[str, Any],
) -> float:
    if "option_confirmation_score" in surface:
        return clamp(safe_float(surface["option_confirmation_score"], 0.0), 0.0, 1.0)

    opt = selected_option(view, branch_id)
    response = float_any(opt, ("response_efficiency",), 0.0)
    depth_ok = safe_bool(opt.get("depth_ok"), safe_bool(frame.get("tradability_ok"), False))
    tradability_ok = safe_bool(opt.get("tradability_ok"), safe_bool(frame.get("tradability_ok"), False))
    delta = abs(float_any(opt, ("delta_3",), 0.0))
    return clamp(response * 1.75 + (0.20 if depth_ok else 0.0) + (0.25 if tradability_ok else 0.0) + min(delta, 3.0) / 3.0 * 0.20, 0.0, 1.0)


def pullback_resume_score(surface: Mapping[str, Any]) -> float:
    explicit = float_any(surface, ("pullback_resume_score", "resume_score"), -1.0)
    if explicit >= 0.0:
        return clamp(explicit, 0.0, 1.0)

    pullback = bool_any(surface, ("pullback_detected", "pullback_ok", "pullback_present"))
    resume = bool_any(surface, ("resume_confirmed", "resume_support", "resume_confirmation_ok"))
    micro_trap = bool_any(surface, ("micro_trap_present", "micro_trap_ok"))
    override = bool_any(surface, ("resume_override_pass", "override_ready"))

    score = 0.0
    if pullback:
        score += 0.35
    if resume:
        score += 0.45
    if micro_trap:
        score += 0.10
    if override:
        score += 0.10
    return clamp(score, 0.0, 1.0)


def context_score(
    view: Mapping[str, Any],
    branch_id: str,
    surface: Mapping[str, Any],
) -> tuple[float, bool, str | None]:
    explicit = float_any(surface, ("context_score", "oi_context_score"), -1.0)
    base = clamp(explicit, 0.0, 1.0) if explicit >= 0.0 else 0.60

    oi_wall = as_mapping(surface.get("oi_wall_context"))
    if not oi_wall:
        oi_wall = as_mapping(nested(view, "oi_wall_context", "call" if branch_id == BRANCH_CALL else "put", default={}))
    if not oi_wall:
        oi_wall = as_mapping(nested(view, "shared_core", "oi_wall_context", "call" if branch_id == BRANCH_CALL else "put", default={}))

    distance = safe_float(oi_wall.get("distance_strikes"), 99.0)
    strength = safe_float(oi_wall.get("wall_strength"), 0.0)

    if distance <= OI_WALL_VETO_DISTANCE_STRIKES and strength >= OI_WALL_STRONG_MIN:
        return max(0.0, base - 0.35), False, "near_strong_oi_wall"

    return base, True, None


def min_score_for_regime(regime: str) -> float:
    regime = normalize_regime(regime)
    if regime == REGIME_FAST:
        return MIN_SCORE_FAST
    if regime == REGIME_LOWVOL:
        return MIN_SCORE_LOWVOL
    return MIN_SCORE_NORMAL


def compute_score(
    *,
    view: Mapping[str, Any],
    branch_id: str,
    surface: Mapping[str, Any],
    frame: Mapping[str, Any],
) -> tuple[float, Mapping[str, Any]]:
    impulse = futures_impulse_score(view, surface)
    option = option_confirmation_score(view, branch_id, surface, frame)
    resume = pullback_resume_score(surface)
    ctx_score, ctx_pass, ctx_blocker = context_score(view, branch_id, surface)

    score = clamp(
        impulse * 0.30
        + option * 0.25
        + resume * 0.30
        + ctx_score * 0.15,
        0.0,
        1.0,
    )

    return score, {
        "futures_impulse_score": impulse,
        "option_confirmation_score": option,
        "pullback_resume_score": resume,
        "context_score": ctx_score,
        "context_pass": ctx_pass,
        "context_blocker": ctx_blocker,
    }


def degraded_mode_entry_allowed(view: Mapping[str, Any], branch_id: str) -> tuple[bool, str | None]:
    mode = runtime_mode(view)
    if mode != RUNTIME_DHAN_DEGRADED:
        return True, None

    opt = selected_option(view, branch_id)
    entry_mode = safe_str(opt.get("entry_mode"), ENTRY_MODE_UNKNOWN).upper()

    if entry_mode in {ENTRY_MODE_ATM.upper(), "ATM"}:
        return True, None

    return False, "degraded_mode_requires_atm_only"


def global_gates_pass(view: Mapping[str, Any]) -> tuple[bool, str | None]:
    if not safe_bool(view.get("safe_to_consume"), True):
        return False, "view_not_safe_to_consume"

    stage = extract_stage_flags(view)

    required = {
        "data_valid": True,
        "data_quality_ok": True,
        "session_eligible": True,
        "warmup_complete": True,
    }
    for key, expected in required.items():
        if key in stage and safe_bool(stage.get(key), False) != expected:
            return False, f"stage_{key}_failed"

    if safe_bool(stage.get("risk_veto_active"), False):
        return False, "risk_veto_active"
    if safe_bool(stage.get("reconciliation_lock_active"), False):
        return False, "reconciliation_lock_active"
    if safe_bool(stage.get("active_position_present"), False):
        return False, "active_position_present"

    if runtime_mode(view) == RUNTIME_DISABLED:
        return False, "classic_runtime_disabled"

    return True, None


# =============================================================================
# Branch evaluation
# =============================================================================


def evaluate_branch(view_like: Any, branch_id: str) -> MistEvaluationResult:
    branch_id = normalize_branch(branch_id) or ""
    if branch_id not in SUPPORTED_BRANCHES:
        return no_signal_result(
            branch_id=None,
            reason="unsupported_branch",
            metadata={"branch_id": branch_id},
        )

    view = consumer_view_to_mapping(view_like)
    frame = extract_branch_frame(view, branch_id)
    surface = extract_family_surface(view, branch_id)
    common = extract_common(view)
    regime = normalize_regime(common.get("regime"))

    gates_ok, gates_reason = global_gates_pass(view)
    if not gates_ok:
        return no_signal_result(
            branch_id=branch_id,
            reason=gates_reason or "global_gates_failed",
        )

    family_status = as_mapping(view.get("family_status"))
    mist_status = as_mapping(family_status.get(FAMILY_ID))
    if mist_status and not safe_bool(mist_status.get("family_present"), False):
        return no_signal_result(
            branch_id=branch_id,
            reason="mist_family_not_present",
        )

    if not frame:
        return no_signal_result(
            branch_id=branch_id,
            reason="branch_frame_missing",
        )

    if not trend_direction_ok(view, branch_id, surface):
        return no_signal_result(
            branch_id=branch_id,
            reason="trend_direction_not_confirmed",
        )

    degraded_ok, degraded_reason = degraded_mode_entry_allowed(view, branch_id)
    if not degraded_ok:
        return blocked_result(
            branch_id=branch_id,
            code=degraded_reason or "degraded_mode_block",
            message="MIST degraded mode allows ATM only.",
            metadata={"runtime_mode": runtime_mode(view)},
        )

    score, score_parts = compute_score(
        view=view,
        branch_id=branch_id,
        surface=surface,
        frame=frame,
    )

    if not score_parts["context_pass"]:
        return no_signal_result(
            branch_id=branch_id,
            reason=safe_str(score_parts["context_blocker"], "context_failed"),
            metadata=score_parts,
        )

    min_score = min_score_for_regime(regime)
    if score < min_score:
        return no_signal_result(
            branch_id=branch_id,
            reason="score_below_threshold",
            metadata={
                "score": score,
                "min_score": min_score,
                "regime": regime,
                **dict(score_parts),
            },
        )

    if score_parts["futures_impulse_score"] < MIN_FUTURES_IMPULSE:
        return no_signal_result(
            branch_id=branch_id,
            reason="futures_impulse_insufficient",
            metadata=score_parts,
        )

    if score_parts["option_confirmation_score"] < MIN_OPTION_CONFIRMATION:
        return no_signal_result(
            branch_id=branch_id,
            reason="option_confirmation_insufficient",
            metadata=score_parts,
        )

    if score_parts["context_score"] < MIN_CONTEXT_SCORE:
        return no_signal_result(
            branch_id=branch_id,
            reason="context_score_insufficient",
            metadata=score_parts,
        )

    side = side_for_branch(branch_id)
    opt = selected_option(view, branch_id)

    instrument_key = (
        safe_str(frame.get("instrument_key"))
        or safe_str(opt.get("instrument_key"))
        or None
    )
    if not instrument_key:
        return no_signal_result(
            branch_id=branch_id,
            reason="instrument_key_missing",
        )

    tick_size = safe_float(
        opt.get("tick_size"),
        safe_float(frame.get("tick_size"), DEFAULT_TICK_SIZE),
    )
    if tick_size <= 0:
        tick_size = DEFAULT_TICK_SIZE

    candidate = MistCandidate(
        family_id=FAMILY_ID,
        doctrine_id=DOCTRINE_ID,
        branch_id=branch_id,
        side=side,
        action=action_for_branch(branch_id),
        score=round(score, 6),
        priority=round(score * 100.0, 6),
        instrument_key=instrument_key,
        instrument_token=safe_str(frame.get("instrument_token")) or safe_str(opt.get("instrument_token")) or None,
        option_symbol=safe_str(frame.get("option_symbol")) or safe_str(opt.get("option_symbol")) or safe_str(opt.get("trading_symbol")) or None,
        strike=(
            safe_float(frame.get("strike"))
            if frame.get("strike") not in (None, "")
            else safe_float(opt.get("strike")) if opt.get("strike") not in (None, "") else None
        ),
        option_price=(
            safe_float(frame.get("option_price"))
            if frame.get("option_price") not in (None, "")
            else safe_float(opt.get("ltp")) if opt.get("ltp") not in (None, "") else None
        ),
        tick_size=tick_size,
        quantity_lots_hint=safe_int(nested(view, "risk", "preview_quantity_lots", default=0), 0) or None,
        source_event_id=safe_str(surface.get("source_event_id")) or None,
        metadata={
            "regime": regime,
            "runtime_mode": runtime_mode(view),
            "score_parts": dict(score_parts),
            "surface_kind": safe_str(surface.get("surface_kind")),
            "setup_kind": "trend_pullback_resume",
        },
    )
    return candidate_result(candidate)


def evaluate(view_like: Any, branch_id: str | None = None) -> MistEvaluationResult:
    if branch_id is not None:
        return evaluate_branch(view_like, branch_id)

    for candidate_branch in SUPPORTED_BRANCHES:
        result = evaluate_branch(view_like, candidate_branch)
        if result.is_candidate or result.is_blocked:
            return result

    return no_signal_result(
        branch_id=None,
        reason="no_mist_branch_candidate",
    )


def evaluate_family(view_like: Any) -> MistEvaluationResult:
    return evaluate(view_like)


def evaluate_doctrine(view_like: Any, branch_id: str | None = None) -> MistEvaluationResult:
    return evaluate(view_like, branch_id=branch_id)


def get_evaluator():
    return evaluate


__all__ = [
    "FAMILY_ID",
    "DOCTRINE_ID",
    "MistBlocker",
    "MistCandidate",
    "MistEvaluationResult",
    "blocked_result",
    "candidate_result",
    "consumer_view_to_mapping",
    "evaluate",
    "evaluate_branch",
    "evaluate_doctrine",
    "evaluate_family",
    "get_evaluator",
    "no_signal_result",
]

# ===== BATCH1_STRATEGY_FAMILY_LEAF_CANDIDATE_CONTRACT START =====
# Batch 1 freeze-final guard:
# Doctrine leaves remain pure candidate evaluators, but any candidate emitted
# from this module must satisfy a minimum promotion-safe metadata contract.
#
# This does NOT promote candidates to live entries.
# This does NOT place orders.
# This does NOT mutate Redis / execution / risk / cooldown.
#
# It prevents report-only candidates from looking promotion-ready when runtime
# mode or order-critical metadata is incomplete.

_BATCH1_ORIGINAL_EVALUATE_BRANCH = evaluate_branch

if "runtime_mode" in globals():
    _BATCH1_ORIGINAL_RUNTIME_MODE = runtime_mode

    def runtime_mode(view: Mapping[str, Any]) -> str:
        common = extract_common(view)
        provider_runtime = extract_provider_runtime(view)

        text = (
            safe_str(common.get("strategy_runtime_mode_classic"))
            or safe_str(common.get("classic_runtime_mode"))
            or safe_str(provider_runtime.get("classic_runtime_mode"))
        )
        if not text:
            return RUNTIME_DISABLED

        normalized = text.upper().replace("-", "_")
        normal = safe_str(RUNTIME_NORMAL).upper().replace("-", "_")
        degraded = safe_str(RUNTIME_DHAN_DEGRADED).upper().replace("-", "_")
        disabled = safe_str(RUNTIME_DISABLED).upper().replace("-", "_")

        if normalized == normal:
            return RUNTIME_NORMAL
        if normalized == degraded:
            return RUNTIME_DHAN_DEGRADED
        if normalized == disabled:
            return RUNTIME_DISABLED
        return RUNTIME_DISABLED
else:
    _BATCH1_ORIGINAL_RUNTIME_MODE = None

if "normalize_mode" in globals():
    _BATCH1_ORIGINAL_NORMALIZE_MODE = normalize_mode

    def normalize_mode(value: Any) -> str:
        text = safe_str(value)
        if not text:
            return MODE_DISABLED

        normalized = text.upper().replace("_", "-")
        aliases = {
            "BASE-5DEPTH": MODE_BASE_5DEPTH,
            "BASE5DEPTH": MODE_BASE_5DEPTH,
            "DEPTH20-ENHANCED": MODE_DEPTH20_ENHANCED,
            "DEPTH20": MODE_DEPTH20_ENHANCED,
            "ENHANCED": MODE_DEPTH20_ENHANCED,
            "DISABLED": MODE_DISABLED,
        }
        return aliases.get(normalized, MODE_DISABLED)
else:
    _BATCH1_ORIGINAL_NORMALIZE_MODE = None


def _batch1_candidate_data(candidate: Any) -> dict[str, Any]:
    if candidate is None:
        return {}
    if hasattr(candidate, "to_dict"):
        try:
            data = candidate.to_dict()
            if isinstance(data, Mapping):
                return dict(data)
        except Exception:
            pass
    return as_mapping(candidate)


def _batch1_result_branch(result: Any, candidate_data: Mapping[str, Any]) -> str | None:
    return (
        safe_str(candidate_data.get("branch_id"))
        or safe_str(getattr(result, "branch_id", ""))
        or None
    )


def _batch1_contract_fail(
    result: Any,
    *,
    reason: str,
    candidate_data: Mapping[str, Any],
    extra: Mapping[str, Any] | None = None,
):
    branch_id = _batch1_result_branch(result, candidate_data)
    return no_signal_result(
        branch_id=branch_id,
        reason=reason,
        metadata={
            "batch1_leaf_candidate_contract_guard": True,
            "candidate_contract_reason": reason,
            "family_id": FAMILY_ID,
            "doctrine_id": DOCTRINE_ID,
            "candidate": dict(candidate_data),
            **dict(extra or {}),
        },
    )


def _batch1_candidate_contract_guard(result: Any):
    if not getattr(result, "is_candidate", False):
        return result

    candidate = getattr(result, "candidate", None)
    data = _batch1_candidate_data(candidate)
    if not data:
        return _batch1_contract_fail(
            result,
            reason="candidate_missing",
            candidate_data={},
        )

    branch_id = safe_str(data.get("branch_id"))
    action = safe_str(data.get("action"))
    expected_action = action_for_branch(branch_id) if branch_id in SUPPORTED_BRANCHES else ""

    if safe_str(data.get("family_id")) != FAMILY_ID:
        return _batch1_contract_fail(
            result,
            reason="candidate_family_mismatch",
            candidate_data=data,
        )

    if safe_str(data.get("doctrine_id")) != DOCTRINE_ID:
        return _batch1_contract_fail(
            result,
            reason="candidate_doctrine_mismatch",
            candidate_data=data,
        )

    if branch_id not in SUPPORTED_BRANCHES:
        return _batch1_contract_fail(
            result,
            reason="candidate_branch_invalid",
            candidate_data=data,
        )

    if action != expected_action:
        return _batch1_contract_fail(
            result,
            reason="candidate_action_mismatch",
            candidate_data=data,
            extra={"expected_action": expected_action, "actual_action": action},
        )

    score = safe_float(data.get("score"), -1.0)
    if score < 0.0 or score > 1.0:
        return _batch1_contract_fail(
            result,
            reason="candidate_score_out_of_range",
            candidate_data=data,
            extra={"score": score},
        )

    priority = safe_float(data.get("priority"), -1.0)
    if priority < 0.0:
        return _batch1_contract_fail(
            result,
            reason="candidate_priority_invalid",
            candidate_data=data,
            extra={"priority": priority},
        )

    instrument_key = safe_str(data.get("instrument_key"))
    instrument_token = safe_str(data.get("instrument_token"))
    option_symbol = safe_str(data.get("option_symbol"))
    strike_raw = data.get("strike")
    option_price_raw = data.get("option_price")

    strike_present = strike_raw not in (None, "") and safe_float(strike_raw, 0.0) > 0.0
    option_price = safe_float(option_price_raw, 0.0)
    tick_size = safe_float(data.get("tick_size"), 0.0)
    target_points = safe_float(data.get("target_points"), 0.0)
    stop_points = safe_float(data.get("stop_points"), 0.0)

    missing: list[str] = []
    if not instrument_key:
        missing.append("instrument_key")
    if not (instrument_token or option_symbol):
        missing.append("instrument_token_or_option_symbol")
    if not strike_present:
        missing.append("strike")
    if option_price <= 0.0:
        missing.append("option_price")
    if tick_size <= 0.0:
        missing.append("tick_size")

    if missing:
        return _batch1_contract_fail(
            result,
            reason="candidate_order_metadata_incomplete",
            candidate_data=data,
            extra={"missing": missing},
        )

    if round(target_points, 6) != round(TARGET_POINTS, 6):
        return _batch1_contract_fail(
            result,
            reason="candidate_target_points_mismatch",
            candidate_data=data,
            extra={"expected": TARGET_POINTS, "actual": target_points},
        )

    if round(stop_points, 6) != round(HARD_STOP_POINTS, 6):
        return _batch1_contract_fail(
            result,
            reason="candidate_stop_points_mismatch",
            candidate_data=data,
            extra={"expected": HARD_STOP_POINTS, "actual": stop_points},
        )

    return result


def evaluate_branch(view_like: Any, branch_id: str):
    result = _BATCH1_ORIGINAL_EVALUATE_BRANCH(view_like, branch_id)
    return _batch1_candidate_contract_guard(result)


def evaluate(view_like: Any, branch_id: str | None = None):
    if branch_id is not None:
        return evaluate_branch(view_like, branch_id)

    for candidate_branch in SUPPORTED_BRANCHES:
        result = evaluate_branch(view_like, candidate_branch)
        if result.is_candidate or result.is_blocked:
            return result

    return no_signal_result(
        branch_id=None,
        reason=f"no_{FAMILY_ID.lower()}_branch_candidate",
    )


def evaluate_family(view_like: Any):
    return evaluate(view_like)


def evaluate_doctrine(view_like: Any, branch_id: str | None = None):
    return evaluate(view_like, branch_id=branch_id)


def get_evaluator():
    return evaluate
# ===== BATCH1_STRATEGY_FAMILY_LEAF_CANDIDATE_CONTRACT END =====
