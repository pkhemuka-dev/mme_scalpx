# LANE-X-R36B_PSTATUS_FAIL_CLOSED_RUNTIME_VERDICT_PATCH_NO_START_NO_ORDER_NO_PAPER_20260614_005215

classification: PASS_LANE_X_R36B_PSTATUS_FAIL_CLOSED_RUNTIME_VERDICT_PATCHED_NO_START_NO_ORDER_NO_PAPER
proof: `run/proofs/LANE-X-R36B_PSTATUS_FAIL_CLOSED_RUNTIME_VERDICT_PATCH_NO_START_NO_ORDER_NO_PAPER_20260614_005215.json`
pstatus: `bin/pstatus`
backup: `run/_code_backups/LANE-X-R36B_PSTATUS_FAIL_CLOSED_RUNTIME_VERDICT_PATCH_NO_START_NO_ORDER_NO_PAPER_20260614_005215_bin_pstatus.bak`

patch_rc=0 compile_rc=0 sample_rc=0 marker_rc=0
safety pre=0/0/0 post=0/0/0 proc=0/0 replay_proc=0

## Markers
3:  "classification": "PSTATUS_FAIL_CLOSED_RUNTIME_VERDICT_READY",
14:      "reason": "CONTROLLED_PAPER_RUNTIME_NOT_ALLOWED",
30:  "paper_runtime_verdict": {
37:    "paper_route_allowed": false,
39:    "reason": "OBSERVE_ONLY_ACTIVE",

## pstatus sample
{
  "broker_order_attempted": false,
  "classification": "PSTATUS_FAIL_CLOSED_RUNTIME_VERDICT_READY",
  "controlled_paper_route_imported": {
    "function": "build_fail_closed_controlled_paper_verdict",
    "import_ok": true,
    "result": {
      "allowed": false,
      "broker_live_blocked": true,
      "controlled_runtime_allowed": false,
      "observe_only": false,
      "paper_armed": false,
      "paper_enabled": false,
      "reason": "CONTROLLED_PAPER_RUNTIME_NOT_ALLOWED",
      "scope_ack_ok": false
    }
  },
  "created_at": "2026-06-13T19:22:15.933350+00:00",
  "env": {
    "B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY": "1",
    "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME": "",
    "SCALPX_CONTROLLED_PAPER_ARMED": "",
    "SCALPX_CONTROLLED_PAPER_SCOPE_ACK": "",
    "SCALPX_ENABLE_LIVE": "",
    "SCALPX_ENABLE_PAPER": "",
    "SCALPX_OBSERVE_ONLY": "1",
    "SCALPX_PAPER_ARMED": ""
  },
  "paper_live_enabled": false,
  "paper_runtime_verdict": {
    "controlled_runtime_allowed": false,
    "fail_closed": true,
    "live_enabled": false,
    "observe_only": true,
    "paper_armed": false,
    "paper_enabled": false,
    "paper_route_allowed": false,
    "position_flat_verified": false,
    "reason": "OBSERVE_ONLY_ACTIVE",
    "scope_ack_present": false
  },
  "project_root": "/home/Lenovo/scalpx/projects/mme_scalpx",
  "redis_delete_attempted": false,
  "redis_write_attempted": false,
  "safety": {
    "no_execution_stream": true,
    "no_order_stream": true,
    "no_risk_stream": true,
    "orders_risk_execution": "0/0/0",
    "processes": {
      "execution": 0,
      "replay": 0,
      "risk": 0
    },
    "risk_execution_not_running": true,
    "streams": {
      "execution": 0,
      "orders": 0,
      "risk": 0
    }
  },
  "schema_version": "pstatus_fail_closed_runtime_verdict_v1"
}

## pstatus stderr

## Compile log
