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

from app.mme_scalpx.replay.live_parity import (
    REPLAY_LIVE_PARITY_REQUIRED_ARTIFACTS,
    build_replay_live_parity_audit_plan,
    materialize_replay_live_parity_audit_plan,
    replay_live_parity_audit_plan_summary,
    validate_materialized_replay_live_parity_plan,
    validate_replay_live_parity_audit_plan,
)


def read_json(path: Path) -> dict:
    if not path.exists():
        return {"missing": True}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_replay_live_parity_audit_plan.json")
    args = parser.parse_args()

    contract_path = ROOT / "etc/replay/schemas/replay_live_parity_audit_plan_contract_v1.json"
    plan_path = ROOT / "etc/replay/parity/live_parity_audit_plan_v1.json"

    contract = read_json(contract_path)
    static_plan = read_json(plan_path)

    runtime_plan = build_replay_live_parity_audit_plan()
    runtime_validation = validate_replay_live_parity_audit_plan(runtime_plan)

    result = materialize_replay_live_parity_audit_plan(
        run_id="batch28a_replay_live_parity_plan",
        root="run/replay/parity/batch28a_replay_live_parity_plan",
    )
    materialized_validation = validate_materialized_replay_live_parity_plan(result)
    artifact_root = Path(result["artifact_root"])

    contract_ok = (
        contract_path.exists()
        and contract.get("schema_version") == "replay_live_parity_audit_plan_contract_v1"
        and contract.get("paper_armed_approved") is False
        and contract.get("live_trading_approved") is False
        and contract.get("production_doctrine_changed") is False
        and contract.get("expected_28a_verdict") == "PASS_REPLAY_LIVE_PARITY_AUDIT_PLAN"
    )

    static_plan_ok = (
        plan_path.exists()
        and static_plan.get("schema_version") == "replay_live_parity_audit_plan_v1"
        and static_plan.get("not_proven_boundary", {}).get("full_live_replay_parity") == "NOT_PROVEN_IN_28A"
        and static_plan.get("paper_armed_approved") is False
        and static_plan.get("live_trading_approved") is False
    )

    required_artifacts_ok = all((artifact_root / name).is_file() for name in REPLAY_LIVE_PARITY_REQUIRED_ARTIFACTS)

    summary = replay_live_parity_audit_plan_summary()
    summary_ok = (
        summary.get("full_live_replay_parity") == "NOT_PROVEN_IN_28A"
        and summary.get("paper_armed_readiness") == "NOT_APPROVED_IN_28A"
        and summary.get("live_trading_readiness") == "NOT_APPROVED_IN_28A"
        and summary.get("paper_armed_approved") is False
        and summary.get("live_trading_approved") is False
    )

    ok = bool(
        contract_ok
        and static_plan_ok
        and runtime_validation.get("ok") is True
        and materialized_validation.get("ok") is True
        and required_artifacts_ok
        and summary_ok
    )

    proof = {
        "schema_version": "proof_replay_live_parity_audit_plan_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "replay_live_parity_audit_plan_ok": ok,
        "contract_ok": contract_ok,
        "static_plan_ok": static_plan_ok,
        "runtime_validation_ok": runtime_validation.get("ok"),
        "materialized_validation_ok": materialized_validation.get("ok"),
        "required_artifacts_ok": required_artifacts_ok,
        "summary_ok": summary_ok,
        "artifact_root": str(artifact_root),
        "runtime_validation": runtime_validation,
        "materialized_validation": materialized_validation,
        "accepted_for": "PARITY_AUDIT_PLAN_ONLY",
        "full_live_replay_parity": "NOT_PROVEN_IN_28A",
        "paper_armed_readiness": "NOT_APPROVED_IN_28A",
        "live_trading_readiness": "NOT_APPROVED_IN_28A",
        "production_strategy_improvement_claim": "NOT_PROVEN_IN_28A",
        "production_doctrine_revision": "NOT_APPROVED_IN_28A",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "verdict": "PASS_REPLAY_LIVE_PARITY_AUDIT_PLAN" if ok else "FAIL_REVIEW_REQUIRED",
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True, default=str), encoding="utf-8")

    print(json.dumps({
        "proof": str(out),
        "verdict": proof["verdict"],
        "replay_live_parity_audit_plan_ok": ok,
        "contract_ok": contract_ok,
        "static_plan_ok": static_plan_ok,
        "runtime_validation_ok": runtime_validation.get("ok"),
        "materialized_validation_ok": materialized_validation.get("ok"),
        "required_artifacts_ok": required_artifacts_ok,
        "accepted_for": proof["accepted_for"],
        "full_live_replay_parity": proof["full_live_replay_parity"],
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "artifact_root": str(artifact_root),
    }, indent=2, sort_keys=True))

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
