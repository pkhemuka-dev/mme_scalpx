# A6-FEED-R4F next runbook

## Status

`FAIL_A6_FEED_R4F_RESTORE_PRECONDITIONS_FAILED_NO_START_NO_ORDER_NO_BROKER_ORDER`

## Next

`A6-FEED-R4F-D precondition diagnostic / no start / no order / no broker order`

## Rule

If PASS, rerun guarded canonical hash publish before A6-PAPER.
If BLOCKED, run restore failure classifier.
Do not run A6-PAPER until canonical provider/feed hashes and feature/decision readiness prove PASS.
