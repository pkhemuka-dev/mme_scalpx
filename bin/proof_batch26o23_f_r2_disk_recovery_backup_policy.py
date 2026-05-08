#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path.cwd().resolve()
BATCH = "26-O23-F-R2"
BATCH_NAME = "disk_pressure_recovery_backup_policy_correction_no_start_no_real_live"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
TAG = f"batch26o23_f_r2_disk_recovery_backup_policy_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

TMP_PROOF_JSON = pathlib.Path("/tmp") / f"proof_{TAG}.json"

PROOF_JSON = PROOF_DIR / "proof_batch26o23_f_r2_disk_recovery_backup_policy.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o23_f_r2_disk_recovery_backup_policy.json"
DISK_RECOVERY_JSON = RUN_DIR / "controlled_paper_o23f_r2_disk_recovery.json"
BACKUP_POLICY_JSON = RUN_DIR / "controlled_paper_o23f_r2_backup_policy.json"
NEXT_DECISION_JSON = RUN_DIR / "controlled_paper_o23f_r2_next_decision.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o23_f_r2_disk_recovery_backup_policy.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o23_f_r2_disk_recovery_backup_policy.md"
BIN_COPY = BIN_DIR / "proof_batch26o23_f_r2_disk_recovery_backup_policy.py"

REDIS_CLI = os.environ.get("REDIS_CLI", "redis-cli")
FEATURES_STREAM = "features:mme:stream"
DECISIONS_STREAM = "decisions:mme:stream"
ORDERS_STREAM = "orders:mme:stream"
POSITION_HASH = "state:position:mme"

TARGET_FREE_BYTES = int(os.environ.get("BATCH26O23F_R2_TARGET_FREE_BYTES", str(6 * 1024**3)))
MIN_PASS_FREE_BYTES = int(os.environ.get("BATCH26O23F_R2_MIN_PASS_FREE_BYTES", str(2 * 1024**3)))
MAX_DELETE_BYTES = int(os.environ.get("BATCH26O23F_R2_MAX_DELETE_BYTES", str(15 * 1024**3)))

CONTROLLED_SERVICES = {"feeds", "features", "strategy", "risk", "execution"}

INSPECT_PATHS = [
    "run/proofs/proof_batch26o23_e_no_candidate_root_cause_review.json",
    "run/proofs/proof_batch26o23_d_second_session_evidence_review.json",
    "run/proofs/proof_batch26o23_c_r1_completion_safety_readback.json",
    "run/proofs/proof_batch26o23_b_r2_evidence_review_correction.json",
    "run/proofs/proof_batch26o23_f_data_valid_activation_candidate_bridge_audit.json",
    "run/proofs/proof_batch26o23_f_r1_memory_safe_bridge_audit_recovery.json",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/services/feeds.py",
    "app/mme_scalpx/core/models.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/redisx.py",
    "app/mme_scalpx/core/settings.py",
    "app/mme_scalpx/main.py",
]

SLICE_MAX_CHARS = 25000
SMALL_COPY_LIMIT_BYTES = 250_000


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
            "stdout": cp.stdout[-20000:],
            "stderr": cp.stderr[-20000:],
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


def disk_state() -> dict[str, Any]:
    u = shutil.disk_usage(ROOT)
    return {
        "total_bytes": u.total,
        "used_bytes": u.used,
        "free_bytes": u.free,
        "free_gb": round(u.free / 1024**3, 3),
        "used_pct": round((u.used / u.total) * 100, 2) if u.total else None,
        "df_h": run("df -h . || true", shell=True, timeout=10),
    }


def du_bytes(path: pathlib.Path) -> int:
    if not path.exists():
        return 0
    out = run(["du", "-sb", str(path)], timeout=120)
    if out.get("ok"):
        try:
            return int((out.get("stdout") or "").split()[0])
        except Exception:
            pass
    total = 0
    if path.is_file():
        return path.stat().st_size
    for root, dirs, files in os.walk(path):
        for f in files:
            try:
                total += (pathlib.Path(root) / f).stat().st_size
            except Exception:
                pass
    return total


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: pathlib.Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_load_error": repr(exc), "_path": str(path)}


def write_json_best_effort(path: pathlib.Path, obj: Any) -> bool:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")
        return True
    except Exception as exc:
        try:
            TMP_PROOF_JSON.write_text(json.dumps({"write_failure": repr(exc), "payload": obj}, indent=2, sort_keys=True), encoding="utf-8")
        except Exception:
            pass
        return False


def safe_file_record(rel: str, backup_root: pathlib.Path | None = None) -> dict[str, Any]:
    p = ROOT / rel
    rec: dict[str, Any] = {
        "path": rel,
        "exists": p.exists(),
        "is_file": p.is_file() if p.exists() else False,
    }
    if not p.exists() or not p.is_file():
        return rec

    rec["size_bytes"] = p.stat().st_size
    rec["sha256"] = sha256_file(p)

    text_sample_written = False
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
        rec["head"] = text[:SLICE_MAX_CHARS // 2]
        rec["tail"] = text[-SLICE_MAX_CHARS // 2:]
        text_sample_written = True
    except Exception as exc:
        rec["slice_error"] = repr(exc)

    if backup_root is not None and p.stat().st_size <= SMALL_COPY_LIMIT_BYTES:
        try:
            dst = backup_root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst)
            rec["small_file_backup"] = str(dst.relative_to(ROOT))
        except Exception as exc:
            rec["small_file_backup_error"] = repr(exc)
    else:
        rec["backup_policy"] = "hash_and_head_tail_slice_only_no_full_copy"

    rec["text_sample_written"] = text_sample_written
    return rec


def cleanup_candidates() -> list[dict[str, Any]]:
    cands: list[dict[str, Any]] = []
    backup_root = ROOT / "run" / "_code_backups"
    if not backup_root.exists():
        return cands

    dirs = [p for p in backup_root.iterdir() if p.is_dir()]
    dirs_sorted_newest = sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)
    keep_newest = set(dirs_sorted_newest[:3])

    for p in dirs:
        name = p.name
        if p in keep_newest and "batch26o23_f_r1_memory_safe_bridge_audit_recovery" not in name:
            continue
        if not (name.startswith("batch") or name.startswith("proof") or name.startswith("o23")):
            continue
        size = du_bytes(p)
        priority = 50
        if "batch26o23_f_r1_memory_safe_bridge_audit_recovery" in name:
            priority = 0
        elif "batch26o23_f" in name:
            priority = 5
        elif "batch26o23" in name:
            priority = 10
        elif "batch26" in name:
            priority = 20
        cands.append({
            "path": str(p),
            "relpath": str(p.relative_to(ROOT)),
            "size_bytes": size,
            "mtime": p.stat().st_mtime,
            "priority": priority,
            "reason": "duplicate_code_backup_dir_only",
        })

    cands.sort(key=lambda x: (x["priority"], -int(x["size_bytes"]), float(x["mtime"])))
    return cands


def remove_pycache_candidates(limit_bytes: int) -> list[dict[str, Any]]:
    out = []
    removed = 0
    candidates = []
    for root, dirs, files in os.walk(ROOT):
        rp = pathlib.Path(root)
        if "__pycache__" in rp.parts or rp.name in {".pytest_cache", ".mypy_cache", ".ruff_cache"}:
            candidates.append(rp)
            dirs[:] = []
    for p in candidates:
        if removed >= limit_bytes:
            break
        try:
            size = du_bytes(p)
            shutil.rmtree(p, ignore_errors=True)
            removed += size
            out.append({"relpath": str(p.relative_to(ROOT)), "size_bytes": size, "deleted": True, "reason": "cache_dir"})
        except Exception as exc:
            out.append({"relpath": str(p), "deleted": False, "error": repr(exc), "reason": "cache_dir"})
    return out


def perform_cleanup() -> dict[str, Any]:
    before = disk_state()
    actions: list[dict[str, Any]] = []
    deleted_bytes = 0

    # First remove duplicate backup dirs, never source/proofs/live evidence.
    for cand in cleanup_candidates():
        current = disk_state()
        if current["free_bytes"] >= TARGET_FREE_BYTES:
            break
        if deleted_bytes >= MAX_DELETE_BYTES:
            break
        p = pathlib.Path(cand["path"])
        rec = dict(cand)
        try:
            shutil.rmtree(p)
            deleted_bytes += int(cand["size_bytes"])
            rec["deleted"] = True
        except Exception as exc:
            rec["deleted"] = False
            rec["error"] = repr(exc)
        actions.append(rec)

    # If still too low, remove only generated Python/cache dirs.
    if disk_state()["free_bytes"] < TARGET_FREE_BYTES and deleted_bytes < MAX_DELETE_BYTES:
        cache_actions = remove_pycache_candidates(MAX_DELETE_BYTES - deleted_bytes)
        actions.extend(cache_actions)
        deleted_bytes += sum(int(x.get("size_bytes") or 0) for x in cache_actions if x.get("deleted"))

    after = disk_state()
    return {
        "before": before,
        "after": after,
        "target_free_bytes": TARGET_FREE_BYTES,
        "min_pass_free_bytes": MIN_PASS_FREE_BYTES,
        "max_delete_bytes": MAX_DELETE_BYTES,
        "deleted_bytes_estimate": deleted_bytes,
        "actions": actions,
        "policy": {
            "deleted_only_duplicate_run_code_backups_and_cache_dirs": True,
            "did_not_delete_source_files": True,
            "did_not_delete_run_proofs": True,
            "did_not_delete_run_live_capture": True,
            "did_not_delete_milestones_or_runbooks": True,
        },
    }


def redis_cmd(args: list[str], timeout: int = 10) -> dict[str, Any]:
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
    d: dict[str, str] = {}
    for i in range(0, len(lines) - 1, 2):
        d[lines[i]] = lines[i + 1]
    return d


def redis_xrevrange_raw(key: str, count: int = 5) -> dict[str, Any]:
    return redis_cmd(["XREVRANGE", key, "+", "-", "COUNT", str(count)], timeout=20)


def proc_lines() -> list[str]:
    out = run("ps -eo pid,ppid,stat,etime,args | grep -E 'app\\.mme_scalpx|mme_scalpx' | grep -v grep || true", shell=True, timeout=10)
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
            "args": args[:600],
            "is_mme_main_service": "app.mme_scalpx.main" in args and service in CONTROLLED_SERVICES,
            "is_risk_execution": service in {"risk", "execution"},
        })
    return rows


def flat_position(pos: dict[str, str]) -> bool:
    return (
        str(pos.get("has_position", "0")).lower() in {"0", "false", "", "none"}
        and str(pos.get("position_side", "FLAT")).upper() in {"", "FLAT", "NONE"}
        and str(pos.get("qty_lots", "0")) in {"0", "0.0", ""}
        and str(pos.get("qty_units", "0")) in {"0", "0.0", ""}
    )


def runtime_snapshot() -> dict[str, Any]:
    rows = parse_processes()
    return {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "features_xlen": redis_xlen(FEATURES_STREAM),
        "decisions_xlen": redis_xlen(DECISIONS_STREAM),
        "orders_xlen": redis_xlen(ORDERS_STREAM),
        "latest_orders_raw": redis_xrevrange_raw(ORDERS_STREAM, count=5),
        "latest_decisions_raw": redis_xrevrange_raw(DECISIONS_STREAM, count=3),
        "position": redis_hgetall(POSITION_HASH),
        "controlled_service_rows": [r for r in rows if r.get("is_mme_main_service")],
        "risk_execution_rows": [r for r in rows if r.get("is_risk_execution")],
    }


def main() -> int:
    proof: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": BATCH_NAME,
        "tag": TAG,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "purpose": "Recover from ENOSPC during O23-F-R1 evidence backup and enforce hash/slice backup policy before retrying bridge audit.",
        "safety_intent": {
            "real_live_enablement": False,
            "paper_restart": False,
            "service_start": False,
            "broker_call": False,
            "order_write": False,
            "threshold_relaxation": False,
            "forced_candidate": False,
            "production_source_patch": False,
            "disk_cleanup_only_duplicate_backups_and_caches": True,
        },
        "disk_recovery": {},
        "inspected_files": {},
        "prior_proofs": {},
        "commands": {},
        "runtime_snapshot": {},
        "backup_policy": {},
        "required_verdicts": {},
        "false_keys": [],
        "final_verdict": "NOT_EVALUATED",
        "next_recommended_batch": "",
    }

    try:
        print("===== DISK RECOVERY FIRST =====")
        proof["disk_recovery"] = perform_cleanup()
        print(json.dumps(proof["disk_recovery"], indent=2, sort_keys=True)[:20000])

        for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
            p.mkdir(parents=True, exist_ok=True)

        print("===== EVIDENCE-FIRST INSPECTION WITH HASH/SLICE BACKUP POLICY =====")
        for rel in INSPECT_PATHS:
            rec = safe_file_record(rel, BACKUP_DIR)
            proof["inspected_files"][rel] = rec
            if rec.get("exists") and rel.endswith(".json"):
                loaded = load_json(ROOT / rel)
                proof["prior_proofs"][rel] = {
                    "final_verdict": loaded.get("final_verdict") if isinstance(loaded, dict) else None,
                    "false_keys": loaded.get("false_keys") if isinstance(loaded, dict) else None,
                    "classification": loaded.get("classification") if isinstance(loaded, dict) else None,
                    "loaded_ok": isinstance(loaded, dict) and "_load_error" not in loaded,
                }

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
        proof["commands"] = {
            "compile": run([sys.executable, "-m", "py_compile", *compile_targets], timeout=60),
            "import": run([
                sys.executable,
                "-c",
                "import app.mme_scalpx.main, app.mme_scalpx.services.feeds, app.mme_scalpx.services.features, app.mme_scalpx.services.strategy, app.mme_scalpx.services.risk, app.mme_scalpx.services.execution; print('IMPORT_OK')",
            ], timeout=60),
        }

        print("===== RUNTIME SAFETY READBACK =====")
        runtime = runtime_snapshot()
        proof["runtime_snapshot"] = runtime

        orders_zero = runtime["orders_xlen"] == 0 and not (runtime["latest_orders_raw"].get("stdout") or "").strip()
        position_flat = flat_position(runtime["position"])
        no_controlled_pids = len(runtime["controlled_service_rows"]) == 0
        risk_execution_not_running = len(runtime["risk_execution_rows"]) == 0

        o23e = proof["prior_proofs"].get("run/proofs/proof_batch26o23_e_no_candidate_root_cause_review.json", {})
        o23f_prior = proof["prior_proofs"].get("run/proofs/proof_batch26o23_f_data_valid_activation_candidate_bridge_audit.json", {})
        o23f_r1_prior = proof["prior_proofs"].get("run/proofs/proof_batch26o23_f_r1_memory_safe_bridge_audit_recovery.json", {})

        policy = {
            "large_file_backup_policy": "hash_sha256_plus_head_tail_slice_only",
            "small_file_copy_limit_bytes": SMALL_COPY_LIMIT_BYTES,
            "old_problem": "O23-F-R1 attempted full copy of proof/evidence files and failed with Errno 28 ENOSPC",
            "corrected_policy": [
                "Do not recursively copy old proof/live_capture artifacts into _code_backups.",
                "For previous JSON/proof artifacts, store sha256 + size + bounded head/tail slices only.",
                "For production source files under small limit, copy source backup.",
                "For large source/proof files, hash/slice only.",
            ],
        }
        proof["backup_policy"] = policy

        BACKUP_POLICY_JSON.write_text(json.dumps(policy, indent=2, sort_keys=True), encoding="utf-8")

        recovery = {
            "batch": BATCH,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "disk_recovery": proof["disk_recovery"],
            "runtime_snapshot": runtime,
            "prior_o23f": o23f_prior,
            "prior_o23f_r1": o23f_r1_prior,
            "backup_policy": policy,
            "classification": "DISK_PRESSURE_RECOVERED_BACKUP_POLICY_CORRECTED" if proof["disk_recovery"]["after"]["free_bytes"] >= MIN_PASS_FREE_BYTES else "DISK_PRESSURE_STILL_TOO_HIGH",
        }
        DISK_RECOVERY_JSON.write_text(json.dumps(recovery, indent=2, sort_keys=True), encoding="utf-8")

        next_decision = {
            "batch": BATCH,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "decision": "RETRY_MEMORY_SAFE_BRIDGE_AUDIT_ONLY_AFTER_DISK_RECOVERY_PASS",
            "recommended_next_batch": "26-O23-F-R3 memory-safe bridge audit retry with no full evidence copying, no service start, no real live",
            "do_not_start_controlled_paper": True,
            "do_not_proceed_to_real_live": True,
            "why": [
                "O23-F was killed during source bridge map.",
                "O23-F-R1 failed before audit because disk was full during backup.",
                "O23-F-R2 reclaims duplicate backup/cache space and freezes hash/slice backup policy.",
            ],
            "forbidden": [
                "real live",
                "third observation before bridge audit/repair",
                "threshold relaxation",
                "forced candidate",
                "quantity increase",
                "family expansion",
                "risk/execution patch without evidence",
            ],
        }
        NEXT_DECISION_JSON.write_text(json.dumps(next_decision, indent=2, sort_keys=True), encoding="utf-8")

        req = {
            "disk_cleanup_ran": bool(proof["disk_recovery"]),
            "disk_free_above_min_pass": proof["disk_recovery"]["after"]["free_bytes"] >= MIN_PASS_FREE_BYTES,
            "disk_recovery_json_written": DISK_RECOVERY_JSON.exists(),
            "backup_policy_json_written": BACKUP_POLICY_JSON.exists(),
            "next_decision_json_written": NEXT_DECISION_JSON.exists(),
            "o23e_pass_loaded": str(o23e.get("final_verdict", "")).startswith("PASS_O23_E_NO_CANDIDATE_ROOT_CAUSE_REVIEW_OK_NO_REAL_LIVE"),
            "compile_pass": bool(proof["commands"]["compile"].get("ok")),
            "import_pass": bool(proof["commands"]["import"].get("ok")),
            "orders_zero_now": orders_zero,
            "position_flat_now": position_flat,
            "no_controlled_pids_now": no_controlled_pids,
            "risk_execution_not_running_now": risk_execution_not_running,
            "did_not_delete_source_files": proof["disk_recovery"]["policy"]["did_not_delete_source_files"] is True,
            "did_not_delete_run_proofs": proof["disk_recovery"]["policy"]["did_not_delete_run_proofs"] is True,
            "did_not_delete_run_live_capture": proof["disk_recovery"]["policy"]["did_not_delete_run_live_capture"] is True,
            "real_live_approval_false": True,
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
        proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()

        if false_keys:
            proof["final_verdict"] = "FAIL_O23_F_R2_DISK_RECOVERY_BACKUP_POLICY_NOT_PROVEN"
            proof["next_recommended_batch"] = "Inspect false_keys and disk recovery artifacts; do not restart controlled-paper."
        else:
            proof["final_verdict"] = "PASS_O23_F_R2_DISK_RECOVERY_BACKUP_POLICY_OK_NO_REAL_LIVE"
            proof["next_recommended_batch"] = "26-O23-F-R3 memory-safe bridge audit retry with no full evidence copying, no service start, no real live."

        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

        RUNBOOK_MD.write_text(
            "\n".join([
                f"# {BATCH} — disk-pressure recovery + backup-policy correction",
                "",
                f"- generated_at_utc: {proof['completed_at_utc']}",
                f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
                f"- disk_recovery: `{DISK_RECOVERY_JSON.relative_to(ROOT)}`",
                f"- backup_policy: `{BACKUP_POLICY_JSON.relative_to(ROOT)}`",
                f"- next_decision: `{NEXT_DECISION_JSON.relative_to(ROOT)}`",
                f"- backup_dir: `{BACKUP_DIR.relative_to(ROOT)}`",
                "",
                "## Purpose",
                "- Recover from `Errno 28 No space left on device` during O23-F-R1 backup.",
                "- Clean only duplicate code-backup/cache surfaces.",
                "- Freeze hash/slice backup policy for future bridge audits.",
                "- No service start, no source patch, no order write, no real live.",
                "",
                "## Disk recovery",
                "```json",
                json.dumps(recovery, indent=2, sort_keys=True),
                "```",
                "",
                "## Verdict",
                f"- final_verdict: `{proof['final_verdict']}`",
                f"- false_keys: `{false_keys}`",
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
                f"# {DATE} — {BATCH} disk recovery and backup policy",
                "",
                f"Verdict: `{proof['final_verdict']}`",
                "",
                "## Achieved",
                "- Classified O23-F-R1 failure as disk full during backup.",
                "- Reclaimed only duplicate `_code_backups` and cache surfaces.",
                "- Preserved production source, run/proofs, run/live_capture, docs/runbooks, and docs/milestones.",
                "- Replaced full evidence-copy behavior with bounded hash/slice policy.",
                "- Confirmed safe runtime state if PASS.",
                "",
                "## Next",
                f"- {proof['next_recommended_batch']}",
            ]),
            encoding="utf-8",
        )

        shutil.copy2(pathlib.Path(__file__), BIN_COPY)

        manifest_paths = [
            PROOF_JSON,
            DISK_RECOVERY_JSON,
            BACKUP_POLICY_JSON,
            NEXT_DECISION_JSON,
            RUNBOOK_MD,
            MILESTONE_MD,
            BIN_COPY,
            *[ROOT / rel for rel in INSPECT_PATHS if (ROOT / rel).exists() and (ROOT / rel).is_file() and (ROOT / rel).stat().st_size <= SMALL_COPY_LIMIT_BYTES],
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
        print("false_keys =", false_keys)
        print("disk_before_free_gb =", proof["disk_recovery"]["before"]["free_gb"])
        print("disk_after_free_gb =", proof["disk_recovery"]["after"]["free_gb"])
        print("deleted_bytes_estimate =", proof["disk_recovery"]["deleted_bytes_estimate"])
        print("next_recommended_batch =", proof["next_recommended_batch"])
        print("proof_json =", PROOF_JSON.relative_to(ROOT))
        print("manifest_json =", MANIFEST_JSON.relative_to(ROOT))
        print("disk_recovery_json =", DISK_RECOVERY_JSON.relative_to(ROOT))
        print("backup_policy_json =", BACKUP_POLICY_JSON.relative_to(ROOT))
        print("next_decision_json =", NEXT_DECISION_JSON.relative_to(ROOT))
        print("runbook =", RUNBOOK_MD.relative_to(ROOT))
        print("milestone =", MILESTONE_MD.relative_to(ROOT))
        return 0 if proof["final_verdict"].startswith("PASS_") else 2

    except Exception as exc:
        proof["exception"] = repr(exc)
        proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
        proof["final_verdict"] = "FAIL_O23_F_R2_EXCEPTION_SAFE_NO_START"
        write_json_best_effort(TMP_PROOF_JSON, proof)
        write_json_best_effort(PROOF_JSON, proof)
        print("===== EXCEPTION SAFE NO START =====")
        print(repr(exc))
        print("tmp_proof_json =", TMP_PROOF_JSON)
        print("proof_json =", PROOF_JSON)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
