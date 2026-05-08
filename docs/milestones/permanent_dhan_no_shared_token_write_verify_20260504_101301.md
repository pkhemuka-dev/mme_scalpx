# Permanent Dhan no shared-token write verification — 20260504_101301

## Verdict
Dhan login no longer writes to shared/tokens.json.

## Proofs
- run/proofs/permanent_dhan_no_shared_token_write_verify_20260504_101301_static_proof.txt
- run/proofs/permanent_dhan_no_shared_token_write_verify_20260504_101301_import_proof.txt
- run/proofs/permanent_dhan_no_shared_token_write_verify_20260504_101301_token_guard_proof.txt
- run/proofs/permanent_dhan_no_shared_token_write_verify_20260504_101301_post_plogin_token_guard_proof.txt

## Safety
- shared/tokens.json remains Zerodha-owned
- Dhan session remains broker-specific
- pfeeds token guard remains active
