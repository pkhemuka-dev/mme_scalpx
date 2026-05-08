#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path("/home/Lenovo/scalpx/projects/mme_scalpx")
OUT = ROOT / "run/proofs/proof_batch26o8_live_25v_gate.json"

PROOFS = [
    {
        "name": "provider_runtime",
        "script": "bin/proof_market_session_provider_runtime.py",
        "proof": "run/proofs/proof_market_session_provider_runtime.json",
        "ok_field": "market_session_provider_runtime_ok",
    },
    {
        "name": "feed_snapshot",
        "script": "bin/proof_market_session_feed_snapshot.py",
        "proof": "run/proofs/proof_market_session_feed_snapshot.json",
        "ok_field": "market_session_feed_snapshot_ok",
    },
    {
        "name": "feature_payload",
        "script": "bin/proof_market_session_feature_payload.py",
        "proof": "run/proofs/proof_market_session_feature_payload.json",
        "ok_field": "market_session_feature_payload_ok",
    },
    {
        "name": "family_surfaces",
        "script": "bin/proof_market_session_family_surfaces.py",
        "proof": "run/proofs/proof_market_session_family_surfaces.json",
        "ok_field": "market_session_family_surfaces_ok",
    },
    {
        "name": "strategy_activation",
        "script": "bin/proof_market_session_strategy_activation.py",
        "proof": "run/proofs/proof_market_session_strategy_activation.json",
        "ok_field": "market_session_strategy_activation_ok",
    },
    {
        "name": "no_order_sent",
        "script": "bin/proof_market_session_no_order_sent.py",
        "proof": "run/proofs/proof_market_session_no_order_sent.json",
        "ok_field": "market_session_no_order_sent_ok",
    },
]

POSITION_KEY = "state:position:mme"
ORDERS_STREAM = "orders:mme:stream"
PROVIDER_KEY = "state:provider:runtime"
FUT_KEY = "state:snapshot:mme:fut:active"
OPT_KEY = "state:snapshot:mme:opt:selected:active"
DHAN_KEY = "state:context:mme:dhan"
HEALTH_FEEDS_KEY = "health:feeds"

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def cmd(args: list[str], timeout: float = 10.0, env: dict[str, str] | None = None) -> dict[str, Any]:
    start = time.perf_counter()
    try:
        cp = subprocess.run(
            args,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            env=env,
        )
        return {
            "ok": cp.returncode == 0,
            "returncode": cp.returncode,
            "stdout": cp.stdout.strip(),
            "stderr": cp.stderr.strip(),
            "elapsed_ms": round((time.perf_counter() - start) * 1000, 2),
        }
    except Exception as exc:
        return {
            "ok": False,
            "returncode": -1,
            "stdout": "",
            "stderr": repr(exc),
            "elapsed_ms": round((time.perf_counter() - start) * 1000, 2),
        }

def rcli(*args: str, timeout: float = 5.0) -> dict[str, Any]:
    return cmd(["redis-cli", *args], timeout=timeout)

def hgetall(key: str) -> dict[str, str]:
    raw = rcli("HGETALL", key)["stdout"].splitlines()
    d: dict[str, str] = {}
    for i in range(0, len(raw) - 1, 2):
        d[raw[i]] = raw[i + 1]
    return d

def exists(key: str) -> bool:
    return rcli("EXISTS", key)["stdout"] == "1"

def xlen(stream: str) -> str:
    return rcli("XLEN", stream)["stdout"]

def pgrep(pattern: str) -> list[str]:
    raw = cmd(["bash", "-lc", f"pgrep -af {pattern!r} || true"])["stdout"].splitlines()
    return [
        x for x in raw
        if "pgrep -af" not in x
        and "run_batch26o8_live_25v_gate.py" not in x
    ]

def disk_used_pct() -> int | None:
    line = cmd(["bash", "-lc", "df -P . | tail -1"])["stdout"]
    parts = line.split()
    if len(parts) >= 5 and parts[4].endswith("%"):
        try:
            return int(parts[4].rstrip("%"))
        except Exception:
            return None
    return None

def is_flat(pos: dict[str, str]) -> bool:
    return (
        pos.get("has_position") == "0"
        and pos.get("position_side") == "FLAT"
        and pos.get("qty_lots") == "0"
        and pos.get("qty_units") == "0"
    )

def parse_json_file(path: str) -> dict[str, Any]:
    p = ROOT / path
    if not p.exists():
        return {"_missing": True}
    try:
        return json.loads(p.read_text(errors="replace"))
    except Exception as exc:
        return {"_parse_error": repr(exc)}

def script_exists_and_compiles(script: str) -> dict[str, Any]:
    p = ROOT / script
    if not p.exists():
        return {"exists": False, "compile_ok": False}
    c = cmd([sys.executable, "-m", "py_compile", script], timeout=20)
    return {"exists": True, "compile_ok": bool(c["ok"]), "compile": c}

def latest_safe_state() -> dict[str, Any]:
    pos = hgetall(POSITION_KEY)
    disk_pct = disk_used_pct()
    risk = pgrep("app.mme_scalpx.main --service risk")
    execution = pgrep("app.mme_scalpx.main --service execution")

    return {
        "redis_ping": rcli("PING")["stdout"],
        "disk_used_pct": disk_pct,
        "disk_below_85": disk_pct is not None and disk_pct < 85,
        "orders_len": xlen(ORDERS_STREAM),
        "orders_zero": xlen(ORDERS_STREAM) == "0",
        "position_hash_present": bool(pos),
        "position_flat": is_flat(pos),
        "provider_runtime_hash_present": exists(PROVIDER_KEY),
        "fut_active_hash_present": exists(FUT_KEY),
        "opt_active_hash_present": exists(OPT_KEY),
        "dhan_context_hash_present": exists(DHAN_KEY),
        "health_feeds_present": exists(HEALTH_FEEDS_KEY),
        "risk_process_count": len(risk),
        "execution_process_count": len(execution),
        "risk_processes": risk,
        "execution_processes": execution,
    }

def run_one_proof(spec: dict[str, str], observe_seconds: int, timeout_sec: int) -> dict[str, Any]:
    env = dict(os.environ)
    env["BATCH25V_OBSERVE_SECONDS"] = str(observe_seconds)

    before_mtime = None
    proof_path = ROOT / spec["proof"]
    if proof_path.exists():
        before_mtime = proof_path.stat().st_mtime

    result = cmd([sys.executable, spec["script"]], timeout=timeout_sec, env=env)

    proof_data = parse_json_file(spec["proof"])
    after_mtime = proof_path.stat().st_mtime if proof_path.exists() else None

    ok_field = spec["ok_field"]
    ok_value = proof_data.get(ok_field)

    return {
        "name": spec["name"],
        "script": spec["script"],
        "proof": spec["proof"],
        "ok_field": ok_field,
        "ok_value": ok_value,
        "script_returncode": result["returncode"],
        "script_ok": result["ok"],
        "elapsed_ms": result["elapsed_ms"],
        "stdout_tail": result["stdout"][-4000:],
        "stderr_tail": result["stderr"][-4000:],
        "proof_updated": after_mtime is not None and after_mtime != before_mtime,
        "proof_data_head": {k: proof_data.get(k) for k in sorted(proof_data.keys())[:80]} if isinstance(proof_data, dict) else {},
        "pass": ok_value is True,
    }

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--install-proof", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--observe-seconds", type=int, default=int(os.environ.get("BATCH25V_OBSERVE_SECONDS", "60")))
    ap.add_argument("--timeout-sec", type=int, default=120)
    args = ap.parse_args()

    mode = "run" if args.run else "install_proof"

    compile_checks = {p["name"]: script_exists_and_compiles(p["script"]) for p in PROOFS}
    support_compile = {
        "o7": script_exists_and_compiles("bin/proof_batch26o7_controlled_runtime_start_preflight.py"),
        "observer": script_exists_and_compiles("bin/live_signal_forensics_observer.py"),
    }

    safe_before = latest_safe_state()

    proof: dict[str, Any] = {
        "batch": "26O8",
        "name": "live_25v_gate",
        "created_at": now_iso(),
        "mode": mode,
        "observe_seconds": args.observe_seconds,
        "timeout_sec": args.timeout_sec,
        "real_live_approved": False,
        "paper_order_approved": False,
        "compile_checks": compile_checks,
        "support_compile": support_compile,
        "safe_before": safe_before,
        "results": {},
    }

    install_ok = (
        all(v["exists"] and v["compile_ok"] for v in compile_checks.values())
        and all(v["exists"] and v["compile_ok"] for v in support_compile.values())
        and safe_before["redis_ping"] == "PONG"
        and safe_before["disk_below_85"]
        and safe_before["orders_zero"]
        and safe_before["position_hash_present"]
        and safe_before["position_flat"]
        and safe_before["provider_runtime_hash_present"]
        and safe_before["fut_active_hash_present"]
        and safe_before["opt_active_hash_present"]
        and safe_before["dhan_context_hash_present"]
        and safe_before["health_feeds_present"]
    )

    proof["install_ok"] = install_ok

    if args.run:
        if not install_ok:
            proof["final_verdict"] = "FAIL_O8_PREFLIGHT_BEFORE_LIVE_25V_GATE"
            proof["batch26o8_live_25v_gate_ok"] = False
        else:
            for spec in PROOFS:
                proof["results"][spec["name"]] = run_one_proof(spec, args.observe_seconds, args.timeout_sec)

            proof["market_session_provider_runtime_ok"] = proof["results"].get("provider_runtime", {}).get("pass") is True
            proof["market_session_feed_snapshot_ok"] = proof["results"].get("feed_snapshot", {}).get("pass") is True
            proof["market_session_feature_payload_ok"] = proof["results"].get("feature_payload", {}).get("pass") is True
            proof["market_session_family_surfaces_ok"] = proof["results"].get("family_surfaces", {}).get("pass") is True
            proof["market_session_strategy_activation_ok"] = proof["results"].get("strategy_activation", {}).get("pass") is True
            proof["market_session_no_order_sent_ok"] = proof["results"].get("no_order_sent", {}).get("pass") is True

            proof["safe_after"] = latest_safe_state()
            proof["orders_still_zero_after"] = proof["safe_after"]["orders_zero"]

            proof["batch26o8_live_25v_gate_ok"] = all([
                proof["market_session_provider_runtime_ok"],
                proof["market_session_feed_snapshot_ok"],
                proof["market_session_feature_payload_ok"],
                proof["market_session_family_surfaces_ok"],
                proof["market_session_strategy_activation_ok"],
                proof["market_session_no_order_sent_ok"],
                proof["orders_still_zero_after"],
            ])

            proof["final_verdict"] = (
                "PASS_BATCH26O8_LIVE_25V_GATE_OK"
                if proof["batch26o8_live_25v_gate_ok"]
                else "FAIL_BATCH26O8_LIVE_25V_GATE_REVIEW_REQUIRED"
            )
    else:
        proof["market_session_provider_runtime_ok"] = None
        proof["market_session_feed_snapshot_ok"] = None
        proof["market_session_feature_payload_ok"] = None
        proof["market_session_family_surfaces_ok"] = None
        proof["market_session_strategy_activation_ok"] = None
        proof["market_session_no_order_sent_ok"] = None
        proof["batch26o8_live_25v_gate_ok"] = None
        proof["final_verdict"] = (
            "PASS_O8_AGGREGATOR_INSTALLED_READY_FOR_LIVE_RUN"
            if install_ok
            else "FAIL_O8_AGGREGATOR_INSTALL_REVIEW_REQUIRED"
        )

    proof["failed_items"] = []
    if args.run:
        for k in [
            "market_session_provider_runtime_ok",
            "market_session_feed_snapshot_ok",
            "market_session_feature_payload_ok",
            "market_session_family_surfaces_ok",
            "market_session_strategy_activation_ok",
            "market_session_no_order_sent_ok",
        ]:
            if proof.get(k) is not True:
                proof["failed_items"].append(k)

    proof["next_required_batch"] = (
        "Batch 26-O9 controlled paper preflight"
        if proof.get("batch26o8_live_25v_gate_ok") is True
        else "Run O8 during live market with --run"
        if proof["final_verdict"] == "PASS_O8_AGGREGATOR_INSTALLED_READY_FOR_LIVE_RUN"
        else "Review O8 failed_items before paper"
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n")

    print(json.dumps({
        "final_verdict": proof["final_verdict"],
        "install_ok": proof.get("install_ok"),
        "batch26o8_live_25v_gate_ok": proof.get("batch26o8_live_25v_gate_ok"),
        "market_session_provider_runtime_ok": proof.get("market_session_provider_runtime_ok"),
        "market_session_feed_snapshot_ok": proof.get("market_session_feed_snapshot_ok"),
        "market_session_feature_payload_ok": proof.get("market_session_feature_payload_ok"),
        "market_session_family_surfaces_ok": proof.get("market_session_family_surfaces_ok"),
        "market_session_strategy_activation_ok": proof.get("market_session_strategy_activation_ok"),
        "market_session_no_order_sent_ok": proof.get("market_session_no_order_sent_ok"),
        "failed_items": proof.get("failed_items"),
        "next_required_batch": proof.get("next_required_batch"),
    }, indent=2, sort_keys=True))

    return 0 if proof["final_verdict"].startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
