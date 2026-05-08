#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import json
import os
import pathlib
import subprocess
import time
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path("/home/Lenovo/scalpx/projects/mme_scalpx")
PROOF = ROOT / "run/proofs/proof_batch26o6_observer_guard.json"
PIDFILE = ROOT / "run/live_capture/live_signal_forensics_observer.pid"

DEFAULT_JSONL = ROOT / "run/live_capture/live_signal_forensics_observer.jsonl"

ORDERS_STREAM = "orders:mme:stream"
FEATURES_STREAM = "features:mme:stream"
DECISIONS_STREAM = "decisions:mme:stream"
POSITION_KEY = "state:position:mme"
PROVIDER_KEY = "state:provider:runtime"
HEALTH_FEEDS_KEY = "health:feeds"

FAMILIES = ["MIST", "MISB", "MISC", "MISR", "MISO"]

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def cmd(args: list[str], timeout: float = 3.0) -> dict[str, Any]:
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
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        return {
            "ok": cp.returncode == 0,
            "stdout": cp.stdout.strip(),
            "stderr": cp.stderr.strip(),
            "returncode": cp.returncode,
            "elapsed_ms": elapsed_ms,
        }
    except Exception as exc:
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        return {
            "ok": False,
            "stdout": "",
            "stderr": repr(exc),
            "returncode": -1,
            "elapsed_ms": elapsed_ms,
        }

def rcli(*args: str, timeout: float = 3.0) -> dict[str, Any]:
    return cmd(["redis-cli", *args], timeout=timeout)

def disk_used_pct() -> int | None:
    out = cmd(["bash", "-lc", "df -P . | tail -1"], timeout=3)["stdout"]
    parts = out.split()
    if len(parts) >= 5 and parts[4].endswith("%"):
        try:
            return int(parts[4].rstrip("%"))
        except Exception:
            return None
    return None

def proc_alive(pid: int) -> bool:
    return pathlib.Path(f"/proc/{pid}").exists()

def singleton_status() -> dict[str, Any]:
    if not PIDFILE.exists():
        return {"pidfile_exists": False, "active": False, "pid": None}
    raw = PIDFILE.read_text(errors="replace").strip()
    try:
        pid = int(raw)
    except Exception:
        return {"pidfile_exists": True, "active": False, "pid": raw, "invalid_pidfile": True}
    return {"pidfile_exists": True, "active": proc_alive(pid), "pid": pid}

def acquire_singleton() -> dict[str, Any]:
    status = singleton_status()
    if status.get("active"):
        return {"ok": False, "reason": "observer_already_running", "status": status}
    PIDFILE.write_text(str(os.getpid()) + "\n")
    return {"ok": True, "reason": "pidfile_written", "pid": os.getpid()}

def release_singleton() -> None:
    try:
        if PIDFILE.exists() and PIDFILE.read_text(errors="replace").strip() == str(os.getpid()):
            PIDFILE.unlink()
    except Exception:
        pass

def rotate_if_needed(path: pathlib.Path, max_mb: int) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        return {"rotated": False, "reason": "missing"}
    size_mb = path.stat().st_size / 1024 / 1024
    if size_mb < max_mb:
        return {"rotated": False, "size_mb": round(size_mb, 3)}
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    gz = path.with_name(path.name + f".{stamp}.gz")
    with path.open("rb") as src, gzip.open(gz, "wb", compresslevel=6) as dst:
        while True:
            chunk = src.read(1024 * 1024)
            if not chunk:
                break
            dst.write(chunk)
    path.unlink()
    return {"rotated": True, "old_size_mb": round(size_mb, 3), "gz": str(gz.relative_to(ROOT))}

def parse_latest_decision(raw: str) -> dict[str, Any]:
    lines = raw.splitlines()
    if "payload_json" not in lines:
        return {"parse_ok": False, "reason": "payload_json_missing"}
    i = lines.index("payload_json")
    if i + 1 >= len(lines):
        return {"parse_ok": False, "reason": "payload_json_value_missing"}
    try:
        payload = json.loads(lines[i + 1])
    except Exception as exc:
        return {"parse_ok": False, "reason": repr(exc)}
    out = {
        "parse_ok": True,
        "decision_id": payload.get("decision_id"),
        "action": payload.get("action"),
        "reason": payload.get("reason"),
        "activation_action": payload.get("activation_action"),
        "activation_promoted": payload.get("activation_promoted"),
        "activation_safe_to_promote": payload.get("activation_safe_to_promote"),
        "activation_candidate_count": payload.get("activation_candidate_count"),
        "activation_reason": payload.get("activation_reason"),
        "data_valid": payload.get("data_valid"),
        "provider_ready_classic": payload.get("provider_ready_classic"),
        "provider_ready_miso": payload.get("provider_ready_miso"),
        "regime": payload.get("regime"),
    }
    cv_raw = payload.get("consumer_view_json")
    if isinstance(cv_raw, str) and cv_raw:
        try:
            cv = json.loads(cv_raw)
            stage = cv.get("stage_flags", {}) if isinstance(cv, dict) else {}
            provider = cv.get("provider_runtime", {}) if isinstance(cv, dict) else {}
            family_status = cv.get("family_status", {}) if isinstance(cv, dict) else {}
            out["stage_flags"] = {
                "provider_ready_classic": stage.get("provider_ready_classic"),
                "provider_ready_miso": stage.get("provider_ready_miso"),
                "dhan_context_fresh": stage.get("dhan_context_fresh"),
                "selected_option_present": stage.get("selected_option_present"),
                "futures_present": stage.get("futures_present"),
                "data_quality_ok": stage.get("data_quality_ok"),
            }
            out["provider_runtime"] = {
                "provider_ready_classic": provider.get("provider_ready_classic"),
                "provider_ready_miso": provider.get("provider_ready_miso"),
                "futures_marketdata_status": provider.get("futures_marketdata_status"),
                "selected_option_marketdata_status": provider.get("selected_option_marketdata_status"),
                "option_context_status": provider.get("option_context_status"),
                "transition_reason": provider.get("transition_reason"),
            }
            out["family_status"] = {
                fam: {
                    "family_present": (family_status.get(fam) or {}).get("family_present"),
                    "contract_eligible": (family_status.get(fam) or {}).get("contract_eligible"),
                    "surface_eligible": (family_status.get(fam) or {}).get("surface_eligible"),
                    "surface_keys_count": len((family_status.get(fam) or {}).get("surface_keys") or []),
                }
                for fam in FAMILIES
            }
        except Exception as exc:
            out["consumer_view_parse_error"] = repr(exc)
    return out

def sample(redis_timeout: float, disk_max_pct: int) -> dict[str, Any]:
    ping = rcli("PING", timeout=redis_timeout)
    d_pct = disk_used_pct()

    pos_has = rcli("HGET", POSITION_KEY, "has_position", timeout=redis_timeout)
    pos_side = rcli("HGET", POSITION_KEY, "position_side", timeout=redis_timeout)
    pos_lots = rcli("HGET", POSITION_KEY, "qty_lots", timeout=redis_timeout)
    pos_units = rcli("HGET", POSITION_KEY, "qty_units", timeout=redis_timeout)

    orders = rcli("XLEN", ORDERS_STREAM, timeout=redis_timeout)
    features = rcli("XLEN", FEATURES_STREAM, timeout=redis_timeout)
    decisions = rcli("XLEN", DECISIONS_STREAM, timeout=redis_timeout)

    provider_exists = rcli("EXISTS", PROVIDER_KEY, timeout=redis_timeout)
    health_feeds_exists = rcli("EXISTS", HEALTH_FEEDS_KEY, timeout=redis_timeout)

    latest_decision_raw = cmd(
        ["redis-cli", "XREVRANGE", DECISIONS_STREAM, "+", "-", "COUNT", "1"],
        timeout=redis_timeout,
    )

    decision = parse_latest_decision(latest_decision_raw["stdout"]) if latest_decision_raw["ok"] else {
        "parse_ok": False,
        "reason": latest_decision_raw["stderr"] or "decision_read_failed",
    }

    stop_reasons: list[str] = []
    if not ping["ok"] or ping["stdout"] != "PONG":
        stop_reasons.append("redis_ping_failed")
    if ping["elapsed_ms"] > redis_timeout * 1000:
        stop_reasons.append("redis_timeout_elapsed")
    if ping["elapsed_ms"] > 2000:
        stop_reasons.append("redis_latency_gt_2000ms")
    if d_pct is not None and d_pct > disk_max_pct:
        stop_reasons.append("disk_usage_gt_threshold")
    if orders["stdout"] not in ("0", ""):
        stop_reasons.append("orders_stream_changed")

    return {
        "ts": now_iso(),
        "redis": {
            "ping": ping["stdout"],
            "ping_ok": ping["ok"] and ping["stdout"] == "PONG",
            "ping_ms": ping["elapsed_ms"],
        },
        "disk": {
            "used_pct": d_pct,
            "threshold_pct": disk_max_pct,
            "ok": d_pct is not None and d_pct <= disk_max_pct,
        },
        "streams": {
            "orders_len": orders["stdout"],
            "features_len": features["stdout"],
            "decisions_len": decisions["stdout"],
        },
        "position": {
            "has_position": pos_has["stdout"],
            "position_side": pos_side["stdout"],
            "qty_lots": pos_lots["stdout"],
            "qty_units": pos_units["stdout"],
        },
        "hash_presence": {
            "provider_runtime_exists": provider_exists["stdout"],
            "health_feeds_exists": health_feeds_exists["stdout"],
        },
        "decision": decision,
        "stop_reasons": stop_reasons,
    }

def static_policy_check() -> dict[str, Any]:
    text = pathlib.Path(__file__).read_text(errors="replace")

    # Avoid self-referential false positives: this checker contains the
    # forbidden examples as strings, so scan the observer runtime code with
    # this function body removed.
    start = text.index("def static_policy_check()")
    end = text.index("\ndef write_proof", start)
    runtime_text = text[:start] + text[end:]

    forbidden_exact = [
        "HGETALL state:features:mme:fut",
        "redis-cli HGETALL state:features:mme:fut",
        "XREVRANGE decisions:mme:stream + - COUNT 2",
        "XREVRANGE decisions:mme:stream + - COUNT 3",
        "XREVRANGE decisions:mme:stream + - COUNT 5",
        "XREVRANGE decisions:mme:stream + - COUNT 10",
        "XREVRANGE decisions:mme:stream + - COUNT 20",
        '"COUNT", "2"',
        '"COUNT", "3"',
        '"COUNT", "5"',
        '"COUNT", "10"',
        '"COUNT", "20"',
    ]

    found = [x for x in forbidden_exact if x in runtime_text]
    uses_count_1 = '"COUNT", "1"' in runtime_text or "COUNT 1" in runtime_text

    # HGETALL is allowed nowhere in the observer runtime. Small HGET reads
    # for position/provider fields are allowed.
    runtime_uses_hgetall = "HGETALL" in runtime_text

    return {
        "no_heavy_redis_calls": (not found) and uses_count_1 and (not runtime_uses_hgetall),
        "banned_patterns_found": found,
        "runtime_uses_hgetall": runtime_uses_hgetall,
        "uses_xrevrange_count_1": uses_count_1,
        "allows_only_compact_latest_decision": uses_count_1,
        "feature_hash_hgetall_forbidden": "HGETALL state:features:mme:fut" not in runtime_text,
    }

def write_proof(proof: dict[str, Any]) -> None:
    PROOF.parent.mkdir(parents=True, exist_ok=True)
    PROOF.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true", help="Run live observer loop")
    ap.add_argument("--duration-sec", type=int, default=0)
    ap.add_argument("--poll-sec", type=int, default=30)
    ap.add_argument("--redis-timeout-sec", type=float, default=2.0)
    ap.add_argument("--disk-max-pct", type=int, default=85)
    ap.add_argument("--jsonl", default=str(DEFAULT_JSONL))
    ap.add_argument("--max-jsonl-mb", type=int, default=5)
    args = ap.parse_args()

    if args.poll_sec < 30:
        args.poll_sec = 30

    jsonl = pathlib.Path(args.jsonl)
    if not jsonl.is_absolute():
        jsonl = ROOT / jsonl

    singleton_before = singleton_status()
    static_policy = static_policy_check()
    rotation = rotate_if_needed(jsonl, args.max_jsonl_mb)

    first_sample = sample(args.redis_timeout_sec, args.disk_max_pct)

    proof: dict[str, Any] = {
        "batch": "26O6",
        "name": "observer_guard",
        "created_at": now_iso(),
        "mode": "run" if args.run else "proof_only",
        "jsonl": str(jsonl.relative_to(ROOT)),
        "pidfile": str(PIDFILE.relative_to(ROOT)),
        "poll_sec": args.poll_sec,
        "duration_sec": args.duration_sec,
        "redis_timeout_sec": args.redis_timeout_sec,
        "disk_max_pct": args.disk_max_pct,
        "singleton_before": singleton_before,
        "rotation": rotation,
        "static_policy": static_policy,
        "first_sample": first_sample,
        "samples_written": 0,
        "stop_reason": "",
        "real_live_approved": False,
        "paper_order_approved": False,
    }

    proof["observer_singleton_ok"] = not bool(singleton_before.get("active"))
    proof["redis_latency_guard_ok"] = (
        first_sample["redis"]["ping_ok"]
        and first_sample["redis"]["ping_ms"] <= 2000
    )
    proof["disk_guard_ok"] = bool(first_sample["disk"]["ok"])
    proof["no_heavy_redis_calls"] = bool(static_policy["no_heavy_redis_calls"])
    proof["poll_interval_ok"] = args.poll_sec >= 30

    if args.run:
        lock = acquire_singleton()
        proof["singleton_acquire"] = lock
        if not lock["ok"]:
            proof["stop_reason"] = "singleton_acquire_failed"
        else:
            jsonl.parent.mkdir(parents=True, exist_ok=True)
            end_at = time.time() + max(1, args.duration_sec)
            try:
                while time.time() <= end_at:
                    s = sample(args.redis_timeout_sec, args.disk_max_pct)
                    with jsonl.open("a", encoding="utf-8") as f:
                        f.write(json.dumps(s, sort_keys=True) + "\n")
                    proof["samples_written"] += 1
                    if s["stop_reasons"]:
                        proof["stop_reason"] = ",".join(s["stop_reasons"])
                        break
                    time.sleep(args.poll_sec)
            finally:
                release_singleton()
        if not proof["stop_reason"]:
            proof["stop_reason"] = "duration_complete"

    proof["observer_guard_ok"] = (
        proof["observer_singleton_ok"]
        and proof["redis_latency_guard_ok"]
        and proof["disk_guard_ok"]
        and proof["no_heavy_redis_calls"]
        and proof["poll_interval_ok"]
    )

    proof["final_verdict"] = (
        "PASS_OBSERVER_GUARD_OK"
        if proof["observer_guard_ok"]
        else "FAIL_OBSERVER_GUARD_REVIEW_REQUIRED"
    )
    proof["next_required_batch"] = (
        "Batch 26-O7 risk/execution controlled startup hardening"
        if proof["observer_guard_ok"]
        else "Review O6 observer guard blockers"
    )

    write_proof(proof)

    print(json.dumps({
        "final_verdict": proof["final_verdict"],
        "observer_singleton_ok": proof["observer_singleton_ok"],
        "redis_latency_guard_ok": proof["redis_latency_guard_ok"],
        "disk_guard_ok": proof["disk_guard_ok"],
        "no_heavy_redis_calls": proof["no_heavy_redis_calls"],
        "poll_interval_ok": proof["poll_interval_ok"],
        "samples_written": proof["samples_written"],
        "stop_reason": proof["stop_reason"],
        "next_required_batch": proof["next_required_batch"],
    }, indent=2, sort_keys=True))

    return 0 if proof["observer_guard_ok"] else 1

if __name__ == "__main__":
    raise SystemExit(main())


