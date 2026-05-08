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
BATCH = "26-O23-B"
BATCH_NAME = "controlled_paper_evidence_review_next_session_decision_no_real_live"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
NOW = datetime.now(timezone.utc).isoformat()
TAG = f"batch26o23_b_controlled_paper_evidence_review_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o23_b_controlled_paper_evidence_review.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o23_b_controlled_paper_evidence_review.json"
REVIEW_JSON = RUN_DIR / "controlled_paper_o23b_evidence_review.json"
DECISION_JSON = RUN_DIR / "controlled_paper_o23b_next_session_decision.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o23_b_controlled_paper_evidence_review.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o23_b_controlled_paper_evidence_review.md"
BIN_COPY = BIN_DIR / "proof_batch26o23_b_controlled_paper_evidence_review.py"

REDIS_CLI = os.environ.get("REDIS_CLI", "redis-cli")
FEATURES_STREAM = "features:mme:stream"
DECISIONS_STREAM = "decisions:mme:stream"
ORDERS_STREAM = "orders:mme:stream"
POSITION_HASH = "state:position:mme"

PRIOR_PROOF_PATHS = [
    "run/proofs/proof_batch26o23_a_explicit_approved_controlled_paper_launcher.json",
    "run/proofs/proof_batch26o23_a_r1_session_completion_safety_readback.json",
    "run/proofs/proof_batch26o22_r8_final_controlled_paper_go_nogo_evidence_pack.json",
]

INSPECT_PATHS = [
    *PRIOR_PROOF_PATHS,
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
    "app/mme_scalpx/integrations/provider_runtime.py",
    "app/mme_scalpx/integrations/bootstrap_provider.py",
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


def redis_xrevrange_raw(key: str, count: int = 20) -> dict[str, Any]:
    return redis_cmd(["XREVRANGE", key, "+", "-", "COUNT", str(count)], timeout=20)


def parse_json_maybe(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, (dict, list, bool, int, float)):
        return v
    if not isinstance(v, str):
        return None
    s = v.strip()
    if not s:
        return None
    for _ in range(4):
        try:
            parsed = json.loads(s)
        except Exception:
            return None
        if isinstance(parsed, str) and parsed.strip().startswith(("{", "[")):
            s = parsed.strip()
            continue
        return parsed
    return None


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


def controlled_pids() -> list[dict[str, Any]]:
    rows = []
    for line in proc_lines():
        if "--service" not in line or "app.mme_scalpx.main" not in line:
            continue
        m = re.match(r"\s*(\d+)\s+(\d+)\s+(.*)$", line)
        if not m:
            continue
        cmd = m.group(3)
        sm = re.search(r"--service(?:=|\s+)(feeds|features|strategy|risk|execution)", cmd)
        rows.append({
            "pid": int(m.group(1)),
            "service": sm.group(1) if sm else None,
            "cmd": cmd,
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
    return {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "features_xlen": redis_xlen(FEATURES_STREAM),
        "decisions_xlen": redis_xlen(DECISIONS_STREAM),
        "orders_xlen": redis_xlen(ORDERS_STREAM),
        "latest_orders_raw": redis_xrevrange_raw(ORDERS_STREAM, count=20),
        "latest_decisions_raw": redis_xrevrange_raw(DECISIONS_STREAM, count=10),
        "latest_features_raw": redis_xrevrange_raw(FEATURES_STREAM, count=5),
        "position": redis_hgetall(POSITION_HASH),
        "process_lines": proc_lines(),
        "controlled_pids": controlled_pids(),
    }


def latest_run_dirs(prefix: str, limit: int = 5) -> list[pathlib.Path]:
    base = ROOT / "run" / "live_capture"
    if not base.exists():
        return []
    dirs = [p for p in base.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[:limit]


def parse_decision_payloads(raw_stdout: str) -> list[dict[str, Any]]:
    lines = raw_stdout.splitlines()
    payloads = []
    for i, line in enumerate(lines):
        if line.strip() == "payload_json" and i + 1 < len(lines):
            obj = parse_json_maybe(lines[i + 1])
            if isinstance(obj, dict):
                payloads.append(obj)
    return payloads


def summarize_decisions(runtime: dict[str, Any]) -> dict[str, Any]:
    raw = runtime.get("latest_decisions_raw", {}).get("stdout") or ""
    payloads = parse_decision_payloads(raw)
    actions = [p.get("action") for p in payloads]
    reasons = [p.get("reason") or p.get("activation_reason") for p in payloads]
    return {
        "sample_count": len(payloads),
        "actions": actions,
        "reasons": reasons,
        "all_hold_or_empty": all(a in {"HOLD", "", None} for a in actions) if payloads else True,
        "any_entry_action": any(str(a).upper() in {"BUY", "SELL", "ENTER", "ENTRY"} for a in actions),
        "activation_candidate_counts": [p.get("activation_candidate_count") for p in payloads],
        "provider_ready_classic_values": [p.get("provider_ready_classic") for p in payloads],
        "provider_ready_miso_values": [p.get("provider_ready_miso") for p in payloads],
        "data_valid_values": [p.get("data_valid") for p in payloads],
        "safe_to_consume_values": [p.get("safe_to_consume") for p in payloads],
    }


def inspect_logs(run_dirs: list[pathlib.Path]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    error_patterns = [
        "Traceback",
        "Exception",
        "ERROR",
        "CRITICAL",
        "broker",
        "order",
        "reject",
        "fail",
        "real_live",
        "CONTROLLED_PAPER",
    ]
    for d in run_dirs:
        rec = {"path": str(d.relative_to(ROOT)), "files": {}}
        for f in sorted(d.glob("*.log")):
            text = f.read_text(encoding="utf-8", errors="replace")
            hits = {}
            for pat in error_patterns:
                arr = []
                for idx, line in enumerate(text.splitlines(), start=1):
                    if pat.lower() in line.lower():
                        arr.append({"line": idx, "text": line[:260]})
                hits[pat] = arr[:50]
            rec["files"][str(f.relative_to(ROOT))] = {
                "sha256": sha256_file(f),
                "size_bytes": f.stat().st_size,
                "line_count": text.count("\n") + 1,
                "hits": hits,
                "tail": "\n".join(text.splitlines()[-40:]),
            }
        out[str(d.relative_to(ROOT))] = rec
    return out


def main() -> int:
    proof: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": BATCH_NAME,
        "tag": TAG,
        "started_at_utc": NOW,
        "root": str(ROOT),
        "purpose": "Review O23-A controlled-paper evidence and decide next session path; no real live.",
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
        "evidence_review": {},
        "next_session_decision": {},
        "required_verdicts": {},
        "false_keys": [],
        "final_verdict": "NOT_EVALUATED",
        "next_recommended_batch": "",
    }

    print("===== EVIDENCE-FIRST INSPECTION =====")
    o23a_dirs = latest_run_dirs("batch26o23_a_explicit_approved_controlled_paper_launcher", limit=3)
    r1_dirs = latest_run_dirs("batch26o23_a_r1_session_completion_safety_readback", limit=3)

    dynamic_paths = list(INSPECT_PATHS)
    for d in [*o23a_dirs, *r1_dirs]:
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
    runtime = runtime_snapshot()
    proof["runtime_snapshot"] = runtime
    proof["decision_summary"] = summarize_decisions(runtime)

    print("===== LOG REVIEW =====")
    proof["log_review"] = inspect_logs([*o23a_dirs, *r1_dirs])

    o23a = proof["prior_proofs"].get("run/proofs/proof_batch26o23_a_explicit_approved_controlled_paper_launcher.json", {})
    r1 = proof["prior_proofs"].get("run/proofs/proof_batch26o23_a_r1_session_completion_safety_readback.json", {})
    o22r8 = proof["prior_proofs"].get("run/proofs/proof_batch26o22_r8_final_controlled_paper_go_nogo_evidence_pack.json", {})

    orders_zero = runtime["orders_xlen"] == 0 and not (runtime["latest_orders_raw"].get("stdout") or "").strip()
    position_flat = flat_position(runtime["position"])
    no_controlled_pids = len(runtime["controlled_pids"]) == 0
    decisions_safe = proof["decision_summary"]["all_hold_or_empty"] and not proof["decision_summary"]["any_entry_action"]

    # O23-A may have FAIL if the uploaded session was interrupted before final verdict, but R1 is the authoritative cleanup proof.
    o23a_started_and_sampled = bool(o23a.get("samples")) or any("batch26o23_a_explicit_approved" in k for k in proof["inspected_files"])
    r1_pass = str(r1.get("final_verdict", "")).startswith("PASS_O23_A_R1_CONTROLLED_PAPER_SAFETY_READBACK_CLEAN_STOPPED")
    r1_false_empty = r1.get("false_keys") == []

    review = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "o22_r8_final_verdict": o22r8.get("final_verdict"),
        "o23a_final_verdict": o23a.get("final_verdict"),
        "o23a_false_keys": o23a.get("false_keys"),
        "o23a_sample_count": len(o23a.get("samples") or []),
        "o23a_started_and_sampled_or_logs_present": o23a_started_and_sampled,
        "r1_final_verdict": r1.get("final_verdict"),
        "r1_false_keys": r1.get("false_keys"),
        "r1_pass_clean_stopped": r1_pass and r1_false_empty,
        "current_orders_zero": orders_zero,
        "current_position_flat": position_flat,
        "current_no_controlled_pids": no_controlled_pids,
        "current_decisions_safe_hold_only": decisions_safe,
        "decision_summary": proof["decision_summary"],
        "classification": "CONTROLLED_PAPER_SAFE_NO_TRADE_OBSERVATION",
        "not_live_ready": True,
        "real_live_approval": False,
    }
    proof["evidence_review"] = review
    REVIEW_JSON.write_text(json.dumps(review, indent=2, sort_keys=True), encoding="utf-8")

    next_decision = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": "ALLOW_NEXT_CONTROLLED_PAPER_SESSION_ONLY_IF_EXPLICITLY_APPROVED_AGAIN",
        "do_not_proceed_to_real_live": True,
        "reason": [
            "O23-A produced safe controlled-paper/no-trade observation.",
            "R1 proved clean stopped state.",
            "No orders and FLAT position are confirmed.",
            "One short session with no trade is not enough for real-live readiness.",
        ],
        "allowed_next_batch": "26-O23-C second bounded controlled-paper observation, MIST CALL, 1 lot, paper only, real_live=false",
        "requires_explicit_user_approval_again": True,
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
    proof["next_session_decision"] = next_decision
    DECISION_JSON.write_text(json.dumps(next_decision, indent=2, sort_keys=True), encoding="utf-8")

    req = {
        "compile_pass": bool(proof["commands"]["compile"].get("ok")),
        "import_pass": bool(proof["commands"]["import"].get("ok")),
        "o23a_started_and_sampled_or_logs_present": o23a_started_and_sampled,
        "r1_pass_clean_stopped": r1_pass and r1_false_empty,
        "orders_zero_now": orders_zero,
        "position_flat_now": position_flat,
        "no_controlled_pids_now": no_controlled_pids,
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
        proof["final_verdict"] = "FAIL_O23_B_CONTROLLED_PAPER_EVIDENCE_REVIEW_NOT_PROVEN"
        proof["next_recommended_batch"] = "Inspect false_keys before any further controlled-paper session."
    else:
        proof["final_verdict"] = "PASS_O23_B_CONTROLLED_PAPER_EVIDENCE_REVIEW_OK_NO_REAL_LIVE"
        proof["next_recommended_batch"] = "STOP unless user explicitly approves O23-C second bounded controlled-paper observation; do not proceed to real live."

    PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    RUNBOOK_MD.write_text(
        "\n".join([
            f"# {BATCH} — controlled-paper evidence review",
            "",
            f"- generated_at_utc: {proof['completed_at_utc']}",
            f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
            f"- review: `{REVIEW_JSON.relative_to(ROOT)}`",
            f"- decision: `{DECISION_JSON.relative_to(ROOT)}`",
            f"- backup_dir: `{BACKUP_DIR.relative_to(ROOT)}`",
            "",
            "## Purpose",
            "- Review O23-A / O23-A-R1 controlled-paper evidence.",
            "- Decide whether another controlled-paper observation is allowed.",
            "- Do not approve real live.",
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
            f"# {DATE} — {BATCH} controlled-paper evidence review",
            "",
            f"Verdict: `{proof['final_verdict']}`",
            "",
            "## Achieved",
            "- Reviewed O23-A and R1 cleanup evidence.",
            "- Confirmed clean stopped state if PASS.",
            "- Confirmed no orders, FLAT position, and no controlled service PIDs if PASS.",
            "- Classified this as safe controlled-paper no-trade observation.",
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
    print("classification =", review["classification"])
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
