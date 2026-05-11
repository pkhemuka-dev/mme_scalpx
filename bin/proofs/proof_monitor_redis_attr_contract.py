#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
APP = ROOT / "app"
if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))

import app.mme_scalpx.services.monitor as MON


def main() -> int:
    source = Path(MON.__file__).read_text(encoding="utf-8")

    checks = {
        "monitor_service_owns_private_redis": "self._redis = redis_client" in source,
        "batch15_uses_private_redis": "_batch15_missing_state_hashes(self._redis)" in source,
        "batch15_does_not_use_missing_public_redis": "_batch15_missing_state_hashes(self.redis)" not in source,
        "batch15_build_snapshot_bound": "MonitorService._build_snapshot = _batch15_build_snapshot" in source,
    }

    proof = {
        "proof_name": "proof_monitor_redis_attr_contract",
        "generated_at_ns": time.time_ns(),
        "monitor_redis_attr_contract_ok": all(checks.values()),
        "checks": checks,
        "proof_path": "run/proofs/proof_monitor_redis_attr_contract.json",
    }

    Path("run/proofs/proof_monitor_redis_attr_contract.json").write_text(
        json.dumps(proof, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0 if proof["monitor_redis_attr_contract_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
