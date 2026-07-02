# LANE-X-R34L-R1_TARGETED_STRATEGY_IDENTITY_CONTEXT_NO_PATCH_NO_REPLAY_NO_ORDER_dump_exact_strategy_view_activation_and_identity_context_before_symbol_token_source_patch_20260613_134724

classification: PASS_R34L_R1_TARGETED_CONTEXT_CAPTURED_NO_PATCH_NO_REPLAY_NO_ORDER
proof: `run/proofs/LANE-X-R34L-R1_TARGETED_STRATEGY_IDENTITY_CONTEXT_NO_PATCH_NO_REPLAY_NO_ORDER_dump_exact_strategy_view_activation_and_identity_context_before_symbol_token_source_patch_20260613_134724.json`
audit_dir: `run/audits/LANE-X-R34L-R1_TARGETED_STRATEGY_IDENTITY_CONTEXT_NO_PATCH_NO_REPLAY_NO_ORDER_dump_exact_strategy_view_activation_and_identity_context_before_symbol_token_source_patch_20260613_134724`

## Safety
- orders/risk/execution: 0 / 0 / 0
- risk/execution proc: 0 / 0

## Identity path grep
# activation_selected identity grep exact
app/mme_scalpx/services/strategy.py:488:        "selected_option_symbol", "selected_option_tradingsymbol",
app/mme_scalpx/services/strategy.py:489:        "selected_option_trading_symbol", "instrument_key",
app/mme_scalpx/services/strategy.py:490:        "selected_option_instrument_key",
app/mme_scalpx/services/strategy.py:494:        "selected_option_token", "selected_option_instrument_token",
app/mme_scalpx/services/strategy.py:497:    candidate_symbol_shadow = _safe_str(
app/mme_scalpx/services/strategy.py:498:        _r34k_walk(selected_map, symbol_keys) or _r34k_walk(view, symbol_keys)
app/mme_scalpx/services/strategy.py:500:    candidate_instrument_token_shadow = _safe_str(
app/mme_scalpx/services/strategy.py:520:        "candidate_symbol_shadow": candidate_symbol_shadow if is_enter else "",
app/mme_scalpx/services/strategy.py:521:        "candidate_instrument_token_shadow": candidate_instrument_token_shadow if is_enter else "",
app/mme_scalpx/services/strategy.py:522:        "symbol": candidate_symbol_shadow if is_enter else "",
app/mme_scalpx/services/strategy.py:523:        "instrument_token": candidate_instrument_token_shadow if is_enter else "",
app/mme_scalpx/services/strategy.py:1100:            "instrument_key": _safe_str(selected_option.get("instrument_key")),
app/mme_scalpx/services/strategy.py:1101:            "instrument_token": _safe_str(selected_option.get("instrument_token")),
app/mme_scalpx/services/strategy.py:1102:            "option_symbol": _safe_str(selected_option.get("option_symbol")),
app/mme_scalpx/services/strategy.py.r34k_backup:1037:            "instrument_key": _safe_str(selected_option.get("instrument_key")),
app/mme_scalpx/services/strategy.py.r34k_backup:1038:            "instrument_token": _safe_str(selected_option.get("instrument_token")),
app/mme_scalpx/services/strategy.py.r34k_backup:1039:            "option_symbol": _safe_str(selected_option.get("option_symbol")),
app/mme_scalpx/services/features.py:2290:                    _safe_bool(selected.get("present"), False) or selected.get("instrument_key")
app/mme_scalpx/services/features.py:2343:                    selected.get("present") or selected.get("instrument_key")
app/mme_scalpx/services/features.py:4589:            "selected_call_instrument_key",
app/mme_scalpx/services/features.py:4590:            "selected_call_option_symbol",
app/mme_scalpx/services/features.py:4599:            "selected_put_instrument_key",
app/mme_scalpx/services/features.py:4600:            "selected_put_option_symbol",
app/mme_scalpx/services/features.py:5582:    for candidate in keys:
app/mme_scalpx/services/features.py:6342:    candidate_keys: set[str] = set()
app/mme_scalpx/services/features.py:6345:            candidate_keys.add(canonical_key)
app/mme_scalpx/services/features.py:6346:            candidate_keys.update(str(alias) for alias in aliases)
app/mme_scalpx/services/features.py:6349:        candidate_keys.add(canonical_key)
app/mme_scalpx/services/features.py:6350:        candidate_keys.update(str(alias) for alias in aliases)
app/mme_scalpx/services/features.py:6356:        candidate_keys.discard("active_zone_valid")
app/mme_scalpx/services/features.py:6357:        candidate_keys.discard("zone_valid")
app/mme_scalpx/services/features.py:6358:        candidate_keys.discard("active_zone_ready")
app/mme_scalpx/services/features.py:6360:    return any(_safe_bool(rich_map.get(key), False) for key in candidate_keys if key in rich_map)
app/mme_scalpx/services/features.py:6982:        selected_present = bool(selected.get("present") or selected.get("instrument_key") or selected.get("ltp"))
app/mme_scalpx/services/feature_family/miso_surface.py:1169:                    "selected_option_symbol",
app/mme_scalpx/services/feature_family/miso_surface.py:1173:                    "selected_symbol",
app/mme_scalpx/services/feature_family/regime.py:607:        _safe_str(_pick(ctx, "selected_call_instrument_key", "call_instrument_key", "ce_instrument_key"))
app/mme_scalpx/services/feature_family/regime.py:615:        _safe_str(_pick(ctx, "selected_put_instrument_key", "put_instrument_key", "pe_instrument_key"))
app/mme_scalpx/services/feature_family/miso_microstructure.py:507:        or _safe_str(_pick(selected_strike, "instrument_key", "security_id", "token", "option_symbol"))
app/mme_scalpx/services/feature_family/option_core.py:92:    "selected_instrument_key",
app/mme_scalpx/services/feature_family/option_core.py:889:            selected_strike_surface.get("selected", {}).get("instrument_key")
app/mme_scalpx/services/feature_family/option_core.py:892:            selected_strike_surface.get("selected_instrument_key"),
app/mme_scalpx/services/feature_family/option_core.py:985:            selected_strike_surface.get("selected", {}).get("instrument_key")
app/mme_scalpx/services/feature_family/option_core.py:988:            selected_strike_surface.get("selected_instrument_key"),
app/mme_scalpx/services/strategy_family/cooldowns.py:613:        bucket, key_candidates, scope, policy, session_reset_required = _bucket_and_keys_for_reason(
app/mme_scalpx/services/strategy_family/cooldowns.py:631:    value, key = _lookup(params, *key_candidates) if key_candidates else (None, None)
app/mme_scalpx/services/strategy_family/activation.py:779:            value = candidate.get(key)
app/mme_scalpx/services/strategy_family/common.py:628:        _metadata_value(candidate_data.get("instrument_key"), existing.get("instrument_key"))
app/mme_scalpx/services/strategy_family/common.py:631:        _metadata_value(candidate_data.get("option_symbol"), existing.get("option_symbol"))
app/mme_scalpx/services/strategy_family/common.py:635:            candidate_data.get("instrument_token"),
app/mme_scalpx/services/strategy_family/common.py:636:            candidate_data.get("option_token"),
app/mme_scalpx/services/strategy_family/arbitration.py:83:                "instrument_key": self.candidate.instrument_key,
app/mme_scalpx/services/strategy_family/arbitration.py:135:                    "instrument_key": self.selected.instrument_key,
app/mme_scalpx/services/strategy_family/arbitration.py:251:            return _strict_float(meta[key], f"candidate.metadata[{key!r}]")
app/mme_scalpx/services/strategy_family/arbitration.py:259:            return _strict_float(meta[key], f"candidate.metadata[{key!r}]")
app/mme_scalpx/services/strategy_family/arbitration.py:273:        instrument_key=_non_empty_str(candidate.instrument_key, "candidate.instrument_key"),
app/mme_scalpx/services/strategy_family/arbitration.py:321:    _non_empty_str(candidate.instrument_key, "candidate.instrument_key")
app/mme_scalpx/services/strategy_family/decisions.py:441:    _require(bool(candidate.instrument_key), "entry candidate requires instrument_key")
app/mme_scalpx/services/strategy_family/decisions.py:475:        instrument_key=_require_non_empty_str(candidate.instrument_key, "candidate.instrument_key"),
app/mme_scalpx/services/strategy_family/internal_order_intent_pipeline.py:81:    # Generic internal candidate-intent input: positive score + family + symbol/side.
app/mme_scalpx/services/strategy_family/internal_order_intent_pipeline.py:120:    symbol = str(candidate.get("symbol") or candidate.get("trading_symbol") or candidate.get("option_symbol") or "")
app/mme_scalpx/services/strategy_family/internal_order_intent_pipeline.py:161:    symbol = str(candidate_intent.get("symbol") or "")
app/mme_scalpx/services/strategy_family/miv_r_contract.py:179:            hard_errors.append("trade_candidate_symbol_missing")
app/mme_scalpx/services/strategy_family/doctrine_runtime.py:370:                _pick(data, "instrument_key", "selected_instrument_key")
app/mme_scalpx/services/strategy_family/order_intent.py:119:def _pick(candidate: Mapping[str, Any], metadata: Mapping[str, Any], *keys: str) -> Any:
app/mme_scalpx/services/strategy_family/order_intent.py:121:        value = candidate.get(key)
app/mme_scalpx/services/strategy_family/order_intent.py:219:        "option_symbol": _safe_str(_pick(candidate, metadata, "option_symbol", "trading_symbol", "symbol")),
app/mme_scalpx/services/strategy_family/order_intent.py:220:        "option_token": _safe_str(_pick(candidate, metadata, "option_token", "instrument_token", "token")),
app/mme_scalpx/services/strategy_family/order_intent.py:239:        "instrument_key": _safe_str(_pick(candidate, metadata, "instrument_key")),
app/mme_scalpx/services/strategy_family/miso.py:1645:                    "selected_option_symbol",
app/mme_scalpx/services/strategy_family/miso.py:1649:                    "selected_symbol",
app/mme_scalpx/services/strategy_legacy_single.py:540:            option_symbol=candidate.option_symbol,
app/mme_scalpx/services/strategy_legacy_single.py:541:            option_token=candidate.option_token,
app/mme_scalpx/services/strategy.py.r34f_r1_backup:998:            "instrument_key": _safe_str(selected_option.get("instrument_key")),
app/mme_scalpx/services/strategy.py.r34f_r1_backup:999:            "instrument_token": _safe_str(selected_option.get("instrument_token")),
app/mme_scalpx/services/strategy.py.r34f_r1_backup:1000:            "option_symbol": _safe_str(selected_option.get("option_symbol")),
app/mme_scalpx/services/feeds.py:1093:            selected_call_instrument_key=_safe_str(_first_value(payload, "selected_call_instrument_key", "call_instrument_key") or ladder_context["selected_call_context"].get("instrument_key")) or None,
app/mme_scalpx/services/feeds.py:1094:            selected_put_instrument_key=_safe_str(_first_value(payload, "selected_put_instrument_key", "put_instrument_key") or ladder_context["selected_put_context"].get("instrument_key")) or None,
app/mme_scalpx/services/feeds.py:1136:            selected_call_option_symbol=_safe_str(ladder_context["selected_call_context"].get("trading_symbol")) or None,
app/mme_scalpx/services/feeds.py:1137:            selected_put_option_symbol=_safe_str(ladder_context["selected_put_context"].get("trading_symbol")) or None,
app/mme_scalpx/services/feeds.py:1138:            selected_call_option_token=_safe_str(ladder_context["selected_call_context"].get("instrument_token")) or None,
app/mme_scalpx/services/feeds.py:1139:            selected_put_option_token=_safe_str(ladder_context["selected_put_context"].get("instrument_token")) or None,
app/mme_scalpx/services/feeds.py:1147:            selected_call_instrument_key=event.selected_call_instrument_key,
app/mme_scalpx/services/feeds.py:1148:            selected_put_instrument_key=event.selected_put_instrument_key,
app/mme_scalpx/services/feeds.py:1272:        selected_call_key = _safe_str(_first_value(payload, "selected_call_instrument_key", "call_instrument_key"))
app/mme_scalpx/services/feeds.py:1273:        selected_put_key = _safe_str(_first_value(payload, "selected_put_instrument_key", "put_instrument_key"))
app/mme_scalpx/services/feeds.py:2169:            payload["selected_call_instrument_key"] = dhan_context_state.selected_call_instrument_key or ""
app/mme_scalpx/services/feeds.py:2170:            payload["selected_put_instrument_key"] = dhan_context_state.selected_put_instrument_key or ""
app/mme_scalpx/services/feeds.py:2174:            payload["selected_call_json"] = _json_dumps(self._selected_option_member(frame, dhan_context_state.selected_call_instrument_key))
app/mme_scalpx/services/feeds.py:2175:            payload["selected_put_json"] = _json_dumps(self._selected_option_member(frame, dhan_context_state.selected_put_instrument_key))
app/mme_scalpx/services/feeds.py:2178:    def _selected_option_member(self, frame: M.SnapshotFrame, instrument_key: str | None) -> Any:
app/mme_scalpx/core/models.py:2018:    selected_call_instrument_key: str | None = None
app/mme_scalpx/core/models.py:2019:    selected_put_instrument_key: str | None = None
app/mme_scalpx/core/models.py:2020:    selected_call_option_symbol: str | None = None
app/mme_scalpx/core/models.py:2021:    selected_put_option_symbol: str | None = None
app/mme_scalpx/core/models.py:2080:            "selected_call_instrument_key",
app/mme_scalpx/core/models.py:2081:            "selected_put_instrument_key",
app/mme_scalpx/core/models.py:2082:            "selected_call_option_symbol",
app/mme_scalpx/core/models.py:2083:            "selected_put_option_symbol",
app/mme_scalpx/core/models.py:2160:    selected_call_instrument_key: str | None = None
app/mme_scalpx/core/models.py:2161:    selected_put_instrument_key: str | None = None
app/mme_scalpx/core/models.py:2162:    selected_call_option_symbol: str | None = None
app/mme_scalpx/core/models.py:2163:    selected_put_option_symbol: str | None = None
app/mme_scalpx/core/models.py:2237:            "selected_call_instrument_key",
app/mme_scalpx/core/models.py:2238:            "selected_put_instrument_key",
app/mme_scalpx/core/models.py:2239:            "selected_call_option_symbol",
app/mme_scalpx/core/models.py:2240:            "selected_put_option_symbol",
app/mme_scalpx/core/names.py:458:    "selected_call_instrument_key",
app/mme_scalpx/core/names.py:459:    "selected_put_instrument_key",
app/mme_scalpx/replay/dataset.py:866:                for key in candidate.keys():
app/mme_scalpx/replay/miv_research_evaluator.py:54:    "selected_symbol",
app/mme_scalpx/replay/miv_research_evaluator.py:55:    "selected_option_symbol",
app/mme_scalpx/replay/miv_research_evaluator.py:204:    raw = f"{run_id}|{dataset_id}|MIV_R|{candidate_type}|{symbol}|{event_ns}|{score:.3f}"
app/mme_scalpx/replay/miv_research_evaluator.py:251:        "miv_candidate_id": _candidate_id(run_id, dataset_id, candidate_type, symbol, event_ns, score_total),
app/mme_scalpx/replay/miv_research_evaluator.py:337:            hard_reasons.append("missing_selected_option_symbol")
app/mme_scalpx/replay/live_evidence_map.py:147:    Path(candidate_path).write_text(json.dumps(candidate, indent=2, sort_keys=True), encoding="utf-8")
app/mme_scalpx/replay/offline_callable.py:52:        candidate = input_dir / f"{key}{suffix}"
app/mme_scalpx/replay/feature_adapter.py:195:            "tradingsymbol": _row_get(row, "selected_tradingsymbol", _row_get(row, "tradingsymbol")),
app/mme_scalpx/replay/artifacts.py:654:            ranked = sorted(candidates, key=lambda item: candidate_score(field, item), reverse=True)
app/mme_scalpx/replay/artifacts.py:663:            "candidates": {key: value[:20] for key, value in found.items()},
app/mme_scalpx/replay/artifacts.py:984:            candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
app/mme_scalpx/replay/batch_runner.py:329:        "selected_tradingsymbol": "NIFTY-REPLAY",
app/mme_scalpx/replay/contracts.py:2023:    "selected_tradingsymbol",

# view identity direct grep

## Targeted context excerpt
# strategy.py helper/context lines 420-530

        if value is None:
            out[field] = ""
        elif isinstance(value, (dict, list, tuple)):
            out[field] = _json_dump(value)
        elif isinstance(value, bool):
            out[field] = "1" if value else "0"
        else:
            out[field] = value

    return out


# R34F_SHADOW_CANDIDATE_TRUTH_EXPORT_BEGIN
def _r34f_shadow_candidate_truth_from_activation_selected(
    selected: Mapping[str, Any],
    view: Any = None,
) -> dict[str, Any]:
    """
    Shadow-only candidate truth export from activation-selected dry-run candidate.

    This deliberately does NOT promote strategy action, does NOT write to any
    trading/order stream, and does NOT enable broker/risk/execution paths.
    """
    selected_map = _mapping(selected)
    action = _safe_str(selected_map.get("action")).upper()
    is_enter = action in {"ENTER_CALL", "ENTER_PUT"}

    # R34K_SYMBOL_TOKEN_IDENTITY_EXPORT_BEGIN
    def _r34k_read(obj: Any, key: str) -> Any:
        if obj is None:
            return None
        if isinstance(obj, Mapping):
            return obj.get(key)
        return getattr(obj, key, None)

    def _r34k_walk(obj: Any, keys: tuple[str, ...], depth: int = 0, seen: set[int] | None = None) -> Any:
        if obj is None or depth > 4:
            return None
        if seen is None:
            seen = set()
        oid = id(obj)
        if oid in seen:
            return None
        seen.add(oid)

        for key in keys:
            value = _r34k_read(obj, key)
            if value not in (None, "", [], {}):
                return value

        if isinstance(obj, Mapping):
            iterable = obj.values()
        elif isinstance(obj, (str, bytes, int, float, bool)):
            iterable = ()
        elif hasattr(obj, "__dict__"):
            iterable = vars(obj).values()
        else:
            iterable = ()

        for child in iterable:
            value = _r34k_walk(child, keys, depth + 1, seen)
            if value not in (None, "", [], {}):
                return value
        return None

    symbol_keys = (
        "symbol", "tradingsymbol", "trading_symbol", "option_symbol",
        "selected_option_symbol", "selected_option_tradingsymbol",
        "selected_option_trading_symbol", "instrument_key",
        "selected_option_instrument_key",
    )
    token_keys = (
        "instrument_token", "token", "option_token",
        "selected_option_token", "selected_option_instrument_token",
    )

    candidate_symbol_shadow = _safe_str(
        _r34k_walk(selected_map, symbol_keys) or _r34k_walk(view, symbol_keys)
    )
    candidate_instrument_token_shadow = _safe_str(
        _r34k_walk(selected_map, token_keys) or _r34k_walk(view, token_keys)
    )
    # R34K_SYMBOL_TOKEN_IDENTITY_EXPORT_END

    return {
        "candidate_true_shadow": int(is_enter),
        "candidate_present_shadow": int(is_enter),
        "candidate_shadow_only": int(is_enter),
        "candidate_truth_mode_shadow": (
            "activation_selected_report_only_shadow" if is_enter else ""
        ),
        "candidate_action_shadow": action if is_enter else "",
        "candidate_family_id_shadow": (
            _safe_str(selected_map.get("family_id")).upper() if is_enter else ""
        ),
        "candidate_branch_id_shadow": (
            _safe_str(selected_map.get("branch_id")) if is_enter else ""
        ),
        "candidate_score_shadow": selected_map.get("score") if is_enter else None,
        "candidate_symbol_shadow": candidate_symbol_shadow if is_enter else "",
        "candidate_instrument_token_shadow": candidate_instrument_token_shadow if is_enter else "",
        "symbol": candidate_symbol_shadow if is_enter else "",
        "instrument_token": candidate_instrument_token_shadow if is_enter else "",
        "real_order_sent_shadow": 0,
        "broker_calls_executed_shadow": 0,
        "redis_trading_stream_write_attempted_shadow": 0,
    }
# R34F_SHADOW_CANDIDATE_TRUTH_EXPORT_END



# strategy.py activation publication lines 1050-1165
            report.setdefault("family_runtime_report_only", bool(report.get("report_only", True)))
            report.setdefault("family_runtime_safe_to_promote", bool(report.get("safe_to_promote", False)))
            report.setdefault("family_runtime_promoted", bool(report.get("promoted", False)))

        return report

    def build_hold_decision(
        self,
        view: StrategyFamilyConsumerView,
        *,
        now_ns: int,
    ) -> dict[str, Any]:
        """
        Build HOLD-only strategy decision.

        This shape is intentionally conservative and diagnostic-rich. Execution
        must ignore HOLD for order placement.
        """
        selected_option = (
            _mapping(view.common.get("selected_option"))
            or _mapping(view.common.get("selected_call"))
            or _mapping(view.common.get("selected_put"))
        )

        activation_report = self.build_activation_report(view, now_ns=now_ns)
        activation_selected = _mapping(activation_report.get("selected"))
        activation_candidates = activation_report.get("candidates")
        activation_candidate_count = (
            len(activation_candidates)
            if isinstance(activation_candidates, list)
            else 0
        )
        r34f_shadow_fields = _r34f_shadow_candidate_truth_from_activation_selected(
            activation_selected,
            view=view,
        )

        decision_id = f"strategy-hold-{now_ns}"

        return {
            "schema_version": getattr(N, "DEFAULT_SCHEMA_VERSION", 1),
            "service": SERVICE_STRATEGY,
            "decision_id": decision_id,
            "ts_ns": now_ns,
            "ts_event_ns": now_ns,
            "action": ACTION_HOLD,
            "side": getattr(N, "POSITION_SIDE_FLAT", "FLAT"),
            "branch_id": "",
            "strategy_family_id": "",
            "doctrine_id": "",
            "instrument_key": _safe_str(selected_option.get("instrument_key")),
            "instrument_token": _safe_str(selected_option.get("instrument_token")),
            "option_symbol": _safe_str(selected_option.get("option_symbol")),
            "strike": selected_option.get("strike"),
            "qty": 0,
            "price": selected_option.get("ltp"),
            "order_type": "",
            "reason": view.reason,
            "confidence": 0.0,
            "hold_only": 1,
            "activation_bridge_enabled": 1,
            "activation_report_only": 1,
            "activation_mode": _safe_str(activation_report.get("activation_mode"), ACTIVATION_REPORT_MODE),
            "activation_action": ACTION_HOLD,
            "activation_observed_action": _safe_str(
                activation_report.get("observed_action_before_strategy_clamp"),
                _safe_str(activation_report.get("action"), ACTION_HOLD),
            ),
            "activation_promoted": 0,
            "activation_safe_to_promote": 0,
            "activation_reason": _safe_str(activation_report.get("reason")),
            "activation_selected_family_id": _safe_str(activation_selected.get("family_id")),
            "activation_selected_branch_id": _safe_str(activation_selected.get("branch_id")),
            "activation_selected_action": _safe_str(activation_selected.get("action")),
            "activation_selected_score": activation_selected.get("score"),
            "activation_candidate_count": activation_candidate_count,
            **r34f_shadow_fields,
            "safe_to_consume": int(view.safe_to_consume),
            "data_valid": int(view.data_valid),
            "warmup_complete": int(view.warmup_complete),
            "provider_ready_classic": int(view.provider_ready_classic),
            "provider_ready_miso": int(view.provider_ready_miso),
            "regime": view.regime or "",
            "features_generated_at_ns": view.features_generated_at_ns,
            "consumer_view_json": _json_dump(view.to_dict()),
            "activation_report_json": _json_dump(activation_report),
            "diagnostics_json": _json_dump(
                {
                    "bridge": "strategy_family_consumer_bridge",
                    "hold_only": True,
                    "activation_bridge_report_only": True,
                    "activation_mode": _safe_str(activation_report.get("activation_mode"), ACTIVATION_REPORT_MODE),
                    "activation_reason": _safe_str(activation_report.get("reason")),
                    "activation_selected_family_id": _safe_str(activation_selected.get("family_id")),
                    "activation_selected_branch_id": _safe_str(activation_selected.get("branch_id")),
                    "activation_candidate_count": activation_candidate_count,
                    "doctrine_leaves_observed": True,
                    "doctrine_leaves_active": False,
                    "broker_side_effects_allowed": False,
                    "live_orders_allowed": False,
                    "families": tuple(view.family_status.keys()),
                    "branch_frame_count": len(view.branch_frames),
                }
            ),
        }


# =============================================================================
# Service
# =============================================================================


class StrategyService:
    def __init__(
        self,
        *,

# strategy.py later view/candidate context lines 1960-2030
    # I ACCEPT FAMILY SIDE 1LOT PAPER ONLY
    return {
        "enabled": True,
        "reason": "classic_1lot_paper_only_scope_ack",
        "ack": ack,
        "family": parts[2],
        "side": parts[3],
    }


def _r38r_controlled_paper_activation_mode():
    return "paper_armed" if _r38r_controlled_paper_env_truth().get("enabled") else ACTIVATION_REPORT_MODE


def _r38r_controlled_paper_candidate_promotion_allowed():
    return bool(_r38r_controlled_paper_env_truth().get("enabled"))
# END R38R_CLASSIC_CONTROLLED_PAPER_ACTIVATION_BRIDGE


def a6_live_r2h_controlled_paper_activation_gate(
    activation_view: _A6R2HMapping[str, _A6R2HAny] | None = None,
    *,
    selected_scope: _A6R2HMapping[str, _A6R2HAny] | None = None,
    position_flat: bool = False,
    orders_zero: bool = False,
) -> dict[str, _A6R2HAny]:
    """A6-LIVE-R2H minimal activation gate.

