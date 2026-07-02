from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class LtpSnapshot:
    symbol: str
    instrument_token: str
    ltp: float
    source_stream: str
    source_id: str
    source_age_ms: int
    raw_keys: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ShadowOpenPosition:
    event_id: str
    source_decision_id: str
    action: str
    symbol: str
    instrument_token: str
    family_id: str
    score: float
    qty_lots: int
    lot_size: int
    entry_price: float
    entry_created_at_ms: int
    entry_ltp_source: dict[str, Any]
    highest_seen: float
    lowest_seen: float
    last_ltp: float
    last_ltp_at_ms: int
    status: str = "OPEN"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ShadowExit:
    event_id: str
    source_decision_id: str
    action: str
    symbol: str
    instrument_token: str
    family_id: str
    score: float
    qty_lots: int
    lot_size: int
    entry_price: float
    exit_price: float
    entry_created_at_ms: int
    exit_created_at_ms: int
    holding_time_ms: int
    exit_reason: str
    highest_seen: float
    lowest_seen: float
    pnl_points_net: float
    pnl_rupees_net_proxy: float
    mfe_points: float
    mae_points: float
    mfe_rupees_proxy: float
    mae_rupees_proxy: float
    slippage_points_total: float
    exit_ltp_source: dict[str, Any]
    broker_order_sent: bool = False
    paper_engine_used: bool = False
    risk_execution_used: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
