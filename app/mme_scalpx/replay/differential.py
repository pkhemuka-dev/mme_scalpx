"""
app/mme_scalpx/replay/differential.py

Freeze-grade replay differential comparison layer for the MME-ScalpX Permanent
Replay & Validation Framework.

Differential responsibilities
-----------------------------
This module owns:
- canonical baseline-vs-shadow comparison contracts
- deterministic differential bundle construction
- explicit run/result comparison helpers
- machine-readable differential serialization helpers

This module does not own:
- dataset discovery/loading
- replay execution orchestration
- artifact persistence
- doctrine mutation
- report interpretation
- hidden metric generation

Design rules
------------
- differential comparison must always remain explicit baseline vs shadow
- comparisons must be deterministic and auditable
- no hidden mutation of either side's truth
- comparison rules must be rule-based and machine-readable first
- this layer must consume canonical upstream replay objects
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from .engine import ReplayEngineResult, engine_result_to_dict
from .experiments import ReplayExperimentBundle, experiment_bundle_to_dict
from .integrity import ReplayIntegrityBundle, integrity_bundle_to_dict
from .modes import DoctrineMode


class ReplayDifferentialError(RuntimeError):
    """Base exception for replay differential failures."""


class ReplayDifferentialValidationError(ReplayDifferentialError):
    """Raised when differential inputs are invalid."""


@dataclass(frozen=True, slots=True)
class ReplayDifferentialMetric:
    """
    Canonical one-metric differential comparison record.
    """

    metric_name: str
    baseline_value: Any
    shadow_value: Any
    delta: Any
    changed: bool


@dataclass(frozen=True, slots=True)
class ReplayDifferentialSummary:
    """
    Canonical high-level differential summary.
    """

    baseline_run_id: str
    shadow_run_id: str
    baseline_integrity_verdict: str
    shadow_integrity_verdict: str
    baseline_final_state: str
    shadow_final_state: str
    baseline_stage_count: int
    shadow_stage_count: int
    changed_metric_count: int
    notes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class ReplayDifferentialBundle:
    """
    Canonical aggregate baseline-vs-shadow comparison bundle.
    """

    baseline_run_id: str
    shadow_run_id: str
    experiment_bundle: ReplayExperimentBundle
    summary: ReplayDifferentialSummary
    metrics: tuple[ReplayDifferentialMetric, ...]
    machine_payload: Mapping[str, Any]
    notes: tuple[str, ...] = field(default_factory=tuple)


class ReplayDifferentialComparer:
    """
    Freeze-grade replay differential comparer.
    """

    def build_bundle(
        self,
        *,
        experiment_bundle: ReplayExperimentBundle,
        baseline_engine_result: ReplayEngineResult,
        shadow_engine_result: ReplayEngineResult,
        baseline_integrity_bundle: ReplayIntegrityBundle,
        shadow_integrity_bundle: ReplayIntegrityBundle,
        notes: Sequence[str] = (),
    ) -> ReplayDifferentialBundle:
        _validate_experiment_bundle(experiment_bundle)
        _validate_engine_result(
            baseline_engine_result,
            expected_doctrine_mode=DoctrineMode.LOCKED,
            name="baseline_engine_result",
        )
        _validate_engine_result(
            shadow_engine_result,
            expected_doctrine_mode=None,
            name="shadow_engine_result",
        )
        _validate_integrity_bundle(
            baseline_integrity_bundle,
            expected_run_id=baseline_engine_result.run_id,
            name="baseline_integrity_bundle",
        )
        _validate_integrity_bundle(
            shadow_integrity_bundle,
            expected_run_id=shadow_engine_result.run_id,
            name="shadow_integrity_bundle",
        )

        if not experiment_bundle.has_shadow:
            raise ReplayDifferentialValidationError(
                "differential comparison requires experiment bundle with shadow experiment"
            )

        metrics = _build_metrics(
            baseline_engine_result=baseline_engine_result,
            shadow_engine_result=shadow_engine_result,
            baseline_integrity_bundle=baseline_integrity_bundle,
            shadow_integrity_bundle=shadow_integrity_bundle,
        )

        changed_metric_count = sum(1 for item in metrics if item.changed)

        summary = ReplayDifferentialSummary(
            baseline_run_id=baseline_engine_result.run_id,
            shadow_run_id=shadow_engine_result.run_id,
            baseline_integrity_verdict=baseline_integrity_bundle.verdict.value,
            shadow_integrity_verdict=shadow_integrity_bundle.verdict.value,
            baseline_final_state=baseline_engine_result.final_state.value,
            shadow_final_state=shadow_engine_result.final_state.value,
            baseline_stage_count=baseline_engine_result.stage_count,
            shadow_stage_count=shadow_engine_result.stage_count,
            changed_metric_count=changed_metric_count,
            notes=tuple(notes),
        )

        machine_payload = {
            "experiment_bundle": experiment_bundle_to_dict(experiment_bundle),
            "baseline_engine_result": engine_result_to_dict(baseline_engine_result),
            "shadow_engine_result": engine_result_to_dict(shadow_engine_result),
            "baseline_integrity_bundle": integrity_bundle_to_dict(baseline_integrity_bundle),
            "shadow_integrity_bundle": integrity_bundle_to_dict(shadow_integrity_bundle),
            "summary": differential_summary_to_dict(summary),
            "metrics": [differential_metric_to_dict(item) for item in metrics],
            "notes": list(notes),
        }

        return ReplayDifferentialBundle(
            baseline_run_id=baseline_engine_result.run_id,
            shadow_run_id=shadow_engine_result.run_id,
            experiment_bundle=experiment_bundle,
            summary=summary,
            metrics=metrics,
            machine_payload=machine_payload,
            notes=tuple(notes),
        )


def build_differential_bundle(
    *,
    experiment_bundle: ReplayExperimentBundle,
    baseline_engine_result: ReplayEngineResult,
    shadow_engine_result: ReplayEngineResult,
    baseline_integrity_bundle: ReplayIntegrityBundle,
    shadow_integrity_bundle: ReplayIntegrityBundle,
    notes: Sequence[str] = (),
) -> ReplayDifferentialBundle:
    comparer = ReplayDifferentialComparer()
    return comparer.build_bundle(
        experiment_bundle=experiment_bundle,
        baseline_engine_result=baseline_engine_result,
        shadow_engine_result=shadow_engine_result,
        baseline_integrity_bundle=baseline_integrity_bundle,
        shadow_integrity_bundle=shadow_integrity_bundle,
        notes=notes,
    )


def differential_metric_to_dict(metric: ReplayDifferentialMetric) -> dict[str, Any]:
    return {
        "metric_name": metric.metric_name,
        "baseline_value": _json_safe_value(metric.baseline_value),
        "shadow_value": _json_safe_value(metric.shadow_value),
        "delta": _json_safe_value(metric.delta),
        "changed": metric.changed,
    }


def differential_summary_to_dict(
    summary: ReplayDifferentialSummary,
) -> dict[str, Any]:
    return {
        "baseline_run_id": summary.baseline_run_id,
        "shadow_run_id": summary.shadow_run_id,
        "baseline_integrity_verdict": summary.baseline_integrity_verdict,
        "shadow_integrity_verdict": summary.shadow_integrity_verdict,
        "baseline_final_state": summary.baseline_final_state,
        "shadow_final_state": summary.shadow_final_state,
        "baseline_stage_count": summary.baseline_stage_count,
        "shadow_stage_count": summary.shadow_stage_count,
        "changed_metric_count": summary.changed_metric_count,
        "notes": list(summary.notes),
    }


def differential_bundle_to_dict(
    bundle: ReplayDifferentialBundle,
) -> dict[str, Any]:
    return {
        "baseline_run_id": bundle.baseline_run_id,
        "shadow_run_id": bundle.shadow_run_id,
        "experiment_bundle": experiment_bundle_to_dict(bundle.experiment_bundle),
        "summary": differential_summary_to_dict(bundle.summary),
        "metrics": [differential_metric_to_dict(item) for item in bundle.metrics],
        "machine_payload": dict(bundle.machine_payload),
        "notes": list(bundle.notes),
    }


def _build_metrics(
    *,
    baseline_engine_result: ReplayEngineResult,
    shadow_engine_result: ReplayEngineResult,
    baseline_integrity_bundle: ReplayIntegrityBundle,
    shadow_integrity_bundle: ReplayIntegrityBundle,
) -> tuple[ReplayDifferentialMetric, ...]:
    metrics = (
        _compare_metric(
            metric_name="final_state",
            baseline_value=baseline_engine_result.final_state.value,
            shadow_value=shadow_engine_result.final_state.value,
        ),
        _compare_metric(
            metric_name="stage_count",
            baseline_value=baseline_engine_result.stage_count,
            shadow_value=shadow_engine_result.stage_count,
        ),
        _compare_metric(
            metric_name="integrity_verdict",
            baseline_value=baseline_integrity_bundle.verdict.value,
            shadow_value=shadow_integrity_bundle.verdict.value,
        ),
        _compare_metric(
            metric_name="integrity_passed_checks",
            baseline_value=baseline_integrity_bundle.passed_checks,
            shadow_value=shadow_integrity_bundle.passed_checks,
        ),
        _compare_metric(
            metric_name="integrity_warned_checks",
            baseline_value=baseline_integrity_bundle.warned_checks,
            shadow_value=shadow_integrity_bundle.warned_checks,
        ),
        _compare_metric(
            metric_name="integrity_failed_checks",
            baseline_value=baseline_integrity_bundle.failed_checks,
            shadow_value=shadow_integrity_bundle.failed_checks,
        ),
    )
    return metrics


def _compare_metric(
    *,
    metric_name: str,
    baseline_value: Any,
    shadow_value: Any,
) -> ReplayDifferentialMetric:
    changed = baseline_value != shadow_value
    delta = _compute_delta(baseline_value, shadow_value)
    return ReplayDifferentialMetric(
        metric_name=metric_name,
        baseline_value=baseline_value,
        shadow_value=shadow_value,
        delta=delta,
        changed=changed,
    )


def _compute_delta(baseline_value: Any, shadow_value: Any) -> Any:
    if isinstance(baseline_value, (int, float)) and isinstance(shadow_value, (int, float)):
        return shadow_value - baseline_value
    return None if baseline_value == shadow_value else {
        "baseline": _json_safe_value(baseline_value),
        "shadow": _json_safe_value(shadow_value),
    }


def _validate_experiment_bundle(bundle: ReplayExperimentBundle) -> None:
    if not bundle.has_shadow:
        raise ReplayDifferentialValidationError(
            "experiment bundle must contain baseline and shadow for differential comparison"
        )

    if bundle.baseline.doctrine_mode is not DoctrineMode.LOCKED:
        raise ReplayDifferentialValidationError(
            "experiment bundle baseline must use doctrine_mode=locked"
        )

    assert bundle.shadow is not None
    if bundle.shadow.doctrine_mode is not DoctrineMode.SHADOW:
        raise ReplayDifferentialValidationError(
            "experiment bundle shadow must use doctrine_mode=shadow"
        )


def _validate_engine_result(
    result: ReplayEngineResult,
    *,
    expected_doctrine_mode: DoctrineMode | None,
    name: str,
) -> None:
    if not result.run_id or not result.run_id.strip():
        raise ReplayDifferentialValidationError(f"{name}.run_id must be non-empty")
    _ = expected_doctrine_mode


def _validate_integrity_bundle(
    bundle: ReplayIntegrityBundle,
    *,
    expected_run_id: str,
    name: str,
) -> None:
    if bundle.run_id != expected_run_id:
        raise ReplayDifferentialValidationError(
            f"{name}.run_id mismatch: expected {expected_run_id!r}, got {bundle.run_id!r}"
        )


def _json_safe_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _json_safe_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe_value(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe_value(item) for item in value]
    return value


__all__ = [
    "ReplayDifferentialError",
    "ReplayDifferentialValidationError",
    "ReplayDifferentialMetric",
    "ReplayDifferentialSummary",
    "ReplayDifferentialBundle",
    "ReplayDifferentialComparer",
    "build_differential_bundle",
    "differential_metric_to_dict",
    "differential_summary_to_dict",
    "differential_bundle_to_dict",
]
