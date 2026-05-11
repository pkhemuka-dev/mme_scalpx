#!/usr/bin/env python3
from __future__ import annotations

"""
Compatibility proof wrapper.

Canonical final-freeze proof name:
    proof_strategy_family_doctrine_leaves.py

Existing proof with equivalent doctrine-leaf coverage:
    proof_strategy_family_doctrine_package.py

This wrapper delegates to the freeze-proven strategy-family doctrine package
proof and returns its exact exit status.
"""

import runpy
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().with_name("proof_strategy_family_doctrine_package.py")

if not TARGET.exists():
    print(f"[FAIL] missing delegated proof: {TARGET}", file=sys.stderr)
    raise SystemExit(2)

runpy.run_path(str(TARGET), run_name="__main__")
