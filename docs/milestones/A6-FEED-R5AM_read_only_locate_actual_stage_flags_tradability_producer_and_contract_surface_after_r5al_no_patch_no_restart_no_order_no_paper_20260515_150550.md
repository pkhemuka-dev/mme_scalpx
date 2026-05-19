# A6-FEED-R5AM_read_only_locate_actual_stage_flags_tradability_producer_and_contract_surface_after_r5al_no_patch_no_restart_no_order_no_paper_20260515_150550

Batch: A6-FEED-R5AM

Purpose: read_only_locate_actual_stage_flags_tradability_producer_and_contract_surface_after_r5al_no_patch_no_restart_no_order_no_paper

Final verdict: FAIL_A6_FEED_R5AM_SAFETY_OR_SURFACE_LOCATION_CHECK

Safety: read-only actual stage_flags producer/contract surface location only; no patch, no restore, no clear/delete, no start/restart/stop, no Redis write, no paper/live, no risk/execution, no broker/order.

Classification:

```json
{
  "decisions_stream_age_ms": 18763338,
  "decisions_stream_xlen": 1684,
  "feature_stream_stage_flags_with_tradability": [],
  "features_stream_age_ms": 15478987,
  "features_stream_xlen": 131,
  "likely_condition": "SURFACE_LOCATION_OR_SAFETY_CHECK_FAILED",
  "next_action": "Stop and review proof.",
  "r5ak_final_verdict": "PASS_A6_FEED_R5AK_STAGE_FLAGS_CONTRACT_ALIGNMENT_PATCH_PLAN_READY_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER",
  "r5ak_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AK_read_only_stage_flags_contract_alignment_patch_plan_no_patch_no_restart_no_order_no_paper_20260515_150204.json",
  "r5al_final_verdict": "FAIL_A6_FEED_R5AL_STAGE_FLAGS_PATCH_OR_SAFETY_CHECK",
  "r5al_patch_applied": null,
  "r5al_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AL_narrow_stage_flags_contract_alignment_patch_remove_extra_tradability_flag_no_restart_no_order_no_paper_20260515_150353.json",
  "services": [],
  "stage_dicts_with_tradability": [
    {
      "end_lineno": 407,
      "file": "app/mme_scalpx/services/feature_family/common.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "lot_size",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "spread",
        "spread_ratio",
        "strike",
        "tick_size",
        "top5_ask_qty",
        "top5_bid_qty",
        "tradability_ok"
      ],
      "lineno": 390
    },
    {
      "end_lineno": 425,
      "file": "app/mme_scalpx/services/feature_family/common.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "side",
        "spread",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 412
    },
    {
      "end_lineno": 808,
      "file": "app/mme_scalpx/services/feature_family/contracts.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "lot_size",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "spread",
        "spread_ratio",
        "strike",
        "tick_size",
        "top5_ask_qty",
        "top5_bid_qty",
        "tradability_ok"
      ],
      "lineno": 791
    },
    {
      "end_lineno": 825,
      "file": "app/mme_scalpx/services/feature_family/contracts.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "side",
        "spread",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 812
    },
    {
      "end_lineno": 733,
      "file": "app/mme_scalpx/services/feature_family/option_core.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "depth_ok",
        "depth_total_min",
        "premium_floor_min",
        "premium_floor_ok",
        "response_efficiency_min",
        "response_efficiency_ok",
        "spread_ratio_max",
        "spread_ratio_ok",
        "tradability_ok"
      ],
      "lineno": 718
    },
    {
      "end_lineno": 5650,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "ask",
        "ask_qty",
        "ask_qty_5",
        "best_ask",
        "best_bid",
        "bid",
        "bid_qty",
        "bid_qty_5",
        "delta",
        "depth_total",
        "instrument_key",
        "instrument_token",
        "iv",
        "ltp",
        "oi",
        "oi_change",
        "option_side",
        "option_symbol",
        "option_token",
        "present",
        "provider_id",
        "raw",
        "role",
        "side",
        "source_member_key",
        "spread",
        "spread_ratio",
        "strike",
        "tradability_ok",
        "trading_symbol",
        "ts_event_ns",
        "valid",
        "volume"
      ],
      "lineno": 5616
    },
    {
      "end_lineno": 6922,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "anomaly",
        "best_ask",
        "best_bid",
        "book_ok",
        "depth_ok",
        "depth_total",
        "ltp",
        "quote_ok",
        "selected_present",
        "side",
        "spread",
        "spread_ok",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 6907
    },
    {
      "end_lineno": 7139,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "side",
        "spread",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 7126
    },
    {
      "end_lineno": 7310,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "side",
        "spread",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 7297
    },
    {
      "end_lineno": 7507,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "side",
        "spread",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 7494
    },
    {
      "end_lineno": 1727,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "ask",
        "bid",
        "delta_3",
        "depth_ok",
        "depth_total",
        "instrument_key",
        "instrument_token",
        "ltp",
        "oi",
        "option_side",
        "present",
        "response_efficiency",
        "side",
        "spread",
        "spread_ratio",
        "strike",
        "tick_size",
        "tradability_ok",
        "trading_symbol",
        "valid",
        "volume"
      ],
      "lineno": 1705
    },
    {
      "end_lineno": 2476,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "blocked_reason",
        "depth_ok",
        "depth_total",
        "entry_pass",
        "premium_floor_ok",
        "response_efficiency",
        "response_efficiency_ok",
        "side",
        "spread_ratio",
        "spread_ratio_ok",
        "tradability_ok"
      ],
      "lineno": 2464
    },
    {
      "end_lineno": 3242,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "lot_size",
        "ltp",
        "nof_slope",
        "ofi_ratio_proxy",
        "response_efficiency",
        "side",
        "spread",
        "spread_ratio",
        "spread_ticks",
        "strike",
        "tick_size",
        "top5_ask_qty",
        "top5_bid_qty",
        "tradability_ok",
        "weighted_ofi_persist"
      ],
      "lineno": 3219
    },
    {
      "end_lineno": 3724,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "active_futures_provider_id",
        "active_option_context_provider_id",
        "active_selected_option_provider_id",
        "branch_id",
        "eligible",
        "family_id",
        "family_runtime_mode",
        "frame_id",
        "frame_ts_ns",
        "instrument_key",
        "instrument_token",
        "option_price",
        "option_symbol",
        "runtime_mode",
        "side",
        "stop_points",
        "strike",
        "surface",
        "target_points",
        "tick_size",
        "tradability_ok"
      ],
      "lineno": 3698
    },
    {
      "end_lineno": 6732,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "depth_ok",
        "entry_pass",
        "source_bridge",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 6726
    },
    {
      "end_lineno": 7016,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "depth_ok",
        "entry_pass",
        "quote_ok",
        "source_bridge",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 7009
    },
    {
      "end_lineno": 467,
      "file": "app/mme_scalpx/services/strategy.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "branch_id",
        "eligible",
        "family_id",
        "instrument_key",
        "instrument_token",
        "key",
        "option_price",
        "option_symbol",
        "side",
        "strike",
        "tradability_ok"
      ],
      "lineno": 455
    },
    {
      "end_lineno": 407,
      "file": "app/mme_scalpx/services/feature_family/common.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "lot_size",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "spread",
        "spread_ratio",
        "strike",
        "tick_size",
        "top5_ask_qty",
        "top5_bid_qty",
        "tradability_ok"
      ],
      "lineno": 390
    },
    {
      "end_lineno": 425,
      "file": "app/mme_scalpx/services/feature_family/common.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "side",
        "spread",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 412
    },
    {
      "end_lineno": 808,
      "file": "app/mme_scalpx/services/feature_family/contracts.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "lot_size",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "spread",
        "spread_ratio",
        "strike",
        "tick_size",
        "top5_ask_qty",
        "top5_bid_qty",
        "tradability_ok"
      ],
      "lineno": 791
    },
    {
      "end_lineno": 825,
      "file": "app/mme_scalpx/services/feature_family/contracts.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "side",
        "spread",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 812
    },
    {
      "end_lineno": 733,
      "file": "app/mme_scalpx/services/feature_family/option_core.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "depth_ok",
        "depth_total_min",
        "premium_floor_min",
        "premium_floor_ok",
        "response_efficiency_min",
        "response_efficiency_ok",
        "spread_ratio_max",
        "spread_ratio_ok",
        "tradability_ok"
      ],
      "lineno": 718
    }
  ],
  "stage_flag_source_files": [
    "app/mme_scalpx/services/feature_family/common.py",
    "app/mme_scalpx/services/feature_family/contracts.py",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/strategy_family/activation.py",
    "app/mme_scalpx/services/strategy_family/common.py",
    "app/mme_scalpx/services/strategy_family/eligibility.py",
    "app/mme_scalpx/services/strategy_family/misb.py",
    "app/mme_scalpx/services/strategy_family/misc.py",
    "app/mme_scalpx/services/strategy_family/miso.py",
    "app/mme_scalpx/services/strategy_family/misr.py",
    "app/mme_scalpx/services/strategy_family/mist.py"
  ],
  "tradability_source_files": [
    "app/mme_scalpx/services/feature_family/common.py",
    "app/mme_scalpx/services/feature_family/contracts.py",
    "app/mme_scalpx/services/feature_family/misb_surface.py",
    "app/mme_scalpx/services/feature_family/misc_surface.py",
    "app/mme_scalpx/services/feature_family/miso_surface.py",
    "app/mme_scalpx/services/feature_family/misr_surface.py",
    "app/mme_scalpx/services/feature_family/mist_surface.py",
    "app/mme_scalpx/services/feature_family/option_core.py",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/strategy_family/misb.py",
    "app/mme_scalpx/services/strategy_family/misc.py",
    "app/mme_scalpx/services/strategy_family/miso.py",
    "app/mme_scalpx/services/strategy_family/misr.py",
    "app/mme_scalpx/services/strategy_family/mist.py"
  ]
}
```

Required checks:

```json
{
  "all_watched_sources_compile": true,
  "latest_r5ak_plan_ready_found": true,
  "latest_r5al_failure_found": false,
  "no_broker_order": true,
  "no_lock_clear_delete": true,
  "no_paper_live": true,
  "no_patch": true,
  "no_redis_write": true,
  "no_restore": true,
  "no_risk_execution_order_process_visible": true,
  "no_service_start_restart_stop": true,
  "orders_mme_stream_zero_or_absent": true,
  "position_flat": true,
  "searched_sources_unchanged_by_this_batch": true,
  "source_hits_found": true,
  "stage_flags_source_reference_found": true,
  "tradability_ok_source_reference_found": true,
  "watched_sources_unchanged_by_this_batch": true
}
```

Failures:

```json
[
  "latest_r5al_failure_found"
]
```

Artifacts:
- Proof: /home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AM_read_only_locate_actual_stage_flags_tradability_producer_and_contract_surface_after_r5al_no_patch_no_restart_no_order_no_paper_20260515_150550.json
- Review note: /home/Lenovo/scalpx/projects/mme_scalpx/docs/runbooks/A6-FEED-R5AM_read_only_locate_actual_stage_flags_tradability_producer_and_contract_surface_after_r5al_no_patch_no_restart_no_order_no_paper_20260515_150550_actual_stage_flags_surface_note.md
