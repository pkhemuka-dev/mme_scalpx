"""
app/mme_scalpx/integrations/login.py

Freeze-grade Zerodha login/session integration for ScalpX MME.

Responsibilities
----------------
- load static broker credentials from integrations.token_store
- perform Zerodha request_token -> access_token session exchange
- verify authenticated session using profile()
- optionally probe LTP for a lightweight market-data auth check
- persist canonical token/session state through integrations.token_store

Non-responsibilities
--------------------
- no market-data subscription
- no order placement
- no Redis state publication
- no runtime supervision ownership
- no composition-root ownership
- no instrument resolution
- no multi-broker vault ownership

Design rules
------------
- api.json remains the authoritative static credential source
- tokens.json remains the authoritative runtime token/session store
- this module does not write ad hoc token files
- this module does not guess expiry semantics that are not explicitly known
- main.py remains the only composition root
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from app.mme_scalpx.integrations.token_store import (
    BrokerApiConfig,
    BrokerTokenState,
    SecretFileFormatError,
    SecretFileMissingError,
    TokenStoreError,
    load_api_config,
    save_token_state,
)

try:
    from kiteconnect import KiteConnect  # type: ignore
except Exception as exc:  # pragma: no cover
    raise RuntimeError(
        "kiteconnect is required by app.mme_scalpx.integrations.login"
    ) from exc


VERSION = "mme-login-zerodha-v1-freeze"
DEFAULT_LTP_PROBE_SYMBOLS = ("NSE:NIFTY 50",)

logger = logging.getLogger("scalpx.mme.integrations.login")


class LoginError(RuntimeError):
    """Base login integration error."""


class StartupValidationError(LoginError):
    """Raised for fail-fast local startup validation errors."""


class BrokerAuthError(LoginError):
    """Raised when broker authentication or verification fails."""


@dataclass(frozen=True)
class ZerodhaLoginConfig:
    api_key: str
    api_secret: str
    user_id: Optional[str]


@dataclass(frozen=True)
class LoginResult:
    broker: str
    ok: bool
    user_id: Optional[str]
    access_token_present: bool
    login_time_utc: str
    detail: str = ""


def setup_logging(level: str = "INFO") -> None:
    if logger.handlers:
        return

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
    )
    logger.addHandler(handler)


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def non_sensitive_head(value: Optional[str]) -> str:
    if not value:
        return "MISSING"
    return f"{value[:8]}..."


def validate_api_config_for_zerodha(api: BrokerApiConfig) -> ZerodhaLoginConfig:
    broker = api.broker.strip().lower()
    if broker != "zerodha":
        raise StartupValidationError(
            f"api.json broker must be 'zerodha' for this login module, got: {api.broker!r}"
        )

    if not api.api_key.strip():
        raise StartupValidationError("api.json missing non-empty api_key")
    if not api.api_secret.strip():
        raise StartupValidationError("api.json missing non-empty api_secret")

    user_id = api.user_id.strip() or None
    return ZerodhaLoginConfig(
        api_key=api.api_key.strip(),
        api_secret=api.api_secret.strip(),
        user_id=user_id,
    )


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ScalpX MME Zerodha login/session integration"
    )
    parser.add_argument(
        "--request-token",
        default=os.getenv("ZERODHA_REQUEST_TOKEN", "").strip(),
        help="Zerodha request_token. If omitted, interactive prompt is used.",
    )
    parser.add_argument(
        "--show-login-url",
        action="store_true",
        help="Print Zerodha login URL before request_token prompt.",
    )
    parser.add_argument(
        "--no-ltp-verify",
        action="store_true",
        help="Skip optional LTP verification after profile() succeeds.",
    )
    parser.add_argument(
        "--log-level",
        default=os.getenv("LOG_LEVEL", "INFO"),
        help="Logging level",
    )
    return parser.parse_args(argv)


def get_request_token(kite: KiteConnect, provided_request_token: str, show_login_url: bool) -> str:
    token = (provided_request_token or "").strip()
    if token:
        logger.info("Using Zerodha request_token from argument/environment")
        return token

    if show_login_url:
        print("Open Zerodha login URL:")
        print(kite.login_url())

    if not sys.stdin.isatty():
        raise BrokerAuthError(
            "request_token not provided and interactive prompt unavailable"
        )

    print("Open Zerodha login URL and complete login:")
    print(kite.login_url())
    entered = input("Paste request_token: ").strip()
    if not entered:
        raise BrokerAuthError("empty Zerodha request_token")
    return entered


def verify_profile(kite: KiteConnect, expected_user_id: Optional[str]) -> dict[str, Any]:
    try:
        profile = kite.profile()
    except Exception as exc:
        raise BrokerAuthError(f"Zerodha profile() verification failed: {exc}") from exc

    if not isinstance(profile, dict):
        raise BrokerAuthError("Zerodha profile() returned non-dict payload")

    user_id = str(profile.get("user_id", "")).strip()
    if not user_id:
        raise BrokerAuthError("Zerodha profile() payload missing user_id")

    if expected_user_id and user_id != expected_user_id:
        raise BrokerAuthError(
            f"Zerodha authenticated user_id mismatch: expected={expected_user_id} got={user_id}"
        )

    return profile


def verify_ltp_optional(kite: KiteConnect, enabled: bool) -> None:
    if not enabled:
        return
    try:
        payload = kite.ltp(list(DEFAULT_LTP_PROBE_SYMBOLS))
    except Exception as exc:
        raise BrokerAuthError(f"Zerodha ltp() probe failed: {exc}") from exc

    if not isinstance(payload, dict) or not payload:
        raise BrokerAuthError("Zerodha ltp() probe returned empty/non-dict payload")


def build_token_state(
    cfg: ZerodhaLoginConfig,
    session_payload: dict[str, Any],
    profile: dict[str, Any],
) -> BrokerTokenState:
    access_token = str(session_payload.get("access_token", "")).strip()
    if not access_token:
        raise BrokerAuthError("Zerodha generate_session() payload missing access_token")

    user_id = str(profile.get("user_id", "")).strip() or (cfg.user_id or "")
    public_token = str(session_payload.get("public_token", "")).strip()
    login_time = now_utc_iso()

    metadata: dict[str, Any] = {
        "version": VERSION,
        "user_id": user_id,
        "public_token": public_token,
        "login_time_utc": login_time,
    }

    user_name = str(profile.get("user_name", "")).strip()
    email = str(profile.get("email", "")).strip()
    user_shortname = str(profile.get("user_shortname", "")).strip()
    if user_name:
        metadata["user_name"] = user_name
    if email:
        metadata["email"] = email
    if user_shortname:
        metadata["user_shortname"] = user_shortname

    return BrokerTokenState(
        broker="zerodha",
        access_token=access_token,
        refresh_token="",
        issued_at=login_time,
        expires_at="",
        session_id=public_token,
        metadata=metadata,
    )


def authenticate_zerodha(
    cfg: ZerodhaLoginConfig,
    request_token: str,
    *,
    show_login_url: bool,
    do_ltp_verify: bool,
) -> LoginResult:
    kite = KiteConnect(api_key=cfg.api_key)

    token = get_request_token(
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

    access_token = str(session_payload.get("access_token", "")).strip()
    if not access_token:
        raise BrokerAuthError("Zerodha generate_session() payload missing access_token")

    kite.set_access_token(access_token)

    profile = verify_profile(kite, expected_user_id=cfg.user_id)
    verify_ltp_optional(kite, enabled=do_ltp_verify)

    state = build_token_state(cfg, session_payload, profile)
    save_token_state(state)

    result_user_id = str(profile.get("user_id", "")).strip() or cfg.user_id
    return LoginResult(
        broker="zerodha",
        ok=True,
        user_id=result_user_id,
        access_token_present=bool(access_token),
        login_time_utc=state.issued_at,
        detail="",
    )


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    setup_logging(args.log_level)

    try:
        api = load_api_config()
        cfg = validate_api_config_for_zerodha(api)
        result = authenticate_zerodha(
            cfg,
            request_token=args.request_token,
            show_login_url=bool(args.show_login_url),
            do_ltp_verify=not bool(args.no_ltp_verify),
        )
    except (
        SecretFileMissingError,
        SecretFileFormatError,
        TokenStoreError,
        StartupValidationError,
        BrokerAuthError,
    ) as exc:
        logger.error("login failed: %s", exc)
        return 1
    except Exception as exc:  # pragma: no cover
        logger.error("unexpected login failure: %s", exc)
        return 1

    print(
        "Zerodha:",
        result.ok,
        "user=",
        result.user_id or "?",
        "login_time_utc=",
        result.login_time_utc,
        "access_token=",
        "present" if result.access_token_present else "missing",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
