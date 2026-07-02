#!/usr/bin/env bash
set -euo pipefail

cd /home/Lenovo/scalpx/projects/mme_scalpx

TAG="LANE-X-R10J_TOMORROW_ONE_LOT_CONTROLLED_PAPER_WRAPPER_$(date +%Y%m%d_%H%M%S)"
mkdir -p run/audits run/proofs run/handoffs

OUT="run/audits/${TAG}_runner.txt"
PROOF="run/proofs/${TAG}.json"

ACK_EXPECTED="I APPROVE R10J ONE-LOT CONTROLLED PAPER ONLY: NO REAL LIVE, NO BROKER ORDER, NO REAL MONEY, MAX ONE PROJECTED ENTER OR PAPER EVENT, STOP AND FREEZE EVIDENCE"
ACK_GOT="${R10J_ONE_LOT_CONTROLLED_PAPER_ACK:-}"

echo "=== R10J TOMORROW ONE-LOT CONTROLLED-PAPER WRAPPER ===" | tee "$OUT"
echo "This wrapper may start controlled-paper ONLY after exact R10J ACK." | tee -a "$OUT"
echo "No real live / no broker order / max-one event / stop-freeze evidence." | tee -a "$OUT"
echo "TAG=$TAG" | tee -a "$OUT"
date -Is | tee -a "$OUT"

if [ "$ACK_GOT" != "$ACK_EXPECTED" ]; then
  echo "ABORT: missing exact R10J_ONE_LOT_CONTROLLED_PAPER_ACK" | tee -a "$OUT"
  cat > "$PROOF" <<JSON
{
  "classification": "R10J_ABORTED_MISSING_EXACT_ACK_NO_START_NO_ORDER",
  "started": false,
  "order": false
}
JSON
  exit 42
fi

export SCALPX_REAL_LIVE_ALLOWED=0
export SCALPX_ALLOW_REAL_LIVE=0
export SCALPX_ALLOW_BROKER_ORDERS=0
export SCALPX_ENABLE_LIVE=0
export MME_ENABLE_LIVE=0
export MME_ALLOW_BROKER_ORDERS=0

echo
echo "=== HARD R10H PREFLIGHT BEFORE DELEGATING TO R38EN ===" | tee -a "$OUT"

POLICY="$(redis-cli CONFIG GET maxmemory-policy 2>/dev/null | tail -1 | tr -d '\r')"
if [ "$POLICY" != "noeviction" ]; then
  echo "ABORT: redis policy is $POLICY, expected noeviction" | tee -a "$OUT"
  exit 43
fi

HP="$(redis-cli HGET state:position:mme has_position 2>/dev/null || true)"
PSIDE="$(redis-cli HGET state:position:mme position_side 2>/dev/null || true)"
QLOTS="$(redis-cli HGET state:position:mme qty_lots 2>/dev/null || true)"
QUNITS="$(redis-cli HGET state:position:mme qty_units 2>/dev/null || true)"
if [ "$HP" != "0" ] || [ "$PSIDE" != "FLAT" ] || [ "$QLOTS" != "0" ] || [ "$QUNITS" != "0" ]; then
  echo "ABORT: position hash not strict FLAT: has_position=$HP side=$PSIDE qty_lots=$QLOTS qty_units=$QUNITS" | tee -a "$OUT"
  exit 44
fi

for k in lock:execution lock:feeds lock:monitor; do
  v="$(redis-cli GET "$k" 2>/dev/null || true)"
  if [ -n "$v" ]; then
    echo "ABORT: lock not clear $k=$v" | tee -a "$OUT"
    exit 45
  fi
done

O="$(redis-cli XLEN orders:mme:stream 2>/dev/null || echo 999)"
R="$(redis-cli XLEN risk:mme:stream 2>/dev/null || echo 999)"
E="$(redis-cli XLEN execution:mme:stream 2>/dev/null || echo 999)"
T="$(redis-cli XLEN trades:ledger:stream 2>/dev/null || echo 999)"
C="$(redis-cli XLEN cmd:mme:stream 2>/dev/null || echo 999)"
if [ "$O/$R/$E/$T/$C" != "0/0/0/0/0" ]; then
  echo "ABORT: order/runtime/cmd streams not zero: $O/$R/$E/$T/$C" | tee -a "$OUT"
  exit 46
fi

echo "R10H_PREFLIGHT_OK" | tee -a "$OUT"

echo
echo "=== PSTATUS MUST ALLOW ===" | tee -a "$OUT"
PSTATUS_JSON="$(mktemp)"
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
  SCALPX_CONTROLLED_PAPER_SCOPE_ACK="I ACKNOWLEDGE CONTROLLED PAPER ONLY: NO REAL LIVE, NO BROKER ORDER, NO REAL MONEY, ONE APPROVED SCOPE ONLY, POSITION MUST START FLAT" \
  SCALPX_REAL_LIVE_ALLOWED=0 \
  SCALPX_ALLOW_REAL_LIVE=0 \
  SCALPX_ALLOW_BROKER_ORDERS=0 \
  SCALPX_ENABLE_LIVE=0 \
  ./bin/pstatus > "$PSTATUS_JSON"

cat "$PSTATUS_JSON" | tee -a "$OUT"

python3 - "$PSTATUS_JSON" <<'PY'
import json, sys
p=json.load(open(sys.argv[1]))
v=p.get("paper_runtime_verdict",{})
if v.get("paper_route_allowed") is not True:
    raise SystemExit("pstatus_not_allowed")
if v.get("reason") != "CONTROLLED_PAPER_ROUTE_ALLOWED_BY_PSTATUS_GATES":
    raise SystemExit("pstatus_reason_unexpected")
PY

echo "PSTATUS_ALLOWED_OK" | tee -a "$OUT"

if [ ! -x bin/r38en_tomorrow_parallel_scope_controlled_paper_runner.sh ]; then
  echo "ABORT: missing executable bin/r38en_tomorrow_parallel_scope_controlled_paper_runner.sh" | tee -a "$OUT"
  exit 47
fi

echo
echo "=== DELEGATING TO R38EN RUNNER ===" | tee -a "$OUT"
echo "R38EN must enforce max-one scoped controlled-paper event and evidence freeze." | tee -a "$OUT"

bash bin/r38en_tomorrow_parallel_scope_controlled_paper_runner.sh 2>&1 | tee -a "$OUT"
RC=${PIPESTATUS[0]}

echo "R38EN_RC=$RC" | tee -a "$OUT"

cat > "$PROOF" <<JSON
{
  "classification": "R10J_WRAPPER_DELEGATED_TO_R38EN_RC_${RC}",
  "r38en_rc": ${RC},
  "real_live_allowed": false,
  "broker_order_allowed": false,
  "max_one_event_scope": true,
  "audit": "$OUT"
}
JSON

exit "$RC"
