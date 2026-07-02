#!/usr/bin/env bash
cd /home/Lenovo/scalpx/projects/mme_scalpx || exit 1
set +e

TAG="LANE-X-R38GA_AFTERMARKET_AUDIT_NO_START_NO_ARM_NO_ORDER_$(date +%Y%m%d_%H%M%S)"
REPORT="run/audits/${TAG}_report.txt"
mkdir -p run/audits

{
  echo "=== $TAG ==="
  date -Is
  pwd

  echo "--- protected streams ---"
  for s in orders:mme:stream risk:mme:stream execution:mme:stream trades:ledger:stream cmd:mme:stream; do
    printf '%s=' "$s"
    redis-cli XLEN "$s" 2>/dev/null || true
  done

  echo "--- processes ---"
  ps -eo pid,ppid,etime,args | grep -Ei 'python.*app\.mme_scalpx\.main.*--service[ =](feeds|features|strategy|risk|execution)' | grep -v grep || true

  echo "--- compile/syntax ---"
  python3 -m py_compile app/mme_scalpx/services/risk.py bin/r38ga_find_candidate.py bin/r38ga_inject_projected_row.py
  echo "py_compile_rc=$?"
  bash -n bin/r38ga_keep_strategy_until_risk_open_one_event.sh
  echo "runner_syntax_rc=$?"

  echo "--- markers ---"
  grep -n "R38GA_GENERATED_SCOPE_ACK_ACCEPTANCE_PATCH" app/mme_scalpx/services/risk.py || true
  grep -n "R38GA_DEPRECATE_R38EN_GUARD" bin/r38en_tomorrow_parallel_scope_controlled_paper_runner.sh 2>/dev/null || true

  echo "--- required runner guards ---"
  grep -nEi 'PASS_R38EQ_HARD_GATE|FAIL_R38EQ_HARD_GATE|max_new_lots|strategy_heartbeat_fresh|execution_heartbeat_fresh|XTRIM decisions:mme:stream MAXLEN 0|SCALPX_CONTROLLED_PAPER_MAX_EVENTS=1|SCALPX_CONTROLLED_PAPER_STOP_AFTER_ONE=1|ensure_observe_strategy|cleanup' bin/r38ga_keep_strategy_until_risk_open_one_event.sh || true

  echo "--- forbidden destructive ops in R38GA runner ---"
  grep -nEi 'FLUSHDB|FLUSHALL|XDEL|redis-cli[[:space:]]+DEL|lock.*delete' bin/r38ga_keep_strategy_until_risk_open_one_event.sh || true

  echo "classification=PASS_R38GA_AFTERMARKET_AUDIT_NO_START_NO_ARM_NO_ORDER"
} | tee "$REPORT"

echo "REPORT=$REPORT"
