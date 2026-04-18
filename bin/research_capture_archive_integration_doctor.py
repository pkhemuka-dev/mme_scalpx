#!/usr/bin/env python3
"""
bin/research_capture_archive_integration_doctor.py

Freeze-grade archive/integrity integration doctor for the research_capture chapter.

Purpose
-------
- prove whether the first real raw-capture lane is using the canonical archive path
  or the jsonl fallback path
- surface whether archive_writer / integrity / health modules are importable
- leave a single auditable report for the next continuation step
"""

from __future__ import annotations

import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.research_capture.raw_capture_bridge import (  # noqa: E402
    run_first_real_raw_capture,
)

DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "run" / "_smokes" / "research_capture" / "archive_integration_doctor"


def _utc_now_z() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _module_probe(module_name: str, expected_symbols: list[str]) -> dict[str, Any]:
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:
        return {
            "module": module_name,
            "import_ok": False,
            "error": repr(exc),
            "file": None,
            "symbols_present": {},
        }

    return {
        "module": module_name,
        "import_ok": True,
        "error": None,
        "file": getattr(module, "__file__", None),
        "symbols_present": {
            symbol: hasattr(module, symbol) for symbol in expected_symbols
        },
    }


def _archive_mode(primary_capture_target: str) -> str:
    if primary_capture_target.endswith(".jsonl"):
        return "jsonl_fallback"
    if primary_capture_target.endswith(".parquet"):
        return "canonical_target_path"
    return "unknown"


def main() -> int:
    output_dir = DEFAULT_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    module_checks = {
        "archive_writer": _module_probe(
            "app.mme_scalpx.research_capture.archive_writer",
            ["ArchiveWriter"],
        ),
        "integrity": _module_probe(
            "app.mme_scalpx.research_capture.integrity",
            ["IntegrityEvaluator"],
        ),
        "health": _module_probe(
            "app.mme_scalpx.research_capture.health",
            ["HealthSnapshot"],
        ),
        "manifest": _module_probe(
            "app.mme_scalpx.research_capture.manifest",
            [],
        ),
    }

    run_result = run_first_real_raw_capture(
        "run",
        run_id="rcap_run_archive_doctor_20260418_demo",
        session_date="2026-04-18",
        instrument_scope="NIFTY_OPTIONS",
        project_root=PROJECT_ROOT,
    )
    backfill_result = run_first_real_raw_capture(
        "backfill",
        run_id="rcap_backfill_archive_doctor_20260418_demo",
        start_date="2026-04-01",
        end_date="2026-04-03",
        instrument_scope="NIFTY_OPTIONS",
        project_root=PROJECT_ROOT,
    )

    report = {
        "doctor_name": "MME Research Capture Archive Integration Doctor",
        "doctor_version": "v1",
        "doctor_ok": True,
        "ts_utc": _utc_now_z(),
        "module_checks": module_checks,
        "run_probe": {
            "entrypoint": run_result.entrypoint,
            "lane": run_result.lane,
            "source": run_result.source,
            "run_id": run_result.run_id,
            "rows_written": run_result.rows_written,
            "primary_capture_target": run_result.primary_capture_target,
            "archive_write_mode": _archive_mode(run_result.primary_capture_target),
            "written_files": [item.to_dict() for item in run_result.written_files],
            "required_capture_targets": [item.to_dict() for item in run_result.capture_plan.required_outputs],
            "optional_capture_targets": [item.to_dict() for item in run_result.capture_plan.optional_outputs],
        },
        "backfill_probe": {
            "entrypoint": backfill_result.entrypoint,
            "lane": backfill_result.lane,
            "source": backfill_result.source,
            "run_id": backfill_result.run_id,
            "rows_written": backfill_result.rows_written,
            "primary_capture_target": backfill_result.primary_capture_target,
            "archive_write_mode": _archive_mode(backfill_result.primary_capture_target),
            "written_files": [item.to_dict() for item in backfill_result.written_files],
            "required_capture_targets": [item.to_dict() for item in backfill_result.capture_plan.required_outputs],
            "optional_capture_targets": [item.to_dict() for item in backfill_result.capture_plan.optional_outputs],
        },
        "artifact_inventory": {
            "archive_integration_doctor_report": "archive_integration_doctor_report.json",
        },
    }

    _write_json(output_dir / "archive_integration_doctor_report.json", report)

    print("archive_integration_doctor_ok", True)
    print("run_archive_mode", report["run_probe"]["archive_write_mode"])
    print("backfill_archive_mode", report["backfill_probe"]["archive_write_mode"])
    print("doctor_report", str(output_dir / "archive_integration_doctor_report.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
