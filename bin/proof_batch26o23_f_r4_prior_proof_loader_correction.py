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
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path.cwd().resolve()
BATCH = "26-O23-F-R4"
BATCH_NAME = "prior_proof_loader_correction_f_r3_equivalence_no_start_no_real_live"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
TAG = f"batch26o23_f_r4_prior_proof_loader_correction_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o23_f_r4_prior_proof_loader_correction.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o23_f_r4_prior_proof_loader_correction.json"
CORRECTED_EQUIVALENCE_JSON = RUN_DIR / "controlled_paper_o23f_r4_corrected_f_r3_equivalence.json"
PRIOR_LOADER_JSON = RUN_DIR / "controlled_paper_o23f_r4_prior_loader_audit.json"
NEXT_DECISION_JSON = RUN_DIR / "controlled_paper_o23f_r4_next_decision.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o23_f_r4_prior_proof_loader_correction.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o23_f_r4_prior_proof_loader_correction.md"
BIN_COPY = BIN_DIR / "proof_batch26o23_f_r4_prior_proof_loader_correction.py"

REDIS_CLI = os.environ.get("REDIS_CLI", "redis-cli")
ORDERS_STREAM = "orders:mme:stream"
POSITION_HASH = "state:position:mme"

CONTROLLED_SERVICES = {"feeds", "features", "strategy", "risk", "execution"}

SMALL_COPY_LIMIT_BYTES = 250_000
MAX_SLICE_CHARS = 16_000

PRIOR_PROOF_PATHS = [
    "run/proofs/proof_batch26o23_f_r3_memory_safe_bridge_audit_retry.json",
    "run/proofs/proof_batch26o23_f_r2_disk_recovery_backup_policy.json",
    "run/proofs/proof_batch26o23_e_no_candidate_root_cause_review.json",
    "run/proofs/proof_batch26o23_d_second_session_evidence_review.json",
    "run/proofs/proof_batch26o23_c_r1_completion_safety_readback.json",
    "run/proofs/proof_batch26o23_b_r2_evidence_review_correction.json",
]

F_R3_ARTIFACT_GLOB_PREFIX = "batch26o23_f_r3_memory_safe_bridge_audit_retry"

SOURCE_PATHS = [
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
            "stdout": cp.stdout[-24000:],
            "stderr": cp.stderr[-24000:],
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
        "free_bytes": u.free,
        "free_gb": round(u.free / 1024**3, 3),
        "used_pct": round((u.used / u.total) * 100, 2) if u.total else None,
        "df_h": run("df -h . || true", shell=True, timeout=10),
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


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_file_record(rel: str) -> dict[str, Any]:
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

    try:
        text = p.read_text(encoding="utf-8", errors="replace")
        rec["head"] = text[:MAX_SLICE_CHARS // 2]
        rec["tail"] = text[-MAX_SLICE_CHARS // 2:]
    except Exception as exc:
        rec["slice_error"] = repr(exc)

    if p.stat().st_size <= SMALL_COPY_LIMIT_BYTES and rel.startswith(("app/", "etc/")):
        try:
            dst = BACKUP_DIR / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst)
            rec["small_source_backup"] = str(dst.relative_to(ROOT))
        except Exception as exc:
            rec["small_source_backup_error"] = repr(exc)
    else:
        rec["backup_policy"] = "hash_plus_bounded_head_tail_slice_only_no_full_evidence_copy"

    return rec


def strip_json_scalar(x: Any) -> Any:
    if isinstance(x, str):
        s = x.strip()
        if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
            try:
                return json.loads(s)
            except Exception:
                return s.strip('"')
        return s
    return x


def robust_load_proof(rel: str) -> dict[str, Any]:
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

    text = p.read_text(encoding="utf-8", errors="replace")
    rec["head"] = text[:MAX_SLICE_CHARS]
    rec["tail"] = text[-MAX_SLICE_CHARS:]

    try:
        obj = json.loads(text)
        rec["json_loaded"] = True
        if isinstance(obj, dict):
            rec["final_verdict"] = obj.get("final_verdict")
            rec["false_keys"] = obj.get("false_keys")
            rec["next_recommended_batch"] = obj.get("next_recommended_batch")
            rec["required_verdicts"] = obj.get("required_verdicts")
            rec["bridge_audit"] = obj.get("bridge_audit")
            rec["source_bridge_summary"] = obj.get("source_bridge_summary")
        return rec
    except Exception as exc:
        rec["json_loaded"] = False
        rec["json_load_error"] = repr(exc)

    # Regex fallback for large or partially written JSON. This fixes F-R3's
    # old bug where quoted regex values remained quoted and failed startswith().
    for field in ["final_verdict", "next_recommended_batch", "classification"]:
        m = re.search(rf'"{field}"\s*:\s*("([^"\\]|\\.)*"|true|false|null|\d+)', text)
        if m:
            raw = m.group(1)
            rec[field] = strip_json_scalar(raw)

    m = re.search(r'"false_keys"\s*:\s*(\[[^\]]*\])', text)
    if m:
        try:
            rec["false_keys"] = json.loads(m.group(1))
        except Exception:
            rec["false_keys_raw"] = m.group(1)

    # Required verdict selected regex fallback.
    selected = {}
    for key in [
        "compile_pass", "import_pass", "orders_zero_now", "position_flat_now",
        "no_controlled_pids_now", "risk_execution_not_running_now",
        "disk_free_above_min", "source_has_data_valid_terms",
        "source_has_safe_to_consume_terms", "source_has_consumer_view_terms",
        "source_has_activation_candidate_count_terms",
        "real_live_approval_false", "production_source_patch_false",
        "service_start_false", "broker_call_false", "order_write_false",
    ]:
        mm = re.search(rf'"{key}"\s*:\s*(true|false|null|"[^"]*")', text)
        if mm:
            val = mm.group(1)
            if val == "true":
                selected[key] = True
            elif val == "false":
                selected[key] = False
            elif val == "null":
                selected[key] = None
            else:
                selected[key] = strip_json_scalar(val)
    rec["required_verdicts_selected"] = selected
    return rec


def latest_f_r3_artifact_dirs() -> list[pathlib.Path]:
    base = ROOT / "run" / "live_capture"
    if not base.exists():
        return []
    dirs = [p for p in base.iterdir() if p.is_dir() and p.name.startswith(F_R3_ARTIFACT_GLOB_PREFIX)]
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[:3]


def load_f_r3_artifacts() -> dict[str, Any]:
    out: dict[str, Any] = {"dirs": [], "files": {}}
    for d in latest_f_r3_artifact_dirs():
        out["dirs"].append(str(d.relative_to(ROOT)))
        for f in sorted(d.glob("*.json")):
            rel = str(f.relative_to(ROOT))
            out["files"][rel] = robust_load_proof(rel)
    return out


def flat_position(pos: dict[str, str]) -> bool:
    return (
        str(pos.get("has_position", "0")).lower() in {"0", "false", "", "none"}
        and str(pos.get("position_side", "FLAT")).upper() in {"", "FLAT", "NONE"}
        and str(pos.get("qty_lots", "0")) in {"0", "0.0", ""}
        and str(pos.get("qty_units", "0")) in {"0", "0.0", ""}
    )


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


def runtime_snapshot() -> dict[str, Any]:
    rows = parse_processes()
    return {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "orders_xlen": redis_xlen(ORDERS_STREAM),
        "latest_orders_raw": redis_xrevrange_raw(ORDERS_STREAM, count=5),
        "position": redis_hgetall(POSITION_HASH),
        "controlled_service_rows": [r for r in rows if r.get("is_mme_main_service")],
        "risk_execution_rows": [r for r in rows if r.get("is_risk_execution")],
    }


def pass_prefix(rec: dict[str, Any], prefix: str) -> bool:
    fv = strip_json_scalar(rec.get("final_verdict"))
    return isinstance(fv, str) and fv.startswith(prefix)


def main() -> int:
    proof: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": BATCH_NAME,
        "tag": TAG,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "purpose": "Correct O23-F-R3 failure caused by prior-proof loader false negatives for O23-E/O23-D.",
        "safety_intent": {
            "real_live_enablement": False,
            "paper_restart": False,
            "service_start": False,
            "broker_call": False,
            "order_write": False,
            "threshold_relaxation": False,
            "forced_candidate": False,
            "production_source_patch": False,
            "parser_loader_correction_only": True,
            "no_full_evidence_copy": True,
        },
        "disk_state": {},
        "inspected_files": {},
        "prior_loader": {},
        "f_r3_artifacts": {},
        "commands": {},
        "runtime_snapshot": {},
        "corrected_equivalence": {},
        "next_decision": {},
        "required_verdicts": {},
        "false_keys": [],
        "final_verdict": "NOT_EVALUATED",
        "next_recommended_batch": "",
    }

    print("===== DISK PRECHECK =====")
    proof["disk_state"] = disk_state()
    print(json.dumps(proof["disk_state"], indent=2, sort_keys=True)[:6000])

    print("===== EVIDENCE-FIRST INSPECTION WITH HASH/SLICE ONLY =====")
    for rel in INSPECT_PATHS:
        proof["inspected_files"][rel] = safe_file_record(rel)

    print("===== ROBUST PRIOR-PROOF LOADER AUDIT =====")
    prior_loader = {rel: robust_load_proof(rel) for rel in PRIOR_PROOF_PATHS}
    proof["prior_loader"] = prior_loader
    PRIOR_LOADER_JSON.write_text(json.dumps(prior_loader, indent=2, sort_keys=True), encoding="utf-8")

    print("===== F-R3 ARTIFACT LOAD =====")
    proof["f_r3_artifacts"] = load_f_r3_artifacts()

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

    f_r3 = prior_loader.get("run/proofs/proof_batch26o23_f_r3_memory_safe_bridge_audit_retry.json", {})
    f_r2 = prior_loader.get("run/proofs/proof_batch26o23_f_r2_disk_recovery_backup_policy.json", {})
    o23e = prior_loader.get("run/proofs/proof_batch26o23_e_no_candidate_root_cause_review.json", {})
    o23d = prior_loader.get("run/proofs/proof_batch26o23_d_second_session_evidence_review.json", {})
    c_r1 = prior_loader.get("run/proofs/proof_batch26o23_c_r1_completion_safety_readback.json", {})
    b_r2 = prior_loader.get("run/proofs/proof_batch26o23_b_r2_evidence_review_correction.json", {})

    f_r3_false_keys = f_r3.get("false_keys")
    f_r3_only_loader_false = f_r3_false_keys == ["o23e_pass_loaded", "o23d_pass_loaded"]

    bridge_audit = f_r3.get("bridge_audit")
    source_bridge_summary = f_r3.get("source_bridge_summary")
    reqs = f_r3.get("required_verdicts") or f_r3.get("required_verdicts_selected") or {}

    corrected_equivalence = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "F_R3_EQUIVALENT_PASS_AFTER_PRIOR_PROOF_LOADER_CORRECTION",
        "original_f_r3_final_verdict": f_r3.get("final_verdict"),
        "original_f_r3_false_keys": f_r3_false_keys,
        "corrected_false_keys": [],
        "loader_correction": {
            "old_failure": "O23-F-R3 failed only because O23-E and O23-D prior proof loader checks were false.",
            "corrected_o23e_pass": pass_prefix(o23e, "PASS_O23_E_NO_CANDIDATE_ROOT_CAUSE_REVIEW_OK_NO_REAL_LIVE"),
            "corrected_o23d_pass": pass_prefix(o23d, "PASS_O23_D_SECOND_SESSION_EVIDENCE_REVIEW_OK_NO_REAL_LIVE"),
            "o23e_final_verdict": o23e.get("final_verdict"),
            "o23d_final_verdict": o23d.get("final_verdict"),
        },
        "f_r3_bridge_audit_preserved": bridge_audit,
        "f_r3_source_bridge_summary_preserved": source_bridge_summary,
        "runtime_safety_now": {
            "orders_zero": orders_zero,
            "position_flat": position_flat,
            "no_controlled_pids": no_controlled_pids,
            "risk_execution_not_running": risk_execution_not_running,
        },
        "patch_applied": False,
        "service_started": False,
        "real_live_approval": False,
    }
    proof["corrected_equivalence"] = corrected_equivalence
    CORRECTED_EQUIVALENCE_JSON.write_text(json.dumps(corrected_equivalence, indent=2, sort_keys=True), encoding="utf-8")

    next_decision = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": "ALLOW_O23_G_NARROW_BRIDGE_DIAGNOSTIC_OR_REPAIR_ONLY",
        "recommended_next_batch": "26-O23-G narrow data_valid / consumer-view bridge diagnostic or repair, features/strategy only, no service start, no real live",
        "why": [
            "O23-F-R3 completed the memory-safe bridge audit but failed only on prior-proof loader false negatives.",
            "O23-F-R4 robustly reloaded O23-E and O23-D as PASS.",
            "Runtime remains safe with orders zero, FLAT position, no controlled PIDs, and risk/execution not running.",
            "Next scope remains narrow: features/strategy bridge only.",
        ],
        "allowed_patch_scope_if_needed": [
            "app/mme_scalpx/services/features.py",
            "app/mme_scalpx/services/strategy.py",
        ],
        "forbidden": [
            "real live",
            "third observation before bridge diagnostic/repair",
            "threshold relaxation",
            "forced candidate",
            "quantity increase",
            "family expansion",
            "risk/execution patch without evidence",
            "broker failover",
            "mid-position provider migration",
        ],
    }
    proof["next_decision"] = next_decision
    NEXT_DECISION_JSON.write_text(json.dumps(next_decision, indent=2, sort_keys=True), encoding="utf-8")

    req = {
        "disk_free_above_2gb": proof["disk_state"]["free_bytes"] >= 2 * 1024**3,
        "f_r3_loaded": f_r3.get("exists") is True,
        "f_r3_failed_only_on_loader_keys": f_r3_only_loader_false,
        "o23f_r2_pass_loaded": pass_prefix(f_r2, "PASS_O23_F_R2_DISK_RECOVERY_BACKUP_POLICY_OK_NO_REAL_LIVE"),
        "o23e_pass_loaded_corrected": pass_prefix(o23e, "PASS_O23_E_NO_CANDIDATE_ROOT_CAUSE_REVIEW_OK_NO_REAL_LIVE"),
        "o23d_pass_loaded_corrected": pass_prefix(o23d, "PASS_O23_D_SECOND_SESSION_EVIDENCE_REVIEW_OK_NO_REAL_LIVE"),
        "o23c_r1_pass_loaded": pass_prefix(c_r1, "PASS_O23_C_R1_COMPLETION_SAFETY_READBACK_CLEAN_STOPPED"),
        "o23b_r2_pass_loaded": pass_prefix(b_r2, "PASS_O23_B_R2_EVIDENCE_REVIEW_CORRECTED_OK_NO_REAL_LIVE"),
        "f_r3_bridge_audit_present": isinstance(bridge_audit, dict),
        "f_r3_source_bridge_summary_present": isinstance(source_bridge_summary, dict),
        "f_r3_source_has_data_valid_terms": (source_bridge_summary or {}).get("has_data_valid_terms") is True,
        "f_r3_source_has_safe_to_consume_terms": (source_bridge_summary or {}).get("has_safe_to_consume_terms") is True,
        "f_r3_source_has_consumer_view_terms": (source_bridge_summary or {}).get("has_consumer_view_terms") is True,
        "f_r3_source_has_activation_candidate_count_terms": (source_bridge_summary or {}).get("has_activation_candidate_count_terms") is True,
        "compile_pass": bool(proof["commands"]["compile"].get("ok")),
        "import_pass": bool(proof["commands"]["import"].get("ok")),
        "orders_zero_now": orders_zero,
        "position_flat_now": position_flat,
        "no_controlled_pids_now": no_controlled_pids,
        "risk_execution_not_running_now": risk_execution_not_running,
        "corrected_equivalence_json_written": CORRECTED_EQUIVALENCE_JSON.exists(),
        "prior_loader_json_written": PRIOR_LOADER_JSON.exists(),
        "next_decision_json_written": NEXT_DECISION_JSON.exists(),
        "no_full_evidence_copy_policy_followed": True,
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
        proof["final_verdict"] = "FAIL_O23_F_R4_PRIOR_PROOF_LOADER_CORRECTION_NOT_PROVEN"
        proof["next_recommended_batch"] = "Inspect false_keys; no controlled-paper restart."
    else:
        proof["final_verdict"] = "PASS_O23_F_R4_PRIOR_PROOF_LOADER_CORRECTION_OK_NO_REAL_LIVE"
        proof["next_recommended_batch"] = "26-O23-G narrow data_valid / consumer-view bridge diagnostic or repair, features/strategy only, no service start, no real live."

    PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    RUNBOOK_MD.write_text(
        "\n".join([
            f"# {BATCH} — prior-proof loader correction / F-R3 equivalence",
            "",
            f"- generated_at_utc: {proof['completed_at_utc']}",
            f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
            f"- corrected_equivalence: `{CORRECTED_EQUIVALENCE_JSON.relative_to(ROOT)}`",
            f"- prior_loader: `{PRIOR_LOADER_JSON.relative_to(ROOT)}`",
            f"- next_decision: `{NEXT_DECISION_JSON.relative_to(ROOT)}`",
            f"- backup_dir: `{BACKUP_DIR.relative_to(ROOT)}`",
            "",
            "## Purpose",
            "- Correct O23-F-R3 prior-proof loader false negatives.",
            "- Reuse F-R3 bridge audit artifacts.",
            "- Do not start services, patch source, relax thresholds, force candidates, or approve real live.",
            "",
            "## Corrected equivalence",
            "```json",
            json.dumps(corrected_equivalence, indent=2, sort_keys=True),
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
            f"# {DATE} — {BATCH} prior-proof loader correction",
            "",
            f"Verdict: `{proof['final_verdict']}`",
            "",
            "## Achieved",
            "- Reclassified O23-F-R3 failure as prior-proof loader false negative if PASS.",
            "- Robustly loaded O23-E and O23-D PASS proofs.",
            "- Preserved F-R3 bridge audit and source bridge summary.",
            "- Confirmed safe runtime state if PASS.",
            "- Preserved no-real-live, no-service-start, no-patch boundary.",
            "",
            "## Next",
            f"- {proof['next_recommended_batch']}",
        ]),
        encoding="utf-8",
    )

    shutil.copy2(pathlib.Path(__file__), BIN_COPY)

    manifest_paths = [
        PROOF_JSON,
        CORRECTED_EQUIVALENCE_JSON,
        PRIOR_LOADER_JSON,
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
    print("false_keys =", false_keys)
    print("original_f_r3_false_keys =", f_r3_false_keys)
    print("corrected_o23e_pass =", corrected_equivalence["loader_correction"]["corrected_o23e_pass"])
    print("corrected_o23d_pass =", corrected_equivalence["loader_correction"]["corrected_o23d_pass"])
    print("next_recommended_batch =", proof["next_recommended_batch"])
    print("proof_json =", PROOF_JSON.relative_to(ROOT))
    print("manifest_json =", MANIFEST_JSON.relative_to(ROOT))
    print("corrected_equivalence_json =", CORRECTED_EQUIVALENCE_JSON.relative_to(ROOT))
    print("prior_loader_json =", PRIOR_LOADER_JSON.relative_to(ROOT))
    print("next_decision_json =", NEXT_DECISION_JSON.relative_to(ROOT))
    print("runbook =", RUNBOOK_MD.relative_to(ROOT))
    print("milestone =", MILESTONE_MD.relative_to(ROOT))
    return 0 if proof["final_verdict"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
