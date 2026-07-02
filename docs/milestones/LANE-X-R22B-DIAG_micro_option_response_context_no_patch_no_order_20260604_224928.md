  1485	            "ltp": ltp,
  1486	            "bid": bid,
  1487	            "ask": ask,
  1488	            "best_bid": bid,
  1489	            "best_ask": ask,
  1490	            "spread": spread,
  1491	            "spread_ratio": _safe_float(
  1492	                _pick(surface_raw, "spread_ratio"),
  1493	                _ratio(spread, max(mid * 0.0001, 0.05), 999.0),
  1494	            ),
  1495	            "depth_total": depth_total,
  1496	            "touch_depth": depth_total,
  1497	            "depth_ok": depth_total >= DEFAULT_DEPTH_MIN,
  1498	            "top5_bid_qty": bid_qty,
  1499	            "top5_ask_qty": ask_qty,
  1500	            "bid_qty": bid_qty,
  1501	            "ask_qty": ask_qty,
  1502	            "bid_qty_5": bid_qty,
  1503	            "ask_qty_5": ask_qty,
  1504	            "ofi_ratio_proxy": ofi,
  1505	            "ofi_persist_score": _safe_float(
  1506	                _pick(surface_raw, "ofi_persist_score", "weighted_ofi_persist"),
  1507	                ofi,
  1508	            ),
  1509	            "weighted_ofi": _clamp(0.5 + ofi / 2.0, 0.0, 1.0),
  1510	            "weighted_ofi_persist": _clamp(0.5 + ofi / 2.0, 0.0, 1.0),
  1511	            "nof": ofi,
  1512	            "nof_slope": _safe_float(_pick(surface_raw, "nof_slope"), 0.0),
  1513	            "delta_3": _safe_float(_pick(surface_raw, "delta_3", "ltp_delta_3"), 0.0),
  1514	            "vel_ratio": _safe_float(_pick(surface_raw, "vel_ratio", "velocity_ratio"), 1.0),
  1515	            "velocity_ratio": _safe_float(_pick(surface_raw, "velocity_ratio", "vel_ratio"), 1.0),
  1516	            "vol_norm": _safe_float(_pick(surface_raw, "vol_norm", "volume_norm"), 1.0),
  1517	            "volume_norm": _safe_float(_pick(surface_raw, "volume_norm", "vol_norm"), 1.0),
  1518	            "vwap": vwap,
  1519	            "vwap_distance": ltp - vwap if ltp > 0 and vwap > 0 else 0.0,
  1520	            "vwap_dist_pct": _ratio(ltp - vwap, vwap, 0.0) if ltp > 0 and vwap > 0 else 0.0,
  1521	            "above_vwap": bool(ltp > vwap) if ltp > 0 and vwap > 0 else False,
  1522	            "below_vwap": bool(ltp < vwap) if ltp > 0 and vwap > 0 else False,
  1523	            "ts_event_ns": _safe_int(_pick(surface_raw, "ts_event_ns", "event_ts_ns"), 0) or None,
  1524	            "age_ms": _safe_int(_pick(surface_raw, "age_ms"), 0) or None,
  1525	        }
  1526	
  1527	    # LANE_X_R22B_MICRO_OPTION_RESPONSE_PRODUCER_BEGIN
  1528	    def _lane_x_r22b_micro_option_response(
  1529	        self,
  1530	        surface_raw: Mapping[str, Any],
  1531	        *,
  1532	        role: str,
  1533	        provider_id: str,
  1534	        side: str,
  1535	    ) -> dict[str, Any]:
  1536	        """Derived live option-response evidence from selected-option price history.
  1537	
  1538	        Additive only: this producer does not force tradability, candidates,
  1539	        paper, execution, order routing, or MISO readiness. It supplies response
  1540	        evidence when upstream option snapshots do not carry delta_3 or
  1541	        response_efficiency.
  1542	        """
  1543	        raw = dict(surface_raw or {})
  1544	        ltp = _safe_float(_pick(raw, "ltp", "last_price", "price"), 0.0)
  1545	        if ltp <= 0.0:
  1546	            return {}
  1547	
  1548	        symbol = _safe_str(
  1549	            _pick(raw, "option_symbol", "trading_symbol", "symbol", "instrument_key", "instrument_token")
  1550	        )
  1551	        token = _safe_str(_pick(raw, "instrument_token", "token"))
  1552	        key = "|".join([_safe_str(provider_id), _safe_str(role), _safe_str(side), symbol or token])
  1553	        if not key.strip("|"):
  1554	            return {}
  1555	
  1556	        ts_ns = _safe_int(_pick(raw, "ts_event_ns", "event_ts_ns", "ltt_ns", "last_trade_time_ns"), 0)
  1557	        if ts_ns <= 0:
  1558	            ts_ns = int(time.time_ns())
  1559	
  1560	        state = self._lane_x_r22b_option_history
  1561	        hist = list(state.get(key, []))
  1562	        if not hist or hist[-1][0] != ts_ns or abs(hist[-1][1] - ltp) > 1e-12:
  1563	            hist.append((ts_ns, ltp))
  1564	        hist = hist[-8:]
  1565	        state[key] = hist
  1566	
  1567	        if len(state) > 128:
  1568	            for old_key in list(state.keys())[:64]:
  1569	                if old_key != key:
  1570	                    state.pop(old_key, None)
  1571	
  1572	        sample_count = len(hist)
  1573	        if sample_count < 2:
  1574	            return {
  1575	                "option_response_sample_count": sample_count,
  1576	                "option_response_source": "micro_option_response",
  1577	                "option_response_ready": False,
  1578	            }
  1579	
  1580	        ref_index = -4 if sample_count >= 4 else 0
  1581	        ref_ts, ref_ltp = hist[ref_index]
  1582	        delta = ltp - ref_ltp
  1583	        age_ns = max(0, ts_ns - ref_ts)
  1584	
  1585	        tick = _safe_float(_pick(raw, "tick_size"), 0.05)
  1586	        if tick <= 0.0:
  1587	            tick = 0.05
  1588	
  1589	        bid = _safe_float(_pick(raw, "bid", "best_bid"), 0.0)
  1590	        ask = _safe_float(_pick(raw, "ask", "best_ask"), 0.0)
  1591	        spread = max(0.0, ask - bid) if bid > 0.0 and ask > 0.0 else 0.0
  1592	        denominator = spread if spread > 0.0 else tick
  1593	
  1594	        response_eff = abs(delta) / max(denominator, tick, 1e-9)
  1595	        velocity_ratio = abs(delta) / max(tick, 1e-9)
  1596	
  1597	        return {
  1598	            "delta_3": delta,
  1599	            "ltp_delta_3": delta,
  1600	            "option_response_delta": delta,
  1601	            "option_response_abs_delta": abs(delta),
  1602	            "option_response_ref_ltp": ref_ltp,
  1603	            "option_response_ref_ts_ns": ref_ts,
  1604	            "option_response_age_ns": age_ns,
  1605	            "option_response_sample_count": sample_count,
  1606	            "option_response_source": "micro_option_response",
  1607	            "option_response_ready": True,
  1608	            "option_response_velocity_ratio": velocity_ratio,
  1609	            "velocity_ratio": velocity_ratio,
  1610	            "vel_ratio": velocity_ratio,
  1611	            "response_efficiency": response_eff,
  1612	            "option_response_efficiency": response_eff,
  1613	        }
  1614	    # LANE_X_R22B_MICRO_OPTION_RESPONSE_PRODUCER_END
  1615	
  1616	    def _option_surface(
  1617	        self,
  1618	        raw: Mapping[str, Any],
  1619	        *,
  1620	        role: str,
  1621	        provider_id: str,
  1622	    ) -> dict[str, Any]:
  1623	        """
  1624	        Batch 25K-I source-anchored repair.
  1625	
  1626	        This is the actual FeatureEngine._option_surface method. It must call
  1627	        option_core.build_live_option_surface through the exact shared-builder
  1628	        ABI path for both CALL and PUT surfaces.
  1629	
  1630	        Required ABI:
  1631	            option_core.build_live_option_surface(
  1632	                side=...,
  1633	                live_source=...,
  1634	                provider_id=...,
  1635	                strike=...,
  1636	                instrument_key=...,
  1637	                instrument_token=...
  1638	            )
  1639	        """
  1640	
  1641	        raw_map = dict(raw or {})
  1642	
  1643	        role_hint = _safe_str(role)
  1644	        symbol_hint = _safe_str(
  1645	            _pick(raw_map, "option_symbol", "trading_symbol", "symbol", "instrument_key", "instrument_token")
  1646	        )
  1647	
  1648	        inferred_side = _normalize_side(_pick(raw_map, "side", "option_side", "right", "branch_id"))
  1649	
  1650	        if inferred_side not in (SIDE_CALL, SIDE_PUT):
  1651	            probe = f"{role_hint} {symbol_hint}".upper()
  1652	            if "PUT" in probe or " PE" in f" {probe} " or probe.endswith("PE") or "_PE" in probe or "-PE" in probe:
  1653	                inferred_side = SIDE_PUT
  1654	            elif "CALL" in probe or " CE" in f" {probe} " or probe.endswith("CE") or "_CE" in probe or "-CE" in probe:
  1655	                inferred_side = SIDE_CALL
  1656	
  1657	        surface_raw = (
  1658	            _flatten_snapshot_member_for_option_surface(
  1659	                raw_map,
  1660	                side=inferred_side,
  1661	                role=role,
  1662	                provider_id=provider_id,
  1663	            )
  1664	            if "_flatten_snapshot_member_for_option_surface" in globals()
  1665	            else raw_map
  1666	        )
  1667	
  1668	        side = _normalize_side(_pick(surface_raw, "side", "option_side", "right", "branch_id"))
  1669	
  1670	        if side not in (SIDE_CALL, SIDE_PUT):
  1671	            probe = f"{role_hint} {symbol_hint} {_safe_str(_pick(surface_raw, 'option_symbol', 'trading_symbol', 'symbol', 'instrument_key', 'instrument_token'))}".upper()
  1672	            if "PUT" in probe or " PE" in f" {probe} " or probe.endswith("PE") or "_PE" in probe or "-PE" in probe:
  1673	                side = SIDE_PUT
  1674	            elif "CALL" in probe or " CE" in f" {probe} " or probe.endswith("CE") or "_CE" in probe or "-CE" in probe:
  1675	                side = SIDE_CALL
  1676	
  1677	        side_text = _safe_str(side).upper()
  1678	        side_call_text = _safe_str(SIDE_CALL).upper()
  1679	        side_put_text = _safe_str(SIDE_PUT).upper()
  1680	
  1681	        builder_side = ""
  1682	        if side_text in {side_call_text, "CALL", "CE", "C"}:
  1683	            builder_side = SIDE_CALL
  1684	        elif side_text in {side_put_text, "PUT", "PE", "P"}:
  1685	            builder_side = SIDE_PUT
  1686	
  1687	        micro_response = self._lane_x_r22b_micro_option_response(
  1688	            surface_raw,
  1689	            role=role,
  1690	            provider_id=provider_id,
  1691	            side=builder_side or side,
  1692	        )
  1693	        if micro_response:
  1694	            surface_raw = dict(surface_raw)
  1695	            for _mx_key, _mx_value in micro_response.items():
  1696	                if _mx_key in {"delta_3", "ltp_delta_3"}:
  1697	                    if abs(_safe_float(_pick(surface_raw, "delta_3", "ltp_delta_3"), 0.0)) <= 1e-12:
  1698	                        surface_raw[_mx_key] = _mx_value
  1699	                elif _mx_key in {"response_efficiency", "option_response_efficiency"}:
  1700	                    if _safe_float(
  1701	                        _pick(surface_raw, "response_efficiency", "response_eff", "option_response_efficiency"),
  1702	                        0.0,
  1703	                    ) <= 0.0:
  1704	                        surface_raw[_mx_key] = _mx_value
  1705	                elif _mx_key in {"velocity_ratio", "vel_ratio"}:
  1706	                    if _safe_float(_pick(surface_raw, "velocity_ratio", "vel_ratio"), 0.0) <= 1.0:
  1707	                        surface_raw[_mx_key] = _mx_value
  1708	                else:
  1709	                    surface_raw.setdefault(_mx_key, _mx_value)
  1710	
  1711	        built = None
  1712	
  1713	        if builder_side in (SIDE_CALL, SIDE_PUT):
  1714	            option_core_module = None
  1715	            try:
