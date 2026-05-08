# RAW-AA13A-R3 Manual Doctrine Authority Map

created_at_utc: 2026-05-02T05:40:38.358455+00:00
verdict: `RAW_AA13A_R3_MANUAL_AUTHORITY_MAP_READY`
blockers: `[]`
next_recommendation: `RAW_AA13B_ECONOMICS_DERIVATION_IMPLEMENTATION`

## Safety

- RAW/research_gate artifact only
- no production strategy code patch
- no replay execution
- no enrichment/backfill
- no broker IO
- no live Redis writes
- no order sending
- no paper/live enablement

## Authority map

| family | target_points | hard_stop_points | tick_size | target_ticks | stop_ticks | reward_cost_ratio |
|---|---:|---:|---:|---:|---:|---|
| MIST | 5.0 | 4.0 | 0.05 | 100 | 80 | unavailable_until_explicit_cost_model_is_proven |
| MISB | 5.0 | 4.0 | 0.05 | 100 | 80 | unavailable_until_explicit_cost_model_is_proven |
| MISC | 5.0 | 4.0 | 0.05 | 100 | 80 | unavailable_until_explicit_cost_model_is_proven |
| MISR | 5.0 | 4.0 | 0.05 | 100 | 80 | unavailable_until_explicit_cost_model_is_proven |
| MISO | 5.0 | 4.0 | 0.05 | 100 | 80 | unavailable_until_explicit_cost_model_is_proven |

## OI wall

OI wall strength and distance remain unavailable until explicit fields or OI-ladder formula/context are proven.

## Outputs

- authority_map: `etc/research_gate/raw_doctrine_economics_authority_map.json`
- proof: `run/proofs/proof_raw_aa13a_r3_manual_doctrine_authority_map.json`
- freeze: `run/proofs/proof_raw_aa13a_r3_freeze_final.json`
- doc: `docs/research_gate/RAW_AA13A_R3_MANUAL_DOCTRINE_AUTHORITY_MAP.md`
- milestone: `docs/milestones/batch_raw_aa13a_r3_manual_doctrine_authority_map_20260502_111038.md`
- run_dir: `run/research_gate/raw_aa13a_r3_manual_doctrine_authority_map_20260502_111038`
