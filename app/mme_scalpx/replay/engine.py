"""
app/mme_scalpx/replay/engine.py

Freeze-grade replay engine layer for the MME-ScalpX Permanent Replay &
Validation Framework.

Engine responsibilities
-----------------------
This module owns:
- replay lifecycle state transitions
- deterministic stage-by-stage orchestration skeleton
- canonical engine context/result contracts
- replay execution envelope for a run context + topology plan
- hook-based integration surface for later clock/injector/artifacts/integrity layers

This module does not own:
- dataset discovery/loading
- replay selection policy
- run-id or artifact path planning
- topology truth definition
- replay clock implementation
- payload injection implementation
- metric/report computation
- doctrine logic
- live runtime mutation

Design rules
------------
- engine state transitions must be explicit and auditable
- engine must not redefine contracts owned elsewhere
- engine must be deterministic given identical inputs and identical hook behavior
- engine must not silently swallow stage failures
- engine must remain reusable by locked, shadow, and differential replay equally
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Protocol, Sequence

from .modes import ReplayRunState
from .runner import ReplayRunContext
from .topology import ReplayStageDefinition, ReplayTopologyPlan, topology_plan_to_dict


class ReplayEngineError(RuntimeError):
    """Base exception for replay engine failures."""


class ReplayEngineValidationError(ReplayEngineError):
    """Raised when engine inputs or state transitions are invalid."""


class ReplayEngineStageError(ReplayEngineError):
    """Raised when a stage execution fails."""


class ReplayEngineHook(Protocol):
    def __call__(self, context: "ReplayEngineContext") -> None:
        ...


class ReplayStageExecutor(Protocol):
    def __call__(
        self,
        context: "ReplayEngineContext",
        stage: ReplayStageDefinition,
    ) -> Mapping[str, Any] | None:
        ...


@dataclass(frozen=True, slots=True)
class ReplayStageExecutionRecord:
    """
    Canonical record of one stage execution.
    """

    stage_name: str
    order_index: int
    started_at: str
    finished_at: str
    terminal_stage: bool
    success: bool
    output_summary: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ReplayEngineResult:
    """
    Canonical engine execution result.
    """

    run_id: str
    engine_started_at: str
    engine_finished_at: str
    final_state: ReplayRunState
    stage_records: tuple[ReplayStageExecutionRecord, ...]
    topology_summary: Mapping[str, Any]
    notes: tuple[str, ...] = field(default_factory=tuple)

    @property
    def stage_count(self) -> int:
        return len(self.stage_records)


@dataclass(slots=True)
class ReplayEngineContext:
    """
    Mutable runtime orchestration context for a single engine run.
    """

    run_context: ReplayRunContext
    topology_plan: ReplayTopologyPlan
    current_state: ReplayRunState = ReplayRunState.CREATED
    current_stage_name: str | None = None
    stage_records: list[ReplayStageExecutionRecord] = field(default_factory=list)
    engine_notes: list[str] = field(default_factory=list)

    @property
    def run_id(self) -> str:
        return self.run_context.run_id

    @property
    def doctrine_mode(self):
        return self.run_context.doctrine_mode


class ReplayEngine:
    """
    Freeze-grade replay engine.
    """

    def __init__(
        self,
        *,
        before_run_hooks: Sequence[ReplayEngineHook] = (),
        after_run_hooks: Sequence[ReplayEngineHook] = (),
        before_stage_hooks: Sequence[ReplayEngineHook] = (),
        after_stage_hooks: Sequence[ReplayEngineHook] = (),
    ) -> None:
        self._before_run_hooks = tuple(before_run_hooks)
        self._after_run_hooks = tuple(after_run_hooks)
        self._before_stage_hooks = tuple(before_stage_hooks)
        self._after_stage_hooks = tuple(after_stage_hooks)

    def build_context(
        self,
        run_context: ReplayRunContext,
        topology_plan: ReplayTopologyPlan,
    ) -> ReplayEngineContext:
        _validate_run_context(run_context)
        _validate_topology_plan(topology_plan)
        return ReplayEngineContext(
            run_context=run_context,
            topology_plan=topology_plan,
            current_state=ReplayRunState.CREATED,
        )

    def execute(
        self,
        run_context: ReplayRunContext,
        topology_plan: ReplayTopologyPlan,
        *,
        stage_executor: ReplayStageExecutor,
    ) -> ReplayEngineResult:
        if stage_executor is None:
            raise ReplayEngineValidationError("stage_executor must be provided")

        context = self.build_context(run_context, topology_plan)
        engine_started_at = _utc_now_iso()

        try:
            self._transition(context, ReplayRunState.RESETTING)
            self._run_hooks(self._before_run_hooks, context)

            self._transition(context, ReplayRunState.READY)
            self._transition(context, ReplayRunState.RUNNING)

            for stage in topology_plan.stages:
                self._execute_stage(context, stage, stage_executor)

            self._transition(context, ReplayRunState.FINALIZING)
            self._run_hooks(self._after_run_hooks, context)
            self._transition(context, ReplayRunState.COMPLETED)

        except Exception as exc:
            context.engine_notes.append(f"engine_failure:{type(exc).__name__}")
            context.current_state = ReplayRunState.FAILED
            engine_finished_at = _utc_now_iso()

            if isinstance(exc, ReplayEngineError):
                raise
            raise ReplayEngineStageError(
                f"replay engine failed for run_id={context.run_id}: {exc}"
            ) from exc

        engine_finished_at = _utc_now_iso()
        return ReplayEngineResult(
            run_id=context.run_id,
            engine_started_at=engine_started_at,
            engine_finished_at=engine_finished_at,
            final_state=context.current_state,
            stage_records=tuple(context.stage_records),
            topology_summary=topology_plan_to_dict(topology_plan),
            notes=tuple(context.engine_notes),
        )

    def _execute_stage(
        self,
        context: ReplayEngineContext,
        stage: ReplayStageDefinition,
        stage_executor: ReplayStageExecutor,
    ) -> None:
        context.current_stage_name = stage.stage_name
        self._run_hooks(self._before_stage_hooks, context)

        started_at = _utc_now_iso()

        try:
            raw_output = stage_executor(context, stage)
            output_summary = dict(raw_output or {})
            success = True
        except Exception as exc:
            finished_at = _utc_now_iso()
            context.stage_records.append(
                ReplayStageExecutionRecord(
                    stage_name=stage.stage_name,
                    order_index=stage.order_index,
                    started_at=started_at,
                    finished_at=finished_at,
                    terminal_stage=stage.terminal_stage,
                    success=False,
                    output_summary={"error_type": type(exc).__name__},
                )
            )
            raise ReplayEngineStageError(
                f"stage execution failed at {stage.stage_name!r}: {exc}"
            ) from exc

        finished_at = _utc_now_iso()
        context.stage_records.append(
            ReplayStageExecutionRecord(
                stage_name=stage.stage_name,
                order_index=stage.order_index,
                started_at=started_at,
                finished_at=finished_at,
                terminal_stage=stage.terminal_stage,
                success=success,
                output_summary=output_summary,
            )
        )

        self._run_hooks(self._after_stage_hooks, context)
        context.current_stage_name = None

    def _run_hooks(
        self,
        hooks: Sequence[ReplayEngineHook],
        context: ReplayEngineContext,
    ) -> None:
        for hook in hooks:
            hook(context)

    def _transition(
        self,
        context: ReplayEngineContext,
        new_state: ReplayRunState,
    ) -> None:
        current = context.current_state
        if not _is_valid_transition(current, new_state):
            raise ReplayEngineValidationError(
                f"invalid engine state transition: {current.value} -> {new_state.value}"
            )
        context.current_state = new_state


def execute_replay_engine(
    run_context: ReplayRunContext,
    topology_plan: ReplayTopologyPlan,
    *,
    stage_executor: ReplayStageExecutor,
    before_run_hooks: Sequence[ReplayEngineHook] = (),
    after_run_hooks: Sequence[ReplayEngineHook] = (),
    before_stage_hooks: Sequence[ReplayEngineHook] = (),
    after_stage_hooks: Sequence[ReplayEngineHook] = (),
) -> ReplayEngineResult:
    engine = ReplayEngine(
        before_run_hooks=before_run_hooks,
        after_run_hooks=after_run_hooks,
        before_stage_hooks=before_stage_hooks,
        after_stage_hooks=after_stage_hooks,
    )
    return engine.execute(
        run_context=run_context,
        topology_plan=topology_plan,
        stage_executor=stage_executor,
    )


def engine_result_to_dict(result: ReplayEngineResult) -> dict[str, Any]:
    return {
        "run_id": result.run_id,
        "engine_started_at": result.engine_started_at,
        "engine_finished_at": result.engine_finished_at,
        "final_state": result.final_state.value,
        "stage_records": [stage_execution_record_to_dict(item) for item in result.stage_records],
        "topology_summary": dict(result.topology_summary),
        "notes": list(result.notes),
        "stage_count": result.stage_count,
    }


def stage_execution_record_to_dict(
    record: ReplayStageExecutionRecord,
) -> dict[str, Any]:
    return {
        "stage_name": record.stage_name,
        "order_index": record.order_index,
        "started_at": record.started_at,
        "finished_at": record.finished_at,
        "terminal_stage": record.terminal_stage,
        "success": record.success,
        "output_summary": dict(record.output_summary),
    }


def _validate_run_context(run_context: ReplayRunContext) -> None:
    if not run_context.run_id or not run_context.run_id.strip():
        raise ReplayEngineValidationError("run_context.run_id must be non-empty")


def _validate_topology_plan(plan: ReplayTopologyPlan) -> None:
    if not plan.stages:
        raise ReplayEngineValidationError("topology_plan must contain at least one stage")

    stage_names = tuple(stage.stage_name for stage in plan.stages)
    if stage_names != plan.stage_names:
        raise ReplayEngineValidationError(
            "topology_plan stage_names must match ordered stage definitions"
        )


def _is_valid_transition(
    current: ReplayRunState,
    new_state: ReplayRunState,
) -> bool:
    allowed: Mapping[ReplayRunState, tuple[ReplayRunState, ...]] = {
        ReplayRunState.CREATED: (
            ReplayRunState.RESETTING,
            ReplayRunState.ABORTED,
        ),
        ReplayRunState.RESETTING: (
            ReplayRunState.READY,
            ReplayRunState.FAILED,
            ReplayRunState.ABORTED,
        ),
        ReplayRunState.READY: (
            ReplayRunState.RUNNING,
            ReplayRunState.ABORTED,
        ),
        ReplayRunState.RUNNING: (
            ReplayRunState.PAUSED,
            ReplayRunState.FINALIZING,
            ReplayRunState.FAILED,
            ReplayRunState.ABORTED,
        ),
        ReplayRunState.PAUSED: (
            ReplayRunState.RUNNING,
            ReplayRunState.ABORTED,
        ),
        ReplayRunState.FINALIZING: (
            ReplayRunState.COMPLETED,
            ReplayRunState.FAILED,
        ),
        ReplayRunState.COMPLETED: (),
        ReplayRunState.FAILED: (),
        ReplayRunState.ABORTED: (),
    }
    return new_state in allowed[current]


def _utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


__all__ = [
    "ReplayEngineError",
    "ReplayEngineValidationError",
    "ReplayEngineStageError",
    "ReplayEngineHook",
    "ReplayStageExecutor",
    "ReplayStageExecutionRecord",
    "ReplayEngineResult",
    "ReplayEngineContext",
    "ReplayEngine",
    "execute_replay_engine",
    "engine_result_to_dict",
    "stage_execution_record_to_dict",
]
