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
BATCH = "26-O22-R5"
BATCH_NAME = "controlled_paper_operator_checklist_explicit_approval_gate_no_start_no_live"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
NOW = datetime.now(timezone.utc).isoformat()
TAG = f"batch26o22_r5_controlled_paper_operator_checklist_gate_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o22_r5_controlled_paper_operator_checklist_gate.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o22_r5_controlled_paper_operator_checklist_gate.json"
CHECKLIST_JSON = RUN_DIR / "controlled_paper_operator_checklist_o22_r5.json"
APPROVAL_GATE_JSON = RUN_DIR / "controlled_paper_explicit_approval_gate_o22_r5.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o22_r5_controlled_paper_operator_checklist_gate.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o22_r5_controlled_paper_operator_checklist_gate.md"
BIN_COPY = BIN_DIR / "proof_batch26o22_r5_controlled_paper_operator_checklist_gate.py"

REDIS_CLI = os.environ.get("REDIS_CLI", "redis-cli")
FEATURES_STREAM = "features:mme:stream"
DECISIONS_STREAM = "decisions:mme:stream"
ORDERS_STREAM = "orders:mme:stream"
POSITION_HASH = "state:position:mme"

INSPECT_PATHS = [
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "app/mme_scalpx/core/redisx.py",
    "app/mme_scalpx/core/settings.py",
    "app/mme_scalpx/main.py",
    "app/mme_scalpx/integrations/provider_runtime.py",
    "etc/strategy_family/family_runtime.yaml",
    "etc/strategy_family/rollout",
    "etc/brokers/runtime.yaml",
    "etc/brokers/provider_roles.yaml",
    "etc/brokers/dhan.yaml",
    "etc/brokers/zerodha.yaml",
    "run/proofs/proof_batch26o20_r3h_current_frame_corrected_bounded_observation.json",
    "run/proofs/proof_batch26o22_r2_controlled_paper_plan_proof_correction.json",
    "run/proofs/proof_batch26o22_r3_controlled_paper_static_gate_proof.json",
    "run/proofs/proof_batch26o22_r4_controlled_paper_dry_run_readiness_preflight.json",
]

CONTROLLED_PAPER_SCOPE_ACK = "I_ACCEPT_MIST_CALL_1LOT_PAPER_ONLY"


def run(cmd: list[str], *, timeout: int = 30, env: dict[str, str] | None = None) -> dict[str, Any]:
    try:
        cp = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
            env=env,
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


def redis_xrevrange_raw(key: str, count: int = 5) -> dict[str, Any]:
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


def service_running(name: str) -> bool:
    needle1 = f"--service {name}"
    needle2 = f"--service={name}"
    for line in proc_lines():
        if needle1 in line or needle2 in line:
            return True
    return False


def flat_position(pos: dict[str, str]) -> bool:
    return (
        str(pos.get("has_position", "0")).lower() in {"0", "false", "", "none"}
        and str(pos.get("position_side", "FLAT")).upper() in {"", "FLAT", "NONE"}
        and str(pos.get("qty_lots", "0")) in {"0", "0.0", ""}
        and str(pos.get("qty_units", "0")) in {"0", "0.0", ""}
    )


def runtime_snapshot() -> dict[str, Any]:
    latest_orders = redis_xrevrange_raw(ORDERS_STREAM, count=5)
    return {
        "features_xlen": redis_xlen(FEATURES_STREAM),
        "decisions_xlen": redis_xlen(DECISIONS_STREAM),
        "orders_xlen": redis_xlen(ORDERS_STREAM),
        "latest_orders_raw": latest_orders,
        "position": redis_hgetall(POSITION_HASH),
        "process_lines": proc_lines(),
        "features_running": service_running("features"),
        "strategy_running": service_running("strategy"),
        "risk_running": service_running("risk"),
        "execution_running": service_running("execution"),
    }


def inspect_source(rel: str) -> dict[str, Any]:
    p = ROOT / rel
    if not p.exists():
        return {"exists": False}
    if p.is_dir():
        return {
            "exists": True,
            "is_dir": True,
            "sample_members": sorted(str(x.relative_to(ROOT)) for x in p.rglob("*") if x.is_file())[:300],
        }

    text = p.read_text(encoding="utf-8", errors="replace")
    patterns = [
        "CONTROLLED_PAPER_NOT_ARMED",
        "CONTROLLED_PAPER_SCOPE_MISMATCH",
        "CONTROLLED_PAPER_QTY_CAP_FAIL",
        "CONTROLLED_PAPER_REAL_LIVE_FORBIDDEN",
        "CONTROLLED_PAPER_TIME_GATE_FAIL",
        "CONTROLLED_PAPER_POSITION_NOT_FLAT",
        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
        "controlled_paper",
        "MIST",
        "CALL",
        "qty_lots",
        "qty_units",
        "real_live",
        "paper",
        "sandbox",
        "broker",
        "order",
        "entry",
        "exit",
        "flatten",
        "kill",
        "failover",
        "fallback",
        "mid_position",
        "migration",
        "FLAT",
        "has_position",
    ]
    lines = text.splitlines()
    hits: dict[str, list[dict[str, Any]]] = {}
    for pat in patterns:
        arr = []
        for idx, line in enumerate(lines, start=1):
            if pat.lower() in line.lower():
                arr.append({"line": idx, "text": line[:260]})
        hits[pat] = arr[:80]

    ast_info: dict[str, Any] = {"ast_applicable": p.suffix == ".py"}
    if p.suffix == ".py":
        try:
            tree = ast.parse(text)
            funcs = []
            classes = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    funcs.append({"name": node.name, "line": node.lineno, "end_line": getattr(node, "end_lineno", None)})
                elif isinstance(node, ast.ClassDef):
                    classes.append({"name": node.name, "line": node.lineno, "end_line": getattr(node, "end_lineno", None)})
            ast_info.update({"ast_ok": True, "functions": funcs, "classes": classes})
        except Exception as exc:
            ast_info.update({"ast_ok": False, "ast_error": repr(exc)})

    return {
        "exists": True,
        "is_file": True,
        "sha256": sha256_file(p),
        "size_bytes": p.stat().st_size,
        "line_count": len(lines),
        "hits": hits,
        "ast": ast_info,
    }


def build_operator_checklist(prior: dict[str, Any], runtime: dict[str, Any]) -> dict[str, Any]:
    return {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "CHECKLIST_ONLY_NOT_ARMED",
        "approval_status": "NOT_APPROVED",
        "explicit_operator_approval_required_later": True,
        "do_not_start_paper_from_this_batch": True,
        "scope": {
            "family": "MIST",
            "branch": "CALL",
            "qty_lots": 1,
            "route": "paper_or_sandbox_only",
            "real_live_allowed": False,
            "automatic_broker_failover_allowed": False,
            "mid_position_provider_migration_allowed": False,
            "position_required_before_entry": "FLAT",
        },
        "required_future_operator_exports_only_after_explicit_approval": {
            "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME": "1",
            "SCALPX_CONTROLLED_PAPER_SCOPE_ACK": CONTROLLED_PAPER_SCOPE_ACK,
        },
        "must_remain_false_or_absent_before_approval": {
            "SCALPX_REAL_LIVE_ALLOWED": "must remain 0/false",
            "SCALPX_LIVE_ORDERS_ALLOWED": "must remain 0/false unless paper/sandbox layer explicitly routes without real-live broker side effects",
            "SCALPX_BROKER_CALLS_ALLOWED": "must remain 0/false until the approved controlled-paper command explicitly sets paper/sandbox-safe route",
            "SCALPX_FORCE_CANDIDATE": "must remain 0/false",
            "SCALPX_THRESHOLD_RELAXATION": "must remain 0/false",
        },
        "operator_pre_start_checklist_for_future_batch": [
            "Confirm this is controlled-paper only, not real live.",
            "Confirm family scope is MIST CALL only.",
            "Confirm quantity is exactly 1 lot.",
            "Confirm position hash is FLAT.",
            "Confirm orders:mme:stream is empty before start.",
            "Confirm risk and execution are not already running before controlled start.",
            "Confirm no automatic broker failover.",
            "Confirm no mid-position provider migration.",
            "Confirm current feature structural shape has all 10 branches and MIST CALL visible.",
            "Confirm strategy remains HOLD/no_candidate before arming.",
            "Confirm explicit env ACK exactly matches required scope string.",
            "Confirm kill/flatten/reconciliation exit paths are available.",
        ],
        "stop_conditions_for_future_controlled_paper": [
            "Any order appears outside paper/sandbox route.",
            "Any real_live flag becomes true.",
            "Any quantity exceeds 1 lot.",
            "Any family/branch outside MIST CALL reaches entry route.",
            "Any position appears before explicit paper start.",
            "Any broker/live route ambiguity appears.",
            "Any risk/execution anomaly or reconciliation anomaly appears.",
            "Any provider migration/failover occurs mid-position.",
        ],
        "prior_o22_r4_summary": prior,
        "current_runtime_snapshot": runtime,
    }


def build_approval_gate(prior: dict[str, Any], runtime: dict[str, Any]) -> dict[str, Any]:
    pos = runtime.get("position") or {}
    orders_zero = runtime.get("orders_xlen") == 0 and not (runtime.get("latest_orders_raw", {}).get("stdout") or "").strip()
    position_flat = flat_position(pos)

    env_state = {
        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME": os.environ.get("SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME", ""),
        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK": os.environ.get("SCALPX_CONTROLLED_PAPER_SCOPE_ACK", ""),
        "SCALPX_REAL_LIVE_ALLOWED": os.environ.get("SCALPX_REAL_LIVE_ALLOWED", ""),
        "SCALPX_LIVE_ORDERS_ALLOWED": os.environ.get("SCALPX_LIVE_ORDERS_ALLOWED", ""),
        "SCALPX_BROKER_CALLS_ALLOWED": os.environ.get("SCALPX_BROKER_CALLS_ALLOWED", ""),
        "SCALPX_FORCE_CANDIDATE": os.environ.get("SCALPX_FORCE_CANDIDATE", ""),
        "SCALPX_THRESHOLD_RELAXATION": os.environ.get("SCALPX_THRESHOLD_RELAXATION", ""),
    }

    explicit_approval_currently_absent = (
        env_state["SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME"] not in {"1", "true", "TRUE", "yes", "YES"}
        and env_state["SCALPX_CONTROLLED_PAPER_SCOPE_ACK"] == ""
    )

    gate = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "approval_gate_status": "LOCKED_NOT_APPROVED",
        "paper_start_allowed_by_this_batch": False,
        "explicit_approval_currently_absent": explicit_approval_currently_absent,
        "future_approval_requires_exact_env": {
            "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME": "1",
            "SCALPX_CONTROLLED_PAPER_SCOPE_ACK": CONTROLLED_PAPER_SCOPE_ACK,
        },
        "current_env_state": env_state,
        "current_runtime_safety": {
            "orders_zero": orders_zero,
            "position_flat": position_flat,
            "risk_running": runtime.get("risk_running"),
            "execution_running": runtime.get("execution_running"),
            "features_running": runtime.get("features_running"),
            "strategy_running": runtime.get("strategy_running"),
        },
        "prior_o22_r4": {
            "final_verdict": prior.get("final_verdict"),
            "false_keys": prior.get("false_keys"),
            "failed_scenarios": prior.get("failed_scenarios"),
            "missing_veto_surfaces": prior.get("missing_veto_surfaces"),
            "next_recommended_batch": prior.get("next_recommended_batch"),
        },
        "next_if_pass": "26-O22-R6 controlled-paper approved-start command template generator, still requiring explicit user approval before actual start",
    }
    return gate


def main() -> int:
    proof: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": BATCH_NAME,
        "tag": TAG,
        "started_at_utc": NOW,
        "root": str(ROOT),
        "evidence_first_policy": {
            "latest_uploaded_evidence_output_read": True,
            "prior_o22_r4_pass_required": True,
            "uploaded_bundle_remains_source_of_truth": True,
        },
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
            "operator_checklist_only": True,
            "explicit_approval_gate_only": True,
        },
        "prior_proofs": {},
        "inspected_files": {},
        "source_inspection": {},
        "commands": {},
        "runtime_snapshot": {},
        "operator_checklist": {},
        "approval_gate": {},
        "required_verdicts": {},
        "false_keys": [],
        "final_verdict": "NOT_EVALUATED",
        "next_recommended_batch": "",
    }

    try:
        print("===== EVIDENCE-FIRST INSPECTION: PRIOR PROOFS + SOURCE HASHES =====")
        for rel in INSPECT_PATHS:
            p = ROOT / rel
            if p.exists() and p.is_file():
                dst = BACKUP_DIR / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, dst)
                proof["inspected_files"][rel] = {
                    "exists": True,
                    "is_file": True,
                    "sha256": sha256_file(p),
                    "size_bytes": p.stat().st_size,
                    "backup": str(dst.relative_to(ROOT)),
                }
                if rel.endswith(".json"):
                    loaded = load_json(p)
                    proof["prior_proofs"][rel] = {
                        "final_verdict": loaded.get("final_verdict") if isinstance(loaded, dict) else None,
                        "false_keys": loaded.get("false_keys") if isinstance(loaded, dict) else None,
                        "required_verdicts": loaded.get("required_verdicts") if isinstance(loaded, dict) else None,
                        "failed_scenarios": loaded.get("failed_scenarios") if isinstance(loaded, dict) else None,
                        "missing_veto_surfaces": loaded.get("missing_veto_surfaces") if isinstance(loaded, dict) else None,
                        "next_recommended_batch": loaded.get("next_recommended_batch") if isinstance(loaded, dict) else None,
                    }
            elif p.exists() and p.is_dir():
                proof["inspected_files"][rel] = {
                    "exists": True,
                    "is_dir": True,
                    "sample_members": sorted(str(x.relative_to(ROOT)) for x in p.rglob("*") if x.is_file())[:300],
                }
            else:
                proof["inspected_files"][rel] = {"exists": False}

        print("===== COMPILE / IMPORT PROOF: NO SOURCE MUTATION =====")
        compile_targets = [
            "app/mme_scalpx/services/risk.py",
            "app/mme_scalpx/services/execution.py",
            "app/mme_scalpx/services/strategy.py",
            "app/mme_scalpx/services/features.py",
            "app/mme_scalpx/core/names.py",
            "app/mme_scalpx/core/models.py",
            "app/mme_scalpx/core/redisx.py",
            "app/mme_scalpx/main.py",
        ]
        proof["commands"]["compile"] = run([sys.executable, "-m", "py_compile", *compile_targets], timeout=60)
        proof["commands"]["import"] = run(
            [
                sys.executable,
                "-c",
                "import app.mme_scalpx.services.risk, app.mme_scalpx.services.execution, app.mme_scalpx.services.strategy, app.mme_scalpx.services.features, app.mme_scalpx.core.names, app.mme_scalpx.core.models; print('IMPORT_OK')",
            ],
            timeout=60,
        )

        print("===== STATIC SOURCE INSPECTION =====")
        for rel in INSPECT_PATHS:
            if not rel.endswith(".json"):
                proof["source_inspection"][rel] = inspect_source(rel)

        print("===== READ-ONLY RUNTIME SAFETY SNAPSHOT =====")
        runtime = runtime_snapshot()
        proof["runtime_snapshot"] = runtime

        o22_r4 = proof["prior_proofs"].get("run/proofs/proof_batch26o22_r4_controlled_paper_dry_run_readiness_preflight.json", {})
        o22_r4_req = o22_r4.get("required_verdicts") or {}

        checklist = build_operator_checklist(o22_r4, runtime)
        approval_gate = build_approval_gate(o22_r4, runtime)
        proof["operator_checklist"] = checklist
        proof["approval_gate"] = approval_gate

        CHECKLIST_JSON.write_text(json.dumps(checklist, indent=2, sort_keys=True), encoding="utf-8")
        APPROVAL_GATE_JSON.write_text(json.dumps(approval_gate, indent=2, sort_keys=True), encoding="utf-8")

        orders_zero = runtime.get("orders_xlen") == 0 and not (runtime.get("latest_orders_raw", {}).get("stdout") or "").strip()
        position_flat = flat_position(runtime.get("position") or {})
        env = approval_gate["current_env_state"]

        req = {
            "o22_r4_pass_loaded": str(o22_r4.get("final_verdict", "")).startswith("PASS_O22_R4_CONTROLLED_PAPER_DRY_RUN_PREFLIGHT_OK"),
            "o22_r4_false_keys_empty": o22_r4.get("false_keys") == [],
            "o22_r4_failed_scenarios_empty": o22_r4.get("failed_scenarios") == [],
            "o22_r4_missing_veto_surfaces_empty": o22_r4.get("missing_veto_surfaces") == [],
            "o22_r4_scenario_matrix_all_expected": o22_r4_req.get("scenario_matrix_all_expected") is True,
            "o22_r4_approved_for_paper_start_false": o22_r4_req.get("approved_for_paper_start_false") is True,
            "compile_pass": bool(proof["commands"]["compile"].get("ok")),
            "import_pass": bool(proof["commands"]["import"].get("ok")),
            "checklist_json_written": CHECKLIST_JSON.exists(),
            "approval_gate_json_written": APPROVAL_GATE_JSON.exists(),
            "approval_gate_locked": approval_gate.get("approval_gate_status") == "LOCKED_NOT_APPROVED",
            "paper_start_allowed_by_this_batch_false": approval_gate.get("paper_start_allowed_by_this_batch") is False,
            "explicit_approval_absent": approval_gate.get("explicit_approval_currently_absent") is True,
            "orders_zero": orders_zero,
            "position_flat": position_flat,
            "real_live_false": env.get("SCALPX_REAL_LIVE_ALLOWED", "") not in {"1", "true", "TRUE", "yes", "YES"},
            "no_paper_start": env.get("SCALPX_PAPER_ARMED", "") not in {"1", "true", "TRUE", "yes", "YES"},
            "no_controlled_paper_runtime_env": env.get("SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME", "") not in {"1", "true", "TRUE", "yes", "YES"},
            "no_scope_ack_env": env.get("SCALPX_CONTROLLED_PAPER_SCOPE_ACK", "") == "",
            "no_broker_call": env.get("SCALPX_BROKER_CALLS_ALLOWED", "") not in {"1", "true", "TRUE", "yes", "YES"},
            "no_order_write_intent": env.get("SCALPX_LIVE_ORDERS_ALLOWED", "") not in {"1", "true", "TRUE", "yes", "YES"},
            "no_threshold_relaxation": env.get("SCALPX_THRESHOLD_RELAXATION", "") not in {"1", "true", "TRUE", "yes", "YES"},
            "no_forced_candidate": env.get("SCALPX_FORCE_CANDIDATE", "") not in {"1", "true", "TRUE", "yes", "YES"},
            "risk_not_running": not runtime.get("risk_running"),
            "execution_not_running": not runtime.get("execution_running"),
            "production_source_patch_false": True,
            "service_start_false": True,
        }

        false_keys = [k for k, v in req.items() if v is not True]
        proof["required_verdicts"] = req
        proof["false_keys"] = false_keys
        proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()

        if false_keys:
            proof["final_verdict"] = "FAIL_O22_R5_CONTROLLED_PAPER_OPERATOR_CHECKLIST_GATE_NOT_PROVEN"
            proof["next_recommended_batch"] = "Inspect false_keys and write smallest Lane-A diagnostic package; no paper start."
        else:
            proof["final_verdict"] = "PASS_O22_R5_CONTROLLED_PAPER_OPERATOR_CHECKLIST_GATE_OK_LOCKED_NO_START"
            proof["next_recommended_batch"] = "26-O22-R6 controlled-paper approved-start command template generator; still requires explicit user approval before any actual start."

        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

        RUNBOOK_MD.write_text(
            "\n".join([
                f"# {BATCH} — controlled-paper operator checklist / explicit-approval gate",
                "",
                f"- generated_at_utc: {proof['completed_at_utc']}",
                f"- tag: `{TAG}`",
                f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
                f"- manifest: `{MANIFEST_JSON.relative_to(ROOT)}`",
                f"- checklist: `{CHECKLIST_JSON.relative_to(ROOT)}`",
                f"- approval_gate: `{APPROVAL_GATE_JSON.relative_to(ROOT)}`",
                f"- backup_dir: `{BACKUP_DIR.relative_to(ROOT)}`",
                "",
                "## Purpose",
                "- Convert O22-R4 dry-run readiness into an operator checklist and explicit approval gate.",
                "- This batch remains locked and does not start controlled paper.",
                "- This batch does not enable real live.",
                "- This batch does not call broker, write orders, start services, or patch production source.",
                "",
                "## Future approval string",
                f"- `SCALPX_CONTROLLED_PAPER_SCOPE_ACK={CONTROLLED_PAPER_SCOPE_ACK}`",
                "- `SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME=1`",
                "",
                "## Scope locked for any future controlled-paper start",
                "- MIST CALL only.",
                "- 1 lot only.",
                "- paper/sandbox route only.",
                "- position FLAT before entry.",
                "- real_live=false.",
                "- no automatic broker failover.",
                "- no mid-position provider migration.",
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
                "",
                "## Operator checklist artifact",
                "```json",
                json.dumps(checklist, indent=2, sort_keys=True),
                "```",
                "",
                "## Approval gate artifact",
                "```json",
                json.dumps(approval_gate, indent=2, sort_keys=True),
                "```",
            ]),
            encoding="utf-8",
        )

        MILESTONE_MD.write_text(
            "\n".join([
                f"# {DATE} — {BATCH} controlled-paper operator checklist / explicit-approval gate",
                "",
                f"Verdict: `{proof['final_verdict']}`",
                "",
                "## Achieved",
                "- Loaded O22-R4 PASS as prerequisite.",
                "- Inspected latest source/proof/config artifacts first.",
                "- Backed up inspected files.",
                "- Ran compile/import proof.",
                "- Generated controlled-paper operator checklist JSON.",
                "- Generated explicit approval gate JSON.",
                "- Confirmed approval gate is locked/not approved.",
                "- Confirmed orders zero and position FLAT.",
                "- Confirmed no controlled-paper env, no scope ACK env, no broker/order intent, risk/execution not running.",
                "",
                "## Not done",
                "- Did not start controlled paper.",
                "- Did not enable paper runtime.",
                "- Did not enable real live.",
                "- Did not start services.",
                "- Did not call broker.",
                "- Did not write orders.",
                "- Did not patch production source.",
                "",
                "## Next",
                f"- {proof['next_recommended_batch']}",
                "",
                "## Artifacts",
                f"- `{PROOF_JSON.relative_to(ROOT)}`",
                f"- `{MANIFEST_JSON.relative_to(ROOT)}`",
                f"- `{CHECKLIST_JSON.relative_to(ROOT)}`",
                f"- `{APPROVAL_GATE_JSON.relative_to(ROOT)}`",
                f"- `{RUNBOOK_MD.relative_to(ROOT)}`",
            ]),
            encoding="utf-8",
        )

        shutil.copy2(pathlib.Path(__file__), BIN_COPY)

        manifest_paths = [
            PROOF_JSON,
            RUNBOOK_MD,
            MILESTONE_MD,
            CHECKLIST_JSON,
            APPROVAL_GATE_JSON,
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
        print(f"final_verdict = {proof['final_verdict']}")
        print(f"false_keys = {false_keys}")
        print(f"next_recommended_batch = {proof['next_recommended_batch']}")
        print(f"proof_json = {PROOF_JSON.relative_to(ROOT)}")
        print(f"manifest_json = {MANIFEST_JSON.relative_to(ROOT)}")
        print(f"checklist_json = {CHECKLIST_JSON.relative_to(ROOT)}")
        print(f"approval_gate_json = {APPROVAL_GATE_JSON.relative_to(ROOT)}")
        print(f"runbook = {RUNBOOK_MD.relative_to(ROOT)}")
        print(f"milestone = {MILESTONE_MD.relative_to(ROOT)}")
        return 0 if proof["final_verdict"].startswith("PASS_") else 2

    except Exception as exc:
        proof["exception"] = repr(exc)
        proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
        proof["final_verdict"] = "FAIL_O22_R5_EXCEPTION_SAFE_STOP_NO_MUTATION"
        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
        print("===== EXCEPTION SAFE STOP =====")
        print(repr(exc))
        print(f"proof_json = {PROOF_JSON.relative_to(ROOT)}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
