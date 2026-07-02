# R35C_R4U_OFFICIAL_PNL_TRADE_ACCOUNTING_ROOT_CAUSE_AUDIT_NO_REPLAY_NO_ORDER_20260613_234914

classification: PASS_R35C_R4U_OFFICIAL_PNL_TRADE_ACCOUNTING_ROOT_CAUSE_AUDIT_DONE_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35C_R4U_OFFICIAL_PNL_TRADE_ACCOUNTING_ROOT_CAUSE_AUDIT_NO_REPLAY_NO_ORDER_20260613_234914.json`

run_dir: `run/replay/r35c_r4t/20260613_233414/replay_locked_single_day_r35c_r4t_20260601_20260613_180423_f4c647f0`
summary: `run/replay/r35c_r4t/20260613_233414/replay_locked_single_day_r35c_r4t_20260601_20260613_180423_f4c647f0/artifacts/10_run_summary.json`
engine: `run/replay/r35c_r4t/20260613_233414/replay_locked_single_day_r35c_r4t_20260601_20260613_180423_f4c647f0/artifacts/engine_result.json`
execution: `run/replay/r35c_r4t/20260613_233414/replay_locked_single_day_r35c_r4t_20260601_20260613_180423_f4c647f0/artifacts/execution_shadow_results.json`

audit_rc=0
safety pre=0/0/0 post=0/0/0 proc=0/0 replay_proc=0

## Artifact accounting audit
{
  "artifact_lengths": {
    "execution_json_type": "list",
    "execution_rows_visible_after_cap": 50,
    "risk_rows_visible_after_cap": 50,
    "strategy_rows_visible_after_cap": 50
  },
  "economics_summary": {
    "authority_candidates": {
      "stop_points": [
        {
          "line": 1212,
          "path": "app/mme_scalpx/core/models.py",
          "text": "_require_float(self.stop_points, \"stop_points\", min_value=0.0)",
          "value": 0.0
        },
        {
          "line": 154,
          "path": "app/mme_scalpx/services/features.py",
          "text": "DEFAULT_STOP_POINTS: Final[float] = 4.0",
          "value": 4.0
        },
        {
          "line": 49,
          "path": "app/mme_scalpx/services/feature_family/miso_surface.py",
          "text": "DEFAULT_HARD_STOP_POINTS: Final[float] = 4.0",
          "value": 4.0
        },
        {
          "line": 50,
          "path": "app/mme_scalpx/services/feature_family/miso_surface.py",
          "text": "DEFAULT_DISASTER_STOP_POINTS: Final[float] = 5.0",
          "value": 5.0
        },
        {
          "line": 80,
          "path": "app/mme_scalpx/services/strategy_family/misb.py",
          "text": "HARD_STOP_POINTS: Final[float] = 4.0",
          "value": 4.0
        },
        {
          "line": 81,
          "path": "app/mme_scalpx/services/strategy_family/misc.py",
          "text": "HARD_STOP_POINTS: Final[float] = 4.0",
          "value": 4.0
        },
        {
          "line": 81,
          "path": "app/mme_scalpx/services/strategy_family/misr.py",
          "text": "HARD_STOP_POINTS: Final[float] = 4.0",
          "value": 4.0
        },
        {
          "line": 81,
          "path": "app/mme_scalpx/services/strategy_family/mist.py",
          "text": "HARD_STOP_POINTS: Final[float] = 4.0",
          "value": 4.0
        },
        {
          "line": 81,
          "path": "app/mme_scalpx/services/strategy_family/miso.py",
          "text": "HARD_STOP_POINTS: Final[float] = 4.0",
          "value": 4.0
        },
        {
          "line": 141,
          "path": "etc/research_gate/raw_doctrine_economics_authority_map.json",
          "text": "\"proof_trade_shell states TARGET_POINTS = 5 and HARD_STOP_POINTS = 4\",",
          "value": 5.0
        },
        {
          "line": 148,
          "path": "etc/research_gate/raw_doctrine_economics_authority_map.json",
          "text": "\"Profit / Stop / Ratchet states TARGET_POINTS = 5.0 and HARD_STOP_POINTS = 4.0\",",
          "value": 5.0
        },
        {
          "line": 156,
          "path": "etc/research_gate/raw_doctrine_economics_authority_map.json",
          "text": "\"Target, Stop, and Cooldown states TARGET_POINTS = 5 and HARD_STOP_POINTS = 4\",",
          "value": 5.0
        },
        {
          "line": 163,
          "path": "etc/research_gate/raw_doctrine_economics_authority_map.json",
          "text": "\"Layer B / Target, Stop, Cooldown states TARGET_POINTS = 5 and HARD_STOP_POINTS = 4\",",
          "value": 5.0
        }
      ],
      "target_points": [
        {
          "line": 1232,
          "path": "app/mme_scalpx/core/models.py",
          "text": "_require_float(self.target_points, \"target_points\", min_value=0.0)",
          "value": 0.0
        },
        {
          "line": 153,
          "path": "app/mme_scalpx/services/features.py",
          "text": "DEFAULT_TARGET_POINTS: Final[float] = 5.0",
          "value": 5.0
        },
        {
          "line": 48,
          "path": "app/mme_scalpx/services/feature_family/miso_surface.py",
          "text": "DEFAULT_TARGET_POINTS: Final[float] = 5.0",
          "value": 5.0
        },
        {
          "line": 79,
          "path": "app/mme_scalpx/services/strategy_family/misb.py",
          "text": "TARGET_POINTS: Final[float] = 5.0",
          "value": 5.0
        },
        {
          "line": 80,
          "path": "app/mme_scalpx/services/strategy_family/misc.py",
          "text": "TARGET_POINTS: Final[float] = 5.0",
          "value": 5.0
        },
        {
          "line": 80,
          "path": "app/mme_scalpx/services/strategy_family/misr.py",
          "text": "TARGET_POINTS: Final[float] = 5.0",
          "value": 5.0
        },
        {
          "line": 80,
          "path": "app/mme_scalpx/services/strategy_family/mist.py",
          "text": "TARGET_POINTS: Final[float] = 5.0",
          "value": 5.0
        },
        {
          "line": 80,
          "path": "app/mme_scalpx/services/strategy_family/miso.py",
          "text": "TARGET_POINTS: Final[float] = 5.0",
          "value": 5.0
        },
        {
          "line": 141,
          "path": "etc/research_gate/raw_doctrine_economics_authority_map.json",
          "text": "\"proof_trade_shell states TARGET_POINTS = 5 and HARD_STOP_POINTS = 4\",",
          "value": 5.0
        },
        {
          "line": 148,
          "path": "etc/research_gate/raw_doctrine_economics_authority_map.json",
          "text": "\"Profit / Stop / Ratchet states TARGET_POINTS = 5.0 and HARD_STOP_POINTS = 4.0\",",
          "value": 5.0
        },
        {
          "line": 156,
          "path": "etc/research_gate/raw_doctrine_economics_authority_map.json",
          "text": "\"Target, Stop, and Cooldown states TARGET_POINTS = 5 and HARD_STOP_POINTS = 4\",",
          "value": 5.0
        },
        {
          "line": 163,
          "path": "etc/research_gate/raw_doctrine_economics_authority_map.json",
          "text": "\"Layer B / Target, Stop, Cooldown states TARGET_POINTS = 5 and HARD_STOP_POINTS = 4\",",
          "value": 5.0
        }
      ],
      "tick_size": [
        {
          "line": 953,
          "path": "app/mme_scalpx/core/models.py",
          "text": "tick_size: float = 0.0",
          "value": 0.0
        },
        {
          "line": 977,
          "path": "app/mme_scalpx/core/models.py",
          "text": "_require_float(self.tick_size, \"tick_size\", min_value=0.0)",
          "value": 0.0
        },
        {
          "line": 414,
          "path": "app/mme_scalpx/research_capture/normalizer.py",
          "text": "tick_size=float(_coerce_float(_first_present(ref, \"tick_size\", default=0.05), default=0.05)),",
          "value": 0.05
        },
        {
          "line": 81,
          "path": "app/mme_scalpx/services/strategy_family/misb.py",
          "text": "DEFAULT_TICK_SIZE: Final[float] = 0.05",
          "value": 0.05
        },
        {
          "line": 82,
          "path": "app/mme_scalpx/services/strategy_family/misc.py",
          "text": "DEFAULT_TICK_SIZE: Final[float] = 0.05",
          "value": 0.05
        },
        {
          "line": 82,
          "path": "app/mme_scalpx/services/strategy_family/misr.py",
          "text": "DEFAULT_TICK_SIZE: Final[float] = 0.05",
          "value": 0.05
        },
        {
          "line": 82,
          "path": "app/mme_scalpx/services/strategy_family/mist.py",
          "text": "DEFAULT_TICK_SIZE: Final[float] = 0.05",
          "value": 0.05
        },
        {
          "line": 460,
          "path": "app/mme_scalpx/services/strategy_family/doctrine_runtime.py",
          "text": "tick_size: float = 0.05",
          "value": 0.05
        },
        {
          "line": 82,
          "path": "app/mme_scalpx/services/strategy_family/miso.py",
          "text": "DEFAULT_TICK_SIZE: Final[float] = 0.05",
          "value": 0.05
        },
        {
          "line": 155,
          "path": "etc/research_gate/raw_doctrine_economics_authority_map.json",
          "text": "\"Layer B states FUT_TICK_SIZE = 0.05\",",
          "value": 0.05
        }
      ]
    },
    "economics_reason_counts": {},
    "enriched_field_values": {
      "reward_cost_ratio": 1.25,
      "reward_points": 5.0,
      "reward_ticks": 100.0,
      "stop_points": 4.0,
      "stop_ticks": 80.0,
      "target_points": 5.0,
      "target_ticks": 100.0,
      "tick_size": 0.05
    },
    "enrichment_schema_version": "b3_r43_economics_export_enrichment_v1",
    "enrichment_sources": {
      "reward_cost_ratio": {
        "formula": "target_points / stop_points",
        "source_type": "derived_from_same_unit_basis",
        "stop_points": 4.0,
        "target_points": 5.0
      },
      "reward_points": {
        "basis": "reward for first target equals target_points in export summary",
        "source_type": "derived_same_as_target_points"
      },
      "reward_ticks": {
        "basis": "reward for first target equals target_ticks in export summary",
        "source_type": "derived_same_as_target_ticks"
      },
      "stop_points": {
        "line": 80,
        "path": "app/mme_scalpx/services/strategy_family/misb.py",
        "source_type": "source_assignment_candidate",
        "text": "HARD_STOP_POINTS: Final[float] = 4.0",
        "value": 4.0
      },

## Artifact audit errors

## Source locator
## source grep: trade_count / pnl_total / economics_summary / execution_shadow_filled_count
bin/replay_build_comparison_summary.py:170:    baseline_pnl = _as_float_or_none(b.get("pnl_total"))
bin/replay_build_comparison_summary.py:171:    shadow_pnl = _as_float_or_none(s.get("pnl_total"))
bin/replay_build_comparison_summary.py:173:    baseline_trade_count = _as_int(b.get("trade_count"))
bin/replay_build_comparison_summary.py:174:    shadow_trade_count = _as_int(s.get("trade_count"))
bin/replay_build_comparison_summary.py:205:        "baseline_trade_count": baseline_trade_count,
bin/replay_build_comparison_summary.py:206:        "shadow_trade_count": shadow_trade_count,
bin/replay_build_comparison_summary.py:207:        "trade_count_diff": shadow_trade_count - baseline_trade_count,
bin/lane_x_r32i_materialize_internal_order_intent_from_replay_results_no_broker.py:247:            "execution_sim_filled_count": 0,
bin/lane_x_r32i_materialize_internal_order_intent_from_replay_results_no_broker.py:285:        and summary.get("execution_sim_filled_count", 0) > 0
bin/proof_risk_restart_rebuild.py:25:        "loss_count_and_pnl_surfaces",
bin/proof_replay_optimization_d6_leaderboard.py:223:if sample_row.get("trade_count") != 0:
bin/replay_run.py:2740:        "pnl_total": None,
bin/replay_run.py:2741:        "trade_count": 0,
bin/replay_run.py:2742:        "win_count": 0,
bin/replay_run.py:2743:        "loss_count": 0,
bin/replay_run.py:2757:        "execution_shadow_filled_count": _count_true(persisted_execution_shadow_results or (), "filled"),
bin/replay_run.py:3195:            filled_count = 0
bin/replay_run.py:3200:                    filled_count += 1
bin/replay_run.py:3209:                "filled_count": filled_count,
bin/proof_r32d_internal_order_intent_pipeline_no_broker.py:132:        and summary["execution_sim_filled_count"] == 2
bin/proof_r32g_real_candidate_hold_normalizer_no_broker.py:122:        and summary.get("execution_sim_filled_count") == 20
bin/proof_risk_batch14_freeze.py:304:        and service.ledger.loss_count == 1
bin/proof_risk_batch14_freeze.py:308:            "loss_count": service.ledger.loss_count,
bin/proof_risk_batch14_freeze.py:401:        and restart_service.ledger.loss_count == 1,
bin/proof_risk_batch14_freeze.py:405:            "loss_count": restart_service.ledger.loss_count,
bin/raw_strategy_rank.py:28:        min_family_trade_count=args.min_family_trades,
app/mme_scalpx/research_capture/enricher.py:776:            "trade_count_proxy": len(history_plus_current),
app/mme_scalpx/research_capture/contracts.py:566:        ("trade_count_proxy", "int", LD, OPT, LIVE, RES, (AP,), "Trade count proxy", ()),
app/mme_scalpx/replay_optimization/leaderboard.py:129:                trade_count=0,
app/mme_scalpx/replay_optimization/leaderboard.py:130:                win_count=0,
app/mme_scalpx/replay_optimization/leaderboard.py:131:                loss_count=0,
app/mme_scalpx/replay_optimization/leaderboard.py:219:            "trade_count": 0,
app/mme_scalpx/replay_optimization/leaderboard.py:235:            "trade_count",
app/mme_scalpx/replay_optimization/contracts.py:188:    "trade_count",
app/mme_scalpx/replay_optimization/contracts.py:189:    "win_count",
app/mme_scalpx/replay_optimization/contracts.py:190:    "loss_count",
app/mme_scalpx/replay_optimization/contracts.py:337:    trade_count: int
app/mme_scalpx/replay_optimization/contracts.py:338:    win_count: int
app/mme_scalpx/replay_optimization/contracts.py:339:    loss_count: int
app/mme_scalpx/replay/dataset.py:1246:def _economics_summary_collect_declared_field_names(value):
app/mme_scalpx/replay/dataset.py:1479:        for field_name in _economics_summary_collect_declared_field_names(dataset_summary.get(key)):
app/mme_scalpx/replay/dataset.py:1504:    economics_summary = build_economics_source_summary_for_dataset(
app/mme_scalpx/replay/dataset.py:1510:    enriched["economics_source_mode"] = economics_summary["source_mode"]
app/mme_scalpx/replay/dataset.py:1511:    enriched["economics_source_status"] = economics_summary["source_status"]
app/mme_scalpx/replay/dataset.py:1512:    enriched["economics_eligible_for_evaluation"] = economics_summary["eligible_for_economics_evaluation"]
app/mme_scalpx/replay/dataset.py:1514:        economics_summary["missing_required_fields"]
app/mme_scalpx/replay/dataset.py:1516:    enriched["economics_source_summary"] = economics_summary
app/mme_scalpx/replay/artifact_materializer.py:135:        "net_pnl_total": sum(float(r.get("execution_shadow_summary", {}).get("net_pnl") or 0.0) for r in results),
app/mme_scalpx/replay/execution_shadow.py:161:        "trade_count": 1 if filled_qty else 0,
app/mme_scalpx/replay/raw_trade_family_backfill.py:247:    trade_count = 0
app/mme_scalpx/replay/raw_trade_family_backfill.py:254:    trade_backfilled_count = 0
app/mme_scalpx/replay/raw_trade_family_backfill.py:261:        trade_count += 1
app/mme_scalpx/replay/raw_trade_family_backfill.py:283:            trade_backfilled_count += 1
app/mme_scalpx/replay/raw_trade_family_backfill.py:292:    family_trade_counts = Counter()
app/mme_scalpx/replay/raw_trade_family_backfill.py:295:            family_trade_counts[norm_upper(row.get("family")) or "UNKNOWN"] += 1
app/mme_scalpx/replay/raw_trade_family_backfill.py:304:        "trade_count": trade_count,
app/mme_scalpx/replay/raw_trade_family_backfill.py:311:        "trade_backfilled_count": trade_backfilled_count,
app/mme_scalpx/replay/raw_trade_family_backfill.py:312:        "trade_family_unknown_ratio_after": round(1.0 - (trade_family_after / max(trade_count, 1)), 6),
app/mme_scalpx/replay/raw_trade_family_backfill.py:313:        "family_trade_counts": dict(sorted(family_trade_counts.items())),
app/mme_scalpx/replay/raw_trade_family_backfill.py:314:        "rank_candidate_family_count": sum(1 for k, v in family_trade_counts.items() if k in FAMILIES and v >= 3),
app/mme_scalpx/replay/raw_trade_family_backfill.py:348:        "trade_count": trade_count,
app/mme_scalpx/replay/raw_trade_family_backfill.py:355:        "trade_backfilled_count": trade_backfilled_count,
app/mme_scalpx/replay/raw_trade_family_backfill.py:358:        "family_trade_counts": summary["family_trade_counts"],
app/mme_scalpx/replay/artifacts.py:793:    def _b3_r32_write_economics_summary_export(self, artifact_plan, strategy_rows, features_rows):
app/mme_scalpx/replay/artifacts.py:826:            "schema_version": "b3_r32_economics_summary_v1",
app/mme_scalpx/replay/artifacts.py:853:        path = Path(getattr(artifact_plan, "artifacts_dir", getattr(artifact_plan, "root_dir", "."))) / "economics_summary.json"
app/mme_scalpx/replay/artifacts.py:933:                for p in root.rglob("economics_summary.json"):
app/mme_scalpx/replay/artifacts.py:1075:            economics_path = _find_named_file(run_dir, artifacts_dir, "economics_summary.json")
app/mme_scalpx/replay/artifacts.py:1122:                "economics_summary_present": bool(isinstance(economics, dict) and economics),
app/mme_scalpx/replay/artifacts.py:1128:                "economics_summary_path": str(economics_path),
app/mme_scalpx/replay/artifacts.py:1129:                "economics_summary": economics,
app/mme_scalpx/replay/artifacts.py:1153:            "schema_version": "b3_r53_combined_economics_summary_v1",
app/mme_scalpx/replay/artifacts.py:1167:                ["source_date", "source_run_dir", "artifacts_dir", "integrity_verdict", "candidate_rows", "blocker_rows", "family_side_rows", "economics_summary_present"],
app/mme_scalpx/replay/artifacts.py:1184:            "combined_economics_summary": _write_json(out_dir / "combined_economics_summary.json", combined_economics),
app/mme_scalpx/replay/artifacts.py:1224:            economics_payload = self._b3_r32_write_economics_summary_export(artifact_plan, strategy_rows, features_rows)
app/mme_scalpx/replay/contracts.py:244:    "pnl_total",
app/mme_scalpx/replay/contracts.py:245:    "trade_count",
app/mme_scalpx/replay/contracts.py:246:    "win_count",
app/mme_scalpx/replay/contracts.py:247:    "loss_count",
app/mme_scalpx/replay/contracts.py:270:    "baseline_trade_count",
app/mme_scalpx/replay/contracts.py:271:    "shadow_trade_count",
app/mme_scalpx/replay/contracts.py:272:    "trade_count_diff",
app/mme_scalpx/replay/contracts.py:556:    pnl_total: float | int | None = None
app/mme_scalpx/replay/contracts.py:557:    trade_count: int = 0
app/mme_scalpx/replay/contracts.py:558:    win_count: int = 0
app/mme_scalpx/replay/contracts.py:559:    loss_count: int = 0
app/mme_scalpx/replay/contracts.py:583:    baseline_trade_count: int = 0
app/mme_scalpx/replay/contracts.py:584:    shadow_trade_count: int = 0
app/mme_scalpx/replay/contracts.py:585:    trade_count_diff: int = 0
app/mme_scalpx/replay/report_exporter.py:183:            "net_pnl_total": sum(float(row.get("execution_shadow_summary", {}).get("net_pnl") or 0.0) for row in subset),
app/mme_scalpx/replay/report_exporter.py:196:        "net_pnl_total": sum(float(row.get("execution_shadow_summary", {}).get("net_pnl") or 0.0) for row in results),
app/mme_scalpx/replay/report_exporter.py:375:            "net_pnl_total", "paper_armed_approved", "live_trading_approved",
app/mme_scalpx/replay/report_exporter.py:380:            "result_count", "filled_qty_total", "net_pnl_total", "real_order_sent_count",
app/mme_scalpx/replay/raw_label_enricher.py:277:        "missed_trade_count": missed,
app/mme_scalpx/replay/raw_label_enricher.py:324:        "missed_trade_count": missed,
app/mme_scalpx/services/feature_family/miso_microstructure.py:611:        "aggressive_trade_count": int(flow_stats["favorable_count"]),
app/mme_scalpx/services/feature_family/miso_microstructure.py:612:        "counter_trade_count": int(flow_stats["unfavorable_count"]),
app/mme_scalpx/services/risk.py:457:    loss_count: int = 0
app/mme_scalpx/services/risk.py:458:    win_count: int = 0
app/mme_scalpx/services/risk.py:468:        self.loss_count = 0
app/mme_scalpx/services/risk.py:469:        self.win_count = 0
app/mme_scalpx/services/risk.py:799:            self.ledger.loss_count += 1
app/mme_scalpx/services/risk.py:805:            self.ledger.win_count += 1
app/mme_scalpx/services/risk.py:932:            "day_loss_count": str(self.ledger.loss_count),
app/mme_scalpx/services/risk.py:933:            "day_win_count": str(self.ledger.win_count),
app/mme_scalpx/services/risk.py:1387:    self.ledger.loss_count = _safe_int(raw.get("day_loss_count"), 0)
app/mme_scalpx/services/risk.py:1388:    self.ledger.win_count = _safe_int(raw.get("day_win_count"), 0)
app/mme_scalpx/services/risk.py:1805:            self.ledger.loss_count += 1
app/mme_scalpx/services/risk.py:1811:            self.ledger.win_count += 1
app/mme_scalpx/services/risk.py:2051:        "day_loss_count": str(self.ledger.loss_count),
app/mme_scalpx/services/risk.py:2052:        "day_win_count": str(self.ledger.win_count),
app/mme_scalpx/services/strategy_family/internal_order_intent_pipeline.py:303:        "execution_sim_filled_count": sum(1 for r in ledgers["execution_sim_shadow"] if r.get("execution_status") == "FILLED_SIM_SHADOW"),
app/mme_scalpx/services/report.py:536:    trade_count: int = 0
app/mme_scalpx/services/report.py:537:    closed_trade_count: int = 0
app/mme_scalpx/services/report.py:538:    open_trade_count: int = 0
app/mme_scalpx/services/report.py:540:    win_count: int = 0
app/mme_scalpx/services/report.py:541:    loss_count: int = 0
app/mme_scalpx/services/report.py:980:        report.trade_count = len(trades)
app/mme_scalpx/services/report.py:981:        report.closed_trade_count = sum(1 for trade in trades if trade.closed)
app/mme_scalpx/services/report.py:982:        report.open_trade_count = report.trade_count - report.closed_trade_count
app/mme_scalpx/services/report.py:989:        report.win_count = len(wins)
app/mme_scalpx/services/report.py:990:        report.loss_count = len(losses)
app/mme_scalpx/services/report.py:1041:        lines.append(f"- Trades: {session_report.trade_count}")
app/mme_scalpx/services/report.py:1042:        lines.append(f"- Closed trades: {session_report.closed_trade_count}")
app/mme_scalpx/services/report.py:1043:        lines.append(f"- Open trades: {session_report.open_trade_count}")
app/mme_scalpx/services/report.py:1044:        lines.append(f"- Wins: {session_report.win_count}")
app/mme_scalpx/services/report.py:1045:        lines.append(f"- Losses: {session_report.loss_count}")
app/mme_scalpx/research_gate/post_raw_s_replay_rerun.py:179:            "trade_count": baseline_q.get("trade_count"),
app/mme_scalpx/research_gate/post_raw_s_replay_rerun.py:186:            "trade_count": baseline_r.get("trade_count"),
app/mme_scalpx/research_gate/post_raw_s_replay_rerun.py:187:            "known_family_trade_count": baseline_r.get("known_family_trade_count"),
app/mme_scalpx/research_gate/post_raw_s_replay_rerun.py:188:            "unknown_family_trade_count": baseline_r.get("unknown_family_trade_count"),
app/mme_scalpx/research_gate/post_raw_s_replay_rerun.py:193:            "trade_count": after_q_summary.get("trade_count"),
app/mme_scalpx/research_gate/post_raw_s_replay_rerun.py:196:            "trade_backfilled_count": after_q_summary.get("trade_backfilled_count"),
app/mme_scalpx/research_gate/post_raw_s_replay_rerun.py:202:            "trade_count": after_r.get("trade_count"),
app/mme_scalpx/research_gate/post_raw_s_replay_rerun.py:203:            "known_family_trade_count": after_r.get("known_family_trade_count"),
app/mme_scalpx/research_gate/post_raw_s_replay_rerun.py:204:            "unknown_family_trade_count": after_r.get("unknown_family_trade_count"),
app/mme_scalpx/research_gate/pnl.py:403:        "trade_count": 0,
app/mme_scalpx/research_gate/pnl.py:422:    bucket["trade_count"] += 1
app/mme_scalpx/research_gate/pnl.py:435:    count = bucket["trade_count"]
app/mme_scalpx/research_gate/pnl.py:522:    trade_count = total["trade_count"]
app/mme_scalpx/research_gate/pnl.py:525:    if trade_count <= 0:
app/mme_scalpx/research_gate/pnl.py:528:    elif trade_count < 5:
app/mme_scalpx/research_gate/pnl.py:571:            "If trade_count is zero, verdict remains insufficient trade evidence instead of inventing results.",
app/mme_scalpx/research_gate/pnl.py:617:        f"- trade_count: {s['trade_count']}",
app/mme_scalpx/research_gate/pnl.py:677:        "trade_count": report["summary"]["trade_count"],
app/mme_scalpx/research_gate/forensics.py:573:        "missed_trade_count": 0,
app/mme_scalpx/research_gate/forensics.py:593:        bucket["missed_trade_count"] += 1
app/mme_scalpx/research_gate/forensics.py:612:        bucket["missed_trade_rate"] = round(bucket["missed_trade_count"] / count, 6)
app/mme_scalpx/research_gate/forensics.py:676:        and total["missed_trade_count"] == 0
app/mme_scalpx/research_gate/forensics.py:814:        f"- missed_trade_count: {s['missed_trade_count']}",
app/mme_scalpx/research_gate/forensics.py:881:            "missed_trade_count",
app/mme_scalpx/research_gate/forensics.py:909:            "missed_trade_count",
app/mme_scalpx/research_gate/forensics.py:940:        "missed_trade_count": s["missed_trade_count"],
app/mme_scalpx/research_gate/replay_verdict.py:96:    trade_count = _safe_int(raw_e.get("trade_count"))
app/mme_scalpx/research_gate/replay_verdict.py:109:        "pnl_positive": net_pnl > 0 and trade_count > 0,
app/mme_scalpx/research_gate/replay_verdict.py:110:        "pnl_negative": net_pnl < 0 and trade_count > 0,
app/mme_scalpx/research_gate/replay_verdict.py:169:    if trade_count <= 0:
app/mme_scalpx/research_gate/replay_verdict.py:235:            "trade_count": trade_count,
app/mme_scalpx/research_gate/replay_verdict.py:262:            "missed_trade_count": raw_h.get("missed_trade_count"),
app/mme_scalpx/research_gate/replay_verdict.py:327:        f"- trade_count: {report['raw_e_pnl']['trade_count']}",
app/mme_scalpx/research_gate/unknown_trade_lineage.py:431:            "unknown_trade_count": count,
app/mme_scalpx/research_gate/unknown_trade_lineage.py:449:        "trade_count": len(trades),
app/mme_scalpx/research_gate/unknown_trade_lineage.py:450:        "unknown_trade_count": len(unknown_trades),
app/mme_scalpx/research_gate/unknown_trade_lineage.py:468:def lineage_verdict(trade_count: int, unknown_count: int, patch_targets: list[dict[str, Any]]) -> str:
app/mme_scalpx/research_gate/unknown_trade_lineage.py:469:    if trade_count <= 0:
app/mme_scalpx/research_gate/unknown_trade_lineage.py:505:    lines.append(f"- trade_count: {trace['trade_count']}")
app/mme_scalpx/research_gate/unknown_trade_lineage.py:506:    lines.append(f"- unknown_trade_count: {trace['unknown_trade_count']}")
app/mme_scalpx/research_gate/unknown_trade_lineage.py:517:            f"unknown_trades={target['unknown_trade_count']} "
app/mme_scalpx/research_gate/unknown_trade_lineage.py:597:        "unknown_trade_count",
app/mme_scalpx/research_gate/unknown_trade_lineage.py:605:        {"source_artifact": source, "unknown_trade_count": count}
app/mme_scalpx/research_gate/unknown_trade_lineage.py:608:    write_csv(source_artifacts_csv, source_rows, ["source_artifact", "unknown_trade_count"])
app/mme_scalpx/research_gate/unknown_trade_lineage.py:643:        "trade_count": trace["trade_count"],
app/mme_scalpx/research_gate/unknown_trade_lineage.py:644:        "unknown_trade_count": trace["unknown_trade_count"],
app/mme_scalpx/research_gate/strategy_rank.py:48:    trade_count: int
app/mme_scalpx/research_gate/strategy_rank.py:100:def _confidence(trade_count: int, bucket_name: str, *, min_trade_count: int) -> str:
app/mme_scalpx/research_gate/strategy_rank.py:103:    if trade_count <= 0:
app/mme_scalpx/research_gate/strategy_rank.py:105:    if trade_count < min_trade_count:
app/mme_scalpx/research_gate/strategy_rank.py:107:    if trade_count < max(min_trade_count * 3, 10):
app/mme_scalpx/research_gate/strategy_rank.py:112:def _score_bucket(bucket: dict[str, Any], bucket_name: str, *, min_trade_count: int) -> tuple[float, str, str]:
app/mme_scalpx/research_gate/strategy_rank.py:113:    trade_count = _safe_int(bucket.get("trade_count"))
app/mme_scalpx/research_gate/strategy_rank.py:120:    conf = _confidence(trade_count, bucket_name, min_trade_count=min_trade_count)
app/mme_scalpx/research_gate/strategy_rank.py:121:    sample_factor = min(trade_count / max(float(min_trade_count), 1.0), 1.0)
app/mme_scalpx/research_gate/strategy_rank.py:126:        + (expectancy * max(trade_count, 1) * 0.25)
app/mme_scalpx/research_gate/strategy_rank.py:134:    if trade_count < min_trade_count:
app/mme_scalpx/research_gate/strategy_rank.py:145:    min_trade_count: int,
app/mme_scalpx/research_gate/strategy_rank.py:151:        score, conf, notes = _score_bucket(bucket, name, min_trade_count=min_trade_count)
app/mme_scalpx/research_gate/strategy_rank.py:156:                trade_count=_safe_int(bucket.get("trade_count")),
app/mme_scalpx/research_gate/strategy_rank.py:168:    rows.sort(key=lambda r: (r.rank_score, r.net_pnl_after_costs, r.trade_count), reverse=True)
app/mme_scalpx/research_gate/strategy_rank.py:174:        "trade_count": 0,
app/mme_scalpx/research_gate/strategy_rank.py:185:    count = bucket["trade_count"]
app/mme_scalpx/research_gate/strategy_rank.py:232:        bucket["trade_count"] += 1
app/mme_scalpx/research_gate/strategy_rank.py:263:        bucket["trade_count"] += 1
app/mme_scalpx/research_gate/strategy_rank.py:279:def _best_labeled(rows: list[RankRow], *, min_trade_count: int) -> dict[str, Any] | None:
app/mme_scalpx/research_gate/strategy_rank.py:283:        if row.trade_count < min_trade_count:
app/mme_scalpx/research_gate/strategy_rank.py:290:    candidates = [r for r in rows if r.bucket_name != UNKNOWN and r.trade_count > 0]
app/mme_scalpx/research_gate/strategy_rank.py:298:    total = _safe_int(pnl_report.get("summary", {}).get("trade_count"))
app/mme_scalpx/research_gate/strategy_rank.py:317:    min_family_trade_count: int = 3,
app/mme_scalpx/research_gate/strategy_rank.py:321:    trade_count = _safe_int(summary.get("trade_count"))
app/mme_scalpx/research_gate/strategy_rank.py:328:        min_trade_count=min_family_trade_count,
app/mme_scalpx/research_gate/strategy_rank.py:333:        min_trade_count=min_family_trade_count,
app/mme_scalpx/research_gate/strategy_rank.py:338:        min_trade_count=min_family_trade_count,
app/mme_scalpx/research_gate/strategy_rank.py:343:        min_trade_count=min_family_trade_count,
app/mme_scalpx/research_gate/strategy_rank.py:349:    best_family = _best_labeled(family_rank, min_trade_count=min_family_trade_count)
app/mme_scalpx/research_gate/strategy_rank.py:351:    best_side = _best_labeled(side_rank, min_trade_count=min_family_trade_count)
app/mme_scalpx/research_gate/strategy_rank.py:355:    if trade_count <= 0:
app/mme_scalpx/research_gate/strategy_rank.py:397:        "min_family_trade_count": min_family_trade_count,
app/mme_scalpx/research_gate/strategy_rank.py:502:    min_family_trade_count: int = 3,
app/mme_scalpx/research_gate/strategy_rank.py:510:        min_family_trade_count=min_family_trade_count,
app/mme_scalpx/research_gate/strategy_rank.py:526:            "trade_count",
app/mme_scalpx/research_gate/strategy_rank.py:548:            "trade_count",
app/mme_scalpx/research_gate/family_gap_review.py:125:        "trade_count": 0,
app/mme_scalpx/research_gate/family_gap_review.py:139:    bucket["trade_count"] += 1
app/mme_scalpx/research_gate/family_gap_review.py:153:    count = int(bucket["trade_count"])
app/mme_scalpx/research_gate/family_gap_review.py:211:    known_family_trades = sum(data["trade_count"] for fam, data in finalized.items() if fam != "UNKNOWN")
app/mme_scalpx/research_gate/family_gap_review.py:212:    unknown_family_trades = finalized.get("UNKNOWN", {}).get("trade_count", 0)
app/mme_scalpx/research_gate/family_gap_review.py:213:    known_family_count = sum(1 for fam, data in finalized.items() if fam != "UNKNOWN" and data["trade_count"] > 0)
app/mme_scalpx/research_gate/family_gap_review.py:214:    rank_candidate_family_count = sum(1 for fam, data in finalized.items() if fam != "UNKNOWN" and data["trade_count"] >= 3)
app/mme_scalpx/research_gate/family_gap_review.py:219:        if fam != "UNKNOWN" and data["trade_count"] > 0
app/mme_scalpx/research_gate/family_gap_review.py:221:    ranked.sort(key=lambda x: (x["net_pnl_after_costs"], x["expectancy"], x["trade_count"]), reverse=True)
app/mme_scalpx/research_gate/family_gap_review.py:266:        "trade_count": len(trades),
app/mme_scalpx/research_gate/family_gap_review.py:267:        "known_family_trade_count": known_family_trades,
app/mme_scalpx/research_gate/family_gap_review.py:268:        "unknown_family_trade_count": unknown_family_trades,
app/mme_scalpx/research_gate/family_gap_review.py:302:def review_verdict(trade_count: int, unknown_family_trade_count: int, rank_candidate_family_count: int) -> str:
app/mme_scalpx/research_gate/family_gap_review.py:303:    if trade_count <= 0:
app/mme_scalpx/research_gate/family_gap_review.py:305:    if rank_candidate_family_count >= 5 and unknown_family_trade_count == 0:
app/mme_scalpx/research_gate/family_gap_review.py:353:            "unknown_trade_count": count,
app/mme_scalpx/research_gate/family_gap_review.py:360:            "unknown_trade_count": count,
app/mme_scalpx/research_gate/family_gap_review.py:363:    fieldnames = ["summary_type", "key", "unknown_trade_count", "suggested_fix"]
app/mme_scalpx/research_gate/family_gap_review.py:384:            f"- {family}: trades={data['trade_count']}, net={data['net_pnl_after_costs']}, "
app/mme_scalpx/research_gate/family_gap_review.py:389:    lines.append(f"- trade_count: {review['trade_count']}")
app/mme_scalpx/research_gate/family_gap_review.py:390:    lines.append(f"- known_family_trade_count: {review['known_family_trade_count']}")
app/mme_scalpx/research_gate/family_gap_review.py:391:    lines.append(f"- unknown_family_trade_count: {review['unknown_family_trade_count']}")
app/mme_scalpx/research_gate/family_gap_review.py:477:        "trade_count": review["trade_count"],
app/mme_scalpx/research_gate/family_gap_review.py:478:        "known_family_trade_count": review["known_family_trade_count"],
app/mme_scalpx/research_gate/family_gap_review.py:479:        "unknown_family_trade_count": review["unknown_family_trade_count"],
app/mme_scalpx/research_gate/enriched_rerun.py:160:        "trade_count": 0,
app/mme_scalpx/research_gate/enriched_rerun.py:174:    bucket["trade_count"] += 1
app/mme_scalpx/research_gate/enriched_rerun.py:188:    count = int(bucket["trade_count"])
app/mme_scalpx/research_gate/enriched_rerun.py:254:    verdict = "PNL_PASS_POSITIVE" if total["net_pnl_after_costs"] > 0 else "PNL_REJECT_NEGATIVE" if total["trade_count"] > 0 else "PNL_INSUFFICIENT_TRADES"
app/mme_scalpx/research_gate/enriched_rerun.py:255:    research_verdict = "RESEARCH_ONLY_POSITIVE" if total["net_pnl_after_costs"] > 0 else "REJECT_NEGATIVE_EXPECTANCY" if total["trade_count"] > 0 else "INCONCLUSIVE_DATA_INSUFFICIENT"
app/mme_scalpx/research_gate/enriched_rerun.py:263:        "trade_count": total["trade_count"],
app/mme_scalpx/research_gate/enriched_rerun.py:285:        if family != UNKNOWN and int(data.get("trade_count", 0)) >= 3
app/mme_scalpx/research_gate/enriched_rerun.py:399:        "missed_trade_count": len(missed),
app/mme_scalpx/research_gate/enriched_rerun.py:413:    if pnl["trade_count"] <= 0:
app/mme_scalpx/research_gate/enriched_rerun.py:498:        "enriched_trade_count": pnl["trade_count"],
app/mme_scalpx/research_gate/enriched_rerun.py:540:        f"- enriched_trade_count: {comparison['enriched_trade_count']}",
app/mme_scalpx/research_gate/enriched_rerun.py:626:        "trade_count": pnl["trade_count"],

## replay_run summary builder context
2689:def build_run_summary_payload(
2740:        "pnl_total": None,
2741:        "trade_count": 0,
2757:        "execution_shadow_filled_count": _count_true(persisted_execution_shadow_results or (), "filled"),

## replay_run likely summary builder lines 2680-2765
  2680	        value = row.get(key)
  2681	        if value is None:
  2682	            continue
  2683	        label = str(value)
  2684	        counts[label] = counts.get(label, 0) + 1
  2685	    return dict(sorted(counts.items()))
  2686	
  2687	
  2688	
  2689	def build_run_summary_payload(
  2690	    *,
  2691	    run_context,
  2692	    report_bundle,
  2693	    engine_result,
  2694	    integrity_bundle,
  2695	    persisted_feature_rows: list[dict[str, Any]],
  2696	    persisted_strategy_decisions: list[dict[str, Any]],
  2697	    persisted_risk_outputs: list[dict[str, Any]],
  2698	    persisted_execution_shadow_results: list[dict[str, Any]] | None = None,
  2699	) -> dict[str, Any]:
  2700	    manifest = run_context.manifest
  2701	    replay = manifest.replay
  2702	    profiles = manifest.profiles
  2703	    experiment = manifest.experiment
  2704	    selection = run_context.selection_plan
  2705	
  2706	    window_start = selection.intraday_window.start if selection.intraday_window else None
  2707	    window_end = selection.intraday_window.end if selection.intraday_window else None
  2708	
  2709	    integrity_waivers = list(getattr(run_context.run_config, "integrity_waivers", ()))
  2710	    notes = list(report_bundle.notes)
  2711	
  2712	    return {
  2713	        "run_id": run_context.run_id,
  2714	        "created_at": run_context.created_at,
  2715	        "started_at": getattr(engine_result, "engine_started_at", None),
  2716	        "completed_at": getattr(engine_result, "engine_finished_at", None),
  2717	        "duration_ms": None,
  2718	        "chapter": "replay",
  2719	        "doctrine_mode": run_context.doctrine_mode.value,
  2720	        "replay_scope": replay.scope.value,
  2721	        "speed_mode": replay.speed_mode.value,
  2722	        "side_mode": replay.side_mode.value,
  2723	        "dataset_id": manifest.dataset.dataset_id,
  2724	        "dataset_fingerprint": manifest.dataset.dataset_fingerprint,
  2725	        "selection_mode": selection.selection_mode.value,
  2726	        "trading_dates": list(selection.trading_dates),
  2727	        "window_start": window_start,
  2728	        "window_end": window_end,
  2729	        "dataset_profile": profiles.dataset_profile,
  2730	        "replay_profile": profiles.replay_profile,
  2731	        "experiment_profile": profiles.experiment_profile,
  2732	        "batch_profile": profiles.batch_profile,
  2733	        "forensic_profile": profiles.forensic_profile,
  2734	        "integrity_profile": profiles.integrity_profile,
  2735	        "override_pack_id": experiment.override_pack_id,
  2736	        "shadow_label": experiment.shadow_label,
  2737	        "input_fingerprint": selection.selection_fingerprint,
  2738	        "integrity_verdict": integrity_bundle.verdict.value,
  2739	        "waiver_count": len(integrity_waivers),
  2740	        "pnl_total": None,
  2741	        "trade_count": 0,
  2742	        "win_count": 0,
  2743	        "loss_count": 0,
  2744	        "candidate_count": _count_true(persisted_strategy_decisions, "candidate"),
  2745	        "blocker_count": _count_non_null(persisted_strategy_decisions, "blocker_name"),
  2746	        "regime_pass_count": _count_true(persisted_strategy_decisions, "regime_pass"),
  2747	        "remarks": "; ".join(notes) if notes else None,
  2748	        "operator_verdict": None,
  2749	        "research_tags": [],
  2750	        "ml_export_eligible": False,
  2751	
  2752	        "stage_count": engine_result.stage_count,
  2753	        "feature_row_count": len(persisted_feature_rows),
  2754	        "strategy_row_count": len(persisted_strategy_decisions),
  2755	        "risk_row_count": len(persisted_risk_outputs),
  2756	        "execution_shadow_row_count": len(persisted_execution_shadow_results or ()),
  2757	        "execution_shadow_filled_count": _count_true(persisted_execution_shadow_results or (), "filled"),
  2758	
  2759	        "feature_side_breakdown": _value_breakdown(persisted_feature_rows, "side"),
  2760	        "feature_leg_breakdown": _value_breakdown(persisted_feature_rows, "leg"),
  2761	        "strategy_action_breakdown": _value_breakdown(persisted_strategy_decisions, "decision_action"),
  2762	        "risk_action_breakdown": _value_breakdown(persisted_risk_outputs, "risk_action"),
  2763	        "execution_shadow_action_breakdown": _value_breakdown(persisted_execution_shadow_results or (), "execution_action"),
  2764	
  2765	        "feature_candidate_true_count": _count_true(persisted_feature_rows, "candidate"),

## replay_run artifact/summary write lines 3540-3655
  3540	
  3541	            return obj
  3542	
  3543	        return slim(value)
  3544	
  3545	    def _r35b_write_compact_json(path, value):
  3546	        # R35C/R4J2: hard top-level row cap before JSON serialization.
  3547	        # R35B/R4S slimmed nested payloads, but R4H proved top-level row files
  3548	        # could still become multi-hundred-MB. This is artifact-only.
  3549	        try:
  3550	            hard_cap = int(os.environ.get("SCALPX_REPLAY_ARTIFACT_ROW_CAP", "0") or "0")
  3551	        except Exception:
  3552	            hard_cap = 0
  3553	
  3554	        # R35C/R4R2: force default cap for known row artifact files.
  3555	        # Artifact-only guard: if env cap is missing inside recursive replay,
