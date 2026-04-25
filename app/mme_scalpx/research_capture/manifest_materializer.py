"""
app.mme_scalpx.research_capture.manifest_materializer

Freeze-grade manifest materialization for the research-capture chapter.

Ownership
---------
This module OWNS:
- writing manifest.json from the frozen manifest seed
- writing source_availability.json as a seeded audit surface
- writing integrity_summary.json as a seeded audit surface
- writing a thin manifest_materialization_report.json audit surface
- returning a deterministic manifest materialization result

This module DOES NOT own:
- runtime business logic
- raw/live capture logic
- archive writing beyond manifest/audit seed surfaces
- broker/source I/O
- production doctrine mutation
- canonical archive mutation

Design laws
-----------
- research-data constitution requires manifest/source/integrity surfaces
- manifest seed comes before full capture/runtime enrichment
- this module writes seeded truth surfaces only
- thin, deterministic, auditable
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from app.mme_scalpx.research_capture.config_loader import (
    ConfigRegistry,
    DEFAULT_CONFIG_REGISTRY_PATH,
    load_config_registry,
)
from app.mme_scalpx.research_capture.manifest_seed import (
    ManifestSeed,
    build_manifest_seed_from_operator_inputs,
)


class ManifestMaterializerError(RuntimeError):
    """Base error for manifest materialization."""


@dataclass(frozen=True, slots=True)
class ManifestMaterializedFile:
    """A file written by manifest materialization."""

    name: str
    path: str

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "path": self.path,
        }


@dataclass(frozen=True, slots=True)
class ManifestMaterializationResult:
    """Deterministic result of manifest materialization."""

    entrypoint: str
    lane: str
    source: str
    run_id: str
    materialized_files: tuple[ManifestMaterializedFile, ...]
    manifest_seed: ManifestSeed

    def to_dict(self) -> dict[str, Any]:
        return {
            "entrypoint": self.entrypoint,
            "lane": self.lane,
            "source": self.source,
            "run_id": self.run_id,
            "materialized_files": [item.to_dict() for item in self.materialized_files],
            "manifest_seed": self.manifest_seed.to_dict(),
        }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _manifest_payload(seed: ManifestSeed) -> dict[str, Any]:
    return {
        "manifest_kind": "research_capture_manifest_seed",
        "manifest_version": "v1",
        "seeded": True,
        "run_id": seed.run_id,
        "entrypoint": seed.entrypoint,
        "lane": seed.lane,
        "source": seed.source,
        "session_date": seed.session_date,
        "start_date": seed.start_date,
        "end_date": seed.end_date,
        "session_dates": list(seed.session_dates),
        "input_scope": seed.input_scope,
        "versions_snapshot": dict(seed.versions_snapshot),
        "paths": {
            "manifest_path": seed.manifest_path,
            "source_availability_path": seed.source_availability_path,
            "integrity_summary_path": seed.integrity_summary_path,
            "effective_inputs_path": seed.effective_inputs_path,
            "effective_registry_snapshot_path": seed.effective_registry_snapshot_path,
        },
        "metadata": dict(seed.metadata),
    }


def _source_availability_payload(seed: ManifestSeed) -> dict[str, Any]:
    return {
        "source_availability_kind": "research_capture_source_availability_seed",
        "seeded": True,
        "run_id": seed.run_id,
        "lane": seed.lane,
        "source": seed.source,
        "session_date": seed.session_date,
        "sources_checked": [seed.source],
        "available_sources": [seed.source],
        "missing_sources": [],
        "availability_verdict": "PASS",
        "versions_snapshot": dict(seed.versions_snapshot),
        "ts_utc": seed.metadata["ts_utc"],
    }


def _integrity_summary_payload(seed: ManifestSeed) -> dict[str, Any]:
    return {
        "integrity_summary_kind": "research_capture_integrity_seed",
        "seeded": True,
        "run_id": seed.run_id,
        "lane": seed.lane,
        "source": seed.source,
        "session_date": seed.session_date,
        "verdict": "PASS",
        "failed_checks": [],
        "warned_checks": [],
        "waived_checks": [],
        "threshold_snapshot": {},
        "versions_snapshot": dict(seed.versions_snapshot),
        "ts_utc": seed.metadata["ts_utc"],
    }


def _manifest_materialization_report_payload(seed: ManifestSeed) -> dict[str, Any]:
    return {
        "manifest_materialization_ok": True,
        "entrypoint": seed.entrypoint,
        "lane": seed.lane,
        "source": seed.source,
        "run_id": seed.run_id,
        "manifest_path": seed.manifest_path,
        "source_availability_path": seed.source_availability_path,
        "integrity_summary_path": seed.integrity_summary_path,
        "effective_inputs_path": seed.effective_inputs_path,
        "effective_registry_snapshot_path": seed.effective_registry_snapshot_path,
        "versions_snapshot": dict(seed.versions_snapshot),
        "ts_utc": seed.metadata["ts_utc"],
    }


def _manifest_materialization_report_path(seed: ManifestSeed) -> Path:
    return (Path(seed.metadata["report_root"]) / "manifest_materialization_report.json").resolve()


def materialize_manifest_seed(
    manifest_seed: ManifestSeed,
) -> ManifestMaterializationResult:
    """
    Write seeded manifest/source/integrity surfaces from the manifest seed.
    """
    manifest_path = Path(manifest_seed.manifest_path).resolve()
    source_availability_path = Path(manifest_seed.source_availability_path).resolve()
    integrity_summary_path = Path(manifest_seed.integrity_summary_path).resolve()
    report_path = _manifest_materialization_report_path(manifest_seed)

    _write_json(manifest_path, _manifest_payload(manifest_seed))
    _write_json(source_availability_path, _source_availability_payload(manifest_seed))
    _write_json(integrity_summary_path, _integrity_summary_payload(manifest_seed))
    _write_json(report_path, _manifest_materialization_report_payload(manifest_seed))

    return ManifestMaterializationResult(
        entrypoint=manifest_seed.entrypoint,
        lane=manifest_seed.lane,
        source=manifest_seed.source,
        run_id=manifest_seed.run_id,
        materialized_files=(
            ManifestMaterializedFile(name="manifest.json", path=str(manifest_path)),
            ManifestMaterializedFile(name="source_availability.json", path=str(source_availability_path)),
            ManifestMaterializedFile(name="integrity_summary.json", path=str(integrity_summary_path)),
            ManifestMaterializedFile(name="manifest_materialization_report.json", path=str(report_path)),
        ),
        manifest_seed=manifest_seed,
    )


def build_and_materialize_manifest_seed(
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
) -> ManifestMaterializationResult:
    """
    Build the frozen manifest seed, then materialize seeded manifest surfaces.
    """
    reg = registry if registry is not None else load_config_registry(
        config_registry_path,
        project_root=project_root,
    )

    manifest_seed = build_manifest_seed_from_operator_inputs(
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
    return materialize_manifest_seed(manifest_seed)


__all__ = [
    "ManifestMaterializerError",
    "ManifestMaterializedFile",
    "ManifestMaterializationResult",
    "materialize_manifest_seed",
    "build_and_materialize_manifest_seed",
]

# =============================================================================
# Batch 17 freeze hardening: contained atomic JSON writes
# =============================================================================
_BATCH17_ATOMIC_JSON_GUARD_VERSION = "1"

from app.mme_scalpx.research_capture.utils import atomic_write_json as _batch17_atomic_write_json

_BATCH17_ORIGINAL_WRITE_JSON = globals().get("_write_json")

def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _batch17_atomic_write_json(
        path,
        payload,
        root=Path.cwd(),
        label=f"{__name__}._write_json",
    )

_write_json._batch17_atomic = True
