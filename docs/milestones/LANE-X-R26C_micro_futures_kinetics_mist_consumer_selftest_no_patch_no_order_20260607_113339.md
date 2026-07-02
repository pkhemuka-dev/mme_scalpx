# R26C Micro Futures Kinetics MIST Consumer Selftest

## FeatureEngine futures output
- surface.micro_futures_kinetics_source: micro_futures_kinetics
- surface.micro_futures_kinetics_ready: True
- surface.micro_futures_kinetics_sample_count: 4
- surface.delta_3: 8.0
- surface.ltp_delta_3: 8.0
- surface.velocity_ratio: 160.0
- surface.vel_ratio: 160.0
- surface.volume_norm: 5.0
- surface.vol_norm: 5.0
- surface.micro_futures_event_rate_norm: 5.0

## Contract futures block
- block.delta_3: 8.0
- block.ltp_delta_3: 8.0
- block.velocity_ratio: 160.0
- block.vel_ratio: 160.0
- block.volume_norm: 5.0
- block.vol_norm: 5.0
- block.micro_futures_kinetics_source: micro_futures_kinetics
- block.micro_futures_kinetics_ready: True

## R22 option output
- option.option_response_source: micro_option_response
- option.option_response_ready: True
- option.option_response_sample_count: 2
- option.delta_3: 0.5
- option.velocity_ratio: 10.0
- option.response_efficiency: 10.0

## MIST source-read predicate clues
- source_has_delta_3: True
- source_has_velocity_ratio: True
- source_has_volume_norm_or_vol_norm: True
- source_has_futures_impulse_ok: True

R26C_MIST_CONSUMER_PRIMITIVE_SELFTEST_OK=True

## Interpretation
- This does not force or create a candidate.
- This proves R26B generates the futures primitives that MIST source reads for futures_impulse.
- Next validation should use sealed Day-5 replay/shadow comparison before any further strategy patch.