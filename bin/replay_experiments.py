#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path.cwd()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.mme_scalpx.replay.experiment_workstation import (  # noqa: E402
    REPLAY_EXPERIMENT_TYPES,
    materialize_replay_experiment_artifacts,
    run_replay_experiment_profile,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay-only experiment workstation. Does not touch live Redis or brokers.")
    parser.add_argument("--profile", choices=REPLAY_EXPERIMENT_TYPES, required=True)
    parser.add_argument("--dates", nargs="*", default=["2026-05-01"])
    parser.add_argument("--out-root", default="run/replay")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    experiment = run_replay_experiment_profile(args.profile, dates=tuple(args.dates))
    experiment_id = str(experiment["experiment_id"])
    export_root = str(Path(args.out_root) / experiment_id / "experiments")

    if args.dry_run:
        print(json.dumps(experiment, indent=2, sort_keys=True, default=str))
        return 0

    materialized = materialize_replay_experiment_artifacts(
        experiment_result=experiment,
        export_root=export_root,
    )
    print(json.dumps(materialized, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
