# Batch 19 — Proof Scripts and Operator Tools Governance Freeze

## Scope

- `etc/proof_registry.yaml`
- `bin/prooflib.py`
- `bin/proof_proof_layer_contracts.py`
- `bin/build_proof_bundle.py`
- `bin/proof_strategy_activation_report_redis_smoke.py`
- `bin/observe_strategy_activation_report_live.py`

## Decision

The existing proof/tooling layer is preserved.

Batch 19 does not claim paper-armed readiness. It classifies the current proof suite and prevents HOLD/report-only proofs from being overread as promoted-entry safety.

## Runtime law

- Redis smoke proof defaults to read-only.
- Replay write uses `--publish-hold-replay`.
- Live decision-stream write uses `--publish-hold-live` plus `I_UNDERSTAND_THIS_WRITES_LIVE_DECISION_STREAM=1`.
- Live observer summary explicitly states:
  - `proof_scope = HOLD_REPORT_ONLY_LIVE_OBSERVATION`
  - `activation_ready = false`
  - `paper_armed_ready = false`
  - `does_not_prove = [...]`

## Proofs

Required proof artifact:

- `run/proofs/proof_layer_contracts.json`

## Freeze status

Batch 19 is freeze-final when `run/proofs/proof_layer_contracts.json` shows `"status": "PASS"`.
