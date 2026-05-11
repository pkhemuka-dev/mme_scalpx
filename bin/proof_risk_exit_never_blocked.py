#!/usr/bin/env python3
"""Disabled migration stub.

This legacy proof script was excluded from automated bin/proofs migration.

Reason:
- R8/R8B/R8C proved the migrated target was wrapper-shaped, not a real implementation.
- Running this path could otherwise recurse or point to a missing target.

Required action:
- Locate the real proof implementation before re-enabling or migrating this script.

Safety:
- This stub performs no runtime action.
- This stub performs no broker call.
- This stub performs no Redis write.
- This stub performs no paper/live enablement.
"""

from __future__ import annotations

import sys

MESSAGE = (
    "DISABLED: bin/proof_risk_exit_never_blocked.py is excluded from automated "
    "bin/proofs migration because its implementation target was wrapper-shaped. "
    "Locate the real implementation before running this proof."
)

if __name__ == "__main__":
    print(MESSAGE, file=sys.stderr)
    raise SystemExit(2)
