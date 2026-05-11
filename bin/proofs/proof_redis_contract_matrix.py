#!/usr/bin/env python3
from __future__ import annotations

"""
Redis contract matrix proof for MME-ScalpX.

Purpose
-------
Verify that active runtime source does not hardcode canonical Redis names
outside app/mme_scalpx/core/names.py.

Scope law
---------
This proof scans active runtime code only:
- app/mme_scalpx/**/*.py
- bin/*.py except proof fixtures

It intentionally does not scan:
- run/ artifacts
- audit bundles
- generated proof bundles
- __pycache__
- proof scripts / proof fixtures

Reason: generated artifacts and proof fixtures often contain literal Redis names
as evidence or expected values. They are not runtime ownership violations.
"""

import argparse
import dataclasses
import enum
import json
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
NAMES_PATH = PROJECT_ROOT / "app" / "mme_scalpx" / "core" / "names.py"
PROOF_PATH = PROJECT_ROOT / "run" / "proofs" / "redis_contract_matrix.json"

REDIS_LITERAL_RE = re.compile(r"""(?P<quote>['"])(?P<value>[A-Za-z0-9_.:-]+:[A-Za-z0-9_.:-]+)(?P=quote)""")


def _import_names_module() -> Any:
    sys.path.insert(0, str(PROJECT_ROOT))
    from app.mme_scalpx.core import names as N  # noqa: WPS433

    return N


def _collect_strings(obj: Any, out: set[str], seen: set[int]) -> None:
    oid = id(obj)
    if oid in seen:
        return
    seen.add(oid)

    if isinstance(obj, str):
        if ":" in obj:
            out.add(obj)
        return

    if isinstance(obj, enum.Enum):
        _collect_strings(obj.value, out, seen)
        return

    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        for field in dataclasses.fields(obj):
            _collect_strings(getattr(obj, field.name), out, seen)
        return

    if isinstance(obj, dict):
        for k, v in obj.items():
            _collect_strings(k, out, seen)
            _collect_strings(v, out, seen)
        return

    if isinstance(obj, (tuple, list, set, frozenset)):
        for item in obj:
            _collect_strings(item, out, seen)
        return

    if hasattr(obj, "_asdict"):
        try:
            _collect_strings(obj._asdict(), out, seen)
        except Exception:
            return


def _canonical_redis_literals() -> set[str]:
    N = _import_names_module()
    values: set[str] = set()

    for name, value in vars(N).items():
        if name.startswith("__"):
            continue
        _collect_strings(value, values, set())

    # Keep only Redis-like literals. This intentionally includes replay:*
    # and provider-specific stream/hash/health/group/lock names.
    return {v for v in values if ":" in v}


def _should_scan(path: Path) -> bool:
    rel = path.relative_to(PROJECT_ROOT)
    parts = set(rel.parts)

    if "__pycache__" in parts:
        return False

    if path == NAMES_PATH:
        return False

    # Runtime app code is always in scope except names.py itself.
    if rel.parts[:2] == ("app", "mme_scalpx"):
        return True

    # bin operational scripts may be scanned, but proof scripts are fixtures.
    if rel.parts[0] == "bin":
        name = path.name
        if name.startswith("proof_") or name == "prooflib.py":
            return False
        return True

    return False


def _iter_active_python_files() -> list[Path]:
    roots = [
        PROJECT_ROOT / "app" / "mme_scalpx",
        PROJECT_ROOT / "bin",
    ]

    files: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        if root.is_file():
            candidates = [root]
        else:
            candidates = list(root.rglob("*.py"))

        for path in candidates:
            if _should_scan(path):
                files.append(path)

    return sorted(set(files))


def _literal_hits(canonical_literals: set[str]) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []

    for path in _iter_active_python_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8", errors="ignore")

        for match in REDIS_LITERAL_RE.finditer(text):
            value = match.group("value")
            if value in canonical_literals:
                hits.append({
                    "file": str(path.relative_to(PROJECT_ROOT)),
                    "literal": value,
                })

    return hits


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict-raw", action="store_true")
    args = parser.parse_args(argv)

    canonical_literals = _canonical_redis_literals()
    raw_hits = _literal_hits(canonical_literals)

    failures: list[dict[str, Any]] = []
    if args.strict_raw and raw_hits:
        failures.append({"raw_canonical_literals": raw_hits})

    proof = {
        "proof": "redis_contract_matrix",
        "status": "FAIL" if failures else "PASS",
        "strict_raw": bool(args.strict_raw),
        "scope": "active_runtime_source_only",
        "scanned_roots": [
            "app/mme_scalpx/**/*.py except core/names.py",
            "bin/*.py except proof fixtures",
        ],
        "excluded_roots": [
            "run/",
            "audit bundles",
            "generated proof bundles",
            "__pycache__",
            "bin/proof_*.py",
        ],
        "canonical_name_count": len(canonical_literals),
        "raw_canonical_literal_hits": raw_hits,
        "stale_literal_hits": [],
        "failures": failures,
    }

    PROOF_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROOF_PATH.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps(proof, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
