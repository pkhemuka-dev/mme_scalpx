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

SEGMENT="${1:-NSE_FNO}"
shift || true

if [ -z "${DHAN_CLIENT_ID:-}" ]; then
  echo "missing DHAN_CLIENT_ID" >&2
  exit 1
fi

if [ -z "${DHAN_ACCESS_TOKEN:-}" ]; then
  echo "missing DHAN_ACCESS_TOKEN" >&2
  exit 1
fi

if [ "$#" -eq 0 ]; then
  echo "usage: mfeed <SEGMENT> <SECURITY_ID> [SECURITY_ID ...]" >&2
  echo "example: mfeed NSE_FNO 49081 123456" >&2
  exit 1
fi

"$ROOT/.venv/bin/python" - "$SEGMENT" "$@" <<'PY'
import json
import sys
import requests
import os

segment = sys.argv[1]
security_ids = [int(x) for x in sys.argv[2:]]

url = "https://api.dhan.co/v2/marketfeed/quote"
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "access-token": os.environ["DHAN_ACCESS_TOKEN"],
    "client-id": os.environ["DHAN_CLIENT_ID"],
}
payload = {segment: security_ids}

resp = requests.post(url, headers=headers, json=payload, timeout=20)
text = resp.text.strip()
try:
    body = resp.json() if text else {}
except Exception:
    body = {"raw_text": text}

print(json.dumps(body, indent=2))

if resp.status_code >= 400:
    raise SystemExit(1)
PY
