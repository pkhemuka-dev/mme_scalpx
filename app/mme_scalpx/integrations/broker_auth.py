from __future__ import annotations

"""
app/mme_scalpx/integrations/broker_auth.py

Broker authentication and session-lifecycle contract for ScalpX MME.

Purpose
-------
This module OWNS:
- broker-auth configuration parsing for provider-auth surfaces
- credentials loading abstraction
- login / refresh / revoke session lifecycle orchestration
- in-memory session truth for one provider
- normalized auth snapshot / health payload construction
- explicit auth-failure truth without silent defaulting

This module DOES NOT own:
- websocket lifecycle
- market-data normalization
- provider-role resolution
- strategy feature computation
- order placement / fill truth
- Redis IO / stream publishing
- main.py composition
- typed system-wide transport models owned by core.models

Design rules
------------
- core.names remains the single source of truth for provider ids and statuses.
- provider_runtime.py consumes provider-health truth; it does not manage sessions.
- broker_auth.py is intentionally model-light so it can stabilize before the
  in-flight core.models lane finishes.
- auth failure must be explicit.
- disabled auth must be explicit.
- no raw secrets may leak in public snapshots or public health payloads.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from types import MappingProxyType
from typing import Any, Mapping, MutableMapping, Protocol, Sequence
import os
import time

try:  # pragma: no cover - optional dependency at import time
    import yaml
except Exception:  # pragma: no cover
    yaml = None

from app.mme_scalpx.core import names
from app.mme_scalpx.core.validators import (
    ValidationError,
    require_bool,
    require_int,
    require_literal,
    require_mapping,
    require_non_empty_str,
)

# ============================================================================
# Compatibility fallbacks against frozen names surfaces
# ============================================================================

_ALLOWED_PROVIDER_IDS: tuple[str, ...] = tuple(
    getattr(
        names,
        "ALLOWED_PROVIDER_IDS",
        getattr(
            names,
            "PROVIDER_IDS",
            (
                names.PROVIDER_ZERODHA,
                names.PROVIDER_DHAN,
            ),
        ),
    )
)

_STATUS_HEALTHY: str = getattr(names, "PROVIDER_STATUS_HEALTHY", "HEALTHY")
_STATUS_DEGRADED: str = getattr(names, "PROVIDER_STATUS_DEGRADED", "DEGRADED")
_STATUS_AUTH_FAILED: str = getattr(names, "PROVIDER_STATUS_AUTH_FAILED", "AUTH_FAILED")
_STATUS_UNAVAILABLE: str = getattr(names, "PROVIDER_STATUS_UNAVAILABLE", "UNAVAILABLE")
_STATUS_DISABLED: str = getattr(names, "PROVIDER_STATUS_DISABLED", "DISABLED")

# ============================================================================
# Exceptions
# ============================================================================


class BrokerAuthError(ValueError):
    """Base error for broker-auth failures."""


class BrokerAuthValidationError(BrokerAuthError):
    """Raised when broker-auth config or inputs are invalid."""


class BrokerCredentialsError(BrokerAuthError):
    """Raised when credentials are missing or malformed."""


class BrokerLoginError(BrokerAuthError):
    """Raised when provider login fails."""


class BrokerRefreshError(BrokerAuthError):
    """Raised when provider session refresh fails."""


class BrokerSessionUnavailableError(BrokerAuthError):
    """Raised when no usable provider session is available."""


# ============================================================================
# Shared validator wrappers
# ============================================================================


def _wrap_validation(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as exc:
        if isinstance(exc, BrokerAuthValidationError):
            raise
        if isinstance(exc, ValidationError):
            raise BrokerAuthValidationError(str(exc)) from exc
        raise BrokerAuthValidationError(str(exc)) from exc


def _require_non_empty_str(value: str, field_name: str) -> str:
    return _wrap_validation(require_non_empty_str, value, field_name=field_name)


def _require_bool(value: bool, field_name: str) -> bool:
    return _wrap_validation(require_bool, value, field_name=field_name)


def _require_int(
    value: int,
    field_name: str,
    *,
    min_value: int | None = None,
) -> int:
    return _wrap_validation(
        require_int,
        value,
        field_name=field_name,
        min_value=min_value,
    )


def _require_literal(
    value: str,
    field_name: str,
    *,
    allowed: Sequence[str],
) -> str:
    return _wrap_validation(
        require_literal,
        value,
        field_name=field_name,
        allowed=allowed,
    )


def _require_mapping(
    value: Mapping[str, object],
    field_name: str,
) -> dict[str, object]:
    return _wrap_validation(require_mapping, value, field_name=field_name)


def _coerce_positive_int(
    value: Any,
    *,
    field_name: str,
    allow_none: bool = False,
) -> int | None:
    if value is None:
        if allow_none:
            return None
        raise BrokerAuthValidationError(f"{field_name} may not be None")
    if isinstance(value, bool):
        raise BrokerAuthValidationError(f"{field_name} must be an int, got bool")
    try:
        parsed = int(value)
    except Exception as exc:
        raise BrokerAuthValidationError(f"{field_name} must be an int") from exc
    if parsed < 0:
        raise BrokerAuthValidationError(f"{field_name} must be >= 0")
    return parsed


def _freeze_mapping(data: Mapping[str, Any] | None) -> Mapping[str, Any]:
    raw = {} if data is None else dict(data)
    return MappingProxyType(raw)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _now_ns() -> int:
    return time.time_ns()


def _dt_from_ns(value_ns: int | None) -> datetime | None:
    if value_ns is None:
        return None
    return datetime.fromtimestamp(value_ns / 1_000_000_000, tz=timezone.utc)


def _iso_from_ns(value_ns: int | None) -> str | None:
    dt = _dt_from_ns(value_ns)
    return dt.isoformat() if dt is not None else None


def _ns_from_datetime(value: datetime | None, *, field_name: str) -> int | None:
    if value is None:
        return None
    if value.tzinfo is None:
        raise BrokerAuthValidationError(f"{field_name} must be timezone-aware")
    return int(value.timestamp() * 1_000_000_000)


def _build_default_env_prefix(provider_id: str) -> str:
    return f"MME_{provider_id.upper()}_"


def _safe_message(exc: Exception) -> str:
    text = str(exc).strip()
    if not text:
        return exc.__class__.__name__
    return text


# ============================================================================
# Public protocols
# ============================================================================


class BrokerCredentialsProvider(Protocol):
    """Protocol for secrets/credential retrieval."""

    def get_credentials(
        self,
        provider_id: str,
        *,
        config: "BrokerAuthConfig",
    ) -> Mapping[str, object]:
        ...


class BrokerSessionClient(Protocol):
    """Protocol for provider-specific login / refresh / revoke operations."""

    def login(
        self,
        credentials: Mapping[str, object],
        *,
        config: "BrokerAuthConfig",
        now_ns: int,
    ) -> "AuthSessionMaterial":
        ...

    def refresh(
        self,
        session: "AuthSessionMaterial",
        credentials: Mapping[str, object],
        *,
        config: "BrokerAuthConfig",
        now_ns: int,
    ) -> "AuthSessionMaterial":
        ...

    def revoke(
        self,
        session: "AuthSessionMaterial",
        *,
        config: "BrokerAuthConfig",
        now_ns: int,
    ) -> None:
        ...


# ============================================================================
# Public value objects
# ============================================================================


@dataclass(frozen=True, slots=True)
class AuthSessionMaterial:
    """
    In-memory provider session material.

    Secrets remain inside this object and must never be emitted through public
    snapshots or public health payloads.
    """

    access_token: str
    refresh_token: str | None = None
    session_id: str | None = None
    issued_at_ns: int | None = None
    expires_at_ns: int | None = None
    account_id: str | None = None
    user_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "access_token",
            _require_non_empty_str(self.access_token, "access_token"),
        )
        if self.refresh_token is not None:
            object.__setattr__(
                self,
                "refresh_token",
                _require_non_empty_str(self.refresh_token, "refresh_token"),
            )
        if self.session_id is not None:
            object.__setattr__(
                self,
                "session_id",
                _require_non_empty_str(self.session_id, "session_id"),
            )
        if self.account_id is not None:
            object.__setattr__(
                self,
                "account_id",
                _require_non_empty_str(self.account_id, "account_id"),
            )
        if self.user_id is not None:
            object.__setattr__(
                self,
                "user_id",
                _require_non_empty_str(self.user_id, "user_id"),
            )
        if self.issued_at_ns is not None:
            object.__setattr__(
                self,
                "issued_at_ns",
                _require_int(self.issued_at_ns, "issued_at_ns", min_value=0),
            )
        if self.expires_at_ns is not None:
            object.__setattr__(
                self,
                "expires_at_ns",
                _require_int(self.expires_at_ns, "expires_at_ns", min_value=0),
            )
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))

    def is_expired(self, *, now_ns: int) -> bool:
        if self.expires_at_ns is None:
            return False
        return now_ns >= self.expires_at_ns

    def refresh_due(self, *, now_ns: int, refresh_lead_seconds: int) -> bool:
        if self.expires_at_ns is None:
            return False
        return now_ns >= (
            self.expires_at_ns - int(refresh_lead_seconds * 1_000_000_000)
        )


@dataclass(frozen=True, slots=True)
class BrokerAuthConfig:
    """
    Provider-auth config.

    This is intentionally independent of core.models so the auth lane can freeze
    cleanly before the typed models lane finalizes.
    """

    provider_id: str
    enabled: bool = True
    auth_required: bool = True
    refresh_supported: bool = True
    refresh_lead_seconds: int = 120
    min_reauth_interval_seconds: int = 3
    failure_backoff_seconds: int = 5
    session_ttl_seconds: int | None = None
    credentials_env_prefix: str | None = None
    account_id: str | None = None
    user_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "provider_id",
            _require_literal(
                self.provider_id,
                "provider_id",
                allowed=_ALLOWED_PROVIDER_IDS,
            ),
        )
        object.__setattr__(self, "enabled", _require_bool(self.enabled, "enabled"))
        object.__setattr__(
            self,
            "auth_required",
            _require_bool(self.auth_required, "auth_required"),
        )
        object.__setattr__(
            self,
            "refresh_supported",
            _require_bool(self.refresh_supported, "refresh_supported"),
        )
        object.__setattr__(
            self,
            "refresh_lead_seconds",
            _require_int(
                self.refresh_lead_seconds,
                "refresh_lead_seconds",
                min_value=0,
            ),
        )
        object.__setattr__(
            self,
            "min_reauth_interval_seconds",
            _require_int(
                self.min_reauth_interval_seconds,
                "min_reauth_interval_seconds",
                min_value=0,
            ),
        )
        object.__setattr__(
            self,
            "failure_backoff_seconds",
            _require_int(
                self.failure_backoff_seconds,
                "failure_backoff_seconds",
                min_value=0,
            ),
        )
        if self.session_ttl_seconds is not None:
            object.__setattr__(
                self,
                "session_ttl_seconds",
                _require_int(
                    self.session_ttl_seconds,
                    "session_ttl_seconds",
                    min_value=0,
                ),
            )
        if self.credentials_env_prefix is not None:
            object.__setattr__(
                self,
                "credentials_env_prefix",
                _require_non_empty_str(
                    self.credentials_env_prefix,
                    "credentials_env_prefix",
                ),
            )
        if self.account_id is not None:
            object.__setattr__(
                self,
                "account_id",
                _require_non_empty_str(self.account_id, "account_id"),
            )
        if self.user_id is not None:
            object.__setattr__(
                self,
                "user_id",
                _require_non_empty_str(self.user_id, "user_id"),
            )
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))

    @classmethod
    def from_provider_mapping(
        cls,
        provider_id: str,
        raw: Mapping[str, object],
    ) -> "BrokerAuthConfig":
        data = _require_mapping(raw, "raw")
        health_contract = data.get("health_contract", {})
        auth_contract = data.get("auth_contract", {})
        health_contract = (
            _require_mapping(health_contract, "health_contract")
            if isinstance(health_contract, Mapping)
            else {}
        )
        auth_contract = (
            _require_mapping(auth_contract, "auth_contract")
            if isinstance(auth_contract, Mapping)
            else {}
        )

        return cls(
            provider_id=provider_id,
            enabled=bool(data.get("enabled", True)),
            auth_required=bool(health_contract.get("auth_required", True)),
            refresh_supported=bool(auth_contract.get("refresh_supported", True)),
            refresh_lead_seconds=int(auth_contract.get("refresh_lead_seconds", 120)),
            min_reauth_interval_seconds=int(
                auth_contract.get("min_reauth_interval_seconds", 3)
            ),
            failure_backoff_seconds=int(
                auth_contract.get("failure_backoff_seconds", 5)
            ),
            session_ttl_seconds=_coerce_positive_int(
                auth_contract.get("session_ttl_seconds"),
                field_name="auth_contract.session_ttl_seconds",
                allow_none=True,
            ),
            credentials_env_prefix=(
                str(auth_contract["credentials_env_prefix"])
                if auth_contract.get("credentials_env_prefix") is not None
                else None
            ),
            account_id=(
                str(auth_contract["account_id"])
                if auth_contract.get("account_id") is not None
                else None
            ),
            user_id=(
                str(auth_contract["user_id"])
                if auth_contract.get("user_id") is not None
                else None
            ),
            metadata={
                "config_source": "provider_mapping",
            },
        )

    @classmethod
    def from_yaml_file(
        cls,
        path: str | Path,
        *,
        provider_id: str | None = None,
    ) -> "BrokerAuthConfig":
        if yaml is None:
            raise BrokerAuthValidationError(
                "PyYAML is required to load broker auth config from YAML"
            )
        candidate = Path(path)
        if not candidate.exists():
            raise BrokerAuthValidationError(f"config file not found: {candidate}")
        loaded = yaml.safe_load(candidate.read_text(encoding="utf-8")) or {}
        if not isinstance(loaded, Mapping):
            raise BrokerAuthValidationError(
                f"config root must be a mapping: {candidate}"
            )

        resolved_provider_id = provider_id or loaded.get("provider_id")
        if resolved_provider_id is None:
            raise BrokerAuthValidationError(
                "provider_id must be supplied either in YAML or argument"
            )
        return cls.from_provider_mapping(str(resolved_provider_id), loaded)


@dataclass(frozen=True, slots=True)
class BrokerAuthSnapshot:
    """
    Public auth/session truth for one provider.

    This object is safe to log or publish. It never contains raw secrets.
    """

    provider_id: str
    status: str
    enabled: bool
    auth_required: bool
    authenticated: bool
    session_active: bool
    account_id: str | None = None
    user_id: str | None = None
    last_success_ns: int | None = None
    last_failure_ns: int | None = None
    expires_at_ns: int | None = None
    refresh_due_ns: int | None = None
    login_count: int = 0
    refresh_count: int = 0
    consecutive_failures: int = 0
    last_error: str | None = None
    last_error_ns: int | None = None
    message: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "provider_id",
            _require_literal(
                self.provider_id,
                "provider_id",
                allowed=_ALLOWED_PROVIDER_IDS,
            ),
        )
        object.__setattr__(
            self,
            "status",
            _require_non_empty_str(self.status, "status"),
        )
        object.__setattr__(self, "enabled", _require_bool(self.enabled, "enabled"))
        object.__setattr__(
            self,
            "auth_required",
            _require_bool(self.auth_required, "auth_required"),
        )
        object.__setattr__(
            self,
            "authenticated",
            _require_bool(self.authenticated, "authenticated"),
        )
        object.__setattr__(
            self,
            "session_active",
            _require_bool(self.session_active, "session_active"),
        )
        if self.account_id is not None:
            object.__setattr__(
                self,
                "account_id",
                _require_non_empty_str(self.account_id, "account_id"),
            )
        if self.user_id is not None:
            object.__setattr__(
                self,
                "user_id",
                _require_non_empty_str(self.user_id, "user_id"),
            )
        for field_name in (
            "last_success_ns",
            "last_failure_ns",
            "expires_at_ns",
            "refresh_due_ns",
            "last_error_ns",
        ):
            value = getattr(self, field_name)
            if value is not None:
                object.__setattr__(
                    self,
                    field_name,
                    _require_int(value, field_name, min_value=0),
                )
        for field_name in (
            "login_count",
            "refresh_count",
            "consecutive_failures",
        ):
            value = getattr(self, field_name)
            object.__setattr__(
                self,
                field_name,
                _require_int(value, field_name, min_value=0),
            )
        if self.last_error is not None:
            object.__setattr__(
                self,
                "last_error",
                _require_non_empty_str(self.last_error, "last_error"),
            )
        if self.message is not None:
            object.__setattr__(
                self,
                "message",
                _require_non_empty_str(self.message, "message"),
            )
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "status": self.status,
            "enabled": self.enabled,
            "auth_required": self.auth_required,
            "authenticated": self.authenticated,
            "session_active": self.session_active,
            "account_id": self.account_id,
            "user_id": self.user_id,
            "last_success_ns": self.last_success_ns,
            "last_failure_ns": self.last_failure_ns,
            "expires_at_ns": self.expires_at_ns,
            "refresh_due_ns": self.refresh_due_ns,
            "login_count": self.login_count,
            "refresh_count": self.refresh_count,
            "consecutive_failures": self.consecutive_failures,
            "last_error": self.last_error,
            "last_error_ns": self.last_error_ns,
            "message": self.message,
            "metadata": dict(self.metadata),
        }

    def to_public_health_payload(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "status": self.status,
            "authenticated": self.authenticated,
            "session_active": self.session_active,
            "last_success_ns": self.last_success_ns,
            "last_failure_ns": self.last_failure_ns,
            "expires_at_ns": self.expires_at_ns,
            "refresh_due_ns": self.refresh_due_ns,
            "consecutive_failures": self.consecutive_failures,
            "last_error": self.last_error,
            "message": self.message,
        }

    def to_hash_fields(self, *, prefix: str = "") -> dict[str, str]:
        p = prefix
        return {
            f"{p}provider_id": self.provider_id,
            f"{p}status": self.status,
            f"{p}enabled": "1" if self.enabled else "0",
            f"{p}auth_required": "1" if self.auth_required else "0",
            f"{p}authenticated": "1" if self.authenticated else "0",
            f"{p}session_active": "1" if self.session_active else "0",
            f"{p}account_id": self.account_id or "",
            f"{p}user_id": self.user_id or "",
            f"{p}last_success_ns": "" if self.last_success_ns is None else str(self.last_success_ns),
            f"{p}last_failure_ns": "" if self.last_failure_ns is None else str(self.last_failure_ns),
            f"{p}expires_at_ns": "" if self.expires_at_ns is None else str(self.expires_at_ns),
            f"{p}refresh_due_ns": "" if self.refresh_due_ns is None else str(self.refresh_due_ns),
            f"{p}login_count": str(self.login_count),
            f"{p}refresh_count": str(self.refresh_count),
            f"{p}consecutive_failures": str(self.consecutive_failures),
            f"{p}last_error": self.last_error or "",
            f"{p}last_error_ns": "" if self.last_error_ns is None else str(self.last_error_ns),
            f"{p}message": self.message or "",
            f"{p}last_success_iso": _iso_from_ns(self.last_success_ns) or "",
            f"{p}last_failure_iso": _iso_from_ns(self.last_failure_ns) or "",
            f"{p}expires_at_iso": _iso_from_ns(self.expires_at_ns) or "",
            f"{p}refresh_due_iso": _iso_from_ns(self.refresh_due_ns) or "",
        }


# ============================================================================
# Built-in credentials providers
# ============================================================================


@dataclass(frozen=True, slots=True)
class StaticCredentialsProvider:
    """Static in-memory credentials provider for tests or controlled bootstraps."""

    credentials_by_provider: Mapping[str, Mapping[str, object]]

    def __post_init__(self) -> None:
        frozen: dict[str, Mapping[str, object]] = {}
        for provider_id, creds in self.credentials_by_provider.items():
            key = _require_literal(
                provider_id,
                "credentials_by_provider.key",
                allowed=_ALLOWED_PROVIDER_IDS,
            )
            frozen[key] = _freeze_mapping(dict(creds))
        object.__setattr__(self, "credentials_by_provider", _freeze_mapping(frozen))

    def get_credentials(
        self,
        provider_id: str,
        *,
        config: BrokerAuthConfig,
    ) -> Mapping[str, object]:
        provider_id = _require_literal(
            provider_id,
            "provider_id",
            allowed=_ALLOWED_PROVIDER_IDS,
        )
        creds = self.credentials_by_provider.get(provider_id)
        if creds is None or not creds:
            raise BrokerCredentialsError(f"no credentials configured for {provider_id}")
        return creds


@dataclass(frozen=True, slots=True)
class EnvCredentialsProvider:
    """
    Environment-backed credentials provider.

    Defaults to reading any populated variables under MME_<PROVIDER>_*.
    Example:
    - MME_DHAN_API_KEY
    - MME_DHAN_CLIENT_ID
    - MME_DHAN_ACCESS_TOKEN
    - MME_ZERODHA_API_KEY
    """

    required_fields_by_provider: Mapping[str, Sequence[str]] = field(default_factory=dict)
    optional_fields_by_provider: Mapping[str, Sequence[str]] = field(default_factory=dict)
    prefix_by_provider: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "required_fields_by_provider",
            _freeze_mapping(
                {
                    str(k): tuple(str(vv) for vv in v)
                    for k, v in dict(self.required_fields_by_provider).items()
                }
            ),
        )
        object.__setattr__(
            self,
            "optional_fields_by_provider",
            _freeze_mapping(
                {
                    str(k): tuple(str(vv) for vv in v)
                    for k, v in dict(self.optional_fields_by_provider).items()
                }
            ),
        )
        object.__setattr__(
            self,
            "prefix_by_provider",
            _freeze_mapping({str(k): str(v) for k, v in dict(self.prefix_by_provider).items()}),
        )

    def get_credentials(
        self,
        provider_id: str,
        *,
        config: BrokerAuthConfig,
    ) -> Mapping[str, object]:
        provider_id = _require_literal(
            provider_id,
            "provider_id",
            allowed=_ALLOWED_PROVIDER_IDS,
        )
        prefix = (
            config.credentials_env_prefix
            or self.prefix_by_provider.get(provider_id)
            or _build_default_env_prefix(provider_id)
        )

        required_fields = tuple(
            self.required_fields_by_provider.get(provider_id, ())
        )
        optional_fields = tuple(
            self.optional_fields_by_provider.get(
                provider_id,
                (
                    "API_KEY",
                    "CLIENT_ID",
                    "CLIENT_SECRET",
                    "ACCESS_TOKEN",
                    "REFRESH_TOKEN",
                    "REQUEST_TOKEN",
                    "USERNAME",
                    "PASSWORD",
                    "PIN",
                    "TOTP",
                    "APP_SECRET",
                ),
            )
        )

        credentials: dict[str, object] = {}
        for field_name in required_fields:
            env_name = f"{prefix}{field_name}"
            value = os.getenv(env_name)
            if value is None or not value.strip():
                raise BrokerCredentialsError(
                    f"missing required credential env var for {provider_id}: {env_name}"
                )
            credentials[field_name.lower()] = value.strip()

        for field_name in optional_fields:
            env_name = f"{prefix}{field_name}"
            value = os.getenv(env_name)
            if value is not None and value.strip():
                credentials[field_name.lower()] = value.strip()

        if not credentials:
            raise BrokerCredentialsError(
                f"no credentials discovered under env prefix {prefix!r} for {provider_id}"
            )
        return credentials


# ============================================================================
# Internal mutable state
# ============================================================================


@dataclass(slots=True)
class _AuthMutableState:
    session: AuthSessionMaterial | None = None
    status: str = _STATUS_UNAVAILABLE
    last_success_ns: int | None = None
    last_failure_ns: int | None = None
    last_error: str | None = None
    last_error_ns: int | None = None
    login_count: int = 0
    refresh_count: int = 0
    consecutive_failures: int = 0
    message: str | None = None


# ============================================================================
# Broker auth manager
# ============================================================================


class BrokerAuthManager:
    """
    Stateful broker-auth/session manager for one provider.

    Thread-safe for service-level usage.
    """

    def __init__(
        self,
        *,
        config: BrokerAuthConfig,
        credentials_provider: BrokerCredentialsProvider,
        session_client: BrokerSessionClient,
        now_ns_fn: Any = _now_ns,
    ) -> None:
        if not isinstance(config, BrokerAuthConfig):
            raise BrokerAuthValidationError(
                f"config must be BrokerAuthConfig, got {type(config).__name__}"
            )
        self._config = config
        self._credentials_provider = credentials_provider
        self._session_client = session_client
        self._now_ns_fn = now_ns_fn
        self._lock = RLock()
        self._state = _AuthMutableState(
            status=_STATUS_DISABLED if not config.enabled else _STATUS_UNAVAILABLE
        )

    @property
    def provider_id(self) -> str:
        return self._config.provider_id

    @property
    def config(self) -> BrokerAuthConfig:
        return self._config

    def snapshot(self, *, now_ns: int | None = None) -> BrokerAuthSnapshot:
        with self._lock:
            return self._build_snapshot_locked(now_ns=now_ns)

    def ensure_authenticated(
        self,
        *,
        force_refresh: bool = False,
        now_ns: int | None = None,
    ) -> BrokerAuthSnapshot:
        with self._lock:
            current_now_ns = self._resolve_now_ns(now_ns)

            if not self._config.enabled:
                self._state.status = _STATUS_DISABLED
                self._state.message = "provider auth disabled by config"
                return self._build_snapshot_locked(now_ns=current_now_ns)

            if not self._config.auth_required:
                self._state.status = _STATUS_HEALTHY
                self._state.message = "provider auth not required by config"
                return self._build_snapshot_locked(now_ns=current_now_ns)

            if (
                not force_refresh
                and self._state.session is not None
                and not self._state.session.is_expired(now_ns=current_now_ns)
                and not self._state.session.refresh_due(
                    now_ns=current_now_ns,
                    refresh_lead_seconds=self._config.refresh_lead_seconds,
                )
            ):
                self._state.status = _STATUS_HEALTHY
                self._state.message = "active provider session reused"
                return self._build_snapshot_locked(now_ns=current_now_ns)

            if self._backoff_active_locked(now_ns=current_now_ns):
                snapshot = self._build_snapshot_locked(now_ns=current_now_ns)
                raise BrokerSessionUnavailableError(
                    snapshot.message or "broker auth backoff active"
                )

            credentials = self._load_credentials_locked()

            refresh_attempted = False
            if (
                self._state.session is not None
                and self._config.refresh_supported
                and self._state.session.refresh_token is not None
                and (
                    force_refresh
                    or self._state.session.refresh_due(
                        now_ns=current_now_ns,
                        refresh_lead_seconds=self._config.refresh_lead_seconds,
                    )
                    or self._state.session.is_expired(now_ns=current_now_ns)
                )
            ):
                refresh_attempted = True
                try:
                    refreshed = self._session_client.refresh(
                        self._state.session,
                        credentials,
                        config=self._config,
                        now_ns=current_now_ns,
                    )
                except Exception as exc:
                    self._mark_failure_locked(
                        error=BrokerRefreshError(_safe_message(exc)),
                        now_ns=current_now_ns,
                        keep_existing_session_if_valid=True,
                    )
                else:
                    self._apply_session_locked(
                        session=refreshed,
                        now_ns=current_now_ns,
                        refreshed=True,
                    )
                    return self._build_snapshot_locked(now_ns=current_now_ns)

            try:
                logged_in = self._session_client.login(
                    credentials,
                    config=self._config,
                    now_ns=current_now_ns,
                )
            except Exception as exc:
                error_cls = BrokerLoginError
                if refresh_attempted:
                    error_cls = BrokerRefreshError
                self._mark_failure_locked(
                    error=error_cls(_safe_message(exc)),
                    now_ns=current_now_ns,
                    keep_existing_session_if_valid=True,
                )
                snapshot = self._build_snapshot_locked(now_ns=current_now_ns)
                raise BrokerSessionUnavailableError(
                    snapshot.message or "broker authentication failed"
                ) from exc

            self._apply_session_locked(
                session=logged_in,
                now_ns=current_now_ns,
                refreshed=False,
            )
            return self._build_snapshot_locked(now_ns=current_now_ns)

    def invalidate(
        self,
        *,
        reason: str = "session invalidated",
        now_ns: int | None = None,
    ) -> BrokerAuthSnapshot:
        with self._lock:
            current_now_ns = self._resolve_now_ns(now_ns)
            self._state.session = None
            self._state.status = _STATUS_UNAVAILABLE if self._config.enabled else _STATUS_DISABLED
            self._state.message = _require_non_empty_str(reason, "reason")
            self._state.last_error = self._state.message
            self._state.last_error_ns = current_now_ns
            return self._build_snapshot_locked(now_ns=current_now_ns)

    def logout(
        self,
        *,
        revoke_remote: bool = False,
        now_ns: int | None = None,
    ) -> BrokerAuthSnapshot:
        with self._lock:
            current_now_ns = self._resolve_now_ns(now_ns)
            if revoke_remote and self._state.session is not None:
                try:
                    self._session_client.revoke(
                        self._state.session,
                        config=self._config,
                        now_ns=current_now_ns,
                    )
                except Exception as exc:
                    self._mark_failure_locked(
                        error=BrokerAuthError(f"session revoke failed: {_safe_message(exc)}"),
                        now_ns=current_now_ns,
                        keep_existing_session_if_valid=False,
                    )
                    raise
            self._state.session = None
            self._state.status = _STATUS_UNAVAILABLE if self._config.enabled else _STATUS_DISABLED
            self._state.message = "session logged out"
            return self._build_snapshot_locked(now_ns=current_now_ns)

    def get_access_token(
        self,
        *,
        ensure_authenticated: bool = True,
        now_ns: int | None = None,
    ) -> str:
        with self._lock:
            current_now_ns = self._resolve_now_ns(now_ns)
        if ensure_authenticated:
            self.ensure_authenticated(now_ns=current_now_ns)
        with self._lock:
            if self._state.session is None or self._state.session.is_expired(now_ns=current_now_ns):
                raise BrokerSessionUnavailableError(
                    f"no active session available for {self._config.provider_id}"
                )
            return self._state.session.access_token

    def get_session_material(
        self,
        *,
        ensure_authenticated: bool = True,
        now_ns: int | None = None,
    ) -> AuthSessionMaterial:
        with self._lock:
            current_now_ns = self._resolve_now_ns(now_ns)
        if ensure_authenticated:
            self.ensure_authenticated(now_ns=current_now_ns)
        with self._lock:
            if self._state.session is None or self._state.session.is_expired(now_ns=current_now_ns):
                raise BrokerSessionUnavailableError(
                    f"no active session available for {self._config.provider_id}"
                )
            return self._state.session

    def build_public_health_payload(
        self,
        *,
        now_ns: int | None = None,
    ) -> dict[str, Any]:
        return self.snapshot(now_ns=now_ns).to_public_health_payload()

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------

    def _resolve_now_ns(self, now_ns: int | None) -> int:
        if now_ns is None:
            value = self._now_ns_fn()
        else:
            value = now_ns
        return _require_int(value, "now_ns", min_value=0)

    def _load_credentials_locked(self) -> Mapping[str, object]:
        creds = self._credentials_provider.get_credentials(
            self._config.provider_id,
            config=self._config,
        )
        if not isinstance(creds, Mapping) or not creds:
            raise BrokerCredentialsError(
                f"credentials provider returned no usable credentials for {self._config.provider_id}"
            )
        return creds

    def _backoff_active_locked(self, *, now_ns: int) -> bool:
        if self._state.last_failure_ns is None:
            return False
        backoff_ns = int(self._config.failure_backoff_seconds * 1_000_000_000)
        if backoff_ns <= 0:
            return False
        if (now_ns - self._state.last_failure_ns) < backoff_ns:
            remaining_ns = backoff_ns - (now_ns - self._state.last_failure_ns)
            self._state.message = (
                f"broker auth backoff active for {self._config.provider_id}; "
                f"retry after {remaining_ns / 1_000_000_000:.3f}s"
            )
            if (
                self._state.session is not None
                and not self._state.session.is_expired(now_ns=now_ns)
            ):
                self._state.status = _STATUS_DEGRADED
                return False
            self._state.status = _STATUS_AUTH_FAILED
            return True
        return False

    def _apply_session_locked(
        self,
        *,
        session: AuthSessionMaterial,
        now_ns: int,
        refreshed: bool,
    ) -> None:
        if not isinstance(session, AuthSessionMaterial):
            raise BrokerAuthValidationError(
                f"session client must return AuthSessionMaterial, got {type(session).__name__}"
            )

        normalized_session = session
        if normalized_session.issued_at_ns is None:
            normalized_session = AuthSessionMaterial(
                access_token=normalized_session.access_token,
                refresh_token=normalized_session.refresh_token,
                session_id=normalized_session.session_id,
                issued_at_ns=now_ns,
                expires_at_ns=normalized_session.expires_at_ns,
                account_id=normalized_session.account_id or self._config.account_id,
                user_id=normalized_session.user_id or self._config.user_id,
                metadata=normalized_session.metadata,
            )

        if (
            normalized_session.expires_at_ns is None
            and self._config.session_ttl_seconds is not None
        ):
            normalized_session = AuthSessionMaterial(
                access_token=normalized_session.access_token,
                refresh_token=normalized_session.refresh_token,
                session_id=normalized_session.session_id,
                issued_at_ns=normalized_session.issued_at_ns,
                expires_at_ns=(
                    normalized_session.issued_at_ns
                    + int(self._config.session_ttl_seconds * 1_000_000_000)
                ),
                account_id=normalized_session.account_id,
                user_id=normalized_session.user_id,
                metadata=normalized_session.metadata,
            )

        self._state.session = normalized_session
        self._state.status = _STATUS_HEALTHY
        self._state.last_success_ns = now_ns
        self._state.last_error = None
        self._state.last_error_ns = None
        self._state.message = (
            "provider session refreshed successfully"
            if refreshed
            else "provider session authenticated successfully"
        )
        self._state.consecutive_failures = 0
        if refreshed:
            self._state.refresh_count += 1
        else:
            self._state.login_count += 1

    def _mark_failure_locked(
        self,
        *,
        error: Exception,
        now_ns: int,
        keep_existing_session_if_valid: bool,
    ) -> None:
        message = _safe_message(error)
        self._state.last_failure_ns = now_ns
        self._state.last_error = message
        self._state.last_error_ns = now_ns
        self._state.consecutive_failures += 1

        session_still_valid = (
            keep_existing_session_if_valid
            and self._state.session is not None
            and not self._state.session.is_expired(now_ns=now_ns)
        )

        if session_still_valid:
            self._state.status = _STATUS_DEGRADED
            self._state.message = (
                f"provider auth operation failed but existing session remains usable: {message}"
            )
            return

        self._state.session = None
        self._state.status = _STATUS_AUTH_FAILED
        self._state.message = f"provider auth failed: {message}"

    def _build_snapshot_locked(self, *, now_ns: int | None) -> BrokerAuthSnapshot:
        current_now_ns = self._resolve_now_ns(now_ns)
        status = self._state.status
        authenticated = False
        session_active = False
        expires_at_ns: int | None = None
        refresh_due_ns: int | None = None
        account_id = self._config.account_id
        user_id = self._config.user_id

        if not self._config.enabled:
            status = _STATUS_DISABLED
        elif not self._config.auth_required:
            status = _STATUS_HEALTHY
            authenticated = True
        elif self._state.session is not None:
            expires_at_ns = self._state.session.expires_at_ns
            account_id = self._state.session.account_id or account_id
            user_id = self._state.session.user_id or user_id

            if self._state.session.is_expired(now_ns=current_now_ns):
                session_active = False
                authenticated = False
                if status not in (_STATUS_AUTH_FAILED, _STATUS_DISABLED):
                    status = _STATUS_UNAVAILABLE
            else:
                session_active = True
                authenticated = True
                if status not in (_STATUS_DEGRADED, _STATUS_AUTH_FAILED):
                    status = _STATUS_HEALTHY

            if expires_at_ns is not None:
                refresh_due_ns = (
                    expires_at_ns
                    - int(self._config.refresh_lead_seconds * 1_000_000_000)
                )

        return BrokerAuthSnapshot(
            provider_id=self._config.provider_id,
            status=status,
            enabled=self._config.enabled,
            auth_required=self._config.auth_required,
            authenticated=authenticated,
            session_active=session_active,
            account_id=account_id,
            user_id=user_id,
            last_success_ns=self._state.last_success_ns,
            last_failure_ns=self._state.last_failure_ns,
            expires_at_ns=expires_at_ns,
            refresh_due_ns=refresh_due_ns,
            login_count=self._state.login_count,
            refresh_count=self._state.refresh_count,
            consecutive_failures=self._state.consecutive_failures,
            last_error=self._state.last_error,
            last_error_ns=self._state.last_error_ns,
            message=self._state.message,
            metadata={
                "last_success_iso": _iso_from_ns(self._state.last_success_ns),
                "last_failure_iso": _iso_from_ns(self._state.last_failure_ns),
                "expires_at_iso": _iso_from_ns(expires_at_ns),
                "refresh_due_iso": _iso_from_ns(refresh_due_ns),
            },
        )


# ============================================================================
# Convenience builders
# ============================================================================


def build_broker_auth_manager_from_yaml(
    *,
    path: str | Path,
    credentials_provider: BrokerCredentialsProvider,
    session_client: BrokerSessionClient,
    provider_id: str | None = None,
    now_ns_fn: Any = _now_ns,
) -> BrokerAuthManager:
    config = BrokerAuthConfig.from_yaml_file(path, provider_id=provider_id)
    return BrokerAuthManager(
        config=config,
        credentials_provider=credentials_provider,
        session_client=session_client,
        now_ns_fn=now_ns_fn,
    )


__all__ = [
    "AuthSessionMaterial",
    "BrokerAuthConfig",
    "BrokerAuthError",
    "BrokerAuthManager",
    "BrokerAuthSnapshot",
    "BrokerAuthValidationError",
    "BrokerCredentialsError",
    "BrokerCredentialsProvider",
    "BrokerLoginError",
    "BrokerRefreshError",
    "BrokerSessionClient",
    "BrokerSessionUnavailableError",
    "EnvCredentialsProvider",
    "StaticCredentialsProvider",
    "build_broker_auth_manager_from_yaml",
]
