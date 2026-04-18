"""
app.mme_scalpx.research_capture.manifest_seed

Freeze-grade manifest-seed composition for the research-capture chapter.

Ownership
---------
This module OWNS:
- composing a deterministic manifest seed from session materialization
- preparing canonical manifest input surfaces before capture logic expands
- exposing thin manifest-ready metadata for downstream manifest handling

This module DOES NOT own:
- runtime business logic
- raw/live capture logic
- archive writing
- broker/source I/O
- production doctrine mutation
- canonical archive mutation

Design laws
-----------
- research-data constitution requires manifestable audit surfaces
- manifest seed comes after session/effective-input truth
- this module prepares manifest input only; it does not perform capture
- thin, deterministic, auditable
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from app.mme_scalpx.research_capture.config_loader import (
    ConfigRegistry,
    DEFAULT_CONFIG_REGISTRY_PATH,
    load_config_registry,
    load_registered_json_contract,
)
from app.mme_scalpx.research_capture.session_materializer import (
    SessionMaterializationResult,
    build_and_materialize_session_context,
)


class ManifestSeedError(RuntimeError):
    """Base error for manifest-seed composition."""


@dataclass(frozen=True, slots=True)
class ManifestSeed:
    """Deterministic manifest seed prepared from frozen session materialization."""

    entrypoint: str
    lane: str
    source: str
    run_id: str
    session_date: str | None
    start_date: str | None
    end_date: str | None
    session_dates: tuple[str, ...]
    input_scope: str
    manifest_path: str
    source_availability_path: str
    integrity_summary_path: str
    effective_inputs_path: str
    effective_registry_snapshot_path: str
    versions_snapshot: dict[str, str]
    metadata: dict[str, Any]
    session_materialization_result: SessionMaterializationResult

    def to_dict(self) -> dict[str, Any]:
        return {
            "entrypoint": self.entrypoint,
            "lane": self.lane,
            "source": self.source,
            "run_id": self.run_id,
            "session_date": self.session_date,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "session_dates": list(self.session_dates),
            "input_scope": self.input_scope,
            "manifest_path": self.manifest_path,
            "source_availability_path": self.source_availability_path,
            "integrity_summary_path": self.integrity_summary_path,
            "effective_inputs_path": self.effective_inputs_path,
            "effective_registry_snapshot_path": self.effective_registry_snapshot_path,
            "versions_snapshot": dict(self.versions_snapshot),
            "metadata": dict(self.metadata),
            "session_materialization_result": self.session_materialization_result.to_dict(),
        }


def _utc_now_z() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _require_dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ManifestSeedError(f"{name} must be a mapping")
    return dict(value)


def _require_nonempty_str(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ManifestSeedError(f"{name} must be a non-empty string")
    return value.strip()


def _optional_nonempty_str(value: str | None, name: str) -> str | None:
    if value is None:
        return None
    return _require_nonempty_str(value, name)


def _normalize_str_seq(value: Sequence[str] | None, name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    normalized: list[str] = []
    for idx, item in enumerate(value):
        normalized.append(_require_nonempty_str(item, f"{name}[{idx}]"))
    return tuple(normalized)


def _pick_first_nonempty(
    mapping: Mapping[str, Any],
    keys: Sequence[str],
    name: str,
    *,
    default: str | None = None,
) -> str:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    if default is not None and isinstance(default, str) and default.strip():
        return default.strip()
    raise ManifestSeedError(f"{name} missing; tried keys={list(keys)}")


def _path_from_selected_outputs(
    result: SessionMaterializationResult,
    output_name: str,
) -> str:
    for item in result.session_context.materialization_result.artifact_plan.required_artifacts:
        if item.name == output_name:
            return item.path
    for item in result.session_context.materialization_result.artifact_plan.optional_artifacts:
        if item.name == output_name:
            return item.path
    raise ManifestSeedError(f"output path not found in artifact plan: {output_name}")


def _path_from_materialized_files(
    result: SessionMaterializationResult,
    file_name: str,
) -> str:
    for item in result.materialized_files:
        if item.name == file_name:
            return item.path
    raise ManifestSeedError(f"materialized file not found: {file_name}")


def _fallback_report_path(
    result: SessionMaterializationResult,
    file_name: str,
) -> str:
    return str((Path(result.session_context.materialization_result.report_root) / file_name).resolve())


def _selected_output_or_fallback_report_path(
    result: SessionMaterializationResult,
    file_name: str,
) -> str:
    try:
        return _path_from_selected_outputs(result, file_name)
    except ManifestSeedError:
        return _fallback_report_path(result, file_name)


def build_manifest_seed(
    session_materialization_result: SessionMaterializationResult,
    *,
    registry: ConfigRegistry | None = None,
    config_registry_path: Path | str = DEFAULT_CONFIG_REGISTRY_PATH,
    project_root: Path | None = None,
) -> ManifestSeed:
    """
    Build a deterministic manifest seed from frozen session materialization.
    """
    reg = registry if registry is not None else load_config_registry(
        config_registry_path,
        project_root=project_root,
    )

    schema_version = load_registered_json_contract("schema_version", registry=reg, project_root=project_root)
    source_policy = load_registered_json_contract("source_policy", registry=reg, project_root=project_root)
    integrity_policy = load_registered_json_contract("integrity_policy", registry=reg, project_root=project_root)
    runtime_policy = load_registered_json_contract("runtime_policy", registry=reg, project_root=project_root)
    report_policy = load_registered_json_contract("report_policy", registry=reg, project_root=project_root)

    session_context = session_materialization_result.session_context
    effective_inputs_payload = _require_dict(
        session_context.effective_inputs_payload,
        "effective_inputs_payload",
    )

    schema_version_value = _pick_first_nonempty(
        schema_version,
        ("schema_version", "version"),
        "schema_version",
    )
    normalization_version_value = _pick_first_nonempty(
        schema_version,
        ("normalization_version",),
        "normalization_version",
        default=schema_version_value,
    )
    derived_version_value = _pick_first_nonempty(
        schema_version,
        ("derived_version",),
        "derived_version",
        default=normalization_version_value,
    )

    versions_snapshot = {
        "schema_version": schema_version_value,
        "normalization_version": normalization_version_value,
        "derived_version": derived_version_value,
        "policy_version": reg.policy_version,
    }

    metadata = {
        "schema_name": "MME Research Capture Manifest Seed",
        "seed_version": "v1",
        "ts_utc": _utc_now_z(),
        "profile_group": session_context.profile_group,
        "entrypoint": session_context.entrypoint,
        "lane": session_context.lane,
        "source": session_context.source,
        "run_id": session_context.run_id,
        "run_root": session_context.materialization_result.run_root,
        "report_root": session_context.materialization_result.report_root,
        "export_root": session_context.materialization_result.export_root,
        "source_policy_version": _require_nonempty_str(source_policy.get("policy_version"), "source_policy.policy_version"),
        "integrity_policy_version": _require_nonempty_str(
            integrity_policy.get("policy_version"),
            "integrity_policy.policy_version",
        ),
        "runtime_policy_version": _require_nonempty_str(
            runtime_policy.get("policy_version"),
            "runtime_policy.policy_version",
        ),
        "report_policy_version": _require_nonempty_str(
            report_policy.get("policy_version"),
            "report_policy.policy_version",
        ),
    }

    manifest_path = _selected_output_or_fallback_report_path(
        session_materialization_result,
        "manifest.json",
    )
    source_availability_path = _selected_output_or_fallback_report_path(
        session_materialization_result,
        "source_availability.json",
    )
    integrity_summary_path = _selected_output_or_fallback_report_path(
        session_materialization_result,
        "integrity_summary.json",
    )

    return ManifestSeed(
        entrypoint=session_context.entrypoint,
        lane=session_context.lane,
        source=session_context.source,
        run_id=session_context.run_id,
        session_date=_optional_nonempty_str(session_context.session_inputs.session_date, "session_date"),
        start_date=_optional_nonempty_str(session_context.session_inputs.start_date, "start_date"),
        end_date=_optional_nonempty_str(session_context.session_inputs.end_date, "end_date"),
        session_dates=_normalize_str_seq(session_context.session_inputs.session_dates, "session_dates"),
        input_scope=_require_nonempty_str(effective_inputs_payload["input_scope"], "effective_inputs_payload.input_scope"),
        manifest_path=manifest_path,
        source_availability_path=source_availability_path,
        integrity_summary_path=integrity_summary_path,
        effective_inputs_path=_path_from_materialized_files(
            session_materialization_result,
            "effective_inputs.json",
        ),
        effective_registry_snapshot_path=session_context.materialization_result.artifact_plan.effective_registry_snapshot_path,
        versions_snapshot=versions_snapshot,
        metadata=metadata,
        session_materialization_result=session_materialization_result,
    )


def build_manifest_seed_from_operator_inputs(
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
) -> ManifestSeed:
    """
    Build session materialization first, then derive the deterministic manifest seed.
    """
    reg = registry if registry is not None else load_config_registry(
        config_registry_path,
        project_root=project_root,
    )

    session_materialization_result = build_and_materialize_session_context(
        entrypoint,
        run_id=run_id,
        session_date=session_date,
        start_date=start_date,
        end_date=end_date,
        session_dates=tuple(session_dates) if session_dates is not None else None,
        instrument_scope=instrument_scope,
        research_profile=research_profile,
        feature_families=tuple(feature_families) if feature_families is not None else None,
        notes=notes,
        lane_override=lane_override,
        source_override=source_override,
        export_format_overrides=export_format_overrides,
        registry=reg,
        project_root=project_root,
    )
    return build_manifest_seed(
        session_materialization_result,
        registry=reg,
        project_root=project_root,
    )


__all__ = [
    "ManifestSeedError",
    "ManifestSeed",
    "build_manifest_seed",
    "build_manifest_seed_from_operator_inputs",
]
