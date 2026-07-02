#!/usr/bin/env python3
from __future__ import annotations

import gzip
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping

STREAM_ID_RE = re.compile(r"^[0-9]{13}-[0-9]+$")
FAMILIES = ["MIST", "MISB", "MISC", "MISR", "MISO"]

def safe_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in {"1", "true", "yes", "y", "on", "pass", "passed"}

def safe_float(v: Any, d: float = 0.0) -> float:
    try:
        if v in (None, ""):
            return d
        return float(v)
    except Exception:
        return d

def as_map(v: Any) -> dict[str, Any]:
    return dict(v) if isinstance(v, Mapping) else {}

def parse_redis_raw(path: Path):
    current_id = ""
    fields = {}
    pending_key = None

    def flush():
        nonlocal fields, current_id, pending_key
        if current_id or fields:
            out = dict(fields)
            out["_stream_id"] = current_id
            yield out
        fields = {}
        pending_key = None

    with gzip.open(path, "rt", errors="ignore") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if STREAM_ID_RE.match(line.strip()):
                yield from flush()
                current_id = line.strip()
                continue
            if pending_key is None:
                pending_key = line
            else:
                fields[pending_key] = line
                pending_key = None

    yield from flush()

def load_json_field(rec: dict[str, str], key: str):
    val = rec.get(key)
    if not val:
        return None
    try:
        return json.loads(val)
    except Exception:
        return None

def get_branch_obj(fam_obj: dict[str, Any], branch: str) -> dict[str, Any]:
    branches = as_map(fam_obj.get("branches"))
    candidates = []
    if branch == "CALL":
        candidates = ["CALL", "call"]
    else:
        candidates = ["PUT", "put"]

    for k in candidates:
        if isinstance(branches.get(k), Mapping):
            return dict(branches[k])
        if isinstance(fam_obj.get(k), Mapping):
            return dict(fam_obj[k])
    return {}

def failed_stage(obj: dict[str, Any], fam: str = "") -> str:
    fs = (
        obj.get("failed_stage")
        or obj.get("batch9_freeze_blocked_reason")
        or obj.get("pre_batch9_failed_stage")
        or obj.get("blocked_reason")
        or ""
    )
    if fs:
        return str(fs)

    # Fallback gate inference when older family_features_json has booleans only.
    if fam == "MIST":
        if obj.get("futures_bias_ok") is False or obj.get("trend_confirmed") is False or obj.get("trend_direction_ok") is False:
            return "futures_bias"
        if obj.get("futures_impulse_ok") is False:
            return "futures_impulse"
        if obj.get("pullback_detected") is False:
            return "pullback"
        if obj.get("resume_confirmed") is False:
            return "resume_confirmation"
    if fam == "MISB":
        if obj.get("shelf_confirmed") is False:
            return "shelf_validation"
        if obj.get("breakout_triggered") is False:
            return "breakout_trigger"
        if obj.get("breakout_accepted") is False:
            return "breakout_acceptance"
    if fam == "MISC":
        if obj.get("compression_detected") is False:
            return "compression_detection"
        if obj.get("directional_breakout_triggered") is False:
            return "directional_breakout"
        if obj.get("expansion_accepted") is False:
            return "expansion_acceptance"
    if fam == "MISR":
        if obj.get("active_zone_valid") is False:
            return "active_trap_zone_selection"
        if obj.get("fake_break_triggered") is False:
            return "fake_break_trigger"
        if obj.get("absorption_pass") is False:
            return "absorption"
        if obj.get("range_reentry_confirmed") is False:
            return "range_reentry"
        if obj.get("flow_flip_confirmed") is False:
            return "flow_flip"
    if fam == "MISO":
        if str(obj.get("mode", "")).upper() == "DISABLED":
            return "runtime_disabled"
        if obj.get("chain_context_ready") is False:
            return "miso_chain_context_not_ready"

    return "NO_FAILED_STAGE"

def compact_branch_snapshot(obj: dict[str, Any]) -> dict[str, Any]:
    keep = [
        "eligible", "branch_ready", "provider_ready", "setup_score",
        "trend_confirmed", "futures_bias_ok", "futures_impulse_ok",
        "trend_direction_ok", "pullback_detected", "resume_confirmed",
        "context_pass", "option_tradability_pass",
        "shelf_confirmed", "breakout_triggered", "breakout_accepted",
        "compression_detected", "directional_breakout_triggered", "expansion_accepted",
        "active_zone_valid", "fake_break_triggered", "absorption_pass",
        "range_reentry_confirmed", "flow_flip_confirmed",
        "mode", "chain_context_ready", "failed_stage", "passed_stages"
    ]
    return {k: obj.get(k) for k in keep if k in obj}

def walk(obj: Any):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for x in obj:
            yield from walk(x)

def main() -> int:
    if len(sys.argv) != 5:
        print("usage: SCRIPT features.redisraw.gz out_json out_md out_rows_jsonl", file=sys.stderr)
        return 2

    features_gz = Path(sys.argv[1])
    out_json = Path(sys.argv[2])
    out_md = Path(sys.argv[3])
    out_rows = Path(sys.argv[4])

    records_seen = 0
    parsed_json_fields = Counter()

    family_seen = Counter()
    family_eligible = Counter()
    family_branch_seen = Counter()
    family_branch_ready = Counter()
    family_branch_failed = Counter()

    mist_call_failed = Counter()
    mist_call_flags = defaultdict(Counter)
    mist_call_top = []

    rows = []

    mivr_hits = []
    mivr_key_counts = Counter()

    for rec in parse_redis_raw(features_gz):
        records_seen += 1

        roots = []
        ff = load_json_field(rec, "family_features_json")
        fs = load_json_field(rec, "family_surfaces_json")

        if isinstance(ff, Mapping):
            roots.append(("family_features_json", dict(ff)))
            parsed_json_fields["family_features_json"] += 1
        if isinstance(fs, Mapping):
            roots.append(("family_surfaces_json", dict(fs)))
            parsed_json_fields["family_surfaces_json"] += 1

        for source, root in roots:
            # Optional MIV-R search.
            if "MIV" in json.dumps(root, default=str).upper():
                for obj in walk(root):
                    if not isinstance(obj, Mapping):
                        continue
                    fid = str(obj.get("family_id") or obj.get("doctrine_id") or obj.get("profile_id") or "")
                    if "MIV" in fid.upper():
                        hit = {
                            "source": source,
                            "stream_id": rec.get("_stream_id"),
                            "family_id": fid,
                            "eligible": obj.get("eligible"),
                            "failed_stage": obj.get("failed_stage"),
                            "score": obj.get("setup_score") or obj.get("score") or obj.get("score_total"),
                            "keys": sorted(list(obj.keys()))[:80],
                        }
                        mivr_hits.append(hit)
                        for k in obj.keys():
                            mivr_key_counts[k] += 1

            families = as_map(root.get("families"))
            if not families:
                continue

            for fam in FAMILIES:
                fam_obj = as_map(families.get(fam))
                if not fam_obj:
                    continue

                family_seen[fam] += 1
                if safe_bool(fam_obj.get("eligible")):
                    family_eligible[fam] += 1

                if fam == "MISO":
                    root_stage = failed_stage(fam_obj, fam)
                    family_branch_failed[(fam, "ROOT", root_stage)] += 1

                for branch in ["CALL", "PUT"]:
                    b = get_branch_obj(fam_obj, branch)
                    if not b:
                        continue

                    fs1 = failed_stage(b, fam)
                    ready = safe_bool(b.get("eligible")) or safe_bool(b.get("branch_ready"))
                    score = safe_float(b.get("setup_score"), 0.0)

                    family_branch_seen[(fam, branch)] += 1
                    family_branch_failed[(fam, branch, fs1)] += 1
                    if ready:
                        family_branch_ready[(fam, branch)] += 1

                    row = {
                        "source": source,
                        "stream_id": rec.get("_stream_id"),
                        "family": fam,
                        "branch": branch,
                        "failed_stage": fs1,
                        "ready_or_eligible": ready,
                        "setup_score": score,
                        "snapshot": compact_branch_snapshot(b),
                    }
                    rows.append(row)

                    if fam == "MIST" and branch == "CALL":
                        mist_call_failed[fs1] += 1
                        snap = compact_branch_snapshot(b)
                        for k, v in snap.items():
                            if isinstance(v, bool):
                                mist_call_flags[k][str(v)] += 1
                        mist_call_top.append(row)

    mist_call_top = sorted(mist_call_top, key=lambda x: safe_float(x.get("setup_score"), 0.0), reverse=True)[:40]

    top_blockers = [
        {"family": fam, "branch": br, "failed_stage": st, "count": c}
        for (fam, br, st), c in family_branch_failed.most_common(100)
    ]

    result = {
        "schema": "r38ar_r2_candidate_suppression_multi_family_mivr_audit_v1",
        "features_source": str(features_gz),
        "records_seen": records_seen,
        "parsed_json_fields": dict(parsed_json_fields),
        "family_seen": dict(family_seen),
        "family_eligible": dict(family_eligible),
        "family_branch_seen": {str(k): v for k, v in family_branch_seen.items()},
        "family_branch_ready": {str(k): v for k, v in family_branch_ready.items()},
        "top_blockers": top_blockers,
        "mist_call_suppression": {
            "failed_stage_counts": dict(mist_call_failed),
            "boolean_gate_counts": {k: dict(v) for k, v in mist_call_flags.items()},
            "top_rows_by_setup_score": mist_call_top,
            "interpretation": "MIST/CALL candidate_count=0 means branch never became ready/eligible; see failed_stage_counts and boolean_gate_counts."
        },
        "mivr_optional": {
            "hit_count": len(mivr_hits),
            "key_counts": dict(mivr_key_counts.most_common(80)),
            "sample_hits": mivr_hits[:30],
            "interpretation": "hit_count=0 means no MIV-R family surface was present in today’s sealed features file."
        },
        "safety": {
            "read_only": True,
            "patch_attempted": False,
            "service_start_attempted": False,
            "replay_started": False,
            "paper_started": False,
            "live_started": False,
            "order_attempted": False,
            "redis_write_attempted": False,
            "redis_delete_attempted": False
        }
    }

    out_json.write_text(json.dumps(result, indent=2, sort_keys=True, default=str), encoding="utf-8")
    with out_rows.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True, default=str) + "\n")

    md = []
    md.append("# R38AR-R2 candidate suppression + multi-family + optional MIV-R audit")
    md.append("")
    md.append(f"- features_source: `{features_gz}`")
    md.append(f"- records_seen: `{records_seen}`")
    md.append(f"- parsed_json_fields: `{dict(parsed_json_fields)}`")
    md.append("")
    md.append("## 1. Why MIST/CALL stayed candidate_count=0")
    md.append("")
    md.append(f"- failed_stage_counts: `{dict(mist_call_failed)}`")
    md.append(f"- boolean_gate_counts: `{ {k: dict(v) for k, v in mist_call_flags.items()} }`")
    md.append("")
    md.append("Interpretation: MIST/CALL did not become branch_ready/eligible. Do not loosen MIST/CALL directly because prior R38AP economics showed CALL-side near rows were weak.")
    md.append("")
    md.append("## 2. Multi-family blocker audit")
    md.append("")
    for x in top_blockers[:50]:
        md.append(f"- {x['family']}/{x['branch']} failed_stage={x['failed_stage']} count={x['count']}")
    md.append("")
    md.append("## 3. Optional MIV-R research evaluation")
    md.append("")
    md.append(f"- mivr_hit_count: `{len(mivr_hits)}`")
    if mivr_hits:
        md.append("- MIV-R-like surfaces found. Inspect summary JSON sample_hits.")
    else:
        md.append("- No MIV-R surface found in today’s sealed features file.")
    md.append("")
    md.append("## Safety")
    md.append("")
    md.append("- read_only: `true`")
    md.append("- patch_attempted: `false`")
    md.append("- replay_started: `false`")
    md.append("- paper/live/order: `false`")

    out_md.write_text("\n".join(md), encoding="utf-8")

    print("records_seen=" + str(records_seen))
    print("parsed_json_fields=" + json.dumps(dict(parsed_json_fields), sort_keys=True))
    print("mist_call_failed_stage_counts=" + json.dumps(dict(mist_call_failed), sort_keys=True))
    print("top_blockers=" + json.dumps(top_blockers[:30], sort_keys=True))
    print("mivr_hit_count=" + str(len(mivr_hits)))
    print("out_json=" + str(out_json))
    print("out_md=" + str(out_md))
    print("out_rows=" + str(out_rows))
    print("")
    print("\n".join(md[:140]))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
