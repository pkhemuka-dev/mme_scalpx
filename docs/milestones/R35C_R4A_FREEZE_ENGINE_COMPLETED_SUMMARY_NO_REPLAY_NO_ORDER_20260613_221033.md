# R35C_R4A_FREEZE_ENGINE_COMPLETED_SUMMARY_NO_REPLAY_NO_ORDER_20260613_221033

classification: PASS_R35C_R4A_ENGINE_COMPLETED_SUMMARY_FROZEN_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35C_R4A_FREEZE_ENGINE_COMPLETED_SUMMARY_NO_REPLAY_NO_ORDER_20260613_221033.json`
recovered_summary: `run/audits/R35C_R4A_FREEZE_ENGINE_COMPLETED_SUMMARY_NO_REPLAY_NO_ORDER_20260613_221033/r4a_recovered_engine_summary.json`

recover_rc=0
safety pre=0/0/0 post=0/0/0 proc=0/0 replay_proc=0

## Recovered summary
{
  "engine_finished_at": "2026-06-13T16:33:53Z",
  "engine_started_at": "2026-06-13T16:31:39Z",
  "execution_shadow_filled_count": 4222,
  "execution_shadow_row_count": 131368,
  "feature_row_count": 131368,
  "feeds_total_injected": 131368,
  "fill_model_name": "immediate_market",
  "final_state": "completed",
  "important_limitation": "Recovered from engine_result.json because official 10_run_summary.json was missing.",
  "paper_order": false,
  "real_order": false,
  "risk_action_breakdown": {
    "ENTER_CALL": 2033,
    "ENTER_PUT": 2189,
    "HOLD": 127146
  },
  "risk_row_count": 131368,
  "run_id": "replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8",
  "schema_version": "r35c_r4a_recovered_engine_summary_v1",
  "source_engine_result": "run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/artifacts/engine_result.json",
  "stage_count": 5,
  "strategy_action_breakdown": {
    "ENTRY": 4222,
    "HOLD": 127146
  },
  "strategy_candidate_true_count": 4222,
  "strategy_row_count": 131368
}
## Recover errors
