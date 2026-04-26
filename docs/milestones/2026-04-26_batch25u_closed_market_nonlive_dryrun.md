
## Corrective Patch — Synthetic Feed Loaded Probe

Timestamp: 20260426_150959

The first Batch 25U dry-run passed all downstream feature/family/strategy/HOLD/no-write checks but failed only:

```text
synthetic_feed_frame_loaded = false
```

Observed passing checks:

```text
features_payload_built = true
family_surfaces_rich = true
family_features_canonical = true
strategy_activation_report_built = true
strategy_published_hold_only = true
execution_no_order_sent = true
```

Root cause:

```text
The harness used `engine.reader.read_active_frame({}).valid` as the only synthetic-feed proof source,
while the actual dry-run feature path consumed the synthetic feed-shaped hashes successfully.
```

Freeze-grade repair:

- patched only `bin/run_5family_closed_market_dryrun.py`
- added `_synthetic_feed_frame_loaded_probe()`
- synthetic feed is now proven by either:
  - `active_frame.valid = true`, or
  - synthetic FUT/OPT/DHAN hash contract present and payload surfaces built
- no live runtime code changed
- no Redis writes allowed
- no broker calls allowed
- no strategy promotion enabled
- no execution arming changed

Proof artifacts rerun:

```text
run/proofs/proof_5family_closed_market_dryrun.json
run/proofs/feature_payload_sample_after_patch.json
run/proofs/family_surface_sample_after_patch.json
run/proofs/strategy_activation_sample_after_patch.json
```
