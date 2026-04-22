"""
app/mme_scalpx/integrations/login.py

Freeze-grade dual-broker login/session integration for ScalpX MME.

Responsibilities
----------------
- load static broker credentials from integrations.token_store when available
- auto-load broker-specific env files for Zerodha and Dhan
- accept environment/CLI fallbacks for provider-specific credentials
- perform Zerodha request_token -> access_token session exchange
- reuse saved Zerodha access token before interactive login
- perform Dhan access-token verification and optional generate/renew flows
- reuse broker-specific Dhan session token from session.env
- persist broker-specific session.env for Zerodha and Dhan
- persist canonical compatibility token/session state through integrations.token_store
- provide one thin operator entrypoint for:
  - Zerodha only
  - Dhan only
  - both brokers

Non-responsibilities
--------------------
- no market-data subscription
- no order placement
- no Redis state publication
- no runtime supervision ownership
- no composition-root ownership
- no instrument resolution
- no provider-runtime role resolution
- no token refresh daemon ownership

Design rules
------------
- broker-specific session reuse must not depend on a shared single-slot token store
- token_store remains a compatibility persistence surface
- broker-specific session.env is the primary reuse surface for dual-broker plogin
- this module is a thin operator/bootstrap wrapper; it does not replace broker_auth.py
- this module does not guess expiry semantics unless they are explicitly known
- no raw secrets are printed
- default operator behavior is to attempt both brokers when no specific broker flag is passed
- broker-specific env preload is convenience only and never overrides already-exported shell vars
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

import requests

from app.mme_scalpx.integrations.token_store import (
    BrokerApiConfig,
    BrokerTokenState,
    SecretFileFormatError,
    SecretFileMissingError,
    TokenStoreError,
    load_api_config,
    load_token_state,
    save_token_state,
)

try:
    from kiteconnect import KiteConnect  # type: ignore
except Exception:  # pragma: no cover
    KiteConnect = None  # type: ignore


VERSION = "mme-login-dual-broker-v3-broker-session-freeze"
DEFAULT_ZERODHA_LTP_PROBE_SYMBOLS = ("NSE:NIFTY 50",)

DHAN_GENERATE_TOKEN_URL = "https://auth.dhan.co/app/generateAccessToken"
DHAN_RENEW_TOKEN_URL = "https://api.dhan.co/v2/RenewToken"
DHAN_VERIFY_FUNDS_URL = "https://api.dhan.co/v2/fundlimit"

logger = logging.getLogger("scalpx.mme.integrations.login")


class LoginError(RuntimeError):
    """Base login integration error."""


class StartupValidationError(LoginError):
    """Raised for fail-fast local startup validation errors."""


class BrokerAuthError(LoginError):
    """Raised when broker authentication or verification fails."""


def setup_logging(level: str = "INFO") -> None:
    if logger.handlers:
        return
    logger.setLevel(getattr(logging, str(level).upper(), logging.INFO))
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
    )
    logger.addHandler(handler)


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _first_non_empty(*values: Any) -> str:
    for value in values:
        text = _normalize_str(value)
        if text:
            return text
    return ""


def _env(*keys: str) -> str:
    for key in keys:
        value = os.getenv(key, "").strip()
        if value:
            return value
    return ""


def _safe_dict(data: Mapping[str, Any] | None) -> dict[str, Any]:
    return {} if data is None else {str(k): v for k, v in data.items()}


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _broker_secret_dir(broker: str) -> Path:
    return _project_root() / "common" / "secrets" / "brokers" / broker.strip().lower()


def _broker_session_env_path(broker: str) -> Path:
    return _broker_secret_dir(broker) / "session.env"


def _resolve_broker_env_candidates(broker: str) -> tuple[Path, ...]:
    root = _project_root()
    broker = broker.strip().lower()
    return (
        root / "common" / "secrets" / "brokers" / broker / "credentials.env",
        root / "common" / "secrets" / "brokers" / broker / "runtime.env",
        root / "common" / "secrets" / "brokers" / broker / "session.env",
        root / "common" / "secrets" / "brokers" / broker / ".env",
        root / "etc" / "brokers" / f"{broker}.env",
    )


def _parse_env_line(line: str, *, path: Path, lineno: int) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None

    if stripped.startswith("export "):
        stripped = stripped[len("export ") :].strip()

    if "=" not in stripped:
        raise StartupValidationError(
            f"invalid env line without '=' in {path}:{lineno}"
        )

    key, value = stripped.split("=", 1)
    key = key.strip()
    if not key:
        raise StartupValidationError(f"empty env key in {path}:{lineno}")

    value = value.strip()
    if value and len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]

    return key, value


def _load_env_file(path: Path, *, override: bool = False) -> bool:
    if not path.exists():
        return False
    if not path.is_file():
        raise StartupValidationError(f"env path is not a file: {path}")

    loaded_any = False
    content = path.read_text(encoding="utf-8")
    for lineno, raw_line in enumerate(content.splitlines(), start=1):
        parsed = _parse_env_line(raw_line, path=path, lineno=lineno)
        if parsed is None:
            continue
        key, value = parsed
        if override or key not in os.environ:
            os.environ[key] = value
        loaded_any = True
    return loaded_any


def preload_broker_env_files(
    brokers: Sequence[str],
    *,
    override: bool = False,
) -> list[str]:
    loaded_paths: list[str] = []
    seen: set[str] = set()

    for broker in brokers:
        for candidate in _resolve_broker_env_candidates(broker):
            candidate_str = str(candidate)
            if candidate_str in seen:
                continue
            seen.add(candidate_str)
            try:
                loaded = _load_env_file(candidate, override=override)
            except Exception as exc:
                logger.warning("broker env preload skipped for %s: %s", candidate, exc)
                continue
            if loaded:
                loaded_paths.append(candidate_str)

    if loaded_paths:
        logger.info("loaded broker env files: %s", ", ".join(loaded_paths))
    return loaded_paths


def _write_broker_session_env(
    broker: str,
    variables: Mapping[str, str],
) -> Path:
    target = _broker_session_env_path(broker)
    target.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        f"{key}={value}"
        for key, value in variables.items()
        if _normalize_str(key) and _normalize_str(value)
    ]
    if not lines:
        raise StartupValidationError(
            f"no non-empty session variables to write for broker={broker!r}"
        )

    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


def resolve_requested_brokers_preparse(argv: Optional[Sequence[str]]) -> tuple[str, ...]:
    args = tuple(argv or ())
    wants_zerodha = "--zerodha" in args
    wants_dhan = "--dhan" in args

    if wants_zerodha and not wants_dhan:
        return ("zerodha",)
    if wants_dhan and not wants_zerodha:
        return ("dhan",)
    if wants_dhan and wants_zerodha:
        return ("zerodha", "dhan")
    return ("zerodha", "dhan")


def _try_load_api_config() -> BrokerApiConfig | None:
    try:
        return load_api_config()
    except (SecretFileMissingError, SecretFileFormatError, TokenStoreError) as exc:
        logger.info("api config unavailable via token_store: %s", exc)
        return None


@dataclass(frozen=True)
class LoginResult:
    broker: str
    ok: bool
    user_id: Optional[str]
    access_token_present: bool
    login_time_utc: str
    detail: str = ""

    def render_line(self) -> str:
        return (
            f"{self.broker}: ok={self.ok} "
            f"user={self.user_id or '?'} "
            f"login_time_utc={self.login_time_utc} "
            f"access_token={'present' if self.access_token_present else 'missing'} "
            f"detail={self.detail or '-'}"
        )


@dataclass(frozen=True)
class ZerodhaLoginConfig:
    api_key: str
    api_secret: str
    user_id: Optional[str]
    access_token: Optional[str]


@dataclass(frozen=True)
class DhanLoginConfig:
    client_id: str
    access_token: Optional[str]
    api_key: Optional[str]
    api_secret: Optional[str]
    pin: Optional[str]
    totp: Optional[str]
    user_id: Optional[str]


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ScalpX MME dual-broker login/session integration"
    )
    parser.add_argument("--zerodha", action="store_true", help="Run Zerodha login flow")
    parser.add_argument("--dhan", action="store_true", help="Run Dhan login flow")

    parser.add_argument(
        "--request-token",
        default=os.getenv("ZERODHA_REQUEST_TOKEN", "").strip(),
        help="Zerodha request_token. If omitted, interactive prompt is used.",
    )
    parser.add_argument(
        "--zerodha-access-token",
        default=_env("ZERODHA_ACCESS_TOKEN", "MME_ZERODHA_ACCESS_TOKEN"),
        help="Saved Zerodha access token for reuse before interactive login.",
    )
    parser.add_argument(
        "--show-login-url",
        action="store_true",
        help="Print Zerodha login URL before request_token prompt.",
    )
    parser.add_argument(
        "--no-ltp-verify",
        action="store_true",
        help="Skip optional Zerodha LTP verification after profile() succeeds.",
    )

    parser.add_argument(
        "--dhan-access-token",
        default=_env("DHAN_ACCESS_TOKEN", "MME_DHAN_ACCESS_TOKEN"),
        help="Dhan access token. If omitted, env or generate/renew flow is used.",
    )
    parser.add_argument(
        "--dhan-client-id",
        default=_env("DHAN_CLIENT_ID", "MME_DHAN_CLIENT_ID"),
        help="Dhan client id.",
    )
    parser.add_argument(
        "--dhan-api-key",
        default=_env("DHAN_API_KEY", "MME_DHAN_API_KEY"),
        help="Optional Dhan API key.",
    )
    parser.add_argument(
        "--dhan-api-secret",
        default=_env("DHAN_API_SECRET", "MME_DHAN_API_SECRET"),
        help="Optional Dhan API secret.",
    )
    parser.add_argument(
        "--dhan-pin",
        default=_env("DHAN_PIN", "MME_DHAN_PIN"),
        help="Optional Dhan pin for generate-token flow.",
    )
    parser.add_argument(
        "--dhan-totp",
        default=_env("DHAN_TOTP", "MME_DHAN_TOTP"),
        help="Optional Dhan TOTP for generate-token flow.",
    )
    parser.add_argument(
        "--dhan-generate-token",
        action="store_true",
        help="Generate Dhan access token using client id + pin + totp.",
    )
    parser.add_argument(
        "--dhan-renew-token",
        action="store_true",
        help="Renew active Dhan access token for another validity window.",
    )
    parser.add_argument(
        "--no-dhan-verify",
        action="store_true",
        help="Skip Dhan fundlimit verification after token acquisition.",
    )
    parser.add_argument(
        "--log-level",
        default=os.getenv("LOG_LEVEL", "INFO"),
        help="Logging level",
    )
    return parser.parse_args(argv)


def resolve_requested_brokers(args: argparse.Namespace) -> tuple[str, ...]:
    requested: list[str] = []
    if bool(args.zerodha):
        requested.append("zerodha")
    if bool(args.dhan):
        requested.append("dhan")
    if not requested:
        requested = ["zerodha", "dhan"]
    return tuple(requested)


# ============================================================================
# Zerodha
# ============================================================================


def validate_api_config_for_zerodha(api: BrokerApiConfig) -> ZerodhaLoginConfig:
    broker = _normalize_str(api.broker).lower()
    if broker != "zerodha":
        raise StartupValidationError(
            f"api.json broker must be 'zerodha' for Zerodha login, got: {api.broker!r}"
        )
    if not _normalize_str(api.api_key):
        raise StartupValidationError("api.json missing non-empty api_key for Zerodha")
    if not _normalize_str(api.api_secret):
        raise StartupValidationError("api.json missing non-empty api_secret for Zerodha")
    user_id = _normalize_str(api.user_id) or None
    return ZerodhaLoginConfig(
        api_key=_normalize_str(api.api_key),
        api_secret=_normalize_str(api.api_secret),
        user_id=user_id,
        access_token=_env("ZERODHA_ACCESS_TOKEN", "MME_ZERODHA_ACCESS_TOKEN") or None,
    )


def resolve_zerodha_login_config(
    api: BrokerApiConfig | None,
    args: argparse.Namespace,
) -> ZerodhaLoginConfig:
    env_access_token = _first_non_empty(
        args.zerodha_access_token,
        _env("ZERODHA_ACCESS_TOKEN", "MME_ZERODHA_ACCESS_TOKEN"),
    ) or None

    if api is not None:
        try:
            cfg = validate_api_config_for_zerodha(api)
            return ZerodhaLoginConfig(
                api_key=cfg.api_key,
                api_secret=cfg.api_secret,
                user_id=cfg.user_id,
                access_token=env_access_token,
            )
        except StartupValidationError:
            logger.info("api.json is not a Zerodha config; falling back to env")

    api_key = _env("ZERODHA_API_KEY", "MME_ZERODHA_API_KEY")
    api_secret = _env("ZERODHA_API_SECRET", "MME_ZERODHA_API_SECRET")
    user_id = _env("ZERODHA_USER_ID", "MME_ZERODHA_USER_ID") or None
    if not api_key:
        raise StartupValidationError("missing Zerodha api_key in api.json or environment")
    if not api_secret:
        raise StartupValidationError("missing Zerodha api_secret in api.json or environment")
    return ZerodhaLoginConfig(
        api_key=api_key,
        api_secret=api_secret,
        user_id=user_id,
        access_token=env_access_token,
    )


def get_zerodha_request_token(
    kite: Any,
    provided_request_token: str,
    show_login_url: bool,
) -> str:
    token = _normalize_str(provided_request_token)
    if token:
        logger.info("Using Zerodha request_token from argument/environment")
        return token

    if KiteConnect is None:
        raise BrokerAuthError("kiteconnect is required for Zerodha login flow")

    if show_login_url:
        print("Open Zerodha login URL:")
        print(kite.login_url())

    if not sys.stdin.isatty():
        raise BrokerAuthError(
            "Zerodha request_token not provided and interactive prompt unavailable"
        )

    print("Open Zerodha login URL and complete login:")
    print(kite.login_url())
    entered = input("Paste Zerodha request_token: ").strip()
    if not entered:
        raise BrokerAuthError("empty Zerodha request_token")
    return entered


def verify_zerodha_profile(kite: Any, expected_user_id: Optional[str]) -> dict[str, Any]:
    try:
        profile = kite.profile()
    except Exception as exc:
        raise BrokerAuthError(f"Zerodha profile() verification failed: {exc}") from exc

    if not isinstance(profile, dict):
        raise BrokerAuthError("Zerodha profile() returned non-dict payload")

    user_id = _normalize_str(profile.get("user_id"))
    if not user_id:
        raise BrokerAuthError("Zerodha profile() payload missing user_id")

    if expected_user_id and user_id != expected_user_id:
        raise BrokerAuthError(
            f"Zerodha authenticated user_id mismatch: expected={expected_user_id} got={user_id}"
        )
    return profile


def verify_zerodha_ltp_optional(kite: Any, enabled: bool) -> None:
    if not enabled:
        return
    try:
        payload = kite.ltp(list(DEFAULT_ZERODHA_LTP_PROBE_SYMBOLS))
    except Exception as exc:
        raise BrokerAuthError(f"Zerodha ltp() probe failed: {exc}") from exc

    if not isinstance(payload, dict) or not payload:
        raise BrokerAuthError("Zerodha ltp() probe returned empty/non-dict payload")


def build_zerodha_token_state(
    cfg: ZerodhaLoginConfig,
    session_payload: Mapping[str, Any],
    profile: Mapping[str, Any],
) -> BrokerTokenState:
    access_token = _normalize_str(session_payload.get("access_token"))
    if not access_token:
        raise BrokerAuthError("Zerodha generate_session() payload missing access_token")

    user_id = _normalize_str(profile.get("user_id")) or (cfg.user_id or "")
    public_token = _normalize_str(session_payload.get("public_token"))
    login_time = now_utc_iso()

    metadata: dict[str, Any] = {
        "version": VERSION,
        "provider_id": "ZERODHA",
        "user_id": user_id,
        "public_token": public_token,
        "login_time_utc": login_time,
    }

    for field in ("user_name", "email", "user_shortname"):
        value = _normalize_str(profile.get(field))
        if value:
            metadata[field] = value

    return BrokerTokenState(
        broker="zerodha",
        access_token=access_token,
        refresh_token="",
        issued_at=login_time,
        expires_at="",
        session_id=public_token,
        metadata=metadata,
    )


def _save_zerodha_broker_session(access_token: str) -> Path:
    return _write_broker_session_env(
        "zerodha",
        {
            "ZERODHA_ACCESS_TOKEN": access_token,
        },
    )


def _save_dhan_broker_session(access_token: str) -> Path:
    return _write_broker_session_env(
        "dhan",
        {
            "DHAN_ACCESS_TOKEN": access_token,
        },
    )


def validate_token_state_for_zerodha(state: BrokerTokenState) -> None:
    if _normalize_str(state.broker).lower() != "zerodha":
        raise StartupValidationError(
            f"tokens.json broker must be 'zerodha' for Zerodha reuse, got: {state.broker!r}"
        )
    if not _normalize_str(state.access_token):
        raise StartupValidationError("tokens.json missing non-empty Zerodha access_token")


def try_reuse_saved_zerodha_session(
    cfg: ZerodhaLoginConfig,
    *,
    do_ltp_verify: bool,
) -> LoginResult | None:
    if KiteConnect is None:
        raise BrokerAuthError("kiteconnect is required by Zerodha login flow")

    candidate_tokens: list[tuple[str, str]] = []

    env_token = _normalize_str(cfg.access_token)
    has_broker_session_env = bool(env_token)
    if has_broker_session_env:
        candidate_tokens.append(("broker_session_env", env_token))

    if not has_broker_session_env:
        try:
            state = load_token_state()
            validate_token_state_for_zerodha(state)
            token_store_token = _normalize_str(state.access_token)
            if token_store_token:
                candidate_tokens.append(("shared_token_store", token_store_token))
        except (
            SecretFileMissingError,
            SecretFileFormatError,
            TokenStoreError,
            StartupValidationError,
        ) as exc:
            logger.info("saved Zerodha token reuse unavailable from shared token store: %s", exc)

    for source_name, candidate_token in candidate_tokens:
        kite = KiteConnect(api_key=cfg.api_key)
        kite.set_access_token(candidate_token)

        try:
            profile = verify_zerodha_profile(kite, expected_user_id=cfg.user_id)
            verify_zerodha_ltp_optional(kite, enabled=do_ltp_verify)
        except BrokerAuthError as exc:
            logger.info(
                "saved Zerodha token reuse failed from %s; trying next source: %s",
                source_name,
                exc,
            )
            continue

        login_time = now_utc_iso()
        user_id = _normalize_str(profile.get("user_id")) or (cfg.user_id or "")

        metadata: dict[str, Any] = {
            "version": VERSION,
            "provider_id": "ZERODHA",
            "user_id": user_id,
            "login_time_utc": login_time,
            "reused_saved_token": True,
            "reuse_source": source_name,
        }

        for field in ("user_name", "email", "user_shortname"):
            value = _normalize_str(profile.get(field))
            if value:
                metadata[field] = value

        refreshed_state = BrokerTokenState(
            broker="zerodha",
            access_token=candidate_token,
            refresh_token="",
            issued_at=login_time,
            expires_at="",
            session_id="",
            metadata=metadata,
        )
        save_token_state(refreshed_state)
        _save_zerodha_broker_session(candidate_token)

        return LoginResult(
            broker="zerodha",
            ok=True,
            user_id=user_id or None,
            access_token_present=True,
            login_time_utc=login_time,
            detail=f"reused_saved_token[{source_name}],verified via profile() and optional ltp()",
        )

    return None


def authenticate_zerodha(
    cfg: ZerodhaLoginConfig,
    request_token: str,
    *,
    show_login_url: bool,
    do_ltp_verify: bool,
) -> LoginResult:
    if KiteConnect is None:
        raise BrokerAuthError("kiteconnect is required by Zerodha login flow")

    if not _normalize_str(request_token):
        reused = try_reuse_saved_zerodha_session(
            cfg,
            do_ltp_verify=do_ltp_verify,
        )
        if reused is not None:
            return reused

    kite = KiteConnect(api_key=cfg.api_key)
    token = get_zerodha_request_token(
        kite=kite,
        provided_request_token=request_token,
        show_login_url=show_login_url,
    )

    try:
        session_payload = kite.generate_session(token, api_secret=cfg.api_secret)
    except Exception as exc:
        raise BrokerAuthError(f"Zerodha generate_session() failed: {exc}") from exc

    if not isinstance(session_payload, dict):
        raise BrokerAuthError("Zerodha generate_session() returned non-dict payload")

    access_token = _normalize_str(session_payload.get("access_token"))
    if not access_token:
        raise BrokerAuthError("Zerodha generate_session() payload missing access_token")

    kite.set_access_token(access_token)
    profile = verify_zerodha_profile(kite, expected_user_id=cfg.user_id)
    verify_zerodha_ltp_optional(kite, enabled=do_ltp_verify)

    state = build_zerodha_token_state(cfg, session_payload, profile)
    save_token_state(state)
    _save_zerodha_broker_session(access_token)

    result_user_id = _normalize_str(profile.get("user_id")) or cfg.user_id
    return LoginResult(
        broker="zerodha",
        ok=True,
        user_id=result_user_id,
        access_token_present=True,
        login_time_utc=state.issued_at,
        detail="verified via profile() and optional ltp()",
    )


# ============================================================================
# Dhan
# ============================================================================


def resolve_dhan_login_config(
    api: BrokerApiConfig | None,
    args: argparse.Namespace,
) -> DhanLoginConfig:
    api_key = (
        _normalize_str(getattr(api, "api_key", ""))
        if api and _normalize_str(getattr(api, "broker", "")).lower() == "dhan"
        else ""
    )
    api_secret = (
        _normalize_str(getattr(api, "api_secret", ""))
        if api and _normalize_str(getattr(api, "broker", "")).lower() == "dhan"
        else ""
    )
    user_id = (
        _normalize_str(getattr(api, "user_id", ""))
        if api and _normalize_str(getattr(api, "broker", "")).lower() == "dhan"
        else ""
    )

    client_id = _first_non_empty(
        args.dhan_client_id,
        user_id,
        _env("DHAN_USER_ID", "MME_DHAN_USER_ID"),
    )
    access_token = _first_non_empty(
        args.dhan_access_token,
        _env("DHAN_TOKEN", "MME_DHAN_TOKEN"),
    ) or None
    resolved_api_key = _first_non_empty(args.dhan_api_key, api_key) or None
    resolved_api_secret = _first_non_empty(args.dhan_api_secret, api_secret) or None
    pin = _first_non_empty(args.dhan_pin) or None
    totp = _first_non_empty(args.dhan_totp) or None
    resolved_user_id = _first_non_empty(user_id, client_id) or None

    if not client_id:
        raise StartupValidationError(
            "missing Dhan client_id in CLI, environment, or api.json"
        )

    return DhanLoginConfig(
        client_id=client_id,
        access_token=access_token,
        api_key=resolved_api_key,
        api_secret=resolved_api_secret,
        pin=pin,
        totp=totp,
        user_id=resolved_user_id,
    )


def generate_dhan_access_token_via_api(cfg: DhanLoginConfig) -> dict[str, Any]:
    if not cfg.pin:
        raise BrokerAuthError("Dhan pin is required for generate-token flow")
    if not cfg.totp:
        raise BrokerAuthError("Dhan TOTP is required for generate-token flow")

    payload = _http_json(
        "POST",
        DHAN_GENERATE_TOKEN_URL,
        params={
            "dhanClientId": cfg.client_id,
            "pin": cfg.pin,
            "totp": cfg.totp,
        },
    )
    if not isinstance(payload, Mapping):
        raise BrokerAuthError("Dhan generate-token response is not a mapping")

    access_token = _normalize_str(payload.get("accessToken"))
    if not access_token:
        raise BrokerAuthError("Dhan generate-token response missing accessToken")
    return dict(payload)


def renew_dhan_access_token(cfg: DhanLoginConfig, active_access_token: str) -> dict[str, Any]:
    if not _normalize_str(active_access_token):
        raise BrokerAuthError("Dhan renew-token requested but no active access token is available")

    payload = _http_json(
        "GET",
        DHAN_RENEW_TOKEN_URL,
        headers={
            "access-token": active_access_token,
            "dhanClientId": cfg.client_id,
        },
    )
    if not isinstance(payload, Mapping):
        raise BrokerAuthError("Dhan renew-token response is not a mapping")

    access_token = _normalize_str(
        payload.get("accessToken") or payload.get("access_token")
    )
    if not access_token:
        payload = dict(payload)
        payload["accessToken"] = active_access_token
    return dict(payload)


def verify_dhan_access_token(
    cfg: DhanLoginConfig,
    access_token: str,
    *,
    enabled: bool,
) -> dict[str, Any]:
    if not enabled:
        return {"verification": "skipped"}

    payload = _http_json(
        "GET",
        DHAN_VERIFY_FUNDS_URL,
        headers={
            "access-token": access_token,
            "dhanClientId": cfg.client_id,
            "Content-Type": "application/json",
        },
    )
    return payload if isinstance(payload, Mapping) else {"raw": payload}


def build_dhan_token_state(
    cfg: DhanLoginConfig,
    *,
    access_token: str,
    expiry_time: str | None,
    session_payload: Mapping[str, Any] | None,
    verification_payload: Mapping[str, Any] | None,
) -> BrokerTokenState:
    login_time = now_utc_iso()
    session_payload = _safe_dict(session_payload)
    verification_payload = _safe_dict(verification_payload)

    metadata: dict[str, Any] = {
        "version": VERSION,
        "provider_id": "DHAN",
        "client_id": cfg.client_id,
        "login_time_utc": login_time,
    }

    for key in (
        "dhanClientId",
        "dhanClientName",
        "dhanClientUcc",
        "givenPowerOfAttorney",
    ):
        if key in session_payload and session_payload[key] not in ("", None):
            metadata[key] = session_payload[key]

    if verification_payload:
        metadata["verify_path"] = "fundlimit"
        metadata["verify_keys"] = sorted(str(k) for k in verification_payload.keys())

    return BrokerTokenState(
        broker="dhan",
        access_token=access_token,
        refresh_token="",
        issued_at=login_time,
        expires_at=_normalize_str(expiry_time),
        session_id=cfg.client_id,
        metadata=metadata,
    )


def authenticate_dhan(
    cfg: DhanLoginConfig,
    *,
    generate_token: bool,
    renew_token: bool,
    do_verify: bool,
) -> LoginResult:
    session_payload: dict[str, Any] | None = None
    verification_payload: dict[str, Any] | None = None

    access_token = _normalize_str(cfg.access_token)
    if generate_token:
        session_payload = generate_dhan_access_token_via_api(cfg)
        access_token = _normalize_str(session_payload.get("accessToken"))
    elif renew_token:
        if not access_token:
            raise BrokerAuthError(
                "Dhan renew-token flow requested but no active access token was supplied"
            )
        session_payload = renew_dhan_access_token(cfg, access_token)
        access_token = _normalize_str(
            session_payload.get("accessToken") or access_token
        )

    if not access_token:
        raise BrokerAuthError(
            "missing Dhan access token; provide --dhan-access-token or use --dhan-generate-token"
        )

    verification_payload = _safe_dict(
        verify_dhan_access_token(cfg, access_token, enabled=do_verify)
    )

    expiry_time = ""
    if session_payload is not None:
        expiry_time = _normalize_str(
            session_payload.get("expiryTime")
            or session_payload.get("expiresAt")
            or session_payload.get("expires_at")
        )

    state = build_dhan_token_state(
        cfg,
        access_token=access_token,
        expiry_time=expiry_time or None,
        session_payload=session_payload,
        verification_payload=verification_payload,
    )
    save_token_state(state)
    _save_dhan_broker_session(access_token)

    detail_parts: list[str] = []
    if generate_token:
        detail_parts.append("generated_token")
    elif renew_token:
        detail_parts.append("renewed_token")
    else:
        detail_parts.append("used_supplied_token")
    if do_verify:
        detail_parts.append("verified_via_fundlimit")
    else:
        detail_parts.append("verify_skipped")

    return LoginResult(
        broker="dhan",
        ok=True,
        user_id=cfg.user_id or cfg.client_id,
        access_token_present=True,
        login_time_utc=state.issued_at,
        detail=",".join(detail_parts),
    )


def _http_json(
    method: str,
    url: str,
    *,
    headers: Mapping[str, str] | None = None,
    params: Mapping[str, Any] | None = None,
    json_body: Any = None,
    timeout_s: int = 15,
) -> Any:
    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            headers=dict(headers or {}),
            params=dict(params or {}),
            json=json_body,
            timeout=timeout_s,
        )
    except Exception as exc:
        raise BrokerAuthError(f"HTTP request failed for {url}: {exc}") from exc

    text = response.text.strip()
    payload: Any
    if text:
        try:
            payload = response.json()
        except Exception:
            payload = {"raw_text": text}
    else:
        payload = {}

    if response.status_code >= 400:
        raise BrokerAuthError(
            f"HTTP {response.status_code} for {url}: {payload}"
        )
    return payload


# ============================================================================
# Orchestration
# ============================================================================


def run_requested_logins(args: argparse.Namespace) -> list[LoginResult]:
    api = _try_load_api_config()
    requested = resolve_requested_brokers(args)
    results: list[LoginResult] = []

    for broker in requested:
        logger.info("starting broker login flow: %s", broker)

        if broker == "zerodha":
            cfg = resolve_zerodha_login_config(api, args)
            result = authenticate_zerodha(
                cfg,
                request_token=args.request_token,
                show_login_url=bool(args.show_login_url),
                do_ltp_verify=not bool(args.no_ltp_verify),
            )
            results.append(result)
            continue

        if broker == "dhan":
            cfg = resolve_dhan_login_config(api, args)
            result = authenticate_dhan(
                cfg,
                generate_token=bool(args.dhan_generate_token),
                renew_token=bool(args.dhan_renew_token),
                do_verify=not bool(args.no_dhan_verify),
            )
            results.append(result)
            continue

        raise StartupValidationError(f"unsupported broker requested: {broker!r}")

    return results


def main(argv: Optional[list[str]] = None) -> int:
    setup_logging(os.getenv("LOG_LEVEL", "INFO"))
    preload_broker_env_files(resolve_requested_brokers_preparse(argv))

    args = parse_args(argv)
    setup_logging(args.log_level)

    try:
        results = run_requested_logins(args)
    except (
        SecretFileMissingError,
        SecretFileFormatError,
        TokenStoreError,
        StartupValidationError,
        BrokerAuthError,
        LoginError,
    ) as exc:
        logger.error("login failed: %s", exc)
        return 1
    except Exception as exc:  # pragma: no cover
        logger.error("unexpected login failure: %s", exc)
        return 1

    for result in results:
        print(result.render_line())

    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
