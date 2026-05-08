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
        {"source_artifact": "run/replay/sample/mist_call_trade.json", "row": {"row_kind": "TRADE", "decision_action": "ENTER_CALL"}},
        {"source_artifact": "run/replay/sample/misb_put_candidate.json", "row": {"row_kind": "CANDIDATE", "action": "ENTER_PE"}},
        {"source_artifact": "run/replay/sample/miso_call_report.json", "row": {"strategy_id": "miso_call", "side": "CE"}},
    ]
    outputs = []
    for item in samples:
        emitted = emit_family_context(item["row"], source_artifact=item["source_artifact"])
        outputs.append(emitted)
    ok = all(row.get("raw_s_producer_family_emission_applied") is True for row in outputs)
    print(json.dumps({"ok": ok, "outputs": outputs}, indent=2, sort_keys=True))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
