#!/usr/bin/env python3
from __future__ import annotations

import gzip, json, re, statistics, sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping

STREAM_ID_RE = re.compile(r"^[0-9]{13}-[0-9]+$")

def safe_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in {"1","true","yes","y","on","pass","passed"}

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
    pending = None

    def flush():
        nonlocal current_id, fields, pending
        if current_id or fields:
            out = dict(fields)
            out["_stream_id"] = current_id
            yield out
        fields = {}
        pending = None

    with gzip.open(path, "rt", errors="ignore") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if STREAM_ID_RE.match(line.strip()):
                yield from flush()
                current_id = line.strip()
                continue
            if pending is None:
                pending = line
            else:
                fields[pending] = line
                pending = None
    yield from flush()

def load_json_field(rec: dict[str,str], key: str):
    val = rec.get(key)
    if not val:
        return None
    try:
        return json.loads(val)
    except Exception:
        return None

def get_branch(fam: dict[str,Any], branch: str):
    branches = as_map(fam.get("branches"))
    for k in [branch, branch.lower()]:
        if isinstance(branches.get(k), Mapping):
            return dict(branches[k])
        if isinstance(fam.get(k), Mapping):
            return dict(fam[k])
    return {}

def failed_stage(obj: dict[str,Any]) -> str:
    return str(
        obj.get("failed_stage")
        or obj.get("batch9_freeze_blocked_reason")
        or obj.get("pre_batch9_failed_stage")
        or obj.get("blocked_reason")
        or "NO_FAILED_STAGE"
    )

def walk_keys(obj: Any, prefix: str = ""):
    found = {}
    if isinstance(obj, Mapping):
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else str(k)
            lk = str(k).lower()
            if any(x in lk for x in ["compression","squeeze","narrow","range","atr","volatility","expansion"]):
                if not isinstance(v, (dict, list)):
                    found[path] = v
            if isinstance(v, (dict, list)):
                found.update(walk_keys(v, path))
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:20]):
            found.update(walk_keys(v, f"{prefix}[{i}]"))
    return found

def stats(vals):
    if not vals:
        return {"count": 0}
    return {
        "count": len(vals),
        "avg": round(sum(vals)/len(vals), 6),
        "median": round(statistics.median(vals), 6),
        "min": round(min(vals), 6),
        "max": round(max(vals), 6),
    }

def main() -> int:
    if len(sys.argv) != 5:
        print("usage: script features.redisraw.gz out_json out_md out_rows", file=sys.stderr)
        return 2

    features_gz = Path(sys.argv[1])
    out_json = Path(sys.argv[2])
    out_md = Path(sys.argv[3])
    out_rows = Path(sys.argv[4])

    records_seen = 0
    parsed_json_fields = Counter()
    rows = []

    branch_counts = Counter()
    stage_counts = Counter()
    bool_counts = defaultdict(Counter)
    nested_key_counts = Counter()
    numeric_values = defaultdict(list)

    for rec in parse_redis_raw(features_gz):
        records_seen += 1

        for source_key in ["family_features_json", "family_surfaces_json"]:
            root = load_json_field(rec, source_key)
            if not isinstance(root, Mapping):
                continue
            parsed_json_fields[source_key] += 1

            families = as_map(root.get("families"))
            misc = as_map(families.get("MISC"))
            if not misc:
                continue

            for branch in ["CALL", "PUT"]:
                b = get_branch(misc, branch)
                if not b:
                    continue

                nested = walk_keys(b)
                fs = failed_stage(b)

                row = {
                    "source": source_key,
                    "stream_id": rec.get("_stream_id"),
                    "family": "MISC",
                    "branch": branch,
                    "failed_stage": fs,
                    "eligible": safe_bool(b.get("eligible")),
                    "branch_ready": safe_bool(b.get("branch_ready")),
                    "provider_ready": b.get("provider_ready"),
                    "option_tradability_pass": b.get("option_tradability_pass"),
                    "compression_detected": b.get("compression_detected"),
                    "directional_breakout_triggered": b.get("directional_breakout_triggered"),
                    "expansion_accepted": b.get("expansion_accepted"),
                    "setup_score": safe_float(b.get("setup_score"), 0.0),
                    "passed_stages": b.get("passed_stages"),
                    "nested_compression_keys": nested,
                }
                rows.append(row)

                branch_counts[branch] += 1
                stage_counts[(branch, fs)] += 1

                for k, v in row.items():
                    if isinstance(v, bool):
                        bool_counts[k][str(v)] += 1

                for k, v in nested.items():
                    nested_key_counts[k] += 1
                    if isinstance(v, (int, float)):
                        numeric_values[k].append(float(v))
                    else:
                        try:
                            numeric_values[k].append(float(v))
                        except Exception:
                            pass

    out_rows.parent.mkdir(parents=True, exist_ok=True)
    with out_rows.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True, default=str) + "\n")

    top_rows = sorted(rows, key=lambda r: safe_float(r.get("setup_score"), 0.0), reverse=True)[:40]

    summary = {
        "schema": "r38au_r2_misc_compression_diagnostic_v1",
        "features_source": str(features_gz),
        "records_seen": records_seen,
        "parsed_json_fields": dict(parsed_json_fields),
        "misc_rows": len(rows),
        "branch_counts": dict(branch_counts),
        "stage_counts": {str(k): v for k, v in stage_counts.items()},
        "boolean_counts": {k: dict(v) for k, v in bool_counts.items()},
        "nested_compression_key_counts": dict(nested_key_counts.most_common(80)),
        "numeric_key_stats": {k: stats(v) for k, v in numeric_values.items()},
        "top_rows_by_setup_score": top_rows,
        "diagnosis": {
            "goal": "Decide whether MISC compression_detection is real no-setup, missing feature, or over-strict logic.",
            "patch_decision_now": False,
            "candidate_route_allowed": False,
            "paper_allowed": False,
            "live_allowed": False
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

    out_json.write_text(json.dumps(summary, indent=2, sort_keys=True, default=str), encoding="utf-8")

    md = []
    md.append("# R38AU-R2 MISC compression diagnostic")
    md.append("")
    md.append(f"- features_source: `{features_gz}`")
    md.append(f"- records_seen: `{records_seen}`")
    md.append(f"- parsed_json_fields: `{dict(parsed_json_fields)}`")
    md.append(f"- misc_rows: `{len(rows)}`")
    md.append(f"- branch_counts: `{dict(branch_counts)}`")
    md.append(f"- stage_counts: `{ {str(k): v for k, v in stage_counts.items()} }`")
    md.append("")
    md.append("## Boolean counts")
    md.append(f"`{ {k: dict(v) for k, v in bool_counts.items()} }`")
    md.append("")
    md.append("## Compression-related keys discovered")
    md.append(f"`{dict(nested_key_counts.most_common(80))}`")
    md.append("")
    md.append("## Numeric stats")
    md.append(f"`{ {k: stats(v) for k, v in numeric_values.items()} }`")
    md.append("")
    md.append("## Decision")
    md.append("- No production patch.")
    md.append("- No candidate route.")
    md.append("- Use this to decide whether compression is missing, always false, or genuinely absent.")
    out_md.write_text("\n".join(md), encoding="utf-8")

    print("records_seen=" + str(records_seen))
    print("parsed_json_fields=" + json.dumps(dict(parsed_json_fields), sort_keys=True))
    print("misc_rows=" + str(len(rows)))
    print("branch_counts=" + json.dumps(dict(branch_counts), sort_keys=True))
    print("stage_counts=" + json.dumps({str(k): v for k, v in stage_counts.items()}, sort_keys=True))
    print("nested_compression_key_counts=" + json.dumps(dict(nested_key_counts.most_common(40)), sort_keys=True))
    print("out_json=" + str(out_json))
    print("out_md=" + str(out_md))
    print("out_rows=" + str(out_rows))
    print("")
    print("\n".join(md[:80]))
    return 0 if rows else 3

if __name__ == "__main__":
    raise SystemExit(main())
