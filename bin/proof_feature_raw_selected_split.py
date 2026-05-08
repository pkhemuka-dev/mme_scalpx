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
        "marker_present": "Batch 25V corrective — split raw active_selected hash, not flattened opt_active" in source,
        "split_uses_active_selected": "call_opt, put_opt = self._split_options(active_selected, opt_dhan, dhan_context)" in source,
        "split_no_longer_uses_opt_active": "call_opt, put_opt = self._split_options(opt_active, opt_dhan, dhan_context)" not in source,
        "call_key_list_present": "_FEED_CALL_JSON_KEYS" in source and "selected_call_json" in source,
        "put_key_list_present": "_FEED_PUT_JSON_KEYS" in source and "selected_put_json" in source,
        "direct_member_surface_present": "def _direct_member_surface(" in source,
    }

    proof = {
        "proof_name": "proof_feature_raw_selected_split",
        "generated_at_ns": time.time_ns(),
        "feature_raw_selected_split_static_ok": all(checks.values()),
        "checks": checks,
        "proof_path": "run/proofs/proof_feature_raw_selected_split.json",
    }

    Path("run/proofs/proof_feature_raw_selected_split.json").write_text(
        json.dumps(proof, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0 if proof["feature_raw_selected_split_static_ok"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
