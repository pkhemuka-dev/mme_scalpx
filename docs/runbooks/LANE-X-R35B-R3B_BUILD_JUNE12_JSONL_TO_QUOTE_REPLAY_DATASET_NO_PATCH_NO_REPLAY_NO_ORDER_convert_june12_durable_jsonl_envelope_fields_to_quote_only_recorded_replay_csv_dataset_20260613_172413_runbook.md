# LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413

classification: PASS_R35B_R3B_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_BUILT_SAFETY_CLEAN_NO_PATCH_NO_REPLAY_NO_ORDER
proof: `run/proofs/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413.json`
src_day_root: `run/staging/LANE-X-R35B0-R3_JUNE_STAGING_SIZE_QUALITY_REPAIR_NO_PATCH_NO_REPLAY_NO_ORDER_grade_r35b0_r2_stage_by_file_size_and_rebuild_preferred_stage_using_durable_when_pseal_streams_are_tiny_20260613_170904/2026-06-12`
dst_root: `run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413`
adapter: `run/patches/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413_jsonl_to_quote_dataset.py`
inspect_json: `run/audits/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413/jsonl_to_quote_dataset_inspect.json`

## Safety
- PRE orders/risk/execution: 0 / 0 / 0
- POST orders/risk/execution: 0 / 0 / 0
- PRE risk/execution proc: 0 / 0
- POST risk/execution proc: 0 / 0

## Build result
- adapter_compile_rc: 0
- build_rc: 0
- fut_rows: 16440
- opt_rows: 79076

## Dataset files
run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413/2026-06-12/quote_ticks_mme_fut_stream.csv 2285257 bytes
run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413/2026-06-12/quote_ticks_mme_opt_stream.csv 11907659 bytes
run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413/2026-06-12/source_manifest.json 2330 bytes
run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413/replay_dataset_declaration.json 774 bytes

## Inspect
{
  "day": "2026-06-12",
  "day_root": "run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413/2026-06-12",
  "declaration": {
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
  },
  "dst_root": "run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413",
  "files": {
    "quote_ticks_mme_fut_stream.csv": {
      "dst": "run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413/2026-06-12/quote_ticks_mme_fut_stream.csv",
      "missing": {
        "ask": 0,
        "bid": 0,
        "ltp": 0,
        "symbol": 0,
        "ts_event": 0
      },
      "rows_in_sampled": 16440,
      "rows_out": 16440,
      "src": "run/staging/LANE-X-R35B0-R3_JUNE_STAGING_SIZE_QUALITY_REPAIR_NO_PATCH_NO_REPLAY_NO_ORDER_grade_r35b0_r2_stage_by_file_size_and_rebuild_preferred_stage_using_durable_when_pseal_streams_are_tiny_20260613_170904/2026-06-12/fut_zerodha.jsonl.gz"
    },
    "quote_ticks_mme_opt_stream.csv": {
      "dst": "run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413/2026-06-12/quote_ticks_mme_opt_stream.csv",
      "missing": {
        "ask": 0,
        "bid": 0,
        "ltp": 0,
        "symbol": 0,
        "ts_event": 0
      },
      "rows_in_sampled": 79076,
      "rows_out": 79076,
      "src": "run/staging/LANE-X-R35B0-R3_JUNE_STAGING_SIZE_QUALITY_REPAIR_NO_PATCH_NO_REPLAY_NO_ORDER_grade_r35b0_r2_stage_by_file_size_and_rebuild_preferred_stage_using_durable_when_pseal_streams_are_tiny_20260613_170904/2026-06-12/opt_selected_zerodha.jsonl.gz"
    }
  },
  "preview": {
    "fut": {
      "exists": true,
      "fieldnames": [
        "ts_event",
        "symbol",
        "bid",
        "ask",
        "ltp",
        "instrument_token",
        "instrument_key",
        "provider_id",
        "source_stream",
        "source_id"
      ],
      "path": "run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413/2026-06-12/quote_ticks_mme_fut_stream.csv",
      "rows": [
        {
          "ask": "23393.0",
          "bid": "23388.1",
          "instrument_key": "NFO:NIFTY26JUNFUT",
          "instrument_token": "15956226",
          "ltp": "23393.7",
          "provider_id": "ZERODHA",
          "source_id": "1781238986660-0",
          "source_stream": "ticks:mme:fut:zerodha:stream",
          "symbol": "NIFTY26JUNFUT",
          "ts_event": "1781258784000000000"
        },
        {
          "ask": "23394.0",
          "bid": "23390.0",
          "instrument_key": "NFO:NIFTY26JUNFUT",
          "instrument_token": "15956226",
          "ltp": "23393.5",
          "provider_id": "ZERODHA",
          "source_id": "1781238993570-0",
          "source_stream": "ticks:mme:fut:zerodha:stream",
          "symbol": "NIFTY26JUNFUT",
          "ts_event": "1781258792000000000"
        },
        {
          "ask": "23395.0",
          "bid": "23389.9",
          "instrument_key": "NFO:NIFTY26JUNFUT",
          "instrument_token": "15956226",
          "ltp": "23390.0",
          "provider_id": "ZERODHA",
          "source_id": "1781238999550-0",
          "source_stream": "ticks:mme:fut:zerodha:stream",
          "symbol": "NIFTY26JUNFUT",
          "ts_event": "1781258797000000000"
        }
      ],
      "size": 2285257
    },
    "opt": {
      "exists": true,
      "fieldnames": [
        "ts_event",
        "symbol",
        "bid",
        "ask",
        "ltp",
        "instrument_token",
        "instrument_key",
        "provider_id",
        "source_stream",
        "source_id"
      ],
      "path": "run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413/2026-06-12/quote_ticks_mme_opt_stream.csv",
      "rows": [
        {
          "ask": "132.45",
          "bid": "132.25",
          "instrument_key": "NFO:NIFTY2661623350PE",
          "instrument_token": "12946690",
          "ltp": "132.6",
          "provider_id": "ZERODHA",
          "source_id": "1781238982862-0",
          "source_stream": "ticks:mme:opt:selected:zerodha:stream",
          "symbol": "NIFTY2661623350PE",
          "ts_event": "1781258782000000000"
        },
        {
          "ask": "151.4",
          "bid": "151.15",
          "instrument_key": "NFO:NIFTY2661623350CE",
          "instrument_token": "12946434",
          "ltp": "151.15",
          "provider_id": "ZERODHA",
          "source_id": "1781238983397-0",
          "source_stream": "ticks:mme:opt:selected:zerodha:stream",
          "symbol": "NIFTY2661623350CE",
          "ts_event": "1781258782000000000"
        },
        {
          "ask": "132.15",
          "bid": "131.8",
          "instrument_key": "NFO:NIFTY2661623350PE",
          "instrument_token": "12946690",
          "ltp": "132.2",
          "provider_id": "ZERODHA",
          "source_id": "1781238984325-0",
          "source_stream": "ticks:mme:opt:selected:zerodha:stream",
          "symbol": "NIFTY2661623350PE",
          "ts_event": "1781258783000000000"
        }
      ],
      "size": 11907659
    }
  },
  "schema": "jsonl_envelope_to_quote_only_recorded_replay_dataset_v1",
  "src_day_root": "run/staging/LANE-X-R35B0-R3_JUNE_STAGING_SIZE_QUALITY_REPAIR_NO_PATCH_NO_REPLAY_NO_ORDER_grade_r35b0_r2_stage_by_file_size_and_rebuild_preferred_stage_using_durable_when_pseal_streams_are_tiny_20260613_170904/2026-06-12"
}
