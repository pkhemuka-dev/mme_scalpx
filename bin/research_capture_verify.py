from __future__ import annotations

"""
bin/research_capture_verify.py

Freeze-grade verification entrypoint for the MME research data capture chapter.

Purpose
-------
This script proves the frozen research-capture stack end to end using synthetic,
deterministic inputs. It exercises:

- normalizer.py
- enricher.py
- router.py
- archive_writer.py
- reader.py
- health.py
- integrity.py
- utils.py

The verifier is intended as a doctor/smoke entrypoint for the chapter, not a
live runtime.

Design laws
-----------
- deterministic inputs
- no broker connectivity
- no Redis dependency
- archive writes only into an explicit archive root
- non-zero exit code on verification failure
"""

import argparse
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.research_capture import archive_writer
from app.mme_scalpx.research_capture import enricher
from app.mme_scalpx.research_capture import health
from app.mme_scalpx.research_capture import integrity
from app.mme_scalpx.research_capture import normalizer
from app.mme_scalpx.research_capture import reader
from app.mme_scalpx.research_capture import router
from app.mme_scalpx.research_capture import utils


def _ensure_non_empty_str(name: str, value: str) -> str:
    return utils.ensure_non_empty_str(name, value)


def _freeze_mapping(values: Mapping[str, Any] | None = None) -> Mapping[str, Any]:
    return utils.freeze_mapping(values)


@dataclass(frozen=True, slots=True)
class VerificationResult:
    session_date: str
    archive_root: str
    session_root: str
    report_path: str
    verify_ok: bool
    health_status: str
    integrity_status: str
    route_counts: Mapping[str, int]
    dataset_row_counts: Mapping[str, int]

    def __post_init__(self) -> None:
        _ensure_non_empty_str("session_date", self.session_date)
        _ensure_non_empty_str("archive_root", self.archive_root)
        _ensure_non_empty_str("session_root", self.session_root)
        _ensure_non_empty_str("report_path", self.report_path)
        if not isinstance(self.verify_ok, bool):
            raise TypeError("verify_ok must be bool")
        _ensure_non_empty_str("health_status", self.health_status)
        _ensure_non_empty_str("integrity_status", self.integrity_status)
        object.__setattr__(self, "route_counts", _freeze_mapping(self.route_counts))
        object.__setattr__(self, "dataset_row_counts", _freeze_mapping(self.dataset_row_counts))

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_date": self.session_date,
            "archive_root": self.archive_root,
            "session_root": self.session_root,
            "report_path": self.report_path,
            "verify_ok": self.verify_ok,
            "health_status": self.health_status,
            "integrity_status": self.integrity_status,
            "route_counts": dict(self.route_counts),
            "dataset_row_counts": dict(self.dataset_row_counts),
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Freeze-grade verifier for the research_capture chapter."
    )
    parser.add_argument(
        "--session-date",
        required=True,
        help="Session date in YYYY-MM-DD.",
    )
    parser.add_argument(
        "--archive-root",
        default="run/_smokes/research_capture_verify",
        help="Archive root to use for verification artifacts.",
    )
    parser.add_argument(
        "--report-name",
        default="verify_report.json",
        help="Verification report filename under the session root.",
    )
    parser.add_argument(
        "--keep-existing",
        action="store_true",
        help="Do not delete the existing session root before verification.",
    )
    return parser


def _build_refs() -> tuple[normalizer.InstrumentReference, normalizer.InstrumentReference]:
    fut_ref = normalizer.InstrumentReference(
        broker_name="zerodha",
        exchange="NFO",
        exchange_segment="NFO",
        instrument_token=123456,
        tradingsymbol="NIFTY24APR26FUT",
        instrument_type="FUT",
        symbol_root="NIFTY",
        underlying_symbol="NIFTY",
        tick_size=0.05,
        lot_size=75,
        expiry="2026-04-23",
        expiry_type="weekly",
    )

    opt_ref = normalizer.InstrumentReference(
        broker_name="dhan",
        exchange="NFO",
        exchange_segment="NFO",
        instrument_token="789012",
        tradingsymbol="NIFTY23500CE",
        instrument_type="CE",
        symbol_root="NIFTY",
        underlying_symbol="NIFTY",
        option_type="CE",
        strike=23500,
        tick_size=0.05,
        lot_size=75,
        expiry="2026-04-23",
        expiry_type="weekly",
    )
    return fut_ref, opt_ref


def _build_shared_contexts(
    session_date: str,
) -> tuple[
    normalizer.AnchorContextInput,
    normalizer.SessionMetadataInput,
    normalizer.RuntimeAuditInput,
]:
    anchors = normalizer.AnchorContextInput(
        spot_symbol="NSE:NIFTY 50",
        spot=22490.0,
        spot_ts=1776500000.0,
        fut_symbol="NIFTY24APR26FUT",
        fut_ltp=22500.0,
        fut_vol=100,
        fut_ts=1776500000.0,
        vix=15.2,
        vix_ts=1776500000.0,
    )

    session_meta = normalizer.SessionMetadataInput(
        market_open="09:15",
        market_close="15:30",
        is_expiry=False,
        dte=5,
        days_to_expiry_exact=5.0,
        is_current_week=True,
        is_next_week=False,
        is_monthly_expiry=False,
        trading_minute_index=1,
        is_preopen=False,
        is_postclose=False,
        weekday=6,
        month=4,
        expiry_week_flag=True,
    )

    runtime = normalizer.RuntimeAuditInput(
        normalization_version="v1",
        derived_version="v1_minimal",
        latency_ns=1000,
        gap_from_prev_tick_ms=0,
    )
    return anchors, session_meta, runtime


def _build_normalization_context(
    *,
    session_date: str,
    exchange_ts_seconds: float,
    event_seq: int,
    snapshot_id: str,
) -> normalizer.NormalizationContext:
    recv_ts_ns = int(exchange_ts_seconds * 1_000_000_000)
    process_ts_ns = recv_ts_ns + 1000
    return normalizer.NormalizationContext(
        session_date=session_date,
        recv_ts_ns=recv_ts_ns,
        process_ts_ns=process_ts_ns,
        event_seq=event_seq,
        source_ts_ns=recv_ts_ns,
        snapshot_id=snapshot_id,
        processed_ts=exchange_ts_seconds + 0.001,
        network_time=exchange_ts_seconds + 0.001,
    )


def _build_synthetic_records(session_date: str) -> tuple[normalizer.CaptureRecord, ...]:
    fut_ref, opt_ref = _build_refs()
    anchors, session_meta, runtime = _build_shared_contexts(session_date)

    fut_raw_1 = {
        "exchange_timestamp": 1776500000.0,
        "last_price": 22500.0,
        "volume_traded": 100,
        "oi": 5000,
        "depth": {
            "buy": [
                {"price": 22499.95, "quantity": 10},
                {"price": 22499.90, "quantity": 15},
            ],
            "sell": [
                {"price": 22500.05, "quantity": 12},
                {"price": 22500.10, "quantity": 18},
            ],
        },
    }

    fut_raw_2 = {
        "exchange_timestamp": 1776500001.0,
        "last_price": 22501.0,
        "volume_traded": 130,
        "oi": 5010,
        "depth": {
            "buy": [
                {"price": 22500.95, "quantity": 14},
                {"price": 22500.90, "quantity": 16},
            ],
            "sell": [
                {"price": 22501.05, "quantity": 11},
                {"price": 22501.10, "quantity": 19},
            ],
        },
    }

    opt_raw = {
        "exchangeTime": 1776500002.0,
        "LTP": 120.5,
        "volume": 250,
        "OI": 9000,
        "bestBidPrice": 120.45,
        "bestAskPrice": 120.55,
        "bestBidQuantity": 20,
        "bestAskQuantity": 22,
        "depth": {
            "buy": [
                {"price": 120.45, "quantity": 20},
                {"price": 120.40, "quantity": 25},
            ],
            "sell": [
                {"price": 120.55, "quantity": 22},
                {"price": 120.60, "quantity": 30},
            ],
        },
    }

    r1 = normalizer.normalize_zerodha_tick(
        raw_payload=fut_raw_1,
        instrument_reference=fut_ref,
        normalization_context=_build_normalization_context(
            session_date=session_date,
            exchange_ts_seconds=1776500000.0,
            event_seq=1,
            snapshot_id="snap-fut-1",
        ),
        anchor_context=anchors,
        session_metadata=session_meta,
        runtime_audit=runtime,
    )

    r2 = normalizer.normalize_zerodha_tick(
        raw_payload=fut_raw_2,
        instrument_reference=fut_ref,
        normalization_context=_build_normalization_context(
            session_date=session_date,
            exchange_ts_seconds=1776500001.0,
            event_seq=2,
            snapshot_id="snap-fut-2",
        ),
        anchor_context=anchors,
        session_metadata=session_meta,
        runtime_audit=runtime,
    )

    r3 = normalizer.normalize_dhan_tick(
        raw_payload=opt_raw,
        instrument_reference=opt_ref,
        normalization_context=_build_normalization_context(
            session_date=session_date,
            exchange_ts_seconds=1776500002.0,
            event_seq=3,
            snapshot_id="snap-opt-1",
        ),
        anchor_context=anchors,
        session_metadata=session_meta,
        runtime_audit=runtime,
    )

    enriched = enricher.enrich_records_sequentially((r1, r2, r3))
    return tuple(enriched)


def run_verification(
    *,
    session_date: str,
    archive_root: str,
    report_name: str,
    keep_existing: bool,
) -> VerificationResult:
    session_date = utils.normalize_session_date(session_date)
    archive_root = _ensure_non_empty_str("archive_root", archive_root)
    report_name = _ensure_non_empty_str("report_name", report_name)

    archive_root_path = Path(archive_root)
    session_root = archive_root_path / session_date

    if session_root.exists() and not keep_existing:
        shutil.rmtree(session_root)

    records = _build_synthetic_records(session_date)
    route_plan = router.route_records(records)

    write_result = archive_writer.write_session_bundle(
        session_date=session_date,
        records=records,
        archive_root_relative=archive_root,
        status="verify_written",
        notes=("research_capture_verify",),
    )

    reader_config = reader.ReaderConfig(
        archive_root_relative=archive_root,
        verify_files_exist=True,
    )

    manifest = reader.read_manifest(session_date, config=reader_config)
    read_bundle = reader.build_session_read_bundle(session_date, config=reader_config)

    health_snapshot = health.build_capture_health_snapshot(
        session_date=session_date,
        manifest=manifest,
        route_plan=route_plan,
        archive_write_result=write_result,
        notes=("verify_health",),
    )

    integrity_report = integrity.build_integrity_report(
        session_date=session_date,
        records=records,
        route_plan=route_plan,
        manifest=manifest,
        archive_write_result=write_result,
        reader_bundle=read_bundle,
        notes=("verify_integrity",),
    )

    verify_ok = (
        health_snapshot.status.value != "ERROR"
        and integrity_report.status.value == "PASS"
    )

    report_payload = {
        "generated_at": utils.utc_now_iso(),
        "session_date": session_date,
        "archive_root": archive_root_path.as_posix(),
        "session_root": session_root.as_posix(),
        "verify_ok": verify_ok,
        "route_counts": dict(route_plan.counts),
        "dataset_row_counts": dict(read_bundle.dataset_row_counts),
        "write_result": write_result.to_dict(),
        "health": health.health_snapshot_to_dict(health_snapshot),
        "integrity": integrity.integrity_report_to_dict(integrity_report),
    }

    report_path = session_root / report_name
    utils.atomic_write_json(report_path, report_payload)

    return VerificationResult(
        session_date=session_date,
        archive_root=archive_root_path.as_posix(),
        session_root=session_root.as_posix(),
        report_path=report_path.as_posix(),
        verify_ok=verify_ok,
        health_status=health_snapshot.status.value,
        integrity_status=integrity_report.status.value,
        route_counts=dict(route_plan.counts),
        dataset_row_counts=dict(read_bundle.dataset_row_counts),
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    result = run_verification(
        session_date=args.session_date,
        archive_root=args.archive_root,
        report_name=args.report_name,
        keep_existing=args.keep_existing,
    )

    print("verify_ok", result.verify_ok)
    print("session_date", result.session_date)
    print("archive_root", result.archive_root)
    print("session_root", result.session_root)
    print("report_path", result.report_path)
    print("health_status", result.health_status)
    print("integrity_status", result.integrity_status)
    print("route_counts", dict(result.route_counts))
    print("dataset_row_counts", dict(result.dataset_row_counts))

    return 0 if result.verify_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
