"""
app/mme_scalpx/replay/runner.py

Freeze-grade replay run assembly layer for the MME-ScalpX Permanent Replay &
Validation Framework.

Runner responsibilities
-----------------------
This module owns:
- replay run-id generation / validation
- replay run directory planning
- canonical artifact path planning
- selection-plan attachment
- manifest skeleton assembly
- doctrine-mode-aware manifest shaping
- top-level replay run context construction

This module does not own:
- replay clock driving
- dataset discovery internals
- selection policy internals
- replay injection
- topology execution
- experiment business logic
- metric/report computation
- live runtime mutation

Design rules
------------
- runner must be deterministic and auditable
- runner must not mutate dataset or selection truth
- manifest assembly must strictly respect contracts.py
- locked / shadow / differential separation must remain explicit
- artifact paths must be stable and reconstructible
- no doctrine logic belongs here
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence
from uuid import uuid4

from .contracts import (
    ARTIFACT_BLOCKER_BREAKDOWN,
    ARTIFACT_CANDIDATE_AUDIT,
    ARTIFACT_DATASET_SUMMARY,
    ARTIFACT_DIFFERENTIAL_REPORT,
    ARTIFACT_EFFECTIVE_INPUTS_JSON,
    ARTIFACT_EFFECTIVE_OVERRIDES_FLAT_JSON,
    ARTIFACT_EXIT_BREAKDOWN,
    ARTIFACT_INTEGRITY_REPORT,
    ARTIFACT_MANIFEST,
    ARTIFACT_METRICS_SUMMARY,
    ARTIFACT_SCOPE_PROFILE,
    ARTIFACT_TRADE_LOG,
    ARTIFACTS_SUBDIR,
    LOGS_SUBDIR,
    REPLAY_CHAPTER_NAME,
    REPLAY_RUNS_DIRNAME,
    ArtifactsSection,
    DatasetSection,
    EffectiveInputsSnapshot,
    ExperimentSection,
    IntegritySection,
    ProfilesSection,
    ReplayRunManifest,
    ReplaySection,
    ResetSection,
    SelectionSection,
    SelectionWindow,
    effective_inputs_to_dict,
    row_to_dict,
    validate_manifest,
)
from .modes import (
    DoctrineMode,
    ExperimentFamily,
    IntegrityVerdict,
    ReplayScope,
    ReplaySelectionMode,
    ReplaySideMode,
    ReplaySpeedMode,
    ReplayVerdictTag,
)
from .selectors import ReplaySelectionPlan, selection_plan_to_dict


class ReplayRunnerError(RuntimeError):
    """Base exception for replay runner failures."""


class ReplayRunnerValidationError(ReplayRunnerError):
    """Raised when run assembly inputs are invalid."""


@dataclass(frozen=True, slots=True)
class ReplayRunConfig:
    """
    Immutable run-assembly input.
    """

    doctrine_mode: DoctrineMode
    replay_scope: ReplayScope = ReplayScope.FEEDS_ONLY
    speed_mode: ReplaySpeedMode = ReplaySpeedMode.ACCELERATED
    side_mode: ReplaySideMode = ReplaySideMode.MIRRORED_BOTH
    run_label: str | None = None
    code_revision: str | None = None
    dataset_id: str | None = None
    profiles: ProfilesSection = field(default_factory=ProfilesSection)
    experiment_family: ExperimentFamily | None = None
    baseline_ref: str | None = None
    override_pack_id: str | None = None
    shadow_label: str | None = None
    differential_pair_id: str | None = None
    reset_policy: str = "full_reset"
    integrity_required_checks: tuple[str, ...] = field(default_factory=tuple)
    integrity_verdict: IntegrityVerdict | None = None
    integrity_waivers: tuple[str, ...] = field(default_factory=tuple)
    fill_model: str | None = None
    run_root: str | Path | None = None
    created_at: str | None = None
    notes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class ReplayArtifactPlan:
    """
    Stable artifact path plan for a run.
    """

    root_dir: str
    manifest_path: str
    log_dir: str
    artifacts_dir: str
    dataset_summary_path: str
    scope_profile_path: str
    integrity_report_path: str
    metrics_summary_path: str
    trade_log_path: str
    candidate_audit_path: str
    blocker_breakdown_path: str
    exit_breakdown_path: str
    differential_report_path: str
    effective_inputs_path: str
    effective_overrides_flat_path: str

    def report_paths_minimum(self) -> tuple[str, ...]:
        return (
            self.dataset_summary_path,
            self.scope_profile_path,
            self.integrity_report_path,
            self.metrics_summary_path,
            self.effective_inputs_path,
            self.effective_overrides_flat_path,
        )


@dataclass(frozen=True, slots=True)
class ReplayRunContext:
    """
    Canonical run-assembly output for downstream replay layers.
    """

    run_id: str
    created_at: str
    doctrine_mode: DoctrineMode
    selection_plan: ReplaySelectionPlan
    run_config: ReplayRunConfig
    artifact_plan: ReplayArtifactPlan
    manifest: ReplayRunManifest

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "created_at": self.created_at,
            "doctrine_mode": self.doctrine_mode.value,
            "selection_plan": selection_plan_to_dict(self.selection_plan),
            "artifact_plan": artifact_plan_to_dict(self.artifact_plan),
            "manifest_validated": True,
        }


class ReplayRunner:
    """
    Freeze-grade replay run assembler.
    """

    def __init__(self, *, run_root: str | Path | None = None) -> None:
        self._run_root = Path(run_root or REPLAY_RUNS_DIRNAME).expanduser()

    @property
    def run_root(self) -> Path:
        return self._run_root

    def build_run_context(
        self,
        selection_plan: ReplaySelectionPlan,
        run_config: ReplayRunConfig,
    ) -> ReplayRunContext:
        _validate_run_config(run_config)

        created_at = run_config.created_at or _utc_now_iso()
        run_id = generate_run_id(
            doctrine_mode=run_config.doctrine_mode,
            selection_mode=selection_plan.selection_mode,
            run_label=run_config.run_label,
            created_at=created_at,
        )

        artifact_plan = plan_artifacts(
            run_id=run_id,
            run_root=run_config.run_root or self._run_root,
        )

        manifest = self._build_manifest(
            run_id=run_id,
            created_at=created_at,
            selection_plan=selection_plan,
            run_config=run_config,
            artifact_plan=artifact_plan,
        )

        validate_manifest(manifest)

        return ReplayRunContext(
            run_id=run_id,
            created_at=created_at,
            doctrine_mode=run_config.doctrine_mode,
            selection_plan=selection_plan,
            run_config=run_config,
            artifact_plan=artifact_plan,
            manifest=manifest,
        )

    def ensure_run_directories(self, context: ReplayRunContext) -> None:
        Path(context.artifact_plan.root_dir).mkdir(parents=True, exist_ok=True)
        Path(context.artifact_plan.log_dir).mkdir(parents=True, exist_ok=True)
        Path(context.artifact_plan.artifacts_dir).mkdir(parents=True, exist_ok=True)

    def _build_manifest(
        self,
        *,
        run_id: str,
        created_at: str,
        selection_plan: ReplaySelectionPlan,
        run_config: ReplayRunConfig,
        artifact_plan: ReplayArtifactPlan,
    ) -> ReplayRunManifest:
        dataset_section = DatasetSection(
            dataset_id=run_config.dataset_id or selection_plan.dataset_summary.dataset_id,
            dataset_fingerprint=selection_plan.dataset_summary.dataset_fingerprint,
            source_path=selection_plan.dataset_summary.dataset_root,
            coverage_summary={
                "trading_days": list(selection_plan.dataset_summary.trading_days),
                "total_days": selection_plan.dataset_summary.total_days,
                "valid_days": selection_plan.dataset_summary.valid_days,
                "invalid_days": selection_plan.dataset_summary.invalid_days,
                "total_files": selection_plan.dataset_summary.total_files,
                "total_size_bytes": selection_plan.dataset_summary.total_size_bytes,
            },
        )

        selection_section = SelectionSection(
            selection_mode=selection_plan.selection_mode,
            trading_dates=selection_plan.trading_dates,
            window=SelectionWindow(
                start=selection_plan.intraday_window.start,
                end=selection_plan.intraday_window.end,
            ),
            session_segment=selection_plan.session_segment,
            market_tags=tuple(selection_plan.market_tags),
        )

        replay_section = ReplaySection(
            scope=run_config.replay_scope,
            speed_mode=run_config.speed_mode,
            doctrine_mode=run_config.doctrine_mode,
            side_mode=run_config.side_mode,
            fill_model=run_config.fill_model,
        )

        experiment_section = ExperimentSection(
            family=run_config.experiment_family,
            baseline_ref=run_config.baseline_ref,
            override_pack_id=run_config.override_pack_id,
            shadow_label=run_config.shadow_label,
            differential_pair_id=run_config.differential_pair_id,
        )

        reset_section = ResetSection(
            policy=run_config.reset_policy,
            reset_started_at=None,
            reset_completed_at=None,
            reset_verdict=None,
        )

        integrity_section = IntegritySection(
            required_checks=tuple(run_config.integrity_required_checks),
            verdict=run_config.integrity_verdict,
            waivers=tuple(run_config.integrity_waivers),
        )

        artifacts_section = ArtifactsSection(
            root_dir=artifact_plan.root_dir,
            manifest_path=artifact_plan.manifest_path,
            log_dir=artifact_plan.log_dir,
            report_paths=_report_paths_for_mode(
                doctrine_mode=run_config.doctrine_mode,
                artifact_plan=artifact_plan,
            ),
        )

        verdict_tags = _verdict_tags_for_mode(
            doctrine_mode=run_config.doctrine_mode,
            integrity_verdict=run_config.integrity_verdict,
        )

        notes = tuple(run_config.notes) + tuple(selection_plan.selection_notes)

        return ReplayRunManifest(
            run_id=run_id,
            chapter=REPLAY_CHAPTER_NAME,
            created_at=created_at,
            code_revision=run_config.code_revision,
            dataset=dataset_section,
            selection=selection_section,
            replay=replay_section,
            profiles=run_config.profiles,
            experiment=experiment_section,
            reset=reset_section,
            integrity=integrity_section,
            artifacts=artifacts_section,
            verdict_tags=verdict_tags,
            notes=notes,
        )


def generate_run_id(
    *,
    doctrine_mode: DoctrineMode,
    selection_mode: ReplaySelectionMode,
    run_label: str | None,
    created_at: str,
) -> str:
    timestamp_part = _run_timestamp(created_at)
    doctrine_part = _slug(doctrine_mode.value)
    selection_part = _slug(selection_mode.value)
    label_part = _slug(run_label) if run_label else None
    suffix = uuid4().hex[:8]

    pieces = ["replay", doctrine_part, selection_part]
    if label_part:
        pieces.append(label_part)
    pieces.extend([timestamp_part, suffix])
    run_id = "_".join(piece for piece in pieces if piece)
    validate_run_id_string(run_id)
    return run_id


def validate_run_id_string(run_id: str) -> None:
    if not run_id or not run_id.strip():
        raise ReplayRunnerValidationError("run_id must be non-empty")
    if any(ch.isspace() for ch in run_id):
        raise ReplayRunnerValidationError("run_id must not contain whitespace")
    if "/" in run_id or "\\" in run_id:
        raise ReplayRunnerValidationError("run_id must not contain path separators")


def plan_artifacts(
    *,
    run_id: str,
    run_root: str | Path,
) -> ReplayArtifactPlan:
    validate_run_id_string(run_id)

    base = Path(run_root).expanduser() / run_id
    base_str = str(base)
    return ReplayArtifactPlan(
        root_dir=base_str,
        manifest_path=str(base / ARTIFACT_MANIFEST),
        log_dir=str(base / LOGS_SUBDIR),
        artifacts_dir=str(base / ARTIFACTS_SUBDIR),
        dataset_summary_path=str(base / ARTIFACT_DATASET_SUMMARY),
        scope_profile_path=str(base / ARTIFACT_SCOPE_PROFILE),
        integrity_report_path=str(base / ARTIFACT_INTEGRITY_REPORT),
        metrics_summary_path=str(base / ARTIFACT_METRICS_SUMMARY),
        trade_log_path=str(base / ARTIFACT_TRADE_LOG),
        candidate_audit_path=str(base / ARTIFACT_CANDIDATE_AUDIT),
        blocker_breakdown_path=str(base / ARTIFACT_BLOCKER_BREAKDOWN),
        exit_breakdown_path=str(base / ARTIFACT_EXIT_BREAKDOWN),
        differential_report_path=str(base / ARTIFACT_DIFFERENTIAL_REPORT),
        effective_inputs_path=str(base / ARTIFACT_EFFECTIVE_INPUTS_JSON),
        effective_overrides_flat_path=str(base / ARTIFACT_EFFECTIVE_OVERRIDES_FLAT_JSON),
    )


def artifact_plan_to_dict(plan: ReplayArtifactPlan) -> dict[str, Any]:
    return {
        "root_dir": plan.root_dir,
        "manifest_path": plan.manifest_path,
        "log_dir": plan.log_dir,
        "artifacts_dir": plan.artifacts_dir,
        "dataset_summary_path": plan.dataset_summary_path,
        "scope_profile_path": plan.scope_profile_path,
        "integrity_report_path": plan.integrity_report_path,
        "metrics_summary_path": plan.metrics_summary_path,
        "trade_log_path": plan.trade_log_path,
        "candidate_audit_path": plan.candidate_audit_path,
        "blocker_breakdown_path": plan.blocker_breakdown_path,
        "exit_breakdown_path": plan.exit_breakdown_path,
        "differential_report_path": plan.differential_report_path,
        "effective_inputs_path": plan.effective_inputs_path,
        "effective_overrides_flat_path": plan.effective_overrides_flat_path,
    }


def build_run_context(
    selection_plan: ReplaySelectionPlan,
    run_config: ReplayRunConfig,
    *,
    run_root: str | Path | None = None,
) -> ReplayRunContext:
    runner = ReplayRunner(run_root=run_root)
    return runner.build_run_context(selection_plan, run_config)




def build_effective_inputs_snapshot(
    run_context: ReplayRunContext,
) -> EffectiveInputsSnapshot:
    selection_plan = run_context.selection_plan
    run_config = run_context.run_config
    manifest = run_context.manifest

    report_profile_input: dict[str, Any] = {}
    research_profile_input: dict[str, Any] = {}

    flattened_overrides = build_flattened_override_payload(run_context)

    return EffectiveInputsSnapshot(
        snapshot_created_at=run_context.created_at,
        dataset_input={
            "dataset_id": manifest.dataset.dataset_id,
            "dataset_fingerprint": manifest.dataset.dataset_fingerprint,
            "source_path": manifest.dataset.source_path,
            "coverage_summary": dict(manifest.dataset.coverage_summary),
            "selection_mode": selection_plan.selection_mode.value,
            "trading_dates": list(selection_plan.trading_dates),
            "intraday_window": {
                "start": selection_plan.intraday_window.start,
                "end": selection_plan.intraday_window.end,
            },
            "session_segment": selection_plan.session_segment,
            "selection_fingerprint": selection_plan.selection_fingerprint,
        },
        replay_profile_input={
            "doctrine_mode": run_context.doctrine_mode.value,
            "scope": manifest.replay.scope.value,
            "speed_mode": manifest.replay.speed_mode.value,
            "side_mode": manifest.replay.side_mode.value,
            "fill_model": manifest.replay.fill_model,
            "reset_policy": run_config.reset_policy,
            "integrity_required_checks": list(run_config.integrity_required_checks),
            "integrity_waivers": list(run_config.integrity_waivers),
        },
        experiment_input={
            "family": manifest.experiment.family.value if manifest.experiment.family else None,
            "baseline_ref": manifest.experiment.baseline_ref,
            "override_pack_id": manifest.experiment.override_pack_id,
            "shadow_label": manifest.experiment.shadow_label,
            "differential_pair_id": manifest.experiment.differential_pair_id,
            "profiles": {
                "dataset_profile": manifest.profiles.dataset_profile,
                "replay_profile": manifest.profiles.replay_profile,
                "experiment_profile": manifest.profiles.experiment_profile,
                "batch_profile": manifest.profiles.batch_profile,
                "forensic_profile": manifest.profiles.forensic_profile,
                "integrity_profile": manifest.profiles.integrity_profile,
            },
        },
        report_profile_input=report_profile_input,
        research_profile_input=research_profile_input,
        flattened_overrides=flattened_overrides,
        input_fingerprint=selection_plan.selection_fingerprint,
    )


def build_flattened_override_payload(
    run_context: ReplayRunContext,
) -> dict[str, Any]:
    manifest = run_context.manifest
    return {
        "run_id": run_context.run_id,
        "created_at": run_context.created_at,
        "doctrine_mode": run_context.doctrine_mode.value,
        "override_pack_id": manifest.experiment.override_pack_id,
        "shadow_label": manifest.experiment.shadow_label,
        "baseline_ref": manifest.experiment.baseline_ref,
        "differential_pair_id": manifest.experiment.differential_pair_id,
        "notes": list(run_context.run_config.notes),
    }


def effective_inputs_snapshot_to_dict(
    snapshot: EffectiveInputsSnapshot,
) -> dict[str, Any]:
    return effective_inputs_to_dict(snapshot)


def flattened_override_payload_to_dict(
    payload: dict[str, Any],
) -> dict[str, Any]:
    return dict(payload)


def _validate_run_config(config: ReplayRunConfig) -> None:
    if not config.reset_policy or not config.reset_policy.strip():
        raise ReplayRunnerValidationError("reset_policy must be non-empty")

    if config.doctrine_mode is DoctrineMode.LOCKED:
        if config.override_pack_id is not None:
            raise ReplayRunnerValidationError(
                "locked run must not carry override_pack_id"
            )
        if config.differential_pair_id is not None:
            raise ReplayRunnerValidationError(
                "locked run must not carry differential_pair_id"
            )
        if config.baseline_ref is not None:
            raise ReplayRunnerValidationError(
                "locked run must not carry baseline_ref"
            )

    if config.doctrine_mode is DoctrineMode.SHADOW:
        if config.override_pack_id is None:
            raise ReplayRunnerValidationError(
                "shadow run requires override_pack_id"
            )

    if config.doctrine_mode is DoctrineMode.DIFFERENTIAL:
        if config.baseline_ref is None:
            raise ReplayRunnerValidationError(
                "differential run requires baseline_ref"
            )
        if config.differential_pair_id is None:
            raise ReplayRunnerValidationError(
                "differential run requires differential_pair_id"
            )

    if config.created_at is not None:
        _parse_created_at(config.created_at)

    for note in config.notes:
        if not isinstance(note, str):
            raise ReplayRunnerValidationError(
                f"run note must be string, got {note!r}"
            )


def _report_paths_for_mode(
    *,
    doctrine_mode: DoctrineMode,
    artifact_plan: ReplayArtifactPlan,
) -> tuple[str, ...]:
    base = list(artifact_plan.report_paths_minimum())
    base.extend(
        [
            artifact_plan.trade_log_path,
            artifact_plan.candidate_audit_path,
            artifact_plan.blocker_breakdown_path,
            artifact_plan.exit_breakdown_path,
        ]
    )

    if doctrine_mode is DoctrineMode.DIFFERENTIAL:
        base.append(artifact_plan.differential_report_path)

    return tuple(base)


def _verdict_tags_for_mode(
    *,
    doctrine_mode: DoctrineMode,
    integrity_verdict: IntegrityVerdict | None,
) -> tuple[ReplayVerdictTag, ...]:
    tags: list[ReplayVerdictTag] = []

    if doctrine_mode is DoctrineMode.LOCKED:
        tags.append(ReplayVerdictTag.CONTRACTUAL_BASELINE)
    elif doctrine_mode is DoctrineMode.SHADOW:
        tags.append(ReplayVerdictTag.SHADOW_EVIDENCE_ONLY)
    elif doctrine_mode is DoctrineMode.DIFFERENTIAL:
        tags.append(ReplayVerdictTag.DIFFERENTIAL_COMPARISON)
    else:
        raise ReplayRunnerValidationError(
            f"unsupported doctrine_mode: {doctrine_mode!r}"
        )

    if integrity_verdict is IntegrityVerdict.FAIL:
        tags.append(ReplayVerdictTag.INVALIDATED_BY_INTEGRITY)

    return tuple(tags)


def _default_speed_mode():
    return ReplaySpeedMode.ACCELERATED


def _default_side_mode():
    return ReplaySideMode.MIRRORED_BOTH


def _utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _parse_created_at(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        return datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ReplayRunnerValidationError(
            f"created_at must be ISO-8601 compatible, got {value!r}"
        ) from exc


def _run_timestamp(created_at: str) -> str:
    dt = _parse_created_at(created_at)
    return dt.strftime("%Y%m%d_%H%M%S")


def _slug(value: str | None) -> str:
    if value is None:
        return ""
    value = value.strip().lower()
    safe = []
    for ch in value:
        if ch.isalnum():
            safe.append(ch)
        elif ch in ("-", "_"):
            safe.append(ch)
        else:
            safe.append("_")
    slugged = "".join(safe).strip("_")
    while "__" in slugged:
        slugged = slugged.replace("__", "_")
    return slugged


__all__ = [
    "ReplayRunnerError",
    "ReplayRunnerValidationError",
    "ReplayRunConfig",
    "ReplayArtifactPlan",
    "ReplayRunContext",
    "ReplayRunner",
    "generate_run_id",
    "validate_run_id_string",
    "plan_artifacts",
    "artifact_plan_to_dict",
    "build_run_context",
    "build_effective_inputs_snapshot",
    "build_flattened_override_payload",
    "effective_inputs_snapshot_to_dict",
    "flattened_override_payload_to_dict",
]
