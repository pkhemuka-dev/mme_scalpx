#!/usr/bin/env bash
set +e

ROOT="/home/Lenovo/scalpx/projects/mme_scalpx"
cd "$ROOT" || exit 2

TAG="${1:?tag required}"
MODE="${2:-full}"
OUTDIR="run/live_capture/${TAG}"
PROOF="run/proofs/${TAG}.json"
AUDIT="run/audits/${TAG}_audit.json"
MILESTONE="docs/milestones/${TAG}.md"
HANDOFF="run/handoffs/${TAG}_handoff.md"
SUMMARY="$OUTDIR/streams_summary.tsv"

mkdir -p "$OUTDIR" run/proofs run/audits docs/milestones run/handoffs

pcnt() {
  (pgrep -af "$1" 2>/dev/null || true) | grep -v grep | wc -l | tr -d ' '
}

ORD0="$(redis-cli XLEN orders:mme:stream 2>/dev/null || echo 999)"
RISK0="$(redis-cli XLEN risk:mme:stream 2>/dev/null || echo 999)"
EXEC0="$(redis-cli XLEN execution:mme:stream 2>/dev/null || echo 999)"
RP0="$(pcnt 'app\.mme_scalpx\.main --service risk')"
EP0="$(pcnt 'app\.mme_scalpx\.main --service execution')"

if [ "$ORD0" != "0" ] || [ "$RISK0" != "0" ] || [ "$EXEC0" != "0" ] || [ "$RP0" != "0" ] || [ "$EP0" != "0" ]; then
  CLASSIFICATION="BLOCKED_PSEAL_SAFETY_NOT_CLEAN_NO_ORDER"
  cat > "$PROOF" <<EOF
{
  "tag": "$TAG",
  "classification": "$CLASSIFICATION",
  "mode": "$MODE",
  "read_only": true,
  "service_start_attempted": false,
  "service_stop_attempted": false,
  "process_kill_attempted": false,
  "redis_delete_attempted": false,
  "risk_start_attempted": false,
  "execution_start_attempted": false,
  "order_attempted": false,
  "safety_before": {
    "orders": "$ORD0",
    "risk": "$RISK0",
    "execution": "$EXEC0",
    "risk_pids": "$RP0",
    "execution_pids": "$EP0"
  }
}
EOF
  cp "$PROOF" "$AUDIT"
  cat "$PROOF"
  exit 2
fi

printf "label\tstream\txlen\tlines\tbytes\tsha256\tpath\n" > "$SUMMARY"

export_stream() {
  label="$1"
  stream="$2"
  path="$OUTDIR/${label}.redisraw.gz"
  err="$OUTDIR/${label}.err"

  if [ "$MODE" = "smoke" ]; then
    redis-cli --raw XRANGE "$stream" - + COUNT 25 2>"$err" | gzip -c > "$path"
  else
    redis-cli --raw XRANGE "$stream" - + 2>"$err" | gzip -c > "$path"
  fi

  xlen="$(redis-cli XLEN "$stream" 2>/dev/null || echo 0)"
  lines="$(gzip -cd "$path" 2>/dev/null | wc -l | tr -d ' ')"
  bytes="$(stat -c%s "$path" 2>/dev/null || echo 0)"
  sha="$(sha256sum "$path" 2>/dev/null | awk '{print $1}')"

  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\n" "$label" "$stream" "$xlen" "$lines" "$bytes" "$sha" "$path" >> "$SUMMARY"
}

export_stream fut_zerodha ticks:mme:fut:zerodha:stream
export_stream fut_dhan ticks:mme:fut:dhan:stream
export_stream opt_selected_zerodha ticks:mme:opt:selected:zerodha:stream
export_stream opt_selected_dhan ticks:mme:opt:selected:dhan:stream
export_stream opt_context_dhan ticks:mme:opt:context:dhan:stream
export_stream features features:mme:stream
export_stream decisions decisions:mme:stream
export_stream errors system:errors:stream

ORD1="$(redis-cli XLEN orders:mme:stream 2>/dev/null || echo 999)"
RISK1="$(redis-cli XLEN risk:mme:stream 2>/dev/null || echo 999)"
EXEC1="$(redis-cli XLEN execution:mme:stream 2>/dev/null || echo 999)"
RP1="$(pcnt 'app\.mme_scalpx\.main --service risk')"
EP1="$(pcnt 'app\.mme_scalpx\.main --service execution')"

if [ "$ORD1" = "0" ] && [ "$RISK1" = "0" ] && [ "$EXEC1" = "0" ] && [ "$RP1" = "0" ] && [ "$EP1" = "0" ]; then
  CLASSIFICATION="PASS_PSEAL_DETACHED_EXPORT_WRITTEN_NO_ORDER"
else
  CLASSIFICATION="REVIEW_PSEAL_SAFETY_CHANGED_NO_ORDER"
fi

cat > "$PROOF" <<EOF
{
  "tag": "$TAG",
  "classification": "$CLASSIFICATION",
  "mode": "$MODE",
  "read_only": true,
  "service_start_attempted": false,
  "service_stop_attempted": false,
  "process_kill_attempted": false,
  "redis_delete_attempted": false,
  "risk_start_attempted": false,
  "execution_start_attempted": false,
  "order_attempted": false,
  "outdir": "$OUTDIR",
  "streams_summary_tsv": "$SUMMARY",
  "safety_before": {
    "orders": "$ORD0",
    "risk": "$RISK0",
    "execution": "$EXEC0",
    "risk_pids": "$RP0",
    "execution_pids": "$EP0"
  },
  "safety_after": {
    "orders": "$ORD1",
    "risk": "$RISK1",
    "execution": "$EXEC1",
    "risk_pids": "$RP1",
    "execution_pids": "$EP1"
  }
}
EOF

cp "$PROOF" "$AUDIT"

cat > "$MILESTONE" <<EOF
# $TAG

Classification: **$CLASSIFICATION**

Detached pseal export completed.

No service start.  
No service stop.  
No process kill.  
No Redis delete.  
No risk start.  
No execution start.  
No order.

Proof: \`$PROOF\`  
Audit: \`$AUDIT\`  
Summary: \`$SUMMARY\`
EOF

cp "$MILESTONE" "$HANDOFF"
cat "$PROOF"
