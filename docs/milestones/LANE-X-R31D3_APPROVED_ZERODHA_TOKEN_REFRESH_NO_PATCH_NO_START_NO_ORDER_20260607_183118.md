# LANE-X-R31D3_APPROVED_ZERODHA_TOKEN_REFRESH_NO_PATCH_NO_START_NO_ORDER_20260607_183118
2026-06-07T18:31:18+05:30

LAW=APPROVED_ZERODHA_TOKEN_REFRESH_ONLY_NO_PATCH_NO_START_NO_ORDER_NO_SECRET_PRINT_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_RISK_NO_EXECUTION

## Prior R31D2 proof
R31D2=run/proofs/LANE-X-R31D2_ZERODHA_AUTH_REPAIR_ROUTE_PLAN_NO_PATCH_NO_START_NO_ORDER_20260607_183018.json
{
  "tag": "LANE-X-R31D2_ZERODHA_AUTH_REPAIR_ROUTE_PLAN_NO_PATCH_NO_START_NO_ORDER_20260607_183018",
  "classification": "PASS_R31D2_AUTH_REPAIR_ROUTE_VISIBLE_READY_FOR_APPROVED_TOKEN_REFRESH",
  "patch_applied": false,
  "started_runtime": false,
  "broker_order": false,
  "paper_live": false,
  "redis_delete": false,
  "risk_execution_start": false,
  "secret_values_printed": false,
  "next_lane_x_batch": "LANE-X-R31D3_APPROVED_ZERODHA_TOKEN_REFRESH_NO_PATCH_NO_ORDER",
  "report": "run/audits/LANE-X-R31D2_ZERODHA_AUTH_REPAIR_ROUTE_PLAN_NO_PATCH_NO_START_NO_ORDER_20260607_183018_report.md"
}

## Pre-refresh safety
ACTIVE_RUNTIME_PROCESSES:
NONE

orders_stream_len_before=0
risk_stream_len_before=0
execution_stream_len_before=0

## Token/api presence before refresh - no values printed
--- /home/Lenovo/scalpx/common/secrets/shared/api.json
exists= True
broker_present= True len= 7
api_key_present= True len= 16
api_secret_present= True len= 32
user_id_present= True len= 6
access_token_present= False len= None
updated_at_present= False len= None
expires_at_present= False len= None
--- /home/Lenovo/scalpx/common/secrets/shared/tokens.json
exists= True
broker_present= True len= 7
api_key_present= False len= None
api_secret_present= False len= None
user_id_present= False len= None
access_token_present= True len= 32
updated_at_present= True len= 32
expires_at_present= False len= 0

## ACTION REQUIRED
1. The login command below will show a Zerodha login URL.
2. Open it in browser and complete Zerodha login.
3. After redirect, copy ONLY the request_token value from the redirected URL.
4. Paste that request_token into THIS TERMINAL prompt only.
5. Do NOT paste request_token/access_token/api_key/api_secret into ChatGPT.

## Running approved Zerodha login flow
LOGIN_RC=1

## Sanitized login log
2026-06-07 18:31:18,652 | scalpx.mme.integrations.login | INFO | loaded broker env files: /home/Lenovo/scalpx/projects/mme_scalpx/common/secrets/brokers/zerodha/session.env, /home/Lenovo/scalpx/projects/mme_scalpx/common/secrets/brokers/dhan/credentials.env, /home/Lenovo/scalpx/projects/mme_scalpx/common/secrets/brokers/dhan/session.env
2026-06-07 18:31:18,754 | scalpx.mme.integrations.login | INFO | saved Zerodha token reuse failed from broker_session_env; trying next source: Zerodha profile() verification failed: Incorrect `api_key` or `access_token`.
Open Zerodha login URL:
Open Zerodha login URL and complete login:
Paste Zerodha request_token: 2026-06-07 18:31:38,490 | scalpx.mme.integrations.login | ERROR | login failed: empty Zerodha request_token

## Token/api presence after refresh - no values printed
--- /home/Lenovo/scalpx/common/secrets/shared/tokens.json
exists= True
broker_present= True len= 7
access_token_present= True len= 32
updated_at_present= True len= 32
expires_at_present= False len= 0
login_time_utc_present= True len= 32

## Post-refresh safety
orders_stream_len_after=0
risk_stream_len_after=0
execution_stream_len_after=0

CLASSIFICATION=REVIEW_R31D3_ZERODHA_TOKEN_REFRESH_FAILED_DO_NOT_START_OBSERVE
