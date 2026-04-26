# Batch 25R — Closed-Market Proof Hygiene Corrective

Date: 2026-04-25  
Timestamp: 20260425_210017  
Run root: `run/batch25R_closed_market_proof_hygiene_corrective_20260425_210017`

## Purpose

Correct/triage Batch 25 closed-market proof failures without moving the system forward functionally.

## Safety posture

```text
SCALPX_ALLOW_LIVE_ORDERS=0
MME_USE_NULL_BROKER=1
MME_USE_NULL_FEED_ADAPTER=1
PYTHONDONTWRITEBYTECODE=1
```

## Actions performed

```text
1. Backed up failing proof/replay files.
2. Removed active app/bin __pycache__ and .pyc files.
3. Moved inactive audit bundle source copies outside project root.
4. Reran repo hygiene proof.
5. Reran proof layer contract proof.
6. Reran Redis strict raw contract matrix.
7. Extracted replay integrity/proof snippets.
8. Reran replay package and replay-engine proofs.
```

## Targeted proof summary

```text
proof	status	rc
bin/proof_repo_hygiene_quarantine.py	PASS	0
bin/proof_proof_layer_contracts.py	PASS	0
bin/proof_redis_contract_matrix.py --strict-raw	FAIL	1
bin/proof_replay_batch16_freeze.py	FAIL	1
bin/proof_replay_engine_contracts.py	FAIL	1
```

## Important note

If replay proofs still fail on `integrity_placeholder_pass_cannot_freeze_pass`, the next corrective patch must be limited to:

```text
app/mme_scalpx/replay/integrity.py
```

Specifically, placeholder PASS integrity checks must not aggregate to a freeze-grade PASS.

## Remaining rule

No strategy redesign.  
No live order activation.  
No market-session paper_armed until live market-hour observation passes.
