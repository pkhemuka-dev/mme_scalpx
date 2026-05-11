# MME-ScalpX Repo Hygiene Policy

## Principle

No destructive cleanup is allowed without prior inventory proof.

## bin/ Policy

bin/ may temporarily contain proof, patch, replay, observe_only, controlled_paper, research_gate, diagnostic, and runtime scripts.

Future target structure:
- bin/runtime/
- bin/proofs/
- bin/patches/
- bin/replay/
- bin/research_gate/
- bin/observe_only/
- bin/controlled_paper/
- bin/diagnostics/

Migration rule:
1. Classify.
2. Prove imports/path calls do not break.
3. Move in small batches.
4. Keep compatibility wrappers where needed.

## ai_patch_runner/ Policy

Keep source/policy:
- ai_patch_runner/*.py
- ai_patch_runner/cli/
- ai_patch_runner/context/
- ai_patch_runner/policy/

Generated artifacts should be ignored or moved to run/ or var/:
- ai_patch_runner/outputs/
- ai_patch_runner/prompts/
- ai_patch_runner/reports/
- ai_patch_runner/sandbox/
- ai_patch_runner/state/
- ai_patch_runner/review_bundles/

## Root Junk Policy

Suspicious root files must be audited before deletion.

Known suspicious examples:
- =
- metrics_dict[baseline_put_candidate_count]

Cleanup sequence:
audit -> quarantine -> milestone -> later delete only if safe

## Legacy Module Policy

Known legacy files:
- app/mme_scalpx/services/features_legacy_single.py
- app/mme_scalpx/services/strategy_legacy_single.py

They may remain as quarantined historical references.

Runtime import count must remain zero unless explicit rollback contract exists.

## Safety

Repo hygiene must never:
- start services
- call brokers
- write live Redis trading streams
- enable paper
- enable real live
- modify runtime behavior without proof
