"""Lane D D2 sweep-space contract surfaces.

This module defines research-only sweep-space structures and deterministic
candidate-row generation. It must remain offline-only and must not execute
replay, train ML, call brokers, write live Redis, or mutate strategy doctrine.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
from typing import Any, Iterable, Sequence

from .contracts import (
    REGIMES,
    SIDES,
    STRATEGY_FAMILIES,
    SweepCandidateRow,
    validate_regime,
    validate_side,
    validate_strategy_family,
)

SWEEP_SPACE_CONTRACT_VERSION = "replay_optimization_d2_sweep_space_contract_v1"
SWEEP_GENERATION_MODE_ONE_FACTOR = "ONE_FACTOR_AT_A_TIME"
SWEEP_GENERATION_MODE_CARTESIAN_CAPPED = "CARTESIAN_CAPPED_CONTRACT_ONLY"

ALLOWED_PARAMETER_GROUPS = (
    "entry_filters",
    "exit_controls",
    "raw_filters",
    "risk_controls_research_only",
)

DEFAULT_MAX_CANDIDATES = 10000


@dataclass(frozen=True, slots=True)
class SweepParameterSpec:
    parameter_group: str
    parameter_name: str
    baseline_value: str
    candidate_values: tuple[str, ...]
    value_type: str = "string"
    unit: str | None = None
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class RawFilterSpec:
    feature_family: str
    feature_name: str
    threshold_values: tuple[str, ...]
    comparator: str = ">="
    required_source: str = "research_gate_or_research_capture"
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class SweepSpaceSpec:
    contract_version: str = SWEEP_SPACE_CONTRACT_VERSION
    generation_mode: str = SWEEP_GENERATION_MODE_ONE_FACTOR
    strategy_families: tuple[str, ...] = STRATEGY_FAMILIES
    sides: tuple[str, ...] = SIDES
    regimes: tuple[str, ...] = REGIMES
    parameter_specs: tuple[SweepParameterSpec, ...] = field(default_factory=tuple)
    raw_filter_specs: tuple[RawFilterSpec, ...] = field(default_factory=tuple)
    max_candidates: int = DEFAULT_MAX_CANDIDATES
    accepted_for: str = "CONTRACT_ONLY"
    remarks: str | None = None


def _stable_id(parts: Sequence[Any]) -> str:
    raw = "|".join("" if p is None else str(p) for p in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def _to_float(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def canonical_parameter_specs() -> tuple[SweepParameterSpec, ...]:
    return (
        SweepParameterSpec(
            parameter_group="entry_filters",
            parameter_name="FUT_VOL_NORM_MIN",
            baseline_value="1.10",
            candidate_values=("0.95", "1.10", "1.25", "1.40"),
            value_type="float",
            unit="ratio",
            remarks="Research-only futures volume threshold sweep.",
        ),
        SweepParameterSpec(
            parameter_group="entry_filters",
            parameter_name="SPREAD_RATIO_MAX",
            baseline_value="1.70",
            candidate_values=("1.45", "1.60", "1.70", "1.85"),
            value_type="float",
            unit="ratio",
            remarks="Research-only selected-option spread threshold sweep.",
        ),
        SweepParameterSpec(
            parameter_group="exit_controls",
            parameter_name="target_points",
            baseline_value="5.0",
            candidate_values=("4.0", "5.0", "6.0", "8.0"),
            value_type="float",
            unit="option_points",
            remarks="Research-only target tightening/loosening sweep.",
        ),
        SweepParameterSpec(
            parameter_group="exit_controls",
            parameter_name="hard_stop_points",
            baseline_value="4.0",
            candidate_values=("3.0", "4.0", "5.0"),
            value_type="float",
            unit="option_points",
            remarks="Research-only hard-stop sweep.",
        ),
        SweepParameterSpec(
            parameter_group="exit_controls",
            parameter_name="profit_stall_points",
            baseline_value="3.0",
            candidate_values=("2.0", "3.0", "4.0"),
            value_type="float",
            unit="option_points",
            remarks="Research-only profit-stall sweep.",
        ),
        SweepParameterSpec(
            parameter_group="exit_controls",
            parameter_name="time_stall_seconds",
            baseline_value="12.0",
            candidate_values=("8.0", "12.0", "16.0", "20.0"),
            value_type="float",
            unit="seconds",
            remarks="Research-only time-stall sweep.",
        ),
    )


def canonical_raw_filter_specs() -> tuple[RawFilterSpec, ...]:
    return (
        RawFilterSpec(
            feature_family="oi_wall",
            feature_name="oi_wall_strength_min",
            threshold_values=("0.50", "0.65", "0.80"),
            comparator=">=",
            required_source="research_gate",
            remarks="Research-only OI wall strength filter sweep.",
        ),
        RawFilterSpec(
            feature_family="microstructure",
            feature_name="tape_speed_score_min",
            threshold_values=("0.50", "0.70"),
            comparator=">=",
            required_source="research_capture",
            remarks="Research-only tape speed filter sweep.",
        ),
    )


def default_sweep_space() -> SweepSpaceSpec:
    return SweepSpaceSpec(
        parameter_specs=canonical_parameter_specs(),
        raw_filter_specs=canonical_raw_filter_specs(),
        remarks="D2 canonical research-only seed sweep space.",
    )


def validate_sweep_space(space: SweepSpaceSpec) -> SweepSpaceSpec:
    if space.accepted_for != "CONTRACT_ONLY":
        raise ValueError("D2 sweep space must remain CONTRACT_ONLY")
    if space.generation_mode not in {
        SWEEP_GENERATION_MODE_ONE_FACTOR,
        SWEEP_GENERATION_MODE_CARTESIAN_CAPPED,
    }:
        raise ValueError(f"unknown generation_mode: {space.generation_mode}")
    if space.max_candidates <= 0:
        raise ValueError("max_candidates must be positive")
    for strategy in space.strategy_families:
        validate_strategy_family(strategy)
    for side in space.sides:
        validate_side(side)
    for regime in space.regimes:
        validate_regime(regime)
    for spec in space.parameter_specs:
        if spec.parameter_group not in ALLOWED_PARAMETER_GROUPS:
            raise ValueError(f"unknown parameter_group: {spec.parameter_group}")
        if not spec.parameter_name:
            raise ValueError("parameter_name cannot be empty")
        if not spec.candidate_values:
            raise ValueError(f"candidate_values empty for {spec.parameter_name}")
    for spec in space.raw_filter_specs:
        if not spec.feature_family or not spec.feature_name:
            raise ValueError("raw filter feature_family and feature_name are required")
        if not spec.threshold_values:
            raise ValueError(f"threshold_values empty for {spec.feature_name}")
    return space


def _candidate_from_parameter(
    optimization_id: str,
    strategy: str,
    side: str,
    regime: str,
    spec: SweepParameterSpec,
    candidate_value: str,
) -> SweepCandidateRow:
    candidate_id = "D2_" + _stable_id(
        (
            optimization_id,
            strategy,
            side,
            regime,
            spec.parameter_group,
            spec.parameter_name,
            candidate_value,
        )
    )

    target_points = None
    hard_stop_points = None
    profit_stall_points = None
    time_stall_seconds = None

    if spec.parameter_group == "exit_controls":
        if spec.parameter_name == "target_points":
            target_points = _to_float(candidate_value)
        elif spec.parameter_name == "hard_stop_points":
            hard_stop_points = _to_float(candidate_value)
        elif spec.parameter_name == "profit_stall_points":
            profit_stall_points = _to_float(candidate_value)
        elif spec.parameter_name == "time_stall_seconds":
            time_stall_seconds = _to_float(candidate_value)

    return SweepCandidateRow(
        optimization_id=optimization_id,
        candidate_id=candidate_id,
        strategy_family=strategy,
        side=side,
        regime=regime,
        parameter_group=spec.parameter_group,
        parameter_name=spec.parameter_name,
        baseline_value=spec.baseline_value,
        candidate_value=candidate_value,
        target_points=target_points,
        hard_stop_points=hard_stop_points,
        profit_stall_points=profit_stall_points,
        time_stall_seconds=time_stall_seconds,
        status="PROPOSED_ONLY",
        remarks="D2 contract-generated research-only candidate.",
    )


def _candidate_from_raw_filter(
    optimization_id: str,
    strategy: str,
    side: str,
    regime: str,
    spec: RawFilterSpec,
    threshold_value: str,
) -> SweepCandidateRow:
    candidate_id = "D2_" + _stable_id(
        (
            optimization_id,
            strategy,
            side,
            regime,
            "raw_filters",
            spec.feature_family,
            spec.feature_name,
            threshold_value,
        )
    )

    return SweepCandidateRow(
        optimization_id=optimization_id,
        candidate_id=candidate_id,
        strategy_family=strategy,
        side=side,
        regime=regime,
        parameter_group="raw_filters",
        parameter_name=spec.feature_name,
        baseline_value="research_only_baseline",
        candidate_value=threshold_value,
        raw_filter_family=spec.feature_family,
        raw_filter_name=spec.feature_name,
        raw_filter_threshold=f"{spec.comparator}{threshold_value}",
        status="PROPOSED_ONLY",
        remarks="D2 contract-generated RAW filter candidate.",
    )


def generate_sweep_candidates(
    optimization_id: str,
    space: SweepSpaceSpec | None = None,
    *,
    max_candidates: int | None = None,
) -> tuple[SweepCandidateRow, ...]:
    active_space = validate_sweep_space(space or default_sweep_space())
    cap = max_candidates if max_candidates is not None else active_space.max_candidates
    if cap <= 0:
        raise ValueError("max_candidates must be positive")

    rows: list[SweepCandidateRow] = []
    for strategy in active_space.strategy_families:
        for side in active_space.sides:
            for regime in active_space.regimes:
                for spec in active_space.parameter_specs:
                    for candidate_value in spec.candidate_values:
                        rows.append(
                            _candidate_from_parameter(
                                optimization_id,
                                strategy,
                                side,
                                regime,
                                spec,
                                candidate_value,
                            )
                        )
                        if len(rows) >= cap:
                            return tuple(rows)
                for spec in active_space.raw_filter_specs:
                    for threshold_value in spec.threshold_values:
                        rows.append(
                            _candidate_from_raw_filter(
                                optimization_id,
                                strategy,
                                side,
                                regime,
                                spec,
                                threshold_value,
                            )
                        )
                        if len(rows) >= cap:
                            return tuple(rows)
    return tuple(rows)


def sweep_space_to_dict(space: SweepSpaceSpec) -> dict[str, Any]:
    return asdict(validate_sweep_space(space))


def candidate_rows_to_dicts(rows: Iterable[SweepCandidateRow]) -> list[dict[str, Any]]:
    return [asdict(row) for row in rows]


def sweep_contract_summary() -> dict[str, Any]:
    space = default_sweep_space()
    rows = generate_sweep_candidates("D2_SUMMARY", space)
    return {
        "contract_version": SWEEP_SPACE_CONTRACT_VERSION,
        "accepted_for": "CONTRACT_ONLY",
        "generation_mode": space.generation_mode,
        "strategy_families": space.strategy_families,
        "sides": space.sides,
        "regimes": space.regimes,
        "parameter_spec_count": len(space.parameter_specs),
        "raw_filter_spec_count": len(space.raw_filter_specs),
        "generated_candidate_count": len(rows),
        "replay_execution_performed": False,
        "ml_training_performed": False,
        "broker_calls_allowed": False,
        "live_redis_writes_allowed": False,
        "paper_live_approved": False,
    }


__all__ = (
    "SWEEP_SPACE_CONTRACT_VERSION",
    "SWEEP_GENERATION_MODE_ONE_FACTOR",
    "SWEEP_GENERATION_MODE_CARTESIAN_CAPPED",
    "ALLOWED_PARAMETER_GROUPS",
    "DEFAULT_MAX_CANDIDATES",
    "SweepParameterSpec",
    "RawFilterSpec",
    "SweepSpaceSpec",
    "canonical_parameter_specs",
    "canonical_raw_filter_specs",
    "default_sweep_space",
    "validate_sweep_space",
    "generate_sweep_candidates",
    "sweep_space_to_dict",
    "candidate_rows_to_dicts",
    "sweep_contract_summary",
)
