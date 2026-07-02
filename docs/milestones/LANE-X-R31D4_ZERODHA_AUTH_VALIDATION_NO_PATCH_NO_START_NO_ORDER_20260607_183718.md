# LANE-X-R31D4_ZERODHA_AUTH_VALIDATION_NO_PATCH_NO_START_NO_ORDER_20260607_183718
2026-06-07T18:37:18+05:30

LAW=AUTH_VALIDATION_ONLY_NO_PATCH_NO_START_NO_ORDER_NO_SECRET_PRINT_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_RISK_NO_EXECUTION

## Prior R31D3R proof
R31D3R=run/proofs/LANE-X-R31D3R_CORRECTED_INTERACTIVE_ZERODHA_TOKEN_REFRESH_NO_PATCH_NO_START_NO_ORDER_20260607_183232.json
{
  "tag": "LANE-X-R31D3R_CORRECTED_INTERACTIVE_ZERODHA_TOKEN_REFRESH_NO_PATCH_NO_START_NO_ORDER_20260607_183232",
  "classification": "PASS_R31D3R_ZERODHA_TOKEN_REFRESH_COMPLETED_READY_FOR_AUTH_VALIDATION",
  "patch_applied": false,
  "started_runtime": false,
  "broker_order": false,
  "paper_live": false,
  "redis_delete": false,
  "risk_execution_start": false,
  "secret_values_printed": false,
  "login_log": "run/logs/LANE-X-R31D3R_CORRECTED_INTERACTIVE_ZERODHA_TOKEN_REFRESH_NO_PATCH_NO_START_NO_ORDER_20260607_183232_zerodha_login_interactive.log",
  "next_lane_x_batch": "LANE-X-R31D4_ZERODHA_AUTH_VALIDATION_NO_PATCH_NO_START_NO_ORDER",
  "report": "run/audits/LANE-X-R31D3R_CORRECTED_INTERACTIVE_ZERODHA_TOKEN_REFRESH_NO_PATCH_NO_START_NO_ORDER_20260607_183232_report.md"
}

## Pre-validation safety
ACTIVE_RUNTIME_PROCESSES:
NONE

orders_stream_len_before=0
risk_stream_len_before=0
execution_stream_len_before=0

## Token/api file validation - no values printed
--- /home/Lenovo/scalpx/common/secrets/shared/api.json
exists= True
broker_present= True len= 7
api_key_present= True len= 16
api_secret_present= True len= 32
user_id_present= True len= 6
access_token_present= False len= None
updated_at_present= False len= None
login_time_utc_present= False len= None
expires_at_present= False len= None
--- /home/Lenovo/scalpx/common/secrets/shared/tokens.json
exists= True
broker_present= True len= 7
api_key_present= False len= None
api_secret_present= False len= None
user_id_present= False len= None
access_token_present= True len= 32
updated_at_present= False len= None
login_time_utc_present= False len= None
expires_at_present= False len= 0
FILE_RC=0

## Direct Zerodha profile + LTP validation - no secret values printed
ZERODHA_PROFILE_OK True
ZERODHA_USER_ID_PRESENT True
ZERODHA_LTP_OK True
LTP_INSTRUMENT NSE:NIFTY 50
Traceback (most recent call last):
  File "<stdin>", line 23, in <module>
AttributeError: 'BootstrapQuote' object has no attribute 'last_price'
AUTH_RC=1

## Post-validation safety
orders_stream_len_after=0
risk_stream_len_after=0
execution_stream_len_after=0

CLASSIFICATION=REVIEW_R31D4_ZERODHA_AUTH_VALIDATION_FAILED_DO_NOT_START
