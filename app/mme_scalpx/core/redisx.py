"""
app/mme_scalpx/core/redisx.py

Canonical Redis transport façade for ScalpX MME.

Purpose
-------
This module OWNS:
- Redis client construction and lifecycle
- sync and async Redis transport helpers
- canonical stream append/read helpers
- canonical hash read/write helpers
- heartbeat helpers
- execution/monitor lock helpers
- consumer-group bootstrap helpers
- typed EventEnvelope / SchemaBase publish-read helpers

This module DOES NOT own:
- Redis naming contracts
- runtime settings schema definition
- payload/state model definitions
- strategy/business logic
- service orchestration policy

Core design rules
-----------------
- Streams are event/history transport.
- Hashes are latest-state/control/liveness truth.
- names.py owns names; redisx.py consumes them.
- settings.py owns runtime and operational thresholds; redisx.py consumes them.
- validators.py owns low-level scalar/type validation primitives.
- codec.py owns serialization; redisx.py uses codec helpers and does not invent wire formats.
- This module is the transport façade, not a business-logic module.
- Both sync and async APIs are supported, but share one contract surface.
"""

from __future__ import annotations

import asyncio
import json
import threading
import uuid
from dataclasses import dataclass
from typing import Any, Final, Mapping, Sequence, TypeVar, cast

import redis
import redis.asyncio as aioredis
from redis.asyncio.client import Redis as AsyncRedis
from redis.client import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import ResponseError as RedisResponseError

from app.mme_scalpx.core import names
from app.mme_scalpx.core.codec import (
    decode_envelope,
    decode_hash_fields,
    decode_model_from_envelope,
    encode_envelope,
    encode_hash_fields,
    envelope_for_model,
)
from app.mme_scalpx.core.models import EventEnvelope, SchemaBase
from app.mme_scalpx.core.settings import AppSettings, RedisSettings, get_settings
from app.mme_scalpx.core.validators import (
    require_mapping,
    require_non_empty_str,
    require_non_negative_int,
    require_positive_int,
)

# ============================================================================
# Constants
# ============================================================================

DEFAULT_GROUP_START_ID: Final[str] = "$"
DEFAULT_STREAM_START_ID: Final[str] = "0-0"
STREAM_ID_NEW_ONLY: Final[str] = ">"

_LOCK_RELEASE_LUA: Final[str] = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('del', KEYS[1])
end
return 0
"""

_LOCK_REFRESH_LUA: Final[str] = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('pexpire', KEYS[1], ARGV[2])
end
return 0
"""

# ============================================================================
# Exceptions
# ============================================================================


class RedisXError(RuntimeError):
    """Base Redis transport error."""


class ConsumerGroupError(RedisXError):
    """Raised when a consumer-group operation fails."""


class LockError(RedisXError):
    """Raised when lock operations fail."""


class LockNotOwnedError(LockError):
    """Raised when a lock refresh/release is attempted by a non-owner."""


class StreamTransportError(RedisXError):
    """Raised when stream transport fails."""


class HashTransportError(RedisXError):
    """Raised when hash transport fails."""


# ============================================================================
# Types
# ============================================================================

T = TypeVar("T", bound=SchemaBase)


@dataclass(frozen=True, slots=True)
class ConsumerGroupStatus:
    """Operational snapshot of a Redis consumer group."""

    stream: str
    group: str
    consumers: int
    pending: int
    last_delivered_id: str
    entries_read: int | None = None
    lag: int | None = None


@dataclass(frozen=True, slots=True)
class LockHandle:
    """Typed view of a distributed lock key."""

    key: str
    owner: str
    ttl_ms: int


# ============================================================================
# Client caches
# ============================================================================

_SYNC_CLIENT_LOCK: Final[threading.RLock] = threading.RLock()
_ASYNC_CLIENT_LOCK: Final[asyncio.Lock] = asyncio.Lock()

_SYNC_CLIENT: Redis | None = None
_ASYNC_CLIENT: AsyncRedis | None = None


# ============================================================================
# Validation adapters
# ============================================================================


def _wrap_validation(fn: Any, *args: Any, **kwargs: Any) -> Any:
    try:
        return fn(*args, **kwargs)
    except Exception as exc:
        raise RedisXError(str(exc)) from exc


def _require_non_empty_str(value: str, *, field_name: str) -> str:
    return cast(
        str,
        _wrap_validation(require_non_empty_str, value, field_name=field_name),
    )


def _require_positive_int(value: int, *, field_name: str) -> int:
    return cast(
        int,
        _wrap_validation(require_positive_int, value, field_name=field_name),
    )


def _require_non_negative_int(value: int, *, field_name: str) -> int:
    return cast(
        int,
        _wrap_validation(require_non_negative_int, value, field_name=field_name),
    )


def _require_mapping(value: Mapping[str, Any], *, field_name: str) -> dict[str, Any]:
    return cast(
        dict[str, Any],
        _wrap_validation(require_mapping, value, field_name=field_name),
    )


# ============================================================================
# Internal helpers
# ============================================================================


def _as_str(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def _normalize_redis_fields(fields_map: Mapping[str, Any]) -> dict[str, str]:
    """
    Normalize a field map for Redis transport.

    codec.py already performs canonical structured encoding for models/envelopes.
    This helper ensures final transport compatibility for any raw field maps.
    """
    source = _require_mapping(fields_map, field_name="fields_map")
    normalized: dict[str, str] = {}

    for raw_key, raw_value in source.items():
        key = _require_non_empty_str(str(raw_key), field_name="field_name")

        if raw_value is None:
            normalized[key] = ""
        elif isinstance(raw_value, bytes):
            normalized[key] = raw_value.decode("utf-8", errors="replace")
        elif isinstance(raw_value, (str, int, float, bool)):
            normalized[key] = str(raw_value)
        else:
            normalized[key] = json.dumps(
                raw_value,
                ensure_ascii=False,
                separators=(",", ":"),
                default=str,
            )

    return normalized


def _redis_url_kwargs(redis_settings: RedisSettings) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "decode_responses": redis_settings.decode_responses,
        "retry_on_timeout": redis_settings.retry_on_timeout,
        "socket_timeout": redis_settings.socket_timeout_s,
        "socket_connect_timeout": redis_settings.socket_connect_timeout_s,
        "health_check_interval": redis_settings.health_check_interval_s,
        "max_connections": redis_settings.max_connections,
        "client_name": redis_settings.client_name,
    }

    if redis_settings.password is not None:
        kwargs["password"] = redis_settings.password

    if redis_settings.uses_tls:
        kwargs["ssl"] = True
        if redis_settings.ssl_ca_path is not None:
            kwargs["ssl_ca_certs"] = str(redis_settings.ssl_ca_path)

    return kwargs


def _is_busy_group_error(exc: Exception) -> bool:
    return "BUSYGROUP" in str(exc).upper()


def _default_stream_maxlen(redis_settings: RedisSettings) -> int:
    return _require_positive_int(
        redis_settings.stream_maxlen_approx,
        field_name="stream_maxlen_approx",
    )


def _default_xread_count(redis_settings: RedisSettings) -> int:
    return _require_positive_int(
        redis_settings.xread_count,
        field_name="xread_count",
    )


def _default_xread_block_ms(redis_settings: RedisSettings) -> int:
    return _require_non_negative_int(
        redis_settings.xread_block_ms,
        field_name="xread_block_ms",
    )


def _get_app_settings(settings: AppSettings | None = None) -> AppSettings:
    return get_settings() if settings is None else settings


def _heartbeat_ttl_ms() -> int:
    settings = get_settings()
    return _require_positive_int(
        settings.runtime.heartbeat_ttl_ms,
        field_name="heartbeat_ttl_ms",
    )


def _lock_ttl_ms() -> int:
    settings = get_settings()
    return _require_positive_int(
        settings.runtime.lock_ttl_ms,
        field_name="lock_ttl_ms",
    )


def _decode_group_info(
    info: Mapping[str, Any],
    *,
    stream: str,
    group: str,
) -> ConsumerGroupStatus:
    entries_read = info.get("entries-read")
    lag = info.get("lag")

    return ConsumerGroupStatus(
        stream=stream,
        group=group,
        consumers=int(info.get("consumers", 0)),
        pending=int(info.get("pending", 0)),
        last_delivered_id=str(info.get("last-delivered-id", "0-0")),
        entries_read=None if entries_read is None else int(entries_read),
        lag=None if lag is None else int(lag),
    )


def _decode_stream_rows(
    rows: Sequence[tuple[Any, Mapping[str, Any]]],
) -> list[tuple[str, dict[str, str]]]:
    decoded_rows: list[tuple[str, dict[str, str]]] = []
    for row_id, raw_fields in rows:
        decoded_rows.append(
            (
                _as_str(row_id),
                {_as_str(k): _as_str(v) for k, v in raw_fields.items()},
            )
        )
    return decoded_rows


def _decode_xread_result(
    raw: Sequence[tuple[Any, Sequence[tuple[Any, Mapping[str, Any]]]]],
) -> list[tuple[str, list[tuple[str, dict[str, str]]]]]:
    decoded: list[tuple[str, list[tuple[str, dict[str, str]]]]] = []
    for stream_name, rows in raw:
        decoded.append((_as_str(stream_name), _decode_stream_rows(rows)))
    return decoded


# ============================================================================
# Client construction / lifecycle
# ============================================================================


def build_redis_client(*, settings: AppSettings | None = None) -> Redis:
    """Build a synchronous Redis client from canonical app settings."""
    app_settings = _get_app_settings(settings)
    redis_settings = app_settings.redis
    return redis.Redis.from_url(
        redis_settings.url,
        **_redis_url_kwargs(redis_settings),
    )


def build_async_redis_client(*, settings: AppSettings | None = None) -> AsyncRedis:
    """Build an asynchronous Redis client from canonical app settings."""
    app_settings = _get_app_settings(settings)
    redis_settings = app_settings.redis
    return aioredis.Redis.from_url(
        redis_settings.url,
        **_redis_url_kwargs(redis_settings),
    )


def get_redis(*, force_new: bool = False) -> Redis:
    """Get the cached synchronous Redis client, creating it on first use."""
    global _SYNC_CLIENT

    with _SYNC_CLIENT_LOCK:
        if force_new or _SYNC_CLIENT is None:
            _SYNC_CLIENT = build_redis_client()
        return _SYNC_CLIENT


async def get_async_redis(*, force_new: bool = False) -> AsyncRedis:
    """Get the cached asynchronous Redis client, creating it on first use."""
    global _ASYNC_CLIENT

    async with _ASYNC_CLIENT_LOCK:
        if force_new or _ASYNC_CLIENT is None:
            _ASYNC_CLIENT = build_async_redis_client()
        return _ASYNC_CLIENT


def close_redis_client() -> None:
    """Close and clear the cached synchronous Redis client."""
    global _SYNC_CLIENT

    with _SYNC_CLIENT_LOCK:
        client = _SYNC_CLIENT
        _SYNC_CLIENT = None

    if client is not None:
        try:
            client.close()
        except Exception as exc:  # pragma: no cover
            raise RedisXError(f"Failed to close sync Redis client: {exc}") from exc


async def close_async_redis_client() -> None:
    """Close and clear the cached asynchronous Redis client."""
    global _ASYNC_CLIENT

    async with _ASYNC_CLIENT_LOCK:
        client = _ASYNC_CLIENT
        _ASYNC_CLIENT = None

    if client is not None:
        close_method = getattr(client, "aclose", None)
        try:
            if callable(close_method):
                await close_method()
            else:
                await client.close()
        except Exception as exc:  # pragma: no cover
            raise RedisXError(f"Failed to close async Redis client: {exc}") from exc


def close_redis_clients() -> None:
    """Close all cached synchronous Redis clients owned by this module."""
    close_redis_client()


async def aclose_redis_clients() -> None:
    """Close all cached asynchronous Redis clients owned by this module."""
    await close_async_redis_client()


def ping_redis(*, client: Redis | None = None) -> bool:
    """Ping Redis using the sync client."""
    redis_client = get_redis() if client is None else client
    try:
        return bool(redis_client.ping())
    except RedisConnectionError as exc:
        raise RedisXError(f"Redis ping failed: {exc}") from exc


async def aping_redis(*, client: AsyncRedis | None = None) -> bool:
    """Ping Redis using the async client."""
    redis_client = await get_async_redis() if client is None else client
    try:
        return bool(await redis_client.ping())
    except RedisConnectionError as exc:
        raise RedisXError(f"Async Redis ping failed: {exc}") from exc


# ============================================================================
# Basic key/value and hash helpers
# ============================================================================


def get_value(key: str, *, client: Redis | None = None) -> str | None:
    """Fetch a plain string key."""
    redis_client = get_redis() if client is None else client
    redis_key = _require_non_empty_str(key, field_name="key")

    try:
        value = redis_client.get(redis_key)
        return None if value is None else _as_str(value)
    except Exception as exc:
        raise RedisXError(f"Failed to GET {redis_key!r}: {exc}") from exc


async def aget_value(key: str, *, client: AsyncRedis | None = None) -> str | None:
    """Fetch a plain string key asynchronously."""
    redis_client = await get_async_redis() if client is None else client
    redis_key = _require_non_empty_str(key, field_name="key")

    try:
        value = await redis_client.get(redis_key)
        return None if value is None else _as_str(value)
    except Exception as exc:
        raise RedisXError(f"Failed to async GET {redis_key!r}: {exc}") from exc


def hgetall(key: str, *, client: Redis | None = None) -> dict[str, str]:
    """Fetch all fields from a Redis hash."""
    redis_client = get_redis() if client is None else client
    redis_key = _require_non_empty_str(key, field_name="key")

    try:
        result = redis_client.hgetall(redis_key)
    except Exception as exc:
        raise HashTransportError(f"Failed to HGETALL {redis_key!r}: {exc}") from exc

    return {_as_str(k): _as_str(v) for k, v in result.items()}


async def ahgetall(key: str, *, client: AsyncRedis | None = None) -> dict[str, str]:
    """Fetch all fields from a Redis hash asynchronously."""
    redis_client = await get_async_redis() if client is None else client
    redis_key = _require_non_empty_str(key, field_name="key")

    try:
        result = await redis_client.hgetall(redis_key)
    except Exception as exc:
        raise HashTransportError(
            f"Failed to async HGETALL {redis_key!r}: {exc}"
        ) from exc

    return {_as_str(k): _as_str(v) for k, v in result.items()}


def write_hash_fields(
    key: str,
    fields_map: Mapping[str, Any],
    *,
    ttl_ms: int | None = None,
    client: Redis | None = None,
) -> int:
    """
    Write a raw field map into a Redis hash.

    Returns the number of fields that were newly added.
    """
    redis_client = get_redis() if client is None else client
    redis_key = _require_non_empty_str(key, field_name="key")
    normalized = _normalize_redis_fields(fields_map)

    try:
        changed = int(redis_client.hset(redis_key, mapping=normalized))
        if ttl_ms is not None:
            redis_client.pexpire(
                redis_key,
                _require_positive_int(ttl_ms, field_name="ttl_ms"),
            )
        return changed
    except Exception as exc:
        raise HashTransportError(f"Failed to write hash {redis_key!r}: {exc}") from exc


async def awrite_hash_fields(
    key: str,
    fields_map: Mapping[str, Any],
    *,
    ttl_ms: int | None = None,
    client: AsyncRedis | None = None,
) -> int:
    """
    Write a raw field map into a Redis hash asynchronously.

    Returns the number of fields that were newly added.
    """
    redis_client = await get_async_redis() if client is None else client
    redis_key = _require_non_empty_str(key, field_name="key")
    normalized = _normalize_redis_fields(fields_map)

    try:
        changed = int(await redis_client.hset(redis_key, mapping=normalized))
        if ttl_ms is not None:
            await redis_client.pexpire(
                redis_key,
                _require_positive_int(ttl_ms, field_name="ttl_ms"),
            )
        return changed
    except Exception as exc:
        raise HashTransportError(
            f"Failed to async write hash {redis_key!r}: {exc}"
        ) from exc


def write_hash_model(
    key: str,
    model: SchemaBase,
    *,
    ttl_ms: int | None = None,
    client: Redis | None = None,
) -> int:
    """Encode and write a SchemaBase instance into a Redis hash."""
    return write_hash_fields(
        key,
        encode_hash_fields(model),
        ttl_ms=ttl_ms,
        client=client,
    )


async def awrite_hash_model(
    key: str,
    model: SchemaBase,
    *,
    ttl_ms: int | None = None,
    client: AsyncRedis | None = None,
) -> int:
    """Encode and write a SchemaBase instance into a Redis hash asynchronously."""
    return await awrite_hash_fields(
        key,
        encode_hash_fields(model),
        ttl_ms=ttl_ms,
        client=client,
    )


def read_hash_model(
    key: str,
    model_cls: type[T],
    *,
    client: Redis | None = None,
) -> T | None:
    """Read and decode a SchemaBase instance from a Redis hash."""
    raw = hgetall(key, client=client)
    if not raw:
        return None

    try:
        return decode_hash_fields(model_cls, raw)
    except Exception as exc:
        raise HashTransportError(
            f"Failed to decode hash model {model_cls.__name__} from {key!r}: {exc}"
        ) from exc


async def aread_hash_model(
    key: str,
    model_cls: type[T],
    *,
    client: AsyncRedis | None = None,
) -> T | None:
    """Read and decode a SchemaBase instance from a Redis hash asynchronously."""
    raw = await ahgetall(key, client=client)
    if not raw:
        return None

    try:
        return decode_hash_fields(model_cls, raw)
    except Exception as exc:
        raise HashTransportError(
            f"Failed to async decode hash model {model_cls.__name__} from {key!r}: {exc}"
        ) from exc


def write_hash_and_append_stream(
    hash_key: str,
    stream_name: str,
    hash_fields: Mapping[str, Any],
    stream_fields: Mapping[str, Any],
    *,
    hash_ttl_ms: int | None = None,
    stream_maxlen_approx: int | None = None,
    client: Redis | None = None,
) -> tuple[int, str]:
    """
    Write a state hash and append an event stream entry.

    This is not a Redis transaction. It is a transport convenience helper.
    """
    changed = write_hash_fields(
        hash_key,
        hash_fields,
        ttl_ms=hash_ttl_ms,
        client=client,
    )
    stream_id = xadd_fields(
        stream_name,
        stream_fields,
        maxlen_approx=stream_maxlen_approx,
        client=client,
    )
    return changed, stream_id


async def awrite_hash_and_append_stream(
    hash_key: str,
    stream_name: str,
    hash_fields: Mapping[str, Any],
    stream_fields: Mapping[str, Any],
    *,
    hash_ttl_ms: int | None = None,
    stream_maxlen_approx: int | None = None,
    client: AsyncRedis | None = None,
) -> tuple[int, str]:
    """
    Write a state hash and append an event stream entry asynchronously.

    This is not a Redis transaction. It is a transport convenience helper.
    """
    changed = await awrite_hash_fields(
        hash_key,
        hash_fields,
        ttl_ms=hash_ttl_ms,
        client=client,
    )
    stream_id = await axadd_fields(
        stream_name,
        stream_fields,
        maxlen_approx=stream_maxlen_approx,
        client=client,
    )
    return changed, stream_id


# ============================================================================
# Stream append helpers
# ============================================================================


def xadd_fields(
    stream_name: str,
    fields_map: Mapping[str, Any],
    *,
    maxlen_approx: int | None = None,
    client: Redis | None = None,
) -> str:
    """Append a raw field map to a Redis stream."""
    redis_client = get_redis() if client is None else client
    redis_settings = get_settings().redis

    stream = _require_non_empty_str(stream_name, field_name="stream_name")
    normalized = _normalize_redis_fields(fields_map)

    maxlen = (
        _default_stream_maxlen(redis_settings)
        if maxlen_approx is None
        else _require_positive_int(maxlen_approx, field_name="maxlen_approx")
    )

    try:
        stream_id = redis_client.xadd(
            stream,
            normalized,
            maxlen=maxlen,
            approximate=True,
        )
        return _as_str(stream_id)
    except Exception as exc:
        raise StreamTransportError(f"Failed to XADD to {stream!r}: {exc}") from exc


async def axadd_fields(
    stream_name: str,
    fields_map: Mapping[str, Any],
    *,
    maxlen_approx: int | None = None,
    client: AsyncRedis | None = None,
) -> str:
    """Append a raw field map to a Redis stream asynchronously."""
    redis_client = await get_async_redis() if client is None else client
    redis_settings = get_settings().redis

    stream = _require_non_empty_str(stream_name, field_name="stream_name")
    normalized = _normalize_redis_fields(fields_map)

    maxlen = (
        _default_stream_maxlen(redis_settings)
        if maxlen_approx is None
        else _require_positive_int(maxlen_approx, field_name="maxlen_approx")
    )

    try:
        stream_id = await redis_client.xadd(
            stream,
            normalized,
            maxlen=maxlen,
            approximate=True,
        )
        return _as_str(stream_id)
    except Exception as exc:
        raise StreamTransportError(
            f"Failed to async XADD to {stream!r}: {exc}"
        ) from exc


def publish_envelope(
    stream_name: str,
    envelope: EventEnvelope,
    *,
    maxlen_approx: int | None = None,
    client: Redis | None = None,
) -> str:
    """Encode and publish an EventEnvelope to a stream."""
    return xadd_fields(
        stream_name,
        encode_envelope(envelope),
        maxlen_approx=maxlen_approx,
        client=client,
    )


async def apublish_envelope(
    stream_name: str,
    envelope: EventEnvelope,
    *,
    maxlen_approx: int | None = None,
    client: AsyncRedis | None = None,
) -> str:
    """Encode and publish an EventEnvelope to a stream asynchronously."""
    return await axadd_fields(
        stream_name,
        encode_envelope(envelope),
        maxlen_approx=maxlen_approx,
        client=client,
    )


def publish_model_as_envelope(
    stream_name: str,
    model: SchemaBase,
    *,
    ts_event_ns: int,
    ts_ingest_ns: int,
    producer: str,
    correlation_id: str | None = None,
    replay: bool = False,
    schema_version: int = names.DEFAULT_SCHEMA_VERSION,
    maxlen_approx: int | None = None,
    client: Redis | None = None,
) -> str:
    """Wrap a model in an EventEnvelope and publish it to a stream."""
    envelope = envelope_for_model(
        model,
        ts_event_ns=ts_event_ns,
        ts_ingest_ns=ts_ingest_ns,
        producer=producer,
        correlation_id=correlation_id,
        stream=stream_name,
        replay=replay,
        schema_version=schema_version,
    )
    return publish_envelope(
        stream_name,
        envelope,
        maxlen_approx=maxlen_approx,
        client=client,
    )


async def apublish_model_as_envelope(
    stream_name: str,
    model: SchemaBase,
    *,
    ts_event_ns: int,
    ts_ingest_ns: int,
    producer: str,
    correlation_id: str | None = None,
    replay: bool = False,
    schema_version: int = names.DEFAULT_SCHEMA_VERSION,
    maxlen_approx: int | None = None,
    client: AsyncRedis | None = None,
) -> str:
    """Wrap a model in an EventEnvelope and publish it to a stream asynchronously."""
    envelope = envelope_for_model(
        model,
        ts_event_ns=ts_event_ns,
        ts_ingest_ns=ts_ingest_ns,
        producer=producer,
        correlation_id=correlation_id,
        stream=stream_name,
        replay=replay,
        schema_version=schema_version,
    )
    return await apublish_envelope(
        stream_name,
        envelope,
        maxlen_approx=maxlen_approx,
        client=client,
    )


# ============================================================================
# Stream read helpers
# ============================================================================


def xread(
    streams: Mapping[str, str],
    *,
    count: int | None = None,
    block_ms: int | None = None,
    client: Redis | None = None,
) -> list[tuple[str, list[tuple[str, dict[str, str]]]]]:
    """Read one or more streams using XREAD."""
    redis_client = get_redis() if client is None else client
    redis_settings = get_settings().redis

    normalized_streams = {
        _require_non_empty_str(str(name), field_name="stream_name"): _require_non_empty_str(
            str(stream_id),
            field_name="stream_id",
        )
        for name, stream_id in streams.items()
    }

    read_count = (
        _default_xread_count(redis_settings)
        if count is None
        else _require_positive_int(count, field_name="count")
    )
    read_block_ms = (
        _default_xread_block_ms(redis_settings)
        if block_ms is None
        else _require_non_negative_int(block_ms, field_name="block_ms")
    )

    try:
        raw = redis_client.xread(
            streams=normalized_streams,
            count=read_count,
            block=read_block_ms,
        )
        return _decode_xread_result(raw)
    except Exception as exc:
        raise StreamTransportError(
            f"Failed XREAD on streams {list(normalized_streams)}: {exc}"
        ) from exc


async def axread(
    streams: Mapping[str, str],
    *,
    count: int | None = None,
    block_ms: int | None = None,
    client: AsyncRedis | None = None,
) -> list[tuple[str, list[tuple[str, dict[str, str]]]]]:
    """Read one or more streams using XREAD asynchronously."""
    redis_client = await get_async_redis() if client is None else client
    redis_settings = get_settings().redis

    normalized_streams = {
        _require_non_empty_str(str(name), field_name="stream_name"): _require_non_empty_str(
            str(stream_id),
            field_name="stream_id",
        )
        for name, stream_id in streams.items()
    }

    read_count = (
        _default_xread_count(redis_settings)
        if count is None
        else _require_positive_int(count, field_name="count")
    )
    read_block_ms = (
        _default_xread_block_ms(redis_settings)
        if block_ms is None
        else _require_non_negative_int(block_ms, field_name="block_ms")
    )

    try:
        raw = await redis_client.xread(
            streams=normalized_streams,
            count=read_count,
            block=read_block_ms,
        )
        return _decode_xread_result(raw)
    except Exception as exc:
        raise StreamTransportError(
            f"Failed async XREAD on streams {list(normalized_streams)}: {exc}"
        ) from exc


def xreadgroup(
    group_name: str,
    consumer_name: str,
    streams: Mapping[str, str],
    *,
    count: int | None = None,
    block_ms: int | None = None,
    noack: bool = False,
    client: Redis | None = None,
) -> list[tuple[str, list[tuple[str, dict[str, str]]]]]:
    """Read one or more streams using XREADGROUP."""
    redis_client = get_redis() if client is None else client
    redis_settings = get_settings().redis

    group = _require_non_empty_str(group_name, field_name="group_name")
    consumer = _require_non_empty_str(consumer_name, field_name="consumer_name")
    normalized_streams = {
        _require_non_empty_str(str(name), field_name="stream_name"): _require_non_empty_str(
            str(stream_id),
            field_name="stream_id",
        )
        for name, stream_id in streams.items()
    }

    read_count = (
        _default_xread_count(redis_settings)
        if count is None
        else _require_positive_int(count, field_name="count")
    )
    read_block_ms = (
        _default_xread_block_ms(redis_settings)
        if block_ms is None
        else _require_non_negative_int(block_ms, field_name="block_ms")
    )

    try:
        raw = redis_client.xreadgroup(
            groupname=group,
            consumername=consumer,
            streams=normalized_streams,
            count=read_count,
            block=read_block_ms,
            noack=noack,
        )
        return _decode_xread_result(raw)
    except Exception as exc:
        raise StreamTransportError(
            f"Failed XREADGROUP for {group!r}/{consumer!r}: {exc}"
        ) from exc


async def axreadgroup(
    group_name: str,
    consumer_name: str,
    streams: Mapping[str, str],
    *,
    count: int | None = None,
    block_ms: int | None = None,
    noack: bool = False,
    client: AsyncRedis | None = None,
) -> list[tuple[str, list[tuple[str, dict[str, str]]]]]:
    """Read one or more streams using XREADGROUP asynchronously."""
    redis_client = await get_async_redis() if client is None else client
    redis_settings = get_settings().redis

    group = _require_non_empty_str(group_name, field_name="group_name")
    consumer = _require_non_empty_str(consumer_name, field_name="consumer_name")
    normalized_streams = {
        _require_non_empty_str(str(name), field_name="stream_name"): _require_non_empty_str(
            str(stream_id),
            field_name="stream_id",
        )
        for name, stream_id in streams.items()
    }

    read_count = (
        _default_xread_count(redis_settings)
        if count is None
        else _require_positive_int(count, field_name="count")
    )
    read_block_ms = (
        _default_xread_block_ms(redis_settings)
        if block_ms is None
        else _require_non_negative_int(block_ms, field_name="block_ms")
    )

    try:
        raw = await redis_client.xreadgroup(
            groupname=group,
            consumername=consumer,
            streams=normalized_streams,
            count=read_count,
            block=read_block_ms,
            noack=noack,
        )
        return _decode_xread_result(raw)
    except Exception as exc:
        raise StreamTransportError(
            f"Failed async XREADGROUP for {group!r}/{consumer!r}: {exc}"
        ) from exc


def xack(
    stream_name: str,
    group_name: str,
    message_ids: Sequence[str],
    *,
    client: Redis | None = None,
) -> int:
    """Acknowledge stream entries for a consumer group."""
    redis_client = get_redis() if client is None else client
    stream = _require_non_empty_str(stream_name, field_name="stream_name")
    group = _require_non_empty_str(group_name, field_name="group_name")
    ids = [
        _require_non_empty_str(str(message_id), field_name="message_id")
        for message_id in message_ids
    ]
    if not ids:
        return 0

    try:
        return int(redis_client.xack(stream, group, *ids))
    except Exception as exc:
        raise StreamTransportError(
            f"Failed XACK for stream={stream!r} group={group!r}: {exc}"
        ) from exc


async def axack(
    stream_name: str,
    group_name: str,
    message_ids: Sequence[str],
    *,
    client: AsyncRedis | None = None,
) -> int:
    """Acknowledge stream entries for a consumer group asynchronously."""
    redis_client = await get_async_redis() if client is None else client
    stream = _require_non_empty_str(stream_name, field_name="stream_name")
    group = _require_non_empty_str(group_name, field_name="group_name")
    ids = [
        _require_non_empty_str(str(message_id), field_name="message_id")
        for message_id in message_ids
    ]
    if not ids:
        return 0

    try:
        return int(await redis_client.xack(stream, group, *ids))
    except Exception as exc:
        raise StreamTransportError(
            f"Failed async XACK for stream={stream!r} group={group!r}: {exc}"
        ) from exc


def read_envelopes_from_group(
    stream_name: str,
    group_name: str,
    consumer_name: str,
    *,
    stream_id: str = STREAM_ID_NEW_ONLY,
    count: int | None = None,
    block_ms: int | None = None,
    noack: bool = False,
    client: Redis | None = None,
) -> list[tuple[str, EventEnvelope]]:
    """Read and decode EventEnvelope rows from a consumer group."""
    results = xreadgroup(
        group_name,
        consumer_name,
        {stream_name: stream_id},
        count=count,
        block_ms=block_ms,
        noack=noack,
        client=client,
    )

    decoded: list[tuple[str, EventEnvelope]] = []
    for _, rows in results:
        for message_id, fields in rows:
            try:
                decoded.append((message_id, decode_envelope(fields)))
            except Exception as exc:
                raise StreamTransportError(
                    f"Failed to decode envelope from stream={stream_name!r} "
                    f"message_id={message_id!r}: {exc}"
                ) from exc
    return decoded


async def aread_envelopes_from_group(
    stream_name: str,
    group_name: str,
    consumer_name: str,
    *,
    stream_id: str = STREAM_ID_NEW_ONLY,
    count: int | None = None,
    block_ms: int | None = None,
    noack: bool = False,
    client: AsyncRedis | None = None,
) -> list[tuple[str, EventEnvelope]]:
    """Read and decode EventEnvelope rows from a consumer group asynchronously."""
    results = await axreadgroup(
        group_name,
        consumer_name,
        {stream_name: stream_id},
        count=count,
        block_ms=block_ms,
        noack=noack,
        client=client,
    )

    decoded: list[tuple[str, EventEnvelope]] = []
    for _, rows in results:
        for message_id, fields in rows:
            try:
                decoded.append((message_id, decode_envelope(fields)))
            except Exception as exc:
                raise StreamTransportError(
                    f"Failed to async decode envelope from stream={stream_name!r} "
                    f"message_id={message_id!r}: {exc}"
                ) from exc
    return decoded


def read_models_from_group(
    stream_name: str,
    group_name: str,
    consumer_name: str,
    model_cls: type[T],
    *,
    stream_id: str = STREAM_ID_NEW_ONLY,
    count: int | None = None,
    block_ms: int | None = None,
    noack: bool = False,
    client: Redis | None = None,
) -> list[tuple[str, EventEnvelope, T]]:
    """Read and decode typed models from EventEnvelope rows in a consumer group."""
    envelopes = read_envelopes_from_group(
        stream_name,
        group_name,
        consumer_name,
        stream_id=stream_id,
        count=count,
        block_ms=block_ms,
        noack=noack,
        client=client,
    )

    decoded: list[tuple[str, EventEnvelope, T]] = []
    for message_id, envelope in envelopes:
        try:
            model = decode_model_from_envelope(model_cls, envelope)
        except Exception as exc:
            raise StreamTransportError(
                f"Failed to decode model {model_cls.__name__} from stream={stream_name!r} "
                f"message_id={message_id!r}: {exc}"
            ) from exc
        decoded.append((message_id, envelope, model))

    return decoded


async def aread_models_from_group(
    stream_name: str,
    group_name: str,
    consumer_name: str,
    model_cls: type[T],
    *,
    stream_id: str = STREAM_ID_NEW_ONLY,
    count: int | None = None,
    block_ms: int | None = None,
    noack: bool = False,
    client: AsyncRedis | None = None,
) -> list[tuple[str, EventEnvelope, T]]:
    """Read and decode typed models from EventEnvelope rows in a consumer group asynchronously."""
    envelopes = await aread_envelopes_from_group(
        stream_name,
        group_name,
        consumer_name,
        stream_id=stream_id,
        count=count,
        block_ms=block_ms,
        noack=noack,
        client=client,
    )

    decoded: list[tuple[str, EventEnvelope, T]] = []
    for message_id, envelope in envelopes:
        try:
            model = decode_model_from_envelope(model_cls, envelope)
        except Exception as exc:
            raise StreamTransportError(
                f"Failed to async decode model {model_cls.__name__} from stream={stream_name!r} "
                f"message_id={message_id!r}: {exc}"
            ) from exc
        decoded.append((message_id, envelope, model))

    return decoded


# ============================================================================
# Consumer-group helpers
# ============================================================================


def ensure_consumer_group(
    stream_name: str,
    group_name: str,
    *,
    start_id: str = DEFAULT_GROUP_START_ID,
    mkstream: bool = True,
    client: Redis | None = None,
) -> None:
    """Ensure a consumer group exists for a stream."""
    redis_client = get_redis() if client is None else client
    stream = _require_non_empty_str(stream_name, field_name="stream_name")
    group = _require_non_empty_str(group_name, field_name="group_name")
    start = _require_non_empty_str(start_id, field_name="start_id")

    try:
        redis_client.xgroup_create(
            name=stream,
            groupname=group,
            id=start,
            mkstream=mkstream,
        )
    except RedisResponseError as exc:
        if _is_busy_group_error(exc):
            return
        raise ConsumerGroupError(
            f"Failed to create consumer group {group!r} on stream {stream!r}: {exc}"
        ) from exc
    except Exception as exc:
        raise ConsumerGroupError(
            f"Failed to create consumer group {group!r} on stream {stream!r}: {exc}"
        ) from exc


async def aensure_consumer_group(
    stream_name: str,
    group_name: str,
    *,
    start_id: str = DEFAULT_GROUP_START_ID,
    mkstream: bool = True,
    client: AsyncRedis | None = None,
) -> None:
    """Ensure a consumer group exists for a stream asynchronously."""
    redis_client = await get_async_redis() if client is None else client
    stream = _require_non_empty_str(stream_name, field_name="stream_name")
    group = _require_non_empty_str(group_name, field_name="group_name")
    start = _require_non_empty_str(start_id, field_name="start_id")

    try:
        await redis_client.xgroup_create(
            name=stream,
            groupname=group,
            id=start,
            mkstream=mkstream,
        )
    except RedisResponseError as exc:
        if _is_busy_group_error(exc):
            return
        raise ConsumerGroupError(
            f"Failed to async create consumer group {group!r} on stream {stream!r}: {exc}"
        ) from exc
    except Exception as exc:
        raise ConsumerGroupError(
            f"Failed to async create consumer group {group!r} on stream {stream!r}: {exc}"
        ) from exc


def bootstrap_group_specs(
    *,
    replay: bool = False,
    client: Redis | None = None,
) -> None:
    """Bootstrap canonical group specs from names.py."""
    specs = names.get_group_specs(replay=replay)
    for stream_name, groups in specs.items():
        for group_name in groups:
            ensure_consumer_group(
                stream_name,
                group_name,
                start_id=DEFAULT_GROUP_START_ID,
                mkstream=True,
                client=client,
            )


async def abootstrap_group_specs(
    *,
    replay: bool = False,
    client: AsyncRedis | None = None,
) -> None:
    """Bootstrap canonical group specs from names.py asynchronously."""
    specs = names.get_group_specs(replay=replay)
    for stream_name, groups in specs.items():
        for group_name in groups:
            await aensure_consumer_group(
                stream_name,
                group_name,
                start_id=DEFAULT_GROUP_START_ID,
                mkstream=True,
                client=client,
            )


def get_consumer_group_status(
    stream_name: str,
    group_name: str,
    *,
    client: Redis | None = None,
) -> ConsumerGroupStatus | None:
    """Inspect a consumer group's operational status."""
    redis_client = get_redis() if client is None else client
    stream = _require_non_empty_str(stream_name, field_name="stream_name")
    group = _require_non_empty_str(group_name, field_name="group_name")

    try:
        groups = redis_client.xinfo_groups(stream)
    except RedisResponseError:
        return None
    except Exception as exc:
        raise ConsumerGroupError(
            f"Failed to inspect group status for {stream!r}/{group!r}: {exc}"
        ) from exc

    for info in groups:
        if _as_str(info.get("name")) != group:
            continue
        return _decode_group_info(info, stream=stream, group=group)

    return None


async def aget_consumer_group_status(
    stream_name: str,
    group_name: str,
    *,
    client: AsyncRedis | None = None,
) -> ConsumerGroupStatus | None:
    """Inspect a consumer group's operational status asynchronously."""
    redis_client = await get_async_redis() if client is None else client
    stream = _require_non_empty_str(stream_name, field_name="stream_name")
    group = _require_non_empty_str(group_name, field_name="group_name")

    try:
        groups = await redis_client.xinfo_groups(stream)
    except RedisResponseError:
        return None
    except Exception as exc:
        raise ConsumerGroupError(
            f"Failed to async inspect group status for {stream!r}/{group!r}: {exc}"
        ) from exc

    for info in groups:
        if _as_str(info.get("name")) != group:
            continue
        return _decode_group_info(info, stream=stream, group=group)

    return None


# ============================================================================
# Heartbeat helpers
# ============================================================================


def write_heartbeat(
    key: str,
    *,
    service: str,
    instance_id: str,
    status: str,
    ts_event_ns: int,
    message: str | None = None,
    ttl_ms: int | None = None,
    client: Redis | None = None,
) -> int:
    """
    Write a heartbeat hash and refresh TTL on the root key explicitly.

    This preserves correct stale-service semantics for hash-based liveness keys.
    """
    redis_client = get_redis() if client is None else client
    heartbeat_key = _require_non_empty_str(key, field_name="key")
    heartbeat_ttl = (
        _heartbeat_ttl_ms()
        if ttl_ms is None
        else _require_positive_int(ttl_ms, field_name="ttl_ms")
    )

    fields_map: dict[str, Any] = {
        "service": _require_non_empty_str(service, field_name="service"),
        "instance_id": _require_non_empty_str(instance_id, field_name="instance_id"),
        "status": _require_non_empty_str(status, field_name="status"),
        "ts_event_ns": _require_non_negative_int(ts_event_ns, field_name="ts_event_ns"),
    }
    if message is not None:
        fields_map["message"] = _require_non_empty_str(message, field_name="message")

    changed = write_hash_fields(
        heartbeat_key,
        fields_map,
        ttl_ms=None,
        client=redis_client,
    )

    try:
        redis_client.pexpire(heartbeat_key, heartbeat_ttl)
    except Exception as exc:
        raise HashTransportError(
            f"Failed to refresh heartbeat TTL for {heartbeat_key!r}: {exc}"
        ) from exc

    return changed


async def awrite_heartbeat(
    key: str,
    *,
    service: str,
    instance_id: str,
    status: str,
    ts_event_ns: int,
    message: str | None = None,
    ttl_ms: int | None = None,
    client: AsyncRedis | None = None,
) -> int:
    """
    Write a heartbeat hash asynchronously and refresh TTL on the root key explicitly.
    """
    redis_client = await get_async_redis() if client is None else client
    heartbeat_key = _require_non_empty_str(key, field_name="key")
    heartbeat_ttl = (
        _heartbeat_ttl_ms()
        if ttl_ms is None
        else _require_positive_int(ttl_ms, field_name="ttl_ms")
    )

    fields_map: dict[str, Any] = {
        "service": _require_non_empty_str(service, field_name="service"),
        "instance_id": _require_non_empty_str(instance_id, field_name="instance_id"),
        "status": _require_non_empty_str(status, field_name="status"),
        "ts_event_ns": _require_non_negative_int(ts_event_ns, field_name="ts_event_ns"),
    }
    if message is not None:
        fields_map["message"] = _require_non_empty_str(message, field_name="message")

    changed = await awrite_hash_fields(
        heartbeat_key,
        fields_map,
        ttl_ms=None,
        client=redis_client,
    )

    try:
        await redis_client.pexpire(heartbeat_key, heartbeat_ttl)
    except Exception as exc:
        raise HashTransportError(
            f"Failed to async refresh heartbeat TTL for {heartbeat_key!r}: {exc}"
        ) from exc

    return changed


# ============================================================================
# Lock helpers
# ============================================================================


def make_lock_owner(prefix: str) -> str:
    """Construct a unique lock-owner token."""
    return f"{_require_non_empty_str(prefix, field_name='prefix')}:{uuid.uuid4().hex}"


def acquire_lock(
    key: str,
    owner: str,
    *,
    ttl_ms: int | None = None,
    client: Redis | None = None,
) -> bool:
    """Acquire a distributed lock via SET NX PX."""
    redis_client = get_redis() if client is None else client
    lock_key = _require_non_empty_str(key, field_name="key")
    lock_owner = _require_non_empty_str(owner, field_name="owner")
    lock_ttl_ms = (
        _lock_ttl_ms()
        if ttl_ms is None
        else _require_positive_int(ttl_ms, field_name="ttl_ms")
    )

    try:
        acquired = redis_client.set(lock_key, lock_owner, nx=True, px=lock_ttl_ms)
        return bool(acquired)
    except Exception as exc:
        raise LockError(f"Failed to acquire lock {lock_key!r}: {exc}") from exc


async def aacquire_lock(
    key: str,
    owner: str,
    *,
    ttl_ms: int | None = None,
    client: AsyncRedis | None = None,
) -> bool:
    """Acquire a distributed lock asynchronously via SET NX PX."""
    redis_client = await get_async_redis() if client is None else client
    lock_key = _require_non_empty_str(key, field_name="key")
    lock_owner = _require_non_empty_str(owner, field_name="owner")
    lock_ttl_ms = (
        _lock_ttl_ms()
        if ttl_ms is None
        else _require_positive_int(ttl_ms, field_name="ttl_ms")
    )

    try:
        acquired = await redis_client.set(lock_key, lock_owner, nx=True, px=lock_ttl_ms)
        return bool(acquired)
    except Exception as exc:
        raise LockError(f"Failed to async acquire lock {lock_key!r}: {exc}") from exc


def refresh_lock(
    key: str,
    owner: str,
    *,
    ttl_ms: int | None = None,
    client: Redis | None = None,
) -> bool:
    """Refresh a distributed lock only if still owned by the caller."""
    redis_client = get_redis() if client is None else client
    lock_key = _require_non_empty_str(key, field_name="key")
    lock_owner = _require_non_empty_str(owner, field_name="owner")
    lock_ttl_ms = (
        _lock_ttl_ms()
        if ttl_ms is None
        else _require_positive_int(ttl_ms, field_name="ttl_ms")
    )

    try:
        refreshed = redis_client.eval(_LOCK_REFRESH_LUA, 1, lock_key, lock_owner, lock_ttl_ms)
        return bool(refreshed)
    except Exception as exc:
        raise LockError(f"Failed to refresh lock {lock_key!r}: {exc}") from exc


async def arefresh_lock(
    key: str,
    owner: str,
    *,
    ttl_ms: int | None = None,
    client: AsyncRedis | None = None,
) -> bool:
    """Refresh a distributed lock asynchronously only if still owned by the caller."""
    redis_client = await get_async_redis() if client is None else client
    lock_key = _require_non_empty_str(key, field_name="key")
    lock_owner = _require_non_empty_str(owner, field_name="owner")
    lock_ttl_ms = (
        _lock_ttl_ms()
        if ttl_ms is None
        else _require_positive_int(ttl_ms, field_name="ttl_ms")
    )

    try:
        refreshed = await redis_client.eval(
            _LOCK_REFRESH_LUA,
            1,
            lock_key,
            lock_owner,
            lock_ttl_ms,
        )
        return bool(refreshed)
    except Exception as exc:
        raise LockError(f"Failed to async refresh lock {lock_key!r}: {exc}") from exc


def release_lock(
    key: str,
    owner: str,
    *,
    client: Redis | None = None,
) -> bool:
    """Release a distributed lock only if still owned by the caller."""
    redis_client = get_redis() if client is None else client
    lock_key = _require_non_empty_str(key, field_name="key")
    lock_owner = _require_non_empty_str(owner, field_name="owner")

    try:
        released = redis_client.eval(_LOCK_RELEASE_LUA, 1, lock_key, lock_owner)
        return bool(released)
    except Exception as exc:
        raise LockError(f"Failed to release lock {lock_key!r}: {exc}") from exc


async def arelease_lock(
    key: str,
    owner: str,
    *,
    client: AsyncRedis | None = None,
) -> bool:
    """Release a distributed lock asynchronously only if still owned by the caller."""
    redis_client = await get_async_redis() if client is None else client
    lock_key = _require_non_empty_str(key, field_name="key")
    lock_owner = _require_non_empty_str(owner, field_name="owner")

    try:
        released = await redis_client.eval(_LOCK_RELEASE_LUA, 1, lock_key, lock_owner)
        return bool(released)
    except Exception as exc:
        raise LockError(f"Failed to async release lock {lock_key!r}: {exc}") from exc


def get_lock_handle(
    key: str,
    *,
    client: Redis | None = None,
) -> LockHandle | None:
    """Inspect an existing distributed lock key."""
    redis_client = get_redis() if client is None else client
    lock_key = _require_non_empty_str(key, field_name="key")

    try:
        owner = redis_client.get(lock_key)
        if owner is None:
            return None

        ttl_ms = int(redis_client.pttl(lock_key))
        return LockHandle(key=lock_key, owner=_as_str(owner), ttl_ms=ttl_ms)
    except Exception as exc:
        raise LockError(f"Failed to inspect lock {lock_key!r}: {exc}") from exc


async def aget_lock_handle(
    key: str,
    *,
    client: AsyncRedis | None = None,
) -> LockHandle | None:
    """Inspect an existing distributed lock key asynchronously."""
    redis_client = await get_async_redis() if client is None else client
    lock_key = _require_non_empty_str(key, field_name="key")

    try:
        owner = await redis_client.get(lock_key)
        if owner is None:
            return None

        ttl_ms = int(await redis_client.pttl(lock_key))
        return LockHandle(key=lock_key, owner=_as_str(owner), ttl_ms=ttl_ms)
    except Exception as exc:
        raise LockError(f"Failed to async inspect lock {lock_key!r}: {exc}") from exc


# ============================================================================
# Optional compatibility aliases
# Keep thin and explicit if older services still call these names.
# ============================================================================
get_redis_client = get_redis
get_async_redis_client = get_async_redis


__all__ = [
    "ConsumerGroupError",
    "ConsumerGroupStatus",
    "DEFAULT_GROUP_START_ID",
    "DEFAULT_STREAM_START_ID",
    "HashTransportError",
    "LockError",
    "LockHandle",
    "LockNotOwnedError",
    "RedisXError",
    "STREAM_ID_NEW_ONLY",
    "StreamTransportError",
    "aacquire_lock",
    "aclose_redis_clients",
    "acquire_lock",
    "aget_consumer_group_status",
    "aget_lock_handle",
    "aget_value",
    "ahgetall",
    "aensure_consumer_group",
    "aping_redis",
    "apublish_envelope",
    "apublish_model_as_envelope",
    "aread_envelopes_from_group",
    "aread_hash_model",
    "aread_models_from_group",
    "arefresh_lock",
    "arelease_lock",
    "awrite_hash_and_append_stream",
    "awrite_hash_fields",
    "awrite_hash_model",
    "awrite_heartbeat",
    "axack",
    "axadd_fields",
    "axread",
    "axreadgroup",
    "abootstrap_group_specs",
    "bootstrap_group_specs",
    "build_async_redis_client",
    "build_redis_client",
    "close_async_redis_client",
    "close_redis_client",
    "close_redis_clients",
    "ensure_consumer_group",
    "get_async_redis",
    "get_async_redis_client",
    "get_consumer_group_status",
    "get_lock_handle",
    "get_redis",
    "get_redis_client",
    "get_value",
    "hgetall",
    "make_lock_owner",
    "ping_redis",
    "publish_envelope",
    "publish_model_as_envelope",
    "read_envelopes_from_group",
    "read_hash_model",
    "read_models_from_group",
    "refresh_lock",
    "release_lock",
    "write_hash_and_append_stream",
    "write_hash_fields",
    "write_hash_model",
    "write_heartbeat",
    "xack",
    "xadd_fields",
    "xread",
    "xreadgroup",
]