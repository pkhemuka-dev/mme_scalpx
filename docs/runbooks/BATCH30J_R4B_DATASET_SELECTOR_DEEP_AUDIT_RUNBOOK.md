# Batch 30J-R4B Runbook

Deep-audits the selected replay dataset inventory and replay selector/date-loading source after 30J-R4A found zero actual available dates.

This batch does not execute replay and does not patch production source. It classifies whether the dataset lacks selector-compatible available-date metadata/indexing.

If GREEN_CONTINUE, run 30J-R4C to build a selector-compatible dataset available_dates metadata/index repair contract. If FAIL, resolve blockers before touching metadata.
