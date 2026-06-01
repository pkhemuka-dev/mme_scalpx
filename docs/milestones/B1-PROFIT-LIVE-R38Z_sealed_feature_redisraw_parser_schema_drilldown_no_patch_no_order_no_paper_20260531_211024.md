# B1-PROFIT-LIVE-R38Z_sealed_feature_redisraw_parser_schema_drilldown_no_patch_no_order_no_paper_20260531_211024

## Verdict
`PASS_R38Z_FEATURE_REDISRAW_SCHEMA_DRILLDOWN_NO_PATCH`

## Audit classification
`FEATURE_FAMILY_FEATURES_JSON_PRESENT_STRATEGY_MAPPING_MUST_BE_TESTED`

## Meaning
R38Z inspects the actual sealed `features.redisraw.gz` field-pair shape. No patch was applied.

## Safety
- orders: `0`
- risk_stream: `0`
- execution_stream: `0`
- lock_execution: ``

## Counts
- feature_record_count: `446`
- decision_record_count: `998`
- family_features_json_count: `446`
- payload_json_feature_count: `0`
- family_surfaces_json_count: `446`
- family_frames_json_count: `0`
- decision_payload_json_count: `998`

## Feature field counts
`{'consumer_view_json': 446, 'family_features_json': 446, 'family_features_version': 446, 'family_surfaces_json': 446, 'frame_id': 446, 'frame_ts_ns': 446, 'o23p_r6b_r3_family_payload_publish_patch': 446, 'schema_version': 446, 'service': 446}`

## Feature JSON field counts
`{'consumer_view_json': 446, 'family_features_json': 446, 'family_surfaces_json': 446}`

## Next
- If `family_features_json_count > 0`, run R38ZA strategy mapping fixture.
- If `family_features_json_count = 0`, patch `features.py` publisher/export shape.
