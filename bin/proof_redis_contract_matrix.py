#!/usr/bin/env python3
"""Compatibility wrapper.

The proof implementation was moved to bin/proofs/proof_redis_contract_matrix.py.
This wrapper preserves the old bin/proof_redis_contract_matrix.py command path.
"""

from __future__ import annotations

import runpy
from pathlib import Path

_TARGET = Path(__file__).resolve().parent / "proofs" / "proof_redis_contract_matrix.py"

if __name__ == "__main__":
    runpy.run_path(str(_TARGET), run_name="__main__")
