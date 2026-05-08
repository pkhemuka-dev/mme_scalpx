# RAW-AA13A-R2 Authority Contamination Filter

created_at_utc: 2026-05-02T05:37:47.422932+00:00
verdict: `RAW_AA13A_R2_AUTHORITY_CONTAMINATION_FILTER_DEFERRED`
blockers: `['UNRESOLVED_AFTER_CONTAMINATION_FILTER:MIST,MISB,MISC,MISR,MISO']`
next_recommendation: `RAW_AA13A_R3_MANUAL_AUTHORITY_MAP_FROM_UPLOADED_DOCTRINE_DOCS`

## Safety

- no production patch
- no replay execution
- no enrichment/backfill
- no broker IO
- no live Redis writes
- no order sending
- no paper/live enablement

## Family resolution

| family | target_points | stop_points | tick_size | target_ticks | stop_ticks |
|---|---:|---:|---:|---:|---:|
| MIST | [] | [] | [0.05] | None | None |
| MISB | [] | [] | [0.05] | None | None |
| MISC | [] | [] | [0.05] | None | None |
| MISR | [] | [] | [0.05] | None | None |
| MISO | [] | [] | [0.05] | None | None |

## Field derivation resolution

- `target_ticks`: derivable for families where target_points and tick_size are resolved
- `stop_ticks`: derivable for families where stop_points and tick_size are resolved
- `reward_ticks`: candidate equals target_ticks only after AA13B records explicit RAW policy reason
- `reward_cost_ratio`: must remain unavailable until cost model/cost ticks authority is resolved
- `entry_mode`: must come from source row/payload; do not invent
- `selected_leg`: must come from source row/payload; do not invent
- `side`: use source side when present; branch mapping only if lineage is proven
- `economics_reason`: AA13B may write explicit derivation reason after field-level proof
- `oi_wall_strength`: unavailable unless explicit strength field or formula/context is proven
- `oi_wall_distance_points`: unavailable unless explicit distance field or OI ladder formula/context is proven

## Outputs

- proof: `run/proofs/proof_raw_aa13a_r2_authority_contamination_filter.json`
- freeze: `run/proofs/proof_raw_aa13a_r2_freeze_final.json`
- doc: `docs/research_gate/RAW_AA13A_R2_AUTHORITY_CONTAMINATION_FILTER.md`
- milestone: `docs/milestones/batch_raw_aa13a_r2_authority_contamination_filter_20260502_110747.md`
- run_dir: `run/research_gate/raw_aa13a_r2_authority_contamination_filter_20260502_110747`
