cd /home/Lenovo/scalpx/projects/mme_scalpx
set -euo pipefail

if [ -x ".venv/bin/python" ]; then
  PYBIN=".venv/bin/python"
else
  PYBIN="python3"
fi

export PYTHONPATH="$(pwd)${PYTHONPATH:+:${PYTHONPATH}}"

mkdir -p run/proofs docs/milestones run/_code_backups run/audits

BATCH_ID="AI-V011-SMOKE"
RUNNER_VERSION="AI Patch Runner v0.1.1"
UTC_TS="$(date -u +%Y%m%dT%H%M%SZ)"
AUDIT_PATH="run/audits/${BATCH_ID}_${UTC_TS}_preflight_audit.txt"
PROOF_PATH="run/proofs/${BATCH_ID}_${UTC_TS}_smoke_proof.json"
MILESTONE_PATH="docs/milestones/${BATCH_ID}_${UTC_TS}_smoke_note.md"
BACKUP_MANIFEST_PATH="run/_code_backups/${BATCH_ID}_${UTC_TS}_backup_manifest.txt"

{
  echo "batch_id=${BATCH_ID}"
  echo "runner_version=${RUNNER_VERSION}"
  echo "utc_ts=${UTC_TS}"
  echo "pwd=$(pwd)"
  echo "python_bin=${PYBIN}"
  echo "git_top_level=$(git rev-parse --show-toplevel 2>/dev/null || true)"
  echo "git_head=$(git rev-parse HEAD 2>/dev/null || true)"
  echo "git_status_short_begin"
  git status --short 2>/dev/null || true
  echo "git_status_short_end"
  echo "existing_smoke_artifacts_begin"
  find run/proofs docs/milestones run/audits run/_code_backups -maxdepth 1 -type f -name "*${BATCH_ID}*" -print 2>/dev/null | sort || true
  echo "existing_smoke_artifacts_end"
  echo "safety_inspection=commands limited to local filesystem proof/audit creation; no services, broker, orders, or Redis writes"
} > "$AUDIT_PATH"

{
  echo "batch_id=${BATCH_ID}"
  echo "utc_ts=${UTC_TS}"
  echo "backup_reason=audit-only smoke package; no project code files targeted or patched"
  echo "backed_up_project_code_files_count=0"
  echo "backed_up_project_code_files=[]"
} > "$BACKUP_MANIFEST_PATH"

export BATCH_ID
export RUNNER_VERSION
export UTC_TS
export AUDIT_PATH
export PROOF_PATH
export MILESTONE_PATH
export BACKUP_MANIFEST_PATH

"$PYBIN" - <<'PY'
import json
import os
import pathlib
import subprocess
from datetime import datetime, timezone

batch_id = os.environ["BATCH_ID"]
runner_version = os.environ["RUNNER_VERSION"]
utc_ts = os.environ["UTC_TS"]
audit_path = pathlib.Path(os.environ["AUDIT_PATH"])
proof_path = pathlib.Path(os.environ["PROOF_PATH"])
milestone_path = pathlib.Path(os.environ["MILESTONE_PATH"])
backup_manifest_path = pathlib.Path(os.environ["BACKUP_MANIFEST_PATH"])

def git_value(args):
    try:
        return subprocess.check_output(["git", *args], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None

dangerous_env_names = [
    "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
    "SCALPX_REAL_LIVE_ALLOWED",
    "SCALPX_ALLOW_REAL_LIVE",
]

dangerous_env_observed = {name: os.environ.get(name) for name in dangerous_env_names}

proof = {
    "schema": "mme_scalpx.ai_patch_runner_smoke_proof.v1",
    "batch_id": batch_id,
    "runner_version": runner_version,
    "created_at_utc": datetime.now(timezone.utc).isoformat(),
    "package_timestamp_token": utc_ts,
    "mode": "audit_only_smoke",
    "goal": "Harmless smoke proof for AI Patch Runner v0.1.1 package generation safety.",
    "assertions": {
        "ai_runner_generated_command_package": True,
        "ai_runner_executed_generated_package": False,
        "project_code_patched": False,
        "project_code_patch_attempted": False,
        "broker_calls_executed": False,
        "orders_placed": False,
        "service_starts_executed": False,
        "nohup_used": False,
        "systemctl_used": False,
        "live_redis_writes_executed": False,
        "redis_cli_set_hset_xadd_del_executed_on_live_trading_keys": False,
        "paper_or_live_enabled": False,
        "paper_armed_enabled": False,
        "real_live_trading_enabled": False,
        "controlled_paper_runtime_enabled_by_package": False,
        "compile_import_proof_required": False,
        "compile_import_proof_reason": "No Python project files were touched by this audit-only smoke package."
    },
    "safety_flags": {
        "broker_calls_executed": False,
        "service_starts_executed": False,
        "live_redis_writes_executed": False,
        "paper_or_live_enabled": False
    },
    "forbidden_environment_variables": {
        "package_set_any_forbidden_variable": False,
        "forbidden_variables_checked": dangerous_env_names,
        "observed_values_in_process_environment": dangerous_env_observed,
        "note": "Observed values are recorded only for audit context; this package does not set or enable them."
    },
    "files_created": {
        "proof_json": str(proof_path),
        "milestone_markdown": str(milestone_path),
        "preflight_audit": str(audit_path),
        "backup_manifest": str(backup_manifest_path)
    },
    "backups": {
        "project_code_files_backed_up": 0,
        "reason": "No project code files were targeted or patched; only audit/proof artifacts were created."
    },
    "repository_context": {
        "git_top_level": git_value(["rev-parse", "--show-toplevel"]),
        "git_head": git_value(["rev-parse", "HEAD"]),
        "git_branch": git_value(["rev-parse", "--abbrev-ref", "HEAD"])
    },
    "heredoc_compliance": {
        "embedded_python_heredocs_single_quoted": True,
        "required_python_delimiter_form": "<<'PY'"
    }
}

proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")

milestone = f"""# {batch_id} — Audit-Only Smoke Proof

- Runner: {runner_version}
- Created UTC: {proof["created_at_utc"]}
- Mode: audit-only smoke
- Proof JSON: `{proof_path}`
- Preflight audit: `{audit_path}`
- Backup manifest: `{backup_manifest_path}`

## Safety confirmations

- AI runner generated a command package: **yes**
- AI runner executed the generated package: **no**
- Project code patched: **no**
- Services started: **no**
- Broker called: **no**
- Orders placed: **no**
- Live Redis trading truth written: **no**
- Paper/live enabled: **no**
- `paper_armed` enabled: **no**
- Forbidden live/paper env vars set by this package: **no**

## Required safety flags

```text
broker_calls_executed=false
service_starts_executed=false
live_redis_writes_executed=false
paper_or_live_enabled=false
```

## Compile/import proof

Not required: this package did not touch Python project files.

## Heredoc compliance

Embedded Python heredocs use the required single-quoted delimiter form: `<<'PY'`.
"""

milestone_path.write_text(milestone, encoding="utf-8")

print(json.dumps({
    "ok": True,
    "batch_id": batch_id,
    "proof_path": str(proof_path),
    "milestone_path": str(milestone_path),
    "audit_path": str(audit_path),
    "backup_manifest_path": str(backup_manifest_path),
    "safety_flags": proof["safety_flags"],
}, indent=2, sort_keys=True))
PY

test -s "$PROOF_PATH"
test -s "$MILESTONE_PATH"
test -s "$AUDIT_PATH"
test -s "$BACKUP_MANIFEST_PATH"

echo "AI-V011-SMOKE audit-only proof created:"
echo "  proof: $PROOF_PATH"
echo "  milestone: $MILESTONE_PATH"
echo "  audit: $AUDIT_PATH"
echo "  backup_manifest: $BACKUP_MANIFEST_PATH"
