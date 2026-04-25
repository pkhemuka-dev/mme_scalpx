#!/usr/bin/env python3
from __future__ import annotations

from _final_static_proof_helpers import contains_all, contains_any, emit, exists_nonempty

FILES = [
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/replay/engine.py",
    "app/mme_scalpx/replay/topology.py",
]

checks = [exists_nonempty(f) for f in FILES[:2]]
checks += [
    contains_all(
        "replay_prefix_contract_exists",
        FILES,
        ["replay", "state:risk"],
    ),
    contains_any(
        "risk_uses_live_and_replay_separation",
        FILES,
        ["replay:state", "replay", "live_keys_touched", "namespace"],
    ),
    contains_any(
        "replay_never_touches_live_guard",
        FILES,
        ["live_keys_touched", "reject", "forbidden", "namespace"],
    ),
]

raise SystemExit(emit(
    "proof_risk_replay_key_separation",
    checks,
    does_not_prove=["full_replay_end_to_end_run"],
))
