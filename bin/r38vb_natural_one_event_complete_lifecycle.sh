#!/usr/bin/env bash
set -Eeuo pipefail

# BEGIN R38VB_DURABLE_PROVEN_CHILD_BASE_V1
# Derived from the successfully executed sealed lifecycle child.
# The base placeholder is replaced by the supervisor with a unique cycle label.
# END R38VB_DURABLE_PROVEN_CHILD_BASE_V1

# BEGIN R38VBBASE_EXECUTION_SOURCE_IDENTITY_GUARD_V1
CHILD_EXECUTION_SRC="app/mme_scalpx/services/execution.py"
CHILD_EXPECTED_EXECUTION_SHA="bfcee7f3901c33955a4c19e81eddee7791598f1826e89031a3f088eea5bfdb4d"

CHILD_ACTUAL_EXECUTION_SHA="$(
    sha256sum "$CHILD_EXECUTION_SRC" |
    awk '{print $1}'
)"

echo "R38VBBASE_EXECUTION_SHA=$CHILD_ACTUAL_EXECUTION_SHA"

[ "$CHILD_ACTUAL_EXECUTION_SHA" = "$CHILD_EXPECTED_EXECUTION_SHA" ] || {
    echo "STOP_R38VBBASE_EXECUTION_SHA_DRIFT"
    exit 92
}

echo "PASS_R38VBBASE_EXECUTION_SOURCE_IDENTITY_GUARD"
# END R38VBBASE_EXECUTION_SOURCE_IDENTITY_GUARD_V1


cd /home/Lenovo/scalpx/projects/mme_scalpx || exit 1

TAG="LANE-X-R38VBBASE_NATURAL_ONE_EVENT_ENTRY_STRATEGY_EXIT_FLAT_$(date +%Y%m%d_%H%M%S)"
ROOT="run/proofs/$TAG"
ARCHIVE="run/evidence_bundles/${TAG}.tar.gz"

PY="$PWD/.venv/bin/python"
PROVIDER="app.mme_scalpx.integrations.bootstrap_provider:provide"

STRATEGY_SRC="app/mme_scalpx/services/strategy.py"
EXECUTION_SRC="app/mme_scalpx/services/execution.py"
MANAGER_SRC="app/mme_scalpx/services/strategy_family/position_exit_manager.py"
RESOLVER_SRC="app/mme_scalpx/services/strategy_family/exact_position_quote_resolver.py"
FINDER="bin/r38ga_find_candidate.py"
INSTRUMENT_FILE="data/instruments/nfo_instruments.csv"

EXPECTED_STRATEGY_SHA="5692fa3d32c224e6ab7ddfcea512da6fbfe5326d4a462bcc9b88a1730e5e9fb7"
EXPECTED_MANAGER_SHA="67d0691abec3b38f4120763b59ad9a6b55316ef33c71f9edad93195c673dde4f"
EXPECTED_RESOLVER_SHA="4a4365f804321bd7c8ff3ef630224a7c2ea3a8419c7c7bc8866753acdeae26c0"

ROUTE_ACK="I ACKNOWLEDGE CONTROLLED PAPER ONLY: NO REAL LIVE, NO BROKER ORDER, NO REAL MONEY, ONE APPROVED SCOPE ONLY, POSITION MUST START FLAT"
NO_BROKER_ACK="ACK_FOR_CONTROLLED_PROJECTION"

EXIT_POLICY_ACK="R38TK2_FAMILY_CONTRACT_EXIT_V2_CLOSE_TARGET5_STOP4_TIME300"
EXIT_SCOPE_ACK="R38TMB1_EXACT_OPEN_POSITION_ONE_LOT_ONE_EVENT_NO_REAL_LIVE_NO_BROKER"

ENTRY_TIMEOUT_SECONDS=240
EXIT_TIMEOUT_SECONDS=360

mkdir -p \
  "$ROOT/logs" \
  "$ROOT/outputs" \
  run/evidence_bundles

PAPER_ACTIVE=0
SUCCESS=0

count_service() {
    local service="$1"

    pgrep -fc \
      "app\.mme_scalpx\.main --service ${service}([[:space:]]|$)" \
      2>/dev/null || true
}

service_pid() {
    local service="$1"

    pgrep -f \
      "app\.mme_scalpx\.main --service ${service}([[:space:]]|$)" \
      2>/dev/null |
    head -1 || true
}

stop_service() {
    local service="$1"
    local pid

    while true; do
        pid="$(service_pid "$service")"

        [ -n "$pid" ] || break

        echo "SIGTERM service=$service pid=$pid"
        kill -TERM "$pid" 2>/dev/null || true

        for _ in $(seq 1 30); do
            kill -0 "$pid" 2>/dev/null || break
            sleep 0.5
        done

        if kill -0 "$pid" 2>/dev/null; then
            echo "STOP_${service^^}_DID_NOT_EXIT_GRACEFULLY pid=$pid"
            return 1
        fi
    done
}

stream_len() {
    local key="$1"
    local type

    type="$(
        redis-cli --raw TYPE "$key" \
          2>/dev/null || true
    )"

    if [ "$type" = "stream" ]; then
        redis-cli --raw XLEN "$key"
    else
        printf '0'
    fi
}

stream_last_id() {
    local key="$1"
    local type
    local value

    type="$(
        redis-cli --raw TYPE "$key" \
          2>/dev/null || true
    )"

    if [ "$type" != "stream" ]; then
        printf '0-0'
        return
    fi

    value="$(
        redis-cli --raw XREVRANGE \
          "$key" + - COUNT 1 \
          2>/dev/null |
        head -1
    )"

    printf '%s' "${value:-0-0}"
}

position_is_open() {
    [ "$(
        redis-cli --raw HGET \
          state:position:mme \
          has_position 2>/dev/null || true
    )" = "1" ]
}

position_is_flat() {
    [ "$(
        redis-cli --raw HGET \
          state:position:mme \
          has_position 2>/dev/null || true
    )" = "0" ] &&
    [ "$(
        redis-cli --raw HGET \
          state:position:mme \
          position_side 2>/dev/null || true
    )" = "FLAT" ] &&
    [ "$(
        redis-cli --raw HGET \
          state:position:mme \
          qty_lots 2>/dev/null || true
    )" = "0" ] &&
    [ "$(
        redis-cli --raw HGET \
          state:position:mme \
          qty_units 2>/dev/null || true
    )" = "0" ]
}

OBSERVE_ENV=(
    "PYTHONPATH=$PWD${PYTHONPATH:+:$PYTHONPATH}"
    "SCALPX_OBSERVE_ONLY=1"
    "B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY=1"
    "SCALPX_ENABLE_STRATEGY_OWNED_EXIT_MANAGER=0"
    "SCALPX_ENABLE_PAPER=0"
    "MME_ENABLE_PAPER=0"
    "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME=0"
    "SCALPX_CONTROLLED_PAPER_ARMED=0"
    "SCALPX_PAPER_ARMED=0"
    "SCALPX_ENABLE_LIVE=0"
    "SCALPX_REAL_LIVE_ALLOWED=0"
    "SCALPX_ALLOW_REAL_LIVE=0"
    "SCALPX_ALLOW_BROKER_ORDERS=0"
    "SCALPX_BROKER_ORDER_ENABLED=0"
    "MME_ENABLE_LIVE=0"
    "MME_ALLOW_LIVE_ORDER=0"
    "MME_ALLOW_BROKER_ORDERS=0"
)

start_observe_service() {
    local service="$1"
    local log="$ROOT/logs/observe_${service}.log"

    nohup env \
      "${OBSERVE_ENV[@]}" \
      "$PY" -m app.mme_scalpx.main \
        --service "$service" \
        --bootstrap-provider "$PROVIDER" \
        --skip-group-bootstrap \
      > "$log" 2>&1 < /dev/null &

    echo "$!"
}

wait_service_one() {
    local service="$1"
    local expected_pid="${2:-}"

    for _ in $(seq 1 60); do
        if [ "$(count_service "$service")" = "1" ]; then
            local actual_pid
            actual_pid="$(service_pid "$service")"

            if [ -z "$expected_pid" ] ||
               [ "$actual_pid" = "$expected_pid" ]; then
                return 0
            fi
        fi

        sleep 0.5
    done

    return 1
}

ensure_observe_stack() {
    local service
    local pid

    for service in feeds features strategy; do
        case "$(count_service "$service")" in
            0)
                pid="$(start_observe_service "$service")"
                echo "observe_${service}_start_pid=$pid"

                wait_service_one "$service" "$pid" || {
                    echo "RECOVERY_OBSERVE_SERVICE_FAILED=$service"
                    return 1
                }

                sleep 3
                ;;
            1)
                ;;
            *)
                echo "RECOVERY_MULTIPLE_SERVICE_PROCESSES=$service"
                return 1
                ;;
        esac
    done
}

cleanup_on_error() {
    local rc=$?

    set +e

    if [ "$rc" -eq 0 ]; then
        return
    fi

    echo
    echo "===== FAILURE SAFETY HANDLER ====="

    if position_is_open; then
        echo "CRITICAL_OPEN_PAPER_POSITION_PRESENT=1"
        echo "FAIL_SAFE_ACTION=KEEP_EXACT_PAPER_STRATEGY_RISK_EXECUTION_RUNNING"
        echo "DO_NOT_KILL_SERVICES_WHILE_POSITION_OPEN=1"

        redis-cli --raw HGETALL \
          state:position:mme \
          > "$ROOT/outputs/open_position_failure_state.txt" \
          2>/dev/null || true

        ps -eo pid,ppid,etime,args |
        grep -E \
          'app\.mme_scalpx\.main.*--service (feeds|features|strategy|risk|execution)' |
        grep -v grep \
          > "$ROOT/outputs/open_position_failure_processes.txt" \
          || true

        exit "$rc"
    fi

    stop_service risk || true
    stop_service execution || true

    if [ "$PAPER_ACTIVE" = "1" ]; then
        stop_service strategy || true
        ensure_observe_stack || true
    fi

    echo "FAILURE_FINAL_POSITION_FLAT=1"
    echo "FAILURE_OBSERVE_RESTORATION_ATTEMPTED=1"

    exit "$rc"
}

trap cleanup_on_error EXIT INT TERM

echo "===== $TAG ====="
date -Is
echo "CURRENT_LOCATION=LANE_X_R38VBBASE"
echo "OBJECTIVE=ONE_REAL_OBSERVED_CANDIDATE_NATURAL_ENTRY_STRATEGY_OWNED_EXIT_FLAT"
echo "ONE_LOT=1"
echo "MAX_ENTRY_EVENTS=1"
echo "NO_REAL_LIVE=1"
echo "NO_BROKER_ORDER=1"
echo "NO_MANUAL_DECISION_XADD=1"
echo "NO_FORCED_ENTRY=1"
echo "NO_FORCED_EXIT=1"
echo "NO_REDIS_DELETE_TRIM_FLUSH=1"

echo
echo "===== 0) MARKET WINDOW ====="

DOW="$(TZ=Asia/Kolkata date +%u)"
HHMM="$(TZ=Asia/Kolkata date +%H%M)"
HHMM_NUM=$((10#$HHMM))

echo "IST_DOW=$DOW"
echo "IST_HHMM=$HHMM"

[ "$DOW" -le 5 ] || {
    echo "STOP_NOT_WEEKDAY"
    exit 10
}

[ "$HHMM_NUM" -ge 915 ] &&
[ "$HHMM_NUM" -le 1505 ] || {
    echo "STOP_OUTSIDE_SAFE_NEW_ENTRY_WINDOW_0915_TO_1505_IST"
    exit 11
}

echo "PASS_MARKET_WINDOW"

echo
echo "===== 1) HARD SAFETY ====="

UNIT="$(
    systemctl show scalpx-mme.service \
      -p ActiveState --value 2>/dev/null || true
)"

echo "system_monolith=$UNIT"

[ "$UNIT" = "inactive" ] || {
    echo "STOP_SYSTEM_MONOLITH_ACTIVE"
    exit 20
}

for service in risk execution; do
    count="$(count_service "$service")"
    echo "${service}_count=$count"

    [ "$count" = "0" ] || {
        echo "STOP_${service^^}_ALREADY_RUNNING"
        exit 21
    }
done

position_is_flat || {
    echo "STOP_POSITION_NOT_STRICT_FLAT"
    redis-cli --raw HGETALL state:position:mme || true
    exit 22
}

echo "PASS_INITIAL_FLAT_SAFETY"

echo
echo "===== 2) SOURCE IDENTITY ====="

for file in \
    "$STRATEGY_SRC" \
    "$EXECUTION_SRC" \
    "$MANAGER_SRC" \
    "$RESOLVER_SRC" \
    "$FINDER" \
    "$INSTRUMENT_FILE"
do
    [ -f "$file" ] || {
        echo "STOP_MISSING_FILE=$file"
        exit 23
    }
done

STRATEGY_SHA="$(
    sha256sum "$STRATEGY_SRC" |
    awk '{print $1}'
)"

echo "strategy_sha=$STRATEGY_SHA"

[ "$STRATEGY_SHA" = "$EXPECTED_STRATEGY_SHA" ] || {
    echo "STOP_STRATEGY_SHA_DRIFT"
    exit 24
}

MANAGER_SHA="$(
    sha256sum "$MANAGER_SRC" |
    awk '{print $1}'
)"

RESOLVER_SHA="$(
    sha256sum "$RESOLVER_SRC" |
    awk '{print $1}'
)"

echo "manager_sha=$MANAGER_SHA"
echo "resolver_sha=$RESOLVER_SHA"

[ "$MANAGER_SHA" = "$EXPECTED_MANAGER_SHA" ] || {
    echo "STOP_MANAGER_SHA_DRIFT"
    exit 93
}

[ "$RESOLVER_SHA" = "$EXPECTED_RESOLVER_SHA" ] || {
    echo "STOP_RESOLVER_SHA_DRIFT"
    exit 94
}

echo "PASS_EXIT_MANAGER_AND_RESOLVER_SOURCE_IDENTITY_GUARD"

grep -q \
  "R38TMB1_ACTIVE_STRATEGY_EXIT_GATE_V1" \
  "$STRATEGY_SRC"

grep -q \
  "R38TK2_FAMILY_CONTRACT_EXIT_V2_CLOSE" \
  "$MANAGER_SRC"

grep -q \
  "R38TMBQ4_PURE_EXACT_POSITION_QUOTE_RESOLVER_V1" \
  "$RESOLVER_SRC"

grep -q \
  "R38TMA1_EXECUTION_ENTRY_OWNERSHIP_EXACT_V1" \
  "$EXECUTION_SRC"

"$PY" -m py_compile \
  "$STRATEGY_SRC" \
  "$EXECUTION_SRC" \
  "$MANAGER_SRC" \
  "$RESOLVER_SRC" \
  "$FINDER"

echo "PASS_SOURCE_IDENTITY_AND_COMPILE"

echo
echo "===== 3) DAILY METADATA CHECK ====="

METADATA_AGE="$(
    "$PY" - "$INSTRUMENT_FILE" <<'PY'
from pathlib import Path
import sys
import time

path = Path(sys.argv[1])

print(
    max(
        0,
        int(time.time() - path.stat().st_mtime),
    )
)
PY
)"

echo "metadata_age_seconds=$METADATA_AGE"

METADATA_REFRESHED=0

if [ "$METADATA_AGE" -gt 64800 ]; then
    echo "METADATA_REFRESH_REQUIRED=1"

    CANDIDATE_METADATA="$ROOT/nfo_instruments.candidate.csv"

    PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}" \
    "$PY" -m app.mme_scalpx.integrations.instrument_master_sync \
      --exchange NFO \
      --output "$CANDIDATE_METADATA" \
      --log-level INFO \
      2>&1 |
    tee "$ROOT/outputs/instrument_sync.txt"

    grep -q \
      "sync_ok = True" \
      "$ROOT/outputs/instrument_sync.txt" || {
        echo "STOP_INSTRUMENT_SYNC_FAILED"
        exit 25
    }

    "$PY" - \
      "$CANDIDATE_METADATA" <<'PY'
from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
import sys

path = Path(sys.argv[1])

required = {
    "instrument_token",
    "tradingsymbol",
    "expiry",
    "strike",
    "lot_size",
    "instrument_type",
    "segment",
    "exchange",
}

rows = 0
types = set()
nifty_future = 0
nifty_call = 0
nifty_put = 0
today = date.today()

with path.open(
    "r",
    encoding="utf-8-sig",
    newline="",
) as handle:
    reader = csv.DictReader(handle)

    header = set(reader.fieldnames or [])

    missing = required - header

    if missing:
        raise SystemExit(
            "missing_columns="
            + ",".join(sorted(missing))
        )

    for row in reader:
        rows += 1

        kind = str(
            row.get("instrument_type")
            or ""
        ).upper()

        types.add(kind)

        symbol = str(
            row.get("tradingsymbol")
            or ""
        ).upper()

        name = str(
            row.get("name")
            or ""
        ).upper()

        expiry_raw = str(
            row.get("expiry")
            or ""
        )[:10]

        try:
            expiry = date.fromisoformat(
                expiry_raw
            )
        except ValueError:
            continue

        if expiry < today:
            continue

        if not (
            name == "NIFTY"
            or symbol.startswith("NIFTY")
        ):
            continue

        if kind == "FUT":
            nifty_future += 1
        elif kind == "CE":
            nifty_call += 1
        elif kind == "PE":
            nifty_put += 1

assert rows >= 10000, rows
assert {"FUT", "CE", "PE"}.issubset(types)
assert nifty_future >= 1
assert nifty_call >= 1
assert nifty_put >= 1

print("PASS_METADATA_CANDIDATE_VALIDATION")
print(f"ROWS={rows}")
print(f"NIFTY_FUT={nifty_future}")
print(f"NIFTY_CE={nifty_call}")
print(f"NIFTY_PE={nifty_put}")
PY

    cp -a \
      "$INSTRUMENT_FILE" \
      "$ROOT/nfo_instruments.before.csv"

    install -m 0664 \
      "$CANDIDATE_METADATA" \
      "${INSTRUMENT_FILE}.r38tn.tmp"

    mv -f \
      "${INSTRUMENT_FILE}.r38tn.tmp" \
      "$INSTRUMENT_FILE"

    METADATA_REFRESHED=1

    echo "PASS_METADATA_REFRESH_AND_ATOMIC_INSTALL"
else
    echo "METADATA_REFRESH_REQUIRED=0"
fi

sha256sum "$INSTRUMENT_FILE" |
tee "$ROOT/outputs/instrument_sha.txt"

echo
echo "===== 4) ENSURE CLEAN CANONICAL OBSERVE STACK ====="

REBUILD_STACK=0

if [ "$METADATA_REFRESHED" = "1" ]; then
    REBUILD_STACK=1
fi

for service in feeds features strategy; do
    count="$(count_service "$service")"

    echo "${service}_count_before=$count"

    [ "$count" -le 1 ] || {
        echo "STOP_MULTIPLE_${service^^}_PROCESSES"
        exit 26
    }

    if [ "$count" = "0" ]; then
        REBUILD_STACK=1
    fi
done

if [ "$REBUILD_STACK" = "1" ]; then
    echo "REBUILD_OBSERVE_STACK=1"

    stop_service strategy || true
    stop_service features || true
    stop_service feeds || true

    FEEDS_PID="$(start_observe_service feeds)"
    wait_service_one feeds "$FEEDS_PID" || {
        tail -200 "$ROOT/logs/observe_feeds.log" || true
        exit 27
    }

    sleep 5

    FEATURES_PID="$(start_observe_service features)"
    wait_service_one features "$FEATURES_PID" || {
        tail -200 "$ROOT/logs/observe_features.log" || true
        exit 28
    }

    sleep 5

    STRATEGY_PID="$(start_observe_service strategy)"
    wait_service_one strategy "$STRATEGY_PID" || {
        tail -200 "$ROOT/logs/observe_strategy.log" || true
        exit 29
    }

    sleep 15
else
    echo "REBUILD_OBSERVE_STACK=0"
fi

for service in feeds features strategy; do
    count="$(count_service "$service")"
    pid="$(service_pid "$service")"

    echo "${service}_count=$count"
    echo "${service}_pid=$pid"

    [ "$count" = "1" ] || {
        echo "STOP_CANONICAL_OBSERVE_STACK_COUNT_${service^^}=$count"
        exit 30
    }
done

position_is_flat || {
    echo "STOP_POSITION_CHANGED_DURING_OBSERVE_START"
    exit 31
}

echo "PASS_CANONICAL_OBSERVE_STACK"

echo
echo "===== 5) EXACT RESOLVER ROLLING QUOTE GATE ====="

PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}" \
"$PY" - \
  "$ROOT/outputs/rolling_quote_gate.json" <<'PY' | tee "$ROOT/outputs/rolling_quote_gate.txt"
from __future__ import annotations

import json
from pathlib import Path
import sys
import time

import redis

from app.mme_scalpx.services.strategy_family.exact_position_quote_resolver import (
    ExactPositionQuoteResolver,
)


output = Path(sys.argv[1])

client = redis.Redis(
    host="127.0.0.1",
    port=6379,
    decode_responses=True,
)

resolver = ExactPositionQuoteResolver()

pair_pass = 0
samples = []

for index in range(25):
    now_ns = time.time_ns()

    raw = client.hget(
        "state:features:mme:fut",
        "family_surfaces_json",
    )

    surfaces = json.loads(raw) if raw else {}

    options = (
        surfaces
        .get("shared_core", {})
        .get("options", {})
    )

    sample = {
        "index": index + 1,
        "call": {},
        "put": {},
    }

    both = True

    for branch, suffix in (
        ("CALL", "CE"),
        ("PUT", "PE"),
    ):
        raw_leg = (
            options
            .get(branch.lower(), {})
            .get("raw")
            or {}
        )

        symbol = str(
            raw_leg.get("option_symbol")
            or raw_leg.get("tradingsymbol")
            or raw_leg.get("trading_symbol")
            or raw_leg.get("symbol")
            or ""
        ).strip().upper()

        token = str(
            raw_leg.get("option_token")
            or raw_leg.get("instrument_token")
            or ""
        ).strip()

        position = {
            "has_position": "1",
            "position_side":
                "LONG_CALL"
                if branch == "CALL"
                else "LONG_PUT",
            "qty_lots": "1",
            "qty_units": "65",
            "strategy_family_id": "MIST",
            "branch_id": branch,
            "entry_option_symbol": symbol,
            "entry_option_token": token,
            "option_symbol": symbol,
            "option_token": token,
            "instrument_token": token,
        }

        result = resolver.resolve(
            family_surfaces=surfaces,
            position=position,
            now_ns=now_ns,
            local_utc_offset_ns=(
                19_800_000_000_000
            ),
        )

        valid = bool(
            symbol.endswith(suffix)
            and result.resolved
            and result.quote is not None
        )

        sample[
            branch.lower()
        ] = {
            "symbol": symbol,
            "token": token,
            "valid": valid,
            "reason":
                result.reason_code,
            "quote":
                result.quote,
        }

        both = both and valid

    if both:
        pair_pass += 1

    samples.append(sample)

    print(
        f"SAMPLE={index + 1} "
        f"CALL_VALID={int(sample['call']['valid'])} "
        f"PUT_VALID={int(sample['put']['valid'])} "
        f"PAIR_VALID={int(both)}",
        flush=True,
    )

    if pair_pass >= 5:
        break

    time.sleep(1)

classification = (
    "PASS_R38VBBASE_ROLLING_EXACT_QUOTE_GATE"
    if pair_pass >= 5
    else
    "BLOCK_R38VBBASE_ROLLING_EXACT_QUOTE_GATE"
)

report = {
    "classification": classification,
    "pair_valid_count": pair_pass,
    "samples": samples,
    "redis_write_attempted": False,
}

output.write_text(
    json.dumps(
        report,
        indent=2,
        sort_keys=True,
        default=str,
    )
    + "\n"
)

print(
    "CLASSIFICATION="
    + classification
)
print(
    "PAIR_VALID_COUNT="
    + str(pair_pass)
)
print("REDIS_WRITE_ATTEMPTED=0")

if pair_pass < 5:
    raise SystemExit(20)
PY

grep -q \
  "CLASSIFICATION=PASS_R38VBBASE_ROLLING_EXACT_QUOTE_GATE" \
  "$ROOT/outputs/rolling_quote_gate.txt"

echo "PASS_ROLLING_EXACT_QUOTE_GATE"

echo
echo "===== 6) FIND AND LOCK ONE REAL OBSERVED CANDIDATE ====="

cat > "$ROOT/validate_candidate.py" <<'PY'
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import time

import redis

from app.mme_scalpx.services.strategy_family.exact_position_quote_resolver import (
    ExactPositionQuoteResolver,
)


source = Path(sys.argv[1])
output = Path(sys.argv[2])

try:
    candidate = json.loads(
        source.read_text()
    )
except Exception:
    raise SystemExit(1)

if candidate.get("classification") != (
    "PASS_REAL_OBSERVED_CANDIDATE_FOUND"
):
    raise SystemExit(2)

family = str(
    candidate.get("family")
    or ""
).strip().upper()

side = str(
    candidate.get("side")
    or ""
).strip().upper()

action = str(
    candidate.get("action")
    or ""
).strip().upper()

token = str(
    candidate.get("instrument_token")
    or ""
).strip()

symbol = str(
    candidate.get("option_symbol")
    or ""
).strip().upper()

stream_id = str(
    candidate.get("stream_id")
    or "0-0"
)

if family not in {
    "MIST",
    "MISB",
    "MISC",
    "MISR",
}:
    raise SystemExit(3)

if side not in {
    "CALL",
    "PUT",
}:
    raise SystemExit(4)

if action != (
    "ENTER_CALL"
    if side == "CALL"
    else "ENTER_PUT"
):
    raise SystemExit(5)

if not token or not symbol:
    raise SystemExit(6)

if not symbol.endswith(
    "CE" if side == "CALL" else "PE"
):
    raise SystemExit(7)

try:
    stream_ms = int(
        stream_id.split("-", 1)[0]
    )
except ValueError:
    raise SystemExit(8)

age_ms = (
    int(time.time() * 1000)
    - stream_ms
)

if age_ms < -1000 or age_ms > 15000:
    raise SystemExit(9)

seed = "|".join(
    [
        "CONTROLLED_PAPER_SCOPE_ACK",
        family,
        side,
        action,
        token,
        symbol,
        "LOTS_1",
    ]
)

expected_ack = (
    "ACK_"
    + hashlib.sha256(
        seed.encode()
    ).hexdigest()[:20].upper()
)

reported_ack = str(
    candidate.get("ack")
    or ""
).strip().upper()

if reported_ack != expected_ack:
    raise SystemExit(10)

client = redis.Redis(
    host="127.0.0.1",
    port=6379,
    decode_responses=True,
)

raw = client.hget(
    "state:features:mme:fut",
    "family_surfaces_json",
)

if not raw:
    raise SystemExit(11)

surfaces = json.loads(raw)

position = {
    "has_position": "1",
    "position_side":
        "LONG_CALL"
        if side == "CALL"
        else "LONG_PUT",
    "qty_lots": "1",
    "qty_units": "65",
    "strategy_family_id": family,
    "branch_id": side,
    "entry_option_symbol": symbol,
    "entry_option_token": token,
    "option_symbol": symbol,
    "option_token": token,
    "instrument_token": token,
}

resolution = (
    ExactPositionQuoteResolver()
    .resolve(
        family_surfaces=surfaces,
        position=position,
        now_ns=time.time_ns(),
        local_utc_offset_ns=(
            19_800_000_000_000
        ),
    )
)

if (
    not resolution.resolved
    or resolution.quote is None
):
    raise SystemExit(12)

locked = dict(candidate)

locked.update(
    {
        "classification":
            "PASS_R38VBBASE_REAL_CANDIDATE_LOCKED",
        "generated_ack":
            expected_ack,
        "candidate_age_ms":
            age_ms,
        "exact_quote":
            resolution.quote,
        "exact_quote_reason":
            resolution.reason_code,
    }
)

output.write_text(
    json.dumps(
        locked,
        indent=2,
        sort_keys=True,
        default=str,
    )
    + "\n"
)

print(
    "CLASSIFICATION="
    "PASS_R38VBBASE_REAL_CANDIDATE_LOCKED"
)
print(f"FAMILY={family}")
print(f"SIDE={side}")
print(f"ACTION={action}")
print(f"TOKEN={token}")
print(f"SYMBOL={symbol}")
print(f"GENERATED_ACK={expected_ack}")
print(f"CANDIDATE_AGE_MS={age_ms}")
PY

FOUND=0
RAW_SCOPE="$ROOT/outputs/candidate_raw.json"
LOCKED_SCOPE="$ROOT/outputs/candidate_locked.json"

for attempt in $(seq 1 180); do
    PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}" \
    "$PY" "$FINDER" \
      > "$RAW_SCOPE" 2>/dev/null || true

    if PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}" \
       "$PY" "$ROOT/validate_candidate.py" \
         "$RAW_SCOPE" \
         "$LOCKED_SCOPE" \
         > "$ROOT/outputs/candidate_validation.txt" \
         2>&1
    then
        FOUND=1
        cat "$ROOT/outputs/candidate_validation.txt"
        break
    fi

    if [ $((attempt % 15)) -eq 0 ]; then
        echo "WAITING_REAL_CANDIDATE attempt=$attempt"
        cat "$RAW_SCOPE" 2>/dev/null || true
    fi

    sleep 1
done

[ "$FOUND" = "1" ] || {
    echo "STOP_NO_FRESH_REAL_ELIGIBLE_CANDIDATE"
    exit 32
}

FAMILY="$(
    "$PY" -c \
      'import json,sys;print(json.load(open(sys.argv[1]))["family"])' \
      "$LOCKED_SCOPE"
)"

SIDE="$(
    "$PY" -c \
      'import json,sys;print(json.load(open(sys.argv[1]))["side"])' \
      "$LOCKED_SCOPE"
)"

ACTION="$(
    "$PY" -c \
      'import json,sys;print(json.load(open(sys.argv[1]))["action"])' \
      "$LOCKED_SCOPE"
)"

TOKEN="$(
    "$PY" -c \
      'import json,sys;print(json.load(open(sys.argv[1]))["instrument_token"])' \
      "$LOCKED_SCOPE"
)"

SYMBOL="$(
    "$PY" -c \
      'import json,sys;print(json.load(open(sys.argv[1]))["option_symbol"])' \
      "$LOCKED_SCOPE"
)"

GENERATED_ACK="$(
    "$PY" -c \
      'import json,sys;print(json.load(open(sys.argv[1]))["generated_ack"])' \
      "$LOCKED_SCOPE"
)"

echo "LOCKED_SCOPE family=$FAMILY side=$SIDE action=$ACTION token=$TOKEN symbol=$SYMBOL generated_ack=$GENERATED_ACK"

echo
echo "===== 7) CAPTURE LIFECYCLE BASELINE ====="

DECISION_BASE_ID="$(
    stream_last_id decisions:mme:stream
)"

ORDER_BASE_ID="$(
    stream_last_id orders:mme:stream
)"

LEDGER_BASE_ID="$(
    stream_last_id trades:ledger:stream
)"

ACK_BASE_ID="$(
    stream_last_id decisions:ack:stream
)"

ORDER_BASE_LEN="$(
    stream_len orders:mme:stream
)"

LEDGER_BASE_LEN="$(
    stream_len trades:ledger:stream
)"

PNL_BEFORE="$(
    redis-cli --raw HGET \
      state:position:mme \
      realized_pnl_day 2>/dev/null || true
)"

cat > "$ROOT/outputs/baseline.txt" <<EOF
DECISION_BASE_ID=$DECISION_BASE_ID
ORDER_BASE_ID=$ORDER_BASE_ID
LEDGER_BASE_ID=$LEDGER_BASE_ID
ACK_BASE_ID=$ACK_BASE_ID
ORDER_BASE_LEN=$ORDER_BASE_LEN
LEDGER_BASE_LEN=$LEDGER_BASE_LEN
PNL_BEFORE=$PNL_BEFORE
EOF

cat "$ROOT/outputs/baseline.txt"

echo
echo "===== 8) START PAPER-ONLY EXECUTION AND RISK ====="

PAPER_COMMON_ENV=(
    "PYTHONPATH=$PWD${PYTHONPATH:+:$PYTHONPATH}"
    "SCALPX_OBSERVE_ONLY=0"
    "B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY=0"
    "SCALPX_ENABLE_PAPER=1"
    "MME_ENABLE_PAPER=1"
    "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME=1"
    "SCALPX_CONTROLLED_PAPER_ARMED=1"
    "SCALPX_PAPER_ARMED=1"
    "SCALPX_POSITION_FLAT_VERIFIED=1"
    "SCALPX_FLAT_POSITION_VERIFIED=1"
    "SCALPX_CONTROLLED_PAPER_GENERATED_ACK=$GENERATED_ACK"
    "SCALPX_CONTROLLED_PAPER_NO_BROKER_ACK=$NO_BROKER_ACK"
    "SCALPX_CONTROLLED_PAPER_FAMILY=$FAMILY"
    "SCALPX_CONTROLLED_PAPER_SIDE=$SIDE"
    "SCALPX_CONTROLLED_PAPER_BRANCH=$SIDE"
    "SCALPX_CONTROLLED_PAPER_ACTION=$ACTION"
    "SCALPX_CONTROLLED_PAPER_INSTRUMENT_TOKEN=$TOKEN"
    "SCALPX_CONTROLLED_PAPER_OPTION_SYMBOL=$SYMBOL"
    "SCALPX_CONTROLLED_PAPER_MAX_LOTS=1"
    "SCALPX_CONTROLLED_PAPER_LOTS=1"
    "SCALPX_CONTROLLED_PAPER_QTY_LOTS=1"
    "SCALPX_CONTROLLED_PAPER_MAX_EVENTS=1"
    "SCALPX_CONTROLLED_PAPER_STOP_AFTER_ONE=1"
    "SCALPX_ENABLE_LIVE=0"
    "SCALPX_REAL_LIVE_ALLOWED=0"
    "SCALPX_ALLOW_REAL_LIVE=0"
    "SCALPX_ALLOW_BROKER_ORDERS=0"
    "SCALPX_BROKER_ORDER_ENABLED=0"
    "MME_ENABLE_LIVE=0"
    "MME_ALLOW_LIVE_ORDER=0"
    "MME_ALLOW_BROKER_ORDERS=0"
)

nohup env \
  "${PAPER_COMMON_ENV[@]}" \
  "SCALPX_CONTROLLED_PAPER_SCOPE_ACK=$ROUTE_ACK" \
  "$PY" -m app.mme_scalpx.main \
    --service execution \
    --bootstrap-provider "$PROVIDER" \
    --skip-group-bootstrap \
  > "$ROOT/logs/paper_execution.log" \
  2>&1 < /dev/null &

EXEC_PID=$!

nohup env \
  "${PAPER_COMMON_ENV[@]}" \
  "SCALPX_CONTROLLED_PAPER_SCOPE_ACK=$ROUTE_ACK" \
  "$PY" -m app.mme_scalpx.main \
    --service risk \
    --bootstrap-provider "$PROVIDER" \
    --skip-group-bootstrap \
  > "$ROOT/logs/paper_risk.log" \
  2>&1 < /dev/null &

RISK_PID=$!

echo "execution_pid=$EXEC_PID"
echo "risk_pid=$RISK_PID"

PAPER_ACTIVE=1

wait_service_one execution "$EXEC_PID" || {
    tail -200 "$ROOT/logs/paper_execution.log" || true
    exit 33
}

wait_service_one risk "$RISK_PID" || {
    tail -200 "$ROOT/logs/paper_risk.log" || true
    exit 34
}

echo
echo "===== 9) WAIT PAPER RISK GATE ====="

RISK_OPEN=0

for attempt in $(seq 1 90); do
    VETO="$(
        redis-cli --raw HGET \
          state:risk veto_entries 2>/dev/null || true
    )"

    MAXLOTS="$(
        redis-cli --raw HGET \
          state:risk max_new_lots 2>/dev/null || true
    )"

    CPVETO="$(
        redis-cli --raw HGET \
          state:risk controlled_paper_entry_veto 2>/dev/null || true
    )"

    UPSTREAM="$(
        redis-cli --raw HGET \
          state:risk upstream_healthy 2>/dev/null || true
    )"

    STRHB="$(
        redis-cli --raw HGET \
          state:risk strategy_heartbeat_fresh 2>/dev/null || true
    )"

    EXEHB="$(
        redis-cli --raw HGET \
          state:risk execution_heartbeat_fresh 2>/dev/null || true
    )"

    echo "RISK_WAIT=$attempt veto=$VETO maxlots=$MAXLOTS cp_veto=$CPVETO upstream=$UPSTREAM strategy_hb=$STRHB execution_hb=$EXEHB"

    if [ "$VETO" = "0" ] &&
       [ "${MAXLOTS:-0}" -ge 1 ] &&
       [ "$CPVETO" = "0" ] &&
       [ "$UPSTREAM" = "1" ] &&
       [ "$STRHB" = "1" ] &&
       [ "$EXEHB" = "1" ]; then
        RISK_OPEN=1
        break
    fi

    kill -0 "$EXEC_PID" 2>/dev/null || {
        tail -200 "$ROOT/logs/paper_execution.log" || true
        exit 35
    }

    kill -0 "$RISK_PID" 2>/dev/null || {
        tail -200 "$ROOT/logs/paper_risk.log" || true
        exit 36
    }

    sleep 1
done

[ "$RISK_OPEN" = "1" ] || {
    echo "STOP_PAPER_RISK_GATE_NOT_OPEN"
    redis-cli --raw HGETALL state:risk || true
    exit 37
}

echo "PASS_PAPER_RISK_GATE_OPEN"

echo
echo "===== 10) SWITCH STRATEGY TO EXACT NATURAL PAPER MODE ====="

OLD_STRATEGY_PID="$(service_pid strategy)"

[ -n "$OLD_STRATEGY_PID" ] || {
    echo "STOP_OBSERVE_STRATEGY_PID_MISSING"
    exit 38
}

kill -TERM "$OLD_STRATEGY_PID"

for _ in $(seq 1 30); do
    kill -0 "$OLD_STRATEGY_PID" 2>/dev/null || break
    sleep 0.5
done

kill -0 "$OLD_STRATEGY_PID" 2>/dev/null && {
    echo "STOP_OBSERVE_STRATEGY_DID_NOT_EXIT"
    exit 39
}

PAPER_STRATEGY_ENV=(
    "${PAPER_COMMON_ENV[@]}"
    "SCALPX_CONTROLLED_PAPER_SCOPE_ACK=$GENERATED_ACK"
    "SCALPX_ENABLE_STRATEGY_OWNED_EXIT_MANAGER=1"
    "SCALPX_STRATEGY_EXIT_POLICY_ACK=$EXIT_POLICY_ACK"
    "SCALPX_STRATEGY_EXIT_SCOPE_ACK=$EXIT_SCOPE_ACK"
)

start_paper_strategy() {
    local ack_mode="$1"
    local scope_ack="$2"
    local log="$ROOT/logs/paper_strategy_${ack_mode}.log"

    nohup env \
      "${PAPER_COMMON_ENV[@]}" \
      "SCALPX_CONTROLLED_PAPER_SCOPE_ACK=$scope_ack" \
      "SCALPX_ENABLE_STRATEGY_OWNED_EXIT_MANAGER=1" \
      "SCALPX_STRATEGY_EXIT_POLICY_ACK=$EXIT_POLICY_ACK" \
      "SCALPX_STRATEGY_EXIT_SCOPE_ACK=$EXIT_SCOPE_ACK" \
      "$PY" -m app.mme_scalpx.main \
        --service strategy \
        --bootstrap-provider "$PROVIDER" \
        --skip-group-bootstrap \
      > "$log" 2>&1 < /dev/null &

    echo "$!"
}

PAPER_STRATEGY_PID="$(
    start_paper_strategy \
      generated_ack \
      "$GENERATED_ACK"
)"

wait_service_one strategy "$PAPER_STRATEGY_PID" || {
    tail -200 \
      "$ROOT/logs/paper_strategy_generated_ack.log" \
      || true
    exit 40
}

sleep 5

echo "paper_strategy_pid=$PAPER_STRATEGY_PID"
echo "paper_strategy_ack_mode=GENERATED_EXACT_SCOPE"
echo "PASS_EXACT_PAPER_STRATEGY_STARTED"

echo
echo "===== 11) WAIT NATURAL ENTRY ====="

ENTRY_SEEN=0
ACK_MODE="GENERATED_EXACT_SCOPE"

for elapsed in $(seq 1 "$ENTRY_TIMEOUT_SECONDS"); do
    HPOS="$(
        redis-cli --raw HGET \
          state:position:mme \
          has_position 2>/dev/null || true
    )"

    ORDER_NOW="$(
        stream_len orders:mme:stream
    )"

    LEDGER_NOW="$(
        stream_len trades:ledger:stream
    )"

    ORDER_DELTA=$(( ORDER_NOW - ORDER_BASE_LEN ))
    LEDGER_DELTA=$(( LEDGER_NOW - LEDGER_BASE_LEN ))

    if [ "$HPOS" = "1" ]; then
        ENTRY_SEEN=1
        echo "NATURAL_ENTRY_POSITION_OPEN elapsed=$elapsed order_delta=$ORDER_DELTA ledger_delta=$LEDGER_DELTA ack_mode=$ACK_MODE"
        break
    fi

    if [ "$elapsed" = "60" ] &&
       [ "$ORDER_DELTA" = "0" ] &&
       [ "$LEDGER_DELTA" = "0" ]; then

        echo "NO_ENTRY_WITH_GENERATED_ACK_SWITCHING_TO_PROJECTION_COMPAT_ACK"

        stop_service strategy

        PAPER_STRATEGY_PID="$(
            start_paper_strategy \
              projection_ack \
              "$NO_BROKER_ACK"
        )"

        wait_service_one strategy "$PAPER_STRATEGY_PID" || {
            tail -200 \
              "$ROOT/logs/paper_strategy_projection_ack.log" \
              || true
            exit 41
        }

        ACK_MODE="ACK_FOR_CONTROLLED_PROJECTION"
    fi

    kill -0 "$EXEC_PID" 2>/dev/null || {
        echo "STOP_EXECUTION_DIED_BEFORE_ENTRY"
        exit 42
    }

    kill -0 "$RISK_PID" 2>/dev/null || {
        echo "STOP_RISK_DIED_BEFORE_ENTRY"
        exit 43
    }

    kill -0 "$PAPER_STRATEGY_PID" 2>/dev/null || {
        echo "STOP_STRATEGY_DIED_BEFORE_ENTRY"
        exit 44
    }

    if [ $((elapsed % 10)) -eq 0 ]; then
        echo "ENTRY_WAIT elapsed=$elapsed order_delta=$ORDER_DELTA ledger_delta=$LEDGER_DELTA ack_mode=$ACK_MODE"
    fi

    sleep 1
done

[ "$ENTRY_SEEN" = "1" ] || {
    echo "CLASSIFICATION=REVIEW_R38VBBASE_NO_NATURAL_ENTRY_WITHIN_TIMEOUT_FLAT"
    exit 45
}

echo
echo "===== 12) VERIFY EXACT ONE-LOT ENTRY ====="

mapfile -t OPEN_POS < <(
    redis-cli --raw HMGET state:position:mme \
      has_position \
      position_side \
      qty_lots \
      qty_units \
      strategy_family_id \
      family_id \
      branch_id \
      entry_option_symbol \
      option_symbol \
      entry_option_token \
      option_token \
      instrument_token \
      avg_price \
      entry_price \
      entry_ts_ns \
      decision_id \
      broker_order_id \
      entry_mode
)

printf '%s\n' \
  "has_position=${OPEN_POS[0]:-}" \
  "position_side=${OPEN_POS[1]:-}" \
  "qty_lots=${OPEN_POS[2]:-}" \
  "qty_units=${OPEN_POS[3]:-}" \
  "strategy_family_id=${OPEN_POS[4]:-}" \
  "family_id=${OPEN_POS[5]:-}" \
  "branch_id=${OPEN_POS[6]:-}" \
  "entry_option_symbol=${OPEN_POS[7]:-}" \
  "option_symbol=${OPEN_POS[8]:-}" \
  "entry_option_token=${OPEN_POS[9]:-}" \
  "option_token=${OPEN_POS[10]:-}" \
  "instrument_token=${OPEN_POS[11]:-}" \
  "avg_price=${OPEN_POS[12]:-}" \
  "entry_price=${OPEN_POS[13]:-}" \
  "entry_ts_ns=${OPEN_POS[14]:-}" \
  "decision_id=${OPEN_POS[15]:-}" \
  "broker_order_id=${OPEN_POS[16]:-}" \
  "entry_mode=${OPEN_POS[17]:-}" \
  | tee "$ROOT/outputs/open_position.txt"

OPEN_FAMILY="${OPEN_POS[4]:-${OPEN_POS[5]:-}}"
OPEN_SYMBOL="${OPEN_POS[7]:-${OPEN_POS[8]:-}}"
OPEN_TOKEN="${OPEN_POS[9]:-${OPEN_POS[10]:-${OPEN_POS[11]:-}}}"

[ "${OPEN_POS[0]:-}" = "1" ] &&
[ "${OPEN_POS[2]:-}" = "1" ] &&
[ "${OPEN_POS[3]:-0}" -gt 0 ] &&
[ "$OPEN_FAMILY" = "$FAMILY" ] &&
[ "${OPEN_POS[6]:-}" = "$SIDE" ] &&
[ "$OPEN_SYMBOL" = "$SYMBOL" ] &&
[ "$OPEN_TOKEN" = "$TOKEN" ] || {
    echo "CRITICAL_OPEN_POSITION_SCOPE_MISMATCH"
    exit 46
}

case "${OPEN_POS[16]:-}" in
    R38KR-PAPER-*)
        ;;
    *)
        echo "CRITICAL_NON_PAPER_BROKER_ORDER_ID=${OPEN_POS[16]:-}"
        exit 47
        ;;
esac

echo "PASS_EXACT_ONE_LOT_PAPER_ENTRY"

echo
echo "===== 13) WAIT STRATEGY-OWNED TARGET/STOP/TIME EXIT ====="

EXIT_SEEN=0

for elapsed in $(seq 1 "$EXIT_TIMEOUT_SECONDS"); do
    if position_is_flat; then
        EXIT_SEEN=1
        echo "NATURAL_EXIT_FLAT elapsed=$elapsed"
        break
    fi

    CURRENT_LOTS="$(
        redis-cli --raw HGET \
          state:position:mme \
          qty_lots 2>/dev/null || true
    )"

    CURRENT_SYMBOL="$(
        redis-cli --raw HGET \
          state:position:mme \
          entry_option_symbol 2>/dev/null || true
    )"

    [ "${CURRENT_LOTS:-0}" = "1" ] || {
        echo "CRITICAL_POSITION_LOTS_CHANGED=$CURRENT_LOTS"
        exit 48
    }

    [ "${CURRENT_SYMBOL:-$SYMBOL}" = "$SYMBOL" ] || {
        echo "CRITICAL_POSITION_SYMBOL_CHANGED=$CURRENT_SYMBOL"
        exit 49
    }

    kill -0 "$EXEC_PID" 2>/dev/null || {
        echo "CRITICAL_EXECUTION_DIED_WITH_OPEN_POSITION"
        exit 50
    }

    kill -0 "$RISK_PID" 2>/dev/null || {
        echo "CRITICAL_RISK_DIED_WITH_OPEN_POSITION"
        exit 51
    }

    kill -0 "$PAPER_STRATEGY_PID" 2>/dev/null || {
        echo "CRITICAL_STRATEGY_DIED_WITH_OPEN_POSITION"
        exit 52
    }

    if [ $((elapsed % 10)) -eq 0 ]; then
        BID="$(
            redis-cli --raw HGET \
              state:position:mme last_bid 2>/dev/null || true
        )"

        echo "EXIT_WAIT elapsed=$elapsed lots=$CURRENT_LOTS symbol=$CURRENT_SYMBOL last_bid=$BID"
    fi

    sleep 1
done

[ "$EXIT_SEEN" = "1" ] || {
    echo "BLOCK_R38VBBASE_NATURAL_EXIT_TIMEOUT_POSITION_REMAINS_OPEN"
    echo "EXACT_PAPER_SERVICES_WILL_REMAIN_RUNNING=1"
    exit 53
}

echo
echo "===== 14) COMPLETE LIFECYCLE AUDIT ====="

ORDER_FINAL_LEN="$(
    stream_len orders:mme:stream
)"

LEDGER_FINAL_LEN="$(
    stream_len trades:ledger:stream
)"

ORDER_DELTA=$(( ORDER_FINAL_LEN - ORDER_BASE_LEN ))
LEDGER_DELTA=$(( LEDGER_FINAL_LEN - LEDGER_BASE_LEN ))

PNL_AFTER="$(
    redis-cli --raw HGET \
      state:position:mme \
      realized_pnl_day 2>/dev/null || true
)"

echo "order_delta=$ORDER_DELTA"
echo "ledger_delta=$LEDGER_DELTA"
echo "pnl_before=$PNL_BEFORE"
echo "pnl_after=$PNL_AFTER"

PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}" \
"$PY" - \
  "$DECISION_BASE_ID" \
  "$ORDER_BASE_ID" \
  "$LEDGER_BASE_ID" \
  "$ACK_BASE_ID" \
  "$FAMILY" \
  "$SIDE" \
  "$SYMBOL" \
  "$TOKEN" \
  "$ROOT/outputs/lifecycle_audit.json" <<'PY' | tee "$ROOT/outputs/lifecycle_audit.txt"
from __future__ import annotations

import json
from pathlib import Path
import sys

import redis


(
    decision_base,
    order_base,
    ledger_base,
    ack_base,
    family,
    side,
    symbol,
    token,
    output_path,
) = sys.argv[1:]

client = redis.Redis(
    host="127.0.0.1",
    port=6379,
    decode_responses=True,
)


def read_after(stream, last_id):
    rows = client.xread(
        {stream: last_id},
        count=10000,
        block=10,
    )

    result = []

    for _, messages in rows:
        for message_id, fields in messages:
            payload = {}

            raw_payload = fields.get(
                "payload_json"
            )

            if raw_payload:
                try:
                    parsed = json.loads(
                        raw_payload
                    )

                    if isinstance(parsed, dict):
                        payload = parsed
                except Exception:
                    pass

            metadata = payload.get(
                "metadata"
            )

            if not isinstance(
                metadata,
                dict,
            ):
                metadata = {}

            merged = {}

            merged.update(fields)
            merged.update(payload)

            for key, value in metadata.items():
                merged.setdefault(
                    key,
                    value,
                )

            merged["_stream_id"] = (
                message_id
            )

            result.append(merged)

    return result


decisions = read_after(
    "decisions:mme:stream",
    decision_base,
)

orders = read_after(
    "orders:mme:stream",
    order_base,
)

ledger = read_after(
    "trades:ledger:stream",
    ledger_base,
)

acks = read_after(
    "decisions:ack:stream",
    ack_base,
)


def text(row, *keys):
    for key in keys:
        value = row.get(key)

        if value is not None and str(
            value
        ).strip():
            return str(value).strip()

    return ""


def upper(row, *keys):
    return text(
        row,
        *keys,
    ).upper()


def identity_matches(row):
    row_family = upper(
        row,
        "strategy_family_id",
        "family_id",
        "doctrine_id",
    )

    row_side = upper(
        row,
        "branch_id",
        "side",
    )

    row_symbol = upper(
        row,
        "option_symbol",
        "entry_option_symbol",
        "symbol",
        "trading_symbol",
    )

    row_token = text(
        row,
        "option_token",
        "entry_option_token",
        "instrument_token",
        "instrument_key",
    )

    return bool(
        row_family == family
        and row_side == side
        and row_symbol == symbol
        and row_token == token
    )


entry_action = (
    "ENTER_CALL"
    if side == "CALL"
    else "ENTER_PUT"
)

entry_decisions = [
    row
    for row in decisions
    if upper(row, "action") == entry_action
    and identity_matches(row)
    and not text(
        row,
        "decision_id",
    ).startswith(
        "r38ga-risk-open-one-event-"
    )
]

exit_decisions = [
    row
    for row in decisions
    if upper(row, "action") == "EXIT"
    and upper(
        row,
        "position_effect",
    ) == "CLOSE"
    and identity_matches(row)
    and upper(
        row,
        "r38tmb1_strategy_owned_exit",
    )
    in {
        "1",
        "TRUE",
        "YES",
        "ON",
    }
]

valid_exit_reasons = {
    "TARGET_POINTS",
    "HARD_STOP_POINTS",
    "MAX_HOLD_SECONDS",
}

strategy_exit_decisions = [
    row
    for row in exit_decisions
    if upper(
        row,
        "reason",
        "reason_code",
    )
    in valid_exit_reasons
]

broker_order_ids = []

for collection in (
    orders,
    ledger,
    acks,
):
    for row in collection:
        order_id = text(
            row,
            "broker_order_id",
            "order_id",
        )

        if order_id:
            broker_order_ids.append(
                order_id
            )

paper_ids_only = bool(
    broker_order_ids
    and all(
        order_id.startswith(
            "R38KR-PAPER-"
        )
        for order_id in broker_order_ids
    )
)

dangerous_true = []

for collection_name, collection in (
    ("decisions", decisions),
    ("orders", orders),
    ("ledger", ledger),
    ("acks", acks),
):
    for row in collection:
        for key in (
            "real_live_allowed",
            "live_orders_allowed",
            "broker_live_order_allowed",
            "real_order_sent_shadow",
            "broker_calls_executed_shadow",
        ):
            if upper(
                row,
                key,
            ) in {
                "1",
                "TRUE",
                "YES",
                "ON",
            }:
                dangerous_true.append(
                    {
                        "collection":
                            collection_name,
                        "stream_id":
                            row.get(
                                "_stream_id"
                            ),
                        "key": key,
                    }
                )

# BEGIN R38VBBASE_ORDER_STREAM_SEMANTICS_V2
#
# The order stream contains four expected rows for one completed lifecycle:
#   1. Strategy projected controlled-paper intent.
#   2. Execution controlled-paper ORDER_INTENT.
#   3. Paper entry submission.
#   4. Paper exit submission.
#
# Only rows 3 and 4 represent submitted paper orders. The first two are
# fail-closed intent stages and must not be counted as additional fills.

def broker_id(row):
    return text(
        row,
        "broker_order_id",
        "order_id",
    )


def event_type(row):
    return upper(
        row,
        "event_type",
        "record_type",
        "stage",
        "status",
    )


def integer(row, *keys):
    value = text(row, *keys)

    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


projected_strategy_intents = [
    row
    for row in orders
    if upper(
        row,
        "reason",
        "reason_code",
    )
    == "R33I_PROJECTED_CONTROLLED_PAPER_ORDER_INTENT"
]

execution_order_intents = [
    row
    for row in orders
    if event_type(row) == "ORDER_INTENT"
    and upper(
        row,
        "reason",
        "reason_code",
    )
    == (
        "R38SG_CONTROLLED_PAPER_ORDER_INTENT_"
        "FROM_CONSUMED_ENTER_DECISION"
    )
]

entry_submitted_orders = [
    row
    for row in orders
    if event_type(row) == "ENTRY_ORDER_SUBMITTED"
    and upper(row, "action") == entry_action
]

exit_submitted_orders = [
    row
    for row in orders
    if event_type(row) == "EXIT_ORDER_SUBMITTED"
    and upper(row, "action") == "EXIT"
]

entry_fills = [
    row
    for row in ledger
    if event_type(row) == "ENTRY_FILL"
]

exit_fills = [
    row
    for row in ledger
    if event_type(row) == "EXIT_FILL"
]

unique_broker_order_ids = sorted(
    {
        order_id
        for order_id in broker_order_ids
        if order_id
    }
)

two_unique_paper_order_ids = bool(
    len(unique_broker_order_ids) == 2
    and all(
        order_id.startswith("R38KR-PAPER-")
        for order_id in unique_broker_order_ids
    )
)

order_fill_links_ok = bool(
    len(entry_submitted_orders) == 1
    and len(exit_submitted_orders) == 1
    and len(entry_fills) == 1
    and len(exit_fills) == 1
    and broker_id(entry_submitted_orders[0])
        == broker_id(entry_fills[0])
    and broker_id(exit_submitted_orders[0])
        == broker_id(exit_fills[0])
    and broker_id(entry_submitted_orders[0])
        != broker_id(exit_submitted_orders[0])
)

# R38VQ_EXECUTED_ENTRY_ANCHOR_AUDIT_V1:
# Strategy may publish repeated matching signal decisions while the
# execution global guard permits only one submitted and filled entry.
# Audit the uniquely executed decision chain, while proving every
# additional matching signal decision remained unexecuted.
entry_order_decision_id = (
    text(
        entry_submitted_orders[0],
        "decision_id",
    )
    if len(entry_submitted_orders) == 1
    else ""
)

entry_fill_decision_id = (
    text(
        entry_fills[0],
        "decision_id",
    )
    if len(entry_fills) == 1
    else ""
)

executed_entry_decisions = [
    row
    for row in entry_decisions
    if entry_order_decision_id
    and text(
        row,
        "decision_id",
    ) == entry_order_decision_id
]

unexecuted_entry_decisions = [
    row
    for row in entry_decisions
    if text(
        row,
        "decision_id",
    ) != entry_order_decision_id
]

entry_execution_decision_ids = {
    text(
        row,
        "decision_id",
    )
    for row in (
        entry_submitted_orders
        + entry_fills
    )
    if text(
        row,
        "decision_id",
    )
}

unexecuted_entry_decisions_safe = all(
    text(
        row,
        "decision_id",
    )
    not in entry_execution_decision_ids
    and not broker_id(row)
    for row in unexecuted_entry_decisions
)

decision_links_ok = bool(
    len(strategy_exit_decisions) == 1
    and len(entry_submitted_orders) == 1
    and len(exit_submitted_orders) == 1
    and len(entry_fills) == 1
    and len(exit_fills) == 1
    and bool(entry_order_decision_id)
    and entry_order_decision_id
        == entry_fill_decision_id
    and len(executed_entry_decisions) == 1
    and unexecuted_entry_decisions_safe
    and text(
        strategy_exit_decisions[0],
        "decision_id",
    )
        == text(
            exit_submitted_orders[0],
            "decision_id",
        )
        == text(
            exit_fills[0],
            "decision_id",
        )
)

quantity_contract_ok = bool(
    len(entry_submitted_orders) == 1
    and len(exit_submitted_orders) == 1
    and len(entry_fills) == 1
    and len(exit_fills) == 1
    and integer(
        entry_submitted_orders[0],
        "quantity",
        "qty_units",
    ) == 65
    and integer(
        exit_submitted_orders[0],
        "quantity",
        "qty_units",
    ) == 65
    and integer(
        entry_fills[0],
        "quantity",
        "qty_units",
    ) == 65
    and integer(
        exit_fills[0],
        "quantity",
        "qty_units",
    ) == 65
)

expanded_auxiliary_intents_safe = bool(
    len(orders) == 4
    and len(projected_strategy_intents) == 1
    and len(execution_order_intents) == 1
    and all(
        identity_matches(row)
        for row in (
            projected_strategy_intents
            + execution_order_intents
        )
    )
    and all(
        upper(
            row,
            "action",
            "order_action",
            "trade_action",
        )
        == entry_action
        for row in (
            projected_strategy_intents
            + execution_order_intents
        )
    )
    and all(
        not broker_id(row)
        for row in (
            projected_strategy_intents
            + execution_order_intents
        )
    )
)

compact_submitted_only_safe = bool(
    len(orders) == 2
    and len(projected_strategy_intents) == 0
    and len(execution_order_intents) == 0
    and len(entry_submitted_orders) == 1
    and len(exit_submitted_orders) == 1
)

auxiliary_intents_safe = bool(
    expanded_auxiliary_intents_safe
    or compact_submitted_only_safe
)

passed = bool(
    len(executed_entry_decisions) == 1
    and unexecuted_entry_decisions_safe
    and len(strategy_exit_decisions) == 1
    and auxiliary_intents_safe
    and len(entry_submitted_orders) == 1
    and len(exit_submitted_orders) == 1
    and len(ledger) == 2
    and len(entry_fills) == 1
    and len(exit_fills) == 1
    and two_unique_paper_order_ids
    and order_fill_links_ok
    and decision_links_ok
    and quantity_contract_ok
    and paper_ids_only
    and not dangerous_true
)
# END R38VBBASE_ORDER_STREAM_SEMANTICS_V2

classification = (
    "PASS_R38VBBASE_NATURAL_ONE_EVENT_COMPLETE_STRATEGY_EXIT_FLAT"
    if passed
    else
    "BLOCK_R38VBBASE_LIFECYCLE_EVIDENCE_MISMATCH"
)

report = {
    "classification":
        classification,
    "scope": {
        "family": family,
        "side": side,
        "symbol": symbol,
        "token": token,
    },
    "new_decision_count":
        len(decisions),
    "matching_entry_decision_count":
        len(entry_decisions),
    "executed_entry_decision_count":
        len(executed_entry_decisions),
    "unexecuted_entry_decision_count":
        len(unexecuted_entry_decisions),
    "unexecuted_entry_decisions_safe":
        unexecuted_entry_decisions_safe,
    "executed_entry_decision_ids": sorted(
        {
            text(
                row,
                "decision_id",
            )
            for row in executed_entry_decisions
            if text(
                row,
                "decision_id",
            )
        }
    ),
    "unexecuted_entry_decision_ids": sorted(
        {
            text(
                row,
                "decision_id",
            )
            for row in unexecuted_entry_decisions
            if text(
                row,
                "decision_id",
            )
        }
    ),
    "matching_strategy_exit_count":
        len(strategy_exit_decisions),
    "new_order_count":
        len(orders),
    "projected_strategy_intent_count":
        len(projected_strategy_intents),
    "execution_order_intent_count":
        len(execution_order_intents),
    "submitted_paper_order_count":
        (
            len(entry_submitted_orders)
            + len(exit_submitted_orders)
        ),
    "entry_submitted_order_count":
        len(entry_submitted_orders),
    "exit_submitted_order_count":
        len(exit_submitted_orders),
    "entry_fill_count":
        len(entry_fills),
    "exit_fill_count":
        len(exit_fills),
    "unique_paper_order_id_count":
        len(unique_broker_order_ids),
    "two_unique_paper_order_ids":
        two_unique_paper_order_ids,
    "auxiliary_intents_safe":
        auxiliary_intents_safe,
    "expanded_auxiliary_intents_safe":
        expanded_auxiliary_intents_safe,
    "compact_submitted_only_safe":
        compact_submitted_only_safe,
    "order_fill_links_ok":
        order_fill_links_ok,
    "decision_links_ok":
        decision_links_ok,
    "quantity_contract_ok":
        quantity_contract_ok,
    "new_ledger_count":
        len(ledger),
    "new_ack_count":
        len(acks),
    "broker_order_ids":
        broker_order_ids,
    "paper_order_ids_only":
        paper_ids_only,
    "dangerous_true":
        dangerous_true,
    "exit_reasons": [
        text(
            row,
            "reason",
            "reason_code",
        )
        for row
        in strategy_exit_decisions
    ],
    "entry_decisions":
        entry_decisions,
    "exit_decisions":
        strategy_exit_decisions,
    "orders":
        orders,
    "ledger":
        ledger,
}

Path(output_path).write_text(
    json.dumps(
        report,
        indent=2,
        sort_keys=True,
        default=str,
    )
    + "\n"
)

print(
    "CLASSIFICATION="
    + classification
)
print(
    "MATCHING_NATURAL_ENTRY_DECISIONS="
    + str(len(entry_decisions))
)
print(
    "EXECUTED_ENTRY_DECISIONS="
    + str(len(executed_entry_decisions))
)
print(
    "UNEXECUTED_ENTRY_DECISIONS="
    + str(len(unexecuted_entry_decisions))
)
print(
    "UNEXECUTED_ENTRY_DECISIONS_SAFE="
    + (
        "1"
        if unexecuted_entry_decisions_safe
        else "0"
    )
)
print(
    "EXECUTED_ENTRY_DECISION_IDS="
    + ",".join(
        report["executed_entry_decision_ids"]
    )
)
print(
    "MATCHING_STRATEGY_OWNED_EXITS="
    + str(
        len(strategy_exit_decisions)
    )
)
print(
    "NEW_ORDER_COUNT="
    + str(len(orders))
)
print(
    "NEW_LEDGER_COUNT="
    + str(len(ledger))
)
print(
    "PAPER_ORDER_IDS_ONLY="
    + (
        "1"
        if paper_ids_only
        else "0"
    )
)
print(
    "DANGEROUS_TRUE_COUNT="
    + str(len(dangerous_true))
)
print(
    "EXIT_REASONS="
    + ",".join(
        report["exit_reasons"]
    )
)

if not passed:
    raise SystemExit(20)
PY

grep -q \
  "CLASSIFICATION=PASS_R38VBBASE_NATURAL_ONE_EVENT_COMPLETE_STRATEGY_EXIT_FLAT" \
  "$ROOT/outputs/lifecycle_audit.txt"

position_is_flat || {
    echo "STOP_FINAL_POSITION_NOT_FLAT"
    exit 54
}

echo "PASS_COMPLETE_NATURAL_LIFECYCLE"

echo
echo "===== 15) STOP PAPER SERVICES AND RESTORE OBSERVE STRATEGY ====="

stop_service strategy
stop_service risk
stop_service execution

PAPER_ACTIVE=0

OBSERVE_STRATEGY_PID="$(
    start_observe_service strategy
)"

wait_service_one \
  strategy \
  "$OBSERVE_STRATEGY_PID" || {
    tail -200 \
      "$ROOT/logs/observe_strategy.log" \
      || true
    exit 55
}

sleep 10

for service in feeds features strategy; do
    count="$(count_service "$service")"
    echo "${service}_final_count=$count"

    [ "$count" = "1" ] || {
        echo "STOP_FINAL_OBSERVE_COUNT_${service^^}=$count"
        exit 56
    }
done

for service in risk execution; do
    count="$(count_service "$service")"
    echo "${service}_final_count=$count"

    [ "$count" = "0" ] || {
        echo "STOP_FINAL_${service^^}_COUNT=$count"
        exit 57
    }
done

position_is_flat || {
    echo "STOP_FINAL_POSITION_NOT_STRICT_FLAT"
    exit 58
}

echo "PASS_OBSERVE_ONLY_RESTORED"

echo
echo "===== 16) EVIDENCE BUNDLE ====="

ps -eo pid,ppid,etime,args |
grep -E \
  'app\.mme_scalpx\.main.*--service (feeds|features|strategy|risk|execution)' |
grep -v grep \
  > "$ROOT/outputs/final_processes.txt" \
  || true

redis-cli --raw HGETALL \
  state:position:mme \
  > "$ROOT/outputs/final_position.txt"

sha256sum \
  "$STRATEGY_SRC" \
  "$EXECUTION_SRC" \
  "$MANAGER_SRC" \
  "$RESOLVER_SRC" \
  "$INSTRUMENT_FILE" \
  > "$ROOT/outputs/source_sha256.txt"

cat > "$ROOT/SUMMARY.txt" <<EOF
CLASSIFICATION=PASS_R38VBBASE_NATURAL_ONE_EVENT_COMPLETE_STRATEGY_EXIT_FLAT
FAMILY=$FAMILY
SIDE=$SIDE
ACTION=$ACTION
SYMBOL=$SYMBOL
TOKEN=$TOKEN
GENERATED_ACK=$GENERATED_ACK
ENTRY_ACK_MODE=$ACK_MODE
ONE_LOT=1
MAX_ENTRY_EVENTS=1
NATURAL_REAL_OBSERVED_CANDIDATE=1
MANUAL_DECISION_XADD=0
FORCED_ENTRY=0
STRATEGY_OWNED_EXIT=1
TARGET_POINTS=5
HARD_STOP_POINTS=4
MAX_HOLD_SECONDS=300
POSITION_EFFECT=CLOSE
NEW_ORDER_COUNT=$ORDER_DELTA
NEW_LEDGER_COUNT=$LEDGER_DELTA
PNL_BEFORE=$PNL_BEFORE
PNL_AFTER=$PNL_AFTER
REAL_BROKER_ORDER=0
PAPER_ORDER_ONLY=1
RISK_FINAL=0
EXECUTION_FINAL=0
OBSERVE_ONLY_RESTORED=1
FINAL_POSITION=FLAT
NEXT=REVIEW_R38VBBASE_PAIRED_PNL_AND_REPEAT_NATURAL_PAPER_EVENTS
EOF

cat "$ROOT/SUMMARY.txt"

tar -czf "$ARCHIVE" \
  -C run/proofs \
  "$TAG"

sha256sum "$ARCHIVE" |
tee "${ARCHIVE}.sha256"

SUCCESS=1
trap - EXIT INT TERM

echo
echo "===== PASS ====="
echo "CLASSIFICATION=PASS_R38VBBASE_NATURAL_ONE_EVENT_COMPLETE_STRATEGY_EXIT_FLAT"
echo "NATURAL_ENTRY=PASS"
echo "STRATEGY_OWNED_EXIT=PASS"
echo "POSITION_EFFECT=CLOSE"
echo "FORCED_ENTRY=0"
echo "FORCED_EXIT=0"
echo "REAL_BROKER_ORDER=0"
echo "OBSERVE_ONLY_RESTORED=1"
echo "RISK_FINAL=0"
echo "EXECUTION_FINAL=0"
echo "FINAL_POSITION=FLAT"
echo "ROOT=$ROOT"
echo "BUNDLE=$ARCHIVE"
echo "SHA=${ARCHIVE}.sha256"
