# MME-AI MAUTO-R2 — Bounded Offline Replay Supervisor

Installed updated `mauto`.

## Safe family-time usage

```bash
mauto --cycles 1 --model gpt-5-mini
mauto --cycles 2 --model gpt-5-mini --max-api-calls 3
```

## Behavior

- Uses existing latest valid script before spending API.
- Uses `mok` only if no valid expected batch script exists.
- Uses `mshow` before `mrun`.
- Uses guarded `mrun`.
- Uses `mremember` before and after.
- Stops on validation failure or mrun failure.
- Offline replay only.

## Safety

- No service start.
- No broker call.
- No live Redis write.
- No paper/live enablement.
- No real order.
