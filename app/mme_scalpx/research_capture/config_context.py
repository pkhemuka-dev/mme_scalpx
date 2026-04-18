"""
app.mme_scalpx.research_capture.config_context

Freeze-grade config context composition for the research-capture chapter.

Ownership
---------
This module OWNS:
- composing deterministic runtime context from the bootstrap package
- resolving canonical run/output roots from frozen defaults
- resolving selected output file paths
- resolving effective registry snapshot path
- building a thin, auditable context payload for entrypoints

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
- deterministic paths only
- no side effects beyond returning data structures
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from app.mme_scalpx.research_capture.config_bootstrap import (
    BootstrapPackage,
    build_bootstrap_package,
)
from app.mme_scalpx.research_capture.config_loader import (
    ConfigRegistry,
    DEFAULT_CONFIG_REGISTRY_PATH,
    load_config_registry,
)


class ConfigContextError(RuntimeError):
    """Base error for config-context composition."""


@dataclass(frozen=True, slots=True)
class OutputFileSelection:
    """Resolved output selection for one named output file."""

    name: str
    path: str

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "path": self.path,
        }


@dataclass(frozen=True, slots=True)
class ConfigContext:
    """Deterministic, auditable context composed from the bootstrap package."""

    entrypoint: str
    profile_group: str
    lane: str
    source: str
    run_id: str
    run_root: str
    report_root: str
    export_root: str
    effective_registry_snapshot_path: str
    selected_outputs: tuple[OutputFileSelection, ...]
    selected_export_formats: dict[str, str]
    bootstrap_package: BootstrapPackage

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
            "selected_outputs": [item.to_dict() for item in self.selected_outputs],
            "selected_export_formats": dict(self.selected_export_formats),
            "bootstrap_package": self.bootstrap_package.to_dict(),
        }


def _require_nonempty_str(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigContextError(f"{name} must be a non-empty string")
    return value


def _resolve_project_root(project_root: Path | None = None) -> Path:
    root = project_root if project_root is not None else Path.cwd()
    return root.resolve()


def _resolve_run_root_paths(
    *,
    registry: ConfigRegistry,
    bootstrap_package: BootstrapPackage,
    project_root: Path,
    run_id: str,
) -> tuple[Path, Path, Path]:
    defaults = bootstrap_package.json_contracts["operator_defaults"]
    default_paths = defaults.get("default_paths", {})
    if not isinstance(default_paths, dict):
        raise ConfigContextError("operator_defaults.default_paths must be a mapping")

    run_root_rel = _require_nonempty_str(default_paths.get("run_root", ""), "default_paths.run_root")
    report_root_rel = _require_nonempty_str(default_paths.get("report_root", ""), "default_paths.report_root")
    export_root_rel = _require_nonempty_str(default_paths.get("export_root", ""), "default_paths.export_root")

    run_root = (project_root / run_root_rel / run_id).resolve()
    report_root = (project_root / report_root_rel / run_id).resolve()
    export_root = (project_root / export_root_rel / run_id).resolve()

    return run_root, report_root, export_root


def _resolve_selected_output_files(
    *,
    bootstrap_package: BootstrapPackage,
    run_root: Path,
    report_root: Path,
) -> tuple[OutputFileSelection, ...]:
    output_selections: list[OutputFileSelection] = []

    for output_name in bootstrap_package.selected_outputs:
        if output_name.endswith(".json"):
            resolved = report_root / output_name
        else:
            resolved = run_root / output_name
        output_selections.append(
            OutputFileSelection(
                name=output_name,
                path=str(resolved),
            )
        )

    return tuple(output_selections)


def _resolve_effective_registry_snapshot_path(
    *,
    registry: ConfigRegistry,
    report_root: Path,
) -> Path:
    output_contract = registry.output_contract
    filename = _require_nonempty_str(
        output_contract.get("effective_registry_snapshot_filename", ""),
        "output_contract.effective_registry_snapshot_filename",
    )
    return (report_root / filename).resolve()


def build_config_context(
    entrypoint: str,
    *,
    run_id: str,
    lane_override: str | None = None,
    source_override: str | None = None,
    export_format_overrides: Mapping[str, str] | None = None,
    registry: ConfigRegistry | None = None,
    config_registry_path: Path | str = DEFAULT_CONFIG_REGISTRY_PATH,
    project_root: Path | None = None,
) -> ConfigContext:
    """
    Compose a deterministic config context for one entrypoint/run_id pair.
    """
    normalized_run_id = _require_nonempty_str(run_id, "run_id")
    root = _resolve_project_root(project_root)

    reg = registry if registry is not None else load_config_registry(
        config_registry_path,
        project_root=root,
    )

    bootstrap_package = build_bootstrap_package(
        entrypoint,
        lane_override=lane_override,
        source_override=source_override,
        export_format_overrides=export_format_overrides,
        registry=reg,
        project_root=root,
    )

    run_root, report_root, export_root = _resolve_run_root_paths(
        registry=reg,
        bootstrap_package=bootstrap_package,
        project_root=root,
        run_id=normalized_run_id,
    )

    selected_outputs = _resolve_selected_output_files(
        bootstrap_package=bootstrap_package,
        run_root=run_root,
        report_root=report_root,
    )

    effective_registry_snapshot_path = _resolve_effective_registry_snapshot_path(
        registry=reg,
        report_root=report_root,
    )

    return ConfigContext(
        entrypoint=bootstrap_package.entrypoint,
        profile_group=bootstrap_package.profile_group,
        lane=bootstrap_package.selected_lane,
        source=bootstrap_package.selected_source,
        run_id=normalized_run_id,
        run_root=str(run_root),
        report_root=str(report_root),
        export_root=str(export_root),
        effective_registry_snapshot_path=str(effective_registry_snapshot_path),
        selected_outputs=selected_outputs,
        selected_export_formats=dict(bootstrap_package.selected_export_formats),
        bootstrap_package=bootstrap_package,
    )


__all__ = [
    "ConfigContextError",
    "OutputFileSelection",
    "ConfigContext",
    "build_config_context",
]
