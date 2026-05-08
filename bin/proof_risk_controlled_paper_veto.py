#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
import os
import pathlib
import py_compile
import re
import subprocess
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

RISK = ROOT / "app/mme_scalpx/services/risk.py"
PROOF = ROOT / "run/proofs/proof_risk_controlled_paper_veto.json"

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
            qty_lots=0,
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
def env_patch(values: dict[str, str | None]):
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


def sha(path: pathlib.Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read() -> str:
    return RISK.read_text(encoding="utf-8", errors="replace")


def helper_block(text: str) -> str:
    start = text.find(HELPER_BEGIN)
    end = text.find(HELPER_END)
    if start < 0 or end < 0:
        raise RuntimeError("Batch 26C helper block missing")
    return text[start:end + len(HELPER_END)]


def run_cmd(args: list[str], timeout: int = 60) -> dict[str, Any]:
    try:
        cp = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, timeout=timeout)
        return {
            "cmd": args,
            "returncode": cp.returncode,
            "stdout": cp.stdout[-5000:],
            "stderr": cp.stderr[-5000:],
        }
    except Exception as exc:
        return {"cmd": args, "returncode": None, "stdout": "", "stderr": repr(exc)}


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


def execute_helper_dynamic_tests() -> dict[str, Any]:
    text = read()
    block = helper_block(text)
    ns: dict[str, Any] = {
        "RiskService": DummyRiskService,
        "__file__": str(RISK),
    }
    exec(block, ns)

    results: dict[str, Any] = {}

    def run_case(
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
        svc.runtime.position_open = position_open
        svc.runtime.qty_lots = qty_lots

        env = {
            "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME": "1" if env_ok else None,
            "SCALPX_CONTROLLED_PAPER_SCOPE_ACK": "I_ACCEPT_MIST_CALL_1LOT_PAPER_ONLY" if env_ok else None,
        }

        with env_patch(env):
            reason, details = ns["_batch26c_controlled_paper_veto_reason"](svc, 1_800_000_000_000_000_000)
            svc._recompute_veto(1_800_000_000_000_000_000)
            snapshot = svc._build_snapshot(1_800_000_000_000_000_000)

        results[name] = {
            "expected": expected,
            "reason": reason,
            "details": details,
            "runtime_veto_entries": svc.runtime.veto_entries,
            "runtime_veto_reason": svc.runtime.veto_reason,
            "snapshot": snapshot,
            "pass": (
                reason == expected
                and snapshot.get("allow_exits") == "1"
                and snapshot.get("risk_blocks_entries_only") == "1"
            ),
        }

    run_case(
        "not_armed",
        valid_cfg(controlled_paper_trial_enabled=False, paper_armed_enabled=False),
        "CONTROLLED_PAPER_NOT_ARMED",
        env_ok=False,
    )
    run_case(
        "real_live_forbidden",
        valid_cfg(real_live_allowed=True),
        "CONTROLLED_PAPER_REAL_LIVE_FORBIDDEN",
    )
    run_case(
        "scope_mismatch",
        valid_cfg(selected_family="MISB", selected_side="CALL"),
        "CONTROLLED_PAPER_SCOPE_MISMATCH",
    )
    run_case(
        "qty_cap_fail",
        valid_cfg(quantity_lots=2),
        "CONTROLLED_PAPER_QTY_CAP_FAIL",
    )
    run_case(
        "position_not_flat",
        valid_cfg(),
        "CONTROLLED_PAPER_POSITION_NOT_FLAT",
        position_open=True,
        qty_lots=1,
    )
    run_case(
        "time_gate_fail",
        valid_cfg(),
        "CONTROLLED_PAPER_TIME_GATE_FAIL",
        time_ok=False,
    )
    run_case(
        "valid_controlled_paper_no_batch26c_veto",
        valid_cfg(),
        None,
        env_ok=True,
        time_ok=True,
        position_open=False,
        qty_lots=0,
    )

    return results


def grep(pattern: str, max_hits: int = 160) -> list[dict[str, Any]]:
    rx = re.compile(pattern, re.IGNORECASE)
    out = []
    for lineno, line in enumerate(read().splitlines(), 1):
        if rx.search(line):
            out.append({"line": lineno, "text": line.rstrip()[:260]})
            if len(out) >= max_hits:
                break
    return out


def main() -> int:
    started = time.time()
    text = read()

    py_compile_result = {"ok": False, "error": None}
    try:
        py_compile.compile(str(RISK), doraise=True)
        py_compile_result = {"ok": True, "error": None}
    except Exception as exc:
        py_compile_result = {"ok": False, "error": repr(exc)}

    compileall_result = run_cmd([sys.executable, "-m", "compileall", "-q", "app/mme_scalpx/services/risk.py"], timeout=60)

    import_results = {}
    for mod in [
        "app.mme_scalpx.services.risk",
        "app.mme_scalpx.services.execution",
        "app.mme_scalpx.services.strategy",
        "app.mme_scalpx.services.controlled_paper_runtime",
    ]:
        try:
            importlib.import_module(mod)
            import_results[mod] = {"ok": True, "error": None}
        except Exception as exc:
            import_results[mod] = {"ok": False, "error": repr(exc)}

    dynamic_results = execute_helper_dynamic_tests()
    reasons_present = {reason: (reason in text) for reason in REQUIRED_REASONS}
    dynamic_all_pass = all(case.get("pass") is True for case in dynamic_results.values())

    static_checks = {
        "helper_begin_present": HELPER_BEGIN in text,
        "helper_end_present": HELPER_END in text,
        "riskservice_recompute_wrapped": "RiskService._recompute_veto = _batch26c_recompute_veto" in text,
        "riskservice_snapshot_wrapped": "RiskService._build_snapshot = _batch26c_build_snapshot" in text,
        "allow_exits_forced_one": 'snapshot["allow_exits"] = "1"' in text,
        "risk_blocks_entries_only_field": 'snapshot["risk_blocks_entries_only"] = "1"' in text,
        "uses_names_for_position_hash_key": "_batch26c_position_hash_key" in text and "HASH_STATE_POSITION_MME" in text,
        "no_raw_state_position_mme_literal": "state:position:mme" not in text,
        "required_reasons_present": reasons_present,
        "controlled_paper_lines": grep(r"CONTROLLED_PAPER|controlled_paper|real_live_allowed|paper_armed", 260),
        "allow_exits_lines": grep(r"allow_exits|risk_blocks_entries_only", 120),
    }

    derived = {
        "py_compile_ok": py_compile_result["ok"],
        "compileall_ok": compileall_result.get("returncode") == 0,
        "imports_ok": all(v.get("ok") for v in import_results.values()),
        "helper_present": static_checks["helper_begin_present"] and static_checks["helper_end_present"],
        "recompute_veto_wrapped": static_checks["riskservice_recompute_wrapped"],
        "snapshot_wrapped": static_checks["riskservice_snapshot_wrapped"],
        "all_required_reasons_present": all(reasons_present.values()),
        "all_dynamic_reason_tests_pass": dynamic_all_pass,
        "risk_blocks_entries": "runtime.veto_entries = True" in text,
        "risk_does_not_block_exits": static_checks["allow_exits_forced_one"],
        "allow_exits_preserved_in_all_dynamic_snapshots": all(
            case.get("snapshot", {}).get("allow_exits") == "1"
            for case in dynamic_results.values()
        ),
        "risk_blocks_entries_only_field_present": static_checks["risk_blocks_entries_only_field"],
        "uses_names_for_position_hash_key": static_checks["uses_names_for_position_hash_key"],
        "no_raw_state_position_mme_literal": static_checks["no_raw_state_position_mme_literal"],
        "paper_armed_approved": False,
        "real_live_approved": False,
        "runtime_promotion_allowed": False,
    }

    blockers = []
    if not derived["py_compile_ok"]:
        blockers.append("PY_COMPILE_FAILED")
    if not derived["compileall_ok"]:
        blockers.append("COMPILEALL_FAILED")
    if not derived["imports_ok"]:
        blockers.append("IMPORT_FAILED")
    if not derived["helper_present"]:
        blockers.append("BATCH26C_HELPER_MISSING")
    if not derived["recompute_veto_wrapped"]:
        blockers.append("RECOMPUTE_VETO_NOT_WRAPPED")
    if not derived["snapshot_wrapped"]:
        blockers.append("BUILD_SNAPSHOT_NOT_WRAPPED")
    if not derived["all_required_reasons_present"]:
        blockers.append("REQUIRED_REASON_TOKEN_MISSING")
    if not derived["all_dynamic_reason_tests_pass"]:
        blockers.append("DYNAMIC_REASON_TEST_FAILED")
    if not derived["risk_blocks_entries"]:
        blockers.append("RISK_ENTRY_BLOCK_NOT_PROVEN")
    if not derived["risk_does_not_block_exits"]:
        blockers.append("RISK_EXIT_ALLOW_NOT_PROVEN")
    if not derived["allow_exits_preserved_in_all_dynamic_snapshots"]:
        blockers.append("DYNAMIC_ALLOW_EXITS_NOT_PRESERVED")
    if not derived["uses_names_for_position_hash_key"]:
        blockers.append("POSITION_HASH_KEY_NOT_NAMES_BASED")
    if not derived["no_raw_state_position_mme_literal"]:
        blockers.append("RAW_POSITION_REDIS_KEY_LITERAL_FOUND")

    report = {
        "batch": "26C_risk_controlled_paper_veto",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": "app/mme_scalpx/services/risk.py",
        "safety_posture": {
            "paper_armed_enabled_by_this_proof": False,
            "real_live_enabled_by_this_proof": False,
            "services_started_by_this_proof": False,
            "redis_writes_by_this_proof": False,
            "source_patched_before_this_proof": True,
        },
        "file": {
            "path": str(RISK.relative_to(ROOT)),
            "sha256": sha(RISK),
        },
        "compile_checks": {
            "py_compile": py_compile_result,
            "compileall_risk_py": compileall_result,
        },
        "import_results": import_results,
        "static_checks": static_checks,
        "dynamic_reason_tests": dynamic_results,
        "required_blockers": REQUIRED_REASONS,
        "derived": derived,
        "final_verdict": {
            "risk_controlled_paper_veto_ok": len(blockers) == 0,
            "all_required_blockers_proven": dynamic_all_pass and all(reasons_present.values()),
            "risk_blocks_entries": derived["risk_blocks_entries"],
            "risk_does_not_block_exits": derived["risk_does_not_block_exits"],
            "blockers": blockers,
            "paper_armed_approved": False,
            "real_live_approved": False,
            "runtime_promotion_allowed": False,
            "next_recommended_batch": "26D_strategy_family_mandatory_stage_fail_closed" if len(blockers) == 0 else "review_26c_blockers",
            "elapsed_seconds": round(time.time() - started, 3),
        },
    }

    PROOF.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

    milestone = ROOT / f"docs/milestones/{datetime.now().date().isoformat()}_batch26c_risk_controlled_paper_veto.md"
    lines = [
        "# Batch 26C — Risk-side Explicit Controlled Paper Arming Veto",
        "",
        f"Date: {datetime.now().date().isoformat()}",
        "",
        "## Verdict",
        "",
        f"- risk_controlled_paper_veto_ok: `{report['final_verdict']['risk_controlled_paper_veto_ok']}`",
        f"- all_required_blockers_proven: `{report['final_verdict']['all_required_blockers_proven']}`",
        f"- risk_blocks_entries: `{report['final_verdict']['risk_blocks_entries']}`",
        f"- risk_does_not_block_exits: `{report['final_verdict']['risk_does_not_block_exits']}`",
        "- paper_armed_approved: `False`",
        "- real_live_approved: `False`",
        "- runtime_promotion_allowed: `False`",
        "",
        "## Patched File",
        "",
        "- `app/mme_scalpx/services/risk.py`",
        "",
        "## Scope",
        "",
        "- Added explicit controlled-paper entry-veto reasons.",
        "- Wrapped `RiskService._recompute_veto` to apply Batch 26C entry-only veto before prior veto logic.",
        "- Wrapped `RiskService._build_snapshot` to preserve `allow_exits=1` and expose controlled-paper veto state.",
        "- Used names.py-derived position hash key lookup; no raw Redis key literal added.",
        "- Did not patch execution, strategy, controlled runtime, names, settings, or configs.",
        "",
        "## Derived Proof",
        "",
    ]

    for k, v in derived.items():
        lines.append(f"- {k}: `{v}`")

    lines.extend(["", "## Required Blocker Dynamic Tests", "", "```json"])
    lines.append(json.dumps(dynamic_results, indent=2, sort_keys=True))
    lines.extend(["```", "", "## Blockers", ""])

    if blockers:
        lines.extend([f"- `{x}`" for x in blockers])
    else:
        lines.append("- none")

    lines.extend([
        "",
        "## Artifacts",
        "",
        "- `bin/patch_batch26c_risk_controlled_paper_veto.py`",
        "- `bin/proof_risk_controlled_paper_veto.py`",
        "- `run/proofs/proof_risk_controlled_paper_veto.json`",
        "- `run/proofs/proof_risk_controlled_paper_veto_patch_step.json`",
        "",
        "## Continuation",
        "",
        "Do not enable paper_armed.",
        "Do not enable real live.",
        "Do not start controlled paper runtime chain from this batch.",
        "",
    ])

    milestone.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(report["final_verdict"], indent=2, sort_keys=True))
    return 0 if len(blockers) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
