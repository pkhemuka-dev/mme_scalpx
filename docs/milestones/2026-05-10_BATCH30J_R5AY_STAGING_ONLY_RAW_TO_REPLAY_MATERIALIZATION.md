# Batch 30J-R5AY — Staging-Only Raw-to-Replay Materialization

Verdict: `PASS_STAGING_ONLY_RAW_MATERIALIZATION_READY_FOR_REPOSITORY_ABI_PROBE`
Classification: `STAGING_ONLY_20260418_DISCOVERABLE_NO_FINAL_REPO_MUTATION`

Raw date:
`2026-04-18`

Staging day:
`run/replay/staging/r5ay_raw_to_replay/2026-04-18`

Final repository day forbidden:
`run/replay/2026-04-18`

Final repo untouched:
`True`

Staging discoverable:
`True`

Row counts:
{
  "all_rows": 15,
  "fut_rows": 0,
  "opt_rows": 15,
  "rejected_rows": 0
}

Staging files:
{
  "materialization_manifest.json": {
    "relative_path": "run/replay/staging/r5ay_raw_to_replay/2026-04-18/materialization_manifest.json",
    "size_bytes": 3836,
    "sha256": "06a034664e9bc945d701fb47e0778f0a1226a8a9d4b8e6ec20cfdec93f37c4c5",
    "line_count": null
  },
  "opt_ticks.jsonl": {
    "relative_path": "run/replay/staging/r5ay_raw_to_replay/2026-04-18/opt_ticks.jsonl",
    "size_bytes": 28751,
    "sha256": "154bd09228557c33afee10ecf801fb381dddc7ac8823a00ebdd35fb74748ed99",
    "line_count": 15
  }
}

No replay execution.
No final repository mutation.
No Redis deletion.
No Redis restart.
No broker/order path.
No risk/execution start.

Next:
Run R5AZ staging repository ABI/detail probe and no-execution replay command planning; no final run/replay mutation.
