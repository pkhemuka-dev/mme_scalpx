# A6-FEED-R5AC-R2_clipboard_safe_freeze_minimal_supported_features_strategy_start_plan_no_start_no_order_no_paper_20260515_104057 Minimal Observe-Only Start Runbook

Batch: A6-FEED-R5AC-R2

Verdict: PASS_A6_FEED_R5AC_R2_MINIMAL_SUPPORTED_START_PLAN_FROZEN_NO_START_NO_ORDER_NO_PAPER

Safety boundary:
- Start only FEATURES and/or STRATEGY if missing.
- No risk/execution.
- No paper/live.
- No broker/order.
- orders:mme:stream must remain 0.
- position must remain FLAT.
- No source patch, no restore, no lock clear/delete.

Approved minimal command shape for a future approved start batch:

```bash
cd /home/Lenovo/scalpx/projects/mme_scalpx
set -euo pipefail

PYBIN=".venv/bin/python"
[ -x "$PYBIN" ] || PYBIN="$(command -v python3)"
export PYTHONPATH="$PWD:${PYTHONPATH:-}"

unset SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME || true
unset SCALPX_CONTROLLED_PAPER_SCOPE_ACK || true
unset SCALPX_REAL_LIVE_ALLOWED || true
unset SCALPX_ALLOW_REAL_LIVE || true
unset SCALPX_ALLOW_BROKER_ORDERS || true
unset SCALPX_PAPER_ARMED || true
export SCALPX_OBSERVE_ONLY=1

# Features if missing:
"$PYBIN" -m app.mme_scalpx.main --service features

# Strategy if missing:
"$PYBIN" -m app.mme_scalpx.main --service strategy
```

Command checks:

```json
{
  "features": {
    "command": [
      ".venv/bin/python",
      "-m",
      "app.mme_scalpx.main",
      "--service",
      "features"
    ],
    "ok": true,
    "option_tokens": [
      "--service"
    ],
    "service_choice_valid": true,
    "service_value": "features",
    "unknown_options": []
  },
  "strategy": {
    "command": [
      ".venv/bin/python",
      "-m",
      "app.mme_scalpx.main",
      "--service",
      "strategy"
    ],
    "ok": true,
    "option_tokens": [
      "--service"
    ],
    "service_choice_valid": true,
    "service_value": "strategy",
    "unknown_options": []
  }
}
```

Next approval phrase:

```text
I APPROVE A6-FEED MINIMAL OBSERVE-ONLY FEATURES/STRATEGY START PLAN: START FEATURES/STRATEGY ONLY IF MISSING USING MINIMAL SUPPORTED COMMANDS, NO PAPER, NO LIVE, NO BROKER ORDER, NO RISK/EXECUTION START, ORDERS STREAM MUST REMAIN 0, POSITION MUST REMAIN FLAT
```
