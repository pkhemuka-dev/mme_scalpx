#!/usr/bin/env python3
"""
bin/research_capture_raw_capture_smoke.py

Freeze-grade smoke entrypoint for the first real raw-capture bridge.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.research_capture.raw_capture_bridge import (  # noqa: E402
    run_first_real_raw_capture,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Freeze-grade first real raw-capture smoke."
    )
    parser.add_argument(
        "--entrypoint",
        choices=("run", "backfill"),
        default="run",
    )
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--session-date", default=None)
    parser.add_argument("--start-date", default=None)
    parser.add_argument("--end-date", default=None)
    parser.add_argument("--instrument-scope", default="NIFTY_OPTIONS")
    parser.add_argument("--notes", default=None)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    result = run_first_real_raw_capture(
        args.entrypoint,
        run_id=args.run_id,
        session_date=args.session_date,
        start_date=args.start_date,
        end_date=args.end_date,
        instrument_scope=args.instrument_scope,
        notes=args.notes,
        project_root=PROJECT_ROOT,
    )

    print("raw_capture_ok", True)
    print("entrypoint", result.entrypoint)
    print("lane", result.lane)
    print("source", result.source)
    print("run_id", result.run_id)
    print("rows_written", result.rows_written)
    print("primary_capture_target", result.primary_capture_target)
    print("written_files", [item.name for item in result.written_files])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
