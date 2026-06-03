# A7-CAPTURE-R39D-LITE_15MIN_GENERIC_MAIN_CAPTURE_CHECK_NO_PATCH_NO_START_NO_STOP_NO_ORDER_NO_PAPER_verify_stream_id_growth_generic_main_runtime_owner_no_new_errors_safety_20260602_100230

classification: `PASS_A7_CAPTURE_R39D_LITE_15MIN_GENERIC_MAIN_CAPTURE_CONTINUITY_SAFE_NO_NEW_ERRORS_NO_ORDER_NO_PAPER`

## 15-minute growth

- futures Zerodha: `345 -> 401` growth `56`
- selected option Zerodha: `4445 -> 4755` growth `310`
- features: `368 -> 387` growth `19`
- decisions: `1233 -> 1422` growth `189`
- errors: `2 -> 2` growth `0`

## Safety

- orders: `0 -> 0`
- risk stream: `0 -> 0`
- execution stream: `0 -> 0`

## Generic main / runtime ownership

Before:

```text
   4124    3954     114 Rs   /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service features --skip-group-bootstrap
   4125    3954     114 Rs   /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service strategy --skip-group-bootstrap
   4688    3954      82 Ssl  /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service feeds --bootstrap-provider app.mme_scalpx.integrations.bootstrap_provider:provide --skip-group-bootstrap
```

After:

```text
   4124    3954     167 Ss   /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service features --skip-group-bootstrap
   4125    3954     167 Ss   /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service strategy --skip-group-bootstrap
   4688    3954     135 Ssl  /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service feeds --bootstrap-provider app.mme_scalpx.integrations.bootstrap_provider:provide --skip-group-bootstrap
```

Locks before:

```text
lock:feeds=feeds:mme-scalpx:4688
lock:execution=
lock:monitor=
```

Locks after:

```text
lock:feeds=feeds:mme-scalpx:4688
lock:execution=
lock:monitor=
```

## New errors after baseline

Saved at:

`run/audits/A7-CAPTURE-R39D-LITE_15MIN_GENERIC_MAIN_CAPTURE_CHECK_NO_PATCH_NO_START_NO_STOP_NO_ORDER_NO_PAPER_verify_stream_id_growth_generic_main_runtime_owner_no_new_errors_safety_20260602_100230_new_errors_after_baseline.txt`

bytes: `60`

## Interpretation

Generic-main runtime ownership is accepted for this checkpoint. Do not classify capture as down merely because service-specific `--service` process names are absent. Paper remains blocked.
