export SCALPX_OBSERVE_ONLY=1
unset SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME || true
unset SCALPX_REAL_LIVE_ALLOWED || true
unset SCALPX_ALLOW_REAL_LIVE || true
unset SCALPX_PAPER || true
unset SCALPX_LIVE || true

cat > /tmp/replay_a14_runner.py <<'PY'
#!/usr/bin/env python3
import os, sys, csv, json, hashlib, datetime, pathlib, io, re

# Inputs (fixed by package)
proof_path = "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/proof_replay_data_a13_risk_outputs_shadow_20260508T182326Z.json"

def safe_read_json(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def sha256_of_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

# Load proof
proof = safe_read_json(proof_path)

# Resolve canonical_root and source_date (try several locations)
canonical_root = proof.get("canonical_root") or proof.get("summary",{}).get("canonical_root")
source_date = proof.get("source_date") or proof.get("summary",{}).get("source_date")
candidate_risk_path = None
# prefer explicit path reported in summary
candidate_risk_path = proof.get("summary",{}).get("candidate_path") or proof.get("summary",{}).get("risk_outputs_candidate_path")
if not candidate_risk_path:
    # fallback: search proof for any string that endswith risk_outputs_candidate.csv
    s = json.dumps(proof)
    m = re.search(r'([^\s"\'\\]+\brisk_outputs_candidate\.csv\b)', s)
    if m:
        candidate_risk_path = m.group(1)

if not canonical_root or not source_date or not candidate_risk_path:
    print(json.dumps({"error":"missing_required_fields","canonical_root":canonical_root,"source_date":source_date,"candidate_risk_path":candidate_risk_path}))
    sys.exit(2)

# Normalize paths
project_root = os.getcwd()
risk_csv_path = candidate_risk_path
if not os.path.isabs(risk_csv_path):
    risk_csv_path = os.path.join(project_root, risk_csv_path)

if not os.path.exists(risk_csv_path):
    print(json.dumps({"error":"risk_candidate_missing","path":risk_csv_path}))
    sys.exit(3)

# Read risk_outputs_candidate schema and sample rows
with open(risk_csv_path, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    risk_headers = reader.fieldnames or []
    sample = []
    row_count = 0
    for r in reader:
        row_count += 1
        if len(sample) < 5:
            sample.append(r)
# reopen to compute exact row_count if csv module didn't iterate fully
if row_count == 0:
    # maybe empty file or header-only - count lines
    with open(risk_csv_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if len(lines) <= 1:
            row_count = 0
        else:
            row_count = max(0, len(lines)-1)

# Attempt to infer decision id column in risk outputs
decision_key = None
for key in ("decision_id","strategy_decision_id","decision","id","signal_id","strategy_id"):
    if key in (risk_headers or []):
        decision_key = key
        break
# fallback to index-based ID
if not decision_key:
    decision_key = "__row_index__"

# Try to detect expected execution shadow schema by scanning replay contracts/reports and services/execution.py
search_paths = [
    "app/mme_scalpx/replay/contracts.py",
    "app/mme_scalpx/replay/reports.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/services/execution.py"
]
detected_cols = None
for sp in search_paths:
    p = os.path.join(project_root, sp)
    if not os.path.exists(p):
        continue
    try:
        txt = open(p, 'r', encoding='utf-8').read()
    except Exception:
        continue
    # look for a declaration of execution_shadow field names as a list or tuple
    m = re.search(r'(execution_shadow|execution_shadow_row|execution_row).*?=\s*(\[[^\]]+\]|\([^\)]+\))', txt, re.S | re.I)
    if m:
        lit = m.group(2)
        # crude eval-safe parse: extract quoted words
        cols = re.findall(r"['\"]([A-Za-z0-9_]+)['\"]", lit)
        if cols:
            detected_cols = cols
            break
    # look for csv header string
    m2 = re.search(r'["\'](ts_event,.*execution.*)["\']', txt)
    if m2:
        cols = [c.strip() for c in m2.group(1).split(",")]
        if cols:
            detected_cols = cols
            break
# If nothing detected, use conservative default schema
if detected_cols:
    exec_cols = detected_cols
else:
    exec_cols = [
        "ts_event",
        "symbol",
        "decision_id",
        "order_sent",
        "order_id",
        "qty",
        "price",
        "status",
        "reason",
        "engine_reason"
    ]

# Conservative population policy: always no order / not_sent / qty=0 unless clear mapping exists
# Build output directory and filename under canonical_root/source_date/
out_dir = os.path.join(project_root, canonical_root, source_date)
os.makedirs(out_dir, exist_ok=True)
out_csv_name = "execution_shadow_candidate.csv"
out_csv_path = os.path.join(out_dir, out_csv_name)

# Write CSV
with open(out_csv_path, "w", newline='', encoding='utf-8') as outf:
    writer = csv.DictWriter(outf, fieldnames=exec_cols, extrasaction='ignore')
    writer.writeheader()
    # iterate over risk rows again for consistent mapping
    with open(risk_csv_path, newline='', encoding='utf-8') as f:
        rdr = csv.DictReader(f)
        idx = 0
        for r in rdr:
            idx += 1
            row = {c:"" for c in exec_cols}
            # populate conservative fields
            # ts_event: try to take from risk row if exists
            for ts_key in ("ts_event","ts","timestamp","time"):
                if ts_key in r and r.get(ts_key):
                    row["ts_event"] = r.get(ts_key)
                    break
            # symbol
            for s_key in ("symbol","instrument","instrument_token","underlying"):
                if s_key in r and r.get(s_key):
                    row["symbol"] = r.get(s_key)
                    break
            # decision_id
            if decision_key == "__row_index__":
                row["decision_id"] = str(idx)
            else:
                row["decision_id"] = r.get(decision_key,"")
            # conservative order fields
            row["order_sent"] = "false"
            row["order_id"] = ""
            row["qty"] = "0"
            row["price"] = ""
            # status and reason - prefer 'risk_blocked' if risk field indicates block
            reason = "no_order_conservative"
            # inspect typical risk flags
            for allow_field in ("allow","allowed","risk_allow","can_trade","pass"):
                if allow_field in r:
                    v = r.get(allow_field,"").strip().lower()
                    if v in ("false","0","no","n","blocked","deny","denied"):
                        reason = "risk_blocked"
                    elif v in ("true","1","yes","y","allow","allowed","pass"):
                        reason = "no_order_conservative"
                    break
            # also look for explicit risk decision fields
            for rf in ("risk_decision","risk_result","risk_status"):
                if rf in r and r.get(rf):
                    if re.search(r'block|deny|rejected', r.get(rf,""), re.I):
                        reason = "risk_blocked"
            row["status"] = "not_sent"
            row["reason"] = reason
            row["engine_reason"] = "execution_shadow_conservative"
            writer.writerow(row)

# compute sha256 and row_count of the created file
created_sha256 = sha256_of_file(out_csv_path)
created_row_count = 0
with open(out_csv_path, newline='', encoding='utf-8') as f:
    dr = csv.reader(f)
    # subtract header
    created_row_count = sum(1 for _ in dr) - 1

# Write proof JSON and milestone markdown
ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
proof_out_name = f"proof_replay_data_a14_execution_shadow_{ts}.json"
proof_out_path = os.path.join("run","proofs", proof_out_name)
md_out_name = f"replay_data_a14_execution_shadow_{ts}.md"
md_out_path = os.path.join("docs","milestones", md_out_name)

proof_obj = {
    "batch": "REPLAY-DATA-A14",
    "title": "execution_shadow reconstruction audit",
    "summary": {
        "execution_shadow_candidate_path": os.path.relpath(out_csv_path, project_root),
        "execution_shadow_candidate_sha256": created_sha256,
        "execution_shadow_candidate_row_count": created_row_count,
        "source_risk_candidate_path": os.path.relpath(risk_csv_path, project_root),
        "source_risk_candidate_row_count": row_count,
        "engine_execution_performed": False,
        "engine_ready": False,
        "next_batch": "REPLAY-DATA-A15 selector-only replay-data surface probe (no full engine)",
        "execution_shadow_candidate_written": True
    },
    "detected_execution_schema": exec_cols,
    "safety": {
        "SCALPX_OBSERVE_ONLY": os.environ.get("SCALPX_OBSERVE_ONLY",""),
        "app_main_runtime_started": False,
        "bin_replay_run_patched": False,
        "broker_calls_executed": False,
        "code_patched": False,
        "engine_execution_performed": False,
        "execution_shadow_created": True,
        "full_replay_engine_run": False,
        "live_redis_writes_executed": False,
        "orders_sent": False,
        "paper_or_live_enabled": False,
        "risk_outputs_candidate_only": True,
        "risk_outputs_created": True,
        "services_started": False,
        "strategy_risk_execution_parity_claimed": False
    },
    "canonical_root": canonical_root,
    "source_date": source_date,
    "created_at_utc": datetime.datetime.utcnow().isoformat() + "Z"
}

os.makedirs(os.path.dirname(proof_out_path), exist_ok=True)
with open(proof_out_path, "w", encoding="utf-8") as pf:
    json.dump(proof_obj, pf, indent=2)

# Write human-friendly milestone
md_lines = [
    f"# REPLAY-DATA-A14 — execution_shadow reconstruction audit",
    "",
    f"- timestamp (utc): {datetime.datetime.utcnow().isoformat()}Z",
    f"- canonical_root: {canonical_root}",
    f"- source_date: {source_date}",
    f"- source_risk_candidate: {os.path.relpath(risk_csv_path, project_root)}",
    f"- execution_shadow_candidate: {os.path.relpath(out_csv_path, project_root)}",
    f"- execution_shadow_candidate_sha256: {created_sha256}",
    f"- execution_shadow_candidate_row_count: {created_row_count}",
    f"- engine_ready: false",
    f"- next_batch: REPLAY-DATA-A15 selector-only replay-data surface probe (no full engine)",
    "",
    "Summary verdict:",
    "",
    "- execution_shadow_candidate_written: true",
    f"- row_count: {created_row_count}",
    "- engine_ready=false",
    "- next_batch=REPLAY-DATA-A15 selector-only replay-data surface probe (no full engine)",
    ""
]
os.makedirs(os.path.dirname(md_out_path), exist_ok=True)
with open(md_out_path, "w", encoding="utf-8") as mf:
    mf.write("\n".join(md_lines))

# Final stdout summary (compact, machine-friendly)
final = {
    "execution_shadow_candidate_written": True,
    "path": os.path.relpath(out_csv_path, project_root),
    "row_count": created_row_count,
    "engine_ready": False,
    "next_batch": "REPLAY-DATA-A15"
}
print(json.dumps(final))
PY

# Run the Python runner with the project venv python
.venv/bin/python /tmp/replay_a14_runner.py >/tmp/replay_a14_runner.out 2>&1 || (cat /tmp/replay_a14_runner.out && exit 1)
# show summary to console
cat /tmp/replay_a14_runner.out || true
