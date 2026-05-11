#!/usr/bin/env python3
from __future__ import annotations

from _final_static_proof_helpers import contains_any, emit, exists_nonempty

FILES = [
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/report.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/core/names.py",
]

checks = [exists_nonempty(f) for f in FILES]
checks += [
    contains_any(
        "trade_ledger_surface_exists",
        FILES,
        ["trades:ledger", "TRADES_LEDGER", "ledger"],
    ),
    contains_any(
        "trade_id_or_event_id_used",
        FILES,
        ["trade_id", "event_id", "position_id", "order_id"],
    ),
    contains_any(
        "idempotency_or_duplicate_guard_language",
        FILES,
        ["duplicate", "idempot", "seen", "processed", "dedupe"],
    ),
    contains_any(
        "net_pnl_preferred_or_pnl_surface",
        FILES,
        ["net_pnl", "realized_pnl", "gross_pnl", "fees"],
    ),
]

raise SystemExit(emit(
    "proof_risk_trade_ledger_idempotency",
    checks,
    does_not_prove=["duplicate_live_redis_event_drill"],
))
