# R19 patch plan: bridge gate after candidate dry-run

## R18 facts

R18 showed:
- snapshot.validity=OK
- snapshot.sync_ok=true
- selected_option.tradability_ok=true
- selected_option_present=true
- safe_to_consume=true
- candidate dry-run observed in decisions
- but action remains HOLD with reason `hold_only_family_features_consumer_bridge`
- provider_ready_classic=false because classic runtime mode is null / not mapped into consumer contract
- stage_flags.tradability_ok=false even though selected_option.tradability_ok=true

## Required patch direction

Patch only the feature/strategy consumer bridge mapping. Do not change strategy thresholds and do not force candidates.

The patch should:
1. Preserve observe-only safety.
2. Allow provider_ready_classic to be true when:
   - snapshot valid + sync_ok
   - futures provider is HEALTHY
   - selected option provider is HEALTHY or FAILOVER_ACTIVE with selected option present
   - selected option market data is valid/tradable
   - classic runtime mode missing/null is normalized to NORMAL/OBSERVE, not treated as disabled
3. Allow stage_flags.tradability_ok to reflect selected_option.tradability_ok / selected_option_tradability_ok when the selected option block is present.
4. Keep MISO provider readiness stricter if Dhan option context is unavailable.
5. Keep final action HOLD unless existing strategy family candidate logic naturally emits candidate.
6. No paper/live/order/risk/execution enablement.
7. No fake candidate and no forced ENTER.
8. After patch: compile, restart observe-only services, then rerun candidate gate. Only after candidate gate and hard pstatus gate can controlled paper be considered.

## Explicitly forbidden

- Do not patch risk/execution/order/broker path.
- Do not enable SCALPX_ENABLE_PAPER or SCALPX_CONTROLLED_PAPER_ARMED.
- Do not run R38EN.
- Do not bypass pstatus.
- Do not convert dry-run candidate into order.
