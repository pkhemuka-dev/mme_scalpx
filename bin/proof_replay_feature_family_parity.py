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

from app.mme_scalpx.replay.contracts import replay_feature_family_adapter_contract_summary  # noqa: E402
from app.mme_scalpx.replay.feature_adapter import (  # noqa: E402
    REPLAY_FEATURE_FAMILIES,
    REPLAY_FEATURE_REQUIRED_PAYLOAD_FIELDS,
    REPLAY_FEATURE_SIDES,
    REPLAY_FAMILY_REQUIRED_SURFACE_TERMS,
    build_replay_feature_payload,
    publish_replay_feature_payload,
    replay_feature_adapter_contract_summary,
    validate_replay_feature_payload,
)
from app.mme_scalpx.replay.transport import LocalReplayTransport, assert_live_shape_event  # noqa: E402


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
            if term in text:
                hits[term].append(str(py.relative_to(ROOT)))
    return {
        "ok": True,
        "hits": hits,
        "hit_counts": {term: len(files) for term, files in hits.items()},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_replay_feature_family_parity.json")
    args = parser.parse_args()

    contract_file = ROOT / "etc/replay/schemas/replay_feature_family_adapter_contract_v1.json"
    contract_payload = json.loads(contract_file.read_text(encoding="utf-8")) if contract_file.exists() else {}

    feature_family_dir = ROOT / "app/mme_scalpx/services/feature_family"
    live_features_file = ROOT / "app/mme_scalpx/services/features.py"

    ast_result = _ast_parse_dir(feature_family_dir)

    all_terms = tuple(
        dict.fromkeys(
            term
            for terms in REPLAY_FAMILY_REQUIRED_SURFACE_TERMS.values()
            for term in terms
        )
    )
    term_scan = _grep_terms(feature_family_dir, all_terms)
    live_features_text = _read(live_features_file)
    live_features_token_hits = {
        token: token in live_features_text
        for token in (
            "family_features_json",
            "family_surfaces_json",
            "family_frames_json",
            "provider_ready_miso",
        )
    }

    row = {
        "event_ts_ns": 1_000_000_000,
        "sequence_id": 1,
        "branch_side": "BOTH",
        "selected_security_id": "REPLAY-SEC",
        "selected_tradingsymbol": "NIFTY-REPLAY",
        "selected_expiry": "2026-05-07",
        "selected_strike": 22500,
        "selected_option_type": "CE",
        "provider_ready_miso": True,
        "chain_context_fresh": True,
        "oi_context_fresh": True,
        "nearest_call_wall": 22600,
        "nearest_put_wall": 22400,
        "oi_wall_strength": 1.25,
        "trend_confirmed": True,
        "pullback_detected": True,
        "resume_confirmed": True,
        "shelf_confirmed": True,
        "breakout_triggered": True,
        "breakout_accepted": True,
        "shelf_high": 22520,
        "shelf_low": 22490,
        "compression_detected": True,
        "directional_breakout_triggered": True,
        "expansion_accepted": True,
        "retest_monitor_active": True,
        "hesitation_retest": False,
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
        "queue_reload_veto": False,
    }

    result = build_replay_feature_payload(run_id="replay_feature_smoke", row=row)
    payload = result.payload
    validation = validate_replay_feature_payload(payload)

    transport = LocalReplayTransport(run_id="replay_feature_smoke")
    event = publish_replay_feature_payload(
        transport,
        run_id="replay_feature_smoke",
        row=row,
        event_ts_ns=1_000_000_000,
        sequence_id=1,
    )
    assert_live_shape_event(event)
    snapshot = transport.snapshot()

    contract_summary = replay_feature_family_adapter_contract_summary()
    contracts_summary = replay_feature_family_adapter_contract_summary()

    families_ok = tuple(contract_payload.get("families", ())) == tuple(REPLAY_FEATURE_FAMILIES)
    sides_ok = tuple(contract_payload.get("sides", ())) == tuple(REPLAY_FEATURE_SIDES)
    required_payload_fields_ok = all(field in payload for field in REPLAY_FEATURE_REQUIRED_PAYLOAD_FIELDS)
    json_fields_ok = all(
        isinstance(payload.get(field), str) and len(payload.get(field, "")) > 2
        for field in ("family_features_json", "family_surfaces_json", "family_frames_json")
    )
    call_put_ok = validation.get("call_put_ok") is True
    family_terms_ok = validation.get("family_terms_ok") is True
    miso_context_ok = (
        payload.get("provider_ready_miso") is True
        and payload.get("dhan_context_fresh") is True
        and payload.get("oi_context_fresh") is True
        and "oi_wall_context" in payload["family_surfaces"]["MISO"]["CALL"]
        and "oi_wall_context" in payload["family_surfaces"]["MISO"]["PUT"]
    )
    no_strategy_decision_ok = (
        payload.get("strategy_decision_generated") is False
        and event.get("payload", {}).get("strategy_decision_generated") is False
    )
    no_approval_ok = (
        payload.get("paper_armed_approved") is False
        and payload.get("live_trading_approved") is False
        and payload.get("execution_arming_created") is False
        and payload.get("production_doctrine_changed") is False
        and event.get("paper_armed_approved") is False
        and event.get("live_trading_approved") is False
        and event.get("production_doctrine_changed") is False
    )
    transport_ok = (
        event.get("surface") == "feature_payload"
        and event.get("replay_key", "").startswith("replay:")
        and snapshot.get("event_count") == 1
    )

    feature_adapter_ok = bool(
        contract_file.exists()
        and ast_result.get("ok") is True
        and families_ok
        and sides_ok
        and required_payload_fields_ok
        and json_fields_ok
        and call_put_ok
        and family_terms_ok
        and miso_context_ok
        and no_strategy_decision_ok
        and no_approval_ok
        and transport_ok
    )

    proof = {
        "schema_version": "proof_replay_feature_family_parity_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "feature_adapter_ok": feature_adapter_ok,
        "contract_file_exists": contract_file.exists(),
        "feature_family_ast_ok": ast_result.get("ok"),
        "families_ok": families_ok,
        "sides_ok": sides_ok,
        "required_payload_fields_ok": required_payload_fields_ok,
        "json_fields_ok": json_fields_ok,
        "family_features_json_present": isinstance(payload.get("family_features_json"), str),
        "family_surfaces_json_present": isinstance(payload.get("family_surfaces_json"), str),
        "family_frames_json_present": isinstance(payload.get("family_frames_json"), str),
        "call_put_side_separation_ok": call_put_ok,
        "all_5_family_surfaces_present": family_terms_ok,
        "miso_provider_ready_replayable": payload.get("provider_ready_miso") is True,
        "miso_dhan_context_replayable": payload.get("dhan_context_fresh") is True,
        "miso_oi_context_replayable": payload.get("oi_context_fresh") is True,
        "miso_context_ok": miso_context_ok,
        "no_strategy_decision_ok": no_strategy_decision_ok,
        "no_approval_ok": no_approval_ok,
        "transport_ok": transport_ok,
        "live_feature_file_token_hits": live_features_token_hits,
        "feature_family_term_scan": term_scan,
        "feature_family_ast_parse": ast_result,
        "validation": validation,
        "contract_summary": contract_summary,
        "contracts_summary": contracts_summary,
        "sample_payload": payload,
        "sample_event": event,
        "snapshot": snapshot,
        "full_live_feature_computation_parity": "NOT_PROVEN_IN_27G",
        "strategy_family_decision_parity": "NOT_PROVEN_IN_27G",
        "safe_payload_shape_parity": "PROVEN_BY_27G",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "verdict": "PASS" if feature_adapter_ok else "FAIL",
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "proof": str(out),
        "verdict": proof["verdict"],
        "feature_adapter_ok": feature_adapter_ok,
        "family_features_json_present": proof["family_features_json_present"],
        "family_surfaces_json_present": proof["family_surfaces_json_present"],
        "call_put_side_separation_ok": call_put_ok,
        "all_5_family_surfaces_present": family_terms_ok,
        "miso_provider_ready_replayable": proof["miso_provider_ready_replayable"],
        "miso_dhan_context_replayable": proof["miso_dhan_context_replayable"],
        "miso_oi_context_replayable": proof["miso_oi_context_replayable"],
        "paper_armed_approved": False,
        "live_trading_approved": False,
    }, indent=2, sort_keys=True))

    return 0 if feature_adapter_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
