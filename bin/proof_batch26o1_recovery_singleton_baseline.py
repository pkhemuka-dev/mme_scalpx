#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path("/home/Lenovo/scalpx/projects/mme_scalpx")
PROOF_PATH = ROOT / "run/proofs/proof_batch26o1_recovery_singleton_baseline.json"

REDIS_TIMEOUT_SEC = float(os.environ.get("BATCH26O1_REDIS_TIMEOUT_SEC", "3"))
PING_ATTEMPTS = int(os.environ.get("BATCH26O1_REDIS_PING_ATTEMPTS", "5"))
DISK_MAX_USED_PCT = int(os.environ.get("BATCH26O1_DISK_MAX_USED_PCT", "85"))
REDIS_MEMORY_WARN_PCT = float(os.environ.get("BATCH26O1_REDIS_MEMORY_WARN_PCT", "0.95"))
STRICT_LIVE = os.environ.get("BATCH26O1_STRICT_LIVE", "0").strip() in {"1", "true", "TRUE", "yes", "YES"}

EXPECTED_FILES = [
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "app/mme_scalpx/core/redisx.py",
    "app/mme_scalpx/core/settings.py",
    "app/mme_scalpx/main.py",
    "app/mme_scalpx/services/feeds.py",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/execution.py",
    "bin/start_controlled_paper_runtime_chain.py",
    "bin/proof_market_session_provider_runtime.py",
    "bin/proof_market_session_feed_snapshot.py",
    "bin/proof_market_session_feature_payload.py",
    "bin/proof_market_session_family_surfaces.py",
    "bin/proof_market_session_strategy_activation.py",
    "bin/proof_market_session_no_order_sent.py",
]

CANONICAL_HASHES = [
    "state:provider:runtime",
    "state:snapshot:mme:fut:active",
    "state:snapshot:mme:opt:selected:active",
    "state:context:mme:dhan",
    "state:features:mme:fut",
    "state:position:mme",
    "health:feeds",
    "health:features",
    "health:strategy",
]

CANONICAL_STREAMS = [
    "ticks:mme:fut:zerodha:stream",
    "ticks:mme:fut:dhan:stream",
    "ticks:mme:opt:selected:zerodha:stream",
    "ticks:mme:opt:selected:dhan:stream",
    "features:mme:stream",
    "decisions:mme:stream",
    "orders:mme:stream",
]

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def run(args: list[str], timeout: float = 10.0) -> dict[str, Any]:
    try:
        cp = subprocess.run(
            args,
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        return {
            "ok": cp.returncode == 0,
            "returncode": cp.returncode,
            "stdout": cp.stdout.strip(),
            "stderr": cp.stderr.strip(),
        }
    except Exception as exc:
        return {"ok": False, "error": repr(exc), "stdout": "", "stderr": ""}

def shell(cmd: str, timeout: float = 10.0) -> dict[str, Any]:
    return run(["bash", "-lc", cmd], timeout=timeout)

def redis(args: list[str], timeout: float = REDIS_TIMEOUT_SEC) -> dict[str, Any]:
    return run(["redis-cli", *args], timeout=timeout)

def read_text(rel: str) -> str:
    p = ROOT / rel
    if not p.exists():
        return ""
    return p.read_text(errors="replace")

def sha256_file(rel: str) -> str | None:
    p = ROOT / rel
    if not p.exists() or not p.is_file():
        return None
    return hashlib.sha256(p.read_bytes()).hexdigest()

def parse_df_pct(df_line: str) -> int | None:
    m = re.search(r"\s(\d+)%\s", df_line)
    return int(m.group(1)) if m else None

def parse_info(raw: str) -> dict[str, str]:
    d: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" in line and not line.startswith("#"):
            k, v = line.split(":", 1)
            d[k.strip()] = v.strip()
    return d

def proc_lines(service: str) -> list[str]:
    r = shell(f"pgrep -af 'app.mme_scalpx.main --service {service}' || true", timeout=5)
    lines = []
    for x in r.get("stdout", "").splitlines():
        if "pgrep -af" in x:
            continue
        if "proof_batch26o1_recovery_singleton_baseline.py" in x:
            continue
        if x.strip():
            lines.append(x)
    return lines

def hgetall_lines(key: str) -> list[str]:
    r = redis(["HGETALL", key])
    if not r.get("ok"):
        return []
    return [x for x in r.get("stdout", "").splitlines() if x.strip()]

def position_eval(lines: list[str]) -> dict[str, Any]:
    d: dict[str, str] = {}
    for i in range(0, len(lines) - 1, 2):
        d[lines[i]] = lines[i + 1]
    required = ["has_position", "position_side", "qty_lots", "qty_units", "realized_pnl_day"]
    flat = (
        d.get("has_position") == "0"
        and d.get("position_side") == "FLAT"
        and d.get("qty_lots") == "0"
        and d.get("qty_units") == "0"
    )
    return {
        "present": bool(d),
        "flat": flat,
        "dict": d,
        "required": required,
        "missing_fields": [k for k in required if k not in d],
    }

def hash_summary(key: str) -> dict[str, Any]:
    return {
        "exists": redis(["EXISTS", key]).get("stdout", ""),
        "hlen": redis(["HLEN", key]).get("stdout", ""),
        "ttl": redis(["TTL", key]).get("stdout", ""),
        "sample": shell(f"redis-cli HGETALL {key!r} | sed -n '1,40p'", timeout=4).get("stdout", "")[:3000],
    }

def stream_summary(key: str) -> dict[str, Any]:
    return {
        "exists": redis(["EXISTS", key]).get("stdout", ""),
        "xlen": redis(["XLEN", key]).get("stdout", ""),
        "latest": shell(f"redis-cli XREVRANGE {key!r} + - COUNT 1 | sed -n '1,60p'", timeout=4).get("stdout", "")[:3000],
    }

def source_scan() -> dict[str, Any]:
    out: dict[str, Any] = {}
    for rel in EXPECTED_FILES:
        text = read_text(rel)
        out[rel] = {
            "exists": bool(text),
            "line_count": text.count("\n") + 1 if text else 0,
            "sha256": sha256_file(rel),
            "mentions": {
                "provider_runtime": "state:provider:runtime" in text or "HASH_STATE_PROVIDER_RUNTIME" in text,
                "fut_active": "state:snapshot:mme:fut:active" in text or "HASH_FUT_ACTIVE" in text,
                "opt_active": "state:snapshot:mme:opt:selected:active" in text or "HASH_OPT_ACTIVE" in text,
                "dhan_context": "state:context:mme:dhan" in text or "HASH_STATE_DHAN_CONTEXT" in text,
                "position": "state:position:mme" in text or "HASH_STATE_POSITION_MME" in text,
                "health_feeds": "health:feeds" in text or "KEY_HEALTH_FEEDS" in text,
                "orders": "orders:mme:stream" in text or "STREAM_ORDERS_MME" in text,
            },
        }
    return out

def main() -> int:
    proof: dict[str, Any] = {
        "batch": "26O1",
        "name": "recovery_singleton_baseline",
        "created_at": now_iso(),
        "strict_live": STRICT_LIVE,
        "real_live_approved": False,
        "paper_order_approved": False,
        "runtime_promotion_allowed": False,
    }

    proof["source_inspection"] = source_scan()
    proof["source_inspection_ok"] = all(v["exists"] for v in proof["source_inspection"].values())

    compile_targets = [
        "bin/proof_batch26o1_recovery_singleton_baseline.py",
        "app/mme_scalpx/core/names.py",
        "app/mme_scalpx/main.py",
        "app/mme_scalpx/services/feeds.py",
        "app/mme_scalpx/services/features.py",
        "app/mme_scalpx/services/strategy.py",
        "app/mme_scalpx/services/risk.py",
        "app/mme_scalpx/services/execution.py",
    ]
    proof["compile"] = {p: run([sys.executable, "-m", "py_compile", p], timeout=25) for p in compile_targets}
    proof["compile_ok"] = all(v.get("ok") for v in proof["compile"].values())

    df = shell("df -h . | tail -1", timeout=5).get("stdout", "")
    dfi = shell("df -ih . | tail -1", timeout=5).get("stdout", "")
    disk_pct = parse_df_pct(df)
    inode_pct = parse_df_pct(dfi)

    proof["disk"] = {
        "df": df,
        "df_inodes": dfi,
        "disk_used_pct": disk_pct,
        "inode_used_pct": inode_pct,
        "threshold_pct": DISK_MAX_USED_PCT,
        "disk_ok": disk_pct is not None and disk_pct < DISK_MAX_USED_PCT,
        "inode_ok": inode_pct is not None and inode_pct < DISK_MAX_USED_PCT,
    }

    pings = []
    for _ in range(PING_ATTEMPTS):
        t0 = time.perf_counter()
        r = redis(["PING"])
        pings.append({
            "ok": r.get("ok"),
            "stdout": r.get("stdout"),
            "latency_ms": round((time.perf_counter() - t0) * 1000, 2),
            "stderr": r.get("stderr"),
            "error": r.get("error"),
        })
        time.sleep(0.2)

    persistence = parse_info(redis(["INFO", "persistence"]).get("stdout", ""))
    memory = parse_info(redis(["INFO", "memory"]).get("stdout", ""))
    clients = parse_info(redis(["INFO", "clients"]).get("stdout", ""))

    used = int(memory.get("used_memory") or 0)
    maxmem = int(memory.get("maxmemory") or 0)
    mem_ratio = (used / maxmem) if maxmem > 0 else None

    proof["redis"] = {
        "pings": pings,
        "ping_stable": all(x["ok"] and x["stdout"] == "PONG" for x in pings),
        "persistence": {
            "rdb_last_bgsave_status": persistence.get("rdb_last_bgsave_status"),
            "rdb_bgsave_in_progress": persistence.get("rdb_bgsave_in_progress"),
            "aof_rewrite_in_progress": persistence.get("aof_rewrite_in_progress"),
            "rdb_changes_since_last_save": persistence.get("rdb_changes_since_last_save"),
            "rdb_last_save_time": persistence.get("rdb_last_save_time"),
        },
        "persistence_ok": persistence.get("rdb_last_bgsave_status") == "ok" and persistence.get("rdb_bgsave_in_progress") == "0",
        "memory": {
            "used_memory_human": memory.get("used_memory_human"),
            "used_memory_peak_human": memory.get("used_memory_peak_human"),
            "maxmemory_human": memory.get("maxmemory_human"),
            "mem_fragmentation_ratio": memory.get("mem_fragmentation_ratio"),
            "memory_ratio": mem_ratio,
        },
        "memory_ok": mem_ratio is None or mem_ratio < REDIS_MEMORY_WARN_PCT,
        "clients": {
            "connected_clients": clients.get("connected_clients"),
            "blocked_clients": clients.get("blocked_clients"),
        },
        "clients_ok": clients.get("blocked_clients") in (None, "0"),
    }

    service_counts = {svc: len(proc_lines(svc)) for svc in ["feeds", "features", "strategy", "risk", "execution"]}
    service_lines = {svc: proc_lines(svc) for svc in ["feeds", "features", "strategy", "risk", "execution"]}

    proof["processes"] = {
        "service_counts": service_counts,
        "service_lines": service_lines,
        "feeds_singleton": service_counts["feeds"] <= 1,
        "features_singleton": service_counts["features"] <= 1,
        "strategy_singleton": service_counts["strategy"] <= 1,
        "risk_not_running": service_counts["risk"] == 0,
        "execution_not_running": service_counts["execution"] == 0,
        "singleton_topology_ok": (
            service_counts["feeds"] <= 1
            and service_counts["features"] <= 1
            and service_counts["strategy"] <= 1
            and service_counts["risk"] == 0
            and service_counts["execution"] == 0
        ),
    }

    proof["hashes"] = {k: hash_summary(k) for k in CANONICAL_HASHES}
    proof["streams"] = {k: stream_summary(k) for k in CANONICAL_STREAMS}

    position = position_eval(hgetall_lines("state:position:mme"))
    orders_len = proof["streams"]["orders:mme:stream"]["xlen"]

    proof["safety_surfaces"] = {
        "orders_len": orders_len,
        "orders_zero": orders_len in ("0", "(integer) 0", ""),
        "position": position,
        "position_hash_present": position["present"],
        "position_flat": position["flat"],
        "position_reseed_required": not position["present"] or not position["flat"],
    }

    proof["canonical_live_state"] = {
        "provider_runtime_hash_present": proof["hashes"]["state:provider:runtime"]["exists"] == "1",
        "futures_active_hash_present": proof["hashes"]["state:snapshot:mme:fut:active"]["exists"] == "1",
        "selected_option_active_hash_present": proof["hashes"]["state:snapshot:mme:opt:selected:active"]["exists"] == "1",
        "dhan_context_hash_present": proof["hashes"]["state:context:mme:dhan"]["exists"] == "1",
        "health_feeds_hash_present": proof["hashes"]["health:feeds"]["exists"] == "1",
        "features_hash_present": proof["hashes"]["state:features:mme:fut"]["exists"] == "1",
        "health_features_present": proof["hashes"]["health:features"]["exists"] == "1",
        "health_strategy_present": proof["hashes"]["health:strategy"]["exists"] == "1",
    }
    proof["canonical_live_state"]["live_canonical_hashes_ready"] = all([
        proof["canonical_live_state"]["provider_runtime_hash_present"],
        proof["canonical_live_state"]["futures_active_hash_present"],
        proof["canonical_live_state"]["selected_option_active_hash_present"],
        proof["canonical_live_state"]["dhan_context_hash_present"],
        proof["canonical_live_state"]["health_feeds_hash_present"],
    ])

    proof["verdicts"] = {
        "source_inspection_ok": proof["source_inspection_ok"],
        "compile_ok": proof["compile_ok"],
        "disk_ok": proof["disk"]["disk_ok"] and proof["disk"]["inode_ok"],
        "redis_ok": proof["redis"]["ping_stable"] and proof["redis"]["persistence_ok"] and proof["redis"]["memory_ok"] and proof["redis"]["clients_ok"],
        "singleton_topology_ok": proof["processes"]["singleton_topology_ok"],
        "orders_zero": proof["safety_surfaces"]["orders_zero"],
        "position_hash_present": proof["safety_surfaces"]["position_hash_present"],
        "position_flat": proof["safety_surfaces"]["position_flat"],
        "position_reseed_required": proof["safety_surfaces"]["position_reseed_required"],
        "canonical_live_hashes_ready": proof["canonical_live_state"]["live_canonical_hashes_ready"],
    }

    base_ok = all([
        proof["verdicts"]["source_inspection_ok"],
        proof["verdicts"]["compile_ok"],
        proof["verdicts"]["disk_ok"],
        proof["verdicts"]["redis_ok"],
        proof["verdicts"]["singleton_topology_ok"],
        proof["verdicts"]["orders_zero"],
    ])

    if not base_ok:
        proof["final_verdict"] = "FAIL_RECOVERY_SINGLETON_BASELINE"
    elif proof["verdicts"]["position_reseed_required"]:
        proof["final_verdict"] = "PASS_BASELINE_BUT_POSITION_RESEED_REQUIRED"
    elif STRICT_LIVE and not proof["verdicts"]["canonical_live_hashes_ready"]:
        proof["final_verdict"] = "PASS_BASELINE_BUT_CANONICAL_LIVE_HASHES_MISSING"
    else:
        proof["final_verdict"] = "PASS_RECOVERY_SINGLETON_BASELINE"

    proof["next_required_batch"] = (
        "Batch 26-O2 position FLAT reseed/verification guard"
        if proof["verdicts"]["position_reseed_required"]
        else "Batch 26-O3 provider runtime publication repair"
        if not proof["verdicts"]["canonical_live_hashes_ready"]
        else "Batch 26-O8 live 25V gate"
    )

    PROOF_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROOF_PATH.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "proof": str(PROOF_PATH.relative_to(ROOT)),
        "final_verdict": proof["final_verdict"],
        "verdicts": proof["verdicts"],
        "next_required_batch": proof["next_required_batch"],
    }, indent=2, sort_keys=True))

    return 0 if proof["final_verdict"].startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())

