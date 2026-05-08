from __future__ import annotations

from typing import Any, Mapping

from app.mme_scalpx.replay.transport import (
    LocalReplayTransport,
    assert_live_shape_event,
    assert_live_shape_state,
    replay_key_for,
)


REPLAY_LIVE_ADAPTER_CONTRACT_VERSION = "replay_live_adapter_v1"


LIVE_CONTRACT_NAMES = {
    "futures_tick": "STREAM_TICKS_MME_FUT",
    "selected_option_tick": "STREAM_TICKS_MME_OPT",
    "dhan_context": "HASH_STATE_DHAN_CONTEXT_REPLAY",
    "oi_ladder": "HASH_STATE_OI_LADDER_REPLAY",
    "provider_runtime": "HASH_STATE_PROVIDER_RUNTIME_REPLAY",
    "feature_payload": "STREAM_FEATURES_MME",
    "strategy_decision": "STREAM_DECISIONS_MME",
    "risk_shadow": "HASH_STATE_REPLAY_RISK_SHADOW",
    "execution_shadow": "HASH_STATE_REPLAY_EXECUTION_SHADOW",
}


def replay_live_contract_name(surface: str) -> str:
    try:
        return LIVE_CONTRACT_NAMES[str(surface)]
    except KeyError as exc:
        raise KeyError(f"unknown replay live-adapter surface: {surface}") from exc


def build_replay_live_shape_payload(
    *,
    surface: str,
    row: Mapping[str, Any] | None = None,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    payload = dict(row or {})
    payload.update(dict(extra or {}))
    payload.setdefault("surface", surface)
    payload.setdefault("replay_only", True)
    payload.setdefault("paper_armed_approved", False)
    payload.setdefault("live_trading_approved", False)
    payload.setdefault("execution_arming_created", False)
    payload.setdefault("production_doctrine_changed", False)
    return payload


def publish_replay_live_shape(
    transport: LocalReplayTransport,
    *,
    surface: str,
    row: Mapping[str, Any] | None = None,
    extra: Mapping[str, Any] | None = None,
    event_ts_ns: int | None = None,
    sequence_id: int | None = None,
) -> dict[str, Any]:
    live_contract_name = replay_live_contract_name(surface)
    payload = build_replay_live_shape_payload(surface=surface, row=row, extra=extra)
    event = transport.publish(
        live_contract_name=live_contract_name,
        surface=surface,
        payload=payload,
        event_ts_ns=event_ts_ns,
        sequence_id=sequence_id,
    )
    assert_live_shape_event(event)
    return event


def write_replay_live_state(
    transport: LocalReplayTransport,
    *,
    surface: str,
    row: Mapping[str, Any] | None = None,
    extra: Mapping[str, Any] | None = None,
    updated_ts_ns: int | None = None,
) -> dict[str, Any]:
    live_contract_name = replay_live_contract_name(surface)
    payload = build_replay_live_shape_payload(surface=surface, row=row, extra=extra)
    state = transport.write_state(
        live_contract_name=live_contract_name,
        surface=surface,
        payload=payload,
        updated_ts_ns=updated_ts_ns,
    )
    assert_live_shape_state(state)
    return state


def replay_live_shape_key(*, run_id: str, surface: str, kind: str) -> str:
    return replay_key_for(replay_live_contract_name(surface), run_id=run_id, kind=kind)


def replay_live_adapter_contract_summary() -> dict[str, Any]:
    return {
        "schema_version": REPLAY_LIVE_ADAPTER_CONTRACT_VERSION,
        "live_contract_names": dict(LIVE_CONTRACT_NAMES),
        "replay_only": True,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "production_doctrine_changed": False,
    }


try:
    __all__
except NameError:
    __all__ = tuple()

__all__ = tuple(dict.fromkeys(tuple(__all__) + (
    "REPLAY_LIVE_ADAPTER_CONTRACT_VERSION",
    "LIVE_CONTRACT_NAMES",
    "replay_live_contract_name",
    "build_replay_live_shape_payload",
    "publish_replay_live_shape",
    "write_replay_live_state",
    "replay_live_shape_key",
    "replay_live_adapter_contract_summary",
)))
