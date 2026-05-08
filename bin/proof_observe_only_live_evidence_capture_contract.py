#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.mme_scalpx.replay.live_evidence import (
    OBSERVE_ONLY_REQUIRED_ARTIFACTS,
    build_observe_only_live_evidence_capture_plan,
    materialize_observe_only_live_evidence_contract,
    observe_only_live_evidence_contract_summary,
    validate_materialized_observe_only_live_evidence_contract,
    validate_observe_only_live_evidence_capture_plan,
)


def load_json(path: Path) -> dict:
    if not path.exists():
        return {"missing": True}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_observe_only_live_evidence_capture_contract.json")
    args = parser.parse_args()

    schema_path = ROOT / "etc/replay/schemas/observe_only_live_evidence_capture_contract_v1.json"
    plan_path = ROOT / "etc/replay/parity/observe_only_live_evidence_capture_contract_v1.json"

    schema = load_json(schema_path)
    static_plan = load_json(plan_path)

    runtime_plan = build_observe_only_live_evidence_capture_plan()
    runtime_validation = validate_observe_only_live_evidence_capture_plan(runtime_plan)

    materialized = materialize_observe_only_live_evidence_contract(
        capture_id="batch28b_contract_only",
        root="run/replay/parity/live_evidence/batch28b_contract_only",
    )
    materialized_validation = validate_materialized_observe_only_live_evidence_contract(materialized)

    artifact_root = Path(materialized["artifact_root"])
    required_artifacts_ok = all((artifact_root / name).is_file() for name in OBSERVE_ONLY_REQUIRED_ARTIFACTS)

    schema_ok = (
        schema_path.exists()
        and schema.get("schema_version") == "observe_only_live_evidence_capture_contract_v1"
        and schema.get("accepted_for") == "OBSERVE_ONLY_LIVE_EVIDENCE_CAPTURE_CONTRACT_ONLY"
        and schema.get("starts_services") is False
        and schema.get("reads_live_redis") is False
        and schema.get("writes_live_redis") is False
        and schema.get("calls_broker_api") is False
        and schema.get("paper_armed_approved") is False
        and schema.get("live_trading_approved") is False
        and schema.get("expected_28b_verdict") == "PASS_OBSERVE_ONLY_LIVE_EVIDENCE_CAPTURE_CONTRACT_28B"
    )

    static_plan_ok = (
        plan_path.exists()
        and static_plan.get("schema_version") == "observe_only_live_evidence_capture_contract_v1"
        and static_plan.get("accepted_for") == "OBSERVE_ONLY_LIVE_EVIDENCE_CAPTURE_CONTRACT_ONLY"
        and static_plan.get("starts_services") is False
        and static_plan.get("reads_live_redis") is False
        and static_plan.get("writes_live_redis") is False
        and static_plan.get("calls_broker_api") is False
        and static_plan.get("paper_armed_approved") is False
        and static_plan.get("live_trading_approved") is False
        and static_plan.get("full_live_replay_parity") == "NOT_PROVEN_IN_28B"
    )

    summary = observe_only_live_evidence_contract_summary()
    summary_ok = (
        summary.get("accepted_for") == "OBSERVE_ONLY_LIVE_EVIDENCE_CAPTURE_CONTRACT_ONLY"
        and summary.get("starts_services") is False
        and summary.get("reads_live_redis") is False
        and summary.get("writes_live_redis") is False
        and summary.get("calls_broker_api") is False
        and summary.get("paper_armed_approved") is False
        and summary.get("live_trading_approved") is False
        and summary.get("full_live_replay_parity") == "NOT_PROVEN_IN_28B"
    )

    ok = bool(
        schema_ok
        and static_plan_ok
        and runtime_validation.get("ok") is True
        and materialized_validation.get("ok") is True
        and required_artifacts_ok
        and summary_ok
    )

    proof = {
        "schema_version": "proof_observe_only_live_evidence_capture_contract_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "observe_only_live_evidence_capture_contract_ok": ok,
        "schema_ok": schema_ok,
        "static_plan_ok": static_plan_ok,
        "runtime_validation_ok": runtime_validation.get("ok"),
        "materialized_validation_ok": materialized_validation.get("ok"),
        "required_artifacts_ok": required_artifacts_ok,
        "summary_ok": summary_ok,
        "artifact_root": str(artifact_root),
        "runtime_validation": runtime_validation,
        "materialized_validation": materialized_validation,
        "accepted_for": "OBSERVE_ONLY_LIVE_EVIDENCE_CAPTURE_CONTRACT_ONLY",
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
        "paper_armed_readiness": "NOT_APPROVED_IN_28B",
        "live_trading_readiness": "NOT_APPROVED_IN_28B",
        "production_strategy_improvement_claim": "NOT_PROVEN_IN_28B",
        "production_doctrine_revision": "NOT_APPROVED_IN_28B",
        "full_live_replay_parity": "NOT_PROVEN_IN_28B",
        "verdict": "PASS_OBSERVE_ONLY_LIVE_EVIDENCE_CAPTURE_CONTRACT" if ok else "FAIL_REVIEW_REQUIRED",
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True, default=str), encoding="utf-8")

    print(json.dumps({
        "proof": str(out),
        "verdict": proof["verdict"],
        "observe_only_live_evidence_capture_contract_ok": ok,
        "schema_ok": schema_ok,
        "static_plan_ok": static_plan_ok,
        "runtime_validation_ok": runtime_validation.get("ok"),
        "materialized_validation_ok": materialized_validation.get("ok"),
        "required_artifacts_ok": required_artifacts_ok,
        "artifact_root": str(artifact_root),
        "accepted_for": proof["accepted_for"],
        "actual_live_evidence_collected": False,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28B",
    }, indent=2, sort_keys=True))

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
