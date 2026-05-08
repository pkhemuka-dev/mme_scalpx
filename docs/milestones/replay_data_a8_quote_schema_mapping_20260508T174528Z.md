# REPLAY-DATA-A8 — quote_only_recorded schema mapping audit

- Created UTC: `20260508T174528Z`
- Input A7 proof: `/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/proof_replay_data_a7_sandbox_canonical_day_dataset_20260508T173739Z.json`
- Canonical root: `/home/Lenovo/scalpx/projects/mme_scalpx/run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z`
- Verdict: `BLOCKED_MISSING_REQUIRED_FIELDS`
- Adapter mapping possible: `False`
- Missing required fields: `ask, bid, symbol, ts_event`

## Required quote_only_recorded fields

ts_event, symbol, bid, ask

## Per-file missing required fields

- `ticks_mme_fut_stream`: `ts_event, symbol, bid, ask`
- `ticks_mme_opt_stream`: `ts_event, symbol, bid, ask`

## Mapping plan

### ticks_mme_fut_stream
- `ts_event` -> `UNMAPPED`
- `symbol` -> `UNMAPPED`
- `bid` -> `UNMAPPED`
- `ask` -> `UNMAPPED`
- `ltp` -> `UNMAPPED`
- `last` -> `UNMAPPED`
- `price` -> `UNMAPPED`
- `bid_qty` -> `UNMAPPED`
- `ask_qty` -> `UNMAPPED`
- `volume` -> `UNMAPPED`
- `oi` -> `UNMAPPED`
- `provider` -> `UNMAPPED`
- `instrument_token` -> `UNMAPPED`

### ticks_mme_opt_stream
- `ts_event` -> `UNMAPPED`
- `symbol` -> `UNMAPPED`
- `bid` -> `UNMAPPED`
- `ask` -> `UNMAPPED`
- `ltp` -> `UNMAPPED`
- `last` -> `UNMAPPED`
- `price` -> `UNMAPPED`
- `bid_qty` -> `UNMAPPED`
- `ask_qty` -> `UNMAPPED`
- `volume` -> `UNMAPPED`
- `oi` -> `UNMAPPED`
- `provider` -> `UNMAPPED`
- `instrument_token` -> `UNMAPPED`

## Safety

- Audit only.
- No data transformation.
- No replay engine run.
- No replay code patch.
- No order placement or paper/live enablement.

Proof JSON: `/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/proof_replay_data_a8_quote_schema_mapping_20260508T174528Z.json`
