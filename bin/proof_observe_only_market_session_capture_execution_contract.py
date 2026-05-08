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

from app.mme_scalpx.replay.live_capture_executor import (
    REQUIRED_EXECUTION_ARTIFACTS,
    build_observe_only_market_session_capture_execution_plan,
    materialize_observe_only_market_session_capture_execution_plan,
    validate_materialized_observe_only_market_session_capture_execution_plan,
    validate_observe_only_market_session_capture_execution_plan,
)


def load_json(path: Path) -> dict:
    if not path.exists():
        return {"missing": True}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_observe_only_market_session_capture_execution_contract.json")
    args = parser.parse_args()

    schema = load_json(Path("etc/replay/schemas/observe_only_market_session_capture_execution_contract_v1.json"))
    static_plan = load_json(Path("etc/replay/parity/observe_only_market_session_capture_execution_plan_v1.json"))
    proof28d = load_json(Path("run/proofs/proof_observe_only_market_session_capture_28d_latest.json"))

    plan = build_observe_only_market_session_capture_execution_plan()
    runtime_validation = validate_observe_only_market_session_capture_execution_plan(plan)

    result = materialize_observe_only_market_session_capture_execution_plan(
        session_id="batch28e_capture_execution_plan",
        root="run/replay/parity/live_session_operator/batch28e_capture_execution_plan",
    )
    materialized_validation = validate_materialized_observe_only_market_session_capture_execution_plan(result)

    root = Path(result["artifact_root"])
    artifacts_ok = all((root / name).is_file() for name in REQUIRED_EXECUTION_ARTIFACTS)

    schema_ok = (
        schema.get("accepted_for") == "OBSERVE_ONLY_MARKET_SESSION_CAPTURE_EXECUTION_WRAPPER_ONLY"
        and schema.get("execute_in_28e") is False
        and schema.get("actual_live_market_capture_in_28e") is False
        and schema.get("future_execution_requires_market_session") is True
        and schema.get("future_execution_requires_explicit_execute_flag") is True
        and schema.get("future_execution_requires_confirm_observe_only") is True
        and schema.get("future_execution_starts_services") is False
        and schema.get("future_execution_reads_live_redis") is False
        and schema.get("future_execution_writes_live_redis") is False
        and schema.get("future_execution_calls_broker_api") is False
        and schema.get("paper_armed_approved") is False
        and schema.get("live_trading_approved") is False
        and schema.get("full_live_replay_parity") == "NOT_PROVEN_IN_28E"
    )
    static_plan_ok = (
        static_plan.get("accepted_for") == "OBSERVE_ONLY_MARKET_SESSION_CAPTURE_EXECUTION_WRAPPER_ONLY"
        and static_plan.get("execute_in_28e") is False
        and static_plan.get("actual_live_market_capture_in_28e") is False
        and static_plan.get("future_execution_requires_market_session") is True
    )
    proof28d_ok = (
        proof28d.get("verdict") == "PASS_OBSERVE_ONLY_MARKET_SESSION_CAPTURE_RUNBOOK_28D"
        and proof28d.get("observe_only_market_session_capture_28d_ok") is True
        and proof28d.get("paper_armed_approved") is False
        and proof28d.get("live_trading_approved") is False
    )

    ok = bool(
        schema_ok
        and static_plan_ok
        and proof28d_ok
        and runtime_validation.get("ok") is True
        and materialized_validation.get("ok") is True
        and artifacts_ok
    )

    proof = {
        "schema_version": "proof_observe_only_market_session_capture_execution_contract_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "observe_only_market_session_capture_execution_contract_ok": ok,
        "schema_ok": schema_ok,
        "static_plan_ok": static_plan_ok,
        "proof28d_ok": proof28d_ok,
        "runtime_validation_ok": runtime_validation.get("ok"),
        "materialized_validation_ok": materialized_validation.get("ok"),
        "required_artifacts_ok": artifacts_ok,
        "artifact_root": str(root),
        "accepted_for": "OBSERVE_ONLY_MARKET_SESSION_CAPTURE_EXECUTION_WRAPPER_ONLY" if ok else "NOT_ACCEPTED",
        "execute_in_28e": False,
        "actual_live_market_capture_in_28e": False,
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
        "verdict": "PASS_OBSERVE_ONLY_MARKET_SESSION_CAPTURE_EXECUTION_CONTRACT" if ok else "FAIL_REVIEW_REQUIRED",
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"verdict": proof["verdict"], "ok": ok}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
