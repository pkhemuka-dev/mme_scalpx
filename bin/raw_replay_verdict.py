#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.research_gate.replay_verdict import write_replay_verdict_bundle


def main() -> int:
    parser = argparse.ArgumentParser(description="Run RAW replay/backtest verdict desk.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--raw-d-proof", required=True)
    parser.add_argument("--raw-e-proof", required=True)
    parser.add_argument("--raw-f-proof", required=True)
    parser.add_argument("--raw-g-proof", required=True)
    parser.add_argument("--raw-h-proof", required=True)
    parser.add_argument("--source-label", default="current_project")
    args = parser.parse_args()

    result = write_replay_verdict_bundle(
        output_dir=args.output_dir,
        run_id=args.run_id,
        raw_d_proof_path=args.raw_d_proof,
        raw_e_proof_path=args.raw_e_proof,
        raw_f_proof_path=args.raw_f_proof,
        raw_g_proof_path=args.raw_g_proof,
        raw_h_proof_path=args.raw_h_proof,
        source_label=args.source_label,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
