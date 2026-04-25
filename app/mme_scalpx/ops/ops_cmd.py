#!/usr/bin/env python3
from __future__ import annotations

"""
ops/ops_cmd.py

Raw runtime command publisher for ScalpX MME.

Batch 15 freeze rule
--------------------
Runtime control commands on STREAM_CMD_MME use raw fields consumed by runtime
services:

    cmd=<canonical command>
    mode=<canonical control mode, for SET_MODE>
    reason=<operator reason>

This intentionally does not publish an OperatorCommand envelope until all
runtime consumers decode envelopes explicitly.
"""

import argparse
import json
import os
import sys
import time
import uuid
from typing import Any

import redis

from app.mme_scalpx.core import names as N


ALLOWED_COMMANDS = (
    N.CMD_PARAMS_RELOAD,
    N.CMD_PAUSE_TRADING,
    N.CMD_RESUME_TRADING,
    N.CMD_FORCE_FLATTEN,
    N.CMD_SET_MODE,
)

ALLOWED_CONTROL_MODES = (
    N.CONTROL_MODE_NORMAL,
    N.CONTROL_MODE_SAFE,
    N.CONTROL_MODE_REPLAY,
    N.CONTROL_MODE_DISABLED,
)


def _env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name, default)
    if value is None:
        return None
    value = value.strip()
    return value if value != "" else None


def _env_required(name: str) -> str:
    value = _env(name)
    if value is None:
        raise RuntimeError(f"missing required environment variable: {name}")
    return value


def _env_int(name: str, default: int) -> int:
    raw = _env(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(f"invalid integer for {name}: {raw!r}") from exc


def _env_bool(name: str, default: bool) -> bool:
    raw = _env(name)
    if raw is None:
        return default
    lowered = raw.lower()
    if lowered in {"1", "true", "yes", "on"}:
        return True
    if lowered in {"0", "false", "no", "off"}:
        return False
    raise RuntimeError(f"invalid boolean for {name}: {raw!r}")


def _redis_client() -> redis.Redis:
    host = _env_required("SCALPX_REDIS_HOST")
    port = _env_int("SCALPX_REDIS_PORT", 6379)
    db = _env_int("SCALPX_REDIS_DB", 0)
    username = _env("SCALPX_REDIS_USERNAME")
    password = _env("SCALPX_REDIS_PASSWORD")
    use_tls = _env_bool("SCALPX_REDIS_TLS", True)
    tls_cert_reqs = (_env("SCALPX_REDIS_TLS_CERT_REQS", "required") or "required").lower()
    ca_cert = _env("SCALPX_REDIS_CA_CERT")
    client_cert = _env("SCALPX_REDIS_CLIENT_CERT")
    client_key = _env("SCALPX_REDIS_CLIENT_KEY")

    if tls_cert_reqs not in {"none", "optional", "required"}:
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
        ssl_cert_reqs=tls_cert_reqs if use_tls else None,
        ssl_ca_certs=ca_cert if use_tls else None,
        ssl_certfile=client_cert if use_tls else None,
        ssl_keyfile=client_key if use_tls else None,
        socket_connect_timeout=float(_env("SCALPX_REDIS_CONNECT_TIMEOUT_SEC", "5") or "5"),
        socket_timeout=float(_env("SCALPX_REDIS_SOCKET_TIMEOUT_SEC", "5") or "5"),
        decode_responses=True,
    )
    client.ping()
    return client


def _parse_set_pairs(items: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for item in items:
        if "=" not in item:
            raise RuntimeError(f"--set requires key=value form, got {item!r}")
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key == "":
            raise RuntimeError(f"--set key must not be empty: {item!r}")
        out[key] = value
    return out


def _build_command_fields(
    *,
    command_type: str,
    producer: str,
    reason: str | None,
    mode: str | None,
    params: dict[str, Any],
) -> dict[str, str]:
    cmd = str(command_type).strip().upper()
    if cmd not in ALLOWED_COMMANDS:
        raise RuntimeError(f"unsupported command: {cmd!r}")

    if cmd == N.CMD_SET_MODE:
        resolved_mode = str(mode or "").strip().upper()
        if resolved_mode not in ALLOWED_CONTROL_MODES:
            raise RuntimeError(
                f"SET_MODE requires mode in {ALLOWED_CONTROL_MODES}, got {resolved_mode!r}"
            )
    else:
        resolved_mode = ""

    ts_ns = time.time_ns()
    correlation_id = str(uuid.uuid4())

    fields: dict[str, str] = {
        "ts_ns": str(ts_ns),
        "ts_event_ns": str(ts_ns),
        "cmd": cmd,
        "command_type": cmd,
        "producer": producer,
        "service_name": "ops_cmd",
        "correlation_id": correlation_id,
    }

    if reason:
        fields["reason"] = reason
    if resolved_mode:
        fields["mode"] = resolved_mode
    if params:
        fields["params_json"] = json.dumps(params, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        for key, value in params.items():
            key_text = str(key).strip()
            if key_text and key_text not in fields:
                fields[key_text] = str(value)

    return fields


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Publish a raw canonical operator command to STREAM_CMD_MME."
    )
    parser.add_argument("command_type", choices=ALLOWED_COMMANDS)
    parser.add_argument("--reason", default=None)
    parser.add_argument("--mode", default=None)
    parser.add_argument("--producer", default="ops_cmd")
    parser.add_argument("--set", dest="set_items", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])

    params = _parse_set_pairs(args.set_items)
    mode = args.mode.strip() if args.mode is not None else None
    reason = args.reason.strip() if args.reason is not None else None
    producer = args.producer.strip()

    fields = _build_command_fields(
        command_type=args.command_type,
        producer=producer,
        reason=reason,
        mode=mode,
        params=params,
    )

    print(f"STREAM      {N.STREAM_CMD_MME}")
    print(f"TYPE        {fields['cmd']}")
    print(f"PRODUCER    {fields['producer']}")
    print(f"CORRELATION {fields['correlation_id']}")
    print("FIELDS")
    for key in sorted(fields.keys()):
        print(f"  {key}={fields[key]}")

    if args.dry_run:
        print("DRY_RUN     no Redis write performed")
        return 0

    client = _redis_client()
    entry_id = client.xadd(N.STREAM_CMD_MME, fields=fields)
    print(f"PUBLISHED   stream={N.STREAM_CMD_MME} id={entry_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
