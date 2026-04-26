#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT_STR = str(PROJECT_ROOT)
if PROJECT_ROOT_STR not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_STR)

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services import features as F


class StubRedis:
    def __init__(self, hashes: dict[str, dict[str, Any]]):
        self.hashes = hashes

    def hgetall(self, key: str) -> dict[str, Any]:
        return dict(self.hashes.get(key, {}))


def _provider_runtime_hash() -> dict[str, Any]:
    return {
        "futures_marketdata_provider_id": getattr(N, "PROVIDER_ZERODHA", "ZERODHA"),
        "selected_option_marketdata_provider_id": getattr(N, "PROVIDER_DHAN", "DHAN"),
        "option_context_provider_id": getattr(N, "PROVIDER_DHAN", "DHAN"),
        "execution_primary_provider_id": getattr(N, "PROVIDER_ZERODHA", "ZERODHA"),
        "execution_fallback_provider_id": getattr(N, "PROVIDER_DHAN", "DHAN"),
        "futures_marketdata_status": getattr(N, "PROVIDER_STATUS_HEALTHY", "HEALTHY"),
        "selected_option_marketdata_status": getattr(N, "PROVIDER_STATUS_HEALTHY", "HEALTHY"),
        "option_context_status": getattr(N, "PROVIDER_STATUS_HEALTHY", "HEALTHY"),
        "execution_primary_status": getattr(N, "PROVIDER_STATUS_HEALTHY", "HEALTHY"),
        "execution_fallback_status": getattr(N, "PROVIDER_STATUS_DEGRADED", "DEGRADED"),
        "family_runtime_mode": getattr(N, "FAMILY_RUNTIME_MODE_OBSERVE_ONLY", "observe_only"),
        "failover_mode": getattr(N, "PROVIDER_FAILOVER_MODE_MANUAL", "MANUAL"),
        "override_mode": getattr(N, "PROVIDER_OVERRIDE_MODE_AUTO", "AUTO"),
        "transition_reason": getattr(N, "PROVIDER_TRANSITION_REASON_BOOTSTRAP", "BOOTSTRAP"),
        "provider_transition_seq": 1,
        "failover_active": False,
        "pending_failover": False,
        "classic_runtime_mode": "NORMAL",
        "miso_runtime_mode": "BASE_5DEPTH",
    }


def _member(
    *,
    role: str,
    token: str,
    symbol: str,
    ltp: float,
    bid: float,
    ask: float,
    bid_qty_5: int,
    ask_qty_5: int,
    side: str | None,
    strike: float | None,
    now_ns: int,
) -> dict[str, Any]:
    out = {
        "role": role,
        "instrument_token": token,
        "trading_symbol": symbol,
        "ts_event_ns": now_ns,
        "ltp": ltp,
        "best_bid": bid,
        "best_ask": ask,
        "bid_qty_5": bid_qty_5,
        "ask_qty_5": ask_qty_5,
        "spread": max(0.0, ask - bid),
        "age_ms": 5,
        "tick_size": 0.05,
        "lot_size": 75,
        "validity": "OK",
        "velocity_ratio": 1.25,
        "volume_norm": 1.3,
        "weighted_ofi": 0.58 if side != getattr(N, "SIDE_PUT", "PUT") else 0.42,
        "weighted_ofi_persist": 0.57 if side != getattr(N, "SIDE_PUT", "PUT") else 0.43,
        "delta_3": 0.55 if side == getattr(N, "SIDE_CALL", "CALL") else -0.55 if side == getattr(N, "SIDE_PUT", "PUT") else 0.0,
        "response_efficiency": 0.45,
        "vwap": ltp - 1.0,
        "vol_norm": 1.3,
    }
    if side is not None:
        out["side"] = side
        out["option_side"] = side
    if strike is not None:
        out["strike"] = strike
    return out


def _dhan_context(now_ns: int) -> dict[str, Any]:
    call = {
        "side": getattr(N, "SIDE_CALL", "CALL"),
        "strike": 25000.0,
        "instrument_key": "CALL-25L",
        "instrument_token": "CALL-25L",
        "trading_symbol": "NIFTY-25000-CE-25L",
        "ltp": 110.0,
        "best_bid": 109.95,
        "best_ask": 110.05,
        "bid_qty_5": 900,
        "ask_qty_5": 800,
        "volume": 10000,
        "oi": 12000,
        "oi_change": 500,
        "iv": 12.5,
        "delta": 0.55,
        "spread_ratio": 0.08,
        "score": 0.85,
        "provider_id": getattr(N, "PROVIDER_DHAN", "DHAN"),
        "ts_event_ns": now_ns,
    }
    put = {
        "side": getattr(N, "SIDE_PUT", "PUT"),
        "strike": 25000.0,
        "instrument_key": "PUT-25L",
        "instrument_token": "PUT-25L",
        "trading_symbol": "NIFTY-25000-PE-25L",
        "ltp": 105.0,
        "best_bid": 104.95,
        "best_ask": 105.05,
        "bid_qty_5": 850,
        "ask_qty_5": 750,
        "volume": 10000,
        "oi": 13000,
        "oi_change": 550,
        "iv": 12.8,
        "delta": -0.55,
        "spread_ratio": 0.08,
        "score": 0.84,
        "provider_id": getattr(N, "PROVIDER_DHAN", "DHAN"),
        "ts_event_ns": now_ns,
    }
    rows = [call, put]
    wall = {
        "present": True,
        "ladder_size": len(rows),
        "has_call_rows": True,
        "has_put_rows": True,
        "call_wall": call,
        "put_wall": put,
        "nearest_call_oi_resistance_strike": 25000.0,
        "nearest_put_oi_support_strike": 25000.0,
        "call_wall_distance_pts": 0.0,
        "put_wall_distance_pts": 0.0,
        "call_wall_strength_score": 1.0,
        "put_wall_strength_score": 1.0,
        "oi_bias": "NEUTRAL",
        "oi_wall_ready": True,
    }
    return {
        "context_status": getattr(N, "PROVIDER_STATUS_HEALTHY", "HEALTHY"),
        "status": getattr(N, "PROVIDER_STATUS_HEALTHY", "HEALTHY"),
        "ts_event_ns": now_ns,
        "atm_strike": 25000.0,
        "selected_call_instrument_key": "CALL-25L",
        "selected_put_instrument_key": "PUT-25L",
        "selected_call_context_json": json.dumps(call, separators=(",", ":")),
        "selected_put_context_json": json.dumps(put, separators=(",", ":")),
        "option_chain_ladder_json": json.dumps(rows, separators=(",", ":")),
        "strike_ladder_json": json.dumps(rows, separators=(",", ":")),
        "oi_wall_summary_json": json.dumps(wall, separators=(",", ":")),
        "nearest_call_oi_resistance_strike": 25000.0,
        "nearest_put_oi_support_strike": 25000.0,
        "call_wall_distance_pts": 0.0,
        "put_wall_distance_pts": 0.0,
        "call_wall_strength_score": 1.0,
        "put_wall_strength_score": 1.0,
        "oi_bias": "NEUTRAL",
        "depth20_ready": False,
    }


def _is_rich_branch(surface: dict[str, Any], family_id: str, branch_id: str) -> bool:
    return bool(
        surface
        and surface.get("family_id") == family_id
        and surface.get("branch_id") == branch_id
        and str(surface.get("surface_kind", "")).endswith("_branch")
        and isinstance(surface.get("futures_features"), dict)
        and isinstance(surface.get("selected_features"), dict)
        and isinstance(surface.get("tradability"), dict)
        and isinstance(surface.get("regime_surface"), dict)
        and surface.get("rich_surface") is True
    )


def main() -> int:
    now_ns = time.time_ns()

    fut_member = _member(
        role="FUTURES",
        token="FUT-25L",
        symbol="NIFTY-FUT-25L",
        ltp=25000.0,
        bid=24999.95,
        ask=25000.05,
        bid_qty_5=1200,
        ask_qty_5=1000,
        side=None,
        strike=None,
        now_ns=now_ns,
    )
    call_member = _member(
        role="CE_ATM",
        token="CALL-25L",
        symbol="NIFTY-25000-CE-25L",
        ltp=110.0,
        bid=109.95,
        ask=110.05,
        bid_qty_5=900,
        ask_qty_5=800,
        side=getattr(N, "SIDE_CALL", "CALL"),
        strike=25000.0,
        now_ns=now_ns,
    )
    put_member = _member(
        role="PE_ATM",
        token="PUT-25L",
        symbol="NIFTY-25000-PE-25L",
        ltp=105.0,
        bid=104.95,
        ask=105.05,
        bid_qty_5=850,
        ask_qty_5=750,
        side=getattr(N, "SIDE_PUT", "PUT"),
        strike=25000.0,
        now_ns=now_ns,
    )

    hashes = {
        F.HASH_PROVIDER_RUNTIME: _provider_runtime_hash(),
        F.HASH_FUT_ACTIVE: {
            "instrument_key": getattr(N, "IK_MME_FUT", "NIFTY_FUT"),
            "provider_id": getattr(N, "PROVIDER_ZERODHA", "ZERODHA"),
            "future_json": json.dumps(fut_member, separators=(",", ":")),
            "bid_qty_5": 1200,
            "ask_qty_5": 1000,
            "validity": "OK",
            "sync_ok": "1",
        },
        F.HASH_OPT_ACTIVE: {
            "provider_id": getattr(N, "PROVIDER_DHAN", "DHAN"),
            "context_status": "OK",
            "selected_call_instrument_key": "CALL-25L",
            "selected_put_instrument_key": "PUT-25L",
            "selected_call_json": json.dumps(call_member, separators=(",", ":")),
            "selected_put_json": json.dumps(put_member, separators=(",", ":")),
            "ce_atm_json": json.dumps(call_member, separators=(",", ":")),
            "pe_atm_json": json.dumps(put_member, separators=(",", ":")),
            "ce_atm1_json": "null",
            "pe_atm1_json": "null",
            "validity": "OK",
            "sync_ok": "1",
        },
        F.HASH_DHAN_CONTEXT: _dhan_context(now_ns),
    }

    # Add optional Dhan-specific frame hashes only if the features module exposes them.
    if hasattr(F, "HASH_DHAN_FUTURES"):
        hashes[getattr(F, "HASH_DHAN_FUTURES")] = hashes[F.HASH_FUT_ACTIVE]
    if hasattr(F, "HASH_DHAN_SELECTED_OPTION"):
        hashes[getattr(F, "HASH_DHAN_SELECTED_OPTION")] = hashes[F.HASH_OPT_ACTIVE]

    engine = F.FeatureEngine(redis_client=StubRedis(hashes))
    payload = engine.build_payload(now_ns=now_ns)

    family_surfaces = payload["family_surfaces"]
    surfaces_by_branch = family_surfaces["surfaces_by_branch"]
    families = family_surfaces["families"]
    audit = F._builder_abi_audit_snapshot()

    expected_families = (
        getattr(N, "STRATEGY_FAMILY_MIST", "MIST"),
        getattr(N, "STRATEGY_FAMILY_MISB", "MISB"),
        getattr(N, "STRATEGY_FAMILY_MISC", "MISC"),
        getattr(N, "STRATEGY_FAMILY_MISR", "MISR"),
        getattr(N, "STRATEGY_FAMILY_MISO", "MISO"),
    )
    expected_branches = (
        getattr(N, "BRANCH_CALL", "CALL"),
        getattr(N, "BRANCH_PUT", "PUT"),
    )

    branch_checks: dict[str, bool] = {}
    for family_id in expected_families:
        for branch_id in expected_branches:
            key = f"{family_id.lower()}_{branch_id.lower()}"
            branch_checks[f"{family_id}_{branch_id}_rich_surface"] = _is_rich_branch(
                dict(surfaces_by_branch.get(key, {})),
                family_id,
                branch_id,
            )

    family_root_checks = {
        f"{family_id}_root_rich_surface": bool(
            isinstance(families.get(family_id), dict)
            and families[family_id].get("family_id") == family_id
            and families[family_id].get("rich_surface") is True
            and isinstance(families[family_id].get("branches"), dict)
        )
        for family_id in expected_families
    }

    checks = {
        **branch_checks,
        **family_root_checks,
        "family_branch_builder_used_count": audit.get("family_branch_builder_used", 0) >= 10,
        "family_root_builder_used_count": audit.get("family_root_builder_used", 0) >= 5,
        "no_exact_builder_exception": audit.get("exact_builder_exception_count", 0) == 0,
        "no_optional_call_first_typeerror": audit.get("call_first_typeerror_count", 0) == 0,
        "no_builder_fallback": audit.get("fallback_builder_count", 0) == 0,
        "no_missing_family_branch_surface": audit.get("family_branch_builder_missing_surface", 0) == 0,
        "no_missing_family_root_surface": audit.get("family_root_builder_missing_surface", 0) == 0,
        "observe_only_remains_default": payload["family_features"]["provider_runtime"].get("family_runtime_mode")
        == getattr(N, "FAMILY_RUNTIME_MODE_OBSERVE_ONLY", "observe_only"),
    }

    proof_ok = all(checks.values())

    proof = {
        "proof_name": "proof_family_surface_service_path",
        "batch": "25L",
        "generated_at_ns": now_ns,
        "family_surface_service_path_ok": proof_ok,
        "checks": checks,
        "builder_abi_audit": audit,
        "families": {
            family_id: {
                "surface_kind": families.get(family_id, {}).get("surface_kind"),
                "family_id": families.get(family_id, {}).get("family_id"),
                "rich_surface": families.get(family_id, {}).get("rich_surface"),
                "eligible": families.get(family_id, {}).get("eligible"),
                "branches_keys": sorted((families.get(family_id, {}).get("branches") or {}).keys()),
            }
            for family_id in expected_families
        },
        "branches": {
            key: {
                "surface_kind": value.get("surface_kind"),
                "family_id": value.get("family_id"),
                "branch_id": value.get("branch_id"),
                "rich_surface": value.get("rich_surface"),
                "present": value.get("present"),
                "eligible": value.get("eligible"),
                "failed_stage": value.get("failed_stage"),
                "has_futures_features": isinstance(value.get("futures_features"), dict),
                "has_selected_features": isinstance(value.get("selected_features"), dict),
                "has_tradability": isinstance(value.get("tradability"), dict),
                "has_regime_surface": isinstance(value.get("regime_surface"), dict),
            }
            for key, value in surfaces_by_branch.items()
        },
    }

    out = Path("run/proofs/proof_family_surface_service_path.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "family_surface_service_path_ok": proof_ok,
        "family_branch_builder_used": audit.get("family_branch_builder_used", 0),
        "family_root_builder_used": audit.get("family_root_builder_used", 0),
        "no_exact_builder_exception": checks["no_exact_builder_exception"],
        "no_optional_call_first_typeerror": checks["no_optional_call_first_typeerror"],
        "no_builder_fallback": checks["no_builder_fallback"],
        "all_branch_rich_surfaces": all(branch_checks.values()),
        "all_root_rich_surfaces": all(family_root_checks.values()),
        "proof_path": str(out),
    }, indent=2, sort_keys=True))

    return 0 if proof_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
