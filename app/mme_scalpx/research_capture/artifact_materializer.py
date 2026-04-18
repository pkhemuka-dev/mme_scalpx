"""
app.mme_scalpx.research_capture.artifact_materializer

Freeze-grade artifact materialization for the research-capture chapter.

Ownership
---------
This module OWNS:
- creating canonical artifact directories from the artifact plan
- writing the effective registry snapshot to its frozen path
- writing a thin materialization report for auditability
- returning a deterministic materialization result for entrypoints

This module DOES NOT own:
- runtime business logic
- archive writing beyond the registry/materialization audit surfaces
- broker/source I/O
- production doctrine mutation
- canonical archive mutation

Design laws
-----------
- config_loader = registry truth
- config_bootstrap = default/override truth
- config_context = path/output context truth
- artifact_plan = artifact inventory/path truth
- artifact_materializer = directory + audit-surface materialization only
- thin, deterministic, auditable
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from app.mme_scalpx.research_capture.artifact_plan import (
    ArtifactPlan,
    build_artifact_plan,
)
from app.mme_scalpx.research_capture.config_loader import (
    ConfigRegistry,
    DEFAULT_CONFIG_REGISTRY_PATH,
    load_config_registry,
)


class ArtifactMaterializerError(RuntimeError):
    """Base error for artifact materialization."""


@dataclass(frozen=True, slots=True)
class MaterializedFile:
    """A file written by artifact materialization."""

    name: str
    path: str

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "path": self.path,
        }


@dataclass(frozen=True, slots=True)
class ArtifactMaterializationResult:
    """Deterministic result of artifact materialization."""

    entrypoint: str
    lane: str
    source: str
    run_id: str
    run_root: str
    report_root: str
    export_root: str
    materialized_directories: tuple[str, ...]
    materialized_files: tuple[MaterializedFile, ...]
    artifact_plan: ArtifactPlan

    def to_dict(self) -> dict[str, Any]:
        return {
            "entrypoint": self.entrypoint,
            "lane": self.lane,
            "source": self.source,
            "run_id": self.run_id,
            "run_root": self.run_root,
            "report_root": self.report_root,
            "export_root": self.export_root,
            "materialized_directories": list(self.materialized_directories),
            "materialized_files": [item.to_dict() for item in self.materialized_files],
            "artifact_plan": self.artifact_plan.to_dict(),
        }


def _resolve_project_root(project_root: Path | None = None) -> Path:
    root = project_root if project_root is not None else Path.cwd()
    return root.resolve()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _materialization_report_path(artifact_plan: ArtifactPlan) -> Path:
    return (Path(artifact_plan.report_root) / "artifact_materialization_report.json").resolve()


def materialize_artifact_plan(
    artifact_plan: ArtifactPlan,
) -> ArtifactMaterializationResult:
    """
    Materialize directories and audit surfaces for a frozen artifact plan.
    """
    run_root = Path(artifact_plan.run_root)
    report_root = Path(artifact_plan.report_root)
    export_root = Path(artifact_plan.export_root)

    for directory in (run_root, report_root, export_root):
        directory.mkdir(parents=True, exist_ok=True)

    effective_registry_snapshot_path = Path(artifact_plan.effective_registry_snapshot_path)
    _write_json(
        effective_registry_snapshot_path,
        artifact_plan.config_context.bootstrap_package.effective_registry_snapshot.to_dict(),
    )

    materialization_report = {
        "materialization_ok": True,
        "entrypoint": artifact_plan.entrypoint,
        "lane": artifact_plan.lane,
        "source": artifact_plan.source,
        "run_id": artifact_plan.run_id,
        "run_root": artifact_plan.run_root,
        "report_root": artifact_plan.report_root,
        "export_root": artifact_plan.export_root,
        "effective_registry_snapshot_path": artifact_plan.effective_registry_snapshot_path,
        "required_artifact_count": len(artifact_plan.required_artifacts),
        "optional_artifact_count": len(artifact_plan.optional_artifacts),
    }
    materialization_report_path = _materialization_report_path(artifact_plan)
    _write_json(materialization_report_path, materialization_report)

    result = ArtifactMaterializationResult(
        entrypoint=artifact_plan.entrypoint,
        lane=artifact_plan.lane,
        source=artifact_plan.source,
        run_id=artifact_plan.run_id,
        run_root=artifact_plan.run_root,
        report_root=artifact_plan.report_root,
        export_root=artifact_plan.export_root,
        materialized_directories=(
            str(run_root),
            str(report_root),
            str(export_root),
        ),
        materialized_files=(
            MaterializedFile(
                name="effective_registry_snapshot.json",
                path=str(effective_registry_snapshot_path),
            ),
            MaterializedFile(
                name="artifact_materialization_report.json",
                path=str(materialization_report_path),
            ),
        ),
        artifact_plan=artifact_plan,
    )
    return result


def build_and_materialize_artifact_plan(
    entrypoint: str,
    *,
    run_id: str,
    lane_override: str | None = None,
    source_override: str | None = None,
    export_format_overrides: Mapping[str, str] | None = None,
    registry: ConfigRegistry | None = None,
    config_registry_path: Path | str = DEFAULT_CONFIG_REGISTRY_PATH,
    project_root: Path | None = None,
) -> ArtifactMaterializationResult:
    """
    Compose the frozen artifact plan, then materialize its directory/audit surfaces.
    """
    root = _resolve_project_root(project_root)
    reg = registry if registry is not None else load_config_registry(
        config_registry_path,
        project_root=root,
    )

    artifact_plan = build_artifact_plan(
        entrypoint,
        run_id=run_id,
        lane_override=lane_override,
        source_override=source_override,
        export_format_overrides=export_format_overrides,
        registry=reg,
        project_root=root,
    )
    return materialize_artifact_plan(artifact_plan)


__all__ = [
    "ArtifactMaterializerError",
    "MaterializedFile",
    "ArtifactMaterializationResult",
    "materialize_artifact_plan",
    "build_and_materialize_artifact_plan",
]
