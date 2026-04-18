#!/usr/bin/env python3
"""
bin/research_capture_config_doctor.py

Freeze-grade config doctor for the research-capture chapter.

Purpose
-------
- prove that the canonical config registry loads successfully
- prove that registered entrypoint bundles resolve successfully
- prove that registered profile-group bundles resolve successfully
- prove that effective registry snapshots can be built successfully
- emit one auditable doctor report without mutating runtime/archive state

This script is intentionally thin and operational:
- no runtime business logic
- no archive writing
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

from app.mme_scalpx.research_capture.config_loader import (  # noqa: E402
    DEFAULT_CONFIG_REGISTRY_PATH,
    build_effective_registry_snapshot,
    load_config_registry,
    load_registered_json_contract,
    resolve_entrypoint_bundle,
    resolve_profile_group_bundle,
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
        description="Research-capture config registry doctor."
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

    entrypoint_names = ("verify", "run", "backfill", "research")
    profile_group_names = ("base", "live_capture", "historical_backfill", "offline_research", "full_bundle")

    entrypoint_bundles = {
        name: resolve_entrypoint_bundle(name, registry=registry, project_root=PROJECT_ROOT).to_dict()
        for name in entrypoint_names
    }
    profile_group_bundles = {
        name: resolve_profile_group_bundle(name, registry=registry, project_root=PROJECT_ROOT).to_dict()
        for name in profile_group_names
    }

    runtime_policy = load_registered_json_contract("runtime_policy", registry=registry, project_root=PROJECT_ROOT)
    report_policy = load_registered_json_contract("report_policy", registry=registry, project_root=PROJECT_ROOT)
    export_policy = load_registered_json_contract("export_policy", registry=registry, project_root=PROJECT_ROOT)

    effective_snapshots = {
        name: build_effective_registry_snapshot(
            entrypoint=name,
            registry=registry,
            project_root=PROJECT_ROOT,
        ).to_dict()
        for name in entrypoint_names
    }

    report = {
        "doctor_name": "MME Research Capture Config Doctor",
        "doctor_version": "v1",
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
        "entrypoint_bundles": entrypoint_bundles,
        "profile_group_bundles": profile_group_bundles,
        "policy_surface_check": {
            "runtime_policy_schema_name": runtime_policy["schema_name"],
            "report_policy_schema_name": report_policy["schema_name"],
            "export_policy_schema_name": export_policy["schema_name"],
        },
        "effective_registry_snapshots": effective_snapshots,
        "artifact_inventory": {
            "doctor_report": "config_doctor_report.json",
        },
    }

    _write_json(output_dir / "config_doctor_report.json", report)

    print("config_doctor_ok", True)
    print("registry_contract_count", len(registry.all_contracts()))
    print("entrypoint_count", len(registry.entrypoint_contracts))
    print("profile_group_count", len(registry.profile_groups))
    print("doctor_report", str(output_dir / "config_doctor_report.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
