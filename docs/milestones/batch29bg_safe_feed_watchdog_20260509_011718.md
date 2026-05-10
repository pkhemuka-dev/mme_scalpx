# Batch 29BG — Safe Feed Watchdog / Self-Repair System — 20260509_011718

## Problem
Repeated runtime hygiene issues:
- duplicate feed processes
- stale feed process spamming feeds singleton lock refresh failed
- pidfile PID differing from lock:feeds owner PID
- stale lock:execution while execution process is absent

## Fix
Added:
- bin/phealth_safe.py
- bin/prepair_safe.py
- bin/pwatch_safe.py
- etc/systemd/scalpx-feed-watchdog.service
- etc/systemd/scalpx-feed-watchdog.timer
- shell helpers: phealth, prepair, pwatchonce, pwatchloop, pwatchinstall, pwatchstart, pwatchstop, pwatchstatus

## Safety
- feed-only repair
- no risk/execution start
- no paper/live enablement
- no Redis restart
- no order sending
- no doctrine mutation

## Proofs
- run/proofs/batch29bg_safe_feed_watchdog_20260509_011718_compile.txt
- run/proofs/batch29bg_safe_feed_watchdog_20260509_011718_phealth_initial.json
- run/proofs/batch29bg_safe_feed_watchdog_20260509_011718_pwatch_once.json
