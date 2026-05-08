# Batch 26C — Risk-side Explicit Controlled Paper Arming Veto

Date: 2026-04-29

## Verdict

- risk_controlled_paper_veto_ok: `True`
- all_required_blockers_proven: `True`
- risk_blocks_entries: `True`
- risk_does_not_block_exits: `True`
- paper_armed_approved: `False`
- real_live_approved: `False`
- runtime_promotion_allowed: `False`

## V3 Note

Batch 26C source patch was already present. V3 repaired only the proof harness by driving the installed helper through runtime position fields instead of an unsupported override.

## Required Blocker Proofs

```json
{
  "not_armed": {
    "allow_exits": "1",
    "details": {
      "batch26c": "risk_controlled_paper_entry_veto",
      "config_present": true,
      "enabled": false,
      "env_ack": false,
      "env_enabled": false,
      "paper_armed_approved_by_patch": false,
      "qty": 1,
      "real_live_allowed": false,
      "real_live_approved_by_patch": false,
      "selected_family": "MIST",
      "selected_side": "CALL"
    },
    "expected": "CONTROLLED_PAPER_NOT_ARMED",
    "pass": true,
    "reason": "CONTROLLED_PAPER_NOT_ARMED",
    "risk_blocks_entries_only": "1",
    "snapshot": {
      "allow_exits": "1",
      "controlled_paper_entry_veto": "1",
      "controlled_paper_veto_detail": "{\"batch26c\": \"risk_controlled_paper_entry_veto\", \"config_present\": true, \"enabled\": false, \"env_ack\": false, \"env_enabled\": false, \"paper_armed_approved_by_patch\": false, \"qty\": 1, \"real_live_allowed\": false, \"real_live_approved_by_patch\": false, \"selected_family\": \"MIST\", \"selected_side\": \"CALL\"}",
      "controlled_paper_veto_reason": "CONTROLLED_PAPER_NOT_ARMED",
      "reason_code": "CONTROLLED_PAPER_NOT_ARMED",
      "reason_message": "CONTROLLED_PAPER_NOT_ARMED",
      "risk_blocks_entries_only": "1",
      "veto_entries": "1"
    },
    "veto_entries": true,
    "veto_reason": "CONTROLLED_PAPER_NOT_ARMED"
  },
  "position_not_flat": {
    "allow_exits": "1",
    "details": {
      "batch26c": "risk_controlled_paper_entry_veto",
      "config_present": true,
      "enabled": true,
      "env_ack": true,
      "env_enabled": true,
      "paper_armed_approved_by_patch": false,
      "position_flat": false,
      "qty": 1,
      "real_live_allowed": false,
      "real_live_approved_by_patch": false,
      "selected_family": "MIST",
      "selected_side": "CALL"
    },
    "expected": "CONTROLLED_PAPER_POSITION_NOT_FLAT",
    "pass": true,
    "reason": "CONTROLLED_PAPER_POSITION_NOT_FLAT",
    "risk_blocks_entries_only": "1",
    "snapshot": {
      "allow_exits": "1",
      "controlled_paper_entry_veto": "1",
      "controlled_paper_veto_detail": "{\"batch26c\": \"risk_controlled_paper_entry_veto\", \"config_present\": true, \"enabled\": true, \"env_ack\": true, \"env_enabled\": true, \"paper_armed_approved_by_patch\": false, \"position_flat\": false, \"qty\": 1, \"real_live_allowed\": false, \"real_live_approved_by_patch\": false, \"selected_family\": \"MIST\", \"selected_side\": \"CALL\"}",
      "controlled_paper_veto_reason": "CONTROLLED_PAPER_POSITION_NOT_FLAT",
      "reason_code": "CONTROLLED_PAPER_POSITION_NOT_FLAT",
      "reason_message": "CONTROLLED_PAPER_POSITION_NOT_FLAT",
      "risk_blocks_entries_only": "1",
      "veto_entries": "1"
    },
    "veto_entries": true,
    "veto_reason": "CONTROLLED_PAPER_POSITION_NOT_FLAT"
  },
  "qty_cap_fail": {
    "allow_exits": "1",
    "details": {
      "batch26c": "risk_controlled_paper_entry_veto",
      "config_present": true,
      "enabled": true,
      "env_ack": true,
      "env_enabled": true,
      "paper_armed_approved_by_patch": false,
      "qty": 2,
      "real_live_allowed": false,
      "real_live_approved_by_patch": false,
      "selected_family": "MIST",
      "selected_side": "CALL"
    },
    "expected": "CONTROLLED_PAPER_QTY_CAP_FAIL",
    "pass": true,
    "reason": "CONTROLLED_PAPER_QTY_CAP_FAIL",
    "risk_blocks_entries_only": "1",
    "snapshot": {
      "allow_exits": "1",
      "controlled_paper_entry_veto": "1",
      "controlled_paper_veto_detail": "{\"batch26c\": \"risk_controlled_paper_entry_veto\", \"config_present\": true, \"enabled\": true, \"env_ack\": true, \"env_enabled\": true, \"paper_armed_approved_by_patch\": false, \"qty\": 2, \"real_live_allowed\": false, \"real_live_approved_by_patch\": false, \"selected_family\": \"MIST\", \"selected_side\": \"CALL\"}",
      "controlled_paper_veto_reason": "CONTROLLED_PAPER_QTY_CAP_FAIL",
      "reason_code": "CONTROLLED_PAPER_QTY_CAP_FAIL",
      "reason_message": "CONTROLLED_PAPER_QTY_CAP_FAIL",
      "risk_blocks_entries_only": "1",
      "veto_entries": "1"
    },
    "veto_entries": true,
    "veto_reason": "CONTROLLED_PAPER_QTY_CAP_FAIL"
  },
  "real_live_forbidden": {
    "allow_exits": "1",
    "details": {
      "batch26c": "risk_controlled_paper_entry_veto",
      "config_present": true,
      "enabled": true,
      "env_ack": true,
      "env_enabled": true,
      "paper_armed_approved_by_patch": false,
      "qty": 1,
      "real_live_allowed": true,
      "real_live_approved_by_patch": false,
      "selected_family": "MIST",
      "selected_side": "CALL"
    },
    "expected": "CONTROLLED_PAPER_REAL_LIVE_FORBIDDEN",
    "pass": true,
    "reason": "CONTROLLED_PAPER_REAL_LIVE_FORBIDDEN",
    "risk_blocks_entries_only": "1",
    "snapshot": {
      "allow_exits": "1",
      "controlled_paper_entry_veto": "1",
      "controlled_paper_veto_detail": "{\"batch26c\": \"risk_controlled_paper_entry_veto\", \"config_present\": true, \"enabled\": true, \"env_ack\": true, \"env_enabled\": true, \"paper_armed_approved_by_patch\": false, \"qty\": 1, \"real_live_allowed\": true, \"real_live_approved_by_patch\": false, \"selected_family\": \"MIST\", \"selected_side\": \"CALL\"}",
      "controlled_paper_veto_reason": "CONTROLLED_PAPER_REAL_LIVE_FORBIDDEN",
      "reason_code": "CONTROLLED_PAPER_REAL_LIVE_FORBIDDEN",
      "reason_message": "CONTROLLED_PAPER_REAL_LIVE_FORBIDDEN",
      "risk_blocks_entries_only": "1",
      "veto_entries": "1"
    },
    "veto_entries": true,
    "veto_reason": "CONTROLLED_PAPER_REAL_LIVE_FORBIDDEN"
  },
  "scope_mismatch": {
    "allow_exits": "1",
    "details": {
      "batch26c": "risk_controlled_paper_entry_veto",
      "config_present": true,
      "enabled": true,
      "env_ack": true,
      "env_enabled": true,
      "paper_armed_approved_by_patch": false,
      "qty": 1,
      "real_live_allowed": false,
      "real_live_approved_by_patch": false,
      "selected_family": "MISB",
      "selected_side": "CALL"
    },
    "expected": "CONTROLLED_PAPER_SCOPE_MISMATCH",
    "pass": true,
    "reason": "CONTROLLED_PAPER_SCOPE_MISMATCH",
    "risk_blocks_entries_only": "1",
    "snapshot": {
      "allow_exits": "1",
      "controlled_paper_entry_veto": "1",
      "controlled_paper_veto_detail": "{\"batch26c\": \"risk_controlled_paper_entry_veto\", \"config_present\": true, \"enabled\": true, \"env_ack\": true, \"env_enabled\": true, \"paper_armed_approved_by_patch\": false, \"qty\": 1, \"real_live_allowed\": false, \"real_live_approved_by_patch\": false, \"selected_family\": \"MISB\", \"selected_side\": \"CALL\"}",
      "controlled_paper_veto_reason": "CONTROLLED_PAPER_SCOPE_MISMATCH",
      "reason_code": "CONTROLLED_PAPER_SCOPE_MISMATCH",
      "reason_message": "CONTROLLED_PAPER_SCOPE_MISMATCH",
      "risk_blocks_entries_only": "1",
      "veto_entries": "1"
    },
    "veto_entries": true,
    "veto_reason": "CONTROLLED_PAPER_SCOPE_MISMATCH"
  },
  "time_gate_fail": {
    "allow_exits": "1",
    "details": {
      "batch26c": "risk_controlled_paper_entry_veto",
      "config_present": true,
      "enabled": true,
      "env_ack": true,
      "env_enabled": true,
      "paper_armed_approved_by_patch": false,
      "position_flat": true,
      "qty": 1,
      "real_live_allowed": false,
      "real_live_approved_by_patch": false,
      "selected_family": "MIST",
      "selected_side": "CALL",
      "time_gate_ok": false
    },
    "expected": "CONTROLLED_PAPER_TIME_GATE_FAIL",
    "pass": true,
    "reason": "CONTROLLED_PAPER_TIME_GATE_FAIL",
    "risk_blocks_entries_only": "1",
    "snapshot": {
      "allow_exits": "1",
      "controlled_paper_entry_veto": "1",
      "controlled_paper_veto_detail": "{\"batch26c\": \"risk_controlled_paper_entry_veto\", \"config_present\": true, \"enabled\": true, \"env_ack\": true, \"env_enabled\": true, \"paper_armed_approved_by_patch\": false, \"position_flat\": true, \"qty\": 1, \"real_live_allowed\": false, \"real_live_approved_by_patch\": false, \"selected_family\": \"MIST\", \"selected_side\": \"CALL\", \"time_gate_ok\": false}",
      "controlled_paper_veto_reason": "CONTROLLED_PAPER_TIME_GATE_FAIL",
      "reason_code": "CONTROLLED_PAPER_TIME_GATE_FAIL",
      "reason_message": "CONTROLLED_PAPER_TIME_GATE_FAIL",
      "risk_blocks_entries_only": "1",
      "veto_entries": "1"
    },
    "veto_entries": true,
    "veto_reason": "CONTROLLED_PAPER_TIME_GATE_FAIL"
  },
  "valid_controlled_paper_no_veto": {
    "allow_exits": "1",
    "details": {
      "batch26c": "risk_controlled_paper_entry_veto",
      "config_present": true,
      "enabled": true,
      "env_ack": true,
      "env_enabled": true,
      "paper_armed_approved_by_patch": false,
      "position_flat": true,
      "qty": 1,
      "real_live_allowed": false,
      "real_live_approved_by_patch": false,
      "selected_family": "MIST",
      "selected_side": "CALL",
      "time_gate_ok": true
    },
    "expected": null,
    "pass": true,
    "reason": null,
    "risk_blocks_entries_only": "1",
    "snapshot": {
      "allow_exits": "1",
      "controlled_paper_entry_veto": "0",
      "controlled_paper_veto_detail": "{\"batch26c\": \"risk_controlled_paper_entry_veto\", \"config_present\": true, \"enabled\": true, \"env_ack\": true, \"env_enabled\": true, \"paper_armed_approved_by_patch\": false, \"position_flat\": true, \"qty\": 1, \"real_live_allowed\": false, \"real_live_approved_by_patch\": false, \"selected_family\": \"MIST\", \"selected_side\": \"CALL\", \"time_gate_ok\": true}",
      "controlled_paper_veto_reason": "",
      "reason_code": "",
      "reason_message": "",
      "risk_blocks_entries_only": "1",
      "veto_entries": "0"
    },
    "veto_entries": false,
    "veto_reason": ""
  }
}
```

## Artifacts

- `run/proofs/proof_risk_controlled_paper_veto.json`
- backup: `$BACKUP_DIR`

## Continuation

Next recommended batch: `26D — Five-family mandatory fail-closed stage repair`.

Do not enable paper_armed. Do not enable real live. Do not start controlled paper runtime chain from this batch.
