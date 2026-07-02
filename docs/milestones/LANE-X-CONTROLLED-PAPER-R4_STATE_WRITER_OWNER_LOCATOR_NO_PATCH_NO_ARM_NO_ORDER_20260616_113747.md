# LANE-X-CONTROLLED-PAPER-R4_STATE_WRITER_OWNER_LOCATOR_NO_PATCH_NO_ARM_NO_ORDER_20260616_113747

## Proof

```json
{
  "classification": "PASS_CONTROLLED_PAPER_R4_SOURCE_WRITERS_EXIST_RUNTIME_PUBLICATION_MISSING_NO_ARM_NO_ORDER",
  "danger_env_absent": true,
  "execution_process_visible": false,
  "git_dirty_lines": 842,
  "helper_found": {
    "paper_status": false,
    "pstatus": false
  },
  "next_step": "If source writers exist but runtime publication is missing, prepare an after-market patch/harness to publish a fail-closed paper gate/status snapshot. Do not arm paper from this audit.",
  "no_execution_start": true,
  "no_order": true,
  "no_paper_armed": true,
  "no_redis_delete": true,
  "no_risk_start": true,
  "no_source_patch": true,
  "observe_env_ok": true,
  "paper_process_visible": false,
  "process_file": "run/audits/LANE-X-CONTROLLED-PAPER-R4_STATE_WRITER_OWNER_LOCATOR_NO_PATCH_NO_ARM_NO_ORDER_20260616_113747_processes.txt",
  "process_present": true,
  "redis_file": "run/audits/LANE-X-CONTROLLED-PAPER-R4_STATE_WRITER_OWNER_LOCATOR_NO_PATCH_NO_ARM_NO_ORDER_20260616_113747_redis_keys.txt",
  "redis_has_execution": true,
  "redis_has_paper_gate": false,
  "redis_has_position": false,
  "redis_has_risk": false,
  "risk_process_visible": false,
  "source_has_execution_writer": true,
  "source_has_paper_gate_logic": true,
  "source_has_position_writer": true,
  "source_has_redis_write_clues": true,
  "source_has_risk_writer": true,
  "source_lines": "run/audits/LANE-X-CONTROLLED-PAPER-R4_STATE_WRITER_OWNER_LOCATOR_NO_PATCH_NO_ARM_NO_ORDER_20260616_113747_source_writer_lines.txt",
  "status_file": "run/audits/LANE-X-CONTROLLED-PAPER-R4_STATE_WRITER_OWNER_LOCATOR_NO_PATCH_NO_ARM_NO_ORDER_20260616_113747_status.txt",
  "tag": "LANE-X-CONTROLLED-PAPER-R4_STATE_WRITER_OWNER_LOCATOR_NO_PATCH_NO_ARM_NO_ORDER_20260616_113747",
  "writers_file": "run/audits/LANE-X-CONTROLLED-PAPER-R4_STATE_WRITER_OWNER_LOCATOR_NO_PATCH_NO_ARM_NO_ORDER_20260616_113747_writer_owner_locator.json"
}
```

## Writer file

run/audits/LANE-X-CONTROLLED-PAPER-R4_STATE_WRITER_OWNER_LOCATOR_NO_PATCH_NO_ARM_NO_ORDER_20260616_113747_writer_owner_locator.json

## Source writer excerpt

```text
===== exact source lines for state/gate writers =====
app/mme_scalpx/core/redisx.py:243:def _redis_url_kwargs(redis_settings: RedisSettings) -> dict[str, Any]:
app/mme_scalpx/core/redisx.py:245:        "decode_responses": redis_settings.decode_responses,
app/mme_scalpx/core/redisx.py:246:        "retry_on_timeout": redis_settings.retry_on_timeout,
app/mme_scalpx/core/redisx.py:247:        "socket_timeout": redis_settings.socket_timeout_s,
app/mme_scalpx/core/redisx.py:248:        "socket_connect_timeout": redis_settings.socket_connect_timeout_s,
app/mme_scalpx/core/redisx.py:249:        "health_check_interval": redis_settings.health_check_interval_s,
app/mme_scalpx/core/redisx.py:250:        "max_connections": redis_settings.max_connections,
app/mme_scalpx/core/redisx.py:251:        "client_name": redis_settings.client_name,
app/mme_scalpx/core/redisx.py:254:    if redis_settings.password is not None:
app/mme_scalpx/core/redisx.py:255:        kwargs["password"] = redis_settings.password
app/mme_scalpx/core/redisx.py:257:    if redis_settings.uses_tls:
app/mme_scalpx/core/redisx.py:259:        if redis_settings.ssl_ca_path is not None:
app/mme_scalpx/core/redisx.py:260:            kwargs["ssl_ca_certs"] = str(redis_settings.ssl_ca_path)
app/mme_scalpx/core/redisx.py:269:def _default_stream_maxlen(redis_settings: RedisSettings) -> int:
app/mme_scalpx/core/redisx.py:271:        redis_settings.stream_maxlen_approx,
app/mme_scalpx/core/redisx.py:276:def _default_xread_count(redis_settings: RedisSettings) -> int:
app/mme_scalpx/core/redisx.py:278:        redis_settings.xread_count,
app/mme_scalpx/core/redisx.py:283:def _default_xread_block_ms(redis_settings: RedisSettings) -> int:
app/mme_scalpx/core/redisx.py:285:        redis_settings.xread_block_ms,
app/mme_scalpx/core/redisx.py:358:def build_redis_client(*, settings: AppSettings | None = None) -> Redis:
app/mme_scalpx/core/redisx.py:361:    redis_settings = app_settings.redis
app/mme_scalpx/core/redisx.py:363:        redis_settings.url,
app/mme_scalpx/core/redisx.py:364:        **_redis_url_kwargs(redis_settings),
app/mme_scalpx/core/redisx.py:368:def build_async_redis_client(*, settings: AppSettings | None = None) -> AsyncRedis:
app/mme_scalpx/core/redisx.py:371:    redis_settings = app_settings.redis
app/mme_scalpx/core/redisx.py:373:        redis_settings.url,
app/mme_scalpx/core/redisx.py:374:        **_redis_url_kwargs(redis_settings),
app/mme_scalpx/core/redisx.py:534:        changed = int(redis_client.hset(redis_key, mapping=normalized))
app/mme_scalpx/core/redisx.py:562:        changed = int(await redis_client.hset(redis_key, mapping=normalized))
app/mme_scalpx/core/redisx.py:666:    stream_id = xadd_fields(
app/mme_scalpx/core/redisx.py:696:    stream_id = await axadd_fields(
app/mme_scalpx/core/redisx.py:710:def xadd_fields(
app/mme_scalpx/core/redisx.py:719:    redis_settings = get_settings().redis
app/mme_scalpx/core/redisx.py:725:        _default_stream_maxlen(redis_settings)
app/mme_scalpx/core/redisx.py:731:        stream_id = redis_client.xadd(
app/mme_scalpx/core/redisx.py:739:        raise StreamTransportError(f"Failed to XADD to {stream!r}: {exc}") from exc
app/mme_scalpx/core/redisx.py:742:async def axadd_fields(
app/mme_scalpx/core/redisx.py:751:    redis_settings = get_settings().redis
app/mme_scalpx/core/redisx.py:757:        _default_stream_maxlen(redis_settings)
app/mme_scalpx/core/redisx.py:763:        stream_id = await redis_client.xadd(
app/mme_scalpx/core/redisx.py:772:            f"Failed to async XADD to {stream!r}: {exc}"
app/mme_scalpx/core/redisx.py:784:    return xadd_fields(
app/mme_scalpx/core/redisx.py:800:    return await axadd_fields(
app/mme_scalpx/core/redisx.py:886:    redis_settings = get_settings().redis
app/mme_scalpx/core/redisx.py:897:        _default_xread_count(redis_settings)
app/mme_scalpx/core/redisx.py:902:        _default_xread_block_ms(redis_settings)
app/mme_scalpx/core/redisx.py:929:    redis_settings = get_settings().redis
app/mme_scalpx/core/redisx.py:940:        _default_xread_count(redis_settings)
app/mme_scalpx/core/redisx.py:945:        _default_xread_block_ms(redis_settings)
app/mme_scalpx/core/redisx.py:975:    redis_settings = get_settings().redis
app/mme_scalpx/core/redisx.py:988:        _default_xread_count(redis_settings)
app/mme_scalpx/core/redisx.py:993:        _default_xread_block_ms(redis_settings)
app/mme_scalpx/core/redisx.py:1026:    redis_settings = get_settings().redis
app/mme_scalpx/core/redisx.py:1039:        _default_xread_count(redis_settings)
app/mme_scalpx/core/redisx.py:1044:        _default_xread_block_ms(redis_settings)
app/mme_scalpx/core/redisx.py:1557:        acquired = redis_client.set(lock_key, lock_owner, nx=True, px=lock_ttl_ms)
app/mme_scalpx/core/redisx.py:1581:        acquired = await redis_client.set(lock_key, lock_owner, nx=True, px=lock_ttl_ms)
app/mme_scalpx/core/redisx.py:1758:    "axadd_fields",
app/mme_scalpx/core/redisx.py:1791:    "xadd_fields",
app/mme_scalpx/core/models.py:2513:    has_position: bool
app/mme_scalpx/core/models.py:2514:    position_side: str
app/mme_scalpx/core/models.py:2538:        _require_bool(self.has_position, "has_position")
app/mme_scalpx/core/models.py:2539:        _require_literal(self.position_side, "position_side", allowed=ALLOWED_POSITION_SIDES)
app/mme_scalpx/core/models.py:2573:        if self.has_position:
app/mme_scalpx/core/models.py:2575:                self.position_side in (
app/mme_scalpx/core/models.py:2586:            _require(self.position_side == names.POSITION_SIDE_FLAT, "flat position must use position_side FLAT")
app/mme_scalpx/core/models.py:2671:    veto_entries: bool
app/mme_scalpx/core/models.py:2688:        _require_bool(self.veto_entries, "veto_entries")
app/mme_scalpx/core/models.py:2883:    position_side: str | None = None
app/mme_scalpx/core/models.py:2908:        if self.position_side is not None:
app/mme_scalpx/core/models.py:2909:            _require_literal(self.position_side, "position_side", allowed=ALLOWED_POSITION_SIDES)
app/mme_scalpx/core/names.py:782:HASH_STATE_RISK: Final[str] = "state:risk"
app/mme_scalpx/core/names.py:783:HASH_STATE_POSITION_MME: Final[str] = "state:position:mme"
app/mme_scalpx/core/names.py:784:HASH_STATE_EXECUTION: Final[str] = "state:execution"
app/mme_scalpx/core/settings.py:837:def build_redis_settings(
app/mme_scalpx/core/settings.py:1163:    if settings.redis.uses_tls and settings.redis.ssl_ca_path is not None:
app/mme_scalpx/core/settings.py:1183:            f"redis={settings.redis.xread_block_ms})"
app/mme_scalpx/core/settings.py:1211:    redis = build_redis_settings(
app/mme_scalpx/core/settings.py:1455:    "build_redis_settings",
app/mme_scalpx/research_capture/models.py:659:    position_side: str | None = None
app/mme_scalpx/research_capture/contracts.py:662:        ("position_side", "str", SA, OPT, LIVE, AUD, (AP,), "Position side", ()),
app/mme_scalpx/main.py:128:        and not os.environ.get("SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME")
app/mme_scalpx/main.py:1060:        sync_client = redisx.build_redis_client(settings=settings)
app/mme_scalpx/main.py:1066:        async_client = redisx.build_async_redis_client(settings=settings)
app/mme_scalpx/main.py:1131:        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
app/mme_scalpx/main.py:1132:        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
app/mme_scalpx/integrations/bootstrap_quote.py:78:        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
app/mme_scalpx/integrations/bootstrap_quote.py:79:        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
app/mme_scalpx/integrations/provider_runtime.py:846:    if inputs.position_state is not None and inputs.position_state.has_position:
app/mme_scalpx/integrations/provider_runtime.py:873:    has_open_position = bool(inputs.position_state.has_position) if inputs.position_state else False
app/mme_scalpx/integrations/broker_api.py:1437:_A6_R3_ALLOWED_CONTROLLED_PAPER_ROUTES = frozenset(("paper", "sandbox"))
app/mme_scalpx/integrations/broker_api.py:1492:def submit_controlled_paper_sandbox_order(
app/mme_scalpx/integrations/broker_api.py:1511:        "controlled_paper": True,
app/mme_scalpx/integrations/broker_api.py:1540:    if route not in _A6_R3_ALLOWED_CONTROLLED_PAPER_ROUTES:
app/mme_scalpx/integrations/broker_api.py:1543:            status="FAIL_CLOSED_INVALID_CONTROLLED_PAPER_ROUTE",
app/mme_scalpx/ops_dashboard/server.py:44:    "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
app/mme_scalpx/ops_dashboard/server.py:45:    "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
app/mme_scalpx/ops_dashboard/server.py:536:        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
app/mme_scalpx/ops_dashboard/server.py:537:        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
app/mme_scalpx/ops/healthcheck.py:226:        side = _first_present(payload, ("side", "position_side", "state"))
app/mme_scalpx/ops/healthcheck.py:230:        veto = _first_present(payload, ("veto_entries", "entries_vetoed", "block_entries"))
app/mme_scalpx/ops/healthcheck.py:232:            s
```
