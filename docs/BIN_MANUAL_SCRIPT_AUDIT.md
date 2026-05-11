# MME-ScalpX Manual Bin Script Audit

Generated: 2026-05-11T23:15:40.735127

## Safety

- Scripts were read, not executed.
- No files moved.
- No files deleted.
- No services started.
- No broker calls.
- No Redis writes.
- No paper/live enablement.

## Classification

### `bin/check_broker_token.py`

- resolved_kind: `provider_auth_diagnostic`
- recommended_future_bucket: `bin/diagnostics/provider_auth/`
- migration_priority: `LATE_MANUAL_ONLY`
- risk_flags: `none`
- reason: broker/session-token tool; keep out of first migration and require manual auth safety review

### `bin/dhan_mcx_option_probe.py`

- resolved_kind: `provider_probe_diagnostic`
- recommended_future_bucket: `bin/diagnostics/provider_probe/`
- migration_priority: `LATE_MANUAL_ONLY`
- risk_flags: `broker_terms, network_terms`
- reason: Dhan/provider probe; do not move with low-risk proof scripts

### `bin/ensure_zerodha_shared_token.py`

- resolved_kind: `provider_auth_diagnostic`
- recommended_future_bucket: `bin/diagnostics/provider_auth/`
- migration_priority: `LATE_MANUAL_ONLY`
- risk_flags: `broker_terms, file_write_terms`
- reason: broker/session-token tool; keep out of first migration and require manual auth safety review

### `bin/feed_depth_witness.py`

- resolved_kind: `feed_diagnostic`
- recommended_future_bucket: `bin/diagnostics/feed/`
- migration_priority: `MEDIUM_AFTER_REVIEW`
- risk_flags: `broker_terms`
- reason: feed/depth witness tool; likely diagnostic but review Redis/provider references first

### `bin/top20.sh`

- resolved_kind: `operator_diagnostic_shell`
- recommended_future_bucket: `bin/diagnostics/operator/`
- migration_priority: `MEDIUM_AFTER_REVIEW`
- risk_flags: `broker_terms, network_terms`
- reason: operator shell helper; review shell commands before movement

### `bin/export_session_artifacts.py`

- resolved_kind: `diagnostic`
- recommended_future_bucket: `bin/diagnostics/`
- migration_priority: `EARLY_SAFE_IF_NO_RUNTIME_START`
- risk_flags: `redis_terms, file_write_terms`
- reason: R5 already resolved as diagnostic; exact audit included for confirmation

### `bin/predischeck.py`

- resolved_kind: `diagnostic`
- recommended_future_bucket: `bin/diagnostics/`
- migration_priority: `EARLY_SAFE_IF_NO_RUNTIME_START`
- risk_flags: `redis_terms`
- reason: R5 already resolved as diagnostic; exact audit included for confirmation

## Decision

Do not move broker/token/provider-probe scripts in the first bin migration.

First migration batch should be proof-only scripts with no runtime-start/order/provider-auth risk flags.
