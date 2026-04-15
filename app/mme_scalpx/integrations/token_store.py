"""
app/mme_scalpx/integrations/token_store.py

Freeze-grade token/session persistence layer for ScalpX MME.

Responsibilities
----------------
- read static broker credential config from shared api.json
- read/write short-lived broker token/session state from tokens.json
- validate minimal structure and required fields
- provide explicit failure on missing/corrupt/invalid files

Non-responsibilities
--------------------
- does not perform broker login
- does not refresh broker tokens
- does not call Redis
- does not mutate main runtime wiring
- does not guess broker-specific auth semantics

Current contract
----------------
api.json owns:
- broker
- api_key
- api_secret
- user_id

tokens.json owns:
- broker
- access_token
- refresh_token
- issued_at
- expires_at
- session_id
- metadata

Notes
-----
- This module intentionally stays vendor-light.
- Expiry interpretation is conservative and optional until login semantics are frozen.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_API_JSON = Path("/home/Lenovo/scalpx/common/secrets/shared/api.json")
DEFAULT_TOKENS_JSON = Path("/home/Lenovo/scalpx/common/secrets/shared/tokens.json")


class TokenStoreError(RuntimeError):
    """Base token store error."""


class SecretFileMissingError(TokenStoreError):
    """Raised when a required secret/config file is missing."""


class SecretFileFormatError(TokenStoreError):
    """Raised when a secret/config file is malformed or invalid."""


@dataclass(frozen=True)
class BrokerApiConfig:
    broker: str
    api_key: str
    api_secret: str
    user_id: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BrokerApiConfig":
        required = ("broker", "api_key", "api_secret", "user_id")
        missing = [k for k in required if not str(data.get(k, "")).strip()]
        if missing:
            raise SecretFileFormatError(
                f"api.json missing required non-empty field(s): {', '.join(missing)}"
            )
        return cls(
            broker=str(data["broker"]).strip(),
            api_key=str(data["api_key"]).strip(),
            api_secret=str(data["api_secret"]).strip(),
            user_id=str(data["user_id"]).strip(),
        )


@dataclass(frozen=True)
class BrokerTokenState:
    broker: str
    access_token: str = ""
    refresh_token: str = ""
    issued_at: str = ""
    expires_at: str = ""
    session_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BrokerTokenState":
        broker = str(data.get("broker", "")).strip()
        if not broker:
            raise SecretFileFormatError("tokens.json missing required non-empty field: broker")

        metadata = data.get("metadata", {})
        if metadata is None:
            metadata = {}
        if not isinstance(metadata, dict):
            raise SecretFileFormatError("tokens.json field 'metadata' must be an object")

        return cls(
            broker=broker,
            access_token=str(data.get("access_token", "")).strip(),
            refresh_token=str(data.get("refresh_token", "")).strip(),
            issued_at=str(data.get("issued_at", "")).strip(),
            expires_at=str(data.get("expires_at", "")).strip(),
            session_id=str(data.get("session_id", "")).strip(),
            metadata=metadata,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "broker": self.broker,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "session_id": self.session_id,
            "metadata": self.metadata,
        }

    def has_access_token(self) -> bool:
        return bool(self.access_token)

    def is_expired(self, now: Optional[datetime] = None) -> bool:
        """
        Conservative expiry check.

        Rules:
        - if expires_at missing -> treat as unknown/non-expired here
        - if expires_at malformed -> raise
        - if expires_at present and <= now -> expired
        """
        if not self.expires_at:
            return False

        dt = _parse_iso8601(self.expires_at)
        now_dt = now or datetime.now(timezone.utc)
        return dt <= now_dt


def _read_json_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise SecretFileMissingError(f"missing file: {path}")
    if not path.is_file():
        raise SecretFileFormatError(f"not a file: {path}")

    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise TokenStoreError(f"failed reading file {path}: {exc}") from exc

    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SecretFileFormatError(f"invalid JSON in {path}: {exc}") from exc

    if not isinstance(obj, dict):
        raise SecretFileFormatError(f"top-level JSON object required in {path}")

    return obj


def _write_json_file_atomic(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    data = json.dumps(payload, indent=2, sort_keys=False) + "\n"
    try:
        tmp.write_text(data, encoding="utf-8")
        tmp.replace(path)
    except OSError as exc:
        raise TokenStoreError(f"failed writing file {path}: {exc}") from exc


def _parse_iso8601(value: str) -> datetime:
    text = value.strip()
    if not text:
        raise SecretFileFormatError("empty datetime string")
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError as exc:
        raise SecretFileFormatError(f"invalid ISO-8601 datetime: {value}") from exc
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def load_api_config(path: Path = DEFAULT_API_JSON) -> BrokerApiConfig:
    return BrokerApiConfig.from_dict(_read_json_file(path))


def load_token_state(path: Path = DEFAULT_TOKENS_JSON) -> BrokerTokenState:
    return BrokerTokenState.from_dict(_read_json_file(path))


def save_token_state(state: BrokerTokenState, path: Path = DEFAULT_TOKENS_JSON) -> None:
    _write_json_file_atomic(path, state.to_dict())


def clear_token_state(path: Path = DEFAULT_TOKENS_JSON, broker: str = "") -> None:
    payload = BrokerTokenState(broker=broker).to_dict()
    _write_json_file_atomic(path, payload)


def token_file_exists(path: Path = DEFAULT_TOKENS_JSON) -> bool:
    return path.exists() and path.is_file()


def validate_api_config(path: Path = DEFAULT_API_JSON) -> None:
    load_api_config(path)


def validate_token_state(path: Path = DEFAULT_TOKENS_JSON) -> None:
    load_token_state(path)


if __name__ == "__main__":
    api = load_api_config()
    print(f"api.json OK | broker={api.broker} | user_id={api.user_id}")

    if token_file_exists():
        token = load_token_state()
        print(
            "tokens.json OK | "
            f"broker={token.broker} | "
            f"has_access_token={token.has_access_token()} | "
            f"expired={token.is_expired() if token.expires_at else 'unknown'}"
        )
    else:
        print("tokens.json not present yet")
