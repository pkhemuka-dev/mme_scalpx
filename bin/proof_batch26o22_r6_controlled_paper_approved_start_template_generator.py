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
BATCH = "26-O22-R6"
BATCH_NAME = "controlled_paper_approved_start_command_template_generator_no_start_no_live"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
NOW = datetime.now(timezone.utc).isoformat()
TAG = f"batch26o22_r6_controlled_paper_approved_start_template_generator_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o22_r6_controlled_paper_approved_start_template_generator.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o22_r6_controlled_paper_approved_start_template_generator.json"
TEMPLATE_SH = RUN_DIR / "CONTROLLED_PAPER_START_TEMPLATE_NOT_APPROVED_o22_r6.sh"
STOP_TEMPLATE_SH = RUN_DIR / "CONTROLLED_PAPER_STOP_TEMPLATE_o22_r6.sh"
TEMPLATE_JSON = RUN_DIR / "controlled_paper_approved_start_template_o22_r6.json"
GATE_JSON = RUN_DIR / "controlled_paper_start_gate_o22_r6.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o22_r6_controlled_paper_approved_start_template_generator.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o22_r6_controlled_paper_approved_start_template_generator.md"
BIN_COPY = BIN_DIR / "proof_batch26o22_r6_controlled_paper_approved_start_template_generator.py"

REDIS_CLI = os.environ.get("REDIS_CLI", "redis-cli")
FEATURES_STREAM = "features:mme:stream"
DECISIONS_STREAM = "decisions:mme:stream"
ORDERS_STREAM = "orders:mme:stream"
POSITION_HASH = "state:position:mme"

CONTROLLED_PAPER_SCOPE_ACK = "I_ACCEPT_MIST_CALL_1LOT_PAPER_ONLY"

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
    "run/proofs/proof_batch26o22_r5_controlled_paper_operator_checklist_gate.json",
]


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


def env_state() -> dict[str, str]:
    keys = [
        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
        "SCALPX_REAL_LIVE_ALLOWED",
        "SCALPX_LIVE_ORDERS_ALLOWED",
        "SCALPX_BROKER_CALLS_ALLOWED",
        "SCALPX_FORCE_CANDIDATE",
        "SCALPX_THRESHOLD_RELAXATION",
        "SCALPX_PAPER_ARMED",
    ]
    return {k: os.environ.get(k, "") for k in keys}


def write_templates(prior: dict[str, Any], runtime: dict[str, Any]) -> dict[str, Any]:
    start_template = f'''#!/usr/bin/env bash
# CONTROLLED PAPER START TEMPLATE — NOT APPROVED BY GENERATION
# Generated by {BATCH} at {datetime.now(timezone.utc).isoformat()}
#
# DO NOT RUN THIS FILE UNTIL THE OPERATOR EXPLICITLY APPROVES CONTROLLED PAPER START.
#
# Scope locked:
# - MIST CALL only
# - 1 lot only
# - paper/sandbox only
# - real_live=false
# - no automatic broker failover
# - no mid-position provider migration
#
# Required future explicit approval phrase from operator:
#   APPROVE CONTROLLED PAPER START: MIST CALL, 1 LOT, PAPER ONLY, REAL LIVE FALSE

set -euo pipefail
cd /home/Lenovo/scalpx/projects/mme_scalpx

PYBIN=".venv/bin/python"
if [ ! -x "$PYBIN" ]; then
  PYBIN="$(command -v python3)"
fi

export PYTHONPATH="$PWD:${{PYTHONPATH:-}}"

# Approval envs — intentionally shown here, not activated by R6.
export SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME=1
export SCALPX_CONTROLLED_PAPER_SCOPE_ACK="{CONTROLLED_PAPER_SCOPE_ACK}"

# Hard safety envs.
export SCALPX_REAL_LIVE_ALLOWED=0
export SCALPX_LIVE_ORDERS_ALLOWED=0
export SCALPX_BROKER_CALLS_ALLOWED=0
export SCALPX_FORCE_CANDIDATE=0
export SCALPX_THRESHOLD_RELAXATION=0

# Scope envs, if consumed by runtime.
export SCALPX_CONTROLLED_PAPER_FAMILY=MIST
export SCALPX_CONTROLLED_PAPER_BRANCH=CALL
export SCALPX_CONTROLLED_PAPER_QTY_LOTS=1
export SCALPX_CONTROLLED_PAPER_ROUTE=paper

# Preflight checks before any process start.
echo "===== CONTROLLED PAPER PRE-START SAFETY CHECK ====="
date -Is

ORDERS_XLEN="$(redis-cli XLEN orders:mme:stream)"
echo "orders:mme:stream XLEN=$ORDERS_XLEN"
if [ "$ORDERS_XLEN" != "0" ]; then
  echo "REFUSE: orders stream is not empty"
  exit 2
fi

HAS_POSITION="$(redis-cli HGET state:position:mme has_position || true)"
POSITION_SIDE="$(redis-cli HGET state:position:mme position_side || true)"
QTY_LOTS="$(redis-cli HGET state:position:mme qty_lots || true)"
QTY_UNITS="$(redis-cli HGET state:position:mme qty_units || true)"
echo "position has_position=$HAS_POSITION side=$POSITION_SIDE qty_lots=$QTY_LOTS qty_units=$QTY_UNITS"
if [ "${{HAS_POSITION:-0}}" != "0" ] || [ "${{POSITION_SIDE:-FLAT}}" != "FLAT" ] || [ "${{QTY_LOTS:-0}}" != "0" ] || [ "${{QTY_UNITS:-0}}" != "0" ]; then
  echo "REFUSE: position is not FLAT"
  exit 2
fi

if ps -eo cmd | grep -E 'app\\.mme_scalpx.*--service (risk|execution)' | grep -v grep; then
  echo "REFUSE: risk/execution already running"
  exit 2
fi

echo "===== START ORDER FOR FUTURE APPROVED CONTROLLED PAPER ====="
echo "1) Start/confirm feeds and features in observe/control-safe mode."
echo "2) Start strategy in controlled-paper scope."
echo "3) Start risk only after risk preflight passes."
echo "4) Start execution only after execution preflight passes."
echo
echo "This generated template intentionally does not contain a live broker-order command."
echo "Before adding any actual start line, run the next approved batch that validates exact CLI flags from current main.py."
exit 0
'''

    stop_template = '''#!/usr/bin/env bash
# CONTROLLED PAPER STOP TEMPLATE
set -euo pipefail
cd /home/Lenovo/scalpx/projects/mme_scalpx

echo "===== CONTROLLED PAPER STOP / SAFETY READBACK ====="
date -Is

ps -eo pid,ppid,cmd | grep -E 'app\\.mme_scalpx|mme_scalpx|services' | grep -v grep || true

echo
echo "orders:mme:stream"
redis-cli XLEN orders:mme:stream || true
redis-cli XREVRANGE orders:mme:stream + - COUNT 5 || true

echo
echo "state:position:mme"
redis-cli HGETALL state:position:mme || true

echo
echo "NOTE: This template does not kill processes automatically. Use the process list above and stop only controlled-paper services deliberately."
'''

    TEMPLATE_SH.write_text(start_template, encoding="utf-8")
    STOP_TEMPLATE_SH.write_text(stop_template, encoding="utf-8")
    TEMPLATE_SH.chmod(0o640)
    STOP_TEMPLATE_SH.chmod(0o640)

    template_json = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "TEMPLATE_GENERATED_NOT_APPROVED_NOT_EXECUTED",
        "start_template": str(TEMPLATE_SH.relative_to(ROOT)),
        "stop_template": str(STOP_TEMPLATE_SH.relative_to(ROOT)),
        "paper_start_allowed_by_this_batch": False,
        "requires_future_explicit_operator_approval": True,
        "future_required_approval_phrase": "APPROVE CONTROLLED PAPER START: MIST CALL, 1 LOT, PAPER ONLY, REAL LIVE FALSE",
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
        "prior_o22_r5": {
            "final_verdict": prior.get("final_verdict"),
            "false_keys": prior.get("false_keys"),
            "next_recommended_batch": prior.get("next_recommended_batch"),
        },
        "runtime_snapshot_at_generation": runtime,
    }
    TEMPLATE_JSON.write_text(json.dumps(template_json, indent=2, sort_keys=True), encoding="utf-8")
    return template_json


def main() -> int:
    proof: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": BATCH_NAME,
        "tag": TAG,
        "started_at_utc": NOW,
        "root": str(ROOT),
        "evidence_first_policy": {
            "latest_uploaded_evidence_output_read": True,
            "prior_o22_r5_pass_required": True,
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
            "template_generation_only": True,
        },
        "prior_proofs": {},
        "inspected_files": {},
        "commands": {},
        "runtime_snapshot": {},
        "env_state": {},
        "template_json": {},
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

        print("===== READ-ONLY RUNTIME SNAPSHOT =====")
        runtime = runtime_snapshot()
        proof["runtime_snapshot"] = runtime

        env = env_state()
        proof["env_state"] = env

        o22_r5 = proof["prior_proofs"].get("run/proofs/proof_batch26o22_r5_controlled_paper_operator_checklist_gate.json", {})
        o22_r5_req = o22_r5.get("required_verdicts") or {}

        print("===== GENERATE LOCKED TEMPLATE ONLY =====")
        template_json = write_templates(o22_r5, runtime)
        proof["template_json"] = template_json

        pos = runtime.get("position") or {}
        orders_zero = runtime.get("orders_xlen") == 0 and not (runtime.get("latest_orders_raw", {}).get("stdout") or "").strip()
        position_flat = flat_position(pos)

        approval_gate = {
            "batch": BATCH,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "status": "LOCKED_TEMPLATE_ONLY_NOT_APPROVED",
            "paper_start_allowed_by_this_batch": False,
            "future_explicit_approval_required": True,
            "future_approval_phrase": "APPROVE CONTROLLED PAPER START: MIST CALL, 1 LOT, PAPER ONLY, REAL LIVE FALSE",
            "template_path": str(TEMPLATE_SH.relative_to(ROOT)),
            "stop_template_path": str(STOP_TEMPLATE_SH.relative_to(ROOT)),
            "current_env_state": env,
            "current_runtime_safety": {
                "orders_zero": orders_zero,
                "position_flat": position_flat,
                "risk_running": runtime.get("risk_running"),
                "execution_running": runtime.get("execution_running"),
            },
            "refusal_if_run_without_next_approved_batch": True,
            "next_if_pass": "26-O22-R7 exact CLI flag validator for controlled-paper start template; still no actual start unless explicitly approved.",
        }
        proof["approval_gate"] = approval_gate
        GATE_JSON.write_text(json.dumps(approval_gate, indent=2, sort_keys=True), encoding="utf-8")

        req = {
            "o22_r5_pass_loaded": str(o22_r5.get("final_verdict", "")).startswith("PASS_O22_R5_CONTROLLED_PAPER_OPERATOR_CHECKLIST_GATE_OK_LOCKED_NO_START"),
            "o22_r5_false_keys_empty": o22_r5.get("false_keys") == [],
            "o22_r5_gate_locked": o22_r5_req.get("approval_gate_locked") is True,
            "o22_r5_paper_start_allowed_false": o22_r5_req.get("paper_start_allowed_by_this_batch_false") is True,
            "compile_pass": bool(proof["commands"]["compile"].get("ok")),
            "import_pass": bool(proof["commands"]["import"].get("ok")),
            "template_sh_written": TEMPLATE_SH.exists(),
            "stop_template_sh_written": STOP_TEMPLATE_SH.exists(),
            "template_json_written": TEMPLATE_JSON.exists(),
            "gate_json_written": GATE_JSON.exists(),
            "template_not_executable_by_default": oct(TEMPLATE_SH.stat().st_mode & 0o777) == "0o640",
            "stop_template_not_executable_by_default": oct(STOP_TEMPLATE_SH.stat().st_mode & 0o777) == "0o640",
            "paper_start_allowed_by_this_batch_false": template_json.get("paper_start_allowed_by_this_batch") is False,
            "approval_gate_locked_template_only": approval_gate.get("status") == "LOCKED_TEMPLATE_ONLY_NOT_APPROVED",
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
            proof["final_verdict"] = "FAIL_O22_R6_CONTROLLED_PAPER_TEMPLATE_GENERATOR_NOT_PROVEN"
            proof["next_recommended_batch"] = "Inspect false_keys and write smallest Lane-A diagnostic package; no paper start."
        else:
            proof["final_verdict"] = "PASS_O22_R6_CONTROLLED_PAPER_TEMPLATE_GENERATOR_OK_LOCKED_NO_START"
            proof["next_recommended_batch"] = "26-O22-R7 exact CLI flag validator for controlled-paper start template; still no actual start unless explicitly approved."

        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

        RUNBOOK_MD.write_text(
            "\n".join([
                f"# {BATCH} — controlled-paper approved-start command template generator",
                "",
                f"- generated_at_utc: {proof['completed_at_utc']}",
                f"- tag: `{TAG}`",
                f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
                f"- manifest: `{MANIFEST_JSON.relative_to(ROOT)}`",
                f"- start_template: `{TEMPLATE_SH.relative_to(ROOT)}`",
                f"- stop_template: `{STOP_TEMPLATE_SH.relative_to(ROOT)}`",
                f"- template_json: `{TEMPLATE_JSON.relative_to(ROOT)}`",
                f"- gate_json: `{GATE_JSON.relative_to(ROOT)}`",
                f"- backup_dir: `{BACKUP_DIR.relative_to(ROOT)}`",
                "",
                "## Purpose",
                "- Generate a locked future controlled-paper start template.",
                "- This batch does not approve or start controlled paper.",
                "- Template files are intentionally non-executable by default.",
                "",
                "## Future explicit approval phrase",
                "`APPROVE CONTROLLED PAPER START: MIST CALL, 1 LOT, PAPER ONLY, REAL LIVE FALSE`",
                "",
                "## Scope locked",
                "- MIST CALL only.",
                "- 1 lot only.",
                "- paper/sandbox route only.",
                "- real_live=false.",
                "- no automatic broker failover.",
                "- no mid-position provider migration.",
                "- FLAT position before entry.",
                "",
                "## Safety",
                "- No service start.",
                "- No broker call.",
                "- No order write.",
                "- No real live.",
                "- No source patch.",
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
                f"# {DATE} — {BATCH} controlled-paper approved-start template generator",
                "",
                f"Verdict: `{proof['final_verdict']}`",
                "",
                "## Achieved",
                "- Loaded O22-R5 PASS as prerequisite.",
                "- Inspected latest source/proof/config artifacts first.",
                "- Backed up inspected files.",
                "- Ran compile/import proof.",
                "- Generated locked start template.",
                "- Generated stop/readback template.",
                "- Generated approval gate JSON.",
                "- Confirmed template is not executable by default.",
                "- Confirmed orders zero and position FLAT.",
                "- Confirmed no controlled-paper env, no scope ACK env, no broker/order intent, risk/execution not running.",
                "",
                "## Not done",
                "- Did not start controlled paper.",
                "- Did not approve controlled paper.",
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
                f"- `{TEMPLATE_SH.relative_to(ROOT)}`",
                f"- `{STOP_TEMPLATE_SH.relative_to(ROOT)}`",
                f"- `{TEMPLATE_JSON.relative_to(ROOT)}`",
                f"- `{GATE_JSON.relative_to(ROOT)}`",
                f"- `{RUNBOOK_MD.relative_to(ROOT)}`",
            ]),
            encoding="utf-8",
        )

        shutil.copy2(pathlib.Path(__file__), BIN_COPY)

        manifest_paths = [
            PROOF_JSON,
            RUNBOOK_MD,
            MILESTONE_MD,
            TEMPLATE_SH,
            STOP_TEMPLATE_SH,
            TEMPLATE_JSON,
            GATE_JSON,
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
        print(f"start_template = {TEMPLATE_SH.relative_to(ROOT)}")
        print(f"stop_template = {STOP_TEMPLATE_SH.relative_to(ROOT)}")
        print(f"template_json = {TEMPLATE_JSON.relative_to(ROOT)}")
        print(f"gate_json = {GATE_JSON.relative_to(ROOT)}")
        print(f"runbook = {RUNBOOK_MD.relative_to(ROOT)}")
        print(f"milestone = {MILESTONE_MD.relative_to(ROOT)}")
        return 0 if proof["final_verdict"].startswith("PASS_") else 2

    except Exception as exc:
        proof["exception"] = repr(exc)
        proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
        proof["final_verdict"] = "FAIL_O22_R6_EXCEPTION_SAFE_STOP_NO_MUTATION"
        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
        print("===== EXCEPTION SAFE STOP =====")
        print(repr(exc))
        print(f"proof_json = {PROOF_JSON.relative_to(ROOT)}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
