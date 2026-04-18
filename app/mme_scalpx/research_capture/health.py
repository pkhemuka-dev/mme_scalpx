from __future__ import annotations

"""
app/mme_scalpx/research_capture/health.py

Frozen health layer for the MME research data capture chapter.

Purpose
-------
This module owns deterministic health/readiness evaluation for the research
capture subsystem. It converts source availability, integrity summaries,
route plans, manifests, and archive-write results into immutable health
checks and one overall health snapshot.

Owns
----
- health status enums
- health threshold/config surface
- immutable health check objects
- deterministic health evaluation helpers
- overall capture health snapshot construction

Does not own
------------
- broker IO
- Redis IO
- parquet writing
- archive writing
- normalization
- enrichment
- routing logic
- production strategy doctrine

Design laws
-----------
- health evaluation must be deterministic and side-effect free by default
- health must summarize, not mutate, upstream objects
- manifest/archive validation must stay aligned with the frozen contracts
- health must clearly separate OK / WARN / ERROR states
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence

from app.mme_scalpx.research_capture.archive_writer import ArchiveWriteResult
from app.mme_scalpx.research_capture.contracts import MANIFEST_REQUIRED_KEYS
from app.mme_scalpx.research_capture.models import (
    CaptureSessionManifest,
    IntegritySummary,
    SourceAvailability,
)
from app.mme_scalpx.research_capture.router import (
    ROUTE_RUNTIME_AUDIT,
    ROUTE_TICKS_FUT,
    ROUTE_TICKS_OPT,
    RoutePlan,
)


def _ensure_non_empty_str(name: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty str")
    return value


def _ensure_bool(name: str, value: bool) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{name} must be bool")
    return value


def _ensure_int(name: str, value: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be int")
    return value


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return float(numerator) / float(denominator)


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


class HealthStatus(str, Enum):
    OK = "OK"
    WARN = "WARN"
    ERROR = "ERROR"


_STATUS_RANK: Mapping[HealthStatus, int] = {
    HealthStatus.OK: 0,
    HealthStatus.WARN: 1,
    HealthStatus.ERROR: 2,
}


def max_health_status(statuses: Iterable[HealthStatus]) -> HealthStatus:
    statuses_tuple = tuple(statuses)
    if not statuses_tuple:
        return HealthStatus.OK
    return max(statuses_tuple, key=lambda status: _STATUS_RANK[status])


@dataclass(frozen=True, slots=True)
class HealthConfig:
    """
    Frozen health threshold/config surface.
    """
    require_records_present: bool = True
    require_broker_presence: bool = True
    require_dataset_presence: bool = True
    require_runtime_audit_route: bool = True
    verify_filesystem_paths: bool = False

    warn_stale_tick_ratio: float = 0.01
    error_stale_tick_ratio: float = 0.10

    warn_missing_depth_ratio: float = 0.02
    error_missing_depth_ratio: float = 0.20

    warn_missing_oi_ratio: float = 0.05
    error_missing_oi_ratio: float = 0.30

    warn_thin_book_ratio: float = 0.10
    error_thin_book_ratio: float = 0.50

    def __post_init__(self) -> None:
        for name in (
            "require_records_present",
            "require_broker_presence",
            "require_dataset_presence",
            "require_runtime_audit_route",
            "verify_filesystem_paths",
        ):
            _ensure_bool(name, getattr(self, name))

        for warn_name, error_name in (
            ("warn_stale_tick_ratio", "error_stale_tick_ratio"),
            ("warn_missing_depth_ratio", "error_missing_depth_ratio"),
            ("warn_missing_oi_ratio", "error_missing_oi_ratio"),
            ("warn_thin_book_ratio", "error_thin_book_ratio"),
        ):
            warn_value = getattr(self, warn_name)
            error_value = getattr(self, error_name)
            if not isinstance(warn_value, (int, float)) or isinstance(warn_value, bool):
                raise TypeError(f"{warn_name} must be numeric")
            if not isinstance(error_value, (int, float)) or isinstance(error_value, bool):
                raise TypeError(f"{error_name} must be numeric")
            if not (0.0 <= float(warn_value) <= float(error_value) <= 1.0):
                raise ValueError(f"{warn_name}/{error_name} thresholds are invalid")


DEFAULT_HEALTH_CONFIG = HealthConfig()


@dataclass(frozen=True, slots=True)
class HealthCheckResult:
    """
    Immutable health check result for one subsystem aspect.
    """
    name: str
    status: HealthStatus
    message: str
    details: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        _ensure_non_empty_str("name", self.name)
        if not isinstance(self.status, HealthStatus):
            raise TypeError("status must be HealthStatus")
        _ensure_non_empty_str("message", self.message)
        object.__setattr__(self, "details", _freeze_mapping(self.details))

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": dict(self.details),
        }


@dataclass(frozen=True, slots=True)
class CaptureHealthSnapshot:
    """
    Immutable overall health snapshot for one capture session.
    """
    session_date: str
    checks: tuple[HealthCheckResult, ...]
    status: HealthStatus | None = None
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _ensure_non_empty_str("session_date", self.session_date)
        object.__setattr__(self, "checks", tuple(self.checks))
        object.__setattr__(self, "notes", _freeze_str_tuple(self.notes))

        if not self.checks:
            raise ValueError("checks must be non-empty")
        seen: set[str] = set()
        for check in self.checks:
            if not isinstance(check, HealthCheckResult):
                raise TypeError("checks must contain only HealthCheckResult instances")
            if check.name in seen:
                raise ValueError(f"duplicate health check name: {check.name}")
            seen.add(check.name)
        computed_status = max_health_status(check.status for check in self.checks)
        if self.status is None:
            object.__setattr__(self, "status", computed_status)
        else:
            if not isinstance(self.status, HealthStatus):
                raise TypeError("status must be HealthStatus or None")
            if _STATUS_RANK[self.status] != _STATUS_RANK[computed_status]:
                raise ValueError(
                    f"provided snapshot status {self.status.value} does not match computed status {computed_status.value}"
                )

    @property
    def checks_by_name(self) -> Mapping[str, HealthCheckResult]:
        return MappingProxyType({check.name: check for check in self.checks})

    @property
    def status_counts(self) -> Mapping[str, int]:
        counts: dict[str, int] = {HealthStatus.OK.value: 0, HealthStatus.WARN.value: 0, HealthStatus.ERROR.value: 0}
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


def evaluate_source_availability(
    source_availability: SourceAvailability,
    *,
    config: HealthConfig = DEFAULT_HEALTH_CONFIG,
) -> HealthCheckResult:
    sources = dict(source_availability.sources)
    counts = dict(source_availability.counts)

    records_present = bool(sources.get("records_present", False))
    brokers_present = int(sources.get("brokers_present", 0) or 0)
    datasets_present = int(sources.get("datasets_present", 0) or 0)

    status = HealthStatus.OK
    messages: list[str] = []

    if config.require_records_present and not records_present:
        status = HealthStatus.ERROR
        messages.append("records_present=false")
    if config.require_broker_presence and brokers_present <= 0:
        status = HealthStatus.ERROR
        messages.append("brokers_present<=0")
    if config.require_dataset_presence and datasets_present <= 0:
        status = HealthStatus.ERROR
        messages.append("datasets_present<=0")

    false_flags = sorted(
        key for key, value in sources.items()
        if isinstance(value, bool) and value is False and key not in {"records_present"}
    )
    if false_flags and status is HealthStatus.OK:
        status = HealthStatus.WARN
        messages.append(f"false_source_flags={','.join(false_flags)}")

    message = "source availability healthy" if not messages else "; ".join(messages)

    return HealthCheckResult(
        name="source_availability",
        status=status,
        message=message,
        details={
            "records_present": records_present,
            "brokers_present": brokers_present,
            "datasets_present": datasets_present,
            "source_keys": sorted(sources.keys()),
            "count_keys": sorted(counts.keys()),
            "notes": list(source_availability.notes),
        },
    )


def evaluate_integrity_summary(
    integrity_summary: IntegritySummary,
    *,
    config: HealthConfig = DEFAULT_HEALTH_CONFIG,
) -> HealthCheckResult:
    total_records = integrity_summary.total_records
    stale_ratio = _ratio(integrity_summary.stale_tick_count, total_records)
    missing_depth_ratio = _ratio(integrity_summary.missing_depth_count, total_records)
    missing_oi_ratio = _ratio(integrity_summary.missing_oi_count, total_records)
    thin_book_ratio = _ratio(integrity_summary.thin_book_count, total_records)

    status = HealthStatus.OK
    messages: list[str] = []

    if total_records <= 0:
        status = HealthStatus.ERROR
        messages.append("total_records<=0")

    if integrity_summary.errors:
        status = HealthStatus.ERROR
        messages.append("integrity_summary.errors_present")

    def _apply_threshold(
        current_status: HealthStatus,
        *,
        ratio_name: str,
        ratio_value: float,
        warn_threshold: float,
        error_threshold: float,
    ) -> HealthStatus:
        if ratio_value >= error_threshold:
            messages.append(f"{ratio_name}>={error_threshold:.4f}")
            return HealthStatus.ERROR
        if ratio_value >= warn_threshold and current_status is HealthStatus.OK:
            messages.append(f"{ratio_name}>={warn_threshold:.4f}")
            return HealthStatus.WARN
        return current_status

    status = _apply_threshold(
        status,
        ratio_name="stale_ratio",
        ratio_value=stale_ratio,
        warn_threshold=float(config.warn_stale_tick_ratio),
        error_threshold=float(config.error_stale_tick_ratio),
    )
    status = _apply_threshold(
        status,
        ratio_name="missing_depth_ratio",
        ratio_value=missing_depth_ratio,
        warn_threshold=float(config.warn_missing_depth_ratio),
        error_threshold=float(config.error_missing_depth_ratio),
    )
    status = _apply_threshold(
        status,
        ratio_name="missing_oi_ratio",
        ratio_value=missing_oi_ratio,
        warn_threshold=float(config.warn_missing_oi_ratio),
        error_threshold=float(config.error_missing_oi_ratio),
    )
    status = _apply_threshold(
        status,
        ratio_name="thin_book_ratio",
        ratio_value=thin_book_ratio,
        warn_threshold=float(config.warn_thin_book_ratio),
        error_threshold=float(config.error_thin_book_ratio),
    )

    if integrity_summary.warnings and status is HealthStatus.OK:
        status = HealthStatus.WARN
        messages.append("integrity_summary.warnings_present")

    message = "integrity summary healthy" if not messages else "; ".join(messages)

    return HealthCheckResult(
        name="integrity_summary",
        status=status,
        message=message,
        details={
            "total_records": total_records,
            "dataset_row_counts": dict(integrity_summary.dataset_row_counts),
            "stale_tick_count": integrity_summary.stale_tick_count,
            "missing_depth_count": integrity_summary.missing_depth_count,
            "missing_oi_count": integrity_summary.missing_oi_count,
            "thin_book_count": integrity_summary.thin_book_count,
            "stale_ratio": stale_ratio,
            "missing_depth_ratio": missing_depth_ratio,
            "missing_oi_ratio": missing_oi_ratio,
            "thin_book_ratio": thin_book_ratio,
            "integrity_flag_counts": dict(integrity_summary.integrity_flag_counts),
            "warnings": list(integrity_summary.warnings),
            "errors": list(integrity_summary.errors),
        },
    )


def evaluate_manifest(
    manifest: CaptureSessionManifest,
    *,
    config: HealthConfig = DEFAULT_HEALTH_CONFIG,
) -> HealthCheckResult:
    payload = manifest.to_dict()

    missing_required = [key for key in MANIFEST_REQUIRED_KEYS if key not in payload]
    archive_output_counts = {output.dataset.value: output.row_count for output in manifest.archive_outputs}
    integrity_counts = dict(manifest.integrity_summary.dataset_row_counts)

    mismatched_datasets = sorted(
        dataset_name
        for dataset_name, count in archive_output_counts.items()
        if integrity_counts.get(dataset_name) != count
    )

    status = HealthStatus.OK
    messages: list[str] = []

    if missing_required:
        status = HealthStatus.ERROR
        messages.append(f"missing_required={','.join(missing_required)}")

    if not manifest.archive_outputs:
        status = HealthStatus.ERROR
        messages.append("archive_outputs_empty")

    if mismatched_datasets:
        status = HealthStatus.ERROR
        messages.append(f"row_count_mismatch={','.join(mismatched_datasets)}")

    if payload.get("status", "").lower() in {"failed", "error"} and status is not HealthStatus.ERROR:
        status = HealthStatus.WARN
        messages.append(f"manifest_status={payload.get('status')}")

    message = "manifest healthy" if not messages else "; ".join(messages)

    return HealthCheckResult(
        name="manifest",
        status=status,
        message=message,
        details={
            "session_date": manifest.session_date,
            "archive_output_count": len(manifest.archive_outputs),
            "archive_output_datasets": sorted(archive_output_counts.keys()),
            "row_counts": archive_output_counts,
            "integrity_row_counts": integrity_counts,
            "manifest_status": payload.get("status"),
        },
    )


def evaluate_route_plan(
    route_plan: RoutePlan,
    *,
    config: HealthConfig = DEFAULT_HEALTH_CONFIG,
) -> HealthCheckResult:
    route_keys = list(route_plan.keys())
    counts = dict(route_plan.counts)

    tick_route_count = counts.get(ROUTE_TICKS_FUT, 0) + counts.get(ROUTE_TICKS_OPT, 0)
    runtime_route_count = counts.get(ROUTE_RUNTIME_AUDIT, 0)

    status = HealthStatus.OK
    messages: list[str] = []

    if tick_route_count <= 0:
        status = HealthStatus.ERROR
        messages.append("no_tick_routes")
    if config.require_runtime_audit_route and runtime_route_count <= 0:
        if status is not HealthStatus.ERROR:
            status = HealthStatus.WARN
        messages.append("runtime_audit_route_missing")

    message = "route plan healthy" if not messages else "; ".join(messages)

    return HealthCheckResult(
        name="route_plan",
        status=status,
        message=message,
        details={
            "session_date": route_plan.session_date,
            "route_keys": route_keys,
            "route_counts": counts,
        },
    )


def evaluate_archive_write_result(
    archive_write_result: ArchiveWriteResult,
    *,
    config: HealthConfig = DEFAULT_HEALTH_CONFIG,
) -> HealthCheckResult:
    dataset_file_paths = dict(archive_write_result.dataset_file_paths)
    dataset_row_counts = dict(archive_write_result.dataset_row_counts)
    dataset_bytes_written = dict(archive_write_result.dataset_bytes_written)

    status = HealthStatus.OK
    messages: list[str] = []

    if not dataset_file_paths:
        status = HealthStatus.ERROR
        messages.append("dataset_file_paths_empty")

    bad_row_counts = sorted(
        dataset_name for dataset_name, count in dataset_row_counts.items() if count <= 0
    )
    if bad_row_counts:
        status = HealthStatus.ERROR
        messages.append(f"nonpositive_row_counts={','.join(bad_row_counts)}")

    bad_bytes = sorted(
        dataset_name for dataset_name, count in dataset_bytes_written.items() if count <= 0
    )
    if bad_bytes:
        status = HealthStatus.ERROR
        messages.append(f"nonpositive_bytes={','.join(bad_bytes)}")

    if config.verify_filesystem_paths:
        missing_paths: list[str] = []
        for path_str in (
            archive_write_result.manifest_path,
            archive_write_result.source_availability_path,
            archive_write_result.integrity_summary_path,
        ):
            if not Path(path_str).exists():
                missing_paths.append(path_str)
        for paths in dataset_file_paths.values():
            for path_str in paths:
                if not Path(path_str).exists():
                    missing_paths.append(path_str)
        if missing_paths:
            status = HealthStatus.ERROR
            messages.append("missing_filesystem_paths")

    message = "archive write result healthy" if not messages else "; ".join(messages)

    return HealthCheckResult(
        name="archive_write_result",
        status=status,
        message=message,
        details={
            "session_date": archive_write_result.session_date,
            "session_archive_root": archive_write_result.session_archive_root,
            "manifest_path": archive_write_result.manifest_path,
            "source_availability_path": archive_write_result.source_availability_path,
            "integrity_summary_path": archive_write_result.integrity_summary_path,
            "dataset_file_paths": {k: list(v) for k, v in dataset_file_paths.items()},
            "dataset_row_counts": dataset_row_counts,
            "dataset_bytes_written": dataset_bytes_written,
            "verify_filesystem_paths": config.verify_filesystem_paths,
        },
    )


def build_capture_health_snapshot(
    *,
    session_date: str,
    source_availability: SourceAvailability | None = None,
    integrity_summary: IntegritySummary | None = None,
    manifest: CaptureSessionManifest | None = None,
    route_plan: RoutePlan | None = None,
    archive_write_result: ArchiveWriteResult | None = None,
    config: HealthConfig = DEFAULT_HEALTH_CONFIG,
    notes: Sequence[str] = (),
) -> CaptureHealthSnapshot:
    _ensure_non_empty_str("session_date", session_date)
    if not isinstance(config, HealthConfig):
        raise TypeError("config must be HealthConfig")

    checks: list[HealthCheckResult] = []

    derived_source_availability = source_availability
    derived_integrity_summary = integrity_summary

    if manifest is not None:
        if manifest.session_date != session_date:
            raise ValueError(
                f"manifest.session_date {manifest.session_date!r} != session_date {session_date!r}"
            )
        checks.append(evaluate_manifest(manifest, config=config))
        if derived_source_availability is None:
            derived_source_availability = manifest.source_availability
        if derived_integrity_summary is None:
            derived_integrity_summary = manifest.integrity_summary

    if derived_source_availability is not None:
        checks.append(evaluate_source_availability(derived_source_availability, config=config))

    if derived_integrity_summary is not None:
        checks.append(evaluate_integrity_summary(derived_integrity_summary, config=config))

    if route_plan is not None:
        if route_plan.session_date is not None and route_plan.session_date != session_date:
            raise ValueError(
                f"route_plan.session_date {route_plan.session_date!r} != session_date {session_date!r}"
            )
        checks.append(evaluate_route_plan(route_plan, config=config))

    if archive_write_result is not None:
        if archive_write_result.session_date != session_date:
            raise ValueError(
                f"archive_write_result.session_date {archive_write_result.session_date!r} != session_date {session_date!r}"
            )
        checks.append(evaluate_archive_write_result(archive_write_result, config=config))

    if not checks:
        raise ValueError("build_capture_health_snapshot requires at least one evaluable component")

    return CaptureHealthSnapshot(
        session_date=session_date,
        checks=tuple(checks),
        notes=_freeze_str_tuple(notes),
    )


def health_snapshot_to_dict(snapshot: CaptureHealthSnapshot) -> dict[str, Any]:
    return snapshot.to_dict()


__all__ = [
    "CaptureHealthSnapshot",
    "DEFAULT_HEALTH_CONFIG",
    "HealthCheckResult",
    "HealthConfig",
    "HealthStatus",
    "build_capture_health_snapshot",
    "evaluate_archive_write_result",
    "evaluate_integrity_summary",
    "evaluate_manifest",
    "evaluate_route_plan",
    "evaluate_source_availability",
    "health_snapshot_to_dict",
    "max_health_status",
]
