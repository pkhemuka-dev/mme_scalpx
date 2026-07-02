# LANE-X-R34U-R1_STRATEGY_HELPER_EXACT_SHAPE_LOCATOR_NO_PATCH_NO_REPLAY_NO_ORDER_locate_current_r34f_shadow_helper_shape_after_r34m_before_repairing_r34u_patch_20260613_145241

classification: PASS_R34U_R1_HELPER_SHAPE_LOCATED_NO_PATCH_NO_REPLAY_NO_ORDER
proof: `run/proofs/LANE-X-R34U-R1_STRATEGY_HELPER_EXACT_SHAPE_LOCATOR_NO_PATCH_NO_REPLAY_NO_ORDER_locate_current_r34f_shadow_helper_shape_after_r34m_before_repairing_r34u_patch_20260613_145241.json`
audit: `run/audits/LANE-X-R34U-R1_STRATEGY_HELPER_EXACT_SHAPE_LOCATOR_NO_PATCH_NO_REPLAY_NO_ORDER_locate_current_r34f_shadow_helper_shape_after_r34m_before_repairing_r34u_patch_20260613_145241`

## Safety
- compile_rc: 0
- orders/risk/execution: 0 / 0 / 0
- risk/execution proc: 0 / 0
- r34u_markers_present: 0
0

## Helper shape
================================================================================
TARGET: _r34f_shadow_candidate_truth_from_activation_selected
HITS: [434, 1095]
--------------------------------------------------------------------------------
CONTEXT 414:479
000414:         field = str(key)
000415: 
000416:         # payload_json above is canonical. Do not allow an incoming flat field
000417:         # to replace the canonical encoded payload.
000418:         if field == "payload_json":
000419:             continue
000420: 
000421:         if value is None:
000422:             out[field] = ""
000423:         elif isinstance(value, (dict, list, tuple)):
000424:             out[field] = _json_dump(value)
000425:         elif isinstance(value, bool):
000426:             out[field] = "1" if value else "0"
000427:         else:
000428:             out[field] = value
000429: 
000430:     return out
000431: 
000432: 
000433: # R34F_SHADOW_CANDIDATE_TRUTH_EXPORT_BEGIN
000434: def _r34f_shadow_candidate_truth_from_activation_selected(
000435:     selected: Mapping[str, Any],
000436:     view: Any = None,
000437: ) -> dict[str, Any]:
000438:     """
000439:     Shadow-only candidate truth export from activation-selected dry-run candidate.
000440: 
000441:     This deliberately does NOT promote strategy action, does NOT write to any
000442:     trading/order stream, and does NOT enable broker/risk/execution paths.
000443:     """
000444:     selected_map = _mapping(selected)
000445:     action = _safe_str(selected_map.get("action")).upper()
000446:     is_enter = action in {"ENTER_CALL", "ENTER_PUT"}
000447: 
000448:     # R34K_SYMBOL_TOKEN_IDENTITY_EXPORT_BEGIN
000449:     def _r34k_read(obj: Any, key: str) -> Any:
000450:         if obj is None:
000451:             return None
000452:         if isinstance(obj, Mapping):
000453:             return obj.get(key)
000454:         return getattr(obj, key, None)
000455: 
000456:     def _r34k_walk(obj: Any, keys: tuple[str, ...], depth: int = 0, seen: set[int] | None = None) -> Any:
000457:         if obj is None or depth > 4:
000458:             return None
000459:         if seen is None:
000460:             seen = set()
000461:         oid = id(obj)
000462:         if oid in seen:
000463:             return None
000464:         seen.add(oid)
000465: 
000466:         for key in keys:
000467:             value = _r34k_read(obj, key)
000468:             if value not in (None, "", [], {}):
000469:                 return value
000470: 
000471:         if isinstance(obj, Mapping):
000472:             iterable = obj.values()
000473:         elif isinstance(obj, (str, bytes, int, float, bool)):
000474:             iterable = ()
000475:         elif hasattr(obj, "__dict__"):
000476:             iterable = vars(obj).values()
000477:         else:
000478:             iterable = ()
000479: 
--------------------------------------------------------------------------------
CONTEXT 1075:1140
001075:             or _mapping(view.common.get("selected_call"))
001076:             or _mapping(view.common.get("selected_put"))
001077:         )
001078: 
001079:         activation_report = self.build_activation_report(view, now_ns=now_ns)
001080:         activation_selected = _mapping(activation_report.get("selected"))
001081:         activation_candidates = activation_report.get("candidates")
001082:         activation_candidate_count = (
001083:             len(activation_candidates)
001084:             if isinstance(activation_candidates, list)
001085:             else 0
001086:         )
001087:         # R34M_EXACT_RUNTIME_IDENTITY_SOURCE_BEGIN
001088:         r34m_identity_source = {
001089:             "selected_option": selected_option,
001090:             "view_common": _mapping(getattr(view, "common", {})),
001091:             "view_dict": view.to_dict(),
001092:             "activation_selected": activation_selected,
001093:         }
001094:         # R34M_EXACT_RUNTIME_IDENTITY_SOURCE_END
001095:         r34f_shadow_fields = _r34f_shadow_candidate_truth_from_activation_selected(
001096:             activation_selected,
001097:             view=r34m_identity_source,
001098:         )
001099: 
001100:         decision_id = f"strategy-hold-{now_ns}"
001101: 
001102:         return {
001103:             "schema_version": getattr(N, "DEFAULT_SCHEMA_VERSION", 1),
001104:             "service": SERVICE_STRATEGY,
001105:             "decision_id": decision_id,
001106:             "ts_ns": now_ns,
001107:             "ts_event_ns": now_ns,
001108:             "action": ACTION_HOLD,
001109:             "side": getattr(N, "POSITION_SIDE_FLAT", "FLAT"),
001110:             "branch_id": "",
001111:             "strategy_family_id": "",
001112:             "doctrine_id": "",
001113:             "instrument_key": _safe_str(selected_option.get("instrument_key")),
001114:             "instrument_token": _safe_str(selected_option.get("instrument_token")),
001115:             "option_symbol": _safe_str(selected_option.get("option_symbol")),
001116:             "strike": selected_option.get("strike"),
001117:             "qty": 0,
001118:             "price": selected_option.get("ltp"),
001119:             "order_type": "",
001120:             "reason": view.reason,
001121:             "confidence": 0.0,
001122:             "hold_only": 1,
001123:             "activation_bridge_enabled": 1,
001124:             "activation_report_only": 1,
001125:             "activation_mode": _safe_str(activation_report.get("activation_mode"), ACTIVATION_REPORT_MODE),
001126:             "activation_action": ACTION_HOLD,
001127:             "activation_observed_action": _safe_str(
001128:                 activation_report.get("observed_action_before_strategy_clamp"),
001129:                 _safe_str(activation_report.get("action"), ACTION_HOLD),
001130:             ),
001131:             "activation_promoted": 0,
001132:             "activation_safe_to_promote": 0,
001133:             "activation_reason": _safe_str(activation_report.get("reason")),
001134:             "activation_selected_family_id": _safe_str(activation_selected.get("family_id")),
001135:             "activation_selected_branch_id": _safe_str(activation_selected.get("branch_id")),
001136:             "activation_selected_action": _safe_str(activation_selected.get("action")),
001137:             "activation_selected_score": activation_selected.get("score"),
001138:             "activation_candidate_count": activation_candidate_count,
001139:             **r34f_shadow_fields,
001140:             "safe_to_consume": int(view.safe_to_consume),
================================================================================
TARGET: candidate_symbol_shadow
HITS: [502, 525, 527]
--------------------------------------------------------------------------------
CONTEXT 482:547
000482:             if value not in (None, "", [], {}):
000483:                 return value
000484:         return None
000485: 
000486:     symbol_keys = (
000487:         "symbol", "tradingsymbol", "trading_symbol", "option_symbol",
000488:         "selected_option_symbol", "selected_option_tradingsymbol",
000489:         "selected_option_trading_symbol", "instrument_key",
000490:         "selected_option_instrument_key",
000491:         "selected_call_option_symbol", "selected_put_option_symbol",
000492:         "selected_call_instrument_key", "selected_put_instrument_key",
000493:         "entry_option_symbol", "selected_symbol",
000494:     )
000495:     token_keys = (
000496:         "instrument_token", "token", "option_token",
000497:         "selected_option_token", "selected_option_instrument_token",
000498:         "selected_call_option_token", "selected_put_option_token",
000499:         "selected_call_instrument_token", "selected_put_instrument_token",
000500:     )
000501: 
000502:     candidate_symbol_shadow = _safe_str(
000503:         _r34k_walk(selected_map, symbol_keys) or _r34k_walk(view, symbol_keys)
000504:     )
000505:     candidate_instrument_token_shadow = _safe_str(
000506:         _r34k_walk(selected_map, token_keys) or _r34k_walk(view, token_keys)
000507:     )
000508:     # R34K_SYMBOL_TOKEN_IDENTITY_EXPORT_END
000509: 
000510:     return {
000511:         "candidate_true_shadow": int(is_enter),
000512:         "candidate_present_shadow": int(is_enter),
000513:         "candidate_shadow_only": int(is_enter),
000514:         "candidate_truth_mode_shadow": (
000515:             "activation_selected_report_only_shadow" if is_enter else ""
000516:         ),
000517:         "candidate_action_shadow": action if is_enter else "",
000518:         "candidate_family_id_shadow": (
000519:             _safe_str(selected_map.get("family_id")).upper() if is_enter else ""
000520:         ),
000521:         "candidate_branch_id_shadow": (
000522:             _safe_str(selected_map.get("branch_id")) if is_enter else ""
000523:         ),
000524:         "candidate_score_shadow": selected_map.get("score") if is_enter else None,
000525:         "candidate_symbol_shadow": candidate_symbol_shadow if is_enter else "",
000526:         "candidate_instrument_token_shadow": candidate_instrument_token_shadow if is_enter else "",
000527:         "symbol": candidate_symbol_shadow if is_enter else "",
000528:         "instrument_token": candidate_instrument_token_shadow if is_enter else "",
000529:         "real_order_sent_shadow": 0,
000530:         "broker_calls_executed_shadow": 0,
000531:         "redis_trading_stream_write_attempted_shadow": 0,
000532:     }
000533: # R34F_SHADOW_CANDIDATE_TRUTH_EXPORT_END
000534: 
000535: 
000536: def _validate_hold_decision_for_publish(decision: Mapping[str, Any]) -> None:
000537:     """
000538:     Enforce the frozen Batch 10 strategy.py law before Redis publication.
000539: 
000540:     strategy.py is a HOLD-only consumer bridge in this lane. Even if a future
000541:     activation/report module observes candidates, this service may not publish
000542:     promoted ENTER/EXIT decisions until a later explicit arming contract changes
000543:     this file and its proofs.
000544:     """
000545: 
000546:     action = _safe_str(decision.get("action"), ACTION_HOLD)
000547:     if action != ACTION_HOLD:
--------------------------------------------------------------------------------
CONTEXT 505:570
000505:     candidate_instrument_token_shadow = _safe_str(
000506:         _r34k_walk(selected_map, token_keys) or _r34k_walk(view, token_keys)
000507:     )
000508:     # R34K_SYMBOL_TOKEN_IDENTITY_EXPORT_END
000509: 
000510:     return {
000511:         "candidate_true_shadow": int(is_enter),
000512:         "candidate_present_shadow": int(is_enter),
000513:         "candidate_shadow_only": int(is_enter),
000514:         "candidate_truth_mode_shadow": (
000515:             "activation_selected_report_only_shadow" if is_enter else ""
000516:         ),
000517:         "candidate_action_shadow": action if is_enter else "",
000518:         "candidate_family_id_shadow": (
000519:             _safe_str(selected_map.get("family_id")).upper() if is_enter else ""
000520:         ),
000521:         "candidate_branch_id_shadow": (
000522:             _safe_str(selected_map.get("branch_id")) if is_enter else ""
000523:         ),
000524:         "candidate_score_shadow": selected_map.get("score") if is_enter else None,
000525:         "candidate_symbol_shadow": candidate_symbol_shadow if is_enter else "",
000526:         "candidate_instrument_token_shadow": candidate_instrument_token_shadow if is_enter else "",
000527:         "symbol": candidate_symbol_shadow if is_enter else "",
000528:         "instrument_token": candidate_instrument_token_shadow if is_enter else "",
000529:         "real_order_sent_shadow": 0,
000530:         "broker_calls_executed_shadow": 0,
000531:         "redis_trading_stream_write_attempted_shadow": 0,
000532:     }
000533: # R34F_SHADOW_CANDIDATE_TRUTH_EXPORT_END
000534: 
000535: 
000536: def _validate_hold_decision_for_publish(decision: Mapping[str, Any]) -> None:
000537:     """
000538:     Enforce the frozen Batch 10 strategy.py law before Redis publication.
000539: 
000540:     strategy.py is a HOLD-only consumer bridge in this lane. Even if a future
000541:     activation/report module observes candidates, this service may not publish
000542:     promoted ENTER/EXIT decisions until a later explicit arming contract changes
000543:     this file and its proofs.
000544:     """
000545: 
000546:     action = _safe_str(decision.get("action"), ACTION_HOLD)
000547:     if action != ACTION_HOLD:
000548:         raise StrategyBridgeError(
000549:             f"strategy.py HOLD-only bridge refused non-HOLD action: {action!r}"
000550:         )
000551: 
000552:     qty = _safe_int(decision.get("qty"), 0)
