# R35C_R4V_EXECUTION_SHADOW_PNL_SCHEMA_AND_SUMMARY_PATCH_PLAN_NO_REPLAY_NO_ORDER_20260613_235337

classification: PASS_R35C_R4V_EXECUTION_SHADOW_PNL_SCHEMA_AUDIT_DONE_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35C_R4V_EXECUTION_SHADOW_PNL_SCHEMA_AND_SUMMARY_PATCH_PLAN_NO_REPLAY_NO_ORDER_20260613_235337.json`

run_dir: `run/replay/r35c_r4t/20260613_233414/replay_locked_single_day_r35c_r4t_20260601_20260613_180423_f4c647f0`
summary: `run/replay/r35c_r4t/20260613_233414/replay_locked_single_day_r35c_r4t_20260601_20260613_180423_f4c647f0/artifacts/10_run_summary.json`
engine: `run/replay/r35c_r4t/20260613_233414/replay_locked_single_day_r35c_r4t_20260601_20260613_180423_f4c647f0/artifacts/engine_result.json`
execution: `run/replay/r35c_r4t/20260613_233414/replay_locked_single_day_r35c_r4t_20260601_20260613_180423_f4c647f0/artifacts/execution_shadow_results.json`

audit_rc=0
safety pre=0/0/0 post=0/0/0 proc=0/0 replay_proc=0

## Execution shadow schema audit
{
  "engine_execution_stage": {
    "execution_channel": "replay:execution_shadow",
    "execution_results_published": 131368,
    "fill_model_name": "immediate_market",
    "filled_count": 4222,
    "mode": "replay_execution_shadow_bridge",
    "run_id": "replay_locked_single_day_r35c_r4t_20260601_20260613_180423_f4c647f0",
    "source_risk_outputs": 131368,
    "stage_name": "execution_shadow",
    "status": "ok"
  },
  "execution_counts": {
    "entry_price": {
      "<MISSING>": 50
    },
    "execution_action": {
      "<MISSING>": 50
    },
    "execution_status": {
      "<MISSING>": 50
    },
    "exit_price": {
      "<MISSING>": 50
    },
    "fill_price": {
      "124.75": 1,
      "125.05": 1,
      "68.6": 1,
      "69.1": 1,
      "None": 46
    },
    "fill_qty": {
      "0": 46,
      "1": 4
    },
    "filled": {
      "False": 46,
      "True": 4
    },
    "net_pnl": {
      "<MISSING>": 50
    },
    "pnl": {
      "<MISSING>": 50
    },
    "pnl_points": {
      "<MISSING>": 50
    },
    "pnl_total": {
      "<MISSING>": 50
    },
    "realized_pnl": {
      "<MISSING>": 50
    },
    "risk_action": {
      "ENTER_CALL": 2,
      "ENTER_PUT": 2,
      "HOLD": 46
    },
    "selected_leg": {
      "<MISSING>": 50
    },
    "side": {
      "<MISSING>": 50
    },
    "status": {
      "<MISSING>": 50
    },
    "symbol": {
      "NIFTY2660223500PE": 12,
      "NIFTY2660223550CE": 10,
      "NIFTY2660223550PE": 9,
      "NIFTY2660223600CE": 11,
      "NIFTY26JUNFUT": 8
    },
    "trade_count": {
      "<MISSING>": 50
    }
  },
  "execution_key_presence": {
    "event_time": 50,
    "execution_channel": 50,
    "execution_id": 50,
    "fill_price": 50,
    "fill_qty": 50,
    "filled": 50,
    "metadata": 50,
    "reason": 50,
    "risk_action": 50,
    "slippage": 50,
    "source_risk_id": 50,
    "symbol": 50
  },
  "execution_sample": [
    {
      "event_time": "2026-06-01T10:06:53Z",
      "execution_channel": "replay:execution_shadow",
      "execution_id": "execution_shadow_000001",
      "fill_price": null,
      "fill_qty": 0,
      "filled": false,
      "metadata": {
        "feature_truth_mode": "replay_bridge_v3_event_normalized",
        "r31a_r9f_r1_family_surface_enriched": true,
        "replay_feature_bridge_version": "v3_event_normalized_r31a_r9f_r1_enriched",
        "source_file": "quote_ticks_mme_fut_stream.csv",
        "source_stem": "quote_ticks_mme_fut_stream",
        "symbol": "NIFTY26JUNFUT",
        "trading_day": "2026-06-01",
        "ts_event": "1780308413000000000"
      },
      "reason": "risk_block_or_non_entry",
      "risk_action": "HOLD",
      "slippage": null,
      "source_risk_id": "risk_output_000001",
      "symbol": "NIFTY26JUNFUT"
    },
    {
      "event_time": "2026-06-01T10:06:53Z",
      "execution_channel": "replay:execution_shadow",
      "execution_id": "execution_shadow_000002",
      "fill_price": null,
      "fill_qty": 0,
      "filled": false,
      "metadata": {
        "feature_truth_mode": "replay_bridge_v3_event_normalized",
        "r31a_r9f_r1_family_surface_enriched": true,
        "replay_feature_bridge_version": "v3_event_normalized_r31a_r9f_r1_enriched",
        "source_file": "quote_ticks_mme_opt_stream.csv",
        "source_stem": "quote_ticks_mme_opt_stream",
        "symbol": "NIFTY2660223500PE",
        "trading_day": "2026-06-01",
        "ts_event": "1780308413000000000"
      },
      "reason": "risk_block_or_non_entry",
      "risk_action": "HOLD",
      "slippage": null,
      "source_risk_id": "risk_output_000002",
      "symbol": "NIFTY2660223500PE"
    },
    {
      "event_time": "2026-06-01T10:06:53Z",
      "execution_channel": "replay:execution_shadow",
      "execution_id": "execution_shadow_000003",
      "fill_price": null,
      "fill_qty": 0,
      "filled": false,
      "metadata": {
        "feature_truth_mode": "replay_bridge_v3_event_normalized",
        "r31a_r9f_r1_family_surface_enriched": true,
        "replay_feature_bridge_version": "v3_event_normalized_r31a_r9f_r1_enriched",
        "source_file": "quote_ticks_mme_opt_stream.csv",
        "source_stem": "quote_ticks_mme_opt_stream",
        "symbol": "NIFTY2660223550CE",
        "trading_day": "2026-06-01",
        "ts_event": "1780308413000000000"
      },
      "reason": "risk_block_or_non_entry",
      "risk_action": "HOLD",
      "slippage": null,
      "source_risk_id": "risk_output_000003",
      "symbol": "NIFTY2660223550CE"
    },
    {
      "event_time": "2026-06-01T10:06:53Z",
      "execution_channel": "replay:execution_shadow",
      "execution_id": "execution_shadow_000004",
      "fill_price": null,
      "fill_qty": 0,
      "filled": false,
      "metadata": {
        "feature_truth_mode": "replay_bridge_v3_event_normalized",
        "r31a_r9f_r1_family_surface_enriched": true,
        "replay_feature_bridge_version": "v3_event_normalized_r31a_r9f_r1_enriched",
        "source_file": "quote_ticks_mme_opt_stream.csv",
        "source_stem": "quote_ticks_mme_opt_stream",
        "symbol": "NIFTY2660223550PE",
        "trading_day": "2026-06-01",
        "ts_event": "1780308413000000000"
      },
      "reason": "risk_block_or_non_entry",
      "risk_action": "HOLD",
      "slippage": null,
      "source_risk_id": "risk_output_000004",
      "symbol": "NIFTY2660223550PE"
    },
    {
      "event_time": "2026-06-01T10:06:53Z",
      "execution_channel": "replay:execution_shadow",
      "execution_id": "execution_shadow_000005",
      "fill_price": null,
      "fill_qty": 0,
      "filled": false,
      "metadata": {
        "feature_truth_mode": "replay_bridge_v3_event_normalized",
        "r31a_r9f_r1_family_surface_enriched": true,
        "replay_feature_bridge_version": "v3_event_normalized_r31a_r9f_r1_enriched",
        "source_file": "quote_ticks_mme_opt_stream.csv",
        "source_stem": "quote_ticks_mme_opt_stream",
        "symbol": "NIFTY2660223600CE",
        "trading_day": "2026-06-01",
        "ts_event": "1780308413000000000"
      },
      "reason": "risk_block_or_non_entry",
      "risk_action": "HOLD",
      "slippage": null,
      "source_risk_id": "risk_output_000005",
      "symbol": "NIFTY2660223600CE"
    },
    {
      "event_time": "2026-06-01T10:06:54Z",
      "execution_channel": "replay:execution_shadow",
      "execution_id": "execution_shadow_000006",
      "fill_price": null,
      "fill_qty": 0,
      "filled": false,
      "metadata": {
        "feature_truth_mode": "replay_bridge_v3_event_normalized",
        "r31a_r9f_r1_family_surface_enriched": true,
        "replay_feature_bridge_version": "v3_event_normalized_r31a_r9f_r1_enriched",
        "source_file": "quote_ticks_mme_fut_stream.csv",
        "source_stem": "quote_ticks_mme_fut_stream",
        "symbol": "NIFTY26JUNFUT",
        "trading_day": "2026-06-01",
        "ts_event": "1780308414000000000"
      },
      "reason": "risk_block_or_non_entry",
      "risk_action": "HOLD",
      "slippage": null,
      "source_risk_id": "risk_output_000006",
      "symbol": "NIFTY26JUNFUT"
    },
    {
      "event_time": "2026-06-01T10:06:54Z",
      "execution_channel": "replay:execution_shadow",
      "execution_id": "execution_shadow_000007",
      "fill_price": null,
      "fill_qty": 0,
      "filled": false,
      "metadata": {
        "feature_truth_mode": "replay_bridge_v3_event_normalized",
        "r31a_r9f_r1_family_surface_enriched": true,
        "replay_feature_bridge_version": "v3_event_normalized_r31a_r9f_r1_enriched",
        "source_file": "quote_ticks_mme_opt_stream.csv",
        "source_stem": "quote_ticks_mme_opt_stream",
        "symbol": "NIFTY2660223550CE",
        "trading_day": "2026-06-01",
        "ts_event": "1780308414000000000"
      },
      "reason": "risk_block_or_non_entry",
      "risk_action": "HOLD",
      "slippage": null,
      "source_risk_id": "risk_output_000007",
      "symbol": "NIFTY2660223550CE"
    },
    {
      "event_time": "2026-06-01T10:06:54Z",
      "execution_channel": "replay:execution_shadow",
      "execution_id": "execution_shadow_000008",
      "fill_price": null,
      "fill_qty": 0,
      "filled": false,
      "metadata": {
        "feature_truth_mode": "replay_bridge_v3_event_normalized",
        "r31a_r9f_r1_family_surface_enriched": true,
        "replay_feature_bridge_version": "v3_event_normalized_r31a_r9f_r1_enriched",
        "source_file": "quote_ticks_mme_opt_stream.csv",
        "source_stem": "quote_ticks_mme_opt_stream",
        "symbol": "NIFTY2660223600CE",
        "trading_day": "2026-06-01",
        "ts_event": "1780308414000000000"
      },
      "reason": "risk_block_or_non_entry",
      "risk_action": "HOLD",
      "slippage": null,
      "source_risk_id": "risk_output_000008",
      "symbol": "NIFTY2660223600CE"
    },
    {
      "event_time": "2026-06-01T10:06:54Z",
      "execution_channel": "replay:execution_shadow",
      "execution_id": "execution_shadow_000009",
      "fill_price": null,
      "fill_qty": 0,
      "filled": false,
      "metadata": {
        "feature_truth_mode": "replay_bridge_v3_event_normalized",
        "r31a_r9f_r1_family_surface_enriched": true,
        "replay_feature_bridge_version": "v3_event_normalized_r31a_r9f_r1_enriched",
        "source_file": "quote_ticks_mme_opt_stream.csv",
        "source_stem": "quote_ticks_mme_opt_stream",
        "symbol": "NIFTY2660223500PE",
        "trading_day": "2026-06-01",
        "ts_event": "1780308414000000000"
      },
      "reason": "risk_block_or_non_entry",
      "risk_action": "HOLD",
      "slippage": null,
      "source_risk_id": "risk_output_000009",

## Audit errors

## Source context
## app/mme_scalpx/replay/execution_shadow.py source context
     1	from __future__ import annotations
     2	
     3	from dataclasses import dataclass
     4	from typing import Any, Mapping
     5	
     6	from app.mme_scalpx.replay.live_adapter import write_replay_live_state
     7	from app.mme_scalpx.replay.transport import LocalReplayTransport
     8	
     9	
    10	REPLAY_EXECUTION_SHADOW_CONTRACT_VERSION = "replay_execution_shadow_v1"
    11	
    12	REPLAY_SHADOW_FILL_POLICIES = (
    13	    "FULL_FILL",
    14	    "PARTIAL_FILL",
    15	    "NO_FILL",
    16	    "REJECTED",
    17	)
    18	
    19	REPLAY_EXECUTION_SHADOW_REQUIRED_FIELDS = (
    20	    "schema_version",
    21	    "run_id",
    22	    "assumption_profile",
    23	    "fill_policy",
    24	    "fill_status",
    25	    "requested_qty",
    26	    "filled_qty",
    27	    "entry_price",
    28	    "exit_price",
    29	    "slippage_points",
    30	    "shadow_position_state",
    31	    "shadow_trade_log",
    32	    "shadow_pnl_summary",
    33	    "real_order_sent",
    34	    "broker_calls_executed",
    35	    "paper_armed_approved",
    36	    "live_trading_approved",
    37	    "production_doctrine_changed",
    38	)
    39	
    40	
    41	@dataclass(frozen=True)
    42	class ReplayShadowAssumptionProfile:
    43	    fill_policy: str = "FULL_FILL"
    44	    requested_qty: int = 75
    45	    partial_fill_ratio: float = 0.5
    46	    entry_reference_price: float = 100.0
    47	    exit_reference_price: float = 104.0
    48	    slippage_points: float = 0.5
    49	    transaction_cost_points: float = 0.25
    50	    reject_reason: str = "replay_assumption_reject"
    51	
    52	
    53	def _clamp_qty(value: int | float) -> int:
    54	    return max(0, int(value))
    55	
    56	
    57	def replay_shadow_assumption_profile(**kwargs: Any) -> dict[str, Any]:
    58	    profile = ReplayShadowAssumptionProfile(**kwargs)
    59	    if profile.fill_policy not in REPLAY_SHADOW_FILL_POLICIES:
    60	        raise ValueError(f"unsupported replay shadow fill_policy: {profile.fill_policy}")
    61	    return {
    62	        "fill_policy": profile.fill_policy,
    63	        "requested_qty": int(profile.requested_qty),
    64	        "partial_fill_ratio": float(profile.partial_fill_ratio),
    65	        "entry_reference_price": float(profile.entry_reference_price),
    66	        "exit_reference_price": float(profile.exit_reference_price),
    67	        "slippage_points": float(profile.slippage_points),
    68	        "transaction_cost_points": float(profile.transaction_cost_points),
    69	        "reject_reason": str(profile.reject_reason),
    70	        "paper_armed_approved": False,
    71	        "live_trading_approved": False,
    72	        "real_order_sent": False,
    73	        "broker_calls_executed": False,
    74	    }
    75	
    76	
    77	def simulate_replay_execution_shadow(
    78	    *,
    79	    run_id: str,
    80	    strategy_decision: Mapping[str, Any],
    81	    risk_decision: Mapping[str, Any],
    82	    assumption_profile: Mapping[str, Any],
    83	) -> dict[str, Any]:
    84	    fill_policy = str(assumption_profile.get("fill_policy", "FULL_FILL"))
    85	    if fill_policy not in REPLAY_SHADOW_FILL_POLICIES:
    86	        raise ValueError(f"unsupported replay shadow fill_policy: {fill_policy}")
    87	
    88	    requested_qty = _clamp_qty(assumption_profile.get("requested_qty", 0))
    89	    partial_ratio = max(0.0, min(1.0, float(assumption_profile.get("partial_fill_ratio", 0.5))))
    90	    entry_ref = float(assumption_profile.get("entry_reference_price", 100.0))
    91	    exit_ref = float(assumption_profile.get("exit_reference_price", entry_ref))
    92	    slippage = float(assumption_profile.get("slippage_points", 0.0))
    93	    costs = float(assumption_profile.get("transaction_cost_points", 0.0))
    94	
    95	    research_allowed = risk_decision.get("research_trade_allowed") is True
    96	    risk_vetoed = risk_decision.get("entry_vetoed") is True
    97	
    98	    if risk_vetoed or not research_allowed:
    99	        fill_status = "RISK_VETOED"
   100	        filled_qty = 0
   101	    elif fill_policy == "FULL_FILL":
   102	        fill_status = "FILLED"
   103	        filled_qty = requested_qty
   104	    elif fill_policy == "PARTIAL_FILL":
   105	        fill_status = "PARTIAL_FILLED"
   106	        filled_qty = _clamp_qty(requested_qty * partial_ratio)
   107	    elif fill_policy == "NO_FILL":
   108	        fill_status = "NO_FILL"
   109	        filled_qty = 0
   110	    else:
   111	        fill_status = "REJECTED"
   112	        filled_qty = 0
   113	
   114	    entry_price = entry_ref + slippage if filled_qty else None
   115	    exit_price = exit_ref - slippage if filled_qty else None
   116	    gross_points = (exit_price - entry_price) if filled_qty and entry_price is not None and exit_price is not None else 0.0
   117	    net_points = gross_points - costs if filled_qty else 0.0
   118	    net_pnl = net_points * filled_qty
   119	
   120	    winning_family = None
   121	    winning_side = None
   122	    arbitration = strategy_decision.get("arbitration")
   123	    if isinstance(arbitration, Mapping):
   124	        winning_family = arbitration.get("winning_family")
   125	        winning_side = arbitration.get("winning_side")
   126	
   127	    shadow_trade = {
   128	        "schema_version": "replay_shadow_trade_v1",
   129	        "run_id": str(run_id),
   130	        "winning_family": winning_family,
   131	        "winning_side": winning_side,
   132	        "fill_policy": fill_policy,
   133	        "fill_status": fill_status,
   134	        "requested_qty": requested_qty,
   135	        "filled_qty": filled_qty,
   136	        "entry_price": entry_price,
   137	        "exit_price": exit_price,
   138	        "gross_points": gross_points,
   139	        "transaction_cost_points": costs,
   140	        "net_points": net_points,
   141	        "net_pnl": net_pnl,
   142	        "real_order_sent": False,
   143	        "broker_calls_executed": False,
   144	    }
   145	
   146	    position_state = {
   147	        "schema_version": "replay_shadow_position_v1",
   148	        "run_id": str(run_id),
   149	        "position_opened": filled_qty > 0,
   150	        "position_closed": filled_qty > 0,
   151	        "net_qty": 0,
   152	        "filled_qty": filled_qty,
   153	        "side": winning_side,
   154	        "family": winning_family,
   155	        "real_position_mutated": False,
   156	    }
   157	
   158	    pnl_summary = {
   159	        "schema_version": "replay_shadow_pnl_summary_v1",
   160	        "run_id": str(run_id),
   161	        "trade_count": 1 if filled_qty else 0,
   162	        "filled_qty": filled_qty,
   163	        "gross_points": gross_points,
   164	        "net_points": net_points,
   165	        "net_pnl": net_pnl,
   166	        "is_profit": net_pnl > 0,
   167	        "is_loss": net_pnl < 0,
   168	    }
   169	
   170	    payload = {
   171	        "schema_version": REPLAY_EXECUTION_SHADOW_CONTRACT_VERSION,
   172	        "run_id": str(run_id),
   173	        "assumption_profile": dict(assumption_profile),
   174	        "fill_policy": fill_policy,
   175	        "fill_status": fill_status,
   176	        "requested_qty": requested_qty,
   177	        "filled_qty": filled_qty,
   178	        "entry_price": entry_price,
   179	        "exit_price": exit_price,
   180	        "slippage_points": slippage,
   181	        "shadow_position_state": position_state,
   182	        "shadow_trade_log": (shadow_trade,),
   183	        "shadow_pnl_summary": pnl_summary,
   184	        "risk_vetoed": risk_vetoed,
   185	        "research_trade_allowed": research_allowed,
   186	        "real_order_sent": False,
   187	        "broker_calls_executed": False,
   188	        "live_redis_writes_executed": False,
   189	        "paper_armed_approved": False,
   190	        "live_trading_approved": False,
   191	        "execution_arming_created": False,
   192	        "production_doctrine_changed": False,
   193	        "execution_shadow_shape": "PROVEN_BY_27I",
   194	        "real_execution_parity": "NOT_PROVEN_IN_27I",
   195	    }
   196	    return payload
   197	
   198	
   199	def validate_replay_execution_shadow(payload: Mapping[str, Any]) -> dict[str, Any]:
   200	    missing = tuple(field for field in REPLAY_EXECUTION_SHADOW_REQUIRED_FIELDS if field not in payload)
   201	    fill_policy_ok = payload.get("fill_policy") in REPLAY_SHADOW_FILL_POLICIES
   202	    no_real_order_ok = (
   203	        payload.get("real_order_sent") is False
   204	        and payload.get("broker_calls_executed") is False
   205	        and payload.get("live_redis_writes_executed") is False
   206	        and payload.get("paper_armed_approved") is False
   207	        and payload.get("live_trading_approved") is False
   208	        and payload.get("execution_arming_created") is False
   209	        and payload.get("production_doctrine_changed") is False
   210	    )
   211	    pnl_ok = isinstance(payload.get("shadow_pnl_summary"), Mapping)
   212	    trade_log_ok = isinstance(payload.get("shadow_trade_log"), tuple)
   213	    position_ok = isinstance(payload.get("shadow_position_state"), Mapping)
   214	    ok = bool(not missing and fill_policy_ok and no_real_order_ok and pnl_ok and trade_log_ok and position_ok)
   215	    return {
   216	        "ok": ok,
   217	        "missing": missing,
   218	        "fill_policy_ok": fill_policy_ok,
   219	        "no_real_order_ok": no_real_order_ok,
   220	        "pnl_ok": pnl_ok,
   221	        "trade_log_ok": trade_log_ok,
   222	        "position_ok": position_ok,
   223	    }
   224	
   225	
   226	def publish_replay_execution_shadow(
   227	    transport: LocalReplayTransport,
   228	    *,
   229	    run_id: str,
   230	    execution_shadow: Mapping[str, Any],
   231	    updated_ts_ns: int | None = None,
   232	) -> dict[str, Any]:
   233	    validation = validate_replay_execution_shadow(execution_shadow)
   234	    if not validation["ok"]:
   235	        raise ValueError(f"invalid replay execution shadow: {validation}")
   236	    return write_replay_live_state(
   237	        transport,
   238	        surface="execution_shadow",
   239	        row=dict(execution_shadow),
   240	        updated_ts_ns=updated_ts_ns,

## bin/replay_run.py summary builder context
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
  2766	        "strategy_candidate_true_count": _count_true(persisted_strategy_decisions, "candidate"),
  2767	        "risk_vetoed_true_count": _count_true(persisted_risk_outputs, "vetoed"),
  2768	

## bin/replay_run.py execution stage context
  3160	            published_count = 0
  3161	            risk_action_breakdown: dict[str, int] = {}
  3162	            vetoed_entries = 0
  3163	            for risk_output in risk_outputs:
  3164	                transport.publish_risk_output(risk_output)
  3165	                published_count += 1
  3166	                risk_action = str(risk_output.get("risk_action"))
  3167	                risk_action_breakdown[risk_action] = (
  3168	                    risk_action_breakdown.get(risk_action, 0) + 1
  3169	                )
  3170	                if bool(risk_output.get("veto_entry")):
  3171	                    vetoed_entries += 1
  3172	
  3173	            return {
  3174	                "stage_name": stage.stage_name,
  3175	                "status": "ok",
  3176	                "run_id": context.run_id,
  3177	                "mode": "replay_risk_bridge",
  3178	                "source_strategy_decisions": len(strategy_decisions),
  3179	                "risk_outputs_published": published_count,
  3180	                "risk_channel": "replay:risk",
  3181	                "risk_action_breakdown": risk_action_breakdown,
  3182	                "vetoed_entries": vetoed_entries,
  3183	            }
  3184	
  3185	        if stage.stage_name == "execution_shadow":
  3186	            risk_outputs = transport.risk_outputs
  3187	            execution_results = build_execution_shadow_results_from_risk_outputs(
  3188	                run_id=context.run_id,
  3189	                risk_outputs=risk_outputs,
  3190	                fill_model_name=fill_model_name,
  3191	                doctrine_mode=doctrine_mode,
  3192	            )
  3193	
  3194	            published_count = 0
  3195	            filled_count = 0
  3196	            for execution_result in execution_results:
  3197	                transport.publish_execution_shadow_result(execution_result)
  3198	                published_count += 1
  3199	                if bool(execution_result.get("filled")):
  3200	                    filled_count += 1
  3201	
  3202	            return {
  3203	                "stage_name": stage.stage_name,
  3204	                "status": "ok",
  3205	                "mode": "replay_execution_shadow_bridge",
  3206	                "run_id": context.run_id,
  3207	                "source_risk_outputs": len(risk_outputs),
  3208	                "execution_results_published": published_count,
  3209	                "filled_count": filled_count,
  3210	                "execution_channel": "replay:execution_shadow",
  3211	                "fill_model_name": _resolve_fill_model_name(fill_model_name),
  3212	            }
  3213	
  3214	        return {
  3215	            "stage_name": stage.stage_name,
  3216	            "status": "ok",
  3217	            "run_id": context.run_id,
  3218	            "mode": "placeholder_stage_bridge",
  3219	        }
  3220	
  3221	    return stage_executor
  3222	
  3223	
  3224	
  3225	

## grep around execution result fields
app/mme_scalpx/replay/raw_artifact_enricher.py:178:        "net_pnl_after_costs",
app/mme_scalpx/replay/raw_artifact_enricher.py:212:    "net_pnl_after_costs": ("net_pnl", "realized_net_pnl", "pnl_net", "closed_net_pnl"),
app/mme_scalpx/replay/raw_artifact_enricher.py:359:        _first_value(row, "net_pnl_after_costs") not in (None, "")
app/mme_scalpx/replay/raw_artifact_enricher.py:444:        elif field in {"entry_price", "exit_price", "qty", "gross_pnl", "net_pnl_after_costs", "costs"}:
app/mme_scalpx/replay/miv_research_evaluator.py:586:        "miv_candidate_id,event_ts,side,entry_ref_price,shadow_fill_price,shadow_exit_price,shadow_exit_reason,gross_points,cost_points,net_points,filled,pnl_surface_version,remarks\n",
app/mme_scalpx/replay/artifact_materializer.py:21:    "06_execution_shadow_summary.json",
app/mme_scalpx/replay/artifact_materializer.py:131:        "schema_version": "replay_execution_shadow_summary_artifact_v1",
app/mme_scalpx/replay/artifact_materializer.py:134:        "filled_qty_total": sum(int(r.get("execution_shadow_summary", {}).get("filled_qty") or 0) for r in results),
app/mme_scalpx/replay/artifact_materializer.py:135:        "net_pnl_total": sum(float(r.get("execution_shadow_summary", {}).get("net_pnl") or 0.0) for r in results),
app/mme_scalpx/replay/artifact_materializer.py:136:        "real_order_sent_count": sum(1 for r in results if r.get("execution_shadow_summary", {}).get("real_order_sent") is True),
app/mme_scalpx/replay/artifact_materializer.py:137:        "broker_calls_executed_count": sum(1 for r in results if r.get("execution_shadow_summary", {}).get("broker_calls_executed") is True),
app/mme_scalpx/replay/artifact_materializer.py:208:        "06_execution_shadow_summary.json": execution_summary,
app/mme_scalpx/replay/execution_shadow.py:118:    net_pnl = net_points * filled_qty
app/mme_scalpx/replay/execution_shadow.py:141:        "net_pnl": net_pnl,
app/mme_scalpx/replay/execution_shadow.py:161:        "trade_count": 1 if filled_qty else 0,
app/mme_scalpx/replay/execution_shadow.py:165:        "net_pnl": net_pnl,
app/mme_scalpx/replay/execution_shadow.py:166:        "is_profit": net_pnl > 0,
app/mme_scalpx/replay/execution_shadow.py:167:        "is_loss": net_pnl < 0,
app/mme_scalpx/replay/raw_trade_family_backfill.py:75:    net = safe_float(row.get("net_pnl_after_costs"))
app/mme_scalpx/replay/raw_trade_family_backfill.py:247:    trade_count = 0
app/mme_scalpx/replay/raw_trade_family_backfill.py:254:    trade_backfilled_count = 0
app/mme_scalpx/replay/raw_trade_family_backfill.py:261:        trade_count += 1
app/mme_scalpx/replay/raw_trade_family_backfill.py:283:            trade_backfilled_count += 1
app/mme_scalpx/replay/raw_trade_family_backfill.py:292:    family_trade_counts = Counter()
app/mme_scalpx/replay/raw_trade_family_backfill.py:295:            family_trade_counts[norm_upper(row.get("family")) or "UNKNOWN"] += 1
app/mme_scalpx/replay/raw_trade_family_backfill.py:304:        "trade_count": trade_count,
