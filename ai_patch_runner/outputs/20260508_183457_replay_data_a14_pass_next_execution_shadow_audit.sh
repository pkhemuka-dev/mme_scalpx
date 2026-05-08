export SCALPX_OBSERVE_ONLY=1
unset SCALPX_PAPER_ENABLED SCALPX_LIVE_ENABLED SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME SCALPX_REAL_LIVE_ALLOWED SCALPX_ALLOW_REAL_LIVE PAPER LIVE
.venv/bin/python - <<'PY'
import os, json, csv, hashlib, datetime, pathlib, sys

# Proof path provided
proof_path = "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/proof_replay_data_a13_risk_outputs_shadow_20260508T182326Z.json"

def load_json(p):
    with open(p, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_value_containing(obj, needle):
    if isinstance(obj, dict):
        for k,v in obj.items():
            if isinstance(v, (dict,list)):
                r = find_value_containing(v, needle)
                if r: return r
            else:
                try:
                    if isinstance(v, str) and needle in v:
                        return v
                except:
                    pass
    elif isinstance(obj, list):
        for it in obj:
            r = find_value_containing(it, needle)
            if r: return r
    return None

def safe_join(base, path):
    p = pathlib.Path(path)
    if p.is_absolute():
        return str(p)
    return str((pathlib.Path(base) / path).resolve())

# Load proof
if not os.path.exists(proof_path):
    print("proof_missing", proof_path)
    sys.exit(1)
proof = load_json(proof_path)

# Extract canonical_root and source_date robustly
canonical_root = proof.get("canonical_root") or find_value_containing(proof, "offline_materialization") or None
source_date = proof.get("source_date") or find_value_containing(proof, "2026-04-17") or None

# Try summary candidate path locations
candidate_path = None
if "summary" in proof and isinstance(proof["summary"], dict):
    candidate_path = proof["summary"].get("candidate_path") or find_value_containing(proof["summary"], "risk_outputs_candidate.csv")
if not candidate_path:
    candidate_path = find_value_containing(proof, "risk_outputs_candidate.csv")

# Normalize candidate path
if candidate_path:
    if not os.path.isabs(candidate_path):
        # resolve relative to project root (assume run/proofs is under project root)
        proj_root = str(pathlib.Path(proof_path).parents[1])  # go two up: run/proofs -> project root
        risk_csv = os.path.normpath(os.path.join(proj_root, candidate_path))
    else:
        risk_csv = candidate_path
else:
    risk_csv = None

# Fallback canonical root: try locating from candidate path
if not canonical_root and risk_csv:
    # find the path up to session_exports... pattern
    p = pathlib.Path(risk_csv)
    parts = p.parts
    try:
        idx = parts.index("run")
        canonical_root = os.path.join(*parts[idx: idx+6])  # best-effort
    except Exception:
        canonical_root = str(p.parent.parent)

# Validate essential pieces
if not canonical_root or not source_date or not risk_csv:
    out = {
        "batch":"REPLAY-DATA-A14",
        "title":"execution shadow reconstruction audit",
        "summary": {
            "engine_ready": False,
            "execution_shadow_candidate_written": False,
            "reason": "missing canonical_root/source_date/risk_csv in proof",
            "proof_path": proof_path
        },
        "canonical_root": canonical_root,
        "source_date": source_date,
    }
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_path = os.path.join("run","proofs",f"proof_replay_data_a14_execution_shadow_failed_{ts}.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print("execution_shadow_candidate_written False; reason missing metadata")
    sys.exit(0)

# Read risk_outputs CSV sample and headers
if not os.path.exists(risk_csv):
    print("risk_csv_missing", risk_csv)
    sys.exit(1)

with open(risk_csv, 'r', encoding='utf-8', errors='replace') as f:
    reader = csv.DictReader(f)
    risk_headers = reader.fieldnames or []
    sample_rows = []
    row_count = 0
    for i,row in enumerate(reader):
        if i < 3:
            sample_rows.append(row)
        row_count += 1

# Build execution_shadow_candidate rows conservatively
out_dir = os.path.join(canonical_root, source_date)
os.makedirs(out_dir, exist_ok=True)
exec_candidate_path = os.path.join(out_dir, "execution_shadow_candidate.csv")

# Define conservative header mapping
exec_headers = ["order_ts","order_id","ts_event","symbol","side","qty","price","status","sent","reason","source_index"]

def pick(row, keys):
    for k in keys:
        if k in row and row[k] not in (None, ""):
            return row[k]
    return ""

# Rewind to iterate again
with open(risk_csv, 'r', encoding='utf-8', errors='replace') as f:
    reader = csv.DictReader(f)
    with open(exec_candidate_path, 'w', newline='', encoding='utf-8') as outf:
        writer = csv.DictWriter(outf, fieldnames=exec_headers)
        writer.writeheader()
        for idx, r in enumerate(reader):
            ts_event = pick(r, ["ts_event","timestamp","time","ts"])
            symbol = pick(r, ["symbol","instrument","instrument_token","underlying"])
            side = pick(r, ["side","decision","direction"])
            # Conservative: do not create real orders; qty=0, status=not_sent, sent=false
            order_id = ""
            row = {
                "order_ts": ts_event or "",
                "order_id": order_id,
                "ts_event": ts_event or "",
                "symbol": symbol,
                "side": side or "NA",
                "qty": "0",
                "price": "",
                "status": "not_sent",
                "sent": "false",
                "reason": pick(r, ["risk_reason","reason","risk_decision","note"]) or "conservative_no_order_from_risk_outputs",
                "source_index": str(idx)
            }
            writer.writerow(row)

# Compute sha256
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

exec_sha = sha256_file(exec_candidate_path)
exec_row_count = 0
with open(exec_candidate_path, 'r', encoding='utf-8', errors='replace') as f:
    exec_row_count = sum(1 for _ in f) - 1  # minus header

# Write proof JSON
ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
proof_out = {
    "batch": "REPLAY-DATA-A14",
    "title": "execution shadow reconstruction audit",
    "summary": {
        "candidate_path": os.path.normpath(exec_candidate_path),
        "candidate_sha256": exec_sha,
        "engine_execution_performed": False,
        "engine_ready": False,
        "execution_shadow_candidate_written": True,
        "row_count": exec_row_count,
        "source_risk_row_count": row_count,
        "notes": [
            "Execution shadow created conservatively: no orders, qty=0, status=not_sent, sent=false.",
            "No broker calls or engine execution performed."
        ]
    },
    "canonical_root": canonical_root,
    "source_date": source_date,
    "safety": {
        "SCALPX_OBSERVE_ONLY": os.environ.get("SCALPX_OBSERVE_ONLY"),
        "app_main_runtime_started": False,
        "engine_execution_performed": False,
        "orders_sent": False
    }
}
proof_out_path = os.path.join("run","proofs", f"proof_replay_data_a14_execution_shadow_{ts}.json")
os.makedirs(os.path.dirname(proof_out_path), exist_ok=True)
with open(proof_out_path, 'w', encoding='utf-8') as f:
    json.dump(proof_out, f, indent=2)

# Write milestone doc
md_out = []
md_out.append(f"# REPLAY-DATA-A14 — execution shadow reconstruction audit")
md_out.append("")
md_out.append(f"- timestamp: {ts}")
md_out.append(f"- canonical_root: {canonical_root}")
md_out.append(f"- source_date: {source_date}")
md_out.append(f"- risk_outputs_candidate_source: {risk_csv}")
md_out.append(f"- execution_shadow_candidate: {os.path.normpath(exec_candidate_path)}")
md_out.append(f"- execution_shadow_rows: {exec_row_count}")
md_out.append(f"- execution_shadow_sha256: {exec_sha}")
md_out.append("")
md_out.append("Summary:")
md_out.append("")
md_out.append("- execution_shadow_candidate_written: true")
md_out.append(f"- row_count: {exec_row_count}")
md_out.append("- engine_ready: false")
md_out.append("- next_batch: REPLAY-DATA-A15 (not generated here) — follow-up to validate engine readiness if desired")
md_out.append("")
md_out.append("Safety notes:")
md_out.append("")
md_out.append("- All rows are conservative placeholders (no orders generated).")
md_out.append("- No broker calls, no service starts, no engine run performed.")
md_out.append("")
md_text = "\n".join(md_out)
md_path = os.path.join("docs","milestones", f"replay_data_a14_execution_shadow_{ts}.md")
os.makedirs(os.path.dirname(md_path), exist_ok=True)
with open(md_path, "w", encoding='utf-8') as f:
    f.write(md_text)

# Final stdout summary required
final_summary = {
    "execution_shadow_candidate_written": True,
    "row_count": exec_row_count,
    "engine_ready": False,
    "next_batch": "REPLAY-DATA-A15"
}
print(json.dumps(final_summary))

PY
