# B3-R31B_ARTIFACTS_PY_FUNCTION_SIGNATURE_CALLGRAPH_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER next route

If classification is PASS:

Run B3-R32 one-file patch:

`app/mme_scalpx/replay/artifacts.py`

Patch laws:

1. Use existing writer helpers where possible.
2. Preserve existing `write_trade_log_csv` and `write_candidate_audit_csv` behavior unless the callgraph proves extension is safe.
3. Add new B3_R32 helpers for:
   - blocker_distribution.csv
   - economics_summary.json
   - family_side_summary.csv
   - candidate_audit export enrichment only if safe
4. No strategy/risk/execution/provider changes.
5. No replay in patch batch.
6. Compile + AST + marker proof only.
