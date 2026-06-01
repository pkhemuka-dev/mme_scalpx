# B1-PROFIT-LIVE-R38B_PROVIDER_RUNTIME_CLASSIC_ZERODHA_SELECTED_OPTION_FALLBACK_PATCH_NO_ORDER

Classification: **PASS_R38B_PROVIDER_RUNTIME_SELECTED_OPTION_ZERODHA_FALLBACK_PATCH_NO_ORDER**

## Patch

- Target: `app/mme_scalpx/integrations/provider_runtime.py`
- Backup: `run/_code_backups/B1-PROFIT-LIVE-R38B_PROVIDER_RUNTIME_CLASSIC_ZERODHA_SELECTED_OPTION_FALLBACK_PATCH_NO_ORDER_patch_manual_failover_selected_option_to_zerodha_when_dhan_unavailable_no_start_no_order_20260528_221023_provider_runtime.py.before`
- Patch RC: 0
- Compile OK: true
- Marker count: 1
- Dangerous marker count: 0

## Doctrine preserved

- Classic families may use Zerodha selected-option when Dhan selected-option is unavailable.
- MISO remains blocked without Dhan context.
- Option context remains Dhan.
- Execution provider unchanged.
- No risk/execution/order/paper enablement.

## Safety after

- orders=0
- risk_stream=0
- execution_stream=0
- risk_pids=0
- execution_pids=0

Proof: `run/proofs/B1-PROFIT-LIVE-R38B_PROVIDER_RUNTIME_CLASSIC_ZERODHA_SELECTED_OPTION_FALLBACK_PATCH_NO_ORDER_patch_manual_failover_selected_option_to_zerodha_when_dhan_unavailable_no_start_no_order_20260528_221023.json`
