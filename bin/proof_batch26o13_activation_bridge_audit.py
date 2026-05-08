#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import subprocess
import datetime
import re
from typing import Any

ROOT = pathlib.Path("/home/Lenovo/scalpx/projects/mme_scalpx")
OUT = ROOT / "run/proofs/proof_batch26o13_activation_bridge_audit.json"

FILES = [
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/strategy_family/activation.py",
    "app/mme_scalpx/services/strategy_family/decisions.py",
    "app/mme_scalpx/services/strategy_family/arbitration.py",
    "app/mme_scalpx/services/strategy_family/eligibility.py",
    "app/mme_scalpx/services/strategy_family/registry.py",
    "app/mme_scalpx/services/strategy_family/common.py",
    "app/mme_scalpx/services/strategy_family/mist.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
]

def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def cmd(args: list[str], timeout: float = 5.0) -> str:
    try:
        cp = subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        return cp.stdout.strip() if cp.returncode == 0 else "ERR:" + (cp.stderr.strip() or cp.stdout.strip())
    except Exception as exc:
        return "EXC:" + repr(exc)

def hgetall(key: str) -> dict[str, str]:
    raw = cmd(["redis-cli", "HGETALL", key]).splitlines()
    d: dict[str, str] = {}
    for i in range(0, len(raw) - 1, 2):
        d[raw[i]] = raw[i + 1]
    return d

def latest_decision_raw() -> str:
    return cmd(["bash", "-lc", "redis-cli XREVRANGE decisions:mme:stream + - COUNT 1 | sed -n '1,260p'"], 5)

def read(rel: str) -> str:
    p = ROOT / rel
    return p.read_text(errors="replace") if p.exists() else ""

def grep_terms(text: str, terms: list[str]) -> dict[str, int]:
    return {term: len(re.findall(re.escape(term), text)) for term in terms}

def pgrep(pattern: str) -> str:
    return cmd(["bash", "-lc", f"pgrep -af {pattern!r} | grep -v grep || true"], 5)

def load_json(path: str) -> dict[str, Any]:
    p = ROOT / path
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(errors="replace"))
    except Exception as exc:
        return {"_parse_error": repr(exc)}

def main() -> int:
    latest = latest_decision_raw()
    provider = hgetall("state:provider:runtime")
    position = hgetall("state:position:mme")
    features = hgetall("state:features:mme:fut")

    source = {}
    for rel in FILES:
        text = read(rel)
        source[rel] = {
            "exists": bool(text),
            "lines": text.count("\n") + 1 if text else 0,
            "terms": grep_terms(text, [
                "activation_mode",
                "dry_run",
                "report_only",
                "strategy_report_only",
                "safe_to_promote",
                "promoted",
                "view_data_invalid",
                "leaf_evaluation_skipped",
                "activation_candidate_count",
                "live_orders_allowed",
                "broker_side_effects_allowed",
                "order_intent",
                "controlled",
                "MIST",
                "CALL",
            ]),
        }

    observed = {
        "latest_decision_contains_dry_run": "dry_run" in latest,
        "latest_decision_contains_hold": "HOLD" in latest,
        "latest_decision_contains_view_data_invalid": "view_data_invalid" in latest,
        "latest_decision_contains_leaf_skipped": "leaf_evaluation_skipped" in latest,
        "latest_decision_contains_promoted_false": '"promoted":false' in latest or "promoted\nfalse" in latest,
        "latest_decision_contains_safe_to_promote_false": '"safe_to_promote":false' in latest or "safe_to_promote\nfalse" in latest,
        "latest_decision_contains_candidate_zero": '"activation_candidate_count":0' in latest or "activation_candidate_count\n0" in latest,
    }

    config_text = "\n".join([
        read("etc/strategy_family/rollout/controlled_paper_trial_enablement_from_25v25w.yaml"),
        read("etc/strategy_family/rollout/controlled_paper_trial_scope_from_25v25w.yaml"),
        read("etc/strategy_family/rollout/paper_armed_readiness_gate.yaml"),
    ])

    proof = {
        "batch": "26O13",
        "name": "activation_bridge_audit_no_patch",
        "created_at": now_iso(),
        "redis_ping": cmd(["redis-cli", "PING"]),
        "orders_len": cmd(["redis-cli", "XLEN", "orders:mme:stream"]),
        "position": position,
        "provider_core": {
            "futures_marketdata_status": provider.get("futures_marketdata_status"),
            "selected_option_marketdata_status": provider.get("selected_option_marketdata_status"),
            "option_context_status": provider.get("option_context_status"),
            "execution_primary_status": provider.get("execution_primary_status"),
            "provider_ready_classic": provider.get("provider_ready_classic"),
            "provider_ready_miso": provider.get("provider_ready_miso"),
        },
        "features_keys": sorted(features.keys()),
        "latest_decision_raw_tail": latest[-12000:],
        "observed_activation_blockers": observed,
        "processes": {
            "feeds": pgrep("app.mme_scalpx.main --service feeds"),
            "features": pgrep("app.mme_scalpx.main --service features"),
            "strategy": pgrep("app.mme_scalpx.main --service strategy"),
            "risk": pgrep("app.mme_scalpx.main --service risk"),
            "execution": pgrep("app.mme_scalpx.main --service execution"),
        },
        "scope_terms": {
            "mist": "MIST" in config_text,
            "call": "CALL" in config_text,
            "one_lot": "quantity_lots" in config_text and "1" in config_text,
            "real_live_false": "real_live_allowed: false" in config_text.lower() or "real_live_approved: false" in config_text.lower(),
        },
        "prior_proofs": {
            "o8": load_json("run/proofs/proof_batch26o8_live_25v_gate.json").get("final_verdict"),
            "o9": load_json("run/proofs/proof_batch26o9_controlled_paper_preflight.json").get("final_verdict"),
            "o10": load_json("run/proofs/proof_batch26o10_controlled_paper_start.json").get("final_verdict"),
        },
        "source_audit": source,
        "real_live_approved": False,
        "paper_start_requested": False,
        "patch_performed": False,
    }

    proof["activation_bridge_block_confirmed"] = (
        proof["orders_len"] == "0"
        and proof["redis_ping"] == "PONG"
        and (
            observed["latest_decision_contains_dry_run"]
            or observed["latest_decision_contains_view_data_invalid"]
            or observed["latest_decision_contains_leaf_skipped"]
            or observed["latest_decision_contains_safe_to_promote_false"]
        )
    )

    proof["activation_source_terms_present"] = (
        source["app/mme_scalpx/services/strategy.py"]["exists"]
        and (
            source["app/mme_scalpx/services/strategy.py"]["terms"]["activation_mode"] > 0
            or source["app/mme_scalpx/services/strategy_family/activation.py"]["terms"]["activation_mode"] > 0
        )
    )

    proof["final_verdict"] = (
        "PASS_ACTIVATION_BRIDGE_BLOCK_CONFIRMED_NO_PATCH"
        if proof["activation_bridge_block_confirmed"] and proof["activation_source_terms_present"]
        else "FAIL_ACTIVATION_BRIDGE_AUDIT_REVIEW_REQUIRED"
    )
    proof["next_required_batch"] = (
        "Batch 26-O14 controlled activation bridge repair, no risk/execution"
        if proof["final_verdict"].startswith("PASS")
        else "Review O13 audit before O14"
    )

    OUT.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "final_verdict": proof["final_verdict"],
        "activation_bridge_block_confirmed": proof["activation_bridge_block_confirmed"],
        "activation_source_terms_present": proof["activation_source_terms_present"],
        "observed_activation_blockers": proof["observed_activation_blockers"],
        "orders_len": proof["orders_len"],
        "real_live_approved": proof["real_live_approved"],
        "patch_performed": proof["patch_performed"],
        "next_required_batch": proof["next_required_batch"],
    }, indent=2, sort_keys=True))
    return 0 if proof["final_verdict"].startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
