#!/usr/bin/env python3
"""
bin/research_capture_verify.py

Freeze-grade operational verify entrypoint for the research-capture chapter.

Purpose
-------
- wire the canonical verify flow through the frozen runtime bridge
- produce canonical seeded verify surfaces
- avoid ad hoc verify paths outside the frozen config/session/manifest stack
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.research_capture.runtime_bridge import (  # noqa: E402
    run_seeded_runtime_bridge,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Freeze-grade research-capture verify entrypoint."
    )
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--notes", default=None)
    return parser.parse_args()


def _default_run_id() -> str:
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"research_capture_verify_{ts}"


def main() -> int:
    args = _parse_args()
    run_id = args.run_id or _default_run_id()

    result = run_seeded_runtime_bridge(
        "verify",
        run_id=run_id,
        notes=args.notes,
        project_root=PROJECT_ROOT,
    )

    print("verify_ok", True)
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
