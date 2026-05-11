# batch26o23_q_a5f_r3_first_controlled_paper_mist_put_1lot_20260511_143019 Runbook

First controlled-paper MIST PUT 1-lot window.

This command:
- consumes the exact A5F approval phrase for A5F-R3 only
- allows only controlled-paper MIST PUT 1-lot scope
- starts risk/execution only for the guarded window
- does not force a candidate
- does not permit real live
- does not permit broker failover
- stops risk/execution after the window
- publishes NO_TRADE / SCOPE_SIGNAL_NOT_PRESENT as a result artifact if no valid MIST PUT signal appears

Proof:
- run/proofs/proof_batch26o23_q_a5f_r3_first_controlled_paper_mist_put_1lot.json
- run/proofs/proof_batch26o23_q_a5f_r3_first_controlled_paper_mist_put_1lot_latest.json
