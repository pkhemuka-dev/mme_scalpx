# B1-R9 Real Capture Bundle Readiness Runbook

Safety: runbook/readiness only. No live run, no replay, no service start, no Redis write/delete, no broker call, no order, no paper/live, no PnL.

## Future capture purpose

Produce a recorded observe-only lifecycle bundle for all five strategies: MIST, MISB, MISC, MISR, MISO.

## Required future bundle files

- `capture_manifest.json`
- `features_rows.jsonl`
- `decision_rows.jsonl`
- `risk_lifecycle_rows.jsonl`
- `execution_shadow_rows.jsonl`
- `position_safety_snapshot.json`
- `order_safety_snapshot.json`
- `identity_continuity_report.json`
- `lifecycle_presence_report.json`
- `backtest_admission_precheck.json`
- `safety_no_order_no_broker_report.json`

## Hard stop conditions

- any broker/order/live flag present
- orders stream grows due to real order
- position not flat
- missing risk lifecycle rows
- missing execution-shadow rows
- missing consumed_risk_evidence
- identity continuity failure
- validator output says lane_e_handoff_allowed=false

## Future validator command

```bash
.venv/bin/python bin/b1_capture_bundle_validator.py --bundle <capture_bundle_dir> --out <validator_out_dir> --dry-only
```

## Rule

B1 validator may only allow `ADMITTED_FOR_LANE_E_REVIEW`. It must not mark PnL ready or run backtest.

Readiness artifact: `run/audits/B1-R9_REAL_CAPTURE_BUNDLE_READINESS_RUNBOOK_NO_LIVE_RUN_NO_REPLAY_20260512_003959.readiness.json`
