# A6-FEED-R5E_features_provider_mapping_patch_static_compile_contract_proof_no_start_no_order_no_broker_20260513_073738 runbook

Next batch:
A6-FEED-R5F

A6-FEED-R5F must be explicit-approval only and may restart/reload observe-only features/strategy if needed.
Still forbidden:
- no paper/live enablement
- no broker order
- no risk/execution start
- no threshold relaxation
- no forced candidate

After R5F PASS:
Run A6-FEED-R5 during live session.
Only after A6-FEED-R5 PASS can A6-PAPER post-feed activation watcher rerun.
