"""
app/mme_scalpx/ops/ops_cmd.py

Frozen-grade operator command publisher for ScalpX MME.

Purpose
-------
Publish canonical operator/runtime control commands to STREAM_CMD_MME using:
- names.py command constants
- models.py OperatorCommand
- codec.py model_to_envelope_dict()

Design rules
------------
- Canonical stream only.
- Canonical typed model only.
- Canonical envelope encoding only.
- No ad hoc raw Redis payload schema.
- Safe dry-run mode.
- Explicit operator intent and correlation id.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from typing import Any, Optional

import redis

from mme_scalpx.core import names
from mme_scalpx.core.codec import model_to_envelope_dict
from mme_scalpx.core.models import OperatorCommand


ALLOWED_COMMANDS = (
    names.CMD_PARAMS_RELOAD,
    names.CMD_PAUSE_TRADING,
    names.CMD_RESUME_TRADING,
    names.CMD_FORCE_FLATTEN,
    names.CMD_SET_MODE,
)


def _env(name: str, default: Optional[str] = None) -> Optional[str]:
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


def _build_command(
    *,
    command_type: str,
    producer: str,
    reason: str | None,
    mode: str | None,
    params: dict[str, Any],
) -> OperatorCommand:
    ts_event_ns = time.time_ns()
    correlation_id = str(uuid.uuid4())

    return OperatorCommand(
        command_type=command_type,
        ts_event_ns=ts_event_ns,
        producer=producer,
        correlation_id=correlation_id,
        mode=mode,
        reason=reason,
        params=params,
    )


def _encode_command(command: OperatorCommand) -> dict[str, str]:
    return model_to_envelope_dict(
        command,
        ts_event_ns=command.ts_event_ns,
        ts_ingest_ns=time.time_ns(),
        producer=command.producer,
        correlation_id=command.correlation_id,
        stream=names.STREAM_CMD_MME,
        replay=False,
        schema_version=names.DEFAULT_SCHEMA_VERSION,
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Publish a canonical operator command to STREAM_CMD_MME."
    )
    parser.add_argument(
        "command_type",
        choices=ALLOWED_COMMANDS,
        help="Canonical command type.",
    )
    parser.add_argument(
        "--reason",
        default=None,
        help="Optional operator reason/message.",
    )
    parser.add_argument(
        "--mode",
        default=None,
        help="Required for CMD_SET_MODE; ignored otherwise.",
    )
    parser.add_argument(
        "--producer",
        default="ops_cmd",
        help="Producer label embedded in envelope and command payload.",
    )
    parser.add_argument(
        "--set",
        dest="set_items",
        action="append",
        default=[],
        help="Extra params entry in key=value form. May be supplied multiple times.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print encoded envelope fields without writing to Redis.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])

    params = _parse_set_pairs(args.set_items)
    mode = args.mode.strip() if args.mode is not None else None
    reason = args.reason.strip() if args.reason is not None else None
    producer = args.producer.strip()

    command = _build_command(
        command_type=args.command_type,
        producer=producer,
        reason=reason,
        mode=mode,
        params=params,
    )
    fields = _encode_command(command)

    print(f"STREAM      {names.STREAM_CMD_MME}")
    print(f"TYPE        {command.command_type}")
    print(f"PRODUCER    {command.producer}")
    print(f"CORRELATION {command.correlation_id}")
    print("FIELDS")
    for key in sorted(fields.keys()):
        print(f"  {key}={fields[key]}")

    if args.dry_run:
        print("DRY_RUN     no Redis write performed")
        return 0

    client = _redis_client()
    entry_id = client.xadd(names.STREAM_CMD_MME, fields=fields)
    print(f"PUBLISHED   stream={names.STREAM_CMD_MME} id={entry_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
