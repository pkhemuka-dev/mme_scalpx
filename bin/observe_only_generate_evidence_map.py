#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path.cwd()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.mme_scalpx.replay.live_evidence_map import write_actual_evidence_maps


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate observe_only actual evidence map from market-session proof outputs."
    )
    parser.add_argument("--candidate-map", default="etc/replay/parity/observe_only_actual_generated_evidence_map_candidate_28g.json")
    parser.add_argument("--final-map", default="etc/replay/parity/observe_only_actual_generated_evidence_map.json")
    parser.add_argument("--missing-report", default="run/proofs/observe_only_actual_evidence_map_missing_report_28g.json")
    args = parser.parse_args()

    result = write_actual_evidence_maps(
        candidate_path=args.candidate_map,
        final_path=args.final_map,
        missing_report_path=args.missing_report,
    )
    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
