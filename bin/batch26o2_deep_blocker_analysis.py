#!/usr/bin/env python3
from __future__ import annotations

import csv
import gzip
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path("/home/Lenovo/scalpx/projects/mme_scalpx")
OUTDIR = Path(sys.argv[1])
OUTDIR.mkdir(parents=True, exist_ok=True)

FAMILIES = ["MIST", "MISB", "MISC", "MISR", "MISO"]
BRANCH_KEYS = [
    "mist_call", "mist_put",
    "misb_call", "misb_put",
    "misc_call", "misc_put",
    "misr_call", "misr_put",
    "miso_call", "miso_put",
]
IMPORTANT_BOOL_KEYS = [
    "present",
    "branch_ready",
    "eligible",
    "entry_eligibility",
    "context_pass",
    "option_tradability_pass",
    "tradability_pass",
    "entry_pass",
    "provider_ready",
    "burst_detected",
    "burst_valid",
    "strike_bundle_present",
    "active_zone_valid",
    "fake_break",
    "absorption",
    "range_reentry",
    "flow_flip",
    "hold_proof",
    "no_mans_land_cleared",
    "reversal_impulse",
    "compression_detected",
    "directional_breakout_triggered",
    "expansion_accepted",
    "retest_monitor_active",
    "resume_confirmed",
    "shelf_confirmed",
    "breakout_triggered",
    "breakout_accepted",
    "trend_confirmed",
    "pullback_detected",
]
IMPORTANT_FIELD_KEYS = [
    "failed_stage",
    "batch9_freeze_blocked_reason",
    "pre_batch9_failed_stage",
    "blocked_reason",
    "runtime_mode",
    "runtime_mode_surface",
    "provider_ready",
    "provider_ready_classic",
    "provider_ready_miso",
    "dhan_context_fresh",
    "data_valid",
    "data_quality_ok",
    "warmup_complete",
    "selected_option_present",
    "futures_present",
    "call_present",
    "put_present",
]

def sh(cmd: list[str], timeout: int = 15) -> str:
    try:
        p = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        return (p.stdout or "") + (p.stderr or "")
    except Exception as exc:
        return f"__ERROR__ {cmd}: {exc}"

def raw(cmd: list[str], timeout: int = 15) -> str:
    return sh(["redis-cli", "--raw"] + cmd, timeout=timeout)

def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str] | None = None) -> None:
    if fields is None:
        fields = []
        seen = set()
        for r in rows:
            for k in r:
                if k not in seen:
                    seen.add(k)
                    fields.append(k)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)

def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")

def parse_xrevrange_raw(text: str) -> list[dict[str, str]]:
    lines = [x for x in text.splitlines() if x != ""]
    out = []
    id_re = re.compile(r"^\d+-\d+$")
    i = 0
    while i < len(lines):
        if not id_re.match(lines[i].strip()):
            i += 1
            continue
        row = {"_id": lines[i].strip()}
        i += 1
        while i < len(lines) and not id_re.match(lines[i].strip()):
            k = lines[i].strip()
            v = ""
            if i + 1 < len(lines) and not id_re.match(lines[i + 1].strip()):
                v = lines[i + 1]
                i += 2
            else:
                i += 1
            row[k] = v
        out.append(row)
    return out

def jloads(s: Any) -> Any:
    if not isinstance(s, str):
        return None
    try:
        return json.loads(s)
    except Exception:
        return None

def deep_get(obj: Any, path: list[str], default: Any = None) -> Any:
    cur = obj
    for p in path:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return default
    return cur

def family_from_branch(branch: str) -> str:
    return branch.split("_", 1)[0].upper() if "_" in branch else ""

def flatten_json_strings(obj: Any, limit: int = 5) -> Any:
    """Recursively decode JSON-in-string fields like consumer_view_json a few levels."""
    if limit <= 0:
        return obj
    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            if isinstance(v, str):
                decoded = jloads(v)
                new[k] = flatten_json_strings(decoded, limit - 1) if decoded is not None else v
            else:
                new[k] = flatten_json_strings(v, limit - 1)
        return new
    if isinstance(obj, list):
        return [flatten_json_strings(x, limit - 1) for x in obj]
    return obj

def iter_dicts(obj: Any):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from iter_dicts(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from iter_dicts(v)

def find_branch_surfaces(obj: Any) -> dict[str, dict[str, Any]]:
    found = {}
    if not isinstance(obj, dict):
        return found
    for d in iter_dicts(obj):
        if not isinstance(d, dict):
            continue
        for key in BRANCH_KEYS:
            val = d.get(key)
            if isinstance(val, dict):
                found[key] = val
    return found

def summarize_branch(branch_key: str, surface: dict[str, Any], source_id: str) -> dict[str, Any]:
    fam = family_from_branch(branch_key)
    side = "CALL" if branch_key.endswith("_call") else "PUT"
    row: dict[str, Any] = {
        "source_id": source_id,
        "branch_key": branch_key,
        "family": fam,
        "side": side,
        "surface_kind": surface.get("surface_kind", ""),
        "present": surface.get("present", ""),
        "branch_ready": surface.get("branch_ready", ""),
        "eligible": surface.get("eligible", surface.get("entry_eligibility", "")),
        "failed_stage": surface.get("failed_stage", ""),
        "blocked_reason": surface.get("blocked_reason", ""),
        "batch9_freeze_blocked_reason": surface.get("batch9_freeze_blocked_reason", ""),
        "pre_batch9_failed_stage": surface.get("pre_batch9_failed_stage", ""),
        "runtime_mode": surface.get("runtime_mode", ""),
        "provider_ready": surface.get("provider_ready", ""),
        "context_pass": surface.get("context_pass", ""),
        "option_tradability_pass": surface.get("option_tradability_pass", surface.get("tradability_pass", "")),
        "entry_eligibility": surface.get("entry_eligibility", ""),
        "setup_score": surface.get("setup_score", ""),
    }

    # Nested runtime/tradability fields.
    rt = surface.get("runtime_mode_surface") if isinstance(surface.get("runtime_mode_surface"), dict) else {}
    tr = surface.get("tradability") if isinstance(surface.get("tradability"), dict) else {}
    tr2 = surface.get("tradability_surface") if isinstance(surface.get("tradability_surface"), dict) else {}
    selected = surface.get("selected_features") if isinstance(surface.get("selected_features"), dict) else {}
    opt = surface.get("option_features") if isinstance(surface.get("option_features"), dict) else {}

    row.update({
        "rt_mode": rt.get("mode", rt.get("runtime_mode", "")),
        "rt_provider_ready": rt.get("provider_ready", ""),
        "rt_depth20_ready": rt.get("depth20_ready", ""),
        "trad_present": tr.get("present", tr2.get("present", "")),
        "trad_entry_pass": tr.get("entry_pass", tr2.get("entry_pass", "")),
        "trad_blocked_reason": tr.get("blocked_reason", tr2.get("blocked_reason", "")),
        "trad_spread_pass": tr.get("spread_pass", tr2.get("spread_pass", "")),
        "trad_depth_pass": tr.get("depth_pass", tr2.get("depth_pass", "")),
        "trad_response_pass": tr.get("response_pass", tr2.get("response_pass", "")),
        "trad_stale_pass": tr.get("stale_pass", tr2.get("stale_pass", "")),
        "trad_crossed_book_pass": tr.get("crossed_book_pass", tr2.get("crossed_book_pass", "")),
        "trad_queue_pass": tr.get("queue_pass", tr2.get("queue_pass", "")),
        "trad_depth_total": tr.get("depth_total", tr2.get("depth_total", "")),
        "trad_spread_ratio": tr.get("spread_ratio", tr2.get("spread_ratio", "")),
        "selected_present": selected.get("present", ""),
        "selected_live_present": selected.get("live_present", ""),
        "selected_fresh": selected.get("fresh", ""),
        "selected_stale": selected.get("stale", ""),
        "selected_ltp": selected.get("ltp", ""),
        "selected_strike": selected.get("strike", ""),
        "selected_symbol": selected.get("option_symbol", selected.get("trading_symbol", "")),
        "option_present": opt.get("present", ""),
        "option_fresh": opt.get("fresh", ""),
        "option_stale": opt.get("stale", ""),
    })

    for k in IMPORTANT_BOOL_KEYS:
        if k in surface and k not in row:
            row[k] = surface.get(k)

    return row

def read_file(path: Path, limit: int = 50_000_000) -> str:
    try:
        if path.suffix == ".gz":
            with gzip.open(path, "rt", errors="replace") as f:
                return f.read(limit)
        with path.open("rt", errors="replace") as f:
            return f.read(limit)
    except Exception as exc:
        return f"__READ_ERROR__ {exc}"

def today_files() -> list[Path]:
    files = []
    for base in [ROOT / "run/live_capture", ROOT / "run/proofs", ROOT / "run/reports"]:
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            n = p.name
            if "20260430" in n or "batch26m" in n.lower() or "batch26n" in n.lower() or "batch26o" in n.lower():
                files.append(p)
    return sorted(set(files))

def extract_json_objects_from_text(text: str, max_objects: int = 500) -> list[Any]:
    """Best-effort extraction for lines containing JSON objects."""
    objs = []
    for line in text.splitlines():
        if "{" not in line or "}" not in line:
            continue
        start = line.find("{")
        end = line.rfind("}")
        if start < 0 or end <= start:
            continue
        candidate = line[start:end+1]
        obj = jloads(candidate)
        if obj is not None:
            objs.append(flatten_json_strings(obj))
        if len(objs) >= max_objects:
            break
    return objs

def counter_to_rows(counter: Counter, label: str) -> list[dict[str, Any]]:
    return [{"metric": label, "key": str(k), "count": int(v)} for k, v in counter.most_common()]

# --- Redis decisions parsing ---
summary: dict[str, Any] = {
    "generated_at": datetime.now().isoformat(),
    "root": str(ROOT),
    "readonly": True,
}

health = {
    "df_h": sh(["df", "-h", "/"], 5),
    "free_h": sh(["free", "-h"], 5),
    "redis_ping": sh(["redis-cli", "PING"], 3),
    "redis_memory": sh(["redis-cli", "INFO", "memory"], 5),
    "redis_persistence": sh(["redis-cli", "INFO", "persistence"], 5),
    "orders_xlen": sh(["redis-cli", "XLEN", "orders:mme:stream"], 5),
    "position": sh(["redis-cli", "HGETALL", "state:position:mme"], 5),
}
write_json(OUTDIR / "health_snapshot.json", health)

decision_raw = raw(["XREVRANGE", "decisions:mme:stream", "+", "-", "COUNT", "5000"], 30)
decision_rows_raw = parse_xrevrange_raw(decision_raw)
decision_rows: list[dict[str, Any]] = []
branch_rows: list[dict[str, Any]] = []

action_counts = Counter()
reason_counts = Counter()
activation_reason_counts = Counter()
selected_family_counts = Counter()
candidate_count_counts = Counter()
provider_mismatch_counts = Counter()
stage_flag_false_counts = Counter()

for row in decision_rows_raw:
    payload = jloads(row.get("payload_json", ""))
    if payload is None:
        continue
    payload = flatten_json_strings(payload)
    view = payload.get("consumer_view_json") if isinstance(payload.get("consumer_view_json"), dict) else {}
    if not view:
        view = payload.get("consumer_view") if isinstance(payload.get("consumer_view"), dict) else {}
    stage_flags = view.get("stage_flags") if isinstance(view.get("stage_flags"), dict) else {}

    provider_runtime = view.get("provider_runtime") if isinstance(view.get("provider_runtime"), dict) else {}
    common = view.get("common") if isinstance(view.get("common"), dict) else {}

    action = payload.get("action", "")
    reason = payload.get("reason", "")
    activation_reason = payload.get("activation_reason", "")
    selected_family = payload.get("activation_selected_family_id", "")
    selected_branch = payload.get("activation_selected_branch_id", "")
    candidate_count = payload.get("activation_candidate_count", "")

    action_counts[action] += 1
    reason_counts[reason] += 1
    activation_reason_counts[activation_reason] += 1
    selected_family_counts[selected_family or "EMPTY"] += 1
    candidate_count_counts[str(candidate_count)] += 1

    for k, v in stage_flags.items():
        if v is False:
            stage_flag_false_counts[k] += 1

    pr_classic = provider_runtime.get("provider_ready_classic")
    sf_classic = stage_flags.get("provider_ready_classic")
    pr_miso = provider_runtime.get("provider_ready_miso")
    sf_miso = stage_flags.get("provider_ready_miso")
    if pr_classic is True and sf_classic is False:
        provider_mismatch_counts["provider_runtime_classic_true_stage_false"] += 1
    if pr_miso is True and sf_miso is False:
        provider_mismatch_counts["provider_runtime_miso_true_stage_false"] += 1

    decision_rows.append({
        "stream_id": row.get("_id", ""),
        "decision_id": payload.get("decision_id", ""),
        "ts_ns": payload.get("ts_ns", ""),
        "action": action,
        "side": payload.get("side", ""),
        "reason": reason,
        "price": payload.get("price", ""),
        "hold_only": payload.get("hold_only", ""),
        "activation_mode": payload.get("activation_mode", ""),
        "activation_action": payload.get("activation_action", ""),
        "activation_observed_action": payload.get("activation_observed_action", ""),
        "activation_promoted": payload.get("activation_promoted", ""),
        "activation_safe_to_promote": payload.get("activation_safe_to_promote", ""),
        "activation_reason": activation_reason,
        "activation_candidate_count": candidate_count,
        "activation_selected_family_id": selected_family,
        "activation_selected_branch_id": selected_branch,
        "data_valid": payload.get("data_valid", view.get("data_valid", "")),
        "safe_to_consume": payload.get("safe_to_consume", view.get("safe_to_consume", "")),
        "warmup_complete": payload.get("warmup_complete", view.get("warmup_complete", "")),
        "provider_ready_classic_payload": payload.get("provider_ready_classic", ""),
        "provider_ready_miso_payload": payload.get("provider_ready_miso", ""),
        "provider_runtime_ready_classic": provider_runtime.get("provider_ready_classic", ""),
        "provider_runtime_ready_miso": provider_runtime.get("provider_ready_miso", ""),
        "stage_provider_ready_classic": stage_flags.get("provider_ready_classic", ""),
        "stage_provider_ready_miso": stage_flags.get("provider_ready_miso", ""),
        "stage_dhan_context_fresh": stage_flags.get("dhan_context_fresh", ""),
        "stage_data_valid": stage_flags.get("data_valid", ""),
        "stage_data_quality_ok": stage_flags.get("data_quality_ok", ""),
        "stage_selected_option_present": stage_flags.get("selected_option_present", ""),
        "stage_futures_present": stage_flags.get("futures_present", ""),
        "stage_call_present": stage_flags.get("call_present", ""),
        "stage_put_present": stage_flags.get("put_present", ""),
        "fut_ltp": deep_get(common, ["futures", "ltp"], ""),
        "call_ltp": deep_get(common, ["call", "ltp"], ""),
        "put_ltp": deep_get(common, ["put", "ltp"], ""),
        "call_tradability_ok": deep_get(common, ["call", "tradability_ok"], ""),
        "put_tradability_ok": deep_get(common, ["put", "tradability_ok"], ""),
        "selected_option_side": deep_get(common, ["selected_option", "side"], ""),
        "selected_option_ltp": deep_get(common, ["selected_option", "ltp"], ""),
    })

    surfaces = find_branch_surfaces(payload)
    for bkey, surf in surfaces.items():
        branch_rows.append(summarize_branch(bkey, surf, row.get("_id", "")))

write_csv(OUTDIR / "decision_rows.csv", decision_rows)
write_csv(OUTDIR / "decision_branch_surfaces.csv", branch_rows)

# --- Features stream parsing ---
feature_raw = raw(["XREVRANGE", "features:mme:stream", "+", "-", "COUNT", "2000"], 60)
feature_rows_raw = parse_xrevrange_raw(feature_raw)
feature_branch_rows: list[dict[str, Any]] = []
feature_summary_rows: list[dict[str, Any]] = []
feature_family_counter = {f: Counter() for f in FAMILIES}

for row in feature_rows_raw:
    # Try every field as JSON, because field names can drift.
    for field, val in row.items():
        if field == "_id":
            continue
        obj = jloads(val)
        if obj is None:
            continue
        obj = flatten_json_strings(obj)
        surfaces = find_branch_surfaces(obj)
        for bkey, surf in surfaces.items():
            r = summarize_branch(bkey, surf, row.get("_id", ""))
            r["source_field"] = field
            feature_branch_rows.append(r)
            fam = r["family"]
            feature_family_counter[fam]["rows"] += 1
            if r.get("eligible") is True:
                feature_family_counter[fam]["eligible_true"] += 1
            if r.get("failed_stage"):
                feature_family_counter[fam][f"failed_stage:{r.get('failed_stage')}"] += 1
            if r.get("batch9_freeze_blocked_reason"):
                feature_family_counter[fam][f"blocked:{r.get('batch9_freeze_blocked_reason')}"] += 1

write_csv(OUTDIR / "feature_branch_surfaces.csv", feature_branch_rows)

# --- Log extraction for blocker terms ---
log_rows: list[dict[str, Any]] = []
log_blocker_counter = Counter()
family_log_blockers = {f: Counter() for f in FAMILIES}

for p in today_files():
    text = read_file(p, 30_000_000)
    row = {
        "path": str(p.relative_to(ROOT)),
        "size_mb": round(p.stat().st_size / 1024 / 1024, 3),
    }

    for fam in FAMILIES:
        fam_count = len(re.findall(rf"\b{fam}\b", text, flags=re.I))
        row[f"{fam.lower()}_mentions"] = fam_count

    for term in [
        "provider_not_ready", "runtime_disabled", "not_present", "stale", "crossed_book",
        "data_valid", "data_quality_ok", "dhan_context_fresh", "entry_pass",
        "tradability_ok", "activation_candidate_count", "activation_safe_to_promote",
        "view_data_invalid", "hold_only_family_features_consumer_bridge",
    ]:
        c = len(re.findall(re.escape(term), text, flags=re.I))
        row[term] = c
        if c:
            log_blocker_counter[term] += c

    # Family-specific failed_stage / blocked_reason snippets.
    for line in text.splitlines():
        if not any(fam in line.upper() for fam in FAMILIES):
            continue
        if any(term in line.lower() for term in ["failed_stage", "blocked_reason", "eligible", "entry_pass", "tradability", "provider_not_ready", "runtime_disabled", "not_present"]):
            fam = "UNKNOWN"
            for f in FAMILIES:
                if f in line.upper():
                    fam = f
                    break
            for m in re.finditer(r'"(?:failed_stage|batch9_freeze_blocked_reason|pre_batch9_failed_stage|blocked_reason)"\s*:\s*"([^"]*)"', line):
                family_log_blockers[fam][m.group(1) or "EMPTY"] += 1

    log_rows.append(row)

write_csv(OUTDIR / "log_blocker_counts.csv", log_rows)

# --- Aggregate branch blockers ---
branch_summary_rows: list[dict[str, Any]] = []
all_branch_rows = branch_rows + feature_branch_rows

for fam in FAMILIES:
    fam_rows = [r for r in all_branch_rows if r.get("family") == fam]
    failed = Counter(str(r.get("failed_stage") or "EMPTY") for r in fam_rows)
    blocked = Counter(str(r.get("batch9_freeze_blocked_reason") or r.get("blocked_reason") or "EMPTY") for r in fam_rows)
    pre = Counter(str(r.get("pre_batch9_failed_stage") or "EMPTY") for r in fam_rows)
    trad_blocked = Counter(str(r.get("trad_blocked_reason") or "EMPTY") for r in fam_rows)
    eligible_true = sum(1 for r in fam_rows if str(r.get("eligible")).lower() == "true")
    entry_pass_true = sum(1 for r in fam_rows if str(r.get("trad_entry_pass")).lower() == "true")
    selected_present_true = sum(1 for r in fam_rows if str(r.get("selected_present")).lower() == "true")
    fresh_true = sum(1 for r in fam_rows if str(r.get("selected_fresh")).lower() == "true")

    branch_summary_rows.append({
        "family": fam,
        "branch_surface_rows": len(fam_rows),
        "eligible_true_count": eligible_true,
        "trad_entry_pass_true_count": entry_pass_true,
        "selected_present_true_count": selected_present_true,
        "selected_fresh_true_count": fresh_true,
        "top_failed_stage": failed.most_common(1)[0][0] if failed else "",
        "top_failed_stage_count": failed.most_common(1)[0][1] if failed else 0,
        "top_blocked_reason": blocked.most_common(1)[0][0] if blocked else "",
        "top_blocked_reason_count": blocked.most_common(1)[0][1] if blocked else 0,
        "top_pre_batch9_failed_stage": pre.most_common(1)[0][0] if pre else "",
        "top_pre_batch9_failed_stage_count": pre.most_common(1)[0][1] if pre else 0,
        "top_trad_blocked_reason": trad_blocked.most_common(1)[0][0] if trad_blocked else "",
        "top_trad_blocked_reason_count": trad_blocked.most_common(1)[0][1] if trad_blocked else 0,
    })

write_csv(OUTDIR / "family_branch_blocker_summary.csv", branch_summary_rows)

# --- Counters output ---
counter_rows: list[dict[str, Any]] = []
for name, ctr in [
    ("decision_action", action_counts),
    ("decision_reason", reason_counts),
    ("activation_reason", activation_reason_counts),
    ("selected_family", selected_family_counts),
    ("activation_candidate_count", candidate_count_counts),
    ("provider_mismatch", provider_mismatch_counts),
    ("stage_flag_false", stage_flag_false_counts),
    ("log_blocker_terms", log_blocker_counter),
]:
    counter_rows.extend(counter_to_rows(ctr, name))

write_csv(OUTDIR / "aggregate_counters.csv", counter_rows)

# --- Verdict logic ---
latest = decision_rows[0] if decision_rows else {}
total_decisions = len(decision_rows)
non_hold = sum(1 for r in decision_rows if r.get("action") != "HOLD")
candidate_positive = sum(1 for r in decision_rows if str(r.get("activation_candidate_count")) not in ("", "0", "None", "null"))
selected_positive = sum(1 for r in decision_rows if r.get("activation_selected_family_id"))

main_blockers: list[str] = []

if action_counts.get("HOLD", 0) == total_decisions and total_decisions > 0:
    main_blockers.append("All strategy decisions were HOLD.")
if candidate_positive == 0:
    main_blockers.append("No activation candidates were selected in decisions:mme:stream.")
if selected_positive == 0:
    main_blockers.append("No activation_selected_family_id was populated.")
if provider_mismatch_counts:
    main_blockers.append("Provider runtime readiness and strategy stage_flags disagree.")
if stage_flag_false_counts.get("data_valid", 0) > 0:
    main_blockers.append("stage_flags.data_valid was false in decision consumer view.")
if stage_flag_false_counts.get("data_quality_ok", 0) > 0:
    main_blockers.append("stage_flags.data_quality_ok was false in decision consumer view.")
if stage_flag_false_counts.get("dhan_context_fresh", 0) > 0:
    main_blockers.append("Dhan context freshness was false.")
if any(r["top_failed_stage"] in ("provider_not_ready", "runtime_disabled") for r in branch_summary_rows):
    main_blockers.append("Branch surfaces show provider_not_ready/runtime_disabled blockers.")
if any(r["top_trad_blocked_reason"] == "not_present" for r in branch_summary_rows):
    main_blockers.append("Tradability surfaces show not_present blockers.")

tomorrow_verdict = "NOT_READY_FOR_REAL_PAPER_ENTRY"
if total_decisions > 0 and non_hold == 0 and candidate_positive == 0:
    tomorrow_verdict = "SAFE_BUT_BLOCKED_FOR_PAPER_ENTRY"
if not main_blockers:
    tomorrow_verdict = "NEEDS_MANUAL_REVIEW"

verdict = {
    "total_decisions": total_decisions,
    "decision_action_counts": dict(action_counts),
    "candidate_positive_decision_count": candidate_positive,
    "selected_family_positive_decision_count": selected_positive,
    "provider_mismatch_counts": dict(provider_mismatch_counts),
    "stage_flag_false_counts": dict(stage_flag_false_counts),
    "latest_decision": latest,
    "main_blockers": main_blockers,
    "tomorrow_paper_trade_verdict": tomorrow_verdict,
    "interpretation": {
        "SAFE_BUT_BLOCKED_FOR_PAPER_ENTRY": "Runtime appears safe, but paper entries will probably remain blocked unless data_valid/provider/stage/tradability readiness are fixed or verified during live market.",
        "NOT_READY_FOR_REAL_PAPER_ENTRY": "Do not enable real/paper entry until blockers are resolved.",
        "NEEDS_MANUAL_REVIEW": "The report did not identify a simple blocker; inspect CSV outputs.",
    }.get(tomorrow_verdict, ""),
}
write_json(OUTDIR / "verdict.json", verdict)

# Markdown report
md = []
md.append("# Batch 26-O2 Deep Blocker Analysis — Read Only")
md.append("")
md.append(f"Generated: `{summary['generated_at']}`")
md.append("")
md.append("## Safety")
md.append("")
md.append("- Read-only analysis.")
md.append("- No broker call.")
md.append("- No Redis write.")
md.append("- No runtime patch.")
md.append("")
md.append("## Final Verdict")
md.append("")
md.append(f"```text\n{tomorrow_verdict}\n```")
md.append("")
md.append("## Decision Stream Summary")
md.append("")
md.append(f"- Total decisions parsed: `{total_decisions}`")
md.append(f"- Non-HOLD decisions: `{non_hold}`")
md.append(f"- Decisions with activation_candidate_count > 0: `{candidate_positive}`")
md.append(f"- Decisions with selected family: `{selected_positive}`")
md.append("")
md.append("### Action counts")
md.append("")
for k, v in action_counts.most_common():
    md.append(f"- `{k}`: `{v}`")
md.append("")
md.append("### Top decision reasons")
md.append("")
for k, v in reason_counts.most_common(10):
    md.append(f"- `{k}`: `{v}`")
md.append("")
md.append("### Top activation reasons")
md.append("")
for k, v in activation_reason_counts.most_common(10):
    md.append(f"- `{k}`: `{v}`")
md.append("")
md.append("## Provider / Stage Flag Mismatches")
md.append("")
if provider_mismatch_counts:
    for k, v in provider_mismatch_counts.most_common():
        md.append(f"- `{k}`: `{v}`")
else:
    md.append("- No provider mismatch detected in parsed decisions.")
md.append("")
md.append("## Stage Flags False Counts")
md.append("")
for k, v in stage_flag_false_counts.most_common():
    md.append(f"- `{k}`: `{v}`")
md.append("")
md.append("## Family Branch Blockers")
md.append("")
md.append("| Family | Rows | Eligible true | Entry pass true | Selected present | Fresh selected | Top failed stage | Count | Top blocked reason | Count | Top tradability block | Count |")
md.append("|---|---:|---:|---:|---:|---:|---|---:|---|---:|---|---:|")
for r in branch_summary_rows:
    md.append(
        f"| {r['family']} | {r['branch_surface_rows']} | {r['eligible_true_count']} | "
        f"{r['trad_entry_pass_true_count']} | {r['selected_present_true_count']} | {r['selected_fresh_true_count']} | "
        f"{r['top_failed_stage']} | {r['top_failed_stage_count']} | "
        f"{r['top_blocked_reason']} | {r['top_blocked_reason_count']} | "
        f"{r['top_trad_blocked_reason']} | {r['top_trad_blocked_reason_count']} |"
    )
md.append("")
md.append("## Main Blockers")
md.append("")
for b in main_blockers:
    md.append(f"- {b}")
md.append("")
md.append("## Tomorrow Paper Trade Guidance")
md.append("")
if tomorrow_verdict == "SAFE_BUT_BLOCKED_FOR_PAPER_ENTRY":
    md.append("The system looks safe, but it is likely to remain HOLD-only tomorrow unless live market readiness changes. Do not enable real broker paper entry until a live preflight proves candidate generation, provider readiness, tradability readiness, and order-block safety together.")
elif tomorrow_verdict == "NOT_READY_FOR_REAL_PAPER_ENTRY":
    md.append("Do not enable real paper entry. Run a targeted live-market blocker repair/preflight first.")
else:
    md.append("Manual review required. Inspect CSV files listed below.")
md.append("")
md.append("## Output Files")
md.append("")
for name in [
    "REPORT.md",
    "verdict.json",
    "health_snapshot.json",
    "decision_rows.csv",
    "decision_branch_surfaces.csv",
    "feature_branch_surfaces.csv",
    "family_branch_blocker_summary.csv",
    "aggregate_counters.csv",
    "log_blocker_counts.csv",
]:
    md.append(f"- `{name}`")
md.append("")
report = "\n".join(md) + "\n"
(OUTDIR / "REPORT.md").write_text(report, encoding="utf-8")
print("===== BATCH 26-O2 DEEP BLOCKER ANALYSIS COMPLETE =====")
print(f"OUTDIR={OUTDIR}")
print(f"REPORT={OUTDIR / 'REPORT.md'}")
print("")
print(report)
