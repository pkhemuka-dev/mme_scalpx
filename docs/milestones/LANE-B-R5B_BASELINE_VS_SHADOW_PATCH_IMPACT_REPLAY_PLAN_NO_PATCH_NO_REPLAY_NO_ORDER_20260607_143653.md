# LANE-B-R5B_BASELINE_VS_SHADOW_PATCH_IMPACT_REPLAY_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143653
2026-06-07T14:36:53+05:30

LAW=PLAN_ONLY_NO_PATCH_NO_REPLAY_NO_ORDER_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_RISK_NO_EXECUTION

## R5A latest proof/report
R5A_PROOF=run/proofs/LANE-B-R5A_PATCH_IMPACT_REPLAY_ROUTE_PREFLIGHT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143419.json
R5A_REPORT=run/audits/LANE-B-R5A_PATCH_IMPACT_REPLAY_ROUTE_PREFLIGHT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143419_report.md
{
  "tag": "LANE-B-R5A_PATCH_IMPACT_REPLAY_ROUTE_PREFLIGHT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143419",
  "classification": "PASS_R5A_PATCH_IMPACT_ROUTE_SURFACE_VISIBLE_READY_FOR_R5B_BASELINE_SHADOW_PLAN",
  "patch_applied": false,
  "replay_executed": false,
  "broker_order": false,
  "paper_live": false,
  "redis_delete": false,
  "risk_execution_start": false,
  "report": "run/audits/LANE-B-R5A_PATCH_IMPACT_REPLAY_ROUTE_PREFLIGHT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143419_report.md"
}

## Dataset selected for patch-impact replay
DATASET_ROOT=run/replay/staging/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337
DAY_MANIFEST=FOUND
FUT_TICKS=21808
OPT_TICKS=112227

## Current source fingerprints
8426ef33c527c3c5c4c66fe1f21a6e4bb08f77a9929d8ef7252aa2fc405cf5c5  app/mme_scalpx/services/features.py
2e8b399696080359148a3d1ed35538f5963c993f03dc7349d193919488da169a  app/mme_scalpx/services/feature_family/misb_surface.py
2b3d3ff7c2870f249d2ff3b9dec5600fb1af0f607fda3c3486de6a58970e7ebc  app/mme_scalpx/services/strategy.py

## Baseline backup candidates with fingerprints
b3e9d9d4519b6758e88ffbf0ea2594671474435920ddfa08acda8a688abeb89a  run/_code_backups/B4-R5P_MICRO_SHELF_PRODUCER_PATCH_NO_START_NO_ORDER_20260603_234829_features.py.bak
15d7a02d6ebf0c084b88351fa8206da89fa30524d9964078f1c710264a2b3718  run/_code_backups/LANE-X-R26B_micro_futures_kinetics_producer_patch_no_start_no_order_20260607_113211_features.py.backup
e3433ac93d0df00ce344f4c87332b1e659e0eb73517a5151ee98d0c0d7fbd359  run/_code_backups/LANE-X-R27E_misb_prior_shelf_breakout_ref_patch_no_start_no_order_20260607_120500_features.py.backup
804b22bd879778e3907641a85e520bca0674e65a2296abe7fde71746812bf474  run/_code_backups/LANE-X-R27E_misb_prior_shelf_breakout_ref_patch_no_start_no_order_20260607_120500_misb_surface.py.backup
53daacc9f0fa23afd0ad78e47c8e6081acf5381cdf545f92116a873eb50a2f4f  run/_code_backups/LANE-X-R27G_misb_prior_shelf_ref_contract_passthrough_patch_no_start_no_order_20260607_120850_features.py.backup

## Exact patch markers in current source
app/mme_scalpx/services/features.py:8927:# B4_R5P_MICRO_SHELF_PRODUCER_PATCH_BEGIN
app/mme_scalpx/services/features.py:8940:_B4_R5P_PREV_FUTURES_SURFACE = FeatureEngine._futures_surface
app/mme_scalpx/services/features.py:8941:_B4_R5P_PREV_CONTRACT_FUTURES_BLOCK = FeatureEngine._contract_futures_block
app/mme_scalpx/services/features.py:8943:_B4_R5P_MICRO_SHELF_WINDOW_NS = 45_000_000_000
app/mme_scalpx/services/features.py:8944:_B4_R5P_MICRO_SHELF_MAX_SAMPLES = 96
app/mme_scalpx/services/features.py:8945:_B4_R5P_MICRO_SHELF_MIN_SNAPSHOTS = 3
app/mme_scalpx/services/features.py:9011:def _b4_r5p_apply_micro_shelf(self, surface):
app/mme_scalpx/services/features.py:9021:        out.setdefault("breakout_shelf_source", "micro_shelf_no_valid_price")
app/mme_scalpx/services/features.py:9029:    history = getattr(self, "_b4_r5p_micro_shelf_history", None)
app/mme_scalpx/services/features.py:9032:        setattr(self, "_b4_r5p_micro_shelf_history", history)
app/mme_scalpx/services/features.py:9037:    cutoff = event_ns - _B4_R5P_MICRO_SHELF_WINDOW_NS if event_ns > 0 else 0
app/mme_scalpx/services/features.py:9043:    samples = samples[-_B4_R5P_MICRO_SHELF_MAX_SAMPLES:]
app/mme_scalpx/services/features.py:9047:    out.setdefault("breakout_shelf_source", "micro_shelf")
app/mme_scalpx/services/features.py:9048:    out.setdefault("breakout_shelf_window_seconds", int(_B4_R5P_MICRO_SHELF_WINDOW_NS / 1_000_000_000))
app/mme_scalpx/services/features.py:9054:    if count < _B4_R5P_MICRO_SHELF_MIN_SNAPSHOTS:
app/mme_scalpx/services/features.py:9055:        out.setdefault("breakout_shelf_missing_reason_hint", "micro_shelf_warming")
app/mme_scalpx/services/features.py:9093:def _b4_r5p_futures_surface_with_micro_shelf(
app/mme_scalpx/services/features.py:9100:    surface = _B4_R5P_PREV_FUTURES_SURFACE(
app/mme_scalpx/services/features.py:9106:    return _b4_r5p_apply_micro_shelf(self, surface)
app/mme_scalpx/services/features.py:9110:    block = _B4_R5P_PREV_CONTRACT_FUTURES_BLOCK(self, surface)
app/mme_scalpx/services/features.py:9153:FeatureEngine._futures_surface = _b4_r5p_futures_surface_with_micro_shelf
app/mme_scalpx/services/features.py:9155:# B4_R5P_MICRO_SHELF_PRODUCER_PATCH_END
app/mme_scalpx/services/features.py:9236:# LANE_X_R26B_MICRO_FUTURES_KINETICS_BEGIN
app/mme_scalpx/services/features.py:9252:_LANE_X_R26B_PREV_FUTURES_SURFACE = FeatureEngine._futures_surface
app/mme_scalpx/services/features.py:9253:_LANE_X_R26B_PREV_CONTRACT_FUTURES_BLOCK = FeatureEngine._contract_futures_block
app/mme_scalpx/services/features.py:9255:_LANE_X_R26B_MAX_SAMPLES = 12
app/mme_scalpx/services/features.py:9256:_LANE_X_R26B_EVENT_RATE_BASELINE_PER_SEC = 0.20
app/mme_scalpx/services/features.py:9338:def _lane_x_r26b_micro_futures_kinetics(self, surface, *, role, provider_id):
app/mme_scalpx/services/features.py:9342:        out.setdefault("micro_futures_kinetics_source", "micro_futures_no_valid_price")
app/mme_scalpx/services/features.py:9343:        out.setdefault("micro_futures_kinetics_ready", False)
app/mme_scalpx/services/features.py:9359:    samples = samples[-_LANE_X_R26B_MAX_SAMPLES:]
app/mme_scalpx/services/features.py:9368:    out["micro_futures_kinetics_source"] = "micro_futures_kinetics"
app/mme_scalpx/services/features.py:9369:    out["micro_futures_kinetics_sample_count"] = sample_count
app/mme_scalpx/services/features.py:9372:        out["micro_futures_kinetics_ready"] = False
app/mme_scalpx/services/features.py:9394:    event_rate_norm = event_rate / max(_LANE_X_R26B_EVENT_RATE_BASELINE_PER_SEC, 1e-9)
app/mme_scalpx/services/features.py:9415:        out["micro_futures_volume_norm_source"] = "micro_event_rate_proxy"
app/mme_scalpx/services/features.py:9417:    out["micro_futures_kinetics_ready"] = True
app/mme_scalpx/services/features.py:9418:    out["micro_futures_ref_ltp"] = ref_price
app/mme_scalpx/services/features.py:9419:    out["micro_futures_ref_ts_ns"] = ref_ts
app/mme_scalpx/services/features.py:9420:    out["micro_futures_delta_3"] = delta
app/mme_scalpx/services/features.py:9421:    out["micro_futures_velocity_ratio"] = velocity_ratio
app/mme_scalpx/services/features.py:9422:    out["micro_futures_event_rate_per_sec"] = event_rate
app/mme_scalpx/services/features.py:9423:    out["micro_futures_event_rate_norm"] = event_rate_norm
app/mme_scalpx/services/features.py:9424:    out["micro_futures_latest_ltp"] = price
app/mme_scalpx/services/features.py:9438:        surface = _LANE_X_R26B_PREV_FUTURES_SURFACE(
app/mme_scalpx/services/features.py:9447:        surface = _LANE_X_R26B_PREV_FUTURES_SURFACE(
app/mme_scalpx/services/features.py:9457:    return _lane_x_r26b_micro_futures_kinetics(
app/mme_scalpx/services/features.py:9466:    block = _LANE_X_R26B_PREV_CONTRACT_FUTURES_BLOCK(self, surface)
app/mme_scalpx/services/features.py:9480:        "micro_futures_kinetics_source",
app/mme_scalpx/services/features.py:9481:        "micro_futures_kinetics_ready",
app/mme_scalpx/services/features.py:9482:        "micro_futures_kinetics_sample_count",
app/mme_scalpx/services/features.py:9483:        "micro_futures_delta_3",
app/mme_scalpx/services/features.py:9484:        "micro_futures_velocity_ratio",
app/mme_scalpx/services/features.py:9485:        "micro_futures_event_rate_per_sec",
app/mme_scalpx/services/features.py:9486:        "micro_futures_event_rate_norm",
app/mme_scalpx/services/features.py:9487:        "micro_futures_volume_norm_source",
app/mme_scalpx/services/features.py:9504:# LANE_X_R26B_MICRO_FUTURES_KINETICS_END
app/mme_scalpx/services/features.py:9506:# LANE_X_R27E_MISB_PRIOR_SHELF_REF_BEGIN
app/mme_scalpx/services/features.py:9509:# R27D proved the existing micro_shelf range is current-inclusive:
app/mme_scalpx/services/features.py:9518:# - breakout_shelf_prior_high / breakout_shelf_prior_low
app/mme_scalpx/services/features.py:9525:_LANE_X_R27E_PREV_FUTURES_SURFACE = FeatureEngine._futures_surface
app/mme_scalpx/services/features.py:9527:_LANE_X_R27E_WINDOW_NS = 45_000_000_000
app/mme_scalpx/services/features.py:9528:_LANE_X_R27E_MAX_SAMPLES = 96
app/mme_scalpx/services/features.py:9632:    cutoff = event_ns - _LANE_X_R27E_WINDOW_NS if event_ns else 0
app/mme_scalpx/services/features.py:9635:    samples = samples[-_LANE_X_R27E_MAX_SAMPLES:]
app/mme_scalpx/services/features.py:9652:                "breakout_shelf_prior_high": high,
app/mme_scalpx/services/features.py:9653:                "breakout_shelf_prior_low": low,
app/mme_scalpx/services/features.py:9654:                "breakout_shelf_prior_width": width,
app/mme_scalpx/services/features.py:9655:                "breakout_shelf_prior_width_pct": width_pct,
app/mme_scalpx/services/features.py:9656:                "breakout_shelf_prior_count": len(prices),
app/mme_scalpx/services/features.py:9657:                "breakout_shelf_ref_source": "prior_micro_shelf",
app/mme_scalpx/services/features.py:9662:        out = _LANE_X_R27E_PREV_FUTURES_SURFACE(
app/mme_scalpx/services/features.py:9671:        out = _LANE_X_R27E_PREV_FUTURES_SURFACE(
app/mme_scalpx/services/features.py:9692:        hist[key] = samples[-_LANE_X_R27E_MAX_SAMPLES:]
app/mme_scalpx/services/features.py:9703:# LANE_X_R27E_MISB_PRIOR_SHELF_REF_END
app/mme_scalpx/services/features.py:9705:# LANE_X_R27G_MISB_PRIOR_REF_CONTRACT_PASSTHROUGH_BEGIN
app/mme_scalpx/services/features.py:9714:_LANE_X_R27G_PREV_CONTRACT_FUTURES_BLOCK = FeatureEngine._contract_futures_block
app/mme_scalpx/services/features.py:9716:_LANE_X_R27G_PRIOR_REF_KEYS = (
app/mme_scalpx/services/features.py:9721:    "breakout_shelf_prior_high",
app/mme_scalpx/services/features.py:9722:    "breakout_shelf_prior_low",
app/mme_scalpx/services/features.py:9723:    "breakout_shelf_prior_width",
app/mme_scalpx/services/features.py:9724:    "breakout_shelf_prior_width_pct",
app/mme_scalpx/services/features.py:9725:    "breakout_shelf_prior_count",
app/mme_scalpx/services/features.py:9732:    block = _LANE_X_R27G_PREV_CONTRACT_FUTURES_BLOCK(self, surface)
app/mme_scalpx/services/features.py:9740:    for key in _LANE_X_R27G_PRIOR_REF_KEYS:
app/mme_scalpx/services/features.py:9749:# LANE_X_R27G_MISB_PRIOR_REF_CONTRACT_PASSTHROUGH_END
app/mme_scalpx/services/feature_family/misb_surface.py:529:    # LANE_X_R27E_MISB_PRIOR_BREAKOUT_REF_BEGIN
app/mme_scalpx/services/feature_family/misb_surface.py:536:                "breakout_shelf_prior_high",
app/mme_scalpx/services/feature_family/misb_surface.py:547:                "breakout_shelf_prior_low",
app/mme_scalpx/services/feature_family/misb_surface.py:552:    # LANE_X_R27E_MISB_PRIOR_BREAKOUT_REF_END

## Proposed baseline/shadow definition
BASELINE_CANDIDATE_A:
  restore only B4-R5P backup features.py as baseline before micro-shelf producer patch
  compare against current source
  purpose: isolate B4-R5P micro-shelf impact

BASELINE_CANDIDATE_B:
  restore Lane-X-R26B backup features.py as baseline before micro futures kinetics patch
  compare against current source
  purpose: isolate R26B/R27 combined weekend microstructure impact

BASELINE_CANDIDATE_C:
  restore Lane-X-R27E backups for features.py and misb_surface.py
  compare against current source
  purpose: isolate R27E/R27G prior-shelf reference/passthrough impact

RECOMMENDED_FIRST_REPLAY:
  baseline = latest clean pre-R27E/R27G backup pair
  shadow   = current source
  dataset  = A7 normalized 2026-06-02
  scope    = feeds_features_strategy_risk_execution_shadow
  fill     = immediate_market
  expected = candidate_count may still be 0; purpose is patch-impact measurement, not forced PnL

CLASSIFICATION=PASS_R5B_BASELINE_SHADOW_PATCH_IMPACT_PLAN_READY_FOR_R5C_DRY_RUN_PACKAGE
