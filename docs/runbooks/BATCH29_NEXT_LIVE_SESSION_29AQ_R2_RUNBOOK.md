# Batch 29 — Next Live Session Runbook: 29AQ-R2

Current gate: WAIT_FOR_VALID_LIVE_OBSERVATION_WINDOW

Do not run 29AS until 29AQ-R2 passes.
Do not patch replay/parity for closed-market or stale provider data.
Do not enable paper_armed or live trading.

Before retry during live market window:
cd /home/Lenovo/scalpx/projects/mme_scalpx
pfeedcheck || true

Rerun:
PYBIN=".venv/bin/python"
if [ ! -x "$PYBIN" ]; then PYBIN="$(command -v python3)"; fi
SCRIPT="/tmp/batch29aq_r2_guarded_fresh_live_observe_readiness.py"
"$PYBIN" -m py_compile "$SCRIPT"
timeout 360s "$PYBIN" "$SCRIPT"

Required PASS:
verdict = PASS_FRESH_LIVE_OBSERVE_READINESS_BUNDLE_29AQ_R2
readiness_all_true = true
safety_boundary_ready_from_29ap = true
paper_armed_approved = false
live_trading_approved = false
