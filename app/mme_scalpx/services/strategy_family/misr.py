from __future__ import annotations

"""
app/mme_scalpx/services/strategy_family/misr.py

Freeze-grade MISR doctrine leaf evaluator for ScalpX MME.

Purpose
-------
This module OWNS:
- pure MISR CALL/PUT candidate evaluation from the already-built strategy
  consumer view / family feature surfaces
- deterministic no-signal / blocked / candidate result construction
- MISR-specific fakeout / absorption / reclaim / reversal support checks

This module DOES NOT own:
- Redis reads or writes
- feature computation
- strategy service publication
- broker calls
- execution mutation
- risk mutation
- cooldown mutation
- order placement

Frozen MISR identity
--------------------
MISR is the fakeout / reversal / range-reentry member of the MIS family.

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
from app.mme_scalpx.services.strategy_family import common as SF_COMMON
from app.mme_scalpx.services.strategy_family import event_registry as MISR_EVENT_REGISTRY


FAMILY_ID: Final[str] = getattr(N, "STRATEGY_FAMILY_MISR", "MISR")
DOCTRINE_ID: Final[str] = getattr(N, "DOCTRINE_MISR", "MISR")
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
ENTRY_MODE_UNKNOWN: Final[str] = getattr(N, "ENTRY_MODE_UNKNOWN", "UNKNOWN")

REGIME_LOWVOL: Final[str] = "LOWVOL"
REGIME_NORMAL: Final[str] = "NORMAL"
REGIME_FAST: Final[str] = "FAST"

SUPPORTED_BRANCHES: Final[tuple[str, str]] = (BRANCH_CALL, BRANCH_PUT)

TARGET_POINTS: Final[float] = 5.0
HARD_STOP_POINTS: Final[float] = 4.0
DEFAULT_TICK_SIZE: Final[float] = 0.05

MIN_SCORE_NORMAL: Final[float] = 0.55
MIN_SCORE_FAST: Final[float] = 0.59
MIN_SCORE_LOWVOL: Final[float] = 0.63

MIN_REVERSAL_STRUCTURE: Final[float] = 0.54
MIN_OPTION_CONFIRMATION: Final[float] = 0.50
MIN_CONTEXT_SCORE: Final[float] = 0.44

OI_WALL_HELP_DISTANCE_STRIKES: Final[float] = 1.25
OI_WALL_STRONG_MIN: Final[float] = 0.68
OI_WALL_VETO_DISTANCE_STRIKES: Final[float] = 0.50
OI_WALL_VETO_STRONG_MIN: Final[float] = 0.82


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



# BEGIN BATCH26D_STRATEGY_LEAF_REQUIRED_COMMON_SURFACE
def _batch26d_required_common_surface(container, key, *, family="MISR", source="unknown"):
    """
    Batch 26D fail-closed common-surface accessor.

    Required surfaces must not silently collapse to empty mappings:
    - view.provider_runtime
    - common.selected_option

    Missing/None/empty required surfaces become explicit blockers by raising
    RuntimeError before family eligibility can interpret absent data as safe.
    """
    sentinel = object()
    value = sentinel

    if container is None:
        raise RuntimeError(f"BATCH26D_REQUIRED_SURFACE_MISSING:{family}:{source}.{key}:container_none")

    if isinstance(container, dict):
        value = container.get(key, sentinel)
    else:
        getter = getattr(container, "get", None)
        if callable(getter):
            try:
                value = getter(key, sentinel)
            except TypeError:
                try:
                    value = getter(key)
                except Exception:
                    value = sentinel
            except Exception:
                value = sentinel

        if value is sentinel:
            try:
                value = getattr(container, key)
            except Exception:
                value = sentinel

    if value is sentinel:
        raise RuntimeError(f"BATCH26D_REQUIRED_SURFACE_MISSING:{family}:{source}.{key}:absent")

    if value is None:
        raise RuntimeError(f"BATCH26D_REQUIRED_SURFACE_MISSING:{family}:{source}.{key}:none")

    if isinstance(value, dict) and not value:
        raise RuntimeError(f"BATCH26D_REQUIRED_SURFACE_MISSING:{family}:{source}.{key}:empty")

    return value
# END BATCH26D_STRATEGY_LEAF_REQUIRED_COMMON_SURFACE

@dataclass(frozen=True, slots=True)
class MisrBlocker:
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
class MisrCandidate:
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
    setup_kind: str = "MISR_FAKEOUT_REVERSAL_RECLAIM"
    source_event_id: str | None = None
    trap_event_id: str | None = None
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
            "trap_event_id": self.trap_event_id,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class MisrEvaluationResult:
    family_id: str
    doctrine_id: str
    branch_id: str | None
    action: str
    is_candidate: bool
    is_blocked: bool
    candidate: MisrCandidate | None = None
    blocker: MisrBlocker | None = None
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
) -> MisrEvaluationResult:
    return MisrEvaluationResult(
        family_id=FAMILY_ID,
        doctrine_id=DOCTRINE_ID,
        branch_id=branch_id,
        action=ACTION_HOLD,
        is_candidate=False,
        is_blocked=False,
        metadata={"reason": reason, **dict(metadata or {})},
    )


def blocked_result(
    *,
    branch_id: str | None,
    code: str,
    message: str,
    metadata: Mapping[str, Any] | None = None,
) -> MisrEvaluationResult:
    return MisrEvaluationResult(
        family_id=FAMILY_ID,
        doctrine_id=DOCTRINE_ID,
        branch_id=branch_id,
        action=ACTION_HOLD,
        is_candidate=False,
        is_blocked=True,
        blocker=MisrBlocker(
            code=code,
            message=message,
            metadata=dict(metadata or {}),
        ),
        metadata={"reason": code, **dict(metadata or {})},
    )


def candidate_result(candidate: MisrCandidate) -> MisrEvaluationResult:
    return MisrEvaluationResult(
        family_id=FAMILY_ID,
        doctrine_id=DOCTRINE_ID,
        branch_id=candidate.branch_id,
        action=candidate.action,
        is_candidate=True,
        is_blocked=False,
        candidate=candidate,
        metadata={"reason": "misr_candidate_ready"},
    )


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
        "family_surfaces",
        "shared_core",
        "risk",
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
    return frame_to_mapping(frames.get(branch_frame_key(branch_id)))


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
    return as_mapping(family_status.get(FAMILY_ID))


def extract_common(view: Mapping[str, Any]) -> dict[str, Any]:
    return as_mapping(view.get("common"))


def extract_stage_flags(view: Mapping[str, Any]) -> dict[str, Any]:
    return as_mapping(view.get("stage_flags"))


def extract_provider_runtime(view: Mapping[str, Any]) -> dict[str, Any]:
    return as_mapping(_batch26d_required_common_surface(view, "provider_runtime", family="MISR", source="view"))


def runtime_mode(view: Mapping[str, Any]) -> str:
    return SF_COMMON.resolve_classic_runtime_mode(
        extract_common(view),
        extract_provider_runtime(view),
    )

def futures_block(view: Mapping[str, Any]) -> dict[str, Any]:
    common = extract_common(view)
    return as_mapping(common.get("futures")) or as_mapping(common.get("futures_features"))


def selected_option(view: Mapping[str, Any], branch_id: str) -> dict[str, Any]:
    common = extract_common(view)
    selected = as_mapping(_batch26d_required_common_surface(common, "selected_option", family="MISR", source="common"))
    side = side_for_branch(branch_id)
    if safe_str(selected.get("side")).upper() == side:
        return selected
    if branch_id == BRANCH_CALL:
        return as_mapping(common.get("call")) or as_mapping(common.get("selected_call"))
    return as_mapping(common.get("put")) or as_mapping(common.get("selected_put"))


def active_zone(view: Mapping[str, Any], surface: Mapping[str, Any]) -> dict[str, Any]:
    """
    Resolve MISR zone context from the richest available source.

    Real bridge views now carry family_surfaces. Older proofs may still carry
    active_zone under family_status/common, so this remains backward-compatible.
    """
    zone = as_mapping(surface.get("active_zone"))
    if zone:
        return zone

    zone = as_mapping(nested(view, "family_surfaces", "families", FAMILY_ID, "active_zone", default={}))
    if zone:
        return zone

    zone = as_mapping(nested(view, "family_surfaces", "families", FAMILY_ID, "zone_registry", "active_zone", default={}))
    if zone:
        return zone

    zone = as_mapping(nested(view, "family_status", FAMILY_ID, "active_zone", default={}))
    if zone:
        return zone

    return as_mapping(nested(view, "common", "active_zone", default={}))



def trap_event_consumed(view: Mapping[str, Any], trap_event_id: str) -> bool:
    """Return true when an external consumed-event registry blocks retry."""
    return MISR_EVENT_REGISTRY.is_trap_event_consumed(
        view,
        trap_event_id=trap_event_id,
        family_id=FAMILY_ID,
    )



def global_gates_pass(view: Mapping[str, Any]) -> tuple[bool, str | None]:
    if not safe_bool(view.get("safe_to_consume"), True):
        return False, "view_not_safe_to_consume"

    ok, reason = SF_COMMON.validate_global_stage_gates(extract_stage_flags(view))
    if not ok:
        return False, reason

    if runtime_mode(view) == RUNTIME_DISABLED:
        return False, "classic_runtime_disabled"

    return True, None


def reversal_direction_ok(view: Mapping[str, Any], branch_id: str, surface: Mapping[str, Any]) -> bool:
    if bool_any(surface, ("reversal_direction_ok", "direction_ok", "futures_bias_ok")):
        return True

    fut = futures_block(view)
    ofi = float_any(fut, ("ofi_ratio_proxy", "nof", "nof_slope", "weighted_ofi_persist"), 0.0)
    delta_3 = float_any(fut, ("delta_3",), 0.0)
    above_vwap = safe_bool(fut.get("above_vwap"), False)
    below_vwap = safe_bool(fut.get("below_vwap"), False)

    if branch_id == BRANCH_CALL:
        return bool(ofi >= -0.05 and delta_3 >= 0.0 and (above_vwap or delta_3 > 0.0))
    return bool(ofi <= 0.05 and delta_3 <= 0.0 and (below_vwap or delta_3 < 0.0))


def reversal_structure_score(
    view: Mapping[str, Any],
    branch_id: str,
    surface: Mapping[str, Any],
) -> float:
    explicit = float_any(surface, ("reversal_score", "trap_score", "fakeout_score"), -1.0)
    if explicit >= 0.0:
        return clamp(explicit, 0.0, 1.0)

    fake_break = bool_any(surface, ("fake_break_triggered", "fake_break_detected", "trap_detected", "trap_triggered"))
    absorption = bool_any(surface, ("absorption_pass", "absorption_ok"))
    reclaim = bool_any(surface, ("range_reentry_confirmed", "reclaim_ok", "reclaim_confirmed"))
    flow_flip = bool_any(surface, ("flow_flip_confirmed", "flow_flip_ok"))
    hold_inside = bool_any(surface, ("hold_inside_range_proved", "hold_proof_ok"))
    no_mans = bool_any(surface, ("no_mans_land_cleared", "zone_clearance_ok"))
    reversal_impulse = bool_any(surface, ("reversal_impulse_confirmed", "reversal_impulse_ok"))

    score = 0.0
    if fake_break:
        score += 0.22
    if absorption:
        score += 0.18
    if reclaim:
        score += 0.20
    if flow_flip:
        score += 0.14
    if hold_inside:
        score += 0.10
    if no_mans:
        score += 0.06
    if reversal_impulse:
        score += 0.10

    zone = active_zone(view, surface)
    if safe_bool(zone.get("zone_valid"), False) or safe_float(zone.get("quality_score"), 0.0) >= 0.45:
        score += 0.04

    return clamp(score, 0.0, 1.0)


def option_confirmation_score(
    view: Mapping[str, Any],
    branch_id: str,
    surface: Mapping[str, Any],
    frame: Mapping[str, Any],
) -> float:
    explicit = float_any(surface, ("option_confirmation_score", "option_response_score"), -1.0)
    if explicit >= 0.0:
        return clamp(explicit, 0.0, 1.0)

    opt = selected_option(view, branch_id)
    response = float_any(opt, ("response_efficiency",), 0.0)
    depth_ok = safe_bool(opt.get("depth_ok"), safe_bool(frame.get("tradability_ok"), False))
    tradability_ok = safe_bool(opt.get("tradability_ok"), safe_bool(frame.get("tradability_ok"), False))
    delta = abs(float_any(opt, ("delta_3",), 0.0))

    return clamp(
        response * 1.55
        + (0.22 if depth_ok else 0.0)
        + (0.26 if tradability_ok else 0.0)
        + min(delta, 3.0) / 3.0 * 0.18,
        0.0,
        1.0,
    )


def context_score(view: Mapping[str, Any], branch_id: str, surface: Mapping[str, Any]) -> tuple[float, bool, str | None]:
    explicit = float_any(surface, ("context_score", "oi_context_score"), -1.0)
    base = clamp(explicit, 0.0, 1.0) if explicit >= 0.0 else 0.60

    oi_wall = as_mapping(surface.get("oi_wall_context"))
    side_key = "call" if branch_id == BRANCH_CALL else "put"

    if not oi_wall:
        oi_wall = as_mapping(nested(view, "family_surfaces", "surfaces_by_branch", branch_frame_key(branch_id), "oi_wall_context", default={}))

    if not oi_wall:
        oi_wall = as_mapping(nested(view, "family_surfaces", "families", FAMILY_ID, "branches", branch_id, "oi_wall_context", default={}))

    if not oi_wall:
        oi_wall = as_mapping(nested(view, "shared_core", "oi_wall_context", side_key, default={}))

    if not oi_wall:
        oi_wall = as_mapping(nested(view, "common", "cross_option", f"{side_key}_oi_wall_context", default={}))

    distance = safe_float(oi_wall.get("distance_strikes"), 99.0)
    strength = safe_float(oi_wall.get("wall_strength"), 0.0)
    supportive = safe_bool(oi_wall.get("supportive"), False)

    if distance <= OI_WALL_VETO_DISTANCE_STRIKES and strength >= OI_WALL_VETO_STRONG_MIN and not supportive:
        return max(0.0, base - 0.40), False, "hostile_near_strong_oi_wall"

    if supportive and distance <= OI_WALL_HELP_DISTANCE_STRIKES and strength >= OI_WALL_STRONG_MIN:
        base = min(1.0, base + 0.08)

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
    reversal = reversal_structure_score(view, branch_id, surface)
    option = option_confirmation_score(view, branch_id, surface, frame)
    ctx_score, ctx_pass, ctx_blocker = context_score(view, branch_id, surface)
    direction_ok = reversal_direction_ok(view, branch_id, surface)

    score = clamp(
        reversal * 0.44
        + option * 0.30
        + ctx_score * 0.16
        + (0.10 if direction_ok else 0.0),
        0.0,
        1.0,
    )

    return score, {
        "reversal_structure_score": reversal,
        "option_confirmation_score": option,
        "context_score": ctx_score,
        "context_pass": ctx_pass,
        "context_blocker": ctx_blocker,
        "reversal_direction_ok": direction_ok,
    }


def degraded_mode_entry_allowed(view: Mapping[str, Any], branch_id: str) -> tuple[bool, str | None]:
    if runtime_mode(view) != RUNTIME_DHAN_DEGRADED:
        return True, None

    opt = selected_option(view, branch_id)
    entry_mode = safe_str(opt.get("entry_mode"), ENTRY_MODE_UNKNOWN).upper()
    if entry_mode in {ENTRY_MODE_ATM.upper(), "ATM"}:
        return True, None

    return False, "degraded_mode_requires_atm_only"


def evaluate_branch(view_like: Any, branch_id: str) -> MisrEvaluationResult:
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
    misr_status = as_mapping(family_status.get(FAMILY_ID))
    if misr_status and not safe_bool(misr_status.get("family_present"), False):
        return no_signal_result(
            branch_id=branch_id,
            reason="misr_family_not_present",
        )

    if not frame:
        return no_signal_result(
            branch_id=branch_id,
            reason="branch_frame_missing",
        )

    if not reversal_direction_ok(view, branch_id, surface):
        return no_signal_result(
            branch_id=branch_id,
            reason="reversal_direction_not_confirmed",
        )

    degraded_ok, degraded_reason = degraded_mode_entry_allowed(view, branch_id)
    if not degraded_ok:
        return blocked_result(
            branch_id=branch_id,
            code=degraded_reason or "degraded_mode_block",
            message="MISR degraded mode allows ATM only.",
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

    if score_parts["reversal_structure_score"] < MIN_REVERSAL_STRUCTURE:
        return no_signal_result(
            branch_id=branch_id,
            reason="reversal_structure_insufficient",
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

    opt = selected_option(view, branch_id)
    instrument_key = safe_str(frame.get("instrument_key")) or safe_str(opt.get("instrument_key")) or None
    if not instrument_key:
        return no_signal_result(
            branch_id=branch_id,
            reason="instrument_key_missing",
        )

    trap_event_id = safe_str(surface.get("trap_event_id"))
    if not trap_event_id:
        return no_signal_result(
            branch_id=branch_id,
            reason="trap_event_id_missing",
            metadata={"active_zone": active_zone(view, surface)},
        )

    if trap_event_consumed(view, trap_event_id):
        return no_signal_result(
            branch_id=branch_id,
            reason="trap_event_already_consumed",
            metadata={
                "trap_event_id": trap_event_id,
                "active_zone": active_zone(view, surface),
            },
        )

    tick_size = safe_float(
        opt.get("tick_size"),
        safe_float(frame.get("tick_size"), DEFAULT_TICK_SIZE),
    )
    if tick_size <= 0:
        tick_size = DEFAULT_TICK_SIZE

    candidate = MisrCandidate(
        family_id=FAMILY_ID,
        doctrine_id=DOCTRINE_ID,
        branch_id=branch_id,
        side=side_for_branch(branch_id),
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
        trap_event_id=trap_event_id,
        metadata={
            "regime": regime,
            "runtime_mode": runtime_mode(view),
            "score_parts": dict(score_parts),
            "surface_kind": safe_str(surface.get("surface_kind")),
            "setup_kind": "fakeout_absorption_reclaim_reversal",
            "trap_event_id": trap_event_id,
            "event_consumed": False,
            "active_zone": active_zone(view, surface),
        },
    )
    return candidate_result(candidate)


def evaluate(view_like: Any, branch_id: str | None = None) -> MisrEvaluationResult:
    if branch_id is not None:
        return evaluate_branch(view_like, branch_id)

    for candidate_branch in SUPPORTED_BRANCHES:
        result = evaluate_branch(view_like, candidate_branch)
        if result.is_candidate or result.is_blocked:
            return result

    return no_signal_result(
        branch_id=None,
        reason="no_misr_branch_candidate",
    )


def evaluate_family(view_like: Any) -> MisrEvaluationResult:
    return evaluate(view_like)


def evaluate_doctrine(view_like: Any, branch_id: str | None = None) -> MisrEvaluationResult:
    return evaluate(view_like, branch_id=branch_id)


def get_evaluator():
    return evaluate


__all__ = [
    "FAMILY_ID",
    "DOCTRINE_ID",
    "MisrBlocker",
    "MisrCandidate",
    "MisrEvaluationResult",
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

# =============================================================================
# Final freeze overrides: bridge-surface-aware lookups
# =============================================================================
#
# These override the earlier definitions by name. This is intentional:
# compute_score() and reversal_structure_score() resolve context_score() /
# active_zone() at call time, so the latest definitions below are used without
# touching the proven evaluator body.


def active_zone(view: Mapping[str, Any], surface: Mapping[str, Any]) -> dict[str, Any]:
    """
    Resolve MISR active zone from the richest available source.

    Priority:
    1. branch-local surface.active_zone
    2. family_surfaces.surfaces_by_branch.<misr_branch>.active_zone
    3. family_surfaces.families.MISR.active_zone
    4. family_surfaces.families.MISR.zone_registry.active_zone
    5. legacy family_status.MISR.active_zone
    6. common.active_zone
    """
    zone = as_mapping(surface.get("active_zone"))
    if zone:
        return zone

    branch_id = normalize_branch(surface.get("branch_id"))
    if branch_id:
        branch_key = branch_frame_key(branch_id)
        zone = as_mapping(
            nested(
                view,
                "family_surfaces",
                "surfaces_by_branch",
                branch_key,
                "active_zone",
                default={},
            )
        )
        if zone:
            return zone

    zone = as_mapping(
        nested(
            view,
            "family_surfaces",
            "families",
            FAMILY_ID,
            "active_zone",
            default={},
        )
    )
    if zone:
        return zone

    zone = as_mapping(
        nested(
            view,
            "family_surfaces",
            "families",
            FAMILY_ID,
            "zone_registry",
            "active_zone",
            default={},
        )
    )
    if zone:
        return zone

    zone = as_mapping(nested(view, "family_status", FAMILY_ID, "active_zone", default={}))
    if zone:
        return zone

    return as_mapping(nested(view, "common", "active_zone", default={}))


def _misr_oi_wall_context(
    view: Mapping[str, Any],
    branch_id: str,
    surface: Mapping[str, Any],
) -> dict[str, Any]:
    side_key = "call" if branch_id == BRANCH_CALL else "put"

    candidates = (
        as_mapping(surface.get("oi_wall_context")),
        as_mapping(
            nested(
                view,
                "family_surfaces",
                "surfaces_by_branch",
                branch_frame_key(branch_id),
                "oi_wall_context",
                default={},
            )
        ),
        as_mapping(
            nested(
                view,
                "family_surfaces",
                "families",
                FAMILY_ID,
                "branches",
                branch_id,
                "oi_wall_context",
                default={},
            )
        ),
        as_mapping(nested(view, "shared_core", "oi_wall_context", side_key, default={})),
        as_mapping(
            nested(
                view,
                "common",
                "cross_option",
                f"{side_key}_oi_wall_context",
                default={},
            )
        ),
    )

    for candidate in candidates:
        if candidate:
            return candidate

    return {}


def context_score(
    view: Mapping[str, Any],
    branch_id: str,
    surface: Mapping[str, Any],
) -> tuple[float, bool, str | None]:
    """
    Resolve MISR context score with medium OI-wall filtering.

    MISR uses OI wall as reversal/fakeout context. A supportive nearby wall can
    improve context slightly, while a hostile very-near strong wall blocks.
    """
    explicit = float_any(surface, ("context_score", "oi_context_score"), -1.0)
    base = clamp(explicit, 0.0, 1.0) if explicit >= 0.0 else 0.60

    oi_wall = _misr_oi_wall_context(view, branch_id, surface)
    distance = safe_float(oi_wall.get("distance_strikes"), 99.0)
    strength = safe_float(oi_wall.get("wall_strength"), 0.0)
    supportive = safe_bool(oi_wall.get("supportive"), False)

    if (
        distance <= OI_WALL_VETO_DISTANCE_STRIKES
        and strength >= OI_WALL_VETO_STRONG_MIN
        and not supportive
    ):
        return max(0.0, base - 0.40), False, "hostile_near_strong_oi_wall"

    if supportive and distance <= OI_WALL_HELP_DISTANCE_STRIKES and strength >= OI_WALL_STRONG_MIN:
        base = min(1.0, base + 0.08)

    return base, True, None

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
        return SF_COMMON.resolve_classic_runtime_mode(
            extract_common(view),
            extract_provider_runtime(view),
        )

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


# =============================================================================
# Batch 25P candidate metadata standardization
# =============================================================================
#
# This wrapper standardizes candidate.metadata after doctrine evaluation. It does
# not promote candidates, publish strategy decisions, call risk, or call execution.

if "_BATCH25P_ORIGINAL_EVALUATE_BRANCH" not in globals():
    _BATCH25P_ORIGINAL_EVALUATE_BRANCH = evaluate_branch
    _BATCH25P_ORIGINAL_EVALUATE = evaluate


def _batch25p_standardize_candidate_result(view_like: Any, result: Any) -> Any:
    return SF_COMMON.standardize_candidate_result(
        result,
        view_like=view_like,
        family_id=FAMILY_ID,
        doctrine_id=DOCTRINE_ID,
    )


def evaluate_branch(view_like: Any, branch_id: str):
    result = _BATCH25P_ORIGINAL_EVALUATE_BRANCH(view_like, branch_id)
    return _batch25p_standardize_candidate_result(view_like, result)


def evaluate(view_like: Any, branch_id: str | None = None):
    if branch_id is not None:
        return evaluate_branch(view_like, branch_id)

    for candidate_branch in SUPPORTED_BRANCHES:
        result = evaluate_branch(view_like, candidate_branch)
        if result.is_candidate or result.is_blocked:
            return result

    return no_signal_result(
        branch_id=None,
        reason="all_branches_no_signal",
        metadata={"family_id": FAMILY_ID},
    )


# BEGIN BATCH26E_MISR_TRAP_EVENT_CONSUMPTION_REGISTRY
BATCH26E_MISR_TRAP_EVENT_CONSUMED_BLOCKER = "MISR_TRAP_EVENT_CONSUMED_NO_RETRY"
BATCH26E_MISR_TRAP_EVENT_MISSING_BLOCKER = "MISR_TRAP_EVENT_ID_MISSING"
BATCH26E_MISR_TRAP_EVENT_INVALID_BLOCKER = "MISR_TRAP_EVENT_ID_INVALID"

# Process-local deterministic consumed-event registry.
# This is intentionally strategy-local and blocks retrying the same trap event
# after an entry-like decision has been emitted for that event.
_BATCH26E_MISR_CONSUMED_TRAP_EVENTS = {}
_BATCH26E_MISR_LATEST_CONSUMED_BY_ZONE_SIDE = {}
_BATCH26E_MISR_ACTIVE_SESSION_KEY = None


def _batch26e_truthy(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {
        "1", "true", "yes", "y", "on", "enabled", "allow", "allowed", "pass", "passed", "ok", "ready"
    }


def _batch26e_falsey(value):
    if isinstance(value, bool):
        return value is False
    if value is None:
        return False
    return str(value).strip().lower() in {
        "0", "false", "no", "n", "off", "disabled", "deny", "denied", "blocked", "fail", "failed"
    }


def _batch26e_get(obj, names, default=None):
    if isinstance(names, str):
        names = [names]
    if obj is None:
        return default
    if isinstance(obj, dict):
        for name in names:
            if name in obj:
                return obj.get(name)
        return default
    for name in names:
        try:
            if hasattr(obj, name):
                return getattr(obj, name)
        except Exception:
            pass
    return default


def _batch26e_iter_children(obj):
    if isinstance(obj, dict):
        for child in obj.values():
            yield child
    elif isinstance(obj, (list, tuple)):
        for child in obj:
            yield child
    else:
        for attr in (
            "stage",
            "stage_flags",
            "metadata",
            "meta",
            "surface",
            "features",
            "family_features",
            "family_surface",
            "candidate",
            "decision",
            "context",
            "event",
            "trap_event",
            "active_zone",
            "zone",
        ):
            try:
                child = getattr(obj, attr)
            except Exception:
                child = None
            if child is not None:
                yield child


def _batch26e_deep_find(obj, names, max_depth=7):
    names = set(names)
    seen = set()

    def walk(value, depth):
        if depth > max_depth:
            return None
        ident = id(value)
        if ident in seen:
            return None
        seen.add(ident)

        found = _batch26e_get(value, names, None)
        if found is not None:
            return found

        for child in _batch26e_iter_children(value):
            result = walk(child, depth + 1)
            if result is not None:
                return result
        return None

    return walk(obj, 0)


def _batch26e_extract_trap_event_id(*objs):
    for obj in objs:
        value = _batch26e_deep_find(
            obj,
            {
                "trap_event_id",
                "misr_trap_event_id",
                "event_id",
            },
        )
        if value is not None:
            text = str(value).strip()
            if text:
                return text
    return None


def _batch26e_extract_session_key(*objs):
    for obj in objs:
        value = _batch26e_deep_find(
            obj,
            {
                "session_key",
                "session_id",
                "trading_session",
                "trading_date",
                "session_date",
                "market_session_date",
            },
        )
        if value is not None:
            text = str(value).strip()
            if text:
                return text
    return None


def _batch26e_parse_trap_event_id(trap_event_id):
    """
    Contract format:
    {branch_side}|{active_zone_id}|{fake_break_start_ts_epoch_ms}|{fake_break_extreme_ts_epoch_ms}
    """
    if trap_event_id is None:
        return {
            "valid": False,
            "error": "missing",
            "trap_event_id": None,
        }

    text = str(trap_event_id).strip()
    parts = text.split("|")
    if len(parts) != 4:
        return {
            "valid": False,
            "error": "expected_4_pipe_separated_parts",
            "trap_event_id": text,
            "parts": parts,
        }

    side, zone_id, start_ms, extreme_ms = [p.strip() for p in parts]
    if side not in {"CALL", "PUT"}:
        return {
            "valid": False,
            "error": "invalid_side",
            "trap_event_id": text,
            "side": side,
            "zone_id": zone_id,
            "start_ms": start_ms,
            "extreme_ms": extreme_ms,
        }

    try:
        start_i = int(float(start_ms))
        extreme_i = int(float(extreme_ms))
    except Exception:
        return {
            "valid": False,
            "error": "invalid_timestamp",
            "trap_event_id": text,
            "side": side,
            "zone_id": zone_id,
            "start_ms": start_ms,
            "extreme_ms": extreme_ms,
        }

    if not zone_id:
        return {
            "valid": False,
            "error": "missing_zone_id",
            "trap_event_id": text,
            "side": side,
            "zone_id": zone_id,
            "start_ms": start_i,
            "extreme_ms": extreme_i,
        }

    return {
        "valid": True,
        "trap_event_id": text,
        "side": side,
        "zone_id": zone_id,
        "zone_side_key": f"{side}|{zone_id}",
        "fake_break_start_ts_epoch_ms": start_i,
        "fake_break_extreme_ts_epoch_ms": extreme_i,
    }


def _batch26e_reset_misr_trap_event_registry(reason="manual_reset"):
    _BATCH26E_MISR_CONSUMED_TRAP_EVENTS.clear()
    _BATCH26E_MISR_LATEST_CONSUMED_BY_ZONE_SIDE.clear()
    return {
        "reset": True,
        "reason": reason,
        "consumed_count": 0,
    }


def _batch26e_update_session_from_objects(*objs):
    global _BATCH26E_MISR_ACTIVE_SESSION_KEY

    session_key = _batch26e_extract_session_key(*objs)
    if not session_key:
        return {
            "session_key": _BATCH26E_MISR_ACTIVE_SESSION_KEY,
            "reset": False,
        }

    if _BATCH26E_MISR_ACTIVE_SESSION_KEY is None:
        _BATCH26E_MISR_ACTIVE_SESSION_KEY = session_key
        return {
            "session_key": session_key,
            "reset": False,
        }

    if session_key != _BATCH26E_MISR_ACTIVE_SESSION_KEY:
        old = _BATCH26E_MISR_ACTIVE_SESSION_KEY
        _BATCH26E_MISR_ACTIVE_SESSION_KEY = session_key
        _batch26e_reset_misr_trap_event_registry(reason=f"session_change:{old}->{session_key}")
        return {
            "session_key": session_key,
            "reset": True,
            "old_session_key": old,
        }

    return {
        "session_key": session_key,
        "reset": False,
    }


def _batch26e_misr_trap_event_consumed_status(trap_event_id):
    parsed = _batch26e_parse_trap_event_id(trap_event_id)
    if not parsed.get("valid"):
        return {
            "blocked": True,
            "reason": BATCH26E_MISR_TRAP_EVENT_INVALID_BLOCKER,
            "parsed": parsed,
        }

    event_id = parsed["trap_event_id"]
    if event_id in _BATCH26E_MISR_CONSUMED_TRAP_EVENTS:
        return {
            "blocked": True,
            "reason": BATCH26E_MISR_TRAP_EVENT_CONSUMED_BLOCKER,
            "parsed": parsed,
            "existing": _BATCH26E_MISR_CONSUMED_TRAP_EVENTS.get(event_id),
        }

    zone_key = parsed["zone_side_key"]
    latest = _BATCH26E_MISR_LATEST_CONSUMED_BY_ZONE_SIDE.get(zone_key)
    if latest is not None:
        latest_start = int(latest.get("fake_break_start_ts_epoch_ms", -1))
        if int(parsed["fake_break_start_ts_epoch_ms"]) <= latest_start:
            return {
                "blocked": True,
                "reason": BATCH26E_MISR_TRAP_EVENT_CONSUMED_BLOCKER,
                "parsed": parsed,
                "zone_latest": latest,
            }

    return {
        "blocked": False,
        "reason": "",
        "parsed": parsed,
    }


def _batch26e_consume_misr_trap_event(trap_event_id, *, consume_reason="entry_decision_emitted"):
    parsed = _batch26e_parse_trap_event_id(trap_event_id)
    if not parsed.get("valid"):
        return {
            "consumed": False,
            "reason": BATCH26E_MISR_TRAP_EVENT_INVALID_BLOCKER,
            "parsed": parsed,
        }

    record = {
        "trap_event_id": parsed["trap_event_id"],
        "side": parsed["side"],
        "zone_id": parsed["zone_id"],
        "zone_side_key": parsed["zone_side_key"],
        "fake_break_start_ts_epoch_ms": parsed["fake_break_start_ts_epoch_ms"],
        "fake_break_extreme_ts_epoch_ms": parsed["fake_break_extreme_ts_epoch_ms"],
        "consume_reason": consume_reason,
    }
    _BATCH26E_MISR_CONSUMED_TRAP_EVENTS[parsed["trap_event_id"]] = record
    _BATCH26E_MISR_LATEST_CONSUMED_BY_ZONE_SIDE[parsed["zone_side_key"]] = record
    return {
        "consumed": True,
        "record": record,
    }


def _batch26e_result_is_entry_like(result):
    if isinstance(result, bool):
        return result is True

    if isinstance(result, dict):
        action = str(result.get("action", "") or result.get("decision", "") or result.get("strategy_action", "")).upper()
        state = str(result.get("state", "") or result.get("next_state", "")).upper()

        if action.startswith("ENTER") or action in {"BUY", "ENTRY", "OPEN", "ENTER_CALL", "ENTER_PUT"}:
            return True
        if state in {"ENTRY_PENDING", "POSITION_OPEN"}:
            return True

        for key in (
            "entry_allowed",
            "entry_ready",
            "eligible",
            "candidate",
            "candidate_found",
            "decision_allowed",
            "trade_allowed",
            "allow_entry",
        ):
            if key in result and _batch26e_truthy(result.get(key)):
                return True

        return False

    for attr in ("action", "decision", "strategy_action"):
        value = _batch26e_get(result, attr)
        if value is not None:
            action = str(value).upper()
            if action.startswith("ENTER") or action in {"BUY", "ENTRY", "OPEN", "ENTER_CALL", "ENTER_PUT"}:
                return True

    for attr in (
        "entry_allowed",
        "entry_ready",
        "eligible",
        "candidate",
        "candidate_found",
        "decision_allowed",
        "trade_allowed",
        "allow_entry",
    ):
        value = _batch26e_get(result, attr)
        if value is not None and _batch26e_truthy(value):
            return True

    return False


def _batch26e_append_blocker_to_dict(result, blocker, details=None):
    existing = result.get("blockers")
    if isinstance(existing, list):
        existing.append(blocker)
    elif existing:
        result["blockers"] = [existing, blocker]
    else:
        result["blockers"] = [blocker]

    existing_reasons = result.get("blocker_reasons")
    if isinstance(existing_reasons, list):
        existing_reasons.append(blocker)
    elif existing_reasons:
        result["blocker_reasons"] = [existing_reasons, blocker]
    else:
        result["blocker_reasons"] = [blocker]

    result["misr_trap_event_consumed_blocked"] = True
    result["misr_trap_event_consumption_registry_reason"] = blocker
    if details is not None:
        result["misr_trap_event_consumption_registry_detail"] = str(details)

    for key in (
        "eligible",
        "entry_allowed",
        "entry_ready",
        "candidate",
        "candidate_found",
        "decision_allowed",
        "trade_allowed",
        "allow_entry",
        "signal",
        "ready",
    ):
        if key in result:
            result[key] = False

    action = str(result.get("action", "") or "").upper()
    if action.startswith("ENTER") or action in {"BUY", "ENTRY", "OPEN", "ENTER_CALL", "ENTER_PUT"}:
        result["action_before_misr_trap_consumed_block"] = action
        result["action"] = "HOLD"

    if "reason_code" not in result:
        result["reason_code"] = blocker
    if "reason" not in result:
        result["reason"] = blocker

    return result


def _batch26e_block_result(result, blocker, details=None):
    if isinstance(result, bool):
        return False

    if isinstance(result, dict):
        return _batch26e_append_blocker_to_dict(result, blocker, details)

    if isinstance(result, list):
        return [_batch26e_block_result(item, blocker, details) for item in result]

    if isinstance(result, tuple):
        return tuple(_batch26e_block_result(item, blocker, details) for item in result)

    mutated = False
    for attr in (
        "eligible",
        "entry_allowed",
        "entry_ready",
        "candidate",
        "candidate_found",
        "decision_allowed",
        "trade_allowed",
        "allow_entry",
        "signal",
        "ready",
    ):
        try:
            if hasattr(result, attr):
                setattr(result, attr, False)
                mutated = True
        except Exception:
            pass

    for attr in ("blockers", "blocker_reasons"):
        try:
            current = getattr(result, attr)
            if isinstance(current, list):
                current.append(blocker)
            else:
                setattr(result, attr, [current, blocker] if current else [blocker])
            mutated = True
        except Exception:
            try:
                setattr(result, attr, [blocker])
                mutated = True
            except Exception:
                pass

    try:
        action = str(getattr(result, "action", "") or "").upper()
        if action.startswith("ENTER") or action in {"BUY", "ENTRY", "OPEN", "ENTER_CALL", "ENTER_PUT"}:
            setattr(result, "action_before_misr_trap_consumed_block", action)
            setattr(result, "action", "HOLD")
            mutated = True
    except Exception:
        pass

    try:
        setattr(result, "misr_trap_event_consumed_blocked", True)
        setattr(result, "misr_trap_event_consumption_registry_reason", blocker)
        setattr(result, "misr_trap_event_consumption_registry_detail", str(details))
        mutated = True
    except Exception:
        pass

    return result if mutated else result


def _batch26e_should_wrap_name(name):
    lowered = str(name).lower()
    if lowered.startswith("_batch26e"):
        return False
    if lowered.startswith("__"):
        return False

    needles = (
        "evaluat",
        "eligib",
        "candidate",
        "decision",
        "decide",
        "entry",
        "signal",
        "select",
        "resolve",
        "confirm",
        "trap",
        "fake",
        "range",
        "impulse",
    )
    return any(n in lowered for n in needles)


def _batch26e_wrap_function(fn):
    import functools

    if getattr(fn, "_batch26e_misr_registry_wrapped", False):
        return fn

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        _batch26e_update_session_from_objects(args, kwargs)

        result = fn(*args, **kwargs)

        _batch26e_update_session_from_objects(args, kwargs, result)

        trap_event_id = _batch26e_extract_trap_event_id(args, kwargs, result)
        if not trap_event_id:
            return result

        consumed_status = _batch26e_misr_trap_event_consumed_status(trap_event_id)
        if consumed_status.get("blocked") is True:
            return _batch26e_block_result(result, consumed_status.get("reason"), consumed_status)

        if _batch26e_result_is_entry_like(result):
            _batch26e_consume_misr_trap_event(
                trap_event_id,
                consume_reason="entry_like_decision_emitted",
            )

        return result

    wrapper._batch26e_misr_registry_wrapped = True
    return wrapper


def _batch26e_install_misr_trap_event_registry(module_globals):
    import inspect

    installed = []

    for name, obj in list(module_globals.items()):
        if not _batch26e_should_wrap_name(name):
            continue

        if inspect.isfunction(obj) and getattr(obj, "__module__", None) == module_globals.get("__name__"):
            module_globals[name] = _batch26e_wrap_function(obj)
            installed.append(name)

        elif inspect.isclass(obj) and getattr(obj, "__module__", None) == module_globals.get("__name__"):
            for attr_name, attr_value in list(obj.__dict__.items()):
                if not _batch26e_should_wrap_name(attr_name):
                    continue

                raw = attr_value
                descriptor_type = None
                if isinstance(raw, staticmethod):
                    descriptor_type = staticmethod
                    raw = raw.__func__
                elif isinstance(raw, classmethod):
                    descriptor_type = classmethod
                    raw = raw.__func__

                if inspect.isfunction(raw):
                    wrapped = _batch26e_wrap_function(raw)
                    if descriptor_type is staticmethod:
                        setattr(obj, attr_name, staticmethod(wrapped))
                    elif descriptor_type is classmethod:
                        setattr(obj, attr_name, classmethod(wrapped))
                    else:
                        setattr(obj, attr_name, wrapped)
                    installed.append(f"{name}.{attr_name}")

    module_globals["BATCH26E_MISR_TRAP_EVENT_REGISTRY_INSTALLED"] = True
    module_globals["BATCH26E_MISR_TRAP_EVENT_REGISTRY_WRAPPERS"] = tuple(sorted(set(installed)))
    return installed


BATCH26E_MISR_TRAP_EVENT_REGISTRY_WRAPPERS = tuple(
    _batch26e_install_misr_trap_event_registry(globals())
)
# END BATCH26E_MISR_TRAP_EVENT_CONSUMPTION_REGISTRY



# ===== BATCH26_OI_C_FAMILY_SOFT_SCORING_ONLY START =====
# Batch 26-OI-C freeze-final law:
# - OI / Dhan option-ladder context is score context only in this strategy leaf.
# - OI wall context may reduce or improve context_score.
# - OI wall context may NOT create a hard entry blocker.
# - No live-order promotion is introduced here.
# - No risk/execution/Redis side effect is introduced here.
# - Canonical OI wall calculation remains owned by strike_selection.py.

_BATCH26_OI_C_FAMILY_ID = "MISR"
_BATCH26_OI_C_SOFT_POLICY = "registered_zone_support_context_only"
_BATCH26_OI_C_SOFT_POLICY_DESCRIPTION = "MISR uses OI wall only to support registered ORB/SWING zone context."
_BATCH26_OI_C_ORIGINAL_CONTEXT_SCORE = context_score

_BATCH26_OI_C_BLOCKER_TOKENS = (
    "oi_wall",
    "near_strong_oi_wall",
    "hostile_near_strong_oi_wall",
    "extreme_near_hostile_oi_wall",
)

def _batch26_oi_c_side_key(branch_id):
    try:
        return "call" if branch_id == BRANCH_CALL else "put"
    except Exception:
        text = str(branch_id or "").upper()
        return "call" if "CALL" in text else "put"

def _batch26_oi_c_as_mapping(value):
    try:
        return as_mapping(value)
    except Exception:
        return value if isinstance(value, dict) else {}

def _batch26_oi_c_nested(mapping, *path):
    try:
        return nested(mapping, *path, default={})
    except Exception:
        return {}

def _batch26_oi_c_has_oi_context(view, branch_id, surface):
    side_key = _batch26_oi_c_side_key(branch_id)
    probes = []

    try:
        probes.append(surface.get("oi_wall_context"))
    except Exception:
        pass

    probes.append(_batch26_oi_c_nested(view, "oi_wall_context", side_key))
    probes.append(_batch26_oi_c_nested(view, "shared_core", "oi_wall_context", side_key))
    probes.append(_batch26_oi_c_nested(view, "shared_core", "strike_selection", "oi_wall_context", side_key))
    probes.append(_batch26_oi_c_nested(view, "common", "cross_option", f"{side_key}_oi_wall_context"))

    try:
        if "branch_frame_key" in globals():
            branch_key = branch_frame_key(branch_id)
            probes.append(_batch26_oi_c_nested(view, "family_surfaces", "surfaces_by_branch", branch_key, "oi_wall_context"))
    except Exception:
        pass

    try:
        probes.append(_batch26_oi_c_nested(view, "family_surfaces", "families", FAMILY_ID, "branches", branch_id, "oi_wall_context"))
    except Exception:
        pass

    for probe in probes:
        item = _batch26_oi_c_as_mapping(probe)
        if item:
            return True

    return False

def _batch26_oi_c_reason_text(reason):
    try:
        return safe_str(reason, "").lower()
    except Exception:
        return str(reason or "").lower()

def _batch26_oi_c_min_context_score():
    try:
        return float(MIN_CONTEXT_SCORE)
    except Exception:
        return 0.0

def context_score(view, branch_id, surface):
    score, passed, reason = _BATCH26_OI_C_ORIGINAL_CONTEXT_SCORE(view, branch_id, surface)

    reason_text = _batch26_oi_c_reason_text(reason)
    reason_is_oi = any(token in reason_text for token in _BATCH26_OI_C_BLOCKER_TOKENS)
    has_oi_context = _batch26_oi_c_has_oi_context(view, branch_id, surface) or reason_is_oi

    if not has_oi_context:
        return score, passed, reason

    soft_floor = _batch26_oi_c_min_context_score()

    # OI-specific blockers become soft metadata and score shaping only.
    if not passed and reason_is_oi:
        return max(float(score), soft_floor), True, f"soft_only_{reason or 'oi_context'}"

    # If canonical OI context dragged context_score below the later MIN_CONTEXT_SCORE
    # gate, floor it to the minimum passing context so OI remains soft. The aggregate
    # family score can still fail normally through score_below_threshold.
    if float(score) < soft_floor:
        return soft_floor, True, "soft_only_oi_context_floor"

    return score, passed, reason

# ===== BATCH26_OI_C_FAMILY_SOFT_SCORING_ONLY END =====

