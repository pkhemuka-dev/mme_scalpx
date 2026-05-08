# 2026-05-06 — 26-O20-R3F persisted features publish-route classifier

Verdict: `PASS_O20_R3F_CLASSIFIED_PROOF_PARSER_GAP_HOLD_ONLY`

## Why this batch exists
- O20-R3E failed because persisted `features:mme:stream` samples did not carry valid consumer-view / structural-valid / 10 branch-frame shape.
- R3E safety stayed clean: HOLD decisions, zero orders, FLAT position.

## What this batch checked
- Loaded prior R3E proof false keys.
- Inspected local evidence archives/proofs first.
- Backed up source and proof files.
- Captured latest Redis feature/decision/position/order shapes.
- Inspected `features.py` publish/run_once surfaces.
- Ran non-service run_once introspection without broker/paper/live enablement.
- Classified blocker as parser gap, persisted publish-route gap, stale/mixed stream, or Lane-B feed/provider dependency.

## Classification
```json
{
  "lane_b_dependency_possible": true,
  "latest_branch_ok": true,
  "latest_consumer_safe": false,
  "latest_consumer_structural": false,
  "latest_consumer_valid": false,
  "latest_feature_branch_frames_source": "consumer_view_json",
  "latest_feature_id": "1778045972081-0",
  "latest_feature_raw_field_keys": [
    "consumer_view_json",
    "family_features_json",
    "family_features_version",
    "family_surfaces_json",
    "frame_id",
    "frame_ts_ns",
    "schema_version",
    "service"
  ],
  "latest_mist_call": true,
  "persisted_publish_route_gap_possible": false,
  "proof_parser_gap_possible": true,
  "r3e_false_keys": [
    "all_10_branch_frames_in_samples",
    "consumer_view_data_valid_in_samples",
    "consumer_view_safe_to_consume_in_samples",
    "consumer_view_structural_valid_in_samples",
    "mist_call_visible_in_samples",
    "payload_structural_valid_in_samples",
    "top_structural_valid_in_samples"
  ],
  "r3e_final_verdict": "FAIL_O20_R3E_CORRECTED_BOUNDED_OBSERVATION_NOT_PROVEN",
  "recommended_lane": "LANE_A",
  "run_once_any_valid": false,
  "run_once_ok": false,
  "stale_or_mixed_stream_possible": false
}
```

## Next
- 26-O20-R3G corrected R3E proof parser only; no production source patch.