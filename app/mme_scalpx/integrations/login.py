#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ScalpX MME - integrations/login.py

Broker authentication and token-governance integration.

Owned responsibilities
----------------------
1. Load broker secrets from the shared secret model.
2. Authenticate Upstox and Zerodha.
3. Verify tokens using broker probes.
4. Persist canonical tokens.json atomically.
5. Publish canonical login state.
6. Publish canonical login heartbeat/health.
7. Publish additive auth observability to system health/error streams.
8. Run an explicit pre-open refresh loop when requested.

Non-responsibilities
--------------------
- No market-data subscription.
- No order placement.
- No strategy / risk / execution logic.
- No runtime supervision ownership.
- No composition-root ownership.
- No trading-state ownership.
- No fallback transport namespace.

Freeze rules
------------
- This module is an integration, not a runtime-supervised trading service.
- State writes only to names.HASH_STATE_LOGIN.
- Heartbeat writes only to names.KEY_HEALTH_LOGIN.
- Additive observability only to names.STREAM_SYSTEM_HEALTH / names.STREAM_SYSTEM_ERRORS.
- main.py remains the only runtime composition root.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import contextlib
import json
import logging
import logging.handlers
import os
import secrets
import signal
import ssl
import sys
import tempfile
import time
import urllib.parse as up
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Final, Optional
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.mme_scalpx.core import names
from app.mme_scalpx.core.clock import CLOCK

try:
    from redis.asyncio import Redis as AsyncRedis  # type: ignore
except Exception as exc:  # pragma: no cover
    raise RuntimeError(
        "redis.asyncio is required by app.mme_scalpx.integrations.login"
    ) from exc

try:
    from kiteconnect import KiteConnect  # type: ignore
except Exception:
    KiteConnect = None  # type: ignore


VERSION: Final[str] = "mme-login-v4-freeze"
SERVICE_NAME: Final[str] = "login"
CANONICAL_MODULE_PATH: Final[str] = "app.mme_scalpx.integrations.login"

LOGIN_STATE_HASH: Final[str] = names.HASH_STATE_LOGIN
LOGIN_HEALTH_KEY: Final[str] = names.KEY_HEALTH_LOGIN
SYSTEM_HEALTH_STREAM: Final[str] = names.STREAM_SYSTEM_HEALTH
SYSTEM_ERRORS_STREAM: Final[str] = names.STREAM_SYSTEM_ERRORS

HEALTH_OK: Final[str] = names.HEALTH_STATUS_OK
HEALTH_WARN: Final[str] = names.HEALTH_STATUS_WARN
HEALTH_ERROR: Final[str] = names.HEALTH_STATUS_ERROR

LOGIN_HEALTH_TTL_MS: Final[int] = 60_000
LOGIN_STATE_TTL_MS: Final[int] = 24 * 60 * 60 * 1000

# Project / shared-secret paths
PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parents[3]
SCALPX_ROOT: Final[Path] = PROJECT_ROOT.parents[1]
COMMON_SECRETS_DIR: Final[Path] = SCALPX_ROOT / "common" / "secrets"
PROJECT_SECRETS_DIR: Final[Path] = COMMON_SECRETS_DIR / "projects" / "mme_scalpx"

DEFAULT_ETC_DIR: Final[Path] = PROJECT_ROOT / "etc"
DEFAULT_VAR_DIR: Final[Path] = PROJECT_ROOT / "var"
DEFAULT_LOG_DIR: Final[Path] = PROJECT_ROOT / "logs"

DEFAULT_VAULT_PATH: Final[Path] = Path(
    os.getenv("SCALPX_LOGIN_VAULT", str(PROJECT_SECRETS_DIR / "vault.json"))
)
DEFAULT_TOKENS_PATH: Final[Path] = Path(
    os.getenv("SCALPX_LOGIN_TOKENS", str(PROJECT_SECRETS_DIR / "tokens.json"))
)

DEFAULT_VAR_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_LOG_DIR.mkdir(parents=True, exist_ok=True)
PROJECT_SECRETS_DIR.mkdir(parents=True, exist_ok=True)

HTTP_TIMEOUT: Final[int] = 30
VERIFY_TIMEOUT: Final[int] = 15
CALLBACK_TIMEOUT: Final[int] = 300
MAX_JSON_FILE_SIZE: Final[int] = 2_000_000

UPSTOX_AUTH_URL: Final[str] = "https://api.upstox.com/v2/login/authorization/dialog"
UPSTOX_TOKEN_URL: Final[str] = "https://api.upstox.com/v2/login/authorization/token"
UPSTOX_PROFILE_URL: Final[str] = "https://api.upstox.com/v2/user/profile"
UPSTOX_QUOTES_URL: Final[str] = "https://api.upstox.com/v2/market-quote/quotes"
UPSTOX_SCOPE: Final[str] = "market-read offline_access"

ZERODHA_LOGIN_URL: Final[str] = "https://kite.zerodha.com/connect/login?v=3"

UPSTOX_PROBE_KEYS: Final[tuple[str, ...]] = (
    "NSE_INDEX|Nifty 50",
    "NSE_INDEX|Nifty Bank",
)
ZERODHA_PROBE_KEYS: Final[tuple[str, ...]] = (
    "NSE:NIFTY 50",
    "NSE:NIFTY BANK",
)

USER_AGENT: Final[str] = os.getenv("SCALPX_USER_AGENT", f"ScalpX-MME-Login/{VERSION}")
COMMON_HEADERS: Final[dict[str, str]] = {"User-Agent": USER_AGENT}

TOKENS_FILE_ENV: Final[str] = os.getenv("TOKENS_FILE", "").strip()
SKIP_VERIFY: Final[bool] = os.getenv("SCALPX_SKIP_VERIFY", "0") == "1"
UPSTOX_HEADLESS_OK: Final[bool] = os.getenv("SCALPX_UPSTOX_HEADLESS_OK", "0") == "1"
ZERODHA_HEADLESS_OK: Final[bool] = os.getenv("SCALPX_ZERODHA_HEADLESS_OK", "0") == "1"
UPSTOX_REQUIRE_VALID: Final[bool] = os.getenv("UPSTOX_REQUIRE_VALID", "0") == "1"

logger = logging.getLogger("scalpx.mme.integrations.login")


class _RedactFilter(logging.Filter):
    _MASK_PATTERNS = (
        "access_token",
        "refresh_token",
        "enctoken",
        "Authorization: Bearer ",
    )

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()
            for pattern in self._MASK_PATTERNS:
                if pattern in message:
                    message = message.replace(pattern, f"{pattern}[REDACTED]")
            record.msg = message
            record.args = ()
        except Exception:
            pass
        return True


def setup_logging(log_level: str = "INFO") -> None:
    if logger.handlers:
        return

    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")

    file_handler = logging.handlers.RotatingFileHandler(
        DEFAULT_LOG_DIR / "login.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
    )
    file_handler.setFormatter(formatter)
    file_handler.addFilter(_RedactFilter())

    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    stream_handler.addFilter(_RedactFilter())

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


class LoginError(RuntimeError):
    """Base login/auth error."""


class VaultError(LoginError):
    """Vault loading error."""


class TokenStoreError(LoginError):
    """Token file read/write error."""


class BrokerAuthError(LoginError):
    """Broker authentication or verification error."""


class HealthPublishError(LoginError):
    """Login health publication failure."""


class StartupValidationError(LoginError):
    """Fail-fast startup validation error."""


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def now_ist() -> datetime:
    return datetime.fromtimestamp(
        CLOCK.now_ns() / 1_000_000_000,
        tz=timezone.utc,
    ).astimezone(timezone(timedelta(hours=5, minutes=30)))


def non_sensitive_head(value: Optional[str]) -> str:
    if not value:
        return "MISSING"
    return f"{value[:8]}..."


def read_json(path: Path) -> Optional[dict[str, Any]]:
    if not path.exists() or path.stat().st_size == 0:
        return None
    if path.stat().st_size > MAX_JSON_FILE_SIZE:
        raise TokenStoreError(f"JSON too large: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise TokenStoreError(f"Failed to parse JSON {path}: {exc}") from exc


def atomic_write_json(path: Path, payload: dict[str, Any], mode: int = 0o640) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    with tempfile.NamedTemporaryFile(
        mode="w",
        delete=False,
        dir=str(path.parent),
        encoding="utf-8",
    ) as tmp:
        tmp.write(raw)
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)
    try:
        os.chmod(path, mode)
    except Exception:
        pass


def ensure_tokens_shape(payload: Optional[dict[str, Any]]) -> dict[str, Any]:
    obj = payload or {}
    if not isinstance(obj.get("upstox"), dict):
        obj["upstox"] = {}
    if not isinstance(obj.get("zerodha"), dict):
        obj["zerodha"] = {}
    obj.setdefault("schema_version", VERSION)
    obj.setdefault("updated_at", now_utc().isoformat())
    return obj


def _b64url_decode(segment: str) -> bytes:
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


def decode_jwt_claims(token: Optional[str]) -> dict[str, Any]:
    if not token or "." not in token:
        return {}
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return {}
        payload = json.loads(_b64url_decode(parts[1]).decode("utf-8"))
        for field_name in ("exp", "iat"):
            value = payload.get(field_name)
            if isinstance(value, (int, float)):
                payload[f"{field_name}_utc"] = datetime.fromtimestamp(
                    int(value),
                    tz=timezone.utc,
                ).isoformat()
        return payload
    except Exception:
        return {}


def ist_seconds_until(hour: int, minute: int) -> int:
    now = now_ist()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target = target + timedelta(days=1)
    return int((target - now).total_seconds())


def build_http_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=2,
        connect=2,
        read=2,
        backoff_factor=0.3,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "POST"),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update(COMMON_HEADERS)
    session.verify = not SKIP_VERIFY
    return session


HTTP = build_http_session()


@dataclass(frozen=True, slots=True)
class UpstoxConfig:
    client_id: str
    client_secret: str
    redirect_uri: str


@dataclass(frozen=True, slots=True)
class ZerodhaConfig:
    api_key: str
    api_secret: str
    user_id: Optional[str] = None


@dataclass(frozen=True, slots=True)
class StorageConfig:
    tokens_file: Path


@dataclass(frozen=True, slots=True)
class UnifiedVault:
    upstox: Optional[UpstoxConfig]
    zerodha: Optional[ZerodhaConfig]
    storage: StorageConfig


@dataclass(slots=True)
class BrokerSessionState:
    broker: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    enctoken: Optional[str] = None
    expires_at_iso: Optional[str] = None
    verified_ok: bool = False
    verified_at_iso: Optional[str] = None
    session_day_ist: Optional[str] = None
    user_id: Optional[str] = None
    account_ref: Optional[str] = None
    last_error: Optional[str] = None

    def to_public_mapping(self) -> dict[str, Any]:
        return {
            "broker": self.broker,
            "has_access_token": bool(self.access_token),
            "has_refresh_token": bool(self.refresh_token),
            "has_enctoken": bool(self.enctoken),
            "expires_at_iso": self.expires_at_iso,
            "verified_ok": self.verified_ok,
            "verified_at_iso": self.verified_at_iso,
            "session_day_ist": self.session_day_ist,
            "user_id": self.user_id,
            "account_ref": self.account_ref,
            "last_error": self.last_error,
        }


@dataclass(frozen=True, slots=True)
class RuntimeConfig:
    vault_path: Path
    tokens_path: Path
    redis_url: Optional[str]
    daemon_refresh: bool
    do_upstox: bool
    do_zerodha: bool
    preopen_hour: int
    preopen_minute: int
    log_level: str


def _extract_registry_module_path(entry: Any) -> Optional[str]:
    if entry is None:
        return None
    if hasattr(entry, "module_path"):
        value = getattr(entry, "module_path")
        return str(value) if value is not None else None
    if isinstance(entry, dict) and "module_path" in entry:
        value = entry.get("module_path")
        return str(value) if value is not None else None
    return None


def _validate_login_registry_binding() -> None:
    registry = getattr(names, "SERVICE_REGISTRY", None)
    service_login_key = getattr(names, "SERVICE_LOGIN", None)

    if registry is None or service_login_key is None:
        return

    entry = registry.get(service_login_key) if hasattr(registry, "get") else None
    module_path = _extract_registry_module_path(entry)
    if module_path and module_path != CANONICAL_MODULE_PATH:
        raise StartupValidationError(
            f"names.SERVICE_REGISTRY login module_path must be "
            f"{CANONICAL_MODULE_PATH}, got {module_path}"
        )


def load_unified_vault(path: Path, tokens_path: Path) -> UnifiedVault:
    payload = read_json(path)
    if payload is None:
        raise VaultError(f"vault not found or empty: {path}")

    up_cfg_raw = payload.get("upstox") or {}
    ze_cfg_raw = payload.get("zerodha") or {}

    up_cfg: Optional[UpstoxConfig] = None
    if up_cfg_raw:
        up_cfg = UpstoxConfig(
            client_id=str(up_cfg_raw.get("client_id", "")).strip(),
            client_secret=str(up_cfg_raw.get("client_secret", "")).strip(),
            redirect_uri=str(
                os.getenv("UPSTOX_REDIRECT_URI")
                or up_cfg_raw.get("redirect_uri")
                or "http://127.0.0.1:8000/callback"
            ).strip(),
        )
        if not up_cfg.client_id or not up_cfg.client_secret:
            raise VaultError("Upstox config missing client_id/client_secret")

    ze_cfg: Optional[ZerodhaConfig] = None
    if ze_cfg_raw:
        ze_cfg = ZerodhaConfig(
            api_key=str(ze_cfg_raw.get("api_key", "")).strip(),
            api_secret=str(ze_cfg_raw.get("api_secret", "")).strip(),
            user_id=str(ze_cfg_raw.get("user_id", "")).strip() or None,
        )
        if not ze_cfg.api_key or not ze_cfg.api_secret:
            raise VaultError("Zerodha config missing api_key/api_secret")

    return UnifiedVault(
        upstox=up_cfg,
        zerodha=ze_cfg,
        storage=StorageConfig(tokens_file=tokens_path),
    )


class TokenStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> dict[str, Any]:
        return ensure_tokens_shape(read_json(self.path))

    def save(self, payload: dict[str, Any]) -> None:
        payload = ensure_tokens_shape(payload)
        payload["updated_at"] = now_utc().isoformat()
        atomic_write_json(self.path, payload)

    def update_broker_state(self, broker: str, state: BrokerSessionState) -> dict[str, Any]:
        payload = self.load()
        payload[broker] = {
            "access_token": state.access_token,
            "refresh_token": state.refresh_token,
            "enctoken": state.enctoken,
            "expires_at_iso": state.expires_at_iso,
            "verified_ok": state.verified_ok,
            "verified_at_iso": state.verified_at_iso,
            "session_day_ist": state.session_day_ist,
            "user_id": state.user_id,
            "account_ref": state.account_ref,
            "last_error": state.last_error,
        }
        self.save(payload)
        return payload


def parse_preopen(text: str) -> tuple[int, int]:
    raw = text.strip()
    if ":" not in raw:
        raise StartupValidationError(f"Invalid --preopen value: {text}")
    hour_text, minute_text = raw.split(":", 1)
    hour = int(hour_text)
    minute = int(minute_text)
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise StartupValidationError(f"Invalid --preopen value: {text}")
    return hour, minute


def validate_runtime_config(cfg: RuntimeConfig, vault: UnifiedVault) -> None:
    if not cfg.do_upstox and not cfg.do_zerodha:
        raise StartupValidationError("At least one broker must be selected")

    if cfg.do_upstox and vault.upstox is None:
        raise StartupValidationError("Upstox selected but missing in vault")

    if cfg.do_zerodha and vault.zerodha is None:
        raise StartupValidationError("Zerodha selected but missing in vault")

    if cfg.do_zerodha and KiteConnect is None:
        raise StartupValidationError("kiteconnect is required for Zerodha login")

    if cfg.do_upstox and vault.upstox is not None:
        parsed = urlparse(vault.upstox.redirect_uri)
        if parsed.scheme not in {"http", "https"}:
            raise StartupValidationError(
                f"Invalid Upstox redirect_uri: {vault.upstox.redirect_uri}"
            )

    cfg.tokens_path.parent.mkdir(parents=True, exist_ok=True)
    if not os.access(cfg.tokens_path.parent, os.W_OK):
        raise StartupValidationError(f"Token directory is not writable: {cfg.tokens_path.parent}")

    if not LOGIN_STATE_HASH:
        raise StartupValidationError("names.HASH_STATE_LOGIN is empty")
    if not LOGIN_HEALTH_KEY:
        raise StartupValidationError("names.KEY_HEALTH_LOGIN is empty")
    if not SYSTEM_HEALTH_STREAM:
        raise StartupValidationError("names.STREAM_SYSTEM_HEALTH is empty")
    if not SYSTEM_ERRORS_STREAM:
        raise StartupValidationError("names.STREAM_SYSTEM_ERRORS is empty")

    _validate_login_registry_binding()


class LoginPublisher:
    """
    Canonical publisher for login integration state and observability.

    Ownership:
    - state only to HASH_STATE_LOGIN
    - heartbeat only to KEY_HEALTH_LOGIN
    - additive observability only to STREAM_SYSTEM_HEALTH / STREAM_SYSTEM_ERRORS
    """

    def __init__(self, redis_url: Optional[str]) -> None:
        self.redis_url = (redis_url or "").strip()
        self._redis: Optional[AsyncRedis] = None

    async def connect(self) -> None:
        if not self.redis_url:
            return
        self._redis = AsyncRedis.from_url(self.redis_url, decode_responses=True)
        await self._redis.ping()

    async def close(self) -> None:
        if self._redis is not None:
            try:
                await self._redis.aclose()
            except Exception:
                pass
            self._redis = None

    async def publish_state(self, result: "LoginResult") -> None:
        if self._redis is None:
            return

        ts_ns = int(CLOCK.now_ns())
        state_payload = {
            "service_name": SERVICE_NAME,
            "instance_id": f"{SERVICE_NAME}-{os.getpid()}",
            "module_path": CANONICAL_MODULE_PATH,
            "ts_ns": str(ts_ns),
            "status": result.overall_status,
            "tokens_ok": "1" if result.tokens_ok else "0",
            "upstox_ok": "1" if result.upstox_ok else "0",
            "zerodha_ok": "1" if result.zerodha_ok else "0",
            "upstox_user_id": str(result.upstox.user_id) if result.upstox and result.upstox.user_id else "",
            "zerodha_user_id": str(result.zerodha.user_id) if result.zerodha and result.zerodha.user_id else "",
            "upstox_account_ref": str(result.upstox.account_ref) if result.upstox and result.upstox.account_ref else "",
            "zerodha_account_ref": str(result.zerodha.account_ref) if result.zerodha and result.zerodha.account_ref else "",
            "detail": result.detail(),
            "version": VERSION,
        }
        await self._redis.hset(LOGIN_STATE_HASH, mapping=state_payload)
        await self._redis.pexpire(LOGIN_STATE_HASH, LOGIN_STATE_TTL_MS)

    async def publish_health(self, result: "LoginResult") -> None:
        if self._redis is None:
            return

        ts_ns = int(CLOCK.now_ns())
        health_payload = {
            "service_name": SERVICE_NAME,
            "instance_id": f"{SERVICE_NAME}-{os.getpid()}",
            "module_path": CANONICAL_MODULE_PATH,
            "status": result.overall_status,
            "ok": "1" if result.tokens_ok else "0",
            "tokens_ok": "1" if result.tokens_ok else "0",
            "upstox_ok": "1" if result.upstox_ok else "0",
            "zerodha_ok": "1" if result.zerodha_ok else "0",
            "pid": str(os.getpid()),
            "ts_ns": str(ts_ns),
            "version": VERSION,
            "detail": result.detail(),
        }
        await self._redis.hset(LOGIN_HEALTH_KEY, mapping=health_payload)
        await self._redis.pexpire(LOGIN_HEALTH_KEY, LOGIN_HEALTH_TTL_MS)
        await self._redis.xadd(
            SYSTEM_HEALTH_STREAM,
            health_payload,
            maxlen=10_000,
            approximate=True,
        )

    async def publish_error(self, detail: str) -> None:
        if self._redis is None or not detail:
            return

        payload = {
            "service_name": SERVICE_NAME,
            "instance_id": f"{SERVICE_NAME}-{os.getpid()}",
            "module_path": CANONICAL_MODULE_PATH,
            "status": HEALTH_ERROR,
            "detail": str(detail),
            "pid": str(os.getpid()),
            "ts_ns": str(int(CLOCK.now_ns())),
            "version": VERSION,
        }
        await self._redis.xadd(
            SYSTEM_ERRORS_STREAM,
            payload,
            maxlen=10_000,
            approximate=True,
        )

    async def publish_all(self, result: "LoginResult") -> None:
        if self._redis is None:
            return
        await self.publish_state(result)
        await self.publish_health(result)
        if result.detail() and result.overall_status != HEALTH_OK:
            await self.publish_error(result.detail())


class UpstoxAuthenticator:
    def __init__(self, cfg: UpstoxConfig, token_store: TokenStore) -> None:
        parsed = urlparse(cfg.redirect_uri)
        if parsed.scheme not in {"http", "https"}:
            raise BrokerAuthError(f"invalid Upstox redirect_uri: {cfg.redirect_uri}")
        self.cfg = cfg
        self.token_store = token_store

    def authenticate(self) -> BrokerSessionState:
        state = BrokerSessionState(
            broker="upstox",
            session_day_ist=now_ist().date().isoformat(),
        )
        code = self._get_authorization_code()
        token_payload = self._exchange_code(code)

        access_token = str(token_payload.get("access_token", "")).strip()
        refresh_token = str(token_payload.get("refresh_token", "")).strip() or None
        if not access_token:
            raise BrokerAuthError(f"Upstox token response missing access_token: {token_payload}")

        claims = decode_jwt_claims(access_token)
        verified = self._verify_access_token(access_token)

        state.access_token = access_token
        state.refresh_token = refresh_token
        state.expires_at_iso = claims.get("exp_utc")
        state.verified_ok = True
        state.verified_at_iso = now_utc().isoformat()
        state.user_id = verified.get("user_id")
        state.account_ref = verified.get("email") or verified.get("user_id")
        state.last_error = None

        self.token_store.update_broker_state("upstox", state)
        return state

    def _get_authorization_code(self) -> str:
        callback_url = os.getenv("UPSTOX_CALLBACK_URL", "").strip()
        if callback_url:
            code = self._extract_code_from_callback_url(callback_url)
            if code:
                logger.info("Upstox using code from UPSTOX_CALLBACK_URL")
                return code

        raw_code = os.getenv("UPSTOX_AUTH_CODE", "").strip()
        if raw_code:
            logger.info("Upstox using raw auth code from UPSTOX_AUTH_CODE")
            return raw_code

        if not sys.stdin.isatty() and UPSTOX_HEADLESS_OK and not UPSTOX_REQUIRE_VALID:
            raise BrokerAuthError("Upstox interactive auth unavailable in headless mode")

        return self._interactive_code()

    @staticmethod
    def _extract_code_from_callback_url(url_with_code: str) -> Optional[str]:
        try:
            parsed = up.urlparse(url_with_code)
            params = dict(up.parse_qsl(parsed.query))
            return params.get("code")
        except Exception:
            return None

    def _interactive_code(self) -> str:
        callback_host = os.getenv("UPSTOX_SERVER_HOST", "127.0.0.1")
        callback_port = int(os.getenv("UPSTOX_SERVER_PORT", "8000"))
        callback_path = os.getenv("UPSTOX_SERVER_PATH", "/callback").strip() or "/callback"
        use_tls = os.getenv("UPSTOX_TLS_ENABLE", "0") == "1"
        tls_cert = os.getenv("UPSTOX_TLS_CERT", "").strip()
        tls_key = os.getenv("UPSTOX_TLS_KEY", "").strip()

        state_box: dict[str, Any] = {
            "code": None,
            "error": None,
            "received": False,
        }

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, fmt: str, *args: Any) -> None:
                return

            def do_GET(self) -> None:  # noqa: N802
                try:
                    if not self.path.startswith(callback_path):
                        self.send_response(404)
                        self.end_headers()
                        return

                    params = dict(up.parse_qsl(up.urlparse(self.path).query))
                    state_box["code"] = params.get("code")
                    state_box["error"] = params.get("error")
                    state_box["received"] = True

                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()

                    if state_box["code"]:
                        self.wfile.write(b"<h3 style='color:green'>ScalpX Upstox auth success</h3>")
                    else:
                        self.wfile.write(b"<h3 style='color:red'>ScalpX Upstox auth failed</h3>")
                except Exception as exc:
                    state_box["error"] = str(exc)
                    state_box["received"] = True

        server: Optional[HTTPServer] = None
        try:
            bind_host = callback_host if not use_tls else "0.0.0.0"
            server = HTTPServer((bind_host, callback_port), Handler)
            scheme = "http"

            if use_tls:
                if not tls_cert or not tls_key:
                    raise BrokerAuthError("UPSTOX_TLS_ENABLE=1 but TLS cert/key missing")
                ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ssl_context.load_cert_chain(tls_cert, tls_key)
                server.socket = ssl_context.wrap_socket(server.socket, server_side=True)
                scheme = "https"

            server.timeout = 1
            auth_url = self._build_auth_url()

            print(f"Callback server: {scheme}://{bind_host}:{callback_port}{callback_path}")
            print("Open this URL in browser:")
            print(auth_url)
            print(f"(redirect_uri must exactly match) {self.cfg.redirect_uri}")

            started_at = time.time()
            while time.time() - started_at < CALLBACK_TIMEOUT:
                server.handle_request()
                if state_box["received"]:
                    break

            if not state_box["received"]:
                raise BrokerAuthError("Upstox auth timeout waiting for callback")
            if state_box["error"]:
                raise BrokerAuthError(f"Upstox auth error: {state_box['error']}")
            if not state_box["code"]:
                raise BrokerAuthError("No authorization code returned from Upstox callback")

            return str(state_box["code"])
        finally:
            if server is not None:
                with contextlib.suppress(Exception):
                    server.server_close()

    def _build_auth_url(self) -> str:
        query = up.urlencode(
            {
                "response_type": "code",
                "client_id": self.cfg.client_id,
                "redirect_uri": self.cfg.redirect_uri,
                "scope": UPSTOX_SCOPE,
                "state": secrets.token_hex(8),
            }
        )
        return f"{UPSTOX_AUTH_URL}?{query}"

    def _exchange_code(self, code: str) -> dict[str, Any]:
        headers = {**COMMON_HEADERS, "Content-Type": "application/x-www-form-urlencoded"}
        response = HTTP.post(
            UPSTOX_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": self.cfg.client_id,
                "client_secret": self.cfg.client_secret,
                "redirect_uri": self.cfg.redirect_uri,
            },
            headers=headers,
            timeout=HTTP_TIMEOUT,
        )
        try:
            payload = response.json()
        except Exception:
            payload = {"http_status": response.status_code, "text": response.text[:500]}
        if response.status_code != 200 or not isinstance(payload, dict):
            raise BrokerAuthError(f"Upstox token exchange failed: {payload}")
        return payload

    def _verify_access_token(self, access_token: str) -> dict[str, Any]:
        headers = {**COMMON_HEADERS, "Authorization": f"Bearer {access_token}"}

        profile_response = HTTP.get(
            UPSTOX_PROFILE_URL,
            headers=headers,
            timeout=VERIFY_TIMEOUT,
        )
        try:
            profile = profile_response.json()
        except Exception:
            profile = {
                "http_status": profile_response.status_code,
                "text": profile_response.text[:500],
            }
        if profile_response.status_code != 200:
            raise BrokerAuthError(f"Upstox profile verify failed: {profile}")

        if not SKIP_VERIFY:
            quote_ok = False
            for instrument_key in UPSTOX_PROBE_KEYS:
                try:
                    quote_response = HTTP.get(
                        UPSTOX_QUOTES_URL,
                        headers=headers,
                        params={"instrument_key": instrument_key},
                        timeout=VERIFY_TIMEOUT,
                    )
                    data = quote_response.json()
                    if isinstance(data, dict) and data.get("status") == "success":
                        payload = data.get("data") or {}
                        if isinstance(payload, dict):
                            for item in payload.values():
                                if isinstance(item, dict) and item.get("last_price") is not None:
                                    quote_ok = True
                                    break
                    if quote_ok:
                        break
                except Exception:
                    continue
            if not quote_ok:
                raise BrokerAuthError("Upstox quote probe failed")

        profile_data = profile.get("data") if isinstance(profile, dict) else {}
        if not isinstance(profile_data, dict):
            profile_data = {}

        user_id = str(profile_data.get("user_id") or profile.get("user_id") or "").strip()
        email = str(profile_data.get("email") or profile.get("email") or "").strip() or None
        if not user_id:
            raise BrokerAuthError("Upstox profile payload missing user_id")

        return {"user_id": user_id, "email": email}


class ZerodhaAuthenticator:
    def __init__(self, cfg: ZerodhaConfig, token_store: TokenStore) -> None:
        if KiteConnect is None:
            raise BrokerAuthError("kiteconnect is not installed")
        self.cfg = cfg
        self.token_store = token_store

    def authenticate(self) -> BrokerSessionState:
        state = BrokerSessionState(
            broker="zerodha",
            session_day_ist=now_ist().date().isoformat(),
        )

        request_token = self._get_request_token()
        kite = KiteConnect(api_key=self.cfg.api_key)
        try:
            token_payload = kite.generate_session(request_token, api_secret=self.cfg.api_secret)
        except Exception as exc:
            raise BrokerAuthError(f"Zerodha generate_session failed: {exc}") from exc

        access_token = str(token_payload.get("access_token", "")).strip()
        if not access_token:
            raise BrokerAuthError(
                f"Zerodha session response missing access_token: {token_payload}"
            )

        kite.set_access_token(access_token)
        verified_user_id = self._verify_kite(kite)

        state.access_token = access_token
        state.expires_at_iso = None
        state.verified_ok = True
        state.verified_at_iso = now_utc().isoformat()
        state.user_id = verified_user_id
        state.account_ref = verified_user_id
        state.last_error = None

        self.token_store.update_broker_state("zerodha", state)
        return state

    def _get_request_token(self) -> str:
        request_token = (
            os.getenv("ZERODHA_REQUEST_TOKEN", "").strip()
            or os.getenv("REQUEST_TOKEN", "").strip()
        )
        if request_token:
            logger.info("Zerodha using request token from environment")
            return request_token

        login_url = f"{ZERODHA_LOGIN_URL}&api_key={self.cfg.api_key}"
        if not sys.stdin.isatty() and ZERODHA_HEADLESS_OK:
            raise BrokerAuthError("Zerodha interactive request-token entry unavailable in headless mode")

        print("Open Zerodha login URL:")
        print(login_url)
        print("After login, paste request_token:")
        entered = input("request_token: ").strip()
        if not entered:
            raise BrokerAuthError("empty Zerodha request_token")
        return entered

    def _verify_kite(self, kite: KiteConnect) -> str:
        try:
            profile = kite.profile()
        except Exception as exc:
            raise BrokerAuthError(f"Zerodha profile verify failed: {exc}") from exc

        user_id = str(profile.get("user_id", "")).strip()
        if not user_id:
            raise BrokerAuthError("Zerodha profile missing user_id")

        if not SKIP_VERIFY:
            try:
                ltps = kite.ltp(list(ZERODHA_PROBE_KEYS))
            except Exception as exc:
                raise BrokerAuthError(f"Zerodha LTP probe failed: {exc}") from exc
            if not isinstance(ltps, dict) or not ltps:
                raise BrokerAuthError("Zerodha LTP probe returned empty payload")

        return user_id


@dataclass(slots=True)
class LoginResult:
    upstox: Optional[BrokerSessionState] = None
    zerodha: Optional[BrokerSessionState] = None

    @property
    def upstox_ok(self) -> bool:
        return bool(self.upstox and self.upstox.verified_ok)

    @property
    def zerodha_ok(self) -> bool:
        return bool(self.zerodha and self.zerodha.verified_ok)

    @property
    def tokens_ok(self) -> bool:
        return self.upstox_ok or self.zerodha_ok

    @property
    def overall_status(self) -> str:
        if self.tokens_ok:
            return HEALTH_OK
        if self.upstox is None and self.zerodha is None:
            return HEALTH_WARN
        return HEALTH_ERROR

    def detail(self) -> str:
        errors: list[str] = []
        if self.upstox is not None and self.upstox.last_error:
            errors.append(f"upstox={self.upstox.last_error}")
        if self.zerodha is not None and self.zerodha.last_error:
            errors.append(f"zerodha={self.zerodha.last_error}")
        return "; ".join(errors)


class LoginManager:
    def __init__(self, vault: UnifiedVault, token_store: TokenStore) -> None:
        self.vault = vault
        self.token_store = token_store

    def run(self, *, do_upstox: bool, do_zerodha: bool) -> LoginResult:
        result = LoginResult()

        if do_upstox and self.vault.upstox is not None:
            try:
                logger.info("Authenticating Upstox")
                result.upstox = UpstoxAuthenticator(self.vault.upstox, self.token_store).authenticate()
                logger.info(
                    "Upstox auth OK token=%s user=%s",
                    non_sensitive_head(result.upstox.access_token),
                    result.upstox.user_id,
                )
            except Exception as exc:
                state = BrokerSessionState(
                    broker="upstox",
                    verified_ok=False,
                    verified_at_iso=now_utc().isoformat(),
                    session_day_ist=now_ist().date().isoformat(),
                    last_error=str(exc),
                )
                self.token_store.update_broker_state("upstox", state)
                result.upstox = state
                logger.error("Upstox auth failed: %s", exc)

        if do_zerodha and self.vault.zerodha is not None:
            try:
                logger.info("Authenticating Zerodha")
                result.zerodha = ZerodhaAuthenticator(self.vault.zerodha, self.token_store).authenticate()
                logger.info(
                    "Zerodha auth OK token=%s user=%s",
                    non_sensitive_head(result.zerodha.access_token),
                    result.zerodha.user_id,
                )
            except Exception as exc:
                state = BrokerSessionState(
                    broker="zerodha",
                    verified_ok=False,
                    verified_at_iso=now_utc().isoformat(),
                    session_day_ist=now_ist().date().isoformat(),
                    last_error=str(exc),
                )
                self.token_store.update_broker_state("zerodha", state)
                result.zerodha = state
                logger.error("Zerodha auth failed: %s", exc)

        return result


async def refresh_tokens_periodic(
    vault: UnifiedVault,
    redis_url: Optional[str],
    preopen_hour: int,
    preopen_minute: int,
) -> None:
    token_store = TokenStore(vault.storage.tokens_file)
    manager = LoginManager(vault, token_store)
    publisher = LoginPublisher(redis_url)
    await publisher.connect()

    try:
        while True:
            logger.info("Starting scheduled login refresh")
            result = await asyncio.to_thread(
                manager.run,
                do_upstox=vault.upstox is not None,
                do_zerodha=vault.zerodha is not None,
            )
            await publisher.publish_all(result)
            sleep_seconds = max(ist_seconds_until(preopen_hour, preopen_minute), 23 * 3600)
            await asyncio.sleep(sleep_seconds)
    finally:
        await publisher.close()


def install_signal_handlers() -> None:
    def _term(_signo: int, _frame: Any) -> None:
        logger.info("Received termination signal, exiting.")
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, _term)
    signal.signal(signal.SIGINT, _term)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ScalpX MME Broker Login Integration")
    parser.add_argument(
        "--vault",
        default=str(DEFAULT_VAULT_PATH),
        help="Path to shared login vault.json",
    )
    parser.add_argument(
        "--tokens",
        default=TOKENS_FILE_ENV or str(DEFAULT_TOKENS_PATH),
        help="Output path for canonical tokens.json",
    )
    parser.add_argument("--upstox", action="store_true", help="Authenticate only Upstox")
    parser.add_argument("--zerodha", action="store_true", help="Authenticate only Zerodha")
    parser.add_argument(
        "--daemon-refresh",
        action="store_true",
        dest="daemon_refresh",
        help="Run periodic pre-open refresh loop",
    )
    parser.add_argument(
        "--redis",
        default=os.getenv("SCALPX_REDIS_URL", "").strip() or None,
        help="Redis URL for login state and auth observability publication",
    )
    parser.add_argument("--preopen", default="08:45", help="IST HH:MM refresh schedule")
    parser.add_argument("--log-level", default=os.getenv("LOG_LEVEL", "INFO"))
    return parser


def runtime_config_from_args(args: argparse.Namespace) -> RuntimeConfig:
    do_upstox = args.upstox or (not args.upstox and not args.zerodha)
    do_zerodha = args.zerodha or (not args.upstox and not args.zerodha)
    preopen_hour, preopen_minute = parse_preopen(args.preopen)

    return RuntimeConfig(
        vault_path=Path(args.vault),
        tokens_path=Path(args.tokens),
        redis_url=(args.redis or "").strip() or None,
        daemon_refresh=bool(args.daemon_refresh),
        do_upstox=do_upstox,
        do_zerodha=do_zerodha,
        preopen_hour=preopen_hour,
        preopen_minute=preopen_minute,
        log_level=str(args.log_level),
    )


def main(argv: Optional[list[str]] = None) -> int:
    """
    Local auth CLI only.

    This is not a runtime-supervised trading service entrypoint.
    main.py remains the only system composition root.
    """
    args = build_parser().parse_args(argv)
    setup_logging(args.log_level)
    install_signal_handlers()

    try:
        runtime_cfg = runtime_config_from_args(args)
        vault = load_unified_vault(runtime_cfg.vault_path, runtime_cfg.tokens_path)
        validate_runtime_config(runtime_cfg, vault)
    except Exception as exc:
        logger.error("startup validation failed: %s", exc)
        return 1

    if runtime_cfg.daemon_refresh:
        try:
            asyncio.run(
                refresh_tokens_periodic(
                    vault=vault,
                    redis_url=runtime_cfg.redis_url,
                    preopen_hour=runtime_cfg.preopen_hour,
                    preopen_minute=runtime_cfg.preopen_minute,
                )
            )
        except KeyboardInterrupt:
            return 0
        except Exception as exc:
            logger.error("daemon-refresh fatal error: %s", exc)
            return 1
        return 0

    token_store = TokenStore(vault.storage.tokens_file)
    manager = LoginManager(vault, token_store)
    result = manager.run(
        do_upstox=runtime_cfg.do_upstox,
        do_zerodha=runtime_cfg.do_zerodha,
    )

    if result.upstox is not None:
        print(
            "Upstox:",
            result.upstox.verified_ok,
            "user=",
            result.upstox.user_id or "?",
            "token=",
            non_sensitive_head(result.upstox.access_token),
        )
    if result.zerodha is not None:
        print(
            "Zerodha:",
            result.zerodha.verified_ok,
            "user=",
            result.zerodha.user_id or "?",
            "token=",
            non_sensitive_head(result.zerodha.access_token),
        )

    if runtime_cfg.redis_url:
        async def _publish_once() -> None:
            publisher = LoginPublisher(runtime_cfg.redis_url)
            await publisher.connect()
            try:
                await publisher.publish_all(result)
            finally:
                await publisher.close()

        try:
            asyncio.run(_publish_once())
        except Exception as exc:
            logger.warning("login-state publication skipped due to error: %s", exc)

    return 0 if result.tokens_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())