#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx import main as M
from app.mme_scalpx.core import names
from app.mme_scalpx.core.clock import LiveClock
from app.mme_scalpx.core.settings import get_settings


class DummyFeedAdapter:
    def __init__(self, provider_id: str | None = None) -> None:
        self.provider_id = provider_id


class DummyBroker:
    provider_id = names.PROVIDER_ZERODHA


class DummyRedis:
    def ping(self) -> bool:
        return True


class DummyInstruments:
    current_future = object()
    ce_atm = object()
    ce_atm1 = object()
    pe_atm = object()
    pe_atm1 = object()
    selection_version = "proof"
    option_expiry = "2099-01-01"
    strike_step = 50
    underlying_reference = 22500.0
    underlying_symbol = "NIFTY"


@contextmanager
def patched_env(**values: str | None) -> Iterator[None]:
    old: dict[str, str | None] = {key: os.environ.get(key) for key in values}
    try:
        for key, value in values.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        yield
    finally:
        for key, value in old.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _app_for(deps: M.BootstrapDependencies) -> M.AppContext:
    settings = get_settings()
    return M.AppContext(
        settings=settings,
        redis=M.RedisRuntime(sync=DummyRedis()),
        clock=LiveClock(),
        node_name="proof-node",
        pid=1,
        app_name=settings.app_name,
        env=settings.app_env,
        dependencies=deps,
    )


def _expect_pass(label: str, fn) -> dict[str, Any]:
    try:
        value = fn()
    except Exception as exc:
        return {"case": label, "status": "FAIL", "error": f"{type(exc).__name__}: {exc}"}
    return {"case": label, "status": "PASS", "value": value}


def _expect_reject(label: str, fn) -> dict[str, Any]:
    try:
        fn()
    except Exception as exc:
        return {"case": label, "status": "PASS", "error": str(exc)}
    return {"case": label, "status": "FAIL", "error": "accepted invalid surface"}


def main() -> int:
    cases: list[dict[str, Any]] = []

    # Legacy single adapter remains migration-compatible in non-strict mode.
    with patched_env(MME_PROVIDER_RUNTIME_STRICT=None, MME_ALLOW_LEGACY_PROVIDER_ALIAS=None):
        deps = M.BootstrapDependencies(
            runtime_instruments=DummyInstruments(),
            feed_adapter=DummyFeedAdapter(names.PROVIDER_ZERODHA),
            broker=DummyBroker(),
        )
        app = _app_for(deps)
        cases.append(
            _expect_pass(
                "non_strict_legacy_zerodha_feed_adapter_still_compatible",
                lambda: M._require_service_dependencies(app, "feeds") or "ok",
            )
        )

    # Dhan context alone must not satisfy feeds dependency.
    with patched_env(MME_PROVIDER_RUNTIME_STRICT=None, MME_ALLOW_LEGACY_PROVIDER_ALIAS=None):
        deps = M.BootstrapDependencies(
            runtime_instruments=DummyInstruments(),
            dhan_context_adapter=object(),
            broker=DummyBroker(),
        )
        app = _app_for(deps)
        cases.append(
            _expect_reject(
                "dhan_context_only_does_not_satisfy_feeds_dependency",
                lambda: M._require_service_dependencies(app, "feeds"),
            )
        )

    # Strict provider runtime rejects legacy-only adapter.
    with patched_env(MME_PROVIDER_RUNTIME_STRICT="1", MME_ALLOW_LEGACY_PROVIDER_ALIAS=None):
        deps = M.BootstrapDependencies(
            runtime_instruments=DummyInstruments(),
            feed_adapter=DummyFeedAdapter(names.PROVIDER_ZERODHA),
            broker=DummyBroker(),
        )
        app = _app_for(deps)
        cases.append(
            _expect_reject(
                "strict_provider_runtime_rejects_legacy_only_feed_adapter",
                lambda: M._require_service_dependencies(app, "feeds"),
            )
        )

    # Strict provider runtime requires explicit Zerodha + Dhan market-data surfaces.
    with patched_env(MME_PROVIDER_RUNTIME_STRICT="1", MME_ALLOW_LEGACY_PROVIDER_ALIAS=None):
        deps = M.BootstrapDependencies(
            runtime_instruments=DummyInstruments(),
            feed_adapters={
                names.PROVIDER_ZERODHA: DummyFeedAdapter(names.PROVIDER_ZERODHA),
                names.PROVIDER_DHAN: DummyFeedAdapter(names.PROVIDER_DHAN),
            },
            zerodha_feed_adapter=DummyFeedAdapter(names.PROVIDER_ZERODHA),
            dhan_feed_adapter=DummyFeedAdapter(names.PROVIDER_DHAN),
            dhan_context_adapter=object(),
            broker=DummyBroker(),
        )
        app = _app_for(deps)
        cases.append(
            _expect_pass(
                "strict_provider_runtime_accepts_explicit_dual_feed_surfaces",
                lambda: M._require_service_dependencies(app, "feeds") or "ok",
            )
        )
        surfaces = M._resolve_feed_surface_bundle(settings=app.settings, dependencies=deps)
        cases.append(
            {
                "case": "strict_dual_provider_surface_map_contains_both",
                "status": "PASS"
                if isinstance(surfaces.feed_adapters, dict)
                and names.PROVIDER_ZERODHA in surfaces.feed_adapters
                and names.PROVIDER_DHAN in surfaces.feed_adapters
                else "FAIL",
                "feed_adapters": sorted(surfaces.feed_adapters.keys()) if isinstance(surfaces.feed_adapters, dict) else [],
            }
        )

    # Strict provider runtime may allow legacy alias only when explicitly opted in.
    with patched_env(MME_PROVIDER_RUNTIME_STRICT="1", MME_ALLOW_LEGACY_PROVIDER_ALIAS="1"):
        deps = M.BootstrapDependencies(
            runtime_instruments=DummyInstruments(),
            feed_adapter=DummyFeedAdapter(names.PROVIDER_ZERODHA),
            feed_adapters={
                names.PROVIDER_ZERODHA: DummyFeedAdapter(names.PROVIDER_ZERODHA),
                names.PROVIDER_DHAN: DummyFeedAdapter(names.PROVIDER_DHAN),
            },
            zerodha_feed_adapter=DummyFeedAdapter(names.PROVIDER_ZERODHA),
            dhan_feed_adapter=DummyFeedAdapter(names.PROVIDER_DHAN),
            broker=DummyBroker(),
        )
        app = _app_for(deps)
        cases.append(
            _expect_pass(
                "strict_provider_runtime_allows_legacy_alias_when_flag_enabled",
                lambda: M._require_service_dependencies(app, "feeds") or "ok",
            )
        )

    # Legacy runtime service files must be forbidden.
    forbidden = set(M.FORBIDDEN_RUNTIME_PATHS)
    cases.append(
        {
            "case": "legacy_service_files_explicitly_forbidden",
            "status": "PASS"
            if {
                "app.mme_scalpx.services.features_legacy_single",
                "app.mme_scalpx.services.strategy_legacy_single",
            }.issubset(forbidden)
            else "FAIL",
            "forbidden_runtime_paths": sorted(forbidden),
        }
    )

    # Service registry and service modules remain frozen.
    cases.append(
        _expect_pass(
            "service_registry_surface_valid",
            lambda: M._validate_service_registry_surface() or "ok",
        )
    )
    cases.append(
        _expect_pass(
            "frozen_service_modules_valid",
            lambda: M._validate_frozen_service_modules() or "ok",
        )
    )

    # Doctor/effective runtime report is visible and non-mutating.
    with patched_env(
        MME_PROVIDER_RUNTIME_STRICT="1",
        MME_ALLOW_LEGACY_PROVIDER_ALIAS=None,
        SCALPX_RUNTIME_MODE="paper",
    ):
        deps = M.BootstrapDependencies(
            runtime_instruments=DummyInstruments(),
            feed_adapters={
                names.PROVIDER_ZERODHA: DummyFeedAdapter(names.PROVIDER_ZERODHA),
                names.PROVIDER_DHAN: DummyFeedAdapter(names.PROVIDER_DHAN),
            },
            zerodha_feed_adapter=DummyFeedAdapter(names.PROVIDER_ZERODHA),
            dhan_feed_adapter=DummyFeedAdapter(names.PROVIDER_DHAN),
            broker=DummyBroker(),
        )
        app = _app_for(deps)
        report = M.build_doctor_report(
            app=app,
            replay_start_wall_time_ns=None,
            bootstrap_groups_enabled=False,
        )
        effective = report.get("effective_runtime", {})
        provider = report.get("provider_surfaces", {})
        cases.append(
            {
                "case": "doctor_report_exposes_effective_runtime_truth",
                "status": "PASS"
                if effective.get("runtime_behavior_changed_by_batch4") is False
                and effective.get("env_scalpx_runtime_mode") == "paper"
                and effective.get("bootstrap_groups_effective") is False
                and provider.get("strict_provider_runtime") is True
                else "FAIL",
                "effective_runtime": effective,
                "provider_surfaces": provider,
            }
        )

    failed = [case for case in cases if case.get("status") != "PASS"]

    proof = {
        "proof": "main_batch4_freeze",
        "status": "FAIL" if failed else "PASS",
        "failed_cases": failed,
        "cases": cases,
    }

    out = PROJECT_ROOT / "run" / "proofs" / "main_batch4_freeze.json"
    out.write_text(json.dumps(proof, indent=2, sort_keys=True))
    print(json.dumps(proof, indent=2, sort_keys=True))

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
