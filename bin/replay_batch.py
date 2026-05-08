#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path.cwd()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.mme_scalpx.replay.artifact_materializer import materialize_replay_run_artifacts  # noqa: E402
from app.mme_scalpx.replay.batch_runner import (  # noqa: E402
    build_date_list_plan,
    build_date_range_plan,
    build_intraday_window_plan,
    build_scenario_matrix_plan,
    build_single_day_plan,
    simulate_replay_batch_plan,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay-only batch runner. Does not touch live Redis or brokers.")
    parser.add_argument("--scope", choices=["single_day", "date_range", "date_list", "intraday_window", "scenario_matrix"], required=True)
    parser.add_argument("--day")
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--dates", nargs="*")
    parser.add_argument("--start-time")
    parser.add_argument("--end-time")
    parser.add_argument("--scenario")
    parser.add_argument("--out-root", default="run/replay")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.scope == "single_day":
        if not args.day:
            raise SystemExit("--day required for single_day")
        plan = build_single_day_plan(day=args.day, scenario_id=args.scenario)
    elif args.scope == "date_range":
        if not args.start_date or not args.end_date:
            raise SystemExit("--start-date and --end-date required for date_range")
        plan = build_date_range_plan(start_date=args.start_date, end_date=args.end_date, scenario_id=args.scenario)
    elif args.scope == "date_list":
        if not args.dates:
            raise SystemExit("--dates required for date_list")
        plan = build_date_list_plan(dates=tuple(args.dates), scenario_id=args.scenario)
    elif args.scope == "intraday_window":
        if not args.day or not args.start_time or not args.end_time:
            raise SystemExit("--day, --start-time, and --end-time required for intraday_window")
        plan = build_intraday_window_plan(day=args.day, start_time=args.start_time, end_time=args.end_time, scenario_id=args.scenario)
    else:
        if not args.dates:
            raise SystemExit("--dates required for scenario_matrix")
        plan = build_scenario_matrix_plan(dates=tuple(args.dates), start_time=args.start_time, end_time=args.end_time)

    result = simulate_replay_batch_plan(plan)
    payload = {
        "plan": plan,
        "simulation_result": result,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
    }

    if args.dry_run:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))
        return 0

    materialized = materialize_replay_run_artifacts(
        run_id=str(plan["plan_id"]),
        plan=plan,
        simulation_result=result,
        base_dir=args.out_root,
    )
    print(json.dumps(materialized, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
