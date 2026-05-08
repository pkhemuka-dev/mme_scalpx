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

from app.mme_scalpx.replay.live_evidence_map import (
    REQUIRED_EVIDENCE_ITEMS,
    validate_actual_evidence_map_generation_result,
    write_actual_evidence_maps,
)


def load_json(path: Path) -> dict:
    if not path.exists():
        return {"missing": True}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_observe_only_actual_evidence_map_generation_contract.json")
    parser.add_argument("--candidate-map", default="etc/replay/parity/observe_only_actual_generated_evidence_map_candidate_28g.json")
    parser.add_argument("--final-map", default="etc/replay/parity/observe_only_actual_generated_evidence_map.json")
    parser.add_argument("--missing-report", default="run/proofs/observe_only_actual_evidence_map_missing_report_28g.json")
    args = parser.parse_args()

    schema = load_json(Path("etc/replay/schemas/observe_only_actual_evidence_map_generation_contract_v1.json"))
    static_plan = load_json(Path("etc/replay/parity/observe_only_actual_evidence_map_generation_plan_v1.json"))
    proof28f = load_json(Path("run/proofs/proof_observe_only_market_session_package_collection_28f_latest.json"))

    result = write_actual_evidence_maps(
        candidate_path=args.candidate_map,
        final_path=args.final_map,
        missing_report_path=args.missing_report,
    )
    validation = validate_actual_evidence_map_generation_result(result)

    schema_ok = (
        schema.get("accepted_for") == "OBSERVE_ONLY_ACTUAL_EVIDENCE_MAP_GENERATION_ONLY"
        and schema.get("generates_candidate_map") is True
        and schema.get("publishes_final_map_only_when_complete") is True
        and schema.get("starts_services") is False
        and schema.get("reads_live_redis") is False
        and schema.get("writes_live_redis") is False
        and schema.get("calls_broker_api") is False
        and schema.get("paper_armed_approved") is False
        and schema.get("live_trading_approved") is False
        and schema.get("full_live_replay_parity") == "NOT_PROVEN_IN_28G"
    )
    static_plan_ok = (
        static_plan.get("accepted_for") == "OBSERVE_ONLY_ACTUAL_EVIDENCE_MAP_GENERATION_ONLY"
        and static_plan.get("generates_candidate_map") is True
        and static_plan.get("publishes_final_map_only_when_complete") is True
    )
    proof28f_ok = (
        proof28f.get("observe_only_market_session_package_collection_28f_ok") is True
        and proof28f.get("paper_armed_approved") is False
        and proof28f.get("live_trading_approved") is False
    )

    install_ok = bool(schema_ok and static_plan_ok and proof28f_ok and validation.get("ok") is True)
    generated_ok = bool(install_ok and result.get("complete") is True and result.get("final_map_published") is True)
    deferred_ok = bool(install_ok and result.get("complete") is False and result.get("final_map_published") is False)

    if generated_ok:
        verdict = "PASS_OBSERVE_ONLY_ACTUAL_EVIDENCE_MAP_GENERATED"
    elif deferred_ok:
        verdict = "DEFERRED_MARKET_SESSION_PROOF_OUTPUTS_REQUIRED"
    else:
        verdict = "FAIL_REVIEW_REQUIRED"

    proof = {
        "schema_version": "proof_observe_only_actual_evidence_map_generation_contract_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "observe_only_actual_evidence_map_generation_contract_ok": install_ok,
        "actual_evidence_map_generated_ok": generated_ok,
        "deferred_ok": deferred_ok,
        "schema_ok": schema_ok,
        "static_plan_ok": static_plan_ok,
        "proof28f_ok": proof28f_ok,
        "validation_ok": validation.get("ok"),
        "candidate_map": args.candidate_map,
        "final_map": args.final_map,
        "missing_report": args.missing_report,
        "required_evidence_items": REQUIRED_EVIDENCE_ITEMS,
        "found_count": result.get("found_count"),
        "missing_count": result.get("missing_count"),
        "missing": result.get("missing"),
        "final_map_published": result.get("final_map_published"),
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
        "verdict": verdict,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps({"verdict": verdict, "install_ok": install_ok, "generated_ok": generated_ok, "deferred_ok": deferred_ok}, indent=2))
    return 0 if install_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
