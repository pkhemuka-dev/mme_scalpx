"""Compact artifact writer helpers for RAW / Research Gate.

Writers are restricted to explicit filesystem paths supplied by callers.
No Redis, broker, strategy, risk, or execution write path exists here.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def write_json_file(path: str | Path, payload: dict[str, Any]) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp, p)
    return p


def write_text_file(path: str | Path, content: str) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, p)
    return p
