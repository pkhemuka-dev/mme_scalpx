cd /home/Lenovo/scalpx/projects/mme_scalpx
set -euo pipefail

if [ -x ".venv/bin/python" ]; then
  PYBIN=".venv/bin/python"
else
  PYBIN="python3"
fi

export PYTHONPATH="/home/Lenovo/scalpx/projects/mme_scalpx${PYTHONPATH:+:$PYTHONPATH}"

mkdir -p run/proofs docs/milestones run/_code_backups run/audits

export SCALPX_BATCH_ID="AI-V012-SMOKE"
export SCALPX_PROOF_PATH="run/proofs/AI-V012-SMOKE.audit_smoke_proof.json"
export SCALPX_MILESTONE_PATH="docs/milestones/AI-V012-SMOKE.audit_smoke_milestone.md"
export SCALPX_AUDIT_PATH="run/audits/AI-V012-SMOKE.audit_smoke_audit.json"
export SCALPX_BACKUP_DIR="run/_code_backups/AI-V012-SMOKE"

mkdir -p "$SCALPX_BACKUP_DIR"

if [ -f "$SCALPX_PROOF_PATH" ]; then
  cp -a "$SCALPX_PROOF_PATH" "$SCALPX_BACKUP_DIR/$(basename "$SCALPX_PROOF_PATH").bak"
fi

if [ -f "$SCALPX_MILESTONE_PATH" ]; then
  cp -a "$SCALPX_MILESTONE_PATH" "$SCALPX_BACKUP_DIR/$(basename "$SCALPX_MILESTONE_PATH").bak"
fi

if [ -f "$SCALPX_AUDIT_PATH" ]; then
  cp -a "$SCALPX_AUDIT_PATH" "$SCALPX_BACKUP_DIR/$(basename "$SCALPX_AUDIT_PATH").bak"
fi

"$PYBIN" - <<'PY'
import json
import os
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

batch_id = os.environ["SCALPX_BATCH_ID"]
proof_path = Path(os.environ["SCALPX_PROOF_PATH"])
milestone_path = Path(os.environ["SCALPX_MILESTONE_PATH"])
audit_path = Path(os.environ["SCALPX_AUDIT_PATH"])
backup_dir = Path(os.environ["SCALPX_BACKUP_DIR"])

root = Path.cwd()

def run_readonly(cmd):
    try:
        proc = subprocess.run(
            cmd,
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=20,
            check=False,
        )
        return {
            "cmd": cmd,
            "returncode": proc.returncode,
            "stdout": proc.stdout[-8000:],
            "stderr": proc.stderr[-8000:],
        }
    except Exception as exc:
        return {
            "cmd": cmd,
            "returncode": None,
            "stdout": "",
            "stderr": f"{type(exc).__name__}: {exc}",
        }

started_at = datetime.now(timezone.utc).isoformat()

readonly_inspection = {
    "pwd": str(root),
    "python_executable": os.sys.executable,
    "python_version": platform.python_version(),
    "platform": platform.platform(),
    "git_rev_parse": run_readonly(["git", "rev-parse", "--show-toplevel"]),
    "git_head": run_readonly(["git", "rev-parse", "HEAD"]),
    "git_status_before_writing_proofs": run_readonly(["git", "status", "--short"]),
}

safety_flags = {
    "broker_calls_executed": False,
    "service_starts_executed": False,
    "live_redis_writes_executed": False,
    "paper_or_live_enabled": False,
}

negative_assertions = {
    "generated_package_only": True,
    "ai_patch_runner_version_declared_by_user": "v0.1.1",
    "target_smoke_subject": "AI Patch Runner v0.1.2",
    "runner_generated_package_but_did_not_execute_project_patch": True,
    "project_code_patched": False,
    "services_started": False,
    "broker_called": False,
    "orders_placed": False,
    "live_redis_trading_truth_written": False,
    "paper_trading_enabled": False,
    "live_trading_enabled": False,
    "paper_armed_enabled": False,
    "real_live_allowed_enabled": False,
    "controlled_paper_runtime_enabled": False,
    "systemctl_used": False,
    "nohup_used": False,
    "redis_live_mutation_commands_used": False,
}

compile_import_proof = {
    "python_project_files_touched": False,
    "required": False,
    "status": "not_applicable",
    "reason": "Audit-only smoke proof touched no project Python source files.",
}

outputs_to_write = [
    str(proof_path),
    str(milestone_path),
    str(audit_path),
]

proof = {
    "batch_id": batch_id,
    "proof_type": "audit_only_smoke",
    "created_at_utc": started_at,
    "root": str(root),
    "purpose": (
        "Harmless audit-only smoke proof that the AI runner generated a safe command "
        "package and that this package performs no project-code patching, no service "
        "starts, no broker calls, no live Redis trading-truth writes, and no paper/live enabling."
    ),
    "safety_flags": safety_flags,
    "negative_assertions": negative_assertions,
    "readonly_inspection": readonly_inspection,
    "files_intentionally_written": outputs_to_write,
    "files_intentionally_backed_up_if_preexisting": [
        str(backup_dir / (proof_path.name + ".bak")),
        str(backup_dir / (milestone_path.name + ".bak")),
        str(backup_dir / (audit_path.name + ".bak")),
    ],
    "project_code_patch": {
        "performed": False,
        "status": "not_performed_audit_only",
        "explanation": "Only proof and milestone artifacts are created or refreshed.",
    },
    "compile_import_proof": compile_import_proof,
}

audit = {
    "batch_id": batch_id,
    "audit_only": True,
    "created_at_utc": started_at,
    "readonly_inspection": readonly_inspection,
    "safety_flags": safety_flags,
    "negative_assertions": negative_assertions,
    "result": "safe_smoke_proof_created",
}

proof_path.parent.mkdir(parents=True, exist_ok=True)
milestone_path.parent.mkdir(parents=True, exist_ok=True)
audit_path.parent.mkdir(parents=True, exist_ok=True)

proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
audit_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")

milestone = f"""# {batch_id} Audit-Only Smoke Proof

Created UTC: {started_at}

## Scope

This is a harmless audit-only smoke proof for AI Patch Runner v0.1.2, generated from the AI Patch Runner v0.1.1 package-generation flow.

## Confirmations

- The AI runner generated a command package.
- The package did not patch project code.
- The package did not start services.
- The package did not call any broker.
- The package did not place orders.
- The package did not write live Redis trading truth.
- The package did not enable paper trading.
- The package did not enable live trading.
- The package did not enable paper_armed.
- The package did not use systemctl or nohup.
- The package only writes audit/proof artifacts under `run/proofs`, `run/audits`, and `docs/milestones`.

## Mandatory Safety Flags

```json
{json.dumps(safety_flags, indent=2, sort_keys=True)}
```

## Compile / Import Proof

Not applicable. No project Python source files were touched.

## Artifacts

- Proof JSON: `{proof_path}`
- Audit JSON: `{audit_path}`
- Milestone: `{milestone_path}`
"""

milestone_path.write_text(milestone, encoding="utf-8")

print(json.dumps({
    "ok": True,
    "batch_id": batch_id,
    "proof_path": str(proof_path),
    "audit_path": str(audit_path),
    "milestone_path": str(milestone_path),
    "safety_flags": safety_flags,
}, indent=2, sort_keys=True))
PY

"$PYBIN" - <<'PY'
import json
import os
from pathlib import Path

proof_path = Path(os.environ["SCALPX_PROOF_PATH"])
milestone_path = Path(os.environ["SCALPX_MILESTONE_PATH"])
audit_path = Path(os.environ["SCALPX_AUDIT_PATH"])

proof = json.loads(proof_path.read_text(encoding="utf-8"))
audit = json.loads(audit_path.read_text(encoding="utf-8"))
milestone = milestone_path.read_text(encoding="utf-8")

required_false_flags = [
    "broker_calls_executed",
    "service_starts_executed",
    "live_redis_writes_executed",
    "paper_or_live_enabled",
]

for key in required_false_flags:
    if proof["safety_flags"].get(key) is not False:
        raise SystemExit(f"Proof safety flag is not false: {key}")
    if audit["safety_flags"].get(key) is not False:
        raise SystemExit(f"Audit safety flag is not false: {key}")

if proof["project_code_patch"]["performed"] is not False:
    raise SystemExit("Project code patch unexpectedly marked as performed")

if proof["compile_import_proof"]["python_project_files_touched"] is not False:
    raise SystemExit("Python project files unexpectedly marked as touched")

if "did not patch project code" not in milestone:
    raise SystemExit("Milestone missing no-project-code-patch confirmation")

print(json.dumps({
    "ok": True,
    "validated": [
        str(proof_path),
        str(audit_path),
        str(milestone_path),
    ],
    "broker_calls_executed": False,
    "service_starts_executed": False,
    "live_redis_writes_executed": False,
    "paper_or_live_enabled": False,
}, indent=2, sort_keys=True))
PY