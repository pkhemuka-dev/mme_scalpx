#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
from datetime import datetime, timezone
from typing import Any

def write_json(path: pathlib.Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
    tmp.replace(path)

def safe_under_run_replay(project_root: pathlib.Path, path: pathlib.Path) -> bool:
    replay_root = (project_root / "run" / "replay").resolve()
    return str(path.resolve()).startswith(str(replay_root) + "/")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--dataset-candidate-root", required=True)
    parser.add_argument("--adapter-execution-root", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    dataset_candidate_root = pathlib.Path(args.dataset_candidate_root).resolve()
    adapter_execution_root = pathlib.Path(args.adapter_execution_root).resolve()
    output_root = pathlib.Path(args.output_root).resolve()

    if not safe_under_run_replay(project_root, dataset_candidate_root):
        raise SystemExit("dataset candidate root must stay under run/replay")
    if not safe_under_run_replay(project_root, adapter_execution_root):
        raise SystemExit("adapter execution root must stay under run/replay")
    if not safe_under_run_replay(project_root, output_root):
        raise SystemExit("output root must stay under run/replay")

    output_root.mkdir(parents=True, exist_ok=True)

    result = {
        "schema_version": "actual_replay_engine_integration_preflight_script_result_28q_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "accepted_for": "ACTUAL_REPLAY_ENGINE_INTEGRATION_PREFLIGHT_ONLY",
        "dataset_candidate_root": str(dataset_candidate_root),
        "adapter_execution_root": str(adapter_execution_root),
        "output_root": str(output_root),
        "preflight_only": bool(args.preflight_only),
        "integration_preflight_script_ok": True,
        "replay_engine_executed": False,
        "replay_run_completed": False,
        "comparison_completed": False,
        "starts_services": False,
        "reads_live_redis": False,
        "writes_live_redis": False,
        "calls_broker_api": False,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "production_doctrine_changed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28Q",
    }

    write_json(output_root / "00_preflight_script_marker.json", result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
