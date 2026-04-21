"""
app/mme_scalpx/replay/topology.py

Freeze-grade replay topology layer for the MME-ScalpX Permanent Replay &
Validation Framework.

Topology responsibilities
-------------------------
This module owns:
- canonical replay stage taxonomy
- replay scope -> stage-chain mapping
- deterministic topology plan construction
- topology validation helpers
- topology serialization helpers

This module does not own:
- replay run-id or artifact planning
- dataset discovery/loading
- selection policy
- replay clock mechanics
- payload injection
- live service supervision
- experiment logic
- report generation
- doctrine logic

Design rules
------------
- topology truth must be explicit and centralized
- scope mapping must be deterministic and auditable
- stage ordering must be stable
- no hidden assumptions beyond frozen replay scope contract
- topology must be reusable by locked, shadow, and differential replay equally
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from .modes import ReplayScope


class ReplayTopologyError(RuntimeError):
    """Base exception for replay topology failures."""


class ReplayTopologyValidationError(ReplayTopologyError):
    """Raised when a replay topology definition or request is invalid."""


STAGE_FEEDS = "feeds"
STAGE_FEATURES = "features"
STAGE_STRATEGY = "strategy"
STAGE_RISK = "risk"
STAGE_EXECUTION_SHADOW = "execution_shadow"

CANONICAL_STAGE_ORDER: tuple[str, ...] = (
    STAGE_FEEDS,
    STAGE_FEATURES,
    STAGE_STRATEGY,
    STAGE_RISK,
    STAGE_EXECUTION_SHADOW,
)

SCOPE_STAGE_MAP: Mapping[ReplayScope, tuple[str, ...]] = {
    ReplayScope.FEEDS_ONLY: (
        STAGE_FEEDS,
    ),
    ReplayScope.FEEDS_FEATURES: (
        STAGE_FEEDS,
        STAGE_FEATURES,
    ),
    ReplayScope.FEEDS_FEATURES_STRATEGY: (
        STAGE_FEEDS,
        STAGE_FEATURES,
        STAGE_STRATEGY,
    ),
    ReplayScope.FEEDS_FEATURES_STRATEGY_RISK: (
        STAGE_FEEDS,
        STAGE_FEATURES,
        STAGE_STRATEGY,
        STAGE_RISK,
    ),
    ReplayScope.FEEDS_FEATURES_STRATEGY_RISK_EXECUTION_SHADOW: (
        STAGE_FEEDS,
        STAGE_FEATURES,
        STAGE_STRATEGY,
        STAGE_RISK,
        STAGE_EXECUTION_SHADOW,
    ),
    ReplayScope.FULL_SYSTEM_REPLAY: (
        STAGE_FEEDS,
        STAGE_FEATURES,
        STAGE_STRATEGY,
        STAGE_RISK,
        STAGE_EXECUTION_SHADOW,
    ),
}


@dataclass(frozen=True, slots=True)
class ReplayStageDefinition:
    """
    Canonical replay stage definition.
    """

    stage_name: str
    order_index: int
    description: str
    owns_runtime_decisioning: bool
    terminal_stage: bool = False


@dataclass(frozen=True, slots=True)
class ReplayTopologyPlan:
    """
    Canonical resolved topology plan.
    """

    scope: ReplayScope
    stages: tuple[ReplayStageDefinition, ...]
    stage_names: tuple[str, ...]
    topology_fingerprint: str
    notes: tuple[str, ...] = field(default_factory=tuple)


class ReplayTopologyBuilder:
    """
    Freeze-grade replay topology builder.
    """

    def __init__(
        self,
        *,
        canonical_stage_order: Sequence[str] = CANONICAL_STAGE_ORDER,
        scope_stage_map: Mapping[ReplayScope, Sequence[str]] = SCOPE_STAGE_MAP,
    ) -> None:
        self._canonical_stage_order = _normalize_stage_order(canonical_stage_order)
        self._scope_stage_map = _normalize_scope_stage_map(
            scope_stage_map=scope_stage_map,
            canonical_stage_order=self._canonical_stage_order,
        )

    @property
    def canonical_stage_order(self) -> tuple[str, ...]:
        return self._canonical_stage_order

    @property
    def scope_stage_map(self) -> Mapping[ReplayScope, tuple[str, ...]]:
        return self._scope_stage_map

    def build_plan(
        self,
        scope: ReplayScope,
        *,
        notes: Sequence[str] | None = None,
    ) -> ReplayTopologyPlan:
        if scope not in self._scope_stage_map:
            raise ReplayTopologyValidationError(f"unsupported replay scope: {scope!r}")

        stage_names = self._scope_stage_map[scope]
        stages = self._build_stage_definitions(stage_names)
        topology_fingerprint = _stable_sha256_json(
            {
                "scope": scope.value,
                "stage_names": list(stage_names),
                "stages": [stage_definition_to_dict(stage) for stage in stages],
            }
        )

        return ReplayTopologyPlan(
            scope=scope,
            stages=stages,
            stage_names=stage_names,
            topology_fingerprint=topology_fingerprint,
            notes=tuple(notes or ()),
        )

    def stages_for_scope(self, scope: ReplayScope) -> tuple[str, ...]:
        if scope not in self._scope_stage_map:
            raise ReplayTopologyValidationError(f"unsupported replay scope: {scope!r}")
        return self._scope_stage_map[scope]

    def has_stage(self, scope: ReplayScope, stage_name: str) -> bool:
        return stage_name in self.stages_for_scope(scope)

    def terminal_stage_for_scope(self, scope: ReplayScope) -> str:
        stages = self.stages_for_scope(scope)
        if not stages:
            raise ReplayTopologyValidationError(
                f"scope {scope.value!r} has no stage chain"
            )
        return stages[-1]

    def _build_stage_definitions(
        self,
        stage_names: Sequence[str],
    ) -> tuple[ReplayStageDefinition, ...]:
        built: list[ReplayStageDefinition] = []
        terminal = stage_names[-1]

        for stage_name in stage_names:
            built.append(
                ReplayStageDefinition(
                    stage_name=stage_name,
                    order_index=self._canonical_stage_order.index(stage_name),
                    description=_stage_description(stage_name),
                    owns_runtime_decisioning=_owns_runtime_decisioning(stage_name),
                    terminal_stage=(stage_name == terminal),
                )
            )

        return tuple(built)


def build_topology_plan(
    scope: ReplayScope,
    *,
    notes: Sequence[str] | None = None,
    canonical_stage_order: Sequence[str] = CANONICAL_STAGE_ORDER,
    scope_stage_map: Mapping[ReplayScope, Sequence[str]] = SCOPE_STAGE_MAP,
) -> ReplayTopologyPlan:
    builder = ReplayTopologyBuilder(
        canonical_stage_order=canonical_stage_order,
        scope_stage_map=scope_stage_map,
    )
    return builder.build_plan(scope=scope, notes=notes)


def topology_plan_to_dict(plan: ReplayTopologyPlan) -> dict[str, Any]:
    return {
        "scope": plan.scope.value,
        "stages": [stage_definition_to_dict(stage) for stage in plan.stages],
        "stage_names": list(plan.stage_names),
        "topology_fingerprint": plan.topology_fingerprint,
        "notes": list(plan.notes),
    }


def stage_definition_to_dict(stage: ReplayStageDefinition) -> dict[str, Any]:
    return {
        "stage_name": stage.stage_name,
        "order_index": stage.order_index,
        "description": stage.description,
        "owns_runtime_decisioning": stage.owns_runtime_decisioning,
        "terminal_stage": stage.terminal_stage,
    }


def _normalize_stage_order(stage_order: Sequence[str]) -> tuple[str, ...]:
    normalized = tuple(stage_order)
    if not normalized:
        raise ReplayTopologyValidationError("canonical_stage_order must be non-empty")

    if len(set(normalized)) != len(normalized):
        raise ReplayTopologyValidationError(
            f"canonical_stage_order contains duplicates: {normalized!r}"
        )

    expected = set(CANONICAL_STAGE_ORDER)
    actual = set(normalized)
    if actual != expected:
        raise ReplayTopologyValidationError(
            "canonical_stage_order must contain exactly the canonical stage set; "
            f"expected={sorted(expected)!r}, got={sorted(actual)!r}"
        )

    return normalized


def _normalize_scope_stage_map(
    *,
    scope_stage_map: Mapping[ReplayScope, Sequence[str]],
    canonical_stage_order: Sequence[str],
) -> Mapping[ReplayScope, tuple[str, ...]]:
    normalized: dict[ReplayScope, tuple[str, ...]] = {}

    expected_scopes = set(SCOPE_STAGE_MAP.keys())
    actual_scopes = set(scope_stage_map.keys())
    if actual_scopes != expected_scopes:
        raise ReplayTopologyValidationError(
            "scope_stage_map must contain exactly the frozen replay scopes; "
            f"expected={sorted(scope.value for scope in expected_scopes)!r}, "
            f"got={sorted(scope.value for scope in actual_scopes)!r}"
        )

    canonical_index = {stage: idx for idx, stage in enumerate(canonical_stage_order)}

    for scope in sorted(scope_stage_map.keys(), key=lambda item: item.value):
        stages = tuple(scope_stage_map[scope])
        if not stages:
            raise ReplayTopologyValidationError(
                f"scope {scope.value!r} must contain at least one stage"
            )
        if len(set(stages)) != len(stages):
            raise ReplayTopologyValidationError(
                f"scope {scope.value!r} contains duplicate stages: {stages!r}"
            )

        for stage in stages:
            if stage not in canonical_index:
                raise ReplayTopologyValidationError(
                    f"scope {scope.value!r} contains unknown stage {stage!r}"
                )

        stage_indexes = [canonical_index[stage] for stage in stages]
        if stage_indexes != sorted(stage_indexes):
            raise ReplayTopologyValidationError(
                f"scope {scope.value!r} stages are not in canonical order: {stages!r}"
            )

        if stage_indexes != list(range(stage_indexes[0], stage_indexes[-1] + 1)):
            raise ReplayTopologyValidationError(
                f"scope {scope.value!r} stages must form a contiguous canonical chain: {stages!r}"
            )

        if stages[0] != STAGE_FEEDS:
            raise ReplayTopologyValidationError(
                f"scope {scope.value!r} must start with {STAGE_FEEDS!r}, got {stages[0]!r}"
            )

        normalized[scope] = stages

    return normalized


def _stage_description(stage_name: str) -> str:
    descriptions = {
        STAGE_FEEDS: "Replay input publication / feed-stage chain entry.",
        STAGE_FEATURES: "Feature computation stage driven from replayed feed truth.",
        STAGE_STRATEGY: "Strategy decision stage driven from replay feature truth.",
        STAGE_RISK: "Risk gating stage applied to replay strategy outputs.",
        STAGE_EXECUTION_SHADOW: "Replay-only execution shadow stage with no live side effects.",
    }
    try:
        return descriptions[stage_name]
    except KeyError as exc:
        raise ReplayTopologyValidationError(
            f"no canonical description defined for stage {stage_name!r}"
        ) from exc


def _owns_runtime_decisioning(stage_name: str) -> bool:
    return stage_name in (
        STAGE_FEATURES,
        STAGE_STRATEGY,
        STAGE_RISK,
        STAGE_EXECUTION_SHADOW,
    )


def _stable_sha256_json(value: Mapping[str, Any]) -> str:
    import hashlib
    import json

    text = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


__all__ = [
    "ReplayTopologyError",
    "ReplayTopologyValidationError",
    "STAGE_FEEDS",
    "STAGE_FEATURES",
    "STAGE_STRATEGY",
    "STAGE_RISK",
    "STAGE_EXECUTION_SHADOW",
    "CANONICAL_STAGE_ORDER",
    "SCOPE_STAGE_MAP",
    "ReplayStageDefinition",
    "ReplayTopologyPlan",
    "ReplayTopologyBuilder",
    "build_topology_plan",
    "topology_plan_to_dict",
    "stage_definition_to_dict",
]
