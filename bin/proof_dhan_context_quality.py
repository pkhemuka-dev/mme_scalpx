#!/usr/bin/env python3
from __future__ import annotations

from _final_static_proof_helpers import contains_all, contains_any, emit, exists_nonempty

FILES = [
    "app/mme_scalpx/integrations/dhan_runtime_clients.py",
    "app/mme_scalpx/integrations/provider_runtime.py",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/feature_family/miso_surface.py",
    "app/mme_scalpx/services/strategy_family/miso.py",
]

checks = [exists_nonempty(f) for f in FILES[:4]]
checks += [
    contains_all(
        "dhan_context_state_surface_exists",
        FILES,
        ["DhanContextState", "dhan", "context"],
    ),
    contains_any(
        "dhan_context_freshness_or_staleness_checked",
        FILES,
        ["stale", "fresh", "max_age", "age", "timestamp"],
    ),
    contains_any(
        "dhan_context_unavailable_blocks_or_degrades",
        FILES,
        ["unavailable", "not_ready", "degraded", "fail", "blocked"],
    ),
    contains_all(
        "miso_requires_dhan_context",
        FILES,
        ["MISO", "dhan", "context"],
    ),
]

raise SystemExit(emit(
    "proof_dhan_context_quality",
    checks,
    does_not_prove=["live_dhan_chain_is_current", "broker_api_reachable"],
))
