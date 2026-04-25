#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LOCK_FILES = [
    "requirements.txt",
    "requirements.lock",
    "pyproject.toml",
    "poetry.lock",
]

def main() -> int:
    checks = []

    present = []
    for f in LOCK_FILES:
        p = ROOT / f
        if p.exists() and p.stat().st_size > 0:
            present.append(f)

    checks.append({
        "case": "dependency_lock_or_manifest_exists",
        "status": "PASS" if present else "FAIL",
        "present": present,
    })

    pip_freeze_path = ROOT / "run/proofs/runtime_dependency_freeze.txt"
    try:
        proc = subprocess.run(
            [str(ROOT / ".venv/bin/python"), "-m", "pip", "freeze"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
        )
        pip_freeze_path.write_text(proc.stdout, encoding="utf-8")
        checks.append({
            "case": "pip_freeze_capture",
            "status": "PASS" if proc.returncode == 0 and bool(proc.stdout.strip()) else "FAIL",
            "artifact": str(pip_freeze_path.relative_to(ROOT)),
        })
    except Exception as exc:
        checks.append({
            "case": "pip_freeze_capture",
            "status": "FAIL",
            "error": repr(exc),
        })

    failed = [c for c in checks if c["status"] == "FAIL"]
    result = {
        "proof_name": "runtime_dependency_lock",
        "proof_version": "1",
        "status": "PASS" if not failed else "FAIL",
        "timestamp_ns": time.time_ns(),
        "checks": checks,
        "failed_checks": failed,
        "uses_broker": False,
        "places_orders": False,
        "writes_live_redis": False,
        "does_not_prove": ["dependency_vulnerability_scan"],
    }

    out = ROOT / "run/proofs/proof_runtime_dependency_lock.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if not failed else 1

if __name__ == "__main__":
    raise SystemExit(main())
