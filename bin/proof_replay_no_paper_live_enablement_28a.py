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


def load_json(path: Path) -> dict:
    if not path.exists():
        return {"missing": True, "verdict": "MISSING"}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_replay_no_paper_live_enablement_28a.json")
    args = parser.parse_args()

    final_27n = load_json(ROOT / "run/proofs/proof_replay_final_acceptance_gate_latest.json")
    parity_plan = load_json(ROOT / "run/proofs/proof_replay_live_parity_audit_plan.json")
    no_broker = load_json(ROOT / "run/proofs/proof_replay_no_broker_call.json")
    no_redis = load_json(ROOT / "run/proofs/proof_replay_no_live_redis_write.json")
    no_promotion = load_json(ROOT / "run/proofs/proof_replay_no_runtime_promotion.json")

    ok = (
        final_27n.get("paper_armed_approved") is False
        and final_27n.get("live_trading_approved") is False
        and final_27n.get("execution_arming_created") is False
        and final_27n.get("real_order_sent") is False
        and final_27n.get("production_doctrine_changed") is False
        and parity_plan.get("paper_armed_approved") is False
        and parity_plan.get("live_trading_approved") is False
        and parity_plan.get("execution_arming_created") is False
        and parity_plan.get("real_order_sent") is False
        and parity_plan.get("production_doctrine_changed") is False
        and parity_plan.get("full_live_replay_parity") == "NOT_PROVEN_IN_28A"
        and no_broker.get("broker_call_reachable") is False
        and no_redis.get("live_redis_write_reachable") is False
        and no_promotion.get("runtime_promotion_reachable") is False
    )

    proof = {
        "schema_version": "proof_replay_no_paper_live_enablement_28a_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "no_paper_live_enablement_28a_ok": ok,
        "broker_call_reachable": no_broker.get("broker_call_reachable"),
        "live_redis_write_reachable": no_redis.get("live_redis_write_reachable"),
        "runtime_promotion_reachable": no_promotion.get("runtime_promotion_reachable"),
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "paper_armed_readiness": "NOT_APPROVED_IN_28A",
        "live_trading_readiness": "NOT_APPROVED_IN_28A",
        "production_strategy_improvement_claim": "NOT_PROVEN_IN_28A",
        "production_doctrine_revision": "NOT_APPROVED_IN_28A",
        "full_live_replay_parity": "NOT_PROVEN_IN_28A",
        "verdict": "PASS_NO_PAPER_LIVE_ENABLEMENT_28A" if ok else "FAIL_REVIEW_REQUIRED",
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "proof": str(out),
        "verdict": proof["verdict"],
        "no_paper_live_enablement_28a_ok": ok,
        "broker_call_reachable": proof["broker_call_reachable"],
        "live_redis_write_reachable": proof["live_redis_write_reachable"],
        "runtime_promotion_reachable": proof["runtime_promotion_reachable"],
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "full_live_replay_parity": proof["full_live_replay_parity"],
    }, indent=2, sort_keys=True))

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
