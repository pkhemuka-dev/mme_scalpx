#!/usr/bin/env python3
from __future__ import annotations

from _final_static_proof_helpers import contains_all, contains_any, emit, exists_nonempty

FILES = [
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/feature_family/option_core.py",
    "app/mme_scalpx/integrations/provider_runtime.py",
    "app/mme_scalpx/integrations/dhan_runtime_clients.py",
]

checks = [exists_nonempty(f) for f in FILES]
checks += [
    contains_any(
        "active_option_marketdata_surface_present",
        FILES,
        ["selected_option", "active_option", "option_marketdata", "marketdata"],
    ),
    contains_any(
        "context_option_surface_separate",
        FILES,
        ["option_context", "context", "chain", "dhan"],
    ),
    contains_any(
        "context_not_substitute_for_live_marketdata",
        FILES,
        ["not_ready", "degraded", "unavailable", "provider_ready", "marketdata"],
    ),
    contains_any(
        "sync_or_staleness_threshold_present",
        FILES,
        ["sync", "stale", "timestamp", "max_age", "age"],
    ),
]

raise SystemExit(emit(
    "proof_features_active_vs_context_option_truth",
    checks,
    does_not_prove=["real_time_cross_provider_timestamp_alignment"],
))
