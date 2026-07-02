# R35C_R4W_SUMMARY_SHADOW_TRADE_COUNT_PATCH_NO_REPLAY_NO_ORDER_20260613_235922

classification: PASS_R35C_R4W_SUMMARY_SHADOW_TRADE_COUNT_PATCHED_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35C_R4W_SUMMARY_SHADOW_TRADE_COUNT_PATCH_NO_REPLAY_NO_ORDER_20260613_235922.json`
backup: `run/_code_backups/R35C_R4W_SUMMARY_SHADOW_TRADE_COUNT_PATCH_NO_REPLAY_NO_ORDER_20260613_235922_bin_replay_run.py.bak`

patch_rc=0 compile_rc=0 marker_rc=0
safety pre=0/0/0 post=0/0/0 proc=0/0 replay_proc=0

## Patch log
patched=1

## Patch errors

## Markers
2712:    # R35C/R4W: official summary uses replay shadow filled count as shadow trade count.
2716:    shadow_trade_count = _count_true(execution_shadow_rows, "filled")
2717:    shadow_filled_qty_total = 0
2720:            shadow_filled_qty_total += int(_row.get("fill_qty") or 0)
2753:        "trade_count": shadow_trade_count,
2756:        "shadow_trade_count": shadow_trade_count,
2757:        "shadow_filled_qty_total": shadow_filled_qty_total,
2758:        "pnl_accounting_status": "PNL_NOT_COMPUTED_EXECUTION_SHADOW_HAS_ENTRY_FILL_ONLY_NO_EXIT_MODEL_R35C_R4W",
2772:        "execution_shadow_filled_count": shadow_trade_count,

## Summary builder context
  2705	
  2706	    window_start = selection.intraday_window.start if selection.intraday_window else None
  2707	    window_end = selection.intraday_window.end if selection.intraday_window else None
  2708	
  2709	    integrity_waivers = list(getattr(run_context.run_config, "integrity_waivers", ()))
  2710	    notes = list(report_bundle.notes)
  2711	
  2712	    # R35C/R4W: official summary uses replay shadow filled count as shadow trade count.
  2713	    # This is summary/export-only. It does not create broker orders, paper/live orders,
  2714	    # Redis writes, risk starts, execution starts, or PnL claims.
  2715	    execution_shadow_rows = list(persisted_execution_shadow_results or ())
  2716	    shadow_trade_count = _count_true(execution_shadow_rows, "filled")
  2717	    shadow_filled_qty_total = 0
  2718	    for _row in execution_shadow_rows:
  2719	        try:
  2720	            shadow_filled_qty_total += int(_row.get("fill_qty") or 0)
  2721	        except Exception:
  2722	            pass
  2723	
  2724	    return {
  2725	        "run_id": run_context.run_id,
  2726	        "created_at": run_context.created_at,
  2727	        "started_at": getattr(engine_result, "engine_started_at", None),
  2728	        "completed_at": getattr(engine_result, "engine_finished_at", None),
  2729	        "duration_ms": None,
  2730	        "chapter": "replay",
  2731	        "doctrine_mode": run_context.doctrine_mode.value,
  2732	        "replay_scope": replay.scope.value,
  2733	        "speed_mode": replay.speed_mode.value,
  2734	        "side_mode": replay.side_mode.value,
  2735	        "dataset_id": manifest.dataset.dataset_id,
  2736	        "dataset_fingerprint": manifest.dataset.dataset_fingerprint,
  2737	        "selection_mode": selection.selection_mode.value,
  2738	        "trading_dates": list(selection.trading_dates),
  2739	        "window_start": window_start,
  2740	        "window_end": window_end,
  2741	        "dataset_profile": profiles.dataset_profile,
  2742	        "replay_profile": profiles.replay_profile,
  2743	        "experiment_profile": profiles.experiment_profile,
  2744	        "batch_profile": profiles.batch_profile,
  2745	        "forensic_profile": profiles.forensic_profile,
  2746	        "integrity_profile": profiles.integrity_profile,
  2747	        "override_pack_id": experiment.override_pack_id,
  2748	        "shadow_label": experiment.shadow_label,
  2749	        "input_fingerprint": selection.selection_fingerprint,
  2750	        "integrity_verdict": integrity_bundle.verdict.value,
  2751	        "waiver_count": len(integrity_waivers),
  2752	        "pnl_total": None,
  2753	        "trade_count": shadow_trade_count,
  2754	        "win_count": 0,
  2755	        "loss_count": 0,
  2756	        "shadow_trade_count": shadow_trade_count,
  2757	        "shadow_filled_qty_total": shadow_filled_qty_total,
  2758	        "pnl_accounting_status": "PNL_NOT_COMPUTED_EXECUTION_SHADOW_HAS_ENTRY_FILL_ONLY_NO_EXIT_MODEL_R35C_R4W",
  2759	        "candidate_count": _count_true(persisted_strategy_decisions, "candidate"),
  2760	        "blocker_count": _count_non_null(persisted_strategy_decisions, "blocker_name"),
  2761	        "regime_pass_count": _count_true(persisted_strategy_decisions, "regime_pass"),
  2762	        "remarks": "; ".join(notes) if notes else None,
  2763	        "operator_verdict": None,
  2764	        "research_tags": [],
  2765	        "ml_export_eligible": False,
  2766	
  2767	        "stage_count": engine_result.stage_count,
  2768	        "feature_row_count": len(persisted_feature_rows),

## Compile log
