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
BATCH = "26-O23-B-R1"
BATCH_NAME = "controlled_paper_pid_ownership_cleanup_readback_no_real_live"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
TAG = f"batch26o23_b_r1_controlled_pid_cleanup_readback_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o23_b_r1_controlled_pid_cleanup_readback.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o23_b_r1_controlled_pid_cleanup_readback.json"
PID_REVIEW_JSON = RUN_DIR / "controlled_paper_pid_review_o23b_r1.json"
SAFETY_JSON = RUN_DIR / "controlled_paper_safety_readback_o23b_r1.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o23_b_r1_controlled_pid_cleanup_readback.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o23_b_r1_controlled_pid_cleanup_readback.md"
BIN_COPY = BIN_DIR / "proof_batch26o23_b_r1_controlled_pid_cleanup_readback.py"

REDIS_CLI = os.environ.get("REDIS_CLI", "redis-cli")
ORDERS_STREAM = "orders:mme:stream"
POSITION_HASH = "state:position:mme"
DECISIONS_STREAM = "decisions:mme:stream"
FEATURES_STREAM = "features:mme:stream"

INSPECT_PATHS = [
    "run/proofs/proof_batch26o23_b_controlled_paper_evidence_review.json",
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
]

CONTROLLED_SERVICES = {"feeds", "features", "strategy", "risk", "execution"}


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
        row = {
            "pid": int(m.group(1)),
            "ppid": int(m.group(2)),
            "stat": m.group(3),
            "etime": m.group(4),
            "service": service,
            "args": args,
            "is_mme_main_service": "app.mme_scalpx.main" in args and service in CONTROLLED_SERVICES,
            "is_risk_execution": service in {"risk", "execution"},
        }
        rows.append(row)
    return rows


def proc_detail(pid: int) -> dict[str, Any]:
    base = pathlib.Path("/proc") / str(pid)
    rec: dict[str, Any] = {"pid": pid, "alive": base.exists()}
    if not base.exists():
        return rec
    try:
        rec["cmdline"] = (base / "cmdline").read_text(errors="replace").replace("\x00", " ")[:5000]
    except Exception as exc:
        rec["cmdline_error"] = repr(exc)
    try:
        status = (base / "status").read_text(errors="replace")
        rec["status"] = "\n".join(
            ln for ln in status.splitlines()
            if ln.startswith(("Name:", "State:", "PPid:", "Threads:", "VmRSS:"))
        )
    except Exception as exc:
        rec["status_error"] = repr(exc)
    try:
        rec["cwd"] = str((base / "cwd").resolve())
    except Exception as exc:
        rec["cwd_error"] = repr(exc)
    return rec


def snapshot() -> dict[str, Any]:
    rows = parse_processes()
    return {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "features_xlen": redis_xlen(FEATURES_STREAM),
        "decisions_xlen": redis_xlen(DECISIONS_STREAM),
        "orders_xlen": redis_xlen(ORDERS_STREAM),
        "latest_orders_raw": redis_xrevrange_raw(ORDERS_STREAM, count=20),
        "latest_decisions_raw": redis_xrevrange_raw(DECISIONS_STREAM, count=10),
        "position": redis_hgetall(POSITION_HASH),
        "process_rows": rows,
        "controlled_service_rows": [r for r in rows if r.get("is_mme_main_service")],
        "risk_execution_rows": [r for r in rows if r.get("is_risk_execution")],
        "pid_details": {str(r["pid"]): proc_detail(int(r["pid"])) for r in rows if r.get("is_mme_main_service")},
    }


def stop_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    priority = {"execution": 0, "risk": 1, "strategy": 2, "features": 3, "feeds": 4}
    out = []
    for row in sorted(rows, key=lambda r: priority.get(r.get("service"), 99)):
        pid = int(row["pid"])
        rec = dict(row)
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(1.5)
            alive = pathlib.Path("/proc").joinpath(str(pid)).exists()
            if alive:
                os.kill(pid, signal.SIGKILL)
                time.sleep(0.5)
                rec["killed"] = True
            else:
                rec["terminated"] = True
        except ProcessLookupError:
            rec["already_exited"] = True
        except Exception as exc:
            rec["stop_error"] = repr(exc)
        out.append(rec)
    return out


def main() -> int:
    proof: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": BATCH_NAME,
        "tag": TAG,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "purpose": "Resolve O23-B false_key no_controlled_pids_now by inspecting controlled-paper process ownership, stopping leftovers, and proving clean readback.",
        "safety_intent": {
            "real_live_enablement": False,
            "paper_restart": False,
            "service_start": False,
            "broker_call": False,
            "order_write": False,
            "production_source_patch": False,
            "cleanup_readback_only": True,
        },
        "prior_proofs": {},
        "inspected_files": {},
        "before_cleanup": {},
        "stop_results": [],
        "after_cleanup": {},
        "classification": "",
        "required_verdicts": {},
        "false_keys": [],
        "final_verdict": "NOT_EVALUATED",
        "next_recommended_batch": "",
    }

    print("===== EVIDENCE-FIRST INSPECTION =====")
    for rel in INSPECT_PATHS:
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
        else:
            proof["inspected_files"][rel] = {"exists": p.exists(), "is_file": p.is_file() if p.exists() else False}

    print("===== BEFORE CLEANUP SNAPSHOT =====")
    before = snapshot()
    proof["before_cleanup"] = before
    print(json.dumps({
        "controlled_service_rows": before["controlled_service_rows"],
        "risk_execution_rows": before["risk_execution_rows"],
        "orders_xlen": before["orders_xlen"],
        "position": before["position"],
    }, indent=2, sort_keys=True))

    print("===== STOP LEFTOVER CONTROLLED SERVICE PIDS =====")
    stop_results = stop_rows(before["controlled_service_rows"])
    proof["stop_results"] = stop_results
    print(json.dumps(stop_results, indent=2, sort_keys=True))

    time.sleep(5)

    print("===== AFTER CLEANUP SNAPSHOT =====")
    after = snapshot()
    proof["after_cleanup"] = after
    print(json.dumps({
        "controlled_service_rows": after["controlled_service_rows"],
        "risk_execution_rows": after["risk_execution_rows"],
        "orders_xlen": after["orders_xlen"],
        "position": after["position"],
    }, indent=2, sort_keys=True))

    o23b = proof["prior_proofs"].get("run/proofs/proof_batch26o23_b_controlled_paper_evidence_review.json", {})
    r1 = proof["prior_proofs"].get("run/proofs/proof_batch26o23_a_r1_session_completion_safety_readback.json", {})

    orders_zero_after = after["orders_xlen"] == 0 and not (after["latest_orders_raw"].get("stdout") or "").strip()
    position_flat_after = flat_position(after["position"])
    no_controlled_pids_after = len(after["controlled_service_rows"]) == 0
    risk_execution_not_running_after = len(after["risk_execution_rows"]) == 0

    if before["controlled_service_rows"] and no_controlled_pids_after and orders_zero_after and position_flat_after:
        classification = "LEFTOVER_CONTROLLED_SERVICE_PIDS_CLEANED_SAFELY"
    elif not before["controlled_service_rows"] and no_controlled_pids_after and orders_zero_after and position_flat_after:
        classification = "NO_LEFTOVER_CONTROLLED_PIDS_FOUND_ON_RECHECK"
    else:
        classification = "CONTROLLED_PID_CLEANUP_NOT_PROVEN"

    proof["classification"] = classification

    req = {
        "o23b_failed_only_on_no_controlled_pids": (
            str(o23b.get("final_verdict", "")).startswith("FAIL_O23_B_CONTROLLED_PAPER_EVIDENCE_REVIEW_NOT_PROVEN")
            and o23b.get("false_keys") == ["no_controlled_pids_now"]
        ),
        "prior_r1_safety_pass_loaded": str(r1.get("final_verdict", "")).startswith("PASS_O23_A_R1_CONTROLLED_PAPER_SAFETY_READBACK_CLEAN_STOPPED"),
        "before_snapshot_captured": bool(before),
        "after_snapshot_captured": bool(after),
        "orders_zero_after": orders_zero_after,
        "position_flat_after": position_flat_after,
        "no_controlled_pids_after": no_controlled_pids_after,
        "risk_execution_not_running_after": risk_execution_not_running_after,
        "no_service_start": True,
        "no_broker_call": True,
        "no_order_write": True,
        "real_live_false": os.environ.get("SCALPX_REAL_LIVE_ALLOWED", "") not in {"1", "true", "TRUE", "yes", "YES"},
        "production_source_patch_false": True,
        "classification_safe": classification in {
            "LEFTOVER_CONTROLLED_SERVICE_PIDS_CLEANED_SAFELY",
            "NO_LEFTOVER_CONTROLLED_PIDS_FOUND_ON_RECHECK",
        },
    }

    false_keys = [k for k, v in req.items() if v is not True]
    proof["required_verdicts"] = req
    proof["false_keys"] = false_keys
    proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()

    if false_keys:
        proof["final_verdict"] = "FAIL_O23_B_R1_CONTROLLED_PID_CLEANUP_NOT_PROVEN"
        proof["next_recommended_batch"] = "Inspect remaining controlled PIDs/process owners before any controlled-paper session."
    else:
        proof["final_verdict"] = "PASS_O23_B_R1_CONTROLLED_PID_CLEANUP_READBACK_OK"
        proof["next_recommended_batch"] = "26-O23-B-R2 evidence review correction using clean PID readback; no real live."

    PID_REVIEW_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
    SAFETY_JSON.write_text(json.dumps({
        "batch": BATCH,
        "generated_at_utc": proof["completed_at_utc"],
        "classification": classification,
        "before_controlled_pids": before["controlled_service_rows"],
        "after_controlled_pids": after["controlled_service_rows"],
        "orders_zero_after": orders_zero_after,
        "position_flat_after": position_flat_after,
        "risk_execution_not_running_after": risk_execution_not_running_after,
    }, indent=2, sort_keys=True), encoding="utf-8")
    PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    RUNBOOK_MD.write_text(
        "\n".join([
            f"# {BATCH} — controlled-paper PID ownership / cleanup readback",
            "",
            f"- generated_at_utc: {proof['completed_at_utc']}",
            f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
            f"- pid_review: `{PID_REVIEW_JSON.relative_to(ROOT)}`",
            f"- safety: `{SAFETY_JSON.relative_to(ROOT)}`",
            "",
            "## Purpose",
            "- O23-B failed only on `no_controlled_pids_now`.",
            "- This batch inspects process ownership, stops leftover controlled service PIDs if present, and proves clean readback.",
            "",
            "## Verdict",
            f"- final_verdict: `{proof['final_verdict']}`",
            f"- classification: `{classification}`",
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
            f"# {DATE} — {BATCH} controlled-paper PID cleanup readback",
            "",
            f"Verdict: `{proof['final_verdict']}`",
            "",
            f"Classification: `{classification}`",
            "",
            "## Achieved",
            "- Inspected O23-B false key.",
            "- Captured before/after process and Redis safety snapshots.",
            "- Stopped leftover controlled service PIDs if present.",
            "- Verified orders zero and FLAT position if PASS.",
            "",
            "## Next",
            f"- {proof['next_recommended_batch']}",
        ]),
        encoding="utf-8",
    )

    shutil.copy2(pathlib.Path(__file__), BIN_COPY)

    manifest_paths = [
        PROOF_JSON,
        PID_REVIEW_JSON,
        SAFETY_JSON,
        RUNBOOK_MD,
        MILESTONE_MD,
        BIN_COPY,
        *[ROOT / rel for rel in INSPECT_PATHS if (ROOT / rel).exists() and (ROOT / rel).is_file()],
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
    print("classification =", classification)
    print("false_keys =", false_keys)
    print("next_recommended_batch =", proof["next_recommended_batch"])
    print("proof_json =", PROOF_JSON.relative_to(ROOT))
    print("manifest_json =", MANIFEST_JSON.relative_to(ROOT))
    print("pid_review_json =", PID_REVIEW_JSON.relative_to(ROOT))
    print("safety_json =", SAFETY_JSON.relative_to(ROOT))
    print("runbook =", RUNBOOK_MD.relative_to(ROOT))
    print("milestone =", MILESTONE_MD.relative_to(ROOT))
    return 0 if proof["final_verdict"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
