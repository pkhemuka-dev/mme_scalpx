# LANE-X-R36F_CONTROLLED_PAPER_CONFIG_CONFLICT_EXACT_AUDIT_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_20260614_110145

classification: PASS_LANE_X_R36F_CONTROLLED_PAPER_CONFIG_CONFLICT_EXACT_AUDIT_DONE_NO_PATCH_NO_START_NO_ORDER_NO_PAPER
proof: `run/proofs/LANE-X-R36F_CONTROLLED_PAPER_CONFIG_CONFLICT_EXACT_AUDIT_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_20260614_110145.json`

pstatus_rc=0 summary_rc=0
paper_route_allowed=false
pstatus_reason=OBSERVE_ONLY_ACTIVE
safety pre=0/0/0 post=0/0/0 proc=0/0 replay_proc=0

## Interpretation
- This audit identifies the exact controlled-paper env/gate source conflict.
- It does not patch and does not approve paper.
- Current pstatus remains fail-closed.

## Config conflict summary
{
  "current_env": {
    "B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY": "1",
    "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME": "",
    "SCALPX_CONTROLLED_PAPER_ARMED": "",
    "SCALPX_CONTROLLED_PAPER_SCOPE_ACK": "",
    "SCALPX_ENABLE_LIVE": "",
    "SCALPX_ENABLE_PAPER": "",
    "SCALPX_OBSERVE_ONLY": "1",
    "SCALPX_PAPER_ARMED": ""
  },
  "env_key_reference_counts": {
    "B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY": 2,
    "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME": 10,
    "SCALPX_CONTROLLED_PAPER_ARMED": 1,
    "SCALPX_CONTROLLED_PAPER_SCOPE_ACK": 9,
    "SCALPX_ENABLE_LIVE": 7,
    "SCALPX_ENABLE_PAPER": 6,
    "SCALPX_OBSERVE_ONLY": 3,
    "SCALPX_PAPER_ARMED": 5
  },
  "paper_route_allowed": false,
  "pstatus_reason": "OBSERVE_ONLY_ACTIVE",
  "recommended_r36g_patch": "Document controlled_paper_route.py as source of truth and make pstatus/dashboard read that verdict; do not alter strategy thresholds or enable paper.",
  "risk_points": [
    "There are multiple env gates and naming variants.",
    "pstatus currently fails closed because observe-only is active.",
    "controlled_paper_route.py is the correct source-of-truth candidate.",
    "Do not paper-arm until one canonical gate contract is documented and same-session checks pass."
  ]
}

## Config conflict summary errors

## Full config conflict audit
## controlled_paper_route.py
     1	"""Fail-closed controlled-paper route guard surface.
     2	
     3	This module is intentionally side-effect free. It does not start services, touch
     4	Redis, call brokers, place paper orders, or mutate position/order state.
     5	
     6	A6-PAPER-R4 adds this as an additive guard surface only. Runtime wiring and any
     7	paper execution path require separate approvals and later proofs.
     8	"""
     9	
    10	from __future__ import annotations
    11	
    12	from dataclasses import dataclass
    13	from typing import Mapping
    14	
    15	ENV_OBSERVE_ONLY = "SCALPX_OBSERVE_ONLY"
    16	ENV_ALLOW_CONTROLLED_PAPER_RUNTIME = "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME"
    17	ENV_CONTROLLED_PAPER_SCOPE_ACK = "SCALPX_CONTROLLED_PAPER_SCOPE_ACK"
    18	ENV_REAL_LIVE_ALLOWED = "SCALPX_REAL_LIVE_ALLOWED"
    19	ENV_ALLOW_REAL_LIVE = "SCALPX_ALLOW_REAL_LIVE"
    20	ENV_ALLOW_BROKER_ORDERS = "SCALPX_ALLOW_BROKER_ORDERS"
    21	ENV_PAPER_ARMED = "SCALPX_PAPER_ARMED"
    22	ENV_ENABLE_PAPER = "SCALPX_ENABLE_PAPER"
    23	ENV_ENABLE_LIVE = "SCALPX_ENABLE_LIVE"
    24	
    25	CONTROLLED_PAPER_SCOPE_ACK_EXPECTED = (
    26	    "I ACKNOWLEDGE CONTROLLED PAPER ONLY: "
    27	    "NO REAL LIVE, NO BROKER ORDER, NO REAL MONEY, "
    28	    "ONE APPROVED SCOPE ONLY, POSITION MUST START FLAT"
    29	)
    30	
    31	TRUTHY_VALUES = frozenset({"1", "true", "yes", "y", "on"})
    32	LIVE_AND_BROKER_BLOCK_FLAGS = (
    33	    ENV_REAL_LIVE_ALLOWED,
    34	    ENV_ALLOW_REAL_LIVE,
    35	    ENV_ALLOW_BROKER_ORDERS,
    36	    ENV_ENABLE_LIVE,
    37	)
    38	
    39	
    40	@dataclass(frozen=True)
    41	class ControlledPaperRouteVerdict:
    42	    """Pure-data result for controlled-paper route gating."""
    43	
    44	    allowed: bool
    45	    reason: str
    46	    observe_only: bool
    47	    paper_enabled: bool
    48	    paper_armed: bool
    49	    controlled_runtime_allowed: bool
    50	    scope_ack_ok: bool
    51	    broker_live_blocked: bool
    52	
    53	    def as_dict(self) -> dict[str, object]:
    54	        return {
    55	            "allowed": self.allowed,
    56	            "reason": self.reason,
    57	            "observe_only": self.observe_only,
    58	            "paper_enabled": self.paper_enabled,
    59	            "paper_armed": self.paper_armed,
    60	            "controlled_runtime_allowed": self.controlled_runtime_allowed,
    61	            "scope_ack_ok": self.scope_ack_ok,
    62	            "broker_live_blocked": self.broker_live_blocked,
    63	        }
    64	
    65	
    66	def _truthy(value: object) -> bool:
    67	    return str(value or "").strip().lower() in TRUTHY_VALUES
    68	
    69	
    70	def _env_truthy(env: Mapping[str, object], name: str) -> bool:
    71	    return _truthy(env.get(name))
    72	
    73	
    74	def evaluate_controlled_paper_route_env(
    75	    env: Mapping[str, object],
    76	    *,
    77	    position_flat: bool,
    78	    risk_execution_absent: bool,
    79	    orders_zero: bool,
    80	) -> ControlledPaperRouteVerdict:
    81	    """Evaluate controlled-paper route eligibility without side effects.
    82	
    83	    The default is fail-closed. This function only returns ``allowed=True`` when
    84	    every explicit paper gate is present, live/broker flags are blocked, and the
    85	    external safety facts prove flat/no-risk/no-orders.
    86	    """
    87	
    88	    observe_only = _env_truthy(env, ENV_OBSERVE_ONLY)
    89	    controlled_runtime_allowed = _env_truthy(env, ENV_ALLOW_CONTROLLED_PAPER_RUNTIME)
    90	    paper_enabled = _env_truthy(env, ENV_ENABLE_PAPER)
    91	    paper_armed = _env_truthy(env, ENV_PAPER_ARMED)
    92	    scope_ack_ok = str(env.get(ENV_CONTROLLED_PAPER_SCOPE_ACK, "")).strip() == CONTROLLED_PAPER_SCOPE_ACK_EXPECTED
    93	    broker_live_blocked = not any(_env_truthy(env, name) for name in LIVE_AND_BROKER_BLOCK_FLAGS)
    94	
    95	    if observe_only:
    96	        return ControlledPaperRouteVerdict(False, "OBSERVE_ONLY_ACTIVE", observe_only, paper_enabled, paper_armed, controlled_runtime_allowed, scope_ack_ok, broker_live_blocked)
    97	    if not controlled_runtime_allowed:
    98	        return ControlledPaperRouteVerdict(False, "CONTROLLED_PAPER_RUNTIME_NOT_ALLOWED", observe_only, paper_enabled, paper_armed, controlled_runtime_allowed, scope_ack_ok, broker_live_blocked)
    99	    if not scope_ack_ok:
   100	        return ControlledPaperRouteVerdict(False, "CONTROLLED_PAPER_SCOPE_ACK_MISSING_OR_INVALID", observe_only, paper_enabled, paper_armed, controlled_runtime_allowed, scope_ack_ok, broker_live_blocked)
   101	    if not paper_enabled:
   102	        return ControlledPaperRouteVerdict(False, "PAPER_NOT_ENABLED", observe_only, paper_enabled, paper_armed, controlled_runtime_allowed, scope_ack_ok, broker_live_blocked)
   103	    if not paper_armed:
   104	        return ControlledPaperRouteVerdict(False, "PAPER_NOT_ARMED", observe_only, paper_enabled, paper_armed, controlled_runtime_allowed, scope_ack_ok, broker_live_blocked)
   105	    if not broker_live_blocked:
   106	        return ControlledPaperRouteVerdict(False, "BROKER_OR_LIVE_FLAG_ACTIVE", observe_only, paper_enabled, paper_armed, controlled_runtime_allowed, scope_ack_ok, broker_live_blocked)
   107	    if not orders_zero:
   108	        return ControlledPaperRouteVerdict(False, "ORDERS_STREAM_NOT_ZERO", observe_only, paper_enabled, paper_armed, controlled_runtime_allowed, scope_ack_ok, broker_live_blocked)
   109	    if not position_flat:
   110	        return ControlledPaperRouteVerdict(False, "POSITION_NOT_FLAT", observe_only, paper_enabled, paper_armed, controlled_runtime_allowed, scope_ack_ok, broker_live_blocked)
   111	    if not risk_execution_absent:
   112	        return ControlledPaperRouteVerdict(False, "RISK_OR_EXECUTION_ALREADY_RUNNING", observe_only, paper_enabled, paper_armed, controlled_runtime_allowed, scope_ack_ok, broker_live_blocked)
   113	
   114	    return ControlledPaperRouteVerdict(True, "CONTROLLED_PAPER_ROUTE_ALLOWED_BY_GATES", observe_only, paper_enabled, paper_armed, controlled_runtime_allowed, scope_ack_ok, broker_live_blocked)
   115	
   116	
   117	def build_fail_closed_controlled_paper_verdict() -> ControlledPaperRouteVerdict:
   118	    """Return the canonical no-env fail-closed verdict."""
   119	
   120	    return evaluate_controlled_paper_route_env(
   121	        {},
   122	        position_flat=False,
   123	        risk_execution_absent=False,
   124	        orders_zero=False,
   125	    )

## main.py env gate references
127:        and not os.environ.get("SCALPX_PAPER_ARMED")
128:        and not os.environ.get("SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME")
1125:        "SCALPX_ENABLE_LIVE",
1131:        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
1132:        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
1133:        "SCALPX_PAPER_ARMED",
1134:        "SCALPX_ENABLE_PAPER",

## strategy.py controlled paper bridge
1873:_A6_LIVE_R2H_RUNTIME_ENV_KEY = "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME"
1874:_A6_LIVE_R2H_SCOPE_ACK_ENV_KEY = "SCALPX_CONTROLLED_PAPER_SCOPE_ACK"
1917:# BEGIN R38R_CLASSIC_CONTROLLED_PAPER_ACTIVATION_BRIDGE
1924:    allow = str(_r38r_os.environ.get("SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME", "")).strip() == "1"
1925:    ack = str(_r38r_os.environ.get("SCALPX_CONTROLLED_PAPER_SCOPE_ACK", "")).strip().upper()
1933:            "SCALPX_ENABLE_LIVE",
1984:    return "paper_armed" if _r38r_controlled_paper_env_truth().get("enabled") else ACTIVATION_REPORT_MODE
1989:# END R38R_CLASSIC_CONTROLLED_PAPER_ACTIVATION_BRIDGE
2039:        blockers.append("CONTROLLED_PAPER_RUNTIME_NOT_ENABLED")
2066:        "status": "CONTROLLED_PAPER_ACTIVATION_GATE_PASS" if ok else "CONTROLLED_PAPER_ACTIVATION_GATE_BLOCKED",
2086:CONTROLLED_PAPER_STRATEGY_BRIDGE_VERSION = "a6_paper_r10_report_only_v1"
2118:    payload["strategy_bridge_version"] = CONTROLLED_PAPER_STRATEGY_BRIDGE_VERSION
2146:        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
2147:        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
2151:        "SCALPX_PAPER_ARMED",
2152:        "SCALPX_ENABLE_PAPER",
2153:        "SCALPX_ENABLE_LIVE",
2337:            out["status"] = "CONTROLLED_PAPER_ACTIVATION_GATE_BLOCKED"
2341:            out["status"] = "CONTROLLED_PAPER_ACTIVATION_GATE_OK_REPORT_ONLY"

## dashboard env display references
44:    "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
45:    "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
50:    "SCALPX_ENABLE_PAPER",
51:    "SCALPX_ENABLE_LIVE",
352:            safe = _pick_first(obj, ["safe_to_promote", "live_orders_allowed", "activation_report_only"], "-")
387:            "<tr><td>Paper status</td><td class='mono'>PAPER BLOCKED - dashboard never promotes paper</td></tr>"
431:        # Intentionally capped for dashboard speed. It is a live visibility panel, not an audit engine.
536:        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
537:        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
542:        "SCALPX_ENABLE_PAPER",
543:        "SCALPX_ENABLE_LIVE",
614:        ("A7 interpretation", "capture/readiness visibility only - dashboard must not control live/paper services"),
699:REPLAY_DATASET_SOURCES = ["latest_available", "sealed_live_capture", "replay_dataset", "evidence_bundle"]
958:        "<tr><td>MIV-R label</td><td class='mono'>MIV-R = research/audit probe only, not production strategy, not paper/live candidate source</td></tr>"
968:        "<p class='mono'>Historical what-would-have-happened view only. This section never changes the Live Truth Board or paper/live readiness.</p>"
972:        + "<p class='mono'>Replay-only synthetic shadow model. not broker PnL, not paper PnL, not live PnL. PNL_COMPUTED_REPLAY_ONLY_SYNTHETIC_SHADOW_MODEL_NOT_BROKER_NOT_PAPER_NOT_LIVE. Keep separate from Official closed-trade PnL, Broker/Paper/Live PnL, and Live Truth Board.</p>"
1009:    live_feeds = sum(1 for x in rows[:5] if x[4] == "LIVE")
1110:<div><h1>MME-ScalpX OPS Dashboard R3H-LX-R3E</h1><div class="sub">R3H-LX-R3E read-only · HOLD reason capped · action distribution · capture progress · paper blocked · no writes · no orders</div></div>
1116:<div class="card"><div class="label">Feeds Live</div><div class="big">{live_feeds}/5</div></div>
1288:        "<div class='panel'><h3>5. NEXT ACTION</h3><h2 class='mono'>%s</h2><p>Dashboard is read-only. It must not promote paper/live.</p></div>"

## configs and docs references
etc/replay_optimization/ml_export_contract.json:20:    "paper_armed_enablement": true,
etc/replay_optimization/handoff/lane_e_candidate_materialization_intake_contract.json:54:    "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME unset",
etc/replay_optimization/handoff/lane_e_candidate_materialization_intake_contract.json:55:    "SCALPX_CONTROLLED_PAPER_SCOPE_ACK unset",
etc/strategy_family/rollout/controlled_paper_trial_enablement_from_25v25w.yaml:10:paper_armed_enabled: true
etc/strategy_family/rollout/paper_armed_readiness_gate.yaml:2:gate_id: batch25w_paper_armed_readiness_gate
etc/strategy_family/rollout/paper_armed_readiness_gate.yaml:6:paper_armed_enabled_by_default: false
etc/strategy_family/rollout/paper_armed_readiness_gate.yaml:7:auto_enable_paper_armed: false
etc/strategy_family/rollout/paper_armed_readiness_gate.yaml:11:  allowed_first_runtime_mode: paper_armed
etc/strategy_family/rollout/controlled_paper_trial_scope_from_25v25w.yaml:7:  batch25w_paper_armed_readiness_gate: PASS_READY_FOR_CONTROLLED_PAPER_PREP
etc/strategy_family/rollout/controlled_paper_trial_scope_from_25v25w.yaml:12:paper_armed_enabled_by_this_file: false
etc/strategy_family/rollout/controlled_paper_trial_scope_from_25v25w.yaml:13:paper_armed_should_be_enabled_now: false
etc/strategy_family/rollout/controlled_paper_trial_scope_from_25v25w.yaml:14:auto_enable_paper_armed: false
etc/strategy_family/rollout/controlled_paper_trial_scope_from_25v25w.yaml:62:  paper_armed_enabled: false
etc/proof_registry.yaml:8:# - list P1/P0 proof gaps required before paper_armed.
etc/proof_registry.yaml:89:      - paper_armed_readiness
etc/proof_registry.yaml:106:      - paper_armed_readiness
etc/proof_registry.yaml:129:      - paper_armed_readiness
etc/proof_registry.yaml:138:required_before_paper_armed:
etc/replay/scenarios/replay_scenario_profile_manifest_v1.json:7:  "paper_armed_approved": false,
etc/replay/scenarios/replay_scenario_profile_manifest_v1.json:23:      "paper_armed_approved": false,
etc/replay/scenarios/replay_scenario_profile_manifest_v1.json:51:      "paper_armed_approved": false,
etc/replay/scenarios/replay_scenario_profile_manifest_v1.json:79:      "paper_armed_approved": false,
etc/replay/scenarios/replay_scenario_profile_manifest_v1.json:104:      "paper_armed_approved": false,
etc/replay/scenarios/replay_scenario_profile_manifest_v1.json:129:      "paper_armed_approved": false,
etc/replay/scenarios/replay_scenario_profile_manifest_v1.json:155:      "paper_armed_approved": false,
etc/replay/scenarios/replay_scenario_profile_manifest_v1.json:181:      "paper_armed_approved": false,
etc/replay/scenarios/replay_scenario_profile_manifest_v1.json:209:      "paper_armed_approved": false,
etc/replay/scenarios/replay_scenario_profile_manifest_v1.json:242:      "paper_armed_approved": false,
etc/replay/scenarios/replay_scenario_profile_manifest_v1.json:268:      "paper_armed_approved": false,
etc/replay/scenarios/replay_scenario_profile_manifest_v1.json:296:      "paper_armed_approved": false,
etc/replay/scenarios/replay_scenario_profile_manifest_v1.json:316:      "paper_armed_approved": false,
etc/replay/scenarios/replay_scenario_profile_manifest_v1.json:340:      "paper_armed_approved": false,
etc/replay/scenarios/replay_scenario_profile_manifest_v1.json:365:      "paper_armed_approved": false,
etc/replay/scenarios/replay_scenario_profile_manifest_v1.json:393:      "paper_armed_approved": false,
etc/replay/scenarios/replay_scenario_profile_manifest_v1.json:422:      "paper_armed_approved": false,
etc/replay/scenarios/replay_scenario_profile_manifest_v1.json:448:      "paper_armed_approved": false,
etc/replay/scenarios/replay_scenario_profile_manifest_v1.json:471:      "paper_armed_approved": false,
etc/replay/scenarios/replay_scenario_profile_manifest_v1.json:493:      "paper_armed_approved": false,
etc/replay/scenarios/replay_scenario_profile_manifest_v1.json:516:      "paper_armed_approved": false,
etc/replay/scenarios/replay_scenario_profile_manifest_v1.json:536:      "paper_armed_approved": false,
etc/replay/scenarios/replay_scenario_profile_manifest_v1.json:563:      "paper_armed_approved": false,
etc/replay/schemas/replay_deterministic_reset_integrity_contract_v1.json:11:  "paper_armed_approved": false,
etc/replay/schemas/observe_only_live_evidence_existing_proof_package_contract_v1.json:10:  "paper_armed_approved": false,
etc/replay/schemas/observe_only_live_evidence_existing_proof_package_contract_v1.json:33:    "paper_armed_readiness",
etc/replay/schemas/replay_scenario_profile_contract_v1.json:5:  "paper_armed_approved": false,
etc/replay/schemas/replay_scenario_profile_contract_v1.json:21:    "paper_armed_approved",
etc/replay/schemas/replay_risk_execution_shadow_contract_v1.json:5:  "paper_armed_approved": false,
etc/replay/schemas/replay_risk_execution_shadow_contract_v1.json:23:    "paper_armed_approved",
etc/replay/schemas/replay_risk_execution_shadow_contract_v1.json:43:    "paper_armed_approved",
etc/replay/schemas/replay_workstation_acceptance_gate_contract_v1.json:6:  "paper_armed_approved": false,
etc/replay/schemas/replay_workstation_acceptance_gate_contract_v1.json:40:    "paper_armed_readiness",
etc/replay/schemas/observe_only_market_session_capture_execution_contract_v1.json:16:  "paper_armed_approved": false,
etc/replay/schemas/replay_feature_family_adapter_contract_v1.json:5:  "paper_armed_approved": false,
etc/replay/schemas/replay_feature_family_adapter_contract_v1.json:35:    "paper_armed_approved",
etc/replay/schemas/replay_live_parity_audit_plan_contract_v1.json:6:  "paper_armed_approved": false,
etc/replay/schemas/replay_live_parity_audit_plan_contract_v1.json:54:    "paper_armed_readiness",
etc/replay/schemas/observe_only_market_session_capture_runbook_contract_v1.json:9:  "paper_armed_approved": false,
etc/replay/schemas/replay_live_shape_transport_contract_v1.json:5:  "paper_armed_approved": false,
etc/replay/schemas/replay_live_shape_transport_contract_v1.json:28:    "paper_armed_approved",
etc/replay/schemas/replay_live_shape_transport_contract_v1.json:40:    "paper_armed_approved",
etc/replay/schemas/replay_batch_runner_contract_v1.json:5:  "paper_armed_approved": false,
etc/replay/schemas/replay_batch_runner_contract_v1.json:28:    "paper_armed_approved",
etc/replay/schemas/observe_only_actual_evidence_map_generation_contract_v1.json:9:  "paper_armed_approved": false,
etc/replay/schemas/observe_only_live_evidence_capture_contract_v1.json:11:  "paper_armed_approved": false,
etc/replay/schemas/observe_only_live_evidence_capture_contract_v1.json:50:    "paper_armed_readiness",
etc/replay/schemas/replay_report_export_contract_v1.json:5:  "paper_armed_approved": false,
etc/replay/schemas/replay_dataset_contract_v1.json:11:  "paper_armed_approved": false,
etc/replay/schemas/replay_safety_firewall_contract_v1.json:11:  "paper_armed_approved": false,
etc/replay/schemas/observe_only_actual_evidence_map_collection_contract_v1.json:11:  "paper_armed_approved": false,
etc/replay/schemas/replay_strategy_family_adapter_contract_v1.json:5:  "paper_armed_approved": false,
etc/replay/schemas/replay_strategy_family_adapter_contract_v1.json:38:    "paper_armed_approved",
etc/replay/schemas/replay_strategy_family_adapter_contract_v1.json:53:    "paper_armed_approved",
etc/replay/schemas/replay_experiment_workstation_contract_v1.json:5:  "paper_armed_approved": false,
etc/replay/schemas/replay_experiment_workstation_contract_v1.json:33:    "paper_armed_approved",
etc/replay/forensics/replay_report_export_manifest_v1.json:11:  "paper_armed_approved": false,
etc/replay/integrity/replay_integrity_policy.yaml:4:paper_armed_approved: false
etc/replay/datasets/replay_dataset_contract_manifest_v1.json:21:    "paper_armed_approved": false,
etc/replay/datasets/replay_live_surface_contract_v2.json:10:    "paper_armed_approved": false,
etc/replay/experiments/replay_experiment_profile_manifest_v1.json:14:  "paper_armed_approved": false,
etc/replay/experiments/replay_experiment_profile_manifest_v1.json:42:      "paper_armed_approved": false,
etc/replay/experiments/replay_experiment_profile_manifest_v1.json:130:      "paper_armed_approved": false,
etc/replay/experiments/replay_experiment_profile_manifest_v1.json:205:      "paper_armed_approved": false,
etc/replay/experiments/replay_experiment_profile_manifest_v1.json:288:      "paper_armed_approved": false,
etc/replay/experiments/replay_experiment_profile_manifest_v1.json:377:      "paper_armed_approved": false,
etc/replay/experiments/replay_experiment_profile_manifest_v1.json:435:      "paper_armed_approved": false,
etc/replay/parity/strategy_activation_reference_discovery_bounded_29bd_r1.json:175:  "paper_armed_approved": false,
etc/replay/parity/topology_plan_scope_runtime_gap_audit_29v.json:191:  "paper_armed_approved": false,
etc/replay/parity/topology_notes_probe_failure_audit_29ag_r1.json:154:  "paper_armed_approved": false,
etc/replay/parity/guarded_offline_replay_dry_run_cli_audit_28p_r1.json:41:      "paper_armed_approved": false,
etc/replay/parity/guarded_offline_replay_dry_run_cli_audit_28p_r1.json:57:      "paper_armed_approved": false,
etc/replay/parity/guarded_offline_replay_dry_run_cli_audit_28p_r1.json:73:      "paper_armed_approved": false,
etc/replay/parity/guarded_offline_replay_dry_run_cli_audit_28p_r1.json:89:      "paper_armed_approved": false,
etc/replay/parity/guarded_offline_replay_dry_run_cli_audit_28p_r1.json:105:      "paper_armed_approved": false,
etc/replay/parity/guarded_offline_replay_dry_run_cli_audit_28p_r1.json:114:  "paper_armed_approved": false,
etc/replay/parity/replay_engine_offline_context_bridge_29d.json:65:    "paper_armed_approved": false,
etc/replay/parity/replay_engine_offline_context_bridge_29d.json:127:      "paper_armed_approved": false,
etc/replay/parity/replay_engine_offline_context_bridge_29d.json:142:      "paper_armed_approved": false,
etc/replay/parity/replay_engine_offline_context_bridge_29d.json:158:      "paper_armed_approved": false,
etc/replay/parity/replay_engine_offline_context_bridge_29d.json:174:      "paper_armed_approved": false,
etc/replay/parity/replay_engine_offline_context_bridge_29d.json:190:      "paper_armed_approved": false,
etc/replay/parity/replay_engine_offline_context_bridge_29d.json:204:      "paper_armed_approved": false,
etc/replay/parity/replay_engine_offline_context_bridge_29d.json:217:      "paper_armed_approved": false,
etc/replay/parity/replay_engine_offline_context_bridge_29d.json:230:      "paper_armed_approved": false,
etc/replay/parity/replay_engine_offline_context_bridge_29d.json:243:      "paper_armed_approved": false,
etc/replay/parity/replay_engine_offline_context_bridge_29d.json:251:  "paper_armed_approved": false,
etc/replay/parity/replay_engine_offline_context_bridge_29d.json:285:    "stdout": "{\n  \"accepted_for\": \"REPLAY_ENGINE_OFFLINE_CONTEXT_BRIDGE_CONTRACT_ONLY\",\n  \"calls_broker_api\": false,\n  \"candidate_executed\": false,\n  \"comparison_completed\": false,\n  \"context_bridge_ready\": true,\n  \"execution_arming_created\": false,\n  \"full_live_replay_parity\": \"NOT_PROVEN_IN_29D\",\n  \"live_trading_approved\": false,\n  \"missing_execute_args_from_29c\": [\n    \"run_context\",\n    \"topology_plan\"\n  ],\n  \"next_batch\": \"Batch 29E \\u2014 materialize guarded offline ReplayEngine context objects, still not paper/live enablement.\",\n  \"next_path\": \"OFFLINE_CONTEXT_SURFACES_READY\",\n  \"paper_armed_approved\": false,\n  \"production_doctrine_changed\": false,\n  \"reads_live_redis\": false,\n  \"real_order_sent\": false,\n  \"replay_core_executed\": false,\n  \"replay_run_completed\": false,\n  \"run_context_bridge_ready\": true,\n  \"run_context_surface_count\": 17,\n  \"schema_version\": \"offline_context_bridge_result_29d_v1\",\n  \"stage_executor_bridge_ready\": true,\n  \"stage_executor_surface_count\": 18,\n  \"starts_services\": false,\n  \"topology_plan_bridge_ready\": true,\n  \"topology_plan_surface_count\": 54,\n  \"writes_live_redis\": false\n}\n",
etc/replay/parity/risk_output_semantic_precheck_rollup_29cx.json:24:  "paper_armed_approved": false,
etc/replay/parity/offline_stage_order_index_alias_repair_29q.json:64:      "paper_armed_approved": false,
etc/replay/parity/offline_stage_order_index_alias_repair_29q.json:77:      "paper_armed_approved": false,
etc/replay/parity/offline_stage_order_index_alias_repair_29q.json:90:      "paper_armed_approved": false,
etc/replay/parity/offline_stage_order_index_alias_repair_29q.json:103:      "paper_armed_approved": false,
etc/replay/parity/offline_stage_order_index_alias_repair_29q.json:116:      "paper_armed_approved": false,
etc/replay/parity/offline_stage_order_index_alias_repair_29q.json:129:      "paper_armed_approved": false,
etc/replay/parity/offline_stage_order_index_alias_repair_29q.json:142:      "paper_armed_approved": false,
etc/replay/parity/offline_stage_order_index_alias_repair_29q.json:155:      "paper_armed_approved": false,
etc/replay/parity/offline_stage_order_index_alias_repair_29q.json:168:      "paper_armed_approved": false,
etc/replay/parity/offline_stage_order_index_alias_repair_29q.json:181:      "paper_armed_approved": false,
etc/replay/parity/offline_stage_order_index_alias_repair_29q.json:194:      "paper_armed_approved": false,
etc/replay/parity/offline_stage_order_index_alias_repair_29q.json:207:      "paper_armed_approved": false,
etc/replay/parity/offline_stage_order_index_alias_repair_29q.json:218:  "paper_armed_approved": false,
etc/replay/parity/guarded_provider_feature_summary_validation_rescue_29aw_r1.json:209:  "paper_armed_approved": false,
etc/replay/parity/replay_provider_feature_source_enrichment_contract_29au.json:233:  "paper_armed_approved": false,
etc/replay/parity/move_provider_feature_emit_before_return_29aw_r5.json:191:  "guarded_retry_stdout_tail": "{\n  \"accepted_for\": \"GUARDED_REPLAY_ENGINE_EXECUTE_DRY_RUN_ONLY\",\n  \"calls_broker_api\": false,\n  \"candidate_executed\": true,\n  \"comparison_completed\": false,\n  \"context_reconstruction_ready\": true,\n  \"engine_instance_ready\": true,\n  \"execution_arming_created\": false,\n  \"execution_attempted\": true,\n  \"execution_ok\": true,\n  \"full_live_replay_parity\": \"NOT_PROVEN_IN_29G\",\n  \"live_trading_approved\": false,\n  \"next_batch\": \"Batch 29H \\u2014 inspect ReplayEngine dry-run outputs and build replay/live parity comparison contract, still not paper/live enablement.\",\n  \"paper_armed_approved\": false,\n  \"production_doctrine_changed\": false,\n  \"reads_live_redis\": false,\n  \"real_order_sent\": false,\n  \"replay_core_executed\": true,\n  \"replay_run_completed\": true,\n  \"schema_version\": \"guarded_replay_engine_execute_result_29g_v1\",\n  \"starts_services\": false,\n  \"writes_live_redis\": false\n}\n",
etc/replay/parity/move_provider_feature_emit_before_return_29aw_r5.json:203:  "paper_armed_approved": false,
etc/replay/parity/stage_executor_mapping_wrapper_repair_29u_r2.json:134:  "paper_armed_approved": false,
etc/replay/parity/semantic_report_classify_consolidate_29cd.json:29:  "paper_armed_approved": false,
etc/replay/parity/semantic_replay_live_parity_review_29aj.json:165:  "paper_armed_approved": false,
etc/replay/parity/concrete_replay_engine_core_wiring_contract_28w.json:21:  "paper_armed_approved": false,
etc/replay/parity/same_session_temporal_alignment_precheck_rollup_29dd.json:25:  "paper_armed_approved": false,
etc/replay/parity/risk_output_semantic_trace_validator_contract_29cw.json:28:  "paper_armed_approved": false,
etc/replay/parity/topology_notes_values_preservation_repair_29ag_r2.json:140:  "paper_armed_approved": false,
etc/replay/parity/replay_provider_feature_summary_materialization_29ar.json:195:  "paper_armed_approved": false,
etc/replay/parity/post_r7_emission_output_root_audit_29aw_r8.json:194:  "paper_armed_approved": false,
etc/replay/parity/inspect_29ab_retry_failure_29ac.json:12:    "paper_armed_approved": false,
etc/replay/parity/strategy_activation_reference_discovery_29bd.json:175:  "paper_armed_approved": false,
etc/replay/parity/runtime_feature_field_inventory_validator_contract_29cn.json:31:  "paper_armed_approved": false,
etc/replay/parity/offline_replay_output_parity_audit_29ak.json:13:    "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_runtime_gap_audit_29h_r1.json:60:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_runtime_gap_audit_29h_r1.json:75:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_runtime_gap_audit_29h_r1.json:90:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_runtime_gap_audit_29h_r1.json:103:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_runtime_gap_audit_29h_r1.json:116:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_runtime_gap_audit_29h_r1.json:129:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_runtime_gap_audit_29h_r1.json:142:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_runtime_gap_audit_29h_r1.json:157:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_runtime_gap_audit_29h_r1.json:171:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_runtime_gap_audit_29h_r1.json:182:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_runtime_gap_audit_29h_r1.json:195:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_runtime_gap_audit_29h_r1.json:203:  "paper_armed_approved": false,
etc/replay/parity/explicit_offline_replay_callable_execution_28v.json:28:    "paper_armed_approved": false,
etc/replay/parity/explicit_offline_replay_callable_execution_28v.json:58:    "paper_armed_approved": false,
etc/replay/parity/explicit_offline_replay_callable_execution_28v.json:108:      "paper_armed_approved": false,
etc/replay/parity/explicit_offline_replay_callable_execution_28v.json:124:      "paper_armed_approved": false,
etc/replay/parity/explicit_offline_replay_callable_execution_28v.json:140:      "paper_armed_approved": false,
etc/replay/parity/explicit_offline_replay_callable_execution_28v.json:156:      "paper_armed_approved": false,
etc/replay/parity/explicit_offline_replay_callable_execution_28v.json:172:      "paper_armed_approved": false,
etc/replay/parity/explicit_offline_replay_callable_execution_28v.json:188:      "paper_armed_approved": false,
etc/replay/parity/explicit_offline_replay_callable_execution_28v.json:202:      "paper_armed_approved": false,
etc/replay/parity/explicit_offline_replay_callable_execution_28v.json:215:      "paper_armed_approved": false,
etc/replay/parity/explicit_offline_replay_callable_execution_28v.json:230:      "paper_armed_approved": false,
etc/replay/parity/explicit_offline_replay_callable_execution_28v.json:291:  "paper_armed_approved": false,
etc/replay/parity/offline_stage_owns_runtime_decisioning_alias_repair_29ac.json:143:  "paper_armed_approved": false,
etc/replay/parity/force_provider_feature_output_root_29aw_r9.json:223:  "guarded_retry_stdout_tail": "{\n  \"accepted_for\": \"GUARDED_REPLAY_ENGINE_EXECUTE_DRY_RUN_ONLY\",\n  \"calls_broker_api\": false,\n  \"candidate_executed\": true,\n  \"comparison_completed\": false,\n  \"context_reconstruction_ready\": true,\n  \"engine_instance_ready\": true,\n  \"execution_arming_created\": false,\n  \"execution_attempted\": true,\n  \"execution_ok\": true,\n  \"full_live_replay_parity\": \"NOT_PROVEN_IN_29G\",\n  \"known_boolean_count\": 0,\n  \"live_trading_approved\": false,\n  \"next_batch\": \"Batch 29H \\u2014 inspect ReplayEngine dry-run outputs and build replay/live parity comparison contract, still not paper/live enablement.\",\n  \"null_value_count\": 4,\n  \"paper_armed_approved\": false,\n  \"production_doctrine_changed\": false,\n  \"provider_feature_field_count\": 4,\n  \"provider_feature_summary_found\": true,\n  \"provider_feature_summary_path\": \"/home/Lenovo/scalpx/projects/mme_scalpx/run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/guarded_replay_engine_execute_retry_29aw_r9_20260502_133235/06_guarded_replay_provider_feature_summary.json\",\n  \"provider_feature_value_comparison_ready\": false,\n  \"reads_live_redis\": false,\n  \"real_order_sent\": false,\n  \"replay_core_executed\": true,\n  \"replay_run_completed\": true,\n  \"schema_version\": \"guarded_replay_engine_execute_result_29g_v1\",\n  \"starts_services\": false,\n  \"writes_live_redis\": false\n}\n",
etc/replay/parity/force_provider_feature_output_root_29aw_r9.json:233:  "paper_armed_approved": false,
etc/replay/parity/real_session_evidence_collection_manifest_validator_29di.json:25:  "paper_armed_approved": false,
etc/replay/parity/topology_stages_runtime_gap_audit_29j.json:72:      "paper_armed_approved": false,
etc/replay/parity/topology_stages_runtime_gap_audit_29j.json:85:      "paper_armed_approved": false,
etc/replay/parity/topology_stages_runtime_gap_audit_29j.json:98:      "paper_armed_approved": false,
etc/replay/parity/topology_stages_runtime_gap_audit_29j.json:111:      "paper_armed_approved": false,
etc/replay/parity/topology_stages_runtime_gap_audit_29j.json:124:      "paper_armed_approved": false,
etc/replay/parity/topology_stages_runtime_gap_audit_29j.json:139:      "paper_armed_approved": false,
etc/replay/parity/topology_stages_runtime_gap_audit_29j.json:153:      "paper_armed_approved": false,
etc/replay/parity/topology_stages_runtime_gap_audit_29j.json:166:      "paper_armed_approved": false,
etc/replay/parity/topology_stages_runtime_gap_audit_29j.json:179:      "paper_armed_approved": false,
etc/replay/parity/topology_stages_runtime_gap_audit_29j.json:187:  "paper_armed_approved": false,
etc/replay/parity/same_session_artifact_index_matrix_contract_29ci.json:32:  "paper_armed_approved": false,
etc/replay/parity/offline_topology_scope_values_preservation_repair_29w_r2.json:144:  "paper_armed_approved": false,
etc/replay/parity/real_same_session_collection_planning_contract_30a.json:27:  "paper_armed_approved": false,
etc/replay/parity/family_surface_payload_parity_audit_29bq_r1.json:42:  "paper_armed_approved": false,
etc/replay/parity/feature_payload_parity_audit_29bj.json:31:  "paper_armed_approved": false,
etc/replay/parity/selected_bundle_safety_boundary_proof_29ap.json:15:    "paper_armed_approved": false,
etc/replay/parity/execution_shadow_semantic_no_order_contract_29cy.json:39:  "paper_armed_approved": false,
etc/replay/parity/bounded_guarded_replay_retry_after_29af_29ag.json:47:    "paper_armed_approved": false,
etc/replay/parity/proof_29aa_pass_integrity_audit_29ab_r2.json:2132:  "paper_armed_approved": false,
etc/replay/parity/topology_fingerprint_runtime_gap_audit_29ad.json:191:  "paper_armed_approved": false,
etc/replay/parity/replay_provider_feature_real_source_discovery_29at.json:215:  "paper_armed_approved": false,
etc/replay/parity/risk_execution_no_order_value_comparison_29bx.json:23:  "paper_armed_approved": false,
etc/replay/parity/guarded_replay_core_candidate_signature_bridge_28y.json:61:    "paper_armed_approved": false,
etc/replay/parity/guarded_replay_core_candidate_signature_bridge_28y.json:148:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_core_candidate_signature_bridge_28y.json:164:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_core_candidate_signature_bridge_28y.json:180:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_core_candidate_signature_bridge_28y.json:194:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_core_candidate_signature_bridge_28y.json:209:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_core_candidate_signature_bridge_28y.json:225:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_core_candidate_signature_bridge_28y.json:241:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_core_candidate_signature_bridge_28y.json:250:  "paper_armed_approved": false,
etc/replay/parity/guarded_replay_core_candidate_signature_bridge_28y.json:286:    "stdout": "{\n  \"accepted_for\": \"REPLAY_CORE_CANDIDATE_IMPORT_SIGNATURE_BRIDGE_ONLY\",\n  \"calls_broker_api\": false,\n  \"candidate_executed\": false,\n  \"comparison_completed\": false,\n  \"core_execution_ready\": true,\n  \"execution_arming_created\": false,\n  \"full_live_replay_parity\": \"NOT_PROVEN_IN_28Y\",\n  \"import_execution_ready\": true,\n  \"live_trading_approved\": false,\n  \"next_batch\": \"Batch 28Z \\u2014 execute ReplayEngineHook through guarded import-ready core adapter, still not paper/live enablement.\",\n  \"paper_armed_approved\": false,\n  \"production_doctrine_changed\": false,\n  \"readiness_kind\": \"IMPORT_READY_CORE_CANDIDATE\",\n  \"reads_live_redis\": false,\n  \"real_order_sent\": false,\n  \"replay_core_executed\": false,\n  \"replay_run_completed\": false,\n  \"schema_version\": \"candidate_signature_bridge_result_28y_v1\",\n  \"source_signature_bridge_ready\": true,\n  \"starts_services\": false,\n  \"writes_live_redis\": false\n}\n",
etc/replay/parity/topology_fingerprint_symbol_locator_29ai_r3.json:12:    "paper_armed_approved": false,
etc/replay/parity/dict_callable_runtime_gap_audit_29t.json:210:  "paper_armed_approved": false,
etc/replay/parity/consolidate_no_order_select_next_29bz.json:23:  "paper_armed_approved": false,
etc/replay/parity/guarded_offline_replay_dry_run_contract_28o.json:59:    "paper_armed_approved": false,
etc/replay/parity/guarded_offline_replay_dry_run_contract_28o.json:176:  "paper_armed_approved": false,
etc/replay/parity/inspect_29ad_retry_artifacts_29ae.json:12:    "paper_armed_approved": false,
etc/replay/parity/offline_stage_terminal_stage_alias_repair_29s.json:144:  "paper_armed_approved": false,
etc/replay/parity/provider_feature_parity_consolidation_29ay.json:243:  "paper_armed_approved": false,
etc/replay/parity/family_surface_value_comparison_29bs.json:24:  "paper_armed_approved": false,
etc/replay/parity/semantic_report_mapped_comparison_29cc.json:27:  "paper_armed_approved": false,
etc/replay/parity/live_observe_field_coverage_resolver_29an.json:17:    "paper_armed_approved": false,
etc/replay/parity/observe_only_offline_replay_materialization_harness_28k.json:67:    "paper_armed_approved": false,
etc/replay/parity/observe_only_offline_replay_materialization_harness_28k.json:85:  "paper_armed_approved": false,
etc/replay/parity/topology_fingerprint_alias_repair_29ai.json:13:    "paper_armed_approved": false,
etc/replay/parity/scope_value_probe_failure_audit_29y_r1.json:154:  "paper_armed_approved": false,
etc/replay/parity/observe_only_market_session_capture_runbook_v1.json:24:    "Stop if paper_armed or live trading is enabled."
etc/replay/parity/observe_only_market_session_capture_runbook_v1.json:29:    "paper_armed_readiness": "NOT_APPROVED_IN_28D",
etc/replay/parity/observe_only_market_session_capture_runbook_v1.json:90:    "confirm_paper_armed_false",
etc/replay/parity/observe_only_market_session_capture_runbook_v1.json:102:    "paper_armed_approved": false,
etc/replay/parity/offline_replay_output_parity_contract_29ak.json:18:    "paper_armed_readiness",
etc/replay/parity/feature_payload_mapping_contract_29bk.json:31:  "paper_armed_approved": false,
etc/replay/parity/explicit_offline_replay_callable_surface_28u.json:49:      "paper_armed_approved": false,
etc/replay/parity/explicit_offline_replay_callable_surface_28u.json:65:      "paper_armed_approved": false,
etc/replay/parity/explicit_offline_replay_callable_surface_28u.json:81:      "paper_armed_approved": false,
etc/replay/parity/explicit_offline_replay_callable_surface_28u.json:97:      "paper_armed_approved": false,
etc/replay/parity/explicit_offline_replay_callable_surface_28u.json:113:      "paper_armed_approved": false,
etc/replay/parity/explicit_offline_replay_callable_surface_28u.json:129:      "paper_armed_approved": false,
etc/replay/parity/explicit_offline_replay_callable_surface_28u.json:145:      "paper_armed_approved": false,
etc/replay/parity/explicit_offline_replay_callable_surface_28u.json:163:  "paper_armed_approved": false,
etc/replay/parity/actual_replay_engine_integration_preflight_28q.json:181:  "paper_armed_approved": false,
etc/replay/parity/actual_replay_engine_integration_preflight_28q.json:247:    "stdout": "{\n  \"accepted_for\": \"ACTUAL_REPLAY_ENGINE_INTEGRATION_PREFLIGHT_ONLY\",\n  \"adapter_execution_root\": \"/home/Lenovo/scalpx/projects/mme_scalpx/run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/guarded_replay_cli_adapter_execution_28p_r3\",\n  \"calls_broker_api\": false,\n  \"comparison_completed\": false,\n  \"dataset_candidate_root\": \"/home/Lenovo/scalpx/projects/mme_scalpx/run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dataset_candidate\",\n  \"execution_arming_created\": false,\n  \"full_live_replay_parity\": \"NOT_PROVEN_IN_28Q\",\n  \"generated_at_utc\": \"2026-05-01T12:43:07.077671+00:00\",\n  \"integration_preflight_script_ok\": true,\n  \"live_trading_approved\": false,\n  \"output_root\": \"/home/Lenovo/scalpx/projects/mme_scalpx/run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/actual_replay_engine_integration_preflight_28q\",\n  \"paper_armed_approved\": false,\n  \"preflight_only\": true,\n  \"production_doctrine_changed\": false,\n  \"reads_live_redis\": false,\n  \"real_order_sent\": false,\n  \"replay_engine_executed\": false,\n  \"replay_run_completed\": false,\n  \"schema_version\": \"actual_replay_engine_integration_preflight_script_result_28q_v1\",\n  \"starts_services\": false,\n  \"writes_live_redis\": false\n}\n",
etc/replay/parity/actual_replay_engine_integration_preflight_28q.json:264:    "paper_armed_approved": false,
etc/replay/parity/repair_no_order_reference_discovery_29bv_r1.json:9:    "paper_armed_approved",
etc/replay/parity/repair_no_order_reference_discovery_29bv_r1.json:34:  "paper_armed_approved": false,
etc/replay/parity/runtime_feature_field_inventory_contract_29cm.json:35:  "paper_armed_approved": false,
etc/replay/parity/next_replay_live_parity_surface_selection_29ba.json:153:  "paper_armed_approved": false,
etc/replay/parity/strategy_activation_mismatch_classification_29bf.json:30:  "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_execute_dry_run_29g.json:88:    "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_execute_dry_run_29g.json:126:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_execute_dry_run_29g.json:139:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_execute_dry_run_29g.json:152:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_execute_dry_run_29g.json:167:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_execute_dry_run_29g.json:183:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_execute_dry_run_29g.json:199:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_execute_dry_run_29g.json:213:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_execute_dry_run_29g.json:226:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_execute_dry_run_29g.json:239:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_execute_dry_run_29g.json:252:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_execute_dry_run_29g.json:265:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_execute_dry_run_29g.json:278:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_execute_dry_run_29g.json:286:  "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_execute_dry_run_29g.json:321:    "stdout": "{\n  \"accepted_for\": \"GUARDED_REPLAY_ENGINE_EXECUTE_DRY_RUN_ONLY\",\n  \"calls_broker_api\": false,\n  \"candidate_executed\": false,\n  \"comparison_completed\": false,\n  \"context_reconstruction_ready\": true,\n  \"engine_instance_ready\": true,\n  \"execution_arming_created\": false,\n  \"execution_attempted\": true,\n  \"execution_ok\": false,\n  \"full_live_replay_parity\": \"NOT_PROVEN_IN_29G\",\n  \"live_trading_approved\": false,\n  \"next_batch\": \"Batch 29H \\u2014 repair guarded ReplayEngine dry-run runtime gap before output comparison, still not paper/live enablement.\",\n  \"paper_armed_approved\": false,\n  \"production_doctrine_changed\": false,\n  \"reads_live_redis\": false,\n  \"real_order_sent\": false,\n  \"replay_core_executed\": false,\n  \"replay_run_completed\": false,\n  \"schema_version\": \"guarded_replay_engine_execute_result_29g_v1\",\n  \"starts_services\": false,\n  \"writes_live_redis\": false\n}\n",
etc/replay/parity/family_surface_value_classification_29bt.json:26:  "paper_armed_approved": false,
etc/replay/parity/observe_only_offline_replay_dataset_candidate_28m.json:149:    "paper_armed_approved": false,
etc/replay/parity/observe_only_offline_replay_dataset_candidate_28m.json:163:  "paper_armed_approved": false,
etc/replay/parity/family_surface_comparison_contract_latest.json:190:    "does_not_enable_paper_armed": true,
etc/replay/parity/offline_live_observe_parity_comparison_contract_29al.json:127:    "paper_armed_enabled",
etc/replay/parity/offline_live_observe_parity_comparison_contract_29al.json:152:    "paper_armed_approved",
etc/replay/parity/offline_live_observe_parity_comparison_contract_29al.json:175:      "paper_armed_readiness",
etc/replay/parity/offline_live_observe_parity_comparison_contract_29al.json:180:    "paper_armed_approved": false,
etc/replay/parity/emit_before_success_stdout_29aw_r7.json:202:  "guarded_retry_stdout_tail": "{\n  \"accepted_for\": \"GUARDED_REPLAY_ENGINE_EXECUTE_DRY_RUN_ONLY\",\n  \"calls_broker_api\": false,\n  \"candidate_executed\": true,\n  \"comparison_completed\": false,\n  \"context_reconstruction_ready\": true,\n  \"engine_instance_ready\": true,\n  \"execution_arming_created\": false,\n  \"execution_attempted\": true,\n  \"execution_ok\": true,\n  \"full_live_replay_parity\": \"NOT_PROVEN_IN_29G\",\n  \"live_trading_approved\": false,\n  \"next_batch\": \"Batch 29H \\u2014 inspect ReplayEngine dry-run outputs and build replay/live parity comparison contract, still not paper/live enablement.\",\n  \"paper_armed_approved\": false,\n  \"production_doctrine_changed\": false,\n  \"reads_live_redis\": false,\n  \"real_order_sent\": false,\n  \"replay_core_executed\": true,\n  \"replay_run_completed\": true,\n  \"schema_version\": \"guarded_replay_engine_execute_result_29g_v1\",\n  \"starts_services\": false,\n  \"writes_live_redis\": false\n}\n",
etc/replay/parity/emit_before_success_stdout_29aw_r7.json:212:  "paper_armed_approved": false,
etc/replay/parity/replay_provider_feature_producer_consumer_seam_audit_29av.json:272:  "paper_armed_approved": false,
etc/replay/parity/replay_live_observe_only_parity_artifact_29ai.json:194:  "paper_armed_approved": false,
etc/replay/parity/offline_stage_description_alias_repair_29aa.json:13:    "paper_armed_approved": false,
etc/replay/parity/offline_live_observe_parity_contract_29al.json:14:    "paper_armed_approved": false,
etc/replay/parity/corrected_strategy_activation_comparison_29bh.json:43:  "paper_armed_approved": false,
etc/replay/parity/protocol_safe_replay_core_candidate_selection_29b.json:77:      "paper_armed_approved": false,
etc/replay/parity/protocol_safe_replay_core_candidate_selection_29b.json:92:      "paper_armed_approved": false,
etc/replay/parity/protocol_safe_replay_core_candidate_selection_29b.json:108:      "paper_armed_approved": false,
etc/replay/parity/protocol_safe_replay_core_candidate_selection_29b.json:124:      "paper_armed_approved": false,
etc/replay/parity/protocol_safe_replay_core_candidate_selection_29b.json:140:      "paper_armed_approved": false,
etc/replay/parity/protocol_safe_replay_core_candidate_selection_29b.json:156:      "paper_armed_approved": false,
etc/replay/parity/protocol_safe_replay_core_candidate_selection_29b.json:172:      "paper_armed_approved": false,
etc/replay/parity/protocol_safe_replay_core_candidate_selection_29b.json:188:      "paper_armed_approved": false,
etc/replay/parity/protocol_safe_replay_core_candidate_selection_29b.json:202:      "paper_armed_approved": false,
etc/replay/parity/protocol_safe_replay_core_candidate_selection_29b.json:210:  "paper_armed_approved": false,
etc/replay/parity/protocol_safe_replay_core_candidate_selection_29b.json:236:    "stdout": "{\n  \"accepted_for\": \"PROTOCOL_SAFE_CONCRETE_REPLAY_CORE_CANDIDATE_SELECTION_ONLY\",\n  \"calls_broker_api\": false,\n  \"candidate_count\": 220,\n  \"candidate_executed\": false,\n  \"comparison_completed\": false,\n  \"concrete_candidate_selected\": true,\n  \"excluded_abstract_count\": 0,\n  \"excluded_protocol_count\": 5,\n  \"execution_arming_created\": false,\n  \"full_live_replay_parity\": \"NOT_PROVEN_IN_29B\",\n  \"live_trading_approved\": false,\n  \"next_batch\": \"Batch 29C \\u2014 build guarded adapter for selected concrete replay-core candidate, still not paper/live enablement.\",\n  \"paper_armed_approved\": false,\n  \"production_doctrine_changed\": false,\n  \"reads_live_redis\": false,\n  \"real_order_sent\": false,\n  \"replay_core_executed\": false,\n  \"replay_run_completed\": false,\n  \"schema_version\": \"protocol_safe_candidate_selection_result_29b_v1\",\n  \"selected_candidate\": {\n    \"bases\": [],\n    \"call_args\": [],\n    \"excluded_reason\": \"low_score_or_no_executable_method\",\n    \"has_call\": false,\n    \"has_run_or_execute\": true,\n    \"is_abstract\": false,\n    \"is_protocol\": false,\n    \"kind\": \"class\",\n    \"lineno\": 147,\n    \"methods\": [\n      \"__init__\",\n      \"build_context\",\n      \"execute\",\n      \"_execute_stage\",\n      \"_run_hooks\",\n      \"_transition\"\n    ],\n    \"module_file\": \"app/mme_scalpx/replay/engine.py\",\n    \"name\": \"ReplayEngine\",\n    \"run_args\": [\n      \"self\",\n      \"run_context\",\n      \"topology_plan\",\n      \"stage_executor\"\n    ],\n    \"score\": 25\n  },\n  \"starts_services\": false,\n  \"writes_live_redis\": false\n}\n",
etc/replay/parity/protocol_safe_replay_core_candidate_selection_29b.json:283:    "paper_armed_approved": false,
etc/replay/parity/fresh_live_observe_readiness_blocker_inspection_29ar.json:15:    "paper_armed_approved": false,
etc/replay/parity/offline_stage_terminal_stage_alias_repair_29s_r1.json:145:  "paper_armed_approved": false,
etc/replay/parity/post_r5_emission_reachability_artifact_audit_29aw_r6.json:170:  "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_adapter_29c.json:19:    "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_adapter_29c.json:126:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_adapter_29c.json:142:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_adapter_29c.json:158:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_adapter_29c.json:174:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_adapter_29c.json:190:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_adapter_29c.json:206:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_adapter_29c.json:220:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_adapter_29c.json:233:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_adapter_29c.json:246:      "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_adapter_29c.json:254:  "paper_armed_approved": false,
etc/replay/parity/guarded_replay_engine_adapter_29c.json:291:    "stdout": "{\n  \"accepted_for\": \"GUARDED_REPLAY_ENGINE_ADAPTER_BUILD_ONLY\",\n  \"adapter_ready\": true,\n  \"calls_broker_api\": false,\n  \"candidate_executed\": false,\n  \"comparison_completed\": false,\n  \"core_execution_binding_ready\": false,\n  \"execute_missing_required_args\": [\n    \"run_context\",\n    \"topology_plan\"\n  ],\n  \"execution_arming_created\": false,\n  \"full_live_replay_parity\": \"NOT_PROVEN_IN_29C\",\n  \"live_trading_approved\": false,\n  \"next_batch\": \"Batch 29D \\u2014 build ReplayEngine run_context/topology_plan/stage_executor bridge, still not paper/live enablement.\",\n  \"paper_armed_approved\": false,\n  \"production_doctrine_changed\": false,\n  \"reads_live_redis\": false,\n  \"real_order_sent\": false,\n  \"replay_core_executed\": false,\n  \"replay_run_completed\": false,\n  \"schema_version\": \"guarded_replay_engine_adapter_result_29c_v1\",\n  \"selected_candidate\": {\n    \"kind\": \"class\",\n    \"module_file\": \"app/mme_scalpx/replay/engine.py\",\n    \"name\": \"ReplayEngine\"\n  },\n  \"starts_services\": false,\n  \"writes_live_redis\": false\n}\n",
etc/replay/parity/strict_semantic_soft_mismatch_review_29am.json:203:  "paper_armed_approved": false,
etc/replay/parity/offline_topology_scope_alias_repair_29w.json:141:  "paper_armed_approved": false,
etc/replay/parity/offline_stage_terminal_stage_runtime_gap_audit_29r.json:66:      "paper_armed_approved": false,
etc/replay/parity/offline_stage_terminal_stage_runtime_gap_audit_29r.json:79:      "paper_armed_approved": false,
etc/replay/parity/offline_stage_terminal_stage_runtime_gap_audit_29r.json:92:      "paper_armed_approved": false,
etc/replay/parity/offline_stage_terminal_stage_runtime_gap_audit_29r.json:105:      "paper_armed_approved": false,
etc/replay/parity/offline_stage_terminal_stage_runtime_gap_audit_29r.json:118:      "paper_armed_approved": false,
etc/replay/parity/offline_stage_terminal_stage_runtime_gap_audit_29r.json:131:      "paper_armed_approved": false,
etc/replay/parity/offline_stage_terminal_stage_runtime_gap_audit_29r.json:144:      "paper_armed_approved": false,

## exact current shell env
B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY=1
SCALPX_OBSERVE_ONLY=1

## pstatus current
{
  "broker_order_attempted": false,
  "classification": "PSTATUS_FAIL_CLOSED_RUNTIME_VERDICT_READY",
  "controlled_paper_route_imported": {
    "function": "build_fail_closed_controlled_paper_verdict",
    "import_ok": true,
    "result": {
      "allowed": false,
      "broker_live_blocked": true,
      "controlled_runtime_allowed": false,
      "observe_only": false,
      "paper_armed": false,
      "paper_enabled": false,
      "reason": "CONTROLLED_PAPER_RUNTIME_NOT_ALLOWED",
      "scope_ack_ok": false
    }
  },
  "created_at": "2026-06-14T05:31:45.238011+00:00",
  "env": {
    "B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY": "1",
    "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME": "",
    "SCALPX_CONTROLLED_PAPER_ARMED": "",
    "SCALPX_CONTROLLED_PAPER_SCOPE_ACK": "",
    "SCALPX_ENABLE_LIVE": "",
    "SCALPX_ENABLE_PAPER": "",
    "SCALPX_OBSERVE_ONLY": "1",
    "SCALPX_PAPER_ARMED": ""
  },
  "paper_live_enabled": false,
  "paper_runtime_verdict": {
    "controlled_runtime_allowed": false,
    "fail_closed": true,
    "live_enabled": false,
    "observe_only": true,
    "paper_armed": false,
    "paper_enabled": false,
    "paper_route_allowed": false,
    "position_flat_verified": false,
    "reason": "OBSERVE_ONLY_ACTIVE",
    "scope_ack_present": false
  },
  "project_root": "/home/Lenovo/scalpx/projects/mme_scalpx",
  "redis_delete_attempted": false,
  "redis_write_attempted": false,
  "safety": {
    "no_execution_stream": true,
    "no_order_stream": true,
    "no_risk_stream": true,
    "orders_risk_execution": "0/0/0",
    "processes": {
      "execution": 0,
      "replay": 0,
      "risk": 0
    },
    "risk_execution_not_running": true,
    "streams": {
      "execution": 0,
      "orders": 0,
      "risk": 0
    }
  },
  "schema_version": "pstatus_fail_closed_runtime_verdict_v1"
}
