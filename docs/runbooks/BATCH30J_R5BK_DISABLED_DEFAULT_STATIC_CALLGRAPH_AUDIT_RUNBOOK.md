# 30J-R5BK Runbook

Purpose: prove the Lane C option-only futures-context seam remains disabled by default.

This verifies that activation requires explicit `--allow-option-only-fut-context`; there is no env auto-enable; helper defaults are false; and all synthetic-context paths are guarded.

This is after-market Lane C hardening only. It does not authorize or run Lane E A64.
