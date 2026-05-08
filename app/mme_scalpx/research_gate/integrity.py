"""Integrity helpers for RAW / Research Gate."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from .contracts import FORBIDDEN_RAW_VERDICTS, validate_research_verdict


def sha256_file(path: str | Path) -> str:
    p = Path(path)
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(str(p))
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def artifact_info(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    return {
        "path": str(p),
        "exists": p.exists(),
        "is_file": p.is_file(),
        "bytes": p.stat().st_size if p.exists() and p.is_file() else None,
        "sha256": sha256_file(p) if p.exists() and p.is_file() else None,
    }


def assert_no_forbidden_raw_verdict(value: str) -> None:
    if value in FORBIDDEN_RAW_VERDICTS:
        raise ValueError(f"forbidden RAW verdict: {value}")


def validate_manifest_dict(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("manifest payload must be a JSON object")
    required = ("run_id", "generated_utc", "source_mode", "verdict")
    missing = [name for name in required if not payload.get(name)]
    if missing:
        raise ValueError(f"missing manifest fields: {missing}")
    validate_research_verdict(str(payload["verdict"]))
    return payload
