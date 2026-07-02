# R33I patch plan — projected decision to paper route

## Evidence

R33G proved projected/top-enter decision exists, but orders/risk/execution/trades streams stayed zero.

## Patch target

Patch only the controlled-paper projected-decision publisher bridge.

## Required conditions before any write to orders/risk/execution stream

1. Controlled paper env only:
   - SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME=1
   - SCALPX_ENABLE_PAPER=1
   - MME_ENABLE_PAPER=1
   - SCALPX_CONTROLLED_PAPER_ARMED=1
   - SCALPX_PAPER_ARMED=1
2. Live broker env absent:
   - no SCALPX_ENABLE_LIVE
   - no MME_ENABLE_LIVE
   - no SCALPX_ALLOW_BROKER_ORDERS
3. Exact scope:
   - family/side/action/token/symbol match fresh R38EN scope lock
   - scope ack valid
4. Decision is projected:
   - action ENTER_CALL/ENTER_PUT
   - r38ee_projection_projected=true or blocker=projected
   - r33e_scoped_frame_applied=1
   - qty=1
5. Safety:
   - position flat before start
   - no prior orders/risk/execution/trade stream activity
   - stop after one event

## Forbidden

- No live broker.
- No fake candidate.
- No threshold relaxation.
- No Redis delete/trim.
- No all-strategy paper.
- No observe-only decision publishing.
- No paper publishing unless exact controlled-paper env and scope are present.
