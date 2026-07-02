# LANE-X-R33A-R2_NARROW_THREE_DAY_CAPTURE_BLOCKER_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_narrow_to_real_capture_pseal_replay_artifacts_avoid_43994_file_noise_20260611_234810

classification: PASS_R33A_R2_NARROW_THREE_DAY_BLOCKER_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER

## Safety

- orders: `0`
- risk: `0`
- execution: `0`

## Narrow file count

`708`

## Day / lane counts

```
===== MATCH 20260529 =====
files=30
===== MATCH 20260602 =====
files=102
===== MATCH 20260611 =====
files=211
===== MATCH R32D =====
files=56
===== MATCH R32E =====
files=12
===== MATCH R32F =====
files=9
===== MATCH R32G =====
files=25
===== MATCH R32I =====
files=18
===== MATCH R32J =====
files=13
===== MATCH R32K =====
files=5
===== MATCH pseal =====
files=93
```

## Top blocker / gate pattern counts

```
file_count=708
```

## Next logical order

1. Fix top repeated provider/context blocker if present.
2. Then snapshot/sync validity.
3. Then tradability/data-valid/safe-to-consume.
4. Then MIV-R candidate frequency.
5. Then shadow PnL percentage.
