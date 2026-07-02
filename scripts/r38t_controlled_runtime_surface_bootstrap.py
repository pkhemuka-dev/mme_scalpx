#!/usr/bin/env python3
"""
R38T controlled runtime surface bootstrap.

Purpose:
- Create/repair required Redis stream + consumer group surfaces.
- Optionally verify feature hash exists before controlled-paper runtime starts.
- No order/risk/execution event write.
- No Redis delete, no XDEL/XTRIM/FLUSH.
"""

from __future__ import annotations

import json
import os
import sys
import time
from typing import Iterable

import redis


REDIS_URL = os.getenv("REDIS_URL") or os.getenv("MME_REDIS_URL") or "redis://localhost:6379/0"

REQUIRED_GROUPS = {
    "cmd:mme:stream": ("cg:risk:mme:v1", "cg:execution:mme:v1"),
    "decisions:mme:stream": ("cg:risk:mme:v1", "cg:execution:mme:v1"),
    "risk:mme:stream": ("cg:execution:mme:v1", "cg:monitor:mme:v1"),
    "execution:mme:stream": ("cg:execution:mme:v1", "cg:monitor:mme:v1"),
    "orders:mme:stream": ("cg:execution:mme:v1", "cg:monitor:mme:v1"),
    "trades:ledger:stream": ("cg:risk:mme:v1", "cg:execution:mme:v1", "cg:monitor:mme:v1"),
    "fills:mme:stream": ("cg:execution:mme:v1", "cg:monitor:mme:v1"),
    "positions:mme:stream": ("cg:risk:mme:v1", "cg:execution:mme:v1"),
    "pnl:mme:stream": ("cg:monitor:mme:v1",),
}

FEATURE_HASH_CANDIDATES = (
    "state:features:mme:fut",
    "state:features:mme",
    "features:mme:latest",
    "feature:mme:latest",
)


def stream_len(r: redis.Redis, key: str) -> int:
    try:
        return int(r.xlen(key))
    except Exception:
        return 0


def type_of(r: redis.Redis, key: str) -> str:
    try:
        raw = r.type(key)
        return raw.decode() if isinstance(raw, bytes) else str(raw)
    except Exception as exc:
        return f"ERR:{exc}"


def groups(r: redis.Redis, key: str) -> list[str]:
    try:
        out = r.xinfo_groups(key)
    except Exception:
        return []
    names = []
    for row in out:
        name = row.get("name")
        if isinstance(name, bytes):
            name = name.decode()
        if name:
            names.append(str(name))
    return names


def create_group(r: redis.Redis, stream: str, group: str) -> dict:
    try:
        r.xgroup_create(name=stream, groupname=group, id="$", mkstream=True)
        return {"stream": stream, "group": group, "status": "created"}
    except redis.ResponseError as exc:
        msg = str(exc)
        if "BUSYGROUP" in msg:
            return {"stream": stream, "group": group, "status": "already_exists"}
        return {"stream": stream, "group": group, "status": "error", "error": msg}


def verify_required_groups(r: redis.Redis) -> tuple[bool, list[str], dict]:
    missing = []
    snapshot = {}
    for stream, needed in REQUIRED_GROUPS.items():
        existing = set(groups(r, stream))
        snapshot[stream] = {
            "type": type_of(r, stream),
            "xlen": stream_len(r, stream),
            "groups": sorted(existing),
        }
        for group in needed:
            if group not in existing:
                missing.append(f"{stream}:{group}")
    return (len(missing) == 0, missing, snapshot)


def feature_surface_status(r: redis.Redis) -> dict:
    rows = {}
    ok = False
    for key in FEATURE_HASH_CANDIDATES:
        typ = type_of(r, key)
        item = {"type": typ}
        if typ == "hash":
            try:
                item["hlen"] = int(r.hlen(key))
                item["ttl"] = int(r.ttl(key))
                ok = ok or item["hlen"] > 0
            except Exception as exc:
                item["error"] = str(exc)
        elif typ == "stream":
            try:
                item["xlen"] = int(r.xlen(key))
                item["ttl"] = int(r.ttl(key))
                ok = ok or item["xlen"] > 0
            except Exception as exc:
                item["error"] = str(exc)
        else:
            try:
                item["ttl"] = int(r.ttl(key))
            except Exception:
                pass
        rows[key] = item
    return {"feature_surface_ok": ok, "keys": rows}


def main() -> int:
    r = redis.Redis.from_url(REDIS_URL, decode_responses=False)

    before_ok, before_missing, before_snapshot = verify_required_groups(r)
    creates = []
    for stream, group_list in REQUIRED_GROUPS.items():
        for group in group_list:
            creates.append(create_group(r, stream, group))

    after_ok, after_missing, after_snapshot = verify_required_groups(r)
    feature_status = feature_surface_status(r)

    danger = {
        "orders": stream_len(r, "orders:mme:stream"),
        "risk": stream_len(r, "risk:mme:stream"),
        "execution": stream_len(r, "execution:mme:stream"),
        "trades": stream_len(r, "trades:ledger:stream"),
    }

    result = {
        "classification": "PASS_R38T_SURFACE_BOOTSTRAP_READY"
        if after_ok and danger == {"orders": 0, "risk": 0, "execution": 0, "trades": 0}
        else "REVIEW_R38T_SURFACE_BOOTSTRAP_NOT_READY",
        "redis_delete_attempted": False,
        "paper_started": False,
        "broker_order_started": False,
        "before_ok": before_ok,
        "before_missing": before_missing,
        "after_ok": after_ok,
        "after_missing": after_missing,
        "creates": creates,
        "before_snapshot": before_snapshot,
        "after_snapshot": after_snapshot,
        "feature_status": feature_status,
        "danger_streams": danger,
        "created_at_ns": time.time_ns(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["classification"].startswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
