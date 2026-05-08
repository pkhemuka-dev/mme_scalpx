#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.replay.raw_artifact_enricher import enrich_replay_artifacts


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe RAW-P true-family emission from replay raw artifact enricher.")
    parser.add_argument("--project-root", default=str(PROJECT_ROOT))
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--max-files", type=int, default=100)
    parser.add_argument("--max-rows-per-file", type=int, default=5000)
    args = parser.parse_args()

    result = enrich_replay_artifacts(
        project_root=args.project_root,
        output_dir=args.output_dir,
        run_id=args.run_id,
        max_files=args.max_files,
        max_rows_per_file=args.max_rows_per_file,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
