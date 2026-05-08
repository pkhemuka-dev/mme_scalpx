# RAW-S Replay Trade/Candidate Producer Family Emission

Date: 2026-05-01
Generated UTC: 2026-05-01T09:45:32.315244+00:00
Batch tag: batch_raw_s_replay_producer_family_emission_freeze_final_20260501_151532

Purpose: patch replay reports/artifacts producer surfaces so emitted rows carry family, side, and strategy_id where source evidence exists.

This is replay-only producer-surface work. It does not touch live runtime, brokers, Redis, orders, strategy, risk, execution, or paper/live enablement.
