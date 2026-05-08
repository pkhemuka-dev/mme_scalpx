#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path.cwd()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.mme_scalpx.replay.live_capture_executor import (
    execute_observe_only_market_session_capture_package,
    materialize_observe_only_market_session_capture_execution_plan,
    market_session_status,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Market-session-gated observe_only evidence capture package executor. Does not start services, touch Redis, call brokers, or enable paper/live."
    )
    parser.add_argument("--session-id", default="observe_only_YYYYMMDD")
    parser.add_argument("--root", default="")
    parser.add_argument("--evidence-map", default="")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirm-observe-only", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()

    if args.status:
        print(json.dumps(market_session_status(), indent=2, sort_keys=True, default=str))
        return 0

    root = args.root or ("run/replay/parity/live_evidence/" + args.session_id)

    if not args.execute:
        result = materialize_observe_only_market_session_capture_execution_plan(
            session_id=args.session_id,
            root=root,
        )
    else:
        if not args.evidence_map:
            raise SystemExit("ERROR: --evidence-map is required with --execute")
        result = execute_observe_only_market_session_capture_package(
            session_id=args.session_id,
            root=root,
            evidence_map=args.evidence_map,
            execute=True,
            confirm_observe_only=args.confirm_observe_only,
        )

    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
