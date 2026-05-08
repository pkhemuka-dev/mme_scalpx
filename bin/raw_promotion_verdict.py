#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.research_gate.promotion import write_promotion_verdict_bundle


def main() -> int:
    parser = argparse.ArgumentParser(description="Run RAW promotion firewall.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--raw-i-proof", required=True)
    parser.add_argument("--source-label", default="current_project")
    args = parser.parse_args()

    result = write_promotion_verdict_bundle(
        output_dir=args.output_dir,
        run_id=args.run_id,
        raw_i_proof_path=args.raw_i_proof,
        source_label=args.source_label,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
