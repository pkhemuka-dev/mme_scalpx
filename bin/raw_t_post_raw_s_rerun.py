#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.research_gate.post_raw_s_replay_rerun import run_post_raw_s_rerun


def main() -> int:
    parser = argparse.ArgumentParser(description="Run RAW-T post-RAW-S replay-only export and RAW rerun.")
    parser.add_argument("--project-root", default=str(PROJECT_ROOT))
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--replay-export-dir", required=True)
    parser.add_argument("--raw-n-before-dir", required=True)
    parser.add_argument("--raw-q-dir", required=True)
    parser.add_argument("--raw-n-after-dir", required=True)
    parser.add_argument("--raw-r-dir", required=True)
    parser.add_argument("--old-raw-j-proof", required=True)
    parser.add_argument("--old-raw-m-proof", required=True)
    parser.add_argument("--baseline-raw-q-proof", required=True)
    parser.add_argument("--baseline-raw-r-proof", required=True)
    parser.add_argument("--max-files", type=int, default=150)
    parser.add_argument("--max-rows-per-file", type=int, default=8000)
    args = parser.parse_args()

    result = run_post_raw_s_rerun(
        project_root=args.project_root,
        run_id=args.run_id,
        output_dir=args.output_dir,
        replay_export_dir=args.replay_export_dir,
        raw_n_before_dir=args.raw_n_before_dir,
        raw_q_dir=args.raw_q_dir,
        raw_n_after_dir=args.raw_n_after_dir,
        raw_r_dir=args.raw_r_dir,
        old_raw_j_proof=args.old_raw_j_proof,
        old_raw_m_proof=args.old_raw_m_proof,
        baseline_raw_q_proof=args.baseline_raw_q_proof,
        baseline_raw_r_proof=args.baseline_raw_r_proof,
        max_files=args.max_files,
        max_rows_per_file=args.max_rows_per_file,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
