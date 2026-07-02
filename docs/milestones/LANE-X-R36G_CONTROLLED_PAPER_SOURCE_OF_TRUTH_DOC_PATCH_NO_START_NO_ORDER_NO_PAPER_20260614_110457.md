# LANE-X-R36G_CONTROLLED_PAPER_SOURCE_OF_TRUTH_DOC_PATCH_NO_START_NO_ORDER_NO_PAPER_20260614_110457

classification: PASS_LANE_X_R36G_CONTROLLED_PAPER_SOURCE_OF_TRUTH_DOC_PATCHED_NO_START_NO_ORDER_NO_PAPER
proof: `run/proofs/LANE-X-R36G_CONTROLLED_PAPER_SOURCE_OF_TRUTH_DOC_PATCH_NO_START_NO_ORDER_NO_PAPER_20260614_110457.json`
doc: `docs/runbooks/CONTROLLED_PAPER_SOURCE_OF_TRUTH.md`
backup: `run/_code_backups/LANE-X-R36G_CONTROLLED_PAPER_SOURCE_OF_TRUTH_DOC_PATCH_NO_START_NO_ORDER_NO_PAPER_20260614_110457_CONTROLLED_PAPER_SOURCE_OF_TRUTH.md.bak`

pstatus_rc=0 doc_check_rc=0 marker_rc=0
safety pre=0/0/0 post=0/0/0 proc=0/0 replay_proc=0

## Interpretation
- This documents controlled_paper_route.py and bin/pstatus as the controlled-paper source of truth.
- It does not arm paper.
- It does not start risk/execution/MME services.
- Paper remains fail-closed.

## Doc check
{
  "all_needles_present": true,
  "doc": "docs/runbooks/CONTROLLED_PAPER_SOURCE_OF_TRUTH.md",
  "exists": true,
  "needle_hits": {
    "CONTROLLED_PAPER_RUNTIME_NOT_ALLOWED": true,
    "OBSERVE_ONLY_ACTIVE": true,
    "PNL_COMPUTED_REPLAY_ONLY_SYNTHETIC_SHADOW_MODEL_R35C_R5C_NOT_BROKER_NOT_PAPER_NOT_LIVE": true,
    "bin/pstatus": true,
    "controlled_paper_route.py": true,
    "explicit user approval": true,
    "fail-closed": true
  },
  "sha256": "1b10dd87931a957defbb75abeca7a761ca7bac227903e2230b49ec852d7015e6"
}

## Doc check errors

## Doc markers
5:Controlled paper is fail-closed by default.
10:app/mme_scalpx/services/controlled_paper_route.py
16:bin/pstatus
41:OBSERVE_ONLY_ACTIVE
42:CONTROLLED_PAPER_RUNTIME_NOT_ALLOWED
66:explicit user approval for micro-batch
97:PNL_COMPUTED_REPLAY_ONLY_SYNTHETIC_SHADOW_MODEL_R35C_R5C_NOT_BROKER_NOT_PAPER_NOT_LIVE

## pstatus
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
  "created_at": "2026-06-14T05:34:57.655601+00:00",
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
