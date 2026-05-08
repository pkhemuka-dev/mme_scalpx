"""Replay/trade artifact enrichment contract and gap audit for RAW.

RAW-K freezes the fields future replay/trade/candidate artifacts must carry so RAW can
judge PnL, strategy ranking, OI-wall impact, blockers, missed trades, and false entries.

This module is read-only. It does not patch replay, does not mutate research_capture,
does not call brokers, does not write Redis, and does not enable paper/live.
"""

from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .writer import write_json_file, write_text_file


ENRICHMENT_SCHEMA_VERSION = "RAW-K.1"

ARTIFACT_ENRICHMENT_CONTRACT = "artifact_enrichment_contract.json"
ARTIFACT_ENRICHMENT_GAP_REPORT = "artifact_enrichment_gap_report.json"
ARTIFACT_REQUIRED_FIELDS_CSV = "artifact_enrichment_required_fields.csv"
ARTIFACT_SOURCE_GAP_MATRIX_CSV = "artifact_enrichment_source_gap_matrix.csv"
ARTIFACT_SUMMARY_MD = "RAW_K_ARTIFACT_ENRICHMENT_SUMMARY.md"
ARTIFACT_MANIFEST = "manifest.json"

ENRICHMENT_VERDICT_CONTRACT_FROZEN = "ENRICHMENT_CONTRACT_FROZEN"
ENRICHMENT_VERDICT_GAPS_FOUND = "ENRICHMENT_GAPS_FOUND"
ENRICHMENT_VERDICT_NO_ARTIFACTS_FOUND = "ENRICHMENT_NO_ARTIFACTS_FOUND"

REQUIRED_FIELD_GROUPS = {
    "identity": (
        "run_id",
        "source_run_id",
        "artifact_kind",
        "row_kind",
        "event_id",
        "event_ts",
    ),
    "strategy_context": (
        "family",
        "strategy_id",
        "side",
        "regime",
        "provider_mode",
    ),
    "candidate_truth": (
        "candidate_id",
        "candidate_state",
        "candidate_vs_executed",
        "decision_action",
        "blocker",
        "blocker_chain",
    ),
    "trade_truth": (
        "trade_id",
        "closed_trade_truth",
        "entry_ts",
        "exit_ts",
        "entry_price",
        "exit_price",
        "qty",
        "gross_pnl",
        "net_pnl_after_costs",
        "costs",
        "exit_reason",
    ),
    "outcome_labels": (
        "false_entry",
        "missed_trade",
        "good_blocker",
        "target_hit_after_block",
        "stop_hit_after_block",
        "hypothetical_pnl_after_block",
    ),
    "oi_wall_context": (
        "oi_wall_state",
        "oi_wall_distance_points",
        "oi_wall_strength",
        "strike_score",
        "selected_strike",
        "selected_strike_source",
    ),
    "audit_lineage": (
        "source_artifact",
        "source_row_index",
        "schema_version",
        "created_by",
        "remarks",
    ),
}

REQUIRED_FIELDS = tuple(
    field for group in REQUIRED_FIELD_GROUPS.values() for field in group
)

ARTIFACT_KIND_TRADE_LOG = "trade_log"
ARTIFACT_KIND_CANDIDATE_AUDIT = "candidate_audit"
ARTIFACT_KIND_DECISION_AUDIT = "decision_audit"
ARTIFACT_KIND_REPLAY_SUMMARY = "replay_summary"

ARTIFACT_KINDS = (
    ARTIFACT_KIND_TRADE_LOG,
    ARTIFACT_KIND_CANDIDATE_AUDIT,
    ARTIFACT_KIND_DECISION_AUDIT,
    ARTIFACT_KIND_REPLAY_SUMMARY,
)

SUPPORTED_SUFFIXES = (".csv", ".json", ".jsonl", ".ndjson")

CANDIDATE_FILE_TOKENS = (
    "trade",
    "trades",
    "ledger",
    "candidate",
    "audit",
    "decision",
    "decisions",
    "pnl",
    "summary",
    "replay",
    "comparison",
)

ALIASES = {
    "net_pnl_after_costs": ("net_pnl", "realized_net_pnl", "pnl_net", "closed_net_pnl"),
    "gross_pnl": ("pnl", "realized_pnl", "trade_pnl", "closed_pnl", "points_pnl"),
    "family": ("strategy_family", "family_id", "doctrine"),
    "side": ("branch_side", "option_side", "direction"),
    "provider_mode": ("runtime_mode", "dhan_mode", "mode"),
    "blocker": ("primary_blocker", "block_reason", "reject_reason", "veto_reason", "reason"),
    "candidate_vs_executed": ("row_kind", "executed", "entered", "filled"),
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_enrichment_contract() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for group, fields in REQUIRED_FIELD_GROUPS.items():
        for field in fields:
            rows.append({
                "field": field,
                "group": group,
                "required": True,
                "aliases": list(ALIASES.get(field, ())),
            })

    return {
        "schema_version": ENRICHMENT_SCHEMA_VERSION,
        "generated_utc": utc_now_iso(),
        "contract_name": "RAW replay/trade artifact enrichment contract",
        "artifact_kinds": list(ARTIFACT_KINDS),
        "required_field_groups": {
            group: list(fields)
            for group, fields in REQUIRED_FIELD_GROUPS.items()
        },
        "required_fields": list(REQUIRED_FIELDS),
        "field_rows": rows,
        "non_live": True,
        "non_mutating": True,
        "purpose": "Freeze fields needed for RAW PnL, ranking, OI-wall, blocker, missed-trade, and false-entry evidence.",
        "laws": [
            "Do not infer family labels after the fact if replay can emit them.",
            "Do not mix candidate rows and executed trades without candidate_vs_executed.",
            "Do not treat OI wall as trigger truth; preserve it as slow-context/strike-quality evidence.",
            "Do not promote paper/live until enriched artifacts produce positive and labeled evidence.",
        ],
    }


def _normalize_keys(row: dict[str, Any]) -> set[str]:
    return {str(k).strip() for k in row.keys() if str(k).strip()}


def _present_fields(keys: set[str]) -> set[str]:
    lower_keys = {k.lower(): k for k in keys}
    present: set[str] = set()

    for field in REQUIRED_FIELDS:
        if field.lower() in lower_keys:
            present.add(field)
            continue
        for alias in ALIASES.get(field, ()):
            if alias.lower() in lower_keys:
                present.add(field)
                break
    return present


def _read_csv_keys(path: Path, max_rows: int) -> tuple[set[str], int]:
    keys: set[str] = set()
    rows = 0
    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames:
            keys.update(str(x) for x in reader.fieldnames if x)
        for row in reader:
            rows += 1
            keys.update(_normalize_keys(row))
            if rows >= max_rows:
                break
    return keys, rows


def _dict_rows_from_json_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        for key in (
            "trades",
            "trade_log",
            "rows",
            "records",
            "fills",
            "orders",
            "data",
            "candidate_audit",
            "decisions",
            "events",
            "summary",
        ):
            value = payload.get(key)
            if isinstance(value, list):
                return [x for x in value if isinstance(x, dict)]
        return [payload]
    return []


def _read_json_keys(path: Path, max_rows: int) -> tuple[set[str], int]:
    keys: set[str] = set()
    if path.stat().st_size > 50 * 1024 * 1024:
        return keys, 0
    payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    rows = _dict_rows_from_json_payload(payload)
    for idx, row in enumerate(rows, start=1):
        keys.update(_normalize_keys(row))
        if idx >= max_rows:
            break
    return keys, min(len(rows), max_rows)


def _read_jsonl_keys(path: Path, max_rows: int) -> tuple[set[str], int]:
    keys: set[str] = set()
    rows = 0
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if rows >= max_rows:
                break
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(row, dict):
                continue
            keys.update(_normalize_keys(row))
            rows += 1
    return keys, rows


def find_candidate_artifacts(project_root: str | Path, max_files: int = 500) -> list[Path]:
    root = Path(project_root).resolve()
    scan_roots = [
        root / "run" / "replay",
        root / "run" / "research_capture",
        root / "run" / "proofs",
        root / "reports",
        root / "data",
    ]
    candidates: list[Path] = []
    skip = {".git", ".venv", "__pycache__", ".pytest_cache", "node_modules"}

    for scan_root in scan_roots:
        if not scan_root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(scan_root):
            dirnames[:] = [d for d in dirnames if d not in skip]
            for filename in filenames:
                path = Path(dirpath) / filename
                low = filename.lower()
                if path.suffix.lower() not in SUPPORTED_SUFFIXES:
                    continue
                if not any(token in low for token in CANDIDATE_FILE_TOKENS):
                    continue
                candidates.append(path)
                if len(candidates) >= max_files:
                    return sorted(candidates)
    return sorted(candidates)


def infer_artifact_kind(path: Path) -> str:
    low = path.name.lower()
    if "candidate" in low or "audit" in low:
        return ARTIFACT_KIND_CANDIDATE_AUDIT
    if "decision" in low:
        return ARTIFACT_KIND_DECISION_AUDIT
    if "summary" in low or "metrics" in low:
        return ARTIFACT_KIND_REPLAY_SUMMARY
    if "trade" in low or "ledger" in low or "pnl" in low:
        return ARTIFACT_KIND_TRADE_LOG
    return "unknown"


def audit_artifact(path: Path, root: Path, max_rows: int = 2000) -> dict[str, Any]:
    relative_path = str(path.relative_to(root))
    suffix = path.suffix.lower()
    artifact_kind = infer_artifact_kind(path)

    try:
        if suffix == ".csv":
            keys, sampled_rows = _read_csv_keys(path, max_rows)
        elif suffix == ".json":
            keys, sampled_rows = _read_json_keys(path, max_rows)
        elif suffix in (".jsonl", ".ndjson"):
            keys, sampled_rows = _read_jsonl_keys(path, max_rows)
        else:
            keys, sampled_rows = set(), 0
        status = "SCANNED"
        error = None
    except Exception as exc:
        keys, sampled_rows = set(), 0
        status = "SCAN_ERROR"
        error = str(exc)

    present = _present_fields(keys)
    missing = [field for field in REQUIRED_FIELDS if field not in present]
    coverage = round(len(present) / max(len(REQUIRED_FIELDS), 1), 6)

    return {
        "path": relative_path,
        "artifact_kind": artifact_kind,
        "suffix": suffix,
        "bytes": path.stat().st_size,
        "status": status,
        "error": error,
        "sampled_rows": sampled_rows,
        "detected_columns": sorted(keys),
        "present_required_fields": sorted(present),
        "missing_required_fields": missing,
        "required_field_coverage": coverage,
        "family_label_present": "family" in present,
        "strategy_id_present": "strategy_id" in present,
        "side_present": "side" in present,
        "closed_trade_truth_present": "closed_trade_truth" in present,
        "candidate_vs_executed_present": "candidate_vs_executed" in present,
        "outcome_labels_present": any(
            field in present
            for field in ("false_entry", "missed_trade", "good_blocker")
        ),
        "oi_wall_state_present": "oi_wall_state" in present,
    }


def build_gap_report(
    *,
    project_root: str | Path,
    run_id: str,
    source_label: str = "current_project",
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    artifacts = [audit_artifact(path, root) for path in find_candidate_artifacts(root)]

    artifact_count = len(artifacts)
    if artifact_count <= 0:
        enrichment_verdict = ENRICHMENT_VERDICT_NO_ARTIFACTS_FOUND
    else:
        all_full = all(a["required_field_coverage"] >= 1.0 for a in artifacts if a["status"] == "SCANNED")
        enrichment_verdict = ENRICHMENT_VERDICT_CONTRACT_FROZEN if all_full else ENRICHMENT_VERDICT_GAPS_FOUND

    missing_counter: dict[str, int] = {field: 0 for field in REQUIRED_FIELDS}
    for artifact in artifacts:
        for field in artifact.get("missing_required_fields", []):
            missing_counter[field] += 1

    field_gap_rows = []
    for field in REQUIRED_FIELDS:
        group = next(
            group for group, fields in REQUIRED_FIELD_GROUPS.items()
            if field in fields
        )
        field_gap_rows.append({
            "field": field,
            "group": group,
            "missing_in_artifact_count": missing_counter[field],
            "artifact_count": artifact_count,
            "coverage_count": artifact_count - missing_counter[field],
            "aliases": list(ALIASES.get(field, ())),
        })

    summary = {
        "artifact_count": artifact_count,
        "scanned_count": sum(1 for a in artifacts if a["status"] == "SCANNED"),
        "scan_error_count": sum(1 for a in artifacts if a["status"] == "SCAN_ERROR"),
        "avg_required_field_coverage": round(
            sum(a["required_field_coverage"] for a in artifacts) / max(artifact_count, 1),
            6,
        ),
        "family_label_artifact_count": sum(1 for a in artifacts if a["family_label_present"]),
        "strategy_id_artifact_count": sum(1 for a in artifacts if a["strategy_id_present"]),
        "side_artifact_count": sum(1 for a in artifacts if a["side_present"]),
        "closed_trade_truth_artifact_count": sum(1 for a in artifacts if a["closed_trade_truth_present"]),
        "candidate_vs_executed_artifact_count": sum(1 for a in artifacts if a["candidate_vs_executed_present"]),
        "outcome_labels_artifact_count": sum(1 for a in artifacts if a["outcome_labels_present"]),
        "oi_wall_state_artifact_count": sum(1 for a in artifacts if a["oi_wall_state_present"]),
    }

    blockers = []
    if summary["family_label_artifact_count"] < artifact_count:
        blockers.append("Family labels are missing from one or more artifacts.")
    if summary["closed_trade_truth_artifact_count"] < artifact_count:
        blockers.append("Closed-trade truth is missing from one or more artifacts.")
    if summary["candidate_vs_executed_artifact_count"] < artifact_count:
        blockers.append("Candidate-vs-executed distinction is missing from one or more artifacts.")
    if summary["outcome_labels_artifact_count"] < artifact_count:
        blockers.append("Outcome labels for false/missed/good-blocker evidence are missing from one or more artifacts.")
    if summary["oi_wall_state_artifact_count"] < artifact_count:
        blockers.append("OI-wall state is missing from one or more artifacts.")

    return {
        "schema_version": ENRICHMENT_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_utc": utc_now_iso(),
        "source_label": source_label,
        "project_root": str(root),
        "non_live": True,
        "non_mutating": True,
        "replay_module_mutation_included": False,
        "research_capture_mutation_included": False,
        "broker_io_included": False,
        "redis_live_write_included": False,
        "order_sending_included": False,
        "paper_live_enablement_included": False,
        "enrichment_verdict": enrichment_verdict,
        "summary": summary,
        "blockers": blockers,
        "required_field_gap_rows": field_gap_rows,
        "artifact_gap_rows": artifacts,
        "recommendations": [
            "Patch replay exporters/writers only after this contract is accepted.",
            "Emit family, strategy_id, side, regime, provider_mode, and source_run_id on every candidate/trade row.",
            "Separate candidate rows from executed trades through candidate_vs_executed and closed_trade_truth.",
            "Add explicit blocker outcome labels instead of inferring them later.",
            "Add OI-wall state at candidate/trade time while keeping OI wall as slow-context evidence.",
            "Rerun RAW-D through RAW-J after enriched replay artifacts are produced.",
        ],
    }


def build_manifest_for_report(*, run_id: str, report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": ENRICHMENT_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_utc": utc_now_iso(),
        "non_live": True,
        "non_mutating": True,
        "artifacts": [
            {"path": ARTIFACT_MANIFEST, "artifact_type": "raw_manifest"},
            {"path": ARTIFACT_ENRICHMENT_CONTRACT, "artifact_type": "artifact_enrichment_contract"},
            {"path": ARTIFACT_ENRICHMENT_GAP_REPORT, "artifact_type": "artifact_enrichment_gap_report"},
            {"path": ARTIFACT_REQUIRED_FIELDS_CSV, "artifact_type": "required_fields"},
            {"path": ARTIFACT_SOURCE_GAP_MATRIX_CSV, "artifact_type": "source_gap_matrix"},
            {"path": ARTIFACT_SUMMARY_MD, "artifact_type": "artifact_enrichment_summary"},
        ],
        "enrichment_verdict": report["enrichment_verdict"],
    }


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in fieldnames})
    os.replace(tmp, path)


def render_summary_markdown(report: dict[str, Any]) -> str:
    s = report["summary"]
    lines = [
        "# RAW-K Replay/Trade Artifact Enrichment Summary",
        "",
        f"Run ID: {report['run_id']}",
        f"Generated UTC: {report['generated_utc']}",
        "",
        "## Verdict",
        "",
        f"- enrichment_verdict: {report['enrichment_verdict']}",
        f"- artifact_count: {s['artifact_count']}",
        f"- avg_required_field_coverage: {s['avg_required_field_coverage']}",
        f"- family_label_artifact_count: {s['family_label_artifact_count']}",
        f"- closed_trade_truth_artifact_count: {s['closed_trade_truth_artifact_count']}",
        f"- candidate_vs_executed_artifact_count: {s['candidate_vs_executed_artifact_count']}",
        f"- outcome_labels_artifact_count: {s['outcome_labels_artifact_count']}",
        f"- oi_wall_state_artifact_count: {s['oi_wall_state_artifact_count']}",
        "",
        "## Blockers",
        "",
    ]
    if report["blockers"]:
        lines.extend(f"- {item}" for item in report["blockers"])
    else:
        lines.append("- none")
    lines.extend(["", "## Recommendations", ""])
    lines.extend(f"- {item}" for item in report["recommendations"])
    lines.extend([
        "",
        "## Boundary confirmation",
        "",
        f"- non_live: {report['non_live']}",
        f"- non_mutating: {report['non_mutating']}",
        f"- replay_module_mutation_included: {report['replay_module_mutation_included']}",
        f"- research_capture_mutation_included: {report['research_capture_mutation_included']}",
        f"- broker_io_included: {report['broker_io_included']}",
        f"- redis_live_write_included: {report['redis_live_write_included']}",
        f"- order_sending_included: {report['order_sending_included']}",
        f"- paper_live_enablement_included: {report['paper_live_enablement_included']}",
        "",
    ])
    return "\n".join(lines)


def write_enrichment_audit_bundle(
    *,
    project_root: str | Path,
    output_dir: str | Path,
    run_id: str,
    source_label: str = "current_project",
) -> dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    contract = build_enrichment_contract()
    report = build_gap_report(
        project_root=project_root,
        run_id=run_id,
        source_label=source_label,
    )
    manifest = build_manifest_for_report(run_id=run_id, report=report)
    summary = render_summary_markdown(report)

    write_json_file(out / ARTIFACT_ENRICHMENT_CONTRACT, contract)
    write_json_file(out / ARTIFACT_ENRICHMENT_GAP_REPORT, report)
    write_json_file(out / ARTIFACT_MANIFEST, manifest)
    write_text_file(out / ARTIFACT_SUMMARY_MD, summary)

    _write_csv(
        out / ARTIFACT_REQUIRED_FIELDS_CSV,
        contract["field_rows"],
        ["field", "group", "required", "aliases"],
    )

    _write_csv(
        out / ARTIFACT_SOURCE_GAP_MATRIX_CSV,
        report["artifact_gap_rows"],
        [
            "path",
            "artifact_kind",
            "suffix",
            "bytes",
            "status",
            "sampled_rows",
            "required_field_coverage",
            "family_label_present",
            "strategy_id_present",
            "side_present",
            "closed_trade_truth_present",
            "candidate_vs_executed_present",
            "outcome_labels_present",
            "oi_wall_state_present",
        ],
    )

    return {
        "output_dir": str(out),
        "manifest": str(out / ARTIFACT_MANIFEST),
        "artifact_enrichment_contract": str(out / ARTIFACT_ENRICHMENT_CONTRACT),
        "artifact_enrichment_gap_report": str(out / ARTIFACT_ENRICHMENT_GAP_REPORT),
        "required_fields_csv": str(out / ARTIFACT_REQUIRED_FIELDS_CSV),
        "source_gap_matrix_csv": str(out / ARTIFACT_SOURCE_GAP_MATRIX_CSV),
        "summary_markdown": str(out / ARTIFACT_SUMMARY_MD),
        "enrichment_verdict": report["enrichment_verdict"],
        "artifact_count": report["summary"]["artifact_count"],
        "avg_required_field_coverage": report["summary"]["avg_required_field_coverage"],
        "blocker_count": len(report["blockers"]),
    }
