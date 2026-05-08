#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Controlled paper enablement from existing 25V/25W PASS — V2 safe version
#
# This script DOES NOT allow real live.
# It requires explicit operator env approval.
# It validates selected family/side/qty before provider/position checks.
# It uses local validated variables in all YAML/JSON writes.
# ============================================================================

PROJECT_ROOT="${PROJECT_ROOT:-/home/Lenovo/scalpx/projects/mme_scalpx}"
cd "$PROJECT_ROOT"

PYBIN="${PYBIN:-.venv/bin/python}"
if [ ! -x "$PYBIN" ]; then
  PYBIN="$(command -v python3)"
fi

REQUIRED_APPROVAL="I_APPROVE_CONTROLLED_PAPER_TRIAL"

OPERATOR_APPROVAL="${BATCH26M_OPERATOR_APPROVAL:-}"
SELECTED_FAMILY="${BATCH26M_SELECTED_FAMILY:-}"
SELECTED_SIDE="${BATCH26M_SELECTED_SIDE:-}"
QTY_LOTS="${BATCH26M_QTY_LOTS:-}"

echo "===== CONTROLLED PAPER ENABLEMENT FROM EXISTING 25V/25W — V2 ====="
echo "timestamp_ist=$(TZ=Asia/Kolkata date -Is)"
echo

echo "===== MANUAL APPROVAL / SCOPE VALIDATION ====="
if [ "$OPERATOR_APPROVAL" != "$REQUIRED_APPROVAL" ]; then
  echo "FAIL: BATCH26M_OPERATOR_APPROVAL must equal $REQUIRED_APPROVAL"
  exit 1
fi

case "$SELECTED_FAMILY" in
  MIST|MISB|MISC|MISR|MISO) ;;
  *) echo "FAIL: BATCH26M_SELECTED_FAMILY must be MIST/MISB/MISC/MISR/MISO. Got: '$SELECTED_FAMILY'"; exit 1 ;;
esac

case "$SELECTED_SIDE" in
  CALL|PUT) ;;
  *) echo "FAIL: BATCH26M_SELECTED_SIDE must be CALL or PUT. Got: '$SELECTED_SIDE'"; exit 1 ;;
esac

if [ "$QTY_LOTS" != "1" ]; then
  echo "FAIL: BATCH26M_QTY_LOTS must be exactly 1. Got: '$QTY_LOTS'"
  exit 1
fi

for var in \
  BATCH26M_BROKER_PAPER_PATH_VERIFIED \
  BATCH26M_CONFIRM_NO_REAL_LIVE \
  BATCH26M_CONFIRM_FORCED_FLATTEN \
  BATCH26M_CONFIRM_KILL_SWITCH \
  BATCH26M_CONFIRM_STOP_AFTER_FIRST_ORDER
do
  if [ "${!var:-}" != "1" ]; then
    echo "FAIL: $var must be 1"
    exit 1
  fi
done

echo "APPROVAL_OK"
echo "SELECTED_FAMILY=$SELECTED_FAMILY"
echo "SELECTED_SIDE=$SELECTED_SIDE"
echo "QTY_LOTS=$QTY_LOTS"

echo
echo "===== LIVE MARKET SESSION GUARD ====="
DOW="$(TZ=Asia/Kolkata date +%u)"
HHMM="$(TZ=Asia/Kolkata date +%H%M)"
if [ "$DOW" -lt 1 ] || [ "$DOW" -gt 5 ] || [ "$HHMM" -lt 0915 ] || [ "$HHMM" -gt 1530 ]; then
  echo "FAIL: controlled paper enablement must run during live market session only."
  echo "DOW=$DOW HHMM=$HHMM"
  exit 1
fi
echo "LIVE_SESSION_OK"

echo
echo "===== PREPARATION PROOF CHECK ====="
"$PYBIN" - <<'PY'
import json
from pathlib import Path

prep = Path("run/proofs/controlled_paper_trial_preparation_from_25v25w.json")
if not prep.exists():
    raise SystemExit("FAIL: preparation proof missing")
data = json.loads(prep.read_text(encoding="utf-8"))
if data.get("controlled_paper_trial_preparation_from_25v25w_ok") is not True:
    raise SystemExit("FAIL: preparation proof is not true")
if data.get("real_live_allowed") is not False:
    raise SystemExit("FAIL: preparation proof unexpectedly allows real live")
print("PREPARATION_PROOF_OK")
PY

echo
echo "===== PROVIDER CURRENT CHECK ====="
if [ -f bin/proof_market_session_provider_runtime.py ]; then
  "$PYBIN" bin/proof_market_session_provider_runtime.py
fi

"$PYBIN" - <<'PY'
import json
from pathlib import Path

p = Path("run/proofs/proof_market_session_provider_runtime.json")
if not p.exists():
    raise SystemExit("FAIL: provider runtime proof missing")
data = json.loads(p.read_text(encoding="utf-8"))
if data.get("market_session_provider_runtime_ok") is not True:
    raise SystemExit("FAIL: provider runtime proof is not true")

checks = data.get("checks", {})
required = [
    "provider_runtime_hash_present",
    "provider_runtime_required_keys_present",
    "futures_provider_allowed",
    "selected_option_provider_is_dhan",
    "option_context_provider_is_dhan",
    "execution_primary_provider_is_zerodha",
    "futures_status_ready",
    "selected_option_status_ready",
    "option_context_status_ready",
    "execution_primary_status_ready",
]
missing = [k for k in required if checks.get(k) is not True]
if missing:
    raise SystemExit(f"FAIL: provider current checks missing/false: {missing}")
print("PROVIDERS_CURRENT_OK")
PY

echo
echo "===== NO OPEN POSITION CHECK ====="
"$PYBIN" - <<'PY'
from __future__ import annotations

import json
from pathlib import Path

try:
    from bin._batch25v_market_observation_common import redis_client
    from app.mme_scalpx.core import names as N
except Exception as exc:
    raise SystemExit(f"FAIL: imports for position guard failed: {exc!r}")

client = redis_client()
candidates = []

for attr in dir(N):
    upper = attr.upper()
    if "POSITION" in upper and ("HASH" in upper or "STATE" in upper or "KEY" in upper):
        value = getattr(N, attr)
        if isinstance(value, str) and "replay" not in value.lower():
            candidates.append((attr, value))

for item in [
    ("FALLBACK_STATE_POSITION_MME", "state:position:mme"),
    ("FALLBACK_STATE_POSITION", "state:position"),
    ("FALLBACK_STATE_POSITION_NIFTY", "state:position:nifty"),
]:
    if item not in candidates:
        candidates.append(item)

def decode_hash(raw):
    return {
        (k.decode() if isinstance(k, bytes) else str(k)):
        (v.decode() if isinstance(v, bytes) else v)
        for k, v in dict(raw or {}).items()
    }

observed = []
existing = False
flat_seen = False

for const, key in candidates:
    try:
        exists = bool(client.exists(key))
    except Exception:
        exists = False

    if not exists:
        observed.append({"const": const, "key": key, "exists": False})
        continue

    existing = True
    h = decode_hash(client.hgetall(key))
    side = str(h.get("side") or h.get("position_side") or h.get("net_side") or h.get("state") or "").upper()
    qty_raw = h.get("quantity") or h.get("qty") or h.get("quantity_lots") or h.get("net_qty") or h.get("open_qty") or "0"
    try:
        qty = float(qty_raw or 0)
    except Exception:
        qty = 999999.0

    flat = side in {"", "FLAT", "NONE", "NO_POSITION", "0"} and abs(qty) <= 0.0
    if side == "FLAT" or abs(qty) <= 0.0:
        flat = True

    row = {"const": const, "key": key, "exists": True, "side": side, "qty": qty, "flat": flat}
    observed.append(row)

    if not flat:
        Path("run/proofs/controlled_paper_enablement_position_guard_failed.json").write_text(
            json.dumps({"no_open_position_ok": False, "blocking_position": row, "observed": observed}, indent=2),
            encoding="utf-8",
        )
        raise SystemExit("FAIL: open position detected")

    flat_seen = True

if not existing or not flat_seen:
    Path("run/proofs/controlled_paper_enablement_position_guard_failed.json").write_text(
        json.dumps({"no_open_position_ok": False, "reason": "flat position not proven", "observed": observed}, indent=2),
        encoding="utf-8",
    )
    raise SystemExit("FAIL: flat position not proven")

Path("run/proofs/controlled_paper_enablement_position_guard.json").write_text(
    json.dumps({"no_open_position_ok": True, "observed": observed}, indent=2),
    encoding="utf-8",
)
print("NO_OPEN_POSITION_OK")
PY

echo
echo "===== WRITE CONTROLLED PAPER ENABLEMENT ARTIFACTS ====="
TS="$(TZ=Asia/Kolkata date +%Y%m%d_%H%M%S)"
mkdir -p etc/strategy_family/rollout run/proofs reports/paper_trials

ENABLEMENT_FILE="etc/strategy_family/rollout/controlled_paper_trial_enablement_from_25v25w.yaml"
PROOF_FILE="run/proofs/controlled_paper_trial_enablement_from_25v25w.json"

cat > "$ENABLEMENT_FILE" <<YAML
schema_version: 1
gate_id: controlled_paper_trial_enablement_from_existing_25v25w
created_at_ist: "$(TZ=Asia/Kolkata date -Is)"

source_basis:
  batch25v: PASS_FREEZE_FINAL
  batch25w: READY_FOR_CONTROLLED_PAPER_PREP

paper_trial_enabled: true
paper_armed_enabled: true
real_live_allowed: false
real_live_enabled: false

selection:
  selected_family: "${SELECTED_FAMILY}"
  selected_side: "${SELECTED_SIDE}"
  quantity_lots: 1
  max_family_count: 1
  max_side_count: 1
  max_quantity_lots: 1

provider_safety:
  broker_path: PAPER_OR_SANDBOX_ONLY
  broker_paper_path_verified: true
  automatic_broker_failover_allowed: false
  fallback_execution_allowed: false
  mid_position_provider_migration_allowed: false

order_safety:
  paper_orders_allowed: true
  real_orders_allowed: false
  max_trial_orders_before_auto_stop: 1
  auto_stop_after_first_paper_order: true

risk_safety:
  forced_flatten_active: true
  kill_switch_active: true

reporting:
  trial_report_mandatory: true
  required_trial_report_dir: reports/paper_trials
  expected_report_name_prefix: controlled_paper_${SELECTED_FAMILY}_${SELECTED_SIDE}_${TS}
YAML

cat > "$PROOF_FILE" <<JSON
{
  "proof": "controlled_paper_trial_enablement_from_existing_25v25w",
  "timestamp_utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "controlled_paper_trial_enablement_from_25v25w_ok": true,
  "controlled_paper_trial_enabled": true,
  "paper_armed_enabled": true,
  "real_live_allowed": false,
  "selected_family": "${SELECTED_FAMILY}",
  "selected_side": "${SELECTED_SIDE}",
  "quantity_lots": 1,
  "automatic_broker_failover_allowed": false,
  "mid_position_provider_migration_allowed": false,
  "forced_flatten_active": true,
  "kill_switch_active": true,
  "auto_stop_after_first_paper_order": true,
  "trial_report_mandatory": true,
  "next_required_action": "Run one controlled paper order max, stop, verify flat, and write mandatory trial report."
}
JSON

echo "ENABLEMENT_FILE_WRITTEN: $ENABLEMENT_FILE"
echo "PROOF_WRITTEN: $PROOF_FILE"
cat "$PROOF_FILE"

echo
echo "CONTROLLED_PAPER_ENABLEMENT_FROM_25V25W_OK"
echo "Real live remains BLOCKED."
echo "Stop after first paper order / configured cap and write trial report."
