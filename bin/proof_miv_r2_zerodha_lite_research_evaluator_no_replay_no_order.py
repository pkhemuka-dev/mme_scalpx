#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import py_compile
import re
import subprocess
import time

from app.mme_scalpx.core import names as N
from app.mme_scalpx.replay import feature_adapter, strategy_adapter
from app.mme_scalpx.replay import miv_research_evaluator as E
from app.mme_scalpx.services.strategy_family import miv_r_contract as MIV


def git_status() -> str:
    try:
        return subprocess.check_output(["git", "status", "--short"], text=True, stderr=subprocess.STDOUT)
    except Exception as exc:
        return f"ERROR: {exc}"


def main() -> None:
    module = pathlib.Path("app/mme_scalpx/replay/miv_research_evaluator.py")
    proof_script = pathlib.Path(__file__)
    out_dir = pathlib.Path("run/audits") / "${TAG}_miv_smoke_artifacts"

    py_compile.compile(str(module), doraise=True)
    py_compile.compile(str(proof_script), doraise=True)

    rows = [
        {
            "event_ns": 1,
            "event_ts": "2026-06-11T09:20:00+05:30",
            "futures_ltp": 23000.0,
            "selected_option_ltp": 100.0,
            "selected_bid": 99.5,
            "selected_ask": 100.5,
            "selected_depth_bid": 1500,
            "selected_depth_ask": 1200,
            "selected_symbol": "NIFTY_TEST_23000_CE",
            "selected_option_type": "CE",
        },
        {
            "event_ns": 2,
            "event_ts": "2026-06-11T09:20:01+05:30",
            "futures_ltp": 23006.0,
            "selected_option_ltp": 103.5,
            "selected_bid": 103.0,
            "selected_ask": 104.0,
            "selected_depth_bid": 1700,
            "selected_depth_ask": 1400,
            "selected_symbol": "NIFTY_TEST_23000_CE",
            "selected_option_type": "CE",
        },
        {
            "event_ns": 3,
            "event_ts": "2026-06-11T09:20:02+05:30",
            "futures_ltp": 23012.0,
            "selected_option_ltp": 107.5,
            "selected_bid": 107.0,
            "selected_ask": 108.0,
            "selected_depth_bid": 1800,
            "selected_depth_ask": 1600,
            "selected_symbol": "NIFTY_TEST_23000_CE",
            "selected_option_type": "CE",
        },
        {
            "event_ns": 4,
            "event_ts": "2026-06-11T09:20:03+05:30",
            "futures_ltp": 23012.5,
            "selected_option_ltp": 110.0,
            "selected_bid": 109.5,
            "selected_ask": 110.5,
            "selected_depth_bid": 1800,
            "selected_depth_ask": 1600,
            "selected_symbol": "NIFTY_TEST_23000_CE",
            "selected_option_type": "CE",
        },
        {
            "event_ns": 5,
            "event_ts": "2026-06-11T09:20:04+05:30",
            "futures_ltp": 23012.7,
            "selected_option_ltp": 111.0,
            "selected_bid": 110.5,
            "selected_ask": 111.5,
            "selected_depth_bid": 1800,
            "selected_depth_ask": 1600,
            "selected_symbol": "NIFTY_TEST_23000_CE",
            "selected_option_type": "CE",
        },
    ]

    result = E.evaluate_miv_zerodha_lite_rows(
        rows,
        run_id="miv_r2_synthetic_smoke",
        dataset_id="synthetic_no_replay",
    )
    artifact_paths = E.write_miv_research_artifacts(result, out_dir)

    text = module.read_text(encoding="utf-8")
    forbidden_patterns = [
        r"\bplace_order\s*\(",
        r"\bkite\.place_order\b",
        r"\bdhan.*place_order\b",
        r"\border_send\s*\(",
        r"\bredis\.delete\s*\(",
        r"\bdelete\s*\(\s*['\"]lock:",
    ]
    forbidden_hits = [p for p in forbidden_patterns if re.search(p, text, flags=re.IGNORECASE)]

    candidates = list(result.get("candidates", []))
    trade_candidates = [c for c in candidates if c.get("trade_shadow_eligible")]
    invalid_contract_rows = [c for c in candidates if not c.get("contract_validation_ok")]

    production_families = tuple(getattr(N, "STRATEGY_FAMILY_IDS", ()))
    doctrine_ids = tuple(getattr(N, "DOCTRINE_IDS", ()))
    replay_feature_families = tuple(getattr(feature_adapter, "REPLAY_FEATURE_FAMILIES", ()))
    replay_strategy_families = tuple(getattr(strategy_adapter, "REPLAY_STRATEGY_FAMILIES", ()))

    artifact_exists = {name: pathlib.Path(path).exists() for name, path in artifact_paths.items()}

    checks = {
        "miv_contract_import_ok": MIV.MIV_FAMILY_ID == "MIV_R",
        "miv_not_in_strategy_family_ids": MIV.MIV_FAMILY_ID not in production_families,
        "miv_not_in_doctrine_ids": MIV.MIV_FAMILY_ID not in doctrine_ids,
        "miv_not_in_replay_feature_families": MIV.MIV_FAMILY_ID not in replay_feature_families,
        "miv_not_in_replay_strategy_families": MIV.MIV_FAMILY_ID not in replay_strategy_families,
        "candidate_count_positive_on_synthetic_burst": int(result.get("candidate_count", 0)) > 0,
        "trade_candidate_count_positive": len(trade_candidates) > 0,
        "all_candidates_contract_valid": not invalid_contract_rows,
        "all_trade_candidates_order_allowed_false": all(c.get("order_allowed") is False for c in trade_candidates),
        "all_trade_candidates_broker_send_false": all(c.get("broker_send_enabled") is False for c in trade_candidates),
        "all_trade_candidates_real_order_false": all(c.get("real_order_sent") is False for c in trade_candidates),
        "all_required_artifacts_written": all(artifact_exists.values()),
        "no_forbidden_patterns": not forbidden_hits,
    }

    classification = (
        "PASS_MIV_R2_ZERODHA_LITE_RESEARCH_EVALUATOR_PATCH_NO_REPLAY_NO_ORDER"
        if all(checks.values())
        else "FAIL_MIV_R2_ZERODHA_LITE_RESEARCH_EVALUATOR"
    )

    print(json.dumps({
        "batch": "LANE-MIV-R2_ZERODHA_LITE_RESEARCH_EVALUATOR_PATCH_NO_REPLAY_NO_ORDER",
        "classification": classification,
        "created_at_epoch": time.time(),
        "checks": checks,
        "candidate_count": result.get("candidate_count"),
        "trade_candidate_count": result.get("trade_candidate_count"),
        "neutral_label_count": result.get("neutral_label_count"),
        "first_candidate": candidates[0] if candidates else None,
        "artifact_paths": artifact_paths,
        "artifact_exists": artifact_exists,
        "forbidden_hits": forbidden_hits,
        "invalid_contract_rows": invalid_contract_rows,
        "safety": {
            "source_patch": True,
            "new_evaluator_only": True,
            "replay_execution": False,
            "broker_order": False,
            "risk_service_start": False,
            "execution_service_start": False,
            "redis_delete": False,
            "lock_delete": False,
            "production_registry_change": False,
            "paper_live_enabled": False,
        },
        "git_status_short": git_status(),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
