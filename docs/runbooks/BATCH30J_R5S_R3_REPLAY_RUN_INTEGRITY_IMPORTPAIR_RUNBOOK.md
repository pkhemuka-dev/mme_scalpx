# Batch 30J-R5S-R3 Runbook

Purpose:
Repair missing replay integrity import pair used by real integrity check producer.

Proof:
`run/proofs/proof_batch30j_r5s_r3_replay_run_integrity_importpair_latest.json`

Backup dir:
`run/_code_backups/batch30j_r5s_r3_replay_run_integrity_importpair_20260508_152038`

Diff:
`run/audits/batch30j_r5s_r3_replay_run_integrity_importpair_20260508_152038/replay_run_importpair.diff`

Next:
Rerun guarded offline replay after importpair repair, then reclassify integrity/output artifacts.
