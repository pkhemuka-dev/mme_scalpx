"""
app/mme_scalpx/replay/reports.py

Freeze-grade replay report assembly layer for the MME-ScalpX Permanent Replay &
Validation Framework.

Report responsibilities
-----------------------
This module owns:
- canonical replay report dataclasses
- report bundle assembly from frozen replay layer outputs
- integrity report shaping
- scope/selection/topology/engine summary shaping
- machine-readable report serialization helpers

This module does not own:
- dataset discovery/loading
- replay execution orchestration
- artifact writing
- doctrine logic
- raw integrity check implementation
- hidden metric computation beyond explicit provided inputs

Design rules
------------
- report assembly must be deterministic and auditable
- report shaping must consume canonical upstream objects
- report layer must not invent missing truths
- report layer must remain machine-readable first
- no hidden persistence side effects
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from .engine import ReplayEngineResult, engine_result_to_dict
from .integrity import ReplayIntegrityBundle, integrity_bundle_to_dict
from .runner import ReplayRunContext
from .selectors import ReplaySelectionPlan, selection_plan_to_dict
from .topology import ReplayTopologyPlan, topology_plan_to_dict


class ReplayReportsError(RuntimeError):
    """Base exception for replay report failures."""


class ReplayReportsValidationError(ReplayReportsError):
    """Raised when replay report inputs are invalid."""


@dataclass(frozen=True, slots=True)
class ReplayCoreReport:
    """
    Canonical core replay report.
    """

    run_id: str
    doctrine_mode: str
    selection_mode: str
    topology_scope: str
    integrity_verdict: str
    final_engine_state: str
    trading_dates: tuple[str, ...]
    stage_names: tuple[str, ...]
    notes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class ReplayIntegrityReport:
    """
    Canonical shaped integrity report.
    """

    run_id: str
    verdict: str
    check_count: int
    passed_checks: int
    warned_checks: int
    failed_checks: int
    waivers: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class ReplayScopeReport:
    """
    Canonical scope/selection/topology report.
    """

    run_id: str
    selection_mode: str
    topology_scope: str
    trading_dates: tuple[str, ...]
    stage_names: tuple[str, ...]
    session_segment: str | None
    intraday_window_start: str | None
    intraday_window_end: str | None
    market_tags: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class ReplayReportBundle:
    """
    Canonical aggregate replay report bundle.
    """

    run_id: str
    core_report: ReplayCoreReport
    integrity_report: ReplayIntegrityReport
    scope_report: ReplayScopeReport
    machine_payload: Mapping[str, Any]
    notes: tuple[str, ...] = field(default_factory=tuple)


class ReplayReportsBuilder:
    """
    Freeze-grade replay reports builder.
    """

    def build_bundle(
        self,
        *,
        run_context: ReplayRunContext,
        selection_plan: ReplaySelectionPlan,
        topology_plan: ReplayTopologyPlan,
        engine_result: ReplayEngineResult,
        integrity_bundle: ReplayIntegrityBundle,
        notes: Sequence[str] = (),
    ) -> ReplayReportBundle:
        _validate_run_context(run_context)
        _validate_selection_plan(selection_plan)
        _validate_topology_plan(topology_plan)
        _validate_engine_result(engine_result, expected_run_id=run_context.run_id)
        _validate_integrity_bundle(integrity_bundle, expected_run_id=run_context.run_id)

        core_report = ReplayCoreReport(
            run_id=run_context.run_id,
            doctrine_mode=run_context.doctrine_mode.value,
            selection_mode=selection_plan.selection_mode.value,
            topology_scope=topology_plan.scope.value,
            integrity_verdict=integrity_bundle.verdict.value,
            final_engine_state=engine_result.final_state.value,
            trading_dates=selection_plan.trading_dates,
            stage_names=topology_plan.stage_names,
            notes=tuple(notes),
        )

        integrity_report = ReplayIntegrityReport(
            run_id=integrity_bundle.run_id,
            verdict=integrity_bundle.verdict.value,
            check_count=integrity_bundle.check_count,
            passed_checks=integrity_bundle.passed_checks,
            warned_checks=integrity_bundle.warned_checks,
            failed_checks=integrity_bundle.failed_checks,
            waivers=integrity_bundle.waivers,
            notes=integrity_bundle.notes,
        )

        scope_report = ReplayScopeReport(
            run_id=run_context.run_id,
            selection_mode=selection_plan.selection_mode.value,
            topology_scope=topology_plan.scope.value,
            trading_dates=selection_plan.trading_dates,
            stage_names=topology_plan.stage_names,
            session_segment=selection_plan.session_segment,
            intraday_window_start=selection_plan.intraday_window.start,
            intraday_window_end=selection_plan.intraday_window.end,
            market_tags=selection_plan.market_tags,
        )

        machine_payload = {
            "run_context": {
                "run_id": run_context.run_id,
                "doctrine_mode": run_context.doctrine_mode.value,
            },
            "selection_plan": selection_plan_to_dict(selection_plan),
            "topology_plan": topology_plan_to_dict(topology_plan),
            "engine_result": engine_result_to_dict(engine_result),
            "integrity_bundle": integrity_bundle_to_dict(integrity_bundle),
            "core_report": core_report_to_dict(core_report),
            "integrity_report": integrity_report_to_dict(integrity_report),
            "scope_report": scope_report_to_dict(scope_report),
            "notes": list(notes),
        }

        return ReplayReportBundle(
            run_id=run_context.run_id,
            core_report=core_report,
            integrity_report=integrity_report,
            scope_report=scope_report,
            machine_payload=machine_payload,
            notes=tuple(notes),
        )


def build_report_bundle(
    *,
    run_context: ReplayRunContext,
    selection_plan: ReplaySelectionPlan,
    topology_plan: ReplayTopologyPlan,
    engine_result: ReplayEngineResult,
    integrity_bundle: ReplayIntegrityBundle,
    notes: Sequence[str] = (),
) -> ReplayReportBundle:
    builder = ReplayReportsBuilder()
    return builder.build_bundle(
        run_context=run_context,
        selection_plan=selection_plan,
        topology_plan=topology_plan,
        engine_result=engine_result,
        integrity_bundle=integrity_bundle,
        notes=notes,
    )


def core_report_to_dict(report: ReplayCoreReport) -> dict[str, Any]:
    return {
        "run_id": report.run_id,
        "doctrine_mode": report.doctrine_mode,
        "selection_mode": report.selection_mode,
        "topology_scope": report.topology_scope,
        "integrity_verdict": report.integrity_verdict,
        "final_engine_state": report.final_engine_state,
        "trading_dates": list(report.trading_dates),
        "stage_names": list(report.stage_names),
        "notes": list(report.notes),
    }


def integrity_report_to_dict(report: ReplayIntegrityReport) -> dict[str, Any]:
    return {
        "run_id": report.run_id,
        "verdict": report.verdict,
        "check_count": report.check_count,
        "passed_checks": report.passed_checks,
        "warned_checks": report.warned_checks,
        "failed_checks": report.failed_checks,
        "waivers": list(report.waivers),
        "notes": list(report.notes),
    }


def scope_report_to_dict(report: ReplayScopeReport) -> dict[str, Any]:
    return {
        "run_id": report.run_id,
        "selection_mode": report.selection_mode,
        "topology_scope": report.topology_scope,
        "trading_dates": list(report.trading_dates),
        "stage_names": list(report.stage_names),
        "session_segment": report.session_segment,
        "intraday_window_start": report.intraday_window_start,
        "intraday_window_end": report.intraday_window_end,
        "market_tags": list(report.market_tags),
    }


def report_bundle_to_dict(bundle: ReplayReportBundle) -> dict[str, Any]:
    return {
        "run_id": bundle.run_id,
        "core_report": core_report_to_dict(bundle.core_report),
        "integrity_report": integrity_report_to_dict(bundle.integrity_report),
        "scope_report": scope_report_to_dict(bundle.scope_report),
        "machine_payload": dict(bundle.machine_payload),
        "notes": list(bundle.notes),
    }


def _validate_run_context(run_context: ReplayRunContext) -> None:
    if not run_context.run_id or not run_context.run_id.strip():
        raise ReplayReportsValidationError("run_context.run_id must be non-empty")


def _validate_selection_plan(selection_plan: ReplaySelectionPlan) -> None:
    if not selection_plan.trading_dates:
        raise ReplayReportsValidationError(
            "selection_plan.trading_dates must be non-empty"
        )


def _validate_topology_plan(topology_plan: ReplayTopologyPlan) -> None:
    if not topology_plan.stage_names:
        raise ReplayReportsValidationError(
            "topology_plan.stage_names must be non-empty"
        )


def _validate_engine_result(
    engine_result: ReplayEngineResult,
    *,
    expected_run_id: str,
) -> None:
    if engine_result.run_id != expected_run_id:
        raise ReplayReportsValidationError(
            f"engine_result.run_id mismatch: expected {expected_run_id!r}, "
            f"got {engine_result.run_id!r}"
        )


def _validate_integrity_bundle(
    integrity_bundle: ReplayIntegrityBundle,
    *,
    expected_run_id: str,
) -> None:
    if integrity_bundle.run_id != expected_run_id:
        raise ReplayReportsValidationError(
            f"integrity_bundle.run_id mismatch: expected {expected_run_id!r}, "
            f"got {integrity_bundle.run_id!r}"
        )


__all__ = [
    "ReplayReportsError",
    "ReplayReportsValidationError",
    "ReplayCoreReport",
    "ReplayIntegrityReport",
    "ReplayScopeReport",
    "ReplayReportBundle",
    "ReplayReportsBuilder",
    "build_report_bundle",
    "core_report_to_dict",
    "integrity_report_to_dict",
    "scope_report_to_dict",
    "report_bundle_to_dict",
]
