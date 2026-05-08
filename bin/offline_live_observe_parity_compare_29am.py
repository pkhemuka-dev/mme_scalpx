#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

def main() -> int:
    proof = ROOT / "run" / "proofs" / "proof_offline_live_observe_parity_compare_29am_latest.json"
    if not proof.exists():
        print("29AM proof not found; run /tmp/batch29am_live_observe_bundle_compare_executor.py first")
        return 2
    obj = json.loads(proof.read_text(encoding="utf-8"))
    print(json.dumps({
        "verdict": obj.get("verdict"),
        "blockers": obj.get("blockers"),
        "comparison_summary": obj.get("comparison_summary"),
        "comparison_json": obj.get("comparison_json"),
        "comparison_csv": obj.get("comparison_csv"),
        "paper_armed_approved": obj.get("paper_armed_approved"),
        "live_trading_approved": obj.get("live_trading_approved"),
    }, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
