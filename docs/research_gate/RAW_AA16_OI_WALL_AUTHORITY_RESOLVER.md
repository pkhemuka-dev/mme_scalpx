# RAW-AA16 — OI Wall Authority Resolver

generated_at_utc: 2026-05-02T07:23:01.637505+00:00

## Verdict

OI wall strength/distance are **not derivable** in this batch.

RAW-AA16 creates only:

- required OI wall formula surface contract
- blank OI wall formula declaration template
- resolver evidence report
- OI wall field status

## Reason

Explicit formula/context declaration is required. Raw OI/strike/expiry/option_type fields alone are not accepted as deterministic authority for oi_wall_strength or oi_wall_distance_points.

## Hard rules

- No oi_wall_strength derivation.
- No oi_wall_distance_points derivation.
- No row mutation.
- No replay execution.
- No broker IO.
- No live Redis writes.
- No paper/live enablement.

## Outputs

- required contract: `etc/research_gate/raw_oi_wall_required_surface_contract.json`
- declaration template: `etc/research_gate/raw_oi_wall_formula_declaration_template.json`
- resolver report: `run/research_gate/raw_aa16_oi_wall_authority_resolver_20260502_125301/raw_aa16_oi_wall_authority_resolver_report.json`
- field status: `run/research_gate/raw_aa16_oi_wall_authority_resolver_20260502_125301/raw_aa16_oi_wall_field_status.json`