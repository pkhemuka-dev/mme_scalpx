#!/usr/bin/env bash
set -euo pipefail
source "$HOME/scalpx/common/etc/redis.env"
export REDISCLI_AUTH="$(cat "$SCALPX_REDIS_PW_FILE")"
HOST="${1:-$SCALPX_REDIS_HOST_PRIMARY}"
shift || true
exec redis-cli --tls -h "$HOST" -p "$SCALPX_REDIS_PORT" --cacert "$SCALPX_REDIS_CACERT" "$@"
