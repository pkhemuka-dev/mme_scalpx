from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from app.mme_scalpx.replay.integrity import replay_fingerprint
from app.mme_scalpx.replay.safety import assert_replay_artifact_path


OBSERVE_ONLY_LIVE_EVIDENCE_CONTRACT_VERSION = "observe_only_live_evidence_capture_contract_v1"

OBSERVE_ONLY_REQUIRED_EVIDENCE_ITEMS = tuple([
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

OBSERVE_ONLY_REQUIRED_ARTIFACTS = tuple([
    "00_live_evidence_manifest.json",
    "01_provider_runtime.json",
    "02_feed_snapshot.json",
    "03_feature_payload.json",
    "04_family_surfaces.json",
    "05_strategy_activation.json",
    "06_no_order_sent.json",
    "07_live_stream_inventory.json",
    "08_live_hash_inventory.json",
    "09_provider_health_snapshot.json",
    "10_selected_option_context.json",
    "11_dhan_oi_ladder_context.json",
    "12_live_capture_log_reference.json",
    "13_capture_completeness.json",
    "14_no_enablement_boundary.json",
    "15_capture_reproducibility.json",
])

OBSERVE_ONLY_EVIDENCE_DEFAULT_SOURCE_HINTS = {
    "provider_runtime": "run/proofs/proof_market_session_provider_runtime.json",
    "feed_snapshot": "run/proofs/proof_market_session_feed_snapshot.json",
    "feature_payload": "run/proofs/proof_market_session_feature_payload.json",
    "family_surfaces": "run/proofs/proof_market_session_family_surfaces.json",
    "strategy_activation": "run/proofs/proof_market_session_strategy_activation.json",
    "no_order_sent": "run/proofs/proof_market_session_no_order_sent.json",
    "live_capture_log": "run/live_capture/<observe_only_capture_log>.log",
    "live_stream_inventory": "future observe_only stream inventory JSON",
    "live_hash_inventory": "future observe_only hash inventory JSON",
    "provider_health_snapshot": "future observe_only provider health snapshot JSON",
    "selected_option_context": "future observe_only selected option context JSON",
    "dhan_oi_ladder_context_if_available": "future observe_only Dhan OI ladder context JSON",
}


def observe_only_live_evidence_contract_summary() -> dict[str, Any]:
    return {
        "schema_version": OBSERVE_ONLY_LIVE_EVIDENCE_CONTRACT_VERSION,
        "accepted_for": "OBSERVE_ONLY_LIVE_EVIDENCE_CAPTURE_CONTRACT_ONLY",
        "required_evidence_items": OBSERVE_ONLY_REQUIRED_EVIDENCE_ITEMS,
        "required_artifacts": OBSERVE_ONLY_REQUIRED_ARTIFACTS,
        "source_hints": OBSERVE_ONLY_EVIDENCE_DEFAULT_SOURCE_HINTS,
        "starts_services": False,
        "reads_live_redis": False,
        "writes_live_redis": False,
        "calls_broker_api": False,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_intent_allowed": False,
        "production_doctrine_changed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28B",
        "paper_armed_readiness": "NOT_APPROVED_IN_28B",
        "live_trading_readiness": "NOT_APPROVED_IN_28B",
        "production_strategy_improvement_claim": "NOT_PROVEN_IN_28B",
        "production_doctrine_revision": "NOT_APPROVED_IN_28B",
    }


def build_observe_only_live_evidence_capture_plan() -> dict[str, Any]:
    plan = observe_only_live_evidence_contract_summary()
    plan.update({
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "capture_rule": "Future capture must be performed only during observe_only/HOLD-report-only mode.",
        "collector_rule": "Collector copies already-generated evidence files only; it does not start services, read Redis, or call brokers.",
        "artifact_root_pattern": "run/replay/parity/live_evidence/<capture_id>/",
        "evidence_mapping_format": {
            "provider_runtime": "/path/to/provider_runtime.json",
            "feed_snapshot": "/path/to/feed_snapshot.json",
            "feature_payload": "/path/to/feature_payload.json",
            "family_surfaces": "/path/to/family_surfaces.json",
            "strategy_activation": "/path/to/strategy_activation.json",
            "no_order_sent": "/path/to/no_order_sent.json",
            "live_capture_log": "/path/to/live_capture.log",
            "live_stream_inventory": "/path/to/live_stream_inventory.json",
            "live_hash_inventory": "/path/to/live_hash_inventory.json",
            "provider_health_snapshot": "/path/to/provider_health_snapshot.json",
            "selected_option_context": "/path/to/selected_option_context.json",
            "dhan_oi_ladder_context_if_available": "/path/to/dhan_oi_ladder_context.json"
        },
        "minimum_complete_required_for_future_28c": tuple([
            "provider_runtime",
            "feed_snapshot",
            "feature_payload",
            "family_surfaces",
            "strategy_activation",
            "no_order_sent",
            "live_stream_inventory",
            "live_hash_inventory",
        ]),
        "optional_but_high_value": tuple([
            "provider_health_snapshot",
            "selected_option_context",
            "dhan_oi_ladder_context_if_available",
            "live_capture_log",
        ]),
    })
    plan["plan_reproducibility_hash"] = replay_fingerprint({
        "schema_version": plan["schema_version"],
        "required_evidence_items": plan["required_evidence_items"],
        "required_artifacts": plan["required_artifacts"],
        "minimum_complete_required_for_future_28c": plan["minimum_complete_required_for_future_28c"],
        "optional_but_high_value": plan["optional_but_high_value"],
        "safety": {
            "starts_services": False,
            "reads_live_redis": False,
            "writes_live_redis": False,
            "calls_broker_api": False,
            "paper_armed_approved": False,
            "live_trading_approved": False,
        },
    })
    return plan


def validate_observe_only_live_evidence_capture_plan(plan: Mapping[str, Any]) -> dict[str, Any]:
    items_ok = tuple(plan.get("required_evidence_items") or ()) == OBSERVE_ONLY_REQUIRED_EVIDENCE_ITEMS
    artifacts_ok = tuple(plan.get("required_artifacts") or ()) == OBSERVE_ONLY_REQUIRED_ARTIFACTS
    hash_ok = bool(plan.get("plan_reproducibility_hash"))
    no_enablement_ok = (
        plan.get("starts_services") is False
        and plan.get("reads_live_redis") is False
        and plan.get("writes_live_redis") is False
        and plan.get("calls_broker_api") is False
        and plan.get("paper_armed_approved") is False
        and plan.get("live_trading_approved") is False
        and plan.get("execution_arming_created") is False
        and plan.get("real_order_intent_allowed") is False
        and plan.get("production_doctrine_changed") is False
    )
    boundary_ok = (
        plan.get("full_live_replay_parity") == "NOT_PROVEN_IN_28B"
        and plan.get("paper_armed_readiness") == "NOT_APPROVED_IN_28B"
        and plan.get("live_trading_readiness") == "NOT_APPROVED_IN_28B"
        and plan.get("production_strategy_improvement_claim") == "NOT_PROVEN_IN_28B"
        and plan.get("production_doctrine_revision") == "NOT_APPROVED_IN_28B"
    )
    ok = bool(items_ok and artifacts_ok and hash_ok and no_enablement_ok and boundary_ok)
    return {
        "ok": ok,
        "items_ok": items_ok,
        "artifacts_ok": artifacts_ok,
        "hash_ok": hash_ok,
        "no_enablement_ok": no_enablement_ok,
        "boundary_ok": boundary_ok,
    }


def _json_payload(schema_version: str, item: str, source: str | None, present: bool, copied_to: str | None) -> dict[str, Any]:
    return {
        "schema_version": schema_version,
        "item": item,
        "source": source,
        "present": present,
        "copied_to": copied_to,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
    }


def materialize_observe_only_live_evidence_contract(*, capture_id: str, root: str) -> dict[str, Any]:
    artifact_root = Path(root)
    assert_replay_artifact_path(str(artifact_root / "00_live_evidence_manifest.json"))
    artifact_root.mkdir(parents=True, exist_ok=True)

    plan = build_observe_only_live_evidence_capture_plan()
    validation = validate_observe_only_live_evidence_capture_plan(plan)

    payloads = {
        "00_live_evidence_manifest.json": plan,
        "01_provider_runtime.json": _json_payload("observe_only_provider_runtime_placeholder_v1", "provider_runtime", None, False, None),
        "02_feed_snapshot.json": _json_payload("observe_only_feed_snapshot_placeholder_v1", "feed_snapshot", None, False, None),
        "03_feature_payload.json": _json_payload("observe_only_feature_payload_placeholder_v1", "feature_payload", None, False, None),
        "04_family_surfaces.json": _json_payload("observe_only_family_surfaces_placeholder_v1", "family_surfaces", None, False, None),
        "05_strategy_activation.json": _json_payload("observe_only_strategy_activation_placeholder_v1", "strategy_activation", None, False, None),
        "06_no_order_sent.json": _json_payload("observe_only_no_order_sent_placeholder_v1", "no_order_sent", None, False, None),
        "07_live_stream_inventory.json": _json_payload("observe_only_live_stream_inventory_placeholder_v1", "live_stream_inventory", None, False, None),
        "08_live_hash_inventory.json": _json_payload("observe_only_live_hash_inventory_placeholder_v1", "live_hash_inventory", None, False, None),
        "09_provider_health_snapshot.json": _json_payload("observe_only_provider_health_snapshot_placeholder_v1", "provider_health_snapshot", None, False, None),
        "10_selected_option_context.json": _json_payload("observe_only_selected_option_context_placeholder_v1", "selected_option_context", None, False, None),
        "11_dhan_oi_ladder_context.json": _json_payload("observe_only_dhan_oi_ladder_context_placeholder_v1", "dhan_oi_ladder_context_if_available", None, False, None),
        "12_live_capture_log_reference.json": _json_payload("observe_only_live_capture_log_reference_placeholder_v1", "live_capture_log", None, False, None),
        "13_capture_completeness.json": {
            "schema_version": "observe_only_live_evidence_capture_completeness_v1",
            "capture_id": capture_id,
            "complete": False,
            "reason": "28B defines contract only; real observe_only evidence is not collected in this batch.",
            "required_evidence_items": OBSERVE_ONLY_REQUIRED_EVIDENCE_ITEMS,
            "present_items": tuple(),
            "missing_items": OBSERVE_ONLY_REQUIRED_EVIDENCE_ITEMS,
            "paper_armed_approved": False,
            "live_trading_approved": False,
            "production_doctrine_changed": False,
        },
        "14_no_enablement_boundary.json": {
            "schema_version": "observe_only_live_evidence_no_enablement_boundary_v1",
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
            "full_live_replay_parity": "NOT_PROVEN_IN_28B",
        },
        "15_capture_reproducibility.json": {
            "schema_version": "observe_only_live_evidence_capture_reproducibility_v1",
            "capture_id": capture_id,
            "plan_reproducibility_hash": plan["plan_reproducibility_hash"],
            "artifact_contract_hash": replay_fingerprint({
                "capture_id": capture_id,
                "required_artifacts": OBSERVE_ONLY_REQUIRED_ARTIFACTS,
                "required_evidence_items": OBSERVE_ONLY_REQUIRED_EVIDENCE_ITEMS,
            }),
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
        "schema_version": "observe_only_live_evidence_contract_materialization_v1",
        "capture_id": capture_id,
        "artifact_root": str(artifact_root),
        "required_artifacts": OBSERVE_ONLY_REQUIRED_ARTIFACTS,
        "written_artifacts": written,
        "written_count": len(written),
        "validation": validation,
        "accepted_for": "OBSERVE_ONLY_LIVE_EVIDENCE_CAPTURE_CONTRACT_ONLY",
        "contract_only": True,
        "actual_live_evidence_collected": False,
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
        "full_live_replay_parity": "NOT_PROVEN_IN_28B",
    }


def collect_observe_only_live_evidence_from_files(
    *,
    capture_id: str,
    root: str,
    evidence_paths: Mapping[str, str],
) -> dict[str, Any]:
    artifact_root = Path(root)
    assert_replay_artifact_path(str(artifact_root / "00_live_evidence_manifest.json"))
    evidence_dir = artifact_root / "evidence_files"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    copied = {}
    missing = {}
    for item in OBSERVE_ONLY_REQUIRED_EVIDENCE_ITEMS:
        raw_source = evidence_paths.get(item)
        if not raw_source:
            missing[item] = "not_provided"
            continue
        source = Path(raw_source)
        if not source.is_file():
            missing[item] = "missing_source_file"
            continue
        dest = evidence_dir / (item + source.suffix)
        shutil.copy2(source, dest)
        copied[item] = {"source": str(source), "copied_to": str(dest)}

    contract = materialize_observe_only_live_evidence_contract(capture_id=capture_id, root=root)

    completeness = {
        "schema_version": "observe_only_live_evidence_capture_completeness_v1",
        "capture_id": capture_id,
        "complete": len(missing) == 0,
        "present_items": tuple(copied.keys()),
        "missing_items": tuple(missing.keys()),
        "missing_reasons": missing,
        "copied": copied,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28B",
    }
    completeness_path = artifact_root / "13_capture_completeness.json"
    completeness_path.write_text(json.dumps(completeness, indent=2, sort_keys=True), encoding="utf-8")

    manifest_path = artifact_root / "00_live_evidence_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["actual_live_evidence_collected"] = len(copied) > 0
    manifest["copied_evidence_items"] = tuple(copied.keys())
    manifest["missing_evidence_items"] = tuple(missing.keys())
    manifest["capture_package_hash"] = replay_fingerprint({
        "capture_id": capture_id,
        "copied": copied,
        "missing": missing,
        "required_evidence_items": OBSERVE_ONLY_REQUIRED_EVIDENCE_ITEMS,
    })
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True, default=str), encoding="utf-8")

    return {
        "schema_version": "observe_only_live_evidence_collection_result_v1",
        "capture_id": capture_id,
        "artifact_root": str(artifact_root),
        "copied": copied,
        "missing": missing,
        "complete": len(missing) == 0,
        "contract": contract,
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
        "full_live_replay_parity": "NOT_PROVEN_IN_28B",
    }


def validate_materialized_observe_only_live_evidence_contract(result: Mapping[str, Any]) -> dict[str, Any]:
    root = Path(str(result.get("artifact_root")))
    written = dict(result.get("written_artifacts") or {})
    missing = tuple(name for name in OBSERVE_ONLY_REQUIRED_ARTIFACTS if name not in written or not Path(written[name]).is_file())
    root_ok = str(root).startswith("run/replay") or "/run/replay/" in str(root)
    count_ok = int(result.get("written_count", -1)) == len(OBSERVE_ONLY_REQUIRED_ARTIFACTS)
    validation_ok = dict(result.get("validation") or {}).get("ok") is True
    no_enablement_ok = (
        result.get("starts_services") is False
        and result.get("reads_live_redis") is False
        and result.get("writes_live_redis") is False
        and result.get("calls_broker_api") is False
        and result.get("paper_armed_approved") is False
        and result.get("live_trading_approved") is False
        and result.get("execution_arming_created") is False
        and result.get("real_order_sent") is False
        and result.get("broker_calls_executed") is False
        and result.get("live_redis_writes_executed") is False
        and result.get("production_doctrine_changed") is False
    )
    not_proven_ok = result.get("full_live_replay_parity") == "NOT_PROVEN_IN_28B"
    ok = bool(not missing and root_ok and count_ok and validation_ok and no_enablement_ok and not_proven_ok)
    return {
        "ok": ok,
        "missing": missing,
        "root_ok": root_ok,
        "count_ok": count_ok,
        "validation_ok": validation_ok,
        "no_enablement_ok": no_enablement_ok,
        "not_proven_ok": not_proven_ok,
    }


__all__ = tuple([
    "OBSERVE_ONLY_LIVE_EVIDENCE_CONTRACT_VERSION",
    "OBSERVE_ONLY_REQUIRED_EVIDENCE_ITEMS",
    "OBSERVE_ONLY_REQUIRED_ARTIFACTS",
    "OBSERVE_ONLY_EVIDENCE_DEFAULT_SOURCE_HINTS",
    "observe_only_live_evidence_contract_summary",
    "build_observe_only_live_evidence_capture_plan",
    "validate_observe_only_live_evidence_capture_plan",
    "materialize_observe_only_live_evidence_contract",
    "collect_observe_only_live_evidence_from_files",
    "validate_materialized_observe_only_live_evidence_contract",
])

# BEGIN BATCH28D_MARKET_SESSION_CAPTURE_RUNBOOK_LINK
def observe_only_market_session_capture_runbook_required_evidence():
    from app.mme_scalpx.replay.live_capture_runbook import REQUIRED_POST_SESSION_EVIDENCE
    return tuple(REQUIRED_POST_SESSION_EVIDENCE)
# END BATCH28D_MARKET_SESSION_CAPTURE_RUNBOOK_LINK
