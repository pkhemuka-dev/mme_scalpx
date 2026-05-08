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
    source = Path("app/mme_scalpx/services/features.py").read_text(encoding="utf-8")

    checks = {
        "direct_surface_helper_present": "def _direct_member_surface(" in source,
        "call_uses_call_member_keys": "_feed_first_member(raw_map, _FEED_CALL_JSON_KEYS)" in source,
        "put_uses_put_member_keys": "_feed_first_member(raw_map, _FEED_PUT_JSON_KEYS)" in source,
        "put_ce_contamination_direct_fallback": 'if put_member and put_symbol.endswith("CE")' in source,
        "call_pe_contamination_direct_fallback": 'if call_member and call_symbol.endswith("PE")' in source,
        "direct_surface_preserves_raw": '"raw": m' in source,
        "final_put_side_forced": 'put_surface["option_side"] = "PUT"' in source,
        "final_call_side_forced": 'call_surface["option_side"] = "CALL"' in source,
    }

    proof = {
        "proof_name": "proof_feature_side_direct_member_surface",
        "generated_at_ns": time.time_ns(),
        "feature_side_direct_member_surface_static_ok": all(checks.values()),
        "checks": checks,
        "proof_path": "run/proofs/proof_feature_side_direct_member_surface.json",
    }

    Path("run/proofs/proof_feature_side_direct_member_surface.json").write_text(
        json.dumps(proof, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0 if proof["feature_side_direct_member_surface_static_ok"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
