# R35C_R5A_EXECUTION_SHADOW_PNL_FIELDS_PATCH_NO_REPLAY_NO_ORDER_20260614_001725

classification: REVIEW_R35C_R5A_PATCH_OR_SAFETY_NEEDS_ATTENTION_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35C_R5A_EXECUTION_SHADOW_PNL_FIELDS_PATCH_NO_REPLAY_NO_ORDER_20260614_001725.json`
backup: `run/_code_backups/R35C_R5A_EXECUTION_SHADOW_PNL_FIELDS_PATCH_NO_REPLAY_NO_ORDER_20260614_001725_bin_replay_run.py.bak`

patch_rc=1 compile_rc=0 marker_rc=1
safety pre=0/0/0 post=0/0/0 proc=0/0 replay_proc=0

## Patch log

## Patch errors
fill_model_block_not_found

## Markers

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
  2306	    results: list[dict[str, Any]] = []
  2307	    for index, risk_output in enumerate(ordered_outputs, start=1):
  2308	        risk_action = str(risk_output.get("risk_action") or "HOLD")
  2309	        veto_entry = bool(risk_output.get("veto_entry"))
  2310	        side = _risk_action_to_fill_side(risk_action)
  2311	
  2312	        if veto_entry or side is None:
  2313	            results.append(
  2314	                {
  2315	                    "execution_id": f"execution_shadow_{index:06d}",
  2316	                    "event_time": risk_output.get("event_time"),
  2317	                    "execution_channel": "replay:execution_shadow",
  2318	                    "source_risk_id": risk_output.get("risk_id"),
  2319	                    "risk_action": risk_action,
  2320	                    "filled": False,
  2321	                    "fill_qty": 0,
  2322	                    "fill_price": None,
  2323	                    "slippage": None,
  2324	                    "reason": "risk_block_or_non_entry",
  2325	                    "symbol": risk_output.get("symbol"),
  2326	                    "metadata": dict(risk_output.get("metadata") or {}),
  2327	                }
  2328	            )
  2329	            continue
  2330	
  2331	        fill_request = ReplayFillRequest(
  2332	            run_id=run_id,
  2333	            order_id=f"shadow_order_{index:06d}",
  2334	            side=side,
  2335	            qty=1,
  2336	            order_price=None,
  2337	            market_price=risk_output.get("ltp"),
  2338	            best_bid=risk_output.get("mid_price"),
  2339	            best_ask=risk_output.get("ltp"),
  2340	            timestamp=risk_output.get("event_time"),
  2341	            metadata=dict(risk_output.get("metadata") or {}),
  2342	        )
  2343	        fill_result = model.fill(fill_request)
  2344	
  2345	        results.append(
  2346	            {
  2347	                "execution_id": f"execution_shadow_{index:06d}",
  2348	                "event_time": risk_output.get("event_time"),
  2349	                "execution_channel": "replay:execution_shadow",
  2350	                "source_risk_id": risk_output.get("risk_id"),
  2351	                "risk_action": risk_action,
  2352	                "filled": fill_result.filled,
  2353	                "fill_qty": fill_result.fill_qty,
  2354	                "fill_price": fill_result.fill_price,
  2355	                "slippage": fill_result.slippage,
  2356	                "reason": fill_result.reason,
  2357	                "symbol": risk_output.get("symbol"),
  2358	                "metadata": dict(risk_output.get("metadata") or {}),
  2359	            }
  2360	        )
  2361	
  2362	    return results
  2363	
  2364	
  2365	
  2366	
  2367	def _artifact_mapping(value: Any) -> Mapping[str, Any]:
  2368	    if isinstance(value, dict):
  2369	        return value
  2370	    return {}
  2371	
  2372	
  2373	def _artifact_first_present(*values: Any) -> Any:
  2374	    for value in values:
  2375	        if value is None:
  2376	            continue
  2377	        if isinstance(value, str):
  2378	            text = value.strip()
  2379	            if not text:
  2380	                continue
  2381	            return text
  2382	        if isinstance(value, (dict, list, tuple, set)):
  2383	            continue
  2384	        return value
  2385	    return None

## Compile log
