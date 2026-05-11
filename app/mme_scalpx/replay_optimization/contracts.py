"""Lane D replay optimization contract surfaces.

D1 Constitution Freeze
----------------------
This module is intentionally limited to names, schema surfaces, dataclasses,
thin validators, and serializers for offline replay optimization.

It must not import or call replay execution, broker adapters, Redis clients,
live services, risk/execution routing, third-party ML/dataframe libraries, or
any production strategy mutation code.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

LANE_D_NAME = "LANE_D_REPLAY_OPTIMIZATION"
REPLAY_OPTIMIZATION_CONTRACT_VERSION = "replay_optimization_d1_contract_v1"
REPLAY_OPTIMIZATION_PACKAGE_NAME = "replay_optimization"

CONFIG_DIRNAME = "etc/replay_optimization"
OUTPUT_ROOT = "run/replay_optimization"
EXPERIMENTS_DIRNAME = "experiments"
LEADERBOARDS_DIRNAME = "leaderboards"
ML_DATASETS_DIRNAME = "ml_datasets"
MODELS_DIRNAME = "models"
REPORTS_DIRNAME = "reports"

OPTIMIZATION_POLICY_FILE = "optimization_policy.json"
SWEEP_SPACE_CONTRACT_FILE = "sweep_space_contract.json"
ML_EXPORT_CONTRACT_FILE = "ml_export_contract.json"

ARTIFACT_OPTIMIZATION_MANIFEST = "00_optimization_manifest.json"
ARTIFACT_SWEEP_SPACE = "01_sweep_space.json"
ARTIFACT_CANDIDATE_MATRIX = "02_candidate_matrix.json"
ARTIFACT_REPLAY_INPUT_INDEX = "03_replay_input_index.json"
ARTIFACT_RAW_FEATURE_INDEX = "04_raw_feature_index.json"
ARTIFACT_RESULT_SUMMARY = "05_result_summary.csv"
ARTIFACT_LEADERBOARD = "06_leaderboard.csv"
ARTIFACT_ML_DATASET_SCHEMA = "07_ml_dataset_schema.json"
ARTIFACT_ML_TRAINING_MANIFEST = "08_ml_training_manifest.json"
ARTIFACT_OPTIMIZER_VERDICT = "09_optimizer_verdict.json"

REQUIRED_OPTIMIZATION_ARTIFACTS = (
    ARTIFACT_OPTIMIZATION_MANIFEST,
    ARTIFACT_SWEEP_SPACE,
    ARTIFACT_CANDIDATE_MATRIX,
    ARTIFACT_REPLAY_INPUT_INDEX,
    ARTIFACT_RAW_FEATURE_INDEX,
    ARTIFACT_RESULT_SUMMARY,
    ARTIFACT_LEADERBOARD,
    ARTIFACT_OPTIMIZER_VERDICT,
)

OPTIONAL_OPTIMIZATION_ARTIFACTS = (
    ARTIFACT_ML_DATASET_SCHEMA,
    ARTIFACT_ML_TRAINING_MANIFEST,
)

ALLOWED_INPUT_ROOTS = (
    "run/replay",
    "run/research_gate",
    "run/research_capture",
    "run/proofs",
    "run/reports",
)

FORBIDDEN_OWNERSHIP = (
    "broker_io",
    "order_placement",
    "position_truth",
    "risk_veto",
    "execution_routing",
    "live_redis_truth",
    "strategy_doctrine_mutation",
    "paper_live_enablement",
    "service_start_stop",
    "replay_engine_mutation",
)

STRATEGY_FAMILIES = ("MIST", "MISB", "MISC", "MISR", "MISO")
SIDES = ("CALL", "PUT")
REGIMES = ("LOWVOL", "NORMAL", "FAST")
SWEEP_STATUSES = ("PROPOSED_ONLY", "READY_FOR_REPLAY", "REPLAYED", "REJECTED")

VERDICT_NOT_READY_REPLAY_SOURCE_MISSING = "NOT_READY_REPLAY_SOURCE_MISSING"
VERDICT_NOT_READY_RAW_SOURCE_MISSING = "NOT_READY_RAW_SOURCE_MISSING"
VERDICT_NOT_READY_UNVERIFIED_REPLAY_SOURCE = "NOT_READY_UNVERIFIED_REPLAY_SOURCE"
VERDICT_READY_FOR_SINGLE_DAY_SWEEP = "READY_FOR_SINGLE_DAY_SWEEP"
VERDICT_READY_FOR_MULTIDAY_SWEEP = "READY_FOR_MULTIDAY_SWEEP"
VERDICT_READY_FOR_ML_DATASET_EXPORT = "READY_FOR_ML_DATASET_EXPORT"
VERDICT_READY_FOR_RESEARCH_ONLY_MODEL_TRAINING = "READY_FOR_RESEARCH_ONLY_MODEL_TRAINING"
VERDICT_REJECT_OVERFIT_RISK = "REJECT_OVERFIT_RISK"
VERDICT_REJECT_INSUFFICIENT_SAMPLE = "REJECT_INSUFFICIENT_SAMPLE"
VERDICT_RESEARCH_ONLY_FINDING = "RESEARCH_ONLY_FINDING"

OPTIMIZER_VERDICTS = (
    VERDICT_NOT_READY_REPLAY_SOURCE_MISSING,
    VERDICT_NOT_READY_RAW_SOURCE_MISSING,
    VERDICT_NOT_READY_UNVERIFIED_REPLAY_SOURCE,
    VERDICT_READY_FOR_SINGLE_DAY_SWEEP,
    VERDICT_READY_FOR_MULTIDAY_SWEEP,
    VERDICT_READY_FOR_ML_DATASET_EXPORT,
    VERDICT_READY_FOR_RESEARCH_ONLY_MODEL_TRAINING,
    VERDICT_REJECT_OVERFIT_RISK,
    VERDICT_REJECT_INSUFFICIENT_SAMPLE,
    VERDICT_RESEARCH_ONLY_FINDING,
)

OPTIMIZATION_RUN_COLUMNS = (
    "optimization_id",
    "created_at",
    "lane",
    "contract_version",
    "mode",
    "dataset_scope",
    "replay_input_root",
    "raw_input_root",
    "output_root",
    "sweep_candidate_count",
    "replay_result_count",
    "leaderboard_row_count",
    "ml_dataset_row_count",
    "optimizer_verdict",
    "remarks",
)

SWEEP_CANDIDATE_COLUMNS = (
    "optimization_id",
    "candidate_id",
    "strategy_family",
    "side",
    "regime",
    "parameter_group",
    "parameter_name",
    "baseline_value",
    "candidate_value",
    "target_points",
    "hard_stop_points",
    "profit_stall_points",
    "time_stall_seconds",
    "raw_filter_family",
    "raw_filter_name",
    "raw_filter_threshold",
    "status",
    "remarks",
)

REPLAY_RESULT_REF_COLUMNS = (
    "optimization_id",
    "candidate_id",
    "replay_run_id",
    "replay_artifact_root",
    "manifest_path",
    "result_summary_path",
    "trade_log_path",
    "candidate_audit_path",
    "integrity_verdict",
    "input_fingerprint",
    "source_verified",
    "remarks",
)

RAW_FEATURE_REF_COLUMNS = (
    "optimization_id",
    "candidate_id",
    "raw_source_root",
    "research_gate_root",
    "feature_family",
    "feature_name",
    "feature_window",
    "join_key",
    "coverage_pct",
    "source_verified",
    "remarks",
)

LEADERBOARD_COLUMNS = (
    "optimization_id",
    "rank",
    "candidate_id",
    "strategy_family",
    "side",
    "regime",
    "total_pnl",
    "trade_count",
    "win_count",
    "loss_count",
    "win_rate",
    "avg_pnl_per_trade",
    "max_drawdown",
    "profit_factor",
    "candidate_count",
    "blocker_count",
    "sample_days",
    "overfit_risk_flag",
    "optimizer_verdict",
    "remarks",
)

ML_DATASET_COLUMNS = (
    "optimization_id",
    "row_id",
    "candidate_id",
    "replay_run_id",
    "strategy_family",
    "side",
    "regime",
    "feature_vector_ref",
    "label_pnl",
    "label_profitable",
    "label_exit_reason",
    "usage_class",
    "compute_stage",
    "storage_target",
    "source_verified",
    "remarks",
)

OPTIMIZER_VERDICT_COLUMNS = (
    "optimization_id",
    "created_at",
    "verdict",
    "sample_days",
    "sample_trades",
    "best_candidate_id",
    "best_candidate_pnl",
    "risk_notes",
    "production_claim_allowed",
    "paper_live_approved",
    "remarks",
)

COLUMN_SURFACES = {
    "optimization_run": OPTIMIZATION_RUN_COLUMNS,
    "sweep_candidate": SWEEP_CANDIDATE_COLUMNS,
    "replay_result_ref": REPLAY_RESULT_REF_COLUMNS,
    "raw_feature_ref": RAW_FEATURE_REF_COLUMNS,
    "leaderboard": LEADERBOARD_COLUMNS,
    "ml_dataset": ML_DATASET_COLUMNS,
    "optimizer_verdict": OPTIMIZER_VERDICT_COLUMNS,
}


@dataclass(frozen=True, slots=True)
class LaneDSafetyPolicy:
    offline_only: bool = True
    broker_calls_allowed: bool = False
    live_redis_writes_allowed: bool = False
    paper_live_enablement_allowed: bool = False
    strategy_doctrine_mutation_allowed: bool = False
    runtime_service_start_allowed: bool = False
    replay_engine_mutation_allowed: bool = False
    production_claim_allowed: bool = False


@dataclass(frozen=True, slots=True)
class OptimizationManifest:
    optimization_id: str
    created_at: str
    lane: str = LANE_D_NAME
    contract_version: str = REPLAY_OPTIMIZATION_CONTRACT_VERSION
    mode: str = "CONTRACT_ONLY"
    dataset_scope: str | None = None
    replay_input_root: str | None = None
    raw_input_root: str | None = None
    output_root: str = OUTPUT_ROOT
    optimizer_verdict: str = VERDICT_NOT_READY_UNVERIFIED_REPLAY_SOURCE
    safety: LaneDSafetyPolicy = field(default_factory=LaneDSafetyPolicy)
    notes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class SweepCandidateRow:
    optimization_id: str
    candidate_id: str
    strategy_family: str
    side: str
    regime: str
    parameter_group: str
    parameter_name: str
    baseline_value: str
    candidate_value: str
    target_points: float | None = None
    hard_stop_points: float | None = None
    profit_stall_points: float | None = None
    time_stall_seconds: float | None = None
    raw_filter_family: str | None = None
    raw_filter_name: str | None = None
    raw_filter_threshold: str | None = None
    status: str = "PROPOSED_ONLY"
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class ReplayResultRefRow:
    optimization_id: str
    candidate_id: str
    replay_run_id: str
    replay_artifact_root: str
    manifest_path: str
    result_summary_path: str | None = None
    trade_log_path: str | None = None
    candidate_audit_path: str | None = None
    integrity_verdict: str | None = None
    input_fingerprint: str | None = None
    source_verified: bool = False
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class RawFeatureRefRow:
    optimization_id: str
    candidate_id: str
    raw_source_root: str
    research_gate_root: str | None
    feature_family: str
    feature_name: str
    feature_window: str | None = None
    join_key: str | None = None
    coverage_pct: float | None = None
    source_verified: bool = False
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class LeaderboardRow:
    optimization_id: str
    rank: int
    candidate_id: str
    strategy_family: str
    side: str
    regime: str
    total_pnl: float
    trade_count: int
    win_count: int
    loss_count: int
    win_rate: float
    avg_pnl_per_trade: float
    max_drawdown: float | None = None
    profit_factor: float | None = None
    candidate_count: int | None = None
    blocker_count: int | None = None
    sample_days: int = 0
    overfit_risk_flag: bool = True
    optimizer_verdict: str = VERDICT_REJECT_INSUFFICIENT_SAMPLE
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class MLDatasetRow:
    optimization_id: str
    row_id: str
    candidate_id: str
    replay_run_id: str
    strategy_family: str
    side: str
    regime: str
    feature_vector_ref: str
    label_pnl: float | None
    label_profitable: bool | None
    label_exit_reason: str | None
    usage_class: str = "research_only"
    compute_stage: str = "offline_replay"
    storage_target: str = OUTPUT_ROOT
    source_verified: bool = False
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class OptimizerVerdictRow:
    optimization_id: str
    created_at: str
    verdict: str
    sample_days: int
    sample_trades: int
    best_candidate_id: str | None = None
    best_candidate_pnl: float | None = None
    risk_notes: str | None = None
    production_claim_allowed: bool = False
    paper_live_approved: bool = False
    remarks: str | None = None


def validate_optimizer_verdict(value: str) -> str:
    if value not in OPTIMIZER_VERDICTS:
        raise ValueError(f"unknown optimizer verdict: {value}")
    return value


def validate_strategy_family(value: str) -> str:
    if value not in STRATEGY_FAMILIES:
        raise ValueError(f"unknown strategy family: {value}")
    return value


def validate_side(value: str) -> str:
    if value not in SIDES:
        raise ValueError(f"unknown side: {value}")
    return value


def validate_regime(value: str) -> str:
    if value not in REGIMES:
        raise ValueError(f"unknown regime: {value}")
    return value


def validate_allowed_input_root(path_value: str) -> str:
    normalized = Path(path_value).as_posix().rstrip("/")
    if not any(normalized == root or normalized.startswith(root + "/") for root in ALLOWED_INPUT_ROOTS):
        raise ValueError(f"Lane D input root not allowed: {path_value}")
    return path_value


def validate_output_root(path_value: str) -> str:
    normalized = Path(path_value).as_posix().rstrip("/")
    if normalized != OUTPUT_ROOT and not normalized.startswith(OUTPUT_ROOT + "/"):
        raise ValueError(f"Lane D output root not allowed: {path_value}")
    return path_value


def validate_safety_policy(policy: LaneDSafetyPolicy) -> LaneDSafetyPolicy:
    if not policy.offline_only:
        raise ValueError("Lane D must remain offline_only")
    forbidden_enabled = {
        "broker_calls_allowed": policy.broker_calls_allowed,
        "live_redis_writes_allowed": policy.live_redis_writes_allowed,
        "paper_live_enablement_allowed": policy.paper_live_enablement_allowed,
        "strategy_doctrine_mutation_allowed": policy.strategy_doctrine_mutation_allowed,
        "runtime_service_start_allowed": policy.runtime_service_start_allowed,
        "replay_engine_mutation_allowed": policy.replay_engine_mutation_allowed,
        "production_claim_allowed": policy.production_claim_allowed,
    }
    enabled = [name for name, value in forbidden_enabled.items() if value]
    if enabled:
        raise ValueError(f"Lane D forbidden safety flags enabled: {enabled}")
    return policy


def validate_manifest(manifest: OptimizationManifest) -> OptimizationManifest:
    validate_output_root(manifest.output_root)
    validate_optimizer_verdict(manifest.optimizer_verdict)
    validate_safety_policy(manifest.safety)
    if manifest.replay_input_root:
        validate_allowed_input_root(manifest.replay_input_root)
    if manifest.raw_input_root:
        validate_allowed_input_root(manifest.raw_input_root)
    return manifest


def validate_sweep_candidate(row: SweepCandidateRow) -> SweepCandidateRow:
    validate_strategy_family(row.strategy_family)
    validate_side(row.side)
    validate_regime(row.regime)
    if row.status not in SWEEP_STATUSES:
        raise ValueError(f"unknown sweep status: {row.status}")
    return row


def columns_for(surface_name: str) -> tuple[str, ...]:
    try:
        return COLUMN_SURFACES[surface_name]
    except KeyError as exc:
        raise ValueError(f"unknown Lane D column surface: {surface_name}") from exc


def row_to_dict(row: Any) -> dict[str, Any]:
    if is_dataclass(row):
        return asdict(row)
    if isinstance(row, Mapping):
        return dict(row)
    raise TypeError(f"unsupported row type: {type(row)!r}")


def rows_to_dicts(rows: Sequence[Any]) -> list[dict[str, Any]]:
    return [row_to_dict(row) for row in rows]


def contract_summary() -> dict[str, Any]:
    return {
        "lane": LANE_D_NAME,
        "contract_version": REPLAY_OPTIMIZATION_CONTRACT_VERSION,
        "package_name": REPLAY_OPTIMIZATION_PACKAGE_NAME,
        "config_dir": CONFIG_DIRNAME,
        "output_root": OUTPUT_ROOT,
        "allowed_input_roots": ALLOWED_INPUT_ROOTS,
        "required_artifacts": REQUIRED_OPTIMIZATION_ARTIFACTS,
        "optional_artifacts": OPTIONAL_OPTIMIZATION_ARTIFACTS,
        "strategy_families": STRATEGY_FAMILIES,
        "sides": SIDES,
        "regimes": REGIMES,
        "optimizer_verdicts": OPTIMIZER_VERDICTS,
        "column_surfaces": tuple(COLUMN_SURFACES),
        "safety": row_to_dict(LaneDSafetyPolicy()),
        "accepted_for": "CONTRACT_ONLY",
        "replay_execution_performed": False,
        "ml_training_performed": False,
        "broker_calls_allowed": False,
        "live_redis_writes_allowed": False,
        "paper_live_approved": False,
        "production_claim_allowed": False,
    }


__all__ = (
    "LANE_D_NAME",
    "REPLAY_OPTIMIZATION_CONTRACT_VERSION",
    "REPLAY_OPTIMIZATION_PACKAGE_NAME",
    "CONFIG_DIRNAME",
    "OUTPUT_ROOT",
    "EXPERIMENTS_DIRNAME",
    "LEADERBOARDS_DIRNAME",
    "ML_DATASETS_DIRNAME",
    "MODELS_DIRNAME",
    "REPORTS_DIRNAME",
    "OPTIMIZATION_POLICY_FILE",
    "SWEEP_SPACE_CONTRACT_FILE",
    "ML_EXPORT_CONTRACT_FILE",
    "ARTIFACT_OPTIMIZATION_MANIFEST",
    "ARTIFACT_SWEEP_SPACE",
    "ARTIFACT_CANDIDATE_MATRIX",
    "ARTIFACT_REPLAY_INPUT_INDEX",
    "ARTIFACT_RAW_FEATURE_INDEX",
    "ARTIFACT_RESULT_SUMMARY",
    "ARTIFACT_LEADERBOARD",
    "ARTIFACT_ML_DATASET_SCHEMA",
    "ARTIFACT_ML_TRAINING_MANIFEST",
    "ARTIFACT_OPTIMIZER_VERDICT",
    "REQUIRED_OPTIMIZATION_ARTIFACTS",
    "OPTIONAL_OPTIMIZATION_ARTIFACTS",
    "ALLOWED_INPUT_ROOTS",
    "FORBIDDEN_OWNERSHIP",
    "STRATEGY_FAMILIES",
    "SIDES",
    "REGIMES",
    "SWEEP_STATUSES",
    "OPTIMIZER_VERDICTS",
    "OPTIMIZATION_RUN_COLUMNS",
    "SWEEP_CANDIDATE_COLUMNS",
    "REPLAY_RESULT_REF_COLUMNS",
    "RAW_FEATURE_REF_COLUMNS",
    "LEADERBOARD_COLUMNS",
    "ML_DATASET_COLUMNS",
    "OPTIMIZER_VERDICT_COLUMNS",
    "COLUMN_SURFACES",
    "LaneDSafetyPolicy",
    "OptimizationManifest",
    "SweepCandidateRow",
    "ReplayResultRefRow",
    "RawFeatureRefRow",
    "LeaderboardRow",
    "MLDatasetRow",
    "OptimizerVerdictRow",
    "validate_optimizer_verdict",
    "validate_strategy_family",
    "validate_side",
    "validate_regime",
    "validate_allowed_input_root",
    "validate_output_root",
    "validate_safety_policy",
    "validate_manifest",
    "validate_sweep_candidate",
    "columns_for",
    "row_to_dict",
    "rows_to_dicts",
    "contract_summary",
)
