#!/usr/bin/env bash
cd /home/Lenovo/scalpx/projects/mme_scalpx
set +e

BATCH="R38_DOCTOR_COMPACT_PREFLIGHT_NO_START_NO_ORDER"
TS="$(date +%Y%m%d_%H%M%S)"
TAG="${BATCH}_${TS}"
OUT="run/proofs/${TAG}"
mkdir -p "$OUT" run/evidence_bundles
REPORT="$OUT/${TAG}_report.txt"

{
echo "===== ${TAG} ====="
date -Is
pwd
hostname
echo "SAFETY=READ_ONLY_NO_PATCH_NO_START_NO_XADD_NO_ORDER_NO_REAL_BROKER"

echo
echo "===== PROCESS ====="
ps -eo pid,ppid,pcpu,pmem,lstart,etime,cmd | grep -E 'redis-server|python -m app\.mme_scalpx\.main|NEXT_MARKET_SESSION_R38RN|R38QW_SHORT_LIVE_PAPER|kite|dhan' | grep -v grep || true

LEFT="$(ps -eo pid=,cmd= | grep -E 'python -m app\.mme_scalpx\.main|NEXT_MARKET_SESSION_R38RN|R38QW_SHORT_LIVE_PAPER' | grep -v grep || true)"
if [ -n "$LEFT" ]; then RUNTIME_ACTIVE=1; else RUNTIME_ACTIVE=0; fi
echo "runtime_active=$RUNTIME_ACTIVE"

echo
echo "===== STREAMS ====="
DOWNSTREAM_ZERO=1
for k in decisions:mme:stream features:mme:stream orders:mme:stream risk:mme:stream execution:mme:stream trades:mme:stream trades:ledger:stream; do
  v="$(redis-cli --raw XLEN "$k" 2>/dev/null || echo 0)"
  printf '%-30s %s\n' "$k" "$v"
  case "$k" in
    orders:mme:stream|risk:mme:stream|execution:mme:stream|trades:mme:stream|trades:ledger:stream)
      [ "$v" = "0" ] || DOWNSTREAM_ZERO=0
      ;;
  esac
done
echo "downstream_zero=$DOWNSTREAM_ZERO"

echo
echo "===== COMPACT DOCTOR ====="
RUNTIME_ACTIVE="$RUNTIME_ACTIVE" DOWNSTREAM_ZERO="$DOWNSTREAM_ZERO" .venv/bin/python - <<'PY'
import json, os, redis, time

r = redis.Redis(decode_responses=True)

def latest_payload(stream):
    rows = r.xrevrange(stream, count=1)
    if not rows:
        return "", {}, {}
    mid, fields = rows[0]
    payload = {}
    for key in ("payload_json", "payload", "decision_json", "consumer_view_json"):
        raw = fields.get(key)
        if raw:
            try:
                payload = json.loads(raw)
                break
            except Exception:
                pass
    if not payload:
        payload = dict(fields)
    return mid, fields, payload

def parse_maybe_json(x):
    if isinstance(x, str):
        try:
            return json.loads(x)
        except Exception:
            return {}
    return x if isinstance(x, dict) else {}

fid, ffields, fpayload = latest_payload("features:mme:stream")
did, dfields, dpayload = latest_payload("decisions:mme:stream")

cv = parse_maybe_json(fpayload.get("consumer_view_json")) or fpayload
provider_runtime = cv.get("provider_runtime") or {}
stage = cv.get("stage_flags") or {}

safe_to_consume = cv.get("safe_to_consume", ffields.get("safe_to_consume"))
data_valid = cv.get("data_valid", ffields.get("data_valid"))
warmup_complete = cv.get("warmup_complete", ffields.get("warmup_complete"))
provider_ready_classic = cv.get("provider_ready_classic", stage.get("provider_ready_classic"))
provider_ready_miso = cv.get("provider_ready_miso", stage.get("provider_ready_miso"))

fut_status = provider_runtime.get("futures_marketdata_status") or provider_runtime.get("futures_provider_status")
opt_status = provider_runtime.get("selected_option_marketdata_status") or provider_runtime.get("selected_option_provider_status")
exec_status = provider_runtime.get("execution_primary_status") or provider_runtime.get("execution_provider_status")
block_reason = provider_runtime.get("provider_runtime_block_reason") or cv.get("reason")

action = dpayload.get("action") or cv.get("action") or dfields.get("action")
reason = dpayload.get("reason") or cv.get("reason") or dfields.get("reason")
hold_only = dpayload.get("hold_only", cv.get("hold_only"))

def b(x):
    if isinstance(x, bool): return x
    if isinstance(x, (int, float)): return bool(x)
    if isinstance(x, str): return x.lower() in ("1", "true", "yes", "y")
    return False

runtime_active = os.environ.get("RUNTIME_ACTIVE") == "1"
downstream_zero = os.environ.get("DOWNSTREAM_ZERO") == "1"
data_ok = b(data_valid)
classic_ok = b(provider_ready_classic)
miso_ok = b(provider_ready_miso)
safe_ok = b(safe_to_consume)
warmup_ok = b(warmup_complete)

print(f"latest_feature_id={fid}")
print(f"latest_decision_id={did}")
print(f"runtime_active={int(runtime_active)}")
print(f"downstream_zero={int(downstream_zero)}")
print(f"safe_to_consume={safe_to_consume}")
print(f"data_valid={data_valid}")
print(f"warmup_complete={warmup_complete}")
print(f"provider_ready_classic={provider_ready_classic}")
print(f"provider_ready_miso={provider_ready_miso}")
print(f"futures_status={fut_status}")
print(f"selected_option_status={opt_status}")
print(f"execution_status={exec_status}")
print(f"latest_action={action}")
print(f"latest_reason={reason}")
print(f"hold_only={hold_only}")
print(f"provider_block_reason={block_reason}")

if runtime_active or not downstream_zero:
    status = "RED_RUNTIME_OR_DOWNSTREAM_UNSAFE"
    next_action = "RUN preflight_stop THEN preflight_bundle"
elif (not data_ok) or (not classic_ok and not miso_ok):
    status = "AMBER_LOGIN_PROVIDER_FEED_BLOCKER"
    next_action = "FIX_LOGIN_PROVIDER_FEED_FIRST; DO_NOT_START_RUNTIME"
elif str(action).startswith("ENTER"):
    status = "GREEN_READY_FOR_PREFLIGHT_ENTER_SEEN"
    next_action = "RUN preflight_start; THEN ASK_APPROVAL_FOR_ONE_CONTROLLED_PAPER"
elif str(action) == "HOLD":
    status = "AMBER_SIGNAL_NOT_AVAILABLE"
    next_action = "SYSTEM_HEALTH_CHECK_OK_BUT_NO_ENTER; WAIT_OR_OBSERVE"
else:
    status = "GREEN_READY_FOR_PREFLIGHT"
    next_action = "RUN preflight_start"

print(f"DOCTOR_STATUS={status}")
print(f"NEXT_ACTION={next_action}")
PY

echo
echo "===== CLASSIFICATION ====="
echo "R38_DOCTOR_COMPACT_PREFLIGHT_DONE_NO_START_NO_ORDER"

} | tee "$REPORT"

tar -czf "run/evidence_bundles/${TAG}.tar.gz" "$OUT"
sha256sum "run/evidence_bundles/${TAG}.tar.gz" > "run/evidence_bundles/${TAG}.tar.gz.sha256"

echo "REPORT=$REPORT"
echo "BUNDLE=run/evidence_bundles/${TAG}.tar.gz"
echo "SHA=run/evidence_bundles/${TAG}.tar.gz.sha256"
