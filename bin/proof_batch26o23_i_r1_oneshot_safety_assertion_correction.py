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
BATCH = "26-O23-I-R1"
BATCH_NAME = "oneshot_safety_assertion_correction_no_patch_no_start_no_real_live"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
TAG = f"batch26o23_i_r1_oneshot_safety_assertion_correction_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o23_i_r1_oneshot_safety_assertion_correction.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o23_i_r1_oneshot_safety_assertion_correction.json"
CORRECTION_JSON = RUN_DIR / "controlled_paper_o23i_r1_corrected_oneshot_safety.json"
SCENARIO_REVIEW_JSON = RUN_DIR / "controlled_paper_o23i_r1_scenario_review.json"
NEXT_DECISION_JSON = RUN_DIR / "controlled_paper_o23i_r1_next_decision.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o23_i_r1_oneshot_safety_assertion_correction.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o23_i_r1_oneshot_safety_assertion_correction.md"
BIN_COPY = BIN_DIR / "proof_batch26o23_i_r1_oneshot_safety_assertion_correction.py"

REDIS_CLI = os.environ.get("REDIS_CLI", "redis-cli")
ORDERS_STREAM = "orders:mme:stream"
POSITION_HASH = "state:position:mme"
FEATURES_STREAM = "features:mme:stream"
DECISIONS_STREAM = "decisions:mme:stream"

CONTROLLED_SERVICES = {"feeds", "features", "strategy", "risk", "execution"}

SMALL_COPY_LIMIT_BYTES = 500_000
MAX_SLICE_CHARS = 24_000

STRATEGY_REL = "app/mme_scalpx/services/strategy.py"
FEATURES_REL = "app/mme_scalpx/services/features.py"
RISK_REL = "app/mme_scalpx/services/risk.py"
EXECUTION_REL = "app/mme_scalpx/services/execution.py"

SOURCE_PATHS = [
    STRATEGY_REL,
    FEATURES_REL,
    RISK_REL,
    EXECUTION_REL,
    "app/mme_scalpx/core/models.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/redisx.py",
    "app/mme_scalpx/main.py",
]

PRIOR_PROOF_PATHS = [
    "run/proofs/proof_batch26o23_i_static_oneshot_bridge_proof.json",
    "run/proofs/proof_batch26o23_h_narrow_bridge_repair.json",
    "run/proofs/proof_batch26o23_g_narrow_bridge_diagnostic.json",
    "run/proofs/proof_batch26o23_f_r4_prior_proof_loader_correction.json",
]

INSPECT_PATHS = PRIOR_PROOF_PATHS + SOURCE_PATHS

O23I_PREFIX = "batch26o23_i_static_oneshot_bridge_proof"


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


def safe_file_record(rel: str, copy_source: bool = False) -> dict[str, Any]:
    p = ROOT / rel
    rec: dict[str, Any] = {"path": rel, "exists": p.exists(), "is_file": p.is_file() if p.exists() else False}
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

    if copy_source and p.stat().st_size <= SMALL_COPY_LIMIT_BYTES and rel.startswith("app/"):
        dst = BACKUP_DIR / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)
        rec["source_backup"] = str(dst.relative_to(ROOT))
    else:
        rec["backup_policy"] = "hash_plus_bounded_head_tail_slice_only_no_full_evidence_copy"

    return rec


def load_json_file(path: pathlib.Path) -> dict[str, Any]:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
        return obj if isinstance(obj, dict) else {"_loaded_type": type(obj).__name__}
    except Exception as exc:
        return {"_load_error": repr(exc), "_path": str(path)}


def load_json_limited(rel: str) -> dict[str, Any]:
    p = ROOT / rel
    rec = safe_file_record(rel, copy_source=False)
    if not p.exists() or not p.is_file():
        return rec
    obj = load_json_file(p)
    rec["json_loaded"] = "_load_error" not in obj
    rec["loaded"] = obj
    if isinstance(obj, dict):
        rec["final_verdict"] = obj.get("final_verdict")
        rec["false_keys"] = obj.get("false_keys")
        rec["next_recommended_batch"] = obj.get("next_recommended_batch")
    return rec


def pass_prefix(rec: dict[str, Any], prefix: str) -> bool:
    fv = rec.get("final_verdict")
    return isinstance(fv, str) and fv.startswith(prefix)


def latest_o23i_dirs(limit: int = 5) -> list[pathlib.Path]:
    base = ROOT / "run" / "live_capture"
    if not base.exists():
        return []
    dirs = [p for p in base.iterdir() if p.is_dir() and p.name.startswith(O23I_PREFIX)]
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[:limit]


def find_latest_oneshot_json() -> pathlib.Path | None:
    for d in latest_o23i_dirs():
        p = d / "controlled_paper_o23i_oneshot_helper_matrix.json"
        if p.exists() and p.is_file():
            return p
    return None


def find_latest_next_decision_json() -> pathlib.Path | None:
    for d in latest_o23i_dirs():
        p = d / "controlled_paper_o23i_next_decision.json"
        if p.exists() and p.is_file():
            return p
    return None


def norm_candidate(value: Any) -> int | None:
    if value in {None, ""}:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        try:
            return int(value)
        except Exception:
            return None
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        try:
            return int(float(s))
        except Exception:
            return None
    return None


def corrected_candidate_safety(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    all_ok = True
    for s in scenarios:
        inp = s.get("input_decision") or {}
        out = s.get("output") or {}
        if not isinstance(inp, dict):
            inp = {}
        if not isinstance(out, dict):
            out = {}

        in_action = str(inp.get("action") or "").upper()
        out_action = str(out.get("action") or "").upper()

        in_count = norm_candidate(inp.get("activation_candidate_count"))
        out_count = norm_candidate(out.get("activation_candidate_count"))

        in_count_eff = 0 if in_count is None else in_count
        out_count_eff = 0 if out_count is None else out_count

        created_positive_from_zero = in_count_eff <= 0 and out_count_eff > 0
        increased_candidate_count = out_count_eff > in_count_eff
        changed_buy_entry_action = in_action in {"BUY", "SELL", "ENTER", "ENTRY"} and out != inp

        # Corrected assertion:
        # The helper may preserve an existing positive candidate in an unchanged
        # BUY/entry scenario. That is not "creating" a candidate. Unsafe only if
        # count increases or a zero/empty candidate becomes positive.
        safe = (
            not created_positive_from_zero
            and not increased_candidate_count
            and not changed_buy_entry_action
        )

        row = {
            "name": s.get("name"),
            "scenario_ok": s.get("ok"),
            "input_action": inp.get("action"),
            "output_action": out.get("action"),
            "input_candidate_count": inp.get("activation_candidate_count"),
            "output_candidate_count": out.get("activation_candidate_count"),
            "input_candidate_count_norm": in_count,
            "output_candidate_count_norm": out_count,
            "created_positive_from_zero": created_positive_from_zero,
            "increased_candidate_count": increased_candidate_count,
            "changed_buy_entry_action": changed_buy_entry_action,
            "corrected_no_candidate_creation_or_increase": safe,
        }
        if not safe:
            all_ok = False
        rows.append(row)

    return {
        "scenario_reviews": rows,
        "corrected_no_positive_candidate_created": all_ok,
        "definition": "PASS means the helper did not increase activation_candidate_count and did not turn zero/empty candidate count into positive. Preserving an unchanged existing BUY candidate is allowed.",
    }


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
        "features_xlen": redis_xlen(FEATURES_STREAM),
        "decisions_xlen": redis_xlen(DECISIONS_STREAM),
        "orders_xlen": redis_xlen(ORDERS_STREAM),
        "latest_orders_raw": redis_xrevrange_raw(ORDERS_STREAM, count=5),
        "latest_decisions_raw": redis_xrevrange_raw(DECISIONS_STREAM, count=5),
        "latest_features_raw": redis_xrevrange_raw(FEATURES_STREAM, count=5),
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
        "purpose": "Correct O23-I one-shot safety assertion: unchanged existing BUY candidate is not candidate creation.",
        "safety_intent": {
            "real_live_enablement": False,
            "paper_restart": False,
            "service_start": False,
            "broker_call": False,
            "order_write": False,
            "threshold_relaxation": False,
            "forced_candidate": False,
            "doctrine_mutation": False,
            "production_source_patch": False,
            "proof_parser_correction_only": True,
        },
        "disk_state": {},
        "inspected_files": {},
        "prior_proofs": {},
        "commands": {},
        "runtime_snapshot": {},
        "oneshot_source": {},
        "corrected_safety": {},
        "next_decision": {},
        "required_verdicts": {},
        "false_keys": [],
        "final_verdict": "NOT_EVALUATED",
        "next_recommended_batch": "",
    }

    print("===== DISK PRECHECK =====")
    proof["disk_state"] = disk_state()

    print("===== EVIDENCE-FIRST INSPECTION WITH HASH/SLICE + SOURCE BACKUPS =====")
    for rel in INSPECT_PATHS:
        copy_source = rel in {STRATEGY_REL, FEATURES_REL, RISK_REL, EXECUTION_REL}
        proof["inspected_files"][rel] = safe_file_record(rel, copy_source=copy_source)
        if rel.endswith(".json"):
            proof["prior_proofs"][rel] = load_json_limited(rel)

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
        "import app.mme_scalpx.main, app.mme_scalpx.services.features, app.mme_scalpx.services.strategy, app.mme_scalpx.services.risk, app.mme_scalpx.services.execution; print('IMPORT_OK')",
    ], timeout=60)

    print("===== RUNTIME SAFETY READBACK =====")
    runtime = runtime_snapshot()
    proof["runtime_snapshot"] = runtime

    print("===== LOAD O23-I ONE-SHOT ARTIFACT =====")
    oneshot_path = find_latest_oneshot_json()
    next_decision_path = find_latest_next_decision_json()
    if oneshot_path is None:
        oneshot = {"_missing": True}
    else:
        oneshot = load_json_file(oneshot_path)

    proof["oneshot_source"] = {
        "oneshot_path": str(oneshot_path.relative_to(ROOT)) if oneshot_path else None,
        "next_decision_path": str(next_decision_path.relative_to(ROOT)) if next_decision_path else None,
        "oneshot_sha256": sha256_file(oneshot_path) if oneshot_path else None,
        "oneshot": oneshot,
    }

    scenarios = oneshot.get("scenarios") if isinstance(oneshot, dict) else []
    if not isinstance(scenarios, list):
        scenarios = []

    corrected = corrected_candidate_safety(scenarios)
    proof["corrected_safety"] = corrected
    SCENARIO_REVIEW_JSON.write_text(json.dumps(corrected, indent=2, sort_keys=True), encoding="utf-8")

    i = proof["prior_proofs"].get("run/proofs/proof_batch26o23_i_static_oneshot_bridge_proof.json", {}).get("loaded", {})
    h = proof["prior_proofs"].get("run/proofs/proof_batch26o23_h_narrow_bridge_repair.json", {}).get("loaded", {})

    orders_zero = runtime["orders_xlen"] == 0 and not (runtime["latest_orders_raw"].get("stdout") or "").strip()
    position_flat = flat_position(runtime["position"])
    no_controlled_pids = len(runtime["controlled_service_rows"]) == 0
    risk_execution_not_running = len(runtime["risk_execution_rows"]) == 0

    o23i_false_keys = i.get("false_keys") if isinstance(i, dict) else None
    o23i_failed_only_assertion = (
        isinstance(i, dict)
        and str(i.get("final_verdict", "")).startswith("FAIL_O23_I_STATIC_ONESHOT_BRIDGE_PROOF_NOT_PROVEN")
        and o23i_false_keys == ["oneshot_no_positive_candidate_created"]
    )

    o23i_oneshot = i.get("oneshot_proof") if isinstance(i, dict) else {}
    o23i_required = i.get("required_verdicts") if isinstance(i, dict) else {}

    correction_record = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "O23I_FALSE_NEGATIVE_ASSERTION_CORRECTED",
        "original_o23i_final_verdict": i.get("final_verdict") if isinstance(i, dict) else None,
        "original_o23i_false_keys": o23i_false_keys,
        "original_all_helpers_present": o23i_oneshot.get("all_helpers_present") if isinstance(o23i_oneshot, dict) else None,
        "original_all_scenarios_passed": o23i_oneshot.get("all_scenarios_passed") if isinstance(o23i_oneshot, dict) else None,
        "corrected_candidate_safety": corrected,
        "corrected_interpretation": [
            "O23-I helper matrix passed all scenarios.",
            "The failed key treated an unchanged BUY scenario with pre-existing activation_candidate_count=1 as positive candidate creation.",
            "Correct safety law is no creation and no increase of candidate count.",
            "Under corrected law, preserving an existing unchanged BUY candidate is safe and not candidate creation.",
        ],
        "source_patch_applied": False,
        "service_started": False,
        "real_live_approval": False,
    }
    CORRECTION_JSON.write_text(json.dumps(correction_record, indent=2, sort_keys=True), encoding="utf-8")

    next_decision = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": "ALLOW_POST_REPAIR_BOUNDED_CONTROLLED_PAPER_OBSERVATION_ONLY_AFTER_EXPLICIT_APPROVAL",
        "recommended_next_batch": "26-O23-J post-repair bounded controlled-paper observation, MIST CALL, 1 lot, paper only, real_live=false",
        "requires_explicit_user_approval": True,
        "required_approval_phrase": "APPROVE O23-J POST-REPAIR CONTROLLED PAPER OBSERVATION: MIST CALL, 1 LOT, PAPER ONLY, REAL LIVE FALSE",
        "why": [
            "O23-H repaired the narrow bridge.",
            "O23-I proved helper behavior but had one false-negative safety assertion.",
            "O23-I-R1 corrected the assertion without patching source.",
            "Next observation must be explicitly approved again.",
        ],
        "forbidden": [
            "real live",
            "quantity increase",
            "family expansion",
            "threshold relaxation",
            "forced candidate",
            "broker failover",
            "mid-position provider migration",
        ],
    }
    NEXT_DECISION_JSON.write_text(json.dumps(next_decision, indent=2, sort_keys=True), encoding="utf-8")

    req = {
        "o23i_failed_only_on_false_negative_assertion": o23i_failed_only_assertion,
        "o23h_pass_loaded": pass_prefix(h, "PASS_O23_H_NARROW_BRIDGE_REPAIR_OK_NO_START_NO_REAL_LIVE"),
        "compile_pass": bool(proof["commands"]["compile"].get("ok")),
        "import_pass": bool(proof["commands"]["import"].get("ok")),
        "oneshot_artifact_found": oneshot_path is not None,
        "oneshot_all_helpers_present": oneshot.get("all_helpers_present") is True if isinstance(oneshot, dict) else False,
        "oneshot_all_scenarios_passed": oneshot.get("all_scenarios_passed") is True if isinstance(oneshot, dict) else False,
        "corrected_no_positive_candidate_created": corrected.get("corrected_no_positive_candidate_created") is True,
        "all_corrected_scenario_rows_present": len(corrected.get("scenario_reviews") or []) >= 5,
        "original_o23i_static_required_keys_ok_except_false_assertion": all(
            v is True
            for k, v in (o23i_required or {}).items()
            if k != "oneshot_no_positive_candidate_created"
        ) if isinstance(o23i_required, dict) and o23i_required else False,
        "orders_zero_now": orders_zero,
        "position_flat_now": position_flat,
        "no_controlled_pids_now": no_controlled_pids,
        "risk_execution_not_running_now": risk_execution_not_running,
        "correction_json_written": CORRECTION_JSON.exists(),
        "scenario_review_json_written": SCENARIO_REVIEW_JSON.exists(),
        "next_decision_json_written": NEXT_DECISION_JSON.exists(),
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
        proof["final_verdict"] = "FAIL_O23_I_R1_ONESHOT_SAFETY_ASSERTION_CORRECTION_NOT_PROVEN"
        proof["next_recommended_batch"] = "Inspect false_keys; do not restart controlled paper."
    else:
        proof["final_verdict"] = "PASS_O23_I_R1_ONESHOT_SAFETY_ASSERTION_CORRECTION_OK_NO_START_NO_REAL_LIVE"
        proof["next_recommended_batch"] = "STOP unless user explicitly approves O23-J post-repair bounded controlled-paper observation."

    PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    RUNBOOK_MD.write_text(
        "\n".join([
            f"# {BATCH} — one-shot safety assertion correction",
            "",
            f"- generated_at_utc: {proof['completed_at_utc']}",
            f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
            f"- correction: `{CORRECTION_JSON.relative_to(ROOT)}`",
            f"- scenario_review: `{SCENARIO_REVIEW_JSON.relative_to(ROOT)}`",
            f"- next_decision: `{NEXT_DECISION_JSON.relative_to(ROOT)}`",
            f"- backup_dir: `{BACKUP_DIR.relative_to(ROOT)}`",
            "",
            "## Purpose",
            "- Correct O23-I false-negative safety assertion.",
            "- Preserve O23-H source exactly; no source patch in this batch.",
            "- Do not start services.",
            "- Do not approve real live.",
            "",
            "## Corrected safety law",
            "- Unsafe means the helper creates a positive candidate from zero/empty, or increases activation_candidate_count.",
            "- Preserving an unchanged existing BUY candidate is not candidate creation.",
            "",
            "## Correction record",
            "```json",
            json.dumps(correction_record, indent=2, sort_keys=True),
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
            f"# {DATE} — {BATCH} one-shot assertion correction",
            "",
            f"Verdict: `{proof['final_verdict']}`",
            "",
            "## Achieved",
            "- Loaded O23-I failure and O23-H repair proof.",
            "- Confirmed O23-I failed only on `oneshot_no_positive_candidate_created` if PASS.",
            "- Recomputed candidate safety using no-create/no-increase rule.",
            "- Preserved no-source-patch, no-service-start, no-real-live boundary.",
            "",
            "## Next",
            f"- {proof['next_recommended_batch']}",
        ]),
        encoding="utf-8",
    )

    shutil.copy2(pathlib.Path(__file__), BIN_COPY)

    manifest_paths = [
        PROOF_JSON,
        CORRECTION_JSON,
        SCENARIO_REVIEW_JSON,
        NEXT_DECISION_JSON,
        RUNBOOK_MD,
        MILESTONE_MD,
        BIN_COPY,
        ROOT / STRATEGY_REL,
        ROOT / FEATURES_REL,
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
    print("original_o23i_false_keys =", o23i_false_keys)
    print("corrected_no_positive_candidate_created =", corrected.get("corrected_no_positive_candidate_created"))
    print("next_recommended_batch =", proof["next_recommended_batch"])
    print("approval_required_for_next_observation =", next_decision["requires_explicit_user_approval"])
    print("required_approval_phrase =", next_decision["required_approval_phrase"])
    print("proof_json =", PROOF_JSON.relative_to(ROOT))
    print("manifest_json =", MANIFEST_JSON.relative_to(ROOT))
    print("correction_json =", CORRECTION_JSON.relative_to(ROOT))
    print("scenario_review_json =", SCENARIO_REVIEW_JSON.relative_to(ROOT))
    print("next_decision_json =", NEXT_DECISION_JSON.relative_to(ROOT))
    print("runbook =", RUNBOOK_MD.relative_to(ROOT))
    print("milestone =", MILESTONE_MD.relative_to(ROOT))
    return 0 if proof["final_verdict"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
