"""
app/mme_scalpx/replay/contracts.py

Replay-local contract surfaces for the MME-ScalpX Permanent Replay & Validation
Framework.

R1 Constitution Freeze
----------------------
This module owns:
- replay-local constants and artifact names
- manifest field-name surfaces
- profile kind labels
- replay contract dataclasses
- replay-local validation helpers
- replay manifest serialization helpers
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from .modes import (
    DoctrineMode,
    ExperimentFamily,
    IntegrityVerdict,
    MarketDayTag,
    ReplayScope,
    ReplaySelectionMode,
    ReplaySideMode,
    ReplaySpeedMode,
    ReplayVerdictTag,
)

REPLAY_CHAPTER_NAME = "replay"
REPLAY_RUNS_DIRNAME = "run/replay"

ARTIFACT_MANIFEST = "00_manifest.json"
ARTIFACT_DATASET_SUMMARY = "01_dataset_summary.json"
ARTIFACT_SCOPE_PROFILE = "02_scope_profile.json"
ARTIFACT_INTEGRITY_REPORT = "03_integrity_report.json"
ARTIFACT_METRICS_SUMMARY = "04_metrics_summary.json"
ARTIFACT_TRADE_LOG = "05_trade_log.csv"
ARTIFACT_CANDIDATE_AUDIT = "06_candidate_audit.csv"
ARTIFACT_BLOCKER_BREAKDOWN = "07_blocker_breakdown.json"
ARTIFACT_EXIT_BREAKDOWN = "08_exit_breakdown.json"
ARTIFACT_DIFFERENTIAL_REPORT = "09_differential_report.json"


ARTIFACT_RUN_SUMMARY_JSON = "10_run_summary.json"
ARTIFACT_RUN_SUMMARY_CSV = "11_run_summary.csv"
ARTIFACT_PARAMETER_SURFACE_CSV = "12_parameter_surface.csv"
ARTIFACT_FEATURE_GATE_SURFACE_CSV = "13_feature_gate_surface.csv"
ARTIFACT_TRADE_LOG_DETAILED_CSV = "14_trade_log_detailed.csv"
ARTIFACT_CANDIDATE_AUDIT_DETAILED_CSV = "15_candidate_audit_detailed.csv"
ARTIFACT_OPERATOR_NOTES_JSON = "16_operator_notes.json"
ARTIFACT_EFFECTIVE_INPUTS_JSON = "17_effective_inputs.json"
ARTIFACT_EFFECTIVE_OVERRIDES_FLAT_JSON = "18_effective_overrides_flat.json"
ARTIFACT_RESEARCH_SUMMARY_JSON = "19_research_summary.json"

ARTIFACT_COMPARISON_SUMMARY_JSON = "20_comparison_summary.json"
ARTIFACT_COMPARISON_SUMMARY_CSV = "21_comparison_summary.csv"
ARTIFACT_TRADE_DIFF_CSV = "22_trade_diff.csv"
ARTIFACT_BLOCKER_DIFF_CSV = "23_blocker_diff.csv"
ARTIFACT_REGIME_DIFF_CSV = "24_regime_diff.csv"
ARTIFACT_FEATURE_GATE_DIFF_CSV = "25_feature_gate_diff.csv"

OPTIONAL_REPORTING_ARTIFACT_FILENAMES = (
    ARTIFACT_RUN_SUMMARY_JSON,
    ARTIFACT_RUN_SUMMARY_CSV,
    ARTIFACT_PARAMETER_SURFACE_CSV,
    ARTIFACT_FEATURE_GATE_SURFACE_CSV,
    ARTIFACT_TRADE_LOG_DETAILED_CSV,
    ARTIFACT_CANDIDATE_AUDIT_DETAILED_CSV,
    ARTIFACT_OPERATOR_NOTES_JSON,
    ARTIFACT_EFFECTIVE_INPUTS_JSON,
    ARTIFACT_EFFECTIVE_OVERRIDES_FLAT_JSON,
    ARTIFACT_RESEARCH_SUMMARY_JSON,
)

OPTIONAL_COMPARISON_ARTIFACT_FILENAMES = (
    ARTIFACT_COMPARISON_SUMMARY_JSON,
    ARTIFACT_COMPARISON_SUMMARY_CSV,
    ARTIFACT_TRADE_DIFF_CSV,
    ARTIFACT_BLOCKER_DIFF_CSV,
    ARTIFACT_REGIME_DIFF_CSV,
    ARTIFACT_FEATURE_GATE_DIFF_CSV,
)

REQUIRED_ARTIFACT_FILENAMES = (
    ARTIFACT_MANIFEST,
    ARTIFACT_DATASET_SUMMARY,
    ARTIFACT_SCOPE_PROFILE,
    ARTIFACT_INTEGRITY_REPORT,
    ARTIFACT_METRICS_SUMMARY,
)

OPTIONAL_ARTIFACT_FILENAMES = (
    ARTIFACT_TRADE_LOG,
    ARTIFACT_CANDIDATE_AUDIT,
    ARTIFACT_BLOCKER_BREAKDOWN,
    ARTIFACT_EXIT_BREAKDOWN,
    ARTIFACT_DIFFERENTIAL_REPORT,
)

ARTIFACTS_SUBDIR = "artifacts"
LOGS_SUBDIR = "logs"


REPLAY_REGISTRY_DIRNAME = "run/replay/_registry"

REGISTRY_RUN_CSV = "run_registry.csv"
REGISTRY_COMPARISON_CSV = "comparison_registry.csv"
REGISTRY_PARAMETER_CSV = "parameter_registry.csv"
REGISTRY_FEATURE_GATE_CSV = "feature_gate_registry.csv"

REGISTRY_FILENAMES = (
    REGISTRY_RUN_CSV,
    REGISTRY_COMPARISON_CSV,
    REGISTRY_PARAMETER_CSV,
    REGISTRY_FEATURE_GATE_CSV,
)

SHEET_RUN_REGISTRY = "run_registry"
SHEET_COMPARISON_SUMMARY = "comparison_summary"
SHEET_PARAMETER_SURFACE = "parameter_surface"
SHEET_FEATURE_GATE_SURFACE = "feature_gate_surface"
SHEET_TRADE_LOG = "trade_log"
SHEET_CANDIDATE_AUDIT = "candidate_audit"
SHEET_BLOCKER_ANALYSIS = "blocker_analysis"
SHEET_REGIME_ANALYSIS = "regime_analysis"
SHEET_OPERATOR_NOTES = "operator_notes"
SHEET_EFFECTIVE_INPUTS = "effective_inputs"
SHEET_EFFECTIVE_OVERRIDES = "effective_overrides"

ALL_STANDARD_SHEET_NAMES = (
    SHEET_RUN_REGISTRY,
    SHEET_COMPARISON_SUMMARY,
    SHEET_PARAMETER_SURFACE,
    SHEET_FEATURE_GATE_SURFACE,
    SHEET_TRADE_LOG,
    SHEET_CANDIDATE_AUDIT,
    SHEET_BLOCKER_ANALYSIS,
    SHEET_REGIME_ANALYSIS,
    SHEET_OPERATOR_NOTES,
    SHEET_EFFECTIVE_INPUTS,
    SHEET_EFFECTIVE_OVERRIDES,
)

MANIFEST_FIELD_RUN_ID = "run_id"
MANIFEST_FIELD_CHAPTER = "chapter"
MANIFEST_FIELD_CREATED_AT = "created_at"
MANIFEST_FIELD_CODE_REVISION = "code_revision"
MANIFEST_FIELD_DATASET = "dataset"
MANIFEST_FIELD_SELECTION = "selection"
MANIFEST_FIELD_REPLAY = "replay"
MANIFEST_FIELD_PROFILES = "profiles"
MANIFEST_FIELD_EXPERIMENT = "experiment"
MANIFEST_FIELD_RESET = "reset"
MANIFEST_FIELD_INTEGRITY = "integrity"
MANIFEST_FIELD_ARTIFACTS = "artifacts"
MANIFEST_FIELD_VERDICT_TAGS = "verdict_tags"
MANIFEST_FIELD_NOTES = "notes"

MANIFEST_REQUIRED_TOP_LEVEL_FIELDS = (
    MANIFEST_FIELD_RUN_ID,
    MANIFEST_FIELD_CHAPTER,
    MANIFEST_FIELD_CREATED_AT,
    MANIFEST_FIELD_CODE_REVISION,
    MANIFEST_FIELD_DATASET,
    MANIFEST_FIELD_SELECTION,
    MANIFEST_FIELD_REPLAY,
    MANIFEST_FIELD_PROFILES,
    MANIFEST_FIELD_EXPERIMENT,
    MANIFEST_FIELD_RESET,
    MANIFEST_FIELD_INTEGRITY,
    MANIFEST_FIELD_ARTIFACTS,
    MANIFEST_FIELD_VERDICT_TAGS,
    MANIFEST_FIELD_NOTES,
)

PROFILE_KIND_DATASET = "dataset_profile"
PROFILE_KIND_REPLAY = "replay_profile"
PROFILE_KIND_EXPERIMENT = "experiment_profile"
PROFILE_KIND_BATCH = "batch_profile"
PROFILE_KIND_FORENSIC = "forensic_profile"
PROFILE_KIND_INTEGRITY = "integrity_profile"

ALL_PROFILE_KINDS = (
    PROFILE_KIND_DATASET,
    PROFILE_KIND_REPLAY,
    PROFILE_KIND_EXPERIMENT,
    PROFILE_KIND_BATCH,
    PROFILE_KIND_FORENSIC,
    PROFILE_KIND_INTEGRITY,
)

INTEGRITY_CHECK_HEARTBEAT = "heartbeat_integrity"
INTEGRITY_CHECK_HASH_FRESHNESS = "hash_freshness"
INTEGRITY_CHECK_SNAPSHOT_SYNC = "snapshot_sync_validity"
INTEGRITY_CHECK_STALE_LEG = "stale_leg_detection"
INTEGRITY_CHECK_RESET_CLEANLINESS = "reset_cleanliness"
INTEGRITY_CHECK_REPRODUCIBILITY = "reproducibility_proof"

REQUIRED_INTEGRITY_CHECKS = (
    INTEGRITY_CHECK_HEARTBEAT,
    INTEGRITY_CHECK_HASH_FRESHNESS,
    INTEGRITY_CHECK_SNAPSHOT_SYNC,
    INTEGRITY_CHECK_STALE_LEG,
    INTEGRITY_CHECK_RESET_CLEANLINESS,
    INTEGRITY_CHECK_REPRODUCIBILITY,
)


RUN_SUMMARY_COLUMNS = (
    "run_id",
    "created_at",
    "started_at",
    "completed_at",
    "duration_ms",
    "chapter",
    "doctrine_mode",
    "replay_scope",
    "speed_mode",
    "side_mode",
    "dataset_id",
    "dataset_fingerprint",
    "selection_mode",
    "trading_dates",
    "window_start",
    "window_end",
    "dataset_profile",
    "replay_profile",
    "experiment_profile",
    "batch_profile",
    "forensic_profile",
    "integrity_profile",
    "override_pack_id",
    "shadow_label",
    "input_fingerprint",
    "integrity_verdict",
    "waiver_count",
    "pnl_total",
    "trade_count",
    "win_count",
    "loss_count",
    "candidate_count",
    "blocker_count",
    "regime_pass_count",
    "remarks",
    "operator_verdict",
    "research_tags",
    "ml_export_eligible",
)

COMPARISON_SUMMARY_COLUMNS = (
    "comparison_id",
    "comparison_created_at",
    "baseline_run_id",
    "shadow_run_id",
    "identical_input_basis",
    "dataset_fingerprint_match",
    "baseline_override_id",
    "shadow_override_id",
    "changed_parameters",
    "baseline_pnl",
    "shadow_pnl",
    "pnl_diff",
    "baseline_trade_count",
    "shadow_trade_count",
    "trade_count_diff",
    "baseline_candidate_count",
    "shadow_candidate_count",
    "candidate_diff",
    "baseline_blocker_count",
    "shadow_blocker_count",
    "blocker_diff",
    "baseline_regime_pass_count",
    "shadow_regime_pass_count",
    "regime_pass_diff",
    "integrity_status",
    "operator_verdict",
    "narration",
)

PARAMETER_SURFACE_COLUMNS = (
    "comparison_id",
    "run_id",
    "parameter_name",
    "parameter_group",
    "baseline_value",
    "shadow_value",
    "effective_value",
    "changed_flag",
    "source_profile",
    "remarks",
)

FEATURE_GATE_SURFACE_COLUMNS = (
    "comparison_id",
    "gate_name",
    "gate_family",
    "baseline_enabled",
    "shadow_enabled",
    "baseline_threshold",
    "shadow_threshold",
    "baseline_pass_count",
    "shadow_pass_count",
    "candidate_impact",
    "trade_impact",
    "pnl_impact_hint",
    "remarks",
)

TRADE_LOG_COLUMNS = (
    "run_id",
    "trade_id",
    "side",
    "entry_ts",
    "exit_ts",
    "entry_mode",
    "entry_price",
    "exit_price",
    "qty",
    "pnl",
    "exit_reason",
    "regime_state",
    "economics_valid",
    "remarks",
)

CANDIDATE_AUDIT_COLUMNS = (
    "run_id",
    "frame_id",
    "source_frame_id",
    "side",
    "candidate_found",
    "regime_ok",
    "economics_valid",
    "blocker_name",
    "blocker_reason",
    "decision_action",
    "entry_mode",
    "remarks",
)

BLOCKER_ANALYSIS_COLUMNS = (
    "comparison_id",
    "blocker_name",
    "baseline_count",
    "shadow_count",
    "diff",
    "remarks",
)

REGIME_ANALYSIS_COLUMNS = (
    "comparison_id",
    "regime_bucket",
    "baseline_frames",
    "shadow_frames",
    "baseline_candidates",
    "shadow_candidates",
    "baseline_trades",
    "shadow_trades",
    "baseline_pnl",
    "shadow_pnl",
    "remarks",
)

OPERATOR_NOTES_COLUMNS = (
    "comparison_id",
    "verdict",
    "observation_summary",
    "primary_improvement",
    "primary_regression",
    "possible_reason",
    "caution_note",
    "next_test_recommended",
)

EFFECTIVE_INPUTS_COLUMNS = (
    "snapshot_created_at",
    "dataset_input",
    "replay_profile_input",
    "experiment_input",
    "report_profile_input",
    "research_profile_input",
    "flattened_overrides",
    "input_fingerprint",
)

RUN_REGISTRY_COLUMNS = RUN_SUMMARY_COLUMNS
COMPARISON_REGISTRY_COLUMNS = COMPARISON_SUMMARY_COLUMNS
PARAMETER_REGISTRY_COLUMNS = PARAMETER_SURFACE_COLUMNS
FEATURE_GATE_REGISTRY_COLUMNS = FEATURE_GATE_SURFACE_COLUMNS


@dataclass(frozen=True, slots=True)
class DatasetSection:
    dataset_id: str
    dataset_fingerprint: str
    source_path: str
    coverage_summary: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class SelectionWindow:
    start: str | None = None
    end: str | None = None


@dataclass(frozen=True, slots=True)
class SelectionSection:
    selection_mode: ReplaySelectionMode
    trading_dates: tuple[str, ...]
    window: SelectionWindow = field(default_factory=SelectionWindow)
    session_segment: str | None = None
    market_tags: tuple[MarketDayTag, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class ReplaySection:
    scope: ReplayScope
    speed_mode: ReplaySpeedMode
    doctrine_mode: DoctrineMode
    side_mode: ReplaySideMode
    fill_model: str | None = None


@dataclass(frozen=True, slots=True)
class ProfilesSection:
    dataset_profile: str | None = None
    replay_profile: str | None = None
    experiment_profile: str | None = None
    batch_profile: str | None = None
    forensic_profile: str | None = None
    integrity_profile: str | None = None


@dataclass(frozen=True, slots=True)
class ExperimentSection:
    family: ExperimentFamily | None = None
    baseline_ref: str | None = None
    override_pack_id: str | None = None
    shadow_label: str | None = None
    differential_pair_id: str | None = None


@dataclass(frozen=True, slots=True)
class ResetSection:
    policy: str
    reset_started_at: str | None = None
    reset_completed_at: str | None = None
    reset_verdict: IntegrityVerdict | None = None


@dataclass(frozen=True, slots=True)
class IntegritySection:
    required_checks: tuple[str, ...]
    verdict: IntegrityVerdict | None = None
    waivers: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class ArtifactsSection:
    root_dir: str
    manifest_path: str
    log_dir: str
    report_paths: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class ReplayRunManifest:
    run_id: str
    chapter: str
    created_at: str
    code_revision: str | None
    dataset: DatasetSection
    selection: SelectionSection
    replay: ReplaySection
    profiles: ProfilesSection
    experiment: ExperimentSection
    reset: ResetSection
    integrity: IntegritySection
    artifacts: ArtifactsSection
    verdict_tags: tuple[ReplayVerdictTag, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)




@dataclass(frozen=True, slots=True)
class ReportProfileSection:
    report_profile_id: str | None = None
    export_csv: bool = True
    export_xlsx: bool = False
    include_trade_log: bool = True
    include_candidate_audit: bool = True
    include_feature_gate_analysis: bool = True
    include_operator_notes: bool = True


@dataclass(frozen=True, slots=True)
class ResearchProfileSection:
    research_profile_id: str | None = None
    study_name: str | None = None
    hypothesis: str | None = None
    research_tags: tuple[str, ...] = field(default_factory=tuple)
    production_comparable: bool = False
    exploratory_only: bool = True
    ml_export_eligible: bool = False


@dataclass(frozen=True, slots=True)
class EffectiveInputsSnapshot:
    snapshot_created_at: str
    dataset_input: Mapping[str, Any]
    replay_profile_input: Mapping[str, Any]
    experiment_input: Mapping[str, Any]
    report_profile_input: Mapping[str, Any]
    research_profile_input: Mapping[str, Any]
    flattened_overrides: Mapping[str, Any]
    input_fingerprint: str


@dataclass(frozen=True, slots=True)
class RunSummaryRow:
    run_id: str
    created_at: str
    started_at: str | None = None
    completed_at: str | None = None
    duration_ms: int | None = None
    chapter: str = REPLAY_CHAPTER_NAME
    doctrine_mode: DoctrineMode | str = ""
    replay_scope: ReplayScope | str = ""
    speed_mode: ReplaySpeedMode | str = ""
    side_mode: ReplaySideMode | str = ""
    dataset_id: str = ""
    dataset_fingerprint: str = ""
    selection_mode: ReplaySelectionMode | str = ""
    trading_dates: tuple[str, ...] = field(default_factory=tuple)
    window_start: str | None = None
    window_end: str | None = None
    dataset_profile: str | None = None
    replay_profile: str | None = None
    experiment_profile: str | None = None
    batch_profile: str | None = None
    forensic_profile: str | None = None
    integrity_profile: str | None = None
    override_pack_id: str | None = None
    shadow_label: str | None = None
    input_fingerprint: str = ""
    integrity_verdict: IntegrityVerdict | str | None = None
    waiver_count: int = 0
    pnl_total: float | int | None = None
    trade_count: int = 0
    win_count: int = 0
    loss_count: int = 0
    candidate_count: int = 0
    blocker_count: int = 0
    regime_pass_count: int = 0
    remarks: str | None = None
    operator_verdict: str | None = None
    research_tags: tuple[str, ...] = field(default_factory=tuple)
    ml_export_eligible: bool = False


@dataclass(frozen=True, slots=True)
class ComparisonSummaryRow:
    comparison_id: str
    comparison_created_at: str
    baseline_run_id: str
    shadow_run_id: str
    identical_input_basis: bool
    dataset_fingerprint_match: bool
    baseline_override_id: str | None = None
    shadow_override_id: str | None = None
    changed_parameters: tuple[str, ...] = field(default_factory=tuple)
    baseline_pnl: float | int | None = None
    shadow_pnl: float | int | None = None
    pnl_diff: float | int | None = None
    baseline_trade_count: int = 0
    shadow_trade_count: int = 0
    trade_count_diff: int = 0
    baseline_candidate_count: int = 0
    shadow_candidate_count: int = 0
    candidate_diff: int = 0
    baseline_blocker_count: int = 0
    shadow_blocker_count: int = 0
    blocker_diff: int = 0
    baseline_regime_pass_count: int = 0
    shadow_regime_pass_count: int = 0
    regime_pass_diff: int = 0
    integrity_status: IntegrityVerdict | str | None = None
    operator_verdict: str | None = None
    narration: str | None = None


@dataclass(frozen=True, slots=True)
class ParameterSurfaceRow:
    comparison_id: str | None = None
    run_id: str | None = None
    parameter_name: str = ""
    parameter_group: str | None = None
    baseline_value: Any = None
    shadow_value: Any = None
    effective_value: Any = None
    changed_flag: bool = False
    source_profile: str | None = None
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class FeatureGateSurfaceRow:
    comparison_id: str | None = None
    gate_name: str = ""
    gate_family: str | None = None
    baseline_enabled: bool = False
    shadow_enabled: bool = False
    baseline_threshold: Any = None
    shadow_threshold: Any = None
    baseline_pass_count: int | None = None
    shadow_pass_count: int | None = None
    candidate_impact: int | None = None
    trade_impact: int | None = None
    pnl_impact_hint: str | None = None
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class TradeLogRow:
    run_id: str
    trade_id: str
    side: str
    entry_ts: str | None = None
    exit_ts: str | None = None
    entry_mode: str | None = None
    entry_price: float | int | None = None
    exit_price: float | int | None = None
    qty: int | float | None = None
    pnl: float | int | None = None
    exit_reason: str | None = None
    regime_state: str | None = None
    economics_valid: bool | None = None
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class CandidateAuditRow:
    run_id: str
    frame_id: str
    source_frame_id: str | None = None
    side: str | None = None
    candidate_found: bool = False
    regime_ok: bool | None = None
    economics_valid: bool | None = None
    blocker_name: str | None = None
    blocker_reason: str | None = None
    decision_action: str | None = None
    entry_mode: str | None = None
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class BlockerAnalysisRow:
    comparison_id: str
    blocker_name: str
    baseline_count: int = 0
    shadow_count: int = 0
    diff: int = 0
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class RegimeAnalysisRow:
    comparison_id: str
    regime_bucket: str
    baseline_frames: int = 0
    shadow_frames: int = 0
    baseline_candidates: int = 0
    shadow_candidates: int = 0
    baseline_trades: int = 0
    shadow_trades: int = 0
    baseline_pnl: float | int | None = None
    shadow_pnl: float | int | None = None
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class OperatorNotesRecord:
    comparison_id: str
    verdict: str | None = None
    observation_summary: str | None = None
    primary_improvement: str | None = None
    primary_regression: str | None = None
    possible_reason: str | None = None
    caution_note: str | None = None
    next_test_recommended: str | None = None
def validate_run_id(run_id: str) -> None:
    if not run_id or not run_id.strip():
        raise ValueError("run_id must be non-empty")


def validate_manifest_chapter(chapter: str) -> None:
    if chapter != REPLAY_CHAPTER_NAME:
        raise ValueError(
            f"manifest chapter must be {REPLAY_CHAPTER_NAME!r}, got {chapter!r}"
        )


def validate_required_integrity_checks(required_checks: Sequence[str]) -> None:
    present = set(required_checks)
    missing = [name for name in REQUIRED_INTEGRITY_CHECKS if name not in present]
    if missing:
        raise ValueError(f"missing required integrity checks: {missing}")


def validate_required_artifact_paths(
    manifest_path: str,
    report_paths: Sequence[str],
) -> None:
    filenames_present = {Path(manifest_path).name}
    filenames_present.update(Path(path).name for path in report_paths)

    missing = sorted(
        filename
        for filename in REQUIRED_ARTIFACT_FILENAMES
        if filename not in filenames_present
    )
    if missing:
        raise ValueError(f"missing required artifact paths: {missing}")


def validate_shadow_visibility(
    doctrine_mode: DoctrineMode,
    experiment_profile: str | None,
    override_pack_id: str | None,
) -> None:
    if doctrine_mode is DoctrineMode.SHADOW:
        if not experiment_profile:
            raise ValueError("shadow replay requires experiment_profile")
        if not override_pack_id:
            raise ValueError("shadow replay requires override_pack_id")


def validate_differential_visibility(
    doctrine_mode: DoctrineMode,
    differential_pair_id: str | None,
    baseline_ref: str | None,
) -> None:
    if doctrine_mode is DoctrineMode.DIFFERENTIAL:
        if not differential_pair_id:
            raise ValueError("differential replay requires differential_pair_id")
        if not baseline_ref:
            raise ValueError("differential replay requires baseline_ref")


def validate_locked_visibility(
    doctrine_mode: DoctrineMode,
    override_pack_id: str | None,
    differential_pair_id: str | None,
) -> None:
    if doctrine_mode is DoctrineMode.LOCKED:
        if override_pack_id:
            raise ValueError("locked replay must not carry override_pack_id")
        if differential_pair_id:
            raise ValueError("locked replay must not carry differential_pair_id")


def validate_selection_section(selection: SelectionSection) -> None:
    if not selection.trading_dates:
        raise ValueError("selection.trading_dates must be non-empty")


def validate_integrity_section(integrity: IntegritySection) -> None:
    validate_required_integrity_checks(integrity.required_checks)


def validate_artifacts_section(artifacts: ArtifactsSection) -> None:
    if not artifacts.root_dir.strip():
        raise ValueError("artifacts.root_dir must be non-empty")
    if not artifacts.manifest_path.strip():
        raise ValueError("artifacts.manifest_path must be non-empty")
    if not artifacts.log_dir.strip():
        raise ValueError("artifacts.log_dir must be non-empty")
    validate_required_artifact_paths(
        manifest_path=artifacts.manifest_path,
        report_paths=artifacts.report_paths,
    )


def validate_manifest(manifest: ReplayRunManifest) -> None:
    validate_run_id(manifest.run_id)
    validate_manifest_chapter(manifest.chapter)
    validate_selection_section(manifest.selection)
    validate_integrity_section(manifest.integrity)
    validate_artifacts_section(manifest.artifacts)
    validate_shadow_visibility(
        doctrine_mode=manifest.replay.doctrine_mode,
        experiment_profile=manifest.profiles.experiment_profile,
        override_pack_id=manifest.experiment.override_pack_id,
    )
    validate_differential_visibility(
        doctrine_mode=manifest.replay.doctrine_mode,
        differential_pair_id=manifest.experiment.differential_pair_id,
        baseline_ref=manifest.experiment.baseline_ref,
    )
    validate_locked_visibility(
        doctrine_mode=manifest.replay.doctrine_mode,
        override_pack_id=manifest.experiment.override_pack_id,
        differential_pair_id=manifest.experiment.differential_pair_id,
    )




def _validate_non_empty_text(field_name: str, value: str | None) -> None:
    if value is None or not str(value).strip():
        raise ValueError(f"{field_name} must be non-empty")


def validate_sheet_name(sheet_name: str) -> None:
    if sheet_name not in ALL_STANDARD_SHEET_NAMES:
        raise ValueError(f"unsupported sheet name: {sheet_name!r}")


def validate_required_columns(
    actual: Sequence[str],
    required: Sequence[str],
) -> None:
    present = set(actual)
    missing = [name for name in required if name not in present]
    if missing:
        raise ValueError(f"missing required columns: {missing}")


def validate_effective_inputs_snapshot(snapshot: EffectiveInputsSnapshot) -> None:
    _validate_non_empty_text("snapshot.snapshot_created_at", snapshot.snapshot_created_at)
    _validate_non_empty_text("snapshot.input_fingerprint", snapshot.input_fingerprint)

    mappings = {
        "dataset_input": snapshot.dataset_input,
        "replay_profile_input": snapshot.replay_profile_input,
        "experiment_input": snapshot.experiment_input,
        "report_profile_input": snapshot.report_profile_input,
        "research_profile_input": snapshot.research_profile_input,
        "flattened_overrides": snapshot.flattened_overrides,
    }
    for name, value in mappings.items():
        if value is None:
            raise ValueError(f"snapshot.{name} must not be None")


def validate_run_summary_row(row: RunSummaryRow) -> None:
    _validate_non_empty_text("row.run_id", row.run_id)
    _validate_non_empty_text("row.created_at", row.created_at)
    _validate_non_empty_text("row.dataset_id", row.dataset_id)
    _validate_non_empty_text("row.dataset_fingerprint", row.dataset_fingerprint)
    _validate_non_empty_text("row.input_fingerprint", row.input_fingerprint)


def validate_comparison_summary_row(row: ComparisonSummaryRow) -> None:
    _validate_non_empty_text("row.comparison_id", row.comparison_id)
    _validate_non_empty_text("row.comparison_created_at", row.comparison_created_at)
    _validate_non_empty_text("row.baseline_run_id", row.baseline_run_id)
    _validate_non_empty_text("row.shadow_run_id", row.shadow_run_id)


def validate_parameter_surface_row(row: ParameterSurfaceRow) -> None:
    _validate_non_empty_text("row.parameter_name", row.parameter_name)


def validate_feature_gate_surface_row(row: FeatureGateSurfaceRow) -> None:
    _validate_non_empty_text("row.gate_name", row.gate_name)
def _serialize_value(value: Any) -> Any:
    if value is None:
        return None
    if hasattr(value, "value"):
        return value.value
    if is_dataclass(value):
        return {k: _serialize_value(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {str(k): _serialize_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize_value(v) for v in value]
    return value


def manifest_to_dict(manifest: ReplayRunManifest) -> dict[str, Any]:
    validate_manifest(manifest)
    return _serialize_value(manifest)


def dataclass_to_dict(value: Any) -> dict[str, Any]:
    if not is_dataclass(value):
        raise TypeError("expected dataclass instance")
    return _serialize_value(value)


def effective_inputs_to_dict(
    snapshot: EffectiveInputsSnapshot,
) -> dict[str, Any]:
    validate_effective_inputs_snapshot(snapshot)
    return dataclass_to_dict(snapshot)


def row_to_dict(value: Any) -> dict[str, Any]:
    if not is_dataclass(value):
        raise TypeError("expected dataclass row")
    return dataclass_to_dict(value)


__all__ = [
    "REPLAY_CHAPTER_NAME",
    "REPLAY_RUNS_DIRNAME",
    "ARTIFACT_MANIFEST",
    "ARTIFACT_DATASET_SUMMARY",
    "ARTIFACT_SCOPE_PROFILE",
    "ARTIFACT_INTEGRITY_REPORT",
    "ARTIFACT_METRICS_SUMMARY",
    "ARTIFACT_TRADE_LOG",
    "ARTIFACT_CANDIDATE_AUDIT",
    "ARTIFACT_BLOCKER_BREAKDOWN",
    "ARTIFACT_EXIT_BREAKDOWN",
    "ARTIFACT_DIFFERENTIAL_REPORT",
    "ARTIFACT_RUN_SUMMARY_JSON",
    "ARTIFACT_RUN_SUMMARY_CSV",
    "ARTIFACT_PARAMETER_SURFACE_CSV",
    "ARTIFACT_FEATURE_GATE_SURFACE_CSV",
    "ARTIFACT_TRADE_LOG_DETAILED_CSV",
    "ARTIFACT_CANDIDATE_AUDIT_DETAILED_CSV",
    "ARTIFACT_OPERATOR_NOTES_JSON",
    "ARTIFACT_EFFECTIVE_INPUTS_JSON",
    "ARTIFACT_EFFECTIVE_OVERRIDES_FLAT_JSON",
    "ARTIFACT_RESEARCH_SUMMARY_JSON",
    "ARTIFACT_COMPARISON_SUMMARY_JSON",
    "ARTIFACT_COMPARISON_SUMMARY_CSV",
    "ARTIFACT_TRADE_DIFF_CSV",
    "ARTIFACT_BLOCKER_DIFF_CSV",
    "ARTIFACT_REGIME_DIFF_CSV",
    "ARTIFACT_FEATURE_GATE_DIFF_CSV",
    "REQUIRED_ARTIFACT_FILENAMES",
    "OPTIONAL_ARTIFACT_FILENAMES",
    "OPTIONAL_REPORTING_ARTIFACT_FILENAMES",
    "OPTIONAL_COMPARISON_ARTIFACT_FILENAMES",
    "ARTIFACTS_SUBDIR",
    "LOGS_SUBDIR",
    "REPLAY_REGISTRY_DIRNAME",
    "REGISTRY_RUN_CSV",
    "REGISTRY_COMPARISON_CSV",
    "REGISTRY_PARAMETER_CSV",
    "REGISTRY_FEATURE_GATE_CSV",
    "REGISTRY_FILENAMES",
    "SHEET_RUN_REGISTRY",
    "SHEET_COMPARISON_SUMMARY",
    "SHEET_PARAMETER_SURFACE",
    "SHEET_FEATURE_GATE_SURFACE",
    "SHEET_TRADE_LOG",
    "SHEET_CANDIDATE_AUDIT",
    "SHEET_BLOCKER_ANALYSIS",
    "SHEET_REGIME_ANALYSIS",
    "SHEET_OPERATOR_NOTES",
    "SHEET_EFFECTIVE_INPUTS",
    "SHEET_EFFECTIVE_OVERRIDES",
    "ALL_STANDARD_SHEET_NAMES",
    "MANIFEST_REQUIRED_TOP_LEVEL_FIELDS",
    "ALL_PROFILE_KINDS",
    "REQUIRED_INTEGRITY_CHECKS",
    "RUN_SUMMARY_COLUMNS",
    "COMPARISON_SUMMARY_COLUMNS",
    "PARAMETER_SURFACE_COLUMNS",
    "FEATURE_GATE_SURFACE_COLUMNS",
    "TRADE_LOG_COLUMNS",
    "CANDIDATE_AUDIT_COLUMNS",
    "BLOCKER_ANALYSIS_COLUMNS",
    "REGIME_ANALYSIS_COLUMNS",
    "OPERATOR_NOTES_COLUMNS",
    "EFFECTIVE_INPUTS_COLUMNS",
    "RUN_REGISTRY_COLUMNS",
    "COMPARISON_REGISTRY_COLUMNS",
    "PARAMETER_REGISTRY_COLUMNS",
    "FEATURE_GATE_REGISTRY_COLUMNS",
    "DatasetSection",
    "SelectionWindow",
    "SelectionSection",
    "ReplaySection",
    "ProfilesSection",
    "ExperimentSection",
    "ResetSection",
    "IntegritySection",
    "ArtifactsSection",
    "ReplayRunManifest",
    "ReportProfileSection",
    "ResearchProfileSection",
    "EffectiveInputsSnapshot",
    "RunSummaryRow",
    "ComparisonSummaryRow",
    "ParameterSurfaceRow",
    "FeatureGateSurfaceRow",
    "TradeLogRow",
    "CandidateAuditRow",
    "BlockerAnalysisRow",
    "RegimeAnalysisRow",
    "OperatorNotesRecord",
    "validate_manifest",
    "validate_sheet_name",
    "validate_required_columns",
    "validate_effective_inputs_snapshot",
    "validate_run_summary_row",
    "validate_comparison_summary_row",
    "validate_parameter_surface_row",
    "validate_feature_gate_surface_row",
    "manifest_to_dict",
    "dataclass_to_dict",
    "effective_inputs_to_dict",
    "row_to_dict",
]

# === Phase A.4 economics-source requirements freeze ===

ECONOMICS_SOURCE_MODE_RECORDED = "recorded"
ECONOMICS_SOURCE_MODE_DERIVED_FROM_EFFECTIVE_INPUTS = "derived_from_effective_inputs"
ECONOMICS_SOURCE_MODE_UNAVAILABLE = "unavailable"

ECONOMICS_SOURCE_STATUS_READY = "ready"
ECONOMICS_SOURCE_STATUS_INSUFFICIENT_SOURCE_TRUTH = "insufficient_source_truth"

ALLOWED_ECONOMICS_SOURCE_MODES = (
    ECONOMICS_SOURCE_MODE_RECORDED,
    ECONOMICS_SOURCE_MODE_DERIVED_FROM_EFFECTIVE_INPUTS,
    ECONOMICS_SOURCE_MODE_UNAVAILABLE,
)

ALLOWED_ECONOMICS_SOURCE_STATUSES = (
    ECONOMICS_SOURCE_STATUS_READY,
    ECONOMICS_SOURCE_STATUS_INSUFFICIENT_SOURCE_TRUTH,
)

ECONOMICS_REQUIRED_QUOTE_COST_FIELDS = (
    "ts_event",
    "source_frame_id",
    "symbol",
    "bid",
    "ask",
    "ltp",
    "tick_size",
)

ECONOMICS_REQUIRED_CANDIDATE_CONTEXT_FIELDS = (
    "side",
    "selected_leg",
    "entry_mode",
)

ECONOMICS_RECORDED_POLICY_FIELDS = (
    "target_ticks",
    "stop_ticks",
    "reward_ticks",
    "reward_cost_ratio",
    "economics_reason",
)

ECONOMICS_EFFECTIVE_INPUT_POLICY_FIELDS = (
    "economics_policy_id",
    "target_policy_surface",
    "stop_policy_surface",
    "reward_cost_threshold",
    "economics_formula_version",
    "cost_model_id",
)

ECONOMICS_REQUIRED_PROVENANCE_FIELDS = (
    "economics_source_mode",
    "economics_source_status",
    "economics_formula_version",
)

ECONOMICS_OPTIONAL_HELPFUL_FIELDS = (
    "lot_size",
    "strike",
    "option_type",
    "expiry",
    "strike_step",
    "slippage_ticks",
    "fees_per_lot",
    "round_trip_cost",
    "premium_in_ticks",
    "delta_proxy",
    "moneyness_bucket",
    "underlying_ltp",
    "fut_ltp",
    "iv",
    "atm_iv",
)

ECONOMICS_DERIVABLE_FIELDS = (
    "spread",
    "mid_price",
    "spread_ticks",
    "cost_ticks",
    "reward_ticks",
    "reward_cost_ratio",
    "economics_valid",
    "reward_cost_valid",
)

ECONOMICS_NEVER_INVENT_FIELDS = (
    "target_ticks",
    "stop_ticks",
    "reward_ticks",
    "reward_cost_ratio",
    "economics_valid",
    "reward_cost_valid",
    "economics_reason",
    "economics_fail",
)

REPLAY_DATASET_OWNED_ECONOMICS_FIELDS = (
    "ts_event",
    "source_frame_id",
    "symbol",
    "bid",
    "ask",
    "ltp",
    "tick_size",
    "side",
    "selected_leg",
    "entry_mode",
)

RESEARCH_CAPTURE_OWNED_ECONOMICS_FIELDS = (
    "round_trip_cost",
    "fees_per_lot",
    "slippage_ticks",
    "premium_in_ticks",
    "delta_proxy",
    "moneyness_bucket",
    "underlying_ltp",
    "fut_ltp",
    "iv",
    "atm_iv",
)

REPLAY_EFFECTIVE_INPUT_OWNED_ECONOMICS_FIELDS = (
    "economics_policy_id",
    "target_policy_surface",
    "stop_policy_surface",
    "reward_cost_threshold",
    "economics_formula_version",
    "cost_model_id",
)

@dataclass(frozen=True)
class EconomicsSourceRequirements:
    required_quote_cost_fields: tuple[str, ...] = ECONOMICS_REQUIRED_QUOTE_COST_FIELDS
    required_candidate_context_fields: tuple[str, ...] = ECONOMICS_REQUIRED_CANDIDATE_CONTEXT_FIELDS
    recorded_policy_fields: tuple[str, ...] = ECONOMICS_RECORDED_POLICY_FIELDS
    effective_input_policy_fields: tuple[str, ...] = ECONOMICS_EFFECTIVE_INPUT_POLICY_FIELDS
    required_provenance_fields: tuple[str, ...] = ECONOMICS_REQUIRED_PROVENANCE_FIELDS
    optional_helpful_fields: tuple[str, ...] = ECONOMICS_OPTIONAL_HELPFUL_FIELDS
    derivable_fields: tuple[str, ...] = ECONOMICS_DERIVABLE_FIELDS
    never_invent_fields: tuple[str, ...] = ECONOMICS_NEVER_INVENT_FIELDS

@dataclass(frozen=True)
class EconomicsSourceCoverage:
    source_mode: str
    source_status: str
    quote_cost_fields_present: tuple[str, ...] = ()
    candidate_context_fields_present: tuple[str, ...] = ()
    recorded_policy_fields_present: tuple[str, ...] = ()
    effective_input_policy_fields_present: tuple[str, ...] = ()
    provenance_fields_present: tuple[str, ...] = ()
    missing_required_fields: tuple[str, ...] = ()
    eligible_for_economics_evaluation: bool = False

@dataclass(frozen=True)
class EffectiveEconomicsInputs:
    economics_policy_id: str | None = None
    target_policy_surface: dict[str, object] | None = None
    stop_policy_surface: dict[str, object] | None = None
    reward_cost_threshold: float | int | None = None
    economics_formula_version: str | None = None
    cost_model_id: str | None = None

def build_default_economics_source_requirements() -> EconomicsSourceRequirements:
    value = EconomicsSourceRequirements()
    validate_economics_source_requirements(value)
    return value

def _economics_serialize_value(value: object) -> object:
    if isinstance(value, tuple):
        return [_economics_serialize_value(item) for item in value]
    if isinstance(value, list):
        return [_economics_serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _economics_serialize_value(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return {
            field_name: _economics_serialize_value(getattr(value, field_name))
            for field_name in value.__dataclass_fields__
        }
    return value

def economics_source_requirements_to_dict(value: EconomicsSourceRequirements) -> dict[str, object]:
    validate_economics_source_requirements(value)
    return _economics_serialize_value(value)

def economics_source_coverage_to_dict(value: EconomicsSourceCoverage) -> dict[str, object]:
    validate_economics_source_coverage(value)
    return _economics_serialize_value(value)

def effective_economics_inputs_to_dict(value: EffectiveEconomicsInputs) -> dict[str, object]:
    validate_effective_economics_inputs(value)
    return _economics_serialize_value(value)

def validate_economics_source_requirements(value: EconomicsSourceRequirements) -> None:
    if not value.required_quote_cost_fields:
        raise ValueError("required_quote_cost_fields must not be empty")
    if not value.required_candidate_context_fields:
        raise ValueError("required_candidate_context_fields must not be empty")
    if not value.recorded_policy_fields:
        raise ValueError("recorded_policy_fields must not be empty")
    if not value.effective_input_policy_fields:
        raise ValueError("effective_input_policy_fields must not be empty")
    if not value.required_provenance_fields:
        raise ValueError("required_provenance_fields must not be empty")
    if not value.never_invent_fields:
        raise ValueError("never_invent_fields must not be empty")

def validate_effective_economics_inputs(value: EffectiveEconomicsInputs) -> None:
    if value.reward_cost_threshold is not None and value.reward_cost_threshold <= 0:
        raise ValueError("reward_cost_threshold must be > 0 when provided")
    if value.economics_policy_id is None and any(
        candidate is not None
        for candidate in (
            value.target_policy_surface,
            value.stop_policy_surface,
            value.reward_cost_threshold,
            value.economics_formula_version,
            value.cost_model_id,
        )
    ):
        raise ValueError("economics_policy_id is required when effective economics inputs are provided")

def validate_economics_source_coverage(value: EconomicsSourceCoverage) -> None:
    if value.source_mode not in ALLOWED_ECONOMICS_SOURCE_MODES:
        raise ValueError(f"unsupported economics source mode: {value.source_mode!r}")
    if value.source_status not in ALLOWED_ECONOMICS_SOURCE_STATUSES:
        raise ValueError(f"unsupported economics source status: {value.source_status!r}")
    if value.eligible_for_economics_evaluation and value.missing_required_fields:
        raise ValueError("eligible_for_economics_evaluation cannot be true when missing_required_fields is non-empty")
    if value.source_mode == ECONOMICS_SOURCE_MODE_UNAVAILABLE and value.eligible_for_economics_evaluation:
        raise ValueError("unavailable economics source mode cannot be eligible_for_economics_evaluation")
    if (
        value.source_status == ECONOMICS_SOURCE_STATUS_READY
        and not value.eligible_for_economics_evaluation
    ):
        raise ValueError("ready economics source status requires eligible_for_economics_evaluation=true")

__all__ = tuple(__all__) + (
    "ECONOMICS_SOURCE_MODE_RECORDED",
    "ECONOMICS_SOURCE_MODE_DERIVED_FROM_EFFECTIVE_INPUTS",
    "ECONOMICS_SOURCE_MODE_UNAVAILABLE",
    "ECONOMICS_SOURCE_STATUS_READY",
    "ECONOMICS_SOURCE_STATUS_INSUFFICIENT_SOURCE_TRUTH",
    "ALLOWED_ECONOMICS_SOURCE_MODES",
    "ALLOWED_ECONOMICS_SOURCE_STATUSES",
    "ECONOMICS_REQUIRED_QUOTE_COST_FIELDS",
    "ECONOMICS_REQUIRED_CANDIDATE_CONTEXT_FIELDS",
    "ECONOMICS_RECORDED_POLICY_FIELDS",
    "ECONOMICS_EFFECTIVE_INPUT_POLICY_FIELDS",
    "ECONOMICS_REQUIRED_PROVENANCE_FIELDS",
    "ECONOMICS_OPTIONAL_HELPFUL_FIELDS",
    "ECONOMICS_DERIVABLE_FIELDS",
    "ECONOMICS_NEVER_INVENT_FIELDS",
    "REPLAY_DATASET_OWNED_ECONOMICS_FIELDS",
    "RESEARCH_CAPTURE_OWNED_ECONOMICS_FIELDS",
    "REPLAY_EFFECTIVE_INPUT_OWNED_ECONOMICS_FIELDS",
    "EconomicsSourceRequirements",
    "EconomicsSourceCoverage",
    "EffectiveEconomicsInputs",
    "build_default_economics_source_requirements",
    "economics_source_requirements_to_dict",
    "economics_source_coverage_to_dict",
    "effective_economics_inputs_to_dict",
    "validate_economics_source_requirements",
    "validate_economics_source_coverage",
    "validate_effective_economics_inputs",
)


# === Phase A.5 replay feed-input contract freeze ===

from dataclasses import dataclass as _phase_a5_dataclass

REPLAY_FEED_INPUT_CONTRACT_VERSION = "v1"

REPLAY_FEED_INPUT_SOURCE_MODE_QUOTE_ONLY_RECORDED = "quote_only_recorded"
REPLAY_FEED_INPUT_SOURCE_MODE_ECONOMICS_ENRICHED_RECORDED = "economics_enriched_recorded"

REPLAY_FEED_INPUT_SOURCE_MODES = (
    REPLAY_FEED_INPUT_SOURCE_MODE_QUOTE_ONLY_RECORDED,
    REPLAY_FEED_INPUT_SOURCE_MODE_ECONOMICS_ENRICHED_RECORDED,
)

REPLAY_FEED_INPUT_COMMON_REQUIRED_FIELDS = (
    "ts_event",
    "symbol",
    "bid",
    "ask",
    "ltp",
)

REPLAY_FEED_INPUT_QUOTE_ONLY_OPTIONAL_FIELDS = (
    "source_frame_id",
    "side",
    "selected_leg",
    "entry_mode",
    "tick_size",
    "target_ticks",
    "stop_ticks",
    "reward_ticks",
    "reward_cost_ratio",
    "economics_reason",
)

REPLAY_FEED_INPUT_ECONOMICS_ENRICHED_REQUIRED_FIELDS = (
    "source_frame_id",
    "side",
    "selected_leg",
    "entry_mode",
    "tick_size",
    "target_ticks",
    "stop_ticks",
    "reward_ticks",
    "reward_cost_ratio",
    "economics_reason",
)

REPLAY_FEED_INPUT_OPTIONAL_PROVENANCE_FIELDS = (
    "source_file",
    "source_stem",
    "trading_day",
)

REPLAY_FEED_INPUT_NEVER_INVENT_FIELDS = (
    "source_frame_id",
    "side",
    "selected_leg",
    "entry_mode",
    "tick_size",
    "target_ticks",
    "stop_ticks",
    "reward_ticks",
    "reward_cost_ratio",
    "economics_reason",
)


@_phase_a5_dataclass(frozen=True, slots=True)
class ReplayFeedInputModeContract:
    source_mode: str
    required_fields: tuple[str, ...]
    optional_fields: tuple[str, ...]
    economics_evaluable: bool
    never_invent_fields: tuple[str, ...]


@_phase_a5_dataclass(frozen=True, slots=True)
class ReplayFeedInputContract:
    contract_version: str
    source_modes: tuple[str, ...]
    common_required_fields: tuple[str, ...]
    optional_provenance_fields: tuple[str, ...]
    quote_only_mode: ReplayFeedInputModeContract
    economics_enriched_mode: ReplayFeedInputModeContract
    never_invent_fields: tuple[str, ...]


def _phase_a5_validate_string_tuple(name: str, values: tuple[str, ...]) -> None:
    if not isinstance(values, tuple):
        raise TypeError(f"{name} must be tuple[str, ...], got {type(values)!r}")
    seen: set[str] = set()
    for item in values:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{name} items must be non-empty strings, got {item!r}")
        if item in seen:
            raise ValueError(f"{name} contains duplicate field {item!r}")
        seen.add(item)


def validate_replay_feed_input_mode_contract(contract: ReplayFeedInputModeContract) -> None:
    if contract.source_mode not in REPLAY_FEED_INPUT_SOURCE_MODES:
        raise ValueError(
            f"unsupported replay feed-input source_mode {contract.source_mode!r}; "
            f"expected one of {REPLAY_FEED_INPUT_SOURCE_MODES!r}"
        )
    _phase_a5_validate_string_tuple("required_fields", contract.required_fields)
    _phase_a5_validate_string_tuple("optional_fields", contract.optional_fields)
    _phase_a5_validate_string_tuple("never_invent_fields", contract.never_invent_fields)


def validate_replay_feed_input_contract(contract: ReplayFeedInputContract) -> None:
    if contract.contract_version != REPLAY_FEED_INPUT_CONTRACT_VERSION:
        raise ValueError(
            f"unexpected replay feed-input contract_version {contract.contract_version!r}; "
            f"expected {REPLAY_FEED_INPUT_CONTRACT_VERSION!r}"
        )
    _phase_a5_validate_string_tuple("source_modes", contract.source_modes)
    _phase_a5_validate_string_tuple("common_required_fields", contract.common_required_fields)
    _phase_a5_validate_string_tuple("optional_provenance_fields", contract.optional_provenance_fields)
    _phase_a5_validate_string_tuple("never_invent_fields", contract.never_invent_fields)

    validate_replay_feed_input_mode_contract(contract.quote_only_mode)
    validate_replay_feed_input_mode_contract(contract.economics_enriched_mode)

    if contract.quote_only_mode.source_mode != REPLAY_FEED_INPUT_SOURCE_MODE_QUOTE_ONLY_RECORDED:
        raise ValueError("quote_only_mode must use quote_only_recorded source mode")
    if contract.economics_enriched_mode.source_mode != REPLAY_FEED_INPUT_SOURCE_MODE_ECONOMICS_ENRICHED_RECORDED:
        raise ValueError("economics_enriched_mode must use economics_enriched_recorded source mode")
    if contract.quote_only_mode.economics_evaluable:
        raise ValueError("quote_only_mode must not be economics_evaluable")
    if not contract.economics_enriched_mode.economics_evaluable:
        raise ValueError("economics_enriched_mode must be economics_evaluable")


def build_default_replay_feed_input_contract() -> ReplayFeedInputContract:
    contract = ReplayFeedInputContract(
        contract_version=REPLAY_FEED_INPUT_CONTRACT_VERSION,
        source_modes=REPLAY_FEED_INPUT_SOURCE_MODES,
        common_required_fields=REPLAY_FEED_INPUT_COMMON_REQUIRED_FIELDS,
        optional_provenance_fields=REPLAY_FEED_INPUT_OPTIONAL_PROVENANCE_FIELDS,
        quote_only_mode=ReplayFeedInputModeContract(
            source_mode=REPLAY_FEED_INPUT_SOURCE_MODE_QUOTE_ONLY_RECORDED,
            required_fields=(),
            optional_fields=REPLAY_FEED_INPUT_QUOTE_ONLY_OPTIONAL_FIELDS,
            economics_evaluable=False,
            never_invent_fields=REPLAY_FEED_INPUT_NEVER_INVENT_FIELDS,
        ),
        economics_enriched_mode=ReplayFeedInputModeContract(
            source_mode=REPLAY_FEED_INPUT_SOURCE_MODE_ECONOMICS_ENRICHED_RECORDED,
            required_fields=REPLAY_FEED_INPUT_ECONOMICS_ENRICHED_REQUIRED_FIELDS,
            optional_fields=(),
            economics_evaluable=True,
            never_invent_fields=REPLAY_FEED_INPUT_NEVER_INVENT_FIELDS,
        ),
        never_invent_fields=REPLAY_FEED_INPUT_NEVER_INVENT_FIELDS,
    )
    validate_replay_feed_input_contract(contract)
    return contract


def replay_feed_input_mode_contract_to_dict(contract: ReplayFeedInputModeContract) -> dict[str, object]:
    validate_replay_feed_input_mode_contract(contract)
    return {
        "source_mode": contract.source_mode,
        "required_fields": list(contract.required_fields),
        "optional_fields": list(contract.optional_fields),
        "economics_evaluable": contract.economics_evaluable,
        "never_invent_fields": list(contract.never_invent_fields),
    }


def replay_feed_input_contract_to_dict(contract: ReplayFeedInputContract) -> dict[str, object]:
    validate_replay_feed_input_contract(contract)
    return {
        "contract_version": contract.contract_version,
        "source_modes": list(contract.source_modes),
        "common_required_fields": list(contract.common_required_fields),
        "optional_provenance_fields": list(contract.optional_provenance_fields),
        "quote_only_mode": replay_feed_input_mode_contract_to_dict(contract.quote_only_mode),
        "economics_enriched_mode": replay_feed_input_mode_contract_to_dict(contract.economics_enriched_mode),
        "never_invent_fields": list(contract.never_invent_fields),
    }


def validate_replay_feed_input_row(source_mode: str, row: dict[str, object]) -> None:
    if source_mode not in REPLAY_FEED_INPUT_SOURCE_MODES:
        raise ValueError(
            f"unsupported replay feed-input source_mode {source_mode!r}; "
            f"expected one of {REPLAY_FEED_INPUT_SOURCE_MODES!r}"
        )
    if not isinstance(row, dict):
        raise TypeError(f"replay feed-input row must be dict[str, object], got {type(row)!r}")

    contract = build_default_replay_feed_input_contract()
    mode_contract = (
        contract.quote_only_mode
        if source_mode == REPLAY_FEED_INPUT_SOURCE_MODE_QUOTE_ONLY_RECORDED
        else contract.economics_enriched_mode
    )

    required_fields = contract.common_required_fields + mode_contract.required_fields
    missing: list[str] = []
    for field_name in required_fields:
        value = row.get(field_name)
        if value is None:
            missing.append(field_name)
            continue
        if isinstance(value, str) and not value.strip():
            missing.append(field_name)

    if missing:
        raise ValueError(
            f"replay feed-input row missing required fields for source_mode={source_mode!r}: "
            f"{tuple(missing)!r}"
        )



__all__ = (
    "REPLAY_FEED_INPUT_CONTRACT_VERSION",
    "REPLAY_FEED_INPUT_SOURCE_MODE_QUOTE_ONLY_RECORDED",
    "REPLAY_FEED_INPUT_SOURCE_MODE_ECONOMICS_ENRICHED_RECORDED",
    "REPLAY_FEED_INPUT_SOURCE_MODES",
    "REPLAY_FEED_INPUT_COMMON_REQUIRED_FIELDS",
    "REPLAY_FEED_INPUT_QUOTE_ONLY_OPTIONAL_FIELDS",
    "REPLAY_FEED_INPUT_ECONOMICS_ENRICHED_REQUIRED_FIELDS",
    "REPLAY_FEED_INPUT_OPTIONAL_PROVENANCE_FIELDS",
    "REPLAY_FEED_INPUT_NEVER_INVENT_FIELDS",
    "ReplayFeedInputModeContract",
    "ReplayFeedInputContract",
    "build_default_replay_feed_input_contract",
    "validate_replay_feed_input_mode_contract",
    "validate_replay_feed_input_contract",
    "replay_feed_input_mode_contract_to_dict",
    "replay_feed_input_contract_to_dict",
    "validate_replay_feed_input_row",
)

# === Phase A.6 replay dataset capability profile freeze ===

REPLAY_DATASET_CAPABILITY_PROFILE_VERSION = "v1"


@dataclass(frozen=True, slots=True)
class ReplayDatasetCapabilityProfile:
    profile_version: str
    profile_id: str
    declared_source_mode: str
    feed_input_contract_version: str
    required_normalized_observed_fields: tuple[str, ...]
    optional_normalized_observed_fields: tuple[str, ...] = ()
    economics_evaluable: bool = False
    notes: tuple[str, ...] = ()


def _phase_a6_validate_string_tuple(name: str, values: tuple[str, ...]) -> None:
    if not isinstance(values, tuple):
        raise TypeError(f"{name} must be tuple[str, ...], got {type(values)!r}")
    seen: set[str] = set()
    for item in values:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{name} items must be non-empty strings, got {item!r}")
        if item in seen:
            raise ValueError(f"{name} contains duplicate field {item!r}")
        seen.add(item)


def validate_replay_dataset_capability_profile(profile: ReplayDatasetCapabilityProfile) -> None:
    if profile.profile_version != REPLAY_DATASET_CAPABILITY_PROFILE_VERSION:
        raise ValueError(
            f"unexpected replay dataset capability profile_version {profile.profile_version!r}; "
            f"expected {REPLAY_DATASET_CAPABILITY_PROFILE_VERSION!r}"
        )
    if profile.declared_source_mode not in REPLAY_FEED_INPUT_SOURCE_MODES:
        raise ValueError(
            f"unsupported declared_source_mode {profile.declared_source_mode!r}; "
            f"expected one of {REPLAY_FEED_INPUT_SOURCE_MODES!r}"
        )
    if not isinstance(profile.profile_id, str) or not profile.profile_id.strip():
        raise ValueError(f"profile_id must be non-empty string, got {profile.profile_id!r}")
    if profile.feed_input_contract_version != REPLAY_FEED_INPUT_CONTRACT_VERSION:
        raise ValueError(
            f"unexpected feed_input_contract_version {profile.feed_input_contract_version!r}; "
            f"expected {REPLAY_FEED_INPUT_CONTRACT_VERSION!r}"
        )
    _phase_a6_validate_string_tuple(
        "required_normalized_observed_fields",
        profile.required_normalized_observed_fields,
    )
    _phase_a6_validate_string_tuple(
        "optional_normalized_observed_fields",
        profile.optional_normalized_observed_fields,
    )
    _phase_a6_validate_string_tuple("notes", profile.notes)


def replay_dataset_capability_profile_to_dict(
    profile: ReplayDatasetCapabilityProfile,
) -> dict[str, object]:
    validate_replay_dataset_capability_profile(profile)
    return {
        "profile_version": profile.profile_version,
        "profile_id": profile.profile_id,
        "declared_source_mode": profile.declared_source_mode,
        "feed_input_contract_version": profile.feed_input_contract_version,
        "required_normalized_observed_fields": list(profile.required_normalized_observed_fields),
        "optional_normalized_observed_fields": list(profile.optional_normalized_observed_fields),
        "economics_evaluable": profile.economics_evaluable,
        "notes": list(profile.notes),
    }


def build_quote_only_replay_dataset_capability_profile() -> ReplayDatasetCapabilityProfile:
    feed_contract = build_default_replay_feed_input_contract()
    profile = ReplayDatasetCapabilityProfile(
        profile_version=REPLAY_DATASET_CAPABILITY_PROFILE_VERSION,
        profile_id="replay_dataset_capability_quote_only_v1",
        declared_source_mode=REPLAY_FEED_INPUT_SOURCE_MODE_QUOTE_ONLY_RECORDED,
        feed_input_contract_version=feed_contract.contract_version,
        required_normalized_observed_fields=feed_contract.common_required_fields,
        optional_normalized_observed_fields=tuple(
            dict.fromkeys(
                feed_contract.quote_only_mode.optional_fields
                + feed_contract.optional_provenance_fields
            )
        ),
        economics_evaluable=False,
        notes=(
            "valid for quote-only recorded replay datasets",
            "economics truth remains non-conclusive when enriched fields are absent",
        ),
    )
    validate_replay_dataset_capability_profile(profile)
    return profile


def build_economics_enriched_replay_dataset_capability_profile() -> ReplayDatasetCapabilityProfile:
    feed_contract = build_default_replay_feed_input_contract()
    profile = ReplayDatasetCapabilityProfile(
        profile_version=REPLAY_DATASET_CAPABILITY_PROFILE_VERSION,
        profile_id="replay_dataset_capability_economics_enriched_v1",
        declared_source_mode=REPLAY_FEED_INPUT_SOURCE_MODE_ECONOMICS_ENRICHED_RECORDED,
        feed_input_contract_version=feed_contract.contract_version,
        required_normalized_observed_fields=tuple(
            dict.fromkeys(
                feed_contract.common_required_fields
                + feed_contract.economics_enriched_mode.required_fields
            )
        ),
        optional_normalized_observed_fields=feed_contract.optional_provenance_fields,
        economics_evaluable=True,
        notes=(
            "valid for economics-enriched recorded replay datasets",
            "enriched fields must be genuinely recorded, never invented downstream",
        ),
    )
    validate_replay_dataset_capability_profile(profile)
    return profile


if "__all__" in globals():
    __all__ = tuple(__all__) + (
        "REPLAY_DATASET_CAPABILITY_PROFILE_VERSION",
        "ReplayDatasetCapabilityProfile",
        "validate_replay_dataset_capability_profile",
        "replay_dataset_capability_profile_to_dict",
        "build_quote_only_replay_dataset_capability_profile",
        "build_economics_enriched_replay_dataset_capability_profile",
    )

# === Phase A.7 replay dataset declaration freeze ===

REPLAY_DATASET_DECLARATION_VERSION = "v1"


@dataclass(frozen=True, slots=True)
class ReplayDatasetDeclaration:
    declaration_version: str
    dataset_id: str
    dataset_root: str
    capability_profile_id: str
    capability_profile_version: str
    notes: tuple[str, ...] = ()


def validate_replay_dataset_declaration(declaration: ReplayDatasetDeclaration) -> None:
    if declaration.declaration_version != REPLAY_DATASET_DECLARATION_VERSION:
        raise ValueError(
            f"unexpected replay dataset declaration_version {declaration.declaration_version!r}; "
            f"expected {REPLAY_DATASET_DECLARATION_VERSION!r}"
        )
    if not isinstance(declaration.dataset_id, str) or not declaration.dataset_id.strip():
        raise ValueError(f"dataset_id must be non-empty string, got {declaration.dataset_id!r}")
    if not isinstance(declaration.dataset_root, str) or not declaration.dataset_root.strip():
        raise ValueError(f"dataset_root must be non-empty string, got {declaration.dataset_root!r}")
    if not isinstance(declaration.capability_profile_id, str) or not declaration.capability_profile_id.strip():
        raise ValueError(
            f"capability_profile_id must be non-empty string, got {declaration.capability_profile_id!r}"
        )
    if declaration.capability_profile_version != REPLAY_DATASET_CAPABILITY_PROFILE_VERSION:
        raise ValueError(
            f"unexpected capability_profile_version {declaration.capability_profile_version!r}; "
            f"expected {REPLAY_DATASET_CAPABILITY_PROFILE_VERSION!r}"
        )
    if not isinstance(declaration.notes, tuple):
        raise TypeError(f"notes must be tuple[str, ...], got {type(declaration.notes)!r}")


def replay_dataset_declaration_to_dict(
    declaration: ReplayDatasetDeclaration,
) -> dict[str, object]:
    validate_replay_dataset_declaration(declaration)
    return {
        "declaration_version": declaration.declaration_version,
        "dataset_id": declaration.dataset_id,
        "dataset_root": declaration.dataset_root,
        "capability_profile_id": declaration.capability_profile_id,
        "capability_profile_version": declaration.capability_profile_version,
        "notes": list(declaration.notes),
    }


def build_quote_only_replay_dataset_declaration(
    *,
    dataset_id: str,
    dataset_root: str,
) -> ReplayDatasetDeclaration:
    declaration = ReplayDatasetDeclaration(
        declaration_version=REPLAY_DATASET_DECLARATION_VERSION,
        dataset_id=dataset_id,
        dataset_root=dataset_root,
        capability_profile_id="replay_dataset_capability_quote_only_v1",
        capability_profile_version=REPLAY_DATASET_CAPABILITY_PROFILE_VERSION,
        notes=(
            "declares this replay dataset as quote-only recorded",
            "economics truth must remain non-conclusive unless a richer dataset is supplied",
        ),
    )
    validate_replay_dataset_declaration(declaration)
    return declaration


def build_economics_enriched_replay_dataset_declaration(
    *,
    dataset_id: str,
    dataset_root: str,
) -> ReplayDatasetDeclaration:
    declaration = ReplayDatasetDeclaration(
        declaration_version=REPLAY_DATASET_DECLARATION_VERSION,
        dataset_id=dataset_id,
        dataset_root=dataset_root,
        capability_profile_id="replay_dataset_capability_economics_enriched_v1",
        capability_profile_version=REPLAY_DATASET_CAPABILITY_PROFILE_VERSION,
        notes=(
            "declares this replay dataset as economics-enriched recorded",
            "enriched economics fields must be genuinely recorded upstream",
        ),
    )
    validate_replay_dataset_declaration(declaration)
    return declaration


if "__all__" in globals():
    __all__ = tuple(__all__) + (
        "REPLAY_DATASET_DECLARATION_VERSION",
        "ReplayDatasetDeclaration",
        "validate_replay_dataset_declaration",
        "replay_dataset_declaration_to_dict",
        "build_quote_only_replay_dataset_declaration",
        "build_economics_enriched_replay_dataset_declaration",
    )

