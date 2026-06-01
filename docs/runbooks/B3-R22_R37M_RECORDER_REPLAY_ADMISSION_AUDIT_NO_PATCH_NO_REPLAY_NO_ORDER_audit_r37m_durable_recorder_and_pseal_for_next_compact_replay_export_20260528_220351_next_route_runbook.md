# B3-R22_R37M_RECORDER_REPLAY_ADMISSION_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER next route

If classification is PASS:

B3-R23 should build a compact replay dataset from:

- fut_zerodha.jsonl.gz
- opt_selected_zerodha.jsonl.gz
- features.jsonl.gz
- decisions.jsonl.gz

Target: a bounded replayable sample first, then full-day export.

Do not patch provider_runtime in B3. Provider fallback remains separate live/paper/provider-lane work.
