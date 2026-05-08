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

from app.mme_scalpx.core import names as N
from app.mme_scalpx.core import redisx as RX
from bin._batch25v_market_observation_common import redis_client


def main() -> int:
    client = redis_client()

    key = "lock:batch25v:proof"
    owner_a = f"owner-a:{time.time_ns()}"
    owner_b = f"owner-b:{time.time_ns()}"
    ttl_ms = 30_000

    client.delete(key)

    acquired = bool(RX.acquire_lock(key, owner_a, ttl_ms=ttl_ms, client=client))
    value_after_acquire = client.get(key)
    if isinstance(value_after_acquire, bytes):
        value_after_acquire = value_after_acquire.decode("utf-8", errors="replace")

    refresh_same_owner = bool(RX.refresh_lock(key, owner_a, ttl_ms=ttl_ms, client=client))
    value_after_refresh = client.get(key)
    if isinstance(value_after_refresh, bytes):
        value_after_refresh = value_after_refresh.decode("utf-8", errors="replace")

    refresh_wrong_owner = bool(RX.refresh_lock(key, owner_b, ttl_ms=ttl_ms, client=client))
    value_after_wrong_refresh = client.get(key)
    if isinstance(value_after_wrong_refresh, bytes):
        value_after_wrong_refresh = value_after_wrong_refresh.decode("utf-8", errors="replace")

    pttl_after_refresh = client.pttl(key)
    client.delete(key)

    checks = {
        "acquire_passed": acquired is True,
        "acquire_stored_owner": value_after_acquire == owner_a,
        "refresh_same_owner_passed": refresh_same_owner is True,
        "refresh_preserved_owner": value_after_refresh == owner_a,
        "refresh_wrong_owner_failed": refresh_wrong_owner is False,
        "wrong_refresh_preserved_owner": value_after_wrong_refresh == owner_a,
        "refresh_extended_ttl": pttl_after_refresh > 0,
        "feeds_lock_name_present": bool(getattr(N, "KEY_LOCK_FEEDS", "")),
        "execution_lock_name_present": bool(getattr(N, "KEY_LOCK_EXECUTION", "")),
    }

    proof = {
        "proof_name": "proof_lock_refresh_contract",
        "generated_at_ns": time.time_ns(),
        "lock_refresh_contract_ok": all(checks.values()),
        "checks": checks,
        "values": {
            "proof_key": key,
            "value_after_acquire": value_after_acquire,
            "value_after_refresh": value_after_refresh,
            "value_after_wrong_refresh": value_after_wrong_refresh,
            "pttl_after_refresh": pttl_after_refresh,
            "feeds_lock_name": getattr(N, "KEY_LOCK_FEEDS", "lock:feeds"),
            "execution_lock_name": getattr(N, "KEY_LOCK_EXECUTION", "lock:execution"),
        },
        "proof_path": "run/proofs/proof_lock_refresh_contract.json",
    }

    Path("run/proofs/proof_lock_refresh_contract.json").write_text(
        json.dumps(proof, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0 if proof["lock_refresh_contract_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
