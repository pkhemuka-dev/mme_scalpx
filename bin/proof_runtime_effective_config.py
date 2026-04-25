#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.core import settings

OUT = PROJECT_ROOT / "run" / "proofs" / "runtime_effective_config.json"

def case(name, ok, **details):
    row = {"case": name, "status": "PASS" if ok else "FAIL", **details}
    if not ok:
        raise AssertionError(json.dumps(row, indent=2, sort_keys=True))
    return row

def main() -> int:
    cases = []

    snap = settings.runtime_mode_input_snapshot(
        {
            "MME_RUNTIME_MODE": "live",
            "SCALPX_RUNTIME_MODE": "paper",
        }
    )
    cases.append(case(
        "runtime_mode_input_snapshot_observes_mme_and_scalpx",
        snap["MME_RUNTIME_MODE"] == "live"
        and snap["SCALPX_RUNTIME_MODE"] == "paper",
        snapshot=snap,
    ))

    state = settings.build_effective_runtime_config_state(
        settings_runtime_mode="live",
        runtime_yaml_mode="paper",
        project_env_runtime_mode="paper",
        env_runtime_mode="live",
        source_of_truth="settings.py_observed_only",
        notes={"rule": "no_runtime_behavior_change_in_batch18"},
    )
    cases.append(case(
        "effective_runtime_config_state_records_mismatch",
        "runtime_mode_mismatch" in state["conflicts"]
        and state["settings_runtime_behavior_changed"] is False,
        state=state,
    ))

    cases.append(case(
        "settings_paper_mode_not_silently_enabled_here",
        "paper" not in snap["settings_allowed_runtime_modes"].split(","),
        allowed=snap["settings_allowed_runtime_modes"],
    ))

    proof = {
        "proof": "runtime_effective_config",
        "status": "PASS",
        "settings_runtime_behavior_changed": False,
        "main_audit_required_for_final_runtime_owner": True,
        "cases": cases,
        "failed_cases": [],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
