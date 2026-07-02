# LANE-X-R31D1_ZERODHA_AUTH_BOOTSTRAP_CONFIG_AUDIT_NO_PATCH_NO_START_NO_ORDER_20260607_182750
2026-06-07T18:27:50+05:30

LAW=AUTH_CONFIG_AUDIT_ONLY_NO_PATCH_NO_START_NO_ORDER_NO_SECRET_PRINT_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_RISK_NO_EXECUTION

## R31D proof
R31D=run/proofs/LANE-X-R31D_OBSERVE_ONLY_START_REUSE_AND_CANDIDATE_WATCH_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION_20260607_182433.json
{
  "tag": "LANE-X-R31D_OBSERVE_ONLY_START_REUSE_AND_CANDIDATE_WATCH_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION_20260607_182433",
  "classification": "PASS_R31D_OBSERVE_ONLY_START_REUSE_DONE_SAFETY_ZERO_READY_FOR_CANDIDATE_WATCH_WINDOW",
  "patch_applied": false,
  "started_or_reused_observe_only": true,
  "broker_order": false,
  "paper_live": false,
  "redis_delete": false,
  "risk_execution_start": false,
  "next_lane_x_batch": "LANE-X-R31E_10MIN_CANDIDATE_WATCH_WINDOW_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION",
  "report": "run/audits/LANE-X-R31D_OBSERVE_ONLY_START_REUSE_AND_CANDIDATE_WATCH_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION_20260607_182433_report.md"
}

## Latest pfeeds failure logs
--- run/live_capture/pfeeds_live_raw_capture_20260607_182447.log
3:  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/integrations/bootstrap_quote.py", line 188, in fetch_underlying_ltp
4:    payload = kite.ltp([instrument_key])
11:kiteconnect.exceptions.TokenException: Incorrect `api_key` or `access_token`.
29:    built = build_runtime_instruments()
30:  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/integrations/runtime_instruments_factory.py", line 265, in build_runtime_instruments
32:  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/integrations/bootstrap_quote.py", line 192, in fetch_underlying_ltp
33:    raise QuoteFetchError(f"kite.ltp({instrument_key!r}) failed: {exc}") from exc
34:app.mme_scalpx.integrations.bootstrap_quote.QuoteFetchError: kite.ltp('NSE:NIFTY 50') failed: Incorrect `api_key` or `access_token`.
--- run/live_capture/pfeeds_live_raw_capture_20260607_182433.log
3:  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/integrations/bootstrap_quote.py", line 188, in fetch_underlying_ltp
4:    payload = kite.ltp([instrument_key])
11:kiteconnect.exceptions.TokenException: Incorrect `api_key` or `access_token`.
29:    built = build_runtime_instruments()
30:  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/integrations/runtime_instruments_factory.py", line 265, in build_runtime_instruments
32:  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/integrations/bootstrap_quote.py", line 192, in fetch_underlying_ltp
33:    raise QuoteFetchError(f"kite.ltp({instrument_key!r}) failed: {exc}") from exc
34:app.mme_scalpx.integrations.bootstrap_quote.QuoteFetchError: kite.ltp('NSE:NIFTY 50') failed: Incorrect `api_key` or `access_token`.
--- run/live_capture/pfeeds_live_raw_capture_20260604_095321.log
3:{"level":"INFO","logger":"app.mme_scalpx.main","message":"bootstrap_provider_completed provider=app.mme_scalpx.integrations.bootstrap_provider:provide mode=returned_dict runtime_instruments=1 feed_adapter=1 market_data_adapter=0 feed_adapters=1 zerodha_feed_adapter=1 dhan_feed_adapter=1 dhan_context_adapter=1 broker=1","process":22720,"thread":"MainThread","ts":"2026-06-04T04:23:44.508095+00:00"}
4:{"level":"INFO","logger":"app.mme_scalpx.main","message":"dependency_surfaces_resolved runtime_instruments=1 feed_adapter=1 market_data_adapter=1 feed_adapters=1 zerodha_feed_adapter=1 dhan_feed_adapter=1 dhan_context_adapter=1 broker=1","process":22720,"thread":"MainThread","ts":"2026-06-04T04:23:44.509861+00:00"}

## Secret/config presence audit - no values printed
--- /home/Lenovo/scalpx/common/secrets/shared/tokens.json
exists= True
size= 691
top_keys= ['access_token', 'broker', 'expires_at', 'issued_at', 'login_time_utc', 'metadata', 'refresh_token', 'session_id', 'updated_at']
broker_present= True len= 7
access_token_present= True len= 32
api_key_present= False
zerodha_present= False
--- etc/brokers/zerodha.yaml
exists= True
size= 2048
api_key_mentioned= False
access_token_mentioned= False
ZERODHA_API_KEY_mentioned= False
ZERODHA_ACCESS_TOKEN_mentioned= False
--- etc/brokers/runtime.yaml
exists= True
size= 2166
api_key_mentioned= False
access_token_mentioned= False
ZERODHA_API_KEY_mentioned= False
ZERODHA_ACCESS_TOKEN_mentioned= False
--- etc/brokers/provider_roles.yaml
exists= True
size= 2300
api_key_mentioned= False
access_token_mentioned= False
ZERODHA_API_KEY_mentioned= False
ZERODHA_ACCESS_TOKEN_mentioned= False
--- .env
exists= False
AUDIT_RC=0

## Source lookup: where bootstrap reads api_key/access_token
app/mme_scalpx/integrations/dhan_marketdata.py:421:    def fetch_chain_snapshot(self, *, access_token: str | None = None) -> Any:
app/mme_scalpx/integrations/dhan_marketdata.py:1184:            access_token=self._auth_token_or_none(),
app/mme_scalpx/integrations/dhan_marketdata.py:1428:            return self._auth_manager.get_access_token(ensure_authenticated=True)
app/mme_scalpx/integrations/bootstrap_quote.py:2:app/mme_scalpx/integrations/bootstrap_quote.py
app/mme_scalpx/integrations/bootstrap_quote.py:9:- create authenticated KiteConnect client
app/mme_scalpx/integrations/bootstrap_quote.py:39:    from kiteconnect import KiteConnect  # type: ignore
app/mme_scalpx/integrations/bootstrap_quote.py:42:        "kiteconnect is required by app.mme_scalpx.integrations.bootstrap_quote"
app/mme_scalpx/integrations/bootstrap_quote.py:127:    if not api.api_key.strip():
app/mme_scalpx/integrations/bootstrap_quote.py:128:        raise StartupValidationError("api.json missing non-empty api_key")
app/mme_scalpx/integrations/bootstrap_quote.py:134:            f"tokens.json broker must be 'zerodha', got {state.broker!r}"
app/mme_scalpx/integrations/bootstrap_quote.py:136:    if not state.access_token.strip():
app/mme_scalpx/integrations/bootstrap_quote.py:137:        raise StartupValidationError("tokens.json missing non-empty access_token")
app/mme_scalpx/integrations/bootstrap_quote.py:140:def build_kite(api: BrokerApiConfig, state: BrokerTokenState) -> KiteConnect:
app/mme_scalpx/integrations/bootstrap_quote.py:141:    kite = KiteConnect(api_key=api.api_key)
app/mme_scalpx/integrations/bootstrap_quote.py:142:    kite.set_access_token(state.access_token)
app/mme_scalpx/integrations/bootstrap_quote.py:171:def fetch_underlying_ltp(instrument_key: str = DEFAULT_UNDERLYING_KEY) -> BootstrapQuote:
app/mme_scalpx/integrations/instrument_master_sync.py:53:    from kiteconnect import KiteConnect  # type: ignore
app/mme_scalpx/integrations/instrument_master_sync.py:157:    if not api.api_key.strip():
app/mme_scalpx/integrations/instrument_master_sync.py:158:        raise StartupValidationError("api.json missing non-empty api_key")
app/mme_scalpx/integrations/instrument_master_sync.py:164:            f"tokens.json broker must be 'zerodha', got {state.broker!r}"
app/mme_scalpx/integrations/instrument_master_sync.py:166:    if not state.access_token.strip():
app/mme_scalpx/integrations/instrument_master_sync.py:167:        raise StartupValidationError("tokens.json missing non-empty access_token")
app/mme_scalpx/integrations/instrument_master_sync.py:170:def build_kite(api: BrokerApiConfig, state: BrokerTokenState) -> KiteConnect:
app/mme_scalpx/integrations/instrument_master_sync.py:171:    kite = KiteConnect(api_key=api.api_key)
app/mme_scalpx/integrations/instrument_master_sync.py:172:    kite.set_access_token(state.access_token)
app/mme_scalpx/integrations/instrument_master_sync.py:176:def fetch_instruments(kite: KiteConnect, exchange: str) -> list[dict[str, Any]]:
app/mme_scalpx/integrations/token_store.py:9:- read/write short-lived broker token/session state from tokens.json
app/mme_scalpx/integrations/token_store.py:25:- api_key
app/mme_scalpx/integrations/token_store.py:29:tokens.json owns:
app/mme_scalpx/integrations/token_store.py:31:- access_token
app/mme_scalpx/integrations/token_store.py:54:DEFAULT_TOKENS_JSON = Path("/home/Lenovo/scalpx/common/secrets/shared/tokens.json")
app/mme_scalpx/integrations/token_store.py:72:    api_key: str
app/mme_scalpx/integrations/token_store.py:78:        required = ("broker", "api_key", "api_secret", "user_id")
app/mme_scalpx/integrations/token_store.py:86:            api_key=str(data["api_key"]).strip(),
app/mme_scalpx/integrations/token_store.py:95:    access_token: str = ""
app/mme_scalpx/integrations/token_store.py:106:            raise SecretFileFormatError("tokens.json missing required non-empty field: broker")
app/mme_scalpx/integrations/token_store.py:112:            raise SecretFileFormatError("tokens.json field 'metadata' must be an object")
app/mme_scalpx/integrations/token_store.py:116:            access_token=str(data.get("access_token", "")).strip(),
app/mme_scalpx/integrations/token_store.py:127:            "access_token": self.access_token,
app/mme_scalpx/integrations/token_store.py:135:    def has_access_token(self) -> bool:
app/mme_scalpx/integrations/token_store.py:136:        return bool(self.access_token)
app/mme_scalpx/integrations/token_store.py:239:            "tokens.json OK | "
app/mme_scalpx/integrations/token_store.py:241:            f"has_access_token={token.has_access_token()} | "
app/mme_scalpx/integrations/token_store.py:245:        print("tokens.json not present yet")
app/mme_scalpx/integrations/zerodha_feed_adapter.py:160:    if not api.api_key.strip():
app/mme_scalpx/integrations/zerodha_feed_adapter.py:161:        raise StartupValidationError("api.json missing non-empty api_key")
app/mme_scalpx/integrations/zerodha_feed_adapter.py:167:            f"tokens.json broker must be 'zerodha', got {state.broker!r}"
app/mme_scalpx/integrations/zerodha_feed_adapter.py:169:    if not state.access_token.strip():
app/mme_scalpx/integrations/zerodha_feed_adapter.py:170:        raise StartupValidationError("tokens.json missing non-empty access_token")
app/mme_scalpx/integrations/zerodha_feed_adapter.py:302:        self._ticker = KiteTicker(api.api_key, state.access_token)
app/mme_scalpx/integrations/dhan_runtime_clients.py:162:        access_token: str | None = None,
app/mme_scalpx/integrations/dhan_runtime_clients.py:167:        self._access_token = _norm(access_token or os.getenv("DHAN_ACCESS_TOKEN") or os.getenv("MME_DHAN_ACCESS_TOKEN"))
app/mme_scalpx/integrations/dhan_runtime_clients.py:177:    def access_token(self) -> str:
app/mme_scalpx/integrations/dhan_runtime_clients.py:178:        if not self._access_token:
app/mme_scalpx/integrations/dhan_runtime_clients.py:180:        return self._access_token
app/mme_scalpx/integrations/dhan_runtime_clients.py:187:            "access-token": self.access_token,
app/mme_scalpx/integrations/dhan_runtime_clients.py:380:        access_token: str | None = None,
app/mme_scalpx/integrations/dhan_runtime_clients.py:387:        self._access_token = _norm(access_token or os.getenv("DHAN_ACCESS_TOKEN") or os.getenv("MME_DHAN_ACCESS_TOKEN"))
app/mme_scalpx/integrations/dhan_runtime_clients.py:395:        if not self._access_token:
app/mme_scalpx/integrations/dhan_runtime_clients.py:400:    def fetch_chain_snapshot(self, *, access_token: str | None = None) -> Any:
app/mme_scalpx/integrations/dhan_runtime_clients.py:401:        token = _norm(access_token or self._access_token)
app/mme_scalpx/integrations/dhan_runtime_clients.py:453:        access_token: str | None = None,
app/mme_scalpx/integrations/dhan_runtime_clients.py:458:        self._access_token = _norm(access_token or os.getenv("DHAN_ACCESS_TOKEN") or os.getenv("MME_DHAN_ACCESS_TOKEN"))
app/mme_scalpx/integrations/dhan_runtime_clients.py:466:        if not self._access_token:
app/mme_scalpx/integrations/dhan_runtime_clients.py:476:            f"?token={quote(self._access_token)}&clientId={quote(self._client_id)}&authType=2"
app/mme_scalpx/integrations/dhan_runtime_clients.py:618:        self._access_token = _norm(os.getenv("DHAN_ACCESS_TOKEN") or os.getenv("MME_DHAN_ACCESS_TOKEN"))
app/mme_scalpx/integrations/dhan_runtime_clients.py:626:        if not self._access_token:
app/mme_scalpx/integrations/dhan_runtime_clients.py:703:            f"?version=2&token={quote(self._access_token)}&clientId={quote(self._client_id)}&authType=2"
app/mme_scalpx/integrations/runtime_instruments_factory.py:8:- fetch bootstrap underlying LTP through bootstrap_quote
app/mme_scalpx/integrations/runtime_instruments_factory.py:33:from app.mme_scalpx.integrations.bootstrap_quote import (
app/mme_scalpx/integrations/runtime_instruments_factory.py:35:    fetch_underlying_ltp,
app/mme_scalpx/integrations/runtime_instruments_factory.py:265:    quote = fetch_underlying_ltp(quote_key)
app/mme_scalpx/integrations/runtime_instruments_factory.py:292:        "bootstrap_quote": {
app/mme_scalpx/integrations/bootstrap_provider.py:19:from app.mme_scalpx.integrations.bootstrap_quote import build_kite
app/mme_scalpx/integrations/bootstrap_provider.py:84:            "transport_mode": "kite_transport_from_bootstrap_quote",
app/mme_scalpx/integrations/broker_api.py:262:        access_token: str | None = None,
app/mme_scalpx/integrations/broker_api.py:271:        access_token: str | None = None,
app/mme_scalpx/integrations/broker_api.py:280:        access_token: str | None = None,
app/mme_scalpx/integrations/broker_api.py:290:        access_token: str | None = None,
app/mme_scalpx/integrations/broker_api.py:298:        access_token: str | None = None,
app/mme_scalpx/integrations/broker_api.py:306:        access_token: str | None = None,
app/mme_scalpx/integrations/broker_api.py:479:        access_token: str | None = None,
app/mme_scalpx/integrations/broker_api.py:484:        return self.healthcheck_fn(access_token=access_token, provider_id=provider_id)
app/mme_scalpx/integrations/broker_api.py:490:        access_token: str | None = None,
app/mme_scalpx/integrations/broker_api.py:497:            access_token=access_token,
app/mme_scalpx/integrations/broker_api.py:505:        access_token: str | None = None,
app/mme_scalpx/integrations/broker_api.py:512:            access_token=access_token,
app/mme_scalpx/integrations/broker_api.py:521:        access_token: str | None = None,
app/mme_scalpx/integrations/broker_api.py:529:            access_token=access_token,
app/mme_scalpx/integrations/broker_api.py:536:        access_token: str | None = None,
app/mme_scalpx/integrations/broker_api.py:542:            access_token=access_token,
app/mme_scalpx/integrations/broker_api.py:549:        access_token: str | None = None,
app/mme_scalpx/integrations/broker_api.py:557:            access_token=access_token,
app/mme_scalpx/integrations/broker_api.py:581:    This wrapper deliberately does not instantiate KiteConnect itself.
app/mme_scalpx/integrations/broker_api.py:590:        access_token: str | None = None,
app/mme_scalpx/integrations/broker_api.py:601:        access_token: str | None = None,
app/mme_scalpx/integrations/broker_api.py:622:        access_token: str | None = None,
app/mme_scalpx/integrations/broker_api.py:635:        access_token: str | None = None,
app/mme_scalpx/integrations/broker_api.py:648:        access_token: str | None = None,
app/mme_scalpx/integrations/broker_api.py:656:        access_token: str | None = None,
app/mme_scalpx/integrations/broker_api.py:743:                access_token=self._transport_access_token(require_for_call=False),
app/mme_scalpx/integrations/broker_api.py:775:                access_token=self._transport_access_token(),
app/mme_scalpx/integrations/broker_api.py:836:                access_token=self._transport_access_token(),
app/mme_scalpx/integrations/broker_api.py:861:                access_token=self._transport_access_token(),
app/mme_scalpx/integrations/broker_api.py:875:                access_token=self._transport_access_token(),
app/mme_scalpx/integrations/broker_api.py:958:    def _transport_access_token(self, *, require_for_call: bool = True) -> str | None:
app/mme_scalpx/integrations/broker_api.py:967:            return self.auth_manager.get_access_token(ensure_authenticated=True)
app/mme_scalpx/integrations/broker_api.py:1016:                access_token=self._transport_access_token(),
app/mme_scalpx/integrations/broker_auth.py:303:    access_token: str
app/mme_scalpx/integrations/broker_auth.py:315:            "access_token",
app/mme_scalpx/integrations/broker_auth.py:316:            _require_non_empty_str(self.access_token, "access_token"),
app/mme_scalpx/integrations/broker_auth.py:1087:    def get_access_token(
app/mme_scalpx/integrations/broker_auth.py:1102:            return self._state.session.access_token
app/mme_scalpx/integrations/broker_auth.py:1187:                access_token=normalized_session.access_token,
app/mme_scalpx/integrations/broker_auth.py:1202:                access_token=normalized_session.access_token,
app/mme_scalpx/integrations/login.py:11:- perform Zerodha request_token -> access_token session exchange
app/mme_scalpx/integrations/login.py:70:    from kiteconnect import KiteConnect  # type: ignore
app/mme_scalpx/integrations/login.py:72:    KiteConnect = None  # type: ignore
app/mme_scalpx/integrations/login.py:281:    access_token_present: bool
app/mme_scalpx/integrations/login.py:290:            f"access_token={'present' if self.access_token_present else 'missing'} "
app/mme_scalpx/integrations/login.py:297:    api_key: str
app/mme_scalpx/integrations/login.py:300:    access_token: Optional[str]
app/mme_scalpx/integrations/login.py:306:    access_token: Optional[str]
app/mme_scalpx/integrations/login.py:307:    api_key: Optional[str]
app/mme_scalpx/integrations/login.py:417:    if not _normalize_str(api.api_key):
app/mme_scalpx/integrations/login.py:418:        raise StartupValidationError("api.json missing non-empty api_key for Zerodha")
app/mme_scalpx/integrations/login.py:423:        api_key=_normalize_str(api.api_key),
app/mme_scalpx/integrations/login.py:426:        access_token=_env("ZERODHA_ACCESS_TOKEN", "MME_ZERODHA_ACCESS_TOKEN") or None,
app/mme_scalpx/integrations/login.py:434:    env_access_token = _first_non_empty(
app/mme_scalpx/integrations/login.py:435:        args.zerodha_access_token,
app/mme_scalpx/integrations/login.py:443:                api_key=cfg.api_key,
app/mme_scalpx/integrations/login.py:446:                access_token=env_access_token,
app/mme_scalpx/integrations/login.py:451:    api_key = _env("ZERODHA_API_KEY", "MME_ZERODHA_API_KEY")
app/mme_scalpx/integrations/login.py:454:    if not api_key:
app/mme_scalpx/integrations/login.py:455:        raise StartupValidationError("missing Zerodha api_key in api.json or environment")
app/mme_scalpx/integrations/login.py:459:        api_key=api_key,
app/mme_scalpx/integrations/login.py:462:        access_token=env_access_token,
app/mme_scalpx/integrations/login.py:476:    if KiteConnect is None:
app/mme_scalpx/integrations/login.py:533:    access_token = _normalize_str(session_payload.get("access_token"))
app/mme_scalpx/integrations/login.py:534:    if not access_token:
app/mme_scalpx/integrations/login.py:535:        raise BrokerAuthError("Zerodha generate_session() payload missing access_token")
app/mme_scalpx/integrations/login.py:556:        access_token=access_token,
app/mme_scalpx/integrations/login.py:565:def _save_zerodha_broker_session(access_token: str) -> Path:
app/mme_scalpx/integrations/login.py:569:            "ZERODHA_ACCESS_TOKEN": access_token,
app/mme_scalpx/integrations/login.py:574:def _save_dhan_broker_session(access_token: str) -> Path:
app/mme_scalpx/integrations/login.py:578:            "DHAN_ACCESS_TOKEN": access_token,
app/mme_scalpx/integrations/login.py:586:            f"tokens.json broker must be 'zerodha' for Zerodha reuse, got: {state.broker!r}"
app/mme_scalpx/integrations/login.py:588:    if not _normalize_str(state.access_token):
app/mme_scalpx/integrations/login.py:589:        raise StartupValidationError("tokens.json missing non-empty Zerodha access_token")
app/mme_scalpx/integrations/login.py:597:    if KiteConnect is None:
app/mme_scalpx/integrations/login.py:602:    env_token = _normalize_str(cfg.access_token)
app/mme_scalpx/integrations/login.py:611:            token_store_token = _normalize_str(state.access_token)
app/mme_scalpx/integrations/login.py:623:        kite = KiteConnect(api_key=cfg.api_key)
app/mme_scalpx/integrations/login.py:624:        kite.set_access_token(candidate_token)
app/mme_scalpx/integrations/login.py:656:            access_token=candidate_token,
app/mme_scalpx/integrations/login.py:670:            access_token_present=True,
app/mme_scalpx/integrations/login.py:685:    if KiteConnect is None:
app/mme_scalpx/integrations/login.py:696:    kite = KiteConnect(api_key=cfg.api_key)
app/mme_scalpx/integrations/login.py:711:    access_token = _normalize_str(session_payload.get("access_token"))
app/mme_scalpx/integrations/login.py:712:    if not access_token:
app/mme_scalpx/integrations/login.py:713:        raise BrokerAuthError("Zerodha generate_session() payload missing access_token")
app/mme_scalpx/integrations/login.py:715:    kite.set_access_token(access_token)
app/mme_scalpx/integrations/login.py:721:    _save_zerodha_broker_session(access_token)
app/mme_scalpx/integrations/login.py:728:        access_token_present=True,
app/mme_scalpx/integrations/login.py:743:    api_key = (
app/mme_scalpx/integrations/login.py:744:        _normalize_str(getattr(api, "api_key", ""))
app/mme_scalpx/integrations/login.py:764:    access_token = _first_non_empty(
app/mme_scalpx/integrations/login.py:765:        args.dhan_access_token,
app/mme_scalpx/integrations/login.py:768:    resolved_api_key = _first_non_empty(args.dhan_api_key, api_key) or None
app/mme_scalpx/integrations/login.py:781:        access_token=access_token,
app/mme_scalpx/integrations/login.py:782:        api_key=resolved_api_key,
app/mme_scalpx/integrations/login.py:790:def generate_dhan_access_token_via_api(cfg: DhanLoginConfig) -> dict[str, Any]:
app/mme_scalpx/integrations/login.py:808:    access_token = _normalize_str(payload.get("accessToken"))
app/mme_scalpx/integrations/login.py:809:    if not access_token:
app/mme_scalpx/integrations/login.py:814:def renew_dhan_access_token(cfg: DhanLoginConfig, active_access_token: str) -> dict[str, Any]:
app/mme_scalpx/integrations/login.py:815:    if not _normalize_str(active_access_token):
app/mme_scalpx/integrations/login.py:822:            "access-token": active_access_token,
app/mme_scalpx/integrations/login.py:829:    access_token = _normalize_str(
app/mme_scalpx/integrations/login.py:830:        payload.get("accessToken") or payload.get("access_token")
app/mme_scalpx/integrations/login.py:832:    if not access_token:
app/mme_scalpx/integrations/login.py:834:        payload["accessToken"] = active_access_token
app/mme_scalpx/integrations/login.py:838:def verify_dhan_access_token(
app/mme_scalpx/integrations/login.py:840:    access_token: str,
app/mme_scalpx/integrations/login.py:851:            "access-token": access_token,
app/mme_scalpx/integrations/login.py:862:    access_token: str,
app/mme_scalpx/integrations/login.py:893:        access_token=access_token,
app/mme_scalpx/integrations/login.py:912:    access_token = _normalize_str(cfg.access_token)
app/mme_scalpx/integrations/login.py:914:        session_payload = generate_dhan_access_token_via_api(cfg)
app/mme_scalpx/integrations/login.py:915:        access_token = _normalize_str(session_payload.get("accessToken"))
app/mme_scalpx/integrations/login.py:917:        if not access_token:
app/mme_scalpx/integrations/login.py:921:        session_payload = renew_dhan_access_token(cfg, access_token)
app/mme_scalpx/integrations/login.py:922:        access_token = _normalize_str(
app/mme_scalpx/integrations/login.py:923:            session_payload.get("accessToken") or access_token
app/mme_scalpx/integrations/login.py:926:    if not access_token:
app/mme_scalpx/integrations/login.py:932:        verify_dhan_access_token(cfg, access_token, enabled=do_verify)
app/mme_scalpx/integrations/login.py:945:        access_token=access_token,
app/mme_scalpx/integrations/login.py:951:    # shared/tokens.json is Zerodha-owned because Zerodha bootstrap_quote,
app/mme_scalpx/integrations/login.py:954:    _save_dhan_broker_session(access_token)
app/mme_scalpx/integrations/login.py:972:        access_token_present=True,
app/mme_scalpx/ops/validate_bootstrap_provider.py:33:    print("bootstrap_quote =", payload["bootstrap_quote"])
app/mme_scalpx/integrations/dhan_marketdata.py:421:    def fetch_chain_snapshot(self, *, access_token: str | None = None) -> Any:
app/mme_scalpx/integrations/dhan_marketdata.py:1184:            access_token=self._auth_token_or_none(),
app/mme_scalpx/integrations/dhan_marketdata.py:1428:            return self._auth_manager.get_access_token(ensure_authenticated=True)
app/mme_scalpx/integrations/bootstrap_quote.py:2:app/mme_scalpx/integrations/bootstrap_quote.py
app/mme_scalpx/integrations/bootstrap_quote.py:9:- create authenticated KiteConnect client
app/mme_scalpx/integrations/bootstrap_quote.py:39:    from kiteconnect import KiteConnect  # type: ignore
app/mme_scalpx/integrations/bootstrap_quote.py:42:        "kiteconnect is required by app.mme_scalpx.integrations.bootstrap_quote"
app/mme_scalpx/integrations/bootstrap_quote.py:127:    if not api.api_key.strip():
app/mme_scalpx/integrations/bootstrap_quote.py:128:        raise StartupValidationError("api.json missing non-empty api_key")
app/mme_scalpx/integrations/bootstrap_quote.py:134:            f"tokens.json broker must be 'zerodha', got {state.broker!r}"
app/mme_scalpx/integrations/bootstrap_quote.py:136:    if not state.access_token.strip():
app/mme_scalpx/integrations/bootstrap_quote.py:137:        raise StartupValidationError("tokens.json missing non-empty access_token")
app/mme_scalpx/integrations/bootstrap_quote.py:140:def build_kite(api: BrokerApiConfig, state: BrokerTokenState) -> KiteConnect:
app/mme_scalpx/integrations/bootstrap_quote.py:141:    kite = KiteConnect(api_key=api.api_key)
app/mme_scalpx/integrations/bootstrap_quote.py:142:    kite.set_access_token(state.access_token)
app/mme_scalpx/integrations/bootstrap_quote.py:171:def fetch_underlying_ltp(instrument_key: str = DEFAULT_UNDERLYING_KEY) -> BootstrapQuote:
app/mme_scalpx/integrations/instrument_master_sync.py:53:    from kiteconnect import KiteConnect  # type: ignore
app/mme_scalpx/integrations/instrument_master_sync.py:157:    if not api.api_key.strip():
app/mme_scalpx/integrations/instrument_master_sync.py:158:        raise StartupValidationError("api.json missing non-empty api_key")
app/mme_scalpx/integrations/instrument_master_sync.py:164:            f"tokens.json broker must be 'zerodha', got {state.broker!r}"

## Safety remains zero
orders_stream_len=0
risk_stream_len=0
execution_stream_len=0

CLASSIFICATION=PASS_R31D1_AUTH_CONFIG_SEAM_IDENTIFIED_ZERODHA_API_KEY_OR_TOKEN_INVALID
