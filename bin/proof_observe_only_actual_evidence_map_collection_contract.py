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

from app.mme_scalpx.replay.live_package_collector import (
    collect_actual_observe_only_evidence_package,
    validate_actual_observe_only_evidence_package_result,
)


def load_json(path: Path) -> dict:
    if not path.exists():
        return {"missing": True}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_observe_only_actual_evidence_map_collection_contract.json")
    parser.add_argument("--capture-id", default="observe_only_actual_market_session")
    parser.add_argument("--evidence-map", default="etc/replay/parity/observe_only_actual_generated_evidence_map.json")
    parser.add_argument("--root", default="")
    args = parser.parse_args()

    root = args.root or ("run/replay/parity/live_evidence/" + args.capture_id)
    schema = load_json(Path("etc/replay/schemas/observe_only_actual_evidence_map_collection_contract_v1.json"))
    static_plan = load_json(Path("etc/replay/parity/observe_only_actual_evidence_map_collection_plan_v1.json"))
    proof28e = load_json(Path("run/proofs/proof_observe_only_market_session_capture_28e_latest.json"))

    result = collect_actual_observe_only_evidence_package(
        capture_id=args.capture_id,
        evidence_map=args.evidence_map,
        root=root,
        require_actual_map=True,
    )
    validation = validate_actual_observe_only_evidence_package_result(result)

    evidence_map_present = result.get("actual_evidence_map_present") is True
    evidence_map_valid = result.get("actual_evidence_map_valid") is True
    collected = result.get("actual_package_collected") is True
    deferred = result.get("collection_deferred") is True

    schema_ok = (
        schema.get("accepted_for") == "OBSERVE_ONLY_ACTUAL_EVIDENCE_MAP_PACKAGE_COLLECTION_ONLY"
        and schema.get("actual_live_market_capture_started_by_28f") is False
        and schema.get("collection_requires_actual_evidence_map") is True
        and schema.get("collection_only_copies_existing_evidence_files") is True
        and schema.get("starts_services") is False
        and schema.get("reads_live_redis") is False
        and schema.get("writes_live_redis") is False
        and schema.get("calls_broker_api") is False
        and schema.get("paper_armed_approved") is False
        and schema.get("live_trading_approved") is False
        and schema.get("full_live_replay_parity") == "NOT_PROVEN_IN_28F"
    )
    static_plan_ok = (
        static_plan.get("accepted_for") == "OBSERVE_ONLY_ACTUAL_EVIDENCE_MAP_PACKAGE_COLLECTION_ONLY"
        and static_plan.get("collection_requires_actual_evidence_map") is True
        and static_plan.get("collection_only_copies_existing_evidence_files") is True
    )
    proof28e_ok = (
        proof28e.get("verdict") == "PASS_OBSERVE_ONLY_MARKET_SESSION_CAPTURE_EXECUTION_WRAPPER_28E"
        and proof28e.get("observe_only_market_session_capture_28e_ok") is True
        and proof28e.get("paper_armed_approved") is False
        and proof28e.get("live_trading_approved") is False
    )
    safety_ok = validation.get("safety_ok") is True

    install_ok = bool(schema_ok and static_plan_ok and proof28e_ok and validation.get("ok") is True and safety_ok)
    actual_collection_ok = bool(install_ok and evidence_map_present and evidence_map_valid and collected and not deferred)
    deferred_ok = bool(install_ok and deferred and not evidence_map_present)

    if actual_collection_ok:
        verdict = "PASS_OBSERVE_ONLY_ACTUAL_EVIDENCE_MAP_PACKAGE_COLLECTION"
    elif deferred_ok:
        verdict = "DEFERRED_ACTUAL_EVIDENCE_MAP_REQUIRED"
    else:
        verdict = "FAIL_REVIEW_REQUIRED"

    proof = {
        "schema_version": "proof_observe_only_actual_evidence_map_collection_contract_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "observe_only_actual_evidence_map_collection_contract_ok": install_ok,
        "actual_collection_ok": actual_collection_ok,
        "deferred_ok": deferred_ok,
        "schema_ok": schema_ok,
        "static_plan_ok": static_plan_ok,
        "proof28e_ok": proof28e_ok,
        "validation_ok": validation.get("ok"),
        "safety_ok": safety_ok,
        "actual_evidence_map": args.evidence_map,
        "actual_evidence_map_present": evidence_map_present,
        "actual_evidence_map_valid": evidence_map_valid,
        "actual_package_collected": collected,
        "collection_deferred": deferred,
        "defer_reason": result.get("defer_reason"),
        "artifact_root": result.get("artifact_root"),
        "accepted_for": result.get("accepted_for"),
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
        "full_live_replay_parity": "NOT_PROVEN_IN_28F",
        "verdict": verdict,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps({"verdict": verdict, "install_ok": install_ok, "actual_collection_ok": actual_collection_ok, "deferred_ok": deferred_ok}, indent=2))
    return 0 if install_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
