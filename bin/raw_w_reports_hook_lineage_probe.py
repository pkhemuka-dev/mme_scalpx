#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.replay.raw_producer_family_emission import emit_family_context


def main() -> int:
    samples = [
        {
            "source_artifact": "run/replay/session/mist_call_trade_artifact.json",
            "row": {
                "row_kind": "TRADE",
                "net_pnl_after_costs": 206.25,
                "decision_action": "ENTER_CALL",
            },
        },
        {
            "source_artifact": "run/replay/session/misr_put_trade_artifact.json",
            "row": {
                "row_kind": "TRADE",
                "net_pnl_after_costs": -25.0,
                "action": "ENTER_PE",
            },
        },
        {
            "source_artifact": "run/replay/session/unknown_trade_artifact.json",
            "row": {
                "row_kind": "TRADE",
                "net_pnl_after_costs": 5.0,
            },
        },
    ]

    outputs = []
    for sample in samples:
        outputs.append(emit_family_context(sample["row"], source_artifact=sample["source_artifact"]))

    ok = (
        outputs[0]["family"] == "MIST"
        and outputs[0]["side"] == "CALL"
        and outputs[0]["strategy_id"] == "MIST_CALL"
        and not outputs[0]["candidate_id"].startswith("UNKNOWN")
        and outputs[1]["family"] == "MISR"
        and outputs[1]["side"] == "PUT"
        and outputs[1]["strategy_id"] == "MISR_PUT"
        and not outputs[1]["candidate_id"].startswith("UNKNOWN")
        and outputs[2]["family"] == "UNKNOWN"
        and outputs[2]["candidate_id"].startswith("RAW_W_SYNTH_")
        and all(row.get("raw_w_hook_lineage_applied") is True for row in outputs)
    )

    print(json.dumps({"ok": ok, "outputs": outputs}, indent=2, sort_keys=True))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
