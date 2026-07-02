# LANE-X-R34L_RUNTIME_IDENTITY_SOURCE_SCHEMA_LOCATOR_NO_PATCH_NO_REPLAY_NO_ORDER_locate_selected_option_symbol_token_publication_path_for_strategy_shadow_identity_export_20260613_134631

classification: PASS_R34L_RUNTIME_IDENTITY_SOURCE_SCHEMA_LOCATED_FOR_MANUAL_INSPECTION_NO_PATCH_NO_REPLAY_NO_ORDER
proof: `run/proofs/LANE-X-R34L_RUNTIME_IDENTITY_SOURCE_SCHEMA_LOCATOR_NO_PATCH_NO_REPLAY_NO_ORDER_locate_selected_option_symbol_token_publication_path_for_strategy_shadow_identity_export_20260613_134631.json`
audit_dir: `run/audits/LANE-X-R34L_RUNTIME_IDENTITY_SOURCE_SCHEMA_LOCATOR_NO_PATCH_NO_REPLAY_NO_ORDER_locate_selected_option_symbol_token_publication_path_for_strategy_shadow_identity_export_20260613_134631`

## Counts
- compile_rc: 0
- identity_hits: 1628
- activation_hits: 79
- publication_hits: 763

## Safety
- orders/risk/execution: 0 / 0 / 0
- risk/execution proc: 0 / 0

## Key hits
# source_identity_grep selected hits
3:app/mme_scalpx/core/models.py:717:    instrument_key: str
4:app/mme_scalpx/core/models.py:723:    instrument_token: str | None = None
5:app/mme_scalpx/core/models.py:724:    trading_symbol: str | None = None
6:app/mme_scalpx/core/models.py:743:    is_selected_option: bool = False
7:app/mme_scalpx/core/models.py:749:        _require_non_empty_str(self.instrument_key, "instrument_key")
8:app/mme_scalpx/core/models.py:762:        if self.instrument_token is not None:
9:app/mme_scalpx/core/models.py:763:            _optional_non_empty_str(self.instrument_token, "instrument_token")
10:app/mme_scalpx/core/models.py:764:        if self.trading_symbol is not None:
11:app/mme_scalpx/core/models.py:765:            _optional_non_empty_str(self.trading_symbol, "trading_symbol")
12:app/mme_scalpx/core/models.py:797:        _require_bool(self.is_selected_option, "is_selected_option")
13:app/mme_scalpx/core/models.py:807:    instrument_key: str
14:app/mme_scalpx/core/models.py:812:    instrument_token: str | None = None
15:app/mme_scalpx/core/models.py:813:    trading_symbol: str | None = None
16:app/mme_scalpx/core/models.py:830:        _require_non_empty_str(self.instrument_key, "instrument_key")
17:app/mme_scalpx/core/models.py:837:        if self.instrument_token is not None:
18:app/mme_scalpx/core/models.py:838:            _optional_non_empty_str(self.instrument_token, "instrument_token")
19:app/mme_scalpx/core/models.py:839:        if self.trading_symbol is not None:
20:app/mme_scalpx/core/models.py:840:            _optional_non_empty_str(self.trading_symbol, "trading_symbol")
21:app/mme_scalpx/core/models.py:867:    instrument_key: str
22:app/mme_scalpx/core/models.py:875:    instrument_token: str | None = None
23:app/mme_scalpx/core/models.py:876:    trading_symbol: str | None = None
24:app/mme_scalpx/core/models.py:890:    is_selected_option: bool = False
25:app/mme_scalpx/core/models.py:896:        _require_non_empty_str(self.instrument_key, "instrument_key")
26:app/mme_scalpx/core/models.py:907:        if self.instrument_token is not None:
27:app/mme_scalpx/core/models.py:908:            _optional_non_empty_str(self.instrument_token, "instrument_token")
28:app/mme_scalpx/core/models.py:909:        if self.trading_symbol is not None:
29:app/mme_scalpx/core/models.py:910:            _optional_non_empty_str(self.trading_symbol, "trading_symbol")
30:app/mme_scalpx/core/models.py:933:        _require_bool(self.is_selected_option, "is_selected_option")
31:app/mme_scalpx/core/models.py:942:    instrument_token: str
32:app/mme_scalpx/core/models.py:943:    trading_symbol: str
33:app/mme_scalpx/core/models.py:966:        _require_non_empty_str(self.instrument_token, "instrument_token")
34:app/mme_scalpx/core/models.py:967:        _require_non_empty_str(self.trading_symbol, "trading_symbol")
35:app/mme_scalpx/core/models.py:1131:    instrument_key: str
36:app/mme_scalpx/core/models.py:1143:    active_selected_option_provider_id: str | None = None
37:app/mme_scalpx/core/models.py:1157:        _require_non_empty_str(self.instrument_key, "instrument_key")
38:app/mme_scalpx/core/models.py:1175:        if self.active_selected_option_provider_id is not None:
39:app/mme_scalpx/core/models.py:1177:                self.active_selected_option_provider_id,
40:app/mme_scalpx/core/models.py:1178:                "active_selected_option_provider_id",
41:app/mme_scalpx/core/models.py:1248:    instrument_key: str | None = None
42:app/mme_scalpx/core/models.py:1258:    active_selected_option_provider_id: str | None = None
43:app/mme_scalpx/core/models.py:1297:            "instrument_key",
44:app/mme_scalpx/core/models.py:1307:            "active_selected_option_provider_id",
45:app/mme_scalpx/core/models.py:1324:            _require(bool(self.instrument_key), "entry actions require non-empty instrument_key")
46:app/mme_scalpx/core/models.py:1353:    instrument_key: str
47:app/mme_scalpx/core/models.py:1354:    option_symbol: str
48:app/mme_scalpx/core/models.py:1362:    trading_symbol: str | None = None
49:app/mme_scalpx/core/models.py:1368:        _require_non_empty_str(self.instrument_key, "instrument_key")
50:app/mme_scalpx/core/models.py:1369:        _require_non_empty_str(self.option_symbol, "option_symbol")
51:app/mme_scalpx/core/models.py:1379:            "trading_symbol",
52:app/mme_scalpx/core/models.py:1407:    active_selected_option_provider_id: str | None = None
53:app/mme_scalpx/core/models.py:1409:    instrument_key: str | None = None
54:app/mme_scalpx/core/models.py:1410:    option_symbol: str | None = None
55:app/mme_scalpx/core/models.py:1442:            "active_selected_option_provider_id",
56:app/mme_scalpx/core/models.py:1448:        for field_name in ("instrument_key", "option_symbol", "option_token"):
57:app/mme_scalpx/core/models.py:1476:    instrument_key: str
58:app/mme_scalpx/core/models.py:1481:    option_symbol: str
59:app/mme_scalpx/core/models.py:1494:    active_selected_option_provider_id: str | None = None
60:app/mme_scalpx/core/models.py:1523:        _require_non_empty_str(self.instrument_key, "instrument_key")
61:app/mme_scalpx/core/models.py:1540:        _require_non_empty_str(self.option_symbol, "option_symbol")
62:app/mme_scalpx/core/models.py:1555:            "active_selected_option_provider_id",
63:app/mme_scalpx/core/models.py:1573:                "option_symbol": self.option_symbol,
64:app/mme_scalpx/core/models.py:1577:                "provider_id": self.active_selected_option_provider_id,
65:app/mme_scalpx/core/models.py:1592:                "active_selected_option_provider_id": self.active_selected_option_provider_id,
66:app/mme_scalpx/core/models.py:1612:            "instrument_key": self.instrument_key,
67:app/mme_scalpx/core/models.py:1622:            "active_selected_option_provider_id": self.active_selected_option_provider_id,
68:app/mme_scalpx/core/models.py:1747:    instrument_key: str
69:app/mme_scalpx/core/models.py:1763:        _require_non_empty_str(self.instrument_key, "instrument_key")
70:app/mme_scalpx/core/models.py:1783:    instrument_key: str
71:app/mme_scalpx/core/models.py:1799:        _require_non_empty_str(self.instrument_key, "instrument_key")
72:app/mme_scalpx/core/models.py:1820:    instrument_key: str
73:app/mme_scalpx/core/models.py:1837:        _require_non_empty_str(self.instrument_key, "instrument_key")
74:app/mme_scalpx/core/models.py:1855:    instrument_key: str
75:app/mme_scalpx/core/models.py:1873:        _require_non_empty_str(self.instrument_key, "instrument_key")
76:app/mme_scalpx/core/models.py:1895:    instrument_key: str
77:app/mme_scalpx/core/models.py:1899:    instrument_token: str | None = None
78:app/mme_scalpx/core/models.py:1900:    trading_symbol: str | None = None
79:app/mme_scalpx/core/models.py:1913:        _require_non_empty_str(self.instrument_key, "instrument_key")
80:app/mme_scalpx/core/models.py:1919:        if self.instrument_token is not None:
81:app/mme_scalpx/core/models.py:1920:            _optional_non_empty_str(self.instrument_token, "instrument_token")
82:app/mme_scalpx/core/models.py:1921:        if self.trading_symbol is not None:
83:app/mme_scalpx/core/models.py:1922:            _optional_non_empty_str(self.trading_symbol, "trading_symbol")
84:app/mme_scalpx/core/models.py:1941:    instrument_key: str
85:app/mme_scalpx/core/models.py:1947:    instrument_token: str | None = None
86:app/mme_scalpx/core/models.py:1948:    trading_symbol: str | None = None
87:app/mme_scalpx/core/models.py:1964:    is_selected_option: bool = False
88:app/mme_scalpx/core/models.py:1969:        _require_non_empty_str(self.instrument_key, "instrument_key")
89:app/mme_scalpx/core/models.py:1977:        if self.instrument_token is not None:
90:app/mme_scalpx/core/models.py:1978:            _optional_non_empty_str(self.instrument_token, "instrument_token")
91:app/mme_scalpx/core/models.py:1979:        if self.trading_symbol is not None:
92:app/mme_scalpx/core/models.py:1980:            _optional_non_empty_str(self.trading_symbol, "trading_symbol")
93:app/mme_scalpx/core/models.py:2007:        _require_bool(self.is_selected_option, "is_selected_option")
94:app/mme_scalpx/core/models.py:2018:    selected_call_instrument_key: str | None = None
95:app/mme_scalpx/core/models.py:2019:    selected_put_instrument_key: str | None = None
96:app/mme_scalpx/core/models.py:2020:    selected_call_option_symbol: str | None = None
97:app/mme_scalpx/core/models.py:2021:    selected_put_option_symbol: str | None = None
100:app/mme_scalpx/core/models.py:2080:            "selected_call_instrument_key",
101:app/mme_scalpx/core/models.py:2081:            "selected_put_instrument_key",
102:app/mme_scalpx/core/models.py:2082:            "selected_call_option_symbol",
103:app/mme_scalpx/core/models.py:2083:            "selected_put_option_symbol",
106:app/mme_scalpx/core/models.py:2160:    selected_call_instrument_key: str | None = None
107:app/mme_scalpx/core/models.py:2161:    selected_put_instrument_key: str | None = None
108:app/mme_scalpx/core/models.py:2162:    selected_call_option_symbol: str | None = None
109:app/mme_scalpx/core/models.py:2163:    selected_put_option_symbol: str | None = None
112:app/mme_scalpx/core/models.py:2237:            "selected_call_instrument_key",
113:app/mme_scalpx/core/models.py:2238:            "selected_put_instrument_key",
114:app/mme_scalpx/core/models.py:2239:            "selected_call_option_symbol",
115:app/mme_scalpx/core/models.py:2240:            "selected_put_option_symbol",
118:app/mme_scalpx/core/models.py:2366:    selected_option_marketdata_provider_id: str
119:app/mme_scalpx/core/models.py:2371:    selected_option_marketdata_status: str = names.PROVIDER_STATUS_HEALTHY
120:app/mme_scalpx/core/models.py:2391:            "selected_option_marketdata_provider_id",
121:app/mme_scalpx/core/models.py:2399:            "selected_option_marketdata_status",
122:app/mme_scalpx/core/models.py:2515:    instrument_key: str | None = None
123:app/mme_scalpx/core/models.py:2516:    entry_option_symbol: str | None = None
124:app/mme_scalpx/core/models.py:2540:        if self.instrument_key is not None:
125:app/mme_scalpx/core/models.py:2541:            _optional_non_empty_str(self.instrument_key, "instrument_key")
126:app/mme_scalpx/core/models.py:2542:        if self.entry_option_symbol is not None:
127:app/mme_scalpx/core/models.py:2543:            _optional_non_empty_str(self.entry_option_symbol, "entry_option_symbol")
128:app/mme_scalpx/core/models.py:2582:            _require(self.instrument_key is not None, "open position requires instrument_key")
129:app/mme_scalpx/core/models.py:2711:    instrument_key: str
130:app/mme_scalpx/core/models.py:2727:        _require_non_empty_str(self.instrument_key, "instrument_key")

# activation selected hits
1:app/mme_scalpx/services/strategy.py:434:def _r34f_shadow_candidate_truth_from_activation_selected(
2:app/mme_scalpx/services/strategy.py:510:            "activation_selected_report_only_shadow" if is_enter else ""
8:app/mme_scalpx/services/strategy.py:1075:        activation_selected = _mapping(activation_report.get("selected"))
9:app/mme_scalpx/services/strategy.py:1076:        activation_candidates = activation_report.get("candidates")
10:app/mme_scalpx/services/strategy.py:1078:            len(activation_candidates)
11:app/mme_scalpx/services/strategy.py:1079:            if isinstance(activation_candidates, list)
12:app/mme_scalpx/services/strategy.py:1082:        r34f_shadow_fields = _r34f_shadow_candidate_truth_from_activation_selected(
13:app/mme_scalpx/services/strategy.py:1083:            activation_selected,
14:app/mme_scalpx/services/strategy.py:1121:            "activation_selected_family_id": _safe_str(activation_selected.get("family_id")),
15:app/mme_scalpx/services/strategy.py:1122:            "activation_selected_branch_id": _safe_str(activation_selected.get("branch_id")),
16:app/mme_scalpx/services/strategy.py:1123:            "activation_selected_action": _safe_str(activation_selected.get("action")),
17:app/mme_scalpx/services/strategy.py:1124:            "activation_selected_score": activation_selected.get("score"),
18:app/mme_scalpx/services/strategy.py:1143:                    "activation_selected_family_id": _safe_str(activation_selected.get("family_id")),
19:app/mme_scalpx/services/strategy.py:1144:                    "activation_selected_branch_id": _safe_str(activation_selected.get("branch_id")),
20:app/mme_scalpx/services/strategy.py:2005:        or view.get("activation_selected_family_id")
21:app/mme_scalpx/services/strategy.py.r34k_backup:434:def _r34f_shadow_candidate_truth_from_activation_selected(
22:app/mme_scalpx/services/strategy.py.r34k_backup:452:            "activation_selected_report_only_shadow" if is_enter else ""
28:app/mme_scalpx/services/strategy.py.r34k_backup:1013:        activation_selected = _mapping(activation_report.get("selected"))
29:app/mme_scalpx/services/strategy.py.r34k_backup:1014:        activation_candidates = activation_report.get("candidates")
30:app/mme_scalpx/services/strategy.py.r34k_backup:1016:            len(activation_candidates)
31:app/mme_scalpx/services/strategy.py.r34k_backup:1017:            if isinstance(activation_candidates, list)
32:app/mme_scalpx/services/strategy.py.r34k_backup:1020:        r34f_shadow_fields = _r34f_shadow_candidate_truth_from_activation_selected(
33:app/mme_scalpx/services/strategy.py.r34k_backup:1021:            activation_selected
34:app/mme_scalpx/services/strategy.py.r34k_backup:1058:            "activation_selected_family_id": _safe_str(activation_selected.get("family_id")),
35:app/mme_scalpx/services/strategy.py.r34k_backup:1059:            "activation_selected_branch_id": _safe_str(activation_selected.get("branch_id")),
36:app/mme_scalpx/services/strategy.py.r34k_backup:1060:            "activation_selected_action": _safe_str(activation_selected.get("action")),
37:app/mme_scalpx/services/strategy.py.r34k_backup:1061:            "activation_selected_score": activation_selected.get("score"),
38:app/mme_scalpx/services/strategy.py.r34k_backup:1080:                    "activation_selected_family_id": _safe_str(activation_selected.get("family_id")),
39:app/mme_scalpx/services/strategy.py.r34k_backup:1081:                    "activation_selected_branch_id": _safe_str(activation_selected.get("branch_id")),
40:app/mme_scalpx/services/strategy.py.r34k_backup:1942:        or view.get("activation_selected_family_id")
41:app/mme_scalpx/services/controlled_paper_runtime.py:309:        c["_a6_r3_score"] = float(c.get("score", c.get("activation_selected_score", 0.0)) or 0.0)
48:app/mme_scalpx/services/strategy_family/activation.py:505:def rank_activation_candidates(
50:app/mme_scalpx/services/strategy_family/activation.py:542:    candidates = rank_activation_candidates(frames, config=cfg)
53:app/mme_scalpx/services/strategy_family/activation.py:665:    "rank_activation_candidates",
67:app/mme_scalpx/services/strategy.py.r34f_r1_backup:977:        activation_selected = _mapping(activation_report.get("selected"))
68:app/mme_scalpx/services/strategy.py.r34f_r1_backup:978:        activation_candidates = activation_report.get("candidates")
69:app/mme_scalpx/services/strategy.py.r34f_r1_backup:980:            len(activation_candidates)
70:app/mme_scalpx/services/strategy.py.r34f_r1_backup:981:            if isinstance(activation_candidates, list)
71:app/mme_scalpx/services/strategy.py.r34f_r1_backup:1019:            "activation_selected_family_id": _safe_str(activation_selected.get("family_id")),
72:app/mme_scalpx/services/strategy.py.r34f_r1_backup:1020:            "activation_selected_branch_id": _safe_str(activation_selected.get("branch_id")),
73:app/mme_scalpx/services/strategy.py.r34f_r1_backup:1021:            "activation_selected_action": _safe_str(activation_selected.get("action")),
74:app/mme_scalpx/services/strategy.py.r34f_r1_backup:1022:            "activation_selected_score": activation_selected.get("score"),
75:app/mme_scalpx/services/strategy.py.r34f_r1_backup:1040:                    "activation_selected_family_id": _safe_str(activation_selected.get("family_id")),
76:app/mme_scalpx/services/strategy.py.r34f_r1_backup:1041:                    "activation_selected_branch_id": _safe_str(activation_selected.get("branch_id")),
77:app/mme_scalpx/services/strategy.py.r34f_r1_backup:1902:        or view.get("activation_selected_family_id")

# strategy decision publication hits
2:app/mme_scalpx/services/strategy.py:398:    Convert strategy decision payload into Redis XADD-safe fields.
3:app/mme_scalpx/services/strategy.py:400:    Execution consumes decisions through payload_json. During the HOLD-only
4:app/mme_scalpx/services/strategy.py:402:    but payload_json is the canonical execution contract.
5:app/mme_scalpx/services/strategy.py:410:        "payload_json": _json_dump(raw),
6:app/mme_scalpx/services/strategy.py:416:        # payload_json above is canonical. Do not allow an incoming flat field
7:app/mme_scalpx/services/strategy.py:418:        if field == "payload_json":
8:app/mme_scalpx/services/strategy.py:590:    Prove flat fields and canonical payload_json cannot drift.
9:app/mme_scalpx/services/strategy.py:592:    execution.py consumes payload_json as canonical. The strategy publisher must
10:app/mme_scalpx/services/strategy.py:593:    therefore ensure that payload_json.action and payload_json.qty preserve the
11:app/mme_scalpx/services/strategy.py:597:    payload = _mapping(_json_load(fields.get("payload_json"), field_name="payload_json"))

## Decision
Inspect key hits. If selected option identity exists in runtime view/source, patch exact extractor path. If not, patch source publication before R34J.
