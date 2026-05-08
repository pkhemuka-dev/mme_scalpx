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

BATCH = "26-O21R"
PROOF_PATH = ROOT / "run/proofs/proof_batch26o21r_post_o21_orphan_cleanup.json"
MANIFEST_PATH = ROOT / "run/proofs/manifest_batch26o21r_post_o21_orphan_cleanup.json"
O21_PATH = ROOT / "run/proofs/proof_batch26o21_controlled_paper_promotion_readiness.json"

TARGETS = [
    "app/mme_scalpx/main.py",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "app/mme_scalpx/core/settings.py",
    "bin/proof_batch26o21r_post_o21_orphan_cleanup.py",
    "run/proofs/proof_batch26o21_controlled_paper_promotion_readiness.json",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: pathlib.Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_json_load(value: Any) -> Any:
    if value is None:
        return {}
    if isinstance(value, bytes):
        value = value.decode("utf-8", "replace")
    if isinstance(value, str):
        if not value.strip():
            return {}
        try:
            obj = json.loads(value)
            return obj if isinstance(obj, dict) else {}
        except Exception:
            return {}
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def load_json(path: pathlib.Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return safe_json_load(path.read_text(encoding="utf-8", errors="replace"))


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
    return {"args": args, "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def ps_lines() -> list[str]:
    try:
        out = subprocess.check_output(["ps", "-eo", "pid=,ppid=,comm=,args="], text=True)
        return [" ".join(x.split()) for x in out.splitlines() if x.strip()]
    except Exception:
        return []


def pgrep_service(service: str) -> list[str]:
    matches: list[str] = []
    self_name = "proof_batch26o21r_post_o21_orphan_cleanup.py"
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


def pid_from_line(line: str) -> int | None:
    try:
        return int(line.split()[0])
    except Exception:
        return None


def cleanup_orphans() -> dict[str, Any]:
    services = ["features", "strategy", "risk", "execution"]
    before = {svc: pgrep_service(svc) for svc in services + ["feeds"]}
    killed: list[dict[str, Any]] = []

    # Do not kill feeds here. It can remain as market-data lane.
    for svc in services:
        for line in before.get(svc, []):
            pid = pid_from_line(line)
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
        for line in mid.get(svc, []):
            pid = pid_from_line(line)
            if not pid:
                continue
            try:
                os.kill(pid, signal.SIGKILL)
                killed.append({"service": svc, "pid": pid, "signal": "KILL", "line": line})
            except Exception as exc:
                killed.append({"service": svc, "pid": pid, "signal": "KILL_FAILED", "error": f"{type(exc).__name__}: {exc}", "line": line})

    time.sleep(1)
    after = {svc: pgrep_service(svc) for svc in services + ["feeds"]}
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


def latest_rows(client: Any, key: str, count: int = 8) -> list[dict[str, Any]]:
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
        promoted = str(f.get("activation_promoted") or "0").lower()

        is_hold = bool(
            action in {"", "HOLD"}
            and side in {"", "FLAT"}
            and qty in {"", "0", "0.0"}
            and order_type == ""
            and not broker_side_effects_allowed
            and not live_orders_allowed
            and promoted in {"", "0", "false"}
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


def write_outputs(result: dict[str, Any]) -> None:
    manifest = {
        "batch": BATCH,
        "created_at_utc": now_utc(),
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
        "batch_name": "post_o21_orphan_cleanup",
        "created_at_utc": now_utc(),
        "scope": {
            "cleanup_only": True,
            "paper_restart": False,
            "risk_start": False,
            "execution_start": False,
            "broker_call": False,
            "order_write_intended": False,
            "real_live_enablement": False,
            "forced_candidate": False,
            "threshold_relaxation": False,
            "feeds_allowed_to_remain": True,
        },
    }

    o21 = load_json(O21_PATH)
    result["o21_gate"] = {
        "exists": bool(o21),
        "final_verdict": o21.get("final_verdict"),
        "readiness_status": o21.get("readiness_status"),
        "explicit_real_live_status": o21.get("explicit_real_live_status"),
        "processes": o21.get("processes"),
        "required_verdicts": o21.get("required_verdicts"),
    }

    if o21.get("final_verdict") != "PASS_O21_CONTROLLED_PAPER_PROMOTION_READINESS_OK_REAL_LIVE_BLOCKED":
        result["final_verdict"] = "FAIL_CLOSED_O21_NOT_PASS"
        result["next_recommended_batch"] = "Do not continue. Inspect O21 proof."
        write_outputs(result)
        return 2

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

    cleanup = cleanup_orphans()

    runtime = hgetall(client, runtime_key)
    position = position_summary(hgetall(client, position_key))
    orders_len = xlen(client, orders_key)
    decisions_len = xlen(client, decisions_key)
    latest_orders = latest_rows(client, orders_key, count=5)
    latest_decisions = latest_rows(client, decisions_key, count=12)
    decision_report = decision_safety(latest_decisions)

    real_live = str(runtime.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}

    result.update({
        "cleanup": cleanup,
        "runtime": runtime,
        "position": position,
        "streams": {
            "orders_len": orders_len,
            "decisions_len": decisions_len,
        },
        "latest_orders": latest_orders,
        "latest_decisions": latest_decisions,
        "decision_safety": decision_report,
    })

    required = {
        "compile_pass": compile_result["returncode"] == 0,
        "o21_pass_gate": o21.get("final_verdict") == "PASS_O21_CONTROLLED_PAPER_PROMOTION_READINESS_OK_REAL_LIVE_BLOCKED",
        "redis_available": True,
        "orders_zero": orders_len == 0,
        "latest_orders_empty": len(latest_orders) == 0,
        "position_flat": position["flat"] is True,
        "real_live_false": real_live is False,
        "decisions_hold_only": decision_report["unsafe_count"] == 0,
        "features_not_running_after_cleanup": len(cleanup["after"].get("features", [])) == 0,
        "strategy_not_running_after_cleanup": len(cleanup["after"].get("strategy", [])) == 0,
        "risk_not_running_after_cleanup": len(cleanup["after"].get("risk", [])) == 0,
        "execution_not_running_after_cleanup": len(cleanup["after"].get("execution", [])) == 0,
        "feeds_allowed_to_remain": True,
        "paper_not_restarted": True,
        "broker_not_called": True,
        "real_live_not_enabled": True,
    }
    result["required_verdicts"] = required

    if not all(required.values()):
        result["final_verdict"] = "FAIL_O21R_POST_O21_ORPHAN_CLEANUP_NOT_PROVEN"
        result["next_recommended_batch"] = "Do not proceed to O22. Inspect O21R proof and manually reconcile."
        write_outputs(result)
        return 2

    result["final_verdict"] = "PASS_O21R_POST_O21_ORPHAN_CLEANUP_SAFE"
    result["next_recommended_batch"] = "26-O22 controlled-paper longer observation plan/runbook; still no real live"
    result["explicit_real_live_status"] = "BLOCKED"
    write_outputs(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
