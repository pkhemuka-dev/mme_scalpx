"""Lane D D2 profile-generator contract surfaces.

This module converts proposed sweep candidates into research-only profile
documents. It writes only Lane D optimization artifacts and never executes
replay, trains ML, calls brokers, writes live Redis, or mutates doctrine.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Sequence

from .contracts import OUTPUT_ROOT, SweepCandidateRow, row_to_dict
from .sweep_space import (
    SweepSpaceSpec,
    candidate_rows_to_dicts,
    default_sweep_space,
    generate_sweep_candidates,
    sweep_space_to_dict,
)

PROFILE_GENERATOR_CONTRACT_VERSION = "replay_optimization_d2_profile_generator_contract_v1"
PROFILE_ACCEPTED_FOR = "CONTRACT_ONLY_PROFILE_GENERATION"


@dataclass(frozen=True, slots=True)
class GeneratedProfileCatalog:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    profile_count: int
    output_root: str
    catalog_path: str
    replay_execution_performed: bool = False
    ml_training_performed: bool = False
    broker_calls_executed: bool = False
    live_redis_writes_executed: bool = False
    paper_or_live_enabled: bool = False


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def candidate_to_profile(candidate: SweepCandidateRow) -> dict[str, Any]:
    profile: dict[str, Any] = {
        "schema_name": "MME-ScalpX Replay Optimization Candidate Profile",
        "contract_version": PROFILE_GENERATOR_CONTRACT_VERSION,
        "accepted_for": PROFILE_ACCEPTED_FOR,
        "optimization_id": candidate.optimization_id,
        "candidate_id": candidate.candidate_id,
        "strategy_family": candidate.strategy_family,
        "side": candidate.side,
        "regime": candidate.regime,
        "status": candidate.status,
        "research_only": True,
        "overrides": {
            "entry_filters": {},
            "exit_controls": {},
            "raw_filters": {},
            "risk_controls_research_only": {},
        },
        "safety": {
            "replay_execution_performed": False,
            "ml_training_performed": False,
            "broker_calls_allowed": False,
            "live_redis_writes_allowed": False,
            "paper_live_enablement_allowed": False,
            "strategy_doctrine_mutation_allowed": False,
            "runtime_service_start_allowed": False,
            "production_claim_allowed": False,
        },
        "source_row": row_to_dict(candidate),
    }

    if candidate.parameter_group == "exit_controls":
        if candidate.target_points is not None:
            profile["overrides"]["exit_controls"]["target_points"] = candidate.target_points
        if candidate.hard_stop_points is not None:
            profile["overrides"]["exit_controls"]["hard_stop_points"] = candidate.hard_stop_points
        if candidate.profit_stall_points is not None:
            profile["overrides"]["exit_controls"]["profit_stall_points"] = candidate.profit_stall_points
        if candidate.time_stall_seconds is not None:
            profile["overrides"]["exit_controls"]["time_stall_seconds"] = candidate.time_stall_seconds
        profile["overrides"]["exit_controls"][candidate.parameter_name] = candidate.candidate_value
    elif candidate.parameter_group == "raw_filters":
        profile["overrides"]["raw_filters"][candidate.parameter_name] = {
            "feature_family": candidate.raw_filter_family,
            "threshold": candidate.raw_filter_threshold or candidate.candidate_value,
        }
    else:
        profile["overrides"].setdefault(candidate.parameter_group, {})
        profile["overrides"][candidate.parameter_group][candidate.parameter_name] = candidate.candidate_value

    return profile


def write_json(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def write_profile_catalog(
    optimization_id: str,
    candidates: Sequence[SweepCandidateRow],
    output_dir: str | Path,
    *,
    max_profiles: int = 100,
) -> GeneratedProfileCatalog:
    if max_profiles <= 0:
        raise ValueError("max_profiles must be positive")
    out = Path(output_dir)
    normalized = out.as_posix().rstrip("/")
    allowed_root = OUTPUT_ROOT.strip("/")
    normalized_guard = "/" + normalized.strip("/") + "/"
    allowed_guard = "/" + allowed_root + "/"
    if not (
        normalized == OUTPUT_ROOT
        or normalized.startswith(OUTPUT_ROOT + "/")
        or normalized.startswith("run/replay_optimization/")
        or allowed_guard in normalized_guard
    ):
        raise ValueError(f"profile output must stay under {OUTPUT_ROOT}: {output_dir}")

    selected = tuple(candidates[:max_profiles])
    profiles = [candidate_to_profile(row) for row in selected]
    catalog = {
        "schema_name": "MME-ScalpX Replay Optimization Profile Catalog",
        "contract_version": PROFILE_GENERATOR_CONTRACT_VERSION,
        "accepted_for": PROFILE_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "profile_count": len(profiles),
        "profiles": profiles,
        "safety": {
            "replay_execution_performed": False,
            "ml_training_performed": False,
            "broker_calls_executed": False,
            "live_redis_writes_executed": False,
            "paper_or_live_enabled": False,
        },
    }
    catalog_path = write_json(out / "profile_catalog.json", catalog)
    return GeneratedProfileCatalog(
        optimization_id=optimization_id,
        created_at=catalog["created_at"],
        contract_version=PROFILE_GENERATOR_CONTRACT_VERSION,
        accepted_for=PROFILE_ACCEPTED_FOR,
        profile_count=len(profiles),
        output_root=out.as_posix(),
        catalog_path=catalog_path.as_posix(),
    )


def build_d2_contract_artifacts(
    optimization_id: str,
    output_dir: str | Path,
    *,
    space: SweepSpaceSpec | None = None,
    max_candidates: int = 10000,
    max_profiles: int = 100,
) -> dict[str, Any]:
    active_space = space or default_sweep_space()
    candidates = generate_sweep_candidates(
        optimization_id,
        active_space,
        max_candidates=max_candidates,
    )
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    sweep_path = write_json(out / "01_sweep_space.json", sweep_space_to_dict(active_space))
    matrix_path = write_json(out / "02_candidate_matrix.json", candidate_rows_to_dicts(candidates))
    catalog = write_profile_catalog(
        optimization_id,
        candidates,
        out,
        max_profiles=max_profiles,
    )

    return {
        "optimization_id": optimization_id,
        "contract_version": PROFILE_GENERATOR_CONTRACT_VERSION,
        "accepted_for": PROFILE_ACCEPTED_FOR,
        "sweep_space_path": sweep_path.as_posix(),
        "candidate_matrix_path": matrix_path.as_posix(),
        "profile_catalog_path": catalog.catalog_path,
        "candidate_count": len(candidates),
        "profile_count": catalog.profile_count,
        "replay_execution_performed": False,
        "ml_training_performed": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "paper_or_live_enabled": False,
    }


__all__ = (
    "PROFILE_GENERATOR_CONTRACT_VERSION",
    "PROFILE_ACCEPTED_FOR",
    "GeneratedProfileCatalog",
    "candidate_to_profile",
    "write_json",
    "write_profile_catalog",
    "build_d2_contract_artifacts",
)
