#!/usr/bin/env python3
from __future__ import annotations

"""
Compatibility proof wrapper.

Canonical final-freeze proof name:
    proof_feature_family_strategy_surfaces.py

Existing batch proof with equivalent surface coverage:
    proof_feature_family_surfaces_batch9_freeze.py

This wrapper does not weaken the gate. It delegates to the existing batch-9
feature-family surfaces proof and returns its exact exit status.
"""

import runpy
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().with_name("proof_feature_family_surfaces_batch9_freeze.py")

if not TARGET.exists():
    print(f"[FAIL] missing delegated proof: {TARGET}", file=sys.stderr)
    raise SystemExit(2)

runpy.run_path(str(TARGET), run_name="__main__")
