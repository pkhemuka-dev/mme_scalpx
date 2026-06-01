# B3-R30_REPLAY_EXPORT_WRITER_SOURCE_OWNERSHIP_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER

Classification: `PASS_R30_REPLAY_EXPORT_WRITER_OWNER_IDENTIFIED_NO_PATCH`  
Created: `2026-05-31T19:33:40.968775+05:30`

## Planned exports

- candidate_audit.csv
- blocker_distribution.csv
- economics_summary.json
- family_side_summary.csv

## Top owner candidate

`app/mme_scalpx/replay/artifacts.py`

## Ranked candidates

`[{'path': 'app/mme_scalpx/replay/artifacts.py', 'score': 19, 'reasons': ['contains file writing/export code', 'materializer ownership signal', 'already has audit/trade export naming surface']}, {'path': 'bin/replay_run.py', 'score': 18, 'reasons': ['writes or references current replay row artifacts', 'contains file writing/export code', 'materializer ownership signal']}, {'path': 'app/mme_scalpx/replay/report_exporter.py', 'score': 14, 'reasons': ['contains file writing/export code', 'materializer ownership signal', 'already has audit/trade export naming surface']}, {'path': 'app/mme_scalpx/replay/artifact_materializer.py', 'score': 10, 'reasons': ['contains file writing/export code', 'materializer ownership signal']}, {'path': 'app/mme_scalpx/replay/runner.py', 'score': 6, 'reasons': ['materializer ownership signal', 'already has audit/trade export naming surface']}, {'path': 'app/mme_scalpx/replay/execution_shadow.py', 'score': 3, 'reasons': ['already has audit/trade export naming surface']}]`

## Safety

Source ownership audit only. No Redis. No replay. No patch. No service action. No broker/order/paper/live/risk/execution.

## Artifacts

- Proof: `run/proofs/B3-R30_REPLAY_EXPORT_WRITER_SOURCE_OWNERSHIP_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_identify_exact_replay_artifact_writer_owner_for_candidate_blocker_economics_family_side_exports_20260531_193340.json`
- Latest proof: `run/proofs/B3_R30_latest.json`
- Audit: `run/audits/B3-R30_REPLAY_EXPORT_WRITER_SOURCE_OWNERSHIP_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_identify_exact_replay_artifact_writer_owner_for_candidate_blocker_economics_family_side_exports_20260531_193340_audit.json`
