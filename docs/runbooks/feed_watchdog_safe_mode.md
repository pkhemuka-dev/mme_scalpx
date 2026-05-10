# Feed Watchdog Safe Mode

## Purpose
Automatically detect and repair feed-only runtime hygiene issues:
- duplicate feeds
- stale feed pidfile
- pidfile vs lock:feeds owner mismatch
- feed process alive but lock lost
- stale lock:execution when no execution process is running

## Safety Boundaries
The watchdog never:
- starts risk
- starts execution
- enables paper/live
- sends orders
- restarts Redis
- patches code
- handles strategy validity

## Commands
- phealth: read-only health classification
- prepair: bounded feed-only repair
- pwatchonce: run one health/repair pass
- pwatchloop [seconds]: foreground loop
- pwatchinstall: install systemd timer/unit
- pwatchstart: start timer
- pwatchstop: stop timer
- pwatchstatus: view timer/service/journal

## Recommended manual-live setup
1. plogin
2. pmanualmode if available
3. pfeeds --force-all
4. pfeedcheck
5. pwatchinstall
6. pwatchstart

## Important
Keep this watchdog feed-only until separately proven safe.
Do not let it start full pstack/risk/execution.
