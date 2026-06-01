# B1-PROFIT-LIVE-R38C_STATIC_IMPORT_VALIDATION_AFTER_PROVIDER_FALLBACK_PATCH_NO_START_NO_ORDER

Classification: **PASS_R38C_STATIC_IMPORT_VALIDATION_NO_START_NO_ORDER**

## Validation

- compile_ok=true
- import_ok=true
- marker_count=1
- dangerous_count=0

## Safety

- orders=0
- risk_stream=0
- execution_stream=0
- risk_pids=0
- execution_pids=0

## Patch context

```text
631:     elif config.failover_mode == names.PROVIDER_FAILOVER_MODE_AUTO_AFTER_PROOF:
632:         desired_provider_id = first_eligible_provider_id or preferred_provider_id
633:     else:
634:         desired_provider_id = previous_provider_id or preferred_provider_id
635: 
636:     # B1_PROFIT_LIVE_R38B_SELECTED_OPTION_ZERODHA_FALLBACK_BEGIN
637:     # Narrow doctrine:
638:     # - In MANUAL failover mode, keep the general policy unchanged for all roles.
639:     # - Exception: selected_option_marketdata may degrade from DHAN to ZERODHA
640:     #   when DHAN is unavailable and ZERODHA is already the first eligible provider.
641:     # - This does not change option_context, MISO doctrine, execution provider,
642:     #   risk, paper, live, broker orders, Redis deletion, or process control.
643:     if (
644:         role == "selected_option_marketdata"
645:         and config.failover_mode == names.PROVIDER_FAILOVER_MODE_MANUAL
646:         and config.override_mode == names.PROVIDER_OVERRIDE_MODE_AUTO
647:         and not has_open_position
648:         and first_eligible_provider_id is not None
649:         and first_eligible_provider_id != desired_provider_id
650:         and not _status_allows_active_assignment(status_by_provider[desired_provider_id])
651:         and _status_allows_active_assignment(status_by_provider[first_eligible_provider_id])
652:     ):
653:         desired_provider_id = first_eligible_provider_id
654:     # B1_PROFIT_LIVE_R38B_SELECTED_OPTION_ZERODHA_FALLBACK_END
655: 
656:     blocked_mid_position_switch = False
657:     pending_failover = False
658: 
659:     if (
660:         has_open_position
661:         and config.require_flat_for_role_switch
```

## Next

If PASS, run R38D fixture behavior validation. Do not start live services yet.
