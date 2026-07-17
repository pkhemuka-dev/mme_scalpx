#!/usr/bin/env bash
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

MODE="${MODE:-paper}"              # paper | observe | real
FAMILY="${FAMILY:-MIST}"
DURATION_SEC="${DURATION_SEC:-7200}"
SAMPLE_EVERY_SEC="${SAMPLE_EVERY_SEC:-5}"
REPORT_MODE="${REPORT_MODE:-lean}" # lean disables report during live session
ORDER_LOTS="${ORDER_LOTS:-1}"

case "$MODE" in
  paper|observe|real) ;;
  *) echo "ERROR: MODE must be paper, observe, or real. Got=$MODE" >&2; exit 2 ;;
esac

PYBIN=".venv/bin/python"
[ -x "$PYBIN" ] || PYBIN="$(command -v python3)"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"

TS="$(date +%Y%m%d_%H%M%S)"
SESSION_TAG="MME_DAILY_${MODE}_${FAMILY}_${TS}"
PROOF_DIR="run/proofs/${SESSION_TAG}"
CAPTURE_DIR="run/daily_sessions/${SESSION_TAG}"
mkdir -p "$PROOF_DIR" "$CAPTURE_DIR" run/evidence_bundles run/logs run/runtime

LOG="$PROOF_DIR/${SESSION_TAG}.log"
exec > >(tee -a "$LOG") 2>&1

echo "===== MME DAILY SESSION ====="
echo "SESSION_TAG=$SESSION_TAG"
echo "MODE=$MODE"
echo "FAMILY=$FAMILY"
echo "DURATION_SEC=$DURATION_SEC"
echo "REPORT_MODE=$REPORT_MODE"
date -Is

# Clean stale runtime only. No Redis delete/trim.
pkill -TERM -f "app.mme_scalpx.main" || true
sleep 5
pkill -KILL -f "app.mme_scalpx.main" || true
sleep 3

echo
echo "===== PRECHECK ====="
ps -ef | grep -E 'app\.mme_scalpx\.main|redis-server' | grep -v grep || true
redis-cli -h "${SCALPX_REDIS_HOST:-127.0.0.1}" -p "${SCALPX_REDIS_PORT:-6379}" -n "${SCALPX_REDIS_DB:-0}" PING || true

RUNTIME_ENV=(
  HOME="$HOME"
  USER="$USER"
  PATH="$PATH"
  PYTHONPATH="$ROOT:${PYTHONPATH:-}"
  MME_BOOTSTRAP_PROVIDER="app.mme_scalpx.integrations.bootstrap_provider:provide"
  SCALPX_ALLOW_ALL_SERVICE_MAIN=1
  SCALPX_REDIS_HOST="${SCALPX_REDIS_HOST:-127.0.0.1}"
  SCALPX_REDIS_PORT="${SCALPX_REDIS_PORT:-6379}"
  SCALPX_REDIS_DB="${SCALPX_REDIS_DB:-0}"
  SCALPX_REDIS_TLS=0
  SCALPX_REDIS_SSL=0
  REDIS_TLS=0
  REDIS_SSL=0
)

# Existing permanent lean switch found in main.py.
if [ "$REPORT_MODE" = "lean" ]; then
  RUNTIME_ENV+=(
    SCALPX_DISABLE_REPORT_SERVICE=1
    SCALPX_DISABLE_REPORT_SERVICE_ACK="R38RP_DISABLE_REPORT_FOR_REDIS_TIMEOUT_BLOCKER_LEAN_RUNTIME"
  )
fi

if [ "$MODE" = "observe" ]; then
  RUNTIME_ENV+=(
    SCALPX_OBSERVE_ONLY=1
    B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY=1
  )
elif [ "$MODE" = "paper" ]; then
  RUNTIME_ENV+=(
    SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME=1
    SCALPX_ENABLE_PAPER=1
    MME_ENABLE_PAPER=1
    SCALPX_PAPER_ARMED=1
    SCALPX_CONTROLLED_PAPER_ARMED=1
    SCALPX_POSITION_FLAT_VERIFIED=1
    SCALPX_FLAT_POSITION_VERIFIED=1
    SCALPX_CONTROLLED_PAPER_DYNAMIC_FIRST_ENTER=1
    SCALPX_CONTROLLED_PAPER_FAMILY="$FAMILY"
    SCALPX_CONTROLLED_PAPER_SCOPE_ACK="ACK_DAILY_PAPER_${SESSION_TAG}"
    SCALPX_CONTROLLED_PAPER_NO_BROKER_ACK="ACK_DAILY_PAPER_${SESSION_TAG}"
  )
elif [ "$MODE" = "real" ]; then
  if [ "${MME_REAL_TRADE_ACK:-}" != "I_APPROVE_REAL_BROKER_ORDERS_FOR_THIS_SESSION" ]; then
    echo "ERROR: real mode requires exact MME_REAL_TRADE_ACK." >&2
    exit 41
  fi
  if [ -z "${REAL_SCOPE_ACK:-}" ]; then
    echo "ERROR: real mode requires non-empty REAL_SCOPE_ACK." >&2
    exit 42
  fi
  RUNTIME_ENV+=(
    SCALPX_ENABLE_LIVE=1
    MME_ENABLE_LIVE=1
    SCALPX_REAL_LIVE_ALLOWED=1
    SCALPX_ALLOW_REAL_LIVE=1
    SCALPX_ALLOW_BROKER_ORDERS=1
    MME_ALLOW_BROKER_ORDERS=1
    SCALPX_BROKER_ORDER_ENABLED=1
    SCALPX_ALLOW_LIVE_ORDERS=1
    SCALPX_TRADING_ENABLED=1
    SCALPX_POSITION_FLAT_VERIFIED=1
    SCALPX_FLAT_POSITION_VERIFIED=1
    SCALPX_ORDER_LOTS="$ORDER_LOTS"
    SCALPX_ORDER_MAX_LOTS="$ORDER_LOTS"
    SCALPX_REAL_LIVE_SCOPE_ACK="$REAL_SCOPE_ACK"
    SCALPX_R38QT_REOPEN_LIVE_ACK="R38QT_REOPEN_AFTER_ONE_EVENT_ENFORCEMENT_PATCHED_AND_TESTED"
    SCALPX_LIVE_ONE_EVENT_ONLY="${SCALPX_LIVE_ONE_EVENT_ONLY:-1}"
  )
fi

echo
echo "===== EFFECTIVE ENV REDACTED ====="
printf '%s\n' "${RUNTIME_ENV[@]}" \
  | sed -E 's/([A-Z0-9_]*(TOKEN|SECRET|PASSWORD|API_KEY|ACCESS_KEY|ACCESS_TOKEN)[A-Z0-9_]*=).*/\1REDACTED/gI' \
  | tee "$PROOF_DIR/${SESSION_TAG}_effective_env.txt"

echo
echo "===== START RUNTIME ====="
nohup env -i "${RUNTIME_ENV[@]}" "$PYBIN" -m app.mme_scalpx.main \
  > "$PROOF_DIR/${SESSION_TAG}_runtime.log" 2>&1 &

MAIN_PID=$!
echo "MAIN_PID=$MAIN_PID" | tee "$PROOF_DIR/${SESSION_TAG}_pid.txt"
sleep 45

echo
echo "===== STARTUP TAIL ====="
ps -ef | grep -E 'app\.mme_scalpx\.main|redis-server' | grep -v grep || true
tail -220 "$PROOF_DIR/${SESSION_TAG}_runtime.log" || true

echo
echo "===== MONITOR STREAM DELTAS ====="
CAPTURE_DIR="$CAPTURE_DIR" SESSION_TAG="$SESSION_TAG" MODE="$MODE" DURATION_SEC="$DURATION_SEC" SAMPLE_EVERY_SEC="$SAMPLE_EVERY_SEC" "$PYBIN" - <<'PY' | tee "$PROOF_DIR/${SESSION_TAG}_monitor_summary.json"
import os, json, time, gzip, datetime, pathlib, subprocess

host=os.environ.get("SCALPX_REDIS_HOST","127.0.0.1")
port=os.environ.get("SCALPX_REDIS_PORT","6379")
db=os.environ.get("SCALPX_REDIS_DB","0")
capture=pathlib.Path(os.environ["CAPTURE_DIR"])
capture.mkdir(parents=True, exist_ok=True)
duration=int(os.environ.get("DURATION_SEC","7200"))
sample=int(os.environ.get("SAMPLE_EVERY_SEC","5"))
tag=os.environ.get("SESSION_TAG","unknown")
mode=os.environ.get("MODE","paper")

streams=[
 "features:mme:stream","decisions:mme:stream","decisions:ack:stream",
 "orders:mme:stream","risk:mme:stream","execution:mme:stream",
 "trades:mme:stream","trades:ledger:stream","cmd:mme:stream",
 "ticks:mme:fut:stream","ticks:mme:fut:zerodha:stream",
 "ticks:mme:opt:selected:zerodha:stream","ticks:mme:opt:stream"
]

def rc(*args, timeout=10):
    return subprocess.run(["redis-cli","-h",host,"-p",port,"-n",db,*args], text=True, capture_output=True, timeout=timeout)

def xlen(s):
    p=rc("XLEN",s)
    try: return int((p.stdout or "0").strip() or "0")
    except Exception: return None

pre={s:xlen(s) for s in streams}
timeline=gzip.open(capture/"timeline.jsonl.gz","at",encoding="utf-8")
samples=gzip.open(capture/"latest_samples.jsonl.gz","at",encoding="utf-8")

decision_enter_seen=False
order_seen=False
risk_seen=False
execution_seen=False
trade_seen=False
deadline=time.time()+duration

try:
    while time.time() < deadline:
        lens={s:xlen(s) for s in streams}
        delta={s:(lens[s]-pre[s] if lens.get(s) is not None and pre.get(s) is not None else None) for s in streams}

        latest={}
        for s in ["decisions:mme:stream","orders:mme:stream","risk:mme:stream","execution:mme:stream","trades:mme:stream","trades:ledger:stream"]:
            p=rc("XREVRANGE",s,"+","-","COUNT","10")
            latest[s]=[x.strip() for x in (p.stdout or "").splitlines() if x.strip()][:220]

        blob=json.dumps(latest).upper()
        decision_enter_seen = decision_enter_seen or any(k in blob for k in ["ENTER_CALL","ENTER_PUT","ACTIVATION_PROMOTED"])
        order_seen = order_seen or ((delta.get("orders:mme:stream") or 0) > 0)
        risk_seen = risk_seen or ((delta.get("risk:mme:stream") or 0) > 0)
        execution_seen = execution_seen or ((delta.get("execution:mme:stream") or 0) > 0)
        trade_seen = trade_seen or ((delta.get("trades:mme:stream") or 0) > 0) or ((delta.get("trades:ledger:stream") or 0) > 0)

        row={"ts":datetime.datetime.now(datetime.timezone.utc).isoformat(),"session_tag":tag,"mode":mode,"delta":delta,"decision_enter_seen":decision_enter_seen,"order_seen":order_seen,"risk_seen":risk_seen,"execution_seen":execution_seen,"trade_seen":trade_seen}
        timeline.write(json.dumps(row,sort_keys=True)+"\n"); timeline.flush()
        samples.write(json.dumps({"ts":row["ts"],"latest":latest},sort_keys=True)+"\n"); samples.flush()
        time.sleep(sample)
finally:
    timeline.close(); samples.close()

post={s:xlen(s) for s in streams}
delta={s:(post[s]-pre[s] if post.get(s) is not None and pre.get(s) is not None else None) for s in streams}
out={"ts":datetime.datetime.now(datetime.timezone.utc).isoformat(),"session_tag":tag,"mode":mode,"duration_sec":duration,"pre":pre,"post":post,"delta":delta,"decision_enter_seen":decision_enter_seen,"order_seen":order_seen,"risk_seen":risk_seen,"execution_seen":execution_seen,"trade_seen":trade_seen,"capture_dir":str(capture)}
(capture/"monitor_summary.json").write_text(json.dumps(out,indent=2,sort_keys=True))
print(json.dumps(out,indent=2,sort_keys=True))
PY
MONITOR_RC="${PIPESTATUS[0]}"
echo "MONITOR_RC=$MONITOR_RC"

echo
echo "===== STOP RUNTIME ====="
pkill -TERM -f "app.mme_scalpx.main" || true
sleep 5
pkill -KILL -f "app.mme_scalpx.main" || true
sleep 3

echo
echo "===== PNL REVIEW ====="
"$PYBIN" bin/mme_daily_pnl_review.py \
  --mode "$MODE" \
  --session-tag "$SESSION_TAG" \
  --capture-dir "$CAPTURE_DIR" \
  --output-dir "$PROOF_DIR" \
  | tee "$PROOF_DIR/${SESSION_TAG}_pnl_review_stdout.json"
PNL_RC="${PIPESTATUS[0]}"
echo "PNL_RC=$PNL_RC"

echo
echo "===== SESSION SUMMARY ====="
"$PYBIN" - <<PY | tee "$PROOF_DIR/${SESSION_TAG}_summary.json"
import json, pathlib, datetime
proof=pathlib.Path("$PROOF_DIR")
mon=json.load(open(proof/"${SESSION_TAG}_monitor_summary.json"))
pnl=json.load(open(proof/"${SESSION_TAG}_pnl_review.json"))
out={
 "session_tag":"$SESSION_TAG",
 "mode":"$MODE",
 "ts":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "monitor_rc":int("$MONITOR_RC"),
 "pnl_rc":int("$PNL_RC"),
 "decision_enter_seen":bool(mon.get("decision_enter_seen")),
 "order_seen":bool(mon.get("order_seen")),
 "risk_seen":bool(mon.get("risk_seen")),
 "execution_seen":bool(mon.get("execution_seen")),
 "trade_seen":bool(mon.get("trade_seen")),
 "closed_trades":pnl.get("closed_trades"),
 "gross_pnl":pnl.get("gross_pnl"),
 "net_pnl":pnl.get("net_pnl"),
 "win_rate_pct":pnl.get("win_rate_pct"),
 "next":"analyze_pnl_winrate_bad_trade_buckets_then_patch_filters"
}
print(json.dumps(out,indent=2,sort_keys=True))
PY

ARCHIVE="run/evidence_bundles/${SESSION_TAG}.tar.gz"
tar -czf "$ARCHIVE" "$PROOF_DIR" "$CAPTURE_DIR"
sha256sum "$ARCHIVE" | tee "${ARCHIVE}.sha256"

echo "ARCHIVE=$ARCHIVE"
cat "${ARCHIVE}.sha256"
echo "NEXT=REVIEW_PNL_WINRATE_BAD_TRADE_BUCKETS"
