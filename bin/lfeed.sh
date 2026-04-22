#!/usr/bin/env bash
set -euo pipefail

ROOT="$HOME/scalpx/projects/mme_scalpx"

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

MODE="${1:-full}"
SEGMENT="${2:-NSE_FNO}"
shift 2 || true

if [ -z "${DHAN_CLIENT_ID:-}" ]; then
  echo "missing DHAN_CLIENT_ID" >&2
  exit 1
fi

if [ -z "${DHAN_ACCESS_TOKEN:-}" ]; then
  echo "missing DHAN_ACCESS_TOKEN" >&2
  exit 1
fi

if [ "$#" -eq 0 ]; then
  echo "usage: lfeed <ticker|quote|full> <SEGMENT> <SECURITY_ID> [SECURITY_ID ...]" >&2
  echo "example: lfeed full NSE_FNO 49081 49082" >&2
  exit 1
fi

"$ROOT/.venv/bin/python" - "$MODE" "$SEGMENT" "$@" <<'PY'
import json
import os
import struct
import sys
from urllib.parse import quote

try:
    import websocket
except Exception as exc:
    raise SystemExit(
        "python package 'websocket-client' is required. "
        "Install with: .venv/bin/pip install websocket-client"
    ) from exc

mode = sys.argv[1].strip().lower()
segment = sys.argv[2].strip()
security_ids = [str(x).strip() for x in sys.argv[3:]]

request_codes = {
    "ticker": 15,
    "quote": 17,
    "full": 21,
}
if mode not in request_codes:
    raise SystemExit("mode must be one of: ticker, quote, full")

token = os.environ["DHAN_ACCESS_TOKEN"].strip()
client_id = os.environ["DHAN_CLIENT_ID"].strip()

url = (
    "wss://api-feed.dhan.co"
    f"?version=2&token={quote(token)}&clientId={quote(client_id)}&authType=2"
)

subscribe_msg = {
    "RequestCode": request_codes[mode],
    "InstrumentCount": len(security_ids),
    "InstrumentList": [
        {"ExchangeSegment": segment, "SecurityId": sid}
        for sid in security_ids
    ],
}

segment_enum = {
    0: "IDX_I",
    1: "NSE_EQ",
    2: "NSE_FNO",
    3: "NSE_CURRENCY",
    4: "BSE_EQ",
    5: "MCX_COMM",
    7: "BSE_CURRENCY",
    8: "BSE_FNO",
}

def f32(buf, off):
    return struct.unpack_from("<f", buf, off)[0]

def i16(buf, off):
    return struct.unpack_from("<h", buf, off)[0]

def u16(buf, off):
    return struct.unpack_from("<H", buf, off)[0]

def i32(buf, off):
    return struct.unpack_from("<i", buf, off)[0]

def header(pkt):
    code = pkt[0]
    msg_len = u16(pkt, 1)
    seg = pkt[3]
    security_id = str(int.from_bytes(pkt[4:8], "little", signed=False))
    return code, msg_len, seg, security_id

def parse_ticker(pkt):
    code, msg_len, seg, security_id = header(pkt)
    return {
        "response_code": code,
        "response_type": "ticker",
        "segment": segment_enum.get(seg, str(seg)),
        "security_id": security_id,
        "ltp": f32(pkt, 8),
        "ltt_epoch": i32(pkt, 12),
    }

def parse_quote(pkt):
    code, msg_len, seg, security_id = header(pkt)
    return {
        "response_code": code,
        "response_type": "quote",
        "segment": segment_enum.get(seg, str(seg)),
        "security_id": security_id,
        "ltp": f32(pkt, 8),
        "ltq": i16(pkt, 12),
        "ltt_epoch": i32(pkt, 14),
        "atp": f32(pkt, 18),
        "volume": i32(pkt, 22),
        "total_sell_qty": i32(pkt, 26),
        "total_buy_qty": i32(pkt, 30),
        "day_open": f32(pkt, 34),
        "day_close": f32(pkt, 38),
        "day_high": f32(pkt, 42),
        "day_low": f32(pkt, 46),
    }

def parse_oi(pkt):
    code, msg_len, seg, security_id = header(pkt)
    return {
        "response_code": code,
        "response_type": "oi",
        "segment": segment_enum.get(seg, str(seg)),
        "security_id": security_id,
        "oi": i32(pkt, 8),
    }

def parse_prev_close(pkt):
    code, msg_len, seg, security_id = header(pkt)
    return {
        "response_code": code,
        "response_type": "prev_close",
        "segment": segment_enum.get(seg, str(seg)),
        "security_id": security_id,
        "prev_close": f32(pkt, 8),
        "prev_oi": i32(pkt, 12),
    }

def parse_full(pkt):
    code, msg_len, seg, security_id = header(pkt)
    out = {
        "response_code": code,
        "response_type": "full",
        "segment": segment_enum.get(seg, str(seg)),
        "security_id": security_id,
        "ltp": f32(pkt, 8),
        "ltq": i16(pkt, 12),
        "ltt_epoch": i32(pkt, 14),
        "atp": f32(pkt, 18),
        "volume": i32(pkt, 22),
        "total_sell_qty": i32(pkt, 26),
        "total_buy_qty": i32(pkt, 30),
        "oi": i32(pkt, 34),
        "day_high_oi": i32(pkt, 38),
        "day_low_oi": i32(pkt, 42),
        "day_open": f32(pkt, 46),
        "day_close": f32(pkt, 50),
        "day_high": f32(pkt, 54),
        "day_low": f32(pkt, 58),
        "depth5": [],
    }
    pos = 62
    for _ in range(5):
        if pos + 20 > len(pkt):
            break
        row = {
            "bid_qty": i32(pkt, pos),
            "ask_qty": i32(pkt, pos + 4),
            "bid_orders": i16(pkt, pos + 8),
            "ask_orders": i16(pkt, pos + 10),
            "bid_price": f32(pkt, pos + 12),
            "ask_price": f32(pkt, pos + 16),
        }
        out["depth5"].append(row)
        pos += 20
    return out

def parse_packet(pkt):
    if len(pkt) < 8:
        return None
    code = pkt[0]
    if code == 2:
        return parse_ticker(pkt)
    if code == 4:
        return parse_quote(pkt)
    if code == 5:
        return parse_oi(pkt)
    if code == 6:
        return parse_prev_close(pkt)
    if code == 8:
        return parse_full(pkt)
    if code == 50:
        reason = u16(pkt, 8) if len(pkt) >= 10 else None
        return {
            "response_code": 50,
            "response_type": "disconnect",
            "reason_code": reason,
        }
    return {
        "response_code": code,
        "response_type": "unknown",
        "raw_len": len(pkt),
    }

def split_packets(blob):
    packets = []
    off = 0
    total = len(blob)
    while off + 8 <= total:
        msg_len = u16(blob, off + 1)
        if msg_len < 8 or off + msg_len > total:
            break
        packets.append(blob[off:off + msg_len])
        off += msg_len
    return packets

ws = websocket.create_connection(url, timeout=30)
ws.send(json.dumps(subscribe_msg))
print(json.dumps({"subscribed": subscribe_msg}, separators=(",", ":")))

try:
    while True:
        msg = ws.recv()
        if isinstance(msg, str):
            print(json.dumps({"text": msg}, separators=(",", ":")))
            continue
        for pkt in split_packets(msg):
            parsed = parse_packet(pkt)
            if parsed is not None:
                print(json.dumps(parsed, separators=(",", ":")), flush=True)
finally:
    try:
        ws.send(json.dumps({"RequestCode": 12}))
    except Exception:
        pass
    try:
        ws.close()
    except Exception:
        pass
PY
