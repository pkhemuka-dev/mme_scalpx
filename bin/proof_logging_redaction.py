#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES = [
    "app/mme_scalpx/core/settings.py",
    "app/mme_scalpx/main.py",
    "app/mme_scalpx/integrations/dhan_runtime_clients.py",
    "app/mme_scalpx/integrations/provider_runtime.py",
    "etc/logging.yaml",
]

SECRET_PATTERNS = [
    re.compile(r"(?i)(password|passwd|secret|access_token|refresh_token|api_key|apikey|enctoken)\s*[:=]\s*['\"][^'\"]{6,}['\"]"),
]

REDACTION_NEEDLES = [
    "redact",
    "REDACTED",
    "secret",
    "token",
]

def read(path: str) -> str:
    p = ROOT / path
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

def main() -> int:
    checks = []
    leaks = []

    for f in FILES:
        p = ROOT / f
        checks.append({
            "case": f"file_available_or_optional:{f}",
            "status": "PASS" if p.exists() else "WARN",
            "path": f,
        })

        text = read(f)
        for pat in SECRET_PATTERNS:
            for m in pat.finditer(text):
                leaks.append({"path": f, "match": m.group(0)[:80]})

    checks.append({
        "case": "no_literal_secrets_in_runtime_files",
        "status": "PASS" if not leaks else "FAIL",
        "leak_count": len(leaks),
        "leaks": leaks[:20],
    })

    combined = "\n".join(read(f) for f in FILES)
    checks.append({
        "case": "redaction_language_present",
        "status": "PASS" if any(n in combined for n in REDACTION_NEEDLES) else "WARN",
        "note": "WARN means redaction may be externalized; manual review needed.",
    })

    failed = [c for c in checks if c["status"] == "FAIL"]
    result = {
        "proof_name": "logging_redaction",
        "proof_version": "1",
        "status": "PASS" if not failed else "FAIL",
        "timestamp_ns": time.time_ns(),
        "checks": checks,
        "failed_checks": failed,
        "uses_broker": False,
        "places_orders": False,
        "writes_live_redis": False,
        "does_not_prove": ["all_runtime_log_lines_are_redacted_under_live_broker_errors"],
    }

    out = ROOT / "run/proofs/proof_logging_redaction.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if not failed else 1

if __name__ == "__main__":
    raise SystemExit(main())
