from __future__ import annotations

"""
app/mme_scalpx/integrations/dhan_runtime_clients.py

Freeze-grade concrete Dhan runtime clients promoted from proven operator scripts.

Purpose
-------
This module provides concrete app-level clients for:
- Dhan option-chain/context fetch
- Dhan 20-level live depth websocket
- Dhan runtime instrument -> security-id resolution for NIFTY futures/options

Why this file exists
--------------------
- main.py / feeds.py are already provider-aware and can accept Dhan surfaces
- dhan_marketdata.py only defines Protocols / manager shell
- proven Dhan REST / websocket logic already exists in bin/ scripts
- this module promotes that reusable logic into app/ so bootstrap_provider.py can wire it safely

Non-responsibilities
--------------------
- no Redis writes
- no runtime supervision
- no strategy logic
- no main.py composition
"""

from dataclasses import dataclass
from datetime import date, datetime
from io import StringIO
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import quote
import csv
import json
import os
import struct
import time

import requests

try:
    import websocket  # type: ignore
except Exception:  # pragma: no cover
    websocket = None  # type: ignore


INSTRUMENT_CSV_URL = "https://images.dhan.co/api-data/api-scrip-master-detailed.csv"
API_BASE = "https://api.dhan.co/v2"
DEFAULT_TIMEOUT = 20
DEFAULT_UNDERLYING_SCRIP_NIFTY = 13
DEFAULT_SEGMENT = "NSE_FNO"


class DhanRuntimeClientError(RuntimeError):
    """Base error for Dhan runtime clients."""


class DhanRuntimeValidationError(DhanRuntimeClientError):
    """Raised when inputs are invalid."""


class DhanRuntimeUnavailableError(DhanRuntimeClientError):
    """Raised when live transport or context is unavailable."""


def _norm(value: Any) -> str:
    return str(value or "").strip()


def _upper(value: Any) -> str:
    return _norm(value).upper()


def _as_int(value: Any) -> int | None:
    if value in (None, "", "NA", "null"):
        return None
    try:
        return int(float(value))
    except Exception:
        return None


def _as_float(value: Any) -> float | None:
    if value in (None, "", "NA", "null"):
        return None
    try:
        return float(value)
    except Exception:
        return None


def _pick(mapping: Mapping[str, Any], *keys: str) -> str:
    for key in keys:
        if key in mapping and mapping[key] not in (None, ""):
            return str(mapping[key]).strip()
    return ""


def _parse_date(value: str) -> date | None:
    value = _norm(value)
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%d-%b-%Y", "%d-%B-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    return None


def _security_id(row: Mapping[str, Any]) -> int | None:
    return _as_int(
        _pick(
            row,
            "SECURITY_ID",
            "SM_SECURITY_ID",
            "SEM_SMST_SECURITY_ID",
            "SEM_SECURITY_ID",
            "SCRIP_ID",
            "ID",
        )
    )


@dataclass(frozen=True, slots=True)
class ResolvedDhanRuntimeIds:
    current_future_security_id: int
    ce_atm_security_id: int
    ce_atm1_security_id: int
    pe_atm_security_id: int
    pe_atm1_security_id: int
    selected_expiry: str
    underlying_scrip: int = DEFAULT_UNDERLYING_SCRIP_NIFTY

    def as_feed_order(self) -> list[str]:
        return [
            str(self.current_future_security_id),
            str(self.ce_atm_security_id),
            str(self.ce_atm1_security_id),
            str(self.pe_atm_security_id),
            str(self.pe_atm1_security_id),
        ]


class DhanNiftyRuntimeResolver:
    """
    Resolve the current RuntimeInstrumentSet contracts to Dhan SecurityIds.

    Current scope:
    - NIFTY futures + ATM/ATM1 CE/PE
    - NSE_FNO only
    """

    def __init__(
        self,
        *,
        session: requests.Session | None = None,
        client_id: str | None = None,
        access_token: str | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self._session = session or requests.Session()
        self._client_id = _norm(client_id or os.getenv("DHAN_CLIENT_ID") or os.getenv("MME_DHAN_CLIENT_ID"))
        self._access_token = _norm(access_token or os.getenv("DHAN_ACCESS_TOKEN") or os.getenv("MME_DHAN_ACCESS_TOKEN"))
        self._timeout = int(timeout)

    @property
    def client_id(self) -> str:
        if not self._client_id:
            raise DhanRuntimeValidationError("missing DHAN_CLIENT_ID / MME_DHAN_CLIENT_ID")
        return self._client_id

    @property
    def access_token(self) -> str:
        if not self._access_token:
            raise DhanRuntimeValidationError("missing DHAN_ACCESS_TOKEN / MME_DHAN_ACCESS_TOKEN")
        return self._access_token

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "client-id": self.client_id,
            "access-token": self.access_token,
        }
        resp = self._session.post(
            f"{API_BASE}{path}",
            headers=headers,
            json=payload,
            timeout=self._timeout,
        )
        try:
            body = resp.json()
        except Exception as exc:
            raise DhanRuntimeUnavailableError(
                f"{path} returned non-JSON: HTTP {resp.status_code}, body={resp.text[:500]!r}"
            ) from exc
        if resp.status_code >= 400:
            raise DhanRuntimeUnavailableError(
                f"{path} failed: HTTP {resp.status_code}, response={json.dumps(body, ensure_ascii=False)}"
            )
        return body

    def fetch_instrument_rows(self) -> list[dict[str, str]]:
        resp = self._session.get(INSTRUMENT_CSV_URL, timeout=self._timeout)
        resp.raise_for_status()
        return list(csv.DictReader(StringIO(resp.text.lstrip("\ufeff"))))

    def resolve_nearest_future(self, rows: Iterable[dict[str, str]], *, symbol: str = "NIFTY") -> dict[str, str]:
        today = date.today()
        futures: list[tuple[date, dict[str, str]]] = []
        banned = {"BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX", "BANKEX"}

        symbol_u = _upper(symbol)

        for row in rows:
            exch = _upper(_pick(row, "EXCH_ID", "SEM_EXM_EXCH_ID"))
            instr = _upper(_pick(row, "INSTRUMENT", "SEM_INSTRUMENT_NAME"))
            if exch != "NSE" or instr != "FUTIDX":
                continue

            under = _upper(_pick(row, "UNDERLYING_SYMBOL"))
            sym = _upper(_pick(row, "SYMBOL_NAME", "SM_SYMBOL_NAME"))
            disp = _upper(_pick(row, "DISPLAY_NAME", "SEM_CUSTOM_SYMBOL"))
            joined = " ".join([under, sym, disp])

            if symbol_u == "NIFTY":
                if any(b in joined for b in banned):
                    continue
                exact_ok = under == "NIFTY" or sym == "NIFTY" or disp == "NIFTY" or disp.startswith("NIFTY ")
                if not exact_ok:
                    continue
            else:
                if under != symbol_u and sym != symbol_u and not disp.startswith(symbol_u + " "):
                    continue

            sid = _security_id(row)
            if sid is None:
                continue

            expiry = _parse_date(_pick(row, "SM_EXPIRY_DATE", "SEM_EXPIRY_DATE"))
            if expiry is None:
                continue

            futures.append((expiry, row))

        if not futures:
            raise DhanRuntimeUnavailableError(f"No exact FUTIDX rows found for {symbol_u}")

        future_or_today = sorted(
            ((exp, row) for exp, row in futures if exp >= today),
            key=lambda item: item[0],
        )
        if future_or_today:
            return future_or_today[0][1]
        return sorted(futures, key=lambda item: item[0])[0][1]

    def get_option_chain(self, *, expiry: str, underlying_scrip: int = DEFAULT_UNDERLYING_SCRIP_NIFTY) -> dict[str, Any]:
        return self._post_json(
            "/optionchain",
            {
                "UnderlyingScrip": int(underlying_scrip),
                "UnderlyingSeg": "IDX_I",
                "Expiry": expiry,
            },
        )

    def resolve_option_security_id(
        self,
        *,
        option_chain: Mapping[str, Any],
        strike: float,
        option_type: str,
    ) -> int:
        data = option_chain.get("data") or {}
        oc = data.get("oc") or {}
        if not isinstance(oc, Mapping) or not oc:
            raise DhanRuntimeUnavailableError("optionchain returned no strike data")

        desired_type = _upper(option_type)
        desired_key = "ce" if desired_type == "CE" else "pe"

        for strike_raw, block in oc.items():
            strike_value = _as_float(strike_raw)
            if strike_value is None:
                continue
            if abs(float(strike_value) - float(strike)) > 0.001:
                continue
            if not isinstance(block, Mapping):
                continue
            side = block.get(desired_key)
            if not isinstance(side, Mapping):
                continue
            sid = _as_int(side.get("security_id"))
            if sid is not None:
                return sid

        raise DhanRuntimeUnavailableError(
            f"Could not resolve {desired_type} security id from optionchain for strike={strike}"
        )

    def resolve_from_runtime_instruments(self, runtime_instruments: Any) -> ResolvedDhanRuntimeIds:
        current_future = getattr(runtime_instruments, "current_future", None)
        ce_atm = getattr(runtime_instruments, "ce_atm", None)
        ce_atm1 = getattr(runtime_instruments, "ce_atm1", None)
        pe_atm = getattr(runtime_instruments, "pe_atm", None)
        pe_atm1 = getattr(runtime_instruments, "pe_atm1", None)

        if any(item is None for item in (current_future, ce_atm, ce_atm1, pe_atm, pe_atm1)):
            raise DhanRuntimeValidationError("runtime_instruments missing one or more required NIFTY contracts")

        rows = self.fetch_instrument_rows()
        future_row = self.resolve_nearest_future(rows, symbol="NIFTY")
        fut_sid = _security_id(future_row)
        if fut_sid is None:
            raise DhanRuntimeUnavailableError("nearest future row missing security id")

        expiry_obj = getattr(ce_atm, "expiry", None)
        if isinstance(expiry_obj, date):
            expiry_text = expiry_obj.isoformat()
        else:
            expiry_text = _norm(expiry_obj)
        if not expiry_text:
            raise DhanRuntimeValidationError("ce_atm expiry missing")

        option_chain = self.get_option_chain(expiry=expiry_text)

        return ResolvedDhanRuntimeIds(
            current_future_security_id=int(fut_sid),
            ce_atm_security_id=self.resolve_option_security_id(
                option_chain=option_chain,
                strike=float(getattr(ce_atm, "strike")),
                option_type="CE",
            ),
            ce_atm1_security_id=self.resolve_option_security_id(
                option_chain=option_chain,
                strike=float(getattr(ce_atm1, "strike")),
                option_type="CE",
            ),
            pe_atm_security_id=self.resolve_option_security_id(
                option_chain=option_chain,
                strike=float(getattr(pe_atm, "strike")),
                option_type="PE",
            ),
            pe_atm1_security_id=self.resolve_option_security_id(
                option_chain=option_chain,
                strike=float(getattr(pe_atm1, "strike")),
                option_type="PE",
            ),
            selected_expiry=expiry_text,
        )


class DhanOptionChainContextClient:
    """
    Concrete DhanContextClient backed by /optionchain REST.
    """

    def __init__(
        self,
        *,
        client_id: str | None = None,
        access_token: str | None = None,
        underlying_scrip: int = DEFAULT_UNDERLYING_SCRIP_NIFTY,
        expiry: str,
        timeout: int = DEFAULT_TIMEOUT,
        session: requests.Session | None = None,
    ) -> None:
        self._client_id = _norm(client_id or os.getenv("DHAN_CLIENT_ID") or os.getenv("MME_DHAN_CLIENT_ID"))
        self._access_token = _norm(access_token or os.getenv("DHAN_ACCESS_TOKEN") or os.getenv("MME_DHAN_ACCESS_TOKEN"))
        self._underlying_scrip = int(underlying_scrip)
        self._expiry = _norm(expiry)
        self._timeout = int(timeout)
        self._session = session or requests.Session()

        if not self._client_id:
            raise DhanRuntimeValidationError("missing DHAN_CLIENT_ID / MME_DHAN_CLIENT_ID")
        if not self._access_token:
            raise DhanRuntimeValidationError("missing DHAN_ACCESS_TOKEN / MME_DHAN_ACCESS_TOKEN")
        if not self._expiry:
            raise DhanRuntimeValidationError("expiry may not be blank")

    def fetch_chain_snapshot(self, *, access_token: str | None = None) -> Any:
        token = _norm(access_token or self._access_token)
        if not token:
            raise DhanRuntimeValidationError("access token missing for fetch_chain_snapshot")

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "client-id": self._client_id,
            "access-token": token,
        }
        payload = {
            "UnderlyingScrip": self._underlying_scrip,
            "UnderlyingSeg": "IDX_I",
            "Expiry": self._expiry,
        }
        resp = self._session.post(
            f"{API_BASE}/optionchain",
            headers=headers,
            json=payload,
            timeout=self._timeout,
        )
        try:
            body = resp.json()
        except Exception as exc:
            raise DhanRuntimeUnavailableError(
                f"/optionchain returned non-JSON: HTTP {resp.status_code}, body={resp.text[:500]!r}"
            ) from exc
        if resp.status_code >= 400:
            raise DhanRuntimeUnavailableError(
                f"/optionchain failed: HTTP {resp.status_code}, response={json.dumps(body, ensure_ascii=False)}"
            )
        return body


class DhanTwentyDepthLiveFeedClient:
    """
    Concrete DhanLiveFeedClient backed by the 20-depth websocket.

    Protocol methods:
    - subscribe(instrument_keys)
    - unsubscribe(instrument_keys)

    Extra runtime helpers:
    - recv(timeout_sec=...)
    - close()
    - parse_packets(blob)
    """

    def __init__(
        self,
        *,
        client_id: str | None = None,
        access_token: str | None = None,
        segment: str = DEFAULT_SEGMENT,
        timeout_sec: int = DEFAULT_TIMEOUT,
    ) -> None:
        self._client_id = _norm(client_id or os.getenv("DHAN_CLIENT_ID") or os.getenv("MME_DHAN_CLIENT_ID"))
        self._access_token = _norm(access_token or os.getenv("DHAN_ACCESS_TOKEN") or os.getenv("MME_DHAN_ACCESS_TOKEN"))
        self._segment = _norm(segment) or DEFAULT_SEGMENT
        self._timeout_sec = int(timeout_sec)
        self._subscriptions: list[str] = []
        self._ws = None

        if not self._client_id:
            raise DhanRuntimeValidationError("missing DHAN_CLIENT_ID / MME_DHAN_CLIENT_ID")
        if not self._access_token:
            raise DhanRuntimeValidationError("missing DHAN_ACCESS_TOKEN / MME_DHAN_ACCESS_TOKEN")
        if websocket is None:
            raise DhanRuntimeUnavailableError(
                "python package 'websocket-client' is required; install with .venv/bin/pip install websocket-client"
            )

    def _url(self) -> str:
        return (
            "wss://depth-api-feed.dhan.co/twentydepth"
            f"?token={quote(self._access_token)}&clientId={quote(self._client_id)}&authType=2"
        )

    def _ensure_connection(self) -> Any:
        if self._ws is not None:
            return self._ws
        self._ws = websocket.create_connection(self._url(), timeout=self._timeout_sec)
        self._ws.settimeout(self._timeout_sec)
        return self._ws

    def _send_subscribe(self) -> dict[str, Any]:
        ws = self._ensure_connection()
        payload = {
            "RequestCode": 23,
            "InstrumentCount": len(self._subscriptions),
            "InstrumentList": [
                {"ExchangeSegment": self._segment, "SecurityId": sid}
                for sid in self._subscriptions
            ],
        }
        ws.send(json.dumps(payload))
        return payload

    def subscribe(self, instrument_keys: Sequence[str]) -> Any:
        cleaned = [_norm(item) for item in instrument_keys if _norm(item)]
        if not cleaned:
            raise DhanRuntimeValidationError("instrument_keys may not be empty")
        merged = list(dict.fromkeys(self._subscriptions + cleaned))
        self._subscriptions = merged
        return self._send_subscribe()

    def unsubscribe(self, instrument_keys: Sequence[str]) -> Any:
        removed = {_norm(item) for item in instrument_keys if _norm(item)}
        self._subscriptions = [sid for sid in self._subscriptions if sid not in removed]
        self.close()
        if not self._subscriptions:
            return {"unsubscribed": sorted(removed), "remaining": []}
        return self._send_subscribe()

    def recv(self, *, timeout_sec: int | None = None) -> bytes | None:
        ws = self._ensure_connection()
        if timeout_sec is not None:
            ws.settimeout(int(timeout_sec))
        try:
            msg = ws.recv()
        except Exception:
            return None
        if isinstance(msg, str):
            return msg.encode("utf-8")
        return msg

    def close(self) -> None:
        if self._ws is None:
            return
        try:
            self._ws.close()
        except Exception:
            pass
        finally:
            self._ws = None

    @staticmethod
    def parse_packets(blob: bytes) -> list[dict[str, Any]]:
        packets: list[dict[str, Any]] = []
        off = 0
        total = len(blob)

        while off + 12 <= total:
            msg_len = int.from_bytes(blob[off:off + 2], "little", signed=False)

            if msg_len < 12 or off + msg_len > total:
                if off + 332 <= total:
                    msg_len = 332
                else:
                    break

            pkt = blob[off:off + msg_len]
            off += msg_len

            response_code = pkt[2]
            security_id = str(int.from_bytes(pkt[4:8], "little", signed=False))

            if response_code not in (41, 51):
                continue

            side = "bid" if response_code == 41 else "ask"
            levels: list[dict[str, Any]] = []
            pos = 12
            for _ in range(20):
                if pos + 16 > len(pkt):
                    break
                price = struct.unpack_from("<d", pkt, pos)[0]
                qty = struct.unpack_from("<I", pkt, pos + 8)[0]
                orders = struct.unpack_from("<I", pkt, pos + 12)[0]
                levels.append(
                    {
                        "price": round(price, 10),
                        "qty": int(qty),
                        "orders": int(orders),
                    }
                )
                pos += 16

            packets.append(
                {
                    "security_id": security_id,
                    "side": side,
                    "levels": levels,
                }
            )
        return packets



@dataclass(frozen=True, slots=True)
class _MappedDhanSubscription:
    security_id: str
    approved_instrument_token: str
    approved_trading_symbol: str
    approved_instrument_key: str
    role: str


class DhanFullFeedPollingAdapter:
    """
    Concrete feeds.py-compatible Dhan market-data adapter.

    Important design choice:
    - use Dhan FULL feed (RequestCode 21) as the first canonical runtime lane
    - this gives ltp + quote + depth5, which feeds.py can normalize immediately
    - TOP20 remains an enhancement lane and can be layered later
    """

    def __init__(
        self,
        *,
        runtime_instruments: Any,
        resolved_ids: ResolvedDhanRuntimeIds,
        segment: str = DEFAULT_SEGMENT,
        timeout_sec: int = 5,
    ) -> None:
        self._client_id = _norm(os.getenv("DHAN_CLIENT_ID") or os.getenv("MME_DHAN_CLIENT_ID"))
        self._access_token = _norm(os.getenv("DHAN_ACCESS_TOKEN") or os.getenv("MME_DHAN_ACCESS_TOKEN"))
        self._segment = _norm(segment) or DEFAULT_SEGMENT
        self._timeout_sec = int(timeout_sec)
        self._ws = None
        self._subscribed = False

        if not self._client_id:
            raise DhanRuntimeValidationError("missing DHAN_CLIENT_ID / MME_DHAN_CLIENT_ID")
        if not self._access_token:
            raise DhanRuntimeValidationError("missing DHAN_ACCESS_TOKEN / MME_DHAN_ACCESS_TOKEN")
        if websocket is None:
            raise DhanRuntimeUnavailableError(
                "python package 'websocket-client' is required; install with .venv/bin/pip install websocket-client"
            )

        current_future = getattr(runtime_instruments, "current_future", None)
        ce_atm = getattr(runtime_instruments, "ce_atm", None)
        ce_atm1 = getattr(runtime_instruments, "ce_atm1", None)
        pe_atm = getattr(runtime_instruments, "pe_atm", None)
        pe_atm1 = getattr(runtime_instruments, "pe_atm1", None)

        if any(item is None for item in (current_future, ce_atm, ce_atm1, pe_atm, pe_atm1)):
            raise DhanRuntimeValidationError("runtime_instruments missing required NIFTY contracts")

        self._subscriptions: dict[str, _MappedDhanSubscription] = {
            str(resolved_ids.current_future_security_id): self._map_contract(
                contract=current_future,
                security_id=resolved_ids.current_future_security_id,
                role="FUTURES",
            ),
            str(resolved_ids.ce_atm_security_id): self._map_contract(
                contract=ce_atm,
                security_id=resolved_ids.ce_atm_security_id,
                role="CE_ATM",
            ),
            str(resolved_ids.ce_atm1_security_id): self._map_contract(
                contract=ce_atm1,
                security_id=resolved_ids.ce_atm1_security_id,
                role="CE_ATM1",
            ),
            str(resolved_ids.pe_atm_security_id): self._map_contract(
                contract=pe_atm,
                security_id=resolved_ids.pe_atm_security_id,
                role="PE_ATM",
            ),
            str(resolved_ids.pe_atm1_security_id): self._map_contract(
                contract=pe_atm1,
                security_id=resolved_ids.pe_atm1_security_id,
                role="PE_ATM1",
            ),
        }

        self._state: dict[str, dict[str, Any]] = {sid: {} for sid in self._subscriptions}

    @staticmethod
    def _map_contract(*, contract: Any, security_id: int, role: str) -> _MappedDhanSubscription:
        trading_symbol = _norm(getattr(contract, "tradingsymbol", None))
        instrument_token = _norm(getattr(contract, "instrument_token", None))
        instrument_key = _norm(getattr(contract, "instrument_key", None)) or f"NFO:{trading_symbol}"
        if not trading_symbol or not instrument_token:
            raise DhanRuntimeValidationError(f"invalid runtime contract for role={role}")
        return _MappedDhanSubscription(
            security_id=str(int(security_id)),
            approved_instrument_token=instrument_token,
            approved_trading_symbol=trading_symbol,
            approved_instrument_key=instrument_key,
            role=role,
        )

    def info(self) -> dict[str, Any]:
        return {
            "adapter_name": self.__class__.__name__,
            "provider_id": "DHAN",
            "segment": self._segment,
            "subscription_count": len(self._subscriptions),
            "connected": self._ws is not None,
            "mode": "FULL_TOP5_BASE",
        }

    def health(self) -> dict[str, Any]:
        return self.info()

    def _url(self) -> str:
        return (
            "wss://api-feed.dhan.co"
            f"?version=2&token={quote(self._access_token)}&clientId={quote(self._client_id)}&authType=2"
        )

    def _ensure_connection(self) -> Any:
        if self._ws is not None:
            return self._ws
        self._ws = websocket.create_connection(self._url(), timeout=self._timeout_sec)
        self._ws.settimeout(0.2)
        self._subscribed = False
        return self._ws

    def _subscribe_if_needed(self) -> None:
        ws = self._ensure_connection()
        if self._subscribed:
            return
        payload = {
            "RequestCode": 21,
            "InstrumentCount": len(self._subscriptions),
            "InstrumentList": [
                {"ExchangeSegment": self._segment, "SecurityId": sid}
                for sid in self._subscriptions.keys()
            ],
        }
        ws.send(json.dumps(payload))
        self._subscribed = True

    @staticmethod
    def _u16(buf: bytes, off: int) -> int:
        return struct.unpack_from("<H", buf, off)[0]

    @staticmethod
    def _i16(buf: bytes, off: int) -> int:
        return struct.unpack_from("<h", buf, off)[0]

    @staticmethod
    def _i32(buf: bytes, off: int) -> int:
        return struct.unpack_from("<i", buf, off)[0]

    @staticmethod
    def _f32(buf: bytes, off: int) -> float:
        return struct.unpack_from("<f", buf, off)[0]

    @classmethod
    def _header(cls, pkt: bytes) -> tuple[int, int, int, str]:
        code = pkt[0]
        msg_len = cls._u16(pkt, 1)
        seg = pkt[3]
        security_id = str(int.from_bytes(pkt[4:8], "little", signed=False))
        return code, msg_len, seg, security_id

    @classmethod
    def _split_packets(cls, blob: bytes) -> list[bytes]:
        packets: list[bytes] = []
        off = 0
        total = len(blob)
        while off + 8 <= total:
            msg_len = cls._u16(blob, off + 1)
            if msg_len < 8 or off + msg_len > total:
                break
            packets.append(blob[off:off + msg_len])
            off += msg_len
        return packets

    @classmethod
    def _parse_quote(cls, pkt: bytes) -> dict[str, Any]:
        code, msg_len, seg, security_id = cls._header(pkt)
        return {
            "response_code": code,
            "response_type": "quote",
            "security_id": security_id,
            "ltp": cls._f32(pkt, 8),
            "ltq": cls._i16(pkt, 12),
            "ltt_epoch": cls._i32(pkt, 14),
            "atp": cls._f32(pkt, 18),
            "volume": cls._i32(pkt, 22),
            "total_sell_qty": cls._i32(pkt, 26),
            "total_buy_qty": cls._i32(pkt, 30),
            "day_open": cls._f32(pkt, 34),
            "day_close": cls._f32(pkt, 38),
            "day_high": cls._f32(pkt, 42),
            "day_low": cls._f32(pkt, 46),
        }

    @classmethod
    def _parse_oi(cls, pkt: bytes) -> dict[str, Any]:
        code, msg_len, seg, security_id = cls._header(pkt)
        return {
            "response_code": code,
            "response_type": "oi",
            "security_id": security_id,
            "oi": cls._i32(pkt, 8),
        }

    @classmethod
    def _parse_prev_close(cls, pkt: bytes) -> dict[str, Any]:
        code, msg_len, seg, security_id = cls._header(pkt)
        return {
            "response_code": code,
            "response_type": "prev_close",
            "security_id": security_id,
            "prev_close": cls._f32(pkt, 8),
            "prev_oi": cls._i32(pkt, 12),
        }

    @classmethod
    def _parse_full(cls, pkt: bytes) -> dict[str, Any]:
        code, msg_len, seg, security_id = cls._header(pkt)
        out = {
            "response_code": code,
            "response_type": "full",
            "security_id": security_id,
            "ltp": cls._f32(pkt, 8),
            "ltq": cls._i16(pkt, 12),
            "ltt_epoch": cls._i32(pkt, 14),
            "atp": cls._f32(pkt, 18),
            "volume": cls._i32(pkt, 22),
            "total_sell_qty": cls._i32(pkt, 26),
            "total_buy_qty": cls._i32(pkt, 30),
            "oi": cls._i32(pkt, 34),
            "day_high_oi": cls._i32(pkt, 38),
            "day_low_oi": cls._i32(pkt, 42),
            "day_open": cls._f32(pkt, 46),
            "day_close": cls._f32(pkt, 50),
            "day_high": cls._f32(pkt, 54),
            "day_low": cls._f32(pkt, 58),
            "depth5": [],
        }
        pos = 62
        for _ in range(5):
            if pos + 20 > len(pkt):
                break
            out["depth5"].append(
                {
                    "bid_qty": cls._i32(pkt, pos),
                    "ask_qty": cls._i32(pkt, pos + 4),
                    "bid_orders": cls._i16(pkt, pos + 8),
                    "ask_orders": cls._i16(pkt, pos + 10),
                    "bid_price": cls._f32(pkt, pos + 12),
                    "ask_price": cls._f32(pkt, pos + 16),
                }
            )
            pos += 20
        return out

    @classmethod
    def _parse_packet(cls, pkt: bytes) -> dict[str, Any] | None:
        if len(pkt) < 8:
            return None
        code = pkt[0]
        if code == 4:
            return cls._parse_quote(pkt)
        if code == 5:
            return cls._parse_oi(pkt)
        if code == 6:
            return cls._parse_prev_close(pkt)
        if code == 8:
            return cls._parse_full(pkt)
        return None

    def _payload_from_event(self, event: dict[str, Any]) -> dict[str, Any] | None:
        sid = _norm(event.get("security_id"))
        sub = self._subscriptions.get(sid)
        if sub is None:
            return None

        state = self._state.setdefault(sid, {})
        state.update(event)

        ltt_epoch = _as_int(state.get("ltt_epoch"))
        provider_ts_ns = int(ltt_epoch) * 1_000_000_000 if ltt_epoch is not None and ltt_epoch > 0 else time.time_ns()

        best_bid = None
        best_ask = None
        bid_qty = None
        ask_qty = None
        bids: list[dict[str, Any]] = []
        asks: list[dict[str, Any]] = []

        depth5 = state.get("depth5")
        if isinstance(depth5, list):
            for row in depth5:
                if not isinstance(row, Mapping):
                    continue
                bid_row = {
                    "price": _as_float(row.get("bid_price")),
                    "quantity": _as_int(row.get("bid_qty")),
                    "orders": _as_int(row.get("bid_orders")),
                }
                ask_row = {
                    "price": _as_float(row.get("ask_price")),
                    "quantity": _as_int(row.get("ask_qty")),
                    "orders": _as_int(row.get("ask_orders")),
                }
                if bid_row["price"] is not None and bid_row["quantity"] is not None:
                    bids.append(bid_row)
                if ask_row["price"] is not None and ask_row["quantity"] is not None:
                    asks.append(ask_row)

        if bids:
            best_bid = bids[0]["price"]
            bid_qty = bids[0]["quantity"]
        if asks:
            best_ask = asks[0]["price"]
            ask_qty = asks[0]["quantity"]

        payload = {
            "instrument_token": sub.approved_instrument_token,
            "instrument_key": sub.approved_instrument_key,
            "tradingsymbol": sub.approved_trading_symbol,
            "provider_security_id": sid,
            "provider_ts_ns": provider_ts_ns,
            "ltp": _as_float(state.get("ltp")),
            "last_qty": _as_int(state.get("ltq")),
            "volume": _as_int(state.get("volume")),
            "oi": _as_int(state.get("oi")),
            "best_bid": best_bid,
            "best_ask": best_ask,
            "bid_qty": bid_qty,
            "ask_qty": ask_qty,
            "bids": bids,
            "asks": asks,
        }
        return payload

    def poll(self) -> Iterable[Mapping[str, Any]]:
        self._subscribe_if_needed()
        ws = self._ensure_connection()
        try:
            msg = ws.recv()
        except Exception:
            return []

        if isinstance(msg, str):
            return []

        out: list[dict[str, Any]] = []
        for pkt in self._split_packets(msg):
            event = self._parse_packet(pkt)
            if event is None:
                continue
            payload = self._payload_from_event(event)
            if payload is not None:
                out.append(payload)
        return out



class DhanContextPollingAdapter:
    """
    feeds.py-compatible polling adapter for Dhan option-chain context.

    Stabilization contract
    ----------------------
    - Dhan option-chain context is an enhancement/context lane.
    - It must not be hammered every feed loop.
    - Last-good context may be reused during minimum-poll interval/backoff.
    - Runtime must degrade gracefully when /optionchain is throttled/unavailable.
    - This adapter performs no Redis writes, no provider failover, and no
      strategy decisions.
    """

    def __init__(
        self,
        *,
        client: DhanOptionChainContextClient,
        runtime_instruments: Any,
        min_poll_interval_sec: float = 3.0,
        stale_after_sec: float = 20.0,
        backoff_base_sec: float = 5.0,
        backoff_max_sec: float = 60.0,
        emit_cached_during_backoff: bool = True,
    ) -> None:
        self._client = client
        self._runtime_instruments = runtime_instruments
        self._min_poll_interval_sec = max(0.0, float(min_poll_interval_sec))
        self._stale_after_sec = max(1.0, float(stale_after_sec))
        self._backoff_base_sec = max(1.0, float(backoff_base_sec))
        self._backoff_max_sec = max(self._backoff_base_sec, float(backoff_max_sec))
        self._emit_cached_during_backoff = bool(emit_cached_during_backoff)

        self._last_fetch_monotonic = 0.0
        self._last_success_monotonic = 0.0
        self._backoff_until_monotonic = 0.0
        self._last_good_item: dict[str, Any] | None = None
        self._consecutive_failures = 0
        self._last_error = ""
        self._last_error_kind = ""

    def info(self) -> dict[str, Any]:
        now = time.monotonic()
        return {
            "adapter_name": self.__class__.__name__,
            "provider_id": "DHAN",
            "mode": "OPTIONCHAIN_CONTEXT_POLL",
            "min_poll_interval_sec": self._min_poll_interval_sec,
            "stale_after_sec": self._stale_after_sec,
            "backoff_base_sec": self._backoff_base_sec,
            "backoff_max_sec": self._backoff_max_sec,
            "backoff_active": now < self._backoff_until_monotonic,
            "consecutive_failures": self._consecutive_failures,
            "last_error_kind": self._last_error_kind,
            "has_cached_context": self._last_good_item is not None,
            "cache_age_sec": self._cache_age_sec(now),
        }

    def health(self) -> dict[str, Any]:
        payload = self.info()
        payload["last_error"] = self._last_error
        return payload

    @staticmethod
    def _contract_key(contract: Any) -> str:
        trading_symbol = _norm(getattr(contract, "tradingsymbol", None))
        instrument_key = _norm(getattr(contract, "instrument_key", None))
        return instrument_key or f"NFO:{trading_symbol}"

    @staticmethod
    def _extract_security_id(side_block: Mapping[str, Any] | None) -> str | None:
        if not isinstance(side_block, Mapping):
            return None
        val = side_block.get("security_id")
        return _norm(val) or None

    @staticmethod
    def _extract_ltp(side_block: Mapping[str, Any] | None) -> float | None:
        if not isinstance(side_block, Mapping):
            return None
        val = side_block.get("last_price")
        return _as_float(val)

    @staticmethod
    def _classify_error(exc: Exception) -> str:
        text = str(exc).lower()
        if "429" in text or "rate" in text or "throttl" in text or "too many" in text:
            return "RATE_LIMITED"
        if "timeout" in text or "timed out" in text:
            return "TIMEOUT"
        if "unauthor" in text or "forbidden" in text or "401" in text or "403" in text:
            return "AUTH_OR_PERMISSION"
        return "UNAVAILABLE"

    def _cache_age_sec(self, now: float | None = None) -> float | None:
        if self._last_good_item is None or self._last_success_monotonic <= 0:
            return None
        now = time.monotonic() if now is None else now
        return max(0.0, now - self._last_success_monotonic)

    def _backoff_delay_sec(self) -> float:
        multiplier = 2 ** min(max(self._consecutive_failures - 1, 0), 6)
        return min(self._backoff_max_sec, self._backoff_base_sec * multiplier)

    def _mark_failure(self, exc: Exception, *, now: float) -> None:
        self._consecutive_failures += 1
        self._last_error = str(exc) or exc.__class__.__name__
        self._last_error_kind = self._classify_error(exc)
        self._backoff_until_monotonic = now + self._backoff_delay_sec()

    def _mark_success(self, *, now: float, item: dict[str, Any]) -> None:
        self._last_success_monotonic = now
        self._backoff_until_monotonic = 0.0
        self._consecutive_failures = 0
        self._last_error = ""
        self._last_error_kind = ""
        self._last_good_item = item

    def _decorate_cached_item(
        self,
        item: Mapping[str, Any],
        *,
        now: float,
        source: str,
    ) -> dict[str, Any]:
        out = dict(item)
        payload_raw = out.get("payload")
        payload = dict(payload_raw) if isinstance(payload_raw, Mapping) else {}

        age = self._cache_age_sec(now)
        stale = bool(age is not None and age > self._stale_after_sec)

        if source == "LIVE":
            status = "HEALTHY"
        elif stale:
            status = "STALE"
        else:
            status = "DEGRADED"

        payload.update(
            {
                "context_status": status,
                "provider_id": "DHAN",
                "context_source": source,
                "context_cache_age_sec": age,
                "context_stale": stale,
                "context_backoff_active": now < self._backoff_until_monotonic,
                "context_consecutive_failures": self._consecutive_failures,
                "context_last_error_kind": self._last_error_kind,
                "context_last_error": self._last_error,
            }
        )

        out["record_type"] = out.get("record_type") or "dhan_context"
        out["payload"] = payload
        return out

    def _build_item_from_snapshot(self, snap: Mapping[str, Any]) -> dict[str, Any] | None:
        data = snap.get("data") if isinstance(snap, Mapping) else None
        oc = data.get("oc") if isinstance(data, Mapping) else None
        if not isinstance(oc, Mapping):
            return None

        ce_atm = getattr(self._runtime_instruments, "ce_atm", None)
        pe_atm = getattr(self._runtime_instruments, "pe_atm", None)

        selected_call_key = self._contract_key(ce_atm) if ce_atm is not None else None
        selected_put_key = self._contract_key(pe_atm) if pe_atm is not None else None

        selected_call_score = None
        selected_put_score = None
        selected_call_security_id = None
        selected_put_security_id = None

        for strike_raw, block in oc.items():
            if not isinstance(block, Mapping):
                continue

            strike_val = _as_float(strike_raw)

            if (
                ce_atm is not None
                and strike_val is not None
                and abs(strike_val - float(getattr(ce_atm, "strike"))) < 0.001
            ):
                ce_block = block.get("ce")
                selected_call_score = self._extract_ltp(ce_block)
                selected_call_security_id = self._extract_security_id(ce_block)

            if (
                pe_atm is not None
                and strike_val is not None
                and abs(strike_val - float(getattr(pe_atm, "strike"))) < 0.001
            ):
                pe_block = block.get("pe")
                selected_put_score = self._extract_ltp(pe_block)
                selected_put_security_id = self._extract_security_id(pe_block)

        atm_strike = None
        if ce_atm is not None:
            atm_strike = _as_float(getattr(ce_atm, "strike", None))
        if atm_strike is None and pe_atm is not None:
            atm_strike = _as_float(getattr(pe_atm, "strike", None))

        payload = {
            "context_status": "HEALTHY",
            "provider_id": "DHAN",
            "context_source": "LIVE",
            "context_epoch_ns": time.time_ns(),
            "atm_strike": atm_strike,
            "selected_call_instrument_key": selected_call_key or "",
            "selected_put_instrument_key": selected_put_key or "",
            "selected_call_security_id": selected_call_security_id or "",
            "selected_put_security_id": selected_put_security_id or "",
            "selected_call_score": selected_call_score,
            "selected_put_score": selected_put_score,
        }

        return {
            "record_type": "dhan_context",
            "payload": payload,
        }

    def poll(self) -> list[dict[str, Any]]:
        now = time.monotonic()

        if now < self._backoff_until_monotonic:
            if self._emit_cached_during_backoff and self._last_good_item is not None:
                return [
                    self._decorate_cached_item(
                        self._last_good_item,
                        now=now,
                        source="CACHED_BACKOFF",
                    )
                ]
            return []

        if (
            self._last_good_item is not None
            and self._min_poll_interval_sec > 0
            and (now - self._last_fetch_monotonic) < self._min_poll_interval_sec
        ):
            return [
                self._decorate_cached_item(
                    self._last_good_item,
                    now=now,
                    source="CACHED_INTERVAL",
                )
            ]

        self._last_fetch_monotonic = now

        try:
            snap = self._client.fetch_chain_snapshot()
            item = self._build_item_from_snapshot(snap)
            if item is None:
                raise DhanRuntimeUnavailableError(
                    "Dhan option-chain snapshot missing data.oc mapping"
                )
        except Exception as exc:
            self._mark_failure(exc, now=now)
            if self._emit_cached_during_backoff and self._last_good_item is not None:
                return [
                    self._decorate_cached_item(
                        self._last_good_item,
                        now=now,
                        source="CACHED_ERROR",
                    )
                ]
            return []

        self._mark_success(now=now, item=item)
        return [
            self._decorate_cached_item(
                item,
                now=now,
                source="LIVE",
            )
        ]


__all__ = [
    "DhanRuntimeClientError",
    "DhanRuntimeValidationError",
    "DhanRuntimeUnavailableError",
    "ResolvedDhanRuntimeIds",
    "DhanNiftyRuntimeResolver",
    "DhanOptionChainContextClient",
    "DhanContextPollingAdapter",
    "DhanTwentyDepthLiveFeedClient",
    "DhanFullFeedPollingAdapter",
]
