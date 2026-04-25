#!/usr/bin/env python3
from __future__ import annotations

"""
Redis contract matrix proof.

Default mode:
- Validates names.py.
- Emits raw canonical Redis-name literal hits outside names.py for review.
- Fails on known stale legacy literals in live source.

Strict mode:
    .venv/bin/python bin/proof_redis_contract_matrix.py --strict-raw

- Also fails on raw canonical Redis-name literals outside names.py.

This proof validates live source, not archived audit bundles.
"""

import argparse
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.core import names as N


ROOT = PROJECT_ROOT

STALE_LITERALS = (
    "state:" + "dhan:context",
    "state:" + "dhan_context",
    "state:" + "option_confirm",
    "state:" + "provider_runtime",
)

EXCLUDED_PREFIXES = (
    ".venv/",
    "run/_code_backups/",
    "run/audit_bundle_",
    "run/proofs/",
)

EXCLUDED_FILES = {
    "app/mme_scalpx/core/names.py",
    "bin/proof_names_hardening.py",
    "bin/proof_redis_contract_matrix.py",
}


def _is_excluded(rel: str) -> bool:
    return rel in EXCLUDED_FILES or any(rel.startswith(prefix) for prefix in EXCLUDED_PREFIXES)


def _canonical_redis_names() -> tuple[str, ...]:
    values: set[str] = set()

    for attr in (
        "LIVE_STREAM_NAMES",
        "LIVE_PROVIDER_STREAM_NAMES",
        "REPLAY_STREAM_NAMES",
        "REPLAY_PROVIDER_STREAM_NAMES",
        "LIVE_STATE_HASH_NAMES",
        "LIVE_PROVIDER_STATE_HASH_NAMES",
        "REPLAY_STATE_HASH_NAMES",
        "REPLAY_PROVIDER_STATE_HASH_NAMES",
        "LIVE_HEALTH_KEYS",
        "LIVE_PROVIDER_HEALTH_KEYS",
        "REPLAY_HEALTH_KEYS",
        "REPLAY_PROVIDER_HEALTH_KEYS",
        "LIVE_LOCK_KEYS",
        "REPLAY_LOCK_KEYS",
        "LIVE_NOTIFY_CHANNELS",
        "REPLAY_NOTIFY_CHANNELS",
        "LIVE_GROUP_NAMES",
        "REPLAY_GROUP_NAMES",
    ):
        values.update(getattr(N, attr))

    values.update(N.get_group_specs(replay=False).keys())
    values.update(N.get_group_specs(replay=True).keys())

    for groups in N.get_group_specs(replay=False).values():
        values.update(groups)
    for groups in N.get_group_specs(replay=True).values():
        values.update(groups)

    return tuple(sorted(values, key=lambda x: (len(x), x)))


def _python_files() -> list[Path]:
    files: list[Path] = []

    for path in ROOT.rglob("*.py"):
        rel = path.relative_to(ROOT).as_posix()

        if "__pycache__" in rel or _is_excluded(rel):
            continue

        files.append(path)

    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict-raw",
        action="store_true",
        help="Fail on raw canonical Redis-name literals outside names.py.",
    )
    args = parser.parse_args()

    N.validate_names_contract()

    stale_hits: list[dict[str, str]] = []
    raw_hits: list[dict[str, str]] = []

    canonical_names = _canonical_redis_names()

    for path in _python_files():
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(errors="replace")

        for literal in STALE_LITERALS:
            if literal in text:
                stale_hits.append({"file": rel, "literal": literal})

        for name in canonical_names:
            if not name:
                continue
            if re.search(re.escape(name), text):
                raw_hits.append({"file": rel, "literal": name})

    failures: list[object] = []
    if stale_hits:
        failures.append({"stale_literals": stale_hits})
    if args.strict_raw and raw_hits:
        failures.append({"raw_canonical_literals": raw_hits})

    proof = {
        "proof": "redis_contract_matrix",
        "status": "FAIL" if failures else "PASS",
        "strict_raw": args.strict_raw,
        "canonical_name_count": len(canonical_names),
        "stale_literal_hits": stale_hits,
        "raw_canonical_literal_hits": raw_hits,
        "failures": failures,
    }

    out = ROOT / "run" / "proofs" / "redis_contract_matrix.json"
    out.write_text(json.dumps(proof, indent=2, sort_keys=True))
    print(json.dumps(proof, indent=2, sort_keys=True))

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
