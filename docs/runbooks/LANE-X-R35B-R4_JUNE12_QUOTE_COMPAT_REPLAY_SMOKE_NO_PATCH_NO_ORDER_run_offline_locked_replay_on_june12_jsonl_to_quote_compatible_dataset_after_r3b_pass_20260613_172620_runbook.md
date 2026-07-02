# LANE-X-R35B-R4_JUNE12_QUOTE_COMPAT_REPLAY_SMOKE_NO_PATCH_NO_ORDER_run_offline_locked_replay_on_june12_jsonl_to_quote_compatible_dataset_after_r3b_pass_20260613_172620

classification: REVIEW_R35B_R4_JUNE12_QUOTE_COMPAT_REPLAY_INCOMPLETE_OR_SAFETY_NOT_CLEAN_NO_ORDER
proof: `run/proofs/LANE-X-R35B-R4_JUNE12_QUOTE_COMPAT_REPLAY_SMOKE_NO_PATCH_NO_ORDER_run_offline_locked_replay_on_june12_jsonl_to_quote_compatible_dataset_after_r3b_pass_20260613_172620.json`
dataset_root: `run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413`
run_root: `run/replay/lane_x_r35b_june12_quote_compat/LANE-X-R35B-R4_JUNE12_QUOTE_COMPAT_REPLAY_SMOKE_NO_PATCH_NO_ORDER_run_offline_locked_replay_on_june12_jsonl_to_quote_compatible_dataset_after_r3b_pass_20260613_172620`
replay_log: `run/audits/LANE-X-R35B-R4_JUNE12_QUOTE_COMPAT_REPLAY_SMOKE_NO_PATCH_NO_ORDER_run_offline_locked_replay_on_june12_jsonl_to_quote_compatible_dataset_after_r3b_pass_20260613_172620/replay.log`
inspect_json: `run/audits/LANE-X-R35B-R4_JUNE12_QUOTE_COMPAT_REPLAY_SMOKE_NO_PATCH_NO_ORDER_run_offline_locked_replay_on_june12_jsonl_to_quote_compatible_dataset_after_r3b_pass_20260613_172620/replay_inspect_summary.json`

## Safety
- PRE orders/risk/execution: 0 / 0 / 0
- POST orders/risk/execution: 0 / 0 / 0
- PRE risk/execution proc: 0 / 0
- POST risk/execution proc: 0 / 0

## RCs
- compile_rc: 0
- replay_rc: 1
- inspect_rc: 0

## Dataset shape
DATASET_ROOT=run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413
DAY=2026-06-12

Dataset declaration:
{
  "broker_order_attempted": false,
  "created_by": "LANE-X-R35B-R3B",
  "dataset_id": "LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413",
  "declaration_version": "v1",
  "feed_input_source_mode": "quote_only_recorded",
  "paper_live_enabled": false,
  "required_file_stems": [
    "quote_ticks_mme_fut_stream",
    "quote_ticks_mme_opt_stream"
  ],
  "source_mode": "quote_only_recorded",
  "supported_scopes": [
    "feeds_only",
    "feeds_features",
    "feeds_features_strategy",
    "feeds_features_strategy_risk",
    "feeds_features_strategy_risk_execution_shadow"
  ],
  "supported_suffixes": [
    ".csv",
    "csv"
  ]
}
Dataset files:
run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413/2026-06-12/quote_ticks_mme_fut_stream.csv 2285257 bytes
run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413/2026-06-12/quote_ticks_mme_opt_stream.csv 11907659 bytes
run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413/2026-06-12/source_manifest.json 2330 bytes
run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413/replay_dataset_declaration.json 774 bytes

CSV headers:
ts_event,symbol,bid,ask,ltp,instrument_token,instrument_key,provider_id,source_stream,source_id
ts_event,symbol,bid,ask,ltp,instrument_token,instrument_key,provider_id,source_stream,source_id

## Replay log tail
Traceback (most recent call last):
  File "/home/Lenovo/scalpx/projects/mme_scalpx/bin/replay_run.py", line 3529, in <module>
    raise SystemExit(main(sys.argv[1:]))
  File "/home/Lenovo/scalpx/projects/mme_scalpx/bin/replay_run.py", line 3362, in main
    engine_result = engine.execute(
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/replay/engine.py", line 199, in execute
    self._execute_stage(context, stage, stage_executor)
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/replay/engine.py", line 477, in _batch16_execute_stage
    return _BATCH16_ORIGINAL_EXECUTE_STAGE(self, context, stage, guarded_executor)
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/replay/engine.py", line 239, in _execute_stage
    raw_output = stage_executor(context, stage)
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/replay/engine.py", line 468, in guarded_executor
    raw = stage_executor(ctx, st)
  File "/home/Lenovo/scalpx/projects/mme_scalpx/bin/replay_run.py", line 3131, in stage_executor
    decisions = build_strategy_decisions_from_feature_frames(
  File "/home/Lenovo/scalpx/projects/mme_scalpx/bin/replay_run.py", line 2056, in build_strategy_decisions_from_feature_frames
    result = _r31a_strategy_adapter(run_id=str(run_id), feature_payload=feature_payload)
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/replay/strategy_adapter.py", line 237, in build_replay_strategy_decision_payload
    "candidate_json": _canonical_json(candidates),
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/replay/strategy_adapter.py", line 73, in _canonical_json
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
  File "/usr/lib/python3.10/json/__init__.py", line 238, in dumps
    **kw).encode(obj)
  File "/usr/lib/python3.10/json/encoder.py", line 199, in encode
    chunks = self.iterencode(o, _one_shot=True)
  File "/usr/lib/python3.10/json/encoder.py", line 257, in iterencode
    return _iterencode(o, 0)
KeyboardInterrupt

## Inspect summary
{
  "action_counts": {},
  "candidate_count": null,
  "csv_counts": {},
  "execution_shadow_filled": null,
  "exists": true,
  "family_counts": {},
  "file_count": 0,
  "files": [],
  "json_summaries": {},
  "pnl_total": null,
  "risk_non_hold": null,
  "run_root": "run/replay/lane_x_r35b_june12_quote_compat/LANE-X-R35B-R4_JUNE12_QUOTE_COMPAT_REPLAY_SMOKE_NO_PATCH_NO_ORDER_run_offline_locked_replay_on_june12_jsonl_to_quote_compatible_dataset_after_r3b_pass_20260613_172620",
  "trade_count": null
}