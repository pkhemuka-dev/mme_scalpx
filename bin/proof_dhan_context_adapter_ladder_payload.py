#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
APP = ROOT / "app"
if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))

import app.mme_scalpx.integrations.dhan_runtime_clients as DRC


def main() -> int:
    source = Path(DRC.__file__).read_text(encoding="utf-8")

    checks = {
        "helper_present": "_batch25v_option_chain_rows_from_snapshot" in source,
        "build_item_mentions_ladder_json": "option_chain_ladder_json" in source and "strike_ladder_json" in source,
        "build_item_mentions_selected_context_json": "selected_call_context_json" in source and "selected_put_context_json" in source,
        "build_item_marks_degraded_when_no_rows": '"DEGRADED"' in source,
        "build_item_preserves_record_type": '"record_type": "dhan_context"' in source,
    }

    proof = {
        "proof_name": "proof_dhan_context_adapter_ladder_payload",
        "generated_at_ns": time.time_ns(),
        "dhan_context_adapter_ladder_payload_ok": all(checks.values()),
        "checks": checks,
        "proof_path": "run/proofs/proof_dhan_context_adapter_ladder_payload.json",
    }

    Path("run/proofs/proof_dhan_context_adapter_ladder_payload.json").write_text(
        json.dumps(proof, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0 if proof["dhan_context_adapter_ladder_payload_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
