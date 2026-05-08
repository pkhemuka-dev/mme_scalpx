# RAW-AA18-R2 — Field Readiness Matrix Source Repair

generated_at_utc: 2026-05-02T07:30:00.225665+00:00

## Verdict

RAW field readiness matrix has been recalculated from the actual AA14/AA13B derived CSV source.

## Summary

- source_csv: `run/research_gate/raw_aa13b_r4_explicit_output_export_resolver_20260502_111828/enriched_replay_records_aa13b_r4_input_normalized_economics_derived.csv`
- row_count: `55677`
- recognized_family_rows: `29109`
- ready_count: `7`
- partial_count: `1`
- gated_count: `3`
- unavailable_count: `9`
- observed_only_count: `1`

## Still gated

- `reward_cost_ratio` — Cost model is not authorized; reward_cost_ratio not derived or written.
- `oi_wall_strength` — Raw OI/strike/expiry fields alone are not sufficient authority.
- `oi_wall_distance_points` — Raw OI/strike/expiry fields alone are not sufficient authority.

## Promotion firewall

- RAW does not trade.
- RAW does not mutate live production truth.
- RAW does not enable paper/live.
- RAW does not write live Redis.
- RAW does not send orders.

## Outputs

- matrix: `run/research_gate/raw_aa18_r2_field_readiness_matrix_source_repair_20260502_130000/raw_aa18_r2_field_readiness_matrix_source_repaired.json`
- csv_counts: `run/research_gate/raw_aa18_r2_field_readiness_matrix_source_repair_20260502_130000/raw_aa18_r2_csv_field_counts.json`
- policy: `etc/research_gate/raw_research_gate_promotion_firewall_policy_r2.json`
