# Batch 30J-DISK-B Runbook

Use after 30J-DISK-A shows disk still full and generated evidence bundles are large.

This package deletes only `run/evidence_bundles/*.tar.gz`. The proof JSONs, milestone notes, runbooks, replay datasets, and source files are preserved.

If GREEN, retry 30J-R3A. If FAIL, run 30J-DISK-C to prune old oversized generated proof files while preserving the latest proof chain.
