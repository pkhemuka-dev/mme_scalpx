#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/home/Lenovo/scalpx/projects/mme_scalpx").resolve()
PYBIN = ROOT / ".venv" / "bin" / "python"

TARGETS = [
    ROOT / "ai_patch_runner" / "generate_command_package.py",
    ROOT / "ai_patch_runner" / "classify_run_output.py",
]


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
            timeout=30,
        )
        return {
            "cmd": cmd,
            "returncode": p.returncode,
            "stdout": p.stdout[-6000:],
            "stderr": p.stderr[-6000:],
        }
    except Exception as exc:
        return {
            "cmd": cmd,
            "returncode": None,
            "stdout": "",
            "stderr": repr(exc),
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, help="proof JSON path")
    args = parser.parse_args()

    out = ROOT / args.out if not Path(args.out).is_absolute() else Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    checks: dict = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "runner_health_version": "v0.2.1",
        "root": str(ROOT),
        "required_python": str(PYBIN),
        "required_python_exists": PYBIN.exists(),
        "required_python_executable": os.access(PYBIN, os.X_OK),
        "targets": {},
        "commands": {},
        "safety": {
            "executes_generated_scripts": False,
            "patches_project": False,
            "starts_services": False,
            "calls_broker": False,
            "writes_live_redis": False,
            "enables_paper_or_live": False,
        },
    }

    ok = True

    if not PYBIN.exists() or not os.access(PYBIN, os.X_OK):
        ok = False
        checks["fatal"] = ".venv/bin/python missing or not executable"

    for target in TARGETS:
        info = {
            "path": str(target),
            "exists": target.exists(),
            "sha256": sha256_file(target) if target.exists() else None,
        }
        checks["targets"][str(target.relative_to(ROOT))] = info
        if not target.exists():
            ok = False

    if ok:
        commands = {
            "openai_import": [str(PYBIN), "-c", "import openai; print(getattr(openai, '__version__', 'unknown'))"],
            "generator_compile": [str(PYBIN), "-m", "py_compile", str(TARGETS[0])],
            "classifier_compile": [str(PYBIN), "-m", "py_compile", str(TARGETS[1])],
            "health_compile": [str(PYBIN), "-m", "py_compile", str(ROOT / 'ai_patch_runner' / 'runner_health_check.py')],
        }

        for name, cmd in commands.items():
            result = run_cmd(cmd)
            checks["commands"][name] = result
            if result["returncode"] != 0:
                ok = False

    checks["health_ok"] = ok
    checks["verdict"] = "PASS" if ok else "FAIL"

    out.write_text(json.dumps(checks, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "runner_health_version": "v0.2.1",
        "proof": str(out),
        "verdict": checks["verdict"],
        "health_ok": checks["health_ok"],
    }, indent=2))

    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
