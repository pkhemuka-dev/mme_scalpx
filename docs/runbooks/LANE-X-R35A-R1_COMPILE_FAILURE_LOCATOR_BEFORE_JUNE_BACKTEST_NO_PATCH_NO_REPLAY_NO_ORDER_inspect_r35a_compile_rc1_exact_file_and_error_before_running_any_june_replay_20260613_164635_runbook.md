# LANE-X-R35A-R1_COMPILE_FAILURE_LOCATOR_BEFORE_JUNE_BACKTEST_NO_PATCH_NO_REPLAY_NO_ORDER_inspect_r35a_compile_rc1_exact_file_and_error_before_running_any_june_replay_20260613_164635

classification: REVIEW_R35A_R1_COMPILE_FAILURE_PINNED_NO_PATCH_NO_REPLAY_NO_ORDER
proof: `run/proofs/LANE-X-R35A-R1_COMPILE_FAILURE_LOCATOR_BEFORE_JUNE_BACKTEST_NO_PATCH_NO_REPLAY_NO_ORDER_inspect_r35a_compile_rc1_exact_file_and_error_before_running_any_june_replay_20260613_164635.json`
audit: `run/audits/LANE-X-R35A-R1_COMPILE_FAILURE_LOCATOR_BEFORE_JUNE_BACKTEST_NO_PATCH_NO_REPLAY_NO_ORDER_inspect_r35a_compile_rc1_exact_file_and_error_before_running_any_june_replay_20260613_164635`

## Safety
- orders/risk/execution: 0 / 0 / 0
- risk/execution proc: 0 / 0

## Compile each
============================================================
FILE=app/mme_scalpx/services/strategy.py
RC=0
============================================================
FILE=app/mme_scalpx/services/features.py
RC=0
============================================================
FILE=app/mme_scalpx/replay/run_replay.py
[Errno 2] No such file or directory: 'app/mme_scalpx/replay/run_replay.py'RC=1

## Import probe
Traceback (most recent call last):
  File "<stdin>", line 11, in <module>
  File "/usr/lib/python3.10/importlib/__init__.py", line 126, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
  File "<frozen importlib._bootstrap>", line 1050, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1027, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1004, in _find_and_load_unlocked
ModuleNotFoundError: No module named 'app.mme_scalpx.replay.run_replay'
================================================================================
MODULE app.mme_scalpx.services.strategy
IMPORT_RC=0
================================================================================
MODULE app.mme_scalpx.services.features
IMPORT_RC=0
================================================================================
MODULE app.mme_scalpx.replay.run_replay
IMPORT_RC=1
