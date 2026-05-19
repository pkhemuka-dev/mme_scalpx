# B1-R12 Real Capture Session Approval Gate

Safety: approval-gate only. No live capture, no replay, no service start, no Redis read/write/delete, no broker call, no order, no paper/live, no PnL.

## Required operator approval text before future capture

`I APPROVE B1 REAL OBSERVE-ONLY CAPTURE: NO PAPER, NO LIVE, NO BROKER ORDER, NO REPLAY, NO PNL, CAPTURE AND VALIDATE ONLY`

## Future capture command package

`B1-R13_REAL_OBSERVE_ONLY_CAPTURE_BUNDLE_COMMAND_APPROVAL_REQUIRED`

## Future command skeleton

```bash
# DO NOT RUN unless operator has explicitly approved:
# I APPROVE B1 REAL OBSERVE-ONLY CAPTURE: NO PAPER, NO LIVE, NO BROKER ORDER, NO REPLAY, NO PNL, CAPTURE AND VALIDATE ONLY

cd /home/Lenovo/scalpx/projects/mme_scalpx
set -euo pipefail

export SCALPX_OBSERVE_ONLY=1
unset SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME || true
unset SCALPX_CONTROLLED_PAPER_SCOPE_ACK || true
unset SCALPX_REAL_LIVE_ALLOWED || true
unset SCALPX_ALLOW_REAL_LIVE || true
unset SCALPX_ALLOW_BROKER_ORDERS || true
unset SCALPX_PAPER_ARMED || true

CAPTURE_TS="$(date +%Y%m%d_%H%M%S)"
CAPTURE_DIR="run/evidence_bundles/observe_only_lifecycle_capture/B1_REAL_CAPTURE_${CAPTURE_TS}"
VALIDATOR_OUT="${CAPTURE_DIR}/validator_out"

mkdir -p "$CAPTURE_DIR" "$VALIDATOR_OUT"

# Future capture tool must export exactly these bundle files into $CAPTURE_DIR:
# capture_manifest.json
# features_rows.jsonl
# decision_rows.jsonl
# risk_lifecycle_rows.jsonl
# execution_shadow_rows.jsonl
# position_safety_snapshot.json
# order_safety_snapshot.json
# identity_continuity_report.json
# lifecycle_presence_report.json
# backtest_admission_precheck.json
# safety_no_order_no_broker_report.json

# After capture completes:
.venv/bin/python bin/b1_capture_bundle_validator.py \
  --bundle "$CAPTURE_DIR" \
  --out "$VALIDATOR_OUT" \
  --dry-only
```

## Rule

This B1-R12 package does not run capture. It only freezes the approval gate.

Approval gate artifact: `run/audits/B1-R12_REAL_CAPTURE_SESSION_APPROVAL_GATE_WAIT_FOR_MARKET_NO_REPLAY_20260512_103715.approval_gate.json`
