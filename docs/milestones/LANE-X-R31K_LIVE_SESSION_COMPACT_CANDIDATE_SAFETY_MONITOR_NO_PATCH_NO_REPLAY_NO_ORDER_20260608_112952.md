# LANE-X-R31K_LIVE_SESSION_COMPACT_CANDIDATE_SAFETY_MONITOR_NO_PATCH_NO_REPLAY_NO_ORDER_20260608_112952
2026-06-08T11:29:52+05:30

LAW=LIVE_SESSION_ONLY_COMPACT_MONITOR_NO_PATCH_NO_SOURCE_AUDIT_NO_REPLAY_NO_START_NO_STOP_NO_ORDER_NO_REDIS_DELETE_NO_PAPER_NO_RISK_NO_EXECUTION

## Safety before
58925 /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main
orders_stream_len_before=0
risk_stream_len_before=0
execution_stream_len_before=0

## 5-minute compact growth monitor
before fut=55 opt=392 features=42 decisions=2780
LIVE_COMPACT i=1 now=2026-06-08T11:30:22+05:30 fut=67 opt=446 features=48 decisions=2810 orders=0 risk=0 execution=0
LIVE_COMPACT i=2 now=2026-06-08T11:30:52+05:30 fut=78 opt=500 features=54 decisions=2840 orders=0 risk=0 execution=0
LIVE_COMPACT i=3 now=2026-06-08T11:31:22+05:30 fut=88 opt=557 features=60 decisions=2870 orders=0 risk=0 execution=0
LIVE_COMPACT i=4 now=2026-06-08T11:31:52+05:30 fut=99 opt=613 features=67 decisions=2901 orders=0 risk=0 execution=0
LIVE_COMPACT i=5 now=2026-06-08T11:32:22+05:30 fut=104 opt=672 features=5 decisions=2932 orders=0 risk=0 execution=0
LIVE_COMPACT i=6 now=2026-06-08T11:32:52+05:30 fut=2 opt=11 features=2 decisions=2943 orders=0 risk=0 execution=0
LIVE_COMPACT i=7 now=2026-06-08T11:33:22+05:30 fut=9 opt=75 features=8 decisions=2975 orders=0 risk=0 execution=0
LIVE_COMPACT i=8 now=2026-06-08T11:33:52+05:30 fut=20 opt=128 features=15 decisions=3006 orders=0 risk=0 execution=0
LIVE_COMPACT i=9 now=2026-06-08T11:34:22+05:30 fut=28 opt=185 features=22 decisions=3037 orders=0 risk=0 execution=0
LIVE_COMPACT i=10 now=2026-06-08T11:34:53+05:30 fut=0 opt=236 features=0 decisions=3067 orders=0 risk=0 execution=0

## Compact decision summary only
{
  "actions": {
    "HOLD": 120
  },
  "decision_rows_sampled": 120,
  "latest_action": "HOLD",
  "latest_data_valid": "0",
  "latest_hold_only": "1",
  "latest_provider_ready_classic": "0",
  "latest_reason": "hold_only_family_features_consumer_bridge",
  "latest_safe_to_consume": "1",
  "max_activation_candidate_count": 0,
  "max_activation_selected_score": 0.0,
  "top_reasons": {
    "hold_only_family_features_consumer_bridge": 120
  }
}
AUDIT_RC=0

## Safety after
orders_stream_len_after=0
risk_stream_len_after=0
execution_stream_len_after=0
CLASSIFICATION=PASS_R31K_LIVE_SESSION_COMPACT_MONITOR_SAFE_CONTINUE_OBSERVE_ONLY
