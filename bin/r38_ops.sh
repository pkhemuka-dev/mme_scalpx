#!/usr/bin/env bash
cd /home/Lenovo/scalpx/projects/mme_scalpx
set -euo pipefail

mkout(){
  local batch="$1"
  local ts tag out
  ts="$(date +%Y%m%d_%H%M%S)"
  tag="${batch}_${ts}"
  out="run/proofs/${tag}"
  mkdir -p "$out" run/evidence_bundles
  echo "$tag|$out|$out/${tag}_report.txt"
}

proc(){
  ps -eo pid,ppid,pcpu,pmem,lstart,etime,cmd | grep -E "redis-server|python -m app\.mme_scalpx\.main|NEXT_MARKET_SESSION_R38RN|R38QW_SHORT_LIVE_PAPER|kite|dhan" | grep -v grep || true
}

streams(){
  for k in decisions:mme:stream features:mme:stream orders:mme:stream risk:mme:stream execution:mme:stream trades:mme:stream trades:ledger:stream; do
    printf "%-30s " "$k"
    redis-cli --raw XLEN "$k" || true
  done
}

assert_no_runtime(){
  local left
  left="$(ps -eo pid=,cmd= | grep -E "python -m app\.mme_scalpx\.main|NEXT_MARKET_SESSION_R38RN|R38QW_SHORT_LIVE_PAPER" | grep -v grep || true)"
  if [ -n "$left" ]; then echo "ERROR_RUNTIME_OR_LAUNCHER_ACTIVE"; echo "$left"; exit 21; fi
  echo "NO_RUNTIME_OR_LAUNCHER_ACTIVE=1"
}

assert_downstream_zero(){
  local v k
  for k in orders:mme:stream risk:mme:stream execution:mme:stream trades:mme:stream trades:ledger:stream; do
    v="$(redis-cli --raw XLEN "$k" 2>/dev/null || echo 0)"
    if [ "$v" != "0" ]; then echo "ERROR_${k}_NOT_ZERO=$v"; exit 22; fi
  done
  echo "DOWNSTREAM_STREAMS_ZERO=1"
}

markers(){
  grep -nE "R38SG_CONTROLLED_PAPER_ORDER_INTENT_ROUTE_BINDING_V1" app/mme_scalpx/services/execution.py
  grep -nE "R38SM_ATTACH_SOFT_ADVISORY_MEMORY_TO_DECISION_XADD_V1|R38SO_COMPACT_R38SM_MEMORY_ATTACH_SUMMARY_ONLY_V1|R38SP_LEGACY_R38QO_NO_BROKER_EMITTER_OPT_IN_ONLY_V1" app/mme_scalpx/services/strategy.py
  grep -nE "R38SK_COMMON_MULTI_WINDOW_MEMORY_ENGINE_V1|R38SKA_SOFT_ADVISORY_MEMORY_HYGIENE_V1" app/mme_scalpx/services/feature_family/multi_window_memory.py
}

compile_check(){
  .venv/bin/python -m py_compile app/mme_scalpx/services/strategy.py app/mme_scalpx/services/execution.py app/mme_scalpx/services/risk.py app/mme_scalpx/services/feature_family/multi_window_memory.py
  echo "PY_COMPILE_SELECTED_PASS=1"
}

finish_bundle(){
  local tag="$1" out="$2"
  tar -czf "run/evidence_bundles/${tag}.tar.gz" "$out"
  sha256sum "run/evidence_bundles/${tag}.tar.gz" > "run/evidence_bundles/${tag}.tar.gz.sha256"
  echo "BUNDLE=run/evidence_bundles/${tag}.tar.gz"
  echo "SHA=run/evidence_bundles/${tag}.tar.gz.sha256"
}

preflight(){
  IFS="|" read -r tag out report < <(mkout "R38SR_NEXT_MARKET_SESSION_CONTROLLED_PAPER_PREFLIGHT_NO_ORDER")
  {
    echo "===== $tag ====="; date -Is; pwd; hostname
    echo "SAFETY=NO_PATCH_NO_START_NO_XADD_NO_ORDER_NO_REAL_BROKER_NO_REAL_LIVE"
    proc; assert_no_runtime
    streams; assert_downstream_zero
    markers; compile_check
    echo "===== BROKER FILES REDACTED ====="
    for f in common/secrets/brokers/zerodha/credentials.env common/secrets/brokers/zerodha/session.env common/secrets/brokers/dhan/credentials.env common/secrets/brokers/dhan/session.env; do if [ -f "$f" ]; then echo "PRESENT $f"; sed "s/=.*$/=REDACTED/" "$f" | head -25; else echo "MISSING $f"; fi; done
    echo "===== LATEST SAMPLES ====="; redis-cli XREVRANGE features:mme:stream + - COUNT 1 || true; redis-cli XREVRANGE decisions:mme:stream + - COUNT 2 || true
    echo "CLASSIFICATION=R38SR_PREFLIGHT_DONE_NO_START_NO_ORDER"
    echo "NEXT_IF_PASS=ASK_APPROVAL_FOR_ONE_CONTROLLED_PAPER_RUNTIME_START"
  } | tee "$report"
  finish_bundle "$tag" "$out"
}

watch_readonly(){
  IFS="|" read -r tag out report < <(mkout "R38WATCH_CONTROLLED_PAPER_READONLY_MONITOR_NO_ORDER")
  local sleep_sec="${R38WATCH_SLEEP_SEC:-10}" ticks="${R38WATCH_TICKS:-60}" i=1
  {
    echo "===== $tag ====="; date -Is; echo "READ_ONLY=1 NO_PATCH=1 NO_START=1 NO_XADD=1 NO_ORDER=1"
    while [ "$i" -le "$ticks" ]; do echo "===== TICK $i/$ticks $(date -Is) ====="; proc; streams; redis-cli XREVRANGE decisions:mme:stream + - COUNT 1 || true; i=$((i+1)); sleep "$sleep_sec"; done
    echo "CLASSIFICATION=R38WATCH_DONE_NO_ORDER"
  } | tee "$report"
  finish_bundle "$tag" "$out"
}

stop_runtime(){
  IFS="|" read -r tag out report < <(mkout "R38STOP_EMERGENCY_RUNTIME_STOP_ONLY_NO_REDIS_DELETE_NO_ORDER")
  {
    echo "===== $tag ====="; date -Is; echo "STOP_RUNTIME_ONLY=1 DO_NOT_STOP_REDIS=1 NO_REDIS_DELETE=1"
    echo "===== BEFORE ====="; proc; streams
    pkill -TERM -f "python -m app\.mme_scalpx\.main" || true; pkill -TERM -f "NEXT_MARKET_SESSION_R38RN|R38QW_SHORT_LIVE_PAPER" || true; sleep 5
    pkill -KILL -f "python -m app\.mme_scalpx\.main" || true; pkill -KILL -f "NEXT_MARKET_SESSION_R38RN|R38QW_SHORT_LIVE_PAPER" || true
    echo "===== AFTER ====="; proc; streams; echo "CLASSIFICATION=R38STOP_RUNTIME_ONLY_DONE"
  } | tee "$report"
  finish_bundle "$tag" "$out"
}

post_bundle(){
  IFS="|" read -r tag out report < <(mkout "R38POST_ATTEMPT_EVIDENCE_BUNDLE_NO_PATCH_NO_ORDER")
  mkdir -p "$out/snapshots"
  {
    echo "===== $tag ====="; date -Is; echo "EVIDENCE_ONLY=1 NO_PATCH=1 NO_START=1 NO_XADD=1 NO_ORDER=1"
    proc; streams
    for k in decisions:mme:stream features:mme:stream orders:mme:stream risk:mme:stream execution:mme:stream trades:mme:stream trades:ledger:stream; do echo "### $k latest 5"; redis-cli XREVRANGE "$k" + - COUNT 5 2>/dev/null || true; done
    ls -td run/proofs/R38* 2>/dev/null | head -40 || true; ls -lht run/evidence_bundles/R38*.tar.gz 2>/dev/null | head -40 || true
    echo "CLASSIFICATION=R38POST_ATTEMPT_EVIDENCE_BUNDLE_DONE"
  } | tee "$report"
  cp -a app/mme_scalpx/services/strategy.py "$out/snapshots/strategy.py.snapshot" 2>/dev/null || true
  cp -a app/mme_scalpx/services/execution.py "$out/snapshots/execution.py.snapshot" 2>/dev/null || true
  cp -a app/mme_scalpx/services/risk.py "$out/snapshots/risk.py.snapshot" 2>/dev/null || true
  cp -a app/mme_scalpx/services/feature_family/multi_window_memory.py "$out/snapshots/multi_window_memory.py.snapshot" 2>/dev/null || true
  finish_bundle "$tag" "$out"
}

case "${1:-help}" in
  preflight) preflight ;;
  watch) watch_readonly ;;
  stop) stop_runtime ;;
  bundle) post_bundle ;;
  help|*) echo "Usage: bash bin/r38_ops.sh preflight|watch|stop|bundle"; exit 0 ;;
esac
