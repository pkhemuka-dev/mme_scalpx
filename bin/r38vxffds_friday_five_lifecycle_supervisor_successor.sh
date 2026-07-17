#!/usr/bin/env bash
set -Eeuo pipefail

cd /home/Lenovo/scalpx/projects/mme_scalpx || exit 1

SELF="bin/r38vxffds_friday_five_lifecycle_supervisor_successor.sh"
RUNNER="bin/r38vxffdp_current_one_event_runner_successor.sh"
GUARD="bin/r38vxffdl_disabled_five_lifecycle_guarded_successor.sh"
BROKER_GATE="bin/r38vxffdr_broker_readonly_safety_gate.py"
LEGACY_SUPERVISOR="bin/r38vb_unattended_multi_lifecycle_paper.sh"
STRATEGY="app/mme_scalpx/services/strategy.py"
EXECUTION="app/mme_scalpx/services/execution.py"
MANAGER="app/mme_scalpx/services/strategy_family/position_exit_manager.py"
RESOLVER="app/mme_scalpx/services/strategy_family/exact_position_quote_resolver.py"
MANIFEST="run/controls/lane_x_friday_paper_hashes.env"
MANIFEST_SHA="${MANIFEST}.sha256"

EXPECTED_RUNNER_SHA="80284a7b109b65850ad7905d30ec649e9c3c9363c9380c0886ce066e23b9f7a3"
EXPECTED_BROKER_GATE_SHA="a0da81e62ec84f1fc62b6002697db55c715b8e98a0351fcb9476c7aa0eaa1dd9"
EXPECTED_LEGACY_SUPERVISOR_SHA="941187b8dfcb8d669410cc1fac8156d00810de426995b5b6df6f294eff3cf2aa"
EXPECTED_STRATEGY_SHA="b6374975d85f7bfe4c44dbe1188caef3fb4fdd316e4323a513b25329a9d5fc52"
EXPECTED_EXECUTION_SHA="94744378b4b7a7ae2d4754a0f1dbf87a06861b0dd8973639b7beece44abcd0a2"
EXPECTED_MANAGER_SHA="ca2742bf5d6b1fd127b7cab7b219ebe1639a626de1c8c288a8e99b0e4e8cf5a0"
EXPECTED_RESOLVER_SHA="4a4365f804321bd7c8ff3ef630224a7c2ea3a8419c7c7bc8866753acdeae26c0"

MAX_LIFECYCLES="${R38VXFFDS_MAX_LIFECYCLES:-5}"
ENTRY_CUTOFF_HHMM="${R38VXFFDS_ENTRY_CUTOFF_HHMM:-1450}"
MAX_CONSECUTIVE_FULL_STOP_LOSSES=2
MAX_CUMULATIVE_LOSS_POINTS=-8
REQUIRED_AUTH="LANE_X_FRIDAY_20260717_CONTROLLED_PAPER_MAX5_NO_REAL_MONEY"

sha_file(){ sha256sum "$1" 2>/dev/null | awk '{print $1}'; }
count_service(){ pgrep -fc "app\\.mme_scalpx\\.main --service $1([[:space:]]|$)" 2>/dev/null || true; }
position_field(){ redis-cli --raw HGET state:position:mme "$1" 2>/dev/null || true; }
position_is_flat(){
  [ "$(position_field has_position)" = "0" ] &&
  [ "$(position_field position_side)" = "FLAT" ] &&
  [ "$(position_field qty_lots)" = "0" ] &&
  [ "$(position_field qty_units)" = "0" ]
}

if [ "${1:-}" = "--selftest" ]; then
  case "$MAX_LIFECYCLES" in 1|2|3|4|5) ;; *) exit 1;; esac
  bash -n "$RUNNER" "$GUARD" "$LEGACY_SUPERVISOR"
  .venv/bin/python -m py_compile "$BROKER_GATE" "$STRATEGY" "$EXECUTION" "$MANAGER" "$RESOLVER"
  [ "$(sha_file "$RUNNER")" = "$EXPECTED_RUNNER_SHA" ]
  [ "$(sha_file "$BROKER_GATE")" = "$EXPECTED_BROKER_GATE_SHA" ]
  [ "$(sha_file "$LEGACY_SUPERVISOR")" = "$EXPECTED_LEGACY_SUPERVISOR_SHA" ]
  [ "$(sha_file "$STRATEGY")" = "$EXPECTED_STRATEGY_SHA" ]
  [ "$(sha_file "$EXECUTION")" = "$EXPECTED_EXECUTION_SHA" ]
  [ "$(sha_file "$MANAGER")" = "$EXPECTED_MANAGER_SHA" ]
  [ "$(sha_file "$RESOLVER")" = "$EXPECTED_RESOLVER_SHA" ]
  grep -q 'R38TK3_FAMILY_CONTRACT_EXIT_V3' "$MANAGER"
  grep -q 'R38VXFFDP_ENABLE_CURRENT_RUNNER_SUCCESSOR' "$RUNNER"
  grep -q 'broker_readonly_flat "pre_stop"' "$RUNNER"
  grep -q 'R38VXFFDM_ENABLE_MARKET_SESSION_GUARD' "$GUARD"
  echo "SELFTEST_CLASSIFICATION=PASS_R38VXFFDS_FRIDAY_FIVE_LIFECYCLE_SUPERVISOR_SUCCESSOR"
  echo "PAPER_STARTED=0"
  echo "LIVE_STARTED=0"
  exit 0
fi

[ "${R38VXFFDS_ENABLE_PAPER_SESSION:-0}" = "1" ] || {
  echo "FINAL_CLASSIFICATION=BLOCK_FRIDAY_PAPER_SUPERVISOR_DISABLED_BY_DEFAULT"
  echo "PAPER_STARTED=0"
  echo "LIVE_STARTED=0"
  exit 1
}
[ "${R38VXFFDS_SESSION_AUTHORIZATION:-}" = "$REQUIRED_AUTH" ] || {
  echo "FINAL_CLASSIFICATION=BLOCK_MISSING_EXACT_FRIDAY_CONTROLLED_PAPER_AUTHORIZATION"
  exit 1
}
case "$MAX_LIFECYCLES" in 1|2|3|4|5) ;; *) echo "STOP_INVALID_MAX_LIFECYCLES"; exit 1;; esac
[ "$ENTRY_CUTOFF_HHMM" -le 1450 ] || { echo "STOP_CUTOFF_EXTENSION_FORBIDDEN"; exit 1; }

TAG="LANE-X-R38VXFFDS_FRIDAY_MAX5_CONTROLLED_PAPER_$(TZ=Asia/Kolkata date +%Y%m%d_%H%M%S)"
OUT="run/proofs/$TAG"
ARCHIVE="run/evidence_bundles/${TAG}.tar.gz"
mkdir -p "$OUT"/{logs,results,broker,streams,children,raw_manifest} run/evidence_bundles
exec > >(tee "$OUT/run.txt") 2>&1

FINAL_CLASSIFICATION="BLOCK_SESSION_NOT_COMPLETED"
FINAL_REASON="UNSET"
ATTEMPTED=0
COMPLETED=0
UNFILLED=0
VETOED=0
TIMED_OUT_FLAT=0
FAILED=0
CONSECUTIVE_FULL_STOPS=0
CUMULATIVE_POINTS="0"

seal_evidence(){
  local rc=$?
  set +e
  printf 'FINAL_CLASSIFICATION=%s\nFINAL_REASON=%s\nATTEMPTED=%s\nCOMPLETED=%s\nUNFILLED=%s\nVETOED=%s\nTIMED_OUT_FLAT=%s\nFAILED=%s\nCONSECUTIVE_FULL_STOPS=%s\nCUMULATIVE_POINTS=%s\nREAL_MONEY_ALLOWED=0\nBROKER_ORDER_ALLOWED=0\n' \
    "$FINAL_CLASSIFICATION" "$FINAL_REASON" "$ATTEMPTED" "$COMPLETED" "$UNFILLED" "$VETOED" "$TIMED_OUT_FLAT" "$FAILED" "$CONSECUTIVE_FULL_STOPS" "$CUMULATIVE_POINTS" > "$OUT/summary.env"
  ps -eo pid,ppid,etime,args | grep -E 'app\.mme_scalpx\.main.*--service (feeds|features|strategy|risk|execution)|praw_capture_v31' | grep -v grep > "$OUT/final_processes.txt" || true
  redis-cli --raw HGETALL state:position:mme > "$OUT/final_local_position.txt" 2>/dev/null || true
  if [ -d "run/raw_capture_v31/$(TZ=Asia/Kolkata date +%Y%m%d)" ]; then
    find "run/raw_capture_v31/$(TZ=Asia/Kolkata date +%Y%m%d)" -maxdepth 1 -type f -print0 | sort -z | xargs -0 -r sha256sum > "$OUT/raw_manifest/friday_raw_sha256.txt" 2>/dev/null || true
    find "run/raw_capture_v31/$(TZ=Asia/Kolkata date +%Y%m%d)" -maxdepth 1 -type f -printf '%p\t%s bytes\n' | sort > "$OUT/raw_manifest/friday_raw_files.txt" 2>/dev/null || true
  fi
  sha256sum "$SELF" "$RUNNER" "$GUARD" "$BROKER_GATE" "$LEGACY_SUPERVISOR" "$STRATEGY" "$EXECUTION" "$MANAGER" "$RESOLVER" > "$OUT/source_sha256.txt" 2>/dev/null || true
  tar -czf "$ARCHIVE" -C run/proofs "$TAG" 2>/dev/null || true
  sha256sum "$ARCHIVE" > "${ARCHIVE}.sha256" 2>/dev/null || true
  echo "EVIDENCE_ROOT=$OUT"
  echo "BUNDLE=$ARCHIVE"
  echo "SHA=${ARCHIVE}.sha256"
  exit "$rc"
}
trap seal_evidence EXIT INT TERM

block(){ FINAL_REASON="$1"; echo "STOP_$1"; exit 1; }

load_and_verify_manifest(){
  [ -f "$MANIFEST" ] && [ -f "$MANIFEST_SHA" ] || block "SEALED_HASH_MANIFEST_MISSING"
  (cd "$(dirname "$MANIFEST")" && sha256sum -c "$(basename "$MANIFEST_SHA")") || block "HASH_MANIFEST_SHA_INVALID"
  # shellcheck disable=SC1090
  source "$MANIFEST"
  [ "${FRIDAY_RUNNER_SHA:-}" = "$EXPECTED_RUNNER_SHA" ] || block "MANIFEST_RUNNER_SHA_UNEXPECTED"
  [ "${FRIDAY_BROKER_GATE_SHA:-}" = "$EXPECTED_BROKER_GATE_SHA" ] || block "MANIFEST_BROKER_GATE_SHA_UNEXPECTED"
  [ "${FRIDAY_LEGACY_SUPERVISOR_SHA:-}" = "$EXPECTED_LEGACY_SUPERVISOR_SHA" ] || block "MANIFEST_LEGACY_SUPERVISOR_SHA_UNEXPECTED"
  [ "$(sha_file "$SELF")" = "${FRIDAY_SUPERVISOR_SUCCESSOR_SHA:-}" ] || block "SUPERVISOR_SUCCESSOR_HASH_DRIFT"
  [ "$(sha_file "$RUNNER")" = "${FRIDAY_RUNNER_SHA:-}" ] || block "RUNNER_HASH_DRIFT"
  [ "$(sha_file "$GUARD")" = "${FRIDAY_GUARD_SHA:-}" ] || block "GUARD_HASH_DRIFT"
  [ "$(sha_file "$BROKER_GATE")" = "${FRIDAY_BROKER_GATE_SHA:-}" ] || block "BROKER_GATE_HASH_DRIFT"
  [ "$(sha_file "$LEGACY_SUPERVISOR")" = "${FRIDAY_LEGACY_SUPERVISOR_SHA:-}" ] || block "LEGACY_SUPERVISOR_HASH_DRIFT"
  [ "$(sha_file "$STRATEGY")" = "$EXPECTED_STRATEGY_SHA" ] || block "STRATEGY_HASH_DRIFT"
  [ "$(sha_file "$EXECUTION")" = "$EXPECTED_EXECUTION_SHA" ] || block "EXECUTION_HASH_DRIFT"
  [ "$(sha_file "$MANAGER")" = "$EXPECTED_MANAGER_SHA" ] || block "MANAGER_HASH_DRIFT"
  [ "$(sha_file "$RESOLVER")" = "$EXPECTED_RESOLVER_SHA" ] || block "RESOLVER_HASH_DRIFT"
}

broker_gate(){
  local stage="$1"
  PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}" .venv/bin/python "$BROKER_GATE" --stage "$stage" --output "$OUT/broker/${stage}.json" 2>&1 | tee "$OUT/broker/${stage}.txt"
}

safe_topology_and_flat(){
  local stage="$1"
  local svc count
  for svc in feeds features strategy; do
    count="$(count_service "$svc")"; echo "${stage}_${svc}_count=$count"; [ "$count" = "1" ] || block "${stage}_${svc^^}_COUNT_NOT_ONE"
  done
  for svc in risk execution; do
    count="$(count_service "$svc")"; echo "${stage}_${svc}_count=$count"; [ "$count" = "0" ] || block "${stage}_${svc^^}_PRESENT"
  done
  position_is_flat || {
    echo "CRITICAL_LOCAL_POSITION_NOT_FLAT=1"
    echo "DO_NOT_KILL_OR_STOP_SERVICES=1"
    redis-cli --raw HGETALL state:position:mme || true
    block "${stage}_LOCAL_POSITION_NOT_STRICT_FLAT"
  }
  broker_gate "$stage" || {
    echo "CRITICAL_BROKER_POSITION_OR_ACTIVE_ORDER_OR_UNPROVEN=1"
    echo "DO_NOT_KILL_OR_STOP_SERVICES=1"
    block "${stage}_BROKER_NOT_PROVEN_FLAT"
  }
}

snapshot_streams(){
  local stage="$1" key type len last
  : > "$OUT/streams/${stage}.env"
  for key in orders:mme:stream risk:mme:stream execution:mme:stream trades:mme:stream trades:ledger:stream cmd:mme:stream; do
    type="$(redis-cli --raw TYPE "$key" 2>/dev/null || true)"
    len=0; last=0-0
    if [ "$type" = stream ]; then
      len="$(redis-cli --raw XLEN "$key" 2>/dev/null || echo ERR)"
      last="$(redis-cli --raw XREVRANGE "$key" + - COUNT 1 2>/dev/null | head -1 || true)"; last="${last:-0-0}"
    fi
    printf '%s_TYPE=%s\n%s_LEN=%s\n%s_LAST_ID=%s\n' "${key//[:.-]/_}" "$type" "${key//[:.-]/_}" "$len" "${key//[:.-]/_}" "$last" >> "$OUT/streams/${stage}.env"
  done
  cat "$OUT/streams/${stage}.env"
}

entry_window_open(){
  local dow hhmm n
  dow="$(TZ=Asia/Kolkata date +%u)"; hhmm="$(TZ=Asia/Kolkata date +%H%M)"; n=$((10#$hhmm))
  [ "$dow" -ge 1 ] && [ "$dow" -le 5 ] && [ "$n" -ge 915 ] && [ "$n" -lt "$ENTRY_CUTOFF_HHMM" ]
}

classify_child(){
  local label="$1" rc="$2" log="$3" broker_report="$4" out="$5"
  .venv/bin/python - "$label" "$rc" "$log" "$broker_report" "$out" <<'PY'
from __future__ import annotations
import json, sys
from pathlib import Path
label, rc_s, log_s, broker_s, out_s = sys.argv[1:]
rc=int(rc_s); log=Path(log_s).read_text(errors='replace') if Path(log_s).is_file() else ''
def last(keys):
    v=''
    for line in log.splitlines():
        for k in keys:
            if line.startswith(k+'='): v=line.split('=',1)[1].strip()
    return v
classification=last(('FINAL_CLASSIFICATION','CLASSIFICATION'))
root_s=last(('EVIDENCE_ROOT','ROOT','CHILD_PROOF_ROOT','PROOF_ROOT'))
root=Path(root_s) if root_s else None
broker={}
try: broker=json.loads(Path(broker_s).read_text())
except Exception: pass
broker_flat=bool(broker.get('broker_flat')) and int(broker.get('broker_active_order_count',999))==0
payload={}; ledger=[]; ledger_path=''
if root and root.is_dir():
    p=root/'outputs'/'lifecycle_audit.json'
    try:
        payload=json.loads(p.read_text()); ledger=payload.get('ledger',[]) if isinstance(payload,dict) else []; ledger_path=str(p)
    except Exception: pass
def et(row): return str(row.get('event_type') or row.get('record_type') or '').upper()
def num(row,*keys):
    for k in keys:
        try:
            if row.get(k) not in (None,''): return float(row[k])
        except Exception: pass
    return None
entries=[x for x in ledger if isinstance(x,dict) and et(x)=='ENTRY_FILL']
exits=[x for x in ledger if isinstance(x,dict) and et(x)=='EXIT_FILL']
result='FAILED'; allow=0; points=''; reason=''; entry_price=''; exit_price=''; qty=''
upper=classification.upper()+'\n'+log.upper()
if rc==0 and 'PASS_' in upper and 'COMPLETE_STRATEGY_EXIT_FLAT' in upper and len(entries)==1 and len(exits)==1 and broker_flat:
    e,x=entries[-1],exits[-1]
    ep=num(e,'price','avg_fill_price','fill_price'); xp=num(x,'price','avg_fill_price','fill_price'); q=num(x,'quantity','qty_units','filled_units')
    if ep is not None and xp is not None:
        points=xp-ep; entry_price=ep; exit_price=xp
    qty='' if q is None else q
    reason=str(x.get('reason') or x.get('reason_code') or '')
    result='COMPLETED'; allow=1
elif 'STOP_NO_FRESH_REAL_ELIGIBLE_CANDIDATE' in upper and broker_flat:
    result='VETOED'; allow=1
elif ('NO_NATURAL_ENTRY_WITHIN_TIMEOUT_FLAT' in upper or 'NO_NATURAL_ENTRY_TIMEOUT' in upper) and broker_flat:
    result='TIMED_OUT_FLAT'; allow=1
elif ('UNFILLED' in upper or 'NO_FILL' in upper) and broker_flat:
    result='UNFILLED'; allow=1
block='' if allow else 'CHILD_FAILED_OR_EVIDENCE_OR_BROKER_FLAT_NOT_PROVEN'
def q(v): return json.dumps(str(v), ensure_ascii=True)
lines={
 'LABEL':label,'RESULT_TYPE':result,'ALLOW_NEXT_LIFECYCLE':allow,'CHILD_RC':rc,
 'CHILD_CLASSIFICATION':classification,'EVIDENCE_ROOT':root_s,'LEDGER_JSON':ledger_path,
 'BROKER_FLAT':1 if broker_flat else 0,'ENTRY_PRICE':entry_price,'EXIT_PRICE':exit_price,
 'QTY_UNITS':qty,'PNL_POINTS':points,'EXIT_REASON':reason,'BLOCK_REASON':block,
}
Path(out_s).write_text('\n'.join(f'{k}={q(v)}' for k,v in lines.items())+'\n')
print('\n'.join(f'{k}={q(v)}' for k,v in lines.items()))
PY
}

float_add(){ python3 - "$1" "$2" <<'PY'
import sys
print(f"{float(sys.argv[1] or 0)+float(sys.argv[2] or 0):.6f}")
PY
}
float_le(){ python3 - "$1" "$2" <<'PY'
import sys
raise SystemExit(0 if float(sys.argv[1] or 0) <= float(sys.argv[2]) else 1)
PY
}

load_and_verify_manifest
bash "$RUNNER" --r38vxffdp-current-runner-selftest | tee "$OUT/runner_selftest.txt"
R38VXFFDM_EXPECTED_SUPERVISOR_SHA="$(sha_file "$SELF")" bash "$GUARD" --selftest | tee "$OUT/guard_selftest.txt"
bash "$SELF" --selftest | tee "$OUT/supervisor_selftest.txt"

for bad in SCALPX_ENABLE_LIVE SCALPX_REAL_LIVE_ALLOWED SCALPX_ALLOW_REAL_LIVE SCALPX_ALLOW_BROKER_ORDERS SCALPX_BROKER_ORDER_ENABLED MME_ENABLE_LIVE MME_ALLOW_LIVE_ORDER MME_ALLOW_BROKER_ORDERS; do
  case "${!bad:-0}" in 1|true|TRUE|yes|YES|on|ON) block "DANGEROUS_ENV_${bad}_TRUE";; esac
done
[ "$(systemctl show scalpx-mme.service -p ActiveState --value 2>/dev/null || true)" = inactive ] || block "SYSTEMD_MONOLITH_NOT_INACTIVE"
[ "$(systemctl show scalpx-mme.service -p MainPID --value 2>/dev/null || true)" = 0 ] || block "SYSTEMD_MONOLITH_MAINPID_NONZERO"
entry_window_open || block "OUTSIDE_SAFE_ENTRY_WINDOW_0915_TO_${ENTRY_CUTOFF_HHMM}"
safe_topology_and_flat INITIAL
snapshot_streams INITIAL

printf 'cycle,result,child_rc,family,side,symbol,entry_price,exit_price,pnl_points,exit_reason,evidence_root\n' > "$OUT/lifecycle_summary.csv"
: > "$OUT/lifecycle_summary.ndjson"

for cycle in $(seq 1 "$MAX_LIFECYCLES"); do
  if ! entry_window_open; then FINAL_REASON="ENTRY_CUTOFF_REACHED"; break; fi
  if [ "$CONSECUTIVE_FULL_STOPS" -ge "$MAX_CONSECUTIVE_FULL_STOP_LOSSES" ]; then FINAL_REASON="TWO_FULL_HARD_STOP_LOSSES"; break; fi
  if float_le "$CUMULATIVE_POINTS" "$MAX_CUMULATIVE_LOSS_POINTS"; then FINAL_REASON="CUMULATIVE_MINUS_8_POINTS"; break; fi
  safe_topology_and_flat "CYCLE_${cycle}_PRE"
  snapshot_streams "CYCLE_${cycle}_PRE"
  AUTH_ID="${R38VXFFDS_SESSION_AUTHORIZATION}-C$(printf '%02d' "$cycle")-$(date +%s%N)"
  GUARD_OUT="$OUT/guard"
  R38VXFFDM_ENABLE_MARKET_SESSION_GUARD=1 \
  R38VXFFDM_EXPECTED_SUPERVISOR_SHA="$(sha_file "$SELF")" \
  R38VXFFDM_OUT="$GUARD_OUT" \
    bash "$GUARD" --check "$cycle" 1 1 1 1 0 "$AUTH_ID" "$CONSECUTIVE_FULL_STOPS" "$CUMULATIVE_POINTS" | tee "$OUT/logs/cycle_${cycle}_guard.txt"

  ATTEMPTED=$((ATTEMPTED+1))
  LOG="$OUT/logs/cycle_${cycle}_runner.log"
  set +e
  env \
    R38VXFFDP_ENABLE_CURRENT_RUNNER_SUCCESSOR=1 \
    SCALPX_ENABLE_LIVE=0 SCALPX_REAL_LIVE_ALLOWED=0 SCALPX_ALLOW_REAL_LIVE=0 \
    SCALPX_ALLOW_BROKER_ORDERS=0 SCALPX_BROKER_ORDER_ENABLED=0 \
    MME_ENABLE_LIVE=0 MME_ALLOW_LIVE_ORDER=0 MME_ALLOW_BROKER_ORDERS=0 \
    bash "$RUNNER" 2>&1 | tee "$LOG"
  CHILD_RC=${PIPESTATUS[0]}
  set -e

  if ! position_is_flat; then
    echo "CRITICAL_LOCAL_POSITION_OPEN_AFTER_CHILD=1"; echo "DO_NOT_KILL_OR_STOP_SERVICES=1"; FINAL_REASON="LOCAL_NONFLAT_AFTER_CHILD"; exit 1
  fi
  broker_gate "cycle_${cycle}_post" || {
    echo "CRITICAL_BROKER_NONFLAT_OR_ACTIVE_ORDER_AFTER_CHILD=1"; echo "DO_NOT_KILL_OR_STOP_SERVICES=1"; FINAL_REASON="BROKER_NONFLAT_AFTER_CHILD"; exit 1
  }
  RESULT_FILE="$OUT/results/cycle_${cycle}.env"
  classify_child "CYCLE_${cycle}" "$CHILD_RC" "$LOG" "$OUT/broker/cycle_${cycle}_post.json" "$RESULT_FILE"
  # shellcheck disable=SC1090
  source "$RESULT_FILE"
  FAMILY=""; SIDE=""; SYMBOL=""
  if [ -n "${EVIDENCE_ROOT:-}" ] && [ -f "$EVIDENCE_ROOT/SUMMARY.txt" ]; then
    FAMILY="$(awk -F= '$1=="FAMILY"{print $2;exit}' "$EVIDENCE_ROOT/SUMMARY.txt")"
    SIDE="$(awk -F= '$1=="SIDE"{print $2;exit}' "$EVIDENCE_ROOT/SUMMARY.txt")"
    SYMBOL="$(awk -F= '$1=="SYMBOL"{print $2;exit}' "$EVIDENCE_ROOT/SUMMARY.txt")"
  fi
  python3 - "$OUT/lifecycle_summary.csv" "$OUT/lifecycle_summary.ndjson" "$cycle" "$RESULT_TYPE" "$CHILD_RC" "$FAMILY" "$SIDE" "$SYMBOL" "${ENTRY_PRICE:-}" "${EXIT_PRICE:-}" "${PNL_POINTS:-}" "${EXIT_REASON:-}" "${EVIDENCE_ROOT:-}" <<'PY'
import csv,json,sys
csvp,jsonp,*v=sys.argv[1:]
with open(csvp,'a',newline='') as f: csv.writer(f).writerow(v)
keys=['cycle','result','child_rc','family','side','symbol','entry_price','exit_price','pnl_points','exit_reason','evidence_root']
with open(jsonp,'a') as f: f.write(json.dumps(dict(zip(keys,v)),sort_keys=True)+'\n')
PY
  case "$RESULT_TYPE" in
    COMPLETED)
      COMPLETED=$((COMPLETED+1)); CUMULATIVE_POINTS="$(float_add "$CUMULATIVE_POINTS" "${PNL_POINTS:-0}")"
      if [ "${EXIT_REASON:-}" = "hard_stop_points" ]; then CONSECUTIVE_FULL_STOPS=$((CONSECUTIVE_FULL_STOPS+1)); else CONSECUTIVE_FULL_STOPS=0; fi
      ;;
    UNFILLED) UNFILLED=$((UNFILLED+1));;
    VETOED) VETOED=$((VETOED+1));;
    TIMED_OUT_FLAT) TIMED_OUT_FLAT=$((TIMED_OUT_FLAT+1));;
    *) FAILED=$((FAILED+1)); FINAL_REASON="CHILD_FAILED"; exit 1;;
  esac
  [ "${ALLOW_NEXT_LIFECYCLE:-0}" = 1 ] || { FAILED=$((FAILED+1)); FINAL_REASON="ADAPTER_BLOCKED_NEXT"; exit 1; }
  snapshot_streams "CYCLE_${cycle}_POST"
  cp -a "$RESULT_FILE" "$OUT/children/cycle_${cycle}_result.env"
  sleep 2
done

safe_topology_and_flat FINAL
snapshot_streams FINAL
FINAL_CLASSIFICATION="PASS_FRIDAY_MAX5_CONTROLLED_PAPER_SESSION_COMPLETE_FLAT"
[ "$FINAL_REASON" != UNSET ] || FINAL_REASON="MAX_ATTEMPTS_OR_CUTOFF_REACHED"
echo "FINAL_CLASSIFICATION=$FINAL_CLASSIFICATION"
echo "FINAL_REASON=$FINAL_REASON"
echo "ATTEMPTED=$ATTEMPTED"
echo "COMPLETED=$COMPLETED"
echo "CUMULATIVE_POINTS=$CUMULATIVE_POINTS"
echo "REAL_MONEY_ALLOWED=0"
echo "BROKER_ORDER_ALLOWED=0"
trap - EXIT INT TERM
seal_evidence
