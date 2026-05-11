# Repo Hygiene R8 — First Proof-Only Bin Migration With Wrappers

Date: 2026-05-11T23:24:21.183786

Verdict: PASS_FIRST_PROOF_ONLY_BIN_MIGRATION_WITH_WRAPPERS

Artifacts:
- run/proofs/repo_hygiene_r8_first_proof_only_migration_20260511_232420.json
- run/_code_backups/repo_hygiene_r8_first_proof_only_migration_20260511_232420

Safety:
- No scripts executed.
- No services started.
- No broker calls.
- No live Redis writes.
- No paper enablement.
- No real live enablement.
- No files deleted.
- Runtime source unchanged.

Actions:
- Moved first proof-only script batch from bin/ to bin/proofs/.
- Created compatibility wrappers at old bin/*.py paths.
- Compiled moved implementations and wrappers.
- Preserved backups under run/_code_backups/repo_hygiene_r8_first_proof_only_migration_20260511_232420.

Summary:
- first_batch_size: 12
- failed_actions: 0
- compile_failed: 0
- all_expected_targets_exist: True
- all_expected_wrappers_exist: True

Next:
- Review proof JSON and git diff.
- Continue only with proof-only scripts if PASS.
- Do not move runtime/controlled-paper/provider/token/broker/order scripts yet.
