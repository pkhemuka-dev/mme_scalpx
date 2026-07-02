#!/usr/bin/env bash
cd /home/Lenovo/scalpx/projects/mme_scalpx || exit 1
set +e

TAG="LANE-X-R38GC_MORNING_OBSERVE_BOOTSTRAP_NO_PAPER_$(date +%Y%m%d_%H%M%S)"
mkdir -p run/audits run/logs

echo "=== $TAG ==="
date -Is
pwd

PY="$PWD/.venv/bin/python"
[ -x "$PY" ] || PY="$(command -v python3)"
PROVIDER="app.mme_scalpx.integrations.bootstrap_provider:provide"

echo "=== 0) OBSERVE ONLY ENV ==="
export SCALPX_OBSERVE_ONLY=1
export B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY=1
unset SCALPX_ENABLE_LIVE SCALPX_ENABLE_PAPER SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME
unset SCALPX_CONTROLLED_PAPER_ARMED SCALPX_PAPER_ARMED SCALPX_CONTROLLED_PAPER_SCOPE_ACK
unset SCALPX_REAL_LIVE_ALLOWED SCALPX_ALLOW_REAL_LIVE SCALPX_ALLOW_BROKER_ORDERS
unset MME_ENABLE_LIVE MME_ENABLE_PAPER MME_ALLOW_BROKER_ORDERS
unset SCALPX_ENABLE_RISK SCALPX_ENABLE_EXECUTION MME_ENABLE_RISK MME_ENABLE_EXECUTION

echo "=== 1) STOP RISK/EXECUTION ONLY ==="
ps -eo pid,args | awk '/python/ && /-m app\.mme_scalpx\.main/ && /--service[ =](risk|execution)/ && $0 !~ /awk/ {print $1}' | while read p; do
  [ -n "$p" ] || continue
  echo "SIGTERM runtime PID=$p"
  kill -TERM "$p" 2>/dev/null || true
done
sleep 4

echo "=== 2) REDIS POLICY ==="
redis-cli CONFIG SET maxmemory-policy noeviction
redis-cli INFO memory | egrep 'used_memory_human|maxmemory_human|maxmemory_policy|mem_fragmentation_ratio' || true

echo "=== 3) PROTECTED STREAMS ZERO ==="
for s in orders:mme:stream risk:mme:stream execution:mme:stream trades:ledger:stream cmd:mme:stream; do
  v="$(redis-cli XLEN "$s" 2>/dev/null | awk '{print $NF}')"
  echo "$s=$v"
  [ "$v" = "0" ] || { echo "STOP_PROTECTED_STREAM_NOT_ZERO $s=$v"; exit 42; }
done

echo "=== 4) STRICT FLAT CHECK ==="
HAS_POS="$(redis-cli HGET state:position:mme has_position 2>/dev/null | tr -d '\r')"
SIDE="$(redis-cli HGET state:position:mme position_side 2>/dev/null | tr -d '\r')"
QTY_LOTS="$(redis-cli HGET state:position:mme qty_lots 2>/dev/null | tr -d '\r')"
QTY_UNITS="$(redis-cli HGET state:position:mme qty_units 2>/dev/null | tr -d '\r')"
echo "position has_position=$HAS_POS side=$SIDE qty_lots=$QTY_LOTS qty_units=$QTY_UNITS"

[ "$HAS_POS" = "0" ] && [ "$SIDE" = "FLAT" ] && [ "${QTY_LOTS:-0}" = "0" ] && [ "${QTY_UNITS:-0}" = "0" ] || {
  echo "STOP_POSITION_NOT_STRICT_FLAT_MANUAL_VERIFY_REQUIRED"
  exit 44
}

start_if_missing() {
  service="$1"
  extra="$2"
  n="$(ps -eo args | grep -Ei "python.*app\.mme_scalpx\.main.*--service[ =]${service}" | grep -v grep | wc -l | tr -d ' ')"
  echo "${service}_before=$n"
  if [ "$n" = "0" ]; then
    echo "START_OBSERVE_${service}"
    nohup env PYTHONPATH="$PWD:${PYTHONPATH:-}" \
      SCALPX_OBSERVE_ONLY=1 \
      B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY=1 \
      "$PY" -m app.mme_scalpx.main --service "$service" --bootstrap-provider "$PROVIDER" $extra \
      > "run/logs/${TAG}_${service}.log" 2>&1 &
    echo "${service}_pid=$!"
  fi
}

echo "=== 5) START OBSERVE STACK IF MISSING ==="
start_if_missing feeds ""
sleep 4
start_if_missing features "--skip-group-bootstrap"
sleep 4
start_if_missing strategy "--skip-group-bootstrap"

echo "=== 6) WAIT STACK READY ==="
READY=0
for i in $(seq 1 60); do
  FEEDS="$(ps -eo args | grep -Ei 'python.*app\.mme_scalpx\.main.*--service[ =]feeds' | grep -v grep | wc -l | tr -d ' ')"
  FEATURES="$(ps -eo args | grep -Ei 'python.*app\.mme_scalpx\.main.*--service[ =]features' | grep -v grep | wc -l | tr -d ' ')"
  STRATEGY="$(ps -eo args | grep -Ei 'python.*app\.mme_scalpx\.main.*--service[ =]strategy' | grep -v grep | wc -l | tr -d ' ')"
  RISK="$(ps -eo args | grep -Ei 'python.*app\.mme_scalpx\.main.*--service[ =]risk' | grep -v grep | wc -l | tr -d ' ')"
  EXECUTION="$(ps -eo args | grep -Ei 'python.*app\.mme_scalpx\.main.*--service[ =]execution' | grep -v grep | wc -l | tr -d ' ')"
  echo "WAIT_STACK i=$i feeds=$FEEDS features=$FEATURES strategy=$STRATEGY risk=$RISK execution=$EXECUTION"
  [ "$FEEDS" -ge 1 ] && [ "$FEATURES" -ge 1 ] && [ "$STRATEGY" -ge 1 ] && [ "$RISK" = "0" ] && [ "$EXECUTION" = "0" ] && { READY=1; break; }
  sleep 2
done

[ "$READY" = "1" ] || { echo "STOP_OBSERVE_STACK_NOT_READY"; exit 70; }

echo "=== 7) R38EQ TEXT PASS REQUIRED ==="
OUT="run/audits/${TAG}_r38eq.txt"
bash bin/r38eq_tomorrow_hardened_preflight_no_start.sh | tee "$OUT"
grep -q "PASS_R38EQ_HARD_GATE" "$OUT" || { echo "STOP_R38EQ_TEXT_NOT_PASS"; exit 71; }
grep -q "FAIL_R38EQ_HARD_GATE" "$OUT" && { echo "STOP_R38EQ_TEXT_HAS_FAIL"; exit 72; }

echo "READY_TO_RUN_R38GA_AFTER_THIS"
echo "bash bin/r38ga_keep_strategy_until_risk_open_one_event.sh"
echo "DONE_${TAG}_OBSERVE_READY_NO_PAPER_NO_RISK_EXECUTION"
