# RAW-AA13A Doctrine/Economics Source Resolver

created_at_utc: 2026-05-02T05:35:44.114406+00:00
verdict: `RAW_AA13A_DOCTRINE_ECONOMICS_SOURCE_RESOLVER_READY`
blockers: `['UNRESOLVED_TARGET_STOP_TICK_AUTHORITY_FOR:MIST,MISB,MISC,MISR,MISO']`
next_recommendation: `RAW_AA13A_R2_MISSING_AUTHORITY_RESCAN`

## Safety

- no patching
- no replay execution
- no broker IO
- no live Redis writes
- no order sending
- no paper/live enablement

## Family authority resolution

| family | target_points | stop_points | tick_size | target_ticks_derivable | stop_ticks_derivable |
|---|---:|---:|---:|---:|---:|
| MIST | [0.0, 5.0] | [0.0, 4.0] | [0.05] | False | False |
| MISB | [0.0, 5.0] | [0.0, 4.0] | [0.05] | False | False |
| MISC | [0.0, 5.0] | [0.0, 4.0] | [0.05] | False | False |
| MISR | [0.0, 5.0] | [0.0, 4.0] | [0.05] | False | False |
| MISO | [0.0, 5.0] | [0.0, 4.0] | [0.05] | False | False |

## OI wall resolution

OI wall strength/distance remains unavailable unless explicit fields or OI-ladder formula/context is proven.

## Outputs

- proof: `run/proofs/proof_raw_aa13a_doctrine_economics_source_resolver.json`
- freeze: `run/proofs/proof_raw_aa13a_freeze_final.json`
- doc: `docs/research_gate/RAW_AA13A_DOCTRINE_ECONOMICS_SOURCE_RESOLVER.md`
- milestone: `docs/milestones/batch_raw_aa13a_doctrine_economics_source_resolver_20260502_110544.md`
- run_dir: `run/research_gate/raw_aa13a_doctrine_economics_source_resolver_20260502_110544`
