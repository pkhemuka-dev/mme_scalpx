# PDASH-R1A_CORRECTED_READONLY_SAFETY_SEAL_NO_PATCH_NO_START_NO_ORDER_reclassify_env_read_false_positive_and_freeze_pdash_stream_lite_20260710_002659 runbook

PDASH Stream Lite is monitoring-only.

Manual start command:

```bash
cd /home/Lenovo/scalpx/projects/mme_scalpx
export PYTHONPATH="$PWD:${PYTHONPATH:-}"
bin/pdash_lite --host 127.0.0.1 --port 8787
```

Do not start risk/execution/order services from PDASH.
