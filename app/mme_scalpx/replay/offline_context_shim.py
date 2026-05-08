"""Offline-only replay context shims for guarded parity work.

This module is intentionally inert:
- no broker imports
- no live transport imports
- no service startup
- no production doctrine mutation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any


# Offline topology notes preservation helpers.
# Added for replay/offline compatibility only; no live runtime, Redis, broker, or doctrine effect.
_OFFLINE_TOPOLOGY_PLAN_NOTES_REGISTRY_29AG_R4_R1 = {}

def _offline_coerce_topology_notes_29ag_r4_r1(value):
    if value is None:
        return tuple()
    if isinstance(value, str):
        stripped = value.strip()
        return (stripped,) if stripped else tuple()
    if isinstance(value, dict):
        import json as _json
        encoded = _json.dumps(value, sort_keys=True, default=str)
        return (encoded,)
    if isinstance(value, (list, tuple, set)):
        rows = []
        for item in value:
            if item in (None, ""):
                continue
            rows.append(str(item))
        return tuple(rows)
    return (str(value),)

def _offline_extract_topology_notes_29ag_r4_r1(container):
    if isinstance(container, dict):
        for key in ("notes", "topology_notes", "plan_notes", "remarks", "comments"):
            if key in container:
                return _offline_coerce_topology_notes_29ag_r4_r1(container.get(key)), True
    return tuple(), False

def _offline_register_topology_notes_29ag_r4_r1(plan, values):
    notes, present = _offline_extract_topology_notes_29ag_r4_r1(values)
    if not present:
        return plan
    try:
        object.__setattr__(plan, "_offline_notes_29ag_r4_r1", notes)
    except Exception:
        pass
    try:
        _OFFLINE_TOPOLOGY_PLAN_NOTES_REGISTRY_29AG_R4_R1[id(plan)] = notes
    except Exception:
        pass
    return plan

def _offline_get_registered_topology_notes_29ag_r4_r1(plan):
    local = getattr(plan, "_offline_notes_29ag_r4_r1", None)
    if local is not None:
        return local
    return _OFFLINE_TOPOLOGY_PLAN_NOTES_REGISTRY_29AG_R4_R1.get(id(plan))



def _safe_path_text(path: Path) -> str:
    return str(path.resolve())


def _stable_offline_run_id(
    *,
    dataset_candidate_root: Path,
    callable_output_root: Path,
    materialization_root_29e: Path,
    metadata: dict[str, Any] | None = None,
) -> str:
    """Return deterministic offline run_id for replay-only guarded dry-runs."""

    metadata = dict(metadata or {})
    seed = {
        "dataset_candidate_root_name": dataset_candidate_root.resolve().name,
        "callable_output_root_name": callable_output_root.resolve().name,
        "materialization_root_29e_name": materialization_root_29e.resolve().name,
        "capture_id": metadata.get("capture_id"),
        "dataset_id": metadata.get("dataset_id"),
        "source_batch": metadata.get("source_batch"),
        "mode": "observe_only_offline_replay",
    }
    digest = hashlib.sha256(
        json.dumps(seed, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()[:16]
    return f"offline_replay_{digest}"


# BEGIN BATCH29U OFFLINE STAGE CALLABLE MATERIALIZATION
def _offline_replay_stage_callable_materializer_29u(
    *,
    stage_name: str,
    order_index: int,
    terminal_stage: bool,
    attr_name: str,
) -> Any:
    """Return an offline-only stage callable for ReplayEngine dry-run traversal.

    This shim does not touch live services, broker APIs, Redis transport, or
    production doctrine. It only gives offline replay placeholder stages a
    callable surface so the guarded ReplayEngine can advance to the next
    contract check.
    """

    def _offline_stage_callable_29u(context: Any, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return {
            "status": "offline_stage_callable_materialized_29u",
            "offline_only": True,
            "stage_name": stage_name,
            "order_index": order_index,
            "terminal_stage": terminal_stage,
            "callable_attr": attr_name,
            "context_type": type(context).__name__,
            "args_count": len(args),
            "kwargs_keys": sorted(kwargs.keys()),
        }

    return _offline_stage_callable_29u
# END BATCH29U OFFLINE STAGE CALLABLE MATERIALIZATION


# BEGIN BATCH29W-R2 OFFLINE TOPOLOGY SCOPE PRESERVATION
def _offline_topology_scope_from_values_29w_r2(topology_plan: Any, values: Any) -> Any:
    """Resolve replay-offline scope without touching production topology contract."""

    if isinstance(values, dict):
        value_scope = values.get("scope")
        if value_scope not in (None, ""):
            return value_scope

    source_scope = getattr(topology_plan, "scope", None)
    if source_scope not in (None, ""):
        return source_scope

    if isinstance(values, dict):
        dataset_id = values.get("dataset_id")
        if dataset_id not in (None, ""):
            return f"offline_replay:{dataset_id}"

    return "offline_replay"
# END BATCH29W-R2 OFFLINE TOPOLOGY SCOPE PRESERVATION


# BEGIN BATCH29Y OFFLINE TOPOLOGY SCOPE VALUE COMPATIBILITY
class OfflineReplayScopeValue29Y(str):
    """Replay-offline scope wrapper.

    It remains string-compatible for existing offline probes, while also
    exposing .value for ReplayEngine topology traversal compatibility.
    """

    @property
    def value(self) -> str:
        return str(self)

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "offline_replay_scope_value_29y_v1",
            "value": str(self),
            "offline_only": True,
        }


def _offline_scope_value_compat_29y(value: Any) -> Any:
    if value is None:
        return OfflineReplayScopeValue29Y("offline_replay")
    if hasattr(value, "value") and not isinstance(value, (str, bytes)):
        return value
    return OfflineReplayScopeValue29Y(str(value))
# END BATCH29Y OFFLINE TOPOLOGY SCOPE VALUE COMPATIBILITY

@dataclass(frozen=True)
class OfflineReplayRunContext:
    """Minimal offline run-context carrier for ReplayEngine dry-run preparation."""

    project_root: str
    dataset_candidate_root: str
    callable_output_root: str
    materialization_root_29e: str
    output_root: str
    run_id: str = "offline_replay_unset"
    mode: str = "observe_only_offline_replay"
    no_broker: bool = True
    no_live_redis: bool = True
    observe_only: bool = True
    dry_run: bool = True
    created_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "project_root": self.project_root,
            "dataset_candidate_root": self.dataset_candidate_root,
            "callable_output_root": self.callable_output_root,
            "materialization_root_29e": self.materialization_root_29e,
            "output_root": self.output_root,
            "run_id": self.run_id,
            "mode": self.mode,
            "no_broker": self.no_broker,
            "no_live_redis": self.no_live_redis,
            "observe_only": self.observe_only,
            "dry_run": self.dry_run,
            "created_at_utc": self.created_at_utc,
            "metadata": dict(self.metadata),
        }


def build_offline_replay_run_context(
    project_root: Path,
    dataset_candidate_root: Path,
    callable_output_root: Path,
    materialization_root_29e: Path,
    output_root: Path,
    metadata: dict[str, Any] | None = None,
    run_id: str | None = None,
) -> OfflineReplayRunContext:
    """Build an offline-only ReplayEngine run context.

    This function only packages filesystem paths and metadata. It does not
    open network connections, start services, or mutate runtime state.
    """

    metadata = dict(metadata or {})
    resolved_run_id = run_id or _stable_offline_run_id(
        dataset_candidate_root=dataset_candidate_root,
        callable_output_root=callable_output_root,
        materialization_root_29e=materialization_root_29e,
        metadata=metadata,
    )

    return OfflineReplayRunContext(
        project_root=_safe_path_text(project_root),
        dataset_candidate_root=_safe_path_text(dataset_candidate_root),
        callable_output_root=_safe_path_text(callable_output_root),
        materialization_root_29e=_safe_path_text(materialization_root_29e),
        output_root=_safe_path_text(output_root),
        run_id=resolved_run_id,
        metadata=metadata,
    )


__all__ = [
    "OfflineReplayRunContext",
    "build_offline_replay_run_context",
]
# ---- Batch 29K-R2 offline topology stages compatibility shim ----
from dataclasses import dataclass as _dataclass_29k_r2, field as _field_29k_r2
from typing import Any as _Any_29k_r2


@_dataclass_29k_r2(frozen=True)
class OfflineReplayStage:
    """Offline-only stage object for guarded ReplayEngine dry-run compatibility."""

    name: str
    stage_id: str
    enabled: bool = True
    ordinal: int = 0
    metadata: dict[str, _Any_29k_r2] = _field_29k_r2(default_factory=dict)

    @property
    def order_index(self) -> int:
        """Compatibility alias expected by ReplayEngine stage ordering."""
        return self.ordinal

    @property
    def stage_name(self) -> str:
        """Compatibility alias expected by ReplayEngine stage traversal."""
        return self.name

    @property
    def terminal_stage(self) -> bool:
        """Compatibility alias expected by ReplayEngine stage execution records."""
        return bool(self.metadata.get("terminal_stage", False))

    @property
    def executor(self) -> Any:
        """Offline-only callable materialization alias added by Batch 29U."""
        raw_callable = self.metadata.get("executor")
        if callable(raw_callable):
            return raw_callable
        return _offline_replay_stage_callable_materializer_29u(
            stage_name=self.stage_name,
            order_index=self.order_index,
            terminal_stage=self.terminal_stage,
            attr_name="executor",
        )

    @property
    def description(self) -> str:
        """Offline-only compatibility alias expected by ReplayEngine stage records."""
        metadata = getattr(self, "metadata", None)
        if isinstance(metadata, dict):
            for key in ("description", "stage_description", "desc", "label"):
                value = metadata.get(key)
                if value not in (None, ""):
                    return str(value)

        stage_name = getattr(self, "stage_name", None)
        if stage_name not in (None, ""):
            return str(stage_name)

        name = getattr(self, "name", None)
        if name not in (None, ""):
            return str(name)

        order_index = getattr(self, "order_index", None)
        if order_index not in (None, ""):
            return f"offline_replay_stage_{order_index}"

        return "offline_replay_stage"

    def as_dict(self) -> dict[str, _Any_29k_r2]:
        return {
            "name": self.name,
            "stage_id": self.stage_id,
            "enabled": self.enabled,
            "ordinal": self.ordinal,
            "terminal_stage": self.terminal_stage,
            "metadata": dict(self.metadata),
        }

    @property
    def owns_runtime_decisioning(self) -> bool:
        """Compatibility alias for offline replay stage runtime-decision ownership."""
        for attr in ("runtime_decisioning_owner", "owns_decisioning", "decisioning_owner", "runtime_owner"):
            value = getattr(self, attr, None)
            if value is not None:
                return bool(value)
        value = getattr(self, "value", None)
        if isinstance(value, dict):
            for key in ("owns_runtime_decisioning", "runtime_decisioning_owner", "owns_decisioning", "decisioning_owner", "runtime_owner"):
                if key in value and value.get(key) is not None:
                    return bool(value.get(key))
        if isinstance(value, (tuple, list)):
            # Historical offline stage tuples may carry runtime-decision ownership after name/description.
            if len(value) >= 3 and value[2] is not None:
                return bool(value[2])
        return False


@_dataclass_29k_r2(frozen=True)
class OfflineReplayTopologyPlan:
    """Offline topology wrapper exposing .stages expected by ReplayEngine.execute."""

    stages: tuple[OfflineReplayStage, ...]
    source_type: str
    source_repr: str
    metadata: dict[str, _Any_29k_r2] = _field_29k_r2(default_factory=dict)

    @property
    def stage_names(self) -> tuple[str, ...]:
        """Compatibility alias expected by ReplayEngine topology traversal."""
        return tuple(getattr(stage, "stage_name", getattr(stage, "name", str(stage))) for stage in self.stages)

    def __iter__(self):
        return iter(self.stages)

    def __len__(self) -> int:
        return len(self.stages)


    @property
    def scope(self) -> Any:
        """Offline-only compatibility alias expected by ReplayEngine topology traversal."""
        values = getattr(self, "values", None)
        if isinstance(values, dict) and values.get("scope") not in (None, ""):
            return _offline_scope_value_compat_29y(values.get("scope"))

        metadata = getattr(self, "metadata", None)
        if isinstance(metadata, dict) and metadata.get("scope") not in (None, ""):
            return _offline_scope_value_compat_29y(metadata.get("scope"))

        for source_attr in ("source", "source_plan", "source_topology", "topology_plan", "raw_plan"):
            source_obj = getattr(self, source_attr, None)
            source_scope = getattr(source_obj, "scope", None)
            if source_scope not in (None, ""):
                return _offline_scope_value_compat_29y(source_scope)

        dataset_id = None
        if isinstance(values, dict):
            dataset_id = values.get("dataset_id")
        if dataset_id not in (None, ""):
            return _offline_scope_value_compat_29y(f"offline_replay:{dataset_id}")

        return _offline_scope_value_compat_29y("offline_replay")



    @property
    def topology_fingerprint(self) -> str:
        """Offline-only deterministic topology fingerprint expected by ReplayEngine."""
        metadata = getattr(self, "metadata", None)
        if isinstance(metadata, dict):
            for key in ("topology_fingerprint", "fingerprint", "topology_hash", "plan_fingerprint"):
                value = metadata.get(key)
                if value not in (None, ""):
                    return str(value)

        for source_attr in ("source", "source_plan", "source_topology", "topology_plan", "raw_plan"):
            source_obj = getattr(self, source_attr, None)
            source_value = getattr(source_obj, "topology_fingerprint", None)
            if source_value not in (None, ""):
                return str(source_value)

        values = getattr(self, "values", None)
        scope_obj = getattr(self, "scope", None)
        scope_value = getattr(scope_obj, "value", scope_obj)
        stage_rows = []

        for stage in tuple(getattr(self, "stages", ()) or ()):
            stage_rows.append({
                "stage_name": str(getattr(stage, "stage_name", getattr(stage, "name", "")) or ""),
                "description": str(getattr(stage, "description", "") or ""),
                "order_index": getattr(stage, "order_index", None),
                "terminal_stage": bool(getattr(stage, "terminal_stage", False)),
                "owns_runtime_decisioning": bool(getattr(stage, "owns_runtime_decisioning", False)),
            })

        dataset_id = None
        if isinstance(values, dict):
            dataset_id = values.get("dataset_id")

        payload = {
            "schema_version": "offline_replay_topology_fingerprint_29ae_v1",
            "scope": str(scope_value) if scope_value is not None else None,
            "dataset_id": dataset_id,
            "stage_rows": stage_rows,
        }

        import hashlib as _hashlib
        import json as _json

        encoded = _json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
        return "offline_topology_" + _hashlib.sha256(encoded).hexdigest()[:24]

    @property
    def notes(self) -> tuple:
        """Offline-only compatibility alias expected by ReplayEngine topology traversal."""
        registered = _offline_get_registered_topology_notes_29ag_r4_r1(self)
        if registered is not None:
            return registered

        values = getattr(self, "values", None)
        notes, present = _offline_extract_topology_notes_29ag_r4_r1(values)
        if present:
            return notes

        metadata = getattr(self, "metadata", None)
        notes, present = _offline_extract_topology_notes_29ag_r4_r1(metadata)
        if present:
            return notes

        for source_attr in ("source", "source_plan", "source_topology", "topology_plan", "raw_plan"):
            source_obj = getattr(self, source_attr, None)
            source_notes = getattr(source_obj, "notes", None)
            coerced = _offline_coerce_topology_notes_29ag_r4_r1(source_notes)
            if coerced:
                return coerced

        return tuple()



    def as_dict(self) -> dict[str, _Any_29k_r2]:
        return {
            "stages": [stage.as_dict() for stage in self.stages],
            "source_type": self.source_type,
            "source_repr": self.source_repr,
            "metadata": dict(self.metadata),
        }


def _offline_topology_stage_names_29k_r2(source: _Any_29k_r2) -> list[str]:
    names: list[str] = []

    for attr in ("stage_names", "stage_ids", "steps", "nodes"):
        value = getattr(source, attr, None)
        if isinstance(value, (list, tuple)):
            for item in value:
                if isinstance(item, str):
                    names.append(item)
                elif hasattr(item, "name"):
                    names.append(str(getattr(item, "name")))
                elif hasattr(item, "stage_id"):
                    names.append(str(getattr(item, "stage_id")))

    build_method = getattr(source, "build", None)
    if callable(build_method):
        try:
            built = build_method()
            if hasattr(built, "stages"):
                for item in getattr(built, "stages"):
                    if isinstance(item, str):
                        names.append(item)
                    elif hasattr(item, "name"):
                        names.append(str(getattr(item, "name")))
                    elif hasattr(item, "stage_id"):
                        names.append(str(getattr(item, "stage_id")))
        except Exception:
            pass

    normalized: list[str] = []
    for item in names:
        clean = str(item).strip()
        if clean and clean not in normalized:
            normalized.append(clean)

    if normalized:
        return normalized

    return [
        "offline_replay_input_load",
        "offline_replay_feature_projection",
        "offline_replay_strategy_projection",
        "offline_replay_artifact_write",
    ]


def ensure_offline_topology_plan(
    topology_plan: _Any_29k_r2,
    values: dict[str, _Any_29k_r2] | None = None,
) -> tuple[_Any_29k_r2, dict[str, _Any_29k_r2]]:
    """Return a topology object with .stages for offline guarded dry-run only."""

    values = dict(values or {})

    if hasattr(topology_plan, "stages"):
        try:
            stage_count = len(getattr(topology_plan, "stages"))
        except Exception:
            stage_count = None
        _offline_register_topology_notes_29ag_r4_r1(topology_plan, locals().get('values'))
        return topology_plan, {
            "wrapped": False,
            "reason": "topology_plan_already_has_stages",
            "source_type": type(topology_plan).__name__,
            "stage_count": stage_count,
        }

    stage_names = _offline_topology_stage_names_29k_r2(topology_plan)
    stage_count_29s = len(stage_names)
    stages = tuple(
        OfflineReplayStage(
            name=name,
            stage_id=f"{idx:02d}_{name}",
            ordinal=idx,
            metadata={
                "source_type": type(topology_plan).__name__,
                "offline_only": True,
                "source_batch": "29K-R2",
                "terminal_stage": idx == (stage_count_29s - 1),
                "source_batch_terminal_stage_alias": "29S",
            },
        )
        for idx, name in enumerate(stage_names)
    )

    offline_scope_29w_r2 = _offline_topology_scope_from_values_29w_r2(topology_plan, values)
    wrapped = OfflineReplayTopologyPlan(
        stages=stages,
        source_type=type(topology_plan).__name__,
        source_repr=repr(topology_plan)[:2000],
        metadata={
            "scope": offline_scope_29w_r2,
            "source_batch_scope_preservation": "29W-R2",
            "source_batch": "29K-R2",
            "offline_only": True,
            "dataset_id": values.get("dataset_id"),
            "run_id": getattr(values.get("run_context"), "run_id", None),
        },
    )

    _offline_register_topology_notes_29ag_r4_r1(wrapped, locals().get('values'))
    return wrapped, {
        "wrapped": True,
        "reason": "topology_plan_missing_stages_wrapped_offline",
        "source_type": type(topology_plan).__name__,
        "stage_count": len(stages),
        "stage_names": [stage.name for stage in stages],
    }


try:
    __all__ = list(__all__)  # type: ignore[name-defined]
except Exception:
    __all__ = []

for _name_29k_r2 in [
    "OfflineReplayStage",
    "OfflineReplayTopologyPlan",
    "ensure_offline_topology_plan",
]:
    if _name_29k_r2 not in __all__:
        __all__.append(_name_29k_r2)
# ---- End Batch 29K-R2 offline topology stages compatibility shim ----

