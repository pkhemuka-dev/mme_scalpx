# RAW-AA19 — Available Fields Research Report

generated_at_utc: 2026-05-02T07:31:32.175988+00:00

## Verdict

Research report generated using available fields only. Promotion remains blocked.

## Source

- source_csv: `run/research_gate/raw_aa13b_r4_explicit_output_export_resolver_20260502_111828/enriched_replay_records_aa13b_r4_input_normalized_economics_derived.csv`
- rows: `55677`
- recognized_family_rows: `29109`

## Available fields used

- `economics_reason`
- `raw_economics_ready`
- `reward_ticks`
- `side`
- `stop_ticks`
- `target_ticks`
- `trade_family`

## Partial field used cautiously

- `selected_leg` — partial coverage only

## Observed-only field

- `net_pnl_after_costs` — observed only; not reconstructed; not lifecycle truth

## Gated fields not used

- `oi_wall_distance_points`
- `oi_wall_strength`
- `reward_cost_ratio`

## Unavailable fields not used

- `costs`
- `entry_mode`
- `entry_price`
- `entry_ts`
- `exit_price`
- `exit_reason`
- `exit_ts`
- `gross_pnl`
- `qty`

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

## RAW safety

- No row mutation.
- No reward_cost_ratio derivation.
- No OI wall derivation.
- No PnL reconstruction.
- No replay execution.
- No broker IO.
- No live Redis writes.
- No paper/live enablement.

## Outputs

- report_json: `run/research_gate/raw_aa19_available_fields_research_report_20260502_130132/raw_aa19_available_fields_research_report.json`
- family_side_csv: `run/research_gate/raw_aa19_available_fields_research_report_20260502_130132/raw_aa19_family_side_counts.csv`
- economics_csv: `run/research_gate/raw_aa19_available_fields_research_report_20260502_130132/raw_aa19_economics_tick_summary.csv`
- observed_pnl_csv: `run/research_gate/raw_aa19_available_fields_research_report_20260502_130132/raw_aa19_observed_net_pnl_summary.csv`
- coverage_json: `run/research_gate/raw_aa19_available_fields_research_report_20260502_130132/raw_aa19_field_coverage_report.json`
