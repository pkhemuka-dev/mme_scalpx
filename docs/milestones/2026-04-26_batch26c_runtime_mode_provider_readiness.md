# Batch 26C — Runtime Mode + Provider Readiness Canonicalization

Date: 2026-04-26  
Timestamp: 20260426_234305

## Verdict

Batch 26C V3 corrective package executed.

Expected proof:

- `run/proofs/batch26c_runtime_mode_provider_readiness.json`
- `batch26c_runtime_mode_provider_readiness_ok=true`

## Files patched

- `app/mme_scalpx/services/strategy_family/common.py`
- `app/mme_scalpx/services/strategy_family/mist.py`
- `app/mme_scalpx/services/strategy_family/misb.py`
- `app/mme_scalpx/services/strategy_family/misc.py`
- `app/mme_scalpx/services/strategy_family/misr.py`
- `app/mme_scalpx/services/strategy_family/miso.py`
- `app/mme_scalpx/services/features.py`
- `etc/brokers/provider_roles.yaml`
- `etc/strategy_family/family_runtime.yaml`

## Contract repaired

Runtime mode law:

- missing classic runtime mode => DISABLED
- unknown classic runtime mode => DISABLED
- DHAN_DEGRADED and DHAN-DEGRADED canonicalize to DHAN-DEGRADED
- missing MISO runtime mode => DISABLED
- unknown MISO runtime mode => DISABLED
- BASE-5DEPTH canonicalizes to BASE-5DEPTH, never None
- missing MISO mode may not default to BASE-5DEPTH

MISO provider-readiness law:

- `stage_flags.provider_ready_miso` is mandatory authority
- `stage_flags.dhan_context_fresh` is mandatory
- futures provider may be ZERODHA or DHAN if healthy/synced
- selected-option marketdata provider must be DHAN
- option-context provider must be DHAN
- Dhan futures is required only when explicit Dhan-futures rollout mode is enabled

## Safety posture

- observe_only default unchanged
- paper_armed not approved
- real live not approved
- execution arming unchanged
- no Redis names added
- no risk/execution behavior changed

## Remaining outside this batch

- Batch 26D: canonical field aliases / naming settlement
- Batch 26E: MIST/MISB/MISC structural surface repair
- Batch 26F: MISR trap-event lifecycle repair
- Batch 26G: MISO burst identity + microstructure repair
- Batch 25V market-session observe_only proof rerun
- Batch 25W paper_armed readiness gate rerun

Paper trading remains blocked until later gates pass.
