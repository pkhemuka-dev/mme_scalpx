"""
app.mme_scalpx.research_capture.artifact_plan

Freeze-grade artifact-plan composition for the research-capture chapter.

Ownership
---------
This module OWNS:
- composing canonical artifact names and paths from the config context
- separating required vs optional artifact surfaces
- resolving deterministic report/export/runtime artifact destinations
- exposing a thin auditable artifact plan for downstream entrypoints

This module DOES NOT own:
- runtime business logic
- archive writing
- report generation
- broker/source I/O
- mutation of production doctrine or canonical archive

Design laws
-----------
- config_loader = canonical registry resolver
- config_bootstrap = canonical default/override resolver
- config_context = canonical path/output composition layer
- artifact_plan = canonical artifact inventory/path layer
- deterministic paths only
- no file writes here; this module only builds plans
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from app.mme_scalpx.research_capture.config_context import (
    ConfigContext,
    build_config_context,
)
from app.mme_scalpx.research_capture.config_loader import (
    ConfigRegistry,
    DEFAULT_CONFIG_REGISTRY_PATH,
    load_config_registry,
    load_registered_json_contract,
)


class ArtifactPlanError(RuntimeError):
    """Base error for artifact-plan composition."""


@dataclass(frozen=True, slots=True)
class ArtifactFilePlan:
    """One resolved artifact file in the canonical artifact plan."""

    name: str
    path: str
    category: str
    required: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "path": self.path,
            "category": self.category,
            "required": self.required,
        }


@dataclass(frozen=True, slots=True)
class ArtifactPlan:
    """Deterministic artifact plan composed from frozen config context and policies."""

    entrypoint: str
    profile_group: str
    lane: str
    source: str
    run_id: str
    run_root: str
    report_root: str
    export_root: str
    effective_registry_snapshot_path: str
    required_artifacts: tuple[ArtifactFilePlan, ...]
    optional_artifacts: tuple[ArtifactFilePlan, ...]
    config_context: ConfigContext

    def to_dict(self) -> dict[str, Any]:
        return {
            "entrypoint": self.entrypoint,
            "profile_group": self.profile_group,
            "lane": self.lane,
            "source": self.source,
            "run_id": self.run_id,
            "run_root": self.run_root,
            "report_root": self.report_root,
            "export_root": self.export_root,
            "effective_registry_snapshot_path": self.effective_registry_snapshot_path,
            "required_artifacts": [item.to_dict() for item in self.required_artifacts],
            "optional_artifacts": [item.to_dict() for item in self.optional_artifacts],
            "config_context": self.config_context.to_dict(),
        }


def _require_nonempty_str(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ArtifactPlanError(f"{name} must be a non-empty string")
    return value


def _resolve_project_root(project_root: Path | None = None) -> Path:
    root = project_root if project_root is not None else Path.cwd()
    return root.resolve()


def _resolve_artifact_path(
    *,
    entrypoint: str,
    name: str,
    run_root: Path,
    report_root: Path,
    export_root: Path,
) -> Path:
    normalized_name = _require_nonempty_str(name, "artifact_name")
    lower = normalized_name.lower()

    if lower.endswith(".json"):
        return (report_root / normalized_name).resolve()

    if entrypoint == "research":
        return (export_root / normalized_name).resolve()

    return (run_root / normalized_name).resolve()


def _build_file_plans(
    *,
    entrypoint: str,
    names: list[str],
    run_root: Path,
    report_root: Path,
    export_root: Path,
    category: str,
    required: bool,
) -> tuple[ArtifactFilePlan, ...]:
    seen: set[str] = set()
    plans: list[ArtifactFilePlan] = []

    for raw_name in names:
        name = _require_nonempty_str(raw_name, "artifact_name")
        if name in seen:
            raise ArtifactPlanError(f"duplicate artifact name in plan: {name}")
        seen.add(name)
        resolved = _resolve_artifact_path(
            entrypoint=entrypoint,
            name=name,
            run_root=run_root,
            report_root=report_root,
            export_root=export_root,
        )
        plans.append(
            ArtifactFilePlan(
                name=name,
                path=str(resolved),
                category=category,
                required=required,
            )
        )

    return tuple(plans)


def _required_names_for_entrypoint(
    *,
    entrypoint: str,
    runtime_policy: Mapping[str, Any],
    backfill_policy: Mapping[str, Any],
    research_policy: Mapping[str, Any],
    effective_registry_snapshot_filename: str,
) -> list[str]:
    if entrypoint == "verify":
        names = list(runtime_policy["runtime_outputs"]["required_for_verify"])
    elif entrypoint == "run":
        names = list(runtime_policy["runtime_outputs"]["required_for_run"])
    elif entrypoint == "backfill":
        names = list(backfill_policy["output_files"]["required"])
    elif entrypoint == "research":
        names = list(research_policy["required_output_files"].values())
    else:
        raise ArtifactPlanError(f"unknown entrypoint for required artifact names: {entrypoint}")

    names.append(effective_registry_snapshot_filename)
    return names


def _optional_names_for_entrypoint(
    *,
    entrypoint: str,
    runtime_policy: Mapping[str, Any],
    backfill_policy: Mapping[str, Any],
    research_policy: Mapping[str, Any],
) -> list[str]:
    if entrypoint == "verify":
        return []
    if entrypoint == "run":
        return list(runtime_policy["runtime_outputs"]["recommended_for_run"])
    if entrypoint == "backfill":
        return list(backfill_policy["output_files"]["recommended"])
    if entrypoint == "research":
        return list(research_policy["optional_output_files"].values())
    raise ArtifactPlanError(f"unknown entrypoint for optional artifact names: {entrypoint}")


def build_artifact_plan(
    entrypoint: str,
    *,
    run_id: str,
    lane_override: str | None = None,
    source_override: str | None = None,
    export_format_overrides: Mapping[str, str] | None = None,
    registry: ConfigRegistry | None = None,
    config_registry_path: Path | str = DEFAULT_CONFIG_REGISTRY_PATH,
    project_root: Path | None = None,
) -> ArtifactPlan:
    """
    Compose a canonical artifact plan from the frozen config context and policies.
    """
    root = _resolve_project_root(project_root)
    reg = registry if registry is not None else load_config_registry(
        config_registry_path,
        project_root=root,
    )

    context = build_config_context(
        entrypoint,
        run_id=run_id,
        lane_override=lane_override,
        source_override=source_override,
        export_format_overrides=export_format_overrides,
        registry=reg,
        project_root=root,
    )

    runtime_policy = load_registered_json_contract("runtime_policy", registry=reg, project_root=root)
    backfill_policy = load_registered_json_contract("backfill_policy", registry=reg, project_root=root)
    research_policy = load_registered_json_contract("research_policy", registry=reg, project_root=root)

    effective_registry_snapshot_filename = _require_nonempty_str(
        reg.output_contract["effective_registry_snapshot_filename"],
        "effective_registry_snapshot_filename",
    )

    required_names = _required_names_for_entrypoint(
        entrypoint=context.entrypoint,
        runtime_policy=runtime_policy,
        backfill_policy=backfill_policy,
        research_policy=research_policy,
        effective_registry_snapshot_filename=effective_registry_snapshot_filename,
    )
    optional_names = _optional_names_for_entrypoint(
        entrypoint=context.entrypoint,
        runtime_policy=runtime_policy,
        backfill_policy=backfill_policy,
        research_policy=research_policy,
    )

    run_root = Path(context.run_root)
    report_root = Path(context.report_root)
    export_root = Path(context.export_root)

    required_artifacts = _build_file_plans(
        entrypoint=context.entrypoint,
        names=required_names,
        run_root=run_root,
        report_root=report_root,
        export_root=export_root,
        category="required",
        required=True,
    )
    optional_artifacts = _build_file_plans(
        entrypoint=context.entrypoint,
        names=optional_names,
        run_root=run_root,
        report_root=report_root,
        export_root=export_root,
        category="optional",
        required=False,
    )

    required_names_set = {item.name for item in required_artifacts}
    optional_names_set = {item.name for item in optional_artifacts}
    overlap = sorted(required_names_set.intersection(optional_names_set))
    if overlap:
        raise ArtifactPlanError(f"required/optional artifact overlap detected: {overlap}")

    return ArtifactPlan(
        entrypoint=context.entrypoint,
        profile_group=context.profile_group,
        lane=context.lane,
        source=context.source,
        run_id=context.run_id,
        run_root=context.run_root,
        report_root=context.report_root,
        export_root=context.export_root,
        effective_registry_snapshot_path=context.effective_registry_snapshot_path,
        required_artifacts=required_artifacts,
        optional_artifacts=optional_artifacts,
        config_context=context,
    )


__all__ = [
    "ArtifactPlanError",
    "ArtifactFilePlan",
    "ArtifactPlan",
    "build_artifact_plan",
]

# =============================================================================
# Batch 17 freeze hardening: artifact path containment
# =============================================================================
_BATCH17_ARTIFACT_PLAN_GUARD_VERSION = "1"

from app.mme_scalpx.research_capture.utils import ensure_path_within_any_root as _batch17_ensure_path_within_any_root

_BATCH17_ORIGINAL_RESOLVE_ARTIFACT_PATH = _resolve_artifact_path

def _resolve_artifact_path(
    *,
    entrypoint: str,
    name: str,
    run_root: Path,
    report_root: Path,
    export_root: Path,
) -> Path:
    resolved = _BATCH17_ORIGINAL_RESOLVE_ARTIFACT_PATH(
        entrypoint=entrypoint,
        name=name,
        run_root=run_root,
        report_root=report_root,
        export_root=export_root,
    )
    return _batch17_ensure_path_within_any_root(
        resolved,
        (run_root, report_root, export_root),
        label=f"artifact_path[{name}]",
    )
