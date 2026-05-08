#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.replay.raw_trade_family_backfill import backfill_trade_families


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill family/side/strategy_id on closed-trade replay rows.")
    parser.add_argument("--input-jsonl", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    result = backfill_trade_families(
        input_jsonl=args.input_jsonl,
        output_dir=args.output_dir,
        run_id=args.run_id,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
