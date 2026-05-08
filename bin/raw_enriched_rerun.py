#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.research_gate.enriched_rerun import run_enriched_rerun


def main() -> int:
    parser = argparse.ArgumentParser(description="Run RAW-N enriched evidence rerun.")
    parser.add_argument("--enriched-jsonl", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--old-raw-j-proof", default="")
    parser.add_argument("--old-raw-m-proof", default="")
    args = parser.parse_args()

    result = run_enriched_rerun(
        enriched_jsonl=args.enriched_jsonl,
        output_dir=args.output_dir,
        run_id=args.run_id,
        old_raw_j_proof=args.old_raw_j_proof or None,
        old_raw_m_proof=args.old_raw_m_proof or None,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
