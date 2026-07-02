# R35C_R5A3_EXECUTION_SHADOW_PNL_FIELDS_BLOCK_REWRITE_NO_REPLAY_NO_ORDER_20260614_002340

classification: PASS_R35C_R5A3_EXECUTION_SHADOW_PNL_FIELDS_PATCHED_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35C_R5A3_EXECUTION_SHADOW_PNL_FIELDS_BLOCK_REWRITE_NO_REPLAY_NO_ORDER_20260614_002340.json`
backup: `run/_code_backups/R35C_R5A3_EXECUTION_SHADOW_PNL_FIELDS_BLOCK_REWRITE_NO_REPLAY_NO_ORDER_20260614_002340_bin_replay_run.py.bak`

patch_rc=0 compile_rc=0 marker_rc=0
safety pre=0/0/0 post=0/0/0 proc=0/0 replay_proc=0

## Patch log
patched=1
replaced_chars=3019

## Patch errors

## Markers
2306:    # R35C/R5A3: replay-only shadow PnL enrichment for execution rows.
2319:    def _r35c_r5a3_shadow_pnl(fill_price, fill_qty):
2328:                "pnl_model_status": "NO_FILL_NO_PNL_R35C_R5A3",
2330:                "exit_reason": None,
2334:                "net_pnl": 0.0,
2339:                "pnl_model": "R35C_R5A3_SYNTHETIC_FIRST_TARGET_REPLAY_ONLY",
2345:        net_pnl = round(net_points * qty, 6)
2348:            "pnl_model_status": "PNL_COMPUTED_SYNTHETIC_FIRST_TARGET_REPLAY_ONLY_R35C_R5A3",
2350:            "exit_reason": "synthetic_first_target",
2354:            "net_pnl": net_pnl,
2355:            "is_profit": net_pnl > 0,
2356:            "is_loss": net_pnl < 0,
2359:            "pnl_model": "R35C_R5A3_SYNTHETIC_FIRST_TARGET_REPLAY_ONLY",
2380:                    **_r35c_r5a3_shadow_pnl(None, 0),
2413:                **_r35c_r5a3_shadow_pnl(fill_result.fill_price, fill_result.fill_qty),

## Builder context
  2280	    return None
  2281	
  2282	
  2283	def build_execution_shadow_results_from_risk_outputs(
  2284	    *,
  2285	    run_id: str,
  2286	    risk_outputs: list[dict[str, Any]] | tuple[dict[str, Any], ...],
  2287	    fill_model_name: str | None,
  2288	    doctrine_mode: DoctrineMode,
  2289	) -> list[dict[str, Any]]:
  2290	    ordered_outputs = sorted(
  2291	        risk_outputs,
  2292	        key=lambda output: (
  2293	            str(output.get("event_time") or ""),
  2294	            str(output.get("risk_channel") or ""),
  2295	            str(output.get("risk_id") or ""),
  2296	        ),
  2297	    )
  2298	
  2299	    model = ReplayFillModelFactory.create(
  2300	        ReplayFillModelConfig(
  2301	            model_name=_resolve_fill_model_name(fill_model_name),
  2302	            doctrine_mode=doctrine_mode,
  2303	        )
  2304	    )
  2305	
  2306	    # R35C/R5A3: replay-only shadow PnL enrichment for execution rows.
  2307	    # Conservative labelled model: entry-fill-only rows get a synthetic first-target
  2308	    # exit using doctrine economics (target_points=5.0, stop_points=4.0).
  2309	    # This does not create broker orders, paper/live orders, Redis writes, risk starts,
  2310	    # execution starts, or production doctrine changes.
  2311	    def _r35c_r5a3_float(value, default=None):
  2312	        try:
  2313	            if value is None or value == "":
  2314	                return default
  2315	            return float(value)
  2316	        except Exception:
  2317	            return default
  2318	
  2319	    def _r35c_r5a3_shadow_pnl(fill_price, fill_qty):
  2320	        qty = int(fill_qty or 0)
  2321	        entry = _r35c_r5a3_float(fill_price)
  2322	        target_points = 5.0
  2323	        stop_points = 4.0
  2324	        cost_points = 0.0
  2325	
  2326	        if qty <= 0 or entry is None:
  2327	            return {
  2328	                "pnl_model_status": "NO_FILL_NO_PNL_R35C_R5A3",
  2329	                "exit_price": None,
  2330	                "exit_reason": None,
  2331	                "gross_points": 0.0,
  2332	                "cost_points": cost_points,
  2333	                "net_points": 0.0,
  2334	                "net_pnl": 0.0,
  2335	                "is_profit": False,
  2336	                "is_loss": False,
  2337	                "target_points": target_points,
  2338	                "stop_points": stop_points,
  2339	                "pnl_model": "R35C_R5A3_SYNTHETIC_FIRST_TARGET_REPLAY_ONLY",
  2340	            }
  2341	
  2342	        exit_price = round(entry + target_points, 6)
  2343	        gross_points = round(exit_price - entry, 6)
  2344	        net_points = round(gross_points - cost_points, 6)
  2345	        net_pnl = round(net_points * qty, 6)
  2346	
  2347	        return {
  2348	            "pnl_model_status": "PNL_COMPUTED_SYNTHETIC_FIRST_TARGET_REPLAY_ONLY_R35C_R5A3",
  2349	            "exit_price": exit_price,
  2350	            "exit_reason": "synthetic_first_target",
  2351	            "gross_points": gross_points,
  2352	            "cost_points": cost_points,
  2353	            "net_points": net_points,
  2354	            "net_pnl": net_pnl,
  2355	            "is_profit": net_pnl > 0,
  2356	            "is_loss": net_pnl < 0,
  2357	            "target_points": target_points,
  2358	            "stop_points": stop_points,
  2359	            "pnl_model": "R35C_R5A3_SYNTHETIC_FIRST_TARGET_REPLAY_ONLY",
  2360	        }
  2361	
  2362	    results: list[dict[str, Any]] = []
  2363	    for index, risk_output in enumerate(ordered_outputs, start=1):
  2364	        risk_action = str(risk_output.get("risk_action") or "HOLD")
  2365	        veto_entry = bool(risk_output.get("veto_entry"))
  2366	        side = _risk_action_to_fill_side(risk_action)
  2367	
  2368	        if veto_entry or side is None:
  2369	            results.append(
  2370	                {
  2371	                    "execution_id": f"execution_shadow_{index:06d}",
  2372	                    "event_time": risk_output.get("event_time"),
  2373	                    "execution_channel": "replay:execution_shadow",
  2374	                    "source_risk_id": risk_output.get("risk_id"),
  2375	                    "risk_action": risk_action,
  2376	                    "filled": False,
  2377	                    "fill_qty": 0,
  2378	                    "fill_price": None,
  2379	                    "slippage": None,
  2380	                    **_r35c_r5a3_shadow_pnl(None, 0),
  2381	                    "reason": "risk_block_or_non_entry",
  2382	                    "symbol": risk_output.get("symbol"),
  2383	                    "metadata": dict(risk_output.get("metadata") or {}),
  2384	                }
  2385	            )
  2386	            continue
  2387	
  2388	        fill_request = ReplayFillRequest(
  2389	            run_id=run_id,
  2390	            order_id=f"shadow_order_{index:06d}",
  2391	            side=side,
  2392	            qty=1,
  2393	            order_price=None,
  2394	            market_price=risk_output.get("ltp"),
  2395	            best_bid=risk_output.get("mid_price"),
  2396	            best_ask=risk_output.get("ltp"),
  2397	            timestamp=risk_output.get("event_time"),
  2398	            metadata=dict(risk_output.get("metadata") or {}),
  2399	        )
  2400	        fill_result = model.fill(fill_request)
  2401	
  2402	        results.append(
  2403	            {
  2404	                "execution_id": f"execution_shadow_{index:06d}",
  2405	                "event_time": risk_output.get("event_time"),
  2406	                "execution_channel": "replay:execution_shadow",
  2407	                "source_risk_id": risk_output.get("risk_id"),
  2408	                "risk_action": risk_action,
  2409	                "filled": fill_result.filled,
  2410	                "fill_qty": fill_result.fill_qty,
  2411	                "fill_price": fill_result.fill_price,
  2412	                "slippage": fill_result.slippage,
  2413	                **_r35c_r5a3_shadow_pnl(fill_result.fill_price, fill_result.fill_qty),
  2414	                "reason": fill_result.reason,
  2415	                "symbol": risk_output.get("symbol"),

## Compile log
