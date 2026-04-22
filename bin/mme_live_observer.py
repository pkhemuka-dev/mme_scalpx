#!/usr/bin/env python3
from __future__ import annotations

"""
Freeze-safe live observer for ScalpX MME feeds/features runtime.

Why this exists
---------------
The frozen migration law keeps feeds.py as the raw fact-ingestion and normalized
raw-publication lane, and features.py as the math / feature lane, so the safest
way to inspect tomorrow's live market behavior is to *observe* the published
Redis surfaces instead of mutating those services.

This observer reads, but does not write:
- feeds lock owner + TTL
- heartbeat hashes and TTLs
- snapshot hashes from feeds
- features / baselines / option-confirm hashes from features
- provider runtime + Dhan context hashes
- recent system health / error stream entries
- recent feeds/features stream entries
- optional live tail of newly appended stream entries

Intended placement
------------------
Save as: bin/mme_live_observer.py
Run from repo root with the project venv.
"""

import argparse
import json
import os
import shutil
import signal
import sys
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, Sequence


STOP_REQUESTED = False


def _request_stop(*_: object) -> None:
    global STOP_REQUESTED
    STOP_REQUESTED = True


signal.signal(signal.SIGINT, _request_stop)
signal.signal(signal.SIGTERM, _request_stop)


def _bootstrap_repo_root() -> Path:
    candidates: list[Path] = []
    seen: set[str] = set()

    def _add(path: Path) -> None:
        key = str(path.resolve())
        if key not in seen:
            seen.add(key)
            candidates.append(path)

    _add(Path.cwd())
    for parent in Path.cwd().parents:
        _add(parent)

    this_file = Path(__file__).resolve()
    _add(this_file.parent)
    for parent in this_file.parents:
        _add(parent)

    for base in candidates:
        if (base / "app").exists():
            sys.path.insert(0, str(base))
            return base

    raise RuntimeError("Could not locate repo root containing ./app.")


REPO_ROOT = _bootstrap_repo_root()

from app.mme_scalpx.core import names as N  # noqa: E402

try:
    from app.mme_scalpx.core import redisx as RX  # noqa: E402
except Exception:
    RX = None  # type: ignore[assignment]


def _build_redis_client() -> Any:
    if RX is not None and hasattr(RX, "build_redis_client"):
        return RX.build_redis_client()

    try:
        import redis  # type: ignore
    except Exception as exc:
        raise RuntimeError(
            "redisx.build_redis_client() unavailable and redis fallback import failed."
        ) from exc

    url = (
        os.getenv("SCALPX_REDIS_URL")
        or os.getenv("REDIS_URL")
        or os.getenv("REDIS_TLS_URL")
        or os.getenv("UPSTASH_REDIS_REST_URL")
    )
    if url:
        return redis.Redis.from_url(url, decode_responses=False)

    host = os.getenv("REDIS_HOST")
    if not host:
        raise RuntimeError("No Redis bootstrap available.")

    port = int(os.getenv("REDIS_PORT", "6379"))
    db = int(os.getenv("REDIS_DB", "0"))
    username = os.getenv("REDIS_USERNAME")
    password = os.getenv("REDIS_PASSWORD")
    ssl = os.getenv("REDIS_SSL", "true").strip().lower() in {"1", "true", "yes", "on"}
    return redis.Redis(
        host=host,
        port=port,
        db=db,
        username=username,
        password=password,
        ssl=ssl,
        decode_responses=False,
    )


@dataclass(frozen=True)
class WatchConfig:
    poll_ms: int
    stream_count: int
    error_count: int
    raw_json_chars: int
    tail_events: bool
    tail_buffer: int
    provider_streams: bool
    no_clear: bool
    once: bool


DEFAULT_TS_KEYS: tuple[str, ...] = (
    "ts_event_ns",
    "ts_ns",
    "frame_ts_ns",
    "ts_frame_ns",
    "last_update_ns",
)


def _decode(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, list):
        return [_decode(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_decode(item) for item in value)
    if isinstance(value, dict):
        return {_decode(k): _decode(v) for k, v in value.items()}
    return value


def _safe_int(value: Any, default: int = 0) -> int:
    if value is None:
        return default
    try:
        text = str(value).strip()
        if text == "":
            return default
        return int(float(text))
    except Exception:
        return default


def _short(text: Any, limit: int) -> str:
    raw = str(text)
    if len(raw) <= limit:
        return raw
    return raw[: max(0, limit - 3)] + "..."


def _compact_json(value: Any, limit: int) -> str:
    try:
        text = json.dumps(value, ensure_ascii=False, separators=(",", ":"), default=str)
    except Exception:
        text = str(value)
    return _short(text, limit)


def _parse_jsonish(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    text = value.strip()
    if text == "":
        return ""
    if text in {"null", "None"}:
        return None
    if not ((text.startswith("{") and text.endswith("}")) or (text.startswith("[") and text.endswith("]"))):
        return value
    try:
        return json.loads(text)
    except Exception:
        return value


def _now_ns() -> int:
    return time.time_ns()


def _format_ns(ts_ns: int) -> str:
    if ts_ns <= 0:
        return "-"
    return datetime.fromtimestamp(ts_ns / 1_000_000_000).strftime("%Y-%m-%d %H:%M:%S")


def _age_s(ts_ns: int) -> float | None:
    if ts_ns <= 0:
        return None
    return max((_now_ns() - ts_ns) / 1_000_000_000, 0.0)


def _age_str(ts_ns: int) -> str:
    age = _age_s(ts_ns)
    if age is None:
        return "-"
    return f"{age:0.2f}s"


def _mapping_ts_ns(mapping: Mapping[str, Any]) -> int:
    for key in DEFAULT_TS_KEYS:
        if key in mapping:
            value = _safe_int(mapping.get(key), 0)
            if value > 0:
                return value
    return 0


def _ttl_status(pttl_ms: int) -> str:
    if pttl_ms == -2:
        return "missing"
    if pttl_ms == -1:
        return "no-expiry"
    return f"{pttl_ms}ms"


def _clear_screen(enabled: bool) -> None:
    if not enabled:
        return
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def _print_section(title: str) -> None:
    print()
    print("=" * 100)
    print(title)
    print("=" * 100)


def _sorted_items(mapping: Mapping[str, Any]) -> list[tuple[str, Any]]:
    return sorted(((str(k), v) for k, v in mapping.items()), key=lambda item: item[0])


def _hgetall(client: Any, key: str) -> dict[str, Any]:
    raw = client.hgetall(key)
    decoded = _decode(raw)
    if isinstance(decoded, dict):
        return {str(k): v for k, v in decoded.items()}
    return {}


def _pttl(client: Any, key: str) -> int:
    try:
        return int(client.pttl(key))
    except Exception:
        return -2


def _get(client: Any, key: str) -> str | None:
    raw = client.get(key)
    if raw is None:
        return None
    decoded = _decode(raw)
    return None if decoded is None else str(decoded)


def _xrevrange(client: Any, key: str, count: int) -> list[tuple[str, dict[str, Any]]]:
    try:
        raw_entries = client.xrevrange(key, count=count)
    except Exception:
        return []

    out: list[tuple[str, dict[str, Any]]] = []
    for entry_id, fields in raw_entries:
        decoded_id = str(_decode(entry_id))
        decoded_fields = _decode(fields)
        if isinstance(decoded_fields, dict):
            out.append((decoded_id, {str(k): v for k, v in decoded_fields.items()}))
    return out


def _heartbeat_summary(client: Any, key: str) -> str:
    data = _hgetall(client, key)
    ttl = _ttl_status(_pttl(client, key))
    if not data:
        return f"{key}: MISSING (ttl={ttl})"

    ts_ns = _mapping_ts_ns(data)
    service = data.get("service", "")
    instance_id = data.get("instance_id", "")
    status = data.get("status", "")
    message = data.get("message", "")
    return (
        f"{key}: status={status or '-'} service={service or '-'} "
        f"instance={instance_id or '-'} age={_age_str(ts_ns)} ttl={ttl} "
        f"message={_short(message or '-', 80)}"
    )


def _lock_summary(client: Any, key: str) -> str:
    owner = _get(client, key)
    ttl_ms = _pttl(client, key)
    return f"{key}: owner={owner or '-'} ttl={_ttl_status(ttl_ms)}"


def _snapshot_member_summary(value: Any) -> str:
    member = _parse_jsonish(value)
    if not isinstance(member, Mapping):
        return _short(member, 160)
    symbol = member.get("trading_symbol") or member.get("instrument_token") or "-"
    return (
        f"symbol={symbol} ltp={member.get('ltp', '-')} bid={member.get('best_bid', '-')} "
        f"ask={member.get('best_ask', '-')} bid_qty_5={member.get('bid_qty_5', '-')} "
        f"ask_qty_5={member.get('ask_qty_5', '-')} age_ms={member.get('age_ms', '-')} "
        f"validity={member.get('validity', '-')} strike={member.get('strike', '-')}"
    )


def _interesting_hash_lines(data: Mapping[str, Any], raw_json_chars: int) -> list[str]:
    lines: list[str] = []
    ts_ns = _mapping_ts_ns(data)
    if ts_ns > 0:
        lines.append(f"updated_at={_format_ns(ts_ns)} age={_age_str(ts_ns)}")

    interesting_order = (
        "frame_id",
        "selection_version",
        "provider_id",
        "active_futures_provider_id",
        "active_selected_option_provider_id",
        "active_option_context_provider_id",
        "futures_marketdata_provider_id",
        "selected_option_marketdata_provider_id",
        "option_context_provider_id",
        "execution_primary_provider_id",
        "execution_fallback_provider_id",
        "validity",
        "validity_reason",
        "sync_ok",
        "ts_span_ms",
        "context_status",
        "family_runtime_mode",
        "failover_mode",
        "override_mode",
        "transition_reason",
        "provider_transition_seq",
        "selected_call_instrument_key",
        "selected_put_instrument_key",
        "selected_call_score",
        "selected_put_score",
    )
    for field in interesting_order:
        if field in data:
            lines.append(f"{field}={data.get(field)}")

    for field in (
        "future_json",
        "selected_call_json",
        "selected_put_json",
        "ce_atm_json",
        "ce_atm1_json",
        "pe_atm_json",
        "pe_atm1_json",
    ):
        if field in data:
            lines.append(f"{field}: {_snapshot_member_summary(data[field])}")

    for field in (
        "feature_state_json",
        "family_frames_json",
        "payload_json",
        "stale_mask_json",
    ):
        if field in data:
            parsed = _parse_jsonish(data[field])
            lines.append(f"{field}: {_compact_json(parsed, raw_json_chars)}")

    used = set(interesting_order) | {
        "future_json",
        "selected_call_json",
        "selected_put_json",
        "ce_atm_json",
        "ce_atm1_json",
        "pe_atm_json",
        "pe_atm1_json",
        "feature_state_json",
        "family_frames_json",
        "payload_json",
        "stale_mask_json",
    }
    extras = [(k, v) for k, v in _sorted_items(data) if k not in used and not k.endswith("_json")]
    for key_name, value in extras[:20]:
        lines.append(f"{key_name}={_short(value, 120)}")
    if len(extras) > 20:
        lines.append(f"... {len(extras) - 20} more fields omitted")
    return lines


def _stream_entry_summary(entry_id: str, fields: Mapping[str, Any], raw_json_chars: int) -> str:
    pieces: list[str] = [f"id={entry_id}"]
    ts_ns = _mapping_ts_ns(fields)
    if ts_ns > 0:
        pieces.append(f"ts={_format_ns(ts_ns)}")
        pieces.append(f"age={_age_str(ts_ns)}")

    priority = (
        "service_name",
        "instance_id",
        "provider_id",
        "instrument_key",
        "instrument_token",
        "trading_symbol",
        "instrument_role",
        "status",
        "event_type",
        "error_type",
        "detail",
        "frame_id",
        "selection_version",
        "family_runtime_mode",
        "ltp",
        "bid",
        "ask",
        "bid_qty_5",
        "ask_qty_5",
        "validity",
    )
    for key in priority:
        if key in fields:
            pieces.append(f"{key}={_short(fields[key], 60)}")

    for json_key in ("payload_json", "future_json", "selected_call_json", "selected_put_json"):
        if json_key in fields:
            parsed = _parse_jsonish(fields[json_key])
            pieces.append(f"{json_key}={_compact_json(parsed, raw_json_chars)}")
            break

    return " | ".join(pieces)


class StreamTailer:
    def __init__(self, client: Any, streams: Sequence[str], *, tail_buffer: int, raw_json_chars: int) -> None:
        self.client = client
        self.streams = tuple(streams)
        self.raw_json_chars = raw_json_chars
        self.last_ids: dict[str, str] = {stream: "$" for stream in self.streams}
        self.buffer: deque[str] = deque(maxlen=max(10, tail_buffer))

    def poll(self, block_ms: int) -> None:
        if not self.streams:
            return
        try:
            raw = self.client.xread(self.last_ids, count=200, block=max(1, block_ms))
        except TypeError:
            try:
                raw = self.client.xread(streams=self.last_ids, count=200, block=max(1, block_ms))
            except Exception:
                return
        except Exception:
            return

        decoded = _decode(raw)
        if not decoded:
            return

        for stream_name, entries in decoded:
            stream_key = str(stream_name)
            for entry_id, fields in entries:
                entry_id_text = str(entry_id)
                if isinstance(fields, dict):
                    formatted = _stream_entry_summary(entry_id_text, fields, self.raw_json_chars)
                else:
                    formatted = f"id={entry_id_text} | {_short(fields, self.raw_json_chars)}"
                self.buffer.appendleft(f"{stream_key}: {formatted}")
                self.last_ids[stream_key] = entry_id_text

    def lines(self) -> list[str]:
        return list(self.buffer)


def _dashboard(client: Any, cfg: WatchConfig, tailer: StreamTailer | None) -> None:
    width = shutil.get_terminal_size((140, 40)).columns
    now_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"ScalpX MME live observer | now={now_text} | repo={REPO_ROOT} | width={width}")

    _print_section("LOCKS")
    print(_lock_summary(client, N.KEY_LOCK_FEEDS))
    if hasattr(N, "KEY_LOCK_STRATEGY"):
        print(_lock_summary(client, N.KEY_LOCK_STRATEGY))
    if hasattr(N, "KEY_LOCK_EXECUTION"):
        print(_lock_summary(client, N.KEY_LOCK_EXECUTION))

    _print_section("HEARTBEATS")
    heartbeat_keys = [
        N.KEY_HEALTH_FEEDS,
        N.KEY_HEALTH_FEATURES,
        getattr(N, "KEY_HEALTH_STRATEGY", ""),
        getattr(N, "KEY_HEALTH_RISK", ""),
        getattr(N, "KEY_HEALTH_EXECUTION", ""),
        getattr(N, "KEY_HEALTH_MONITOR", ""),
        getattr(N, "KEY_HEALTH_PROVIDER_RUNTIME", ""),
        getattr(N, "KEY_HEALTH_ZERODHA_MARKETDATA", ""),
        getattr(N, "KEY_HEALTH_ZERODHA_EXECUTION", ""),
        getattr(N, "KEY_HEALTH_DHAN_MARKETDATA", ""),
        getattr(N, "KEY_HEALTH_DHAN_EXECUTION", ""),
        getattr(N, "KEY_HEALTH_DHAN_AUTH", ""),
    ]
    seen_hb: set[str] = set()
    for key in heartbeat_keys:
        if key and key not in seen_hb:
            seen_hb.add(key)
            print(_heartbeat_summary(client, key))

    _print_section("SNAPSHOT HASHES (feeds.py outputs)")
    snapshot_keys = [
        N.HASH_STATE_SNAPSHOT_MME_FUT,
        N.HASH_STATE_SNAPSHOT_MME_OPT_SELECTED,
        getattr(N, "HASH_STATE_SNAPSHOT_MME_FUT_ACTIVE", ""),
        getattr(N, "HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ACTIVE", ""),
        getattr(N, "HASH_STATE_SNAPSHOT_MME_FUT_ZERODHA", ""),
        getattr(N, "HASH_STATE_SNAPSHOT_MME_FUT_DHAN", ""),
        getattr(N, "HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA", ""),
        getattr(N, "HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_DHAN", ""),
        getattr(N, "HASH_STATE_DHAN_CONTEXT", ""),
        getattr(N, "HASH_STATE_PROVIDER_RUNTIME", ""),
    ]
    seen_snap: set[str] = set()
    for key in snapshot_keys:
        if not key or key in seen_snap:
            continue
        seen_snap.add(key)
        data = _hgetall(client, key)
        print(f"\n[{key}]")
        if not data:
            print("MISSING")
            continue
        for line in _interesting_hash_lines(data, cfg.raw_json_chars):
            print(line)

    _print_section("FEATURE HASHES (features.py outputs)")
    feature_keys = [
        N.HASH_STATE_FEATURES_MME_FUT,
        N.HASH_STATE_BASELINES_MME_FUT,
        N.HASH_STATE_OPTION_CONFIRM,
    ]
    for key in feature_keys:
        data = _hgetall(client, key)
        print(f"\n[{key}]")
        if not data:
            print("MISSING")
            continue
        for line in _interesting_hash_lines(data, cfg.raw_json_chars):
            print(line)

    _print_section("LATEST STREAM ENTRIES (feeds/features/system)")
    stream_keys: list[str] = [
        N.STREAM_TICKS_MME_FUT,
        N.STREAM_TICKS_MME_OPT,
        N.STREAM_FEATURES_MME,
        N.STREAM_SYSTEM_HEALTH,
        N.STREAM_SYSTEM_ERRORS,
    ]
    if cfg.provider_streams:
        stream_keys.extend(
            [
                getattr(N, "STREAM_TICKS_MME_FUT_ZERODHA", ""),
                getattr(N, "STREAM_TICKS_MME_FUT_DHAN", ""),
                getattr(N, "STREAM_TICKS_MME_OPT_SELECTED_ZERODHA", ""),
                getattr(N, "STREAM_TICKS_MME_OPT_SELECTED_DHAN", ""),
                getattr(N, "STREAM_TICKS_MME_OPT_CONTEXT_DHAN", ""),
                getattr(N, "STREAM_PROVIDER_RUNTIME", ""),
            ]
        )
    seen_streams: set[str] = set()
    for key in stream_keys:
        if not key or key in seen_streams:
            continue
        seen_streams.add(key)
        print(f"\n[{key}]")
        entries = _xrevrange(client, key, cfg.stream_count)
        if not entries:
            print("no entries")
            continue
        for entry_id, fields in entries:
            print(_stream_entry_summary(entry_id, fields, cfg.raw_json_chars))

    _print_section("LAST SYSTEM ERRORS")
    for entry_id, fields in _xrevrange(client, N.STREAM_SYSTEM_ERRORS, cfg.error_count):
        print(_stream_entry_summary(entry_id, fields, cfg.raw_json_chars))

    if tailer is not None:
        _print_section("LIVE TAIL BUFFER (new entries only since observer start)")
        lines = tailer.lines()
        if not lines:
            print("no new events yet")
        else:
            for line in lines:
                print(line)


def _parse_args(argv: Sequence[str]) -> WatchConfig:
    parser = argparse.ArgumentParser(description="Freeze-safe live observer for MME feeds/features runtime")
    parser.add_argument("--poll-ms", type=int, default=1000)
    parser.add_argument("--stream-count", type=int, default=2)
    parser.add_argument("--error-count", type=int, default=8)
    parser.add_argument("--raw-json-chars", type=int, default=600)
    parser.add_argument("--tail-events", action="store_true")
    parser.add_argument("--tail-buffer", type=int, default=60)
    parser.add_argument("--no-provider-streams", action="store_true")
    parser.add_argument("--no-clear", action="store_true")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args(argv)
    return WatchConfig(
        poll_ms=max(100, args.poll_ms),
        stream_count=max(1, args.stream_count),
        error_count=max(1, args.error_count),
        raw_json_chars=max(120, args.raw_json_chars),
        tail_events=bool(args.tail_events),
        tail_buffer=max(10, args.tail_buffer),
        provider_streams=not bool(args.no_provider_streams),
        no_clear=bool(args.no_clear),
        once=bool(args.once),
    )


def main(argv: Sequence[str] | None = None) -> int:
    cfg = _parse_args(sys.argv[1:] if argv is None else argv)
    client = _build_redis_client()

    tailer: StreamTailer | None = None
    if cfg.tail_events:
        tail_streams = [
            N.STREAM_TICKS_MME_FUT,
            N.STREAM_TICKS_MME_OPT,
            N.STREAM_FEATURES_MME,
            N.STREAM_SYSTEM_ERRORS,
            N.STREAM_SYSTEM_HEALTH,
        ]
        if cfg.provider_streams:
            tail_streams.extend(
                [
                    getattr(N, "STREAM_TICKS_MME_FUT_ZERODHA", ""),
                    getattr(N, "STREAM_TICKS_MME_FUT_DHAN", ""),
                    getattr(N, "STREAM_TICKS_MME_OPT_SELECTED_ZERODHA", ""),
                    getattr(N, "STREAM_TICKS_MME_OPT_SELECTED_DHAN", ""),
                    getattr(N, "STREAM_TICKS_MME_OPT_CONTEXT_DHAN", ""),
                    getattr(N, "STREAM_PROVIDER_RUNTIME", ""),
                ]
            )
        tailer = StreamTailer(
            client,
            [stream for stream in tail_streams if stream],
            tail_buffer=cfg.tail_buffer,
            raw_json_chars=cfg.raw_json_chars,
        )

    try:
        while not STOP_REQUESTED:
            if tailer is not None:
                tailer.poll(block_ms=min(cfg.poll_ms, 400))
            _clear_screen(not cfg.no_clear)
            _dashboard(client, cfg, tailer)
            if cfg.once:
                break
            sleep_s = max(cfg.poll_ms / 1000.0, 0.10)
            end = time.monotonic() + sleep_s
            while time.monotonic() < end and not STOP_REQUESTED:
                time.sleep(0.05)
    finally:
        close = getattr(client, "close", None)
        if callable(close):
            try:
                close()
            except Exception:
                pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
