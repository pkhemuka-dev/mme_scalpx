# 2026-04-25 — Batch 5 integrations freeze-final patch

## Scope

Target folder:

```text
app/mme_scalpx/integrations/
```

Patched files:

```text
app/mme_scalpx/integrations/provider_runtime.py
app/mme_scalpx/integrations/bootstrap_provider.py
app/mme_scalpx/integrations/broker_api.py
app/mme_scalpx/integrations/feed_adapter.py
app/mme_scalpx/integrations/dhan_execution.py
bin/proof_integrations_batch5_freeze.py
bin/proof_provider_runtime_roles.py
```

## Freeze issues closed

- Dhan option_context can no longer become usable from generic Dhan provider health.
- Dhan option_context now requires actual DhanContextState; otherwise it is UNAVAILABLE.
- Dhan execution fallback is explicitly DISABLED until concrete Dhan execution transport is implemented and proof-enabled.
- Broker order payload validation now happens before transport availability check.
- bootstrap_provider now emits provider_bootstrap_report with explicit Dhan context/feed/fallback truth.
- feed_adapter now uses canonical provider symbol from names.py.
- dhan_execution.py is no longer an ambiguous empty file; it is an explicit disabled/quarantined surface.

## Proof artifact

```text
run/proofs/integrations_batch5_freeze.json
```

## Status

Batch 5 integrations freeze status:

```text
FREEZE-PASS after proof output PASS
```

Whole-project freeze status:

```text
NOT YET WHOLE-PROJECT FREEZE-FINAL
```

Remaining outside this batch:

- promoted StrategyOrderIntent / execution payload contract
- risk/execution live-entry safety proofs
- replay/dataset.py syntax blocker if not already fixed
- Dhan MISO-grade full option-chain materializer
- concrete Dhan execution transport implementation and proof
- longer live report-only observation
