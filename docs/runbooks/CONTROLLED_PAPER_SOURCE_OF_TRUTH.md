# Controlled Paper Source of Truth

## Status

Controlled paper is fail-closed by default.

The canonical controlled-paper gate is:

```text
app/mme_scalpx/services/controlled_paper_route.py
```

The canonical runtime verdict command is:

```text
bin/pstatus
```

## Mandatory rule

No controlled-paper run may start unless `pstatus` and the controlled-paper route gate both show paper is allowed.

The dashboard is visibility only. It must not:

```text
arm paper
start risk
start execution
call broker
write Redis
delete Redis
delete locks
place orders
```

## Canonical gate order

Controlled paper remains blocked if any of these is true:

```text
OBSERVE_ONLY_ACTIVE
CONTROLLED_PAPER_RUNTIME_NOT_ALLOWED
CONTROLLED_PAPER_SCOPE_ACK_MISSING_OR_INVALID
PAPER_NOT_ENABLED
PAPER_NOT_ARMED
BROKER_OR_LIVE_FLAG_ACTIVE
ORDERS_STREAM_NOT_ZERO
POSITION_NOT_FLAT
RISK_OR_EXECUTION_ALREADY_RUNNING
```

## Required same-session checks before paper

All must be proven fresh in the same session:

```text
orders:mme:stream = 0
risk:mme:stream = 0
execution:mme:stream = 0
risk process = 0
execution process = 0
position = FLAT
provider runtime = ready
selected option tradability = ready
pstatus paper_route_allowed = true
explicit user approval for micro-batch
```

## Forbidden shortcuts

Never treat any of these as paper approval:

```text
Replay synthetic PnL
Shadow PnL
Dashboard green card
Old cockpit plan
Historical proof
Dirty repo freeze
MIV-R research result
```

## PnL labelling

Replay/backtest dashboard must keep these separate:

```text
Official closed-trade PnL
Replay synthetic PnL
Shadow PnL
Broker/paper/live PnL
```

R35C/R5D synthetic PnL is explicitly:

```text
PNL_COMPUTED_REPLAY_ONLY_SYNTHETIC_SHADOW_MODEL_R35C_R5C_NOT_BROKER_NOT_PAPER_NOT_LIVE
```

## Current rule

Observe-only / live-shadow can continue.

Controlled paper remains blocked until a separate micro-batch explicitly passes the canonical gate and receives user approval.
