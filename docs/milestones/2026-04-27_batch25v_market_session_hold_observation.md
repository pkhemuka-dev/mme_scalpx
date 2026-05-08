
## Closed-Market Continuation Note — 20260427_091829

Batch 25V is not freeze-final yet because market-session observation cannot be completed after market close.

Completed during this continuation:

```text
Zerodha token refresh: PASS
bootstrap quote fetch: PASS
safe user service start: PASS
order guards safe: trading_enabled=0 / allow_live_orders=0
runtime mode: OBSERVE_ONLY
```

Observed blocker:

```text
futures_marketdata_status = UNAVAILABLE
selected_option_marketdata_status = UNAVAILABLE
execution_primary_status = UNAVAILABLE
option_context_status = DEGRADED
```

Interpretation:

```text
This is expected after market close. Provider/feed freshness cannot be proven now.
```

Verdict:

```text
Batch 25V: PREPARED / AUTH-READY / NOT FREEZE-FINAL
paper_armed: STILL BLOCKED
real live trading: STILL BLOCKED
```

Next valid action:

```text
During next market session, start safe HOLD/report-only service and rerun all six 25V proofs.
```

## Corrective Patch — Precise Family Runtime Mode Normalization

Timestamp: 20260427_095248

The exact failing `ProviderRuntimeConfig` block in `feeds.py` was identified:

```python
family_runtime_mode=str(
    runtime.get("family_runtime_mode", N.FAMILY_RUNTIME_MODE_OBSERVE_ONLY)
),
```

Live startup crash:

```text
family_runtime_mode must be one of ('OBSERVE_ONLY', 'LEGACY_LIVE_FAMILY_SHADOW', 'FAMILY_LIVE_LEGACY_SHADOW', 'FAMILY_LIVE_ONLY'), got 'observe_only'
```

Repair:

- patched only `app/mme_scalpx/services/feeds.py`
- inserted `_batch25v_normalize_family_runtime_mode()`
- replaced exact `family_runtime_mode=str(...)` block with normalized canonical uppercase value
- maps `observe_only` to `OBSERVE_ONLY`
- refuses unknown rollout values
- did not enable strategy promotion
- did not enable paper_armed
- did not enable live orders
- did not change 25V proof logic

Backup:

```text
run/_code_backups/batch25v_family_runtime_mode_precise_patch_20260427_095248/app/mme_scalpx/services/feeds.py
```

## Corrective Patch — Dhan Runtime Environment Wiring

Timestamp: 20260427_095549

After family runtime mode normalization, provider runtime became fresh and Zerodha futures/execution became healthy, but Dhan lanes remained unavailable:

```text
selected_option_marketdata_status = UNAVAILABLE
option_context_status = UNAVAILABLE
```

Root cause:

```text
DHAN_CLIENT_ID / MME_DHAN_CLIENT_ID and DHAN_ACCESS_TOKEN / MME_DHAN_ACCESS_TOKEN were not visible in the runtime process environment.
```

Repair:

- created secret env file outside repo code:
  - `/home/Lenovo/scalpx/common/secrets/projects/mme_scalpx/dhan_runtime.env`
- added it as `EnvironmentFile` to user systemd unit:
  - `/home/Lenovo/.config/systemd/user/scalpx-mme.service`
- did not print secrets
- did not enable strategy promotion
- did not enable paper_armed
- did not enable live orders
- did not change 25V proof logic

Backup:

```text
run/_code_backups/batch25v_dhan_runtime_env_20260427_095549
```

## Corrective Patch — Restart Race Safe Lock Cleanup

Timestamp: 20260427_100240

The first lock cleanup refused correctly because orphan runtime processes were still present and the feeds lock was owned by a live process.

A later attempt to mask the user unit failed because the unit file exists directly at:

```text
/home/Lenovo/.config/systemd/user/scalpx-mme.service
```

Repair:

- stopped and disabled the user unit
- temporarily changed `Restart=on-failure` to `Restart=no`
- killed orphan MME processes
- cleaned runtime locks only after no MME process remained
- restored `Restart=on-failure`
- restarted one canonical safe user unit
- did not enable strategy promotion
- did not enable paper_armed
- did not enable live orders
- did not change 25V proof logic

Proof:

```text
run/proofs/proof_batch25v_runtime_lock_cleanup_restart_disabled.json
```

Backup:

```text
run/_code_backups/batch25v_stop_restart_race_20260427_100240
```

## Forensics — Single Start Lock / Monitor Failure

Timestamp: 20260427_100450

After Dhan env wiring and restart-race cleanup, the service still failed in startup.

Observed blockers:

```text
feeds singleton lock not acquired
MonitorService object has no attribute redis
Dhan /optionchain HTTP 429 appeared after repeated restart attempts
```

Action:

- disabled restart temporarily using `Restart=no`
- killed leftover MME processes
- verified locks before single start
- started service once only
- captured lock owners after failure
- inspected feeds lock acquisition code
- inspected monitor redis attribute code
- restored `Restart=on-failure`
- left service stopped to avoid Dhan rate-limit escalation
- did not enable strategy promotion
- did not enable paper_armed
- did not enable live orders
- did not change 25V proof logic

Proof:

```text
run/proofs/proof_batch25v_single_start_lock_forensics.json
```

Backup:

```text
run/_code_backups/batch25v_single_start_lock_forensics_20260427_100450
```

## Corrective Patch — Monitor Redis Attribute Repair

Timestamp: 20260427_100701

Single-start forensics identified a direct monitor code bug:

```python
missing = _batch15_missing_state_hashes(self.redis)
```

But `MonitorService.__init__()` owns the Redis client as:

```python
self._redis = redis_client
```

Repair:

- patched only `app/mme_scalpx/services/monitor.py`
- changed `self.redis` to `self._redis` in the Batch15 monitor snapshot wrapper
- added proof `bin/proof_monitor_redis_attr_contract.py`
- did not enable strategy promotion
- did not enable paper_armed
- did not enable live orders
- did not change 25V proof logic
- service was single-started under `Restart=no` and then stopped to avoid Dhan 429 escalation

Proof:

```text
run/proofs/proof_monitor_redis_attr_contract.json
```

Backup:

```text
run/_code_backups/batch25v_monitor_redis_attr_fix_20260427_100701
```

## Forensics — Feeds / Provider Runtime Single-Start Observation

Timestamp: 20260427_100848

After monitor redis attribute repair, service single-started under `Restart=no`.

Purpose:

- check whether feeds enters the live loop
- check whether provider runtime leaves BOOTSTRAP
- check whether futures/selected-option/Dhan context hashes become current
- avoid repeated Dhan calls after prior HTTP 429

Proof:

```text
run/proofs/proof_batch25v_feeds_provider_single_start.json
```

Backup:

```text
run/_code_backups/batch25v_feeds_provider_single_start_20260427_100848
```

Service intentionally stopped after observation.

## Corrective Patch — Feeds Lock Refresh Before Adapter Poll

Timestamp: 20260427_102800

The first lock-refresh repair attempt stopped at a proof-script bug. The audit showed the actual redisx signature:

```text
acquire_lock(key, owner, *, ttl_ms=None, client=None)
refresh_lock(key, owner, *, ttl_ms=None, client=None)
```

Repair:

- rewrote `bin/proof_lock_refresh_contract.py` with correct redisx call signature
- proved Redis lock acquire/refresh same-owner contract
- patched `app/mme_scalpx/services/feeds.py` to refresh the feeds singleton lock before adapter polling
- removed duplicate post-poll refresh in the same loop
- left execution lock code unchanged in this patch
- did not change strategy promotion
- did not enable paper_armed
- did not enable live orders
- did not change 25V proof logic

Proofs:

```text
run/proofs/proof_lock_refresh_contract.json
run/proofs/proof_feeds_lock_refresh_pre_poll.json
```

Backup:

```text
run/_code_backups/batch25v_lock_refresh_pre_poll_repair_20260427_102800
```

## Audit — Dhan Context Completeness

Timestamp: 20260427_103056

After lock-refresh stabilization, the remaining 25V blocker was:

```text
option_context_status = DEGRADED
transition_reason = STALE_DATA
```

This audit:

- single-started service with `Restart=no`
- observed Dhan context for 90 seconds
- captured provider runtime and Dhan context hash completeness
- inspected Dhan context adapter / feeds handler code surfaces
- did not change strategy promotion
- did not enable paper_armed
- did not enable live orders
- did not change 25V proof logic

Proof:

```text
run/proofs/proof_batch25v_dhan_context_completeness_audit.json
```

Backup:

```text
run/_code_backups/batch25v_dhan_context_completeness_audit_20260427_103056
```

## Corrective Patch — Dhan Context Adapter Ladder Payload

Timestamp: 20260427_103432

Dhan context completeness audit showed:

```text
Dhan context hash fresh
selected option marketdata healthy
selected CALL/PUT keys present
option_chain_ladder_len = 0
strike_ladder_len = 0
selected_call_context_keys = []
selected_put_context_keys = []
```

Root cause:

```text
DhanContextPollingAdapter emitted a minimal context payload from /optionchain but did not carry normalized option-chain ladder rows into the feeds Dhan context contract.
```

Repair:

- patched `app/mme_scalpx/integrations/dhan_runtime_clients.py`
- normalized Dhan /optionchain `data.oc` CE/PE blocks into frozen ladder rows
- emitted `option_chain_ladder`, `strike_ladder`, `option_chain_ladder_json`, `strike_ladder_json`
- emitted selected call/put context JSON where ATM rows are present
- did not change strategy promotion
- did not enable paper_armed
- did not enable live orders
- did not change 25V proof logic

Proof:

```text
run/proofs/proof_dhan_context_adapter_ladder_payload.json
run/proofs/proof_batch25v_dhan_context_completeness_audit.json
```

Backup:

```text
run/_code_backups/batch25v_dhan_context_ladder_payload_repair_20260427_103432
```

## Corrective Patch — Selected Option Active Snapshot Bridge

Timestamp: 20260427_104902

Feed snapshot proof failed because:

```text
selected_option_hash_present = true
selected_call_json_present = false
selected_put_json_present = false
option_call_depth_consumed = false
option_put_depth_consumed = false
```

Observed:

```text
ce_atm_json / pe_atm_json were populated
Dhan context selected_call_context_json / selected_put_context_json were populated
selected_call_json / selected_put_json were null
```

Root cause:

```text
feeds._selected_option_member only matched via _token_to_approved instrument_key. Provider migration left the frame member present but the approved-map key did not match the normalized Dhan context selected key.
```

Repair:

- patched only `app/mme_scalpx/services/feeds.py`
- preserved original approved-map match
- added fallback selected-option member matching by CE/PE side + strike/trading symbol
- did not change strategy promotion
- did not enable paper_armed
- did not enable live orders
- did not change 25V proof logic

Proof:

```text
run/proofs/proof_selected_option_active_bridge.json
run/proofs/proof_market_session_feed_snapshot.json
```

Backup:

```text
run/_code_backups/batch25v_selected_option_active_bridge_20260427_104902
```
