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

from app.mme_scalpx.replay.live_adapter import (  # noqa: E402
    publish_replay_live_shape,
    replay_live_shape_key,
    write_replay_live_state,
)
from app.mme_scalpx.replay.transport import (  # noqa: E402
    REPLAY_LIVE_SHAPE_SURFACES,
    LocalReplayTransport,
    assert_live_shape_event,
    assert_live_shape_state,
)
from app.mme_scalpx.replay.safety import assert_replay_key  # noqa: E402


STREAM_SURFACES = ("futures_tick", "selected_option_tick", "feature_payload", "strategy_decision")
STATE_SURFACES = ("dhan_context", "oi_ladder", "provider_runtime", "risk_shadow", "execution_shadow")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_replay_live_shape_transport.json")
    args = parser.parse_args()

    run_id = "replay_transport_smoke"
    transport = LocalReplayTransport(run_id=run_id)

    events = []
    states = []

    for index, surface in enumerate(STREAM_SURFACES, start=1):
        row = {
            "event_ts_ns": 1_000_000_000 + index,
            "sequence_id": index,
            "surface_test": surface,
            "provider_ready_miso": surface != "futures_tick",
            "family_features_json": "{}" if surface == "feature_payload" else None,
            "family_surfaces_json": "{}" if surface == "feature_payload" else None,
        }
        event = publish_replay_live_shape(
            transport,
            surface=surface,
            row=row,
            event_ts_ns=row["event_ts_ns"],
            sequence_id=index,
        )
        assert_live_shape_event(event)
        events.append(event)

    for index, surface in enumerate(STATE_SURFACES, start=1):
        row = {
            "updated_ts_ns": 2_000_000_000 + index,
            "surface_test": surface,
            "dhan_context_fresh": surface == "dhan_context",
            "oi_wall_strength": 1.0 if surface == "oi_ladder" else None,
            "provider_ready_miso": surface == "provider_runtime",
        }
        state = write_replay_live_state(
            transport,
            surface=surface,
            row=row,
            updated_ts_ns=row["updated_ts_ns"],
        )
        assert_live_shape_state(state)
        states.append(state)

    snapshot = transport.snapshot()

    all_keys = []
    for surface in STREAM_SURFACES:
        key = replay_live_shape_key(run_id=run_id, surface=surface, kind="stream")
        assert_replay_key(key)
        all_keys.append(key)

    for surface in STATE_SURFACES:
        key = replay_live_shape_key(run_id=run_id, surface=surface, kind="state")
        assert_replay_key(key)
        all_keys.append(key)

    namespace_ok = all(str(key).startswith("replay:") for key in all_keys)
    live_shape_event_ok = all(event.get("replay_key", "").startswith("replay:") for event in events)
    live_shape_state_ok = all(state.get("replay_key", "").startswith("replay:") for state in states)

    no_approval_ok = (
        all(event.get("paper_armed_approved") is False for event in events)
        and all(event.get("live_trading_approved") is False for event in events)
        and all(event.get("production_doctrine_changed") is False for event in events)
        and all(state.get("paper_armed_approved") is False for state in states)
        and all(state.get("live_trading_approved") is False for state in states)
        and all(state.get("production_doctrine_changed") is False for state in states)
    )

    event_count_ok = snapshot.get("event_count") == len(STREAM_SURFACES)
    state_count_ok = snapshot.get("state_count") == len(STATE_SURFACES)

    reset_result = transport.reset()
    reset_ok = (
        reset_result.get("reset_ok") is True
        and transport.snapshot().get("event_count") == 0
        and transport.snapshot().get("state_count") == 0
    )

    transport_ok = bool(
        namespace_ok
        and live_shape_event_ok
        and live_shape_state_ok
        and no_approval_ok
        and event_count_ok
        and state_count_ok
        and reset_ok
        and set(REPLAY_LIVE_SHAPE_SURFACES) == set(STREAM_SURFACES + STATE_SURFACES)
    )

    proof = {
        "schema_version": "proof_replay_live_shape_transport_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "live_shape_transport_ok": transport_ok,
        "namespace_ok": namespace_ok,
        "live_shape_event_ok": live_shape_event_ok,
        "live_shape_state_ok": live_shape_state_ok,
        "no_approval_ok": no_approval_ok,
        "event_count_ok": event_count_ok,
        "state_count_ok": state_count_ok,
        "reset_ok": reset_ok,
        "stream_surfaces": STREAM_SURFACES,
        "state_surfaces": STATE_SURFACES,
        "all_keys": all_keys,
        "events": events,
        "states": states,
        "snapshot_before_reset": snapshot,
        "reset_result": reset_result,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "verdict": "PASS" if transport_ok else "FAIL",
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "proof": str(out),
        "verdict": proof["verdict"],
        "live_shape_transport_ok": transport_ok,
        "namespace_ok": namespace_ok,
        "event_count_ok": event_count_ok,
        "state_count_ok": state_count_ok,
        "reset_ok": reset_ok,
        "paper_armed_approved": False,
        "live_trading_approved": False,
    }, indent=2, sort_keys=True))

    return 0 if transport_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
