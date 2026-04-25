#!/usr/bin/env python3
from __future__ import annotations

"""
Final-freeze legacy quarantine proof.

Combines:
- proof_legacy_baseline_quarantine.py
- proof_repo_hygiene_quarantine.py

Important:
Some delegated proofs import app modules, which can create __pycache__.
Before running the repo hygiene proof, this wrapper removes active bytecode so
the hygiene proof validates repository cleanliness rather than Python runtime
side effects.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYBIN = ROOT / ".venv" / "bin" / "python"
if not PYBIN.exists():
    PYBIN = Path(sys.executable)

ENV = os.environ.copy()
ENV["PYTHONDONTWRITEBYTECODE"] = "1"

BASELINE = ROOT / "bin" / "proof_legacy_baseline_quarantine.py"
HYGIENE = ROOT / "bin" / "proof_repo_hygiene_quarantine.py"

def clean_active_pycache() -> None:
    for base in (ROOT / "app", ROOT / "bin"):
        if not base.exists():
            continue
        for f in list(base.rglob("*.pyc")) + list(base.rglob("*.pyo")):
            try:
                f.unlink()
            except FileNotFoundError:
                pass
        for d in sorted(base.rglob("__pycache__"), key=lambda p: len(p.parts), reverse=True):
            shutil.rmtree(d, ignore_errors=True)

def run(target: Path) -> int:
    print(f"===== RUN {target.relative_to(ROOT)} =====")
    return subprocess.run(
        [str(PYBIN), "-B", str(target.relative_to(ROOT))],
        cwd=ROOT,
        env=ENV,
    ).returncode

for target in (BASELINE, HYGIENE):
    if not target.exists():
        print(f"[FAIL] missing delegated proof: {target.relative_to(ROOT)}", file=sys.stderr)
        raise SystemExit(2)

clean_active_pycache()

rc1 = run(BASELINE)
clean_active_pycache()

rc2 = run(HYGIENE)
clean_active_pycache()

if rc1 != 0 or rc2 != 0:
    print(f"[FAIL] delegated legacy quarantine proof failed: baseline={rc1}, hygiene={rc2}", file=sys.stderr)
    raise SystemExit(1)

print("[PASS] legacy quarantine contracts delegated proofs passed")
