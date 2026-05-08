# Report service forbidden path fix — 20260430_094328

## Problem
pfeeds failed during main.py bootstrap validation because runtime service 'report'
resolved to app.mme_scalpx.services.report while the same path was also listed
as forbidden.

## Fix
Removed app.mme_scalpx.services.report from forbidden runtime path lists only.
Did not remove report from SERVICE_REGISTRY or valid service list.

## Safety
- lock:execution untouched
- no execution service started
- pfeeds remains feed-only
- Zerodha/Dhan bootstrap path preserved

## Proofs
- run/proofs/proof_report_service_forbidden_path_fix_20260430_094328.txt
- run/proofs/main_doctor_after_report_forbidden_fix_20260430_094328.txt
