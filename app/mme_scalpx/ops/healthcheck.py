"""
app/mme_scalpx/ops/healthcheck.py

Frozen-grade health snapshot tool for ScalpX MME.

Purpose
-------
Read-only operator health view over canonical Redis-backed runtime state.

Design rules
------------
- Read-only: no stream writes, hash writes, locks, or commands.
- Canonical names only; no ad hoc runtime keys.
- Safe to run repeatedly.
- Clear PASS/WARN/FAIL output.
- Conservative: checks only facts visible from Redis/env.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

import redis

from app.mme_scalpx.core.names import (
    HASH_STATE_EXECUTION,
    HASH_STATE_LOGIN,
    HASH_STATE_POSITION_MME,
    HASH_STATE_RISK,
    KEY_HEALTH_EXECUTION,
    KEY_HEALTH_FEATURES,
    KEY_HEALTH_FEEDS,
    KEY_HEALTH_INSTRUMENTS,
    KEY_HEALTH_LOGIN,
    KEY_HEALTH_MONITOR,
    KEY_HEALTH_REPORT,
    KEY_HEALTH_RISK,
    KEY_HEALTH_STRATEGY,
    KEY_LOCK_EXECUTION,
)


@dataclass(frozen=True)
class CheckResult:
    status: str  # PASS | WARN | FAIL
    code: str
    message: str


HEALTH_KEYS: Tuple[Tuple[str, str], ...] = (
    ("login", KEY_HEALTH_LOGIN),
    ("instruments", KEY_HEALTH_INSTRUMENTS),
    ("feeds", KEY_HEALTH_FEEDS),
    ("features", KEY_HEALTH_FEATURES),
    ("strategy", KEY_HEALTH_STRATEGY),
    ("risk", KEY_HEALTH_RISK),
    ("execution", KEY_HEALTH_EXECUTION),
    ("monitor", KEY_HEALTH_MONITOR),
    ("report", KEY_HEALTH_REPORT),
)

STATE_HASHES: Tuple[Tuple[str, str], ...] = (
    ("login", HASH_STATE_LOGIN),
    ("risk", HASH_STATE_RISK),
    ("execution", HASH_STATE_EXECUTION),
    ("position", HASH_STATE_POSITION_MME),
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

    return redis.Redis(
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


def _safe_int(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _first_present(mapping: dict, keys: Sequence[str]) -> Optional[str]:
    lowered = {str(k).lower(): v for k, v in mapping.items()}
    for key in keys:
        if key.lower() in lowered:
            value = lowered[key.lower()]
            if value is None:
                return None
            return str(value)
    return None


def _read_health_key(client: redis.Redis, label: str, key: str, stale_after_ms: int) -> CheckResult:
    exists = bool(client.exists(key))
    if not exists:
        return CheckResult("FAIL", "HEALTH_KEY_MISSING", f"{label}: {key} does not exist")

    ttl_ms = client.pttl(key)
    if ttl_ms == -2:
        return CheckResult("FAIL", "HEALTH_KEY_MISSING", f"{label}: {key} no longer exists")
    if ttl_ms == -1:
        return CheckResult("WARN", "HEALTH_TTL_MISSING", f"{label}: {key} exists but has no TTL")

    payload = client.hgetall(key)
    status_value = _first_present(payload, ("status", "health", "state"))
    ts_value = _first_present(
        payload,
        (
            "ts_ms",
            "timestamp_ms",
            "updated_at_ms",
            "heartbeat_ts_ms",
            "last_seen_ms",
        ),
    )
    ts_ms = _safe_int(ts_value)

    if ttl_ms <= 0:
        return CheckResult("FAIL", "HEALTH_STALE", f"{label}: {key} ttl_ms={ttl_ms}")

    if ttl_ms < stale_after_ms:
        base = f"{label}: {key} ttl_ms={ttl_ms}"
        if status_value is not None:
            base += f" status={status_value}"
        if ts_ms is not None:
            age_ms = max(0, int(time.time() * 1000) - ts_ms)
            base += f" age_ms={age_ms}"
        return CheckResult("WARN", "HEALTH_NEAR_STALE", base)

    message = f"{label}: {key} ttl_ms={ttl_ms}"
    if status_value is not None:
        message += f" status={status_value}"
    if ts_ms is not None:
        age_ms = max(0, int(time.time() * 1000) - ts_ms)
        message += f" age_ms={age_ms}"
    return CheckResult("PASS", "HEALTH_OK", message)


def _read_state_hash_presence(client: redis.Redis, label: str, key: str) -> CheckResult:
    exists = bool(client.exists(key))
    if not exists:
        return CheckResult("WARN", "STATE_HASH_MISSING", f"{label}: {key} does not exist")

    fields = client.hlen(key)
    payload = client.hgetall(key)
    summary_parts = [f"{label}: {key}", f"fields={fields}"]

    if label == "execution":
        mode = _first_present(payload, ("mode", "execution_mode", "state"))
        if mode is not None:
            summary_parts.append(f"mode={mode}")
    elif label == "position":
        side = _first_present(payload, ("side", "position_side", "state"))
        if side is not None:
            summary_parts.append(f"side={side}")
    elif label == "risk":
        veto = _first_present(payload, ("veto_entries", "entries_vetoed", "block_entries"))
        if veto is not None:
            summary_parts.append(f"veto_entries={veto}")
    elif label == "login":
        login_state = _first_present(payload, ("status", "state", "login_status"))
        if login_state is not None:
            summary_parts.append(f"status={login_state}")

    return CheckResult("PASS", "STATE_HASH_OK", " ".join(summary_parts))


def _read_execution_lock(client: redis.Redis) -> CheckResult:
    exists = bool(client.exists(KEY_LOCK_EXECUTION))
    if not exists:
        return CheckResult("WARN", "EXEC_LOCK_MISSING", f"{KEY_LOCK_EXECUTION} does not exist")

    ttl_ms = client.pttl(KEY_LOCK_EXECUTION)
    owner = client.get(KEY_LOCK_EXECUTION)

    if ttl_ms == -1:
        return CheckResult(
            "WARN",
            "EXEC_LOCK_NO_TTL",
            f"{KEY_LOCK_EXECUTION} exists owner={owner!r} but has no TTL",
        )
    if ttl_ms <= 0:
        return CheckResult(
            "WARN",
            "EXEC_LOCK_STALE",
            f"{KEY_LOCK_EXECUTION} exists owner={owner!r} ttl_ms={ttl_ms}",
        )

    return CheckResult(
        "PASS",
        "EXEC_LOCK_OK",
        f"{KEY_LOCK_EXECUTION} owner={owner!r} ttl_ms={ttl_ms}",
    )


def _redis_ping_check(client: redis.Redis) -> CheckResult:
    try:
        pong = client.ping()
        if pong is True:
            return CheckResult("PASS", "REDIS_PING_OK", "Redis ping succeeded")
        return CheckResult("FAIL", "REDIS_PING_BAD", f"unexpected Redis ping response: {pong!r}")
    except Exception as exc:  # pragma: no cover - defensive by design
        return CheckResult("FAIL", "REDIS_CONNECT_FAILED", str(exc))


def run_checks(stale_after_ms: int) -> List[CheckResult]:
    client = _redis_client()
    results: List[CheckResult] = []

    results.append(_redis_ping_check(client))
    results.append(_read_execution_lock(client))

    for label, key in HEALTH_KEYS:
        results.append(_read_health_key(client, label=label, key=key, stale_after_ms=stale_after_ms))

    for label, key in STATE_HASHES:
        results.append(_read_state_hash_presence(client, label=label, key=key))

    return results


def summarize(results: List[CheckResult]) -> int:
    fail_count = sum(1 for item in results if item.status == "FAIL")
    warn_count = sum(1 for item in results if item.status == "WARN")
    pass_count = sum(1 for item in results if item.status == "PASS")

    for item in results:
        print(f"{item.status:<4} | {item.code:<22} | {item.message}")

    print(
        f"SUMMARY | pass={pass_count} warn={warn_count} fail={fail_count} total={len(results)}"
    )
    return 1 if fail_count > 0 else 0


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run read-only health snapshot checks for ScalpX MME."
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as failures.",
    )
    parser.add_argument(
        "--stale-after-ms",
        type=int,
        default=_env_int("SCALPX_HEARTBEAT_STALE_AFTER_MS", 20000),
        help="Heartbeat TTL threshold below which health is considered near-stale.",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    if args.stale_after_ms <= 0:
        raise RuntimeError("--stale-after-ms must be positive")

    results = run_checks(stale_after_ms=args.stale_after_ms)

    if args.strict:
        results = [
            CheckResult("FAIL", item.code, item.message) if item.status == "WARN" else item
            for item in results
        ]

    return summarize(results)


if __name__ == "__main__":
    raise SystemExit(main())
