from __future__ import annotations

"""
app/mme_scalpx/research_capture/utils.py

Frozen utility layer for the MME research data capture chapter.

Purpose
-------
This module owns small, deterministic helper utilities shared across the
research-capture chapter. These helpers are deliberately generic and
side-effect-light so that other modules can reuse them without duplicating
basic validation, serialization, and atomic file-write logic.

Owns
----
- basic scalar validation helpers
- frozen mapping / tuple helpers
- stable JSON serialization helpers
- atomic text / JSON file writing
- canonical session-date normalization
- small ordered-sequence helpers

Does not own
------------
- broker IO
- Redis IO
- parquet IO
- archive writing policy
- normalization logic
- enrichment logic
- production strategy doctrine

Design laws
-----------
- helpers must be deterministic and narrow
- helpers must not import heavy optional dependencies
- helpers must avoid hidden global state
- helpers must preserve stable output ordering where possible
"""

import json
import os
from datetime import date, datetime, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence, TypeVar

T = TypeVar("T")


def ensure_non_empty_str(name: str, value: str) -> str:
    """
    Validate that a value is a non-empty stripped string.
    """
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty str")
    return value


def ensure_bool(name: str, value: bool) -> bool:
    """
    Validate that a value is bool.
    """
    if not isinstance(value, bool):
        raise TypeError(f"{name} must be bool")
    return value


def ensure_int(name: str, value: int) -> int:
    """
    Validate that a value is int but not bool.
    """
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be int")
    return value


def ensure_float_like(name: str, value: float | int) -> float:
    """
    Validate and coerce a numeric value into float.
    """
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TypeError(f"{name} must be float-like")
    return float(value)


def freeze_mapping(values: Mapping[str, Any] | None = None) -> Mapping[str, Any]:
    """
    Return an immutable shallow copy of a mapping.
    """
    if values is None:
        return MappingProxyType({})
    return MappingProxyType(dict(values))


def freeze_str_tuple(values: Sequence[str] | None = None) -> tuple[str, ...]:
    """
    Return an immutable tuple[str, ...].
    """
    if values is None:
        return ()
    result = tuple(values)
    for value in result:
        if not isinstance(value, str):
            raise TypeError("expected a sequence of strings")
    return result


def freeze_tuple(values: Sequence[T] | None = None) -> tuple[T, ...]:
    """
    Return an immutable tuple copy of a sequence.
    """
    if values is None:
        return ()
    return tuple(values)


def dedupe_preserve_order(values: Iterable[T]) -> tuple[T, ...]:
    """
    Remove duplicates while preserving first-seen order.
    """
    seen: set[Any] = set()
    result: list[T] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return tuple(result)


def utc_now_iso() -> str:
    """
    Return the current UTC time in ISO-8601 format with timezone info.
    """
    return datetime.now(timezone.utc).isoformat()


def normalize_session_date(value: str | date | datetime) -> str:
    """
    Normalize a session date input into YYYY-MM-DD.
    """
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            raise ValueError("session_date must be non-empty")
        normalized = stripped.replace("/", "-")
        if "T" in normalized:
            normalized = normalized.split("T", 1)[0]
        if " " in normalized and len(normalized) >= 10:
            normalized = normalized[:10]
        if len(normalized) != 10:
            raise ValueError(f"session_date has invalid shape: {value!r}")
        return normalized
    raise TypeError(f"unsupported session_date type: {type(value).__name__}")


def ensure_parent_dir(path: str | Path) -> Path:
    """
    Ensure the parent directory exists and return Path.
    """
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    return path_obj


def stable_json_dumps(payload: Any, *, indent: int = 2) -> str:
    """
    Serialize JSON deterministically with sorted keys and final newline omitted.
    """
    return json.dumps(
        payload,
        indent=indent,
        sort_keys=True,
        ensure_ascii=False,
        default=str,
    )


def atomic_write_text(path: str | Path, text: str, *, encoding: str = "utf-8") -> Path:
    """
    Atomically write text to a file via a temporary sibling file.
    """
    path_obj = ensure_parent_dir(path)
    tmp_path = path_obj.with_suffix(path_obj.suffix + ".tmp")
    tmp_path.write_text(text, encoding=encoding)
    os.replace(tmp_path, path_obj)
    return path_obj


def atomic_write_json(path: str | Path, payload: Any, *, indent: int = 2) -> Path:
    """
    Atomically write JSON with stable serialization and trailing newline.
    """
    text = stable_json_dumps(payload, indent=indent) + "\n"
    return atomic_write_text(path, text, encoding="utf-8")


def read_json(path: str | Path) -> Any:
    """
    Read and parse a JSON file.
    """
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(path_obj.as_posix())
    return json.loads(path_obj.read_text(encoding="utf-8"))


def path_exists(path: str | Path) -> bool:
    """
    Return True if a filesystem path exists.
    """
    return Path(path).exists()


__all__ = [
    "atomic_write_json",
    "atomic_write_text",
    "dedupe_preserve_order",
    "ensure_bool",
    "ensure_float_like",
    "ensure_int",
    "ensure_non_empty_str",
    "ensure_parent_dir",
    "freeze_mapping",
    "freeze_str_tuple",
    "freeze_tuple",
    "normalize_session_date",
    "path_exists",
    "read_json",
    "stable_json_dumps",
    "utc_now_iso",
]

# =============================================================================
# Batch 17 freeze hardening: path containment and atomic write firewall
# =============================================================================

_BATCH17_RESEARCH_CAPTURE_GUARD_VERSION = "1"


def ensure_path_within_root(path: str | Path, root: str | Path, *, label: str) -> Path:
    """Resolve and prove that path is under root."""
    resolved_path = Path(path).resolve()
    resolved_root = Path(root).resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(
            f"{label} escapes root: {resolved_path.as_posix()} not under {resolved_root.as_posix()}"
        ) from exc
    return resolved_path


def ensure_path_within_any_root(
    path: str | Path,
    roots: Sequence[str | Path],
    *,
    label: str,
) -> Path:
    resolved_path = Path(path).resolve()
    errors: list[str] = []
    for root in roots:
        try:
            return ensure_path_within_root(resolved_path, root, label=label)
        except ValueError as exc:
            errors.append(str(exc))
    raise ValueError(f"{label} escapes all allowed roots: {resolved_path.as_posix()} errors={errors!r}")


def reject_unsafe_path_fragment(value: str, *, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    raw = value.strip()
    candidate = Path(raw)
    if candidate.is_absolute():
        raise ValueError(f"{label} must be relative, got absolute path: {raw!r}")
    if any(part in {"..", ""} for part in candidate.parts):
        raise ValueError(f"{label} contains unsafe path segment: {raw!r}")
    return raw


def research_capture_project_root() -> Path:
    return Path.cwd().resolve()


def research_capture_run_root(project_root: str | Path | None = None) -> Path:
    root = Path(project_root).resolve() if project_root is not None else research_capture_project_root()
    return ensure_path_within_root(root / "run", root, label="research_capture.run_root")


def research_capture_archive_root(project_root: str | Path | None = None) -> Path:
    root = Path(project_root).resolve() if project_root is not None else research_capture_project_root()
    return ensure_path_within_root(root / "run" / "research_capture", root, label="research_capture.archive_root")


def _batch17_write_text_atomic(path: Path, text: str) -> None:
    import tempfile as _batch17_tempfile
    path.parent.mkdir(parents=True, exist_ok=True)
    with _batch17_tempfile.NamedTemporaryFile(
        "w",
        delete=False,
        encoding="utf-8",
        dir=str(path.parent),
    ) as handle:
        handle.write(text)
        temp_path = Path(handle.name)
    os.replace(temp_path, path)


def _batch17_write_json_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    _batch17_write_text_atomic(
        path,
        json.dumps(dict(payload), indent=2, sort_keys=True, ensure_ascii=False) + "\n",
    )


_BATCH17_ORIGINAL_ATOMIC_WRITE_TEXT = globals().get("atomic_write_text")
_BATCH17_ORIGINAL_ATOMIC_WRITE_JSON = globals().get("atomic_write_json")


def atomic_write_text(
    path: str | Path,
    text: str,
    *,
    root: str | Path | None = None,
    label: str = "atomic_write_text",
) -> Path:
    resolved_root = Path(root).resolve() if root is not None else research_capture_project_root()
    resolved_path = ensure_path_within_root(path, resolved_root, label=label)
    if callable(_BATCH17_ORIGINAL_ATOMIC_WRITE_TEXT):
        try:
            _BATCH17_ORIGINAL_ATOMIC_WRITE_TEXT(resolved_path, text)
        except TypeError:
            _batch17_write_text_atomic(resolved_path, text)
    else:
        _batch17_write_text_atomic(resolved_path, text)
    return resolved_path


def atomic_write_json(
    path: str | Path,
    payload: Mapping[str, Any],
    *,
    root: str | Path | None = None,
    label: str = "atomic_write_json",
) -> Path:
    resolved_root = Path(root).resolve() if root is not None else research_capture_project_root()
    resolved_path = ensure_path_within_root(path, resolved_root, label=label)
    if callable(_BATCH17_ORIGINAL_ATOMIC_WRITE_JSON):
        try:
            _BATCH17_ORIGINAL_ATOMIC_WRITE_JSON(resolved_path, dict(payload))
        except TypeError:
            _batch17_write_json_atomic(resolved_path, payload)
    else:
        _batch17_write_json_atomic(resolved_path, payload)
    return resolved_path
