#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import inspect
import json
import re
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path("/home/Lenovo/scalpx/projects/mme_scalpx")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PROOF_PATH = ROOT / "run/proofs/proof_oi_wall_authority_canonicalized.json"

TARGETS = [
    "app/mme_scalpx/services/feeds.py",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/feature_family/strike_selection.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/strategy_family/order_intent.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/core/models.py",
    "app/mme_scalpx/core/names.py",
]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8", errors="replace")


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def file_info(rel: str) -> dict[str, Any]:
    path = ROOT / rel
    if not path.exists():
        return {"path": rel, "present": False}
    text = read(rel)
    return {
        "path": rel,
        "present": True,
        "line_count": len(text.splitlines()),
        "sha256": sha(text),
    }


def lines(text: str, needle: str) -> list[int]:
    return [i for i, line in enumerate(text.splitlines(), 1) if needle in line]


def any_token(text: str, tokens: list[str]) -> bool:
    return any(token in text for token in tokens)


def false_checks(checks: dict[str, bool]) -> dict[str, bool]:
    return {k: v for k, v in checks.items() if v is False}


def canonical_smoke_exact_kwargs() -> dict[str, Any]:
    mod = importlib.import_module("app.mme_scalpx.services.feature_family.strike_selection")
    func = getattr(mod, "build_oi_wall_summary")
    sig = str(inspect.signature(func))

    rows = [
        {
            "strike": 22450,
            "side": "PUT",
            "option_type": "PE",
            "right": "PE",
            "oi": 30000,
            "open_interest": 30000,
            "oi_change": 5000,
            "change_in_oi": 5000,
            "volume": 1000,
            "bid": 80,
            "ask": 81,
            "best_bid": 80,
            "best_ask": 81,
            "ltp": 85,
            "iv": 11.5,
            "delta": -0.35,
            "gamma": 0.01,
        },
        {
            "strike": 22500,
            "side": "PUT",
            "option_type": "PE",
            "right": "PE",
            "oi": 100000,
            "open_interest": 100000,
            "oi_change": 10000,
            "change_in_oi": 10000,
            "volume": 2000,
            "bid": 90,
            "ask": 91,
            "best_bid": 90,
            "best_ask": 91,
            "ltp": 95,
            "iv": 12.0,
            "delta": -0.48,
            "gamma": 0.015,
        },
        {
            "strike": 22550,
            "side": "CALL",
            "option_type": "CE",
            "right": "CE",
            "oi": 120000,
            "open_interest": 120000,
            "oi_change": 15000,
            "change_in_oi": 15000,
            "volume": 2500,
            "bid": 95,
            "ask": 96,
            "best_bid": 95,
            "best_ask": 96,
            "ltp": 100,
            "iv": 12.2,
            "delta": 0.52,
            "gamma": 0.014,
        },
        {
            "strike": 22600,
            "side": "CALL",
            "option_type": "CE",
            "right": "CE",
            "oi": 60000,
            "open_interest": 60000,
            "oi_change": 4000,
            "change_in_oi": 4000,
            "volume": 1200,
            "bid": 70,
            "ask": 71,
            "best_bid": 70,
            "best_ask": 71,
            "ltp": 75,
            "iv": 11.8,
            "delta": 0.37,
            "gamma": 0.01,
        },
    ]

    rows_json = json.dumps(rows)
    dhan_context = {
        "atm_strike": 22500,
        "underlying_atm": 22500,
        "reference_strike": 22500,
        "strike_ladder_json": rows_json,
        "option_chain_ladder_json": rows_json,
        "strike_ladder": rows,
        "option_chain_ladder": rows,
        "strike_ladder_rows": rows,
        "chain_rows": rows,
        "rows": rows,
        "ladder": rows,
    }
    futures_features = {
        "ltp": 22500,
        "fut_ltp": 22500,
        "atm_strike": 22500,
    }
    selected_features = {
        "strike": 22500,
        "opt_strike": 22500,
        "side": "CALL",
    }

    attempts: list[dict[str, Any]] = []

    call_shapes = [
        (
            "exact_contract_kwargs",
            {},
            {
                "dhan_context": dhan_context,
                "futures_features": futures_features,
                "selected_features": selected_features,
            },
        ),
        (
            "exact_contract_kwargs_with_ladder",
            {},
            {
                "dhan_context": dhan_context,
                "futures_features": futures_features,
                "selected_features": selected_features,
                "strike_ladder": rows,
            },
        ),
        (
            "positional_context_plus_exact_kwargs",
            (dhan_context,),
            {
                "dhan_context": dhan_context,
                "futures_features": futures_features,
                "selected_features": selected_features,
            },
        ),
    ]

    last_out: Any = None

    for mode, args, kwargs in call_shapes:
        try:
            out = func(*args, **kwargs)
            last_out = out
            result_keys = sorted(out.keys()) if isinstance(out, dict) else []
            ok = False
            if isinstance(out, dict):
                wall_ready_surface = any(
                    key in out
                    for key in (
                        "oi_wall_ready",
                        "wall_computable",
                        "call_wall",
                        "put_wall",
                        "nearest_call_oi_resistance_strike",
                        "nearest_put_oi_support_strike",
                    )
                )
                call_surface = bool(
                    out.get("call_wall")
                    or out.get("nearest_call_oi_resistance_strike")
                    or out.get("nearest_call_oi_resistance")
                )
                put_surface = bool(
                    out.get("put_wall")
                    or out.get("nearest_put_oi_support_strike")
                    or out.get("nearest_put_oi_support")
                )
                ok = bool(wall_ready_surface and (call_surface or put_surface or out.get("wall_computable")))

            attempts.append({
                "mode": mode,
                "arg_count": len(args),
                "kwargs": sorted(kwargs.keys()),
                "ok": ok,
                "result_keys": result_keys,
                "oi_wall_ready": out.get("oi_wall_ready") if isinstance(out, dict) else None,
                "wall_computable": out.get("wall_computable") if isinstance(out, dict) else None,
                "call_wall_present": bool(out.get("call_wall")) if isinstance(out, dict) else False,
                "put_wall_present": bool(out.get("put_wall")) if isinstance(out, dict) else False,
                "nearest_call_oi_resistance_strike": out.get("nearest_call_oi_resistance_strike") if isinstance(out, dict) else None,
                "nearest_put_oi_support_strike": out.get("nearest_put_oi_support_strike") if isinstance(out, dict) else None,
            })
            if ok:
                return {
                    "ok": True,
                    "signature": sig,
                    "winning_attempt": attempts[-1],
                    "attempts": attempts,
                    "result_keys": result_keys,
                    "oi_wall_ready": out.get("oi_wall_ready"),
                    "wall_computable": out.get("wall_computable"),
                    "nearest_call_oi_resistance_strike": out.get("nearest_call_oi_resistance_strike"),
                    "nearest_put_oi_support_strike": out.get("nearest_put_oi_support_strike"),
                    "oi_bias": out.get("oi_bias"),
                }
        except Exception as exc:
            attempts.append({
                "mode": mode,
                "arg_count": len(args),
                "kwargs": sorted(kwargs.keys()),
                "ok": False,
                "error": repr(exc),
            })

    return {
        "ok": False,
        "signature": sig,
        "attempts": attempts,
        "last_result_keys": sorted(last_out.keys()) if isinstance(last_out, dict) else [],
        "last_result_excerpt": {
            key: last_out.get(key)
            for key in (
                "oi_wall_ready",
                "wall_computable",
                "ladder_present",
                "atm_reference_present",
                "call_wall",
                "put_wall",
                "nearest_call_oi_resistance_strike",
                "nearest_put_oi_support_strike",
                "oi_bias",
            )
            if isinstance(last_out, dict)
        },
    }


def main() -> int:
    generated_at_ns = time.time_ns()

    feeds = read("app/mme_scalpx/services/feeds.py")
    features = read("app/mme_scalpx/services/features.py")
    strike = read("app/mme_scalpx/services/feature_family/strike_selection.py")
    strategy = read("app/mme_scalpx/services/strategy.py")
    order_intent = read("app/mme_scalpx/services/strategy_family/order_intent.py")
    execution = read("app/mme_scalpx/services/execution.py")
    risk = read("app/mme_scalpx/services/risk.py")

    files_inspected = [file_info(rel) for rel in TARGETS]

    strike_selection_authority_checks = {
        "has_canonical_header": "Canonical strike-selection" in strike,
        "declares_module_owns_wall_summary": "nearest OI wall summaries" in strike,
        "declares_oi_not_trigger_law": "OI may never be treated as immediate trigger truth" in strike,
        "has_build_oi_wall_summary": "def build_oi_wall_summary" in strike,
    }

    features_canonicalized_checks = {
        "calls_build_oi_wall_summary": "build_oi_wall_summary" in features,
        "does_not_define_local_nearest_wall": "def _nearest_wall" not in features,
        "does_not_call_local_nearest_wall": "self._nearest_wall" not in features,
        "does_not_have_fallback_if_missing_wall": "if not call_wall or not put_wall" not in features,
        "publishes_oi_wall_context": '"oi_wall_context": {' in features,
        "publishes_context_not_trigger_law": '"law": "context_not_trigger"' in features,
        "publishes_wall_authority": "wall_authority" in features,
        "marks_canonical_true": '"canonical": True' in features,
    }

    feeds_canonicalized_checks = {
        "keeps_dhan_ladder_builder": "def _build_dhan_ladder_context" in feeds,
        "keeps_option_chain_ladder_json": "option_chain_ladder_json" in feeds,
        "keeps_strike_ladder_json": "strike_ladder_json" in feeds,
        "keeps_oi_wall_summary_json_compat_field": "oi_wall_summary_json" in feeds,
        "does_not_define_local_wall_function": "def _wall(" not in feeds,
        "declares_raw_non_authoritative_source": "feeds_raw_ladder_context_non_authoritative" in feeds,
        "declares_wall_calculation_delegated": '"wall_calculation_delegated": True' in feeds,
        "declares_canonical_wall_authority": "strike_selection.build_oi_wall_summary" in feeds,
        "neutralizes_producer_wall_ready": '"oi_wall_ready": False' in feeds,
        "neutralizes_producer_call_wall": '"call_wall": None' in feeds,
        "neutralizes_producer_put_wall": '"put_wall": None' in feeds,
    }

    duplicate_wall_logic_locations: list[dict[str, Any]] = []

    if "def _nearest_wall" in features or "self._nearest_wall" in features:
        duplicate_wall_logic_locations.append({
            "path": "app/mme_scalpx/services/features.py",
            "reason": "local nearest-wall fallback still present",
            "lines": lines(features, "_nearest_wall"),
        })

    if "def _wall(" in feeds:
        duplicate_wall_logic_locations.append({
            "path": "app/mme_scalpx/services/feeds.py",
            "reason": "producer-side wall calculator still present",
            "lines": lines(feeds, "def _wall("),
        })

    if "def build_oi_wall_summary" in strike:
        duplicate_wall_logic_locations.append({
            "path": "app/mme_scalpx/services/feature_family/strike_selection.py",
            "reason": "canonical authority",
            "lines": lines(strike, "def build_oi_wall_summary"),
        })

    noncanonical_duplicate_wall_logic_detected = any(
        item["path"] != "app/mme_scalpx/services/feature_family/strike_selection.py"
        for item in duplicate_wall_logic_locations
    )

    strategy_hold_only_checks = {
        "mentions_hold_only": "HOLD-only" in strategy,
        "has_hold_publish_guard": "_validate_hold_decision_for_publish" in strategy,
        "refuses_non_hold_action": "refused non-HOLD action" in strategy,
        "refuses_non_zero_qty": "refused non-zero qty" in strategy,
        "refuses_live_orders_allowed": "live_orders_allowed" in strategy and "refused" in strategy,
        "order_intent_adapter_disabled": "STRATEGY_ORDER_INTENT_ADAPTER_ENABLED" in strategy and "False" in strategy,
        "order_intent_publication_disabled": "STRATEGY_ORDER_INTENT_PUBLICATION_ENABLED" in strategy and "False" in strategy,
        "activation_promotion_disabled": "ACTIVATION_ALLOW_CANDIDATE_PROMOTION" in strategy and "False" in strategy,
        "does_not_write_orders_stream": "STREAM_ORDERS_MME" not in strategy,
        "does_not_call_broker_entry": "place_entry_order" not in strategy,
    }

    live_order_bypass_checks = {
        "strategy_no_orders_stream": "STREAM_ORDERS_MME" not in strategy,
        "strategy_no_place_entry_order": "place_entry_order" not in strategy,
        "strategy_no_place_exit_order": "place_exit_order" not in strategy,
        "order_intent_preview_disabled": any_token(order_intent, ["disabled_preview_only", "publish forbidden", "return False"]),
        "execution_remains_order_owner": any_token(execution, ["STREAM_ORDERS_MME", "place_entry_order"]),
        "risk_veto_surface_present": any_token(risk, ["veto_reason", "risk_veto", "broker_disconnected"]),
    }

    trigger_pattern = re.compile(
        r"(trigger|burst|fake_break|breakout|resume|impulse).*="
        r".*\\boi\\b|\\boi\\b.*=.*(trigger|burst|fake_break|breakout|resume|impulse)",
        re.IGNORECASE,
    )
    suspicious_trigger_lines: list[dict[str, Any]] = []
    for rel in [
        "app/mme_scalpx/services/features.py",
        "app/mme_scalpx/services/feature_family/strike_selection.py",
    ]:
        text = read(rel)
        for idx, line in enumerate(text.splitlines(), 1):
            if trigger_pattern.search(line):
                lower = line.lower()
                if any(word in lower for word in ["context", "wall", "bias", "score", "penalty", "metadata", "comment"]):
                    continue
                suspicious_trigger_lines.append({"path": rel, "line": idx, "text": line.strip()})

    oi_used_as_trigger_detected = bool(suspicious_trigger_lines)

    try:
        canonical_smoke = canonical_smoke_exact_kwargs()
    except Exception as exc:
        canonical_smoke = {"ok": False, "error": repr(exc)}

    blocking_checks = {
        "strike_selection_authority_ok": all(strike_selection_authority_checks.values()),
        "features_canonicalized_ok": all(features_canonicalized_checks.values()),
        "feeds_canonicalized_ok": all(feeds_canonicalized_checks.values()),
        "noncanonical_duplicate_wall_logic_absent": not noncanonical_duplicate_wall_logic_detected,
        "strategy_hold_only_ok": all(strategy_hold_only_checks.values()),
        "live_order_bypass_absent": all(live_order_bypass_checks.values()),
        "oi_not_used_as_trigger": not oi_used_as_trigger_detected,
        "canonical_smoke_ok": bool(canonical_smoke.get("ok")),
    }

    blocking_failures = false_checks(blocking_checks)
    final_verdict = "PASS" if not blocking_failures else "FAIL"

    recommended_next_batch = (
        "Batch 26-OI-C — family-specific soft scoring only, no hard OI filters, after replay/report proof."
        if final_verdict == "PASS"
        else "Stop. Fix blocking failures before Batch 26-OI-C."
    )

    proof = {
        "proof_name": "proof_oi_wall_authority_canonicalized",
        "batch": "26-OI-B",
        "revision": "R4",
        "generated_at_ns": generated_at_ns,
        "final_verdict": final_verdict,
        "files_inspected": files_inspected,
        "strike_selection_authority_checks": strike_selection_authority_checks,
        "features_canonicalized_checks": features_canonicalized_checks,
        "feeds_canonicalized_checks": feeds_canonicalized_checks,
        "duplicate_wall_logic_locations": duplicate_wall_logic_locations,
        "noncanonical_duplicate_wall_logic_detected": noncanonical_duplicate_wall_logic_detected,
        "strategy_hold_only_checks": strategy_hold_only_checks,
        "live_order_bypass_checks": live_order_bypass_checks,
        "live_order_bypass_detected": not all(live_order_bypass_checks.values()),
        "oi_used_as_trigger_detected": oi_used_as_trigger_detected,
        "oi_trigger_suspicious_lines": suspicious_trigger_lines,
        "canonical_smoke": canonical_smoke,
        "blocking_checks": blocking_checks,
        "blocking_failures": blocking_failures,
        "recommended_next_batch": recommended_next_batch,
    }

    PROOF_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROOF_PATH.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "batch": "26-OI-B",
        "revision": "R4",
        "final_verdict": final_verdict,
        "noncanonical_duplicate_wall_logic_detected": noncanonical_duplicate_wall_logic_detected,
        "oi_used_as_trigger_detected": oi_used_as_trigger_detected,
        "live_order_bypass_detected": proof["live_order_bypass_detected"],
        "strategy_hold_only_ok": all(strategy_hold_only_checks.values()),
        "canonical_smoke_ok": canonical_smoke.get("ok"),
        "blocking_failures": blocking_failures,
        "proof_path": str(PROOF_PATH),
        "recommended_next_batch": recommended_next_batch,
    }, indent=2, sort_keys=True))

    return 0 if final_verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
