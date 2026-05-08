"""Promotion firewall for RAW / Research Gate.

RAW-J converts RAW-I evidence into a strict promotion verdict.

This module never enables paper/live, never mutates strategy/config, never calls brokers,
never writes Redis, never sends orders, and never overrides risk/execution.
"""

from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .contracts import ARTIFACT_MANIFEST, ARTIFACT_PROMOTION_VERDICT
from .writer import write_json_file, write_text_file


PROMOTION_SCHEMA_VERSION = "RAW-J.1"

PROMOTION_REJECTED_BY_EVIDENCE = "PROMOTION_REJECTED_BY_EVIDENCE"
PROMOTION_BLOCKED_PENDING_ENRICHMENT = "PROMOTION_BLOCKED_PENDING_REPLAY_ARTIFACT_ENRICHMENT"
PROMOTION_RESEARCH_ONLY_NO_ACTION = "PROMOTION_RESEARCH_ONLY_NO_ACTION"
PROMOTION_PROPOSAL_ONLY_AFTER_FURTHER_REPLAY = "PROMOTION_PROPOSAL_ONLY_AFTER_FURTHER_REPLAY"

PROMOTION_BLOCKERS_CSV = "promotion_blockers.csv"
PROMOTION_ACTION_PLAN_CSV = "promotion_action_plan.csv"
SUMMARY_MD = "RAW_J_PROMOTION_FIREWALL_SUMMARY.md"

FORBIDDEN_PROMOTION_OUTPUTS = (
    "ENABLE_LIVE",
    "ENABLE_PAPER_ARMED",
    "SEND_ORDER",
    "MUTATE_CONFIG_NOW",
    "OVERRIDE_RISK",
    "OVERRIDE_EXECUTION",
)

REQUIRED_ENRICHMENT_ACTIONS = (
    "Add family, strategy_id, side, regime, provider_mode, and source_run_id to replay/trade artifacts.",
    "Add explicit closed-trade truth and separate candidate rows from executed trades.",
    "Add blocker outcome labels: good_blocker, missed_trade, false_entry, target_hit_after_block, stop_hit_after_block, hypothetical_pnl_after_block.",
    "Add OI-wall state at candidate/trade time while preserving slow-context versus trigger-truth separation.",
    "Run larger replay batch after enrichment.",
    "Rerun RAW-D through RAW-J before any paper/live proposal.",
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    payload = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {p}")
    return payload


def _truthy(value: Any) -> bool:
    return bool(value is True or str(value).strip().lower() == "true")


def build_promotion_verdict(
    *,
    run_id: str,
    raw_i_proof_path: str | Path,
    source_label: str = "current_project",
) -> dict[str, Any]:
    raw_i = _load_json(raw_i_proof_path)

    replay_verdict = str(raw_i.get("replay_verdict") or "")
    research_verdict = str(raw_i.get("research_verdict") or "")
    weighted_score = raw_i.get("weighted_evidence_score")
    blocking_reasons = list(raw_i.get("blocking_reasons") or [])
    recommendations = list(raw_i.get("recommendations") or [])
    raw_i_promotion_allowed = _truthy(raw_i.get("promotion_allowed"))
    raw_i_paper_live_allowed = _truthy(raw_i.get("paper_live_allowed"))

    hard_blockers: list[str] = []
    hard_blockers.extend(blocking_reasons)

    if raw_i_promotion_allowed:
        hard_blockers.append("RAW-I unexpectedly allowed promotion; RAW-J requires manual governance review.")
    if raw_i_paper_live_allowed:
        hard_blockers.append("RAW-I unexpectedly allowed paper/live; RAW-J blocks direct enablement.")

    if "NEGATIVE" in replay_verdict or "NOT_READY" in replay_verdict or "REJECT" in replay_verdict:
        promotion_verdict = PROMOTION_REJECTED_BY_EVIDENCE
    elif hard_blockers:
        promotion_verdict = PROMOTION_BLOCKED_PENDING_ENRICHMENT
    elif research_verdict in {"RESEARCH_ONLY", "NEEDS_REPLAY_ARTIFACT_ENRICHMENT"}:
        promotion_verdict = PROMOTION_RESEARCH_ONLY_NO_ACTION
    else:
        promotion_verdict = PROMOTION_PROPOSAL_ONLY_AFTER_FURTHER_REPLAY
        hard_blockers.append("Further replay and explicit promotion review required before any paper/live proposal.")

    # RAW-J is a firewall: these remain false under all verdicts.
    promotion_allowed = False
    paper_live_allowed = False
    live_allowed = False
    production_patch_allowed = False
    strategy_mutation_allowed = False
    config_mutation_allowed = False
    order_sending_allowed = False
    risk_override_allowed = False
    execution_override_allowed = False

    action_plan = []
    for idx, item in enumerate(REQUIRED_ENRICHMENT_ACTIONS, start=1):
        action_plan.append({
            "priority": idx,
            "action": item,
            "required_before_promotion": True,
        })

    for item in recommendations:
        if item and item not in [x["action"] for x in action_plan]:
            action_plan.append({
                "priority": len(action_plan) + 1,
                "action": item,
                "required_before_promotion": True,
            })

    verdict = {
        "schema_version": PROMOTION_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_utc": utc_now_iso(),
        "source_label": source_label,
        "non_live": True,
        "non_mutating": True,
        "broker_io_included": False,
        "redis_live_write_included": False,
        "order_sending_included": False,
        "risk_override_included": False,
        "execution_override_included": False,
        "strategy_mutation_included": False,
        "production_config_mutation_included": False,
        "paper_live_enablement_included": False,
        "promotion_firewall_included": True,
        "raw_i_proof_path": str(raw_i_proof_path),
        "raw_i_replay_verdict": replay_verdict,
        "raw_i_research_verdict": research_verdict,
        "raw_i_weighted_evidence_score": weighted_score,
        "promotion_verdict": promotion_verdict,
        "promotion_allowed": promotion_allowed,
        "paper_live_allowed": paper_live_allowed,
        "live_allowed": live_allowed,
        "production_patch_allowed": production_patch_allowed,
        "strategy_mutation_allowed": strategy_mutation_allowed,
        "config_mutation_allowed": config_mutation_allowed,
        "order_sending_allowed": order_sending_allowed,
        "risk_override_allowed": risk_override_allowed,
        "execution_override_allowed": execution_override_allowed,
        "hard_blocker_count": len(hard_blockers),
        "hard_blockers": hard_blockers,
        "action_plan": action_plan,
        "forbidden_outputs": list(FORBIDDEN_PROMOTION_OUTPUTS),
        "remarks": [
            "RAW-J is a promotion firewall, not a promotion engine.",
            "Current evidence is blocked from paper/live.",
            "No production patch is allowed directly from RAW output.",
            "Manual patch + proof + freeze governance remains mandatory.",
        ],
    }

    for key in (
        "promotion_allowed",
        "paper_live_allowed",
        "live_allowed",
        "production_patch_allowed",
        "strategy_mutation_allowed",
        "config_mutation_allowed",
        "order_sending_allowed",
        "risk_override_allowed",
        "execution_override_allowed",
    ):
        if verdict[key] is not False:
            raise ValueError(f"RAW-J firewall invariant failed: {key}")

    return verdict


def build_manifest_for_report(*, run_id: str, report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": PROMOTION_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_utc": utc_now_iso(),
        "non_live": True,
        "non_mutating": True,
        "artifacts": [
            {"path": ARTIFACT_MANIFEST, "artifact_type": "raw_manifest"},
            {"path": ARTIFACT_PROMOTION_VERDICT, "artifact_type": "promotion_verdict"},
            {"path": PROMOTION_BLOCKERS_CSV, "artifact_type": "promotion_blockers"},
            {"path": PROMOTION_ACTION_PLAN_CSV, "artifact_type": "promotion_action_plan"},
            {"path": SUMMARY_MD, "artifact_type": "promotion_firewall_summary"},
        ],
        "promotion_verdict": report["promotion_verdict"],
        "promotion_allowed": report["promotion_allowed"],
        "paper_live_allowed": report["paper_live_allowed"],
        "production_patch_allowed": report["production_patch_allowed"],
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
        "# RAW-J Promotion Firewall Summary",
        "",
        f"Run ID: {report['run_id']}",
        f"Generated UTC: {report['generated_utc']}",
        "",
        "## Verdict",
        "",
        f"- promotion_verdict: {report['promotion_verdict']}",
        f"- raw_i_replay_verdict: {report['raw_i_replay_verdict']}",
        f"- raw_i_research_verdict: {report['raw_i_research_verdict']}",
        f"- raw_i_weighted_evidence_score: {report['raw_i_weighted_evidence_score']}",
        "",
        "## Firewall decisions",
        "",
        f"- promotion_allowed: {report['promotion_allowed']}",
        f"- paper_live_allowed: {report['paper_live_allowed']}",
        f"- live_allowed: {report['live_allowed']}",
        f"- production_patch_allowed: {report['production_patch_allowed']}",
        f"- strategy_mutation_allowed: {report['strategy_mutation_allowed']}",
        f"- config_mutation_allowed: {report['config_mutation_allowed']}",
        f"- order_sending_allowed: {report['order_sending_allowed']}",
        "",
        "## Hard blockers",
        "",
    ]
    if report["hard_blockers"]:
        lines.extend(f"- {item}" for item in report["hard_blockers"])
    else:
        lines.append("- none")
    lines.extend(["", "## Required action plan", ""])
    for item in report["action_plan"]:
        lines.append(f"- P{item['priority']}: {item['action']}")
    lines.extend([
        "",
        "## Boundary confirmation",
        "",
        f"- non_live: {report['non_live']}",
        f"- non_mutating: {report['non_mutating']}",
        f"- broker_io_included: {report['broker_io_included']}",
        f"- redis_live_write_included: {report['redis_live_write_included']}",
        f"- order_sending_included: {report['order_sending_included']}",
        f"- risk_override_included: {report['risk_override_included']}",
        f"- execution_override_included: {report['execution_override_included']}",
        f"- strategy_mutation_included: {report['strategy_mutation_included']}",
        f"- production_config_mutation_included: {report['production_config_mutation_included']}",
        f"- paper_live_enablement_included: {report['paper_live_enablement_included']}",
        "",
    ])
    return "\n".join(lines)


def write_promotion_verdict_bundle(
    *,
    output_dir: str | Path,
    run_id: str,
    raw_i_proof_path: str | Path,
    source_label: str = "current_project",
) -> dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    report = build_promotion_verdict(
        run_id=run_id,
        raw_i_proof_path=raw_i_proof_path,
        source_label=source_label,
    )
    manifest = build_manifest_for_report(run_id=run_id, report=report)
    summary = render_summary_markdown(report)

    write_json_file(out / ARTIFACT_PROMOTION_VERDICT, report)
    write_json_file(out / ARTIFACT_MANIFEST, manifest)
    write_text_file(out / SUMMARY_MD, summary)

    blocker_rows = [
        {"index": idx, "blocker": blocker}
        for idx, blocker in enumerate(report["hard_blockers"], start=1)
    ]
    _write_csv(out / PROMOTION_BLOCKERS_CSV, blocker_rows, ["index", "blocker"])

    _write_csv(
        out / PROMOTION_ACTION_PLAN_CSV,
        report["action_plan"],
        ["priority", "action", "required_before_promotion"],
    )

    return {
        "output_dir": str(out),
        "manifest": str(out / ARTIFACT_MANIFEST),
        "promotion_verdict": str(out / ARTIFACT_PROMOTION_VERDICT),
        "promotion_blockers_csv": str(out / PROMOTION_BLOCKERS_CSV),
        "promotion_action_plan_csv": str(out / PROMOTION_ACTION_PLAN_CSV),
        "summary_markdown": str(out / SUMMARY_MD),
        "promotion_verdict_value": report["promotion_verdict"],
        "promotion_allowed": report["promotion_allowed"],
        "paper_live_allowed": report["paper_live_allowed"],
        "live_allowed": report["live_allowed"],
        "production_patch_allowed": report["production_patch_allowed"],
        "hard_blocker_count": report["hard_blocker_count"],
    }
