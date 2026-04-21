#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.replay.frame_export import (
    ReplayComparisonFrame,
    comparison_frames_to_rows,
)

def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def main() -> int:
    output_root = PROJECT_ROOT / "run" / "replay" / "frame_export_smoke"

    baseline_rows = comparison_frames_to_rows([
        ReplayComparisonFrame(
            frame_id="frame-1",
            healthy=True,
            regime_pass=False,
            economics_valid=False,
            candidate=False,
            side="PUT",
            leg="PUT_ATM1",
            blocker="velocity_ratio",
            ambiguity=False,
            reward_cost_valid=False,
        ),
        ReplayComparisonFrame(
            frame_id="frame-2",
            healthy=True,
            regime_pass=True,
            economics_valid=False,
            candidate=False,
            side="PUT",
            leg="PUT_ATM",
            blocker="reward_cost_fail",
            ambiguity=False,
            reward_cost_valid=False,
        ),
    ])

    shadow_rows = comparison_frames_to_rows([
        ReplayComparisonFrame(
            frame_id="frame-1",
            healthy=True,
            regime_pass=True,
            economics_valid=True,
            candidate=True,
            side="PUT",
            leg="PUT_ATM1",
            blocker=None,
            ambiguity=False,
            reward_cost_valid=True,
        ),
        ReplayComparisonFrame(
            frame_id="frame-2",
            healthy=True,
            regime_pass=True,
            economics_valid=True,
            candidate=True,
            side="PUT",
            leg="PUT_ATM",
            blocker=None,
            ambiguity=False,
            reward_cost_valid=True,
        ),
    ])

    write_json(output_root / "baseline_frames.json", baseline_rows)
    write_json(output_root / "shadow_frames.json", shadow_rows)

    print("output_root", str(output_root))
    print("baseline_count", len(baseline_rows))
    print("shadow_count", len(shadow_rows))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
