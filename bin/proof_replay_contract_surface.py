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

from app.mme_scalpx.replay.contracts import (  # noqa: E402
    REPLAY_LIVE_SHAPE_EVENT_REQUIRED_FIELDS,
    REPLAY_LIVE_SHAPE_REQUIRED_SURFACES,
    REPLAY_LIVE_SHAPE_STATE_REQUIRED_FIELDS,
    replay_live_shape_transport_contract_summary,
)
from app.mme_scalpx.replay.live_adapter import LIVE_CONTRACT_NAMES, replay_live_adapter_contract_summary  # noqa: E402
from app.mme_scalpx.replay.transport import (  # noqa: E402
    REPLAY_LIVE_SHAPE_SURFACES,
    REPLAY_TRANSPORT_REQUIRED_METHODS,
    LocalReplayTransport,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_replay_contract_surface.json")
    args = parser.parse_args()

    contract_file = ROOT / "etc/replay/schemas/replay_live_shape_transport_contract_v1.json"
    contract_payload = json.loads(contract_file.read_text(encoding="utf-8")) if contract_file.exists() else {}

    required_methods = tuple(contract_payload.get("required_transport_methods", ()))
    required_surfaces = tuple(contract_payload.get("required_surfaces", ()))
    event_fields = tuple(contract_payload.get("required_event_fields", ()))
    state_fields = tuple(contract_payload.get("required_state_fields", ()))

    method_results = {
        method: hasattr(LocalReplayTransport, method)
        for method in required_methods
    }

    surfaces_match_contracts = (
        tuple(REPLAY_LIVE_SHAPE_REQUIRED_SURFACES) == tuple(REPLAY_LIVE_SHAPE_SURFACES)
        and set(required_surfaces) == set(REPLAY_LIVE_SHAPE_SURFACES)
        and set(LIVE_CONTRACT_NAMES) == set(REPLAY_LIVE_SHAPE_SURFACES)
    )

    event_fields_ok = set(REPLAY_LIVE_SHAPE_EVENT_REQUIRED_FIELDS).issubset(set(event_fields))
    state_fields_ok = set(REPLAY_LIVE_SHAPE_STATE_REQUIRED_FIELDS).issubset(set(state_fields))

    no_approval_ok = (
        contract_payload.get("paper_armed_approved") is False
        and contract_payload.get("live_trading_approved") is False
        and contract_payload.get("execution_arming_created") is False
        and contract_payload.get("broker_calls_allowed") is False
        and contract_payload.get("live_redis_writes_allowed") is False
        and contract_payload.get("production_doctrine_changed") is False
    )

    summary = replay_live_shape_transport_contract_summary()
    adapter_summary = replay_live_adapter_contract_summary()

    contract_surface_ok = bool(
        contract_file.exists()
        and all(method_results.values())
        and surfaces_match_contracts
        and event_fields_ok
        and state_fields_ok
        and no_approval_ok
        and summary.get("paper_armed_approved") is False
        and adapter_summary.get("paper_armed_approved") is False
    )

    proof = {
        "schema_version": "proof_replay_contract_surface_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "contract_surface_ok": contract_surface_ok,
        "contract_file_exists": contract_file.exists(),
        "method_results": method_results,
        "surfaces_match_contracts": surfaces_match_contracts,
        "event_fields_ok": event_fields_ok,
        "state_fields_ok": state_fields_ok,
        "no_approval_ok": no_approval_ok,
        "contract_summary": summary,
        "adapter_summary": adapter_summary,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "production_doctrine_changed": False,
        "verdict": "PASS" if contract_surface_ok else "FAIL",
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "proof": str(out),
        "verdict": proof["verdict"],
        "contract_surface_ok": contract_surface_ok,
        "surfaces_match_contracts": surfaces_match_contracts,
        "event_fields_ok": event_fields_ok,
        "state_fields_ok": state_fields_ok,
        "paper_armed_approved": False,
        "live_trading_approved": False,
    }, indent=2, sort_keys=True))

    return 0 if contract_surface_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
