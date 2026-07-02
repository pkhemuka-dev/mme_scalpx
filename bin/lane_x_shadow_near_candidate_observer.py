#!/usr/bin/env python3
"""
Lane X shadow near-candidate observer.

Diagnostic only.
- Does not create production candidates.
- Does not change thresholds.
- Does not write Redis.
- Does not start risk/execution/paper/order paths.
- Can read latest Redis decision payload or R10/R11 sampler CSVs.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path
from typing import Any, Mapping


FAMILIES = ("MIST", "MISB", "MISC", "MISR", "MISO")
SIDES = ("CALL", "PUT")

WEAK = 0.35
MEDIUM = 0.45
STRONG = 0.55


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def _as_json(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return value
    if not isinstance(value, str) or not value.strip():
        return {}
    try:
        return json.loads(value)
    except Exception:
        return {}


def _latest_redis_map(stream: str) -> dict[str, str]:
    try:
        raw = subprocess.check_output(
            ["redis-cli", "--raw", "XREVRANGE", stream, "+", "-", "COUNT", "1"],
            text=True,
            errors="replace",
        )
    except Exception:
        return {}
    lines = raw.splitlines()
    out: dict[str, str] = {}
    for i in range(1, len(lines) - 1, 2):
        out[lines[i]] = lines[i + 1]
    return out


def _band(score: float) -> str:
    if score >= STRONG:
        return "shadow_strong_near_candidate"
    if score >= MEDIUM:
        return "shadow_medium_near_candidate"
    if score >= WEAK:
        return "shadow_weak_near_candidate"
    return ""


def _gap(score: float, min_score: float) -> float | None:
    if min_score <= 0:
        return None
    return max(0.0, min_score - score)


def _branch_from_family(fam: Mapping[str, Any], side: str) -> Mapping[str, Any]:
    return (
        fam.get(side)
        or fam.get(side.lower())
        or (fam.get("branches") or {}).get(side)
        or (fam.get("branches") or {}).get(side.lower())
        or {}
    )


def _extract_families_from_latest_decision() -> tuple[dict[str, Any], dict[str, Any]]:
    decision = _latest_redis_map("decisions:mme:stream")
    payload = _as_json(decision.get("payload_json"))
    consumer = _as_json(payload.get("consumer_view_json"))

    fs_wrap = consumer.get("family_surfaces") or payload.get("family_surfaces") or {}
    families = fs_wrap.get("families") if isinstance(fs_wrap, dict) else {}
    if not isinstance(families, dict) or not families:
        families = fs_wrap if isinstance(fs_wrap, dict) else {}

    return payload if isinstance(payload, dict) else {}, families if isinstance(families, dict) else {}


def _rows_from_families(payload: Mapping[str, Any], families: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fid in FAMILIES:
        fam = families.get(fid) or families.get(fid.lower()) or {}
        if not isinstance(fam, Mapping):
            continue
        for side in SIDES:
            b = _branch_from_family(fam, side)
            if not isinstance(b, Mapping) or not b:
                continue

            score = _safe_float(
                b.get("setup_score", b.get("score", b.get("trend_score", 0.0))),
                0.0,
            )
            min_score = _safe_float(
                b.get("min_score", b.get("required_score", b.get("threshold_score", 0.0))),
                0.0,
            )

            band = _band(score)
            gap = _gap(score, min_score)

            rows.append({
                "source": "redis_latest",
                "decision_id": payload.get("decision_id", ""),
                "activation_reason": payload.get("activation_reason", ""),
                "family": fid,
                "side": side,
                "score": score,
                "min_score": min_score,
                "score_gap": gap,
                "shadow_band": band,
                "shadow_candidate_like": bool(band),
                "failed_stage": b.get("failed_stage", ""),
                "blocker": b.get("blocked_reason", b.get("batch9_freeze_blocked_reason", "")),
                "production_candidate": False,
                "no_production_effect": True,
            })
    return rows


def _rows_from_csv(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(newline="") as f:
        for r in csv.DictReader(f):
            score = _safe_float(r.get("score"), 0.0)
            min_score = _safe_float(r.get("min_score"), 0.0)
            band = _band(score)
            rows.append({
                "source": str(path),
                "decision_id": r.get("decision_id", ""),
                "activation_reason": r.get("activation_reason", ""),
                "family": r.get("family", ""),
                "side": r.get("side", ""),
                "score": score,
                "min_score": min_score,
                "score_gap": _gap(score, min_score),
                "shadow_band": band,
                "shadow_candidate_like": bool(band),
                "failed_stage": r.get("failed_stage", ""),
                "blocker": r.get("blocker", ""),
                "production_candidate": False,
                "no_production_effect": True,
            })
    return rows


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    near = [r for r in rows if r.get("shadow_candidate_like")]
    top = sorted(rows, key=lambda r: _safe_float(r.get("score"), 0.0), reverse=True)[:10]
    bands: dict[str, int] = {}
    fams: dict[str, int] = {}
    for r in near:
        bands[str(r.get("shadow_band") or "")] = bands.get(str(r.get("shadow_band") or ""), 0) + 1
        key = f"{r.get('family')}:{r.get('side')}"
        fams[key] = fams.get(key, 0) + 1

    return {
        "row_count": len(rows),
        "near_candidate_count": len(near),
        "band_counts": bands,
        "family_side_counts": fams,
        "top": top,
        "production_candidate_created": False,
        "order_allowed": False,
        "risk_allowed": False,
        "execution_allowed": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", action="append", default=[])
    ap.add_argument("--json-out", default="")
    ap.add_argument("--print-table", action="store_true")
    args = ap.parse_args()

    rows: list[dict[str, Any]] = []

    if args.csv:
        for item in args.csv:
            p = Path(item)
            if p.exists():
                rows.extend(_rows_from_csv(p))
    else:
        payload, families = _extract_families_from_latest_decision()
        rows.extend(_rows_from_families(payload, families))

    summary = _summary(rows)
    result = {"summary": summary, "rows": rows}

    if args.print_table:
        print("family | side | score | min_score | gap | shadow_band | failed_stage | blocker")
        for r in summary["top"]:
            print(
                f"{r.get('family')} | {r.get('side')} | {r.get('score')} | "
                f"{r.get('min_score')} | {r.get('score_gap')} | {r.get('shadow_band')} | "
                f"{r.get('failed_stage')} | {r.get('blocker')}"
            )
    print(json.dumps(result, indent=2, sort_keys=True))

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(result, indent=2, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
