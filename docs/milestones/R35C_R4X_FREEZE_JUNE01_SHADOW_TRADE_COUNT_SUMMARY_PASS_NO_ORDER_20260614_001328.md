# R35C_R4X_FREEZE_JUNE01_SHADOW_TRADE_COUNT_SUMMARY_PASS_NO_ORDER_20260614_001328

classification: PASS_R35C_R4X_JUNE01_SHADOW_TRADE_COUNT_SUMMARY_FROZEN_NO_ORDER
proof: `run/proofs/R35C_R4X_FREEZE_JUNE01_SHADOW_TRADE_COUNT_SUMMARY_PASS_NO_ORDER_20260614_001328.json`

root: `run/replay/r35c_r4x/20260614_000314`
run_dir: `run/replay/r35c_r4x/20260614_000314/replay_locked_single_day_r35c_r4x_20260601_20260613_183322_0860a772`
summary: `run/replay/r35c_r4x/20260614_000314/replay_locked_single_day_r35c_r4x_20260601_20260613_183322_0860a772/artifacts/10_run_summary.json`
summary_csv: `run/replay/r35c_r4x/20260614_000314/replay_locked_single_day_r35c_r4x_20260601_20260613_183322_0860a772/artifacts/11_run_summary.csv`
engine: `run/replay/r35c_r4x/20260614_000314/replay_locked_single_day_r35c_r4x_20260601_20260613_183322_0860a772/artifacts/engine_result.json`

summary_ok=1 summary_csv_ok=1 engine_ok=1
big_files_over_50mb=0
trade_count=4222 shadow_trade_count=4222 execution_shadow_filled_count=4222 pnl_status_present=1
safety pre=0/0/0 post=0/0/0 proc=0/0 replay_proc=0

## Summary freeze check
{
  "dataset_id": "r35c_r4x",
  "execution_shadow_filled_count": 4222,
  "execution_shadow_row_count": 131368,
  "integrity_verdict": "fail",
  "loss_count": 0,
  "pnl_accounting_status": "PNL_NOT_COMPUTED_EXECUTION_SHADOW_HAS_ENTRY_FILL_ONLY_NO_EXIT_MODEL_R35C_R4W",
  "pnl_total": null,
  "risk_action_breakdown": {
    "ENTER_CALL": 2033,
    "ENTER_PUT": 2189,
    "HOLD": 127146
  },
  "shadow_filled_qty_total": 4222,
  "shadow_trade_count": 4222,
  "strategy_action_breakdown": {
    "ENTRY": 4222,
    "HOLD": 127146
  },
  "trade_count": 4222,
  "win_count": 0
}

## Largest files
550470 run/replay/r35c_r4x/20260614_000314/replay_locked_single_day_r35c_r4x_20260601_20260613_183322_0860a772/artifacts/features_rows.json
159822 run/replay/r35c_r4x/20260614_000314/replay_locked_single_day_r35c_r4x_20260601_20260613_183322_0860a772/artifacts/strategy_decisions.json
75930 run/replay/r35c_r4x/20260614_000314/replay_locked_single_day_r35c_r4x_20260601_20260613_183322_0860a772/artifacts/risk_outputs.json
33961 run/replay/r35c_r4x/20260614_000314/replay_locked_single_day_r35c_r4x_20260601_20260613_183322_0860a772/artifacts/execution_shadow_results.json
12627 run/replay/r35c_r4x/20260614_000314/replay_locked_single_day_r35c_r4x_20260601_20260613_183322_0860a772/02_scope_profile.json
10361 run/replay/r35c_r4x/20260614_000314/replay_locked_single_day_r35c_r4x_20260601_20260613_183322_0860a772/artifacts/economics_summary.json
7811 run/replay/r35c_r4x/20260614_000314/replay_locked_single_day_r35c_r4x_20260601_20260613_183322_0860a772/03_integrity_report.json
7642 run/replay/r35c_r4x/20260614_000314/replay_locked_single_day_r35c_r4x_20260601_20260613_183322_0860a772/01_dataset_summary.json
5043 run/replay/r35c_r4x/20260614_000314/replay_locked_single_day_r35c_r4x_20260601_20260613_183322_0860a772/artifacts/engine_result.json
3884 run/replay/r35c_r4x/20260614_000314/replay_locked_single_day_r35c_r4x_20260601_20260613_183322_0860a772/00_manifest.json
2675 run/replay/r35c_r4x/20260614_000314/replay_locked_single_day_r35c_r4x_20260601_20260613_183322_0860a772/artifacts/10_run_summary.json
2336 run/replay/r35c_r4x/20260614_000314/replay_locked_single_day_r35c_r4x_20260601_20260613_183322_0860a772/17_effective_inputs.json
967 run/replay/r35c_r4x/20260614_000314/replay_locked_single_day_r35c_r4x_20260601_20260613_183322_0860a772/artifacts/11_run_summary.csv
769 run/replay/r35c_r4x/20260614_000314/replay_locked_single_day_r35c_r4x_20260601_20260613_183322_0860a772/artifacts/b3_r32_analysis_exports_status.json
278 run/replay/r35c_r4x/20260614_000314/replay_locked_single_day_r35c_r4x_20260601_20260613_183322_0860a772/18_effective_overrides_flat.json
202 run/replay/r35c_r4x/20260614_000314/replay_locked_single_day_r35c_r4x_20260601_20260613_183322_0860a772/06_candidate_audit.csv
113 run/replay/r35c_r4x/20260614_000314/replay_locked_single_day_r35c_r4x_20260601_20260613_183322_0860a772/artifacts/blocker_distribution.csv
81 run/replay/r35c_r4x/20260614_000314/replay_locked_single_day_r35c_r4x_20260601_20260613_183322_0860a772/artifacts/family_side_summary.csv
59 run/replay/r35c_r4x/20260614_000314/replay_locked_single_day_r35c_r4x_20260601_20260613_183322_0860a772/04_metrics_summary.json
