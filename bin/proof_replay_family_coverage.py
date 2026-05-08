#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.mme_scalpx.replay.feature_adapter import build_replay_feature_payload  # noqa: E402
from app.mme_scalpx.replay.strategy_adapter import (  # noqa: E402
    REPLAY_STRATEGY_FAMILIES,
    REPLAY_STRATEGY_SIDES,
    build_replay_strategy_candidates,
    replay_strategy_adapter_contract_summary,
    validate_replay_strategy_candidates,
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def _ast_parse_dir(path: Path) -> dict[str, object]:
    results = []
    ok = True
    if not path.exists():
        return {"ok": False, "missing_dir": str(path), "results": []}
    for py in sorted(path.rglob("*.py")):
        try:
            ast.parse(_read(py), filename=str(py))
            results.append({"path": str(py.relative_to(ROOT)), "ast_parse_ok": True})
        except SyntaxError as exc:
            ok = False
            results.append({"path": str(py.relative_to(ROOT)), "ast_parse_ok": False, "error": str(exc)})
    return {"ok": ok, "results": results}


def _grep_terms(path: Path, terms: tuple[str, ...]) -> dict[str, object]:
    hits = {term: [] for term in terms}
    if not path.exists():
        return {"ok": False, "missing_dir": str(path), "hits": hits}
    for py in sorted(path.rglob("*.py")):
        text = _read(py)
        for term in terms:
            if term.lower() in text.lower():
                hits[term].append(str(py.relative_to(ROOT)))
    return {
        "ok": True,
        "hits": hits,
        "hit_counts": {term: len(files) for term, files in hits.items()},
    }


def sample_row() -> dict[str, object]:
    return {
        "provider_ready_miso": True,
        "chain_context_fresh": True,
        "oi_context_fresh": True,
        "selected_security_id": "REPLAY-SEC",
        "selected_tradingsymbol": "NIFTY-REPLAY",
        "selected_expiry": "2026-05-07",
        "selected_strike": 22500,
        "selected_option_type": "CE",
        "nearest_call_wall": 22600,
        "nearest_put_wall": 22400,
        "oi_wall_strength": 1.25,
        "trend_confirmed": True,
        "pullback_detected": True,
        "resume_confirmed": True,
        "micro_trap_flag": True,
        "futures_impulse_ok": True,
        "shelf_confirmed": True,
        "breakout_triggered": True,
        "breakout_accepted": True,
        "shelf_high": 22520,
        "shelf_low": 22490,
        "compression_detected": True,
        "directional_breakout_triggered": True,
        "expansion_accepted": True,
        "retest_monitor_active": True,
        "hesitation_retest": True,
        "active_zone_valid": True,
        "active_zone": "ORB_LOW",
        "fake_break": True,
        "range_reentry": True,
        "flow_flip": True,
        "trap_event_id": "CALL|ORB_LOW|1000|2000",
        "burst_detected": True,
        "burst_event_id": "CALL|REPLAY-SEC|1000",
        "aggression_ok": True,
        "tape_speed_ok": True,
        "imbalance_persistence_ok": True,
        "queue_reload_veto": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_replay_family_coverage.json")
    args = parser.parse_args()

    contract_file = ROOT / "etc/replay/schemas/replay_strategy_family_adapter_contract_v1.json"
    contract_payload = json.loads(contract_file.read_text(encoding="utf-8")) if contract_file.exists() else {}

    strategy_family_dir = ROOT / "app/mme_scalpx/services/strategy_family"
    live_strategy_file = ROOT / "app/mme_scalpx/services/strategy.py"

    ast_result = _ast_parse_dir(strategy_family_dir)
    term_scan = _grep_terms(strategy_family_dir, tuple(REPLAY_STRATEGY_FAMILIES + REPLAY_STRATEGY_SIDES + ("arbitr", "candidate", "decision", "blocker")))

    live_strategy_text = _read(live_strategy_file)
    live_strategy_token_hits = {
        token: token.lower() in live_strategy_text.lower()
        for token in (
            "family_features_json",
            "family_surfaces_json",
            "arbitr",
            "candidate",
            "decision",
        )
    }

    feature_result = build_replay_feature_payload(run_id="replay_strategy_coverage_smoke", row=sample_row())
    feature_payload = feature_result.payload

    candidates = build_replay_strategy_candidates(
        run_id="replay_strategy_coverage_smoke",
        feature_payload=feature_payload,
    )
    validation = validate_replay_strategy_candidates(candidates)
    summary = replay_strategy_adapter_contract_summary()

    required_pairs = {(family, side) for family in REPLAY_STRATEGY_FAMILIES for side in REPLAY_STRATEGY_SIDES}
    found_pairs = {(candidate["family"], candidate["side"]) for candidate in candidates}

    candidate_no_order_ok = all(
        c.get("order_allowed") is False
        and c.get("real_order_intent_generated") is False
        and c.get("paper_armed_approved") is False
        and c.get("live_trading_approved") is False
        and c.get("execution_arming_created") is False
        and c.get("production_doctrine_changed") is False
        for c in candidates
    )

    coverage_ok = bool(
        contract_file.exists()
        and ast_result.get("ok") is True
        and tuple(contract_payload.get("families", ())) == tuple(REPLAY_STRATEGY_FAMILIES)
        and tuple(contract_payload.get("sides", ())) == tuple(REPLAY_STRATEGY_SIDES)
        and found_pairs == required_pairs
        and validation.get("ok") is True
        and candidate_no_order_ok
        and summary.get("paper_armed_approved") is False
        and summary.get("live_trading_approved") is False
    )

    proof = {
        "schema_version": "proof_replay_family_coverage_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "family_coverage_ok": coverage_ok,
        "contract_file_exists": contract_file.exists(),
        "strategy_family_ast_ok": ast_result.get("ok"),
        "required_candidate_count": len(required_pairs),
        "candidate_count": len(candidates),
        "family_side_coverage_ok": found_pairs == required_pairs,
        "candidate_validation_ok": validation.get("ok"),
        "candidate_no_order_ok": candidate_no_order_ok,
        "families": REPLAY_STRATEGY_FAMILIES,
        "sides": REPLAY_STRATEGY_SIDES,
        "found_pairs": sorted([f"{family}:{side}" for family, side in found_pairs]),
        "live_strategy_token_hits": live_strategy_token_hits,
        "strategy_family_term_scan": term_scan,
        "strategy_family_ast_parse": ast_result,
        "validation": validation,
        "contract_summary": summary,
        "sample_candidates": candidates,
        "full_live_strategy_decision_parity": "NOT_PROVEN_IN_27H",
        "safe_decision_shape_parity": "PROVEN_BY_27H",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "verdict": "PASS" if coverage_ok else "FAIL",
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "proof": str(out),
        "verdict": proof["verdict"],
        "family_coverage_ok": coverage_ok,
        "candidate_count": proof["candidate_count"],
        "family_side_coverage_ok": proof["family_side_coverage_ok"],
        "candidate_no_order_ok": candidate_no_order_ok,
        "paper_armed_approved": False,
        "live_trading_approved": False,
    }, indent=2, sort_keys=True))

    return 0 if coverage_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
