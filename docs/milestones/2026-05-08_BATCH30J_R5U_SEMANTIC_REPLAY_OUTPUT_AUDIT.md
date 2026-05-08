# Batch 30J-R5U — Semantic Replay Output Audit

Verdict: `REVIEW_SEMANTIC_AUDIT_ORDER_LIKE_TOKENS_FOUND`
Classification: `ORDER_LIKE_REPLAY_OUTPUT_REQUIRES_REVIEW`

Inner run:
`/home/Lenovo/scalpx/projects/mme_scalpx/run/replay/guarded_offline/batch30j_r5t_20260417_20260508_152130/replay_locked_single_day_20260508_095131_8fb68cf5`

Record counts:
{
  "features_rows": 4,
  "strategy_decisions": 4,
  "risk_outputs": 4,
  "execution_shadow_results": 4
}

No replay execution.
No patch.
No Redis deletion.
No Redis restart.
No broker/order path.
No risk/execution start.

Next:
Inspect order_like_hits before parity or paper readiness.
