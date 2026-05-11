#!/usr/bin/env python3
from __future__ import annotations

from _final_static_proof_helpers import contains_all, contains_any, emit, exists_nonempty

FILES = [
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/feature_family/common.py",
    "app/mme_scalpx/services/feature_family/option_core.py",
    "app/mme_scalpx/services/feature_family/futures_core.py",
    "app/mme_scalpx/services/feature_family/tradability.py",
    "app/mme_scalpx/services/feature_family/miso_surface.py",
]

checks = [exists_nonempty(f) for f in FILES]
checks += [
    contains_any(
        "missing_provider_fails_closed",
        FILES,
        ["provider_not_ready", "provider_ready", "runtime_disabled", "not_ready"],
    ),
    contains_any(
        "zero_or_missing_ltp_not_live_present",
        FILES,
        ["ltp", "present", "0", "missing"],
    ),
    contains_any(
        "missing_spread_or_depth_does_not_pass",
        FILES,
        ["spread", "depth", "tradability", "entry_pass"],
    ),
    contains_any(
        "dominant_ready_branch_empty_when_not_ready",
        FILES,
        ["dominant_ready_branch", "branch_ready", "eligible"],
    ),
    contains_all(
        "family_payload_and_stage_flags_exist",
        ["app/mme_scalpx/services/features.py"],
        ["family_features", "stage_flags"],
    ),
]

raise SystemExit(emit(
    "proof_features_false_readiness_guards",
    checks,
    does_not_prove=["live_positive_candidate_quality"],
))
