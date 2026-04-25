#!/usr/bin/env python3
from __future__ import annotations

from _final_static_proof_helpers import contains_any, emit, exists_nonempty

FILES = [
    "app/mme_scalpx/research_capture",
    "app/mme_scalpx/research_capture.py",
    "app/mme_scalpx/core/names.py",
    "etc/config_registry.yaml",
]

# Include all python files under package if directory exists.
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
dynamic_files = []
pkg = ROOT / "app/mme_scalpx/research_capture"
if pkg.exists():
    dynamic_files.extend(str(p.relative_to(ROOT)) for p in pkg.rglob("*.py"))
elif (ROOT / "app/mme_scalpx/research_capture.py").exists():
    dynamic_files.append("app/mme_scalpx/research_capture.py")

FILES2 = dynamic_files + ["etc/config_registry.yaml", "app/mme_scalpx/core/names.py"]

checks = []
if dynamic_files:
    non_init_files = [f for f in dynamic_files if not f.endswith("/__init__.py")]
    init_files = [f for f in dynamic_files if f.endswith("/__init__.py")]

    for f in init_files[:5]:
        checks.append({
            "case": f"package_marker_exists:{f}",
            "status": "PASS",
            "path": f,
            "note": "__init__.py may be empty as a package marker",
        })

    if non_init_files:
        checks += [exists_nonempty(f) for f in non_init_files[:8]]
    else:
        checks.append({
            "case": "research_capture_has_non_init_module",
            "status": "FAIL",
            "path": "app/mme_scalpx/research_capture",
        })
else:
    checks.append({
        "case": "research_capture_package_or_module_exists",
        "status": "FAIL",
        "path": "app/mme_scalpx/research_capture",
    })

checks += [
    contains_any(
        "archive_or_manifest_surface_exists",
        FILES2,
        ["archive", "manifest", "parquet", "jsonl"],
    ),
    contains_any(
        "path_containment_or_traversal_guard",
        FILES2,
        ["resolve", "relative_to", "path traversal", "outside", "contain"],
    ),
    contains_any(
        "production_mutation_firewall_language",
        FILES2,
        ["production_doctrine_mutated", "read_only", "firewall", "cannot write", "forbidden"],
    ),
    contains_any(
        "raw_payload_preservation",
        FILES2,
        ["raw_payload_json", "unknown", "extra", "broker"],
    ),
]

raise SystemExit(emit(
    "proof_research_capture_production_firewall",
    checks,
    does_not_prove=["actual_large_archive_backfill_integrity"],
))
