"""
app/mme_scalpx/core/codec.py

Canonical serialization and transport codec for ScalpX MME.

Purpose
-------
This module OWNS:
- canonical JSON serialization / deserialization
- canonical EventEnvelope encode / decode
- model <-> envelope conversion helpers
- flat Redis hash field encode / decode helpers
- transport-safe scalar coercion rules
- stable schema-version-aware serialization entrypoints

This module DOES NOT own:
- Redis naming contracts
- Redis client lifecycle
- business / trading logic
- runtime settings schema
- clock implementation
- strategy signal generation

Core design rules
-----------------
- models.py validates and structures; codec.py serializes and reconstructs.
- validators.py owns low-level scalar/type validation primitives.
- names.py remains the only source of contract constants.
- EventEnvelope.payload is always a mapping, never None.
- JSON payloads must be deterministic and utf-8 safe.
- Redis hash encoding is only for flat/simple latest-state models.
- Complex/nested models belong in JSON/event payload transport, not hash fields.
- Validation failures must be explicit and deterministic.
- Services should use this module's helpers for payload/envelope/hash wire handling
  rather than ad hoc json.loads()/json.dumps() or bespoke Redis-field decoding.
"""

from __future__ import annotations

import json
import math
import sys
import types
from dataclasses import MISSING, fields, is_dataclass
from datetime import date, datetime
from typing import Any, Final, Mapping, TypeVar, get_args, get_origin, get_type_hints

from . import names
from .models import (
    EventEnvelope,
    ModelValidationError,
    SchemaBase,
    model_from_type,
)
from .validators import (
    ValidationError,
    require_mapping,
    require_non_empty_str,
)

# ============================================================================
# Constants
# ============================================================================

JSON_SORT_KEYS: Final[bool] = True
JSON_ENSURE_ASCII: Final[bool] = False
JSON_ALLOW_NAN: Final[bool] = False
JSON_SEPARATORS: Final[tuple[str, str]] = (",", ":")

REQUIRED_ENVELOPE_FIELDS: Final[tuple[str, ...]] = (
    "envelope_type",
    "schema_version",
    "ts_event_ns",
    "ts_ingest_ns",
    "producer",
    "replay",
    "payload",
)

HASH_NULL_SENTINEL: Final[str] = ""
HASH_BOOL_TRUE: Final[str] = "1"
HASH_BOOL_FALSE: Final[str] = "0"

_SIMPLE_HASH_SCALAR_TYPES: Final[tuple[type[Any], ...]] = (
    str,
    int,
    float,
    bool,
)

_BOOL_TRUE_VALUES: Final[frozenset[str]] = frozenset(
    {"1", "true", "yes", "y", "on"}
)
_BOOL_FALSE_VALUES: Final[frozenset[str]] = frozenset(
    {"0", "false", "no", "n", "off"}
)

T = TypeVar("T", bound=SchemaBase)


# ============================================================================
# Exceptions
# ============================================================================


class CodecError(ValueError):
    """Base codec error."""


class EnvelopeDecodeError(CodecError):
    """Raised when an envelope cannot be decoded."""


class HashCodecError(CodecError):
    """Raised when a hash model cannot be encoded or decoded safely."""


# ============================================================================
# Local wrappers around shared validators
# Keeps codec-specific exception contracts intact.
# ============================================================================


def _wrap_validation(
    error_cls: type[Exception],
    fn: Any,
    *args: Any,
    **kwargs: Any,
) -> Any:
    try:
        return fn(*args, **kwargs)
    except Exception as exc:
        if isinstance(exc, error_cls):
            raise
        raise error_cls(str(exc)) from exc


def _require_non_empty_str(value: str, *, field_name: str) -> str:
    return _wrap_validation(
        CodecError,
        require_non_empty_str,
        value,
        field_name=field_name,
    )


def _require_mapping(value: Mapping[str, Any], *, field_name: str) -> dict[str, Any]:
    return _wrap_validation(
        CodecError,
        require_mapping,
        value,
        field_name=field_name,
    )


# ============================================================================
# Small helpers
# ============================================================================


def _is_finite_float(value: float) -> bool:
    return math.isfinite(value)


def _json_default(value: Any) -> Any:
    """
    Deterministic JSON fallback conversion.

    Allowed conversions:
    - SchemaBase -> to_dict()
    - dataclass  -> plain dict
    - datetime   -> ISO-8601 string
    - date       -> ISO-8601 string
    - tuple      -> list
    """
    if isinstance(value, SchemaBase):
        return value.to_dict()

    if is_dataclass(value):
        result: dict[str, Any] = {}
        for dc_field in fields(value):
            result[dc_field.name] = getattr(value, dc_field.name)
        return result

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, date):
        return value.isoformat()

    if isinstance(value, tuple):
        return list(value)

    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _ensure_json_mapping(value: Any, *, field_name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise EnvelopeDecodeError(
            f"{field_name} must decode to mapping, got {type(value).__name__}"
        )
    return {str(k): v for k, v in value.items()}


def _model_type_name(model: SchemaBase) -> str:
    model_type = getattr(model.__class__, "_TYPE", "")
    if not isinstance(model_type, str) or not model_type.strip():
        raise CodecError(
            f"{model.__class__.__name__} must define a non-empty _TYPE for transport"
        )
    return model_type.strip()



def _resolved_type_hints(model_cls: type[SchemaBase]) -> dict[str, Any]:
    """Resolve postponed annotations for dataclass model fields.

    The project uses from __future__ import annotations, so dataclass field.type
    may be a string. Hash/event helpers must validate real annotations, not
    unresolved strings.
    """
    try:
        module = sys.modules.get(model_cls.__module__)
        module_ns = vars(module) if module is not None else None
        return get_type_hints(model_cls, globalns=module_ns, localns=module_ns)
    except Exception as exc:
        raise CodecError(
            f"Failed to resolve type hints for {model_cls.__name__}: {exc}"
        ) from exc

def _is_union_type(origin: Any) -> bool:
    return origin in (types.UnionType, getattr(__import__("typing"), "Union", None))


def _is_optional_annotation(annotation: Any) -> bool:
    """
    Return True for Optional[T] / T | None annotations.
    """
    origin = get_origin(annotation)
    if origin is None:
        return False

    args = get_args(annotation)
    return _is_union_type(origin) and any(arg is type(None) for arg in args)


def _unwrap_optional_annotation(annotation: Any) -> Any:
    """
    Return the non-None member of Optional[T] / T | None.
    """
    if not _is_optional_annotation(annotation):
        return annotation

    args = get_args(annotation)
    non_none = [arg for arg in args if arg is not type(None)]
    if len(non_none) != 1:
        raise CodecError(f"Unsupported optional annotation shape: {annotation!r}")
    return non_none[0]


def _is_supported_hash_scalar_annotation(annotation: Any) -> bool:
    if annotation is Any:
        return False

    if _is_optional_annotation(annotation):
        annotation = _unwrap_optional_annotation(annotation)

    origin = get_origin(annotation)
    if origin is not None:
        return False

    return annotation in _SIMPLE_HASH_SCALAR_TYPES


def _bool_from_text(value: Any, *, field_name: str, error_cls: type[Exception]) -> bool:
    text = str(value).strip().lower()
    if text in _BOOL_TRUE_VALUES:
        return True
    if text in _BOOL_FALSE_VALUES:
        return False
    raise error_cls(f"{field_name} must be boolean-like, got {value!r}")


def decode_optional_field(
    annotation: Any,
    data: Mapping[str, Any],
    field_name: str,
) -> Any:
    """
    Handle missing optional fields during decoding.

    Rules:
    - missing Optional[...] -> None
    - missing required      -> raise CodecError
    - present value         -> return raw value
    """
    if field_name not in data:
        if _is_optional_annotation(annotation):
            return None
        raise CodecError(f"Missing required field: {field_name}")
    return data[field_name]


# ============================================================================
# Canonical JSON helpers
# ============================================================================


def json_dumps(value: Any) -> str:
    """
    Deterministic JSON dump.

    Rules:
    - UTF-8 friendly
    - sorted keys
    - compact separators
    - NaN/Inf rejected
    """
    try:
        return json.dumps(
            value,
            ensure_ascii=JSON_ENSURE_ASCII,
            sort_keys=JSON_SORT_KEYS,
            allow_nan=JSON_ALLOW_NAN,
            separators=JSON_SEPARATORS,
            default=_json_default,
        )
    except (TypeError, ValueError) as exc:
        raise CodecError(f"Failed to JSON-encode value: {exc}") from exc


def json_loads(raw: str | bytes | bytearray) -> Any:
    """
    Load JSON from utf-8 text/bytes.
    """
    if isinstance(raw, (bytes, bytearray)):
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise CodecError(f"Failed to decode bytes as utf-8: {exc}") from exc
    elif isinstance(raw, str):
        text = raw
    else:
        raise CodecError(
            f"json_loads() requires str/bytes/bytearray, got {type(raw).__name__}"
        )

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise CodecError(f"Failed to JSON-decode value: {exc}") from exc


# ============================================================================
# Envelope encode / decode
# ============================================================================


def encode_envelope(envelope: EventEnvelope) -> dict[str, str]:
    """
    Encode EventEnvelope to Redis stream/hash-safe flat string fields.

    payload is always serialized as JSON object text.
    Optional scalar metadata fields are omitted when None.
    """
    if not isinstance(envelope, EventEnvelope):
        raise CodecError(
            f"encode_envelope() requires EventEnvelope, got {type(envelope).__name__}"
        )

    encoded: dict[str, str] = {
        "envelope_type": envelope.envelope_type,
        "schema_version": str(envelope.schema_version),
        "ts_event_ns": str(envelope.ts_event_ns),
        "ts_ingest_ns": str(envelope.ts_ingest_ns),
        "producer": envelope.producer,
        "replay": HASH_BOOL_TRUE if envelope.replay else HASH_BOOL_FALSE,
        "payload": json_dumps(dict(envelope.payload)),
    }

    if envelope.correlation_id is not None:
        encoded["correlation_id"] = envelope.correlation_id
    if envelope.stream is not None:
        encoded["stream"] = envelope.stream

    return encoded


def decode_envelope(raw: Mapping[str, Any]) -> EventEnvelope:
    """
    Decode flat Redis fields back into EventEnvelope.
    """
    try:
        source = require_mapping(raw, field_name="raw")
    except ValidationError as exc:
        raise EnvelopeDecodeError(str(exc)) from exc

    missing = [name for name in REQUIRED_ENVELOPE_FIELDS if name not in source]
    if missing:
        raise EnvelopeDecodeError(
            f"Envelope missing required fields: {', '.join(missing)}"
        )

    try:
        schema_version = int(str(source["schema_version"]))
        ts_event_ns = int(str(source["ts_event_ns"]))
        ts_ingest_ns = int(str(source["ts_ingest_ns"]))
    except (TypeError, ValueError) as exc:
        raise EnvelopeDecodeError(
            "schema_version, ts_event_ns, and ts_ingest_ns must be int-like values"
        ) from exc

    replay = _bool_from_text(
        source["replay"],
        field_name="replay",
        error_cls=EnvelopeDecodeError,
    )

    payload_raw = source["payload"]
    if not isinstance(payload_raw, str):
        payload_raw = str(payload_raw)

    payload_value = json_loads(payload_raw)
    payload = _ensure_json_mapping(payload_value, field_name="payload")

    try:
        return EventEnvelope(
            envelope_type=str(source["envelope_type"]),
            schema_version=schema_version,
            ts_event_ns=ts_event_ns,
            ts_ingest_ns=ts_ingest_ns,
            producer=str(source["producer"]),
            correlation_id=(
                None
                if source.get("correlation_id") in (None, "")
                else str(source["correlation_id"])
            ),
            stream=(
                None if source.get("stream") in (None, "") else str(source["stream"])
            ),
            replay=replay,
            payload=payload,
        )
    except ModelValidationError as exc:
        raise EnvelopeDecodeError(f"Decoded envelope is invalid: {exc}") from exc


def encode_envelope_json(envelope: EventEnvelope) -> str:
    """
    Encode EventEnvelope directly as canonical JSON text.

    This is useful for file/report transport or any surface that stores
    the envelope as a single JSON blob rather than Redis fields.
    """
    return json_dumps(encode_envelope(envelope))


def decode_envelope_json(raw: str | bytes | bytearray) -> EventEnvelope:
    """
    Decode EventEnvelope from canonical JSON text representing the encoded envelope dict.
    """
    decoded = json_loads(raw)
    if not isinstance(decoded, Mapping):
        raise EnvelopeDecodeError(
            f"Encoded envelope JSON must decode to mapping, got {type(decoded).__name__}"
        )
    return decode_envelope(decoded)


# ============================================================================
# Model <-> envelope helpers
# ============================================================================


def envelope_for_model(
    model: SchemaBase,
    *,
    ts_event_ns: int,
    ts_ingest_ns: int,
    producer: str,
    correlation_id: str | None = None,
    stream: str | None = None,
    replay: bool = False,
    schema_version: int = names.DEFAULT_SCHEMA_VERSION,
) -> EventEnvelope:
    """
    Build canonical envelope from a typed model.
    """
    if not isinstance(model, SchemaBase):
        raise CodecError(
            f"envelope_for_model() requires SchemaBase, got {type(model).__name__}"
        )

    return EventEnvelope(
        envelope_type=_model_type_name(model),
        schema_version=schema_version,
        ts_event_ns=ts_event_ns,
        ts_ingest_ns=ts_ingest_ns,
        producer=_require_non_empty_str(producer, field_name="producer"),
        correlation_id=correlation_id,
        stream=stream,
        replay=replay,
        payload=model.to_dict(),
    )


def model_to_envelope_dict(
    model: SchemaBase,
    *,
    ts_event_ns: int,
    ts_ingest_ns: int,
    producer: str,
    correlation_id: str | None = None,
    stream: str | None = None,
    replay: bool = False,
    schema_version: int = names.DEFAULT_SCHEMA_VERSION,
) -> dict[str, str]:
    """
    Convenience: typed model -> EventEnvelope -> encoded flat dict.
    """
    envelope = envelope_for_model(
        model,
        ts_event_ns=ts_event_ns,
        ts_ingest_ns=ts_ingest_ns,
        producer=producer,
        correlation_id=correlation_id,
        stream=stream,
        replay=replay,
        schema_version=schema_version,
    )
    return encode_envelope(envelope)


def model_to_envelope_json(
    model: SchemaBase,
    *,
    ts_event_ns: int,
    ts_ingest_ns: int,
    producer: str,
    correlation_id: str | None = None,
    stream: str | None = None,
    replay: bool = False,
    schema_version: int = names.DEFAULT_SCHEMA_VERSION,
) -> str:
    """
    Convenience: typed model -> EventEnvelope -> canonical JSON text.
    """
    envelope = envelope_for_model(
        model,
        ts_event_ns=ts_event_ns,
        ts_ingest_ns=ts_ingest_ns,
        producer=producer,
        correlation_id=correlation_id,
        stream=stream,
        replay=replay,
        schema_version=schema_version,
    )
    return encode_envelope_json(envelope)


def decode_model_from_envelope(
    envelope: EventEnvelope | Mapping[str, Any],
) -> SchemaBase:
    """
    Decode typed model from envelope instance or raw encoded envelope mapping.
    """
    decoded = (
        decode_envelope(envelope)
        if not isinstance(envelope, EventEnvelope)
        else envelope
    )
    return model_from_type(decoded.envelope_type, decoded.payload)

def decode_model_from_envelope_as(
    model_cls: type[T],
    envelope: EventEnvelope | Mapping[str, Any],
) -> T:
    """Decode envelope and require the expected SchemaBase subclass."""
    if not isinstance(model_cls, type) or not issubclass(model_cls, SchemaBase):
        raise CodecError("model_cls must be a SchemaBase subclass")

    model = decode_model_from_envelope(envelope)
    if not isinstance(model, model_cls):
        raise CodecError(
            f"Envelope decoded to {type(model).__name__}, expected {model_cls.__name__}"
        )
    return model


def decode_model_from_envelope_json(raw: str | bytes | bytearray) -> SchemaBase:
    """
    Decode typed model from canonical JSON text representing an encoded envelope dict.
    """
    envelope = decode_envelope_json(raw)
    return model_from_type(envelope.envelope_type, envelope.payload)


def encode_model_payload(model: SchemaBase) -> str:
    """
    Encode a typed model as canonical JSON payload text.
    """
    if not isinstance(model, SchemaBase):
        raise CodecError(
            f"encode_model_payload() requires SchemaBase, got {type(model).__name__}"
        )
    return json_dumps(model.to_dict())


def decode_model_payload(model_cls: type[T], raw: str | bytes | bytearray) -> T:
    """
    Decode canonical JSON payload text into a typed model.
    """
    if not isinstance(model_cls, type) or not issubclass(model_cls, SchemaBase):
        raise CodecError("model_cls must be a SchemaBase subclass")

    decoded = json_loads(raw)
    if not isinstance(decoded, Mapping):
        raise CodecError(
            f"Decoded payload for {model_cls.__name__} must be mapping, "
            f"got {type(decoded).__name__}"
        )

    try:
        return model_cls.from_mapping(decoded)
    except ModelValidationError as exc:
        raise CodecError(
            f"Decoded payload is invalid for {model_cls.__name__}: {exc}"
        ) from exc


def decode_event_payload(data: Mapping[str, Any], model_cls: type[T]) -> T:
    """
    Decode event payload mapping into the target model.

    This helper explicitly tolerates missing Optional[...] fields by
    populating them as None before reconstructing the model.
    """
    if not isinstance(model_cls, type) or not issubclass(model_cls, SchemaBase):
        raise CodecError("model_cls must be a SchemaBase subclass")

    source = _require_mapping(data, field_name="data")

    type_hints = _resolved_type_hints(model_cls)
    model_fields = {
        dc_field.name: type_hints.get(dc_field.name, dc_field.type)
        for dc_field in fields(model_cls)
    }
    decoded_data: dict[str, Any] = {}

    for field_name, annotation in model_fields.items():
        decoded_data[field_name] = decode_optional_field(
            annotation,
            source,
            field_name,
        )

    try:
        return model_cls.from_mapping(decoded_data)
    except ModelValidationError as exc:
        raise CodecError(
            f"Decoded event payload is invalid for {model_cls.__name__}: {exc}"
        ) from exc


# ============================================================================
# Redis hash encode / decode
# ============================================================================


def _encode_hash_scalar(value: Any, *, field_name: str) -> str:
    if value is None:
        return HASH_NULL_SENTINEL

    if isinstance(value, bool):
        return HASH_BOOL_TRUE if value else HASH_BOOL_FALSE

    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)

    if isinstance(value, float):
        if not _is_finite_float(value):
            raise HashCodecError(
                f"{field_name} must be a finite float for hash transport"
            )
        return repr(value)

    if isinstance(value, str):
        return value

    raise HashCodecError(
        f"{field_name} has unsupported hash scalar type {type(value).__name__}"
    )


def _decode_hash_scalar(
    annotation: Any,
    raw_value: Any,
    *,
    field_name: str,
) -> Any:
    if not _is_supported_hash_scalar_annotation(annotation):
        raise HashCodecError(
            f"{field_name} has unsupported hash field annotation {annotation!r}"
        )

    is_optional = _is_optional_annotation(annotation)
    target = _unwrap_optional_annotation(annotation) if is_optional else annotation
    text = str(raw_value) if raw_value is not None else HASH_NULL_SENTINEL

    if text == HASH_NULL_SENTINEL:
        if is_optional:
            return None
        if target is str:
            return ""
        raise HashCodecError(
            f"{field_name} is non-optional but received empty/null sentinel"
        )

    if target is str:
        return text

    if target is bool:
        return _bool_from_text(
            text,
            field_name=field_name,
            error_cls=HashCodecError,
        )

    if target is int:
        try:
            return int(text)
        except ValueError as exc:
            raise HashCodecError(
                f"{field_name} must be int-like, got {raw_value!r}"
            ) from exc

    if target is float:
        try:
            value = float(text)
        except ValueError as exc:
            raise HashCodecError(
                f"{field_name} must be float-like, got {raw_value!r}"
            ) from exc
        if not _is_finite_float(value):
            raise HashCodecError(
                f"{field_name} must be finite float, got {raw_value!r}"
            )
        return value

    raise HashCodecError(
        f"{field_name} has unsupported target annotation {target!r}"
    )


def encode_hash_fields(model: SchemaBase) -> dict[str, str]:
    """
    Encode a flat/simple SchemaBase model into Redis hash fields.

    Supported field types:
    - str
    - int
    - float
    - bool
    - Optional[str|int|float|bool]

    Unsupported:
    - nested models
    - mappings
    - tuples/lists
    - Any
    """
    if not isinstance(model, SchemaBase):
        raise HashCodecError(
            f"encode_hash_fields() requires SchemaBase, got {type(model).__name__}"
        )

    model_cls = model.__class__
    type_hints = _resolved_type_hints(model_cls)
    encoded: dict[str, str] = {}

    for dc_field in fields(model_cls):
        annotation = type_hints.get(dc_field.name, dc_field.type)
        if not _is_supported_hash_scalar_annotation(annotation):
            raise HashCodecError(
                f"{model_cls.__name__}.{dc_field.name} is not hash-safe; "
                f"use JSON/event transport for complex fields"
            )
        encoded[dc_field.name] = _encode_hash_scalar(
            getattr(model, dc_field.name),
            field_name=f"{model_cls.__name__}.{dc_field.name}",
        )

    return encoded


def decode_hash_fields(model_cls: type[T], raw: Mapping[str, Any]) -> T:
    """
    Decode Redis hash fields into a flat/simple SchemaBase model.
    """
    if not isinstance(model_cls, type) or not issubclass(model_cls, SchemaBase):
        raise HashCodecError("model_cls must be a SchemaBase subclass")

    try:
        source = require_mapping(raw, field_name="raw")
    except ValidationError as exc:
        raise HashCodecError(str(exc)) from exc

    kwargs: dict[str, Any] = {}
    type_hints = _resolved_type_hints(model_cls)

    for dc_field in fields(model_cls):
        field_name = dc_field.name
        annotation = type_hints.get(field_name, dc_field.type)

        if not _is_supported_hash_scalar_annotation(annotation):
            raise HashCodecError(
                f"{model_cls.__name__}.{field_name} is not hash-safe; "
                f"use JSON/event transport for complex fields"
            )

        if field_name not in source:
            if dc_field.default is not MISSING:
                continue
            if (
                hasattr(dc_field, "default_factory")
                and dc_field.default_factory is not MISSING
            ):
                continue
            if _is_optional_annotation(annotation):
                kwargs[field_name] = None
                continue
            raise HashCodecError(
                f"Missing required hash field for {model_cls.__name__}: {field_name}"
            )

        kwargs[field_name] = _decode_hash_scalar(
            annotation,
            source[field_name],
            field_name=f"{model_cls.__name__}.{field_name}",
        )

    try:
        return model_cls(**kwargs)
    except ModelValidationError as exc:
        raise HashCodecError(
            f"Decoded hash fields are invalid for {model_cls.__name__}: {exc}"
        ) from exc


def encode_hash_model(model: SchemaBase) -> dict[str, str]:
    """
    Canonical alias for services: typed latest-state model -> Redis hash fields.
    """
    return encode_hash_fields(model)


def decode_hash_model(model_cls: type[T], raw: Mapping[str, Any]) -> T:
    """
    Canonical alias for services: Redis hash fields -> typed latest-state model.
    """
    return decode_hash_fields(model_cls, raw)


# ============================================================================
# Public exports
# ============================================================================

__all__ = [
    "CodecError",
    "EnvelopeDecodeError",
    "HASH_BOOL_FALSE",
    "HASH_BOOL_TRUE",
    "HASH_NULL_SENTINEL",
    "HashCodecError",
    "decode_envelope",
    "decode_envelope_json",
    "decode_event_payload",
    "decode_hash_fields",
    "decode_hash_model",
    "decode_model_from_envelope",
    "decode_model_from_envelope_as",
    "decode_model_from_envelope_json",
    "decode_model_payload",
    "decode_optional_field",
    "encode_envelope",
    "encode_envelope_json",
    "encode_hash_fields",
    "encode_hash_model",
    "encode_model_payload",
    "envelope_for_model",
    "json_dumps",
    "json_loads",
    "model_to_envelope_dict",
    "model_to_envelope_json",
]

# ===== BATCH18_CORE_INFRA_SPINE_FREEZE START =====
# Batch 18 freeze-final guard:
# codec.py remains the serialization owner. These overrides preserve existing
# wire format while making hash/event dataclass helpers safe under
# `from __future__ import annotations`.

import sys as _batch18_sys
from dataclasses import MISSING as _batch18_MISSING, fields as _batch18_fields
from typing import Any as _batch18_Any
from typing import Mapping as _batch18_Mapping
from typing import get_type_hints as _batch18_get_type_hints


def _batch18_resolved_type_hints(model_cls: type) -> dict[str, _batch18_Any]:
    module = _batch18_sys.modules.get(getattr(model_cls, "__module__", ""))
    globalns = vars(module) if module is not None else {}
    try:
        return dict(_batch18_get_type_hints(model_cls, globalns=globalns, localns=dict(vars(model_cls))))
    except Exception:
        return {}


def _batch18_require_schema_model_cls(model_cls: type, *, error_cls: type[Exception]) -> None:
    schema_base = globals().get("SchemaBase")
    if schema_base is None or not isinstance(model_cls, type) or not issubclass(model_cls, schema_base):
        raise error_cls("model_cls must be a SchemaBase subclass")


def _batch18_require_schema_model(model: object, *, error_cls: type[Exception]) -> None:
    schema_base = globals().get("SchemaBase")
    if schema_base is None or not isinstance(model, schema_base):
        raise error_cls("model must be a SchemaBase instance")


def _batch18_default_factory_is_missing(dc_field: object) -> bool:
    return getattr(dc_field, "default_factory", _batch18_MISSING) is _batch18_MISSING


def _batch18_decode_event_field_value(
    annotation: _batch18_Any,
    value: _batch18_Any,
    *,
    model_cls: type,
    field_name: str,
) -> _batch18_Any:
    """
    Compatibility shim for the existing codec.decode_optional_field() API.

    Current codec.py shape is:
        decode_optional_field(annotation, data, field_name)

    The data argument must be the source mapping, and field_name must be the
    actual key inside that mapping. Do not pass the scalar value directly.
    """

    try:
        return decode_optional_field(
            annotation,
            {field_name: value},
            field_name=field_name,
        )
    except Exception as exc:
        raise CodecError(
            f"Failed to decode {model_cls.__name__}.{field_name}: {exc}"
        ) from exc


def decode_model_from_envelope_as(model_cls: type[T], envelope: EventEnvelope | _batch18_Mapping[str, _batch18_Any]) -> T:
    model = decode_model_from_envelope(envelope)
    if not isinstance(model, model_cls):
        raise CodecError(
            f"Envelope decoded to {type(model).__name__}, expected {model_cls.__name__}"
        )
    return model


def decode_event_payload(data: _batch18_Mapping[str, _batch18_Any], model_cls: type[T]) -> T:
    _batch18_require_schema_model_cls(model_cls, error_cls=CodecError)

    try:
        source = _require_mapping(data, field_name="data")
    except Exception:
        try:
            source = require_mapping(data, field_name="data")
        except Exception as exc:
            raise CodecError(str(exc)) from exc

    type_hints = _batch18_resolved_type_hints(model_cls)
    kwargs: dict[str, _batch18_Any] = {}

    for dc_field in _batch18_fields(model_cls):
        field_name = dc_field.name
        annotation = type_hints.get(field_name, dc_field.type)

        if field_name not in source:
            if dc_field.default is not _batch18_MISSING:
                continue
            if not _batch18_default_factory_is_missing(dc_field):
                continue
            if _is_optional_annotation(annotation):
                kwargs[field_name] = None
                continue
            raise CodecError(f"Missing required field: {field_name}")

        try:
            kwargs[field_name] = _batch18_decode_event_field_value(
                annotation,
                source[field_name],
                model_cls=model_cls,
                field_name=field_name,
            )
        except Exception as exc:
            raise CodecError(str(exc)) from exc

    try:
        return model_cls(**kwargs)
    except ModelValidationError as exc:
        raise CodecError(
            f"Decoded event payload is invalid for {model_cls.__name__}: {exc}"
        ) from exc


def encode_hash_fields(model: SchemaBase) -> dict[str, str]:
    _batch18_require_schema_model(model, error_cls=HashCodecError)

    model_cls = type(model)
    type_hints = _batch18_resolved_type_hints(model_cls)
    encoded: dict[str, str] = {}

    for dc_field in _batch18_fields(model):
        field_name = dc_field.name
        annotation = type_hints.get(field_name, dc_field.type)

        if not _is_supported_hash_scalar_annotation(annotation):
            raise HashCodecError(
                f"{model_cls.__name__}.{field_name} is not hash-safe; "
                f"use JSON/event transport for complex fields"
            )

        value = getattr(model, field_name)
        encoded[field_name] = _encode_hash_scalar(
            value,
            field_name=f"{model_cls.__name__}.{field_name}",
        )

    return encoded


def decode_hash_fields(model_cls: type[T], raw: _batch18_Mapping[str, _batch18_Any]) -> T:
    _batch18_require_schema_model_cls(model_cls, error_cls=HashCodecError)

    try:
        source = _require_mapping(raw, field_name="raw")
    except Exception:
        try:
            source = require_mapping(raw, field_name="raw")
        except Exception as exc:
            raise HashCodecError(str(exc)) from exc

    type_hints = _batch18_resolved_type_hints(model_cls)
    kwargs: dict[str, _batch18_Any] = {}

    for dc_field in _batch18_fields(model_cls):
        field_name = dc_field.name
        annotation = type_hints.get(field_name, dc_field.type)

        if not _is_supported_hash_scalar_annotation(annotation):
            raise HashCodecError(
                f"{model_cls.__name__}.{field_name} is not hash-safe; "
                f"use JSON/event transport for complex fields"
            )

        if field_name not in source:
            if dc_field.default is not _batch18_MISSING:
                continue
            if not _batch18_default_factory_is_missing(dc_field):
                continue
            if _is_optional_annotation(annotation):
                kwargs[field_name] = None
                continue
            raise HashCodecError(
                f"Missing required hash field for {model_cls.__name__}: {field_name}"
            )

        kwargs[field_name] = _decode_hash_scalar(
            annotation,
            source[field_name],
            field_name=f"{model_cls.__name__}.{field_name}",
        )

    try:
        return model_cls(**kwargs)
    except ModelValidationError as exc:
        raise HashCodecError(
            f"Decoded hash fields are invalid for {model_cls.__name__}: {exc}"
        ) from exc


try:
    if "decode_model_from_envelope_as" not in __all__:
        __all__.append("decode_model_from_envelope_as")
except Exception:
    pass
# ===== BATCH18_CORE_INFRA_SPINE_FREEZE END =====
