"""OI-wall impact desk for RAW / Research Gate.

RAW-G scans existing artifacts for OI/OI-wall/strike-selection context and optional PnL linkage.

It does not convert OI wall into trigger truth, does not call brokers, does not write Redis,
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
    ARTIFACT_OI_WALL_IMPACT,
    VERDICT_INCONCLUSIVE_DATA_INSUFFICIENT,
    VERDICT_REJECT_NEGATIVE_EXPECTANCY,
    VERDICT_RESEARCH_ONLY_FINDING,
)
from .writer import write_json_file, write_text_file


OI_SCHEMA_VERSION = "RAW-G.1"

OI_VERDICT_INSUFFICIENT_OI_EVIDENCE = "OI_IMPACT_INSUFFICIENT_OI_EVIDENCE"
OI_VERDICT_CONTEXT_FOUND_NO_PNL_LINKAGE = "OI_CONTEXT_FOUND_NO_PNL_LINKAGE"
OI_VERDICT_RESEARCH_POSITIVE = "OI_IMPACT_RESEARCH_POSITIVE"
OI_VERDICT_RESEARCH_NEGATIVE = "OI_IMPACT_RESEARCH_NEGATIVE"
OI_VERDICT_RESEARCH_MIXED = "OI_IMPACT_RESEARCH_MIXED"

OI_CONTEXT_MATRIX_CSV = "oi_wall_context_matrix.csv"
OI_SOURCE_BREAKDOWN_CSV = "oi_wall_source_breakdown.csv"
SUMMARY_MD = "RAW_G_OI_WALL_SUMMARY.md"

UNKNOWN = "UNKNOWN"

SUPPORTED_SUFFIXES = (".csv", ".json", ".jsonl", ".ndjson")
CANDIDATE_FILE_TOKENS = (
    "oi",
    "wall",
    "strike",
    "chain",
    "dhan",
    "context",
    "candidate",
    "trade",
    "trades",
    "pnl",
    "ledger",
    "decision",
)

OI_FIELD_TOKENS = (
    "oi",
    "open_interest",
    "oi_change",
    "oi_wall",
    "wall",
    "strike_score",
    "nearest_call",
    "nearest_put",
    "call_wall",
    "put_wall",
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

COST_FIELDS = (
    "cost",
    "costs",
    "charges",
    "fees",
    "brokerage",
    "transaction_cost",
    "round_trip_cost",
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

REGIME_FIELDS = (
    "regime",
    "market_regime",
    "volatility_regime",
)

PROVIDER_MODE_FIELDS = (
    "provider_mode",
    "mode",
    "runtime_mode",
    "dhan_mode",
)

OI_WALL_STATE_FIELDS = (
    "oi_wall_state",
    "wall_state",
    "oi_context_state",
    "oi_bias",
    "oi_wall_bias",
    "near_oi_wall",
    "near_wall",
)

OI_WALL_DISTANCE_FIELDS = (
    "oi_wall_distance",
    "oi_wall_distance_points",
    "wall_distance",
    "wall_distance_points",
    "distance_to_oi_wall",
    "distance_to_wall",
)

OI_WALL_STRENGTH_FIELDS = (
    "oi_wall_strength",
    "call_wall_strength",
    "put_wall_strength",
    "nearest_call_oi_resistance",
    "nearest_put_oi_support",
    "oi_support_strength",
    "oi_resistance_strength",
)

STRIKE_SCORE_FIELDS = (
    "strike_score",
    "selected_strike_score",
    "oi_score",
    "oi_change_support",
)


@dataclass(frozen=True)
class OIContextRecord:
    source_path: str
    row_index: int
    family: str
    side: str
    regime: str
    provider_mode: str
    wall_state: str
    has_oi_context: bool
    has_wall_distance: bool
    has_wall_strength: bool
    has_strike_score: bool
    net_pnl: float | None
    gross_pnl: float | None
    cost: float | None
    remarks: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
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


def _row_has_oi_context(row: dict[str, Any]) -> bool:
    for key, value in row.items():
        low = str(key).lower()
        if any(token in low for token in OI_FIELD_TOKENS):
            if value not in (None, ""):
                return True
    return False


def _cost(row: dict[str, Any]) -> float:
    total = 0.0
    found = False
    lower_map = {str(k).lower(): k for k in row.keys()}
    for field in COST_FIELDS:
        key = lower_map.get(field.lower())
        if key is None:
            continue
        val = _safe_float(row.get(key))
        if val is None:
            continue
        total += val
        found = True
    return total if found else 0.0


def _extract_net_gross_cost(row: dict[str, Any]) -> tuple[float | None, float | None, float | None, str]:
    cost = _cost(row)
    net = _safe_float(_first_present(row, NET_PNL_FIELDS))
    gross = _safe_float(_first_present(row, GROSS_PNL_FIELDS))
    if net is not None:
        return net, gross, cost, "explicit_net_pnl"
    if gross is not None:
        return gross - cost, gross, cost, "explicit_gross_pnl_minus_cost"
    return None, None, cost, "no_pnl_linkage"


def _boolish(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "near", "present", "pass"}:
        return True
    if text in {"0", "false", "no", "n", "away", "missing", "fail"}:
        return False
    return None


def _wall_state(row: dict[str, Any], near_distance_points: float) -> tuple[str, bool, bool, bool]:
    state_value = _first_present(row, OI_WALL_STATE_FIELDS)
    distance_value = _first_present(row, OI_WALL_DISTANCE_FIELDS)
    strength_value = _first_present(row, OI_WALL_STRENGTH_FIELDS)
    strike_score_value = _first_present(row, STRIKE_SCORE_FIELDS)

    has_distance = distance_value not in (None, "")
    has_strength = strength_value not in (None, "")
    has_strike_score = strike_score_value not in (None, "")

    if state_value not in (None, ""):
        bool_state = _boolish(state_value)
        if bool_state is True:
            return "NEAR_OI_WALL", has_distance, has_strength, has_strike_score
        if bool_state is False:
            return "AWAY_FROM_OI_WALL", has_distance, has_strength, has_strike_score
        return str(state_value).strip().upper().replace(" ", "_"), has_distance, has_strength, has_strike_score

    distance = _safe_float(distance_value)
    if distance is not None:
        if abs(distance) <= near_distance_points:
            return "NEAR_OI_WALL", has_distance, has_strength, has_strike_score
        return "AWAY_FROM_OI_WALL", has_distance, has_strength, has_strike_score

    if has_strength:
        return "OI_WALL_CONTEXT_PRESENT", has_distance, has_strength, has_strike_score
    if has_strike_score:
        return "STRIKE_SCORE_CONTEXT_PRESENT", has_distance, has_strength, has_strike_score

    return "OI_CONTEXT_PRESENT", has_distance, has_strength, has_strike_score


def extract_oi_context_record(
    row: dict[str, Any],
    *,
    source_path: str,
    row_index: int,
    near_distance_points: float,
) -> OIContextRecord | None:
    if not _row_has_oi_context(row):
        return None

    family = _first_text(row, FAMILY_FIELDS)
    side = _first_text(row, SIDE_FIELDS)
    regime = _first_text(row, REGIME_FIELDS)
    provider_mode = _first_text(row, PROVIDER_MODE_FIELDS)
    wall_state, has_distance, has_strength, has_strike_score = _wall_state(row, near_distance_points)
    net, gross, cost, pnl_source = _extract_net_gross_cost(row)

    remarks = pnl_source
    if net is None:
        remarks = "OI context found but no PnL linkage."

    return OIContextRecord(
        source_path=source_path,
        row_index=row_index,
        family=family,
        side=side,
        regime=regime,
        provider_mode=provider_mode,
        wall_state=wall_state,
        has_oi_context=True,
        has_wall_distance=has_distance,
        has_wall_strength=has_strength,
        has_strike_score=has_strike_score,
        net_pnl=net,
        gross_pnl=gross,
        cost=cost,
        remarks=remarks,
    )


def _read_csv_records(path: Path, relative_path: str, max_rows: int, near_distance_points: float) -> list[OIContextRecord]:
    records: list[OIContextRecord] = []
    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            if idx > max_rows:
                break
            rec = extract_oi_context_record(
                row,
                source_path=relative_path,
                row_index=idx,
                near_distance_points=near_distance_points,
            )
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
            "contexts",
            "snapshots",
        ):
            value = payload.get(key)
            if isinstance(value, list):
                return [x for x in value if isinstance(x, dict)]
        return [payload]
    return []


def _read_json_records(path: Path, relative_path: str, max_rows: int, near_distance_points: float) -> list[OIContextRecord]:
    records: list[OIContextRecord] = []
    if path.stat().st_size > 50 * 1024 * 1024:
        return records
    payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    rows = _dict_rows_from_json_payload(payload)
    for idx, row in enumerate(rows, start=1):
        if idx > max_rows:
            break
        rec = extract_oi_context_record(
            row,
            source_path=relative_path,
            row_index=idx,
            near_distance_points=near_distance_points,
        )
        if rec is not None:
            records.append(rec)
    return records


def _read_jsonl_records(path: Path, relative_path: str, max_rows: int, near_distance_points: float) -> list[OIContextRecord]:
    records: list[OIContextRecord] = []
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
            rec = extract_oi_context_record(
                row,
                source_path=relative_path,
                row_index=idx,
                near_distance_points=near_distance_points,
            )
            if rec is not None:
                records.append(rec)
    return records


def find_candidate_oi_files(project_root: str | Path, max_files: int = 500) -> list[Path]:
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


def read_oi_context_records(
    project_root: str | Path,
    *,
    max_rows_per_file: int = 20000,
    near_distance_points: float = 10.0,
) -> tuple[list[OIContextRecord], list[dict[str, Any]]]:
    root = Path(project_root).resolve()
    records: list[OIContextRecord] = []
    scanned_files: list[dict[str, Any]] = []

    for path in find_candidate_oi_files(root):
        relative_path = str(path.relative_to(root))
        before_count = len(records)
        try:
            suffix = path.suffix.lower()
            if suffix == ".csv":
                records.extend(_read_csv_records(path, relative_path, max_rows_per_file, near_distance_points))
            elif suffix == ".json":
                records.extend(_read_json_records(path, relative_path, max_rows_per_file, near_distance_points))
            elif suffix in (".jsonl", ".ndjson"):
                records.extend(_read_jsonl_records(path, relative_path, max_rows_per_file, near_distance_points))
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
        "pnl_linked_count": 0,
        "gross_pnl": 0.0,
        "net_pnl_after_costs": 0.0,
        "total_costs": 0.0,
        "winning_records": 0,
        "losing_records": 0,
        "flat_records": 0,
        "has_wall_distance_count": 0,
        "has_wall_strength_count": 0,
        "has_strike_score_count": 0,
    }


def _apply_record(bucket: dict[str, Any], record: OIContextRecord) -> None:
    bucket["record_count"] += 1
    if record.has_wall_distance:
        bucket["has_wall_distance_count"] += 1
    if record.has_wall_strength:
        bucket["has_wall_strength_count"] += 1
    if record.has_strike_score:
        bucket["has_strike_score_count"] += 1

    if record.net_pnl is None:
        return

    net = float(record.net_pnl)
    gross = float(record.gross_pnl if record.gross_pnl is not None else net)
    cost = float(record.cost or 0.0)

    bucket["pnl_linked_count"] += 1
    bucket["gross_pnl"] += gross
    bucket["net_pnl_after_costs"] += net
    bucket["total_costs"] += cost
    if net > 0:
        bucket["winning_records"] += 1
        bucket["_gross_profit"] = bucket.get("_gross_profit", 0.0) + net
    elif net < 0:
        bucket["losing_records"] += 1
        bucket["_gross_loss"] = bucket.get("_gross_loss", 0.0) + net
    else:
        bucket["flat_records"] += 1


def _finalize_bucket(bucket: dict[str, Any]) -> dict[str, Any]:
    linked = bucket["pnl_linked_count"]
    if linked > 0:
        bucket["average_net_pnl"] = round(bucket["net_pnl_after_costs"] / linked, 6)
        bucket["win_rate"] = round(bucket["winning_records"] / linked, 6)
    else:
        bucket["average_net_pnl"] = 0.0
        bucket["win_rate"] = 0.0

    gross_profit = bucket.pop("_gross_profit", 0.0)
    gross_loss = abs(bucket.pop("_gross_loss", 0.0))
    if gross_loss > 0:
        bucket["profit_factor"] = round(gross_profit / gross_loss, 6)
    elif gross_profit > 0:
        bucket["profit_factor"] = None
    else:
        bucket["profit_factor"] = 0.0

    for key in ("gross_pnl", "net_pnl_after_costs", "total_costs", "average_net_pnl"):
        bucket[key] = round(float(bucket.get(key, 0.0)), 6)
    return bucket


def _aggregate(records: list[OIContextRecord], key_name: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for rec in records:
        key = getattr(rec, key_name)
        bucket = result.setdefault(key, _bucket_template())
        _apply_record(bucket, rec)
    return {key: _finalize_bucket(bucket) for key, bucket in sorted(result.items())}


def _aggregate_family_side(records: list[OIContextRecord]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for rec in records:
        key = f"{rec.family}|{rec.side}|{rec.wall_state}"
        bucket = result.setdefault(
            key,
            {
                "family": rec.family,
                "side": rec.side,
                "wall_state": rec.wall_state,
                **_bucket_template(),
            },
        )
        _apply_record(bucket, rec)
    return {key: _finalize_bucket(bucket) for key, bucket in sorted(result.items())}


def build_oi_wall_impact_report(
    *,
    project_root: str | Path,
    run_id: str,
    source_label: str = "current_project",
    near_distance_points: float = 10.0,
) -> dict[str, Any]:
    records, scanned_files = read_oi_context_records(
        project_root,
        near_distance_points=near_distance_points,
    )

    total = _bucket_template()
    for rec in records:
        _apply_record(total, rec)
    total = _finalize_bucket(total)

    oi_context_record_count = total["record_count"]
    pnl_linked_count = total["pnl_linked_count"]
    net = float(total["net_pnl_after_costs"])

    if oi_context_record_count <= 0:
        oi_verdict = OI_VERDICT_INSUFFICIENT_OI_EVIDENCE
        research_verdict = VERDICT_INCONCLUSIVE_DATA_INSUFFICIENT
    elif pnl_linked_count <= 0:
        oi_verdict = OI_VERDICT_CONTEXT_FOUND_NO_PNL_LINKAGE
        research_verdict = VERDICT_RESEARCH_ONLY_FINDING
    elif net > 0:
        oi_verdict = OI_VERDICT_RESEARCH_POSITIVE
        research_verdict = VERDICT_RESEARCH_ONLY_FINDING
    elif net < 0:
        oi_verdict = OI_VERDICT_RESEARCH_NEGATIVE
        research_verdict = VERDICT_REJECT_NEGATIVE_EXPECTANCY
    else:
        oi_verdict = OI_VERDICT_RESEARCH_MIXED
        research_verdict = VERDICT_RESEARCH_ONLY_FINDING

    warnings: list[str] = []
    if oi_context_record_count <= 0:
        warnings.append("No OI/OI-wall/strike-score context rows found in scanned artifacts.")
    if pnl_linked_count <= 0 and oi_context_record_count > 0:
        warnings.append("OI context exists but no PnL linkage found; impact cannot be measured.")
    if any("candidate" in item["path"].lower() for item in scanned_files if item.get("records_found", 0) > 0):
        warnings.append("Candidate/audit artifacts contributed OI context; verify closed-trade linkage before promotion.")
    if net < 0 and pnl_linked_count > 0:
        warnings.append("OI-linked evidence is net negative; treat as diagnostic, not promotion evidence.")

    return {
        "schema_version": OI_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_utc": utc_now_iso(),
        "source_label": source_label,
        "project_root": str(Path(project_root).resolve()),
        "near_distance_points": near_distance_points,
        "non_live": True,
        "non_mutating": True,
        "pnl_computation_included": False,
        "strategy_ranking_included": False,
        "oi_wall_computation_included": True,
        "oi_wall_trigger_truth_allowed": False,
        "broker_io_included": False,
        "redis_live_write_included": False,
        "order_sending_included": False,
        "production_mutation_included": False,
        "paper_live_enablement_included": False,
        "oi_verdict": oi_verdict,
        "research_verdict": research_verdict,
        "summary": total,
        "by_wall_state": _aggregate(records, "wall_state"),
        "by_family": _aggregate(records, "family"),
        "by_side": _aggregate(records, "side"),
        "by_regime": _aggregate(records, "regime"),
        "by_provider_mode": _aggregate(records, "provider_mode"),
        "family_side_wall_matrix": _aggregate_family_side(records),
        "source_breakdown": _aggregate(records, "source_path"),
        "scanned_files": scanned_files,
        "oi_context_records_sample": [rec.to_dict() for rec in records[:80]],
        "warnings": warnings,
        "remarks": [
            "RAW-G uses OI/OI-wall/strike-selection context as research evidence only.",
            "RAW-G does not convert OI wall into immediate trigger truth.",
            "RAW-G does not mutate any strategy threshold or doctrine.",
            "RAW-G does not approve paper/live.",
            "If OI/PnL linkage is missing, verdict remains insufficient instead of guessing.",
        ],
    }


def build_manifest_for_report(*, run_id: str, report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": OI_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_utc": utc_now_iso(),
        "non_live": True,
        "non_mutating": True,
        "artifacts": [
            {"path": ARTIFACT_MANIFEST, "artifact_type": "raw_manifest"},
            {"path": ARTIFACT_OI_WALL_IMPACT, "artifact_type": "oi_wall_impact_report"},
            {"path": OI_CONTEXT_MATRIX_CSV, "artifact_type": "oi_context_matrix"},
            {"path": OI_SOURCE_BREAKDOWN_CSV, "artifact_type": "oi_source_breakdown"},
            {"path": SUMMARY_MD, "artifact_type": "oi_wall_summary"},
        ],
        "oi_verdict": report["oi_verdict"],
        "research_verdict": report["research_verdict"],
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
        "# RAW-G OI-Wall Impact Summary",
        "",
        f"Run ID: {report['run_id']}",
        f"Generated UTC: {report['generated_utc']}",
        "",
        "## Verdict",
        "",
        f"- oi_verdict: {report['oi_verdict']}",
        f"- research_verdict: {report['research_verdict']}",
        f"- oi_context_record_count: {s['record_count']}",
        f"- pnl_linked_count: {s['pnl_linked_count']}",
        f"- net_pnl_after_costs: {s['net_pnl_after_costs']}",
        f"- average_net_pnl: {s['average_net_pnl']}",
        f"- win_rate: {s['win_rate']}",
        "",
        "## OI-wall law",
        "",
        f"- oi_wall_trigger_truth_allowed: {report['oi_wall_trigger_truth_allowed']}",
        "",
        "## Warnings",
        "",
    ]
    if report["warnings"]:
        lines.extend(f"- {w}" for w in report["warnings"])
    else:
        lines.append("- none")
    lines.extend([
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
        f"- production_mutation_included: {report['production_mutation_included']}",
        "",
    ])
    return "\n".join(lines)


def write_oi_wall_impact_bundle(
    *,
    project_root: str | Path,
    output_dir: str | Path,
    run_id: str,
    source_label: str = "current_project",
    near_distance_points: float = 10.0,
) -> dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    report = build_oi_wall_impact_report(
        project_root=project_root,
        run_id=run_id,
        source_label=source_label,
        near_distance_points=near_distance_points,
    )
    manifest = build_manifest_for_report(run_id=run_id, report=report)
    summary = render_summary_markdown(report)

    write_json_file(out / ARTIFACT_OI_WALL_IMPACT, report)
    write_json_file(out / ARTIFACT_MANIFEST, manifest)
    write_text_file(out / SUMMARY_MD, summary)

    matrix_rows = list(report["family_side_wall_matrix"].values())
    _write_csv(
        out / OI_CONTEXT_MATRIX_CSV,
        matrix_rows,
        [
            "family",
            "side",
            "wall_state",
            "record_count",
            "pnl_linked_count",
            "gross_pnl",
            "net_pnl_after_costs",
            "total_costs",
            "winning_records",
            "losing_records",
            "flat_records",
            "has_wall_distance_count",
            "has_wall_strength_count",
            "has_strike_score_count",
            "average_net_pnl",
            "win_rate",
            "profit_factor",
        ],
    )

    source_rows = [
        {"source_path": key, **value}
        for key, value in report["source_breakdown"].items()
    ]
    _write_csv(
        out / OI_SOURCE_BREAKDOWN_CSV,
        source_rows,
        [
            "source_path",
            "record_count",
            "pnl_linked_count",
            "gross_pnl",
            "net_pnl_after_costs",
            "total_costs",
            "winning_records",
            "losing_records",
            "flat_records",
            "has_wall_distance_count",
            "has_wall_strength_count",
            "has_strike_score_count",
            "average_net_pnl",
            "win_rate",
            "profit_factor",
        ],
    )

    return {
        "output_dir": str(out),
        "manifest": str(out / ARTIFACT_MANIFEST),
        "oi_wall_impact_report": str(out / ARTIFACT_OI_WALL_IMPACT),
        "oi_context_matrix_csv": str(out / OI_CONTEXT_MATRIX_CSV),
        "oi_source_breakdown_csv": str(out / OI_SOURCE_BREAKDOWN_CSV),
        "summary_markdown": str(out / SUMMARY_MD),
        "oi_verdict": report["oi_verdict"],
        "research_verdict": report["research_verdict"],
        "oi_context_record_count": report["summary"]["record_count"],
        "pnl_linked_count": report["summary"]["pnl_linked_count"],
        "net_pnl_after_costs": report["summary"]["net_pnl_after_costs"],
        "warning_count": len(report["warnings"]),
    }
