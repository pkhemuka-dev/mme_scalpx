# LANE-B-R5C_BASELINE_SHADOW_DRY_RUN_PACKAGE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143758
2026-06-07T14:37:58+05:30

LAW=DRY_RUN_PACKAGE_ONLY_NO_PATCH_NO_REPLAY_NO_ORDER_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_RISK_NO_EXECUTION

## R5B proof
R5B=run/proofs/LANE-B-R5B_BASELINE_VS_SHADOW_PATCH_IMPACT_REPLAY_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143653.json
{
  "tag": "LANE-B-R5B_BASELINE_VS_SHADOW_PATCH_IMPACT_REPLAY_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143653",
  "classification": "PASS_R5B_BASELINE_SHADOW_PATCH_IMPACT_PLAN_READY_FOR_R5C_DRY_RUN_PACKAGE",
  "patch_applied": false,
  "replay_executed": false,
  "broker_order": false,
  "paper_live": false,
  "redis_delete": false,
  "risk_execution_start": false,
  "dataset_root": "run/replay/staging/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337",
  "report": "run/audits/LANE-B-R5B_BASELINE_VS_SHADOW_PATCH_IMPACT_REPLAY_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143653_report.md"
}

## Required file presence
FOUND run/replay/staging/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/2026-06-02/fut_ticks.jsonl
FOUND run/replay/staging/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/2026-06-02/opt_ticks.jsonl
FOUND run/_code_backups/LANE-X-R27E_misb_prior_shelf_breakout_ref_patch_no_start_no_order_20260607_120500_features.py.backup
FOUND run/_code_backups/LANE-X-R27E_misb_prior_shelf_breakout_ref_patch_no_start_no_order_20260607_120500_misb_surface.py.backup
FOUND app/mme_scalpx/services/features.py
FOUND app/mme_scalpx/services/feature_family/misb_surface.py
FOUND app/mme_scalpx/services/strategy.py
FOUND bin/replay_run.py

## Fingerprints
e3433ac93d0df00ce344f4c87332b1e659e0eb73517a5151ee98d0c0d7fbd359  run/_code_backups/LANE-X-R27E_misb_prior_shelf_breakout_ref_patch_no_start_no_order_20260607_120500_features.py.backup
804b22bd879778e3907641a85e520bca0674e65a2296abe7fde71746812bf474  run/_code_backups/LANE-X-R27E_misb_prior_shelf_breakout_ref_patch_no_start_no_order_20260607_120500_misb_surface.py.backup
8426ef33c527c3c5c4c66fe1f21a6e4bb08f77a9929d8ef7252aa2fc405cf5c5  app/mme_scalpx/services/features.py
2e8b399696080359148a3d1ed35538f5963c993f03dc7349d193919488da169a  app/mme_scalpx/services/feature_family/misb_surface.py
2b3d3ff7c2870f249d2ff3b9dec5600fb1af0f607fda3c3486de6a58970e7ebc  app/mme_scalpx/services/strategy.py

## Created dry plan
DRY_PLAN=run/patches/LANE-B-R5C_BASELINE_SHADOW_DRY_RUN_PACKAGE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143758_r5d_reversible_baseline_shadow_plan.sh
#!/usr/bin/env bash
# LANE-B-R5C_BASELINE_SHADOW_DRY_RUN_PACKAGE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143758
# DRY PLAN ONLY CREATED BY R5C.
# Do not run blindly. R5D should execute only after reviewing this file.

set -euo pipefail
cd /home/Lenovo/scalpx/projects/mme_scalpx
exec 1>&2

PY=".venv/bin/python"
[ -x "$PY" ] || PY="python3"

DATASET_ROOT="run/replay/staging/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337"

BASE_FEATURES="run/_code_backups/LANE-X-R27E_misb_prior_shelf_breakout_ref_patch_no_start_no_order_20260607_120500_features.py.backup"
BASE_MISB="run/_code_backups/LANE-X-R27E_misb_prior_shelf_breakout_ref_patch_no_start_no_order_20260607_120500_misb_surface.py.backup"
CUR_FEATURES="app/mme_scalpx/services/features.py"
CUR_MISB="app/mme_scalpx/services/feature_family/misb_surface.py"
CUR_STRATEGY="app/mme_scalpx/services/strategy.py"

R5D_TAG="LANE-B-R5D_EXECUTE_BASELINE_SHADOW_PATCH_IMPACT_REPLAY_NO_PATCH_FINAL_RESTORE_NO_ORDER_$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="run/replay/lane_b_r5d/$R5D_TAG"
LOG_ROOT="run/logs/$R5D_TAG"
RESTORE_DIR="run/_code_backups/${R5D_TAG}_restore_current_sources"

mkdir -p "$RUN_ROOT" "$LOG_ROOT" "$RESTORE_DIR"

# Save current shadow sources for restore.
cp "$CUR_FEATURES" "$RESTORE_DIR/features.py.current"
cp "$CUR_MISB" "$RESTORE_DIR/misb_surface.py.current"
cp "$CUR_STRATEGY" "$RESTORE_DIR/strategy.py.current"

restore_current() {
  cp "$RESTORE_DIR/features.py.current" "$CUR_FEATURES"
  cp "$RESTORE_DIR/misb_surface.py.current" "$CUR_MISB"
  cp "$RESTORE_DIR/strategy.py.current" "$CUR_STRATEGY"
  "$PY" -m compileall -q app/mme_scalpx/services app/mme_scalpx/replay
}

trap restore_current EXIT

echo "## Baseline replay: restore pre-R27E/R27G backup pair temporarily"
cp "$BASE_FEATURES" "$CUR_FEATURES"
cp "$BASE_MISB" "$CUR_MISB"
"$PY" -m compileall -q app/mme_scalpx/services app/mme_scalpx/replay

"$PY" bin/replay_run.py \
  --dataset-root "$DATASET_ROOT" \
  --selection-mode single_day \
  --single-day 2026-06-02 \
  --doctrine-mode locked \
  --scope feeds_features_strategy_risk_execution_shadow \
  --speed-mode accelerated \
  --fill-model immediate_market \
  --run-label "${R5D_TAG}_BASELINE_PRE_R27E_R27G" \
  --run-root "$RUN_ROOT/baseline_pre_r27e_r27g" \
  > "$LOG_ROOT/baseline.log" 2>&1

echo "## Shadow replay: restore current source and run current"
restore_current

"$PY" bin/replay_run.py \
  --dataset-root "$DATASET_ROOT" \
  --selection-mode single_day \
  --single-day 2026-06-02 \
  --doctrine-mode locked \
  --scope feeds_features_strategy_risk_execution_shadow \
  --speed-mode accelerated \
  --fill-model immediate_market \
  --run-label "${R5D_TAG}_SHADOW_CURRENT" \
  --run-root "$RUN_ROOT/shadow_current" \
  > "$LOG_ROOT/shadow.log" 2>&1

echo "R5D_RUN_ROOT=$RUN_ROOT"
echo "R5D_LOG_ROOT=$LOG_ROOT"
echo "RESTORE_DIR=$RESTORE_DIR"

CLASSIFICATION=PASS_R5C_DRY_RUN_PACKAGE_READY_FOR_REVIEWED_R5D_EXECUTION
