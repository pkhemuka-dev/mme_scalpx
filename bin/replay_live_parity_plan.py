#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path.cwd()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.mme_scalpx.replay.live_parity import materialize_replay_live_parity_audit_plan


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay/live parity audit plan materializer. Plan-only.")
    parser.add_argument("--run-id", default="batch28a_replay_live_parity_plan")
    parser.add_argument("--root", default="")
    args = parser.parse_args()

    root = args.root or ("run/replay/parity/" + args.run_id)
    result = materialize_replay_live_parity_audit_plan(run_id=args.run_id, root=root)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
