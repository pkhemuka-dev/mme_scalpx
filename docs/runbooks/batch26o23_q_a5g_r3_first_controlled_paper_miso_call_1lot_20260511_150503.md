# batch26o23_q_a5g_r3_first_controlled_paper_miso_call_1lot_20260511_150503 Runbook

First controlled-paper MISO CALL 1-lot window.

This command:
- consumes the exact A5G approval phrase for A5G-R3 only
- allows only controlled-paper MISO CALL 1-lot scope
- starts risk/execution only for the guarded window
- does not force a candidate
- does not permit real live
- does not permit broker failover
- does not permit MISO PUT without fresh/current Dhan context proof
- stops risk/execution after the window
- publishes NO_TRADE / SCOPE_SIGNAL_NOT_PRESENT as a result artifact if no valid MISO CALL signal appears

Proof:
- run/proofs/proof_batch26o23_q_a5g_r3_first_controlled_paper_miso_call_1lot.json
- run/proofs/proof_batch26o23_q_a5g_r3_first_controlled_paper_miso_call_1lot_latest.json
