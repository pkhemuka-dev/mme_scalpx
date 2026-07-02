
from __future__ import annotations

# LANE-X-R32I_AUTO_MATERIALIZE_INTERNAL_ORDER_INTENT_FROM_REPLAY_RESULTS_NO_BROKER_NO_ORDER
# Reads existing replay strategy_decisions artifacts and writes R32D/R32G internal ledgers.
# No replay start. No Redis writes. No broker transport.

import ast
import argparse
import gzip
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Iterable, Mapping

from app.mme_scalpx.services.strategy_family.internal_order_intent_pipeline import (
    BrokerTransportHardBlocked,
    InternalPipelineConfig,
    run_internal_order_intent_pipeline,
)

MATERIALIZER_VERSION = "r32i_replay_results_to_internal_order_intent_materializer_v1"


def sh(cmd: str) -> str:
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def truth(v: Any) -> bool:
    return str(v or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def num(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return default


def load_json_any(path: Path) -> Any:
    try:
        if path.suffix == ".gz":
            with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
                return json.load(f)
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def iter_json_rows(path: Path) -> Iterable[dict[str, Any]]:
    data = load_json_any(path)
    if isinstance(data, list):
        for row in data:
            if isinstance(row, dict):
                yield row
        return
    if isinstance(data, dict):
        for key in ("rows", "results", "strategy", "candidates", "records", "data"):
            v = data.get(key)
            if isinstance(v, list):
                for row in v:
                    if isinstance(row, dict):
                        yield row
                return
        yield data
        return

    opener = gzip.open if path.suffix == ".gz" else open
    try:
        with opener(path, "rt", encoding="utf-8", errors="replace") as f:
            for line in f:
                s = line.strip()
                if not s or not s.startswith("{"):
                    continue
                try:
                    row = json.loads(s)
                    if isinstance(row, dict):
                        yield row
                except Exception:
                    continue
    except Exception:
        return


def candidate_truth(row: Mapping[str, Any]) -> bool:
    if truth(row.get("candidate_present")) or truth(row.get("eligible")):
        return True
    if int(num(row.get("strict_candidate_count"), 0)) > 0:
        return True
    if truth(row.get("surface_available")) and num(row.get("score"), 0.0) > 0:
        return True
    if num(row.get("score"), 0.0) > 0 and (
        row.get("side") or row.get("side_fallback") or row.get("selected_leg") or row.get("selected_leg_fallback")
    ):
        return True
    return False


def side_from(row: Mapping[str, Any]) -> str:
    side = str(
        row.get("side")
        or row.get("side_fallback")
        or row.get("option_side")
        or row.get("selected_leg")
        or row.get("selected_leg_fallback")
        or row.get("linked_feature_side")
        or ""
    ).upper()
    if side in {"CE"}:
        return "CALL"
    if side in {"PE"}:
        return "PUT"
    if side in {"CALL", "PUT"}:
        return side

    symbol = str(row.get("symbol") or row.get("trading_symbol") or row.get("option_symbol") or "").upper()
    if symbol.endswith("CE"):
        return "CALL"
    if symbol.endswith("PE"):
        return "PUT"
    return side


def normalize_replay_strategy_row(row: Mapping[str, Any], *, source_path: Path, source_index: int) -> dict[str, Any] | None:
    if not candidate_truth(row):
        return None

    side = side_from(row)
    if side not in {"CALL", "PUT"}:
        return None

    symbol = str(
        row.get("symbol")
        or row.get("trading_symbol")
        or row.get("option_symbol")
        or row.get("instrument_key")
        or ""
    )
    if not symbol:
        return None

    action = str(row.get("action") or row.get("decision_action") or row.get("risk_action") or "HOLD").upper()

    return {
        "source": "r32i_replay_strategy_decisions_materializer",
        "source_path": str(source_path),
        "source_index": source_index,
        "materializer_version": MATERIALIZER_VERSION,
        "family_id": str(row.get("family_id") or row.get("family") or row.get("strategy_family") or "UNKNOWN"),
        "side": side,
        "action": action,
        "symbol": symbol,
        "qty": int(num(row.get("qty", row.get("quantity", 75)), 75)),
        "price": num(row.get("price", row.get("ltp", row.get("mid_price", row.get("entry_price", 0.0)))), 0.0),
        "score": num(row.get("score", row.get("candidate_score", row.get("activation_score", 0.0))), 0.0),
        "candidate_present": row.get("candidate_present"),
        "eligible": row.get("eligible"),
        "strict_candidate_count": row.get("strict_candidate_count"),
        "source_action": action,
        "raw_keys": sorted(str(k) for k in row.keys())[:160],
    }


def discover_latest_strategy_decisions() -> Path | None:
    # Prefer latest R32E-discovered R9X artifact if present.
    r32e_dir = sh("ls -1dt run/audits/LANE-X-R32E_REAL_CANDIDATE_TO_INTERNAL_ORDER_INTENT_BRIDGE_NO_PATCH_NO_REPLAY_NO_ORDER_* 2>/dev/null | head -1")
    if r32e_dir:
        discovery = Path(r32e_dir) / "r9x_discovery.txt"
        if discovery.exists():
            for line in discovery.read_text(encoding="utf-8", errors="replace").splitlines():
                if "path=" in line and "strategy_decisions.json" in line:
                    p = Path(line.split("path=", 1)[1].strip())
                    if p.exists():
                        return p

    # Fallback scan.
    hits = sh("find run/replay -path '*artifacts/strategy_decisions.json' -type f 2>/dev/null | sort | tail -1")
    return Path(hits) if hits else None


def forbidden_call_names(path: Path) -> list[str]:
    bad = []
    forbidden = {"place_order", "send_order", "modify_order", "cancel_order"}
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return ["AST_PARSE_FAILED"]
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Attribute) and fn.attr in forbidden:
                bad.append(fn.attr)
            if isinstance(fn, ast.Name) and fn.id in forbidden:
                bad.append(fn.id)
    return sorted(set(bad))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="", help="Replay strategy_decisions.json path. If empty, auto-discovers latest.")
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--proof", required=True)
    parser.add_argument("--limit", type=int, default=200)
    args = parser.parse_args()

    source_path = Path(args.input) if args.input else discover_latest_strategy_decisions()
    outdir = Path(args.outdir)
    proof_path = Path(args.proof)

    orders_before = sh("redis-cli XLEN orders")
    risk_before = sh("redis-cli XLEN risk")
    execution_before = sh("redis-cli XLEN execution")

    candidates = []
    if source_path and source_path.exists():
        for idx, row in enumerate(iter_json_rows(source_path)):
            c = normalize_replay_strategy_row(row, source_path=source_path, source_index=idx)
            if c:
                candidates.append(c)
            if len(candidates) >= args.limit:
                break

    result = None
    if candidates:
        result = run_internal_order_intent_pipeline(
            candidates,
            outdir=outdir / "internal_ledgers",
            config=InternalPipelineConfig(default_qty=75, max_qty=75),
            env={
                "SCALPX_OBSERVE_ONLY": "1",
                "SCALPX_ENABLE_LIVE": "",
                "SCALPX_ENABLE_PAPER": "",
                "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME": "",
                "SCALPX_CONTROLLED_PAPER_SCOPE_ACK": "",
            },
        )
        summary = result["summary"]
    else:
        summary = {
            "candidate_intent_count": 0,
            "risk_accept_shadow_count": 0,
            "risk_reject_shadow_count": 0,
            "execution_sim_filled_count": 0,
            "order_intent_recorded_count": 0,
            "would_have_order_count": 0,
            "real_order_sent_count": 0,
            "broker_calls_executed_count": 0,
            "broker_transport_block_reason": "NO_CANDIDATES_MATERIALIZED",
        }

    dangerous_env_blocked = False
    try:
        if candidates:
            run_internal_order_intent_pipeline(
                candidates[:1],
                outdir=outdir / "dangerous_env_should_not_write",
                env={"SCALPX_ENABLE_LIVE": "1"},
            )
    except BrokerTransportHardBlocked:
        dangerous_env_blocked = True

    orders_after = sh("redis-cli XLEN orders")
    risk_after = sh("redis-cli XLEN risk")
    execution_after = sh("redis-cli XLEN execution")

    self_forbidden = forbidden_call_names(Path(__file__))

    safety_ok = (
        orders_before == "0"
        and risk_before == "0"
        and execution_before == "0"
        and orders_after == "0"
        and risk_after == "0"
        and execution_after == "0"
    )

    pass_ok = (
        safety_ok
        and bool(candidates)
        and summary.get("risk_accept_shadow_count", 0) > 0
        and summary.get("execution_sim_filled_count", 0) > 0
        and summary.get("would_have_order_count", 0) > 0
        and summary.get("real_order_sent_count") == 0
        and summary.get("broker_calls_executed_count") == 0
        and dangerous_env_blocked
        and not self_forbidden
    )

    classification = (
        "PASS_R32I_REPLAY_RESULTS_AUTO_MATERIALIZED_INTERNAL_ORDER_INTENT_NO_BROKER_NO_ORDER"
        if pass_ok
        else "REVIEW_R32I_REPLAY_RESULTS_MATERIALIZER_INCOMPLETE_NO_BROKER_NO_ORDER"
    )

    proof = {
        "classification": classification,
        "materializer_version": MATERIALIZER_VERSION,
        "source_path": str(source_path) if source_path else "",
        "candidate_count_materialized": len(candidates),
        "summary": summary,
        "dangerous_env_blocked": dangerous_env_blocked,
        "forbidden_broker_call_names_in_materializer": self_forbidden,
        "orders_before": orders_before,
        "risk_before": risk_before,
        "execution_before": execution_before,
        "orders_after": orders_after,
        "risk_after": risk_after,
        "execution_after": execution_after,
        "outdir": str(outdir),
        "patch_applied": True,
        "replay_started": False,
        "broker_order_attempted": False,
        "risk_service_started": False,
        "execution_service_started": False,
        "redis_delete_attempted": False,
        "lock_delete_attempted": False,
    }
    proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0 if pass_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
