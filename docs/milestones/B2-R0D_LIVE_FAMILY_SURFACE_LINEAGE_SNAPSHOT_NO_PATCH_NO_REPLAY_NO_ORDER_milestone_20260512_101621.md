# B2-R0D — Live family surface lineage snapshot

Created: 2026-05-12T10:16:39+05:30

Purpose:
- Live-session read-only capture of feature-vs-decision family lineage.
- No patch, no replay, no PnL/backtest, no broker call, no order, no Redis write/delete, no service start/restart.

Proof:
- `run/proofs/B2-R0D_LIVE_FAMILY_SURFACE_LINEAGE_SNAPSHOT_NO_PATCH_NO_REPLAY_NO_ORDER_proof_20260512_101621.txt`

Audit:
- `run/audits/B2-R0D_LIVE_FAMILY_SURFACE_LINEAGE_SNAPSHOT_NO_PATCH_NO_REPLAY_NO_ORDER_summary_20260512_101621.txt`

Expected interpretation:
- If decision family tokens are present but feature family tokens are missing, then B2-R1 should inspect feature-to-decision lineage and publication surfaces after market.
- If `classic_runtime_disabled` persists, inspect runtime/config gating for MIST/MISB/MISC/MISR.
- If `stage_provider_ready_miso_failed` persists, inspect MISO provider-ready source despite option/Dhan context.
- Backtest remains blocked until strategy-approved + risk-approved trade lifecycle rows exist.

Next:
- `B2-R1_FEATURE_DECISION_FAMILY_SURFACE_LINEAGE_GAP_AUDIT_NO_PATCH`
