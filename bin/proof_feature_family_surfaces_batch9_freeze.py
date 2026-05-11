#!/usr/bin/env python3
"""Compatibility wrapper.

The proof implementation was moved to bin/proofs/proof_feature_family_surfaces_batch9_freeze.py.
This wrapper preserves the old bin/proof_feature_family_surfaces_batch9_freeze.py command path.
"""

from __future__ import annotations

import runpy
from pathlib import Path

_TARGET = Path(__file__).resolve().parent / "proofs" / "proof_feature_family_surfaces_batch9_freeze.py"

if __name__ == "__main__":
    runpy.run_path(str(_TARGET), run_name="__main__")
