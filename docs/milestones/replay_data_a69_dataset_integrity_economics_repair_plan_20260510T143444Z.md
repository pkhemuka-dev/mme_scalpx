# REPLAY-DATA-A69 dataset integrity + economics readiness repair plan

{
  "a68_blockers": [
    "full-system/economics readiness blocked: integrity_verdict is fail; prior stale-leg stem-equivalence waiver is acceptable for execution-shadow audit only, not for full-system/economics promotion",
    "economics/readiness blocked: ml_export_eligible is False",
    "economics readiness blocked: feature_economics_valid_true_count is zero/null",
    "economics readiness blocked: strategy_economics_valid_true_count is zero/null",
    "economics readiness blocked: risk_economics_valid_true_count is zero/null",
    "full-system readiness blocked: candidate_count is zero; no entry lifecycle exercised",
    "full-system/economics readiness blocked: trade_count is zero",
    "full-system/economics readiness blocked: execution_shadow_filled_count is zero"
  ],
  "allowed_next_actions": [
    "A70 dataset declaration + stem-alias contract audit only",
    "A71 economics field availability audit only",
    "A72 candidate/trade/fill dataset discovery audit only"
  ],
  "batch": "REPLAY-DATA-A69",
  "blocker_count": 0,
  "blockers": [],
  "broker_calls_executed": false,
  "classification": "REPAIR_PLAN_ONLY_FULL_SYSTEM_ECONOMICS_REMAIN_BLOCKED",
  "command_executed": false,
  "economics_pnl_evaluation_allowed": false,
  "economics_pnl_evaluation_authorized": false,
  "economics_preview_generated": false,
  "forbidden_next_actions": [
    "do not run full_system_replay",
    "do not run economics/PnL evaluation",
    "do not start services",
    "do not call broker APIs",
    "do not write live Redis",
    "do not enable paper/live",
    "do not send orders"
  ],
  "full_engine_replay_allowed": false,
  "full_system_execution_authorized": false,
  "full_system_preview_generated": false,
  "live_redis_writes_executed": false,
  "live_trading_approved": false,
  "new_replay_execution_started": false,
  "next_batch": "REPLAY-DATA-A70 dataset declaration + stem-alias contract audit only",
  "orders_sent": false,
  "paper_armed_approved": false,
  "paper_or_live_enabled": false,
  "readiness_repair_plan_only": true,
  "repair_plan": [
    {
      "allowed_work": [
        "audit-only inspection of dataset declaration/profile files",
        "contract-only proposal for stem equivalence mapping",
        "no replay execution"
      ],
      "blocked_until_done": [
        "full_system_replay",
        "economics_pnl_evaluation"
      ],
      "evidence": {
        "integrity_verdict": "fail",
        "stale_leg_alias_issue": "fut_ticks/opt_ticks vs quote_ticks_mme_fut_stream/quote_ticks_mme_opt_stream"
      },
      "purpose": "Convert the known stale-leg naming mismatch into an explicit dataset profile contract before any full-system/economics gate.",
      "repair_id": "A69-RP1",
      "title": "Freeze dataset stem-alias policy for replay integrity"
    },
    {
      "allowed_work": [
        "artifact audit",
        "dataset declaration audit",
        "schema/readiness report"
      ],
      "blocked_until_done": [
        "economics_pnl_evaluation",
        "ML export eligibility promotion"
      ],
      "evidence": {
        "execution_shadow_filled_count": 0,
        "feature_economics_valid_true_count": 0,
        "pnl_total": null,
        "risk_economics_valid_true_count": 0,
        "strategy_economics_valid_true_count": 0,
        "trade_count": 0
      },
      "minimum_required_truth": [
        "economics_valid true counts must be non-zero or explicitly declared not evaluable",
        "entry/fill/exit lifecycle must be present for PnL, or PnL must remain blocked",
        "dataset declaration must state quote-only vs economics-evaluable clearly"
      ],
      "purpose": "Identify what fields/artifacts must exist before economics/PnL can be evaluated.",
      "repair_id": "A69-RP2",
      "title": "Define economics eligibility requirements"
    },
    {
      "allowed_work": [
        "search/audit for alternate datasets with candidates/fills",
        "no execution until dataset is admitted"
      ],
      "blocked_until_done": [
        "full_system_replay",
        "economics_pnl_evaluation"
      ],
      "evidence": {
        "candidate_count": 0,
        "execution_shadow_filled_count": 0,
        "trade_count": 0
      },
      "minimum_required_truth": [
        "candidate_count > 0 for setup lifecycle testing",
        "execution_shadow_filled_count > 0 for fill/PnL testing",
        "trade_count > 0 or explicit no-trade economics classification"
      ],
      "purpose": "Prevent full-system/economics promotion on a HOLD-only replay that never exercised entry lifecycle.",
      "repair_id": "A69-RP3",
      "title": "Establish candidate/trade/fill readiness requirement"
    }
  ],
  "source_a68": "run/proofs/proof_replay_data_a68_full_system_economics_readiness_audit_20260510T143258Z.json",
  "verdict": "PASS_A69_REPAIR_PLAN_FROZEN_NO_EXECUTION",
  "warning_count": 0,
  "warnings": []
}
