#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services.feature_family import (
    mist_surface,
    misb_surface,
    misc_surface,
    misr_surface,
    miso_surface,
)

MODULES = {
    "MIST": mist_surface,
    "MISB": misb_surface,
    "MISC": misc_surface,
    "MISR": misr_surface,
    "MISO": miso_surface,
}


def _expect_reject(label: str, fn: Callable[[], Any]) -> dict[str, Any]:
    try:
        fn()
    except Exception as exc:
        return {"case": label, "status": "PASS", "error": str(exc)}
    return {"case": label, "status": "FAIL", "error": "accepted invalid input"}


def _expect_pass(label: str, fn: Callable[[], Any]) -> dict[str, Any]:
    try:
        value = fn()
    except Exception as exc:
        return {"case": label, "status": "FAIL", "error": f"{type(exc).__name__}: {exc}"}
    return {"case": label, "status": "PASS", "value": value}


def _runtime(mode: str) -> dict[str, Any]:
    return {"runtime_mode": mode}


def _futures() -> dict[str, Any]:
    return {
        "present": True,
        "selected_features": {
            "present": True,
            "ltp": 22500.0,
            "delta_3": 2.0,
            "velocity_ratio": 2.0,
            "weighted_ofi": 0.80,
            "weighted_ofi_persist": 0.80,
            "vwap_distance": 2.0,
            "volume_norm": 2.0,
            "event_rate_spike_ratio": 2.0,
            "direction_score": 1.0,
            "ema9_slope": 1.0,
            "cvd_delta": 1.0,
            "spread_ratio": 1.0,
            "book_pressure": 0.8,
            "nof": 0.12,
        },
    }


def _option(side: str = N.SIDE_CALL) -> dict[str, Any]:
    return {
        "present": True,
        "selected_features": {
            "present": True,
            "ltp": 100.0,
            "delta_3": 2.0 if side == N.SIDE_CALL else -2.0,
            "velocity_ratio": 2.0,
            "weighted_ofi": 0.80 if side == N.SIDE_CALL else 0.20,
            "response_efficiency": 1.0,
            "spread_ratio": 1.0,
            "depth_total": 500,
            "ofi_ratio_proxy": 0.80 if side == N.SIDE_CALL else 0.20,
            "volume": 1000,
            "option_side": side,
        },
        "context_features": {
            "context_score": 0.8,
            "oi_bias": "NEUTRAL",
        },
        "premium_health": {"tradability_ok": True},
        "shadow_features": {"support_count": 2},
    }


def _base_kwargs(family: str, *, branch_id: str, mode: str, provider_ready: bool = True) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "branch_id": branch_id,
        "futures_surface": _futures(),
        "option_surface": _option(N.SIDE_CALL if branch_id == N.BRANCH_CALL else N.SIDE_PUT),
        "tradability_surface": {"entry_pass": True, "tradability_ok": True},
        "regime_surface": {"regime": "NORMAL"},
        "runtime_mode_surface": _runtime(mode),
        "thresholds": {},
        "provider_ready": provider_ready,
    }

    if family in {"MIST", "MISB", "MISC", "MISR"}:
        kwargs["fallback_option_surface"] = _option(N.SIDE_CALL if branch_id == N.BRANCH_CALL else N.SIDE_PUT)
        kwargs["strike_surface"] = {"present": True, "selection_mode_hint": "ATM"}

    if family == "MISR":
        kwargs["zone_registry_surface"] = {
            "present": True,
            "active_call_zone": {
                "zone_id": "orb-low",
                "zone_type": "ORB_LOW",
                "side_bias": "DOWNSIDE_TRAP",
                "trap_zone_level": 22490.0,
                "zone_low": 22490.0,
                "zone_high": 22495.0,
                "quality_score": 1.0,
            },
            "active_put_zone": {
                "zone_id": "orb-high",
                "zone_type": "ORB_HIGH",
                "side_bias": "UPSIDE_TRAP",
                "trap_zone_level": 22510.0,
                "zone_low": 22505.0,
                "zone_high": 22510.0,
                "quality_score": 1.0,
            },
        }

    if family == "MISO":
        kwargs["strike_surface"] = {
            "present": True,
            "selected": {"strike": 22500, "side": branch_id},
            "monitored": [{"strike": 22400}, {"strike": 22450}, {"strike": 22500}, {"strike": 22550}, {"strike": 22600}],
            "tradable": [{"strike": 22450}, {"strike": 22500}, {"strike": 22550}],
            "shadow": [{"strike": 22400}, {"strike": 22600}],
        }

    return kwargs


def _branch_builder(module: Any, family: str) -> Callable[..., Mapping[str, Any]]:
    return getattr(module, f"build_{family.lower()}_branch_surface")


def _family_builder(module: Any, family: str) -> Callable[..., Mapping[str, Any]]:
    return getattr(module, f"build_{family.lower()}_family_surface")


def _assert_jsonable(value: Any) -> str:
    return json.dumps(value, sort_keys=True)


def main() -> int:
    cases: list[dict[str, Any]] = []

    for family, module in MODULES.items():
        branch_fn = _branch_builder(module, family)
        family_fn = _family_builder(module, family)

        cases.append(
            _expect_reject(
                f"{family}_invalid_branch_rejected",
                lambda fn=branch_fn, fam=family: fn(**_base_kwargs(fam, branch_id="BAD_BRANCH", mode="NORMAL")),
            )
        )

        disabled_branch = branch_fn(
            **_base_kwargs(
                family,
                branch_id=N.BRANCH_CALL,
                mode=getattr(N, "STRATEGY_RUNTIME_MODE_DISABLED", "DISABLED"),
            )
        )
        cases.append(
            {
                "case": f"{family}_disabled_runtime_fail_closed_branch",
                "status": "PASS"
                if disabled_branch["branch_ready"] is False
                and disabled_branch["eligible"] is False
                and disabled_branch["failed_stage"] == "runtime_disabled"
                else "FAIL",
                "surface": disabled_branch,
            }
        )

        provider_false_branch = branch_fn(
            **_base_kwargs(
                family,
                branch_id=N.BRANCH_CALL,
                mode="NORMAL" if family != "MISO" else getattr(N, "STRATEGY_RUNTIME_MODE_BASE_5DEPTH", "BASE_5DEPTH"),
                provider_ready=False,
            )
        )
        cases.append(
            {
                "case": f"{family}_provider_not_ready_fail_closed_branch",
                "status": "PASS"
                if provider_false_branch["branch_ready"] is False
                and provider_false_branch["eligible"] is False
                and provider_false_branch["failed_stage"] == "provider_not_ready"
                else "FAIL",
                "surface": provider_false_branch,
            }
        )

        fake_ready_call = {
            "present": True,
            "branch_ready": True,
            "eligible": True,
            "context_pass": True,
            "option_tradability_pass": True,
            "setup_score": 99.0,
            "failed_stage": "context_pass",
        }
        fake_not_ready_put = {
            "present": True,
            "branch_ready": False,
            "eligible": False,
            "context_pass": False,
            "option_tradability_pass": True,
            "setup_score": 1.0,
            "failed_stage": "context_pass",
        }
        family_surface = family_fn(
            call_surface=fake_ready_call,
            put_surface=fake_not_ready_put,
            runtime_mode_surface=_runtime("NORMAL" if family != "MISO" else getattr(N, "STRATEGY_RUNTIME_MODE_BASE_5DEPTH", "BASE_5DEPTH")),
            regime_surface={"regime": "NORMAL"},
        )
        cases.append(
            {
                "case": f"{family}_family_ignores_failed_branch_even_with_high_score",
                "status": "PASS"
                if family_surface["eligible"] is False
                and family_surface["dominant_branch"] == ""
                and family_surface.get("dominant_ready_branch", "") == ""
                else "FAIL",
                "surface": family_surface,
            }
        )

        disabled_family = family_fn(
            call_surface={
                "present": True,
                "branch_ready": True,
                "eligible": True,
                "context_pass": True,
                "option_tradability_pass": True,
                "setup_score": 10.0,
                "failed_stage": "",
                "strike_bundle_present": True,
            },
            put_surface={},
            runtime_mode_surface=_runtime(getattr(N, "STRATEGY_RUNTIME_MODE_DISABLED", "DISABLED")),
            regime_surface={"regime": "NORMAL"},
        )
        cases.append(
            {
                "case": f"{family}_disabled_runtime_fail_closed_family",
                "status": "PASS"
                if disabled_family["eligible"] is False
                and disabled_family["dominant_branch"] == ""
                else "FAIL",
                "surface": disabled_family,
            }
        )

        cases.append(
            {
                "case": f"{family}_surface_json_serializable",
                "status": "PASS" if _assert_jsonable(disabled_family) else "FAIL",
            }
        )

    miso_family = miso_surface.build_miso_family_surface(
        call_surface={
            "present": True,
            "branch_ready": True,
            "eligible": True,
            "context_pass": True,
            "option_tradability_pass": True,
            "setup_score": 10.0,
            "failed_stage": "",
            "strike_bundle_present": False,
        },
        put_surface={},
        runtime_mode_surface=_runtime(getattr(N, "STRATEGY_RUNTIME_MODE_BASE_5DEPTH", "BASE_5DEPTH")),
        regime_surface={"regime": "NORMAL"},
    )
    cases.append(
        {
            "case": "MISO_family_requires_chain_or_strike_context",
            "status": "PASS"
            if miso_family["eligible"] is False
            and miso_family["chain_context_ready"] is False
            and miso_family["selected_side"] is None
            else "FAIL",
            "surface": miso_family,
        }
    )

    missing_batch9 = [
        family for family, module in MODULES.items()
        if not hasattr(module, "_BATCH9_SURFACE_HARDENING_VERSION")
    ]
    cases.append(
        {
            "case": "all_surface_modules_have_batch9_hardening_marker",
            "status": "PASS" if not missing_batch9 else "FAIL",
            "missing": missing_batch9,
        }
    )

    failed = [case for case in cases if case.get("status") != "PASS"]
    proof = {
        "proof": "feature_family_surfaces_batch9_freeze",
        "status": "FAIL" if failed else "PASS",
        "failed_cases": failed,
        "cases": cases,
    }

    out = PROJECT_ROOT / "run" / "proofs" / "feature_family_surfaces_batch9_freeze.json"
    out.write_text(json.dumps(proof, indent=2, sort_keys=True))
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
