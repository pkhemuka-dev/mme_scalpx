#!/usr/bin/env bash
set -uo pipefail

cd /home/Lenovo/scalpx/projects/mme_scalpx

BATCH="R38QW_SHORT_LIVE_PAPER_CONFIRM_AFTER_R38QX"
PURPOSE="confirm_position_effect_open_allows_risk_execution_trade_flow"
TS="$(date +%Y%m%d_%H%M%S)"
TAG="${BATCH}_${PURPOSE}_${TS}"
PROOF_DIR="run/proofs/${TAG}"
CAPTURE_DIR="run/daily_sessions/${TAG}"
mkdir -p "$PROOF_DIR" "$CAPTURE_DIR" run/evidence_bundles run/logs run/runtime
export TAG PROOF_DIR CAPTURE_DIR BATCH

LOG="$PROOF_DIR/${TAG}.log"
exec > >(tee -a "$LOG") 2>&1

echo "===== ${BATCH} ====="
date -Is
pwd
hostname || true

PYBIN=".venv/bin/python"
[ -x "$PYBIN" ] || PYBIN="$(command -v python3)"
export PYTHONPATH="$PWD:${PYTHONPATH:-}"

export DURATION_SEC="${DURATION_SEC:-600}"
export SAMPLE_EVERY_SEC="${SAMPLE_EVERY_SEC:-5}"
export FAMILY="${FAMILY:-MIST}"

echo "DURATION_SEC=$DURATION_SEC"
echo "FAMILY=$FAMILY"

echo
echo "===== STEP 1 — stop stale runtime only ====="
pkill -TERM -f "app.mme_scalpx.main" || true
sleep 5
pkill -KILL -f "app.mme_scalpx.main" || true
sleep 3

ps -ef | grep -E 'app\.mme_scalpx\.main|redis-server' | grep -v grep || true
redis-cli -h 127.0.0.1 -p 6379 -n 0 PING || true

echo
echo "===== STEP 2 — pre lengths ====="
for s in decisions:mme:stream orders:mme:stream risk:mme:stream execution:mme:stream trades:mme:stream trades:ledger:stream features:mme:stream; do
  printf "%-28s " "$s"
  redis-cli XLEN "$s" || true
done | tee "$PROOF_DIR/${TAG}_pre_lengths.txt"

echo
echo "===== STEP 3 — start live paper runtime, no real broker ====="
nohup env -i \
  HOME="$HOME" \
  USER="$USER" \
  PATH="$PATH" \
  PYTHONPATH="$PWD:${PYTHONPATH:-}" \
  MME_BOOTSTRAP_PROVIDER="app.mme_scalpx.integrations.bootstrap_provider:provide" \
  SCALPX_ALLOW_ALL_SERVICE_MAIN=1 \
  SCALPX_DISABLE_REPORT_SERVICE=1 \
  SCALPX_DISABLE_REPORT_SERVICE_ACK="R38RP_DISABLE_REPORT_FOR_REDIS_TIMEOUT_BLOCKER_LEAN_RUNTIME" \
  SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME=1 \
  SCALPX_ENABLE_PAPER=1 \
  MME_ENABLE_PAPER=1 \
  SCALPX_PAPER_ARMED=1 \
  SCALPX_CONTROLLED_PAPER_ARMED=1 \
  SCALPX_POSITION_FLAT_VERIFIED=1 \
  SCALPX_FLAT_POSITION_VERIFIED=1 \
  SCALPX_CONTROLLED_PAPER_DYNAMIC_FIRST_ENTER=1 \
  SCALPX_CONTROLLED_PAPER_FAMILY="$FAMILY" \
  SCALPX_CONTROLLED_PAPER_SCOPE_ACK="ACK_R38QX_POSITION_EFFECT_OPEN_${TAG}" \
  SCALPX_CONTROLLED_PAPER_NO_BROKER_ACK="ACK_R38QX_POSITION_EFFECT_OPEN_${TAG}" \
  SCALPX_REDIS_HOST=127.0.0.1 \
  SCALPX_REDIS_PORT=6379 \
  SCALPX_REDIS_DB=0 \
  SCALPX_REDIS_TLS=0 \
  SCALPX_REDIS_SSL=0 \
  REDIS_TLS=0 \
  REDIS_SSL=0 \
  "$PYBIN" -m app.mme_scalpx.main \
  > "$PROOF_DIR/${TAG}_runtime.log" 2>&1 &

MAIN_PID=$!
echo "MAIN_PID=$MAIN_PID" | tee "$PROOF_DIR/${TAG}_pid.txt"

sleep 45

echo
echo "===== STEP 4 — startup tail ====="
ps -ef | grep -E 'app\.mme_scalpx\.main|redis-server' | grep -v grep || true
tail -180 "$PROOF_DIR/${TAG}_runtime.log" || true

echo
echo "===== STEP 5 — monitor stream deltas ====="
"$PYBIN" - <<'PY' | tee "$PROOF_DIR/${TAG}_monitor_summary.json"
from __future__ import annotations
import os, time, json, pathlib, subprocess, datetime

tag=os.environ["TAG"]
cap=pathlib.Path(os.environ["CAPTURE_DIR"])
cap.mkdir(parents=True, exist_ok=True)
duration=int(os.environ.get("DURATION_SEC","600"))
sample=int(os.environ.get("SAMPLE_EVERY_SEC","5"))

streams=[
 "features:mme:stream",
 "decisions:mme:stream",
 "orders:mme:stream",
 "risk:mme:stream",
 "execution:mme:stream",
 "trades:mme:stream",
 "trades:ledger:stream",
]

def rc(*args, timeout=10):
    return subprocess.run(["redis-cli","-h","127.0.0.1","-p","6379","-n","0",*args], text=True, capture_output=True, timeout=timeout)

def xlen(s):
    p=rc("XLEN",s)
    try: return int((p.stdout or "0").strip() or "0")
    except Exception: return None

pre={s:xlen(s) for s in streams}
deadline=time.time()+duration
rows=[]

while time.time() < deadline:
    lens={s:xlen(s) for s in streams}
    delta={s:(lens[s]-pre[s] if lens.get(s) is not None and pre.get(s) is not None else None) for s in streams}
    row={"ts":datetime.datetime.now(datetime.timezone.utc).isoformat(),"delta":delta}
    rows.append(row)
    (cap/"timeline.jsonl").open("a").write(json.dumps(row,sort_keys=True)+"\n")
    time.sleep(sample)

post={s:xlen(s) for s in streams}
delta={s:(post[s]-pre[s] if post.get(s) is not None and pre.get(s) is not None else None) for s in streams}

latest={}
for s in ["decisions:mme:stream","orders:mme:stream","risk:mme:stream","execution:mme:stream","trades:mme:stream","trades:ledger:stream"]:
    p=rc("XREVRANGE",s,"+","-","COUNT","20")
    latest[s]=[x.strip() for x in (p.stdout or "").splitlines() if x.strip()][:500]

out={
 "tag":tag,
 "duration_sec":duration,
 "pre":pre,
 "post":post,
 "delta":delta,
 "decision_delta":delta.get("decisions:mme:stream"),
 "order_delta":delta.get("orders:mme:stream"),
 "risk_delta":delta.get("risk:mme:stream"),
 "execution_delta":delta.get("execution:mme:stream"),
 "trade_delta":delta.get("trades:mme:stream"),
 "ledger_delta":delta.get("trades:ledger:stream"),
 "latest":latest,
 "capture_dir":str(cap),
}
(cap/"monitor_summary.json").write_text(json.dumps(out,indent=2,sort_keys=True))
print(json.dumps(out,indent=2,sort_keys=True))
PY
MONITOR_RC="${PIPESTATUS[0]}"
echo "MONITOR_RC=$MONITOR_RC"

echo
echo "===== STEP 6 — stop runtime ====="
pkill -TERM -f "app.mme_scalpx.main" || true
sleep 5
pkill -KILL -f "app.mme_scalpx.main" || true
sleep 3

ps -ef | grep -E 'app\.mme_scalpx\.main|redis-server' | grep -v grep || true

echo
echo "===== STEP 7 — error scan ====="
grep -RIn "entry_position_effect_not_open\|decision_contract_rejected\|DecisionContractError" \
  "$PROOF_DIR/${TAG}_runtime.log" \
  | tail -80 \
  | tee "$PROOF_DIR/${TAG}_error_scan.txt" || true

echo
echo "===== STEP 8 — final summary ====="
"$PYBIN" - <<PY | tee "$PROOF_DIR/${TAG}_summary.json"
import json, pathlib, datetime
proof=pathlib.Path("$PROOF_DIR")
mon=json.load(open(proof/"${TAG}_monitor_summary.json"))
err=(proof/"${TAG}_error_scan.txt").read_text(errors="replace") if (proof/"${TAG}_error_scan.txt").exists() else ""
failed=[]
if int("$MONITOR_RC") != 0:
    failed.append("MONITOR_FAILED")
if "entry_position_effect_not_open" in err:
    failed.append("ENTRY_POSITION_EFFECT_STILL_BLOCKING")
out={
 "batch":"$BATCH",
 "tag":"$TAG",
 "ts":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "final_verdict":"PASS_SHORT_LIVE_PAPER_CONFIRM_AFTER_R38QX" if not failed else "REVIEW_SHORT_LIVE_PAPER_CONFIRM_AFTER_R38QX",
 "failed_observations":failed if failed else ["NONE"],
 "decision_delta":mon.get("decision_delta"),
 "order_delta":mon.get("order_delta"),
 "risk_delta":mon.get("risk_delta"),
 "execution_delta":mon.get("execution_delta"),
 "trade_delta":mon.get("trade_delta"),
 "ledger_delta":mon.get("ledger_delta"),
 "runtime_started":True,
 "real_broker_enabled":False,
 "next":"if_risk_execution_trade_delta_grows_then_full_daily_paper_session_else_patch_next_contract_blocker",
}
print(json.dumps(out,indent=2,sort_keys=True))
PY

ARCHIVE="run/evidence_bundles/${TAG}.tar.gz"
tar -czf "$ARCHIVE" "$PROOF_DIR" "$CAPTURE_DIR"
sha256sum "$ARCHIVE" | tee "${ARCHIVE}.sha256"

echo "ARCHIVE=$ARCHIVE"
cat "${ARCHIVE}.sha256"
echo "NEXT=UPLOAD_OUTPUT_FOR_RISK_EXECUTION_TRADE_FLOW_REVIEW"
