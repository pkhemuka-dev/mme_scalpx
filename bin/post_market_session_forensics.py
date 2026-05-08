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
from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path
from typing import Any

ROOT = Path("/home/Lenovo/scalpx/projects/mme_scalpx")
OUTDIR = Path(sys.argv[1])
OUTDIR.mkdir(parents=True, exist_ok=True)

FAMILIES = ["MIST", "MISB", "MISC", "MISR", "MISO"]
SIDES = ["CALL", "PUT", "CE", "PE"]

TODAY = date.today()
TODAY_YYYYMMDD = TODAY.strftime("%Y%m%d")
TODAY_ISO = TODAY.isoformat()

IMPORTANT_LOG_PATTERNS = [
    "batch26m_readonly_live_capture",
    "batch26n_all_family_paper_shadow",
    "batch26m_compact_live_summary",
    "batch26m_safe_watch",
    "batch26l_mist_call_paper_watch",
    "pfeatures",
    "pstrategy",
    "pfeeds_live_raw_capture",
]

ENTRY_PATTERNS = [
    "ENTER_CALL",
    "ENTER_PUT",
    "ENTRY",
    "entry",
    "entry_like",
    "paper entry",
    "dry paper",
    "BUY",
    "buy",
]

CANDIDATE_PATTERNS = [
    "candidate",
    "CANDIDATE",
    "armed",
    "ARMED",
    "eligible",
    "ELIGIBLE",
    "opportunity",
    "setup",
    "signal",
]

HOLD_PATTERNS = [
    "HOLD",
    "hold",
    "report-only",
    "observe_only",
    "blocked",
    "veto",
    "reject",
    "not enabled",
]

EXIT_PATTERNS = [
    "EXIT",
    "exit",
    "target",
    "stop",
    "pnl",
    "PnL",
    "profit",
    "loss",
]

PRICE_KEYS = [
    "entry_price",
    "exit_price",
    "option_ltp",
    "selected_option_ltp",
    "ltp",
    "price",
    "fill_price",
    "paper_entry_price",
    "paper_exit_price",
    "pnl",
    "pnl_points",
    "points",
]

def now() -> str:
    return datetime.now().isoformat()

def run(cmd: list[str], timeout: int = 10) -> str:
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

def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", errors="replace")

def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")

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

def read_file(path: Path, max_bytes: int = 25_000_000) -> str:
    try:
        if path.suffix == ".gz":
            with gzip.open(path, "rt", errors="replace") as f:
                return f.read(max_bytes)
        with path.open("rt", errors="replace") as f:
            return f.read(max_bytes)
    except Exception as e:
        return f"__READ_ERROR__ {path}: {e}"

def redis_ping() -> bool:
    return "PONG" in run(["redis-cli", "PING"], timeout=3)

def redis_raw(cmd: list[str], timeout: int = 10) -> str:
    return run(["redis-cli", "--raw"] + cmd, timeout=timeout)

def redis_keys(pattern: str) -> list[str]:
    out = redis_raw(["KEYS", pattern], timeout=8)
    return sorted([x.strip() for x in out.splitlines() if x.strip() and not x.startswith("__ERROR__")])

def redis_type(key: str) -> str:
    out = redis_raw(["TYPE", key], timeout=4).strip().splitlines()
    return out[-1].strip() if out else ""

def redis_xlen(key: str) -> int:
    out = redis_raw(["XLEN", key], timeout=4).strip().splitlines()
    try:
        return int(out[-1])
    except Exception:
        return -1

def redis_xrange_recent(key: str, count: int = 5000) -> str:
    return redis_raw(["XREVRANGE", key, "+", "-", "COUNT", str(count)], timeout=30)

def redis_hgetall(key: str) -> str:
    return redis_raw(["HGETALL", key], timeout=10)

def parse_raw_stream(raw: str) -> list[dict[str, Any]]:
    lines = [x for x in raw.splitlines() if x != ""]
    id_re = re.compile(r"^\d+-\d+$")
    out = []
    i = 0
    while i < len(lines):
        if not id_re.match(lines[i].strip()):
            i += 1
            continue
        row = {"_id": lines[i].strip()}
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
        out.append(row)
    return out

def family_of(text: str) -> str:
    for f in FAMILIES:
        if re.search(rf"\b{f}\b", text, re.I):
            return f
    return "UNKNOWN"

def side_of(text: str) -> str:
    u = text.upper()
    if "CALL" in u or " CE" in u or "_CE" in u or "LONG_CALL" in u or "ENTER_CALL" in u:
        return "CALL"
    if "PUT" in u or " PE" in u or "_PE" in u or "LONG_PUT" in u or "ENTER_PUT" in u:
        return "PUT"
    return "UNKNOWN"

def action_of(text: str) -> str:
    u = text.upper()
    if "ENTER_CALL" in u:
        return "ENTER_CALL"
    if "ENTER_PUT" in u:
        return "ENTER_PUT"
    if "ENTRY" in u or " BUY" in u or '"BUY"' in u:
        return "ENTRY"
    if "EXIT" in u:
        return "EXIT"
    if "CANDIDATE" in u or "ELIGIBLE" in u or "OPPORTUNITY" in u:
        return "CANDIDATE"
    if "ARMED" in u:
        return "ARMED"
    if "HOLD" in u:
        return "HOLD"
    if "BLOCK" in u or "VETO" in u or "REJECT" in u:
        return "BLOCKED"
    return "UNKNOWN"

def count_any(text: str, pats: list[str]) -> int:
    total = 0
    for p in pats:
        total += len(re.findall(re.escape(p), text, flags=re.I))
    return total

def extract_prices(text: str) -> dict[str, list[float]]:
    result: dict[str, list[float]] = defaultdict(list)

    for key in PRICE_KEYS:
        patterns = [
            rf'"{re.escape(key)}"\s*:\s*"?(-?\d+(?:\.\d+)?)"?',
            rf"'{re.escape(key)}'\s*:\s*'?(-?\d+(?:\.\d+)?)'?",
            rf"\b{re.escape(key)}\b\s*[=:]\s*(-?\d+(?:\.\d+)?)",
        ]
        for pat in patterns:
            for m in re.finditer(pat, text, flags=re.I):
                try:
                    result[key].append(float(m.group(1)))
                except Exception:
                    pass

    return dict(result)

def first_price(price_map: dict[str, list[float]], keys: list[str]) -> float | None:
    for k in keys:
        vals = price_map.get(k) or []
        if vals:
            return vals[0]
    return None

def latest_price(price_map: dict[str, list[float]], keys: list[str]) -> float | None:
    for k in keys:
        vals = price_map.get(k) or []
        if vals:
            return vals[-1]
    return None

def classify_file(path: Path) -> str:
    name = path.name.lower()
    if "pfeeds" in name or "feed" in name:
        return "feeds"
    if "pfeatures" in name or "feature" in name:
        return "features"
    if "pstrategy" in name or "strategy" in name:
        return "strategy"
    if "paper" in name:
        return "paper_shadow"
    if "capture" in name:
        return "capture"
    return "other"

def important_today_files() -> list[Path]:
    files: list[Path] = []
    roots = [ROOT / "run/live_capture", ROOT / "run/proofs", ROOT / "run/reports"]
    for base in roots:
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            name = p.name
            lowered = name.lower()
            if TODAY_YYYYMMDD in name or "20260430" in name:
                files.append(p)
                continue
            if any(x in lowered for x in IMPORTANT_LOG_PATTERNS):
                # include recent files too
                if datetime.fromtimestamp(p.stat().st_mtime).date() == TODAY:
                    files.append(p)
    return sorted(set(files), key=lambda x: (str(x.parent), x.name))

def text_excerpt_lines(text: str, max_lines: int = 100) -> str:
    lines = []
    for line in text.splitlines():
        l = line.strip()
        if not l:
            continue
        if (
            any(re.search(rf"\b{f}\b", l, re.I) for f in FAMILIES)
            or count_any(l, ENTRY_PATTERNS + CANDIDATE_PATTERNS + HOLD_PATTERNS + EXIT_PATTERNS) > 0
        ):
            lines.append(l[:1600])
        if len(lines) >= max_lines:
            break
    return "\n".join(lines)

summary: dict[str, Any] = {
    "generated_at": now(),
    "root": str(ROOT),
    "today": TODAY_ISO,
    "readonly": True,
    "redis_ping": redis_ping(),
}

# System snapshot
system_snapshot = {
    "df_h_root": run(["df", "-h", "/"], timeout=5),
    "free_h": run(["free", "-h"], timeout=5),
    "redis_memory": run(["redis-cli", "INFO", "memory"], timeout=5),
    "redis_persistence": run(["redis-cli", "INFO", "persistence"], timeout=5),
    "orders_xlen": run(["redis-cli", "XLEN", "orders:mme:stream"], timeout=5),
    "position": run(["redis-cli", "HGETALL", "state:position:mme"], timeout=5),
}
write_json(OUTDIR / "system_snapshot.json", system_snapshot)

# Redis inventory
redis_inventory: list[dict[str, Any]] = []
stream_rows: list[dict[str, Any]] = []
hash_rows: list[dict[str, Any]] = []

if summary["redis_ping"]:
    all_keys = []
    for pat in [
        "*mme*",
        "*MME*",
        "*tick*",
        "*feature*",
        "*decision*",
        "*order*",
        "*trade*",
        "*position*",
        "*runtime*",
        "*risk*",
        "*health*",
    ]:
        for k in redis_keys(pat):
            if k not in all_keys:
                all_keys.append(k)

    for k in sorted(all_keys):
        t = redis_type(k)
        row: dict[str, Any] = {"key": k, "type": t}
        if t == "stream":
            row["xlen"] = redis_xlen(k)
            stream_rows.append(row)
        elif t == "hash":
            raw = redis_hgetall(k)
            row["excerpt"] = raw[:3000]
            hash_rows.append(row)
        redis_inventory.append(row)

write_csv(OUTDIR / "redis_inventory.csv", redis_inventory)
write_csv(OUTDIR / "redis_hashes.csv", hash_rows)

# Stream samples and strategy decision evidence
stream_samples: list[dict[str, Any]] = []
family_counter: dict[str, Counter] = {f: Counter() for f in FAMILIES}
family_counter["UNKNOWN"] = Counter()

for s in stream_rows:
    key = s["key"]
    if not any(x in key.lower() for x in ["tick", "feature", "decision", "order", "trade"]):
        continue

    raw = redis_xrange_recent(key, count=7000)
    parsed = parse_raw_stream(raw)

    for row in parsed:
        text = json.dumps(row, ensure_ascii=False)
        fam = family_of(text)
        side = side_of(text)
        action = action_of(text)
        prices = extract_prices(text)

        family_counter[fam]["rows"] += 1
        family_counter[fam][action] += 1
        family_counter[fam][side] += 1
        if prices:
            family_counter[fam]["rows_with_price_fields"] += 1

        if fam != "UNKNOWN" or action != "UNKNOWN" or any(x in key.lower() for x in ["decision", "feature"]):
            stream_samples.append({
                "source": "redis_stream",
                "stream": key,
                "id": row.get("_id", ""),
                "family": fam,
                "side": side,
                "action": action,
                "price_fields": json.dumps(prices, ensure_ascii=False)[:1000],
                "excerpt": text[:2400],
            })

write_csv(OUTDIR / "redis_stream_strategy_evidence.csv", stream_samples)

# Log file analysis
files = important_today_files()
file_rows: list[dict[str, Any]] = []
line_evidence: list[dict[str, Any]] = []
log_family_counter: dict[str, Counter] = {f: Counter() for f in FAMILIES}
log_family_counter["UNKNOWN"] = Counter()

for p in files:
    rel = str(p.relative_to(ROOT))
    text = read_file(p)
    lower = text.lower()

    prices = extract_prices(text)
    frow: dict[str, Any] = {
        "path": rel,
        "kind": classify_file(p),
        "size_mb": round(p.stat().st_size / 1024 / 1024, 3),
        "lines_approx": text.count("\n") + 1,
        "entry_mentions": count_any(text, ENTRY_PATTERNS),
        "candidate_mentions": count_any(text, CANDIDATE_PATTERNS),
        "hold_block_mentions": count_any(text, HOLD_PATTERNS),
        "exit_pnl_mentions": count_any(text, EXIT_PATTERNS),
        "price_field_types_found": ",".join(sorted(prices.keys())),
    }

    for fam in FAMILIES:
        mentions = len(re.findall(rf"\b{fam}\b", text, flags=re.I))
        frow[f"{fam.lower()}_mentions"] = mentions
        if mentions:
            log_family_counter[fam]["mentions"] += mentions
            log_family_counter[fam]["files"] += 1

    file_rows.append(frow)

    for idx, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        if (
            any(re.search(rf"\b{fam}\b", line, re.I) for fam in FAMILIES)
            or count_any(line, ENTRY_PATTERNS + CANDIDATE_PATTERNS + HOLD_PATTERNS + EXIT_PATTERNS) > 0
        ):
            fam = family_of(line)
            action = action_of(line)
            side = side_of(line)
            lprices = extract_prices(line)
            log_family_counter[fam]["line_rows"] += 1
            log_family_counter[fam][action] += 1
            log_family_counter[fam][side] += 1
            if lprices:
                log_family_counter[fam]["lines_with_price_fields"] += 1
            line_evidence.append({
                "source": "log_file",
                "path": rel,
                "line_no": idx,
                "family": fam,
                "side": side,
                "action": action,
                "price_fields": json.dumps(lprices, ensure_ascii=False)[:1000],
                "line": line[:2400],
            })
            if len(line_evidence) > 50000:
                break

write_csv(OUTDIR / "today_file_inventory.csv", file_rows)
write_csv(OUTDIR / "log_line_strategy_evidence.csv", line_evidence)

# Family combined summary
family_summary: list[dict[str, Any]] = []
for fam in FAMILIES:
    rc = family_counter[fam]
    lc = log_family_counter[fam]

    entry_like = (
        rc.get("ENTER_CALL", 0) + rc.get("ENTER_PUT", 0) + rc.get("ENTRY", 0)
        + lc.get("ENTER_CALL", 0) + lc.get("ENTER_PUT", 0) + lc.get("ENTRY", 0)
    )
    candidate_like = (
        rc.get("CANDIDATE", 0) + rc.get("ARMED", 0)
        + lc.get("CANDIDATE", 0) + lc.get("ARMED", 0)
    )
    hold_block = (
        rc.get("HOLD", 0) + rc.get("BLOCKED", 0)
        + lc.get("HOLD", 0) + lc.get("BLOCKED", 0)
    )
    exit_like = rc.get("EXIT", 0) + lc.get("EXIT", 0)
    price_rows = rc.get("rows_with_price_fields", 0) + lc.get("lines_with_price_fields", 0)

    family_summary.append({
        "family": fam,
        "redis_rows": rc.get("rows", 0),
        "log_mentions": lc.get("mentions", 0),
        "log_files": lc.get("files", 0),
        "entry_like_count": entry_like,
        "candidate_or_armed_count": candidate_like,
        "hold_or_block_count": hold_block,
        "exit_or_pnl_count": exit_like,
        "call_like_count": rc.get("CALL", 0) + lc.get("CALL", 0),
        "put_like_count": rc.get("PUT", 0) + lc.get("PUT", 0),
        "price_rows": price_rows,
        "opportunity_best_effort": "YES" if entry_like > 0 or candidate_like > 0 else "NO",
    })

write_csv(OUTDIR / "family_combined_summary.csv", family_summary)

# Best effort PnL reconstruction.
# This is intentionally conservative.
all_evidence = stream_samples + line_evidence
pnl_rows: list[dict[str, Any]] = []

for fam in FAMILIES:
    fam_ev = [e for e in all_evidence if e.get("family") == fam]
    entries = [e for e in fam_ev if e.get("action") in ("ENTER_CALL", "ENTER_PUT", "ENTRY")]
    exits = [e for e in fam_ev if e.get("action") == "EXIT"]

    candidates = [e for e in fam_ev if e.get("action") in ("CANDIDATE", "ARMED")]
    holds = [e for e in fam_ev if e.get("action") in ("HOLD", "BLOCKED")]

    estimated = ""
    method = "not_computable"
    entry_excerpt = ""
    exit_excerpt = ""

    if entries and exits:
        entry = entries[-1]
        exit_ = exits[0]
        try:
            ep = extract_prices(json.dumps(entry, ensure_ascii=False))
            xp = extract_prices(json.dumps(exit_, ensure_ascii=False))
            entry_price = first_price(ep, ["entry_price", "paper_entry_price", "fill_price", "option_ltp", "selected_option_ltp", "ltp", "price"])
            exit_price = first_price(xp, ["exit_price", "paper_exit_price", "fill_price", "option_ltp", "selected_option_ltp", "ltp", "price"])
            if entry_price is not None and exit_price is not None:
                estimated = round(exit_price - entry_price, 4)
                method = "exit_price_minus_entry_price_best_effort"
                entry_excerpt = str(entry.get("line") or entry.get("excerpt") or "")[:800]
                exit_excerpt = str(exit_.get("line") or exit_.get("excerpt") or "")[:800]
        except Exception as e:
            method = f"pnl_parse_error:{e}"

    pnl_rows.append({
        "family": fam,
        "entries_found": len(entries),
        "exits_found": len(exits),
        "candidates_or_armed_found": len(candidates),
        "holds_or_blocks_found": len(holds),
        "opportunity_existed_best_effort": "YES" if entries or candidates else "NO",
        "hypothetical_pnl_points_best_effort": estimated,
        "method": method,
        "entry_excerpt": entry_excerpt,
        "exit_excerpt": exit_excerpt,
    })

write_csv(OUTDIR / "missed_trade_pnl_best_effort.csv", pnl_rows)

# Special focus files excerpts
focus_rows: list[dict[str, Any]] = []
for p in files:
    if any(x in p.name.lower() for x in IMPORTANT_LOG_PATTERNS):
        text = read_file(p, max_bytes=10_000_000)
        focus_rows.append({
            "path": str(p.relative_to(ROOT)),
            "kind": classify_file(p),
            "size_mb": round(p.stat().st_size / 1024 / 1024, 3),
            "excerpt": text_excerpt_lines(text, max_lines=120),
        })
write_csv(OUTDIR / "important_log_excerpts.csv", focus_rows)

# Markdown report
md: list[str] = []
md.append("# Batch 26-O1 Post-Market Read-Only Session Forensics")
md.append("")
md.append(f"Generated: `{summary['generated_at']}`")
md.append(f"Root: `{ROOT}`")
md.append("")
md.append("## Safety")
md.append("")
md.append("- Read-only analysis.")
md.append("- No code patch to runtime modules.")
md.append("- No Redis writes.")
md.append("- No service start.")
md.append("- No order send.")
md.append("")
md.append("## Infra / Safety State")
md.append("")
md.append("```text")
md.append(system_snapshot["df_h_root"].strip())
md.append(system_snapshot["free_h"].strip())
md.append("orders:mme:stream = " + system_snapshot["orders_xlen"].strip())
md.append("state:position:mme = " + system_snapshot["position"].strip())
md.append("```")
md.append("")
md.append("## Redis Streams Found")
md.append("")
md.append("| Stream | XLEN |")
md.append("|---|---:|")
for s in sorted(stream_rows, key=lambda x: str(x.get("key"))):
    if any(x in s["key"].lower() for x in ["tick", "feature", "decision", "order", "trade"]):
        md.append(f"| `{s['key']}` | {s.get('xlen', '')} |")
md.append("")
md.append("## Family-Wise Signal / Opportunity Summary")
md.append("")
md.append("| Family | Redis rows | Log mentions | Entry-like | Candidate/Armed | Hold/Block | Exit/PnL | CALL | PUT | Price rows | Opportunity? |")
md.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|")
for r in family_summary:
    md.append(
        f"| {r['family']} | {r['redis_rows']} | {r['log_mentions']} | {r['entry_like_count']} | "
        f"{r['candidate_or_armed_count']} | {r['hold_or_block_count']} | {r['exit_or_pnl_count']} | "
        f"{r['call_like_count']} | {r['put_like_count']} | {r['price_rows']} | {r['opportunity_best_effort']} |"
    )
md.append("")
md.append("## Missed Trade / Hypothetical PnL Best-Effort")
md.append("")
md.append("| Family | Opportunity? | Entries | Candidates/Armed | Exits | Holds/Blocks | PnL points | Method |")
md.append("|---|---|---:|---:|---:|---:|---:|---|")
for r in pnl_rows:
    md.append(
        f"| {r['family']} | {r['opportunity_existed_best_effort']} | {r['entries_found']} | "
        f"{r['candidates_or_armed_found']} | {r['exits_found']} | {r['holds_or_blocks_found']} | "
        f"{r['hypothetical_pnl_points_best_effort']} | {r['method']} |"
    )
md.append("")
md.append("## Files Analyzed")
md.append("")
md.append("| File | Kind | Size MB | Entry | Candidate | Hold/Block | Exit/PnL |")
md.append("|---|---|---:|---:|---:|---:|---:|")
for r in file_rows:
    md.append(
        f"| `{r['path']}` | {r['kind']} | {r['size_mb']} | {r['entry_mentions']} | "
        f"{r['candidate_mentions']} | {r['hold_block_mentions']} | {r['exit_pnl_mentions']} |"
    )
md.append("")
md.append("## Output Files")
md.append("")
for fname in [
    "POST_MARKET_FORENSICS_REPORT.md",
    "system_snapshot.json",
    "redis_inventory.csv",
    "redis_hashes.csv",
    "redis_stream_strategy_evidence.csv",
    "today_file_inventory.csv",
    "log_line_strategy_evidence.csv",
    "family_combined_summary.csv",
    "missed_trade_pnl_best_effort.csv",
    "important_log_excerpts.csv",
]:
    md.append(f"- `{fname}`")
md.append("")
md.append("## Interpretation")
md.append("")
md.append("- `Entry-like` means the evidence contains an actual entry-style row or line.")
md.append("- `Candidate/Armed` means setup/opportunity evidence existed but may have been blocked by HOLD/report-only, gates, or missing executable entry approval.")
md.append("- PnL is intentionally blank unless both entry and exit price evidence can be extracted safely.")
md.append("- If Opportunity is YES but PnL is blank, the session should be replayed from captured ticks/features with an explicit paper fill model.")
md.append("")

report = "\n".join(md) + "\n"
write_text(OUTDIR / "POST_MARKET_FORENSICS_REPORT.md", report)

write_json(OUTDIR / "summary.json", {
    "summary": summary,
    "system_snapshot": system_snapshot,
    "family_summary": family_summary,
    "pnl_rows": pnl_rows,
    "files_analyzed_count": len(file_rows),
    "stream_count": len(stream_rows),
})

print("===== POST-MARKET FORENSICS COMPLETE =====")
print(f"OUTDIR={OUTDIR}")
print(f"REPORT={OUTDIR / 'POST_MARKET_FORENSICS_REPORT.md'}")
print("")
print(report)
