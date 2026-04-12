from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import redis


@dataclass(frozen=True)
class RedisTLSConfig:
    host_primary: str
    host_replica: str
    port: int
    cacert: str
    pw_file: str

    @staticmethod
    def from_env(prefix: str = "SCALPX_REDIS_") -> "RedisTLSConfig":
        hp = os.getenv(f"{prefix}HOST_PRIMARY", "redis-node1")
        hr = os.getenv(f"{prefix}HOST_REPLICA", "redis-node2")
        port_s = os.getenv(f"{prefix}PORT", "6380")
        cacert = os.getenv(f"{prefix}CACERT", "/etc/scalpx/redis/certs/ca_bundle.pem")
        pw_file = os.getenv(f"{prefix}PW_FILE", "/etc/scalpx/redis/pw.txt")

        try:
            port = int(port_s)
        except ValueError as e:
            raise ValueError(f"Invalid Redis port: {port_s!r}") from e

        return RedisTLSConfig(
            host_primary=hp,
            host_replica=hr,
            port=port,
            cacert=cacert,
            pw_file=pw_file,
        )

    def read_password(self) -> str:
        with open(self.pw_file, "r", encoding="utf-8") as f:
            return f.read().strip()


def make_redis_client(
    cfg: Optional[RedisTLSConfig] = None,
    *,
    role: str = "primary",
    decode_responses: bool = False,
    socket_timeout: float = 2.0,
) -> redis.Redis:
    cfg = cfg or RedisTLSConfig.from_env()
    host = cfg.host_primary if role.lower() == "primary" else cfg.host_replica
    password = cfg.read_password()

    return redis.Redis(
        host=host,
        port=cfg.port,
        password=password,
        ssl=True,
        ssl_ca_certs=cfg.cacert,
        ssl_cert_reqs="required",
        ssl_check_hostname=True,
        decode_responses=decode_responses,
        socket_timeout=socket_timeout,
        socket_connect_timeout=socket_timeout,
        retry_on_timeout=True,
        health_check_interval=10,
    )


def ping_both() -> tuple[bool, bool]:
    cfg = RedisTLSConfig.from_env()
    r1 = make_redis_client(cfg, role="primary")
    r2 = make_redis_client(cfg, role="replica")
    return bool(r1.ping()), bool(r2.ping())
