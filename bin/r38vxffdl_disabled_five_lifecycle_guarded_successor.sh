#!/usr/bin/env bash
set -Eeuo pipefail

cd /home/Lenovo/scalpx/projects/mme_scalpx || exit 1

MODE="FRIDAY_FIVE_LIFECYCLE_GUARDED_SUCCESSOR_R3"
SUCCESSOR_ENABLED_DEFAULT=0
MAX_LIFECYCLES=5
MAX_LOTS=1
MAX_POSITIONS=1
MAX_CONSECUTIVE_FULL_STOP_LOSSES=2
MAX_CUMULATIVE_LOSS_POINTS=-8
FRESH_AUTHORIZATION_PER_LIFECYCLE=1
RETRY_ALLOWED=0
REPLACEMENT_ALLOWED=0
MANDATORY_BROKER_AND_LOCAL_FLAT_BETWEEN_TRADES=1

SUPERVISOR="bin/r38vxffds_friday_five_lifecycle_supervisor_successor.sh"
RUNNER="bin/r38vxffdp_current_one_event_runner_successor.sh"
EXPECTED_SUPERVISOR_SHA="2956721162d275ec4eca9d8c96fabc82f9a7233621a986dbbb219cda22d07196"
EXPECTED_RUNNER_SHA="80284a7b109b65850ad7905d30ec649e9c3c9363c9380c0886ce066e23b9f7a3"

OUT="${R38VXFFDM_OUT:-run/proofs/R38VXFFDM_DISABLED_GUARD_SELFTEST_$(TZ=Asia/Kolkata date +%Y%m%d_%H%M%S)}"
AUTH_SEEN_FILE="$OUT/guard_seen_authorizations.txt"

mkdir -p "$OUT"
touch "$AUTH_SEEN_FILE"

die()
{
    echo "GUARD_RESULT=BLOCK"
    echo "GUARD_REASON=$1"
    exit 1
}

sha_file()
{
    sha256sum "$1" 2>/dev/null | awk '{print $1}'
}

check_identity()
{
    [ "$(sha_file "$SUPERVISOR")" = "$EXPECTED_SUPERVISOR_SHA" ] || die "SUPERVISOR_HASH_DRIFT"
    [ "$(sha_file "$RUNNER")" = "$EXPECTED_RUNNER_SHA" ] || die "RUNNER_HASH_DRIFT"
}

authorization_seen()
{
    local auth="$1"
    grep -Fxq "$auth" "$AUTH_SEEN_FILE" 2>/dev/null
}

remember_authorization()
{
    local auth="$1"
    printf '%s\n' "$auth" >> "$AUTH_SEEN_FILE"
}

guard_lifecycle()
{
    local cycle="$1"
    local lots="$2"
    local positions="$3"
    local local_flat="$4"
    local broker_flat="$5"
    local active_orders="$6"
    local authorization_id="$7"
    local consecutive_full_stop_losses="$8"
    local cumulative_loss_points="$9"

    [ "$cycle" -ge 1 ] && [ "$cycle" -le "$MAX_LIFECYCLES" ] || die "MAX_LIFECYCLES_EXCEEDED"
    [ "$lots" -le "$MAX_LOTS" ] || die "MAX_LOTS_EXCEEDED"
    [ "$positions" -le "$MAX_POSITIONS" ] || die "MAX_POSITIONS_EXCEEDED"
    [ "$local_flat" = "1" ] || die "LOCAL_NOT_FLAT_BETWEEN_TRADES"
    [ "$broker_flat" = "1" ] || die "BROKER_NOT_FLAT_BETWEEN_TRADES"
    [ "$active_orders" = "0" ] || die "ACTIVE_ORDER_PRESENT_BETWEEN_TRADES"
    [ -n "$authorization_id" ] || die "FRESH_AUTHORIZATION_MISSING"

    authorization_seen "$authorization_id" && die "AUTHORIZATION_REUSE_BLOCKED"
    remember_authorization "$authorization_id"

    [ "$consecutive_full_stop_losses" -lt "$MAX_CONSECUTIVE_FULL_STOP_LOSSES" ] ||
        die "MAX_CONSECUTIVE_FULL_STOP_LOSSES_REACHED"

    awk -v value="$cumulative_loss_points" -v limit="$MAX_CUMULATIVE_LOSS_POINTS" 'BEGIN { exit !(value <= limit) }' &&
        die "MAX_CUMULATIVE_LOSS_POINTS_REACHED"

    echo "GUARD_RESULT=ALLOW"
    echo "GUARD_REASON=PASS"
}

selftest_case()
{
    local name="$1"
    local expected="$2"
    shift 2

    set +e
    OUTPUT="$(guard_lifecycle "$@" 2>&1)"
    RC=$?
    set -e

    echo "SELFTEST_CASE=$name"
    echo "$OUTPUT"

    if [ "$expected" = "ALLOW" ]; then
        [ "$RC" -eq 0 ] || return 1
        echo "$OUTPUT" | grep -q 'GUARD_RESULT=ALLOW' || return 1
    else
        [ "$RC" -ne 0 ] || return 1
        echo "$OUTPUT" | grep -q "GUARD_REASON=$expected" || return 1
    fi
}

if [ "${1:-}" = "--selftest" ]; then
    check_identity

    : > "$AUTH_SEEN_FILE"
    selftest_case allow_cycle_1 ALLOW 1 1 1 1 1 0 AUTH-1 0 0
    selftest_case allow_cycle_2 ALLOW 2 1 1 1 1 0 AUTH-2 1 -4
    selftest_case block_auth_reuse AUTHORIZATION_REUSE_BLOCKED 3 1 1 1 1 0 AUTH-2 0 0

    : > "$AUTH_SEEN_FILE"
    selftest_case block_max_lifecycles MAX_LIFECYCLES_EXCEEDED 6 1 1 1 1 0 AUTH-6 0 0
    selftest_case block_max_lots MAX_LOTS_EXCEEDED 1 2 1 1 1 0 AUTH-7 0 0
    selftest_case block_max_positions MAX_POSITIONS_EXCEEDED 1 1 2 1 1 0 AUTH-8 0 0
    selftest_case block_local_nonflat LOCAL_NOT_FLAT_BETWEEN_TRADES 1 1 1 0 1 0 AUTH-9 0 0
    selftest_case block_broker_nonflat BROKER_NOT_FLAT_BETWEEN_TRADES 1 1 1 1 0 0 AUTH-10 0 0
    selftest_case block_active_order ACTIVE_ORDER_PRESENT_BETWEEN_TRADES 1 1 1 1 1 1 AUTH-11 0 0
    selftest_case block_missing_auth FRESH_AUTHORIZATION_MISSING 1 1 1 1 1 0 "" 0 0
    selftest_case block_two_full_stop_losses MAX_CONSECUTIVE_FULL_STOP_LOSSES_REACHED 1 1 1 1 1 0 AUTH-12 2 -4
    selftest_case block_minus_8 MAX_CUMULATIVE_LOSS_POINTS_REACHED 1 1 1 1 1 0 AUTH-13 0 -8

    echo "SELFTEST_CLASSIFICATION=PASS_R38VXFFDM_DISABLED_FIVE_LIFECYCLE_GUARD_SUCCESSOR_R2"
    echo "MAX_LIFECYCLES=5"
    echo "MAX_LOTS=1"
    echo "MAX_POSITIONS=1"
    echo "MAX_CONSECUTIVE_FULL_STOP_LOSSES=2"
    echo "MAX_CUMULATIVE_LOSS_POINTS=-8"
    echo "FRESH_AUTHORIZATION_PER_LIFECYCLE=1"
    echo "AUTHORIZATION_REUSE_BLOCKED=1"
    echo "RETRY_ALLOWED=0"
    echo "REPLACEMENT_ALLOWED=0"
    echo "MANDATORY_BROKER_AND_LOCAL_FLAT_BETWEEN_TRADES=1"
    exit 0
fi

if [ "${1:-}" = "--check" ]; then
    [ "${R38VXFFDM_ENABLE_MARKET_SESSION_GUARD:-0}" = "1" ] || die "MARKET_SESSION_GUARD_NOT_EXPLICITLY_ENABLED"
    check_identity
    shift
    [ "$#" -eq 9 ] || die "INVALID_RUNTIME_ARGUMENT_COUNT"
    guard_lifecycle "$@"
    exit 0
fi

echo "FINAL_CLASSIFICATION=BLOCK_SUCCESSOR_DISABLED_BY_DEFAULT"
echo "REASON=THIS_SUCCESSOR_REQUIRES_A_SEPARATE_MARKET_SESSION_AUTHORIZATION"
echo "PAPER_STARTED=0"
echo "LIVE_STARTED=0"
exit 1
