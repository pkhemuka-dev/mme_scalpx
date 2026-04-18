"""
app.mme_scalpx.research_capture.session_materializer

Freeze-grade session materialization for the research-capture chapter.

Ownership
---------
This module OWNS:
- writing effective_inputs.json from the composed session context
- writing a thin session_materialization_report.json audit surface
- returning a deterministic session materialization result for entrypoints

This module DOES NOT own:
- runtime business logic
- archive writing
- report generation beyond the session audit surfaces
- broker/source I/O
- production doctrine mutation
- canonical archive mutation

Design laws
-----------
- session_context = operator/session truth surface
- session_materializer = persistence of effective input truth only
- raw/live/backfill/research stay separate lanes
- thin, deterministic, auditable
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from app.mme_scalpx.research_capture.config_loader import (
    ConfigRegistry,
    DEFAULT_CONFIG_REGISTRY_PATH,
    load_config_registry,
)
from app.mme_scalpx.research_capture.session_context import (
    SessionContext,
    build_session_context,
)


class SessionMaterializerError(RuntimeError):
    """Base error for session materialization."""


@dataclass(frozen=True, slots=True)
class SessionMaterializedFile:
    """A file written by session materialization."""

    name: str
    path: str

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "path": self.path,
        }


@dataclass(frozen=True, slots=True)
class SessionMaterializationResult:
    """Deterministic result of session materialization."""

    entrypoint: str
    lane: str
    source: str
    run_id: str
    report_root: str
    materialized_files: tuple[SessionMaterializedFile, ...]
    session_context: SessionContext

    def to_dict(self) -> dict[str, Any]:
        return {
            "entrypoint": self.entrypoint,
            "lane": self.lane,
            "source": self.source,
            "run_id": self.run_id,
            "report_root": self.report_root,
            "materialized_files": [item.to_dict() for item in self.materialized_files],
            "session_context": self.session_context.to_dict(),
        }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _effective_inputs_path(session_context: SessionContext) -> Path:
    return (
        Path(session_context.materialization_result.report_root) / "effective_inputs.json"
    ).resolve()


def _session_materialization_report_path(session_context: SessionContext) -> Path:
    return (
        Path(session_context.materialization_result.report_root) / "session_materialization_report.json"
    ).resolve()


def materialize_session_context(
    session_context: SessionContext,
) -> SessionMaterializationResult:
    """
    Persist effective session inputs and the thin session materialization audit surface.
    """
    report_root = Path(session_context.materialization_result.report_root)
    report_root.mkdir(parents=True, exist_ok=True)

    effective_inputs_path = _effective_inputs_path(session_context)
    _write_json(effective_inputs_path, session_context.effective_inputs_payload)

    session_materialization_report = {
        "session_materialization_ok": True,
        "entrypoint": session_context.entrypoint,
        "lane": session_context.lane,
        "source": session_context.source,
        "run_id": session_context.run_id,
        "report_root": session_context.materialization_result.report_root,
        "effective_inputs_path": str(effective_inputs_path),
        "profile_group": session_context.profile_group,
    }
    session_materialization_report_path = _session_materialization_report_path(session_context)
    _write_json(session_materialization_report_path, session_materialization_report)

    return SessionMaterializationResult(
        entrypoint=session_context.entrypoint,
        lane=session_context.lane,
        source=session_context.source,
        run_id=session_context.run_id,
        report_root=session_context.materialization_result.report_root,
        materialized_files=(
            SessionMaterializedFile(
                name="effective_inputs.json",
                path=str(effective_inputs_path),
            ),
            SessionMaterializedFile(
                name="session_materialization_report.json",
                path=str(session_materialization_report_path),
            ),
        ),
        session_context=session_context,
    )


def build_and_materialize_session_context(
    entrypoint: str,
    *,
    run_id: str,
    session_date: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    session_dates: tuple[str, ...] | list[str] | None = None,
    instrument_scope: str | None = None,
    research_profile: str | None = None,
    feature_families: tuple[str, ...] | list[str] | None = None,
    notes: str | None = None,
    lane_override: str | None = None,
    source_override: str | None = None,
    export_format_overrides: Mapping[str, str] | None = None,
    registry: ConfigRegistry | None = None,
    config_registry_path: Path | str = DEFAULT_CONFIG_REGISTRY_PATH,
    project_root: Path | None = None,
) -> SessionMaterializationResult:
    """
    Compose the frozen session context, then materialize its session audit surfaces.
    """
    reg = registry if registry is not None else load_config_registry(
        config_registry_path,
        project_root=project_root,
    )

    session_context = build_session_context(
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
    return materialize_session_context(session_context)


__all__ = [
    "SessionMaterializerError",
    "SessionMaterializedFile",
    "SessionMaterializationResult",
    "materialize_session_context",
    "build_and_materialize_session_context",
]
