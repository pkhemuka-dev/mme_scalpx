#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys

def rc(*cmd: str) -> str:
    return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT).strip()

def info(section: str) -> dict[str, str]:
    out = rc("redis-cli", "-h", "127.0.0.1", "-p", "6379", "INFO", section)
    d = {}
    for line in out.splitlines():
        if ":" in line and not line.startswith("#"):
            k, v = line.split(":", 1)
            d[k] = v.strip()
    return d

def main() -> int:
    try:
        ping = rc("redis-cli", "-h", "127.0.0.1", "-p", "6379", "PING")
    except Exception as e:
        print("predischeck=FAIL")
        print("reason=redis_ping_failed")
        print("detail=", str(e))
        return 1

    if ping != "PONG":
        print("predischeck=FAIL")
        print("reason=redis_ping_not_pong")
        print("ping=", ping)
        return 1

    persistence = info("persistence")
    memory = info("memory")
    clients = info("clients")

    loading = persistence.get("loading")
    bgsave = persistence.get("rdb_bgsave_in_progress")
    aof_rewrite = persistence.get("aof_rewrite_in_progress")
    used = memory.get("used_memory", "0")
    maxmem = memory.get("maxmemory", "0")
    blocked = clients.get("blocked_clients", "0")

    print("redis_ping=PONG")
    print("loading=", loading)
    print("rdb_bgsave_in_progress=", bgsave)
    print("aof_rewrite_in_progress=", aof_rewrite)
    print("used_memory=", used)
    print("maxmemory=", maxmem)
    print("blocked_clients=", blocked)

    if loading != "0":
        print("predischeck=FAIL")
        print("reason=redis_loading_dataset")
        return 1

    if blocked != "0":
        print("predischeck=FAIL")
        print("reason=blocked_clients_present")
        return 1

    try:
        used_i = int(used)
        max_i = int(maxmem)
        if max_i > 0 and used_i / max_i > 0.85:
            print("predischeck=FAIL")
            print("reason=redis_memory_above_85_percent")
            return 1
    except Exception:
        pass

    print("predischeck=PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
