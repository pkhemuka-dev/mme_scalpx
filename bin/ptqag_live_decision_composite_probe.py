#!/usr/bin/env python3
"""Live decision + selected option + broker GET-only composite probe.

No Redis writes. No service starts. No broker order transport.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from app.mme_scalpx.services.tqag_live_evidence_adapter import derive_tqag_live_evidence


def redis_raw(*args: str) -> str:
    proc = subprocess.run(["redis-cli", "--raw", *args], text=True, capture_output=True)
    return proc.stdout if proc.returncode == 0 else ""


def hgetall(key: str) -> dict[str, str]:
    lines = redis_raw("HGETALL", key).splitlines()
    out = {}
    for i in range(0, len(lines) - 1, 2):
        out[lines[i]] = lines[i + 1]
    return out


def latest_stream_entry(stream: str) -> dict[str, Any]:
    raw = redis_raw("XREVRANGE", stream, "+", "-", "COUNT", "1")
    lines = raw.splitlines()
    if not lines:
        return {}

    out: dict[str, Any] = {"stream_id": lines[0]}
    i = 1
    while i + 1 < len(lines):
        k = lines[i]
        v = lines[i + 1]
        out[k] = v
        if isinstance(v, str) and v.strip().startswith(("{", "[")):
            try:
                out[f"{k}__json"] = json.loads(v)
            except Exception:
                pass
        i += 2
    return out


def flatten_json(value: Any, prefix: str = "") -> dict[str, Any]:
    out = {}
    if isinstance(value, dict):
        for k, v in value.items():
            path = f"{prefix}.{k}" if prefix else str(k)
            out[path] = v
            out.update(flatten_json(v, path))
    elif isinstance(value, list):
        for i, v in enumerate(value[:20]):
            path = f"{prefix}[{i}]"
            out[path] = v
            out.update(flatten_json(v, path))
    return out


def pick_candidate(decision_entry: dict[str, Any]) -> dict[str, Any]:
    candidate = dict(decision_entry)

    for key, value in list(decision_entry.items()):
        if key.endswith("__json"):
            flat = flatten_json(value)
            for path, child in flat.items():
                # Keep both fully-qualified path and leaf name where not already present.
                candidate[path] = child
                leaf = path.split(".")[-1]
                candidate.setdefault(leaf, child)

    # Normalize common aliases expected by the adapter.
    aliases = {
        "futures_vwap_align_ok": [
            "futures_vwap_align_ok",
            "futures_alignment_ok",
            "futures_veto_clear",
            "underlying_option_aligned",
        ],
        "symbol": [
            "symbol",
            "option_symbol",
            "candidate_symbol_shadow",
            "trading_symbol",
        ],
        "token": [
            "token",
            "option_token",
            "instrument_token",
            "candidate_instrument_token_shadow",
        ],
        "target_points": [
            "target_points",
            "risk_shell.target_points",
            "expected_move_points",
        ],
        "timeframe_complete": [
            "timeframe_complete",
            "micro_observation_complete",
            "observation_complete",
        ],
        "no_chase": [
            "no_chase",
            "chase_ok",
            "breakout_not_overextended",
        ],
    }

    for canonical, names in aliases.items():
        for name in names:
            if name in candidate and candidate.get(name) not in ("", None, "null"):
                candidate.setdefault(canonical, candidate[name])
                break

    return candidate


def main() -> int:
    selected = hgetall("state:feed:selected_option:active")
    provider = hgetall("state:provider_runtime:mme")
    decision = latest_stream_entry("decisions:mme:stream")
    candidate = pick_candidate(decision)

    # Prefer selected-option symbol/token for candidate identity if decision row lacks them.
    for k in ("symbol", "trading_symbol", "option_symbol"):
        if not candidate.get("symbol") and selected.get(k):
            candidate["symbol"] = selected[k]

    for k in ("token", "instrument_token", "option_token"):
        if not candidate.get("token") and selected.get(k):
            candidate["token"] = selected[k]

    evidence = derive_tqag_live_evidence(
        selected_option=selected,
        candidate=candidate,
        provider_runtime=provider,
    )

    record = {
        "decision_stream_id": decision.get("stream_id"),
        "selected_symbol": selected.get("trading_symbol") or selected.get("option_symbol") or selected.get("symbol"),
        "candidate_symbol": candidate.get("symbol"),
        "candidate_family": candidate.get("family"),
        "candidate_side": candidate.get("side"),
        "tqag_live_evidence": evidence.to_record(),
        "can_create_order": False,
        "can_route_order": False,
        "can_send_broker_order": False,
        "real_order_allowed": False,
    }

    print(json.dumps(record, indent=2, sort_keys=True))

    blockers = record["tqag_live_evidence"].get("reasons", [])
    return 0 if not blockers else 2


if __name__ == "__main__":
    raise SystemExit(main())
