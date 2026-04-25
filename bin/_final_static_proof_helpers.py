from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]

def read(path: str) -> str:
    p = ROOT / path
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

def exists_nonempty(path: str) -> dict:
    p = ROOT / path
    return {
        "case": f"exists_nonempty:{path}",
        "status": "PASS" if p.exists() and p.stat().st_size > 0 else "FAIL",
        "path": path,
        "size": p.stat().st_size if p.exists() else 0,
    }

def contains_any(case: str, files: Iterable[str], needles: Iterable[str], *, warn: bool = False) -> dict:
    text = "\n".join(read(f) for f in files).lower()
    hits = [n for n in needles if n.lower() in text]
    return {
        "case": case,
        "status": "PASS" if hits else ("WARN" if warn else "FAIL"),
        "needles": list(needles),
        "hits": hits,
    }

def contains_all(case: str, files: Iterable[str], needles: Iterable[str], *, warn: bool = False) -> dict:
    text = "\n".join(read(f) for f in files).lower()
    missing = [n for n in needles if n.lower() not in text]
    return {
        "case": case,
        "status": "PASS" if not missing else ("WARN" if warn else "FAIL"),
        "needles": list(needles),
        "missing": missing,
    }

def regex_any(case: str, files: Iterable[str], patterns: Iterable[str], *, warn: bool = False) -> dict:
    text = "\n".join(read(f) for f in files)
    hits = []
    for pat in patterns:
        if re.search(pat, text, flags=re.IGNORECASE | re.MULTILINE):
            hits.append(pat)
    return {
        "case": case,
        "status": "PASS" if hits else ("WARN" if warn else "FAIL"),
        "patterns": list(patterns),
        "hits": hits,
    }

def emit(proof_name: str, checks: list[dict], *, does_not_prove: list[str] | None = None) -> int:
    failed = [c for c in checks if c.get("status") == "FAIL"]
    result = {
        "proof_name": proof_name,
        "proof_version": "1",
        "status": "PASS" if not failed else "FAIL",
        "timestamp_ns": time.time_ns(),
        "checks": checks,
        "failed_checks": failed,
        "uses_broker": False,
        "places_orders": False,
        "writes_live_redis": False,
        "writes_replay_redis": False,
        "does_not_prove": does_not_prove or [],
    }
    out = ROOT / "run" / "proofs" / f"{proof_name}.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if not failed else 1
