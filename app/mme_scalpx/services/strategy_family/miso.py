from __future__ import annotations

"""
app/mme_scalpx/services/strategy_family/miso.py

Freeze-grade MISO doctrine leaf evaluator for ScalpX MME.

Purpose
-------
This module OWNS:
- pure MISO CALL/PUT candidate evaluation from the already-built strategy
  consumer view / family feature surfaces
- deterministic no-signal / blocked / candidate result construction
- MISO-specific option-led burst / aggression / tape-speed / imbalance /
  queue-reload / futures-veto support checks

This module DOES NOT own:
- Redis reads or writes
- feature computation
- strategy service publication
- broker calls
- execution mutation
- risk mutation
- cooldown mutation
- order placement

Frozen MISO identity
--------------------
MISO is the option-led, futures-aligned, futures-vetoed intraday
microstructure burst scalper.

It is:
- option-led
- Dhan market-data/context mandatory
- futures-aligned / futures-vetoed
- intraday-only
- short-hold
- single-position compatible
- no same-burst re-entry
- 5-point first-target oriented

This leaf evaluates candidate support only. It does not publish decisions.
"""

import math
from dataclasses import dataclass, field
from typing import Any, Final, Mapping, Sequence

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services.strategy_family import common as SF_COMMON


FAMILY_ID: Final[str] = getattr(N, "STRATEGY_FAMILY_MISO", "MISO")
DOCTRINE_ID: Final[str] = getattr(N, "DOCTRINE_MISO", "MISO")

BRANCH_CALL: Final[str] = getattr(N, "BRANCH_CALL", "CALL")
BRANCH_PUT: Final[str] = getattr(N, "BRANCH_PUT", "PUT")
SIDE_CALL: Final[str] = getattr(N, "SIDE_CALL", "CALL")
SIDE_PUT: Final[str] = getattr(N, "SIDE_PUT", "PUT")

PROVIDER_DHAN: Final[str] = getattr(N, "PROVIDER_DHAN", "DHAN")
PROVIDER_ZERODHA: Final[str] = getattr(N, "PROVIDER_ZERODHA", "ZERODHA")
PROVIDER_STATUS_HEALTHY: Final[str] = getattr(N, "PROVIDER_STATUS_HEALTHY", "HEALTHY")
PROVIDER_STATUS_OK: Final[str] = "OK"

ACTION_ENTER_CALL: Final[str] = getattr(N, "ACTION_ENTER_CALL", "ENTER_CALL")
ACTION_ENTER_PUT: Final[str] = getattr(N, "ACTION_ENTER_PUT", "ENTER_PUT")
ACTION_HOLD: Final[str] = getattr(N, "ACTION_HOLD", "HOLD")

MODE_BASE_5DEPTH: Final[str] = getattr(N, "STRATEGY_RUNTIME_MODE_BASE_5DEPTH", "BASE-5DEPTH")
MODE_DEPTH20_ENHANCED: Final[str] = getattr(N, "STRATEGY_RUNTIME_MODE_DEPTH20_ENHANCED", "DEPTH20-ENHANCED")
MODE_DISABLED: Final[str] = getattr(N, "STRATEGY_RUNTIME_MODE_DISABLED", "DISABLED")

REGIME_LOWVOL: Final[str] = "LOWVOL"
REGIME_NORMAL: Final[str] = "NORMAL"
REGIME_FAST: Final[str] = "FAST"

SUPPORTED_BRANCHES: Final[tuple[str, str]] = (BRANCH_CALL, BRANCH_PUT)

TARGET_POINTS: Final[float] = 5.0
HARD_STOP_POINTS: Final[float] = 4.0
DEFAULT_TICK_SIZE: Final[float] = 0.05

MIN_SCORE_BASE: Final[float] = 0.58
MIN_SCORE_DEPTH20: Final[float] = 0.56
MIN_SCORE_FAST: Final[float] = 0.60
MIN_SCORE_LOWVOL: Final[float] = 0.64

MIN_BURST_SCORE: Final[float] = 0.55
MIN_TAPE_SCORE: Final[float] = 0.50
MIN_TRADABILITY_SCORE: Final[float] = 0.50
MIN_FUTURES_ALIGNMENT_SCORE: Final[float] = 0.45

OI_WALL_EXTREME_DISTANCE_STRIKES: Final[float] = 0.35
OI_WALL_EXTREME_STRENGTH_MIN: Final[float] = 0.86


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


def normalize_mode(value: Any) -> str:
    return SF_COMMON.normalize_miso_runtime_mode(value)

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


# =============================================================================
# Result contracts
# =============================================================================


@dataclass(frozen=True, slots=True)
class MisoBlocker:
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
class MisoCandidate:
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
    setup_kind: str = "MISO_OPTION_LED_BURST"
    mode: str = MODE_BASE_5DEPTH
    burst_event_id: str | None = None
    selected_side: str | None = None
    selected_strike: float | None = None
    shadow_call_strike: float | None = None
    shadow_put_strike: float | None = None
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
            "mode": self.mode,
            "burst_event_id": self.burst_event_id,
            "selected_side": self.selected_side,
            "selected_strike": self.selected_strike,
            "shadow_call_strike": self.shadow_call_strike,
            "shadow_put_strike": self.shadow_put_strike,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class MisoEvaluationResult:
    family_id: str
    doctrine_id: str
    branch_id: str | None
    action: str
    is_candidate: bool
    is_blocked: bool
    candidate: MisoCandidate | None = None
    blocker: MisoBlocker | None = None
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
) -> MisoEvaluationResult:
    return MisoEvaluationResult(
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
) -> MisoEvaluationResult:
    return MisoEvaluationResult(
        family_id=FAMILY_ID,
        doctrine_id=DOCTRINE_ID,
        branch_id=branch_id,
        action=ACTION_HOLD,
        is_candidate=False,
        is_blocked=True,
        candidate=None,
        blocker=MisoBlocker(
            code=code,
            message=message,
            metadata=dict(metadata or {}),
        ),
        metadata={"reason": code, **dict(metadata or {})},
    )


def candidate_result(candidate: MisoCandidate) -> MisoEvaluationResult:
    return MisoEvaluationResult(
        family_id=FAMILY_ID,
        doctrine_id=DOCTRINE_ID,
        branch_id=candidate.branch_id,
        action=candidate.action,
        is_candidate=True,
        is_blocked=False,
        candidate=candidate,
        blocker=None,
        metadata={"reason": "miso_candidate_ready"},
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
        "family_surfaces",
        "shared_core",
        "oi_wall_context",
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


def extract_family_status(view: Mapping[str, Any]) -> dict[str, Any]:
    return as_mapping(nested(view, "family_status", FAMILY_ID, default={}))


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

    status = extract_family_status(view)
    if branch_id == BRANCH_CALL:
        return as_mapping(status.get("call_support")) or as_mapping(nested(status, "branches", BRANCH_CALL, default={}))
    return as_mapping(status.get("put_support")) or as_mapping(nested(status, "branches", BRANCH_PUT, default={}))


def extract_common(view: Mapping[str, Any]) -> dict[str, Any]:
    return as_mapping(view.get("common"))


def extract_stage_flags(view: Mapping[str, Any]) -> dict[str, Any]:
    return as_mapping(view.get("stage_flags"))


def extract_provider_runtime(view: Mapping[str, Any]) -> dict[str, Any]:
    return as_mapping(view.get("provider_runtime"))


def futures_block(view: Mapping[str, Any]) -> dict[str, Any]:
    common = extract_common(view)
    return as_mapping(common.get("futures")) or as_mapping(common.get("futures_features"))


def selected_option(view: Mapping[str, Any], branch_id: str) -> dict[str, Any]:
    common = extract_common(view)
    selected = as_mapping(common.get("selected_option"))
    branch_side = side_for_branch(branch_id)

    if safe_str(selected.get("side")).upper() == branch_side:
        return selected

    if branch_id == BRANCH_CALL:
        return as_mapping(common.get("call")) or as_mapping(common.get("selected_call"))
    return as_mapping(common.get("put")) or as_mapping(common.get("selected_put"))


def miso_mode(view: Mapping[str, Any]) -> str:
    return SF_COMMON.resolve_miso_runtime_mode(
        extract_common(view),
        extract_provider_runtime(view),
        extract_family_status(view),
    )

def selected_side_from_view(view: Mapping[str, Any], surface: Mapping[str, Any]) -> str | None:
    status = extract_family_status(view)
    text = (
        safe_str(surface.get("selected_side"))
        or safe_str(status.get("selected_side"))
        or safe_str(nested(view, "market", "active_branch_hint", default=""))
        or safe_str(nested(view, "common", "selected_option", "side", default=""))
    )
    return normalize_branch(text)


def selected_strike_from_view(view: Mapping[str, Any], surface: Mapping[str, Any], frame: Mapping[str, Any]) -> float | None:
    status = extract_family_status(view)
    value = (
        surface.get("selected_strike")
        if surface.get("selected_strike") not in (None, "")
        else status.get("selected_strike")
        if status.get("selected_strike") not in (None, "")
        else frame.get("strike")
    )
    return safe_float(value, 0.0) if value not in (None, "") else None


def chain_context_ready(view: Mapping[str, Any], surface: Mapping[str, Any]) -> bool:
    status = extract_family_status(view)
    if "chain_context_ready" in surface:
        return safe_bool(surface.get("chain_context_ready"), False)
    if "chain_context_ready" in status:
        return safe_bool(status.get("chain_context_ready"), False)
    return safe_bool(nested(view, "stage_flags", "dhan_context_fresh", default=False), False)


def provider_is_dhan(provider_id: Any) -> bool:
    return safe_str(provider_id).upper() == PROVIDER_DHAN.upper()


# =============================================================================
# MISO gates and scoring
# =============================================================================


def global_gates_pass(view: Mapping[str, Any]) -> tuple[bool, str | None]:
    if not safe_bool(view.get("safe_to_consume"), True):
        return False, "view_not_safe_to_consume"

    required_true = SF_COMMON.GLOBAL_REQUIRED_STAGE_FLAGS + SF_COMMON.MISO_REQUIRED_STAGE_FLAGS
    ok, reason = SF_COMMON.validate_global_stage_gates(
        extract_stage_flags(view),
        required_true=required_true,
    )
    if not ok:
        return False, reason

    if miso_mode(view) == MODE_DISABLED:
        return False, "miso_runtime_disabled"

    return True, None


def provider_status_is_healthy(value: Any) -> bool:
    text = safe_str(value).upper()
    return text in {PROVIDER_STATUS_HEALTHY.upper(), PROVIDER_STATUS_OK}


def provider_is_allowed_miso_futures(provider_id: Any) -> bool:
    text = safe_str(provider_id).upper()
    return text in {PROVIDER_ZERODHA.upper(), PROVIDER_DHAN.upper()}


def _provider_pick(mapping: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in mapping and mapping[key] not in (None, ""):
            return mapping[key]
    return None


def _stage_flag_failed(stage: Mapping[str, Any], *keys: str) -> bool:
    for key in keys:
        if key in stage and not safe_bool(stage.get(key), False):
            return True
    return False


def provider_gate_pass(view: Mapping[str, Any]) -> tuple[bool, str | None]:
    provider_runtime = extract_provider_runtime(view)
    stage = extract_stage_flags(view)

    futures_provider = _provider_pick(
        provider_runtime,
        "futures_marketdata_provider_id",
        "active_futures_provider_id",
        "active_futures_marketdata_provider",
        "futures_provider_id",
    )
    selected_provider = _provider_pick(
        provider_runtime,
        "selected_option_marketdata_provider_id",
        "active_selected_option_provider_id",
        "active_selected_option_marketdata_provider",
        "selected_option_provider_id",
    )
    context_provider = _provider_pick(
        provider_runtime,
        "option_context_provider_id",
        "active_option_context_provider_id",
        "active_option_context_provider",
        "context_provider_id",
    )

    if not futures_provider:
        return False, "miso_futures_provider_missing"
    if not selected_provider:
        return False, "miso_selected_option_provider_missing"
    if not context_provider:
        return False, "miso_option_context_provider_missing"

    dhan_futures_rollout_enabled = (
        safe_bool(provider_runtime.get("miso_dhan_futures_rollout_enabled"), False)
        or safe_bool(stage.get("miso_dhan_futures_rollout_enabled"), False)
    )

    if dhan_futures_rollout_enabled and not provider_is_dhan(futures_provider):
        return False, "miso_dhan_futures_rollout_requires_dhan_futures_provider"

    if not dhan_futures_rollout_enabled and not provider_is_allowed_miso_futures(futures_provider):
        return False, "miso_requires_healthy_futures_provider_allowed_zerodha_or_dhan"

    if not provider_is_dhan(selected_provider):
        return False, "miso_requires_dhan_selected_option_provider"
    if not provider_is_dhan(context_provider):
        return False, "miso_requires_dhan_option_context_provider"

    futures_status = _provider_pick(
        provider_runtime,
        "futures_marketdata_status",
        "futures_provider_status",
        "active_futures_provider_status",
    )
    selected_status = _provider_pick(
        provider_runtime,
        "selected_option_marketdata_status",
        "selected_option_provider_status",
        "active_selected_option_provider_status",
    )
    context_status = _provider_pick(
        provider_runtime,
        "option_context_status",
        "option_context_provider_status",
        "active_option_context_provider_status",
    )

    if not provider_status_is_healthy(futures_status):
        return False, "miso_futures_provider_unhealthy_or_stale"
    if not provider_status_is_healthy(selected_status):
        return False, "miso_selected_option_provider_unhealthy_or_stale"
    if not provider_status_is_healthy(context_status):
        return False, "miso_option_context_provider_unhealthy_or_stale"

    if _stage_flag_failed(
        stage,
        "futures_marketdata_fresh",
        "futures_fresh",
        "active_futures_fresh",
    ):
        return False, "miso_futures_freshness_failed"

    if _stage_flag_failed(
        stage,
        "selected_option_marketdata_fresh",
        "selected_option_fresh",
        "dhan_selected_option_fresh",
    ):
        return False, "miso_selected_option_freshness_failed"

    if _stage_flag_failed(
        stage,
        "dhan_context_fresh",
        "option_context_fresh",
        "dhan_option_context_fresh",
    ):
        return False, "miso_option_context_freshness_failed"

    if _stage_flag_failed(
        stage,
        "cross_provider_sync_ok",
        "provider_sync_ok",
        "futures_option_sync_ok",
    ):
        return False, "miso_cross_provider_sync_failed"

    if _stage_flag_failed(
        provider_runtime,
        "cross_provider_sync_ok",
        "provider_sync_ok",
        "futures_option_sync_ok",
    ):
        return False, "miso_cross_provider_sync_failed"

    return True, None


def queue_reload_veto(surface: Mapping[str, Any]) -> bool:
    return bool_any(surface, ("queue_reload_blocked", "queue_reload_veto", "ask_reload_blocked", "bid_reload_blocked"))


def futures_veto_pass(view: Mapping[str, Any], branch_id: str, surface: Mapping[str, Any]) -> tuple[bool, str | None, float]:
    if safe_bool(surface.get("futures_contradiction_blocked"), False) or safe_bool(surface.get("futures_contradiction_veto"), False):
        return False, "futures_contradiction_veto", 0.0

    if safe_bool(surface.get("futures_vwap_align_ok"), False) or safe_bool(surface.get("futures_alignment_ok"), False):
        return True, None, 1.0

    fut = futures_block(view)
    delta_3 = float_any(fut, ("delta_3",), 0.0)
    ofi = float_any(fut, ("ofi_ratio_proxy", "nof", "nof_slope", "weighted_ofi_persist"), 0.0)
    above_vwap = safe_bool(fut.get("above_vwap"), False)
    below_vwap = safe_bool(fut.get("below_vwap"), False)

    if branch_id == BRANCH_CALL:
        score = 0.0
        score += 0.40 if delta_3 >= 0.0 else 0.0
        score += 0.30 if ofi >= -0.05 else 0.0
        score += 0.30 if above_vwap or delta_3 > 0.0 else 0.0
    else:
        score = 0.0
        score += 0.40 if delta_3 <= 0.0 else 0.0
        score += 0.30 if ofi <= 0.05 else 0.0
        score += 0.30 if below_vwap or delta_3 < 0.0 else 0.0

    score = clamp(score, 0.0, 1.0)
    if score < MIN_FUTURES_ALIGNMENT_SCORE:
        return False, "futures_alignment_insufficient", score
    return True, None, score


def burst_score(surface: Mapping[str, Any]) -> float:
    explicit = float_any(surface, ("burst_score", "option_burst_score"), -1.0)
    if explicit >= 0.0:
        return clamp(explicit, 0.0, 1.0)

    burst = bool_any(surface, ("burst_detected", "option_burst_detected", "burst_ok"))
    aggression = bool_any(surface, ("aggression_ok", "aggressive_flow", "aggressive_buy_flow", "aggressive_sell_flow"))
    tape_speed = bool_any(surface, ("tape_speed_ok", "speed_of_tape_ok", "tape_urgency_ok"))
    imbalance = bool_any(surface, ("imbalance_persist_ok", "imbalance_persistence_ok", "persistence_ok"))
    shadow = bool_any(surface, ("shadow_strike_support_ok", "shadow_support_ok"))
    tradability = bool_any(surface, ("tradability_pass", "option_tradability_pass", "tradability_ok"))

    score = 0.0
    if burst:
        score += 0.25
    if aggression:
        score += 0.22
    if tape_speed:
        score += 0.20
    if imbalance:
        score += 0.17
    if shadow:
        score += 0.06
    if tradability:
        score += 0.10
    return clamp(score, 0.0, 1.0)


def tape_score(surface: Mapping[str, Any]) -> float:
    explicit = float_any(surface, ("tape_score", "tape_speed_score", "speed_of_tape_score"), -1.0)
    if explicit >= 0.0:
        return clamp(explicit, 0.0, 1.0)

    tape_speed = bool_any(surface, ("tape_speed_ok", "speed_of_tape_ok", "tape_urgency_ok"))
    persistence = bool_any(surface, ("imbalance_persist_ok", "imbalance_persistence_ok", "persistence_ok"))
    burst = bool_any(surface, ("burst_detected", "option_burst_detected", "burst_ok"))
    large_counter_trade_absent = not safe_bool(surface.get("large_counter_trade_present"), False)

    score = 0.0
    if tape_speed:
        score += 0.36
    if persistence:
        score += 0.32
    if burst:
        score += 0.18
    if large_counter_trade_absent:
        score += 0.14
    return clamp(score, 0.0, 1.0)


def tradability_score(view: Mapping[str, Any], branch_id: str, surface: Mapping[str, Any], frame: Mapping[str, Any]) -> float:
    explicit = float_any(surface, ("tradability_score", "liquidity_score"), -1.0)
    if explicit >= 0.0:
        return clamp(explicit, 0.0, 1.0)

    opt = selected_option(view, branch_id)
    tradability = safe_bool(surface.get("tradability_pass"), safe_bool(opt.get("tradability_ok"), safe_bool(frame.get("tradability_ok"), False)))
    depth_ok = safe_bool(opt.get("depth_ok"), safe_bool(frame.get("tradability_ok"), False))
    response = float_any(opt, ("response_efficiency",), 0.0)
    delta = abs(float_any(opt, ("delta_3", "delta_proxy"), 0.0))

    return clamp(
        (0.32 if tradability else 0.0)
        + (0.24 if depth_ok else 0.0)
        + response * 1.25
        + min(delta, 3.0) / 3.0 * 0.18,
        0.0,
        1.0,
    )


def context_score(view: Mapping[str, Any], branch_id: str, surface: Mapping[str, Any]) -> tuple[float, bool, str | None]:
    explicit = float_any(surface, ("context_score", "oi_context_score"), -1.0)
    base = clamp(explicit, 0.0, 1.0) if explicit >= 0.0 else 0.64

    oi_wall = as_mapping(surface.get("oi_wall_context"))
    if not oi_wall:
        side_key = "call" if branch_id == BRANCH_CALL else "put"
        oi_wall = as_mapping(nested(view, "oi_wall_context", side_key, default={}))
    if not oi_wall:
        side_key = "call" if branch_id == BRANCH_CALL else "put"
        oi_wall = as_mapping(nested(view, "shared_core", "oi_wall_context", side_key, default={}))
    if not oi_wall:
        side_key = "call" if branch_id == BRANCH_CALL else "put"
        oi_wall = as_mapping(nested(view, "shared_core", "strike_selection", "oi_wall_context", side_key, default={}))

    distance = safe_float(oi_wall.get("distance_strikes"), 99.0)
    strength = safe_float(oi_wall.get("wall_strength"), 0.0)
    supportive = safe_bool(oi_wall.get("supportive"), False)

    if distance <= OI_WALL_EXTREME_DISTANCE_STRIKES and strength >= OI_WALL_EXTREME_STRENGTH_MIN and not supportive:
        return max(0.0, base - 0.45), False, "extreme_near_hostile_oi_wall"

    if supportive and distance <= 1.25 and strength >= 0.70:
        base = min(1.0, base + 0.06)

    return base, True, None


def min_score_for_mode_and_regime(mode: str, regime: str) -> float:
    regime = normalize_regime(regime)
    mode = normalize_mode(mode)

    if regime == REGIME_LOWVOL:
        return MIN_SCORE_LOWVOL
    if regime == REGIME_FAST:
        return MIN_SCORE_FAST
    if mode == MODE_DEPTH20_ENHANCED:
        return MIN_SCORE_DEPTH20
    return MIN_SCORE_BASE


def compute_score(
    *,
    view: Mapping[str, Any],
    branch_id: str,
    surface: Mapping[str, Any],
    frame: Mapping[str, Any],
) -> tuple[float, Mapping[str, Any]]:
    burst = burst_score(surface)
    tape = tape_score(surface)
    tradability = tradability_score(view, branch_id, surface, frame)
    futures_ok, futures_blocker, futures_score = futures_veto_pass(view, branch_id, surface)
    ctx, ctx_pass, ctx_blocker = context_score(view, branch_id, surface)
    mode = miso_mode(view)

    enhanced_bonus = 0.03 if mode == MODE_DEPTH20_ENHANCED else 0.0

    score = clamp(
        burst * 0.34
        + tape * 0.22
        + tradability * 0.20
        + futures_score * 0.14
        + ctx * 0.10
        + enhanced_bonus,
        0.0,
        1.0,
    )

    return score, {
        "burst_score": burst,
        "tape_score": tape,
        "tradability_score": tradability,
        "futures_alignment_score": futures_score,
        "futures_veto_pass": futures_ok,
        "futures_blocker": futures_blocker,
        "context_score": ctx,
        "context_pass": ctx_pass,
        "context_blocker": ctx_blocker,
        "mode": mode,
    }


# =============================================================================
# Branch evaluation
# =============================================================================


def evaluate_branch(view_like: Any, branch_id: str) -> MisoEvaluationResult:
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

    provider_ok, provider_reason = provider_gate_pass(view)
    if not provider_ok:
        return blocked_result(
            branch_id=branch_id,
            code=provider_reason or "miso_dhan_provider_required",
            message="MISO requires healthy synced futures plus Dhan selected-option and Dhan option-context providers.",
            metadata={"provider_runtime": extract_provider_runtime(view)},
        )

    status = extract_family_status(view)
    if status and not safe_bool(status.get("eligible"), True):
        return no_signal_result(
            branch_id=branch_id,
            reason="miso_family_not_eligible",
        )

    if not chain_context_ready(view, surface):
        return blocked_result(
            branch_id=branch_id,
            code="miso_chain_context_not_ready",
            message="MISO requires fresh Dhan chain context before entry.",
            metadata={"family_status": status},
        )

    if not frame:
        return no_signal_result(
            branch_id=branch_id,
            reason="branch_frame_missing",
        )

    selected_side = selected_side_from_view(view, surface)
    if selected_side is not None and selected_side != branch_id:
        return no_signal_result(
            branch_id=branch_id,
            reason="branch_not_selected_side",
            metadata={"selected_side": selected_side},
        )

    if queue_reload_veto(surface):
        return no_signal_result(
            branch_id=branch_id,
            reason="queue_reload_veto",
        )

    score, score_parts = compute_score(
        view=view,
        branch_id=branch_id,
        surface=surface,
        frame=frame,
    )

    if not score_parts["futures_veto_pass"]:
        return no_signal_result(
            branch_id=branch_id,
            reason=safe_str(score_parts["futures_blocker"], "futures_veto_failed"),
            metadata=score_parts,
        )

    if not score_parts["context_pass"]:
        return no_signal_result(
            branch_id=branch_id,
            reason=safe_str(score_parts["context_blocker"], "context_failed"),
            metadata=score_parts,
        )

    mode = safe_str(score_parts["mode"], MODE_BASE_5DEPTH)
    min_score = min_score_for_mode_and_regime(mode, regime)
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

    if score_parts["burst_score"] < MIN_BURST_SCORE:
        return no_signal_result(
            branch_id=branch_id,
            reason="burst_score_insufficient",
            metadata=score_parts,
        )

    if score_parts["tape_score"] < MIN_TAPE_SCORE:
        return no_signal_result(
            branch_id=branch_id,
            reason="tape_score_insufficient",
            metadata=score_parts,
        )

    if score_parts["tradability_score"] < MIN_TRADABILITY_SCORE:
        return no_signal_result(
            branch_id=branch_id,
            reason="tradability_score_insufficient",
            metadata=score_parts,
        )

    opt = selected_option(view, branch_id)
    instrument_key = safe_str(frame.get("instrument_key")) or safe_str(opt.get("instrument_key")) or None
    if not instrument_key:
        return no_signal_result(
            branch_id=branch_id,
            reason="instrument_key_missing",
        )

    burst_event_id = safe_str(surface.get("burst_event_id")) or safe_str(surface.get("source_event_id")) or None
    if not burst_event_id:
        return no_signal_result(
            branch_id=branch_id,
            reason="burst_event_id_missing",
            metadata={
                "surface_kind": safe_str(surface.get("surface_kind")),
                "microstructure": as_mapping(surface.get("microstructure")),
            },
        )

    tick_size = safe_float(
        opt.get("tick_size"),
        safe_float(frame.get("tick_size"), DEFAULT_TICK_SIZE),
    )
    if tick_size <= 0:
        tick_size = DEFAULT_TICK_SIZE

    candidate = MisoCandidate(
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
        mode=mode,
        burst_event_id=burst_event_id,
        selected_side=selected_side,
        selected_strike=selected_strike_from_view(view, surface, frame),
        shadow_call_strike=(
            safe_float(status.get("shadow_call_strike"))
            if status.get("shadow_call_strike") not in (None, "")
            else safe_float(surface.get("shadow_call_strike")) if surface.get("shadow_call_strike") not in (None, "") else None
        ),
        shadow_put_strike=(
            safe_float(status.get("shadow_put_strike"))
            if status.get("shadow_put_strike") not in (None, "")
            else safe_float(surface.get("shadow_put_strike")) if surface.get("shadow_put_strike") not in (None, "") else None
        ),
        metadata={
            "regime": regime,
            "score_parts": dict(score_parts),
            "surface_kind": safe_str(surface.get("surface_kind")),
            "setup_kind": "option_led_burst",
            "burst_event_id": burst_event_id,
            "microstructure": as_mapping(surface.get("microstructure")),
            "chain_context_ready": chain_context_ready(view, surface),
            "provider_runtime": extract_provider_runtime(view),
        },
    )
    return candidate_result(candidate)


def evaluate(view_like: Any, branch_id: str | None = None) -> MisoEvaluationResult:
    if branch_id is not None:
        return evaluate_branch(view_like, branch_id)

    for candidate_branch in SUPPORTED_BRANCHES:
        result = evaluate_branch(view_like, candidate_branch)
        if result.is_candidate or result.is_blocked:
            return result

    return no_signal_result(
        branch_id=None,
        reason="no_miso_branch_candidate",
    )


def evaluate_family(view_like: Any) -> MisoEvaluationResult:
    return evaluate(view_like)


def evaluate_doctrine(view_like: Any, branch_id: str | None = None) -> MisoEvaluationResult:
    return evaluate(view_like, branch_id=branch_id)


def get_evaluator():
    return evaluate


__all__ = [
    "FAMILY_ID",
    "DOCTRINE_ID",
    "MisoBlocker",
    "MisoCandidate",
    "MisoEvaluationResult",
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
        return SF_COMMON.normalize_miso_runtime_mode(value)

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

