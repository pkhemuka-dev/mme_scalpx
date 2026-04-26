# Session Export Schema Audit — 2026-04-25

## Purpose
Inspect real recorded session export CSVs before replay integration.

## Inputs
- run/session_exports/2026-04-17/ticks_mme_fut_stream.csv
- run/session_exports/2026-04-17/ticks_mme_opt_stream.csv
- run/session_exports/2026-04-20/ticks_mme_fut_stream.csv
- run/session_exports/2026-04-20/ticks_mme_opt_stream.csv
- run/session_exports/2026-04-21/ticks_mme_fut_stream.csv
- run/session_exports/2026-04-21/ticks_mme_opt_stream.csv

## Artifacts
- run/proofs/session_export_schema_audit_20260425_150405/session_export_schema_audit.log
- run/proofs/session_export_schema_audit_20260425_150405/session_export_schema_audit_latest.json
- run/proofs/session_export_schema_audit_20260425_150405/replay_tool_help.log

## Next
Choose best candidate date and run replay compatibility / module communication audit.
