#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.core import clock as C

OUT = PROJECT_ROOT / "run" / "proofs" / "clock_session_policy.json"
IST = ZoneInfo("Asia/Kolkata")


def case(name: str, ok: bool, **details: Any) -> dict[str, Any]:
    row = {"case": name, "status": "PASS" if ok else "FAIL", **details}
    if not ok:
        raise AssertionError(json.dumps(row, indent=2, sort_keys=True))
    return row


def phase_value(value: Any) -> str:
    return str(getattr(value, "value", value))


def snapshot(dt: datetime) -> dict[str, Any]:
    phase = phase_value(C.market_phase_from_ist_datetime(dt))
    can_enter = bool(C.can_enter_new_positions(dt))
    regular_open = bool(C.is_regular_market_session_open(dt))
    return {
        "dt": dt.isoformat(),
        "phase": phase,
        "can_enter_new_positions": can_enter,
        "is_regular_market_session_open": regular_open,
    }


def main() -> int:
    cases: list[dict[str, Any]] = []

    required_api = [
        "market_phase_from_ist_datetime",
        "can_enter_new_positions",
        "is_regular_market_session_open",
    ]
    missing_api = [name for name in required_api if not hasattr(C, name)]
    cases.append(case(
        "clock_required_api_present",
        not missing_api,
        missing_api=missing_api,
        required_api=required_api,
    ))

    pre_open = snapshot(datetime(2026, 4, 24, 9, 0, 0, tzinfo=IST))
    cases.append(case(
        "pre_open_blocks_fresh_entry",
        pre_open["can_enter_new_positions"] is False,
        **pre_open,
    ))

    regular = snapshot(datetime(2026, 4, 24, 9, 20, 0, tzinfo=IST))
    cases.append(case(
        "regular_session_allows_fresh_entry",
        regular["phase"] == "REGULAR"
        and regular["can_enter_new_positions"] is True,
        **regular,
    ))

    weekend = snapshot(datetime(2026, 4, 25, 10, 0, 0, tzinfo=IST))
    cases.append(case(
        "weekend_blocks_fresh_entry",
        weekend["can_enter_new_positions"] is False
        and weekend["is_regular_market_session_open"] is False,
        **weekend,
    ))

    post_close = snapshot(datetime(2026, 4, 24, 15, 31, 0, tzinfo=IST))
    cases.append(case(
        "post_close_blocks_fresh_entry",
        post_close["can_enter_new_positions"] is False,
        **post_close,
    ))

    late_regular = snapshot(datetime(2026, 4, 24, 15, 11, 0, tzinfo=IST))
    cases.append(case(
        "late_regular_policy_boundary_recorded_not_changed",
        late_regular["phase"] == "REGULAR"
        and late_regular["can_enter_new_positions"] is True,
        rule=(
            "Batch 18 does not change clock.py behavior. "
            "Current core clock treats 15:11 IST as REGULAR/can_enter=True. "
            "Family-specific LAST_FRESH_ENTRY_TIME and forced-flatten policies "
            "remain strategy/session-policy owned."
        ),
        **late_regular,
    ))

    proof = {
        "proof": "clock_session_policy",
        "status": "PASS",
        "clock_behavior_changed": False,
        "batch18_clock_boundary": {
            "core_clock_owner": "generic wall/session primitives",
            "late_entry_cutoff_owned_here": False,
            "late_entry_cutoff_owner": "strategy_family/session_policy",
            "observed_late_regular_1511_can_enter": late_regular["can_enter_new_positions"],
            "observed_late_regular_1511_phase": late_regular["phase"],
        },
        "clock_api_used": {
            "phase": "market_phase_from_ist_datetime",
            "fresh_entry": "can_enter_new_positions",
            "market_open_for_management": "is_regular_market_session_open",
        },
        "cases": cases,
        "failed_cases": [],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
