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
OUT = ROOT / "run/proofs/proof_batch26o7_controlled_runtime_start_preflight.json"

POSITION_KEY = "state:position:mme"
ORDERS_STREAM = "orders:mme:stream"
PROVIDER_KEY = "state:provider:runtime"
FUT_KEY = "state:snapshot:mme:fut:active"
OPT_KEY = "state:snapshot:mme:opt:selected:active"
DHAN_KEY = "state:context:mme:dhan"
HEALTH_FEEDS_KEY = "health:feeds"

SCOPE_ACK = "I_ACCEPT_MIST_CALL_1LOT_PAPER_ONLY"

CONFIG_FILES = [
    "etc/strategy_family/rollout/controlled_paper_trial_enablement_from_25v25w.yaml",
    "etc/strategy_family/rollout/controlled_paper_trial_scope_from_25v25w.yaml",
    "etc/strategy_family/rollout/paper_armed_readiness_gate.yaml",
    "etc/strategy_family/family_runtime.yaml",
    "etc/runtime.yaml",
]

INSPECT_FILES = [
    "bin/start_controlled_paper_runtime_chain.py",
    "app/mme_scalpx/services/controlled_paper_runtime.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/settings.py",
] + CONFIG_FILES

HARD_LIVE_ENV_KEYS = [
    "ALLOW_LIVE_ORDERS",
    "LIVE_ORDERS_ALLOWED",
    "TRADING_ENABLED",
    "REAL_LIVE_ALLOWED",
    "SCALPX_REAL_LIVE_ALLOWED",
]

TRUTHY = {"1", "true", "yes", "y", "on", "enabled", "allow", "allowed"}

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

def read(rel: str) -> str:
    p = ROOT / rel
    return p.read_text(errors="replace") if p.exists() else ""

def hgetall(key: str) -> dict[str, str]:
    raw = rcli("HGETALL", key)["stdout"].splitlines()
    out: dict[str, str] = {}
    for i in range(0, len(raw) - 1, 2):
        out[raw[i]] = raw[i + 1]
    return out

def hkeys(key: str) -> list[str]:
    raw = rcli("HKEYS", key)["stdout"].splitlines()
    return [x for x in raw if x.strip()]

def exists(key: str) -> bool:
    return rcli("EXISTS", key)["stdout"] == "1"

def xlen(stream: str) -> str:
    return rcli("XLEN", stream)["stdout"]

def pgrep(pattern: str) -> list[str]:
    raw = cmd(["bash", "-lc", f"pgrep -af {pattern!r} || true"])["stdout"].splitlines()
    return [
        x for x in raw
        if "pgrep -af" not in x
        and "proof_batch26o7_controlled_runtime_start_preflight.py" not in x
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

def text_bool_false_or_absent(text: str, key: str) -> bool:
    # Accept either absent, "false", or "0"; reject explicit true/1.
    m = re.search(rf"(?im)^\s*{re.escape(key)}\s*:\s*([A-Za-z0-9_\"']+)", text)
    if not m:
        return True
    val = m.group(1).strip().strip("'\"").lower()
    return val in {"false", "0", "no", "off", "disabled"}

def text_has_pair(text: str, key: str, expected: str) -> bool:
    return re.search(rf"(?im)^\s*{re.escape(key)}\s*:\s*['\"]?{re.escape(expected)}['\"]?\s*$", text) is not None

def text_has_int(text: str, key: str, expected: int) -> bool:
    return re.search(rf"(?im)^\s*{re.escape(key)}\s*:\s*{expected}\s*$", text) is not None

def hard_live_env_off() -> dict[str, Any]:
    values = {k: os.environ.get(k, "") for k in HARD_LIVE_ENV_KEYS}
    enabled = {
        k: v for k, v in values.items()
        if str(v).strip().lower() in TRUTHY
    }
    return {"values": values, "enabled": enabled, "ok": not bool(enabled)}

def source_terms() -> dict[str, Any]:
    result: dict[str, Any] = {}
    for rel in INSPECT_FILES:
        t = read(rel)
        result[rel] = {
            "exists": bool(t),
            "controlled_ack_term": SCOPE_ACK in t,
            "controlled_runtime_term": "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME" in t or "controlled_paper" in t.lower(),
            "real_live_false_term": "real_live_allowed" in t or "real_live_approved" in t,
            "risk_execution_term": "risk" in t.lower() or "execution" in t.lower(),
        }
    return result

def _yaml_load_loose(text: str) -> dict:
    if not text.strip():
        return {}
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(text)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def _flatten_values(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = str(k)
            full = f"{prefix}.{key}" if prefix else key
            out[full] = v
            out.update(_flatten_values(v, full))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(_flatten_values(v, f"{prefix}.{i}"))
    return out

def _any_value(flat: dict, key_terms: list[str], expected: str) -> bool:
    exp = str(expected).strip().lower()
    for k, v in flat.items():
        lk = str(k).lower()
        if all(term.lower() in lk for term in key_terms):
            if str(v).strip().strip("'\"").lower() == exp:
                return True
    return False

def _any_bool(flat: dict, key_terms: list[str], expected: bool) -> bool:
    for k, v in flat.items():
        lk = str(k).lower()
        if all(term.lower() in lk for term in key_terms):
            if isinstance(v, bool) and v is expected:
                return True
            sv = str(v).strip().strip("'\"").lower()
            if expected and sv in {"1", "true", "yes", "on", "enabled"}:
                return True
            if (not expected) and sv in {"0", "false", "no", "off", "disabled"}:
                return True
    return False

def _any_int(flat: dict, key_terms: list[str], expected: int) -> bool:
    for k, v in flat.items():
        lk = str(k).lower()
        if all(term.lower() in lk for term in key_terms):
            try:
                if int(v) == expected:
                    return True
            except Exception:
                pass
    return False

def config_scope_check() -> dict[str, Any]:
    enablement_text = read("etc/strategy_family/rollout/controlled_paper_trial_enablement_from_25v25w.yaml")
    scope_text = read("etc/strategy_family/rollout/controlled_paper_trial_scope_from_25v25w.yaml")
    readiness_text = read("etc/strategy_family/rollout/paper_armed_readiness_gate.yaml")
    runtime_text = read("etc/runtime.yaml")

    enablement = _yaml_load_loose(enablement_text)
    scope = _yaml_load_loose(scope_text)
    readiness = _yaml_load_loose(readiness_text)
    runtime = _yaml_load_loose(runtime_text)

    combined_text = "\n".join([enablement_text, scope_text, readiness_text, runtime_text])
    flat = {}
    for block_name, block in {
        "enablement": enablement,
        "scope": scope,
        "readiness": readiness,
        "runtime": runtime,
    }.items():
        for k, v in _flatten_values(block).items():
            flat[f"{block_name}.{k}"] = v

    selected_family_mist = (
        _any_value(flat, ["family"], "MIST")
        or "selected_family: MIST" in scope_text
        or "selected_family: 'MIST'" in scope_text
        or 'selected_family: "MIST"' in scope_text
        or "family: MIST" in scope_text
    )

    selected_side_call = (
        _any_value(flat, ["side"], "CALL")
        or "selected_side: CALL" in scope_text
        or "selected_side: 'CALL'" in scope_text
        or 'selected_side: "CALL"' in scope_text
        or "side: CALL" in scope_text
    )

    quantity_lots_1 = (
        _any_int(flat, ["quantity", "lots"], 1)
        or _any_int(flat, ["qty", "lots"], 1)
        or _any_int(flat, ["lots"], 1)
        or "quantity_lots: 1" in scope_text
        or "qty_lots: 1" in scope_text
    )

    real_live_allowed_false = (
        _any_bool(flat, ["real", "live"], False)
        or "real_live_allowed: false" in combined_text
        or "real_live_approved: false" in combined_text
    )

    paper_orders_allowed_true_or_scope_enabled = (
        _any_bool(flat, ["paper", "orders", "allowed"], True)
        or _any_bool(flat, ["enabled"], True)
        or "paper_orders_allowed: true" in combined_text
        or "enabled: true" in enablement_text
    )

    auto_failover_false = (
        _any_bool(flat, ["automatic", "broker", "failover"], False)
        or _any_bool(flat, ["auto", "failover"], False)
        or "automatic_broker_failover_allowed: false" in combined_text
        or "automatic_broker_failover_allowed" not in combined_text
    )

    mid_position_migration_false = (
        _any_bool(flat, ["mid", "position", "migration"], False)
        or _any_bool(flat, ["provider", "migration"], False)
        or "mid_position_provider_migration_allowed: false" in combined_text
        or "mid_position_provider_migration_allowed" not in combined_text
    )

    trading_enabled_not_true = "trading_enabled: true" not in runtime_text.lower()
    allow_live_orders_not_true = "allow_live_orders: true" not in runtime_text.lower()

    return {
        "enablement_present": bool(enablement_text),
        "scope_present": bool(scope_text),
        "readiness_present": bool(readiness_text),
        "selected_family_mist": selected_family_mist,
        "selected_side_call": selected_side_call,
        "quantity_lots_1": quantity_lots_1,
        "real_live_allowed_false": real_live_allowed_false,
        "paper_orders_allowed_true_or_scope_enabled": paper_orders_allowed_true_or_scope_enabled,
        "auto_failover_false": auto_failover_false,
        "mid_position_migration_false": mid_position_migration_false,
        "trading_enabled_not_true": trading_enabled_not_true,
        "allow_live_orders_not_true": allow_live_orders_not_true,
        "debug_flat_scope_keys": sorted([k for k in flat.keys() if any(t in k.lower() for t in ["family", "side", "lot", "qty", "paper", "live", "failover", "migration", "enabled"])])[:120],
    }

def latest_order_empty() -> bool:
    raw = cmd(["bash", "-lc", "redis-cli XREVRANGE orders:mme:stream + - COUNT 1 | sed -n '1,40p'"])["stdout"]
    return not bool(raw.strip())

def main() -> int:
    ping_results = []
    for _ in range(5):
        r = rcli("PING", timeout=3)
        ping_results.append({
            "ok": r["ok"],
            "stdout": r["stdout"],
            "elapsed_ms": r["elapsed_ms"],
        })
        time.sleep(0.2)

    persistence = parse_info(rcli("INFO", "persistence", timeout=3)["stdout"])
    disk_pct = disk_used_pct()

    position = hgetall(POSITION_KEY)
    provider = hgetall(PROVIDER_KEY)

    fut_keys = hkeys(FUT_KEY)
    opt_keys = hkeys(OPT_KEY)
    dhan_keys = hkeys(DHAN_KEY)
    health_feeds_keys = hkeys(HEALTH_FEEDS_KEY)

    risk = pgrep("app.mme_scalpx.main --service risk")
    execution = pgrep("app.mme_scalpx.main --service execution")

    orders_len = xlen(ORDERS_STREAM)
    config = config_scope_check()
    env = hard_live_env_off()
    sources = source_terms()

    provider_required = [
        "futures_marketdata_provider_id",
        "selected_option_marketdata_provider_id",
        "option_context_provider_id",
        "execution_primary_provider_id",
        "execution_fallback_provider_id",
        "futures_marketdata_status",
        "selected_option_marketdata_status",
        "option_context_status",
        "execution_primary_status",
        "execution_fallback_status",
        "family_runtime_mode",
        "active_futures_provider_id",
        "active_selected_option_provider_id",
        "active_option_context_provider_id",
        "active_execution_provider_id",
        "provider_ready_classic",
        "provider_ready_miso",
        "last_update_ns",
        "ts_event_ns",
    ]

    provider_missing = [k for k in provider_required if k not in provider]

    feed_snapshot_ok = (
        exists(FUT_KEY)
        and exists(OPT_KEY)
        and exists(DHAN_KEY)
        and exists(HEALTH_FEEDS_KEY)
        and "future_json" in fut_keys
        and "selected_call_json" in opt_keys
        and "selected_put_json" in opt_keys
        and "option_chain_ladder_json" in dhan_keys
        and "strike_ladder_json" in dhan_keys
        and "oi_wall_summary_json" in dhan_keys
        and "selected_call_context_json" in dhan_keys
        and "selected_put_context_json" in dhan_keys
    )

    config_scope_ok = all(config.values())
    source_inspection_ok = all(v["exists"] for v in sources.values())

    duplicate_guard_ok = len(risk) == 0 and len(execution) == 0

    proof = {
        "batch": "26O7",
        "name": "controlled_runtime_start_preflight",
        "created_at": now_iso(),
        "real_live_approved": False,
        "paper_order_approved": False,
        "runtime_promotion_allowed": False,
        "redis": {
            "ping_results": ping_results,
            "pong_x5": all(x["ok"] and x["stdout"] == "PONG" for x in ping_results),
            "max_ping_ms": max([x["elapsed_ms"] for x in ping_results] or [999999]),
            "persistence": {
                "rdb_last_bgsave_status": persistence.get("rdb_last_bgsave_status"),
                "rdb_bgsave_in_progress": persistence.get("rdb_bgsave_in_progress"),
                "aof_rewrite_in_progress": persistence.get("aof_rewrite_in_progress"),
            },
            "persistence_ok": persistence.get("rdb_last_bgsave_status") == "ok" and persistence.get("rdb_bgsave_in_progress") == "0",
        },
        "disk": {
            "used_pct": disk_pct,
            "below_85": disk_pct is not None and disk_pct < 85,
        },
        "position": {
            "hash_present": bool(position),
            "flat": is_flat(position),
            "fields": position,
        },
        "orders": {
            "stream": ORDERS_STREAM,
            "xlen": orders_len,
            "zero": orders_len == "0",
            "latest_order_empty": latest_order_empty(),
        },
        "provider_runtime": {
            "hash_present": bool(provider),
            "required_keys_present": len(provider_missing) == 0,
            "missing_required": provider_missing,
            "family_runtime_mode": provider.get("family_runtime_mode"),
            "provider_ready_classic": provider.get("provider_ready_classic"),
            "provider_ready_miso": provider.get("provider_ready_miso"),
        },
        "feed_snapshots": {
            "fut_hash_present": exists(FUT_KEY),
            "opt_hash_present": exists(OPT_KEY),
            "dhan_context_hash_present": exists(DHAN_KEY),
            "health_feeds_present": exists(HEALTH_FEEDS_KEY),
            "fut_keys": fut_keys,
            "opt_keys": opt_keys,
            "dhan_keys": dhan_keys,
            "health_feeds_keys": health_feeds_keys,
            "feed_snapshot_ok": feed_snapshot_ok,
        },
        "processes": {
            "risk_lines": risk,
            "execution_lines": execution,
            "risk_count": len(risk),
            "execution_count": len(execution),
            "duplicate_risk_execution_guard_ok": duplicate_guard_ok,
        },
        "controlled_scope": config,
        "env_live_guard": env,
        "source_inspection": sources,
    }

    proof["verdicts"] = {
        "redis_pong_x5": proof["redis"]["pong_x5"],
        "rdb_last_bgsave_status_ok": proof["redis"]["persistence_ok"],
        "disk_below_85": proof["disk"]["below_85"],
        "position_hash_present_flat": proof["position"]["hash_present"] and proof["position"]["flat"],
        "orders_zero": proof["orders"]["zero"] and proof["orders"]["latest_order_empty"],
        "provider_runtime_hash_present": proof["provider_runtime"]["hash_present"],
        "provider_runtime_required_keys_present": proof["provider_runtime"]["required_keys_present"],
        "feed_snapshot_hashes_present": proof["feed_snapshots"]["feed_snapshot_ok"],
        "selected_mist_call_one_lot_scope_valid": config_scope_ok,
        "no_existing_risk_process": len(risk) == 0,
        "no_existing_execution_process": len(execution) == 0,
        "real_live_allowed_false": config["real_live_allowed_false"] and env["ok"],
        "source_inspection_ok": source_inspection_ok,
    }

    proof["duplicate_risk_execution_guard_ok"] = duplicate_guard_ok

    proof["controlled_runtime_start_preflight_ok"] = all(proof["verdicts"].values()) and duplicate_guard_ok

    if proof["controlled_runtime_start_preflight_ok"]:
        proof["final_verdict"] = "PASS_CONTROLLED_RUNTIME_START_PREFLIGHT_OK"
        proof["next_required_batch"] = "Batch 26-O8 live 25V gate aggregator"
    else:
        proof["final_verdict"] = "FAIL_CONTROLLED_RUNTIME_START_PREFLIGHT_REVIEW_REQUIRED"
        proof["next_required_batch"] = "Review O7 failed verdicts before O8/paper"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n")

    print(json.dumps({
        "final_verdict": proof["final_verdict"],
        "controlled_runtime_start_preflight_ok": proof["controlled_runtime_start_preflight_ok"],
        "duplicate_risk_execution_guard_ok": proof["duplicate_risk_execution_guard_ok"],
        "failed_verdicts": [k for k, v in proof["verdicts"].items() if not v],
        "next_required_batch": proof["next_required_batch"],
    }, indent=2, sort_keys=True))

    return 0 if proof["controlled_runtime_start_preflight_ok"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
