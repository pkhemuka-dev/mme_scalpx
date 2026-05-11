# 30J-R5BE-R1 Runbook

Purpose: classify whether the prior R5BE runtime-dirty stop was real or caused by self-match from `pgrep`.

This batch is read-only except proof/doc artifact writes.

If verdict is PASS_RUNTIME_CLEAN_FALSE_POSITIVE_CONFIRMED_NO_PATCH, rerun R5BE with a corrected runtime classifier.

If verdict is FAIL_RUNTIME_DIRTY_ACTUAL_APP_MAIN_PRESENT_NO_PATCH, do not patch Lane C until runtime is clean.
