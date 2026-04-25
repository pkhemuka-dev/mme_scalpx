#!/usr/bin/env python3
from __future__ import annotations

import compileall
import json
import sys
import time
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROOF_PATH = ROOT / "run" / "proofs" / "replay_batch16_freeze.json"

TARGET_FILES = (
    "app/mme_scalpx/replay/__init__.py",
    "app/mme_scalpx/replay/artifacts.py",
    "app/mme_scalpx/replay/clock.py",
    "app/mme_scalpx/replay/comparison_artifacts.py",
    "app/mme_scalpx/replay/contracts.py",
    "app/mme_scalpx/replay/dataset.py",
    "app/mme_scalpx/replay/differential.py",
    "app/mme_scalpx/replay/engine.py",
    "app/mme_scalpx/replay/experiments.py",
    "app/mme_scalpx/replay/fill_model.py",
    "app/mme_scalpx/replay/frame_export.py",
    "app/mme_scalpx/replay/injector.py",
    "app/mme_scalpx/replay/integrity.py",
    "app/mme_scalpx/replay/metrics.py",
    "app/mme_scalpx/replay/modes.py",
    "app/mme_scalpx/replay/overrides.py",
    "app/mme_scalpx/replay/reports.py",
    "app/mme_scalpx/replay/runner.py",
    "app/mme_scalpx/replay/selectors.py",
    "app/mme_scalpx/replay/topology.py",
)

def assert_case(name: str, condition: bool, details: dict[str, Any] | None = None) -> dict[str, Any]:
    row = {"name": name, "ok": bool(condition), "details": details or {}}
    if not condition:
        raise AssertionError(json.dumps(row, indent=2, sort_keys=True))
    return row

def main() -> int:
    sys.path.insert(0, str(ROOT))
    cases: list[dict[str, Any]] = []

    compile_ok = compileall.compile_dir(
        str(ROOT / "app" / "mme_scalpx" / "replay"),
        quiet=1,
        force=True,
    )
    cases.append(assert_case(
        "replay_package_compileall_passes",
        compile_ok is True,
    ))

    from app.mme_scalpx import replay
    from app.mme_scalpx.replay import artifacts, clock, contracts, dataset, engine
    from app.mme_scalpx.replay import injector, integrity, modes, runner, topology

    cases.append(assert_case(
        "replay_modules_import",
        replay.__doc__ is not None
        and hasattr(contracts, "validate_mme_replay_feature_frame")
        and hasattr(dataset, "dataset_summary_to_dict")
        and hasattr(injector, "_validate_event")
        and hasattr(integrity, "compute_integrity_verdict")
        and hasattr(engine, "validate_replay_stage_output_summary"),
    ))

    dataset_src = (ROOT / "app/mme_scalpx/replay/dataset.py").read_text(encoding="utf-8")
    cases.append(assert_case(
        "dataset_stray_return_fragment_removed",
        "return payload\n        dataset_summary=payload," not in dataset_src,
    ))

    summary = dataset.ReplayDatasetSummary(
        dataset_id="proof-dataset",
        dataset_root="/tmp/proof-dataset",
        dataset_fingerprint="abc123",
        trading_days=("2026-04-25",),
        total_days=1,
        valid_days=1,
        invalid_days=0,
        total_files=1,
        total_size_bytes=123,
        required_file_stems=(),
        optional_file_stems=(),
        supported_suffixes=(".jsonl",),
        created_at_utc="2026-04-25T00:00:00Z",
        # dataset_summary_to_dict() attaches the replay feed-input contract
        # summary. observed_source_fields must therefore describe captured feed
        # input fields, not the separate MME feature-frame payload fields tested
        # below through contracts.validate_mme_replay_feature_frame().
        observed_source_fields=(
            "ts_event",
            "symbol",
            "bid",
            "ask",
            "ltp",
        ),
        notes=("proof",),
    )
    summary_dict = dataset.dataset_summary_to_dict(summary)
    cases.append(assert_case(
        "dataset_summary_to_dict_executes",
        summary_dict["dataset_id"] == "proof-dataset"
        and "observed_source_fields" in summary_dict,
        {"keys": sorted(summary_dict.keys())[:20]},
    ))

    valid_feature = {
        "provider_runtime": {"active_futures_provider_id": "ZERODHA"},
        "stage_flags": {"provider_ready_classic": False},
        "families": {family_id: {} for family_id in contracts.MME_REPLAY_FAMILY_IDS},
    }
    valid_record = {
        "family_features_json": json.dumps(valid_feature, separators=(",", ":")),
        "family_surfaces_json": json.dumps({"surfaces_by_branch": {}}, separators=(",", ":")),
        "family_frames_json": json.dumps({"frames": {}}, separators=(",", ":")),
        "payload_json": json.dumps({"frame_id": "proof-frame"}, separators=(",", ":")),
        "ts_event_ns": "1777111200000000000",
    }
    contract_report = contracts.validate_mme_replay_feature_frame(valid_record)
    cases.append(assert_case(
        "contracts_validate_current_mme_feature_frame",
        contract_report["ok"] is True
        and contract_report["families_checked"] == list(contracts.MME_REPLAY_FAMILY_IDS),
        contract_report,
    ))

    bad_record = dict(valid_record)
    bad_record["family_features_json"] = json.dumps({"families": {}}, separators=(",", ":"))
    try:
        contracts.validate_mme_replay_feature_frame(bad_record)
        missing_stage_flags_rejected = False
    except contracts.ReplayMMEPayloadValidationError:
        missing_stage_flags_rejected = True
    cases.append(assert_case(
        "contracts_reject_missing_provider_runtime_stage_flags",
        missing_stage_flags_rejected is True,
    ))

    live_event = injector.ReplayInjectionEvent(
        sequence_id=1,
        event_time="2026-04-25T09:15:00+05:30",
        channel="ticks:mme:stream",
        payload={},
    )
    try:
        injector._validate_event(live_event)
        live_channel_rejected = False
    except injector.ReplayInjectorValidationError:
        live_channel_rejected = True
    cases.append(assert_case(
        "injector_rejects_live_channel",
        live_channel_rejected is True,
    ))

    replay_event = injector.ReplayInjectionEvent(
        sequence_id=1,
        event_time="2026-04-25T09:15:00+05:30",
        channel="replay:ticks:mme:stream",
        payload={},
    )
    injector._validate_event(replay_event)
    cases.append(assert_case(
        "injector_accepts_replay_channel",
        True,
    ))

    ordered_events = (
        injector.ReplayInjectionEvent(
            sequence_id=1,
            event_time="2026-04-25T09:15:00+05:30",
            channel="replay:ticks:mme:stream",
            payload={},
        ),
        injector.ReplayInjectionEvent(
            sequence_id=2,
            event_time="2026-04-25T03:45:01Z",
            channel="replay:ticks:mme:stream",
            payload={},
        ),
    )
    injector._validate_event_batch(ordered_events)

    # Sequence ids stay increasing; only parsed event time goes backward.
    time_reversed_events = (
        injector.ReplayInjectionEvent(
            sequence_id=1,
            event_time="2026-04-25T09:15:01+05:30",
            channel="replay:ticks:mme:stream",
            payload={},
        ),
        injector.ReplayInjectionEvent(
            sequence_id=2,
            event_time="2026-04-25T03:45:00Z",
            channel="replay:ticks:mme:stream",
            payload={},
        ),
    )
    try:
        injector._validate_event_batch(time_reversed_events)
        parsed_time_rejected = False
    except injector.ReplayInjectorValidationError:
        parsed_time_rejected = True
    cases.append(assert_case(
        "injector_event_time_order_uses_parsed_datetime",
        parsed_time_rejected is True,
    ))

    placeholder_result = integrity.ReplayIntegrityCheckResult(
        check_name=contracts.INTEGRITY_CHECK_HEARTBEAT,
        verdict=modes.IntegrityVerdict.PASS,
        message="heartbeat placeholder pass",
        details={"placeholder": True},
    )
    real_result = integrity.ReplayIntegrityCheckResult(
        check_name=contracts.INTEGRITY_CHECK_HASH_FRESHNESS,
        verdict=modes.IntegrityVerdict.PASS,
        message="real pass",
        details={},
    )
    all_results = [
        placeholder_result,
        real_result,
        integrity.ReplayIntegrityCheckResult(
            check_name=contracts.INTEGRITY_CHECK_SNAPSHOT_SYNC,
            verdict=modes.IntegrityVerdict.PASS,
            message="real pass",
            details={},
        ),
        integrity.ReplayIntegrityCheckResult(
            check_name=contracts.INTEGRITY_CHECK_STALE_LEG,
            verdict=modes.IntegrityVerdict.PASS,
            message="real pass",
            details={},
        ),
        integrity.ReplayIntegrityCheckResult(
            check_name=contracts.INTEGRITY_CHECK_RESET_CLEANLINESS,
            verdict=modes.IntegrityVerdict.PASS,
            message="real pass",
            details={},
        ),
        integrity.ReplayIntegrityCheckResult(
            check_name=contracts.INTEGRITY_CHECK_REPRODUCIBILITY,
            verdict=modes.IntegrityVerdict.PASS,
            message="real pass",
            details={},
        ),
    ]
    verdict = integrity.compute_integrity_verdict(all_results)
    cases.append(assert_case(
        "integrity_placeholder_pass_cannot_freeze_pass",
        verdict is modes.IntegrityVerdict.FAIL,
        {"verdict": verdict.value},
    ))

    stage_ok = engine.validate_replay_stage_output_summary({"records": 1})
    cases.append(assert_case(
        "engine_accepts_mapping_stage_output",
        stage_ok == {"records": 1},
        stage_ok,
    ))

    try:
        engine.validate_replay_stage_output_summary({"live_order_id": "BROKER123"})
        live_stage_output_rejected = False
    except engine.ReplayEngineValidationError:
        live_stage_output_rejected = True
    cases.append(assert_case(
        "engine_rejects_live_broker_stage_output",
        live_stage_output_rejected is True,
    ))

    topo = topology.build_topology_plan(modes.ReplayScope.FULL_SYSTEM_REPLAY)
    topo_report = topology.topology_replay_safety_report(topo)
    cases.append(assert_case(
        "topology_uses_execution_shadow_not_live_execution",
        topo_report["execution_shadow_present"] is True
        and topo_report["live_execution_stage_present"] is False
        and topo_report["safe_for_replay"] is True,
        topo_report,
    ))

    with TemporaryDirectory() as tmp:
        root = Path(tmp) / "run1"
        plan = runner.ReplayArtifactPlan(
            root_dir=str(root),
            manifest_path=str(root / "00_manifest.json"),
            log_dir=str(root / "logs"),
            artifacts_dir=str(root / "artifacts"),
            dataset_summary_path=str(root / "artifacts" / "01_dataset_summary.json"),
            scope_profile_path=str(root / "artifacts" / "02_scope_profile.json"),
            integrity_report_path=str(root / "artifacts" / "03_integrity_report.json"),
            metrics_summary_path=str(root / "artifacts" / "04_metrics_summary.json"),
            trade_log_path=str(root / "artifacts" / "05_trade_log.csv"),
            candidate_audit_path=str(root / "artifacts" / "06_candidate_audit.csv"),
            blocker_breakdown_path=str(root / "artifacts" / "07_blocker_breakdown.json"),
            exit_breakdown_path=str(root / "artifacts" / "08_exit_breakdown.json"),
            differential_report_path=str(root / "artifacts" / "09_differential_report.json"),
            effective_inputs_path=str(root / "artifacts" / "17_effective_inputs.json"),
            effective_overrides_flat_path=str(root / "artifacts" / "18_effective_overrides_flat.json"),
        )
        containment = artifacts.validate_artifact_plan_path_containment(plan)
        bad_plan = replace(plan, manifest_path=str(Path(tmp) / "escape.json"))
        try:
            artifacts.validate_artifact_plan_path_containment(bad_plan)
            escaped_path_rejected = False
        except artifacts.ReplayArtifactsValidationError:
            escaped_path_rejected = True

    cases.append(assert_case(
        "artifact_plan_path_containment_enforced",
        containment["ok"] is True and escaped_path_rejected is True,
        containment,
    ))

    # Minimal engine execution proof with safe stage output.
    run_context = SimpleNamespace(
        run_id="proof-run",
        doctrine_mode=modes.DoctrineMode.LOCKED,
    )
    small_topology = topology.build_topology_plan(modes.ReplayScope.FEEDS_ONLY)
    replay_engine = engine.ReplayEngine()
    result = replay_engine.execute(
        run_context=run_context,
        topology_plan=small_topology,
        stage_executor=lambda ctx, stage: {"stage": stage.stage_name, "records": 1},
    )
    cases.append(assert_case(
        "engine_executes_safe_mapping_stage_output",
        result.final_state is modes.ReplayRunState.COMPLETED
        and result.stage_count == 1
        and result.stage_records[0].success is True,
        engine.engine_result_to_dict(result),
    ))

    try:
        replay_engine.execute(
            run_context=run_context,
            topology_plan=small_topology,
            stage_executor=lambda ctx, stage: [("records", 1)],
        )
        non_mapping_rejected = False
    except engine.ReplayEngineError:
        non_mapping_rejected = True

    cases.append(assert_case(
        "engine_rejects_non_mapping_stage_output",
        non_mapping_rejected is True,
    ))

    proof = {
        "proof_name": "replay_batch16_freeze",
        "status": "PASS",
        "ts_epoch": time.time(),
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "compileall_pass": True,
            "dataset_p0_syntax_fixed": True,
            "mme_feature_payload_contract": True,
            "injector_replay_namespace_enforced": True,
            "injector_event_time_parsed": True,
            "placeholder_integrity_pass_rejected": True,
            "engine_stage_output_contract": True,
            "topology_shadow_execution_only": True,
            "artifact_path_containment": True,
        },
    }

    PROOF_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROOF_PATH.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps(proof["summary"], indent=2, sort_keys=True))
    print(f"proof_artifact={PROOF_PATH}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
