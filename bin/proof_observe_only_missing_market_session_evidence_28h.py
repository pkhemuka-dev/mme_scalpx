#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import pathlib
import shutil
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path.cwd().resolve()
PROOF_DIR = ROOT / "run" / "proofs"
NOW = datetime.now(timezone.utc).isoformat()

SAFETY = {
    "starts_services": False,
    "reads_live_redis": False,
    "writes_live_redis": False,
    "calls_broker_api": False,
    "broker_call_reachable": False,
    "live_redis_write_reachable": False,
    "runtime_promotion_reachable": False,
    "paper_armed_approved": False,
    "live_trading_approved": False,
    "execution_arming_created": False,
    "real_order_sent": False,
    "broker_calls_executed": False,
    "live_redis_writes_executed": False,
    "production_doctrine_changed": False,
}

BOUNDARY = {
    "paper_armed_readiness": "NOT_APPROVED_IN_28H",
    "live_trading_readiness": "NOT_APPROVED_IN_28H",
    "production_strategy_improvement_claim": "NOT_PROVEN_IN_28H",
    "production_doctrine_revision": "NOT_APPROVED_IN_28H",
    "full_live_replay_parity": "NOT_PROVEN_IN_28H",
}

def read_json(rel: str) -> dict[str, Any]:
    path = ROOT / rel
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "_read_error": type(exc).__name__,
            "_read_error_text": str(exc),
            "_path": rel,
        }

def write_json(rel: str, payload: dict[str, Any]) -> str:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
    tmp.replace(path)
    return rel

def sha256_file(path: pathlib.Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def file_state(rel: str) -> dict[str, Any]:
    path = ROOT / rel
    return {
        "path": rel,
        "present": path.is_file(),
        "size_bytes": path.stat().st_size if path.is_file() else 0,
        "sha256": sha256_file(path),
    }

def first_present(paths: list[str]) -> str | None:
    for raw in paths:
        if (ROOT / raw).is_file():
            return raw
    return None

def safe_keys(obj: Any) -> list[str]:
    if isinstance(obj, dict):
        return sorted(str(k) for k in obj.keys())
    return []

provider_runtime_proof = read_json("run/proofs/proof_market_session_provider_runtime.json")
feed_snapshot_proof = read_json("run/proofs/proof_market_session_feed_snapshot.json")
feature_payload_proof = read_json("run/proofs/proof_market_session_feature_payload.json")
family_surfaces_proof = read_json("run/proofs/proof_market_session_family_surfaces.json")
strategy_activation_proof = read_json("run/proofs/proof_market_session_strategy_activation.json")
no_order_sent_proof = read_json("run/proofs/proof_market_session_no_order_sent.json")
candidate_28g = read_json("etc/replay/parity/observe_only_actual_generated_evidence_map_candidate_28g.json")

source_file_states = {
    "provider_runtime": file_state("run/proofs/proof_market_session_provider_runtime.json"),
    "feed_snapshot": file_state("run/proofs/proof_market_session_feed_snapshot.json"),
    "feature_payload": file_state("run/proofs/proof_market_session_feature_payload.json"),
    "family_surfaces": file_state("run/proofs/proof_market_session_family_surfaces.json"),
    "strategy_activation": file_state("run/proofs/proof_market_session_strategy_activation.json"),
    "no_order_sent": file_state("run/proofs/proof_market_session_no_order_sent.json"),
    "candidate_28g": file_state("etc/replay/parity/observe_only_actual_generated_evidence_map_candidate_28g.json"),
}

streams = no_order_sent_proof.get("streams") if isinstance(no_order_sent_proof.get("streams"), dict) else {}
decisions_stream = streams.get("decisions") if isinstance(streams.get("decisions"), dict) else {}
orders_stream = streams.get("orders") if isinstance(streams.get("orders"), dict) else {}

live_stream_inventory = {
    "schema_version": "market_session_live_stream_inventory_v1",
    "proof_name": "proof_market_session_live_stream_inventory",
    "batch": "28H",
    "generated_at_utc": NOW,
    "accepted_for": "OBSERVE_ONLY_MARKET_SESSION_STREAM_INVENTORY_FROM_EXISTING_EVIDENCE",
    "inventory_method": "derived_from_existing_proof_files_only_no_live_redis_read",
    "source_proofs": {
        "no_order_sent": "run/proofs/proof_market_session_no_order_sent.json",
    },
    "streams": streams,
    "stream_count": len(streams),
    "decisions_stream_key": decisions_stream.get("key"),
    "orders_stream_key": orders_stream.get("key"),
    "strategy_decisions_observed": bool(no_order_sent_proof.get("checks", {}).get("strategy_decisions_observed")),
    "recent_decision_actions": decisions_stream.get("recent_actions", []),
    "non_hold_actions": decisions_stream.get("non_hold_actions", []),
    "orders_len_before": orders_stream.get("len_before"),
    "orders_len_after": orders_stream.get("len_after"),
    "market_session_live_stream_inventory_ok": bool(streams),
    **SAFETY,
    **BOUNDARY,
}

feed_hashes = feed_snapshot_proof.get("hashes") if isinstance(feed_snapshot_proof.get("hashes"), dict) else {}
hash_inventory = {}
for name, info in feed_hashes.items():
    if isinstance(info, dict):
        hash_inventory[str(name)] = {
            "source": "proof_market_session_feed_snapshot",
            "constant": info.get("constant"),
            "key": info.get("key"),
        }

provider_hash_key = provider_runtime_proof.get("hash_key")
provider_hash_constant = provider_runtime_proof.get("hash_constant")
if provider_hash_key or provider_hash_constant:
    hash_inventory["provider_runtime"] = {
        "source": "proof_market_session_provider_runtime",
        "constant": provider_hash_constant,
        "key": provider_hash_key,
    }

feature_hash_key = strategy_activation_proof.get("feature_hash_key")
if feature_hash_key:
    hash_inventory["feature_payload"] = {
        "source": "proof_market_session_strategy_activation",
        "constant": "HASH_STATE_FEATURES_MME_FUT",
        "key": feature_hash_key,
    }

live_hash_inventory = {
    "schema_version": "market_session_live_hash_inventory_v1",
    "proof_name": "proof_market_session_live_hash_inventory",
    "batch": "28H",
    "generated_at_utc": NOW,
    "accepted_for": "OBSERVE_ONLY_MARKET_SESSION_HASH_INVENTORY_FROM_EXISTING_EVIDENCE",
    "inventory_method": "derived_from_existing_proof_files_only_no_live_redis_read",
    "source_proofs": {
        "feed_snapshot": "run/proofs/proof_market_session_feed_snapshot.json",
        "provider_runtime": "run/proofs/proof_market_session_provider_runtime.json",
        "strategy_activation": "run/proofs/proof_market_session_strategy_activation.json",
    },
    "hashes": hash_inventory,
    "hash_count": len(hash_inventory),
    "feed_snapshot_checks": feed_snapshot_proof.get("checks", {}),
    "provider_runtime_checks": provider_runtime_proof.get("checks", {}),
    "market_session_live_hash_inventory_ok": bool(hash_inventory),
    **SAFETY,
    **BOUNDARY,
}

provider_runtime = {}
if isinstance(provider_runtime_proof.get("provider_runtime"), dict) and provider_runtime_proof.get("provider_runtime"):
    provider_runtime = provider_runtime_proof["provider_runtime"]
elif isinstance(feature_payload_proof.get("provider_runtime"), dict):
    provider_runtime = feature_payload_proof["provider_runtime"]

provider_status_fields = {
    key: value
    for key, value in provider_runtime.items()
    if key.endswith("_status") or key.endswith("_provider_status") or key in {
        "family_runtime_mode",
        "provider_runtime_mode",
        "provider_runtime_blocked",
        "provider_runtime_block_reason",
        "provider_ready_classic",
        "provider_ready_miso",
        "failover_active",
        "pending_failover",
        "transition_reason",
    }
}

provider_health_snapshot = {
    "schema_version": "market_session_provider_health_snapshot_v1",
    "proof_name": "proof_market_session_provider_health_snapshot",
    "batch": "28H",
    "generated_at_utc": NOW,
    "accepted_for": "OBSERVE_ONLY_PROVIDER_HEALTH_SNAPSHOT_FROM_EXISTING_EVIDENCE",
    "snapshot_method": "derived_from_existing_provider_runtime_and_feature_payload_proofs_only",
    "source_proofs": {
        "provider_runtime": "run/proofs/proof_market_session_provider_runtime.json",
        "feature_payload": "run/proofs/proof_market_session_feature_payload.json",
    },
    "provider_runtime_source": "provider_runtime_proof" if provider_runtime_proof.get("provider_runtime") else "feature_payload_proof",
    "provider_runtime_keys": safe_keys(provider_runtime),
    "provider_status_fields": provider_status_fields,
    "provider_runtime_checks": provider_runtime_proof.get("checks", {}),
    "feature_payload_provider_runtime_present": bool(feature_payload_proof.get("provider_runtime")),
    "provider_health_ready_claim": False,
    "provider_health_snapshot_present": bool(provider_runtime or provider_runtime_proof.get("checks")),
    "market_session_provider_health_snapshot_ok": bool(provider_runtime or provider_runtime_proof.get("checks")),
    **SAFETY,
    **BOUNDARY,
}

feature_observed = feature_payload_proof.get("observed") if isinstance(feature_payload_proof.get("observed"), dict) else {}
feed_observed = feed_snapshot_proof.get("observed") if isinstance(feed_snapshot_proof.get("observed"), dict) else {}
call_context = feature_observed.get("call") if isinstance(feature_observed.get("call"), dict) else {}
put_context = feature_observed.get("put") if isinstance(feature_observed.get("put"), dict) else {}

selected_option_context = {
    "schema_version": "market_session_selected_option_context_v1",
    "proof_name": "proof_market_session_selected_option_context",
    "batch": "28H",
    "generated_at_utc": NOW,
    "accepted_for": "OBSERVE_ONLY_SELECTED_OPTION_CONTEXT_FROM_EXISTING_EVIDENCE",
    "snapshot_method": "derived_from_existing_feed_snapshot_and_feature_payload_proofs_only",
    "source_proofs": {
        "feed_snapshot": "run/proofs/proof_market_session_feed_snapshot.json",
        "feature_payload": "run/proofs/proof_market_session_feature_payload.json",
    },
    "feed_snapshot_selected_option_hash_present": feed_snapshot_proof.get("checks", {}).get("selected_option_hash_present"),
    "feed_snapshot_selected_call_present_during_market": feed_snapshot_proof.get("checks", {}).get("selected_call_present_during_market"),
    "feed_snapshot_selected_put_present_during_market": feed_snapshot_proof.get("checks", {}).get("selected_put_present_during_market"),
    "feed_snapshot_observed": {
        "call_depth_total": feed_observed.get("call_depth_total"),
        "put_depth_total": feed_observed.get("put_depth_total"),
        "call_member_keys": safe_keys(feed_observed.get("call_member")),
        "put_member_keys": safe_keys(feed_observed.get("put_member")),
    },
    "feature_call_context": call_context,
    "feature_put_context": put_context,
    "selected_option_context_ready_claim": False,
    "selected_option_context_present": bool(call_context or put_context or feed_snapshot_proof.get("checks", {}).get("selected_option_hash_present")),
    "market_session_selected_option_context_ok": bool(call_context or put_context or feed_snapshot_proof.get("checks", {}).get("selected_option_hash_present")),
    **SAFETY,
    **BOUNDARY,
}

context_quality = feature_payload_proof.get("context_quality") if isinstance(feature_payload_proof.get("context_quality"), dict) else {}
strike_summary = feature_observed.get("strike_selection_summary") if isinstance(feature_observed.get("strike_selection_summary"), dict) else {}

dhan_oi_ladder_context = {
    "schema_version": "market_session_dhan_oi_ladder_context_v1",
    "proof_name": "proof_market_session_dhan_oi_ladder_context",
    "batch": "28H",
    "generated_at_utc": NOW,
    "accepted_for": "OBSERVE_ONLY_DHAN_OI_LADDER_CONTEXT_IF_AVAILABLE_FROM_EXISTING_EVIDENCE",
    "snapshot_method": "derived_from_existing_feature_payload_and_feed_snapshot_proofs_only",
    "source_proofs": {
        "feature_payload": "run/proofs/proof_market_session_feature_payload.json",
        "feed_snapshot": "run/proofs/proof_market_session_feed_snapshot.json",
    },
    "context_quality": context_quality,
    "strike_selection_summary": strike_summary,
    "feed_snapshot_dhan_context_hash_present": feed_snapshot_proof.get("checks", {}).get("dhan_context_hash_present"),
    "feed_snapshot_dhan_context_keys": feed_observed.get("dhan_context_keys", []),
    "dhan_oi_ladder_available": bool(context_quality.get("has_ladder") or strike_summary.get("ladder_size")),
    "dhan_oi_wall_available": bool(context_quality.get("has_oi_wall")),
    "dhan_context_present": bool(context_quality.get("present") or feed_snapshot_proof.get("checks", {}).get("dhan_context_hash_present")),
    "dhan_oi_ladder_context_ready_claim": False,
    "market_session_dhan_oi_ladder_context_if_available_ok": True,
    **SAFETY,
    **BOUNDARY,
}

written = []
written.append(write_json("run/proofs/proof_market_session_live_stream_inventory.json", live_stream_inventory))
written.append(write_json("run/proofs/proof_market_session_live_hash_inventory.json", live_hash_inventory))
written.append(write_json("run/proofs/proof_market_session_provider_health_snapshot.json", provider_health_snapshot))
written.append(write_json("run/proofs/proof_market_session_selected_option_context.json", selected_option_context))
written.append(write_json("run/proofs/proof_market_session_dhan_oi_ladder_context.json", dhan_oi_ladder_context))
written.append(write_json("run/proofs/proof_market_session_dhan_oi_ladder_context_if_available.json", dhan_oi_ladder_context))

required_for_28g = {
    "live_stream_inventory": "run/proofs/proof_market_session_live_stream_inventory.json",
    "live_hash_inventory": "run/proofs/proof_market_session_live_hash_inventory.json",
    "provider_health_snapshot": "run/proofs/proof_market_session_provider_health_snapshot.json",
    "selected_option_context": "run/proofs/proof_market_session_selected_option_context.json",
    "dhan_oi_ladder_context_if_available": first_present([
        "run/proofs/proof_market_session_dhan_oi_ladder_context.json",
        "run/proofs/proof_market_session_dhan_oi_ladder_context_if_available.json",
    ]),
}

all_required_written = all(path and (ROOT / path).is_file() for path in required_for_28g.values())

result = {
    "schema_version": "proof_observe_only_missing_market_session_evidence_28h_v1",
    "batch": "28H",
    "generated_at_utc": NOW,
    "accepted_for": "MISSING_MARKET_SESSION_PROOF_OUTPUT_GENERATION_ONLY",
    "verdict": "PASS_OBSERVE_ONLY_MISSING_MARKET_SESSION_PROOF_OUTPUTS_28H" if all_required_written else "FAIL_OBSERVE_ONLY_MISSING_MARKET_SESSION_PROOF_OUTPUTS_28H",
    "observe_only_missing_market_session_evidence_28h_ok": bool(all_required_written),
    "source_file_states": source_file_states,
    "preexisting_28g_candidate": {
        "candidate_present": bool(candidate_28g),
        "found_count": candidate_28g.get("found_count"),
        "missing_count": candidate_28g.get("missing_count"),
        "complete": candidate_28g.get("complete"),
        "missing": candidate_28g.get("missing", {}),
    },
    "written_outputs": written,
    "required_for_28g_now": required_for_28g,
    "all_required_missing_outputs_written": bool(all_required_written),
    "reran_28g": False,
    "final_map_published": False,
    "next_batch": "Rerun Batch 28G. If 28G publishes final map, rerun Batch 28F.",
    **SAFETY,
    **BOUNDARY,
}

write_json("run/proofs/proof_observe_only_missing_market_session_evidence_28h.json", result)
write_json("run/proofs/proof_observe_only_missing_market_session_evidence_28h_latest.json", result)

milestone = f"""Batch 28H Generate missing market-session proof outputs for actual observe_only evidence map

Date: {datetime.now().strftime('%Y-%m-%d')}

Verdict: {result['verdict']}

Accepted for:
MISSING_MARKET_SESSION_PROOF_OUTPUT_GENERATION_ONLY

Scope:
28H generates the missing market-session proof output files required by the 28G actual observe_only evidence-map generator.
28H derives these proof outputs only from existing observe_only proof artifacts.
28H does not start services.
28H does not read live Redis.
28H does not write live Redis.
28H does not call broker APIs.
28H does not approve paper_armed.
28H does not approve live trading.
28H does not prove replay/live parity.

Generated missing proof outputs:
- run/proofs/proof_market_session_live_stream_inventory.json
- run/proofs/proof_market_session_live_hash_inventory.json
- run/proofs/proof_market_session_provider_health_snapshot.json
- run/proofs/proof_market_session_selected_option_context.json
- run/proofs/proof_market_session_dhan_oi_ladder_context.json
- run/proofs/proof_market_session_dhan_oi_ladder_context_if_available.json

Important:
These files are evidence/inventory snapshots.
They do not certify provider readiness.
They do not certify selected option tradability.
They do not approve runtime promotion.
They do not publish the final actual evidence map.

Next:
Rerun Batch 28G.
If and only if 28G publishes etc/replay/parity/observe_only_actual_generated_evidence_map.json, rerun Batch 28F.

Safety:
paper_armed_approved=false
live_trading_approved=false
starts_services=false
reads_live_redis=false
writes_live_redis=false
calls_broker_api=false
full_live_replay_parity=NOT_PROVEN_IN_28H
"""
write_json("run/proofs/proof_observe_only_missing_market_session_evidence_28h_milestone_payload.json", {
    "milestone_path": "docs/milestones/BATCH28H_GENERATE_MISSING_MARKET_SESSION_PROOF_OUTPUTS.md",
    "milestone_text_sha256": hashlib.sha256(milestone.encode("utf-8")).hexdigest(),
})
(ROOT / "docs" / "milestones").mkdir(parents=True, exist_ok=True)
(ROOT / "docs" / "milestones" / "BATCH28H_GENERATE_MISSING_MARKET_SESSION_PROOF_OUTPUTS.md").write_text(milestone, encoding="utf-8")

print(json.dumps(result, indent=2, sort_keys=True))
