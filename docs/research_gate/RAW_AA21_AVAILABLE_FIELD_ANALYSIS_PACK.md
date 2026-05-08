# RAW-AA21 — Available Field Analysis Pack

generated_at_utc: 2026-05-02T07:35:13.123299+00:00

## Verdict

Available-field analysis pack generated. This is descriptive RAW research only.

## Source

- rows: `55677`
- recognized_family_rows: `29109`

## Family counts

```json
{
  "MISB": 5740,
  "MISC": 5740,
  "MISO": 5823,
  "MISR": 5740,
  "MIST": 6066,
  "UNKNOWN": 26568
}
```

## Top family-side rows

- `UNKNOWN` / `UNKNOWN`: `15457` rows
- `UNKNOWN` / `CALL`: `9134` rows
- `MIST` / `CALL`: `3146` rows
- `MISB` / `PUT`: `2854` rows
- `MISR` / `CALL`: `2761` rows
- `MISO` / `CALL`: `2761` rows
- `MISC` / `CALL`: `2761` rows
- `MISB` / `CALL`: `2761` rows
- `MIST` / `PUT`: `2750` rows
- `MISR` / `PUT`: `2750` rows

## Safety interpretation

- Observed `net_pnl_after_costs` remains observed-only.
- No reward_cost_ratio derivation.
- No OI wall derivation.
- No PnL lifecycle reconstruction.
- No row mutation.
- No paper/live enablement.

## Outputs

- analysis_json: `run/research_gate/raw_aa21_available_field_analysis_pack_20260502_130513/raw_aa21_available_field_analysis_pack.json`
- family_rank_csv: `run/research_gate/raw_aa21_available_field_analysis_pack_20260502_130513/raw_aa21_family_side_rank.csv`
- economics_rank_csv: `run/research_gate/raw_aa21_available_field_analysis_pack_20260502_130513/raw_aa21_economics_tick_rank.csv`
- observed_pnl_rank_csv: `run/research_gate/raw_aa21_available_field_analysis_pack_20260502_130513/raw_aa21_observed_net_pnl_rank.csv`
