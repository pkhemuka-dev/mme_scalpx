#!/usr/bin/env python3
from __future__ import annotations

"""
Compatibility proof wrapper for Batch 5 provider-runtime role hardening.

Canonical proof artifact:
  run/proofs/integrations_batch5_freeze.json
"""

from pathlib import Path
import runpy

SCRIPT = Path(__file__).with_name("proof_integrations_batch5_freeze.py")
runpy.run_path(str(SCRIPT), run_name="__main__")
