#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.replay.raw_enrichment_flow import (
    assert_flow_safety,
    maybe_run_raw_enrichment_after_replay,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run optional RAW enrichment post-export flow for replay artifacts.")
    parser.add_argument("--project-root", default=str(PROJECT_ROOT))
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--enable", action="store_true")
    parser.add_argument("--max-files", type=int, default=100)
    parser.add_argument("--max-rows-per-file", type=int, default=5000)
    args = parser.parse_args()

    result = maybe_run_raw_enrichment_after_replay(
        project_root=args.project_root,
        run_id=args.run_id,
        output_dir=args.output_dir,
        enabled=args.enable,
        max_files=args.max_files,
        max_rows_per_file=args.max_rows_per_file,
    )
    result["flow_safety_ok"] = assert_flow_safety(result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["flow_safety_ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
