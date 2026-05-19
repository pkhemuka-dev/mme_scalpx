# A6-PAPER-R15_controlled_paper_trial_static_preflight_risk_execution_route_surface_no_start_no_order_no_paper_20260519_104436

Verdict: `PASS_A6_PAPER_R15_CONTROLLED_PAPER_TRIAL_STATIC_PREFLIGHT_NO_START_NO_ORDER_NO_PAPER`

Lane: A6-PAPER / controlled-paper trial static preflight only.

## Boundary
- No paper order.
- No real live.
- No broker order.
- No real money.
- No risk/execution start.
- No source patch.
- No service start/stop.
- No Redis mutation.
- `orders:mme:stream` must remain 0.
- Position must remain FLAT.

## Static summary
- source_files_inspected: `['app/mme_scalpx/services/risk.py', 'app/mme_scalpx/services/execution.py', 'app/mme_scalpx/services/strategy.py', 'app/mme_scalpx/services/controlled_paper_route.py', 'app/mme_scalpx/services/controlled_paper_observability.py', 'app/mme_scalpx/main.py', 'app/mme_scalpx/core/names.py', 'app/mme_scalpx/core/settings.py', 'app/mme_scalpx/core/models.py', 'app/mme_scalpx/integrations/broker_api.py', 'app/mme_scalpx/integrations/provider_runtime.py']`
- risk_execution_surface_present: `True`
- paper_guard_surface_present: `True`
- compile_all_ok: `True`
- parse_all_ok: `True`
- import_checks_ok: `True`
- note: `Dangerous call inventory is inspection-only, not an automatic blocker in R15 because risk/execution/order modules naturally contain order/position code. Future R16 must decide exact arming sequence and kill rules.`

## Dangerous call inventory
### app/mme_scalpx/services/risk.py
- line 1976: `RX.xadd_fields(self.keys.system_health_stream, {'event_type': event, 'service_name': N.SERVICE_RISK, 'instance_id': self.cfg.instance_id, 'status': status, 'detail': detail, 'ts_ns': str(ts_ns), 'ts_event_ns': str(ts_ns)}, maxlen_approx=DEFAULT_HEALT`
- line 1999: `RX.xadd_fields(self.keys.system_errors_stream, {'event_type': event, 'service_name': N.SERVICE_RISK, 'instance_id': self.cfg.instance_id, 'detail': detail, 'ts_ns': str(ts_ns), 'ts_event_ns': str(ts_ns)}, maxlen_approx=DEFAULT_ERROR_STREAM_MAXLEN, cl`
- line 2283: `_batch26c_flatten_values(cfg)`
- line 987: `RX.xadd_fields(N.STREAM_SYSTEM_HEALTH, {'event_type': event, 'service_name': N.SERVICE_RISK, 'instance_id': self.cfg.instance_id, 'status': status, 'detail': detail, 'ts_ns': str(ts_ns)}, maxlen_approx=DEFAULT_HEALTH_STREAM_MAXLEN, client=self.redis)`
- line 1008: `RX.xadd_fields(N.STREAM_SYSTEM_ERRORS, {'event_type': event, 'service_name': N.SERVICE_RISK, 'instance_id': self.cfg.instance_id, 'detail': detail, 'ts_ns': str(ts_ns)}, maxlen_approx=DEFAULT_ERROR_STREAM_MAXLEN, client=self.redis)`
- line 1309: `_safe_str(payload.get('broker_order_id'))`
- line 1093: `hasattr(_client, 'xadd')`
- line 1094: `_client.xadd(_stream, _fields)`
- line 1309: `payload.get('broker_order_id')`
### app/mme_scalpx/services/execution.py
- line 2386: `RX.xadd_fields(N.STREAM_DECISIONS_ACK, payload, maxlen_approx=self.stream_maxlen, client=self.redis)`
- line 2465: `_status_upper(broker_order.get('status'))`
- line 2484: `_BATCH13_ORIGINAL_APPLY_BROKER_ORDER_UPDATE(self, pending, broker_order, current_ns)`
- line 450: `PendingOrder(intent=_safe_str(raw.get('intent')), action=_safe_str(raw.get('action')), decision_id=_safe_str(raw.get('decision_id')), client_order_id=_safe_str(raw.get('client_order_id')), option_symbol=_safe_str(raw.get('option_symbol')), option_tok`
- line 646: `_safe_str(raw.get('broker_order_id'))`
- line 960: `self._apply_broker_order_update(pending, broker_order, current_ns)`
- line 1003: `self._publish_ack_simple(ack_type=N.ACK_FAILED, decision_id=pending.decision_id, reason='entry_timeout_cancelled', broker_order=None, entry_mode=pending.entry_mode)`
- line 1058: `_safe_str(broker_state.get('broker_order_id'))`
- line 1142: `_safe_str(tracked.get('broker_order_id'))`
- line 1219: `self._publish_ack(ack_type=N.ACK_RECEIVED, decision=decision, reason='decision_received', broker_order=None)`
- line 1325: `_safe_str(broker_order.get('broker_order_id'))`
- line 1326: `_status_upper(broker_order.get('status'))`
- line 1327: `_safe_int(broker_order.get('filled_quantity'), 0)`
- line 1328: `_safe_str(broker_order.get('avg_fill_price'))`
- line 1340: `self._publish_order_event(event_type='ENTRY_ORDER_SUBMITTED', decision=decision, broker_order=broker_order, requested_limit_price=requested_limit_price, quantity=pending.qty_lots, entry_mode=entry_mode)`
- line 1348: `self._publish_ack(ack_type=N.ACK_SENT_TO_BROKER, decision=decision, reason='entry_sent_to_broker', broker_order=broker_order)`
- line 1354: `self._apply_broker_order_update(pending, broker_order, current_ns)`
- line 1424: `_safe_str(broker_order.get('broker_order_id'))`
- line 1425: `_status_upper(broker_order.get('status'))`
- line 1426: `_safe_int(broker_order.get('filled_quantity'), 0)`
### app/mme_scalpx/services/strategy.py
- line 1042: `self.redis.xadd(STREAM_DECISIONS, fields=fields, maxlen=DEFAULT_STREAM_MAXLEN, approximate=True)`
- line 1061: `self.redis.hset(KEY_HEALTH_STRATEGY, mapping=payload)`
- line 1064: `self.redis.xadd(STREAM_HEALTH, fields=payload, maxlen=DEFAULT_STREAM_MAXLEN, approximate=True)`
- line 1084: `self.redis.xadd(STREAM_ERRORS, fields=payload, maxlen=DEFAULT_STREAM_MAXLEN, approximate=True)`
### app/mme_scalpx/main.py
- line 164: `RuntimeError('b1_execution_shadow_no_broker_refuses_cancel_order')`
- line 124: `os.environ.get('SCALPX_ALLOW_BROKER_ORDERS')`
### app/mme_scalpx/core/names.py
- line 1864: `StateHashSet(instruments_mme=HASH_STATE_INSTRUMENTS_MME, snapshot_mme_fut=HASH_STATE_SNAPSHOT_MME_FUT, snapshot_mme_opt_selected=HASH_STATE_SNAPSHOT_MME_OPT_SELECTED, features_mme_fut=HASH_STATE_FEATURES_MME_FUT, baselines_mme_fut=HASH_STATE_BASELINE`
- line 1882: `StateHashSet(instruments_mme=HASH_REPLAY_STATE_INSTRUMENTS_MME, snapshot_mme_fut=HASH_REPLAY_STATE_SNAPSHOT_MME_FUT, snapshot_mme_opt_selected=HASH_REPLAY_STATE_SNAPSHOT_MME_OPT_SELECTED, features_mme_fut=HASH_REPLAY_STATE_FEATURES_MME_FUT, baselines`
- line 1900: `HealthSet(login=KEY_HEALTH_LOGIN, instruments=KEY_HEALTH_INSTRUMENTS, feeds=KEY_HEALTH_FEEDS, features=KEY_HEALTH_FEATURES, strategy=KEY_HEALTH_STRATEGY, risk=KEY_HEALTH_RISK, execution=KEY_HEALTH_EXECUTION, monitor=KEY_HEALTH_MONITOR, report=KEY_HEA`
- line 1912: `HealthSet(login=KEY_REPLAY_HEALTH_LOGIN, instruments=KEY_REPLAY_HEALTH_INSTRUMENTS, feeds=KEY_REPLAY_HEALTH_FEEDS, features=KEY_REPLAY_HEALTH_FEATURES, strategy=KEY_REPLAY_HEALTH_STRATEGY, risk=KEY_REPLAY_HEALTH_RISK, execution=KEY_REPLAY_HEALTH_EXEC`
- line 1942: `ProviderStateHashSet(snapshot_mme_fut_zerodha=HASH_STATE_SNAPSHOT_MME_FUT_ZERODHA, snapshot_mme_fut_dhan=HASH_STATE_SNAPSHOT_MME_FUT_DHAN, snapshot_mme_fut_active=HASH_STATE_SNAPSHOT_MME_FUT_ACTIVE, snapshot_mme_opt_selected_zerodha=HASH_STATE_SNAPSH`
- line 1953: `ProviderStateHashSet(snapshot_mme_fut_zerodha=HASH_REPLAY_STATE_SNAPSHOT_MME_FUT_ZERODHA, snapshot_mme_fut_dhan=HASH_REPLAY_STATE_SNAPSHOT_MME_FUT_DHAN, snapshot_mme_fut_active=HASH_REPLAY_STATE_SNAPSHOT_MME_FUT_ACTIVE, snapshot_mme_opt_selected_zero`
- line 1964: `ProviderHealthSet(zerodha_auth=KEY_HEALTH_ZERODHA_AUTH, zerodha_marketdata=KEY_HEALTH_ZERODHA_MARKETDATA, zerodha_execution=KEY_HEALTH_ZERODHA_EXECUTION, dhan_auth=KEY_HEALTH_DHAN_AUTH, dhan_marketdata=KEY_HEALTH_DHAN_MARKETDATA, dhan_execution=KEY_H`
- line 1974: `ProviderHealthSet(zerodha_auth=KEY_REPLAY_HEALTH_ZERODHA_AUTH, zerodha_marketdata=KEY_REPLAY_HEALTH_ZERODHA_MARKETDATA, zerodha_execution=KEY_REPLAY_HEALTH_ZERODHA_EXECUTION, dhan_auth=KEY_REPLAY_HEALTH_DHAN_AUTH, dhan_marketdata=KEY_REPLAY_HEALTH_DH`
- line 2531: `tuple((name for name in globals() if name.isupper() or name in {'NamesContractError', 'ServiceDef', 'StreamSet', 'StateHashSet', 'HealthSet', 'LockSet', 'GroupSet', 'ProviderStreamSet', 'ProviderStateHashSet', 'ProviderHealthSet', 'ensure_live_name',`
### app/mme_scalpx/core/models.py
- line 1331: `_require(self.position_effect in (names.POSITION_EFFECT_CLOSE, names.POSITION_EFFECT_REDUCE, names.POSITION_EFFECT_FLATTEN), 'EXIT requires CLOSE / REDUCE / FLATTEN position_effect')`
- line 1775: `_optional_non_empty_str(self.broker_order_id, 'broker_order_id')`
- line 1805: `_optional_non_empty_str(self.broker_order_id, 'broker_order_id')`
- line 2641: `_optional_non_empty_str(self.last_broker_order_id, 'last_broker_order_id')`
### app/mme_scalpx/integrations/broker_api.py
- line 510: `self.place_order_fn(payload, access_token=access_token, provider_id=provider_id)`
- line 526: `self.cancel_order_fn(order_id, payload, access_token=access_token, provider_id=provider_id)`
- line 625: `self.kite.place_order(**dict(payload))`
- line 640: `self.kite.cancel_order(**kwargs)`
- line 901: `self._place_order_common(intent='entry', tradingsymbol=tradingsymbol, exchange=exchange, transaction_type=transaction_type, quantity=quantity, product=product, order_type=order_type, variety=variety, price=price, trigger_price=trigger_price, validity`
- line 933: `self._place_order_common(intent='exit', tradingsymbol=tradingsymbol, exchange=exchange, transaction_type=transaction_type, quantity=quantity, product=product, order_type=order_type, variety=variety, price=price, trigger_price=trigger_price, validity=`
- line 1527: `ControlledPaperOrderResult(ok=False, status='FAIL_CLOSED_REAL_LIVE_FORBIDDEN', reason='real_live_or_broker_order_env_present', route=route, order_sent=False, order_created=False, broker_calls_executed=False, real_live_forbidden=True, paper_backend_ac`
- line 509: `BrokerAdapterUnavailableError('place_order_fn not configured')`
- line 525: `BrokerAdapterUnavailableError('cancel_order_fn not configured')`
- line 833: `transport.cancel_order(order_id, payload, access_token=self._transport_access_token(), provider_id=self.provider_id)`
- line 843: `self._augment_response(raw, intent='cancel_order', request={'order_id': order_id, **payload})`
- line 1014: `transport.place_order(payload, access_token=self._transport_access_token(), provider_id=self.provider_id)`
- line 840: `BrokerAdapterRequestError(f'cancel_order() failed: {exc}')`

## Future runtime constraints
- R16 remains runbook only: no start/order.
- R17 may inspect arming environment but still no paper order unless all gates true.
- R18 is the earliest possible one-lot controlled-paper trial batch.
- Risk/execution must not start until a future exact approval specifically allows it.
- Paper route must remain fail-closed unless controlled-paper runtime env, scope ack, paper enabled, paper armed, safety facts, and no live/broker flags all pass.
- Broker/live flags must remain unset for controlled-paper trial.
- orders:mme:stream must be zero before any arming attempt.
- position must be FLAT before any arming attempt.

## Required next approval
```text
I APPROVE A6 CONTROLLED-PAPER RUNTIME PRE-ARM RUNBOOK ONLY: NO PAPER ORDER YET, NO REAL LIVE, NO BROKER ORDER, NO REAL MONEY, NO RISK/EXECUTION START YET, ORDERS STREAM MUST REMAIN 0, POSITION MUST REMAIN FLAT
```
