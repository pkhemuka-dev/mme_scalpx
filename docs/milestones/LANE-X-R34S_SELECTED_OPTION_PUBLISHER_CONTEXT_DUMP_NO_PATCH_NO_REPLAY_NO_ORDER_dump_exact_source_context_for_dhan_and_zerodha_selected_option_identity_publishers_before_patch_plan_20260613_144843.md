# LANE-X-R34S_SELECTED_OPTION_PUBLISHER_CONTEXT_DUMP_NO_PATCH_NO_REPLAY_NO_ORDER_dump_exact_source_context_for_dhan_and_zerodha_selected_option_identity_publishers_before_patch_plan_20260613_144843

classification: PASS_R34S_SELECTED_OPTION_PUBLISHER_CONTEXT_DUMP_WRITTEN_NO_PATCH_NO_REPLAY_NO_ORDER
proof: `run/proofs/LANE-X-R34S_SELECTED_OPTION_PUBLISHER_CONTEXT_DUMP_NO_PATCH_NO_REPLAY_NO_ORDER_dump_exact_source_context_for_dhan_and_zerodha_selected_option_identity_publishers_before_patch_plan_20260613_144843.json`
audit: `run/audits/LANE-X-R34S_SELECTED_OPTION_PUBLISHER_CONTEXT_DUMP_NO_PATCH_NO_REPLAY_NO_ORDER_dump_exact_source_context_for_dhan_and_zerodha_selected_option_identity_publishers_before_patch_plan_20260613_144843`

## Safety
- compile_rc: 0
- orders/risk/execution: 0 / 0 / 0
- risk/execution proc: 0 / 0

## Counts
- source_files_with_context: 63
- context_lines: 1115

## Interpretation target
Find whether selected option identity is published from DHAN context, Zerodha selected-option snapshot, or both.
Patch, if any, must be shadow-identity-only and must not enable paper/live/broker/risk/execution.

## Source candidates
=== SOURCE FILE CANDIDATES ===
app/mme_scalpx/core/models.py
app/mme_scalpx/core/names.py
app/mme_scalpx/integrations/dhan_runtime_clients.py
app/mme_scalpx/integrations/provider_runtime.py
app/mme_scalpx/replay/live_adapter.py
app/mme_scalpx/services/feature_family/common.py
app/mme_scalpx/services/feature_family/contracts.py
app/mme_scalpx/services/feature_family/regime.py
app/mme_scalpx/services/feature_family/strike_selection.py
app/mme_scalpx/services/features.py
app/mme_scalpx/services/feeds.py
app/mme_scalpx/services/strategy.py
app/mme_scalpx/services/strategy.py.r34f_r1_backup
app/mme_scalpx/services/strategy.py.r34k_backup
app/mme_scalpx/services/strategy.py.r34m_backup
app/mme_scalpx/services/strategy_family/common.py
app/mme_scalpx/services/strategy_family/decisions.py
app/mme_scalpx/services/strategy_family/doctrine_runtime.py
app/mme_scalpx/services/strategy_family/miso.py
bin/_batch25v_market_observation_common.py
bin/audit_dhan_context_completeness_25v.py
bin/mme_live_observer.py
bin/proof_batch26o16_consumer_view_mapping_repair.py
bin/proof_batch26o16a_consumer_view_proof_correction_runtime_data_valid_audit.py
bin/proof_batch26o16b_runtime_feature_frame_valid_root_cause_audit.py
bin/proof_batch26o16c_exact_feature_input_snapshot_mapping_repair.py
bin/proof_batch26o16d_selected_option_classic_provider_readiness.py
bin/proof_batch26o16e_selected_option_feed_source_o8c_bridge.py
bin/proof_batch26o16h_final_data_valid_composition.py
bin/proof_batch26o16h_r2_persistent_final_composition.py
bin/proof_batch26o1_recovery_singleton_baseline.py
bin/proof_batch26o5_live_key_topology.py
bin/proof_batch26o7_controlled_runtime_start_preflight.py
bin/proof_batch26o9_controlled_paper_preflight.py
bin/proof_contract_field_registry.py
bin/proof_dhan_context_quality.py
bin/proof_dhan_oi_ladder_persistence.py
bin/proof_family_features_offline.py
bin/proof_family_surface_service_path.py
bin/proof_feature_family_shared_builder_abi.py
bin/proof_feature_family_shared_core_guards.py
bin/proof_feeds_features_batch7_freeze.py
bin/proof_market_session_feed_snapshot.py
bin/proof_market_session_provider_runtime.py
bin/proof_misb_doctrine_offline.py
bin/proof_misc_doctrine_offline.py
bin/proof_miso_doctrine_offline.py
bin/proof_miso_provider_doctrine_alignment.py
bin/proof_misr_doctrine_offline.py
bin/proof_mist_doctrine_offline.py
bin/proof_models_batch2_freeze.py
bin/proof_oi_context_surface_audit.py
bin/proof_or_bridge_classic_selected_option_from_zerodha.py
bin/proof_or_publish_provider_runtime_state.py
bin/proof_provider_runtime_contract_seam.py
bin/proof_strategy_activation_report_only.py
bin/proof_strategy_candidate_metadata_contract.py
bin/proof_strategy_family_activation_bridge.py
bin/proof_strategy_family_compat_offline.py
bin/proof_strategy_family_consumer_offline.py
bin/proof_strategy_family_shared_layer_contracts.py
bin/proof_strategy_hold_bridge_offline.py
bin/run_5family_closed_market_dryrun.py

## Context dump head
============================================================
FILE: app/mme_scalpx/core/models.py
227:    names.STRATEGY_RUNTIME_MODE_DISABLED,
232:    names.STRATEGY_RUNTIME_MODE_DISABLED,
1143:    active_selected_option_provider_id: str | None = None
1144:    active_option_context_provider_id: str | None = None
1175:        if self.active_selected_option_provider_id is not None:
1177:                self.active_selected_option_provider_id,
1178:                "active_selected_option_provider_id",
1181:        if self.active_option_context_provider_id is not None:
1183:                self.active_option_context_provider_id,
1184:                "active_option_context_provider_id",
1258:    active_selected_option_provider_id: str | None = None
1259:    active_option_context_provider_id: str | None = None
1307:            "active_selected_option_provider_id",
1308:            "active_option_context_provider_id",
1407:    active_selected_option_provider_id: str | None = None
1408:    active_option_context_provider_id: str | None = None
1442:            "active_selected_option_provider_id",
1443:            "active_option_context_provider_id",
1494:    active_selected_option_provider_id: str | None = None
1495:    active_option_context_provider_id: str | None = None
1555:            "active_selected_option_provider_id",
1556:            "active_option_context_provider_id",
1577:                "provider_id": self.active_selected_option_provider_id,
1592:                "active_selected_option_provider_id": self.active_selected_option_provider_id,
1593:                "active_option_context_provider_id": self.active_option_context_provider_id,
1622:            "active_selected_option_provider_id": self.active_selected_option_provider_id,
1623:            "active_option_context_provider_id": self.active_option_context_provider_id,
2013:class DhanContextEvent(SchemaBase):
2018:    selected_call_instrument_key: str | None = None
2019:    selected_put_instrument_key: str | None = None
2020:    selected_call_option_symbol: str | None = None
2021:    selected_put_option_symbol: str | None = None
2022:    selected_call_option_token: str | None = None
2023:    selected_put_option_token: str | None = None
2024:    selected_call_dhan_security_id: str | None = None
2025:    selected_put_dhan_security_id: str | None = None
2026:    selected_call_zerodha_token: str | None = None
2027:    selected_put_zerodha_token: str | None = None
2080:            "selected_call_instrument_key",
2081:            "selected_put_instrument_key",
2082:            "selected_call_option_symbol",
2083:            "selected_put_option_symbol",
2084:            "selected_call_option_token",
2085:            "selected_put_option_token",
2086:            "selected_call_dhan_security_id",
2087:            "selected_put_dhan_security_id",
2088:            "selected_call_zerodha_token",
2089:            "selected_put_zerodha_token",
2155:class DhanContextState(SchemaBase):
2160:    selected_call_instrument_key: str | None = None
2161:    selected_put_instrument_key: str | None = None
2162:    selected_call_option_symbol: str | None = None
2163:    selected_put_option_symbol: str | None = None
2164:    selected_call_option_token: str | None = None
2165:    selected_put_option_token: str | None = None
2166:    selected_call_dhan_security_id: str | None = None
2167:    selected_put_dhan_security_id: str | None = None
2168:    selected_call_zerodha_token: str | None = None
2169:    selected_put_zerodha_token: str | None = None
2237:            "selected_call_instrument_key",
2238:            "selected_put_instrument_key",
2239:            "selected_call_option_symbol",
2240:            "selected_put_option_symbol",
2241:            "selected_call_option_token",
2242:            "selected_put_option_token",
2243:            "selected_call_dhan_security_id",
2244:            "selected_put_dhan_security_id",
2245:            "selected_call_zerodha_token",
2246:            "selected_put_zerodha_token",
2366:    selected_option_marketdata_provider_id: str
2367:    option_context_provider_id: str
2371:    selected_option_marketdata_status: str = names.PROVIDER_STATUS_HEALTHY
2372:    option_context_status: str = names.PROVIDER_STATUS_HEALTHY
2391:            "selected_option_marketdata_provider_id",
2392:            "option_context_provider_id",
2399:            "selected_option_marketdata_status",
2400:            "option_context_status",
2758:    active_selected_option_provider_id: str | None = None
2759:    active_option_context_provider_id: str | None = None
2794:            "active_selected_option_provider_id",
============================================================
FILE: app/mme_scalpx/core/names.py
339:PROVIDER_STATUS_UNAVAILABLE: Final[str] = "UNAVAILABLE"
340:PROVIDER_STATUS_DISABLED: Final[str] = "DISABLED"
341:PROVIDER_STATUS_FAILOVER_ACTIVE: Final[str] = "FAILOVER_ACTIVE"
348:    PROVIDER_STATUS_UNAVAILABLE,
349:    PROVIDER_STATUS_DISABLED,
350:    PROVIDER_STATUS_FAILOVER_ACTIVE,
399:STRATEGY_RUNTIME_MODE_DISABLED: Final[str] = "DISABLED"
406:    STRATEGY_RUNTIME_MODE_DISABLED,
428:    "selected_option_marketdata_provider_id",
429:    "option_context_provider_id",
433:    "selected_option_marketdata_status",
434:    "option_context_status",
458:    "selected_call_instrument_key",
459:    "selected_put_instrument_key",
586:        "active_selected_option_provider_id": "selected_option_marketdata_provider_id",
587:        "active_option_context_provider_id": "option_context_provider_id",
591:        "selected_option_provider_status": "selected_option_marketdata_status",
592:        "option_context_provider_status": "option_context_status",
708:STREAM_TICKS_MME_OPT_SELECTED_ZERODHA: Final[str] = "ticks:mme:opt:selected:zerodha:stream"
716:    STREAM_TICKS_MME_OPT_SELECTED_ZERODHA,
740:    STREAM_TICKS_MME_OPT_SELECTED_ZERODHA
813:HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA: Final[str] = (
822:HASH_STATE_DHAN_CONTEXT: Final[str] = "state:context:mme:dhan"
829:    HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA,
832:    HASH_STATE_DHAN_CONTEXT,
868:    HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA
876:HASH_REPLAY_STATE_DHAN_CONTEXT: Final[str] = replay_name(HASH_STATE_DHAN_CONTEXT)
1306:STATE_DISABLED: Final[str] = "DISABLED"
1320:    STATE_DISABLED,
1331:CONTROL_MODE_DISABLED: Final[str] = "DISABLED"
1337:    CONTROL_MODE_DISABLED,
1390:STATE_SNAPSHOT_OPT_SELECTED_ZERODHA: Final[str] = HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA
1393:STATE_DHAN_CONTEXT: Final[str] = HASH_STATE_DHAN_CONTEXT
1441:        "STATE_SNAPSHOT_OPT_SELECTED_ZERODHA": CompatibilityAliasDef("STATE_SNAPSHOT_OPT_SELECTED_ZERODHA", "HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA", ALIAS_STATUS_TEMPORARY_MIGRATION, False),
1444:        "STATE_DHAN_CONTEXT": CompatibilityAliasDef("STATE_DHAN_CONTEXT", "HASH_STATE_DHAN_CONTEXT", ALIAS_STATUS_TEMPORARY_MIGRATION, False),
1529:        STREAM_TICKS_MME_OPT_SELECTED_ZERODHA: SERVICE_FEEDS,
1556:        HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA: SERVICE_FEEDS,
1559:        HASH_STATE_DHAN_CONTEXT: SERVICE_FEEDS,
1927:    ticks_mme_opt_selected_zerodha=STREAM_TICKS_MME_OPT_SELECTED_ZERODHA,
1946:    snapshot_mme_opt_selected_zerodha=HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA,
1949:    dhan_context=HASH_STATE_DHAN_CONTEXT,
============================================================
FILE: app/mme_scalpx/integrations/dhan_runtime_clients.py
1206:        return "UNAVAILABLE"
1277:        HASH_STATE_DHAN_CONTEXT fresh but empty:
1336:            "selected_call_instrument_key": selected_call_key or selected_call_context.get("instrument_key", ""),
1337:            "selected_put_instrument_key": selected_put_key or selected_put_context.get("instrument_key", ""),
============================================================
FILE: app/mme_scalpx/integrations/provider_runtime.py
175:        names.PROVIDER_STATUS_FAILOVER_ACTIVE,
232:        return runtime_state.selected_option_marketdata_provider_id
234:        return runtime_state.option_context_provider_id
249:        return runtime_state.selected_option_marketdata_status
251:        return runtime_state.option_context_status
266:        names.PROVIDER_STATUS_UNAVAILABLE,
267:        names.PROVIDER_STATUS_DISABLED,
278:    dhan_context_state: models.DhanContextState | None,
285:    For option_context + DHAN, a concrete DhanContextState is mandatory.
286:    Without it, the context lane is UNAVAILABLE even if generic Dhan
292:            return names.PROVIDER_STATUS_UNAVAILABLE
302:        if base_status == names.PROVIDER_STATUS_DISABLED:
303:            return names.PROVIDER_STATUS_DISABLED
311:            names.PROVIDER_STATUS_UNAVAILABLE,
312:            names.PROVIDER_STATUS_DISABLED,
323:        return names.PROVIDER_STATUS_UNAVAILABLE
327:    if base_status == names.PROVIDER_STATUS_DISABLED:
328:        return names.PROVIDER_STATUS_DISABLED
342:            names.PROVIDER_STATUS_FAILOVER_ACTIVE,
353:            names.PROVIDER_STATUS_FAILOVER_ACTIVE,
469:    dhan_context_state: models.DhanContextState | None = None
487:            models.DhanContextState,
490:                f"dhan_context_state must be DhanContextState, got {type(self.dhan_context_state).__name__}"
567:        dhan_context_state: models.DhanContextState | None = None,
715:        elif status == names.PROVIDER_STATUS_FAILOVER_ACTIVE:
910:        execution_fallback_status = names.PROVIDER_STATUS_DISABLED
1001:        selected_option_marketdata_provider_id=selected_option_choice.provider_id,
1002:        option_context_provider_id=option_context_choice.provider_id,
1006:            names.PROVIDER_STATUS_FAILOVER_ACTIVE
1010:        selected_option_marketdata_status=(
1011:            names.PROVIDER_STATUS_FAILOVER_ACTIVE
1015:        option_context_status=option_context_choice.status,
1017:            names.PROVIDER_STATUS_FAILOVER_ACTIVE
1058:    dhan_context_state: models.DhanContextState | None = None,
============================================================
FILE: app/mme_scalpx/replay/live_adapter.py
19:    "dhan_context": "HASH_STATE_DHAN_CONTEXT_REPLAY",
============================================================
FILE: app/mme_scalpx/services/feature_family/common.py
117:    fallback = default or getattr(N, "PROVIDER_STATUS_UNAVAILABLE", "UNAVAILABLE")
130:        return getattr(N, "STRATEGY_RUNTIME_MODE_DISABLED", "DISABLED")
133:        text = getattr(N, "STRATEGY_RUNTIME_MODE_DISABLED", "DISABLED")
139:        return getattr(N, "STRATEGY_RUNTIME_MODE_DISABLED", "DISABLED")
142:        text = getattr(N, "STRATEGY_RUNTIME_MODE_DISABLED", "DISABLED")
151:def derive_provider_ready_classic(
154:    active_selected_option_provider_id: Any,
162:        getattr(N, "PROVIDER_STATUS_FAILOVER_ACTIVE", "FAILOVER_ACTIVE"),
166:        and _provider_id(active_selected_option_provider_id)
168:        != getattr(N, "STRATEGY_RUNTIME_MODE_DISABLED", "DISABLED")
174:def derive_provider_ready_miso(
177:    active_selected_option_provider_id: Any,
178:    active_option_context_provider_id: Any,
188:        getattr(N, "PROVIDER_STATUS_FAILOVER_ACTIVE", "FAILOVER_ACTIVE"),
192:        and _provider_id(active_selected_option_provider_id) == N.PROVIDER_DHAN
193:        and _provider_id(active_option_context_provider_id) == N.PROVIDER_DHAN
195:        != getattr(N, "STRATEGY_RUNTIME_MODE_DISABLED", "DISABLED")
302:    active_selected_option_provider_id: Any = None,
303:    active_option_context_provider_id: Any = None,
318:        "active_selected_option_provider_id": _provider_id(active_selected_option_provider_id, None),
319:        "active_option_context_provider_id": _provider_id(active_option_context_provider_id, None),
524:    provider_ready_classic: bool = False,
525:    provider_ready_miso: bool = False,
541:        "provider_ready_classic": bool(provider_ready_classic),
542:        "provider_ready_miso": bool(provider_ready_miso),
854:    "derive_provider_ready_classic",
855:    "derive_provider_ready_miso",
============================================================
FILE: app/mme_scalpx/services/feature_family/contracts.py
113:    N.STRATEGY_RUNTIME_MODE_DISABLED,
119:    N.STRATEGY_RUNTIME_MODE_DISABLED,
188:    "active_selected_option_provider_id",
189:    "active_option_context_provider_id",
243:    "provider_ready_classic",
244:    "provider_ready_miso",
600:        "active_selected_option_provider_id": "selected_option_marketdata_provider_id",
601:        "active_option_context_provider_id": "option_context_provider_id",
606:        "selected_option_provider_status": "selected_option_marketdata_status",
607:        "option_context_provider_status": "option_context_status",
630:            "FAILOVER_ACTIVE",
635:    if "provider_ready_classic" not in pr:
636:        pr["provider_ready_classic"] = bool(
640:            and pr.get("active_selected_option_provider_id")
643:    if "provider_ready_miso" not in pr:
644:        pr["provider_ready_miso"] = bool(
645:            bool(pr.get("provider_ready_classic"))
647:            and pr.get("active_option_context_provider_id")
652:        "active_selected_option_provider_id",
653:        "active_option_context_provider_id",
662:        "provider_ready_classic",
663:        "provider_ready_miso",
791:        "validity": "UNAVAILABLE",
812:        "selected_option_marketdata_provider_id": None,
813:        "option_context_provider_id": None,
817:        "selected_option_marketdata_status": None,
818:        "option_context_status": None,
831:        "active_selected_option_provider_id": None,
832:        "active_option_context_provider_id": None,
982:        "provider_ready_classic": False,
983:        "provider_ready_miso": False,
1187:        "selected_option_marketdata_provider_id",
1188:        "option_context_provider_id",
1194:        "active_selected_option_provider_id",
1195:        "active_option_context_provider_id",
1201:        "selected_option_marketdata_status",
1202:        "option_context_status",
1217:            "selected_option_marketdata_provider_id",
1219:            "active_selected_option_provider_id",
1237:            "selected_option_marketdata_status",
1303:        ("selected_option_marketdata_provider_id", "active_selected_option_provider_id"),
1304:        ("option_context_provider_id", "active_option_context_provider_id"),
1308:        ("selected_option_marketdata_status", "selected_option_provider_status"),
1309:        ("option_context_status", "option_context_provider_status"),
1723:    carry snapshot.valid=False, UNAVAILABLE provider statuses, and all entry
1983:    "selected_option_marketdata_provider_id": "active_selected_option_provider_id",
1984:    "option_context_provider_id": "active_option_context_provider_id",
1988:    "selected_option_marketdata_status": "selected_option_provider_status",
1989:    "option_context_status": "option_context_provider_status",
2000:        return getattr(N, "PROVIDER_STATUS_UNAVAILABLE", "UNAVAILABLE")
2111:    "active_selected_option_provider_id",
2112:    "active_option_context_provider_id",
2124:    "provider_ready_classic",
2125:    "provider_ready_miso",
2143:    "selected_option_marketdata_provider_id": "active_selected_option_provider_id",
2144:    "option_context_provider_id": "active_option_context_provider_id",
2148:    "selected_option_marketdata_status": "selected_option_provider_status",
2149:    "option_context_status": "option_context_provider_status",
2156:    return getattr(N, "PROVIDER_STATUS_UNAVAILABLE", "UNAVAILABLE")
