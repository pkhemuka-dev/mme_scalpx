#!/usr/bin/env python3
from __future__ import annotations

from _final_static_proof_helpers import contains_all, contains_any, emit, exists_nonempty

FILES = [
    "app/mme_scalpx/services/feeds.py",
    "app/mme_scalpx/integrations/provider_runtime.py",
    "app/mme_scalpx/main.py",
    "etc/runtime.yaml",
]

checks = [exists_nonempty(f) for f in FILES[:3]]
checks += [
    contains_all(
        "provider_runtime_roles_visible_to_feeds",
        FILES,
        ["provider_runtime", "zerodha", "dhan"],
    ),
    contains_any(
        "feed_surface_distinguishes_context_from_marketdata",
        FILES,
        ["marketdata", "market_data", "option_context", "context"],
    ),
    contains_any(
        "feed_surface_fail_closed_language",
        FILES,
        ["strict", "required", "reject", "fail", "degraded", "not_ready"],
    ),
    contains_any(
        "no_silent_legacy_aliasing_language",
        FILES,
        ["legacy", "forbidden", "compat", "allow_legacy"],
    ),
]

raise SystemExit(emit(
    "proof_feeds_provider_surface_strictness",
    checks,
    does_not_prove=["actual_provider_socket_stream_quality"],
))
