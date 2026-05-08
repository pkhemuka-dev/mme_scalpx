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

SCAN_FILES = [
    Path("app/mme_scalpx/replay/live_capture_executor.py"),
    Path("bin/observe_only_market_session_capture_execute.py"),
]

FORBIDDEN_IMPORTS = ["kiteconnect", "broker_api", "broker_auth", "zerodha_execution", "dhan_execution"]
FORBIDDEN_CALLS = ["place_order", "modify_order", "cancel_order", "send_order", "flatten_position", "broker_flatten", "xadd", "hset", "publish", "Popen", "system"]


def load_json(path: Path) -> dict:
    if not path.exists():
        return {"missing": True}
    return json.loads(path.read_text(encoding="utf-8"))


def scan(path: Path) -> dict:
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    imports = []
    calls = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if any(item in alias.name.lower() for item in FORBIDDEN_IMPORTS):
                    imports.append({"line": node.lineno, "import": alias.name})
        elif isinstance(node, ast.ImportFrom):
            module = (node.module or "").lower()
            if any(item in module for item in FORBIDDEN_IMPORTS):
                imports.append({"line": node.lineno, "import_from": node.module})
        elif isinstance(node, ast.Call):
            name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else ""
            if name in FORBIDDEN_CALLS:
                calls.append({"line": node.lineno, "call": name})

    return {
        "path": str(path),
        "ok": not imports and not calls,
        "forbidden_imports": imports,
        "forbidden_calls": calls,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_observe_only_market_session_capture_execution_no_enablement.json")
    args = parser.parse_args()

    execution_contract = load_json(Path("run/proofs/proof_observe_only_market_session_capture_execution_contract.json"))
    proof28d = load_json(Path("run/proofs/proof_observe_only_market_session_capture_28d_latest.json"))
    no_broker = load_json(Path("run/proofs/proof_replay_no_broker_call.json"))
    no_redis = load_json(Path("run/proofs/proof_replay_no_live_redis_write.json"))
    no_promotion = load_json(Path("run/proofs/proof_replay_no_runtime_promotion.json"))

    scans = [scan(p) for p in SCAN_FILES]
    static_scan_ok = all(item["ok"] for item in scans)

    ok = bool(
        static_scan_ok
        and execution_contract.get("observe_only_market_session_capture_execution_contract_ok") is True
        and execution_contract.get("execute_in_28e") is False
        and execution_contract.get("actual_live_market_capture_in_28e") is False
        and execution_contract.get("starts_services") is False
        and execution_contract.get("reads_live_redis") is False
        and execution_contract.get("writes_live_redis") is False
        and execution_contract.get("calls_broker_api") is False
        and execution_contract.get("paper_armed_approved") is False
        and execution_contract.get("live_trading_approved") is False
        and execution_contract.get("full_live_replay_parity") == "NOT_PROVEN_IN_28E"
        and proof28d.get("observe_only_market_session_capture_28d_ok") is True
        and no_broker.get("broker_call_reachable") is False
        and no_redis.get("live_redis_write_reachable") is False
        and no_promotion.get("runtime_promotion_reachable") is False
    )

    proof = {
        "schema_version": "proof_observe_only_market_session_capture_execution_no_enablement_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "observe_only_market_session_capture_execution_no_enablement_ok": ok,
        "static_scan_ok": static_scan_ok,
        "scan_results": scans,
        "execute_in_28e": False,
        "actual_live_market_capture_in_28e": False,
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
        "paper_armed_readiness": "NOT_APPROVED_IN_28E",
        "live_trading_readiness": "NOT_APPROVED_IN_28E",
        "production_strategy_improvement_claim": "NOT_PROVEN_IN_28E",
        "production_doctrine_revision": "NOT_APPROVED_IN_28E",
        "full_live_replay_parity": "NOT_PROVEN_IN_28E",
        "verdict": "PASS_OBSERVE_ONLY_MARKET_SESSION_CAPTURE_EXECUTION_NO_ENABLEMENT" if ok else "FAIL_REVIEW_REQUIRED",
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"verdict": proof["verdict"], "ok": ok}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
