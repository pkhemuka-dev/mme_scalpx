Batch 28E Real observe_only evidence capture execution wrapper

Date: 2026-05-01

Purpose:
Install a future market-session-gated observe_only evidence capture execution wrapper.

Scope:
28E does not run live capture.
28E does not start services.
28E does not read Redis.
28E does not write Redis.
28E does not call broker APIs.
28E does not enable paper_armed.
28E does not enable live trading.
28E does not prove full replay/live parity.

Future operator status command:
cd /home/Lenovo/scalpx/projects/mme_scalpx
.venv/bin/python bin/observe_only_market_session_capture_execute.py --status

Future operator execution command during real market session only:
cd /home/Lenovo/scalpx/projects/mme_scalpx
.venv/bin/python bin/observe_only_market_session_capture_execute.py --execute --confirm-observe-only --session-id observe_only_YYYYMMDD --root run/replay/parity/live_evidence/observe_only_YYYYMMDD --evidence-map etc/replay/parity/observe_only_YYYYMMDD_evidence_map.json

The future execution command only packages provided evidence files. It does not start services, read live Redis, write live Redis, call broker APIs, or place orders.

Stop if:
paper_armed is true
live trading is true
broker_call_reachable is true
live_redis_write_reachable is true
runtime_promotion_reachable is true
no_order_sent proof fails
market-session time gate is closed
