#!/usr/bin/env bash
set -euo pipefail

cd /home/Lenovo/scalpx/projects/mme_scalpx

echo "=== R10I TOMORROW COMBINED R10H+R38 PREFLIGHT — NO START ==="
echo "NO START / NO ARM / NO ORDER / NO REDIS DELETE / NO LOCK DELETE"
date -Is

ACK_EXPECTED="I ACKNOWLEDGE CONTROLLED PAPER ONLY: NO REAL LIVE, NO BROKER ORDER, NO REAL MONEY, ONE APPROVED SCOPE ONLY, POSITION MUST START FLAT"

echo
echo "=== Runtime/process snapshot ==="
ps -eo pid,ppid,stat,etime,lstart,cmd | grep -E 'app\.mme_scalpx\.main|controlled_paper|risk|execution|feeds|features|strategy' | grep -v grep || true

echo
echo "=== Redis locks ==="
for k in lock:execution lock:feeds lock:monitor; do
  echo "$k value=$(redis-cli GET "$k" 2>/dev/null || true) ttl=$(redis-cli TTL "$k" 2>/dev/null || true)"
done

echo
echo "=== Stream lengths ==="
for s in orders:mme:stream risk:mme:stream execution:mme:stream trades:ledger:stream cmd:mme:stream decisions:mme:stream features:mme:stream ticks:mme:fut:zerodha:stream ticks:mme:fut:stream ticks:mme:opt:selected:zerodha:stream; do
  echo "$s $(redis-cli XLEN "$s" 2>/dev/null || echo ERR)"
done

echo
echo "=== Redis policy ==="
redis-cli CONFIG GET maxmemory-policy 2>/dev/null || true

echo
echo "=== Position hash ==="
redis-cli HGETALL state:position:mme 2>/dev/null || true

echo
echo "=== pstatus controlled-paper no-start verdict ==="
env -i \
  PATH="$PATH" \
  HOME="$HOME" \
  PYTHONPATH="$PWD" \
  SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME=1 \
  SCALPX_ENABLE_PAPER=1 \
  SCALPX_CONTROLLED_PAPER_ARMED=1 \
  SCALPX_PAPER_ARMED=1 \
  SCALPX_POSITION_FLAT_VERIFIED=1 \
  SCALPX_FLAT_POSITION_VERIFIED=1 \
  SCALPX_CONTROLLED_PAPER_SCOPE_ACK="$ACK_EXPECTED" \
  SCALPX_REAL_LIVE_ALLOWED=0 \
  SCALPX_ALLOW_REAL_LIVE=0 \
  SCALPX_ALLOW_BROKER_ORDERS=0 \
  SCALPX_ENABLE_LIVE=0 \
  ./bin/pstatus

echo
echo "=== Marker checks ==="
grep -RIn "R10D_NOGROUP_RECOVERY_FINAL_OVERRIDE_STATIC_ONLY_NO_ORDER\|R10D_REDIS_POLICY_AND_POSITION_HASH_FAIL_CLOSED" app/mme_scalpx/services/execution.py bin/pstatus || true
grep -RIn "R38EM_R1_PROJECTION_DIAG_AND_SYMBOL_FALLBACK_PATCH\|r38ee_projection_projected\|r38ee_projection_blocker" app/mme_scalpx/services/strategy.py bin 2>/dev/null || true

echo
echo "=== Existing R38 tomorrow scripts ==="
ls -l bin/r38en_tomorrow_parallel_scope_controlled_paper_runner.sh bin/r38eo_tomorrow_preflight_no_start.sh 2>/dev/null || true

echo
echo "PREFLIGHT_DONE_NO_START"
