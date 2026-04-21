"""
app/mme_scalpx/replay/experiments.py

Freeze-grade replay experiment layer for the MME-ScalpX Permanent Replay &
Validation Framework.

Experiment responsibilities
---------------------------
This module owns:
- canonical replay experiment contracts
- baseline vs shadow experiment bundle shaping
- explicit override-pack attachment
- deterministic experiment serialization helpers
- experiment validation

This module does not own:
- dataset discovery/loading
- replay execution orchestration
- artifact persistence
- doctrine mutation
- live runtime config mutation
- report interpretation

Design rules
------------
- experiments must remain explicit and auditable
- baseline and shadow must remain cleanly separated
- overrides are shadow-only inputs, never silent baseline mutation
- experiment assembly must be deterministic
- no hidden config inference
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from .modes import DoctrineMode, ExperimentFamily
from .overrides import (
    ReplayOverridePack,
    override_pack_to_dict,
)


class ReplayExperimentsError(RuntimeError):
    """Base exception for replay experiment failures."""


class ReplayExperimentsValidationError(ReplayExperimentsError):
    """Raised when experiment definitions or bundles are invalid."""


@dataclass(frozen=True, slots=True)
class ReplayExperimentDefinition:
    """
    Canonical replay experiment definition.
    """

    experiment_id: str
    family: ExperimentFamily
    doctrine_mode: DoctrineMode
    label: str
    override_pack: ReplayOverridePack | None = None
    baseline_ref: str | None = None
    notes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class ReplayExperimentBundle:
    """
    Canonical experiment bundle for replay orchestration.
    """

    baseline: ReplayExperimentDefinition
    shadow: ReplayExperimentDefinition | None = None
    notes: tuple[str, ...] = field(default_factory=tuple)

    @property
    def has_shadow(self) -> bool:
        return self.shadow is not None

    @property
    def experiment_ids(self) -> tuple[str, ...]:
        if self.shadow is None:
            return (self.baseline.experiment_id,)
        return (self.baseline.experiment_id, self.shadow.experiment_id)


class ReplayExperimentsManager:
    """
    Freeze-grade replay experiments manager.
    """

    def validate_definition(self, definition: ReplayExperimentDefinition) -> None:
        _validate_experiment_definition(definition)

    def build_baseline(
        self,
        *,
        experiment_id: str,
        family: ExperimentFamily,
        label: str,
        baseline_ref: str | None = None,
        notes: Sequence[str] = (),
    ) -> ReplayExperimentDefinition:
        definition = ReplayExperimentDefinition(
            experiment_id=experiment_id,
            family=family,
            doctrine_mode=DoctrineMode.LOCKED,
            label=label,
            override_pack=None,
            baseline_ref=baseline_ref,
            notes=tuple(notes),
        )
        _validate_experiment_definition(definition)
        return definition

    def build_shadow(
        self,
        *,
        experiment_id: str,
        family: ExperimentFamily,
        label: str,
        override_pack: ReplayOverridePack,
        baseline_ref: str | None = None,
        notes: Sequence[str] = (),
    ) -> ReplayExperimentDefinition:
        definition = ReplayExperimentDefinition(
            experiment_id=experiment_id,
            family=family,
            doctrine_mode=DoctrineMode.SHADOW,
            label=label,
            override_pack=override_pack,
            baseline_ref=baseline_ref,
            notes=tuple(notes),
        )
        _validate_experiment_definition(definition)
        return definition

    def build_bundle(
        self,
        *,
        baseline: ReplayExperimentDefinition,
        shadow: ReplayExperimentDefinition | None = None,
        notes: Sequence[str] = (),
    ) -> ReplayExperimentBundle:
        _validate_experiment_definition(baseline)

        if baseline.doctrine_mode is not DoctrineMode.LOCKED:
            raise ReplayExperimentsValidationError(
                "baseline experiment must use doctrine_mode=locked"
            )

        if shadow is not None:
            _validate_experiment_definition(shadow)
            if shadow.doctrine_mode is not DoctrineMode.SHADOW:
                raise ReplayExperimentsValidationError(
                    "shadow experiment must use doctrine_mode=shadow"
                )
            if shadow.family is not baseline.family:
                raise ReplayExperimentsValidationError(
                    "baseline and shadow experiment families must match"
                )
            if shadow.experiment_id == baseline.experiment_id:
                raise ReplayExperimentsValidationError(
                    "baseline and shadow experiment_id must be distinct"
                )

        bundle = ReplayExperimentBundle(
            baseline=baseline,
            shadow=shadow,
            notes=tuple(notes),
        )
        _validate_experiment_bundle(bundle)
        return bundle


def validate_experiment_definition(definition: ReplayExperimentDefinition) -> None:
    _validate_experiment_definition(definition)


def validate_experiment_bundle(bundle: ReplayExperimentBundle) -> None:
    _validate_experiment_bundle(bundle)


def experiment_definition_to_dict(
    definition: ReplayExperimentDefinition,
) -> dict[str, Any]:
    return {
        "experiment_id": definition.experiment_id,
        "family": definition.family.value,
        "doctrine_mode": definition.doctrine_mode.value,
        "label": definition.label,
        "override_pack": (
            override_pack_to_dict(definition.override_pack)
            if definition.override_pack is not None
            else None
        ),
        "baseline_ref": definition.baseline_ref,
        "notes": list(definition.notes),
    }


def experiment_bundle_to_dict(
    bundle: ReplayExperimentBundle,
) -> dict[str, Any]:
    return {
        "baseline": experiment_definition_to_dict(bundle.baseline),
        "shadow": (
            experiment_definition_to_dict(bundle.shadow)
            if bundle.shadow is not None
            else None
        ),
        "has_shadow": bundle.has_shadow,
        "experiment_ids": list(bundle.experiment_ids),
        "notes": list(bundle.notes),
    }


def build_baseline_experiment(
    *,
    experiment_id: str,
    family: ExperimentFamily,
    label: str,
    baseline_ref: str | None = None,
    notes: Sequence[str] = (),
) -> ReplayExperimentDefinition:
    manager = ReplayExperimentsManager()
    return manager.build_baseline(
        experiment_id=experiment_id,
        family=family,
        label=label,
        baseline_ref=baseline_ref,
        notes=notes,
    )


def build_shadow_experiment(
    *,
    experiment_id: str,
    family: ExperimentFamily,
    label: str,
    override_pack: ReplayOverridePack,
    baseline_ref: str | None = None,
    notes: Sequence[str] = (),
) -> ReplayExperimentDefinition:
    manager = ReplayExperimentsManager()
    return manager.build_shadow(
        experiment_id=experiment_id,
        family=family,
        label=label,
        override_pack=override_pack,
        baseline_ref=baseline_ref,
        notes=notes,
    )


def build_experiment_bundle(
    *,
    baseline: ReplayExperimentDefinition,
    shadow: ReplayExperimentDefinition | None = None,
    notes: Sequence[str] = (),
) -> ReplayExperimentBundle:
    manager = ReplayExperimentsManager()
    return manager.build_bundle(
        baseline=baseline,
        shadow=shadow,
        notes=notes,
    )


def _validate_experiment_definition(definition: ReplayExperimentDefinition) -> None:
    if not isinstance(definition.experiment_id, str) or not definition.experiment_id.strip():
        raise ReplayExperimentsValidationError(
            f"experiment_id must be non-empty string, got {definition.experiment_id!r}"
        )

    if not isinstance(definition.label, str) or not definition.label.strip():
        raise ReplayExperimentsValidationError(
            f"label must be non-empty string, got {definition.label!r}"
        )

    if definition.doctrine_mode is DoctrineMode.LOCKED:
        if definition.override_pack is not None:
            raise ReplayExperimentsValidationError(
                "locked baseline experiment must not carry override_pack"
            )

    elif definition.doctrine_mode is DoctrineMode.SHADOW:
        if definition.override_pack is None:
            raise ReplayExperimentsValidationError(
                "shadow experiment must carry override_pack"
            )

    else:
        raise ReplayExperimentsValidationError(
            "experiment layer supports only locked baseline and shadow definitions"
        )

    for note in definition.notes:
        if not isinstance(note, str):
            raise ReplayExperimentsValidationError(
                f"experiment note must be string, got {note!r}"
            )


def _validate_experiment_bundle(bundle: ReplayExperimentBundle) -> None:
    _validate_experiment_definition(bundle.baseline)

    if bundle.baseline.doctrine_mode is not DoctrineMode.LOCKED:
        raise ReplayExperimentsValidationError(
            "bundle baseline must use doctrine_mode=locked"
        )

    if bundle.shadow is not None:
        _validate_experiment_definition(bundle.shadow)
        if bundle.shadow.doctrine_mode is not DoctrineMode.SHADOW:
            raise ReplayExperimentsValidationError(
                "bundle shadow must use doctrine_mode=shadow"
            )
        if bundle.shadow.family is not bundle.baseline.family:
            raise ReplayExperimentsValidationError(
                "bundle baseline and shadow families must match"
            )

    for note in bundle.notes:
        if not isinstance(note, str):
            raise ReplayExperimentsValidationError(
                f"bundle note must be string, got {note!r}"
            )


__all__ = [
    "ReplayExperimentsError",
    "ReplayExperimentsValidationError",
    "ReplayExperimentDefinition",
    "ReplayExperimentBundle",
    "ReplayExperimentsManager",
    "validate_experiment_definition",
    "validate_experiment_bundle",
    "experiment_definition_to_dict",
    "experiment_bundle_to_dict",
    "build_baseline_experiment",
    "build_shadow_experiment",
    "build_experiment_bundle",
]
