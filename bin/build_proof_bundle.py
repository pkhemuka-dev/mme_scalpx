#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tarfile
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXCLUDE_PARTS = {"__pycache__"}
EXCLUDE_SUFFIXES = (".pyc",)
EXCLUDE_CONTAINS = (".bak", "token", "secret")


def safe_include(path: Path) -> bool:
    rel = path.relative_to(PROJECT_ROOT)
    text = str(rel)
    if any(part in EXCLUDE_PARTS for part in rel.parts):
        return False
    if path.name.endswith(EXCLUDE_SUFFIXES):
        return False
    lowered = text.lower()
    if any(x in lowered for x in EXCLUDE_CONTAINS):
        return False
    return True


def git_status() -> str:
    try:
        return subprocess.check_output(["git", "status", "--short"], cwd=PROJECT_ROOT, text=True)
    except Exception as exc:
        return f"git status unavailable: {type(exc).__name__}: {exc}\n"


def main() -> int:
    stamp = time.strftime("%Y%m%d_%H%M%S")
    out_dir = PROJECT_ROOT / "run/proof_bundles"
    out_dir.mkdir(parents=True, exist_ok=True)

    status_path = out_dir / f"git_status_{stamp}.txt"
    status_path.write_text(git_status())

    bundle_path = out_dir / f"mme_proof_bundle_{stamp}.tar.gz"

    candidates = []
    for p in [
        PROJECT_ROOT / "etc/proof_registry.yaml",
        PROJECT_ROOT / "etc/config_registry.yaml",
        PROJECT_ROOT / "docs/systemd_runtime_unit_registry.md",
        PROJECT_ROOT / "docs/contracts/compatibility_alias_registry.md",
        status_path,
    ]:
        if p.exists() and safe_include(p):
            candidates.append(p)

    for p in (PROJECT_ROOT / "run/proofs").glob("*.json"):
        if safe_include(p):
            candidates.append(p)

    for p in (PROJECT_ROOT / "run/proofs/latest").glob("*.json"):
        if safe_include(p):
            candidates.append(p)

    manifest = {
        "created_at_ns": time.time_ns(),
        "bundle_path": str(bundle_path.relative_to(PROJECT_ROOT)),
        "included_files": [str(p.relative_to(PROJECT_ROOT)) for p in candidates],
        "excluded_policy": {
            "parts": sorted(EXCLUDE_PARTS),
            "suffixes": list(EXCLUDE_SUFFIXES),
            "contains": list(EXCLUDE_CONTAINS),
        },
    }

    manifest_path = out_dir / f"manifest_{stamp}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    candidates.append(manifest_path)

    with tarfile.open(bundle_path, "w:gz") as tf:
        for p in candidates:
            tf.add(p, arcname=str(p.relative_to(PROJECT_ROOT)))

    print(json.dumps(manifest, indent=2, sort_keys=True))
    print("bundle =", bundle_path.relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
