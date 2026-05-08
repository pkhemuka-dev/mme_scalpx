"""Replay/backtest verdict desk for RAW / Research Gate.

RAW-I consolidates RAW-D/E/F/G/H evidence into a replay/backtest research verdict.

It does not run live trading, does not send orders, does not call brokers, does not write
Redis, does not mutate replay/research_capture/strategy/risk/execution, and does not
enable paper/live. It is a non-live verdict layer only.
"""

from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .contracts import ARTIFACT_MANIFEST, ARTIFACT_REPLAY_BACKTEST_VERDICT
from .writer import write_json_file, write_text_file


REPLAY_VERDICT_SCHEMA_VERSION = "RAW-I.1"

VERDICT_REJECT_NEGATIVE_EXPECTANCY_DIAGNOSTIC = "REJECT_NEGATIVE_EXPECTANCY_DIAGNOSTIC"
VERDICT_INCONCLUSIVE_FOR_PROMOTION = "INCONCLUSIVE_FOR_PROMOTION"
VERDICT_NOT_READY_MISSING_LABELS = "NOT_READY_MISSING_LABELS"
VERDICT_RESEARCH_ONLY_DIAGNOSTIC = "RESEARCH_ONLY_DIAGNOSTIC"
VERDICT_READY_FOR_LARGER_REPLAY_ONLY = "READY_FOR_LARGER_REPLAY_ONLY"

RESEARCH_VERDICT_NOT_READY_FOR_PAPER = "NOT_READY_FOR_PAPER_OR_LIVE"
RESEARCH_VERDICT_RESEARCH_ONLY = "RESEARCH_ONLY"
RESEARCH_VERDICT_NEEDS_ENRICHMENT = "NEEDS_REPLAY_ARTIFACT_ENRICHMENT"

EVIDENCE_SCORECARD_CSV = "replay_evidence_scorecard.csv"
SUMMARY_MD = "RAW_I_REPLAY_BACKTEST_VERDICT_SUMMARY.md"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    payload = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {p}")
    return payload


def _safe_float(value: Any, default: float = 0.0) -> float:
    if value is None or isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).strip().replace(",", ""))
    except Exception:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except Exception:
        return default


def _score_yes_no(ok: bool) -> float:
    return 1.0 if ok else 0.0


def build_replay_backtest_verdict(
    *,
    run_id: str,
    raw_d_proof_path: str | Path,
    raw_e_proof_path: str | Path,
    raw_f_proof_path: str | Path,
    raw_g_proof_path: str | Path,
    raw_h_proof_path: str | Path,
    source_label: str = "current_project",
) -> dict[str, Any]:
    raw_d = _load_json(raw_d_proof_path)
    raw_e = _load_json(raw_e_proof_path)
    raw_f = _load_json(raw_f_proof_path)
    raw_g = _load_json(raw_g_proof_path)
    raw_h = _load_json(raw_h_proof_path)

    dataset_quality_score = _safe_float(raw_d.get("data_quality_score"))
    dataset_verdict = str(raw_d.get("dataset_quality_verdict") or "")
    pnl_verdict = str(raw_e.get("pnl_verdict") or "")
    rank_verdict = str(raw_f.get("rank_verdict") or "")
    oi_verdict = str(raw_g.get("oi_verdict") or "")
    forensics_verdict = str(raw_h.get("forensics_verdict") or "")

    trade_count = _safe_int(raw_e.get("trade_count"))
    net_pnl = _safe_float(raw_e.get("net_pnl_after_costs"))
    profit_factor = raw_e.get("profit_factor")
    expectancy = _safe_float(raw_e.get("expectancy"))
    max_drawdown = _safe_float(raw_e.get("max_drawdown"))
    unknown_family_ratio = _safe_float(raw_f.get("unknown_family_ratio_in_sample"), 1.0)
    oi_context_record_count = _safe_int(raw_g.get("oi_context_record_count"))
    oi_pnl_linked_count = _safe_int(raw_g.get("pnl_linked_count"))
    forensics_record_count = _safe_int(raw_h.get("record_count"))
    unknown_outcome_rate = _safe_float(raw_h.get("unknown_outcome_rate"), 1.0)

    evidence_flags = {
        "dataset_pass": dataset_verdict == "DATASET_PASS" and dataset_quality_score >= 0.90,
        "pnl_positive": net_pnl > 0 and trade_count > 0,
        "pnl_negative": net_pnl < 0 and trade_count > 0,
        "family_labels_sufficient": unknown_family_ratio < 0.25 and "INSUFFICIENT" not in rank_verdict,
        "oi_evidence_linked": oi_context_record_count > 0 and oi_pnl_linked_count > 0,
        "oi_evidence_positive": str(oi_verdict).endswith("POSITIVE"),
        "forensics_labels_sufficient": unknown_outcome_rate < 0.50 and "NO_OUTCOME_LABELS" not in forensics_verdict,
        "paper_live_forbidden": True,
    }

    evidence_scorecard = [
        {
            "metric": "dataset_quality",
            "score": round(dataset_quality_score, 4),
            "verdict": dataset_verdict,
            "weight": 0.20,
        },
        {
            "metric": "pnl_edge",
            "score": _score_yes_no(evidence_flags["pnl_positive"]),
            "verdict": pnl_verdict,
            "weight": 0.25,
        },
        {
            "metric": "family_label_quality",
            "score": round(max(0.0, 1.0 - unknown_family_ratio), 4),
            "verdict": rank_verdict,
            "weight": 0.15,
        },
        {
            "metric": "oi_pnl_linkage",
            "score": _score_yes_no(evidence_flags["oi_evidence_linked"]),
            "verdict": oi_verdict,
            "weight": 0.15,
        },
        {
            "metric": "forensics_outcome_label_quality",
            "score": round(max(0.0, 1.0 - unknown_outcome_rate), 4),
            "verdict": forensics_verdict,
            "weight": 0.15,
        },
        {
            "metric": "paper_live_safety",
            "score": 1.0,
            "verdict": "RAW_NON_LIVE_NON_MUTATING",
            "weight": 0.10,
        },
    ]

    weighted_score = round(
        sum(float(item["score"]) * float(item["weight"]) for item in evidence_scorecard),
        6,
    )

    blocking_reasons: list[str] = []
    recommendations: list[str] = []

    if not evidence_flags["dataset_pass"]:
        blocking_reasons.append("Dataset quality is not PASS.")
    if evidence_flags["pnl_negative"]:
        blocking_reasons.append("RAW-E PnL is negative.")
    if trade_count <= 0:
        blocking_reasons.append("No trade evidence available.")
    if not evidence_flags["family_labels_sufficient"]:
        blocking_reasons.append("Family labels are insufficient or UNKNOWN-heavy.")
    if not evidence_flags["forensics_labels_sufficient"]:
        blocking_reasons.append("False-entry / missed-trade / good-blocker outcome labels are insufficient.")
    if not evidence_flags["oi_evidence_linked"]:
        blocking_reasons.append("OI context lacks sufficient PnL linkage.")
    elif not evidence_flags["oi_evidence_positive"]:
        blocking_reasons.append("OI-linked evidence is not positive.")

    recommendations.extend([
        "Do not promote this evidence to paper/live.",
        "Enrich replay/trade artifacts with family, strategy_id, side, regime, provider_mode, and source_run_id.",
        "Add explicit closed-trade truth and distinguish candidate rows from executed trades.",
        "Add blocker outcome labels: good_blocker, missed_trade, false_entry, target_hit_after_block, stop_hit_after_block, hypothetical_pnl_after_block.",
        "Add OI-wall state at candidate/trade time and preserve slow-context vs trigger-truth separation.",
        "Run a larger replay batch after enrichment, then rerun RAW-D through RAW-I.",
    ])

    if evidence_flags["pnl_negative"]:
        replay_verdict = VERDICT_REJECT_NEGATIVE_EXPECTANCY_DIAGNOSTIC
        research_verdict = RESEARCH_VERDICT_NOT_READY_FOR_PAPER
    elif not evidence_flags["family_labels_sufficient"] or not evidence_flags["forensics_labels_sufficient"]:
        replay_verdict = VERDICT_NOT_READY_MISSING_LABELS
        research_verdict = RESEARCH_VERDICT_NEEDS_ENRICHMENT
    elif not evidence_flags["oi_evidence_linked"]:
        replay_verdict = VERDICT_INCONCLUSIVE_FOR_PROMOTION
        research_verdict = RESEARCH_VERDICT_NEEDS_ENRICHMENT
    elif evidence_flags["dataset_pass"] and evidence_flags["pnl_positive"]:
        replay_verdict = VERDICT_READY_FOR_LARGER_REPLAY_ONLY
        research_verdict = RESEARCH_VERDICT_RESEARCH_ONLY
        blocking_reasons.append("Not paper/live ready until larger replay and promotion firewall batches pass.")
    else:
        replay_verdict = VERDICT_RESEARCH_ONLY_DIAGNOSTIC
        research_verdict = RESEARCH_VERDICT_RESEARCH_ONLY

    return {
        "schema_version": REPLAY_VERDICT_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_utc": utc_now_iso(),
        "source_label": source_label,
        "non_live": True,
        "non_mutating": True,
        "replay_engine_execution_included": False,
        "broker_io_included": False,
        "redis_live_write_included": False,
        "order_sending_included": False,
        "production_mutation_included": False,
        "paper_live_enablement_included": False,
        "replay_verdict": replay_verdict,
        "research_verdict": research_verdict,
        "promotion_allowed": False,
        "paper_live_allowed": False,
        "weighted_evidence_score": weighted_score,
        "evidence_flags": evidence_flags,
        "evidence_scorecard": evidence_scorecard,
        "blocking_reasons": blocking_reasons,
        "recommendations": recommendations,
        "raw_d_dataset_quality": {
            "dataset_verdict": dataset_verdict,
            "data_quality_score": dataset_quality_score,
            "proof": str(raw_d_proof_path),
        },
        "raw_e_pnl": {
            "pnl_verdict": pnl_verdict,
            "trade_count": trade_count,
            "net_pnl_after_costs": net_pnl,
            "profit_factor": profit_factor,
            "expectancy": expectancy,
            "max_drawdown": max_drawdown,
            "proof": str(raw_e_proof_path),
        },
        "raw_f_strategy_ranking": {
            "rank_verdict": rank_verdict,
            "unknown_family_ratio_in_sample": unknown_family_ratio,
            "best_family": raw_f.get("best_family"),
            "worst_family": raw_f.get("worst_family"),
            "best_side": raw_f.get("best_side"),
            "worst_side": raw_f.get("worst_side"),
            "proof": str(raw_f_proof_path),
        },
        "raw_g_oi_wall": {
            "oi_verdict": oi_verdict,
            "oi_context_record_count": oi_context_record_count,
            "pnl_linked_count": oi_pnl_linked_count,
            "net_pnl_after_costs": raw_g.get("net_pnl_after_costs"),
            "proof": str(raw_g_proof_path),
        },
        "raw_h_forensics": {
            "forensics_verdict": forensics_verdict,
            "record_count": forensics_record_count,
            "false_entry_count": raw_h.get("false_entry_count"),
            "missed_trade_count": raw_h.get("missed_trade_count"),
            "good_blocker_count": raw_h.get("good_blocker_count"),
            "unknown_outcome_rate": unknown_outcome_rate,
            "proof": str(raw_h_proof_path),
        },
        "remarks": [
            "RAW-I consolidates RAW desk outputs into a non-live replay/backtest verdict.",
            "RAW-I does not execute replay engine code.",
            "RAW-I does not approve paper/live.",
            "Negative PnL or missing labels blocks promotion.",
        ],
    }


def build_manifest_for_report(*, run_id: str, report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": REPLAY_VERDICT_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_utc": utc_now_iso(),
        "non_live": True,
        "non_mutating": True,
        "artifacts": [
            {"path": ARTIFACT_MANIFEST, "artifact_type": "raw_manifest"},
            {"path": ARTIFACT_REPLAY_BACKTEST_VERDICT, "artifact_type": "replay_backtest_verdict"},
            {"path": EVIDENCE_SCORECARD_CSV, "artifact_type": "replay_evidence_scorecard"},
            {"path": SUMMARY_MD, "artifact_type": "replay_verdict_summary"},
        ],
        "replay_verdict": report["replay_verdict"],
        "research_verdict": report["research_verdict"],
        "promotion_allowed": report["promotion_allowed"],
        "paper_live_allowed": report["paper_live_allowed"],
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
    lines = [
        "# RAW-I Replay / Backtest Verdict Summary",
        "",
        f"Run ID: {report['run_id']}",
        f"Generated UTC: {report['generated_utc']}",
        "",
        "## Verdict",
        "",
        f"- replay_verdict: {report['replay_verdict']}",
        f"- research_verdict: {report['research_verdict']}",
        f"- promotion_allowed: {report['promotion_allowed']}",
        f"- paper_live_allowed: {report['paper_live_allowed']}",
        f"- weighted_evidence_score: {report['weighted_evidence_score']}",
        "",
        "## Evidence summary",
        "",
        f"- dataset_verdict: {report['raw_d_dataset_quality']['dataset_verdict']}",
        f"- data_quality_score: {report['raw_d_dataset_quality']['data_quality_score']}",
        f"- pnl_verdict: {report['raw_e_pnl']['pnl_verdict']}",
        f"- trade_count: {report['raw_e_pnl']['trade_count']}",
        f"- net_pnl_after_costs: {report['raw_e_pnl']['net_pnl_after_costs']}",
        f"- rank_verdict: {report['raw_f_strategy_ranking']['rank_verdict']}",
        f"- unknown_family_ratio: {report['raw_f_strategy_ranking']['unknown_family_ratio_in_sample']}",
        f"- oi_verdict: {report['raw_g_oi_wall']['oi_verdict']}",
        f"- oi_pnl_linked_count: {report['raw_g_oi_wall']['pnl_linked_count']}",
        f"- forensics_verdict: {report['raw_h_forensics']['forensics_verdict']}",
        f"- unknown_outcome_rate: {report['raw_h_forensics']['unknown_outcome_rate']}",
        "",
        "## Blocking reasons",
        "",
    ]
    if report["blocking_reasons"]:
        lines.extend(f"- {item}" for item in report["blocking_reasons"])
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
        f"- replay_engine_execution_included: {report['replay_engine_execution_included']}",
        f"- broker_io_included: {report['broker_io_included']}",
        f"- redis_live_write_included: {report['redis_live_write_included']}",
        f"- order_sending_included: {report['order_sending_included']}",
        f"- production_mutation_included: {report['production_mutation_included']}",
        f"- paper_live_enablement_included: {report['paper_live_enablement_included']}",
        "",
    ])
    return "\n".join(lines)


def write_replay_verdict_bundle(
    *,
    output_dir: str | Path,
    run_id: str,
    raw_d_proof_path: str | Path,
    raw_e_proof_path: str | Path,
    raw_f_proof_path: str | Path,
    raw_g_proof_path: str | Path,
    raw_h_proof_path: str | Path,
    source_label: str = "current_project",
) -> dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    report = build_replay_backtest_verdict(
        run_id=run_id,
        raw_d_proof_path=raw_d_proof_path,
        raw_e_proof_path=raw_e_proof_path,
        raw_f_proof_path=raw_f_proof_path,
        raw_g_proof_path=raw_g_proof_path,
        raw_h_proof_path=raw_h_proof_path,
        source_label=source_label,
    )
    manifest = build_manifest_for_report(run_id=run_id, report=report)
    summary = render_summary_markdown(report)

    write_json_file(out / ARTIFACT_REPLAY_BACKTEST_VERDICT, report)
    write_json_file(out / ARTIFACT_MANIFEST, manifest)
    write_text_file(out / SUMMARY_MD, summary)
    _write_csv(
        out / EVIDENCE_SCORECARD_CSV,
        report["evidence_scorecard"],
        ["metric", "score", "verdict", "weight"],
    )

    return {
        "output_dir": str(out),
        "manifest": str(out / ARTIFACT_MANIFEST),
        "replay_backtest_verdict": str(out / ARTIFACT_REPLAY_BACKTEST_VERDICT),
        "evidence_scorecard_csv": str(out / EVIDENCE_SCORECARD_CSV),
        "summary_markdown": str(out / SUMMARY_MD),
        "replay_verdict": report["replay_verdict"],
        "research_verdict": report["research_verdict"],
        "promotion_allowed": report["promotion_allowed"],
        "paper_live_allowed": report["paper_live_allowed"],
        "weighted_evidence_score": report["weighted_evidence_score"],
        "blocking_reason_count": len(report["blocking_reasons"]),
    }
