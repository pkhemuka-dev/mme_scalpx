# Batch 26-OI-D — OI Replay/Report Impact Proof

Date: 2026-04-30

## Verdict

`final_verdict = PASS`

## Scope

This batch is proof/report only.

No family strategy code was changed.
No live trading behavior was promoted.
No hard OI filter was added.
No strategy.py promotion path was enabled.
No order-intent publication was enabled.
No risk/execution path was changed.

## Purpose

Measure the impact of Batch 26-OI-C soft scoring before any future hard-veto discussion.

## Aggregate Impact

- Matrix rows: `50`
- Original pass count: `32`
- Current pass count: `50`
- Candidate count delta current minus original: `18`
- Current OI hard veto count: `0`
- OI soft recovered count: `18`
- Score increase count: `16`
- Score decrease count: `0`
- Score unchanged count: `34`

## Safety Results

- Canonical wall authority preserved: `True`
- Strategy HOLD-only preserved: `True`
- Live order bypass detected: `False`
- OI used as immediate trigger detected: `False`
- OI hard veto count: `0`

## Family Impact Summary

- `MISB`: original_pass=`4`, current_pass=`10`, candidate_delta=`6`, oi_hard_veto=`0`, score_delta_mean=`0.138`
- `MISC`: original_pass=`8`, current_pass=`10`, candidate_delta=`2`, oi_hard_veto=`0`, score_delta_mean=`0.04`
- `MISO`: original_pass=`8`, current_pass=`10`, candidate_delta=`2`, oi_hard_veto=`0`, score_delta_mean=`0.0`
- `MISR`: original_pass=`8`, current_pass=`10`, candidate_delta=`2`, oi_hard_veto=`0`, score_delta_mean=`0.04800000000000001`
- `MIST`: original_pass=`4`, current_pass=`10`, candidate_delta=`6`, oi_hard_veto=`0`, score_delta_mean=`0.12`

## Blocking Failures

- None.

## Artifacts

- `run/proofs/proof_oi_replay_report_impact.json`
- `run/proofs/proof_oi_replay_report_impact_matrix.csv`

## Recommended Next Step

Batch 26-OI-E is NOT recommended yet for hard veto. First run market-session/replay candidate-impact observation using this matrix and compare real candidate counts.
