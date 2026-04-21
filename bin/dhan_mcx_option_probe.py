from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from dataclasses import dataclass
from datetime import date, datetime
from io import StringIO
from typing import Any, Iterable

import requests


INSTRUMENT_CSV_URL = "https://images.dhan.co/api-data/api-scrip-master-detailed.csv"
API_BASE = "https://api.dhan.co/v2"
DEFAULT_TIMEOUT = 20


@dataclass(frozen=True)
class ContractView:
    strike: float
    security_id: int
    option_type: str
    last_price: float | None
    top_bid_price: float | None
    top_ask_price: float | None
    top_bid_quantity: int | None
    top_ask_quantity: int | None
    volume: int | None
    oi: int | None
    implied_volatility: float | None
    greeks: dict[str, Any]


def _norm(s: str | None) -> str:
    return (s or "").strip()


def _upper(s: str | None) -> str:
    return _norm(s).upper()


def _as_float(v: Any) -> float | None:
    if v in (None, "", "NA", "null"):
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _as_int(v: Any) -> int | None:
    if v in (None, "", "NA", "null"):
        return None
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def _pick(row: dict[str, Any], *keys: str) -> str:
    for key in keys:
        if key in row and row[key] not in (None, ""):
            return str(row[key]).strip()
    return ""


def fetch_instrument_master(session: requests.Session) -> list[dict[str, str]]:
    response = session.get(INSTRUMENT_CSV_URL, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
    csv_text = response.text.lstrip("\ufeff")
    return list(csv.DictReader(StringIO(csv_text)))


def find_underlying_and_candidates(
    rows: Iterable[dict[str, str]],
    commodity_symbol: str,
) -> tuple[int, list[dict[str, str]]]:
    symbol = commodity_symbol.upper()
    candidates: list[dict[str, str]] = []

    for row in rows:
        exch = _upper(_pick(row, "EXCH_ID", "SEM_EXM_EXCH_ID"))
        underlying_symbol = _upper(_pick(row, "UNDERLYING_SYMBOL"))
        option_type = _upper(_pick(row, "OPTION_TYPE", "SEM_OPTION_TYPE"))
        if exch != "MCX":
            continue
        if underlying_symbol == symbol and option_type in {"CE", "PE"}:
            candidates.append(row)

    if not candidates:
        raise RuntimeError(
            f"No MCX option contracts found for underlying symbol={symbol!r} in Dhan instrument master."
        )

    underlying_ids = {
        _as_int(_pick(row, "UNDERLYING_SECURITY_ID"))
        for row in candidates
        if _as_int(_pick(row, "UNDERLYING_SECURITY_ID")) is not None
    }
    if not underlying_ids:
        raise RuntimeError(
            f"Could not resolve UNDERLYING_SECURITY_ID for MCX options of {symbol}."
        )
    if len(underlying_ids) != 1:
        raise RuntimeError(
            f"Expected one underlying id for {symbol}, got {sorted(x for x in underlying_ids if x is not None)}."
        )

    return next(iter(underlying_ids)), candidates


def post_json(
    session: requests.Session,
    path: str,
    client_id: str,
    access_token: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "client-id": client_id,
        "access-token": access_token,
    }
    response = session.post(
        f"{API_BASE}{path}",
        headers=headers,
        json=payload,
        timeout=DEFAULT_TIMEOUT,
    )
    try:
        data = response.json()
    except Exception as exc:
        raise RuntimeError(
            f"Non-JSON response from {path}: HTTP {response.status_code}, body={response.text[:500]!r}"
        ) from exc

    if response.status_code >= 400:
        raise RuntimeError(
            f"{path} failed: HTTP {response.status_code}, response={json.dumps(data, ensure_ascii=False)}"
        )
    return data


def get_expiries(
    session: requests.Session,
    client_id: str,
    access_token: str,
    underlying_scrip: int,
) -> list[str]:
    data = post_json(
        session=session,
        path="/optionchain/expirylist",
        client_id=client_id,
        access_token=access_token,
        payload={
            "UnderlyingScrip": underlying_scrip,
            "UnderlyingSeg": "MCX_COMM",
        },
    )
    expiries = data.get("data") or data.get("expiries") or data.get("expiryList") or []
    if not isinstance(expiries, list):
        raise RuntimeError(
            f"Unexpected expirylist payload: {json.dumps(data, ensure_ascii=False)[:800]}"
        )
    expiries = [str(x) for x in expiries if str(x).strip()]
    if not expiries:
        raise RuntimeError(
            f"No expiries returned for underlying_scrip={underlying_scrip}. Full response={json.dumps(data, ensure_ascii=False)}"
        )
    return expiries


def choose_expiry(expiries: list[str], requested: str | None) -> str:
    if requested:
        if requested not in expiries:
            raise RuntimeError(
                f"Requested expiry {requested!r} not in active expiries: {expiries}"
            )
        return requested

    today = date.today()
    parsed: list[tuple[date, str]] = []
    for expiry in expiries:
        try:
            parsed.append((datetime.strptime(expiry, "%Y-%m-%d").date(), expiry))
        except ValueError:
            pass

    if parsed:
        future_or_today = sorted((d, raw) for d, raw in parsed if d >= today)
        if future_or_today:
            return future_or_today[0][1]
        return sorted(parsed)[0][1]

    return expiries[0]


def get_option_chain(
    session: requests.Session,
    client_id: str,
    access_token: str,
    underlying_scrip: int,
    expiry: str,
) -> dict[str, Any]:
    data = post_json(
        session=session,
        path="/optionchain",
        client_id=client_id,
        access_token=access_token,
        payload={
            "UnderlyingScrip": underlying_scrip,
            "UnderlyingSeg": "MCX_COMM",
            "Expiry": expiry,
        },
    )
    if (data.get("status") or "").lower() not in {"", "success"}:
        raise RuntimeError(
            f"Option chain returned non-success status: {json.dumps(data, ensure_ascii=False)}"
        )
    return data


def parse_contracts(option_chain_data: dict[str, Any]) -> tuple[float | None, list[ContractView]]:
    data = option_chain_data.get("data") or {}
    underlying_last_price = _as_float(data.get("last_price"))
    oc = data.get("oc") or {}
    if not isinstance(oc, dict) or not oc:
        raise RuntimeError(
            f"Option chain has no strike data: {json.dumps(option_chain_data, ensure_ascii=False)[:1200]}"
        )

    contracts: list[ContractView] = []
    for strike_raw, strike_block in oc.items():
        strike = _as_float(strike_raw)
        if strike is None:
            continue
        if not isinstance(strike_block, dict):
            continue
        for option_type in ("ce", "pe"):
            side = strike_block.get(option_type)
            if not isinstance(side, dict):
                continue
            security_id = _as_int(side.get("security_id"))
            if security_id is None:
                continue
            contracts.append(
                ContractView(
                    strike=float(strike),
                    security_id=security_id,
                    option_type=option_type.upper(),
                    last_price=_as_float(side.get("last_price")),
                    top_bid_price=_as_float(side.get("top_bid_price")),
                    top_ask_price=_as_float(side.get("top_ask_price")),
                    top_bid_quantity=_as_int(side.get("top_bid_quantity")),
                    top_ask_quantity=_as_int(side.get("top_ask_quantity")),
                    volume=_as_int(side.get("volume")),
                    oi=_as_int(side.get("oi")),
                    implied_volatility=_as_float(side.get("implied_volatility")),
                    greeks=side.get("greeks") if isinstance(side.get("greeks"), dict) else {},
                )
            )
    if not contracts:
        raise RuntimeError("Option chain parsed zero option contracts.")
    return underlying_last_price, contracts


def pick_atm_pair(
    underlying_last_price: float | None,
    contracts: list[ContractView],
) -> tuple[float, ContractView | None, ContractView | None]:
    strikes = sorted({c.strike for c in contracts})
    if not strikes:
        raise RuntimeError("No strikes found in option chain.")
    if underlying_last_price is None:
        atm_strike = strikes[len(strikes) // 2]
    else:
        atm_strike = min(strikes, key=lambda x: abs(x - underlying_last_price))

    ce = next((c for c in contracts if c.strike == atm_strike and c.option_type == "CE"), None)
    pe = next((c for c in contracts if c.strike == atm_strike and c.option_type == "PE"), None)
    return atm_strike, ce, pe


def get_market_quote(
    session: requests.Session,
    client_id: str,
    access_token: str,
    security_ids: list[int],
) -> dict[str, Any]:
    data = post_json(
        session=session,
        path="/marketfeed/quote",
        client_id=client_id,
        access_token=access_token,
        payload={"MCX_COMM": security_ids},
    )
    if (data.get("status") or "").lower() not in {"", "success"}:
        raise RuntimeError(
            f"Market quote returned non-success status: {json.dumps(data, ensure_ascii=False)}"
        )
    return data


def summarize_contract(c: ContractView | None) -> dict[str, Any] | None:
    if c is None:
        return None
    spread = None
    if c.top_bid_price is not None and c.top_ask_price is not None:
        spread = c.top_ask_price - c.top_bid_price
    return {
        "security_id": c.security_id,
        "option_type": c.option_type,
        "strike": c.strike,
        "last_price": c.last_price,
        "top_bid_price": c.top_bid_price,
        "top_ask_price": c.top_ask_price,
        "spread": spread,
        "top_bid_quantity": c.top_bid_quantity,
        "top_ask_quantity": c.top_ask_quantity,
        "volume": c.volume,
        "oi": c.oi,
        "implied_volatility": c.implied_volatility,
        "greeks": c.greeks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Standalone smoke test for Dhan MCX option data."
    )
    parser.add_argument(
        "--symbol",
        default="CRUDEOIL",
        help="MCX underlying symbol, e.g. CRUDEOIL, GOLD, SILVER, COPPER.",
    )
    parser.add_argument(
        "--expiry",
        default=None,
        help="Exact expiry date YYYY-MM-DD. Default: nearest active expiry.",
    )
    parser.add_argument(
        "--client-id",
        default=os.getenv("DHAN_CLIENT_ID"),
        help="Dhan client id. Can also come from DHAN_CLIENT_ID.",
    )
    parser.add_argument(
        "--access-token",
        default=os.getenv("DHAN_ACCESS_TOKEN"),
        help="Dhan access token. Can also come from DHAN_ACCESS_TOKEN.",
    )
    parser.add_argument(
        "--print-raw",
        action="store_true",
        help="Print raw option-chain and market-quote payload excerpts.",
    )
    args = parser.parse_args()

    if not args.client_id or not args.access_token:
        print(
            "ERROR: missing Dhan credentials. Set DHAN_CLIENT_ID and DHAN_ACCESS_TOKEN or pass --client-id/--access-token.",
            file=sys.stderr,
        )
        return 2

    session = requests.Session()

    try:
        rows = fetch_instrument_master(session)
        underlying_scrip, option_rows = find_underlying_and_candidates(rows, args.symbol)
        expiries = get_expiries(session, args.client_id, args.access_token, underlying_scrip)
        chosen_expiry = choose_expiry(expiries, args.expiry)
        option_chain = get_option_chain(
            session, args.client_id, args.access_token, underlying_scrip, chosen_expiry
        )
        underlying_last_price, contracts = parse_contracts(option_chain)
        atm_strike, ce, pe = pick_atm_pair(underlying_last_price, contracts)

        security_ids = [c.security_id for c in (ce, pe) if c is not None]
        if not security_ids:
            raise RuntimeError("Could not resolve ATM CE/PE security ids from option chain.")

        market_quote = get_market_quote(
            session, args.client_id, args.access_token, security_ids
        )

        summary = {
            "probe_ok": True,
            "exchange_segment": "MCX_COMM",
            "symbol": args.symbol.upper(),
            "underlying_scrip": underlying_scrip,
            "active_expiries": expiries,
            "chosen_expiry": chosen_expiry,
            "underlying_last_price": underlying_last_price,
            "instrument_master_option_rows_found": len(option_rows),
            "option_chain_contracts_found": len(contracts),
            "atm_strike": atm_strike,
            "atm_ce": summarize_contract(ce),
            "atm_pe": summarize_contract(pe),
            "market_quote_keys": list((market_quote.get("data") or {}).keys()),
            "market_quote_excerpt": (market_quote.get("data") or {}).get("MCX_COMM", {}),
        }

        print(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=False, default=str))

        if args.print_raw:
            print("\n=== RAW OPTION CHAIN (truncated) ===")
            print(json.dumps(option_chain, indent=2, ensure_ascii=False)[:4000])
            print("\n=== RAW MARKET QUOTE ===")
            print(json.dumps(market_quote, indent=2, ensure_ascii=False)[:4000])

        return 0

    except requests.HTTPError as exc:
        body = ""
        if exc.response is not None:
            try:
                body = exc.response.text[:1000]
            except Exception:
                body = "<unreadable>"
        print(f"HTTP ERROR: {exc}. body={body}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"PROBE FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
