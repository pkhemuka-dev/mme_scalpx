# LANE-X-R31H_FEATURE_FAMILY_COMMON_KEYS_CONTRACT_SEAM_LOCATOR_NO_PATCH_NO_START_NO_ORDER_20260608_110710
2026-06-08T11:07:10+05:30

LAW=SOURCE_SEAM_LOCATOR_ONLY_NO_PATCH_NO_START_NO_STOP_NO_ORDER_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_RISK_NO_EXECUTION

## Prior R31G proof
R31G=run/proofs/LANE-X-R31G_STRATEGY_BRIDGE_AND_CONTRACT_ERROR_SEAM_AUDIT_NO_PATCH_NO_START_NO_ORDER_20260608_104135.json
{
  "tag": "LANE-X-R31G_STRATEGY_BRIDGE_AND_CONTRACT_ERROR_SEAM_AUDIT_NO_PATCH_NO_START_NO_ORDER_20260608_104135",
  "classification": "PASS_R31G_BRIDGE_OR_CONTRACT_ERROR_SEAM_IDENTIFIED_NO_PATCH_YET",
  "patch_applied": false,
  "started_runtime": false,
  "stopped_runtime": false,
  "broker_order": false,
  "paper_live": false,
  "redis_delete": false,
  "risk_execution_start": false,
  "report": "run/audits/LANE-X-R31G_STRATEGY_BRIDGE_AND_CONTRACT_ERROR_SEAM_AUDIT_NO_PATCH_NO_START_NO_ORDER_20260608_104135_report.md"
}

## Safety before source locator
56286 /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main
orders_stream_len=0
risk_stream_len=0
execution_stream_len=0

## Exact error evidence from latest system errors

## Source grep: contract validators and common-key surfaces
app/mme_scalpx/services/strategy.py:204:        "family_runtime_mode": src.get("family_runtime_mode", "OBSERVE_ONLY"),
app/mme_scalpx/services/strategy.py:244:    common.setdefault("family_runtime_mode", runtime.get("family_runtime_mode", "OBSERVE_ONLY"))
app/mme_scalpx/services/strategy.py:245:    common.setdefault("active_futures_provider_id", runtime.get("futures_marketdata_provider_id"))
app/mme_scalpx/services/strategy.py:246:    common.setdefault("active_selected_option_provider_id", runtime.get("selected_option_marketdata_provider_id"))
app/mme_scalpx/services/strategy.py:247:    common.setdefault("active_option_context_provider_id", runtime.get("option_context_provider_id"))
app/mme_scalpx/services/strategy.py:824:            reason="hold_only_family_features_consumer_bridge",
app/mme_scalpx/services/strategy.py:1625:    - only activates on the existing hold_only_family_features_consumer_bridge path;
app/mme_scalpx/services/strategy.py:1641:    if _r4r20m_reason == "hold_only_family_features_consumer_bridge":
app/mme_scalpx/services/strategy.py:1644:            "family_runtime_gate_reason": "global_gate_hold_only_family_features_consumer_bridge",
app/mme_scalpx/services/strategy.py:1658:                _r4r20m_meta.setdefault("family_runtime_gate_reason", "global_gate_hold_only_family_features_consumer_bridge")
app/mme_scalpx/services/strategy.py:1664:        if "hold_only_family_features_consumer_bridge" not in reason:
app/mme_scalpx/services/features.py:573:def _family_runtime_mode(value: Any) -> str:
app/mme_scalpx/services/features.py:1213:                "active_futures_provider_id",
app/mme_scalpx/services/features.py:1222:                "active_selected_option_provider_id",
app/mme_scalpx/services/features.py:1231:                "active_option_context_provider_id",
app/mme_scalpx/services/features.py:1299:        family_runtime_mode = _family_runtime_mode(raw_map.get("family_runtime_mode"))
app/mme_scalpx/services/features.py:1313:            "family_runtime_mode": family_runtime_mode,
app/mme_scalpx/services/features.py:1322:            "active_futures_provider_id": futures_provider,
app/mme_scalpx/services/features.py:1323:            "active_selected_option_provider_id": selected_option_provider,
app/mme_scalpx/services/features.py:1324:            "active_option_context_provider_id": option_context_provider,
app/mme_scalpx/services/features.py:1357:            provider_id=_safe_str(provider_runtime["active_futures_provider_id"]),
app/mme_scalpx/services/features.py:1367:            provider_id=_safe_str(provider_runtime["active_selected_option_provider_id"]),
app/mme_scalpx/services/features.py:3084:                "active_futures_provider_id",
app/mme_scalpx/services/features.py:3093:                "active_selected_option_provider_id",
app/mme_scalpx/services/features.py:3102:                "active_option_context_provider_id",
app/mme_scalpx/services/features.py:3154:            "family_runtime_mode": _family_runtime_mode(
app/mme_scalpx/services/features.py:3155:                provider_runtime.get("family_runtime_mode")
app/mme_scalpx/services/features.py:3170:            "active_futures_provider_id": futures_provider,
app/mme_scalpx/services/features.py:3171:            "active_selected_option_provider_id": selected_option_provider,
app/mme_scalpx/services/features.py:3172:            "active_option_context_provider_id": option_context_provider,
app/mme_scalpx/services/features.py:3299:                "family_runtime_mode": provider.get("family_runtime_mode"),
app/mme_scalpx/services/features.py:3834:                    "family_runtime_mode": provider_runtime.get("family_runtime_mode"),
app/mme_scalpx/services/features.py:3835:                    "active_futures_provider_id": provider_runtime.get("active_futures_provider_id"),
app/mme_scalpx/services/features.py:3836:                    "active_selected_option_provider_id": provider_runtime.get(
app/mme_scalpx/services/features.py:3837:                        "active_selected_option_provider_id"
app/mme_scalpx/services/features.py:3839:                    "active_option_context_provider_id": provider_runtime.get(
app/mme_scalpx/services/features.py:3840:                        "active_option_context_provider_id"
app/mme_scalpx/services/features.py:4132:            frame.setdefault("family_runtime_mode", provider_runtime.get("family_runtime_mode"))
app/mme_scalpx/services/features.py:4133:            frame.setdefault("active_futures_provider_id", provider_runtime.get("active_futures_provider_id"))
app/mme_scalpx/services/features.py:4135:                "active_selected_option_provider_id",
app/mme_scalpx/services/features.py:4136:                provider_runtime.get("active_selected_option_provider_id"),
app/mme_scalpx/services/features.py:4139:                "active_option_context_provider_id",
app/mme_scalpx/services/features.py:4140:                provider_runtime.get("active_option_context_provider_id"),
app/mme_scalpx/services/features.py:4225:        "reason": "features_consumer_view_mapping_repair_o16",
app/mme_scalpx/services/features.py:4853:        provider_runtime.get("active_futures_provider_id")
app/mme_scalpx/services/features.py:4858:        provider_runtime.get("active_selected_option_provider_id")
app/mme_scalpx/services/features.py:4863:        provider_runtime.get("active_option_context_provider_id")
app/mme_scalpx/services/features.py:5261:    "futures_marketdata_provider_id": "active_futures_provider_id",
app/mme_scalpx/services/features.py:5262:    "selected_option_marketdata_provider_id": "active_selected_option_provider_id",
app/mme_scalpx/services/features.py:5263:    "option_context_provider_id": "active_option_context_provider_id",
app/mme_scalpx/services/features.py:5274:        "active_futures_provider_id",
app/mme_scalpx/services/features.py:5279:        "active_selected_option_provider_id",
app/mme_scalpx/services/features.py:5284:        "active_option_context_provider_id",
app/mme_scalpx/services/features.py:5405:    family_runtime_mode = _batch25h_str_or_none(
app/mme_scalpx/services/features.py:5408:            "family_runtime_mode",
app/mme_scalpx/services/features.py:5424:        "family_runtime_mode": family_runtime_mode,
app/mme_scalpx/services/features.py:5519:    "futures_marketdata_provider_id": "active_futures_provider_id",
app/mme_scalpx/services/features.py:5520:    "selected_option_marketdata_provider_id": "active_selected_option_provider_id",
app/mme_scalpx/services/features.py:5521:    "option_context_provider_id": "active_option_context_provider_id",
app/mme_scalpx/services/features.py:5533:        "active_futures_provider_id",
app/mme_scalpx/services/features.py:5538:        "active_selected_option_provider_id",
app/mme_scalpx/services/features.py:5543:        "active_option_context_provider_id",
app/mme_scalpx/services/features.py:5666:        "family_runtime_mode": (
app/mme_scalpx/services/features.py:5667:            _batch25hc_text_or_none(source.get("family_runtime_mode"))
app/mme_scalpx/services/features.py:7181:        _mapping(family_features.get("provider_runtime", {})).get("active_selected_option_provider_id"),
app/mme_scalpx/services/features.py:7182:        _mapping(family_features.get("provider_runtime", {})).get("active_futures_provider_id"),
app/mme_scalpx/services/features.py:7188:            raw.get("active_selected_option_provider_id"),
app/mme_scalpx/services/features.py:7189:            raw.get("active_futures_provider_id"),
app/mme_scalpx/services/features.py:7196:                parsed.get("active_selected_option_provider_id"),
app/mme_scalpx/services/features.py:7197:                parsed.get("active_futures_provider_id"),
app/mme_scalpx/services/features.py:7580:_BATCH26O17B_COMMON_ABI_KEYS = (
app/mme_scalpx/services/features.py:7739:                "common_keys": list(common_sanitized.keys()),
app/mme_scalpx/services/features.py:7740:                "expected_common_keys": list(_BATCH26O17B_COMMON_ABI_KEYS),
app/mme_scalpx/services/features.py:7741:                "common_key_match": tuple(common_sanitized.keys()) == _BATCH26O17B_COMMON_ABI_KEYS,
app/mme_scalpx/services/features.py:7742:                "selected_option_keys": list(common_sanitized["selected_option"].keys()),
app/mme_scalpx/services/features.py:7744:                "selected_option_key_match": tuple(common_sanitized["selected_option"].keys()) == _BATCH26O17B_SELECTED_OPTION_ABI_KEYS,
app/mme_scalpx/services/features.py:7778:_BATCH26O20R3A_COMMON_KEYS = (
app/mme_scalpx/services/features.py:7912:                            "common_keys": list(_BATCH26O20R3A_COMMON_KEYS),
app/mme_scalpx/services/features.py:8575:        provider.get("active_selected_option_provider_id")
app/mme_scalpx/services/features.py:8664:        provider["family_runtime_mode"] = provider.get("family_runtime_mode") or "OBSERVE_ONLY"
app/mme_scalpx/services/feature_family/common.py:121:def _family_runtime_mode(value: Any) -> str:
app/mme_scalpx/services/feature_family/common.py:153:    active_futures_provider_id: Any,
app/mme_scalpx/services/feature_family/common.py:154:    active_selected_option_provider_id: Any,
app/mme_scalpx/services/feature_family/common.py:165:        _provider_id(active_futures_provider_id)
app/mme_scalpx/services/feature_family/common.py:166:        and _provider_id(active_selected_option_provider_id)
app/mme_scalpx/services/feature_family/common.py:176:    active_futures_provider_id: Any,
app/mme_scalpx/services/feature_family/common.py:177:    active_selected_option_provider_id: Any,
app/mme_scalpx/services/feature_family/common.py:178:    active_option_context_provider_id: Any,
app/mme_scalpx/services/feature_family/common.py:191:        _provider_id(active_futures_provider_id) == N.PROVIDER_DHAN
app/mme_scalpx/services/feature_family/common.py:192:        and _provider_id(active_selected_option_provider_id) == N.PROVIDER_DHAN
app/mme_scalpx/services/feature_family/common.py:193:        and _provider_id(active_option_context_provider_id) == N.PROVIDER_DHAN
app/mme_scalpx/services/feature_family/common.py:301:    active_futures_provider_id: Any = None,
app/mme_scalpx/services/feature_family/common.py:302:    active_selected_option_provider_id: Any = None,
app/mme_scalpx/services/feature_family/common.py:303:    active_option_context_provider_id: Any = None,
app/mme_scalpx/services/feature_family/common.py:309:    family_runtime_mode: Any = None,
app/mme_scalpx/services/feature_family/common.py:317:        "active_futures_provider_id": _provider_id(active_futures_provider_id, None),
app/mme_scalpx/services/feature_family/common.py:318:        "active_selected_option_provider_id": _provider_id(active_selected_option_provider_id, None),
app/mme_scalpx/services/feature_family/common.py:319:        "active_option_context_provider_id": _provider_id(active_option_context_provider_id, None),
app/mme_scalpx/services/feature_family/common.py:323:        "family_runtime_mode": _family_runtime_mode(family_runtime_mode),
app/mme_scalpx/services/feature_family/contracts.py:50:class FeatureFamilyContractError(ValueError):
app/mme_scalpx/services/feature_family/contracts.py:187:    "active_futures_provider_id",
app/mme_scalpx/services/feature_family/contracts.py:188:    "active_selected_option_provider_id",
app/mme_scalpx/services/feature_family/contracts.py:189:    "active_option_context_provider_id",
app/mme_scalpx/services/feature_family/contracts.py:221:COMMON_KEYS: Final[tuple[str, ...]] = (
app/mme_scalpx/services/feature_family/contracts.py:254:COMMON_FUTURES_KEYS: Final[tuple[str, ...]] = (
app/mme_scalpx/services/feature_family/contracts.py:284:COMMON_OPTION_KEYS: Final[tuple[str, ...]] = (
app/mme_scalpx/services/feature_family/contracts.py:303:COMMON_SELECTED_OPTION_KEYS: Final[tuple[str, ...]] = (
app/mme_scalpx/services/feature_family/contracts.py:318:COMMON_CROSS_OPTION_KEYS: Final[tuple[str, ...]] = (
app/mme_scalpx/services/feature_family/contracts.py:324:COMMON_ECONOMICS_KEYS: Final[tuple[str, ...]] = (
app/mme_scalpx/services/feature_family/contracts.py:333:COMMON_SIGNALS_KEYS: Final[tuple[str, ...]] = (
app/mme_scalpx/services/feature_family/contracts.py:599:        "active_futures_provider_id": "futures_marketdata_provider_id",
app/mme_scalpx/services/feature_family/contracts.py:600:        "active_selected_option_provider_id": "selected_option_marketdata_provider_id",
app/mme_scalpx/services/feature_family/contracts.py:601:        "active_option_context_provider_id": "option_context_provider_id",
app/mme_scalpx/services/feature_family/contracts.py:604:        "provider_runtime_mode": "family_runtime_mode",
app/mme_scalpx/services/feature_family/contracts.py:618:            pr.get("family_runtime_mode")
app/mme_scalpx/services/feature_family/contracts.py:639:            and pr.get("active_futures_provider_id")
app/mme_scalpx/services/feature_family/contracts.py:640:            and pr.get("active_selected_option_provider_id")
app/mme_scalpx/services/feature_family/contracts.py:647:            and pr.get("active_option_context_provider_id")
app/mme_scalpx/services/feature_family/contracts.py:651:        "active_futures_provider_id",
app/mme_scalpx/services/feature_family/contracts.py:652:        "active_selected_option_provider_id",
app/mme_scalpx/services/feature_family/contracts.py:653:        "active_option_context_provider_id",
app/mme_scalpx/services/feature_family/contracts.py:678:        raise FeatureFamilyContractError(message)
app/mme_scalpx/services/feature_family/contracts.py:683:        raise FeatureFamilyContractError(f"{field_name} must be bool")
app/mme_scalpx/services/feature_family/contracts.py:689:        raise FeatureFamilyContractError(f"{field_name} must be str")
app/mme_scalpx/services/feature_family/contracts.py:692:        raise FeatureFamilyContractError(f"{field_name} must be non-empty str")
app/mme_scalpx/services/feature_family/contracts.py:698:        raise FeatureFamilyContractError(f"{field_name} must be int")
app/mme_scalpx/services/feature_family/contracts.py:700:        raise FeatureFamilyContractError(
app/mme_scalpx/services/feature_family/contracts.py:708:        raise FeatureFamilyContractError(f"{field_name} must be a mapping")
app/mme_scalpx/services/feature_family/contracts.py:722:        raise FeatureFamilyContractError(
app/mme_scalpx/services/feature_family/contracts.py:736:        raise FeatureFamilyContractError(
app/mme_scalpx/services/feature_family/contracts.py:757:        raise FeatureFamilyContractError(
app/mme_scalpx/services/feature_family/contracts.py:821:        "family_runtime_mode": N.FAMILY_RUNTIME_MODE_OBSERVE_ONLY,
app/mme_scalpx/services/feature_family/contracts.py:830:        "active_futures_provider_id": None,
app/mme_scalpx/services/feature_family/contracts.py:831:        "active_selected_option_provider_id": None,
app/mme_scalpx/services/feature_family/contracts.py:832:        "active_option_context_provider_id": None,
app/mme_scalpx/services/feature_family/contracts.py:1193:        "active_futures_provider_id",
app/mme_scalpx/services/feature_family/contracts.py:1194:        "active_selected_option_provider_id",
app/mme_scalpx/services/feature_family/contracts.py:1195:        "active_option_context_provider_id",
app/mme_scalpx/services/feature_family/contracts.py:1218:            "active_futures_provider_id",
app/mme_scalpx/services/feature_family/contracts.py:1219:            "active_selected_option_provider_id",
app/mme_scalpx/services/feature_family/contracts.py:1255:            provider_runtime["family_runtime_mode"],
app/mme_scalpx/services/feature_family/contracts.py:1256:            field_name="provider_runtime.family_runtime_mode",
app/mme_scalpx/services/feature_family/contracts.py:1261:            provider_runtime["family_runtime_mode"],
app/mme_scalpx/services/feature_family/contracts.py:1262:            field_name="provider_runtime.family_runtime_mode",
app/mme_scalpx/services/feature_family/contracts.py:1302:        ("futures_marketdata_provider_id", "active_futures_provider_id"),
app/mme_scalpx/services/feature_family/contracts.py:1303:        ("selected_option_marketdata_provider_id", "active_selected_option_provider_id"),
app/mme_scalpx/services/feature_family/contracts.py:1304:        ("option_context_provider_id", "active_option_context_provider_id"),
app/mme_scalpx/services/feature_family/contracts.py:1335:    _require_exact_keys(common, required_keys=COMMON_KEYS, field_name="common")
app/mme_scalpx/services/feature_family/contracts.py:1353:        required_keys=COMMON_FUTURES_KEYS,
app/mme_scalpx/services/feature_family/contracts.py:1358:        required_keys=COMMON_OPTION_KEYS,
app/mme_scalpx/services/feature_family/contracts.py:1363:        required_keys=COMMON_OPTION_KEYS,
app/mme_scalpx/services/feature_family/contracts.py:1368:        required_keys=COMMON_SELECTED_OPTION_KEYS,
app/mme_scalpx/services/feature_family/contracts.py:1373:        required_keys=COMMON_CROSS_OPTION_KEYS,
app/mme_scalpx/services/feature_family/contracts.py:1378:        required_keys=COMMON_ECONOMICS_KEYS,
app/mme_scalpx/services/feature_family/contracts.py:1383:        required_keys=COMMON_SIGNALS_KEYS,
app/mme_scalpx/services/feature_family/contracts.py:1801:            raise FeatureFamilyContractError(
app/mme_scalpx/services/feature_family/contracts.py:1827:        raise FeatureFamilyContractError("CANONICAL_FAMILY_SUPPORT_KEYS family coverage drift")
app/mme_scalpx/services/feature_family/contracts.py:1837:        raise FeatureFamilyContractError("CANONICAL_FIELD_COMPATIBILITY_ALIASES drift")
app/mme_scalpx/services/feature_family/contracts.py:1850:    "FeatureFamilyContractError",
app/mme_scalpx/services/feature_family/contracts.py:1889:    "COMMON_KEYS",
app/mme_scalpx/services/feature_family/contracts.py:1891:    "COMMON_FUTURES_KEYS",
app/mme_scalpx/services/feature_family/contracts.py:1892:    "COMMON_OPTION_KEYS",
app/mme_scalpx/services/feature_family/contracts.py:1893:    "COMMON_SELECTED_OPTION_KEYS",
app/mme_scalpx/services/feature_family/contracts.py:1894:    "COMMON_CROSS_OPTION_KEYS",
app/mme_scalpx/services/feature_family/contracts.py:1895:    "COMMON_ECONOMICS_KEYS",
app/mme_scalpx/services/feature_family/contracts.py:1896:    "COMMON_SIGNALS_KEYS",
app/mme_scalpx/services/feature_family/contracts.py:1982:    "futures_marketdata_provider_id": "active_futures_provider_id",
app/mme_scalpx/services/feature_family/contracts.py:1983:    "selected_option_marketdata_provider_id": "active_selected_option_provider_id",
app/mme_scalpx/services/feature_family/contracts.py:1984:    "option_context_provider_id": "active_option_context_provider_id",
app/mme_scalpx/services/feature_family/contracts.py:2001:    if key == "family_runtime_mode":
app/mme_scalpx/services/feature_family/contracts.py:2029:        raise FeatureFamilyContractError(f"{field_name} must be a mapping")
app/mme_scalpx/services/feature_family/contracts.py:2044:        raise FeatureFamilyContractError(f"{field_name} missing provider-runtime keys: {missing!r}")
app/mme_scalpx/services/feature_family/contracts.py:2050:                raise FeatureFamilyContractError(f"{field_name}.{key} must be bool")
app/mme_scalpx/services/feature_family/contracts.py:2054:                raise FeatureFamilyContractError(f"{field_name}.{key} must be int")
app/mme_scalpx/services/feature_family/contracts.py:2057:            raise FeatureFamilyContractError(f"{field_name}.{key} must be str or None")
app/mme_scalpx/services/feature_family/contracts.py:2063:            raise FeatureFamilyContractError(f"{field_name}.{compat} must be str or None")
app/mme_scalpx/services/feature_family/contracts.py:2065:            raise FeatureFamilyContractError(
app/mme_scalpx/services/feature_family/contracts.py:2070:        raise FeatureFamilyContractError(f"{field_name}.provider_runtime_blocked must be bool")
app/mme_scalpx/services/feature_family/contracts.py:2073:        raise FeatureFamilyContractError(f"{field_name}.provider_runtime_block_reason must be str")
app/mme_scalpx/services/feature_family/contracts.py:2077:        raise FeatureFamilyContractError(f"{field_name}.provider_runtime_missing_keys must be tuple/list")
app/mme_scalpx/services/feature_family/contracts.py:2110:    "active_futures_provider_id",
app/mme_scalpx/services/feature_family/contracts.py:2111:    "active_selected_option_provider_id",
app/mme_scalpx/services/feature_family/contracts.py:2112:    "active_option_context_provider_id",
app/mme_scalpx/services/feature_family/contracts.py:2142:    "futures_marketdata_provider_id": "active_futures_provider_id",
app/mme_scalpx/services/feature_family/contracts.py:2143:    "selected_option_marketdata_provider_id": "active_selected_option_provider_id",
app/mme_scalpx/services/feature_family/contracts.py:2144:    "option_context_provider_id": "active_option_context_provider_id",
app/mme_scalpx/services/feature_family/contracts.py:2166:    if key == "family_runtime_mode":
app/mme_scalpx/services/feature_family/contracts.py:2200:        raise FeatureFamilyContractError("provider_runtime must be a mapping")
app/mme_scalpx/services/feature_family/contracts.py:2206:        raise FeatureFamilyContractError(f"provider_runtime missing keys: {missing!r}")
app/mme_scalpx/services/feature_family/contracts.py:2213:                raise FeatureFamilyContractError(f"provider_runtime.{key} must be bool")
app/mme_scalpx/services/feature_family/contracts.py:2218:                raise FeatureFamilyContractError(f"provider_runtime.{key} must be int")
app/mme_scalpx/services/feature_family/contracts.py:2221:        if key == "family_runtime_mode":
app/mme_scalpx/services/feature_family/contracts.py:2223:                raise FeatureFamilyContractError(
app/mme_scalpx/services/feature_family/contracts.py:2230:                raise FeatureFamilyContractError(f"provider_runtime.{key} must be str or None")
app/mme_scalpx/services/feature_family/contracts.py:2234:            raise FeatureFamilyContractError(f"provider_runtime.{key} must be str or None")
app/mme_scalpx/services/feature_family/contracts.py:2241:            raise FeatureFamilyContractError(f"provider_runtime.{compat} must be str or None")
app/mme_scalpx/services/feature_family/contracts.py:2244:            raise FeatureFamilyContractError(
app/mme_scalpx/services/feature_family/contracts.py:2249:        raise FeatureFamilyContractError("provider_runtime.provider_ready_classic must be bool")
app/mme_scalpx/services/feature_family/contracts.py:2252:        raise FeatureFamilyContractError("provider_runtime.provider_ready_miso must be bool")
app/mme_scalpx/services/feature_family/contracts.py:2255:        raise FeatureFamilyContractError("provider_runtime.provider_runtime_blocked must be bool")
app/mme_scalpx/services/feature_family/contracts.py:2258:        raise FeatureFamilyContractError("provider_runtime.provider_runtime_block_reason must be str")
app/mme_scalpx/services/feature_family/contracts.py:2261:        raise FeatureFamilyContractError("provider_runtime.provider_runtime_missing_keys must be tuple/list")
app/mme_scalpx/services/feature_family/contracts.py:2273:                raise FeatureFamilyContractError(f"publishable provider_runtime.{key} is required")
app/mme_scalpx/services/feature_family/contracts.py:2278:        raise FeatureFamilyContractError("family_features payload must be a mapping")
app/mme_scalpx/services/feature_family/contracts.py:2283:        raise FeatureFamilyContractError(
app/mme_scalpx/services/feature_family/contracts.py:2368:        raise FeatureFamilyContractError("Batch26H family_surfaces.families must be a mapping")
app/mme_scalpx/services/feature_family/contracts.py:2372:        raise FeatureFamilyContractError("Batch26H family_surfaces.surfaces_by_branch must be a mapping")
app/mme_scalpx/services/feature_family/contracts.py:2377:            raise FeatureFamilyContractError(f"Batch26H missing family surface: {family_id}")
app/mme_scalpx/services/feature_family/contracts.py:2382:            raise FeatureFamilyContractError(
app/mme_scalpx/services/feature_family/contracts.py:2389:            raise FeatureFamilyContractError(f"Batch26H {family_id}.branches must be a mapping")
app/mme_scalpx/services/feature_family/contracts.py:2395:                raise FeatureFamilyContractError(f"Batch26H missing branch surface: {family_id}.{branch_id}")
app/mme_scalpx/services/feature_family/contracts.py:2399:                raise FeatureFamilyContractError(
app/mme_scalpx/services/feature_family/contracts.py:2407:                raise FeatureFamilyContractError(f"Batch26H missing surfaces_by_branch key: {branch_key}")
app/mme_scalpx/services/feature_family/contracts.py:2411:                raise FeatureFamilyContractError(
app/mme_scalpx/services/strategy_family/eligibility.py:172:    family_runtime_mode: str | None
app/mme_scalpx/services/strategy_family/eligibility.py:181:            "family_runtime_mode": self.family_runtime_mode,
app/mme_scalpx/services/strategy_family/eligibility.py:202:    family_runtime_mode: str | None
app/mme_scalpx/services/strategy_family/eligibility.py:218:            "family_runtime_mode": self.family_runtime_mode,
app/mme_scalpx/services/strategy_family/eligibility.py:342:    family_runtime_mode = _optional_literal(
app/mme_scalpx/services/strategy_family/eligibility.py:343:        provider_runtime.get("family_runtime_mode"),
app/mme_scalpx/services/strategy_family/eligibility.py:344:        field_name="provider_runtime.family_runtime_mode",
app/mme_scalpx/services/strategy_family/eligibility.py:365:        family_runtime_mode=family_runtime_mode,
app/mme_scalpx/services/strategy_family/eligibility.py:569:        family_runtime_mode=_optional_literal(
app/mme_scalpx/services/strategy_family/eligibility.py:570:            provider_runtime.get("family_runtime_mode"),
app/mme_scalpx/services/strategy_family/eligibility.py:571:            field_name="provider_runtime.family_runtime_mode",
app/mme_scalpx/services/strategy_family/eligibility.py:715:        family_runtime_mode=_optional_literal(
app/mme_scalpx/services/strategy_family/eligibility.py:716:            provider_runtime.get("family_runtime_mode"),
app/mme_scalpx/services/strategy_family/eligibility.py:717:            field_name="provider_runtime.family_runtime_mode",
app/mme_scalpx/services/strategy_family/activation.py:907:    required = list(SF_COMMON.CANDIDATE_METADATA_REQUIRED_KEYS)
app/mme_scalpx/services/strategy_family/common.py:670:            provider_runtime.get("active_selected_option_provider_id"),
app/mme_scalpx/services/strategy_family/arbitration.py:85:                "family_runtime_mode": self.candidate.family_runtime_mode,
app/mme_scalpx/services/strategy_family/arbitration.py:137:                    "family_runtime_mode": self.selected.family_runtime_mode,
app/mme_scalpx/services/strategy_family/decisions.py:415:        _clean_optional_str(metadata.get("active_futures_provider_id")),
app/mme_scalpx/services/strategy_family/decisions.py:416:        _clean_optional_str(metadata.get("active_selected_option_provider_id")),
app/mme_scalpx/services/strategy_family/decisions.py:417:        _clean_optional_str(metadata.get("active_option_context_provider_id")),
app/mme_scalpx/services/strategy_family/decisions.py:434:    active_futures_provider_id: str | None = None,
app/mme_scalpx/services/strategy_family/decisions.py:435:    active_selected_option_provider_id: str | None = None,
app/mme_scalpx/services/strategy_family/decisions.py:436:    active_option_context_provider_id: str | None = None,
app/mme_scalpx/services/strategy_family/decisions.py:479:        family_runtime_mode=_clean_optional_str(candidate.family_runtime_mode),
app/mme_scalpx/services/strategy_family/decisions.py:484:        active_futures_provider_id=(
app/mme_scalpx/services/strategy_family/decisions.py:485:            _clean_optional_str(active_futures_provider_id) or cand_fut_pid
app/mme_scalpx/services/strategy_family/decisions.py:487:        active_selected_option_provider_id=(
app/mme_scalpx/services/strategy_family/decisions.py:488:            _clean_optional_str(active_selected_option_provider_id) or cand_opt_pid
app/mme_scalpx/services/strategy_family/decisions.py:490:        active_option_context_provider_id=(
app/mme_scalpx/services/strategy_family/decisions.py:491:            _clean_optional_str(active_option_context_provider_id) or cand_ctx_pid
app/mme_scalpx/services/strategy_family/decisions.py:515:    family_runtime_mode: str | None = None,
app/mme_scalpx/services/strategy_family/decisions.py:524:    active_futures_provider_id: str | None = None,
app/mme_scalpx/services/strategy_family/decisions.py:525:    active_selected_option_provider_id: str | None = None,
app/mme_scalpx/services/strategy_family/decisions.py:526:    active_option_context_provider_id: str | None = None,
app/mme_scalpx/services/strategy_family/decisions.py:567:        family_runtime_mode=_clean_optional_str(family_runtime_mode),
app/mme_scalpx/services/strategy_family/decisions.py:572:        active_futures_provider_id=_clean_optional_str(active_futures_provider_id),
app/mme_scalpx/services/strategy_family/decisions.py:573:        active_selected_option_provider_id=_clean_optional_str(active_selected_option_provider_id),
app/mme_scalpx/services/strategy_family/decisions.py:574:        active_option_context_provider_id=_clean_optional_str(active_option_context_provider_id),
app/mme_scalpx/services/strategy_family/decisions.py:594:    family_runtime_mode: str | None = None,
app/mme_scalpx/services/strategy_family/decisions.py:599:    active_futures_provider_id: str | None = None,
app/mme_scalpx/services/strategy_family/decisions.py:600:    active_selected_option_provider_id: str | None = None,
app/mme_scalpx/services/strategy_family/decisions.py:601:    active_option_context_provider_id: str | None = None,
app/mme_scalpx/services/strategy_family/decisions.py:632:        family_runtime_mode=_clean_optional_str(family_runtime_mode),
app/mme_scalpx/services/strategy_family/decisions.py:637:        active_futures_provider_id=_clean_optional_str(active_futures_provider_id),
app/mme_scalpx/services/strategy_family/decisions.py:638:        active_selected_option_provider_id=_clean_optional_str(active_selected_option_provider_id),

## Focused AST/function locator
[
  {
    "line": 204,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/strategy.py",
    "scope": "FunctionDef:_r38zr_provider_runtime_from_state",
    "text": "\"family_runtime_mode\": src.get(\"family_runtime_mode\", \"OBSERVE_ONLY\"),"
  },
  {
    "line": 244,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/strategy.py",
    "scope": "FunctionDef:_r38zr_backfill_family_features_provider_runtime",
    "text": "common.setdefault(\"family_runtime_mode\", runtime.get(\"family_runtime_mode\", \"OBSERVE_ONLY\"))"
  },
  {
    "line": 245,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/strategy.py",
    "scope": "FunctionDef:_r38zr_backfill_family_features_provider_runtime",
    "text": "common.setdefault(\"active_futures_provider_id\", runtime.get(\"futures_marketdata_provider_id\"))"
  },
  {
    "line": 246,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/strategy.py",
    "scope": "FunctionDef:_r38zr_backfill_family_features_provider_runtime",
    "text": "common.setdefault(\"active_selected_option_provider_id\", runtime.get(\"selected_option_marketdata_provider_id\"))"
  },
  {
    "line": 247,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/strategy.py",
    "scope": "FunctionDef:_r38zr_backfill_family_features_provider_runtime",
    "text": "common.setdefault(\"active_option_context_provider_id\", runtime.get(\"option_context_provider_id\"))"
  },
  {
    "line": 824,
    "matched": [
      "hold_only_family_features_consumer_bridge"
    ],
    "path": "app/mme_scalpx/services/strategy.py",
    "scope": "FunctionDef:build_consumer_view",
    "text": "reason=\"hold_only_family_features_consumer_bridge\","
  },
  {
    "line": 1625,
    "matched": [
      "hold_only_family_features_consumer_bridge"
    ],
    "path": "app/mme_scalpx/services/strategy.py",
    "scope": "FunctionDef:_o23h_repair_hold_bridge_decision",
    "text": "- only activates on the existing hold_only_family_features_consumer_bridge path;"
  },
  {
    "line": 1641,
    "matched": [
      "hold_only_family_features_consumer_bridge"
    ],
    "path": "app/mme_scalpx/services/strategy.py",
    "scope": "FunctionDef:_o23h_repair_hold_bridge_decision",
    "text": "if _r4r20m_reason == \"hold_only_family_features_consumer_bridge\":"
  },
  {
    "line": 1644,
    "matched": [
      "hold_only_family_features_consumer_bridge"
    ],
    "path": "app/mme_scalpx/services/strategy.py",
    "scope": "FunctionDef:_o23h_repair_hold_bridge_decision",
    "text": "\"family_runtime_gate_reason\": \"global_gate_hold_only_family_features_consumer_bridge\","
  },
  {
    "line": 1658,
    "matched": [
      "hold_only_family_features_consumer_bridge"
    ],
    "path": "app/mme_scalpx/services/strategy.py",
    "scope": "FunctionDef:_o23h_repair_hold_bridge_decision",
    "text": "_r4r20m_meta.setdefault(\"family_runtime_gate_reason\", \"global_gate_hold_only_family_features_consumer_bridge\")"
  },
  {
    "line": 1664,
    "matched": [
      "hold_only_family_features_consumer_bridge"
    ],
    "path": "app/mme_scalpx/services/strategy.py",
    "scope": "FunctionDef:_o23h_repair_hold_bridge_decision",
    "text": "if \"hold_only_family_features_consumer_bridge\" not in reason:"
  },
  {
    "line": 573,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_family_runtime_mode",
    "text": "def _family_runtime_mode(value: Any) -> str:"
  },
  {
    "line": 1213,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_provider_runtime",
    "text": "\"active_futures_provider_id\","
  },
  {
    "line": 1222,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_provider_runtime",
    "text": "\"active_selected_option_provider_id\","
  },
  {
    "line": 1231,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_provider_runtime",
    "text": "\"active_option_context_provider_id\","
  },
  {
    "line": 1299,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_provider_runtime",
    "text": "family_runtime_mode = _family_runtime_mode(raw_map.get(\"family_runtime_mode\"))"
  },
  {
    "line": 1313,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_provider_runtime",
    "text": "\"family_runtime_mode\": family_runtime_mode,"
  },
  {
    "line": 1322,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_provider_runtime",
    "text": "\"active_futures_provider_id\": futures_provider,"
  },
  {
    "line": 1323,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_provider_runtime",
    "text": "\"active_selected_option_provider_id\": selected_option_provider,"
  },
  {
    "line": 1324,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_provider_runtime",
    "text": "\"active_option_context_provider_id\": option_context_provider,"
  },
  {
    "line": 1357,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_shared_core",
    "text": "provider_id=_safe_str(provider_runtime[\"active_futures_provider_id\"]),"
  },
  {
    "line": 1367,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_shared_core",
    "text": "provider_id=_safe_str(provider_runtime[\"active_selected_option_provider_id\"]),"
  },
  {
    "line": 3084,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_contract_provider",
    "text": "\"active_futures_provider_id\","
  },
  {
    "line": 3093,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_contract_provider",
    "text": "\"active_selected_option_provider_id\","
  },
  {
    "line": 3102,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_contract_provider",
    "text": "\"active_option_context_provider_id\","
  },
  {
    "line": 3154,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_contract_provider",
    "text": "\"family_runtime_mode\": _family_runtime_mode("
  },
  {
    "line": 3155,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_contract_provider",
    "text": "provider_runtime.get(\"family_runtime_mode\")"
  },
  {
    "line": 3170,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_contract_provider",
    "text": "\"active_futures_provider_id\": futures_provider,"
  },
  {
    "line": 3171,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_contract_provider",
    "text": "\"active_selected_option_provider_id\": selected_option_provider,"
  },
  {
    "line": 3172,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_contract_provider",
    "text": "\"active_option_context_provider_id\": option_context_provider,"
  },
  {
    "line": 3299,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_contract_common",
    "text": "\"family_runtime_mode\": provider.get(\"family_runtime_mode\"),"
  },
  {
    "line": 3834,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_family_frames",
    "text": "\"family_runtime_mode\": provider_runtime.get(\"family_runtime_mode\"),"
  },
  {
    "line": 3835,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_family_frames",
    "text": "\"active_futures_provider_id\": provider_runtime.get(\"active_futures_provider_id\"),"
  },
  {
    "line": 3836,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_family_frames",
    "text": "\"active_selected_option_provider_id\": provider_runtime.get("
  },
  {
    "line": 3837,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_family_frames",
    "text": "\"active_selected_option_provider_id\""
  },
  {
    "line": 3839,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_family_frames",
    "text": "\"active_option_context_provider_id\": provider_runtime.get("
  },
  {
    "line": 3840,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_family_frames",
    "text": "\"active_option_context_provider_id\""
  },
  {
    "line": 4132,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_batch26o16_normalize_family_frames",
    "text": "frame.setdefault(\"family_runtime_mode\", provider_runtime.get(\"family_runtime_mode\"))"
  },
  {
    "line": 4133,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_batch26o16_normalize_family_frames",
    "text": "frame.setdefault(\"active_futures_provider_id\", provider_runtime.get(\"active_futures_provider_id\"))"
  },
  {
    "line": 4135,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_batch26o16_normalize_family_frames",
    "text": "\"active_selected_option_provider_id\","
  },
  {
    "line": 4136,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_batch26o16_normalize_family_frames",
    "text": "provider_runtime.get(\"active_selected_option_provider_id\"),"
  },
  {
    "line": 4139,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_batch26o16_normalize_family_frames",
    "text": "\"active_option_context_provider_id\","
  },
  {
    "line": 4140,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_batch26o16_normalize_family_frames",
    "text": "provider_runtime.get(\"active_option_context_provider_id\"),"
  },
  {
    "line": 4225,
    "matched": [
      "features_consumer_view_mapping_repair_o16"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_batch26o16_build_consumer_view",
    "text": "\"reason\": \"features_consumer_view_mapping_repair_o16\","
  },
  {
    "line": 4853,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_batch26c_miso_provider_ready",
    "text": "provider_runtime.get(\"active_futures_provider_id\")"
  },
  {
    "line": 4858,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_batch26c_miso_provider_ready",
    "text": "provider_runtime.get(\"active_selected_option_provider_id\")"
  },
  {
    "line": 4863,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_batch26c_miso_provider_ready",
    "text": "provider_runtime.get(\"active_option_context_provider_id\")"
  },
  {
    "line": 5261,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "module",
    "text": "\"futures_marketdata_provider_id\": \"active_futures_provider_id\","
  },
  {
    "line": 5262,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "module",
    "text": "\"selected_option_marketdata_provider_id\": \"active_selected_option_provider_id\","
  },
  {
    "line": 5263,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "module",
    "text": "\"option_context_provider_id\": \"active_option_context_provider_id\","
  },
  {
    "line": 5274,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "module",
    "text": "\"active_futures_provider_id\","
  },
  {
    "line": 5279,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "module",
    "text": "\"active_selected_option_provider_id\","
  },
  {
    "line": 5284,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "module",
    "text": "\"active_option_context_provider_id\","
  },
  {
    "line": 5405,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_batch25h_canonical_provider_runtime",
    "text": "family_runtime_mode = _batch25h_str_or_none("
  },
  {
    "line": 5408,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_batch25h_canonical_provider_runtime",
    "text": "\"family_runtime_mode\","
  },
  {
    "line": 5424,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_batch25h_canonical_provider_runtime",
    "text": "\"family_runtime_mode\": family_runtime_mode,"
  },
  {
    "line": 5519,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "module",
    "text": "\"futures_marketdata_provider_id\": \"active_futures_provider_id\","
  },
  {
    "line": 5520,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "module",
    "text": "\"selected_option_marketdata_provider_id\": \"active_selected_option_provider_id\","
  },
  {
    "line": 5521,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "module",
    "text": "\"option_context_provider_id\": \"active_option_context_provider_id\","
  },
  {
    "line": 5533,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "module",
    "text": "\"active_futures_provider_id\","
  },
  {
    "line": 5538,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "module",
    "text": "\"active_selected_option_provider_id\","
  },
  {
    "line": 5543,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "module",
    "text": "\"active_option_context_provider_id\","
  },
  {
    "line": 5666,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_batch25hc_provider_runtime_from_raw",
    "text": "\"family_runtime_mode\": ("
  },
  {
    "line": 5667,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_batch25hc_provider_runtime_from_raw",
    "text": "_batch25hc_text_or_none(source.get(\"family_runtime_mode\"))"
  },
  {
    "line": 7181,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_batch26o16h_r2_provider_from_runtime",
    "text": "_mapping(family_features.get(\"provider_runtime\", {})).get(\"active_selected_option_provider_id\"),"
  },
  {
    "line": 7182,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_batch26o16h_r2_provider_from_runtime",
    "text": "_mapping(family_features.get(\"provider_runtime\", {})).get(\"active_futures_provider_id\"),"
  },
  {
    "line": 7188,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_batch26o16h_r2_provider_from_runtime",
    "text": "raw.get(\"active_selected_option_provider_id\"),"
  },
  {
    "line": 7189,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_batch26o16h_r2_provider_from_runtime",
    "text": "raw.get(\"active_futures_provider_id\"),"
  },
  {
    "line": 7196,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_batch26o16h_r2_provider_from_runtime",
    "text": "parsed.get(\"active_selected_option_provider_id\"),"
  },
  {
    "line": 7197,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_batch26o16h_r2_provider_from_runtime",
    "text": "parsed.get(\"active_futures_provider_id\"),"
  },
  {
    "line": 8575,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_r38zb_classic_failover_ready",
    "text": "provider.get(\"active_selected_option_provider_id\")"
  },
  {
    "line": 8664,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/features.py",
    "scope": "FunctionDef:_r38zb_repair_classic_failover_family_features",
    "text": "provider[\"family_runtime_mode\"] = provider.get(\"family_runtime_mode\") or \"OBSERVE_ONLY\""
  },
  {
    "line": 484,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/feeds.py",
    "scope": "module",
    "text": "# Batch 25V corrective \u2014 normalize family_runtime_mode for ProviderRuntimeConfig"
  },
  {
    "line": 485,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/feeds.py",
    "scope": "FunctionDef:_batch25v_normalize_family_runtime_mode",
    "text": "def _batch25v_normalize_family_runtime_mode(value: object) -> str:"
  },
  {
    "line": 510,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/feeds.py",
    "scope": "FunctionDef:_batch25v_normalize_family_runtime_mode",
    "text": "raise ValueError(f\"unsupported family_runtime_mode: {raw!r}\")"
  },
  {
    "line": 525,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/feeds.py",
    "scope": "FunctionDef:provider_runtime_config",
    "text": "family_runtime_mode=_batch25v_normalize_family_runtime_mode("
  },
  {
    "line": 526,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/feeds.py",
    "scope": "FunctionDef:provider_runtime_config",
    "text": "runtime.get(\"family_runtime_mode\", N.FAMILY_RUNTIME_MODE_OBSERVE_ONLY)"
  },
  {
    "line": 770,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/feeds.py",
    "scope": "ClassDef:FeedState",
    "text": "active_futures_provider_id: str"
  },
  {
    "line": 771,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/feeds.py",
    "scope": "ClassDef:FeedState",
    "text": "active_selected_option_provider_id: str"
  },
  {
    "line": 772,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/feeds.py",
    "scope": "ClassDef:FeedState",
    "text": "active_option_context_provider_id: str"
  },
  {
    "line": 2384,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/feeds.py",
    "scope": "FunctionDef:_publish_state",
    "text": "active_futures_provider_id=active_fut,"
  },
  {
    "line": 2385,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/feeds.py",
    "scope": "FunctionDef:_publish_state",
    "text": "active_selected_option_provider_id=active_opt,"
  },
  {
    "line": 2386,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/feeds.py",
    "scope": "FunctionDef:_publish_state",
    "text": "active_option_context_provider_id=active_ctx,"
  },
  {
    "line": 121,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/feature_family/common.py",
    "scope": "FunctionDef:_family_runtime_mode",
    "text": "def _family_runtime_mode(value: Any) -> str:"
  },
  {
    "line": 153,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/common.py",
    "scope": "FunctionDef:derive_provider_ready_classic",
    "text": "active_futures_provider_id: Any,"
  },
  {
    "line": 154,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/common.py",
    "scope": "FunctionDef:derive_provider_ready_classic",
    "text": "active_selected_option_provider_id: Any,"
  },
  {
    "line": 165,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/common.py",
    "scope": "FunctionDef:derive_provider_ready_classic",
    "text": "_provider_id(active_futures_provider_id)"
  },
  {
    "line": 166,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/common.py",
    "scope": "FunctionDef:derive_provider_ready_classic",
    "text": "and _provider_id(active_selected_option_provider_id)"
  },
  {
    "line": 176,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/common.py",
    "scope": "FunctionDef:derive_provider_ready_miso",
    "text": "active_futures_provider_id: Any,"
  },
  {
    "line": 177,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/common.py",
    "scope": "FunctionDef:derive_provider_ready_miso",
    "text": "active_selected_option_provider_id: Any,"
  },
  {
    "line": 178,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/common.py",
    "scope": "FunctionDef:derive_provider_ready_miso",
    "text": "active_option_context_provider_id: Any,"
  },
  {
    "line": 191,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/common.py",
    "scope": "FunctionDef:derive_provider_ready_miso",
    "text": "_provider_id(active_futures_provider_id) == N.PROVIDER_DHAN"
  },
  {
    "line": 192,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/common.py",
    "scope": "FunctionDef:derive_provider_ready_miso",
    "text": "and _provider_id(active_selected_option_provider_id) == N.PROVIDER_DHAN"
  },
  {
    "line": 193,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/common.py",
    "scope": "FunctionDef:derive_provider_ready_miso",
    "text": "and _provider_id(active_option_context_provider_id) == N.PROVIDER_DHAN"
  },
  {
    "line": 301,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/common.py",
    "scope": "FunctionDef:build_provider_runtime_block",
    "text": "active_futures_provider_id: Any = None,"
  },
  {
    "line": 302,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/common.py",
    "scope": "FunctionDef:build_provider_runtime_block",
    "text": "active_selected_option_provider_id: Any = None,"
  },
  {
    "line": 303,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/common.py",
    "scope": "FunctionDef:build_provider_runtime_block",
    "text": "active_option_context_provider_id: Any = None,"
  },
  {
    "line": 309,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/feature_family/common.py",
    "scope": "FunctionDef:build_provider_runtime_block",
    "text": "family_runtime_mode: Any = None,"
  },
  {
    "line": 317,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/common.py",
    "scope": "FunctionDef:build_provider_runtime_block",
    "text": "\"active_futures_provider_id\": _provider_id(active_futures_provider_id, None),"
  },
  {
    "line": 318,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/common.py",
    "scope": "FunctionDef:build_provider_runtime_block",
    "text": "\"active_selected_option_provider_id\": _provider_id(active_selected_option_provider_id, None),"
  },
  {
    "line": 319,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/common.py",
    "scope": "FunctionDef:build_provider_runtime_block",
    "text": "\"active_option_context_provider_id\": _provider_id(active_option_context_provider_id, None),"
  },
  {
    "line": 323,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/feature_family/common.py",
    "scope": "FunctionDef:build_provider_runtime_block",
    "text": "\"family_runtime_mode\": _family_runtime_mode(family_runtime_mode),"
  },
  {
    "line": 50,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "ClassDef:FeatureFamilyContractError",
    "text": "class FeatureFamilyContractError(ValueError):"
  },
  {
    "line": 187,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "module",
    "text": "\"active_futures_provider_id\","
  },
  {
    "line": 188,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "module",
    "text": "\"active_selected_option_provider_id\","
  },
  {
    "line": 189,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "module",
    "text": "\"active_option_context_provider_id\","
  },
  {
    "line": 599,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:_r39h_provider_runtime_with_compat_aliases",
    "text": "\"active_futures_provider_id\": \"futures_marketdata_provider_id\","
  },
  {
    "line": 600,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:_r39h_provider_runtime_with_compat_aliases",
    "text": "\"active_selected_option_provider_id\": \"selected_option_marketdata_provider_id\","
  },
  {
    "line": 601,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:_r39h_provider_runtime_with_compat_aliases",
    "text": "\"active_option_context_provider_id\": \"option_context_provider_id\","
  },
  {
    "line": 604,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:_r39h_provider_runtime_with_compat_aliases",
    "text": "\"provider_runtime_mode\": \"family_runtime_mode\","
  },
  {
    "line": 618,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:_r39h_provider_runtime_with_compat_aliases",
    "text": "pr.get(\"family_runtime_mode\")"
  },
  {
    "line": 639,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:_r39h_provider_runtime_with_compat_aliases",
    "text": "and pr.get(\"active_futures_provider_id\")"
  },
  {
    "line": 640,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:_r39h_provider_runtime_with_compat_aliases",
    "text": "and pr.get(\"active_selected_option_provider_id\")"
  },
  {
    "line": 647,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:_r39h_provider_runtime_with_compat_aliases",
    "text": "and pr.get(\"active_option_context_provider_id\")"
  },
  {
    "line": 651,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:_r39h_provider_runtime_with_compat_aliases",
    "text": "\"active_futures_provider_id\","
  },
  {
    "line": 652,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:_r39h_provider_runtime_with_compat_aliases",
    "text": "\"active_selected_option_provider_id\","
  },
  {
    "line": 653,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:_r39h_provider_runtime_with_compat_aliases",
    "text": "\"active_option_context_provider_id\","
  },
  {
    "line": 678,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:_require",
    "text": "raise FeatureFamilyContractError(message)"
  },
  {
    "line": 683,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:_require_bool",
    "text": "raise FeatureFamilyContractError(f\"{field_name} must be bool\")"
  },
  {
    "line": 689,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:_require_str",
    "text": "raise FeatureFamilyContractError(f\"{field_name} must be str\")"
  },
  {
    "line": 692,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:_require_str",
    "text": "raise FeatureFamilyContractError(f\"{field_name} must be non-empty str\")"
  },
  {
    "line": 698,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:_require_int",
    "text": "raise FeatureFamilyContractError(f\"{field_name} must be int\")"
  },
  {
    "line": 700,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:_require_int",
    "text": "raise FeatureFamilyContractError("
  },
  {
    "line": 708,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:_require_mapping",
    "text": "raise FeatureFamilyContractError(f\"{field_name} must be a mapping\")"
  },
  {
    "line": 722,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:_require_optional_literal",
    "text": "raise FeatureFamilyContractError("
  },
  {
    "line": 736,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:_require_literal",
    "text": "raise FeatureFamilyContractError("
  },
  {
    "line": 757,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:_require_exact_keys",
    "text": "raise FeatureFamilyContractError("
  },
  {
    "line": 821,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:build_empty_provider_runtime_block",
    "text": "\"family_runtime_mode\": N.FAMILY_RUNTIME_MODE_OBSERVE_ONLY,"
  },
  {
    "line": 830,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:build_empty_provider_runtime_block",
    "text": "\"active_futures_provider_id\": None,"
  },
  {
    "line": 831,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:build_empty_provider_runtime_block",
    "text": "\"active_selected_option_provider_id\": None,"
  },
  {
    "line": 832,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:build_empty_provider_runtime_block",
    "text": "\"active_option_context_provider_id\": None,"
  },
  {
    "line": 1193,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "\"active_futures_provider_id\","
  },
  {
    "line": 1194,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "\"active_selected_option_provider_id\","
  },
  {
    "line": 1195,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "\"active_option_context_provider_id\","
  },
  {
    "line": 1218,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "\"active_futures_provider_id\","
  },
  {
    "line": 1219,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "\"active_selected_option_provider_id\","
  },
  {
    "line": 1255,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "provider_runtime[\"family_runtime_mode\"],"
  },
  {
    "line": 1256,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "field_name=\"provider_runtime.family_runtime_mode\","
  },
  {
    "line": 1261,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "provider_runtime[\"family_runtime_mode\"],"
  },
  {
    "line": 1262,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "field_name=\"provider_runtime.family_runtime_mode\","
  },
  {
    "line": 1302,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "(\"futures_marketdata_provider_id\", \"active_futures_provider_id\"),"
  },
  {
    "line": 1303,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "(\"selected_option_marketdata_provider_id\", \"active_selected_option_provider_id\"),"
  },
  {
    "line": 1304,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "(\"option_context_provider_id\", \"active_option_context_provider_id\"),"
  },
  {
    "line": 1801,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:_require_tuple_match",
    "text": "raise FeatureFamilyContractError("
  },
  {
    "line": 1827,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_contract_field_registry",
    "text": "raise FeatureFamilyContractError(\"CANONICAL_FAMILY_SUPPORT_KEYS family coverage drift\")"
  },
  {
    "line": 1837,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_contract_field_registry",
    "text": "raise FeatureFamilyContractError(\"CANONICAL_FIELD_COMPATIBILITY_ALIASES drift\")"
  },
  {
    "line": 1850,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "module",
    "text": "\"FeatureFamilyContractError\","
  },
  {
    "line": 1982,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "module",
    "text": "\"futures_marketdata_provider_id\": \"active_futures_provider_id\","
  },
  {
    "line": 1983,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "module",
    "text": "\"selected_option_marketdata_provider_id\": \"active_selected_option_provider_id\","
  },
  {
    "line": 1984,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "module",
    "text": "\"option_context_provider_id\": \"active_option_context_provider_id\","
  },
  {
    "line": 2001,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:_batch25h_provider_default",
    "text": "if key == \"family_runtime_mode\":"
  },
  {
    "line": 2029,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "raise FeatureFamilyContractError(f\"{field_name} must be a mapping\")"
  },
  {
    "line": 2044,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "raise FeatureFamilyContractError(f\"{field_name} missing provider-runtime keys: {missing!r}\")"
  },
  {
    "line": 2050,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "raise FeatureFamilyContractError(f\"{field_name}.{key} must be bool\")"
  },
  {
    "line": 2054,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "raise FeatureFamilyContractError(f\"{field_name}.{key} must be int\")"
  },
  {
    "line": 2057,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "raise FeatureFamilyContractError(f\"{field_name}.{key} must be str or None\")"
  },
  {
    "line": 2063,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "raise FeatureFamilyContractError(f\"{field_name}.{compat} must be str or None\")"
  },
  {
    "line": 2065,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "raise FeatureFamilyContractError("
  },
  {
    "line": 2070,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "raise FeatureFamilyContractError(f\"{field_name}.provider_runtime_blocked must be bool\")"
  },
  {
    "line": 2073,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "raise FeatureFamilyContractError(f\"{field_name}.provider_runtime_block_reason must be str\")"
  },
  {
    "line": 2077,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "raise FeatureFamilyContractError(f\"{field_name}.provider_runtime_missing_keys must be tuple/list\")"
  },
  {
    "line": 2110,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "module",
    "text": "\"active_futures_provider_id\","
  },
  {
    "line": 2111,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "module",
    "text": "\"active_selected_option_provider_id\","
  },
  {
    "line": 2112,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "module",
    "text": "\"active_option_context_provider_id\","
  },
  {
    "line": 2142,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "module",
    "text": "\"futures_marketdata_provider_id\": \"active_futures_provider_id\","
  },
  {
    "line": 2143,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "module",
    "text": "\"selected_option_marketdata_provider_id\": \"active_selected_option_provider_id\","
  },
  {
    "line": 2144,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "module",
    "text": "\"option_context_provider_id\": \"active_option_context_provider_id\","
  },
  {
    "line": 2166,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:_batch25hc_default_provider_runtime_value",
    "text": "if key == \"family_runtime_mode\":"
  },
  {
    "line": 2200,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "raise FeatureFamilyContractError(\"provider_runtime must be a mapping\")"
  },
  {
    "line": 2206,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "raise FeatureFamilyContractError(f\"provider_runtime missing keys: {missing!r}\")"
  },
  {
    "line": 2213,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "raise FeatureFamilyContractError(f\"provider_runtime.{key} must be bool\")"
  },
  {
    "line": 2218,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "raise FeatureFamilyContractError(f\"provider_runtime.{key} must be int\")"
  },
  {
    "line": 2221,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "if key == \"family_runtime_mode\":"
  },
  {
    "line": 2223,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "raise FeatureFamilyContractError("
  },
  {
    "line": 2230,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "raise FeatureFamilyContractError(f\"provider_runtime.{key} must be str or None\")"
  },
  {
    "line": 2234,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "raise FeatureFamilyContractError(f\"provider_runtime.{key} must be str or None\")"
  },
  {
    "line": 2241,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "raise FeatureFamilyContractError(f\"provider_runtime.{compat} must be str or None\")"
  },
  {
    "line": 2244,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "raise FeatureFamilyContractError("
  },
  {
    "line": 2249,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "raise FeatureFamilyContractError(\"provider_runtime.provider_ready_classic must be bool\")"
  },
  {
    "line": 2252,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "raise FeatureFamilyContractError(\"provider_runtime.provider_ready_miso must be bool\")"
  },
  {
    "line": 2255,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "raise FeatureFamilyContractError(\"provider_runtime.provider_runtime_blocked must be bool\")"
  },
  {
    "line": 2258,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "raise FeatureFamilyContractError(\"provider_runtime.provider_runtime_block_reason must be str\")"
  },
  {
    "line": 2261,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "raise FeatureFamilyContractError(\"provider_runtime.provider_runtime_missing_keys must be tuple/list\")"
  },
  {
    "line": 2273,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_provider_runtime_block",
    "text": "raise FeatureFamilyContractError(f\"publishable provider_runtime.{key} is required\")"
  },
  {
    "line": 2278,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_family_features_payload",
    "text": "raise FeatureFamilyContractError(\"family_features payload must be a mapping\")"
  },
  {
    "line": 2283,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_family_features_payload",
    "text": "raise FeatureFamilyContractError("
  },
  {
    "line": 2368,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_batch26h_surface_kinds",
    "text": "raise FeatureFamilyContractError(\"Batch26H family_surfaces.families must be a mapping\")"
  },
  {
    "line": 2372,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_batch26h_surface_kinds",
    "text": "raise FeatureFamilyContractError(\"Batch26H family_surfaces.surfaces_by_branch must be a mapping\")"
  },
  {
    "line": 2377,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_batch26h_surface_kinds",
    "text": "raise FeatureFamilyContractError(f\"Batch26H missing family surface: {family_id}\")"
  },
  {
    "line": 2382,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_batch26h_surface_kinds",
    "text": "raise FeatureFamilyContractError("
  },
  {
    "line": 2389,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_batch26h_surface_kinds",
    "text": "raise FeatureFamilyContractError(f\"Batch26H {family_id}.branches must be a mapping\")"
  },
  {
    "line": 2395,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_batch26h_surface_kinds",
    "text": "raise FeatureFamilyContractError(f\"Batch26H missing branch surface: {family_id}.{branch_id}\")"
  },
  {
    "line": 2399,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_batch26h_surface_kinds",
    "text": "raise FeatureFamilyContractError("
  },
  {
    "line": 2407,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_batch26h_surface_kinds",
    "text": "raise FeatureFamilyContractError(f\"Batch26H missing surfaces_by_branch key: {branch_key}\")"
  },
  {
    "line": 2411,
    "matched": [
      "FeatureFamilyContractError"
    ],
    "path": "app/mme_scalpx/services/feature_family/contracts.py",
    "scope": "FunctionDef:validate_batch26h_surface_kinds",
    "text": "raise FeatureFamilyContractError("
  },
  {
    "line": 172,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/strategy_family/eligibility.py",
    "scope": "ClassDef:GlobalGateResult",
    "text": "family_runtime_mode: str | None"
  },
  {
    "line": 181,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/strategy_family/eligibility.py",
    "scope": "FunctionDef:to_dict",
    "text": "\"family_runtime_mode\": self.family_runtime_mode,"
  },
  {
    "line": 202,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/strategy_family/eligibility.py",
    "scope": "ClassDef:BranchEligibilityResult",
    "text": "family_runtime_mode: str | None"
  },
  {
    "line": 218,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/strategy_family/eligibility.py",
    "scope": "FunctionDef:to_dict",
    "text": "\"family_runtime_mode\": self.family_runtime_mode,"
  },
  {
    "line": 342,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/strategy_family/eligibility.py",
    "scope": "FunctionDef:evaluate_global_gates",
    "text": "family_runtime_mode = _optional_literal("
  },
  {
    "line": 343,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/strategy_family/eligibility.py",
    "scope": "FunctionDef:evaluate_global_gates",
    "text": "provider_runtime.get(\"family_runtime_mode\"),"
  },
  {
    "line": 344,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/strategy_family/eligibility.py",
    "scope": "FunctionDef:evaluate_global_gates",
    "text": "field_name=\"provider_runtime.family_runtime_mode\","
  },
  {
    "line": 365,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/strategy_family/eligibility.py",
    "scope": "FunctionDef:evaluate_global_gates",
    "text": "family_runtime_mode=family_runtime_mode,"
  },
  {
    "line": 569,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/strategy_family/eligibility.py",
    "scope": "FunctionDef:evaluate_classic_branch_eligibility",
    "text": "family_runtime_mode=_optional_literal("
  },
  {
    "line": 570,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/strategy_family/eligibility.py",
    "scope": "FunctionDef:evaluate_classic_branch_eligibility",
    "text": "provider_runtime.get(\"family_runtime_mode\"),"
  },
  {
    "line": 571,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/strategy_family/eligibility.py",
    "scope": "FunctionDef:evaluate_classic_branch_eligibility",
    "text": "field_name=\"provider_runtime.family_runtime_mode\","
  },
  {
    "line": 715,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/strategy_family/eligibility.py",
    "scope": "FunctionDef:evaluate_miso_side_eligibility",
    "text": "family_runtime_mode=_optional_literal("
  },
  {
    "line": 716,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/strategy_family/eligibility.py",
    "scope": "FunctionDef:evaluate_miso_side_eligibility",
    "text": "provider_runtime.get(\"family_runtime_mode\"),"
  },
  {
    "line": 717,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/strategy_family/eligibility.py",
    "scope": "FunctionDef:evaluate_miso_side_eligibility",
    "text": "field_name=\"provider_runtime.family_runtime_mode\","
  },
  {
    "line": 670,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/strategy_family/common.py",
    "scope": "FunctionDef:standardize_candidate_metadata",
    "text": "provider_runtime.get(\"active_selected_option_provider_id\"),"
  },
  {
    "line": 85,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/strategy_family/arbitration.py",
    "scope": "FunctionDef:to_dict",
    "text": "\"family_runtime_mode\": self.candidate.family_runtime_mode,"
  },
  {
    "line": 137,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/strategy_family/arbitration.py",
    "scope": "FunctionDef:to_dict",
    "text": "\"family_runtime_mode\": self.selected.family_runtime_mode,"
  },
  {
    "line": 415,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/strategy_family/decisions.py",
    "scope": "FunctionDef:_provider_ids_from_candidate",
    "text": "_clean_optional_str(metadata.get(\"active_futures_provider_id\")),"
  },
  {
    "line": 416,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/strategy_family/decisions.py",
    "scope": "FunctionDef:_provider_ids_from_candidate",
    "text": "_clean_optional_str(metadata.get(\"active_selected_option_provider_id\")),"
  },
  {
    "line": 417,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/strategy_family/decisions.py",
    "scope": "FunctionDef:_provider_ids_from_candidate",
    "text": "_clean_optional_str(metadata.get(\"active_option_context_provider_id\")),"
  },
  {
    "line": 434,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/strategy_family/decisions.py",
    "scope": "FunctionDef:build_entry_decision",
    "text": "active_futures_provider_id: str | None = None,"
  },
  {
    "line": 435,
    "matched": [
      "active_selected_option_provider_id"
    ],
    "path": "app/mme_scalpx/services/strategy_family/decisions.py",
    "scope": "FunctionDef:build_entry_decision",
    "text": "active_selected_option_provider_id: str | None = None,"
  },
  {
    "line": 436,
    "matched": [
      "active_option_context_provider_id"
    ],
    "path": "app/mme_scalpx/services/strategy_family/decisions.py",
    "scope": "FunctionDef:build_entry_decision",
    "text": "active_option_context_provider_id: str | None = None,"
  },
  {
    "line": 479,
    "matched": [
      "family_runtime_mode"
    ],
    "path": "app/mme_scalpx/services/strategy_family/decisions.py",
    "scope": "FunctionDef:build_entry_decision",
    "text": "family_runtime_mode=_clean_optional_str(candidate.family_runtime_mode),"
  },
  {
    "line": 484,
    "matched": [
      "active_futures_provider_id"
    ],
    "path": "app/mme_scalpx/services/strategy_family/decisions.py",
    "scope": "FunctionDef:build_entry_decision",
    "text": "active_futures_provider_id=("
  }
]
LOCATOR_RC=0

## Compile smoke after readonly locator
COMPILE_RC=0

## Safety after source locator
orders_stream_len_after=0
risk_stream_len_after=0
execution_stream_len_after=0

CLASSIFICATION=PASS_R31H_COMMON_KEYS_CONTRACT_SEAM_LOCATED_REVIEW_FOR_THIN_PATCH
