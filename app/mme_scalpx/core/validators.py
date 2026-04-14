"""
app/mme_scalpx/core/validators.py

Tiny shared validation primitives for the ScalpX MME platform spine.

Purpose
-------
This module OWNS:
- low-level scalar/type validation helpers
- tiny collection/mapping validation helpers
- small coercion/normalization helpers used by spine modules
- deterministic, dependency-light validation behavior

This module DOES NOT own:
- Redis naming contracts
- runtime settings schema
- clock policy
- schema/business model rules
- serialization rules
- Redis client lifecycle
- trading logic

Core design rules
-----------------
- Keep this module extremely small and stdlib-only.
- No imports from names.py, settings.py, models.py, codec.py, redisx.py, or main.py.
- No business/domain-specific rules.
- Only generic scalar/type/collection validation belongs here.
- Helpers should be deterministic, explicit, and side-effect free.
- Callers own their own exception types; this module raises ValidationError only.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Final, Mapping, Sequence


# ============================================================================
# Constants
# ============================================================================

TRUE_VALUES: Final[frozenset[str]] = frozenset({"1", "true", "yes", "y", "on"})
FALSE_VALUES: Final[frozenset[str]] = frozenset({"0", "false", "no", "n", "off"})


# ============================================================================
# Exceptions
# ============================================================================


class ValidationError(ValueError):
    """Raised when a low-level validation helper fails."""


# ============================================================================
# Core failure helpers
# ============================================================================


def fail(message: str) -> None:
    """Raise ValidationError with the provided message."""
    raise ValidationError(message)


def require(condition: bool, message: str) -> None:
    """Raise ValidationError when condition is false."""
    if not condition:
        fail(message)


# ============================================================================
# Primitive validators
# ============================================================================


def require_non_empty_str(value: str, *, field_name: str) -> str:
    """Validate and return a stripped non-empty string."""
    if not isinstance(value, str):
        fail(f"{field_name} must be str, got {type(value).__name__}")
    cleaned = value.strip()
    if not cleaned:
        fail(f"{field_name} must be non-empty")
    return cleaned


def optional_non_empty_str(value: str | None, *, field_name: str) -> str | None:
    """Validate an optional string; return stripped value or None."""
    if value is None:
        return None
    return require_non_empty_str(value, field_name=field_name)


def normalize_optional_str(value: str | None) -> str | None:
    """Strip a string and collapse blank strings to None."""
    if value is None:
        return None
    if not isinstance(value, str):
        fail(f"value must be str | None, got {type(value).__name__}")
    cleaned = value.strip()
    return cleaned or None


def require_bool(value: bool, *, field_name: str) -> bool:
    """Validate a bool."""
    if not isinstance(value, bool):
        fail(f"{field_name} must be bool, got {type(value).__name__}")
    return value


def require_bytes(value: bytes, *, field_name: str) -> bytes:
    """Validate bytes."""
    if not isinstance(value, bytes):
        fail(f"{field_name} must be bytes, got {type(value).__name__}")
    return value


def require_int(
    value: int,
    *,
    field_name: str,
    min_value: int | None = None,
    max_value: int | None = None,
) -> int:
    """Validate an int with optional inclusive bounds."""
    if not isinstance(value, int) or isinstance(value, bool):
        fail(f"{field_name} must be int, got {type(value).__name__}")
    if min_value is not None and value < min_value:
        fail(f"{field_name} must be >= {min_value}, got {value}")
    if max_value is not None and value > max_value:
        fail(f"{field_name} must be <= {max_value}, got {value}")
    return value


def require_non_negative_int(value: int, *, field_name: str) -> int:
    """Validate an integer >= 0."""
    return require_int(value, field_name=field_name, min_value=0)


def require_positive_int(value: int, *, field_name: str) -> int:
    """Validate an integer >= 1."""
    return require_int(value, field_name=field_name, min_value=1)


def require_float(
    value: float | int,
    *,
    field_name: str,
    min_value: float | None = None,
    max_value: float | None = None,
    finite: bool = True,
    strictly_positive: bool = False,
) -> float:
    """
    Validate a numeric value and normalize it to float.

    Notes
    -----
    - bool is explicitly rejected even though bool is a subclass of int.
    - By default, non-finite values are rejected.
    """
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        fail(f"{field_name} must be float, got {type(value).__name__}")

    normalized = float(value)

    if finite and not math.isfinite(normalized):
        fail(f"{field_name} must be finite, got {normalized!r}")

    if strictly_positive and normalized <= 0.0:
        fail(f"{field_name} must be > 0, got {normalized}")

    if min_value is not None and normalized < min_value:
        fail(f"{field_name} must be >= {min_value}, got {normalized}")

    if max_value is not None and normalized > max_value:
        fail(f"{field_name} must be <= {max_value}, got {normalized}")

    return normalized


def require_non_negative_float(value: float | int, *, field_name: str) -> float:
    """Validate a float >= 0."""
    return require_float(value, field_name=field_name, min_value=0.0)


def require_positive_float(value: float | int, *, field_name: str) -> float:
    """Validate a float > 0."""
    return require_float(value, field_name=field_name, strictly_positive=True)


# ============================================================================
# Choice / parsing helpers
# ============================================================================


def require_literal(
    value: str,
    *,
    field_name: str,
    allowed: Sequence[str],
) -> str:
    """Validate that a non-empty string belongs to the allowed literal set."""
    normalized = require_non_empty_str(value, field_name=field_name)
    if normalized not in allowed:
        fail(f"{field_name} must be one of {tuple(allowed)}, got {normalized!r}")
    return normalized


def parse_bool(
    raw: str | None,
    *,
    field_name: str,
    default: bool | None = None,
) -> bool:
    """Parse a boolean from a string with optional default."""
    if raw is None:
        if default is None:
            fail(f"{field_name} is required")
        return default

    if not isinstance(raw, str):
        fail(f"{field_name} must be str | None, got {type(raw).__name__}")

    value = raw.strip().lower()
    if not value:
        if default is None:
            fail(f"{field_name} must be non-empty")
        return default

    if value in TRUE_VALUES:
        return True
    if value in FALSE_VALUES:
        return False

    fail(
        f"{field_name} must be one of "
        f"{sorted(TRUE_VALUES | FALSE_VALUES)}, got {raw!r}"
    )


def parse_int(
    raw: str | None,
    *,
    field_name: str,
    default: int | None = None,
    min_value: int | None = None,
    max_value: int | None = None,
) -> int:
    """Parse an integer from a string with optional default and bounds."""
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        if default is None:
            fail(f"{field_name} is required")
        return require_int(
            default,
            field_name=field_name,
            min_value=min_value,
            max_value=max_value,
        )

    if not isinstance(raw, str):
        fail(f"{field_name} must be str | None, got {type(raw).__name__}")

    try:
        value = int(raw.strip())
    except ValueError as exc:
        raise ValidationError(f"{field_name} must be int, got {raw!r}") from exc

    return require_int(
        value,
        field_name=field_name,
        min_value=min_value,
        max_value=max_value,
    )


def parse_float(
    raw: str | None,
    *,
    field_name: str,
    default: float | None = None,
    min_value: float | None = None,
    max_value: float | None = None,
    finite: bool = True,
    strictly_positive: bool = False,
) -> float:
    """Parse a float from a string with optional default and validation."""
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        if default is None:
            fail(f"{field_name} is required")
        return require_float(
            default,
            field_name=field_name,
            min_value=min_value,
            max_value=max_value,
            finite=finite,
            strictly_positive=strictly_positive,
        )

    if not isinstance(raw, str):
        fail(f"{field_name} must be str | None, got {type(raw).__name__}")

    try:
        value = float(raw.strip())
    except ValueError as exc:
        raise ValidationError(f"{field_name} must be float, got {raw!r}") from exc

    return require_float(
        value,
        field_name=field_name,
        min_value=min_value,
        max_value=max_value,
        finite=finite,
        strictly_positive=strictly_positive,
    )


def parse_choice(
    raw: str | None,
    *,
    field_name: str,
    allowed: Sequence[str],
    default: str | None = None,
    casefold: bool = True,
) -> str:
    """
    Parse a string choice from an allowed set.

    Returns the canonical item from `allowed`, preserving the exact allowed value.
    """
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        if default is None:
            fail(f"{field_name} is required")
        candidate = default
    else:
        if not isinstance(raw, str):
            fail(f"{field_name} must be str | None, got {type(raw).__name__}")
        candidate = raw.strip()

    normalized = candidate.lower() if casefold else candidate
    allowed_lookup = {
        (item.lower() if casefold else item): item for item in allowed
    }

    if normalized not in allowed_lookup:
        fail(f"{field_name} must be one of {tuple(allowed)}, got {candidate!r}")

    return allowed_lookup[normalized]


# ============================================================================
# Mapping / sequence validators
# ============================================================================


def require_mapping(
    value: Mapping[str, Any],
    *,
    field_name: str,
) -> dict[str, Any]:
    """
    Validate a mapping and normalize keys to stripped non-empty strings.

    Keys are converted via str(key) before validation so callers get one stable
    output shape.
    """
    if not isinstance(value, Mapping):
        fail(f"{field_name} must be mapping, got {type(value).__name__}")

    normalized: dict[str, Any] = {}
    for key, item in value.items():
        normalized_key = require_non_empty_str(str(key), field_name=f"{field_name}.key")
        normalized[normalized_key] = item
    return normalized


def require_non_empty_mapping(
    value: Mapping[str, Any],
    *,
    field_name: str,
) -> dict[str, Any]:
    """Validate a non-empty mapping and normalize keys."""
    normalized = require_mapping(value, field_name=field_name)
    if not normalized:
        fail(f"{field_name} must be non-empty")
    return normalized


def require_sequence(
    value: Sequence[Any],
    *,
    field_name: str,
) -> Sequence[Any]:
    """Validate a generic sequence, excluding str/bytes-like values."""
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        fail(f"{field_name} must be sequence, got {type(value).__name__}")
    return value


def require_non_empty_sequence(
    value: Sequence[Any],
    *,
    field_name: str,
) -> Sequence[Any]:
    """Validate a non-empty generic sequence."""
    source = require_sequence(value, field_name=field_name)
    if len(source) == 0:
        fail(f"{field_name} must be non-empty")
    return source


def require_sequence_of_str(
    value: Sequence[str],
    *,
    field_name: str,
) -> tuple[str, ...]:
    """Validate a sequence of non-empty strings and return a normalized tuple."""
    source = require_sequence(value, field_name=field_name)
    return tuple(
        require_non_empty_str(item, field_name=f"{field_name}[]")
        for item in source
    )


def assert_no_duplicates(
    values: Sequence[str],
    *,
    label: str,
) -> None:
    """Raise when duplicate string values are present."""
    seen: set[str] = set()
    duplicates: set[str] = set()

    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)

    if duplicates:
        fail(f"Duplicate {label} detected: {', '.join(sorted(duplicates))}")


# ============================================================================
# Path helpers
# ============================================================================


def parse_path(raw: str | None, *, field_name: str) -> Path | None:
    """Parse an optional filesystem path from a string."""
    value = normalize_optional_str(raw)
    if value is None:
        return None

    if "\x00" in value:
        fail(f"{field_name} contains null byte")

    return Path(value).expanduser()


def require_existing_file(path: Path, *, field_name: str) -> Path:
    """Validate that a Path exists and is a file."""
    if not isinstance(path, Path):
        fail(f"{field_name} must be Path, got {type(path).__name__}")
    if not path.exists():
        fail(f"{field_name} does not exist: {path}")
    if not path.is_file():
        fail(f"{field_name} is not a file: {path}")
    return path


def require_existing_dir(path: Path, *, field_name: str) -> Path:
    """Validate that a Path exists and is a directory."""
    if not isinstance(path, Path):
        fail(f"{field_name} must be Path, got {type(path).__name__}")
    if not path.exists():
        fail(f"{field_name} does not exist: {path}")
    if not path.is_dir():
        fail(f"{field_name} is not a directory: {path}")
    return path


# ============================================================================
# Public exports
# ============================================================================

__all__ = [
    "FALSE_VALUES",
    "TRUE_VALUES",
    "ValidationError",
    "assert_no_duplicates",
    "fail",
    "normalize_optional_str",
    "optional_non_empty_str",
    "parse_bool",
    "parse_choice",
    "parse_float",
    "parse_int",
    "parse_path",
    "require",
    "require_bool",
    "require_bytes",
    "require_existing_dir",
    "require_existing_file",
    "require_float",
    "require_int",
    "require_literal",
    "require_mapping",
    "require_non_empty_mapping",
    "require_non_empty_sequence",
    "require_non_empty_str",
    "require_non_negative_float",
    "require_non_negative_int",
    "require_positive_float",
    "require_positive_int",
    "require_sequence",
    "require_sequence_of_str",
]