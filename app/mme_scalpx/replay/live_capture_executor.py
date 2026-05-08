from __future__ import annotations

import json
from datetime import datetime, time, timezone
from pathlib import Path
from typing import Any, Mapping
from zoneinfo import ZoneInfo

from app.mme_scalpx.replay.integrity import replay_fingerprint
from app.mme_scalpx.replay.safety import assert_replay_artifact_path

OBSERVE_ONLY_MARKET_SESSION_CAPTURE_EXECUTION_VERSION = "observe_only_market_session_capture_execution_v1"
IST = ZoneInfo("Asia/Kolkata")

REQUIRED_EXECUTION_FLAGS = tuple([
    "execute",
    "confirm_observe_only",
    "evidence_map",
    "session_id",
    "output_root",
])

REQUIRED_CAPTURE_EVIDENCE_ITEMS = tuple([
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

REQUIRED_EXECUTION_ARTIFACTS = tuple([
    "00_execution_manifest.json",
    "01_market_session_gate.json",
    "02_execution_request.json",
    "03_evidence_map_validation.json",
    "04_no_enablement_boundary.json",
    "05_operator_command_result.json",
    "06_reproducibility.json",
])


def market_session_status(now_utc: datetime | None = None) -> dict[str, Any]:
    now = now_utc or datetime.now(timezone.utc)
    local = now.astimezone(IST)
    start = time(9, 15)
    end = time(15, 30)
    weekday_open = local.weekday() < 5
    time_open = start <= local.time() <= end
    return {
        "schema_version": "observe_only_market_session_status_v1",
        "now_utc": now.isoformat(),
        "now_ist": local.isoformat(),
        "weekday_open": weekday_open,
        "time_open": time_open,
        "holiday_calendar_verified": False,
        "market_session_open_by_time_rule": bool(weekday_open and time_open),
        "market_session_rule": "weekday and 09:15-15:30 IST only; holiday calendar is not verified by this local proof",
    }


def build_observe_only_market_session_capture_execution_plan() -> dict[str, Any]:
    status = market_session_status()
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
        "paper_armed_readiness": "NOT_APPROVED_IN_28E",
        "live_trading_readiness": "NOT_APPROVED_IN_28E",
        "production_strategy_improvement_claim": "NOT_PROVEN_IN_28E",
        "production_doctrine_revision": "NOT_APPROVED_IN_28E",
        "full_live_replay_parity": "NOT_PROVEN_IN_28E",
    }
    plan = {
        "schema_version": OBSERVE_ONLY_MARKET_SESSION_CAPTURE_EXECUTION_VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "accepted_for": "OBSERVE_ONLY_MARKET_SESSION_CAPTURE_EXECUTION_WRAPPER_ONLY",
        "purpose": "Market-session-gated observe_only evidence package execution wrapper.",
        "execute_in_28e": False,
        "actual_live_market_capture_in_28e": False,
        "future_execution_requires_market_session": True,
        "future_execution_requires_explicit_execute_flag": True,
        "future_execution_requires_confirm_observe_only": True,
        "future_execution_starts_services": False,
        "future_execution_reads_live_redis": False,
        "future_execution_writes_live_redis": False,
        "future_execution_calls_broker_api": False,
        "future_execution_only_packages_existing_evidence_files": True,
        "required_execution_flags": REQUIRED_EXECUTION_FLAGS,
        "required_capture_evidence_items": REQUIRED_CAPTURE_EVIDENCE_ITEMS,
        "required_execution_artifacts": REQUIRED_EXECUTION_ARTIFACTS,
        "market_session_status": status,
        "safety_boundary": safety,
        "not_approved_or_not_proven_boundary": boundary,
    }
    plan["execution_plan_hash"] = replay_fingerprint({
        "schema_version": plan["schema_version"],
        "required_execution_flags": plan["required_execution_flags"],
        "required_capture_evidence_items": plan["required_capture_evidence_items"],
        "required_execution_artifacts": plan["required_execution_artifacts"],
        "safety_boundary": plan["safety_boundary"],
        "boundary": plan["not_approved_or_not_proven_boundary"],
    })
    return plan


def validate_observe_only_market_session_capture_execution_plan(plan: Mapping[str, Any]) -> dict[str, Any]:
    safety = dict(plan.get("safety_boundary") or {})
    boundary = dict(plan.get("not_approved_or_not_proven_boundary") or {})
    ok = (
        plan.get("accepted_for") == "OBSERVE_ONLY_MARKET_SESSION_CAPTURE_EXECUTION_WRAPPER_ONLY"
        and plan.get("execute_in_28e") is False
        and plan.get("actual_live_market_capture_in_28e") is False
        and plan.get("future_execution_requires_market_session") is True
        and plan.get("future_execution_requires_explicit_execute_flag") is True
        and plan.get("future_execution_requires_confirm_observe_only") is True
        and plan.get("future_execution_starts_services") is False
        and plan.get("future_execution_reads_live_redis") is False
        and plan.get("future_execution_writes_live_redis") is False
        and plan.get("future_execution_calls_broker_api") is False
        and plan.get("future_execution_only_packages_existing_evidence_files") is True
        and tuple(plan.get("required_execution_flags") or ()) == REQUIRED_EXECUTION_FLAGS
        and tuple(plan.get("required_capture_evidence_items") or ()) == REQUIRED_CAPTURE_EVIDENCE_ITEMS
        and tuple(plan.get("required_execution_artifacts") or ()) == REQUIRED_EXECUTION_ARTIFACTS
        and safety.get("starts_services") is False
        and safety.get("reads_live_redis") is False
        and safety.get("writes_live_redis") is False
        and safety.get("calls_broker_api") is False
        and safety.get("paper_armed_approved") is False
        and safety.get("live_trading_approved") is False
        and safety.get("execution_arming_created") is False
        and safety.get("real_order_sent") is False
        and safety.get("broker_calls_executed") is False
        and safety.get("live_redis_writes_executed") is False
        and safety.get("production_doctrine_changed") is False
        and boundary.get("paper_armed_readiness") == "NOT_APPROVED_IN_28E"
        and boundary.get("live_trading_readiness") == "NOT_APPROVED_IN_28E"
        and boundary.get("full_live_replay_parity") == "NOT_PROVEN_IN_28E"
        and bool(plan.get("execution_plan_hash"))
    )
    return {"ok": bool(ok)}


def validate_evidence_map_file(path_text: str) -> dict[str, Any]:
    path = Path(path_text)
    if not path.is_file():
        return {"ok": False, "reason": "evidence_map_missing", "path": path_text}
    data = json.loads(path.read_text(encoding="utf-8"))
    missing_keys = tuple(item for item in REQUIRED_CAPTURE_EVIDENCE_ITEMS if item not in data)
    missing_files = tuple(
        {"item": item, "path": str(data.get(item))}
        for item in REQUIRED_CAPTURE_EVIDENCE_ITEMS
        if item in data and not Path(str(data.get(item))).is_file()
    )
    return {
        "ok": not missing_keys and not missing_files,
        "path": path_text,
        "missing_keys": missing_keys,
        "missing_files": missing_files,
        "item_count": len(data),
    }


def materialize_observe_only_market_session_capture_execution_plan(*, session_id: str, root: str) -> dict[str, Any]:
    artifact_root = Path(root)
    assert_replay_artifact_path(str(artifact_root / "00_execution_manifest.json"))
    artifact_root.mkdir(parents=True, exist_ok=True)

    plan = build_observe_only_market_session_capture_execution_plan()
    validation = validate_observe_only_market_session_capture_execution_plan(plan)

    payloads = {
        "00_execution_manifest.json": plan,
        "01_market_session_gate.json": plan["market_session_status"],
        "02_execution_request.json": {
            "schema_version": "observe_only_capture_execution_request_v1",
            "session_id": session_id,
            "execute_requested_in_28e": False,
            "future_execute_flag_required": True,
            "future_confirm_observe_only_required": True,
        },
        "03_evidence_map_validation.json": {
            "schema_version": "observe_only_capture_evidence_map_validation_placeholder_v1",
            "session_id": session_id,
            "validated_in_28e": False,
            "reason": "28E installs execution wrapper only; real evidence map validation happens when operator executes during market session.",
        },
        "04_no_enablement_boundary.json": plan["safety_boundary"] | {"full_live_replay_parity": "NOT_PROVEN_IN_28E"},
        "05_operator_command_result.json": {
            "schema_version": "observe_only_capture_operator_command_result_v1",
            "session_id": session_id,
            "command_executed_in_28e": False,
            "actual_live_market_capture": False,
        },
        "06_reproducibility.json": {
            "schema_version": "observe_only_capture_execution_reproducibility_v1",
            "session_id": session_id,
            "execution_plan_hash": plan["execution_plan_hash"],
            "artifact_hash": replay_fingerprint({
                "session_id": session_id,
                "required_execution_artifacts": REQUIRED_EXECUTION_ARTIFACTS,
                "required_capture_evidence_items": REQUIRED_CAPTURE_EVIDENCE_ITEMS,
            }),
        },
    }

    written = {}
    for name, payload in payloads.items():
        path = artifact_root / name
        path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
        written[name] = str(path)

    return {
        "schema_version": "observe_only_capture_execution_plan_materialization_v1",
        "session_id": session_id,
        "artifact_root": str(artifact_root),
        "written_artifacts": written,
        "written_count": len(written),
        "required_execution_artifacts": REQUIRED_EXECUTION_ARTIFACTS,
        "validation": validation,
        "accepted_for": "OBSERVE_ONLY_MARKET_SESSION_CAPTURE_EXECUTION_WRAPPER_ONLY",
        "execute_in_28e": False,
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
        "full_live_replay_parity": "NOT_PROVEN_IN_28E",
    }


def validate_materialized_observe_only_market_session_capture_execution_plan(result: Mapping[str, Any]) -> dict[str, Any]:
    root = Path(str(result.get("artifact_root")))
    written = dict(result.get("written_artifacts") or {})
    missing = tuple(
        name for name in REQUIRED_EXECUTION_ARTIFACTS
        if name not in written or not Path(written[name]).is_file()
    )
    ok = (
        not missing
        and (str(root).startswith("run/replay") or "/run/replay/" in str(root))
        and int(result.get("written_count", -1)) == len(REQUIRED_EXECUTION_ARTIFACTS)
        and dict(result.get("validation") or {}).get("ok") is True
        and result.get("execute_in_28e") is False
        and result.get("actual_live_market_capture") is False
        and result.get("starts_services") is False
        and result.get("reads_live_redis") is False
        and result.get("writes_live_redis") is False
        and result.get("calls_broker_api") is False
        and result.get("paper_armed_approved") is False
        and result.get("live_trading_approved") is False
        and result.get("real_order_sent") is False
        and result.get("production_doctrine_changed") is False
        and result.get("full_live_replay_parity") == "NOT_PROVEN_IN_28E"
    )
    return {"ok": bool(ok), "missing": missing}


def execute_observe_only_market_session_capture_package(
    *,
    session_id: str,
    root: str,
    evidence_map: str,
    execute: bool,
    confirm_observe_only: bool,
) -> dict[str, Any]:
    status = market_session_status()
    if not execute:
        return materialize_observe_only_market_session_capture_execution_plan(session_id=session_id, root=root)
    if not confirm_observe_only:
        raise RuntimeError("confirm_observe_only flag is required")
    if not status.get("market_session_open_by_time_rule"):
        raise RuntimeError("market session time gate is closed")
    validation = validate_evidence_map_file(evidence_map)
    if not validation.get("ok"):
        raise RuntimeError("evidence map validation failed: " + json.dumps(validation, sort_keys=True))

    from app.mme_scalpx.replay.live_evidence import collect_observe_only_live_evidence_from_files

    evidence_data = json.loads(Path(evidence_map).read_text(encoding="utf-8"))
    return collect_observe_only_live_evidence_from_files(
        capture_id=session_id,
        root=root,
        evidence_paths={str(k): str(v) for k, v in evidence_data.items()},
    )


__all__ = tuple([
    "OBSERVE_ONLY_MARKET_SESSION_CAPTURE_EXECUTION_VERSION",
    "REQUIRED_EXECUTION_FLAGS",
    "REQUIRED_CAPTURE_EVIDENCE_ITEMS",
    "REQUIRED_EXECUTION_ARTIFACTS",
    "market_session_status",
    "build_observe_only_market_session_capture_execution_plan",
    "validate_observe_only_market_session_capture_execution_plan",
    "validate_evidence_map_file",
    "materialize_observe_only_market_session_capture_execution_plan",
    "validate_materialized_observe_only_market_session_capture_execution_plan",
    "execute_observe_only_market_session_capture_package",
])
