cd /home/Lenovo/scalpx/projects/mme_scalpx
set -euo pipefail

PYBIN=".venv/bin/python"
if [ ! -x "$PYBIN" ]; then
  PYBIN="python3"
fi

export PYTHONPATH="$(pwd)${PYTHONPATH:+:$PYTHONPATH}"

mkdir -p run/proofs docs/milestones run/_code_backups run/audits

BATCH_ID="AI-V01-SMOKE"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
PROOF_PATH="run/proofs/${BATCH_ID}_${TS}.json"
MILESTONE_PATH="docs/milestones/${BATCH_ID}_${TS}.md"
AUDIT_PATH="run/audits/${BATCH_ID}_${TS}.txt"
BACKUP_DIR="run/_code_backups/${BATCH_ID}_${TS}"
mkdir -p "$BACKUP_DIR"

{
  echo "batch_id=${BATCH_ID}"
  echo "timestamp_utc=${TS}"
  echo "pwd=$(pwd)"
  echo "python_bin=${PYBIN}"
  echo "git_status_before:"
  git status --short || true
  echo
  echo "existing_target_paths_before:"
  [ -e "$PROOF_PATH" ] && ls -l "$PROOF_PATH" || echo "proof_path_absent"
  [ -e "$MILESTONE_PATH" ] && ls -l "$MILESTONE_PATH" || echo "milestone_path_absent"
} > "$AUDIT_PATH"

if [ -e "$PROOF_PATH" ]; then
  cp -a "$PROOF_PATH" "$BACKUP_DIR/$(basename "$PROOF_PATH").bak"
fi
if [ -e "$MILESTONE_PATH" ]; then
  cp -a "$MILESTONE_PATH" "$BACKUP_DIR/$(basename "$MILESTONE_PATH").bak"
fi

"$PYBIN" - <<PY
import json
import os
import pathlib
import subprocess
import hashlib
from datetime import datetime, timezone

batch_id = os.environ.get("BATCH_ID", "AI-V01-SMOKE")
ts = os.environ.get("TS", datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))

proof_path = pathlib.Path(os.environ.get("PROOF_PATH", f"run/proofs/{batch_id}_{ts}.json"))
milestone_path = pathlib.Path(os.environ.get("MILESTONE_PATH", f"docs/milestones/{batch_id}_{ts}.md"))
audit_path = pathlib.Path(os.environ.get("AUDIT_PATH", f"run/audits/{batch_id}_{ts}.txt"))

def run_capture(cmd):
    try:
        p = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        return {
            "cmd": cmd,
            "returncode": p.returncode,
            "stdout": p.stdout[-4000:],
            "stderr": p.stderr[-4000:],
        }
    except Exception as exc:
        return {"cmd": cmd, "error": repr(exc)}

for p in [proof_path.parent, milestone_path.parent, audit_path.parent]:
    p.mkdir(parents=True, exist_ok=True)

forbidden_env_names = [
    "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
    "SCALPX_REAL_LIVE_ALLOWED",
    "SCALPX_ALLOW_REAL_LIVE",
    "paper_armed",
]
forbidden_env_observed = {
    name: os.environ.get(name)
    for name in forbidden_env_names
    if os.environ.get(name) not in (None, "", "0", "false", "False", "FALSE")
}

proof = {
    "batch_id": batch_id,
    "kind": "audit_only_smoke_proof",
    "component": "AI Patch Runner v0.1",
    "created_at_utc": datetime.now(timezone.utc).isoformat(),
    "purpose": (
        "Harmless smoke proof confirming the AI runner generated a safe command package "
        "and that this package only writes proof artifacts."
    ),
    "attestations": {
        "ai_runner_generated_package": True,
        "ai_runner_executed_generated_patch": False,
        "project_code_patched": False,
        "broker_calls_executed": False,
        "service_starts_executed": False,
        "live_redis_writes_executed": False,
        "paper_or_live_enabled": False,
        "orders_placed": False,
        "broker_login_called": False,
        "nohup_used": False,
        "systemctl_used": False,
        "paper_armed_enabled": False,
        "real_live_trading_enabled": False,
        "scalpx_allow_controlled_paper_runtime_set_to_1": False,
        "scalpx_real_live_allowed_set_to_1": False,
        "scalpx_allow_real_live_set_to_1": False,
        "execution_risk_broker_main_live_control_files_patched": False,
        "python_files_touched": False,
        "compile_import_proof_required": False
    },
    "artifacts_written": {
        "proof_json": str(proof_path),
        "milestone_markdown": str(milestone_path),
        "audit_log": str(audit_path)
    },
    "inspection": {
        "git_status_short": run_capture(["git", "status", "--short"]),
        "git_rev_parse_head": run_capture(["git", "rev-parse", "HEAD"]),
        "forbidden_runtime_env_observed": forbidden_env_observed
    },
    "safety_result": {
        "safe": True,
        "audit_only": True,
        "no_project_code_patch": True,
        "no_live_trading_mutation": True
    }
}

proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\\n", encoding="utf-8")

milestone = f"""# {batch_id} — AI Patch Runner v0.1 Smoke Proof

Timestamp UTC: {proof['created_at_utc']}

## Result

Audit-only smoke proof created.

## Safety Attestations

- AI Patch Runner v0.1 generated a command package: yes
- Generated patch/package executed by runner: no
- Project code patched: no
- Services started: no
- Broker called: no
- Broker login called: no
- Orders placed: no
- Live Redis trading truth written: no
- Paper/live enabled: no
- paper_armed enabled: no
- Real live trading enabled: no
- Forbidden live/paper env flags set by this package: no
- Python files touched: no
- Compile/import proof required: no

## Artifacts

- Proof JSON: `{proof_path}`
- Audit log: `{audit_path}`

## Notes

This package is intentionally harmless and proof-oriented. It only creates audit/proof
artifacts under `run/proofs`, `run/audits`, and `docs/milestones`.
"""
milestone_path.write_text(milestone, encoding="utf-8")

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

proof["artifact_sha256"] = {
    "proof_json_pre_final": sha256_file(proof_path),
    "milestone_markdown": sha256_file(milestone_path),
    "audit_log": sha256_file(audit_path),
}
proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
PY

"$PYBIN" -m json.tool "$PROOF_PATH" >/dev/null

{
  echo
  echo "git_status_after:"
  git status --short || true
  echo
  echo "created_artifacts:"
  ls -l "$PROOF_PATH" "$MILESTONE_PATH" "$AUDIT_PATH"
  echo
  echo "proof_json_validated=true"
  echo "broker_calls_executed=false"
  echo "service_starts_executed=false"
  echo "live_redis_writes_executed=false"
  echo "paper_or_live_enabled=false"
} >> "$AUDIT_PATH"

echo "AI-V01-SMOKE audit-only smoke proof complete:"
echo "  proof: $PROOF_PATH"
echo "  milestone: $MILESTONE_PATH"
echo "  audit: $AUDIT_PATH"
