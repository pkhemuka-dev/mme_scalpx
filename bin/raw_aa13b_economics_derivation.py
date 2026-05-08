from __future__ import annotations

import argparse
import csv
import json
import pathlib
from datetime import datetime, timezone

FAMILY_ALIASES = {
    "MIS-T": "MIST", "MIST": "MIST",
    "MIS-B": "MISB", "MISB": "MISB",
    "MIS-C": "MISC", "MISC": "MISC",
    "MIS-R": "MISR", "MISR": "MISR",
    "MISO": "MISO",
}

def norm_family(v: str) -> str:
    s = (v or "").strip().upper().replace("_", "-")
    return FAMILY_ALIASES.get(s, s.replace("-", ""))

def first(row, keys):
    for k in keys:
        v = row.get(k)
        if v is not None and str(v).strip() != "":
            return str(v).strip()
    return ""

def derive_row(row, authority):
    family_raw = first(row, ["trade_family", "family", "strategy_family", "strategy_id"])
    family = norm_family(family_raw)
    out = dict(row)

    if family not in authority:
        out["raw_economics_ready"] = "false"
        out["economics_reason"] = "family_authority_unavailable"
        return out

    a = authority[family]
    side = first(row, ["side", "trade_side", "branch", "option_side"])
    selected_leg = first(row, ["selected_leg", "selected_option", "instrument", "symbol", "tradingsymbol"])
    entry_mode = first(row, ["entry_mode", "entry_kind", "entry_type"])

    out["trade_family"] = family
    out["target_points"] = str(a["target_points"])
    out["hard_stop_points"] = str(a["hard_stop_points"])
    out["tick_size"] = str(a["tick_size"])
    out["target_ticks"] = str(a["target_ticks"])
    out["stop_ticks"] = str(a["stop_ticks"])
    out["reward_ticks"] = str(a["reward_ticks"])
    out["reward_cost_ratio"] = ""
    out["reward_cost_ratio_status"] = a.get("reward_cost_ratio_status", "unavailable")
    out["oi_wall_strength_status"] = a.get("oi_wall_strength_status", "unavailable")
    out["oi_wall_distance_points_status"] = a.get("oi_wall_distance_points_status", "unavailable")

    blockers = []
    if not side:
        blockers.append("side_missing")
    if not selected_leg:
        blockers.append("selected_leg_missing")
    if not entry_mode:
        blockers.append("entry_mode_missing")

    if blockers:
        out["raw_economics_ready"] = "partial"
        out["economics_reason"] = "authority_derived_but_" + ",".join(blockers)
    else:
        out["raw_economics_ready"] = "true"
        out["economics_reason"] = "authority_derived_from_raw_doctrine_economics_authority_map"

    return out

def load_authority(path):
    obj = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    fams = obj["family_authority"]
    return {k: v for k, v in fams.items()}

def run(input_csv, output_csv, authority_path, limit=None):
    authority = load_authority(authority_path)
    input_path = pathlib.Path(input_csv)
    output_path = pathlib.Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows_written = 0
    family_counts = {}
    ready_counts = {"true": 0, "partial": 0, "false": 0}
    fieldnames = None

    with input_path.open("r", encoding="utf-8", newline="") as src:
        reader = csv.DictReader(src)
        if not reader.fieldnames:
            raise SystemExit("input_csv_has_no_header")

        derived_rows = []
        for idx, row in enumerate(reader):
            if limit is not None and idx >= limit:
                break
            d = derive_row(row, authority)
            derived_rows.append(d)
            fam = d.get("trade_family", "")
            family_counts[fam] = family_counts.get(fam, 0) + 1
            ready = d.get("raw_economics_ready", "false")
            ready_counts[ready] = ready_counts.get(ready, 0) + 1
            rows_written += 1

        base_fields = list(reader.fieldnames)
        extra_fields = []
        for r in derived_rows:
            for k in r.keys():
                if k not in base_fields and k not in extra_fields:
                    extra_fields.append(k)
        fieldnames = base_fields + extra_fields

    with output_path.open("w", encoding="utf-8", newline="") as dst:
        writer = csv.DictWriter(dst, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in derived_rows:
            writer.writerow(r)

    summary = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_csv": str(input_path),
        "output_csv": str(output_path),
        "rows_written": rows_written,
        "family_counts": family_counts,
        "ready_counts": ready_counts,
        "authority_path": str(authority_path),
    }
    return summary

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-csv", required=True)
    ap.add_argument("--output-csv", required=True)
    ap.add_argument("--authority-map", required=True)
    ap.add_argument("--summary-json", required=True)
    ap.add_argument("--limit", type=int, default=None)
    ns = ap.parse_args()

    summary = run(ns.input_csv, ns.output_csv, ns.authority_map, ns.limit)
    pathlib.Path(ns.summary_json).write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
