# Batch 29BG-R4 — Watchdog repair start-failure audit — 20260511_101416

## Problem
29BG-R3 attempted safe stale-feed repair, but final pfeedcheck showed:
- pfeeds process not alive
- lock:feeds absent
- critical streams not growing
- errors still growing

## Purpose
Diagnose whether pfeeds --force-all itself fails after repair, and patch prepair_safe.py so failed feed restart is explicitly classified as REPAIR_START_FAILED.

## Safety
- No risk/execution start
- No paper/live enablement
- No Redis restart
- No order sending
- Feed-only cleanup/restart only

## Proofs
- run/proofs/batch29bg_r4_watchdog_repair_start_failure_audit_20260511_101416_processes_before.txt
- run/proofs/batch29bg_r4_watchdog_repair_start_failure_audit_20260511_101416_redis_before.txt
- run/proofs/batch29bg_r4_watchdog_repair_start_failure_audit_20260511_101416_latest_watchdog_events.txt
- run/proofs/batch29bg_r4_watchdog_repair_start_failure_audit_20260511_101416_latest_pfeeds_log_tail.txt
- run/proofs/batch29bg_r4_watchdog_repair_start_failure_audit_20260511_101416_phealth_before_restart.json
- run/proofs/batch29bg_r4_watchdog_repair_start_failure_audit_20260511_101416_direct_pfeeds_start.txt
- run/proofs/batch29bg_r4_watchdog_repair_start_failure_audit_20260511_101416_pfeedcheck_after_direct_start.txt
- run/proofs/batch29bg_r4_watchdog_repair_start_failure_audit_20260511_101416_phealth_after_restart.json
- run/proofs/batch29bg_r4_watchdog_repair_start_failure_audit_20260511_101416_compile.txt
