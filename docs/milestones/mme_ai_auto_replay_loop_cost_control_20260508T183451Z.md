# MME-AI Auto Replay Loop — Cost Controlled

Installed `mauto`.

## Usage

```bash
mauto --cycles 1 --model gpt-5-mini
mauto --cycles 2 --model gpt-5-mini
mauto --cycles 1 --model gpt-5-nano
```

## Safety

- offline replay only
- uses existing `mok/mshow/mrun/mremember`
- `mrun` guard remains mandatory
- no services
- no broker
- no live Redis write
- no paper/live enablement

## Cost control

- default model: `gpt-5-mini`
- max cycles default: 2
- max API calls default: 3
