# LANE-X-R31H_FEATURE_FAMILY_COMMON_KEYS_CONTRACT_SEAM_LOCATOR_NO_PATCH_NO_START_NO_ORDER_20260608_110710

If PASS:
- Review exact files/functions.
- Next batch may be a thin contract-alignment patch plan only.
- Do not patch until the producer/consumer ownership direction is clear.

Likely acceptable patch directions:
1. Expand the validator expected common-key contract to include provider-aware keys, if these keys are now frozen doctrine.
2. Or move provider-aware keys out of common if common must remain old-core-only.

Do not force candidates.
Do not tune thresholds blindly.
Do not run replay/PnL until candidate-positive evidence exists.
