from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from app.mme_scalpx.replay.integrity import replay_fingerprint
from app.mme_scalpx.replay.safety import assert_replay_artifact_path
from app.mme_scalpx.replay.strategy_adapter import REPLAY_STRATEGY_FAMILIES, REPLAY_STRATEGY_SIDES


REPLAY_LIVE_PARITY_AUDIT_PLAN_CONTRACT_VERSION = "replay_live_parity_audit_plan_v1"

REPLAY_LIVE_PARITY_REQUIRED_LIVE_EVIDENCE = tuple([
    "provider_runtime",
    "feed_snapshot",
    "feature_payload",
    "family_surfaces",
    "strategy_activation",
    "no_order_sent",
    "live_capture_log",
    "live_stream_inventory",
    "live_hash_inventory",
    "provider_health_snapshot",
    "selected_option_context",
    "dhan_oi_ladder_context_if_available",
])

REPLAY_LIVE_PARITY_REQUIRED_REPLAY_EVIDENCE = tuple([
    "dataset_manifest",
    "replay_run_manifest",
    "replay_transport_manifest",
    "feature_family_adapter_proof",
    "strategy_family_adapter_proof",
    "risk_execution_shadow_proof",
    "scenario_profile_manifest",
    "batch_runner_artifacts",
    "report_exports",
    "experiment_artifacts",
])

REPLAY_LIVE_PARITY_SECTIONS = tuple([
    "provider_runtime_parity",
    "stream_shape_parity",
    "hash_shape_parity",
    "timestamp_staleness_parity",
    "dataset_row_parity",
    "feature_payload_parity",
    "family_surface_parity",
    "strategy_decision_parity",
    "risk_execution_shadow_parity",
    "report_export_parity",
    "safety_no_order_parity",
])

REPLAY_LIVE_PARITY_REQUIRED_ARTIFACTS = tuple([
    "00_parity_plan_manifest.json",
    "01_required_live_evidence.json",
    "02_required_replay_evidence.json",
    "03_contract_parity_matrix.json",
    "04_field_parity_matrix.json",
    "05_family_side_parity_matrix.json",
    "06_acceptance_gates.json",
    "07_not_proven_boundary.json",
    "08_parity_runbook.json",
    "09_plan_reproducibility.json",
])


def build_replay_live_parity_contract_matrix() -> tuple[dict[str, Any], ...]:
    families_sides = tuple(
        family + "_" + side for family in REPLAY_STRATEGY_FAMILIES for side in REPLAY_STRATEGY_SIDES
    )

    return tuple([
        {
            "section": "provider_runtime_parity",
            "live_source": "future observe_only provider_runtime proof/capture",
            "replay_source": "replay transport/provider-context artifacts",
            "required_fields": tuple(["active_futures_provider", "active_option_provider", "provider_ready", "provider_health"]),
            "verdict_28a": "PLAN_ONLY_NOT_PROVEN",
        },
        {
            "section": "stream_shape_parity",
            "live_source": "future live Redis stream inventory",
            "replay_source": "isolated replay namespace transport inventory",
            "required_fields": tuple(["stream_name", "event_order", "payload_keys", "timestamp_fields", "provider_id"]),
            "verdict_28a": "PLAN_ONLY_NOT_PROVEN",
        },
        {
            "section": "hash_shape_parity",
            "live_source": "future live Redis hash inventory",
            "replay_source": "replay namespace hash/state artifacts",
            "required_fields": tuple(["hash_name", "field_names", "json_payloads", "safety_flags"]),
            "verdict_28a": "PLAN_ONLY_NOT_PROVEN",
        },
        {
            "section": "feature_payload_parity",
            "live_source": "future feature payload capture",
            "replay_source": "feature-family adapter proof and replay feature summaries",
            "required_fields": tuple(["family_features_json", "family_surfaces", "provider_context", "side_split"]),
            "verdict_28a": "PLAN_ONLY_NOT_PROVEN",
        },
        {
            "section": "family_surface_parity",
            "live_source": "future live family_surfaces proof/capture",
            "replay_source": "replay family adapter / strategy adapter proofs",
            "required_fields": families_sides,
            "verdict_28a": "PLAN_ONLY_NOT_PROVEN",
        },
        {
            "section": "strategy_decision_parity",
            "live_source": "future strategy_activation and no_order_sent proofs",
            "replay_source": "strategy-family adapter arbitration and replay reports",
            "required_fields": tuple(["final_action", "candidate_count", "blocker_chain", "decision_reason", "orders_sent"]),
            "verdict_28a": "PLAN_ONLY_NOT_PROVEN",
        },
        {
            "section": "risk_execution_shadow_parity",
            "live_source": "future risk/execution no-order observe_only state",
            "replay_source": "risk adapter / execution shadow artifacts",
            "required_fields": tuple(["entry_vetoed", "shadow_fill_status", "real_order_sent", "broker_calls_executed"]),
            "verdict_28a": "PLAN_ONLY_NOT_PROVEN",
        },
        {
            "section": "report_export_parity",
            "live_source": "future live observation reports if available",
            "replay_source": "27L report/export workstation",
            "required_fields": tuple(["trade_log", "candidate_log", "blocker_chain", "side_split", "family_split", "pnl_shadow"]),
            "verdict_28a": "PLAN_ONLY_NOT_PROVEN",
        },
        {
            "section": "safety_no_order_parity",
            "live_source": "future no_order_sent proof and broker audit",
            "replay_source": "replay no-live/no-broker/no-redis proofs",
            "required_fields": tuple(["broker_call_reachable", "live_redis_write_reachable", "runtime_promotion_reachable", "real_order_sent"]),
            "verdict_28a": "PLAN_ONLY_NOT_PROVEN",
        },
    ])


def build_replay_live_parity_field_matrix() -> tuple[dict[str, Any], ...]:
    rows = []
    fields = tuple([
        ("timestamp_ns", "event ordering / staleness"),
        ("provider_id", "provider runtime parity"),
        ("instrument_token", "instrument identity parity"),
        ("symbol", "instrument identity parity"),
        ("side", "CALL/PUT separation"),
        ("family", "5-family separation"),
        ("family_features_json", "feature payload parity"),
        ("family_surfaces", "strategy surface parity"),
        ("candidate_metadata", "candidate parity"),
        ("blocker_chain", "blocker parity"),
        ("decision_action", "decision parity"),
        ("risk_veto", "risk parity"),
        ("shadow_fill", "execution-shadow parity"),
        ("dhan_context_age", "Dhan context parity"),
        ("oi_ladder", "OI ladder parity"),
        ("oi_wall", "OI wall parity"),
    ])
    for field, purpose in fields:
        rows.append({
            "field": field,
            "purpose": purpose,
            "live_required": True,
            "replay_required": True,
            "comparison_method": "exact_or_tolerance_defined_in_future_28B",
            "verdict_28a": "PLAN_ONLY_NOT_PROVEN",
        })
    return tuple(rows)


def build_replay_live_parity_family_side_matrix() -> tuple[dict[str, Any], ...]:
    rows = []
    for family in REPLAY_STRATEGY_FAMILIES:
        for side in REPLAY_STRATEGY_SIDES:
            rows.append({
                "family": family,
                "side": side,
                "live_surface_required": True,
                "replay_surface_required": True,
                "candidate_report_required": True,
                "blocker_report_required": True,
                "decision_report_required": True,
                "verdict_28a": "PLAN_ONLY_NOT_PROVEN",
            })
    return tuple(rows)


def build_replay_live_parity_acceptance_gates() -> tuple[dict[str, Any], ...]:
    return tuple([
        {"gate": "evidence_presence", "required": "all required live and replay evidence files present", "status_28a": "DEFINED_NOT_EXECUTED"},
        {"gate": "contract_shape_comparison", "required": "live and replay contract keys mapped section-by-section", "status_28a": "DEFINED_NOT_EXECUTED"},
        {"gate": "field_tolerance_policy", "required": "exact/tolerance rules declared before comparison", "status_28a": "DEFINED_NOT_EXECUTED"},
        {"gate": "family_side_coverage", "required": "MIST/MISB/MISC/MISR/MISO x CALL/PUT coverage", "status_28a": "DEFINED_NOT_EXECUTED"},
        {"gate": "no_order_safety", "required": "broker_call=false, live_redis_write=false, runtime_promotion=false, real_order=false", "status_28a": "DEFINED_NOT_EXECUTED"},
        {"gate": "doctrine_boundary", "required": "replay findings advisory only; no production doctrine change", "status_28a": "DEFINED_NOT_EXECUTED"},
    ])


def build_replay_live_parity_audit_plan() -> dict[str, Any]:
    plan = {
        "schema_version": REPLAY_LIVE_PARITY_AUDIT_PLAN_CONTRACT_VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "accepted_for": "PARITY_AUDIT_PLAN_ONLY",
        "purpose": "Define future replay/live parity audit after a real observe_only market session capture.",
        "required_live_evidence": REPLAY_LIVE_PARITY_REQUIRED_LIVE_EVIDENCE,
        "required_replay_evidence": REPLAY_LIVE_PARITY_REQUIRED_REPLAY_EVIDENCE,
        "parity_sections": REPLAY_LIVE_PARITY_SECTIONS,
        "required_artifacts": REPLAY_LIVE_PARITY_REQUIRED_ARTIFACTS,
        "contract_matrix": build_replay_live_parity_contract_matrix(),
        "field_matrix": build_replay_live_parity_field_matrix(),
        "family_side_matrix": build_replay_live_parity_family_side_matrix(),
        "acceptance_gates": build_replay_live_parity_acceptance_gates(),
        "runbook": {
            "step_1": "Capture an observe_only live market session without paper/live enablement.",
            "step_2": "Freeze live evidence files and stream/hash inventories.",
            "step_3": "Build replay dataset from the same session capture.",
            "step_4": "Run replay in isolated replay namespace.",
            "step_5": "Compare provider, transport, feature, family, strategy, risk, execution-shadow, and report surfaces.",
            "step_6": "Record gaps as replay/live parity findings only.",
            "step_7": "Do not mutate production doctrine without separate evidence, review, and freeze.",
        },
        "not_proven_boundary": {
            "full_live_replay_parity": "NOT_PROVEN_IN_28A",
            "paper_armed_readiness": "NOT_APPROVED_IN_28A",
            "live_trading_readiness": "NOT_APPROVED_IN_28A",
            "production_strategy_improvement_claim": "NOT_PROVEN_IN_28A",
            "production_doctrine_revision": "NOT_APPROVED_IN_28A",
        },
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
    }

    plan["plan_reproducibility_hash"] = replay_fingerprint({
        "schema_version": plan["schema_version"],
        "required_live_evidence": plan["required_live_evidence"],
        "required_replay_evidence": plan["required_replay_evidence"],
        "parity_sections": plan["parity_sections"],
        "contract_matrix": plan["contract_matrix"],
        "field_matrix": plan["field_matrix"],
        "family_side_matrix": plan["family_side_matrix"],
        "acceptance_gates": plan["acceptance_gates"],
        "not_proven_boundary": plan["not_proven_boundary"],
    })
    return plan


def validate_replay_live_parity_audit_plan(plan: Mapping[str, Any]) -> dict[str, Any]:
    required_live_ok = tuple(plan.get("required_live_evidence") or ()) == REPLAY_LIVE_PARITY_REQUIRED_LIVE_EVIDENCE
    required_replay_ok = tuple(plan.get("required_replay_evidence") or ()) == REPLAY_LIVE_PARITY_REQUIRED_REPLAY_EVIDENCE
    sections_ok = tuple(plan.get("parity_sections") or ()) == REPLAY_LIVE_PARITY_SECTIONS
    artifacts_ok = tuple(plan.get("required_artifacts") or ()) == REPLAY_LIVE_PARITY_REQUIRED_ARTIFACTS
    family_side_ok = len(tuple(plan.get("family_side_matrix") or ())) == len(REPLAY_STRATEGY_FAMILIES) * len(REPLAY_STRATEGY_SIDES)
    hash_ok = bool(plan.get("plan_reproducibility_hash"))
    boundary = dict(plan.get("not_proven_boundary") or {})
    boundary_ok = (
        boundary.get("full_live_replay_parity") == "NOT_PROVEN_IN_28A"
        and boundary.get("paper_armed_readiness") == "NOT_APPROVED_IN_28A"
        and boundary.get("live_trading_readiness") == "NOT_APPROVED_IN_28A"
        and boundary.get("production_strategy_improvement_claim") == "NOT_PROVEN_IN_28A"
        and boundary.get("production_doctrine_revision") == "NOT_APPROVED_IN_28A"
    )
    no_live_ok = (
        plan.get("paper_armed_approved") is False
        and plan.get("live_trading_approved") is False
        and plan.get("execution_arming_created") is False
        and plan.get("real_order_sent") is False
        and plan.get("broker_calls_executed") is False
        and plan.get("live_redis_writes_executed") is False
        and plan.get("production_doctrine_changed") is False
    )
    ok = bool(required_live_ok and required_replay_ok and sections_ok and artifacts_ok and family_side_ok and hash_ok and boundary_ok and no_live_ok)
    return {
        "ok": ok,
        "required_live_ok": required_live_ok,
        "required_replay_ok": required_replay_ok,
        "sections_ok": sections_ok,
        "artifacts_ok": artifacts_ok,
        "family_side_ok": family_side_ok,
        "hash_ok": hash_ok,
        "boundary_ok": boundary_ok,
        "no_live_ok": no_live_ok,
    }


def materialize_replay_live_parity_audit_plan(*, run_id: str, root: str) -> dict[str, Any]:
    artifact_root = Path(root)
    assert_replay_artifact_path(str(artifact_root / "00_parity_plan_manifest.json"))
    artifact_root.mkdir(parents=True, exist_ok=True)

    plan = build_replay_live_parity_audit_plan()
    validation = validate_replay_live_parity_audit_plan(plan)

    payloads = {
        "00_parity_plan_manifest.json": plan,
        "01_required_live_evidence.json": {
            "schema_version": "replay_live_parity_required_live_evidence_v1",
            "items": REPLAY_LIVE_PARITY_REQUIRED_LIVE_EVIDENCE,
            "status_28a": "DEFINED_NOT_COLLECTED",
            "paper_armed_approved": False,
            "live_trading_approved": False,
            "production_doctrine_changed": False,
        },
        "02_required_replay_evidence.json": {
            "schema_version": "replay_live_parity_required_replay_evidence_v1",
            "items": REPLAY_LIVE_PARITY_REQUIRED_REPLAY_EVIDENCE,
            "status_28a": "DEFINED_FROM_27N_WORKSTATION",
            "paper_armed_approved": False,
            "live_trading_approved": False,
            "production_doctrine_changed": False,
        },
        "03_contract_parity_matrix.json": plan["contract_matrix"],
        "04_field_parity_matrix.json": plan["field_matrix"],
        "05_family_side_parity_matrix.json": plan["family_side_matrix"],
        "06_acceptance_gates.json": plan["acceptance_gates"],
        "07_not_proven_boundary.json": plan["not_proven_boundary"],
        "08_parity_runbook.json": plan["runbook"],
        "09_plan_reproducibility.json": {
            "schema_version": "replay_live_parity_plan_reproducibility_v1",
            "run_id": run_id,
            "plan_reproducibility_hash": plan["plan_reproducibility_hash"],
            "paper_armed_approved": False,
            "live_trading_approved": False,
            "production_doctrine_changed": False,
        },
    }

    written = {}
    for name, payload in payloads.items():
        path = artifact_root / name
        path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
        written[name] = str(path)

    return {
        "schema_version": "replay_live_parity_audit_plan_materialization_v1",
        "run_id": run_id,
        "artifact_root": str(artifact_root),
        "required_artifacts": REPLAY_LIVE_PARITY_REQUIRED_ARTIFACTS,
        "written_artifacts": written,
        "written_count": len(written),
        "plan": plan,
        "validation": validation,
        "plan_reproducibility_hash": plan["plan_reproducibility_hash"],
        "accepted_for": "PARITY_AUDIT_PLAN_ONLY",
        "full_live_replay_parity": "NOT_PROVEN_IN_28A",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
    }


def validate_materialized_replay_live_parity_plan(result: Mapping[str, Any]) -> dict[str, Any]:
    root = Path(str(result.get("artifact_root")))
    written = dict(result.get("written_artifacts") or {})
    missing = tuple(name for name in REPLAY_LIVE_PARITY_REQUIRED_ARTIFACTS if name not in written or not Path(written[name]).exists())
    root_ok = str(root).startswith("run/replay") or "/run/replay/" in str(root)
    count_ok = int(result.get("written_count", -1)) == len(REPLAY_LIVE_PARITY_REQUIRED_ARTIFACTS)
    validation_ok = dict(result.get("validation") or {}).get("ok") is True
    no_live_ok = (
        result.get("paper_armed_approved") is False
        and result.get("live_trading_approved") is False
        and result.get("execution_arming_created") is False
        and result.get("real_order_sent") is False
        and result.get("broker_calls_executed") is False
        and result.get("live_redis_writes_executed") is False
        and result.get("production_doctrine_changed") is False
    )
    not_proven_ok = result.get("full_live_replay_parity") == "NOT_PROVEN_IN_28A"
    ok = bool(not missing and root_ok and count_ok and validation_ok and no_live_ok and not_proven_ok)
    return {
        "ok": ok,
        "missing": missing,
        "root_ok": root_ok,
        "count_ok": count_ok,
        "validation_ok": validation_ok,
        "no_live_ok": no_live_ok,
        "not_proven_ok": not_proven_ok,
    }


def replay_live_parity_audit_plan_summary() -> dict[str, Any]:
    return {
        "schema_version": REPLAY_LIVE_PARITY_AUDIT_PLAN_CONTRACT_VERSION,
        "required_live_evidence": REPLAY_LIVE_PARITY_REQUIRED_LIVE_EVIDENCE,
        "required_replay_evidence": REPLAY_LIVE_PARITY_REQUIRED_REPLAY_EVIDENCE,
        "parity_sections": REPLAY_LIVE_PARITY_SECTIONS,
        "required_artifacts": REPLAY_LIVE_PARITY_REQUIRED_ARTIFACTS,
        "accepted_for": "PARITY_AUDIT_PLAN_ONLY",
        "full_live_replay_parity": "NOT_PROVEN_IN_28A",
        "paper_armed_readiness": "NOT_APPROVED_IN_28A",
        "live_trading_readiness": "NOT_APPROVED_IN_28A",
        "production_strategy_improvement_claim": "NOT_PROVEN_IN_28A",
        "production_doctrine_revision": "NOT_APPROVED_IN_28A",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "broker_calls_allowed": False,
        "live_redis_writes_allowed": False,
        "production_doctrine_changed": False,
    }


__all__ = tuple([
    "REPLAY_LIVE_PARITY_AUDIT_PLAN_CONTRACT_VERSION",
    "REPLAY_LIVE_PARITY_REQUIRED_LIVE_EVIDENCE",
    "REPLAY_LIVE_PARITY_REQUIRED_REPLAY_EVIDENCE",
    "REPLAY_LIVE_PARITY_SECTIONS",
    "REPLAY_LIVE_PARITY_REQUIRED_ARTIFACTS",
    "build_replay_live_parity_contract_matrix",
    "build_replay_live_parity_field_matrix",
    "build_replay_live_parity_family_side_matrix",
    "build_replay_live_parity_acceptance_gates",
    "build_replay_live_parity_audit_plan",
    "validate_replay_live_parity_audit_plan",
    "materialize_replay_live_parity_audit_plan",
    "validate_materialized_replay_live_parity_plan",
    "replay_live_parity_audit_plan_summary",
])

# BEGIN BATCH28B_LIVE_EVIDENCE_LINK

def observe_only_live_evidence_required_for_parity():
    from app.mme_scalpx.replay.live_evidence import OBSERVE_ONLY_REQUIRED_EVIDENCE_ITEMS
    return tuple(OBSERVE_ONLY_REQUIRED_EVIDENCE_ITEMS)

try:
    __all__
except NameError:
    __all__ = tuple()

__all__ = tuple(dict.fromkeys(tuple(__all__) + (
    "observe_only_live_evidence_required_for_parity",
)))

# END BATCH28B_LIVE_EVIDENCE_LINK

