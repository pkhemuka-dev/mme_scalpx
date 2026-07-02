#!/usr/bin/env bash
# R38GC_NEXT_POINTER_PATCH_R38GA: next runner is R38GA, not deprecated R38EN
# R38EO tomorrow preflight only.
# Does NOT start risk, execution, paper, strategy, feeds, or any order path.
# It verifies R38EM-R1 + R38EN safety/readiness before the actual runner is executed.

set +e
cd /home/Lenovo/scalpx/projects/mme_scalpx || exit 1

TAG="LANE-X-R38EO_TOMORROW_PREFLIGHT_NO_START_NO_ARM_NO_ORDER_$(date +%Y%m%d_%H%M%S)"
mkdir -p run/audits run/proofs run/evidence_bundles

LOG="run/audits/${TAG}.stdout"
REPORT="run/audits/${TAG}_report.json"
PSTATUS="run/audits/${TAG}_pstatus_observe_only.json"
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

xlen_safe(){ redis-cli XLEN "$1" 2>/dev/null | awk '{print $1+0}'; }
safety(){ echo "$(xlen_safe orders:mme:stream)/$(xlen_safe risk:mme:stream)/$(xlen_safe execution:mme:stream)/$(xlen_safe trades:ledger:stream)"; }

RUNNER="bin/r38ga_keep_strategy_until_risk_open_one_event.sh"
SRC="app/mme_scalpx/services/strategy.py"

SAFETY_NOW="$(safety)"
FEEDS="$(ps -eo args | grep -Ei 'python.*app\.mme_scalpx\.main.*--service[ =]feeds' | grep -v grep | wc -l | tr -d ' ')"
FEATURES="$(ps -eo args | grep -Ei 'python.*app\.mme_scalpx\.main.*--service[ =]features' | grep -v grep | wc -l | tr -d ' ')"
STRATEGY="$(ps -eo args | grep -Ei 'python.*app\.mme_scalpx\.main.*--service[ =]strategy' | grep -v grep | wc -l | tr -d ' ')"
RISK="$(ps -eo args | grep -Ei 'python.*app\.mme_scalpx\.main.*--service[ =]risk' | grep -v grep | wc -l | tr -d ' ')"
EXEC="$(ps -eo args | grep -Ei 'python.*app\.mme_scalpx\.main.*--service[ =]execution' | grep -v grep | wc -l | tr -d ' ')"

echo "SAFETY_NOW=$SAFETY_NOW"
echo "COUNTS feeds=$FEEDS features=$FEATURES strategy=$STRATEGY risk=$RISK execution=$EXEC"

MARKER_R38EM=0
grep -q "R38EM_R1_PROJECTION_DIAG_AND_SYMBOL_FALLBACK_PATCH" "$SRC" && MARKER_R38EM=1

RUNNER_EXISTS=0
test -s "$RUNNER" && RUNNER_EXISTS=1

RUNNER_SYNTAX_RC=99
if [ "$RUNNER_EXISTS" = "1" ]; then
  bash -n "$RUNNER"
  RUNNER_SYNTAX_RC="$?"
fi

COMPILE_RC=99
PYTHONPATH="$PWD:${PYTHONPATH:-}" python3 -m py_compile "$SRC"
COMPILE_RC="$?"

FORBIDDEN_RUNNER_MATCHES="$(grep -nE 'redis-cli[^\n]*(DEL|FLUSHDB|FLUSHALL|XDEL|XTRIM)|\\bpauto\\b|SCALPX_ENABLE_LIVE=1|MME_ENABLE_LIVE=1|SCALPX_ALLOW_BROKER_ORDERS=1|MME_ALLOW_BROKER_ORDERS=1' "$RUNNER" 2>/dev/null || true)"

REQUIRED_RUNNER_MATCHES="$(grep -nE 'SCALPX_CONTROLLED_PAPER_MAX_EVENTS=1|SCALPX_CONTROLLED_PAPER_STOP_AFTER_ONE=1|SCALPX_CONTROLLED_PAPER_MAX_LOTS=1|SCALPX_CONTROLLED_PAPER_SCOPE_ACK|SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME=1|SCALPX_FLAT_POSITION_VERIFIED=1|restore_fail_closed' "$RUNNER" 2>/dev/null || true)"

PYTHONPATH="$PWD:${PYTHONPATH:-}" ./bin/pstatus > "$PSTATUS" 2>&1 || true

python3 - "$REPORT" "$PSTATUS" "$SAFETY_NOW" "$FEEDS" "$FEATURES" "$STRATEGY" "$RISK" "$EXEC" "$MARKER_R38EM" "$RUNNER_EXISTS" "$RUNNER_SYNTAX_RC" "$COMPILE_RC" "$FORBIDDEN_RUNNER_MATCHES" "$REQUIRED_RUNNER_MATCHES" <<'PY'
import json, sys, pathlib, datetime

report_path = pathlib.Path(sys.argv[1])
pstatus_path = pathlib.Path(sys.argv[2])

safety = sys.argv[3]
feeds = int(sys.argv[4])
features = int(sys.argv[5])
strategy = int(sys.argv[6])
risk = int(sys.argv[7])
execution = int(sys.argv[8])
marker_r38em = int(sys.argv[9])
runner_exists = int(sys.argv[10])
runner_syntax_rc = int(sys.argv[11])
compile_rc = int(sys.argv[12])
forbidden = sys.argv[13]
required = sys.argv[14]

try:
    pstatus = json.loads(pstatus_path.read_text())
except Exception:
    pstatus = {}

verdict = pstatus.get("paper_runtime_verdict", {})
psafety = pstatus.get("safety", {})

checks = {
    "safety_streams_zero": safety == "0/0/0/0",
    "risk_execution_not_running": risk == 0 and execution == 0,
    "observe_stack_present": feeds >= 1 and features >= 1 and strategy >= 1,
    "r38em_r1_marker_present": marker_r38em == 1,
    "runner_exists": runner_exists == 1,
    "runner_syntax_ok": runner_syntax_rc == 0,
    "strategy_compile_ok": compile_rc == 0,
    "runner_no_forbidden_ops": forbidden.strip() == "",
    "runner_has_required_guards": all(x in required for x in [
        "SCALPX_CONTROLLED_PAPER_MAX_EVENTS=1",
        "SCALPX_CONTROLLED_PAPER_STOP_AFTER_ONE=1",
        "SCALPX_CONTROLLED_PAPER_MAX_LOTS=1",
        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME=1",
        "SCALPX_FLAT_POSITION_VERIFIED=1",
        "restore_fail_closed",
    ]),
    "pstatus_observe_fail_closed": verdict.get("paper_route_allowed") is False,
    "pstatus_no_orders_risk_execution": psafety.get("orders_risk_execution") in {"0/0/0", "0/0/0/0", None},
}

hard_ok = (
    checks["safety_streams_zero"]
    and checks["risk_execution_not_running"]
    and checks["r38em_r1_marker_present"]
    and checks["runner_exists"]
    and checks["runner_syntax_ok"]
    and checks["strategy_compile_ok"]
    and checks["runner_no_forbidden_ops"]
    and checks["runner_has_required_guards"]
    and checks["pstatus_observe_fail_closed"]
)

classification = (
    "PASS_R38EO_PREFLIGHT_READY_TO_RUN_R38EN_WHEN_MARKET_LIVE_NO_START_NO_ARM_NO_ORDER"
    if hard_ok and checks["observe_stack_present"]
    else "REVIEW_R38EO_PREFLIGHT_HARD_GUARDS_OK_BUT_OBSERVE_STACK_NOT_READY_NO_START_NO_ARM_NO_ORDER"
    if hard_ok
    else "FAIL_R38EO_PREFLIGHT_GUARD_FAILED_NO_START_NO_ARM_NO_ORDER"
)

report = {
    "classification": classification,
    "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "checks": checks,
    "process_counts": {
        "feeds": feeds,
        "features": features,
        "strategy": strategy,
        "risk": risk,
        "execution": execution,
    },
    "safety_streams": safety,
    "runner_syntax_rc": runner_syntax_rc,
    "strategy_compile_rc": compile_rc,
    "forbidden_runner_matches": forbidden,
    "required_runner_matches_head": required[:4000],
    "pstatus_path": str(pstatus_path),
    "next_command_if_pass": "bash bin/r38ga_keep_strategy_until_risk_open_one_event.sh",
    "runtime_started": False,
    "paper_armed": False,
    "paper_started": False,
    "risk_started": False,
    "execution_started": False,
    "order_attempted": False,
    "redis_delete_attempted": False,
    "lock_delete_attempted": False,
}
report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
print(json.dumps(report, indent=2, sort_keys=True))
raise SystemExit(0 if hard_ok else 2)
PY

RC="$?"
echo "PREFLIGHT_RC=$RC"

if [ "$RC" = "0" ]; then
  CLASS="PASS_R38EO_TOMORROW_PREFLIGHT_EXECUTED_NO_START_NO_ARM_NO_ORDER"
else
  CLASS="REVIEW_R38EO_TOMORROW_PREFLIGHT_NEEDS_FIX_NO_START_NO_ARM_NO_ORDER"
fi

python3 - "$PROOF" "$TAG" "$CLASS" "$REPORT" "$RC" "$SAFETY_NOW" "$RISK" "$EXEC" <<'PY'
import json, sys, datetime, pathlib
proof={
  "classification":sys.argv[3],
  "tag":sys.argv[2],
  "created_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
  "report":sys.argv[4],
  "preflight_rc":int(sys.argv[5]),
  "safety_after":sys.argv[6],
  "risk_process_count_after":int(sys.argv[7]),
  "execution_process_count_after":int(sys.argv[8]),
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

tar -czf "$ARCHIVE" "$LOG" "$REPORT" "$PROOF" "$PSTATUS" 2>/dev/null || true
sha256sum "$ARCHIVE" > "${ARCHIVE}.sha256" 2>/dev/null || true

echo "REPORT=$REPORT"
echo "ARCHIVE=$ARCHIVE"
cat "${ARCHIVE}.sha256" 2>/dev/null || true
echo "R38EO_PREFLIGHT_DONE_NO_START_NO_ARM_NO_ORDER"
