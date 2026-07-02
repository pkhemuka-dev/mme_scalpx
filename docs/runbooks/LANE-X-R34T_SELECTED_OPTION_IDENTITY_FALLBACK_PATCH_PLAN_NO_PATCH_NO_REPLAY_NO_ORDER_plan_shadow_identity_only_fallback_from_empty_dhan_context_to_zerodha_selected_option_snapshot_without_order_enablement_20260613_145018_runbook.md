# LANE-X-R34T_SELECTED_OPTION_IDENTITY_FALLBACK_PATCH_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_plan_shadow_identity_only_fallback_from_empty_dhan_context_to_zerodha_selected_option_snapshot_without_order_enablement_20260613_145018

classification: PASS_R34T_SELECTED_OPTION_IDENTITY_FALLBACK_PATCH_PLAN_WRITTEN_NO_PATCH_NO_REPLAY_NO_ORDER
proof: `run/proofs/LANE-X-R34T_SELECTED_OPTION_IDENTITY_FALLBACK_PATCH_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_plan_shadow_identity_only_fallback_from_empty_dhan_context_to_zerodha_selected_option_snapshot_without_order_enablement_20260613_145018.json`
audit: `run/audits/LANE-X-R34T_SELECTED_OPTION_IDENTITY_FALLBACK_PATCH_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_plan_shadow_identity_only_fallback_from_empty_dhan_context_to_zerodha_selected_option_snapshot_without_order_enablement_20260613_145018`

## Safety
- compile_rc: 0
- orders/risk/execution: 0 / 0 / 0
- risk/execution proc: 0 / 0

## Patch plan: shadow identity only

### Problem
DHAN context can be fresh but empty. In that case selected_call/selected_put identity fields remain blank, so fresh candidate-truth rows may still lack symbol/token.

### Do not change
- Do not enable paper/live.
- Do not start risk/execution.
- Do not promote top-level action.
- Do not promote payload_json.action.
- Do not route broker orders.
- Do not treat fallback identity as trade authorization.

### Safe fallback rule
For shadow candidate identity export only:
1. Read DHAN selected_call/selected_put identity first.
2. If DHAN selected side identity is blank, read Zerodha selected-option snapshot identity.
3. Fill only candidate_symbol_shadow/candidate_instrument_token_shadow/symbol/instrument_token in shadow truth.
4. Preserve HOLD everywhere outside shadow fields.

### Candidate implementation options

Option A: patch source publisher so DhanContextState fills selected_call/put identity from Zerodha selected-option snapshot when Dhan context is empty.
- Better for all downstream consumers.
- Must mark fallback_source='ZERODHA_SELECTED_OPTION_IDENTITY_ONLY'.
- Must not mark provider_ready_miso/classic true by itself.

Option B: patch strategy shadow helper to also search view/provider runtime Zerodha selected-option snapshot fields.
- Smaller scope.
- Only helps candidate-truth identity.
- Safer for Monday R34O because it cannot accidentally enable provider readiness.

### Recommendation
Use Option B first for R34U: strategy shadow identity fallback only. It is narrower and safest. Later, fix Dhan context publisher separately if needed.

## Source context
=== DHAN RUNTIME CLIENT CONTEXT ===
  1240	        payload_raw = out.get("payload")
  1241	        payload = dict(payload_raw) if isinstance(payload_raw, Mapping) else {}
  1242	
  1243	        age = self._cache_age_sec(now)
  1244	        stale = bool(age is not None and age > self._stale_after_sec)
  1245	
  1246	        if source == "LIVE":
  1247	            status = "HEALTHY"
  1248	        elif stale:
  1249	            status = "STALE"
  1250	        else:
  1251	            status = "DEGRADED"
  1252	
  1253	        payload.update(
  1254	            {
  1255	                "context_status": status,
  1256	                "provider_id": "DHAN",
  1257	                "context_source": source,
  1258	                "context_cache_age_sec": age,
  1259	                "context_stale": stale,
  1260	                "context_backoff_active": now < self._backoff_until_monotonic,
  1261	                "context_consecutive_failures": self._consecutive_failures,
  1262	                "context_last_error_kind": self._last_error_kind,
  1263	                "context_last_error": self._last_error,
  1264	            }
  1265	        )
  1266	
  1267	        out["record_type"] = out.get("record_type") or "dhan_context"
  1268	        out["payload"] = payload
  1269	        return out
  1270	
  1271	    def _build_item_from_snapshot(self, snap: Mapping[str, Any]) -> dict[str, Any] | None:
  1272	        """
  1273	        Build a feeds.py-compatible Dhan option context item from /optionchain.
  1274	
  1275	        Batch 25V corrective:
  1276	        the previous implementation emitted only selected keys/scores, which made
  1277	        HASH_STATE_DHAN_CONTEXT fresh but empty:
  1278	        option_chain_ladder_json=[], selected_call_context_json={}.
  1279	        This method now carries normalized option-chain rows so feeds.py can
  1280	        persist the frozen Dhan ladder contract.
  1281	        """
  1282	        if not isinstance(snap, Mapping) or not snap:
  1283	            return None
  1284	
  1285	        ts_event_ns = time.time_ns()
  1286	        rows = _batch25v_option_chain_rows_from_snapshot(snap, ts_event_ns=ts_event_ns)
  1287	
  1288	        ce_atm = getattr(self._runtime_instruments, "ce_atm", None)
  1289	        pe_atm = getattr(self._runtime_instruments, "pe_atm", None)
  1290	
  1291	        atm_strike = None
  1292	        if ce_atm is not None:
  1293	            atm_strike = _as_float(getattr(ce_atm, "strike", None))
  1294	        if atm_strike is None and pe_atm is not None:
  1295	            atm_strike = _as_float(getattr(pe_atm, "strike", None))
  1296	
  1297	        selected_call_key = ""
  1298	        selected_put_key = ""
  1299	        selected_call_security_id = ""
  1300	        selected_put_security_id = ""
  1301	
  1302	        if ce_atm is not None:
  1303	            selected_call_key = str(getattr(ce_atm, "instrument_key", "") or "")
  1304	        if pe_atm is not None:
  1305	            selected_put_key = str(getattr(pe_atm, "instrument_key", "") or "")
  1306	
  1307	        selected_call_context: dict[str, Any] = {}
  1308	        selected_put_context: dict[str, Any] = {}
  1309	
  1310	        if atm_strike is not None:
  1311	            for row in rows:
  1312	                try:
  1313	                    row_strike = float(row.get("strike"))
  1314	                except Exception:
  1315	                    continue
  1316	                if abs(row_strike - float(atm_strike)) > 0.001:
  1317	                    continue
  1318	
  1319	                side = str(row.get("side") or row.get("option_type") or "").upper()
  1320	                if side in {"CALL", "CE"} and not selected_call_context:
  1321	                    selected_call_context = dict(row)
  1322	                    selected_call_security_id = str(row.get("dhan_security_id") or row.get("instrument_token") or "")
  1323	                elif side in {"PUT", "PE"} and not selected_put_context:
  1324	                    selected_put_context = dict(row)
  1325	                    selected_put_security_id = str(row.get("dhan_security_id") or row.get("instrument_token") or "")
  1326	
  1327	        selected_call_score = _batch25v_safe_float(selected_call_context.get("score"), 0.0) or 0.0
  1328	        selected_put_score = _batch25v_safe_float(selected_put_context.get("score"), 0.0) or 0.0
  1329	
  1330	        payload = {
  1331	            "context_status": "HEALTHY" if rows else "DEGRADED",
  1332	            "provider_id": "DHAN",
  1333	            "context_source": "LIVE",
  1334	            "context_epoch_ns": ts_event_ns,
  1335	            "atm_strike": atm_strike,
  1336	            "selected_call_instrument_key": selected_call_key or selected_call_context.get("instrument_key", ""),
  1337	            "selected_put_instrument_key": selected_put_key or selected_put_context.get("instrument_key", ""),
  1338	            "selected_call_security_id": selected_call_security_id,
  1339	            "selected_put_security_id": selected_put_security_id,
  1340	            "selected_call_score": selected_call_score,
  1341	            "selected_put_score": selected_put_score,
  1342	            "option_chain_ladder": rows,
  1343	            "strike_ladder": rows,
  1344	            "option_chain_ladder_json": json.dumps(rows, separators=(",", ":"), sort_keys=True),
  1345	            "strike_ladder_json": json.dumps(rows, separators=(",", ":"), sort_keys=True),
  1346	            "selected_call_context": selected_call_context,
  1347	            "selected_put_context": selected_put_context,
  1348	            "selected_call_context_json": json.dumps(selected_call_context, separators=(",", ":"), sort_keys=True),
  1349	            "selected_put_context_json": json.dumps(selected_put_context, separators=(",", ":"), sort_keys=True),
  1350	        }
  1351	
  1352	        return {
  1353	            "record_type": "dhan_context",
  1354	            "payload": payload,
  1355	        }
  1356	
  1357	    def poll(self) -> list[dict[str, Any]]:
  1358	        now = time.monotonic()
  1359	
  1360	        if now < self._backoff_until_monotonic:
  1361	            if self._emit_cached_during_backoff and self._last_good_item is not None:
  1362	                return [
  1363	                    self._decorate_cached_item(
  1364	                        self._last_good_item,
  1365	                        now=now,

=== PROVIDER RUNTIME CONTEXT ===
   260	    if status == names.PROVIDER_STATUS_STALE:
   261	        return names.PROVIDER_TRANSITION_REASON_STALE_DATA
   262	    if status == names.PROVIDER_STATUS_AUTH_FAILED:
   263	        return names.PROVIDER_TRANSITION_REASON_AUTH_FAILED
   264	    if status in (
   265	        names.PROVIDER_STATUS_DEGRADED,
   266	        names.PROVIDER_STATUS_UNAVAILABLE,
   267	        names.PROVIDER_STATUS_DISABLED,
   268	    ):
   269	        return names.PROVIDER_TRANSITION_REASON_HEALTH_FAIL
   270	    return names.PROVIDER_TRANSITION_REASON_FAILOVER_ACTIVATED
   271	
   272	
   273	def _determine_provider_status(
   274	    *,
   275	    provider_id: str,
   276	    role: str,
   277	    provider_health_map: Mapping[str, models.ProviderHealthState],
   278	    dhan_context_state: models.DhanContextState | None,
   279	) -> str:
   280	    """
   281	    Resolve provider status for a specific runtime role.
   282	
   283	    Freeze law:
   284	    Dhan provider-level health is not option-chain/context health.
   285	    For option_context + DHAN, a concrete DhanContextState is mandatory.
   286	    Without it, the context lane is UNAVAILABLE even if generic Dhan
   287	    market-data health is HEALTHY.
   288	    """
   289	
   290	    if role == names.PROVIDER_ROLE_OPTION_CONTEXT and provider_id == names.PROVIDER_DHAN:
   291	        if dhan_context_state is None:
   292	            return names.PROVIDER_STATUS_UNAVAILABLE
   293	
   294	        context_status = dhan_context_state.context_status
   295	        health_state = provider_health_map.get(provider_id)
   296	
   297	        if health_state is None:
   298	            return context_status
   299	
   300	        base_status = health_state.status
   301	
   302	        if base_status == names.PROVIDER_STATUS_DISABLED:
   303	            return names.PROVIDER_STATUS_DISABLED
   304	
   305	        if health_state.authenticated is False:
   306	            return names.PROVIDER_STATUS_AUTH_FAILED
   307	
   308	        if context_status in (
   309	            names.PROVIDER_STATUS_AUTH_FAILED,
   310	            names.PROVIDER_STATUS_STALE,
   311	            names.PROVIDER_STATUS_UNAVAILABLE,
   312	            names.PROVIDER_STATUS_DISABLED,
   313	        ):
   314	            return context_status
   315	
   316	        if health_state.stale:
   317	            return names.PROVIDER_STATUS_STALE
   318	
   319	        return context_status
   320	
   321	    health_state = provider_health_map.get(provider_id)
   322	    if health_state is None:
   323	        return names.PROVIDER_STATUS_UNAVAILABLE
   324	
   325	    base_status = health_state.status
   326	
   327	    if base_status == names.PROVIDER_STATUS_DISABLED:
   328	        return names.PROVIDER_STATUS_DISABLED
   329	
   330	    if health_state.authenticated is False:
   331	        return names.PROVIDER_STATUS_AUTH_FAILED
   332	
   333	    if health_state.stale:
   334	        return names.PROVIDER_STATUS_STALE
   335	
   336	    if role in (
   337	        names.PROVIDER_ROLE_FUTURES_MARKETDATA,
   338	        names.PROVIDER_ROLE_SELECTED_OPTION_MARKETDATA,
   339	    ) and health_state.marketdata_healthy is False:
   340	        if base_status in (
   341	            names.PROVIDER_STATUS_HEALTHY,
   342	            names.PROVIDER_STATUS_FAILOVER_ACTIVE,
   343	        ):
   344	            return names.PROVIDER_STATUS_DEGRADED
   345	        return base_status
   346	
   347	    if role in (
   348	        names.PROVIDER_ROLE_EXECUTION_PRIMARY,
   349	        names.PROVIDER_ROLE_EXECUTION_FALLBACK,
   350	    ) and health_state.execution_healthy is False:
   351	        if base_status in (
   352	            names.PROVIDER_STATUS_HEALTHY,
   353	            names.PROVIDER_STATUS_FAILOVER_ACTIVE,
   354	        ):
   355	            return names.PROVIDER_STATUS_DEGRADED
   356	        return base_status
   357	
   358	    return base_status
   359	
   360	
   361	def _candidate_order_for_role(
   362	    *,
   363	    role: str,
   364	    override_mode: str,
   365	) -> tuple[str, ...]:
   366	    baseline = _BASELINE_ROLE_PROVIDER_ORDER[role]
   367	
   368	    if role == names.PROVIDER_ROLE_OPTION_CONTEXT:
   369	        return baseline
   370	
   980	            else names.PROVIDER_TRANSITION_REASON_BOOTSTRAP
   981	        )
   982	    )
   983	
   984	    setup_rebuild_required, setup_rebuild_reason = _build_setup_rebuild_flags(
   985	        role_choices=role_choices,
   986	        inputs=inputs,
   987	    )
   988	
   989	    messages = [
   990	        choice.message
   991	        for choice in role_choices.values()
   992	        if choice.message is not None
   993	    ]
   994	    if setup_rebuild_reason is not None:
   995	        messages.append(setup_rebuild_reason)
   996	    message = "; ".join(messages) if messages else None
   997	
   998	    runtime_state = models.ProviderRuntimeState(
   999	        ts_event_ns=inputs.ts_event_ns,
