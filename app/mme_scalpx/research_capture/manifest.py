from __future__ import annotations

"""
app/mme_scalpx/research_capture/manifest.py

Frozen manifest layer for the MME research data capture chapter.

Purpose
-------
This module owns deterministic construction of manifest-side objects for one
research-capture session. It converts validated capture records and explicit
session metadata into immutable, serialization-ready manifest models.

Owns
----
- source-availability construction
- integrity-summary construction
- archive-output construction
- session-manifest construction
- manifest payload validation and serialization helpers

Does not own
------------
- file writing
- parquet writing
- broker IO
- Redis IO
- runtime orchestration
- replay evaluation
- production strategy doctrine

Design laws
-----------
- manifest construction must be deterministic and side-effect free
- manifest payloads must remain aligned with the frozen contract surface
- archive/session metadata must be derivable from records without hidden state
"""

from collections import Counter
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, Sequence

from app.mme_scalpx.research_capture.contracts import (
    ARCHIVE_OUTPUT_FILENAMES,
    MANIFEST_REQUIRED_KEYS,
    PRIMARY_PARTITIONS,
    SCHEMA_STATUS,
    SECONDARY_PARTITIONS,
    SESSION_FILE_FILENAMES,
)
from app.mme_scalpx.research_capture.models import (
    CaptureArchiveOutput,
    CaptureDatasetName,
    CaptureRecord,
    CaptureSessionManifest,
    IntegritySummary,
    SourceAvailability,
)


def _utc_now_iso() -> str:
    """Return a UTC ISO-8601 timestamp for manifest creation."""
    return datetime.now(timezone.utc).isoformat()


def _as_str_tuple(values: Sequence[str] | None) -> tuple[str, ...]:
    """Normalize an optional sequence of strings into an immutable tuple."""
    if values is None:
        return ()
    result = tuple(values)
    for value in result:
        if not isinstance(value, str):
            raise TypeError("expected a sequence of strings")
    return result


def _ensure_non_empty_str(name: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty str")
    return value


def _ensure_int(name: str, value: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be int")
    return value


def _normalize_dataset(dataset: CaptureDatasetName | str) -> CaptureDatasetName:
    if isinstance(dataset, CaptureDatasetName):
        return dataset
    if not isinstance(dataset, str):
        raise TypeError("dataset must be CaptureDatasetName or str")
    try:
        return CaptureDatasetName(dataset)
    except ValueError as exc:
        raise ValueError(f"Unknown capture dataset: {dataset!r}") from exc


def _normalize_dataset_counts(
    dataset_row_counts: Mapping[CaptureDatasetName | str, int],
) -> dict[str, int]:
    normalized: dict[str, int] = {}
    for dataset, row_count in dataset_row_counts.items():
        dataset_name = _normalize_dataset(dataset).value
        count = _ensure_int(f"row_count[{dataset_name}]", row_count)
        if count < 0:
            raise ValueError(f"row_count[{dataset_name}] must be >= 0")
        normalized[dataset_name] = count
    return normalized


def _normalize_bytes_written(
    bytes_written_by_dataset: Mapping[CaptureDatasetName | str, int] | None,
) -> dict[str, int]:
    if bytes_written_by_dataset is None:
        return {}
    normalized: dict[str, int] = {}
    for dataset, bytes_written in bytes_written_by_dataset.items():
        dataset_name = _normalize_dataset(dataset).value
        count = _ensure_int(f"bytes_written[{dataset_name}]", bytes_written)
        if count < 0:
            raise ValueError(f"bytes_written[{dataset_name}] must be >= 0")
        normalized[dataset_name] = count
    return normalized


def build_source_availability(
    *,
    sources: Mapping[str, Any],
    counts: Mapping[str, int] | None = None,
    notes: Sequence[str] = (),
) -> SourceAvailability:
    """
    Build a canonical SourceAvailability instance.

    Parameters
    ----------
    sources:
        Mapping of source name -> presence/status indicator.
    counts:
        Optional mapping of source name -> numeric count.
    notes:
        Optional human-readable notes.
    """
    return SourceAvailability(
        sources=sources,
        counts={} if counts is None else counts,
        notes=_as_str_tuple(notes),
    )


def build_source_availability_from_records(
    records: Sequence[CaptureRecord],
    *,
    extra_sources: Mapping[str, Any] | None = None,
    notes: Sequence[str] = (),
) -> SourceAvailability:
    """
    Build source availability from capture records.

    The default summary is intentionally simple and deterministic:
    - `records_present`: whether any records exist
    - `brokers_present`: number of distinct brokers represented
    - one boolean presence flag per broker name
    - `datasets_present`: number of distinct datasets represented
    """
    broker_counter: Counter[str] = Counter()
    dataset_counter: Counter[str] = Counter()

    for record in records:
        broker_counter[record.instrument.broker_name] += 1
        dataset_counter[record.dataset.value] += 1

    sources: dict[str, Any] = {
        "records_present": bool(records),
        "brokers_present": len(broker_counter),
        "datasets_present": len(dataset_counter),
    }
    counts: dict[str, int] = {}

    for broker_name, broker_count in sorted(broker_counter.items()):
        safe_key = f"broker:{broker_name}"
        sources[safe_key] = True
        counts[safe_key] = broker_count

    for dataset_name, dataset_count in sorted(dataset_counter.items()):
        safe_key = f"dataset:{dataset_name}"
        sources[safe_key] = True
        counts[safe_key] = dataset_count

    if extra_sources:
        for key, value in extra_sources.items():
            sources[key] = value

    return build_source_availability(
        sources=sources,
        counts=counts,
        notes=notes,
    )


def build_integrity_summary(
    *,
    records: Sequence[CaptureRecord],
    warnings: Sequence[str] = (),
    errors: Sequence[str] = (),
) -> IntegritySummary:
    """
    Build the canonical integrity summary from capture records.
    """
    dataset_row_counts: Counter[str] = Counter()
    integrity_flag_counts: Counter[str] = Counter()

    stale_tick_count = 0
    missing_depth_count = 0
    missing_oi_count = 0
    thin_book_count = 0

    for record in records:
        dataset_row_counts[record.dataset.value] += 1

        audit = record.runtime_audit
        if audit.is_stale_tick:
            stale_tick_count += 1
        if audit.missing_depth_flag:
            missing_depth_count += 1
        if audit.missing_oi_flag:
            missing_oi_count += 1
        if audit.thin_book or bool(audit.book_is_thin):
            thin_book_count += 1
        integrity_flag_counts.update(audit.integrity_flags)

    return IntegritySummary(
        total_records=len(records),
        dataset_row_counts=dict(sorted(dataset_row_counts.items())),
        stale_tick_count=stale_tick_count,
        missing_depth_count=missing_depth_count,
        missing_oi_count=missing_oi_count,
        thin_book_count=thin_book_count,
        integrity_flag_counts=dict(sorted(integrity_flag_counts.items())),
        warnings=_as_str_tuple(warnings),
        errors=_as_str_tuple(errors),
    )


def build_integrity_summary_from_counts(
    *,
    total_records: int,
    dataset_row_counts: Mapping[CaptureDatasetName | str, int],
    stale_tick_count: int = 0,
    missing_depth_count: int = 0,
    missing_oi_count: int = 0,
    thin_book_count: int = 0,
    integrity_flag_counts: Mapping[str, int] | None = None,
    warnings: Sequence[str] = (),
    errors: Sequence[str] = (),
) -> IntegritySummary:
    """
    Build an integrity summary from explicit counters rather than raw records.
    """
    total = _ensure_int("total_records", total_records)
    if total < 0:
        raise ValueError("total_records must be >= 0")

    normalized_dataset_counts = _normalize_dataset_counts(dataset_row_counts)
    flag_counts = {} if integrity_flag_counts is None else dict(integrity_flag_counts)

    for key, value in flag_counts.items():
        _ensure_non_empty_str("integrity_flag_name", key)
        count = _ensure_int(f"integrity_flag_count[{key}]", value)
        if count < 0:
            raise ValueError(f"integrity_flag_count[{key}] must be >= 0")

    return IntegritySummary(
        total_records=total,
        dataset_row_counts=normalized_dataset_counts,
        stale_tick_count=_ensure_int("stale_tick_count", stale_tick_count),
        missing_depth_count=_ensure_int("missing_depth_count", missing_depth_count),
        missing_oi_count=_ensure_int("missing_oi_count", missing_oi_count),
        thin_book_count=_ensure_int("thin_book_count", thin_book_count),
        integrity_flag_counts=flag_counts,
        warnings=_as_str_tuple(warnings),
        errors=_as_str_tuple(errors),
    )


def build_archive_output(
    *,
    dataset: CaptureDatasetName | str,
    row_count: int,
    file_name: str | None = None,
    partition_columns: Sequence[str] | None = None,
    bytes_written: int | None = None,
    notes: Sequence[str] = (),
) -> CaptureArchiveOutput:
    """
    Build one canonical archive-output descriptor.
    """
    dataset_name = _normalize_dataset(dataset)

    if file_name is None:
        file_name = ARCHIVE_OUTPUT_FILENAMES[dataset_name.value]
    else:
        _ensure_non_empty_str("file_name", file_name)

    if partition_columns is None:
        partition_columns = tuple(PRIMARY_PARTITIONS + SECONDARY_PARTITIONS)

    return CaptureArchiveOutput(
        dataset=dataset_name,
        row_count=row_count,
        file_name=file_name,
        partition_columns=tuple(partition_columns),
        bytes_written=bytes_written,
        notes=_as_str_tuple(notes),
    )


def build_archive_outputs_from_counts(
    *,
    dataset_row_counts: Mapping[CaptureDatasetName | str, int],
    bytes_written_by_dataset: Mapping[CaptureDatasetName | str, int] | None = None,
    notes_by_dataset: Mapping[CaptureDatasetName | str, Sequence[str]] | None = None,
    include_zero_count_outputs: bool = False,
) -> tuple[CaptureArchiveOutput, ...]:
    """
    Build canonical archive outputs from dataset row counts.
    """
    counts = _normalize_dataset_counts(dataset_row_counts)
    bytes_written_map = _normalize_bytes_written(bytes_written_by_dataset)
    notes_map = {} if notes_by_dataset is None else dict(notes_by_dataset)

    outputs: list[CaptureArchiveOutput] = []
    for dataset in CaptureDatasetName:
        row_count = counts.get(dataset.value, 0)
        if row_count == 0 and not include_zero_count_outputs:
            continue

        notes = notes_map.get(dataset, notes_map.get(dataset.value, ()))
        outputs.append(
            build_archive_output(
                dataset=dataset,
                row_count=row_count,
                bytes_written=bytes_written_map.get(dataset.value),
                notes=notes,
            )
        )

    return tuple(outputs)


def build_session_manifest(
    *,
    session_date: str,
    source_availability: SourceAvailability,
    integrity_summary: IntegritySummary,
    archive_outputs: Sequence[CaptureArchiveOutput],
    created_at: str | None = None,
    status: str = SCHEMA_STATUS,
    notes: Sequence[str] = (),
) -> CaptureSessionManifest:
    """
    Build the canonical session manifest and validate cross-object consistency.
    """
    _ensure_non_empty_str("session_date", session_date)
    _ensure_non_empty_str("status", status)

    outputs = tuple(archive_outputs)
    if not outputs:
        raise ValueError("archive_outputs must be non-empty")

    integrity_counts = dict(integrity_summary.dataset_row_counts)
    output_counts = {output.dataset.value: output.row_count for output in outputs}

    for dataset_name, row_count in output_counts.items():
        expected = integrity_counts.get(dataset_name)
        if expected is None:
            raise ValueError(
                f"archive output dataset {dataset_name!r} not present in integrity_summary.dataset_row_counts"
            )
        if expected != row_count:
            raise ValueError(
                f"archive output row_count mismatch for {dataset_name!r}: "
                f"output={row_count} integrity_summary={expected}"
            )

    positive_integrity_datasets = {
        dataset_name for dataset_name, row_count in integrity_counts.items() if row_count > 0
    }
    missing_outputs = sorted(positive_integrity_datasets.difference(output_counts))
    if missing_outputs:
        raise ValueError(
            f"archive outputs missing datasets present in integrity_summary: {missing_outputs}"
        )

    manifest = CaptureSessionManifest(
        session_date=session_date,
        source_availability=source_availability,
        integrity_summary=integrity_summary,
        archive_outputs=outputs,
        created_at=_utc_now_iso() if created_at is None else created_at,
        status=status,
        notes=_as_str_tuple(notes),
    )

    validate_manifest_payload(manifest.to_dict())
    return manifest


def build_session_manifest_from_records(
    *,
    session_date: str,
    records: Sequence[CaptureRecord],
    source_availability: SourceAvailability | None = None,
    warnings: Sequence[str] = (),
    errors: Sequence[str] = (),
    created_at: str | None = None,
    status: str = SCHEMA_STATUS,
    notes: Sequence[str] = (),
    bytes_written_by_dataset: Mapping[CaptureDatasetName | str, int] | None = None,
) -> CaptureSessionManifest:
    """
    Build a full session manifest directly from capture records.
    """
    if source_availability is None:
        source_availability = build_source_availability_from_records(records, notes=("derived_from_records",))

    integrity_summary = build_integrity_summary(
        records=records,
        warnings=warnings,
        errors=errors,
    )

    archive_outputs = build_archive_outputs_from_counts(
        dataset_row_counts=integrity_summary.dataset_row_counts,
        bytes_written_by_dataset=bytes_written_by_dataset,
        include_zero_count_outputs=False,
    )

    if not archive_outputs:
        raise ValueError("cannot build session manifest from records with zero archive outputs")

    return build_session_manifest(
        session_date=session_date,
        source_availability=source_availability,
        integrity_summary=integrity_summary,
        archive_outputs=archive_outputs,
        created_at=created_at,
        status=status,
        notes=notes,
    )


def manifest_to_dict(manifest: CaptureSessionManifest) -> dict[str, Any]:
    """
    Return the canonical manifest payload as a plain dict.
    """
    payload = manifest.to_dict()
    validate_manifest_payload(payload)
    return payload


def validate_manifest_payload(payload: Mapping[str, Any]) -> None:
    """
    Validate that a manifest payload satisfies the frozen contract surface.
    """
    missing = [key for key in MANIFEST_REQUIRED_KEYS if key not in payload]
    if missing:
        raise ValueError(f"manifest payload missing required keys: {missing}")

    archive_outputs = payload.get("archive_outputs")
    if not isinstance(archive_outputs, list) or not archive_outputs:
        raise ValueError("manifest payload archive_outputs must be a non-empty list")

    session_files = payload.get("session_files")
    if session_files != dict(SESSION_FILE_FILENAMES):
        raise ValueError("manifest payload session_files drift detected from frozen contract")

    for output in archive_outputs:
        if not isinstance(output, dict):
            raise TypeError("each archive_outputs entry must be a dict")
        dataset_name = output.get("dataset")
        if dataset_name not in ARCHIVE_OUTPUT_FILENAMES:
            raise ValueError(f"unknown archive output dataset: {dataset_name!r}")
        file_name = output.get("file_name")
        if not isinstance(file_name, str) or not file_name:
            raise ValueError(f"archive output file_name invalid for dataset {dataset_name!r}")

    source_availability = payload.get("source_availability")
    if not isinstance(source_availability, dict):
        raise TypeError("manifest payload source_availability must be a dict")

    integrity_summary = payload.get("integrity_summary")
    if not isinstance(integrity_summary, dict):
        raise TypeError("manifest payload integrity_summary must be a dict")


__all__ = [
    "build_archive_output",
    "build_archive_outputs_from_counts",
    "build_integrity_summary",
    "build_integrity_summary_from_counts",
    "build_session_manifest",
    "build_session_manifest_from_records",
    "build_source_availability",
    "build_source_availability_from_records",
    "manifest_to_dict",
    "validate_manifest_payload",
]

# =============================================================================
# Batch 17 freeze hardening: production firewall in manifest surfaces
# =============================================================================

_BATCH17_MANIFEST_FIREWALL_VERSION = "1"


def build_production_firewall_manifest_section() -> dict[str, bool]:
    return {
        "production_doctrine_mutated": False,
        "production_params_mutated": False,
        "live_runtime_mutated": False,
        "research_outputs_are_advisory": True,
        "promotion_requires_manual_patch_and_proof": True,
    }


_BATCH17_ORIGINAL_MANIFEST_TO_DICT = manifest_to_dict


def manifest_to_dict(manifest: CaptureSessionManifest) -> dict[str, Any]:
    payload = _BATCH17_ORIGINAL_MANIFEST_TO_DICT(manifest)
    payload["production_firewall"] = build_production_firewall_manifest_section()
    return payload
