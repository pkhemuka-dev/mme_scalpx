# LANE-X-R34R_DHAN_SELECTED_OPTION_NULL_IDENTITY_ROUTE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_source_level_contract_audit_for_why_selected_call_put_option_identity_is_null_and_provider_not_ready_20260613_144440

classification: PASS_R34R_DHAN_SELECTED_OPTION_NULL_ROUTE_AUDIT_WRITTEN_NO_PATCH_NO_REPLAY_NO_ORDER
proof: `run/proofs/LANE-X-R34R_DHAN_SELECTED_OPTION_NULL_IDENTITY_ROUTE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_source_level_contract_audit_for_why_selected_call_put_option_identity_is_null_and_provider_not_ready_20260613_144440.json`
audit: `run/audits/LANE-X-R34R_DHAN_SELECTED_OPTION_NULL_IDENTITY_ROUTE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_source_level_contract_audit_for_why_selected_call_put_option_identity_is_null_and_provider_not_ready_20260613_144440`

## Safety
- compile_strategy_rc: 0
- orders/risk/execution: 0 / 0 / 0
- risk/execution proc: 0 / 0

## Hit counts
- source_files: 4759
- selected_option_publish_hits: 4531
- selected_option_reader_hits: 3422
- dhan_hits: 5803
- zerodha_hits: 2514
- provider_ready_hits: 5872

## What this audit is checking
1. Where selected_call / selected_put / selected_option identity is published.
2. Where strategy reads selected option identity.
3. Why DHAN selected-option context is provider_not_ready / runtime_disabled / not_present.
4. Whether Zerodha selected-option identity can safely act as the identity source while broker/order path remains blocked.

## Selected option publisher hits
app/mme_scalpx/core/models.py:743:    is_selected_option: bool = False
app/mme_scalpx/core/models.py:797:        _require_bool(self.is_selected_option, "is_selected_option")
app/mme_scalpx/core/models.py:890:    is_selected_option: bool = False
app/mme_scalpx/core/models.py:933:        _require_bool(self.is_selected_option, "is_selected_option")
app/mme_scalpx/core/models.py:1143:    active_selected_option_provider_id: str | None = None
app/mme_scalpx/core/models.py:1175:        if self.active_selected_option_provider_id is not None:
app/mme_scalpx/core/models.py:1177:                self.active_selected_option_provider_id,
app/mme_scalpx/core/models.py:1178:                "active_selected_option_provider_id",
app/mme_scalpx/core/models.py:1258:    active_selected_option_provider_id: str | None = None
app/mme_scalpx/core/models.py:1307:            "active_selected_option_provider_id",
app/mme_scalpx/core/models.py:1407:    active_selected_option_provider_id: str | None = None
app/mme_scalpx/core/models.py:1442:            "active_selected_option_provider_id",
app/mme_scalpx/core/models.py:1494:    active_selected_option_provider_id: str | None = None
app/mme_scalpx/core/models.py:1555:            "active_selected_option_provider_id",
app/mme_scalpx/core/models.py:1577:                "provider_id": self.active_selected_option_provider_id,
app/mme_scalpx/core/models.py:1592:                "active_selected_option_provider_id": self.active_selected_option_provider_id,
app/mme_scalpx/core/models.py:1622:            "active_selected_option_provider_id": self.active_selected_option_provider_id,
app/mme_scalpx/core/models.py:1964:    is_selected_option: bool = False
app/mme_scalpx/core/models.py:2007:        _require_bool(self.is_selected_option, "is_selected_option")
app/mme_scalpx/core/models.py:2018:    selected_call_instrument_key: str | None = None
app/mme_scalpx/core/models.py:2019:    selected_put_instrument_key: str | None = None
app/mme_scalpx/core/models.py:2020:    selected_call_option_symbol: str | None = None
app/mme_scalpx/core/models.py:2021:    selected_put_option_symbol: str | None = None
app/mme_scalpx/core/models.py:2022:    selected_call_option_token: str | None = None
app/mme_scalpx/core/models.py:2023:    selected_put_option_token: str | None = None
app/mme_scalpx/core/models.py:2024:    selected_call_dhan_security_id: str | None = None
app/mme_scalpx/core/models.py:2025:    selected_put_dhan_security_id: str | None = None
app/mme_scalpx/core/models.py:2026:    selected_call_zerodha_token: str | None = None
app/mme_scalpx/core/models.py:2027:    selected_put_zerodha_token: str | None = None
app/mme_scalpx/core/models.py:2029:    selected_call_score: float | None = None
app/mme_scalpx/core/models.py:2030:    selected_put_score: float | None = None
app/mme_scalpx/core/models.py:2031:    selected_call_delta: float | None = None
app/mme_scalpx/core/models.py:2032:    selected_put_delta: float | None = None
app/mme_scalpx/core/models.py:2033:    selected_call_authoritative_delta: float | None = None
app/mme_scalpx/core/models.py:2034:    selected_put_authoritative_delta: float | None = None
app/mme_scalpx/core/models.py:2035:    selected_call_gamma: float | None = None
app/mme_scalpx/core/models.py:2036:    selected_put_gamma: float | None = None
app/mme_scalpx/core/models.py:2037:    selected_call_theta: float | None = None
app/mme_scalpx/core/models.py:2038:    selected_put_theta: float | None = None
app/mme_scalpx/core/models.py:2039:    selected_call_vega: float | None = None
app/mme_scalpx/core/models.py:2040:    selected_put_vega: float | None = None
app/mme_scalpx/core/models.py:2041:    selected_call_iv: float | None = None
app/mme_scalpx/core/models.py:2042:    selected_put_iv: float | None = None
app/mme_scalpx/core/models.py:2043:    selected_call_iv_change_1m_pct: float | None = None
app/mme_scalpx/core/models.py:2044:    selected_put_iv_change_1m_pct: float | None = None
app/mme_scalpx/core/models.py:2045:    selected_call_oi: int | None = None
app/mme_scalpx/core/models.py:2046:    selected_put_oi: int | None = None
app/mme_scalpx/core/models.py:2047:    selected_call_oi_change: int | None = None
app/mme_scalpx/core/models.py:2048:    selected_put_oi_change: int | None = None
app/mme_scalpx/core/models.py:2049:    selected_call_volume: int | None = None
app/mme_scalpx/core/models.py:2050:    selected_put_volume: int | None = None
app/mme_scalpx/core/models.py:2051:    selected_call_cross_strike_spread_rank: float | None = None
app/mme_scalpx/core/models.py:2052:    selected_put_cross_strike_spread_rank: float | None = None
app/mme_scalpx/core/models.py:2053:    selected_call_cross_strike_volume_rank: float | None = None
app/mme_scalpx/core/models.py:2054:    selected_put_cross_strike_volume_rank: float | None = None
app/mme_scalpx/core/models.py:2058:    selected_call_context_json: str | None = None
app/mme_scalpx/core/models.py:2059:    selected_put_context_json: str | None = None
app/mme_scalpx/core/models.py:2067:    selected_call_score_components: DhanStrikeScoreComponents | None = None
app/mme_scalpx/core/models.py:2068:    selected_put_score_components: DhanStrikeScoreComponents | None = None
app/mme_scalpx/core/models.py:2080:            "selected_call_instrument_key",
app/mme_scalpx/core/models.py:2081:            "selected_put_instrument_key",
app/mme_scalpx/core/models.py:2082:            "selected_call_option_symbol",
app/mme_scalpx/core/models.py:2083:            "selected_put_option_symbol",
app/mme_scalpx/core/models.py:2084:            "selected_call_option_token",
app/mme_scalpx/core/models.py:2085:            "selected_put_option_token",
app/mme_scalpx/core/models.py:2086:            "selected_call_dhan_security_id",
app/mme_scalpx/core/models.py:2087:            "selected_put_dhan_security_id",
app/mme_scalpx/core/models.py:2088:            "selected_call_zerodha_token",
app/mme_scalpx/core/models.py:2089:            "selected_put_zerodha_token",
app/mme_scalpx/core/models.py:2094:            "selected_call_context_json",
app/mme_scalpx/core/models.py:2095:            "selected_put_context_json",
app/mme_scalpx/core/models.py:2102:            "selected_call_score",
app/mme_scalpx/core/models.py:2103:            "selected_put_score",
app/mme_scalpx/core/models.py:2104:            "selected_call_delta",
app/mme_scalpx/core/models.py:2105:            "selected_put_delta",
app/mme_scalpx/core/models.py:2106:            "selected_call_authoritative_delta",
app/mme_scalpx/core/models.py:2107:            "selected_put_authoritative_delta",
app/mme_scalpx/core/models.py:2108:            "selected_call_gamma",
app/mme_scalpx/core/models.py:2109:            "selected_put_gamma",
app/mme_scalpx/core/models.py:2110:            "selected_call_theta",
app/mme_scalpx/core/models.py:2111:            "selected_put_theta",
app/mme_scalpx/core/models.py:2112:            "selected_call_vega",
app/mme_scalpx/core/models.py:2113:            "selected_put_vega",
app/mme_scalpx/core/models.py:2114:            "selected_call_iv",
app/mme_scalpx/core/models.py:2115:            "selected_put_iv",
app/mme_scalpx/core/models.py:2116:            "selected_call_iv_change_1m_pct",
app/mme_scalpx/core/models.py:2117:            "selected_put_iv_change_1m_pct",
app/mme_scalpx/core/models.py:2118:            "selected_call_cross_strike_spread_rank",
app/mme_scalpx/core/models.py:2119:            "selected_put_cross_strike_spread_rank",
app/mme_scalpx/core/models.py:2120:            "selected_call_cross_strike_volume_rank",
app/mme_scalpx/core/models.py:2121:            "selected_put_cross_strike_volume_rank",
app/mme_scalpx/core/models.py:2134:            "selected_call_oi",
app/mme_scalpx/core/models.py:2135:            "selected_put_oi",
app/mme_scalpx/core/models.py:2136:            "selected_call_oi_change",
app/mme_scalpx/core/models.py:2137:            "selected_put_oi_change",
app/mme_scalpx/core/models.py:2138:            "selected_call_volume",
app/mme_scalpx/core/models.py:2139:            "selected_put_volume",
app/mme_scalpx/core/models.py:2160:    selected_call_instrument_key: str | None = None
app/mme_scalpx/core/models.py:2161:    selected_put_instrument_key: str | None = None
app/mme_scalpx/core/models.py:2162:    selected_call_option_symbol: str | None = None
app/mme_scalpx/core/models.py:2163:    selected_put_option_symbol: str | None = None
app/mme_scalpx/core/models.py:2164:    selected_call_option_token: str | None = None
app/mme_scalpx/core/models.py:2165:    selected_put_option_token: str | None = None
app/mme_scalpx/core/models.py:2166:    selected_call_dhan_security_id: str | None = None
app/mme_scalpx/core/models.py:2167:    selected_put_dhan_security_id: str | None = None
app/mme_scalpx/core/models.py:2168:    selected_call_zerodha_token: str | None = None
app/mme_scalpx/core/models.py:2169:    selected_put_zerodha_token: str | None = None
app/mme_scalpx/core/models.py:2171:    selected_call_score: float | None = None
app/mme_scalpx/core/models.py:2172:    selected_put_score: float | None = None
app/mme_scalpx/core/models.py:2173:    selected_call_delta: float | None = None
app/mme_scalpx/core/models.py:2174:    selected_put_delta: float | None = None
app/mme_scalpx/core/models.py:2175:    selected_call_authoritative_delta: float | None = None
app/mme_scalpx/core/models.py:2176:    selected_put_authoritative_delta: float | None = None
app/mme_scalpx/core/models.py:2177:    selected_call_gamma: float | None = None
app/mme_scalpx/core/models.py:2178:    selected_put_gamma: float | None = None
app/mme_scalpx/core/models.py:2179:    selected_call_theta: float | None = None
app/mme_scalpx/core/models.py:2180:    selected_put_theta: float | None = None
app/mme_scalpx/core/models.py:2181:    selected_call_vega: float | None = None
app/mme_scalpx/core/models.py:2182:    selected_put_vega: float | None = None
app/mme_scalpx/core/models.py:2183:    selected_call_iv: float | None = None

## Selected option reader hits
app/mme_scalpx/core/models.py:717:    instrument_key: str
app/mme_scalpx/core/models.py:723:    instrument_token: str | None = None
app/mme_scalpx/core/models.py:724:    trading_symbol: str | None = None
app/mme_scalpx/core/models.py:749:        _require_non_empty_str(self.instrument_key, "instrument_key")
app/mme_scalpx/core/models.py:762:        if self.instrument_token is not None:
app/mme_scalpx/core/models.py:763:            _optional_non_empty_str(self.instrument_token, "instrument_token")
app/mme_scalpx/core/models.py:764:        if self.trading_symbol is not None:
app/mme_scalpx/core/models.py:765:            _optional_non_empty_str(self.trading_symbol, "trading_symbol")
app/mme_scalpx/core/models.py:807:    instrument_key: str
app/mme_scalpx/core/models.py:812:    instrument_token: str | None = None
app/mme_scalpx/core/models.py:813:    trading_symbol: str | None = None
app/mme_scalpx/core/models.py:830:        _require_non_empty_str(self.instrument_key, "instrument_key")
app/mme_scalpx/core/models.py:837:        if self.instrument_token is not None:
app/mme_scalpx/core/models.py:838:            _optional_non_empty_str(self.instrument_token, "instrument_token")
app/mme_scalpx/core/models.py:839:        if self.trading_symbol is not None:
app/mme_scalpx/core/models.py:840:            _optional_non_empty_str(self.trading_symbol, "trading_symbol")
app/mme_scalpx/core/models.py:867:    instrument_key: str
app/mme_scalpx/core/models.py:875:    instrument_token: str | None = None
app/mme_scalpx/core/models.py:876:    trading_symbol: str | None = None
app/mme_scalpx/core/models.py:896:        _require_non_empty_str(self.instrument_key, "instrument_key")
app/mme_scalpx/core/models.py:907:        if self.instrument_token is not None:
app/mme_scalpx/core/models.py:908:            _optional_non_empty_str(self.instrument_token, "instrument_token")
app/mme_scalpx/core/models.py:909:        if self.trading_symbol is not None:
app/mme_scalpx/core/models.py:910:            _optional_non_empty_str(self.trading_symbol, "trading_symbol")
app/mme_scalpx/core/models.py:942:    instrument_token: str
app/mme_scalpx/core/models.py:943:    trading_symbol: str
app/mme_scalpx/core/models.py:966:        _require_non_empty_str(self.instrument_token, "instrument_token")
app/mme_scalpx/core/models.py:967:        _require_non_empty_str(self.trading_symbol, "trading_symbol")
app/mme_scalpx/core/models.py:1131:    instrument_key: str
app/mme_scalpx/core/models.py:1157:        _require_non_empty_str(self.instrument_key, "instrument_key")
app/mme_scalpx/core/models.py:1248:    instrument_key: str | None = None
app/mme_scalpx/core/models.py:1297:            "instrument_key",
app/mme_scalpx/core/models.py:1324:            _require(bool(self.instrument_key), "entry actions require non-empty instrument_key")
app/mme_scalpx/core/models.py:1353:    instrument_key: str
app/mme_scalpx/core/models.py:1354:    option_symbol: str
app/mme_scalpx/core/models.py:1355:    option_token: str
app/mme_scalpx/core/models.py:1362:    trading_symbol: str | None = None
app/mme_scalpx/core/models.py:1368:        _require_non_empty_str(self.instrument_key, "instrument_key")
app/mme_scalpx/core/models.py:1369:        _require_non_empty_str(self.option_symbol, "option_symbol")
app/mme_scalpx/core/models.py:1370:        _require_non_empty_str(self.option_token, "option_token")
app/mme_scalpx/core/models.py:1379:            "trading_symbol",
app/mme_scalpx/core/models.py:1409:    instrument_key: str | None = None
app/mme_scalpx/core/models.py:1410:    option_symbol: str | None = None
app/mme_scalpx/core/models.py:1411:    option_token: str | None = None
app/mme_scalpx/core/models.py:1448:        for field_name in ("instrument_key", "option_symbol", "option_token"):
app/mme_scalpx/core/models.py:1476:    instrument_key: str
app/mme_scalpx/core/models.py:1481:    option_symbol: str
app/mme_scalpx/core/models.py:1482:    option_token: str
app/mme_scalpx/core/models.py:1523:        _require_non_empty_str(self.instrument_key, "instrument_key")
app/mme_scalpx/core/models.py:1540:        _require_non_empty_str(self.option_symbol, "option_symbol")
app/mme_scalpx/core/models.py:1541:        _require_non_empty_str(self.option_token, "option_token")
app/mme_scalpx/core/models.py:1573:                "option_symbol": self.option_symbol,
app/mme_scalpx/core/models.py:1574:                "option_token": self.option_token,
app/mme_scalpx/core/models.py:1612:            "instrument_key": self.instrument_key,
app/mme_scalpx/core/models.py:1747:    instrument_key: str
app/mme_scalpx/core/models.py:1763:        _require_non_empty_str(self.instrument_key, "instrument_key")
app/mme_scalpx/core/models.py:1783:    instrument_key: str
app/mme_scalpx/core/models.py:1799:        _require_non_empty_str(self.instrument_key, "instrument_key")
app/mme_scalpx/core/models.py:1820:    instrument_key: str
app/mme_scalpx/core/models.py:1837:        _require_non_empty_str(self.instrument_key, "instrument_key")
app/mme_scalpx/core/models.py:1855:    instrument_key: str
app/mme_scalpx/core/models.py:1873:        _require_non_empty_str(self.instrument_key, "instrument_key")
app/mme_scalpx/core/models.py:1895:    instrument_key: str
app/mme_scalpx/core/models.py:1899:    instrument_token: str | None = None
app/mme_scalpx/core/models.py:1900:    trading_symbol: str | None = None
app/mme_scalpx/core/models.py:1913:        _require_non_empty_str(self.instrument_key, "instrument_key")
app/mme_scalpx/core/models.py:1919:        if self.instrument_token is not None:
app/mme_scalpx/core/models.py:1920:            _optional_non_empty_str(self.instrument_token, "instrument_token")
app/mme_scalpx/core/models.py:1921:        if self.trading_symbol is not None:
app/mme_scalpx/core/models.py:1922:            _optional_non_empty_str(self.trading_symbol, "trading_symbol")
app/mme_scalpx/core/models.py:1941:    instrument_key: str
app/mme_scalpx/core/models.py:1947:    instrument_token: str | None = None
app/mme_scalpx/core/models.py:1948:    trading_symbol: str | None = None
app/mme_scalpx/core/models.py:1969:        _require_non_empty_str(self.instrument_key, "instrument_key")
app/mme_scalpx/core/models.py:1977:        if self.instrument_token is not None:
app/mme_scalpx/core/models.py:1978:            _optional_non_empty_str(self.instrument_token, "instrument_token")
app/mme_scalpx/core/models.py:1979:        if self.trading_symbol is not None:
app/mme_scalpx/core/models.py:1980:            _optional_non_empty_str(self.trading_symbol, "trading_symbol")
app/mme_scalpx/core/models.py:2018:    selected_call_instrument_key: str | None = None
app/mme_scalpx/core/models.py:2019:    selected_put_instrument_key: str | None = None
app/mme_scalpx/core/models.py:2020:    selected_call_option_symbol: str | None = None
app/mme_scalpx/core/models.py:2021:    selected_put_option_symbol: str | None = None
app/mme_scalpx/core/models.py:2022:    selected_call_option_token: str | None = None
app/mme_scalpx/core/models.py:2023:    selected_put_option_token: str | None = None
app/mme_scalpx/core/models.py:2080:            "selected_call_instrument_key",
app/mme_scalpx/core/models.py:2081:            "selected_put_instrument_key",
app/mme_scalpx/core/models.py:2082:            "selected_call_option_symbol",
app/mme_scalpx/core/models.py:2083:            "selected_put_option_symbol",
app/mme_scalpx/core/models.py:2084:            "selected_call_option_token",
app/mme_scalpx/core/models.py:2085:            "selected_put_option_token",
app/mme_scalpx/core/models.py:2160:    selected_call_instrument_key: str | None = None
app/mme_scalpx/core/models.py:2161:    selected_put_instrument_key: str | None = None
app/mme_scalpx/core/models.py:2162:    selected_call_option_symbol: str | None = None
app/mme_scalpx/core/models.py:2163:    selected_put_option_symbol: str | None = None
app/mme_scalpx/core/models.py:2164:    selected_call_option_token: str | None = None
app/mme_scalpx/core/models.py:2165:    selected_put_option_token: str | None = None
app/mme_scalpx/core/models.py:2237:            "selected_call_instrument_key",
app/mme_scalpx/core/models.py:2238:            "selected_put_instrument_key",
app/mme_scalpx/core/models.py:2239:            "selected_call_option_symbol",
app/mme_scalpx/core/models.py:2240:            "selected_put_option_symbol",
app/mme_scalpx/core/models.py:2241:            "selected_call_option_token",
app/mme_scalpx/core/models.py:2242:            "selected_put_option_token",
app/mme_scalpx/core/models.py:2515:    instrument_key: str | None = None
app/mme_scalpx/core/models.py:2516:    entry_option_symbol: str | None = None
app/mme_scalpx/core/models.py:2540:        if self.instrument_key is not None:
app/mme_scalpx/core/models.py:2541:            _optional_non_empty_str(self.instrument_key, "instrument_key")
app/mme_scalpx/core/models.py:2542:        if self.entry_option_symbol is not None:
app/mme_scalpx/core/models.py:2543:            _optional_non_empty_str(self.entry_option_symbol, "entry_option_symbol")
app/mme_scalpx/core/models.py:2582:            _require(self.instrument_key is not None, "open position requires instrument_key")
app/mme_scalpx/core/models.py:2711:    instrument_key: str
app/mme_scalpx/core/models.py:2727:        _require_non_empty_str(self.instrument_key, "instrument_key")
app/mme_scalpx/core/models.py:2880:    instrument_key: str | None = None
app/mme_scalpx/core/models.py:2902:        if self.instrument_key is not None:
app/mme_scalpx/core/models.py:2903:            _optional_non_empty_str(self.instrument_key, "instrument_key")
app/mme_scalpx/core/names.py:458:    "selected_call_instrument_key",
app/mme_scalpx/core/names.py:459:    "selected_put_instrument_key",
app/mme_scalpx/core/names.py:548:    "instrument_key",
app/mme_scalpx/core/names.py:553:    "option_symbol",
app/mme_scalpx/core/names.py:554:    "option_token",
app/mme_scalpx/domain/instruments.py:450:    instrument_token: str

## DHAN/provider context hits
app/mme_scalpx/core/models.py:211:MODEL_CONTRACT_DHAN_CONTEXT_KEYS: Final[tuple[str, ...]] = tuple(
app/mme_scalpx/core/models.py:212:    names.CONTRACT_DHAN_CONTEXT_KEYS
app/mme_scalpx/core/models.py:231:    names.STRATEGY_RUNTIME_MODE_DHAN_DEGRADED,
app/mme_scalpx/core/models.py:1100:class DhanStrikeScoreComponents(SchemaBase):
app/mme_scalpx/core/models.py:1110:    _TYPE: ClassVar[str] = "dhan_strike_score_components"
app/mme_scalpx/core/models.py:1144:    active_option_context_provider_id: str | None = None
app/mme_scalpx/core/models.py:1181:        if self.active_option_context_provider_id is not None:
app/mme_scalpx/core/models.py:1183:                self.active_option_context_provider_id,
app/mme_scalpx/core/models.py:1184:                "active_option_context_provider_id",
app/mme_scalpx/core/models.py:1259:    active_option_context_provider_id: str | None = None
app/mme_scalpx/core/models.py:1308:            "active_option_context_provider_id",
app/mme_scalpx/core/models.py:1359:    dhan_security_id: str | None = None
app/mme_scalpx/core/models.py:1376:            "dhan_security_id",
app/mme_scalpx/core/models.py:1408:    active_option_context_provider_id: str | None = None
app/mme_scalpx/core/models.py:1443:            "active_option_context_provider_id",
app/mme_scalpx/core/models.py:1495:    active_option_context_provider_id: str | None = None
app/mme_scalpx/core/models.py:1556:            "active_option_context_provider_id",
app/mme_scalpx/core/models.py:1593:                "active_option_context_provider_id": self.active_option_context_provider_id,
app/mme_scalpx/core/models.py:1623:            "active_option_context_provider_id": self.active_option_context_provider_id,
app/mme_scalpx/core/models.py:2013:class DhanContextEvent(SchemaBase):
app/mme_scalpx/core/models.py:2024:    selected_call_dhan_security_id: str | None = None
app/mme_scalpx/core/models.py:2025:    selected_put_dhan_security_id: str | None = None
app/mme_scalpx/core/models.py:2067:    selected_call_score_components: DhanStrikeScoreComponents | None = None
app/mme_scalpx/core/models.py:2068:    selected_put_score_components: DhanStrikeScoreComponents | None = None
app/mme_scalpx/core/models.py:2071:    _TYPE: ClassVar[str] = "dhan_context_event"
app/mme_scalpx/core/models.py:2086:            "selected_call_dhan_security_id",
app/mme_scalpx/core/models.py:2087:            "selected_put_dhan_security_id",
app/mme_scalpx/core/models.py:2155:class DhanContextState(SchemaBase):
app/mme_scalpx/core/models.py:2157:    provider_id: str = names.PROVIDER_DHAN
app/mme_scalpx/core/models.py:2166:    selected_call_dhan_security_id: str | None = None
app/mme_scalpx/core/models.py:2167:    selected_put_dhan_security_id: str | None = None
app/mme_scalpx/core/models.py:2228:    _TYPE: ClassVar[str] = "dhan_context_state"
app/mme_scalpx/core/models.py:2243:            "selected_call_dhan_security_id",
app/mme_scalpx/core/models.py:2244:            "selected_put_dhan_security_id",
app/mme_scalpx/core/models.py:2367:    option_context_provider_id: str
app/mme_scalpx/core/models.py:2392:            "option_context_provider_id",
app/mme_scalpx/core/models.py:2759:    active_option_context_provider_id: str | None = None
app/mme_scalpx/core/models.py:2795:            "active_option_context_provider_id",
app/mme_scalpx/core/models.py:3002:            DhanStrikeScoreComponents,
app/mme_scalpx/core/models.py:3019:            DhanContextEvent,
app/mme_scalpx/core/models.py:3020:            DhanContextState,
app/mme_scalpx/core/models.py:3083:    "DhanContextEvent",
app/mme_scalpx/core/models.py:3084:    "DhanContextState",
app/mme_scalpx/core/models.py:3085:    "DhanStrikeScoreComponents",
app/mme_scalpx/core/models.py:3103:    "MODEL_CONTRACT_DHAN_CONTEXT_KEYS",
app/mme_scalpx/core/names.py:314:PROVIDER_DHAN: Final[str] = "DHAN"
app/mme_scalpx/core/names.py:318:    PROVIDER_DHAN,
app/mme_scalpx/core/names.py:365:PROVIDER_OVERRIDE_MODE_FORCE_DHAN: Final[str] = "FORCE_DHAN"
app/mme_scalpx/core/names.py:370:    PROVIDER_OVERRIDE_MODE_FORCE_DHAN,
app/mme_scalpx/core/names.py:396:STRATEGY_RUNTIME_MODE_DHAN_DEGRADED: Final[str] = "DHAN_DEGRADED"
app/mme_scalpx/core/names.py:403:    STRATEGY_RUNTIME_MODE_DHAN_DEGRADED,
app/mme_scalpx/core/names.py:429:    "option_context_provider_id",
app/mme_scalpx/core/names.py:462:CONTRACT_DHAN_CONTEXT_KEYS: Final[tuple[str, ...]] = (
app/mme_scalpx/core/names.py:574:        "dhan_context": CONTRACT_DHAN_CONTEXT_KEYS,
app/mme_scalpx/core/names.py:587:        "active_option_context_provider_id": "option_context_provider_id",
app/mme_scalpx/core/names.py:592:        "option_context_provider_status": "option_context_status",
app/mme_scalpx/core/names.py:646:    _validate_tuple("CONTRACT_DHAN_CONTEXT_KEYS", CONTRACT_DHAN_CONTEXT_KEYS)
app/mme_scalpx/core/names.py:707:STREAM_TICKS_MME_FUT_DHAN: Final[str] = "ticks:mme:fut:dhan:stream"
app/mme_scalpx/core/names.py:709:STREAM_TICKS_MME_OPT_SELECTED_DHAN: Final[str] = "ticks:mme:opt:selected:dhan:stream"
app/mme_scalpx/core/names.py:710:STREAM_TICKS_MME_OPT_CONTEXT_DHAN: Final[str] = "ticks:mme:opt:context:dhan:stream"
app/mme_scalpx/core/names.py:715:    STREAM_TICKS_MME_FUT_DHAN,
app/mme_scalpx/core/names.py:717:    STREAM_TICKS_MME_OPT_SELECTED_DHAN,
app/mme_scalpx/core/names.py:718:    STREAM_TICKS_MME_OPT_CONTEXT_DHAN,
app/mme_scalpx/core/names.py:738:STREAM_REPLAY_TICKS_MME_FUT_DHAN: Final[str] = replay_name(STREAM_TICKS_MME_FUT_DHAN)
app/mme_scalpx/core/names.py:742:STREAM_REPLAY_TICKS_MME_OPT_SELECTED_DHAN: Final[str] = replay_name(
app/mme_scalpx/core/names.py:743:    STREAM_TICKS_MME_OPT_SELECTED_DHAN
app/mme_scalpx/core/names.py:745:STREAM_REPLAY_TICKS_MME_OPT_CONTEXT_DHAN: Final[str] = replay_name(
app/mme_scalpx/core/names.py:746:    STREAM_TICKS_MME_OPT_CONTEXT_DHAN
app/mme_scalpx/core/names.py:765:    STREAM_REPLAY_TICKS_MME_FUT_DHAN,
app/mme_scalpx/core/names.py:767:    STREAM_REPLAY_TICKS_MME_OPT_SELECTED_DHAN,
app/mme_scalpx/core/names.py:768:    STREAM_REPLAY_TICKS_MME_OPT_CONTEXT_DHAN,
app/mme_scalpx/core/names.py:811:HASH_STATE_SNAPSHOT_MME_FUT_DHAN: Final[str] = "state:snapshot:mme:fut:dhan"
app/mme_scalpx/core/names.py:816:HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_DHAN: Final[str] = (
app/mme_scalpx/core/names.py:817:    "state:snapshot:mme:opt:selected:dhan"
app/mme_scalpx/core/names.py:822:HASH_STATE_DHAN_CONTEXT: Final[str] = "state:context:mme:dhan"
app/mme_scalpx/core/names.py:827:    HASH_STATE_SNAPSHOT_MME_FUT_DHAN,
app/mme_scalpx/core/names.py:830:    HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_DHAN,
app/mme_scalpx/core/names.py:832:    HASH_STATE_DHAN_CONTEXT,
app/mme_scalpx/core/names.py:861:HASH_REPLAY_STATE_SNAPSHOT_MME_FUT_DHAN: Final[str] = replay_name(
app/mme_scalpx/core/names.py:862:    HASH_STATE_SNAPSHOT_MME_FUT_DHAN
app/mme_scalpx/core/names.py:870:HASH_REPLAY_STATE_SNAPSHOT_MME_OPT_SELECTED_DHAN: Final[str] = replay_name(
app/mme_scalpx/core/names.py:871:    HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_DHAN
app/mme_scalpx/core/names.py:876:HASH_REPLAY_STATE_DHAN_CONTEXT: Final[str] = replay_name(HASH_STATE_DHAN_CONTEXT)
app/mme_scalpx/core/names.py:899:    HASH_REPLAY_STATE_SNAPSHOT_MME_FUT_DHAN,
app/mme_scalpx/core/names.py:902:    HASH_REPLAY_STATE_SNAPSHOT_MME_OPT_SELECTED_DHAN,
app/mme_scalpx/core/names.py:904:    HASH_REPLAY_STATE_DHAN_CONTEXT,
app/mme_scalpx/core/names.py:937:KEY_HEALTH_DHAN_AUTH: Final[str] = "health:dhan:auth"
app/mme_scalpx/core/names.py:938:KEY_HEALTH_DHAN_MARKETDATA: Final[str] = "health:dhan:marketdata"
app/mme_scalpx/core/names.py:939:KEY_HEALTH_DHAN_EXECUTION: Final[str] = "health:dhan:execution"
app/mme_scalpx/core/names.py:946:    KEY_HEALTH_DHAN_AUTH,
app/mme_scalpx/core/names.py:947:    KEY_HEALTH_DHAN_MARKETDATA,
app/mme_scalpx/core/names.py:948:    KEY_HEALTH_DHAN_EXECUTION,
app/mme_scalpx/core/names.py:969:KEY_REPLAY_HEALTH_DHAN_AUTH: Final[str] = replay_name(KEY_HEALTH_DHAN_AUTH)
app/mme_scalpx/core/names.py:970:KEY_REPLAY_HEALTH_DHAN_MARKETDATA: Final[str] = replay_name(
app/mme_scalpx/core/names.py:971:    KEY_HEALTH_DHAN_MARKETDATA
app/mme_scalpx/core/names.py:973:KEY_REPLAY_HEALTH_DHAN_EXECUTION: Final[str] = replay_name(
app/mme_scalpx/core/names.py:974:    KEY_HEALTH_DHAN_EXECUTION
app/mme_scalpx/core/names.py:996:    KEY_REPLAY_HEALTH_DHAN_AUTH,
app/mme_scalpx/core/names.py:997:    KEY_REPLAY_HEALTH_DHAN_MARKETDATA,
app/mme_scalpx/core/names.py:998:    KEY_REPLAY_HEALTH_DHAN_EXECUTION,
app/mme_scalpx/core/names.py:1388:STATE_SNAPSHOT_FUT_DHAN: Final[str] = HASH_STATE_SNAPSHOT_MME_FUT_DHAN
app/mme_scalpx/core/names.py:1391:STATE_SNAPSHOT_OPT_SELECTED_DHAN: Final[str] = HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_DHAN
app/mme_scalpx/core/names.py:1393:STATE_DHAN_CONTEXT: Final[str] = HASH_STATE_DHAN_CONTEXT
app/mme_scalpx/core/names.py:1399:HB_DHAN_AUTH: Final[str] = KEY_HEALTH_DHAN_AUTH
app/mme_scalpx/core/names.py:1400:HB_DHAN_MARKETDATA: Final[str] = KEY_HEALTH_DHAN_MARKETDATA
app/mme_scalpx/core/names.py:1401:HB_DHAN_EXECUTION: Final[str] = KEY_HEALTH_DHAN_EXECUTION
app/mme_scalpx/core/names.py:1439:        "STATE_SNAPSHOT_FUT_DHAN": CompatibilityAliasDef("STATE_SNAPSHOT_FUT_DHAN", "HASH_STATE_SNAPSHOT_MME_FUT_DHAN", ALIAS_STATUS_TEMPORARY_MIGRATION, False),
app/mme_scalpx/core/names.py:1442:        "STATE_SNAPSHOT_OPT_SELECTED_DHAN": CompatibilityAliasDef("STATE_SNAPSHOT_OPT_SELECTED_DHAN", "HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_DHAN", ALIAS_STATUS_TEMPORARY_MIGRATION, False),
app/mme_scalpx/core/names.py:1444:        "STATE_DHAN_CONTEXT": CompatibilityAliasDef("STATE_DHAN_CONTEXT", "HASH_STATE_DHAN_CONTEXT", ALIAS_STATUS_TEMPORARY_MIGRATION, False),
app/mme_scalpx/core/names.py:1528:        STREAM_TICKS_MME_FUT_DHAN: SERVICE_FEEDS,
app/mme_scalpx/core/names.py:1530:        STREAM_TICKS_MME_OPT_SELECTED_DHAN: SERVICE_FEEDS,
app/mme_scalpx/core/names.py:1531:        STREAM_TICKS_MME_OPT_CONTEXT_DHAN: SERVICE_FEEDS,
app/mme_scalpx/core/names.py:1554:        HASH_STATE_SNAPSHOT_MME_FUT_DHAN: SERVICE_FEEDS,
app/mme_scalpx/core/names.py:1557:        HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_DHAN: SERVICE_FEEDS,
app/mme_scalpx/core/names.py:1559:        HASH_STATE_DHAN_CONTEXT: SERVICE_FEEDS,
app/mme_scalpx/core/names.py:1578:        KEY_HEALTH_DHAN_AUTH: SERVICE_LOGIN,
app/mme_scalpx/core/names.py:1579:        KEY_HEALTH_DHAN_MARKETDATA: SERVICE_FEEDS,
app/mme_scalpx/core/names.py:1580:        KEY_HEALTH_DHAN_EXECUTION: SERVICE_EXECUTION,
app/mme_scalpx/core/names.py:1804:    ticks_mme_fut_dhan: str
app/mme_scalpx/core/names.py:1806:    ticks_mme_opt_selected_dhan: str

## ZERODHA hits
app/mme_scalpx/core/models.py:1360:    zerodha_token: str | None = None
app/mme_scalpx/core/models.py:1377:            "zerodha_token",
app/mme_scalpx/core/models.py:2026:    selected_call_zerodha_token: str | None = None
app/mme_scalpx/core/models.py:2027:    selected_put_zerodha_token: str | None = None
app/mme_scalpx/core/models.py:2088:            "selected_call_zerodha_token",
app/mme_scalpx/core/models.py:2089:            "selected_put_zerodha_token",
app/mme_scalpx/core/models.py:2168:    selected_call_zerodha_token: str | None = None
app/mme_scalpx/core/models.py:2169:    selected_put_zerodha_token: str | None = None
app/mme_scalpx/core/models.py:2245:            "selected_call_zerodha_token",
app/mme_scalpx/core/models.py:2246:            "selected_put_zerodha_token",
app/mme_scalpx/core/models.py:2365:    futures_marketdata_provider_id: str
app/mme_scalpx/core/models.py:2366:    selected_option_marketdata_provider_id: str
app/mme_scalpx/core/models.py:2370:    futures_marketdata_status: str = names.PROVIDER_STATUS_HEALTHY
app/mme_scalpx/core/models.py:2371:    selected_option_marketdata_status: str = names.PROVIDER_STATUS_HEALTHY
app/mme_scalpx/core/models.py:2390:            "futures_marketdata_provider_id",
app/mme_scalpx/core/models.py:2391:            "selected_option_marketdata_provider_id",
app/mme_scalpx/core/models.py:2398:            "futures_marketdata_status",
app/mme_scalpx/core/models.py:2399:            "selected_option_marketdata_status",
app/mme_scalpx/core/names.py:313:PROVIDER_ZERODHA: Final[str] = "ZERODHA"
app/mme_scalpx/core/names.py:317:    PROVIDER_ZERODHA,
app/mme_scalpx/core/names.py:321:PROVIDER_ROLE_FUTURES_MARKETDATA: Final[str] = "futures_marketdata"
app/mme_scalpx/core/names.py:322:PROVIDER_ROLE_SELECTED_OPTION_MARKETDATA: Final[str] = "selected_option_marketdata"
app/mme_scalpx/core/names.py:328:    PROVIDER_ROLE_FUTURES_MARKETDATA,
app/mme_scalpx/core/names.py:329:    PROVIDER_ROLE_SELECTED_OPTION_MARKETDATA,
app/mme_scalpx/core/names.py:364:PROVIDER_OVERRIDE_MODE_FORCE_ZERODHA: Final[str] = "FORCE_ZERODHA"
app/mme_scalpx/core/names.py:369:    PROVIDER_OVERRIDE_MODE_FORCE_ZERODHA,
app/mme_scalpx/core/names.py:427:    "futures_marketdata_provider_id",
app/mme_scalpx/core/names.py:428:    "selected_option_marketdata_provider_id",
app/mme_scalpx/core/names.py:432:    "futures_marketdata_status",
app/mme_scalpx/core/names.py:433:    "selected_option_marketdata_status",
app/mme_scalpx/core/names.py:585:        "active_futures_provider_id": "futures_marketdata_provider_id",
app/mme_scalpx/core/names.py:586:        "active_selected_option_provider_id": "selected_option_marketdata_provider_id",
app/mme_scalpx/core/names.py:590:        "futures_provider_status": "futures_marketdata_status",
app/mme_scalpx/core/names.py:591:        "selected_option_provider_status": "selected_option_marketdata_status",
app/mme_scalpx/core/names.py:706:STREAM_TICKS_MME_FUT_ZERODHA: Final[str] = "ticks:mme:fut:zerodha:stream"
app/mme_scalpx/core/names.py:708:STREAM_TICKS_MME_OPT_SELECTED_ZERODHA: Final[str] = "ticks:mme:opt:selected:zerodha:stream"
app/mme_scalpx/core/names.py:714:    STREAM_TICKS_MME_FUT_ZERODHA,
app/mme_scalpx/core/names.py:716:    STREAM_TICKS_MME_OPT_SELECTED_ZERODHA,
app/mme_scalpx/core/names.py:737:STREAM_REPLAY_TICKS_MME_FUT_ZERODHA: Final[str] = replay_name(STREAM_TICKS_MME_FUT_ZERODHA)
app/mme_scalpx/core/names.py:739:STREAM_REPLAY_TICKS_MME_OPT_SELECTED_ZERODHA: Final[str] = replay_name(
app/mme_scalpx/core/names.py:740:    STREAM_TICKS_MME_OPT_SELECTED_ZERODHA
app/mme_scalpx/core/names.py:764:    STREAM_REPLAY_TICKS_MME_FUT_ZERODHA,
app/mme_scalpx/core/names.py:766:    STREAM_REPLAY_TICKS_MME_OPT_SELECTED_ZERODHA,
app/mme_scalpx/core/names.py:810:HASH_STATE_SNAPSHOT_MME_FUT_ZERODHA: Final[str] = "state:snapshot:mme:fut:zerodha"
app/mme_scalpx/core/names.py:813:HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA: Final[str] = (
app/mme_scalpx/core/names.py:814:    "state:snapshot:mme:opt:selected:zerodha"
app/mme_scalpx/core/names.py:826:    HASH_STATE_SNAPSHOT_MME_FUT_ZERODHA,
app/mme_scalpx/core/names.py:829:    HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA,
app/mme_scalpx/core/names.py:858:HASH_REPLAY_STATE_SNAPSHOT_MME_FUT_ZERODHA: Final[str] = replay_name(
app/mme_scalpx/core/names.py:859:    HASH_STATE_SNAPSHOT_MME_FUT_ZERODHA
app/mme_scalpx/core/names.py:867:HASH_REPLAY_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA: Final[str] = replay_name(
app/mme_scalpx/core/names.py:868:    HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA
app/mme_scalpx/core/names.py:898:    HASH_REPLAY_STATE_SNAPSHOT_MME_FUT_ZERODHA,
app/mme_scalpx/core/names.py:901:    HASH_REPLAY_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA,
app/mme_scalpx/core/names.py:934:KEY_HEALTH_ZERODHA_AUTH: Final[str] = "health:zerodha:auth"
app/mme_scalpx/core/names.py:935:KEY_HEALTH_ZERODHA_MARKETDATA: Final[str] = "health:zerodha:marketdata"
app/mme_scalpx/core/names.py:936:KEY_HEALTH_ZERODHA_EXECUTION: Final[str] = "health:zerodha:execution"
app/mme_scalpx/core/names.py:943:    KEY_HEALTH_ZERODHA_AUTH,
app/mme_scalpx/core/names.py:944:    KEY_HEALTH_ZERODHA_MARKETDATA,
app/mme_scalpx/core/names.py:945:    KEY_HEALTH_ZERODHA_EXECUTION,
app/mme_scalpx/core/names.py:962:KEY_REPLAY_HEALTH_ZERODHA_AUTH: Final[str] = replay_name(KEY_HEALTH_ZERODHA_AUTH)
app/mme_scalpx/core/names.py:963:KEY_REPLAY_HEALTH_ZERODHA_MARKETDATA: Final[str] = replay_name(
app/mme_scalpx/core/names.py:964:    KEY_HEALTH_ZERODHA_MARKETDATA
app/mme_scalpx/core/names.py:966:KEY_REPLAY_HEALTH_ZERODHA_EXECUTION: Final[str] = replay_name(
app/mme_scalpx/core/names.py:967:    KEY_HEALTH_ZERODHA_EXECUTION
app/mme_scalpx/core/names.py:993:    KEY_REPLAY_HEALTH_ZERODHA_AUTH,
app/mme_scalpx/core/names.py:994:    KEY_REPLAY_HEALTH_ZERODHA_MARKETDATA,
app/mme_scalpx/core/names.py:995:    KEY_REPLAY_HEALTH_ZERODHA_EXECUTION,
app/mme_scalpx/core/names.py:1387:STATE_SNAPSHOT_FUT_ZERODHA: Final[str] = HASH_STATE_SNAPSHOT_MME_FUT_ZERODHA
app/mme_scalpx/core/names.py:1390:STATE_SNAPSHOT_OPT_SELECTED_ZERODHA: Final[str] = HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA
app/mme_scalpx/core/names.py:1396:HB_ZERODHA_AUTH: Final[str] = KEY_HEALTH_ZERODHA_AUTH
app/mme_scalpx/core/names.py:1397:HB_ZERODHA_MARKETDATA: Final[str] = KEY_HEALTH_ZERODHA_MARKETDATA
app/mme_scalpx/core/names.py:1398:HB_ZERODHA_EXECUTION: Final[str] = KEY_HEALTH_ZERODHA_EXECUTION
app/mme_scalpx/core/names.py:1438:        "STATE_SNAPSHOT_FUT_ZERODHA": CompatibilityAliasDef("STATE_SNAPSHOT_FUT_ZERODHA", "HASH_STATE_SNAPSHOT_MME_FUT_ZERODHA", ALIAS_STATUS_TEMPORARY_MIGRATION, False),
app/mme_scalpx/core/names.py:1441:        "STATE_SNAPSHOT_OPT_SELECTED_ZERODHA": CompatibilityAliasDef("STATE_SNAPSHOT_OPT_SELECTED_ZERODHA", "HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA", ALIAS_STATUS_TEMPORARY_MIGRATION, False),
app/mme_scalpx/core/names.py:1527:        STREAM_TICKS_MME_FUT_ZERODHA: SERVICE_FEEDS,
app/mme_scalpx/core/names.py:1529:        STREAM_TICKS_MME_OPT_SELECTED_ZERODHA: SERVICE_FEEDS,
app/mme_scalpx/core/names.py:1553:        HASH_STATE_SNAPSHOT_MME_FUT_ZERODHA: SERVICE_FEEDS,
app/mme_scalpx/core/names.py:1556:        HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA: SERVICE_FEEDS,
app/mme_scalpx/core/names.py:1575:        KEY_HEALTH_ZERODHA_AUTH: SERVICE_LOGIN,
app/mme_scalpx/core/names.py:1576:        KEY_HEALTH_ZERODHA_MARKETDATA: SERVICE_FEEDS,
app/mme_scalpx/core/names.py:1577:        KEY_HEALTH_ZERODHA_EXECUTION: SERVICE_EXECUTION,
app/mme_scalpx/core/names.py:1803:    ticks_mme_fut_zerodha: str
app/mme_scalpx/core/names.py:1805:    ticks_mme_opt_selected_zerodha: str
app/mme_scalpx/core/names.py:1813:    snapshot_mme_fut_zerodha: str
app/mme_scalpx/core/names.py:1816:    snapshot_mme_opt_selected_zerodha: str
app/mme_scalpx/core/names.py:1825:    zerodha_auth: str
app/mme_scalpx/core/names.py:1826:    zerodha_marketdata: str
app/mme_scalpx/core/names.py:1827:    zerodha_execution: str
app/mme_scalpx/core/names.py:1925:    ticks_mme_fut_zerodha=STREAM_TICKS_MME_FUT_ZERODHA,
app/mme_scalpx/core/names.py:1927:    ticks_mme_opt_selected_zerodha=STREAM_TICKS_MME_OPT_SELECTED_ZERODHA,
app/mme_scalpx/core/names.py:1934:    ticks_mme_fut_zerodha=STREAM_REPLAY_TICKS_MME_FUT_ZERODHA,
app/mme_scalpx/core/names.py:1936:    ticks_mme_opt_selected_zerodha=STREAM_REPLAY_TICKS_MME_OPT_SELECTED_ZERODHA,
app/mme_scalpx/core/names.py:1943:    snapshot_mme_fut_zerodha=HASH_STATE_SNAPSHOT_MME_FUT_ZERODHA,
app/mme_scalpx/core/names.py:1946:    snapshot_mme_opt_selected_zerodha=HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA,
app/mme_scalpx/core/names.py:1954:    snapshot_mme_fut_zerodha=HASH_REPLAY_STATE_SNAPSHOT_MME_FUT_ZERODHA,
app/mme_scalpx/core/names.py:1957:    snapshot_mme_opt_selected_zerodha=HASH_REPLAY_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA,
app/mme_scalpx/core/names.py:1965:    zerodha_auth=KEY_HEALTH_ZERODHA_AUTH,
app/mme_scalpx/core/names.py:1966:    zerodha_marketdata=KEY_HEALTH_ZERODHA_MARKETDATA,
app/mme_scalpx/core/names.py:1967:    zerodha_execution=KEY_HEALTH_ZERODHA_EXECUTION,

## Provider/runtime readiness hits
app/mme_scalpx/core/models.py:227:    names.STRATEGY_RUNTIME_MODE_DISABLED,
app/mme_scalpx/core/models.py:232:    names.STRATEGY_RUNTIME_MODE_DISABLED,
app/mme_scalpx/core/models.py:319:def _validate_strategy_runtime_mode_for_family(
app/mme_scalpx/core/models.py:321:    strategy_runtime_mode: str | None,
app/mme_scalpx/core/models.py:325:    if strategy_family_id is None or strategy_runtime_mode is None:
app/mme_scalpx/core/models.py:334:        strategy_runtime_mode,
app/mme_scalpx/core/models.py:341:            strategy_runtime_mode in MISO_ALLOWED_STRATEGY_RUNTIME_MODES,
app/mme_scalpx/core/models.py:342:            f"{field_name}={strategy_runtime_mode!r} is invalid for MISO",
app/mme_scalpx/core/models.py:347:        strategy_runtime_mode in NON_MISO_ALLOWED_STRATEGY_RUNTIME_MODES,
app/mme_scalpx/core/models.py:348:        f"{field_name}={strategy_runtime_mode!r} is invalid for non-MISO family",
app/mme_scalpx/core/models.py:1140:    strategy_runtime_mode: str | None = None
app/mme_scalpx/core/models.py:1141:    family_runtime_mode: str | None = None
app/mme_scalpx/core/models.py:1165:        if self.strategy_runtime_mode is not None:
app/mme_scalpx/core/models.py:1166:            _validate_strategy_runtime_mode_for_family(
app/mme_scalpx/core/models.py:1168:                self.strategy_runtime_mode,
app/mme_scalpx/core/models.py:1169:                field_name="strategy_runtime_mode",
app/mme_scalpx/core/models.py:1171:        if self.family_runtime_mode is not None:
app/mme_scalpx/core/models.py:1172:            _require_literal(self.family_runtime_mode, "family_runtime_mode", allowed=ALLOWED_FAMILY_RUNTIME_MODES)
app/mme_scalpx/core/models.py:1252:    family_runtime_mode: str | None = None
app/mme_scalpx/core/models.py:1253:    strategy_runtime_mode: str | None = None
app/mme_scalpx/core/models.py:1285:        if self.family_runtime_mode is not None:
app/mme_scalpx/core/models.py:1286:            _require_literal(self.family_runtime_mode, "family_runtime_mode", allowed=ALLOWED_FAMILY_RUNTIME_MODES)
app/mme_scalpx/core/models.py:1287:        if self.strategy_runtime_mode is not None:
app/mme_scalpx/core/models.py:1288:            _validate_strategy_runtime_mode_for_family(
app/mme_scalpx/core/models.py:1290:                self.strategy_runtime_mode,
app/mme_scalpx/core/models.py:1291:                field_name="strategy_runtime_mode",
app/mme_scalpx/core/models.py:1396:    family_runtime_mode: str
app/mme_scalpx/core/models.py:1400:    strategy_runtime_mode: str | None = None
app/mme_scalpx/core/models.py:1423:        _require_literal(self.family_runtime_mode, "family_runtime_mode", allowed=ALLOWED_FAMILY_RUNTIME_MODES)
app/mme_scalpx/core/models.py:1424:        if self.strategy_runtime_mode is not None:
app/mme_scalpx/core/models.py:1425:            _validate_strategy_runtime_mode_for_family(
app/mme_scalpx/core/models.py:1427:                self.strategy_runtime_mode,
app/mme_scalpx/core/models.py:1428:                field_name="strategy_runtime_mode",
app/mme_scalpx/core/models.py:1480:    family_runtime_mode: str
app/mme_scalpx/core/models.py:1489:    strategy_runtime_mode: str | None = None
app/mme_scalpx/core/models.py:1527:        _require_literal(self.family_runtime_mode, "family_runtime_mode", allowed=ALLOWED_FAMILY_RUNTIME_MODES)
app/mme_scalpx/core/models.py:1528:        if self.strategy_runtime_mode is not None:
app/mme_scalpx/core/models.py:1529:            _validate_strategy_runtime_mode_for_family(
app/mme_scalpx/core/models.py:1531:                self.strategy_runtime_mode,
app/mme_scalpx/core/models.py:1532:                field_name="strategy_runtime_mode",
app/mme_scalpx/core/models.py:1586:                "family_runtime_mode": self.family_runtime_mode,
app/mme_scalpx/core/models.py:1587:                "strategy_runtime_mode": self.strategy_runtime_mode,
app/mme_scalpx/core/models.py:1616:            "family_runtime_mode": self.family_runtime_mode,
app/mme_scalpx/core/models.py:1617:            "strategy_runtime_mode": self.strategy_runtime_mode,
app/mme_scalpx/core/models.py:1644:    runtime_mode: str
app/mme_scalpx/core/models.py:1650:    config_file_runtime_mode: str | None = None
app/mme_scalpx/core/models.py:1651:    systemd_runtime_mode: str | None = None
app/mme_scalpx/core/models.py:1652:    env_runtime_mode: str | None = None
app/mme_scalpx/core/models.py:1653:    settings_runtime_mode: str | None = None
app/mme_scalpx/core/models.py:1654:    family_runtime_mode: str | None = None
app/mme_scalpx/core/models.py:1661:        allowed_runtime_modes = ("paper", "live", "replay")
app/mme_scalpx/core/models.py:1663:        _require_literal(self.runtime_mode, "runtime_mode", allowed=allowed_runtime_modes)
app/mme_scalpx/core/models.py:1670:            "config_file_runtime_mode",
app/mme_scalpx/core/models.py:1671:            "systemd_runtime_mode",
app/mme_scalpx/core/models.py:1672:            "env_runtime_mode",
app/mme_scalpx/core/models.py:1673:            "settings_runtime_mode",
app/mme_scalpx/core/models.py:1677:                _require_literal(value, field_name, allowed=allowed_runtime_modes)
app/mme_scalpx/core/models.py:1678:        if self.family_runtime_mode is not None:
app/mme_scalpx/core/models.py:1679:            _require_literal(self.family_runtime_mode, "family_runtime_mode", allowed=ALLOWED_FAMILY_RUNTIME_MODES)
app/mme_scalpx/core/models.py:2375:    family_runtime_mode: str = names.FAMILY_RUNTIME_MODE_OBSERVE_ONLY
app/mme_scalpx/core/models.py:2405:        _require_literal(self.family_runtime_mode, "family_runtime_mode", allowed=ALLOWED_FAMILY_RUNTIME_MODES)
app/mme_scalpx/core/models.py:2426:    family_runtime_mode: str | None = None
app/mme_scalpx/core/models.py:2448:        if self.family_runtime_mode is not None:
app/mme_scalpx/core/models.py:2449:            _require_literal(self.family_runtime_mode, "family_runtime_mode", allowed=ALLOWED_FAMILY_RUNTIME_MODES)
app/mme_scalpx/core/models.py:2471:    family_runtime_mode: str
app/mme_scalpx/core/models.py:2472:    strategy_runtime_mode: str | None = None
app/mme_scalpx/core/models.py:2479:    _TYPE: ClassVar[str] = "runtime_mode_state"
app/mme_scalpx/core/models.py:2483:            self.family_runtime_mode,
app/mme_scalpx/core/models.py:2484:            "family_runtime_mode",
app/mme_scalpx/core/models.py:2490:        if self.strategy_runtime_mode is not None:
app/mme_scalpx/core/models.py:2491:            _validate_strategy_runtime_mode_for_family(
app/mme_scalpx/core/models.py:2493:                self.strategy_runtime_mode,
app/mme_scalpx/core/models.py:2494:                field_name="strategy_runtime_mode",
app/mme_scalpx/core/models.py:2595:    family_runtime_mode: str | None = None
app/mme_scalpx/core/models.py:2596:    strategy_runtime_mode: str | None = None
app/mme_scalpx/core/models.py:2620:        if self.family_runtime_mode is not None:
app/mme_scalpx/core/models.py:2621:            _require_literal(self.family_runtime_mode, "family_runtime_mode", allowed=ALLOWED_FAMILY_RUNTIME_MODES)
app/mme_scalpx/core/models.py:2622:        if self.strategy_runtime_mode is not None:
app/mme_scalpx/core/models.py:2623:            _require_literal(self.strategy_runtime_mode, "strategy_runtime_mode", allowed=ALLOWED_STRATEGY_RUNTIME_MODES)
app/mme_scalpx/core/models.py:2719:    strategy_runtime_mode: str | None = None
app/mme_scalpx/core/models.py:2720:    family_runtime_mode: str | None = None
app/mme_scalpx/core/models.py:2735:        if self.strategy_runtime_mode is not None:
app/mme_scalpx/core/models.py:2736:            _validate_strategy_runtime_mode_for_family(
app/mme_scalpx/core/models.py:2738:                self.strategy_runtime_mode,
app/mme_scalpx/core/models.py:2739:                field_name="strategy_runtime_mode",
app/mme_scalpx/core/models.py:2741:        if self.family_runtime_mode is not None:
app/mme_scalpx/core/models.py:2742:            _require_literal(self.family_runtime_mode, "family_runtime_mode", allowed=ALLOWED_FAMILY_RUNTIME_MODES)
app/mme_scalpx/core/models.py:2755:    family_runtime_mode: str | None = None
app/mme_scalpx/core/models.py:2756:    strategy_runtime_mode: str | None = None
app/mme_scalpx/core/models.py:2784:        if self.family_runtime_mode is not None:
app/mme_scalpx/core/models.py:2785:            _require_literal(self.family_runtime_mode, "family_runtime_mode", allowed=ALLOWED_FAMILY_RUNTIME_MODES)
app/mme_scalpx/core/models.py:2786:        if self.strategy_runtime_mode is not None:
app/mme_scalpx/core/models.py:2787:            _validate_strategy_runtime_mode_for_family(
app/mme_scalpx/core/models.py:2789:                self.strategy_runtime_mode,
app/mme_scalpx/core/models.py:2790:                field_name="strategy_runtime_mode",
app/mme_scalpx/core/names.py:339:PROVIDER_STATUS_UNAVAILABLE: Final[str] = "UNAVAILABLE"
app/mme_scalpx/core/names.py:340:PROVIDER_STATUS_DISABLED: Final[str] = "DISABLED"
app/mme_scalpx/core/names.py:341:PROVIDER_STATUS_FAILOVER_ACTIVE: Final[str] = "FAILOVER_ACTIVE"
app/mme_scalpx/core/names.py:348:    PROVIDER_STATUS_UNAVAILABLE,
app/mme_scalpx/core/names.py:349:    PROVIDER_STATUS_DISABLED,
app/mme_scalpx/core/names.py:350:    PROVIDER_STATUS_FAILOVER_ACTIVE,
app/mme_scalpx/core/names.py:399:STRATEGY_RUNTIME_MODE_DISABLED: Final[str] = "DISABLED"
app/mme_scalpx/core/names.py:406:    STRATEGY_RUNTIME_MODE_DISABLED,
app/mme_scalpx/core/names.py:437:    "family_runtime_mode",
app/mme_scalpx/core/names.py:1306:STATE_DISABLED: Final[str] = "DISABLED"
app/mme_scalpx/core/names.py:1320:    STATE_DISABLED,
app/mme_scalpx/core/names.py:1331:CONTROL_MODE_DISABLED: Final[str] = "DISABLED"
app/mme_scalpx/core/names.py:1337:    CONTROL_MODE_DISABLED,
app/mme_scalpx/core/settings.py:400:# Batch 3 deliberately does not change runtime_mode behavior. settings.py still
app/mme_scalpx/core/settings.py:419:def runtime_mode_input_snapshot(env: Mapping[str, str]) -> dict[str, str | None]:
app/mme_scalpx/core/settings.py:424:        "settings_allowed_runtime_modes": ",".join(_ALLOWED_RUNTIME_MODES),
app/mme_scalpx/core/settings.py:425:        "settings_default_runtime_mode": DEFAULT_RUNTIME_MODE,
app/mme_scalpx/core/settings.py:429:def validate_runtime_mode_input_snapshot(env: Mapping[str, str]) -> dict[str, str | None]:
app/mme_scalpx/core/settings.py:433:    SCALPX_* into settings.runtime.runtime_mode before the main.py audit.
app/mme_scalpx/core/settings.py:435:    snapshot = runtime_mode_input_snapshot(env)
app/mme_scalpx/core/settings.py:450:    runtime_mode: str
app/mme_scalpx/core/settings.py:459:        if self.runtime_mode not in _ALLOWED_RUNTIME_MODES:
app/mme_scalpx/core/settings.py:461:                f"runtime_mode must be one of {_ALLOWED_RUNTIME_MODES}, got {self.runtime_mode!r}"
app/mme_scalpx/core/settings.py:488:        return self.runtime_mode == "live"
app/mme_scalpx/core/settings.py:492:        return self.runtime_mode == "replay"
app/mme_scalpx/core/settings.py:784:    runtime_mode = _parse_choice(
app/mme_scalpx/core/settings.py:827:        runtime_mode=runtime_mode,
app/mme_scalpx/core/settings.py:1437:    "runtime_mode_input_snapshot",
app/mme_scalpx/core/settings.py:1438:    "validate_runtime_mode_input_snapshot",
app/mme_scalpx/core/settings.py:1480:def runtime_mode_input_snapshot(
app/mme_scalpx/core/settings.py:1495:        "settings_allowed_runtime_modes": ",".join(str(x) for x in allowed),
app/mme_scalpx/core/settings.py:1496:        "settings_default_runtime_mode": str(default),
app/mme_scalpx/core/settings.py:1502:    settings_runtime_mode: str,
app/mme_scalpx/core/settings.py:1504:    project_env_runtime_mode: str | None = None,
app/mme_scalpx/core/settings.py:1505:    env_runtime_mode: str | None = None,
app/mme_scalpx/core/settings.py:1510:        "settings_runtime_mode": settings_runtime_mode,
app/mme_scalpx/core/settings.py:1512:        "project_env_runtime_mode": project_env_runtime_mode,
app/mme_scalpx/core/settings.py:1513:        "env_runtime_mode": env_runtime_mode,
app/mme_scalpx/core/settings.py:1521:        conflicts.append("runtime_mode_mismatch")
app/mme_scalpx/core/settings.py:1536:    for _name in ("runtime_mode_input_snapshot", "build_effective_runtime_config_state"):
app/mme_scalpx/integrations/bootstrap_provider.py:184:            else names.PROVIDER_STATUS_UNAVAILABLE
app/mme_scalpx/integrations/bootstrap_provider.py:186:        "dhan_execution_fallback_status": names.PROVIDER_STATUS_DISABLED,
app/mme_scalpx/integrations/broker_api.py:1572:        status="FAIL_CLOSED_BACKEND_CALL_DISABLED_IN_A6_R3",
app/mme_scalpx/integrations/broker_auth.py:85:_STATUS_UNAVAILABLE: str = getattr(names, "PROVIDER_STATUS_UNAVAILABLE", "UNAVAILABLE")
app/mme_scalpx/integrations/broker_auth.py:86:_STATUS_DISABLED: str = getattr(names, "PROVIDER_STATUS_DISABLED", "DISABLED")
