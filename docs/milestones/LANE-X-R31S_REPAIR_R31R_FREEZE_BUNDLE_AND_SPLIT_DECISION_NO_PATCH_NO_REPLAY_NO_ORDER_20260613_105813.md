# LANE-X-R31S_REPAIR_R31R_FREEZE_BUNDLE_AND_SPLIT_DECISION_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_105813
2026-06-13T10:58:13+05:30

LAW=BUNDLE_REPAIR_AND_DECISION_FREEZE_ONLY_NO_PATCH_NO_REPLAY_NO_START_NO_STOP_NO_ORDER_NO_REDIS_DELETE_NO_PAPER_NO_RISK_NO_EXECUTION

## Latest R31R artifacts
R31R_PROOF=run/proofs/LANE-X-R31R_COMMON_KEY_SEAM_CLOSED_AND_DIRTY_TREE_FREEZE_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_105507.json
R31R_REPORT=run/audits/LANE-X-R31R_COMMON_KEY_SEAM_CLOSED_AND_DIRTY_TREE_FREEZE_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_105507_report.md
R31R_MANIFEST=run/audits/LANE-X-R31R_COMMON_KEY_SEAM_CLOSED_AND_DIRTY_TREE_FREEZE_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_105507_dirty_manifest.sha256
R31R_RUNBOOK=docs/runbooks/LANE-X-R31R_COMMON_KEY_SEAM_CLOSED_AND_DIRTY_TREE_FREEZE_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_105507_runbook.md

{
  "tag": "LANE-X-R31R_COMMON_KEY_SEAM_CLOSED_AND_DIRTY_TREE_FREEZE_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_105507",
  "classification": "PASS_R31R_R31_COMMON_KEY_SEAM_CLOSED_DIRTY_TREE_FREEZE_READY",
  "r31_common_key_seam": "closed_no_patch_required",
  "patch_applied": false,
  "replay_executed": false,
  "started_runtime": false,
  "stopped_runtime": false,
  "broker_order": false,
  "paper_live": false,
  "redis_delete": false,
  "risk_execution_start": false,
  "compile_rc": "0",
  "import_rc": "0",
  "bundle": "run/evidence_bundles/LANE-X-R31R_COMMON_KEY_SEAM_CLOSED_AND_DIRTY_TREE_FREEZE_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_105507.tar.gz",
  "manifest": "run/audits/LANE-X-R31R_COMMON_KEY_SEAM_CLOSED_AND_DIRTY_TREE_FREEZE_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_105507_dirty_manifest.sha256",
  "report": "run/audits/LANE-X-R31R_COMMON_KEY_SEAM_CLOSED_AND_DIRTY_TREE_FREEZE_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_105507_report.md"
}

## Safety
ACTIVE_RUNTIME_PROCESSES=NONE
orders_stream_len=0
risk_stream_len=0
execution_stream_len=0

## Frozen decision
R31_COMMON_KEY_SEAM=CLOSED_NO_PATCH_REQUIRED
COMMON_KEY_PATCH_ALLOWED=false
REASON=R31P exact common contract match plus R31Q no active common-key/bridge errors.

## Dirty tree split decision
DIRTY_TREE_STATUS=INTEGRATED_PENDING_PATCH_SET
NEXT_SPLIT_LANES:
1_MIV_RESEARCH=app/mme_scalpx/replay/miv_research_evaluator.py app/mme_scalpx/services/strategy_family/miv_r_contract.py proof_miv/audit_miv scripts
2_REPLAY_BRIDGE=app/mme_scalpx/replay/strategy_adapter.py bin/replay_run.py
3_INTERNAL_ORDER_INTENT=app/mme_scalpx/services/strategy_family/internal_order_intent_pipeline.py bin/proof_r32* bin/lane_x_r32i*
4_DASHBOARD=app/mme_scalpx/ops_dashboard/server.py
5_MARKETDATA_FEATURES=app/mme_scalpx/services/features.py app/mme_scalpx/services/feature_family/misb_surface.py data/instruments/nfo_instruments.csv

## Dirty tracked files
M	app/mme_scalpx/ops_dashboard/server.py
M	app/mme_scalpx/replay/strategy_adapter.py
M	app/mme_scalpx/services/feature_family/misb_surface.py
M	app/mme_scalpx/services/features.py
M	app/mme_scalpx/services/strategy.py
M	bin/replay_run.py
M	data/instruments/nfo_instruments.csv

## Dirty diff stat
 app/mme_scalpx/ops_dashboard/server.py             |   131 +-
 app/mme_scalpx/replay/strategy_adapter.py          |     7 +-
 .../services/feature_family/misb_surface.py        |    24 +
 app/mme_scalpx/services/features.py                |   957 +
 app/mme_scalpx/services/strategy.py                |    27 +
 bin/replay_run.py                                  |   440 +-
 data/instruments/nfo_instruments.csv               | 42399 ++++++++++---------
 7 files changed, 24753 insertions(+), 19232 deletions(-)

## Untracked source scripts compact
app/mme_scalpx/replay/miv_research_evaluator.py
app/mme_scalpx/services/strategy_family/internal_order_intent_pipeline.py
app/mme_scalpx/services/strategy_family/miv_r_contract.py
bin/audit_miv_r1b_gate_surfaces_no_patch_no_replay_no_order.py
bin/audit_miv_r2b_evaluator_output_shape_no_patch_no_replay_no_order.py
bin/lane_x_r32i_materialize_internal_order_intent_from_replay_results_no_broker.py
bin/lane_x_shadow_near_candidate_observer.py
bin/proof_miv_r1a_strategy_family_dormant_contract_no_replay_no_order.py
bin/proof_miv_r2_zerodha_lite_research_evaluator_no_replay_no_order.py
bin/proof_miv_r2c_neutral_label_route_no_patch_no_replay_no_order.py
bin/proof_r32d_internal_order_intent_pipeline_no_broker.py
bin/proof_r32g_real_candidate_hold_normalizer_no_broker.py

## Compile/import verification
COMPILE_RC=0
{
  "app.mme_scalpx.replay.miv_research_evaluator": "OK",
  "app.mme_scalpx.replay.strategy_adapter": "OK",
  "app.mme_scalpx.services.feature_family.contracts": "OK",
  "app.mme_scalpx.services.features": "OK",
  "app.mme_scalpx.services.strategy": "OK",
  "app.mme_scalpx.services.strategy_family.decisions": "OK",
  "app.mme_scalpx.services.strategy_family.internal_order_intent_pipeline": "OK",
  "app.mme_scalpx.services.strategy_family.miv_r_contract": "OK"
}
IMPORT_RC=0

## Write repaired evidence bundle
BUNDLE_RC=0
ebd539cc885c035f42610959936a23311e0386b775d5ecc37dad20fd4cdb4d7e  run/evidence_bundles/LANE-X-R31S_REPAIR_R31R_FREEZE_BUNDLE_AND_SPLIT_DECISION_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_105813.tar.gz
BUNDLE=run/evidence_bundles/LANE-X-R31S_REPAIR_R31R_FREEZE_BUNDLE_AND_SPLIT_DECISION_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_105813.tar.gz

orders_stream_len_after=0
risk_stream_len_after=0
execution_stream_len_after=0
CLASSIFICATION=PASS_R31S_R31_FREEZE_BUNDLE_REPAIRED_READY_FOR_DIRTY_TREE_SPLIT
