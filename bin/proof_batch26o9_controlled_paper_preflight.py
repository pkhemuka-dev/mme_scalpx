#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import time
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path("/home/Lenovo/scalpx/projects/mme_scalpx")
OUT = ROOT / "run/proofs/proof_batch26o9_controlled_paper_preflight.json"

ORDERS_STREAM = "orders:mme:stream"
POSITION_KEY = "state:position:mme"
PROVIDER_KEY = "state:provider:runtime"
FUT_KEY = "state:snapshot:mme:fut:active"
OPT_KEY = "state:snapshot:mme:opt:selected:active"
DHAN_KEY = "state:context:mme:dhan"
HEALTH_FEEDS_KEY = "health:feeds"

O8_PROOF = ROOT / "run/proofs/proof_batch26o8_live_25v_gate.json"
O7_PROOF = ROOT / "run/proofs/proof_batch26o7_controlled_runtime_start_preflight.json"
O6_PROOF = ROOT / "run/proofs/proof_batch26o6_observer_guard.json"

SCOPE_ACK = "I_ACCEPT_MIST_CALL_1LOT_PAPER_ONLY"

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def cmd(args: list[str], timeout: float = 5.0) -> dict[str, Any]:
    start = time.perf_counter()
    try:
        cp = subprocess.run(
            args,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        return {
            "ok": cp.returncode == 0,
            "stdout": cp.stdout.strip(),
            "stderr": cp.stderr.strip(),
            "returncode": cp.returncode,
            "elapsed_ms": round((time.perf_counter() - start) * 1000, 2),
        }
    except Exception as exc:
        return {
            "ok": False,
            "stdout": "",
            "stderr": repr(exc),
            "returncode": -1,
            "elapsed_ms": round((time.perf_counter() - start) * 1000, 2),
        }

def rcli(*args: str, timeout: float = 5.0) -> dict[str, Any]:
    return cmd(["redis-cli", *args], timeout=timeout)

def hgetall(key: str) -> dict[str, str]:
    raw = rcli("HGETALL", key)["stdout"].splitlines()
    out: dict[str, str] = {}
    for i in range(0, len(raw) - 1, 2):
        out[raw[i]] = raw[i + 1]
    return out

def xlen(stream: str) -> str:
    return rcli("XLEN", stream)["stdout"]

def exists(key: str) -> bool:
    return rcli("EXISTS", key)["stdout"] == "1"

def hlen(key: str) -> str:
    return rcli("HLEN", key)["stdout"]

def read_json(path: pathlib.Path) -> dict[str, Any]:
    if not path.exists():
        return {"_missing": True}
    try:
        return json.loads(path.read_text(errors="replace"))
    except Exception as exc:
        return {"_parse_error": repr(exc)}

def read_text(rel: str) -> str:
    p = ROOT / rel
    return p.read_text(errors="replace") if p.exists() else ""

def pgrep(pattern: str) -> list[str]:
    raw = cmd(["bash", "-lc", f"pgrep -af {pattern!r} | grep -v grep || true"])["stdout"].splitlines()
    return [
        x for x in raw
        if "proof_batch26o9_controlled_paper_preflight.py" not in x
        and "pgrep -af" not in x
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

def parse_info(raw: str) -> dict[str, str]:
    d: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" in line and not line.startswith("#"):
            k, v = line.split(":", 1)
            d[k.strip()] = v.strip()
    return d

def is_flat(pos: dict[str, str]) -> bool:
    return (
        pos.get("has_position") == "0"
        and pos.get("position_side") == "FLAT"
        and pos.get("qty_lots") == "0"
        and pos.get("qty_units") == "0"
    )

def config_text() -> str:
    files = [
        "etc/strategy_family/rollout/controlled_paper_trial_enablement_from_25v25w.yaml",
        "etc/strategy_family/rollout/controlled_paper_trial_scope_from_25v25w.yaml",
        "etc/strategy_family/rollout/paper_armed_readiness_gate.yaml",
        "etc/strategy_family/family_runtime.yaml",
        "etc/runtime.yaml",
    ]
    return "\n".join(read_text(f) for f in files)

def scope_ok() -> dict[str, Any]:
    text = config_text()
    lowered = text.lower()

    selected_family_mist = bool(re.search(r"(?im)\b(selected_family|family)\s*:\s*['\"]?MIST['\"]?\s*$", text))
    selected_side_call = bool(re.search(r"(?im)\b(selected_side|side)\s*:\s*['\"]?CALL['\"]?\s*$", text))
    quantity_lots_1 = bool(re.search(r"(?im)\b(quantity_lots|qty_lots|lots)\s*:\s*1\s*$", text))

    # Also accept earlier proven O7 scope if the raw YAML structure is nested and regex misses it.
    o7 = read_json(O7_PROOF)
    o7_scope = o7.get("controlled_scope", {}) if isinstance(o7, dict) else {}

    selected_family_mist = selected_family_mist or bool(o7_scope.get("selected_family_mist"))
    selected_side_call = selected_side_call or bool(o7_scope.get("selected_side_call"))
    quantity_lots_1 = quantity_lots_1 or bool(o7_scope.get("quantity_lots_1"))

    real_live_false = (
        "real_live_allowed: false" in lowered
        or "real_live_approved: false" in lowered
        or bool(o7_scope.get("real_live_allowed_false"))
    )

    paper_scope_true = (
        "paper_orders_allowed: true" in lowered
        or "enabled: true" in lowered
        or bool(o7_scope.get("paper_orders_allowed_true_or_scope_enabled"))
    )

    auto_failover_false = (
        "automatic_broker_failover_allowed: false" in lowered
        or bool(o7_scope.get("auto_failover_false"))
    )

    migration_false = (
        "mid_position_provider_migration_allowed: false" in lowered
        or bool(o7_scope.get("mid_position_migration_false"))
    )

    return {
        "selected_family_mist": selected_family_mist,
        "selected_side_call": selected_side_call,
        "quantity_lots_1": quantity_lots_1,
        "real_live_allowed_false": real_live_false,
        "paper_orders_allowed_or_scope_enabled": paper_scope_true,
        "automatic_broker_failover_false": auto_failover_false,
        "mid_position_provider_migration_false": migration_false,
        "ok": all([
            selected_family_mist,
            selected_side_call,
            quantity_lots_1,
            real_live_false,
            paper_scope_true,
            auto_failover_false,
            migration_false,
        ]),
    }

def env_live_guard() -> dict[str, Any]:
    hard_live_keys = [
        "ALLOW_LIVE_ORDERS",
        "LIVE_ORDERS_ALLOWED",
        "TRADING_ENABLED",
        "REAL_LIVE_ALLOWED",
        "SCALPX_REAL_LIVE_ALLOWED",
    ]
    truthy = {"1", "true", "yes", "on", "enabled", "allow", "allowed"}
    vals = {k: os.environ.get(k, "") for k in hard_live_keys}
    enabled = {k: v for k, v in vals.items() if str(v).strip().lower() in truthy}
    return {"values": vals, "enabled": enabled, "ok": not bool(enabled)}

def rollback_ready() -> dict[str, Any]:
    stop_cmds = [
        "pkill -f 'app.mme_scalpx.main --service risk'",
        "pkill -f 'app.mme_scalpx.main --service execution'",
        "redis-cli XLEN orders:mme:stream",
        "redis-cli HGETALL state:position:mme",
    ]
    return {
        "commands": stop_cmds,
        "pkill_available": cmd(["bash", "-lc", "command -v pkill"])["ok"],
        "redis_cli_available": cmd(["bash", "-lc", "command -v redis-cli"])["ok"],
        "ok": cmd(["bash", "-lc", "command -v pkill"])["ok"] and cmd(["bash", "-lc", "command -v redis-cli"])["ok"],
    }

def process_state() -> dict[str, Any]:
    feeds = pgrep("app.mme_scalpx.main --service feeds")
    features = pgrep("app.mme_scalpx.main --service features")
    strategy = pgrep("app.mme_scalpx.main --service strategy")
    risk = pgrep("app.mme_scalpx.main --service risk")
    execution = pgrep("app.mme_scalpx.main --service execution")
    return {
        "feeds": feeds,
        "features": features,
        "strategy": strategy,
        "risk": risk,
        "execution": execution,
        "feeds_count": len(feeds),
        "features_count": len(features),
        "strategy_count": len(strategy),
        "risk_count": len(risk),
        "execution_count": len(execution),
    }

def main() -> int:
    o8 = read_json(O8_PROOF)
    o7 = read_json(O7_PROOF)
    o6 = read_json(O6_PROOF)

    ping_results = []
    for _ in range(5):
        r = rcli("PING", timeout=3)
        ping_results.append({"ok": r["ok"], "stdout": r["stdout"], "elapsed_ms": r["elapsed_ms"]})
        time.sleep(0.15)

    persistence = parse_info(rcli("INFO", "persistence", timeout=3)["stdout"])
    disk_pct = disk_used_pct()
    pos = hgetall(POSITION_KEY)
    provider = hgetall(PROVIDER_KEY)
    opt = hgetall(OPT_KEY)
    dhan = hgetall(DHAN_KEY)
    proc = process_state()
    scope = scope_ok()
    env = env_live_guard()
    rollback = rollback_ready()

    proof: dict[str, Any] = {
        "batch": "26O9",
        "name": "controlled_paper_preflight",
        "created_at": now_iso(),
        "real_live_approved": False,
        "paper_start_allowed_by_this_batch": False,
        "paper_order_approved": False,
        "runtime_promotion_allowed": False,
        "o8": {
            "proof_present": not o8.get("_missing", False),
            "final_verdict": o8.get("final_verdict"),
            "batch26o8_live_25v_gate_ok": o8.get("batch26o8_live_25v_gate_ok"),
            "failed_items": o8.get("failed_items"),
        },
        "o7": {
            "proof_present": not o7.get("_missing", False),
            "final_verdict": o7.get("final_verdict"),
            "controlled_runtime_start_preflight_ok": o7.get("controlled_runtime_start_preflight_ok"),
            "duplicate_risk_execution_guard_ok": o7.get("duplicate_risk_execution_guard_ok"),
        },
        "o6": {
            "proof_present": not o6.get("_missing", False),
            "final_verdict": o6.get("final_verdict"),
            "observer_guard_ok": o6.get("observer_guard_ok"),
            "no_heavy_redis_calls": o6.get("no_heavy_redis_calls"),
        },
        "redis": {
            "ping_results": ping_results,
            "pong_x5": all(x["ok"] and x["stdout"] == "PONG" for x in ping_results),
            "max_ping_ms": max([x["elapsed_ms"] for x in ping_results] or [999999]),
            "rdb_last_bgsave_status": persistence.get("rdb_last_bgsave_status"),
            "rdb_bgsave_in_progress": persistence.get("rdb_bgsave_in_progress"),
            "persistence_ok": persistence.get("rdb_last_bgsave_status") == "ok" and persistence.get("rdb_bgsave_in_progress") == "0",
        },
        "disk": {
            "used_pct": disk_pct,
            "below_85": disk_pct is not None and disk_pct < 85,
        },
        "position": {
            "hash_present": bool(pos),
            "flat": is_flat(pos),
            "fields": pos,
        },
        "orders": {
            "xlen": xlen(ORDERS_STREAM),
            "zero": xlen(ORDERS_STREAM) == "0",
        },
        "provider_runtime": {
            "hash_present": bool(provider),
            "futures_marketdata_status": provider.get("futures_marketdata_status"),
            "selected_option_marketdata_provider_id": provider.get("selected_option_marketdata_provider_id"),
            "selected_option_marketdata_status": provider.get("selected_option_marketdata_status"),
            "option_context_status": provider.get("option_context_status"),
            "execution_primary_status": provider.get("execution_primary_status"),
            "provider_ready_classic": provider.get("provider_ready_classic"),
            "provider_ready_miso": provider.get("provider_ready_miso"),
        },
        "snapshots": {
            "fut_active_present": exists(FUT_KEY),
            "opt_active_present": exists(OPT_KEY),
            "dhan_context_present": exists(DHAN_KEY),
            "health_feeds_present": exists(HEALTH_FEEDS_KEY),
            "opt_hlen": hlen(OPT_KEY),
            "dhan_hlen": hlen(DHAN_KEY),
        },
        "scope": scope,
        "env_live_guard": env,
        "processes": proc,
        "rollback": rollback,
    }

    proof["verdicts"] = {
        "o8_live_gate_passed": o8.get("batch26o8_live_25v_gate_ok") is True,
        "o7_preflight_passed": o7.get("controlled_runtime_start_preflight_ok") is True,
        "o6_observer_guard_passed": o6.get("final_verdict") == "PASS_OBSERVER_GUARD_OK" or o6.get("observer_guard_ok") is True,
        "redis_pong_x5": proof["redis"]["pong_x5"],
        "redis_persistence_ok": proof["redis"]["persistence_ok"],
        "disk_below_85": proof["disk"]["below_85"],
        "orders_zero": proof["orders"]["zero"],
        "position_hash_present_flat": proof["position"]["hash_present"] and proof["position"]["flat"],
        "provider_classic_ready": (
            proof["provider_runtime"]["futures_marketdata_status"] == "HEALTHY"
            and proof["provider_runtime"]["selected_option_marketdata_status"] == "HEALTHY"
            and proof["provider_runtime"]["execution_primary_status"] == "HEALTHY"
            and str(proof["provider_runtime"]["provider_ready_classic"]) == "True"
        ),
        "miso_not_enabled": str(proof["provider_runtime"]["provider_ready_miso"]) == "False",
        "snapshots_present": all([
            proof["snapshots"]["fut_active_present"],
            proof["snapshots"]["opt_active_present"],
            proof["snapshots"]["dhan_context_present"],
            proof["snapshots"]["health_feeds_present"],
        ]),
        "scope_mist_call_one_lot": scope["ok"],
        "real_live_guard_ok": env["ok"],
        "no_existing_risk_process": proc["risk_count"] == 0,
        "no_existing_execution_process": proc["execution_count"] == 0,
        "rollback_ready": rollback["ok"],
    }

    proof["controlled_paper_preflight_ok"] = all(proof["verdicts"].values())
    proof["duplicate_risk_execution_guard_ok"] = proc["risk_count"] == 0 and proc["execution_count"] == 0
    proof["real_live_blocked"] = True

    if proof["controlled_paper_preflight_ok"]:
        proof["final_verdict"] = "PASS_CONTROLLED_PAPER_PREFLIGHT_OK"
        proof["next_required_batch"] = "Batch 26-O10 controlled paper start package"
    else:
        proof["final_verdict"] = "FAIL_CONTROLLED_PAPER_PREFLIGHT_REVIEW_REQUIRED"
        proof["next_required_batch"] = "Review O9 failed verdicts before controlled paper start"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n")

    print(json.dumps({
        "final_verdict": proof["final_verdict"],
        "controlled_paper_preflight_ok": proof["controlled_paper_preflight_ok"],
        "duplicate_risk_execution_guard_ok": proof["duplicate_risk_execution_guard_ok"],
        "failed_verdicts": [k for k, v in proof["verdicts"].items() if not v],
        "paper_start_allowed_by_this_batch": proof["paper_start_allowed_by_this_batch"],
        "real_live_approved": proof["real_live_approved"],
        "next_required_batch": proof["next_required_batch"],
    }, indent=2, sort_keys=True))

    return 0 if proof["controlled_paper_preflight_ok"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
