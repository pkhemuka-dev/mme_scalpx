#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import re
import time
import subprocess
from collections import defaultdict


ROOT = pathlib.Path(".").resolve()

SEARCH_ROOTS = [
    pathlib.Path("app/mme_scalpx"),
    pathlib.Path("bin"),
    pathlib.Path("scripts"),
    pathlib.Path("docs"),
    pathlib.Path("tests"),
]

PATTERNS = {
    "candidate_gate": [
        "candidate_positive",
        "strategy_candidate",
        "candidate_audit",
        "candidate_true",
        "activation_candidate",
    ],
    "hold_gate": [
        "HOLD",
        "hold_only",
        "hold_only_family_features_consumer_bridge",
    ],
    "runtime_disabled_gate": [
        "runtime_disabled",
        "classic_runtime_disabled",
        "system_state",
        "DISABLED",
    ],
    "consumer_safety_gate": [
        "safe_to_consume",
        "provider_ready_classic",
        "tradability_ok",
        "data_valid",
        "snapshot_sync_valid",
        "data_quality_ok",
    ],
    "risk_shadow_gate": [
        "risk_shadow",
        "research_trade_allowed",
        "order_allowed",
        "HOLD_REPORT_ONLY",
        "final_action",
    ],
    "execution_shadow_gate": [
        "execution_shadow",
        "shadow_fill",
        "filled",
        "execution_shadow_filled",
    ],
    "order_intent_ledger_gate": [
        "order_intent",
        "real_order_intent_generated",
        "broker_send_enabled",
        "order_allowed",
        "route_to_order_intent_ledger",
    ],
    "miv_contract": [
        "MIV_R",
        "MIV_ZERODHA_LITE",
        "MIV_DHAN_FULL",
        "research_shadow_only",
    ],
    "broker_danger": [
        "place_order",
        "kite.place_order",
        "dhan",
        "broker",
        "send_order",
    ],
}

TEXT_SUFFIXES = {
    ".py", ".md", ".txt", ".json", ".jsonl", ".csv", ".sh", ".toml", ".yaml", ".yml"
}


def git_status() -> str:
    try:
        return subprocess.check_output(["git", "status", "--short"], text=True, stderr=subprocess.STDOUT)
    except Exception as exc:
        return f"ERROR: {exc}"


def iter_files():
    for root in SEARCH_ROOTS:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if ".venv" in p.parts or "__pycache__" in p.parts or ".git" in p.parts:
                continue
            if p.suffix.lower() not in TEXT_SUFFIXES:
                continue
            try:
                if p.stat().st_size > 2_000_000:
                    continue
            except OSError:
                continue
            yield p


def scan():
    hits = defaultdict(list)
    for p in iter_files():
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        lines = text.splitlines()
        for category, pats in PATTERNS.items():
            for i, line in enumerate(lines, 1):
                for pat in pats:
                    if re.search(re.escape(pat), line, flags=re.IGNORECASE):
                        hits[category].append({
                            "path": str(p),
                            "line": i,
                            "pattern": pat,
                            "text": line[:240],
                        })
    return hits


def import_checks():
    out = {
        "miv_contract_import_ok": False,
        "miv_family_id": None,
        "miv_active_production": None,
        "miv_research_shadow_only": None,
        "miv_not_in_strategy_family_ids": None,
        "miv_not_in_doctrine_ids": None,
        "miv_not_in_replay_feature_families": None,
        "miv_not_in_replay_strategy_families": None,
        "errors": [],
    }
    try:
        from app.mme_scalpx.services.strategy_family import miv_r_contract as MIV
        out["miv_contract_import_ok"] = True
        out["miv_family_id"] = getattr(MIV, "MIV_FAMILY_ID", None)
        out["miv_active_production"] = getattr(MIV, "MIV_IS_ACTIVE_PRODUCTION_FAMILY", None)
        out["miv_research_shadow_only"] = getattr(MIV, "MIV_RESEARCH_SHADOW_ONLY", None)

        from app.mme_scalpx.core import names as N
        from app.mme_scalpx.replay import feature_adapter, strategy_adapter

        fid = getattr(MIV, "MIV_FAMILY_ID", "MIV_R")
        out["miv_not_in_strategy_family_ids"] = fid not in tuple(getattr(N, "STRATEGY_FAMILY_IDS", ()))
        out["miv_not_in_doctrine_ids"] = fid not in tuple(getattr(N, "DOCTRINE_IDS", ()))
        out["miv_not_in_replay_feature_families"] = fid not in tuple(getattr(feature_adapter, "REPLAY_FEATURE_FAMILIES", ()))
        out["miv_not_in_replay_strategy_families"] = fid not in tuple(getattr(strategy_adapter, "REPLAY_STRATEGY_FAMILIES", ()))
    except Exception as exc:
        out["errors"].append(repr(exc))
    return out


def main():
    hits = scan()
    imports = import_checks()

    hit_counts = {k: len(v) for k, v in hits.items()}
    top_files_by_category = {}
    for category, rows in hits.items():
        counts = defaultdict(int)
        for r in rows:
            counts[r["path"]] += 1
        top_files_by_category[category] = sorted(
            [{"path": p, "hits": c} for p, c in counts.items()],
            key=lambda x: (-x["hits"], x["path"])
        )[:25]

    required_categories = [
        "candidate_gate",
        "hold_gate",
        "runtime_disabled_gate",
        "consumer_safety_gate",
        "risk_shadow_gate",
        "execution_shadow_gate",
        "order_intent_ledger_gate",
        "miv_contract",
    ]

    checks = {
        "miv_contract_import_ok": imports["miv_contract_import_ok"] is True,
        "miv_not_active_production": imports["miv_active_production"] is False,
        "miv_research_shadow_only": imports["miv_research_shadow_only"] is True,
        "miv_not_in_strategy_family_ids": imports["miv_not_in_strategy_family_ids"] is True,
        "miv_not_in_doctrine_ids": imports["miv_not_in_doctrine_ids"] is True,
        "miv_not_in_replay_feature_families": imports["miv_not_in_replay_feature_families"] is True,
        "miv_not_in_replay_strategy_families": imports["miv_not_in_replay_strategy_families"] is True,
        "all_required_gate_categories_found": all(hit_counts.get(c, 0) > 0 for c in required_categories),
    }

    recommendations = [
        "Do not mutate MIST/MISB/MISC/MISR/MISO thresholds.",
        "Do not add MIV_R to active production registries in R1/R2.",
        "Build MIV-ZERODHA-LITE as replay/research-only evaluator first.",
        "Use existing risk_shadow/execution_shadow/order_intent surfaces only with research_shadow_only=true and broker_send_enabled=false.",
        "Neutral active labels must stay label-only and must not route to risk/execution/order-intent.",
        "Before any gate opening patch, freeze exact input/output adapter surface from this audit report.",
    ]

    classification = (
        "PASS_MIV_R1B_GATE_SURFACE_AUDIT_READY_FOR_R2_REPLAY_ONLY_EVALUATOR_PLAN"
        if all(checks.values())
        else "REVIEW_MIV_R1B_GATE_SURFACE_AUDIT_NEEDS_MANUAL_INSPECTION"
    )

    print(json.dumps({
        "batch": "LANE-MIV-R1B_GATE_SURFACE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER",
        "classification": classification,
        "created_at_epoch": time.time(),
        "checks": checks,
        "import_checks": imports,
        "hit_counts": hit_counts,
        "top_files_by_category": top_files_by_category,
        "sample_hits": {k: v[:20] for k, v in hits.items()},
        "recommendations": recommendations,
        "safety": {
            "source_patch": False,
            "replay_execution": False,
            "broker_order": False,
            "risk_service_start": False,
            "execution_service_start": False,
            "redis_delete": False,
            "lock_delete": False,
            "production_registry_change": False,
            "paper_live_enabled": False,
        },
        "git_status_short": git_status(),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
