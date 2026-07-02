#!/usr/bin/env bash
# R38GA_DEPRECATE_R38EN_GUARD_BEGIN
# R38EN deprecated after R38FY/R38FZ/PSEAL. Use R38GA instead.
if [ "${SCALPX_ALLOW_DEPRECATED_R38EN:-}" != "1" ]; then
  echo "STOP_R38EN_DEPRECATED_USE_R38GA_KEEP_STRATEGY_UNTIL_RISK_OPEN_ONE_EVENT"
  exit 90
fi
# R38GA_DEPRECATE_R38EN_GUARD_END
# LANE-X-R29A MANUAL UNLOCK GUARD
# This prevents stale/background shells from launching controlled-paper runtime.
# To intentionally run later after hard gates, invoke with:
#   SCALPX_R38EN_MANUAL_UNLOCK=ACK_R38EN_MANUAL_UNLOCK_20260618 bash bin/r38en_tomorrow_parallel_scope_controlled_paper_runner.sh
if [ "${SCALPX_R38EN_MANUAL_UNLOCK:-}" != "ACK_R38EN_MANUAL_UNLOCK_20260618" ]; then
  echo "R38EN_BLOCKED_BY_R29A_MANUAL_UNLOCK_GUARD: set SCALPX_R38EN_MANUAL_UNLOCK=ACK_R38EN_MANUAL_UNLOCK_20260618 only after hard gate approval"
  exit 97
fi
# LANE-X-R29A MANUAL UNLOCK GUARD END

# R38EN tomorrow runner:
# Goal: one-lot controlled paper attempt with fresh exact scope, but without stopping observe strategy first.
# This avoids the R38EI stale-candidate delay.
#
# Safety:
# - paper only
# - no live broker orders
# - exact family/side/action/token/symbol ACK
# - one lot
# - stop after first event
# - restore observe-only after stop
# - no Redis delete / no lock delete

set +e

cd /home/Lenovo/scalpx/projects/mme_scalpx || exit 1

TAG="LANE-X-R38EN_TOMORROW_PARALLEL_SCOPE_CONTROLLED_PAPER_ONE_LOT_STOP_AFTER_EVENT_NO_LIVE_ORDER_$(date +%Y%m%d_%H%M%S)"
mkdir -p run/audits run/proofs run/evidence_bundles run/locks

LOG="run/audits/${TAG}.stdout"
SCOPE_LOCK="run/locks/${TAG}_scope_lock.json"
PSTATUS_BEFORE="run/audits/${TAG}_pstatus_before.json"
PSTATUS_AFTER="run/audits/${TAG}_pstatus_after.json"
EXEC_LOG="run/audits/${TAG}_execution.stdout"
RISK_LOG="run/audits/${TAG}_risk.stdout"
STRATEGY_LOG="run/audits/${TAG}_controlled_strategy.stdout"
MONITOR="run/audits/${TAG}_monitor.txt"
PROOF="run/proofs/${TAG}.json"
ARCHIVE="run/evidence_bundles/${TAG}.tar.gz"

EXEC_SESSION="r38en_execution_paper"
RISK_SESSION="r38en_risk_paper"
STRATEGY_SESSION="r38en_controlled_strategy"

exec > >(tee "$LOG") 2>&1

echo "=== $TAG ==="
date -Is
pwd

xlen_safe(){ redis-cli XLEN "$1" 2>/dev/null | awk '{print $1+0}'; }
safety(){ echo "$(xlen_safe orders:mme:stream)/$(xlen_safe risk:mme:stream)/$(xlen_safe execution:mme:stream)/$(xlen_safe trades:ledger:stream)"; }

restore_fail_closed() {
  tmux kill-session -t "$STRATEGY_SESSION" 2>/dev/null || true
  tmux kill-session -t "$RISK_SESSION" 2>/dev/null || true
  tmux kill-session -t "$EXEC_SESSION" 2>/dev/null || true

  ps -eo pid,args | grep -Ei 'python.*app\.mme_scalpx\.main.*--service[ =](risk|execution)' | grep -v grep | awk '{print $1}' | while read -r p; do
    [ -n "$p" ] && kill -TERM "$p" 2>/dev/null
  done
  sleep 3
  ps -eo pid,args | grep -Ei 'python.*app\.mme_scalpx\.main.*--service[ =](risk|execution)' | grep -v grep | awk '{print $1}' | while read -r p; do
    [ -n "$p" ] && kill -KILL "$p" 2>/dev/null
  done

  export SCALPX_OBSERVE_ONLY=1
  export B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY=1
  unset SCALPX_ENABLE_PAPER MME_ENABLE_PAPER SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME
  unset SCALPX_CONTROLLED_PAPER_SCOPE_ACK SCALPX_CONTROLLED_PAPER_FAMILY SCALPX_CONTROLLED_PAPER_SIDE
  unset SCALPX_CONTROLLED_PAPER_ACTION SCALPX_CONTROLLED_PAPER_INSTRUMENT_TOKEN SCALPX_CONTROLLED_PAPER_OPTION_SYMBOL
  unset SCALPX_CONTROLLED_PAPER_MAX_LOTS SCALPX_CONTROLLED_PAPER_LOTS SCALPX_CONTROLLED_PAPER_ONE_LOT SCALPX_CONTROLLED_PAPER_MICRO
  unset SCALPX_CONTROLLED_PAPER_MAX_EVENTS SCALPX_CONTROLLED_PAPER_STOP_AFTER_ONE
  unset SCALPX_POSITION_FLAT_VERIFIED SCALPX_FLAT_POSITION_VERIFIED
  unset SCALPX_CONTROLLED_PAPER_ARMED SCALPX_PAPER_ARMED
  unset SCALPX_ENABLE_RISK SCALPX_ENABLE_EXECUTION MME_ENABLE_RISK MME_ENABLE_EXECUTION
  unset SCALPX_ENABLE_LIVE SCALPX_REAL_LIVE_ALLOWED SCALPX_ALLOW_REAL_LIVE SCALPX_ALLOW_BROKER_ORDERS MME_ENABLE_LIVE MME_ALLOW_BROKER_ORDERS
}
trap restore_fail_closed EXIT INT TERM

echo "=== R38EQ hard gate before controlled runtime ==="
if [ -x bin/r38eq_controlled_paper_hard_gate.sh ]; then
  bash bin/r38eq_controlled_paper_hard_gate.sh live-before-runner
  R38EQ_GATE_RC="$?"
  echo "R38EQ_GATE_RC=$R38EQ_GATE_RC"
  if [ "$R38EQ_GATE_RC" != "0" ]; then
    echo "FAIL_R38EQ_HARD_GATE_BLOCKED_R38EN_NO_RUNTIME_START"
    exit 14
  fi
else
  echo "FAIL_R38EQ_GUARD_SCRIPT_MISSING_NO_RUNTIME_START"
  exit 14
fi


echo "=== R33I_AFTERMARKET_CONSUMER_GROUP_BOOTSTRAP_AND_ROUTE_DIAG_PATCH ==="
echo "R33I patch active: controlled runner will allow normal consumer group bootstrap; no Redis delete/trim; no live broker."
{
  echo "--- XINFO GROUPS decisions:mme:stream before runtime ---"
  redis-cli --raw XINFO GROUPS decisions:mme:stream 2>/dev/null || true
  echo "--- XINFO GROUPS risk:mme:stream before runtime ---"
  redis-cli --raw XINFO GROUPS risk:mme:stream 2>/dev/null || true
  echo "--- XINFO GROUPS execution:mme:stream before runtime ---"
  redis-cli --raw XINFO GROUPS execution:mme:stream 2>/dev/null || true
} | tee -a "$MONITOR"

echo "SAFETY_BEFORE=$(safety)"
if [ "$(safety)" != "0/0/0/0" ]; then
  echo "FAIL_CLOSED_STREAM_NONZERO_BEFORE_RUNTIME"
  exit 10
fi

FEEDS="$(ps -eo args | grep -Ei 'python.*app\.mme_scalpx\.main.*--service[ =]feeds' | grep -v grep | wc -l | tr -d ' ')"
FEATURES="$(ps -eo args | grep -Ei 'python.*app\.mme_scalpx\.main.*--service[ =]features' | grep -v grep | wc -l | tr -d ' ')"
OBS_STRATEGY="$(ps -eo args | grep -Ei 'python.*app\.mme_scalpx\.main.*--service[ =]strategy' | grep -v grep | wc -l | tr -d ' ')"
RISK0="$(ps -eo args | grep -Ei 'python.*app\.mme_scalpx\.main.*--service[ =]risk' | grep -v grep | wc -l | tr -d ' ')"
EXEC0="$(ps -eo args | grep -Ei 'python.*app\.mme_scalpx\.main.*--service[ =]execution' | grep -v grep | wc -l | tr -d ' ')"

echo "COUNTS_BEFORE feeds=$FEEDS features=$FEATURES observe_strategy=$OBS_STRATEGY risk=$RISK0 execution=$EXEC0"

if [ "$FEEDS" -lt 1 ] || [ "$FEATURES" -lt 1 ] || [ "$OBS_STRATEGY" -lt 1 ]; then
  echo "FAIL_OBSERVE_STACK_NOT_READY_START_R38EB_OR_R38EH_FIRST"
  exit 11
fi

if [ "$RISK0/$EXEC0" != "0/0" ]; then
  echo "FAIL_RISK_OR_EXECUTION_ALREADY_RUNNING"
  exit 12
fi

grep -n "R38EM_R1_PROJECTION_DIAG_AND_SYMBOL_FALLBACK_PATCH" app/mme_scalpx/services/strategy.py || {
  echo "FAIL_R38EM_R1_PATCH_NOT_PRESENT"
  exit 13
}

echo "=== FIND FRESH EXACT SCOPE FROM OBSERVE STRATEGY ==="
python3 - "$SCOPE_LOCK" <<'PY'
import json, re, subprocess, sys, datetime, pathlib, hashlib, time

out = pathlib.Path(sys.argv[1])
idre = re.compile(r"^[0-9]{10,17}-[0-9]+$")
ALLOWED_FAMILIES = {"MIST", "MISB", "MISC", "MISR"}
MAX_AGE_MS = 10000

def run(cmd):
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=8).stdout

def parse(raw):
    rows=[]; sid=None; fields={}; key=None
    for line in raw.splitlines():
        if idre.match(line):
            if sid is not None:
                rows.append((sid, fields))
            sid=line; fields={}; key=None
        elif sid is not None:
            if key is None:
                key=line
            else:
                fields[key]=line; key=None
    if sid is not None:
        rows.append((sid, fields))
    return rows

def jload(v):
    try:
        return json.loads(v) if isinstance(v,str) and v.strip().startswith(("{","[")) else None
    except Exception:
        return None

def mp(v):
    return v if isinstance(v,dict) else {}

def id_ms(s):
    try:
        return int(s.split("-")[0])
    except Exception:
        return 0

for attempt in range(1, 61):
    now_ms=int(time.time()*1000)
    rows=parse(run(["redis-cli","--raw","XREVRANGE","decisions:mme:stream","+","-","COUNT","120"]))

    for sid, f in rows:
        age=now_ms-id_ms(sid)
        if age > MAX_AGE_MS:
            continue

        payload=jload(f.get("payload_json","")) or {}
        activation=jload(f.get("activation_report_json") or payload.get("activation_report_json") or "") or {}
        selected=mp(activation.get("selected"))
        cand=mp(selected.get("candidate"))
        meta=mp(cand.get("metadata"))

        action=str(selected.get("action") or cand.get("action") or f.get("activation_selected_action") or payload.get("activation_selected_action") or "").upper()
        family=str(selected.get("family_id") or cand.get("family_id") or cand.get("doctrine_id") or meta.get("family_id") or "").upper()
        side=str(selected.get("branch_id") or selected.get("side") or cand.get("branch_id") or cand.get("side") or meta.get("side") or "").upper()
        token=str(cand.get("instrument_token") or cand.get("instrument_key") or meta.get("instrument_token") or meta.get("instrument_key") or f.get("candidate_instrument_token_shadow") or payload.get("candidate_instrument_token_shadow") or f.get("instrument_token") or payload.get("instrument_token") or "")
        symbol=str(cand.get("option_symbol") or meta.get("option_symbol") or f.get("candidate_symbol_shadow") or payload.get("candidate_symbol_shadow") or f.get("option_symbol") or payload.get("option_symbol") or f.get("symbol") or payload.get("symbol") or "").upper()
        price=cand.get("option_price") or cand.get("price") or meta.get("limit_price_hint") or f.get("price") or payload.get("price")
        score=selected.get("score") if selected.get("score") is not None else cand.get("score")

        if action in {"ENTER_CALL","ENTER_PUT"} and family in ALLOWED_FAMILIES and side in {"CALL","PUT"} and token and symbol and price not in (None,"","0",0):
            seed="|".join(["CONTROLLED_PAPER_SCOPE_ACK",family,side,action,token,symbol,"LOTS_1"])
            lock={
                "classification":"PASS_R38EN_FRESH_EXACT_SCOPE_LOCK_READY_NO_ARM_NO_ORDER",
                "created_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "attempt":attempt,
                "stream_id":sid,
                "age_ms":age,
                "family":family,
                "side":side,
                "action":action,
                "instrument_token":token,
                "option_symbol":symbol,
                "option_price":price,
                "score":score,
                "quantity_lots":1,
                "entry_mode":meta.get("entry_mode") or "DIRECT",
                "provider_id":meta.get("provider_id") or "ZERODHA",
                "ack_seed":seed,
                "ack":"ACK_"+hashlib.sha256(seed.encode()).hexdigest()[:20].upper(),
                "paper_armed":False,
                "risk_started":False,
                "execution_started":False,
                "order_attempted":False,
            }
            out.write_text(json.dumps(lock, indent=2, sort_keys=True, default=str), encoding="utf-8")
            print(json.dumps(lock, indent=2, sort_keys=True, default=str))
            raise SystemExit(0)

    print(f"NO_FRESH_EXACT_SCOPE attempt={attempt}")
    time.sleep(1)

print("FAIL_NO_FRESH_EXACT_SCOPE")
raise SystemExit(2)
PY

SCOPE_RC="$?"
echo "SCOPE_RC=$SCOPE_RC"
if [ "$SCOPE_RC" != "0" ]; then
  echo "REVIEW_NO_FRESH_SCOPE_NO_RUNTIME_START"
  exit 20
fi

eval "$(python3 - "$SCOPE_LOCK" <<'PY'
import json, shlex, sys
j=json.load(open(sys.argv[1]))
for k,v in {
  "ACK":j["ack"],
  "FAMILY":j["family"],
  "SIDE":j["side"],
  "ACTION":j["action"],
  "TOKEN":j["instrument_token"],
  "SYMBOL":j["option_symbol"],
}.items():
    print(f'{k}={shlex.quote(str(v))}')
PY
)"

echo "USING_SCOPE family=$FAMILY side=$SIDE action=$ACTION token=$TOKEN symbol=$SYMBOL ack=$ACK"

export SCALPX_OBSERVE_ONLY=0
export B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY=0
export SCALPX_ENABLE_PAPER=1
export MME_ENABLE_PAPER=1
export SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME=1
export SCALPX_CONTROLLED_PAPER_SCOPE_ACK="$ACK"
export SCALPX_CONTROLLED_PAPER_FAMILY="$FAMILY"
export SCALPX_CONTROLLED_PAPER_SIDE="$SIDE"
export SCALPX_CONTROLLED_PAPER_ACTION="$ACTION"
export SCALPX_CONTROLLED_PAPER_INSTRUMENT_TOKEN="$TOKEN"
export SCALPX_CONTROLLED_PAPER_OPTION_SYMBOL="$SYMBOL"
export SCALPX_CONTROLLED_PAPER_MAX_LOTS=1
export SCALPX_CONTROLLED_PAPER_LOTS=1
export SCALPX_CONTROLLED_PAPER_ONE_LOT=1
export SCALPX_CONTROLLED_PAPER_MICRO=1
export SCALPX_CONTROLLED_PAPER_MAX_EVENTS=1
export SCALPX_CONTROLLED_PAPER_STOP_AFTER_ONE=1
export SCALPX_POSITION_FLAT_VERIFIED=1
export SCALPX_FLAT_POSITION_VERIFIED=1
export SCALPX_CONTROLLED_PAPER_ARMED=1
export SCALPX_PAPER_ARMED=1
export SCALPX_ENABLE_RISK=1
export SCALPX_ENABLE_EXECUTION=1
export MME_ENABLE_RISK=1
export MME_ENABLE_EXECUTION=1
unset SCALPX_ENABLE_LIVE SCALPX_REAL_LIVE_ALLOWED SCALPX_ALLOW_REAL_LIVE SCALPX_ALLOW_BROKER_ORDERS MME_ENABLE_LIVE MME_ALLOW_BROKER_ORDERS

PYTHONPATH="$PWD:${PYTHONPATH:-}" ./bin/pstatus > "$PSTATUS_BEFORE" 2>&1 || true
cat "$PSTATUS_BEFORE" | head -120

python3 - "$PSTATUS_BEFORE" <<'PY'
import json, sys
j=json.load(open(sys.argv[1]))
v=j.get("paper_runtime_verdict",{})
s=j.get("safety",{})
ok = (
  v.get("paper_route_allowed") is True
  and v.get("paper_armed") is True
  and v.get("paper_enabled") is True
  and v.get("controlled_runtime_allowed") is True
  and v.get("position_flat_verified") is True
  and s.get("risk_execution_not_running") is True
  and s.get("orders_risk_execution") == "0/0/0"
)
print("PSTATUS_RUNTIME_OK=", ok)
raise SystemExit(0 if ok else 2)
PY

if [ "$?" != "0" ]; then
  echo "FAIL_PSTATUS_GATE_NOT_READY_NO_RUNTIME_START"
  exit 21
fi

O0="$(xlen_safe orders:mme:stream)"
R0="$(xlen_safe risk:mme:stream)"
E0="$(xlen_safe execution:mme:stream)"
T0="$(xlen_safe trades:ledger:stream)"
echo "STREAMS_BEFORE=$O0/$R0/$E0/$T0"

if [ "$O0/$R0/$E0/$T0" != "0/0/0/0" ]; then
  echo "FAIL_STREAM_NONZERO_BEFORE_RUNTIME"
  exit 22
fi

PYBIN=".venv/bin/python"
[ -x "$PYBIN" ] || PYBIN="python3"

echo "=== START EXECUTION PAPER ==="
tmux kill-session -t "$EXEC_SESSION" 2>/dev/null || true
tmux new-session -d -s "$EXEC_SESSION" "
cd /home/Lenovo/scalpx/projects/mme_scalpx
export SCALPX_OBSERVE_ONLY=0
export B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY=0
export SCALPX_ENABLE_PAPER=1
export MME_ENABLE_PAPER=1
export SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME=1
export SCALPX_CONTROLLED_PAPER_SCOPE_ACK='$ACK'
export SCALPX_CONTROLLED_PAPER_FAMILY='$FAMILY'
export SCALPX_CONTROLLED_PAPER_SIDE='$SIDE'
export SCALPX_CONTROLLED_PAPER_ACTION='$ACTION'
export SCALPX_CONTROLLED_PAPER_INSTRUMENT_TOKEN='$TOKEN'
export SCALPX_CONTROLLED_PAPER_OPTION_SYMBOL='$SYMBOL'
export SCALPX_CONTROLLED_PAPER_MAX_LOTS=1
export SCALPX_CONTROLLED_PAPER_LOTS=1
export SCALPX_CONTROLLED_PAPER_ONE_LOT=1
export SCALPX_CONTROLLED_PAPER_MICRO=1
export SCALPX_CONTROLLED_PAPER_MAX_EVENTS=1
export SCALPX_CONTROLLED_PAPER_STOP_AFTER_ONE=1
export SCALPX_POSITION_FLAT_VERIFIED=1
export SCALPX_FLAT_POSITION_VERIFIED=1
export SCALPX_CONTROLLED_PAPER_ARMED=1
export SCALPX_PAPER_ARMED=1
export SCALPX_ENABLE_EXECUTION=1
unset SCALPX_ENABLE_LIVE SCALPX_REAL_LIVE_ALLOWED SCALPX_ALLOW_REAL_LIVE SCALPX_ALLOW_BROKER_ORDERS MME_ENABLE_LIVE MME_ALLOW_BROKER_ORDERS
echo 'R38EN execution paper start' | tee -a '$EXEC_LOG'
date -Is | tee -a '$EXEC_LOG'
exec $PYBIN -m app.mme_scalpx.main --service execution --bootstrap-provider app.mme_scalpx.integrations.bootstrap_provider:provide 2>&1 | tee -a '$EXEC_LOG'
"

sleep 5

echo "=== START RISK PAPER ==="
tmux kill-session -t "$RISK_SESSION" 2>/dev/null || true
tmux new-session -d -s "$RISK_SESSION" "
cd /home/Lenovo/scalpx/projects/mme_scalpx
export SCALPX_OBSERVE_ONLY=0
export B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY=0
export SCALPX_ENABLE_PAPER=1
export MME_ENABLE_PAPER=1
export SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME=1
export SCALPX_CONTROLLED_PAPER_SCOPE_ACK='$ACK'
export SCALPX_CONTROLLED_PAPER_FAMILY='$FAMILY'
export SCALPX_CONTROLLED_PAPER_SIDE='$SIDE'
export SCALPX_CONTROLLED_PAPER_ACTION='$ACTION'
export SCALPX_CONTROLLED_PAPER_INSTRUMENT_TOKEN='$TOKEN'
export SCALPX_CONTROLLED_PAPER_OPTION_SYMBOL='$SYMBOL'
export SCALPX_CONTROLLED_PAPER_MAX_LOTS=1
export SCALPX_CONTROLLED_PAPER_LOTS=1
export SCALPX_CONTROLLED_PAPER_ONE_LOT=1
export SCALPX_CONTROLLED_PAPER_MICRO=1
export SCALPX_CONTROLLED_PAPER_MAX_EVENTS=1
export SCALPX_CONTROLLED_PAPER_STOP_AFTER_ONE=1
export SCALPX_POSITION_FLAT_VERIFIED=1
export SCALPX_FLAT_POSITION_VERIFIED=1
export SCALPX_CONTROLLED_PAPER_ARMED=1
export SCALPX_PAPER_ARMED=1
export SCALPX_ENABLE_RISK=1
unset SCALPX_ENABLE_LIVE SCALPX_REAL_LIVE_ALLOWED SCALPX_ALLOW_REAL_LIVE SCALPX_ALLOW_BROKER_ORDERS MME_ENABLE_LIVE MME_ALLOW_BROKER_ORDERS
echo 'R38EN risk paper start' | tee -a '$RISK_LOG'
date -Is | tee -a '$RISK_LOG'
exec $PYBIN -m app.mme_scalpx.main --service risk --bootstrap-provider app.mme_scalpx.integrations.bootstrap_provider:provide 2>&1 | tee -a '$RISK_LOG'
"

sleep 5

echo "=== START CONTROLLED STRATEGY IN PARALLEL; DO NOT STOP OBSERVE STRATEGY ==="
tmux kill-session -t "$STRATEGY_SESSION" 2>/dev/null || true
tmux new-session -d -s "$STRATEGY_SESSION" "
cd /home/Lenovo/scalpx/projects/mme_scalpx
export SCALPX_OBSERVE_ONLY=0
export B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY=0
export SCALPX_ENABLE_PAPER=1
export MME_ENABLE_PAPER=1
export SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME=1
export SCALPX_CONTROLLED_PAPER_SCOPE_ACK='$ACK'
export SCALPX_CONTROLLED_PAPER_FAMILY='$FAMILY'
export SCALPX_CONTROLLED_PAPER_SIDE='$SIDE'
export SCALPX_CONTROLLED_PAPER_ACTION='$ACTION'
export SCALPX_CONTROLLED_PAPER_INSTRUMENT_TOKEN='$TOKEN'
export SCALPX_CONTROLLED_PAPER_OPTION_SYMBOL='$SYMBOL'
export SCALPX_CONTROLLED_PAPER_MAX_LOTS=1
export SCALPX_CONTROLLED_PAPER_LOTS=1
export SCALPX_CONTROLLED_PAPER_ONE_LOT=1
export SCALPX_CONTROLLED_PAPER_MICRO=1
export SCALPX_CONTROLLED_PAPER_MAX_EVENTS=1
export SCALPX_CONTROLLED_PAPER_STOP_AFTER_ONE=1
export SCALPX_POSITION_FLAT_VERIFIED=1
export SCALPX_FLAT_POSITION_VERIFIED=1
export SCALPX_CONTROLLED_PAPER_ARMED=1
export SCALPX_PAPER_ARMED=1
unset SCALPX_ENABLE_LIVE SCALPX_REAL_LIVE_ALLOWED SCALPX_ALLOW_REAL_LIVE SCALPX_ALLOW_BROKER_ORDERS MME_ENABLE_LIVE MME_ALLOW_BROKER_ORDERS
echo 'R38EN controlled strategy start' | tee -a '$STRATEGY_LOG'
date -Is | tee -a '$STRATEGY_LOG'
exec $PYBIN -m app.mme_scalpx.main --service strategy --bootstrap-provider app.mme_scalpx.integrations.bootstrap_provider:provide 2>&1 | tee -a '$STRATEGY_LOG'
"

echo "=== MONITOR 480s STOP AFTER FIRST PAPER ACTIVITY OR PROJECTED ROW ===" | tee "$MONITOR"
EVENT_SEEN=0
PROJECTED_SEEN=0
TOP_ENTER_SEEN=0
BLOCKER_COUNTS_FILE="run/audits/${TAG}_projection_blockers.txt"

for i in $(seq 1 96); do
  sleep 5
  O="$(xlen_safe orders:mme:stream)"
  R="$(xlen_safe risk:mme:stream)"
  E="$(xlen_safe execution:mme:stream)"
  T="$(xlen_safe trades:ledger:stream)"

  PROJ="$(redis-cli --raw XREVRANGE decisions:mme:stream + - COUNT 80 2>/dev/null | grep -c 'projected_activation_selected_exact_scope_1lot' || true)"
  TOP="$(redis-cli --raw XREVRANGE decisions:mme:stream + - COUNT 80 2>/dev/null | grep -E 'ENTER_CALL|ENTER_PUT' | wc -l | tr -d ' ')"
  BLOCKERS="$(redis-cli --raw XREVRANGE decisions:mme:stream + - COUNT 80 2>/dev/null | grep -A1 'r38ee_projection_blocker' | tail -40 | tr '\n' '|' | cut -c1-1000)"

  [ "$PROJ" -gt 0 ] && PROJECTED_SEEN=1
  [ "$TOP" -gt 0 ] && TOP_ENTER_SEEN=1

  echo "WATCH i=$i streams=$O/$R/$E/$T projected_hits=$PROJ top_enter_hits=$TOP blockers=$BLOCKERS ts=$(date -Is)" | tee -a "$MONITOR"

  if [ "$i" = "1" ] || [ "$i" = "6" ] || [ "$i" = "12" ] || [ "$PROJ" -gt 0 ]; then
    {
      echo "--- R33I group diag i=$i ts=$(date -Is) ---"
      echo "decisions groups:"
      redis-cli --raw XINFO GROUPS decisions:mme:stream 2>/dev/null || true
      echo "risk groups:"
      redis-cli --raw XINFO GROUPS risk:mme:stream 2>/dev/null || true
      echo "execution groups:"
      redis-cli --raw XINFO GROUPS execution:mme:stream 2>/dev/null || true
    } >> "$MONITOR"
  fi

  echo "i=$i blockers=$BLOCKERS" >> "$BLOCKER_COUNTS_FILE"

  if [ "$O" -gt "$O0" ] || [ "$R" -gt "$R0" ] || [ "$E" -gt "$E0" ] || [ "$T" -gt "$T0" ]; then
    EVENT_SEEN=1
    echo "PAPER_ACTIVITY_SEEN_WAIT_20S_THEN_STOP" | tee -a "$MONITOR"
    sleep 20
    break
  fi
done

echo "=== STOP CONTROLLED RUNTIME ==="
restore_fail_closed
trap - EXIT INT TERM

sleep 8

O1="$(xlen_safe orders:mme:stream)"
R1="$(xlen_safe risk:mme:stream)"
E1="$(xlen_safe execution:mme:stream)"
T1="$(xlen_safe trades:ledger:stream)"

FEEDS_AFTER="$(ps -eo args | grep -Ei 'python.*app\.mme_scalpx\.main.*--service[ =]feeds' | grep -v grep | wc -l | tr -d ' ')"
FEATURES_AFTER="$(ps -eo args | grep -Ei 'python.*app\.mme_scalpx\.main.*--service[ =]features' | grep -v grep | wc -l | tr -d ' ')"
STRATEGY_AFTER="$(ps -eo args | grep -Ei 'python.*app\.mme_scalpx\.main.*--service[ =]strategy' | grep -v grep | wc -l | tr -d ' ')"
RISK_AFTER="$(ps -eo args | grep -Ei 'python.*app\.mme_scalpx\.main.*--service[ =]risk' | grep -v grep | wc -l | tr -d ' ')"
EXEC_AFTER="$(ps -eo args | grep -Ei 'python.*app\.mme_scalpx\.main.*--service[ =]execution' | grep -v grep | wc -l | tr -d ' ')"

PYTHONPATH="$PWD:${PYTHONPATH:-}" ./bin/pstatus > "$PSTATUS_AFTER" 2>&1 || true

echo "=== FINAL ==="
echo "STREAMS_BEFORE=$O0/$R0/$E0/$T0"
echo "STREAMS_AFTER=$O1/$R1/$E1/$T1"
echo "EVENT_SEEN=$EVENT_SEEN"
echo "PROJECTED_SEEN=$PROJECTED_SEEN"
echo "TOP_ENTER_SEEN=$TOP_ENTER_SEEN"
echo "COUNTS_AFTER feeds=$FEEDS_AFTER features=$FEATURES_AFTER strategy=$STRATEGY_AFTER risk=$RISK_AFTER execution=$EXEC_AFTER"
cat "$PSTATUS_AFTER" | head -120

echo "--- controlled strategy tail ---"
tail -120 "$STRATEGY_LOG" 2>/dev/null || true
echo "--- risk tail ---"
tail -100 "$RISK_LOG" 2>/dev/null || true
echo "--- execution tail ---"
tail -100 "$EXEC_LOG" 2>/dev/null || true
echo "--- monitor tail ---"
tail -120 "$MONITOR" 2>/dev/null || true

if [ "$EVENT_SEEN" = "1" ] && [ "$RISK_AFTER/$EXEC_AFTER" = "0/0" ]; then
  CLASS="PASS_R38EN_PARALLEL_SCOPE_CONTROLLED_PAPER_ACTIVITY_SEEN_AND_STOPPED_NO_LIVE_ORDER"
elif [ "$PROJECTED_SEEN" = "1" ] && [ "$RISK_AFTER/$EXEC_AFTER" = "0/0" ]; then
  CLASS="REVIEW_R38EN_PROJECTED_ENTER_SEEN_BUT_NO_PAPER_ACTIVITY_NO_LIVE_ORDER"
else
  CLASS="REVIEW_R38EN_NO_PROJECTED_OR_PAPER_ACTIVITY_NO_LIVE_ORDER"
fi

python3 - "$PROOF" "$TAG" "$CLASS" "$SCOPE_LOCK" "$O0/$R0/$E0/$T0" "$O1/$R1/$E1/$T1" "$EVENT_SEEN" "$PROJECTED_SEEN" "$TOP_ENTER_SEEN" "$FEEDS_AFTER" "$FEATURES_AFTER" "$STRATEGY_AFTER" "$RISK_AFTER" "$EXEC_AFTER" <<'PY'
import json, sys, datetime, pathlib
proof={
  "classification":sys.argv[3],
  "tag":sys.argv[2],
  "created_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
  "scope_lock":sys.argv[4],
  "streams_before":sys.argv[5],
  "streams_after":sys.argv[6],
  "event_seen":sys.argv[7]=="1",
  "projected_seen":sys.argv[8]=="1",
  "top_enter_seen":sys.argv[9]=="1",
  "feeds_process_count_after":int(sys.argv[10]),
  "features_process_count_after":int(sys.argv[11]),
  "strategy_process_count_after":int(sys.argv[12]),
  "risk_process_count_after":int(sys.argv[13]),
  "execution_process_count_after":int(sys.argv[14]),
  "paper_runtime_started":True,
  "quantity_lots":1,
  "real_live_allowed":False,
  "broker_live_order_allowed":False,
  "redis_delete_attempted":False,
  "lock_delete_attempted":False
}
pathlib.Path(sys.argv[1]).write_text(json.dumps(proof, indent=2), encoding="utf-8")
print(json.dumps(proof, indent=2))
PY

tar -czf "$ARCHIVE" "$LOG" "$PROOF" "$SCOPE_LOCK" "$PSTATUS_BEFORE" "$PSTATUS_AFTER" "$EXEC_LOG" "$RISK_LOG" "$STRATEGY_LOG" "$MONITOR" "$BLOCKER_COUNTS_FILE" 2>/dev/null || true
sha256sum "$ARCHIVE" > "${ARCHIVE}.sha256" 2>/dev/null || true

echo "ARCHIVE=$ARCHIVE"
cat "${ARCHIVE}.sha256" 2>/dev/null || true
echo "R38EN_DONE_PARALLEL_SCOPE_CONTROLLED_PAPER_RUNNER_NO_LIVE_ORDER"
