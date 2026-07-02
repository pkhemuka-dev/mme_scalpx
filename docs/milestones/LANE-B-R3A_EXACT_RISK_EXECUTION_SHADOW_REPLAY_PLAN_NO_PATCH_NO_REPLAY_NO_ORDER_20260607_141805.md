# LANE-B-R3A_EXACT_RISK_EXECUTION_SHADOW_REPLAY_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141805
2026-06-07T14:18:05+05:30

LAW=PLAN_ONLY_NO_PATCH_NO_REPLAY_NO_ORDER_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_RISK_NO_EXECUTION

## Inputs
DATASET_ROOT=run/replay/staging/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337
RUN_ROOT=run/replay/lane_b_r4/LANE-B-R3A_EXACT_RISK_EXECUTION_SHADOW_REPLAY_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141805
DATASET_MANIFEST=FOUND
DAY_MANIFEST=FOUND
FUT_TICKS=21808
OPT_TICKS=112227

## Exact proposed R4 command
.venv/bin/python bin/replay_run.py \
  --dataset-root "run/replay/staging/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337" \
  --selection-mode single_day \
  --single-day 2026-06-02 \
  --doctrine-mode locked \
  --scope feeds_features_strategy_risk_execution_shadow \
  --speed-mode accelerated \
  --fill-model immediate_market \
  --run-label LANE-B-R4_A7_20260602_RISK_EXECUTION_SHADOW_REPLAY_SMOKE_NO_PATCH_NO_ORDER \
  --run-root "run/replay/lane_b_r4/LANE-B-R3A_EXACT_RISK_EXECUTION_SHADOW_REPLAY_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141805"

## Source checks for scope/fill-model strings
bin/replay_run.py:49:from app.mme_scalpx.replay.fill_model import (
bin/replay_run.py:121:        self._execution_shadow_results: list[dict[str, Any]] = []
bin/replay_run.py:140:    def execution_shadow_results(self) -> tuple[dict[str, Any], ...]:
bin/replay_run.py:141:        return tuple(self._execution_shadow_results)
bin/replay_run.py:192:    def publish_execution_shadow_result(
bin/replay_run.py:197:        self._execution_shadow_results.append(stored)
bin/replay_run.py:251:    parser.add_argument("--fill-model", default=None)
bin/replay_run.py:358:        fill_model=args.fill_model,
bin/replay_run.py:1833:def _resolve_fill_model_name(fill_model_name: str | None) -> str:
bin/replay_run.py:1834:    if fill_model_name:
bin/replay_run.py:1835:        return fill_model_name
bin/replay_run.py:1845:def build_execution_shadow_results_from_risk_outputs(
bin/replay_run.py:1849:    fill_model_name: str | None,
bin/replay_run.py:1863:            model_name=_resolve_fill_model_name(fill_model_name),
bin/replay_run.py:1877:                    "execution_id": f"execution_shadow_{index:06d}",
bin/replay_run.py:1879:                    "execution_channel": "replay:execution_shadow",
bin/replay_run.py:1909:                "execution_id": f"execution_shadow_{index:06d}",
bin/replay_run.py:1911:                "execution_channel": "replay:execution_shadow",
bin/replay_run.py:2260:    persisted_execution_shadow_results: list[dict[str, Any]] | None = None,
bin/replay_run.py:2318:        "execution_shadow_row_count": len(persisted_execution_shadow_results or ()),
bin/replay_run.py:2319:        "execution_shadow_filled_count": _count_true(persisted_execution_shadow_results or (), "filled"),
bin/replay_run.py:2325:        "execution_shadow_action_breakdown": _value_breakdown(persisted_execution_shadow_results or (), "execution_action"),
bin/replay_run.py:2615:    fill_model_name: str | None,
bin/replay_run.py:2747:        if stage.stage_name == "execution_shadow":
bin/replay_run.py:2749:            execution_results = build_execution_shadow_results_from_risk_outputs(
bin/replay_run.py:2752:                fill_model_name=fill_model_name,
bin/replay_run.py:2759:                transport.publish_execution_shadow_result(execution_result)
bin/replay_run.py:2767:                "mode": "replay_execution_shadow_bridge",
bin/replay_run.py:2772:                "execution_channel": "replay:execution_shadow",
bin/replay_run.py:2773:                "fill_model_name": _resolve_fill_model_name(fill_model_name),
bin/replay_run.py:2934:            fill_model_name=args.fill_model,
bin/replay_run.py:2993:    persisted_execution_shadow_results = [dict(row) for row in transport.execution_shadow_results]
bin/replay_run.py:2995:    (replay_artifacts_dir / "execution_shadow_results.json").write_text(
bin/replay_run.py:2996:        json.dumps(persisted_execution_shadow_results, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n",
bin/replay_run.py:3045:        persisted_execution_shadow_results=persisted_execution_shadow_results,
bin/replay_run.py:3161:    "schema_version": "batch27i_replay_run_risk_execution_shadow_note_v1",
bin/replay_run.py:3162:    "purpose": "future replay_run integration may use replay-only risk_adapter and execution_shadow",
app/mme_scalpx/replay/artifact_materializer.py:21:    "06_execution_shadow_summary.json",
app/mme_scalpx/replay/artifact_materializer.py:131:        "schema_version": "replay_execution_shadow_summary_artifact_v1",
app/mme_scalpx/replay/artifact_materializer.py:133:        "execution_shadow_count": len(results),
app/mme_scalpx/replay/artifact_materializer.py:134:        "filled_qty_total": sum(int(r.get("execution_shadow_summary", {}).get("filled_qty") or 0) for r in results),
app/mme_scalpx/replay/artifact_materializer.py:135:        "net_pnl_total": sum(float(r.get("execution_shadow_summary", {}).get("net_pnl") or 0.0) for r in results),
app/mme_scalpx/replay/artifact_materializer.py:136:        "real_order_sent_count": sum(1 for r in results if r.get("execution_shadow_summary", {}).get("real_order_sent") is True),
app/mme_scalpx/replay/artifact_materializer.py:137:        "broker_calls_executed_count": sum(1 for r in results if r.get("execution_shadow_summary", {}).get("broker_calls_executed") is True),
app/mme_scalpx/replay/artifact_materializer.py:208:        "06_execution_shadow_summary.json": execution_summary,
app/mme_scalpx/replay/artifacts.py:277:    def write_trade_log_csv(
app/mme_scalpx/replay/batch_runner.py:8:from app.mme_scalpx.replay.execution_shadow import (
app/mme_scalpx/replay/batch_runner.py:10:    simulate_replay_execution_shadow,
app/mme_scalpx/replay/batch_runner.py:14:from app.mme_scalpx.replay.risk_adapter import build_replay_risk_decision
app/mme_scalpx/replay/batch_runner.py:391:    execution_shadow = simulate_replay_execution_shadow(
app/mme_scalpx/replay/batch_runner.py:422:        "execution_shadow_summary": {
app/mme_scalpx/replay/batch_runner.py:423:            "fill_policy": execution_shadow.get("fill_policy"),
app/mme_scalpx/replay/batch_runner.py:424:            "fill_status": execution_shadow.get("fill_status"),
app/mme_scalpx/replay/batch_runner.py:425:            "filled_qty": execution_shadow.get("filled_qty"),
app/mme_scalpx/replay/batch_runner.py:426:            "net_pnl": execution_shadow.get("shadow_pnl_summary", {}).get("net_pnl"),
app/mme_scalpx/replay/batch_runner.py:427:            "real_order_sent": execution_shadow.get("real_order_sent"),
app/mme_scalpx/replay/batch_runner.py:428:            "broker_calls_executed": execution_shadow.get("broker_calls_executed"),
app/mme_scalpx/replay/batch_runner.py:446:    total_pnl = sum(float(r.get("execution_shadow_summary", {}).get("net_pnl") or 0.0) for r in results)
app/mme_scalpx/replay/contracts.py:428:    fill_model: str | None = None
app/mme_scalpx/replay/contracts.py:2233:    "execution_shadow_state",
app/mme_scalpx/replay/contracts.py:2301:    "execution_shadow",
app/mme_scalpx/replay/contracts.py:2569:REPLAY_RISK_EXECUTION_SHADOW_CONTRACT_VERSION = "replay_risk_execution_shadow_contract_v1"
app/mme_scalpx/replay/contracts.py:2615:REPLAY_RISK_EXECUTION_SHADOW_CONTRACT_FILE = "etc/replay/schemas/replay_risk_execution_shadow_contract_v1.json"
app/mme_scalpx/replay/contracts.py:2617:def replay_risk_execution_shadow_contract_summary():
app/mme_scalpx/replay/contracts.py:2621:        "execution_shadow_required_fields": REPLAY_EXECUTION_SHADOW_REQUIRED_FIELDS,
app/mme_scalpx/replay/contracts.py:2625:        "execution_shadow_shape": "PROVEN_BY_27I",
app/mme_scalpx/replay/contracts.py:2647:    "replay_risk_execution_shadow_contract_summary",
app/mme_scalpx/replay/contracts.py:2765:    "06_execution_shadow_summary.json",
app/mme_scalpx/replay/contracts.py:2829:    "07_pnl_execution_shadow_summary.csv",
app/mme_scalpx/replay/contracts.py:2830:    "07_pnl_execution_shadow_summary.json",
app/mme_scalpx/replay/engine.py:585:def replay_engine_risk_execution_shadow_plan(*, run_id):
app/mme_scalpx/replay/engine.py:587:    from app.mme_scalpx.replay.execution_shadow import REPLAY_SHADOW_FILL_POLICIES
app/mme_scalpx/replay/engine.py:590:        "schema_version": "replay_engine_risk_execution_shadow_plan_v1",
app/mme_scalpx/replay/engine.py:594:        "execution_shadow_surface": "execution_shadow",
app/mme_scalpx/replay/engine.py:609:    "replay_engine_risk_execution_shadow_plan",
app/mme_scalpx/replay/execution_shadow.py:10:REPLAY_EXECUTION_SHADOW_CONTRACT_VERSION = "replay_execution_shadow_v1"
app/mme_scalpx/replay/execution_shadow.py:77:def simulate_replay_execution_shadow(
app/mme_scalpx/replay/execution_shadow.py:193:        "execution_shadow_shape": "PROVEN_BY_27I",
app/mme_scalpx/replay/execution_shadow.py:199:def validate_replay_execution_shadow(payload: Mapping[str, Any]) -> dict[str, Any]:
app/mme_scalpx/replay/execution_shadow.py:226:def publish_replay_execution_shadow(
app/mme_scalpx/replay/execution_shadow.py:230:    execution_shadow: Mapping[str, Any],
app/mme_scalpx/replay/execution_shadow.py:233:    validation = validate_replay_execution_shadow(execution_shadow)
app/mme_scalpx/replay/execution_shadow.py:238:        surface="execution_shadow",
app/mme_scalpx/replay/execution_shadow.py:239:        row=dict(execution_shadow),
app/mme_scalpx/replay/execution_shadow.py:244:def replay_execution_shadow_contract_summary() -> dict[str, Any]:
app/mme_scalpx/replay/execution_shadow.py:249:        "execution_shadow_shape": "PROVEN_BY_27I",
app/mme_scalpx/replay/execution_shadow.py:272:    "simulate_replay_execution_shadow",
app/mme_scalpx/replay/execution_shadow.py:273:    "validate_replay_execution_shadow",
app/mme_scalpx/replay/execution_shadow.py:274:    "publish_replay_execution_shadow",
app/mme_scalpx/replay/execution_shadow.py:275:    "replay_execution_shadow_contract_summary",
app/mme_scalpx/replay/fill_model.py:2:app/mme_scalpx/replay/fill_model.py
app/mme_scalpx/replay/fill_model.py:40:    """Base exception for replay fill-model failures."""
app/mme_scalpx/replay/fill_model.py:44:    """Raised when fill-model inputs are invalid."""
app/mme_scalpx/replay/fill_model.py:335:def replay_fill_model_shadow_assumption_profiles():
app/mme_scalpx/replay/fill_model.py:336:    """Return replay-only fill policies supported by execution_shadow."""
app/mme_scalpx/replay/fill_model.py:337:    from app.mme_scalpx.replay.execution_shadow import REPLAY_SHADOW_FILL_POLICIES
app/mme_scalpx/replay/fill_model.py:340:        "schema_version": "replay_fill_model_shadow_assumption_profiles_v1",
app/mme_scalpx/replay/fill_model.py:355:    "replay_fill_model_shadow_assumption_profiles",
app/mme_scalpx/replay/live_adapter.py:25:    "execution_shadow": "HASH_STATE_REPLAY_EXECUTION_SHADOW",
app/mme_scalpx/replay/live_parity.py:36:    "risk_execution_shadow_proof",
app/mme_scalpx/replay/live_parity.py:52:    "risk_execution_shadow_parity",
app/mme_scalpx/replay/live_parity.py:120:            "section": "risk_execution_shadow_parity",
app/mme_scalpx/replay/modes.py:62:        "feeds_features_strategy_risk_execution_shadow"
app/mme_scalpx/replay/modes.py:64:    FULL_SYSTEM_REPLAY = "full_system_replay"
app/mme_scalpx/replay/report_exporter.py:30:    "07_pnl_execution_shadow_summary.csv",
app/mme_scalpx/replay/report_exporter.py:31:    "07_pnl_execution_shadow_summary.json",
app/mme_scalpx/replay/report_exporter.py:67:        exec_summary = dict(result.get("execution_shadow_summary") or {})
app/mme_scalpx/replay/report_exporter.py:182:            "filled_qty_total": sum(int(row.get("execution_shadow_summary", {}).get("filled_qty") or 0) for row in subset),
app/mme_scalpx/replay/report_exporter.py:183:            "net_pnl_total": sum(float(row.get("execution_shadow_summary", {}).get("net_pnl") or 0.0) for row in subset),
app/mme_scalpx/replay/report_exporter.py:191:def build_pnl_execution_shadow_summary(simulation_result: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
app/mme_scalpx/replay/report_exporter.py:195:        "filled_qty_total": sum(int(row.get("execution_shadow_summary", {}).get("filled_qty") or 0) for row in results),
app/mme_scalpx/replay/report_exporter.py:196:        "net_pnl_total": sum(float(row.get("execution_shadow_summary", {}).get("net_pnl") or 0.0) for row in results),
app/mme_scalpx/replay/report_exporter.py:197:        "real_order_sent_count": sum(1 for row in results if row.get("execution_shadow_summary", {}).get("real_order_sent") is True),
app/mme_scalpx/replay/report_exporter.py:198:        "broker_calls_executed_count": sum(1 for row in results if row.get("execution_shadow_summary", {}).get("broker_calls_executed") is True),
app/mme_scalpx/replay/report_exporter.py:212:    base_pnl = sum(float(row.get("execution_shadow_summary", {}).get("net_pnl") or 0.0) for row in _results(baseline_result))
app/mme_scalpx/replay/report_exporter.py:213:    shadow_pnl = sum(float(row.get("execution_shadow_summary", {}).get("net_pnl") or 0.0) for row in _results(shadow_result))
app/mme_scalpx/replay/report_exporter.py:288:    pnl_summary = build_pnl_execution_shadow_summary(simulation_result)
app/mme_scalpx/replay/report_exporter.py:379:        "07_pnl_execution_shadow_summary.csv": _write_csv(root / "07_pnl_execution_shadow_summary.csv", pnl_summary, fieldnames=(
app/mme_scalpx/replay/report_exporter.py:384:        "07_pnl_execution_shadow_summary.json": _write_json(root / "07_pnl_execution_shadow_summary.json", pnl_summary),
app/mme_scalpx/replay/report_exporter.py:481:    "build_pnl_execution_shadow_summary",
app/mme_scalpx/replay/reset.py:23:    "execution_shadow_state",
app/mme_scalpx/replay/reset.py:47:    execution_shadow_state: tuple[tuple[str, Any], ...] = field(default_factory=tuple)
app/mme_scalpx/replay/reset.py:77:    execution_shadow_state: Mapping[str, Any] | None = None,
app/mme_scalpx/replay/reset.py:91:        execution_shadow_state=_freeze_mapping(execution_shadow_state),
app/mme_scalpx/replay/risk_adapter.py:10:REPLAY_RISK_ADAPTER_CONTRACT_VERSION = "replay_risk_adapter_v1"
app/mme_scalpx/replay/risk_adapter.py:144:def replay_risk_adapter_contract_summary() -> dict[str, Any]:
app/mme_scalpx/replay/risk_adapter.py:170:    "replay_risk_adapter_contract_summary",
app/mme_scalpx/replay/runner.py:140:    fill_model: str | None = None
app/mme_scalpx/replay/runner.py:300:            fill_model=run_config.fill_model,
app/mme_scalpx/replay/runner.py:483:            "fill_model": manifest.replay.fill_model,
app/mme_scalpx/replay/topology.py:56:STAGE_EXECUTION_SHADOW = "execution_shadow"
app/mme_scalpx/replay/topology.py:386:    execution_shadow_present = STAGE_EXECUTION_SHADOW in stage_names
app/mme_scalpx/replay/topology.py:390:        "execution_shadow_present": execution_shadow_present,
app/mme_scalpx/replay/transport.py:35:    "execution_shadow",

## Expected artifact names from contracts/artifacts
app/mme_scalpx/replay/contracts.py:40:ARTIFACT_DATASET_SUMMARY = "01_dataset_summary.json"
app/mme_scalpx/replay/contracts.py:43:ARTIFACT_METRICS_SUMMARY = "04_metrics_summary.json"
app/mme_scalpx/replay/contracts.py:44:ARTIFACT_TRADE_LOG = "05_trade_log.csv"
app/mme_scalpx/replay/contracts.py:45:ARTIFACT_CANDIDATE_AUDIT = "06_candidate_audit.csv"
app/mme_scalpx/replay/contracts.py:51:ARTIFACT_RUN_SUMMARY_JSON = "10_run_summary.json"
app/mme_scalpx/replay/contracts.py:52:ARTIFACT_RUN_SUMMARY_CSV = "11_run_summary.csv"
app/mme_scalpx/replay/contracts.py:55:ARTIFACT_TRADE_LOG_DETAILED_CSV = "14_trade_log_detailed.csv"
app/mme_scalpx/replay/contracts.py:56:ARTIFACT_CANDIDATE_AUDIT_DETAILED_CSV = "15_candidate_audit_detailed.csv"
app/mme_scalpx/replay/contracts.py:60:ARTIFACT_RESEARCH_SUMMARY_JSON = "19_research_summary.json"
app/mme_scalpx/replay/contracts.py:62:ARTIFACT_COMPARISON_SUMMARY_JSON = "20_comparison_summary.json"
app/mme_scalpx/replay/contracts.py:63:ARTIFACT_COMPARISON_SUMMARY_CSV = "21_comparison_summary.csv"
app/mme_scalpx/replay/contracts.py:126:SHEET_COMPARISON_SUMMARY = "comparison_summary"
app/mme_scalpx/replay/contracts.py:129:SHEET_TRADE_LOG = "trade_log"
app/mme_scalpx/replay/contracts.py:130:SHEET_CANDIDATE_AUDIT = "candidate_audit"
app/mme_scalpx/replay/contracts.py:244:    "pnl_total",
app/mme_scalpx/replay/contracts.py:267:    "baseline_pnl",
app/mme_scalpx/replay/contracts.py:268:    "shadow_pnl",
app/mme_scalpx/replay/contracts.py:269:    "pnl_diff",
app/mme_scalpx/replay/contracts.py:312:    "pnl_impact_hint",
app/mme_scalpx/replay/contracts.py:326:    "pnl",
app/mme_scalpx/replay/contracts.py:366:    "baseline_pnl",
app/mme_scalpx/replay/contracts.py:367:    "shadow_pnl",
app/mme_scalpx/replay/contracts.py:374:    "observation_summary",
app/mme_scalpx/replay/contracts.py:404:    coverage_summary: Mapping[str, Any]
app/mme_scalpx/replay/contracts.py:498:    include_trade_log: bool = True
app/mme_scalpx/replay/contracts.py:499:    include_candidate_audit: bool = True
app/mme_scalpx/replay/contracts.py:556:    pnl_total: float | int | None = None
app/mme_scalpx/replay/contracts.py:580:    baseline_pnl: float | int | None = None
app/mme_scalpx/replay/contracts.py:581:    shadow_pnl: float | int | None = None
app/mme_scalpx/replay/contracts.py:582:    pnl_diff: float | int | None = None
app/mme_scalpx/replay/contracts.py:627:    pnl_impact_hint: str | None = None
app/mme_scalpx/replay/contracts.py:642:    pnl: float | int | None = None
app/mme_scalpx/replay/contracts.py:685:    baseline_pnl: float | int | None = None
app/mme_scalpx/replay/contracts.py:686:    shadow_pnl: float | int | None = None
app/mme_scalpx/replay/contracts.py:694:    observation_summary: str | None = None
app/mme_scalpx/replay/contracts.py:855:def validate_run_summary_row(row: RunSummaryRow) -> None:
app/mme_scalpx/replay/contracts.py:863:def validate_comparison_summary_row(row: ComparisonSummaryRow) -> None:
app/mme_scalpx/replay/contracts.py:1010:    "validate_run_summary_row",
app/mme_scalpx/replay/contracts.py:1011:    "validate_comparison_summary_row",
app/mme_scalpx/replay/contracts.py:2176:def replay_dataset_contract_summary():
app/mme_scalpx/replay/contracts.py:2210:    "replay_dataset_contract_summary",
app/mme_scalpx/replay/contracts.py:2232:    "risk_state",
app/mme_scalpx/replay/contracts.py:2233:    "execution_shadow_state",
app/mme_scalpx/replay/contracts.py:2259:def replay_deterministic_integrity_contract_summary():
app/mme_scalpx/replay/contracts.py:2283:    "replay_deterministic_integrity_contract_summary",
app/mme_scalpx/replay/contracts.py:2300:    "risk_shadow",
app/mme_scalpx/replay/contracts.py:2301:    "execution_shadow",
app/mme_scalpx/replay/contracts.py:2333:def replay_live_shape_transport_contract_summary():
app/mme_scalpx/replay/contracts.py:2357:    "replay_live_shape_transport_contract_summary",
app/mme_scalpx/replay/contracts.py:2440:def replay_feature_family_adapter_contract_summary():
app/mme_scalpx/replay/contracts.py:2469:    "replay_feature_family_adapter_contract_summary",
app/mme_scalpx/replay/contracts.py:2530:def replay_strategy_family_adapter_contract_summary():
app/mme_scalpx/replay/contracts.py:2562:    "replay_strategy_family_adapter_contract_summary",
app/mme_scalpx/replay/contracts.py:2569:REPLAY_RISK_EXECUTION_SHADOW_CONTRACT_VERSION = "replay_risk_execution_shadow_contract_v1"
app/mme_scalpx/replay/contracts.py:2574:    "risk_evaluated",
app/mme_scalpx/replay/contracts.py:2578:    "risk_score",
app/mme_scalpx/replay/contracts.py:2599:    "shadow_trade_log",
app/mme_scalpx/replay/contracts.py:2600:    "shadow_pnl_summary",
app/mme_scalpx/replay/contracts.py:2615:REPLAY_RISK_EXECUTION_SHADOW_CONTRACT_FILE = "etc/replay/schemas/replay_risk_execution_shadow_contract_v1.json"
app/mme_scalpx/replay/contracts.py:2617:def replay_risk_execution_shadow_contract_summary():
app/mme_scalpx/replay/contracts.py:2620:        "risk_required_fields": REPLAY_RISK_REQUIRED_FIELDS,
app/mme_scalpx/replay/contracts.py:2621:        "execution_shadow_required_fields": REPLAY_EXECUTION_SHADOW_REQUIRED_FIELDS,
app/mme_scalpx/replay/contracts.py:2624:        "risk_shape_parity": "PROVEN_BY_27I",
app/mme_scalpx/replay/contracts.py:2625:        "execution_shadow_shape": "PROVEN_BY_27I",
app/mme_scalpx/replay/contracts.py:2626:        "pnl_shadow_math": "PROVEN_BY_27I",
app/mme_scalpx/replay/contracts.py:2647:    "replay_risk_execution_shadow_contract_summary",
app/mme_scalpx/replay/contracts.py:2672:    "forced_risk_veto",
app/mme_scalpx/replay/contracts.py:2686:    "risk_effects",
app/mme_scalpx/replay/contracts.py:2698:def replay_scenario_profile_engine_contract_summary():
app/mme_scalpx/replay/contracts.py:2727:    "replay_scenario_profile_engine_contract_summary",
app/mme_scalpx/replay/contracts.py:2760:    "01_dataset_summary.json",
app/mme_scalpx/replay/contracts.py:2761:    "02_scenario_summary.json",
app/mme_scalpx/replay/contracts.py:2762:    "03_feature_summary.json",
app/mme_scalpx/replay/contracts.py:2763:    "04_strategy_summary.json",
app/mme_scalpx/replay/contracts.py:2764:    "05_risk_summary.json",
app/mme_scalpx/replay/contracts.py:2765:    "06_execution_shadow_summary.json",
app/mme_scalpx/replay/contracts.py:2767:    "08_batch_summary.json",
app/mme_scalpx/replay/contracts.py:2773:def replay_batch_runner_artifact_contract_summary():
app/mme_scalpx/replay/contracts.py:2806:    "replay_batch_runner_artifact_contract_summary",
app/mme_scalpx/replay/contracts.py:2817:    "01_trade_log.csv",
app/mme_scalpx/replay/contracts.py:2818:    "01_trade_log.json",
app/mme_scalpx/replay/contracts.py:2823:    "04_side_split_summary.csv",
app/mme_scalpx/replay/contracts.py:2824:    "04_side_split_summary.json",
app/mme_scalpx/replay/contracts.py:2825:    "05_family_split_summary.csv",
app/mme_scalpx/replay/contracts.py:2826:    "05_family_split_summary.json",
app/mme_scalpx/replay/contracts.py:2827:    "06_scenario_summary.csv",
app/mme_scalpx/replay/contracts.py:2828:    "06_scenario_summary.json",
app/mme_scalpx/replay/contracts.py:2829:    "07_pnl_execution_shadow_summary.csv",
app/mme_scalpx/replay/contracts.py:2830:    "07_pnl_execution_shadow_summary.json",
app/mme_scalpx/replay/contracts.py:2838:def replay_report_export_contract_summary():
app/mme_scalpx/replay/contracts.py:2868:    "replay_report_export_contract_summary",
app/mme_scalpx/replay/contracts.py:2888:    "01_experiment_summary.json",
app/mme_scalpx/replay/contracts.py:2890:    "03_differential_summary.json",
app/mme_scalpx/replay/contracts.py:2891:    "04_parameter_sweep_summary.json",
app/mme_scalpx/replay/contracts.py:2892:    "05_threshold_sweep_summary.json",
app/mme_scalpx/replay/contracts.py:2893:    "06_family_side_summary.json",
app/mme_scalpx/replay/contracts.py:2901:def replay_experiment_workstation_contract_summary():
app/mme_scalpx/replay/contracts.py:2909:        "differential_summary_shape": "PROVEN_BY_27M",
app/mme_scalpx/replay/contracts.py:2935:    "replay_experiment_workstation_contract_summary",
app/mme_scalpx/replay/contracts.py:2946:def replay_live_parity_audit_plan_contract_summary():
app/mme_scalpx/replay/contracts.py:2974:    "replay_live_parity_audit_plan_contract_summary",
app/mme_scalpx/replay/contracts.py:2985:def observe_only_live_evidence_capture_contract_summary():
app/mme_scalpx/replay/contracts.py:3013:    "observe_only_live_evidence_capture_contract_summary",
app/mme_scalpx/replay/artifacts.py:87:from .dataset import dataset_summary_to_dict
app/mme_scalpx/replay/artifacts.py:122:    Canonical result summary for a bundle write.
app/mme_scalpx/replay/artifacts.py:199:    def write_dataset_summary(
app/mme_scalpx/replay/artifacts.py:204:        payload = dataset_summary_to_dict(selection_plan.dataset_summary)
app/mme_scalpx/replay/artifacts.py:205:        return self.write_json_artifact(artifact_plan.dataset_summary_path, payload)
app/mme_scalpx/replay/artifacts.py:234:    def write_metrics_summary_placeholder(
app/mme_scalpx/replay/artifacts.py:238:        metrics: Mapping[str, Any] = {},
app/mme_scalpx/replay/artifacts.py:242:            "metrics": dict(metrics),
app/mme_scalpx/replay/artifacts.py:245:        return self.write_json_artifact(artifact_plan.metrics_summary_path, payload)
app/mme_scalpx/replay/artifacts.py:277:    def write_trade_log_csv(
app/mme_scalpx/replay/artifacts.py:285:            artifact_plan.trade_log_path,
app/mme_scalpx/replay/artifacts.py:290:    def write_candidate_audit_csv(
app/mme_scalpx/replay/artifacts.py:298:            artifact_plan.candidate_audit_path,
app/mme_scalpx/replay/artifacts.py:429:    def _b3_r32_write_candidate_audit_export(self, artifact_plan, strategy_rows):
app/mme_scalpx/replay/artifacts.py:469:        candidate_path = getattr(artifact_plan, "candidate_audit_path", None)
app/mme_scalpx/replay/artifacts.py:472:            candidate_path = Path(getattr(artifact_plan, "artifacts_dir", getattr(artifact_plan, "root_dir", "."))) / "candidate_audit.csv"
app/mme_scalpx/replay/artifacts.py:537:        replay decisions, broker/order behavior, paper/live behavior, risk,
app/mme_scalpx/replay/artifacts.py:725:                "basis": "reward for first target equals target_points in export summary",
app/mme_scalpx/replay/artifacts.py:755:                "basis": "reward for first target equals target_ticks in export summary",
app/mme_scalpx/replay/artifacts.py:788:                "Do not claim paper/live, broker/order, risk/execution, or profitability readiness from this enrichment.",
app/mme_scalpx/replay/artifacts.py:793:    def _b3_r32_write_economics_summary_export(self, artifact_plan, strategy_rows, features_rows):
app/mme_scalpx/replay/artifacts.py:826:            "schema_version": "b3_r32_economics_summary_v1",
app/mme_scalpx/replay/artifacts.py:853:        path = Path(getattr(artifact_plan, "artifacts_dir", getattr(artifact_plan, "root_dir", "."))) / "economics_summary.json"
app/mme_scalpx/replay/artifacts.py:857:    def _b3_r32_write_family_side_summary_export(self, artifact_plan, strategy_rows):
app/mme_scalpx/replay/artifacts.py:902:        path = Path(getattr(artifact_plan, "artifacts_dir", getattr(artifact_plan, "root_dir", "."))) / "family_side_summary.csv"
app/mme_scalpx/replay/artifacts.py:913:        broker/order paths, or touch paper/live/risk/execution.
app/mme_scalpx/replay/artifacts.py:933:                for p in root.rglob("economics_summary.json"):
app/mme_scalpx/replay/artifacts.py:987:        def _find_candidate_audit_file(run_dir, artifacts_dir):
app/mme_scalpx/replay/artifacts.py:991:                root / "06_candidate_audit.csv",
app/mme_scalpx/replay/artifacts.py:992:                root / "candidate_audit.csv",
app/mme_scalpx/replay/artifacts.py:993:                artifacts / "06_candidate_audit.csv",
app/mme_scalpx/replay/artifacts.py:994:                artifacts / "candidate_audit.csv",
app/mme_scalpx/replay/artifacts.py:1072:            candidate_path = _find_candidate_audit_file(run_dir, artifacts_dir)
app/mme_scalpx/replay/artifacts.py:1074:            family_side_path = _find_named_file(run_dir, artifacts_dir, "family_side_summary.csv")
app/mme_scalpx/replay/artifacts.py:1075:            economics_path = _find_named_file(run_dir, artifacts_dir, "economics_summary.json")
app/mme_scalpx/replay/artifacts.py:1122:                "economics_summary_present": bool(isinstance(economics, dict) and economics),
app/mme_scalpx/replay/artifacts.py:1128:                "economics_summary_path": str(economics_path),
app/mme_scalpx/replay/artifacts.py:1129:                "economics_summary": economics,
app/mme_scalpx/replay/artifacts.py:1147:                "No Redis, broker/order, paper/live, risk/execution side effects.",
app/mme_scalpx/replay/artifacts.py:1153:            "schema_version": "b3_r53_combined_economics_summary_v1",
app/mme_scalpx/replay/artifacts.py:1164:            "per_day_summary": _write_csv(
app/mme_scalpx/replay/artifacts.py:1165:                out_dir / "per_day_summary.csv",
app/mme_scalpx/replay/artifacts.py:1167:                ["source_date", "source_run_dir", "artifacts_dir", "integrity_verdict", "candidate_rows", "blocker_rows", "family_side_rows", "economics_summary_present"],
app/mme_scalpx/replay/artifacts.py:1169:            "combined_candidate_audit": _write_csv(
app/mme_scalpx/replay/artifacts.py:1170:                out_dir / "combined_candidate_audit.csv",
app/mme_scalpx/replay/artifacts.py:1179:            "combined_family_side_summary": _write_csv(
app/mme_scalpx/replay/artifacts.py:1180:                out_dir / "combined_family_side_summary.csv",
app/mme_scalpx/replay/artifacts.py:1184:            "combined_economics_summary": _write_json(out_dir / "combined_economics_summary.json", combined_economics),
app/mme_scalpx/replay/artifacts.py:1204:        broker/order behavior, paper/live behavior, risk, or execution.
app/mme_scalpx/replay/artifacts.py:1222:            candidate_rows = self._b3_r32_write_candidate_audit_export(artifact_plan, strategy_rows)
app/mme_scalpx/replay/artifacts.py:1224:            economics_payload = self._b3_r32_write_economics_summary_export(artifact_plan, strategy_rows, features_rows)
app/mme_scalpx/replay/artifacts.py:1225:            family_side_rows = self._b3_r32_write_family_side_summary_export(artifact_plan, strategy_rows)
app/mme_scalpx/replay/artifacts.py:1235:                "candidate_audit_rows": len(candidate_rows),
app/mme_scalpx/replay/artifacts.py:1237:                "family_side_summary_rows": len(family_side_rows),
app/mme_scalpx/replay/artifacts.py:1260:        metrics: Mapping[str, Any] = {},
app/mme_scalpx/replay/artifacts.py:1261:        metrics_notes: Sequence[str] = (),
app/mme_scalpx/replay/artifacts.py:1270:            self.write_dataset_summary(run_context.selection_plan, artifact_plan).path
app/mme_scalpx/replay/artifacts.py:1288:            self.write_metrics_summary_placeholder(
app/mme_scalpx/replay/artifacts.py:1290:                metrics=metrics,
app/mme_scalpx/replay/artifacts.py:1291:                notes=metrics_notes,
app/mme_scalpx/replay/artifacts.py:1341:        artifact_plan.dataset_summary_path,
app/mme_scalpx/replay/artifacts.py:1344:        artifact_plan.metrics_summary_path,
app/mme_scalpx/replay/artifacts.py:1422:        "dataset_summary_path",
app/mme_scalpx/replay/artifacts.py:1425:        "metrics_summary_path",
app/mme_scalpx/replay/artifacts.py:1426:        "trade_log_path",
app/mme_scalpx/replay/artifacts.py:1427:        "candidate_audit_path",
app/mme_scalpx/replay/execution_shadow.py:10:REPLAY_EXECUTION_SHADOW_CONTRACT_VERSION = "replay_execution_shadow_v1"
app/mme_scalpx/replay/execution_shadow.py:31:    "shadow_trade_log",
app/mme_scalpx/replay/execution_shadow.py:32:    "shadow_pnl_summary",
app/mme_scalpx/replay/execution_shadow.py:77:def simulate_replay_execution_shadow(
app/mme_scalpx/replay/execution_shadow.py:81:    risk_decision: Mapping[str, Any],
app/mme_scalpx/replay/execution_shadow.py:95:    research_allowed = risk_decision.get("research_trade_allowed") is True
app/mme_scalpx/replay/execution_shadow.py:96:    risk_vetoed = risk_decision.get("entry_vetoed") is True
app/mme_scalpx/replay/execution_shadow.py:98:    if risk_vetoed or not research_allowed:
app/mme_scalpx/replay/execution_shadow.py:118:    net_pnl = net_points * filled_qty
app/mme_scalpx/replay/execution_shadow.py:141:        "net_pnl": net_pnl,
app/mme_scalpx/replay/execution_shadow.py:158:    pnl_summary = {
app/mme_scalpx/replay/execution_shadow.py:159:        "schema_version": "replay_shadow_pnl_summary_v1",
app/mme_scalpx/replay/execution_shadow.py:165:        "net_pnl": net_pnl,
app/mme_scalpx/replay/execution_shadow.py:166:        "is_profit": net_pnl > 0,
app/mme_scalpx/replay/execution_shadow.py:167:        "is_loss": net_pnl < 0,
app/mme_scalpx/replay/execution_shadow.py:182:        "shadow_trade_log": (shadow_trade,),
app/mme_scalpx/replay/execution_shadow.py:183:        "shadow_pnl_summary": pnl_summary,
app/mme_scalpx/replay/execution_shadow.py:184:        "risk_vetoed": risk_vetoed,
app/mme_scalpx/replay/execution_shadow.py:193:        "execution_shadow_shape": "PROVEN_BY_27I",
app/mme_scalpx/replay/execution_shadow.py:199:def validate_replay_execution_shadow(payload: Mapping[str, Any]) -> dict[str, Any]:
app/mme_scalpx/replay/execution_shadow.py:211:    pnl_ok = isinstance(payload.get("shadow_pnl_summary"), Mapping)
app/mme_scalpx/replay/execution_shadow.py:212:    trade_log_ok = isinstance(payload.get("shadow_trade_log"), tuple)
app/mme_scalpx/replay/execution_shadow.py:214:    ok = bool(not missing and fill_policy_ok and no_real_order_ok and pnl_ok and trade_log_ok and position_ok)
app/mme_scalpx/replay/execution_shadow.py:220:        "pnl_ok": pnl_ok,
app/mme_scalpx/replay/execution_shadow.py:221:        "trade_log_ok": trade_log_ok,
app/mme_scalpx/replay/execution_shadow.py:226:def publish_replay_execution_shadow(
app/mme_scalpx/replay/execution_shadow.py:230:    execution_shadow: Mapping[str, Any],
app/mme_scalpx/replay/execution_shadow.py:233:    validation = validate_replay_execution_shadow(execution_shadow)
app/mme_scalpx/replay/execution_shadow.py:238:        surface="execution_shadow",
app/mme_scalpx/replay/execution_shadow.py:239:        row=dict(execution_shadow),
app/mme_scalpx/replay/execution_shadow.py:244:def replay_execution_shadow_contract_summary() -> dict[str, Any]:
app/mme_scalpx/replay/execution_shadow.py:249:        "execution_shadow_shape": "PROVEN_BY_27I",
app/mme_scalpx/replay/execution_shadow.py:250:        "pnl_shadow_math": "PROVEN_BY_27I",
app/mme_scalpx/replay/execution_shadow.py:272:    "simulate_replay_execution_shadow",
app/mme_scalpx/replay/execution_shadow.py:273:    "validate_replay_execution_shadow",
app/mme_scalpx/replay/execution_shadow.py:274:    "publish_replay_execution_shadow",
app/mme_scalpx/replay/execution_shadow.py:275:    "replay_execution_shadow_contract_summary",
app/mme_scalpx/replay/metrics.py:2:app/mme_scalpx/replay/metrics.py
app/mme_scalpx/replay/metrics.py:4:Replay comparison metrics for baseline-vs-shadow studies.
app/mme_scalpx/replay/metrics.py:15:    """Base error for replay metrics handling."""
app/mme_scalpx/replay/metrics.py:51:def compute_comparison_metrics(
app/mme_scalpx/replay/metrics.py:173:def comparison_metrics_to_dict(bundle: ComparisonMetricsBundle) -> dict[str, Any]:
app/mme_scalpx/replay/metrics.py:335:    "comparison_metrics_to_dict",
app/mme_scalpx/replay/metrics.py:336:    "compute_comparison_metrics",

## Fill model supported names
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ImportError: cannot import name 'build_replay_fill_model' from 'app.mme_scalpx.replay.fill_model' (/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/replay/fill_model.py)
FILL_RC=1

CLASSIFICATION=PASS_R3A_EXACT_R4_SHADOW_REPLAY_PLAN_READY
