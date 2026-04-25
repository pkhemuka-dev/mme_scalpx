# Batch 6 — Domain Instrument Resolution Freeze Final

Date: 2026-04-25 10:41:48 IST

## Scope

Files:

- `app/mme_scalpx/domain/instruments.py`
- `app/mme_scalpx/domain/__init__.py`
- `app/mme_scalpx/integrations/runtime_instruments_factory.py`
- `etc/symbols.yaml` where present
- `source/etc_redacted/symbols.yaml` where present
- `ops/validate_runtime_instruments.py`

## Result required

Batch 6 is freeze-final if:

- compile proof passes
- import/surface proof passes
- `bin/proof_domain_instruments_batch6_freeze.py` status PASS
- `bin/proof_runtime_instrument_source.py` status PASS
- strict Redis regression remains PASS
- prior core regression smoke remains PASS where proof scripts exist

## Fixes applied

- Removed hardcoded Thursday live expiry policy from domain selection.
- Added configurable weekly/monthly expiry weekday policy.
- Defaulted NIFTY expiry policy to Tuesday.
- Added explicit expiry weekday validation.
- Replaced UTC-date selection with IST exchange-date selection for current future and option expiry filtering.
- Added Dhan token aliases:
  - `security_id`
  - `securityId`
  - `dhan_security_id`
- Added explicit Tuesday expiry weekday policy into symbols.yaml where present.
- Made runtime instruments factory consume symbols.yaml domain-safe fields.
- Exposed runtime instrument source/config proof.
- Added domain package export hygiene.
- Replaced/added operator validation helper for runtime instruments.

## Explicit non-change

- No Redis ownership was added to domain.
- No service loop was added to domain.
- No broker order logic was added to domain.
- No live quote fetch is performed by the proof scripts.
- `params_mme.yaml` remains non-domain tuning/config surface and does not override domain instrument contracts.

## Proof artifacts

- `run/proofs/domain_instruments_batch6_freeze.json`
- `run/proofs/runtime_instrument_source.json`

## Remaining outside Batch 6

Whole-tree freeze remains blocked by the known replay compile issue until fixed:

- `app/mme_scalpx/replay/dataset.py`
- `IndentationError around line 786`

Provider/broker integration and Dhan/Zerodha full equivalence remain Batch 5/7+ surfaces if not already closed:

- Dhan option context health
- Dhan execution fallback quarantine/implementation
- MISO/Dhan-context promotion disable/degrade proof
- selected option live feed synchronisation proof

