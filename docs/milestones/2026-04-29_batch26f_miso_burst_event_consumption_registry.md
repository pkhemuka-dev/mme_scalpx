# Batch 26F — MISO Burst-Event Consumption Registry

Date: 2026-04-29

## Verdict

- miso_burst_event_consumption_registry_ok: `True`
- deterministic_burst_event_id_proven: `True`
- burst_consumed_on_entry_order_sent: `True`
- same_burst_retry_blocked: `True`
- older_same_symbol_retry_blocked: `True`
- new_burst_or_new_symbol_allowed: `True`
- dhan_option_context_mandatory_proven: `True`
- registry_resets_on_session_change: `True`
- paper_armed_approved: `False`
- real_live_approved: `False`

## Files Patched

- `app/mme_scalpx/services/feature_family/miso_surface.py`
- `app/mme_scalpx/services/strategy_family/miso.py`

## Files Inspected

- `app/mme_scalpx/services/feature_family/miso_surface.py`
- `app/mme_scalpx/services/strategy_family/miso.py`
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
      "action_before_miso_burst_consumed_block": "ENTER_CALL",
      "blocker_reasons": [
        "MISO_BURST_EVENT_CONSUMED_NO_RETRY"
      ],
      "blockers": [
        "MISO_BURST_EVENT_CONSUMED_NO_RETRY"
      ],
      "burst_event_id": "MISO|CALL|NIFTY2650524050CE|1714200000000|1714200001500",
      "candidate": false,
      "eligible": false,
      "entry_allowed": false,
      "miso_burst_event_consumed_blocked": true,
      "miso_burst_event_consumption_registry_detail": "{'blocked': True, 'reason': 'MISO_BURST_EVENT_CONSUMED_NO_RETRY', 'parsed': {'valid': True, 'burst_event_id': 'MISO|CALL|NIFTY2650524050CE|1714200000000|1714200001500', 'family': 'MISO', 'side': 'CALL', 'symbol': 'NIFTY2650524050CE', 'symbol_side_key': 'CALL|NIFTY2650524050CE', 'burst_start_ts_epoch_ms': 1714200000000, 'burst_extreme_ts_epoch_ms': 1714200001500}, 'existing': {'burst_event_id': 'MISO|CALL|NIFTY2650524050CE|1714200000000|1714200001500', 'side': 'CALL', 'symbol': 'NIFTY2650524050CE', 'symbol_side_key': 'CALL|NIFTY2650524050CE', 'burst_start_ts_epoch_ms': 1714200000000, 'burst_extreme_ts_epoch_ms': 1714200001500, 'consume_reason': 'entry_order_sent'}}",
      "miso_burst_event_consumption_registry_reason": "MISO_BURST_EVENT_CONSUMED_NO_RETRY",
      "miso_dhan_context_required_blocked": false,
      "reason": "MISO_BURST_EVENT_CONSUMED_NO_RETRY",
      "reason_code": "MISO_BURST_EVENT_CONSUMED_NO_RETRY"
    }
  },
  "burst_consumed_on_entry_order_sent": {
    "consume": {
      "consumed": true,
      "record": {
        "burst_event_id": "MISO|CALL|NIFTY2650524050CE|1714200000000|1714200001500",
        "burst_extreme_ts_epoch_ms": 1714200001500,
        "burst_start_ts_epoch_ms": 1714200000000,
        "consume_reason": "entry_order_sent",
        "side": "CALL",
        "symbol": "NIFTY2650524050CE",
        "symbol_side_key": "CALL|NIFTY2650524050CE"
      }
    },
    "pass": true
  },
  "deterministic_surface_burst_event_id": {
    "attached": {
      "burst_detected": true,
      "burst_event_id": "MISO|CALL|NIFTY2650524050CE|1714200000000|1714200001500",
      "burst_event_id_source": "batch26f_deterministic_surface",
      "burst_extreme_ts_epoch_ms": 1714200001500,
      "burst_start_ts_epoch_ms": 1714200000000,
      "dhan_context_ready": true,
      "entry_allowed": true,
      "miso_burst_event_id": "MISO|CALL|NIFTY2650524050CE|1714200000000|1714200001500",
      "option_context_status": "HEALTHY",
      "selected_option_provider": "DHAN",
      "selected_option_symbol": "NIFTY2650524050CE",
      "side": "CALL"
    },
    "built_1": "MISO|CALL|NIFTY2650524050CE|1714200000000|1714200001500",
    "built_2": "MISO|CALL|NIFTY2650524050CE|1714200000000|1714200001500",
    "pass": true
  },
  "dhan_context_mandatory_negative": {
    "pass": true
  },
  "dhan_context_mandatory_positive": {
    "pass": true
  },
  "dhan_missing_result_forces_hold": {
    "pass": true,
    "result": {
      "action": "HOLD",
      "action_before_miso_burst_consumed_block": "ENTER_CALL",
      "blocker_reasons": [
        "MISO_DHAN_CONTEXT_REQUIRED"
      ],
      "blockers": [
        "MISO_DHAN_CONTEXT_REQUIRED"
      ],
      "burst_event_id": "MISO|CALL|NIFTY2650524100CE|1714200000000|1714200001500",
      "candidate": false,
      "eligible": false,
      "entry_allowed": false,
      "miso_burst_event_consumed_blocked": false,
      "miso_burst_event_consumption_registry_detail": "{'reason': 'Dhan context missing'}",
      "miso_burst_event_consumption_registry_reason": "MISO_DHAN_CONTEXT_REQUIRED",
      "miso_dhan_context_required_blocked": true,
      "reason": "MISO_DHAN_CONTEXT_REQUIRED",
      "reason_code": "MISO_DHAN_CONTEXT_REQUIRED"
    }
  },
  "first_burst_pre_consume_allowed": {
    "pass": true,
    "status": {
      "blocked": false,
      "parsed": {
        "burst_event_id": "MISO|CALL|NIFTY2650524050CE|1714200000000|1714200001500",
        "burst_extreme_ts_epoch_ms": 1714200001500,
        "burst_start_ts_epoch_ms": 1714200000000,
        "family": "MISO",
        "side": "CALL",
        "symbol": "NIFTY2650524050CE",
        "symbol_side_key": "CALL|NIFTY2650524050CE",
        "valid": true
      },
      "reason": ""
    }
  },
  "leaf_burst_event_id_parse": {
    "parsed": {
      "burst_event_id": "MISO|CALL|NIFTY2650524050CE|1714200000000|1714200001500",
      "burst_extreme_ts_epoch_ms": 1714200001500,
      "burst_start_ts_epoch_ms": 1714200000000,
      "family": "MISO",
      "side": "CALL",
      "symbol": "NIFTY2650524050CE",
      "symbol_side_key": "CALL|NIFTY2650524050CE",
      "valid": true
    },
    "pass": true
  },
  "new_symbol_burst_allowed": {
    "pass": true,
    "status": {
      "blocked": false,
      "parsed": {
        "burst_event_id": "MISO|CALL|NIFTY2650524100CE|1714200000000|1714200001500",
        "burst_extreme_ts_epoch_ms": 1714200001500,
        "burst_start_ts_epoch_ms": 1714200000000,
        "family": "MISO",
        "side": "CALL",
        "symbol": "NIFTY2650524100CE",
        "symbol_side_key": "CALL|NIFTY2650524100CE",
        "valid": true
      },
      "reason": ""
    }
  },
  "newer_burst_blocks_after_own_consumption": {
    "consume": {
      "consumed": true,
      "record": {
        "burst_event_id": "MISO|CALL|NIFTY2650524050CE|1714200002000|1714200003000",
        "burst_extreme_ts_epoch_ms": 1714200003000,
        "burst_start_ts_epoch_ms": 1714200002000,
        "consume_reason": "later_new_burst_entry_order_sent",
        "side": "CALL",
        "symbol": "NIFTY2650524050CE",
        "symbol_side_key": "CALL|NIFTY2650524050CE"
      }
    },
    "pass": true,
    "status": {
      "blocked": true,
      "existing": {
        "burst_event_id": "MISO|CALL|NIFTY2650524050CE|1714200002000|1714200003000",
        "burst_extreme_ts_epoch_ms": 1714200003000,
        "burst_start_ts_epoch_ms": 1714200002000,
        "consume_reason": "later_new_burst_entry_order_sent",
        "side": "CALL",
        "symbol": "NIFTY2650524050CE",
        "symbol_side_key": "CALL|NIFTY2650524050CE"
      },
      "parsed": {
        "burst_event_id": "MISO|CALL|NIFTY2650524050CE|1714200002000|1714200003000",
        "burst_extreme_ts_epoch_ms": 1714200003000,
        "burst_start_ts_epoch_ms": 1714200002000,
        "family": "MISO",
        "side": "CALL",
        "symbol": "NIFTY2650524050CE",
        "symbol_side_key": "CALL|NIFTY2650524050CE",
        "valid": true
      },
      "reason": "MISO_BURST_EVENT_CONSUMED_NO_RETRY"
    }
  },
  "newer_same_symbol_allowed_as_new_burst": {
    "pass": true,
    "status": {
      "blocked": false,
      "parsed": {
        "burst_event_id": "MISO|CALL|NIFTY2650524050CE|1714200002000|1714200003000",
        "burst_extreme_ts_epoch_ms": 1714200003000,
        "burst_start_ts_epoch_ms": 1714200002000,
        "family": "MISO",
        "side": "CALL",
        "symbol": "NIFTY2650524050CE",
        "symbol_side_key": "CALL|NIFTY2650524050CE",
        "valid": true
      },
      "reason": ""
    }
  },
  "older_same_symbol_retry_blocked": {
    "pass": true,
    "status": {
      "blocked": true,
      "parsed": {
        "burst_event_id": "MISO|CALL|NIFTY2650524050CE|1714199999000|1714200000100",
        "burst_extreme_ts_epoch_ms": 1714200000100,
        "burst_start_ts_epoch_ms": 1714199999000,
        "family": "MISO",
        "side": "CALL",
        "symbol": "NIFTY2650524050CE",
        "symbol_side_key": "CALL|NIFTY2650524050CE",
        "valid": true
      },
      "reason": "MISO_BURST_EVENT_CONSUMED_NO_RETRY",
      "symbol_latest": {
        "burst_event_id": "MISO|CALL|NIFTY2650524050CE|1714200000000|1714200001500",
        "burst_extreme_ts_epoch_ms": 1714200001500,
        "burst_start_ts_epoch_ms": 1714200000000,
        "consume_reason": "entry_order_sent",
        "side": "CALL",
        "symbol": "NIFTY2650524050CE",
        "symbol_side_key": "CALL|NIFTY2650524050CE"
      }
    }
  },
  "same_burst_retry_blocked": {
    "pass": true,
    "status": {
      "blocked": true,
      "existing": {
        "burst_event_id": "MISO|CALL|NIFTY2650524050CE|1714200000000|1714200001500",
        "burst_extreme_ts_epoch_ms": 1714200001500,
        "burst_start_ts_epoch_ms": 1714200000000,
        "consume_reason": "entry_order_sent",
        "side": "CALL",
        "symbol": "NIFTY2650524050CE",
        "symbol_side_key": "CALL|NIFTY2650524050CE"
      },
      "parsed": {
        "burst_event_id": "MISO|CALL|NIFTY2650524050CE|1714200000000|1714200001500",
        "burst_extreme_ts_epoch_ms": 1714200001500,
        "burst_start_ts_epoch_ms": 1714200000000,
        "family": "MISO",
        "side": "CALL",
        "symbol": "NIFTY2650524050CE",
        "symbol_side_key": "CALL|NIFTY2650524050CE",
        "valid": true
      },
      "reason": "MISO_BURST_EVENT_CONSUMED_NO_RETRY"
    }
  },
  "session_reset_clears_registry": {
    "after_session_change": {
      "blocked": false,
      "parsed": {
        "burst_event_id": "MISO|CALL|NIFTY2650524050CE|1714200000000|1714200001500",
        "burst_extreme_ts_epoch_ms": 1714200001500,
        "burst_start_ts_epoch_ms": 1714200000000,
        "family": "MISO",
        "side": "CALL",
        "symbol": "NIFTY2650524050CE",
        "symbol_side_key": "CALL|NIFTY2650524050CE",
        "valid": true
      },
      "reason": ""
    },
    "before_session_change": {
      "blocked": true,
      "existing": {
        "burst_event_id": "MISO|CALL|NIFTY2650524050CE|1714200000000|1714200001500",
        "burst_extreme_ts_epoch_ms": 1714200001500,
        "burst_start_ts_epoch_ms": 1714200000000,
        "consume_reason": "entry_order_sent",
        "side": "CALL",
        "symbol": "NIFTY2650524050CE",
        "symbol_side_key": "CALL|NIFTY2650524050CE"
      },
      "parsed": {
        "burst_event_id": "MISO|CALL|NIFTY2650524050CE|1714200000000|1714200001500",
        "burst_extreme_ts_epoch_ms": 1714200001500,
        "burst_start_ts_epoch_ms": 1714200000000,
        "family": "MISO",
        "side": "CALL",
        "symbol": "NIFTY2650524050CE",
        "symbol_side_key": "CALL|NIFTY2650524050CE",
        "valid": true
      },
      "reason": "MISO_BURST_EVENT_CONSUMED_NO_RETRY"
    },
    "pass": true
  },
  "wrapped_function_blocks_without_dhan_context": {
    "pass": true,
    "result": {
      "action": "HOLD",
      "action_before_miso_burst_consumed_block": "ENTER_CALL",
      "blocker_reasons": [
        "MISO_DHAN_CONTEXT_REQUIRED"
      ],
      "blockers": [
        "MISO_DHAN_CONTEXT_REQUIRED"
      ],
      "burst_extreme_ts_epoch_ms": 1714200001500,
      "burst_start_ts_epoch_ms": 1714200000000,
      "candidate": false,
      "eligible": false,
      "entry_allowed": false,
      "miso_burst_event_consumed_blocked": false,
      "miso_burst_event_consumption_registry_detail": "{'reason': 'Dhan selected-option/context lane not proven healthy/current'}",
      "miso_burst_event_consumption_registry_reason": "MISO_DHAN_CONTEXT_REQUIRED",
      "miso_dhan_context_required_blocked": true,
      "option_context_status": "HEALTHY",
      "reason": "MISO_DHAN_CONTEXT_REQUIRED",
      "reason_code": "MISO_DHAN_CONTEXT_REQUIRED",
      "selected_option_provider": "ZERODHA",
      "selected_option_symbol": "NIFTY2650524050CE",
      "side": "CALL"
    }
  },
  "wrapped_function_consumes_then_blocks_same_burst": {
    "first_wrapped": {
      "action": "ENTER_CALL",
      "burst_detected": true,
      "burst_event_id": "MISO|CALL|NIFTY2650524050CE|1714200000000|1714200001500",
      "burst_extreme_ts_epoch_ms": 1714200001500,
      "burst_start_ts_epoch_ms": 1714200000000,
      "dhan_context_ready": true,
      "entry_allowed": true,
      "option_context_status": "HEALTHY",
      "selected_option_provider": "DHAN",
      "selected_option_symbol": "NIFTY2650524050CE",
      "side": "CALL"
    },
    "pass": true,
    "second_wrapped": {
      "action": "HOLD",
      "action_before_miso_burst_consumed_block": "ENTER_CALL",
      "blocker_reasons": [
        "MISO_BURST_EVENT_CONSUMED_NO_RETRY"
      ],
      "blockers": [
        "MISO_BURST_EVENT_CONSUMED_NO_RETRY"
      ],
      "burst_detected": true,
      "burst_event_id": "MISO|CALL|NIFTY2650524050CE|1714200000000|1714200001500",
      "burst_extreme_ts_epoch_ms": 1714200001500,
      "burst_start_ts_epoch_ms": 1714200000000,
      "dhan_context_ready": true,
      "entry_allowed": false,
      "miso_burst_event_consumed_blocked": true,
      "miso_burst_event_consumption_registry_detail": "{'blocked': True, 'reason': 'MISO_BURST_EVENT_CONSUMED_NO_RETRY', 'parsed': {'valid': True, 'burst_event_id': 'MISO|CALL|NIFTY2650524050CE|1714200000000|1714200001500', 'family': 'MISO', 'side': 'CALL', 'symbol': 'NIFTY2650524050CE', 'symbol_side_key': 'CALL|NIFTY2650524050CE', 'burst_start_ts_epoch_ms': 1714200000000, 'burst_extreme_ts_epoch_ms': 1714200001500}, 'existing': {'burst_event_id': 'MISO|CALL|NIFTY2650524050CE|1714200000000|1714200001500', 'side': 'CALL', 'symbol': 'NIFTY2650524050CE', 'symbol_side_key': 'CALL|NIFTY2650524050CE', 'burst_start_ts_epoch_ms': 1714200000000, 'burst_extreme_ts_epoch_ms': 1714200001500, 'consume_reason': 'entry_like_decision_emitted'}}",
      "miso_burst_event_consumption_registry_reason": "MISO_BURST_EVENT_CONSUMED_NO_RETRY",
      "miso_dhan_context_required_blocked": false,
      "option_context_status": "HEALTHY",
      "reason": "MISO_BURST_EVENT_CONSUMED_NO_RETRY",
      "reason_code": "MISO_BURST_EVENT_CONSUMED_NO_RETRY",
      "selected_option_provider": "DHAN",
      "selected_option_symbol": "NIFTY2650524050CE",
      "side": "CALL"
    }
  }
}
```

## Artifacts

- `run/proofs/proof_miso_burst_event_consumption_registry.json`
- `run/proofs/proof_miso_burst_event_consumption_registry_patch_step.json`
- backup: `run/_code_backups/batch26f_miso_burst_event_registry_20260429_223056`

## Continuation

Next recommended batch: `26G — legacy quarantine import graph proof` or `26H — alias / override inventory`, depending on your chosen order.

Do not enable paper_armed. Do not enable real live. Do not start controlled paper runtime chain from this batch.
