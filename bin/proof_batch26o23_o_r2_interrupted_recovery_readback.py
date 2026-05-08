#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path.cwd().resolve()
BATCH = "26-O23-O-R2"
BATCH_NAME = "interrupted_o23o_r1_recovery_clean_safety_readback_no_start_no_real_live"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
TAG = f"batch26o23_o_r2_interrupted_recovery_readback_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o23_o_r2_interrupted_recovery_readback.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o23_o_r2_interrupted_recovery_readback.json"
RECOVERY_JSON = RUN_DIR / "controlled_paper_o23o_r2_interruption_recovery.json"
PID_READBACK_JSON = RUN_DIR / "controlled_paper_o23o_r2_pid_readback.json"
SAFETY_JSON = RUN_DIR / "controlled_paper_o23o_r2_safety_readback.json"
INTERRUPTED_DIR_REVIEW_JSON = RUN_DIR / "controlled_paper_o23o_r2_interrupted_dir_review.json"
NEXT_DECISION_JSON = RUN_DIR / "controlled_paper_o23o_r2_next_decision.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o23_o_r2_interrupted_recovery_readback.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o23_o_r2_interrupted_recovery_readback.md"
BIN_COPY = BIN_DIR / "proof_batch26o23_o_r2_interrupted_recovery_readback.py"

REDIS_CLI = os.environ.get("REDIS_CLI", "redis-cli")
FEATURES_STREAM = "features:mme:stream"
DECISIONS_STREAM = "decisions:mme:stream"
ORDERS_STREAM = "orders:mme:stream"
POSITION_HASH = "state:position:mme"

ALL_SERVICES = {"feeds", "features", "strategy", "risk", "execution"}
SMALL_COPY_LIMIT_BYTES = 500_000
MAX_SLICE_CHARS = 24_000

PRIOR_PROOF_PATHS = [
    "run/proofs/proof_batch26o23_o_r1_cleanup_rerun_readonly_sampler.json",
    "run/proofs/proof_batch26o23_o_live_readonly_family_surface_sampler.json",
    "run/proofs/proof_batch26o23_n_corrected_opportunity_parser_deeper_sampler.json",
    "run/proofs/proof_batch26o23_m_validate_mist_put_single_scope.json",
    "run/proofs/proof_batch26o23_k_post_repair_evidence_review.json",
]

SOURCE_PATHS = [
    "app/mme_scalpx/main.py",
    "app/mme_scalpx/services/feeds.py",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "app/mme_scalpx/core/redisx.py",
]

INSPECT_PATHS = PRIOR_PROOF_PATHS + SOURCE_PATHS


def run(cmd: list[str] | str, *, timeout: int = 30, shell: bool = False) -> dict[str, Any]:
    try:
        cp = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
            shell=shell,
        )
        return {
            "cmd": cmd if isinstance(cmd, str) else " ".join(cmd),
            "returncode": cp.returncode,
            "stdout": cp.stdout[-30000:],
            "stderr": cp.stderr[-30000:],
            "ok": cp.returncode == 0,
        }
    except Exception as exc:
        return {
            "cmd": cmd if isinstance(cmd, str) else " ".join(cmd),
            "returncode": None,
            "stdout": "",
            "stderr": repr(exc),
            "ok": False,
        }


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def disk_state() -> dict[str, Any]:
    u = shutil.disk_usage(ROOT)
    return {
        "free_bytes": u.free,
        "free_gb": round(u.free / 1024**3, 3),
        "used_pct": round((u.used / u.total) * 100, 2) if u.total else None,
        "df_h": run("df -h . || true", shell=True, timeout=10),
    }


def bounded_text(path: pathlib.Path) -> dict[str, Any]:
    rec: dict[str, Any] = {}
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        rec["head"] = text[:MAX_SLICE_CHARS // 2]
        rec["tail"] = text[-MAX_SLICE_CHARS // 2:]
    except Exception as exc:
        rec["slice_error"] = repr(exc)
    return rec


def scan_json_lines(path: pathlib.Path) -> dict[str, Any]:
    """Memory-safe summary for very large pretty JSON proof files."""
    rec: dict[str, Any] = {
        "exists": path.exists(),
        "path": str(path.relative_to(ROOT)) if path.exists() else str(path),
    }
    if not path.exists() or not path.is_file():
        return rec

    rec["size_bytes"] = path.stat().st_size
    rec["sha256"] = sha256_file(path)

    keys = {
        "final_verdict": None,
        "classification": None,
        "next_recommended_batch": None,
    }
    false_keys_lines = []
    required_false_lines = []

    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            capture_false = False
            for line in f:
                s = line.strip()
                for k in list(keys):
                    if f'"{k}"' in s and ":" in s and keys[k] is None:
                        m = re.search(r':\s*"([^"]*)"', s)
                        if m:
                            keys[k] = m.group(1)

                if '"false_keys"' in s:
                    false_keys_lines.append(s[:500])
                    capture_false = True
                    continue

                if capture_false:
                    false_keys_lines.append(s[:500])
                    if "]" in s:
                        capture_false = False

                if re.search(r':\s*false[,}]?$', s, flags=re.I):
                    required_false_lines.append(s[:500])
                    if len(required_false_lines) >= 80:
                        break
    except Exception as exc:
        rec["scan_error"] = repr(exc)

    rec.update(keys)
    rec["false_keys_lines"] = false_keys_lines[:80]
    rec["required_false_lines"] = required_false_lines[:80]
    rec.update(bounded_text(path))
    return rec


def safe_file_record(rel: str, copy_source: bool = False) -> dict[str, Any]:
    p = ROOT / rel
    rec: dict[str, Any] = {
        "path": rel,
        "exists": p.exists(),
        "is_file": p.is_file() if p.exists() else False,
        "is_dir": p.is_dir() if p.exists() else False,
    }

    if not p.exists():
        return rec

    if p.is_dir():
        files = sorted([x for x in p.rglob("*") if x.is_file()])
        rec["file_count"] = len(files)
        rec["sample_files"] = [str(x.relative_to(ROOT)) for x in files[:250]]
        rec["hash_sample"] = {
            str(x.relative_to(ROOT)): sha256_file(x)
            for x in files[:120]
            if x.stat().st_size <= SMALL_COPY_LIMIT_BYTES
        }
        return rec

    rec["size_bytes"] = p.stat().st_size
    rec["sha256"] = sha256_file(p)
    rec.update(bounded_text(p))

    if copy_source and p.stat().st_size <= SMALL_COPY_LIMIT_BYTES and rel.startswith("app/"):
        dst = BACKUP_DIR / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)
        rec["source_backup"] = str(dst.relative_to(ROOT))
    else:
        rec["backup_policy"] = "hash_plus_bounded_head_tail_slice_only"

    return rec


def load_small_json(path: pathlib.Path, max_bytes: int = 20_000_000) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        return {"exists": False}
    if path.stat().st_size > max_bytes:
        return scan_json_lines(path)
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(obj, dict):
            return {"exists": True, "loaded_type": type(obj).__name__}
        return {
            "exists": True,
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "final_verdict": obj.get("final_verdict"),
            "classification": obj.get("classification"),
            "false_keys": obj.get("false_keys"),
            "next_recommended_batch": obj.get("next_recommended_batch"),
            "required_verdicts": obj.get("required_verdicts") if isinstance(obj.get("required_verdicts"), dict) else {},
            "tag": obj.get("tag"),
        }
    except Exception as exc:
        rec = scan_json_lines(path)
        rec["json_load_error"] = repr(exc)
        return rec


def redis_cmd(args: list[str], timeout: int = 15) -> dict[str, Any]:
    return run([REDIS_CLI, *args], timeout=timeout)


def redis_xlen(key: str) -> int:
    out = redis_cmd(["XLEN", key])
    try:
        return int((out.get("stdout") or "0").strip() or "0")
    except Exception:
        return -1


def redis_hgetall(key: str) -> dict[str, str]:
    out = redis_cmd(["HGETALL", key])
    lines = [x for x in (out.get("stdout") or "").splitlines()]
    d = {}
    for i in range(0, len(lines) - 1, 2):
        d[lines[i]] = lines[i + 1]
    return d


def redis_xrevrange_raw(key: str, count: int = 10) -> dict[str, Any]:
    return redis_cmd(["XREVRANGE", key, "+", "-", "COUNT", str(count)], timeout=20)


def flat_position(pos: dict[str, str]) -> bool:
    if not pos:
        return True
    return (
        str(pos.get("has_position", "0")).lower() in {"0", "false", "", "none"}
        and str(pos.get("position_side", "FLAT")).upper() in {"", "FLAT", "NONE"}
        and str(pos.get("qty_lots", "0")) in {"0", "0.0", ""}
        and str(pos.get("qty_units", "0")) in {"0", "0.0", ""}
    )


def proc_lines() -> list[str]:
    out = run(
        "ps -eo pid,ppid,stat,etime,args | grep -E 'app\\.mme_scalpx|mme_scalpx' | grep -v grep || true",
        shell=True,
        timeout=10,
    )
    return [x for x in (out.get("stdout") or "").splitlines() if x.strip()]


def parse_processes() -> list[dict[str, Any]]:
    rows = []
    for line in proc_lines():
        m = re.match(r"\s*(\d+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(.*)$", line)
        if not m:
            continue
        args = m.group(5)
        sm = re.search(r"--service(?:=|\s+)(feeds|features|strategy|risk|execution|monitor|report)", args)
        service = sm.group(1) if sm else None
        rows.append({
            "pid": int(m.group(1)),
            "ppid": int(m.group(2)),
            "stat": m.group(3),
            "etime": m.group(4),
            "service": service,
            "args": args[:1400],
            "is_mme_main_service": "app.mme_scalpx.main" in args and service in ALL_SERVICES,
            "is_risk_execution": "app.mme_scalpx.main" in args and service in {"risk", "execution"},
        })
    return rows


def runtime_snapshot() -> dict[str, Any]:
    rows = parse_processes()
    return {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "features_xlen": redis_xlen(FEATURES_STREAM),
        "decisions_xlen": redis_xlen(DECISIONS_STREAM),
        "orders_xlen": redis_xlen(ORDERS_STREAM),
        "latest_orders_raw": redis_xrevrange_raw(ORDERS_STREAM, count=10),
        "latest_decisions_raw": redis_xrevrange_raw(DECISIONS_STREAM, count=5),
        "latest_features_raw": redis_xrevrange_raw(FEATURES_STREAM, count=5),
        "position": redis_hgetall(POSITION_HASH),
        "process_rows": rows,
        "all_mme_service_rows": [r for r in rows if r.get("is_mme_main_service")],
        "risk_execution_rows": [r for r in rows if r.get("is_risk_execution")],
    }


def stop_mme_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    priority = {"execution": 0, "risk": 1, "strategy": 2, "features": 3, "feeds": 4}
    out = []
    for row in sorted(rows, key=lambda r: priority.get(r.get("service"), 99)):
        rec = dict(row)
        pid = int(row["pid"])
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(1.5)
            if pathlib.Path("/proc").joinpath(str(pid)).exists():
                os.kill(pid, signal.SIGKILL)
                rec["killed"] = True
            else:
                rec["terminated"] = True
        except ProcessLookupError:
            rec["already_exited"] = True
        except Exception as exc:
            rec["stop_error"] = repr(exc)
        out.append(rec)
    return out


def review_interrupted_dirs() -> dict[str, Any]:
    base = ROOT / "run" / "live_capture"
    out: dict[str, Any] = {
        "latest_o23o_dirs": [],
        "dirs": {},
    }
    if not base.exists():
        return out

    dirs = sorted(
        [p for p in base.iterdir() if p.is_dir() and p.name.startswith("batch26o23_o")],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )[:8]
    out["latest_o23o_dirs"] = [str(p.relative_to(ROOT)) for p in dirs]

    for d in dirs:
        rec: dict[str, Any] = {
            "path": str(d.relative_to(ROOT)),
            "mtime": datetime.fromtimestamp(d.stat().st_mtime, tz=timezone.utc).isoformat(),
            "files": {},
        }
        for f in sorted(d.glob("*")):
            if not f.is_file():
                continue
            frec: dict[str, Any] = {
                "size_bytes": f.stat().st_size,
                "sha256": sha256_file(f),
            }
            if f.suffix == ".json":
                frec["json_summary"] = load_small_json(f)
            elif f.suffix == ".log":
                text = f.read_text(encoding="utf-8", errors="replace")
                frec["tail"] = "\n".join(text.splitlines()[-80:])
                frec["error_lines"] = [
                    {"line": i, "text": line[:400]}
                    for i, line in enumerate(text.splitlines(), 1)
                    if any(tok in line.lower() for tok in ["traceback", "exception", "error", "critical"])
                ][:80]
            else:
                frec.update(bounded_text(f))
            rec["files"][str(f.relative_to(ROOT))] = frec
        out["dirs"][str(d.relative_to(ROOT))] = rec

    return out


def main() -> int:
    proof: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": BATCH_NAME,
        "tag": TAG,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "purpose": "Recover from system shutdown during O23-O-R1; prove clean safety state before retrying sampler.",
        "safety_intent": {
            "real_live_enablement": False,
            "paper_start": False,
            "controlled_paper_runtime": False,
            "service_start": False,
            "cleanup_existing_mme_pids_if_any": True,
            "risk_start": False,
            "execution_start": False,
            "broker_call": False,
            "order_write": False,
            "threshold_relaxation": False,
            "forced_candidate": False,
            "production_source_patch": False,
            "recovery_readback_only": True,
        },
        "disk_state": {},
        "inspected_files": {},
        "prior_proofs": {},
        "commands": {},
        "interrupted_dir_review": {},
        "before_snapshot": {},
        "pid_cleanup_results": [],
        "after_snapshot": {},
        "recovery_summary": {},
        "required_verdicts": {},
        "false_keys": [],
        "classification": "",
        "final_verdict": "NOT_EVALUATED",
        "next_recommended_batch": "",
    }

    print("===== DISK PRECHECK =====")
    proof["disk_state"] = disk_state()

    print("===== EVIDENCE-FIRST INSPECTION =====")
    for rel in INSPECT_PATHS:
        proof["inspected_files"][rel] = safe_file_record(rel, copy_source=rel in SOURCE_PATHS and (ROOT / rel).is_file())
        if rel.endswith(".json"):
            proof["prior_proofs"][rel] = load_small_json(ROOT / rel)

    print("===== COMPILE / IMPORT PROOF =====")
    compile_targets = [
        "app/mme_scalpx/main.py",
        "app/mme_scalpx/services/feeds.py",
        "app/mme_scalpx/services/features.py",
        "app/mme_scalpx/services/strategy.py",
        "app/mme_scalpx/services/risk.py",
        "app/mme_scalpx/services/execution.py",
        "app/mme_scalpx/core/names.py",
        "app/mme_scalpx/core/models.py",
        "app/mme_scalpx/core/redisx.py",
    ]
    proof["commands"]["compile"] = run([sys.executable, "-m", "py_compile", *compile_targets], timeout=60)
    proof["commands"]["import"] = run([
        sys.executable,
        "-c",
        "import app.mme_scalpx.main, app.mme_scalpx.services.feeds, app.mme_scalpx.services.features, app.mme_scalpx.services.strategy, app.mme_scalpx.services.risk, app.mme_scalpx.services.execution; print('IMPORT_OK')",
    ], timeout=60)

    print("===== REVIEW INTERRUPTED O23-O / O23-O-R1 ARTIFACT DIRS =====")
    interrupted = review_interrupted_dirs()
    proof["interrupted_dir_review"] = interrupted
    INTERRUPTED_DIR_REVIEW_JSON.write_text(json.dumps(interrupted, indent=2, sort_keys=True), encoding="utf-8")

    print("===== BEFORE CLEANUP SAFETY SNAPSHOT =====")
    before = runtime_snapshot()
    proof["before_snapshot"] = before

    before_orders_zero = before["orders_xlen"] == 0 and not (before["latest_orders_raw"].get("stdout") or "").strip()
    before_position_flat = flat_position(before["position"])
    before_pids = before["all_mme_service_rows"]
    before_risk_exec = before["risk_execution_rows"]

    print(json.dumps({
        "orders_xlen": before["orders_xlen"],
        "position": before["position"],
        "all_mme_service_rows": before_pids,
        "risk_execution_rows": before_risk_exec,
    }, indent=2, sort_keys=True)[:10000])

    cleanup_allowed = before_orders_zero and before_position_flat
    if before_pids and cleanup_allowed:
        print("===== CLEANUP CURRENT MME PIDS FOUND AFTER POWER LOSS =====")
        proof["pid_cleanup_results"] = stop_mme_rows(before_pids)
        time.sleep(5)
    else:
        print("===== NO PID CLEANUP NEEDED OR NOT ALLOWED =====")
        proof["pid_cleanup_results"] = []

    print("===== AFTER CLEANUP SAFETY SNAPSHOT =====")
    after = runtime_snapshot()
    proof["after_snapshot"] = after

    after_orders_zero = after["orders_xlen"] == 0 and not (after["latest_orders_raw"].get("stdout") or "").strip()
    after_position_flat = flat_position(after["position"])
    after_no_pids = len(after["all_mme_service_rows"]) == 0
    after_no_risk_exec = len(after["risk_execution_rows"]) == 0

    print(json.dumps({
        "orders_xlen": after["orders_xlen"],
        "position": after["position"],
        "all_mme_service_rows": after["all_mme_service_rows"],
        "risk_execution_rows": after["risk_execution_rows"],
    }, indent=2, sort_keys=True)[:10000])

    o23o = proof["prior_proofs"].get("run/proofs/proof_batch26o23_o_live_readonly_family_surface_sampler.json", {})
    o23or1 = proof["prior_proofs"].get("run/proofs/proof_batch26o23_o_r1_cleanup_rerun_readonly_sampler.json", {})
    o23n = proof["prior_proofs"].get("run/proofs/proof_batch26o23_n_corrected_opportunity_parser_deeper_sampler.json", {})

    o23o_refused_on_pre_pids = (
        str(o23o.get("final_verdict", "")).startswith("REFUSE_O23_O_PREFLIGHT_NOT_SAFE_NO_START")
        and "pre_no_mme_service_pids" in json.dumps(o23o.get("false_keys_lines") or o23o.get("false_keys") or "")
    )

    o23or1_missing = not (ROOT / "run/proofs/proof_batch26o23_o_r1_cleanup_rerun_readonly_sampler.json").exists()
    o23or1_dir_exists = any("batch26o23_o_r1_cleanup_rerun_readonly_sampler" in p for p in interrupted.get("latest_o23o_dirs", []))

    recovery_summary = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "o23o_refused_on_pre_no_mme_service_pids": o23o_refused_on_pre_pids,
        "o23or1_proof_missing": o23or1_missing,
        "o23or1_live_capture_dir_exists": o23or1_dir_exists,
        "before_orders_zero": before_orders_zero,
        "before_position_flat": before_position_flat,
        "before_mme_pid_count": len(before_pids),
        "pid_cleanup_attempted_count": len(proof["pid_cleanup_results"]),
        "after_orders_zero": after_orders_zero,
        "after_position_flat": after_position_flat,
        "after_no_mme_service_pids": after_no_pids,
        "after_no_risk_execution_pids": after_no_risk_exec,
        "classification": "POWER_LOSS_INTERRUPTED_O23O_R1_CLEAN_RECOVERY" if after_no_pids and after_orders_zero and after_position_flat else "POWER_LOSS_RECOVERY_NOT_CLEAN",
        "paper_started": False,
        "real_live": False,
    }
    proof["recovery_summary"] = recovery_summary

    next_decision = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": "RERUN_O23_O_READONLY_SURFACE_SAMPLER_AFTER_CLEAN_RECOVERY" if recovery_summary["classification"] == "POWER_LOSS_INTERRUPTED_O23O_R1_CLEAN_RECOVERY" else "STOP_AND_INSPECT_RECOVERY_FALSE_KEYS",
        "recommended_next_batch": "26-O23-O-R3 clean rerun of live-session read-only family-surface sampler; feeds/features/strategy only; no paper; no real live.",
        "do_not_start_paper_yet": True,
        "do_not_proceed_to_real_live": True,
        "why": [
            "O23-O-R1 was interrupted by system shutdown before writing proof.",
            "Recovery package proves whether service PIDs, orders, and position are clean.",
            "Only after clean recovery should the read-only sampler be retried.",
        ],
        "forbidden": [
            "real live",
            "paper start",
            "risk/execution start",
            "threshold relaxation",
            "forced candidate",
            "quantity increase",
            "broker failover",
            "mid-position provider migration",
        ],
    }
    NEXT_DECISION_JSON.write_text(json.dumps(next_decision, indent=2, sort_keys=True), encoding="utf-8")
    PID_READBACK_JSON.write_text(json.dumps({
        "before_snapshot": before,
        "pid_cleanup_results": proof["pid_cleanup_results"],
        "after_snapshot": after,
    }, indent=2, sort_keys=True), encoding="utf-8")
    SAFETY_JSON.write_text(json.dumps({
        "recovery_summary": recovery_summary,
        "before_snapshot": before,
        "after_snapshot": after,
        "safety_intent": proof["safety_intent"],
    }, indent=2, sort_keys=True), encoding="utf-8")
    RECOVERY_JSON.write_text(json.dumps({
        "recovery_summary": recovery_summary,
        "next_decision": next_decision,
        "interrupted_dir_review_path": str(INTERRUPTED_DIR_REVIEW_JSON.relative_to(ROOT)),
        "pid_readback_path": str(PID_READBACK_JSON.relative_to(ROOT)),
        "safety_path": str(SAFETY_JSON.relative_to(ROOT)),
    }, indent=2, sort_keys=True), encoding="utf-8")

    req = {
        "o23n_pass_loaded": str(o23n.get("final_verdict", "")).startswith("PASS_O23_N_CORRECTED_OPPORTUNITY_PARSER_OK_NO_START_NO_REAL_LIVE"),
        "o23o_refused_on_pre_no_mme_service_pids": o23o_refused_on_pre_pids,
        "o23or1_proof_missing": o23or1_missing,
        "o23or1_live_capture_dir_exists": o23or1_dir_exists,
        "compile_pass": bool(proof["commands"]["compile"].get("ok")),
        "import_pass": bool(proof["commands"]["import"].get("ok")),
        "before_snapshot_captured": bool(before),
        "before_orders_zero": before_orders_zero,
        "before_position_flat": before_position_flat,
        "cleanup_allowed_if_pids_found": cleanup_allowed,
        "after_snapshot_captured": bool(after),
        "after_orders_zero": after_orders_zero,
        "after_position_flat": after_position_flat,
        "after_no_mme_service_pids": after_no_pids,
        "after_no_risk_execution_pids": after_no_risk_exec,
        "interrupted_dir_review_json_written": INTERRUPTED_DIR_REVIEW_JSON.exists(),
        "pid_readback_json_written": PID_READBACK_JSON.exists(),
        "safety_json_written": SAFETY_JSON.exists(),
        "recovery_json_written": RECOVERY_JSON.exists(),
        "next_decision_json_written": NEXT_DECISION_JSON.exists(),
        "paper_start_false": True,
        "real_live_false": True,
        "production_source_patch_false": True,
        "service_start_false": True,
        "broker_call_false": True,
        "order_write_false": True,
        "threshold_relaxation_false": True,
        "forced_candidate_false": True,
    }

    false_keys = [k for k, v in req.items() if v is not True]
    proof["required_verdicts"] = req
    proof["false_keys"] = false_keys
    proof["classification"] = recovery_summary["classification"]
    proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()

    if false_keys:
        proof["final_verdict"] = "FAIL_O23_O_R2_INTERRUPTED_RECOVERY_NOT_PROVEN"
        proof["next_recommended_batch"] = "Inspect false_keys; do not retry sampler, paper, or real live."
    else:
        proof["final_verdict"] = "PASS_O23_O_R2_INTERRUPTED_RECOVERY_CLEAN_OK_NO_START_NO_REAL_LIVE"
        proof["next_recommended_batch"] = next_decision["recommended_next_batch"]

    PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    RUNBOOK_MD.write_text(
        "\n".join([
            f"# {BATCH} — interrupted O23-O-R1 recovery",
            "",
            f"- generated_at_utc: {proof['completed_at_utc']}",
            f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
            f"- recovery: `{RECOVERY_JSON.relative_to(ROOT)}`",
            f"- pid_readback: `{PID_READBACK_JSON.relative_to(ROOT)}`",
            f"- safety: `{SAFETY_JSON.relative_to(ROOT)}`",
            f"- interrupted_dir_review: `{INTERRUPTED_DIR_REVIEW_JSON.relative_to(ROOT)}`",
            f"- next_decision: `{NEXT_DECISION_JSON.relative_to(ROOT)}`",
            "",
            "## Purpose",
            "- Recover from system shutdown during O23-O-R1.",
            "- Prove no leftover MME PIDs, zero orders, and FLAT/empty position.",
            "- Do not start services.",
            "- Do not patch source.",
            "- Do not approve paper or real live.",
            "",
            "## Result",
            f"- final_verdict: `{proof['final_verdict']}`",
            f"- classification: `{proof['classification']}`",
            f"- false_keys: `{false_keys}`",
            f"- before_mme_pid_count: `{len(before_pids)}`",
            f"- cleanup_attempted_count: `{len(proof['pid_cleanup_results'])}`",
            f"- after_no_mme_service_pids: `{after_no_pids}`",
            f"- after_orders_zero: `{after_orders_zero}`",
            f"- after_position_flat: `{after_position_flat}`",
            f"- next_recommended_batch: `{proof['next_recommended_batch']}`",
            "",
            "## Required verdicts",
            "```json",
            json.dumps(req, indent=2, sort_keys=True),
            "```",
        ]),
        encoding="utf-8",
    )

    MILESTONE_MD.write_text(
        "\n".join([
            f"# {DATE} — {BATCH} interrupted O23-O-R1 recovery",
            "",
            f"Verdict: `{proof['final_verdict']}`",
            "",
            f"Classification: `{proof['classification']}`",
            "",
            "## Achieved",
            "- Reviewed O23-O refusal and interrupted O23-O-R1 live_capture directory.",
            "- Proved current Redis/order/position safety.",
            "- Cleaned any leftover MME PIDs only if FLAT/zero-order safety allowed it.",
            "- Preserved no-service-start, no-paper, no-real-live, no-source-patch boundary.",
            "",
            "## Next",
            f"- {proof['next_recommended_batch']}",
        ]),
        encoding="utf-8",
    )

    shutil.copy2(pathlib.Path(__file__), BIN_COPY)

    manifest_paths = [
        PROOF_JSON,
        RECOVERY_JSON,
        PID_READBACK_JSON,
        SAFETY_JSON,
        INTERRUPTED_DIR_REVIEW_JSON,
        NEXT_DECISION_JSON,
        RUNBOOK_MD,
        MILESTONE_MD,
        BIN_COPY,
        *[ROOT / rel for rel in SOURCE_PATHS if (ROOT / rel).exists() and (ROOT / rel).is_file() and (ROOT / rel).stat().st_size <= SMALL_COPY_LIMIT_BYTES],
    ]
    manifest = {
        "batch": BATCH,
        "tag": TAG,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "files": {
            str(p.relative_to(ROOT)): sha256_file(p)
            for p in manifest_paths
            if p.exists()
        },
    }
    MANIFEST_JSON.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    print("===== FINAL SUMMARY =====")
    print("final_verdict =", proof["final_verdict"])
    print("classification =", proof["classification"])
    print("false_keys =", false_keys)
    print("o23o_refused_on_pre_no_mme_service_pids =", o23o_refused_on_pre_pids)
    print("o23or1_proof_missing =", o23or1_missing)
    print("o23or1_live_capture_dir_exists =", o23or1_dir_exists)
    print("before_mme_pid_count =", len(before_pids))
    print("cleanup_attempted_count =", len(proof["pid_cleanup_results"]))
    print("after_no_mme_service_pids =", after_no_pids)
    print("after_no_risk_execution_pids =", after_no_risk_exec)
    print("after_orders_zero =", after_orders_zero)
    print("after_position_flat =", after_position_flat)
    print("next_recommended_batch =", proof["next_recommended_batch"])
    print("proof_json =", PROOF_JSON.relative_to(ROOT))
    print("manifest_json =", MANIFEST_JSON.relative_to(ROOT))
    print("recovery_json =", RECOVERY_JSON.relative_to(ROOT))
    print("pid_readback_json =", PID_READBACK_JSON.relative_to(ROOT))
    print("safety_json =", SAFETY_JSON.relative_to(ROOT))
    print("interrupted_dir_review_json =", INTERRUPTED_DIR_REVIEW_JSON.relative_to(ROOT))
    print("next_decision_json =", NEXT_DECISION_JSON.relative_to(ROOT))
    print("runbook =", RUNBOOK_MD.relative_to(ROOT))
    print("milestone =", MILESTONE_MD.relative_to(ROOT))
    return 0 if proof["final_verdict"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
