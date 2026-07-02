# LANE-X-R34C_EXACT_FULL_TOKEN_AUDIT_ENTER_CANDIDATE_MIV_NO_PATCH_NO_REPLAY_NO_ORDER_prove_whether_enter_call_put_candidate_true_or_miv_tokens_exist_anywhere_in_sealed_friday_durable_and_pseal_20260613_103045

classification: PASS_R34C_EXACT_TOKEN_AUDIT_WRITTEN_NO_ORDER

## Exact token result

- durable decisions ENTER_CALL: `263511`
- durable decisions ENTER_PUT: `239982`
- pseal decisions ENTER_CALL: `0`
- pseal decisions ENTER_PUT: `0`
- durable candidate_true true: `0`
- durable candidate_present true: `0`
- durable MIV_R: `0`

## Safety

- orders: `0`
- risk: `0`
- execution: `0`

## Meaning

If ENTER token counts are zero, R33I ENTER counts are not real decision actions and must be demoted.
Then next work is:
1. why activation_candidate_count stays 0 / view_data_invalid;
2. run offline MIV evaluator on sealed durable tape, because MIV is dormant/replay-only, not live-emitted.
