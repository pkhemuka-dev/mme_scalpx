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

from app.mme_scalpx.replay.contracts import (  # noqa: E402
    REPLAY_INTEGRITY_POLICY_FILE,
    REPLAY_INTEGRITY_REQUIRED_CHECKS,
    REPLAY_RESET_REQUIRED_COMPONENTS,
    REPLAY_RUN_ID_HASH_INPUTS,
    replay_deterministic_integrity_contract_summary,
)
from app.mme_scalpx.replay.integrity import (  # noqa: E402
    replay_compute_deterministic_run_id,
    replay_event_order_integrity,
    replay_fingerprint,
    replay_integrity_summary,
)
from app.mme_scalpx.replay.reset import REPLAY_RESET_COMPONENTS, replay_empty_reset_state, assert_replay_reset_clean  # noqa: E402


def read_policy_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_replay_integrity.json")
    args = parser.parse_args()

    policy_path = ROOT / REPLAY_INTEGRITY_POLICY_FILE
    policy_exists = policy_path.exists()
    policy_text = read_policy_text(policy_path) if policy_exists else ""

    policy_required_terms = [
        "deterministic_run_id",
        "dataset_hash_present",
        "profile_hash_present",
        "event_order_monotonic",
        "reset_cleanliness",
        "no_broker_call",
        "no_live_redis_write",
        "no_runtime_promotion",
        "paper_armed_approved: false",
        "live_trading_approved: false",
        "production_doctrine_changed: false",
    ]
    missing_policy_terms = [term for term in policy_required_terms if term not in policy_text]

    dataset_fp = replay_fingerprint({"dataset": "integrity_smoke", "row_count": 3})
    profile_fp = replay_fingerprint({"profile": "default"})
    experiment_fp = replay_fingerprint({"experiment": "baseline"})
    selected_window_fp = replay_fingerprint({"date": "2026-05-01", "window": "full"})
    code_fp = replay_fingerprint({
        "contracts": Path("app/mme_scalpx/replay/contracts.py").read_text(encoding="utf-8"),
        "reset": Path("app/mme_scalpx/replay/reset.py").read_text(encoding="utf-8"),
        "integrity": Path("app/mme_scalpx/replay/integrity.py").read_text(encoding="utf-8"),
    })

    run_id = replay_compute_deterministic_run_id(
        dataset_fingerprint=dataset_fp,
        profile_fingerprint=profile_fp,
        experiment_fingerprint=experiment_fp,
        selected_window_fingerprint=selected_window_fp,
        code_fingerprint=code_fp,
    )

    ordered_events = [
        {"event_ts_ns": 100, "sequence_id": 1},
        {"event_ts_ns": 100, "sequence_id": 2},
        {"event_ts_ns": 200, "sequence_id": 3},
    ]
    unordered_events = [
        {"event_ts_ns": 200, "sequence_id": 3},
        {"event_ts_ns": 100, "sequence_id": 1},
    ]

    ordered = replay_event_order_integrity(ordered_events)
    unordered = replay_event_order_integrity(unordered_events)

    summary = replay_integrity_summary(
        run_id=run_id,
        dataset_fingerprint=dataset_fp,
        profile_fingerprint=profile_fp,
        experiment_fingerprint=experiment_fp,
        selected_window_fingerprint=selected_window_fp,
        code_fingerprint=code_fp,
        events=ordered_events,
    )

    reset_state = replay_empty_reset_state(run_id=run_id)
    reset_clean = assert_replay_reset_clean(reset_state)

    contract_summary = replay_deterministic_integrity_contract_summary()

    required_inputs_ok = all(name in REPLAY_RUN_ID_HASH_INPUTS for name in (
        "dataset_fingerprint",
        "profile_fingerprint",
        "experiment_fingerprint",
        "selected_window_fingerprint",
        "code_fingerprint",
    ))

    reset_components_ok = all(name in REPLAY_RESET_COMPONENTS for name in REPLAY_RESET_REQUIRED_COMPONENTS)

    required_checks_ok = all(name in REPLAY_INTEGRITY_REQUIRED_CHECKS for name in (
        "deterministic_run_id",
        "dataset_hash_present",
        "profile_hash_present",
        "experiment_hash_present",
        "selected_window_hash_present",
        "code_hash_present",
        "event_order_monotonic",
        "reset_cleanliness",
        "no_broker_call",
        "no_live_redis_write",
        "no_runtime_promotion",
    ))

    integrity_ok = (
        policy_exists
        and not missing_policy_terms
        and required_inputs_ok
        and reset_components_ok
        and required_checks_ok
        and ordered["ok"] is True
        and unordered["ok"] is False
        and summary["ok"] is True
        and reset_clean is True
        and contract_summary.get("paper_armed_approved") is False
        and contract_summary.get("live_trading_approved") is False
        and contract_summary.get("production_doctrine_changed") is False
    )

    proof = {
        "schema_version": "proof_replay_integrity_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "integrity_ok": integrity_ok,
        "policy_exists": policy_exists,
        "policy_path": str(policy_path),
        "missing_policy_terms": missing_policy_terms,
        "required_inputs_ok": required_inputs_ok,
        "reset_components_ok": reset_components_ok,
        "required_checks_ok": required_checks_ok,
        "ordered_event_integrity": ordered,
        "unordered_event_detection": unordered,
        "integrity_summary": summary,
        "reset_cleanliness_ok": reset_clean,
        "contract_summary": contract_summary,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "production_doctrine_changed": False,
        "verdict": "PASS" if integrity_ok else "FAIL",
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "proof": str(out),
        "verdict": proof["verdict"],
        "integrity_ok": integrity_ok,
        "policy_exists": policy_exists,
        "missing_policy_terms": missing_policy_terms,
        "required_inputs_ok": required_inputs_ok,
        "reset_components_ok": reset_components_ok,
        "required_checks_ok": required_checks_ok,
        "paper_armed_approved": False,
        "live_trading_approved": False,
    }, indent=2, sort_keys=True))

    return 0 if integrity_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
