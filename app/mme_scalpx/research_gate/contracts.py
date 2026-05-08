"""Frozen names and constants for RAW / Research Gate.

This module intentionally contains names/constants plus thin validation helpers only.
No broker IO, Redis IO, strategy logic, risk logic, execution logic, pandas, or replay engine code belongs here.
"""

from __future__ import annotations

RAW_PACKAGE_NAME = "research_gate"
RAW_CONTRACT_VERSION = "RAW-C.1"

EVIDENCE_TRACK_LIVE = "live_evidence_audit"
EVIDENCE_TRACK_REPLAY = "replay_evidence_audit"
EVIDENCE_TRACK_PARITY = "live_vs_replay_parity"

EVIDENCE_TRACKS = (
    EVIDENCE_TRACK_LIVE,
    EVIDENCE_TRACK_REPLAY,
    EVIDENCE_TRACK_PARITY,
)

ARTIFACT_MANIFEST = "manifest.json"
ARTIFACT_DATASET_QUALITY = "dataset_quality_report.json"
ARTIFACT_LIVE_PROVIDER_CONTEXT = "live_provider_context_report.json"
ARTIFACT_LIVE_FAMILY_SURFACE = "live_family_surface_report.json"
ARTIFACT_LIVE_SAFETY = "live_safety_report.json"
ARTIFACT_REPLAY_BACKTEST_VERDICT = "replay_backtest_verdict.json"
ARTIFACT_PNL_REPORT = "pnl_report.json"
ARTIFACT_STRATEGY_RANK = "strategy_rank_report.json"
ARTIFACT_OI_WALL_IMPACT = "oi_wall_impact_report.json"
ARTIFACT_BLOCKER_CHAIN = "blocker_chain_report.json"
ARTIFACT_MISSED_TRADE = "missed_trade_report.json"
ARTIFACT_FALSE_ENTRY = "false_entry_report.json"
ARTIFACT_PROMOTION_VERDICT = "promotion_verdict.json"
ARTIFACT_RAW_SUMMARY = "RAW_SUMMARY.md"

CORE_ARTIFACT_FILENAMES = (
    ARTIFACT_MANIFEST,
    ARTIFACT_DATASET_QUALITY,
    ARTIFACT_REPLAY_BACKTEST_VERDICT,
    ARTIFACT_PNL_REPORT,
    ARTIFACT_STRATEGY_RANK,
    ARTIFACT_OI_WALL_IMPACT,
    ARTIFACT_PROMOTION_VERDICT,
)

OPTIONAL_ARTIFACT_FILENAMES = (
    ARTIFACT_LIVE_PROVIDER_CONTEXT,
    ARTIFACT_LIVE_FAMILY_SURFACE,
    ARTIFACT_LIVE_SAFETY,
    ARTIFACT_BLOCKER_CHAIN,
    ARTIFACT_MISSED_TRADE,
    ARTIFACT_FALSE_ENTRY,
    ARTIFACT_RAW_SUMMARY,
)

VERDICT_RESEARCH_ONLY_FINDING = "RESEARCH_ONLY_FINDING"
VERDICT_PASS_WITH_POSITIVE_EDGE = "PASS_WITH_POSITIVE_EDGE"
VERDICT_PASS_BUT_LOW_SAMPLE = "PASS_BUT_LOW_SAMPLE"
VERDICT_PASS_BUT_HIGH_DRAWDOWN = "PASS_BUT_HIGH_DRAWDOWN"
VERDICT_PASS_ONLY_IN_ONE_REGIME = "PASS_ONLY_IN_ONE_REGIME"
VERDICT_REJECT_NEGATIVE_EXPECTANCY = "REJECT_NEGATIVE_EXPECTANCY"
VERDICT_REJECT_OVERFIT_RISK = "REJECT_OVERFIT_RISK"
VERDICT_INCONCLUSIVE_DATA_INSUFFICIENT = "INCONCLUSIVE_DATA_INSUFFICIENT"
VERDICT_READY_FOR_SHADOW_PAPER_PROPOSAL = "READY_FOR_SHADOW_PAPER_PROPOSAL"
VERDICT_READY_FOR_PAPER_TEST_PROPOSAL = "READY_FOR_PAPER_TEST_PROPOSAL"
VERDICT_PRODUCTION_PATCH_PROPOSAL_ONLY = "PRODUCTION_PATCH_PROPOSAL_ONLY"
VERDICT_INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
VERDICT_REJECTED_BY_EVIDENCE = "REJECTED_BY_EVIDENCE"

ALLOWED_RESEARCH_VERDICTS = (
    VERDICT_RESEARCH_ONLY_FINDING,
    VERDICT_PASS_WITH_POSITIVE_EDGE,
    VERDICT_PASS_BUT_LOW_SAMPLE,
    VERDICT_PASS_BUT_HIGH_DRAWDOWN,
    VERDICT_PASS_ONLY_IN_ONE_REGIME,
    VERDICT_REJECT_NEGATIVE_EXPECTANCY,
    VERDICT_REJECT_OVERFIT_RISK,
    VERDICT_INCONCLUSIVE_DATA_INSUFFICIENT,
    VERDICT_READY_FOR_SHADOW_PAPER_PROPOSAL,
    VERDICT_READY_FOR_PAPER_TEST_PROPOSAL,
    VERDICT_PRODUCTION_PATCH_PROPOSAL_ONLY,
    VERDICT_INSUFFICIENT_EVIDENCE,
    VERDICT_REJECTED_BY_EVIDENCE,
)

FORBIDDEN_RAW_VERDICTS = (
    "ENABLE_LIVE",
    "ENABLE_PAPER_ARMED",
    "SEND_ORDER",
    "MUTATE_CONFIG_NOW",
    "OVERRIDE_RISK",
    "OVERRIDE_EXECUTION",
)

RAW_FORBIDDEN_OWNERSHIP = (
    "live_entries",
    "live_exits",
    "broker_io",
    "order_placement",
    "position_truth",
    "risk_veto",
    "execution_routing",
    "live_redis_truth",
    "strategy_doctrine_mutation",
    "paper_live_enablement",
)

RAW_ALLOWED_INPUT_ROOT_HINTS = (
    "run/research_capture",
    "run/replay",
    "run/proofs",
    "run/live_capture",
)

RAW_ALLOWED_OUTPUT_ROOT = "run/research_gate"

RAW_POLICY_FILENAMES = (
    "raw_policy.json",
    "report_policy.json",
    "promotion_policy.json",
    "pnl_policy.json",
    "oi_wall_policy.json",
)


def is_allowed_research_verdict(value: str) -> bool:
    return value in ALLOWED_RESEARCH_VERDICTS


def is_forbidden_raw_verdict(value: str) -> bool:
    return value in FORBIDDEN_RAW_VERDICTS


def validate_research_verdict(value: str) -> str:
    if is_forbidden_raw_verdict(value):
        raise ValueError(f"forbidden RAW verdict: {value}")
    if not is_allowed_research_verdict(value):
        raise ValueError(f"unknown RAW research verdict: {value}")
    return value
