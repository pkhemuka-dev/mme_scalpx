# Batch 30J-R4D Runbook

Scans dataset CSV/JSON/text files for ISO dates, compact dates, Redis stream IDs, and epoch timestamps to decide whether selector available_dates can be built from real content.

This batch does not install metadata, does not execute replay, does not patch production source, and does not create tar bundles.

If candidate dates are found with MEDIUM/HIGH confidence, proceed to selector metadata validation. If no dates are found, freeze this selected dataset as a non-executable artifact library and build a replay dataset rebuild plan.
