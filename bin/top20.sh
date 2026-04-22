#!/usr/bin/env bash
set -euo pipefail

ROOT="${HOME}/scalpx/projects/mme_scalpx"

# Auto-load Dhan broker secrets/session if present.
for f in \
  "$ROOT/common/secrets/brokers/dhan/credentials.env" \
  "$ROOT/common/secrets/brokers/dhan/session.env" \
  "$ROOT/common/secrets/brokers/dhan/runtime.env" \
  "$ROOT/common/secrets/brokers/dhan/.env" \
  "$ROOT/etc/brokers/dhan.env"
do
  if [ -f "$f" ]; then
    set -a
    . "$f"
    set +a
  fi
done

export DHAN_CLIENT_ID="${DHAN_CLIENT_ID:-${MME_DHAN_CLIENT_ID:-}}"
export DHAN_ACCESS_TOKEN="${DHAN_ACCESS_TOKEN:-${MME_DHAN_ACCESS_TOKEN:-}}"

FUT_ID="${1:-${TOP20_FUT_ID:-}}"
OPT_ID="${2:-${TOP20_OPT_ID:-}}"
SEGMENT="${TOP20_SEGMENT:-NSE_FNO}"
TIMEOUT_SEC="${TOP20_TIMEOUT_SEC:-20}"

if [ -z "${DHAN_CLIENT_ID:-}" ]; then
  echo "missing DHAN_CLIENT_ID" >&2
  exit 1
fi

if [ -z "${DHAN_ACCESS_TOKEN:-}" ]; then
  echo "missing DHAN_ACCESS_TOKEN" >&2
  exit 1
fi

if [ -z "${FUT_ID}" ] || [ -z "${OPT_ID}" ]; then
  echo "usage: top20 <FUT_SECURITY_ID> <OPT_SECURITY_ID>" >&2
  echo "or export TOP20_FUT_ID / TOP20_OPT_ID and run: top20" >&2
  exit 1
fi

"$ROOT/.venv/bin/python" - "$FUT_ID" "$OPT_ID" "$SEGMENT" "$TIMEOUT_SEC" <<'PY'
import json
import struct
import sys
import time
from urllib.parse import quote

try:
    import websocket
except Exception as exc:
    raise SystemExit(
        "python package 'websocket-client' is required. "
        "Install with: .venv/bin/pip install websocket-client"
    ) from exc

import os

fut_id = str(sys.argv[1]).strip()
opt_id = str(sys.argv[2]).strip()
segment = str(sys.argv[3]).strip()
timeout_sec = int(sys.argv[4])

client_id = os.environ["DHAN_CLIENT_ID"].strip()
token = os.environ["DHAN_ACCESS_TOKEN"].strip()

url = (
    "wss://depth-api-feed.dhan.co/twentydepth"
    f"?token={quote(token)}&clientId={quote(client_id)}&authType=2"
)

subscribe_msg = {
    "RequestCode": 23,
    "InstrumentCount": 2,
    "InstrumentList": [
        {"ExchangeSegment": segment, "SecurityId": fut_id},
        {"ExchangeSegment": segment, "SecurityId": opt_id},
    ],
}

def parse_packets(blob: bytes):
    packets = []
    off = 0
    total = len(blob)

    while off + 12 <= total:
        msg_len = int.from_bytes(blob[off:off+2], "little", signed=False)

        if msg_len < 12 or off + msg_len > total:
            # Fallback for stacked fixed-size 20-depth packets if length field is unusable.
            if off + 332 <= total:
                msg_len = 332
            else:
                break

        pkt = blob[off:off+msg_len]
        off += msg_len

        response_code = pkt[2]
        security_id = str(int.from_bytes(pkt[4:8], "little", signed=False))

        if response_code not in (41, 51):
            continue

        side = "bid" if response_code == 41 else "ask"
        levels = []
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

state = {
    fut_id: {"bid": None, "ask": None},
    opt_id: {"bid": None, "ask": None},
}

def print_side(label: str, side: str, levels):
    print()
    print(f"{label} | {side.upper()} | levels={len(levels)}")
    print("-" * 44)
    print(f"{'#':>2} {'price':>12} {'qty':>12} {'orders':>10}")
    print("-" * 44)
    for i, row in enumerate(levels, start=1):
        print(f"{i:>2} {row['price']:>12} {row['qty']:>12} {row['orders']:>10}")

ws = websocket.create_connection(url, timeout=timeout_sec)
ws.send(json.dumps(subscribe_msg))

deadline = time.time() + timeout_sec
try:
    while time.time() < deadline:
        msg = ws.recv()
        if isinstance(msg, str):
            continue

        for pkt in parse_packets(msg):
            sid = pkt["security_id"]
            side = pkt["side"]
            if sid in state:
                state[sid][side] = pkt["levels"]

        if all(state[s]["bid"] is not None and state[s]["ask"] is not None for s in state):
            break
finally:
    try:
        ws.send(json.dumps({"RequestCode": 12}))
    except Exception:
        pass
    try:
        ws.close()
    except Exception:
        pass

missing = []
for sid in (fut_id, opt_id):
    for side in ("bid", "ask"):
        if state[sid][side] is None:
            missing.append(f"{sid}:{side}")

if missing:
    print("incomplete top20 snapshot; missing:", ", ".join(missing), file=sys.stderr)
    print("partial_state=", json.dumps(state, indent=2), file=sys.stderr)
    raise SystemExit(2)

print_side(f"FUT {fut_id}", "bid", state[fut_id]["bid"])
print_side(f"FUT {fut_id}", "ask", state[fut_id]["ask"])
print_side(f"OPT {opt_id}", "bid", state[opt_id]["bid"])
print_side(f"OPT {opt_id}", "ask", state[opt_id]["ask"])
PY
