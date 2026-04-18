#!/usr/bin/env python3
"""
bin/research_capture_config_doctor.py

Freeze-grade config doctor for the research-capture chapter.

Purpose
-------
- prove that the canonical config registry loads successfully
- prove that the config bootstrap layer resolves successfully
- prove that registered entrypoints map to policy-consistent bootstrap packages
- emit one auditable doctor artifact without mutating runtime/archive state

This script is intentionally thin and operational:
- no runtime business logic
- no archive writing
- no broker/source I/O
- no report generation beyond the doctor artifact itself
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.research_capture.config_bootstrap import (  # noqa: E402
    build_bootstrap_package,
)
from app.mme_scalpx.research_capture.config_loader import (  # noqa: E402
    DEFAULT_CONFIG_REGISTRY_PATH,
    load_config_registry,
)

DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "run" / "_smokes" / "research_capture" / "config_doctor"


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
        description="Research-capture config registry/bootstrap doctor."
    )
    parser.add_argument(
        "--config-registry",
        default=str(DEFAULT_CONFIG_REGISTRY_PATH),
        help="Path to the canonical config registry JSON.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where the doctor report will be written.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    config_registry_path = Path(args.config_registry)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    registry = load_config_registry(config_registry_path, project_root=PROJECT_ROOT)

    verify_pkg = build_bootstrap_package(
        "verify",
        registry=registry,
        project_root=PROJECT_ROOT,
    )
    run_pkg = build_bootstrap_package(
        "run",
        registry=registry,
        project_root=PROJECT_ROOT,
    )
    run_dry_pkg = build_bootstrap_package(
        "run",
        lane_override="dry_run",
        source_override="zerodha",
        registry=registry,
        project_root=PROJECT_ROOT,
    )
    backfill_pkg = build_bootstrap_package(
        "backfill",
        registry=registry,
        project_root=PROJECT_ROOT,
    )
    research_pkg = build_bootstrap_package(
        "research",
        registry=registry,
        project_root=PROJECT_ROOT,
    )
    research_override_pkg = build_bootstrap_package(
        "research",
        export_format_overrides={
            "research_summary": "csv",
            "ml_ready": "parquet",
            "audit_export": "json",
        },
        registry=registry,
        project_root=PROJECT_ROOT,
    )

    report = {
        "doctor_name": "MME Research Capture Config Doctor",
        "doctor_version": "v2",
        "doctor_ok": True,
        "ts_utc": _utc_now_z(),
        "config_registry_path": str(config_registry_path),
        "registry": {
            "schema_name": registry.schema_name,
            "policy_version": registry.policy_version,
            "source_path": registry.source_path,
            "contract_count": len(registry.all_contracts()),
            "entrypoint_count": len(registry.entrypoint_contracts),
            "profile_group_count": len(registry.profile_groups),
            "load_order": list(registry.load_order),
        },
        "bootstrap_packages": {
            "verify": verify_pkg.to_dict(),
            "run": run_pkg.to_dict(),
            "run_dry": run_dry_pkg.to_dict(),
            "backfill": backfill_pkg.to_dict(),
            "research": research_pkg.to_dict(),
            "research_override": research_override_pkg.to_dict(),
        },
        "assertions": {
            "verify_lane": verify_pkg.selected_lane,
            "run_lane": run_pkg.selected_lane,
            "run_dry_lane": run_dry_pkg.selected_lane,
            "backfill_lane": backfill_pkg.selected_lane,
            "research_lane": research_pkg.selected_lane,
            "verify_source": verify_pkg.selected_source,
            "run_source": run_pkg.selected_source,
            "backfill_source": backfill_pkg.selected_source,
            "research_source": research_pkg.selected_source,
        },
        "artifact_inventory": {
            "doctor_report": "config_doctor_report.json",
        },
    }

    _write_json(output_dir / "config_doctor_report.json", report)

    print("config_doctor_ok", True)
    print("registry_contract_count", len(registry.all_contracts()))
    print("entrypoint_count", len(registry.entrypoint_contracts))
    print("profile_group_count", len(registry.profile_groups))
    print("verify_lane", verify_pkg.selected_lane)
    print("run_lane", run_pkg.selected_lane)
    print("run_dry_lane", run_dry_pkg.selected_lane)
    print("backfill_lane", backfill_pkg.selected_lane)
    print("research_lane", research_pkg.selected_lane)
    print("doctor_report", str(output_dir / "config_doctor_report.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
