from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping

from app.mme_scalpx.replay.feature_adapter import (
    REPLAY_FEATURE_FAMILIES,
    REPLAY_FEATURE_SIDES,
    REPLAY_FAMILY_REQUIRED_SURFACE_TERMS,
)
from app.mme_scalpx.replay.live_adapter import publish_replay_live_shape
from app.mme_scalpx.replay.transport import LocalReplayTransport


REPLAY_STRATEGY_ADAPTER_CONTRACT_VERSION = "replay_strategy_family_adapter_v1"

REPLAY_STRATEGY_FAMILIES = tuple(REPLAY_FEATURE_FAMILIES)
REPLAY_STRATEGY_SIDES = tuple(REPLAY_FEATURE_SIDES)

REPLAY_STRATEGY_ALLOWED_FINAL_ACTIONS = ("HOLD_REPORT_ONLY",)

REPLAY_STRATEGY_REQUIRED_CANDIDATE_FIELDS = (
    "schema_version",
    "run_id",
    "family",
    "side",
    "candidate_id",
    "candidate_present",
    "eligible",
    "score",
    "blockers",
    "metadata",
    "order_allowed",
    "paper_armed_approved",
    "live_trading_approved",
    "production_doctrine_changed",
)

REPLAY_STRATEGY_REQUIRED_ARBITRATION_FIELDS = (
    "schema_version",
    "run_id",
    "candidate_count",
    "eligible_candidate_count",
    "winner",
    "winning_family",
    "winning_side",
    "final_action",
    "order_allowed",
    "arbitration_reason",
    "paper_armed_approved",
    "live_trading_approved",
    "production_doctrine_changed",
)


@dataclass(frozen=True)
class ReplayStrategyAdapterResult:
    schema_version: str
    run_id: str
    candidates: tuple[dict[str, Any], ...]
    arbitration: dict[str, Any]
    decision_payload: dict[str, Any]
    strategy_decision_generated: bool = True
    real_order_intent_generated: bool = False
    paper_armed_approved: bool = False
    live_trading_approved: bool = False
    execution_arming_created: bool = False
    production_doctrine_changed: bool = False


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _truthy(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "ok", "pass"}
    return bool(value)


def _family_surface_score(family: str, surface: Mapping[str, Any]) -> tuple[float, tuple[str, ...]]:
    terms = REPLAY_FAMILY_REQUIRED_SURFACE_TERMS[family]
    blockers: list[str] = []
    score = 0.0

    for term in terms:
        value = surface.get(term)
        if isinstance(value, bool):
            if value:
                score += 1.0
            else:
                blockers.append(f"{term}_false")
        elif value is None:
            blockers.append(f"{term}_missing")
        elif isinstance(value, (int, float)):
            score += min(float(value), 1.0) if value > 0 else 0.0
        elif isinstance(value, str):
            if value:
                score += 1.0
            else:
                blockers.append(f"{term}_empty")
        elif isinstance(value, Mapping):
            if value:
                score += 1.0
            else:
                blockers.append(f"{term}_empty_mapping")
        else:
            score += 1.0 if _truthy(value) else 0.0

    # Family-specific safe replay readiness hints.
    if family == "MISO":
        if surface.get("provider_ready_miso") is not True:
            blockers.append("provider_ready_miso_false")
        if not surface.get("burst_event_id"):
            blockers.append("burst_event_id_missing")
    if family == "MISR":
        if not surface.get("trap_event_id"):
            blockers.append("trap_event_id_missing")

    return score, tuple(blockers)


def build_replay_strategy_candidates(
    *,
    run_id: str,
    feature_payload: Mapping[str, Any],
) -> tuple[dict[str, Any], ...]:
    family_surfaces = feature_payload.get("family_surfaces") or {}
    candidates: list[dict[str, Any]] = []

    for family in REPLAY_STRATEGY_FAMILIES:
        side_surfaces = family_surfaces.get(family, {})
        for side in REPLAY_STRATEGY_SIDES:
            surface = dict(side_surfaces.get(side, {}))
            score, blockers = _family_surface_score(family, surface)
            eligible = bool(score > 0 and not blockers)
            candidate_id = f"{run_id}|{family}|{side}"
            candidate = {
                "schema_version": "replay_strategy_candidate_v1",
                "run_id": str(run_id),
                "family": family,
                "side": side,
                "candidate_id": candidate_id,
                "candidate_present": bool(surface),
                "eligible": eligible,
                "score": score,
                "blockers": blockers,
                "metadata": {
                    "surface_kind": surface.get("surface_kind"),
                    "source": "replay_strategy_adapter",
                    "strategy_decision_parity": "NOT_PROVEN_IN_27H",
                    "safe_decision_shape_parity": "PROVEN_BY_27H",
                    "surface": surface,
                },
                "order_allowed": False,
                "real_order_intent_generated": False,
                "paper_armed_approved": False,
                "live_trading_approved": False,
                "execution_arming_created": False,
                "production_doctrine_changed": False,
            }
            candidates.append(candidate)

    return tuple(candidates)


def arbitrate_replay_strategy_candidates(
    *,
    run_id: str,
    candidates: tuple[Mapping[str, Any], ...] | list[Mapping[str, Any]],
) -> dict[str, Any]:
    candidate_rows = [dict(c) for c in candidates]
    eligible = [c for c in candidate_rows if c.get("eligible") is True]
    winner = None
    if eligible:
        # Deterministic arbitration: highest score, then family order, then side order.
        family_order = {family: index for index, family in enumerate(REPLAY_STRATEGY_FAMILIES)}
        side_order = {side: index for index, side in enumerate(REPLAY_STRATEGY_SIDES)}
        winner = sorted(
            eligible,
            key=lambda c: (
                -float(c.get("score", 0.0)),
                family_order.get(str(c.get("family")), 999),
                side_order.get(str(c.get("side")), 999),
                str(c.get("candidate_id")),
            ),
        )[0]

    arbitration = {
        "schema_version": "replay_strategy_arbitration_v1",
        "run_id": str(run_id),
        "candidate_count": len(candidate_rows),
        "eligible_candidate_count": len(eligible),
        "winner": winner,
        "winning_family": winner.get("family") if winner else None,
        "winning_side": winner.get("side") if winner else None,
        "final_action": "HOLD_REPORT_ONLY",
        "order_allowed": False,
        "real_order_intent_generated": False,
        "arbitration_reason": "winner_selected_for_research_only_hold_report" if winner else "no_eligible_candidate_hold_report",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "production_doctrine_changed": False,
    }
    return arbitration


def build_replay_strategy_decision_payload(
    *,
    run_id: str,
    feature_payload: Mapping[str, Any],
) -> ReplayStrategyAdapterResult:
    candidates = build_replay_strategy_candidates(run_id=run_id, feature_payload=feature_payload)
    arbitration = arbitrate_replay_strategy_candidates(run_id=run_id, candidates=candidates)

    decision_payload = {
        "schema_version": REPLAY_STRATEGY_ADAPTER_CONTRACT_VERSION,
        "run_id": str(run_id),
        "candidates": candidates,
        "candidate_count": len(candidates),
        "arbitration": arbitration,
        "final_action": "HOLD_REPORT_ONLY",
        "action": "HOLD_REPORT_ONLY",
        "order_allowed": False,
        "real_order_intent_generated": False,
        "strategy_decision_generated": True,
        "strategy_decision_replay_only": True,
        "strategy_decision_parity": "NOT_PROVEN_IN_27H",
        "safe_decision_shape_parity": "PROVEN_BY_27H",
        "candidate_json": _canonical_json(candidates),
        "arbitration_json": _canonical_json(arbitration),
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "production_doctrine_changed": False,
    }

    return ReplayStrategyAdapterResult(
        schema_version=REPLAY_STRATEGY_ADAPTER_CONTRACT_VERSION,
        run_id=str(run_id),
        candidates=tuple(dict(c) for c in candidates),
        arbitration=arbitration,
        decision_payload=decision_payload,
    )


def publish_replay_strategy_decision(
    transport: LocalReplayTransport,
    *,
    run_id: str,
    feature_payload: Mapping[str, Any],
    event_ts_ns: int | None = None,
    sequence_id: int | None = None,
) -> dict[str, Any]:
    result = build_replay_strategy_decision_payload(run_id=run_id, feature_payload=feature_payload)
    return publish_replay_live_shape(
        transport,
        surface="strategy_decision",
        row=result.decision_payload,
        event_ts_ns=event_ts_ns,
        sequence_id=sequence_id,
    )


def validate_replay_strategy_candidates(candidates: tuple[Mapping[str, Any], ...] | list[Mapping[str, Any]]) -> dict[str, Any]:
    rows = [dict(c) for c in candidates]
    missing_by_candidate: dict[str, tuple[str, ...]] = {}
    family_side = set()

    for candidate in rows:
        candidate_id = str(candidate.get("candidate_id"))
        missing = tuple(
            field for field in REPLAY_STRATEGY_REQUIRED_CANDIDATE_FIELDS
            if field not in candidate
        )
        missing_by_candidate[candidate_id] = missing
        family_side.add((candidate.get("family"), candidate.get("side")))

    required_pairs = {
        (family, side)
        for family in REPLAY_STRATEGY_FAMILIES
        for side in REPLAY_STRATEGY_SIDES
    }

    no_approval_ok = all(
        c.get("order_allowed") is False
        and c.get("real_order_intent_generated") is False
        and c.get("paper_armed_approved") is False
        and c.get("live_trading_approved") is False
        and c.get("execution_arming_created") is False
        and c.get("production_doctrine_changed") is False
        for c in rows
    )

    ok = bool(
        len(rows) == len(required_pairs)
        and family_side == required_pairs
        and all(not missing for missing in missing_by_candidate.values())
        and no_approval_ok
    )

    return {
        "ok": ok,
        "candidate_count": len(rows),
        "required_candidate_count": len(required_pairs),
        "family_side_coverage_ok": family_side == required_pairs,
        "missing_by_candidate": missing_by_candidate,
        "no_approval_ok": no_approval_ok,
    }


def validate_replay_strategy_arbitration(arbitration: Mapping[str, Any]) -> dict[str, Any]:
    missing = tuple(
        field for field in REPLAY_STRATEGY_REQUIRED_ARBITRATION_FIELDS
        if field not in arbitration
    )
    final_action_ok = arbitration.get("final_action") in REPLAY_STRATEGY_ALLOWED_FINAL_ACTIONS
    no_order_ok = (
        arbitration.get("order_allowed") is False
        and arbitration.get("real_order_intent_generated") is False
        and arbitration.get("paper_armed_approved") is False
        and arbitration.get("live_trading_approved") is False
        and arbitration.get("execution_arming_created") is False
        and arbitration.get("production_doctrine_changed") is False
    )

    ok = bool(not missing and final_action_ok and no_order_ok)
    return {
        "ok": ok,
        "missing": missing,
        "final_action_ok": final_action_ok,
        "no_order_ok": no_order_ok,
    }


def replay_strategy_adapter_contract_summary() -> dict[str, Any]:
    return {
        "schema_version": REPLAY_STRATEGY_ADAPTER_CONTRACT_VERSION,
        "families": REPLAY_STRATEGY_FAMILIES,
        "sides": REPLAY_STRATEGY_SIDES,
        "allowed_final_actions": REPLAY_STRATEGY_ALLOWED_FINAL_ACTIONS,
        "candidate_required_fields": REPLAY_STRATEGY_REQUIRED_CANDIDATE_FIELDS,
        "arbitration_required_fields": REPLAY_STRATEGY_REQUIRED_ARBITRATION_FIELDS,
        "safe_decision_shape_parity": "PROVEN_BY_27H",
        "family_side_coverage": "PROVEN_BY_27H",
        "arbitration_surface": "PROVEN_BY_27H",
        "full_live_strategy_decision_parity": "NOT_PROVEN_IN_27H",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "production_doctrine_changed": False,
    }


try:
    __all__
except NameError:
    __all__ = tuple()

__all__ = tuple(dict.fromkeys(tuple(__all__) + (
    "REPLAY_STRATEGY_ADAPTER_CONTRACT_VERSION",
    "REPLAY_STRATEGY_FAMILIES",
    "REPLAY_STRATEGY_SIDES",
    "REPLAY_STRATEGY_ALLOWED_FINAL_ACTIONS",
    "REPLAY_STRATEGY_REQUIRED_CANDIDATE_FIELDS",
    "REPLAY_STRATEGY_REQUIRED_ARBITRATION_FIELDS",
    "ReplayStrategyAdapterResult",
    "build_replay_strategy_candidates",
    "arbitrate_replay_strategy_candidates",
    "build_replay_strategy_decision_payload",
    "publish_replay_strategy_decision",
    "validate_replay_strategy_candidates",
    "validate_replay_strategy_arbitration",
    "replay_strategy_adapter_contract_summary",
)))
