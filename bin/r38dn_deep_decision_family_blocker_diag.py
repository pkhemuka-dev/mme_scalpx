#!/usr/bin/env python3
"""
R38DN read-only deep decision/family blocker diagnostic.

Reads Redis streams only. No writes, no deletes, no paper/risk/execution.
Explains why decisions remain HOLD/no_candidate/side=FLAT by inspecting nested
consumer_view_json / diagnostics_json / activation_report_json.
"""
from __future__ import annotations

import datetime as _dt
import json
import re
import subprocess
import sys
from collections import Counter
from typing import Any

STREAMS = [
    "decisions:mme:stream",
    "strategy:mme:stream",
    "strategy:decisions:stream",
    "decision:mme:stream",
    "candidate:audit:stream",
    "candidates:mme:stream",
]
ID_RE = re.compile(r"^[0-9]{10,17}-[0-9]+$")

FAMILIES = ("MIST", "MISB", "MISC", "MISR", "MISO", "MISLS", "MIV-R")
BRANCHES = ("CALL", "PUT")


def _run(cmd: list[str], timeout: int = 8) -> str:
    return subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    ).stdout


def _parse_xrange(raw: str) -> list[tuple[str, dict[str, str]]]:
    rows: list[tuple[str, dict[str, str]]] = []
    sid: str | None = None
    fields: dict[str, str] = {}
    key: str | None = None
    for line in raw.splitlines():
        if ID_RE.match(line):
            if sid is not None:
                rows.append((sid, fields))
            sid = line
            fields = {}
            key = None
        elif sid is not None:
            if key is None:
                key = line
            else:
                fields[key] = line
                key = None
    if sid is not None:
        rows.append((sid, fields))
    return rows


def _json(v: Any) -> Any:
    if not isinstance(v, str):
        return None
    s = v.strip()
    if not s or s[0] not in "{[":
        return None
    try:
        return json.loads(s)
    except Exception:
        return None


def _asdict(v: Any) -> dict[str, Any]:
    return v if isinstance(v, dict) else {}


def _truth(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return v != 0
    s = str(v or "").strip().lower()
    return s in {"1", "true", "yes", "y", "on", "enter", "enter_call", "enter_put"}


def _pick(d: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for k in keys:
        if k in d and d.get(k) not in (None, ""):
            return d.get(k)
    return default


def _flatten_decision(fields: dict[str, str]) -> dict[str, Any]:
    out: dict[str, Any] = dict(fields)
    for k, v in list(fields.items()):
        if k.endswith("_json") or k in {"payload", "payload_json", "consumer_view_json", "diagnostics_json", "activation_report_json"}:
            j = _json(v)
            if j is not None:
                out[k] = j
    payload = _asdict(out.get("payload_json") or out.get("payload"))
    diag = _asdict(out.get("diagnostics_json"))
    activation = _asdict(out.get("activation_report_json"))
    consumer = _asdict(out.get("consumer_view_json"))
    return {
        "flat": out,
        "payload": payload,
        "diagnostics": diag,
        "activation": activation,
        "consumer": consumer,
    }


def _family_branch_summary(consumer: dict[str, Any]) -> dict[str, Any]:
    family_status = _asdict(consumer.get("family_status"))
    family_surfaces = _asdict(consumer.get("family_surfaces"))
    branch_frames = _asdict(consumer.get("branch_frames"))
    family_frames = _asdict(consumer.get("family_frames"))

    rows: list[dict[str, Any]] = []

    # First summarize explicit family_status if present.
    for fam, val in family_status.items():
        d = _asdict(val)
        if not d:
            rows.append({"family": fam, "raw": val})
            continue
        rows.append({
            "family": fam,
            "source": "family_status",
            "active": d.get("active"),
            "eligible": d.get("eligible"),
            "reason": d.get("reason") or d.get("failed_stage") or d.get("blocked_reason"),
            "call": d.get("call") or d.get("CALL"),
            "put": d.get("put") or d.get("PUT"),
        })

    # Then scan surfaces recursively for known family/branch nodes.
    for name, val in family_surfaces.items():
        d = _asdict(val)
        fam = str(d.get("family_id") or d.get("doctrine_id") or name).upper()
        branch = str(d.get("branch_id") or d.get("side") or "").upper()
        if fam or branch:
            rows.append({
                "family": fam or name,
                "branch": branch,
                "source": "family_surfaces",
                "eligible": d.get("eligible"),
                "branch_ready": d.get("branch_ready"),
                "failed_stage": d.get("failed_stage"),
                "passed_stages": d.get("passed_stages"),
                "reason": d.get("reason") or d.get("blocked_reason") or d.get("compression_missing_reason"),
                "instrument_token": d.get("instrument_token"),
                "option_symbol": d.get("option_symbol"),
            })

        # common nested case: misc_call/misc_put/misr_call/misr_put
        for subname, subval in d.items():
            sd = _asdict(subval)
            if not sd:
                continue
            sfam = str(sd.get("family_id") or sd.get("doctrine_id") or "").upper()
            sbranch = str(sd.get("branch_id") or sd.get("side") or "").upper()
            if sfam in FAMILIES or sbranch in BRANCHES or any(x in subname.upper() for x in FAMILIES):
                surf = _asdict(sd.get("surface"))
                rows.append({
                    "family": sfam or subname,
                    "branch": sbranch,
                    "source": f"family_surfaces.{name}.{subname}",
                    "eligible": sd.get("eligible"),
                    "tradability_ok": sd.get("tradability_ok"),
                    "failed_stage": sd.get("failed_stage") or surf.get("failed_stage"),
                    "passed_stages": sd.get("passed_stages") or surf.get("passed_stages"),
                    "reason": sd.get("reason") or surf.get("compression_missing_reason") or surf.get("misr_trap_zone_failure_reason"),
                    "option_symbol": sd.get("option_symbol") or surf.get("option_symbol"),
                    "instrument_token": sd.get("instrument_token") or surf.get("instrument_token"),
                    "surface_diag": {
                        "compression_width_pct": surf.get("compression_width_pct"),
                        "compression_width_min_threshold": surf.get("compression_width_min_threshold"),
                        "compression_width_max_threshold": surf.get("compression_width_max_threshold"),
                        "compression_width_below_min": surf.get("compression_width_below_min"),
                        "compression_width_above_max": surf.get("compression_width_above_max"),
                        "misr_trap_zone_failure_reason": surf.get("misr_trap_zone_failure_reason"),
                        "active_zone_valid": surf.get("active_zone_valid"),
                    },
                })

    return {
        "family_status_count": len(family_status),
        "family_surfaces_count": len(family_surfaces),
        "branch_frames_count": len(branch_frames),
        "family_frames_count": len(family_frames),
        "rows": rows[:120],
    }


def _decision_reason(entry: dict[str, Any]) -> dict[str, Any]:
    flat = entry["flat"]
    payload = entry["payload"]
    diag = entry["diagnostics"]
    activation = entry["activation"]
    consumer = entry["consumer"]

    action = _pick(flat, "action", default=_pick(payload, "action", default=_pick(activation, "action", default="")))
    side = _pick(flat, "side", default=_pick(payload, "side", default=""))
    reason = _pick(flat, "reason", default=_pick(payload, "reason", default=_pick(activation, "reason", default="")))
    candidate_count = _pick(flat, "activation_candidate_count", default=_pick(payload, "activation_candidate_count", default=_pick(diag, "activation_candidate_count", default=0)))
    safe = _pick(flat, "activation_safe_to_promote", default=_pick(payload, "activation_safe_to_promote", default=_pick(activation, "safe_to_promote", default=False)))
    selected = _asdict(activation.get("selected"))

    if str(action).upper().startswith("ENTER"):
        category = "ENTER_VISIBLE"
    elif int(float(candidate_count or 0)) <= 0:
        category = "NO_CANDIDATE"
    elif not _truth(safe):
        category = "CANDIDATE_NOT_SAFE_TO_PROMOTE"
    elif str(side).upper() in {"", "FLAT", "UNKNOWN"}:
        category = "SIDE_NOT_PAPERABLE"
    else:
        category = "HOLD_OTHER"

    return {
        "category": category,
        "action": action,
        "side": side,
        "reason": reason,
        "candidate_count": candidate_count,
        "safe_to_promote": safe,
        "selected_family": _pick(selected, "family_id", "strategy_family_id", default=_pick(payload, "activation_selected_family_id", default="")),
        "selected_branch": _pick(selected, "branch_id", "side", default=_pick(payload, "activation_selected_branch_id", default="")),
        "selected_action": _pick(selected, "action", default=_pick(payload, "activation_selected_action", default="")),
        "consumer_hold_only": consumer.get("hold_only"),
        "consumer_reason": consumer.get("reason"),
    }


def main() -> int:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    entries: list[dict[str, Any]] = []
    for stream in STREAMS:
        raw = _run(["redis-cli", "--raw", "XREVRANGE", stream, "+", "-", "COUNT", str(limit)])
        for sid, fields in _parse_xrange(raw):
            e = _flatten_decision(fields)
            e["stream"] = stream
            e["stream_id"] = sid
            reason = _decision_reason(e)
            fam = _family_branch_summary(e["consumer"])
            entries.append({
                "stream": stream,
                "stream_id": sid,
                "decision": reason,
                "family_summary": fam,
            })

    categories = Counter(e["decision"]["category"] for e in entries)
    reasons = Counter(str(e["decision"].get("reason") or e["decision"].get("consumer_reason") or "") for e in entries)

    payload = {
        "classification": "R38DN_DEEP_DECISION_FAMILY_BLOCKER_DIAG_READONLY_NO_ORDER",
        "created_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "streams_checked": STREAMS,
        "row_count": len(entries),
        "category_counts": dict(categories),
        "reason_counts": dict(reasons),
        "entries": entries[:80],
        "paper_armed": False,
        "paper_started": False,
        "risk_started": False,
        "execution_started": False,
        "order_attempted": False,
        "redis_delete_attempted": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
