# Repair negative volume feed/snapshot normalizer — 20260505_151326

## Problem
Earlier negative-volume patch was incomplete:
- normalize_tick did not have provider_id in scope, causing NameError.
- M.OptionSnapshot.volume still received negative provider values.
- feeds error stream continued growing.

## Fix
- Removed invalid provider_id direct reference.
- Made non-negative integer guard tolerant.
- Applied volume guard to model construction blocks.
- Kept core models strict.

## Safety
- No execution/risk patch.
- No model relaxation.
- Feed-layer normalization only.
