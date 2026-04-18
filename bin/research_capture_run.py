#!/usr/bin/env python3
"""
bin/research_capture_run.py

Freeze-grade operational run entrypoint for the research-capture chapter.

Operational routing
-------------------
- verify   -> seeded runtime bridge
- research -> seeded runtime bridge
- run      -> first real raw-capture bridge
- backfill -> first real raw-capture bridge

Design laws
-----------
- raw capture first
- light live-derived later
- heavy offline-derived later
- canonical operational entrypoint should use the real raw-capture lane where available
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
from app.mme_scalpx.research_capture.runtime_bridge import (  # noqa: E402
    run_seeded_runtime_bridge,
)


def _csv_to_list(value: str | None) -> list[str] | None:
    if value is None:
        return None
    parts = [item.strip() for item in value.split(",")]
    parts = [item for item in parts if item]
    return parts or None


def _export_overrides(values: list[str] | None) -> dict[str, str] | None:
    if not values:
        return None
    overrides: dict[str, str] = {}
    for raw in values:
        if "=" not in raw:
            raise SystemExit(f"invalid --export-format override: {raw!r}; expected family=format")
        family, fmt = raw.split("=", 1)
        family = family.strip()
        fmt = fmt.strip()
        if not family or not fmt:
            raise SystemExit(f"invalid --export-format override: {raw!r}; expected family=format")
        overrides[family] = fmt
    return overrides


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Freeze-grade research-capture run entrypoint.")
    parser.add_argument(
        "--entrypoint",
        choices=("verify", "run", "backfill", "research"),
        default="run",
    )
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--session-date", default=None)
    parser.add_argument("--start-date", default=None)
    parser.add_argument("--end-date", default=None)
    parser.add_argument("--session-dates", default=None, help="Comma-separated session dates.")
    parser.add_argument("--instrument-scope", default=None)
    parser.add_argument("--research-profile", default=None)
    parser.add_argument("--feature-families", default=None, help="Comma-separated feature families.")
    parser.add_argument("--notes", default=None)
    parser.add_argument("--lane-override", default=None)
    parser.add_argument("--source-override", default=None)
    parser.add_argument(
        "--export-format",
        action="append",
        default=None,
        help="Override export format as family=format; may be repeated.",
    )
    return parser.parse_args()


def _default_run_id(entrypoint: str) -> str:
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"research_capture_{entrypoint}_{ts}"


def main() -> int:
    args = _parse_args()

    run_id = args.run_id or _default_run_id(args.entrypoint)
    session_dates = _csv_to_list(args.session_dates)
    feature_families = _csv_to_list(args.feature_families)
    export_format_overrides = _export_overrides(args.export_format)

    if args.entrypoint in {"run", "backfill"}:
        result = run_first_real_raw_capture(
            args.entrypoint,
            run_id=run_id,
            session_date=args.session_date,
            start_date=args.start_date,
            end_date=args.end_date,
            session_dates=session_dates,
            instrument_scope=args.instrument_scope,
            research_profile=args.research_profile,
            feature_families=feature_families,
            notes=args.notes,
            lane_override=args.lane_override,
            source_override=args.source_override,
            export_format_overrides=export_format_overrides,
            project_root=PROJECT_ROOT,
        )
        print("run_ok", True)
        print("entrypoint", result.entrypoint)
        print("lane", result.lane)
        print("source", result.source)
        print("run_id", result.run_id)
        print("rows_written", result.rows_written)
        print("primary_capture_target", result.primary_capture_target)
        print("written_files", [item.name for item in result.written_files])
        print("capture_targets_required", [item.name for item in result.capture_plan.required_outputs])
        print("capture_targets_optional", [item.name for item in result.capture_plan.optional_outputs])
        return 0

    result = run_seeded_runtime_bridge(
        args.entrypoint,
        run_id=run_id,
        session_date=args.session_date,
        start_date=args.start_date,
        end_date=args.end_date,
        session_dates=session_dates,
        instrument_scope=args.instrument_scope,
        research_profile=args.research_profile,
        feature_families=feature_families,
        notes=args.notes,
        lane_override=args.lane_override,
        source_override=args.source_override,
        export_format_overrides=export_format_overrides,
        project_root=PROJECT_ROOT,
    )
    print("run_ok", True)
    print("entrypoint", result.entrypoint)
    print("lane", result.lane)
    print("source", result.source)
    print("run_id", result.run_id)
    print("written_files", [item.name for item in result.written_files])
    print("capture_targets_required", [item.name for item in result.capture_plan.required_outputs])
    print("capture_targets_optional", [item.name for item in result.capture_plan.optional_outputs])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
