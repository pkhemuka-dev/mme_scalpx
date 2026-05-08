#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.replay.raw_source_lineage import inject_source_lineage


rows = [
    ("run/replay/source/mist_call_source_row.json", {"row_kind": "TRADE", "net_pnl_after_costs": 206.25, "decision_action": "ENTER_CALL"}),
    ("run/replay/source/misc_put_candidate.json", {"artifact_kind": "CANDIDATE", "action": "ENTER_PE"}),
]

out = [inject_source_lineage(row, source_artifact=src) for src, row in rows]
ok = (
    out[0].get("family") == "MIST"
    and out[0].get("side") == "CALL"
    and out[0].get("strategy_id") == "MIST_CALL"
    and out[1].get("family") == "MISC"
    and out[1].get("side") == "PUT"
    and out[1].get("strategy_id") == "MISC_PUT"
    and all(x.get("raw_x_source_lineage_applied") is True for x in out)
)

print(json.dumps({"ok": ok, "outputs": out}, indent=2, sort_keys=True))
raise SystemExit(0 if ok else 2)
