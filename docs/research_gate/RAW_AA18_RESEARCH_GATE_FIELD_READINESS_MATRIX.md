# RAW-AA18 — Research Gate Field Readiness Matrix

generated_at_utc: 2026-05-02T07:28:44.055661+00:00

## Verdict

RAW field readiness is consolidated. Promotion remains blocked.

## Summary

- rows: `0`
- recognized_family_rows: `0`
- ready_count: `0`
- partial_count: `0`
- gated_count: `3`
- unavailable_count: `17`
- observed_only_count: `1`

## Gated fields

- `reward_cost_ratio` — Cost model is not authorized; reward_cost_ratio not derived or written.
- `oi_wall_strength` — Raw OI/strike/expiry fields alone are not sufficient authority.
- `oi_wall_distance_points` — Raw OI/strike/expiry fields alone are not sufficient authority.

## Unavailable fields

- `trade_family`
- `side`
- `target_ticks`
- `stop_ticks`
- `reward_ticks`
- `raw_economics_ready`
- `economics_reason`
- `selected_leg`
- `entry_mode`
- `entry_price`
- `exit_price`
- `qty`
- `gross_pnl`
- `costs`
- `exit_reason`
- `entry_ts`
- `exit_ts`

## Promotion firewall

- RAW does not trade.
- RAW does not mutate live production truth.
- RAW does not enable paper/live.
- RAW does not write live Redis.
- RAW does not send orders.

## Outputs

- matrix: `run/research_gate/raw_aa18_research_gate_field_readiness_matrix_20260502_125844/raw_aa18_field_readiness_matrix.json`
- policy: `etc/research_gate/raw_research_gate_promotion_firewall_policy.json`
