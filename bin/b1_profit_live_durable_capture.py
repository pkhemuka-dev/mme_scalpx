#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import json
import os
import pathlib
import signal
import sys
import time
from datetime import datetime, timezone
from typing import Any

from app.mme_scalpx.core.redisx import get_redis_client

DEFAULT_STREAMS = {
    "fut_zerodha": "ticks:mme:fut:zerodha:stream",
    "opt_selected_zerodha": "ticks:mme:opt:selected:zerodha:stream",
    "features": "features:mme:stream",
    "decisions": "decisions:mme:stream",
    "health": "system:health:stream",
    "errors": "system:errors:stream",
    "provider_runtime": "provider:runtime:stream",
}

STOP = False


def _stop(*_: object) -> None:
    global STOP
    STOP = True


signal.signal(signal.SIGTERM, _stop)
signal.signal(signal.SIGINT, _stop)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def clean(v: Any) -> Any:
    if isinstance(v, bytes):
        return v.decode("utf-8", errors="replace")
    if isinstance(v, dict):
        return {clean(k): clean(x) for k, x in v.items()}
    if isinstance(v, list):
        return [clean(x) for x in v]
    return v


def atomic_write_json(path: pathlib.Path, data: dict[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def safe_xlen(r: Any, stream: str) -> int:
    try:
        return int(r.xlen(stream))
    except Exception:
        return -1


def safe_status(r: Any) -> dict[str, Any]:
    def xl(stream: str) -> int:
        try:
            return int(r.xlen(stream))
        except Exception:
            return -1

    return {
        "orders_xlen": xl("orders:mme:stream"),
        "risk_xlen": xl("risk:mme:stream"),
        "execution_xlen": xl("execution:mme:stream"),
    }


def open_files(outdir: pathlib.Path, streams: dict[str, str]) -> dict[str, Any]:
    files: dict[str, Any] = {}
    for label in streams:
        files[label] = gzip.open(outdir / f"{label}.jsonl.gz", "at", encoding="utf-8")
    return files


def close_files(files: dict[str, Any]) -> None:
    for f in files.values():
        try:
            f.flush()
            f.close()
        except Exception:
            pass


def write_row(files: dict[str, Any], label: str, stream: str, msg_id: str, fields: dict[str, Any]) -> None:
    files[label].write(json.dumps(
        {
            "stream": stream,
            "id": msg_id,
            "fields": clean(fields),
        },
        sort_keys=True,
        separators=(",", ":"),
    ) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MME-ScalpX read-only durable Redis stream capture recorder.")
    parser.add_argument("--outdir", required=False, help="Output directory under run/live_capture.")
    parser.add_argument("--block-ms", type=int, default=1000)
    parser.add_argument("--count", type=int, default=500)
    parser.add_argument("--heartbeat-sec", type=float, default=5.0)
    parser.add_argument("--flush-sec", type=float, default=2.0)
    parser.add_argument("--duration-sec", type=int, default=0, help="0 means run until SIGTERM.")
    parser.add_argument("--no-backfill", action="store_true", help="Start from current latest IDs, do not write retained rows.")
    parser.add_argument("--self-test", action="store_true", help="Print config and exit without Redis access.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.self_test:
        print(json.dumps({
            "self_test": True,
            "default_streams": DEFAULT_STREAMS,
            "read_only": True,
            "redis_delete_attempted": False,
            "order_attempted": False,
        }, indent=2, sort_keys=True))
        return 0

    if not args.outdir:
        print("--outdir is required unless --self-test is used", file=sys.stderr)
        return 2

    outdir = pathlib.Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    r = get_redis_client()
    streams = dict(DEFAULT_STREAMS)

    files = open_files(outdir, streams)
    counts = {label: 0 for label in streams}
    last_ids = {stream: "0-0" for stream in streams.values()}

    start_time = time.time()
    last_heartbeat = 0.0
    last_flush = 0.0

    start_manifest = {
        "service": "b1_profit_live_durable_capture",
        "started_at_utc": utc_now(),
        "pid": os.getpid(),
        "outdir": str(outdir),
        "streams": streams,
        "read_only": True,
        "source_patch_applied": False,
        "service_start_attempted": False,
        "service_stop_attempted": False,
        "process_kill_attempted": False,
        "redis_delete_attempted": False,
        "risk_start_attempted": False,
        "execution_start_attempted": False,
        "order_attempted": False,
        "args": vars(args),
    }
    atomic_write_json(outdir / "manifest_start.json", start_manifest)

    try:
        if args.no_backfill:
            for label, stream in streams.items():
                rows = r.xrevrange(stream, "+", "-", count=1)
                if rows:
                    last_ids[stream] = clean(rows[0][0])
                else:
                    last_ids[stream] = "0-0"
        else:
            for label, stream in streams.items():
                rows = r.xrange(stream, "-", "+")
                last = "0-0"
                for msg_id, fields in rows:
                    mid = clean(msg_id)
                    write_row(files, label, stream, mid, fields)
                    counts[label] += 1
                    last = mid
                last_ids[stream] = last
            for f in files.values():
                f.flush()

        while not STOP:
            if args.duration_sec and time.time() - start_time >= args.duration_sec:
                break

            try:
                resp = r.xread(last_ids, block=args.block_ms, count=args.count)
                for stream_name, rows in resp or []:
                    stream = clean(stream_name)
                    label = next((k for k, v in streams.items() if v == stream), stream.replace(":", "_"))
                    if label not in files:
                        files[label] = gzip.open(outdir / f"{label}.jsonl.gz", "at", encoding="utf-8")
                        counts[label] = 0

                    for msg_id, fields in rows:
                        mid = clean(msg_id)
                        write_row(files, label, stream, mid, fields)
                        counts[label] += 1
                        last_ids[stream] = mid
            except Exception as exc:
                with (outdir / "recorder_errors.log").open("a", encoding="utf-8") as ef:
                    ef.write(f"{utc_now()} {type(exc).__name__}: {exc}\n")
                time.sleep(1)

            now = time.time()

            if now - last_flush >= args.flush_sec:
                for f in files.values():
                    try:
                        f.flush()
                    except Exception:
                        pass
                last_flush = now

            if now - last_heartbeat >= args.heartbeat_sec:
                heartbeat = {
                    "service": "b1_profit_live_durable_capture",
                    "heartbeat_at_utc": utc_now(),
                    "pid": os.getpid(),
                    "running": True,
                    "outdir": str(outdir),
                    "counts": counts,
                    "last_ids": last_ids,
                    "redis_xlens": {label: safe_xlen(r, stream) for label, stream in streams.items()},
                    "safety": safe_status(r),
                    "read_only": True,
                }
                atomic_write_json(outdir / "heartbeat.json", heartbeat)
                atomic_write_json(outdir / "state.json", {
                    "updated_at_utc": utc_now(),
                    "counts": counts,
                    "last_ids": last_ids,
                    "safety": safe_status(r),
                })
                last_heartbeat = now

    finally:
        close_files(files)
        stop_manifest = {
            "service": "b1_profit_live_durable_capture",
            "stopped_at_utc": utc_now(),
            "pid": os.getpid(),
            "outdir": str(outdir),
            "counts": counts,
            "last_ids": last_ids,
            "safety": safe_status(r),
            "read_only": True,
        }
        atomic_write_json(outdir / "manifest_stop.json", stop_manifest)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
