# R35C_R4X_JUNE01_REPLAY_VERIFY_SHADOW_TRADE_COUNT_SUMMARY_NO_ORDER_20260614_000314

classification: PASS_R35C_R4X_JUNE01_SUMMARY_SHADOW_TRADE_COUNT_VERIFIED_NO_ORDER
proof: `run/proofs/R35C_R4X_JUNE01_REPLAY_VERIFY_SHADOW_TRADE_COUNT_SUMMARY_NO_ORDER_20260614_000314.json`
run_root: `run/replay/r35c_r4x/20260614_000314`

replay_rc=0
summary=run/replay/r35c_r4x/20260614_000314/replay_locked_single_day_r35c_r4x_20260601_20260613_183322_0860a772/artifacts/10_run_summary.json
summary_csv=run/replay/r35c_r4x/20260614_000314/replay_locked_single_day_r35c_r4x_20260601_20260613_183322_0860a772/artifacts/11_run_summary.csv
engine=run/replay/r35c_r4x/20260614_000314/replay_locked_single_day_r35c_r4x_20260601_20260613_183322_0860a772/artifacts/engine_result.json
early_error=
safety_post=0/0/0 replay_proc=0
big_files_over_50mb=0
trade_count=4222 shadow_trade_count=4222 execution_shadow_filled_count=4222 pnl_status_present=1

## Summary check
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

## Summary check errors

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
    "selection_fingerprint": "1badfbc7ae2e56b8fe7103bd7b165b9c89bae349cac496a7cc7b3d146d30ced9",
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
