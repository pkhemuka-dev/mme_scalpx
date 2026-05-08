#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any, Mapping

ROOT = pathlib.Path.cwd().resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BATCH = "26-O22A"
PROOF_PATH = ROOT / "run/proofs/proof_batch26o22a_o20r2_o22_proof_chain_consistency.json"
MANIFEST_PATH = ROOT / "run/proofs/manifest_batch26o22a_o20r2_o22_proof_chain_consistency.json"

PATHS = {
    "o19": ROOT / "run/proofs/proof_batch26o19_lightweight_controlled_paper_runtime.json",
    "o20r": ROOT / "run/proofs/proof_batch26o20r_recovery_after_terminated_o20.json",
    "o20r2": ROOT / "run/proofs/proof_batch26o20_r2_bounded_short_observation.json",
    "o20r2_manifest": ROOT / "run/proofs/manifest_batch26o20_r2_bounded_short_observation.json",
    "o21": ROOT / "run/proofs/proof_batch26o21_controlled_paper_promotion_readiness.json",
    "o21r": ROOT / "run/proofs/proof_batch26o21r_post_o21_orphan_cleanup.json",
    "o22": ROOT / "run/proofs/proof_batch26o22_controlled_paper_longer_observation_plan.json",
    "o22_manifest": ROOT / "run/proofs/manifest_batch26o22_controlled_paper_longer_observation_plan.json",
}

TARGETS = [
    "run/proofs/proof_batch26o22_controlled_paper_longer_observation_plan.json",
    "run/proofs/manifest_batch26o22_controlled_paper_longer_observation_plan.json",
    "run/proofs/proof_batch26o20_r2_bounded_short_observation.json",
    "run/proofs/manifest_batch26o20_r2_bounded_short_observation.json",
    "run/proofs/proof_batch26o21_controlled_paper_promotion_readiness.json",
    "run/proofs/proof_batch26o21r_post_o21_orphan_cleanup.json",
    "run/proofs/proof_batch26o20r_recovery_after_terminated_o20.json",
    "run/proofs/proof_batch26o19_lightweight_controlled_paper_runtime.json",
    "bin/proof_batch26o20_r2_bounded_short_observation.py",
    "bin/proof_batch26o22_controlled_paper_longer_observation_plan.py",
    "bin/proof_batch26o22a_o20r2_o22_proof_chain_consistency.py",
    "app/mme_scalpx/main.py",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/core/names.py",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: pathlib.Path) -> str | None:
    if not path.exists() or path.is_dir():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: pathlib.Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        return obj if isinstance(obj, dict) else {}
    except Exception as exc:
        return {"_load_error": f"{type(exc).__name__}: {exc}"}


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


def redis_client_or_none():
    try:
        import redis  # type: ignore
        client = redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=False)
        client.ping()
        return client
    except Exception:
        return None


def decode_hash(raw: Mapping[Any, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in dict(raw or {}).items():
        kk = k.decode("utf-8", "replace") if isinstance(k, bytes) else str(k)
        vv = v.decode("utf-8", "replace") if isinstance(v, bytes) else str(v)
        out[kk] = vv
    return out


def ps_lines() -> list[str]:
    try:
        out = subprocess.check_output(["ps", "-eo", "pid=,ppid=,comm=,args="], text=True)
        return [" ".join(x.split()) for x in out.splitlines() if x.strip()]
    except Exception:
        return []


def pgrep_service(service: str) -> list[str]:
    matches: list[str] = []
    self_name = "proof_batch26o22a_o20r2_o22_proof_chain_consistency.py"
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
    return {"raw": dict(raw), "has_position_raw": has_position_raw, "qty_lots": qty_lots, "qty_units": qty_units, "side": side, "flat": flat}


def summarize_proof(name: str, data: Mapping[str, Any]) -> dict[str, Any]:
    req = data.get("required_verdicts", {}) if isinstance(data.get("required_verdicts"), Mapping) else {}
    return {
        "name": name,
        "exists": bool(data),
        "batch": data.get("batch"),
        "final_verdict": data.get("final_verdict"),
        "readiness_status": data.get("readiness_status"),
        "explicit_real_live_status": data.get("explicit_real_live_status"),
        "next_recommended_batch": data.get("next_recommended_batch"),
        "required_false_keys": sorted([k for k, v in req.items() if v is not True]),
        "streams": data.get("streams"),
        "position": data.get("position"),
        "position_before": data.get("position_before"),
        "position_after": data.get("position_after"),
    }


def find_o20r2_run_dirs() -> list[dict[str, Any]]:
    dirs = sorted((ROOT / "run/live_capture").glob("batch26o20_r2_bounded_short_observation_*"))
    out: list[dict[str, Any]] = []
    for d in dirs[-10:]:
        files = []
        for p in sorted(d.glob("*")):
            files.append({
                "path": str(p.relative_to(ROOT)),
                "is_file": p.is_file(),
                "size": p.stat().st_size if p.exists() else None,
                "sha256": sha256_file(p) if p.is_file() else None,
            })
        tail = {}
        for p in sorted(d.glob("*.log")):
            try:
                tail[str(p.relative_to(ROOT))] = p.read_text(encoding="utf-8", errors="replace").splitlines()[-40:]
            except Exception as exc:
                tail[str(p.relative_to(ROOT))] = [f"READ_ERROR: {type(exc).__name__}: {exc}"]
        out.append({
            "dir": str(d.relative_to(ROOT)),
            "mtime": datetime.fromtimestamp(d.stat().st_mtime, tz=timezone.utc).isoformat(),
            "files": files,
            "log_tail": tail,
        })
    return out


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
        "batch_name": "o20r2_o22_proof_chain_consistency",
        "created_at_utc": now_utc(),
        "scope": {
            "audit_only": True,
            "paper_start": False,
            "risk_start": False,
            "execution_start": False,
            "broker_call": False,
            "order_write_intended": False,
            "real_live_enablement": False,
            "patch_performed": False,
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
    ])
    result["compile"] = compile_result

    proofs = {name: load_json(path) for name, path in PATHS.items()}
    result["proof_summaries"] = {name: summarize_proof(name, data) for name, data in proofs.items() if not name.endswith("_manifest")}
    result["proof_file_hashes"] = {
        name: {
            "path": str(path.relative_to(ROOT)),
            "exists": path.exists(),
            "sha256": sha256_file(path),
            "mtime_utc": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat() if path.exists() else None,
        }
        for name, path in PATHS.items()
    }

    result["o20r2_run_dirs"] = find_o20r2_run_dirs()

    client = redis_client_or_none()
    result["redis_available"] = client is not None
    if client is not None:
        from app.mme_scalpx.core import names as N  # type: ignore
        orders_key = getattr(N, "STREAM_ORDERS_MME", "orders:mme:stream")
        decisions_key = getattr(N, "STREAM_DECISIONS_MME", "decisions:mme:stream")
        runtime_key = getattr(N, "HASH_STATE_RUNTIME", "state:runtime")
        position_key = getattr(N, "HASH_STATE_POSITION_MME", "state:position:mme")
        runtime = hgetall(client, runtime_key)
        position = position_summary(hgetall(client, position_key))
        result["current_runtime_safety"] = {
            "orders_len": xlen(client, orders_key),
            "decisions_len": xlen(client, decisions_key),
            "latest_orders": latest_rows(client, orders_key, count=5),
            "position": position,
            "real_live_approved": str(runtime.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"},
            "runtime": runtime,
        }

    processes = {
        "feeds": pgrep_service("feeds"),
        "features": pgrep_service("features"),
        "strategy": pgrep_service("strategy"),
        "risk": pgrep_service("risk"),
        "execution": pgrep_service("execution"),
    }
    result["processes"] = processes

    o20r2 = proofs["o20r2"]
    o21 = proofs["o21"]
    o21r = proofs["o21r"]
    o22 = proofs["o22"]

    o20r2_verdict = o20r2.get("final_verdict")
    o22_verdict = o22.get("final_verdict")

    o20r2_req = o20r2.get("required_verdicts", {}) if isinstance(o20r2.get("required_verdicts"), Mapping) else {}
    o22_req = o22.get("required_verdicts", {}) if isinstance(o22.get("required_verdicts"), Mapping) else {}

    o20r2_false_keys = sorted([k for k, v in o20r2_req.items() if v is not True])
    o22_false_keys = sorted([k for k, v in o22_req.items() if v is not True])

    # Classification:
    # - If the canonical O20-R2 proof file says FAIL, O22 must remain NOT_READY.
    # - Earlier terminal PASS summaries are not enough to override the stored proof JSON.
    current_orders_zero = result.get("current_runtime_safety", {}).get("orders_len") == 0
    current_position_flat = result.get("current_runtime_safety", {}).get("position", {}).get("flat") is True
    current_real_live_false = result.get("current_runtime_safety", {}).get("real_live_approved") is False

    classification = {
        "canonical_o20r2_file_verdict": o20r2_verdict,
        "canonical_o22_file_verdict": o22_verdict,
        "o20r2_false_keys": o20r2_false_keys,
        "o22_false_keys": o22_false_keys,
        "o21_passed_despite_o20r2_issue": o21.get("final_verdict") == "PASS_O21_CONTROLLED_PAPER_PROMOTION_READINESS_OK_REAL_LIVE_BLOCKED",
        "o21r_cleanup_passed": o21r.get("final_verdict") == "PASS_O21R_POST_O21_ORPHAN_CLEANUP_SAFE",
        "stored_proof_chain_is_consistent_for_blocking_o23": (
            o20r2_verdict != "PASS_O20_R2_BOUNDED_SHORT_OBSERVATION_OK_NO_ORDER"
            and o22_verdict == "FAIL_O22_LONGER_OBSERVATION_PLAN_NOT_PROVEN"
        ),
        "likely_issue": None,
        "recommended_next": None,
    }

    if o20r2_verdict != "PASS_O20_R2_BOUNDED_SHORT_OBSERVATION_OK_NO_ORDER":
        classification["likely_issue"] = "O20-R2 canonical proof is not PASS; O22 correctly blocked O23. Earlier terminal PASS cannot be used as authority until proof-file provenance is repaired or O20-R2 is rerun."
        classification["recommended_next"] = "26-O20-R3 corrected bounded observation rerun with stricter process-liveness accounting and no stale PASS reuse"
    elif o22_verdict != "PASS_O22_LONGER_OBSERVATION_PLAN_READY_REAL_LIVE_BLOCKED":
        classification["likely_issue"] = "O20-R2 canonical proof is PASS but O22 proof logic failed; run O22-R2 proof correction."
        classification["recommended_next"] = "26-O22-R2 proof correction only"
    else:
        classification["likely_issue"] = "No blocking proof-chain inconsistency detected."
        classification["recommended_next"] = "26-O23 controlled-paper longer observation runtime; still no real live"

    result["classification"] = classification

    required = {
        "compile_pass": compile_result["returncode"] == 0,
        "redis_available": client is not None,
        "o22_fail_recorded": o22_verdict == "FAIL_O22_LONGER_OBSERVATION_PLAN_NOT_PROVEN",
        "o23_not_allowed": o22_verdict != "PASS_O22_LONGER_OBSERVATION_PLAN_READY_REAL_LIVE_BLOCKED",
        "current_orders_zero": current_orders_zero,
        "current_position_flat": current_position_flat,
        "current_real_live_false": current_real_live_false,
        "risk_not_running_now": len(processes["risk"]) == 0,
        "execution_not_running_now": len(processes["execution"]) == 0,
        "strategy_not_running_now": len(processes["strategy"]) == 0,
        "features_not_running_now": len(processes["features"]) == 0,
        "audit_only_no_runtime_start": True,
        "broker_not_called": True,
        "real_live_not_enabled": True,
        "patch_not_performed": True,
    }
    result["required_verdicts"] = required

    if not all(required.values()):
        result["final_verdict"] = "FAIL_O22A_PROOF_CHAIN_AUDIT_SAFETY_NOT_PROVEN"
        result["next_recommended_batch"] = "Do not proceed. Inspect O22A proof and manually reconcile."
        write_outputs(result)
        return 2

    if classification["recommended_next"] == "26-O20-R3 corrected bounded observation rerun with stricter process-liveness accounting and no stale PASS reuse":
        result["final_verdict"] = "PASS_O22A_PROOF_CHAIN_AUDIT_BLOCK_O23_RERUN_O20R3_REQUIRED"
        result["next_recommended_batch"] = "26-O20-R3 corrected bounded observation rerun; still no real live"
        write_outputs(result)
        return 0

    if classification["recommended_next"] == "26-O22-R2 proof correction only":
        result["final_verdict"] = "PASS_O22A_PROOF_CHAIN_AUDIT_O22R2_PROOF_CORRECTION_REQUIRED"
        result["next_recommended_batch"] = "26-O22-R2 proof correction only; still no real live"
        write_outputs(result)
        return 0

    result["final_verdict"] = "PASS_O22A_PROOF_CHAIN_AUDIT_READY_FOR_O23"
    result["next_recommended_batch"] = "26-O23 controlled-paper longer observation runtime; still no real live"
    write_outputs(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
