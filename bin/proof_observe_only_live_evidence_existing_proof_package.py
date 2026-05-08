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


REQUIRED_ITEMS = tuple([
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

REQUIRED_ARTIFACTS = tuple([
    "00_live_evidence_manifest.json",
    "01_provider_runtime.json",
    "02_feed_snapshot.json",
    "03_feature_payload.json",
    "04_family_surfaces.json",
    "05_strategy_activation.json",
    "06_no_order_sent.json",
    "07_live_stream_inventory.json",
    "08_live_hash_inventory.json",
    "09_provider_health_snapshot.json",
    "10_selected_option_context.json",
    "11_dhan_oi_ladder_context.json",
    "12_live_capture_log_reference.json",
    "13_capture_completeness.json",
    "14_no_enablement_boundary.json",
    "15_capture_reproducibility.json",
])


def load_json(path: Path) -> dict:
    if not path.exists():
        return {"missing": True, "verdict": "MISSING"}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_observe_only_live_evidence_existing_proof_package.json")
    parser.add_argument("--capture-root", default="run/replay/parity/live_evidence/batch28c_existing_proof_dry_run")
    parser.add_argument("--collect-result", default="run/proofs/observe_only_live_evidence_existing_proof_collect_stdout_28c.json")
    parser.add_argument("--evidence-map", default="etc/replay/parity/observe_only_live_evidence_existing_proof_map_28c.json")
    args = parser.parse_args()

    capture_root = Path(args.capture_root)
    collect_result = load_json(Path(args.collect_result))
    evidence_map = load_json(Path(args.evidence_map))
    proof28b = load_json(Path("run/proofs/proof_observe_only_live_evidence_capture_28b_latest.json"))

    map_missing = []
    for item in REQUIRED_ITEMS:
        raw = evidence_map.get(item)
        if not raw or not Path(raw).is_file():
            map_missing.append({"item": item, "path": raw})

    artifact_missing = []
    for name in REQUIRED_ARTIFACTS:
        if not (capture_root / name).is_file():
            artifact_missing.append(name)

    evidence_dir = capture_root / "evidence_files"
    copied_files = sorted(str(p) for p in evidence_dir.glob("*") if p.is_file()) if evidence_dir.exists() else []

    completeness = load_json(capture_root / "13_capture_completeness.json")
    boundary = load_json(capture_root / "14_no_enablement_boundary.json")
    manifest = load_json(capture_root / "00_live_evidence_manifest.json")

    copied_items = tuple(sorted((collect_result.get("copied") or {}).keys()))
    missing_items = tuple(sorted((collect_result.get("missing") or {}).keys()))

    map_ok = not map_missing and tuple(sorted(evidence_map.keys())) == tuple(sorted(REQUIRED_ITEMS))
    artifacts_ok = not artifact_missing
    copy_ok = len(copied_items) == len(REQUIRED_ITEMS) and not missing_items and len(copied_files) >= len(REQUIRED_ITEMS)
    completeness_ok = completeness.get("complete") is True and not completeness.get("missing_items")
    boundary_ok = (
        boundary.get("starts_services") is False
        and boundary.get("reads_live_redis") is False
        and boundary.get("writes_live_redis") is False
        and boundary.get("calls_broker_api") is False
        and boundary.get("paper_armed_approved") is False
        and boundary.get("live_trading_approved") is False
        and boundary.get("execution_arming_created") is False
        and boundary.get("real_order_sent") is False
        and boundary.get("broker_calls_executed") is False
        and boundary.get("live_redis_writes_executed") is False
        and boundary.get("production_doctrine_changed") is False
        and boundary.get("full_live_replay_parity") == "NOT_PROVEN_IN_28B"
    )
    manifest_ok = (
        manifest.get("actual_live_evidence_collected") is True
        and len(tuple(manifest.get("copied_evidence_items") or ())) == len(REQUIRED_ITEMS)
        and manifest.get("paper_armed_approved") is False
        and manifest.get("live_trading_approved") is False
    )
    no_enablement_ok = (
        collect_result.get("starts_services") is False
        and collect_result.get("reads_live_redis") is False
        and collect_result.get("writes_live_redis") is False
        and collect_result.get("calls_broker_api") is False
        and collect_result.get("paper_armed_approved") is False
        and collect_result.get("live_trading_approved") is False
        and collect_result.get("execution_arming_created") is False
        and collect_result.get("real_order_sent") is False
        and collect_result.get("broker_calls_executed") is False
        and collect_result.get("live_redis_writes_executed") is False
        and collect_result.get("production_doctrine_changed") is False
    )
    prerequisite_ok = (
        proof28b.get("verdict") == "PASS_OBSERVE_ONLY_LIVE_EVIDENCE_CAPTURE_CONTRACT_28B"
        and proof28b.get("observe_only_live_evidence_capture_28b_ok") is True
    )

    ok = bool(
        map_ok
        and artifacts_ok
        and copy_ok
        and completeness_ok
        and boundary_ok
        and manifest_ok
        and no_enablement_ok
        and prerequisite_ok
    )

    proof = {
        "schema_version": "proof_observe_only_live_evidence_existing_proof_package_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "observe_only_live_evidence_existing_proof_package_ok": ok,
        "accepted_for": "EXISTING_PROOF_PACKAGE_DRY_RUN_ONLY" if ok else "NOT_ACCEPTED",
        "capture_root": str(capture_root),
        "map_ok": map_ok,
        "map_missing": map_missing,
        "artifacts_ok": artifacts_ok,
        "artifact_missing": artifact_missing,
        "copy_ok": copy_ok,
        "copied_items": copied_items,
        "missing_items": missing_items,
        "copied_file_count": len(copied_files),
        "completeness_ok": completeness_ok,
        "boundary_ok": boundary_ok,
        "manifest_ok": manifest_ok,
        "no_enablement_ok": no_enablement_ok,
        "prerequisite_28b_ok": prerequisite_ok,
        "evidence_source_type": "EXISTING_PROOF_ARTIFACTS_DRY_RUN",
        "actual_live_market_capture": False,
        "actual_live_evidence_collected_from_existing_files": True,
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
        "paper_armed_readiness": "NOT_APPROVED_IN_28C",
        "live_trading_readiness": "NOT_APPROVED_IN_28C",
        "production_strategy_improvement_claim": "NOT_PROVEN_IN_28C",
        "production_doctrine_revision": "NOT_APPROVED_IN_28C",
        "full_live_replay_parity": "NOT_PROVEN_IN_28C",
        "verdict": "PASS_OBSERVE_ONLY_LIVE_EVIDENCE_EXISTING_PROOF_PACKAGE" if ok else "FAIL_REVIEW_REQUIRED",
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True, default=str), encoding="utf-8")

    print(json.dumps({
        "proof": str(out),
        "verdict": proof["verdict"],
        "observe_only_live_evidence_existing_proof_package_ok": ok,
        "accepted_for": proof["accepted_for"],
        "map_ok": map_ok,
        "artifacts_ok": artifacts_ok,
        "copy_ok": copy_ok,
        "completeness_ok": completeness_ok,
        "boundary_ok": boundary_ok,
        "manifest_ok": manifest_ok,
        "no_enablement_ok": no_enablement_ok,
        "actual_live_market_capture": False,
        "starts_services": False,
        "reads_live_redis": False,
        "writes_live_redis": False,
        "calls_broker_api": False,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28C",
    }, indent=2, sort_keys=True))

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
