#!/usr/bin/env python3
from __future__ import annotations

import json, re, subprocess, sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping

STREAM_ID_RE = re.compile(r"^[0-9]{13}-[0-9]+$")

FAMILIES = ["MIST", "MISB", "MISC", "MISR", "MISO"]
BRANCHES = ["CALL", "PUT"]

def as_map(v: Any) -> dict[str, Any]:
    return dict(v) if isinstance(v, Mapping) else {}

def truth(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in {"1", "true", "yes", "pass", "passed", "ok"}

def fnum(v: Any, d: float = 0.0) -> float:
    try:
        if v in (None, ""):
            return d
        return float(v)
    except Exception:
        return d

def parse_stream_raw(lines: list[str]):
    recs = []
    cur_id = None
    fields = {}
    pending = None
    for line in lines:
        line = line.rstrip("\n")
        if STREAM_ID_RE.match(line):
            if cur_id is not None:
                recs.append((cur_id, fields))
            cur_id = line
            fields = {}
            pending = None
            continue
        if cur_id is None:
            continue
        if pending is None:
            pending = line
        else:
            fields[pending] = line
            pending = None
    if cur_id is not None:
        recs.append((cur_id, fields))
    return recs

def load_json(fields: dict[str, str], key: str):
    val = fields.get(key)
    if not val:
        return None
    try:
        return json.loads(val)
    except Exception:
        return None

def get_family(root: Mapping[str, Any], fam: str) -> dict[str, Any]:
    families = as_map(root.get("families"))
    if isinstance(families.get(fam), Mapping):
        return dict(families[fam])
    if isinstance(root.get(fam), Mapping):
        return dict(root[fam])
    return {}

def get_branch(fam_obj: Mapping[str, Any], branch: str) -> dict[str, Any]:
    branches = as_map(fam_obj.get("branches"))
    for k in [branch, branch.lower()]:
        if isinstance(branches.get(k), Mapping):
            return dict(branches[k])
        if isinstance(fam_obj.get(k), Mapping):
            return dict(fam_obj[k])
    if branch == "CALL" and isinstance(fam_obj.get("call"), Mapping):
        return dict(fam_obj["call"])
    if branch == "PUT" and isinstance(fam_obj.get("put"), Mapping):
        return dict(fam_obj["put"])
    return {}

def failed_stage(obj: Mapping[str, Any]) -> str:
    return str(
        obj.get("failed_stage")
        or obj.get("batch9_freeze_blocked_reason")
        or obj.get("pre_batch9_failed_stage")
        or obj.get("blocked_reason")
        or "NO_FAILED_STAGE"
    )

def setup_score(obj: Mapping[str, Any]) -> float:
    return max(
        fnum(obj.get("setup_score"), 0.0),
        fnum(obj.get("score"), 0.0),
        fnum(obj.get("score_total"), 0.0),
        fnum(obj.get("candidate_score"), 0.0),
    )

def main() -> int:
    out_json = Path(sys.argv[1])
    out_md = Path(sys.argv[2])
    count = sys.argv[3] if len(sys.argv) > 3 else "800"

    cmd = ["redis-cli", "--raw", "xrevrange", "features:mme:stream", "+", "-", "COUNT", count]
    p = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines = p.stdout.splitlines()
    recs = parse_stream_raw(lines)

    family_branch_counts = Counter()
    eligible_counts = Counter()
    ready_counts = Counter()
    stage_counts = Counter()
    shadow_counts = Counter()
    top = defaultdict(list)

    parsed = Counter()
    rows_seen = 0

    for sid, fields in recs:
        for source_key in ["family_surfaces_json", "family_features_json"]:
            root = load_json(fields, source_key)
            if not isinstance(root, Mapping):
                continue
            parsed[source_key] += 1

            for fam in FAMILIES:
                fam_obj = get_family(root, fam)
                if not fam_obj:
                    continue

                branches_to_check = BRANCHES if fam != "MISO" else ["ROOT", "CALL", "PUT"]
                for branch in branches_to_check:
                    if branch == "ROOT":
                        obj = fam_obj
                    else:
                        obj = get_branch(fam_obj, branch)
                    if not obj:
                        continue

                    rows_seen += 1
                    key = (fam, branch)
                    family_branch_counts[key] += 1

                    elig = truth(obj.get("eligible"))
                    ready = truth(obj.get("branch_ready")) or truth(obj.get("ready"))
                    if elig:
                        eligible_counts[key] += 1
                    if ready:
                        ready_counts[key] += 1

                    fs = failed_stage(obj)
                    stage_counts[(fam, branch, fs)] += 1

                    if truth(obj.get("compression_detected_shadow")) or truth(obj.get("compression_width_ok_shadow")):
                        shadow_counts[key] += 1

                    row = {
                        "stream_id": sid,
                        "source": source_key,
                        "family": fam,
                        "branch": branch,
                        "eligible": elig,
                        "branch_ready": ready,
                        "failed_stage": fs,
                        "setup_score": setup_score(obj),
                        "provider_ready": obj.get("provider_ready"),
                        "option_tradability_pass": obj.get("option_tradability_pass"),
                        "compression_detected_shadow": obj.get("compression_detected_shadow"),
                        "compression_width_ok_shadow": obj.get("compression_width_ok_shadow"),
                        "passed_stages": obj.get("passed_stages"),
                    }
                    top[key].append(row)

    top_out = {}
    for key, vals in top.items():
        vals = sorted(vals, key=lambda r: r["setup_score"], reverse=True)[:10]
        top_out[str(key)] = vals

    current_possible = {
        str(k): {
            "eligible_rows": eligible_counts.get(k, 0),
            "ready_rows": ready_counts.get(k, 0),
            "paper_candidate_possible_now": eligible_counts.get(k, 0) > 0,
        }
        for k in family_branch_counts
    }

    result = {
        "schema": "r38ba_all_strategy_both_side_live_shadow_gate_v1",
        "features_rows_sampled": len(recs),
        "parsed": dict(parsed),
        "family_surface_rows_seen": rows_seen,
        "family_branch_counts": {str(k): v for k, v in family_branch_counts.items()},
        "eligible_counts": {str(k): v for k, v in eligible_counts.items()},
        "ready_counts": {str(k): v for k, v in ready_counts.items()},
        "shadow_counts": {str(k): v for k, v in shadow_counts.items()},
        "failed_stage_counts_top": {str(k): v for k, v in stage_counts.most_common(80)},
        "top_rows_by_score": top_out,
        "current_possible": current_possible,
        "decision": {
            "all_strategy_paper_allowed": False,
            "why": "This gate is shadow-only. It only identifies if any family/side is live-eligible. Paper requires separate whitelist gate.",
            "next_if_any_eligible": "Run controlled micro-paper whitelist gate for one eligible family/side only.",
            "next_if_none_eligible": "Continue observe-only capture and fix family blockers."
        },
        "safety": {
            "read_only": True,
            "paper_started": False,
            "live_started": False,
            "risk_started": False,
            "execution_started": False,
            "order_attempted": False,
            "redis_delete_attempted": False
        }
    }

    out_json.write_text(json.dumps(result, indent=2, sort_keys=True, default=str), encoding="utf-8")

    md = []
    md.append("# R38BA all-strategy both-side live shadow gate")
    md.append("")
    md.append(f"- features_rows_sampled: `{len(recs)}`")
    md.append(f"- parsed: `{dict(parsed)}`")
    md.append(f"- family_surface_rows_seen: `{rows_seen}`")
    md.append("")
    md.append("## Eligible counts")
    md.append(f"`{ {str(k): v for k, v in eligible_counts.items()} }`")
    md.append("")
    md.append("## Ready counts")
    md.append(f"`{ {str(k): v for k, v in ready_counts.items()} }`")
    md.append("")
    md.append("## Shadow counts")
    md.append(f"`{ {str(k): v for k, v in shadow_counts.items()} }`")
    md.append("")
    md.append("## Top failed stages")
    md.append(f"`{ {str(k): v for k, v in stage_counts.most_common(40)} }`")
    md.append("")
    md.append("## Decision")
    md.append("- all_strategy_paper_allowed: `false`")
    md.append("- this is all-family, both-side live shadow visibility only")
    md.append("- if any family/side becomes eligible, use a separate one-family/one-side controlled micro-paper gate")
    out_md.write_text("\n".join(md), encoding="utf-8")

    print(json.dumps({
        "features_rows_sampled": len(recs),
        "parsed": dict(parsed),
        "family_surface_rows_seen": rows_seen,
        "eligible_counts": {str(k): v for k, v in eligible_counts.items()},
        "ready_counts": {str(k): v for k, v in ready_counts.items()},
        "shadow_counts": {str(k): v for k, v in shadow_counts.items()},
    }, indent=2, sort_keys=True))
    print("out_json=" + str(out_json))
    print("out_md=" + str(out_md))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
