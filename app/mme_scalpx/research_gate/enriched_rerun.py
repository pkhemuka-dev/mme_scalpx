"""RAW-N enriched-evidence rerun.

Reruns RAW-D through RAW-J style analysis against RAW-M enriched replay records.
This writes an isolated RAW-N evidence bundle and does not overwrite old RAW-D/J proofs.

No broker IO. No Redis IO. No orders. No strategy/risk/execution mutation. No paper/live.
"""

from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RAW_N_SCHEMA_VERSION = "RAW-N.1"

DATASET_REPORT = "raw_n_d_dataset_quality_report.json"
PNL_REPORT = "raw_n_e_pnl_report.json"
RANK_REPORT = "raw_n_f_strategy_ranking_report.json"
OI_REPORT = "raw_n_g_oi_wall_report.json"
FORENSICS_REPORT = "raw_n_h_forensics_report.json"
REPLAY_VERDICT_REPORT = "raw_n_i_replay_backtest_verdict.json"
PROMOTION_REPORT = "raw_n_j_promotion_firewall.json"
COMPARISON_REPORT = "raw_n_old_vs_enriched_comparison.json"
SUMMARY_MD = "RAW_N_ENRICHED_RERUN_SUMMARY.md"
MANIFEST_JSON = "manifest.json"
SCORECARD_CSV = "raw_n_evidence_scorecard.csv"

REQUIRED_FIELDS = (
    "run_id",
    "source_run_id",
    "artifact_kind",
    "row_kind",
    "event_id",
    "event_ts",
    "family",
    "strategy_id",
    "side",
    "regime",
    "provider_mode",
    "candidate_id",
    "candidate_state",
    "candidate_vs_executed",
    "decision_action",
    "blocker",
    "blocker_chain",
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
    "false_entry",
    "missed_trade",
    "good_blocker",
    "target_hit_after_block",
    "stop_hit_after_block",
    "hypothetical_pnl_after_block",
    "oi_wall_state",
    "oi_wall_distance_points",
    "oi_wall_strength",
    "strike_score",
    "selected_strike",
    "selected_strike_source",
    "source_artifact",
    "source_row_index",
    "schema_version",
    "created_by",
    "remarks",
)

UNKNOWN = "UNKNOWN"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_float(value: Any, default: float | None = None) -> float | None:
    if value is None or isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "")
    if not text or text.upper() == UNKNOWN:
        return default
    try:
        return float(text)
    except ValueError:
        return default


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


def is_unknown(value: Any) -> bool:
    return value in (None, "", UNKNOWN, "NO_BLOCKER") or str(value).strip().upper() == UNKNOWN


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    p = Path(path)
    rows: list[dict[str, Any]] = []
    with p.open("r", encoding="utf-8", errors="replace") as f:
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


def trade_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for row in rows:
        closed = safe_bool(row.get("closed_trade_truth"))
        executed = str(row.get("candidate_vs_executed") or "").upper() == "EXECUTED"
        row_kind = str(row.get("row_kind") or "").lower()
        net = safe_float(row.get("net_pnl_after_costs"))
        if closed is True or (executed and net is not None) or (row_kind == "trade" and net is not None):
            selected.append(row)
    return selected


def pnl_value(row: dict[str, Any]) -> float:
    net = safe_float(row.get("net_pnl_after_costs"))
    if net is not None:
        return float(net)
    gross = safe_float(row.get("gross_pnl"))
    costs = safe_float(row.get("costs"), 0.0) or 0.0
    if gross is not None:
        return float(gross) - costs
    return 0.0


def bucket_template() -> dict[str, Any]:
    return {
        "trade_count": 0,
        "gross_pnl": 0.0,
        "net_pnl_after_costs": 0.0,
        "winning_trades": 0,
        "losing_trades": 0,
        "flat_trades": 0,
        "_gross_profit": 0.0,
        "_gross_loss": 0.0,
    }


def apply_trade(bucket: dict[str, Any], row: dict[str, Any]) -> None:
    pnl = pnl_value(row)
    gross = safe_float(row.get("gross_pnl"), pnl) or pnl
    bucket["trade_count"] += 1
    bucket["gross_pnl"] += gross
    bucket["net_pnl_after_costs"] += pnl
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
    bucket["gross_pnl"] = round(float(bucket["gross_pnl"]), 6)
    bucket["net_pnl_after_costs"] = round(net, 6)
    bucket["expectancy"] = round(net / count, 6) if count else 0.0
    bucket["win_rate"] = round(float(bucket["winning_trades"]) / count, 6) if count else 0.0
    if gross_loss > 0:
        bucket["profit_factor"] = round(gross_profit / gross_loss, 6)
    elif gross_profit > 0:
        bucket["profit_factor"] = None
    else:
        bucket["profit_factor"] = 0.0
    return bucket


def aggregate_by(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for row in rows:
        name = str(row.get(key) or UNKNOWN)
        bucket = out.setdefault(name, bucket_template())
        apply_trade(bucket, row)
    return {k: finalize_bucket(v) for k, v in sorted(out.items())}


def build_dataset_report(rows: list[dict[str, Any]], enriched_path: str) -> dict[str, Any]:
    total = len(rows)
    missing_counts = {field: 0 for field in REQUIRED_FIELDS}
    complete_rows = 0
    parseable_pnl_rows = 0

    for row in rows:
        missing = [field for field in REQUIRED_FIELDS if field not in row]
        if not missing:
            complete_rows += 1
        for field in missing:
            missing_counts[field] += 1
        if safe_float(row.get("net_pnl_after_costs")) is not None or safe_float(row.get("gross_pnl")) is not None:
            parseable_pnl_rows += 1

    quality_score = round(complete_rows / max(total, 1), 6)
    return {
        "schema_version": RAW_N_SCHEMA_VERSION,
        "report_type": "RAW-N-D-dataset-quality",
        "generated_utc": utc_now_iso(),
        "enriched_input": enriched_path,
        "row_count": total,
        "complete_required_field_rows": complete_rows,
        "required_field_count": len(REQUIRED_FIELDS),
        "data_quality_score": quality_score,
        "parseable_pnl_rows": parseable_pnl_rows,
        "missing_counts": missing_counts,
        "dataset_verdict": "DATASET_PASS" if total > 0 and quality_score >= 0.99 else "DATASET_FAIL_OR_INCOMPLETE",
        "research_verdict": "RESEARCH_ONLY_FINDING",
        "non_live": True,
        "non_mutating": True,
    }


def build_pnl_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    trades = trade_rows(rows)
    total = bucket_template()
    for row in trades:
        apply_trade(total, row)
    total = finalize_bucket(total)
    verdict = "PNL_PASS_POSITIVE" if total["net_pnl_after_costs"] > 0 else "PNL_REJECT_NEGATIVE" if total["trade_count"] > 0 else "PNL_INSUFFICIENT_TRADES"
    research_verdict = "RESEARCH_ONLY_POSITIVE" if total["net_pnl_after_costs"] > 0 else "REJECT_NEGATIVE_EXPECTANCY" if total["trade_count"] > 0 else "INCONCLUSIVE_DATA_INSUFFICIENT"
    return {
        "schema_version": RAW_N_SCHEMA_VERSION,
        "report_type": "RAW-N-E-pnl",
        "generated_utc": utc_now_iso(),
        "pnl_verdict": verdict,
        "research_verdict": research_verdict,
        "summary": total,
        "trade_count": total["trade_count"],
        "net_pnl_after_costs": total["net_pnl_after_costs"],
        "expectancy": total["expectancy"],
        "profit_factor": total["profit_factor"],
        "by_family": aggregate_by(trades, "family"),
        "by_side": aggregate_by(trades, "side"),
        "by_regime": aggregate_by(trades, "regime"),
        "by_provider_mode": aggregate_by(trades, "provider_mode"),
        "trade_records_sample": trades[:100],
        "non_live": True,
        "non_mutating": True,
    }


def build_rank_report(rows: list[dict[str, Any]], pnl_report: dict[str, Any]) -> dict[str, Any]:
    trades = trade_rows(rows)
    unknown_family = sum(1 for row in trades if is_unknown(row.get("family")))
    unknown_ratio = round(unknown_family / max(len(trades), 1), 6)
    by_family = pnl_report["by_family"]
    labeled = [
        (family, data)
        for family, data in by_family.items()
        if family != UNKNOWN and int(data.get("trade_count", 0)) >= 3
    ]
    labeled.sort(key=lambda x: (float(x[1].get("net_pnl_after_costs", 0.0)), float(x[1].get("expectancy", 0.0))), reverse=True)

    if not trades:
        rank_verdict = "RANK_INSUFFICIENT_TRADE_EVIDENCE"
        research_verdict = "INCONCLUSIVE_DATA_INSUFFICIENT"
    elif not labeled:
        rank_verdict = "RANK_INSUFFICIENT_FAMILY_LABELS"
        research_verdict = "INCONCLUSIVE_DATA_INSUFFICIENT"
    else:
        rank_verdict = "RANK_AVAILABLE_FOR_RESEARCH"
        research_verdict = "RESEARCH_ONLY_FINDING"

    best_family = {"family": labeled[0][0], **labeled[0][1]} if labeled else None
    worst_family = {"family": labeled[-1][0], **labeled[-1][1]} if labeled else None

    return {
        "schema_version": RAW_N_SCHEMA_VERSION,
        "report_type": "RAW-N-F-strategy-ranking",
        "generated_utc": utc_now_iso(),
        "rank_verdict": rank_verdict,
        "research_verdict": research_verdict,
        "unknown_family_ratio_in_sample": unknown_ratio,
        "best_family": best_family,
        "worst_family": worst_family,
        "family_rank": by_family,
        "side_rank": pnl_report["by_side"],
        "regime_rank": pnl_report["by_regime"],
        "provider_mode_rank": pnl_report["by_provider_mode"],
        "non_live": True,
        "non_mutating": True,
    }


def build_oi_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    trades = trade_rows(rows)
    trade_ids = {id(row) for row in trades}
    oi_rows = [
        row for row in rows
        if not is_unknown(row.get("oi_wall_state"))
        or safe_float(row.get("oi_wall_distance_points")) is not None
        or safe_float(row.get("oi_wall_strength")) is not None
        or safe_float(row.get("strike_score")) is not None
    ]
    linked = [row for row in oi_rows if id(row) in trade_ids]
    total = bucket_template()
    for row in linked:
        apply_trade(total, row)
    total = finalize_bucket(total)

    if not oi_rows:
        verdict = "OI_IMPACT_INSUFFICIENT_OI_EVIDENCE"
        research = "INCONCLUSIVE_DATA_INSUFFICIENT"
    elif not linked:
        verdict = "OI_CONTEXT_FOUND_NO_PNL_LINKAGE"
        research = "RESEARCH_ONLY_FINDING"
    elif total["net_pnl_after_costs"] > 0:
        verdict = "OI_IMPACT_RESEARCH_POSITIVE"
        research = "RESEARCH_ONLY_FINDING"
    elif total["net_pnl_after_costs"] < 0:
        verdict = "OI_IMPACT_RESEARCH_NEGATIVE"
        research = "REJECT_NEGATIVE_EXPECTANCY"
    else:
        verdict = "OI_IMPACT_RESEARCH_MIXED"
        research = "RESEARCH_ONLY_FINDING"

    return {
        "schema_version": RAW_N_SCHEMA_VERSION,
        "report_type": "RAW-N-G-oi-wall",
        "generated_utc": utc_now_iso(),
        "oi_verdict": verdict,
        "research_verdict": research,
        "oi_context_record_count": len(oi_rows),
        "pnl_linked_count": len(linked),
        "summary": total,
        "net_pnl_after_costs": total["net_pnl_after_costs"],
        "by_wall_state": aggregate_by(linked, "oi_wall_state"),
        "sample": oi_rows[:80],
        "oi_wall_trigger_truth_allowed": False,
        "non_live": True,
        "non_mutating": True,
    }


def build_forensics_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    false_entries = [row for row in rows if safe_bool(row.get("false_entry")) is True]
    missed = [row for row in rows if safe_bool(row.get("missed_trade")) is True]
    good_blockers = [row for row in rows if safe_bool(row.get("good_blocker")) is True]
    blocked = [row for row in rows if not is_unknown(row.get("blocker"))]
    entered = [row for row in rows if str(row.get("candidate_vs_executed") or "").upper() == "EXECUTED"]
    outcome_labeled = len(false_entries) + len(missed) + len(good_blockers)
    unknown_outcome_rate = round(1.0 - (outcome_labeled / max(len(rows), 1)), 6)

    if not rows:
        verdict = "FORENSICS_INSUFFICIENT_EVIDENCE"
        research = "INCONCLUSIVE_DATA_INSUFFICIENT"
    elif outcome_labeled == 0:
        verdict = "FORENSICS_CONTEXT_FOUND_NO_OUTCOME_LABELS"
        research = "RESEARCH_ONLY_FINDING"
    else:
        verdict = "FORENSICS_RESEARCH_FINDINGS"
        research = "RESEARCH_ONLY_FINDING"

    return {
        "schema_version": RAW_N_SCHEMA_VERSION,
        "report_type": "RAW-N-H-forensics",
        "generated_utc": utc_now_iso(),
        "forensics_verdict": verdict,
        "research_verdict": research,
        "record_count": len(rows),
        "blocked_count": len(blocked),
        "entered_count": len(entered),
        "false_entry_count": len(false_entries),
        "missed_trade_count": len(missed),
        "good_blocker_count": len(good_blockers),
        "unknown_outcome_rate": unknown_outcome_rate,
        "non_live": True,
        "non_mutating": True,
    }


def build_replay_verdict(dataset: dict[str, Any], pnl: dict[str, Any], rank: dict[str, Any], oi: dict[str, Any], forensics: dict[str, Any]) -> dict[str, Any]:
    blocking: list[str] = []
    if dataset["dataset_verdict"] != "DATASET_PASS":
        blocking.append("Enriched dataset quality is not PASS.")
    if pnl["net_pnl_after_costs"] < 0:
        blocking.append("Enriched PnL is negative.")
    if pnl["trade_count"] <= 0:
        blocking.append("No enriched closed-trade evidence.")
    if rank["rank_verdict"] != "RANK_AVAILABLE_FOR_RESEARCH":
        blocking.append("Enriched family labels are still insufficient for ranking.")
    if oi["oi_verdict"] != "OI_IMPACT_RESEARCH_POSITIVE":
        blocking.append("Enriched OI-linked evidence is not positive.")
    if forensics["forensics_verdict"] == "FORENSICS_CONTEXT_FOUND_NO_OUTCOME_LABELS":
        blocking.append("Enriched blocker outcome labels are still insufficient.")

    if pnl["net_pnl_after_costs"] < 0:
        replay_verdict = "REJECT_NEGATIVE_EXPECTANCY_DIAGNOSTIC"
        research_verdict = "NOT_READY_FOR_PAPER_OR_LIVE"
    elif blocking:
        replay_verdict = "INCONCLUSIVE_FOR_PROMOTION"
        research_verdict = "NEEDS_MORE_ENRICHED_REPLAY_EVIDENCE"
    else:
        replay_verdict = "READY_FOR_LARGER_REPLAY_ONLY"
        research_verdict = "RESEARCH_ONLY"

    scorecard = [
        {"metric": "dataset_quality", "score": dataset["data_quality_score"], "verdict": dataset["dataset_verdict"], "weight": 0.20},
        {"metric": "pnl_edge", "score": 1.0 if pnl["net_pnl_after_costs"] > 0 else 0.0, "verdict": pnl["pnl_verdict"], "weight": 0.25},
        {"metric": "family_label_quality", "score": max(0.0, 1.0 - rank["unknown_family_ratio_in_sample"]), "verdict": rank["rank_verdict"], "weight": 0.15},
        {"metric": "oi_pnl_linkage", "score": 1.0 if oi["pnl_linked_count"] > 0 else 0.0, "verdict": oi["oi_verdict"], "weight": 0.15},
        {"metric": "forensics_label_quality", "score": max(0.0, 1.0 - forensics["unknown_outcome_rate"]), "verdict": forensics["forensics_verdict"], "weight": 0.15},
        {"metric": "paper_live_safety", "score": 1.0, "verdict": "RAW_NON_LIVE_NON_MUTATING", "weight": 0.10},
    ]
    weighted = round(sum(float(row["score"]) * float(row["weight"]) for row in scorecard), 6)

    return {
        "schema_version": RAW_N_SCHEMA_VERSION,
        "report_type": "RAW-N-I-replay-verdict",
        "generated_utc": utc_now_iso(),
        "replay_verdict": replay_verdict,
        "research_verdict": research_verdict,
        "weighted_evidence_score": weighted,
        "promotion_allowed": False,
        "paper_live_allowed": False,
        "blocking_reason_count": len(blocking),
        "blocking_reasons": blocking,
        "scorecard": scorecard,
        "recommendations": [
            "Do not enable paper/live from RAW-N output.",
            "If PnL remains negative, inspect enriched source artifacts for candidate/trade pollution.",
            "If family labels remain UNKNOWN, patch replay producers closer to strategy-family source fields.",
            "If outcome labels remain missing, add explicit replay post-outcome labeling logic.",
            "Run a larger controlled replay only after enriched labels are confirmed.",
        ],
        "non_live": True,
        "non_mutating": True,
    }


def build_promotion_firewall(replay_verdict: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": RAW_N_SCHEMA_VERSION,
        "report_type": "RAW-N-J-promotion-firewall",
        "generated_utc": utc_now_iso(),
        "promotion_verdict": "PROMOTION_REJECTED_BY_EVIDENCE" if replay_verdict["blocking_reasons"] else "PROMOTION_BLOCKED_PENDING_MANUAL_GOVERNANCE",
        "promotion_allowed": False,
        "paper_live_allowed": False,
        "live_allowed": False,
        "production_patch_allowed": False,
        "strategy_mutation_allowed": False,
        "config_mutation_allowed": False,
        "order_sending_allowed": False,
        "risk_override_allowed": False,
        "execution_override_allowed": False,
        "hard_blocker_count": replay_verdict["blocking_reason_count"],
        "hard_blockers": replay_verdict["blocking_reasons"],
        "action_plan": replay_verdict["recommendations"],
        "non_live": True,
        "non_mutating": True,
    }


def build_comparison(old_raw_j: dict[str, Any], old_raw_m: dict[str, Any], dataset: dict[str, Any], pnl: dict[str, Any], rank: dict[str, Any], oi: dict[str, Any], forensics: dict[str, Any], replay: dict[str, Any], promotion: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": RAW_N_SCHEMA_VERSION,
        "report_type": "RAW-N-old-vs-enriched-comparison",
        "generated_utc": utc_now_iso(),
        "old_raw_j_promotion_verdict": old_raw_j.get("promotion_verdict_value"),
        "old_raw_j_hard_blockers": old_raw_j.get("hard_blockers"),
        "old_raw_m_total_enriched_rows": old_raw_m.get("total_enriched_rows"),
        "enriched_dataset_quality_score": dataset["data_quality_score"],
        "enriched_trade_count": pnl["trade_count"],
        "enriched_net_pnl_after_costs": pnl["net_pnl_after_costs"],
        "enriched_unknown_family_ratio": rank["unknown_family_ratio_in_sample"],
        "enriched_oi_pnl_linked_count": oi["pnl_linked_count"],
        "enriched_unknown_outcome_rate": forensics["unknown_outcome_rate"],
        "enriched_replay_verdict": replay["replay_verdict"],
        "enriched_promotion_verdict": promotion["promotion_verdict"],
        "promotion_allowed": promotion["promotion_allowed"],
        "paper_live_allowed": promotion["paper_live_allowed"],
        "non_live": True,
        "non_mutating": True,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)


def write_scorecard_csv(path: Path, scorecard: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "score", "verdict", "weight"])
        writer.writeheader()
        writer.writerows(scorecard)


def write_summary(path: Path, replay: dict[str, Any], promotion: dict[str, Any], comparison: dict[str, Any]) -> None:
    lines = [
        "# RAW-N Enriched Rerun Summary",
        "",
        f"Generated UTC: {utc_now_iso()}",
        "",
        "## Verdict",
        f"- replay_verdict: {replay['replay_verdict']}",
        f"- research_verdict: {replay['research_verdict']}",
        f"- promotion_verdict: {promotion['promotion_verdict']}",
        f"- promotion_allowed: {promotion['promotion_allowed']}",
        f"- paper_live_allowed: {promotion['paper_live_allowed']}",
        "",
        "## Enriched evidence",
        f"- enriched_trade_count: {comparison['enriched_trade_count']}",
        f"- enriched_net_pnl_after_costs: {comparison['enriched_net_pnl_after_costs']}",
        f"- enriched_unknown_family_ratio: {comparison['enriched_unknown_family_ratio']}",
        f"- enriched_oi_pnl_linked_count: {comparison['enriched_oi_pnl_linked_count']}",
        f"- enriched_unknown_outcome_rate: {comparison['enriched_unknown_outcome_rate']}",
        "",
        "## Blocking reasons",
    ]
    if replay["blocking_reasons"]:
        lines.extend(f"- {item}" for item in replay["blocking_reasons"])
    else:
        lines.append("- none")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_enriched_rerun(
    *,
    enriched_jsonl: str | Path,
    output_dir: str | Path,
    run_id: str,
    old_raw_j_proof: str | Path | None = None,
    old_raw_m_proof: str | Path | None = None,
) -> dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    enriched_path = Path(enriched_jsonl)

    rows = read_jsonl(enriched_path)
    old_j = json.loads(Path(old_raw_j_proof).read_text(encoding="utf-8")) if old_raw_j_proof else {}
    old_m = json.loads(Path(old_raw_m_proof).read_text(encoding="utf-8")) if old_raw_m_proof else {}

    dataset = build_dataset_report(rows, str(enriched_path))
    pnl = build_pnl_report(rows)
    rank = build_rank_report(rows, pnl)
    oi = build_oi_report(rows)
    forensics = build_forensics_report(rows)
    replay = build_replay_verdict(dataset, pnl, rank, oi, forensics)
    promotion = build_promotion_firewall(replay)
    comparison = build_comparison(old_j, old_m, dataset, pnl, rank, oi, forensics, replay, promotion)

    outputs = {
        DATASET_REPORT: dataset,
        PNL_REPORT: pnl,
        RANK_REPORT: rank,
        OI_REPORT: oi,
        FORENSICS_REPORT: forensics,
        REPLAY_VERDICT_REPORT: replay,
        PROMOTION_REPORT: promotion,
        COMPARISON_REPORT: comparison,
    }
    for name, payload in outputs.items():
        write_json(out / name, payload)

    write_scorecard_csv(out / SCORECARD_CSV, replay["scorecard"])
    write_summary(out / SUMMARY_MD, replay, promotion, comparison)

    manifest = {
        "schema_version": RAW_N_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_utc": utc_now_iso(),
        "enriched_jsonl": str(enriched_path),
        "artifacts": list(outputs.keys()) + [SCORECARD_CSV, SUMMARY_MD],
        "replay_verdict": replay["replay_verdict"],
        "promotion_verdict": promotion["promotion_verdict"],
        "promotion_allowed": promotion["promotion_allowed"],
        "paper_live_allowed": promotion["paper_live_allowed"],
        "non_live": True,
        "non_mutating": True,
    }
    write_json(out / MANIFEST_JSON, manifest)

    return {
        "run_id": run_id,
        "output_dir": str(out),
        "manifest": str(out / MANIFEST_JSON),
        "dataset_report": str(out / DATASET_REPORT),
        "pnl_report": str(out / PNL_REPORT),
        "rank_report": str(out / RANK_REPORT),
        "oi_report": str(out / OI_REPORT),
        "forensics_report": str(out / FORENSICS_REPORT),
        "replay_verdict_report": str(out / REPLAY_VERDICT_REPORT),
        "promotion_report": str(out / PROMOTION_REPORT),
        "comparison_report": str(out / COMPARISON_REPORT),
        "scorecard_csv": str(out / SCORECARD_CSV),
        "summary_md": str(out / SUMMARY_MD),
        "row_count": len(rows),
        "trade_count": pnl["trade_count"],
        "net_pnl_after_costs": pnl["net_pnl_after_costs"],
        "dataset_verdict": dataset["dataset_verdict"],
        "pnl_verdict": pnl["pnl_verdict"],
        "rank_verdict": rank["rank_verdict"],
        "oi_verdict": oi["oi_verdict"],
        "forensics_verdict": forensics["forensics_verdict"],
        "replay_verdict": replay["replay_verdict"],
        "promotion_verdict": promotion["promotion_verdict"],
        "promotion_allowed": promotion["promotion_allowed"],
        "paper_live_allowed": promotion["paper_live_allowed"],
        "blocking_reason_count": replay["blocking_reason_count"],
        "blocking_reasons": replay["blocking_reasons"],
        "non_live": True,
        "non_mutating": True,
        "broker_io_added": False,
        "redis_live_writer_added": False,
        "order_sending_added": False,
        "paper_live_enablement_added": False,
    }
