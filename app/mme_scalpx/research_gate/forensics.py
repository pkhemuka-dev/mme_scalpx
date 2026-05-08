"""Blocker, missed-trade, and false-entry desk for RAW / Research Gate.

RAW-H performs conservative forensics on existing replay/research/proof artifacts.

It does not infer missing outcomes, does not call brokers, does not write Redis,
does not send orders, does not mutate strategy/risk/execution, and does not approve paper/live.
"""

from __future__ import annotations

import csv
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .contracts import (
    ARTIFACT_MANIFEST,
    VERDICT_INCONCLUSIVE_DATA_INSUFFICIENT,
    VERDICT_REJECT_NEGATIVE_EXPECTANCY,
    VERDICT_RESEARCH_ONLY_FINDING,
)
from .writer import write_json_file, write_text_file


FORENSICS_SCHEMA_VERSION = "RAW-H.1"

ARTIFACT_BLOCKER_CHAIN = "blocker_chain_report.json"
ARTIFACT_MISSED_TRADE = "missed_trade_report.json"
ARTIFACT_FALSE_ENTRY = "false_entry_report.json"
ARTIFACT_FORENSICS_SUMMARY = "RAW_H_FORENSICS_SUMMARY.md"
BLOCKER_MATRIX_CSV = "blocker_matrix.csv"
SOURCE_BREAKDOWN_CSV = "forensics_source_breakdown.csv"

FORENSICS_VERDICT_INSUFFICIENT_EVIDENCE = "FORENSICS_INSUFFICIENT_EVIDENCE"
FORENSICS_VERDICT_CONTEXT_FOUND_NO_OUTCOME_LABELS = "FORENSICS_CONTEXT_FOUND_NO_OUTCOME_LABELS"
FORENSICS_VERDICT_RESEARCH_FINDINGS = "FORENSICS_RESEARCH_FINDINGS"
FORENSICS_VERDICT_NEGATIVE_DIAGNOSIS = "FORENSICS_NEGATIVE_DIAGNOSIS"

UNKNOWN = "UNKNOWN"

SUPPORTED_SUFFIXES = (".csv", ".json", ".jsonl", ".ndjson")
CANDIDATE_FILE_TOKENS = (
    "candidate",
    "audit",
    "blocker",
    "blocked",
    "decision",
    "decisions",
    "trade",
    "trades",
    "ledger",
    "pnl",
    "entry",
    "exit",
)

FAMILY_FIELDS = (
    "family",
    "strategy_family",
    "family_id",
    "strategy",
    "strategy_id",
    "doctrine",
)

SIDE_FIELDS = (
    "side",
    "branch_side",
    "option_side",
    "direction",
)

STAGE_FIELDS = (
    "stage",
    "stage_reached",
    "candidate_stage",
    "pipeline_stage",
    "failed_stage",
    "last_stage",
)

ACTION_FIELDS = (
    "action",
    "decision",
    "decision_action",
    "final_action",
    "strategy_action",
    "order_action",
    "result",
    "status",
)

BLOCKER_FIELDS = (
    "blocker",
    "primary_blocker",
    "blocker_primary",
    "block_reason",
    "blocked_reason",
    "reject_reason",
    "veto_reason",
    "reason",
    "blockers",
    "blocker_chain",
)

ENTRY_FIELDS = (
    "entry_sent",
    "order_sent",
    "entry_order_sent",
    "entered",
    "filled",
    "fill_qty",
    "filled_qty",
    "position_open",
)

EXIT_REASON_FIELDS = (
    "exit_reason",
    "close_reason",
    "final_exit_reason",
)

NET_PNL_FIELDS = (
    "net_pnl",
    "net_pnl_after_costs",
    "realized_net_pnl",
    "pnl_net",
    "realized_pnl_net",
    "closed_net_pnl",
)

GROSS_PNL_FIELDS = (
    "gross_pnl",
    "pnl",
    "realized_pnl",
    "trade_pnl",
    "pnl_points",
    "points_pnl",
    "closed_pnl",
)

HYPOTHETICAL_PNL_FIELDS = (
    "would_pnl",
    "hypothetical_pnl",
    "missed_pnl",
    "future_pnl",
    "would_have_pnl",
    "would_net_pnl",
    "mfe_after_block",
)

TARGET_FIELDS = (
    "target_hit",
    "would_hit_target",
    "future_target_hit",
    "hit_target",
)

STOP_FIELDS = (
    "stop_hit",
    "would_hit_stop",
    "future_stop_hit",
    "hit_stop",
    "hard_stop_hit",
)

FALSE_ENTRY_LABEL_FIELDS = (
    "false_entry",
    "bad_entry",
    "should_have_blocked",
)

MISSED_TRADE_LABEL_FIELDS = (
    "missed_trade",
    "should_have_entered",
    "valid_trade_missed",
)

GOOD_BLOCKER_LABEL_FIELDS = (
    "good_blocker",
    "saved_loss",
    "blocker_saved_loss",
)


@dataclass(frozen=True)
class ForensicsRecord:
    source_path: str
    row_index: int
    family: str
    side: str
    stage: str
    action: str
    blocker: str
    is_blocked: bool
    is_entered: bool
    net_pnl: float | None
    hypothetical_pnl: float | None
    target_hit: bool | None
    stop_hit: bool | None
    classification: str
    evidence_strength: str
    remarks: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _boolish(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "hit", "pass", "filled", "entered", "sent"}:
        return True
    if text in {"0", "false", "no", "n", "miss", "fail", "none", "not_sent"}:
        return False
    return None


def _first_present(row: dict[str, Any], fields: Iterable[str]) -> Any:
    lower_map = {str(k).lower(): k for k in row.keys()}
    for field in fields:
        key = lower_map.get(field.lower())
        if key is not None:
            value = row.get(key)
            if value not in (None, ""):
                return value
    return None


def _first_text(row: dict[str, Any], fields: Iterable[str], default: str = UNKNOWN) -> str:
    value = _first_present(row, fields)
    if value in (None, ""):
        return default
    return str(value)


def _has_any_key_token(row: dict[str, Any], tokens: Iterable[str]) -> bool:
    for key, value in row.items():
        low = str(key).lower()
        if any(token in low for token in tokens):
            if value not in (None, ""):
                return True
    return False


def _row_is_forensics_relevant(row: dict[str, Any]) -> bool:
    tokens = (
        "block",
        "candidate",
        "decision",
        "action",
        "entry",
        "exit",
        "pnl",
        "target",
        "stop",
        "missed",
        "false",
        "veto",
        "reject",
    )
    return _has_any_key_token(row, tokens)


def _net_pnl(row: dict[str, Any]) -> float | None:
    net = _safe_float(_first_present(row, NET_PNL_FIELDS))
    if net is not None:
        return net
    gross = _safe_float(_first_present(row, GROSS_PNL_FIELDS))
    return gross


def _hypothetical_pnl(row: dict[str, Any]) -> float | None:
    return _safe_float(_first_present(row, HYPOTHETICAL_PNL_FIELDS))


def _any_bool(row: dict[str, Any], fields: Iterable[str]) -> bool | None:
    for field in fields:
        value = _first_present(row, (field,))
        result = _boolish(value)
        if result is not None:
            return result
    return None


def _is_entered(row: dict[str, Any], action: str) -> bool:
    action_low = action.lower()
    if any(token in action_low for token in ("enter", "entry", "buy", "sell", "filled", "position_open")):
        return True
    for field in ENTRY_FIELDS:
        value = _first_present(row, (field,))
        b = _boolish(value)
        if b is True:
            return True
        num = _safe_float(value)
        if num is not None and num > 0:
            return True
    return False


def _is_blocked(row: dict[str, Any], action: str, blocker: str) -> bool:
    if blocker not in ("", UNKNOWN, "NONE", "NO_BLOCKER"):
        return True
    action_low = action.lower()
    return any(token in action_low for token in ("hold", "block", "reject", "veto", "skip", "no_trade", "not_enter"))


def classify_forensics_record(row: dict[str, Any], *, source_path: str, row_index: int) -> ForensicsRecord | None:
    if not _row_is_forensics_relevant(row):
        return None

    family = _first_text(row, FAMILY_FIELDS)
    side = _first_text(row, SIDE_FIELDS)
    stage = _first_text(row, STAGE_FIELDS)
    action = _first_text(row, ACTION_FIELDS)
    blocker = _first_text(row, BLOCKER_FIELDS)
    exit_reason = _first_text(row, EXIT_REASON_FIELDS, "")

    net = _net_pnl(row)
    hypo = _hypothetical_pnl(row)
    target_hit = _any_bool(row, TARGET_FIELDS)
    stop_hit = _any_bool(row, STOP_FIELDS)

    false_entry_label = _any_bool(row, FALSE_ENTRY_LABEL_FIELDS)
    missed_trade_label = _any_bool(row, MISSED_TRADE_LABEL_FIELDS)
    good_blocker_label = _any_bool(row, GOOD_BLOCKER_LABEL_FIELDS)

    entered = _is_entered(row, action)
    blocked = _is_blocked(row, action, blocker)

    classification = "UNCLASSIFIED_CONTEXT"
    evidence_strength = "LOW"
    remarks: list[str] = []

    if false_entry_label is True:
        classification = "FALSE_ENTRY_EXPLICIT_LABEL"
        evidence_strength = "HIGH"
        remarks.append("Explicit false-entry label.")
    elif entered and net is not None and net < 0:
        classification = "FALSE_ENTRY_LOSS_AFTER_ENTRY"
        evidence_strength = "MEDIUM"
        remarks.append("Entered trade with negative explicit PnL.")
    elif entered and (stop_hit is True or "stop" in exit_reason.lower() or "proof_failure" in exit_reason.lower()):
        classification = "FALSE_ENTRY_STOP_OR_PROOF_FAILURE"
        evidence_strength = "MEDIUM"
        remarks.append("Entered trade with stop/proof-failure evidence.")
    elif missed_trade_label is True:
        classification = "MISSED_TRADE_EXPLICIT_LABEL"
        evidence_strength = "HIGH"
        remarks.append("Explicit missed-trade label.")
    elif blocked and target_hit is True:
        classification = "MISSED_TRADE_BLOCKED_TARGET_HIT"
        evidence_strength = "MEDIUM"
        remarks.append("Blocked candidate with explicit target-hit evidence.")
    elif blocked and hypo is not None and hypo > 0:
        classification = "MISSED_TRADE_BLOCKED_POSITIVE_HYPOTHETICAL_PNL"
        evidence_strength = "MEDIUM"
        remarks.append("Blocked candidate with positive hypothetical/future PnL.")
    elif good_blocker_label is True:
        classification = "GOOD_BLOCKER_EXPLICIT_LABEL"
        evidence_strength = "HIGH"
        remarks.append("Explicit good-blocker label.")
    elif blocked and stop_hit is True:
        classification = "GOOD_BLOCKER_BLOCKED_STOP_HIT"
        evidence_strength = "MEDIUM"
        remarks.append("Blocked candidate with stop-hit evidence.")
    elif blocked and hypo is not None and hypo < 0:
        classification = "GOOD_BLOCKER_BLOCKED_NEGATIVE_HYPOTHETICAL_PNL"
        evidence_strength = "MEDIUM"
        remarks.append("Blocked candidate with negative hypothetical/future PnL.")
    elif blocked:
        classification = "BLOCKED_NO_OUTCOME_LABEL"
        evidence_strength = "LOW"
        remarks.append("Blocked candidate but no explicit outcome label.")
    elif entered:
        classification = "ENTERED_NO_FORENSIC_LABEL"
        evidence_strength = "LOW"
        remarks.append("Entered/filled record but no explicit forensic label.")

    return ForensicsRecord(
        source_path=source_path,
        row_index=row_index,
        family=family,
        side=side,
        stage=stage,
        action=action,
        blocker=blocker,
        is_blocked=blocked,
        is_entered=entered,
        net_pnl=net,
        hypothetical_pnl=hypo,
        target_hit=target_hit,
        stop_hit=stop_hit,
        classification=classification,
        evidence_strength=evidence_strength,
        remarks=" ".join(remarks),
    )


def _read_csv_records(path: Path, relative_path: str, max_rows: int) -> list[ForensicsRecord]:
    records: list[ForensicsRecord] = []
    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            if idx > max_rows:
                break
            rec = classify_forensics_record(row, source_path=relative_path, row_index=idx)
            if rec is not None:
                records.append(rec)
    return records


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
            "blockers",
            "events",
        ):
            value = payload.get(key)
            if isinstance(value, list):
                return [x for x in value if isinstance(x, dict)]
        return [payload]
    return []


def _read_json_records(path: Path, relative_path: str, max_rows: int) -> list[ForensicsRecord]:
    records: list[ForensicsRecord] = []
    if path.stat().st_size > 50 * 1024 * 1024:
        return records
    payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    rows = _dict_rows_from_json_payload(payload)
    for idx, row in enumerate(rows, start=1):
        if idx > max_rows:
            break
        rec = classify_forensics_record(row, source_path=relative_path, row_index=idx)
        if rec is not None:
            records.append(rec)
    return records


def _read_jsonl_records(path: Path, relative_path: str, max_rows: int) -> list[ForensicsRecord]:
    records: list[ForensicsRecord] = []
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for idx, line in enumerate(f, start=1):
            if idx > max_rows:
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
            rec = classify_forensics_record(row, source_path=relative_path, row_index=idx)
            if rec is not None:
                records.append(rec)
    return records


def find_candidate_forensics_files(project_root: str | Path, max_files: int = 500) -> list[Path]:
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


def read_forensics_records(project_root: str | Path, max_rows_per_file: int = 20000) -> tuple[list[ForensicsRecord], list[dict[str, Any]]]:
    root = Path(project_root).resolve()
    records: list[ForensicsRecord] = []
    scanned_files: list[dict[str, Any]] = []

    for path in find_candidate_forensics_files(root):
        relative_path = str(path.relative_to(root))
        before_count = len(records)
        try:
            suffix = path.suffix.lower()
            if suffix == ".csv":
                records.extend(_read_csv_records(path, relative_path, max_rows_per_file))
            elif suffix == ".json":
                records.extend(_read_json_records(path, relative_path, max_rows_per_file))
            elif suffix in (".jsonl", ".ndjson"):
                records.extend(_read_jsonl_records(path, relative_path, max_rows_per_file))
        except Exception as exc:
            scanned_files.append({
                "path": relative_path,
                "suffix": path.suffix.lower(),
                "bytes": path.stat().st_size,
                "records_found": len(records) - before_count,
                "status": "SCAN_ERROR",
                "error": str(exc),
            })
            continue

        scanned_files.append({
            "path": relative_path,
            "suffix": path.suffix.lower(),
            "bytes": path.stat().st_size,
            "records_found": len(records) - before_count,
            "status": "SCANNED",
        })

    return records, scanned_files


def _bucket_template() -> dict[str, Any]:
    return {
        "record_count": 0,
        "blocked_count": 0,
        "entered_count": 0,
        "false_entry_count": 0,
        "missed_trade_count": 0,
        "good_blocker_count": 0,
        "unknown_outcome_count": 0,
        "explicit_high_confidence_count": 0,
        "net_pnl_sum": 0.0,
        "hypothetical_pnl_sum": 0.0,
        "pnl_linked_count": 0,
        "hypothetical_linked_count": 0,
    }


def _apply_record(bucket: dict[str, Any], record: ForensicsRecord) -> None:
    bucket["record_count"] += 1
    if record.is_blocked:
        bucket["blocked_count"] += 1
    if record.is_entered:
        bucket["entered_count"] += 1
    if record.classification.startswith("FALSE_ENTRY"):
        bucket["false_entry_count"] += 1
    if record.classification.startswith("MISSED_TRADE"):
        bucket["missed_trade_count"] += 1
    if record.classification.startswith("GOOD_BLOCKER"):
        bucket["good_blocker_count"] += 1
    if record.evidence_strength == "HIGH":
        bucket["explicit_high_confidence_count"] += 1
    if record.classification in {"BLOCKED_NO_OUTCOME_LABEL", "ENTERED_NO_FORENSIC_LABEL", "UNCLASSIFIED_CONTEXT"}:
        bucket["unknown_outcome_count"] += 1
    if record.net_pnl is not None:
        bucket["pnl_linked_count"] += 1
        bucket["net_pnl_sum"] += float(record.net_pnl)
    if record.hypothetical_pnl is not None:
        bucket["hypothetical_linked_count"] += 1
        bucket["hypothetical_pnl_sum"] += float(record.hypothetical_pnl)


def _finalize_bucket(bucket: dict[str, Any]) -> dict[str, Any]:
    count = bucket["record_count"]
    if count > 0:
        bucket["false_entry_rate"] = round(bucket["false_entry_count"] / count, 6)
        bucket["missed_trade_rate"] = round(bucket["missed_trade_count"] / count, 6)
        bucket["good_blocker_rate"] = round(bucket["good_blocker_count"] / count, 6)
        bucket["unknown_outcome_rate"] = round(bucket["unknown_outcome_count"] / count, 6)
    else:
        bucket["false_entry_rate"] = 0.0
        bucket["missed_trade_rate"] = 0.0
        bucket["good_blocker_rate"] = 0.0
        bucket["unknown_outcome_rate"] = 0.0
    bucket["net_pnl_sum"] = round(float(bucket["net_pnl_sum"]), 6)
    bucket["hypothetical_pnl_sum"] = round(float(bucket["hypothetical_pnl_sum"]), 6)
    return bucket


def _aggregate(records: list[ForensicsRecord], key_name: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for rec in records:
        key = getattr(rec, key_name)
        bucket = result.setdefault(key, _bucket_template())
        _apply_record(bucket, rec)
    return {key: _finalize_bucket(bucket) for key, bucket in sorted(result.items())}


def build_blocker_matrix(records: list[ForensicsRecord]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for rec in records:
        key = f"{rec.blocker}|{rec.stage}|{rec.family}|{rec.side}"
        bucket = result.setdefault(
            key,
            {
                "blocker": rec.blocker,
                "stage": rec.stage,
                "family": rec.family,
                "side": rec.side,
                **_bucket_template(),
            },
        )
        _apply_record(bucket, rec)
    return {key: _finalize_bucket(bucket) for key, bucket in sorted(result.items())}


def build_forensics_reports(
    *,
    project_root: str | Path,
    run_id: str,
    source_label: str = "current_project",
) -> dict[str, Any]:
    records, scanned_files = read_forensics_records(project_root)

    total = _bucket_template()
    for rec in records:
        _apply_record(total, rec)
    total = _finalize_bucket(total)

    false_entries = [r for r in records if r.classification.startswith("FALSE_ENTRY")]
    missed_trades = [r for r in records if r.classification.startswith("MISSED_TRADE")]
    good_blockers = [r for r in records if r.classification.startswith("GOOD_BLOCKER")]

    warnings: list[str] = []
    if total["record_count"] <= 0:
        forensics_verdict = FORENSICS_VERDICT_INSUFFICIENT_EVIDENCE
        research_verdict = VERDICT_INCONCLUSIVE_DATA_INSUFFICIENT
        warnings.append("No forensics-relevant blocker/candidate/decision records found.")
    elif (
        total["false_entry_count"] == 0
        and total["missed_trade_count"] == 0
        and total["good_blocker_count"] == 0
    ):
        forensics_verdict = FORENSICS_VERDICT_CONTEXT_FOUND_NO_OUTCOME_LABELS
        research_verdict = VERDICT_RESEARCH_ONLY_FINDING
        warnings.append("Forensics context found but no explicit false-entry/missed-trade/good-blocker outcome labels.")
    elif total["false_entry_count"] > 0 and total["net_pnl_sum"] < 0:
        forensics_verdict = FORENSICS_VERDICT_NEGATIVE_DIAGNOSIS
        research_verdict = VERDICT_REJECT_NEGATIVE_EXPECTANCY
        warnings.append("False-entry/loss evidence exists; diagnostic only, no promotion conclusion.")
    else:
        forensics_verdict = FORENSICS_VERDICT_RESEARCH_FINDINGS
        research_verdict = VERDICT_RESEARCH_ONLY_FINDING

    if total["unknown_outcome_rate"] > 0.50:
        warnings.append("High unknown-outcome ratio; enrich replay/trade artifacts with explicit outcome labels.")

    if any("candidate" in item["path"].lower() for item in scanned_files if item.get("records_found", 0) > 0):
        warnings.append("Candidate/audit artifacts contributed records; verify closed-trade linkage before promotion.")

    base = {
        "schema_version": FORENSICS_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_utc": utc_now_iso(),
        "source_label": source_label,
        "project_root": str(Path(project_root).resolve()),
        "non_live": True,
        "non_mutating": True,
        "pnl_computation_included": False,
        "strategy_ranking_included": False,
        "oi_wall_computation_included": False,
        "forensics_computation_included": True,
        "broker_io_included": False,
        "redis_live_write_included": False,
        "order_sending_included": False,
        "production_mutation_included": False,
        "paper_live_enablement_included": False,
        "forensics_verdict": forensics_verdict,
        "research_verdict": research_verdict,
        "summary": total,
        "by_classification": _aggregate(records, "classification"),
        "by_blocker": _aggregate(records, "blocker"),
        "by_stage": _aggregate(records, "stage"),
        "by_family": _aggregate(records, "family"),
        "by_side": _aggregate(records, "side"),
        "by_source": _aggregate(records, "source_path"),
        "blocker_matrix": build_blocker_matrix(records),
        "scanned_files": scanned_files,
        "warnings": warnings,
        "remarks": [
            "RAW-H is forensic evidence only.",
            "RAW-H does not infer missed trades without explicit labels or hypothetical outcome fields.",
            "RAW-H does not mutate strategy/risk/execution.",
            "RAW-H does not approve paper/live.",
        ],
    }

    blocker_report = {
        **base,
        "report_type": "blocker_chain_report",
        "good_blocker_records_sample": [r.to_dict() for r in good_blockers[:80]],
        "blocked_unknown_records_sample": [
            r.to_dict()
            for r in records
            if r.classification == "BLOCKED_NO_OUTCOME_LABEL"
        ][:80],
    }

    missed_trade_report = {
        **base,
        "report_type": "missed_trade_report",
        "missed_trade_records_sample": [r.to_dict() for r in missed_trades[:100]],
    }

    false_entry_report = {
        **base,
        "report_type": "false_entry_report",
        "false_entry_records_sample": [r.to_dict() for r in false_entries[:100]],
    }

    return {
        "blocker_report": blocker_report,
        "missed_trade_report": missed_trade_report,
        "false_entry_report": false_entry_report,
        "all_records_sample": [r.to_dict() for r in records[:120]],
    }


def build_manifest_for_reports(*, run_id: str, reports: dict[str, Any]) -> dict[str, Any]:
    blocker = reports["blocker_report"]
    return {
        "schema_version": FORENSICS_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_utc": utc_now_iso(),
        "non_live": True,
        "non_mutating": True,
        "artifacts": [
            {"path": ARTIFACT_MANIFEST, "artifact_type": "raw_manifest"},
            {"path": ARTIFACT_BLOCKER_CHAIN, "artifact_type": "blocker_chain_report"},
            {"path": ARTIFACT_MISSED_TRADE, "artifact_type": "missed_trade_report"},
            {"path": ARTIFACT_FALSE_ENTRY, "artifact_type": "false_entry_report"},
            {"path": BLOCKER_MATRIX_CSV, "artifact_type": "blocker_matrix"},
            {"path": SOURCE_BREAKDOWN_CSV, "artifact_type": "forensics_source_breakdown"},
            {"path": ARTIFACT_FORENSICS_SUMMARY, "artifact_type": "forensics_summary"},
        ],
        "forensics_verdict": blocker["forensics_verdict"],
        "research_verdict": blocker["research_verdict"],
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


def render_summary_markdown(reports: dict[str, Any]) -> str:
    r = reports["blocker_report"]
    s = r["summary"]
    lines = [
        "# RAW-H Forensics Summary",
        "",
        f"Run ID: {r['run_id']}",
        f"Generated UTC: {r['generated_utc']}",
        "",
        "## Verdict",
        "",
        f"- forensics_verdict: {r['forensics_verdict']}",
        f"- research_verdict: {r['research_verdict']}",
        f"- record_count: {s['record_count']}",
        f"- blocked_count: {s['blocked_count']}",
        f"- entered_count: {s['entered_count']}",
        f"- false_entry_count: {s['false_entry_count']}",
        f"- missed_trade_count: {s['missed_trade_count']}",
        f"- good_blocker_count: {s['good_blocker_count']}",
        f"- unknown_outcome_rate: {s['unknown_outcome_rate']}",
        "",
        "## Warnings",
        "",
    ]
    if r["warnings"]:
        lines.extend(f"- {w}" for w in r["warnings"])
    else:
        lines.append("- none")
    lines.extend([
        "",
        "## Boundary confirmation",
        "",
        f"- non_live: {r['non_live']}",
        f"- non_mutating: {r['non_mutating']}",
        f"- pnl_computation_included: {r['pnl_computation_included']}",
        f"- strategy_ranking_included: {r['strategy_ranking_included']}",
        f"- oi_wall_computation_included: {r['oi_wall_computation_included']}",
        f"- forensics_computation_included: {r['forensics_computation_included']}",
        f"- broker_io_included: {r['broker_io_included']}",
        f"- redis_live_write_included: {r['redis_live_write_included']}",
        f"- order_sending_included: {r['order_sending_included']}",
        f"- production_mutation_included: {r['production_mutation_included']}",
        "",
    ])
    return "\n".join(lines)


def write_forensics_bundle(
    *,
    project_root: str | Path,
    output_dir: str | Path,
    run_id: str,
    source_label: str = "current_project",
) -> dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    reports = build_forensics_reports(
        project_root=project_root,
        run_id=run_id,
        source_label=source_label,
    )
    manifest = build_manifest_for_reports(run_id=run_id, reports=reports)
    summary = render_summary_markdown(reports)

    write_json_file(out / ARTIFACT_BLOCKER_CHAIN, reports["blocker_report"])
    write_json_file(out / ARTIFACT_MISSED_TRADE, reports["missed_trade_report"])
    write_json_file(out / ARTIFACT_FALSE_ENTRY, reports["false_entry_report"])
    write_json_file(out / ARTIFACT_MANIFEST, manifest)
    write_text_file(out / ARTIFACT_FORENSICS_SUMMARY, summary)

    matrix_rows = list(reports["blocker_report"]["blocker_matrix"].values())
    _write_csv(
        out / BLOCKER_MATRIX_CSV,
        matrix_rows,
        [
            "blocker",
            "stage",
            "family",
            "side",
            "record_count",
            "blocked_count",
            "entered_count",
            "false_entry_count",
            "missed_trade_count",
            "good_blocker_count",
            "unknown_outcome_count",
            "explicit_high_confidence_count",
            "net_pnl_sum",
            "hypothetical_pnl_sum",
            "pnl_linked_count",
            "hypothetical_linked_count",
            "false_entry_rate",
            "missed_trade_rate",
            "good_blocker_rate",
            "unknown_outcome_rate",
        ],
    )

    source_rows = [
        {"source_path": key, **value}
        for key, value in reports["blocker_report"]["by_source"].items()
    ]
    _write_csv(
        out / SOURCE_BREAKDOWN_CSV,
        source_rows,
        [
            "source_path",
            "record_count",
            "blocked_count",
            "entered_count",
            "false_entry_count",
            "missed_trade_count",
            "good_blocker_count",
            "unknown_outcome_count",
            "explicit_high_confidence_count",
            "net_pnl_sum",
            "hypothetical_pnl_sum",
            "pnl_linked_count",
            "hypothetical_linked_count",
            "false_entry_rate",
            "missed_trade_rate",
            "good_blocker_rate",
            "unknown_outcome_rate",
        ],
    )

    blocker = reports["blocker_report"]
    s = blocker["summary"]

    return {
        "output_dir": str(out),
        "manifest": str(out / ARTIFACT_MANIFEST),
        "blocker_chain_report": str(out / ARTIFACT_BLOCKER_CHAIN),
        "missed_trade_report": str(out / ARTIFACT_MISSED_TRADE),
        "false_entry_report": str(out / ARTIFACT_FALSE_ENTRY),
        "blocker_matrix_csv": str(out / BLOCKER_MATRIX_CSV),
        "source_breakdown_csv": str(out / SOURCE_BREAKDOWN_CSV),
        "summary_markdown": str(out / ARTIFACT_FORENSICS_SUMMARY),
        "forensics_verdict": blocker["forensics_verdict"],
        "research_verdict": blocker["research_verdict"],
        "record_count": s["record_count"],
        "false_entry_count": s["false_entry_count"],
        "missed_trade_count": s["missed_trade_count"],
        "good_blocker_count": s["good_blocker_count"],
        "unknown_outcome_rate": s["unknown_outcome_rate"],
        "warning_count": len(blocker["warnings"]),
    }
