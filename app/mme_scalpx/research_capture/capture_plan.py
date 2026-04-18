"""
app.mme_scalpx.research_capture.capture_plan

Freeze-grade capture-plan composition for the research-capture chapter.

Ownership
---------
This module OWNS:
- composing deterministic raw-capture output targets from manifest materialization
- classifying capture outputs by requirement mode and metadata labels
- exposing canonical archive/audit output paths for downstream capture writers

This module DOES NOT own:
- runtime business logic
- raw/live capture execution
- parquet writing
- broker/source I/O
- production doctrine mutation
- canonical archive mutation

Design laws
-----------
- raw capture first
- light live-derived second
- heavy offline-derived later
- this module plans capture outputs only; it does not write them
- thin, deterministic, auditable
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from app.mme_scalpx.research_capture.config_loader import (
    ConfigRegistry,
    DEFAULT_CONFIG_REGISTRY_PATH,
    load_config_registry,
    load_registered_json_contract,
)
from app.mme_scalpx.research_capture.manifest_materializer import (
    ManifestMaterializationResult,
    build_and_materialize_manifest_seed,
)


class CapturePlanError(RuntimeError):
    """Base error for capture-plan composition."""


@dataclass(frozen=True, slots=True)
class CaptureOutputPlan:
    """One planned capture output surface."""

    name: str
    path: str
    requirement: str
    usage_class: str
    compute_stage: str
    storage_target: str

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "path": self.path,
            "requirement": self.requirement,
            "usage_class": self.usage_class,
            "compute_stage": self.compute_stage,
            "storage_target": self.storage_target,
        }


@dataclass(frozen=True, slots=True)
class CapturePlan:
    """Deterministic capture plan derived from manifest materialization."""

    entrypoint: str
    lane: str
    source: str
    run_id: str
    required_outputs: tuple[CaptureOutputPlan, ...]
    optional_outputs: tuple[CaptureOutputPlan, ...]
    manifest_materialization_result: ManifestMaterializationResult

    def to_dict(self) -> dict[str, Any]:
        return {
            "entrypoint": self.entrypoint,
            "lane": self.lane,
            "source": self.source,
            "run_id": self.run_id,
            "required_outputs": [item.to_dict() for item in self.required_outputs],
            "optional_outputs": [item.to_dict() for item in self.optional_outputs],
            "manifest_materialization_result": self.manifest_materialization_result.to_dict(),
        }


def _require_nonempty_str(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CapturePlanError(f"{name} must be a non-empty string")
    return value.strip()


def _capture_output_path(result: ManifestMaterializationResult, filename: str) -> str:
    run_root = Path(result.manifest_seed.metadata["run_root"]).resolve()
    return str((run_root / filename).resolve())


def _build_output(
    *,
    result: ManifestMaterializationResult,
    filename: str,
    requirement: str,
    usage_class: str,
    compute_stage: str,
    storage_target: str,
) -> CaptureOutputPlan:
    return CaptureOutputPlan(
        name=filename,
        path=_capture_output_path(result, filename),
        requirement=requirement,
        usage_class=usage_class,
        compute_stage=compute_stage,
        storage_target=storage_target,
    )


def build_capture_plan(
    manifest_materialization_result: ManifestMaterializationResult,
    *,
    registry: ConfigRegistry | None = None,
    config_registry_path: Path | str = DEFAULT_CONFIG_REGISTRY_PATH,
    project_root: Path | None = None,
) -> CapturePlan:
    """
    Build a deterministic capture plan from manifest materialization.

    Requirement modes:
    - minimum_one_of: at least one of the listed raw capture parquet outputs must exist
    - optional: audit/adjacent outputs that may be written by downstream runtime lanes
    """
    reg = registry if registry is not None else load_config_registry(
        config_registry_path,
        project_root=project_root,
    )

    runtime_policy = load_registered_json_contract("runtime_policy", registry=reg, project_root=project_root)
    backfill_policy = load_registered_json_contract("backfill_policy", registry=reg, project_root=project_root)

    entrypoint = manifest_materialization_result.entrypoint
    lane = manifest_materialization_result.lane

    required_outputs: list[CaptureOutputPlan] = []
    optional_outputs: list[CaptureOutputPlan] = []

    if entrypoint == "run":
        minimum_one_of = runtime_policy["runtime_outputs"]["required_archive_minimum_one_of"]
        recommended = runtime_policy["runtime_outputs"]["recommended_for_run"]

        for filename in minimum_one_of:
            required_outputs.append(
                _build_output(
                    result=manifest_materialization_result,
                    filename=_require_nonempty_str(filename, "runtime minimum_one_of filename"),
                    requirement="minimum_one_of",
                    usage_class="research_only",
                    compute_stage="raw_capture",
                    storage_target="archive_parquet",
                )
            )

        for filename in recommended:
            optional_outputs.append(
                _build_output(
                    result=manifest_materialization_result,
                    filename=_require_nonempty_str(filename, "runtime recommended filename"),
                    requirement="optional",
                    usage_class="audit_only",
                    compute_stage="raw_capture",
                    storage_target="archive_parquet",
                )
            )

    elif entrypoint == "backfill":
        minimum_one_of = backfill_policy["output_files"]["minimum_archive_one_of"]
        recommended = backfill_policy["output_files"]["recommended"]

        for filename in minimum_one_of:
            required_outputs.append(
                _build_output(
                    result=manifest_materialization_result,
                    filename=_require_nonempty_str(filename, "backfill minimum_one_of filename"),
                    requirement="minimum_one_of",
                    usage_class="research_only",
                    compute_stage="raw_capture",
                    storage_target="archive_parquet",
                )
            )

        for filename in recommended:
            optional_outputs.append(
                _build_output(
                    result=manifest_materialization_result,
                    filename=_require_nonempty_str(filename, "backfill recommended filename"),
                    requirement="optional",
                    usage_class="audit_only",
                    compute_stage="raw_capture",
                    storage_target="archive_parquet",
                )
            )

    elif entrypoint in {"verify", "research"}:
        required_outputs = []
        optional_outputs = []

    else:
        raise CapturePlanError(f"unknown entrypoint for capture planning: {entrypoint}")

    required_names = [item.name for item in required_outputs]
    optional_names = [item.name for item in optional_outputs]
    if len(required_names) != len(set(required_names)):
        raise CapturePlanError("duplicate required capture output names detected")
    if len(optional_names) != len(set(optional_names)):
        raise CapturePlanError("duplicate optional capture output names detected")
    if set(required_names).intersection(optional_names):
        raise CapturePlanError("required/optional capture outputs overlap")

    return CapturePlan(
        entrypoint=entrypoint,
        lane=lane,
        source=manifest_materialization_result.source,
        run_id=manifest_materialization_result.run_id,
        required_outputs=tuple(required_outputs),
        optional_outputs=tuple(optional_outputs),
        manifest_materialization_result=manifest_materialization_result,
    )


def build_capture_plan_from_operator_inputs(
    entrypoint: str,
    *,
    run_id: str,
    session_date: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    session_dates: Sequence[str] | None = None,
    instrument_scope: str | None = None,
    research_profile: str | None = None,
    feature_families: Sequence[str] | None = None,
    notes: str | None = None,
    lane_override: str | None = None,
    source_override: str | None = None,
    export_format_overrides: Mapping[str, str] | None = None,
    registry: ConfigRegistry | None = None,
    config_registry_path: Path | str = DEFAULT_CONFIG_REGISTRY_PATH,
    project_root: Path | None = None,
) -> CapturePlan:
    """
    Build manifest materialization first, then derive the deterministic capture plan.
    """
    reg = registry if registry is not None else load_config_registry(
        config_registry_path,
        project_root=project_root,
    )

    manifest_materialization_result = build_and_materialize_manifest_seed(
        entrypoint,
        run_id=run_id,
        session_date=session_date,
        start_date=start_date,
        end_date=end_date,
        session_dates=session_dates,
        instrument_scope=instrument_scope,
        research_profile=research_profile,
        feature_families=feature_families,
        notes=notes,
        lane_override=lane_override,
        source_override=source_override,
        export_format_overrides=export_format_overrides,
        registry=reg,
        project_root=project_root,
    )
    return build_capture_plan(
        manifest_materialization_result,
        registry=reg,
        project_root=project_root,
    )


__all__ = [
    "CapturePlanError",
    "CaptureOutputPlan",
    "CapturePlan",
    "build_capture_plan",
    "build_capture_plan_from_operator_inputs",
]
