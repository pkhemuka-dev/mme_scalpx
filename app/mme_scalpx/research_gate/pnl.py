"""PnL analytics desk for RAW / Research Gate.

RAW-E computes PnL from existing replay/research/proof artifacts only.

It does not infer trades when evidence is missing, does not call brokers, does not
write Redis, does not send orders, does not mutate live runtime, and does not rank
strategies. Strategy ranking is reserved for RAW-F.
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
    ARTIFACT_PNL_REPORT,
    VERDICT_INCONCLUSIVE_DATA_INSUFFICIENT,
    VERDICT_PASS_BUT_LOW_SAMPLE,
    VERDICT_PASS_WITH_POSITIVE_EDGE,
    VERDICT_REJECT_NEGATIVE_EXPECTANCY,
    VERDICT_RESEARCH_ONLY_FINDING,
)
from .writer import write_json_file, write_text_file


PNL_SCHEMA_VERSION = "RAW-E.1"

PNL_VERDICT_NO_TRADE_EVIDENCE = "PNL_INSUFFICIENT_TRADE_EVIDENCE"
PNL_VERDICT_PASS_POSITIVE = "PNL_PASS_POSITIVE"
PNL_VERDICT_REJECT_NEGATIVE = "PNL_REJECT_NEGATIVE"
PNL_VERDICT_FLAT_OR_LOW_SIGNAL = "PNL_FLAT_OR_LOW_SIGNAL"

TRADE_FILE_NAME_TOKENS = (
    "trade",
    "trades",
    "ledger",
    "pnl",
    "fill",
    "fills",
    "candidate_audit",
)

SUPPORTED_SUFFIXES = (".csv", ".json", ".jsonl", ".ndjson")

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

ENTRY_FIELDS = (
    "entry_price",
    "avg_entry_price",
    "entry_avg_price",
    "buy_price",
)

EXIT_FIELDS = (
    "exit_price",
    "avg_exit_price",
    "exit_avg_price",
    "sell_price",
)

QTY_FIELDS = (
    "qty",
    "quantity",
    "filled_qty",
    "exit_qty",
    "contracts",
    "lots",
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


@dataclass(frozen=True)
class TradePnlRecord:
    source_path: str
    row_index: int
    family: str
    side: str
    regime: str
    provider_mode: str
    gross_pnl: float | None
    net_pnl: float | None
    cost: float | None
    pnl_source: str
    remarks: str = ""

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
    text = str(value).strip()
    if not text:
        return None
    text = text.replace(",", "")
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


def _first_text(row: dict[str, Any], fields: Iterable[str], default: str) -> str:
    value = _first_present(row, fields)
    if value in (None, ""):
        return default
    return str(value)


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


def extract_trade_pnl_from_row(
    row: dict[str, Any],
    *,
    source_path: str,
    row_index: int,
) -> TradePnlRecord | None:
    family = _first_text(row, FAMILY_FIELDS, "UNKNOWN")
    side = _first_text(row, SIDE_FIELDS, "UNKNOWN")
    regime = _first_text(row, REGIME_FIELDS, "UNKNOWN")
    provider_mode = _first_text(row, PROVIDER_MODE_FIELDS, "UNKNOWN")
    cost = _cost(row)

    net = _safe_float(_first_present(row, NET_PNL_FIELDS))
    if net is not None:
        gross = _safe_float(_first_present(row, GROSS_PNL_FIELDS))
        return TradePnlRecord(
            source_path=source_path,
            row_index=row_index,
            family=family,
            side=side,
            regime=regime,
            provider_mode=provider_mode,
            gross_pnl=gross,
            net_pnl=net,
            cost=cost,
            pnl_source="explicit_net_pnl",
        )

    gross = _safe_float(_first_present(row, GROSS_PNL_FIELDS))
    if gross is not None:
        return TradePnlRecord(
            source_path=source_path,
            row_index=row_index,
            family=family,
            side=side,
            regime=regime,
            provider_mode=provider_mode,
            gross_pnl=gross,
            net_pnl=gross - cost,
            cost=cost,
            pnl_source="explicit_gross_pnl_minus_cost",
        )

    entry = _safe_float(_first_present(row, ENTRY_FIELDS))
    exit_ = _safe_float(_first_present(row, EXIT_FIELDS))
    qty = _safe_float(_first_present(row, QTY_FIELDS))
    if entry is not None and exit_ is not None:
        effective_qty = qty if qty is not None and qty > 0 else 1.0
        derived_gross = (exit_ - entry) * effective_qty
        return TradePnlRecord(
            source_path=source_path,
            row_index=row_index,
            family=family,
            side=side,
            regime=regime,
            provider_mode=provider_mode,
            gross_pnl=derived_gross,
            net_pnl=derived_gross - cost,
            cost=cost,
            pnl_source="derived_from_entry_exit_qty",
            remarks="Derived PnL from entry/exit price fields; verify quantity semantics before promotion.",
        )

    return None


def _read_csv_records(path: Path, relative_path: str, max_rows: int) -> list[TradePnlRecord]:
    records: list[TradePnlRecord] = []
    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            if idx > max_rows:
                break
            rec = extract_trade_pnl_from_row(row, source_path=relative_path, row_index=idx)
            if rec is not None:
                records.append(rec)
    return records


def _dict_rows_from_json_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        for key in ("trades", "trade_log", "rows", "records", "fills", "orders", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return [x for x in value if isinstance(x, dict)]
        return [payload]
    return []


def _read_json_records(path: Path, relative_path: str, max_rows: int) -> list[TradePnlRecord]:
    records: list[TradePnlRecord] = []
    if path.stat().st_size > 50 * 1024 * 1024:
        return records
    payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    rows = _dict_rows_from_json_payload(payload)
    for idx, row in enumerate(rows, start=1):
        if idx > max_rows:
            break
        rec = extract_trade_pnl_from_row(row, source_path=relative_path, row_index=idx)
        if rec is not None:
            records.append(rec)
    return records


def _read_jsonl_records(path: Path, relative_path: str, max_rows: int) -> list[TradePnlRecord]:
    records: list[TradePnlRecord] = []
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
            rec = extract_trade_pnl_from_row(row, source_path=relative_path, row_index=idx)
            if rec is not None:
                records.append(rec)
    return records


def find_candidate_trade_files(project_root: str | Path, max_files: int = 300) -> list[Path]:
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
                if not any(token in low for token in TRADE_FILE_NAME_TOKENS):
                    continue
                candidates.append(path)
                if len(candidates) >= max_files:
                    return sorted(candidates)
    return sorted(candidates)


def read_trade_pnl_records(project_root: str | Path, max_rows_per_file: int = 20000) -> tuple[list[TradePnlRecord], list[dict[str, Any]]]:
    root = Path(project_root).resolve()
    records: list[TradePnlRecord] = []
    scanned_files: list[dict[str, Any]] = []

    for path in find_candidate_trade_files(root):
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


def _empty_bucket() -> dict[str, Any]:
    return {
        "trade_count": 0,
        "winning_trades": 0,
        "losing_trades": 0,
        "flat_trades": 0,
        "gross_pnl": 0.0,
        "net_pnl_after_costs": 0.0,
        "total_costs": 0.0,
        "average_net_pnl": 0.0,
        "win_rate": 0.0,
        "profit_factor": None,
        "expectancy": 0.0,
    }


def _apply_record(bucket: dict[str, Any], record: TradePnlRecord) -> None:
    net = float(record.net_pnl or 0.0)
    gross = float(record.gross_pnl or net)
    cost = float(record.cost or 0.0)

    bucket["trade_count"] += 1
    bucket["gross_pnl"] += gross
    bucket["net_pnl_after_costs"] += net
    bucket["total_costs"] += cost
    if net > 0:
        bucket["winning_trades"] += 1
    elif net < 0:
        bucket["losing_trades"] += 1
    else:
        bucket["flat_trades"] += 1


def _finalize_bucket(bucket: dict[str, Any]) -> dict[str, Any]:
    count = bucket["trade_count"]
    if count <= 0:
        return bucket

    wins = bucket["winning_trades"]
    losses = bucket["losing_trades"]
    bucket["average_net_pnl"] = round(bucket["net_pnl_after_costs"] / count, 6)
    bucket["win_rate"] = round(wins / count, 6)

    gross_profit = bucket.get("_gross_profit", 0.0)
    gross_loss_abs = abs(bucket.get("_gross_loss", 0.0))
    if gross_loss_abs > 0:
        bucket["profit_factor"] = round(gross_profit / gross_loss_abs, 6)
    elif gross_profit > 0:
        bucket["profit_factor"] = None
    else:
        bucket["profit_factor"] = 0.0

    bucket["expectancy"] = bucket["average_net_pnl"]

    for hidden in ("_gross_profit", "_gross_loss"):
        bucket.pop(hidden, None)

    for key in ("gross_pnl", "net_pnl_after_costs", "total_costs", "average_net_pnl", "expectancy"):
        if isinstance(bucket.get(key), float):
            bucket[key] = round(bucket[key], 6)
    return bucket


def _aggregate(records: list[TradePnlRecord], key_name: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for rec in records:
        key = getattr(rec, key_name)
        bucket = result.setdefault(key, _empty_bucket())
        net = float(rec.net_pnl or 0.0)
        if net > 0:
            bucket["_gross_profit"] = bucket.get("_gross_profit", 0.0) + net
        elif net < 0:
            bucket["_gross_loss"] = bucket.get("_gross_loss", 0.0) + net
        _apply_record(bucket, rec)
    return {key: _finalize_bucket(bucket) for key, bucket in sorted(result.items())}


def _equity_curve(records: list[TradePnlRecord]) -> tuple[list[dict[str, Any]], float]:
    curve: list[dict[str, Any]] = []
    equity = 0.0
    peak = 0.0
    max_drawdown = 0.0
    for idx, rec in enumerate(records, start=1):
        equity += float(rec.net_pnl or 0.0)
        peak = max(peak, equity)
        drawdown = equity - peak
        max_drawdown = min(max_drawdown, drawdown)
        curve.append({
            "trade_index": idx,
            "net_pnl": round(float(rec.net_pnl or 0.0), 6),
            "equity": round(equity, 6),
            "drawdown": round(drawdown, 6),
            "family": rec.family,
            "side": rec.side,
            "source_path": rec.source_path,
            "row_index": rec.row_index,
        })
    return curve, round(max_drawdown, 6)


def build_pnl_report(
    *,
    project_root: str | Path,
    run_id: str,
    source_label: str = "current_project",
) -> dict[str, Any]:
    records, scanned_files = read_trade_pnl_records(project_root)
    total = _empty_bucket()

    for rec in records:
        net = float(rec.net_pnl or 0.0)
        if net > 0:
            total["_gross_profit"] = total.get("_gross_profit", 0.0) + net
        elif net < 0:
            total["_gross_loss"] = total.get("_gross_loss", 0.0) + net
        _apply_record(total, rec)
    total = _finalize_bucket(total)

    equity_curve, max_drawdown = _equity_curve(records)
    total["max_drawdown"] = max_drawdown

    trade_count = total["trade_count"]
    net_total = float(total["net_pnl_after_costs"])

    if trade_count <= 0:
        pnl_verdict = PNL_VERDICT_NO_TRADE_EVIDENCE
        research_verdict = VERDICT_INCONCLUSIVE_DATA_INSUFFICIENT
    elif trade_count < 5:
        pnl_verdict = PNL_VERDICT_FLAT_OR_LOW_SIGNAL if net_total >= 0 else PNL_VERDICT_REJECT_NEGATIVE
        research_verdict = VERDICT_PASS_BUT_LOW_SAMPLE if net_total >= 0 else VERDICT_REJECT_NEGATIVE_EXPECTANCY
    elif net_total > 0:
        pnl_verdict = PNL_VERDICT_PASS_POSITIVE
        research_verdict = VERDICT_PASS_WITH_POSITIVE_EDGE
    elif net_total < 0:
        pnl_verdict = PNL_VERDICT_REJECT_NEGATIVE
        research_verdict = VERDICT_REJECT_NEGATIVE_EXPECTANCY
    else:
        pnl_verdict = PNL_VERDICT_FLAT_OR_LOW_SIGNAL
        research_verdict = VERDICT_RESEARCH_ONLY_FINDING

    return {
        "schema_version": PNL_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_utc": utc_now_iso(),
        "source_label": source_label,
        "project_root": str(Path(project_root).resolve()),
        "non_live": True,
        "non_mutating": True,
        "pnl_computation_included": True,
        "strategy_ranking_included": False,
        "oi_wall_computation_included": False,
        "broker_io_included": False,
        "redis_live_write_included": False,
        "order_sending_included": False,
        "production_mutation_included": False,
        "pnl_verdict": pnl_verdict,
        "research_verdict": research_verdict,
        "summary": total,
        "by_family": _aggregate(records, "family"),
        "by_side": _aggregate(records, "side"),
        "by_regime": _aggregate(records, "regime"),
        "by_provider_mode": _aggregate(records, "provider_mode"),
        "scanned_files": scanned_files,
        "trade_records_sample": [rec.to_dict() for rec in records[:50]],
        "equity_curve_sample": equity_curve[:100],
        "remarks": [
            "RAW-E calculates PnL only from explicit trade/PnL evidence or entry/exit/qty fields found in existing artifacts.",
            "RAW-E does not infer missing trades.",
            "RAW-E does not rank strategies; ranking is reserved for RAW-F.",
            "RAW-E does not compute OI-wall impact; that is reserved for RAW-G.",
            "If trade_count is zero, verdict remains insufficient trade evidence instead of inventing results.",
        ],
    }


def build_manifest_for_report(*, run_id: str, report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": PNL_SCHEMA_VERSION,
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
                "path": ARTIFACT_PNL_REPORT,
                "artifact_type": "pnl_report",
            },
            {
                "path": "RAW_E_PNL_SUMMARY.md",
                "artifact_type": "pnl_summary",
            },
        ],
        "pnl_verdict": report["pnl_verdict"],
        "research_verdict": report["research_verdict"],
    }


def render_summary_markdown(report: dict[str, Any]) -> str:
    s = report["summary"]
    lines = [
        "# RAW-E PnL Summary",
        "",
        f"Run ID: {report['run_id']}",
        f"Generated UTC: {report['generated_utc']}",
        "",
        "## Verdict",
        "",
        f"- pnl_verdict: {report['pnl_verdict']}",
        f"- research_verdict: {report['research_verdict']}",
        "",
        "## Total PnL",
        "",
        f"- trade_count: {s['trade_count']}",
        f"- gross_pnl: {s['gross_pnl']}",
        f"- net_pnl_after_costs: {s['net_pnl_after_costs']}",
        f"- total_costs: {s['total_costs']}",
        f"- win_rate: {s['win_rate']}",
        f"- profit_factor: {s['profit_factor']}",
        f"- expectancy: {s['expectancy']}",
        f"- max_drawdown: {s.get('max_drawdown')}",
        "",
        "## Boundary confirmation",
        "",
        f"- non_live: {report['non_live']}",
        f"- non_mutating: {report['non_mutating']}",
        f"- strategy_ranking_included: {report['strategy_ranking_included']}",
        f"- oi_wall_computation_included: {report['oi_wall_computation_included']}",
        f"- broker_io_included: {report['broker_io_included']}",
        f"- redis_live_write_included: {report['redis_live_write_included']}",
        f"- order_sending_included: {report['order_sending_included']}",
        "",
        "## Scanned files",
        "",
    ]
    if report["scanned_files"]:
        for item in report["scanned_files"][:50]:
            lines.append(f"- {item['path']} :: {item['status']} :: records_found={item['records_found']}")
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def write_pnl_report_bundle(
    *,
    project_root: str | Path,
    output_dir: str | Path,
    run_id: str,
    source_label: str = "current_project",
) -> dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    report = build_pnl_report(
        project_root=project_root,
        run_id=run_id,
        source_label=source_label,
    )
    manifest = build_manifest_for_report(run_id=run_id, report=report)
    summary = render_summary_markdown(report)

    write_json_file(out / ARTIFACT_PNL_REPORT, report)
    write_json_file(out / ARTIFACT_MANIFEST, manifest)
    write_text_file(out / "RAW_E_PNL_SUMMARY.md", summary)

    return {
        "output_dir": str(out),
        "manifest": str(out / ARTIFACT_MANIFEST),
        "pnl_report": str(out / ARTIFACT_PNL_REPORT),
        "summary_markdown": str(out / "RAW_E_PNL_SUMMARY.md"),
        "pnl_verdict": report["pnl_verdict"],
        "research_verdict": report["research_verdict"],
        "trade_count": report["summary"]["trade_count"],
        "net_pnl_after_costs": report["summary"]["net_pnl_after_costs"],
        "scanned_file_count": len(report["scanned_files"]),
    }
