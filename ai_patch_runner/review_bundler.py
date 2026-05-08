#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/home/Lenovo/scalpx/projects/mme_scalpx").resolve()
PYBIN = ROOT / ".venv" / "bin" / "python"
POLICY_CHECK = ROOT / "ai_patch_runner" / "policy" / "check_policy.py"
POLICY_JSON = ROOT / "ai_patch_runner" / "policy" / "ai_patch_policy.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_cmd(cmd: list[str]) -> dict:
    try:
        p = subprocess.run(
            cmd,
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=45,
        )
        return {
            "cmd": cmd,
            "returncode": p.returncode,
            "stdout": p.stdout[-8000:],
            "stderr": p.stderr[-8000:],
        }
    except Exception as exc:
        return {
            "cmd": cmd,
            "returncode": None,
            "stdout": "",
            "stderr": repr(exc),
        }


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def copy_artifact(src: Path, dst: Path) -> dict:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return {
        "source": str(src),
        "bundle_path": str(dst),
        "sha256": sha256_file(dst),
        "size_bytes": dst.stat().st_size,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sandbox-dir", required=True)
    parser.add_argument("--bundle-root", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--checklist", required=True)
    parser.add_argument("--compile-summary", required=True)
    parser.add_argument("--policy-snapshot", required=True)
    args = parser.parse_args()

    sandbox_dir = (ROOT / args.sandbox_dir).resolve() if not Path(args.sandbox_dir).is_absolute() else Path(args.sandbox_dir).resolve()
    bundle_root = (ROOT / args.bundle_root).resolve() if not Path(args.bundle_root).is_absolute() else Path(args.bundle_root).resolve()
    manifest_path = (ROOT / args.manifest).resolve() if not Path(args.manifest).is_absolute() else Path(args.manifest).resolve()
    checklist_path = (ROOT / args.checklist).resolve() if not Path(args.checklist).is_absolute() else Path(args.checklist).resolve()
    compile_summary_path = (ROOT / args.compile_summary).resolve() if not Path(args.compile_summary).is_absolute() else Path(args.compile_summary).resolve()
    policy_snapshot_path = (ROOT / args.policy_snapshot).resolve() if not Path(args.policy_snapshot).is_absolute() else Path(args.policy_snapshot).resolve()

    allowed_bundle_root = ROOT / "ai_patch_runner" / "review_bundles"
    if not str(bundle_root).startswith(str(allowed_bundle_root)):
        raise SystemExit(f"Refusing bundle outside {allowed_bundle_root}: {bundle_root}")

    required = {
        "sandbox_diff": sandbox_dir / "sandbox.diff",
        "sandbox_report": sandbox_dir / "sandbox_report.json",
        "ai_patch_plan": sandbox_dir / "ai_patch_plan.json",
        "ai_classification": sandbox_dir / "ai_classification.json",
    }

    missing = [str(p) for p in required.values() if not p.exists()]
    if missing:
        raise SystemExit(f"Missing required sandbox artifacts: {missing}")

    sandbox_report = load_json(required["sandbox_report"])
    ai_plan = load_json(required["ai_patch_plan"])
    ai_classification = load_json(required["ai_classification"])

    # Validate latest sandbox result before bundling.
    validations = {
        "sandbox_report_verdict_pass": sandbox_report.get("verdict") == "PASS",
        "ai_plan_validation_ok": ai_plan.get("validation_ok") is True,
        "ai_classification_pass": ai_classification.get("classification", {}).get("verdict") == "PASS",
        "diff_nonempty": sandbox_report.get("diff", {}).get("diff_nonempty") is True,
        "diff_policy_check_allowed": sandbox_report.get("diff_policy_check", {}).get("allowed") is True,
        "real_project_patched_false": sandbox_report.get("real_project_integrity", {}).get("real_project_patched") is False,
        "real_target_exists_false": sandbox_report.get("real_project_integrity", {}).get("real_target_exists") is False,
        "sandbox_only_true": sandbox_report.get("safety", {}).get("sandbox_only") is True,
        "applied_to_real_project_false": sandbox_report.get("safety", {}).get("applied_to_real_project") is False,
        "started_services_false": sandbox_report.get("safety", {}).get("started_services") is False,
        "called_broker_false": sandbox_report.get("safety", {}).get("called_broker") is False,
        "wrote_live_redis_false": sandbox_report.get("safety", {}).get("wrote_live_redis") is False,
        "enabled_paper_or_live_false": sandbox_report.get("safety", {}).get("enabled_paper_or_live") is False,
    }

    compile_results = sandbox_report.get("compile_results", {})
    compile_ok = bool(compile_results) and all(v.get("returncode") == 0 for v in compile_results.values())
    validations["compile_results_ok"] = compile_ok

    all_valid = all(validations.values())

    # Policy-check the diff again at bundle time.
    policy_diff_check = run_cmd([str(PYBIN), str(POLICY_CHECK), "--command-file", str(required["sandbox_diff"]), "--json"])
    policy_diff_payload = None
    try:
        policy_diff_payload = json.loads(policy_diff_check["stdout"])
    except Exception:
        policy_diff_payload = None

    if not policy_diff_payload or policy_diff_payload.get("ok") is not True:
        all_valid = False

    bundle_root.mkdir(parents=True, exist_ok=True)

    copied = {
        name: copy_artifact(src, bundle_root / src.name)
        for name, src in required.items()
    }

    policy_snapshot = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "policy_json": load_json(POLICY_JSON),
        "policy_json_sha256": sha256_file(POLICY_JSON),
        "policy_check_sha256": sha256_file(POLICY_CHECK),
        "bundle_time_diff_policy_check": {
            "command_result": policy_diff_check,
            "payload": policy_diff_payload,
        },
    }
    policy_snapshot_path.write_text(json.dumps(policy_snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    compile_summary = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "compile_ok": compile_ok,
        "compile_results": compile_results,
    }
    compile_summary_path.write_text(json.dumps(compile_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    copied["policy_snapshot"] = {
        "source": "generated",
        "bundle_path": str(policy_snapshot_path),
        "sha256": sha256_file(policy_snapshot_path),
        "size_bytes": policy_snapshot_path.stat().st_size,
    }
    copied["compile_summary"] = {
        "source": "generated",
        "bundle_path": str(compile_summary_path),
        "sha256": sha256_file(compile_summary_path),
        "size_bytes": compile_summary_path.stat().st_size,
    }

    checklist = f"""# AI Patch Runner v0.4 Human Approval Checklist

Generated UTC: {datetime.now(timezone.utc).isoformat()}

## Bundle Scope

This bundle packages a sandbox-only AI-generated patch result for human review.

Sandbox source:

`{sandbox_dir}`

Bundle root:

`{bundle_root}`

## Required Checks Before Any Real Apply

Do not apply anything unless every box is checked manually.

- [ ] I confirm this bundle is for review only.
- [ ] I confirm no patch has been applied to the real project by the runner.
- [ ] I reviewed `sandbox.diff`.
- [ ] I reviewed `ai_patch_plan.json`.
- [ ] I reviewed `ai_classification.json`.
- [ ] I reviewed `sandbox_report.json`.
- [ ] I reviewed `policy_snapshot.json`.
- [ ] I reviewed `compile_summary.json`.
- [ ] I confirm the patch touches only allowed low-risk paths.
- [ ] I confirm no `app/`, `etc/`, `bin/`, `scripts/`, `systemd/`, `deployment/`, or `common/secrets/` path is being auto-applied.
- [ ] I confirm no broker/login/order/service-start/live-Redis/paper/live action exists.
- [ ] I confirm rollback/backups are available before any future manual apply.
- [ ] I understand v0.4 does not authorize direct live-system auto-patching.

## Bundle Validation Summary

- sandbox_report_verdict_pass={validations["sandbox_report_verdict_pass"]}
- ai_plan_validation_ok={validations["ai_plan_validation_ok"]}
- ai_classification_pass={validations["ai_classification_pass"]}
- diff_nonempty={validations["diff_nonempty"]}
- diff_policy_check_allowed={validations["diff_policy_check_allowed"]}
- real_project_patched_false={validations["real_project_patched_false"]}
- real_target_exists_false={validations["real_target_exists_false"]}
- compile_results_ok={validations["compile_results_ok"]}

## Safety Status

- broker_calls_executed=false
- service_starts_executed=false
- live_redis_writes_executed=false
- paper_or_live_enabled=false
- applied_to_real_project=false

## Decision

- [ ] APPROVE FOR MANUAL LOW-RISK APPLY LATER
- [ ] REJECT
- [ ] NEEDS MORE AUDIT

Reviewer:

Date:
"""
    checklist_path.write_text(checklist, encoding="utf-8")

    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "review_bundler_version": "v0.4",
        "bundle_root": str(bundle_root),
        "sandbox_dir": str(sandbox_dir),
        "verdict": "PASS" if all_valid else "FAIL",
        "validations": validations,
        "policy_diff_check_ok": bool(policy_diff_payload and policy_diff_payload.get("ok") is True),
        "artifacts": copied,
        "human_checklist": str(checklist_path),
        "safety": {
            "bundle_only": True,
            "applied_to_real_project": False,
            "executes_generated_scripts": False,
            "starts_services": False,
            "calls_broker": False,
            "writes_live_redis": False,
            "enables_paper_or_live": False,
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "review_bundler_version": "v0.4",
        "bundle_root": str(bundle_root),
        "manifest": str(manifest_path),
        "checklist": str(checklist_path),
        "verdict": manifest["verdict"],
    }, indent=2))

    return 0 if manifest["verdict"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
