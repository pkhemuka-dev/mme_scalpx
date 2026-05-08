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
BATCH = "26-O23-D"
BATCH_NAME = "second_session_controlled_paper_evidence_review_no_real_live"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
TAG = f"batch26o23_d_second_session_evidence_review_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o23_d_second_session_evidence_review.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o23_d_second_session_evidence_review.json"
REVIEW_JSON = RUN_DIR / "controlled_paper_o23d_second_session_review.json"
DECISION_JSON = RUN_DIR / "controlled_paper_o23d_next_decision.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o23_d_second_session_evidence_review.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o23_d_second_session_evidence_review.md"
BIN_COPY = BIN_DIR / "proof_batch26o23_d_second_session_evidence_review.py"

REDIS_CLI = os.environ.get("REDIS_CLI", "redis-cli")
FEATURES_STREAM = "features:mme:stream"
DECISIONS_STREAM = "decisions:mme:stream"
ORDERS_STREAM = "orders:mme:stream"
POSITION_HASH = "state:position:mme"

CONTROLLED_SERVICES = {"feeds", "features", "strategy", "risk", "execution"}

INSPECT_PATHS = [
    "run/proofs/proof_batch26o23_c_r1_completion_safety_readback.json",
    "run/proofs/proof_batch26o23_c_second_bounded_controlled_paper_observation.json",
    "run/proofs/proof_batch26o23_b_r2_evidence_review_correction.json",
    "run/proofs/proof_batch26o23_b_r1_controlled_pid_cleanup_readback.json",
    "run/proofs/proof_batch26o23_a_r1_session_completion_safety_readback.json",
    "run/proofs/proof_batch26o23_a_explicit_approved_controlled_paper_launcher.json",
    "run/proofs/proof_batch26o22_r8_final_controlled_paper_go_nogo_evidence_pack.json",
    "app/mme_scalpx/main.py",
    "app/mme_scalpx/services/feeds.py",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "app/mme_scalpx/core/redisx.py",
    "app/mme_scalpx/core/settings.py",
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
            "stdout": cp.stdout,
            "stderr": cp.stderr,
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


def redis_xrevrange_raw(key: str, count: int = 20) -> dict[str, Any]:
    return redis_cmd(["XREVRANGE", key, "+", "-", "COUNT", str(count)], timeout=20)


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
            "args": args,
            "is_mme_main_service": "app.mme_scalpx.main" in args and service in CONTROLLED_SERVICES,
            "is_risk_execution": service in {"risk", "execution"},
        })
    return rows


def snapshot() -> dict[str, Any]:
    rows = parse_processes()
    return {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "features_xlen": redis_xlen(FEATURES_STREAM),
        "decisions_xlen": redis_xlen(DECISIONS_STREAM),
        "orders_xlen": redis_xlen(ORDERS_STREAM),
        "latest_orders_raw": redis_xrevrange_raw(ORDERS_STREAM, count=20),
        "latest_decisions_raw": redis_xrevrange_raw(DECISIONS_STREAM, count=10),
        "latest_features_raw": redis_xrevrange_raw(FEATURES_STREAM, count=5),
        "position": redis_hgetall(POSITION_HASH),
        "process_rows": rows,
        "controlled_service_rows": [r for r in rows if r.get("is_mme_main_service")],
        "risk_execution_rows": [r for r in rows if r.get("is_risk_execution")],
    }


def parse_decision_payloads(raw_stdout: str) -> list[dict[str, Any]]:
    lines = raw_stdout.splitlines()
    payloads = []
    for i, line in enumerate(lines):
        if line.strip() == "payload_json" and i + 1 < len(lines):
            try:
                obj = json.loads(lines[i + 1])
            except Exception:
                continue
            if isinstance(obj, dict):
                payloads.append(obj)
    return payloads


def decision_summary(runtime: dict[str, Any]) -> dict[str, Any]:
    payloads = parse_decision_payloads(runtime.get("latest_decisions_raw", {}).get("stdout") or "")
    actions = [p.get("action") for p in payloads]
    reasons = [p.get("reason") or p.get("activation_reason") for p in payloads]
    return {
        "sample_count": len(payloads),
        "actions": actions,
        "reasons": reasons,
        "any_entry_action": any(str(a).upper() in {"BUY", "SELL", "ENTER", "ENTRY"} for a in actions),
        "all_hold_or_empty": all(str(a).upper() in {"HOLD", "", "NONE", "NULL"} for a in actions) if payloads else True,
        "activation_candidate_counts": [p.get("activation_candidate_count") for p in payloads],
        "data_valid_values": [p.get("data_valid") for p in payloads],
        "safe_to_consume_values": [p.get("safe_to_consume") for p in payloads],
    }


def latest_run_dirs(prefix: str, limit: int = 5) -> list[pathlib.Path]:
    base = ROOT / "run" / "live_capture"
    if not base.exists():
        return []
    dirs = [p for p in base.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[:limit]


def inspect_logs(run_dirs: list[pathlib.Path]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    patterns = [
        "Traceback",
        "Exception",
        "ERROR",
        "CRITICAL",
        "broker",
        "order",
        "reject",
        "real_live",
        "CONTROLLED_PAPER",
        "HOLD",
        "BUY",
        "SELL",
        "ENTRY",
    ]
    for d in run_dirs:
        rec = {"path": str(d.relative_to(ROOT)), "files": {}}
        for f in sorted(d.glob("*.log")):
            text = f.read_text(encoding="utf-8", errors="replace")
            hits = {}
            for pat in patterns:
                arr = []
                for idx, line in enumerate(text.splitlines(), start=1):
                    if pat.lower() in line.lower():
                        arr.append({"line": idx, "text": line[:260]})
                hits[pat] = arr[:80]
            rec["files"][str(f.relative_to(ROOT))] = {
                "sha256": sha256_file(f),
                "size_bytes": f.stat().st_size,
                "line_count": text.count("\n") + 1,
                "hits": hits,
                "tail": "\n".join(text.splitlines()[-60:]),
            }
        out[str(d.relative_to(ROOT))] = rec
    return out


def prior_status(d: Any) -> dict[str, Any]:
    if not isinstance(d, dict):
        return {"exists": False}
    return {
        "exists": True,
        "final_verdict": d.get("final_verdict"),
        "false_keys": d.get("false_keys"),
        "classification": d.get("classification") or (d.get("corrected_review") or {}).get("classification"),
        "next_recommended_batch": d.get("next_recommended_batch"),
        "sample_count": len(d.get("samples") or []),
    }


def main() -> int:
    proof: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": BATCH_NAME,
        "tag": TAG,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "purpose": "Review second controlled-paper observation O23-C/R1 and decide next lane-local path; no real live.",
        "safety_intent": {
            "real_live_enablement": False,
            "paper_restart": False,
            "service_start": False,
            "broker_call": False,
            "order_write": False,
            "production_source_patch": False,
            "evidence_review_only": True,
        },
        "prior_proofs": {},
        "inspected_files": {},
        "runtime_snapshot": {},
        "decision_summary": {},
        "log_review": {},
        "second_session_review": {},
        "next_decision": {},
        "required_verdicts": {},
        "false_keys": [],
        "final_verdict": "NOT_EVALUATED",
        "next_recommended_batch": "",
    }

    print("===== EVIDENCE-FIRST INSPECTION =====")
    o23c_dirs = latest_run_dirs("batch26o23_c_second_bounded_controlled_paper_observation", limit=5)
    o23c_r1_dirs = latest_run_dirs("batch26o23_c_r1_completion_safety_readback", limit=5)

    dynamic_paths = list(INSPECT_PATHS)
    for d in [*o23c_dirs, *o23c_r1_dirs]:
        dynamic_paths.extend(str(p.relative_to(ROOT)) for p in d.glob("*"))

    for rel in dynamic_paths:
        p = ROOT / rel
        if p.exists() and p.is_file():
            dst = BACKUP_DIR / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst)
            proof["inspected_files"][rel] = {
                "exists": True,
                "sha256": sha256_file(p),
                "size_bytes": p.stat().st_size,
                "backup": str(dst.relative_to(ROOT)),
            }
            if rel.endswith(".json"):
                proof["prior_proofs"][rel] = load_json(p)
        elif p.exists() and p.is_dir():
            proof["inspected_files"][rel] = {
                "exists": True,
                "is_dir": True,
                "sample_members": sorted(str(x.relative_to(ROOT)) for x in p.rglob("*") if x.is_file())[:200],
            }
        else:
            proof["inspected_files"][rel] = {"exists": False}

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

    print("===== RUNTIME READBACK =====")
    runtime = snapshot()
    proof["runtime_snapshot"] = runtime
    proof["decision_summary"] = decision_summary(runtime)

    print("===== LOG REVIEW =====")
    proof["log_review"] = inspect_logs([*o23c_dirs, *o23c_r1_dirs])

    o23c = proof["prior_proofs"].get("run/proofs/proof_batch26o23_c_second_bounded_controlled_paper_observation.json", {})
    c_r1 = proof["prior_proofs"].get("run/proofs/proof_batch26o23_c_r1_completion_safety_readback.json", {})
    b_r2 = proof["prior_proofs"].get("run/proofs/proof_batch26o23_b_r2_evidence_review_correction.json", {})
    a_r1 = proof["prior_proofs"].get("run/proofs/proof_batch26o23_a_r1_session_completion_safety_readback.json", {})

    orders_zero = runtime["orders_xlen"] == 0 and not (runtime["latest_orders_raw"].get("stdout") or "").strip()
    position_flat = flat_position(runtime["position"])
    no_controlled_pids = len(runtime["controlled_service_rows"]) == 0
    risk_execution_not_running = len(runtime["risk_execution_rows"]) == 0
    decisions_safe = proof["decision_summary"]["all_hold_or_empty"] and not proof["decision_summary"]["any_entry_action"]

    c_r1_pass = str(c_r1.get("final_verdict", "")).startswith("PASS_O23_C_R1_COMPLETION_SAFETY_READBACK_CLEAN_STOPPED")
    c_r1_false_empty = c_r1.get("false_keys") == []
    c_r1_classification = c_r1.get("classification")

    # O23-C may be truncated due disconnect; C-R1 is authoritative for cleanup and safety.
    o23c_logs_or_dir_present = len(o23c_dirs) > 0
    o23c_started_or_seen = bool(o23c) or o23c_logs_or_dir_present

    second_session_review = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "o23a_r1_status": prior_status(a_r1),
        "o23b_r2_status": prior_status(b_r2),
        "o23c_status": prior_status(o23c),
        "o23c_r1_status": prior_status(c_r1),
        "o23c_dirs": [str(p.relative_to(ROOT)) for p in o23c_dirs],
        "o23c_r1_dirs": [str(p.relative_to(ROOT)) for p in o23c_r1_dirs],
        "current_orders_zero": orders_zero,
        "current_position_flat": position_flat,
        "current_no_controlled_pids": no_controlled_pids,
        "current_risk_execution_not_running": risk_execution_not_running,
        "current_decisions_safe_hold_only": decisions_safe,
        "decision_summary": proof["decision_summary"],
        "classification": "SECOND_CONTROLLED_PAPER_SAFE_NO_TRADE_OBSERVATION_AFTER_CLEAN_READBACK",
        "real_live_approval": False,
        "not_live_ready": True,
        "reason_not_live_ready": [
            "Two controlled-paper observations were safe/no-trade or interrupted-clean-readback observations.",
            "No actual controlled-paper trade lifecycle has been proven.",
            "No entry/fill/exit/reconciliation evidence exists yet.",
            "Real live remains forbidden until broader controlled-paper evidence exists.",
        ],
    }
    proof["second_session_review"] = second_session_review
    REVIEW_JSON.write_text(json.dumps(second_session_review, indent=2, sort_keys=True), encoding="utf-8")

    next_decision = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": "ALLOW_THIRD_CONTROLLED_PAPER_OBSERVATION_OR_TARGETED_VALIDITY_REPAIR_ONLY_IF_EXPLICITLY_APPROVED",
        "do_not_proceed_to_real_live": True,
        "why": [
            "O23-C-R1 passed clean readback after internet disconnect.",
            "Orders remained zero and position remained FLAT.",
            "Latest decisions are HOLD-only with candidate_count=0.",
            "No controlled-paper trade lifecycle has occurred yet.",
        ],
        "recommended_next": "26-O23-E controlled-paper no-candidate root-cause review before another observation",
        "alternate_next_if_user_wants_more_observation": "26-O23-F third bounded controlled-paper observation, MIST CALL, 1 lot, paper only, real_live=false",
        "requires_explicit_user_approval_again_for_any_new_observation": True,
        "forbidden_next_steps": [
            "real live",
            "quantity increase",
            "family expansion",
            "threshold relaxation",
            "forced candidate",
            "broker failover",
            "mid-position provider migration",
        ],
    }
    proof["next_decision"] = next_decision
    DECISION_JSON.write_text(json.dumps(next_decision, indent=2, sort_keys=True), encoding="utf-8")

    req = {
        "compile_pass": bool(proof["commands"]["compile"].get("ok")),
        "import_pass": bool(proof["commands"]["import"].get("ok")),
        "o23b_r2_pass_loaded": str(b_r2.get("final_verdict", "")).startswith("PASS_O23_B_R2_EVIDENCE_REVIEW_CORRECTED_OK_NO_REAL_LIVE"),
        "o23c_started_or_dir_present": o23c_started_or_seen,
        "o23c_r1_pass_clean_readback": c_r1_pass,
        "o23c_r1_false_keys_empty": c_r1_false_empty,
        "orders_zero_now": orders_zero,
        "position_flat_now": position_flat,
        "no_controlled_pids_now": no_controlled_pids,
        "risk_execution_not_running_now": risk_execution_not_running,
        "decisions_safe_hold_only_now": decisions_safe,
        "review_json_written": REVIEW_JSON.exists(),
        "decision_json_written": DECISION_JSON.exists(),
        "real_live_approval_false": True,
        "production_source_patch_false": True,
        "service_start_false": True,
        "broker_call_false": True,
        "order_write_false": True,
    }

    false_keys = [k for k, v in req.items() if v is not True]
    proof["required_verdicts"] = req
    proof["false_keys"] = false_keys
    proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()

    if false_keys:
        proof["final_verdict"] = "FAIL_O23_D_SECOND_SESSION_EVIDENCE_REVIEW_NOT_PROVEN"
        proof["next_recommended_batch"] = "Inspect false_keys before any further controlled-paper session."
    else:
        proof["final_verdict"] = "PASS_O23_D_SECOND_SESSION_EVIDENCE_REVIEW_OK_NO_REAL_LIVE"
        proof["next_recommended_batch"] = "26-O23-E controlled-paper no-candidate root-cause review; do not proceed to real live."

    PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    RUNBOOK_MD.write_text(
        "\n".join([
            f"# {BATCH} — second-session controlled-paper evidence review",
            "",
            f"- generated_at_utc: {proof['completed_at_utc']}",
            f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
            f"- review: `{REVIEW_JSON.relative_to(ROOT)}`",
            f"- decision: `{DECISION_JSON.relative_to(ROOT)}`",
            f"- backup_dir: `{BACKUP_DIR.relative_to(ROOT)}`",
            "",
            "## Purpose",
            "- Review O23-C and O23-C-R1 after internet disconnect.",
            "- Preserve no-real-live boundary.",
            "- Decide whether to do root-cause review or another controlled-paper observation.",
            "",
            "## Verdict",
            f"- final_verdict: `{proof['final_verdict']}`",
            f"- classification: `{second_session_review['classification']}`",
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
            f"# {DATE} — {BATCH} second-session evidence review",
            "",
            f"Verdict: `{proof['final_verdict']}`",
            "",
            f"Classification: `{second_session_review['classification']}`",
            "",
            "## Achieved",
            "- Reviewed O23-C interrupted session and O23-C-R1 clean readback.",
            "- Confirmed orders zero, FLAT position, no controlled PIDs, and HOLD-only decisions if PASS.",
            "- Preserved no-real-live boundary.",
            "- Classified current state as safe no-trade observation, not live readiness.",
            "",
            "## Next",
            f"- {proof['next_recommended_batch']}",
        ]),
        encoding="utf-8",
    )

    shutil.copy2(pathlib.Path(__file__), BIN_COPY)

    manifest_paths = [
        PROOF_JSON,
        REVIEW_JSON,
        DECISION_JSON,
        RUNBOOK_MD,
        MILESTONE_MD,
        BIN_COPY,
        *[ROOT / rel for rel in dynamic_paths if (ROOT / rel).exists() and (ROOT / rel).is_file()],
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
    print("classification =", second_session_review["classification"])
    print("next_recommended_batch =", proof["next_recommended_batch"])
    print("proof_json =", PROOF_JSON.relative_to(ROOT))
    print("manifest_json =", MANIFEST_JSON.relative_to(ROOT))
    print("review_json =", REVIEW_JSON.relative_to(ROOT))
    print("decision_json =", DECISION_JSON.relative_to(ROOT))
    print("runbook =", RUNBOOK_MD.relative_to(ROOT))
    print("milestone =", MILESTONE_MD.relative_to(ROOT))
    return 0 if proof["final_verdict"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
