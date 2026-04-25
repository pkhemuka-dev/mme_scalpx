# MME Compatibility Alias Registry

Batch: 20  
Status: freeze governance surface  
Owner: core/names.py

## Law

Compatibility aliases are allowed only when they are explicitly classified.

Allowed statuses:

- `permanent_compatibility_alias`
- `temporary_migration_alias`
- `deprecated_alias`
- `forbidden_for_new_code`

New runtime code must prefer canonical names. Temporary/deprecated aliases must have an owner and a removal condition.

## Registry

| alias | target | status | new_code_allowed | owner | removal_condition |
|---|---|---|---:|---|---|
| STREAM_CMD | STREAM_CMD_MME | temporary_migration_alias | false | core_spine | all runtime code imports STREAM_CMD_MME directly |
| STREAM_DECISIONS | STREAM_DECISIONS_MME | temporary_migration_alias | false | core_spine | all runtime code imports STREAM_DECISIONS_MME directly |
| STREAM_ORDERS | STREAM_ORDERS_MME | temporary_migration_alias | false | core_spine | all runtime code imports STREAM_ORDERS_MME directly |
| STREAM_FEATURES | STREAM_FEATURES_MME | temporary_migration_alias | false | core_spine | all runtime code imports STREAM_FEATURES_MME directly |
| STATE_FEATURES | HASH_STATE_FEATURES_MME_FUT | temporary_migration_alias | false | core_spine | all runtime code imports HASH_STATE_FEATURES_MME_FUT directly |
| STATE_POSITION | HASH_STATE_POSITION_MME | temporary_migration_alias | false | core_spine | all runtime code imports HASH_STATE_POSITION_MME directly |
| HB_FEATURES | KEY_HEALTH_FEATURES | temporary_migration_alias | false | core_spine | all runtime code imports KEY_HEALTH_FEATURES directly |
| GROUP_EXEC | GROUP_EXECUTION_MME_V1 | temporary_migration_alias | false | core_spine | all runtime code imports GROUP_EXECUTION_MME_V1 directly |
| LOCK_EXECUTION | KEY_LOCK_EXECUTION | permanent_compatibility_alias | false | core_spine | none; operator compatibility |
| EXEC_MODE_NORMAL | EXECUTION_MODE_NORMAL | temporary_migration_alias | false | core_spine | all runtime code imports EXECUTION_MODE_NORMAL directly |
| HEALTH_OK | HEALTH_STATUS_OK | temporary_migration_alias | false | core_spine | all runtime code imports HEALTH_STATUS_OK directly |

## Batch 20 note

This document does not introduce Redis names. It classifies Python symbol aliases only.
