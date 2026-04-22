from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUN_ROOT = PROJECT_ROOT / "run" / "validation" / "dhan_closed_market"
DHAN_HISTORICAL_URL = "https://api.dhan.co/v2/charts/historical"
DHAN_INTRADAY_URL = "https://api.dhan.co/v2/charts/intraday"
DHAN_ROLLING_OPTION_URL = "https://api.dhan.co/v2/charts/rollingoption"
DHAN_QUOTE_URL = "https://api.dhan.co/v2/marketfeed/quote"

BROKER_ENV_CANDIDATES = (
    PROJECT_ROOT / "common" / "secrets" / "brokers" / "dhan" / "credentials.env",
    PROJECT_ROOT / "common" / "secrets" / "brokers" / "dhan" / "session.env",
    PROJECT_ROOT / "common" / "secrets" / "brokers" / "dhan" / "runtime.env",
    PROJECT_ROOT / "common" / "secrets" / "brokers" / "dhan" / ".env",
    PROJECT_ROOT / "etc" / "brokers" / "dhan.env",
)


class ValidationError(RuntimeError):
    """Raised when the validation harness cannot proceed."""


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def now_utc_iso() -> str:
    return now_utc().isoformat()


def read_env_file(path: Path) -> bool:
    if not path.exists():
        return False
    if not path.is_file():
        raise ValidationError(f"env path is not a file: {path}")

    loaded = False
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            raise ValidationError(f"invalid env line without '=' in {path}:{lineno}")
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if value and len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        if key and key not in os.environ:
            os.environ[key] = value
            loaded = True
    return loaded


def preload_dhan_env() -> list[str]:
    loaded_paths: list[str] = []
    for candidate in BROKER_ENV_CANDIDATES:
        try:
            if read_env_file(candidate):
                loaded_paths.append(str(candidate))
        except Exception as exc:
            raise ValidationError(f"failed loading env file {candidate}: {exc}") from exc
    return loaded_paths


def env(*keys: str) -> str:
    for key in keys:
        value = os.getenv(key, "").strip()
        if value:
            return value
    return ""


def http_post_json(
    url: str,
    *,
    client_id: str,
    access_token: str,
    payload: Mapping[str, Any],
    timeout_s: int = 20,
) -> Any:
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "access-token": access_token,
        "client-id": client_id,
    }
    try:
        response = requests.post(url, headers=headers, json=dict(payload), timeout=timeout_s)
    except Exception as exc:
        raise ValidationError(f"HTTP request failed for {url}: {exc}") from exc

    text = response.text.strip()
    if not text:
        body: Any = {}
    else:
        try:
            body = response.json()
        except Exception:
            body = {"raw_text": text}

    if response.status_code >= 400:
        raise ValidationError(f"HTTP {response.status_code} for {url}: {body}")
    return body


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")


def aligned_candle_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    keys = ("open", "high", "low", "close", "volume", "timestamp")
    lengths = {key: len(payload.get(key, []) or []) for key in keys}
    unique_lengths = sorted(set(lengths.values()))
    timestamps = list(payload.get("timestamp", []) or [])
    monotonic = all(int(timestamps[i]) < int(timestamps[i + 1]) for i in range(len(timestamps) - 1))
    non_empty = len(timestamps) > 0
    return {
        "lengths": lengths,
        "aligned": len(unique_lengths) == 1,
        "non_empty": non_empty,
        "monotonic_timestamps": monotonic,
        "first_timestamp": timestamps[0] if timestamps else None,
        "last_timestamp": timestamps[-1] if timestamps else None,
    }


def rolling_option_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = payload.get("data", {}) or {}
    ce = data.get("ce")
    pe = data.get("pe")
    out: dict[str, Any] = {}

    for side_name, side_payload in (("ce", ce), ("pe", pe)):
        if side_payload is None:
            out[side_name] = {
                "present": False,
                "non_empty": False,
                "aligned": False,
                "monotonic_timestamps": False,
            }
            continue

        timestamps = list(side_payload.get("timestamp", []) or [])
        required_lengths = {
            "timestamp": len(timestamps),
            "open": len(side_payload.get("open", []) or []),
            "high": len(side_payload.get("high", []) or []),
            "low": len(side_payload.get("low", []) or []),
            "close": len(side_payload.get("close", []) or []),
            "volume": len(side_payload.get("volume", []) or []),
        }
        optional_lengths = {
            "iv": len(side_payload.get("iv", []) or []),
            "oi": len(side_payload.get("oi", []) or []),
            "spot": len(side_payload.get("spot", []) or []),
            "strike": len(side_payload.get("strike", []) or []),
        }
        monotonic = all(int(timestamps[i]) < int(timestamps[i + 1]) for i in range(len(timestamps) - 1))
        aligned_required = len(set(required_lengths.values())) == 1
        out[side_name] = {
            "present": True,
            "non_empty": len(timestamps) > 0,
            "aligned": aligned_required,
            "monotonic_timestamps": monotonic,
            "required_lengths": required_lengths,
            "optional_lengths": optional_lengths,
            "first_timestamp": timestamps[0] if timestamps else None,
            "last_timestamp": timestamps[-1] if timestamps else None,
        }
    return out


def quote_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = payload.get("data", {}) or {}
    rows = 0
    depth_rows = 0
    instruments: list[str] = []
    for segment, segment_payload in data.items():
        if not isinstance(segment_payload, Mapping):
            continue
        for security_id, row in segment_payload.items():
            rows += 1
            instruments.append(f"{segment}:{security_id}")
            depth = row.get("depth", {}) if isinstance(row, Mapping) else {}
            if isinstance(depth, Mapping):
                buy = depth.get("buy", []) or []
                sell = depth.get("sell", []) or []
                depth_rows += len(buy) + len(sell)
    return {
        "status": payload.get("status"),
        "row_count": rows,
        "depth_rows": depth_rows,
        "instruments": instruments,
    }


def import_module_summary(module_name: str) -> dict[str, Any]:
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:
        return {"import_ok": False, "error": f"{type(exc).__name__}: {exc}"}

    summary = {
        "import_ok": True,
        "module_name": module_name,
        "file": getattr(module, "__file__", ""),
    }

    interesting = [
        "SYNC_WINDOW_MS",
        "FEED_STALE_MS",
        "REGIME_MIN_HISTORY",
        "VELOCITY_REGIME_MIN",
        "SPREAD_REGIME_MAX",
        "SnapshotFrameView",
        "SnapshotMemberView",
        "LegHistory",
    ]
    found: dict[str, Any] = {}
    for name in interesting:
        if hasattr(module, name):
            value = getattr(module, name)
            found[name] = value if isinstance(value, (int, float, str, bool)) else type(value).__name__
    summary["surfaces_found"] = found
    return summary


@dataclass(frozen=True)
class FetchConfig:
    client_id: str
    access_token: str
    fut_security_id: str
    underlying_security_id: str
    quote_security_ids: tuple[str, ...]
    exchange_segment: str
    fut_instrument: str
    opt_instrument: str
    interval: str
    expiry_flag: str
    expiry_code: int
    rolling_from_date: str
    rolling_to_date: str
    intraday_from_date: str
    intraday_to_date: str


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    now = now_utc()
    intraday_to = now.replace(second=0, microsecond=0)
    intraday_from = intraday_to - timedelta(days=3)
    rolling_to = now.date().isoformat()
    rolling_from = (now.date() - timedelta(days=7)).isoformat()

    parser = argparse.ArgumentParser(
        description="Closed-market Dhan validation harness for frozen feeds.py and features.py"
    )
    parser.add_argument("--client-id", default=env("DHAN_CLIENT_ID", "MME_DHAN_CLIENT_ID"))
    parser.add_argument("--access-token", default=env("DHAN_ACCESS_TOKEN", "MME_DHAN_ACCESS_TOKEN"))
    parser.add_argument("--fut-security-id", required=True, help="Dhan securityId for the futures/underlying historical lane")
    parser.add_argument("--underlying-security-id", required=True, help="Dhan underlying securityId for rolling option data")
    parser.add_argument(
        "--quote-security-id",
        action="append",
        dest="quote_security_ids",
        default=[],
        help="One or more Dhan securityIds for /marketfeed/quote snapshot checks; can be repeated",
    )
    parser.add_argument("--exchange-segment", default="NSE_FNO")
    parser.add_argument("--fut-instrument", default="FUTIDX")
    parser.add_argument("--opt-instrument", default="OPTIDX")
    parser.add_argument("--interval", default="1", choices=("1", "5", "15", "25", "60"))
    parser.add_argument("--expiry-flag", default="WEEK", choices=("WEEK", "MONTH"))
    parser.add_argument("--expiry-code", default=0, type=int)
    parser.add_argument("--rolling-from-date", default=rolling_from)
    parser.add_argument("--rolling-to-date", default=rolling_to)
    parser.add_argument("--intraday-from-date", default=intraday_from.strftime("%Y-%m-%d %H:%M:%S"))
    parser.add_argument("--intraday-to-date", default=intraday_to.strftime("%Y-%m-%d %H:%M:%S"))
    return parser.parse_args(argv)


def build_config(args: argparse.Namespace) -> FetchConfig:
    client_id = args.client_id.strip()
    access_token = args.access_token.strip()
    if not client_id:
        raise ValidationError("missing Dhan client id; set DHAN_CLIENT_ID or pass --client-id")
    if not access_token:
        raise ValidationError("missing Dhan access token; set DHAN_ACCESS_TOKEN or pass --access-token")
    quote_ids = tuple(dict.fromkeys([args.fut_security_id, *args.quote_security_ids]))
    return FetchConfig(
        client_id=client_id,
        access_token=access_token,
        fut_security_id=str(args.fut_security_id).strip(),
        underlying_security_id=str(args.underlying_security_id).strip(),
        quote_security_ids=quote_ids,
        exchange_segment=str(args.exchange_segment).strip(),
        fut_instrument=str(args.fut_instrument).strip(),
        opt_instrument=str(args.opt_instrument).strip(),
        interval=str(args.interval).strip(),
        expiry_flag=str(args.expiry_flag).strip(),
        expiry_code=int(args.expiry_code),
        rolling_from_date=str(args.rolling_from_date).strip(),
        rolling_to_date=str(args.rolling_to_date).strip(),
        intraday_from_date=str(args.intraday_from_date).strip(),
        intraday_to_date=str(args.intraday_to_date).strip(),
    )


def main(argv: Sequence[str] | None = None) -> int:
    loaded_env_paths = preload_dhan_env()
    args = parse_args(argv)
    cfg = build_config(args)

    run_id = now_utc().strftime("%Y%m%d_%H%M%S")
    out_dir = RUN_ROOT / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    module_checks = {
        "feeds": import_module_summary("app.mme_scalpx.services.feeds"),
        "features": import_module_summary("app.mme_scalpx.services.features"),
    }

    quote_payload = http_post_json(
        DHAN_QUOTE_URL,
        client_id=cfg.client_id,
        access_token=cfg.access_token,
        payload={cfg.exchange_segment: list(cfg.quote_security_ids)},
    )
    write_json(out_dir / "quote.json", quote_payload)

    intraday_payload = http_post_json(
        DHAN_INTRADAY_URL,
        client_id=cfg.client_id,
        access_token=cfg.access_token,
        payload={
            "securityId": cfg.fut_security_id,
            "exchangeSegment": cfg.exchange_segment,
            "instrument": cfg.fut_instrument,
            "interval": cfg.interval,
            "oi": True,
            "fromDate": cfg.intraday_from_date,
            "toDate": cfg.intraday_to_date,
        },
    )
    write_json(out_dir / "fut_intraday.json", intraday_payload)

    rolling_ce_payload = http_post_json(
        DHAN_ROLLING_OPTION_URL,
        client_id=cfg.client_id,
        access_token=cfg.access_token,
        payload={
            "exchangeSegment": cfg.exchange_segment,
            "interval": cfg.interval,
            "securityId": cfg.underlying_security_id,
            "instrument": cfg.opt_instrument,
            "expiryFlag": cfg.expiry_flag,
            "expiryCode": cfg.expiry_code,
            "strike": "ATM",
            "drvOptionType": "CALL",
            "requiredData": ["open", "high", "low", "close", "iv", "volume", "oi", "spot", "strike"],
            "fromDate": cfg.rolling_from_date,
            "toDate": cfg.rolling_to_date,
        },
    )
    write_json(out_dir / "rolling_call.json", rolling_ce_payload)

    rolling_pe_payload = http_post_json(
        DHAN_ROLLING_OPTION_URL,
        client_id=cfg.client_id,
        access_token=cfg.access_token,
        payload={
            "exchangeSegment": cfg.exchange_segment,
            "interval": cfg.interval,
            "securityId": cfg.underlying_security_id,
            "instrument": cfg.opt_instrument,
            "expiryFlag": cfg.expiry_flag,
            "expiryCode": cfg.expiry_code,
            "strike": "ATM",
            "drvOptionType": "PUT",
            "requiredData": ["open", "high", "low", "close", "iv", "volume", "oi", "spot", "strike"],
            "fromDate": cfg.rolling_from_date,
            "toDate": cfg.rolling_to_date,
        },
    )
    write_json(out_dir / "rolling_put.json", rolling_pe_payload)

    intraday_summary = aligned_candle_summary(intraday_payload if isinstance(intraday_payload, Mapping) else {})
    rolling_call_summary = rolling_option_summary(rolling_ce_payload if isinstance(rolling_ce_payload, Mapping) else {})
    rolling_put_summary = rolling_option_summary(rolling_pe_payload if isinstance(rolling_pe_payload, Mapping) else {})
    quote_check = quote_summary(quote_payload if isinstance(quote_payload, Mapping) else {})

    checks = {
        "feeds_import_ok": bool(module_checks["feeds"].get("import_ok")),
        "features_import_ok": bool(module_checks["features"].get("import_ok")),
        "intraday_aligned": bool(intraday_summary["aligned"]),
        "intraday_non_empty": bool(intraday_summary["non_empty"]),
        "intraday_monotonic": bool(intraday_summary["monotonic_timestamps"]),
        "rolling_call_present": bool(rolling_call_summary["ce"]["present"]),
        "rolling_call_non_empty": bool(rolling_call_summary["ce"]["non_empty"]),
        "rolling_call_aligned": bool(rolling_call_summary["ce"]["aligned"]),
        "rolling_put_present": bool(rolling_put_summary["pe"]["present"]),
        "rolling_put_non_empty": bool(rolling_put_summary["pe"]["non_empty"]),
        "rolling_put_aligned": bool(rolling_put_summary["pe"]["aligned"]),
        "quote_rows_non_empty": int(quote_check["row_count"]) > 0,
        "quote_depth_present": int(quote_check["depth_rows"]) > 0,
    }
    overall_ok = all(checks.values())

    summary = {
        "run_id": run_id,
        "created_at_utc": now_utc_iso(),
        "loaded_env_paths": loaded_env_paths,
        "config": {
            "client_id": cfg.client_id,
            "exchange_segment": cfg.exchange_segment,
            "fut_security_id": cfg.fut_security_id,
            "underlying_security_id": cfg.underlying_security_id,
            "quote_security_ids": list(cfg.quote_security_ids),
            "fut_instrument": cfg.fut_instrument,
            "opt_instrument": cfg.opt_instrument,
            "interval": cfg.interval,
            "expiry_flag": cfg.expiry_flag,
            "expiry_code": cfg.expiry_code,
            "rolling_from_date": cfg.rolling_from_date,
            "rolling_to_date": cfg.rolling_to_date,
            "intraday_from_date": cfg.intraday_from_date,
            "intraday_to_date": cfg.intraday_to_date,
        },
        "module_checks": module_checks,
        "quote_summary": quote_check,
        "intraday_summary": intraday_summary,
        "rolling_call_summary": rolling_call_summary,
        "rolling_put_summary": rolling_put_summary,
        "checks": checks,
        "overall_ok": overall_ok,
    }
    write_json(out_dir / "summary.json", summary)

    print(f"run_dir={out_dir}")
    print(f"overall_ok={overall_ok}")
    for key, value in checks.items():
        print(f"{key}={value}")
    return 0 if overall_ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
