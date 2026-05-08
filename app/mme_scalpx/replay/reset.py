from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

from app.mme_scalpx.replay.safety import (
    assert_replay_artifact_path,
    assert_replay_config_path,
    assert_runtime_mode_not_promoted,
)


REPLAY_RESET_CONTRACT_VERSION = "replay_reset_contract_v1"

REPLAY_RESET_COMPONENTS = (
    "replay_clock",
    "local_replay_transport",
    "feature_state",
    "strategy_state",
    "risk_state",
    "execution_shadow_state",
    "misr_consumed_trap_event_registry",
    "miso_consumed_burst_event_registry",
    "cooldown_state",
    "position_state",
    "artifact_state",
)


@dataclass(frozen=True)
class ReplayResetState:
    """Deterministic replay reset state.

    This dataclass is replay-only. It does not touch live Redis, live broker
    state, execution truth, production doctrine, or runtime mode.
    """

    schema_version: str = REPLAY_RESET_CONTRACT_VERSION
    run_id: str = ""
    replay_clock_ns: int = 0
    local_replay_transport_seq: int = 0
    feature_state: tuple[tuple[str, Any], ...] = field(default_factory=tuple)
    strategy_state: tuple[tuple[str, Any], ...] = field(default_factory=tuple)
    risk_state: tuple[tuple[str, Any], ...] = field(default_factory=tuple)
    execution_shadow_state: tuple[tuple[str, Any], ...] = field(default_factory=tuple)
    misr_consumed_trap_event_registry: tuple[str, ...] = field(default_factory=tuple)
    miso_consumed_burst_event_registry: tuple[str, ...] = field(default_factory=tuple)
    cooldown_state: tuple[tuple[str, Any], ...] = field(default_factory=tuple)
    position_state: tuple[tuple[str, Any], ...] = field(default_factory=tuple)
    artifact_state: tuple[tuple[str, Any], ...] = field(default_factory=tuple)
    reset_reason: str = "deterministic_replay_reset"
    paper_armed_approved: bool = False
    live_trading_approved: bool = False
    execution_arming_created: bool = False
    production_doctrine_changed: bool = False


def _freeze_mapping(value: Mapping[str, Any] | None) -> tuple[tuple[str, Any], ...]:
    if not value:
        return tuple()
    return tuple((str(k), value[k]) for k in sorted(value))


def replay_empty_reset_state(*, run_id: str = "") -> ReplayResetState:
    return ReplayResetState(run_id=str(run_id or ""))


def build_replay_reset_state(
    *,
    run_id: str = "",
    replay_clock_ns: int = 0,
    feature_state: Mapping[str, Any] | None = None,
    strategy_state: Mapping[str, Any] | None = None,
    risk_state: Mapping[str, Any] | None = None,
    execution_shadow_state: Mapping[str, Any] | None = None,
    misr_consumed_trap_event_registry: tuple[str, ...] | list[str] | None = None,
    miso_consumed_burst_event_registry: tuple[str, ...] | list[str] | None = None,
    cooldown_state: Mapping[str, Any] | None = None,
    position_state: Mapping[str, Any] | None = None,
    artifact_state: Mapping[str, Any] | None = None,
) -> ReplayResetState:
    assert_runtime_mode_not_promoted("replay")
    return ReplayResetState(
        run_id=str(run_id or ""),
        replay_clock_ns=int(replay_clock_ns),
        feature_state=_freeze_mapping(feature_state),
        strategy_state=_freeze_mapping(strategy_state),
        risk_state=_freeze_mapping(risk_state),
        execution_shadow_state=_freeze_mapping(execution_shadow_state),
        misr_consumed_trap_event_registry=tuple(sorted(str(x) for x in (misr_consumed_trap_event_registry or ()))),
        miso_consumed_burst_event_registry=tuple(sorted(str(x) for x in (miso_consumed_burst_event_registry or ()))),
        cooldown_state=_freeze_mapping(cooldown_state),
        position_state=_freeze_mapping(position_state),
        artifact_state=_freeze_mapping(artifact_state),
    )


def replay_reset_state_to_dict(state: ReplayResetState) -> dict[str, Any]:
    payload = asdict(state)
    payload["reset_components"] = REPLAY_RESET_COMPONENTS
    payload["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    return payload


def replay_reset_state_canonical_json(state: ReplayResetState) -> str:
    payload = asdict(state)
    payload["reset_components"] = REPLAY_RESET_COMPONENTS
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def replay_reset_manifest(
    *,
    run_id: str,
    artifact_path: str,
    config_path: str,
    state: ReplayResetState | None = None,
) -> dict[str, Any]:
    assert_replay_artifact_path(artifact_path)
    assert_replay_config_path(config_path)
    reset_state = state or replay_empty_reset_state(run_id=run_id)
    return {
        "schema_version": REPLAY_RESET_CONTRACT_VERSION,
        "run_id": run_id,
        "artifact_path": str(artifact_path),
        "config_path": str(config_path),
        "reset_components": REPLAY_RESET_COMPONENTS,
        "reset_state": replay_reset_state_to_dict(reset_state),
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "production_doctrine_changed": False,
    }


def assert_replay_reset_clean(state: ReplayResetState) -> bool:
    if state.paper_armed_approved is not False:
        raise AssertionError("reset state must not approve paper_armed")
    if state.live_trading_approved is not False:
        raise AssertionError("reset state must not approve live trading")
    if state.execution_arming_created is not False:
        raise AssertionError("reset state must not create execution arming")
    if state.production_doctrine_changed is not False:
        raise AssertionError("reset state must not mutate production doctrine")
    if state.misr_consumed_trap_event_registry:
        raise AssertionError("MISR consumed trap event registry must reset clean")
    if state.miso_consumed_burst_event_registry:
        raise AssertionError("MISO consumed burst event registry must reset clean")
    return True


try:
    __all__
except NameError:
    __all__ = tuple()

__all__ = tuple(dict.fromkeys(tuple(__all__) + (
    "REPLAY_RESET_CONTRACT_VERSION",
    "REPLAY_RESET_COMPONENTS",
    "ReplayResetState",
    "replay_empty_reset_state",
    "build_replay_reset_state",
    "replay_reset_state_to_dict",
    "replay_reset_state_canonical_json",
    "replay_reset_manifest",
    "assert_replay_reset_clean",
)))
