Batch 28P-R1 Replay dry-run CLI/interface audit and repair contract

Date: 2026-05-01

Verdict:
PASS_GUARDED_OFFLINE_REPLAY_DRY_RUN_CLI_AUDIT_28P_R1

Accepted for:
REPLAY_DRY_RUN_CLI_INTERFACE_AUDIT_AND_REPAIR_CONTRACT_ONLY

Reason:
Batch 28P passed guard preflight but failed during guarded dry-run execution with process_returncode=2.
This batch inspects the complete 28P failure proof, 28O contract, replay_run.py CLI surface, replay entrypoint inventory, and writes a repair contract.
It does not execute replay again.

Source:
- 28P proof: run/proofs/proof_guarded_offline_replay_dry_run_execution_28p_latest.json
- 28O contract proof: run/proofs/proof_guarded_offline_replay_dry_run_contract_28o_latest.json
- replay entrypoint: bin/replay_run.py

Generated:
- etc/replay/parity/guarded_offline_replay_dry_run_cli_audit_28p_r1.json
- run/proofs/proof_guarded_offline_replay_dry_run_cli_audit_28p_r1.json
- run/proofs/proof_guarded_offline_replay_dry_run_cli_audit_28p_r1_latest.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/replay_cli_interface_audit_28p_r1/

Findings:
failure_kind=ARGPARSE_OR_CLI_INTERFACE_RETURN_CODE_2
interface_gap_confirmed=true
adapter_required=true
missing_expected_flags=['--offline', '--dataset-candidate', '--output-root', '--no-broker', '--no-live-redis', '--observe-only', '--dry-run']
supported_expected_flags=[]

Safety:
starts_services=false
reads_live_redis=false
writes_live_redis=false
calls_broker_api=false
paper_armed_approved=false
live_trading_approved=false
execution_arming_created=false
real_order_sent=false
production_doctrine_changed=false
replay_run_completed=false
comparison_completed=false
full_live_replay_parity=NOT_PROVEN_IN_28P_R1

Next:
Batch 28P-R2 — guarded replay CLI adapter/compatibility repair, still not paper/live enablement.
