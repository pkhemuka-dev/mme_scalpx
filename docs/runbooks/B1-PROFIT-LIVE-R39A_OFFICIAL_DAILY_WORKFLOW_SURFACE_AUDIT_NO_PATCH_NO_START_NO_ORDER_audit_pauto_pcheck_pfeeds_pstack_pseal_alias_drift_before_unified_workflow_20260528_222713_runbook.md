# B1-PROFIT-LIVE-R39A_OFFICIAL_DAILY_WORKFLOW_SURFACE_AUDIT_NO_PATCH_NO_START_NO_ORDER

Classification: **PASS_R39A_WORKFLOW_SURFACE_AUDIT_WRITTEN_NO_PATCH_NO_ORDER**

## Safety
- orders=0
- risk_stream=0
- execution_stream=0
- risk_pids=0
- execution_pids=0

## Alias/function identity

### pauto_start
pauto_start is a function
pauto_start () 
{ 
    cd /home/Lenovo/scalpx/projects/mme_scalpx || return 1;
    TS="$(date +%Y%m%d_%H%M%S)";
    OUTDIR="run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_${TS}";
    mkdir -p "$OUTDIR";
    echo "===== PAUTO START / OBSERVE-ONLY CAPTURE SUPERVISOR =====";
    date -Is;
    echo "outdir=$OUTDIR";
    ORD="$(redis-cli XLEN orders:mme:stream 2>/dev/null || echo 999)";
    RISK="$(redis-cli XLEN risk:mme:stream 2>/dev/null || echo 999)";
    EXEC="$(redis-cli XLEN execution:mme:stream 2>/dev/null || echo 999)";
    RP="$( (pgrep -af 'app\.mme_scalpx\.main --service risk' 2>/dev/null || true) | grep -v grep | wc -l | tr -d ' ' )";
    EP="$( (pgrep -af 'app\.mme_scalpx\.main --service execution' 2>/dev/null || true) | grep -v grep | wc -l | tr -d ' ' )";
    echo "safety: orders=$ORD risk=$RISK execution=$EXEC risk_pids=$RP execution_pids=$EP";
    if [ "$ORD" != "0" ] || [ "$RISK" != "0" ] || [ "$EXEC" != "0" ] || [ "$RP" != "0" ] || [ "$EP" != "0" ]; then
        echo "BLOCKED: safety not clean. Supervisor not started.";
        return 2;
    fi;
    nohup .venv/bin/python bin/b1_profit_live_capture_supervisor.py --outdir "$OUTDIR" --action-mode apply --interval-sec 15 --stale-after-ms 30000 > "$OUTDIR/supervisor.log" 2>&1 & echo $! > "$OUTDIR/supervisor.pid";
    echo "pid=$(cat "$OUTDIR/supervisor.pid")";
    echo "Run: pauto_status"
}

### pauto_status
pauto_status is a function
pauto_status () 
{ 
    cd /home/Lenovo/scalpx/projects/mme_scalpx || return 1;
    LATEST="$(ls -1dt run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_* 2>/dev/null | head -1 || true)";
    echo "latest=${LATEST:-NONE}";
    if [ -z "${LATEST:-}" ]; then
        return 0;
    fi;
    if [ -f "$LATEST/supervisor.pid" ]; then
        PID="$(cat "$LATEST/supervisor.pid")";
        if kill -0 "$PID" 2> /dev/null; then
            echo "status=RUNNING pid=$PID";
        else
            echo "status=NOT_RUNNING pid=$PID";
        fi;
    fi;
    echo;
    echo "state:";
    cat "$LATEST/supervisor_state.json" 2> /dev/null || echo "NO_STATE_YET";
    echo;
    echo "files:";
    ls -lh "$LATEST" 2> /dev/null || true;
    echo;
    echo "log_tail:";
    tail -40 "$LATEST/supervisor.log" 2> /dev/null || true
}

### pauto_stop
pauto_stop is a function
pauto_stop () 
{ 
    cd /home/Lenovo/scalpx/projects/mme_scalpx || return 1;
    LATEST="$(ls -1dt run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_* 2>/dev/null | head -1 || true)";
    echo "latest=${LATEST:-NONE}";
    if [ -z "${LATEST:-}" ] || [ ! -f "$LATEST/supervisor.pid" ]; then
        echo "NO_SUPERVISOR_PID";
        return 0;
    fi;
    PID="$(cat "$LATEST/supervisor.pid")";
    echo "stopping_supervisor_pid=$PID";
    kill -TERM "$PID" 2> /dev/null || true;
    sleep 5;
    pauto_status
}

### pcheck
pcheck is a function
pcheck () 
{ 
    _pcheck_core_before_r37m "$@";
    _pcheck_r37m_status
}

### pcheck5min
pcheck5min is a function
pcheck5min () 
{ 
    pcheck "$@"
}

### pfeeds
pfeeds is a function
pfeeds () 
{ 
    local PROJECT="$(_pfeeds_project_root)";
    local PYBIN="$(_pfeeds_pybin)";
    local TS LOG PIDFILE PID;
    local FORCE="${1:-}";
    cd "$PROJECT" || return 1;
    mkdir -p run/live_capture run/proofs;
    PIDFILE="run/live_capture/pfeeds.pid";
    TS="$(date +%Y%m%d_%H%M%S)";
    LOG="run/live_capture/pfeeds_live_raw_capture_${TS}.log";
    echo "===== PFEEDS COMPREHENSIVE BACKGROUND START =====";
    echo "project=$PROJECT";
    echo "log=$LOG";
    echo "mode=${FORCE:-normal}";
    _pfeeds_load_env;
    echo;
    echo "===== PREFLIGHT: ZERODHA SHARED TOKEN GUARD =====";
    "$PYBIN" "$PROJECT/bin/ensure_zerodha_shared_token.py" || { 
        echo "status=FAILED";
        echo "remark=Zerodha shared token guard failed; pfeeds not started.";
        return 1
    };
    echo;
    echo "===== PREFLIGHT: REDIS =====";
    if ! _pfeeds_redis_ping; then
        echo "status=FAILED";
        echo "remark=Redis ping failed; pfeeds not started.";
        return 1;
    fi;
    echo;
    echo "===== PREFLIGHT: INSTRUMENT MASTER =====";
    if ! _pfeeds_refresh_instruments_if_needed; then
        echo "status=FAILED";
        echo "remark=Instrument master refresh/check failed; pfeeds not started.";
        return 1;
    fi;
    echo;
    echo "===== PREFLIGHT: EXISTING MME/FEEDS PROCESS =====";
    if [ "$FORCE" = "--force-all" ] || [ "$FORCE" = "force-all" ]; then
        echo "force_all=true";
        echo "remark=stopping all app.mme_scalpx.main processes before feed-only restart";
        for pid in $(pgrep -f 'app.mme_scalpx.main' || true);
        do
            echo "stopping mme main pid=$pid";
            kill "$pid" || true;
        done;
        sleep 5;
        for pid in $(pgrep -f 'app.mme_scalpx.main' || true);
        do
            echo "mme main pid still alive=$pid; sending KILL";
            kill -9 "$pid" || true;
        done;
        sleep 2;
        if ps -ef | grep --color=auto -E 'app.mme_scalpx.main' | grep --color=auto -v grep > /dev/null 2>&1; then
            echo "status=FAILED";
            echo "remark=some app.mme_scalpx.main process still alive; refusing pfeeds start";
            ps -ef | grep --color=auto -E 'app.mme_scalpx.main' | grep --color=auto -v grep || true;
            return 1;
        fi;
    else
        if [ "$FORCE" = "--force" ] || [ "$FORCE" = "force" ]; then
            _pfeeds_stop_feeds_only || return 1;
        else
            if [ -f "$PIDFILE" ]; then
                local OLD_PID;
                OLD_PID="$(cat "$PIDFILE" 2>/dev/null || true)";
                if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2> /dev/null; then
                    echo "status=ALREADY_RUNNING";
                    echo "pid=$OLD_PID";
                    echo "remark=pfeeds already running. Use pfeedcheck or pfeeds --force.";
                    return 0;
                fi;
            fi;
            if ps -ef | grep --color=auto -E 'app.mme_scalpx.main --service feeds' | grep --color=auto -v grep > /dev/null 2>&1; then
                echo "status=FEEDS_PROCESS_ALREADY_EXISTS";
                ps -ef | grep --color=auto -E 'app.mme_scalpx.main --service feeds' | grep --color=auto -v grep || true;
                echo "remark=Use: pfeeds --force to stop old feeds process and start clean.";
                return 1;
            fi;
        fi;
    fi;
    echo;
    echo "===== PREFLIGHT: CLEAR FEEDS LOCK ONLY =====";
    _pfeeds_clear_feeds_lock_only || return 1;
    rm -f "$PIDFILE";
    echo;
    echo "===== STARTING FEEDS IN BACKGROUND =====";
    nohup "$PYBIN" -m app.mme_scalpx.main --service feeds --bootstrap-provider app.mme_scalpx.integrations.bootstrap_provider:provide --skip-group-bootstrap > "$LOG" 2>&1 & PID=$!;
    echo "$PID" > "$PIDFILE";
    sleep 10;
    echo;
    echo "===== STARTUP STRICT HEALTH CHECK =====";
    if ! kill -0 "$PID" 2> /dev/null; then
        echo "status=FAILED";
        echo "pid=$PID";
        echo "remark=pfeeds exited during startup.";
        echo "log=$LOG";
        tail -120 "$LOG" 2> /dev/null || true;
        return 1;
    fi;
    "$PYBIN" - "$PID" "$LOG" <<'PY'
import sys, time
from app.mme_scalpx.core import names
from app.mme_scalpx.core.redisx import get_redis_client, ping_redis

pid = sys.argv[1]
log = sys.argv[2]
r = get_redis_client()

ok_ping = ping_redis(client=r)
lock_owner = r.get(names.KEY_LOCK_FEEDS)
lock_ttl = r.pttl(names.KEY_LOCK_FEEDS)

streams = [
    ("fut_zerodha", names.STREAM_TICKS_MME_FUT_ZERODHA),
    ("fut_dhan", names.STREAM_TICKS_MME_FUT_DHAN),
    ("opt_selected_zerodha", names.STREAM_TICKS_MME_OPT_SELECTED_ZERODHA),
    ("opt_selected_dhan", names.STREAM_TICKS_MME_OPT_SELECTED_DHAN),

### pfeedcheck
pfeedcheck is a function
pfeedcheck () 
{ 
    local PROJECT="$(_pfeeds_project_root)";
    local PYBIN="$(_pfeeds_pybin)";
    local PIDFILE="$PROJECT/run/live_capture/pfeeds.pid";
    local PID="";
    local ALIVE="False";
    cd "$PROJECT" || return 1;
    echo "===== PFEEDCHECK STRICT =====";
    date -Is;
    if [ -f "$PIDFILE" ]; then
        PID="$(cat "$PIDFILE" 2>/dev/null || true)";
    fi;
    echo;
    echo "===== PROCESS STATUS =====";
    if [ -n "$PID" ] && kill -0 "$PID" 2> /dev/null; then
        ALIVE="True";
        echo "process_alive=True";
        ps -o pid,ppid,stat,pcpu,pmem,etime,cmd -p "$PID" || true;
    else
        echo "process_alive=False";
        echo "pidfile_pid=${PID:-missing}";
        ps -ef | grep --color=auto -E 'app.mme_scalpx.main --service feeds' | grep --color=auto -v grep || true;
    fi;
    echo;
    echo "===== LATEST LOG =====";
    local LATEST_LOG;
    LATEST_LOG="$(ls -1t run/live_capture/pfeeds_live_raw_capture_*.log 2>/dev/null | head -1 || true)";
    if [ -n "$LATEST_LOG" ]; then
        ls -lh "$LATEST_LOG";
        echo "last_log_lines:";
        tail -40 "$LATEST_LOG" || true;
    else
        echo "no pfeeds live capture log found";
    fi;
    echo;
    echo "===== REDIS STREAM RECORDING CHECK =====";
    "$PYBIN" - "$ALIVE" "$PID" <<'PY'
import sys, time
from app.mme_scalpx.core import names
from app.mme_scalpx.core.redisx import get_redis_client, ping_redis

process_alive = sys.argv[1] == "True"
pid = sys.argv[2] if len(sys.argv) > 2 else ""

r = get_redis_client()
ok_ping = ping_redis(client=r)
lock_owner = r.get(names.KEY_LOCK_FEEDS)
lock_ttl = r.pttl(names.KEY_LOCK_FEEDS)

print("redis_ping =", ok_ping)
print("lock_feeds_owner =", lock_owner)
print("lock_feeds_ttl_ms =", lock_ttl)
print()

streams = [
    ("fut_zerodha", names.STREAM_TICKS_MME_FUT_ZERODHA),
    ("fut_dhan", names.STREAM_TICKS_MME_FUT_DHAN),
    ("opt_selected_zerodha", names.STREAM_TICKS_MME_OPT_SELECTED_ZERODHA),
    ("opt_selected_dhan", names.STREAM_TICKS_MME_OPT_SELECTED_DHAN),
    ("opt_context_dhan", names.STREAM_TICKS_MME_OPT_CONTEXT_DHAN),
    ("health", names.STREAM_SYSTEM_HEALTH),
    ("errors", names.STREAM_SYSTEM_ERRORS),
]

before = {label: int(r.xlen(stream)) for label, stream in streams}
time.sleep(5)
after = {label: int(r.xlen(stream)) for label, stream in streams}
growth = {label: after[label] - before[label] for label, _ in streams}

for label, stream in streams:
    print(f"{label:24s} {stream:42s} xlen={after[label]:<8} growth_5s={growth[label]}")

print()

critical_growth = (
    growth["fut_zerodha"] > 0
    and growth["fut_dhan"] > 0
    and growth["opt_selected_zerodha"] > 0
    and growth["opt_selected_dhan"] > 0
)
# A6-FEED-R4P pfeedcheck strictness refinement:
# Treat short-window option-context stream non-growth as a soft warning when
# durable source hashes and A6 compatibility hashes are present. This keeps
# hard safety gates unchanged: process, Redis, critical streams, errors,
# and lock ownership still decide health.
source_keys = [
    "state:provider:runtime",
    "state:snapshot:mme:fut:active",
    "state:snapshot:mme:opt:selected:active",
    "state:context:mme:dhan",
]
compat_keys = [
    "state:provider_runtime:mme",
    "state:feed:futures:active",
    "state:feed:selected_option:active",
    "state:feed:option_context:active",
]
try:
    source_compat_ok = all(str(r.type(k)) == "hash" for k in source_keys) and all(
        str(r.type(k)) == "hash" and r.hget(k, "compatibility_published_by") == "A6-FEED-R4K"
        for k in compat_keys
    )
except Exception:
    source_compat_ok = False

context_ok = growth["opt_context_dhan"] >= 0 or source_compat_ok
error_stable = growth["errors"] <= 0
lock_owner_ok = bool(lock_owner) and (pid in str(lock_owner) if pid else True)

if source_compat_ok and growth["opt_context_dhan"] < 0:
    print("context_soft_pass=A6-FEED-R4P_SOURCE_AND_COMPAT_HASHES_PRESENT")

if process_alive and ok_ping and critical_growth and context_ok and error_stable and lock_owner_ok:
    print("status=HEALTHY_RECORDING")
    print("remark=live raw market data is being recorded cleanly into Redis streams.")
elif process_alive and ok_ping and zerodha_critical_growth and (not dhan_critical_growth) and error_stable and lock_owner_ok:
    print("status=DHAN_DEGRADED_ZERODHA_RECORDING")
    print("remark=Zerodha futures/options are recording, but Dhan critical stream growth is incomplete; useful diagnostic capture only.")

### pstack
pstack is a function
pstack () 
{ 
    cd /home/Lenovo/scalpx/projects/mme_scalpx || return 1;
    set -euo pipefail;
    echo "===== PSTACK OBSERVE-ONLY START / FAIL-CLOSED FEED GATE =====";
    echo "services=feeds,features,strategy";
    echo "execution=NOT_STARTED";
    echo "risk=NOT_STARTED";
    echo "stack_mode=observe_only_no_execution";
    echo "settings_runtime_mode=live";
    date -Is;
    unset SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME || true;
    unset SCALPX_CONTROLLED_PAPER_SCOPE_ACK || true;
    unset SCALPX_REAL_LIVE_ALLOWED || true;
    unset SCALPX_ALLOW_REAL_LIVE || true;
    unset SCALPX_ALLOW_BROKER_ORDERS || true;
    unset SCALPX_PAPER_ARMED || true;
    unset SCALPX_ENABLE_PAPER || true;
    unset SCALPX_ENABLE_LIVE || true;
    export SCALPX_OBSERVE_ONLY=1;
    export MME_RUNTIME_MODE=live;
    PYBIN=".venv/bin/python";
    if [ ! -x "$PYBIN" ]; then
        PYBIN="$(command -v python3)";
    fi;
    echo;
    echo "===== 0. PRECHECK: NO RISK / EXECUTION PROCESS =====";
    if ps -ef | grep --color=auto -E 'app.mme_scalpx.main --service (risk|execution)' | grep --color=auto -v grep; then
        echo "status=REFUSED";
        echo "reason=risk_or_execution_process_running";
        return 2;
    fi;
    echo;
    echo "===== 1. START / VERIFY FEEDS =====";
    pfeeds;
    echo;
    echo "===== 2. STRICT FEED GATE =====";
    FEED_GATE_FILE="run/proofs/pstack_feed_gate_$(date +%Y%m%d_%H%M%S).txt";
    set +e;
    pfeedcheck 2>&1 | tee "$FEED_GATE_FILE";
    PFEEDCHECK_RC=${PIPESTATUS[0]};
    set -e;
    echo "pfeedcheck_rc=$PFEEDCHECK_RC" | tee -a "$FEED_GATE_FILE";
    if ! grep --color=auto -q '^status=HEALTHY_RECORDING$' "$FEED_GATE_FILE"; then
        echo;
        echo "status=REFUSED";
        echo "reason=pfeedcheck_not_healthy_recording";
        echo "feed_gate_file=$FEED_GATE_FILE";
        echo "PSTACK_FAIL_CLOSED: features/strategy were NOT started.";
        return 3;
    fi;
    echo;
    echo "===== 3. EXECUTION LOCK GATE =====";
    EXEC_LOCK="$("$PYBIN" - <<'PY'
from app.mme_scalpx.core.redisx import get_redis_client
r = get_redis_client()
v = r.get("lock:execution")
print("" if v is None else v)
PY
)";
    echo "lock_execution=${EXEC_LOCK:-None}";
    if [ -n "${EXEC_LOCK:-}" ]; then
        echo "status=REFUSED";
        echo "reason=lock_execution_present";
        echo "lock_execution=$EXEC_LOCK";
        echo "PSTACK_FAIL_CLOSED: features/strategy were NOT started.";
        return 4;
    fi;
    echo;
    echo "===== 4. CLEAR ONLY STRATEGY STALE LOCK / FEATURE STRATEGY PIDFILES =====";
    "$PYBIN" - <<'PY'
from app.mme_scalpx.core.redisx import get_redis_client
r = get_redis_client()
print("redis_ping =", r.ping())
print("before lock:strategy =", r.get("lock:strategy"), "ttl_ms=", r.pttl("lock:strategy"))
print("deleted lock:strategy =", r.delete("lock:strategy"))
print("after  lock:strategy =", r.get("lock:strategy"), "ttl_ms=", r.pttl("lock:strategy"))
print("lock:feeds =", r.get("lock:feeds"), "ttl_ms=", r.pttl("lock:feeds"))
print("lock:execution =", r.get("lock:execution"), "ttl_ms=", r.pttl("lock:execution"))
print("orders_xlen =", r.xlen("orders:mme:stream"))
PY

    rm -f run/live_capture/pfeatures.pid run/live_capture/pstrategy.pid;
    TS_LOCAL="$(date +%Y%m%d_%H%M%S)";
    FEATURE_LOG="run/live_capture/pfeatures_${TS_LOCAL}.log";
    STRATEGY_LOG="run/live_capture/pstrategy_${TS_LOCAL}.log";
    echo;
    echo "===== 5. START FEATURES =====";
    nohup "$PYBIN" -m app.mme_scalpx.main --service features --skip-group-bootstrap > "$FEATURE_LOG" 2>&1 & FEATURE_PID=$!;
    echo "$FEATURE_PID" > run/live_capture/pfeatures.pid;
    echo "features_pid=$FEATURE_PID";
    echo "features_log=$FEATURE_LOG";
    sleep 8;
    echo;
    echo "===== 6. START STRATEGY =====";
    nohup "$PYBIN" -m app.mme_scalpx.main --service strategy --skip-group-bootstrap > "$STRATEGY_LOG" 2>&1 & STRATEGY_PID=$!;
    echo "$STRATEGY_PID" > run/live_capture/pstrategy.pid;
    echo "strategy_pid=$STRATEGY_PID";
    echo "strategy_log=$STRATEGY_LOG";
    sleep 15;
    echo;
    echo "===== 7. STACK CHECK =====";
    pstackcheck;
    echo;
    echo "===== 8. FINAL ORDER/LOCK SAFETY =====";
    "$PYBIN" - <<'PY'
from app.mme_scalpx.core.redisx import get_redis_client
r = get_redis_client()
print("orders_xlen =", r.xlen("orders:mme:stream"))
print("lock_feeds =", r.get("lock:feeds"))
print("lock_strategy =", r.get("lock:strategy"))
print("lock_execution =", r.get("lock:execution"))
PY

}

### pstackcheck
pstackcheck is a function
pstackcheck () 
{ 
    local PROJECT="$(_pstack_project_root)";
    local PYBIN="$(_pstack_pybin)";
    cd "$PROJECT" || return 1;
    echo "===== PSTACKCHECK =====";
    date -Is;
    echo;
    echo "===== PROCESS STATUS =====";
    for service in feeds features strategy execution risk monitor report;
    do
        echo "--- $service ---";
        ps -ef | grep --color=auto -E "app.mme_scalpx.main --service ${service}" | grep --color=auto -v grep || echo "not running";
    done;
    echo;
    echo "===== REDIS SURFACE CHECK =====";
    "$PYBIN" - <<'PY'
import json
import time
from app.mme_scalpx.core import names
from app.mme_scalpx.core.redisx import get_redis_client, ping_redis

r = get_redis_client()
print("redis_ping =", ping_redis(client=r))
print()

stream_attrs = [
    "STREAM_TICKS_MME_FUT_ZERODHA",
    "STREAM_TICKS_MME_FUT_DHAN",
    "STREAM_TICKS_MME_OPT_SELECTED_ZERODHA",
    "STREAM_TICKS_MME_OPT_SELECTED_DHAN",
    "STREAM_TICKS_MME_OPT_CONTEXT_DHAN",
    "STREAM_FEATURES_MME",
    "STREAM_DECISIONS_MME",
    "STREAM_SYSTEM_HEALTH",
    "STREAM_SYSTEM_ERRORS",
]

streams = []
for attr in stream_attrs:
    stream = getattr(names, attr, None)
    if stream:
        streams.append((attr, stream))

before = {}
for attr, stream in streams:
    try:
        before[(attr, stream)] = int(r.xlen(stream))
    except Exception:
        before[(attr, stream)] = -1

time.sleep(5)

after = {}
for attr, stream in streams:
    try:
        after[(attr, stream)] = int(r.xlen(stream))
    except Exception:
        after[(attr, stream)] = -1

for attr, stream in streams:
    b = before[(attr, stream)]
    a = after[(attr, stream)]
    growth = a - b if a >= 0 and b >= 0 else -1
    print(f"{attr:38s} {stream:45s} xlen={a:<8} growth_5s={growth}")

print()
print("===== LATEST FEATURE / DECISION SAMPLE KEYS =====")
for attr in ["STREAM_FEATURES_MME", "STREAM_DECISIONS_MME", "STREAM_SYSTEM_ERRORS"]:
    stream = getattr(names, attr, None)
    if not stream:
        continue
    rows = r.xrevrange(stream, "+", "-", count=1)
    print()
    print(attr, "=", stream)
    if not rows:
        print("  no rows")
        continue
    msg_id, fields = rows[0]
    print("  latest_id =", msg_id)
    print("  field_keys =", sorted(fields.keys())[:40])

    # Show safe selected high-level fields only
    for k in [
        "service_name", "instance_id", "status", "event", "event_type",
        "action", "decision_action", "runtime_mode", "strategy_id",
        "reason", "detail", "ts_event_ns", "ts_ns"
    ]:
        if k in fields:
            print(f"  {k}={fields.get(k)}")

print()
print("===== LOCKS =====")
for attr in [
    "KEY_LOCK_FEEDS",
    "KEY_LOCK_FEATURES",
    "KEY_LOCK_STRATEGY",
    "KEY_LOCK_EXECUTION",
]:
    key = getattr(names, attr, None)
    if not key:
        continue
    print(f"{attr:24s} {key:30s} value={r.get(key)} ttl_ms={r.pttl(key)}")
PY

}

### pseal
pseal is a function
pseal () 
{ 
    cd /home/Lenovo/scalpx/projects/mme_scalpx || return 1;
    BATCH="B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER";
    PURPOSE="detached_market_close_seal_export_no_order";
    TS="$(date +%Y%m%d_%H%M%S)";
    TAG="${BATCH}_${PURPOSE}_${TS}";
    OUTDIR="run/live_capture/${TAG}";
    mkdir -p "$OUTDIR" run/proofs run/audits;
    nohup bash bin/b1_profit_live_detached_pseal.sh "$TAG" full > "$OUTDIR/pseal.log" 2>&1 < /dev/null & PID="$!";
    echo "$PID" > "$OUTDIR/pseal.pid";
    echo "started_pseal_pid=$PID";
    echo "log=$OUTDIR/pseal.log";
    echo "Run: pseal_status"
}

### pseal_status
pseal_status is a function
pseal_status () 
{ 
    cd /home/Lenovo/scalpx/projects/mme_scalpx || return 1;
    LATEST="$(ls -1dt run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_* 2>/dev/null | head -1 || true)";
    echo "latest=${LATEST:-NONE}";
    [ -n "${LATEST:-}" ] || return 0;
    if [ -f "$LATEST/pseal.pid" ]; then
        PID="$(cat "$LATEST/pseal.pid" 2>/dev/null || true)";
        if [ -n "$PID" ] && kill -0 "$PID" 2> /dev/null; then
            echo "status=RUNNING pid=$PID";
        else
            echo "status=NOT_RUNNING pid=${PID:-UNKNOWN}";
        fi;
    fi;
    echo;
    ls -lh "$LATEST" 2> /dev/null || true;
    echo;
    cat run/proofs/"$(basename "$LATEST")".json 2> /dev/null || true;
    echo;
    tail -80 "$LATEST/pseal.log" 2> /dev/null || true
}

## Relevant bin scripts
bin/b1_profit_live_capture_supervisor.py
bin/b1_profit_live_detached_pseal.sh
bin/b1_profit_live_recorder_backtest_handoff_builder.py
bin/pcheck
bin/pfeedcheck
bin/pfeeds
bin/pfeedstop
bin/pstack
bin/pstackcheck

## R37/R38 proof chain latest
run/proofs/B1-PROFIT-LIVE-R38E_PREOPEN_LIVE_OBSERVE_READINESS_RUNBOOK_NO_PATCH_NO_START_NO_ORDER_freeze_tomorrow_observe_only_to_controlled_paper_gate_after_provider_fallback_patch_20260528_222506.json
run/proofs/B1-PROFIT-LIVE-R38D_FIXTURE_BEHAVIOR_VALIDATION_AFTER_PROVIDER_FALLBACK_PATCH_NO_START_NO_ORDER_prove_selected_option_dhan_unavailable_zerodha_fallback_without_runtime_start_20260528_221343.json
run/proofs/B1-PROFIT-LIVE-R38C_STATIC_IMPORT_VALIDATION_AFTER_PROVIDER_FALLBACK_PATCH_NO_START_NO_ORDER_validate_r38b_patch_import_marker_ast_no_danger_no_service_start_20260528_221123.json
run/proofs/B1-PROFIT-LIVE-R38B_PROVIDER_RUNTIME_CLASSIC_ZERODHA_SELECTED_OPTION_FALLBACK_PATCH_NO_ORDER_patch_manual_failover_selected_option_to_zerodha_when_dhan_unavailable_no_start_no_order_20260528_221023.json
run/proofs/B1-PROFIT-LIVE-R37Q-R1_DATA_ADMISSION_AND_PDEV_TARGETING_NO_PATCH_NO_START_NO_ORDER_correct_pseal_admission_inventory_pdev_and_target_provider_fallback_surface_20260528_220400.json
run/proofs/B1A-R39_RETRY_HELPER_EXECUTE_AFTER_R38D_LIFECYCLE_PATCH_APPROVAL_REQUIRED_guarded_helper_execute_verify_observe_only_risk_execution_lifecycle_rows_zero_order_20260517_172400.json
run/proofs/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008.json
run/proofs/B1A-R38C_NAMES_AUTHORITY_AND_LIFECYCLE_PATCH_PLAN_NO_START_plan_names_authority_and_lifecycle_patch_after_missing_risk_execution_stream_constants_no_patch_no_start_20260517_171848.json
run/proofs/B1A-R38B_CORRECT_FALSE_STREAM_SYMBOL_DISCOVERY_NO_PATCH_NO_START_correct_r38a_false_stream_symbol_discovery_and_plan_names_authority_no_patch_no_start_20260517_171743.json

## Live-capture latest
run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260527_153107
run/live_capture/B1-PROFIT-LIVE-R37M_LIVE_SESSION_EMERGENCY_DURABLE_RECORDER_NO_ORDER_start_readonly_redis_stream_recorder_without_restart_no_risk_no_execution_no_order_20260527_092428
run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_smoke_limited_export_no_order_20260526_235353

## Desired official workflow
pauto_start: official start; must start recorder first, then feeds, then features, then strategy observe-only.
pcheck: official single dashboard; must include recorder, feeds, features, strategy, provider, fallback, and safety.
pauto_stop: official stop; must stop observe-only supervisor/recorder safely without touching Redis data.
pseal: official close; must seal/export and create replay handoff.

## Rules for R39B
- Do not create more aliases.
- Do not patch strategy/risk/execution/order paths.
- Do not enable paper/live.
- Keep pauto_start, pcheck, pauto_stop, pseal as the official names.
- Prefer wrapper consolidation over rewriting working internals.
- Preserve R38 provider fallback doctrine.
