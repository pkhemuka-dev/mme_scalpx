# B1-PROFIT-LIVE-R38E_PREOPEN_LIVE_OBSERVE_READINESS_RUNBOOK_NO_PATCH_NO_START_NO_ORDER

Classification: **PASS_R38E_PREOPEN_LIVE_OBSERVE_READINESS_RUNBOOK_FROZEN_NO_ORDER**

## Current safety

- orders=0
- risk_stream=0
- execution_stream=0
- risk_pids=0
- execution_pids=0

## Proof chain

- R37Q data admission: `run/proofs/B1-PROFIT-LIVE-R37Q-R1_DATA_ADMISSION_AND_PDEV_TARGETING_NO_PATCH_NO_START_NO_ORDER_correct_pseal_admission_inventory_pdev_and_target_provider_fallback_surface_20260528_220400.json`
- R38B provider fallback patch: `run/proofs/B1-PROFIT-LIVE-R38B_PROVIDER_RUNTIME_CLASSIC_ZERODHA_SELECTED_OPTION_FALLBACK_PATCH_NO_ORDER_patch_manual_failover_selected_option_to_zerodha_when_dhan_unavailable_no_start_no_order_20260528_221023.json`
- R38C static/import validation: `run/proofs/B1-PROFIT-LIVE-R38C_STATIC_IMPORT_VALIDATION_AFTER_PROVIDER_FALLBACK_PATCH_NO_START_NO_ORDER_validate_r38b_patch_import_marker_ast_no_danger_no_service_start_20260528_221123.json`
- R38D fixture behavior validation: `run/proofs/B1-PROFIT-LIVE-R38D_FIXTURE_BEHAVIOR_VALIDATION_AFTER_PROVIDER_FALLBACK_PATCH_NO_START_NO_ORDER_prove_selected_option_dhan_unavailable_zerodha_fallback_without_runtime_start_20260528_221343.json`
- R37P/PSeal dir: `run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260527_153107`
- R37M durable recorder dir: `run/live_capture/B1-PROFIT-LIVE-R37M_LIVE_SESSION_EMERGENCY_DURABLE_RECORDER_NO_ORDER_start_readonly_redis_stream_recorder_without_restart_no_risk_no_execution_no_order_20260527_092428`
- R38B backup: `run/_code_backups/B1-PROFIT-LIVE-R38B_PROVIDER_RUNTIME_CLASSIC_ZERODHA_SELECTED_OPTION_FALLBACK_PATCH_NO_ORDER_patch_manual_failover_selected_option_to_zerodha_when_dhan_unavailable_no_start_no_order_20260528_221023_provider_runtime.py.before`
- R38B marker_count=1

## Tomorrow logical sequence

### Phase 1 — pre-open safety check only

Run:

```bash
cd /home/Lenovo/scalpx/projects/mme_scalpx
source ~/.bash_aliases 2>/dev/null || true
pcheck
```

Must show:

- orders=0
- risk_stream=0
- execution_stream=0
- risk_proc=0
- execution_proc=0
- no existing paper/live process
- no active position

### Phase 2 — observe-only start

Only if Phase 1 is clean:

```bash
pauto_start
sleep 60
pcheck
```

Required observe-only result:

- feeds OK
- features OK
- strategy OK
- Zerodha futures fresh
- Zerodha selected option fresh
- orders=0
- risk_stream=0
- execution_stream=0
- risk_proc=0
- execution_proc=0

### Phase 3 — provider fallback proof

Expected after R38B patch:

- If Dhan selected-option/context is unavailable:
  - classic selected-option provider should become ZERODHA / failover-active or equivalent healthy assignment
  - MIST/MISB/MISC/MISR may become candidate-watch eligible
  - MISO remains blocked without Dhan context

Forbidden:

- no paper
- no risk start
- no execution start
- no broker order
- no Redis delete
- no lock delete

### Phase 4 — read-only family candidate preflight

Only after pcheck is healthy:

- inspect MIST/MISB/MISC/MISR candidate surfaces
- MISO must remain blocked if Dhan context is unavailable
- choose one family/side only for controlled-paper scope

### Phase 5 — controlled-paper approval gate

Paper may begin only after a fresh approval message.

Required approval phrase:

```text
I APPROVE B1-PROFIT-LIVE-R38 CONTROLLED-PAPER TRIAL: observe-only fallback proof passed, selected family/side is <FAMILY> <CALL/PUT>, max 1 lot, no real live, Zerodha execution only, Dhan execution disabled, stop immediately on any anomaly.
```

Without this exact approval, paper remains blocked.

## Rollback if needed

If provider fallback behaves wrongly:

1. Do not start paper.
2. Restore backup:
   `run/_code_backups/B1-PROFIT-LIVE-R38B_PROVIDER_RUNTIME_CLASSIC_ZERODHA_SELECTED_OPTION_FALLBACK_PATCH_NO_ORDER_patch_manual_failover_selected_option_to_zerodha_when_dhan_unavailable_no_start_no_order_20260528_221023_provider_runtime.py.before`
3. Re-run py_compile/import validation.
4. Keep observe-only only.

## Permanent doctrine after R38

- Zerodha remains primary futures + execution truth.
- Dhan remains option-context / MISO context lane.
- Classic families may use Zerodha selected-option in Dhan-degraded mode.
- MISO requires Dhan context and remains blocked without it.
- Execution provider unchanged.
- No automatic paper/live enablement.
