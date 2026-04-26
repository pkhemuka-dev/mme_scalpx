#!/usr/bin/env python3
from __future__ import annotations

import json
import time

from _batch25v_market_observation_common import (
    build_all_static_guard_report,
    proof_path,
    write_proof,
)


def main() -> int:
    static = build_all_static_guard_report()

    proof = {
        "proof_name": "proof_5family_producer_consumer_matrix",
        "batch": "26I",
        "generated_at_ns": time.time_ns(),
        "producer_consumer_matrix_ok": bool(static.get("ok")),
        "checks": {
            "every_canonical_field_has_producer_and_consumer": bool(static.get("producer_consumer_matrix", {}).get("ok")),
            "no_inverted_boolean_alias_in_global_non_inverting_alias_map": bool(static.get("inverted_alias_report", {}).get("ok")),
            "missing_mode_does_not_become_normal_or_base": bool(static.get("missing_mode_report", {}).get("ok")),
            "provider_unavailable_does_not_become_ready": bool(static.get("unavailable_provider_report", {}).get("ok")),
        },
        "static_guard_report": static,
        "paper_armed_approved": False,
        "real_live_approved": False,
    }

    out = proof_path("proof_5family_producer_consumer_matrix.json")
    write_proof(out, proof)
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0 if proof["producer_consumer_matrix_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
