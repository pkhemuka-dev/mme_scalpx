from __future__ import annotations

import csv
import gzip
import json
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
BASE = Path("/home/Lenovo/scalpx/projects/mme_scalpx/run/session_exports")

def sh(*args: str) -> str:
    return subprocess.check_output(list(args), text=True)

def stream_to_rows(stream_key: str) -> list[dict]:
    raw = sh("redis-cli", "--raw", "XRANGE", stream_key, "-", "+")
    lines = raw.splitlines()
    rows = []
    i = 0
    n = len(lines)
    while i < n:
        entry_id = lines[i].strip()
        if not entry_id:
            i += 1
            continue
        i += 1
        row = {"stream_id": entry_id}
        while i + 1 < n:
            k = lines[i].strip()
            v = lines[i + 1]
            if "-" in k and k.replace("-", "").isdigit():
                break
            row[k] = v
            i += 2
        rows.append(row)
    return rows

def hgetall(key: str) -> dict[str, str]:
    raw = sh("redis-cli", "--raw", "HGETALL", key)
    lines = raw.splitlines()
    out: dict[str, str] = {}
    for i in range(0, len(lines), 2):
        if i + 1 < len(lines):
            out[lines[i]] = lines[i + 1]
    return out

def xlen(key: str) -> int:
    return int(sh("redis-cli", "--raw", "XLEN", key).strip() or "0")

def now_ist() -> datetime:
    return datetime.now(tz=IST)

def ns_to_ist(ns_text: str | None) -> str | None:
    if not ns_text:
        return None
    try:
        ns = int(ns_text)
    except Exception:
        return None
    return datetime.fromtimestamp(ns / 1_000_000_000, tz=ZoneInfo("UTC")).astimezone(IST).isoformat()

def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys = []
    seen = set()
    for r in rows:
        for k in r.keys():
            if k not in seen:
                seen.add(k)
                keys.append(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)

def main() -> int:
    day = now_ist().strftime("%Y-%m-%d")
    outdir = BASE / day
    outdir.mkdir(parents=True, exist_ok=True)

    fut_rows = stream_to_rows("ticks:mme:fut:stream")
    opt_rows = stream_to_rows("ticks:mme:opt:stream")

    write_csv(outdir / "ticks_mme_fut_stream.csv", fut_rows)
    write_csv(outdir / "ticks_mme_opt_stream.csv", opt_rows)

    (outdir / "state_snapshot_mme_fut.json").write_text(
        json.dumps(hgetall("state:snapshot:mme:fut"), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (outdir / "state_snapshot_mme_opt_selected.json").write_text(
        json.dumps(hgetall("state:snapshot:mme:opt:selected"), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (outdir / "state_runtime.json").write_text(
        json.dumps(hgetall("state:runtime"), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (outdir / "health_feeds.json").write_text(
        json.dumps(hgetall("health:feeds"), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (outdir / "health_features.json").write_text(
        json.dumps(hgetall("health:features"), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    first_fut = fut_rows[0] if fut_rows else {}
    last_fut = fut_rows[-1] if fut_rows else {}
    first_opt = opt_rows[0] if opt_rows else {}
    last_opt = opt_rows[-1] if opt_rows else {}

    manifest = {
        "session_date_ist": day,
        "exported_at_ist": now_ist().isoformat(),
        "fut_tick_count": xlen("ticks:mme:fut:stream"),
        "opt_tick_count": xlen("ticks:mme:opt:stream"),
        "first_fut_stream_id": first_fut.get("stream_id"),
        "first_fut_exchange_time_ist": ns_to_ist(first_fut.get("ts_exchange_ns") or first_fut.get("ts_event_ns") or first_fut.get("ts_recv_ns")),
        "last_fut_stream_id": last_fut.get("stream_id"),
        "last_fut_exchange_time_ist": ns_to_ist(last_fut.get("ts_exchange_ns") or last_fut.get("ts_event_ns") or last_fut.get("ts_recv_ns")),
        "first_opt_stream_id": first_opt.get("stream_id"),
        "first_opt_exchange_time_ist": ns_to_ist(first_opt.get("ts_exchange_ns") or first_opt.get("ts_event_ns") or first_opt.get("ts_recv_ns")),
        "last_opt_stream_id": last_opt.get("stream_id"),
        "last_opt_exchange_time_ist": ns_to_ist(last_opt.get("ts_exchange_ns") or last_opt.get("ts_event_ns") or last_opt.get("ts_recv_ns")),
        "runtime_selection_version": hgetall("state:runtime").get("feeds_selection_version"),
        "health_feeds_status": hgetall("health:feeds").get("status"),
        "health_features_status": hgetall("health:features").get("status"),
    }
    (outdir / "session_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    tar_path = BASE / f"{day}.tar.gz"
    subprocess.check_call(
        ["tar", "-czf", str(tar_path), "-C", str(BASE), day]
    )

    print(f"EXPORT_OK {outdir}")
    print(f"ARCHIVE_OK {tar_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
