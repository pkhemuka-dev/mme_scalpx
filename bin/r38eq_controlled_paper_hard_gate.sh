#!/usr/bin/env bash
set +e

MODE="${R38EQ_HARD_GATE_MODE:-${1:-live-before-runner}}"
echo "=== R38EQ live-before-runner hard gate ==="
echo "R38EQ_HARD_GATE_MODE=$MODE"

xlen() {
  redis-cli XLEN "$1" 2>/dev/null | awk '{print $NF}' | tr -d '\r'
}

rtype() {
  redis-cli TYPE "$1" 2>/dev/null | awk '{print $NF}' | tr -d '\r'
}

hget() {
  redis-cli --raw HGET "$1" "$2" 2>/dev/null | tr -d '\r'
}

proc_count() {
  ps -eo args | grep -Ei "python.*app\.mme_scalpx\.main.*--service[ =]$1" | grep -v grep | wc -l | tr -d ' '
}

ORDERS_XLEN="$(xlen orders:mme:stream)"; ORDERS_XLEN="${ORDERS_XLEN:-0}"
RISK_XLEN="$(xlen risk:mme:stream)"; RISK_XLEN="${RISK_XLEN:-0}"
EXEC_XLEN="$(xlen execution:mme:stream)"; EXEC_XLEN="${EXEC_XLEN:-0}"
TRADES_XLEN="$(xlen trades:ledger:stream)"; TRADES_XLEN="${TRADES_XLEN:-0}"
CMD_XLEN="$(xlen cmd:mme:stream)"; CMD_XLEN="${CMD_XLEN:-0}"

FEEDS="$(proc_count feeds)"
FEATURES="$(proc_count features)"
STRATEGY="$(proc_count strategy)"
RISK_PROC="$(proc_count risk)"
EXEC_PROC="$(proc_count execution)"

MAXMEM="$(redis-cli CONFIG GET maxmemory 2>/dev/null | tail -1 | tr -d '\r')"
POLICY="$(redis-cli CONFIG GET maxmemory-policy 2>/dev/null | tail -1 | tr -d '\r')"
APPENDONLY="$(redis-cli CONFIG GET appendonly 2>/dev/null | tail -1 | tr -d '\r')"

POS_KEY=""
for k in state:position:mme state:mme:position position:mme:state position:mme r10d:position state:runtime:position; do
  t="$(rtype "$k")"
  if [ "$t" = "hash" ]; then
    side="$(hget "$k" position_side)"
    hasp="$(hget "$k" has_position)"
    ql="$(hget "$k" qty_lots)"
    qu="$(hget "$k" qty_units)"
    if [ -n "$side$hasp$ql$qu" ]; then
      POS_KEY="$k"
      break
    fi
  fi
done

if [ -z "$POS_KEY" ]; then
  for k in $(redis-cli --scan --pattern '*position*' 2>/dev/null | head -80); do
    t="$(rtype "$k")"
    [ "$t" = "hash" ] || continue
    side="$(hget "$k" position_side)"
    hasp="$(hget "$k" has_position)"
    ql="$(hget "$k" qty_lots)"
    qu="$(hget "$k" qty_units)"
    if [ -n "$side$hasp$ql$qu" ]; then
      POS_KEY="$k"
      break
    fi
  done
fi

POS_TYPE="none"
SIDE=""
QTY_LOTS=""
QTY_UNITS=""
HAS_POSITION=""
if [ -n "$POS_KEY" ]; then
  POS_TYPE="$(rtype "$POS_KEY")"
  SIDE="$(hget "$POS_KEY" position_side)"
  QTY_LOTS="$(hget "$POS_KEY" qty_lots)"
  QTY_UNITS="$(hget "$POS_KEY" qty_units)"
  HAS_POSITION="$(hget "$POS_KEY" has_position)"
fi

SIDE="${SIDE:-}"
QTY_LOTS="${QTY_LOTS:-}"
QTY_UNITS="${QTY_UNITS:-}"
HAS_POSITION="${HAS_POSITION:-}"

STRICT_FLAT=0
if [ "$POS_TYPE" = "hash" ] && [ "$SIDE" = "FLAT" ] && [ "${QTY_LOTS:-999}" = "0" ] && [ "${QTY_UNITS:-999}" = "0" ] && [ "${HAS_POSITION:-1}" = "0" ]; then
  STRICT_FLAT=1
fi

BROKER_TYPE="none"
BROKER_HLEN="0"
ORDERS_TYPE="none"
ORDERS_HLEN="0"
for k in state:broker:mme state:mme:broker broker:mme state:orders:mme orders:mme; do
  t="$(rtype "$k")"
  case "$k" in
    *broker*)
      BROKER_TYPE="$t"
      [ "$t" = "hash" ] && BROKER_HLEN="$(redis-cli HLEN "$k" 2>/dev/null | tr -d '\r')"
      ;;
    *orders*)
      ORDERS_TYPE="$t"
      [ "$t" = "hash" ] && ORDERS_HLEN="$(redis-cli HLEN "$k" 2>/dev/null | tr -d '\r')"
      ;;
  esac
done

REAL_ORDER_KEYS_HEAD="$(
  {
    redis-cli --scan --pattern '*real*order*' 2>/dev/null
    redis-cli --scan --pattern '*broker*order*' 2>/dev/null
    redis-cli --scan --pattern '*live*order*' 2>/dev/null
  } | sort -u | head -20
)"

real_order_clear=0
orders_zero=0
runtime_zero=0
cmd_zero=0

[ -z "$REAL_ORDER_KEYS_HEAD" ] && real_order_clear=1
[ "$ORDERS_XLEN" = "0" ] && [ "${ORDERS_HLEN:-0}" = "0" ] && orders_zero=1
[ "$RISK_XLEN" = "0" ] && [ "$EXEC_XLEN" = "0" ] && [ "$TRADES_XLEN" = "0" ] && [ "$RISK_PROC" = "0" ] && [ "$EXEC_PROC" = "0" ] && runtime_zero=1
[ "$CMD_XLEN" = "0" ] && cmd_zero=1

LOCK_RISK="$(redis-cli --raw GET lock:risk 2>/dev/null | tr -d '\r')"
LOCK_EXEC="$(redis-cli --raw GET lock:execution 2>/dev/null | tr -d '\r')"

bash -n bin/r38en_tomorrow_parallel_scope_controlled_paper_runner.sh >/dev/null 2>&1
RUNNER_SYNTAX="$?"
bash -n bin/r38eq_tomorrow_hardened_preflight_no_start.sh >/dev/null 2>&1
PREFLIGHT_SYNTAX="$?"

MARKER_R38EM=0
grep -R "R38EM" app/mme_scalpx/services/strategy.py >/dev/null 2>&1 && MARKER_R38EM=1

FORBIDDEN_RUNNER_MATCHES="$(
  grep -nE 'redis-cli[[:space:]]+(DEL|XDEL|XTRIM|FLUSHDB|FLUSHALL)|SCALPX_ALLOW_BROKER_ORDERS=1|SCALPX_ENABLE_LIVE=1|SCALPX_REAL_LIVE_ALLOWED=1|MME_ALLOW_BROKER_ORDERS=1' \
    bin/r38en_tomorrow_parallel_scope_controlled_paper_runner.sh 2>/dev/null | head -20
)"

echo "streams=${ORDERS_XLEN}/${RISK_XLEN}/${EXEC_XLEN}/${TRADES_XLEN}/${CMD_XLEN}"
echo "processes feeds=$FEEDS features=$FEATURES strategy=$STRATEGY risk=$RISK_PROC execution=$EXEC_PROC"
echo "redis maxmemory=$MAXMEM policy=$POLICY appendonly=$APPENDONLY"
echo "position key='${POS_KEY}' type=${POS_TYPE} side=${SIDE} qty_lots=${QTY_LOTS} qty_units=${QTY_UNITS} has_position=${HAS_POSITION} strict_flat=${STRICT_FLAT} real_order_clear=${real_order_clear} orders_zero=${orders_zero} runtime_zero=${runtime_zero} cmd_zero=${cmd_zero}"
echo "state broker_type=${BROKER_TYPE} broker_hlen=${BROKER_HLEN} orders_type=${ORDERS_TYPE} orders_hlen=${ORDERS_HLEN}"
echo "locks risk='${LOCK_RISK}' execution='${LOCK_EXEC}'"
echo "marker_r38em=${MARKER_R38EM} runner_syntax=${RUNNER_SYNTAX} preflight_syntax=${PREFLIGHT_SYNTAX}"
echo "real_order_keys_head=${REAL_ORDER_KEYS_HEAD}"
if [ -n "$FORBIDDEN_RUNNER_MATCHES" ]; then
  echo "forbidden_runner_matches=${FORBIDDEN_RUNNER_MATCHES}"
else
  echo "forbidden_runner_matches=none"
fi

FAILS=()
[ "$ORDERS_XLEN" = "0" ] || FAILS+=("orders_stream_not_zero:$ORDERS_XLEN")
[ "$RISK_XLEN" = "0" ] || FAILS+=("risk_stream_not_zero:$RISK_XLEN")
[ "$EXEC_XLEN" = "0" ] || FAILS+=("execution_stream_not_zero:$EXEC_XLEN")
[ "$TRADES_XLEN" = "0" ] || FAILS+=("trades_stream_not_zero:$TRADES_XLEN")
[ "$CMD_XLEN" = "0" ] || FAILS+=("cmd_stream_not_zero:$CMD_XLEN")
[ "$FEEDS" -ge 1 ] || FAILS+=("feeds_not_running:$FEEDS")
[ "$FEATURES" -ge 1 ] || FAILS+=("features_not_running:$FEATURES")
[ "$STRATEGY" -ge 1 ] || FAILS+=("observe_strategy_not_running:$STRATEGY")
[ "$RISK_PROC" = "0" ] || FAILS+=("risk_process_running:$RISK_PROC")
[ "$EXEC_PROC" = "0" ] || FAILS+=("execution_process_running:$EXEC_PROC")
[ "$POLICY" = "noeviction" ] || FAILS+=("redis_policy_not_noeviction:$POLICY")
[ "$STRICT_FLAT" = "1" ] || FAILS+=("position_not_strict_flat")
[ "$real_order_clear" = "1" ] || FAILS+=("real_order_clear_not_1:$real_order_clear")
[ "$orders_zero" = "1" ] || FAILS+=("orders_zero_not_1:$orders_zero")
[ "$runtime_zero" = "1" ] || FAILS+=("runtime_zero_not_1:$runtime_zero")
[ "$cmd_zero" = "1" ] || FAILS+=("cmd_zero_not_1:$cmd_zero")
[ -z "$LOCK_RISK" ] || FAILS+=("lock_risk_present:$LOCK_RISK")
[ -z "$LOCK_EXEC" ] || FAILS+=("lock_execution_present:$LOCK_EXEC")
[ "$MARKER_R38EM" = "1" ] || FAILS+=("marker_r38em_missing")
[ "$RUNNER_SYNTAX" = "0" ] || FAILS+=("runner_syntax_bad:$RUNNER_SYNTAX")
[ "$PREFLIGHT_SYNTAX" = "0" ] || FAILS+=("preflight_syntax_bad:$PREFLIGHT_SYNTAX")
[ -z "$FORBIDDEN_RUNNER_MATCHES" ] || FAILS+=("forbidden_runner_matches_present")

if [ "${#FAILS[@]}" -gt 0 ]; then
  echo "FAIL_R38EQ_HARD_GATE"
  for f in "${FAILS[@]}"; do echo " - $f"; done
  exit 2
fi

echo "PASS_R38EQ_HARD_GATE"
exit 0
