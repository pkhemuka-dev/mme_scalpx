# Redis hot-runtime reset — 20260505_122132

## Problem
Redis was loading a very large RDB dataset at startup and rejecting/resetting client connections.
This caused pfeeds ping failure, lock refresh failure, XADD failures, and systemd restart loops.

## Fix
- Stopped MME systemd services/timers during manual mode.
- Backed up existing dump.rdb.
- Moved dump.rdb out of Redis startup path.
- Disabled Redis save lines for hot runtime.
- Kept appendonly disabled.
- Preserved maxmemory/allkeys-lru.

## Design law
Redis is hot runtime only.
Long-term raw/research data must be handled by research_capture/Parquet, not Redis persistence.

## Proof
- run/proofs/redis_hot_reset_before_20260505_122132.txt
- run/proofs/redis_rdb_files_before_20260505_122132.txt
