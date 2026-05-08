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
    assert_runtime_mode_not_promoted,
    replay_python_paths,
    scan_python_static_violations,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_replay_no_runtime_promotion.json")
    args = parser.parse_args()

    paths = replay_python_paths(include_bins=True, include_proofs=False)
    violations = scan_python_static_violations(paths, categories={"runtime_promotion"})

    guard_checks = {}
    for mode in ["observe_only", "replay", "paper_armed", "live"]:
        try:
            assert_runtime_mode_not_promoted(mode)
            guard_checks[mode] = "ALLOWED"
        except Exception as exc:  # noqa: BLE001
            guard_checks[mode] = f"BLOCKED:{type(exc).__name__}"

    required_blocks_ok = (
        str(guard_checks.get("paper_armed", "")).startswith("BLOCKED")
        and str(guard_checks.get("live", "")).startswith("BLOCKED")
    )

    proof = {
        "schema_version": "proof_replay_no_runtime_promotion_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_root": str(PROJECT_ROOT),
        "scan_files": [str(p.relative_to(PROJECT_ROOT)) for p in paths],
        "runtime_guard_checks": guard_checks,
        "required_blocks_ok": required_blocks_ok,
        "runtime_promotion_reachable": bool(violations),
        "runtime_promotion_violation_count": len(violations),
        "violations": violations,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "verdict": "PASS" if not violations and required_blocks_ok else "FAIL",
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "proof": str(out),
        "runtime_promotion_reachable": proof["runtime_promotion_reachable"],
        "runtime_promotion_violation_count": proof["runtime_promotion_violation_count"],
        "required_blocks_ok": required_blocks_ok,
        "verdict": proof["verdict"],
    }, indent=2, sort_keys=True))

    return 0 if proof["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
