from __future__ import annotations

"""
app/mme_scalpx/research_capture/archive_writer.py

Frozen archive writer for the MME research data capture chapter.

Purpose
-------
This module owns deterministic writing of research-capture session artifacts:
- partitioned parquet outputs
- manifest/session JSON files
- one high-level session write path

Owns
----
- pyarrow schema construction from frozen contracts
- stable row normalization for parquet writing
- deterministic grouping of records by archive partition path
- session JSON artifact writing
- one high-level session bundle write function

Does not own
------------
- broker IO
- Redis IO
- runtime orchestration
- replay logic
- production strategy doctrine

Design laws
-----------
- writing must be deterministic and side-effect free except for filesystem output
- schema must come from frozen contracts, never ad hoc row inspection
- partition layout must come from the partitioning layer only
- manifest/session files must be written atomically
- archive writes must preserve a stable canonical shape
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence

from app.mme_scalpx.research_capture.contracts import (
    ARCHIVE_COMPRESSION,
    ARCHIVE_ROOT_RELATIVE,
    ARCHIVE_WRITE_MODE,
    FIELD_NAMES,
    FIELD_SPECS,
    FIELD_SPECS_BY_NAME,
    SESSION_FILE_FILENAMES,
)
from app.mme_scalpx.research_capture.manifest import (
    build_session_manifest_from_records,
    manifest_to_dict,
)
from app.mme_scalpx.research_capture.models import (
    CaptureDatasetName,
    CaptureRecord,
    CaptureSessionManifest,
)
from app.mme_scalpx.research_capture.partitioning import (
    PartitionPlan,
    build_partition_plan,
    normalize_partition_value,
)

_PARQUET_IMPORT_ERROR = (
    "pyarrow is required for research_capture archive writing. "
    "Install it in the project environment before using archive_writer.py."
)


def _load_pyarrow():
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except Exception as exc:  # pragma: no cover - runtime dependency gate
        raise RuntimeError(_PARQUET_IMPORT_ERROR) from exc
    return pa, pq


def _ensure_non_empty_str(name: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty str")
    return value


def _ensure_int(name: str, value: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be int")
    return value


def _as_str_tuple(values: Sequence[str] | None) -> tuple[str, ...]:
    if values is None:
        return ()
    result = tuple(values)
    for value in result:
        if not isinstance(value, str):
            raise TypeError("expected a sequence of strings")
    return result


def _pyarrow_type_for_contract_dtype(dtype: str):
    pa, _ = _load_pyarrow()
    if dtype == "str":
        return pa.string()
    if dtype == "str_or_int":
        return pa.string()
    if dtype == "int":
        return pa.int64()
    if dtype == "float":
        return pa.float64()
    if dtype == "bool":
        return pa.bool_()
    if dtype == "json_list_float":
        return pa.list_(pa.float64())
    if dtype == "json_list_int":
        return pa.list_(pa.int64())
    if dtype == "json_list_str":
        return pa.list_(pa.string())
    raise ValueError(f"Unsupported contract dtype for arrow schema: {dtype!r}")


def build_arrow_schema():
    """
    Build a stable pyarrow schema directly from the frozen field contract.
    """
    pa, _ = _load_pyarrow()
    return pa.schema(
        [
            pa.field(spec.name, _pyarrow_type_for_contract_dtype(spec.dtype), nullable=True)
            for spec in FIELD_SPECS
        ]
    )


def _normalize_value_for_arrow(field_name: str, value: Any) -> Any:
    if value is None:
        return None

    spec = FIELD_SPECS_BY_NAME[field_name]
    dtype = spec.dtype

    if dtype == "str":
        return str(value)
    if dtype == "str_or_int":
        return str(value)
    if dtype == "int":
        return int(value)
    if dtype == "float":
        return float(value)
    if dtype == "bool":
        return bool(value)
    if dtype == "json_list_float":
        return [float(item) for item in value]
    if dtype == "json_list_int":
        return [int(item) for item in value]
    if dtype == "json_list_str":
        return [str(item) for item in value]

    raise ValueError(f"Unsupported contract dtype for arrow row normalization: {dtype!r}")


def canonicalize_record_row(record: CaptureRecord) -> dict[str, Any]:
    """
    Convert one capture record into a canonical full-width row for parquet.
    """
    raw_row = record.to_archive_row(include_none=True)
    canonical: dict[str, Any] = {}
    for field_name in FIELD_NAMES:
        canonical[field_name] = _normalize_value_for_arrow(field_name, raw_row.get(field_name))
    return canonical


def records_to_arrow_rows(records: Sequence[CaptureRecord]) -> list[dict[str, Any]]:
    """
    Convert capture records into canonical full-width arrow-compatible rows.
    """
    return [canonicalize_record_row(record) for record in records]


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(text, encoding="utf-8")
    os.replace(tmp_path, path)


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n"
    _atomic_write_text(path, text)


def _atomic_write_table(path: Path, table, *, compression: str) -> int:
    pa, pq = _load_pyarrow()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    pq.write_table(table, tmp_path, compression=compression)
    os.replace(tmp_path, path)
    return path.stat().st_size


def _append_or_write_table(path: Path, table, *, write_mode: str, compression: str) -> int:
    pa, pq = _load_pyarrow()

    if path.exists() and write_mode == "append":
        existing = pq.read_table(path)
        combined = pa.concat_tables([existing, table])
        return _atomic_write_table(path, combined, compression=compression)

    if path.exists() and write_mode == "overwrite":
        return _atomic_write_table(path, table, compression=compression)

    if path.exists() and write_mode not in {"append", "overwrite"}:
        raise ValueError(f"Unsupported archive write_mode: {write_mode!r}")

    return _atomic_write_table(path, table, compression=compression)


def _session_root_from_session_date(
    session_date: str,
    *,
    archive_root_relative: str = ARCHIVE_ROOT_RELATIVE,
) -> Path:
    session_token = normalize_partition_value(_ensure_non_empty_str("session_date", session_date))
    return Path(archive_root_relative) / session_token


@dataclass(frozen=True, slots=True)
class ArchiveWriteResult:
    """
    Immutable result of writing one research-capture session bundle.
    """
    session_date: str
    session_archive_root: str
    manifest_path: str
    source_availability_path: str
    integrity_summary_path: str
    dataset_file_paths: Mapping[str, tuple[str, ...]]
    dataset_row_counts: Mapping[str, int]
    dataset_bytes_written: Mapping[str, int]

    def __post_init__(self) -> None:
        _ensure_non_empty_str("session_date", self.session_date)
        _ensure_non_empty_str("session_archive_root", self.session_archive_root)
        _ensure_non_empty_str("manifest_path", self.manifest_path)
        _ensure_non_empty_str("source_availability_path", self.source_availability_path)
        _ensure_non_empty_str("integrity_summary_path", self.integrity_summary_path)

        frozen_file_paths: dict[str, tuple[str, ...]] = {}
        for dataset_name, paths in dict(self.dataset_file_paths).items():
            _ensure_non_empty_str("dataset_name", dataset_name)
            tuple_paths = tuple(paths)
            for file_path in tuple_paths:
                _ensure_non_empty_str("dataset_file_path", file_path)
            frozen_file_paths[dataset_name] = tuple_paths

        frozen_row_counts: dict[str, int] = {}
        for dataset_name, count in dict(self.dataset_row_counts).items():
            _ensure_non_empty_str("dataset_name", dataset_name)
            frozen_row_counts[dataset_name] = _ensure_int(f"dataset_row_count[{dataset_name}]", count)

        frozen_bytes: dict[str, int] = {}
        for dataset_name, count in dict(self.dataset_bytes_written).items():
            _ensure_non_empty_str("dataset_name", dataset_name)
            frozen_bytes[dataset_name] = _ensure_int(f"dataset_bytes_written[{dataset_name}]", count)

        object.__setattr__(self, "dataset_file_paths", MappingProxyType(frozen_file_paths))
        object.__setattr__(self, "dataset_row_counts", MappingProxyType(frozen_row_counts))
        object.__setattr__(self, "dataset_bytes_written", MappingProxyType(frozen_bytes))

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_date": self.session_date,
            "session_archive_root": self.session_archive_root,
            "manifest_path": self.manifest_path,
            "source_availability_path": self.source_availability_path,
            "integrity_summary_path": self.integrity_summary_path,
            "dataset_file_paths": {k: list(v) for k, v in self.dataset_file_paths.items()},
            "dataset_row_counts": dict(self.dataset_row_counts),
            "dataset_bytes_written": dict(self.dataset_bytes_written),
        }


def group_records_by_partition_path(
    records: Sequence[CaptureRecord],
    *,
    archive_root_relative: str = ARCHIVE_ROOT_RELATIVE,
    partition_columns: Sequence[str] | None = None,
) -> Mapping[str, tuple[PartitionPlan, tuple[CaptureRecord, ...]]]:
    """
    Group capture records by canonical archive file path.
    """
    grouped: dict[str, tuple[PartitionPlan, list[CaptureRecord]]] = {}

    for record in records:
        plan = build_partition_plan(
            record.dataset,
            record,
            archive_root_relative=archive_root_relative,
            partition_columns=partition_columns,
        )
        if plan.archive_file_path not in grouped:
            grouped[plan.archive_file_path] = (plan, [])
        grouped[plan.archive_file_path][1].append(record)

    frozen: dict[str, tuple[PartitionPlan, tuple[CaptureRecord, ...]]] = {}
    for archive_file_path, (plan, grouped_records) in grouped.items():
        frozen[archive_file_path] = (plan, tuple(grouped_records))
    return MappingProxyType(frozen)


def write_capture_records(
    records: Sequence[CaptureRecord],
    *,
    archive_root_relative: str = ARCHIVE_ROOT_RELATIVE,
    partition_columns: Sequence[str] | None = None,
    write_mode: str = ARCHIVE_WRITE_MODE,
    compression: str = ARCHIVE_COMPRESSION,
) -> tuple[Mapping[str, tuple[str, ...]], Mapping[str, int], Mapping[str, int]]:
    """
    Write parquet outputs for the supplied records.

    Returns
    -------
    dataset_file_paths:
        dataset -> tuple of written file paths
    dataset_row_counts:
        dataset -> total row count written from provided records
    dataset_bytes_written:
        dataset -> cumulative bytes of resulting parquet files
    """
    if not records:
        raise ValueError("write_capture_records requires at least one record")

    pa, _ = _load_pyarrow()
    schema = build_arrow_schema()
    grouped = group_records_by_partition_path(
        records,
        archive_root_relative=archive_root_relative,
        partition_columns=partition_columns,
    )

    dataset_file_paths: dict[str, list[str]] = {}
    dataset_row_counts: dict[str, int] = {}
    dataset_bytes_written: dict[str, int] = {}

    for archive_file_path, (plan, grouped_records) in grouped.items():
        rows = records_to_arrow_rows(grouped_records)
        table = pa.Table.from_pylist(rows, schema=schema)
        file_path = Path(archive_file_path)
        bytes_written = _append_or_write_table(
            file_path,
            table,
            write_mode=write_mode,
            compression=compression,
        )

        dataset_name = plan.dataset.value
        dataset_file_paths.setdefault(dataset_name, []).append(file_path.as_posix())
        dataset_row_counts[dataset_name] = dataset_row_counts.get(dataset_name, 0) + len(grouped_records)
        dataset_bytes_written[dataset_name] = dataset_bytes_written.get(dataset_name, 0) + bytes_written

    frozen_paths = {k: tuple(v) for k, v in dataset_file_paths.items()}
    return (
        MappingProxyType(frozen_paths),
        MappingProxyType(dict(dataset_row_counts)),
        MappingProxyType(dict(dataset_bytes_written)),
    )


def write_manifest_files(
    manifest: CaptureSessionManifest,
    *,
    archive_root_relative: str = ARCHIVE_ROOT_RELATIVE,
) -> Mapping[str, str]:
    """
    Write the three canonical session JSON artifacts:
    - manifest.json
    - source_availability.json
    - integrity_summary.json
    """
    session_root = _session_root_from_session_date(
        manifest.session_date,
        archive_root_relative=archive_root_relative,
    )

    manifest_path = session_root / SESSION_FILE_FILENAMES["manifest"]
    source_availability_path = session_root / SESSION_FILE_FILENAMES["source_availability"]
    integrity_summary_path = session_root / SESSION_FILE_FILENAMES["integrity_summary"]

    manifest_payload = manifest_to_dict(manifest)
    _atomic_write_json(manifest_path, manifest_payload)
    _atomic_write_json(source_availability_path, manifest.source_availability.to_dict())
    _atomic_write_json(integrity_summary_path, manifest.integrity_summary.to_dict())

    return MappingProxyType(
        {
            "manifest": manifest_path.as_posix(),
            "source_availability": source_availability_path.as_posix(),
            "integrity_summary": integrity_summary_path.as_posix(),
        }
    )


def write_session_bundle(
    *,
    session_date: str,
    records: Sequence[CaptureRecord],
    archive_root_relative: str = ARCHIVE_ROOT_RELATIVE,
    partition_columns: Sequence[str] | None = None,
    write_mode: str = ARCHIVE_WRITE_MODE,
    compression: str = ARCHIVE_COMPRESSION,
    source_availability=None,
    warnings: Sequence[str] = (),
    errors: Sequence[str] = (),
    status: str = "session_written",
    notes: Sequence[str] = (),
) -> ArchiveWriteResult:
    """
    High-level frozen session writer.

    Workflow
    --------
    1. validate all records belong to one session_date
    2. write parquet outputs
    3. build session manifest from written records and byte counts
    4. write manifest/session JSON files
    5. return immutable write result
    """
    _ensure_non_empty_str("session_date", session_date)

    if not records:
        raise ValueError("write_session_bundle requires at least one record")

    for index, record in enumerate(records):
        if record.timing.session_date != session_date:
            raise ValueError(
                f"record session_date mismatch at index {index}: "
                f"{record.timing.session_date!r} != {session_date!r}"
            )

    dataset_file_paths, dataset_row_counts, dataset_bytes_written = write_capture_records(
        records,
        archive_root_relative=archive_root_relative,
        partition_columns=partition_columns,
        write_mode=write_mode,
        compression=compression,
    )

    manifest = build_session_manifest_from_records(
        session_date=session_date,
        records=records,
        source_availability=source_availability,
        warnings=warnings,
        errors=errors,
        status=status,
        notes=notes,
        bytes_written_by_dataset=dataset_bytes_written,
    )

    session_file_paths = write_manifest_files(
        manifest,
        archive_root_relative=archive_root_relative,
    )

    session_root = _session_root_from_session_date(
        session_date,
        archive_root_relative=archive_root_relative,
    )

    return ArchiveWriteResult(
        session_date=session_date,
        session_archive_root=session_root.as_posix(),
        manifest_path=session_file_paths["manifest"],
        source_availability_path=session_file_paths["source_availability"],
        integrity_summary_path=session_file_paths["integrity_summary"],
        dataset_file_paths=dataset_file_paths,
        dataset_row_counts=dataset_row_counts,
        dataset_bytes_written=dataset_bytes_written,
    )


__all__ = [
    "ArchiveWriteResult",
    "build_arrow_schema",
    "canonicalize_record_row",
    "group_records_by_partition_path",
    "records_to_arrow_rows",
    "write_capture_records",
    "write_manifest_files",
    "write_session_bundle",
]
