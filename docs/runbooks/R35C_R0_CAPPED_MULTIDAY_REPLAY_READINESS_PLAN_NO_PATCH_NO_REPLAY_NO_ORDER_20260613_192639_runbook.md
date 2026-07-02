# R35C_R0_CAPPED_MULTIDAY_REPLAY_READINESS_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_192639

classification: PASS_R35C_R0_CAPPED_MULTIDAY_REPLAY_READINESS_PLAN_DONE_NO_PATCH_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35C_R0_CAPPED_MULTIDAY_REPLAY_READINESS_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_192639.json`

safety pre=0/0/0 post=0/0/0 proc=0/0 replay_proc=0

## Safety baseline
orders=0 risk=0 execution=0

## Replay/risk/execution processes

## Disk
Filesystem      Size  Used Avail Use% Mounted on
/dev/root       155G  112G   44G  72% /

## Current patch markers
3407:        """R35B/R4S replay artifact slimming.
3410:        Use SCALPX_REPLAY_ARTIFACT_ROW_CAP=500 to persist small samples instead
3414:            cap = int(os.environ.get("SCALPX_REPLAY_ARTIFACT_ROW_CAP", "0") or "0")
3445:                return "<omitted_by_R35B_R4S:max_depth>"
3453:                        "_r35b_r4s_truncated": True,
3457:                        "reason": "SCALPX_REPLAY_ARTIFACT_ROW_CAP",
3465:                        out[k] = f"<omitted_by_R35B_R4S:{k}>"

## Known June staging / replay datasets
1825 run/replay/staging/B3-R61B_A7_DURABLE_CAPTURE_REPLAY_CONSUMABILITY_NO_REDIS_NO_PATCH_NO_ORDER_build_dataset_from_r61a_confirmed_durable_fut_opt_run_replay_exports_candidate_blocker_economics_audit_20260602_221650/dataset_manifest.json
1195 run/replay/staging/LANE-X-R31A-R9H_MICRO_REPLAY_DATASET_SLICE_BUILD_NO_PATCH_NO_REPLAY_NO_ORDER_build_tiny_dataset_slice_for_fast_family_bridge_replay_smoke_without_touching_source_dataset_20260607_193229_micro_dataset/dataset_manifest.json
1195 run/replay/staging/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/dataset_manifest.json
774 run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413/replay_dataset_declaration.json
684 run/replay/staging/B3-R61_A7_SEALED_DAY_REPLAY_CONSUMABILITY_AND_BLOCKER_AUDIT_NO_REDIS_NO_PATCH_NO_ORDER_build_replay_dataset_from_a7_pseal_run_offline_replay_exports_economics_candidate_blocker_analysis_20260602_220634/dataset_manifest.json
550 run/replay/staging/LANE-X-R31A-R9H_MICRO_REPLAY_DATASET_SLICE_BUILD_NO_PATCH_NO_REPLAY_NO_ORDER_build_tiny_dataset_slice_for_fast_family_bridge_replay_smoke_without_touching_source_dataset_20260607_193229_micro_dataset/_MICRO_SLICE_MARKER.json

## Known evidence bundle
-rw-rw-r-- 1 Lenovo Lenovo 7.7K Jun 13 19:12 run/evidence_bundles/R35B_FINAL_SHADOW_PNL_EVIDENCE_20260613_191226.tar.gz
-rw-rw-r-- 1 Lenovo Lenovo  141 Jun 13 19:12 run/evidence_bundles/R35B_FINAL_SHADOW_PNL_EVIDENCE_20260613_191226.tar.gz.sha256

## Proposed R35C plan
R35C plan:
1. R35C-R0: readiness inventory only. No replay.
2. R35C-R1: verify usable June days and dataset roots.
3. R35C-R2: verify capped artifact settings and no stale processes.
4. R35C-R3: one-day capped replay smoke, full shadow scope, no order.
5. R35C-R4: two-day capped replay.
6. R35C-R5: usable June capped multi-day replay.
7. R35C-R6: conservative no-pyramiding PnL summary across days.
Safety doctrine:
- no broker order
- no paper/live
- no risk/execution service start
- no Redis delete
- no lock delete
- artifact cap must be enabled
- B3/R32 heavy export skip must be enabled
