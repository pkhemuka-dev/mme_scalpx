#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def main() -> int:
    source = Path("app/mme_scalpx/services/feeds.py").read_text(encoding="utf-8")

    marker = "# Batch 25V corrective — refresh feeds lock before adapter polling"
    marker_idx = source.find(marker)
    adapter_idx = source.find("for provider_id, surface in adapters.items():")
    post_poll_refresh_idx = source.find(
        '''position_state = getattr(context, "position_state", None)
                strategy_state = getattr(context, "strategy_state", None)
                service.refresh_lock_if_due()'''
    )

    checks = {
        "pre_poll_marker_present": marker_idx >= 0,
        "adapter_loop_present": adapter_idx >= 0,
        "pre_poll_refresh_before_adapter_loop": marker_idx >= 0 and adapter_idx >= 0 and marker_idx < adapter_idx,
        "post_poll_duplicate_refresh_removed": post_poll_refresh_idx < 0,
        "refresh_function_still_raises_on_lost_ownership": "feeds singleton lock refresh failed" in source,
        "acquire_lock_still_present": "RX.acquire_lock(" in source and "N.KEY_LOCK_FEEDS" in source,
        "release_lock_still_present": "RX.release_lock(N.KEY_LOCK_FEEDS" in source,
    }

    proof = {
        "proof_name": "proof_feeds_lock_refresh_pre_poll",
        "generated_at_ns": time.time_ns(),
        "feeds_lock_refresh_pre_poll_ok": all(checks.values()),
        "checks": checks,
        "proof_path": "run/proofs/proof_feeds_lock_refresh_pre_poll.json",
    }

    Path("run/proofs/proof_feeds_lock_refresh_pre_poll.json").write_text(
        json.dumps(proof, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0 if proof["feeds_lock_refresh_pre_poll_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
