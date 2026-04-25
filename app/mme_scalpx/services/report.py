from __future__ import annotations

"""
app/mme_scalpx/services/report.py

Read-only session reconstruction and report generation for ScalpX MME.

Frozen contract
---------------
This module OWNS:
- read-only reconstruction from canonical streams and latest-state hashes
- report artifact generation on filesystem
- latest report status publication to HASH_STATE_REPORT
- report heartbeat publication to KEY_HEALTH_REPORT
- runtime entrypoint `run(context)`

This module DOES NOT own:
- execution truth
- position truth
- risk truth
- strategy truth
- broker truth
- command publication
- business-state mutation outside HASH_STATE_REPORT
- alternate startup roots
- service supervision

Design rules
------------
- report = read-only reconstruction only
- names.py is the only symbolic source of truth
- redisx.py is the canonical Redis façade for client lifecycle, hash access,
  heartbeat publication, and latest-state publication
- main.py is the only startup root
- runtime service entrypoint is exactly `run(context)`
- filesystem artifacts are atomic
- replay-safe and restart-safe

Important freeze rule
---------------------
settings.py proves only the typed report settings surface:

- settings.report.history_limit
- settings.report.include_entry_mode
- settings.report.ack_limit
- settings.report.order_limit
- settings.report.health_limit
- settings.report.error_limit

This module therefore:
- uses typed settings.report.* for those fields
- preserves the already-proven context override surface from the uploaded
  report lineage for:
    report_dir
    report_history_limit
    report_ack_limit
    report_order_limit
    report_health_limit
    report_error_limit
    report_health_tail_limit
    report_error_tail_limit
    report_interval_sec
    session_date
- does NOT invent any new settings fields or dependency factories

Freeze correction
-----------------
main.py already provides context.redis and context.settings in the canonical
runtime context. This service therefore does NOT fall back to RX.get_redis()
or any alternate dependency factory.
"""

import csv
import json
import logging
import tempfile
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, time as dt_time, timedelta, timezone
from pathlib import Path
from typing import Any, Final, Mapping, Sequence

from app.mme_scalpx.core import names as N
from app.mme_scalpx.core import redisx as RX
from app.mme_scalpx.core.settings import (
    DEFAULT_HEARTBEAT_TTL_MS,
    AppSettings,
    get_settings,
)

LOGGER = logging.getLogger("app.mme_scalpx.services.report")

IST: Final[timezone] = timezone(timedelta(hours=5, minutes=30))

REPORT_JSON: Final[str] = "session_report.json"
REPORT_MD: Final[str] = "session_report.md"
TRADES_CSV: Final[str] = "trades.csv"
TRADES_JSONL: Final[str] = "trades.jsonl"
DIAGNOSTICS_JSON: Final[str] = "diagnostics.json"
MANIFEST_JSON: Final[str] = "manifest.json"

DEFAULT_REPORT_DIR: Final[Path] = Path("run/reports")
DEFAULT_REPORT_HEALTH_TAIL_LIMIT: Final[int] = 50
DEFAULT_REPORT_ERROR_TAIL_LIMIT: Final[int] = 50
DEFAULT_REPORT_INTERVAL_SEC: Final[float] = 30.0


# ============================================================================
# Exceptions
# ============================================================================


class ReportError(RuntimeError):
    """Base report-service error."""


class ReportConfigError(ReportError):
    """Raised when report runtime configuration is invalid."""


class ReportContractError(ReportError):
    """Raised when a report contract or payload assumption is violated."""


# ============================================================================
# Required surface validation
# ============================================================================

_REQUIRED_NAME_EXPORTS: Final[tuple[str, ...]] = (
    "SERVICE_REPORT",
    "STREAM_TRADES_LEDGER",
    "STREAM_DECISIONS_ACK",
    "STREAM_ORDERS_MME",
    "STREAM_SYSTEM_HEALTH",
    "STREAM_SYSTEM_ERRORS",
    "HASH_STATE_POSITION_MME",
    "HASH_STATE_EXECUTION",
    "HASH_STATE_RISK",
    "HASH_STATE_REPORT",
    "HASH_STATE_RUNTIME",
    "HASH_PARAMS_MME",
    "HASH_PARAMS_MME_META",
    "KEY_HEALTH_REPORT",
    "HEALTH_STATUS_OK",
    "HEALTH_STATUS_WARN",
    "HEALTH_STATUS_ERROR",
    "ACK_RECEIVED",
    "ACK_REJECTED",
    "ACK_SENT_TO_BROKER",
    "ACK_FILLED",
    "ACK_FAILED",
    "ACK_EXIT_SENT",
    "ACK_EXIT_FILLED",
    "ENTRY_MODE_UNKNOWN",
)


def _validate_name_surface_or_die() -> None:
    missing = [name for name in _REQUIRED_NAME_EXPORTS if not hasattr(N, name)]
    if missing:
        raise ReportContractError(
            "report.py missing required names.py exports: "
            + ", ".join(sorted(missing))
        )


# ============================================================================
# Small helpers
# ============================================================================


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace").strip()
    return str(value).strip()


def _safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    raw = _safe_str(value).lower()
    if raw in {"1", "true", "yes", "y", "on"}:
        return True
    if raw in {"0", "false", "no", "n", "off"}:
        return False
    return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value in (None, ""):
            return default
        return int(float(value))
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        out = float(value)
        if out != out or out in (float("inf"), float("-inf")):
            return default
        return out
    except Exception:
        return default


def _parse_datetime(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
    if isinstance(value, date):
        return datetime.combine(value, dt_time.min, tzinfo=IST).astimezone(timezone.utc)

    raw = _safe_str(value)
    if not raw:
        return None

    if raw.isdigit():
        number = int(raw)
        if number >= 1_000_000_000_000_000_000:
            return datetime.fromtimestamp(number / 1_000_000_000, tz=timezone.utc)
        if number >= 1_000_000_000_000:
            return datetime.fromtimestamp(number / 1_000, tz=timezone.utc)
        return datetime.fromtimestamp(number, tz=timezone.utc)

    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _ensure_ist(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(IST)


def _dt_to_iso(value: datetime | None) -> str:
    return "" if value is None else value.isoformat()


def _stream_id_to_datetime(stream_id: str) -> datetime | None:
    raw = _safe_str(stream_id)
    if "-" not in raw:
        return None
    try:
        ms_text, _seq = raw.split("-", 1)
        return datetime.fromtimestamp(int(ms_text) / 1000, tz=timezone.utc)
    except Exception:
        return None


def _session_bounds_ist(session_day: date) -> tuple[datetime, datetime]:
    start_ist = datetime.combine(session_day, dt_time.min, tzinfo=IST)
    end_ist = start_ist + timedelta(days=1) - timedelta(microseconds=1)
    return start_ist.astimezone(timezone.utc), end_ist.astimezone(timezone.utc)


def _datetime_to_stream_floor_id(value: datetime) -> str:
    ts = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
    return f"{int(ts.timestamp() * 1000)}-0"


def _datetime_to_stream_ceil_id(value: datetime) -> str:
    ts = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
    return f"{int(ts.timestamp() * 1000)}-18446744073709551615"


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        delete=False,
        encoding="utf-8",
        dir=str(path.parent),
    ) as handle:
        handle.write(text)
        temp_path = Path(handle.name)
    temp_path.replace(path)


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        delete=False,
        encoding="utf-8",
        dir=str(path.parent),
    ) as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
        temp_path = Path(handle.name)
    temp_path.replace(path)


def _atomic_write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    headers: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row.keys():
            if key not in seen:
                headers.append(key)
                seen.add(key)

    with tempfile.NamedTemporaryFile(
        "w",
        delete=False,
        encoding="utf-8",
        newline="",
        dir=str(path.parent),
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in headers})
        temp_path = Path(handle.name)

    temp_path.replace(path)


def _atomic_write_jsonl(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        delete=False,
        encoding="utf-8",
        dir=str(path.parent),
    ) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            handle.write("\n")
        temp_path = Path(handle.name)
    temp_path.replace(path)


# ============================================================================
# Config
# ============================================================================


@dataclass(frozen=True, slots=True)
class ReportConfig:
    report_dir: Path
    history_limit: int
    include_entry_mode: bool
    ack_limit: int
    order_limit: int
    health_limit: int
    error_limit: int
    health_tail_limit: int
    error_tail_limit: int
    interval_sec: float
    heartbeat_ttl_ms: int

    @classmethod
    def from_runtime(
        cls,
        *,
        settings: AppSettings,
        context: Any | None = None,
    ) -> "ReportConfig":
        ctx = context

        report_dir = Path(str(getattr(ctx, "report_dir", DEFAULT_REPORT_DIR)))
        history_limit = max(
            1,
            int(getattr(ctx, "report_history_limit", settings.report.history_limit)),
        )
        ack_limit = max(
            1,
            int(getattr(ctx, "report_ack_limit", settings.report.ack_limit)),
        )
        order_limit = max(
            1,
            int(getattr(ctx, "report_order_limit", settings.report.order_limit)),
        )
        health_limit = max(
            1,
            int(getattr(ctx, "report_health_limit", settings.report.health_limit)),
        )
        error_limit = max(
            1,
            int(getattr(ctx, "report_error_limit", settings.report.error_limit)),
        )
        health_tail_limit = max(
            1,
            int(
                getattr(
                    ctx,
                    "report_health_tail_limit",
                    DEFAULT_REPORT_HEALTH_TAIL_LIMIT,
                )
            ),
        )
        error_tail_limit = max(
            1,
            int(
                getattr(
                    ctx,
                    "report_error_tail_limit",
                    DEFAULT_REPORT_ERROR_TAIL_LIMIT,
                )
            ),
        )
        interval_sec = max(
            1.0,
            float(getattr(ctx, "report_interval_sec", DEFAULT_REPORT_INTERVAL_SEC)),
        )

        return cls(
            report_dir=report_dir,
            history_limit=history_limit,
            include_entry_mode=bool(settings.report.include_entry_mode),
            ack_limit=ack_limit,
            order_limit=order_limit,
            health_limit=health_limit,
            error_limit=error_limit,
            health_tail_limit=health_tail_limit,
            error_tail_limit=error_tail_limit,
            interval_sec=interval_sec,
            heartbeat_ttl_ms=int(DEFAULT_HEARTBEAT_TTL_MS),
        )


# ============================================================================
# Data models
# ============================================================================


@dataclass(slots=True)
class StreamRecord:
    stream: str
    stream_id: str
    ts: datetime | None
    fields: dict[str, Any]


@dataclass(slots=True)
class TradeRecord:
    trade_key: str

    decision_id: str = ""
    position_id: str = ""
    entry_order_id: str = ""
    exit_order_id: str = ""

    symbol: str = ""
    instrument: str = ""
    side: str = ""
    expiry: str = ""
    strike: float | None = None

    entry_mode: str = ""
    fallback_mode: bool = False

    entry_ts: datetime | None = None
    exit_ts: datetime | None = None
    signal_ts: datetime | None = None
    confirm_ts: datetime | None = None

    entry_price: float = 0.0
    exit_price: float = 0.0
    entry_qty: int = 0
    exit_qty: int = 0
    filled_qty: int = 0

    realized_pnl: float = 0.0
    gross_pnl: float = 0.0
    net_pnl: float = 0.0
    fees: float = 0.0
    hold_seconds: float = 0.0

    exit_reason: str = ""
    entry_ack_status: str = ""
    exit_ack_status: str = ""

    partial_fill: bool = False
    degraded: bool = False
    broker_mismatch: bool = False

    raw_events: list[dict[str, Any]] = field(default_factory=list)

    @property
    def closed(self) -> bool:
        return self.entry_ts is not None and self.exit_ts is not None

    @property
    def won(self) -> bool:
        return self.net_pnl > 0.0

    @property
    def lost(self) -> bool:
        return self.net_pnl < 0.0

    def to_row(self, *, include_entry_mode: bool) -> dict[str, Any]:
        payload = asdict(self)
        payload["entry_ts"] = _dt_to_iso(_ensure_ist(self.entry_ts))
        payload["exit_ts"] = _dt_to_iso(_ensure_ist(self.exit_ts))
        payload["signal_ts"] = _dt_to_iso(_ensure_ist(self.signal_ts))
        payload["confirm_ts"] = _dt_to_iso(_ensure_ist(self.confirm_ts))
        if not include_entry_mode:
            payload.pop("entry_mode", None)
        return payload


@dataclass(slots=True)
class Diagnostics:
    ack_total: int = 0
    health_total: int = 0
    error_total: int = 0
    reject_total: int = 0
    failed_total: int = 0
    degraded_records: int = 0
    broker_mismatch_records: int = 0
    partial_fill_records: int = 0


@dataclass(slots=True)
class SessionReport:
    session_date: str
    generated_at: str
    session_start: str
    session_end: str

    trade_count: int = 0
    closed_trade_count: int = 0
    open_trade_count: int = 0

    win_count: int = 0
    loss_count: int = 0
    flat_count: int = 0
    win_rate_pct: float = 0.0

    gross_pnl: float = 0.0
    net_pnl: float = 0.0
    fees_total: float = 0.0
    avg_hold_seconds: float = 0.0
    best_trade_pnl: float = 0.0
    worst_trade_pnl: float = 0.0

    side_mix: dict[str, int] = field(default_factory=dict)
    entry_mode_mix: dict[str, int] = field(default_factory=dict)
    exit_reason_mix: dict[str, int] = field(default_factory=dict)

    diagnostics: dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Redis adapter
# ============================================================================


class RedisAdapter:
    """
    Thin read-only adapter over the canonical Redis client supplied by
    main.py / redisx.py.

    This adapter does not create or own clients. It only reads through the
    canonical client already composed by main.py.
    """

    def __init__(self, client: Any) -> None:
        self.client = client

    def hgetall(self, key: str) -> dict[str, Any]:
        return RX.hgetall(key, client=self.client)

    def xrange(
        self,
        stream: str,
        *,
        start: str,
        end: str,
        count: int,
    ) -> list[StreamRecord]:
        """
        Historical stream-range read using the canonical client composed by
        main.py. redisx.py does not expose a proven historical XRANGE wrapper in
        the uploaded API surface, so this remains a read-only client operation.
        """
        try:
            rows = self.client.xrange(stream, min=start, max=end, count=count)
        except TypeError:
            rows = self.client.xrange(stream, start, end, count=count)

        records: list[StreamRecord] = []
        for stream_id, fields in rows:
            sid = _safe_str(stream_id)
            decoded = {_safe_str(k): _safe_str(v) for k, v in fields.items()}
            records.append(
                StreamRecord(
                    stream=stream,
                    stream_id=sid,
                    ts=_stream_id_to_datetime(sid),
                    fields=decoded,
                )
            )
        return records


# ============================================================================
# Repository
# ============================================================================


class ReportRepository:
    def __init__(self, redis: RedisAdapter, cfg: ReportConfig) -> None:
        self.redis = redis
        self.cfg = cfg

    def _load_stream_window(
        self,
        stream: str,
        *,
        start_dt: datetime,
        end_dt: datetime,
        limit: int,
    ) -> list[StreamRecord]:
        return self.redis.xrange(
            stream,
            start=_datetime_to_stream_floor_id(start_dt),
            end=_datetime_to_stream_ceil_id(end_dt),
            count=limit,
        )

    def load_trade_ledger(
        self,
        *,
        start_dt: datetime,
        end_dt: datetime,
    ) -> list[StreamRecord]:
        return self._load_stream_window(
            N.STREAM_TRADES_LEDGER,
            start_dt=start_dt,
            end_dt=end_dt,
            limit=self.cfg.history_limit,
        )

    def load_decision_acks(
        self,
        *,
        start_dt: datetime,
        end_dt: datetime,
    ) -> list[StreamRecord]:
        return self._load_stream_window(
            N.STREAM_DECISIONS_ACK,
            start_dt=start_dt,
            end_dt=end_dt,
            limit=self.cfg.ack_limit,
        )

    def load_orders(
        self,
        *,
        start_dt: datetime,
        end_dt: datetime,
    ) -> list[StreamRecord]:
        return self._load_stream_window(
            N.STREAM_ORDERS_MME,
            start_dt=start_dt,
            end_dt=end_dt,
            limit=self.cfg.order_limit,
        )

    def load_health(
        self,
        *,
        start_dt: datetime,
        end_dt: datetime,
    ) -> list[StreamRecord]:
        return self._load_stream_window(
            N.STREAM_SYSTEM_HEALTH,
            start_dt=start_dt,
            end_dt=end_dt,
            limit=self.cfg.health_limit,
        )

    def load_errors(
        self,
        *,
        start_dt: datetime,
        end_dt: datetime,
    ) -> list[StreamRecord]:
        return self._load_stream_window(
            N.STREAM_SYSTEM_ERRORS,
            start_dt=start_dt,
            end_dt=end_dt,
            limit=self.cfg.error_limit,
        )

    def load_state_snapshot(self) -> dict[str, dict[str, Any]]:
        return {
            "position": self.redis.hgetall(N.HASH_STATE_POSITION_MME),
            "execution": self.redis.hgetall(N.HASH_STATE_EXECUTION),
            "risk": self.redis.hgetall(N.HASH_STATE_RISK),
            "report": self.redis.hgetall(N.HASH_STATE_REPORT),
            "runtime": self.redis.hgetall(N.HASH_STATE_RUNTIME),
            "params": self.redis.hgetall(N.HASH_PARAMS_MME),
            "params_meta": self.redis.hgetall(N.HASH_PARAMS_MME_META),
        }


# ============================================================================
# Review engine
# ============================================================================


class ReviewEngine:
    def __init__(self, repo: ReportRepository, *, cfg: ReportConfig, clock: Any) -> None:
        self.repo = repo
        self.cfg = cfg
        self.clock = clock

    def _guess_trade_key(self, payload: Mapping[str, Any], index: int) -> str:
        for key in (
            "trade_key",
            "position_id",
            "decision_id",
            "entry_order_id",
            "exit_order_id",
            "order_id",
        ):
            value = _safe_str(payload.get(key))
            if value:
                return value
        return f"trade-{index}"

    def _normalize_entry_mode(self, payload: Mapping[str, Any]) -> str:
        value = _safe_str(payload.get("entry_mode")).upper()
        return value or N.ENTRY_MODE_UNKNOWN

    def _normalize_side(self, payload: Mapping[str, Any]) -> str:
        for key in ("side", "position_side", "action"):
            value = _safe_str(payload.get(key)).upper()
            if value:
                return value
        return ""

    def _normalize_symbol(self, payload: Mapping[str, Any]) -> str:
        for key in ("symbol", "option_symbol", "tradingsymbol"):
            value = _safe_str(payload.get(key))
            if value:
                return value
        return ""

    def _normalize_exit_reason(self, payload: Mapping[str, Any]) -> str:
        for key in ("exit_reason", "reason_code", "close_reason"):
            value = _safe_str(payload.get(key))
            if value:
                return value
        return ""

    def _event_ts(self, payload: Mapping[str, Any], fallback: datetime | None) -> datetime | None:
        for key in (
            "ts_ns",
            "ts_event_ns",
            "ts_ms",
            "ts",
            "timestamp",
            "entry_ts",
            "exit_ts",
            "signal_ts",
            "confirm_ts",
        ):
            parsed = _parse_datetime(payload.get(key))
            if parsed is not None:
                return parsed
        return fallback

    def _is_entry_payload(self, payload: Mapping[str, Any]) -> bool:
        return _safe_bool(payload.get("is_entry")) or bool(
            payload.get("entry_ts") or payload.get("entry_price") or payload.get("entry_qty")
        )

    def _is_exit_payload(self, payload: Mapping[str, Any]) -> bool:
        return _safe_bool(payload.get("is_exit")) or bool(
            payload.get("exit_ts") or payload.get("exit_price") or payload.get("exit_qty")
        )

    def _reconstruct_trades(
        self,
        *,
        ledger: Sequence[StreamRecord],
        acks: Sequence[StreamRecord],
        orders: Sequence[StreamRecord],
    ) -> list[TradeRecord]:
        by_key: dict[str, TradeRecord] = {}
        ack_by_trade: dict[str, list[StreamRecord]] = defaultdict(list)
        order_by_trade: dict[str, list[StreamRecord]] = defaultdict(list)

        for idx, ack in enumerate(acks):
            ack_by_trade[self._guess_trade_key(ack.fields, idx)].append(ack)

        for idx, order in enumerate(orders):
            order_by_trade[self._guess_trade_key(order.fields, idx)].append(order)

        for idx, record in enumerate(ledger):
            payload = record.fields
            trade_key = self._guess_trade_key(payload, idx)
            trade = by_key.get(trade_key)
            if trade is None:
                trade = TradeRecord(trade_key=trade_key)
                by_key[trade_key] = trade

            event_ts = self._event_ts(payload, record.ts)
            trade.raw_events.append(
                {
                    "stream": record.stream,
                    "stream_id": record.stream_id,
                    "ts": _dt_to_iso(_ensure_ist(event_ts)),
                    "fields": dict(payload),
                }
            )

            trade.decision_id = trade.decision_id or _safe_str(payload.get("decision_id"))
            trade.position_id = trade.position_id or _safe_str(payload.get("position_id"))
            trade.entry_order_id = trade.entry_order_id or _safe_str(
                payload.get("entry_order_id") or payload.get("order_id")
            )
            trade.exit_order_id = trade.exit_order_id or _safe_str(payload.get("exit_order_id"))

            trade.symbol = trade.symbol or self._normalize_symbol(payload)
            trade.instrument = trade.instrument or _safe_str(
                payload.get("instrument") or payload.get("instrument_token") or payload.get("token")
            )
            trade.side = trade.side or self._normalize_side(payload)
            trade.expiry = trade.expiry or _safe_str(payload.get("expiry"))

            if trade.strike is None and payload.get("strike") not in (None, ""):
                trade.strike = _safe_float(payload.get("strike"))

            trade.entry_mode = trade.entry_mode or self._normalize_entry_mode(payload)
            trade.fallback_mode = trade.fallback_mode or (
                trade.entry_mode == _safe_str(getattr(N, "ENTRY_MODE_FALLBACK", "FALLBACK")).upper()
            )

            trade.signal_ts = trade.signal_ts or _parse_datetime(payload.get("signal_ts"))
            trade.confirm_ts = trade.confirm_ts or _parse_datetime(payload.get("confirm_ts"))

            if self._is_entry_payload(payload):
                trade.entry_ts = trade.entry_ts or event_ts
                trade.entry_price = trade.entry_price or _safe_float(
                    payload.get("entry_price") or payload.get("fill_price") or payload.get("avg_fill_price")
                )
                trade.entry_qty = trade.entry_qty or _safe_int(
                    payload.get("entry_qty") or payload.get("filled_qty") or payload.get("quantity")
                )

            if self._is_exit_payload(payload):
                trade.exit_ts = trade.exit_ts or event_ts
                trade.exit_price = trade.exit_price or _safe_float(
                    payload.get("exit_price") or payload.get("fill_price") or payload.get("avg_fill_price")
                )
                trade.exit_qty = trade.exit_qty or _safe_int(
                    payload.get("exit_qty") or payload.get("filled_qty") or payload.get("quantity")
                )

            trade.realized_pnl = trade.realized_pnl or _safe_float(
                payload.get("realized_pnl") or payload.get("pnl") or payload.get("net_pnl")
            )
            trade.fees += _safe_float(payload.get("fees") or payload.get("fee") or payload.get("charges"), 0.0)
            trade.exit_reason = trade.exit_reason or self._normalize_exit_reason(payload)
            trade.partial_fill = trade.partial_fill or _safe_bool(payload.get("partial_fill"))
            trade.broker_mismatch = trade.broker_mismatch or _safe_bool(payload.get("broker_mismatch"))
            trade.degraded = trade.degraded or _safe_bool(payload.get("degraded"))

        for trade_key, trade in by_key.items():
            for record in ack_by_trade.get(trade_key, []):
                payload = record.fields
                ack_status = _safe_str(payload.get("ack_type") or payload.get("status")).upper()

                trade.entry_mode = trade.entry_mode or self._normalize_entry_mode(payload)
                trade.entry_order_id = trade.entry_order_id or _safe_str(
                    payload.get("order_id") or payload.get("entry_order_id")
                )
                trade.exit_order_id = trade.exit_order_id or _safe_str(payload.get("exit_order_id"))
                trade.exit_reason = trade.exit_reason or self._normalize_exit_reason(payload)

                if ack_status in {N.ACK_RECEIVED, N.ACK_SENT_TO_BROKER, N.ACK_FILLED}:
                    trade.entry_ack_status = ack_status
                elif ack_status in {N.ACK_EXIT_SENT, N.ACK_EXIT_FILLED}:
                    trade.exit_ack_status = ack_status
                elif ack_status in {N.ACK_REJECTED, N.ACK_FAILED}:
                    trade.entry_ack_status = trade.entry_ack_status or ack_status
                    trade.degraded = True

            for record in order_by_trade.get(trade_key, []):
                payload = record.fields
                trade.entry_mode = trade.entry_mode or self._normalize_entry_mode(payload)
                trade.entry_order_id = trade.entry_order_id or _safe_str(
                    payload.get("order_id") or payload.get("entry_order_id")
                )
                trade.exit_order_id = trade.exit_order_id or _safe_str(payload.get("exit_order_id"))
                trade.partial_fill = trade.partial_fill or _safe_bool(payload.get("partial_fill"))
                trade.broker_mismatch = trade.broker_mismatch or _safe_bool(payload.get("broker_mismatch"))
                trade.degraded = trade.degraded or _safe_bool(payload.get("degraded"))

            if trade.entry_ts and trade.exit_ts:
                trade.hold_seconds = max((trade.exit_ts - trade.entry_ts).total_seconds(), 0.0)

            trade.gross_pnl = trade.realized_pnl
            trade.net_pnl = trade.gross_pnl - trade.fees

            if trade.filled_qty == 0:
                trade.filled_qty = trade.entry_qty or trade.exit_qty

            if not trade.entry_mode:
                trade.entry_mode = N.ENTRY_MODE_UNKNOWN

        return sorted(
            by_key.values(),
            key=lambda item: (
                item.entry_ts or item.exit_ts or datetime.min.replace(tzinfo=timezone.utc),
                item.trade_key,
            ),
        )

    def _build_diagnostics(
        self,
        *,
        acks: Sequence[StreamRecord],
        health: Sequence[StreamRecord],
        errors: Sequence[StreamRecord],
        ledger: Sequence[StreamRecord],
    ) -> Diagnostics:
        diagnostics = Diagnostics(
            ack_total=len(acks),
            health_total=len(health),
            error_total=len(errors),
        )

        for ack in acks:
            ack_status = _safe_str(ack.fields.get("ack_type") or ack.fields.get("status")).upper()
            if ack_status == N.ACK_REJECTED:
                diagnostics.reject_total += 1
            if ack_status == N.ACK_FAILED:
                diagnostics.failed_total += 1

        for event in ledger:
            payload = event.fields
            diagnostics.degraded_records += int(_safe_bool(payload.get("degraded")))
            diagnostics.broker_mismatch_records += int(_safe_bool(payload.get("broker_mismatch")))
            diagnostics.partial_fill_records += int(_safe_bool(payload.get("partial_fill")))

        return diagnostics

    def _build_summary_report(
        self,
        *,
        session_day: date,
        session_start: datetime,
        session_end: datetime,
        trades: Sequence[TradeRecord],
        diagnostics: Diagnostics,
    ) -> SessionReport:
        now_dt = (
            self.clock.wall_time_ist()
            if hasattr(self.clock, "wall_time_ist")
            else datetime.now(tz=IST)
        )

        report = SessionReport(
            session_date=session_day.isoformat(),
            generated_at=_dt_to_iso(now_dt),
            session_start=_dt_to_iso(_ensure_ist(session_start)),
            session_end=_dt_to_iso(_ensure_ist(session_end)),
        )

        report.trade_count = len(trades)
        report.closed_trade_count = sum(1 for trade in trades if trade.closed)
        report.open_trade_count = report.trade_count - report.closed_trade_count

        closed_trades = [trade for trade in trades if trade.closed]
        wins = [trade for trade in closed_trades if trade.won]
        losses = [trade for trade in closed_trades if trade.lost]
        flats = [trade for trade in closed_trades if not trade.won and not trade.lost]

        report.win_count = len(wins)
        report.loss_count = len(losses)
        report.flat_count = len(flats)
        if closed_trades:
            report.win_rate_pct = round((len(wins) / len(closed_trades)) * 100.0, 2)

        report.gross_pnl = round(sum(trade.gross_pnl for trade in closed_trades), 4)
        report.net_pnl = round(sum(trade.net_pnl for trade in closed_trades), 4)
        report.fees_total = round(sum(trade.fees for trade in closed_trades), 4)

        if closed_trades:
            report.avg_hold_seconds = round(
                sum(trade.hold_seconds for trade in closed_trades) / len(closed_trades),
                4,
            )
            report.best_trade_pnl = max((trade.net_pnl for trade in closed_trades), default=0.0)
            report.worst_trade_pnl = min((trade.net_pnl for trade in closed_trades), default=0.0)

        report.side_mix = dict(sorted(Counter(trade.side for trade in trades if trade.side).items()))
        report.entry_mode_mix = dict(
            sorted(Counter(trade.entry_mode for trade in trades if trade.entry_mode).items())
        )
        report.exit_reason_mix = dict(
            sorted(Counter(trade.exit_reason for trade in trades if trade.exit_reason).items())
        )
        report.diagnostics = asdict(diagnostics)
        return report

    def _record_preview(self, record: StreamRecord) -> dict[str, Any]:
        return {
            "stream": record.stream,
            "stream_id": record.stream_id,
            "ts": _dt_to_iso(_ensure_ist(record.ts)),
            "fields": dict(record.fields),
        }

    def _render_markdown(
        self,
        *,
        session_report: SessionReport,
        trades: Sequence[TradeRecord],
        diagnostics_payload: Mapping[str, Any],
    ) -> str:
        lines: list[str] = []
        lines.append(f"# ScalpX MME Session Report — {session_report.session_date}")
        lines.append("")
        lines.append(f"- Generated at: {session_report.generated_at}")
        lines.append(f"- Session start: {session_report.session_start}")
        lines.append(f"- Session end: {session_report.session_end}")
        lines.append("")
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- Trades: {session_report.trade_count}")
        lines.append(f"- Closed trades: {session_report.closed_trade_count}")
        lines.append(f"- Open trades: {session_report.open_trade_count}")
        lines.append(f"- Wins: {session_report.win_count}")
        lines.append(f"- Losses: {session_report.loss_count}")
        lines.append(f"- Flats: {session_report.flat_count}")
        lines.append(f"- Win rate: {session_report.win_rate_pct}%")
        lines.append(f"- Gross PnL: {session_report.gross_pnl}")
        lines.append(f"- Net PnL: {session_report.net_pnl}")
        lines.append(f"- Fees: {session_report.fees_total}")
        lines.append(f"- Avg hold seconds: {session_report.avg_hold_seconds}")
        lines.append("")
        lines.append("## Mix")
        lines.append("")
        lines.append(
            f"- Side mix: {json.dumps(session_report.side_mix, ensure_ascii=False, sort_keys=True)}"
        )
        if self.cfg.include_entry_mode:
            lines.append(
                f"- Entry mode mix: {json.dumps(session_report.entry_mode_mix, ensure_ascii=False, sort_keys=True)}"
            )
        lines.append(
            f"- Exit reason mix: {json.dumps(session_report.exit_reason_mix, ensure_ascii=False, sort_keys=True)}"
        )
        lines.append("")
        lines.append("## Diagnostics")
        lines.append("")
        diag = diagnostics_payload["diagnostics"]
        lines.append(f"- ACK total: {diag['ack_total']}")
        lines.append(f"- Health total: {diag['health_total']}")
        lines.append(f"- Error total: {diag['error_total']}")
        lines.append(f"- Reject total: {diag['reject_total']}")
        lines.append(f"- Failed total: {diag['failed_total']}")
        lines.append("")
        lines.append("## Trades")
        lines.append("")
        if not trades:
            lines.append("No trades reconstructed for this session.")
        else:
            for idx, trade in enumerate(trades, start=1):
                lines.append(f"### Trade {idx} — {trade.trade_key}")
                lines.append(f"- Side: {trade.side}")
                if self.cfg.include_entry_mode:
                    lines.append(f"- Entry mode: {trade.entry_mode}")
                lines.append(f"- Symbol: {trade.symbol}")
                lines.append(f"- Entry time: {_dt_to_iso(_ensure_ist(trade.entry_ts))}")
                lines.append(f"- Exit time: {_dt_to_iso(_ensure_ist(trade.exit_ts))}")
                lines.append(f"- Net PnL: {trade.net_pnl}")
                lines.append(f"- Exit reason: {trade.exit_reason}")
                lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    def build_session_pack(self, *, session_day: date) -> dict[str, Any]:
        session_start, session_end = _session_bounds_ist(session_day)

        ledger = self.repo.load_trade_ledger(start_dt=session_start, end_dt=session_end)
        acks = self.repo.load_decision_acks(start_dt=session_start, end_dt=session_end)
        orders = self.repo.load_orders(start_dt=session_start, end_dt=session_end)
        health = self.repo.load_health(start_dt=session_start, end_dt=session_end)
        errors = self.repo.load_errors(start_dt=session_start, end_dt=session_end)
        state_snapshot = self.repo.load_state_snapshot()

        trades = self._reconstruct_trades(ledger=ledger, acks=acks, orders=orders)
        diagnostics = self._build_diagnostics(
            acks=acks,
            health=health,
            errors=errors,
            ledger=ledger,
        )
        session_report = self._build_summary_report(
            session_day=session_day,
            session_start=session_start,
            session_end=session_end,
            trades=trades,
            diagnostics=diagnostics,
        )

        diagnostics_payload = {
            "state_snapshot": state_snapshot,
            "diagnostics": asdict(diagnostics),
            "source_counts": {
                "ledger": len(ledger),
                "acks": len(acks),
                "orders": len(orders),
                "health": len(health),
                "errors": len(errors),
            },
            "health_tail": [
                self._record_preview(record)
                for record in health[-self.cfg.health_tail_limit :]
            ],
            "error_tail": [
                self._record_preview(record)
                for record in errors[-self.cfg.error_tail_limit :]
            ],
        }

        trades_rows = [
            trade.to_row(include_entry_mode=self.cfg.include_entry_mode)
            for trade in trades
        ]

        manifest = {
            "service_name": N.SERVICE_REPORT,
            "service_module": "app.mme_scalpx.services.report",
            "session_date": session_day.isoformat(),
            "generated_at": session_report.generated_at,
            "read_only": True,
            "files": [
                REPORT_JSON,
                REPORT_MD,
                TRADES_CSV,
                TRADES_JSONL,
                DIAGNOSTICS_JSON,
                MANIFEST_JSON,
            ],
        }

        return {
            "session_report": asdict(session_report),
            "trades_rows": trades_rows,
            "session_markdown": self._render_markdown(
                session_report=session_report,
                trades=trades,
                diagnostics_payload=diagnostics_payload,
            ),
            "diagnostics": diagnostics_payload,
            "manifest": manifest,
        }


# ============================================================================
# Service
# ============================================================================


class ReportService:
    def __init__(
        self,
        *,
        cfg: ReportConfig,
        redis_client: Any,
        clock: Any,
        shutdown: Any,
        instance_id: str,
    ) -> None:
        self.cfg = cfg
        self.redis_client = redis_client
        self.clock = clock
        self.shutdown = shutdown
        self.instance_id = instance_id
        self.redis = RedisAdapter(redis_client)
        self.repo = ReportRepository(self.redis, cfg)
        self.engine = ReviewEngine(self.repo, cfg=cfg, clock=clock)

        self._validate_runtime_contract()

    def _validate_runtime_contract(self) -> None:
        if self.redis_client is None:
            raise ReportConfigError("report requires redis client")
        if self.clock is None or not hasattr(self.clock, "wall_time_ns"):
            raise ReportConfigError("report requires context.clock.wall_time_ns()")
        if self.shutdown is None or not hasattr(self.shutdown, "wait") or not hasattr(self.shutdown, "is_set"):
            raise ReportConfigError("report requires context.shutdown.wait()/is_set()")
        if not self.instance_id:
            raise ReportConfigError("report requires non-empty instance_id")
        if not RX.ping_redis(client=self.redis_client):
            raise ReportConfigError("report redis ping failed during startup")

    def _resolve_session_date(self, context: Any) -> date:
        value = getattr(context, "session_date", None)
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if isinstance(value, datetime):
            dt = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
            return dt.astimezone(IST).date()
        if value not in (None, ""):
            return datetime.strptime(str(value), "%Y-%m-%d").date()

        if hasattr(self.clock, "wall_time_ist"):
            return self.clock.wall_time_ist().date()
        if hasattr(self.clock, "wall_time_utc"):
            return self.clock.wall_time_utc().astimezone(IST).date()
        return datetime.now(tz=IST).date()

    def _session_dir(self, session_day: date) -> Path:
        return self.cfg.report_dir / session_day.isoformat()

    def _publish_status(
        self,
        *,
        status: str,
        session_day: date,
        session_dir: Path,
        detail: str,
    ) -> None:
        now_ns = int(self.clock.wall_time_ns())
        generated_at = (
            self.clock.wall_time_ist().isoformat()
            if hasattr(self.clock, "wall_time_ist")
            else datetime.now(tz=IST).isoformat()
        )

        RX.write_hash_fields(
            N.HASH_STATE_REPORT,
            {
                "service_name": N.SERVICE_REPORT,
                "instance_id": self.instance_id,
                "status": status,
                "session_date": session_day.isoformat(),
                "generated_at": generated_at,
                "latest_session_dir": str(session_dir),
                "read_only": "1",
                "detail": detail,
                "updated_at_ns": str(now_ns),
            },
            client=self.redis_client,
        )

    def _publish_heartbeat(self, *, status: str) -> None:
        RX.write_heartbeat(
            N.KEY_HEALTH_REPORT,
            service=N.SERVICE_REPORT,
            instance_id=self.instance_id,
            status=status,
            ts_event_ns=int(self.clock.wall_time_ns()),
            ttl_ms=self.cfg.heartbeat_ttl_ms,
            client=self.redis_client,
        )

    def _publish_shutdown_heartbeat(self) -> None:
        try:
            RX.write_heartbeat(
                N.KEY_HEALTH_REPORT,
                service=N.SERVICE_REPORT,
                instance_id=self.instance_id,
                status="STOPPED",
                ts_event_ns=int(self.clock.wall_time_ns()),
                ttl_ms=self.cfg.heartbeat_ttl_ms,
                client=self.redis_client,
            )
        except Exception:
            LOGGER.exception("report_shutdown_heartbeat_failed")

    def run_once(self, *, session_day: date) -> Path:
        pack = self.engine.build_session_pack(session_day=session_day)
        session_dir = self._session_dir(session_day)
        session_dir.mkdir(parents=True, exist_ok=True)

        _atomic_write_json(session_dir / REPORT_JSON, pack["session_report"])
        _atomic_write_text(session_dir / REPORT_MD, pack["session_markdown"])
        _atomic_write_csv(session_dir / TRADES_CSV, pack["trades_rows"])
        _atomic_write_jsonl(session_dir / TRADES_JSONL, pack["trades_rows"])
        _atomic_write_json(session_dir / DIAGNOSTICS_JSON, pack["diagnostics"])
        _atomic_write_json(session_dir / MANIFEST_JSON, pack["manifest"])

        self._publish_status(
            status=N.HEALTH_STATUS_OK,
            session_day=session_day,
            session_dir=session_dir,
            detail="report_written",
        )
        return session_dir

    def start(self, *, context: Any) -> int:
        session_day = self._resolve_session_date(context)
        last_run_monotonic = 0.0
        heartbeat_interval_sec = max(1.0, min(self.cfg.interval_sec / 3.0, 3.0))

        try:
            while True:
                now_monotonic = (
                    self.clock.monotonic_ns() / 1_000_000_000.0
                    if hasattr(self.clock, "monotonic_ns")
                    else 0.0
                )

                self._publish_heartbeat(status=N.HEALTH_STATUS_OK)

                should_run = (
                    last_run_monotonic == 0.0
                    or now_monotonic == 0.0
                    or (now_monotonic - last_run_monotonic) >= self.cfg.interval_sec
                )

                if should_run:
                    self.run_once(session_day=session_day)
                    if now_monotonic != 0.0:
                        last_run_monotonic = now_monotonic

                    if getattr(context, "session_date", None) not in (None, ""):
                        break

                    session_day = self._resolve_session_date(context)

                if self.shutdown.is_set():
                    break

                self.shutdown.wait(heartbeat_interval_sec)
        finally:
            self._publish_shutdown_heartbeat()

        return 0


# ============================================================================
# Canonical entrypoint
# ============================================================================


def _resolve_redis_client_from_context(context: Any) -> Any:
    redis_runtime = getattr(context, "redis", None)
    if redis_runtime is None:
        raise ReportConfigError("run(context) requires context.redis")
    if hasattr(redis_runtime, "sync"):
        return redis_runtime.sync
    return redis_runtime


def _resolve_settings_from_context(context: Any) -> AppSettings:
    settings = getattr(context, "settings", None)
    if settings is None:
        settings = get_settings()
    if not isinstance(settings, AppSettings):
        raise ReportConfigError(
            "report requires context.settings or get_settings() returning AppSettings"
        )
    return settings


def run(context: Any) -> int:
    _validate_name_surface_or_die()

    settings = _resolve_settings_from_context(context)
    cfg = ReportConfig.from_runtime(settings=settings, context=context)
    redis_client = _resolve_redis_client_from_context(context)
    clock = getattr(context, "clock", None)
    shutdown = getattr(context, "shutdown", None)
    instance_id = _safe_str(getattr(context, "instance_id", ""))

    if clock is None:
        raise ReportConfigError("run(context) requires context.clock")
    if shutdown is None:
        raise ReportConfigError("run(context) requires context.shutdown")
    if not instance_id:
        raise ReportConfigError("run(context) requires context.instance_id")

    service = ReportService(
        cfg=cfg,
        redis_client=redis_client,
        clock=clock,
        shutdown=shutdown,
        instance_id=instance_id,
    )
    return service.start(context=context)

# =============================================================================
# Batch 15 freeze hardening: deterministic trade linking and PnL semantics
# =============================================================================

_BATCH15_REPORT_OPS_FREEZE_VERSION = "1"


def _batch15_trade_stable_key(trade: TradeRecord) -> str:
    for value in (
        trade.position_id,
        trade.decision_id,
        trade.trade_key,
    ):
        text = _safe_str(value)
        if text:
            return text
    return trade.trade_key


def _batch15_merge_trade_records(trades: Sequence[TradeRecord]) -> list[TradeRecord]:
    merged: dict[str, TradeRecord] = {}

    for trade in trades:
        key = _batch15_trade_stable_key(trade)
        if key not in merged:
            merged[key] = trade
            continue

        base = merged[key]
        base.entry_ts = base.entry_ts or trade.entry_ts
        base.exit_ts = base.exit_ts or trade.exit_ts
        base.signal_ts = base.signal_ts or trade.signal_ts
        base.confirm_ts = base.confirm_ts or trade.confirm_ts

        for attr in (
            "decision_id",
            "position_id",
            "entry_order_id",
            "exit_order_id",
            "symbol",
            "instrument",
            "side",
            "expiry",
            "entry_mode",
            "exit_reason",
            "entry_ack_status",
            "exit_ack_status",
        ):
            if not getattr(base, attr):
                setattr(base, attr, getattr(trade, attr))

        if base.strike is None:
            base.strike = trade.strike
        base.entry_price = base.entry_price or trade.entry_price
        base.exit_price = base.exit_price or trade.exit_price
        base.entry_qty = base.entry_qty or trade.entry_qty
        base.exit_qty = base.exit_qty or trade.exit_qty
        base.filled_qty = base.filled_qty or trade.filled_qty
        base.realized_pnl = base.realized_pnl or trade.realized_pnl
        base.gross_pnl = base.gross_pnl or trade.gross_pnl
        base.net_pnl = base.net_pnl or trade.net_pnl
        base.fees += trade.fees

        base.partial_fill = base.partial_fill or trade.partial_fill
        base.degraded = base.degraded or trade.degraded
        base.broker_mismatch = base.broker_mismatch or trade.broker_mismatch
        base.raw_events.extend(trade.raw_events)

    return list(merged.values())


def _batch15_payload_values(trade: TradeRecord, key: str) -> list[float]:
    out: list[float] = []
    for event in trade.raw_events:
        if not isinstance(event, Mapping):
            continue
        if key in event and event.get(key) not in (None, ""):
            out.append(_safe_float(event.get(key), 0.0))
    return out


def _batch15_finalize_trade_pnl(trade: TradeRecord) -> None:
    net_values = _batch15_payload_values(trade, "net_pnl")
    gross_values = _batch15_payload_values(trade, "gross_pnl")
    realized_values = _batch15_payload_values(trade, "realized_pnl")
    pnl_values = _batch15_payload_values(trade, "pnl")

    if net_values:
        trade.net_pnl = net_values[-1]
        trade.gross_pnl = gross_values[-1] if gross_values else trade.net_pnl + trade.fees
        trade.realized_pnl = trade.net_pnl
    elif gross_values:
        trade.gross_pnl = gross_values[-1]
        trade.net_pnl = trade.gross_pnl - trade.fees
        trade.realized_pnl = trade.gross_pnl
    elif realized_values:
        trade.gross_pnl = realized_values[-1]
        trade.net_pnl = trade.gross_pnl - trade.fees
        trade.realized_pnl = trade.gross_pnl
    elif pnl_values:
        trade.gross_pnl = pnl_values[-1]
        trade.net_pnl = trade.gross_pnl - trade.fees
        trade.realized_pnl = trade.gross_pnl
    else:
        trade.gross_pnl = trade.realized_pnl
        trade.net_pnl = trade.gross_pnl - trade.fees

    if trade.entry_ts and trade.exit_ts:
        trade.hold_seconds = max((trade.exit_ts - trade.entry_ts).total_seconds(), 0.0)
    if trade.filled_qty == 0:
        trade.filled_qty = trade.entry_qty or trade.exit_qty
    if not trade.entry_mode:
        trade.entry_mode = N.ENTRY_MODE_UNKNOWN


_BATCH15_ORIGINAL_RECONSTRUCT_TRADES = ReviewEngine._reconstruct_trades


def _batch15_reconstruct_trades(
    self: ReviewEngine,
    *,
    ledger: Sequence[StreamRecord],
    acks: Sequence[StreamRecord],
    orders: Sequence[StreamRecord],
) -> list[TradeRecord]:
    trades = list(
        _BATCH15_ORIGINAL_RECONSTRUCT_TRADES(
            self,
            ledger=ledger,
            acks=acks,
            orders=orders,
        )
    )
    merged = _batch15_merge_trade_records(trades)
    for trade in merged:
        _batch15_finalize_trade_pnl(trade)

    return sorted(
        merged,
        key=lambda item: (
            item.entry_ts or item.exit_ts or datetime.min.replace(tzinfo=timezone.utc),
            item.trade_key,
        ),
    )


ReviewEngine._reconstruct_trades = _batch15_reconstruct_trades


_BATCH15_ORIGINAL_BUILD_SESSION_PACK = ReviewEngine.build_session_pack


def _batch15_build_session_pack(self: ReviewEngine, *, session_day: date) -> dict[str, Any]:
    pack = dict(_BATCH15_ORIGINAL_BUILD_SESSION_PACK(self, session_day=session_day))
    diagnostics = dict(pack.get("diagnostics", {}) or {})
    source_counts = dict(diagnostics.get("source_counts", {}) or {})

    truncation = {
        "ledger_may_be_truncated": int(source_counts.get("ledger", 0)) >= int(self.cfg.history_limit),
        "acks_may_be_truncated": int(source_counts.get("acks", 0)) >= int(self.cfg.ack_limit),
        "orders_may_be_truncated": int(source_counts.get("orders", 0)) >= int(self.cfg.order_limit),
        "health_may_be_truncated": int(source_counts.get("health", 0)) >= int(self.cfg.health_limit),
        "errors_may_be_truncated": int(source_counts.get("errors", 0)) >= int(self.cfg.error_limit),
    }
    diagnostics["truncation"] = truncation
    pack["diagnostics"] = diagnostics

    session_report = dict(pack.get("session_report", {}) or {})
    report_diag = dict(session_report.get("diagnostics", {}) or {})
    report_diag["truncation"] = truncation
    session_report["diagnostics"] = report_diag
    pack["session_report"] = session_report

    return pack


ReviewEngine.build_session_pack = _batch15_build_session_pack
