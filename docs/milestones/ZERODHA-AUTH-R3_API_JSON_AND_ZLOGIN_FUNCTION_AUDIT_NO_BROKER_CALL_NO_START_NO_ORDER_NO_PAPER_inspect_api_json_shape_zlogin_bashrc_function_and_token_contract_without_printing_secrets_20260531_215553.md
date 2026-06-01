# ZERODHA-AUTH-R3_API_JSON_AND_ZLOGIN_FUNCTION_AUDIT_NO_BROKER_CALL_NO_START_NO_ORDER_NO_PAPER

Classification: **PASS_ZERODHA_AUTH_R3_API_ZLOGIN_AUDIT_READY_NO_BROKER_CALL_NO_START_NO_ORDER_NO_PAPER**

## Purpose

Read-only audit of Zerodha static credential source and zlogin function/alias source.

No broker call, no service start/stop, no Redis write, no order, no paper/live.

## Checks

- api_parse_ok=1
- api_has_key=1
- api_has_secret=1
- api_has_user=1
- token_parse_ok=1
- token_has_access=1
- token_has_key=0
- zlogin_body_ok=1
- safety_ok=1

## Artifacts

- API audit: `run/audits/ZERODHA-AUTH-R3_API_JSON_AND_ZLOGIN_FUNCTION_AUDIT_NO_BROKER_CALL_NO_START_NO_ORDER_NO_PAPER_inspect_api_json_shape_zlogin_bashrc_function_and_token_contract_without_printing_secrets_20260531_215553_api_json_shape.json`
- Token audit: `run/audits/ZERODHA-AUTH-R3_API_JSON_AND_ZLOGIN_FUNCTION_AUDIT_NO_BROKER_CALL_NO_START_NO_ORDER_NO_PAPER_inspect_api_json_shape_zlogin_bashrc_function_and_token_contract_without_printing_secrets_20260531_215553_tokens_json_shape.json`
- Bashrc audit: `run/audits/ZERODHA-AUTH-R3_API_JSON_AND_ZLOGIN_FUNCTION_AUDIT_NO_BROKER_CALL_NO_START_NO_ORDER_NO_PAPER_inspect_api_json_shape_zlogin_bashrc_function_and_token_contract_without_printing_secrets_20260531_215553_bashrc_zlogin_extract.txt`
- Source audit: `run/audits/ZERODHA-AUTH-R3_API_JSON_AND_ZLOGIN_FUNCTION_AUDIT_NO_BROKER_CALL_NO_START_NO_ORDER_NO_PAPER_inspect_api_json_shape_zlogin_bashrc_function_and_token_contract_without_printing_secrets_20260531_215553_auth_source_contract_extract.txt`
- State: `run/audits/ZERODHA-AUTH-R3_API_JSON_AND_ZLOGIN_FUNCTION_AUDIT_NO_BROKER_CALL_NO_START_NO_ORDER_NO_PAPER_inspect_api_json_shape_zlogin_bashrc_function_and_token_contract_without_printing_secrets_20260531_215553_state.txt`

## Safety

- orders=0
- risk_stream=0
- execution_stream=0
- feeds_proc=0
- risk_proc=0
- execution_proc=0
