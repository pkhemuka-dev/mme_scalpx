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

from app.mme_scalpx.replay.live_capture_runbook import (
    REQUIRED_OPERATOR_PLAN_ARTIFACTS,
    build_observe_only_market_session_capture_runbook,
    materialize_observe_only_market_session_operator_plan,
    validate_materialized_observe_only_market_session_operator_plan,
    validate_observe_only_market_session_capture_runbook,
)


def load_json(path: Path) -> dict:
    if not path.exists():
        return {"missing": True}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_observe_only_market_session_capture_runbook.json")
    args = parser.parse_args()

    schema = load_json(Path("etc/replay/schemas/observe_only_market_session_capture_runbook_contract_v1.json"))
    static_plan = load_json(Path("etc/replay/parity/observe_only_market_session_capture_runbook_v1.json"))
    proof28c = load_json(Path("run/proofs/proof_observe_only_live_evidence_capture_28c_latest.json"))

    runtime_plan = build_observe_only_market_session_capture_runbook()
    runtime_validation = validate_observe_only_market_session_capture_runbook(runtime_plan)

    result = materialize_observe_only_market_session_operator_plan(
        session_id="batch28d_operator_plan",
        root="run/replay/parity/live_session_operator/batch28d_operator_plan",
    )

    materialized_validation = validate_materialized_observe_only_market_session_operator_plan(result)
    root = Path(result["artifact_root"])
    artifacts_ok = all((root / name).is_file() for name in REQUIRED_OPERATOR_PLAN_ARTIFACTS)

    ok = bool(
        schema.get("operator_plan_only") is True
        and schema.get("actual_live_market_capture") is False
        and static_plan.get("operator_plan_only") is True
        and static_plan.get("actual_live_market_capture") is False
        and proof28c.get("observe_only_live_evidence_capture_28c_ok") is True
        and runtime_validation.get("ok") is True
        and materialized_validation.get("ok") is True
        and artifacts_ok
    )

    proof = {
        "schema_version": "proof_observe_only_market_session_capture_runbook_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "observe_only_market_session_capture_runbook_ok": ok,
        "runtime_validation_ok": runtime_validation.get("ok"),
        "materialized_validation_ok": materialized_validation.get("ok"),
        "required_artifacts_ok": artifacts_ok,
        "proof28c_ok": proof28c.get("observe_only_live_evidence_capture_28c_ok"),
        "artifact_root": str(root),
        "accepted_for": "OBSERVE_ONLY_MARKET_SESSION_CAPTURE_RUNBOOK_ONLY" if ok else "NOT_ACCEPTED",
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
        "verdict": "PASS_OBSERVE_ONLY_MARKET_SESSION_CAPTURE_RUNBOOK" if ok else "FAIL_REVIEW_REQUIRED",
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"verdict": proof["verdict"], "ok": ok}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
