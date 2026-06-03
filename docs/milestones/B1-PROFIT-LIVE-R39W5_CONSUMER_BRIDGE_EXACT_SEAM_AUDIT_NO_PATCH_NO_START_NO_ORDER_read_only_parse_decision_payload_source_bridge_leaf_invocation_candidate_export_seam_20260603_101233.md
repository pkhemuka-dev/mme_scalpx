# B1-PROFIT-LIVE-R39W5_CONSUMER_BRIDGE_EXACT_SEAM_AUDIT_NO_PATCH_NO_START_NO_ORDER_read_only_parse_decision_payload_source_bridge_leaf_invocation_candidate_export_seam_20260603_101233

Classification: `BLOCKED_R39W5_CLASSIC_BRIDGE_SAFE_BUT_ZERO_CANDIDATES_NEEDS_LEAF_INVOCATION_OR_EXPORT_SEAM_PATCH_PLAN`

## Current XLEN / safety
```text
orders:mme:stream=0
risk:mme:stream=0
execution:mme:stream=0
system:errors:stream=3
decisions:mme:stream=496
features:mme:stream=283
```

## Interpretation
- Live decisions exist, but this audit determines whether they are only bridge-HOLD decisions.
- Paper remains blocked.
- No patch/start/stop/delete/order was performed.

## Decision reason counts
- hold_only_family_features_consumer_bridge: 496

## Activation reason counts
- no_candidate: 420
- view_data_invalid: 76

## Candidate count counts
- 0: 496

## Readiness counts
- safe_to_consume: {'1': 496}
- data_valid: {'1': 420, '0': 76}
- provider_ready_classic: {'1': 430, '0': 66}
- provider_ready_miso: {'0': 496}

## Activation bridge counts
- activation_bridge_enabled: {'1': 496}
- activation_report_only: {'1': 496}
- activation_mode: {'dry_run': 496}
- activation_selected_family: {'': 496}
- activation_selected_branch: {'': 496}
- activation_selected_action: {'': 496}

## Feature snapshot
- valid: False
- validity: MARKETDATA_COMPOSITION_FAIL
- sync_ok: False
- freshness_ok: True
- packet_gap_ok: True
- warmup_ok: True
- active_snapshot_ns: 1780481549000000000
- futures_snapshot_ns: 1780481549000000000
- selected_option_snapshot_ns: None
- dhan_futures_snapshot_ns: None
- dhan_option_snapshot_ns: None
- max_member_age_ms: 0
- fut_opt_skew_ms: None
- hard_packet_gap_ms: 1000
- samples_seen: 1

## Selected option feature state
```json
{
  "delta_3": null,
  "depth_ok": true,
  "depth_total": 1690.0,
  "ltp": 185.3,
  "micro_edge": null,
  "microprice": null,
  "ofi_ratio_proxy": null,
  "response_efficiency": 0.0,
  "side": "CALL",
  "spread": 0.4000000000000057,
  "spread_ratio": 0.0021727322107550555,
  "tradability_ok": false
}
```

## Family eval summary
- mist_call: {'family_id': 'MIST', 'branch_id': 'CALL', 'runtime_mode': 'NORMAL', 'family_runtime_mode': 'OBSERVE_ONLY', 'instrument_key': '10825730', 'instrument_token': '10825730', 'option_symbol': 'NIFTY2660923300CE', 'strike': 23300.0, 'option_price': 195.0, 'eligible': False, 'tradability_ok': False}
  - $.eligible: false
  - $.tradability_ok: false
  - $.surface.futures_features.raw.validity_reason: "invalid_members:CE_ATM,PE_ATM,PE_ATM1"
  - $.surface.futures_features.trend_score: 0.0
  - $.surface.futures_features.direction_score: 0.0
  - $.surface.futures_features.contradiction_score_call: -0.0
  - $.surface.futures_features.contradiction_score_put: 0.0
  - $.surface.futures_features.context_score: 0.8999999999999999
- mist_put: {'family_id': 'MIST', 'branch_id': 'PUT', 'runtime_mode': 'NORMAL', 'family_runtime_mode': 'OBSERVE_ONLY', 'instrument_key': '10825986', 'instrument_token': '10825986', 'option_symbol': 'NIFTY2660923300PE', 'strike': 23300.0, 'option_price': 211.15, 'eligible': False, 'tradability_ok': False}
  - $.eligible: false
  - $.tradability_ok: false
  - $.surface.futures_features.raw.validity_reason: "invalid_members:CE_ATM,PE_ATM,PE_ATM1"
  - $.surface.futures_features.trend_score: 0.0
  - $.surface.futures_features.direction_score: 0.0
  - $.surface.futures_features.contradiction_score_call: -0.0
  - $.surface.futures_features.contradiction_score_put: 0.0
  - $.surface.futures_features.context_score: 0.8999999999999999
- misb_call: {'family_id': 'MISB', 'branch_id': 'CALL', 'runtime_mode': 'NORMAL', 'family_runtime_mode': 'OBSERVE_ONLY', 'instrument_key': '10825730', 'instrument_token': '10825730', 'option_symbol': 'NIFTY2660923300CE', 'strike': 23300.0, 'option_price': 195.0, 'eligible': False, 'tradability_ok': False}
  - $.eligible: false
  - $.tradability_ok: false
  - $.surface.futures_features.raw.validity_reason: "invalid_members:CE_ATM,PE_ATM,PE_ATM1"
  - $.surface.futures_features.trend_score: 0.0
  - $.surface.futures_features.direction_score: 0.0
  - $.surface.futures_features.contradiction_score_call: -0.0
  - $.surface.futures_features.contradiction_score_put: 0.0
  - $.surface.futures_features.context_score: 0.8999999999999999
- misb_put: {'family_id': 'MISB', 'branch_id': 'PUT', 'runtime_mode': 'NORMAL', 'family_runtime_mode': 'OBSERVE_ONLY', 'instrument_key': '10825986', 'instrument_token': '10825986', 'option_symbol': 'NIFTY2660923300PE', 'strike': 23300.0, 'option_price': 211.15, 'eligible': False, 'tradability_ok': False}
  - $.eligible: false
  - $.tradability_ok: false
  - $.surface.futures_features.raw.validity_reason: "invalid_members:CE_ATM,PE_ATM,PE_ATM1"
  - $.surface.futures_features.trend_score: 0.0
  - $.surface.futures_features.direction_score: 0.0
  - $.surface.futures_features.contradiction_score_call: -0.0
  - $.surface.futures_features.contradiction_score_put: 0.0
  - $.surface.futures_features.context_score: 0.8999999999999999
- misc_call: {'family_id': 'MISC', 'branch_id': 'CALL', 'runtime_mode': 'NORMAL', 'family_runtime_mode': 'OBSERVE_ONLY', 'instrument_key': '10825730', 'instrument_token': '10825730', 'option_symbol': 'NIFTY2660923300CE', 'strike': 23300.0, 'option_price': 195.0, 'eligible': False, 'tradability_ok': False}
  - $.eligible: false
  - $.tradability_ok: false
  - $.surface.futures_features.raw.validity_reason: "invalid_members:CE_ATM,PE_ATM,PE_ATM1"
  - $.surface.futures_features.trend_score: 0.0
  - $.surface.futures_features.direction_score: 0.0
  - $.surface.futures_features.contradiction_score_call: -0.0
  - $.surface.futures_features.contradiction_score_put: 0.0
  - $.surface.futures_features.context_score: 0.8999999999999999
- misc_put: {'family_id': 'MISC', 'branch_id': 'PUT', 'runtime_mode': 'NORMAL', 'family_runtime_mode': 'OBSERVE_ONLY', 'instrument_key': '10825986', 'instrument_token': '10825986', 'option_symbol': 'NIFTY2660923300PE', 'strike': 23300.0, 'option_price': 211.15, 'eligible': False, 'tradability_ok': False}
  - $.eligible: false
  - $.tradability_ok: false
  - $.surface.futures_features.raw.validity_reason: "invalid_members:CE_ATM,PE_ATM,PE_ATM1"
  - $.surface.futures_features.trend_score: 0.0
  - $.surface.futures_features.direction_score: 0.0
  - $.surface.futures_features.contradiction_score_call: -0.0
  - $.surface.futures_features.contradiction_score_put: 0.0
  - $.surface.futures_features.context_score: 0.8999999999999999
- misr_call: {'family_id': 'MISR', 'branch_id': 'CALL', 'runtime_mode': 'NORMAL', 'family_runtime_mode': 'OBSERVE_ONLY', 'instrument_key': '10825730', 'instrument_token': '10825730', 'option_symbol': 'NIFTY2660923300CE', 'strike': 23300.0, 'option_price': 195.0, 'eligible': False, 'tradability_ok': False}
  - $.eligible: false
  - $.tradability_ok: false
  - $.surface.futures_features.raw.validity_reason: "invalid_members:CE_ATM,PE_ATM,PE_ATM1"
  - $.surface.futures_features.trend_score: 0.0
  - $.surface.futures_features.direction_score: 0.0
  - $.surface.futures_features.contradiction_score_call: -0.0
  - $.surface.futures_features.contradiction_score_put: 0.0
  - $.surface.futures_features.context_score: 0.8999999999999999
- misr_put: {'family_id': 'MISR', 'branch_id': 'PUT', 'runtime_mode': 'NORMAL', 'family_runtime_mode': 'OBSERVE_ONLY', 'instrument_key': '10825986', 'instrument_token': '10825986', 'option_symbol': 'NIFTY2660923300PE', 'strike': 23300.0, 'option_price': 211.15, 'eligible': False, 'tradability_ok': False}
  - $.eligible: false
  - $.tradability_ok: false
  - $.surface.futures_features.raw.validity_reason: "invalid_members:CE_ATM,PE_ATM,PE_ATM1"
  - $.surface.futures_features.trend_score: 0.0
  - $.surface.futures_features.direction_score: 0.0
  - $.surface.futures_features.contradiction_score_call: -0.0
  - $.surface.futures_features.contradiction_score_put: 0.0
  - $.surface.futures_features.context_score: 0.8999999999999999
- miso_call: {'family_id': 'MISO', 'branch_id': 'CALL', 'runtime_mode': 'DISABLED', 'family_runtime_mode': 'OBSERVE_ONLY', 'instrument_key': '10825730', 'instrument_token': '10825730', 'option_symbol': 'NIFTY2660923300CE', 'strike': 23300.0, 'option_price': 195.0, 'eligible': False, 'tradability_ok': True}
  - $.eligible: false
  - $.tradability_ok: true
  - $.surface.futures_features.raw.validity_reason: "invalid_members:CE_ATM,PE_ATM,PE_ATM1"
  - $.surface.futures_features.trend_score: 0.0
  - $.surface.futures_features.direction_score: 0.0
  - $.surface.futures_features.contradiction_score_call: -0.0
  - $.surface.futures_features.contradiction_score_put: 0.0
  - $.surface.futures_features.context_score: 0.8999999999999999
- miso_put: {'family_id': 'MISO', 'branch_id': 'PUT', 'runtime_mode': 'DISABLED', 'family_runtime_mode': 'OBSERVE_ONLY', 'instrument_key': '10825986', 'instrument_token': '10825986', 'option_symbol': 'NIFTY2660923300PE', 'strike': 23300.0, 'option_price': 211.15, 'eligible': False, 'tradability_ok': True}
  - $.eligible: false
  - $.tradability_ok: true
  - $.surface.futures_features.raw.validity_reason: "invalid_members:CE_ATM,PE_ATM,PE_ATM1"
  - $.surface.futures_features.trend_score: 0.0
  - $.surface.futures_features.direction_score: 0.0
  - $.surface.futures_features.contradiction_score_call: -0.0
  - $.surface.futures_features.contradiction_score_put: 0.0
  - $.surface.futures_features.context_score: 0.8999999999999999

## Decision samples
- {'id': '1780461753940-0', 'reason': 'hold_only_family_features_consumer_bridge', 'action': 'HOLD', 'hold_only': 1, 'safe_to_consume': 1, 'data_valid': 0, 'provider_ready_classic': 1, 'provider_ready_miso': 0, 'activation_bridge_enabled': 1, 'activation_report_only': 1, 'activation_mode': 'dry_run', 'activation_reason': 'view_data_invalid', 'activation_candidate_count': 0, 'activation_selected_family_id': '', 'activation_selected_branch_id': '', 'activation_selected_action': '', 'activation_selected_score': None, 'price': 185.3, 'features_generated_at_ns': 1780461751862285824}
- {'id': '1780461753028-0', 'reason': 'hold_only_family_features_consumer_bridge', 'action': 'HOLD', 'hold_only': 1, 'safe_to_consume': 1, 'data_valid': 0, 'provider_ready_classic': 0, 'provider_ready_miso': 0, 'activation_bridge_enabled': 1, 'activation_report_only': 1, 'activation_mode': 'dry_run', 'activation_reason': 'view_data_invalid', 'activation_candidate_count': 0, 'activation_selected_family_id': '', 'activation_selected_branch_id': '', 'activation_selected_action': '', 'activation_selected_score': None, 'price': 195.0, 'features_generated_at_ns': 1780461751862285824}
- {'id': '1780461752431-0', 'reason': 'hold_only_family_features_consumer_bridge', 'action': 'HOLD', 'hold_only': 1, 'safe_to_consume': 1, 'data_valid': 1, 'provider_ready_classic': 1, 'provider_ready_miso': 0, 'activation_bridge_enabled': 1, 'activation_report_only': 1, 'activation_mode': 'dry_run', 'activation_reason': 'no_candidate', 'activation_candidate_count': 0, 'activation_selected_family_id': '', 'activation_selected_branch_id': '', 'activation_selected_action': '', 'activation_selected_score': None, 'price': 186.7, 'features_generated_at_ns': 1780461748557197568}
- {'id': '1780461751791-0', 'reason': 'hold_only_family_features_consumer_bridge', 'action': 'HOLD', 'hold_only': 1, 'safe_to_consume': 1, 'data_valid': 1, 'provider_ready_classic': 1, 'provider_ready_miso': 0, 'activation_bridge_enabled': 1, 'activation_report_only': 1, 'activation_mode': 'dry_run', 'activation_reason': 'no_candidate', 'activation_candidate_count': 0, 'activation_selected_family_id': '', 'activation_selected_branch_id': '', 'activation_selected_action': '', 'activation_selected_score': None, 'price': 186.7, 'features_generated_at_ns': 1780461748557197568}
- {'id': '1780461751182-0', 'reason': 'hold_only_family_features_consumer_bridge', 'action': 'HOLD', 'hold_only': 1, 'safe_to_consume': 1, 'data_valid': 1, 'provider_ready_classic': 1, 'provider_ready_miso': 0, 'activation_bridge_enabled': 1, 'activation_report_only': 1, 'activation_mode': 'dry_run', 'activation_reason': 'no_candidate', 'activation_candidate_count': 0, 'activation_selected_family_id': '', 'activation_selected_branch_id': '', 'activation_selected_action': '', 'activation_selected_score': None, 'price': 186.7, 'features_generated_at_ns': 1780461748557197568}
- {'id': '1780461750336-0', 'reason': 'hold_only_family_features_consumer_bridge', 'action': 'HOLD', 'hold_only': 1, 'safe_to_consume': 1, 'data_valid': 1, 'provider_ready_classic': 1, 'provider_ready_miso': 0, 'activation_bridge_enabled': 1, 'activation_report_only': 1, 'activation_mode': 'dry_run', 'activation_reason': 'no_candidate', 'activation_candidate_count': 0, 'activation_selected_family_id': '', 'activation_selected_branch_id': '', 'activation_selected_action': '', 'activation_selected_score': None, 'price': 186.7, 'features_generated_at_ns': 1780461748557197568}
- {'id': '1780461749338-0', 'reason': 'hold_only_family_features_consumer_bridge', 'action': 'HOLD', 'hold_only': 1, 'safe_to_consume': 1, 'data_valid': 1, 'provider_ready_classic': 1, 'provider_ready_miso': 0, 'activation_bridge_enabled': 1, 'activation_report_only': 1, 'activation_mode': 'dry_run', 'activation_reason': 'no_candidate', 'activation_candidate_count': 0, 'activation_selected_family_id': '', 'activation_selected_branch_id': '', 'activation_selected_action': '', 'activation_selected_score': None, 'price': 171.0, 'features_generated_at_ns': 1780461745046711040}
- {'id': '1780461748563-0', 'reason': 'hold_only_family_features_consumer_bridge', 'action': 'HOLD', 'hold_only': 1, 'safe_to_consume': 1, 'data_valid': 1, 'provider_ready_classic': 1, 'provider_ready_miso': 0, 'activation_bridge_enabled': 1, 'activation_report_only': 1, 'activation_mode': 'dry_run', 'activation_reason': 'no_candidate', 'activation_candidate_count': 0, 'activation_selected_family_id': '', 'activation_selected_branch_id': '', 'activation_selected_action': '', 'activation_selected_score': None, 'price': 171.0, 'features_generated_at_ns': 1780461745046711040}
- {'id': '1780461747870-0', 'reason': 'hold_only_family_features_consumer_bridge', 'action': 'HOLD', 'hold_only': 1, 'safe_to_consume': 1, 'data_valid': 1, 'provider_ready_classic': 1, 'provider_ready_miso': 0, 'activation_bridge_enabled': 1, 'activation_report_only': 1, 'activation_mode': 'dry_run', 'activation_reason': 'no_candidate', 'activation_candidate_count': 0, 'activation_selected_family_id': '', 'activation_selected_branch_id': '', 'activation_selected_action': '', 'activation_selected_score': None, 'price': 171.0, 'features_generated_at_ns': 1780461745046711040}
- {'id': '1780461747187-0', 'reason': 'hold_only_family_features_consumer_bridge', 'action': 'HOLD', 'hold_only': 1, 'safe_to_consume': 1, 'data_valid': 1, 'provider_ready_classic': 1, 'provider_ready_miso': 0, 'activation_bridge_enabled': 1, 'activation_report_only': 1, 'activation_mode': 'dry_run', 'activation_reason': 'no_candidate', 'activation_candidate_count': 0, 'activation_selected_family_id': '', 'activation_selected_branch_id': '', 'activation_selected_action': '', 'activation_selected_score': None, 'price': 171.0, 'features_generated_at_ns': 1780461745046711040}
- {'id': '1780461746188-0', 'reason': 'hold_only_family_features_consumer_bridge', 'action': 'HOLD', 'hold_only': 1, 'safe_to_consume': 1, 'data_valid': 0, 'provider_ready_classic': 0, 'provider_ready_miso': 0, 'activation_bridge_enabled': 1, 'activation_report_only': 1, 'activation_mode': 'dry_run', 'activation_reason': 'view_data_invalid', 'activation_candidate_count': 0, 'activation_selected_family_id': '', 'activation_selected_branch_id': '', 'activation_selected_action': '', 'activation_selected_score': None, 'price': 194.7, 'features_generated_at_ns': 1780461745046711040}
- {'id': '1780461745596-0', 'reason': 'hold_only_family_features_consumer_bridge', 'action': 'HOLD', 'hold_only': 1, 'safe_to_consume': 1, 'data_valid': 1, 'provider_ready_classic': 1, 'provider_ready_miso': 0, 'activation_bridge_enabled': 1, 'activation_report_only': 1, 'activation_mode': 'dry_run', 'activation_reason': 'no_candidate', 'activation_candidate_count': 0, 'activation_selected_family_id': '', 'activation_selected_branch_id': '', 'activation_selected_action': '', 'activation_selected_score': None, 'price': 170.45, 'features_generated_at_ns': 1780461741814814976}
- {'id': '1780461745045-0', 'reason': 'hold_only_family_features_consumer_bridge', 'action': 'HOLD', 'hold_only': 1, 'safe_to_consume': 1, 'data_valid': 1, 'provider_ready_classic': 1, 'provider_ready_miso': 0, 'activation_bridge_enabled': 1, 'activation_report_only': 1, 'activation_mode': 'dry_run', 'activation_reason': 'no_candidate', 'activation_candidate_count': 0, 'activation_selected_family_id': '', 'activation_selected_branch_id': '', 'activation_selected_action': '', 'activation_selected_score': None, 'price': 170.45, 'features_generated_at_ns': 1780461741814814976}
- {'id': '1780461744446-0', 'reason': 'hold_only_family_features_consumer_bridge', 'action': 'HOLD', 'hold_only': 1, 'safe_to_consume': 1, 'data_valid': 1, 'provider_ready_classic': 1, 'provider_ready_miso': 0, 'activation_bridge_enabled': 1, 'activation_report_only': 1, 'activation_mode': 'dry_run', 'activation_reason': 'no_candidate', 'activation_candidate_count': 0, 'activation_selected_family_id': '', 'activation_selected_branch_id': '', 'activation_selected_action': '', 'activation_selected_score': None, 'price': 170.45, 'features_generated_at_ns': 1780461741814814976}
- {'id': '1780461743579-0', 'reason': 'hold_only_family_features_consumer_bridge', 'action': 'HOLD', 'hold_only': 1, 'safe_to_consume': 1, 'data_valid': 1, 'provider_ready_classic': 1, 'provider_ready_miso': 0, 'activation_bridge_enabled': 1, 'activation_report_only': 1, 'activation_mode': 'dry_run', 'activation_reason': 'no_candidate', 'activation_candidate_count': 0, 'activation_selected_family_id': '', 'activation_selected_branch_id': '', 'activation_selected_action': '', 'activation_selected_score': None, 'price': 170.45, 'features_generated_at_ns': 1780461741814814976}

## Candidate/blocker key hits from decision payloads
- decision=1780461753940-0 $.activation_bridge_enabled: 1
- decision=1780461753940-0 $.activation_report_only: 1
- decision=1780461753940-0 $.activation_mode: "dry_run"
- decision=1780461753940-0 $.activation_action: "HOLD"
- decision=1780461753940-0 $.activation_observed_action: "HOLD"
- decision=1780461753940-0 $.activation_promoted: 0
- decision=1780461753940-0 $.activation_safe_to_promote: 0
- decision=1780461753940-0 $.activation_reason: "view_data_invalid"
- decision=1780461753940-0 $.activation_selected_family_id: ""
- decision=1780461753940-0 $.activation_selected_branch_id: ""
- decision=1780461753940-0 $.activation_selected_action: ""
- decision=1780461753940-0 $.activation_selected_score: null
- decision=1780461753940-0 $.activation_candidate_count: 0
- decision=1780461753940-0 $.activation_report_json: "{\"activation_mode\":\"dry_run\",\"action\":\"HOLD\",\"hold\":true,\"promoted\":false,\"safe_to_promote\":false,\"reason\":\"view_data_invalid\",\"selected\":null,\"candidates\":[],\"blocked\":[],\"no_signal\":[],\"family_count\":5,\"branch_count\":2,\"metadata\":{\"gate\":\"global\",\"leaf_evaluation_skipped\":true,\"batch11_fail_closed\":true},\"strategy_report_only\":true,\"strategy_ts_ns\":1780461753190395566,\"live_orders_allowed\":false,\"family_runtime_enabled\":false,\"family_runtime_gate_reason\":\"view_data_invalid\",\"family_runtime_family_id\":\"GLOBAL\",\"family_runtime_branch_id\":\"GLOBAL_GATE\",\"family_runtime_action\":\"HOLD\",\"family_runtime_activation_mode\":\"dry_run\",\"family_runtime_report_only\":true,\"family_runtime_safe_to_promote\":false,\"family_runtime_promoted\":false}"
- decision=1780461753028-0 $.activation_bridge_enabled: 1
- decision=1780461753028-0 $.activation_report_only: 1
- decision=1780461753028-0 $.activation_mode: "dry_run"
- decision=1780461753028-0 $.activation_action: "HOLD"
- decision=1780461753028-0 $.activation_observed_action: "HOLD"
- decision=1780461753028-0 $.activation_promoted: 0
- decision=1780461753028-0 $.activation_safe_to_promote: 0
- decision=1780461753028-0 $.activation_reason: "view_data_invalid"
- decision=1780461753028-0 $.activation_selected_family_id: ""
- decision=1780461753028-0 $.activation_selected_branch_id: ""
- decision=1780461753028-0 $.activation_selected_action: ""
- decision=1780461753028-0 $.activation_selected_score: null
- decision=1780461753028-0 $.activation_candidate_count: 0
- decision=1780461753028-0 $.activation_report_json: "{\"activation_mode\":\"dry_run\",\"action\":\"HOLD\",\"hold\":true,\"promoted\":false,\"safe_to_promote\":false,\"reason\":\"view_data_invalid\",\"selected\":null,\"candidates\":[],\"blocked\":[],\"no_signal\":[],\"family_count\":5,\"branch_count\":2,\"metadata\":{\"gate\":\"global\",\"leaf_evaluation_skipped\":true,\"batch11_fail_closed\":true},\"strategy_report_only\":true,\"strategy_ts_ns\":1780461752638430572,\"live_orders_allowed\":false,\"family_runtime_enabled\":false,\"family_runtime_gate_reason\":\"view_data_invalid\",\"family_runtime_family_id\":\"GLOBAL\",\"family_runtime_branch_id\":\"GLOBAL_GATE\",\"family_runtime_action\":\"HOLD\",\"family_runtime_activation_mode\":\"dry_run\",\"family_runtime_report_only\":true,\"family_runtime_safe_to_promote\":false,\"family_runtime_promoted\":false}"
- decision=1780461752431-0 $.activation_bridge_enabled: 1
- decision=1780461752431-0 $.activation_report_only: 1
- decision=1780461752431-0 $.activation_mode: "dry_run"
- decision=1780461752431-0 $.activation_action: "HOLD"
- decision=1780461752431-0 $.activation_observed_action: "HOLD"
- decision=1780461752431-0 $.activation_promoted: 0
- decision=1780461752431-0 $.activation_safe_to_promote: 0
- decision=1780461752431-0 $.activation_reason: "no_candidate"
- decision=1780461752431-0 $.activation_selected_family_id: ""
- decision=1780461752431-0 $.activation_selected_branch_id: ""
- decision=1780461752431-0 $.activation_selected_action: ""
- decision=1780461752431-0 $.activation_selected_score: null
- decision=1780461752431-0 $.activation_candidate_count: 0
- decision=1780461752431-0 $.activation_report_json: "{\"activation_mode\":\"dry_run\",\"action\":\"HOLD\",\"hold\":true,\"promoted\":false,\"safe_to_promote\":false,\"reason\":\"no_candidate\",\"selected\":null,\"candidates\":[],\"blocked\":[],\"no_signal\":[{\"family_id\":\"MIST\",\"branch_id\":\"CALL\",\"is_candidate\":false,\"is_blocked\":false,\"is_no_signal\":true,\"action\":\"HOLD\",\"score\":0.0,\"priority\":0.0,\"candidate\":{},\"blocker\":{},\"reason\":\"classic_runtime_disabled\",\"raw\":{\"family_id\":\"MIST\",\"doctrine_id\":\"MIST\",\"branch_id\":\"CALL\",\"action\":\"HOLD\",\"is_candidate\":false,\"is_blocked\":false,\"is_no_signal\":true,\"candidate\":null,\"blocker\":null,\"metadata\":{\"reason\":\"classic_runtime_disabled\"},\"lane_f_r4r15h_raw_diagnostic_wiring\":true,\"family_runtime_enabled\":false,\"family_runtime_gate_reason\":\"classic_runtime_disabled\",\"family_runtime_family_id\":\"MIST\",\"family_runtime_branch_id\":\"CALL\",\"family_runtime_action\":\"HOLD\",\"family_runtime_activation_mode\":null,\"family_ru
- decision=1780461751791-0 $.activation_bridge_enabled: 1
- decision=1780461751791-0 $.activation_report_only: 1
- decision=1780461751791-0 $.activation_mode: "dry_run"
- decision=1780461751791-0 $.activation_action: "HOLD"
- decision=1780461751791-0 $.activation_observed_action: "HOLD"
- decision=1780461751791-0 $.activation_promoted: 0
- decision=1780461751791-0 $.activation_safe_to_promote: 0
- decision=1780461751791-0 $.activation_reason: "no_candidate"
- decision=1780461751791-0 $.activation_selected_family_id: ""
- decision=1780461751791-0 $.activation_selected_branch_id: ""
- decision=1780461751791-0 $.activation_selected_action: ""
- decision=1780461751791-0 $.activation_selected_score: null
- decision=1780461751791-0 $.activation_candidate_count: 0
- decision=1780461751791-0 $.activation_report_json: "{\"activation_mode\":\"dry_run\",\"action\":\"HOLD\",\"hold\":true,\"promoted\":false,\"safe_to_promote\":false,\"reason\":\"no_candidate\",\"selected\":null,\"candidates\":[],\"blocked\":[],\"no_signal\":[{\"family_id\":\"MIST\",\"branch_id\":\"CALL\",\"is_candidate\":false,\"is_blocked\":false,\"is_no_signal\":true,\"action\":\"HOLD\",\"score\":0.0,\"priority\":0.0,\"candidate\":{},\"blocker\":{},\"reason\":\"classic_runtime_disabled\",\"raw\":{\"family_id\":\"MIST\",\"doctrine_id\":\"MIST\",\"branch_id\":\"CALL\",\"action\":\"HOLD\",\"is_candidate\":false,\"is_blocked\":false,\"is_no_signal\":true,\"candidate\":null,\"blocker\":null,\"metadata\":{\"reason\":\"classic_runtime_disabled\"},\"lane_f_r4r15h_raw_diagnostic_wiring\":true,\"family_runtime_enabled\":false,\"family_runtime_gate_reason\":\"classic_runtime_disabled\",\"family_runtime_family_id\":\"MIST\",\"family_runtime_branch_id\":\"CALL\",\"family_runtime_action\":\"HOLD\",\"family_runtime_activation_mode\":null,\"family_ru
- decision=1780461751182-0 $.activation_bridge_enabled: 1
- decision=1780461751182-0 $.activation_report_only: 1
- decision=1780461751182-0 $.activation_mode: "dry_run"
- decision=1780461751182-0 $.activation_action: "HOLD"
- decision=1780461751182-0 $.activation_observed_action: "HOLD"
- decision=1780461751182-0 $.activation_promoted: 0
- decision=1780461751182-0 $.activation_safe_to_promote: 0
- decision=1780461751182-0 $.activation_reason: "no_candidate"
- decision=1780461751182-0 $.activation_selected_family_id: ""
- decision=1780461751182-0 $.activation_selected_branch_id: ""
- decision=1780461751182-0 $.activation_selected_action: ""
- decision=1780461751182-0 $.activation_selected_score: null
- decision=1780461751182-0 $.activation_candidate_count: 0
- decision=1780461751182-0 $.activation_report_json: "{\"activation_mode\":\"dry_run\",\"action\":\"HOLD\",\"hold\":true,\"promoted\":false,\"safe_to_promote\":false,\"reason\":\"no_candidate\",\"selected\":null,\"candidates\":[],\"blocked\":[],\"no_signal\":[{\"family_id\":\"MIST\",\"branch_id\":\"CALL\",\"is_candidate\":false,\"is_blocked\":false,\"is_no_signal\":true,\"action\":\"HOLD\",\"score\":0.0,\"priority\":0.0,\"candidate\":{},\"blocker\":{},\"reason\":\"classic_runtime_disabled\",\"raw\":{\"family_id\":\"MIST\",\"doctrine_id\":\"MIST\",\"branch_id\":\"CALL\",\"action\":\"HOLD\",\"is_candidate\":false,\"is_blocked\":false,\"is_no_signal\":true,\"candidate\":null,\"blocker\":null,\"metadata\":{\"reason\":\"classic_runtime_disabled\"},\"lane_f_r4r15h_raw_diagnostic_wiring\":true,\"family_runtime_enabled\":false,\"family_runtime_gate_reason\":\"classic_runtime_disabled\",\"family_runtime_family_id\":\"MIST\",\"family_runtime_branch_id\":\"CALL\",\"family_runtime_action\":\"HOLD\",\"family_runtime_activation_mode\":null,\"family_ru
- decision=1780461750336-0 $.activation_bridge_enabled: 1
- decision=1780461750336-0 $.activation_report_only: 1
- decision=1780461750336-0 $.activation_mode: "dry_run"
- decision=1780461750336-0 $.activation_action: "HOLD"
- decision=1780461750336-0 $.activation_observed_action: "HOLD"
- decision=1780461750336-0 $.activation_promoted: 0
- decision=1780461750336-0 $.activation_safe_to_promote: 0
- decision=1780461750336-0 $.activation_reason: "no_candidate"
- decision=1780461750336-0 $.activation_selected_family_id: ""
- decision=1780461750336-0 $.activation_selected_branch_id: ""

## Source grep summary
```text
### hold_only_family_features_consumer_bridge
app/mme_scalpx/services/strategy.py:824:            reason="hold_only_family_features_consumer_bridge",
app/mme_scalpx/services/strategy.py:1625:    - only activates on the existing hold_only_family_features_consumer_bridge path;
app/mme_scalpx/services/strategy.py:1641:    if _r4r20m_reason == "hold_only_family_features_consumer_bridge":
app/mme_scalpx/services/strategy.py:1644:            "family_runtime_gate_reason": "global_gate_hold_only_family_features_consumer_bridge",
app/mme_scalpx/services/strategy.py:1658:                _r4r20m_meta.setdefault("family_runtime_gate_reason", "global_gate_hold_only_family_features_consumer_bridge")
app/mme_scalpx/services/strategy.py:1664:        if "hold_only_family_features_consumer_bridge" not in reason:
bin/proof_batch26o20_r3h_current_frame_corrected_bounded_observation.py:657:                or d.get("reason") in {"no_candidate", "hold_only_family_features_consumer_bridge", "", None}
bin/batch26o2_deep_blocker_analysis.py:477:        "view_data_invalid", "hold_only_family_features_consumer_bridge",
bin/proof_batch26o20_r3g_corrected_r3e_proof_parser.py:493:                or d.get("reason") in {"no_candidate", "hold_only_family_features_consumer_bridge", "", None}
bin/proof_batch26o23_h_narrow_bridge_repair.py:316:    - only activates on the existing hold_only_family_features_consumer_bridge path;
bin/proof_batch26o23_h_narrow_bridge_repair.py:325:        if "hold_only_family_features_consumer_bridge" not in reason:
bin/proof_batch26o23_h_narrow_bridge_repair.py:618:        if "hold_only_family_features_consumer_bridge" in src:
bin/proof_batch26o23_h_narrow_bridge_repair.py:662:            "reason": "No function containing hold_only_family_features_consumer_bridge was found",
bin/proof_batch26o23_h_narrow_bridge_repair.py:742:        "strategy_has_bridge_reason": "hold_only_family_features_consumer_bridge" in strategy_text,
bin/proof_batch26o23_h_narrow_bridge_repair.py:774:        "purpose": "Apply narrow strategy-side consumer-view validity propagation repair on proven hold_only_family_features_consumer_bridge path.",
bin/proof_batch26o23_e_no_candidate_root_cause_review.py:375:        "hold_only_family_features_consumer_bridge",
bin/proof_batch26o23_e_no_candidate_root_cause_review.py:425:        "hold_only_family_features_consumer_bridge",
bin/proof_batch26o23_e_no_candidate_root_cause_review.py:585:    if "hold_only_family_features_consumer_bridge" in json.dumps(dec):
bin/proof_batch26o23_g_narrow_bridge_diagnostic.py:88:    "hold_only_family_features_consumer_bridge",
bin/proof_batch26o23_g_narrow_bridge_diagnostic.py:510:    for term in ["consumer_view", "data_valid", "safe_to_consume", "structural_valid", "activation_candidate_count", "hold_only_family_features_consumer_bridge"]:
bin/proof_batch26o23_g_narrow_bridge_diagnostic.py:538:    source_has_strategy_bridge_reason = "hold_only_family_features_consumer_bridge" in json.dumps(strategy).lower()
bin/proof_batch26o23_i_static_oneshot_bridge_proof.py:313:        "strategy_has_bridge_reason": "hold_only_family_features_consumer_bridge" in strategy_text,
bin/proof_batch26o23_i_static_oneshot_bridge_proof.py:375:            "reason": "hold_only_family_features_consumer_bridge",
bin/proof_batch26o23_i_static_oneshot_bridge_proof.py:376:            "activation_reason": "hold_only_family_features_consumer_bridge",
bin/proof_batch26o23_i_static_oneshot_bridge_proof.py:405:            "reason": "hold_only_family_features_consumer_bridge",
bin/proof_batch26o23_i_static_oneshot_bridge_proof.py:441:            "reason": "hold_only_family_features_consumer_bridge",
bin/proof_batch26o23_i_static_oneshot_bridge_proof.py:459:            "reason": "hold_only_family_features_consumer_bridge",
bin/proof_batch26o23_f_r3_memory_safe_bridge_audit_retry.py:95:    "hold_only_family_features_consumer_bridge",
bin/proof_batch26o23_f_r3_memory_safe_bridge_audit_retry.py:489:        "has_hold_bridge_reason_terms": "hold_only_family_features_consumer_bridge" in flat,
bin/proof_batch26o22_r2_controlled_paper_plan_proof_correction.py:583:            or decision_samples[0].get("reason") in {"no_candidate", "hold_only_family_features_consumer_bridge", "", None}

### activation_candidate_count
app/mme_scalpx/services/strategy.py:953:        activation_candidate_count = (
app/mme_scalpx/services/strategy.py:997:            "activation_candidate_count": activation_candidate_count,
app/mme_scalpx/services/strategy.py:1016:                    "activation_candidate_count": activation_candidate_count,
app/mme_scalpx/services/strategy.py:1566:        return decision.get("activation_candidate_count")
app/mme_scalpx/services/strategy.py:1567:    return getattr(decision, "activation_candidate_count", None)
app/mme_scalpx/services/strategy.py:1713:            updates["activation_candidate_count"] = 0
app/mme_scalpx/services/strategy.py:1886:    candidate_count = int(view.get("activation_candidate_count") or view.get("candidate_count") or 0)
app/mme_scalpx/services/strategy.py:2136:            _r38v_gate_int(_r38v_gate_get(view, "activation_candidate_count", "candidate_count"), 0),
app/mme_scalpx/services/strategy.py:2137:            _r38v_gate_int(_r38v_gate_get(scope, "activation_candidate_count", "candidate_count"), 0),
bin/proof_batch26o20_r3h_current_frame_corrected_bounded_observation.py:397:        "activation_candidate_count": diag.get("activation_candidate_count") if isinstance(diag, dict) else None,
bin/proof_batch26o23_n_corrected_opportunity_parser_deeper_sampler.py:107:    "activation_candidate_count", "promoted", "paper",
bin/proof_strategy_activation_report_redis_smoke.py:430:            "activation_candidate_count": decision.get("activation_candidate_count"),
bin/proof_strategy_activation_report_redis_smoke.py:456:    print("activation_candidate_count =", decision["activation_candidate_count"])
bin/batch26o2_deep_blocker_analysis.py:354:    candidate_count = payloa
```

## Source context file
- `run/audits/B1-PROFIT-LIVE-R39W5_CONSUMER_BRIDGE_EXACT_SEAM_AUDIT_NO_PATCH_NO_START_NO_ORDER_read_only_parse_decision_payload_source_bridge_leaf_invocation_candidate_export_seam_20260603_101233_raw/source_context_extract.txt`

## Next route
- If classification says bridge safe but zero candidates, next step is a tiny patch-plan audit of the exact bridge function, not threshold tuning.
- If source shows leaves are not invoked/exported, patch only that seam.
- If leaves are invoked and return natural no-candidate, continue observe-only capture and improve blocker export only.
- Paper remains blocked.