#!/usr/bin/env python3
from __future__ import annotations

"""
Compatibility proof wrapper.

Canonical final-freeze proof name:
    proof_replay_engine_contracts.py

Existing batch proof with replay-engine coverage:
    proof_replay_batch16_freeze.py

This wrapper delegates to the existing replay batch-16 freeze proof and returns
its exact exit status.
"""

import runpy
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().with_name("proof_replay_batch16_freeze.py")

if not TARGET.exists():
    print(f"[FAIL] missing delegated proof: {TARGET}", file=sys.stderr)
    raise SystemExit(2)

runpy.run_path(str(TARGET), run_name="__main__")
