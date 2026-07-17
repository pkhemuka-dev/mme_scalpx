from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable, Mapping


# R38TMBQ4_PURE_EXACT_POSITION_QUOTE_RESOLVER_V1

RESOLVER_VERSION = (
    "R38TMBQ4_EXACT_POSITION_QUOTE_RESOLVER_V1"
)

CALL_PATH = "shared_core.options.call.raw"
PUT_PATH = "shared_core.options.put.raw"
SELECTED_PATH = "shared_core.options.selected.raw"

DEFAULT_MAX_QUOTE_AGE_MS = 5_000
DEFAULT_FUTURE_TOLERANCE_MS = 1_000

SYMBOL_KEYS = (
    "option_symbol",
    "tradingsymbol",
    "trading_symbol",
    "symbol",
    "instrument_key",
)

TOKEN_KEYS = (
    "option_token",
    "instrument_token",
    "token",
    "instrument_id",
)

BID_KEYS = (
    "bid",
    "best_bid",
    "bid_price",
    "buy_price",
    "selected_option_bid",
    "quote_bid",
)

ASK_KEYS = (
    "ask",
    "best_ask",
    "ask_price",
    "sell_price",
    "selected_option_ask",
    "quote_ask",
)

TS_KEYS = (
    "ts_event_ns",
    "ts_ns",
    "timestamp_ns",
    "updated_at_ns",
    "exchange_timestamp_ns",
)


@dataclass(frozen=True)
class QuoteResolution:
    resolved: bool
    blocked: bool
    reason_code: str
    quote: dict[str, Any] | None
    diagnostics: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "resolved": self.resolved,
            "blocked": self.blocked,
            "reason_code": self.reason_code,
            "quote": (
                dict(self.quote)
                if self.quote is not None
                else None
            ),
            "diagnostics": dict(
                self.diagnostics
            ),
        }


def _text(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip()


def _upper(value: Any) -> str:
    return _text(value).upper()


def _symbol(value: Any) -> str:
    result = _upper(value)

    if ":" in result:
        result = result.split(
            ":",
            1,
        )[1]

    return result


def _integer(
    value: Any,
    default: int = 0,
) -> int:
    try:
        if isinstance(value, bool):
            return default

        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def _decimal(
    value: Any,
) -> Decimal | None:
    raw = _text(value)

    if not raw:
        return None

    try:
        result = Decimal(raw)
    except (InvalidOperation, ValueError):
        return None

    if not result.is_finite():
        return None

    return result


def _truthy(value: Any) -> bool:
    return _upper(value) in {
        "1",
        "TRUE",
        "YES",
        "ON",
    }


def _pick(
    mapping: Mapping[str, Any],
    names: Iterable[str],
) -> tuple[str, Any]:
    normalized = {
        str(key).lower(): value
        for key, value in mapping.items()
    }

    for name in names:
        if name in normalized:
            return name, normalized[name]

    return "", None


def _path_get(
    root: Any,
    dotted_path: str,
) -> Any:
    current = root

    for part in dotted_path.split("."):
        if not isinstance(
            current,
            Mapping,
        ):
            return None

        current = current.get(part)

    return current


def _position_branch(
    position: Mapping[str, Any],
) -> str:
    branch = _upper(
        position.get("branch_id")
        or position.get("side")
    )

    if branch == "CE":
        branch = "CALL"
    elif branch == "PE":
        branch = "PUT"

    position_side = _upper(
        position.get("position_side")
    )

    if not branch:
        if position_side in {
            "LONG_CALL",
            "CALL",
        }:
            branch = "CALL"
        elif position_side in {
            "LONG_PUT",
            "PUT",
        }:
            branch = "PUT"

    return branch


def _parse_leg(
    *,
    name: str,
    path: str,
    raw: Any,
    now_ns: int,
    local_utc_offset_ns: int,
    max_quote_age_ms: int,
    future_tolerance_ms: int,
) -> dict[str, Any]:
    if not isinstance(
        raw,
        Mapping,
    ):
        return {
            "name": name,
            "path": path,
            "valid_mapping": False,
            "reason": "path_not_mapping",
        }

    symbol_key, symbol_raw = _pick(
        raw,
        SYMBOL_KEYS,
    )
    token_key, token_raw = _pick(
        raw,
        TOKEN_KEYS,
    )
    bid_key, bid_raw = _pick(
        raw,
        BID_KEYS,
    )
    ask_key, ask_raw = _pick(
        raw,
        ASK_KEYS,
    )
    ts_key, ts_raw = _pick(
        raw,
        TS_KEYS,
    )

    symbol = _symbol(symbol_raw)
    token = _text(token_raw)
    bid = _decimal(bid_raw)
    ask = _decimal(ask_raw)
    raw_ts_ns = _integer(ts_raw)

    raw_age_ms = None
    adjusted_age_ms = None
    timestamp_domain = ""
    normalized_ts_ns = 0
    normalized_age_ms = None

    if raw_ts_ns > 0:
        raw_age_ms = (
            now_ns - raw_ts_ns
        ) / 1_000_000

        adjusted_ts_ns = (
            raw_ts_ns
            - local_utc_offset_ns
        )

        adjusted_age_ms = (
            now_ns - adjusted_ts_ns
        ) / 1_000_000

        if (
            -future_tolerance_ms
            <= raw_age_ms
            <= max_quote_age_ms
        ):
            timestamp_domain = (
                "UNIX_EPOCH_NS"
            )
            normalized_ts_ns = raw_ts_ns
            normalized_age_ms = raw_age_ms

        elif (
            local_utc_offset_ns != 0
            and -future_tolerance_ms
            <= adjusted_age_ms
            <= max_quote_age_ms
        ):
            timestamp_domain = (
                "LOCAL_WALLCLOCK_AS_EPOCH_NS"
            )
            normalized_ts_ns = (
                adjusted_ts_ns
            )
            normalized_age_ms = (
                adjusted_age_ms
            )

    quote_valid = bool(
        bid is not None
        and ask is not None
        and bid > 0
        and ask > 0
        and bid <= ask
    )

    timestamp_valid = bool(
        timestamp_domain
        in {
            "UNIX_EPOCH_NS",
            "LOCAL_WALLCLOCK_AS_EPOCH_NS",
        }
    )

    return {
        "name": name,
        "path": path,
        "valid_mapping": True,
        "symbol_key": symbol_key,
        "symbol": symbol,
        "token_key": token_key,
        "token": token,
        "bid_key": bid_key,
        "bid": bid,
        "ask_key": ask_key,
        "ask": ask,
        "quote_valid": quote_valid,
        "timestamp_key": ts_key,
        "raw_ts_ns": raw_ts_ns,
        "raw_age_ms": raw_age_ms,
        "offset_adjusted_age_ms":
            adjusted_age_ms,
        "timestamp_domain":
            timestamp_domain,
        "normalized_ts_ns":
            normalized_ts_ns,
        "normalized_age_ms":
            normalized_age_ms,
        "timestamp_valid":
            timestamp_valid,
    }


class ExactPositionQuoteResolver:
    def __init__(
        self,
        *,
        max_quote_age_ms: int = (
            DEFAULT_MAX_QUOTE_AGE_MS
        ),
        future_tolerance_ms: int = (
            DEFAULT_FUTURE_TOLERANCE_MS
        ),
    ):
        self.max_quote_age_ms = int(
            max_quote_age_ms
        )
        self.future_tolerance_ms = int(
            future_tolerance_ms
        )

        if self.max_quote_age_ms <= 0:
            raise ValueError(
                "max_quote_age_ms_must_be_positive"
            )

        if self.future_tolerance_ms < 0:
            raise ValueError(
                "future_tolerance_ms_must_be_nonnegative"
            )

    def resolve(
        self,
        *,
        family_surfaces: Mapping[str, Any],
        position: Mapping[str, Any],
        now_ns: int,
        local_utc_offset_ns: int,
    ) -> QuoteResolution:
        diagnostics: dict[str, Any] = {
            "resolver_version":
                RESOLVER_VERSION,
            "call_path": CALL_PATH,
            "put_path": PUT_PATH,
            "selected_path_role":
                "diagnostic_alias_only",
            "max_quote_age_ms":
                self.max_quote_age_ms,
            "future_tolerance_ms":
                self.future_tolerance_ms,
            "local_utc_offset_ns":
                int(local_utc_offset_ns),
        }

        has_position = _truthy(
            position.get("has_position")
        )

        qty_lots = _integer(
            position.get("qty_lots")
        )
        qty_units = _integer(
            position.get("qty_units")
        )

        if (
            not has_position
            or qty_lots <= 0
            or qty_units <= 0
        ):
            return QuoteResolution(
                resolved=False,
                blocked=True,
                reason_code=(
                    "position_not_open"
                ),
                quote=None,
                diagnostics=diagnostics,
            )

        position_symbol = _symbol(
            position.get(
                "entry_option_symbol"
            )
            or position.get(
                "option_symbol"
            )
        )

        position_token = _text(
            position.get(
                "entry_option_token"
            )
            or position.get(
                "option_token"
            )
            or position.get(
                "instrument_token"
            )
        )

        branch = _position_branch(
            position
        )

        diagnostics.update(
            {
                "position_symbol":
                    position_symbol,
                "position_token":
                    position_token,
                "position_branch":
                    branch,
            }
        )

        if (
            not position_symbol
            or not position_token
        ):
            return QuoteResolution(
                resolved=False,
                blocked=True,
                reason_code=(
                    "position_identity_missing"
                ),
                quote=None,
                diagnostics=diagnostics,
            )

        if branch not in {
            "CALL",
            "PUT",
        }:
            return QuoteResolution(
                resolved=False,
                blocked=True,
                reason_code=(
                    "position_branch_invalid"
                ),
                quote=None,
                diagnostics=diagnostics,
            )

        legs = [
            _parse_leg(
                name="CALL",
                path=CALL_PATH,
                raw=_path_get(
                    family_surfaces,
                    CALL_PATH,
                ),
                now_ns=now_ns,
                local_utc_offset_ns=(
                    local_utc_offset_ns
                ),
                max_quote_age_ms=(
                    self.max_quote_age_ms
                ),
                future_tolerance_ms=(
                    self.future_tolerance_ms
                ),
            ),
            _parse_leg(
                name="PUT",
                path=PUT_PATH,
                raw=_path_get(
                    family_surfaces,
                    PUT_PATH,
                ),
                now_ns=now_ns,
                local_utc_offset_ns=(
                    local_utc_offset_ns
                ),
                max_quote_age_ms=(
                    self.max_quote_age_ms
                ),
                future_tolerance_ms=(
                    self.future_tolerance_ms
                ),
            ),
        ]

        diagnostics["leg_summaries"] = [
            {
                key: (
                    str(value)
                    if isinstance(
                        value,
                        Decimal,
                    )
                    else value
                )
                for key, value in leg.items()
            }
            for leg in legs
        ]

        exact_matches = [
            leg
            for leg in legs
            if (
                leg.get("symbol")
                == position_symbol
                and leg.get("token")
                == position_token
            )
        ]

        diagnostics["exact_match_count"] = (
            len(exact_matches)
        )

        if not exact_matches:
            return QuoteResolution(
                resolved=False,
                blocked=True,
                reason_code=(
                    "exact_position_quote_not_found"
                ),
                quote=None,
                diagnostics=diagnostics,
            )

        if len(exact_matches) != 1:
            return QuoteResolution(
                resolved=False,
                blocked=True,
                reason_code=(
                    "exact_position_quote_ambiguous"
                ),
                quote=None,
                diagnostics=diagnostics,
            )

        matched = exact_matches[0]

        if matched.get("name") != branch:
            return QuoteResolution(
                resolved=False,
                blocked=True,
                reason_code=(
                    "position_branch_quote_mismatch"
                ),
                quote=None,
                diagnostics=diagnostics,
            )

        if not matched.get(
            "quote_valid"
        ):
            return QuoteResolution(
                resolved=False,
                blocked=True,
                reason_code=(
                    "exact_position_bid_ask_invalid"
                ),
                quote=None,
                diagnostics=diagnostics,
            )

        if not matched.get(
            "timestamp_valid"
        ):
            return QuoteResolution(
                resolved=False,
                blocked=True,
                reason_code=(
                    "exact_position_quote_stale_or_future"
                ),
                quote=None,
                diagnostics=diagnostics,
            )

        bid = matched["bid"]
        ask = matched["ask"]

        quote = {
            "option_symbol":
                position_symbol,
            "option_token":
                position_token,
            "instrument_token":
                position_token,
            "branch_id":
                branch,
            "bid": str(bid),
            "ask": str(ask),
            "spread": str(ask - bid),
            "ts_event_ns":
                int(
                    matched[
                        "normalized_ts_ns"
                    ]
                ),
            "raw_ts_event_ns":
                int(
                    matched[
                        "raw_ts_ns"
                    ]
                ),
            "timestamp_domain":
                matched[
                    "timestamp_domain"
                ],
            "normalized_age_ms":
                matched[
                    "normalized_age_ms"
                ],
            "quote_owner_path":
                matched["path"],
            "selected_path_role":
                "diagnostic_alias_only",
            "resolver_version":
                RESOLVER_VERSION,
        }

        diagnostics.update(
            {
                "resolved_path":
                    matched["path"],
                "resolved_branch":
                    matched["name"],
                "timestamp_domain":
                    matched[
                        "timestamp_domain"
                    ],
                "normalized_age_ms":
                    matched[
                        "normalized_age_ms"
                    ],
            }
        )

        return QuoteResolution(
            resolved=True,
            blocked=False,
            reason_code=(
                "exact_position_quote_resolved"
            ),
            quote=quote,
            diagnostics=diagnostics,
        )
