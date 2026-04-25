#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services import monitor as M
from app.mme_scalpx.services import report as R


class FakeRedis:
    def __init__(self, hashes: dict[str, dict[str, Any]] | None = None) -> None:
        self.hashes = hashes or {}

    def hgetall(self, key: str) -> dict[str, Any]:
        return dict(self.hashes.get(key, {}))


def _run_py(args: list[str]) -> tuple[int, str, str]:
    completed = subprocess.run(
        [sys.executable, *args],
        cwd=str(PROJECT_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return completed.returncode, completed.stdout, completed.stderr


def main() -> int:
    cases: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # bootstrap_groups consumes names.get_group_specs only.
    # ------------------------------------------------------------------
    import app.mme_scalpx.ops.bootstrap_groups as BG

    live_expected = [
        (stream, group)
        for stream, groups in N.get_group_specs(replay=False).items()
        for group in groups
    ]
    replay_expected = [
        (stream, group)
        for stream, groups in N.get_group_specs(replay=True).items()
        for group in groups
    ]
    live_actual = [(spec.stream, spec.group) for spec in BG.canonical_group_specs(replay=False)]
    replay_actual = [(spec.stream, spec.group) for spec in BG.canonical_group_specs(replay=True)]

    bg_text = Path("app/mme_scalpx/ops/bootstrap_groups.py").read_text()
    cases.append({
        "case": "bootstrap_groups_matches_names_live_and_replay",
        "status": "PASS"
        if live_actual == live_expected and replay_actual == replay_expected and "LIVE_GROUP_SPECS" not in bg_text
        else "FAIL",
        "live_actual": live_actual,
        "live_expected": live_expected,
        "replay_actual": replay_actual,
        "replay_expected": replay_expected,
    })

    cases.append({
        "case": "bootstrap_groups_option_stream_uses_option_group",
        "status": "PASS"
        if (N.STREAM_TICKS_MME_OPT, getattr(N, "GROUP_FEATURES_MME_OPT_V1", N.get_group_specs(replay=False)[N.STREAM_TICKS_MME_OPT][0])) in live_actual
        else "FAIL",
        "live_actual": live_actual,
    })

    # ------------------------------------------------------------------
    # ops_cmd raw schema.
    # ------------------------------------------------------------------
    import app.mme_scalpx.ops.ops_cmd as OC

    fields = OC._build_command_fields(
        command_type=N.CMD_SET_MODE,
        producer="proof",
        reason="proof_reason",
        mode=N.CONTROL_MODE_SAFE,
        params={"x": "1"},
    )
    cases.append({
        "case": "ops_cmd_publishes_raw_runtime_command_schema",
        "status": "PASS"
        if fields.get("cmd") == N.CMD_SET_MODE
        and fields.get("mode") == N.CONTROL_MODE_SAFE
        and fields.get("reason") == "proof_reason"
        and "payload_json" not in fields
        and "model_type" not in fields
        else "FAIL",
        "fields": fields,
    })

    try:
        OC._build_command_fields(
            command_type=N.CMD_SET_MODE,
            producer="proof",
            reason="bad",
            mode=getattr(N, "EXECUTION_MODE_EXIT_ONLY", "EXIT_ONLY"),
            params={},
        )
    except Exception as exc:
        cases.append({
            "case": "ops_cmd_rejects_exit_only_as_control_mode",
            "status": "PASS" if "SET_MODE requires mode" in str(exc) else "FAIL",
            "error": str(exc),
        })
    else:
        cases.append({
            "case": "ops_cmd_rejects_exit_only_as_control_mode",
            "status": "FAIL",
            "error": "EXIT_ONLY accepted",
        })

    # ------------------------------------------------------------------
    # stop_session no invalid EXIT_ONLY publication path.
    # ------------------------------------------------------------------
    stop_text = Path("app/mme_scalpx/ops/stop_session.py").read_text()
    cases.append({
        "case": "stop_session_uses_safe_mode_not_exit_only",
        "status": "PASS"
        if "--set-safe-mode" in stop_text and "EXIT_ONLY" not in stop_text
        else "FAIL",
    })

    rc, out, err = _run_py(["-m", "app.mme_scalpx.ops.ops_cmd", N.CMD_SET_MODE, "--mode", N.CONTROL_MODE_SAFE, "--reason", "proof", "--dry-run"])
    cases.append({
        "case": "ops_cmd_dry_run_set_mode_safe",
        "status": "PASS" if rc == 0 and "cmd=SET_MODE" in out and "mode=SAFE" in out else "FAIL",
        "stdout": out,
        "stderr": err,
        "returncode": rc,
    })

    # ------------------------------------------------------------------
    # monitor context redis + missing state visibility.
    # ------------------------------------------------------------------
    original_get_redis = M.RX.get_redis
    try:
        M.RX.get_redis = lambda: (_ for _ in ()).throw(RuntimeError("RX.get_redis must not be called"))
        ctx = type("Ctx", (), {"redis": FakeRedis(), "settings": None})()
        try:
            resolved = M._resolve_redis_client_from_context(ctx)
            cases.append({
                "case": "monitor_uses_context_raw_redis_without_fallback",
                "status": "PASS" if isinstance(resolved, FakeRedis) else "FAIL",
            })
        except Exception as exc:
            cases.append({
                "case": "monitor_uses_context_raw_redis_without_fallback",
                "status": "FAIL",
                "error": str(exc),
            })
    finally:
        M.RX.get_redis = original_get_redis

    missing = M._batch15_missing_state_hashes(FakeRedis({}))
    cases.append({
        "case": "monitor_missing_critical_state_is_error_not_ok",
        "status": "PASS"
        if M._batch15_state_missing_status(missing) == N.HEALTH_STATUS_ERROR
        and any(label == "execution" for label, _severity in missing)
        and any(label == "risk" for label, _severity in missing)
        else "FAIL",
        "missing": missing,
    })

    # ------------------------------------------------------------------
    # report merge and PnL semantics.
    # ------------------------------------------------------------------
    entry = R.TradeRecord(trade_key="entry-order-a")
    entry.position_id = "pos-1"
    entry.entry_ts = datetime(2026, 4, 25, 9, 30, tzinfo=timezone.utc)
    entry.entry_qty = 1
    entry.fees = 10.0
    entry.raw_events.append({"position_id": "pos-1", "fees": "10"})

    exit_trade = R.TradeRecord(trade_key="exit-order-b")
    exit_trade.position_id = "pos-1"
    exit_trade.exit_ts = datetime(2026, 4, 25, 9, 31, tzinfo=timezone.utc)
    exit_trade.exit_qty = 1
    exit_trade.fees = 5.0
    exit_trade.raw_events.append({"position_id": "pos-1", "net_pnl": "100", "fees": "5"})

    merged = R._batch15_merge_trade_records([entry, exit_trade])
    for trade in merged:
        R._batch15_finalize_trade_pnl(trade)

    cases.append({
        "case": "report_merges_entry_exit_by_position_id",
        "status": "PASS" if len(merged) == 1 and merged[0].closed else "FAIL",
        "merged_count": len(merged),
        "trade": merged[0].to_row(include_entry_mode=True) if merged else {},
    })

    cases.append({
        "case": "report_net_pnl_not_double_subtracted",
        "status": "PASS"
        if len(merged) == 1 and merged[0].net_pnl == 100.0 and merged[0].gross_pnl == 115.0
        else "FAIL",
        "net_pnl": merged[0].net_pnl if merged else None,
        "gross_pnl": merged[0].gross_pnl if merged else None,
        "fees": merged[0].fees if merged else None,
    })

    # ------------------------------------------------------------------
    # Ops import root consistency.
    # ------------------------------------------------------------------
    ops_files = sorted(Path("app/mme_scalpx/ops").glob("*.py"))
    bad_imports: list[str] = []
    for path in ops_files:
        text = path.read_text()
        if "from mme_scalpx." in text or "import mme_scalpx." in text or '"mme_scalpx.' in text or "'mme_scalpx." in text:
            bad_imports.append(str(path))

    cases.append({
        "case": "ops_tools_use_app_mme_scalpx_package_root",
        "status": "PASS" if not bad_imports else "FAIL",
        "bad_imports": bad_imports,
    })

    import app.mme_scalpx.ops.healthcheck
    import app.mme_scalpx.ops.preflight
    import app.mme_scalpx.ops.start_session
    import app.mme_scalpx.ops.stop_session
    import app.mme_scalpx.ops.validate_bootstrap_provider
    import app.mme_scalpx.ops.validate_bootstrap_runtime
    import app.mme_scalpx.ops.validate_runtime_instruments
    import app.mme_scalpx.ops.validate_zerodha_feed_adapter

    cases.append({
        "case": "ops_modules_import",
        "status": "PASS",
    })

    failed = [case for case in cases if case.get("status") != "PASS"]
    proof = {
        "proof": "monitor_report_ops_contracts",
        "status": "FAIL" if failed else "PASS",
        "failed_cases": failed,
        "cases": cases,
    }

    out_path = PROJECT_ROOT / "run" / "proofs" / "monitor_report_ops_contracts.json"
    out_path.write_text(json.dumps(proof, indent=2, sort_keys=True, default=str))
    print(json.dumps(proof, indent=2, sort_keys=True, default=str))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
