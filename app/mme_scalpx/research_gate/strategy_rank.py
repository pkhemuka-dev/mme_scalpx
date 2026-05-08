"""Strategy ranking desk for RAW / Research Gate.

RAW-F consumes RAW-E PnL reports and ranks available family/side/regime/provider buckets.

It does not read brokers, does not write Redis, does not send orders, does not mutate
strategy/risk/execution, and does not approve paper/live. Ranking is research-only.
"""

from __future__ import annotations

import csv
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .contracts import (
    ARTIFACT_MANIFEST,
    ARTIFACT_STRATEGY_RANK,
    VERDICT_INCONCLUSIVE_DATA_INSUFFICIENT,
    VERDICT_REJECT_NEGATIVE_EXPECTANCY,
    VERDICT_RESEARCH_ONLY_FINDING,
)
from .writer import write_json_file, write_text_file


RANK_SCHEMA_VERSION = "RAW-F.1"

RANK_VERDICT_INSUFFICIENT_TRADE_EVIDENCE = "RANK_INSUFFICIENT_TRADE_EVIDENCE"
RANK_VERDICT_INSUFFICIENT_FAMILY_LABELS = "RANK_INSUFFICIENT_FAMILY_LABELS"
RANK_VERDICT_NEGATIVE_EXPECTANCY_DIAGNOSIS = "RANK_NEGATIVE_EXPECTANCY_DIAGNOSIS"
RANK_VERDICT_AVAILABLE_FOR_RESEARCH = "RANK_AVAILABLE_FOR_RESEARCH"
RANK_VERDICT_RESEARCH_ONLY_WARNING = "RANK_RESEARCH_ONLY_WARNING"

UNKNOWN = "UNKNOWN"

FAMILY_SIDE_MATRIX_CSV = "family_side_matrix.csv"
SOURCE_BREAKDOWN_CSV = "source_artifact_breakdown.csv"
SUMMARY_MD = "RAW_F_STRATEGY_RANK_SUMMARY.md"


@dataclass(frozen=True)
class RankRow:
    bucket_type: str
    bucket_name: str
    trade_count: int
    net_pnl_after_costs: float
    gross_pnl: float
    profit_factor: float | None
    expectancy: float
    win_rate: float
    max_drawdown: float | None = None
    rank_score: float = 0.0
    confidence: str = "LOW"
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "")
    if not text:
        return default
    try:
        return float(text)
    except ValueError:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except Exception:
        return default


def load_pnl_report(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    payload = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected PnL report JSON object: {p}")
    if "summary" not in payload:
        raise ValueError(f"PnL report missing summary: {p}")
    return payload


def _confidence(trade_count: int, bucket_name: str, *, min_trade_count: int) -> str:
    if bucket_name == UNKNOWN:
        return "LOW_UNKNOWN_LABEL"
    if trade_count <= 0:
        return "NONE"
    if trade_count < min_trade_count:
        return "LOW_SAMPLE"
    if trade_count < max(min_trade_count * 3, 10):
        return "MEDIUM"
    return "HIGH"


def _score_bucket(bucket: dict[str, Any], bucket_name: str, *, min_trade_count: int) -> tuple[float, str, str]:
    trade_count = _safe_int(bucket.get("trade_count"))
    net = _safe_float(bucket.get("net_pnl_after_costs"))
    expectancy = _safe_float(bucket.get("expectancy"))
    win_rate = _safe_float(bucket.get("win_rate"))
    pf = bucket.get("profit_factor")
    pf_num = _safe_float(pf, 0.0) if pf is not None else 0.0

    conf = _confidence(trade_count, bucket_name, min_trade_count=min_trade_count)
    sample_factor = min(trade_count / max(float(min_trade_count), 1.0), 1.0)

    unknown_penalty = 0.50 if bucket_name == UNKNOWN else 1.0
    score = (
        (net * 1.0)
        + (expectancy * max(trade_count, 1) * 0.25)
        + (win_rate * 25.0)
        + (pf_num * 5.0)
    ) * sample_factor * unknown_penalty

    notes: list[str] = []
    if bucket_name == UNKNOWN:
        notes.append("UNKNOWN label; do not use for production conclusion.")
    if trade_count < min_trade_count:
        notes.append("Low sample count.")
    if net < 0:
        notes.append("Negative net PnL.")
    return round(score, 6), conf, " ".join(notes)


def _rank_from_bucket_map(
    bucket_type: str,
    bucket_map: dict[str, Any],
    *,
    min_trade_count: int,
) -> list[RankRow]:
    rows: list[RankRow] = []
    for name, bucket in sorted(bucket_map.items()):
        if not isinstance(bucket, dict):
            continue
        score, conf, notes = _score_bucket(bucket, name, min_trade_count=min_trade_count)
        rows.append(
            RankRow(
                bucket_type=bucket_type,
                bucket_name=name,
                trade_count=_safe_int(bucket.get("trade_count")),
                net_pnl_after_costs=round(_safe_float(bucket.get("net_pnl_after_costs")), 6),
                gross_pnl=round(_safe_float(bucket.get("gross_pnl")), 6),
                profit_factor=bucket.get("profit_factor"),
                expectancy=round(_safe_float(bucket.get("expectancy")), 6),
                win_rate=round(_safe_float(bucket.get("win_rate")), 6),
                max_drawdown=_safe_float(bucket.get("max_drawdown")) if bucket.get("max_drawdown") is not None else None,
                rank_score=score,
                confidence=conf,
                notes=notes,
            )
        )
    rows.sort(key=lambda r: (r.rank_score, r.net_pnl_after_costs, r.trade_count), reverse=True)
    return rows


def _bucket_template() -> dict[str, Any]:
    return {
        "trade_count": 0,
        "gross_pnl": 0.0,
        "net_pnl_after_costs": 0.0,
        "winning_trades": 0,
        "losing_trades": 0,
        "flat_trades": 0,
        "total_costs": 0.0,
    }


def _finalize_matrix_bucket(bucket: dict[str, Any]) -> dict[str, Any]:
    count = bucket["trade_count"]
    net = bucket["net_pnl_after_costs"]
    if count > 0:
        bucket["expectancy"] = round(net / count, 6)
        bucket["win_rate"] = round(bucket["winning_trades"] / count, 6)
    else:
        bucket["expectancy"] = 0.0
        bucket["win_rate"] = 0.0

    gross_profit = bucket.pop("_gross_profit", 0.0)
    gross_loss = abs(bucket.pop("_gross_loss", 0.0))
    if gross_loss > 0:
        bucket["profit_factor"] = round(gross_profit / gross_loss, 6)
    elif gross_profit > 0:
        bucket["profit_factor"] = None
    else:
        bucket["profit_factor"] = 0.0

    for key in ("gross_pnl", "net_pnl_after_costs", "total_costs", "expectancy"):
        bucket[key] = round(float(bucket.get(key, 0.0)), 6)
    return bucket


def build_family_side_matrix_from_sample(pnl_report: dict[str, Any]) -> dict[str, Any]:
    rows = pnl_report.get("trade_records_sample") or []
    matrix: dict[str, dict[str, Any]] = {}

    for row in rows:
        if not isinstance(row, dict):
            continue
        family = str(row.get("family") or UNKNOWN)
        side = str(row.get("side") or UNKNOWN)
        key = f"{family}|{side}"

        bucket = matrix.setdefault(
            key,
            {
                "family": family,
                "side": side,
                **_bucket_template(),
            },
        )

        net = _safe_float(row.get("net_pnl"))
        gross = _safe_float(row.get("gross_pnl"), net)
        cost = _safe_float(row.get("cost"))

        bucket["trade_count"] += 1
        bucket["gross_pnl"] += gross
        bucket["net_pnl_after_costs"] += net
        bucket["total_costs"] += cost

        if net > 0:
            bucket["winning_trades"] += 1
            bucket["_gross_profit"] = bucket.get("_gross_profit", 0.0) + net
        elif net < 0:
            bucket["losing_trades"] += 1
            bucket["_gross_loss"] = bucket.get("_gross_loss", 0.0) + net
        else:
            bucket["flat_trades"] += 1

    finalized = {key: _finalize_matrix_bucket(bucket) for key, bucket in matrix.items()}
    return finalized


def build_source_breakdown_from_sample(pnl_report: dict[str, Any]) -> dict[str, Any]:
    rows = pnl_report.get("trade_records_sample") or []
    result: dict[str, Any] = {}

    for row in rows:
        if not isinstance(row, dict):
            continue
        source = str(row.get("source_path") or UNKNOWN)
        bucket = result.setdefault(source, _bucket_template())
        net = _safe_float(row.get("net_pnl"))
        gross = _safe_float(row.get("gross_pnl"), net)
        cost = _safe_float(row.get("cost"))

        bucket["trade_count"] += 1
        bucket["gross_pnl"] += gross
        bucket["net_pnl_after_costs"] += net
        bucket["total_costs"] += cost
        if net > 0:
            bucket["winning_trades"] += 1
            bucket["_gross_profit"] = bucket.get("_gross_profit", 0.0) + net
        elif net < 0:
            bucket["losing_trades"] += 1
            bucket["_gross_loss"] = bucket.get("_gross_loss", 0.0) + net
        else:
            bucket["flat_trades"] += 1

    return {key: _finalize_matrix_bucket(bucket) for key, bucket in result.items()}


def _best_labeled(rows: list[RankRow], *, min_trade_count: int) -> dict[str, Any] | None:
    for row in rows:
        if row.bucket_name == UNKNOWN:
            continue
        if row.trade_count < min_trade_count:
            continue
        return row.to_dict()
    return None


def _worst_labeled(rows: list[RankRow]) -> dict[str, Any] | None:
    candidates = [r for r in rows if r.bucket_name != UNKNOWN and r.trade_count > 0]
    if not candidates:
        return None
    candidates.sort(key=lambda r: (r.net_pnl_after_costs, r.expectancy, r.rank_score))
    return candidates[0].to_dict()


def _unknown_ratio(pnl_report: dict[str, Any]) -> float:
    total = _safe_int(pnl_report.get("summary", {}).get("trade_count"))
    if total <= 0:
        return 1.0
    unknown_count = 0
    for row in pnl_report.get("trade_records_sample") or []:
        if not isinstance(row, dict):
            continue
        if str(row.get("family") or UNKNOWN) == UNKNOWN:
            unknown_count += 1
    sample_count = len(pnl_report.get("trade_records_sample") or [])
    if sample_count <= 0:
        return 1.0
    return round(unknown_count / sample_count, 6)


def build_strategy_rank_report(
    *,
    pnl_report_path: str | Path,
    run_id: str,
    min_family_trade_count: int = 3,
) -> dict[str, Any]:
    pnl_report = load_pnl_report(pnl_report_path)
    summary = pnl_report.get("summary", {})
    trade_count = _safe_int(summary.get("trade_count"))
    net_pnl = _safe_float(summary.get("net_pnl_after_costs"))
    unknown_family_ratio = _unknown_ratio(pnl_report)

    family_rank = _rank_from_bucket_map(
        "family",
        pnl_report.get("by_family") or {},
        min_trade_count=min_family_trade_count,
    )
    side_rank = _rank_from_bucket_map(
        "side",
        pnl_report.get("by_side") or {},
        min_trade_count=min_family_trade_count,
    )
    regime_rank = _rank_from_bucket_map(
        "regime",
        pnl_report.get("by_regime") or {},
        min_trade_count=min_family_trade_count,
    )
    provider_mode_rank = _rank_from_bucket_map(
        "provider_mode",
        pnl_report.get("by_provider_mode") or {},
        min_trade_count=min_family_trade_count,
    )

    family_side_matrix = build_family_side_matrix_from_sample(pnl_report)
    source_breakdown = build_source_breakdown_from_sample(pnl_report)

    best_family = _best_labeled(family_rank, min_trade_count=min_family_trade_count)
    worst_family = _worst_labeled(family_rank)
    best_side = _best_labeled(side_rank, min_trade_count=min_family_trade_count)
    worst_side = _worst_labeled(side_rank)

    warnings: list[str] = []
    if trade_count <= 0:
        rank_verdict = RANK_VERDICT_INSUFFICIENT_TRADE_EVIDENCE
        research_verdict = VERDICT_INCONCLUSIVE_DATA_INSUFFICIENT
        warnings.append("No trade evidence available; no ranking conclusion allowed.")
    elif not best_family:
        rank_verdict = RANK_VERDICT_INSUFFICIENT_FAMILY_LABELS
        research_verdict = VERDICT_INCONCLUSIVE_DATA_INSUFFICIENT
        warnings.append("No labeled family bucket has enough trades for ranking conclusion.")
    elif net_pnl < 0:
        rank_verdict = RANK_VERDICT_NEGATIVE_EXPECTANCY_DIAGNOSIS
        research_verdict = VERDICT_REJECT_NEGATIVE_EXPECTANCY
        warnings.append("Overall PnL is negative; use ranking for diagnosis only, not promotion.")
    else:
        rank_verdict = RANK_VERDICT_AVAILABLE_FOR_RESEARCH
        research_verdict = VERDICT_RESEARCH_ONLY_FINDING

    if unknown_family_ratio > 0.25:
        warnings.append("High UNKNOWN family label ratio; rankings may be low confidence.")

    if any("candidate" in str(src).lower() for src in source_breakdown):
        warnings.append("Candidate/audit source artifacts detected; verify these are closed trades before promotion.")

    return {
        "schema_version": RANK_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_utc": utc_now_iso(),
        "pnl_report_path": str(pnl_report_path),
        "non_live": True,
        "non_mutating": True,
        "pnl_computation_included": False,
        "strategy_ranking_included": True,
        "oi_wall_computation_included": False,
        "broker_io_included": False,
        "redis_live_write_included": False,
        "order_sending_included": False,
        "production_mutation_included": False,
        "rank_verdict": rank_verdict,
        "research_verdict": research_verdict,
        "overall_pnl_verdict_from_raw_e": pnl_report.get("pnl_verdict"),
        "overall_research_verdict_from_raw_e": pnl_report.get("research_verdict"),
        "overall_summary": summary,
        "unknown_family_ratio_in_sample": unknown_family_ratio,
        "min_family_trade_count": min_family_trade_count,
        "best_family": best_family,
        "worst_family": worst_family,
        "best_side": best_side,
        "worst_side": worst_side,
        "family_rank": [row.to_dict() for row in family_rank],
        "side_rank": [row.to_dict() for row in side_rank],
        "regime_rank": [row.to_dict() for row in regime_rank],
        "provider_mode_rank": [row.to_dict() for row in provider_mode_rank],
        "family_side_matrix": family_side_matrix,
        "source_artifact_breakdown": source_breakdown,
        "warnings": warnings,
        "remarks": [
            "RAW-F ranks only existing PnL buckets from RAW-E.",
            "RAW-F does not approve paper/live.",
            "RAW-F does not mutate strategy configuration.",
            "RAW-F does not compute OI-wall impact.",
            "Negative overall PnL turns ranking into diagnosis only.",
        ],
    }


def build_manifest_for_report(*, run_id: str, report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": RANK_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_utc": utc_now_iso(),
        "non_live": True,
        "non_mutating": True,
        "artifacts": [
            {"path": ARTIFACT_MANIFEST, "artifact_type": "raw_manifest"},
            {"path": ARTIFACT_STRATEGY_RANK, "artifact_type": "strategy_rank_report"},
            {"path": FAMILY_SIDE_MATRIX_CSV, "artifact_type": "family_side_matrix"},
            {"path": SOURCE_BREAKDOWN_CSV, "artifact_type": "source_artifact_breakdown"},
            {"path": SUMMARY_MD, "artifact_type": "strategy_rank_summary"},
        ],
        "rank_verdict": report["rank_verdict"],
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
    best_family = report.get("best_family") or {}
    worst_family = report.get("worst_family") or {}
    lines = [
        "# RAW-F Strategy Ranking Summary",
        "",
        f"Run ID: {report['run_id']}",
        f"Generated UTC: {report['generated_utc']}",
        "",
        "## Verdict",
        "",
        f"- rank_verdict: {report['rank_verdict']}",
        f"- research_verdict: {report['research_verdict']}",
        f"- RAW-E pnl_verdict: {report['overall_pnl_verdict_from_raw_e']}",
        f"- UNKNOWN family ratio in sample: {report['unknown_family_ratio_in_sample']}",
        "",
        "## Best / worst family",
        "",
        f"- best_family: {best_family.get('bucket_name')}",
        f"- best_family_net_pnl: {best_family.get('net_pnl_after_costs')}",
        f"- best_family_confidence: {best_family.get('confidence')}",
        f"- worst_family: {worst_family.get('bucket_name')}",
        f"- worst_family_net_pnl: {worst_family.get('net_pnl_after_costs')}",
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
        "",
    ])
    return "\n".join(lines)


def write_strategy_rank_bundle(
    *,
    pnl_report_path: str | Path,
    output_dir: str | Path,
    run_id: str,
    min_family_trade_count: int = 3,
) -> dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    report = build_strategy_rank_report(
        pnl_report_path=pnl_report_path,
        run_id=run_id,
        min_family_trade_count=min_family_trade_count,
    )
    manifest = build_manifest_for_report(run_id=run_id, report=report)
    summary = render_summary_markdown(report)

    write_json_file(out / ARTIFACT_STRATEGY_RANK, report)
    write_json_file(out / ARTIFACT_MANIFEST, manifest)
    write_text_file(out / SUMMARY_MD, summary)

    matrix_rows = list(report["family_side_matrix"].values())
    _write_csv(
        out / FAMILY_SIDE_MATRIX_CSV,
        matrix_rows,
        [
            "family",
            "side",
            "trade_count",
            "gross_pnl",
            "net_pnl_after_costs",
            "total_costs",
            "winning_trades",
            "losing_trades",
            "flat_trades",
            "win_rate",
            "profit_factor",
            "expectancy",
        ],
    )

    source_rows = [
        {"source_path": key, **value}
        for key, value in report["source_artifact_breakdown"].items()
    ]
    _write_csv(
        out / SOURCE_BREAKDOWN_CSV,
        source_rows,
        [
            "source_path",
            "trade_count",
            "gross_pnl",
            "net_pnl_after_costs",
            "total_costs",
            "winning_trades",
            "losing_trades",
            "flat_trades",
            "win_rate",
            "profit_factor",
            "expectancy",
        ],
    )

    return {
        "output_dir": str(out),
        "manifest": str(out / ARTIFACT_MANIFEST),
        "strategy_rank_report": str(out / ARTIFACT_STRATEGY_RANK),
        "family_side_matrix_csv": str(out / FAMILY_SIDE_MATRIX_CSV),
        "source_breakdown_csv": str(out / SOURCE_BREAKDOWN_CSV),
        "summary_markdown": str(out / SUMMARY_MD),
        "rank_verdict": report["rank_verdict"],
        "research_verdict": report["research_verdict"],
        "best_family": report["best_family"],
        "worst_family": report["worst_family"],
        "warning_count": len(report["warnings"]),
    }
