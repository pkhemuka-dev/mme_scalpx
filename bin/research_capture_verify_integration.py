#!/usr/bin/env python3
"""
bin/research_capture_verify_integration.py

Freeze-grade integration doctor for the research_capture chapter.

Purpose
-------
Prove that the frozen research_capture stack is wired coherently enough for the
first real raw-capture lane, before patching live execution paths deeper.

This verifies, end to end:
- config registry / bootstrap / context / artifact plan / materialization
- session context + effective inputs
- manifest seed + manifest materialization
- capture plan
- runtime bridge operational entrypoint
- presence/importability of the canonical frozen modules:
  manifest.py, archive_writer.py, integrity.py, health.py, router.py,
  normalizer.py, enricher.py, reader.py, utils.py

This script does NOT:
- connect to brokers
- fabricate parquet outputs
- mutate production doctrine
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.research_capture.config_loader import load_config_registry  # noqa: E402
from app.mme_scalpx.research_capture.config_bootstrap import build_bootstrap_package  # noqa: E402
from app.mme_scalpx.research_capture.config_context import build_config_context  # noqa: E402
from app.mme_scalpx.research_capture.artifact_plan import build_artifact_plan  # noqa: E402
from app.mme_scalpx.research_capture.artifact_materializer import (  # noqa: E402
    build_and_materialize_artifact_plan,
)
from app.mme_scalpx.research_capture.session_context import build_session_context  # noqa: E402
from app.mme_scalpx.research_capture.session_materializer import (  # noqa: E402
    build_and_materialize_session_context,
)
from app.mme_scalpx.research_capture.manifest_seed import (  # noqa: E402
    build_manifest_seed_from_operator_inputs,
)
from app.mme_scalpx.research_capture.manifest_materializer import (  # noqa: E402
    build_and_materialize_manifest_seed,
)
from app.mme_scalpx.research_capture.capture_plan import (  # noqa: E402
    build_capture_plan_from_operator_inputs,
)
from app.mme_scalpx.research_capture.runtime_bridge import (  # noqa: E402
    run_seeded_runtime_bridge,
)

DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "run" / "_smokes" / "research_capture" / "integration_doctor"


def _utc_now_z() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Freeze-grade research_capture integration doctor."
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where the integration doctor report will be written.",
    )
    return parser.parse_args()


def _import_surface(module_name: str) -> dict[str, Any]:
    module = importlib.import_module(module_name)
    exports = getattr(module, "__all__", None)
    return {
        "module": module_name,
        "import_ok": True,
        "file": getattr(module, "__file__", None),
        "has___all__": exports is not None,
        "export_count": len(exports) if isinstance(exports, list) else None,
    }


def main() -> int:
    args = _parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    registry = load_config_registry(project_root=PROJECT_ROOT)

    verify_bootstrap = build_bootstrap_package("verify", registry=registry, project_root=PROJECT_ROOT)
    run_bootstrap = build_bootstrap_package("run", registry=registry, project_root=PROJECT_ROOT)
    backfill_bootstrap = build_bootstrap_package("backfill", registry=registry, project_root=PROJECT_ROOT)
    research_bootstrap = build_bootstrap_package("research", registry=registry, project_root=PROJECT_ROOT)

    verify_context = build_config_context(
        "verify",
        run_id="rcap_verify_integration_20260418_demo",
        registry=registry,
        project_root=PROJECT_ROOT,
    )
    run_context = build_config_context(
        "run",
        run_id="rcap_run_integration_20260418_demo",
        registry=registry,
        project_root=PROJECT_ROOT,
    )
    backfill_context = build_config_context(
        "backfill",
        run_id="rcap_backfill_integration_20260418_demo",
        registry=registry,
        project_root=PROJECT_ROOT,
    )
    research_context = build_config_context(
        "research",
        run_id="rcap_research_integration_20260418_demo",
        registry=registry,
        project_root=PROJECT_ROOT,
    )

    verify_artifact_plan = build_artifact_plan(
        "verify",
        run_id="rcap_verify_integration_20260418_demo",
        registry=registry,
        project_root=PROJECT_ROOT,
    )
    run_artifact_materialization = build_and_materialize_artifact_plan(
        "run",
        run_id="rcap_run_integration_20260418_demo",
        registry=registry,
        project_root=PROJECT_ROOT,
    )
    run_session_context = build_session_context(
        "run",
        run_id="rcap_run_integration_20260418_demo",
        session_date="2026-04-18",
        instrument_scope="NIFTY_OPTIONS",
        registry=registry,
        project_root=PROJECT_ROOT,
    )
    run_session_materialization = build_and_materialize_session_context(
        "run",
        run_id="rcap_run_integration_20260418_demo",
        session_date="2026-04-18",
        instrument_scope="NIFTY_OPTIONS",
        registry=registry,
        project_root=PROJECT_ROOT,
    )
    run_manifest_seed = build_manifest_seed_from_operator_inputs(
        "run",
        run_id="rcap_run_integration_20260418_demo",
        session_date="2026-04-18",
        instrument_scope="NIFTY_OPTIONS",
        registry=registry,
        project_root=PROJECT_ROOT,
    )
    run_manifest_materialization = build_and_materialize_manifest_seed(
        "run",
        run_id="rcap_run_integration_20260418_demo",
        session_date="2026-04-18",
        instrument_scope="NIFTY_OPTIONS",
        registry=registry,
        project_root=PROJECT_ROOT,
    )
    run_capture_plan = build_capture_plan_from_operator_inputs(
        "run",
        run_id="rcap_run_integration_20260418_demo",
        session_date="2026-04-18",
        instrument_scope="NIFTY_OPTIONS",
        registry=registry,
        project_root=PROJECT_ROOT,
    )
    verify_bridge = run_seeded_runtime_bridge(
        "verify",
        run_id="rcap_verify_integration_20260418_demo",
        registry=registry,
        project_root=PROJECT_ROOT,
    )
    run_bridge = run_seeded_runtime_bridge(
        "run",
        run_id="rcap_run_integration_20260418_demo",
        session_date="2026-04-18",
        instrument_scope="NIFTY_OPTIONS",
        registry=registry,
        project_root=PROJECT_ROOT,
    )
    backfill_bridge = run_seeded_runtime_bridge(
        "backfill",
        run_id="rcap_backfill_integration_20260418_demo",
        start_date="2026-04-01",
        end_date="2026-04-03",
        instrument_scope="NIFTY_OPTIONS",
        registry=registry,
        project_root=PROJECT_ROOT,
    )
    research_bridge = run_seeded_runtime_bridge(
        "research",
        run_id="rcap_research_integration_20260418_demo",
        session_date="2026-04-18",
        instrument_scope="NIFTY_OPTIONS",
        research_profile="baseline_profile_v1",
        feature_families=["microstructure", "regime", "economics"],
        registry=registry,
        project_root=PROJECT_ROOT,
    )

    module_checks = {
        name: _import_surface(f"app.mme_scalpx.research_capture.{name}")
        for name in (
            "manifest",
            "archive_writer",
            "integrity",
            "health",
            "router",
            "normalizer",
            "enricher",
            "reader",
            "utils",
            "config_loader",
            "config_bootstrap",
            "config_context",
            "artifact_plan",
            "artifact_materializer",
            "session_context",
            "session_materializer",
            "manifest_seed",
            "manifest_materializer",
            "capture_plan",
            "runtime_bridge",
        )
    }

    report = {
        "doctor_name": "MME Research Capture Integration Doctor",
        "doctor_version": "v1",
        "doctor_ok": True,
        "ts_utc": _utc_now_z(),
        "registry": {
            "schema_name": registry.schema_name,
            "policy_version": registry.policy_version,
            "contract_count": len(registry.all_contracts()),
            "entrypoint_count": len(registry.entrypoint_contracts),
            "profile_group_count": len(registry.profile_groups),
        },
        "bootstrap_checks": {
            "verify_lane": verify_bootstrap.selected_lane,
            "run_lane": run_bootstrap.selected_lane,
            "backfill_lane": backfill_bootstrap.selected_lane,
            "research_lane": research_bootstrap.selected_lane,
        },
        "context_checks": {
            "verify_report_root": verify_context.report_root,
            "run_report_root": run_context.report_root,
            "backfill_report_root": backfill_context.report_root,
            "research_report_root": research_context.report_root,
        },
        "artifact_checks": {
            "verify_required_artifacts": [item.name for item in verify_artifact_plan.required_artifacts],
            "run_materialized_files": [item.name for item in run_artifact_materialization.materialized_files],
        },
        "session_checks": {
            "run_input_scope": run_session_context.effective_inputs_payload["input_scope"],
            "run_session_materialized_files": [item.name for item in run_session_materialization.materialized_files],
        },
        "manifest_checks": {
            "run_manifest_path": run_manifest_seed.manifest_path,
            "run_manifest_materialized_files": [item.name for item in run_manifest_materialization.materialized_files],
        },
        "capture_checks": {
            "run_required_outputs": [item.to_dict() for item in run_capture_plan.required_outputs],
            "run_optional_outputs": [item.to_dict() for item in run_capture_plan.optional_outputs],
        },
        "runtime_bridge_checks": {
            "verify_written_files": [item.name for item in verify_bridge.written_files],
            "run_written_files": [item.name for item in run_bridge.written_files],
            "backfill_written_files": [item.name for item in backfill_bridge.written_files],
            "research_written_files": [item.name for item in research_bridge.written_files],
        },
        "module_checks": module_checks,
        "artifact_inventory": {
            "integration_doctor_report": "integration_doctor_report.json",
        },
    }

    _write_json(output_dir / "integration_doctor_report.json", report)

    print("integration_doctor_ok", True)
    print("registry_contract_count", len(registry.all_contracts()))
    print("module_count", len(module_checks))
    print("run_required_capture_targets", [item.name for item in run_capture_plan.required_outputs])
    print("run_optional_capture_targets", [item.name for item in run_capture_plan.optional_outputs])
    print("doctor_report", str(output_dir / "integration_doctor_report.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
