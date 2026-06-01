# B1-PROFIT-LIVE-R38W-R3_heredoc_free_finalize_controlled_paper_lifecycle_plan_no_patch_no_order_20260531_193410 controlled-paper lifecycle plan

## Step 1: pre-start safety
```bash
cd /home/Lenovo/scalpx/projects/mme_scalpx
source ~/.bash_aliases 2>/dev/null || true
pcheck
```

## Step 2: observe-only start
```bash
pauto_start
sleep 60
pauto_status
pcheck
```

## Step 3: read-only candidate preflight
Scope: MIST/MISB/MISC/MISR only. Identify CALL/PUT side and blockers. MISO stays blocked if Dhan context unavailable.

## Step 4: approval gate
Paper remains blocked unless this exact approval is given:

I APPROVE B1-PROFIT-LIVE-R38 CONTROLLED-PAPER TRIAL: observe-only fallback proof passed, selected family/side is <FAMILY> <CALL/PUT>, max 1 lot, no real live, Zerodha execution only, Dhan execution disabled, stop immediately on any anomaly.

## Step 5: after approval only
Separate micro-batch: risk/execution controlled-paper path only, max 1 lot, Zerodha only, Dhan execution disabled, no real live, stop on anomaly.
