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

REPLAY_SCAN_DIR = Path("app/mme_scalpx/replay")

FORBIDDEN_CALLS = {
    "place_order",
    "modify_order",
    "cancel_order",
    "send_order",
    "exit_order",
    "flatten_position",
    "broker_flatten",
}

FORBIDDEN_IMPORT_FRAGMENTS = (
    "kiteconnect",
    "broker_api",
    "broker_auth",
    "zerodha_execution",
    "dhan_execution",
)


def load_json(path: Path) -> dict:
    if not path.exists():
        return {"missing": True, "path": str(path)}
    return json.loads(path.read_text(encoding="utf-8"))


def scan_replay_python_files() -> dict:
    results = []
    ok = True

    for path in sorted(REPLAY_SCAN_DIR.rglob("*.py")):
        rel = path.as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            ok = False
            results.append({
                "path": rel,
                "ok": False,
                "syntax_error": str(exc),
                "forbidden_calls": [],
                "forbidden_imports": []
            })
            continue

        forbidden_calls = []
        forbidden_imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = ""
                if isinstance(node.func, ast.Name):
                    name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    name = node.func.attr
                if name in FORBIDDEN_CALLS:
                    forbidden_calls.append({"line": node.lineno, "call": name})

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    n = alias.name.lower()
                    if any(fragment in n for fragment in FORBIDDEN_IMPORT_FRAGMENTS):
                        forbidden_imports.append({"line": node.lineno, "import": alias.name})

            elif isinstance(node, ast.ImportFrom):
                n = (node.module or "").lower()
                if any(fragment in n for fragment in FORBIDDEN_IMPORT_FRAGMENTS):
                    forbidden_imports.append({"line": node.lineno, "import_from": node.module})

        row_ok = not forbidden_calls and not forbidden_imports
        ok = ok and row_ok
        results.append({
            "path": rel,
            "ok": row_ok,
            "forbidden_calls": forbidden_calls,
            "forbidden_imports": forbidden_imports
        })

    return {"ok": ok, "results": results, "scanned_file_count": len(results)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_replay_final_no_live_contamination.json")
    args = parser.parse_args()

    broker = load_json(ROOT / "run/proofs/proof_replay_no_broker_call.json")
    redis = load_json(ROOT / "run/proofs/proof_replay_no_live_redis_write.json")
    promotion = load_json(ROOT / "run/proofs/proof_replay_no_runtime_promotion.json")
    firewall = load_json(ROOT / "run/proofs/proof_replay_safety_firewall_latest.json")
    scan = scan_replay_python_files()

    proof_reuse_ok = (
        broker.get("verdict") == "PASS"
        and broker.get("broker_call_reachable") is False
        and redis.get("verdict") == "PASS"
        and redis.get("live_redis_write_reachable") is False
        and promotion.get("verdict") == "PASS"
        and promotion.get("runtime_promotion_reachable") is False
        and firewall.get("verdict") == "PASS_REPLAY_SAFETY_FIREWALL"
        and firewall.get("replay_safety_firewall_ok") is True
        and firewall.get("broker_call_reachable") is False
        and firewall.get("live_redis_write_reachable") is False
        and firewall.get("runtime_promotion_reachable") is False
    )

    ok = bool(scan["ok"] and proof_reuse_ok)

    proof = {
        "schema_version": "proof_replay_final_no_live_contamination_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "no_live_contamination_ok": ok,
        "static_scan_ok": scan["ok"],
        "proof_reuse_ok": proof_reuse_ok,
        "scan": scan,
        "broker_call_reachable": False if ok else broker.get("broker_call_reachable"),
        "live_redis_write_reachable": False if ok else redis.get("live_redis_write_reachable"),
        "runtime_promotion_reachable": False if ok else promotion.get("runtime_promotion_reachable"),
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_27N",
        "verdict": "PASS" if ok else "FAIL"
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "proof": str(out),
        "verdict": proof["verdict"],
        "no_live_contamination_ok": ok,
        "static_scan_ok": scan["ok"],
        "proof_reuse_ok": proof_reuse_ok,
        "scanned_file_count": scan["scanned_file_count"],
        "broker_call_reachable": proof["broker_call_reachable"],
        "live_redis_write_reachable": proof["live_redis_write_reachable"],
        "runtime_promotion_reachable": proof["runtime_promotion_reachable"],
        "paper_armed_approved": False,
        "live_trading_approved": False
    }, indent=2, sort_keys=True))

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
