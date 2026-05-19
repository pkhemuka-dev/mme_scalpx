# B1-R8B Validator Fixture/Self-Test Repair — Dry Only

Safety: dry-only validator fixture repair. No replay, no service start, no Redis write/delete, no broker call, no order, no paper/live, no PnL.

B1-R8B verifies three fixture paths:

1. valid minimal fixture -> lane_e_handoff_allowed true
2. shape-valid lifecycle-invalid fixture -> returncode 0, bundle shape true, lifecycle false
3. shape-invalid fixture -> returncode 2, bundle shape false

Validator: `bin/b1_capture_bundle_validator.py`
Proof: `run/proofs/lane_b1_r8b_validator_fixture_selftest_repair_20260512_003739.json`
