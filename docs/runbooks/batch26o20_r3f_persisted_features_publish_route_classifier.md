# 26-O20-R3F — persisted features publish-route audit / repair classifier

- generated_at_utc: 2026-05-06T06:38:17.747955+00:00
- tag: `batch26o20_r3f_persisted_features_publish_route_classifier_20260506_120806`
- proof: `run/proofs/proof_batch26o20_r3f_persisted_features_publish_route_classifier.json`
- manifest: `run/proofs/manifest_batch26o20_r3f_persisted_features_publish_route_classifier.json`
- backup_dir: `run/_code_backups/batch26o20_r3f_persisted_features_publish_route_classifier_20260506_120806`

## Evidence-first rule
- Latest uploaded evidence must be inspected before patch work.
- This script also inspects local evidence/proof artifacts available under the project tree.

## Safety
- No real-live enablement.
- No paper restart.
- No broker call.
- No order write.
- No threshold relaxation.
- No forced candidate.
- No doctrine mutation.
- No risk/execution start.
- No production source mutation in this classifier batch.

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

## Verdict
- final_verdict: `PASS_O20_R3F_CLASSIFIED_PROOF_PARSER_GAP_HOLD_ONLY`
- false_keys: `[]`
- next_recommended_batch: `26-O20-R3G corrected R3E proof parser only; no production source patch.`
