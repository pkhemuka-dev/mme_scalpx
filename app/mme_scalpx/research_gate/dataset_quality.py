"""Dataset quality desk for RAW / Research Gate.

RAW-D is read-only analysis of artifact availability and readiness.

This module does not compute PnL, does not evaluate strategies, does not call brokers,
does not write Redis, and does not mutate live runtime.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .contracts import (
    ARTIFACT_DATASET_QUALITY,
    ARTIFACT_MANIFEST,
    EVIDENCE_TRACK_LIVE,
    EVIDENCE_TRACK_PARITY,
    EVIDENCE_TRACK_REPLAY,
    VERDICT_INCONCLUSIVE_DATA_INSUFFICIENT,
    VERDICT_RESEARCH_ONLY_FINDING,
)
from .writer import write_json_file, write_text_file


DATASET_QUALITY_SCHEMA_VERSION = "RAW-D.1"

DATASET_VERDICT_PASS = "DATASET_PASS"
DATASET_VERDICT_PASS_WITH_WARNINGS = "DATASET_PASS_WITH_WARNINGS"
DATASET_VERDICT_PARTIAL = "DATASET_PARTIAL"
DATASET_VERDICT_INSUFFICIENT = "DATASET_INSUFFICIENT"

LIVE_SURFACE_GROUP = "live_evidence"
REPLAY_SURFACE_GROUP = "replay_evidence"
RESEARCH_CAPTURE_SURFACE_GROUP = "research_capture"
PROOF_SURFACE_GROUP = "proofs"
RAW_SURFACE_GROUP = "raw_research_gate"


@dataclass(frozen=True)
class DatasetSurfaceQuality:
    name: str
    path: str
    group: str
    required: bool
    exists: bool
    kind: str
    file_count: int
    total_bytes: int
    newest_mtime_utc: str | None
    oldest_mtime_utc: str | None
    status: str
    remarks: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _mtime_iso(ts: float | None) -> str | None:
    if ts is None:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def _scan_path(path: Path, max_files: int = 5000) -> tuple[int, int, str | None, str | None]:
    if not path.exists():
        return 0, 0, None, None

    if path.is_file():
        st = path.stat()
        mt = st.st_mtime
        return 1, st.st_size, _mtime_iso(mt), _mtime_iso(mt)

    file_count = 0
    total_bytes = 0
    newest: float | None = None
    oldest: float | None = None

    skip = {".git", ".venv", "__pycache__", ".pytest_cache", "node_modules"}

    for dirpath, dirnames, filenames in os.walk(path):
        dirnames[:] = [d for d in dirnames if d not in skip]
        for filename in filenames:
            p = Path(dirpath) / filename
            try:
                st = p.stat()
            except OSError:
                continue
            file_count += 1
            total_bytes += st.st_size
            newest = st.st_mtime if newest is None else max(newest, st.st_mtime)
            oldest = st.st_mtime if oldest is None else min(oldest, st.st_mtime)
            if file_count >= max_files:
                return file_count, total_bytes, _mtime_iso(newest), _mtime_iso(oldest)

    return file_count, total_bytes, _mtime_iso(newest), _mtime_iso(oldest)


def evaluate_surface(
    *,
    project_root: str | Path,
    name: str,
    relative_path: str,
    group: str,
    required: bool,
    remarks: str,
) -> DatasetSurfaceQuality:
    root = Path(project_root).resolve()
    path = root / relative_path
    exists = path.exists()
    kind = "dir" if path.is_dir() else "file" if path.is_file() else "missing"
    file_count, total_bytes, newest, oldest = _scan_path(path)

    if exists:
        status = "PASS"
    elif required:
        status = "FAIL_MISSING_REQUIRED"
    else:
        status = "WARN_MISSING_OPTIONAL"

    return DatasetSurfaceQuality(
        name=name,
        path=relative_path,
        group=group,
        required=required,
        exists=exists,
        kind=kind,
        file_count=file_count,
        total_bytes=total_bytes,
        newest_mtime_utc=newest,
        oldest_mtime_utc=oldest,
        status=status,
        remarks=remarks,
    )


def default_surface_plan() -> tuple[dict[str, Any], ...]:
    return (
        {
            "name": "research_capture_code",
            "relative_path": "app/mme_scalpx/research_capture",
            "group": RESEARCH_CAPTURE_SURFACE_GROUP,
            "required": True,
            "remarks": "Existing capture/archive producer. RAW must reuse, not duplicate.",
        },
        {
            "name": "replay_code",
            "relative_path": "app/mme_scalpx/replay",
            "group": REPLAY_SURFACE_GROUP,
            "required": True,
            "remarks": "Replay/backtest producer. RAW consumes replay outputs.",
        },
        {
            "name": "raw_research_gate_code",
            "relative_path": "app/mme_scalpx/research_gate",
            "group": RAW_SURFACE_GROUP,
            "required": True,
            "remarks": "RAW package owner created in RAW-C.",
        },
        {
            "name": "raw_research_gate_config",
            "relative_path": "etc/research_gate",
            "group": RAW_SURFACE_GROUP,
            "required": True,
            "remarks": "RAW policy config owner created in RAW-C.",
        },
        {
            "name": "proof_artifacts",
            "relative_path": "run/proofs",
            "group": PROOF_SURFACE_GROUP,
            "required": True,
            "remarks": "Proof evidence root.",
        },
        {
            "name": "research_capture_runtime_artifacts",
            "relative_path": "run/research_capture",
            "group": RESEARCH_CAPTURE_SURFACE_GROUP,
            "required": False,
            "remarks": "Captured historical/live research artifacts if present.",
        },
        {
            "name": "replay_runtime_artifacts",
            "relative_path": "run/replay",
            "group": REPLAY_SURFACE_GROUP,
            "required": False,
            "remarks": "Replay run artifacts if present.",
        },
        {
            "name": "live_capture_artifacts",
            "relative_path": "run/live_capture",
            "group": LIVE_SURFACE_GROUP,
            "required": False,
            "remarks": "Live capture logs/artifacts if present. Optional during closed market.",
        },
        {
            "name": "research_capture_config",
            "relative_path": "etc/research_capture",
            "group": RESEARCH_CAPTURE_SURFACE_GROUP,
            "required": False,
            "remarks": "Capture policies/configs.",
        },
        {
            "name": "strategy_family_config",
            "relative_path": "etc/strategy_family",
            "group": REPLAY_SURFACE_GROUP,
            "required": False,
            "remarks": "Frozen strategy-family doctrine/configs used by replay/research.",
        },
    )


def build_dataset_quality_report(
    *,
    project_root: str | Path,
    run_id: str,
    source_label: str = "current_project",
) -> dict[str, Any]:
    surfaces = [
        evaluate_surface(project_root=project_root, **spec)
        for spec in default_surface_plan()
    ]

    required = [s for s in surfaces if s.required]
    optional = [s for s in surfaces if not s.required]
    required_pass_count = sum(1 for s in required if s.exists)
    optional_present_count = sum(1 for s in optional if s.exists)

    required_surface_score = required_pass_count / max(len(required), 1)
    optional_surface_score = optional_present_count / max(len(optional), 1)
    data_quality_score = round((0.75 * required_surface_score) + (0.25 * optional_surface_score), 4)

    missing_required = [s.name for s in required if not s.exists]
    missing_optional = [s.name for s in optional if not s.exists]

    if missing_required:
        dataset_verdict = DATASET_VERDICT_INSUFFICIENT
        research_verdict = VERDICT_INCONCLUSIVE_DATA_INSUFFICIENT
    elif missing_optional:
        dataset_verdict = DATASET_VERDICT_PASS_WITH_WARNINGS
        research_verdict = VERDICT_RESEARCH_ONLY_FINDING
    else:
        dataset_verdict = DATASET_VERDICT_PASS
        research_verdict = VERDICT_RESEARCH_ONLY_FINDING

    live_surfaces = [s.to_dict() for s in surfaces if s.group == LIVE_SURFACE_GROUP]
    replay_surfaces = [s.to_dict() for s in surfaces if s.group == REPLAY_SURFACE_GROUP]
    research_capture_surfaces = [s.to_dict() for s in surfaces if s.group == RESEARCH_CAPTURE_SURFACE_GROUP]
    proof_surfaces = [s.to_dict() for s in surfaces if s.group == PROOF_SURFACE_GROUP]
    raw_surfaces = [s.to_dict() for s in surfaces if s.group == RAW_SURFACE_GROUP]

    report = {
        "schema_version": DATASET_QUALITY_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_utc": utc_now_iso(),
        "source_label": source_label,
        "project_root": str(Path(project_root).resolve()),
        "non_live": True,
        "non_mutating": True,
        "pnl_computation_included": False,
        "strategy_ranking_included": False,
        "oi_wall_computation_included": False,
        "broker_io_included": False,
        "redis_live_write_included": False,
        "order_sending_included": False,
        "evidence_tracks": {
            EVIDENCE_TRACK_LIVE: {
                "role": "runtime safety, data trust, provider context, family surface, no-order evidence",
                "surfaces": live_surfaces,
            },
            EVIDENCE_TRACK_REPLAY: {
                "role": "strategy PnL/backtest/missed-trade/false-entry/blocker/OI-wall/regime evidence in later batches",
                "surfaces": replay_surfaces,
            },
            EVIDENCE_TRACK_PARITY: {
                "role": "future comparison of live capture surfaces vs replay surfaces before promotion",
                "ready_for_future_parity_check": bool(live_surfaces and replay_surfaces),
            },
        },
        "research_capture_surfaces": research_capture_surfaces,
        "proof_surfaces": proof_surfaces,
        "raw_surfaces": raw_surfaces,
        "summary": {
            "required_surface_count": len(required),
            "required_surface_pass_count": required_pass_count,
            "optional_surface_count": len(optional),
            "optional_surface_present_count": optional_present_count,
            "required_surface_score": round(required_surface_score, 4),
            "optional_surface_score": round(optional_surface_score, 4),
            "data_quality_score": data_quality_score,
            "missing_required": missing_required,
            "missing_optional": missing_optional,
            "dataset_verdict": dataset_verdict,
            "research_verdict": research_verdict,
        },
        "all_surfaces": [s.to_dict() for s in surfaces],
        "remarks": [
            "RAW-D is dataset-quality only.",
            "PnL analysis is reserved for RAW-E or later.",
            "Strategy ranking is reserved for RAW-F or later.",
            "OI-wall impact computation is reserved for RAW-G or later.",
            "Missing live_capture artifacts are warnings during closed-market/non-live runs.",
        ],
    }
    return report


def build_manifest_for_report(*, run_id: str, report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": DATASET_QUALITY_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_utc": utc_now_iso(),
        "non_live": True,
        "non_mutating": True,
        "artifacts": [
            {
                "path": ARTIFACT_MANIFEST,
                "artifact_type": "raw_manifest",
            },
            {
                "path": ARTIFACT_DATASET_QUALITY,
                "artifact_type": "dataset_quality_report",
            },
            {
                "path": "RAW_D_DATASET_QUALITY_SUMMARY.md",
                "artifact_type": "dataset_quality_summary",
            },
        ],
        "dataset_verdict": report["summary"]["dataset_verdict"],
        "research_verdict": report["summary"]["research_verdict"],
    }


def render_summary_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# RAW-D Dataset Quality Summary",
        "",
        f"Run ID: {report['run_id']}",
        f"Generated UTC: {report['generated_utc']}",
        "",
        "## Verdict",
        "",
        f"- dataset_verdict: {summary['dataset_verdict']}",
        f"- research_verdict: {summary['research_verdict']}",
        f"- data_quality_score: {summary['data_quality_score']}",
        "",
        "## Boundary confirmation",
        "",
        f"- non_live: {report['non_live']}",
        f"- non_mutating: {report['non_mutating']}",
        f"- pnl_computation_included: {report['pnl_computation_included']}",
        f"- strategy_ranking_included: {report['strategy_ranking_included']}",
        f"- oi_wall_computation_included: {report['oi_wall_computation_included']}",
        f"- broker_io_included: {report['broker_io_included']}",
        f"- redis_live_write_included: {report['redis_live_write_included']}",
        f"- order_sending_included: {report['order_sending_included']}",
        "",
        "## Missing required surfaces",
        "",
    ]
    if summary["missing_required"]:
        lines.extend(f"- {item}" for item in summary["missing_required"])
    else:
        lines.append("- none")
    lines.extend(["", "## Missing optional surfaces", ""])
    if summary["missing_optional"]:
        lines.extend(f"- {item}" for item in summary["missing_optional"])
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def write_dataset_quality_bundle(
    *,
    project_root: str | Path,
    output_dir: str | Path,
    run_id: str,
    source_label: str = "current_project",
) -> dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    report = build_dataset_quality_report(
        project_root=project_root,
        run_id=run_id,
        source_label=source_label,
    )
    manifest = build_manifest_for_report(run_id=run_id, report=report)
    summary = render_summary_markdown(report)

    write_json_file(out / ARTIFACT_DATASET_QUALITY, report)
    write_json_file(out / ARTIFACT_MANIFEST, manifest)
    write_text_file(out / "RAW_D_DATASET_QUALITY_SUMMARY.md", summary)

    return {
        "output_dir": str(out),
        "manifest": str(out / ARTIFACT_MANIFEST),
        "dataset_quality_report": str(out / ARTIFACT_DATASET_QUALITY),
        "summary_markdown": str(out / "RAW_D_DATASET_QUALITY_SUMMARY.md"),
        "dataset_verdict": report["summary"]["dataset_verdict"],
        "research_verdict": report["summary"]["research_verdict"],
        "data_quality_score": report["summary"]["data_quality_score"],
    }
