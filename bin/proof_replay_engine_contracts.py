#!/usr/bin/env python3
"""Disabled migration stub.

This proof script was excluded from automated bin/proofs migration.

Reason:
- Migration inspection proved the moved target was not a real implementation.
- No safe real implementation was found in R8 backup or git HEAD during R8F.

Source:
- bin/proof_replay_engine_contracts.py

Invalid target:
- bin/proofs/proof_replay_engine_contracts.py

Safety:
- This stub performs no runtime action.
- This stub performs no broker call.
- This stub performs no Redis write.
- This stub performs no paper/live enablement.
"""

from __future__ import annotations

import sys

MESSAGE = (
    "DISABLED: bin/proof_replay_engine_contracts.py is excluded from automated bin/proofs migration. "
    "No real implementation was found. Locate the real proof implementation before running."
)

if __name__ == "__main__":
    print(MESSAGE, file=sys.stderr)
    raise SystemExit(2)
