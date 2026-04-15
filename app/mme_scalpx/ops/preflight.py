"""
app/mme_scalpx/ops/preflight.py

Frozen-grade preflight validator for ScalpX MME.

Purpose
-------
Read-only readiness checks before runtime startup.

Design rules
------------
- No trading side effects.
- No stream writes, hash writes, or command publication.
- Clear PASS/WARN/FAIL output.
- Safe to run repeatedly.
- Conservative: validates only facts available from env/filesystem/Redis/imports.
"""

from __future__ import annotations

import argparse
import importlib
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import redis


@dataclass(frozen=True)
class CheckResult:
    status: str  # PASS | WARN | FAIL
    code: str
    message: str


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


def _path_exists(path_str: Optional[str], *, expect_file: bool = False, expect_dir: bool = False) -> CheckResult:
    if not path_str:
        return CheckResult("FAIL", "PATH_MISSING", "required path value is empty")
    path = Path(path_str)
    if not path.exists():
        return CheckResult("FAIL", "PATH_NOT_FOUND", f"{path} does not exist")
    if expect_file and not path.is_file():
        return CheckResult("FAIL", "PATH_NOT_FILE", f"{path} is not a file")
    if expect_dir and not path.is_dir():
        return CheckResult("FAIL", "PATH_NOT_DIR", f"{path} is not a directory")
    return CheckResult("PASS", "PATH_OK", f"{path} exists")


def _path_writable_dir(path_str: Optional[str]) -> CheckResult:
    if not path_str:
        return CheckResult("FAIL", "DIR_MISSING", "required directory path value is empty")
    path = Path(path_str)
    if not path.exists():
        return CheckResult("FAIL", "DIR_NOT_FOUND", f"{path} does not exist")
    if not path.is_dir():
        return CheckResult("FAIL", "DIR_NOT_DIR", f"{path} is not a directory")
    if not os.access(path, os.W_OK):
        return CheckResult("FAIL", "DIR_NOT_WRITABLE", f"{path} is not writable")
    return CheckResult("PASS", "DIR_OK", f"{path} is writable")


def _import_check(module_name: str) -> CheckResult:
    try:
        importlib.import_module(module_name)
        return CheckResult("PASS", "IMPORT_OK", f"imported {module_name}")
    except Exception as exc:  # pragma: no cover - defensive by design
        return CheckResult("FAIL", "IMPORT_FAILED", f"{module_name}: {exc}")


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


def _redis_ping_check() -> CheckResult:
    try:
        client = _redis_client()
        pong = client.ping()
        if pong is True:
            return CheckResult("PASS", "REDIS_PING_OK", "Redis ping succeeded")
        return CheckResult("FAIL", "REDIS_PING_BAD", f"unexpected Redis ping response: {pong!r}")
    except Exception as exc:  # pragma: no cover - defensive by design
        return CheckResult("FAIL", "REDIS_CONNECT_FAILED", str(exc))


def _runtime_mode_check() -> CheckResult:
    runtime_mode = _env("SCALPX_RUNTIME_MODE", "paper")
    allowed = {"paper", "live", "replay"}
    if runtime_mode not in allowed:
        return CheckResult(
            "FAIL",
            "RUNTIME_MODE_INVALID",
            f"SCALPX_RUNTIME_MODE must be one of {sorted(allowed)}, got {runtime_mode!r}",
        )
    return CheckResult("PASS", "RUNTIME_MODE_OK", f"runtime_mode={runtime_mode}")


def _live_order_guard_check() -> CheckResult:
    runtime_mode = _env("SCALPX_RUNTIME_MODE", "paper")
    trading_enabled = _env_bool("SCALPX_TRADING_ENABLED", False)
    allow_live_orders = _env_bool("SCALPX_ALLOW_LIVE_ORDERS", False)

    if runtime_mode == "live" and not trading_enabled:
        return CheckResult(
            "WARN",
            "LIVE_TRADING_DISABLED",
            "runtime_mode=live but SCALPX_TRADING_ENABLED=0",
        )
    if runtime_mode == "live" and not allow_live_orders:
        return CheckResult(
            "WARN",
            "LIVE_ORDERS_DISABLED",
            "runtime_mode=live but SCALPX_ALLOW_LIVE_ORDERS=0",
        )
    return CheckResult(
        "PASS",
        "ORDER_GUARDS_OK",
        f"trading_enabled={int(trading_enabled)} allow_live_orders={int(allow_live_orders)}",
    )


def _login_requirement_check() -> CheckResult:
    require_valid_login = _env_bool("SCALPX_REQUIRE_VALID_LOGIN", False)
    token_file = _env("SCALPX_SESSION_TOKEN_FILE")
    creds_file = _env("SCALPX_BROKER_CREDENTIALS_FILE")

    if not require_valid_login:
        return CheckResult("PASS", "LOGIN_NOT_REQUIRED", "valid login not required by env")

    if not token_file and not creds_file:
        return CheckResult(
            "FAIL",
            "LOGIN_FILES_MISSING",
            "SCALPX_REQUIRE_VALID_LOGIN=1 but no token/credentials file paths are configured",
        )

    if token_file and Path(token_file).exists():
        return CheckResult("PASS", "LOGIN_TOKEN_PRESENT", f"{token_file} exists")
    if creds_file and Path(creds_file).exists():
        return CheckResult("PASS", "LOGIN_CREDS_PRESENT", f"{creds_file} exists")

    return CheckResult(
        "FAIL",
        "LOGIN_ARTIFACT_MISSING",
        "SCALPX_REQUIRE_VALID_LOGIN=1 but configured login artifacts do not exist",
    )


def run_checks() -> List[CheckResult]:
    results: List[CheckResult] = []

    # Required env presence
    required_envs = [
        "SCALPX_PROJECT_ROOT",
        "SCALPX_APP_ROOT",
        "SCALPX_LOG_DIR",
        "SCALPX_LOGGING_CONFIG",
        "SCALPX_SYMBOLS_FILE",
        "SCALPX_PARAMS_FILE",
        "SCALPX_RISK_LIMITS_FILE",
        "SCALPX_REDIS_HOST",
    ]
    for name in required_envs:
        try:
            value = _env_required(name)
            results.append(CheckResult("PASS", "ENV_OK", f"{name}={value}"))
        except Exception as exc:
            results.append(CheckResult("FAIL", "ENV_MISSING", str(exc)))

    # Paths
    results.append(_path_exists(_env("SCALPX_PROJECT_ROOT"), expect_dir=True))
    results.append(_path_exists(_env("SCALPX_APP_ROOT"), expect_dir=True))
    results.append(_path_writable_dir(_env("SCALPX_LOG_DIR")))
    results.append(_path_exists(_env("SCALPX_LOGGING_CONFIG"), expect_file=True))
    results.append(_path_exists(_env("SCALPX_SYMBOLS_FILE"), expect_file=True))
    results.append(_path_exists(_env("SCALPX_PARAMS_FILE"), expect_file=True))
    results.append(_path_exists(_env("SCALPX_RISK_LIMITS_FILE"), expect_file=True))

    runtime_config_file = _env("SCALPX_RUNTIME_CONFIG_FILE")
    if runtime_config_file:
        results.append(_path_exists(runtime_config_file, expect_file=True))
    else:
        results.append(CheckResult("WARN", "RUNTIME_CONFIG_UNSET", "SCALPX_RUNTIME_CONFIG_FILE is not set"))

    execution_config_file = _env("SCALPX_EXECUTION_CONFIG_FILE")
    if execution_config_file:
        results.append(_path_exists(execution_config_file, expect_file=True))
    else:
        results.append(CheckResult("WARN", "EXECUTION_CONFIG_UNSET", "SCALPX_EXECUTION_CONFIG_FILE is not set"))

    # Imports
    for module_name in (
        "mme_scalpx.main",
        "mme_scalpx.core.names",
        "mme_scalpx.core.redisx",
        "mme_scalpx.core.settings",
        "mme_scalpx.services.feeds",
        "mme_scalpx.services.features",
        "mme_scalpx.services.strategy",
        "mme_scalpx.services.execution",
        "mme_scalpx.services.risk",
        "mme_scalpx.services.monitor",
        "mme_scalpx.services.report",
        "mme_scalpx.domain.instruments",
        "mme_scalpx.integrations.login",
    ):
        results.append(_import_check(module_name))

    # Runtime policy sanity
    results.append(_runtime_mode_check())
    results.append(_live_order_guard_check())
    results.append(_login_requirement_check())

    # Redis
    results.append(_redis_ping_check())

    return results


def summarize(results: List[CheckResult]) -> int:
    fail_count = sum(1 for item in results if item.status == "FAIL")
    warn_count = sum(1 for item in results if item.status == "WARN")
    pass_count = sum(1 for item in results if item.status == "PASS")

    for item in results:
        print(f"{item.status:<4} | {item.code:<24} | {item.message}")

    print(
        f"SUMMARY | pass={pass_count} warn={warn_count} fail={fail_count} total={len(results)}"
    )
    return 1 if fail_count > 0 else 0


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run read-only preflight validation for ScalpX MME."
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as failures.",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    results = run_checks()

    if args.strict:
        results = [
            CheckResult("FAIL", item.code, item.message) if item.status == "WARN" else item
            for item in results
        ]

    return summarize(results)


if __name__ == "__main__":
    raise SystemExit(main())
