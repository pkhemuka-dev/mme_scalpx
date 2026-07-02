#!/usr/bin/env bash
set -euo pipefail

cd /home/Lenovo/scalpx/projects/mme_scalpx

TAG="${1:-LANE-X-R10K_REUSABLE_FAMILY_PROJECTION_BOARD_$(date +%Y%m%d_%H%M%S)}"
mkdir -p run/proofs run/audits run/handoffs

OUT="run/audits/${TAG}_audit.txt"
PROOF="run/proofs/${TAG}.json"
REPORT="run/audits/${TAG}_report.md"
CSV="run/audits/${TAG}_family_projection_board.csv"
BOARD_MD="run/audits/${TAG}_family_projection_board.md"
SRC_AUDIT="run/audits/${TAG}_source_marker_audit.txt"

echo "=== R10K REUSABLE FAMILY PROJECTION READINESS BOARD ===" | tee "$OUT"
echo "NO START / NO ARM / NO ORDER / NO BROKER ORDER / NO LIVE ORDER / NO REDIS DELETE / NO LOCK DELETE / NO XTRIM / NO FLUSH" | tee -a "$OUT"
echo "TAG=$TAG" | tee -a "$OUT"
echo "CREATED=$(date -Is)" | tee -a "$OUT"

{
  echo "===== SOURCE MARKERS ====="
  echo
  echo "R10D execution/pstatus markers:"
  grep -RIn "R10D_NOGROUP_RECOVERY_FINAL_OVERRIDE_STATIC_ONLY_NO_ORDER\|R10D_REDIS_POLICY_AND_POSITION_HASH_FAIL_CLOSED" app/mme_scalpx/services/execution.py bin/pstatus 2>/dev/null || true

  echo
  echo "R38 projection markers:"
  grep -RIn "R38EM_R1_PROJECTION_DIAG_AND_SYMBOL_FALLBACK_PATCH\|r38ee_projection_projected\|r38ee_projection_blocker\|r38ee_extracted_family\|r38ee_extracted_side\|r38ee_extracted_action\|r38ee_extracted_token\|r38ee_extracted_symbol" app/mme_scalpx/services/strategy.py bin 2>/dev/null || true

  echo
  echo "Combined wrapper scripts:"
  ls -l \
    bin/r10i_tomorrow_combined_r10h_r38_preflight_no_start.sh \
    bin/r10j_tomorrow_one_lot_controlled_paper_wrapper_requires_fresh_approval.sh \
    bin/r38en_tomorrow_parallel_scope_controlled_paper_runner.sh \
    bin/r38eo_tomorrow_preflight_no_start.sh 2>/dev/null || true
} | tee "$SRC_AUDIT" | tee -a "$OUT"

echo | tee -a "$OUT"
echo "=== HARD SAFETY SNAPSHOT ===" | tee -a "$OUT"
{
  echo "DATE=$(date -Is)"

  echo
  echo "APP PROCESSES:"
  ps -eo pid,ppid,stat,etime,lstart,cmd | grep -E 'app\.mme_scalpx\.main|controlled_paper|risk|execution|feeds|features|strategy' | grep -v grep || true

  echo
  echo "LOCKS:"
  for k in lock:execution lock:feeds lock:monitor; do
    echo "$k value=$(redis-cli GET "$k" 2>/dev/null || true) ttl=$(redis-cli TTL "$k" 2>/dev/null || true)"
  done

  echo
  echo "STREAM LENGTHS:"
  for s in orders:mme:stream risk:mme:stream execution:mme:stream trades:ledger:stream cmd:mme:stream decisions:mme:stream features:mme:stream ticks:mme:fut:zerodha:stream ticks:mme:fut:stream ticks:mme:opt:selected:zerodha:stream; do
    echo "$s $(redis-cli XLEN "$s" 2>/dev/null || echo ERR)"
  done

  echo
  echo "REDIS POLICY:"
  redis-cli CONFIG GET maxmemory-policy 2>/dev/null || true

  echo
  echo "POSITION:"
  redis-cli HGETALL state:position:mme 2>/dev/null || true
} | tee -a "$OUT"

python3 - "$TAG" "$PROOF" "$REPORT" "$CSV" "$BOARD_MD" "$SRC_AUDIT" <<'PY' | tee -a "$OUT"
import csv
import json
import subprocess
import sys
from collections import defaultdict, Counter
from datetime import datetime, timezone
from pathlib import Path

tag, proof, report, csv_path, board_md, src_audit = sys.argv[1:7]
ROOT = Path("/home/Lenovo/scalpx/projects/mme_scalpx")
FAMILIES = ["MIST", "MISB", "MISC", "MISR", "MISO"]
SIDES = ["CALL", "PUT"]
ENTER_ACTIONS = {"ENTER_CALL", "ENTER_PUT", "BUY_CALL", "BUY_PUT"}

def cmd(c, timeout=20):
    p = subprocess.run(c, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
    return p.returncode, p.stdout, p.stderr

def redis_config(name):
    vals = [x.strip() for x in cmd(["redis-cli", "CONFIG", "GET", name])[1].splitlines() if x.strip()]
    return vals[-1] if len(vals) >= 2 else ""

def hgetall(k):
    vals = cmd(["redis-cli", "HGETALL", k])[1].splitlines()
    return {vals[i]: vals[i+1] for i in range(0, len(vals)-1, 2)}

def get(k):
    return cmd(["redis-cli", "GET", k])[1].strip()

def xlen(s):
    try:
        return int(cmd(["redis-cli", "XLEN", s])[1].strip() or 0)
    except Exception:
        return -1

def decode_id_ms(stream_id):
    try:
        return int(str(stream_id).split("-")[0])
    except Exception:
        return None

def parse_redis_stream_raw(raw):
    # redis-cli --raw XREVRANGE output is:
    # id
    # field
    # value
    # field
    # value
    # id
    # ...
    lines = raw.splitlines()
    entries = []
    i = 0
    while i < len(lines):
        sid = lines[i].strip()
        if "-" not in sid:
            i += 1
            continue
        i += 1
        fields = {}
        while i + 1 < len(lines):
            nxt = lines[i].strip()
            if "-" in nxt and i + 2 < len(lines):
                # Ambiguous field may contain hyphen, but stream IDs are usually numeric-numeric.
                a, b = nxt.split("-", 1)
                if a.isdigit() and b.isdigit():
                    break
            key = lines[i]
            val = lines[i+1] if i + 1 < len(lines) else ""
            fields[key] = val
            i += 2
        entries.append((sid, fields))
    return entries

def try_json(v):
    if not isinstance(v, str):
        return v
    s = v.strip()
    if not s:
        return v
    if (s.startswith("{") and s.endswith("}")) or (s.startswith("[") and s.endswith("]")):
        try:
            return json.loads(s)
        except Exception:
            return v
    return v

def flatten(obj, prefix="", out=None):
    if out is None:
        out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            kk = f"{prefix}.{k}" if prefix else str(k)
            flatten(v, kk, out)
    elif isinstance(obj, list):
        # Keep first few list items only for key discovery; also preserve length.
        out[f"{prefix}.__len__"] = len(obj)
        for idx, v in enumerate(obj[:5]):
            flatten(v, f"{prefix}.{idx}", out)
    else:
        out[prefix] = obj
    return out

def text(v):
    if v is None:
        return ""
    if isinstance(v, bytes):
        try:
            return v.decode()
        except Exception:
            return repr(v)
    return str(v)

def first_key(flat, names):
    for name in names:
        # direct suffix match
        for k, v in flat.items():
            if k == name or k.endswith("." + name):
                if text(v).strip() != "":
                    return text(v).strip()
    return ""

def intish(v):
    try:
        if v is None or str(v).strip() == "":
            return 0
        return int(float(str(v).strip()))
    except Exception:
        return 0

def infer_entry(sid, fields):
    parsed = {}
    # include raw fields
    for k, v in fields.items():
        parsed[k] = try_json(v)
    # if there is a single huge json payload, flatten it too
    flat = {}
    for k, v in parsed.items():
        flatten(v, k, flat)
    raw_blob = json.dumps(parsed, default=str, ensure_ascii=False)[:50000]
    raw_upper = raw_blob.upper()

    fam = first_key(flat, [
        "r38ee_extracted_family", "family_id", "family", "doctrine_id",
        "selected_family", "scope_family", "env_family"
    ]).upper()

    side = first_key(flat, [
        "r38ee_extracted_side", "side", "branch_id", "option_side",
        "selected_side", "scope_side", "env_side"
    ]).upper()

    action = first_key(flat, [
        "r38ee_extracted_action", "action", "flat_action", "payload_action",
        "decision_action", "selected_action", "scope_action", "env_action"
    ]).upper()

    qty = first_key(flat, ["qty", "quantity", "order_qty", "lots", "qty_lots"])
    token = first_key(flat, [
        "r38ee_extracted_token", "instrument_token", "option_token", "token",
        "selected_token", "scope_token", "env_token"
    ])
    symbol = first_key(flat, [
        "r38ee_extracted_symbol", "trading_symbol", "option_symbol", "symbol",
        "selected_symbol", "scope_symbol", "env_symbol"
    ])

    projected = intish(first_key(flat, ["r38ee_projection_projected", "projected"]))
    blocker = first_key(flat, ["r38ee_projection_blocker", "blocked_reason", "failed_stage", "reason"])
    eligible = first_key(flat, ["eligible", "branch_ready", "entry_pass"])
    score = first_key(flat, ["score", "setup_score", "candidate_score"])

    # Fallback inference from raw blob when fields are nested/odd.
    if not fam:
        for f in FAMILIES:
            if f in raw_upper:
                fam = f
                break
    if not side:
        if "ENTER_CALL" in raw_upper or '"CALL"' in raw_upper or "'CALL'" in raw_upper:
            side = "CALL"
        elif "ENTER_PUT" in raw_upper or '"PUT"' in raw_upper or "'PUT'" in raw_upper:
            side = "PUT"
    if not action:
        for a in ENTER_ACTIONS.union({"HOLD"}):
            if a in raw_upper:
                action = a
                break

    candidate_like = bool(fam in FAMILIES and side in SIDES and (
        "CANDIDATE" in raw_upper or "ELIGIBLE" in raw_upper or "ENTER_" in raw_upper or projected
    ))
    top_enter = action in {"ENTER_CALL", "ENTER_PUT"}
    qty_positive = intish(qty) > 0
    symbol_present = bool(symbol.strip())
    token_present = bool(token.strip())

    return {
        "stream_id": sid,
        "stream_ms": decode_id_ms(sid),
        "family": fam if fam in FAMILIES else "",
        "side": side if side in SIDES else "",
        "action": action,
        "qty": qty,
        "qty_positive": qty_positive,
        "token": token,
        "symbol": symbol,
        "projected": projected,
        "blocker": blocker,
        "eligible": eligible,
        "score": score,
        "candidate_like": candidate_like,
        "top_enter": top_enter,
        "token_present": token_present,
        "symbol_present": symbol_present,
        "raw_field_count": len(flat),
        "raw_excerpt": raw_blob[:1200],
    }

# Pull recent decision rows only. This is read-only.
rc, raw, err = cmd(["redis-cli", "--raw", "XREVRANGE", "decisions:mme:stream", "+", "-", "COUNT", "5000"], timeout=30)
entries = parse_redis_stream_raw(raw) if rc == 0 else []
records = [infer_entry(sid, fields) for sid, fields in entries]

board = {}
for fam in FAMILIES:
    for side in SIDES:
        key = (fam, side)
        rows = [r for r in records if r["family"] == fam and r["side"] == side]
        candidate_rows = [r for r in rows if r["candidate_like"]]
        projected_rows = [r for r in rows if r["projected"] == 1]
        top_enter_rows = [r for r in rows if r["top_enter"]]
        executable_rows = [r for r in rows if r["top_enter"] and r["qty_positive"] and r["token_present"]]
        symbol_ok_rows = [r for r in executable_rows if r["symbol_present"]]
        latest = rows[0] if rows else {}
        blockers = Counter([r["blocker"] for r in rows if r["blocker"]]).most_common(5)
        actions = Counter([r["action"] for r in rows if r["action"]]).most_common(5)

        readiness = "NOT_READY"
        reason = "no_family_side_rows"
        if rows:
            reason = "no_candidate_or_projection"
        if candidate_rows:
            reason = "candidate_seen_but_no_top_level_enter"
            readiness = "CANDIDATE_ONLY"
        if projected_rows:
            reason = "r38_projection_seen"
            readiness = "PROJECTED"
        if executable_rows:
            reason = "top_level_enter_qty_token_seen"
            readiness = "ENTER_READY"
        if symbol_ok_rows:
            reason = "top_level_enter_qty_token_symbol_seen"
            readiness = "ENTER_READY_SYMBOL_OK"

        board[key] = {
            "family": fam,
            "side": side,
            "recent_rows": len(rows),
            "candidate_like_rows": len(candidate_rows),
            "r38_projected_rows": len(projected_rows),
            "top_level_enter_rows": len(top_enter_rows),
            "executable_enter_qty_token_rows": len(executable_rows),
            "symbol_ok_executable_rows": len(symbol_ok_rows),
            "latest_action": latest.get("action", ""),
            "latest_qty": latest.get("qty", ""),
            "latest_token": latest.get("token", ""),
            "latest_symbol": latest.get("symbol", ""),
            "latest_blocker": latest.get("blocker", ""),
            "latest_score": latest.get("score", ""),
            "latest_stream_id": latest.get("stream_id", ""),
            "top_actions": actions,
            "top_blockers": blockers,
            "readiness": readiness,
            "reason": reason,
        }

# safety checks
ps = cmd(["ps", "-eo", "pid,ppid,stat,etime,cmd"])[1]
app = [l for l in ps.splitlines() if "app.mme_scalpx.main" in l]
locks = {"execution": get("lock:execution"), "feeds": get("lock:feeds"), "monitor": get("lock:monitor")}
streams = {
    "orders": xlen("orders:mme:stream"),
    "risk": xlen("risk:mme:stream"),
    "execution": xlen("execution:mme:stream"),
    "trades": xlen("trades:ledger:stream"),
    "cmd": xlen("cmd:mme:stream"),
    "decisions": xlen("decisions:mme:stream"),
    "features": xlen("features:mme:stream"),
}
pos = hgetall("state:position:mme")
position_strict_flat = (
    pos.get("has_position") == "0"
    and str(pos.get("position_side", "")).upper() == "FLAT"
    and pos.get("qty_lots") == "0"
    and pos.get("qty_units") == "0"
)
src = Path(src_audit).read_text(errors="replace") if Path(src_audit).exists() else ""

checks = {
    "redis_policy": redis_config("maxmemory-policy"),
    "position_strict_flat": position_strict_flat,
    "r10d_marker_present": "R10D_NOGROUP_RECOVERY_FINAL_OVERRIDE_STATIC_ONLY_NO_ORDER" in src,
    "r38_projection_marker_present": ("r38ee_projection_projected" in src or "R38EM_R1_PROJECTION_DIAG_AND_SYMBOL_FALLBACK_PATCH" in src),
    "r10i_preflight_present": Path("bin/r10i_tomorrow_combined_r10h_r38_preflight_no_start.sh").exists(),
    "r10j_runner_present": Path("bin/r10j_tomorrow_one_lot_controlled_paper_wrapper_requires_fresh_approval.sh").exists(),
    "app_process_count": len(app),
    "locks_clear": not any(locks.values()),
    "orders_zero": streams["orders"] == 0,
    "runtime_zero": streams["risk"] == 0 and streams["execution"] == 0 and streams["trades"] == 0,
    "cmd_zero": streams["cmd"] == 0,
    "decision_rows_scanned": len(records),
}

blockers = []
if checks["redis_policy"] != "noeviction":
    blockers.append("redis_policy_not_noeviction")
if not position_strict_flat:
    blockers.append("position_not_strict_flat")
if not checks["r10d_marker_present"]:
    blockers.append("r10d_marker_missing")
if not checks["r38_projection_marker_present"]:
    blockers.append("r38_projection_marker_missing")
if not checks["r10i_preflight_present"]:
    blockers.append("r10i_preflight_missing")
if not checks["r10j_runner_present"]:
    blockers.append("r10j_runner_missing")
if app:
    blockers.append("app_process_running")
if not checks["locks_clear"]:
    blockers.append("locks_not_clear")
if not checks["orders_zero"]:
    blockers.append("orders_nonzero")
if not checks["runtime_zero"]:
    blockers.append("runtime_nonzero")
if not checks["cmd_zero"]:
    blockers.append("cmd_nonzero")

# These are not blockers after-market; they are findings for tomorrow.
ready_now = [v for v in board.values() if v["readiness"].startswith("ENTER_READY")]
projected_now = [v for v in board.values() if v["readiness"] == "PROJECTED"]
candidate_only = [v for v in board.values() if v["readiness"] == "CANDIDATE_ONLY"]

classification = "R10K_FAMILY_PROJECTION_BOARD_PASS_NO_START_NO_ORDER" if not blockers else "R10K_FAMILY_PROJECTION_BOARD_REVIEW_REQUIRED_NO_START_NO_ORDER"

rows = list(board.values())
with open(csv_path, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=[
        "family","side","readiness","reason","recent_rows","candidate_like_rows",
        "r38_projected_rows","top_level_enter_rows","executable_enter_qty_token_rows",
        "symbol_ok_executable_rows","latest_action","latest_qty","latest_token",
        "latest_symbol","latest_blocker","latest_score","latest_stream_id",
    ])
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in w.fieldnames})

md = []
md.append(f"# {tag} — Family Projection Readiness Board")
md.append("")
md.append(f"classification: **{classification}**")
md.append("")
md.append("## Safety blockers")
if blockers:
    md += [f"- `{b}`" for b in blockers]
else:
    md.append("- none")
md.append("")
md.append("## Hard checks")
for k, v in checks.items():
    md.append(f"- {k}: `{v}`")
md.append("")
md.append("## Board")
md.append("")
md.append("| family | side | readiness | reason | rows | candidate | projected | top_ENTER | exec_qty_token | symbol_ok | latest_action | latest_blocker | latest_token | latest_symbol |")
md.append("|---|---:|---|---|---:|---:|---:|---:|---:|---:|---|---|---|---|")
for r in rows:
    md.append("| {family} | {side} | {readiness} | {reason} | {recent_rows} | {candidate_like_rows} | {r38_projected_rows} | {top_level_enter_rows} | {executable_enter_qty_token_rows} | {symbol_ok_executable_rows} | {latest_action} | {latest_blocker} | {latest_token} | {latest_symbol} |".format(**{k: str(v).replace("|","/") for k,v in r.items()}))
md.append("")
md.append("## Interpretation")
if ready_now:
    md.append("- At least one family/side has top-level ENTER-like readiness in recent decision rows. Tomorrow still needs fresh same-session validation before any runner.")
elif projected_now:
    md.append("- Projection was seen, but executable ENTER+qty+token was not fully confirmed in recent rows.")
elif candidate_only:
    md.append("- Candidate-like rows exist, but no top-level projected/executable ENTER was confirmed. This matches the earlier R38 learning.")
else:
    md.append("- No recent production family/side is executable from current after-market stream state. This is normal after-market; tomorrow must use fresh live data.")
md.append("")
md.append("## Next action")
md.append("- After-market: do not start runtime.")
md.append("- Tomorrow: run `bin/r10i_tomorrow_combined_r10h_r38_preflight_no_start.sh`, then choose the freshest clean family/side under R10J wrapper only after explicit approval.")
md.append("")
md.append("## Safety")
md.append("- no start")
md.append("- no arm")
md.append("- no order")
md.append("- no broker order")
md.append("- no live order")
md.append("- no Redis delete")
md.append("- no lock delete")
md.append("- no XTRIM")
md.append("- no FLUSH")
Path(board_md).write_text("\n".join(md) + "\n")

data = {
    "tag": tag,
    "created_at": datetime.now(timezone.utc).isoformat(),
    "classification": classification,
    "blockers": blockers,
    "checks": checks,
    "board": rows,
    "findings": {
        "enter_ready_count": len(ready_now),
        "projected_count": len(projected_now),
        "candidate_only_count": len(candidate_only),
    },
    "artifacts": {
        "csv": csv_path,
        "board_md": board_md,
        "report": report,
        "source_audit": src_audit,
    },
    "safety": {
        "no_start": True,
        "no_arm": True,
        "no_order": True,
        "no_broker_order": True,
        "no_live_order": True,
        "no_redis_delete": True,
        "no_lock_delete": True,
        "no_xtrim": True,
        "no_flush": True,
    },
}
Path(proof).write_text(json.dumps(data, indent=2, sort_keys=True))
Path(report).write_text("\n".join(md) + "\n")

print(json.dumps({
    "classification": classification,
    "blockers": blockers,
    "checks": checks,
    "findings": data["findings"],
    "report": report,
    "proof": proof,
    "csv": csv_path,
    "board_md": board_md,
}, indent=2))
PY

echo
echo "=== R10K REPORT ==="
cat "$REPORT"

echo
echo "=== OUTPUT FILES ==="
echo "OUT=$OUT"
echo "PROOF=$PROOF"
echo "REPORT=$REPORT"
echo "CSV=$CSV"
echo "BOARD_MD=$BOARD_MD"
echo "SRC_AUDIT=$SRC_AUDIT"
