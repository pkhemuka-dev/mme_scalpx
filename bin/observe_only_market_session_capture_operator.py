#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path.cwd()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.mme_scalpx.replay.live_capture_runbook import materialize_observe_only_market_session_operator_plan


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-id", default="batch28d_operator_plan")
    parser.add_argument("--root", default="")
    args = parser.parse_args()

    root = args.root or ("run/replay/parity/live_session_operator/" + args.session_id)
    result = materialize_observe_only_market_session_operator_plan(session_id=args.session_id, root=root)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
