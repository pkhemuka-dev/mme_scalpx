# B3-R31C_ARTIFACTS_PY_EXACT_SOURCE_CONTEXT_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER next route

If classification is PASS:

Run B3-R32 one-file patch in:

`app/mme_scalpx/replay/artifacts.py`

Rules:

1. Add helpers inside the writer owner class if class ownership is confirmed.
2. Use existing `write_csv_artifact` and `write_json_artifact`.
3. Add analysis exports only:
   - blocker_distribution.csv
   - economics_summary.json
   - family_side_summary.csv
   - optionally enrich candidate_audit.csv if safe
4. No strategy/risk/execution/provider changes.
5. No replay in patch batch.
