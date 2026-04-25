#!/usr/bin/env python3
from __future__ import annotations

from _final_static_proof_helpers import contains_all, contains_any, emit, exists_nonempty

FILES = [
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
]

checks = [exists_nonempty(f) for f in FILES]
checks += [
    contains_all(
        "hold_action_surface_present",
        FILES,
        ["HOLD", "ACK"],
    ),
    contains_any(
        "hold_does_not_order",
        FILES,
        ["no_order", "hold", "ack", "quantity", "qty"],
    ),
    contains_any(
        "enter_zero_qty_reject",
        FILES,
        ["qty", "quantity", "reject", "zero"],
    ),
    contains_any(
        "flat_payload_action_mismatch_reject",
        FILES,
        ["payload_json", "action", "mismatch", "reject"],
    ),
    contains_any(
        "broker_call_guarded",
        FILES,
        ["place_order", "broker", "live_orders", "disabled", "reject"],
    ),
]

raise SystemExit(emit(
    "proof_execution_hold_no_order",
    checks,
    does_not_prove=["actual_broker_not_called_in_external_monkeypatch"],
))
