from __future__ import annotations

import json
import time
from typing import Any

from app.mme_scalpx.shadow_paper.models import LtpSnapshot


PRICE_KEYS = [
    "ltp",
    "last_price",
    "last_traded_price",
    "price",
    "close",
    "selected_option_ltp",
    "option_ltp",
]

SYMBOL_KEYS = [
    "symbol",
    "tradingsymbol",
    "trading_symbol",
    "option_symbol",
    "selected_option_symbol",
]

TOKEN_KEYS = [
    "instrument_token",
    "token",
    "option_token",
    "selected_option_token",
]


def _dec(x: Any) -> str:
    return x.decode("utf-8", "replace") if isinstance(x, bytes) else str(x)


def _parse_json_maybe(v: Any) -> Any | None:
    if isinstance(v, (dict, list)):
        return v
    s = str(v).strip()
    if not s or s[0] not in "[{":
        return None
    try:
        return json.loads(s)
    except Exception:
        return None


def _flatten(obj: Any, prefix: str = "", out: list[tuple[str, Any]] | None = None, limit: int = 40000):
    if out is None:
        out = []
    if len(out) >= limit:
        return out

    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}.{k}" if prefix else str(k)
            out.append((p, v))
            parsed = _parse_json_maybe(v)
            if parsed is not None and parsed is not v:
                _flatten(parsed, p + "$json", out, limit)
            else:
                _flatten(v, p, out, limit)
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:100]):
            p = f"{prefix}[{i}]"
            out.append((p, v))
            _flatten(v, p, out, limit)
    return out


def _path_key(path: str) -> str:
    p = path.lower().replace("$json", "")
    return p.split(".")[-1].split("]")[-1].strip(".").lower()


def _msg_age_ms(msg_id: str) -> int:
    try:
        return int(time.time() * 1000) - int(msg_id.split("-", 1)[0])
    except Exception:
        return 10**12


def _as_float(v: Any) -> float | None:
    try:
        x = float(str(v).strip())
        if x > 0:
            return x
    except Exception:
        return None
    return None


def _stream_candidates() -> list[str]:
    streams = [
        "ticks:mme:opt:selected:zerodha",
        "ticks:mme:opt_selected:zerodha",
        "ticks:mme:options:selected:zerodha",
        "ticks:mme:opt:zerodha",
        "ticks:mme:nfo:zerodha",
    ]

    try:
        from app.mme_scalpx.core import names
        for attr in dir(names):
            if not attr.startswith("STREAM_"):
                continue
            value = getattr(names, attr)
            text = str(value)
            upper = attr.upper() + " " + text.upper()
            if "OPT" in upper or "NFO" in upper or "SELECTED" in upper:
                streams.append(text)
    except Exception:
        pass

    # preserve order, remove duplicates
    seen: set[str] = set()
    out: list[str] = []
    for s in streams:
        if s and s not in seen:
            seen.add(s)
            out.append(s)
    return out


def find_live_ltp(
    redis_client: Any,
    symbol: str,
    instrument_token: str,
    max_age_ms: int = 30000,
    count: int = 500,
) -> LtpSnapshot | None:
    symbol_u = str(symbol or "").strip().upper()
    token_s = str(instrument_token or "").strip()

    best: LtpSnapshot | None = None

    for stream in _stream_candidates():
        try:
            rows = redis_client.xrevrange(stream, "+", "-", count=count)
        except Exception:
            continue

        for msg_id_raw, raw_fields in rows:
            msg_id = _dec(msg_id_raw)
            age_ms = _msg_age_ms(msg_id)
            if age_ms > max_age_ms:
                continue

            fields = {_dec(k): _dec(v) for k, v in raw_fields.items()}
            flat = _flatten(fields)
            keys_seen = sorted({_path_key(p) for p, _ in flat})

            row_symbols: list[str] = []
            row_tokens: list[str] = []
            prices: list[float] = []

            for path, value in flat:
                key = _path_key(path)
                text = str(value).strip()
                if key in SYMBOL_KEYS and text:
                    row_symbols.append(text.upper())
                if key in TOKEN_KEYS and text:
                    row_tokens.append(text)
                if key in PRICE_KEYS:
                    price = _as_float(value)
                    if price is not None:
                        prices.append(price)

            symbol_match = bool(symbol_u and symbol_u in row_symbols)
            token_match = bool(token_s and token_s in row_tokens)

            # Some streams are selected-option-only and may not repeat symbol/token
            weak_match_allowed = not row_symbols and not row_tokens and len(prices) > 0

            if not (symbol_match or token_match or weak_match_allowed):
                continue
            if not prices:
                continue

            snap = LtpSnapshot(
                symbol=symbol,
                instrument_token=instrument_token,
                ltp=float(prices[0]),
                source_stream=stream,
                source_id=msg_id,
                source_age_ms=age_ms,
                raw_keys=keys_seen[:80],
            )

            if best is None or snap.source_age_ms < best.source_age_ms:
                best = snap

    return best
