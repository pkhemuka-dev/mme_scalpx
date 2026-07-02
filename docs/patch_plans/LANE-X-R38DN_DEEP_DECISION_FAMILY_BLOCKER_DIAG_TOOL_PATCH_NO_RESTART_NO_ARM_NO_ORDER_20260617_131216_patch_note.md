# R38DN Patch Note

Tag: LANE-X-R38DN_DEEP_DECISION_FAMILY_BLOCKER_DIAG_TOOL_PATCH_NO_RESTART_NO_ARM_NO_ORDER_20260617_131216
Created: 2026-06-17T13:12:17+05:30

Patched/added:
- bin/r38dn_deep_decision_family_blocker_diag.py

Patch type:
- Read-only diagnostic tool.
- No strategy threshold change.
- No candidate forcing.
- No promotion change.
- No risk/execution/order path touched.
- No restart performed.

Purpose:
- Explain why decisions are HOLD/no_candidate/side=FLAT.
- Inspect nested consumer_view_json, diagnostics_json, activation_report_json.
- Surface family and branch blocker state for MIST/MISB/MISC/MISR/MISO/MISLS/MIV-R.

Safety:
- before streams: 0/0/0/0
- after streams: 0/0/0/0
- compile_rc: 0
