# MME Research Data Capture Constitution v1

## Chapter intent
This chapter defines the research/archive data contract for MME.

It is not the frozen production strategy contract.

## Non-negotiable separation
- recorded != strategy-approved
- derived != production-used
- researched != contract-changed

## Five-layer structure
1. Raw mandatory
2. Raw recommended
3. Live-derived lightweight
4. Offline-derived heavyweight
5. Audit / runtime / strategy-forensics

## Governance
- capture broadly
- derive selectively live
- derive heavily offline
- store anything hard to reconstruct later as raw capture
- keep Redis only for hot/latest/live streams
- use partitioned Parquet archive for long-term research/replay
- every manifest/archive should carry usage_class, compute_stage, and storage_target
- no silent promotion of research or audit fields into production doctrine

## Metadata attributes required for every field
- name
- type
- source
- requiredness
- compute_stage
- usage_class
- storage_target
