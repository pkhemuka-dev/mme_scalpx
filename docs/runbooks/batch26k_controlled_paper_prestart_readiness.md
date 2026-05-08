# Batch 26K — Controlled Paper Pre-start Readiness

Date: 2026-04-29

## Verdict

- controlled_paper_prestart_readiness_ok: `True`
- controlled_paper_start_allowed_by_this_batch: `False`
- source_code_patched: `False`
- services_started: `False`
- Redis writes: `False`
- paper_armed_approved: `False`
- real_live_approved: `False`

## Exact controlled-paper scope to be used later

- Family: `MIST`
- Side: `CALL`
- Quantity: `1 lot`
- Real live: `forbidden`

## Required environment for a later start command

```bash
export SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME='1'
export SCALPX_CONTROLLED_PAPER_SCOPE_ACK='I_ACCEPT_MIST_CALL_1LOT_PAPER_ONLY'
unset ALLOW_LIVE_ORDERS LIVE_ORDERS_ALLOWED TRADING_ENABLED REAL_LIVE_ALLOWED SCALPX_REAL_LIVE_ALLOWED
```

## Later start command candidate

Do not run this from Batch 26K. This is only the pre-start reference:

```bash
cd /home/Lenovo/scalpx/projects/mme_scalpx
.venv/bin/python bin/start_controlled_paper_runtime_chain.py
```

## Rollback / stop commands

```bash
pfeedstop || true
pkill -f 'app\.mme_scalpx\.main --service' || true
ps -ef | grep -E 'app\.mme_scalpx\.main|start_controlled_paper_runtime_chain' | grep -v grep || true
redis-cli XLEN orders:mme:stream
redis-cli HGETALL state:position:mme
```

## Required next gate

Batch 26L may be a controlled-paper dry-start/runbook validation or operator-confirmed start package. Batch 26K itself does not start anything.

