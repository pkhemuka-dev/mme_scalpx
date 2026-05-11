# Evidence-Based Development Gate

Every future batch must include:
1. Files inspected
2. Files patched
3. Backup path
4. Proofs run
5. Proof output paths
6. Pass/fail verdict
7. Known gaps
8. Next safe step

RAW / research_capture gate:
- config parse proof
- manifest proof
- archive writer proof
- runtime bridge proof
- no-live-side-effect proof
- replay boundary proof

Replay gate:
- dataset selector proof
- clock/reset proof
- injector proof
- topology proof
- experiment profile proof
- artifact/report proof
- no-live-namespace-contamination proof

OpenAI / AI / ML gate:
- config parse proof
- prompt/template inventory
- model/feature interface inventory
- no-live-side-effect proof
- no broker/execution dependency proof
- no secret material proof
