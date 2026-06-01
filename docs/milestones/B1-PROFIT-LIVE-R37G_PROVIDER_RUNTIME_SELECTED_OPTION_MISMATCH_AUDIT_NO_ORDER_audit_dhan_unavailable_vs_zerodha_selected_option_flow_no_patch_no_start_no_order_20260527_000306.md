# B1-PROFIT-LIVE-R37G_PROVIDER_RUNTIME_SELECTED_OPTION_MISMATCH_AUDIT_NO_ORDER

Classification: **REVIEW_R37G_DHAN_CONTEXT_UNAVAILABLE_WITH_ZERODHA_SELECTED_FLOW_SCOPE_DECISION_REQUIRED_NO_ORDER**

## Purpose

Audit provider runtime mismatch after R37F pseal repair:
- Dhan selected/context unavailable versus Zerodha selected-option/futures flow
- determine whether this is a controlled-paper blocker or a scope decision
- no patch, no service start, no Redis delete, no risk/execution, no order

## Provider line



## Key signals

- dhan_unavailable_seen: 
- zerodha_selected_seen: 
- stream_lengths: 
- safety_after: 

## Preliminary interpretation

If classification is , the next design decision is:

1. Accept Zerodha selected-option + Zerodha futures as observe/capture/paper scope for eligible Zerodha-complete families where Dhan is enhancement only; or
2. Keep Dhan context as a hard blocker until Dhan context feed is fixed; or
3. Allow only strategy families/modes whose frozen contracts support Dhan-degraded operation.

No controlled paper should start from this batch alone.

## Artifacts

- Proof: 
- Audit JSON: 
- Audit dir: 
- Report: 
