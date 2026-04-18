from __future__ import annotations

"""
app/mme_scalpx/research_capture/partitioning.py

Frozen partitioning layer for the MME research data capture chapter.

Purpose
-------
This module owns deterministic construction of canonical archive partition
paths for research-capture datasets. It converts a capture record or canonical
row mapping into a stable session-root path, dataset partition directory, and
relative parquet file path.

Owns
----
- partition-column validation
- partition-value normalization and sanitization
- canonical session-root construction
- canonical dataset partition directory construction
- immutable partition-plan objects for archive writing

Does not own
------------
- file writing
- parquet writing
- broker IO
- Redis IO
- replay logic
- production strategy doctrine

Design laws
-----------
- partitioning must be deterministic and side-effect free
- session_date owns the session root
- archive paths must be broker-agnostic at the schema level
- raw provenance remains in the row payload, not in path heuristics
- path building must be stable across repeated runs for the same input
"""

from dataclasses import dataclass
from pathlib import PurePosixPath
from types import MappingProxyType
from typing import Any, Mapping, Sequence
import re

from app.mme_scalpx.research_capture.contracts import (
    ARCHIVE_OUTPUT_FILENAMES,
    ARCHIVE_ROOT_RELATIVE,
    FIELD_SPECS_BY_NAME,
    PRIMARY_PARTITIONS,
    SECONDARY_PARTITIONS,
)
from app.mme_scalpx.research_capture.models import CaptureDatasetName, CaptureRecord

DEFAULT_PARTITION_COLUMNS: tuple[str, ...] = tuple(PRIMARY_PARTITIONS + SECONDARY_PARTITIONS)

NULL_PARTITION_TOKEN = "__null__"
EMPTY_STRING_PARTITION_TOKEN = "__empty__"
TRUE_PARTITION_TOKEN = "true"
FALSE_PARTITION_TOKEN = "false"

_SAFE_TOKEN_RE = re.compile(r"[^A-Za-z0-9._-]+")


def _ensure_non_empty_str(name: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty str")
    return value


def _ensure_known_field(name: str) -> str:
    _ensure_non_empty_str("partition_field", name)
    if name not in FIELD_SPECS_BY_NAME:
        raise KeyError(f"Unknown research-capture field used for partitioning: {name}")
    return name


def _normalize_dataset(dataset: CaptureDatasetName | str) -> CaptureDatasetName:
    if isinstance(dataset, CaptureDatasetName):
        return dataset
    if not isinstance(dataset, str):
        raise TypeError("dataset must be CaptureDatasetName or str")
    try:
        return CaptureDatasetName(dataset)
    except ValueError as exc:
        raise ValueError(f"Unknown capture dataset: {dataset!r}") from exc


def _row_from_input(record_or_row: CaptureRecord | Mapping[str, Any]) -> Mapping[str, Any]:
    if isinstance(record_or_row, CaptureRecord):
        return MappingProxyType(record_or_row.to_archive_row(include_none=True))
    if not isinstance(record_or_row, Mapping):
        raise TypeError("record_or_row must be CaptureRecord or Mapping[str, Any]")
    return MappingProxyType(dict(record_or_row))


def sanitize_partition_token(value: str) -> str:
    """
    Sanitize one partition token into a filesystem-safe stable form.

    Rules
    -----
    - trim leading/trailing whitespace
    - replace unsupported characters with "_"
    - collapse repeated unsafe runs into a single "_"
    - strip leading/trailing underscores after replacement
    - preserve case for readability
    """
    trimmed = value.strip()
    if not trimmed:
        return EMPTY_STRING_PARTITION_TOKEN
    sanitized = _SAFE_TOKEN_RE.sub("_", trimmed).strip("_")
    return sanitized or EMPTY_STRING_PARTITION_TOKEN


def normalize_partition_value(value: Any) -> str:
    """
    Normalize one partition value into a stable sanitized token.
    """
    if value is None:
        return NULL_PARTITION_TOKEN
    if isinstance(value, bool):
        return TRUE_PARTITION_TOKEN if value else FALSE_PARTITION_TOKEN
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        # Preserve a stable, readable numeric form without locale effects.
        return format(value, ".15g")
    if isinstance(value, str):
        return sanitize_partition_token(value)
    return sanitize_partition_token(str(value))


def canonical_partition_columns(
    partition_columns: Sequence[str] | None = None,
) -> tuple[str, ...]:
    """
    Return validated canonical partition columns.

    Default order follows the frozen contract:
    PRIMARY_PARTITIONS + SECONDARY_PARTITIONS
    """
    columns = DEFAULT_PARTITION_COLUMNS if partition_columns is None else tuple(partition_columns)
    if not columns:
        raise ValueError("partition_columns must be non-empty")

    seen: set[str] = set()
    normalized: list[str] = []
    for name in columns:
        field_name = _ensure_known_field(name)
        if field_name in seen:
            raise ValueError(f"Duplicate partition column: {field_name}")
        seen.add(field_name)
        normalized.append(field_name)

    return tuple(normalized)


def build_partition_value_map(
    record_or_row: CaptureRecord | Mapping[str, Any],
    *,
    partition_columns: Sequence[str] | None = None,
    include_unlisted_session_date: bool = True,
) -> Mapping[str, Any]:
    """
    Build raw partition values for the requested columns.

    session_date is always required by the archive session-root convention.
    """
    row = _row_from_input(record_or_row)
    columns = canonical_partition_columns(partition_columns)

    if include_unlisted_session_date and "session_date" not in columns:
        columns = ("session_date",) + columns

    if "session_date" not in row or row["session_date"] in (None, ""):
        raise ValueError("partitioning requires a non-empty session_date")

    values: dict[str, Any] = {}
    for name in columns:
        if name not in row:
            raise KeyError(f"Missing partition field in row: {name}")
        values[name] = row[name]
    return MappingProxyType(values)


def build_encoded_partition_value_map(
    record_or_row: CaptureRecord | Mapping[str, Any],
    *,
    partition_columns: Sequence[str] | None = None,
    include_unlisted_session_date: bool = True,
) -> Mapping[str, str]:
    """
    Build encoded partition values using normalized/sanitized tokens.
    """
    raw_values = build_partition_value_map(
        record_or_row,
        partition_columns=partition_columns,
        include_unlisted_session_date=include_unlisted_session_date,
    )
    encoded = {name: normalize_partition_value(value) for name, value in raw_values.items()}
    return MappingProxyType(encoded)


def build_session_archive_root(
    record_or_row: CaptureRecord | Mapping[str, Any],
    *,
    archive_root_relative: str = ARCHIVE_ROOT_RELATIVE,
) -> str:
    """
    Build the canonical session archive root:

        run/research_capture/<session_date>
    """
    row = _row_from_input(record_or_row)
    session_date = row.get("session_date")
    if session_date is None:
        raise ValueError("session_date is required to build the session archive root")
    session_token = normalize_partition_value(session_date)
    root = PurePosixPath(archive_root_relative) / session_token
    return root.as_posix()


def build_dataset_partition_dir(
    dataset: CaptureDatasetName | str,
    record_or_row: CaptureRecord | Mapping[str, Any],
    *,
    partition_columns: Sequence[str] | None = None,
    session_date_in_root: bool = True,
) -> str:
    """
    Build the dataset-relative partition directory.

    Example shape:
        ticks_opt/instrument_type=CE/underlying_symbol=NIFTY/expiry=2026-04-23/option_type=CE/strike=23500

    session_date is omitted from the dataset partition directory by default
    because it already owns the session root.
    """
    dataset_name = _normalize_dataset(dataset)
    encoded_values = build_encoded_partition_value_map(
        record_or_row,
        partition_columns=partition_columns,
        include_unlisted_session_date=True,
    )

    segments = [dataset_name.value]
    for key, value in encoded_values.items():
        if session_date_in_root and key == "session_date":
            continue
        segments.append(f"{key}={value}")

    return PurePosixPath(*segments).as_posix()


def build_dataset_relative_file_path(
    dataset: CaptureDatasetName | str,
    record_or_row: CaptureRecord | Mapping[str, Any],
    *,
    file_name: str | None = None,
    partition_columns: Sequence[str] | None = None,
    session_date_in_root: bool = True,
) -> str:
    """
    Build the dataset-relative parquet file path.

    Example:
        ticks_opt/instrument_type=CE/.../ticks_opt.parquet
    """
    dataset_name = _normalize_dataset(dataset)
    actual_file_name = ARCHIVE_OUTPUT_FILENAMES[dataset_name.value] if file_name is None else _ensure_non_empty_str("file_name", file_name)
    relative_dir = build_dataset_partition_dir(
        dataset_name,
        record_or_row,
        partition_columns=partition_columns,
        session_date_in_root=session_date_in_root,
    )
    return (PurePosixPath(relative_dir) / actual_file_name).as_posix()


def build_archive_file_path(
    dataset: CaptureDatasetName | str,
    record_or_row: CaptureRecord | Mapping[str, Any],
    *,
    archive_root_relative: str = ARCHIVE_ROOT_RELATIVE,
    file_name: str | None = None,
    partition_columns: Sequence[str] | None = None,
    session_date_in_root: bool = True,
) -> str:
    """
    Build the full canonical archive file path.

    Example:
        run/research_capture/2026-04-18/ticks_opt/.../ticks_opt.parquet
    """
    session_root = build_session_archive_root(
        record_or_row,
        archive_root_relative=archive_root_relative,
    )
    relative_file_path = build_dataset_relative_file_path(
        dataset,
        record_or_row,
        file_name=file_name,
        partition_columns=partition_columns,
        session_date_in_root=session_date_in_root,
    )
    return (PurePosixPath(session_root) / relative_file_path).as_posix()


@dataclass(frozen=True, slots=True)
class PartitionPlan:
    """
    Immutable canonical partition plan for one dataset and one row.
    """
    dataset: CaptureDatasetName
    file_name: str
    partition_columns: tuple[str, ...]
    raw_partition_values: Mapping[str, Any]
    encoded_partition_values: Mapping[str, str]
    session_archive_root: str
    dataset_partition_dir: str
    dataset_relative_file_path: str
    archive_file_path: str

    def __post_init__(self) -> None:
        if not isinstance(self.dataset, CaptureDatasetName):
            raise TypeError("dataset must be CaptureDatasetName")
        _ensure_non_empty_str("file_name", self.file_name)

        object.__setattr__(self, "partition_columns", tuple(self.partition_columns))
        object.__setattr__(self, "raw_partition_values", MappingProxyType(dict(self.raw_partition_values)))
        object.__setattr__(self, "encoded_partition_values", MappingProxyType(dict(self.encoded_partition_values)))

        for attr_name in (
            "session_archive_root",
            "dataset_partition_dir",
            "dataset_relative_file_path",
            "archive_file_path",
        ):
            _ensure_non_empty_str(attr_name, getattr(self, attr_name))

        if not self.partition_columns:
            raise ValueError("partition_columns must be non-empty")
        for name in self.partition_columns:
            _ensure_known_field(name)

        if "session_date" not in self.raw_partition_values:
            raise ValueError("raw_partition_values must include session_date")
        if "session_date" not in self.encoded_partition_values:
            raise ValueError("encoded_partition_values must include session_date")

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset": self.dataset.value,
            "file_name": self.file_name,
            "partition_columns": list(self.partition_columns),
            "raw_partition_values": dict(self.raw_partition_values),
            "encoded_partition_values": dict(self.encoded_partition_values),
            "session_archive_root": self.session_archive_root,
            "dataset_partition_dir": self.dataset_partition_dir,
            "dataset_relative_file_path": self.dataset_relative_file_path,
            "archive_file_path": self.archive_file_path,
        }


def build_partition_plan(
    dataset: CaptureDatasetName | str,
    record_or_row: CaptureRecord | Mapping[str, Any],
    *,
    archive_root_relative: str = ARCHIVE_ROOT_RELATIVE,
    file_name: str | None = None,
    partition_columns: Sequence[str] | None = None,
    session_date_in_root: bool = True,
) -> PartitionPlan:
    """
    Build the immutable canonical partition plan for one dataset and one row.
    """
    dataset_name = _normalize_dataset(dataset)
    actual_file_name = ARCHIVE_OUTPUT_FILENAMES[dataset_name.value] if file_name is None else _ensure_non_empty_str("file_name", file_name)
    columns = canonical_partition_columns(partition_columns)

    raw_values = build_partition_value_map(
        record_or_row,
        partition_columns=columns,
        include_unlisted_session_date=True,
    )
    encoded_values = build_encoded_partition_value_map(
        record_or_row,
        partition_columns=columns,
        include_unlisted_session_date=True,
    )

    session_root = build_session_archive_root(
        record_or_row,
        archive_root_relative=archive_root_relative,
    )
    dataset_dir = build_dataset_partition_dir(
        dataset_name,
        record_or_row,
        partition_columns=columns,
        session_date_in_root=session_date_in_root,
    )
    relative_file_path = build_dataset_relative_file_path(
        dataset_name,
        record_or_row,
        file_name=actual_file_name,
        partition_columns=columns,
        session_date_in_root=session_date_in_root,
    )
    archive_file_path = (PurePosixPath(session_root) / relative_file_path).as_posix()

    return PartitionPlan(
        dataset=dataset_name,
        file_name=actual_file_name,
        partition_columns=columns,
        raw_partition_values=raw_values,
        encoded_partition_values=encoded_values,
        session_archive_root=session_root,
        dataset_partition_dir=dataset_dir,
        dataset_relative_file_path=relative_file_path,
        archive_file_path=archive_file_path,
    )


__all__ = [
    "DEFAULT_PARTITION_COLUMNS",
    "EMPTY_STRING_PARTITION_TOKEN",
    "FALSE_PARTITION_TOKEN",
    "NULL_PARTITION_TOKEN",
    "PartitionPlan",
    "TRUE_PARTITION_TOKEN",
    "build_archive_file_path",
    "build_dataset_partition_dir",
    "build_dataset_relative_file_path",
    "build_encoded_partition_value_map",
    "build_partition_plan",
    "build_partition_value_map",
    "build_session_archive_root",
    "canonical_partition_columns",
    "normalize_partition_value",
    "sanitize_partition_token",
]