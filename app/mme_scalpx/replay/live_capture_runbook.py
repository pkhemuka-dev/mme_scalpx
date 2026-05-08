from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from app.mme_scalpx.replay.integrity import replay_fingerprint
from app.mme_scalpx.replay.safety import assert_replay_artifact_path

OBSERVE_ONLY_MARKET_SESSION_CAPTURE_RUNBOOK_VERSION = "observe_only_market_session_capture_runbook_v1"

REQUIRED_PRE_SESSION_CHECKS = tuple([
    "confirm_market_open_day",
    "confirm_runtime_observe_only",
    "confirm_paper_armed_false",
    "confirm_live_trading_false",
    "confirm_no_existing_execution_position",
    "confirm_28c_dry_run_passed",
])

REQUIRED_POST_SESSION_EVIDENCE = tuple([
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

REQUIRED_OPERATOR_PLAN_ARTIFACTS = tuple([
    "00_operator_plan_manifest.json",
    "01_pre_session_checklist.json",
    "02_operator_command_sequence.json",
    "03_expected_evidence_map_template.json",
    "04_no_enablement_boundary.json",
    "05_post_session_collection_steps.json",
    "06_failure_diagnostics.json",
    "07_reproducibility.json",
])


def build_observe_only_market_session_capture_runbook() -> dict[str, Any]:
    commands = tuple([
        {
            "step": "operator_plan",
            "operator_command": ".venv/bin/python bin/observe_only_market_session_capture_operator.py --session-id observe_only_YYYYMMDD",
            "executes_in_28d": False,
        },
        {
            "step": "future_capture",
            "operator_command": "Use existing safe observe_only capture flow during market session only.",
            "executes_in_28d": False,
        },
        {
            "step": "post_capture_proofs",
            "operator_command": "Run proof_market_session scripts after capture; do not arm execution.",
            "executes_in_28d": False,
        },
        {
            "step": "collect_package",
            "operator_command": ".venv/bin/python bin/observe_only_live_evidence_collect.py --capture-id observe_only_YYYYMMDD --evidence-map etc/replay/parity/observe_only_YYYYMMDD_evidence_map.json",
            "executes_in_28d": False,
        },
    ])

    safety = {
        "starts_services": False,
        "reads_live_redis": False,
        "writes_live_redis": False,
        "calls_broker_api": False,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
    }

    boundary = {
        "real_live_market_capture": "NOT_PERFORMED_IN_28D",
        "full_live_replay_parity": "NOT_PROVEN_IN_28D",
        "paper_armed_readiness": "NOT_APPROVED_IN_28D",
        "live_trading_readiness": "NOT_APPROVED_IN_28D",
        "production_strategy_improvement_claim": "NOT_PROVEN_IN_28D",
        "production_doctrine_revision": "NOT_APPROVED_IN_28D",
    }

    plan = {
        "schema_version": OBSERVE_ONLY_MARKET_SESSION_CAPTURE_RUNBOOK_VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "accepted_for": "OBSERVE_ONLY_MARKET_SESSION_CAPTURE_RUNBOOK_ONLY",
        "operator_plan_only": True,
        "actual_live_market_capture": False,
        "required_pre_session_checks": REQUIRED_PRE_SESSION_CHECKS,
        "required_post_session_evidence": REQUIRED_POST_SESSION_EVIDENCE,
        "required_plan_artifacts": REQUIRED_OPERATOR_PLAN_ARTIFACTS,
        "operator_command_sequence": commands,
        "evidence_map_template": {item: "future_session_artifact_path" for item in REQUIRED_POST_SESSION_EVIDENCE},
        "failure_diagnostics": tuple([
            "Stop if no_order_sent proof fails.",
            "Stop if broker_call_reachable is true.",
            "Stop if live_redis_write_reachable is true.",
            "Stop if runtime_promotion_reachable is true.",
            "Stop if paper_armed or live trading is enabled.",
        ]),
        "post_session_collection_steps": tuple([
            "Freeze generated market-session proof files.",
            "Create session evidence map JSON.",
            "Run observe_only_live_evidence_collect.py.",
            "Do not change production doctrine from replay output.",
        ]),
        "safety_boundary": safety,
        "not_proven_boundary": boundary,
    }

    plan["runbook_reproducibility_hash"] = replay_fingerprint({
        "schema_version": plan["schema_version"],
        "checks": plan["required_pre_session_checks"],
        "evidence": plan["required_post_session_evidence"],
        "safety": safety,
        "boundary": boundary,
    })

    return plan


def validate_observe_only_market_session_capture_runbook(plan: Mapping[str, Any]) -> dict[str, Any]:
    safety = dict(plan.get("safety_boundary") or {})
    boundary = dict(plan.get("not_proven_boundary") or {})
    commands = tuple(plan.get("operator_command_sequence") or ())

    ok = (
        tuple(plan.get("required_pre_session_checks") or ()) == REQUIRED_PRE_SESSION_CHECKS
        and tuple(plan.get("required_post_session_evidence") or ()) == REQUIRED_POST_SESSION_EVIDENCE
        and tuple(plan.get("required_plan_artifacts") or ()) == REQUIRED_OPERATOR_PLAN_ARTIFACTS
        and all(item.get("executes_in_28d") is False for item in commands)
        and plan.get("operator_plan_only") is True
        and plan.get("actual_live_market_capture") is False
        and safety.get("starts_services") is False
        and safety.get("reads_live_redis") is False
        and safety.get("writes_live_redis") is False
        and safety.get("calls_broker_api") is False
        and safety.get("paper_armed_approved") is False
        and safety.get("live_trading_approved") is False
        and boundary.get("full_live_replay_parity") == "NOT_PROVEN_IN_28D"
        and bool(plan.get("runbook_reproducibility_hash"))
    )

    return {"ok": bool(ok)}


def materialize_observe_only_market_session_operator_plan(*, session_id: str, root: str) -> dict[str, Any]:
    artifact_root = Path(root)
    assert_replay_artifact_path(str(artifact_root / "00_operator_plan_manifest.json"))
    artifact_root.mkdir(parents=True, exist_ok=True)

    plan = build_observe_only_market_session_capture_runbook()
    validation = validate_observe_only_market_session_capture_runbook(plan)

    payloads = {
        "00_operator_plan_manifest.json": plan,
        "01_pre_session_checklist.json": {"items": REQUIRED_PRE_SESSION_CHECKS, "checked_in_28d": False},
        "02_operator_command_sequence.json": {"commands": plan["operator_command_sequence"], "executed_in_28d": False},
        "03_expected_evidence_map_template.json": {"template": plan["evidence_map_template"]},
        "04_no_enablement_boundary.json": {**plan["safety_boundary"], "full_live_replay_parity": "NOT_PROVEN_IN_28D"},
        "05_post_session_collection_steps.json": {"items": plan["post_session_collection_steps"]},
        "06_failure_diagnostics.json": {"items": plan["failure_diagnostics"]},
        "07_reproducibility.json": {
            "session_id": session_id,
            "runbook_reproducibility_hash": plan["runbook_reproducibility_hash"],
        },
    }

    written = {}
    for name, payload in payloads.items():
        path = artifact_root / name
        path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
        written[name] = str(path)

    return {
        "schema_version": "observe_only_market_session_operator_plan_materialization_v1",
        "session_id": session_id,
        "artifact_root": str(artifact_root),
        "required_artifacts": REQUIRED_OPERATOR_PLAN_ARTIFACTS,
        "written_artifacts": written,
        "written_count": len(written),
        "validation": validation,
        "accepted_for": "OBSERVE_ONLY_MARKET_SESSION_CAPTURE_RUNBOOK_ONLY",
        "operator_plan_only": True,
        "actual_live_market_capture": False,
        "starts_services": False,
        "reads_live_redis": False,
        "writes_live_redis": False,
        "calls_broker_api": False,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28D",
    }


def validate_materialized_observe_only_market_session_operator_plan(result: Mapping[str, Any]) -> dict[str, Any]:
    root = Path(str(result.get("artifact_root")))
    written = dict(result.get("written_artifacts") or {})

    missing = tuple(
        name
        for name in REQUIRED_OPERATOR_PLAN_ARTIFACTS
        if name not in written or not Path(written[name]).is_file()
    )

    ok = (
        not missing
        and (str(root).startswith("run/replay") or "/run/replay/" in str(root))
        and int(result.get("written_count", -1)) == len(REQUIRED_OPERATOR_PLAN_ARTIFACTS)
        and dict(result.get("validation") or {}).get("ok") is True
        and result.get("operator_plan_only") is True
        and result.get("actual_live_market_capture") is False
        and result.get("starts_services") is False
        and result.get("reads_live_redis") is False
        and result.get("writes_live_redis") is False
        and result.get("calls_broker_api") is False
        and result.get("paper_armed_approved") is False
        and result.get("live_trading_approved") is False
        and result.get("full_live_replay_parity") == "NOT_PROVEN_IN_28D"
    )

    return {"ok": bool(ok), "missing": missing}


__all__ = tuple([
    "OBSERVE_ONLY_MARKET_SESSION_CAPTURE_RUNBOOK_VERSION",
    "REQUIRED_PRE_SESSION_CHECKS",
    "REQUIRED_POST_SESSION_EVIDENCE",
    "REQUIRED_OPERATOR_PLAN_ARTIFACTS",
    "build_observe_only_market_session_capture_runbook",
    "validate_observe_only_market_session_capture_runbook",
    "materialize_observe_only_market_session_operator_plan",
    "validate_materialized_observe_only_market_session_operator_plan",
])
