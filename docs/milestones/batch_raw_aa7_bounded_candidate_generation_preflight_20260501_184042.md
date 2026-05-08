# RAW-AA7 Bounded Candidate Generation Preflight

created_at_utc: 2026-05-01T13:10:42.151708+00:00

## Verdict

- raw_aa7_freeze_final_ok: `True`
- planning_verdict: `RAW_AA7_BOUNDED_CANDIDATE_PREFLIGHT_BLOCKED`
- preflight_ready: `False`
- preflight_blockers: `['MISSING_RAW_ENRICHMENT_ENTRYPOINT']`
- validation_only: `true`
- preflight_only: `true`
- patching_performed: `false`

## Candidate plan

- candidate_dir: `run/replay/raw_aa7_larger_balanced_candidate_20260501_184042`
- candidate_enrich_dir: `run/replay/raw_aa7_larger_balanced_candidate_20260501_184042_enriched`
- candidate_backfill_dir: `run/replay/raw_aa7_larger_balanced_candidate_20260501_184042_trade_family_backfill`

## Safety

No live runtime, broker IO, Redis live writes, order sending, strategy/risk/execution mutation, replay execution, export execution, backfill execution, raw enrichment execution, promotion, or paper/live enablement.