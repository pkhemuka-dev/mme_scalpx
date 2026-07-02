# LANE-X-R34Z-R1_EXACT_POSSIBLE_TRADE_TABLE_RECONSTRUCTION_NO_PATCH_NO_REPLAY_NO_ORDER_extract_closed_trade_truth_rows_with_entry_exit_instrument_and_pnl_from_existing_artifacts_only_20260613_162302

classification: PASS_R34Z_R1_EXACT_POSSIBLE_TRADE_TABLE_RECONSTRUCTED_NO_PATCH_NO_REPLAY_NO_ORDER
proof: `run/proofs/LANE-X-R34Z-R1_EXACT_POSSIBLE_TRADE_TABLE_RECONSTRUCTION_NO_PATCH_NO_REPLAY_NO_ORDER_extract_closed_trade_truth_rows_with_entry_exit_instrument_and_pnl_from_existing_artifacts_only_20260613_162302.json`
audit: `run/audits/LANE-X-R34Z-R1_EXACT_POSSIBLE_TRADE_TABLE_RECONSTRUCTION_NO_PATCH_NO_REPLAY_NO_ORDER_extract_closed_trade_truth_rows_with_entry_exit_instrument_and_pnl_from_existing_artifacts_only_20260613_162302`
csv: `run/audits/LANE-X-R34Z-R1_EXACT_POSSIBLE_TRADE_TABLE_RECONSTRUCTION_NO_PATCH_NO_REPLAY_NO_ORDER_extract_closed_trade_truth_rows_with_entry_exit_instrument_and_pnl_from_existing_artifacts_only_20260613_162302/exact_possible_trades.csv`
summary: `run/audits/LANE-X-R34Z-R1_EXACT_POSSIBLE_TRADE_TABLE_RECONSTRUCTION_NO_PATCH_NO_REPLAY_NO_ORDER_extract_closed_trade_truth_rows_with_entry_exit_instrument_and_pnl_from_existing_artifacts_only_20260613_162302/exact_possible_trades_summary.json`

## Safety
- compile_rc: 0
- recon_rc: 0
- orders/risk/execution: 0 / 0 / 0
- risk/execution proc: 0 / 0

## Trade reconstruction result
- raw_trade_like_rows: 51
- complete_trade_rows: 12
- net_pnl_count: 34
- net_pnl_total: 4561.5

## Summary
{
  "complete_trade_rows": 12,
  "csv": "run/audits/LANE-X-R34Z-R1_EXACT_POSSIBLE_TRADE_TABLE_RECONSTRUCTION_NO_PATCH_NO_REPLAY_NO_ORDER_extract_closed_trade_truth_rows_with_entry_exit_instrument_and_pnl_from_existing_artifacts_only_20260613_162302/exact_possible_trades.csv",
  "exit_reason_counts": {
    "UNKNOWN": 34,
    "liquidity_exit": 1,
    "momentum_exit": 16
  },
  "family_counts": {
    "MISB": 1,
    "MISC": 1,
    "MISO": 1,
    "MISR": 1,
    "MIST": 13,
    "UNKNOWN": 34
  },
  "files_seen": 30000,
  "files_with_trade_terms": 1271,
  "first_20_rows": [
    {
      "blocker": "NO_BLOCKER",
      "candidate_id": "",
      "entry_price": "",
      "entry_time_ist": "",
      "entry_ts_raw": "",
      "exit_price": "",
      "exit_reason": "",
      "exit_time_ist": "",
      "exit_ts_raw": "",
      "false_entry": "",
      "family": "UNKNOWN",
      "good_blocker": "",
      "gross_pnl": "",
      "instrument_token": "",
      "missed_trade": "",
      "net_pnl_after_costs": 206.25,
      "remarks": "RAW-L enriched copy; unknown values are not inferred.",
      "row_kind": "trade",
      "selected_strike": "",
      "side": "UNKNOWN",
      "source_file": "run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl",
      "stop_hit_after_block": "",
      "strategy_id": "UNKNOWN",
      "symbol": "",
      "target_hit_after_block": "",
      "trade_id": "exports:1"
    },
    {
      "blocker": "NO_BLOCKER",
      "candidate_id": "",
      "entry_price": "",
      "entry_time_ist": "",
      "entry_ts_raw": "",
      "exit_price": "",
      "exit_reason": "",
      "exit_time_ist": "",
      "exit_ts_raw": "",
      "false_entry": "",
      "family": "UNKNOWN",
      "good_blocker": "",
      "gross_pnl": "",
      "instrument_token": "",
      "missed_trade": "",
      "net_pnl_after_costs": 206.25,
      "remarks": "RAW-L enriched copy; unknown values are not inferred.",
      "row_kind": "trade",
      "selected_strike": "",
      "side": "UNKNOWN",
      "source_file": "run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl",
      "stop_hit_after_block": "",
      "strategy_id": "UNKNOWN",
      "symbol": "",
      "target_hit_after_block": "",
      "trade_id": "exports:2"
    },
    {
      "blocker": "NO_BLOCKER",
      "candidate_id": "",
      "entry_price": "",
      "entry_time_ist": "",
      "entry_ts_raw": "",
      "exit_price": "",
      "exit_reason": "",
      "exit_time_ist": "",
      "exit_ts_raw": "",
      "false_entry": "",
      "family": "UNKNOWN",
      "good_blocker": "",
      "gross_pnl": "",
      "instrument_token": "",
      "missed_trade": "",
      "net_pnl_after_costs": 206.25,
      "remarks": "RAW-L enriched copy; unknown values are not inferred.",
      "row_kind": "trade",
      "selected_strike": "",
      "side": "UNKNOWN",
      "source_file": "run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl",
      "stop_hit_after_block": "",
      "strategy_id": "UNKNOWN",
      "symbol": "",
      "target_hit_after_block": "",
      "trade_id": "exports:3"
    },
    {
      "blocker": "NO_BLOCKER",
      "candidate_id": "",
      "entry_price": "",
      "entry_time_ist": "",
      "entry_ts_raw": "",
      "exit_price": "",
      "exit_reason": "",
      "exit_time_ist": "",
      "exit_ts_raw": "",
      "false_entry": "",
      "family": "UNKNOWN",
      "good_blocker": "",
      "gross_pnl": "",
      "instrument_token": "",
      "missed_trade": "",
      "net_pnl_after_costs": 206.25,
      "remarks": "RAW-L enriched copy; unknown values are not inferred.",
      "row_kind": "trade",
      "selected_strike": "",
      "side": "UNKNOWN",
      "source_file": "run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl",
      "stop_hit_after_block": "",
      "strategy_id": "UNKNOWN",
      "symbol": "",
      "target_hit_after_block": "",
      "trade_id": "exports:4"
    },
    {
      "blocker": "NO_BLOCKER",
      "candidate_id": "",
      "entry_price": "",
      "entry_time_ist": "",
      "entry_ts_raw": "",
      "exit_price": "",
      "exit_reason": "",
      "exit_time_ist": "",
      "exit_ts_raw": "",
      "false_entry": "",
      "family": "UNKNOWN",
      "good_blocker": "",
      "gross_pnl": "",
      "instrument_token": "",
      "missed_trade": "",
      "net_pnl_after_costs": 206.25,
      "remarks": "RAW-L enriched copy; unknown values are not inferred.",
      "row_kind": "trade",
      "selected_strike": "",
      "side": "UNKNOWN",
      "source_file": "run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl",
      "stop_hit_after_block": "",
      "strategy_id": "UNKNOWN",
      "symbol": "",
      "target_hit_after_block": "",
      "trade_id": "exports:5"
    },
    {
      "blocker": "NO_BLOCKER",
      "candidate_id": "",
      "entry_price": "",
      "entry_time_ist": "",
      "entry_ts_raw": "",
      "exit_price": "",
      "exit_reason": "",
      "exit_time_ist": "",
      "exit_ts_raw": "",
      "false_entry": "",
      "family": "UNKNOWN",
      "good_blocker": "",
      "gross_pnl": "",
      "instrument_token": "",
      "missed_trade": "",
      "net_pnl_after_costs": 206.25,
      "remarks": "RAW-L enriched copy; unknown values are not inferred.",
      "row_kind": "trade",
      "selected_strike": "",
      "side": "UNKNOWN",
      "source_file": "run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl",
      "stop_hit_after_block": "",
      "strategy_id": "UNKNOWN",
      "symbol": "",
      "target_hit_after_block": "",
      "trade_id": "exports:6"
    },
    {
      "blocker": "NO_BLOCKER",
      "candidate_id": "",
      "entry_price": "",
      "entry_time_ist": "",
      "entry_ts_raw": "",
      "exit_price": "",
      "exit_reason": "",
      "exit_time_ist": "",
      "exit_ts_raw": "",
      "false_entry": "",
      "family": "UNKNOWN",
      "good_blocker": "",
      "gross_pnl": "",
      "instrument_token": "",
      "missed_trade": "",
      "net_pnl_after_costs": 206.25,
      "remarks": "RAW-L enriched copy; unknown values are not inferred.",
      "row_kind": "trade",
      "selected_strike": "",
      "side": "UNKNOWN",
      "source_file": "run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl",
      "stop_hit_after_block": "",
      "strategy_id": "UNKNOWN",
      "symbol": "",
      "target_hit_after_block": "",
      "trade_id": "exports:7"
    },
    {
      "blocker": "NO_BLOCKER",
      "candidate_id": "",
      "entry_price": "",
      "entry_time_ist": "",
      "entry_ts_raw": "",
      "exit_price": "",
      "exit_reason": "",
      "exit_time_ist": "",
      "exit_ts_raw": "",
      "false_entry": "",
      "family": "UNKNOWN",
      "good_blocker": "",
      "gross_pnl": "",
      "instrument_token": "",
      "missed_trade": "",
      "net_pnl_after_costs": 206.25,
      "remarks": "RAW-L enriched copy; unknown values are not inferred.",
      "row_kind": "trade",
      "selected_strike": "",
      "side": "UNKNOWN",
      "source_file": "run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl",
      "stop_hit_after_block": "",
      "strategy_id": "UNKNOWN",
      "symbol": "",
      "target_hit_after_block": "",
      "trade_id": "exports:8"
    },
    {
      "blocker": "NO_BLOCKER",
      "candidate_id": "",
      "entry_price": "",
      "entry_time_ist": "",
      "entry_ts_raw": "",
      "exit_price": "",
      "exit_reason": "",
      "exit_time_ist": "",
      "exit_ts_raw": "",
      "false_entry": "",
      "family": "UNKNOWN",
      "good_blocker": "",
      "gross_pnl": "",
      "instrument_token": "",
      "missed_trade": "",
      "net_pnl_after_costs": 206.25,
      "remarks": "RAW-L enriched copy; unknown values are not inferred.",
      "row_kind": "trade",
      "selected_strike": "",
      "side": "UNKNOWN",
      "source_file": "run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl",
      "stop_hit_after_block": "",
      "strategy_id": "UNKNOWN",
      "symbol": "",
      "target_hit_after_block": "",
      "trade_id": "exports:9"
    },
    {
      "blocker": "NO_BLOCKER",
      "candidate_id": "",
      "entry_price": "",
      "entry_time_ist": "",
      "entry_ts_raw": "",
      "exit_price": "",
      "exit_reason": "",
      "exit_time_ist": "",
      "exit_ts_raw": "",
      "false_entry": "",
      "family": "UNKNOWN",
      "good_blocker": "",
      "gross_pnl": "",
      "instrument_token": "",
      "missed_trade": "",
      "net_pnl_after_costs": 206.25,
      "remarks": "RAW-L enriched copy; unknown values are not inferred.",
      "row_kind": "trade",
      "selected_strike": "",
      "side": "UNKNOWN",
      "source_file": "run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl",
      "stop_hit_after_block": "",
      "strategy_id": "UNKNOWN",
      "symbol": "",
      "target_hit_after_block": "",
      "trade_id": "exports:10"
    },
    {
      "blocker": "NO_BLOCKER",
      "candidate_id": "",
      "entry_price": "",
      "entry_time_ist": "",
      "entry_ts_raw": "",
      "exit_price": "",
      "exit_reason": "",
      "exit_time_ist": "",
      "exit_ts_raw": "",
      "false_entry": true,
      "family": "UNKNOWN",
      "good_blocker": "",
      "gross_pnl": "",
      "instrument_token": "",
      "missed_trade": "",
      "net_pnl_after_costs": -468.75,
      "remarks": "RAW-L enriched copy; unknown values are not inferred.",
      "row_kind": "trade",
      "selected_strike": "",
      "side": "UNKNOWN",
      "source_file": "run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl",
      "stop_hit_after_block": "",
      "strategy_id": "UNKNOWN",
      "symbol": "",
      "target_hit_after_block": "",
      "trade_id": "exports:11"
    },
    {
      "blocker": "NO_BLOCKER",
      "candidate_id": "",
      "entry_price": "",
      "entry_time_ist": "",
      "entry_ts_raw": "",
      "exit_price": "",
      "exit_reason": "",
      "exit_time_ist": "",
      "exit_ts_raw": "",
      "false_entry": "",
      "family": "UNKNOWN",
      "good_blocker": "",
      "gross_pnl": "",
      "instrument_token": "",
      "missed_trade": "",
      "net_pnl_after_costs": 206.25,
      "remarks": "RAW-L enriched copy; unknown values are not inferred.",
      "row_kind": "trade",
      "selected_strike": "",
      "side": "UNKNOWN",
      "source_file": "run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl",
      "stop_hit_after_block": "",
      "strategy_id": "UNKNOWN",
      "symbol": "",
      "target_hit_after_block": "",
      "trade_id": "exports:12"
    },
    {
      "blocker": "NO_BLOCKER",
      "candidate_id": "",
      "entry_price": "",
      "entry_time_ist": "",
      "entry_ts_raw": "",
      "exit_price": "",
      "exit_reason": "",
      "exit_time_ist": "",
      "exit_ts_raw": "",
      "false_entry": "",
      "family": "UNKNOWN",
      "good_blocker": "",
      "gross_pnl": "",
      "instrument_token": "",
      "missed_trade": "",
      "net_pnl_after_costs": 206.25,
      "remarks": "RAW-L enriched copy; unknown values are not inferred.",
      "row_kind": "trade",
      "selected_strike": "",
      "side": "UNKNOWN",
      "source_file": "run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl",
      "stop_hit_after_block": "",
      "strategy_id": "UNKNOWN",
      "symbol": "",
      "target_hit_after_block": "",
      "trade_id": "exports:13"
    },
    {
      "blocker": "NO_BLOCKER",
      "candidate_id": "",
      "entry_price": "",
      "entry_time_ist": "",
      "entry_ts_raw": "",
      "exit_price": "",
      "exit_reason": "",
      "exit_time_ist": "",
      "exit_ts_raw": "",
      "false_entry": "",
      "family": "UNKNOWN",
      "good_blocker": "",
      "gross_pnl": "",
      "instrument_token": "",
      "missed_trade": "",
      "net_pnl_after_costs": 206.25,
      "remarks": "RAW-L enriched copy; unknown values are not inferred.",
      "row_kind": "trade",
      "selected_strike": "",
      "side": "UNKNOWN",
      "source_file": "run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl",
      "stop_hit_after_block": "",
      "strategy_id": "UNKNOWN",
      "symbol": "",
      "target_hit_after_block": "",
      "trade_id": "exports:14"
    },
    {
      "blocker": "NO_BLOCKER",
      "candidate_id": "",
      "entry_price": "",
      "entry_time_ist": "",
      "entry_ts_raw": "",
      "exit_price": "",
      "exit_reason": "",
      "exit_time_ist": "",
      "exit_ts_raw": "",
      "false_entry": true,
      "family": "UNKNOWN",
      "good_blocker": "",
      "gross_pnl": "",
      "instrument_token": "",
      "missed_trade": "",
      "net_pnl_after_costs": -220.5,
      "remarks": "RAW-L enriched copy; unknown values are not inferred.",
      "row_kind": "trade",
      "selected_strike": "",
      "side": "UNKNOWN",
      "source_file": "run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl",
      "stop_hit_after_block": "",
      "strategy_id": "UNKNOWN",
      "symbol": "",
      "target_hit_after_block": "",
      "trade_id": "exports:15"
    },
    {
      "blocker": "NO_BLOCKER",
      "candidate_id": "",
      "entry_price": "",
      "entry_time_ist": "",
      "entry_ts_raw": "",
      "exit_price": "",
      "exit_reason": "",
      "exit_time_ist": "",
      "exit_ts_raw": "",
      "false_entry": "",
      "family": "UNKNOWN",
      "good_blocker": "",
      "gross_pnl": "",
      "instrument_token": "",
      "missed_trade": "",
      "net_pnl_after_costs": 206.25,
      "remarks": "RAW-L enriched copy; unknown values are not inferred.",
      "row_kind": "trade",
      "selected_strike": "",
      "side": "UNKNOWN",
      "source_file": "run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl",
      "stop_hit_after_block": "",
      "strategy_id": "UNKNOWN",
      "symbol": "",
      "target_hit_after_block": "",
      "trade_id": "exports:17"
    },
    {
      "blocker": "NO_BLOCKER",
      "candidate_id": "",
      "entry_price": "",
      "entry_time_ist": "",
      "entry_ts_raw": "",
      "exit_price": "",
      "exit_reason": "",
      "exit_time_ist": "",
      "exit_ts_raw": "",
      "false_entry": "",
      "family": "UNKNOWN",
      "good_blocker": "",
      "gross_pnl": "",
      "instrument_token": "",
      "missed_trade": "",
      "net_pnl_after_costs": 82.5,
      "remarks": "RAW-L enriched copy; unknown values are not inferred.",
      "row_kind": "trade",
      "selected_strike": "",
      "side": "UNKNOWN",
      "source_file": "run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl",
      "stop_hit_after_block": "",
      "strategy_id": "UNKNOWN",
      "symbol": "",
      "target_hit_after_block": "",
      "trade_id": "exports:18"
    },
    {
      "blocker": "NO_BLOCKER",
      "candidate_id": "RAW_W_EVENT_ID_exports:1",
      "entry_price": "",
      "entry_time_ist": "",
      "entry_ts_raw": "",
      "exit_price": "",
      "exit_reason": "",
      "exit_time_ist": "",
      "exit_ts_raw": "",
      "false_entry": "",
      "family": "MIST",
      "good_blocker": "",
      "gross_pnl": "",
      "instrument_token": "",
      "missed_trade": "",
      "net_pnl_after_costs": 206.25,
      "remarks": "RAW-L enriched copy; unknown values are not inferred.",
      "row_kind": "trade",
      "selected_strike": "",
      "side": "CALL",
      "source_file": "run/replay/raw_y_small_validation_20260501_155332_trade_family_backfill/trade_family_backfilled_records.jsonl",
      "stop_hit_after_block": "",
      "strategy_id": "MIST",
      "symbol": "",
      "target_hit_after_block": "",
      "trade_id": "exports:1"
    },
    {
      "blocker": "NO_BLOCKER",
      "candidate_id": "RAW_W_EVENT_ID_exports:2",
      "entry_price": "",
      "entry_time_ist": "",
      "entry_ts_raw": "",
      "exit_price": "",
      "exit_reason": "",
      "exit_time_ist": "",
      "exit_ts_raw": "",
      "false_entry": "",
      "family": "MISB",
      "good_blocker": "",
      "gross_pnl": "",
      "instrument_token": "",
      "missed_trade": "",
      "net_pnl_after_costs": 206.25,
      "remarks": "RAW-L enriched copy; unknown values are not inferred.",
      "row_kind": "trade",
      "selected_strike": "",
      "side": "PUT",
      "source_file": "run/replay/raw_y_small_validation_20260501_155332_trade_family_backfill/trade_family_backfilled_records.jsonl",
      "stop_hit_after_block": "",
      "strategy_id": "MISB",
      "symbol": "",
      "target_hit_after_block": "",
      "trade_id": "exports:2"
    },
    {
      "blocker": "NO_BLOCKER",
      "candidate_id": "RAW_W_EVENT_ID_exports:3",
      "entry_price": "",
      "entry_time_ist": "",
      "entry_ts_raw": "",
      "exit_price": "",
      "exit_reason": "",
      "exit_time_ist": "",
      "exit_ts_raw": "",
      "false_entry": "",
      "family": "MISC",
      "good_blocker": "",
      "gross_pnl": "",
      "instrument_token": "",
      "missed_trade": "",
      "net_pnl_after_costs": 206.25,
      "remarks": "RAW-L enriched copy; unknown values are not inferred.",
      "row_kind": "trade",
      "selected_strike": "",
      "side": "CALL",
      "source_file": "run/replay/raw_y_small_validation_20260501_155332_trade_family_backfill/trade_family_backfilled_records.jsonl",
      "stop_hit_after_block": "",
      "strategy_id": "MISC",
      "symbol": "",
      "target_hit_after_block": "",
      "trade_id": "exports:3"
    }
  ],
  "gross_pnl_avg": -24.104166666666668,
  "gross_pnl_count": 12,
  "gross_pnl_total": -289.25,
  "json_objs_seen": 37831,
  "net_pnl_avg": 134.16176470588235,
  "net_pnl_count": 34,
  "net_pnl_total": 4561.5,
  "raw_trade_like_rows": 51,
  "side_counts": {
    "CALL": 21,
    "PUT": 8,
    "UNKNOWN": 22
  },
  "source_files_used_top": [
    [
      "run/replay/raw_t_post_raw_s_replay_rerun_20260501_151908_raw_s_export/enriched_replay_records.jsonl",
      408
    ],
    [
      "run/replay/raw_t_post_raw_s_replay_rerun_20260501_151908_trade_family_backfill/trade_family_backfilled_records.jsonl",
      408
    ],
    [
      "run/replay/raw_t_post_raw_s_replay_rerun_20260501_151813_trade_family_backfill/trade_family_backfilled_records.jsonl",
      102
    ],
    [
      "run/replay/raw_t_post_raw_s_replay_rerun_20260501_151813_raw_s_export/enriched_replay_records.jsonl",
      102
    ],
    [
      "run/replay/raw_y_small_validation_20260501_155332_trade_family_backfill/trade_family_backfilled_records.jsonl",
      68
    ],
    [
      "run/replay/raw_y_small_validation_20260501_155332_export/enriched_replay_records.jsonl",
      68
    ],
    [
      "run/replay/raw_q_trade_family_backfill_20260501_143325/trade_family_backfilled_records.jsonl",
      51
    ],
    [
      "run/replay/raw_p_repair_true_family_20260501_143008/enriched_replay_records.jsonl",
      51
    ],
    [
      "run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl",
      17
    ],
    [
      "run/replay/raw_m_replay_enrichment_flow_20260501_140443/enriched_replay_records.jsonl",
      17
    ],
    [
      "run/proofs/forced_trade_feature_forensics_2026_04_16.txt",
      12
    ],
    [
      "run/proofs/forced_trade_feature_forensics_2026-04-16.txt",
      12
    ],
    [
      "run/proofs/batch_raw_v_unknown_trade_lineage_trace_freeze_final_20260501_152651_inspection/extracted_bundle/run/proofs/forced_trade_feature_forensics_2026_04_16.txt",
      12
    ],
    [
      "run/proofs/batch_raw_v_unknown_trade_lineage_trace_freeze_final_20260501_152651_inspection/extracted_bundle/run/proofs/forced_trade_feature_forensics_2026-04-16.txt",
      12
    ],
    [
      "run/proofs/batch_raw_w_reports_hook_lineage_fix_freeze_final_20260501_153007_inspection/extracted_bundle/run/proofs/forced_trade_feature_forensics_2026_04_16.txt",
      12
    ],
    [
      "run/proofs/batch_raw_w_reports_hook_lineage_fix_freeze_final_20260501_153007_inspection/extracted_bundle/run/proofs/forced_trade_feature_forensics_2026-04-16.txt",
      12
    ],
    [
      "run/proofs/batch_raw_n_enriched_rerun_freeze_final_20260501_140812_inspection/extracted_bundle/run/proofs/forced_trade_feature_forensics_2026_04_16.txt",
      12
    ],
    [
      "run/proofs/batch_raw_n_enriched_rerun_freeze_final_20260501_140812_inspection/extracted_bundle/run/proofs/forced_trade_feature_forensics_2026-04-16.txt",
      12
    ],
    [
      "run/proofs/batch_raw_u_deep_constructor_audit_freeze_final_20260501_152209_inspection/extracted_bundle/run/proofs/forced_trade_feature_forensics_2026_04_16.txt",
      12
    ],
    [
      "run/proofs/batch_raw_u_deep_constructor_audit_freeze_final_20260501_152209_inspection/extracted_bundle/run/proofs/forced_trade_feature_forensics_2026-04-16.txt",
      12
    ],
    [
      "run/proofs/batch_raw_n_enriched_rerun_freeze_final_v2_20260501_141141_inspection/extracted_bundle/run/proofs/forced_trade_feature_forensics_2026_04_16.txt",
      12
    ],
    [
      "run/proofs/batch_raw_n_enriched_rerun_freeze_final_v2_20260501_141141_inspection/extracted_bundle/run/proofs/forced_trade_feature_forensics_2026-04-16.txt",
      12
    ],
    [
      "run/proofs/batch_raw_p_repair_true_family_emission_freeze_final_v2_20260501_143008_inspection/extracted_bundle/run/proofs/forced_trade_feature_forensics_2026_04_16.txt",
      12
    ],
    [
      "run/proofs/batch_raw_p_repair_true_family_emission_freeze_final_v2_20260501_143008_inspection/extracted_bundle/run/proofs/forced_trade_feature_forensics_2026-04-16.txt",
      12
    ],
    [
      "run/proofs/call_broader_context_audit_2026-04-16.txt",
      5
    ],
    [
      "run/proofs/call_entry_trend_audit_2026-04-16.txt",
      5
    ],
    [
      "run/proofs/batch_raw_v_unknown_trade_lineage_trace_freeze_final_20260501_152651_inspection/extracted_bundle/run/proofs/call_broader_context_audit_2026-04-16.txt",
      5
    ],
    [
      "run/proofs/batch_raw_v_unknown_trade_lineage_trace_freeze_final_20260501_152651_inspection/extracted_bundle/run/proofs/call_entry_trend_audit_2026-04-16.txt",
      5
    ],
    [
      "run/proofs/batch_raw_w_reports_hook_lineage_fix_freeze_final_20260501_153007_inspection/extracted_bundle/run/proofs/call_broader_context_audit_2026-04-16.txt",
      5
    ],
    [
      "run/proofs/batch_raw_w_reports_hook_lineage_fix_freeze_final_20260501_153007_inspection/extracted_bundle/run/proofs/call_entry_trend_audit_2026-04-16.txt",
      5
    ]
  ]
}
## CSV preview
source_file,row_kind,trade_id,candidate_id,family,strategy_id,side,symbol,instrument_token,selected_strike,entry_time_ist,exit_time_ist,entry_price,exit_price,exit_reason,gross_pnl,net_pnl_after_costs,target_hit_after_block,stop_hit_after_block,missed_trade,false_entry,good_blocker,blocker,remarks
run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl,trade,exports:1,,UNKNOWN,UNKNOWN,UNKNOWN,,,,,,,,,,206.25,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl,trade,exports:2,,UNKNOWN,UNKNOWN,UNKNOWN,,,,,,,,,,206.25,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl,trade,exports:3,,UNKNOWN,UNKNOWN,UNKNOWN,,,,,,,,,,206.25,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl,trade,exports:4,,UNKNOWN,UNKNOWN,UNKNOWN,,,,,,,,,,206.25,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl,trade,exports:5,,UNKNOWN,UNKNOWN,UNKNOWN,,,,,,,,,,206.25,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl,trade,exports:6,,UNKNOWN,UNKNOWN,UNKNOWN,,,,,,,,,,206.25,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl,trade,exports:7,,UNKNOWN,UNKNOWN,UNKNOWN,,,,,,,,,,206.25,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl,trade,exports:8,,UNKNOWN,UNKNOWN,UNKNOWN,,,,,,,,,,206.25,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl,trade,exports:9,,UNKNOWN,UNKNOWN,UNKNOWN,,,,,,,,,,206.25,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl,trade,exports:10,,UNKNOWN,UNKNOWN,UNKNOWN,,,,,,,,,,206.25,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl,trade,exports:11,,UNKNOWN,UNKNOWN,UNKNOWN,,,,,,,,,,-468.75,,,,True,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl,trade,exports:12,,UNKNOWN,UNKNOWN,UNKNOWN,,,,,,,,,,206.25,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl,trade,exports:13,,UNKNOWN,UNKNOWN,UNKNOWN,,,,,,,,,,206.25,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl,trade,exports:14,,UNKNOWN,UNKNOWN,UNKNOWN,,,,,,,,,,206.25,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl,trade,exports:15,,UNKNOWN,UNKNOWN,UNKNOWN,,,,,,,,,,-220.5,,,,True,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl,trade,exports:17,,UNKNOWN,UNKNOWN,UNKNOWN,,,,,,,,,,206.25,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl,trade,exports:18,,UNKNOWN,UNKNOWN,UNKNOWN,,,,,,,,,,82.5,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_y_small_validation_20260501_155332_trade_family_backfill/trade_family_backfilled_records.jsonl,trade,exports:1,RAW_W_EVENT_ID_exports:1,MIST,MIST,CALL,,,,,,,,,,206.25,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_y_small_validation_20260501_155332_trade_family_backfill/trade_family_backfilled_records.jsonl,trade,exports:2,RAW_W_EVENT_ID_exports:2,MISB,MISB,PUT,,,,,,,,,,206.25,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_y_small_validation_20260501_155332_trade_family_backfill/trade_family_backfilled_records.jsonl,trade,exports:3,RAW_W_EVENT_ID_exports:3,MISC,MISC,CALL,,,,,,,,,,206.25,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_y_small_validation_20260501_155332_trade_family_backfill/trade_family_backfilled_records.jsonl,trade,exports:4,RAW_W_EVENT_ID_exports:4,MISR,MISR,CALL,,,,,,,,,,206.25,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_y_small_validation_20260501_155332_trade_family_backfill/trade_family_backfilled_records.jsonl,trade,exports:5,RAW_W_EVENT_ID_exports:5,MISO,MISO,CALL,,,,,,,,,,206.25,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_y_small_validation_20260501_155332_trade_family_backfill/trade_family_backfilled_records.jsonl,trade,exports:6,RAW_W_EVENT_ID_exports:6,MIST,MIST_CALL,CALL,,,,,,,,,,206.25,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_y_small_validation_20260501_155332_trade_family_backfill/trade_family_backfilled_records.jsonl,trade,exports:7,RAW_W_EVENT_ID_exports:7,MIST,MIST_CALL,CALL,,,,,,,,,,206.25,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_y_small_validation_20260501_155332_trade_family_backfill/trade_family_backfilled_records.jsonl,trade,exports:8,RAW_W_EVENT_ID_exports:8,MIST,MIST_CALL,CALL,,,,,,,,,,206.25,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_y_small_validation_20260501_155332_trade_family_backfill/trade_family_backfilled_records.jsonl,trade,exports:9,RAW_W_EVENT_ID_exports:9,MIST,MIST_CALL,CALL,,,,,,,,,,206.25,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_y_small_validation_20260501_155332_trade_family_backfill/trade_family_backfilled_records.jsonl,trade,exports:10,RAW_W_EVENT_ID_exports:10,MIST,MIST_CALL,CALL,,,,,,,,,,206.25,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_y_small_validation_20260501_155332_trade_family_backfill/trade_family_backfilled_records.jsonl,trade,exports:11,RAW_W_EVENT_ID_exports:11,MIST,MIST_CALL,CALL,,,,,,,,,,-468.75,,,,True,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_y_small_validation_20260501_155332_trade_family_backfill/trade_family_backfilled_records.jsonl,trade,exports:12,RAW_W_EVENT_ID_exports:12,MIST,MIST_CALL,CALL,,,,,,,,,,206.25,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_y_small_validation_20260501_155332_trade_family_backfill/trade_family_backfilled_records.jsonl,trade,exports:13,RAW_W_EVENT_ID_exports:13,MIST,MIST_CALL,CALL,,,,,,,,,,206.25,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_y_small_validation_20260501_155332_trade_family_backfill/trade_family_backfilled_records.jsonl,trade,exports:14,RAW_W_EVENT_ID_exports:14,MIST,MIST_CALL,CALL,,,,,,,,,,206.25,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_y_small_validation_20260501_155332_trade_family_backfill/trade_family_backfilled_records.jsonl,trade,exports:15,RAW_W_EVENT_ID_exports:15,MIST,MIST_CALL,CALL,,,,,,,,,,-220.5,,,,True,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_y_small_validation_20260501_155332_trade_family_backfill/trade_family_backfilled_records.jsonl,trade,exports:17,RAW_W_EVENT_ID_exports:17,MIST,MIST_CALL,CALL,,,,,,,,,,206.25,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/replay/raw_y_small_validation_20260501_155332_trade_family_backfill/trade_family_backfilled_records.jsonl,trade,exports:18,RAW_W_EVENT_ID_exports:18,MIST,MIST_CALL,CALL,,,,,,,,,,82.5,,,,,,NO_BLOCKER,RAW-L enriched copy; unknown values are not inferred.
run/proofs/forced_trade_feature_forensics_2026_04_16.txt,,,,,,PUT,NIFTY2642124250PE,,,2026-04-16 11:10:16.768 IST,2026-04-16 11:10:17.772 IST,158.1,157.55,liquidity_exit,-35.75,,,,,,,,
run/proofs/call_broader_context_audit_2026-04-16.txt,,,,,,,NIFTY2642124300CE,,,2026-04-16 11:21:12.667 IST,2026-04-16 11:21:14.677 IST,188.6,188.65,momentum_exit,,,,,,,,,
run/proofs/forced_trade_feature_forensics_2026_04_16.txt,,,,,,CALL,NIFTY2642124300CE,,,2026-04-16 11:21:12.667 IST,2026-04-16 11:21:14.677 IST,188.6,188.65,momentum_exit,3.25,,,,,,,,
run/proofs/forced_trade_feature_forensics_2026_04_16.txt,,,,,,PUT,NIFTY2642124300PE,,,2026-04-16 11:40:51.098 IST,2026-04-16 11:40:53.116 IST,208.05,207.65,momentum_exit,-26.0,,,,,,,,
run/proofs/forced_trade_feature_forensics_2026_04_16.txt,,,,,,PUT,NIFTY2642124300PE,,,2026-04-16 11:55:53.311 IST,2026-04-16 11:55:55.324 IST,234.4,233.4,momentum_exit,-65.0,,,,,,,,
