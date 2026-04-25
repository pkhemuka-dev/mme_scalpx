#!/usr/bin/env python3
from __future__ import annotations

from _final_static_proof_helpers import contains_any, emit, exists_nonempty

FILES = [
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
]

checks = [exists_nonempty(f) for f in FILES]
checks += [
    contains_any(
        "risk_state_hash_surface",
        FILES,
        ["state:risk", "KEY_STATE_RISK", "state_risk"],
    ),
    contains_any(
        "risk_rebuild_or_restore_language",
        FILES,
        ["restart", "restore", "rebuild", "recover", "ledger"],
    ),
    contains_any(
        "loss_count_and_pnl_surfaces",
        FILES,
        ["realized_pnl", "net_pnl", "consecutive", "daily_loss"],
    ),
    contains_any(
        "risk_heartbeat_surface",
        FILES,
        ["risk:heartbeat", "HEARTBEAT", "heartbeat"],
    ),
]

raise SystemExit(emit(
    "proof_risk_restart_rebuild",
    checks,
    does_not_prove=["live_restart_drill_completed"],
))
