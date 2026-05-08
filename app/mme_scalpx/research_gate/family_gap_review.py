"""RAW-R family PnL review and producer-source gap map.

Reads RAW-Q backfilled evidence and produces:
- family-level PnL review
- UNKNOWN trade source gap map
- producer-source summary
- governance verdict

Review only. No broker IO. No Redis. No orders. No live/paper enablement.
"""

from __future__ import annotations

import csv
import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RAW_R_SCHEMA_VERSION = "RAW-R.1"

FAMILY_PNL_REVIEW_JSON = "family_pnl_review.json"
UNKNOWN_TRADE_GAP_CSV = "unknown_trade_source_gap_map.csv"
SOURCE_GAP_SUMMARY_CSV = "unknown_trade_source_gap_summary.csv"
PRODUCER_GAP_JSON = "producer_source_gap_review.json"
SUMMARY_MD = "RAW_R_FAMILY_PNL_AND_GAP_REVIEW.md"
MANIFEST_JSON = "manifest.json"

FAMILIES = {"MIST", "MISB", "MISC", "MISR", "MISO"}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def norm(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def norm_upper(value: Any) -> str:
    return norm(value).upper()


def is_unknown(value: Any) -> bool:
    text = norm_upper(value)
    return text in {"", "UNKNOWN", "NONE", "NULL", "NO_BLOCKER"}


def safe_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "")
    if not text or text.upper() in {"UNKNOWN", "NONE", "NULL"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def safe_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "pass", "filled", "executed", "closed"}:
        return True
    if text in {"0", "false", "no", "n", "fail", "none", "unknown"}:
        return False
    return None


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                rows.append(payload)
    return rows


def is_trade_row(row: dict[str, Any]) -> bool:
    closed = safe_bool(row.get("closed_trade_truth"))
    executed = norm_upper(row.get("candidate_vs_executed")) == "EXECUTED"
    row_kind = norm_upper(row.get("row_kind"))
    net = safe_float(row.get("net_pnl_after_costs"))
    gross = safe_float(row.get("gross_pnl"))
    return closed is True or (executed and net is not None) or (row_kind == "TRADE" and (net is not None or gross is not None))


def pnl_value(row: dict[str, Any]) -> float:
    net = safe_float(row.get("net_pnl_after_costs"))
    if net is not None:
        return net
    gross = safe_float(row.get("gross_pnl"))
    costs = safe_float(row.get("costs")) or 0.0
    if gross is not None:
        return gross - costs
    return 0.0


def family_name(row: dict[str, Any]) -> str:
    fam = norm_upper(row.get("family"))
    if fam in FAMILIES:
        return fam
    return "UNKNOWN"


def bucket_template() -> dict[str, Any]:
    return {
        "trade_count": 0,
        "net_pnl_after_costs": 0.0,
        "gross_pnl": 0.0,
        "winning_trades": 0,
        "losing_trades": 0,
        "flat_trades": 0,
        "_gross_profit": 0.0,
        "_gross_loss": 0.0,
    }


def apply_trade(bucket: dict[str, Any], row: dict[str, Any]) -> None:
    pnl = pnl_value(row)
    gross = safe_float(row.get("gross_pnl")) or pnl
    bucket["trade_count"] += 1
    bucket["net_pnl_after_costs"] += pnl
    bucket["gross_pnl"] += gross
    if pnl > 0:
        bucket["winning_trades"] += 1
        bucket["_gross_profit"] += pnl
    elif pnl < 0:
        bucket["losing_trades"] += 1
        bucket["_gross_loss"] += pnl
    else:
        bucket["flat_trades"] += 1


def finalize_bucket(bucket: dict[str, Any]) -> dict[str, Any]:
    count = int(bucket["trade_count"])
    net = float(bucket["net_pnl_after_costs"])
    gross_profit = float(bucket.pop("_gross_profit", 0.0))
    gross_loss = abs(float(bucket.pop("_gross_loss", 0.0)))
    bucket["net_pnl_after_costs"] = round(net, 6)
    bucket["gross_pnl"] = round(float(bucket["gross_pnl"]), 6)
    bucket["expectancy"] = round(net / count, 6) if count else 0.0
    bucket["win_rate"] = round(float(bucket["winning_trades"]) / count, 6) if count else 0.0
    if gross_loss > 0:
        bucket["profit_factor"] = round(gross_profit / gross_loss, 6)
    elif gross_profit > 0:
        bucket["profit_factor"] = None
    else:
        bucket["profit_factor"] = 0.0
    return bucket


def infer_likely_producer(source_artifact: str, row: dict[str, Any]) -> str:
    src = source_artifact.lower()
    row_kind = norm_upper(row.get("row_kind"))
    artifact_kind = norm_upper(row.get("artifact_kind"))

    if "comparison" in src:
        return "app/mme_scalpx/replay/comparison_artifacts.py"
    if "metric" in src:
        return "app/mme_scalpx/replay/metrics.py"
    if "frame" in src:
        return "app/mme_scalpx/replay/frame_export.py"
    if "trade" in src or "ledger" in src or row_kind == "TRADE" or artifact_kind == "TRADE_LOG":
        return "app/mme_scalpx/replay/reports.py or app/mme_scalpx/replay/artifacts.py"
    if "decision" in src or "candidate" in src or "audit" in src:
        return "app/mme_scalpx/replay/artifacts.py or app/mme_scalpx/replay/runner.py"
    if "proof" in src:
        return "run/proofs producer or proof harness; inspect source proof script"
    if "replay" in src:
        return "app/mme_scalpx/replay/runner.py or app/mme_scalpx/replay/engine.py"
    return "unknown producer; inspect source_artifact lineage"


def source_parent(source_artifact: str) -> str:
    if not source_artifact:
        return ""
    return str(Path(source_artifact).parent)


def build_review(rows: list[dict[str, Any]], input_jsonl: str) -> dict[str, Any]:
    trades = [row for row in rows if is_trade_row(row)]
    family_buckets: dict[str, dict[str, Any]] = defaultdict(bucket_template)
    unknown_rows: list[dict[str, Any]] = []

    for row in trades:
        fam = family_name(row)
        apply_trade(family_buckets[fam], row)
        if fam == "UNKNOWN":
            unknown_rows.append(row)

    finalized = {family: finalize_bucket(bucket) for family, bucket in sorted(family_buckets.items())}

    known_family_trades = sum(data["trade_count"] for fam, data in finalized.items() if fam != "UNKNOWN")
    unknown_family_trades = finalized.get("UNKNOWN", {}).get("trade_count", 0)
    known_family_count = sum(1 for fam, data in finalized.items() if fam != "UNKNOWN" and data["trade_count"] > 0)
    rank_candidate_family_count = sum(1 for fam, data in finalized.items() if fam != "UNKNOWN" and data["trade_count"] >= 3)

    ranked = [
        {"family": fam, **data}
        for fam, data in finalized.items()
        if fam != "UNKNOWN" and data["trade_count"] > 0
    ]
    ranked.sort(key=lambda x: (x["net_pnl_after_costs"], x["expectancy"], x["trade_count"]), reverse=True)

    best_family = ranked[0] if ranked else None
    worst_family = ranked[-1] if ranked else None

    source_counter: Counter[str] = Counter()
    parent_counter: Counter[str] = Counter()
    producer_counter: Counter[str] = Counter()
    gap_rows: list[dict[str, Any]] = []

    for idx, row in enumerate(unknown_rows, start=1):
        source_artifact = norm(row.get("source_artifact"))
        parent = source_parent(source_artifact)
        producer = infer_likely_producer(source_artifact, row)

        source_counter[source_artifact or "UNKNOWN_SOURCE"] += 1
        parent_counter[parent or "UNKNOWN_PARENT"] += 1
        producer_counter[producer] += 1

        gap_rows.append({
            "unknown_trade_index": idx,
            "source_artifact": source_artifact,
            "source_parent": parent,
            "likely_producer": producer,
            "source_run_id": norm(row.get("source_run_id")),
            "artifact_kind": norm(row.get("artifact_kind")),
            "row_kind": norm(row.get("row_kind")),
            "event_id": norm(row.get("event_id")),
            "candidate_id": norm(row.get("candidate_id")),
            "trade_id": norm(row.get("trade_id")),
            "decision_action": norm(row.get("decision_action")),
            "side": norm(row.get("side")),
            "strategy_id": norm(row.get("strategy_id")),
            "net_pnl_after_costs": pnl_value(row),
            "exit_reason": norm(row.get("exit_reason")),
            "raw_p_family_source": norm(row.get("raw_p_family_source")),
            "raw_q_family_source": norm(row.get("raw_q_family_source")),
            "suggested_fix": producer_fix_recommendation(producer),
        })

    return {
        "schema_version": RAW_R_SCHEMA_VERSION,
        "generated_utc": utc_now_iso(),
        "input_jsonl": input_jsonl,
        "row_count": len(rows),
        "trade_count": len(trades),
        "known_family_trade_count": known_family_trades,
        "unknown_family_trade_count": unknown_family_trades,
        "unknown_family_ratio": round(unknown_family_trades / max(len(trades), 1), 6),
        "known_family_count": known_family_count,
        "rank_candidate_family_count": rank_candidate_family_count,
        "family_pnl": finalized,
        "ranked_families": ranked,
        "best_family": best_family,
        "worst_family": worst_family,
        "unknown_trade_gap_rows": gap_rows,
        "unknown_source_counts": dict(source_counter.most_common()),
        "unknown_parent_counts": dict(parent_counter.most_common()),
        "likely_producer_counts": dict(producer_counter.most_common()),
        "review_verdict": review_verdict(len(trades), unknown_family_trades, rank_candidate_family_count),
        "promotion_allowed": False,
        "paper_live_allowed": False,
        "non_live": True,
        "non_mutating": True,
    }


def producer_fix_recommendation(producer: str) -> str:
    if "reports.py" in producer or "artifacts.py" in producer:
        return "Emit family, side, strategy_id into trade/candidate rows at artifact creation time."
    if "comparison_artifacts.py" in producer:
        return "Carry family, side, strategy_id through comparison artifact row model."
    if "metrics.py" in producer:
        return "Attach family/strategy labels before metric aggregation."
    if "runner.py" in producer or "engine.py" in producer:
        return "Propagate selected strategy_family/strategy_id/side from replay decision lifecycle into emitted trade row."
    if "proof" in producer:
        return "Patch proof harness to preserve family/side/strategy_id in generated trade evidence."
    return "Inspect source artifact and add family/side/strategy_id at producer boundary."


def review_verdict(trade_count: int, unknown_family_trade_count: int, rank_candidate_family_count: int) -> str:
    if trade_count <= 0:
        return "NO_TRADE_EVIDENCE"
    if rank_candidate_family_count >= 5 and unknown_family_trade_count == 0:
        return "FAMILY_RANKING_READY_FULL_COVERAGE"
    if rank_candidate_family_count >= 5:
        return "FAMILY_RANKING_READY_PARTIAL_COVERAGE"
    return "FAMILY_RANKING_NOT_READY_SOURCE_GAPS_REMAIN"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)


def write_gap_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "unknown_trade_index",
        "source_artifact",
        "source_parent",
        "likely_producer",
        "source_run_id",
        "artifact_kind",
        "row_kind",
        "event_id",
        "candidate_id",
        "trade_id",
        "decision_action",
        "side",
        "strategy_id",
        "net_pnl_after_costs",
        "exit_reason",
        "raw_p_family_source",
        "raw_q_family_source",
        "suggested_fix",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_summary_csv(path: Path, review: dict[str, Any]) -> None:
    rows: list[dict[str, Any]] = []
    for producer, count in review["likely_producer_counts"].items():
        rows.append({
            "summary_type": "likely_producer",
            "key": producer,
            "unknown_trade_count": count,
            "suggested_fix": producer_fix_recommendation(producer),
        })
    for source, count in review["unknown_source_counts"].items():
        rows.append({
            "summary_type": "source_artifact",
            "key": source,
            "unknown_trade_count": count,
            "suggested_fix": "",
        })
    fieldnames = ["summary_type", "key", "unknown_trade_count", "suggested_fix"]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, review: dict[str, Any]) -> None:
    lines: list[str] = []
    lines.append("# RAW-R Family PnL and Producer-Source Gap Review")
    lines.append("")
    lines.append(f"Generated UTC: {utc_now_iso()}")
    lines.append("")
    lines.append("## Verdict")
    lines.append(f"- review_verdict: {review['review_verdict']}")
    lines.append(f"- promotion_allowed: {review['promotion_allowed']}")
    lines.append(f"- paper_live_allowed: {review['paper_live_allowed']}")
    lines.append("")
    lines.append("## Family PnL")
    for family, data in review["family_pnl"].items():
        lines.append(
            f"- {family}: trades={data['trade_count']}, net={data['net_pnl_after_costs']}, "
            f"expectancy={data['expectancy']}, win_rate={data['win_rate']}"
        )
    lines.append("")
    lines.append("## Coverage")
    lines.append(f"- trade_count: {review['trade_count']}")
    lines.append(f"- known_family_trade_count: {review['known_family_trade_count']}")
    lines.append(f"- unknown_family_trade_count: {review['unknown_family_trade_count']}")
    lines.append(f"- unknown_family_ratio: {review['unknown_family_ratio']}")
    lines.append(f"- rank_candidate_family_count: {review['rank_candidate_family_count']}")
    lines.append("")
    lines.append("## Likely producer gaps")
    for producer, count in review["likely_producer_counts"].items():
        lines.append(f"- {producer}: {count} unknown trades")
        lines.append(f"  - fix: {producer_fix_recommendation(producer)}")
    lines.append("")
    lines.append("## Governance")
    lines.append("RAW-R is review-only. It does not enable paper/live and does not mutate production.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_family_gap_review(
    *,
    input_jsonl: str | Path,
    output_dir: str | Path,
    run_id: str,
) -> dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    rows = read_jsonl(input_jsonl)
    review = build_review(rows, str(input_jsonl))

    family_pnl_path = out / FAMILY_PNL_REVIEW_JSON
    gap_csv_path = out / UNKNOWN_TRADE_GAP_CSV
    summary_csv_path = out / SOURCE_GAP_SUMMARY_CSV
    producer_gap_path = out / PRODUCER_GAP_JSON
    summary_md_path = out / SUMMARY_MD
    manifest_path = out / MANIFEST_JSON

    producer_gap = {
        "schema_version": RAW_R_SCHEMA_VERSION,
        "generated_utc": utc_now_iso(),
        "likely_producer_counts": review["likely_producer_counts"],
        "unknown_source_counts": review["unknown_source_counts"],
        "unknown_parent_counts": review["unknown_parent_counts"],
        "recommendations": [
            "Patch original replay trade/candidate producers to emit family/side/strategy_id at creation time.",
            "Do not rely on post-processing inference for promotion-grade evidence.",
            "Run larger replay-only validation before any paper/live discussion.",
        ],
        "promotion_allowed": False,
        "paper_live_allowed": False,
    }

    manifest = {
        "schema_version": RAW_R_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_utc": utc_now_iso(),
        "input_jsonl": str(input_jsonl),
        "artifacts": [
            FAMILY_PNL_REVIEW_JSON,
            UNKNOWN_TRADE_GAP_CSV,
            SOURCE_GAP_SUMMARY_CSV,
            PRODUCER_GAP_JSON,
            SUMMARY_MD,
        ],
        "review_verdict": review["review_verdict"],
        "promotion_allowed": False,
        "paper_live_allowed": False,
        "non_live": True,
        "non_mutating": True,
    }

    review_for_json = dict(review)
    gap_rows = review_for_json.pop("unknown_trade_gap_rows")

    write_json(family_pnl_path, review_for_json)
    write_gap_csv(gap_csv_path, gap_rows)
    write_summary_csv(summary_csv_path, review)
    write_json(producer_gap_path, producer_gap)
    write_markdown(summary_md_path, review)
    write_json(manifest_path, manifest)

    return {
        "run_id": run_id,
        "output_dir": str(out),
        "family_pnl_review": str(family_pnl_path),
        "unknown_trade_source_gap_map": str(gap_csv_path),
        "source_gap_summary": str(summary_csv_path),
        "producer_gap_review": str(producer_gap_path),
        "summary_md": str(summary_md_path),
        "manifest": str(manifest_path),
        "trade_count": review["trade_count"],
        "known_family_trade_count": review["known_family_trade_count"],
        "unknown_family_trade_count": review["unknown_family_trade_count"],
        "unknown_family_ratio": review["unknown_family_ratio"],
        "rank_candidate_family_count": review["rank_candidate_family_count"],
        "review_verdict": review["review_verdict"],
        "best_family": review["best_family"],
        "worst_family": review["worst_family"],
        "likely_producer_counts": review["likely_producer_counts"],
        "promotion_allowed": False,
        "paper_live_allowed": False,
        "non_live": True,
        "non_mutating": True,
        "broker_io_added": False,
        "redis_live_writer_added": False,
        "order_sending_added": False,
    }
