#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI


ROOT = Path("/home/Lenovo/scalpx/projects/mme_scalpx").resolve()
PYBIN = ROOT / ".venv" / "bin" / "python"
POLICY_CHECK = ROOT / "ai_patch_runner" / "policy" / "check_policy.py"

SANDBOX_TARGET_REL = "ai_patch_runner/SANDBOX_AI_PATCH_NOTE.md"

ALLOWED_COPY_FILES = [
    "ai_patch_runner/generate_command_package.py",
    "ai_patch_runner/classify_run_output.py",
    "ai_patch_runner/runner_health_check.py",
    "ai_patch_runner/sandbox_patcher.py",
    "ai_patch_runner/policy/check_policy.py",
    "ai_patch_runner/policy/ai_patch_policy.json",
    "ai_patch_runner/policy/ai_patch_policy.md",
]


SYSTEM_PROMPT = """
You are generating a tiny AI Patch Runner sandbox-only patch plan.

Return ONLY valid JSON. No markdown. No prose.

Schema:
{
  "target_rel": "ai_patch_runner/SANDBOX_AI_PATCH_NOTE.md",
  "operation": "write_text",
  "content": "markdown content",
  "reason": "short reason",
  "safety": {
    "sandbox_only": true,
    "touches_real_project": false,
    "starts_services": false,
    "calls_broker": false,
    "writes_live_redis": false,
    "enables_paper_or_live": false
  }
}

Hard rules:
- target_rel must be exactly ai_patch_runner/SANDBOX_AI_PATCH_NOTE.md
- operation must be write_text
- content must be harmless markdown only
- do not include shell commands
- do not include Redis commands
- do not include broker/login/order instructions
- do not include paper/live enablement flags
"""


CLASSIFIER_PROMPT = """
You are classifying an MME-ScalpX sandbox-only AI patch run.

Return ONLY valid JSON:
{
  "verdict": "PASS" | "FAIL" | "UNCLEAR",
  "reason": "short reason",
  "evidence": ["short evidence"],
  "safety_flags": {
    "real_project_patched": true/false,
    "broker_calls_detected": true/false,
    "service_starts_detected": true/false,
    "live_redis_writes_detected": true/false,
    "paper_or_live_enabled": true/false
  },
  "next_action": "STOP" | "NEXT_BATCH" | "REPAIR_PATCH" | "AUDIT_MORE"
}

PASS only if sandbox-only patch succeeded, diff exists, compile checks pass, and real project was not patched.
"""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_cmd(cmd: list[str], cwd: Path | None = None) -> dict:
    try:
        p = subprocess.run(
            cmd,
            cwd=str(cwd or ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=60,
        )
        return {
            "cmd": cmd,
            "returncode": p.returncode,
            "stdout": p.stdout[-10000:],
            "stderr": p.stderr[-10000:],
        }
    except Exception as exc:
        return {
            "cmd": cmd,
            "returncode": None,
            "stdout": "",
            "stderr": repr(exc),
        }


def extract_json(text: str) -> dict:
    s = text.strip()
    if s.startswith("```"):
        lines = s.splitlines()
        if len(lines) >= 2 and lines[0].strip().startswith("```") and lines[-1].strip() == "```":
            s = "\n".join(lines[1:-1]).strip()
    start = s.find("{")
    end = s.rfind("}")
    if start < 0 or end < start:
        raise ValueError(f"No JSON object found in model output: {text[:500]}")
    return json.loads(s[start:end + 1])


def policy_check_path(path: str) -> dict:
    result = run_cmd([str(PYBIN), str(POLICY_CHECK), "--path", path, "--json"])
    payload = None
    try:
        payload = json.loads(result["stdout"])
    except Exception:
        payload = None
    return {
        "path": path,
        "command_result": result,
        "payload": payload,
        "allowed": bool(payload and payload.get("ok") is True),
    }


def policy_check_command_file(path: Path) -> dict:
    result = run_cmd([str(PYBIN), str(POLICY_CHECK), "--command-file", str(path), "--json"])
    payload = None
    try:
        payload = json.loads(result["stdout"])
    except Exception:
        payload = None
    return {
        "path": str(path),
        "command_result": result,
        "payload": payload,
        "allowed": bool(payload and payload.get("ok") is True),
    }


def ensure_allowed(paths: list[str]) -> list[dict]:
    checks = []
    for rel in paths:
        check = policy_check_path(rel)
        checks.append(check)
        if not check["allowed"]:
            raise SystemExit(f"Policy blocked path: {rel}")
    return checks


def copy_files(files: list[str], sandbox_project: Path) -> dict:
    copied = {}
    for rel in files:
        src = ROOT / rel
        dst = sandbox_project / rel
        if not src.exists():
            raise SystemExit(f"Missing source file: {rel}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied[rel] = {
            "source": str(src),
            "sandbox": str(dst),
            "sha256_before": sha256_file(src),
            "sha256_sandbox_initial": sha256_file(dst),
        }
    return copied


def validate_ai_plan(plan: dict) -> list[str]:
    findings = []

    if plan.get("target_rel") != SANDBOX_TARGET_REL:
        findings.append("target_rel_not_allowed")
    if plan.get("operation") != "write_text":
        findings.append("operation_not_allowed")

    content = plan.get("content", "")
    if not isinstance(content, str) or not content.strip():
        findings.append("content_missing")

    forbidden_patterns = [
        r"\bnohup\b",
        r"\bsystemctl\b",
        r"app\.mme_scalpx\.main",
        r"redis-cli\s+.*\b(SET|HSET|XADD|DEL)\b",
        r"SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME\s*=\s*1",
        r"SCALPX_REAL_LIVE_ALLOWED\s*=\s*1",
        r"SCALPX_ALLOW_REAL_LIVE\s*=\s*1",
        r"\border\b",
        r"\bbroker\b.*\blogin\b",
    ]
    scan_text = json.dumps(plan, sort_keys=True)
    for pat in forbidden_patterns:
        if re.search(pat, scan_text, re.I):
            findings.append(f"forbidden_pattern:{pat}")

    safety = plan.get("safety", {})
    expected = {
        "sandbox_only": True,
        "touches_real_project": False,
        "starts_services": False,
        "calls_broker": False,
        "writes_live_redis": False,
        "enables_paper_or_live": False,
    }
    for k, v in expected.items():
        if safety.get(k) is not v:
            findings.append(f"safety_flag_invalid:{k}")

    return findings


def apply_ai_plan_to_sandbox(plan: dict, sandbox_project: Path) -> dict:
    target_rel = plan["target_rel"]
    target = sandbox_project / target_rel
    if not str(target.resolve()).startswith(str(sandbox_project.resolve())):
        raise SystemExit("Resolved target escapes sandbox")

    target.parent.mkdir(parents=True, exist_ok=True)
    before_exists = target.exists()
    before = target.read_text(encoding="utf-8") if target.exists() else ""
    target.write_text(plan["content"].rstrip() + "\n", encoding="utf-8")

    return {
        "target_rel": target_rel,
        "target_path": str(target),
        "before_exists": before_exists,
        "before_sha256": hashlib.sha256(before.encode("utf-8")).hexdigest() if before_exists else None,
        "after_sha256": sha256_file(target),
    }


def make_diff(files: list[str], sandbox_project: Path, extra_paths: list[str], diff_path: Path) -> dict:
    chunks: list[str] = []
    compared = {}
    for rel in list(files) + list(extra_paths):
        real_path = ROOT / rel
        sand_path = sandbox_project / rel
        real_lines = real_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True) if real_path.exists() else []
        sand_lines = sand_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True) if sand_path.exists() else []

        diff = list(difflib.unified_diff(
            real_lines,
            sand_lines,
            fromfile=f"real/{rel}",
            tofile=f"sandbox/{rel}",
        ))
        if diff:
            chunks.extend(diff)
        compared[rel] = {
            "different": bool(diff),
            "real_exists": real_path.exists(),
            "sandbox_exists": sand_path.exists(),
        }

    diff_path.parent.mkdir(parents=True, exist_ok=True)
    diff_path.write_text("".join(chunks), encoding="utf-8")
    return {
        "diff_path": str(diff_path),
        "diff_nonempty": bool(chunks),
        "compared": compared,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sandbox-project", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--diff", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--classification", required=True)
    parser.add_argument("--model", default=os.environ.get("OPENAI_MODEL", "gpt-5.5"))
    args = parser.parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set")

    sandbox_project = Path(args.sandbox_project).resolve()
    report_path = Path(args.report).resolve()
    diff_path = Path(args.diff).resolve()
    plan_path = Path(args.plan).resolve()
    classification_path = Path(args.classification).resolve()

    sandbox_root_allowed = ROOT / "ai_patch_runner" / "sandbox"
    if not str(sandbox_project).startswith(str(sandbox_root_allowed)):
        raise SystemExit(f"Refusing sandbox outside {sandbox_root_allowed}: {sandbox_project}")

    if not PYBIN.exists():
        raise SystemExit(f"Missing venv Python: {PYBIN}")
    if not POLICY_CHECK.exists():
        raise SystemExit(f"Missing policy checker: {POLICY_CHECK}")

    policy_checks = ensure_allowed(ALLOWED_COPY_FILES + [SANDBOX_TARGET_REL])

    sandbox_project.mkdir(parents=True, exist_ok=True)
    copied = copy_files(ALLOWED_COPY_FILES, sandbox_project)

    client = OpenAI()
    ai_response = client.responses.create(
        model=args.model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Create a harmless sandbox-only note explaining that v0.3.1 can "
                    "generate an AI patch plan and apply it only inside the sandbox."
                ),
            },
        ],
    )

    ai_plan_raw = ai_response.output_text
    ai_plan = extract_json(ai_plan_raw)
    validation_findings = validate_ai_plan(ai_plan)

    plan_payload = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "model": args.model,
        "raw_output": ai_plan_raw,
        "plan": ai_plan,
        "validation_findings": validation_findings,
        "validation_ok": not validation_findings,
    }
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(json.dumps(plan_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if validation_findings:
        raise SystemExit(f"AI patch plan validation failed: {validation_findings}")

    applied = apply_ai_plan_to_sandbox(ai_plan, sandbox_project)

    compile_results = {}
    for rel in [
        "ai_patch_runner/generate_command_package.py",
        "ai_patch_runner/classify_run_output.py",
        "ai_patch_runner/runner_health_check.py",
        "ai_patch_runner/sandbox_patcher.py",
        "ai_patch_runner/policy/check_policy.py",
    ]:
        compile_results[rel] = run_cmd([str(PYBIN), "-m", "py_compile", str(sandbox_project / rel)])

    diff_result = make_diff(ALLOWED_COPY_FILES, sandbox_project, [SANDBOX_TARGET_REL], diff_path)

    command_policy_check = policy_check_command_file(diff_path)

    real_target = ROOT / SANDBOX_TARGET_REL
    real_target_exists = real_target.exists()

    ok = True
    if real_target_exists:
        ok = False
    if not diff_result["diff_nonempty"]:
        ok = False
    if not command_policy_check["allowed"]:
        ok = False
    for result in compile_results.values():
        if result["returncode"] != 0:
            ok = False

    report = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "sandbox_ai_patcher_version": "v0.3.1",
        "model": args.model,
        "sandbox_project": str(sandbox_project),
        "ai_plan_path": str(plan_path),
        "ai_plan_validation_ok": not validation_findings,
        "policy_checks": policy_checks,
        "copied": copied,
        "applied_ai_plan": applied,
        "compile_results": compile_results,
        "diff": diff_result,
        "diff_policy_check": command_policy_check,
        "real_project_integrity": {
            "real_target_path": str(real_target),
            "real_target_exists": real_target_exists,
            "real_project_patched": real_target_exists,
        },
        "safety": {
            "sandbox_only": True,
            "applied_to_real_project": False,
            "executed_generated_scripts": False,
            "started_services": False,
            "called_broker": False,
            "wrote_live_redis": False,
            "enabled_paper_or_live": False,
        },
        "verdict": "PASS" if ok else "FAIL",
    }

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    classification_response = client.responses.create(
        model=args.model,
        input=[
            {"role": "system", "content": CLASSIFIER_PROMPT},
            {"role": "user", "content": json.dumps(report, indent=2)[-24000:]},
        ],
    )
    classification = extract_json(classification_response.output_text)
    classification_path.parent.mkdir(parents=True, exist_ok=True)
    classification_path.write_text(json.dumps({
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "model": args.model,
        "raw_output": classification_response.output_text,
        "classification": classification,
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if report["verdict"] != "PASS":
        return_code = 2
    elif classification.get("verdict") != "PASS":
        return_code = 3
    else:
        return_code = 0

    print(json.dumps({
        "sandbox_ai_patcher_version": "v0.3.1",
        "report": str(report_path),
        "diff": str(diff_path),
        "plan": str(plan_path),
        "classification": str(classification_path),
        "report_verdict": report["verdict"],
        "classification_verdict": classification.get("verdict"),
        "sandbox_project": str(sandbox_project),
    }, indent=2))

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
