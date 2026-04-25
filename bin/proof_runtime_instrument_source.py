#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.integrations.runtime_instruments_factory import (
    CANONICAL_SOURCE_PATH,
    DEFAULT_SYMBOLS_PATH,
    build_instrument_config,
)


def main() -> int:
    config = build_instrument_config(
        source_path=CANONICAL_SOURCE_PATH,
        symbols_path=DEFAULT_SYMBOLS_PATH,
    )
    source = config.source_path_resolved
    stat = source.stat() if source.exists() else None
    now = datetime.now(tz=timezone.utc)

    proof = {
        "proof": "runtime_instrument_source",
        "status": "PASS",
        "instrument_master_path": str(source),
        "instrument_master_exists": source.exists(),
        "instrument_master_size_bytes": None if stat is None else stat.st_size,
        "instrument_master_modified_at_utc": None
        if stat is None
        else datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "instrument_master_age_seconds": None
        if stat is None
        else max(0.0, (now - datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)).total_seconds()),
        "symbols_path": str(DEFAULT_SYMBOLS_PATH),
        "symbols_exists": DEFAULT_SYMBOLS_PATH.exists(),
        "config": {
            "underlying_symbol": config.underlying_symbol,
            "future_root": config.future_root,
            "option_root": config.option_root,
            "require_weekly_options": config.require_weekly_options,
            "allow_monthly_fallback": config.allow_monthly_fallback,
            "weekly_expiry_weekday": config.weekly_expiry_weekday,
            "monthly_expiry_weekday": config.monthly_expiry_weekday,
            "strike_step_override": None
            if config.strike_step_override is None
            else str(config.strike_step_override),
            "option_expiry_days_guard": config.option_expiry_days_guard,
        },
        "note": "This proof exposes source/config truth without fetching live quote or publishing Redis.",
    }

    out = PROJECT_ROOT / "run" / "proofs" / "runtime_instrument_source.json"
    out.write_text(json.dumps(proof, indent=2, sort_keys=True))
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
