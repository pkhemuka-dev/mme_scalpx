from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.research_capture.raw_capture_bridge import run_first_real_raw_capture
from app.mme_scalpx.research_capture.reader import (
    build_session_read_bundle,
    read_capture_report_dir,
)

TS = datetime.now().strftime("%Y%m%d_%H%M%S")
RUN_ID = f"research_capture_manifest_report_surface_proof_{TS}"
SESSION_DATE = "2026-04-18"

REQUIRED_REPORT_FILES = (
    "manifest.json",
    "source_availability.json",
    "integrity_summary.json",
    "integrity_report.json",
    "health_snapshot.json",
    "effective_inputs.json",
    "effective_registry_snapshot.json",
)

REQUIRED_DATASET_COUNTS = {
    "ticks_fut": 1,
    "ticks_opt": 2,
    "runtime_audit": 3,
}

OPTIONAL_ZERO_ALLOWED = {
    "signals_audit": 0,
}


def _load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    result = run_first_real_raw_capture(
        "run",
        run_id=RUN_ID,
        session_date=SESSION_DATE,
        notes="canonical_manifest_report_surface_proof",
        project_root=PROJECT_ROOT,
    )

    report_dir = Path(
        result.manifest_materialization_result.manifest_seed.metadata["report_root"]
    ).resolve()

    for file_name in REQUIRED_REPORT_FILES:
        file_path = report_dir / file_name
        if not file_path.exists():
            raise FileNotFoundError(f"required report file missing: {file_path}")

    report_bundle = read_capture_report_dir(report_dir)
    session_bundle = build_session_read_bundle(SESSION_DATE)

    report_manifest_payload = _load_json(report_dir / "manifest.json")
    report_source_availability_payload = _load_json(report_dir / "source_availability.json")
    report_integrity_summary_payload = _load_json(report_dir / "integrity_summary.json")
    integrity_report_payload = _load_json(report_dir / "integrity_report.json")
    health_snapshot_payload = _load_json(report_dir / "health_snapshot.json")
    effective_inputs_payload = _load_json(report_dir / "effective_inputs.json")
    effective_registry_payload = _load_json(report_dir / "effective_registry_snapshot.json")

    session_root = Path(session_bundle.session_root).resolve()
    session_manifest_payload = _load_json(session_root / "manifest.json")
    session_source_availability_payload = _load_json(session_root / "source_availability.json")
    session_integrity_summary_payload = _load_json(session_root / "integrity_summary.json")

    report_counts = dict(report_bundle["dataset_row_counts"])
    session_counts = dict(session_bundle.dataset_row_counts)
    integrity_counts = dict(report_bundle["integrity_summary_dataset_row_counts"])
    report_manifest_session_date = report_manifest_payload.get("session_date")
    session_manifest_session_date = session_manifest_payload.get("session_date")
    effective_inputs_session_date = effective_inputs_payload.get("session_date")
    session_manifest_status = session_manifest_payload.get("status")

    if report_counts != session_counts:
        raise AssertionError(
            f"report_counts != session_counts :: {report_counts} != {session_counts}"
        )

    if report_counts != integrity_counts:
        raise AssertionError(
            f"report_counts != integrity_counts :: {report_counts} != {integrity_counts}"
        )

    for dataset_name, expected in REQUIRED_DATASET_COUNTS.items():
        actual = int(report_counts.get(dataset_name, 0))
        if actual != expected:
            raise AssertionError(
                f"unexpected dataset count for {dataset_name}: actual={actual} expected={expected}"
            )

    for dataset_name, expected in OPTIONAL_ZERO_ALLOWED.items():
        actual = int(report_counts.get(dataset_name, 0))
        if actual != expected:
            raise AssertionError(
                f"unexpected optional dataset count for {dataset_name}: actual={actual} expected={expected}"
            )

    if report_manifest_session_date is not None and report_manifest_session_date != SESSION_DATE:
        raise AssertionError(
            f"report manifest session_date mismatch: {report_manifest_session_date!r} != {SESSION_DATE!r}"
        )

    if session_manifest_session_date != SESSION_DATE:
        raise AssertionError(
            f"session manifest session_date mismatch: {session_manifest_session_date!r} != {SESSION_DATE!r}"
        )

    if effective_inputs_session_date != SESSION_DATE:
        raise AssertionError(
            f"effective_inputs session_date mismatch: {effective_inputs_session_date!r} != {SESSION_DATE!r}"
        )

    if session_manifest_status != "session_written":
        raise AssertionError(
            f"session manifest status mismatch: {session_manifest_status!r} != 'session_written'"
        )

    if "source_availability" not in session_manifest_payload:
        raise AssertionError("session manifest missing source_availability")
    if "integrity_summary" not in session_manifest_payload:
        raise AssertionError("session manifest missing integrity_summary")
    if "archive_outputs" not in session_manifest_payload:
        raise AssertionError("session manifest missing archive_outputs")

    if not isinstance(report_source_availability_payload, dict) or not report_source_availability_payload:
        raise AssertionError("report source_availability payload unexpectedly empty")
    if not isinstance(session_source_availability_payload.get("sources"), dict):
        raise AssertionError("session source_availability.sources must be dict")
    if not isinstance(report_integrity_summary_payload, dict) or not report_integrity_summary_payload:
        raise AssertionError("report integrity_summary payload unexpectedly empty")
    if int(session_integrity_summary_payload.get("total_records", 0)) < 3:
        raise AssertionError("session integrity_summary.total_records unexpectedly low")
    if not isinstance(integrity_report_payload, dict) or not integrity_report_payload:
        raise AssertionError("integrity_report payload unexpectedly empty")
    if not isinstance(health_snapshot_payload, dict) or not health_snapshot_payload:
        raise AssertionError("health_snapshot payload unexpectedly empty")
    if not isinstance(effective_registry_payload, dict) or not effective_registry_payload:
        raise AssertionError("effective_registry_snapshot unexpectedly empty")

    print("===== CANONICAL_MANIFEST_REPORT_SURFACE_PROOF =====")
    print(f"run_id={result.run_id}")
    print(f"entrypoint={result.entrypoint}")
    print(f"session_root={session_bundle.session_root}")
    print(f"report_dir={report_dir}")
    print(f"report_counts={report_counts}")
    print(f"session_counts={session_counts}")
    print(f"integrity_counts={integrity_counts}")
    print(f"session_manifest_status={session_manifest_status}")
    print(f"report_manifest_session_date={report_manifest_session_date}")
    print(f"session_manifest_session_date={session_manifest_session_date}")
    print(f"effective_inputs_session_date={effective_inputs_session_date}")
    print(f"report_source_availability_payload_type={type(report_source_availability_payload).__name__}")
    print(f"report_integrity_summary_payload_type={type(report_integrity_summary_payload).__name__}")
    print(f"integrity_report_payload_type={type(integrity_report_payload).__name__}")
    print(f"health_snapshot_payload_type={type(health_snapshot_payload).__name__}")
    print("required_report_files_ok=True")
    print("status=GREEN")


if __name__ == "__main__":
    main()
