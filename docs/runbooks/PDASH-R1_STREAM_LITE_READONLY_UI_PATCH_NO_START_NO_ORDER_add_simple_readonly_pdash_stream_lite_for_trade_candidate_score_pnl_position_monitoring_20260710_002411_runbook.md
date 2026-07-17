# PDASH-R1_STREAM_LITE_READONLY_UI_PATCH_NO_START_NO_ORDER_add_simple_readonly_pdash_stream_lite_for_trade_candidate_score_pnl_position_monitoring_20260710_002411 runbook

Manual run only:

```bash
cd /home/Lenovo/scalpx/projects/mme_scalpx
export PYTHONPATH="$PWD:${PYTHONPATH:-}"
bin/pdash_lite --host 127.0.0.1 --port 8787
```

Do not start risk/execution/order services from PDASH.
PDASH is monitoring-only.
