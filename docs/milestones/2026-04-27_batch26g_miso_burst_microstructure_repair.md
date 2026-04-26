# Batch 26G — MISO Burst Identity + Microstructure Repair

Date: 2026-04-27
Timestamp: 20260427_002518

## Verdict

Batch 26G V6 proof-correction package executed.

Expected proof:

- `run/proofs/batch26g_miso_burst_microstructure_repair.json`
- `batch26g_miso_burst_microstructure_repair_ok=true`

## Corrective note

V1 compiled/imported but failed on `option_core.preserves_ltt_ns`. V2 repaired exact `ltt_ns` integer preservation and compiled/imported, but proof omitted required `tradability_surface`. V3 corrected the proof call, but read `result.reason`; MISO results carry reasons in `metadata["reason"]`. V4 corrected reason extraction but omitted healthy `provider_runtime`. V5 supplied provider runtime but omitted the required MISO branch frame. V6 supplies the proof branch frame only.

## Files patched / created in Batch 26G

Patched:

- `app/mme_scalpx/services/feature_family/option_core.py`
- `app/mme_scalpx/services/feature_family/miso_surface.py`
- `app/mme_scalpx/services/features.py`
- `app/mme_scalpx/services/strategy_family/miso.py`

Created:

- `app/mme_scalpx/services/feature_family/miso_microstructure.py`

## Contract repaired

- deterministic `burst_event_id`
- MISO strategy requires `burst_event_id`
- candidate metadata carries `burst_event_id`
- aggressive-flow ratio from live tick/trade rows
- speed-of-tape from favorable trades per second
- binned imbalance persistence
- queue-reload veto
- shadow support from actual shadow live data
- monitored-row shadow fallback removed
- exact `ltt_ns` preservation added

## Safety posture

- observe_only default unchanged
- paper_armed not approved
- real live not approved
- execution arming unchanged
- no Redis names added
- no Redis mutation added
- no broker/risk/execution behavior changed

## Remaining outside this batch

- Batch 26H: runtime structural cleanup / monkey-patch consolidation
- Batch 26I: proof layer upgrade + 25V helper alignment
- Batch 25V market-session observe_only proof rerun
- Batch 25W paper_armed readiness gate rerun

Paper trading remains blocked until later gates pass.
