#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any, Mapping

ROOT = pathlib.Path.cwd().resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BATCH = "26-O20R"
PROOF_PATH = ROOT / "run/proofs/proof_batch26o20r_recovery_after_terminated_o20.json"
MANIFEST_PATH = ROOT / "run/proofs/manifest_batch26o20r_recovery_after_terminated_o20.json"

TARGETS = [
    "bin/proof_batch26o20r_recovery_after_terminated_o20.py",
    "bin/proof_batch26o20_controlled_paper_extended_observation.py",
    "run/proofs/proof_batch26o19_lightweight_controlled_paper_runtime.json",
    "run/proofs/proof_batch26o20_controlled_paper_extended_observation.json",
    "app/mme_scalpx/main.py",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/core/names.py",
]


def sha256_file(path: pathlib.Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_json_load_path(path: pathlib.Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def decode_hash(raw: Mapping[Any, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in dict(raw or {}).items():
        kk = k.decode("utf-8", "replace") if isinstance(k, bytes) else str(k)
        vv = v.decode("utf-8", "replace") if isinstance(v, bytes) else str(v)
        out[kk] = vv
    return out


def redis_client_or_none():
    try:
        import redis  # type: ignore
        client = redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=False)
        client.ping()
        return client
    except Exception:
        return None


def run_cmd(args: list[str], timeout: int = 60) -> dict[str, Any]:
    proc = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
    )
    return {
        "args": args,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def ps_lines() -> list[str]:
    try:
        out = subprocess.check_output(["ps", "-eo", "pid=,ppid=,comm=,args="], text=True)
        return [" ".join(x.split()) for x in out.splitlines() if x.strip()]
    except Exception:
        return []


def pgrep_service(service: str) -> list[str]:
    matches: list[str] = []
    self_name = "proof_batch26o20r_recovery_after_terminated_o20.py"
    for clean in ps_lines():
        lower = clean.lower()
        if self_name in clean:
            continue
        if "grep" in lower or "pgrep" in lower or "bash -lc" in lower or " sh -c " in lower:
            continue
        if "python" not in lower:
            continue
        if "-m app.mme_scalpx.main" not in clean:
            continue
        if f"--service {service}" not in clean:
            continue
        matches.append(clean)
    return matches


def pid_from_ps_line(line: str) -> int | None:
    try:
        return int(line.split()[0])
    except Exception:
        return None


def terminate_service_processes(services: list[str]) -> dict[str, Any]:
    before = {svc: pgrep_service(svc) for svc in services}
    killed: list[dict[str, Any]] = []

    # Do NOT kill feeds by default. Only kill features/strategy/risk/execution orphaned from O20/O19.
    for svc in services:
        if svc == "feeds":
            continue
        for line in before.get(svc, []):
            pid = pid_from_ps_line(line)
            if not pid:
                continue
            try:
                os.kill(pid, signal.SIGTERM)
                killed.append({"service": svc, "pid": pid, "signal": "TERM", "line": line})
            except Exception as exc:
                killed.append({"service": svc, "pid": pid, "signal": "TERM_FAILED", "error": f"{type(exc).__name__}: {exc}", "line": line})

    time.sleep(3)

    mid = {svc: pgrep_service(svc) for svc in services}
    for svc in services:
        if svc == "feeds":
            continue
        for line in mid.get(svc, []):
            pid = pid_from_ps_line(line)
            if not pid:
                continue
            try:
                os.kill(pid, signal.SIGKILL)
                killed.append({"service": svc, "pid": pid, "signal": "KILL", "line": line})
            except Exception as exc:
                killed.append({"service": svc, "pid": pid, "signal": "KILL_FAILED", "error": f"{type(exc).__name__}: {exc}", "line": line})

    time.sleep(1)
    after = {svc: pgrep_service(svc) for svc in services}
    return {"before": before, "killed": killed, "after": after}


def xlen(client: Any, key: str) -> int:
    try:
        return int(client.xlen(key))
    except Exception:
        return 0


def hgetall(client: Any, key: str) -> dict[str, str]:
    try:
        return decode_hash(client.hgetall(key) or {})
    except Exception:
        return {}


def position_summary(raw: Mapping[str, str]) -> dict[str, Any]:
    has_position_raw = str(raw.get("has_position", raw.get("position_open", "false"))).lower()
    qty_lots = float(raw.get("qty_lots", raw.get("quantity_lots", "0")) or 0)
    qty_units = float(raw.get("qty_units", raw.get("quantity_units", "0")) or 0)
    side = str(raw.get("position_side", raw.get("side", ""))).upper()
    flat = bool(
        has_position_raw not in {"1", "true", "yes", "y"}
        and qty_lots == 0
        and qty_units == 0
        and side in {"", "FLAT", "NONE"}
    )
    return {
        "raw": dict(raw),
        "has_position_raw": has_position_raw,
        "qty_lots": qty_lots,
        "qty_units": qty_units,
        "side": side,
        "flat": flat,
    }


def latest_rows(client: Any, key: str, count: int = 5) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    try:
        rows = client.xrevrange(key, count=count)
        for msg_id, fields in rows:
            out.append({
                "id": msg_id.decode("utf-8", "replace") if isinstance(msg_id, bytes) else str(msg_id),
                "fields": decode_hash(fields),
            })
    except Exception:
        pass
    return out


def decision_safety(rows: list[dict[str, Any]]) -> dict[str, Any]:
    unsafe = []
    hold_like = []
    for row in rows:
        f = row.get("fields", {})
        action = str(f.get("action") or f.get("decision") or "").upper()
        side = str(f.get("side") or "").upper()
        qty = str(f.get("qty") or f.get("quantity_lots") or "0")
        order_type = str(f.get("order_type") or "")
        broker_side_effects_allowed = str(f.get("broker_side_effects_allowed") or "").lower() in {"1", "true", "yes"}
        live_orders_allowed = str(f.get("live_orders_allowed") or "").lower() in {"1", "true", "yes"}

        is_hold = bool(
            action in {"", "HOLD"}
            and side in {"", "FLAT"}
            and qty in {"", "0", "0.0"}
            and order_type == ""
            and not broker_side_effects_allowed
            and not live_orders_allowed
        )
        if is_hold:
            hold_like.append(row)
        else:
            unsafe.append(row)
    return {
        "row_count": len(rows),
        "hold_like_count": len(hold_like),
        "unsafe_count": len(unsafe),
        "unsafe_rows": unsafe,
        "latest_rows": rows,
    }


def find_recent_o20_artifacts() -> dict[str, Any]:
    artifacts: dict[str, Any] = {}
    patterns = [
        "run/live_capture/batch26o20_controlled_paper_extended_observation_*",
        "run/proofs/proof_batch26o20_controlled_paper_extended_observation.json",
        "run/proofs/manifest_batch26o20_controlled_paper_extended_observation.json",
    ]
    for pattern in patterns:
        paths = sorted(ROOT.glob(pattern))
        artifacts[pattern] = [
            {
                "path": str(p.relative_to(ROOT)),
                "exists": p.exists(),
                "is_dir": p.is_dir(),
                "sha256": None if p.is_dir() else sha256_file(p),
            }
            for p in paths[-10:]
        ]
    return artifacts


def write_outputs(result: dict[str, Any]) -> None:
    manifest = {
        "batch": BATCH,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "files": [
            {"path": p, "exists": (ROOT / p).exists(), "sha256": sha256_file(ROOT / p)}
            for p in TARGETS
        ],
    }
    PROOF_PATH.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


def main() -> int:
    result: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": "recovery_after_terminated_o20",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "recovery_only": True,
            "paper_restart": False,
            "risk_start": False,
            "execution_start": False,
            "broker_call": False,
            "order_write_intended": False,
            "real_live_approval": False,
            "forced_candidate": False,
            "threshold_relaxation": False,
        },
    }

    compile_result = run_cmd([
        sys.executable, "-m", "py_compile",
        "app/mme_scalpx/main.py",
        "app/mme_scalpx/services/features.py",
        "app/mme_scalpx/services/strategy.py",
        "app/mme_scalpx/services/risk.py",
        "app/mme_scalpx/services/execution.py",
        "app/mme_scalpx/core/names.py",
        "app/mme_scalpx/core/models.py",
        "app/mme_scalpx/core/settings.py",
    ])
    result["compile"] = compile_result

    client = redis_client_or_none()
    result["redis_available"] = client is not None
    if client is None:
        result["final_verdict"] = "FAIL_CLOSED_REDIS_NOT_AVAILABLE"
        write_outputs(result)
        return 2

    from app.mme_scalpx.core import names as N  # type: ignore

    orders_key = getattr(N, "STREAM_ORDERS_MME", "orders:mme:stream")
    decisions_key = getattr(N, "STREAM_DECISIONS_MME", "decisions:mme:stream")
    runtime_key = getattr(N, "HASH_STATE_RUNTIME", "state:runtime")
    position_key = getattr(N, "HASH_STATE_POSITION_MME", "state:position:mme")

    o19 = safe_json_load_path(ROOT / "run/proofs/proof_batch26o19_lightweight_controlled_paper_runtime.json")
    o20 = safe_json_load_path(ROOT / "run/proofs/proof_batch26o20_controlled_paper_extended_observation.json")

    result["prior_proofs"] = {
        "o19_exists": bool(o19),
        "o19_final_verdict": o19.get("final_verdict"),
        "o20_exists": bool(o20),
        "o20_final_verdict": o20.get("final_verdict"),
    }

    before_processes = {
        "feeds": pgrep_service("feeds"),
        "features": pgrep_service("features"),
        "strategy": pgrep_service("strategy"),
        "risk": pgrep_service("risk"),
        "execution": pgrep_service("execution"),
    }

    cleanup = terminate_service_processes(["feeds", "features", "strategy", "risk", "execution"])

    runtime = hgetall(client, runtime_key)
    position = position_summary(hgetall(client, position_key))
    orders_len = xlen(client, orders_key)
    decisions_len = xlen(client, decisions_key)
    latest_decisions = latest_rows(client, decisions_key, count=5)
    latest_orders = latest_rows(client, orders_key, count=5)
    dec_safety = decision_safety(latest_decisions)

    real_live = str(runtime.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}

    result.update({
        "o20_artifacts": find_recent_o20_artifacts(),
        "before_processes": before_processes,
        "cleanup": cleanup,
        "runtime": runtime,
        "position": position,
        "streams": {
            "orders_len": orders_len,
            "decisions_len": decisions_len,
        },
        "latest_decisions": latest_decisions,
        "latest_orders": latest_orders,
        "decision_safety": dec_safety,
    })

    required = {
        "compile_pass": compile_result["returncode"] == 0,
        "o19_pass_exists": o19.get("final_verdict") == "PASS_O19_LIGHTWEIGHT_CONTROLLED_PAPER_RUNTIME_OK_NO_ORDER",
        "o20_not_proven_or_missing": o20.get("final_verdict") != "PASS_O20_CONTROLLED_PAPER_EXTENDED_OBSERVATION_OK_NO_ORDER",
        "redis_available": True,
        "orders_zero": orders_len == 0,
        "latest_orders_empty": len(latest_orders) == 0,
        "position_flat": position["flat"] is True,
        "real_live_false": real_live is False,
        "decisions_hold_only": dec_safety["unsafe_count"] == 0,
        "risk_not_running_after_cleanup": len(cleanup["after"].get("risk", [])) == 0,
        "execution_not_running_after_cleanup": len(cleanup["after"].get("execution", [])) == 0,
        "strategy_not_running_after_cleanup": len(cleanup["after"].get("strategy", [])) == 0,
        "features_not_running_after_cleanup": len(cleanup["after"].get("features", [])) == 0,
        "feeds_allowed_to_remain": True,
        "no_paper_restart": True,
        "no_broker_call": True,
    }
    result["required_verdicts"] = required

    if not all(required.values()):
        result["final_verdict"] = "FAIL_O20R_RECOVERY_NOT_SAFE"
        result["next_recommended_batch"] = "Do not rerun O20. Inspect proof and manually stop/reconcile."
        write_outputs(result)
        return 2

    result["final_verdict"] = "PASS_O20R_RECOVERY_SAFE_AFTER_TERMINATED_O20"
    result["next_recommended_batch"] = "26-O20-R2 bounded short rerun with nohup/tmux-safe execution, reduced duration"
    write_outputs(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
