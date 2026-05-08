#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def main() -> int:
    source = Path("app/mme_scalpx/services/feeds.py").read_text(encoding="utf-8")

    checks = {
        "fallback_marker_present": "Batch 25V corrective — selected option member fallback" in source,
        "selected_call_json_still_written": 'payload["selected_call_json"]' in source,
        "selected_put_json_still_written": 'payload["selected_put_json"]' in source,
        "approved_map_match_preserved": "_token_to_approved.get(member.instrument_token)" in source,
        "fallback_uses_strike_match": "abs(member_strike - want_strike)" in source,
        "fallback_uses_symbol_match": "digits in symbol and symbol.endswith(want_side)" in source,
    }

    proof = {
        "proof_name": "proof_selected_option_active_bridge",
        "generated_at_ns": time.time_ns(),
        "selected_option_active_bridge_static_ok": all(checks.values()),
        "checks": checks,
        "proof_path": "run/proofs/proof_selected_option_active_bridge.json",
    }

    Path("run/proofs/proof_selected_option_active_bridge.json").write_text(
        json.dumps(proof, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0 if proof["selected_option_active_bridge_static_ok"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
