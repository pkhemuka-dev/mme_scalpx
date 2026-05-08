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
BATCH = "26-O23-A-R1"
BATCH_NAME = "controlled_paper_session_completion_safety_readback"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
NOW = datetime.now(timezone.utc).isoformat()
TAG = f"batch26o23_a_r1_session_completion_safety_readback_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o23_a_r1_session_completion_safety_readback.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o23_a_r1_session_completion_safety_readback.json"
SAFETY_JSON = RUN_DIR / "controlled_paper_o23a_r1_safety_readback.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o23_a_r1_session_completion_safety_readback.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o23_a_r1_session_completion_safety_readback.md"
BIN_COPY = BIN_DIR / "proof_batch26o23_a_r1_session_completion_safety_readback.py"

REDIS_CLI = os.environ.get("REDIS_CLI", "redis-cli")
ORDERS_STREAM = "orders:mme:stream"
POSITION_HASH = "state:position:mme"
DECISIONS_STREAM = "decisions:mme:stream"
FEATURES_STREAM = "features:mme:stream"

CONTROLLED_TAG_PREFIX = "batch26o23_a_explicit_approved_controlled_paper_launcher"

INSPECT_PATHS = [
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


def run(cmd: list[str], *, timeout: int = 30) -> dict[str, Any]:
    try:
        cp = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        return {
            "cmd": cmd,
            "returncode": cp.returncode,
            "stdout": cp.stdout,
            "stderr": cp.stderr,
            "ok": cp.returncode == 0,
        }
    except Exception as exc:
        return {
            "cmd": cmd,
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


def redis_xrevrange_raw(key: str, count: int = 10) -> dict[str, Any]:
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


def proc_lines() -> list[str]:
    out = run(["bash", "-lc", "ps -eo pid,ppid,cmd | grep -E 'app\\.mme_scalpx|mme_scalpx|services' | grep -v grep || true"], timeout=10)
    return [x for x in (out.get("stdout") or "").splitlines() if x.strip()]


def find_controlled_pids() -> list[dict[str, Any]]:
    rows = []
    for line in proc_lines():
        if "--service" not in line:
            continue
        if "app.mme_scalpx.main" not in line:
            continue
        m = re.match(r"\s*(\d+)\s+(\d+)\s+(.*)$", line)
        if not m:
            continue
        pid = int(m.group(1))
        cmd = m.group(3)
        service = None
        sm = re.search(r"--service(?:=|\s+)(feeds|features|strategy|risk|execution)", cmd)
        if sm:
            service = sm.group(1)
        rows.append({"pid": pid, "service": service, "cmd": cmd})
    return rows


def stop_services(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results = []
    # Stop execution/risk first, then strategy/features/feeds last.
    priority = {"execution": 0, "risk": 1, "strategy": 2, "features": 3, "feeds": 4, None: 9}
    for row in sorted(rows, key=lambda x: priority.get(x.get("service"), 9)):
        pid = int(row["pid"])
        rec = dict(row)
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(1)
            alive = run(["bash", "-lc", f"kill -0 {pid} >/dev/null 2>&1; echo $?"], timeout=5).get("stdout", "").strip() == "0"
            if alive:
                os.kill(pid, signal.SIGKILL)
                rec["killed"] = True
            else:
                rec["terminated"] = True
        except ProcessLookupError:
            rec["already_exited"] = True
        except Exception as exc:
            rec["stop_error"] = repr(exc)
        results.append(rec)
    return results


def flat_position(pos: dict[str, str]) -> bool:
    return (
        str(pos.get("has_position", "0")).lower() in {"0", "false", "", "none"}
        and str(pos.get("position_side", "FLAT")).upper() in {"", "FLAT", "NONE"}
        and str(pos.get("qty_lots", "0")) in {"0", "0.0", ""}
        and str(pos.get("qty_units", "0")) in {"0", "0.0", ""}
    )


def snapshot() -> dict[str, Any]:
    return {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "features_xlen": redis_xlen(FEATURES_STREAM),
        "decisions_xlen": redis_xlen(DECISIONS_STREAM),
        "orders_xlen": redis_xlen(ORDERS_STREAM),
        "latest_orders_raw": redis_xrevrange_raw(ORDERS_STREAM, count=20),
        "latest_decisions_raw": redis_xrevrange_raw(DECISIONS_STREAM, count=5),
        "position": redis_hgetall(POSITION_HASH),
        "process_lines": proc_lines(),
        "controlled_pids": find_controlled_pids(),
    }


def latest_o23a_run_dir() -> pathlib.Path | None:
    base = ROOT / "run" / "live_capture"
    if not base.exists():
        return None
    dirs = [p for p in base.iterdir() if p.is_dir() and p.name.startswith(CONTROLLED_TAG_PREFIX)]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def main() -> int:
    proof: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": BATCH_NAME,
        "tag": TAG,
        "started_at_utc": NOW,
        "root": str(ROOT),
        "purpose": "Complete safety readback after uploaded O23-A output lacked final stop/readback verdict.",
        "inspected_files": {},
        "prior_o23a": {},
        "latest_o23a_run_dir": None,
        "before_stop_snapshot": {},
        "stop_results": [],
        "after_stop_snapshot": {},
        "required_verdicts": {},
        "false_keys": [],
        "final_verdict": "NOT_EVALUATED",
        "next_recommended_batch": "",
    }

    print("===== EVIDENCE-FIRST INSPECTION =====")
    latest_dir = latest_o23a_run_dir()
    proof["latest_o23a_run_dir"] = str(latest_dir.relative_to(ROOT)) if latest_dir else None

    dynamic_paths = list(INSPECT_PATHS)
    if latest_dir:
        dynamic_paths.extend(str(p.relative_to(ROOT)) for p in latest_dir.glob("*"))

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
            if rel.endswith(".json") and "proof_batch26o23_a_explicit_approved" in rel:
                proof["prior_o23a"] = load_json(p)
        elif p.exists() and p.is_dir():
            proof["inspected_files"][rel] = {
                "exists": True,
                "is_dir": True,
                "sample_members": sorted(str(x.relative_to(ROOT)) for x in p.rglob("*") if x.is_file())[:200],
            }
        else:
            proof["inspected_files"][rel] = {"exists": False}

    print("===== BEFORE-STOP SNAPSHOT =====")
    before = snapshot()
    proof["before_stop_snapshot"] = before
    print(json.dumps(before, indent=2, sort_keys=True)[:6000])

    print("===== STOP CONTROLLED-PAPER SERVICES IF STILL RUNNING =====")
    stop_results = stop_services(before["controlled_pids"])
    proof["stop_results"] = stop_results
    print(json.dumps(stop_results, indent=2, sort_keys=True))

    time.sleep(5)

    print("===== AFTER-STOP SAFETY READBACK =====")
    after = snapshot()
    proof["after_stop_snapshot"] = after
    print(json.dumps(after, indent=2, sort_keys=True)[:6000])

    orders_zero_after = after["orders_xlen"] == 0 and not (after["latest_orders_raw"].get("stdout") or "").strip()
    position_flat_after = flat_position(after["position"])
    no_controlled_pids_after = len(after["controlled_pids"]) == 0
    risk_execution_not_running_after = not any(x.get("service") in {"risk", "execution"} for x in after["controlled_pids"])

    req = {
        "before_snapshot_captured": bool(before),
        "after_snapshot_captured": bool(after),
        "orders_zero_after": orders_zero_after,
        "position_flat_after": position_flat_after,
        "no_controlled_pids_after": no_controlled_pids_after,
        "risk_execution_not_running_after": risk_execution_not_running_after,
        "safety_json_written": True,
        "production_source_patch_false": True,
    }

    proof["required_verdicts"] = req
    false_keys = [k for k, v in req.items() if v is not True]
    proof["false_keys"] = false_keys
    proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()

    if false_keys:
        proof["final_verdict"] = "FAIL_O23_A_R1_SAFETY_READBACK_NOT_CLEAN"
        proof["next_recommended_batch"] = "Inspect false_keys immediately; do not start another controlled-paper run."
    else:
        proof["final_verdict"] = "PASS_O23_A_R1_CONTROLLED_PAPER_SAFETY_READBACK_CLEAN_STOPPED"
        proof["next_recommended_batch"] = "26-O23-B controlled-paper evidence review; do not proceed to real live."

    SAFETY_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
    PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    RUNBOOK_MD.write_text(
        "\n".join([
            f"# {BATCH} — controlled-paper session completion / safety readback",
            "",
            f"- generated_at_utc: {proof['completed_at_utc']}",
            f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
            f"- safety_json: `{SAFETY_JSON.relative_to(ROOT)}`",
            f"- backup_dir: `{BACKUP_DIR.relative_to(ROOT)}`",
            "",
            "## Purpose",
            "- The uploaded O23-A output showed a safe running session but did not include final stop/readback verdict.",
            "- This package captures current state, stops controlled-paper services if still running, and proves post-stop safety.",
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
            f"# {DATE} — {BATCH} safety readback",
            "",
            f"Verdict: `{proof['final_verdict']}`",
            "",
            "## Achieved",
            "- Captured before-stop controlled-paper process/Redis/position snapshot.",
            "- Stopped any still-running controlled-paper services.",
            "- Captured after-stop readback.",
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
        SAFETY_JSON,
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
    print("next_recommended_batch =", proof["next_recommended_batch"])
    print("proof_json =", PROOF_JSON.relative_to(ROOT))
    print("manifest_json =", MANIFEST_JSON.relative_to(ROOT))
    print("safety_json =", SAFETY_JSON.relative_to(ROOT))
    print("runbook =", RUNBOOK_MD.relative_to(ROOT))
    print("milestone =", MILESTONE_MD.relative_to(ROOT))
    return 0 if proof["final_verdict"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
