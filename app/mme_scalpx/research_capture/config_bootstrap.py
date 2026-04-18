"""
app.mme_scalpx.research_capture.config_bootstrap

Freeze-grade bootstrap helper for the research-capture config bundle.

Ownership
---------
This module OWNS:
- resolving operator defaults for a named entrypoint
- validating thin operator overrides against frozen policies
- composing a resolved bootstrap package from config_loader surfaces
- producing an auditable effective bootstrap payload for downstream entrypoints

This module DOES NOT own:
- runtime business logic
- archive writing
- report generation
- broker/source I/O
- mutation of production doctrine or canonical archive

Design laws
-----------
- config_loader remains the canonical registry resolver
- operator_defaults remain the canonical default selector
- bootstrap stays thin and deterministic
- explicit operator input may override defaults only when policy-consistent
- this module returns data; it does not execute runtime actions
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from app.mme_scalpx.research_capture.config_loader import (
    ConfigRegistry,
    DEFAULT_CONFIG_REGISTRY_PATH,
    EntrypointBundle,
    EffectiveRegistrySnapshot,
    RegistryValidationError,
    build_effective_registry_snapshot,
    load_config_registry,
    load_registered_json_contract,
    resolve_entrypoint_bundle,
)

_DEFAULT_PROFILE_GROUP_BY_ENTRYPOINT: dict[str, str] = {
    "verify": "base",
    "run": "live_capture",
    "backfill": "historical_backfill",
    "research": "offline_research",
}


class ConfigBootstrapError(RuntimeError):
    """Base error for config-bootstrap resolution."""


class InvalidLaneOverrideError(ConfigBootstrapError):
    """Raised when a lane override violates frozen policy."""


class InvalidSourceOverrideError(ConfigBootstrapError):
    """Raised when a source override violates frozen policy."""


@dataclass(frozen=True, slots=True)
class BootstrapPackage:
    """Resolved bootstrap package for one research-capture entrypoint."""

    entrypoint: str
    profile_group: str
    selected_lane: str
    selected_source: str
    selected_outputs: list[str]
    selected_export_formats: dict[str, str]
    registry_source_path: str
    registry_version: str
    entrypoint_bundle: EntrypointBundle
    effective_registry_snapshot: EffectiveRegistrySnapshot
    json_contracts: dict[str, dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "entrypoint": self.entrypoint,
            "profile_group": self.profile_group,
            "selected_lane": self.selected_lane,
            "selected_source": self.selected_source,
            "selected_outputs": list(self.selected_outputs),
            "selected_export_formats": dict(self.selected_export_formats),
            "registry_source_path": self.registry_source_path,
            "registry_version": self.registry_version,
            "entrypoint_bundle": self.entrypoint_bundle.to_dict(),
            "effective_registry_snapshot": self.effective_registry_snapshot.to_dict(),
            "json_contracts": {key: dict(value) for key, value in self.json_contracts.items()},
        }


def _normalize_override(value: str | None, name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ConfigBootstrapError(f"{name} override must be a non-empty string")
    return value


def _allowed_lanes_for_entrypoint(
    entrypoint: str,
    *,
    runtime_policy: Mapping[str, Any],
    research_policy: Mapping[str, Any],
) -> set[str]:
    if entrypoint == "verify":
        return {"verify_only"}
    if entrypoint == "run":
        return {"live_capture", "dry_run"}
    if entrypoint == "backfill":
        return {"historical_backfill"}
    if entrypoint == "research":
        lanes = research_policy.get("offline_lanes", {})
        if not isinstance(lanes, dict):
            raise RegistryValidationError("research_policy.offline_lanes must be a mapping")
        return set(lanes.keys())
    raise ConfigBootstrapError(f"unknown entrypoint for lane resolution: {entrypoint}")


def _allowed_sources_for_entrypoint_lane(
    entrypoint: str,
    lane: str,
    *,
    runtime_policy: Mapping[str, Any],
    backfill_policy: Mapping[str, Any],
    research_policy: Mapping[str, Any],
) -> set[str]:
    lane_source_matrix = runtime_policy.get("lane_source_matrix", {})
    if not isinstance(lane_source_matrix, dict):
        raise RegistryValidationError("runtime_policy.lane_source_matrix must be a mapping")

    if entrypoint == "verify":
        return set(lane_source_matrix.get("verify_only", []))

    if entrypoint == "run":
        if lane == "live_capture":
            return set(lane_source_matrix.get("live_capture", []))
        if lane == "dry_run":
            return set(lane_source_matrix.get("dry_run", []))
        raise InvalidLaneOverrideError(f"run entrypoint does not allow lane: {lane}")

    if entrypoint == "backfill":
        runtime_sources = set(lane_source_matrix.get("historical_backfill", []))
        policy_sources = set(backfill_policy.get("allowed_sources", {}).get("allowed", []))
        return runtime_sources.intersection(policy_sources)

    if entrypoint == "research":
        return set(research_policy.get("input_contract", {}).get("allowed_sources", []))

    raise ConfigBootstrapError(f"unknown entrypoint for source resolution: {entrypoint}")


def _select_default_lane_and_source(
    entrypoint: str,
    *,
    operator_defaults: Mapping[str, Any],
) -> tuple[str, str]:
    entry_defaults = operator_defaults.get("entrypoint_defaults", {})
    if not isinstance(entry_defaults, dict) or entrypoint not in entry_defaults:
        raise RegistryValidationError(f"operator_defaults missing entrypoint_defaults for {entrypoint}")
    cfg = entry_defaults[entrypoint]
    if not isinstance(cfg, dict):
        raise RegistryValidationError(f"operator_defaults entrypoint_defaults.{entrypoint} must be a mapping")

    lane = cfg.get("lane")
    source = cfg.get("source")
    if not isinstance(lane, str) or not lane.strip():
        raise RegistryValidationError(f"operator_defaults entrypoint_defaults.{entrypoint}.lane invalid")
    if not isinstance(source, str) or not source.strip():
        raise RegistryValidationError(f"operator_defaults entrypoint_defaults.{entrypoint}.source invalid")
    return lane, source


def _selected_outputs_for_entrypoint(
    entrypoint: str,
    *,
    operator_defaults: Mapping[str, Any],
) -> list[str]:
    output_cfg = operator_defaults.get("default_output_files", {})
    if not isinstance(output_cfg, dict) or entrypoint not in output_cfg:
        raise RegistryValidationError(f"operator_defaults missing default_output_files for {entrypoint}")
    outputs = output_cfg[entrypoint]
    if not isinstance(outputs, list) or not outputs:
        raise RegistryValidationError(f"default_output_files.{entrypoint} must be a non-empty list")
    normalized: list[str] = []
    for idx, item in enumerate(outputs):
        if not isinstance(item, str) or not item.strip():
            raise RegistryValidationError(f"default_output_files.{entrypoint}[{idx}] invalid")
        normalized.append(item)
    return normalized


def _selected_export_formats(
    *,
    operator_defaults: Mapping[str, Any],
    export_policy: Mapping[str, Any],
    export_format_overrides: Mapping[str, str] | None,
) -> dict[str, str]:
    defaults = operator_defaults.get("default_export_formats_by_family", {})
    families = export_policy.get("allowed_export_families", {})

    if not isinstance(defaults, dict):
        raise RegistryValidationError("operator_defaults.default_export_formats_by_family must be a mapping")
    if not isinstance(families, dict):
        raise RegistryValidationError("export_policy.allowed_export_families must be a mapping")

    selected: dict[str, str] = {}
    for family, fmt in defaults.items():
        if family not in families:
            raise RegistryValidationError(f"default export family not in export_policy: {family}")
        family_cfg = families[family]
        if not isinstance(family_cfg, dict):
            raise RegistryValidationError(f"export_policy family cfg must be mapping: {family}")
        allowed_formats = family_cfg.get("allowed_formats", [])
        if not isinstance(allowed_formats, list) or not allowed_formats:
            raise RegistryValidationError(f"allowed_export_families.{family}.allowed_formats invalid")
        if fmt not in allowed_formats:
            raise RegistryValidationError(f"default export format invalid for {family}: {fmt}")
        selected[family] = fmt

    if export_format_overrides:
        for family, override_fmt in export_format_overrides.items():
            if family not in families:
                raise ConfigBootstrapError(f"unknown export family override: {family}")
            if not isinstance(override_fmt, str) or not override_fmt.strip():
                raise ConfigBootstrapError(f"invalid export format override for {family}")
            allowed_formats = families[family].get("allowed_formats", [])
            if override_fmt not in allowed_formats:
                raise ConfigBootstrapError(
                    f"export format override not allowed for {family}: {override_fmt}"
                )
            selected[family] = override_fmt

    return selected


def build_bootstrap_package(
    entrypoint: str,
    *,
    lane_override: str | None = None,
    source_override: str | None = None,
    export_format_overrides: Mapping[str, str] | None = None,
    registry: ConfigRegistry | None = None,
    config_registry_path: Path | str = DEFAULT_CONFIG_REGISTRY_PATH,
    project_root: Path | None = None,
) -> BootstrapPackage:
    """
    Resolve a freeze-grade bootstrap package for one entrypoint.

    This function:
    - loads the canonical registry if needed
    - loads operator default / policy JSON contracts
    - validates optional lane/source/export overrides
    - resolves the effective registry snapshot
    """
    reg = registry if registry is not None else load_config_registry(
        config_registry_path,
        project_root=project_root,
    )

    entry = entrypoint.strip() if isinstance(entrypoint, str) else ""
    if not entry:
        raise ConfigBootstrapError("entrypoint must be a non-empty string")

    entry_bundle = resolve_entrypoint_bundle(entry, registry=reg, project_root=project_root)

    operator_defaults = load_registered_json_contract("operator_defaults", registry=reg, project_root=project_root)
    runtime_policy = load_registered_json_contract("runtime_policy", registry=reg, project_root=project_root)
    report_policy = load_registered_json_contract("report_policy", registry=reg, project_root=project_root)
    backfill_policy = load_registered_json_contract("backfill_policy", registry=reg, project_root=project_root)
    research_policy = load_registered_json_contract("research_policy", registry=reg, project_root=project_root)
    export_policy = load_registered_json_contract("export_policy", registry=reg, project_root=project_root)

    default_lane, default_source = _select_default_lane_and_source(entry, operator_defaults=operator_defaults)

    resolved_lane = _normalize_override(lane_override, "lane") or default_lane
    resolved_source = _normalize_override(source_override, "source") or default_source

    allowed_lanes = _allowed_lanes_for_entrypoint(
        entry,
        runtime_policy=runtime_policy,
        research_policy=research_policy,
    )
    if resolved_lane not in allowed_lanes:
        raise InvalidLaneOverrideError(
            f"entrypoint={entry} does not allow lane={resolved_lane}; allowed={sorted(allowed_lanes)}"
        )

    allowed_sources = _allowed_sources_for_entrypoint_lane(
        entry,
        resolved_lane,
        runtime_policy=runtime_policy,
        backfill_policy=backfill_policy,
        research_policy=research_policy,
    )
    if resolved_source not in allowed_sources:
        raise InvalidSourceOverrideError(
            f"entrypoint={entry} lane={resolved_lane} does not allow source={resolved_source}; "
            f"allowed={sorted(allowed_sources)}"
        )

    selected_outputs = _selected_outputs_for_entrypoint(entry, operator_defaults=operator_defaults)
    selected_export_formats = _selected_export_formats(
        operator_defaults=operator_defaults,
        export_policy=export_policy,
        export_format_overrides=export_format_overrides,
    )

    profile_group = _DEFAULT_PROFILE_GROUP_BY_ENTRYPOINT.get(entry)
    if profile_group is None:
        raise ConfigBootstrapError(f"no profile group mapping for entrypoint: {entry}")

    snapshot = build_effective_registry_snapshot(
        entrypoint=entry,
        profile_group=profile_group,
        registry=reg,
        project_root=project_root,
    )

    json_contracts = {
        "operator_defaults": operator_defaults,
        "runtime_policy": runtime_policy,
        "report_policy": report_policy,
        "backfill_policy": backfill_policy,
        "research_policy": research_policy,
        "export_policy": export_policy,
    }

    return BootstrapPackage(
        entrypoint=entry,
        profile_group=profile_group,
        selected_lane=resolved_lane,
        selected_source=resolved_source,
        selected_outputs=selected_outputs,
        selected_export_formats=selected_export_formats,
        registry_source_path=reg.source_path,
        registry_version=reg.policy_version,
        entrypoint_bundle=entry_bundle,
        effective_registry_snapshot=snapshot,
        json_contracts=json_contracts,
    )


__all__ = [
    "ConfigBootstrapError",
    "InvalidLaneOverrideError",
    "InvalidSourceOverrideError",
    "BootstrapPackage",
    "build_bootstrap_package",
]
