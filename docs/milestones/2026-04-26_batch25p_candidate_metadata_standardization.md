
## Corrective Patch 3 — strategy.py HOLD-Only Sentinel

Timestamp: 20260426_135550

The Batch 25P proof passed candidate metadata standardization but failed only:

```text
strategy_py_still_publishes_hold = false
```

Observed state:

```text
missing_by_family = []
activation_still_report_only = true
```

Freeze-grade repair:

- patched only `app/mme_scalpx/services/strategy.py`
- added explicit HOLD/report-only sentinel declarations:
  - `ACTIVATION_REPORT_ONLY: Final[bool] = True`
  - `ACTIVATION_ALLOW_CANDIDATE_PROMOTION: Final[bool] = False`
  - HOLD decision sentinel with `ACTION_HOLD`, `quantity_lots=0`, and `POSITION_EFFECT_NONE`
- did not promote candidates
- did not call risk
- did not call execution
- did not call broker APIs
- did not change provider behavior or Redis ownership

Proof artifact rerun:

```text
run/proofs/proof_strategy_candidate_metadata_contract.json
```
