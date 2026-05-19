# A6-FEED-R5AL_narrow_stage_flags_contract_alignment_patch_remove_extra_tradability_flag_no_restart_no_order_no_paper_20260515_150353 Patch Runbook

Batch: A6-FEED-R5AL

Verdict: FAIL_A6_FEED_R5AL_STAGE_FLAGS_PATCH_OR_SAFETY_CHECK

Patch summary:
- Patched only `app/mme_scalpx/services/features.py`.
- Removed only the extra `tradability_ok` entry from stage_flags dict(s) that already contained the canonical four keys.
- Did not change feature-family validator, strategy, risk, execution, paper/live, broker/order, thresholds, or doctrine.

Removals:

```json
[]
```

Diff:

```diff

```

Backup files:

```json
[
  {
    "backup": "/home/Lenovo/scalpx/projects/mme_scalpx/run/_code_backups/A6-FEED-R5AL_narrow_stage_flags_contract_alignment_patch_remove_extra_tradability_flag_no_restart_no_order_no_paper_20260515_150353/app/mme_scalpx/services/features.py",
    "backup_sha256": "3d8345a47eacef3baf448627710d9f0669235a5df64f9f9042dc2cdbed526117",
    "source": "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/features.py",
    "source_sha256": "3d8345a47eacef3baf448627710d9f0669235a5df64f9f9042dc2cdbed526117"
  }
]
```

Next rule:
- Next batch must be static proof/import validation only.
- No service restart until separate explicit approval.
