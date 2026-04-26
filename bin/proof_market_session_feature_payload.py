#!/usr/bin/env python3
from __future__ import annotations

import json
import time

from _batch25v_market_observation_common import (
    build_all_static_guard_report,
    eligible_truth_ok,
    family_surfaces_canonical_report,
    proof_path,
    redis_client,
    safe_bool,
    safe_float,
    write_proof,
)


def main() -> int:
    from app.mme_scalpx.services import features as F

    client = redis_client()
    engine = F.FeatureEngine(redis_client=client)
    payload = engine.build_payload(now_ns=time.time_ns())

    shared = dict(payload.get("shared_core") or {})
    provider = dict(payload.get("family_features", {}).get("provider_runtime") or {})
    families = dict(payload.get("family_features", {}).get("families") or {})
    family_surfaces = dict(payload.get("family_surfaces") or {})

    futures = dict(shared.get("futures", {}).get("active") or {})
    options = dict(shared.get("options") or {})
    call = dict(options.get("call") or {})
    put = dict(options.get("put") or {})
    strike = dict(shared.get("strike_selection") or {})
    context_quality = dict(shared.get("context_quality") or shared.get("dhan_context_quality") or {})

    eligibility_ok, eligibility_report = eligible_truth_ok(families)
    canonical_surfaces = family_surfaces_canonical_report(family_surfaces)
    static_guard = build_all_static_guard_report()

    dhan_available = (
        str(provider.get("option_context_provider_id") or provider.get("active_option_context_provider_id")) == "DHAN"
        and str(provider.get("option_context_status") or provider.get("option_context_provider_status", "")).upper()
        not in {"", "UNAVAILABLE", "STALE", "DEAD", "ERROR", "FATAL"}
    )

    checks = {
        "feature_payload_present": bool(payload),
        "provider_runtime_present": bool(provider),
        "futures_present": safe_bool(futures.get("present"), False) or safe_float(futures.get("ltp"), 0.0) > 0.0,
        "futures_depth_consumed": safe_float(futures.get("depth_total"), 0.0) > 0.0,
        "missing_futures_not_valid": not (not futures and safe_bool(futures.get("present"), False)),
        "call_present": safe_bool(call.get("present"), False),
        "put_present": safe_bool(put.get("present"), False),
        "call_depth_consumed": safe_float(call.get("depth_total"), 0.0) > 0.0,
        "put_depth_consumed": safe_float(put.get("depth_total"), 0.0) > 0.0,
        "strike_context_present": bool(strike),
        "dhan_oi_context_fresh_when_available": (
            not dhan_available
            or safe_bool(context_quality.get("miso_context_ready"), False)
            or safe_float(strike.get("ladder_size"), 0.0) > 0.0
        ),
        "canonical_family_features_not_falsely_eligible": eligibility_ok,
        "family_surfaces_canonical_fields_present": bool(canonical_surfaces.get("ok")),
        "static_guard_matrix_ok": bool(static_guard.get("ok")),
    }

    ok = all(checks.values())

    proof = {
        "proof_name": "proof_market_session_feature_payload",
        "batch": "25V/26I",
        "generated_at_ns": time.time_ns(),
        "market_session_feature_payload_ok": ok,
        "checks": checks,
        "provider_runtime": provider,
        "context_quality": context_quality,
        "eligibility_report": eligibility_report,
        "canonical_surface_report": canonical_surfaces,
        "static_guard_report": static_guard,
        "observed": {
            "futures": futures,
            "call": call,
            "put": put,
            "strike_selection_summary": {
                "ladder_size": strike.get("ladder_size"),
                "chain_context_ready": strike.get("chain_context_ready"),
                "oi_bias": strike.get("oi_bias"),
            },
        },
        "paper_armed_approved": False,
        "real_live_approved": False,
    }

    out = proof_path("proof_market_session_feature_payload.json")
    write_proof(out, proof)
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
