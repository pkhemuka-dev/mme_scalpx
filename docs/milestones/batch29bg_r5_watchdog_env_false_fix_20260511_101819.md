# Batch 29BG-R5 — Watchdog env false parsing fix — 20260511_101819

## Problem
Watchdog classified SCALPX_ALLOW_REAL_LIVE="0" and SCALPX_REAL_LIVE_ALLOWED="0" as PAPER_OR_LIVE_ENABLED because non-empty strings were treated as truthy.

## Fix
Added env_enabled() parser:
- "0", "false", "no", "off", "", "none", "null" are false
- only explicit truthy values are true

## Safety
- No risk/execution start
- No paper/live enablement
- No Redis restart
- No order sending

## Proofs
- run/proofs/batch29bg_r5_watchdog_env_false_fix_20260511_101819_compile.txt
- run/proofs/batch29bg_r5_watchdog_env_false_fix_20260511_101819_phealth_before.json
- run/proofs/batch29bg_r5_watchdog_env_false_fix_20260511_101819_pwatch_once.json
- run/proofs/batch29bg_r5_watchdog_env_false_fix_20260511_101819_phealth_after.json
- run/proofs/batch29bg_r5_watchdog_env_false_fix_20260511_101819_pfeedcheck_after.txt
