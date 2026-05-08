#!/usr/bin/env python3
from __future__ import annotations

import csv
import gzip
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, date
from pathlib import Path
from typing import Any

ROOT = Path("/home/Lenovo/scalpx/projects/mme_scalpx")
TODAY = date.today().strftime("%Y%m%d")
TODAY_DASH = date.today().isoformat()

OUTDIR = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "run/reports/live_session_forensics_manual"
OUTDIR.mkdir(parents=True, exist_ok=True)

FAMILIES = ["MIST", "MISB", "MISC", "MISR", "MISO"]
SIGNAL_WORDS = [
    "signal",
    "candidate",
    "eligible",
    "entry",
    "ENTRY",
    "armed",
    "ARMED",
    "opportunity",
    "decision",
    "HOLD",
    "ENTER",
    "EXIT",
    "CALL",
    "PUT",
    "CE",
    "PE",
    "paper",
    "shadow",
    "dry",
    "pnl",
    "PnL",
    "profit",
    "loss",
]

ACTION_WORDS = [
    "ENTER",
    "ENTRY",
    "BUY",
    "SELL",
    "EXIT",
    "HOLD",
    "REJECT",
    "BLOCK",
    "VETO",
    "ARMED",
    "CANDIDATE",
]

def run(cmd: list[str], timeout: int = 8) -> str:
    try:
        p = subprocess.run(
            cmd,
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return (p.stdout or "") + (p.stderr or "")
    except Exception as e:
        return f"__ERROR__ {cmd}: {e}"

def redis_ok() -> bool:
    return "PONG" in run(["redis-cli", "PING"], timeout=3)

def redis_type(key: str) -> str:
    return run(["redis-cli", "TYPE", key], timeout=3).strip().splitlines()[-1].strip()

def redis_keys(pattern: str) -> list[str]:
    out = run(["redis-cli", "--raw", "KEYS", pattern], timeout=10)
    return sorted([x.strip() for x in out.splitlines() if x.strip() and not x.startswith("__ERROR__")])

def stream_len(key: str) -> int:
    out = run(["redis-cli", "XLEN", key], timeout=5).strip()
    m = re.search(r"\(integer\)\s*(\d+)", out)
    if m:
        return int(m.group(1))
    try:
        return int(out.splitlines()[-1])
    except Exception:
        return -1

def stream_range(key: str, count: int = 2000) -> str:
    return run(["redis-cli", "--raw", "XREVRANGE", key, "+", "-", "COUNT", str(count)], timeout=20)

def hash_all(key: str) -> str:
    return run(["redis-cli", "--raw", "HGETALL", key], timeout=10)

def safe_json_loads(s: str) -> Any:
    try:
        return json.loads(s)
    except Exception:
        return None

def parse_stream_raw(raw: str) -> list[dict[str, Any]]:
    """
    Best-effort parser for redis-cli --raw XREVRANGE output.
    Output pattern generally:
      id
      field
      value
      field
      value
      id
      ...
    We detect stream IDs and pair following field/value lines.
    """
    lines = [x for x in raw.splitlines() if x != ""]
    rows: list[dict[str, Any]] = []
    i = 0
    id_re = re.compile(r"^\d+-\d+$")
    while i < len(lines):
        if not id_re.match(lines[i].strip()):
            i += 1
            continue
        row: dict[str, Any] = {"_id": lines[i].strip()}
        i += 1
        while i < len(lines) and not id_re.match(lines[i].strip()):
            field = lines[i].strip()
            val = ""
            if i + 1 < len(lines) and not id_re.match(lines[i + 1].strip()):
                val = lines[i + 1]
                i += 2
            else:
                i += 1
            row[field] = val
        rows.append(row)
    return rows

def flatten_candidate_json(value: str) -> list[dict[str, Any]]:
    found = []
    obj = safe_json_loads(value)
    if obj is None:
        return found
    if isinstance(obj, dict):
        found.append(obj)
        for v in obj.values():
            if isinstance(v, str):
                found += flatten_candidate_json(v)
            elif isinstance(v, dict):
                found.append(v)
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, dict):
                        found.append(item)
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict):
                found.append(item)
    return found

def contains_family(text: str, fam: str) -> bool:
    return bool(re.search(rf"\b{re.escape(fam)}\b", text, re.I))

def infer_family_from_text(text: str) -> str:
    for fam in FAMILIES:
        if contains_family(text, fam):
            return fam
    return "UNKNOWN"

def infer_side_from_text(text: str) -> str:
    up = text.upper()
    if "CALL" in up or " CE" in up or "_CE" in up or "LONG_CALL" in up:
        return "CALL"
    if "PUT" in up or " PE" in up or "_PE" in up or "LONG_PUT" in up:
        return "PUT"
    return "UNKNOWN"

def infer_action_from_text(text: str) -> str:
    up = text.upper()
    for a in ["ENTER_CALL", "ENTER_PUT", "ENTER", "ENTRY", "BUY", "EXIT", "HOLD", "REJECT", "BLOCK", "VETO", "ARMED", "CANDIDATE"]:
        if a in up:
            return a
    return "UNKNOWN"

def extract_float_candidates(text: str) -> list[float]:
    vals = []
    for pat in [
        r'"(?:ltp|option_ltp|entry_price|exit_price|price|pnl|pnl_points|points)"\s*:\s*"?(-?\d+(?:\.\d+)?)"?',
        r'(?:ltp|option_ltp|entry_price|exit_price|price|pnl|pnl_points|points)[=:]\s*(-?\d+(?:\.\d+)?)',
    ]:
        for m in re.finditer(pat, text, re.I):
            try:
                vals.append(float(m.group(1)))
            except Exception:
                pass
    return vals

def read_text_file(path: Path, limit_bytes: int = 8_000_000) -> str:
    try:
        if path.suffix == ".gz":
            with gzip.open(path, "rt", errors="replace") as f:
                return f.read(limit_bytes)
        with open(path, "rt", errors="replace") as f:
            return f.read(limit_bytes)
    except Exception as e:
        return f"__READ_ERROR__ {e}"

def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        keys = []
        seen = set()
        for r in rows:
            for k in r.keys():
                if k not in seen:
                    seen.add(k)
                    keys.append(k)
        fieldnames = keys
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)

summary: dict[str, Any] = {
    "generated_at": datetime.now().isoformat(),
    "today_yyyymmdd": TODAY,
    "today_iso": TODAY_DASH,
    "root": str(ROOT),
    "redis_ok": redis_ok(),
    "verdict": {},
    "notes": [],
}

# 1. Redis stream inventory
stream_rows: list[dict[str, Any]] = []
all_keys = []
if summary["redis_ok"]:
    for pattern in ["*mme*", "*MEE*", "*ticks*", "*features*", "*decisions*", "*orders*", "*trades*", "*health*", "*state*"]:
        for k in redis_keys(pattern):
            if k not in all_keys:
                all_keys.append(k)

    for k in sorted(all_keys):
        t = redis_type(k)
        row = {"key": k, "type": t}
        if t == "stream":
            row["xlen"] = stream_len(k)
        else:
            row["xlen"] = ""
        stream_rows.append(row)

write_csv(OUTDIR / "redis_key_inventory.csv", stream_rows, ["key", "type", "xlen"])

# 2. Relevant stream samples
relevant_streams = [
    r for r in stream_rows
    if r.get("type") == "stream"
    and any(x in r["key"].lower() for x in ["tick", "feature", "decision", "order", "trade"])
]
stream_sample_rows: list[dict[str, Any]] = []
decision_rows: list[dict[str, Any]] = []
family_counts = {fam: Counter() for fam in FAMILIES}
family_unknown = Counter()

for r in relevant_streams:
    key = r["key"]
    raw = stream_range(key, count=3000)
    parsed = parse_stream_raw(raw)
    for row in parsed[:3000]:
        text = json.dumps(row, ensure_ascii=False)
        fam = infer_family_from_text(text)
        side = infer_side_from_text(text)
        action = infer_action_from_text(text)
        floats = extract_float_candidates(text)
        sample = {
            "stream": key,
            "id": row.get("_id", ""),
            "family": fam,
            "side": side,
            "action": action,
            "fields": ",".join([k for k in row.keys() if k != "_id"])[:500],
            "text_excerpt": text[:1500],
            "numeric_candidates": ",".join(map(str, floats[:10])),
        }
        stream_sample_rows.append(sample)

        if "decision" in key.lower() or fam != "UNKNOWN" or action != "UNKNOWN":
            decision_rows.append(sample)

        if fam in FAMILIES:
            family_counts[fam][action] += 1
            family_counts[fam][side] += 1
            family_counts[fam]["rows"] += 1
        else:
            family_unknown[action] += 1

write_csv(
    OUTDIR / "stream_relevant_samples.csv",
    stream_sample_rows,
    ["stream", "id", "family", "side", "action", "fields", "numeric_candidates", "text_excerpt"],
)
write_csv(
    OUTDIR / "strategy_decision_like_rows.csv",
    decision_rows,
    ["stream", "id", "family", "side", "action", "fields", "numeric_candidates", "text_excerpt"],
)

# 3. Hash snapshots likely containing latest features/state
hash_rows: list[dict[str, Any]] = []
if summary["redis_ok"]:
    for r in stream_rows:
        k = r["key"]
        if r.get("type") == "hash" and any(x in k.lower() for x in ["feature", "state", "runtime", "position", "risk", "execution", "health"]):
            raw = hash_all(k)
            text = raw[:5000]
            hash_rows.append({
                "key": k,
                "raw_excerpt": text,
                "family": infer_family_from_text(text),
                "side": infer_side_from_text(text),
            })
write_csv(OUTDIR / "redis_hash_snapshots.csv", hash_rows, ["key", "family", "side", "raw_excerpt"])

# 4. Log forensics
log_candidates: list[Path] = []
for base in [ROOT / "run/live_capture", ROOT / "run/proofs", ROOT / "run/reports"]:
    if base.exists():
        for p in base.rglob("*"):
            if p.is_file() and (
                p.suffix in [".log", ".txt", ".json", ".gz"]
                or "capture" in p.name.lower()
                or "paper" in p.name.lower()
                or "shadow" in p.name.lower()
            ):
                name = p.name
                if TODAY in name or "20260430" in name or p.stat().st_mtime >= (datetime.now().timestamp() - 36 * 3600):
                    log_candidates.append(p)

log_rows: list[dict[str, Any]] = []
log_family_summary = {fam: Counter() for fam in FAMILIES}

for p in sorted(set(log_candidates)):
    text = read_text_file(p)
    lower = text.lower()
    row = {
        "path": str(p.relative_to(ROOT)),
        "size_mb": round(p.stat().st_size / 1024 / 1024, 3),
        "lines_scanned_approx": text.count("\n") + 1,
    }
    for fam in FAMILIES:
        c = len(re.findall(rf"\b{fam}\b", text, re.I))
        row[fam.lower() + "_mentions"] = c
        if c:
            log_family_summary[fam]["mentions"] += c
    for word in SIGNAL_WORDS:
        count = lower.count(word.lower())
        safe_word = re.sub(r"[^a-zA-Z0-9]+", "_", word).strip("_").lower()
        row[f"kw_{safe_word}"] = count

    # extract relevant lines
    relevant_lines = []
    for line in text.splitlines():
        if any(contains_family(line, fam) for fam in FAMILIES) or any(w.lower() in line.lower() for w in SIGNAL_WORDS):
            relevant_lines.append(line[:1200])
        if len(relevant_lines) >= 80:
            break
    row["relevant_excerpt"] = "\n".join(relevant_lines)[:8000]
    log_rows.append(row)

write_csv(OUTDIR / "log_forensics_summary.csv", log_rows)

# 5. Family summary from all surfaces
family_summary_rows: list[dict[str, Any]] = []
for fam in FAMILIES:
    c = family_counts[fam]
    lc = log_family_summary[fam]
    family_summary_rows.append({
        "family": fam,
        "redis_rows_mentioning_family": c.get("rows", 0),
        "redis_hold_like": c.get("HOLD", 0),
        "redis_enter_like": c.get("ENTER", 0) + c.get("ENTRY", 0) + c.get("BUY", 0) + c.get("ENTER_CALL", 0) + c.get("ENTER_PUT", 0),
        "redis_exit_like": c.get("EXIT", 0),
        "redis_candidate_like": c.get("CANDIDATE", 0) + c.get("ARMED", 0),
        "redis_call_like": c.get("CALL", 0),
        "redis_put_like": c.get("PUT", 0),
        "log_mentions": lc.get("mentions", 0),
    })
write_csv(
    OUTDIR / "family_signal_summary.csv",
    family_summary_rows,
    [
        "family",
        "redis_rows_mentioning_family",
        "redis_hold_like",
        "redis_enter_like",
        "redis_exit_like",
        "redis_candidate_like",
        "redis_call_like",
        "redis_put_like",
        "log_mentions",
    ],
)

# 6. Best-effort hypothetical opportunity/PnL inference
# Conservative: only count an opportunity if non-HOLD entry-like/candidate-like/armed-like evidence exists.
opportunity_rows: list[dict[str, Any]] = []
for fam in FAMILIES:
    fam_rows = [r for r in decision_rows if r["family"] == fam]
    non_hold = [r for r in fam_rows if r["action"] not in ["HOLD", "UNKNOWN"]]
    entry_like = [r for r in fam_rows if r["action"] in ["ENTER", "ENTRY", "BUY", "ENTER_CALL", "ENTER_PUT"]]
    candidate_like = [r for r in fam_rows if r["action"] in ["CANDIDATE", "ARMED"]]
    exits = [r for r in fam_rows if r["action"] == "EXIT"]

    # Estimate points only when both entry-like and exit-like rows have numeric price candidates.
    estimated_points = ""
    pnl_method = "not_computable_from_available_fields"
    if entry_like and exits:
        try:
            e_nums = [float(x) for x in entry_like[-1]["numeric_candidates"].split(",") if x.strip()]
            x_nums = [float(x) for x in exits[0]["numeric_candidates"].split(",") if x.strip()]
            if e_nums and x_nums:
                estimated_points = round(x_nums[0] - e_nums[0], 3)
                pnl_method = "best_effort_first_exit_numeric_minus_entry_numeric"
        except Exception:
            pass

    opportunity_rows.append({
        "family": fam,
        "decision_rows": len(fam_rows),
        "non_hold_rows": len(non_hold),
        "entry_like_rows": len(entry_like),
        "candidate_or_armed_rows": len(candidate_like),
        "exit_like_rows": len(exits),
        "trade_opportunity_existed_best_effort": "YES" if entry_like or candidate_like else "NO",
        "hypothetical_pnl_points_best_effort": estimated_points,
        "pnl_method": pnl_method,
        "important_note": "PnL is computable only if logs/streams contain both entry and exit prices. Otherwise use candidate/opportunity count, not PnL.",
    })

write_csv(
    OUTDIR / "hypothetical_opportunity_pnl_best_effort.csv",
    opportunity_rows,
    [
        "family",
        "decision_rows",
        "non_hold_rows",
        "entry_like_rows",
        "candidate_or_armed_rows",
        "exit_like_rows",
        "trade_opportunity_existed_best_effort",
        "hypothetical_pnl_points_best_effort",
        "pnl_method",
        "important_note",
    ],
)

# 7. Markdown report
summary["streams_total"] = len([r for r in stream_rows if r.get("type") == "stream"])
summary["relevant_streams"] = relevant_streams
summary["family_summary"] = family_summary_rows
summary["opportunity_summary"] = opportunity_rows
summary["disk"] = run(["df", "-h", "/"], timeout=5)
summary["redis_memory"] = run(["redis-cli", "INFO", "memory"], timeout=5)
summary["redis_persistence"] = run(["redis-cli", "INFO", "persistence"], timeout=5)

with (OUTDIR / "summary.json").open("w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

md = []
md.append("# Live Session Forensics — Read Only")
md.append("")
md.append(f"Generated: `{summary['generated_at']}`")
md.append(f"Date: `{summary['today_iso']}`")
md.append("")
md.append("## Safety")
md.append("")
md.append(f"- Redis OK: `{summary['redis_ok']}`")
md.append("- This script did not write to Redis, did not patch code, did not send orders.")
md.append("")
md.append("## Redis Streams")
md.append("")
for r in relevant_streams:
    md.append(f"- `{r['key']}`: XLEN `{r.get('xlen')}`")
md.append("")
md.append("## Family Signal Summary")
md.append("")
md.append("| Family | Redis rows | Hold | Entry-like | Candidate/Armed | Exit-like | CALL | PUT | Log mentions |")
md.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
for r in family_summary_rows:
    md.append(
        f"| {r['family']} | {r['redis_rows_mentioning_family']} | {r['redis_hold_like']} | "
        f"{r['redis_enter_like']} | {r['redis_candidate_like']} | {r['redis_exit_like']} | "
        f"{r['redis_call_like']} | {r['redis_put_like']} | {r['log_mentions']} |"
    )
md.append("")
md.append("## Opportunity / PnL Best-Effort")
md.append("")
md.append("| Family | Opportunity? | Decision rows | Entry-like | Candidate/Armed | Exit-like | Hypothetical PnL points | Method |")
md.append("|---|---|---:|---:|---:|---:|---:|---|")
for r in opportunity_rows:
    md.append(
        f"| {r['family']} | {r['trade_opportunity_existed_best_effort']} | {r['decision_rows']} | "
        f"{r['entry_like_rows']} | {r['candidate_or_armed_rows']} | {r['exit_like_rows']} | "
        f"{r['hypothetical_pnl_points_best_effort']} | {r['pnl_method']} |"
    )
md.append("")
md.append("## Files Produced")
md.append("")
for name in [
    "summary.json",
    "redis_key_inventory.csv",
    "stream_relevant_samples.csv",
    "strategy_decision_like_rows.csv",
    "redis_hash_snapshots.csv",
    "log_forensics_summary.csv",
    "family_signal_summary.csv",
    "hypothetical_opportunity_pnl_best_effort.csv",
]:
    md.append(f"- `{name}`")
md.append("")
md.append("## Interpretation Rule")
md.append("")
md.append("If `entry_like_rows` is zero but `candidate_or_armed_rows` is positive, the session had setup/opportunity evidence but no confirmed executable paper entry in available logs/streams.")
md.append("")
md.append("If `hypothetical_pnl_points_best_effort` is blank, the available evidence did not contain enough entry/exit price data to calculate PnL safely.")
md.append("")

(OUTDIR / "LIVE_SESSION_FORENSICS_REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")

print("===== LIVE SESSION FORENSICS COMPLETE =====")
print(f"OUTDIR={OUTDIR}")
print(f"REPORT={OUTDIR / 'LIVE_SESSION_FORENSICS_REPORT.md'}")
print("")
print((OUTDIR / "LIVE_SESSION_FORENSICS_REPORT.md").read_text(encoding="utf-8"))
