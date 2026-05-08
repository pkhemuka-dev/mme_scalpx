#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import subprocess
import datetime
from typing import Any

ROOT = pathlib.Path("/home/Lenovo/scalpx/projects/mme_scalpx")
OUT = ROOT / "run/proofs/proof_batch26o15_activation_candidate_surface_audit.json"

def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def cmd(args: list[str], timeout: float = 5.0) -> str:
    try:
        cp = subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        return cp.stdout.strip() if cp.returncode == 0 else "ERR:" + (cp.stderr.strip() or cp.stdout.strip())
    except Exception as exc:
        return "EXC:" + repr(exc)

def hgetall(key: str) -> dict[str, str]:
    raw = cmd(["redis-cli", "HGETALL", key], 5).splitlines()
    d: dict[str, str] = {}
    for i in range(0, len(raw) - 1, 2):
        d[raw[i]] = raw[i + 1]
    return d

def parse_json(raw: str) -> Any:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception as exc:
        return {"_parse_error": repr(exc), "_raw_head": raw[:1000]}

def pgrep(pattern: str) -> str:
    return cmd(["bash", "-lc", f"pgrep -af {pattern!r} | grep -v grep || true"], 5)

def latest_decision() -> str:
    return cmd(["bash", "-lc", "redis-cli XREVRANGE decisions:mme:stream + - COUNT 1 | sed -n '1,320p'"], 5)

def load_json(path: str) -> dict[str, Any]:
    p = ROOT / path
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(errors="replace"))
    except Exception as exc:
        return {"_parse_error": repr(exc)}

def read(rel: str) -> str:
    p = ROOT / rel
    return p.read_text(errors="replace") if p.exists() else ""

def summarize_branch(obj: Any) -> dict[str, Any]:
    if not isinstance(obj, dict):
        return {"present": False}
    surface = obj.get("surface") if isinstance(obj.get("surface"), dict) else {}
    tradability = obj.get("tradability") if isinstance(obj.get("tradability"), dict) else {}
    selected_features = obj.get("selected_features") if isinstance(obj.get("selected_features"), dict) else {}
    option_features = obj.get("option_features") if isinstance(obj.get("option_features"), dict) else {}
    return {
        "present": True,
        "family_id": obj.get("family_id") or surface.get("family_id"),
        "branch_id": obj.get("branch_id") or surface.get("branch_id"),
        "side": obj.get("side") or surface.get("side"),
        "eligible": obj.get("eligible"),
        "tradability_ok": obj.get("tradability_ok") if "tradability_ok" in obj else tradability.get("entry_pass"),
        "entry_pass": obj.get("entry_pass") if "entry_pass" in obj else tradability.get("entry_pass"),
        "failed_stage": obj.get("failed_stage") or surface.get("failed_stage"),
        "blocked_reason": obj.get("blocked_reason") or obj.get("batch9_freeze_blocked_reason") or surface.get("blocked_reason"),
        "provider_ready": obj.get("provider_ready") if "provider_ready" in obj else surface.get("provider_ready"),
        "runtime_mode": obj.get("runtime_mode") or surface.get("runtime_mode"),
        "option_symbol": obj.get("option_symbol") or selected_features.get("option_symbol") or option_features.get("option_symbol"),
        "option_price": obj.get("option_price") or selected_features.get("ltp") or option_features.get("ltp"),
        "selected_features_present": selected_features.get("present"),
        "selected_features_fresh": selected_features.get("fresh"),
        "selected_features_valid": selected_features.get("valid"),
        "selected_features_provider_id": selected_features.get("provider_id"),
        "option_features_present": option_features.get("present"),
        "option_features_fresh": option_features.get("fresh"),
        "option_features_valid": option_features.get("valid"),
        "raw_keys": sorted(obj.keys())[:160],
    }

def find_key_recursive(obj: Any, wanted: str, hits: list[tuple[str, Any]], path: str = "") -> None:
    if len(hits) >= 50:
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else str(k)
            if str(k).lower() == wanted.lower() or wanted.lower() in str(k).lower():
                hits.append((p, v))
            find_key_recursive(v, wanted, hits, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:20]):
            find_key_recursive(v, wanted, hits, f"{path}[{i}]")

def main() -> int:
    features_hash = hgetall("state:features:mme:fut")
    provider = hgetall("state:provider:runtime")
    position = hgetall("state:position:mme")

    family_features = parse_json(features_hash.get("family_features_json", ""))
    family_surfaces = parse_json(features_hash.get("family_surfaces_json", ""))
    consumer_view = parse_json(features_hash.get("consumer_view_json", ""))

    latest = latest_decision()

    surfaces_to_search = {
        "family_features_json": family_features,
        "family_surfaces_json": family_surfaces,
        "consumer_view_json": consumer_view,
    }

    hits: dict[str, Any] = {}
    for name, payload in surfaces_to_search.items():
        local_hits: list[tuple[str, Any]] = []
        find_key_recursive(payload, "mist_call", local_hits)
        hits[name] = [
            {
                "path": p,
                "summary": summarize_branch(v),
            }
            for p, v in local_hits[:20]
        ]

    direct = {
        "family_features_mist_call": summarize_branch(family_features.get("mist_call") if isinstance(family_features, dict) else None),
        "family_surfaces_mist_call": summarize_branch(family_surfaces.get("mist_call") if isinstance(family_surfaces, dict) else None),
        "consumer_view_mist_call": summarize_branch(consumer_view.get("mist_call") if isinstance(consumer_view, dict) else None),
    }

    branch_frames = {}
    if isinstance(consumer_view, dict) and isinstance(consumer_view.get("branch_frames"), dict):
        branch_frames = consumer_view["branch_frames"]
    elif isinstance(family_surfaces, dict) and isinstance(family_surfaces.get("branch_frames"), dict):
        branch_frames = family_surfaces["branch_frames"]
    elif isinstance(family_features, dict) and isinstance(family_features.get("branch_frames"), dict):
        branch_frames = family_features["branch_frames"]

    branch_frame_mist_call = summarize_branch(branch_frames.get("mist_call") if isinstance(branch_frames, dict) else None)

    data_valid_candidates = {}
    for name, payload in surfaces_to_search.items():
        if isinstance(payload, dict):
            data_valid_candidates[name] = {
                "data_valid": payload.get("data_valid"),
                "safe_to_consume": payload.get("safe_to_consume"),
                "consumer_view_valid": payload.get("consumer_view_valid"),
                "view_data_valid": payload.get("view_data_valid"),
                "family_count": payload.get("family_count"),
                "branch_count": payload.get("branch_count"),
                "keys": sorted(payload.keys())[:100],
            }

    source_terms = {}
    for rel in [
        "app/mme_scalpx/services/strategy.py",
        "app/mme_scalpx/services/strategy_family/activation.py",
        "app/mme_scalpx/services/strategy_family/eligibility.py",
        "app/mme_scalpx/services/strategy_family/arbitration.py",
        "app/mme_scalpx/services/strategy_family/mist.py",
        "app/mme_scalpx/services/features.py",
    ]:
        text = read(rel)
        source_terms[rel] = {
            "exists": bool(text),
            "view_data_invalid_count": text.count("view_data_invalid"),
            "leaf_evaluation_skipped_count": text.count("leaf_evaluation_skipped"),
            "branch_frames_count": text.count("branch_frames"),
            "family_features_json_count": text.count("family_features_json"),
            "family_surfaces_json_count": text.count("family_surfaces_json"),
            "consumer_view_json_count": text.count("consumer_view_json"),
            "mist_call_count": text.count("mist_call"),
            "safe_to_consume_count": text.count("safe_to_consume"),
            "data_valid_count": text.count("data_valid"),
        }

    observed_activation = {
        "latest_contains_view_data_invalid": "view_data_invalid" in latest,
        "latest_contains_leaf_evaluation_skipped": "leaf_evaluation_skipped" in latest,
        "latest_contains_activation_candidate_count_zero": "activation_candidate_count\n0" in latest or '"activation_candidate_count":0' in latest,
        "latest_contains_dry_run": "dry_run" in latest,
        "latest_contains_hold": "HOLD" in latest,
        "latest_contains_safe_to_promote_false": "safe_to_promote\nfalse" in latest or '"safe_to_promote":false' in latest,
    }

    proof = {
        "batch": "26O15",
        "name": "activation_candidate_surface_audit",
        "created_at": now_iso(),
        "redis_ping": cmd(["redis-cli", "PING"], 5),
        "orders_len": cmd(["redis-cli", "XLEN", "orders:mme:stream"], 5),
        "position": position,
        "provider_core": {
            "futures_marketdata_status": provider.get("futures_marketdata_status"),
            "selected_option_marketdata_status": provider.get("selected_option_marketdata_status"),
            "option_context_status": provider.get("option_context_status"),
            "execution_primary_status": provider.get("execution_primary_status"),
            "provider_ready_classic": provider.get("provider_ready_classic"),
            "provider_ready_miso": provider.get("provider_ready_miso"),
        },
        "features_hash_keys": sorted(features_hash.keys()),
        "payload_presence": {
            "family_features_json": isinstance(family_features, dict),
            "family_surfaces_json": isinstance(family_surfaces, dict),
            "consumer_view_json": isinstance(consumer_view, dict),
        },
        "data_valid_candidates": data_valid_candidates,
        "direct_mist_call": direct,
        "branch_frame_mist_call": branch_frame_mist_call,
        "recursive_mist_call_hits": hits,
        "observed_activation": observed_activation,
        "latest_decision_tail": latest[-12000:],
        "source_terms": source_terms,
        "prior_proofs": {
            "o8": load_json("run/proofs/proof_batch26o8_live_25v_gate.json").get("final_verdict"),
            "o13": load_json("run/proofs/proof_batch26o13_activation_bridge_audit.json").get("final_verdict"),
            "o14": load_json("run/proofs/proof_batch26o14_controlled_activation_bridge.json").get("final_verdict"),
        },
        "processes": {
            "feeds": pgrep("app.mme_scalpx.main --service feeds"),
            "features": pgrep("app.mme_scalpx.main --service features"),
            "strategy": pgrep("app.mme_scalpx.main --service strategy"),
            "risk": pgrep("app.mme_scalpx.main --service risk"),
            "execution": pgrep("app.mme_scalpx.main --service execution"),
        },
        "patch_performed": False,
        "paper_start_requested": False,
        "real_live_approved": False,
    }

    mist_call_present_anywhere = any(
        item.get("summary", {}).get("present") for group in hits.values() for item in group
    ) or any(v.get("present") for v in direct.values()) or branch_frame_mist_call.get("present")

    mist_call_eligible_anywhere = any(
        item.get("summary", {}).get("eligible") is True for group in hits.values() for item in group
    ) or any(v.get("eligible") is True for v in direct.values()) or branch_frame_mist_call.get("eligible") is True

    proof["conclusions"] = {
        "mist_call_present_anywhere": bool(mist_call_present_anywhere),
        "mist_call_eligible_anywhere": bool(mist_call_eligible_anywhere),
        "activation_fails_before_leaf_eval": observed_activation["latest_contains_leaf_evaluation_skipped"],
        "activation_view_data_invalid": observed_activation["latest_contains_view_data_invalid"],
        "candidate_count_zero": observed_activation["latest_contains_activation_candidate_count_zero"],
        "no_paper_order_safe": proof["orders_len"] == "0",
    }

    proof["o15_audit_ok"] = (
        proof["redis_ping"] == "PONG"
        and proof["orders_len"] == "0"
        and proof["payload_presence"]["family_features_json"]
        and proof["payload_presence"]["family_surfaces_json"]
        and (
            proof["conclusions"]["activation_view_data_invalid"]
            or proof["conclusions"]["activation_fails_before_leaf_eval"]
            or proof["conclusions"]["candidate_count_zero"]
        )
    )

    if proof["o15_audit_ok"]:
        if not proof["conclusions"]["mist_call_present_anywhere"]:
            next_step = "Batch 26-O16 feature-to-strategy branch-frame mapping repair"
        elif proof["conclusions"]["activation_view_data_invalid"]:
            next_step = "Batch 26-O16 strategy consumer-view data_valid mapping repair"
        elif not proof["conclusions"]["mist_call_eligible_anywhere"]:
            next_step = "Batch 26-O16 MIST CALL eligibility blocker proof/threshold design"
        else:
            next_step = "Batch 26-O16 activation candidate extraction repair"
        proof["final_verdict"] = "PASS_ACTIVATION_CANDIDATE_SURFACE_AUDIT_OK"
        proof["next_required_batch"] = next_step
    else:
        proof["final_verdict"] = "FAIL_ACTIVATION_CANDIDATE_SURFACE_AUDIT_REVIEW_REQUIRED"
        proof["next_required_batch"] = "Review O15 payload/activation evidence"

    OUT.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n")

    print(json.dumps({
        "final_verdict": proof["final_verdict"],
        "o15_audit_ok": proof["o15_audit_ok"],
        "conclusions": proof["conclusions"],
        "payload_presence": proof["payload_presence"],
        "branch_frame_mist_call": proof["branch_frame_mist_call"],
        "direct_mist_call": proof["direct_mist_call"],
        "observed_activation": proof["observed_activation"],
        "orders_len": proof["orders_len"],
        "patch_performed": proof["patch_performed"],
        "paper_start_requested": proof["paper_start_requested"],
        "real_live_approved": proof["real_live_approved"],
        "next_required_batch": proof["next_required_batch"],
    }, indent=2, sort_keys=True))
    return 0 if proof["final_verdict"].startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
