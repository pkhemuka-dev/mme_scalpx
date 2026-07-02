# R35C_R4Y_REPLAY_EXIT_PNL_MODEL_SOURCE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260614_001445

classification: PASS_R35C_R4Y_REPLAY_EXIT_PNL_MODEL_SOURCE_AUDIT_DONE_NO_PATCH_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35C_R4Y_REPLAY_EXIT_PNL_MODEL_SOURCE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260614_001445.json`
run_dir: `run/replay/r35c_r4x/20260614_000314/replay_locked_single_day_r35c_r4x_20260601_20260613_183322_0860a772`

audit_rc=0
safety pre=0/0/0 post=0/0/0 proc=0/0 replay_proc=0

## Artifact schema sample
{
  "economics_summary_keys": [
    "authority_candidates",
    "economics_reason_counts",
    "enriched_field_values",
    "enrichment_schema_version",
    "enrichment_sources",
    "enrichment_status",
    "field_presence",
    "fields_left_missing",
    "governance_notes",
    "missing_economics_fields",
    "note",
    "row_count",
    "schema_version",
    "selected_leg_counts",
    "unit_basis",
    "value_counts"
  ],
  "economics_summary_sample": {
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
      "stop_ticks": {
        "formula": "stop_points / tick_size",
        "source_type": "derived_from_points_and_tick_size",
        "stop_points": 4.0,
        "tick_size": 0.05
      },
      "target_points": {
        "line": 79,
        "path": "app/mme_scalpx/services/strategy_family/misb.py",
        "source_type": "source_assignment_candidate",
        "text": "TARGET_POINTS: Final[float] = 5.0",
        "value": 5.0
      },
      "target_ticks": {
        "formula": "target_points / tick_size",
        "source_type": "derived_from_points_and_tick_size",
        "target_points": 5.0,
        "tick_size": 0.05
      },
      "tick_size": {
        "line": 81,
        "path": "app/mme_scalpx/services/strategy_family/misb.py",
        "source_type": "source_assignment_candidate",
        "text": "DEFAULT_TICK_SIZE: Final[float] = 0.05",
        "value": 0.05
      }
    },
    "enrichment_status": "enriched_source_labelled",
    "field_presence": {},
    "fields_left_missing": [
      "source_frame_id",
      "selected_leg",
      "entry_mode",
      "economics_reason"
    ],
    "governance_notes": [
      "Export-only enrichment; does not change strategy decisions.",
      "Values are source-labelled and must not be treated as trade/PnL proof.",
      "entry_mode=NO_ENTRY_HOLD_ONLY is only an export label when all rows are HOLD and candidate_true_count is zero.",
      "Do not claim paper/live, broker/order, risk/execution, or profitability readiness from this enrichment."
    ],
    "missing_economics_fields": [
      "source_frame_id",
      "selected_leg",
      "entry_mode",
      "tick_size",
      "target_ticks",
      "stop_ticks",

## Artifact schema errors

## Source audit
## Current R4X summary
{
  "batch_profile": null,
  "blocker_count": 131368,
  "candidate_count": 4222,
  "chapter": "replay",
  "completed_at": "2026-06-13T18:35:30Z",
  "created_at": "2026-06-13T18:33:22Z",
  "dataset_fingerprint": "83cd5b7373313ef6cbb3aa3dc7f3ee82a2523b7e05e7b30bba91f882560e46f6",
  "dataset_id": "r35c_r4x",
  "dataset_profile": null,
  "doctrine_mode": "locked",
  "duration_ms": null,
  "execution_shadow_action_breakdown": {},
  "execution_shadow_filled_count": 4222,
  "execution_shadow_row_count": 131368,
  "experiment_profile": null,
  "feature_blocker_non_null_count": 131368,
  "feature_candidate_true_count": 0,
  "feature_economics_valid_true_count": 0,
  "feature_leg_breakdown": {
    "CALL_ATM": 55098,
    "FUTURES": 21229,
    "PUT_ATM": 55041
  },
  "feature_regime_pass_true_count": 131368,
  "feature_row_count": 131368,
  "feature_side_breakdown": {
    "CALL": 55098,
    "CONTEXT": 21229,
    "PUT": 55041
  },
  "forensic_profile": null,
  "input_fingerprint": "1badfbc7ae2e56b8fe7103bd7b165b9c89bae349cac496a7cc7b3d146d30ced9",
  "integrity_profile": null,
  "integrity_verdict": "fail",
  "loss_count": 0,
  "ml_export_eligible": false,
  "notes": [],
  "operator_verdict": null,
  "override_pack_id": null,
  "pnl_accounting_status": "PNL_NOT_COMPUTED_EXECUTION_SHADOW_HAS_ENTRY_FILL_ONLY_NO_EXIT_MODEL_R35C_R4W",
  "pnl_total": null,
  "regime_pass_count": 131368,
  "remarks": null,
  "replay_profile": null,
  "replay_scope": "feeds_features_strategy_risk_execution_shadow",
  "research_tags": [],
  "risk_action_breakdown": {
    "ENTER_CALL": 2033,
    "ENTER_PUT": 2189,
    "HOLD": 127146
  },
  "risk_blocker_non_null_count": 131368,
  "risk_economics_valid_true_count": 0,
  "risk_regime_pass_true_count": 131368,
  "risk_row_count": 131368,
  "risk_vetoed_true_count": 0,
  "run_id": "replay_locked_single_day_r35c_r4x_20260601_20260613_183322_0860a772",
  "selection_mode": "single_day",
  "shadow_filled_qty_total": 4222,
  "shadow_label": null,
  "shadow_trade_count": 4222,
  "side_mode": "mirrored_both",
  "speed_mode": "accelerated",
  "stage_count": 5,
  "stage_names": [
    "feeds",
    "features",
    "strategy",
    "risk",
    "execution_shadow"
  ],
  "started_at": "2026-06-13T18:33:22Z",
  "strategy_action_breakdown": {
    "ENTRY": 4222,
    "HOLD": 127146
  },
  "strategy_blocker_non_null_count": 131368,
  "strategy_candidate_true_count": 4222,
  "strategy_economics_valid_true_count": 0,
  "strategy_regime_pass_true_count": 131368,
  "strategy_row_count": 131368,
  "trade_count": 4222,
  "trading_dates": [
    "2026-06-01"
  ],
  "waiver_count": 0,
  "win_count": 0,
  "window_end": null,
  "window_start": null
}

## Execution shadow source
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

## Replay run execution-shadow builder
app/mme_scalpx/core/models.py:1202:    stop_points: float | None = None
app/mme_scalpx/core/models.py:1211:        if self.stop_points is not None:
app/mme_scalpx/core/models.py:1212:            _require_float(self.stop_points, "stop_points", min_value=0.0)
app/mme_scalpx/core/models.py:1222:    target_points: float | None = None
app/mme_scalpx/core/models.py:1231:        if self.target_points is not None:
app/mme_scalpx/core/models.py:1232:            _require_float(self.target_points, "target_points", min_value=0.0)
app/mme_scalpx/core/models.py:1823:    fill_price: float
app/mme_scalpx/core/models.py:1840:        _require_float(self.fill_price, "fill_price", min_value=0.0)
app/mme_scalpx/core/models.py:1860:    fill_price: float
app/mme_scalpx/core/models.py:1878:        _require_float(self.fill_price, "fill_price", min_value=0.0)
app/mme_scalpx/core/models.py:2885:    exit_price: float | None = None
app/mme_scalpx/core/models.py:2912:        if self.exit_price is not None:
app/mme_scalpx/core/models.py:2913:            _require_float(self.exit_price, "exit_price", min_value=0.0)
app/mme_scalpx/replay_optimization/profile_generator.py:81:        if candidate.target_points is not None:
app/mme_scalpx/replay_optimization/profile_generator.py:82:            profile["overrides"]["exit_controls"]["target_points"] = candidate.target_points
app/mme_scalpx/replay_optimization/profile_generator.py:83:        if candidate.hard_stop_points is not None:
app/mme_scalpx/replay_optimization/profile_generator.py:84:            profile["overrides"]["exit_controls"]["hard_stop_points"] = candidate.hard_stop_points
app/mme_scalpx/replay_optimization/sweep_space.py:109:            parameter_name="target_points",
app/mme_scalpx/replay_optimization/sweep_space.py:118:            parameter_name="hard_stop_points",
app/mme_scalpx/replay_optimization/sweep_space.py:226:    target_points = None
app/mme_scalpx/replay_optimization/sweep_space.py:227:    hard_stop_points = None
app/mme_scalpx/replay_optimization/sweep_space.py:232:        if spec.parameter_name == "target_points":
app/mme_scalpx/replay_optimization/sweep_space.py:233:            target_points = _to_float(candidate_value)
app/mme_scalpx/replay_optimization/sweep_space.py:234:        elif spec.parameter_name == "hard_stop_points":
app/mme_scalpx/replay_optimization/sweep_space.py:235:            hard_stop_points = _to_float(candidate_value)
app/mme_scalpx/replay_optimization/sweep_space.py:251:        target_points=target_points,
app/mme_scalpx/replay_optimization/sweep_space.py:252:        hard_stop_points=hard_stop_points,
app/mme_scalpx/replay_optimization/contracts.py:140:    "target_points",
app/mme_scalpx/replay_optimization/contracts.py:141:    "hard_stop_points",
app/mme_scalpx/replay_optimization/contracts.py:286:    target_points: float | None = None
app/mme_scalpx/replay_optimization/contracts.py:287:    hard_stop_points: float | None = None
app/mme_scalpx/replay/raw_artifact_enricher.py:175:        "exit_price",
app/mme_scalpx/replay/raw_artifact_enricher.py:357:    has_exit = _first_value(row, "exit_price") not in (None, "")
app/mme_scalpx/replay/raw_artifact_enricher.py:444:        elif field in {"entry_price", "exit_price", "qty", "gross_pnl", "net_pnl_after_costs", "costs"}:
app/mme_scalpx/replay/miv_research_evaluator.py:586:        "miv_candidate_id,event_ts,side,entry_ref_price,shadow_fill_price,shadow_exit_price,shadow_exit_reason,gross_points,cost_points,net_points,filled,pnl_surface_version,remarks\n",
app/mme_scalpx/replay/execution_shadow.py:28:    "exit_price",
app/mme_scalpx/replay/execution_shadow.py:115:    exit_price = exit_ref - slippage if filled_qty else None
app/mme_scalpx/replay/execution_shadow.py:116:    gross_points = (exit_price - entry_price) if filled_qty and entry_price is not None and exit_price is not None else 0.0
app/mme_scalpx/replay/execution_shadow.py:137:        "exit_price": exit_price,
app/mme_scalpx/replay/execution_shadow.py:179:        "exit_price": exit_price,
app/mme_scalpx/replay/raw_trade_family_backfill.py:254:    trade_backfilled_count = 0
app/mme_scalpx/replay/raw_trade_family_backfill.py:283:            trade_backfilled_count += 1
app/mme_scalpx/replay/raw_trade_family_backfill.py:311:        "trade_backfilled_count": trade_backfilled_count,
app/mme_scalpx/replay/raw_trade_family_backfill.py:355:        "trade_backfilled_count": trade_backfilled_count,
app/mme_scalpx/replay/raw_producer_family_emission.py:168:        "exit_price": row.get("exit_price"),
app/mme_scalpx/replay/artifacts.py:551:            "target_points": ["TARGET_POINTS", "target_points", "profit_target"],
app/mme_scalpx/replay/artifacts.py:552:            "stop_points": ["HARD_STOP_POINTS", "STOP_POINTS", "hard_stop_points", "stop_points", "hard_stop"],
app/mme_scalpx/replay/artifacts.py:641:            if field == "target_points" and "TARGET_POINTS" in line_text:
app/mme_scalpx/replay/artifacts.py:643:            if field == "stop_points" and "HARD_STOP_POINTS" in line_text:
app/mme_scalpx/replay/artifacts.py:667:                "reject numeric zero for tick_size/target_points/stop_points",
app/mme_scalpx/replay/artifacts.py:693:        target_points = (selected.get("target_points") or {}).get("value")
app/mme_scalpx/replay/artifacts.py:694:        stop_points = (selected.get("stop_points") or {}).get("value")
app/mme_scalpx/replay/artifacts.py:716:        if target_points is not None:
app/mme_scalpx/replay/artifacts.py:717:            enriched_values["target_points"] = target_points
app/mme_scalpx/replay/artifacts.py:718:            enriched_values["reward_points"] = target_points
app/mme_scalpx/replay/artifacts.py:719:            enrichment_sources["target_points"] = {
app/mme_scalpx/replay/artifacts.py:721:                **(selected.get("target_points") or {}),
app/mme_scalpx/replay/artifacts.py:724:                "source_type": "derived_same_as_target_points",
app/mme_scalpx/replay/artifacts.py:725:                "basis": "reward for first target equals target_points in export summary",
app/mme_scalpx/replay/artifacts.py:728:        if stop_points is not None:
app/mme_scalpx/replay/artifacts.py:729:            enriched_values["stop_points"] = stop_points
app/mme_scalpx/replay/artifacts.py:730:            enrichment_sources["stop_points"] = {
app/mme_scalpx/replay/artifacts.py:732:                **(selected.get("stop_points") or {}),
app/mme_scalpx/replay/artifacts.py:735:        if target_points is not None and stop_points not in (None, 0):
app/mme_scalpx/replay/artifacts.py:736:            enriched_values["reward_cost_ratio"] = round(float(target_points) / float(stop_points), 6)
app/mme_scalpx/replay/artifacts.py:739:                "formula": "target_points / stop_points",
app/mme_scalpx/replay/artifacts.py:740:                "target_points": target_points,
app/mme_scalpx/replay/artifacts.py:741:                "stop_points": stop_points,
app/mme_scalpx/replay/artifacts.py:744:        if tick_size not in (None, 0) and target_points is not None:
app/mme_scalpx/replay/artifacts.py:745:            enriched_values["target_ticks"] = round(float(target_points) / float(tick_size), 6)
app/mme_scalpx/replay/artifacts.py:749:                "formula": "target_points / tick_size",
app/mme_scalpx/replay/artifacts.py:750:                "target_points": target_points,
app/mme_scalpx/replay/artifacts.py:758:        if tick_size not in (None, 0) and stop_points is not None:
app/mme_scalpx/replay/artifacts.py:759:            enriched_values["stop_ticks"] = round(float(stop_points) / float(tick_size), 6)
app/mme_scalpx/replay/artifacts.py:762:                "formula": "stop_points / tick_size",
app/mme_scalpx/replay/artifacts.py:763:                "stop_points": stop_points,
app/mme_scalpx/replay/artifacts.py:775:                "target_points": "points",
app/mme_scalpx/replay/artifacts.py:776:                "stop_points": "points",
app/mme_scalpx/replay/contracts.py:324:    "exit_price",
app/mme_scalpx/replay/contracts.py:640:    exit_price: float | int | None = None
app/mme_scalpx/replay/contracts.py:2596:    "exit_price",
app/mme_scalpx/replay/fill_model.py:76:    fill_qty: int
app/mme_scalpx/replay/fill_model.py:77:    fill_price: float | None
app/mme_scalpx/replay/fill_model.py:119:        fill_price = _resolve_immediate_market_fill_price(request)
app/mme_scalpx/replay/fill_model.py:120:        if fill_price is None:
app/mme_scalpx/replay/fill_model.py:125:                fill_qty=0,
app/mme_scalpx/replay/fill_model.py:126:                fill_price=None,
app/mme_scalpx/replay/fill_model.py:128:                reason="no_fill_price_available",
app/mme_scalpx/replay/fill_model.py:135:            slippage = fill_price - reference
app/mme_scalpx/replay/fill_model.py:141:            fill_qty=request.qty,
app/mme_scalpx/replay/fill_model.py:142:            fill_price=fill_price,
app/mme_scalpx/replay/fill_model.py:172:        fill_price = _resolve_limit_touch_fill_price(request)
app/mme_scalpx/replay/fill_model.py:173:        if fill_price is None:
app/mme_scalpx/replay/fill_model.py:178:                fill_qty=0,
app/mme_scalpx/replay/fill_model.py:179:                fill_price=None,
app/mme_scalpx/replay/fill_model.py:188:            slippage = fill_price - reference
app/mme_scalpx/replay/fill_model.py:194:            fill_qty=request.qty,
app/mme_scalpx/replay/fill_model.py:195:            fill_price=fill_price,
app/mme_scalpx/replay/fill_model.py:247:        "fill_qty": result.fill_qty,
app/mme_scalpx/replay/fill_model.py:248:        "fill_price": result.fill_price,
app/mme_scalpx/replay/fill_model.py:294:def _resolve_immediate_market_fill_price(request: ReplayFillRequest) -> float | None:
app/mme_scalpx/replay/fill_model.py:304:def _resolve_limit_touch_fill_price(request: ReplayFillRequest) -> float | None:
app/mme_scalpx/services/features.py:3414:                "target_points": DEFAULT_TARGET_POINTS,
app/mme_scalpx/services/features.py:3415:                "stop_points": DEFAULT_STOP_POINTS,
app/mme_scalpx/services/features.py:3848:                    "target_points": DEFAULT_TARGET_POINTS,
app/mme_scalpx/services/features.py:3849:                    "stop_points": DEFAULT_STOP_POINTS,
app/mme_scalpx/services/features.py:4148:            frame.setdefault("target_points", DEFAULT_TARGET_POINTS)
app/mme_scalpx/services/features.py:4149:            frame.setdefault("stop_points", DEFAULT_STOP_POINTS)
app/mme_scalpx/services/feature_family/miso_surface.py:397:    target_points = _threshold_float(thresholds, "TARGET_POINTS", DEFAULT_TARGET_POINTS)
app/mme_scalpx/services/feature_family/miso_surface.py:398:    hard_stop_points = _threshold_float(thresholds, "HARD_STOP_POINTS", DEFAULT_HARD_STOP_POINTS)
app/mme_scalpx/services/feature_family/miso_surface.py:399:    disaster_stop_points = _threshold_float(thresholds, "DISASTER_STOP_POINTS", DEFAULT_DISASTER_STOP_POINTS)
app/mme_scalpx/services/feature_family/miso_surface.py:604:            "target_points": target_points,
app/mme_scalpx/services/feature_family/miso_surface.py:605:            "hard_stop_points": hard_stop_points,
app/mme_scalpx/services/feature_family/miso_surface.py:606:            "disaster_stop_points": disaster_stop_points,
app/mme_scalpx/services/feature_family/common.py:453:    target_points: Any = None,
app/mme_scalpx/services/feature_family/common.py:454:    stop_points: Any = None,
app/mme_scalpx/services/feature_family/common.py:464:        "target_points": _safe_float(target_points, None),
app/mme_scalpx/services/feature_family/common.py:465:        "stop_points": _safe_float(stop_points, None),
app/mme_scalpx/services/feature_family/contracts.py:326:    "target_points",
app/mme_scalpx/services/feature_family/contracts.py:327:    "stop_points",
app/mme_scalpx/services/feature_family/contracts.py:938:        "target_points": None,
app/mme_scalpx/services/feature_family/contracts.py:939:        "stop_points": None,
app/mme_scalpx/services/strategy_family/misb.py:290:    target_points: float = TARGET_POINTS
app/mme_scalpx/services/strategy_family/misb.py:291:    stop_points: float = HARD_STOP_POINTS
app/mme_scalpx/services/strategy_family/misb.py:312:            "target_points": self.target_points,
app/mme_scalpx/services/strategy_family/misb.py:313:            "stop_points": self.stop_points,
app/mme_scalpx/services/strategy_family/misb.py:1036:    target_points = safe_float(data.get("target_points"), 0.0)
app/mme_scalpx/services/strategy_family/misb.py:1037:    stop_points = safe_float(data.get("stop_points"), 0.0)
app/mme_scalpx/services/strategy_family/misb.py:1059:    if round(target_points, 6) != round(TARGET_POINTS, 6):
app/mme_scalpx/services/strategy_family/misb.py:1062:            reason="candidate_target_points_mismatch",
app/mme_scalpx/services/strategy_family/misb.py:1064:            extra={"expected": TARGET_POINTS, "actual": target_points},
app/mme_scalpx/services/strategy_family/misb.py:1067:    if round(stop_points, 6) != round(HARD_STOP_POINTS, 6):
app/mme_scalpx/services/strategy_family/misb.py:1070:            reason="candidate_stop_points_mismatch",
app/mme_scalpx/services/strategy_family/misb.py:1072:            extra={"expected": HARD_STOP_POINTS, "actual": stop_points},
app/mme_scalpx/services/strategy_family/misc.py:302:    target_points: float = TARGET_POINTS
app/mme_scalpx/services/strategy_family/misc.py:303:    stop_points: float = HARD_STOP_POINTS
app/mme_scalpx/services/strategy_family/misc.py:327:            "target_points": self.target_points,
app/mme_scalpx/services/strategy_family/misc.py:328:            "stop_points": self.stop_points,
app/mme_scalpx/services/strategy_family/misc.py:1157:    target_points = safe_float(data.get("target_points"), 0.0)
app/mme_scalpx/services/strategy_family/misc.py:1158:    stop_points = safe_float(data.get("stop_points"), 0.0)
app/mme_scalpx/services/strategy_family/misc.py:1180:    if round(target_points, 6) != round(TARGET_POINTS, 6):
app/mme_scalpx/services/strategy_family/misc.py:1183:            reason="candidate_target_points_mismatch",
app/mme_scalpx/services/strategy_family/misc.py:1185:            extra={"expected": TARGET_POINTS, "actual": target_points},
app/mme_scalpx/services/strategy_family/misc.py:1188:    if round(stop_points, 6) != round(HARD_STOP_POINTS, 6):
app/mme_scalpx/services/strategy_family/misc.py:1191:            reason="candidate_stop_points_mismatch",
app/mme_scalpx/services/strategy_family/misc.py:1193:            extra={"expected": HARD_STOP_POINTS, "actual": stop_points},
app/mme_scalpx/services/strategy_family/misr.py:292:    target_points: float = TARGET_POINTS
app/mme_scalpx/services/strategy_family/misr.py:293:    stop_points: float = HARD_STOP_POINTS
app/mme_scalpx/services/strategy_family/misr.py:315:            "target_points": self.target_points,
app/mme_scalpx/services/strategy_family/misr.py:316:            "stop_points": self.stop_points,
app/mme_scalpx/services/strategy_family/misr.py:1280:    target_points = safe_float(data.get("target_points"), 0.0)
app/mme_scalpx/services/strategy_family/misr.py:1281:    stop_points = safe_float(data.get("stop_points"), 0.0)
app/mme_scalpx/services/strategy_family/misr.py:1303:    if round(target_points, 6) != round(TARGET_POINTS, 6):
app/mme_scalpx/services/strategy_family/misr.py:1306:            reason="candidate_target_points_mismatch",
app/mme_scalpx/services/strategy_family/misr.py:1308:            extra={"expected": TARGET_POINTS, "actual": target_points},
app/mme_scalpx/services/strategy_family/misr.py:1311:    if round(stop_points, 6) != round(HARD_STOP_POINTS, 6):
app/mme_scalpx/services/strategy_family/misr.py:1314:            reason="candidate_stop_points_mismatch",
app/mme_scalpx/services/strategy_family/misr.py:1316:            extra={"expected": HARD_STOP_POINTS, "actual": stop_points},
app/mme_scalpx/services/strategy_family/arbitration.py:90:                "target_points": self.candidate.target_points,
app/mme_scalpx/services/strategy_family/arbitration.py:91:                "stop_points": self.candidate.stop_points,
app/mme_scalpx/services/strategy_family/arbitration.py:142:                    "target_points": self.selected.target_points,
app/mme_scalpx/services/strategy_family/arbitration.py:143:                    "stop_points": self.selected.stop_points,
app/mme_scalpx/services/strategy_family/mist.py:308:    target_points: float = TARGET_POINTS
app/mme_scalpx/services/strategy_family/mist.py:309:    stop_points: float = HARD_STOP_POINTS
app/mme_scalpx/services/strategy_family/mist.py:330:            "target_points": self.target_points,
app/mme_scalpx/services/strategy_family/mist.py:331:            "stop_points": self.stop_points,
app/mme_scalpx/services/strategy_family/mist.py:1085:    target_points = safe_float(data.get("target_points"), 0.0)
app/mme_scalpx/services/strategy_family/mist.py:1086:    stop_points = safe_float(data.get("stop_points"), 0.0)
app/mme_scalpx/services/strategy_family/mist.py:1108:    if round(target_points, 6) != round(TARGET_POINTS, 6):
app/mme_scalpx/services/strategy_family/mist.py:1111:            reason="candidate_target_points_mismatch",
app/mme_scalpx/services/strategy_family/mist.py:1113:            extra={"expected": TARGET_POINTS, "actual": target_points},
app/mme_scalpx/services/strategy_family/mist.py:1116:    if round(stop_points, 6) != round(HARD_STOP_POINTS, 6):
app/mme_scalpx/services/strategy_family/mist.py:1119:            reason="candidate_stop_points_mismatch",
app/mme_scalpx/services/strategy_family/mist.py:1121:            extra={"expected": HARD_STOP_POINTS, "actual": stop_points},
app/mme_scalpx/services/strategy_family/decisions.py:222:            "stop_points": value.stop_points,
app/mme_scalpx/services/strategy_family/decisions.py:229:            "target_points": value.target_points,
app/mme_scalpx/services/strategy_family/decisions.py:291:    target_points = _optional_non_negative_float(data.get("target_points"), "target_points")
app/mme_scalpx/services/strategy_family/decisions.py:302:        and target_points is None
app/mme_scalpx/services/strategy_family/decisions.py:309:        target_points=target_points,
app/mme_scalpx/services/strategy_family/decisions.py:320:    stop_points = _optional_non_negative_float(data.get("stop_points"), "stop_points")
app/mme_scalpx/services/strategy_family/decisions.py:331:        and stop_points is None
app/mme_scalpx/services/strategy_family/decisions.py:338:        stop_points=stop_points,
app/mme_scalpx/services/strategy_family/decisions.py:359:    target_points = _optional_non_negative_float(candidate.target_points, "candidate.target_points")
app/mme_scalpx/services/strategy_family/decisions.py:363:        and target_points is None
