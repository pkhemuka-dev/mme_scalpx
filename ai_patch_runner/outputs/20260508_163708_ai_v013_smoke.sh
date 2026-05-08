cd /home/Lenovo/scalpx/projects/mme_scalpx
set -euo pipefail

if [ -x ".venv/bin/python" ]; then
  PYBIN=".venv/bin/python"
else
  PYBIN="python3"
fi

export PYTHONPATH="/home/Lenovo/scalpx/projects/mme_scalpx${PYTHONPATH:+:$PYTHONPATH}"

mkdir -p run/proofs docs/milestones run/_code_backups run/audits

BATCH_ID="AI-V013-SMOKE"
UTC_TS="$(date -u +%Y%m%dT%H%M%SZ)"
PROOF_PATH="run/proofs/${BATCH_ID}_${UTC_TS}.json"
MILESTONE_PATH="docs/milestones/${BATCH_ID}_${UTC_TS}.md"
AUDIT_PATH="run/audits/${BATCH_ID}_${UTC_TS}_prewrite_audit.txt"

{
  echo "batch_id=${BATCH_ID}"
  echo "utc_ts=${UTC_TS}"
  echo "pwd=$(pwd)"
  echo "pybin=${PYBIN}"
  echo "git_head=$(git rev-parse HEAD 2>/dev/null || true)"
  echo "git_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
  echo "git_status_short_begin"
  git status --short 2>/dev/null || true
  echo "git_status_short_end"
  echo "target_proof_path=${PROOF_PATH}"
  echo "target_milestone_path=${MILESTONE_PATH}"
  echo "inspection_result=audit_only_smoke_no_project_code_targets"
} > "${AUDIT_PATH}"

if [ -e "${PROOF_PATH}" ]; then
  cp -a "${PROOF_PATH}" "run/_code_backups/$(basename "${PROOF_PATH}").bak_${UTC_TS}"
fi

if [ -e "${MILESTONE_PATH}" ]; then
  cp -a "${MILESTONE_PATH}" "run/_code_backups/$(basename "${MILESTONE_PATH}").bak_${UTC_TS}"
fi

export BATCH_ID UTC_TS PROOF_PATH MILESTONE_PATH AUDIT_PATH PYBIN

"$PYBIN" - <<'PY'
import json
import os
import pathlib
import platform
import subprocess
import sys

batch_id = os.environ["BATCH_ID"]
utc_ts = os.environ["UTC_TS"]
proof_path = pathlib.Path(os.environ["PROOF_PATH"])
milestone_path = pathlib.Path(os.environ["MILESTONE_PATH"])
audit_path = pathlib.Path(os.environ["AUDIT_PATH"])
pybin = os.environ["PYBIN"]

def run_capture(cmd):
    try:
        p = subprocess.run(cmd, cwd=pathlib.Path.cwd(), text=True, capture_output=True, timeout=10)
        return {
            "cmd": cmd,
            "returncode": p.returncode,
            "stdout": p.stdout.strip(),
            "stderr": p.stderr.strip(),
        }
    except Exception as exc:
        return {
            "cmd": cmd,
            "returncode": None,
            "stdout": "",
            "stderr": repr(exc),
        }

git_head = run_capture(["git", "rev-parse", "HEAD"])
git_status = run_capture(["git", "status", "--short"])

proof = {
    "batch_id": batch_id,
    "title": "AI Patch Runner v0.1.3 harmless audit-only smoke proof",
    "utc_ts": utc_ts,
    "schema_version": "smoke-proof-v1",
    "ai_patch_runner": {
        "version": "0.1.3",
        "mode": "command_package_generation_only",
        "command_package_generated": True,
        "target_patch_payload_executed": False,
        "project_code_patched": False,
        "audit_only": True,
    },
    "safety_flags": {
        "broker_calls_executed": False,
        "service_starts_executed": False,
        "live_redis_writes_executed": False,
        "paper_or_live_enabled": False,
    },
    "negative_assertions": {
        "did_not_start_services": True,
        "did_not_call_broker": True,
        "did_not_place_orders": True,
        "did_not_write_live_redis_trading_truth": True,
        "did_not_enable_paper": True,
        "did_not_enable_live": True,
        "did_not_patch_project_code": True,
        "did_not_modify_execution_risk_broker_or_main_live_control_files": True,
    },
    "files_written": [
        str(proof_path),
        str(milestone_path),
        str(audit_path),
    ],
    "files_touched_scope": "proof_json_milestone_markdown_audit_text_only",
    "compile_import_proof": {
        "python_files_touched": False,
        "compile_required": False,
        "import_required": False,
        "reason": "No Python project files were patched or created.",
    },
    "environment": {
        "cwd": str(pathlib.Path.cwd()),
        "python_executable": sys.executable,
        "selected_pybin": pybin,
        "python_version": platform.python_version(),
    },
    "git": {
        "head": git_head,
        "status_short": git_status,
    },
    "audit_artifact": str(audit_path),
}

proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")

milestone = f"""# {batch_id} — AI Patch Runner v0.1.3 Smoke Proof

UTC: {utc_ts}

## Result

Harmless audit-only smoke proof created.

## Confirmations

- AI Patch Runner v0.1.3 generated a command package.
- No target patch payload was executed.
- No project code was patched.
- No services were started.
- No broker calls were made.
- No orders were placed.
- No live Redis trading truth was written.
- Paper/live was not enabled.

## Safety Flags

- broker_calls_executed=false
- service_starts_executed=false
- live_redis_writes_executed=false
- paper_or_live_enabled=false

## Artifacts

- Proof JSON: `{proof_path}`
- Prewrite audit: `{audit_path}`

## Scope

Only proof, milestone, and audit artifacts were written.
"""
milestone_path.write_text(milestone, encoding="utf-8")
PY

"$PYBIN" - <<'PY'
import json
import os
import pathlib

proof_path = pathlib.Path(os.environ["PROOF_PATH"])
milestone_path = pathlib.Path(os.environ["MILESTONE_PATH"])

proof = json.loads(proof_path.read_text(encoding="utf-8"))
required_false = [
    ("safety_flags", "broker_calls_executed"),
    ("safety_flags", "service_starts_executed"),
    ("safety_flags", "live_redis_writes_executed"),
    ("safety_flags", "paper_or_live_enabled"),
]
for section, key in required_false:
    if proof.get(section, {}).get(key) is not False:
        raise SystemExit(f"Required false safety flag failed: {section}.{key}")

if proof.get("ai_patch_runner", {}).get("audit_only") is not True:
    raise SystemExit("audit_only was not true")
if proof.get("ai_patch_runner", {}).get("project_code_patched") is not False:
    raise SystemExit("project_code_patched was not false")
if not milestone_path.exists():
    raise SystemExit("milestone note missing")

print(f"SMOKE_PROOF_OK {proof_path} {milestone_path}")
PY
