"""
app.mme_scalpx.research_capture.raw_capture_bridge

Freeze-grade real raw-capture bridge for the research-capture chapter.

Ownership
---------
This module OWNS:
- taking the frozen manifest/capture-plan stack and preparing a first real raw record batch
- coercing a minimal raw batch into CaptureRecord objects
- routing the batch into the frozen archive writer
- building canonical manifest / integrity / health surfaces from the real write result
- returning a deterministic raw-capture result

This module DOES NOT own:
- broker connectivity
- live feed polling
- production doctrine mutation
- heavy offline derivations
- non-audit business logic

Design laws
-----------
- raw capture first
- light live-derived second
- heavy offline-derived later
- use frozen archive/manifest/integrity/health surfaces, not ad hoc writes
- required raw outputs and optional audit outputs should flow through the same canonical archive lane
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from app.mme_scalpx.research_capture.capture_plan import (
    CapturePlan,
    build_capture_plan,
)
from app.mme_scalpx.research_capture.config_loader import (
    ConfigRegistry,
    DEFAULT_CONFIG_REGISTRY_PATH,
    load_config_registry,
)
from app.mme_scalpx.research_capture.manifest_materializer import (
    ManifestMaterializationResult,
    build_and_materialize_manifest_seed,
)
from app.mme_scalpx.research_capture.manifest import (
    build_archive_outputs_from_counts,
    build_integrity_summary,
    build_session_manifest,
    build_source_availability_from_records,
    manifest_to_dict,
    validate_manifest_payload,
)
from app.mme_scalpx.research_capture.archive_writer import (
    ArchiveWriteResult,
    write_capture_records,
    write_manifest_files,
)
from app.mme_scalpx.research_capture.integrity import (
    build_integrity_report,
    integrity_report_to_dict,
)
from app.mme_scalpx.research_capture.health import (
    build_capture_health_snapshot,
    health_snapshot_to_dict,
)
from app.mme_scalpx.research_capture.router import (
    ROUTE_RUNTIME_AUDIT,
    ROUTE_SIGNALS_AUDIT,
    build_route_plan,
)
from app.mme_scalpx.research_capture.utils import atomic_write_json


class RawCaptureBridgeError(RuntimeError):
    """Base error for raw-capture bridging."""


@dataclass(frozen=True, slots=True)
class RawCaptureWrittenFile:
    """A file touched or written by the raw-capture bridge."""

    name: str
    path: str

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "path": self.path,
        }


@dataclass(frozen=True, slots=True)
class RawCaptureBridgeResult:
    """Deterministic result of the real raw-capture bridge."""

    entrypoint: str
    lane: str
    source: str
    run_id: str
    rows_written: int
    primary_capture_target: str
    written_files: tuple[RawCaptureWrittenFile, ...]
    capture_plan: CapturePlan
    manifest_materialization_result: ManifestMaterializationResult

    def to_dict(self) -> dict[str, Any]:
        return {
            "entrypoint": self.entrypoint,
            "lane": self.lane,
            "source": self.source,
            "run_id": self.run_id,
            "rows_written": self.rows_written,
            "primary_capture_target": self.primary_capture_target,
            "written_files": [item.to_dict() for item in self.written_files],
            "capture_plan": self.capture_plan.to_dict(),
            "manifest_materialization_result": self.manifest_materialization_result.to_dict(),
        }


def _utc_now_z() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _require_nonempty_str(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RawCaptureBridgeError(f"{name} must be a non-empty string")
    return value.strip()


def _capture_session_date(seed) -> str:
    if seed.session_date:
        return seed.session_date
    if seed.session_dates:
        return seed.session_dates[0]
    if seed.start_date:
        return seed.start_date
    if seed.end_date:
        return seed.end_date
    return date.today().isoformat()


def _report_root(manifest_result: ManifestMaterializationResult) -> Path:
    return Path(manifest_result.manifest_seed.metadata["report_root"]).resolve()


def _default_row_batch(
    *,
    source: str,
    session_date: str,
    instrument_scope: str | None,
) -> list[dict[str, Any]]:
    symbol = instrument_scope or "NIFTY_OPTIONS"
    common = {
        "session_date": session_date,
        "exchange": "NSE",
        "exchange_segment": "NFO",
        "symbol_root": symbol,
        "underlying_symbol": "NIFTY",
        "tick_size": 0.05,
        "lot_size": 75,
        "expiry": "2026-04-23",
        "expiry_type": "weekly",
        "freeze_qty": 1800,
        "strike_step": 50,
        "spot": 22010.0,
        "fut_ltp": 22020.0,
        "trading_minute_index": 1,
        "is_preopen": False,
        "is_postclose": False,
        "weekday": 5,
        "month": 4,
        "spread": 0.10,
        "spread_pct": 0.001,
        "half_spread": 0.05,
        "nof": 0.0,
        "vwap": 100.0,
        "vwap_dist": 0.0,
        "is_stale_tick": False,
        "missing_depth_flag": False,
        "missing_oi_flag": False,
        "crossed_book_flag": False,
        "locked_book_flag": False,
        "integrity_flags": [],
        "schema_version": "v1",
        "normalization_version": "v1",
        "derived_version": "v1",
        "heartbeat_ok": True,
        "runtime_mode": "real_raw_capture_with_audit_routes",
        "candidate_found": False,
        "blocker_found": False,
        "regime_ok": False,
        "broker_name": source,
    }

    rows: list[dict[str, Any]] = []

    rows.append(
        {
            **common,
            "exchange_ts": 1776464700000000001,
            "recv_ts_ns": 1776464700000001001,
            "process_ts_ns": 1776464700000002001,
            "event_seq": 1,
            "snapshot_id": "seed-fut-1",
            "instrument_token": "seed-fut-1",
            "tradingsymbol": f"{symbol}-FUT",
            "symbol": f"{symbol}-FUT",
            "contract_name": f"{symbol}-FUT-CONTRACT",
            "instrument_type": "FUT",
            "option_type": None,
            "strike": None,
            "latency_ns": 1000,
            "gap_from_prev_tick_ms": 0,
            "ltp": 22020.0,
            "volume": 100,
            "oi": 1000,
            "best_bid": 22019.95,
            "best_ask": 22020.05,
            "best_bid_qty": 10,
            "best_ask_qty": 12,
            "mid_price": 22020.0,
            "microprice": 22020.0,
            "bid_prices": [22019.95],
            "bid_qty": [10],
            "ask_prices": [22020.05],
            "ask_qty": [12],
            "depth_levels_present_bid": 1,
            "depth_levels_present_ask": 1,
            "sum_bid_qty": 10,
            "sum_ask_qty": 12,
            "premium": 22020.0,
            "strike_dist_pts": 0.0,
        }
    )

    rows.append(
        {
            **common,
            "exchange_ts": 1776464700000000002,
            "recv_ts_ns": 1776464700000001002,
            "process_ts_ns": 1776464700000002002,
            "event_seq": 2,
            "snapshot_id": "seed-opt-1",
            "instrument_token": "seed-opt-1",
            "tradingsymbol": f"{symbol}-CE-22000",
            "symbol": f"{symbol}-CE-22000",
            "contract_name": f"{symbol}-CE-22000-CONTRACT",
            "instrument_type": "CE",
            "option_type": "CE",
            "strike": 22000,
            "latency_ns": 1000,
            "gap_from_prev_tick_ms": 0,
            "ltp": 100.0,
            "volume": 200,
            "oi": 2000,
            "best_bid": 99.95,
            "best_ask": 100.05,
            "best_bid_qty": 20,
            "best_ask_qty": 22,
            "mid_price": 100.0,
            "microprice": 100.0,
            "bid_prices": [99.95],
            "bid_qty": [20],
            "ask_prices": [100.05],
            "ask_qty": [22],
            "depth_levels_present_bid": 1,
            "depth_levels_present_ask": 1,
            "sum_bid_qty": 20,
            "sum_ask_qty": 22,
            "premium": 100.0,
            "strike_dist_pts": 10.0,
        }
    )

    rows.append(
        {
            **common,
            "exchange_ts": 1776464700000000003,
            "recv_ts_ns": 1776464700000001003,
            "process_ts_ns": 1776464700000002003,
            "event_seq": 3,
            "snapshot_id": "seed-opt-2",
            "instrument_token": "seed-opt-2",
            "tradingsymbol": f"{symbol}-PE-22000",
            "symbol": f"{symbol}-PE-22000",
            "contract_name": f"{symbol}-PE-22000-CONTRACT",
            "instrument_type": "PE",
            "option_type": "PE",
            "strike": 22000,
            "latency_ns": 1000,
            "gap_from_prev_tick_ms": 0,
            "ltp": 101.0,
            "volume": 300,
            "oi": 3000,
            "best_bid": 100.95,
            "best_ask": 101.05,
            "best_bid_qty": 30,
            "best_ask_qty": 32,
            "mid_price": 101.0,
            "microprice": 101.0,
            "bid_prices": [100.95],
            "bid_qty": [30],
            "ask_prices": [101.05],
            "ask_qty": [32],
            "depth_levels_present_bid": 1,
            "depth_levels_present_ask": 1,
            "sum_bid_qty": 30,
            "sum_ask_qty": 32,
            "premium": 101.0,
            "strike_dist_pts": 10.0,
        }
    )

    return rows


def _build_capture_record_via_normalizer(row: Mapping[str, Any]):
    from app.mme_scalpx.research_capture.normalizer import (
        InstrumentReference,
        NormalizationContext,
        RuntimeAuditInput,
        SessionMetadataInput,
        normalize_dhan_tick,
        normalize_zerodha_tick,
    )

    raw = dict(row)

    instrument_reference = InstrumentReference(
        broker_name=_require_nonempty_str(raw["broker_name"], "broker_name"),
        exchange=_require_nonempty_str(raw["exchange"], "exchange"),
        exchange_segment=_require_nonempty_str(raw["exchange_segment"], "exchange_segment"),
        instrument_token=_require_nonempty_str(raw["instrument_token"], "instrument_token"),
        tradingsymbol=_require_nonempty_str(raw["tradingsymbol"], "tradingsymbol"),
        instrument_type=_require_nonempty_str(raw["instrument_type"], "instrument_type"),
        symbol_root=_require_nonempty_str(raw["symbol_root"], "symbol_root"),
        underlying_symbol=_require_nonempty_str(raw["underlying_symbol"], "underlying_symbol"),
        tick_size=float(raw["tick_size"]),
        lot_size=int(raw["lot_size"]),
        symbol=raw.get("symbol"),
        contract_name=raw.get("contract_name"),
        option_type=raw.get("option_type"),
        strike=raw.get("strike"),
        expiry=raw.get("expiry"),
        expiry_type=raw.get("expiry_type"),
        freeze_qty=raw.get("freeze_qty"),
        strike_step=raw.get("strike_step"),
    )

    normalization_context = NormalizationContext(
        session_date=_require_nonempty_str(raw["session_date"], "session_date"),
        recv_ts_ns=int(raw["recv_ts_ns"]),
        process_ts_ns=int(raw["process_ts_ns"]),
        event_seq=int(raw["event_seq"]),
        source_ts_ns=int(raw["exchange_ts"]),
        snapshot_id=_require_nonempty_str(raw["snapshot_id"], "snapshot_id"),
    )

    session_metadata = SessionMetadataInput(
        trading_minute_index=int(raw["trading_minute_index"]),
        is_preopen=bool(raw["is_preopen"]),
        is_postclose=bool(raw["is_postclose"]),
        weekday=int(raw["weekday"]),
        month=int(raw["month"]),
    )

    runtime_audit = RuntimeAuditInput(
        normalization_version=str(raw["normalization_version"]),
        derived_version=str(raw["derived_version"]),
        latency_ns=int(raw["latency_ns"]),
        gap_from_prev_tick_ms=int(raw["gap_from_prev_tick_ms"]),
        heartbeat_status="OK",
    )

    raw_payload = {
        "ltp": raw["ltp"],
        "last_price": raw["ltp"],
        "volume": raw["volume"],
        "volume_traded": raw["volume"],
        "oi": raw["oi"],
        "best_bid": raw["best_bid"],
        "best_ask": raw["best_ask"],
        "best_bid_qty": raw["best_bid_qty"],
        "best_ask_qty": raw["best_ask_qty"],
        "bid_prices": raw["bid_prices"],
        "bid_qty": raw["bid_qty"],
        "ask_prices": raw["ask_prices"],
        "ask_qty": raw["ask_qty"],
        "depth": {
            "buy": [{"price": raw["best_bid"], "quantity": raw["best_bid_qty"]}],
            "sell": [{"price": raw["best_ask"], "quantity": raw["best_ask_qty"]}],
        },
        "tradingsymbol": raw["tradingsymbol"],
        "exchange_timestamp": raw["exchange_ts"],
    }

    broker_name = raw["broker_name"].lower()
    if broker_name == "dhan":
        return normalize_dhan_tick(
            raw_payload=raw_payload,
            instrument_reference=instrument_reference,
            normalization_context=normalization_context,
            session_metadata=session_metadata,
            runtime_audit=runtime_audit,
        )

    return normalize_zerodha_tick(
        raw_payload=raw_payload,
        instrument_reference=instrument_reference,
        normalization_context=normalization_context,
        session_metadata=session_metadata,
        runtime_audit=runtime_audit,
    )


def _build_capture_records(rows: Sequence[Mapping[str, Any]]) -> tuple[Any, ...]:
    records = []
    for row in rows:
        record = _build_capture_record_via_normalizer(row)
        records.append(record)
    return tuple(records)


def _archive_write_result(
    *,
    session_date: str,
    manifest_paths: Mapping[str, str],
    dataset_file_paths: Mapping[str, tuple[str, ...]],
    dataset_row_counts: Mapping[str, int],
    dataset_bytes_written: Mapping[str, int],
) -> ArchiveWriteResult:
    manifest_path = ""
    source_availability_path = ""
    integrity_summary_path = ""

    for key, value in manifest_paths.items():
        v = str(value)
        k = str(key).lower()
        if not manifest_path and ("manifest" in k or v.endswith("manifest.json")):
            manifest_path = v
        if not source_availability_path and ("source" in k or v.endswith("source_availability.json")):
            source_availability_path = v
        if not integrity_summary_path and ("integrity" in k or v.endswith("integrity_summary.json")):
            integrity_summary_path = v

    if not manifest_path or not source_availability_path or not integrity_summary_path:
        raise RawCaptureBridgeError(f"unexpected manifest_paths mapping: {manifest_paths}")

    session_archive_root = str(Path(manifest_path).resolve().parent)
    return ArchiveWriteResult(
        session_date=session_date,
        session_archive_root=session_archive_root,
        manifest_path=manifest_path,
        source_availability_path=source_availability_path,
        integrity_summary_path=integrity_summary_path,
        dataset_file_paths=dataset_file_paths,
        dataset_row_counts=dataset_row_counts,
        dataset_bytes_written=dataset_bytes_written,
    )


def _first_actual_capture_target(dataset_file_paths: Mapping[str, tuple[str, ...]]) -> str:
    flattened = []
    for _, paths in sorted(dataset_file_paths.items()):
        flattened.extend(list(paths))
    if not flattened:
        raise RawCaptureBridgeError("archive writer returned no dataset file paths")
    return str(Path(sorted(flattened)[0]).resolve())


def _write_reports(
    *,
    manifest_result: ManifestMaterializationResult,
    integrity_report,
    health_snapshot,
) -> tuple[Path, Path]:
    report_root = _report_root(manifest_result)
    integrity_report_path = (report_root / "integrity_report.json").resolve()
    health_snapshot_path = (report_root / "health_snapshot.json").resolve()

    atomic_write_json(integrity_report_path, integrity_report_to_dict(integrity_report))
    atomic_write_json(health_snapshot_path, health_snapshot_to_dict(health_snapshot))

    return integrity_report_path, health_snapshot_path


# RC_OPTIONAL_ROUTE_DATASET_RELABEL_HELPERS
def _clone_capture_record_with_dataset(record, dataset_name: str):
    from dataclasses import is_dataclass, replace as dataclass_replace
    from app.mme_scalpx.research_capture.models import CaptureDatasetName

    dataset_enum = (
        dataset_name
        if isinstance(dataset_name, CaptureDatasetName)
        else CaptureDatasetName(str(dataset_name))
    )

    if hasattr(record, "model_copy") and callable(record.model_copy):
        return record.model_copy(update={"dataset": dataset_enum})

    if hasattr(record, "copy") and callable(record.copy):
        try:
            return record.copy(update={"dataset": dataset_enum})
        except TypeError:
            pass

    if is_dataclass(record):
        return dataclass_replace(record, dataset=dataset_enum)

    if hasattr(record, "__dict__"):
        payload = dict(record.__dict__)
        payload["dataset"] = dataset_enum
        return type(record)(**payload)

    raise TypeError(
        f"unsupported capture record type for dataset relabel: {type(record)!r}"
    )


def _records_for_optional_dataset(records, dataset_name: str):
    return tuple(
        _clone_capture_record_with_dataset(record, dataset_name)
        for record in records
    )


def _optional_dataset_root(
    *,
    session_date: str,
    dataset_name: str,
    archive_root_relative: str = "run/research_capture",
) -> Path:
    return (Path(archive_root_relative) / session_date / dataset_name).resolve()


def _purge_optional_dataset_if_absent(
    *,
    session_date: str,
    dataset_name: str,
    archive_root_relative: str = "run/research_capture",
) -> None:
    dataset_root = _optional_dataset_root(
        session_date=session_date,
        dataset_name=dataset_name,
        archive_root_relative=archive_root_relative,
    )
    if dataset_root.exists():
        shutil.rmtree(dataset_root)


def _write_route_optional_outputs(
    *,
    route_plan,
    capture_plan: CapturePlan,
    session_date: str,
) -> tuple[Mapping[str, tuple[str, ...]], Mapping[str, int], Mapping[str, int]]:
    route_buckets = dict(route_plan.items())

    runtime_records = tuple(route_buckets.get(ROUTE_RUNTIME_AUDIT, ()))
    signals_records = tuple(route_buckets.get(ROUTE_SIGNALS_AUDIT, ()))

    merged_file_paths: dict[str, tuple[str, ...]] = {}
    merged_row_counts: dict[str, int] = {}
    merged_bytes: dict[str, int] = {}

    optional_targets = {item.name for item in capture_plan.optional_outputs}

    if "runtime_audit.parquet" in optional_targets and not runtime_records:
        _purge_optional_dataset_if_absent(
            session_date=session_date,
            dataset_name="runtime_audit",
        )

    if runtime_records and "runtime_audit.parquet" in optional_targets:
        runtime_dataset_records = _records_for_optional_dataset(
            runtime_records,
            "runtime_audit",
        )
        file_paths, row_counts, bytes_written = write_capture_records(
            runtime_dataset_records,
            archive_root_relative="run/research_capture",
            partition_columns=None,
            write_mode="overwrite",
            compression="snappy",
        )
        merged_file_paths.update(file_paths)
        merged_row_counts.update(row_counts)
        merged_bytes.update(bytes_written)

    if "signals_audit.parquet" in optional_targets and not signals_records:
        _purge_optional_dataset_if_absent(
            session_date=session_date,
            dataset_name="signals_audit",
        )

    if signals_records and "signals_audit.parquet" in optional_targets:
        signals_dataset_records = _records_for_optional_dataset(
            signals_records,
            "signals_audit",
        )
        file_paths, row_counts, bytes_written = write_capture_records(
            signals_dataset_records,
            archive_root_relative="run/research_capture",
            partition_columns=None,
            write_mode="overwrite",
            compression="snappy",
        )
        merged_file_paths.update(file_paths)
        merged_row_counts.update(row_counts)
        merged_bytes.update(bytes_written)

    return merged_file_paths, merged_row_counts, merged_bytes

def run_first_real_raw_capture(
    entrypoint: str,
    *,
    run_id: str,
    session_date: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    session_dates: Sequence[str] | None = None,
    instrument_scope: str | None = None,
    research_profile: str | None = None,
    feature_families: Sequence[str] | None = None,
    notes: str | None = None,
    lane_override: str | None = None,
    source_override: str | None = None,
    export_format_overrides: Mapping[str, str] | None = None,
    batch_rows: Sequence[Mapping[str, Any]] | None = None,
    registry: ConfigRegistry | None = None,
    config_registry_path: Path | str = DEFAULT_CONFIG_REGISTRY_PATH,
    project_root: Path | None = None,
) -> RawCaptureBridgeResult:
    reg = registry if registry is not None else load_config_registry(
        config_registry_path,
        project_root=project_root,
    )

    manifest_result = build_and_materialize_manifest_seed(
        entrypoint,
        run_id=run_id,
        session_date=session_date,
        start_date=start_date,
        end_date=end_date,
        session_dates=session_dates,
        instrument_scope=instrument_scope,
        research_profile=research_profile,
        feature_families=feature_families,
        notes=notes,
        lane_override=lane_override,
        source_override=source_override,
        export_format_overrides=export_format_overrides,
        registry=reg,
        project_root=project_root,
    )
    capture_plan = build_capture_plan(
        manifest_result,
        registry=reg,
        project_root=project_root,
    )

    if entrypoint not in {"run", "backfill"}:
        raise RawCaptureBridgeError(f"real raw capture only supports run/backfill, got {entrypoint}")

    if not capture_plan.required_outputs:
        raise RawCaptureBridgeError(
            f"entrypoint={entrypoint} lane={capture_plan.lane} has no required raw capture targets"
        )

    seed = manifest_result.manifest_seed
    capture_session_date = _capture_session_date(seed)

    rows = list(batch_rows) if batch_rows is not None else _default_row_batch(
        source=seed.source,
        session_date=capture_session_date,
        instrument_scope=seed.session_materialization_result.session_context.session_inputs.instrument_scope,
    )
    if not rows:
        raise RawCaptureBridgeError("raw capture batch is empty")

    records = _build_capture_records(rows)

    dataset_file_paths, dataset_row_counts, dataset_bytes_written = write_capture_records(
        records,
        archive_root_relative="run/research_capture",
        partition_columns=None,
        write_mode="overwrite",
        compression="snappy",
    )

    route_plan = build_route_plan(records)

    optional_targets = {item.name for item in capture_plan.optional_outputs}
    optional_integrity_records: list[object] = []

    runtime_route_records = tuple(route_plan.get(ROUTE_RUNTIME_AUDIT, ()))
    if runtime_route_records and "runtime_audit.parquet" in optional_targets:
        optional_integrity_records.extend(
            _records_for_optional_dataset(runtime_route_records, "runtime_audit")
        )

    signals_route_records = tuple(route_plan.get(ROUTE_SIGNALS_AUDIT, ()))
    if signals_route_records and "signals_audit.parquet" in optional_targets:
        optional_integrity_records.extend(
            _records_for_optional_dataset(signals_route_records, "signals_audit")
        )

    optional_file_paths, optional_row_counts, optional_bytes_written = _write_route_optional_outputs(
        route_plan=route_plan,
        capture_plan=capture_plan,
        session_date=capture_session_date,
    )

    merged_file_paths = dict(dataset_file_paths)
    merged_row_counts = dict(dataset_row_counts)
    merged_bytes_written = dict(dataset_bytes_written)

    merged_file_paths.update(optional_file_paths)
    merged_row_counts.update(optional_row_counts)
    merged_bytes_written.update(optional_bytes_written)

    source_availability = build_source_availability_from_records(
        records,
        extra_sources={seed.source: True},
        notes=("real_raw_capture_with_audit_routes",),
    )
    integrity_records = tuple(records) + tuple(optional_integrity_records)
    integrity_summary = build_integrity_summary(
        records=integrity_records,
        warnings=(),
        errors=(),
    )
    archive_outputs = build_archive_outputs_from_counts(
        dataset_row_counts=merged_row_counts,
        bytes_written_by_dataset=merged_bytes_written,
        include_zero_count_outputs=False,
    )
    manifest = build_session_manifest(
        session_date=capture_session_date,
        source_availability=source_availability,
        integrity_summary=integrity_summary,
        archive_outputs=archive_outputs,
        created_at=_utc_now_z(),
        status="session_written",
        notes=("real_raw_capture_with_audit_routes",),
    )
    validate_manifest_payload(manifest_to_dict(manifest))

    manifest_paths = write_manifest_files(
        manifest,
        archive_root_relative="run/research_capture",
    )

    archive_write_result = _archive_write_result(
        session_date=capture_session_date,
        manifest_paths=manifest_paths,
        dataset_file_paths=merged_file_paths,
        dataset_row_counts=merged_row_counts,
        dataset_bytes_written=merged_bytes_written,
    )

    integrity_report = build_integrity_report(
        session_date=capture_session_date,
        records=records,
        route_plan=route_plan,
        manifest=manifest,
        archive_write_result=archive_write_result,
        notes=("real_raw_capture_with_audit_routes",),
    )
    health_snapshot = build_capture_health_snapshot(
        session_date=capture_session_date,
        source_availability=source_availability,
        integrity_summary=integrity_summary,
        manifest=manifest,
        route_plan=route_plan,
        archive_write_result=archive_write_result,
        notes=("real_raw_capture_with_audit_routes",),
    )
    integrity_report_path, health_snapshot_path = _write_reports(
        manifest_result=manifest_result,
        integrity_report=integrity_report,
        health_snapshot=health_snapshot,
    )

    primary_capture_target = _first_actual_capture_target(merged_file_paths)

    written_files: list[RawCaptureWrittenFile] = []
    seen_paths: set[str] = set()

    for paths in merged_file_paths.values():
        for raw_path in paths:
            p = str(Path(raw_path).resolve())
            if p in seen_paths:
                continue
            seen_paths.add(p)
            written_files.append(RawCaptureWrittenFile(name=Path(p).name, path=p))

    for _, value in manifest_paths.items():
        p = str(Path(value).resolve())
        if p in seen_paths:
            continue
        seen_paths.add(p)
        written_files.append(RawCaptureWrittenFile(name=Path(p).name, path=p))

    for extra_path in (str(integrity_report_path), str(health_snapshot_path)):
        if extra_path in seen_paths:
            continue
        seen_paths.add(extra_path)
        written_files.append(RawCaptureWrittenFile(name=Path(extra_path).name, path=extra_path))

    return RawCaptureBridgeResult(
        entrypoint=manifest_result.entrypoint,
        lane=manifest_result.lane,
        source=manifest_result.source,
        run_id=manifest_result.run_id,
        rows_written=len(records),
        primary_capture_target=primary_capture_target,
        written_files=tuple(written_files),
        capture_plan=capture_plan,
        manifest_materialization_result=manifest_result,
    )


__all__ = [
    "RawCaptureBridgeError",
    "RawCaptureWrittenFile",
    "RawCaptureBridgeResult",
    "run_first_real_raw_capture",
]
