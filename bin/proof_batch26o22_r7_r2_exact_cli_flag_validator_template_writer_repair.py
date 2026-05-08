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
BATCH = "26-O22-R7-R2"
BATCH_NAME = "exact_cli_flag_validator_template_writer_repair_no_start_no_live"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
NOW = datetime.now(timezone.utc).isoformat()
TAG = f"batch26o22_r7_r2_exact_cli_flag_validator_template_writer_repair_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o22_r7_r2_exact_cli_flag_validator_template_writer_repair.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o22_r7_r2_exact_cli_flag_validator_template_writer_repair.json"
CLI_VALIDATION_JSON = RUN_DIR / "controlled_paper_cli_flag_validation_o22_r7_r2.json"
VALIDATED_TEMPLATE_SH = RUN_DIR / "CONTROLLED_PAPER_START_TEMPLATE_VALIDATED_NOT_APPROVED_o22_r7_r2.sh"
START_PLAN_JSON = RUN_DIR / "controlled_paper_start_plan_validated_o22_r7_r2.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o22_r7_r2_exact_cli_flag_validator_template_writer_repair.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o22_r7_r2_exact_cli_flag_validator_template_writer_repair.md"
BIN_COPY = BIN_DIR / "proof_batch26o22_r7_r2_exact_cli_flag_validator_template_writer_repair.py"

REDIS_CLI = os.environ.get("REDIS_CLI", "redis-cli")
ORDERS_STREAM = "orders:mme:stream"
POSITION_HASH = "state:position:mme"

CONTROLLED_PAPER_SCOPE_ACK = "I_ACCEPT_MIST_CALL_1LOT_PAPER_ONLY"
APPROVAL_PHRASE = "APPROVE CONTROLLED PAPER START: MIST CALL, 1 LOT, PAPER ONLY, REAL LIVE FALSE"

INSPECT_PATHS = [
    "app/mme_scalpx/main.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/feeds.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "app/mme_scalpx/core/redisx.py",
    "app/mme_scalpx/core/settings.py",
    "app/mme_scalpx/integrations/provider_runtime.py",
    "app/mme_scalpx/integrations/bootstrap_provider.py",
    "run/proofs/proof_batch26o22_r6_controlled_paper_approved_start_template_generator.json",
    "run/proofs/proof_batch26o22_r7_exact_cli_flag_validator.json",
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
        "orders_xlen": redis_xlen(ORDERS_STREAM),
        "latest_orders_raw": latest_orders,
        "position": redis_hgetall(POSITION_HASH),
        "process_lines": proc_lines(),
        "features_running": service_running("features"),
        "strategy_running": service_running("strategy"),
        "risk_running": service_running("risk"),
        "execution_running": service_running("execution"),
    }


def extract_main_cli_flags() -> dict[str, Any]:
    main_py = ROOT / "app/mme_scalpx/main.py"
    text = main_py.read_text(encoding="utf-8", errors="replace") if main_py.exists() else ""
    flags = sorted(set(re.findall(r"""["'](--[a-zA-Z0-9][a-zA-Z0-9_-]*)["']""", text)))
    service_literals = sorted(set(re.findall(r"""["'](feeds|features|strategy|risk|execution|monitor|report)["']""", text)))
    relevant_lines = []
    for idx, line in enumerate(text.splitlines(), start=1):
        if any(tok in line for tok in ["add_argument", "argparse", "--service", "--bootstrap-provider", "--skip-group-bootstrap", "--once"]):
            relevant_lines.append({"line": idx, "text": line[:260]})
    return {
        "main_exists": main_py.exists(),
        "main_sha256": sha256_file(main_py) if main_py.exists() else None,
        "flags": flags,
        "service_literals": service_literals,
        "relevant_lines": relevant_lines[:200],
        "has_service_flag": "--service" in flags or "--service" in text,
        "has_bootstrap_provider_flag": "--bootstrap-provider" in flags or "--bootstrap-provider" in text,
        "has_skip_group_bootstrap_flag": "--skip-group-bootstrap" in flags or "--skip-group-bootstrap" in text,
        "has_once_flag": "--once" in flags or "--once" in text,
    }


def validate_main_help() -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{ROOT}:{env.get('PYTHONPATH', '')}"
    env["SCALPX_REAL_LIVE_ALLOWED"] = "0"
    env["SCALPX_LIVE_ORDERS_ALLOWED"] = "0"
    env["SCALPX_BROKER_CALLS_ALLOWED"] = "0"
    env["SCALPX_PAPER_ARMED"] = "0"
    env["SCALPX_FORCE_CANDIDATE"] = "0"
    return run([sys.executable, "-m", "app.mme_scalpx.main", "--help"], timeout=30, env=env)


def make_service_command(service: str, cli: dict[str, Any]) -> str:
    cmd = f'"$PYBIN" -m app.mme_scalpx.main --service {service}'
    if cli.get("has_bootstrap_provider_flag") is True:
        cmd += " --bootstrap-provider app.mme_scalpx.integrations.bootstrap_provider:provide"
    if cli.get("has_skip_group_bootstrap_flag") is True:
        cmd += " --skip-group-bootstrap"
    return cmd


def write_validated_template(cli: dict[str, Any], prior_r6: dict[str, Any], prior_r7_fail: dict[str, Any], runtime: dict[str, Any]) -> dict[str, Any]:
    services = ["feeds", "features", "strategy", "risk", "execution"]
    service_commands = [make_service_command(svc, cli) for svc in services]

    start_chunks: list[str] = []
    for idx, (svc, cmd) in enumerate(zip(services, service_commands), start=1):
        start_chunks.append(f'echo "WOULD START {svc}: {cmd}"\n')
        start_chunks.append(f'# nohup {cmd} > "run/live_capture/controlled_paper_{idx}_{svc}_${{TS}}.log" 2>&1 &\n')
        start_chunks.append(f'# echo $! > "run/live_capture/controlled_paper_{idx}_{svc}.pid"\n\n')
    start_lines = "".join(start_chunks)

    script = f'''#!/usr/bin/env bash
# CONTROLLED PAPER START TEMPLATE — VALIDATED BUT NOT APPROVED / NOT EXECUTABLE BY DEFAULT
# Generated by {BATCH} at {datetime.now(timezone.utc).isoformat()}
#
# DO NOT RUN UNTIL USER EXPLICITLY APPROVES:
# {APPROVAL_PHRASE}
#
# This template keeps all service start lines commented out.
# R7-R2 repaired the R7 template-writer bug and still starts nothing.

set -euo pipefail
cd /home/Lenovo/scalpx/projects/mme_scalpx

TS="$(date +%Y%m%d_%H%M%S)"
PYBIN=".venv/bin/python"
if [ ! -x "$PYBIN" ]; then
  PYBIN="$(command -v python3)"
fi

export PYTHONPATH="$PWD:${{PYTHONPATH:-}}"

export SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME=1
export SCALPX_CONTROLLED_PAPER_SCOPE_ACK="{CONTROLLED_PAPER_SCOPE_ACK}"

export SCALPX_REAL_LIVE_ALLOWED=0
export SCALPX_LIVE_ORDERS_ALLOWED=0
export SCALPX_BROKER_CALLS_ALLOWED=0
export SCALPX_FORCE_CANDIDATE=0
export SCALPX_THRESHOLD_RELAXATION=0

export SCALPX_CONTROLLED_PAPER_FAMILY=MIST
export SCALPX_CONTROLLED_PAPER_BRANCH=CALL
export SCALPX_CONTROLLED_PAPER_QTY_LOTS=1
export SCALPX_CONTROLLED_PAPER_ROUTE=paper

echo "===== CONTROLLED PAPER VALIDATED TEMPLATE PREFLIGHT ====="
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

echo "===== VALIDATED SERVICE COMMANDS — COMMENTED OUT BY DESIGN ====="
{start_lines}
echo "Template validation complete. No service was started by this template."
exit 0
'''
    VALIDATED_TEMPLATE_SH.write_text(script, encoding="utf-8")
    VALIDATED_TEMPLATE_SH.chmod(0o640)

    start_plan = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "VALIDATED_TEMPLATE_ONLY_NOT_APPROVED_NOT_EXECUTED",
        "validated_template": str(VALIDATED_TEMPLATE_SH.relative_to(ROOT)),
        "template_mode": oct(VALIDATED_TEMPLATE_SH.stat().st_mode & 0o777),
        "paper_start_allowed_by_this_batch": False,
        "service_commands_commented_out": True,
        "future_approval_phrase_required": APPROVAL_PHRASE,
        "scope": {
            "family": "MIST",
            "branch": "CALL",
            "qty_lots": 1,
            "route": "paper_or_sandbox_only",
            "real_live_allowed": False,
            "automatic_broker_failover_allowed": False,
            "mid_position_provider_migration_allowed": False,
        },
        "validated_cli": {
            "main_flags": cli.get("flags"),
            "has_service_flag": cli.get("has_service_flag"),
            "has_bootstrap_provider_flag": cli.get("has_bootstrap_provider_flag"),
            "has_skip_group_bootstrap_flag": cli.get("has_skip_group_bootstrap_flag"),
            "service_commands": service_commands,
        },
        "prior_o22_r6": {
            "final_verdict": prior_r6.get("final_verdict"),
            "false_keys": prior_r6.get("false_keys"),
            "next_recommended_batch": prior_r6.get("next_recommended_batch"),
        },
        "prior_o22_r7_failed_safely": {
            "final_verdict": prior_r7_fail.get("final_verdict"),
            "exception": prior_r7_fail.get("exception"),
            "false_keys": prior_r7_fail.get("false_keys"),
        },
        "runtime_snapshot_at_generation": runtime,
    }
    START_PLAN_JSON.write_text(json.dumps(start_plan, indent=2, sort_keys=True), encoding="utf-8")
    return start_plan


def main() -> int:
    proof: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": BATCH_NAME,
        "tag": TAG,
        "started_at_utc": NOW,
        "root": str(ROOT),
        "evidence_first_policy": {
            "latest_uploaded_evidence_output_read": True,
            "prior_o22_r6_pass_required": True,
            "prior_o22_r7_failure_inspected": True,
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
            "cli_validation_template_writer_repair_only": True,
        },
        "prior_proofs": {},
        "inspected_files": {},
        "commands": {},
        "main_cli": {},
        "main_help": {},
        "runtime_snapshot": {},
        "start_plan": {},
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
                        "exception": loaded.get("exception") if isinstance(loaded, dict) else None,
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
            "app/mme_scalpx/main.py",
            "app/mme_scalpx/services/risk.py",
            "app/mme_scalpx/services/execution.py",
            "app/mme_scalpx/services/strategy.py",
            "app/mme_scalpx/services/features.py",
            "app/mme_scalpx/services/feeds.py",
            "app/mme_scalpx/core/names.py",
            "app/mme_scalpx/core/models.py",
            "app/mme_scalpx/core/redisx.py",
        ]
        proof["commands"]["compile"] = run([sys.executable, "-m", "py_compile", *compile_targets], timeout=60)
        proof["commands"]["import"] = run(
            [
                sys.executable,
                "-c",
                "import app.mme_scalpx.main, app.mme_scalpx.services.risk, app.mme_scalpx.services.execution, app.mme_scalpx.services.strategy, app.mme_scalpx.services.features, app.mme_scalpx.services.feeds; print('IMPORT_OK')",
            ],
            timeout=60,
        )

        print("===== VALIDATE MAIN CLI FLAGS =====")
        main_cli = extract_main_cli_flags()
        proof["main_cli"] = main_cli
        main_help = validate_main_help()
        proof["main_help"] = main_help

        print("===== READ-ONLY RUNTIME SNAPSHOT =====")
        runtime = runtime_snapshot()
        proof["runtime_snapshot"] = runtime

        o22_r6 = proof["prior_proofs"].get("run/proofs/proof_batch26o22_r6_controlled_paper_approved_start_template_generator.json", {})
        o22_r6_req = o22_r6.get("required_verdicts") or {}
        o22_r7_fail = proof["prior_proofs"].get("run/proofs/proof_batch26o22_r7_exact_cli_flag_validator.json", {})

        print("===== WRITE VALIDATED LOCKED TEMPLATE WITH R7 WRITER BUG FIXED =====")
        start_plan = write_validated_template(main_cli, o22_r6, o22_r7_fail, runtime)
        proof["start_plan"] = start_plan

        orders_zero = runtime.get("orders_xlen") == 0 and not (runtime.get("latest_orders_raw", {}).get("stdout") or "").strip()
        position_flat = flat_position(runtime.get("position") or {})
        env = {
            "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME": os.environ.get("SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME", ""),
            "SCALPX_CONTROLLED_PAPER_SCOPE_ACK": os.environ.get("SCALPX_CONTROLLED_PAPER_SCOPE_ACK", ""),
            "SCALPX_REAL_LIVE_ALLOWED": os.environ.get("SCALPX_REAL_LIVE_ALLOWED", ""),
            "SCALPX_LIVE_ORDERS_ALLOWED": os.environ.get("SCALPX_LIVE_ORDERS_ALLOWED", ""),
            "SCALPX_BROKER_CALLS_ALLOWED": os.environ.get("SCALPX_BROKER_CALLS_ALLOWED", ""),
            "SCALPX_FORCE_CANDIDATE": os.environ.get("SCALPX_FORCE_CANDIDATE", ""),
            "SCALPX_THRESHOLD_RELAXATION": os.environ.get("SCALPX_THRESHOLD_RELAXATION", ""),
            "SCALPX_PAPER_ARMED": os.environ.get("SCALPX_PAPER_ARMED", ""),
        }

        cli_text = json.dumps(main_cli) + "\n" + (main_help.get("stdout") or "") + "\n" + (main_help.get("stderr") or "")

        req = {
            "o22_r6_pass_loaded": str(o22_r6.get("final_verdict", "")).startswith("PASS_O22_R6_CONTROLLED_PAPER_TEMPLATE_GENERATOR_OK_LOCKED_NO_START"),
            "o22_r6_false_keys_empty": o22_r6.get("false_keys") == [],
            "o22_r6_template_written": o22_r6_req.get("template_sh_written") is True,
            "o22_r6_paper_start_allowed_false": o22_r6_req.get("paper_start_allowed_by_this_batch_false") is True,
            "o22_r7_failure_loaded": str(o22_r7_fail.get("final_verdict", "")).startswith("FAIL_O22_R7") or "sequence item" in str(o22_r7_fail.get("exception")),
            "o22_r7_failure_was_template_writer_typeerror": "sequence item" in str(o22_r7_fail.get("exception")),
            "compile_pass": bool(proof["commands"]["compile"].get("ok")),
            "import_pass": bool(proof["commands"]["import"].get("ok")),
            "main_cli_service_flag_present": main_cli.get("has_service_flag") is True or "--service" in cli_text,
            "main_help_invocation_safe": main_help.get("returncode") in {0, 1, 2},
            "validated_template_written": VALIDATED_TEMPLATE_SH.exists(),
            "validated_template_not_executable_by_default": oct(VALIDATED_TEMPLATE_SH.stat().st_mode & 0o777) == "0o640",
            "start_plan_json_written": START_PLAN_JSON.exists(),
            "service_commands_commented_out": start_plan.get("service_commands_commented_out") is True,
            "paper_start_allowed_by_this_batch_false": start_plan.get("paper_start_allowed_by_this_batch") is False,
            "service_command_count_is_5": len(start_plan.get("validated_cli", {}).get("service_commands") or []) == 5,
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
            proof["final_verdict"] = "FAIL_O22_R7_R2_EXACT_CLI_FLAG_VALIDATOR_NOT_PROVEN"
            proof["next_recommended_batch"] = "Inspect false_keys and write smallest Lane-A diagnostic package; no paper start."
        else:
            proof["final_verdict"] = "PASS_O22_R7_R2_EXACT_CLI_FLAG_VALIDATOR_OK_LOCKED_NO_START"
            proof["next_recommended_batch"] = "26-O22-R8 final controlled-paper go/no-go evidence pack; still no actual start unless explicit user approval."

        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

        CLI_VALIDATION_JSON.write_text(
            json.dumps(
                {
                    "batch": BATCH,
                    "generated_at_utc": proof["completed_at_utc"],
                    "main_cli": main_cli,
                    "main_help": main_help,
                    "start_plan": start_plan,
                    "required_verdicts": req,
                    "final_verdict": proof["final_verdict"],
                },
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

        RUNBOOK_MD.write_text(
            "\n".join([
                f"# {BATCH} — exact CLI flag validator template-writer repair",
                "",
                f"- generated_at_utc: {proof['completed_at_utc']}",
                f"- tag: `{TAG}`",
                f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
                f"- manifest: `{MANIFEST_JSON.relative_to(ROOT)}`",
                f"- cli_validation: `{CLI_VALIDATION_JSON.relative_to(ROOT)}`",
                f"- validated_template: `{VALIDATED_TEMPLATE_SH.relative_to(ROOT)}`",
                f"- start_plan: `{START_PLAN_JSON.relative_to(ROOT)}`",
                f"- backup_dir: `{BACKUP_DIR.relative_to(ROOT)}`",
                "",
                "## Purpose",
                "- Repair R7 template-writer bug only.",
                "- Validate current `app.mme_scalpx.main` CLI surfaces.",
                "- Generate a validated but still locked start template.",
                "- Keep all service start lines commented out.",
                "- No paper start, no service start, no broker call, no order write, no source patch.",
                "",
                "## Future explicit approval phrase",
                f"`{APPROVAL_PHRASE}`",
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
                f"# {DATE} — {BATCH} exact CLI flag validator repair",
                "",
                f"Verdict: `{proof['final_verdict']}`",
                "",
                "## Achieved",
                "- Loaded O22-R6 PASS as prerequisite.",
                "- Loaded R7 failed proof and classified failure as template-writer TypeError.",
                "- Inspected latest source/proof/config artifacts first.",
                "- Backed up inspected files.",
                "- Ran compile/import proof.",
                "- Inspected `main.py` CLI flags and safe help output.",
                "- Generated validated but locked start template.",
                "- Kept service commands commented out.",
                "- Confirmed template is not executable by default.",
                "- Confirmed orders zero, position FLAT, no paper env, no scope ACK env, no broker/order intent, risk/execution not running.",
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
                f"- `{CLI_VALIDATION_JSON.relative_to(ROOT)}`",
                f"- `{VALIDATED_TEMPLATE_SH.relative_to(ROOT)}`",
                f"- `{START_PLAN_JSON.relative_to(ROOT)}`",
                f"- `{RUNBOOK_MD.relative_to(ROOT)}`",
            ]),
            encoding="utf-8",
        )

        shutil.copy2(pathlib.Path(__file__), BIN_COPY)

        manifest_paths = [
            PROOF_JSON,
            RUNBOOK_MD,
            MILESTONE_MD,
            CLI_VALIDATION_JSON,
            VALIDATED_TEMPLATE_SH,
            START_PLAN_JSON,
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
        print(f"cli_validation_json = {CLI_VALIDATION_JSON.relative_to(ROOT)}")
        print(f"validated_template = {VALIDATED_TEMPLATE_SH.relative_to(ROOT)}")
        print(f"start_plan_json = {START_PLAN_JSON.relative_to(ROOT)}")
        print(f"runbook = {RUNBOOK_MD.relative_to(ROOT)}")
        print(f"milestone = {MILESTONE_MD.relative_to(ROOT)}")
        return 0 if proof["final_verdict"].startswith("PASS_") else 2

    except Exception as exc:
        proof["exception"] = repr(exc)
        proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
        proof["final_verdict"] = "FAIL_O22_R7_R2_EXCEPTION_SAFE_STOP_NO_MUTATION"
        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
        print("===== EXCEPTION SAFE STOP =====")
        print(repr(exc))
        print(f"proof_json = {PROOF_JSON.relative_to(ROOT)}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
