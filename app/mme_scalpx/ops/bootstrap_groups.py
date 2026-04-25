#!/usr/bin/env python3
from __future__ import annotations

"""
ops/bootstrap_groups.py

Canonical Redis consumer-group bootstrap for ScalpX MME.

Batch 15 freeze rule
--------------------
This operator tool does not own group specs. The only source of truth is
app.mme_scalpx.core.names.get_group_specs().
"""

import argparse
import os
import sys
from dataclasses import dataclass
from typing import Iterable

import redis

from app.mme_scalpx.core import names as N


@dataclass(frozen=True, slots=True)
class GroupSpec:
    stream: str
    group: str


def _env_str(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or str(value).strip() == "":
        raise RuntimeError(f"missing required environment variable: {name}")
    return str(value).strip()


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(f"invalid integer for {name}: {raw!r}") from exc


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    value = raw.strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    raise RuntimeError(f"invalid boolean for {name}: {raw!r}")


def build_redis_client() -> redis.Redis:
    host = _env_str("SCALPX_REDIS_HOST")
    port = _env_int("SCALPX_REDIS_PORT", 6379)
    db = _env_int("SCALPX_REDIS_DB", 0)
    username = os.getenv("SCALPX_REDIS_USERNAME") or None
    password = os.getenv("SCALPX_REDIS_PASSWORD") or None
    use_tls = _env_bool("SCALPX_REDIS_TLS", True)
    tls_cert_reqs = os.getenv("SCALPX_REDIS_TLS_CERT_REQS", "required").strip().lower()
    ca_cert = os.getenv("SCALPX_REDIS_CA_CERT") or None
    client_cert = os.getenv("SCALPX_REDIS_CLIENT_CERT") or None
    client_key = os.getenv("SCALPX_REDIS_CLIENT_KEY") or None
    socket_connect_timeout = float(os.getenv("SCALPX_REDIS_CONNECT_TIMEOUT_SEC", "5") or "5")
    socket_timeout = float(os.getenv("SCALPX_REDIS_SOCKET_TIMEOUT_SEC", "5") or "5")

    ssl_cert_reqs_map = {
        "none": "none",
        "optional": "optional",
        "required": "required",
    }
    if tls_cert_reqs not in ssl_cert_reqs_map:
        raise RuntimeError(
            "SCALPX_REDIS_TLS_CERT_REQS must be one of: none, optional, required"
        )

    client = redis.Redis(
        host=host,
        port=port,
        db=db,
        username=username,
        password=password,
        ssl=use_tls,
        ssl_cert_reqs=ssl_cert_reqs_map[tls_cert_reqs] if use_tls else None,
        ssl_ca_certs=ca_cert if use_tls else None,
        ssl_certfile=client_cert if use_tls else None,
        ssl_keyfile=client_key if use_tls else None,
        socket_connect_timeout=socket_connect_timeout,
        socket_timeout=socket_timeout,
        decode_responses=True,
    )
    client.ping()
    return client


def canonical_group_specs(*, replay: bool = False) -> tuple[GroupSpec, ...]:
    raw = N.get_group_specs(replay=replay)
    out: list[GroupSpec] = []
    for stream, groups in raw.items():
        for group in groups:
            out.append(GroupSpec(stream=str(stream), group=str(group)))
    return tuple(out)


def create_group(client: redis.Redis, spec: GroupSpec, start_id: str, verbose: bool) -> str:
    try:
        client.xgroup_create(name=spec.stream, groupname=spec.group, id=start_id, mkstream=True)
        if verbose:
            print(f"CREATED  stream={spec.stream} group={spec.group} start_id={start_id}")
        return "created"
    except redis.ResponseError as exc:
        text = str(exc)
        if "BUSYGROUP" in text:
            if verbose:
                print(f"EXISTS   stream={spec.stream} group={spec.group}")
            return "exists"
        raise


def list_specs(*, replay: bool = False) -> None:
    for spec in canonical_group_specs(replay=replay):
        print(f"{spec.stream} -> {spec.group}")


def run(specs: Iterable[GroupSpec], start_id: str, verbose: bool) -> int:
    client = build_redis_client()
    created = 0
    exists = 0

    for spec in specs:
        outcome = create_group(client=client, spec=spec, start_id=start_id, verbose=verbose)
        if outcome == "created":
            created += 1
        elif outcome == "exists":
            exists += 1

    print(
        "SUMMARY "
        f"created={created} "
        f"exists={exists} "
        f"total={created + exists}"
    )
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap canonical ScalpX MME Redis consumer groups."
    )
    parser.add_argument(
        "--start-id",
        default="0",
        help="Consumer-group start ID. Use '0' for historical replayable consumption or '$' for only new entries.",
    )
    parser.add_argument(
        "--replay",
        action="store_true",
        help="Bootstrap replay consumer groups from names.get_group_specs(replay=True).",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List canonical stream->group mappings and exit.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce per-group output.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])

    if args.list:
        list_specs(replay=bool(args.replay))
        return 0

    start_id = args.start_id.strip()
    if start_id == "":
        raise RuntimeError("--start-id must not be empty")

    return run(
        specs=canonical_group_specs(replay=bool(args.replay)),
        start_id=start_id,
        verbose=not args.quiet,
    )


if __name__ == "__main__":
    raise SystemExit(main())
