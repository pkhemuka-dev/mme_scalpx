# MME Provider-Aware Runtime Stabilization Milestone

Date: 2026-04-24  
Host: mme-scalpx  
Project: `/home/Lenovo/scalpx/projects/mme_scalpx`

## Milestone Verdict

`provider-aware canonical runtime: STABILIZED`

Proof file:

`run/proofs/runtime_stabilization_20260424_235008.txt`

## Achieved

- Canonical `scalpx-mme.service` is active and stable.
- Systemd drop-in broker env is loaded:
  - `/etc/systemd/system/scalpx-mme.service.d/10-broker-env.conf`
- Provider bootstrap completes with all required surfaces:
  - `runtime_instruments=1`
  - `feed_adapter=1`
  - `feed_adapters=1`
  - `zerodha_feed_adapter=1`
  - `dhan_feed_adapter=1`
  - `dhan_context_adapter=1`
  - `broker=1`
- Consumer group bootstrap completes.
- All runtime services start under canonical systemd ownership.
- No duplicate standalone `--service` runtime ownership remains.
- Monitor reports stable:
  - `health overall_status=OK summary=risk_blocks_entries`

## Fixed

### features.py

- Fixed provider-runtime publishable schema seam.
- Fixed provider status string coercion.
- Fixed slots/dataclass serialization issue.
- Removed temporary `features_run_once_phase` probe spam.
- Added `ts_event_ns` to feature health heartbeat.
- Reduced feature heartbeat interval from 5 seconds to 2 seconds.

### strategy.py

- Fixed Redis XADD `NoneType` field failure.
- Added Redis-safe stream field sanitizer.
- Added canonical `payload_json` for execution decision parsing.
- Added `ts_event_ns` to strategy health heartbeat.
- Reduced strategy heartbeat interval from 5 seconds to 2 seconds.

### dhan_runtime_clients.py

- Added Dhan option-chain context cache/backoff behavior.
- Dhan context no longer needs to hammer `/optionchain` every poll loop.
- Offline cache/backoff behavior was proven.

### Runtime ownership

- Stopped duplicate/manual service processes.
- Stopped competing feeds collector ownership.
- Canonical systemd runtime now owns live runtime.

## Validation Performed

- Syntax proof passed for:
  - `app/mme_scalpx/services/features.py`
  - `app/mme_scalpx/services/strategy.py`
  - `app/mme_scalpx/integrations/dhan_runtime_clients.py`
- Systemd runtime active.
- Provider bootstrap proof passed.
- Health proof passed.
- No current runtime errors for:
  - `family_features_publishable_validation_failed`
  - `SnapshotMemberView.__dict__`
  - Redis `NoneType`
  - `DecisionContractError`
  - `payload_json missing`
  - singleton lock conflict
  - heartbeat missing `ts_event_ns`
  - heartbeat aging after warmup

## Remaining Expected Status

`risk_blocks_entries`

This is acceptable for this milestone. It means the risk layer is blocking entries. It is not a provider/runtime failure.

## Not Yet Frozen / Needs Later Cleanup

- Git diff is large and includes older family/doctrine changes.
- Backup files should not be deleted yet.
- Runtime stabilization changes should be reviewed and separated from strategy-family doctrine work before final git commit.
- Dhan context cache/backoff is offline-proven; it should receive longer live observation later.

## Next Recommended Lane

Do not immediately patch more runtime code.

Recommended next sequence:

1. Review `git diff` by file.
2. Separate runtime-stabilization changes from family/doctrine changes.
3. Keep current runtime running for observation.
4. Then move to the next lane:
   - risk state / `risk_blocks_entries` review, or
   - family strategy activation readiness, depending on priority.

