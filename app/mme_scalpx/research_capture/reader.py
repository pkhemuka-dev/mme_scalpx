from __future__ import annotations

"""
app/mme_scalpx/research_capture/reader.py

Frozen archive reader for the MME research data capture chapter.

Purpose
-------
This module owns deterministic reading of research-capture session artifacts
from the canonical archive layout.

Owns
----
- session-root resolution
- manifest/source-availability/integrity-summary reading
- dataset parquet discovery
- dataset table / row reading
- one immutable session-read bundle surface

Does not own
------------
- broker IO
- Redis IO
- archive writing
- normalization
- enrichment
- production strategy doctrine

Design laws
-----------
- reading must be deterministic and side-effect free
- reader must follow the frozen archive contract exactly
- reader must not infer alternate layouts
- reader returns typed/session-safe structures wherever practical
"""

import json
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence

from app.mme_scalpx.research_capture.contracts import (
    ARCHIVE_OUTPUT_FILENAMES,
    ARCHIVE_ROOT_RELATIVE,
    CONSTITUTION_NAME,
    SCHEMA_NAME,
    SCHEMA_STATUS,
    SCHEMA_VERSION,
    SESSION_FILE_FILENAMES,
)
from app.mme_scalpx.research_capture.models import (
    CaptureArchiveOutput,
    CaptureDatasetName,
    CaptureSessionManifest,
    IntegritySummary,
    SourceAvailability,
)

_PARQUET_IMPORT_ERROR = (
    "pyarrow is required for research_capture reader operations. "
    "Install it in the project environment before using reader.py."
)


def _load_pyarrow():
    try:
        import pyarrow.parquet as pq
    except Exception as exc:  # pragma: no cover - dependency gate
        raise RuntimeError(_PARQUET_IMPORT_ERROR) from exc
    return pq


def _ensure_non_empty_str(name: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty str")
    return value


def _freeze_mapping(values: Mapping[str, Any] | None) -> Mapping[str, Any]:
    if values is None:
        return MappingProxyType({})
    return MappingProxyType(dict(values))


def _freeze_str_tuple(values: Sequence[str] | None) -> tuple[str, ...]:
    if values is None:
        return ()
    result = tuple(values)
    for value in result:
        if not isinstance(value, str):
            raise TypeError("expected a sequence of strings")
    return result


def _normalize_dataset(dataset: CaptureDatasetName | str) -> CaptureDatasetName:
    if isinstance(dataset, CaptureDatasetName):
        return dataset
    if not isinstance(dataset, str):
        raise TypeError("dataset must be CaptureDatasetName or str")
    try:
        return CaptureDatasetName(dataset)
    except ValueError as exc:
        raise ValueError(f"Unknown capture dataset: {dataset!r}") from exc


def _session_root(session_date: str, *, archive_root_relative: str = ARCHIVE_ROOT_RELATIVE) -> Path:
    return Path(archive_root_relative) / _ensure_non_empty_str("session_date", session_date)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path.as_posix())
    return json.loads(path.read_text(encoding="utf-8"))


def _manifest_path(session_date: str, *, archive_root_relative: str = ARCHIVE_ROOT_RELATIVE) -> Path:
    return _session_root(session_date, archive_root_relative=archive_root_relative) / SESSION_FILE_FILENAMES["manifest"]


def _source_availability_path(session_date: str, *, archive_root_relative: str = ARCHIVE_ROOT_RELATIVE) -> Path:
    return _session_root(session_date, archive_root_relative=archive_root_relative) / SESSION_FILE_FILENAMES["source_availability"]


def _integrity_summary_path(session_date: str, *, archive_root_relative: str = ARCHIVE_ROOT_RELATIVE) -> Path:
    return _session_root(session_date, archive_root_relative=archive_root_relative) / SESSION_FILE_FILENAMES["integrity_summary"]


def _capture_archive_output_from_dict(payload: Mapping[str, Any]) -> CaptureArchiveOutput:
    return CaptureArchiveOutput(
        dataset=_normalize_dataset(payload["dataset"]),
        row_count=int(payload["row_count"]),
        file_name=payload.get("file_name"),
        partition_columns=tuple(payload.get("partition_columns", ())),
        bytes_written=payload.get("bytes_written"),
        notes=tuple(payload.get("notes", ())),
    )


def _source_availability_from_dict(payload: Mapping[str, Any]) -> SourceAvailability:
    return SourceAvailability(
        sources=dict(payload.get("sources", {})),
        counts=dict(payload.get("counts", {})),
        notes=tuple(payload.get("notes", ())),
    )


def _integrity_summary_from_dict(payload: Mapping[str, Any]) -> IntegritySummary:
    return IntegritySummary(
        total_records=int(payload["total_records"]),
        dataset_row_counts=dict(payload.get("dataset_row_counts", {})),
        stale_tick_count=int(payload.get("stale_tick_count", 0)),
        missing_depth_count=int(payload.get("missing_depth_count", 0)),
        missing_oi_count=int(payload.get("missing_oi_count", 0)),
        thin_book_count=int(payload.get("thin_book_count", 0)),
        integrity_flag_counts=dict(payload.get("integrity_flag_counts", {})),
        warnings=tuple(payload.get("warnings", ())),
        errors=tuple(payload.get("errors", ())),
    )


def _manifest_from_dict(payload: Mapping[str, Any]) -> CaptureSessionManifest:
    source_availability = _source_availability_from_dict(payload["source_availability"])
    integrity_summary = _integrity_summary_from_dict(payload["integrity_summary"])
    archive_outputs = tuple(
        _capture_archive_output_from_dict(item)
        for item in payload.get("archive_outputs", [])
    )
    return CaptureSessionManifest(
        session_date=payload["session_date"],
        source_availability=source_availability,
        integrity_summary=integrity_summary,
        archive_outputs=archive_outputs,
        created_at=payload.get("created_at"),
        schema_name=payload.get("schema_name", SCHEMA_NAME),
        schema_version=payload.get("schema_version", SCHEMA_VERSION),
        constitution_name=payload.get("constitution_name", CONSTITUTION_NAME),
        chapter=payload.get("chapter", "research_capture"),
        status=payload.get("status", SCHEMA_STATUS),
        notes=tuple(payload.get("notes", ())),
    )


@dataclass(frozen=True, slots=True)
class ReaderConfig:
    archive_root_relative: str = ARCHIVE_ROOT_RELATIVE
    verify_files_exist: bool = True

    def __post_init__(self) -> None:
        _ensure_non_empty_str("archive_root_relative", self.archive_root_relative)
        if not isinstance(self.verify_files_exist, bool):
            raise TypeError("verify_files_exist must be bool")


DEFAULT_READER_CONFIG = ReaderConfig()


@dataclass(frozen=True, slots=True)
class SessionReadBundle:
    session_date: str
    session_root: str
    manifest: CaptureSessionManifest
    source_availability: SourceAvailability
    integrity_summary: IntegritySummary
    dataset_file_paths: Mapping[str, tuple[str, ...]]
    dataset_row_counts: Mapping[str, int]

    def __post_init__(self) -> None:
        _ensure_non_empty_str("session_date", self.session_date)
        _ensure_non_empty_str("session_root", self.session_root)

        if not isinstance(self.manifest, CaptureSessionManifest):
            raise TypeError("manifest must be CaptureSessionManifest")
        if not isinstance(self.source_availability, SourceAvailability):
            raise TypeError("source_availability must be SourceAvailability")
        if not isinstance(self.integrity_summary, IntegritySummary):
            raise TypeError("integrity_summary must be IntegritySummary")

        frozen_paths: dict[str, tuple[str, ...]] = {}
        for dataset_name, paths in dict(self.dataset_file_paths).items():
            _normalize_dataset(dataset_name)
            tuple_paths = tuple(paths)
            for path in tuple_paths:
                _ensure_non_empty_str("dataset_file_path", path)
            frozen_paths[str(dataset_name)] = tuple_paths

        frozen_counts: dict[str, int] = {}
        for dataset_name, count in dict(self.dataset_row_counts).items():
            _normalize_dataset(dataset_name)
            if not isinstance(count, int) or isinstance(count, bool):
                raise TypeError("dataset_row_counts values must be int")
            frozen_counts[str(dataset_name)] = count

        object.__setattr__(self, "dataset_file_paths", MappingProxyType(frozen_paths))
        object.__setattr__(self, "dataset_row_counts", MappingProxyType(frozen_counts))

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_date": self.session_date,
            "session_root": self.session_root,
            "manifest": self.manifest.to_dict(),
            "source_availability": self.source_availability.to_dict(),
            "integrity_summary": self.integrity_summary.to_dict(),
            "dataset_file_paths": {k: list(v) for k, v in self.dataset_file_paths.items()},
            "dataset_row_counts": dict(self.dataset_row_counts),
        }


def session_exists(
    session_date: str,
    *,
    config: ReaderConfig = DEFAULT_READER_CONFIG,
) -> bool:
    return _session_root(session_date, archive_root_relative=config.archive_root_relative).exists()


def read_manifest(
    session_date: str,
    *,
    config: ReaderConfig = DEFAULT_READER_CONFIG,
) -> CaptureSessionManifest:
    payload = _read_json(_manifest_path(session_date, archive_root_relative=config.archive_root_relative))
    manifest = _manifest_from_dict(payload)
    if config.verify_files_exist:
        # basic contract-alignment sanity on session files
        for rel_name in SESSION_FILE_FILENAMES.values():
            path = _session_root(session_date, archive_root_relative=config.archive_root_relative) / rel_name
            if not path.exists():
                raise FileNotFoundError(path.as_posix())
    return manifest


def read_source_availability(
    session_date: str,
    *,
    config: ReaderConfig = DEFAULT_READER_CONFIG,
) -> SourceAvailability:
    payload = _read_json(_source_availability_path(session_date, archive_root_relative=config.archive_root_relative))
    return _source_availability_from_dict(payload)


def read_integrity_summary(
    session_date: str,
    *,
    config: ReaderConfig = DEFAULT_READER_CONFIG,
) -> IntegritySummary:
    payload = _read_json(_integrity_summary_path(session_date, archive_root_relative=config.archive_root_relative))
    return _integrity_summary_from_dict(payload)


def list_dataset_files(
    session_date: str,
    dataset: CaptureDatasetName | str,
    *,
    config: ReaderConfig = DEFAULT_READER_CONFIG,
) -> tuple[str, ...]:
    dataset_name = _normalize_dataset(dataset)
    session_root = _session_root(session_date, archive_root_relative=config.archive_root_relative)
    dataset_dir = session_root / dataset_name.value
    if not dataset_dir.exists():
        return ()
    filename = ARCHIVE_OUTPUT_FILENAMES[dataset_name.value]
    paths = tuple(sorted(path.as_posix() for path in dataset_dir.rglob(filename)))
    if config.verify_files_exist:
        for path_str in paths:
            if not Path(path_str).exists():
                raise FileNotFoundError(path_str)
    return paths


def read_dataset_table(
    session_date: str,
    dataset: CaptureDatasetName | str,
    *,
    config: ReaderConfig = DEFAULT_READER_CONFIG,
):
    pq = _load_pyarrow()
    file_paths = list_dataset_files(session_date, dataset, config=config)
    if not file_paths:
        raise FileNotFoundError(
            f"No dataset files found for session_date={session_date!r}, dataset={_normalize_dataset(dataset).value!r}"
        )
    tables = [pq.ParquetFile(path).read() for path in file_paths]
    if len(tables) == 1:
        return tables[0]

    import pyarrow as pa  # loaded only when needed
    return pa.concat_tables(tables)


def read_dataset_rows(
    session_date: str,
    dataset: CaptureDatasetName | str,
    *,
    config: ReaderConfig = DEFAULT_READER_CONFIG,
) -> list[dict[str, Any]]:
    table = read_dataset_table(session_date, dataset, config=config)
    return table.to_pylist()


def build_session_read_bundle(
    session_date: str,
    *,
    config: ReaderConfig = DEFAULT_READER_CONFIG,
) -> SessionReadBundle:
    manifest = read_manifest(session_date, config=config)
    source_availability = read_source_availability(session_date, config=config)
    integrity_summary = read_integrity_summary(session_date, config=config)

    dataset_file_paths: dict[str, tuple[str, ...]] = {}
    dataset_row_counts: dict[str, int] = {}

    for dataset_name in ARCHIVE_OUTPUT_FILENAMES:
        files = list_dataset_files(session_date, dataset_name, config=config)
        if files:
            dataset_file_paths[dataset_name] = files

    for dataset_name, row_count in integrity_summary.dataset_row_counts.items():
        dataset_row_counts[dataset_name] = int(row_count)

    return SessionReadBundle(
        session_date=session_date,
        session_root=_session_root(session_date, archive_root_relative=config.archive_root_relative).as_posix(),
        manifest=manifest,
        source_availability=source_availability,
        integrity_summary=integrity_summary,
        dataset_file_paths=dataset_file_paths,
        dataset_row_counts=dataset_row_counts,
    )


__all__ = [
    "DEFAULT_READER_CONFIG",
    "ReaderConfig",
    "SessionReadBundle",
    "build_session_read_bundle",
    "list_dataset_files",
    "read_dataset_rows",
    "read_dataset_table",
    "read_integrity_summary",
    "read_manifest",
    "read_source_availability",
    "session_exists",
]
