# B1-PROFIT-LIVE-R37Q_R38A_AFTERMARKET_DATA_ADMISSION_AND_PROVIDER_FALLBACK_AUDIT_NO_PATCH_NO_START_NO_ORDER

Classification: **BLOCKED_R37Q_DATA_ADMISSION_INCOMPLETE_NO_ORDER**

## Data admission
- pseal_pass: False
- r37m_present: True
- r37m_stopped: True
- fut_zerodha_ok: True
- opt_selected_zerodha_ok: True
- features_ok: True
- decisions_ok: True
- safety_clean: True
- dhan_absent_expected: True

## Final recorder counts
- fut_zerodha: 9822
- opt_selected_zerodha: 53471
- features: 7971
- decisions: 63095
- health: 200026
- errors: 332
- fut_dhan: 0
- opt_selected_dhan: 0
- opt_context_dhan: 0

## PSeal
- classification: None
- read_only: None
- outdir: None

## Safety
```json
{
  "orders": "0",
  "risk_stream": "0",
  "execution_stream": "0",
  "risk_pids": 0,
  "execution_pids": 0
}
```

## Provider fallback patch plan
- Classic families: MIST/MISB/MISC/MISR should be allowed to use fresh Zerodha selected-option data when Dhan selected option/context is unavailable.
- MISO remains blocked until Dhan context/ladder is healthy.
- Execution provider must not change.
- No paper/live/order enablement in the patch.

## Next
Run R38B patch only after reviewing this report.

Proof: `run/proofs/B1-PROFIT-LIVE-R37Q_R38A_AFTERMARKET_DATA_ADMISSION_AND_PROVIDER_FALLBACK_AUDIT_NO_PATCH_NO_START_NO_ORDER_verify_r37m_capture_pseal_and_prepare_classic_zerodha_fallback_patch_plan_20260528_215320.json`
Audit: `run/audits/B1-PROFIT-LIVE-R37Q_R38A_AFTERMARKET_DATA_ADMISSION_AND_PROVIDER_FALLBACK_AUDIT_NO_PATCH_NO_START_NO_ORDER_verify_r37m_capture_pseal_and_prepare_classic_zerodha_fallback_patch_plan_20260528_215320_audit.json`
