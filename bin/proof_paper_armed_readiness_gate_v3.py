#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "run/proofs/proof_paper_armed_readiness_gate_v3.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_first(paths: list[str]) -> dict[str, Any]:
    for path in paths:
        p = ROOT / path
        if not p.exists():
            continue
        try:
            d = json.loads(p.read_text(errors="replace"))
            if isinstance(d, dict):
                d["_path"] = path
                return d
        except Exception as exc:
            return {"_path": path, "_parse_error": repr(exc)}
    return {"_missing": True, "_paths": paths}


def status(d: dict[str, Any]) -> str:
    if d.get("_missing"):
        return "MISSING"
    if d.get("_parse_error"):
        return "PARSE_ERROR"
    return str(d.get("status") or d.get("overall_status") or d.get("result") or "UNKNOWN").upper()


def is_pass(d: dict[str, Any]) -> bool:
    return status(d) == "PASS"


def no_failures(d: dict[str, Any]) -> bool:
    for k in ("failures", "failed_cases", "failed_checks"):
        v = d.get(k)
        if isinstance(v, list) and v:
            return False
    return True


def main() -> int:
    proofs = {
        "runtime_truth": load_first(["run/proofs/proof_runtime_truth_authority.json"]),
        "broad_replay_materialization": load_first(["run/proofs/proof_aftermarket_broad_replay_materialization.json"]),
        "strong_replay_sample": load_first(["run/proofs/proof_aftermarket_strong_replay_sample.json"]),
        "semantic_replay_dry_run": load_first(["run/proofs/proof_aftermarket_full_replay_dry_run.json"]),
        "repo_hygiene": load_first(["run/proofs/repo_hygiene_quarantine.json"]),
        "redis_contract": load_first(["run/proofs/redis_contract_matrix.json"]),
        "provider_equivalence_static": load_first(["run/proofs/proof_runtime_instrument_provider_equivalence.json"]),
        "strategy_promoted_contract": load_first(["run/proofs/proof_strategy_promoted_decision_contract.json"]),
        "execution_entry_safety": load_first([
            "run/proofs/execution_family_entry_safety.json",
            "run/proofs/proof_execution_family_entry_safety.json",
        ]),
        "risk_exit_never_blocked": load_first([
            "run/proofs/proof_risk_exit_never_blocked.json",
            "run/proofs/risk_batch14_freeze.json",
        ]),
        "research_firewall": load_first(["run/proofs/proof_research_capture_production_firewall.json"]),
        "monitor_report_ops": load_first(["run/proofs/monitor_report_ops_contracts.json"]),
        "legacy_quarantine": load_first(["run/proofs/legacy_baseline_quarantine.json"]),
        "names_alias_lifecycle": load_first(["run/proofs/names_alias_lifecycle.json"]),
    }

    checks = []

    def add(name: str, ok: bool, sev: str, detail: str) -> None:
        checks.append({"name": name, "ok": bool(ok), "severity": sev, "detail": detail})

    rt = proofs["runtime_truth"]
    add(
        "runtime_truth_pass",
        is_pass(rt) and rt.get("paper_armed_allowed") is True,
        "P0",
        f"status={status(rt)} paper_armed_allowed={rt.get('paper_armed_allowed')} path={rt.get('_path')}",
    )

    br = proofs["broad_replay_materialization"]
    add(
        "broad_replay_materialization_pass",
        is_pass(br)
        and br.get("replay_only_channels") is True
        and int(br.get("events_materialized") or 0) >= int(br.get("minimum_events_required") or 150)
        and len(br.get("kinds") or []) >= int(br.get("minimum_kinds_required") or 3),
        "P1",
        f"status={status(br)} events={br.get('events_materialized')} kinds={br.get('kinds')} path={br.get('_path')}",
    )

    # Strong single-session sample is useful but not a structural blocker if broad materialization passes.
    sr = proofs["strong_replay_sample"]
    add(
        "single_selection_strong_replay_observed",
        status(sr) in {"PASS", "WARN"},
        "P2",
        f"status={status(sr)} events={sr.get('events_materialized')} path={sr.get('_path')}",
    )

    sem = proofs["semantic_replay_dry_run"]
    add(
        "semantic_replay_smoke_pass",
        is_pass(sem) and sem.get("replay_only_channels") is True and int(sem.get("events_materialized") or 0) > 0,
        "P2",
        f"status={status(sem)} events={sem.get('events_materialized')} path={sem.get('_path')}",
    )

    for key, sev in [
        ("repo_hygiene", "P1"),
        ("redis_contract", "P1"),
        ("provider_equivalence_static", "P1"),
        ("strategy_promoted_contract", "P0"),
        ("execution_entry_safety", "P0"),
        ("risk_exit_never_blocked", "P0"),
        ("research_firewall", "P1"),
        ("monitor_report_ops", "P2"),
        ("legacy_quarantine", "P1"),
        ("names_alias_lifecycle", "P1"),
    ]:
        d = proofs[key]
        add(key, is_pass(d) and no_failures(d), sev, f"status={status(d)} path={d.get('_path')}")

    p0 = [c for c in checks if not c["ok"] and c["severity"] == "P0"]
    p1 = [c for c in checks if not c["ok"] and c["severity"] == "P1"]
    p2 = [c for c in checks if not c["ok"] and c["severity"] == "P2"]

    structural = not p0 and not p1

    result = {
        "proof": "proof_paper_armed_readiness_gate_v3",
        "generated_at": now_iso(),
        "status": "PASS" if structural else "WARN",
        "structural_paper_armed_allowed": structural,
        "market_session_paper_armed_allowed": False,
        "paper_armed_should_be_enabled_now": False,
        "gate_checks": checks,
        "p0_blockers": p0,
        "p1_blockers": p1,
        "p2_blockers": p2,
        "proof_statuses": {k: status(v) for k, v in proofs.items()},
        "notes": [
            "This proof does not enable paper_armed.",
            "V3 uses broad historical replay materialization as the after-hours replay strength gate.",
            "Single-selection strong replay WARN is tracked as P2 if broad materialization passes.",
            "Market-session paper readiness remains false until live provider/token/currentness proof passes.",
        ],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True))

    print(json.dumps({
        "status": result["status"],
        "structural_paper_armed_allowed": structural,
        "market_session_paper_armed_allowed": False,
        "p0_blockers": p0,
        "p1_blockers": p1,
        "p2_blockers": p2,
        "out": str(OUT.relative_to(ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
