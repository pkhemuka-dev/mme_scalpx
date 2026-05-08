from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

from app.mme_scalpx.replay.safety import (
    REPLAY_KEY_PREFIX,
    assert_replay_key,
    assert_runtime_mode_not_promoted,
)


REPLAY_TRANSPORT_CONTRACT_VERSION = "replay_live_shape_transport_v1"

REPLAY_TRANSPORT_REQUIRED_METHODS = (
    "publish",
    "write_state",
    "read_stream",
    "read_state",
    "snapshot",
    "reset",
)

REPLAY_LIVE_SHAPE_SURFACES = (
    "futures_tick",
    "selected_option_tick",
    "dhan_context",
    "oi_ladder",
    "provider_runtime",
    "feature_payload",
    "strategy_decision",
    "risk_shadow",
    "execution_shadow",
)


class ReplayTransportError(RuntimeError):
    """Replay transport contract violation."""


def replay_key_for(live_contract_name: str, *, kind: str = "stream", run_id: str = "") -> str:
    safe_live = str(live_contract_name).strip().replace(" ", "_").replace("/", ":")
    safe_kind = str(kind).strip().replace(" ", "_")
    safe_run = str(run_id or "default").strip().replace(" ", "_")
    return f"{REPLAY_KEY_PREFIX}{safe_run}:{safe_kind}:{safe_live}"


def _utc_now_ns() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1_000_000_000)


def _copy_payload(payload: Mapping[str, Any] | None) -> dict[str, Any]:
    return dict(deepcopy(dict(payload or {})))


@dataclass(frozen=True)
class ReplayTransportEvent:
    schema_version: str
    run_id: str
    replay_key: str
    live_contract_name: str
    surface: str
    payload: dict[str, Any]
    event_ts_ns: int
    sequence_id: int
    paper_armed_approved: bool = False
    live_trading_approved: bool = False
    execution_arming_created: bool = False
    production_doctrine_changed: bool = False


@dataclass(frozen=True)
class ReplayTransportState:
    schema_version: str
    run_id: str
    replay_key: str
    live_contract_name: str
    surface: str
    payload: dict[str, Any]
    updated_ts_ns: int
    paper_armed_approved: bool = False
    live_trading_approved: bool = False
    execution_arming_created: bool = False
    production_doctrine_changed: bool = False


@dataclass
class LocalReplayTransport:
    """Replay-only in-memory transport.

    This class intentionally does not import Redis, redisx, brokers, execution,
    or live services. It stores live-compatible event/state shapes under replay:
    keys only.
    """

    run_id: str
    streams: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    states: dict[str, dict[str, Any]] = field(default_factory=dict)
    sequence: int = 0

    def __post_init__(self) -> None:
        assert_runtime_mode_not_promoted("replay")
        self.run_id = str(self.run_id or "default")

    def reset(self) -> dict[str, Any]:
        self.streams.clear()
        self.states.clear()
        self.sequence = 0
        return {
            "schema_version": "local_replay_transport_reset_v1",
            "run_id": self.run_id,
            "reset_ok": True,
            "paper_armed_approved": False,
            "live_trading_approved": False,
            "execution_arming_created": False,
            "production_doctrine_changed": False,
        }

    def publish(
        self,
        *,
        live_contract_name: str,
        surface: str,
        payload: Mapping[str, Any] | None = None,
        replay_key: str | None = None,
        event_ts_ns: int | None = None,
        sequence_id: int | None = None,
    ) -> dict[str, Any]:
        if surface not in REPLAY_LIVE_SHAPE_SURFACES:
            raise ReplayTransportError(f"unknown replay live-shape surface: {surface}")
        key = assert_replay_key(replay_key or replay_key_for(live_contract_name, kind="stream", run_id=self.run_id))
        self.sequence = int(sequence_id) if sequence_id is not None else self.sequence + 1
        event = ReplayTransportEvent(
            schema_version=REPLAY_TRANSPORT_CONTRACT_VERSION,
            run_id=self.run_id,
            replay_key=key,
            live_contract_name=str(live_contract_name),
            surface=str(surface),
            payload=_copy_payload(payload),
            event_ts_ns=int(event_ts_ns if event_ts_ns is not None else _utc_now_ns()),
            sequence_id=int(self.sequence),
        )
        row = asdict(event)
        self.streams.setdefault(key, []).append(row)
        return row

    def write_state(
        self,
        *,
        live_contract_name: str,
        surface: str,
        payload: Mapping[str, Any] | None = None,
        replay_key: str | None = None,
        updated_ts_ns: int | None = None,
    ) -> dict[str, Any]:
        if surface not in REPLAY_LIVE_SHAPE_SURFACES:
            raise ReplayTransportError(f"unknown replay live-shape surface: {surface}")
        key = assert_replay_key(replay_key or replay_key_for(live_contract_name, kind="state", run_id=self.run_id))
        state = ReplayTransportState(
            schema_version=REPLAY_TRANSPORT_CONTRACT_VERSION,
            run_id=self.run_id,
            replay_key=key,
            live_contract_name=str(live_contract_name),
            surface=str(surface),
            payload=_copy_payload(payload),
            updated_ts_ns=int(updated_ts_ns if updated_ts_ns is not None else _utc_now_ns()),
        )
        row = asdict(state)
        self.states[key] = row
        return row

    def read_stream(self, replay_key: str) -> tuple[dict[str, Any], ...]:
        key = assert_replay_key(replay_key)
        return tuple(deepcopy(self.streams.get(key, [])))

    def read_state(self, replay_key: str) -> dict[str, Any] | None:
        key = assert_replay_key(replay_key)
        value = self.states.get(key)
        return deepcopy(value) if value is not None else None

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema_version": "local_replay_transport_snapshot_v1",
            "run_id": self.run_id,
            "stream_count": len(self.streams),
            "state_count": len(self.states),
            "event_count": sum(len(v) for v in self.streams.values()),
            "streams": deepcopy(self.streams),
            "states": deepcopy(self.states),
            "sequence": self.sequence,
            "paper_armed_approved": False,
            "live_trading_approved": False,
            "execution_arming_created": False,
            "production_doctrine_changed": False,
        }


def assert_live_shape_event(event: Mapping[str, Any]) -> bool:
    required = (
        "schema_version",
        "run_id",
        "replay_key",
        "live_contract_name",
        "surface",
        "payload",
        "event_ts_ns",
        "sequence_id",
        "paper_armed_approved",
        "live_trading_approved",
        "production_doctrine_changed",
    )
    missing = [name for name in required if name not in event]
    if missing:
        raise ReplayTransportError(f"missing live-shape event fields: {missing}")
    assert_replay_key(str(event["replay_key"]))
    if event["surface"] not in REPLAY_LIVE_SHAPE_SURFACES:
        raise ReplayTransportError(f"invalid live-shape surface: {event['surface']}")
    if event.get("paper_armed_approved") is not False:
        raise ReplayTransportError("event must not approve paper_armed")
    if event.get("live_trading_approved") is not False:
        raise ReplayTransportError("event must not approve live trading")
    if event.get("production_doctrine_changed") is not False:
        raise ReplayTransportError("event must not mutate doctrine")
    return True


def assert_live_shape_state(state: Mapping[str, Any]) -> bool:
    required = (
        "schema_version",
        "run_id",
        "replay_key",
        "live_contract_name",
        "surface",
        "payload",
        "updated_ts_ns",
        "paper_armed_approved",
        "live_trading_approved",
        "production_doctrine_changed",
    )
    missing = [name for name in required if name not in state]
    if missing:
        raise ReplayTransportError(f"missing live-shape state fields: {missing}")
    assert_replay_key(str(state["replay_key"]))
    if state["surface"] not in REPLAY_LIVE_SHAPE_SURFACES:
        raise ReplayTransportError(f"invalid live-shape surface: {state['surface']}")
    if state.get("paper_armed_approved") is not False:
        raise ReplayTransportError("state must not approve paper_armed")
    if state.get("live_trading_approved") is not False:
        raise ReplayTransportError("state must not approve live trading")
    if state.get("production_doctrine_changed") is not False:
        raise ReplayTransportError("state must not mutate doctrine")
    return True


try:
    __all__
except NameError:
    __all__ = tuple()

__all__ = tuple(dict.fromkeys(tuple(__all__) + (
    "REPLAY_TRANSPORT_CONTRACT_VERSION",
    "REPLAY_TRANSPORT_REQUIRED_METHODS",
    "REPLAY_LIVE_SHAPE_SURFACES",
    "ReplayTransportError",
    "ReplayTransportEvent",
    "ReplayTransportState",
    "LocalReplayTransport",
    "replay_key_for",
    "assert_live_shape_event",
    "assert_live_shape_state",
)))
