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

# Scan only the 28B operational surface.
# Do not scan proof scripts themselves; proof scripts may contain scanner helper
# code such as set(), tuple(), dict(), and AST logic that is not runtime reachability.
SCAN_FILES = tuple([
    Path("app/mme_scalpx/replay/live_evidence.py"),
    Path("bin/observe_only_live_evidence_collect.py"),
])

FORBIDDEN_IMPORT_FRAGMENTS = tuple([
    "redis",
    "kiteconnect",
    "broker_api",
    "broker_auth",
    "zerodha_execution",
    "dhan_execution",
])

FORBIDDEN_RUNTIME_CALLS = tuple([
    "place_order",
    "modify_order",
    "cancel_order",
    "send_order",
    "flatten_position",
    "broker_flatten",
    "xadd",
    "hset",
    "publish",
])


def load_json(path: Path) -> dict:
    if not path.exists():
        return {"missing": True, "verdict": "MISSING"}
    return json.loads(path.read_text(encoding="utf-8"))


def scan_file(path: Path) -> dict:
    if not path.exists():
        return {
            "path": str(path),
            "exists": False,
            "ok": False,
            "reason": "missing",
            "forbidden_imports": [],
            "forbidden_calls": [],
        }

    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return {
            "path": str(path),
            "exists": True,
            "ok": False,
            "reason": "syntax_error",
            "error": str(exc),
            "forbidden_imports": [],
            "forbidden_calls": [],
        }

    imports = []
    calls = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                lowered = alias.name.lower()
                if any(fragment in lowered for fragment in FORBIDDEN_IMPORT_FRAGMENTS):
                    imports.append({"line": node.lineno, "import": alias.name})

        elif isinstance(node, ast.ImportFrom):
            lowered = (node.module or "").lower()
            if any(fragment in lowered for fragment in FORBIDDEN_IMPORT_FRAGMENTS):
                imports.append({"line": node.lineno, "import_from": node.module})

        elif isinstance(node, ast.Call):
            name = ""
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr

            # Deliberately do not ban Python builtins such as set(), dict(), tuple().
            if name in FORBIDDEN_RUNTIME_CALLS:
                calls.append({"line": node.lineno, "call": name})

    ok = not imports and not calls
    return {
        "path": str(path),
        "exists": True,
        "ok": ok,
        "forbidden_imports": imports,
        "forbidden_calls": calls,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_observe_only_live_evidence_no_enablement.json")
    args = parser.parse_args()

    contract = load_json(ROOT / "run/proofs/proof_observe_only_live_evidence_capture_contract.json")
    plan28a = load_json(ROOT / "run/proofs/proof_replay_live_parity_audit_plan_28a_latest.json")
    no_broker = load_json(ROOT / "run/proofs/proof_replay_no_broker_call.json")
    no_redis = load_json(ROOT / "run/proofs/proof_replay_no_live_redis_write.json")
    no_promotion = load_json(ROOT / "run/proofs/proof_replay_no_runtime_promotion.json")

    scans = [scan_file(p) for p in SCAN_FILES]
    static_scan_ok = all(row.get("ok") is True for row in scans)

    no_enablement_ok = (
        static_scan_ok
        and contract.get("observe_only_live_evidence_capture_contract_ok") is True
        and contract.get("starts_services") is False
        and contract.get("reads_live_redis") is False
        and contract.get("writes_live_redis") is False
        and contract.get("calls_broker_api") is False
        and contract.get("paper_armed_approved") is False
        and contract.get("live_trading_approved") is False
        and contract.get("actual_live_evidence_collected") is False
        and contract.get("full_live_replay_parity") == "NOT_PROVEN_IN_28B"
        and plan28a.get("replay_live_parity_audit_plan_28a_ok") is True
        and plan28a.get("paper_armed_approved") is False
        and plan28a.get("live_trading_approved") is False
        and no_broker.get("broker_call_reachable") is False
        and no_redis.get("live_redis_write_reachable") is False
        and no_promotion.get("runtime_promotion_reachable") is False
    )

    proof = {
        "schema_version": "proof_observe_only_live_evidence_no_enablement_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "observe_only_live_evidence_no_enablement_ok": no_enablement_ok,
        "static_scan_ok": static_scan_ok,
        "scan_scope": [str(p) for p in SCAN_FILES],
        "scan_results": scans,
        "starts_services": False,
        "reads_live_redis": False,
        "writes_live_redis": False,
        "calls_broker_api": False,
        "broker_call_reachable": no_broker.get("broker_call_reachable"),
        "live_redis_write_reachable": no_redis.get("live_redis_write_reachable"),
        "runtime_promotion_reachable": no_promotion.get("runtime_promotion_reachable"),
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "paper_armed_readiness": "NOT_APPROVED_IN_28B",
        "live_trading_readiness": "NOT_APPROVED_IN_28B",
        "production_strategy_improvement_claim": "NOT_PROVEN_IN_28B",
        "production_doctrine_revision": "NOT_APPROVED_IN_28B",
        "full_live_replay_parity": "NOT_PROVEN_IN_28B",
        "verdict": "PASS_OBSERVE_ONLY_LIVE_EVIDENCE_NO_ENABLEMENT" if no_enablement_ok else "FAIL_REVIEW_REQUIRED",
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "proof": str(out),
        "verdict": proof["verdict"],
        "observe_only_live_evidence_no_enablement_ok": no_enablement_ok,
        "static_scan_ok": static_scan_ok,
        "scan_scope": proof["scan_scope"],
        "starts_services": False,
        "reads_live_redis": False,
        "writes_live_redis": False,
        "calls_broker_api": False,
        "broker_call_reachable": proof["broker_call_reachable"],
        "live_redis_write_reachable": proof["live_redis_write_reachable"],
        "runtime_promotion_reachable": proof["runtime_promotion_reachable"],
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28B",
    }, indent=2, sort_keys=True))

    return 0 if no_enablement_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
