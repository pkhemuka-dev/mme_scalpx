# Systemd Runtime Unit Registry — MME ScalpX

## Batch 25S Status

This document freezes service ownership, restart order, and runtime safety alignment for the MME-ScalpX 5-family migration.

## Default Runtime

rollout_mode = observe_only
strategy_publish_mode = HOLD_ONLY
family_order_intent_publish = false
execution_arming = false
broker_orders_allowed = false

## Service Ownership

| Service | Owner role | Writes | Consumes | Lock ownership |
|---|---|---|---|---|
| feeds | Broker/feed normalization and provider runtime publication | feed/provider hashes and heartbeats | broker market data only | no execution lock |
| features | Feature construction and family_features payload | feature payload/state and feature heartbeat | feed/provider hashes | no execution lock |
| strategy | HOLD/report-only family consumer until later arming proof | decision stream and strategy heartbeat | family_features | no execution lock |
| risk | Global entry veto, limits, cooldown, loss/health gate | risk state and heartbeat | trade ledger, commands, execution health | no execution lock |
| execution | Sole order, position, ACK, and broker-order truth | orders, trade ledger, position, execution state, ACKs | strategy decisions, risk state | owns execution lock |
| monitor | Control and observability only | monitor/system health, commands where permitted | state, streams, heartbeats | no execution lock |
| report | Read-only reconstruction and reporting | report files only | streams/state snapshots | no execution lock |

## Required Startup Order

1. feeds
2. features
3. strategy

## Health-Linked Services

risk and execution are independently started but health-linked.
execution must respect risk state for entries.
risk must not block exits.

## Read-Only Law

monitor is control/observability only.
report is read-only reconstruction.
Neither owns trading truth.

## Provider-Role Law

futures marketdata preferred provider = ZERODHA
selected option marketdata provider = DHAN
option context provider = DHAN
execution primary provider = ZERODHA
execution fallback provider = DHAN manual/fallback-ready only

## Dhan Depth Honesty Law

configured target = TOP20_ENHANCED
runtime active mode must not claim TOP20_ENHANCED unless runtime activation proof exists
default closed-market/static mode = FULL_TOP5_BASE

## Service Lock Ownership

execution owns execution lock.
feeds/features/strategy/risk/monitor/report do not own execution lock.
mid-position provider migration is forbidden.
pre-position provider change invalidates setup and requires rebuild.

## Batch 25S Verdict Law

runtime_config_alignment_ok = true
systemd_runtime_alignment_ok = true
no_secret_values_in_configs = true
