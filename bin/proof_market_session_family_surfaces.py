#!/usr/bin/env python3
from __future__ import annotations

import json
import time

from _batch25v_market_observation_common import (
    branch_ids,
    build_all_static_guard_report,
    family_ids,
    family_surfaces_canonical_report,
    proof_path,
    redis_client,
    write_proof,
)


def _branch_key(family: str, branch: str) -> str:
    return f"{family.lower()}_{branch.lower()}"


def _is_rich(surface: dict) -> bool:
    return bool(
        surface
        and surface.get("rich_surface") is True
        and isinstance(surface.get("futures_features"), dict)
        and isinstance(surface.get("selected_features"), dict)
        and isinstance(surface.get("tradability"), dict)
        and isinstance(surface.get("regime_surface"), dict)
        and str(surface.get("surface_kind", "")).endswith("_branch")
    )


def main() -> int:
    from app.mme_scalpx.services import features as F
    from app.mme_scalpx.services.feature_family import contracts as C

    client = redis_client()
    engine = F.FeatureEngine(redis_client=client)
    payload = engine.build_payload(now_ns=time.time_ns())

    family_surfaces = dict(payload.get("family_surfaces") or {})
    surfaces_by_branch = dict(family_surfaces.get("surfaces_by_branch") or {})
    families = dict(family_surfaces.get("families") or {})
    audit = dict(family_surfaces.get("builder_abi_audit") or payload.get("shared_core", {}).get("builder_abi_audit") or {})

    branch_checks = {}
    surface_kind_checks = {}
    for family in family_ids():
        expected_kind = f"{family.lower()}_branch"
        for branch in branch_ids():
            key = _branch_key(family, branch)
            surface = dict(surfaces_by_branch.get(key) or {})
            branch_checks[f"{family}_{branch}_rich_surface"] = _is_rich(surface)
            surface_kind_checks[f"{family}_{branch}_surface_kind"] = surface.get("surface_kind") == expected_kind

    root_checks = {
        f"{family}_root_surface_present": bool(
            isinstance(families.get(family), dict)
            and dict(families[family]).get("rich_surface") is True
            and dict(families[family]).get("surface_kind") == f"{family.lower()}_family"
        )
        for family in family_ids()
    }

    canonical_report = family_surfaces_canonical_report(family_surfaces)
    static_guard = build_all_static_guard_report()

    contract_surface_kind_ok = True
    contract_surface_kind_error = None
    try:
        if hasattr(C, "validate_batch26h_surface_kinds"):
            C.validate_batch26h_surface_kinds(family_surfaces)
    except Exception as exc:
        contract_surface_kind_ok = False
        contract_surface_kind_error = str(exc)

    checks = {
        **branch_checks,
        **surface_kind_checks,
        **root_checks,
        "all_5_family_surfaces_rich": all(branch_checks.values()) and all(root_checks.values()),
        "all_branch_surface_kinds_final": all(surface_kind_checks.values()),
        "contract_surface_kind_validation_ok": contract_surface_kind_ok,
        "canonical_fields_present_on_branch_surfaces": bool(canonical_report.get("ok")),
        "producer_consumer_static_guard_ok": bool(static_guard.get("ok")),
        "no_family_builder_exception_observed": int(audit.get("exact_builder_exception_count", 0)) == 0,
        "no_optional_call_first_typeerror_observed": int(audit.get("call_first_typeerror_count", 0)) == 0,
    }

    ok = all(checks.values())

    proof = {
        "proof_name": "proof_market_session_family_surfaces",
        "batch": "25V/26I",
        "generated_at_ns": time.time_ns(),
        "market_session_family_surfaces_ok": ok,
        "checks": checks,
        "contract_surface_kind_error": contract_surface_kind_error,
        "canonical_surface_report": canonical_report,
        "static_guard_report": static_guard,
        "builder_abi_audit": audit,
        "surface_keys": sorted(surfaces_by_branch.keys()),
        "family_keys": sorted(families.keys()),
        "paper_armed_approved": False,
        "real_live_approved": False,
    }

    out = proof_path("proof_market_session_family_surfaces.json")
    write_proof(out, proof)
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
