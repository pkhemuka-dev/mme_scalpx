#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import pathlib
import shutil
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path("/home/Lenovo/scalpx/projects/mme_scalpx").resolve()

SHARED_TOKEN = pathlib.Path(
    os.environ.get(
        "SCALPX_SHARED_TOKEN_FILE",
        "/home/Lenovo/scalpx/common/secrets/shared/tokens.json",
    )
)

ZERODHA_SESSION = pathlib.Path(
    os.environ.get(
        "SCALPX_ZERODHA_SESSION_ENV",
        str(ROOT / "common/secrets/brokers/zerodha/session.env"),
    )
)

BACKUP_DIR = ROOT / "run" / "_token_backups"


def read_env_value(path: pathlib.Path, key: str) -> str:
    if not path.exists():
        raise SystemExit(f"MISSING_ENV_FILE: {path}")

    value = ""
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        if k.strip() == key:
            value = v.strip().strip('"').strip("'")
    return value


def main() -> int:
    zerodha_access_token = read_env_value(ZERODHA_SESSION, "ZERODHA_ACCESS_TOKEN")
    zerodha_api_key = read_env_value(ZERODHA_SESSION, "ZERODHA_API_KEY")
    zerodha_user_id = read_env_value(ZERODHA_SESSION, "ZERODHA_USER_ID")

    if not zerodha_access_token:
        raise SystemExit("ZERODHA_ACCESS_TOKEN missing in Zerodha session.env")

    SHARED_TOKEN.parent.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).isoformat()

    data: dict[str, object] = {}
    if SHARED_TOKEN.exists():
        try:
            data = json.loads(SHARED_TOKEN.read_text())
        except Exception:
            data = {}

        backup = BACKUP_DIR / f"tokens.before_ensure_zerodha_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        shutil.copy2(SHARED_TOKEN, backup)
        os.chmod(backup, 0o600)

    before_broker = data.get("broker")
    changed = False

    if data.get("broker") != "zerodha":
        data["broker"] = "zerodha"
        changed = True

    if data.get("access_token") != zerodha_access_token:
        data["access_token"] = zerodha_access_token
        changed = True

    if zerodha_api_key and not data.get("api_key"):
        data["api_key"] = zerodha_api_key
        changed = True

    if zerodha_user_id and not data.get("user_id"):
        data["user_id"] = zerodha_user_id
        changed = True

    data["updated_at"] = now
    data["login_time_utc"] = data.get("login_time_utc") or now

    SHARED_TOKEN.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    os.chmod(SHARED_TOKEN, 0o600)

    print("ensure_zerodha_shared_token=PASS")
    print("shared_token_file=", SHARED_TOKEN)
    print("before_broker=", before_broker)
    print("after_broker=", data.get("broker"))
    print("access_token=", "<present>" if data.get("access_token") else "missing")
    print("api_key=", "<present>" if data.get("api_key") else "missing")
    print("changed=", changed)

    if data.get("broker") != "zerodha":
        raise SystemExit("FAILED: shared token broker is not zerodha after repair")
    if not data.get("access_token"):
        raise SystemExit("FAILED: shared token access_token missing after repair")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
