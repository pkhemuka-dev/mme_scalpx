# LANE-X-R31D3R_CORRECTED_INTERACTIVE_ZERODHA_TOKEN_REFRESH_NO_PATCH_NO_START_NO_ORDER_20260607_183232
2026-06-07T18:32:32+05:30

LAW=CORRECTED_INTERACTIVE_TOKEN_REFRESH_ONLY_NO_PATCH_NO_START_NO_ORDER_NO_SECRET_PRINT_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_RISK_NO_EXECUTION

## Prior failed R31D3 proof
R31D3=run/proofs/LANE-X-R31D3_APPROVED_ZERODHA_TOKEN_REFRESH_NO_PATCH_NO_START_NO_ORDER_20260607_183118.json
{
  "tag": "LANE-X-R31D3_APPROVED_ZERODHA_TOKEN_REFRESH_NO_PATCH_NO_START_NO_ORDER_20260607_183118",
  "classification": "REVIEW_R31D3_ZERODHA_TOKEN_REFRESH_FAILED_DO_NOT_START_OBSERVE",
  "patch_applied": false,
  "started_runtime": false,
  "broker_order": false,
  "paper_live": false,
  "redis_delete": false,
  "risk_execution_start": false,
  "secret_values_printed": false,
  "login_log": "run/logs/LANE-X-R31D3_APPROVED_ZERODHA_TOKEN_REFRESH_NO_PATCH_NO_START_NO_ORDER_20260607_183118_zerodha_login.log",
  "next_lane_x_batch": "LANE-X-R31D4_ZERODHA_AUTH_VALIDATION_NO_PATCH_NO_START_NO_ORDER",
  "report": "run/audits/LANE-X-R31D3_APPROVED_ZERODHA_TOKEN_REFRESH_NO_PATCH_NO_START_NO_ORDER_20260607_183118_report.md"
}

## Pre-refresh safety
ACTIVE_RUNTIME_PROCESSES=NONE
orders_stream_len_before=0
risk_stream_len_before=0
execution_stream_len_before=0

## IMPORTANT
The next command is interactive.

Steps:
1. Open the Zerodha login URL printed by the command.
2. Complete Zerodha login.
3. Copy ONLY the request_token from the redirected URL.
4. Paste it into this terminal prompt.
5. Do NOT paste request_token/api_key/api_secret/access_token into ChatGPT.

===== STARTING INTERACTIVE ZERODHA LOGIN NOW =====
Paste request_token only when prompted by the program.

LOGIN_RC=0

## Sanitized login evidence
2026-06-07 18:32:32,771 | scalpx.mme.integrations.login | INFO | loaded broker env files: /home/Lenovo/scalpx/projects/mme_scalpx/common/secrets/brokers/zerodha/session.env, /home/Lenovo/scalpx/projects/mme_scalpx/common/secrets/brokers/dhan/credentials.env, /home/Lenovo/scalpx/projects/mme_scalpx/common/secrets/brokers/dhan/session.env
2026-06-07 18:32:32,859 | scalpx.mme.integrations.login | INFO | saved Zerodha token reuse failed from broker_session_env; trying next source: Zerodha profile() verification failed: Incorrect `api_key` or `access_token`.
Open Zerodha login URL:
Open Zerodha login URL and complete login:
Paste Zerodha request_token: zerodha: ok=True user=DD6241 login_time_utc=2026-06-07T13:03:33.916490+00:00 access_token=<redacted> detail=verified via profile() and optional ltp()

## Token presence after refresh - no values printed
tokens_exists= True
broker_present= True len= 7
access_token_present= True len= 32
updated_at_present= False len= None
login_time_utc_present= False len= None
expires_at_present= False len= 0
TOKEN_AUDIT_RC=0

## Post-refresh safety
orders_stream_len_after=0
risk_stream_len_after=0
execution_stream_len_after=0

CLASSIFICATION=PASS_R31D3R_ZERODHA_TOKEN_REFRESH_COMPLETED_READY_FOR_AUTH_VALIDATION
