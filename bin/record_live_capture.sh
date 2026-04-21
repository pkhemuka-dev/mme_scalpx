#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/Lenovo/scalpx/projects/mme_scalpx"
cd "$ROOT"

TS="$(date +%Y%m%d_%H%M%S)"
OUT_DIR="run/proofs/live_capture_${TS}"
PID_FILE="run/pids/live_capture.pid"
LOG_FILE="${OUT_DIR}/collector.log"

mkdir -p "$OUT_DIR"/streams "$OUT_DIR"/hashes "$OUT_DIR"/health

echo "$$" > "$PID_FILE"

touch \
  "$OUT_DIR/streams/features_mme_stream.txt" \
  "$OUT_DIR/streams/decisions_mme_stream.txt" \
  "$OUT_DIR/streams/decisions_ack_stream.txt" \
  "$OUT_DIR/streams/orders_mme_stream.txt" \
  "$OUT_DIR/streams/trades_ledger_stream.txt" \
  "$OUT_DIR/streams/system_health_stream.txt" \
  "$OUT_DIR/streams/system_errors_stream.txt"

touch \
  "$OUT_DIR/hashes/state_execution.txt" \
  "$OUT_DIR/hashes/state_position_mme.txt" \
  "$OUT_DIR/hashes/state_risk.txt" \
  "$OUT_DIR/hashes/state_report.txt" \
  "$OUT_DIR/hashes/state_runtime.txt"

touch \
  "$OUT_DIR/health/health_feeds.txt" \
  "$OUT_DIR/health/health_features.txt" \
  "$OUT_DIR/health/health_strategy.txt" \
  "$OUT_DIR/health/health_risk.txt" \
  "$OUT_DIR/health/health_execution.txt" \
  "$OUT_DIR/health/health_monitor.txt" \
  "$OUT_DIR/health/health_report.txt"

echo "capture_started ts=${TS} out_dir=${OUT_DIR}" | tee -a "$LOG_FILE"

LAST_FEATURES='$'
LAST_DECISIONS='$'
LAST_ACKS='$'
LAST_ORDERS='$'
LAST_LEDGER='$'
LAST_SYS_HEALTH='$'
LAST_SYS_ERRORS='$'

snapshot_hashes() {
  {
    echo "===== $(date --iso-8601=seconds) ====="
    redis-cli HGETALL state:execution
    echo
  } >> "$OUT_DIR/hashes/state_execution.txt"

  {
    echo "===== $(date --iso-8601=seconds) ====="
    redis-cli HGETALL state:position:mme
    echo
  } >> "$OUT_DIR/hashes/state_position_mme.txt"

  {
    echo "===== $(date --iso-8601=seconds) ====="
    redis-cli HGETALL state:risk
    echo
  } >> "$OUT_DIR/hashes/state_risk.txt"

  {
    echo "===== $(date --iso-8601=seconds) ====="
    redis-cli HGETALL state:report
    echo
  } >> "$OUT_DIR/hashes/state_report.txt"

  {
    echo "===== $(date --iso-8601=seconds) ====="
    redis-cli HGETALL state:runtime
    echo
  } >> "$OUT_DIR/hashes/state_runtime.txt"
}

snapshot_health() {
  {
    echo "===== $(date --iso-8601=seconds) ====="
    redis-cli HGETALL health:feeds
    echo
  } >> "$OUT_DIR/health/health_feeds.txt"

  {
    echo "===== $(date --iso-8601=seconds) ====="
    redis-cli HGETALL health:features
    echo
  } >> "$OUT_DIR/health/health_features.txt"

  {
    echo "===== $(date --iso-8601=seconds) ====="
    redis-cli HGETALL health:strategy
    echo
  } >> "$OUT_DIR/health/health_strategy.txt"

  {
    echo "===== $(date --iso-8601=seconds) ====="
    redis-cli HGETALL health:risk
    echo
  } >> "$OUT_DIR/health/health_risk.txt"

  {
    echo "===== $(date --iso-8601=seconds) ====="
    redis-cli HGETALL health:execution
    echo
  } >> "$OUT_DIR/health/health_execution.txt"

  {
    echo "===== $(date --iso-8601=seconds) ====="
    redis-cli HGETALL health:monitor
    echo
  } >> "$OUT_DIR/health/health_monitor.txt"

  {
    echo "===== $(date --iso-8601=seconds) ====="
    redis-cli HGETALL health:report
    echo
  } >> "$OUT_DIR/health/health_report.txt"
}

append_stream_range() {
  local stream="$1"
  local last_id="$2"
  local outfile="$3"

  local data
  data="$(redis-cli --raw XRANGE "$stream" "($last_id" + COUNT 500 || true)"
  if [[ -n "$data" ]]; then
    {
      echo "===== $(date --iso-8601=seconds) stream=${stream} from=${last_id} ====="
      echo "$data"
      echo
    } >> "$outfile"

    local new_last
    new_last="$(echo "$data" | awk 'NF{print $1}' | tail -n 1)"
    if [[ -n "$new_last" ]]; then
      echo "$new_last"
      return 0
    fi
  fi

  echo "$last_id"
}

trap 'echo "capture_stopping ts=$(date --iso-8601=seconds)" | tee -a "$LOG_FILE"; rm -f "$PID_FILE"; exit 0' INT TERM

ITER=0
while true; do
  LAST_FEATURES="$(append_stream_range "features:mme:stream" "$LAST_FEATURES" "$OUT_DIR/streams/features_mme_stream.txt")"
  LAST_DECISIONS="$(append_stream_range "decisions:mme:stream" "$LAST_DECISIONS" "$OUT_DIR/streams/decisions_mme_stream.txt")"
  LAST_ACKS="$(append_stream_range "decisions:ack:stream" "$LAST_ACKS" "$OUT_DIR/streams/decisions_ack_stream.txt")"
  LAST_ORDERS="$(append_stream_range "orders:mme:stream" "$LAST_ORDERS" "$OUT_DIR/streams/orders_mme_stream.txt")"
  LAST_LEDGER="$(append_stream_range "trades:ledger:stream" "$LAST_LEDGER" "$OUT_DIR/streams/trades_ledger_stream.txt")"
  LAST_SYS_HEALTH="$(append_stream_range "system:health:stream" "$LAST_SYS_HEALTH" "$OUT_DIR/streams/system_health_stream.txt")"
  LAST_SYS_ERRORS="$(append_stream_range "system:errors:stream" "$LAST_SYS_ERRORS" "$OUT_DIR/streams/system_errors_stream.txt")"

  if (( ITER % 2 == 0 )); then
    snapshot_hashes
    snapshot_health
  fi

  if (( ITER % 30 == 0 )); then
    echo "capture_heartbeat ts=$(date --iso-8601=seconds) iter=${ITER} out_dir=${OUT_DIR}" >> "$LOG_FILE"
  fi

  ITER=$((ITER + 1))
  sleep 1
done
