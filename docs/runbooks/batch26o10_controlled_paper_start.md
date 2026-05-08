Batch 26-O10 - Controlled Paper Start

Starts only risk and execution under controlled paper environment.

Scope:
- MIST
- CALL
- 1 lot
- paper/sandbox only
- real live blocked
- no automatic broker failover
- no mid-position provider migration

Rollback:
pkill -f 'app.mme_scalpx.main --service risk'
pkill -f 'app.mme_scalpx.main --service execution'
redis-cli XLEN orders:mme:stream
redis-cli HGETALL state:position:mme
