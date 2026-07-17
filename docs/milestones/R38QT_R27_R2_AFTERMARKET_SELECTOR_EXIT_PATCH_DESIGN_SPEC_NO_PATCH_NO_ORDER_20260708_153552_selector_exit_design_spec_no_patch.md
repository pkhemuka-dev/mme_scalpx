# R38QT_R27_R2_AFTERMARKET_SELECTOR_EXIT_PATCH_DESIGN_SPEC_NO_PATCH_NO_ORDER_20260708_153552

## Purpose
After-market design spec only. No source patch, no restart, no Redis write, no broker/order.

## Evidence base
- R25 hard decision: NO_LIVE_RETRY_NO_PATCH_FROM_R20_R21_RULE
- R25 blockers: ['ZERODHA_KITE_IP_WHITELIST_BLOCKER_FOR_ORDER_PLACEMENT', 'ACTIVE_MIST_MISB_SELECTOR_EXIT_MODEL_NOT_ROBUST_FOR_REAL_MONEY', 'SIGNAL_CHANGE_EXIT_DOMINATES_AND_PRODUCES_NEGATIVE_FORWARD_RESULTS']
- R26 top active source files: [['./app/mme_scalpx/services/strategy.py', 156], ['./app/mme_scalpx/services/features.py', 80], ['./app/mme_scalpx/services/feature_family/contracts.py', 34], ['./app/mme_scalpx/services/strategy_family/activation.py', 24], ['./app/mme_scalpx/core/names.py', 18], ['./app/mme_scalpx/services/execution.py', 17], ['./app/mme_scalpx/services/strategy_family/misr.py', 16], ['./app/mme_scalpx/services/strategy_family/miso.py', 16], ['./app/mme_scalpx/services/feature_family/mist_surface.py', 13], ['./app/mme_scalpx/services/strategy_family/order_intent.py', 12]]

## R27_R1 failure
R27_R1 failed safely due to markdown/design rendering KeyError. No patch, no order.

## Decision
Do not promote the R20/R21 rule directly.
R22 and R24 showed practical exit/risk variants failed.
The design must fix selector stability and exit behavior before any patch or live retry.

## Design components
### selector_stability_gate
- Purpose: Prevent rapid family/action/symbol/token flips from becoming tradable state.
- Candidate rule: Candidate must keep same family + action + symbol + token for persistence window and minimum sample count.
- Initial safe values: {"cooldown_after_switch_sec": 20, "max_switches_per_min": 6, "min_persistence_sec": 10, "min_samples": 3}

### entry_filter
- Purpose: Only convert observed dry-run candidate into virtual tradable candidate after selector stability.
- Candidate rule: Allow ENTER_PUT only until independent CALL proof exists; require fresh tick price and valid selected option.
- Initial safe values: {"allowed_action_initial": "ENTER_PUT_ONLY", "candidate_age_ms_max": 20000, "fresh_tick_age_ms_max": 5000}

### exit_model
- Purpose: Avoid immediate signal-change exit dominance found in R22/R24.
- Candidate rule: Target/stop have priority; signal-change requires grace period and confirmation samples.
- Initial safe values: {"max_hold_sec": 90, "signal_change_confirm_samples": 2, "signal_change_grace_sec": 20, "stop_points": 12, "target_points": 24}

### risk_envelope
- Purpose: Cap one-trade damage and prevent repeat churn.
- Candidate rule: One virtual/open position max, cooldown after exit, daily attempt cap in controlled paper.
- Initial safe values: {"cooldown_after_exit_sec": 30, "max_controlled_paper_events_per_session": 1, "max_open_positions": 1}

### evidence_contract
- Purpose: Every selector/entry/exit state transition must be replayable and auditable.
- Required fields: ["selector_key", "selector_stable_for_sec", "selector_sample_count", "entry_reason", "exit_reason", "exit_priority", "tick_price_source", "mfe_points", "mae_points", "virtual_pnl_one_lot"]

## Patch restrictions
- Do not promote R20/R21 ENTER_PUT 5-sec rule directly.
- Do not enable broker/order/paper/live.
- Do not start risk/execution.
- Do not remove observe-only gates.
- Do not make signal_changed the only or immediate exit driver.

## Source review focus
### app/mme_scalpx/services/strategy.py
- Find where activation_selected_action/family/symbol/token are projected.
- Find where hold_only/report_only/dry_run fields are emitted.
- Find where candidate_observed_dry_run is converted into decision stream fields.
- Design selector stability and exit evidence fields here if strategy owns projection.
### app/mme_scalpx/services/features.py
- Find where family feature frame validity is produced.
- Find where hold_only_family_features_consumer_bridge is produced.
- Find where safe_to_consume/provider_ready/data_valid are computed.
- Avoid mixing feature validity ownership with trade lifecycle ownership.

## Next batch
R38QT_R28_AFTERMARKET_SOURCE_LEVEL_PATCH_PLAN_NO_PATCH

## Final verdict
PASS_R38QT_R27_R2_SELECTOR_EXIT_DESIGN_SPEC_CREATED_NO_PATCH_NO_ORDER
