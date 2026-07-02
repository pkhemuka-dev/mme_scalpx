# R35C_R5D_JUNE01_VERIFY_SUMMARY_SYNTHETIC_PNL_AGGREGATION_NO_ORDER_20260614_003605

classification: PASS_R35C_R5D_JUNE01_SUMMARY_SYNTHETIC_PNL_AGGREGATION_VERIFIED_NO_ORDER
proof: `run/proofs/R35C_R5D_JUNE01_VERIFY_SUMMARY_SYNTHETIC_PNL_AGGREGATION_NO_ORDER_20260614_003605.json`
run_root: `run/replay/r35c_r5d/20260614_003605`

replay_rc=0
summary=run/replay/r35c_r5d/20260614_003605/replay_locked_single_day_r35c_r5d_20260601_20260613_190615_46090f86/artifacts/10_run_summary.json
summary_csv=run/replay/r35c_r5d/20260614_003605/replay_locked_single_day_r35c_r5d_20260601_20260613_190615_46090f86/artifacts/11_run_summary.csv
engine=run/replay/r35c_r5d/20260614_003605/replay_locked_single_day_r35c_r5d_20260601_20260613_190615_46090f86/artifacts/engine_result.json
execution=run/replay/r35c_r5d/20260614_003605/replay_locked_single_day_r35c_r5d_20260601_20260613_190615_46090f86/artifacts/execution_shadow_results.json
early_error=
safety_post=0/0/0 replay_proc=0
big_files_over_50mb=0
trade_count=4222 pnl_total=21110.0 shadow_pnl_total=21110.0 win_count=4222 computed_visible_rows_after_cap=4 pnl_status_present=1 pnl_model_present=5

## Summary PnL check
{
  "computed_visible_rows_after_cap": 4,
  "execution_visible_rows_after_cap": 50,
  "filled_visible_rows_after_cap": 4,
  "sample_computed": [
    {
      "cost_points": 0.0,
      "event_time": "2026-06-01T10:06:55Z",
      "execution_channel": "replay:execution_shadow",
      "execution_id": "execution_shadow_000014",
      "exit_price": 129.75,
      "exit_reason": "synthetic_first_target",
      "fill_price": 124.75,
      "fill_qty": 1,
      "filled": true,
      "gross_points": 5.0,
      "is_loss": false,
      "is_profit": true,
      "metadata": {
        "feature_truth_mode": "replay_bridge_v3_event_normalized",
        "r31a_r9f_r1_family_surface_enriched": true,
        "replay_feature_bridge_version": "v3_event_normalized_r31a_r9f_r1_enriched",
        "source_file": "quote_ticks_mme_opt_stream.csv",
        "source_stem": "quote_ticks_mme_opt_stream",
        "symbol": "NIFTY2660223550CE",
        "trading_day": "2026-06-01",
        "ts_event": "1780308415000000000"
      },
      "net_pnl": 5.0,
      "net_points": 5.0,
      "pnl_model": "R35C_R5A3_SYNTHETIC_FIRST_TARGET_REPLAY_ONLY",
      "pnl_model_status": "PNL_COMPUTED_SYNTHETIC_FIRST_TARGET_REPLAY_ONLY_R35C_R5A3",
      "reason": "immediate_market_fill",
      "risk_action": "ENTER_CALL",
      "slippage": 0.0,
      "source_risk_id": "risk_output_000014",
      "stop_points": 4.0,
      "symbol": "NIFTY2660223550CE",
      "target_points": 5.0
    },
    {
      "cost_points": 0.0,
      "event_time": "2026-06-01T10:06:55Z",
      "execution_channel": "replay:execution_shadow",
      "execution_id": "execution_shadow_000017",
      "exit_price": 74.1,
      "exit_reason": "synthetic_first_target",
      "fill_price": 69.1,
      "fill_qty": 1,
      "filled": true,
      "gross_points": 5.0,
      "is_loss": false,
      "is_profit": true,
      "metadata": {
        "feature_truth_mode": "replay_bridge_v3_event_normalized",
        "r31a_r9f_r1_family_surface_enriched": true,
        "replay_feature_bridge_version": "v3_event_normalized_r31a_r9f_r1_enriched",
        "source_file": "quote_ticks_mme_opt_stream.csv",
        "source_stem": "quote_ticks_mme_opt_stream",
        "symbol": "NIFTY2660223500PE",
        "trading_day": "2026-06-01",
        "ts_event": "1780308415000000000"
      },
      "net_pnl": 5.0,
      "net_points": 5.0,
      "pnl_model": "R35C_R5A3_SYNTHETIC_FIRST_TARGET_REPLAY_ONLY",
      "pnl_model_status": "PNL_COMPUTED_SYNTHETIC_FIRST_TARGET_REPLAY_ONLY_R35C_R5A3",
      "reason": "immediate_market_fill",
      "risk_action": "ENTER_PUT",
      "slippage": 0.0,
      "source_risk_id": "risk_output_000017",
      "stop_points": 4.0,
      "symbol": "NIFTY2660223500PE",
      "target_points": 5.0
    },
    {
      "cost_points": 0.0,
      "event_time": "2026-06-01T10:06:58Z",
      "execution_channel": "replay:execution_shadow",
      "execution_id": "execution_shadow_000033",
      "exit_price": 130.05,
      "exit_reason": "synthetic_first_target",
      "fill_price": 125.05,
      "fill_qty": 1,
      "filled": true,
      "gross_points": 5.0,
      "is_loss": false,
      "is_profit": true,
      "metadata": {
        "feature_truth_mode": "replay_bridge_v3_event_normalized",
        "r31a_r9f_r1_family_surface_enriched": true,
        "replay_feature_bridge_version": "v3_event_normalized_r31a_r9f_r1_enriched",
        "source_file": "quote_ticks_mme_opt_stream.csv",
        "source_stem": "quote_ticks_mme_opt_stream",
        "symbol": "NIFTY2660223550CE",
        "trading_day": "2026-06-01",
        "ts_event": "1780308418000000000"
      },
      "net_pnl": 5.0,
      "net_points": 5.0,
      "pnl_model": "R35C_R5A3_SYNTHETIC_FIRST_TARGET_REPLAY_ONLY",
      "pnl_model_status": "PNL_COMPUTED_SYNTHETIC_FIRST_TARGET_REPLAY_ONLY_R35C_R5A3",
      "reason": "immediate_market_fill",
      "risk_action": "ENTER_CALL",
      "slippage": 0.0,
      "source_risk_id": "risk_output_000033",
      "stop_points": 4.0,
      "symbol": "NIFTY2660223550CE",
      "target_points": 5.0
    },
    {
      "cost_points": 0.0,
      "event_time": "2026-06-01T10:06:59Z",
      "execution_channel": "replay:execution_shadow",
      "execution_id": "execution_shadow_000043",
      "exit_price": 73.6,
      "exit_reason": "synthetic_first_target",
      "fill_price": 68.6,
      "fill_qty": 1,
      "filled": true,
      "gross_points": 5.0,
      "is_loss": false,
      "is_profit": true,
      "metadata": {
        "feature_truth_mode": "replay_bridge_v3_event_normalized",
        "r31a_r9f_r1_family_surface_enriched": true,
        "replay_feature_bridge_version": "v3_event_normalized_r31a_r9f_r1_enriched",
        "source_file": "quote_ticks_mme_opt_stream.csv",
        "source_stem": "quote_ticks_mme_opt_stream",
        "symbol": "NIFTY2660223500PE",
        "trading_day": "2026-06-01",
        "ts_event": "1780308419000000000"
      },
      "net_pnl": 5.0,
      "net_points": 5.0,
      "pnl_model": "R35C_R5A3_SYNTHETIC_FIRST_TARGET_REPLAY_ONLY",
      "pnl_model_status": "PNL_COMPUTED_SYNTHETIC_FIRST_TARGET_REPLAY_ONLY_R35C_R5A3",
      "reason": "immediate_market_fill",
      "risk_action": "ENTER_PUT",
      "slippage": 0.0,
      "source_risk_id": "risk_output_000043",
      "stop_points": 4.0,
      "symbol": "NIFTY2660223500PE",
      "target_points": 5.0
    }
  ],
  "summary_selected": {
    "dataset_id": "r35c_r5d",
    "execution_shadow_filled_count": 4222,
    "execution_shadow_row_count": 131368,
    "integrity_verdict": "fail",
    "loss_count": 0,
    "pnl_accounting_status": "PNL_COMPUTED_REPLAY_ONLY_SYNTHETIC_SHADOW_MODEL_R35C_R5C_NOT_BROKER_NOT_PAPER_NOT_LIVE",
    "pnl_total": 21110.0,
    "risk_action_breakdown": {
      "ENTER_CALL": 2033,
      "ENTER_PUT": 2189,
      "HOLD": 127146
    },
    "shadow_filled_qty_total": 4222,
    "shadow_loss_count": 0,
    "shadow_pnl_model": "R35C_R5A3_SYNTHETIC_FIRST_TARGET_REPLAY_ONLY",
    "shadow_pnl_model_status_counts": {
      "PNL_COMPUTED_SYNTHETIC_FIRST_TARGET_REPLAY_ONLY_R35C_R5A3": 4222
    },
    "shadow_pnl_total": 21110.0,
    "shadow_trade_count": 4222,
    "shadow_win_count": 4222,
    "strategy_action_breakdown": {
      "ENTRY": 4222,
      "HOLD": 127146
    },
    "trade_count": 4222,
    "win_count": 4222
  },
  "visible_net_pnl_sum_after_cap": 20.0
}

## Summary PnL check errors

## Largest files
550470 run/replay/r35c_r5d/20260614_003605/replay_locked_single_day_r35c_r5d_20260601_20260613_190615_46090f86/artifacts/features_rows.json
159822 run/replay/r35c_r5d/20260614_003605/replay_locked_single_day_r35c_r5d_20260601_20260613_190615_46090f86/artifacts/strategy_decisions.json
75930 run/replay/r35c_r5d/20260614_003605/replay_locked_single_day_r35c_r5d_20260601_20260613_190615_46090f86/artifacts/risk_outputs.json
48273 run/replay/r35c_r5d/20260614_003605/replay_locked_single_day_r35c_r5d_20260601_20260613_190615_46090f86/artifacts/execution_shadow_results.json
12627 run/replay/r35c_r5d/20260614_003605/replay_locked_single_day_r35c_r5d_20260601_20260613_190615_46090f86/02_scope_profile.json
10361 run/replay/r35c_r5d/20260614_003605/replay_locked_single_day_r35c_r5d_20260601_20260613_190615_46090f86/artifacts/economics_summary.json
7811 run/replay/r35c_r5d/20260614_003605/replay_locked_single_day_r35c_r5d_20260601_20260613_190615_46090f86/03_integrity_report.json
7642 run/replay/r35c_r5d/20260614_003605/replay_locked_single_day_r35c_r5d_20260601_20260613_190615_46090f86/01_dataset_summary.json
5043 run/replay/r35c_r5d/20260614_003605/replay_locked_single_day_r35c_r5d_20260601_20260613_190615_46090f86/artifacts/engine_result.json
3884 run/replay/r35c_r5d/20260614_003605/replay_locked_single_day_r35c_r5d_20260601_20260613_190615_46090f86/00_manifest.json
2959 run/replay/r35c_r5d/20260614_003605/replay_locked_single_day_r35c_r5d_20260601_20260613_190615_46090f86/artifacts/10_run_summary.json
2336 run/replay/r35c_r5d/20260614_003605/replay_locked_single_day_r35c_r5d_20260601_20260613_190615_46090f86/17_effective_inputs.json
977 run/replay/r35c_r5d/20260614_003605/replay_locked_single_day_r35c_r5d_20260601_20260613_190615_46090f86/artifacts/11_run_summary.csv
769 run/replay/r35c_r5d/20260614_003605/replay_locked_single_day_r35c_r5d_20260601_20260613_190615_46090f86/artifacts/b3_r32_analysis_exports_status.json
278 run/replay/r35c_r5d/20260614_003605/replay_locked_single_day_r35c_r5d_20260601_20260613_190615_46090f86/18_effective_overrides_flat.json
202 run/replay/r35c_r5d/20260614_003605/replay_locked_single_day_r35c_r5d_20260601_20260613_190615_46090f86/06_candidate_audit.csv
113 run/replay/r35c_r5d/20260614_003605/replay_locked_single_day_r35c_r5d_20260601_20260613_190615_46090f86/artifacts/blocker_distribution.csv
81 run/replay/r35c_r5d/20260614_003605/replay_locked_single_day_r35c_r5d_20260601_20260613_190615_46090f86/artifacts/family_side_summary.csv
59 run/replay/r35c_r5d/20260614_003605/replay_locked_single_day_r35c_r5d_20260601_20260613_190615_46090f86/04_metrics_summary.json

## Replay log tail
            "relative_path": "quote_ticks_mme_opt_stream.csv",
            "row_count": 110139,
            "sha256": "d83b79bcc9acc15906cbc867b35ecd3f51bfe659cf2cf89b755f7adbaacf7342",
            "size_bytes": 20109951,
            "stem": "quote_ticks_mme_opt_stream",
            "suffix": ".csv"
          },
          {
            "line_count": 8,
            "modified_at_utc": "2026-06-13T14:00:50Z",
            "name": "source_manifest.json",
            "relative_path": "source_manifest.json",
            "row_count": null,
            "sha256": "05c948e473da0c6c115e01381f3d9a7f19c8df1e0c63ea4a7f70b076588b51d1",
            "size_bytes": 222,
            "stem": "source_manifest",
            "suffix": ".json"
          }
        ]
      }
    ],
    "selection_fingerprint": "31294f99eb51f9e5908ed6604050ddcfb329f6c70bee573a6f5d5050c8ec666f",
    "selection_mode": "single_day",
    "selection_notes": [],
    "session_segment": null,
    "trading_dates": [
      "2026-06-01"
    ]
  },
  "status": "ok",
  "topology_plan": {
    "notes": [],
    "scope": "feeds_features_strategy_risk_execution_shadow",
    "stage_names": [
      "feeds",
      "features",
      "strategy",
      "risk",
      "execution_shadow"
    ],
    "stages": [
      {
        "description": "Replay input publication / feed-stage chain entry.",
        "order_index": 0,
        "owns_runtime_decisioning": false,
        "stage_name": "feeds",
        "terminal_stage": false
      },
      {
        "description": "Feature computation stage driven from replayed feed truth.",
        "order_index": 1,
        "owns_runtime_decisioning": true,
        "stage_name": "features",
        "terminal_stage": false
      },
      {
        "description": "Strategy decision stage driven from replay feature truth.",
        "order_index": 2,
        "owns_runtime_decisioning": true,
        "stage_name": "strategy",
        "terminal_stage": false
      },
      {
        "description": "Risk gating stage applied to replay strategy outputs.",
        "order_index": 3,
        "owns_runtime_decisioning": true,
        "stage_name": "risk",
        "terminal_stage": false
      },
      {
        "description": "Replay-only execution shadow stage with no live side effects.",
        "order_index": 4,
        "owns_runtime_decisioning": true,
        "stage_name": "execution_shadow",
        "terminal_stage": true
      }
    ],
    "topology_fingerprint": "4b6fc95a56eb8cd691208a5c21bd70994aa136956bd1f683863f0090813eda59"
  }
}
