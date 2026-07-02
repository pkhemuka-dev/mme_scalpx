# R35C_R5C_SUMMARY_SYNTHETIC_PNL_AGGREGATION_PATCH_NO_REPLAY_NO_ORDER_20260614_003429

classification: PASS_R35C_R5C_SUMMARY_SYNTHETIC_PNL_AGGREGATION_PATCHED_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35C_R5C_SUMMARY_SYNTHETIC_PNL_AGGREGATION_PATCH_NO_REPLAY_NO_ORDER_20260614_003429.json`
backup: `run/_code_backups/R35C_R5C_SUMMARY_SYNTHETIC_PNL_AGGREGATION_PATCH_NO_REPLAY_NO_ORDER_20260614_003429_bin_replay_run.py.bak`

patch_rc=0 compile_rc=0 marker_rc=0
safety pre=0/0/0 post=0/0/0 proc=0/0 replay_proc=0

## Patch log
patched=1

## Patch errors

## Markers
2776:    # R35C/R5C: aggregate replay-only synthetic PnL into official summary.
2779:    shadow_pnl_total = 0.0
2780:    shadow_win_count = 0
2781:    shadow_loss_count = 0
2782:    shadow_pnl_model = None
2783:    shadow_pnl_model_status_counts: dict[str, int] = {}
2796:            shadow_pnl_model_status_counts[_status] = shadow_pnl_model_status_counts.get(_status, 0) + 1
2799:        if _model and shadow_pnl_model is None:
2800:            shadow_pnl_model = str(_model)
2807:        shadow_pnl_total += _pnl
2809:            shadow_win_count += 1
2811:            shadow_loss_count += 1
2813:    shadow_pnl_total = round(shadow_pnl_total, 6)
2843:        "pnl_total": shadow_pnl_total,
2845:        "win_count": shadow_win_count,
2846:        "loss_count": shadow_loss_count,
2849:        "shadow_pnl_total": shadow_pnl_total,
2850:        "shadow_win_count": shadow_win_count,
2851:        "shadow_loss_count": shadow_loss_count,
2852:        "shadow_pnl_model": shadow_pnl_model,
2853:        "shadow_pnl_model_status_counts": shadow_pnl_model_status_counts,
2854:        "pnl_accounting_status": "PNL_COMPUTED_REPLAY_ONLY_SYNTHETIC_SHADOW_MODEL_R35C_R5C_NOT_BROKER_NOT_PAPER_NOT_LIVE",

## Summary builder context
  2708	        row.setdefault("veto_reason", None)
  2709	        row.setdefault("side", row.get("side_fallback"))
  2710	        row.setdefault("entry_mode", row.get("entry_mode_fallback"))
  2711	        row.setdefault("candidate", row.get("candidate_fallback"))
  2712	        row.setdefault("regime_pass", row.get("regime_pass_fallback"))
  2713	        row.setdefault("economics_valid", row.get("economics_valid_fallback"))
  2714	        row.setdefault("blocker_name", row.get("blocker_name_fallback"))
  2715	        row.setdefault("blocker_reason", row.get("blocker_reason_fallback"))
  2716	
  2717	        rows.append(row)
  2718	
  2719	    return rows
  2720	
  2721	
  2722	
  2723	def _count_true(rows: list[dict[str, Any]] | tuple[dict[str, Any], ...], key: str) -> int:
  2724	    return sum(1 for row in rows if row.get(key) is True)
  2725	
  2726	
  2727	def _count_non_null(rows: list[dict[str, Any]] | tuple[dict[str, Any], ...], key: str) -> int:
  2728	    return sum(1 for row in rows if row.get(key) is not None)
  2729	
  2730	
  2731	def _value_breakdown(
  2732	    rows: list[dict[str, Any]] | tuple[dict[str, Any], ...],
  2733	    key: str,
  2734	) -> dict[str, int]:
  2735	    counts: dict[str, int] = {}
  2736	    for row in rows:
  2737	        value = row.get(key)
  2738	        if value is None:
  2739	            continue
  2740	        label = str(value)
  2741	        counts[label] = counts.get(label, 0) + 1
  2742	    return dict(sorted(counts.items()))
  2743	
  2744	
  2745	
  2746	def build_run_summary_payload(
  2747	    *,
  2748	    run_context,
  2749	    report_bundle,
  2750	    engine_result,
  2751	    integrity_bundle,
  2752	    persisted_feature_rows: list[dict[str, Any]],
  2753	    persisted_strategy_decisions: list[dict[str, Any]],
  2754	    persisted_risk_outputs: list[dict[str, Any]],
  2755	    persisted_execution_shadow_results: list[dict[str, Any]] | None = None,
  2756	) -> dict[str, Any]:
  2757	    manifest = run_context.manifest
  2758	    replay = manifest.replay
  2759	    profiles = manifest.profiles
  2760	    experiment = manifest.experiment
  2761	    selection = run_context.selection_plan
  2762	
  2763	    window_start = selection.intraday_window.start if selection.intraday_window else None
  2764	    window_end = selection.intraday_window.end if selection.intraday_window else None
  2765	
  2766	    integrity_waivers = list(getattr(run_context.run_config, "integrity_waivers", ()))
  2767	    notes = list(report_bundle.notes)
  2768	
  2769	    # R35C/R4W: official summary uses replay shadow filled count as shadow trade count.
  2770	    # This is summary/export-only. It does not create broker orders, paper/live orders,
  2771	    # Redis writes, risk starts, execution starts, or PnL claims.
  2772	    execution_shadow_rows = list(persisted_execution_shadow_results or ())
  2773	    shadow_trade_count = _count_true(execution_shadow_rows, "filled")
  2774	    shadow_filled_qty_total = 0
  2775	
  2776	    # R35C/R5C: aggregate replay-only synthetic PnL into official summary.
  2777	    # This only summarizes execution_shadow rows already produced by replay.
  2778	    # It is not broker PnL, not paper/live PnL, and does not create any order.
  2779	    shadow_pnl_total = 0.0
  2780	    shadow_win_count = 0
  2781	    shadow_loss_count = 0
  2782	    shadow_pnl_model = None
  2783	    shadow_pnl_model_status_counts: dict[str, int] = {}
  2784	
  2785	    for _row in execution_shadow_rows:
  2786	        try:
  2787	            shadow_filled_qty_total += int(_row.get("fill_qty") or 0)
  2788	        except Exception:

## Compile log
