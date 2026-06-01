# B1-PROFIT-LIVE-R38N_read_only_classic_activation_bridge_patch_plan_no_patch_no_order_no_paper_20260529_101627 patch plan

## Current state
- Observe-only recording remains running.
- `pcheck` classic degraded preflight is OK.
- MISO remains blocked without Dhan context.
- No eligible market candidate has appeared yet.
- Activation bridge still reports classic runtime disabled / hold-only.

## Patch-plan doctrine, not applied in this batch
A future patch, only after review, should do exactly this:

1. Preserve observe-only default.
2. Preserve no-order default.
3. Preserve MISO blocked unless Dhan context is healthy.
4. Permit classic-family activation bridge evaluation only when all of these are true:
   - explicit controlled-paper approval env is present,
   - selected scope family/side is explicitly named,
   - max lot is 1,
   - Zerodha execution only,
   - Dhan execution disabled,
   - safety streams and PIDs are zero before arming,
   - no active position,
   - current candidate is entry-eligible.
5. Do not enable real live.
6. Do not enable broker orders unless execution/risk controlled-paper batch explicitly starts them later.
7. Do not relax strategy thresholds.
8. Do not convert no-signal into candidate.
9. Do not allow MISO in Dhan-degraded mode.

## Recommended next after this audit
If R38N passes, create a separate R38O patch plan or R38O dry-run fixture. Do not patch during live unless the plan is tiny and explicitly approved.
