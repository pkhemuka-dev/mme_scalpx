"""
app.mme_scalpx.research_capture.session_context

Freeze-grade session-context composition for the research-capture chapter.

Ownership
---------
This module OWNS:
- normalizing operator input surfaces for verify/run/backfill/research entrypoints
- validating entrypoint-specific session/date-scope requirements
- composing a deterministic session context on top of artifact materialization
- building an auditable effective-inputs payload for downstream entrypoints

This module DOES NOT own:
- runtime business logic
- archive writing
- report generation
- broker/source I/O
- production doctrine mutation
- canonical archive mutation

Design laws
-----------
- raw/live/backfill/research remain distinct lanes
- live capture requires explicit session_date
- backfill requires explicit date scope
- research requires explicit input scope and research profile
- this module stays thin, deterministic, and audit-oriented
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from app.mme_scalpx.research_capture.artifact_materializer import (
    ArtifactMaterializationResult,
    build_and_materialize_artifact_plan,
)
from app.mme_scalpx.research_capture.config_loader import (
    ConfigRegistry,
    DEFAULT_CONFIG_REGISTRY_PATH,
    load_config_registry,
)


class SessionContextError(RuntimeError):
    """Base error for session-context composition."""


class MissingSessionInputError(SessionContextError):
    """Raised when required operator/session inputs are missing."""


class InvalidSessionScopeError(SessionContextError):
    """Raised when date scope or entrypoint scope is invalid."""


@dataclass(frozen=True, slots=True)
class SessionInputs:
    """Normalized operator/session inputs."""

    entrypoint: str
    run_id: str
    lane: str
    source: str
    session_date: str | None
    start_date: str | None
    end_date: str | None
    session_dates: tuple[str, ...]
    instrument_scope: str | None
    research_profile: str | None
    feature_families: tuple[str, ...]
    notes: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "entrypoint": self.entrypoint,
            "run_id": self.run_id,
            "lane": self.lane,
            "source": self.source,
            "session_date": self.session_date,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "session_dates": list(self.session_dates),
            "instrument_scope": self.instrument_scope,
            "research_profile": self.research_profile,
            "feature_families": list(self.feature_families),
            "notes": self.notes,
        }


@dataclass(frozen=True, slots=True)
class SessionContext:
    """Deterministic, auditable session context."""

    entrypoint: str
    lane: str
    source: str
    run_id: str
    profile_group: str
    session_inputs: SessionInputs
    effective_inputs_payload: dict[str, Any]
    materialization_result: ArtifactMaterializationResult

    def to_dict(self) -> dict[str, Any]:
        return {
            "entrypoint": self.entrypoint,
            "lane": self.lane,
            "source": self.source,
            "run_id": self.run_id,
            "profile_group": self.profile_group,
            "session_inputs": self.session_inputs.to_dict(),
            "effective_inputs_payload": dict(self.effective_inputs_payload),
            "materialization_result": self.materialization_result.to_dict(),
        }


def _utc_now_z() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _optional_str(value: str | None, name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise SessionContextError(f"{name} must be a non-empty string when provided")
    return value.strip()


def _required_str(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SessionContextError(f"{name} must be a non-empty string")
    return value.strip()


def _optional_str_seq(value: Sequence[str] | None, name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    normalized: list[str] = []
    for idx, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise SessionContextError(f"{name}[{idx}] must be a non-empty string")
        normalized.append(item.strip())
    return tuple(normalized)


def _validate_entrypoint_scope(
    *,
    entrypoint: str,
    session_date: str | None,
    start_date: str | None,
    end_date: str | None,
    session_dates: tuple[str, ...],
    research_profile: str | None,
) -> None:
    if entrypoint == "verify":
        return

    if entrypoint == "run":
        if session_date is None:
            raise MissingSessionInputError("run entrypoint requires session_date")
        return

    if entrypoint == "backfill":
        has_range = start_date is not None and end_date is not None
        has_list = len(session_dates) > 0
        if not (has_range or has_list):
            raise MissingSessionInputError(
                "backfill entrypoint requires start_date/end_date or non-empty session_dates"
            )
        return

    if entrypoint == "research":
        has_single = session_date is not None
        has_range = start_date is not None and end_date is not None
        has_list = len(session_dates) > 0
        if not (has_single or has_range or has_list):
            raise MissingSessionInputError(
                "research entrypoint requires session_date, start_date/end_date, or non-empty session_dates"
            )
        if research_profile is None:
            raise MissingSessionInputError("research entrypoint requires research_profile")
        return

    raise InvalidSessionScopeError(f"unknown entrypoint for session scope validation: {entrypoint}")


def _derive_input_scope(
    *,
    entrypoint: str,
    source: str,
    session_date: str | None,
    start_date: str | None,
    end_date: str | None,
    session_dates: tuple[str, ...],
    instrument_scope: str | None,
) -> str:
    suffix = f"/instrument_scope={instrument_scope}" if instrument_scope else ""

    if session_date is not None:
        return f"{source}/session_date={session_date}{suffix}"

    if start_date is not None and end_date is not None:
        return f"{source}/start_date={start_date}/end_date={end_date}{suffix}"

    if session_dates:
        joined = ",".join(session_dates)
        return f"{source}/session_dates={joined}{suffix}"

    if entrypoint == "verify":
        return f"{source}/verify{suffix}"

    raise InvalidSessionScopeError(f"unable to derive input scope for entrypoint={entrypoint}")


def _build_effective_inputs_payload(
    *,
    materialization_result: ArtifactMaterializationResult,
    session_inputs: SessionInputs,
) -> dict[str, Any]:
    bootstrap = materialization_result.artifact_plan.config_context.bootstrap_package
    operator_defaults = bootstrap.json_contracts["operator_defaults"]
    required_fields = operator_defaults["required_effective_inputs_fields"]

    payload = {
        "run_id": session_inputs.run_id,
        "entrypoint": session_inputs.entrypoint,
        "lane": session_inputs.lane,
        "source": session_inputs.source,
        "selected_export_formats": dict(bootstrap.selected_export_formats),
        "selected_outputs": list(bootstrap.selected_outputs),
        "ts_utc": _utc_now_z(),
        "session_date": session_inputs.session_date,
        "start_date": session_inputs.start_date,
        "end_date": session_inputs.end_date,
        "session_dates": list(session_inputs.session_dates),
        "instrument_scope": session_inputs.instrument_scope,
        "research_profile": session_inputs.research_profile,
        "feature_families": list(session_inputs.feature_families),
        "notes": session_inputs.notes,
        "profile_group": materialization_result.artifact_plan.profile_group,
        "run_root": materialization_result.run_root,
        "report_root": materialization_result.report_root,
        "export_root": materialization_result.export_root,
        "effective_registry_snapshot_path": (
            materialization_result.artifact_plan.effective_registry_snapshot_path
        ),
        "input_scope": _derive_input_scope(
            entrypoint=session_inputs.entrypoint,
            source=session_inputs.source,
            session_date=session_inputs.session_date,
            start_date=session_inputs.start_date,
            end_date=session_inputs.end_date,
            session_dates=session_inputs.session_dates,
            instrument_scope=session_inputs.instrument_scope,
        ),
    }

    missing = [field for field in required_fields if field not in payload]
    if missing:
        raise SessionContextError(f"effective_inputs_payload missing required fields: {missing}")

    return payload


def build_session_context(
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
) -> SessionContext:
    """
    Build a deterministic, audited session context on top of artifact materialization.
    """
    normalized_entrypoint = _required_str(entrypoint, "entrypoint")
    normalized_run_id = _required_str(run_id, "run_id")
    normalized_session_date = _optional_str(session_date, "session_date")
    normalized_start_date = _optional_str(start_date, "start_date")
    normalized_end_date = _optional_str(end_date, "end_date")
    normalized_instrument_scope = _optional_str(instrument_scope, "instrument_scope")
    normalized_research_profile = _optional_str(research_profile, "research_profile")
    normalized_notes = _optional_str(notes, "notes")
    normalized_session_dates = _optional_str_seq(session_dates, "session_dates")
    normalized_feature_families = _optional_str_seq(feature_families, "feature_families")

    _validate_entrypoint_scope(
        entrypoint=normalized_entrypoint,
        session_date=normalized_session_date,
        start_date=normalized_start_date,
        end_date=normalized_end_date,
        session_dates=normalized_session_dates,
        research_profile=normalized_research_profile,
    )

    reg = registry if registry is not None else load_config_registry(
        config_registry_path,
        project_root=project_root,
    )

    materialization_result = build_and_materialize_artifact_plan(
        normalized_entrypoint,
        run_id=normalized_run_id,
        lane_override=lane_override,
        source_override=source_override,
        export_format_overrides=export_format_overrides,
        registry=reg,
        project_root=project_root,
    )

    session_inputs = SessionInputs(
        entrypoint=normalized_entrypoint,
        run_id=normalized_run_id,
        lane=materialization_result.lane,
        source=materialization_result.source,
        session_date=normalized_session_date,
        start_date=normalized_start_date,
        end_date=normalized_end_date,
        session_dates=normalized_session_dates,
        instrument_scope=normalized_instrument_scope,
        research_profile=normalized_research_profile,
        feature_families=normalized_feature_families,
        notes=normalized_notes,
    )

    effective_inputs_payload = _build_effective_inputs_payload(
        materialization_result=materialization_result,
        session_inputs=session_inputs,
    )

    return SessionContext(
        entrypoint=normalized_entrypoint,
        lane=materialization_result.lane,
        source=materialization_result.source,
        run_id=normalized_run_id,
        profile_group=materialization_result.artifact_plan.profile_group,
        session_inputs=session_inputs,
        effective_inputs_payload=effective_inputs_payload,
        materialization_result=materialization_result,
    )


__all__ = [
    "SessionContextError",
    "MissingSessionInputError",
    "InvalidSessionScopeError",
    "SessionInputs",
    "SessionContext",
    "build_session_context",
]
