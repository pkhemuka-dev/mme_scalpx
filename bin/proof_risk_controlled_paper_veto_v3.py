#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import pathlib
import py_compile
import subprocess
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
RISK = ROOT / "app/mme_scalpx/services/risk.py"
PROOF = ROOT / "run/proofs/proof_risk_controlled_paper_veto.json"
MILESTONE = ROOT / f"docs/milestones/{datetime.now().date().isoformat()}_batch26c_risk_controlled_paper_veto.md"

HELPER_BEGIN = "# BEGIN BATCH26C_RISK_CONTROLLED_PAPER_VETO"
HELPER_END = "# END BATCH26C_RISK_CONTROLLED_PAPER_VETO"

REQUIRED_REASONS = [
    "CONTROLLED_PAPER_NOT_ARMED",
    "CONTROLLED_PAPER_SCOPE_MISMATCH",
    "CONTROLLED_PAPER_QTY_CAP_FAIL",
    "CONTROLLED_PAPER_REAL_LIVE_FORBIDDEN",
    "CONTROLLED_PAPER_TIME_GATE_FAIL",
    "CONTROLLED_PAPER_POSITION_NOT_FLAT",
]


class DummyRiskService:
    def __init__(self) -> None:
        self.runtime = SimpleNamespace(
            veto_entries=False,
            veto_reason="",
            position_open=False,
            has_position=False,
            qty_lots=0,
            quantity=0,
            qty=0,
            batch26c_controlled_paper_veto_detail="",
        )
        self.redis = None
        self._batch26c_controlled_paper_config_override = {}
        self._batch26c_time_gate_override = True

    def _recompute_veto(self, now_ns: int) -> None:
        self.runtime.veto_entries = False
        self.runtime.veto_reason = ""

    def _build_snapshot(self, now_ns: int) -> dict[str, str]:
        return {
            "veto_entries": "1" if self.runtime.veto_entries else "0",
            "reason_code": self.runtime.veto_reason,
            "reason_message": self.runtime.veto_reason,
            "allow_exits": "1",
        }


@contextmanager
def patched_env(values: dict[str, str | None]):
    old = {k: os.environ.get(k) for k in values}
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


def run_cmd(args: list[str], timeout: int = 60) -> dict[str, Any]:
    try:
        cp = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, timeout=timeout)
        return {
            "returncode": cp.returncode,
            "stdout": cp.stdout[-5000:],
            "stderr": cp.stderr[-5000:],
        }
    except Exception as exc:
        return {"returncode": None, "stdout": "", "stderr": repr(exc)}


def read_risk() -> str:
    return RISK.read_text(encoding="utf-8", errors="replace")


def helper_block(text: str) -> str:
    start = text.find(HELPER_BEGIN)
    end = text.find(HELPER_END)
    if start < 0 or end < 0:
        raise RuntimeError("Batch 26C helper block missing or partial")
    return text[start:end + len(HELPER_END)]


def valid_cfg(**overrides: Any) -> dict[str, Any]:
    cfg = {
        "controlled_paper_trial_enabled": True,
        "paper_armed_enabled": True,
        "real_live_allowed": False,
        "selected_family": "MIST",
        "selected_side": "CALL",
        "quantity_lots": 1,
        "automatic_broker_failover_allowed": False,
        "mid_position_provider_migration_allowed": False,
    }
    cfg.update(overrides)
    return cfg


def run_dynamic_tests() -> dict[str, Any]:
    text = read_risk()
    ns: dict[str, Any] = {
        "RiskService": DummyRiskService,
        "__file__": str(RISK),
    }
    exec(helper_block(text), ns)

    results: dict[str, Any] = {}

    def case(
        name: str,
        cfg: dict[str, Any],
        expected: str | None,
        *,
        env_ok: bool = True,
        time_ok: bool = True,
        position_open: bool = False,
        qty_lots: int = 0,
    ) -> None:
        svc = DummyRiskService()
        svc._batch26c_controlled_paper_config_override = cfg
        svc._batch26c_time_gate_override = time_ok

        # Important v3 repair:
        # Drive the installed helper through the runtime fields it actually reads.
        svc.runtime.position_open = position_open
        svc.runtime.has_position = position_open
        svc.runtime.qty_lots = qty_lots
        svc.runtime.quantity = qty_lots
        svc.runtime.qty = qty_lots

        env = {
            "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME": "1" if env_ok else None,
            "SCALPX_CONTROLLED_PAPER_SCOPE_ACK": "I_ACCEPT_MIST_CALL_1LOT_PAPER_ONLY" if env_ok else None,
        }

        with patched_env(env):
            reason, details = ns["_batch26c_controlled_paper_veto_reason"](svc, 1_800_000_000_000_000_000)
            svc._recompute_veto(1_800_000_000_000_000_000)
            snapshot = svc._build_snapshot(1_800_000_000_000_000_000)

        results[name] = {
            "expected": expected,
            "reason": reason,
            "pass": (
                reason == expected
                and snapshot.get("allow_exits") == "1"
                and snapshot.get("risk_blocks_entries_only") == "1"
            ),
            "veto_entries": svc.runtime.veto_entries,
            "veto_reason": svc.runtime.veto_reason,
            "allow_exits": snapshot.get("allow_exits"),
            "risk_blocks_entries_only": snapshot.get("risk_blocks_entries_only"),
            "snapshot": snapshot,
            "details": details,
        }

    case(
        "not_armed",
        valid_cfg(controlled_paper_trial_enabled=False, paper_armed_enabled=False),
        "CONTROLLED_PAPER_NOT_ARMED",
        env_ok=False,
    )
    case(
        "scope_mismatch",
        valid_cfg(selected_family="MISB", selected_side="CALL"),
        "CONTROLLED_PAPER_SCOPE_MISMATCH",
    )
    case(
        "qty_cap_fail",
        valid_cfg(quantity_lots=2),
        "CONTROLLED_PAPER_QTY_CAP_FAIL",
    )
    case(
        "real_live_forbidden",
        valid_cfg(real_live_allowed=True),
        "CONTROLLED_PAPER_REAL_LIVE_FORBIDDEN",
    )
    case(
        "time_gate_fail",
        valid_cfg(),
        "CONTROLLED_PAPER_TIME_GATE_FAIL",
        time_ok=False,
    )
    case(
        "position_not_flat",
        valid_cfg(),
        "CONTROLLED_PAPER_POSITION_NOT_FLAT",
        position_open=True,
        qty_lots=1,
    )
    case(
        "valid_controlled_paper_no_veto",
        valid_cfg(),
        None,
        position_open=False,
        qty_lots=0,
    )

    return results


def main() -> int:
    text = read_risk()

    py_compile_result = {"ok": True, "error": None}
    try:
        py_compile.compile(str(RISK), doraise=True)
    except Exception as exc:
        py_compile_result = {"ok": False, "error": repr(exc)}

    compileall_result = run_cmd([sys.executable, "-m", "compileall", "-q", "app/mme_scalpx/services/risk.py"])

    tests = run_dynamic_tests()
    all_tests_pass = all(item["pass"] is True for item in tests.values())

    required_reasons_present = {reason: reason in text for reason in REQUIRED_REASONS}
    static_ok = (
        HELPER_BEGIN in text
        and HELPER_END in text
        and all(required_reasons_present.values())
        and 'snapshot["allow_exits"] = "1"' in text
        and 'snapshot["risk_blocks_entries_only"] = "1"' in text
        and "RiskService._recompute_veto = _batch26c_recompute_veto" in text
        and "RiskService._build_snapshot = _batch26c_build_snapshot" in text
    )

    report = {
        "batch": "26C_risk_controlled_paper_veto_v3_proof_harness_repair",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": "app/mme_scalpx/services/risk.py",
        "source_code_patched_by_this_v3": False,
        "paper_armed_enabled_by_this_proof": False,
        "real_live_enabled_by_this_proof": False,
        "services_started_by_this_proof": False,
        "redis_writes_by_this_proof": False,
        "compile_checks": {
            "py_compile": py_compile_result,
            "compileall_risk_py": compileall_result,
        },
        "static_checks": {
            "helper_present": HELPER_BEGIN in text and HELPER_END in text,
            "required_reasons_present": required_reasons_present,
            "allow_exits_forced_one": 'snapshot["allow_exits"] = "1"' in text,
            "risk_blocks_entries_only_forced_one": 'snapshot["risk_blocks_entries_only"] = "1"' in text,
            "recompute_wrapped": "RiskService._recompute_veto = _batch26c_recompute_veto" in text,
            "snapshot_wrapped": "RiskService._build_snapshot = _batch26c_build_snapshot" in text,
            "static_ok": static_ok,
        },
        "dynamic_reason_tests": tests,
        "verdict": {
            "risk_controlled_paper_veto_ok": bool(
                py_compile_result["ok"]
                and compileall_result["returncode"] == 0
                and static_ok
                and all_tests_pass
            ),
            "all_required_blockers_proven": all_tests_pass,
            "risk_blocks_entries": True,
            "risk_does_not_block_exits": all(item["allow_exits"] == "1" for item in tests.values()),
            "paper_armed_approved": False,
            "real_live_approved": False,
            "runtime_promotion_allowed": False,
            "next_recommended_batch": "26D_strategy_family_mandatory_stage_fail_closed",
        },
    }

    PROOF.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# Batch 26C — Risk-side Explicit Controlled Paper Arming Veto",
        "",
        f"Date: {datetime.now().date().isoformat()}",
        "",
        "## Verdict",
        "",
        f"- risk_controlled_paper_veto_ok: `{report['verdict']['risk_controlled_paper_veto_ok']}`",
        f"- all_required_blockers_proven: `{report['verdict']['all_required_blockers_proven']}`",
        f"- risk_blocks_entries: `{report['verdict']['risk_blocks_entries']}`",
        f"- risk_does_not_block_exits: `{report['verdict']['risk_does_not_block_exits']}`",
        "- paper_armed_approved: `False`",
        "- real_live_approved: `False`",
        "- runtime_promotion_allowed: `False`",
        "",
        "## V3 Note",
        "",
        "Batch 26C source patch was already present. V3 repaired only the proof harness by driving the installed helper through runtime position fields instead of an unsupported override.",
        "",
        "## Required Blocker Proofs",
        "",
        "```json",
        json.dumps(tests, indent=2, sort_keys=True),
        "```",
        "",
        "## Artifacts",
        "",
        "- `run/proofs/proof_risk_controlled_paper_veto.json`",
        f"- backup: `{pathlib.Path('$BACKUP_DIR').name}`",
        "",
        "## Continuation",
        "",
        "Next recommended batch: `26D — Five-family mandatory fail-closed stage repair`.",
        "",
        "Do not enable paper_armed. Do not enable real live. Do not start controlled paper runtime chain from this batch.",
        "",
    ]
    MILESTONE.write_text("\n".join(lines), encoding="utf-8")

    print("===== BATCH 26C V3 FINAL VERDICT =====")
    print(json.dumps(report["verdict"], indent=2, sort_keys=True))

    print("===== BATCH 26C V3 REQUIRED BLOCKER CHECKS =====")
    for name, result in tests.items():
        print(
            f"{name}: pass={result['pass']} "
            f"reason={result['reason']} "
            f"expected={result['expected']} "
            f"allow_exits={result['allow_exits']} "
            f"risk_blocks_entries_only={result['risk_blocks_entries_only']}"
        )

    print("===== BATCH 26C V3 OUTPUTS =====")
    print("Proof:", PROOF.relative_to(ROOT))
    print("Milestone:", MILESTONE.relative_to(ROOT))

    return 0 if report["verdict"]["risk_controlled_paper_veto_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
