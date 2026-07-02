#!/usr/bin/env bash
# R38GC_NEXT_POINTER_PATCH_R38GA: next runner is R38GA, not deprecated R38EN
# R38EQ hardened no-start preflight wrapper.
# This does not run R38EN. It only checks R10H-style hard gate + R38EO preflight.

set +e
cd /home/Lenovo/scalpx/projects/mme_scalpx || exit 1

TAG="LANE-X-R38EQ_TOMORROW_HARDENED_PREFLIGHT_NO_START_NO_ARM_NO_ORDER_$(date +%Y%m%d_%H%M%S)"
mkdir -p run/audits run/proofs run/evidence_bundles

LOG="run/audits/${TAG}.stdout"
PROOF="run/proofs/${TAG}.json"
ARCHIVE="run/evidence_bundles/${TAG}.tar.gz"

exec > >(tee "$LOG") 2>&1

echo "=== $TAG ==="
date -Is
pwd

export SCALPX_OBSERVE_ONLY=1
export B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY=1
unset SCALPX_ENABLE_LIVE SCALPX_ENABLE_PAPER SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME
unset SCALPX_CONTROLLED_PAPER_SCOPE_ACK SCALPX_CONTROLLED_PAPER_ARMED SCALPX_PAPER_ARMED
unset SCALPX_REAL_LIVE_ALLOWED SCALPX_ALLOW_REAL_LIVE SCALPX_ALLOW_BROKER_ORDERS
unset MME_ENABLE_LIVE MME_ENABLE_PAPER MME_ALLOW_BROKER_ORDERS
unset SCALPX_ENABLE_RISK SCALPX_ENABLE_EXECUTION MME_ENABLE_RISK MME_ENABLE_EXECUTION

echo "=== R38EQ live-before-runner hard gate ==="
bash bin/r38eq_controlled_paper_hard_gate.sh live-before-runner
GATE_RC="$?"
echo "GATE_RC=$GATE_RC"

echo "=== R38EO no-start preflight ==="
bash bin/r38eo_tomorrow_preflight_no_start.sh
PREFLIGHT_RC="$?"
echo "PREFLIGHT_RC=$PREFLIGHT_RC"

CLASS="REVIEW_R38EQ_HARDENED_PREFLIGHT_NOT_READY_NO_START_NO_ARM_NO_ORDER"
if [ "$GATE_RC" = "0" ] && [ "$PREFLIGHT_RC" = "0" ]; then
  CLASS="PASS_R38EQ_HARDENED_PREFLIGHT_READY_FOR_R38EN_WHEN_MARKET_LIVE_NO_START_NO_ARM_NO_ORDER"
fi

python3 - "$PROOF" "$TAG" "$CLASS" "$GATE_RC" "$PREFLIGHT_RC" <<'PY'
import json, sys, datetime, pathlib
proof={
  "classification":sys.argv[3],
  "tag":sys.argv[2],
  "created_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
  "gate_rc":int(sys.argv[4]),
  "preflight_rc":int(sys.argv[5]),
  "next_if_pass":"bash bin/r38ga_keep_strategy_until_risk_open_one_event.sh",
  "runtime_started":False,
  "paper_armed":False,
  "paper_started":False,
  "risk_started":False,
  "execution_started":False,
  "order_attempted":False,
  "redis_delete_attempted":False,
  "lock_delete_attempted":False
}
pathlib.Path(sys.argv[1]).write_text(json.dumps(proof, indent=2), encoding="utf-8")
print(json.dumps(proof, indent=2))
PY

tar -czf "$ARCHIVE" "$LOG" "$PROOF" 2>/dev/null || true
sha256sum "$ARCHIVE" > "${ARCHIVE}.sha256" 2>/dev/null || true

echo "ARCHIVE=$ARCHIVE"
cat "${ARCHIVE}.sha256" 2>/dev/null || true
echo "R38EQ_HARDENED_PREFLIGHT_DONE_NO_START_NO_ARM_NO_ORDER"
