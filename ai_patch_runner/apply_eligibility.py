#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/home/Lenovo/scalpx/projects/mme_scalpx").resolve()
PYBIN = ROOT / ".venv" / "bin" / "python"
POLICY_CHECK = ROOT / "ai_patch_runner" / "policy" / "check_policy.py"


REQUIRED_BUNDLE_FILES = [
    "review_bundle_manifest.json",
    "human_approval_checklist.md",
    "sandbox.diff",
    "ai_patch_plan.json",
    "ai_classification.json",
    "sandbox_report.json",
    "policy_snapshot.json",
    "compile_summary.json",
]


FORBIDDEN_APPLY_PATH_PREFIXES = [
    "app/",
    "etc/",
    "bin/",
    "scripts/",
    "systemd/",
    "deployment/",
    "common/secrets/",
]

FORBIDDEN_DIFF_PATTERNS = [
    r"SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME\s*=\s*1",
    r"SCALPX_REAL_LIVE_ALLOWED\s*=\s*1",
    r"SCALPX_ALLOW_REAL_LIVE\s*=\s*1",
    r"redis-cli\s+.*\b(SET|HSET|XADD|DEL)\b",
    r"^\+?\s*nohup\b",
    r"^\+?\s*(sudo\s+)?systemctl\b",
    r"^\+?\s*(sudo\s+)?service\s+[A-Za-z0-9_.@-]+(?:\s+|$)",
    r"app\.mme_scalpx\.main",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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


def parse_diff_paths(diff_text: str) -> dict:
    paths = []
    for line in diff_text.splitlines():
        if line.startswith("--- real/"):
            paths.append(line[len("--- real/"):].strip())
        elif line.startswith("+++ sandbox/"):
            paths.append(line[len("+++ sandbox/"):].strip())

    unique = sorted(set(p for p in paths if p and p != "/dev/null"))
    forbidden = []
    for p in unique:
        for prefix in FORBIDDEN_APPLY_PATH_PREFIXES:
            if p.startswith(prefix):
                forbidden.append({"path": p, "prefix": prefix})

    return {
        "paths": unique,
        "forbidden_paths": forbidden,
        "only_low_risk_paths": not forbidden,
    }


def scan_diff_for_forbidden_commands(diff_text: str) -> list[dict]:
    findings = []
    for lineno, line in enumerate(diff_text.splitlines(), start=1):
        # Only inspect added lines and raw command-like lines.
        if not (line.startswith("+") and not line.startswith("+++")):
            continue
        text = line[1:]
        stripped = text.strip()
        if not stripped:
            continue
        if stripped.startswith(("#", "- ", "* ", "{", "}", "\"", "'", ":", ",")):
            continue
        for pat in FORBIDDEN_DIFF_PATTERNS:
            if re.search(pat, stripped, flags=re.IGNORECASE):
                findings.append({
                    "line": lineno,
                    "pattern": pat,
                    "text": stripped,
                })
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    bundle = (ROOT / args.bundle).resolve() if not Path(args.bundle).is_absolute() else Path(args.bundle).resolve()
    out = (ROOT / args.out).resolve() if not Path(args.out).is_absolute() else Path(args.out).resolve()

    allowed_bundle_root = ROOT / "ai_patch_runner" / "review_bundles"
    if not str(bundle).startswith(str(allowed_bundle_root)):
        raise SystemExit(f"Refusing bundle outside {allowed_bundle_root}: {bundle}")

    checks = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "apply_eligibility_version": "v0.4.1",
        "bundle": str(bundle),
        "required_files": {},
        "validations": {},
        "safety": {
            "applies_patch": False,
            "patches_real_project": False,
            "starts_services": False,
            "calls_broker": False,
            "writes_live_redis": False,
            "enables_paper_or_live": False,
        },
    }

    ok = True

    for name in REQUIRED_BUNDLE_FILES:
        path = bundle / name
        exists = path.exists() and path.stat().st_size > 0
        checks["required_files"][name] = {
            "path": str(path),
            "exists": exists,
            "sha256": sha256_file(path) if exists else None,
            "size_bytes": path.stat().st_size if exists else 0,
        }
        if not exists:
            ok = False

    if not ok:
        checks["eligibility"] = "NOT_ELIGIBLE"
        checks["reason"] = "missing required bundle files"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(checks, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"eligibility": checks["eligibility"], "out": str(out)}, indent=2))
        return 2

    manifest = load_json(bundle / "review_bundle_manifest.json")
    ai_plan = load_json(bundle / "ai_patch_plan.json")
    ai_classification = load_json(bundle / "ai_classification.json")
    sandbox_report = load_json(bundle / "sandbox_report.json")
    compile_summary = load_json(bundle / "compile_summary.json")
    policy_snapshot = load_json(bundle / "policy_snapshot.json")
    checklist_text = (bundle / "human_approval_checklist.md").read_text(encoding="utf-8")
    diff_text = (bundle / "sandbox.diff").read_text(encoding="utf-8")

    diff_paths = parse_diff_paths(diff_text)
    forbidden_diff_commands = scan_diff_for_forbidden_commands(diff_text)

    policy_check = run_cmd([str(PYBIN), str(POLICY_CHECK), "--command-file", str(bundle / "sandbox.diff"), "--json"])
    try:
        policy_check_payload = json.loads(policy_check["stdout"])
    except Exception:
        policy_check_payload = None

    validations = {
        "manifest_verdict_pass": manifest.get("verdict") == "PASS",
        "manifest_bundle_only": manifest.get("safety", {}).get("bundle_only") is True,
        "manifest_not_applied": manifest.get("safety", {}).get("applied_to_real_project") is False,
        "manifest_no_execution": manifest.get("safety", {}).get("executes_generated_scripts") is False,
        "manifest_no_services": manifest.get("safety", {}).get("starts_services") is False,
        "manifest_no_broker": manifest.get("safety", {}).get("calls_broker") is False,
        "manifest_no_redis": manifest.get("safety", {}).get("writes_live_redis") is False,
        "manifest_no_paper_live": manifest.get("safety", {}).get("enables_paper_or_live") is False,

        "ai_plan_validation_ok": ai_plan.get("validation_ok") is True,
        "ai_plan_target_low_risk": ai_plan.get("plan", {}).get("target_rel", "").startswith("ai_patch_runner/"),
        "ai_plan_sandbox_only": ai_plan.get("plan", {}).get("safety", {}).get("sandbox_only") is True,
        "ai_plan_no_real_touch": ai_plan.get("plan", {}).get("safety", {}).get("touches_real_project") is False,

        "ai_classification_pass": ai_classification.get("classification", {}).get("verdict") == "PASS",

        "sandbox_report_pass": sandbox_report.get("verdict") == "PASS",
        "sandbox_report_not_applied": sandbox_report.get("safety", {}).get("applied_to_real_project") is False,
        "sandbox_report_real_project_not_patched": sandbox_report.get("real_project_integrity", {}).get("real_project_patched") is False,
        "sandbox_report_real_target_absent": sandbox_report.get("real_project_integrity", {}).get("real_target_exists") is False,

        "compile_summary_ok": compile_summary.get("compile_ok") is True,
        "policy_snapshot_diff_check_ok": policy_snapshot.get("bundle_time_diff_policy_check", {}).get("payload", {}).get("ok") is True,
        "bundle_time_policy_check_ok": bool(policy_check_payload and policy_check_payload.get("ok") is True),

        "checklist_contains_no_direct_auto_patch_warning": "does not authorize direct live-system auto-patching" in checklist_text,
        "diff_nonempty": bool(diff_text.strip()),
        "diff_only_low_risk_paths": diff_paths["only_low_risk_paths"],
        "diff_no_forbidden_commands": not forbidden_diff_commands,
    }

    checks["validations"] = validations
    checks["diff_paths"] = diff_paths
    checks["forbidden_diff_commands"] = forbidden_diff_commands
    checks["bundle_time_policy_check"] = {
        "command_result": policy_check,
        "payload": policy_check_payload,
    }

    all_valid = all(validations.values())

    if all_valid:
        checks["eligibility"] = "ELIGIBLE_FOR_MANUAL_APPLY"
        checks["reason"] = "review bundle is eligible for future human-approved low-risk manual apply only"
        return_code = 0
    else:
        checks["eligibility"] = "NOT_ELIGIBLE"
        checks["reason"] = "one or more eligibility validations failed"
        return_code = 2

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(checks, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "apply_eligibility_version": "v0.4.1",
        "bundle": str(bundle),
        "out": str(out),
        "eligibility": checks["eligibility"],
        "all_valid": all_valid,
        "diff_paths": diff_paths["paths"],
    }, indent=2))

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
