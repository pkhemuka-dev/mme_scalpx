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

from app.mme_scalpx.replay.integrity import (  # noqa: E402
    replay_compute_deterministic_run_id,
    replay_fingerprint,
)
from app.mme_scalpx.replay.reset import (  # noqa: E402
    REPLAY_RESET_COMPONENTS,
    assert_replay_reset_clean,
    replay_empty_reset_state,
    replay_reset_state_canonical_json,
)
from app.mme_scalpx.replay.safety import (  # noqa: E402
    assert_replay_artifact_path,
    assert_replay_config_path,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_replay_deterministic_repeatability.json")
    args = parser.parse_args()

    dataset = {
        "dataset_id": "deterministic_smoke_dataset",
        "rows": [
            {"event_ts_ns": 100, "sequence_id": 1, "fut_ltp": 22000.0},
            {"event_ts_ns": 200, "sequence_id": 2, "fut_ltp": 22001.0},
        ],
    }
    profile = {"profile_id": "deterministic_profile", "mode": "replay"}
    experiment = {"experiment_id": "baseline", "shadow": False}
    selected_window = {"date": "2026-05-01", "start": "09:15:00", "end": "15:30:00"}
    code = {
        "contracts_sha256": replay_fingerprint(Path("app/mme_scalpx/replay/contracts.py").read_text(encoding="utf-8")),
        "integrity_sha256": replay_fingerprint(Path("app/mme_scalpx/replay/integrity.py").read_text(encoding="utf-8")),
    }

    dataset_fp = replay_fingerprint(dataset)
    profile_fp = replay_fingerprint(profile)
    experiment_fp = replay_fingerprint(experiment)
    selected_window_fp = replay_fingerprint(selected_window)
    code_fp = replay_fingerprint(code)

    run_id_1 = replay_compute_deterministic_run_id(
        dataset_fingerprint=dataset_fp,
        profile_fingerprint=profile_fp,
        experiment_fingerprint=experiment_fp,
        selected_window_fingerprint=selected_window_fp,
        code_fingerprint=code_fp,
    )
    run_id_2 = replay_compute_deterministic_run_id(
        dataset_fingerprint=dataset_fp,
        profile_fingerprint=profile_fp,
        experiment_fingerprint=experiment_fp,
        selected_window_fingerprint=selected_window_fp,
        code_fingerprint=code_fp,
    )

    changed_dataset_fp = replay_fingerprint({**dataset, "rows": dataset["rows"] + [{"event_ts_ns": 300, "sequence_id": 3}]})
    changed_run_id = replay_compute_deterministic_run_id(
        dataset_fingerprint=changed_dataset_fp,
        profile_fingerprint=profile_fp,
        experiment_fingerprint=experiment_fp,
        selected_window_fingerprint=selected_window_fp,
        code_fingerprint=code_fp,
    )

    state_1 = replay_empty_reset_state(run_id=run_id_1)
    state_2 = replay_empty_reset_state(run_id=run_id_1)

    reset_clean_1 = assert_replay_reset_clean(state_1)
    reset_clean_2 = assert_replay_reset_clean(state_2)
    reset_json_1 = replay_reset_state_canonical_json(state_1)
    reset_json_2 = replay_reset_state_canonical_json(state_2)

    artifact_root_ok = False
    config_root_ok = False
    artifact_root_rejects_live = False
    config_root_rejects_live = False

    try:
        assert_replay_artifact_path(f"run/replay/{run_id_1}/manifest.json")
        artifact_root_ok = True
    except Exception:
        pass

    try:
        assert_replay_config_path("etc/replay/integrity/replay_integrity_policy.yaml")
        config_root_ok = True
    except Exception:
        pass

    try:
        assert_replay_artifact_path("run/live_capture/not_allowed.json")
    except Exception:
        artifact_root_rejects_live = True

    try:
        assert_replay_config_path("etc/strategy_family/family_runtime.yaml")
    except Exception:
        config_root_rejects_live = True

    deterministic_ok = (
        run_id_1 == run_id_2
        and run_id_1 != changed_run_id
        and reset_clean_1 is True
        and reset_clean_2 is True
        and reset_json_1 == reset_json_2
        and artifact_root_ok
        and config_root_ok
        and artifact_root_rejects_live
        and config_root_rejects_live
    )

    proof = {
        "schema_version": "proof_replay_deterministic_repeatability_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "deterministic_repeatability_ok": deterministic_ok,
        "same_input_same_run_id": run_id_1 == run_id_2,
        "changed_dataset_changes_run_id": run_id_1 != changed_run_id,
        "reset_cleanliness_ok": reset_clean_1 and reset_clean_2,
        "same_reset_state_same_canonical_json": reset_json_1 == reset_json_2,
        "artifact_root_ok": artifact_root_ok,
        "config_root_ok": config_root_ok,
        "artifact_root_rejects_live": artifact_root_rejects_live,
        "config_root_rejects_live": config_root_rejects_live,
        "run_id": run_id_1,
        "changed_run_id": changed_run_id,
        "reset_components": REPLAY_RESET_COMPONENTS,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "production_doctrine_changed": False,
        "verdict": "PASS" if deterministic_ok else "FAIL",
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "proof": str(out),
        "verdict": proof["verdict"],
        "deterministic_repeatability_ok": deterministic_ok,
        "same_input_same_run_id": proof["same_input_same_run_id"],
        "changed_dataset_changes_run_id": proof["changed_dataset_changes_run_id"],
        "reset_cleanliness_ok": proof["reset_cleanliness_ok"],
        "paper_armed_approved": False,
        "live_trading_approved": False,
    }, indent=2, sort_keys=True))

    return 0 if deterministic_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
