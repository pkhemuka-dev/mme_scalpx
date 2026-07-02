# LANE-X-R31D2_ZERODHA_AUTH_REPAIR_ROUTE_PLAN_NO_PATCH_NO_START_NO_ORDER_20260607_183018
2026-06-07T18:30:18+05:30

LAW=AUTH_REPAIR_ROUTE_PLAN_ONLY_NO_PATCH_NO_START_NO_ORDER_NO_SECRET_PRINT_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_RISK_NO_EXECUTION

## Prior R31D1 proof
R31D1=run/proofs/LANE-X-R31D1_ZERODHA_AUTH_BOOTSTRAP_CONFIG_AUDIT_NO_PATCH_NO_START_NO_ORDER_20260607_182750.json
{
  "tag": "LANE-X-R31D1_ZERODHA_AUTH_BOOTSTRAP_CONFIG_AUDIT_NO_PATCH_NO_START_NO_ORDER_20260607_182750",
  "classification": "PASS_R31D1_AUTH_CONFIG_SEAM_IDENTIFIED_ZERODHA_API_KEY_OR_TOKEN_INVALID",
  "patch_applied": false,
  "started_runtime": false,
  "broker_order": false,
  "paper_live": false,
  "redis_delete": false,
  "risk_execution_start": false,
  "secret_values_printed": false,
  "report": "run/audits/LANE-X-R31D1_ZERODHA_AUTH_BOOTSTRAP_CONFIG_AUDIT_NO_PATCH_NO_START_NO_ORDER_20260607_182750_report.md"
}

## Locate expected API/token store paths from source
app/mme_scalpx/integrations/token_store.py:8:- read static broker credential config from shared api.json
app/mme_scalpx/integrations/token_store.py:9:- read/write short-lived broker token/session state from tokens.json
app/mme_scalpx/integrations/token_store.py:23:api.json owns:
app/mme_scalpx/integrations/token_store.py:29:tokens.json owns:
app/mme_scalpx/integrations/token_store.py:53:DEFAULT_API_JSON = Path("/home/Lenovo/scalpx/common/secrets/shared/api.json")
app/mme_scalpx/integrations/token_store.py:54:DEFAULT_TOKENS_JSON = Path("/home/Lenovo/scalpx/common/secrets/shared/tokens.json")
app/mme_scalpx/integrations/token_store.py:70:class BrokerApiConfig:
app/mme_scalpx/integrations/token_store.py:77:    def from_dict(cls, data: Dict[str, Any]) -> "BrokerApiConfig":
app/mme_scalpx/integrations/token_store.py:82:                f"api.json missing required non-empty field(s): {', '.join(missing)}"
app/mme_scalpx/integrations/token_store.py:93:class BrokerTokenState:
app/mme_scalpx/integrations/token_store.py:103:    def from_dict(cls, data: Dict[str, Any]) -> "BrokerTokenState":
app/mme_scalpx/integrations/token_store.py:106:            raise SecretFileFormatError("tokens.json missing required non-empty field: broker")
app/mme_scalpx/integrations/token_store.py:112:            raise SecretFileFormatError("tokens.json field 'metadata' must be an object")
app/mme_scalpx/integrations/token_store.py:203:def load_api_config(path: Path = DEFAULT_API_JSON) -> BrokerApiConfig:
app/mme_scalpx/integrations/token_store.py:204:    return BrokerApiConfig.from_dict(_read_json_file(path))
app/mme_scalpx/integrations/token_store.py:207:def load_token_state(path: Path = DEFAULT_TOKENS_JSON) -> BrokerTokenState:
app/mme_scalpx/integrations/token_store.py:208:    return BrokerTokenState.from_dict(_read_json_file(path))
app/mme_scalpx/integrations/token_store.py:211:def save_token_state(state: BrokerTokenState, path: Path = DEFAULT_TOKENS_JSON) -> None:
app/mme_scalpx/integrations/token_store.py:215:def clear_token_state(path: Path = DEFAULT_TOKENS_JSON, broker: str = "") -> None:
app/mme_scalpx/integrations/token_store.py:216:    payload = BrokerTokenState(broker=broker).to_dict()
app/mme_scalpx/integrations/token_store.py:220:def token_file_exists(path: Path = DEFAULT_TOKENS_JSON) -> bool:
app/mme_scalpx/integrations/token_store.py:224:def validate_api_config(path: Path = DEFAULT_API_JSON) -> None:
app/mme_scalpx/integrations/token_store.py:228:def validate_token_state(path: Path = DEFAULT_TOKENS_JSON) -> None:
app/mme_scalpx/integrations/token_store.py:234:    print(f"api.json OK | broker={api.broker} | user_id={api.user_id}")
app/mme_scalpx/integrations/token_store.py:239:            "tokens.json OK | "
app/mme_scalpx/integrations/token_store.py:245:        print("tokens.json not present yet")
app/mme_scalpx/integrations/bootstrap_quote.py:29:    BrokerApiConfig,
app/mme_scalpx/integrations/bootstrap_quote.py:30:    BrokerTokenState,
app/mme_scalpx/integrations/bootstrap_quote.py:122:def validate_api_config_for_zerodha(api: BrokerApiConfig) -> None:
app/mme_scalpx/integrations/bootstrap_quote.py:125:            f"api.json broker must be 'zerodha', got {api.broker!r}"
app/mme_scalpx/integrations/bootstrap_quote.py:128:        raise StartupValidationError("api.json missing non-empty api_key")
app/mme_scalpx/integrations/bootstrap_quote.py:131:def validate_token_state_for_zerodha(state: BrokerTokenState) -> None:
app/mme_scalpx/integrations/bootstrap_quote.py:134:            f"tokens.json broker must be 'zerodha', got {state.broker!r}"
app/mme_scalpx/integrations/bootstrap_quote.py:137:        raise StartupValidationError("tokens.json missing non-empty access_token")
app/mme_scalpx/integrations/bootstrap_quote.py:140:def build_kite(api: BrokerApiConfig, state: BrokerTokenState) -> KiteConnect:
app/mme_scalpx/integrations/login.py:59:    BrokerApiConfig,
app/mme_scalpx/integrations/login.py:60:    BrokerTokenState,
app/mme_scalpx/integrations/login.py:268:def _try_load_api_config() -> BrokerApiConfig | None:
app/mme_scalpx/integrations/login.py:411:def validate_api_config_for_zerodha(api: BrokerApiConfig) -> ZerodhaLoginConfig:
app/mme_scalpx/integrations/login.py:415:            f"api.json broker must be 'zerodha' for Zerodha login, got: {api.broker!r}"
app/mme_scalpx/integrations/login.py:418:        raise StartupValidationError("api.json missing non-empty api_key for Zerodha")
app/mme_scalpx/integrations/login.py:420:        raise StartupValidationError("api.json missing non-empty api_secret for Zerodha")
app/mme_scalpx/integrations/login.py:431:    api: BrokerApiConfig | None,
app/mme_scalpx/integrations/login.py:449:            logger.info("api.json is not a Zerodha config; falling back to env")
app/mme_scalpx/integrations/login.py:455:        raise StartupValidationError("missing Zerodha api_key in api.json or environment")
app/mme_scalpx/integrations/login.py:457:        raise StartupValidationError("missing Zerodha api_secret in api.json or environment")
app/mme_scalpx/integrations/login.py:532:) -> BrokerTokenState:
app/mme_scalpx/integrations/login.py:554:    return BrokerTokenState(
app/mme_scalpx/integrations/login.py:583:def validate_token_state_for_zerodha(state: BrokerTokenState) -> None:
app/mme_scalpx/integrations/login.py:586:            f"tokens.json broker must be 'zerodha' for Zerodha reuse, got: {state.broker!r}"
app/mme_scalpx/integrations/login.py:589:        raise StartupValidationError("tokens.json missing non-empty Zerodha access_token")
app/mme_scalpx/integrations/login.py:654:        refreshed_state = BrokerTokenState(
app/mme_scalpx/integrations/login.py:740:    api: BrokerApiConfig | None,
app/mme_scalpx/integrations/login.py:776:            "missing Dhan client_id in CLI, environment, or api.json"
app/mme_scalpx/integrations/login.py:866:) -> BrokerTokenState:
app/mme_scalpx/integrations/login.py:891:    return BrokerTokenState(
app/mme_scalpx/integrations/login.py:951:    # shared/tokens.json is Zerodha-owned because Zerodha bootstrap_quote,

## Secret/config presence audit - no values printed
--- /home/Lenovo/scalpx/common/secrets/shared/api.json
exists= True
size= 134
top_keys= ['api_key', 'api_secret', 'broker', 'user_id']
broker_present= True len= 7
api_key_present= True len= 16
api_secret_present= True len= 32
user_id_present= True len= 6
access_token_present= False
refresh_token_present= False
expires_at_present= False
updated_at_present= False
--- /home/Lenovo/scalpx/common/secrets/shared/tokens.json
exists= True
size= 691
top_keys= ['access_token', 'broker', 'expires_at', 'issued_at', 'login_time_utc', 'metadata', 'refresh_token', 'session_id', 'updated_at']
broker_present= True len= 7
api_key_present= False
api_secret_present= False
user_id_present= False
access_token_present= True len= 32
refresh_token_present= False len= 0
expires_at_present= False len= 0
updated_at_present= True len= 32
--- /home/Lenovo/scalpx/common/secrets/api.json
exists= False
--- /home/Lenovo/scalpx/common/secrets/tokens.json
exists= False
--- api.json
exists= False
--- tokens.json
exists= False
--- .env
exists= False
CONFIG_RC=0

## Login CLI/help surface
2026-06-07 18:30:19,024 | scalpx.mme.integrations.login | INFO | loaded broker env files: /home/Lenovo/scalpx/projects/mme_scalpx/common/secrets/brokers/zerodha/session.env, /home/Lenovo/scalpx/projects/mme_scalpx/common/secrets/brokers/dhan/credentials.env, /home/Lenovo/scalpx/projects/mme_scalpx/common/secrets/brokers/dhan/session.env
usage: login.py [-h] [--zerodha] [--dhan] [--request-token REQUEST_TOKEN]
                [--zerodha-access-token ZERODHA_ACCESS_TOKEN]
                [--show-login-url] [--no-ltp-verify]
                [--dhan-access-token DHAN_ACCESS_TOKEN]
                [--dhan-client-id DHAN_CLIENT_ID]
                [--dhan-api-key DHAN_API_KEY]
                [--dhan-api-secret DHAN_API_SECRET] [--dhan-pin DHAN_PIN]
                [--dhan-totp DHAN_TOTP] [--dhan-generate-token]
                [--dhan-renew-token] [--no-dhan-verify]
                [--log-level LOG_LEVEL]

ScalpX MME dual-broker login/session integration

options:
  -h, --help            show this help message and exit
  --zerodha             Run Zerodha login flow
  --dhan                Run Dhan login flow
  --request-token REQUEST_TOKEN
                        Zerodha request_token. If omitted, interactive prompt
                        is used.
  --zerodha-access-token ZERODHA_ACCESS_TOKEN
                        Saved Zerodha access token for reuse before
                        interactive login.
  --show-login-url      Print Zerodha login URL before request_token prompt.
  --no-ltp-verify       Skip optional Zerodha LTP verification after profile()
                        succeeds.
  --dhan-access-token DHAN_ACCESS_TOKEN
                        Dhan access token. If omitted, env or generate/renew
                        flow is used.
  --dhan-client-id DHAN_CLIENT_ID
                        Dhan client id.
  --dhan-api-key DHAN_API_KEY
                        Optional Dhan API key.
  --dhan-api-secret DHAN_API_SECRET
                        Optional Dhan API secret.
  --dhan-pin DHAN_PIN   Optional Dhan pin for generate-token flow.
  --dhan-totp DHAN_TOTP
                        Optional Dhan TOTP for generate-token flow.
  --dhan-generate-token
                        Generate Dhan access token using client id + pin +
                        totp.
  --dhan-renew-token    Renew active Dhan access token for another validity
                        window.
  --no-dhan-verify      Skip Dhan fundlimit verification after token
                        acquisition.
  --log-level LOG_LEVEL
                        Logging level
LOGIN_HELP_RC=0

## Safety remains zero
orders_stream_len=0
risk_stream_len=0
execution_stream_len=0

## Planned repair route
REPAIR_ROUTE:
  1. Confirm api.json exists and has api_key/api_secret/user_id presence without printing values.
  2. Refresh Zerodha access_token through the approved login flow.
  3. Re-run a no-start auth validation audit.
  4. Only after auth validation passes, retry observe-only pfeeds/pstack.
  5. Do not run candidate watch until feeds are alive and growing.

DO_NOT:
  - Do not paste secrets into chat.
  - Do not print api_key/api_secret/access_token.
  - Do not patch source for this.
  - Do not start risk/execution.
  - Do not enable paper/live.

CLASSIFICATION=PASS_R31D2_AUTH_REPAIR_ROUTE_VISIBLE_READY_FOR_APPROVED_TOKEN_REFRESH
