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
BATCH = "26-O23-O-R5"
BATCH_NAME = "o23o_r4_nameerror_recovery_no_stream_growth_freeze_no_start_no_real_live"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
TAG = f"batch26o23_o_r5_nameerror_recovery_no_stream_growth_freeze_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o23_o_r5_nameerror_recovery_no_stream_growth_freeze.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o23_o_r5_nameerror_recovery_no_stream_growth_freeze.json"
R3_REVIEW_JSON = RUN_DIR / "controlled_paper_o23o_r5_o23o_r3_review.json"
R4_REVIEW_JSON = RUN_DIR / "controlled_paper_o23o_r5_o23o_r4_nameerror_review.json"
LOG_REVIEW_JSON = RUN_DIR / "controlled_paper_o23o_r5_reconstructed_log_review.json"
NO_STREAM_JSON = RUN_DIR / "controlled_paper_o23o_r5_no_stream_growth_freeze.json"
SAFETY_JSON = RUN_DIR / "controlled_paper_o23o_r5_safety_readback.json"
NEXT_DECISION_JSON = RUN_DIR / "controlled_paper_o23o_r5_next_decision.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o23_o_r5_nameerror_recovery_no_stream_growth_freeze.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o23_o_r5_nameerror_recovery_no_stream_growth_freeze.md"
BIN_COPY = BIN_DIR / "proof_batch26o23_o_r5_nameerror_recovery_no_stream_growth_freeze.py"

REDIS_CLI = os.environ.get("REDIS_CLI", "redis-cli")
FEATURES_STREAM = "features:mme:stream"
DECISIONS_STREAM = "decisions:mme:stream"
ORDERS_STREAM = "orders:mme:stream"
POSITION_HASH = "state:position:mme"

ALL_SERVICES = {"feeds", "features", "strategy", "risk", "execution"}
SMALL_COPY_LIMIT_BYTES = 500_000
MAX_SLICE_CHARS = 18_000

PRIOR_PROOFS = [
    "run/proofs/proof_batch26o23_o_r4_artifact_correction_no_stream_growth.json",
    "run/proofs/proof_batch26o23_o_r3_clean_rerun_readonly_sampler.json",
    "run/proofs/proof_batch26o23_o_r2_interrupted_recovery_readback.json",
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
    "app/mme_scalpx/integrations/provider_runtime.py",
    "app/mme_scalpx/integrations/bootstrap_provider.py",
]


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


def bounded_file_record(rel: str, copy_source: bool = False) -> dict[str, Any]:
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
        rec["sample_files"] = [str(x.relative_to(ROOT)) for x in files[:120]]
        return rec

    rec["size_bytes"] = p.stat().st_size
    rec["sha256"] = sha256_file(p)

    try:
        text = p.read_text(encoding="utf-8", errors="replace")
        rec["head"] = text[:MAX_SLICE_CHARS // 2]
        rec["tail"] = text[-MAX_SLICE_CHARS // 2:]
    except Exception as exc:
        rec["slice_error"] = repr(exc)

    if copy_source and p.stat().st_size <= SMALL_COPY_LIMIT_BYTES and rel.startswith("app/"):
        dst = BACKUP_DIR / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)
        rec["source_backup"] = str(dst.relative_to(ROOT))
    else:
        rec["backup_policy"] = "hash_plus_bounded_slice_only"

    return rec


def load_json_memory_safe(path: pathlib.Path, max_bytes: int = 25_000_000) -> dict[str, Any]:
    rec: dict[str, Any] = {
        "path": str(path.relative_to(ROOT)) if path.exists() else str(path),
        "exists": path.exists(),
    }
    if not path.exists() or not path.is_file():
        return rec

    rec["size_bytes"] = path.stat().st_size
    rec["sha256"] = sha256_file(path)

    if path.stat().st_size <= max_bytes:
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(obj, dict):
                rec["json_loaded"] = True
                rec["obj"] = obj
                rec["final_verdict"] = obj.get("final_verdict")
                rec["classification"] = obj.get("classification")
                rec["false_keys"] = obj.get("false_keys")
                rec["next_recommended_batch"] = obj.get("next_recommended_batch")
                rec["required_verdicts"] = obj.get("required_verdicts") if isinstance(obj.get("required_verdicts"), dict) else {}
                rec["tag"] = obj.get("tag")
                return rec
        except Exception as exc:
            rec["json_load_error"] = repr(exc)

    final_verdict = None
    classification = None
    next_recommended_batch = None
    false_keys_text = []
    required_false_lines = []
    tag = None

    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            in_false = False
            for line in f:
                s = line.strip()

                def grab_string(key: str) -> str | None:
                    m = re.search(rf'"{re.escape(key)}"\s*:\s*"([^"]*)"', s)
                    return m.group(1) if m else None

                final_verdict = final_verdict or grab_string("final_verdict")
                classification = classification or grab_string("classification")
                next_recommended_batch = next_recommended_batch or grab_string("next_recommended_batch")
                tag = tag or grab_string("tag")

                if '"false_keys"' in s:
                    in_false = True
                    false_keys_text.append(s[:500])
                    continue
                if in_false:
                    false_keys_text.append(s[:500])
                    if "]" in s:
                        in_false = False

                if re.search(r':\s*false[,}]?$', s, flags=re.I):
                    required_false_lines.append(s[:500])
                    if len(required_false_lines) > 100:
                        break
    except Exception as exc:
        rec["scan_error"] = repr(exc)

    rec.update({
        "json_loaded": False,
        "final_verdict": final_verdict,
        "classification": classification,
        "next_recommended_batch": next_recommended_batch,
        "tag": tag,
        "false_keys_text": false_keys_text[:80],
        "required_false_lines": required_false_lines[:80],
    })
    return rec


# This is the deliberately fixed helper missing in O23-O-R4.
def load_json_summary(rel: str) -> dict[str, Any]:
    return load_json_memory_safe(ROOT / rel)


def pass_prefix(rec: dict[str, Any], prefix: str) -> bool:
    fv = rec.get("final_verdict")
    return isinstance(fv, str) and fv.startswith(prefix)


def parse_false_keys(rec: dict[str, Any]) -> list[str]:
    fk = rec.get("false_keys")
    if isinstance(fk, list):
        return [str(x) for x in fk]
    text = json.dumps(rec.get("false_keys_text") or "")
    out = []
    for known in [
        "log_review_json_written",
        "pre_no_mme_service_pids",
        "feature_entries_materialized",
        "decision_entries_materialized",
    ]:
        if known in text:
            out.append(known)
    for line in rec.get("required_false_lines") or []:
        m = re.search(r'"([^"]+)"\s*:\s*false', line, flags=re.I)
        if m:
            out.append(m.group(1))
    return sorted(set(out))


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


def parse_processes() -> list[dict[str, Any]]:
    out = run(
        "ps -eo pid,ppid,stat,etime,args | grep -E 'app\\.mme_scalpx|mme_scalpx' | grep -v grep || true",
        shell=True,
        timeout=10,
    )
    rows = []
    for line in (out.get("stdout") or "").splitlines():
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
        "position": redis_hgetall(POSITION_HASH),
        "process_rows": rows,
        "all_mme_service_rows": [r for r in rows if r.get("is_mme_main_service")],
        "risk_execution_rows": [r for r in rows if r.get("is_risk_execution")],
    }


def latest_run_dir(prefix: str, proof: dict[str, Any] | None = None) -> pathlib.Path | None:
    tag = (proof or {}).get("tag")
    if tag:
        p = ROOT / "run/live_capture" / str(tag)
        if p.exists() and p.is_dir():
            return p

    base = ROOT / "run/live_capture"
    if not base.exists():
        return None

    dirs = [p for p in base.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0] if dirs else None


def read_optional_json(path: pathlib.Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        return {"exists": False, "path": str(path.relative_to(ROOT)) if path.exists() else str(path)}
    return load_json_memory_safe(path)


def loaded_obj(rec: dict[str, Any]) -> dict[str, Any]:
    obj = rec.get("obj")
    return obj if isinstance(obj, dict) else {}


def reconstruct_log_review(run_dir: pathlib.Path | None) -> dict[str, Any]:
    review: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_dir.relative_to(ROOT)) if run_dir else None,
        "logs": {},
        "json_artifacts": {},
        "log_file_count": 0,
        "error_line_count": 0,
        "service_exit_indicators": [],
    }

    if not run_dir or not run_dir.exists():
        review["missing_run_dir"] = True
        return review

    for f in sorted(run_dir.glob("*")):
        if not f.is_file():
            continue

        rel = str(f.relative_to(ROOT))
        if f.suffix == ".log":
            text = f.read_text(encoding="utf-8", errors="replace")
            lines = text.splitlines()
            error_lines = []
            signal_lines = []
            for i, line in enumerate(lines, 1):
                low = line.lower()
                if any(tok in low for tok in ["traceback", "exception", "error", "critical", "failed", "killed"]):
                    error_lines.append({"line": i, "text": line[:500]})
                if any(tok in low for tok in ["started", "service", "exited", "returncode", "family", "surface", "candidate", "no_candidate", "feed", "provider", "heartbeat"]):
                    signal_lines.append({"line": i, "text": line[:500]})
            review["logs"][rel] = {
                "sha256": sha256_file(f),
                "size_bytes": f.stat().st_size,
                "tail": "\n".join(lines[-120:]),
                "error_lines": error_lines[:120],
                "signal_lines": signal_lines[:160],
            }
            review["log_file_count"] += 1
            review["error_line_count"] += len(error_lines)

        elif f.suffix == ".json":
            review["json_artifacts"][rel] = load_json_memory_safe(f, max_bytes=5_000_000)

    return review


def review_r4_nameerror() -> dict[str, Any]:
    r4_proof = ROOT / "run/proofs/proof_batch26o23_o_r4_artifact_correction_no_stream_growth.json"
    r4_tmp = pathlib.Path("/tmp/batch26o23_o_r4_artifact_correction_no_stream_growth.py")
    r4_dir = latest_run_dir("batch26o23_o_r4_artifact_correction_no_stream_growth")

    tmp_text = ""
    if r4_tmp.exists():
        tmp_text = r4_tmp.read_text(encoding="utf-8", errors="replace")

    missing_helper = ("load_json_summary(" in tmp_text) and ("def load_json_summary" not in tmp_text)
    nameerror_classified = missing_helper and not r4_proof.exists()

    review = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "r4_proof_exists": r4_proof.exists(),
        "r4_tmp_script_exists": r4_tmp.exists(),
        "r4_tmp_script_sha256": sha256_file(r4_tmp) if r4_tmp.exists() else None,
        "r4_tmp_calls_load_json_summary": "load_json_summary(" in tmp_text,
        "r4_tmp_defines_load_json_summary": "def load_json_summary" in tmp_text,
        "r4_missing_helper_bug_detected": missing_helper,
        "r4_nameerror_classified": nameerror_classified,
        "r4_latest_run_dir": str(r4_dir.relative_to(ROOT)) if r4_dir else None,
        "classification": "O23O_R4_SCRIPT_BUG_NAMEERROR_LOAD_JSON_SUMMARY_MISSING" if nameerror_classified else "O23O_R4_NAMEERROR_NOT_FULLY_PROVEN_FROM_FILES",
        "operator_terminal_output_note": "User pasted NameError: name 'load_json_summary' is not defined.",
    }
    return review


def main() -> int:
    proof: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": BATCH_NAME,
        "tag": TAG,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "purpose": "Recover from O23-O-R4 script NameError, reconstruct log review, and freeze substantive O23-O-R3 no-stream-growth result.",
        "safety_intent": {
            "real_live_enablement": False,
            "paper_start": False,
            "controlled_paper_runtime": False,
            "service_start": False,
            "risk_start": False,
            "execution_start": False,
            "broker_call": False,
            "order_write": False,
            "threshold_relaxation": False,
            "forced_candidate": False,
            "production_source_patch": False,
            "artifact_correction_only": True,
            "fixes_o23o_r4_helper_bug_in_new_script_only": True,
        },
        "disk_state": {},
        "inspected_files": {},
        "prior_proofs": {},
        "commands": {},
        "runtime_snapshot": {},
        "r3_review": {},
        "r4_nameerror_review": {},
        "reconstructed_log_review": {},
        "no_stream_growth_freeze": {},
        "next_decision": {},
        "required_verdicts": {},
        "false_keys": [],
        "classification": "",
        "final_verdict": "NOT_EVALUATED",
        "next_recommended_batch": "",
    }

    print("===== DISK PRECHECK =====")
    proof["disk_state"] = disk_state()

    print("===== EVIDENCE-FIRST INSPECTION =====")
    for rel in PRIOR_PROOFS:
        proof["prior_proofs"][rel] = load_json_summary(rel)

    for rel in SOURCE_PATHS:
        proof["inspected_files"][rel] = bounded_file_record(rel, copy_source=True)

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

    print("===== RUNTIME SAFETY READBACK =====")
    snap = runtime_snapshot()
    proof["runtime_snapshot"] = snap

    orders_zero = snap["orders_xlen"] == 0 and not (snap["latest_orders_raw"].get("stdout") or "").strip()
    position_flat = flat_position(snap["position"])
    no_mme_pids = len(snap["all_mme_service_rows"]) == 0
    no_risk_execution = len(snap["risk_execution_rows"]) == 0

    print("===== REVIEW O23-O-R4 NAMEERROR =====")
    r4_review = review_r4_nameerror()
    proof["r4_nameerror_review"] = r4_review
    R4_REVIEW_JSON.write_text(json.dumps(r4_review, indent=2, sort_keys=True), encoding="utf-8")

    print("===== LOAD O23-O-R3 AND RECONSTRUCT LOG REVIEW =====")
    r3_path = ROOT / "run/proofs/proof_batch26o23_o_r3_clean_rerun_readonly_sampler.json"
    r3 = load_json_memory_safe(r3_path)
    r3_false_keys = parse_false_keys(r3)
    r3_dir = latest_run_dir("batch26o23_o_r3_clean_rerun_readonly_sampler", r3)

    log_review = reconstruct_log_review(r3_dir)
    proof["reconstructed_log_review"] = log_review
    LOG_REVIEW_JSON.write_text(json.dumps(log_review, indent=2, sort_keys=True), encoding="utf-8")

    r3_sample = {}
    r3_surface = {}
    r3_safety = {}
    if r3_dir:
        r3_sample = read_optional_json(r3_dir / "controlled_paper_o23o_r3_sample_review.json")
        r3_surface = read_optional_json(r3_dir / "controlled_paper_o23o_r3_family_surface_matrix.json")
        r3_safety = read_optional_json(r3_dir / "controlled_paper_o23o_r3_safety_readback.json")

    sample_obj = loaded_obj(r3_sample)
    surface_obj = loaded_obj(r3_surface)

    feature_entries = sample_obj.get("feature_entries_since_start")
    decision_entries = sample_obj.get("decision_entries_since_start")
    feature_payload_count = sample_obj.get("feature_payload_count")
    decision_payload_count = sample_obj.get("decision_payload_count")
    best_scope = surface_obj.get("best_evidence_backed_scope")

    no_stream_growth = feature_entries == 0 and decision_entries == 0
    no_payloads = feature_payload_count == 0 and decision_payload_count == 0

    r3_review = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "r3_proof_path": str(r3_path.relative_to(ROOT)),
        "r3_proof_exists": r3_path.exists(),
        "r3_final_verdict": r3.get("final_verdict"),
        "r3_classification": r3.get("classification"),
        "r3_false_keys": r3_false_keys,
        "r3_failed_only_on_log_review_json_written": r3_false_keys == ["log_review_json_written"],
        "r3_run_dir": str(r3_dir.relative_to(ROOT)) if r3_dir else None,
        "sample_review_present": r3_sample.get("exists") is True,
        "surface_matrix_present": r3_surface.get("exists") is True,
        "safety_present": r3_safety.get("exists") is True,
        "reconstructed_log_review_written": LOG_REVIEW_JSON.exists(),
        "feature_entries_since_start": feature_entries,
        "decision_entries_since_start": decision_entries,
        "feature_payload_count": feature_payload_count,
        "decision_payload_count": decision_payload_count,
        "best_evidence_backed_scope": best_scope,
    }
    proof["r3_review"] = r3_review
    R3_REVIEW_JSON.write_text(json.dumps(r3_review, indent=2, sort_keys=True), encoding="utf-8")

    print("===== FREEZE NO STREAM GROWTH CLASSIFICATION =====")
    no_stream_freeze = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "O23O_R5_R4_NAMEERROR_RECOVERED_R3_NO_STREAM_GROWTH_CONFIRMED" if no_stream_growth else "O23O_R5_R4_NAMEERROR_RECOVERED_R3_STREAM_GROWTH_PRESENT",
        "substantive_result": {
            "feature_entries_since_start": feature_entries,
            "decision_entries_since_start": decision_entries,
            "feature_payload_count": feature_payload_count,
            "decision_payload_count": decision_payload_count,
            "best_evidence_backed_scope": best_scope,
            "no_stream_growth": no_stream_growth,
            "no_payloads": no_payloads,
        },
        "operator_interpretation": [
            "O23-O-R4 failed due script helper bug, not production behavior.",
            "O23-O-R3 had no feature/decision entries since sampler start.",
            "O23-O-R3 samples showed readonly_service_count=0 in terminal output, so next work must diagnose service start/liveness/output path.",
            "No family/side scope is evidence-backed for paper expansion.",
        ],
        "paper_started": False,
        "real_live": False,
    }
    proof["no_stream_growth_freeze"] = no_stream_freeze
    NO_STREAM_JSON.write_text(json.dumps(no_stream_freeze, indent=2, sort_keys=True), encoding="utf-8")

    next_decision = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": "RUN_O23_P_SERVICE_START_OUTPUT_DIAGNOSTIC_NEXT",
        "recommended_next_batch": "26-O23-P read-only service start/liveness/output diagnostic for feeds/features/strategy; no paper start, no real live.",
        "do_not_start_paper_yet": True,
        "do_not_proceed_to_real_live": True,
        "why": [
            "O23-O-R4 NameError is recovered in O23-O-R5.",
            "O23-O-R3 substantive result is no feature/decision growth.",
            "Readonly service count was zero during samples, so diagnose service start/liveness and output publication before any more paper.",
            "No evidence-backed family/side scope exists yet.",
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
    proof["next_decision"] = next_decision
    NEXT_DECISION_JSON.write_text(json.dumps(next_decision, indent=2, sort_keys=True), encoding="utf-8")

    o23r2 = proof["prior_proofs"].get("run/proofs/proof_batch26o23_o_r2_interrupted_recovery_readback.json", {})
    o23n = proof["prior_proofs"].get("run/proofs/proof_batch26o23_n_corrected_opportunity_parser_deeper_sampler.json", {})

    req = {
        "o23o_r2_pass_loaded": pass_prefix(o23r2, "PASS_O23_O_R2_INTERRUPTED_RECOVERY_CLEAN_OK_NO_START_NO_REAL_LIVE"),
        "o23n_pass_loaded": pass_prefix(o23n, "PASS_O23_N_CORRECTED_OPPORTUNITY_PARSER_OK_NO_START_NO_REAL_LIVE"),
        "o23o_r4_nameerror_classified": r4_review.get("r4_missing_helper_bug_detected") is True,
        "o23o_r5_helper_defined": True,
        "o23o_r3_proof_exists": r3_path.exists(),
        "o23o_r3_failed_only_on_log_review_json_written": r3_false_keys == ["log_review_json_written"],
        "r3_sample_review_present": r3_sample.get("exists") is True,
        "r3_surface_matrix_present": r3_surface.get("exists") is True,
        "r3_safety_present": r3_safety.get("exists") is True,
        "r3_no_stream_growth_confirmed": no_stream_growth is True,
        "r3_no_payloads_confirmed": no_payloads is True,
        "reconstructed_log_review_json_written": LOG_REVIEW_JSON.exists(),
        "r3_review_json_written": R3_REVIEW_JSON.exists(),
        "r4_review_json_written": R4_REVIEW_JSON.exists(),
        "no_stream_json_written": NO_STREAM_JSON.exists(),
        "safety_json_written": SAFETY_JSON.exists(),
        "next_decision_json_written": NEXT_DECISION_JSON.exists(),
        "compile_pass": bool(proof["commands"]["compile"].get("ok")),
        "import_pass": bool(proof["commands"]["import"].get("ok")),
        "runtime_orders_zero": orders_zero,
        "runtime_position_flat": position_flat,
        "runtime_no_mme_service_pids": no_mme_pids,
        "runtime_no_risk_execution_pids": no_risk_execution,
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
    proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()

    SAFETY_JSON.write_text(json.dumps({
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "runtime_snapshot": snap,
        "orders_zero": orders_zero,
        "position_flat": position_flat,
        "no_mme_service_pids": no_mme_pids,
        "no_risk_execution_pids": no_risk_execution,
        "safety_intent": proof["safety_intent"],
    }, indent=2, sort_keys=True), encoding="utf-8")

    if false_keys:
        proof["classification"] = "O23O_R5_NAMEERROR_RECOVERY_NOT_PROVEN"
        proof["final_verdict"] = "FAIL_O23_O_R5_NAMEERROR_RECOVERY_NOT_PROVEN"
        proof["next_recommended_batch"] = "Inspect false_keys; do not start paper or real live."
    else:
        proof["classification"] = no_stream_freeze["classification"]
        proof["final_verdict"] = "PASS_O23_O_R5_NAMEERROR_RECOVERY_NO_STREAM_GROWTH_FREEZE_OK_NO_START_NO_REAL_LIVE"
        proof["next_recommended_batch"] = next_decision["recommended_next_batch"]

    PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    RUNBOOK_MD.write_text(
        "\n".join([
            f"# {BATCH} — O23-O-R4 NameError recovery / O23-O-R3 no-stream-growth freeze",
            "",
            f"- generated_at_utc: {proof['completed_at_utc']}",
            f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
            f"- r3_review: `{R3_REVIEW_JSON.relative_to(ROOT)}`",
            f"- r4_review: `{R4_REVIEW_JSON.relative_to(ROOT)}`",
            f"- reconstructed_log_review: `{LOG_REVIEW_JSON.relative_to(ROOT)}`",
            f"- no_stream_growth: `{NO_STREAM_JSON.relative_to(ROOT)}`",
            f"- safety: `{SAFETY_JSON.relative_to(ROOT)}`",
            f"- next_decision: `{NEXT_DECISION_JSON.relative_to(ROOT)}`",
            "",
            "## Scope",
            "- No service start.",
            "- No paper start.",
            "- No real live.",
            "- No source patch.",
            "- Recover O23-O-R4 script helper bug only in this proof script.",
            "- Freeze O23-O-R3 substantive no-stream-growth result.",
            "",
            "## Result",
            f"- final_verdict: `{proof['final_verdict']}`",
            f"- classification: `{proof['classification']}`",
            f"- false_keys: `{false_keys}`",
            f"- r3_false_keys: `{r3_false_keys}`",
            f"- feature_entries_since_start: `{feature_entries}`",
            f"- decision_entries_since_start: `{decision_entries}`",
            f"- feature_payload_count: `{feature_payload_count}`",
            f"- decision_payload_count: `{decision_payload_count}`",
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
            f"# {DATE} — {BATCH} O23-O-R4 NameError recovery",
            "",
            f"Verdict: `{proof['final_verdict']}`",
            "",
            f"Classification: `{proof['classification']}`",
            "",
            "## Achieved",
            "- Classified O23-O-R4 proof-script NameError.",
            "- Reconstructed O23-O-R3 log-review artifact.",
            "- Confirmed O23-O-R3 material no-stream-growth result if PASS.",
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
        R3_REVIEW_JSON,
        R4_REVIEW_JSON,
        LOG_REVIEW_JSON,
        NO_STREAM_JSON,
        SAFETY_JSON,
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
    print("r4_nameerror_classification =", r4_review.get("classification"))
    print("r3_final_verdict =", r3.get("final_verdict"))
    print("r3_classification =", r3.get("classification"))
    print("r3_false_keys =", r3_false_keys)
    print("feature_entries_since_start =", feature_entries)
    print("decision_entries_since_start =", decision_entries)
    print("feature_payload_count =", feature_payload_count)
    print("decision_payload_count =", decision_payload_count)
    print("best_evidence_backed_scope =", best_scope)
    print("runtime_orders_zero =", orders_zero)
    print("runtime_position_flat =", position_flat)
    print("runtime_no_mme_service_pids =", no_mme_pids)
    print("next_recommended_batch =", proof["next_recommended_batch"])
    print("proof_json =", PROOF_JSON.relative_to(ROOT))
    print("manifest_json =", MANIFEST_JSON.relative_to(ROOT))
    print("r3_review_json =", R3_REVIEW_JSON.relative_to(ROOT))
    print("r4_review_json =", R4_REVIEW_JSON.relative_to(ROOT))
    print("reconstructed_log_review_json =", LOG_REVIEW_JSON.relative_to(ROOT))
    print("no_stream_json =", NO_STREAM_JSON.relative_to(ROOT))
    print("safety_json =", SAFETY_JSON.relative_to(ROOT))
    print("next_decision_json =", NEXT_DECISION_JSON.relative_to(ROOT))
    print("runbook =", RUNBOOK_MD.relative_to(ROOT))
    print("milestone =", MILESTONE_MD.relative_to(ROOT))
    return 0 if proof["final_verdict"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
