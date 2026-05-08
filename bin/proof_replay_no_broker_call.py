#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.mme_scalpx.replay.safety import (  # noqa: E402
    PROJECT_ROOT,
    replay_python_paths,
    scan_python_static_violations,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_replay_no_broker_call.json")
    args = parser.parse_args()

    paths = replay_python_paths(include_bins=True, include_proofs=False)
    violations = scan_python_static_violations(paths, categories={"broker"})

    proof = {
        "schema_version": "proof_replay_no_broker_call_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_root": str(PROJECT_ROOT),
        "scan_files": [str(p.relative_to(PROJECT_ROOT)) for p in paths],
        "broker_call_reachable": bool(violations),
        "broker_violation_count": len(violations),
        "violations": violations,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "verdict": "PASS" if not violations else "FAIL",
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "proof": str(out),
        "broker_call_reachable": proof["broker_call_reachable"],
        "broker_violation_count": proof["broker_violation_count"],
        "verdict": proof["verdict"],
    }, indent=2, sort_keys=True))

    return 0 if proof["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
