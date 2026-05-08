#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path.cwd()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.mme_scalpx.replay.batch_runner import build_scenario_matrix_plan, simulate_replay_batch_plan  # noqa: E402
from app.mme_scalpx.replay.report_exporter import (  # noqa: E402
    build_baseline_shadow_comparison,
    materialize_replay_report_exports,
)
from app.mme_scalpx.replay.scenarios import REPLAY_REQUIRED_SCENARIOS  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay-only report exporter. Does not touch live Redis or brokers.")
    parser.add_argument("--dates", nargs="*", default=["2026-05-01"])
    parser.add_argument("--out-root", default="run/replay")
    parser.add_argument("--run-id")
    args = parser.parse_args()

    baseline_plan = build_scenario_matrix_plan(dates=tuple(args.dates), scenarios=("full_fill",))
    shadow_plan = build_scenario_matrix_plan(dates=tuple(args.dates), scenarios=REPLAY_REQUIRED_SCENARIOS)

    baseline_result = simulate_replay_batch_plan(baseline_plan)
    shadow_result = simulate_replay_batch_plan(shadow_plan)

    run_id = args.run_id or f"report_export_{shadow_plan['plan_id']}"
    export_root = str(Path(args.out_root) / run_id / "exports")

    comparison = build_baseline_shadow_comparison(
        baseline_label="baseline_full_fill",
        baseline_result=baseline_result,
        shadow_label="shadow_scenario_matrix",
        shadow_result=shadow_result,
    )

    result = materialize_replay_report_exports(
        run_id=run_id,
        simulation_result=shadow_result,
        export_root=export_root,
        baseline_comparison=comparison,
    )

    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
