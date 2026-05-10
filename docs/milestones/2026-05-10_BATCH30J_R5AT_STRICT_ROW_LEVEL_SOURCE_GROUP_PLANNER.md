# Batch 30J-R5AT — Strict Row-Level Source-Group Planner

Verdict: `REVIEW_NO_STRICT_ROW_LEVEL_SOURCE_GROUP_FOUND`
Classification: `R5AS_CANDIDATES_DOMINATED_BY_WEAK_DATE_OR_PROOF_PNL_ARTIFACTS`

Repository dates:
[
  "2026-04-17"
]

Files loaded from R5AS:
`24601`

Strict accepted file count:
`0`

Strict rejected file count:
`24601`

Group count:
`0`

Strong group count:
`0`

Complete group count:
`0`

Rejection summary:
{
  "NO_STRICT_ROW_LEVEL_NON_REPO_DATE": 24601,
  "HARD_NOISE_MARKER:/run/proofs/": 23283,
  "SURFACE_UNKNOWN_AFTER_STRICT_INFERENCE": 7106,
  "HARD_NOISE_MARKER:_audit": 1100,
  "HARD_NOISE_MARKER:proof_": 96,
  "HARD_NOISE_MARKER:/etc/replay/parity/": 80,
  "HARD_NOISE_MARKER:_contract": 24
}

No replay execution.
No repository mutation.
No staging materialization.
No patch.
No Redis deletion.
No Redis restart.
No broker/order path.
No risk/execution start.

Next:
Do not materialize. Upload/locate raw captured source files with explicit source_date/trading_date or epoch event timestamps.
