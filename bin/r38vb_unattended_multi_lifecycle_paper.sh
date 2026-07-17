#!/usr/bin/env bash
set -Eeuo pipefail

cd /home/Lenovo/scalpx/projects/mme_scalpx || exit 1

BASE_RUNNER="bin/r38vb_natural_one_event_complete_lifecycle.sh"
EXPECTED_BASE_SHA="e4ba50254e85490eaae36db0d3c3b7112abf1741793043d887d0d2a7c264f950"

STRATEGY="app/mme_scalpx/services/strategy.py"
EXECUTION="app/mme_scalpx/services/execution.py"
MANAGER="app/mme_scalpx/services/strategy_family/position_exit_manager.py"
RESOLVER="app/mme_scalpx/services/strategy_family/exact_position_quote_resolver.py"
EXPECTED_STRATEGY_SHA="b6374975d85f7bfe4c44dbe1188caef3fb4fdd316e4323a513b25329a9d5fc52"
EXPECTED_EXECUTION_SHA="94744378b4b7a7ae2d4754a0f1dbf87a06861b0dd8973639b7beece44abcd0a2"
EXPECTED_MANAGER_SHA="ca2742bf5d6b1fd127b7cab7b219ebe1639a626de1c8c288a8e99b0e4e8cf5a0"
EXPECTED_RESOLVER_SHA="4a4365f804321bd7c8ff3ef630224a7c2ea3a8419c7c7bc8866753acdeae26c0"

MAX_LIFECYCLES="${R38VB_MAX_LIFECYCLES:-5}"
ENTRY_CUTOFF_HHMM=1450
MAX_DAILY_PAPER_LOSS="-1000.0"

case "$MAX_LIFECYCLES" in
    1|2|3|4|5)
        ;;
    *)
        echo "STOP_INVALID_MAX_LIFECYCLES=$MAX_LIFECYCLES"
        exit 1
        ;;
esac

TAG="R38VB_UNATTENDED_MULTI_NATURAL_LIFECYCLE_PAPER_$(date +%Y%m%d_%H%M%S)"
OUT="run/proofs/$TAG"
SUMMARY="$OUT/summary.txt"

mkdir -p "$OUT"/{runners,logs,results}

count_service() {
    pgrep -fc       "app\.mme_scalpx\.main --service $1([[:space:]]|$)"       2>/dev/null || true
}

position_field() {
    redis-cli --raw HGET state:position:mme "$1" 2>/dev/null || true
}

position_is_flat() {
    [ "$(position_field has_position)" = "0" ] &&
    [ "$(position_field position_side)" = "FLAT" ] &&
    [ "$(position_field qty_lots)" = "0" ] &&
    [ "$(position_field qty_units)" = "0" ]
}

safe_between_cycles() {
    local stage="$1"

    [ "$(count_service feeds)" = "1" ] || {
        echo "STOP_${stage}_FEEDS_COUNT_NOT_ONE"
        return 1
    }

    [ "$(count_service features)" = "1" ] || {
        echo "STOP_${stage}_FEATURES_COUNT_NOT_ONE"
        return 1
    }

    [ "$(count_service strategy)" = "1" ] || {
        echo "STOP_${stage}_STRATEGY_COUNT_NOT_ONE"
        return 1
    }

    [ "$(count_service risk)" = "0" ] || {
        echo "STOP_${stage}_RISK_PRESENT"
        return 1
    }

    [ "$(count_service execution)" = "0" ] || {
        echo "STOP_${stage}_EXECUTION_PRESENT"
        return 1
    }

    position_is_flat || {
        echo "STOP_${stage}_POSITION_NOT_FLAT"
        return 1
    }
}

daily_loss_reached() {
    python3 - "${1:-0}" "$MAX_DAILY_PAPER_LOSS" <<'PY'
import sys
try:
    pnl = float(sys.argv[1] or 0)
    limit = float(sys.argv[2])
except Exception:
    raise SystemExit(1)
raise SystemExit(0 if pnl <= limit else 1)
PY
}


r38vxff_env_get() {
    local file="$1"
    local key="$2"

    awk -F= -v key="$key" '
        $1 == key {
            sub(/^[^=]*=/, "")
            print
            exit
        }
    ' "$file" 2>/dev/null || true
}

r38vxff_classify_child_lifecycle_result() {
    local label="$1"
    local child_rc="$2"
    local log_file="$3"
    local local_flat_now="$4"
    local output_file="$5"

    python3 - "$label" "$child_rc" "$log_file" "$local_flat_now" "$output_file" <<'PY_TYPED_ADAPTER_R38VXFFDK'
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


label = sys.argv[1]
child_rc = int(sys.argv[2] or "999")
log_path = Path(sys.argv[3])
local_flat_now = sys.argv[4] == "1"
output_path = Path(sys.argv[5])


def read_env(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}

    try:
        lines = path.read_text(errors="replace").splitlines()
    except Exception:
        return data

    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()

    return data


def truth(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "pass", "flat"}


def int_value(value: Any, default: int = 999) -> int:
    try:
        return int(str(value).strip())
    except Exception:
        return default


def find_last_assignment(text: str, keys: tuple[str, ...]) -> str:
    found = ""
    for line in text.splitlines():
        for key in keys:
            prefix = key + "="
            if line.startswith(prefix):
                found = line[len(prefix):].strip()
    return found


def ledger_events(rows: list[dict[str, Any]], event_type: str) -> list[dict[str, Any]]:
    return [row for row in rows if row.get("event_type") == event_type]


log_text = log_path.read_text(errors="replace") if log_path.is_file() else ""

classification = find_last_assignment(log_text, ("FINAL_CLASSIFICATION", "CLASSIFICATION"))
evidence_root_text = find_last_assignment(log_text, ("EVIDENCE_ROOT", "CHILD_PROOF_ROOT", "PROOF_ROOT"))

summary_candidates: list[Path] = []

if evidence_root_text:
    evidence_root = Path(evidence_root_text)
    if evidence_root.is_dir():
        for name in ("summary.env", "summary.txt", "final_summary.env", "result.env"):
            summary_candidates.append(evidence_root / name)

summary_text_path = find_last_assignment(log_text, ("SUMMARY", "CHILD_SUMMARY", "SUMMARY_ENV"))

if summary_text_path:
    summary_candidates.append(Path(summary_text_path))

summary_path = next((path for path in summary_candidates if path.is_file()), None)
summary = read_env(summary_path) if summary_path else {}
summary_read = bool(summary_path)

summary_classification = (
    summary.get("FINAL_CLASSIFICATION")
    or summary.get("CLASSIFICATION")
    or summary.get("classification")
    or ""
)

if summary_classification:
    classification = summary_classification

upper = classification.upper()

ledger_candidates: list[Path] = []

for key in ("LEDGER_JSON", "TRADES_LEDGER_JSON", "TRADE_LEDGER_JSON"):
    value = summary.get(key)
    if value:
        ledger_candidates.append(Path(value))

if evidence_root_text:
    evidence_root = Path(evidence_root_text)
    if evidence_root.is_dir():
        ledger_candidates.extend(sorted(evidence_root.glob("**/*ledger*.json")))

ledger_rows: list[dict[str, Any]] = []
ledger_path = None
ledger_read = False

for candidate in ledger_candidates:
    try:
        payload = json.loads(candidate.read_text())
    except Exception:
        continue

    if isinstance(payload, list):
        ledger_rows = [row for row in payload if isinstance(row, dict)]
        ledger_path = candidate
        ledger_read = True
        break

entry_rows = ledger_events(ledger_rows, "ENTRY_FILL")
exit_rows = ledger_events(ledger_rows, "EXIT_FILL")

active_order_count = int_value(
    summary.get("ACTIVE_ORDER_COUNT")
    or summary.get("broker_active_order_count")
    or summary.get("BROKER_ACTIVE_ORDER_COUNT")
    or summary.get("active_order_count"),
    999,
)

broker_flat = False

if "BROKER_FLAT" in summary:
    broker_flat = truth(summary.get("BROKER_FLAT"))
elif "broker_flat" in summary:
    broker_flat = truth(summary.get("broker_flat"))
else:
    nonflat_count = summary.get("broker_nonflat_position_count")
    active_count = summary.get("broker_active_order_count") or summary.get("ACTIVE_ORDER_COUNT")
    if nonflat_count is not None and active_count is not None:
        broker_flat = int_value(nonflat_count, 999) == 0 and int_value(active_count, 999) == 0

local_flat = local_flat_now

if "LOCAL_FLAT" in summary:
    local_flat = truth(summary.get("LOCAL_FLAT"))
elif "local_flat" in summary:
    local_flat = truth(summary.get("local_flat"))
elif "FINAL_POSITION_FLAT" in summary:
    local_flat = truth(summary.get("FINAL_POSITION_FLAT"))
elif str(summary.get("final_position", "")).upper() == "FLAT":
    local_flat = True

flat_between_cycles = local_flat and broker_flat and active_order_count == 0

exit_reason = ""
pnl_points = ""

if exit_rows:
    exit_row = exit_rows[-1]
    exit_reason = str(exit_row.get("reason") or exit_row.get("reason_code") or "")
    pnl_points = str(exit_row.get("pnl_points") or exit_row.get("pnl") or "")

completed_looking = (
    child_rc == 0
    and "PASS" in upper
    and ("COMPLETE" in upper or "COMPLETED" in upper)
)

timeout_looking = any(
    token in upper
    for token in (
        "TIMEOUT",
        "TIMED_OUT",
        "NO_NATURAL_ENTRY_TIMEOUT",
        "NO_NATURAL_ENTRY_WITHIN_TIMEOUT",
    )
)

unfilled_looking = any(
    token in upper
    for token in (
        "UNFILLED",
        "NO_FILL",
        "NO_ENTRY_FILL",
        "SAFE_NO_CANDIDATE",
        "NO_CANDIDATE",
    )
) and not timeout_looking

vetoed_looking = any(
    token in upper
    for token in (
        "VETO",
        "RISK_BLOCK",
        "RISK_VETO",
        "CANDIDATE_REJECTED",
    )
)

if completed_looking:
    if summary_read and ledger_read and len(entry_rows) >= 1 and len(exit_rows) >= 1 and exit_reason and flat_between_cycles:
        result_type = "COMPLETED"
        completed_delta = 1
        allow_next = True
        block_reason = ""
    else:
        result_type = "FAILED"
        completed_delta = 0
        allow_next = False
        block_reason = "COMPLETED_CLASSIFICATION_WITHOUT_LEDGER_OR_FLAT"

elif unfilled_looking:
    result_type = "UNFILLED"
    completed_delta = 0
    allow_next = flat_between_cycles
    block_reason = "" if flat_between_cycles else "UNFILLED_BUT_NOT_FLAT"

elif vetoed_looking:
    result_type = "VETOED"
    completed_delta = 0
    allow_next = flat_between_cycles
    block_reason = "" if flat_between_cycles else "VETOED_BUT_NOT_FLAT"

elif timeout_looking:
    result_type = "TIMED_OUT_FLAT" if flat_between_cycles else "TIMED_OUT_OPEN"
    completed_delta = 0
    allow_next = flat_between_cycles
    block_reason = "" if flat_between_cycles else "TIMEOUT_WITH_NONFLAT_OR_ACTIVE_ORDER"

else:
    result_type = "FAILED"
    completed_delta = 0
    allow_next = False
    block_reason = "UNKNOWN_OR_FAILED_CHILD_RESULT"

if result_type != "COMPLETED":
    completed_delta = 0

retry_allowed = False

output_path.parent.mkdir(parents=True, exist_ok=True)

output_path.write_text(
    "\n".join(
        [
            f"LABEL={label}",
            f"CHILD_RC={child_rc}",
            f"CLASSIFICATION={classification}",
            f"RESULT_TYPE={result_type}",
            f"COMPLETED_COUNT_DELTA={completed_delta}",
            f"ALLOW_NEXT_LIFECYCLE={1 if allow_next else 0}",
            f"BLOCK_REASON={block_reason}",
            f"SUMMARY_READ={1 if summary_read else 0}",
            f"SUMMARY_PATH={summary_path or ''}",
            f"LEDGER_READ={1 if ledger_read else 0}",
            f"LEDGER_PATH={ledger_path or ''}",
            f"ENTRY_FILL_COUNT={len(entry_rows)}",
            f"EXIT_FILL_COUNT={len(exit_rows)}",
            f"PNL_POINTS={pnl_points}",
            f"EXIT_REASON={exit_reason}",
            f"LOCAL_FLAT={1 if local_flat else 0}",
            f"BROKER_FLAT={1 if broker_flat else 0}",
            f"ACTIVE_ORDER_COUNT={active_order_count}",
            f"FLAT_BETWEEN_CYCLES={1 if flat_between_cycles else 0}",
            f"RETRY_ALLOWED={1 if retry_allowed else 0}",
        ]
    )
    + "\n"
)
PY_TYPED_ADAPTER_R38VXFFDK
}

r38vxff_selftest_make_fixture() {
    local name="$1"
    local child_rc="$2"
    local classification="$3"
    local local_flat="$4"
    local broker_flat="$5"
    local active_orders="$6"
    local ledger_kind="$7"

    local fixture="$OUT/typed_selftest/$name"
    mkdir -p "$fixture"

    local ledger="$fixture/trades_ledger.json"

    case "$ledger_kind" in
        completed)
            cat > "$ledger" <<'JSON_LEDGER_R38VXFFDK'
[
  {
    "event_type": "ENTRY_FILL",
    "decision_id": "entry-1",
    "instrument_id": "13152002",
    "option_symbol": "NIFTY2671424100CE",
    "quantity": 65,
    "price": "100"
  },
  {
    "event_type": "EXIT_FILL",
    "decision_id": "exit-1",
    "instrument_id": "13152002",
    "option_symbol": "NIFTY2671424100CE",
    "quantity": 65,
    "price": "105",
    "pnl_points": "5",
    "reason": "target_points"
  }
]
JSON_LEDGER_R38VXFFDK
            ;;
        *)
            echo "[]" > "$ledger"
            ;;
    esac

    cat > "$fixture/summary.env" <<EOF_SUMMARY_R38VXFFDK
CHILD_RC=$child_rc
FINAL_CLASSIFICATION=$classification
LOCAL_FLAT=$local_flat
BROKER_FLAT=$broker_flat
ACTIVE_ORDER_COUNT=$active_orders
LEDGER_JSON=$ledger
EOF_SUMMARY_R38VXFFDK

    cat > "$fixture/child.log" <<EOF_CHILD_LOG_R38VXFFDK
CLASSIFICATION=$classification
EVIDENCE_ROOT=$fixture
EOF_CHILD_LOG_R38VXFFDK

    echo "$fixture"
}

r38vxff_selftest_expect() {
    local name="$1"
    local expected_type="$2"
    local expected_completed_delta="$3"
    local expected_allow_next="$4"
    local fixture="$5"
    local child_rc="$6"
    local local_flat="$7"

    local result="$fixture/result.env"

    r38vxff_classify_child_lifecycle_result \
        "SELFTEST_${name}" \
        "$child_rc" \
        "$fixture/child.log" \
        "$local_flat" \
        "$result"

    cat "$result"

    local actual_type
    actual_type="$(r38vxff_env_get "$result" RESULT_TYPE)"

    local actual_delta
    actual_delta="$(r38vxff_env_get "$result" COMPLETED_COUNT_DELTA)"

    local actual_allow_next
    actual_allow_next="$(r38vxff_env_get "$result" ALLOW_NEXT_LIFECYCLE)"

    [ "$actual_type" = "$expected_type" ] || {
        echo "SELFTEST_FAIL_TYPE_$name=$actual_type"
        return 1
    }

    [ "$actual_delta" = "$expected_completed_delta" ] || {
        echo "SELFTEST_FAIL_DELTA_$name=$actual_delta"
        return 1
    }

    [ "$actual_allow_next" = "$expected_allow_next" ] || {
        echo "SELFTEST_FAIL_ALLOW_NEXT_$name=$actual_allow_next"
        return 1
    }

    return 0
}

if [ "${1:-}" = "--r38vxff-typed-result-selftest" ]; then
    mkdir -p "$OUT/typed_selftest"

    F_COMPLETED="$(r38vxff_selftest_make_fixture completed 0 PASS_ONE_EVENT_COMPLETED 1 1 0 completed)"
    F_UNFILLED="$(r38vxff_selftest_make_fixture unfilled 0 SAFE_NO_CANDIDATE_NO_ENTRY_FILL 1 1 0 empty)"
    F_VETOED="$(r38vxff_selftest_make_fixture vetoed 0 BLOCK_RISK_VETOED 1 1 0 empty)"
    F_TIMEOUT_FLAT="$(r38vxff_selftest_make_fixture timed_out_flat 124 NO_NATURAL_ENTRY_TIMEOUT 1 1 0 empty)"
    F_TIMEOUT_OPEN="$(r38vxff_selftest_make_fixture timed_out_open 124 NO_NATURAL_ENTRY_TIMEOUT 0 0 1 empty)"
    F_FAILED="$(r38vxff_selftest_make_fixture failed 2 FAILED_UNKNOWN_CHILD_RESULT 1 1 0 empty)"
    F_COMPLETED_MISSING_LEDGER="$(r38vxff_selftest_make_fixture completed_missing_ledger 0 PASS_ONE_EVENT_COMPLETED 1 1 0 empty)"
    F_COMPLETED_NONFLAT="$(r38vxff_selftest_make_fixture completed_nonflat 0 PASS_ONE_EVENT_COMPLETED 0 1 0 completed)"

    r38vxff_selftest_expect completed COMPLETED 1 1 "$F_COMPLETED" 0 1
    r38vxff_selftest_expect unfilled UNFILLED 0 1 "$F_UNFILLED" 0 1
    r38vxff_selftest_expect vetoed VETOED 0 1 "$F_VETOED" 0 1
    r38vxff_selftest_expect timed_out_flat TIMED_OUT_FLAT 0 1 "$F_TIMEOUT_FLAT" 124 1
    r38vxff_selftest_expect timed_out_open TIMED_OUT_OPEN 0 0 "$F_TIMEOUT_OPEN" 124 0
    r38vxff_selftest_expect failed FAILED 0 0 "$F_FAILED" 2 1
    r38vxff_selftest_expect completed_missing_ledger FAILED 0 0 "$F_COMPLETED_MISSING_LEDGER" 0 1
    r38vxff_selftest_expect completed_nonflat FAILED 0 0 "$F_COMPLETED_NONFLAT" 0 0

    echo "SELFTEST_CLASSIFICATION=PASS_SUPERVISOR_TYPED_RESULT_ADAPTER_SOURCE_SELFTEST"
    echo "OBSERVED_TYPES=COMPLETED,FAILED,TIMED_OUT_FLAT,TIMED_OUT_OPEN,UNFILLED,VETOED"
    echo "NEVER_COUNT_FAILED_COMPLETED=1"
    echo "BROKER_FLAT_BETWEEN_CYCLES=1"
    echo "BLOCK_NEXT_ON_NONFLAT=1"
    echo "UNFILLED_NO_RETRY=1"
    echo "VETOED_NO_RETRY=1"
    exit 0
fi


{
    echo "===== R38VB UNATTENDED MULTI-LIFECYCLE PAPER ====="
    date -Is

    echo "MODE=UNATTENDED_CONTROLLED_PAPER"
    echo "MAX_LIFECYCLES=$MAX_LIFECYCLES"
    echo "ENTRY_CUTOFF_HHMM=$ENTRY_CUTOFF_HHMM"
    echo "MAX_DAILY_PAPER_LOSS=$MAX_DAILY_PAPER_LOSS"
    echo "ONE_OPEN_POSITION_MAX=1"
    echo "ONE_LOT_PER_LIFECYCLE=1"
    echo "ELIGIBLE_FAMILIES=MIST,MISB,MISC,MISR"
    echo "MISLS_EXCLUDED=1"
    echo "MIV_R_EXCLUDED=1"
    echo "MISO_WATCH_ONLY=1"
    echo "NATURAL_CANDIDATES_ONLY=1"
    echo "NO_FORCED_ENTRY=1"
    echo "NO_MANUAL_REDIS_XADD=1"
    echo "NO_REAL_LIVE=1"
    echo "NO_BROKER_ORDER=1"

    [ "$(systemctl show scalpx-mme.service -p ActiveState --value 2>/dev/null || true)" = "inactive" ] || {
        echo "STOP_SYSTEMD_NOT_INACTIVE"
        exit 1
    }

    [ "$(systemctl show scalpx-mme.service -p MainPID --value 2>/dev/null || true)" = "0" ] || {
        echo "STOP_SYSTEMD_MAIN_PID_NONZERO"
        exit 1
    }

    safe_between_cycles INITIAL
    echo "PASS_INITIAL_FLAT_OBSERVE_ONLY_TOPOLOGY"

    BASE_SHA="$(sha256sum "$BASE_RUNNER" | awk '{print $1}')"
    STRATEGY_SHA="$(sha256sum "$STRATEGY" | awk '{print $1}')"
    EXECUTION_SHA="$(sha256sum "$EXECUTION" | awk '{print $1}')"
    MANAGER_SHA="$(sha256sum "$MANAGER" | awk '{print $1}')"
    RESOLVER_SHA="$(sha256sum "$RESOLVER" | awk '{print $1}')"

    echo "base_runner_sha=$BASE_SHA"
    echo "strategy_sha=$STRATEGY_SHA"
    echo "execution_sha=$EXECUTION_SHA"
    echo "manager_sha=$MANAGER_SHA"
    echo "resolver_sha=$RESOLVER_SHA"

    [ "$BASE_SHA" = "$EXPECTED_BASE_SHA" ] || {
        echo "STOP_BASE_RUNNER_SHA_MISMATCH"
        exit 1
    }

    [ "$STRATEGY_SHA" = "$EXPECTED_STRATEGY_SHA" ] || {
        echo "STOP_STRATEGY_SHA_MISMATCH"
        exit 1
    }

    [ "$EXECUTION_SHA" = "$EXPECTED_EXECUTION_SHA" ] || {
        echo "STOP_EXECUTION_SHA_MISMATCH"
        exit 1
    }

    [ "$MANAGER_SHA" = "$EXPECTED_MANAGER_SHA" ] || {
        echo "STOP_MANAGER_SHA_MISMATCH"
        exit 1
    }

    [ "$RESOLVER_SHA" = "$EXPECTED_RESOLVER_SHA" ] || {
        echo "STOP_RESOLVER_SHA_MISMATCH"
        exit 1
    }

    .venv/bin/python -m py_compile "$STRATEGY" "$EXECUTION" "$MANAGER" "$RESOLVER"
    echo "PASS_PATCHED_SOURCE_IDENTITIES"

    DOW="$(TZ=Asia/Kolkata date +%u)"
    HHMM="$(TZ=Asia/Kolkata date +%H%M)"
    HHMM_NUM=$((10#$HHMM))

    [ "$DOW" -ge 1 ] && [ "$DOW" -le 5 ] || {
        echo "STOP_NOT_MARKET_WEEKDAY"
        exit 1
    }

    [ "$HHMM_NUM" -ge 915 ] && [ "$HHMM_NUM" -lt "$ENTRY_CUTOFF_HHMM" ] || {
        echo "STOP_OUTSIDE_UNATTENDED_ENTRY_WINDOW"
        exit 1
    }

    COMPLETED=0
    ATTEMPTED=0
    TYPED_COMPLETED=0
    TYPED_UNFILLED=0
    TYPED_VETOED=0
    TYPED_TIMED_OUT_FLAT=0
    TYPED_TIMED_OUT_OPEN=0
    TYPED_FAILED=0
    FINAL_REASON="MAX_LIFECYCLES_OR_CUTOFF"

    for cycle in $(seq 1 "$MAX_LIFECYCLES"); do
        HHMM="$(TZ=Asia/Kolkata date +%H%M)"
        HHMM_NUM=$((10#$HHMM))

        if [ "$HHMM_NUM" -ge "$ENTRY_CUTOFF_HHMM" ]; then
            FINAL_REASON="ENTRY_CUTOFF_REACHED"
            break
        fi

        CURRENT_PNL="$(position_field realized_pnl_day)"

        if daily_loss_reached "$CURRENT_PNL"; then
            FINAL_REASON="DAILY_PAPER_LOSS_LIMIT_REACHED"
            break
        fi

        safe_between_cycles "CYCLE_${cycle}_PRE"

        LABEL="$(printf 'R38VB%02d' "$cycle")"
        CHILD="$OUT/runners/${LABEL}_natural_one_event_lifecycle.sh"
        LOG="$OUT/logs/${LABEL}.log"

        cp -a "$BASE_RUNNER" "$CHILD"

        python3 - "$CHILD" "$LABEL" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
label = sys.argv[2]
source = path.read_text()

count = source.count("R38VBBASE")
print(f"identifier_patch_count={count}")

if count != 22:
    raise SystemExit("STOP_R38VBBASE_IDENTIFIER_COUNT_NOT_22")

source = source.replace("R38VBBASE", label)
path.write_text(source)

print("PASS_R38VB_DURABLE_CHILD_MATERIALIZED")
PY

        chmod 0755 "$CHILD"
        bash -n "$CHILD"

        ! grep -q 'R38VBBASE' "$CHILD" || {
            echo "STOP_R38VBBASE_IDENTIFIER_REMAINS"
            exit 1
        }

        grep -q "$EXPECTED_STRATEGY_SHA" "$CHILD" || {
            echo "STOP_STRATEGY_SHA_MISSING_FROM_CHILD"
            exit 1
        }

        grep -q "$EXPECTED_EXECUTION_SHA" "$CHILD" || {
            echo "STOP_EXECUTION_SHA_MISSING_FROM_CHILD"
            exit 1
        }

        grep -q 'compact_submitted_only_safe' "$CHILD" || {
            echo "STOP_COMPACT_SEMANTICS_MISSING_FROM_CHILD"
            exit 1
        }

        grep -q 'EXECUTION_SOURCE_IDENTITY_GUARD' "$CHILD" || {
            echo "STOP_EXECUTION_GUARD_MISSING_FROM_CHILD"
            exit 1
        }

        grep -q           'PASS_EXIT_MANAGER_AND_RESOLVER_SOURCE_IDENTITY_GUARD'           "$CHILD" || {
            echo "STOP_EXIT_MANAGER_RESOLVER_GUARD_MISSING_FROM_CHILD"
            exit 1
        }

        grep -q "$EXPECTED_MANAGER_SHA" "$CHILD" || {
            echo "STOP_EXPECTED_MANAGER_SHA_MISSING_FROM_CHILD"
            exit 1
        }

        grep -q "$EXPECTED_RESOLVER_SHA" "$CHILD" || {
            echo "STOP_EXPECTED_RESOLVER_SHA_MISSING_FROM_CHILD"
            exit 1
        }

        ATTEMPTED=$((ATTEMPTED + 1))

        echo "===== STARTING UNATTENDED CYCLE $cycle ====="
        echo "cycle_label=$LABEL"
        echo "child_runner_sha=$(sha256sum "$CHILD" | awk '{print $1}')"

        set +e
        bash "$CHILD" 2>&1 | tee "$LOG"
        CHILD_RC=${PIPESTATUS[0]}
        set -e

        HAS_POSITION="$(position_field has_position)"
        POSITION_SIDE="$(position_field position_side)"

        if [ "$HAS_POSITION" = "1" ]; then
            echo "CRITICAL_OPEN_PAPER_POSITION_PRESENT=1"
            echo "DO_NOT_KILL_PAPER_SERVICES=1"
            exit 1
        fi

        LOCAL_FLAT_NOW=0
        if position_is_flat; then
            LOCAL_FLAT_NOW=1
        fi

        TYPED_RESULT_FILE="$OUT/results/${LABEL}_typed_lifecycle_result.env"

        r38vxff_classify_child_lifecycle_result \
            "$LABEL" \
            "$CHILD_RC" \
            "$LOG" \
            "$LOCAL_FLAT_NOW" \
            "$TYPED_RESULT_FILE"

        cat "$TYPED_RESULT_FILE"

        # shellcheck disable=SC1090
        source "$TYPED_RESULT_FILE"

        case "${RESULT_TYPE:-FAILED}" in
            COMPLETED)
                [ "${COMPLETED_COUNT_DELTA:-0}" = "1" ] || {
                    FINAL_REASON="COMPLETED_RESULT_WITHOUT_DELTA"
                    echo "STOP_TYPED_RESULT_INVALID_COMPLETED_DELTA"
                    exit 1
                }
                COMPLETED=$((COMPLETED + 1))
                TYPED_COMPLETED=$((TYPED_COMPLETED + 1))
                FINAL_REASON="COMPLETED"
                ;;

            UNFILLED)
                TYPED_UNFILLED=$((TYPED_UNFILLED + 1))
                FINAL_REASON="UNFILLED"
                ;;

            VETOED)
                TYPED_VETOED=$((TYPED_VETOED + 1))
                FINAL_REASON="VETOED"
                ;;

            TIMED_OUT_FLAT)
                TYPED_TIMED_OUT_FLAT=$((TYPED_TIMED_OUT_FLAT + 1))
                FINAL_REASON="TIMED_OUT_FLAT"
                ;;

            TIMED_OUT_OPEN)
                TYPED_TIMED_OUT_OPEN=$((TYPED_TIMED_OUT_OPEN + 1))
                FINAL_REASON="TIMED_OUT_OPEN"
                echo "STOP_TYPED_LIFECYCLE_RESULT=TIMED_OUT_OPEN"
                echo "STOP_TYPED_LIFECYCLE_BLOCK_REASON=${BLOCK_REASON:-UNKNOWN}"
                exit 1
                ;;

            FAILED)
                TYPED_FAILED=$((TYPED_FAILED + 1))
                FINAL_REASON="FAILED"
                echo "STOP_TYPED_LIFECYCLE_RESULT=FAILED"
                echo "STOP_TYPED_LIFECYCLE_BLOCK_REASON=${BLOCK_REASON:-UNKNOWN}"
                exit 1
                ;;

            *)
                TYPED_FAILED=$((TYPED_FAILED + 1))
                FINAL_REASON="UNKNOWN_TYPED_RESULT"
                echo "STOP_UNKNOWN_TYPED_LIFECYCLE_RESULT=${RESULT_TYPE:-ABSENT}"
                exit 1
                ;;
        esac

        [ "${ALLOW_NEXT_LIFECYCLE:-0}" = "1" ] || {
            echo "STOP_NEXT_LIFECYCLE_BLOCKED_BY_TYPED_ADAPTER"
            echo "STOP_TYPED_LIFECYCLE_RESULT=${RESULT_TYPE:-ABSENT}"
            echo "STOP_TYPED_LIFECYCLE_BLOCK_REASON=${BLOCK_REASON:-UNKNOWN}"
            exit 1
        }

        safe_between_cycles "CYCLE_${cycle}_POST"
        sleep 2
    done

    safe_between_cycles FINAL

    FINAL_PNL="$(position_field realized_pnl_day)"
    ORDER_LEN="$(redis-cli --raw XLEN orders:mme:stream 2>/dev/null || true)"
    LEDGER_LEN="$(redis-cli --raw XLEN trades:ledger:stream 2>/dev/null || true)"

    {
        echo "classification=PASS_R38VB_UNATTENDED_MULTI_LIFECYCLE_SESSION_COMPLETE_FLAT"
        echo "lifecycles_attempted=$ATTEMPTED"
        echo "lifecycles_completed=$COMPLETED"
        echo "typed_completed=$TYPED_COMPLETED"
        echo "typed_unfilled=$TYPED_UNFILLED"
        echo "typed_vetoed=$TYPED_VETOED"
        echo "typed_timed_out_flat=$TYPED_TIMED_OUT_FLAT"
        echo "typed_timed_out_open=$TYPED_TIMED_OUT_OPEN"
        echo "typed_failed=$TYPED_FAILED"
        echo "typed_result_adapter=1"
        echo "final_reason=$FINAL_REASON"
        echo "final_realized_pnl_day=${FINAL_PNL:-ABSENT}"
        echo "final_order_stream_length=$ORDER_LEN"
        echo "final_ledger_stream_length=$LEDGER_LEN"
        echo "final_position=FLAT"
        echo "risk_count=0"
        echo "execution_count=0"
        echo "no_real_live=1"
        echo "no_broker_order=1"
    } > "$SUMMARY"

    cat "$SUMMARY"
    echo "CLASSIFICATION=PASS_R38VB_UNATTENDED_MULTI_LIFECYCLE_SESSION_COMPLETE_FLAT"
} 2>&1 | tee "$OUT/run.txt"
