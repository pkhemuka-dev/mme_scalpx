"""
app/mme_scalpx/replay/overrides.py

Freeze-grade shadow override layer for the MME-ScalpX Permanent Replay &
Validation Framework.

Override responsibilities
-------------------------
This module owns:
- canonical shadow override contracts
- override pack validation
- deterministic override serialization
- merge helpers for explicit replay-only shadow overrides

This module does not own:
- experiment orchestration
- replay execution
- dataset selection
- doctrine mutation
- live runtime settings mutation
- report interpretation

Design rules
------------
- overrides are shadow-only unless explicitly proven otherwise elsewhere
- overrides must be explicit, auditable, and serializable
- no hidden mutation of baseline truth
- override application must be deterministic
- nested override merging must be rule-based, not ad hoc
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


class ReplayOverridesError(RuntimeError):
    """Base exception for replay override failures."""


class ReplayOverridesValidationError(ReplayOverridesError):
    """Raised when override packs or override payloads are invalid."""


@dataclass(frozen=True, slots=True)
class ReplayOverrideEntry:
    """
    Canonical one-key override entry.
    """

    path: str
    value: Any
    reason: str


@dataclass(frozen=True, slots=True)
class ReplayOverridePack:
    """
    Canonical shadow override pack.
    """

    pack_id: str
    label: str
    entries: tuple[ReplayOverrideEntry, ...]
    notes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class ReplayOverrideApplyResult:
    """
    Canonical result of applying an override pack.
    """

    pack_id: str
    label: str
    changed_paths: tuple[str, ...]
    payload: Mapping[str, Any]
    notes: tuple[str, ...] = field(default_factory=tuple)


class ReplayOverridesManager:
    """
    Freeze-grade replay overrides manager.
    """

    def validate_pack(self, pack: ReplayOverridePack) -> None:
        _validate_override_pack(pack)

    def apply_pack(
        self,
        *,
        base_payload: Mapping[str, Any],
        override_pack: ReplayOverridePack,
        notes: Sequence[str] = (),
    ) -> ReplayOverrideApplyResult:
        _validate_override_pack(override_pack)
        _validate_mapping_payload(base_payload, name="base_payload")

        merged = _deep_copy_mapping(base_payload)
        changed_paths: list[str] = []

        for entry in override_pack.entries:
            _apply_entry_in_place(merged, entry)
            changed_paths.append(entry.path)

        return ReplayOverrideApplyResult(
            pack_id=override_pack.pack_id,
            label=override_pack.label,
            changed_paths=tuple(changed_paths),
            payload=merged,
            notes=tuple(notes) + override_pack.notes,
        )


def validate_override_pack(pack: ReplayOverridePack) -> None:
    _validate_override_pack(pack)


def override_entry_to_dict(entry: ReplayOverrideEntry) -> dict[str, Any]:
    return {
        "path": entry.path,
        "value": _json_safe_value(entry.value),
        "reason": entry.reason,
    }


def override_pack_to_dict(pack: ReplayOverridePack) -> dict[str, Any]:
    return {
        "pack_id": pack.pack_id,
        "label": pack.label,
        "entries": [override_entry_to_dict(item) for item in pack.entries],
        "notes": list(pack.notes),
    }


def override_apply_result_to_dict(
    result: ReplayOverrideApplyResult,
) -> dict[str, Any]:
    return {
        "pack_id": result.pack_id,
        "label": result.label,
        "changed_paths": list(result.changed_paths),
        "payload": _json_safe_value(result.payload),
        "notes": list(result.notes),
    }


def build_override_pack(
    *,
    pack_id: str,
    label: str,
    entries: Sequence[ReplayOverrideEntry],
    notes: Sequence[str] = (),
) -> ReplayOverridePack:
    pack = ReplayOverridePack(
        pack_id=pack_id,
        label=label,
        entries=tuple(entries),
        notes=tuple(notes),
    )
    _validate_override_pack(pack)
    return pack


def merge_shadow_payload(
    *,
    base_payload: Mapping[str, Any],
    override_pack: ReplayOverridePack,
    notes: Sequence[str] = (),
) -> ReplayOverrideApplyResult:
    manager = ReplayOverridesManager()
    return manager.apply_pack(
        base_payload=base_payload,
        override_pack=override_pack,
        notes=notes,
    )


def _validate_override_pack(pack: ReplayOverridePack) -> None:
    if not isinstance(pack.pack_id, str) or not pack.pack_id.strip():
        raise ReplayOverridesValidationError(
            f"pack_id must be non-empty string, got {pack.pack_id!r}"
        )
    if not isinstance(pack.label, str) or not pack.label.strip():
        raise ReplayOverridesValidationError(
            f"label must be non-empty string, got {pack.label!r}"
        )
    if not pack.entries:
        raise ReplayOverridesValidationError("override pack must contain at least one entry")

    seen_paths: set[str] = set()
    for entry in pack.entries:
        _validate_override_entry(entry)
        if entry.path in seen_paths:
            raise ReplayOverridesValidationError(
                f"duplicate override path in pack {pack.pack_id!r}: {entry.path!r}"
            )
        seen_paths.add(entry.path)

    for note in pack.notes:
        if not isinstance(note, str):
            raise ReplayOverridesValidationError(
                f"override pack note must be string, got {note!r}"
            )


def _validate_override_entry(entry: ReplayOverrideEntry) -> None:
    if not isinstance(entry.path, str) or not entry.path.strip():
        raise ReplayOverridesValidationError(
            f"override entry path must be non-empty string, got {entry.path!r}"
        )
    if entry.path.startswith(".") or entry.path.endswith(".") or ".." in entry.path:
        raise ReplayOverridesValidationError(
            f"override entry path must be a clean dotted path, got {entry.path!r}"
        )
    if not isinstance(entry.reason, str) or not entry.reason.strip():
        raise ReplayOverridesValidationError(
            f"override entry reason must be non-empty string, got {entry.reason!r}"
        )


def _validate_mapping_payload(payload: Mapping[str, Any], *, name: str) -> None:
    if not isinstance(payload, Mapping):
        raise ReplayOverridesValidationError(
            f"{name} must be mapping, got {type(payload)!r}"
        )


def _apply_entry_in_place(target: dict[str, Any], entry: ReplayOverrideEntry) -> None:
    parts = entry.path.split(".")
    cursor: dict[str, Any] = target

    for part in parts[:-1]:
        current = cursor.get(part)
        if current is None:
            current = {}
            cursor[part] = current
        elif not isinstance(current, dict):
            raise ReplayOverridesValidationError(
                f"cannot descend into non-mapping path segment {part!r} for {entry.path!r}"
            )
        cursor = current

    cursor[parts[-1]] = _deep_copy_value(entry.value)


def _deep_copy_mapping(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {str(key): _deep_copy_value(value) for key, value in payload.items()}


def _deep_copy_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _deep_copy_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_deep_copy_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_deep_copy_value(item) for item in value)
    return value


def _json_safe_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _json_safe_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe_value(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe_value(item) for item in value]
    return value


__all__ = [
    "ReplayOverridesError",
    "ReplayOverridesValidationError",
    "ReplayOverrideEntry",
    "ReplayOverridePack",
    "ReplayOverrideApplyResult",
    "ReplayOverridesManager",
    "validate_override_pack",
    "override_entry_to_dict",
    "override_pack_to_dict",
    "override_apply_result_to_dict",
    "build_override_pack",
    "merge_shadow_payload",
]
