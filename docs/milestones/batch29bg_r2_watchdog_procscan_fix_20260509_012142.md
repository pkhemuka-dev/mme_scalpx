# Batch 29BG-R2 — watchdog process-scan false-positive repair — 20260509_012142

## Problem
phealth_safe.py used pgrep -f, which can match its own shell/pgrep command line and falsely report feeds/features/strategy/risk/execution processes.

## Fix
Replaced pgrep-based process detection with direct /proc/*/cmdline scanning in:
- bin/phealth_safe.py
- bin/prepair_safe.py

## Safety
- No trading service started
- No risk/execution start
- No paper/live enablement
- No Redis restart
- No orders

## Proofs
- run/proofs/batch29bg_r2_watchdog_procscan_fix_20260509_012142_compile.txt
- run/proofs/batch29bg_r2_watchdog_procscan_fix_20260509_012142_phealth_after_procscan_fix.json
