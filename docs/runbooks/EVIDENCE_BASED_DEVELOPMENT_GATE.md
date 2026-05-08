# Evidence-Based Development Gate

Every batch must include:
1. Files inspected
2. Files patched
3. Backup path
4. Proofs run
5. Proof output paths
6. Pass/fail verdict
7. Known gaps
8. Next safe step

RAW minimum proofs:
- config parse
- manifest
- archive writer
- runtime bridge
- no-live-side-effect
- replay boundary

Replay minimum proofs:
- dataset selector
- clock/reset
- injector
- topology
- experiment profile
- artifact/report
- no-live-namespace-contamination
