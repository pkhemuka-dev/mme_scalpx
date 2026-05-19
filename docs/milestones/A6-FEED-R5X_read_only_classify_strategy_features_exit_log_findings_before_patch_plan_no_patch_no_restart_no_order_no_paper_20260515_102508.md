# A6-FEED-R5X_read_only_classify_strategy_features_exit_log_findings_before_patch_plan_no_patch_no_restart_no_order_no_paper_20260515_102508

Batch: A6-FEED-R5X

Purpose: read_only_classify_strategy_features_exit_log_findings_before_patch_plan_no_patch_no_restart_no_order_no_paper

Final verdict: PASS_A6_FEED_R5X_STRATEGY_EXIT_LOG_FINDINGS_CLASSIFIED_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER

Safety: read-only strategy/features exit-log classification only; no patch, no restore, no clear/delete, no start/restart/stop, no Redis write, no paper/live, no risk/execution, no broker/order.

Classification:

```json
{
  "decisions_stream_age_ms": 1929460,
  "decisions_stream_xlen": 1684,
  "error_window_count": 60,
  "features_stream_age_ms": 450867,
  "features_stream_xlen": 91,
  "likely_condition": "STRATEGY_EXIT_LOG_CLASSIFIED_NAME_ERROR",
  "log_pattern_scores": {
    "attribute_error": 0,
    "controlled_paper": 8,
    "decision_publish": 33,
    "exception": 36,
    "feature_consumer": 15,
    "import_error": 0,
    "key_error": 0,
    "lock_error": 1,
    "name_error": 10,
    "provider_context": 14,
    "redis_error": 1,
    "traceback": 6,
    "type_error": 0,
    "value_error": 0
  },
  "next_action": "Prepare narrow patch plan for exact NameError only. No restart/paper/live.",
  "r5w_final_verdict": "PASS_A6_FEED_R5W_STRATEGY_FEATURES_EXIT_CAUSE_EVIDENCE_EXTRACTED_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER",
  "r5w_likely_condition": "STRATEGY_NOT_RUNNING_WITH_LOGGED_EXIT_OR_ERROR_EVIDENCE",
  "r5w_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5W_read_only_strategy_features_start_log_exit_cause_inspection_after_services_not_running_no_patch_no_restart_no_order_no_paper_20260515_102207.json",
  "standard_services": []
}
```

Pattern scores:

```json
{
  "attribute_error": 0,
  "controlled_paper": 8,
  "decision_publish": 33,
  "exception": 36,
  "feature_consumer": 15,
  "import_error": 0,
  "key_error": 0,
  "lock_error": 1,
  "name_error": 10,
  "provider_context": 14,
  "redis_error": 1,
  "traceback": 6,
  "type_error": 0,
  "value_error": 0
}
```

Error windows:

```json
[
  {
    "line": 4,
    "window_redacted": "[\n  {\n    \"decision_seen\": false,\n    \"exception_seen\": true,\n    \"exit_seen\": true,\n    \"feature_seen\": true,\n    \"mtime_iso_utc\": \"2026-05-15T04:47:53.901807+00:00\",\n    \"path\": \"/<REDACTED_SECRET_OR_TOKEN>\","
  },
  {
    "line": 12,
    "window_redacted": "    \"path\": \"/<REDACTED_SECRET_OR_TOKEN>\",\n    \"sha256\": \"<REDACTED_SECRET_OR_TOKEN>\",\n    \"size\": 2862,\n    \"strategy_seen\": false,\n    \"tail_redacted\": \"{\\\"level\\\":\\\"INFO\\\",\\\"logger\\\":\\\"app.mme_scalpx.main\\\",\\\"message\\\":\\\"logging_configured level=INFO format=json\\\",\\\"process\\\":2980,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"2026-05-15T04:42:44.539061+00:00\\\"}\\n{\\\"level\\\":\\\"INFO\\\",\\\"logger\\\":\\\"app.mme_scalpx.domain.instruments\\\",\\\"message\\\":\\\"instrument_repository_loaded <REDACTED_SECRET_OR_TOKEN> format=csv records=43288 futures=6 calls=1651 puts=1673\\\",\\\"process\\\":2980,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"2026-05-15T04:42:50.761267+00:00\\\"}\\n{\\\"level\\\":\\\"WARNING\\\",\\\"logger\\\":\\\"app.mme_scalpx.integrations.bootstrap_provider\\\",\\\"message\\\":\\\"bootstrap_provider_dhan_live_unavailable error=missing DHAN_CLIENT_ID / MME_DHAN_CLIENT_ID\\\",\\\"process\\\":2980,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"2026-05-15T04:42:57.637842+00:00\\\"}\\n{\\\"level\\\":\\\"INFO\\\",\\\"logger\\\":\\\"app.mme_scalpx.main\\\",\\\"message\\\":\\\"bootstrap_provider_completed provider=app.mme_scalpx.integrations.bootstrap_provider:provide mode=returned_dict runtime_instruments=1 feed_adapter=1 market_data_adapter=0 feed_adapters=1 zerodha_feed_adapter=1 dhan_feed_adapter=0 dhan_context_adapter=0 broker=1\\\",\\\"process\\\":2980,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"2026-05-15T04:42:57.874401+00:00\\\"}\\n{\\\"level\\\":\\\"INFO\\\",\\\"logger\\\":\\\"app.mme_scalpx.main\\\",\\\"message\\\":\\\"dependency_surfaces_resolved runtime_instruments=1 feed_adapter=1 market_data_adapter=1 feed_adapters=1 zerodha_feed_adapter=1 dhan_feed_adapter=0 dhan_context_adapter=0 broker=1\\\",\\\"process\\\":2980,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"2026-05-15T04:42:57.876257+00:00\\\"}\\n{\\\"level\\\":\\\"INFO\\\",\\\"logger\\\":\\\"app.mme_scalpx.main\\\",\\\"message\\\":\\\"consumer_group_bootstrap_disabled\\\",\\\"process\\\":2980,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"2026-05-15T04:42:57.971179+00:00\\\"}\\n{\\\"level\\\":\\\"INFO\\\",\\\"logger\\\":\\\"app.mme_scalpx.main\\\",\\\"message\\\":\\\"runtime_service_starting service=features module=app.mme_scalpx.services.features instance_id=features:mme-scalpx:2980 replay=False\\\",\\\"process\\\":2980,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"2026-05-15T04:42:57.971581+00:00\\\"}\\n{\\\"level\\\":\\\"INFO\\\",\\\"logger\\\":\\\"app.mme_scalpx.services.features\\\",\\\"message\\\":\\\"features_service_started instance_id=features:mme-scalpx:2980\\\",\\\"process\\\":2980,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"2026-05-15T04:42:57.977999+00:00\\\"}\\n{\\\"level\\\":\\\"WARNING\\\",\\\"logger\\\":\\\"app.mme_scalpx.main\\\",\\\"message\\\":\\\"received_shutdown_signal signum=15\\\",\\\"process\\\":2980,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"2026-05-15T04:47:47.941540+00:00\\\"}\\n{\\\"level\\\":\\\"INFO\\\",\\\"logger\\\":\\\"app.mme_scalpx.services.features\\\",\\\"message\\\":\\\"features_service_stopped\\\",\\\"process\\\":2980,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"2026-05-15T04:47:53.902221+00:00\\\"}\\n{\\\"level\\\":\\\"INFO\\\",\\\"logger\\\":\\\"app.mme_scalpx.main\\\",\\\"message\\\":\\\"runtime_service_exited service=features instance_id=features:mme-scalpx:2980 exit_code=0\\\",\\\"process\\\":2980,\\\"thread\\\":\\\"MainThre"
  },
  {
    "line": 13,
    "window_redacted": "    \"sha256\": \"<REDACTED_SECRET_OR_TOKEN>\",\n    \"size\": 2862,\n    \"strategy_seen\": false,\n    \"tail_redacted\": \"{\\\"level\\\":\\\"INFO\\\",\\\"logger\\\":\\\"app.mme_scalpx.main\\\",\\\"message\\\":\\\"logging_configured level=INFO format=json\\\",\\\"process\\\":2980,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"2026-05-15T04:42:44.539061+00:00\\\"}\\n{\\\"level\\\":\\\"INFO\\\",\\\"logger\\\":\\\"app.mme_scalpx.domain.instruments\\\",\\\"message\\\":\\\"instrument_repository_loaded <REDACTED_SECRET_OR_TOKEN> format=csv records=43288 futures=6 calls=1651 puts=1673\\\",\\\"process\\\":2980,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"2026-05-15T04:42:50.761267+00:00\\\"}\\n{\\\"level\\\":\\\"WARNING\\\",\\\"logger\\\":\\\"app.mme_scalpx.integrations.bootstrap_provider\\\",\\\"message\\\":\\\"bootstrap_provider_dhan_live_unavailable error=missing DHAN_CLIENT_ID / MME_DHAN_CLIENT_ID\\\",\\\"process\\\":2980,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"2026-05-15T04:42:57.637842+00:00\\\"}\\n{\\\"level\\\":\\\"INFO\\\",\\\"logger\\\":\\\"app.mme_scalpx.main\\\",\\\"message\\\":\\\"bootstrap_provider_completed provider=app.mme_scalpx.integrations.bootstrap_provider:provide mode=returned_dict runtime_instruments=1 feed_adapter=1 market_data_adapter=0 feed_adapters=1 zerodha_feed_adapter=1 dhan_feed_adapter=0 dhan_context_adapter=0 broker=1\\\",\\\"process\\\":2980,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"2026-05-15T04:42:57.874401+00:00\\\"}\\n{\\\"level\\\":\\\"INFO\\\",\\\"logger\\\":\\\"app.mme_scalpx.main\\\",\\\"message\\\":\\\"dependency_surfaces_resolved runtime_instruments=1 feed_adapter=1 market_data_adapter=1 feed_adapters=1 zerodha_feed_adapter=1 dhan_feed_adapter=0 dhan_context_adapter=0 broker=1\\\",\\\"process\\\":2980,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"2026-05-15T04:42:57.876257+00:00\\\"}\\n{\\\"level\\\":\\\"INFO\\\",\\\"logger\\\":\\\"app.mme_scalpx.main\\\",\\\"message\\\":\\\"consumer_group_bootstrap_disabled\\\",\\\"process\\\":2980,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"2026-05-15T04:42:57.971179+00:00\\\"}\\n{\\\"level\\\":\\\"INFO\\\",\\\"logger\\\":\\\"app.mme_scalpx.main\\\",\\\"message\\\":\\\"runtime_service_starting service=features module=app.mme_scalpx.services.features instance_id=features:mme-scalpx:2980 replay=False\\\",\\\"process\\\":2980,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"2026-05-15T04:42:57.971581+00:00\\\"}\\n{\\\"level\\\":\\\"INFO\\\",\\\"logger\\\":\\\"app.mme_scalpx.services.features\\\",\\\"message\\\":\\\"features_service_started instance_id=features:mme-scalpx:2980\\\",\\\"process\\\":2980,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"2026-05-15T04:42:57.977999+00:00\\\"}\\n{\\\"level\\\":\\\"WARNING\\\",\\\"logger\\\":\\\"app.mme_scalpx.main\\\",\\\"message\\\":\\\"received_shutdown_signal signum=15\\\",\\\"process\\\":2980,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"2026-05-15T04:47:47.941540+00:00\\\"}\\n{\\\"level\\\":\\\"INFO\\\",\\\"logger\\\":\\\"app.mme_scalpx.services.features\\\",\\\"message\\\":\\\"features_service_stopped\\\",\\\"process\\\":2980,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"2026-05-15T04:47:53.902221+00:00\\\"}\\n{\\\"level\\\":\\\"INFO\\\",\\\"logger\\\":\\\"app.mme_scalpx.main\\\",\\\"message\\\":\\\"runtime_service_exited service=features instance_id=features:mme-scalpx:2980 exit_code=0\\\",\\\"process\\\":2980,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"2026-05-15T04:47:53.902489+00"
  },
  {
    "line": 17,
    "window_redacted": "    \"traceback_seen\": false\n  },\n  {\n    \"decision_seen\": false,\n    \"exception_seen\": true,\n    \"exit_seen\": true,\n    \"feature_seen\": true,\n    \"mtime_iso_utc\": \"2026-05-15T04:47:48.150314+00:00\",\n    \"path\": \"/<REDACTED_SECRET_OR_TOKEN>\","
  },
  {
    "line": 25,
    "window_redacted": "    \"path\": \"/<REDACTED_SECRET_OR_TOKEN>\",\n    \"sha256\": \"<REDACTED_SECRET_OR_TOKEN>\",\n    \"size\": 1995922,\n    \"strategy_seen\": true,\n    \"tail_redacted\": \"{\\\"exc_info\\\":\\\"Traceback (most recent call last):\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 1100, in start\\\\n    self.run_once()\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 910, in run_once\\\\n    bundle = self.bridge.read_feature_bundle()\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 584, in read_feature_bundle\\\\n    return self._bundle_from_hash(raw)\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 599, in _bundle_from_hash\\\\n    FF_C.validate_family_features_payload(family_features)\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 2187, in validate_family_features_payload\\\\n    validate_stage_flags_block(payload[KEY_STAGE_FLAGS])\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 1331, in validate_stage_flags_block\\\\n    _require_exact_keys(\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 658, in _require_exact_keys\\\\n    raise FeatureFamilyContractError(\\\\<REDACTED_SECRET_OR_TOKEN>: stage_flags keys mismatch. expected=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present') actual=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present', 'snapshot_sync_valid', 'classic_provider_degraded_safe')\\\",\\\"level\\\":\\\"ERROR\\\",\\\"logger\\\":\\\"app.mme_scalpx.services.strategy\\\",\\\"message\\\":\\\"strategy_hold_bridge_loop_error\\\",\\\"process\\\":2981,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"2026-05-15T04:46:52.201954+00:00\\\"}\\n{\\\"exc_info\\\":\\\"Traceback (most recent call last):\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 1100, in start\\\\n    self.run_once()\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 910, in run_once\\\\n    bundle = self.bridge.read_feature_bundle()\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 584, in read_feature_bundle\\\\n    return self._bundle_from_hash(raw)\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 599, in _bundle_from_hash\\\\n    FF_C.validate_family_features_payload(family_features)\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 2187, in validate_family_features_payload\\\\n    validate_stage_flags_block(payload[KEY_STAGE_FLAGS])\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 1331, in validate_stage_flags_block\\\\n    _require_exact_keys(\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 658, in _require_exact_keys\\\\n    raise FeatureFamilyContractError(\\\\<REDACTED_SECRET_OR_TOKEN>: stage_flags keys mismatch. expected=('data_valid', 'data_quality_ok', 'session_eligi"
  },
  {
    "line": 26,
    "window_redacted": "    \"sha256\": \"<REDACTED_SECRET_OR_TOKEN>\",\n    \"size\": 1995922,\n    \"strategy_seen\": true,\n    \"tail_redacted\": \"{\\\"exc_info\\\":\\\"Traceback (most recent call last):\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 1100, in start\\\\n    self.run_once()\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 910, in run_once\\\\n    bundle = self.bridge.read_feature_bundle()\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 584, in read_feature_bundle\\\\n    return self._bundle_from_hash(raw)\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 599, in _bundle_from_hash\\\\n    FF_C.validate_family_features_payload(family_features)\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 2187, in validate_family_features_payload\\\\n    validate_stage_flags_block(payload[KEY_STAGE_FLAGS])\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 1331, in validate_stage_flags_block\\\\n    _require_exact_keys(\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 658, in _require_exact_keys\\\\n    raise FeatureFamilyContractError(\\\\<REDACTED_SECRET_OR_TOKEN>: stage_flags keys mismatch. expected=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present') actual=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present', 'snapshot_sync_valid', 'classic_provider_degraded_safe')\\\",\\\"level\\\":\\\"ERROR\\\",\\\"logger\\\":\\\"app.mme_scalpx.services.strategy\\\",\\\"message\\\":\\\"strategy_hold_bridge_loop_error\\\",\\\"process\\\":2981,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"2026-05-15T04:46:52.201954+00:00\\\"}\\n{\\\"exc_info\\\":\\\"Traceback (most recent call last):\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 1100, in start\\\\n    self.run_once()\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 910, in run_once\\\\n    bundle = self.bridge.read_feature_bundle()\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 584, in read_feature_bundle\\\\n    return self._bundle_from_hash(raw)\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 599, in _bundle_from_hash\\\\n    FF_C.validate_family_features_payload(family_features)\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 2187, in validate_family_features_payload\\\\n    validate_stage_flags_block(payload[KEY_STAGE_FLAGS])\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 1331, in validate_stage_flags_block\\\\n    _require_exact_keys(\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 658, in _require_exact_keys\\\\n    raise FeatureFamilyContractError(\\\\<REDACTED_SECRET_OR_TOKEN>: stage_flags keys mismatch. expected=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'risk_veto_active'"
  },
  {
    "line": 30,
    "window_redacted": "    \"traceback_seen\": true\n  },\n  {\n    \"decision_seen\": false,\n    \"exception_seen\": true,\n    \"exit_seen\": false,\n    \"feature_seen\": false,\n    \"mtime_iso_utc\": \"2026-05-13T02:24:28.012913+00:00\",\n    \"path\": \"/<REDACTED_SECRET_OR_TOKEN>\","
  },
  {
    "line": 38,
    "window_redacted": "    \"path\": \"/<REDACTED_SECRET_OR_TOKEN>\",\n    \"sha256\": \"<REDACTED_SECRET_OR_TOKEN>\",\n    \"size\": 384,\n    \"strategy_seen\": false,\n    \"tail_redacted\": \"usage: python -m app.mme_scalpx.main [-h] [--service SERVICE]\\n                                     [--bootstrap-provider BOOTSTRAP_PROVIDER]\\n                                     [--doctor] [--skip-group-bootstrap]\\n                                     [--replay-start-wall-time-ns REPLAY_START_WALL_TIME_NS]\\npython -m app.mme_scalpx.main: error: unrecognized arguments: --observe-only\",\n    \"traceback_seen\": false\n  },\n  {\n    \"decision_seen\": false,"
  },
  {
    "line": 39,
    "window_redacted": "    \"sha256\": \"<REDACTED_SECRET_OR_TOKEN>\",\n    \"size\": 384,\n    \"strategy_seen\": false,\n    \"tail_redacted\": \"usage: python -m app.mme_scalpx.main [-h] [--service SERVICE]\\n                                     [--bootstrap-provider BOOTSTRAP_PROVIDER]\\n                                     [--doctor] [--skip-group-bootstrap]\\n                                     [--replay-start-wall-time-ns REPLAY_START_WALL_TIME_NS]\\npython -m app.mme_scalpx.main: error: unrecognized arguments: --observe-only\",\n    \"traceback_seen\": false\n  },\n  {\n    \"decision_seen\": false,\n    \"exception_seen\": true,"
  },
  {
    "line": 43,
    "window_redacted": "    \"traceback_seen\": false\n  },\n  {\n    \"decision_seen\": false,\n    \"exception_seen\": true,\n    \"exit_seen\": false,\n    \"feature_seen\": false,\n    \"mtime_iso_utc\": \"2026-05-13T02:24:20.002185+00:00\",\n    \"path\": \"/<REDACTED_SECRET_OR_TOKEN>\","
  },
  {
    "line": 51,
    "window_redacted": "    \"path\": \"/<REDACTED_SECRET_OR_TOKEN>\",\n    \"sha256\": \"<REDACTED_SECRET_OR_TOKEN>\",\n    \"size\": 384,\n    \"strategy_seen\": false,\n    \"tail_redacted\": \"usage: python -m app.mme_scalpx.main [-h] [--service SERVICE]\\n                                     [--bootstrap-provider BOOTSTRAP_PROVIDER]\\n                                     [--doctor] [--skip-group-bootstrap]\\n                                     [--replay-start-wall-time-ns REPLAY_START_WALL_TIME_NS]\\npython -m app.mme_scalpx.main: error: unrecognized arguments: --observe-only\",\n    \"traceback_seen\": false\n  },\n  {\n    \"decision_seen\": false,"
  },
  {
    "line": 52,
    "window_redacted": "    \"sha256\": \"<REDACTED_SECRET_OR_TOKEN>\",\n    \"size\": 384,\n    \"strategy_seen\": false,\n    \"tail_redacted\": \"usage: python -m app.mme_scalpx.main [-h] [--service SERVICE]\\n                                     [--bootstrap-provider BOOTSTRAP_PROVIDER]\\n                                     [--doctor] [--skip-group-bootstrap]\\n                                     [--replay-start-wall-time-ns REPLAY_START_WALL_TIME_NS]\\npython -m app.mme_scalpx.main: error: unrecognized arguments: --observe-only\",\n    \"traceback_seen\": false\n  },\n  {\n    \"decision_seen\": false,\n    \"exception_seen\": true,"
  },
  {
    "line": 56,
    "window_redacted": "    \"traceback_seen\": false\n  },\n  {\n    \"decision_seen\": false,\n    \"exception_seen\": true,\n    \"exit_seen\": false,\n    \"feature_seen\": false,\n    \"mtime_iso_utc\": \"2026-05-13T02:10:26.938450+00:00\",\n    \"path\": \"/<REDACTED_SECRET_OR_TOKEN>\","
  },
  {
    "line": 64,
    "window_redacted": "    \"path\": \"/<REDACTED_SECRET_OR_TOKEN>\",\n    \"sha256\": \"<REDACTED_SECRET_OR_TOKEN>\",\n    \"size\": 384,\n    \"strategy_seen\": false,\n    \"tail_redacted\": \"usage: python -m app.mme_scalpx.main [-h] [--service SERVICE]\\n                                     [--bootstrap-provider BOOTSTRAP_PROVIDER]\\n                                     [--doctor] [--skip-group-bootstrap]\\n                                     [--replay-start-wall-time-ns REPLAY_START_WALL_TIME_NS]\\npython -m app.mme_scalpx.main: error: unrecognized arguments: --observe-only\",\n    \"traceback_seen\": false\n  },\n  {\n    \"decision_seen\": false,"
  },
  {
    "line": 65,
    "window_redacted": "    \"sha256\": \"<REDACTED_SECRET_OR_TOKEN>\",\n    \"size\": 384,\n    \"strategy_seen\": false,\n    \"tail_redacted\": \"usage: python -m app.mme_scalpx.main [-h] [--service SERVICE]\\n                                     [--bootstrap-provider BOOTSTRAP_PROVIDER]\\n                                     [--doctor] [--skip-group-bootstrap]\\n                                     [--replay-start-wall-time-ns REPLAY_START_WALL_TIME_NS]\\npython -m app.mme_scalpx.main: error: unrecognized arguments: --observe-only\",\n    \"traceback_seen\": false\n  },\n  {\n    \"decision_seen\": false,\n    \"exception_seen\": true,"
  },
  {
    "line": 69,
    "window_redacted": "    \"traceback_seen\": false\n  },\n  {\n    \"decision_seen\": false,\n    \"exception_seen\": true,\n    \"exit_seen\": false,\n    \"feature_seen\": false,\n    \"mtime_iso_utc\": \"2026-05-13T02:10:21.977998+00:00\",\n    \"path\": \"/<REDACTED_SECRET_OR_TOKEN>\","
  },
  {
    "line": 77,
    "window_redacted": "    \"path\": \"/<REDACTED_SECRET_OR_TOKEN>\",\n    \"sha256\": \"<REDACTED_SECRET_OR_TOKEN>\",\n    \"size\": 384,\n    \"strategy_seen\": false,\n    \"tail_redacted\": \"usage: python -m app.mme_scalpx.main [-h] [--service SERVICE]\\n                                     [--bootstrap-provider BOOTSTRAP_PROVIDER]\\n                                     [--doctor] [--skip-group-bootstrap]\\n                                     [--replay-start-wall-time-ns REPLAY_START_WALL_TIME_NS]\\npython -m app.mme_scalpx.main: error: unrecognized arguments: --observe-only\",\n    \"traceback_seen\": false\n  },\n  {\n    \"decision_seen\": false,"
  },
  {
    "line": 78,
    "window_redacted": "    \"sha256\": \"<REDACTED_SECRET_OR_TOKEN>\",\n    \"size\": 384,\n    \"strategy_seen\": false,\n    \"tail_redacted\": \"usage: python -m app.mme_scalpx.main [-h] [--service SERVICE]\\n                                     [--bootstrap-provider BOOTSTRAP_PROVIDER]\\n                                     [--doctor] [--skip-group-bootstrap]\\n                                     [--replay-start-wall-time-ns REPLAY_START_WALL_TIME_NS]\\npython -m app.mme_scalpx.main: error: unrecognized arguments: --observe-only\",\n    \"traceback_seen\": false\n  },\n  {\n    \"decision_seen\": false,\n    \"exception_seen\": true,"
  },
  {
    "line": 82,
    "window_redacted": "    \"traceback_seen\": false\n  },\n  {\n    \"decision_seen\": false,\n    \"exception_seen\": true,\n    \"exit_seen\": false,\n    \"feature_seen\": false,\n    \"mtime_iso_utc\": \"2026-05-13T02:10:17.575598+00:00\",\n    \"path\": \"/<REDACTED_SECRET_OR_TOKEN>\","
  },
  {
    "line": 90,
    "window_redacted": "    \"path\": \"/<REDACTED_SECRET_OR_TOKEN>\",\n    \"sha256\": \"<REDACTED_SECRET_OR_TOKEN>\",\n    \"size\": 1016,\n    \"strategy_seen\": false,\n    \"tail_redacted\": \"===== PFEEDCHECK STRICT =====\\n2026-05-13T07:40:12+05:30\\n\\n===== PROCESS STATUS =====\\nprocess_alive=False\\npidfile_pid=missing\\n\\n===== LATEST LOG =====\\nno pfeeds live capture log found\\n\\n===== REDIS STREAM RECORDING CHECK =====\\nredis_ping = True\\nlock_feeds_owner = None\\nlock_feeds_ttl_ms = -2\\n\\nfut_zerodha              ticks:mme:fut:zerodha:stream               xlen=0        growth_5s=0\\nfut_dhan                 ticks:mme:fut:dhan:stream                  xlen=0        growth_5s=0\\nopt_selected_zerodha     ticks:mme:opt:selected:zerodha:stream      xlen=0        growth_5s=0\\nopt_selected_dhan        ticks:mme:opt:selected:dhan:stream         xlen=0        growth_5s=0\\nopt_context_dhan         ticks:mme:opt:context:dhan:stream          xlen=0        growth_5s=0\\nhealth                   system:health:stream                       xlen=4332     growth_5s=0\\nerrors                   system:errors:stream                       xlen=10006    growth_5s=0\\n\\nstatus=NOT_HEALTHY_PROCESS_DEAD\\nremark=pfeeds process is not alive.\",\n    \"traceback_seen\": false\n  },\n  {\n    \"decision_seen\": false,"
  }
]
```

Required checks:

```json
{
  "all_watched_sources_compile": true,
  "latest_r5w_proof_found": true,
  "no_broker_order": true,
  "no_lock_clear_delete": true,
  "no_paper_live": true,
  "no_patch": true,
  "no_redis_write": true,
  "no_restore": true,
  "no_risk_execution_order_process_visible": true,
  "no_service_start_restart_stop": true,
  "orders_mme_stream_zero_or_absent": true,
  "position_flat": true,
  "r5w_logged_exit_or_error_condition_found": true,
  "watched_sources_unchanged_by_this_batch": true
}
```

Failures:

```json
[]
```

Proof:
- /home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5X_read_only_classify_strategy_features_exit_log_findings_before_patch_plan_no_patch_no_restart_no_order_no_paper_20260515_102508.json
