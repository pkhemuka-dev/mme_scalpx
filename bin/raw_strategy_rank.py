#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.research_gate.strategy_rank import write_strategy_rank_bundle


def main() -> int:
    parser = argparse.ArgumentParser(description="Run RAW strategy-ranking desk.")
    parser.add_argument("--pnl-report", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--min-family-trades", type=int, default=3)
    args = parser.parse_args()

    result = write_strategy_rank_bundle(
        pnl_report_path=args.pnl_report,
        output_dir=args.output_dir,
        run_id=args.run_id,
        min_family_trade_count=args.min_family_trades,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
