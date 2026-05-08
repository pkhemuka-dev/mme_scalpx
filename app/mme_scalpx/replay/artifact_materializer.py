from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from app.mme_scalpx.replay.integrity import replay_fingerprint
from app.mme_scalpx.replay.safety import assert_replay_artifact_path


REPLAY_ARTIFACT_MATERIALIZER_CONTRACT_VERSION = "replay_artifact_materializer_v1"

REPLAY_BATCH_REQUIRED_ARTIFACTS = (
    "00_manifest.json",
    "01_dataset_summary.json",
    "02_scenario_summary.json",
    "03_feature_summary.json",
    "04_strategy_summary.json",
    "05_risk_summary.json",
    "06_execution_shadow_summary.json",
    "07_reproducibility.json",
    "08_batch_summary.json",
)


def _json_ready(value: Any) -> Any:
    return json.loads(json.dumps(value, sort_keys=True, default=str))


def _write_json(path: Path, payload: Mapping[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_json_ready(payload), indent=2, sort_keys=True), encoding="utf-8")
    return str(path)


def build_replay_reproducibility_hash(
    *,
    plan: Mapping[str, Any],
    simulation_result: Mapping[str, Any],
) -> str:
    payload = {
        "plan_schema_version": plan.get("schema_version"),
        "plan_id": plan.get("plan_id"),
        "scope": plan.get("scope"),
        "request_count": plan.get("request_count"),
        "requests": plan.get("requests"),
        "result_schema_version": simulation_result.get("schema_version"),
        "result_count": simulation_result.get("result_count"),
        "scenario_ids": simulation_result.get("scenario_ids"),
        "total_shadow_pnl": simulation_result.get("total_shadow_pnl"),
        "results": simulation_result.get("results"),
    }
    return replay_fingerprint(payload)


def build_replay_artifact_payloads(
    *,
    run_id: str,
    plan: Mapping[str, Any],
    simulation_result: Mapping[str, Any],
    artifact_root: str,
) -> dict[str, dict[str, Any]]:
    results = tuple(simulation_result.get("results") or ())
    scenario_ids = tuple(sorted({str(r.get("scenario_id")) for r in results if r.get("scenario_id")}))
    reproducibility_hash = build_replay_reproducibility_hash(plan=plan, simulation_result=simulation_result)

    dataset_summary = {
        "schema_version": "replay_dataset_summary_artifact_v1",
        "run_id": run_id,
        "scope": plan.get("scope"),
        "request_count": plan.get("request_count"),
        "result_count": len(results),
        "dates": tuple(sorted({str(r.get("date")) for r in results if r.get("date")})),
        "intraday_windows": tuple(sorted({
            f"{r.get('start_time')}->{r.get('end_time')}"
            for r in results
            if r.get("start_time") or r.get("end_time")
        })),
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "production_doctrine_changed": False,
    }

    scenario_summary = {
        "schema_version": "replay_scenario_summary_artifact_v1",
        "run_id": run_id,
        "scenario_count": len(scenario_ids),
        "scenario_ids": scenario_ids,
        "scenario_result_count": sum(1 for r in results if r.get("scenario_id")),
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "production_doctrine_changed": False,
    }

    feature_summary = {
        "schema_version": "replay_feature_summary_artifact_v1",
        "run_id": run_id,
        "family_features_json_present_count": sum(1 for r in results if r.get("feature_summary", {}).get("family_features_json_present")),
        "family_surfaces_json_present_count": sum(1 for r in results if r.get("feature_summary", {}).get("family_surfaces_json_present")),
        "provider_ready_miso_true_count": sum(1 for r in results if r.get("feature_summary", {}).get("provider_ready_miso") is True),
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "production_doctrine_changed": False,
    }

    strategy_summary = {
        "schema_version": "replay_strategy_summary_artifact_v1",
        "run_id": run_id,
        "decision_count": len(results),
        "hold_report_only_count": sum(1 for r in results if r.get("strategy_summary", {}).get("final_action") == "HOLD_REPORT_ONLY"),
        "order_allowed_true_count": sum(1 for r in results if r.get("strategy_summary", {}).get("order_allowed") is True),
        "candidate_count_total": sum(int(r.get("strategy_summary", {}).get("candidate_count") or 0) for r in results),
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "production_doctrine_changed": False,
    }

    risk_summary = {
        "schema_version": "replay_risk_summary_artifact_v1",
        "run_id": run_id,
        "risk_evaluated_count": sum(1 for r in results if r.get("risk_summary", {}).get("risk_evaluated") is True),
        "entry_vetoed_count": sum(1 for r in results if r.get("risk_summary", {}).get("entry_vetoed") is True),
        "research_trade_allowed_count": sum(1 for r in results if r.get("risk_summary", {}).get("research_trade_allowed") is True),
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "production_doctrine_changed": False,
    }

    execution_summary = {
        "schema_version": "replay_execution_shadow_summary_artifact_v1",
        "run_id": run_id,
        "execution_shadow_count": len(results),
        "filled_qty_total": sum(int(r.get("execution_shadow_summary", {}).get("filled_qty") or 0) for r in results),
        "net_pnl_total": sum(float(r.get("execution_shadow_summary", {}).get("net_pnl") or 0.0) for r in results),
        "real_order_sent_count": sum(1 for r in results if r.get("execution_shadow_summary", {}).get("real_order_sent") is True),
        "broker_calls_executed_count": sum(1 for r in results if r.get("execution_shadow_summary", {}).get("broker_calls_executed") is True),
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "production_doctrine_changed": False,
    }

    reproducibility = {
        "schema_version": "replay_reproducibility_artifact_v1",
        "run_id": run_id,
        "reproducibility_hash": reproducibility_hash,
        "plan_fingerprint": replay_fingerprint(plan),
        "simulation_fingerprint": replay_fingerprint(simulation_result),
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "production_doctrine_changed": False,
    }

    batch_summary = {
        "schema_version": "replay_batch_summary_artifact_v1",
        "run_id": run_id,
        "scope": plan.get("scope"),
        "request_count": plan.get("request_count"),
        "result_count": simulation_result.get("result_count"),
        "scenario_count": simulation_result.get("scenario_count"),
        "total_shadow_pnl": simulation_result.get("total_shadow_pnl"),
        "artifact_root": artifact_root,
        "reproducibility_hash": reproducibility_hash,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
    }

    manifest = {
        "schema_version": REPLAY_ARTIFACT_MATERIALIZER_CONTRACT_VERSION,
        "run_id": run_id,
        "artifact_root": artifact_root,
        "materialized_at_utc": datetime.now(timezone.utc).isoformat(),
        "required_artifacts": REPLAY_BATCH_REQUIRED_ARTIFACTS,
        "reproducibility_hash": reproducibility_hash,
        "plan": plan,
        # Batch 27K-R1: expose safety flags at top-level too, because
        # artifact verification treats every artifact uniformly.
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "safety": {
            "paper_armed_approved": False,
            "live_trading_approved": False,
            "execution_arming_created": False,
            "real_order_sent": False,
            "broker_calls_executed": False,
            "live_redis_writes_executed": False,
            "production_doctrine_changed": False,
        },
    }

    return {
        "00_manifest.json": manifest,
        "01_dataset_summary.json": dataset_summary,
        "02_scenario_summary.json": scenario_summary,
        "03_feature_summary.json": feature_summary,
        "04_strategy_summary.json": strategy_summary,
        "05_risk_summary.json": risk_summary,
        "06_execution_shadow_summary.json": execution_summary,
        "07_reproducibility.json": reproducibility,
        "08_batch_summary.json": batch_summary,
    }


def materialize_replay_run_artifacts(
    *,
    run_id: str,
    plan: Mapping[str, Any],
    simulation_result: Mapping[str, Any],
    base_dir: str = "run/replay",
) -> dict[str, Any]:
    run_root = Path(base_dir) / str(run_id)
    assert_replay_artifact_path(str(run_root / "00_manifest.json"))
    run_root.mkdir(parents=True, exist_ok=True)

    payloads = build_replay_artifact_payloads(
        run_id=str(run_id),
        plan=plan,
        simulation_result=simulation_result,
        artifact_root=str(run_root),
    )

    written = {
        name: _write_json(run_root / name, payload)
        for name, payload in payloads.items()
    }

    return {
        "schema_version": "replay_artifact_materialization_result_v1",
        "run_id": str(run_id),
        "artifact_root": str(run_root),
        "required_artifacts": REPLAY_BATCH_REQUIRED_ARTIFACTS,
        "written_artifacts": written,
        "written_count": len(written),
        "reproducibility_hash": payloads["07_reproducibility.json"]["reproducibility_hash"],
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
    }


def validate_replay_artifact_materialization(result: Mapping[str, Any]) -> dict[str, Any]:
    root = Path(str(result.get("artifact_root")))
    written = dict(result.get("written_artifacts") or {})
    missing = tuple(name for name in REPLAY_BATCH_REQUIRED_ARTIFACTS if name not in written or not Path(written[name]).exists())
    root_ok = str(root).startswith("run/replay") or "/run/replay/" in str(root)
    count_ok = int(result.get("written_count", -1)) == len(REPLAY_BATCH_REQUIRED_ARTIFACTS)
    reproducibility_ok = bool(result.get("reproducibility_hash"))
    no_live_ok = (
        result.get("paper_armed_approved") is False
        and result.get("live_trading_approved") is False
        and result.get("execution_arming_created") is False
        and result.get("real_order_sent") is False
        and result.get("broker_calls_executed") is False
        and result.get("live_redis_writes_executed") is False
        and result.get("production_doctrine_changed") is False
    )
    ok = bool(not missing and root_ok and count_ok and reproducibility_ok and no_live_ok)
    return {
        "ok": ok,
        "missing": missing,
        "root_ok": root_ok,
        "count_ok": count_ok,
        "reproducibility_ok": reproducibility_ok,
        "no_live_ok": no_live_ok,
    }


def replay_artifact_materializer_contract_summary() -> dict[str, Any]:
    return {
        "schema_version": REPLAY_ARTIFACT_MATERIALIZER_CONTRACT_VERSION,
        "required_artifacts": REPLAY_BATCH_REQUIRED_ARTIFACTS,
        "artifact_root": "run/replay/",
        "artifact_materialization": "PROVEN_BY_27K",
        "reproducibility_hash": "PROVEN_BY_27K",
        "full_live_replay_parity": "NOT_PROVEN_IN_27K",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "broker_calls_allowed": False,
        "live_redis_writes_allowed": False,
        "production_doctrine_changed": False,
    }


try:
    __all__
except NameError:
    __all__ = tuple()

__all__ = tuple(dict.fromkeys(tuple(__all__) + (
    "REPLAY_ARTIFACT_MATERIALIZER_CONTRACT_VERSION",
    "REPLAY_BATCH_REQUIRED_ARTIFACTS",
    "build_replay_reproducibility_hash",
    "build_replay_artifact_payloads",
    "materialize_replay_run_artifacts",
    "validate_replay_artifact_materialization",
    "replay_artifact_materializer_contract_summary",
)))
