from __future__ import annotations

"""
app/mme_scalpx/services/strategy_family/eligibility.py

Frozen strategy-family eligibility consumer for ScalpX MME.

Purpose
-------
This module OWNS:
- consumption of the frozen family_features payload published by services/features.py
- global pre-entry gate resolution from:
  - payload["stage_flags"]
  - payload["provider_runtime"]
  - payload["common"]
- doctrine/family eligibility reduction from:
  - payload["families"][...]
- deterministic blocked-reason generation
- typed eligibility outputs for downstream decision/arbitration layers

This module DOES NOT own:
- Redis reads or writes
- feature computation
- provider routing policy
- cooldown state mutation
- candidate ranking or cross-family arbitration
- entry/exit order decisions
- proof-window logic
- broker truth

Frozen design law
-----------------
- This module consumes only the frozen family_features seam.
- It must not reach back into old ad hoc feature internals.
- Classic families remain branch-shaped:
  MIST / MISB / MISC / MISR -> branches -> CALL / PUT
- MISO remains side-support-shaped:
  call_support / put_support
- Eligibility here is necessary-but-not-sufficient for a trade.
  Later decision logic may add stricter doctrine checks, but may not bypass
  these frozen gate surfaces.
"""

from dataclasses import dataclass
from typing import Any, Callable, Final, Mapping

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services.feature_family import contracts as FF_C


# ============================================================================
# Exceptions
# ============================================================================


class EligibilityError(ValueError):
    """Base error for eligibility evaluation failures."""


class EligibilityValidationError(EligibilityError):
    """Raised when family_features payload or request inputs are invalid."""


# ============================================================================
# Canonical vocabularies
# ============================================================================

FAMILY_IDS: Final[tuple[str, ...]] = tuple(FF_C.FAMILY_IDS)
CLASSIC_FAMILY_IDS: Final[tuple[str, ...]] = tuple(FF_C.CLASSIC_FAMILY_IDS)
BRANCH_IDS: Final[tuple[str, ...]] = tuple(FF_C.BRANCH_IDS)
OPTION_SIDE_IDS: Final[tuple[str, ...]] = (N.SIDE_CALL, N.SIDE_PUT)

CLASSIC_RUNTIME_MODES: Final[tuple[str, ...]] = (
    N.STRATEGY_RUNTIME_MODE_NORMAL,
    N.STRATEGY_RUNTIME_MODE_DHAN_DEGRADED,
    N.STRATEGY_RUNTIME_MODE_DISABLED,
)

MISO_RUNTIME_MODES: Final[tuple[str, ...]] = (
    N.STRATEGY_RUNTIME_MODE_BASE_5DEPTH,
    N.STRATEGY_RUNTIME_MODE_DEPTH20_ENHANCED,
    N.STRATEGY_RUNTIME_MODE_DISABLED,
)

ALLOWED_PROVIDER_STATUSES: Final[tuple[str, ...]] = tuple(N.ALLOWED_PROVIDER_STATUSES)
ALLOWED_FAMILY_RUNTIME_MODES: Final[tuple[str, ...]] = tuple(N.ALLOWED_FAMILY_RUNTIME_MODES)
ALLOWED_REGIMES: Final[tuple[str, ...]] = tuple(FF_C.ALLOWED_REGIMES)


# ============================================================================
# Reason codes
# ============================================================================

REASON_PAYLOAD_INVALID: Final[str] = "PAYLOAD_INVALID"
REASON_FAMILY_UNSUPPORTED: Final[str] = "FAMILY_UNSUPPORTED"
REASON_BRANCH_UNSUPPORTED: Final[str] = "BRANCH_UNSUPPORTED"
REASON_DATA_INVALID: Final[str] = "DATA_INVALID"
REASON_DATA_QUALITY_FAIL: Final[str] = "DATA_QUALITY_FAIL"
REASON_SESSION_INELIGIBLE: Final[str] = "SESSION_INELIGIBLE"
REASON_WARMUP_INCOMPLETE: Final[str] = "WARMUP_INCOMPLETE"
REASON_RISK_VETO_ACTIVE: Final[str] = "RISK_VETO_ACTIVE"
REASON_RECONCILIATION_LOCK_ACTIVE: Final[str] = "RECONCILIATION_LOCK_ACTIVE"
REASON_ACTIVE_POSITION_PRESENT: Final[str] = "ACTIVE_POSITION_PRESENT"
REASON_PROVIDER_NOT_READY_CLASSIC: Final[str] = "PROVIDER_NOT_READY_CLASSIC"
REASON_PROVIDER_NOT_READY_MISO: Final[str] = "PROVIDER_NOT_READY_MISO"
REASON_DHAN_CONTEXT_NOT_FRESH: Final[str] = "DHAN_CONTEXT_NOT_FRESH"
REASON_FUTURES_NOT_PRESENT: Final[str] = "FUTURES_NOT_PRESENT"
REASON_CALL_NOT_PRESENT: Final[str] = "CALL_NOT_PRESENT"
REASON_PUT_NOT_PRESENT: Final[str] = "PUT_NOT_PRESENT"
REASON_SELECTED_OPTION_NOT_PRESENT: Final[str] = "SELECTED_OPTION_NOT_PRESENT"
REASON_CONTEXT_PASS_FAIL: Final[str] = "CONTEXT_PASS_FAIL"
REASON_OPTION_TRADABILITY_FAIL: Final[str] = "OPTION_TRADABILITY_FAIL"
REASON_RUNTIME_MODE_DISABLED: Final[str] = "RUNTIME_MODE_DISABLED"
REASON_REGIME_UNKNOWN: Final[str] = "REGIME_UNKNOWN"
REASON_BRANCH_SURFACE_MISSING: Final[str] = "BRANCH_SURFACE_MISSING"
REASON_FAMILY_NOT_ELIGIBLE: Final[str] = "FAMILY_NOT_ELIGIBLE"
REASON_STRUCTURAL_FAIL: Final[str] = "STRUCTURAL_FAIL"
REASON_SELECTED_SIDE_MISMATCH: Final[str] = "SELECTED_SIDE_MISMATCH"
REASON_CHAIN_CONTEXT_NOT_READY: Final[str] = "CHAIN_CONTEXT_NOT_READY"
REASON_QUEUE_RELOAD_BLOCKED: Final[str] = "QUEUE_RELOAD_BLOCKED"
REASON_FUTURES_CONTRADICTION_BLOCKED: Final[str] = "FUTURES_CONTRADICTION_BLOCKED"

# Classic family structural reason labels
REASON_MIST_FUTURES_BIAS_FAIL: Final[str] = "MIST_FUTURES_BIAS_FAIL"
REASON_MIST_FUTURES_IMPULSE_FAIL: Final[str] = "MIST_FUTURES_IMPULSE_FAIL"
REASON_MIST_PULLBACK_FAIL: Final[str] = "MIST_PULLBACK_FAIL"
REASON_MIST_RESUME_FAIL: Final[str] = "MIST_RESUME_FAIL"
REASON_MIST_MICRO_TRAP_BLOCKED: Final[str] = "MIST_MICRO_TRAP_BLOCKED"

REASON_MISB_FUTURES_BIAS_FAIL: Final[str] = "MISB_FUTURES_BIAS_FAIL"
REASON_MISB_SHELF_INVALID: Final[str] = "MISB_SHELF_INVALID"
REASON_MISB_BREAKOUT_NOT_TRIGGERED: Final[str] = "MISB_BREAKOUT_NOT_TRIGGERED"
REASON_MISB_BREAKOUT_NOT_ACCEPTED: Final[str] = "MISB_BREAKOUT_NOT_ACCEPTED"

REASON_MISC_COMPRESSION_FAIL: Final[str] = "MISC_COMPRESSION_FAIL"
REASON_MISC_BREAKOUT_NOT_TRIGGERED: Final[str] = "MISC_BREAKOUT_NOT_TRIGGERED"
REASON_MISC_EXPANSION_NOT_ACCEPTED: Final[str] = "MISC_EXPANSION_NOT_ACCEPTED"
REASON_MISC_RETEST_MONITOR_INACTIVE: Final[str] = "MISC_RETEST_MONITOR_INACTIVE"
REASON_MISC_RESUME_NOT_CONFIRMED: Final[str] = "MISC_RESUME_NOT_CONFIRMED"

REASON_MISR_FAKE_BREAK_NOT_TRIGGERED: Final[str] = "MISR_FAKE_BREAK_NOT_TRIGGERED"
REASON_MISR_ABSORPTION_FAIL: Final[str] = "MISR_ABSORPTION_FAIL"
REASON_MISR_RANGE_REENTRY_FAIL: Final[str] = "MISR_RANGE_REENTRY_FAIL"
REASON_MISR_FLOW_FLIP_FAIL: Final[str] = "MISR_FLOW_FLIP_FAIL"
REASON_MISR_HOLD_PROOF_FAIL: Final[str] = "MISR_HOLD_PROOF_FAIL"
REASON_MISR_NO_MANS_LAND_FAIL: Final[str] = "MISR_NO_MANS_LAND_FAIL"
REASON_MISR_REVERSAL_IMPULSE_FAIL: Final[str] = "MISR_REVERSAL_IMPULSE_FAIL"

REASON_MISR_ACTIVE_ZONE_INVALID: Final[str] = "MISR_ACTIVE_ZONE_INVALID"

# MISO structural reason labels
REASON_MISO_BURST_NOT_DETECTED: Final[str] = "MISO_BURST_NOT_DETECTED"
REASON_MISO_AGGRESSION_FAIL: Final[str] = "MISO_AGGRESSION_FAIL"
REASON_MISO_TAPE_SPEED_FAIL: Final[str] = "MISO_TAPE_SPEED_FAIL"
REASON_MISO_IMBALANCE_PERSIST_FAIL: Final[str] = "MISO_IMBALANCE_PERSIST_FAIL"
REASON_MISO_TRADABILITY_FAIL: Final[str] = "MISO_TRADABILITY_FAIL"
REASON_MISO_FUTURES_VWAP_ALIGN_FAIL: Final[str] = "MISO_FUTURES_VWAP_ALIGN_FAIL"


# ============================================================================
# Typed outputs
# ============================================================================


@dataclass(frozen=True, slots=True)
class GlobalGateResult:
    """Global frozen pre-entry gates derived from stage_flags/common/provider_runtime."""

    eligible: bool
    blocked_reasons: tuple[str, ...]
    regime: str | None
    family_runtime_mode: str | None
    classic_runtime_mode: str | None
    miso_runtime_mode: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "eligible": self.eligible,
            "blocked_reasons": list(self.blocked_reasons),
            "regime": self.regime,
            "family_runtime_mode": self.family_runtime_mode,
            "classic_runtime_mode": self.classic_runtime_mode,
            "miso_runtime_mode": self.miso_runtime_mode,
        }


@dataclass(frozen=True, slots=True)
class BranchEligibilityResult:
    """Eligibility result for one family/branch consumer."""

    family_id: str
    branch_id: str
    eligible: bool
    global_gate_pass: bool
    family_gate_pass: bool
    context_pass: bool
    option_tradability_pass: bool
    structural_pass: bool
    blocked_reasons: tuple[str, ...]
    regime: str | None
    strategy_runtime_mode: str | None
    family_runtime_mode: str | None
    support: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "family_id": self.family_id,
            "branch_id": self.branch_id,
            "eligible": self.eligible,
            "global_gate_pass": self.global_gate_pass,
            "family_gate_pass": self.family_gate_pass,
            "context_pass": self.context_pass,
            "option_tradability_pass": self.option_tradability_pass,
            "structural_pass": self.structural_pass,
            "blocked_reasons": list(self.blocked_reasons),
            "regime": self.regime,
            "strategy_runtime_mode": self.strategy_runtime_mode,
            "family_runtime_mode": self.family_runtime_mode,
            "support": dict(self.support),
        }


# ============================================================================
# Internal helpers
# ============================================================================


def _fail(message: str) -> None:
    raise EligibilityValidationError(message)


def _require(condition: bool, message: str) -> None:
    if not condition:
        _fail(message)


def _require_mapping(value: Any, *, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        _fail(f"{field_name} must be a mapping")
    return value


def _require_literal(value: str, *, field_name: str, allowed: tuple[str, ...]) -> str:
    if not isinstance(value, str):
        _fail(f"{field_name} must be str")
    normalized = value.strip()
    if not normalized:
        _fail(f"{field_name} must be non-empty str")
    if normalized not in allowed:
        _fail(f"{field_name} must be one of {allowed!r}, got {normalized!r}")
    return normalized


def _optional_literal(
    value: Any,
    *,
    field_name: str,
    allowed: tuple[str, ...],
) -> str | None:
    if value is None:
        return None
    return _require_literal(value, field_name=field_name, allowed=allowed)


def _bool(value: Any) -> bool:
    return bool(value)


def _tuple_unique(values: list[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return tuple(out)


def _normalize_family_features_payload(raw: Mapping[str, Any]) -> Mapping[str, Any]:
    """
    Accept either:
    - a direct family_features payload
    - a wrapper mapping containing key 'family_features'
    """
    candidate: Any = raw
    if "family_features" in raw and isinstance(raw.get("family_features"), Mapping):
        candidate = raw["family_features"]
    payload = _require_mapping(candidate, field_name="family_features_payload")
    FF_C.validate_family_features_payload(payload)
    return payload


def _read_global_blocks(
    payload: Mapping[str, Any],
) -> tuple[Mapping[str, Any], Mapping[str, Any], Mapping[str, Any], Mapping[str, Any]]:
    provider_runtime = _require_mapping(
        payload.get("provider_runtime"),
        field_name="payload.provider_runtime",
    )
    common = _require_mapping(payload.get("common"), field_name="payload.common")
    stage_flags = _require_mapping(
        payload.get("stage_flags"),
        field_name="payload.stage_flags",
    )
    families = _require_mapping(payload.get("families"), field_name="payload.families")
    return provider_runtime, common, stage_flags, families


# ============================================================================
# Frozen global gate evaluation
# ============================================================================


def evaluate_global_gates(payload: Mapping[str, Any]) -> GlobalGateResult:
    """Evaluate global frozen pre-entry gates from the family_features payload."""
    family_features = _normalize_family_features_payload(payload)
    provider_runtime, common, stage_flags, _ = _read_global_blocks(family_features)

    reasons: list[str] = []

    if not _bool(stage_flags.get("data_valid")):
        reasons.append(REASON_DATA_INVALID)
    if not _bool(stage_flags.get("data_quality_ok")):
        reasons.append(REASON_DATA_QUALITY_FAIL)
    if not _bool(stage_flags.get("session_eligible")):
        reasons.append(REASON_SESSION_INELIGIBLE)
    if not _bool(stage_flags.get("warmup_complete")):
        reasons.append(REASON_WARMUP_INCOMPLETE)
    if _bool(stage_flags.get("risk_veto_active")):
        reasons.append(REASON_RISK_VETO_ACTIVE)
    if _bool(stage_flags.get("reconciliation_lock_active")):
        reasons.append(REASON_RECONCILIATION_LOCK_ACTIVE)
    if _bool(stage_flags.get("active_position_present")):
        reasons.append(REASON_ACTIVE_POSITION_PRESENT)

    regime = _optional_literal(
        common.get("regime"),
        field_name="common.regime",
        allowed=ALLOWED_REGIMES,
    )

    family_runtime_mode = _optional_literal(
        provider_runtime.get("family_runtime_mode"),
        field_name="provider_runtime.family_runtime_mode",
        allowed=ALLOWED_FAMILY_RUNTIME_MODES,
    )
    classic_runtime_mode = _optional_literal(
        common.get("strategy_runtime_mode_classic"),
        field_name="common.strategy_runtime_mode_classic",
        allowed=CLASSIC_RUNTIME_MODES,
    )
    miso_runtime_mode = _optional_literal(
        common.get("strategy_runtime_mode_miso"),
        field_name="common.strategy_runtime_mode_miso",
        allowed=MISO_RUNTIME_MODES,
    )

    if regime is None:
        reasons.append(REASON_REGIME_UNKNOWN)

    return GlobalGateResult(
        eligible=len(reasons) == 0,
        blocked_reasons=_tuple_unique(reasons),
        regime=regime,
        family_runtime_mode=family_runtime_mode,
        classic_runtime_mode=classic_runtime_mode,
        miso_runtime_mode=miso_runtime_mode,
    )


# ============================================================================
# Classic family branch evaluation
# ============================================================================


def _classic_global_reasons(
    *,
    stage_flags: Mapping[str, Any],
    branch_id: str,
) -> list[str]:
    reasons: list[str] = []
    if not _bool(stage_flags.get("data_valid")):
        reasons.append(REASON_DATA_INVALID)
    if not _bool(stage_flags.get("data_quality_ok")):
        reasons.append(REASON_DATA_QUALITY_FAIL)
    if not _bool(stage_flags.get("session_eligible")):
        reasons.append(REASON_SESSION_INELIGIBLE)
    if not _bool(stage_flags.get("warmup_complete")):
        reasons.append(REASON_WARMUP_INCOMPLETE)
    if _bool(stage_flags.get("risk_veto_active")):
        reasons.append(REASON_RISK_VETO_ACTIVE)
    if _bool(stage_flags.get("reconciliation_lock_active")):
        reasons.append(REASON_RECONCILIATION_LOCK_ACTIVE)
    if _bool(stage_flags.get("active_position_present")):
        reasons.append(REASON_ACTIVE_POSITION_PRESENT)
    if not _bool(stage_flags.get("provider_ready_classic")):
        reasons.append(REASON_PROVIDER_NOT_READY_CLASSIC)
    if not _bool(stage_flags.get("futures_present")):
        reasons.append(REASON_FUTURES_NOT_PRESENT)
    if branch_id == N.BRANCH_CALL and not _bool(stage_flags.get("call_present")):
        reasons.append(REASON_CALL_NOT_PRESENT)
    if branch_id == N.BRANCH_PUT and not _bool(stage_flags.get("put_present")):
        reasons.append(REASON_PUT_NOT_PRESENT)
    return reasons


def _classic_branch_support(
    payload: Mapping[str, Any],
    *,
    family_id: str,
    branch_id: str,
) -> tuple[Mapping[str, Any], Mapping[str, Any], Mapping[str, Any], Mapping[str, Any]]:
    family_features = _normalize_family_features_payload(payload)
    provider_runtime, common, stage_flags, families = _read_global_blocks(family_features)

    family_surface = _require_mapping(
        families.get(family_id),
        field_name=f'payload.families["{family_id}"]',
    )
    branches = _require_mapping(
        family_surface.get("branches"),
        field_name=f'payload.families["{family_id}"].branches',
    )
    support = _require_mapping(
        branches.get(branch_id),
        field_name=f'payload.families["{family_id}"].branches["{branch_id}"]',
    )
    return provider_runtime, common, stage_flags, support


def _mist_structural_reasons(support: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []
    if not _bool(support.get("trend_confirmed")):
        reasons.append(REASON_MIST_FUTURES_BIAS_FAIL)
    if not _bool(support.get("futures_impulse_ok")):
        reasons.append(REASON_MIST_FUTURES_IMPULSE_FAIL)
    if not _bool(support.get("pullback_detected")):
        reasons.append(REASON_MIST_PULLBACK_FAIL)
    if not mist_micro_trap_resolved(support):
        reasons.append(REASON_MIST_MICRO_TRAP_BLOCKED)
    if not _bool(support.get("resume_confirmed")):
        reasons.append(REASON_MIST_RESUME_FAIL)
    return reasons


def _misb_structural_reasons(support: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []
    if not _bool(support.get("shelf_confirmed")):
        reasons.append(REASON_MISB_SHELF_INVALID)
    if not _bool(support.get("breakout_triggered")):
        reasons.append(REASON_MISB_BREAKOUT_NOT_TRIGGERED)
    if not _bool(support.get("breakout_accepted")):
        reasons.append(REASON_MISB_BREAKOUT_NOT_ACCEPTED)
    return reasons


def _misc_structural_reasons(support: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []
    if not _bool(support.get("compression_detected")):
        reasons.append(REASON_MISC_COMPRESSION_FAIL)
    if not _bool(support.get("directional_breakout_triggered")):
        reasons.append(REASON_MISC_BREAKOUT_NOT_TRIGGERED)
    if not _bool(support.get("expansion_accepted")):
        reasons.append(REASON_MISC_EXPANSION_NOT_ACCEPTED)
    if not _bool(support.get("retest_monitor_active")):
        reasons.append(REASON_MISC_RETEST_MONITOR_INACTIVE)
    if not _bool(support.get("resume_confirmed")):
        reasons.append(REASON_MISC_RESUME_NOT_CONFIRMED)
    return reasons


def _misr_structural_reasons(support: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []
    if not _bool(support.get("active_zone_valid")):
        reasons.append(REASON_MISR_ACTIVE_ZONE_INVALID)
    if not _bool(support.get("fake_break_triggered")):
        reasons.append(REASON_MISR_FAKE_BREAK_NOT_TRIGGERED)
    if not _bool(support.get("absorption_pass")):
        reasons.append(REASON_MISR_ABSORPTION_FAIL)
    if not _bool(support.get("range_reentry_confirmed")):
        reasons.append(REASON_MISR_RANGE_REENTRY_FAIL)
    if not _bool(support.get("flow_flip_confirmed")):
        reasons.append(REASON_MISR_FLOW_FLIP_FAIL)
    if not _bool(support.get("hold_inside_range_proved")):
        reasons.append(REASON_MISR_HOLD_PROOF_FAIL)
    if not _bool(support.get("no_mans_land_cleared")):
        reasons.append(REASON_MISR_NO_MANS_LAND_FAIL)
    if not _bool(support.get("reversal_impulse_confirmed")):
        reasons.append(REASON_MISR_REVERSAL_IMPULSE_FAIL)
    return reasons


CLASSIC_STRUCTURAL_REASON_BUILDERS: Final[Mapping[str, Callable[[Mapping[str, Any]], list[str]]]] = {
    N.STRATEGY_FAMILY_MIST: _mist_structural_reasons,
    N.STRATEGY_FAMILY_MISB: _misb_structural_reasons,
    N.STRATEGY_FAMILY_MISC: _misc_structural_reasons,
    N.STRATEGY_FAMILY_MISR: _misr_structural_reasons,
}


def evaluate_classic_branch_eligibility(
    payload: Mapping[str, Any],
    *,
    family_id: str,
    branch_id: str,
) -> BranchEligibilityResult:
    """Evaluate one classic family branch (CALL or PUT)."""
    _require_literal(family_id, field_name="family_id", allowed=CLASSIC_FAMILY_IDS)
    _require_literal(branch_id, field_name="branch_id", allowed=BRANCH_IDS)

    provider_runtime, common, stage_flags, support = _classic_branch_support(
        payload,
        family_id=family_id,
        branch_id=branch_id,
    )

    reasons: list[str] = []
    reasons.extend(_classic_global_reasons(stage_flags=stage_flags, branch_id=branch_id))

    family_features = _normalize_family_features_payload(payload)
    families = _require_mapping(family_features.get("families"), field_name="payload.families")
    family_surface = _require_mapping(
        families.get(family_id),
        field_name=f'payload.families["{family_id}"]',
    )

    if not _bool(family_surface.get("eligible")):
        reasons.append(REASON_FAMILY_NOT_ELIGIBLE)

    runtime_mode = _optional_literal(
        common.get("strategy_runtime_mode_classic"),
        field_name="common.strategy_runtime_mode_classic",
        allowed=CLASSIC_RUNTIME_MODES,
    )
    if runtime_mode == N.STRATEGY_RUNTIME_MODE_DISABLED:
        reasons.append(REASON_RUNTIME_MODE_DISABLED)

    context_pass = _bool(support.get("context_pass"))
    option_tradability_pass = _bool(support.get("option_tradability_pass"))

    if not context_pass:
        reasons.append(REASON_CONTEXT_PASS_FAIL)
    if not option_tradability_pass:
        reasons.append(REASON_OPTION_TRADABILITY_FAIL)

    structural_reasons = CLASSIC_STRUCTURAL_REASON_BUILDERS[family_id](support)
    reasons.extend(structural_reasons)

    structural_pass = len(structural_reasons) == 0
    global_gate_pass = len(_classic_global_reasons(stage_flags=stage_flags, branch_id=branch_id)) == 0
    family_gate_pass = _bool(family_surface.get("eligible"))

    return BranchEligibilityResult(
        family_id=family_id,
        branch_id=branch_id,
        eligible=len(reasons) == 0,
        global_gate_pass=global_gate_pass,
        family_gate_pass=family_gate_pass,
        context_pass=context_pass,
        option_tradability_pass=option_tradability_pass,
        structural_pass=structural_pass,
        blocked_reasons=_tuple_unique(reasons),
        regime=_optional_literal(
            common.get("regime"),
            field_name="common.regime",
            allowed=ALLOWED_REGIMES,
        ),
        strategy_runtime_mode=runtime_mode,
        family_runtime_mode=_optional_literal(
            provider_runtime.get("family_runtime_mode"),
            field_name="provider_runtime.family_runtime_mode",
            allowed=ALLOWED_FAMILY_RUNTIME_MODES,
        ),
        support=support,
    )


# ============================================================================
# MISO evaluation
# ============================================================================


def _miso_global_reasons(
    *,
    stage_flags: Mapping[str, Any],
    side: str,
) -> list[str]:
    reasons: list[str] = []
    if not _bool(stage_flags.get("data_valid")):
        reasons.append(REASON_DATA_INVALID)
    if not _bool(stage_flags.get("data_quality_ok")):
        reasons.append(REASON_DATA_QUALITY_FAIL)
    if not _bool(stage_flags.get("session_eligible")):
        reasons.append(REASON_SESSION_INELIGIBLE)
    if not _bool(stage_flags.get("warmup_complete")):
        reasons.append(REASON_WARMUP_INCOMPLETE)
    if _bool(stage_flags.get("risk_veto_active")):
        reasons.append(REASON_RISK_VETO_ACTIVE)
    if _bool(stage_flags.get("reconciliation_lock_active")):
        reasons.append(REASON_RECONCILIATION_LOCK_ACTIVE)
    if _bool(stage_flags.get("active_position_present")):
        reasons.append(REASON_ACTIVE_POSITION_PRESENT)
    if not _bool(stage_flags.get("provider_ready_miso")):
        reasons.append(REASON_PROVIDER_NOT_READY_MISO)
    if not _bool(stage_flags.get("dhan_context_fresh")):
        reasons.append(REASON_DHAN_CONTEXT_NOT_FRESH)
    if not _bool(stage_flags.get("futures_present")):
        reasons.append(REASON_FUTURES_NOT_PRESENT)
    if not _bool(stage_flags.get("selected_option_present")):
        reasons.append(REASON_SELECTED_OPTION_NOT_PRESENT)
    if side == N.SIDE_CALL and not _bool(stage_flags.get("call_present")):
        reasons.append(REASON_CALL_NOT_PRESENT)
    if side == N.SIDE_PUT and not _bool(stage_flags.get("put_present")):
        reasons.append(REASON_PUT_NOT_PRESENT)
    return reasons


def _miso_support(
    payload: Mapping[str, Any],
    *,
    side: str,
) -> tuple[Mapping[str, Any], Mapping[str, Any], Mapping[str, Any], Mapping[str, Any], Mapping[str, Any]]:
    family_features = _normalize_family_features_payload(payload)
    provider_runtime, common, stage_flags, families = _read_global_blocks(family_features)
    miso = _require_mapping(
        families.get(N.STRATEGY_FAMILY_MISO),
        field_name='payload.families["MISO"]',
    )
    support_key = "call_support" if side == N.SIDE_CALL else "put_support"
    support = _require_mapping(
        miso.get(support_key),
        field_name=f'payload.families["MISO"].{support_key}',
    )
    return provider_runtime, common, stage_flags, miso, support


def _miso_structural_reasons(support: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []
    if not _bool(support.get("burst_detected")):
        reasons.append(REASON_MISO_BURST_NOT_DETECTED)
    if not _bool(support.get("aggression_ok")):
        reasons.append(REASON_MISO_AGGRESSION_FAIL)
    if not _bool(support.get("tape_speed_ok")):
        reasons.append(REASON_MISO_TAPE_SPEED_FAIL)
    if not _bool(support.get("imbalance_persist_ok")):
        reasons.append(REASON_MISO_IMBALANCE_PERSIST_FAIL)
    if _bool(support.get("queue_reload_blocked")):
        reasons.append(REASON_QUEUE_RELOAD_BLOCKED)
    if not _bool(support.get("futures_vwap_align_ok")):
        reasons.append(REASON_MISO_FUTURES_VWAP_ALIGN_FAIL)
    if _bool(support.get("futures_contradiction_blocked")):
        reasons.append(REASON_FUTURES_CONTRADICTION_BLOCKED)
    if not _bool(support.get("tradability_pass")):
        reasons.append(REASON_MISO_TRADABILITY_FAIL)
    return reasons


def evaluate_miso_side_eligibility(
    payload: Mapping[str, Any],
    *,
    side: str,
) -> BranchEligibilityResult:
    """Evaluate MISO eligibility for CALL or PUT side."""
    _require_literal(side, field_name="side", allowed=OPTION_SIDE_IDS)

    provider_runtime, common, stage_flags, miso, support = _miso_support(payload, side=side)

    reasons: list[str] = []
    reasons.extend(_miso_global_reasons(stage_flags=stage_flags, side=side))

    if not _bool(miso.get("eligible")):
        reasons.append(REASON_FAMILY_NOT_ELIGIBLE)
    if not _bool(miso.get("chain_context_ready")):
        reasons.append(REASON_CHAIN_CONTEXT_NOT_READY)

    runtime_mode = _optional_literal(
        miso.get("mode"),
        field_name='payload.families["MISO"].mode',
        allowed=MISO_RUNTIME_MODES,
    )
    if runtime_mode == N.STRATEGY_RUNTIME_MODE_DISABLED:
        reasons.append(REASON_RUNTIME_MODE_DISABLED)

    selected_side = _optional_literal(
        miso.get("selected_side"),
        field_name='payload.families["MISO"].selected_side',
        allowed=OPTION_SIDE_IDS,
    )
    if selected_side is not None and selected_side != side:
        reasons.append(REASON_SELECTED_SIDE_MISMATCH)

    structural_reasons = _miso_structural_reasons(support)
    reasons.extend(structural_reasons)

    structural_pass = len(structural_reasons) == 0
    global_gate_pass = len(_miso_global_reasons(stage_flags=stage_flags, side=side)) == 0
    family_gate_pass = _bool(miso.get("eligible")) and _bool(miso.get("chain_context_ready"))

    return BranchEligibilityResult(
        family_id=N.STRATEGY_FAMILY_MISO,
        branch_id=N.BRANCH_CALL if side == N.SIDE_CALL else N.BRANCH_PUT,
        eligible=len(reasons) == 0,
        global_gate_pass=global_gate_pass,
        family_gate_pass=family_gate_pass,
        context_pass=_bool(miso.get("chain_context_ready")),
        option_tradability_pass=_bool(support.get("tradability_pass")),
        structural_pass=structural_pass,
        blocked_reasons=_tuple_unique(reasons),
        regime=_optional_literal(
            common.get("regime"),
            field_name="common.regime",
            allowed=ALLOWED_REGIMES,
        ),
        strategy_runtime_mode=runtime_mode,
        family_runtime_mode=_optional_literal(
            provider_runtime.get("family_runtime_mode"),
            field_name="provider_runtime.family_runtime_mode",
            allowed=ALLOWED_FAMILY_RUNTIME_MODES,
        ),
        support=support,
    )


# ============================================================================
# Public façade helpers
# ============================================================================


def evaluate_branch_eligibility(
    payload: Mapping[str, Any],
    *,
    family_id: str,
    branch_id: str,
) -> BranchEligibilityResult:
    """
    Public unified branch evaluation helper.

    For classic families:
    - family_id must be one of MIST/MISB/MISC/MISR
    - branch_id must be CALL/PUT

    For MISO:
    - family_id must be MISO
    - branch_id still uses CALL/PUT
    """
    family = _require_literal(family_id, field_name="family_id", allowed=FAMILY_IDS)
    branch = _require_literal(branch_id, field_name="branch_id", allowed=BRANCH_IDS)

    if family in CLASSIC_FAMILY_IDS:
        return evaluate_classic_branch_eligibility(
            payload,
            family_id=family,
            branch_id=branch,
        )

    if family == N.STRATEGY_FAMILY_MISO:
        return evaluate_miso_side_eligibility(
            payload,
            side=N.SIDE_CALL if branch == N.BRANCH_CALL else N.SIDE_PUT,
        )

    _fail(f"unsupported family_id: {family!r}")


def pre_entry_gate(
    payload: Mapping[str, Any],
    *,
    family_id: str,
    branch_id: str,
) -> BranchEligibilityResult:
    """
    Frozen top-level entry gate façade for downstream decisions/arbitration.

    This function is intentionally thin so later files can call a stable
    high-level gate without bypassing the frozen family_features seam.
    """
    return evaluate_branch_eligibility(
        payload,
        family_id=family_id,
        branch_id=branch_id,
    )


__all__ = [
    "EligibilityError",
    "EligibilityValidationError",
    "GlobalGateResult",
    "BranchEligibilityResult",
    "evaluate_global_gates",
    "evaluate_classic_branch_eligibility",
    "evaluate_miso_side_eligibility",
    "evaluate_branch_eligibility",
    "pre_entry_gate",
    "FAMILY_IDS",
    "CLASSIC_FAMILY_IDS",
    "BRANCH_IDS",
    "OPTION_SIDE_IDS",
    "REASON_PAYLOAD_INVALID",
    "REASON_FAMILY_UNSUPPORTED",
    "REASON_BRANCH_UNSUPPORTED",
    "REASON_DATA_INVALID",
    "REASON_DATA_QUALITY_FAIL",
    "REASON_SESSION_INELIGIBLE",
    "REASON_WARMUP_INCOMPLETE",
    "REASON_RISK_VETO_ACTIVE",
    "REASON_RECONCILIATION_LOCK_ACTIVE",
    "REASON_ACTIVE_POSITION_PRESENT",
    "REASON_PROVIDER_NOT_READY_CLASSIC",
    "REASON_PROVIDER_NOT_READY_MISO",
    "REASON_DHAN_CONTEXT_NOT_FRESH",
    "REASON_FUTURES_NOT_PRESENT",
    "REASON_CALL_NOT_PRESENT",
    "REASON_PUT_NOT_PRESENT",
    "REASON_SELECTED_OPTION_NOT_PRESENT",
    "REASON_CONTEXT_PASS_FAIL",
    "REASON_OPTION_TRADABILITY_FAIL",
    "REASON_RUNTIME_MODE_DISABLED",
    "REASON_REGIME_UNKNOWN",
    "REASON_BRANCH_SURFACE_MISSING",
    "REASON_FAMILY_NOT_ELIGIBLE",
    "REASON_STRUCTURAL_FAIL",
    "REASON_SELECTED_SIDE_MISMATCH",
    "REASON_CHAIN_CONTEXT_NOT_READY",
    "REASON_QUEUE_RELOAD_BLOCKED",
    "REASON_FUTURES_CONTRADICTION_BLOCKED",
    "REASON_MISR_ACTIVE_ZONE_INVALID",
    "REASON_MISC_RETEST_MONITOR_INACTIVE",
]

# =============================================================================
# Batch 11 freeze hardening: support-vs-sequence readiness helpers
# =============================================================================

_BATCH11_ELIGIBILITY_SEQUENCE_VERSION = "1"


def mist_micro_trap_resolved(support: Mapping[str, Any]) -> bool:
    """Compatibility-safe MIST micro-trap resolution.

    Preferred Batch 9+ field:
        micro_trap_resolved

    Legacy compatibility:
        micro_trap_blocked represented the old resolved/not-blocked shell.
    """
    if "micro_trap_resolved" in support:
        return bool(support.get("micro_trap_resolved"))
    return bool(support.get("micro_trap_blocked"))


def annotate_activation_readiness(
    result: BranchEligibilityResult,
    *,
    support: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return report-only activation readiness annotations.

    Eligibility remains necessary-but-not-sufficient. MISC/MISR sequence truth
    must come from doctrine/state-machine layers, not from this static reducer.
    """
    support_map = dict(support or result.support or {})
    structural_support_pass = bool(result.structural_pass)

    sequence_keys = (
        "state_machine_sequence_pass",
        "sequence_pass",
        "event_sequence_pass",
        "setup_sequence_pass",
        "trap_event_sequence_pass",
    )
    state_machine_sequence_pass = any(bool(support_map.get(key)) for key in sequence_keys)

    activation_eligible = bool(
        result.eligible
        and structural_support_pass
        and (
            result.family_id not in (N.STRATEGY_FAMILY_MISC, N.STRATEGY_FAMILY_MISR)
            or state_machine_sequence_pass
        )
    )

    return {
        "structural_support_pass": structural_support_pass,
        "state_machine_sequence_pass": state_machine_sequence_pass,
        "activation_eligible": activation_eligible,
        "eligibility_is_necessary_not_sufficient": True,
    }
