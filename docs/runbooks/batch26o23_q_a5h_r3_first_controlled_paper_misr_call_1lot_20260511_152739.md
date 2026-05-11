# batch26o23_q_a5h_r3_first_controlled_paper_misr_call_1lot_20260511_152739 Runbook

First controlled-paper MISR CALL 1-lot window.

This command:
- consumes the exact A5H approval phrase for A5H-R3 only
- allows only controlled-paper MISR CALL 1-lot scope
- starts risk/execution only for the guarded window
- does not force a candidate
- does not permit real live
- does not permit broker failover
- does not permit MISR PUT under this contract
- stops risk/execution after the window
- publishes NO_TRADE / SCOPE_SIGNAL_NOT_PRESENT as a result artifact if no valid MISR CALL signal appears

Proof:
- run/proofs/proof_batch26o23_q_a5h_r3_first_controlled_paper_misr_call_1lot.json
- run/proofs/proof_batch26o23_q_a5h_r3_first_controlled_paper_misr_call_1lot_latest.json
