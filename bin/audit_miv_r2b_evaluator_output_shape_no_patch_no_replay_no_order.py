#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import pathlib
import py_compile
import subprocess
import time

from app.mme_scalpx.core import names as N
from app.mme_scalpx.replay import feature_adapter, strategy_adapter
from app.mme_scalpx.replay import miv_research_evaluator as E
from app.mme_scalpx.services.strategy_family import miv_r_contract as MIV

OUT_DIR = pathlib.Path("run/audits/LANE-MIV-R2B_EVALUATOR_OUTPUT_SHAPE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_audit_miv_r2_evaluator_outputs_with_real_timestamp_paths_neutral_label_and_blocker_cases_20260611_232406_miv_shape_artifacts")


def git_status() -> str:
    try:
        return subprocess.check_output(["git", "status", "--short"], text=True, stderr=subprocess.STDOUT)
    except Exception as exc:
        return f"ERROR: {exc}"


def read_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def csv_count(path: pathlib.Path) -> int:
    if not path.exists() or path.stat().st_size == 0:
        return 0
    with path.open("r", encoding="utf-8", newline="") as fh:
        return max(0, sum(1 for _ in csv.DictReader(fh)))


def main() -> None:
    module = pathlib.Path("app/mme_scalpx/replay/miv_research_evaluator.py")
    contract = pathlib.Path("app/mme_scalpx/services/strategy_family/miv_r_contract.py")
    py_compile.compile(str(module), doraise=True)
    py_compile.compile(str(contract), doraise=True)

    # Case A: trade candidate burst, should emit CALL candidates.
    call_rows = [
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
    ]

    # Case B: unknown option type but active/tradable tape, should permit neutral labels only.
    neutral_rows = [
        {
            "event_ns": 11,
            "event_ts": "2026-06-11T09:21:00+05:30",
            "futures_ltp": 23000.0,
            "selected_option_ltp": 100.0,
            "selected_bid": 99.5,
            "selected_ask": 100.5,
            "selected_depth_bid": 1500,
            "selected_depth_ask": 1500,
            "selected_symbol": "NIFTY_TEST_UNKNOWN",
        },
        {
            "event_ns": 12,
            "event_ts": "2026-06-11T09:21:01+05:30",
            "futures_ltp": 23000.5,
            "selected_option_ltp": 104.0,
            "selected_bid": 103.5,
            "selected_ask": 104.5,
            "selected_depth_bid": 1500,
            "selected_depth_ask": 1500,
            "selected_symbol": "NIFTY_TEST_UNKNOWN",
        },
        {
            "event_ns": 13,
            "event_ts": "2026-06-11T09:21:02+05:30",
            "futures_ltp": 23000.7,
            "selected_option_ltp": 108.0,
            "selected_bid": 107.5,
            "selected_ask": 108.5,
            "selected_depth_bid": 1500,
            "selected_depth_ask": 1500,
            "selected_symbol": "NIFTY_TEST_UNKNOWN",
        },
    ]

    # Case C: impossible spread, must create blocker rows and no trade candidate.
    blocked_rows = [
        {
            "event_ns": 21,
            "event_ts": "2026-06-11T09:22:00+05:30",
            "futures_ltp": 23000.0,
            "selected_option_ltp": 100.0,
            "selected_bid": 110.0,
            "selected_ask": 100.0,
            "selected_depth_bid": 1500,
            "selected_depth_ask": 1500,
            "selected_symbol": "NIFTY_TEST_BAD_CE",
            "selected_option_type": "CE",
        },
        {
            "event_ns": 22,
            "event_ts": "2026-06-11T09:22:01+05:30",
            "futures_ltp": 23010.0,
            "selected_option_ltp": 106.0,
            "selected_bid": 112.0,
            "selected_ask": 101.0,
            "selected_depth_bid": 1500,
            "selected_depth_ask": 1500,
            "selected_symbol": "NIFTY_TEST_BAD_CE",
            "selected_option_type": "CE",
        },
    ]

    call_result = E.evaluate_miv_zerodha_lite_rows(call_rows, run_id="miv_r2b_call_shape", dataset_id="synthetic_shape_no_replay")
    neutral_result = E.evaluate_miv_zerodha_lite_rows(neutral_rows, run_id="miv_r2b_neutral_shape", dataset_id="synthetic_shape_no_replay")
    blocked_result = E.evaluate_miv_zerodha_lite_rows(blocked_rows, run_id="miv_r2b_blocker_shape", dataset_id="synthetic_shape_no_replay")

    artifact_paths = E.write_miv_research_artifacts(call_result, OUT_DIR / "call_case")

    candidates_doc = read_json(pathlib.Path(artifact_paths["miv_research_candidates.json"]))
    shadow_doc = read_json(pathlib.Path(artifact_paths["miv_shadow_decisions.json"]))

    call_candidates = list(call_result.get("candidates", []))
    neutral_candidates = list(neutral_result.get("candidates", []))
    blocked_candidates = list(blocked_result.get("candidates", []))

    call_trade = [c for c in call_candidates if c.get("trade_shadow_eligible")]
    neutral_bad_routes = [
        c for c in neutral_candidates
        if c.get("route_to_risk_shadow") or c.get("route_to_execution_shadow") or c.get("route_to_order_intent_ledger")
    ]

    required_candidate_fields = set(MIV.MIV_REQUIRED_CANDIDATE_FIELDS)
    missing_fields_by_candidate = {
        c.get("miv_candidate_id", f"idx_{idx}"): sorted(required_candidate_fields - set(c.keys()))
        for idx, c in enumerate(call_candidates + neutral_candidates + blocked_candidates)
    }

    fid = MIV.MIV_FAMILY_ID
    checks = {
        "module_compiles": True,
        "contract_compiles": True,
        "miv_not_in_strategy_family_ids": fid not in tuple(getattr(N, "STRATEGY_FAMILY_IDS", ())),
        "miv_not_in_doctrine_ids": fid not in tuple(getattr(N, "DOCTRINE_IDS", ())),
        "miv_not_in_replay_feature_families": fid not in tuple(getattr(feature_adapter, "REPLAY_FEATURE_FAMILIES", ())),
        "miv_not_in_replay_strategy_families": fid not in tuple(getattr(strategy_adapter, "REPLAY_STRATEGY_FAMILIES", ())),
        "call_case_has_trade_candidates": len(call_trade) > 0,
        "call_candidates_contract_valid": all(c.get("contract_validation_ok") is True for c in call_candidates),
        "all_call_trade_candidates_order_blocked": all(c.get("order_allowed") is False and c.get("broker_send_enabled") is False and c.get("real_order_sent") is False for c in call_trade),
        "neutral_candidates_label_only": all(c.get("label_only") is True and c.get("trade_shadow_eligible") is False for c in neutral_candidates),
        "neutral_candidates_do_not_route_to_trade_shadow": len(neutral_bad_routes) == 0,
        "blocked_case_no_trade_candidates": not any(c.get("trade_shadow_eligible") for c in blocked_candidates),
        "blocked_case_has_blocker_rows": len(blocked_result.get("blocker_rows", [])) > 0,
        "all_required_artifacts_exist": all(pathlib.Path(p).exists() for p in artifact_paths.values()),
        "candidate_audit_csv_non_empty": csv_count(pathlib.Path(artifact_paths["miv_candidate_audit.csv"])) > 0,
        "factor_surface_csv_non_empty": csv_count(pathlib.Path(artifact_paths["miv_factor_surface.csv"])) > 0,
        "shadow_decisions_json_non_empty": int(shadow_doc.get("decision_count", 0)) > 0,
        "artifact_path_uses_real_tag_not_literal": "${TAG}" not in str(OUT_DIR),
        "no_candidate_missing_required_fields": all(not v for v in missing_fields_by_candidate.values()),
    }

    classification = (
        "PASS_MIV_R2B_EVALUATOR_OUTPUT_SHAPE_AUDIT_READY_FOR_R3_EXISTING_ARTIFACT_RUN"
        if all(checks.values())
        else "FAIL_MIV_R2B_EVALUATOR_OUTPUT_SHAPE_AUDIT"
    )

    print(json.dumps({
        "batch": "LANE-MIV-R2B_EVALUATOR_OUTPUT_SHAPE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER",
        "classification": classification,
        "created_at_epoch": time.time(),
        "checks": checks,
        "out_dir": str(OUT_DIR),
        "artifact_paths": artifact_paths,
        "call_candidate_count": call_result.get("candidate_count"),
        "call_trade_candidate_count": call_result.get("trade_candidate_count"),
        "neutral_candidate_count": neutral_result.get("candidate_count"),
        "neutral_label_count": neutral_result.get("neutral_label_count"),
        "blocked_candidate_count": blocked_result.get("candidate_count"),
        "blocked_blocker_count": len(blocked_result.get("blocker_rows", [])),
        "first_call_candidate": call_candidates[0] if call_candidates else None,
        "first_neutral_candidate": neutral_candidates[0] if neutral_candidates else None,
        "missing_fields_by_candidate": missing_fields_by_candidate,
        "candidate_artifact_summary": {
            "candidate_count": candidates_doc.get("candidate_count"),
            "trade_candidate_count": candidates_doc.get("trade_candidate_count"),
            "neutral_label_count": candidates_doc.get("neutral_label_count"),
        },
        "safety": {
            "source_patch": False,
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
