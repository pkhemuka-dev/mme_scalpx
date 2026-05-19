# B1-R10 Capture Bundle Collection Command Dry Plan

Safety: dry-plan only. No live capture, no replay, no service start, no Redis read/write/delete, no broker call, no order, no paper/live, no PnL.

## Required future bundle files

- `capture_manifest.json`
- `features_rows.jsonl`
- `decision_rows.jsonl`
- `risk_lifecycle_rows.jsonl`
- `execution_shadow_rows.jsonl`
- `position_safety_snapshot.json`
- `order_safety_snapshot.json`
- `identity_continuity_report.json`
- `lifecycle_presence_report.json`
- `backtest_admission_precheck.json`
- `safety_no_order_no_broker_report.json`

## Future operator command skeleton

```bash
# B1 future real capture skeleton only.
# Do not run until explicit live-session approval.

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
mkdir -p "$CAPTURE_DIR"

# Future collection command must be supplied by the observe-only capture lane/tooling.
# It must export these files:
# - capture_manifest.json
# - features_rows.jsonl
# - decision_rows.jsonl
# - risk_lifecycle_rows.jsonl
# - execution_shadow_rows.jsonl
# - position_safety_snapshot.json
# - order_safety_snapshot.json
# - identity_continuity_report.json
# - lifecycle_presence_report.json
# - backtest_admission_precheck.json
# - safety_no_order_no_broker_report.json

.venv/bin/python bin/b1_capture_bundle_validator.py \
  --bundle "$CAPTURE_DIR" \
  --out "$CAPTURE_DIR/validator_out" \
  --dry-only
```

## Validator after future capture

```bash
.venv/bin/python bin/b1_capture_bundle_validator.py --bundle <capture_bundle_dir> --out <capture_bundle_dir>/validator_out --dry-only
```

## Rule

This B1-R10 package does not run capture. It only freezes the future collection command shape.

Dry plan: `run/audits/B1-R10_CAPTURE_BUNDLE_COLLECTION_COMMAND_DRY_PLAN_NO_LIVE_RUN_NO_REPLAY_20260512_004406.dry_plan.json`
