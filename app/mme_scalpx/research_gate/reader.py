"""Read-only JSON helpers for RAW / Research Gate.

This module provides file-reading utilities only. It does not know broker APIs,
Redis, strategy logic, risk logic, or execution logic.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_json_file(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(str(p))
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object in {p}")
    return data


def read_optional_json_file(path: str | Path) -> dict[str, Any] | None:
    p = Path(path)
    if not p.exists():
        return None
    return read_json_file(p)
