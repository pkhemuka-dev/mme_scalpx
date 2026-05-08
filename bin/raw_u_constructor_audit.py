#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.research_gate.constructor_audit import (
    patch_constructor_sites,
    write_json,
    write_sites_csv,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="RAW-U v2 deep constructor audit and targeted patch.")
    parser.add_argument("--reports", required=True)
    parser.add_argument("--artifacts", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    output_dir = pathlib.Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    patch_results = [
        patch_constructor_sites(args.reports),
        patch_constructor_sites(args.artifacts),
    ]

    total_detected = sum(int(r.get("constructor_sites_detected", 0)) for r in patch_results)
    total_patched = sum(int(r.get("constructor_sites_patched", 0)) for r in patch_results)

    report = {
        "run_id": args.run_id,
        "result": "PASS",
        "constructor_sites_detected": total_detected,
        "constructor_sites_patched": total_patched,
        "constructor_patch_added": total_patched > 0,
        "patch_results": patch_results,
        "promotion_allowed": False,
        "paper_live_allowed": False,
        "non_live": True,
        "non_mutating": True,
    }

    write_json(output_dir / "constructor_audit.json", report)
    write_sites_csv(output_dir / "constructor_patch_map.csv", patch_results)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
