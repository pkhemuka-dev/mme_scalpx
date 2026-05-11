#!/usr/bin/env python3
from __future__ import annotations

"""
Compatibility wrapper for the Batch 14 risk freeze proof.

Canonical artifact:
  run/proofs/risk_batch14_freeze.json
"""

from pathlib import Path
import runpy

SCRIPT = Path(__file__).with_name("proof_risk_batch14_freeze.py")
runpy.run_path(str(SCRIPT), run_name="__main__")
