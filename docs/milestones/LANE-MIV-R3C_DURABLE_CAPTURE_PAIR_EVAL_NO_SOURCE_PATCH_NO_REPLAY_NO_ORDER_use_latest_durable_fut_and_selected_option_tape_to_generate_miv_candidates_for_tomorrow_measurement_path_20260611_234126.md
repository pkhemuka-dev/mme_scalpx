# LANE-MIV-R3C_DURABLE_CAPTURE_PAIR_EVAL_NO_SOURCE_PATCH_NO_REPLAY_NO_ORDER_use_latest_durable_fut_and_selected_option_tape_to_generate_miv_candidates_for_tomorrow_measurement_path_20260611_234126

Result: Latest durable futures + selected-option tape paired and evaluated by MIV-R.

Proof:
- run/proofs/LANE-MIV-R3C_DURABLE_CAPTURE_PAIR_EVAL_NO_SOURCE_PATCH_NO_REPLAY_NO_ORDER_use_latest_durable_fut_and_selected_option_tape_to_generate_miv_candidates_for_tomorrow_measurement_path_20260611_234126.json

Safety:
- no source patch
- no replay
- no broker order
- no risk/execution start
- no Redis delete
- no lock delete

Next:
- If PASS with candidates: R4 feed MIV candidate_intent-compatible rows into R32 internal chain.
- If REVIEW: inspect futures_files/option_files and row keys, then patch normalization only.
