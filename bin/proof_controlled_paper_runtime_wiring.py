#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/Lenovo/scalpx/projects/mme_scalpx")
os.chdir(ROOT)

ROOT_STR = str(ROOT)
if ROOT_STR not in sys.path:
    sys.path.insert(0, ROOT_STR)

OUT = ROOT / "run/proofs/proof_controlled_paper_runtime_wiring.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

os.environ["SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME"] = "1"
os.environ["SCALPX_CONTROLLED_PAPER_SCOPE_ACK"] = "I_ACCEPT_MIST_CALL_1LOT_PAPER_ONLY"

from app.mme_scalpx.services.controlled_paper_runtime import controlled_runtime_report

strategy_text = (ROOT / "app/mme_scalpx/services/strategy.py").read_text(
    encoding="utf-8",
    errors="replace",
)

static_report = controlled_runtime_report(ignore_time_gate=True)
live_report = controlled_runtime_report(ignore_time_gate=False)

processes = subprocess.run(
    ["bash", "-lc", "pgrep -af 'app.mme_scalpx.main|pfeeds|mme_scalpx' || true"],
    cwd=ROOT,
    text=True,
    capture_output=True,
).stdout

checks = {
    "static_runtime_truth_ok": static_report.get("enabled") is True,
    "scope_mist": static_report.get("selected_family") == "MIST",
    "scope_call": static_report.get("selected_side") == "CALL",
    "scope_one_lot": static_report.get("quantity_lots") == 1,
    "real_live_false": static_report.get("real_live_allowed") is False,
    "paper_orders_allowed": static_report.get("paper_orders_allowed") is True,
    "no_auto_failover": static_report.get("automatic_broker_failover_allowed") is False,
    "no_mid_position_migration": static_report.get("mid_position_provider_migration_allowed") is False,
    "stop_after_first": static_report.get("auto_stop_after_first_paper_order") is True,
    "forced_flatten": static_report.get("forced_flatten_active") is True,
    "kill_switch": static_report.get("kill_switch_active") is True,
    "strategy_promotion_guard_installed": "controlled_strategy_promotion_enabled" in strategy_text,
    "order_adapter_guard_installed": "controlled_order_intent_adapter_enabled" in strategy_text,
    "no_plain_promotion_true": "ACTIVATION_ALLOW_CANDIDATE_PROMOTION: Final[bool] = True" not in strategy_text,
    "no_plain_adapter_true": "STRATEGY_ORDER_INTENT_ADAPTER_ENABLED = True" not in strategy_text,
}

proof = {
    "proof": "proof_controlled_paper_runtime_wiring",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "proof_controlled_paper_runtime_wiring_ok": all(checks.values()),
    "checks": checks,
    "static_runtime_report_ignore_time_gate": static_report,
    "live_runtime_report_with_time_gate": live_report,
    "processes": processes,
    "real_live_allowed": False,
    "selected_family": "MIST",
    "selected_side": "CALL",
    "quantity_lots": 1,
    "note": "Static wiring proof may pass after hours. live_runtime_report_with_time_gate must refuse outside 09:15-15:10 IST.",
}

OUT.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

print(json.dumps({
    "proof_controlled_paper_runtime_wiring_ok": proof["proof_controlled_paper_runtime_wiring_ok"],
    "checks": checks,
    "live_runtime_report_with_time_gate": live_report,
    "proof_path": str(OUT.relative_to(ROOT)),
}, indent=2, sort_keys=True))

raise SystemExit(0 if proof["proof_controlled_paper_runtime_wiring_ok"] else 1)
