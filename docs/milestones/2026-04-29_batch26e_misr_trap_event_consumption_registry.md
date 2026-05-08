# Batch 26E — MISR Trap-Event Consumption Registry

Date: 2026-04-29

## Verdict

- misr_trap_event_consumption_registry_ok: `True`
- trap_event_id_deterministic_parse_proven: `True`
- event_consumed_on_entry_order_sent: `True`
- same_event_retry_blocked: `True`
- older_same_zone_retry_blocked: `True`
- new_event_or_new_zone_allowed: `True`
- registry_resets_on_session_change: `True`
- paper_armed_approved: `False`
- real_live_approved: `False`

## Files Patched

- `app/mme_scalpx/services/strategy_family/misr.py`

## Files Inspected

- `app/mme_scalpx/services/feature_family/misr_surface.py`
- `app/mme_scalpx/services/strategy_family/misr.py`
- `app/mme_scalpx/services/strategy.py`
- `app/mme_scalpx/services/features.py`
- `app/mme_scalpx/services/risk.py`
- `app/mme_scalpx/services/execution.py`

## Dynamic Proof

```json
{
  "blocked_result_forces_hold": {
    "pass": true,
    "result": {
      "action": "HOLD",
      "action_before_misr_trap_consumed_block": "ENTER_CALL",
      "blocker_reasons": [
        "MISR_TRAP_EVENT_CONSUMED_NO_RETRY"
      ],
      "blockers": [
        "MISR_TRAP_EVENT_CONSUMED_NO_RETRY"
      ],
      "candidate": false,
      "eligible": false,
      "entry_allowed": false,
      "misr_trap_event_consumed_blocked": true,
      "misr_trap_event_consumption_registry_detail": "{'blocked': True, 'reason': 'MISR_TRAP_EVENT_CONSUMED_NO_RETRY', 'parsed': {'valid': True, 'trap_event_id': 'CALL|ORB_LOW_001|1714200000000|1714200001500', 'side': 'CALL', 'zone_id': 'ORB_LOW_001', 'zone_side_key': 'CALL|ORB_LOW_001', 'fake_break_start_ts_epoch_ms': 1714200000000, 'fake_break_extreme_ts_epoch_ms': 1714200001500}, 'existing': {'trap_event_id': 'CALL|ORB_LOW_001|1714200000000|1714200001500', 'side': 'CALL', 'zone_id': 'ORB_LOW_001', 'zone_side_key': 'CALL|ORB_LOW_001', 'fake_break_start_ts_epoch_ms': 1714200000000, 'fake_break_extreme_ts_epoch_ms': 1714200001500, 'consume_reason': 'entry_order_sent'}}",
      "misr_trap_event_consumption_registry_reason": "MISR_TRAP_EVENT_CONSUMED_NO_RETRY",
      "reason": "MISR_TRAP_EVENT_CONSUMED_NO_RETRY",
      "reason_code": "MISR_TRAP_EVENT_CONSUMED_NO_RETRY",
      "trap_event_id": "CALL|ORB_LOW_001|1714200000000|1714200001500"
    }
  },
  "deterministic_parse": {
    "parsed": {
      "fake_break_extreme_ts_epoch_ms": 1714200001500,
      "fake_break_start_ts_epoch_ms": 1714200000000,
      "side": "CALL",
      "trap_event_id": "CALL|ORB_LOW_001|1714200000000|1714200001500",
      "valid": true,
      "zone_id": "ORB_LOW_001",
      "zone_side_key": "CALL|ORB_LOW_001"
    },
    "pass": true
  },
  "event_consumed_on_entry_order_sent": {
    "consume": {
      "consumed": true,
      "record": {
        "consume_reason": "entry_order_sent",
        "fake_break_extreme_ts_epoch_ms": 1714200001500,
        "fake_break_start_ts_epoch_ms": 1714200000000,
        "side": "CALL",
        "trap_event_id": "CALL|ORB_LOW_001|1714200000000|1714200001500",
        "zone_id": "ORB_LOW_001",
        "zone_side_key": "CALL|ORB_LOW_001"
      }
    },
    "pass": true
  },
  "first_event_pre_consume_allowed": {
    "pass": true,
    "status": {
      "blocked": false,
      "parsed": {
        "fake_break_extreme_ts_epoch_ms": 1714200001500,
        "fake_break_start_ts_epoch_ms": 1714200000000,
        "side": "CALL",
        "trap_event_id": "CALL|ORB_LOW_001|1714200000000|1714200001500",
        "valid": true,
        "zone_id": "ORB_LOW_001",
        "zone_side_key": "CALL|ORB_LOW_001"
      },
      "reason": ""
    }
  },
  "new_zone_event_allowed": {
    "pass": true,
    "status": {
      "blocked": false,
      "parsed": {
        "fake_break_extreme_ts_epoch_ms": 1714200001500,
        "fake_break_start_ts_epoch_ms": 1714200000000,
        "side": "CALL",
        "trap_event_id": "CALL|SWING_LOW_002|1714200000000|1714200001500",
        "valid": true,
        "zone_id": "SWING_LOW_002",
        "zone_side_key": "CALL|SWING_LOW_002"
      },
      "reason": ""
    }
  },
  "newer_event_blocks_after_own_consumption": {
    "consume": {
      "consumed": true,
      "record": {
        "consume_reason": "later_new_event_entry_order_sent",
        "fake_break_extreme_ts_epoch_ms": 1714200003000,
        "fake_break_start_ts_epoch_ms": 1714200002000,
        "side": "CALL",
        "trap_event_id": "CALL|ORB_LOW_001|1714200002000|1714200003000",
        "zone_id": "ORB_LOW_001",
        "zone_side_key": "CALL|ORB_LOW_001"
      }
    },
    "pass": true,
    "status": {
      "blocked": true,
      "existing": {
        "consume_reason": "later_new_event_entry_order_sent",
        "fake_break_extreme_ts_epoch_ms": 1714200003000,
        "fake_break_start_ts_epoch_ms": 1714200002000,
        "side": "CALL",
        "trap_event_id": "CALL|ORB_LOW_001|1714200002000|1714200003000",
        "zone_id": "ORB_LOW_001",
        "zone_side_key": "CALL|ORB_LOW_001"
      },
      "parsed": {
        "fake_break_extreme_ts_epoch_ms": 1714200003000,
        "fake_break_start_ts_epoch_ms": 1714200002000,
        "side": "CALL",
        "trap_event_id": "CALL|ORB_LOW_001|1714200002000|1714200003000",
        "valid": true,
        "zone_id": "ORB_LOW_001",
        "zone_side_key": "CALL|ORB_LOW_001"
      },
      "reason": "MISR_TRAP_EVENT_CONSUMED_NO_RETRY"
    }
  },
  "newer_same_zone_allowed_as_new_event": {
    "pass": true,
    "status": {
      "blocked": false,
      "parsed": {
        "fake_break_extreme_ts_epoch_ms": 1714200003000,
        "fake_break_start_ts_epoch_ms": 1714200002000,
        "side": "CALL",
        "trap_event_id": "CALL|ORB_LOW_001|1714200002000|1714200003000",
        "valid": true,
        "zone_id": "ORB_LOW_001",
        "zone_side_key": "CALL|ORB_LOW_001"
      },
      "reason": ""
    }
  },
  "older_same_zone_retry_blocked": {
    "pass": true,
    "status": {
      "blocked": true,
      "parsed": {
        "fake_break_extreme_ts_epoch_ms": 1714200000100,
        "fake_break_start_ts_epoch_ms": 1714199999000,
        "side": "CALL",
        "trap_event_id": "CALL|ORB_LOW_001|1714199999000|1714200000100",
        "valid": true,
        "zone_id": "ORB_LOW_001",
        "zone_side_key": "CALL|ORB_LOW_001"
      },
      "reason": "MISR_TRAP_EVENT_CONSUMED_NO_RETRY",
      "zone_latest": {
        "consume_reason": "entry_order_sent",
        "fake_break_extreme_ts_epoch_ms": 1714200001500,
        "fake_break_start_ts_epoch_ms": 1714200000000,
        "side": "CALL",
        "trap_event_id": "CALL|ORB_LOW_001|1714200000000|1714200001500",
        "zone_id": "ORB_LOW_001",
        "zone_side_key": "CALL|ORB_LOW_001"
      }
    }
  },
  "same_event_retry_blocked": {
    "pass": true,
    "status": {
      "blocked": true,
      "existing": {
        "consume_reason": "entry_order_sent",
        "fake_break_extreme_ts_epoch_ms": 1714200001500,
        "fake_break_start_ts_epoch_ms": 1714200000000,
        "side": "CALL",
        "trap_event_id": "CALL|ORB_LOW_001|1714200000000|1714200001500",
        "zone_id": "ORB_LOW_001",
        "zone_side_key": "CALL|ORB_LOW_001"
      },
      "parsed": {
        "fake_break_extreme_ts_epoch_ms": 1714200001500,
        "fake_break_start_ts_epoch_ms": 1714200000000,
        "side": "CALL",
        "trap_event_id": "CALL|ORB_LOW_001|1714200000000|1714200001500",
        "valid": true,
        "zone_id": "ORB_LOW_001",
        "zone_side_key": "CALL|ORB_LOW_001"
      },
      "reason": "MISR_TRAP_EVENT_CONSUMED_NO_RETRY"
    }
  },
  "session_reset_clears_registry": {
    "after_session_change": {
      "blocked": false,
      "parsed": {
        "fake_break_extreme_ts_epoch_ms": 1714200001500,
        "fake_break_start_ts_epoch_ms": 1714200000000,
        "side": "CALL",
        "trap_event_id": "CALL|ORB_LOW_001|1714200000000|1714200001500",
        "valid": true,
        "zone_id": "ORB_LOW_001",
        "zone_side_key": "CALL|ORB_LOW_001"
      },
      "reason": ""
    },
    "before_session_change": {
      "blocked": true,
      "existing": {
        "consume_reason": "entry_order_sent",
        "fake_break_extreme_ts_epoch_ms": 1714200001500,
        "fake_break_start_ts_epoch_ms": 1714200000000,
        "side": "CALL",
        "trap_event_id": "CALL|ORB_LOW_001|1714200000000|1714200001500",
        "zone_id": "ORB_LOW_001",
        "zone_side_key": "CALL|ORB_LOW_001"
      },
      "parsed": {
        "fake_break_extreme_ts_epoch_ms": 1714200001500,
        "fake_break_start_ts_epoch_ms": 1714200000000,
        "side": "CALL",
        "trap_event_id": "CALL|ORB_LOW_001|1714200000000|1714200001500",
        "valid": true,
        "zone_id": "ORB_LOW_001",
        "zone_side_key": "CALL|ORB_LOW_001"
      },
      "reason": "MISR_TRAP_EVENT_CONSUMED_NO_RETRY"
    },
    "pass": true
  }
}
```

## Artifacts

- `run/proofs/proof_misr_trap_event_consumption_registry.json`
- `run/proofs/proof_misr_trap_event_consumption_registry_patch_step.json`
- backup: `run/_code_backups/batch26e_misr_trap_event_registry_20260429_222807`

## Continuation

Next recommended batch: `26F — MISO burst-event consumption registry`.

Do not enable paper_armed. Do not enable real live. Do not start controlled paper runtime chain from this batch.
