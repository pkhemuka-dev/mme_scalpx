from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from app.mme_scalpx.replay.integrity import replay_fingerprint

OBSERVE_ONLY_ACTUAL_EVIDENCE_MAP_GENERATION_VERSION = "observe_only_actual_evidence_map_generation_v1"

REQUIRED_EVIDENCE_ITEMS = tuple([
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

DEFAULT_SOURCE_CANDIDATES = {
    "provider_runtime": tuple(["run/proofs/proof_market_session_provider_runtime.json"]),
    "feed_snapshot": tuple(["run/proofs/proof_market_session_feed_snapshot.json"]),
    "feature_payload": tuple(["run/proofs/proof_market_session_feature_payload.json"]),
    "family_surfaces": tuple(["run/proofs/proof_market_session_family_surfaces.json"]),
    "strategy_activation": tuple(["run/proofs/proof_market_session_strategy_activation.json"]),
    "no_order_sent": tuple(["run/proofs/proof_market_session_no_order_sent.json"]),
    "live_stream_inventory": tuple(["run/proofs/proof_market_session_live_stream_inventory.json"]),
    "live_hash_inventory": tuple(["run/proofs/proof_market_session_live_hash_inventory.json"]),
    "provider_health_snapshot": tuple(["run/proofs/proof_market_session_provider_health_snapshot.json"]),
    "selected_option_context": tuple(["run/proofs/proof_market_session_selected_option_context.json"]),
    "dhan_oi_ladder_context_if_available": tuple([
        "run/proofs/proof_market_session_dhan_oi_ladder_context.json",
        "run/proofs/proof_market_session_dhan_oi_ladder_context_if_available.json",
    ]),
}


def latest_live_capture_log() -> str | None:
    candidates = sorted(Path("run/live_capture").glob("*.log"))
    if not candidates:
        return None
    return str(candidates[-1])


def build_actual_evidence_map_generation_contract() -> dict[str, Any]:
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
        "paper_armed_readiness": "NOT_APPROVED_IN_28G",
        "live_trading_readiness": "NOT_APPROVED_IN_28G",
        "production_strategy_improvement_claim": "NOT_PROVEN_IN_28G",
        "production_doctrine_revision": "NOT_APPROVED_IN_28G",
        "full_live_replay_parity": "NOT_PROVEN_IN_28G",
    }
    contract = {
        "schema_version": OBSERVE_ONLY_ACTUAL_EVIDENCE_MAP_GENERATION_VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "accepted_for": "OBSERVE_ONLY_ACTUAL_EVIDENCE_MAP_GENERATION_ONLY",
        "generates_candidate_map": True,
        "publishes_final_map_only_when_complete": True,
        "required_evidence_items": REQUIRED_EVIDENCE_ITEMS,
        "default_source_candidates": DEFAULT_SOURCE_CANDIDATES,
        "safety_boundary": safety,
        "not_approved_or_not_proven_boundary": boundary,
    }
    contract["contract_hash"] = replay_fingerprint({
        "schema_version": contract["schema_version"],
        "required_evidence_items": contract["required_evidence_items"],
        "default_source_candidates": contract["default_source_candidates"],
        "safety_boundary": safety,
        "boundary": boundary,
    })
    return contract


def discover_actual_evidence_map() -> dict[str, Any]:
    evidence = {}
    missing = {}
    candidate_details = {}

    for item in REQUIRED_EVIDENCE_ITEMS:
        candidates = list(DEFAULT_SOURCE_CANDIDATES.get(item, tuple()))
        if item == "live_capture_log":
            latest_log = latest_live_capture_log()
            if latest_log:
                candidates.append(latest_log)

        candidate_details[item] = candidates
        selected = None
        for raw in candidates:
            if raw and Path(raw).is_file():
                selected = raw
                break

        if selected:
            evidence[item] = selected
        else:
            missing[item] = candidates

    complete = not missing
    return {
        "schema_version": "observe_only_actual_evidence_map_discovery_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "complete": complete,
        "evidence": evidence,
        "missing": missing,
        "candidate_details": candidate_details,
        "required_count": len(REQUIRED_EVIDENCE_ITEMS),
        "found_count": len(evidence),
        "missing_count": len(missing),
        "safety_boundary": build_actual_evidence_map_generation_contract()["safety_boundary"],
        "not_approved_or_not_proven_boundary": build_actual_evidence_map_generation_contract()["not_approved_or_not_proven_boundary"],
    }


def write_actual_evidence_maps(*, candidate_path: str, final_path: str, missing_report_path: str) -> dict[str, Any]:
    discovery = discover_actual_evidence_map()
    candidate = {
        "schema_version": "observe_only_actual_generated_evidence_map_candidate_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "complete": discovery["complete"],
        "evidence": discovery["evidence"],
        "missing": discovery["missing"],
        "found_count": discovery["found_count"],
        "missing_count": discovery["missing_count"],
    }

    Path(candidate_path).parent.mkdir(parents=True, exist_ok=True)
    Path(candidate_path).write_text(json.dumps(candidate, indent=2, sort_keys=True), encoding="utf-8")

    missing_report = {
        "schema_version": "observe_only_actual_evidence_map_missing_report_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "complete": discovery["complete"],
        "missing": discovery["missing"],
        "candidate_details": discovery["candidate_details"],
        "final_map_published": False,
    }

    if discovery["complete"]:
        final = {item: discovery["evidence"][item] for item in REQUIRED_EVIDENCE_ITEMS}
        Path(final_path).parent.mkdir(parents=True, exist_ok=True)
        Path(final_path).write_text(json.dumps(final, indent=2, sort_keys=True), encoding="utf-8")
        missing_report["final_map_published"] = True
    else:
        final_file = Path(final_path)
        if final_file.exists():
            final_file.unlink()
        missing_report["final_map_published"] = False

    Path(missing_report_path).parent.mkdir(parents=True, exist_ok=True)
    Path(missing_report_path).write_text(json.dumps(missing_report, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "schema_version": "observe_only_actual_evidence_map_write_result_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "candidate_path": candidate_path,
        "final_path": final_path,
        "missing_report_path": missing_report_path,
        "complete": discovery["complete"],
        "final_map_published": bool(discovery["complete"]),
        "found_count": discovery["found_count"],
        "missing_count": discovery["missing_count"],
        "missing": discovery["missing"],
        "evidence": discovery["evidence"],
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
        "full_live_replay_parity": "NOT_PROVEN_IN_28G",
    }


def validate_actual_evidence_map_generation_result(result: Mapping[str, Any]) -> dict[str, Any]:
    candidate_ok = Path(str(result.get("candidate_path"))).is_file()
    missing_report_ok = Path(str(result.get("missing_report_path"))).is_file()
    complete = result.get("complete") is True
    final_ok = Path(str(result.get("final_path"))).is_file() if complete else not Path(str(result.get("final_path"))).exists()
    safety_ok = (
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
        and result.get("full_live_replay_parity") == "NOT_PROVEN_IN_28G"
    )
    return {
        "ok": bool(candidate_ok and missing_report_ok and final_ok and safety_ok),
        "candidate_ok": candidate_ok,
        "missing_report_ok": missing_report_ok,
        "final_ok": final_ok,
        "complete": complete,
        "safety_ok": safety_ok,
    }


__all__ = tuple([
    "OBSERVE_ONLY_ACTUAL_EVIDENCE_MAP_GENERATION_VERSION",
    "REQUIRED_EVIDENCE_ITEMS",
    "DEFAULT_SOURCE_CANDIDATES",
    "latest_live_capture_log",
    "build_actual_evidence_map_generation_contract",
    "discover_actual_evidence_map",
    "write_actual_evidence_maps",
    "validate_actual_evidence_map_generation_result",
])
