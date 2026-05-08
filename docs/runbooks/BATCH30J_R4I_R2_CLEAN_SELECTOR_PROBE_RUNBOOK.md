# Batch 30J-R4I-R2 Runbook

Reruns source-specific selector API probing under clean offline isolation.

This batch directly exercises replay selector date-validation and date-resolution API surfaces using candidate available_dates, but does not install metadata into the dataset root and does not execute replay_run.py.

If GREEN/REVIEW with selector API accepted, proceed only to reversible metadata install planning and dry CLI selector validation. Replay execution remains blocked.
