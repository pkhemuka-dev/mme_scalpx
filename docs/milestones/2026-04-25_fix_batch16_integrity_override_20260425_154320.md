# Fix Batch16 Integrity Override — 2026-04-25

## Purpose
Fix Batch16 override that forced placeholder PASS integrity checks to aggregate FAIL.

## Root cause
app/mme_scalpx/replay/integrity.py had a later compute_integrity_verdict override:

```python
if any(_batch16_is_placeholder_pass(result) for result in results):
    return IntegrityVerdict.FAIL
```

This overrode the original correct aggregate rule.

## Patch
Changed Batch16 override to aggregate by actual verdict values:
- any fail => fail
- else any warn => warn
- else all pass => pass

## Safety note
This does not prove live readiness. It only makes replay integrity artifact verdict consistent with executed check results.

## Artifacts
- run/proofs/fix_batch16_integrity_override_20260425_154320/verify_after_batch16_override_patch.log
- run/replay_audits/fix_batch16_integrity_override_20260425_154320
