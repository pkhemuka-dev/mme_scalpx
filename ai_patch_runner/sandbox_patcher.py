#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/home/Lenovo/scalpx/projects/mme_scalpx").resolve()
POLICY_CHECK = ROOT / "ai_patch_runner" / "policy" / "check_policy.py"
PYBIN = ROOT / ".venv" / "bin" / "python"

DEFAULT_ALLOWED_COPY_FILES = [
    "ai_patch_runner/generate_command_package.py",
    "ai_patch_runner/classify_run_output.py",
    "ai_patch_runner/runner_health_check.py",
    "ai_patch_runner/policy/check_policy.py",
    "ai_patch_runner/policy/ai_patch_policy.json",
    "ai_patch_runner/policy/ai_patch_policy.md",
]


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


def ensure_allowed(paths: list[str]) -> list[dict]:
    checks = []
    for path in paths:
        check = policy_check_path(path)
        checks.append(check)
        if not check["allowed"]:
            raise SystemExit(f"Policy blocked path for sandbox copy: {path}")
    return checks


def copy_into_sandbox(files: list[str], sandbox_project: Path) -> dict:
    copied = {}
    for rel in files:
        src = ROOT / rel
        dst = sandbox_project / rel
        if not src.exists():
            raise SystemExit(f"Missing source for sandbox copy: {rel}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied[rel] = {
            "source": str(src),
            "sandbox": str(dst),
            "sha256_before": sha256_file(src),
            "sha256_sandbox_initial": sha256_file(dst),
        }
    return copied


def harmless_sandbox_patch(sandbox_project: Path) -> dict:
    target_rel = "ai_patch_runner/SANDBOX_ONLY_MARKER.md"
    target = sandbox_project / target_rel
    target.parent.mkdir(parents=True, exist_ok=True)
    content = (
        "# Sandbox Only Marker\n\n"
        "This file was created only inside ai_patch_runner/sandbox by AI Patch Runner v0.3.\n\n"
        "It must not exist in the real project root unless manually copied by a human.\n"
    )
    before = target.read_text(encoding="utf-8") if target.exists() else ""
    target.write_text(content, encoding="utf-8")

    return {
        "target_rel": target_rel,
        "target_path": str(target),
        "created_or_updated": True,
        "before_exists": bool(before),
        "sha256_after": sha256_file(target),
    }


def make_diff(files: list[str], sandbox_project: Path, extra_paths: list[str], diff_path: Path) -> dict:
    diff_chunks: list[str] = []
    compared = {}

    all_paths = list(files) + extra_paths

    for rel in all_paths:
        root_path = ROOT / rel
        sandbox_path = sandbox_project / rel

        root_text = root_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True) if root_path.exists() else []
        sandbox_text = sandbox_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True) if sandbox_path.exists() else []

        diff = list(difflib.unified_diff(
            root_text,
            sandbox_text,
            fromfile=f"real/{rel}",
            tofile=f"sandbox/{rel}",
        ))
        if diff:
            diff_chunks.extend(diff)
            compared[rel] = {
                "different": True,
                "root_exists": root_path.exists(),
                "sandbox_exists": sandbox_path.exists(),
            }
        else:
            compared[rel] = {
                "different": False,
                "root_exists": root_path.exists(),
                "sandbox_exists": sandbox_path.exists(),
            }

    diff_path.parent.mkdir(parents=True, exist_ok=True)
    diff_path.write_text("".join(diff_chunks), encoding="utf-8")

    return {
        "diff_path": str(diff_path),
        "diff_nonempty": bool(diff_chunks),
        "compared": compared,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sandbox-project", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--diff", required=True)
    parser.add_argument("--mode", default="smoke")
    args = parser.parse_args()

    sandbox_project = Path(args.sandbox_project).resolve()
    report_path = Path(args.report).resolve()
    diff_path = Path(args.diff).resolve()

    if not str(sandbox_project).startswith(str(ROOT / "ai_patch_runner" / "sandbox")):
        raise SystemExit(f"Refusing sandbox outside ai_patch_runner/sandbox: {sandbox_project}")

    if not PYBIN.exists():
        raise SystemExit(f"Missing venv Python: {PYBIN}")

    if not POLICY_CHECK.exists():
        raise SystemExit(f"Missing policy checker: {POLICY_CHECK}")

    allowed_files = list(DEFAULT_ALLOWED_COPY_FILES)
    policy_checks = ensure_allowed(allowed_files)

    sandbox_project.mkdir(parents=True, exist_ok=True)
    copied = copy_into_sandbox(allowed_files, sandbox_project)

    patch_result = harmless_sandbox_patch(sandbox_project)

    compile_results = {}
    for rel in [
        "ai_patch_runner/generate_command_package.py",
        "ai_patch_runner/classify_run_output.py",
        "ai_patch_runner/runner_health_check.py",
        "ai_patch_runner/policy/check_policy.py",
    ]:
        compile_results[rel] = run_cmd([str(PYBIN), "-m", "py_compile", str(sandbox_project / rel)])

    diff_result = make_diff(
        allowed_files,
        sandbox_project,
        [patch_result["target_rel"]],
        diff_path,
    )

    # Prove real project was not patched with the sandbox-only marker.
    real_marker = ROOT / patch_result["target_rel"]
    real_marker_exists = real_marker.exists()

    ok = True
    if real_marker_exists:
        ok = False
    if not diff_result["diff_nonempty"]:
        ok = False
    for result in compile_results.values():
        if result["returncode"] != 0:
            ok = False

    report = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "sandbox_patcher_version": "v0.3",
        "mode": args.mode,
        "root": str(ROOT),
        "sandbox_project": str(sandbox_project),
        "policy_checks": policy_checks,
        "copied": copied,
        "sandbox_patch": patch_result,
        "compile_results": compile_results,
        "diff": diff_result,
        "real_project_integrity": {
            "real_marker_path": str(real_marker),
            "real_marker_exists": real_marker_exists,
            "real_project_patched": False if not real_marker_exists else True,
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

    print(json.dumps({
        "sandbox_patcher_version": "v0.3",
        "report": str(report_path),
        "diff": str(diff_path),
        "verdict": report["verdict"],
        "sandbox_project": str(sandbox_project),
    }, indent=2))

    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
