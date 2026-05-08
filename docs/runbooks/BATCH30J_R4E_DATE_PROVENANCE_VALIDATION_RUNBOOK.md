# Batch 30J-R4E Runbook

Validates whether timestamp-derived dates from 30J-R4D are true market/session dates or merely artifact metadata such as file mtime.

This batch does not install selector metadata, does not execute replay, does not patch production source, and does not create tar bundles.

If dates are artifact metadata only, the selected dataset is frozen as a non-executable artifact library and the next step is rebuilding/materializing a proper replay dataset from original live/research_capture artifacts.
