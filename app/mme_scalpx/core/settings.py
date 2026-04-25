"""
app/mme_scalpx/core/settings.py

Canonical runtime settings for ScalpX MME.

Purpose
-------
Single source of truth for:
- environment loading
- typed runtime configuration
- Redis connection and transport settings
- logging settings
- replay/live runtime settings
- fail-fast startup validation policy
- centralized service/runtime thresholds
- bootstrap-safe validated settings access

Ownership
---------
This module OWNS:
- configuration schema
- environment parsing
- validation of runtime configuration
- process-wide cached settings access
- safe redaction helpers for sensitive fields
- bootstrap logging setup

This module DOES NOT own:
- Redis names / contracts
- Redis client lifecycle
- clock implementation
- payload schemas / serialization
- trading logic
- broker APIs
- market calendars
- service transport ownership

Core design rules
-----------------
- One canonical settings object per process.
- All callers must use get_settings().
- No other module should maintain its own mutable config singleton.
- Validation failures must be explicit and early.
- Sensitive values must never be logged raw.
- Environment parsing must remain deterministic and dependency-light.
- Operational transport thresholds belong here, not in service modules.
- Cross-service runtime policy belongs here unless constitutionally frozen elsewhere.
- Logging bootstrap must be idempotent and safe for repeated initialization.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Final, Mapping
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from .validators import (
    normalize_optional_str,
    parse_bool,
    parse_choice,
    parse_float,
    parse_int,
    parse_path,
    require_existing_file,
    require_non_empty_str,
)

# ============================================================================
# Constants
# ============================================================================

DEFAULT_ENV_FILE: Final[str] = ".env"
DEFAULT_ENV_PREFIX: Final[str] = "MME_"

DEFAULT_APP_NAME: Final[str] = "ScalpX MME"
DEFAULT_RUNTIME_MODE: Final[str] = "live"
DEFAULT_APP_ENV: Final[str] = "dev"

DEFAULT_LOG_LEVEL: Final[str] = "INFO"
DEFAULT_LOG_FORMAT: Final[str] = "json"
DEFAULT_LOG_INCLUDE_PROCESS_ID: Final[bool] = True
DEFAULT_LOG_INCLUDE_THREAD_NAME: Final[bool] = True

DEFAULT_REDIS_URL: Final[str] = "redis://localhost:6379/0"
DEFAULT_REDIS_DECODE_RESPONSES: Final[bool] = True
DEFAULT_REDIS_RETRY_ON_TIMEOUT: Final[bool] = True
DEFAULT_REDIS_SOCKET_TIMEOUT_S: Final[float] = 2.0
DEFAULT_REDIS_SOCKET_CONNECT_TIMEOUT_S: Final[float] = 2.0
DEFAULT_REDIS_HEALTH_CHECK_INTERVAL_S: Final[int] = 15
DEFAULT_REDIS_MAX_CONNECTIONS: Final[int] = 100

DEFAULT_STREAM_MAXLEN_APPROX: Final[int] = 25_000
DEFAULT_XREAD_COUNT: Final[int] = 100
DEFAULT_XREAD_BLOCK_MS: Final[int] = 1_000

DEFAULT_REPLAY_SPEED: Final[float] = 1.0
DEFAULT_REPLAY_SLEEP_FLOOR_MS: Final[int] = 0
DEFAULT_REPLAY_STRICT_MONOTONICITY: Final[bool] = True

DEFAULT_HEARTBEAT_TTL_MS: Final[int] = 10_000
DEFAULT_LOCK_TTL_MS: Final[int] = 30_000
DEFAULT_LOCK_REFRESH_INTERVAL_MS: Final[int] = 10_000

# Cross-service centralized runtime policy.
# These belong here unless constitutionally frozen in names.py.
DEFAULT_STRATEGY_TARGET_PCT: Final[float] = 0.12
DEFAULT_STRATEGY_STOP_PCT: Final[float] = 0.07
DEFAULT_STRATEGY_PENDING_WAIT_MS: Final[int] = 2_500

DEFAULT_FEEDS_PUBLISH_COMPLETE_ONLY: Final[bool] = True
DEFAULT_FEEDS_MAX_FRAME_STALENESS_MS: Final[int] = 1_500

DEFAULT_REPORT_HISTORY_LIMIT: Final[int] = 50_000
DEFAULT_REPORT_INCLUDE_ENTRY_MODE: Final[bool] = True
DEFAULT_REPORT_ACK_LIMIT: Final[int] = 10_000
DEFAULT_REPORT_ORDER_LIMIT: Final[int] = 10_000
DEFAULT_REPORT_HEALTH_LIMIT: Final[int] = 5_000
DEFAULT_REPORT_ERROR_LIMIT: Final[int] = 5_000

DEFAULT_STARTUP_FAIL_FAST: Final[bool] = True
DEFAULT_STARTUP_REQUIRE_REDIS_PING: Final[bool] = True
DEFAULT_STARTUP_REQUIRE_RUNTIME_INSTRUMENTS: Final[bool] = True
DEFAULT_STARTUP_REQUIRE_LOGIN_HEALTH: Final[bool] = False

DEFAULT_MONITOR_POLL_INTERVAL_MS: Final[int] = 1_000
DEFAULT_MONITOR_HEALTH_PUBLISH_INTERVAL_MS: Final[int] = 5_000

DEFAULT_LOGIN_PUBLISH_HEALTH: Final[bool] = True
DEFAULT_LOGIN_HEALTH_PUBLISH_INTERVAL_MS: Final[int] = 5_000

DEFAULT_EXECUTION_IDLE_SLEEP_MS: Final[int] = 250
DEFAULT_EXECUTION_DECISION_BLOCK_MS: Final[int] = 1_000
DEFAULT_EXECUTION_LOCK_ACQUIRE_TIMEOUT_MS: Final[int] = 5_000

_ALLOWED_RUNTIME_MODES: Final[tuple[str, ...]] = ("live", "replay")
_ALLOWED_APP_ENVS: Final[tuple[str, ...]] = ("dev", "test", "staging", "prod")
_ALLOWED_LOG_LEVELS: Final[tuple[str, ...]] = (
    "CRITICAL",
    "ERROR",
    "WARNING",
    "INFO",
    "DEBUG",
)
_ALLOWED_LOG_FORMATS: Final[tuple[str, ...]] = ("json", "text")

# ============================================================================
# Exceptions
# ============================================================================


class SettingsError(ValueError):
    """Raised when configuration is invalid or cannot be loaded."""


# ============================================================================
# Local wrappers around shared validators
# Keeps SettingsError as the module-facing exception contract.
# ============================================================================


def _wrap_validation(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as exc:  # pragma: no cover - preserves module contract
        if isinstance(exc, SettingsError):
            raise
        raise SettingsError(str(exc)) from exc


def _require_non_empty_str(value: str, *, field_name: str) -> str:
    return _wrap_validation(require_non_empty_str, value, field_name=field_name)


def _normalize_optional_str(value: str | None) -> str | None:
    return _wrap_validation(normalize_optional_str, value)


def _parse_bool(raw: str | None, *, field_name: str, default: bool) -> bool:
    return _wrap_validation(parse_bool, raw, field_name=field_name, default=default)


def _parse_int(
    raw: str | None,
    *,
    field_name: str,
    default: int,
    minimum: int | None = None,
) -> int:
    return _wrap_validation(
        parse_int,
        raw,
        field_name=field_name,
        default=default,
        min_value=minimum,
    )


def _parse_float(
    raw: str | None,
    *,
    field_name: str,
    default: float,
    minimum: float | None = None,
    strictly_positive: bool = False,
) -> float:
    return _wrap_validation(
        parse_float,
        raw,
        field_name=field_name,
        default=default,
        min_value=minimum,
        strictly_positive=strictly_positive,
    )


def _parse_choice(
    raw: str | None,
    *,
    field_name: str,
    default: str,
    allowed: tuple[str, ...],
    casefold: bool = True,
) -> str:
    return _wrap_validation(
        parse_choice,
        raw,
        field_name=field_name,
        allowed=allowed,
        default=default,
        casefold=casefold,
    )


def _parse_path(raw: str | None, *, field_name: str) -> Path | None:
    return _wrap_validation(parse_path, raw, field_name=field_name)


def _require_existing_file(path: Path, *, field_name: str) -> Path:
    return _wrap_validation(require_existing_file, path, field_name=field_name)


# ============================================================================
# Helper utilities
# ============================================================================


def _mask_url_secrets(url: str) -> str:
    """
    Redact sensitive URL components for safe logging.

    Masks:
    - password in userinfo
    - password/token-like query values if present
    """
    parsed = urlsplit(url)
    username = parsed.username
    password = parsed.password
    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port is not None else ""

    if username is not None:
        userinfo = username
        if password is not None:
            userinfo += ":***"
        netloc = f"{userinfo}@{hostname}{port}"
    else:
        netloc = hostname + port

    query_pairs = parse_qsl(parsed.query, keep_blank_values=True)
    if query_pairs:
        safe_pairs: list[tuple[str, str]] = []
        for key, value in query_pairs:
            if key.lower() in {"password", "passwd", "pwd", "token", "secret"}:
                safe_pairs.append((key, "***"))
            else:
                safe_pairs.append((key, value))
        query = urlencode(safe_pairs, doseq=True)
    else:
        query = parsed.query

    return urlunsplit((parsed.scheme, netloc, parsed.path, query, parsed.fragment))


def _read_env_file(path: Path) -> dict[str, str]:
    """
    Minimal .env reader.

    Supported line forms:
        KEY=value
        export KEY=value

    Notes
    -----
    - No variable interpolation.
    - Surrounding single/double quotes are stripped if balanced.
    - Blank lines and comment lines are ignored.
    """
    if not path.exists():
        return {}

    if not path.is_file():
        raise SettingsError(f"Environment file path is not a file: {path}")

    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SettingsError(f"Failed to read environment file {path}: {exc}") from exc

    loaded: dict[str, str] = {}

    for lineno, raw_line in enumerate(content.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("export "):
            line = line[len("export ") :].strip()

        if "=" not in line:
            raise SettingsError(
                f"Invalid line in environment file {path} at line {lineno}: {raw_line!r}"
            )

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if not key:
            raise SettingsError(
                f"Invalid empty key in environment file {path} at line {lineno}"
            )

        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]

        loaded[key] = value

    return loaded


def _resolve_env_file(
    env_file: str | Path | None,
    environ: Mapping[str, str],
) -> Path:
    """
    Resolve the env file path.

    Priority:
    1. explicit env_file argument
    2. MME_CONFIG_PATH environment variable
    3. default .env
    """
    if env_file is not None:
        candidate = Path(env_file)
    else:
        config_path = environ.get(f"{DEFAULT_ENV_PREFIX}CONFIG_PATH")
        candidate = Path(config_path) if config_path else Path(DEFAULT_ENV_FILE)

    return candidate.expanduser()


def _build_env(
    *,
    env_file: str | Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> dict[str, str]:
    source_environ = os.environ if environ is None else environ
    resolved_env_file = _resolve_env_file(env_file=env_file, environ=source_environ)

    merged: dict[str, str] = {}
    merged.update(_read_env_file(resolved_env_file))

    for key, value in source_environ.items():
        if isinstance(key, str) and isinstance(value, str):
            merged[key] = value

    return merged


def _env_get(env: Mapping[str, str], suffix: str) -> str | None:
    return env.get(f"{DEFAULT_ENV_PREFIX}{suffix}")


def _utc_iso_now() -> str:
    return datetime.now(tz=timezone.utc).isoformat(timespec="milliseconds")



# ============================================================================
# Runtime truth introspection helpers
# ============================================================================
#
# Batch 3 deliberately does not change runtime_mode behavior. settings.py still
# accepts its current low-level runtime choices until main.py composition audit
# decides the final effective runtime owner. These helpers make the mismatch
# explicit and auditable.

def env_get_any(
    env: Mapping[str, str],
    suffix: str,
    *,
    prefixes: tuple[str, ...] = (DEFAULT_ENV_PREFIX, "SCALPX_"),
) -> str | None:
    """Read an environment suffix from accepted operational prefixes."""
    for prefix in prefixes:
        value = env.get(f"{prefix}{suffix}")
        if value is not None:
            return value
    return None


def runtime_mode_input_snapshot(env: Mapping[str, str]) -> dict[str, str | None]:
    """Return all known runtime-mode inputs without deciding effective mode."""
    return {
        "MME_RUNTIME_MODE": env.get("MME_RUNTIME_MODE"),
        "SCALPX_RUNTIME_MODE": env.get("SCALPX_RUNTIME_MODE"),
        "settings_allowed_runtime_modes": ",".join(_ALLOWED_RUNTIME_MODES),
        "settings_default_runtime_mode": DEFAULT_RUNTIME_MODE,
    }


def validate_runtime_mode_input_snapshot(env: Mapping[str, str]) -> dict[str, str | None]:
    """Validate runtime-mode input surface for proof bundles.

    This is intentionally observational. It does not reinterpret paper mode or
    SCALPX_* into settings.runtime.runtime_mode before the main.py audit.
    """
    snapshot = runtime_mode_input_snapshot(env)
    for key in ("MME_RUNTIME_MODE", "SCALPX_RUNTIME_MODE"):
        value = snapshot.get(key)
        if value is not None and not str(value).strip():
            raise SettingsError(f"{key} cannot be blank when provided")
    return snapshot


# ============================================================================
# Settings models
# ============================================================================


@dataclass(frozen=True, slots=True)
class RuntimeSettings:
    runtime_mode: str
    replay_speed: float
    replay_sleep_floor_ms: int
    replay_strict_monotonicity: bool
    heartbeat_ttl_ms: int
    lock_ttl_ms: int
    lock_refresh_interval_ms: int

    def __post_init__(self) -> None:
        if self.runtime_mode not in _ALLOWED_RUNTIME_MODES:
            raise SettingsError(
                f"runtime_mode must be one of {_ALLOWED_RUNTIME_MODES}, got {self.runtime_mode!r}"
            )
        if self.replay_speed <= 0:
            raise SettingsError(f"replay_speed must be > 0, got {self.replay_speed}")
        if self.replay_sleep_floor_ms < 0:
            raise SettingsError(
                f"replay_sleep_floor_ms must be >= 0, got {self.replay_sleep_floor_ms}"
            )
        if self.heartbeat_ttl_ms <= 0:
            raise SettingsError(
                f"heartbeat_ttl_ms must be > 0, got {self.heartbeat_ttl_ms}"
            )
        if self.lock_ttl_ms <= 0:
            raise SettingsError(f"lock_ttl_ms must be > 0, got {self.lock_ttl_ms}")
        if self.lock_refresh_interval_ms <= 0:
            raise SettingsError(
                "lock_refresh_interval_ms must be > 0, "
                f"got {self.lock_refresh_interval_ms}"
            )
        if self.lock_refresh_interval_ms >= self.lock_ttl_ms:
            raise SettingsError(
                "lock_refresh_interval_ms must be smaller than lock_ttl_ms "
                f"(got refresh={self.lock_refresh_interval_ms}, ttl={self.lock_ttl_ms})"
            )

    @property
    def is_live(self) -> bool:
        return self.runtime_mode == "live"

    @property
    def is_replay(self) -> bool:
        return self.runtime_mode == "replay"


@dataclass(frozen=True, slots=True)
class RedisSettings:
    url: str
    password: str | None
    socket_timeout_s: float
    socket_connect_timeout_s: float
    health_check_interval_s: int
    decode_responses: bool
    retry_on_timeout: bool
    ssl_ca_path: Path | None
    max_connections: int
    client_name: str
    stream_maxlen_approx: int
    xread_count: int
    xread_block_ms: int

    def __post_init__(self) -> None:
        _require_non_empty_str(self.url, field_name="redis.url")
        _require_non_empty_str(self.client_name, field_name="redis.client_name")

        if self.socket_timeout_s <= 0:
            raise SettingsError(
                f"redis.socket_timeout_s must be > 0, got {self.socket_timeout_s}"
            )
        if self.socket_connect_timeout_s <= 0:
            raise SettingsError(
                "redis.socket_connect_timeout_s must be > 0, "
                f"got {self.socket_connect_timeout_s}"
            )
        if self.health_check_interval_s < 0:
            raise SettingsError(
                "redis.health_check_interval_s must be >= 0, "
                f"got {self.health_check_interval_s}"
            )
        if self.max_connections <= 0:
            raise SettingsError(
                f"redis.max_connections must be > 0, got {self.max_connections}"
            )
        if self.stream_maxlen_approx <= 0:
            raise SettingsError(
                "redis.stream_maxlen_approx must be > 0, "
                f"got {self.stream_maxlen_approx}"
            )
        if self.xread_count <= 0:
            raise SettingsError(
                f"redis.xread_count must be > 0, got {self.xread_count}"
            )
        if self.xread_block_ms < 0:
            raise SettingsError(
                f"redis.xread_block_ms must be >= 0, got {self.xread_block_ms}"
            )

    @property
    def masked_url(self) -> str:
        return _mask_url_secrets(self.url)

    @property
    def uses_tls(self) -> bool:
        return self.url.lower().startswith("rediss://")


@dataclass(frozen=True, slots=True)
class LoggingSettings:
    level: str
    fmt: str
    json_indent: int | None
    include_process_id: bool
    include_thread_name: bool

    def __post_init__(self) -> None:
        if self.level not in _ALLOWED_LOG_LEVELS:
            raise SettingsError(
                f"logging.level must be one of {_ALLOWED_LOG_LEVELS}, got {self.level!r}"
            )
        if self.fmt not in _ALLOWED_LOG_FORMATS:
            raise SettingsError(
                f"logging.fmt must be one of {_ALLOWED_LOG_FORMATS}, got {self.fmt!r}"
            )
        if self.json_indent is not None and self.json_indent < 0:
            raise SettingsError(
                f"logging.json_indent must be >= 0, got {self.json_indent}"
            )


@dataclass(frozen=True, slots=True)
class StrategySettings:
    target_pct: float
    stop_pct: float
    pending_wait_ms: int

    def __post_init__(self) -> None:
        if self.target_pct <= 0:
            raise SettingsError(
                f"strategy.target_pct must be > 0, got {self.target_pct}"
            )
        if self.stop_pct <= 0:
            raise SettingsError(f"strategy.stop_pct must be > 0, got {self.stop_pct}")
        if self.target_pct <= self.stop_pct:
            raise SettingsError(
                "strategy.target_pct must be greater than strategy.stop_pct "
                f"(got target={self.target_pct}, stop={self.stop_pct})"
            )
        if self.pending_wait_ms < 0:
            raise SettingsError(
                f"strategy.pending_wait_ms must be >= 0, got {self.pending_wait_ms}"
            )


@dataclass(frozen=True, slots=True)
class FeedsSettings:
    publish_snapshots_only_when_complete: bool
    max_frame_staleness_ms: int

    def __post_init__(self) -> None:
        if self.max_frame_staleness_ms < 0:
            raise SettingsError(
                "feeds.max_frame_staleness_ms must be >= 0, "
                f"got {self.max_frame_staleness_ms}"
            )


@dataclass(frozen=True, slots=True)
class ReportSettings:
    history_limit: int
    include_entry_mode: bool
    ack_limit: int
    order_limit: int
    health_limit: int
    error_limit: int

    def __post_init__(self) -> None:
        if self.history_limit <= 0:
            raise SettingsError(
                f"report.history_limit must be > 0, got {self.history_limit}"
            )
        if self.ack_limit <= 0:
            raise SettingsError(f"report.ack_limit must be > 0, got {self.ack_limit}")
        if self.order_limit <= 0:
            raise SettingsError(
                f"report.order_limit must be > 0, got {self.order_limit}"
            )
        if self.health_limit <= 0:
            raise SettingsError(
                f"report.health_limit must be > 0, got {self.health_limit}"
            )
        if self.error_limit <= 0:
            raise SettingsError(
                f"report.error_limit must be > 0, got {self.error_limit}"
            )


@dataclass(frozen=True, slots=True)
class StartupSettings:
    fail_fast: bool
    require_redis_ping: bool
    require_runtime_instruments: bool
    require_login_health: bool


@dataclass(frozen=True, slots=True)
class MonitorSettings:
    poll_interval_ms: int
    health_publish_interval_ms: int

    def __post_init__(self) -> None:
        if self.poll_interval_ms <= 0:
            raise SettingsError(
                f"monitor.poll_interval_ms must be > 0, got {self.poll_interval_ms}"
            )
        if self.health_publish_interval_ms <= 0:
            raise SettingsError(
                "monitor.health_publish_interval_ms must be > 0, "
                f"got {self.health_publish_interval_ms}"
            )


@dataclass(frozen=True, slots=True)
class LoginSettings:
    publish_health: bool
    health_publish_interval_ms: int

    def __post_init__(self) -> None:
        if self.health_publish_interval_ms <= 0:
            raise SettingsError(
                "login.health_publish_interval_ms must be > 0, "
                f"got {self.health_publish_interval_ms}"
            )


@dataclass(frozen=True, slots=True)
class ExecutionSettings:
    idle_sleep_ms: int
    decision_block_ms: int
    lock_acquire_timeout_ms: int

    def __post_init__(self) -> None:
        if self.idle_sleep_ms < 0:
            raise SettingsError(
                f"execution.idle_sleep_ms must be >= 0, got {self.idle_sleep_ms}"
            )
        if self.decision_block_ms < 0:
            raise SettingsError(
                f"execution.decision_block_ms must be >= 0, got {self.decision_block_ms}"
            )
        if self.lock_acquire_timeout_ms <= 0:
            raise SettingsError(
                "execution.lock_acquire_timeout_ms must be > 0, "
                f"got {self.lock_acquire_timeout_ms}"
            )


@dataclass(frozen=True, slots=True)
class AppSettings:
    app_name: str
    app_env: str
    runtime: RuntimeSettings
    redis: RedisSettings
    logging: LoggingSettings
    strategy: StrategySettings
    feeds: FeedsSettings
    report: ReportSettings
    startup: StartupSettings
    monitor: MonitorSettings
    login: LoginSettings
    execution: ExecutionSettings

    def __post_init__(self) -> None:
        _require_non_empty_str(self.app_name, field_name="app_name")
        if self.app_env not in _ALLOWED_APP_ENVS:
            raise SettingsError(
                f"app_env must be one of {_ALLOWED_APP_ENVS}, got {self.app_env!r}"
            )

    @property
    def is_dev(self) -> bool:
        return self.app_env == "dev"

    @property
    def is_test(self) -> bool:
        return self.app_env == "test"

    @property
    def is_staging(self) -> bool:
        return self.app_env == "staging"

    @property
    def is_prod(self) -> bool:
        return self.app_env == "prod"

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "app_name": self.app_name,
            "app_env": self.app_env,
            "runtime": asdict(self.runtime),
            "redis": {
                "url": self.redis.masked_url,
                "password": "***" if self.redis.password else None,
                "socket_timeout_s": self.redis.socket_timeout_s,
                "socket_connect_timeout_s": self.redis.socket_connect_timeout_s,
                "health_check_interval_s": self.redis.health_check_interval_s,
                "decode_responses": self.redis.decode_responses,
                "retry_on_timeout": self.redis.retry_on_timeout,
                "ssl_ca_path": (
                    str(self.redis.ssl_ca_path) if self.redis.ssl_ca_path else None
                ),
                "max_connections": self.redis.max_connections,
                "client_name": self.redis.client_name,
                "stream_maxlen_approx": self.redis.stream_maxlen_approx,
                "xread_count": self.redis.xread_count,
                "xread_block_ms": self.redis.xread_block_ms,
                "uses_tls": self.redis.uses_tls,
            },
            "logging": asdict(self.logging),
            "strategy": asdict(self.strategy),
            "feeds": asdict(self.feeds),
            "report": asdict(self.report),
            "startup": asdict(self.startup),
            "monitor": asdict(self.monitor),
            "login": asdict(self.login),
            "execution": asdict(self.execution),
        }


# ============================================================================
# Builders
# ============================================================================


def build_runtime_settings(env: Mapping[str, str]) -> RuntimeSettings:
    runtime_mode = _parse_choice(
        _env_get(env, "RUNTIME_MODE"),
        field_name="MME_RUNTIME_MODE",
        default=DEFAULT_RUNTIME_MODE,
        allowed=_ALLOWED_RUNTIME_MODES,
    )
    replay_speed = _parse_float(
        _env_get(env, "REPLAY_SPEED"),
        field_name="MME_REPLAY_SPEED",
        default=DEFAULT_REPLAY_SPEED,
        strictly_positive=True,
    )
    replay_sleep_floor_ms = _parse_int(
        _env_get(env, "REPLAY_SLEEP_FLOOR_MS"),
        field_name="MME_REPLAY_SLEEP_FLOOR_MS",
        default=DEFAULT_REPLAY_SLEEP_FLOOR_MS,
        minimum=0,
    )
    replay_strict_monotonicity = _parse_bool(
        _env_get(env, "REPLAY_STRICT_MONOTONICITY"),
        field_name="MME_REPLAY_STRICT_MONOTONICITY",
        default=DEFAULT_REPLAY_STRICT_MONOTONICITY,
    )
    heartbeat_ttl_ms = _parse_int(
        _env_get(env, "HEARTBEAT_TTL_MS"),
        field_name="MME_HEARTBEAT_TTL_MS",
        default=DEFAULT_HEARTBEAT_TTL_MS,
        minimum=1,
    )
    lock_ttl_ms = _parse_int(
        _env_get(env, "LOCK_TTL_MS"),
        field_name="MME_LOCK_TTL_MS",
        default=DEFAULT_LOCK_TTL_MS,
        minimum=1,
    )
    lock_refresh_interval_ms = _parse_int(
        _env_get(env, "LOCK_REFRESH_INTERVAL_MS"),
        field_name="MME_LOCK_REFRESH_INTERVAL_MS",
        default=DEFAULT_LOCK_REFRESH_INTERVAL_MS,
        minimum=1,
    )

    return RuntimeSettings(
        runtime_mode=runtime_mode,
        replay_speed=replay_speed,
        replay_sleep_floor_ms=replay_sleep_floor_ms,
        replay_strict_monotonicity=replay_strict_monotonicity,
        heartbeat_ttl_ms=heartbeat_ttl_ms,
        lock_ttl_ms=lock_ttl_ms,
        lock_refresh_interval_ms=lock_refresh_interval_ms,
    )


def build_redis_settings(
    env: Mapping[str, str],
    *,
    app_name: str,
    app_env: str,
    runtime: RuntimeSettings,
) -> RedisSettings:
    del app_env
    del runtime

    redis_url = _require_non_empty_str(
        _env_get(env, "REDIS_URL") or DEFAULT_REDIS_URL,
        field_name="MME_REDIS_URL",
    )
    password = _normalize_optional_str(_env_get(env, "REDIS_PASSWORD"))
    socket_timeout_s = _parse_float(
        _env_get(env, "REDIS_SOCKET_TIMEOUT_S"),
        field_name="MME_REDIS_SOCKET_TIMEOUT_S",
        default=DEFAULT_REDIS_SOCKET_TIMEOUT_S,
        strictly_positive=True,
    )
    socket_connect_timeout_s = _parse_float(
        _env_get(env, "REDIS_SOCKET_CONNECT_TIMEOUT_S"),
        field_name="MME_REDIS_SOCKET_CONNECT_TIMEOUT_S",
        default=DEFAULT_REDIS_SOCKET_CONNECT_TIMEOUT_S,
        strictly_positive=True,
    )
    health_check_interval_s = _parse_int(
        _env_get(env, "REDIS_HEALTH_CHECK_INTERVAL_S"),
        field_name="MME_REDIS_HEALTH_CHECK_INTERVAL_S",
        default=DEFAULT_REDIS_HEALTH_CHECK_INTERVAL_S,
        minimum=0,
    )
    decode_responses = _parse_bool(
        _env_get(env, "REDIS_DECODE_RESPONSES"),
        field_name="MME_REDIS_DECODE_RESPONSES",
        default=DEFAULT_REDIS_DECODE_RESPONSES,
    )
    retry_on_timeout = _parse_bool(
        _env_get(env, "REDIS_RETRY_ON_TIMEOUT"),
        field_name="MME_REDIS_RETRY_ON_TIMEOUT",
        default=DEFAULT_REDIS_RETRY_ON_TIMEOUT,
    )
    ssl_ca_path = _parse_path(
        _env_get(env, "REDIS_SSL_CA_PATH"),
        field_name="MME_REDIS_SSL_CA_PATH",
    )
    max_connections = _parse_int(
        _env_get(env, "REDIS_MAX_CONNECTIONS"),
        field_name="MME_REDIS_MAX_CONNECTIONS",
        default=DEFAULT_REDIS_MAX_CONNECTIONS,
        minimum=1,
    )
    stream_maxlen_approx = _parse_int(
        _env_get(env, "STREAM_MAXLEN_APPROX"),
        field_name="MME_STREAM_MAXLEN_APPROX",
        default=DEFAULT_STREAM_MAXLEN_APPROX,
        minimum=1,
    )
    xread_count = _parse_int(
        _env_get(env, "XREAD_COUNT"),
        field_name="MME_XREAD_COUNT",
        default=DEFAULT_XREAD_COUNT,
        minimum=1,
    )
    xread_block_ms = _parse_int(
        _env_get(env, "XREAD_BLOCK_MS"),
        field_name="MME_XREAD_BLOCK_MS",
        default=DEFAULT_XREAD_BLOCK_MS,
        minimum=0,
    )

    client_name = _require_non_empty_str(
        _env_get(env, "REDIS_CLIENT_NAME") or app_name.lower().replace(" ", "-"),
        field_name="MME_REDIS_CLIENT_NAME",
    )

    return RedisSettings(
        url=redis_url,
        password=password,
        socket_timeout_s=socket_timeout_s,
        socket_connect_timeout_s=socket_connect_timeout_s,
        health_check_interval_s=health_check_interval_s,
        decode_responses=decode_responses,
        retry_on_timeout=retry_on_timeout,
        ssl_ca_path=ssl_ca_path,
        max_connections=max_connections,
        client_name=client_name,
        stream_maxlen_approx=stream_maxlen_approx,
        xread_count=xread_count,
        xread_block_ms=xread_block_ms,
    )


def build_logging_settings(env: Mapping[str, str]) -> LoggingSettings:
    level = _parse_choice(
        _env_get(env, "LOG_LEVEL"),
        field_name="MME_LOG_LEVEL",
        default=DEFAULT_LOG_LEVEL,
        allowed=_ALLOWED_LOG_LEVELS,
    )
    fmt = _parse_choice(
        _env_get(env, "LOG_FORMAT"),
        field_name="MME_LOG_FORMAT",
        default=DEFAULT_LOG_FORMAT,
        allowed=_ALLOWED_LOG_FORMATS,
    )

    json_indent_raw = _env_get(env, "LOG_JSON_INDENT")
    json_indent = (
        None
        if _normalize_optional_str(json_indent_raw) is None
        else _parse_int(
            json_indent_raw,
            field_name="MME_LOG_JSON_INDENT",
            default=0,
            minimum=0,
        )
    )

    include_process_id = _parse_bool(
        _env_get(env, "LOG_INCLUDE_PROCESS_ID"),
        field_name="MME_LOG_INCLUDE_PROCESS_ID",
        default=DEFAULT_LOG_INCLUDE_PROCESS_ID,
    )
    include_thread_name = _parse_bool(
        _env_get(env, "LOG_INCLUDE_THREAD_NAME"),
        field_name="MME_LOG_INCLUDE_THREAD_NAME",
        default=DEFAULT_LOG_INCLUDE_THREAD_NAME,
    )

    return LoggingSettings(
        level=level,
        fmt=fmt,
        json_indent=json_indent,
        include_process_id=include_process_id,
        include_thread_name=include_thread_name,
    )


def build_strategy_settings(env: Mapping[str, str]) -> StrategySettings:
    return StrategySettings(
        target_pct=_parse_float(
            _env_get(env, "STRATEGY_TARGET_PCT"),
            field_name="MME_STRATEGY_TARGET_PCT",
            default=DEFAULT_STRATEGY_TARGET_PCT,
            strictly_positive=True,
        ),
        stop_pct=_parse_float(
            _env_get(env, "STRATEGY_STOP_PCT"),
            field_name="MME_STRATEGY_STOP_PCT",
            default=DEFAULT_STRATEGY_STOP_PCT,
            strictly_positive=True,
        ),
        pending_wait_ms=_parse_int(
            _env_get(env, "STRATEGY_PENDING_WAIT_MS"),
            field_name="MME_STRATEGY_PENDING_WAIT_MS",
            default=DEFAULT_STRATEGY_PENDING_WAIT_MS,
            minimum=0,
        ),
    )


def build_feeds_settings(env: Mapping[str, str]) -> FeedsSettings:
    return FeedsSettings(
        publish_snapshots_only_when_complete=_parse_bool(
            _env_get(env, "FEEDS_PUBLISH_SNAPSHOTS_ONLY_WHEN_COMPLETE"),
            field_name="MME_FEEDS_PUBLISH_SNAPSHOTS_ONLY_WHEN_COMPLETE",
            default=DEFAULT_FEEDS_PUBLISH_COMPLETE_ONLY,
        ),
        max_frame_staleness_ms=_parse_int(
            _env_get(env, "FEEDS_MAX_FRAME_STALENESS_MS"),
            field_name="MME_FEEDS_MAX_FRAME_STALENESS_MS",
            default=DEFAULT_FEEDS_MAX_FRAME_STALENESS_MS,
            minimum=0,
        ),
    )


def build_report_settings(env: Mapping[str, str]) -> ReportSettings:
    return ReportSettings(
        history_limit=_parse_int(
            _env_get(env, "REPORT_HISTORY_LIMIT"),
            field_name="MME_REPORT_HISTORY_LIMIT",
            default=DEFAULT_REPORT_HISTORY_LIMIT,
            minimum=1,
        ),
        include_entry_mode=_parse_bool(
            _env_get(env, "REPORT_INCLUDE_ENTRY_MODE"),
            field_name="MME_REPORT_INCLUDE_ENTRY_MODE",
            default=DEFAULT_REPORT_INCLUDE_ENTRY_MODE,
        ),
        ack_limit=_parse_int(
            _env_get(env, "REPORT_ACK_LIMIT"),
            field_name="MME_REPORT_ACK_LIMIT",
            default=DEFAULT_REPORT_ACK_LIMIT,
            minimum=1,
        ),
        order_limit=_parse_int(
            _env_get(env, "REPORT_ORDER_LIMIT"),
            field_name="MME_REPORT_ORDER_LIMIT",
            default=DEFAULT_REPORT_ORDER_LIMIT,
            minimum=1,
        ),
        health_limit=_parse_int(
            _env_get(env, "REPORT_HEALTH_LIMIT"),
            field_name="MME_REPORT_HEALTH_LIMIT",
            default=DEFAULT_REPORT_HEALTH_LIMIT,
            minimum=1,
        ),
        error_limit=_parse_int(
            _env_get(env, "REPORT_ERROR_LIMIT"),
            field_name="MME_REPORT_ERROR_LIMIT",
            default=DEFAULT_REPORT_ERROR_LIMIT,
            minimum=1,
        ),
    )


def build_startup_settings(env: Mapping[str, str]) -> StartupSettings:
    return StartupSettings(
        fail_fast=_parse_bool(
            _env_get(env, "STARTUP_FAIL_FAST"),
            field_name="MME_STARTUP_FAIL_FAST",
            default=DEFAULT_STARTUP_FAIL_FAST,
        ),
        require_redis_ping=_parse_bool(
            _env_get(env, "STARTUP_REQUIRE_REDIS_PING"),
            field_name="MME_STARTUP_REQUIRE_REDIS_PING",
            default=DEFAULT_STARTUP_REQUIRE_REDIS_PING,
        ),
        require_runtime_instruments=_parse_bool(
            _env_get(env, "STARTUP_REQUIRE_RUNTIME_INSTRUMENTS"),
            field_name="MME_STARTUP_REQUIRE_RUNTIME_INSTRUMENTS",
            default=DEFAULT_STARTUP_REQUIRE_RUNTIME_INSTRUMENTS,
        ),
        require_login_health=_parse_bool(
            _env_get(env, "STARTUP_REQUIRE_LOGIN_HEALTH"),
            field_name="MME_STARTUP_REQUIRE_LOGIN_HEALTH",
            default=DEFAULT_STARTUP_REQUIRE_LOGIN_HEALTH,
        ),
    )


def build_monitor_settings(env: Mapping[str, str]) -> MonitorSettings:
    return MonitorSettings(
        poll_interval_ms=_parse_int(
            _env_get(env, "MONITOR_POLL_INTERVAL_MS"),
            field_name="MME_MONITOR_POLL_INTERVAL_MS",
            default=DEFAULT_MONITOR_POLL_INTERVAL_MS,
            minimum=1,
        ),
        health_publish_interval_ms=_parse_int(
            _env_get(env, "MONITOR_HEALTH_PUBLISH_INTERVAL_MS"),
            field_name="MME_MONITOR_HEALTH_PUBLISH_INTERVAL_MS",
            default=DEFAULT_MONITOR_HEALTH_PUBLISH_INTERVAL_MS,
            minimum=1,
        ),
    )


def build_login_settings(env: Mapping[str, str]) -> LoginSettings:
    return LoginSettings(
        publish_health=_parse_bool(
            _env_get(env, "LOGIN_PUBLISH_HEALTH"),
            field_name="MME_LOGIN_PUBLISH_HEALTH",
            default=DEFAULT_LOGIN_PUBLISH_HEALTH,
        ),
        health_publish_interval_ms=_parse_int(
            _env_get(env, "LOGIN_HEALTH_PUBLISH_INTERVAL_MS"),
            field_name="MME_LOGIN_HEALTH_PUBLISH_INTERVAL_MS",
            default=DEFAULT_LOGIN_HEALTH_PUBLISH_INTERVAL_MS,
            minimum=1,
        ),
    )


def build_execution_settings(env: Mapping[str, str]) -> ExecutionSettings:
    return ExecutionSettings(
        idle_sleep_ms=_parse_int(
            _env_get(env, "EXECUTION_IDLE_SLEEP_MS"),
            field_name="MME_EXECUTION_IDLE_SLEEP_MS",
            default=DEFAULT_EXECUTION_IDLE_SLEEP_MS,
            minimum=0,
        ),
        decision_block_ms=_parse_int(
            _env_get(env, "EXECUTION_DECISION_BLOCK_MS"),
            field_name="MME_EXECUTION_DECISION_BLOCK_MS",
            default=DEFAULT_EXECUTION_DECISION_BLOCK_MS,
            minimum=0,
        ),
        lock_acquire_timeout_ms=_parse_int(
            _env_get(env, "EXECUTION_LOCK_ACQUIRE_TIMEOUT_MS"),
            field_name="MME_EXECUTION_LOCK_ACQUIRE_TIMEOUT_MS",
            default=DEFAULT_EXECUTION_LOCK_ACQUIRE_TIMEOUT_MS,
            minimum=1,
        ),
    )


def validate_settings(settings: AppSettings) -> None:
    """
    Run cross-field validation after all sections are built.
    """
    _require_non_empty_str(settings.app_name, field_name="app_name")

    if settings.app_env not in _ALLOWED_APP_ENVS:
        raise SettingsError(
            f"Invalid app_env {settings.app_env!r}; must be one of {_ALLOWED_APP_ENVS}"
        )

    if settings.runtime.is_live and settings.runtime.replay_speed != DEFAULT_REPLAY_SPEED:
        raise SettingsError(
            "replay_speed must remain at default in live mode "
            f"(got {settings.runtime.replay_speed})"
        )

    if settings.runtime.is_live and settings.runtime.replay_sleep_floor_ms != 0:
        raise SettingsError(
            "replay_sleep_floor_ms must be 0 in live mode "
            f"(got {settings.runtime.replay_sleep_floor_ms})"
        )

    if settings.runtime.is_live and not settings.startup.fail_fast:
        raise SettingsError("startup.fail_fast must remain enabled in live mode")

    if settings.redis.uses_tls and settings.redis.ssl_ca_path is not None:
        _require_existing_file(
            settings.redis.ssl_ca_path,
            field_name="MME_REDIS_SSL_CA_PATH",
        )

    if (
        settings.runtime.heartbeat_ttl_ms >= settings.runtime.lock_ttl_ms
        and settings.runtime.is_live
    ):
        raise SettingsError(
            "heartbeat_ttl_ms should be smaller than lock_ttl_ms in live mode "
            f"(got heartbeat_ttl_ms={settings.runtime.heartbeat_ttl_ms}, "
            f"lock_ttl_ms={settings.runtime.lock_ttl_ms})"
        )

    if settings.execution.decision_block_ms > settings.redis.xread_block_ms:
        raise SettingsError(
            "execution.decision_block_ms must be <= redis.xread_block_ms "
            f"(got execution={settings.execution.decision_block_ms}, "
            f"redis={settings.redis.xread_block_ms})"
        )


def build_settings(
    *,
    env_file: str | Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> AppSettings:
    """
    Build a validated AppSettings object.

    This function does not cache. Most callers should use get_settings().
    """
    env = _build_env(env_file=env_file, environ=environ)

    app_name = _require_non_empty_str(
        _env_get(env, "APP_NAME") or DEFAULT_APP_NAME,
        field_name="MME_APP_NAME",
    )
    app_env = _parse_choice(
        _env_get(env, "APP_ENV"),
        field_name="MME_APP_ENV",
        default=DEFAULT_APP_ENV,
        allowed=_ALLOWED_APP_ENVS,
    )

    runtime = build_runtime_settings(env)
    redis = build_redis_settings(
        env,
        app_name=app_name,
        app_env=app_env,
        runtime=runtime,
    )
    logging_settings = build_logging_settings(env)
    strategy_settings = build_strategy_settings(env)
    feeds_settings = build_feeds_settings(env)
    report_settings = build_report_settings(env)
    startup_settings = build_startup_settings(env)
    monitor_settings = build_monitor_settings(env)
    login_settings = build_login_settings(env)
    execution_settings = build_execution_settings(env)

    settings = AppSettings(
        app_name=app_name,
        app_env=app_env,
        runtime=runtime,
        redis=redis,
        logging=logging_settings,
        strategy=strategy_settings,
        feeds=feeds_settings,
        report=report_settings,
        startup=startup_settings,
        monitor=monitor_settings,
        login=login_settings,
        execution=execution_settings,
    )
    validate_settings(settings)
    return settings


# ============================================================================
# Logging bootstrap
# ============================================================================


class _JsonFormatter(logging.Formatter):
    """
    Minimal stdlib-only JSON formatter.
    """

    def __init__(
        self,
        *,
        include_process_id: bool,
        include_thread_name: bool,
        indent: int | None,
    ) -> None:
        super().__init__()
        self._include_process_id = include_process_id
        self._include_thread_name = include_thread_name
        self._indent = indent

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": _utc_iso_now(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if self._include_process_id:
            payload["pid"] = record.process
        if self._include_thread_name:
            payload["thread"] = record.threadName

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False, indent=self._indent)


class _TextFormatter(logging.Formatter):
    def __init__(
        self,
        *,
        include_process_id: bool,
        include_thread_name: bool,
    ) -> None:
        parts = [
            "%(asctime)s",
            "%(levelname)s",
            "%(name)s",
        ]
        if include_process_id:
            parts.append("pid=%(process)d")
        if include_thread_name:
            parts.append("thread=%(threadName)s")
        parts.append("%(message)s")
        fmt = " | ".join(parts)
        super().__init__(fmt=fmt, datefmt="%Y-%m-%dT%H:%M:%S%z")


def _build_log_formatter(logging_settings: LoggingSettings) -> logging.Formatter:
    if logging_settings.fmt == "json":
        return _JsonFormatter(
            include_process_id=logging_settings.include_process_id,
            include_thread_name=logging_settings.include_thread_name,
            indent=logging_settings.json_indent,
        )
    return _TextFormatter(
        include_process_id=logging_settings.include_process_id,
        include_thread_name=logging_settings.include_thread_name,
    )


def setup_logging(
    logging_settings: LoggingSettings | None = None,
    *,
    force: bool = False,
) -> None:
    """
    Configure root logging exactly once unless force=True.
    """
    settings = logging_settings or get_settings().logging
    root = logging.getLogger()

    if root.handlers and not force:
        root.setLevel(getattr(logging, settings.level, logging.INFO))
        return

    if force:
        for handler in list(root.handlers):
            root.removeHandler(handler)
            try:
                handler.close()
            except Exception:
                pass

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(_build_log_formatter(settings))

    root.addHandler(handler)
    root.setLevel(getattr(logging, settings.level, logging.INFO))


def configure_logging_from_settings(*, force: bool = False) -> None:
    """
    Convenience bootstrap for application entrypoints.
    """
    setup_logging(get_settings().logging, force=force)


# ============================================================================
# Cached process-wide access
# ============================================================================


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """
    Return the canonical process-wide validated settings object.
    """
    return build_settings()


def reset_settings_cache() -> None:
    """
    Clear the cached settings singleton.
    """
    get_settings.cache_clear()


def settings_to_safe_json(*, indent: int | None = 2) -> str:
    """
    Render the canonical settings as redacted JSON for diagnostics.
    """
    return json.dumps(get_settings().to_safe_dict(), ensure_ascii=False, indent=indent)


# ============================================================================
# Public exports
# ============================================================================

__all__ = [
    "AppSettings",
    "DEFAULT_APP_ENV",
    "DEFAULT_APP_NAME",
    "DEFAULT_ENV_FILE",
    "DEFAULT_ENV_PREFIX",
    "DEFAULT_EXECUTION_DECISION_BLOCK_MS",
    "DEFAULT_EXECUTION_IDLE_SLEEP_MS",
    "DEFAULT_EXECUTION_LOCK_ACQUIRE_TIMEOUT_MS",
    "DEFAULT_FEEDS_MAX_FRAME_STALENESS_MS",
    "DEFAULT_FEEDS_PUBLISH_COMPLETE_ONLY",
    "DEFAULT_HEARTBEAT_TTL_MS",
    "DEFAULT_LOCK_REFRESH_INTERVAL_MS",
    "DEFAULT_LOCK_TTL_MS",
    "DEFAULT_LOGIN_HEALTH_PUBLISH_INTERVAL_MS",
    "DEFAULT_LOGIN_PUBLISH_HEALTH",
    "DEFAULT_LOG_FORMAT",
    "DEFAULT_LOG_INCLUDE_PROCESS_ID",
    "DEFAULT_LOG_INCLUDE_THREAD_NAME",
    "DEFAULT_LOG_LEVEL",
    "DEFAULT_MONITOR_HEALTH_PUBLISH_INTERVAL_MS",
    "DEFAULT_MONITOR_POLL_INTERVAL_MS",
    "DEFAULT_REDIS_DECODE_RESPONSES",
    "DEFAULT_REDIS_HEALTH_CHECK_INTERVAL_S",
    "DEFAULT_REDIS_MAX_CONNECTIONS",
    "DEFAULT_REDIS_RETRY_ON_TIMEOUT",
    "DEFAULT_REDIS_SOCKET_CONNECT_TIMEOUT_S",
    "DEFAULT_REDIS_SOCKET_TIMEOUT_S",
    "DEFAULT_REDIS_URL",
    "DEFAULT_REPLAY_SLEEP_FLOOR_MS",
    "DEFAULT_REPLAY_SPEED",
    "DEFAULT_REPLAY_STRICT_MONOTONICITY",
    "DEFAULT_REPORT_ACK_LIMIT",
    "DEFAULT_REPORT_ERROR_LIMIT",
    "DEFAULT_REPORT_HEALTH_LIMIT",
    "DEFAULT_REPORT_HISTORY_LIMIT",
    "DEFAULT_REPORT_INCLUDE_ENTRY_MODE",
    "DEFAULT_REPORT_ORDER_LIMIT",
    "DEFAULT_RUNTIME_MODE",
    "DEFAULT_STARTUP_FAIL_FAST",
    "DEFAULT_STARTUP_REQUIRE_LOGIN_HEALTH",
    "DEFAULT_STARTUP_REQUIRE_REDIS_PING",
    "DEFAULT_STARTUP_REQUIRE_RUNTIME_INSTRUMENTS",
    "DEFAULT_STRATEGY_PENDING_WAIT_MS",
    "DEFAULT_STRATEGY_STOP_PCT",
    "DEFAULT_STRATEGY_TARGET_PCT",
    "DEFAULT_STREAM_MAXLEN_APPROX",
    "DEFAULT_XREAD_BLOCK_MS",
    "DEFAULT_XREAD_COUNT",
    "env_get_any",
    "runtime_mode_input_snapshot",
    "validate_runtime_mode_input_snapshot",
    "ExecutionSettings",
    "FeedsSettings",
    "LoggingSettings",
    "LoginSettings",
    "MonitorSettings",
    "RedisSettings",
    "ReportSettings",
    "RuntimeSettings",
    "SettingsError",
    "StartupSettings",
    "StrategySettings",
    "build_execution_settings",
    "build_feeds_settings",
    "build_logging_settings",
    "build_login_settings",
    "build_monitor_settings",
    "build_redis_settings",
    "build_report_settings",
    "build_runtime_settings",
    "build_settings",
    "build_startup_settings",
    "build_strategy_settings",
    "configure_logging_from_settings",
    "get_settings",
    "reset_settings_cache",
    "settings_to_safe_json",
    "setup_logging",
    "validate_settings",
]

# ===== BATCH18_CORE_INFRA_SPINE_FREEZE START =====
# Batch 18 freeze-final guard:
# settings.py remains the low-level environment/settings loader. These helpers
# do not change runtime behavior. They expose runtime-truth inputs so main/config
# governance can prove whether YAML/env/systemd agree.

import os as _batch18_os
from typing import Mapping as _batch18_Mapping
from typing import Any as _batch18_Any


def runtime_mode_input_snapshot(
    environ: _batch18_Mapping[str, str] | None = None,
) -> dict[str, str]:
    env = dict(environ or _batch18_os.environ)
    allowed = globals().get("ALLOWED_RUNTIME_MODES", ("live", "replay"))
    default = globals().get("DEFAULT_RUNTIME_MODE", "live")
    return {
        "MME_RUNTIME_MODE": env.get("MME_RUNTIME_MODE", ""),
        "SCALPX_RUNTIME_MODE": env.get("SCALPX_RUNTIME_MODE", ""),
        "MME_TRADING_ENABLED": env.get("MME_TRADING_ENABLED", ""),
        "SCALPX_TRADING_ENABLED": env.get("SCALPX_TRADING_ENABLED", ""),
        "MME_ALLOW_LIVE_ORDERS": env.get("MME_ALLOW_LIVE_ORDERS", ""),
        "SCALPX_ALLOW_LIVE_ORDERS": env.get("SCALPX_ALLOW_LIVE_ORDERS", ""),
        "MME_BOOTSTRAP_GROUPS_ON_START": env.get("MME_BOOTSTRAP_GROUPS_ON_START", ""),
        "SCALPX_BOOTSTRAP_GROUPS_ON_START": env.get("SCALPX_BOOTSTRAP_GROUPS_ON_START", ""),
        "settings_allowed_runtime_modes": ",".join(str(x) for x in allowed),
        "settings_default_runtime_mode": str(default),
    }


def build_effective_runtime_config_state(
    *,
    settings_runtime_mode: str,
    runtime_yaml_mode: str | None = None,
    project_env_runtime_mode: str | None = None,
    env_runtime_mode: str | None = None,
    source_of_truth: str = "settings.py",
    notes: _batch18_Mapping[str, _batch18_Any] | None = None,
) -> dict[str, _batch18_Any]:
    values = {
        "settings_runtime_mode": settings_runtime_mode,
        "runtime_yaml_mode": runtime_yaml_mode,
        "project_env_runtime_mode": project_env_runtime_mode,
        "env_runtime_mode": env_runtime_mode,
    }
    present = {k: v for k, v in values.items() if v not in (None, "")}
    normalized = {k: str(v).strip().lower() for k, v in present.items()}

    conflicts: list[str] = []
    unique_modes = set(normalized.values())
    if len(unique_modes) > 1:
        conflicts.append("runtime_mode_mismatch")

    return {
        "source_of_truth": source_of_truth,
        "settings_runtime_behavior_changed": False,
        "values": values,
        "normalized_values": normalized,
        "conflicts": conflicts,
        "conflict_count": len(conflicts),
        "status": "WARN" if conflicts else "OK",
        "notes": dict(notes or {}),
    }


try:
    for _name in ("runtime_mode_input_snapshot", "build_effective_runtime_config_state"):
        if _name not in __all__:
            __all__.append(_name)
except Exception:
    pass
# ===== BATCH18_CORE_INFRA_SPINE_FREEZE END =====
