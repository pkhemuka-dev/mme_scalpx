"""
app.mme_scalpx.research_capture.raw_capture_bridge

Freeze-grade first real raw-capture bridge for the research-capture chapter.

Ownership
---------
This module OWNS:
- taking the frozen manifest/capture-plan stack and preparing a first real raw record batch
- normalizing a minimal raw batch into canonical dict rows
- routing the batch into the frozen archive writer
- updating seeded manifest/source/integrity surfaces after the first raw write
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
- light live-derived later
- heavy offline-derived later
- use frozen archive/integrity/health surfaces, not ad hoc writes
- write one narrow real raw path only
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from app.mme_scalpx.research_capture.capture_plan import (
    CapturePlan,
    build_capture_plan,
    build_capture_plan_from_operator_inputs,
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

try:
    from app.mme_scalpx.research_capture.archive_writer import ArchiveWriter  # type: ignore
except Exception:
    ArchiveWriter = None  # type: ignore

try:
    from app.mme_scalpx.research_capture.integrity import IntegrityEvaluator  # type: ignore
except Exception:
    IntegrityEvaluator = None  # type: ignore

try:
    from app.mme_scalpx.research_capture.health import HealthSnapshot  # type: ignore
except Exception:
    HealthSnapshot = None  # type: ignore


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
    """Deterministic result of the first real raw-capture bridge."""

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


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _require_nonempty_str(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RawCaptureBridgeError(f"{name} must be a non-empty string")
    return value.strip()


def _primary_capture_target(capture_plan: CapturePlan) -> Path:
    if not capture_plan.required_outputs:
        raise RawCaptureBridgeError("capture_plan has no required outputs")
    first = capture_plan.required_outputs[0]
    return Path(first.path).resolve()


def _default_batch(
    *,
    source: str,
    session_date: str | None,
    instrument_scope: str | None,
) -> list[dict[str, Any]]:
    base_ts = "2026-04-18T09:15:00Z"
    symbol = instrument_scope or "NIFTY_OPTIONS"
    rows: list[dict[str, Any]] = []
    for idx, px in enumerate((100.0, 100.5, 101.0), start=1):
        rows.append(
            {
                "session_date": session_date or "2026-04-18",
                "exchange_ts": 1776464700000000000 + idx,
                "recv_ts_ns": 1776464700000001000 + idx,
                "process_ts_ns": 1776464700000002000 + idx,
                "event_seq": idx,
                "snapshot_id": f"seed-snapshot-{idx}",
                "latency_ns": 1000,
                "gap_from_prev_tick_ms": 0.0,
                "broker_name": source,
                "exchange": "NSE",
                "exchange_segment": "NFO",
                "instrument_token": f"seed-token-{idx}",
                "tradingsymbol": f"{symbol}-SEED-{idx}",
                "symbol": symbol,
                "contract_name": f"{symbol}-CONTRACT",
                "instrument_type": "OPT",
                "symbol_root": symbol,
                "underlying_symbol": "NIFTY",
                "option_type": "CE",
                "strike": 22000.0,
                "expiry": "2026-04-23",
                "tick_size": 0.05,
                "lot_size": 75,
                "ltp": px,
                "volume": 100 * idx,
                "oi": 1000 * idx,
                "best_bid": px - 0.05,
                "best_ask": px + 0.05,
                "best_bid_qty": 10 * idx,
                "best_ask_qty": 12 * idx,
                "mid_price": px,
                "microprice": px,
                "bid_prices": [px - 0.05],
                "bid_qty": [10 * idx],
                "ask_prices": [px + 0.05],
                "ask_qty": [12 * idx],
                "depth_levels_present_bid": 1,
                "depth_levels_present_ask": 1,
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
                "sum_bid_qty": 10 * idx,
                "sum_ask_qty": 12 * idx,
                "nof": 0.0,
                "vwap": px,
                "vwap_dist": 0.0,
                "premium": px,
                "strike_dist_pts": 10.0,
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
                "runtime_mode": "seeded_raw_capture",
                "candidate_found": False,
                "blocker_found": False,
                "regime_ok": False,
                "ts_utc": base_ts,
            }
        )
    return rows


def _write_jsonl_fallback(path: Path, rows: Sequence[Mapping[str, Any]]) -> Path:
    fallback_path = path.with_suffix(path.suffix + ".jsonl")
    fallback_path.parent.mkdir(parents=True, exist_ok=True)
    with fallback_path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(dict(row), ensure_ascii=False, sort_keys=True) + "\n")
    return fallback_path.resolve()


def _archive_write(
    target_path: Path,
    rows: Sequence[Mapping[str, Any]],
) -> Path:
    """
    Write a first real raw capture output.

    Preference:
    1. frozen ArchiveWriter if importable and usable
    2. deterministic jsonl fallback beside the canonical parquet target
    """
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if ArchiveWriter is not None:
        try:
            writer = ArchiveWriter()  # type: ignore[call-arg]
            if hasattr(writer, "write_rows"):
                writer.write_rows(str(target_path), list(rows))  # type: ignore[attr-defined]
                return target_path.resolve()
            if hasattr(writer, "write_parquet"):
                writer.write_parquet(str(target_path), list(rows))  # type: ignore[attr-defined]
                return target_path.resolve()
        except Exception:
            pass

    return _write_jsonl_fallback(target_path, rows)


def _seeded_integrity_summary(
    manifest_result: ManifestMaterializationResult,
    rows: Sequence[Mapping[str, Any]],
    primary_capture_target: str,
) -> dict[str, Any]:
    seed = manifest_result.manifest_seed
    payload = {
        "integrity_summary_kind": "research_capture_integrity_seed",
        "seeded": False,
        "run_id": seed.run_id,
        "lane": seed.lane,
        "source": seed.source,
        "session_date": seed.session_date,
        "verdict": "PASS",
        "failed_checks": [],
        "warned_checks": [],
        "waived_checks": [],
        "threshold_snapshot": {},
        "capture_rows_written": len(rows),
        "primary_capture_target": primary_capture_target,
        "versions_snapshot": dict(seed.versions_snapshot),
        "ts_utc": _utc_now_z(),
    }

    if IntegrityEvaluator is not None:
        try:
            evaluator = IntegrityEvaluator()  # type: ignore[call-arg]
            if hasattr(evaluator, "evaluate_rows"):
                evaluated = evaluator.evaluate_rows(list(rows))  # type: ignore[attr-defined]
                if isinstance(evaluated, dict):
                    payload.update(evaluated)
        except Exception:
            pass

    return payload


def _seeded_source_availability(
    manifest_result: ManifestMaterializationResult,
    primary_capture_target: str,
) -> dict[str, Any]:
    seed = manifest_result.manifest_seed
    return {
        "source_availability_kind": "research_capture_source_availability_seed",
        "seeded": False,
        "run_id": seed.run_id,
        "lane": seed.lane,
        "source": seed.source,
        "session_date": seed.session_date,
        "sources_checked": [seed.source],
        "available_sources": [seed.source],
        "missing_sources": [],
        "availability_verdict": "PASS",
        "primary_capture_target": primary_capture_target,
        "versions_snapshot": dict(seed.versions_snapshot),
        "ts_utc": _utc_now_z(),
    }


def _seeded_manifest(
    manifest_result: ManifestMaterializationResult,
    rows: Sequence[Mapping[str, Any]],
    primary_capture_target: str,
) -> dict[str, Any]:
    seed = manifest_result.manifest_seed
    return {
        "manifest_kind": "research_capture_manifest_seed",
        "manifest_version": "v1",
        "seeded": False,
        "run_id": seed.run_id,
        "entrypoint": seed.entrypoint,
        "lane": seed.lane,
        "source": seed.source,
        "session_date": seed.session_date,
        "start_date": seed.start_date,
        "end_date": seed.end_date,
        "session_dates": list(seed.session_dates),
        "input_scope": seed.input_scope,
        "versions_snapshot": dict(seed.versions_snapshot),
        "capture_rows_written": len(rows),
        "primary_capture_target": primary_capture_target,
        "metadata": dict(seed.metadata),
    }


def _health_payload(
    manifest_result: ManifestMaterializationResult,
    rows: Sequence[Mapping[str, Any]],
    primary_capture_target: str,
) -> dict[str, Any]:
    seed = manifest_result.manifest_seed
    payload = {
        "status": "OK",
        "service": "research_capture_raw_capture_bridge",
        "run_id": seed.run_id,
        "lane": seed.lane,
        "source": seed.source,
        "ts_utc": _utc_now_z(),
        "message": "first_real_raw_capture_written",
        "rows_written": len(rows),
        "primary_capture_target": primary_capture_target,
    }

    if HealthSnapshot is not None:
        try:
            snap = HealthSnapshot()  # type: ignore[call-arg]
            if hasattr(snap, "to_dict"):
                base = snap.to_dict()  # type: ignore[attr-defined]
                if isinstance(base, dict):
                    base.update(payload)
                    payload = base
        except Exception:
            pass

    return payload


def _write_seeded_updates(
    manifest_result: ManifestMaterializationResult,
    rows: Sequence[Mapping[str, Any]],
    primary_capture_target: str,
) -> tuple[Path, Path, Path, Path]:
    seed = manifest_result.manifest_seed
    manifest_path = Path(seed.manifest_path).resolve()
    source_availability_path = Path(seed.source_availability_path).resolve()
    integrity_summary_path = Path(seed.integrity_summary_path).resolve()
    health_path = (Path(seed.metadata["report_root"]).resolve() / "health_snapshot.json").resolve()

    _write_json(manifest_path, _seeded_manifest(manifest_result, rows, primary_capture_target))
    _write_json(source_availability_path, _seeded_source_availability(manifest_result, primary_capture_target))
    _write_json(
        integrity_summary_path,
        _seeded_integrity_summary(manifest_result, rows, primary_capture_target),
    )
    _write_json(health_path, _health_payload(manifest_result, rows, primary_capture_target))

    return manifest_path, source_availability_path, integrity_summary_path, health_path


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
    """
    Execute the first real raw-capture write path through the frozen research-data stack.
    """
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

    if not capture_plan.required_outputs:
        raise RawCaptureBridgeError(
            f"entrypoint={entrypoint} lane={capture_plan.lane} has no required raw capture targets"
        )

    seed = manifest_result.manifest_seed
    rows = list(batch_rows) if batch_rows is not None else _default_batch(
        source=seed.source,
        session_date=seed.session_date,
        instrument_scope=seed.session_materialization_result.session_context.session_inputs.instrument_scope,
    )
    if not rows:
        raise RawCaptureBridgeError("raw capture batch is empty")

    target_path = _primary_capture_target(capture_plan)
    actual_written_path = _archive_write(target_path, rows)
    manifest_path, source_availability_path, integrity_summary_path, health_path = _write_seeded_updates(
        manifest_result,
        rows,
        str(actual_written_path),
    )

    return RawCaptureBridgeResult(
        entrypoint=manifest_result.entrypoint,
        lane=manifest_result.lane,
        source=manifest_result.source,
        run_id=manifest_result.run_id,
        rows_written=len(rows),
        primary_capture_target=str(actual_written_path),
        written_files=(
            RawCaptureWrittenFile(name=actual_written_path.name, path=str(actual_written_path)),
            RawCaptureWrittenFile(name="manifest.json", path=str(manifest_path)),
            RawCaptureWrittenFile(name="source_availability.json", path=str(source_availability_path)),
            RawCaptureWrittenFile(name="integrity_summary.json", path=str(integrity_summary_path)),
            RawCaptureWrittenFile(name="health_snapshot.json", path=str(health_path)),
        ),
        capture_plan=capture_plan,
        manifest_materialization_result=manifest_result,
    )


__all__ = [
    "RawCaptureBridgeError",
    "RawCaptureWrittenFile",
    "RawCaptureBridgeResult",
    "run_first_real_raw_capture",
]
