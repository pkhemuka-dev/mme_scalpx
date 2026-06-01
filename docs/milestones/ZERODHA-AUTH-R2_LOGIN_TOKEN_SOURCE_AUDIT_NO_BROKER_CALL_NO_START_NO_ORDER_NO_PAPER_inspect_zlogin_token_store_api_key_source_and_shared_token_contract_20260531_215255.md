# ZERODHA-AUTH-R2_LOGIN_TOKEN_SOURCE_AUDIT_NO_BROKER_CALL_NO_START_NO_ORDER_NO_PAPER

Classification: **PASS_ZERODHA_AUTH_R2_SOURCE_AUDIT_READY_NO_BROKER_CALL_NO_START_NO_ORDER_NO_PAPER**

## Purpose

Read-only source audit to determine how Zerodha `api_key` should be supplied or repaired before retrying pfeeds.

## Checks

- zlogin_ok=1
- ensure_token_ok=1
- check_token_ok=1
- token_parse_ok=1
- has_access_token=1
- has_api_key=0
- safety_ok=1

## Artifacts

- Zlogin source: `run/audits/ZERODHA-AUTH-R2_LOGIN_TOKEN_SOURCE_AUDIT_NO_BROKER_CALL_NO_START_NO_ORDER_NO_PAPER_inspect_zlogin_token_store_api_key_source_and_shared_token_contract_20260531_215255_zlogin_source.txt`
- Token source grep: `run/audits/ZERODHA-AUTH-R2_LOGIN_TOKEN_SOURCE_AUDIT_NO_BROKER_CALL_NO_START_NO_ORDER_NO_PAPER_inspect_zlogin_token_store_api_key_source_and_shared_token_contract_20260531_215255_token_store_source.txt`
- Auth source: `run/audits/ZERODHA-AUTH-R2_LOGIN_TOKEN_SOURCE_AUDIT_NO_BROKER_CALL_NO_START_NO_ORDER_NO_PAPER_inspect_zlogin_token_store_api_key_source_and_shared_token_contract_20260531_215255_auth_source_grep.txt`
- Config shape: `run/audits/ZERODHA-AUTH-R2_LOGIN_TOKEN_SOURCE_AUDIT_NO_BROKER_CALL_NO_START_NO_ORDER_NO_PAPER_inspect_zlogin_token_store_api_key_source_and_shared_token_contract_20260531_215255_config_shape_no_secrets.txt`
- State: `run/audits/ZERODHA-AUTH-R2_LOGIN_TOKEN_SOURCE_AUDIT_NO_BROKER_CALL_NO_START_NO_ORDER_NO_PAPER_inspect_zlogin_token_store_api_key_source_and_shared_token_contract_20260531_215255_state.txt`

## Safety

No broker call, no service start/stop, no Redis write, no order, no paper/live.

- orders=0
- risk_stream=0
- execution_stream=0
- feeds_proc=0
- risk_proc=0
- execution_proc=0
