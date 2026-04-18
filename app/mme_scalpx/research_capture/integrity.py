from __future__ import annotations

"""
app/mme_scalpx/research_capture/integrity.py

Frozen integrity layer for the MME research data capture chapter.

Purpose
-------
This module owns deterministic integrity checks for canonical research-capture
records, route plans, manifests, archive write results, and reader bundles.

Owns
----
- immutable integrity check/report models
- record-sequence integrity checks
- route/manifest/archive/readback alignment checks
- one high-level integrity report builder

Does not own
------------
- broker IO
- Redis IO
- parquet writing
- archive writing
- normalization
- enrichment
- routing
- production strategy doctrine

Design laws
-----------
- integrity checks must be deterministic and side-effect free
- integrity checks must validate explicit surfaces, not infer hidden state
- integrity is stricter than health: failures mean structural or factual drift
- reports must remain serialization-ready and auditable
"""

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence

from app.mme_scalpx.research_capture.archive_writer import ArchiveWriteResult
from app.mme_scalpx.research_capture.models import (
    CaptureRecord,
    CaptureSessionManifest,
)
from app.mme_scalpx.research_capture.reader import SessionReadBundle
from app.mme_scalpx.research_capture.router import (
    ROUTE_RUNTIME_AUDIT,
    ROUTE_SIGNALS_AUDIT,
    ROUTE_TICKS_FUT,
    ROUTE_TICKS_OPT,
    RoutePlan,
)


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


class IntegrityStatus(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


_STATUS_RANK: Mapping[IntegrityStatus, int] = {
    IntegrityStatus.PASS: 0,
    IntegrityStatus.WARN: 1,
    IntegrityStatus.FAIL: 2,
}


def max_integrity_status(statuses: Iterable[IntegrityStatus]) -> IntegrityStatus:
    statuses_tuple = tuple(statuses)
    if not statuses_tuple:
        return IntegrityStatus.PASS
    return max(statuses_tuple, key=lambda status: _STATUS_RANK[status])


@dataclass(frozen=True, slots=True)
class IntegrityConfig:
    """
    Frozen integrity configuration surface.
    """
    require_runtime_audit_for_all_records: bool = True
    require_route_plan_session_match: bool = True
    require_manifest_row_alignment: bool = True
    require_reader_alignment: bool = True
    require_archive_write_alignment: bool = True
    allow_duplicate_snapshot_ids: bool = True
    warn_on_missing_strategy_audit_route: bool = True

    def __post_init__(self) -> None:
        for name in (
            "require_runtime_audit_for_all_records",
            "require_route_plan_session_match",
            "require_manifest_row_alignment",
            "require_reader_alignment",
            "require_archive_write_alignment",
            "allow_duplicate_snapshot_ids",
            "warn_on_missing_strategy_audit_route",
        ):
            value = getattr(self, name)
            if not isinstance(value, bool):
                raise TypeError(f"{name} must be bool")


DEFAULT_INTEGRITY_CONFIG = IntegrityConfig()


@dataclass(frozen=True, slots=True)
class IntegrityCheckResult:
    """
    Immutable integrity check result.
    """
    name: str
    status: IntegrityStatus
    message: str
    details: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        _ensure_non_empty_str("name", self.name)
        if not isinstance(self.status, IntegrityStatus):
            raise TypeError("status must be IntegrityStatus")
        _ensure_non_empty_str("message", self.message)
        object.__setattr__(self, "details", _freeze_mapping(self.details))

    @property
    def passed(self) -> bool:
        return self.status is IntegrityStatus.PASS

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": dict(self.details),
        }


@dataclass(frozen=True, slots=True)
class IntegrityReport:
    """
    Immutable integrity report.
    """
    session_date: str
    checks: tuple[IntegrityCheckResult, ...]
    status: IntegrityStatus | None = None
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _ensure_non_empty_str("session_date", self.session_date)
        object.__setattr__(self, "checks", tuple(self.checks))
        object.__setattr__(self, "notes", _freeze_str_tuple(self.notes))

        if not self.checks:
            raise ValueError("checks must be non-empty")

        seen: set[str] = set()
        for check in self.checks:
            if not isinstance(check, IntegrityCheckResult):
                raise TypeError("checks must contain only IntegrityCheckResult instances")
            if check.name in seen:
                raise ValueError(f"duplicate integrity check name: {check.name}")
            seen.add(check.name)

        computed_status = max_integrity_status(check.status for check in self.checks)
        if self.status is None:
            object.__setattr__(self, "status", computed_status)
        else:
            if not isinstance(self.status, IntegrityStatus):
                raise TypeError("status must be IntegrityStatus or None")
            if _STATUS_RANK[self.status] != _STATUS_RANK[computed_status]:
                raise ValueError(
                    f"provided report status {self.status.value} does not match computed status {computed_status.value}"
                )

    @property
    def checks_by_name(self) -> Mapping[str, IntegrityCheckResult]:
        return MappingProxyType({check.name: check for check in self.checks})

    @property
    def status_counts(self) -> Mapping[str, int]:
        counts = {
            IntegrityStatus.PASS.value: 0,
            IntegrityStatus.WARN.value: 0,
            IntegrityStatus.FAIL.value: 0,
        }
        for check in self.checks:
            counts[check.status.value] += 1
        return MappingProxyType(counts)

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_date": self.session_date,
            "status": self.status.value,
            "status_counts": dict(self.status_counts),
            "checks": [check.to_dict() for check in self.checks],
            "notes": list(self.notes),
        }


def _record_key(record: CaptureRecord) -> tuple[Any, ...]:
    return (
        record.dataset.value,
        record.timing.session_date,
        record.instrument.instrument_token,
        record.timing.event_seq,
        record.timing.exchange_ts,
    )


def check_single_session(
    records: Sequence[CaptureRecord],
    *,
    session_date: str,
) -> IntegrityCheckResult:
    mismatched = [
        idx for idx, record in enumerate(records)
        if record.timing.session_date != session_date
    ]
    status = IntegrityStatus.PASS if not mismatched else IntegrityStatus.FAIL
    message = "single session validated" if not mismatched else "mixed session dates detected"
    return IntegrityCheckResult(
        name="single_session",
        status=status,
        message=message,
        details={
            "session_date": session_date,
            "record_count": len(records),
            "mismatched_indices": mismatched,
        },
    )


def check_monotonic_event_sequence(
    records: Sequence[CaptureRecord],
) -> IntegrityCheckResult:
    violations: list[dict[str, Any]] = []
    if records:
        sorted_records = sorted(records, key=lambda r: (_record_key(r)))
        prev: CaptureRecord | None = None
        for record in sorted_records:
            if prev is not None:
                same_stream = (
                    prev.dataset == record.dataset
                    and prev.timing.session_date == record.timing.session_date
                    and prev.instrument.instrument_token == record.instrument.instrument_token
                )
                if same_stream and record.timing.event_seq <= prev.timing.event_seq:
                    violations.append(
                        {
                            "instrument_token": str(record.instrument.instrument_token),
                            "prev_event_seq": prev.timing.event_seq,
                            "curr_event_seq": record.timing.event_seq,
                        }
                    )
            prev = record

    status = IntegrityStatus.PASS if not violations else IntegrityStatus.FAIL
    message = "event sequence monotonic" if not violations else "event sequence violations detected"
    return IntegrityCheckResult(
        name="monotonic_event_sequence",
        status=status,
        message=message,
        details={
            "record_count": len(records),
            "violation_count": len(violations),
            "violations": violations,
        },
    )


def check_monotonic_exchange_timestamps(
    records: Sequence[CaptureRecord],
) -> IntegrityCheckResult:
    violations: list[dict[str, Any]] = []
    if records:
        sorted_records = sorted(records, key=lambda r: (_record_key(r)))
        prev: CaptureRecord | None = None
        for record in sorted_records:
            if prev is not None:
                same_stream = (
                    prev.dataset == record.dataset
                    and prev.timing.session_date == record.timing.session_date
                    and prev.instrument.instrument_token == record.instrument.instrument_token
                )
                if same_stream and record.timing.exchange_ts < prev.timing.exchange_ts:
                    violations.append(
                        {
                            "instrument_token": str(record.instrument.instrument_token),
                            "prev_exchange_ts": prev.timing.exchange_ts,
                            "curr_exchange_ts": record.timing.exchange_ts,
                        }
                    )
            prev = record

    status = IntegrityStatus.PASS if not violations else IntegrityStatus.FAIL
    message = "exchange timestamps monotonic" if not violations else "exchange timestamp regressions detected"
    return IntegrityCheckResult(
        name="monotonic_exchange_timestamps",
        status=status,
        message=message,
        details={
            "record_count": len(records),
            "violation_count": len(violations),
            "violations": violations,
        },
    )


def check_runtime_audit_presence(
    records: Sequence[CaptureRecord],
    *,
    config: IntegrityConfig = DEFAULT_INTEGRITY_CONFIG,
) -> IntegrityCheckResult:
    missing = [idx for idx, record in enumerate(records) if record.runtime_audit is None]

    if not missing:
        status = IntegrityStatus.PASS
        message = "runtime audit present on all records"
    elif config.require_runtime_audit_for_all_records:
        status = IntegrityStatus.FAIL
        message = "runtime audit missing on one or more records"
    else:
        status = IntegrityStatus.WARN
        message = "runtime audit missing on one or more records"

    return IntegrityCheckResult(
        name="runtime_audit_presence",
        status=status,
        message=message,
        details={
            "record_count": len(records),
            "missing_indices": missing,
        },
    )


def check_duplicate_snapshot_ids(
    records: Sequence[CaptureRecord],
    *,
    config: IntegrityConfig = DEFAULT_INTEGRITY_CONFIG,
) -> IntegrityCheckResult:
    seen: set[str] = set()
    duplicates: list[str] = []

    for record in records:
        snapshot_id = record.timing.snapshot_id
        if not snapshot_id:
            continue
        if snapshot_id in seen and snapshot_id not in duplicates:
            duplicates.append(snapshot_id)
        seen.add(snapshot_id)

    if not duplicates:
        status = IntegrityStatus.PASS
        message = "snapshot id duplication check passed"
    elif config.allow_duplicate_snapshot_ids:
        status = IntegrityStatus.WARN
        message = "duplicate snapshot ids detected"
    else:
        status = IntegrityStatus.FAIL
        message = "duplicate snapshot ids detected"

    return IntegrityCheckResult(
        name="duplicate_snapshot_ids",
        status=status,
        message=message,
        details={
            "duplicate_snapshot_ids": duplicates,
            "duplicate_count": len(duplicates),
        },
    )


def check_route_plan_alignment(
    route_plan: RoutePlan,
    records: Sequence[CaptureRecord],
    *,
    session_date: str,
    config: IntegrityConfig = DEFAULT_INTEGRITY_CONFIG,
) -> IntegrityCheckResult:
    issues: list[str] = []
    expected_record_keys = {_record_key(record) for record in records}

    if config.require_route_plan_session_match and route_plan.session_date != session_date:
        issues.append("route_plan_session_mismatch")

    tick_keys = set()
    for route_name in (ROUTE_TICKS_FUT, ROUTE_TICKS_OPT):
        for record in route_plan.get(route_name, ()):
            tick_keys.add(_record_key(record))

    runtime_audit_keys = {_record_key(record) for record in route_plan.get(ROUTE_RUNTIME_AUDIT, ())}
    signals_audit_keys = {_record_key(record) for record in route_plan.get(ROUTE_SIGNALS_AUDIT, ())}

    if tick_keys != expected_record_keys:
        issues.append("tick_route_membership_mismatch")

    missing_runtime_audit_keys = {
        _record_key(record) for record in records
        if record.runtime_audit is not None and _record_key(record) not in runtime_audit_keys
    }
    if missing_runtime_audit_keys:
        issues.append("runtime_audit_route_mismatch")

    expected_signals = {
        _record_key(record) for record in records
        if record.strategy_audit is not None and record.strategy_audit.to_field_map(include_none=False)
    }
    if expected_signals != signals_audit_keys and expected_signals:
        issues.append("signals_audit_route_mismatch")
    elif not expected_signals and ROUTE_SIGNALS_AUDIT not in route_plan and config.warn_on_missing_strategy_audit_route:
        pass

    status = IntegrityStatus.PASS if not issues else IntegrityStatus.FAIL
    message = "route plan aligned" if not issues else "; ".join(issues)

    return IntegrityCheckResult(
        name="route_plan_alignment",
        status=status,
        message=message,
        details={
            "session_date": session_date,
            "route_keys": sorted(route_plan.keys()),
            "route_counts": dict(route_plan.counts),
            "expected_record_count": len(expected_record_keys),
            "tick_route_count": len(tick_keys),
            "runtime_audit_route_count": len(runtime_audit_keys),
            "signals_audit_route_count": len(signals_audit_keys),
        },
    )


def check_manifest_alignment(
    manifest: CaptureSessionManifest,
    *,
    session_date: str,
    config: IntegrityConfig = DEFAULT_INTEGRITY_CONFIG,
) -> IntegrityCheckResult:
    issues: list[str] = []
    archive_output_counts = {output.dataset.value: output.row_count for output in manifest.archive_outputs}
    integrity_counts = dict(manifest.integrity_summary.dataset_row_counts)

    if manifest.session_date != session_date:
        issues.append("manifest_session_mismatch")

    if config.require_manifest_row_alignment:
        if archive_output_counts != integrity_counts:
            issues.append("manifest_integrity_row_count_mismatch")

    status = IntegrityStatus.PASS if not issues else IntegrityStatus.FAIL
    message = "manifest aligned" if not issues else "; ".join(issues)

    return IntegrityCheckResult(
        name="manifest_alignment",
        status=status,
        message=message,
        details={
            "session_date": session_date,
            "manifest_session_date": manifest.session_date,
            "archive_output_counts": archive_output_counts,
            "integrity_counts": integrity_counts,
            "archive_output_count": len(manifest.archive_outputs),
        },
    )


def check_archive_write_alignment(
    archive_write_result: ArchiveWriteResult,
    manifest: CaptureSessionManifest,
    *,
    session_date: str,
    config: IntegrityConfig = DEFAULT_INTEGRITY_CONFIG,
) -> IntegrityCheckResult:
    issues: list[str] = []

    if archive_write_result.session_date != session_date:
        issues.append("archive_write_session_mismatch")
    if manifest.session_date != session_date:
        issues.append("manifest_session_mismatch")

    manifest_counts = {output.dataset.value: output.row_count for output in manifest.archive_outputs}
    write_counts = dict(archive_write_result.dataset_row_counts)

    if config.require_archive_write_alignment and manifest_counts != write_counts:
        issues.append("archive_write_row_count_mismatch")

    manifest_bytes = {
        output.dataset.value: int(output.bytes_written or 0)
        for output in manifest.archive_outputs
    }
    write_bytes = dict(archive_write_result.dataset_bytes_written)
    if config.require_archive_write_alignment and manifest_bytes != write_bytes:
        issues.append("archive_write_bytes_mismatch")

    status = IntegrityStatus.PASS if not issues else IntegrityStatus.FAIL
    message = "archive write aligned" if not issues else "; ".join(issues)

    return IntegrityCheckResult(
        name="archive_write_alignment",
        status=status,
        message=message,
        details={
            "session_date": session_date,
            "manifest_counts": manifest_counts,
            "write_counts": write_counts,
            "manifest_bytes": manifest_bytes,
            "write_bytes": write_bytes,
        },
    )


def check_reader_bundle_alignment(
    bundle: SessionReadBundle,
    manifest: CaptureSessionManifest,
    *,
    session_date: str,
    config: IntegrityConfig = DEFAULT_INTEGRITY_CONFIG,
) -> IntegrityCheckResult:
    issues: list[str] = []

    if bundle.session_date != session_date:
        issues.append("reader_bundle_session_mismatch")
    if manifest.session_date != session_date:
        issues.append("manifest_session_mismatch")

    manifest_counts = {output.dataset.value: output.row_count for output in manifest.archive_outputs}
    bundle_counts = dict(bundle.dataset_row_counts)

    if config.require_reader_alignment and manifest_counts != bundle_counts:
        issues.append("reader_bundle_row_count_mismatch")

    manifest_datasets = sorted(manifest_counts.keys())
    bundle_datasets = sorted(bundle.dataset_file_paths.keys())
    if config.require_reader_alignment and manifest_datasets != bundle_datasets:
        issues.append("reader_bundle_dataset_path_mismatch")

    status = IntegrityStatus.PASS if not issues else IntegrityStatus.FAIL
    message = "reader bundle aligned" if not issues else "; ".join(issues)

    return IntegrityCheckResult(
        name="reader_bundle_alignment",
        status=status,
        message=message,
        details={
            "session_date": session_date,
            "manifest_counts": manifest_counts,
            "bundle_counts": bundle_counts,
            "manifest_datasets": manifest_datasets,
            "bundle_datasets": bundle_datasets,
        },
    )


def build_integrity_report(
    *,
    session_date: str,
    records: Sequence[CaptureRecord] = (),
    route_plan: RoutePlan | None = None,
    manifest: CaptureSessionManifest | None = None,
    archive_write_result: ArchiveWriteResult | None = None,
    reader_bundle: SessionReadBundle | None = None,
    config: IntegrityConfig = DEFAULT_INTEGRITY_CONFIG,
    notes: Sequence[str] = (),
) -> IntegrityReport:
    _ensure_non_empty_str("session_date", session_date)
    if not isinstance(config, IntegrityConfig):
        raise TypeError("config must be IntegrityConfig")

    checks: list[IntegrityCheckResult] = []

    if records:
        checks.append(check_single_session(records, session_date=session_date))
        checks.append(check_monotonic_event_sequence(records))
        checks.append(check_monotonic_exchange_timestamps(records))
        checks.append(check_runtime_audit_presence(records, config=config))
        checks.append(check_duplicate_snapshot_ids(records, config=config))

    if route_plan is not None:
        checks.append(check_route_plan_alignment(route_plan, records, session_date=session_date, config=config))

    if manifest is not None:
        checks.append(check_manifest_alignment(manifest, session_date=session_date, config=config))

    if archive_write_result is not None:
        if manifest is None:
            raise ValueError("archive_write_result integrity requires manifest")
        checks.append(
            check_archive_write_alignment(
                archive_write_result,
                manifest,
                session_date=session_date,
                config=config,
            )
        )

    if reader_bundle is not None:
        if manifest is None:
            raise ValueError("reader_bundle integrity requires manifest")
        checks.append(
            check_reader_bundle_alignment(
                reader_bundle,
                manifest,
                session_date=session_date,
                config=config,
            )
        )

    if not checks:
        raise ValueError("build_integrity_report requires at least one evaluable component")

    return IntegrityReport(
        session_date=session_date,
        checks=tuple(checks),
        notes=_freeze_str_tuple(notes),
    )


def integrity_report_to_dict(report: IntegrityReport) -> dict[str, Any]:
    return report.to_dict()


__all__ = [
    "DEFAULT_INTEGRITY_CONFIG",
    "IntegrityCheckResult",
    "IntegrityConfig",
    "IntegrityReport",
    "IntegrityStatus",
    "build_integrity_report",
    "check_archive_write_alignment",
    "check_duplicate_snapshot_ids",
    "check_manifest_alignment",
    "check_monotonic_event_sequence",
    "check_monotonic_exchange_timestamps",
    "check_reader_bundle_alignment",
    "check_route_plan_alignment",
    "check_runtime_audit_presence",
    "check_single_session",
    "integrity_report_to_dict",
    "max_integrity_status",
]
