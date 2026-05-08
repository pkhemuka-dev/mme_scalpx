set -euo pipefail
cd /home/Lenovo/scalpx/projects/mme_scalpx

export SCALPX_OBSERVE_ONLY=1
unset SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME || true
unset SCALPX_REAL_LIVE_ALLOWED || true
unset SCALPX_ALLOW_REAL_LIVE || true
unset SCALPX_PAPER_TRADING || true
unset SCALPX_LIVE_TRADING || true
unset SCALPX_ENABLE_PAPER || true
unset SCALPX_ENABLE_LIVE || true
unset SCALPX_PAPER_MODE || true
unset SCALPX_LIVE_MODE || true
unset MME_PAPER_ENABLED || true
unset MME_LIVE_ENABLED || true
unset PAPER_TRADING || true
unset LIVE_TRADING || true

test -x .venv/bin/python

cat > /tmp/mme_replay_data_a14_execution_shadow.py <<'PY'
import csv
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path.cwd().resolve()
LATEST_PROOF = Path("/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/proof_replay_data_a13_risk_outputs_shadow_20260508T182326Z.json").resolve()
BATCH = "REPLAY-DATA-A14"
TITLE = "execution shadow reconstruction audit"
NEXT_BATCH = "REPLAY-DATA-A15 selector-only replay-data surface probe (no full engine)"

def utc_stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def iso_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def rel(p):
    p = Path(p).resolve()
    try:
        return str(p.relative_to(PROJECT))
    except Exception:
        return str(p)

def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write("\n")

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def safe_under(path, root):
    path = Path(path).resolve()
    root = Path(root).resolve()
    try:
        path.relative_to(root)
        return True
    except Exception:
        return False

def read_text_limited(path, limit=250000):
    p = PROJECT / path
    if not p.exists() or not p.is_file():
        return None
    return p.read_text(encoding="utf-8", errors="replace")[:limit]

def snippets_for(text, tokens, max_lines=30):
    if not text:
        return []
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        low = line.lower()
        if any(t in low for t in tokens):
            s = line.strip()
            if len(s) > 220:
                s = s[:217] + "..."
            out.append({"line": i, "text": s})
        if len(out) >= max_lines:
            break
    return out

def sanitize_col(name):
    name = str(name or "").strip()
    name = re.sub(r"[^A-Za-z0-9_]+", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name or "blank"

def first_value(row, names):
    for n in names:
        if n in row and row.get(n) not in (None, ""):
            return row.get(n, "")
    return ""

def add_unique(cols, name):
    if name not in cols:
        cols.append(name)

started_at = iso_now()
stamp = utc_stamp()

proof_in = read_json(LATEST_PROOF)
summary_in = proof_in.get("summary", {}) if isinstance(proof_in, dict) else {}

canonical_root = proof_in.get("canonical_root")
source_date = proof_in.get("source_date")
risk_candidate_path = summary_in.get("candidate_path") or proof_in.get("risk_outputs_candidate_path")

findings = []
errors = []

if proof_in.get("batch") != "REPLAY-DATA-A13":
    errors.append({"severity": "ERROR", "area": "input_proof", "message": "latest proof is not REPLAY-DATA-A13"})
if not canonical_root:
    errors.append({"severity": "ERROR", "area": "input_proof", "message": "canonical_root missing"})
if not source_date:
    errors.append({"severity": "ERROR", "area": "input_proof", "message": "source_date missing"})
if not risk_candidate_path:
    errors.append({"severity": "ERROR", "area": "input_proof", "message": "risk_outputs_candidate.csv path missing"})

offline_root = (PROJECT / "run/replay/parity/offline_materialization").resolve()
canonical_abs = (PROJECT / canonical_root).resolve() if canonical_root else None
risk_abs = (PROJECT / risk_candidate_path).resolve() if risk_candidate_path else None

if canonical_abs and not safe_under(canonical_abs, offline_root):
    errors.append({"severity": "ERROR", "area": "path_safety", "message": "canonical_root is outside offline materialization root"})
if canonical_abs and not canonical_abs.exists():
    errors.append({"severity": "ERROR", "area": "path_safety", "message": "canonical_root does not exist"})
if risk_abs and canonical_abs and not safe_under(risk_abs, canonical_abs):
    errors.append({"severity": "ERROR", "area": "path_safety", "message": "risk candidate is outside canonical_root"})
if risk_abs and not risk_abs.exists():
    errors.append({"severity": "ERROR", "area": "input_data", "message": "risk_outputs_candidate.csv not found"})

execution_expectation_tokens = [
    "execution_shadow",
    "execution",
    "order_sent",
    "not_sent",
    "broker_order",
    "filled_qty",
    "qty",
    "quantity",
    "status",
    "order_id",
    "no_order",
]
expectation_sources = []
for src in [
    "app/mme_scalpx/replay/dataset.py",
    "app/mme_scalpx/replay/contracts.py",
    "app/mme_scalpx/replay/reports.py",
    "app/mme_scalpx/services/execution.py",
]:
    txt = read_text_limited(src)
    expectation_sources.append({
        "path": src,
        "exists": txt is not None,
        "sha256": hashlib.sha256(txt.encode("utf-8", errors="replace")).hexdigest() if txt is not None else None,
        "snippets": snippets_for(txt, execution_expectation_tokens),
    })

risk_header = []
risk_sample_rows = []
risk_row_count_observed = 0
risk_sha256 = sha256_file(risk_abs) if risk_abs and risk_abs.exists() else None

if not errors:
    with open(risk_abs, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        risk_header = list(reader.fieldnames or [])
        for row in reader:
            risk_row_count_observed += 1
            if len(risk_sample_rows) < 5:
                risk_sample_rows.append({k: row.get(k, "") for k in risk_header[:40]})
    if not risk_header:
        errors.append({"severity": "ERROR", "area": "risk_schema", "message": "risk_outputs_candidate.csv has no header"})
    if risk_row_count_observed <= 0:
        errors.append({"severity": "ERROR", "area": "risk_schema", "message": "risk_outputs_candidate.csv has no rows"})

timestamp_candidates = ["ts_event", "timestamp", "ts", "event_time", "created_at", "decision_ts", "source_ts_event"]
symbol_candidates = ["symbol", "tradingsymbol", "instrument", "instrument_symbol", "underlying", "source_symbol"]
token_candidates = ["instrument_token", "token", "instrument_id", "source_instrument_token"]
side_candidates = ["side", "order_side", "signal_side", "source_side"]
allow_candidates = ["allow", "risk_allow", "allowed", "approved", "is_allowed", "source_risk_allow"]
action_candidates = ["risk_action", "action", "order_action", "decision", "strategy_action", "source_risk_action"]
reason_candidates = ["risk_reason", "reason", "block_reason", "reject_reason", "source_risk_reason"]

has_ts = any(c in risk_header for c in timestamp_candidates)
has_symbol_or_token = any(c in risk_header for c in symbol_candidates + token_candidates)
schema_safe = bool(not errors and has_ts and has_symbol_or_token)

if not has_ts:
    findings.append({"severity": "WARN", "area": "risk_schema", "message": "No timestamp-like column found; execution shadow candidate not written."})
if not has_symbol_or_token:
    findings.append({"severity": "WARN", "area": "risk_schema", "message": "No symbol/token-like column found; execution shadow candidate not written."})

candidate_written = False
candidate_abs = None
candidate_sha = None
row_count = 0
candidate_header = []

if schema_safe:
    date_dir = (canonical_abs / source_date).resolve()
    if not safe_under(date_dir, canonical_abs):
        errors.append({"severity": "ERROR", "area": "path_safety", "message": "date_dir is outside canonical_root"})
    else:
        date_dir.mkdir(parents=True, exist_ok=True)
        candidate_abs = (date_dir / "execution_shadow_candidate.csv").resolve()
        if not safe_under(candidate_abs, canonical_abs):
            errors.append({"severity": "ERROR", "area": "path_safety", "message": "candidate path is outside canonical_root"})
        elif not safe_under(candidate_abs, offline_root):
            errors.append({"severity": "ERROR", "area": "path_safety", "message": "candidate path is outside offline materialization root"})

if schema_safe and not errors and candidate_abs:
    base_cols = [
        "ts_event",
        "timestamp",
        "symbol",
        "instrument_token",
        "side",
        "qty",
        "quantity",
        "filled_qty",
        "price",
        "order_sent",
        "broker_order_sent",
        "execution_action",
        "status",
        "execution_status",
        "order_id",
        "broker_order_id",
        "reason",
        "source_risk_allow",
        "source_risk_action",
        "source_risk_reason",
        "source_risk_row_index",
    ]
    candidate_header = []
    for c in base_cols:
        add_unique(candidate_header, c)

    source_col_map = []
    used_source_names = set(candidate_header)
    for c in risk_header:
        sc = "source_risk_" + sanitize_col(c)
        if sc in used_source_names:
            continue
        used_source_names.add(sc)
        source_col_map.append((c, sc))
        add_unique(candidate_header, sc)

    with open(risk_abs, "r", encoding="utf-8", newline="") as src, open(candidate_abs, "w", encoding="utf-8", newline="") as dst:
        reader = csv.DictReader(src)
        writer = csv.DictWriter(dst, fieldnames=candidate_header, extrasaction="ignore")
        writer.writeheader()
        for idx, row in enumerate(reader):
            ts = first_value(row, timestamp_candidates)
            sym = first_value(row, symbol_candidates)
            tok = first_value(row, token_candidates)
            side = first_value(row, side_candidates)
            risk_allow = first_value(row, allow_candidates)
            risk_action = first_value(row, action_candidates)
            risk_reason = first_value(row, reason_candidates)
            reason = "conservative_execution_shadow_no_order_not_sent_qty_0"
            if risk_reason:
                reason = reason + "__risk_reason=" + str(risk_reason)[:180]
            out = {
                "ts_event": ts,
                "timestamp": ts,
                "symbol": sym,
                "instrument_token": tok,
                "side": side,
                "qty": "0",
                "quantity": "0",
                "filled_qty": "0",
                "price": "",
                "order_sent": "false",
                "broker_order_sent": "false",
                "execution_action": "no_order",
                "status": "not_sent",
                "execution_status": "not_sent",
                "order_id": "",
                "broker_order_id": "",
                "reason": reason,
                "source_risk_allow": risk_allow,
                "source_risk_action": risk_action,
                "source_risk_reason": risk_reason,
                "source_risk_row_index": str(idx),
            }
            for src_col, dst_col in source_col_map:
                out[dst_col] = row.get(src_col, "")
            writer.writerow(out)
            row_count += 1

    candidate_sha = sha256_file(candidate_abs)
    candidate_written = True
    findings.append({
        "severity": "INFO",
        "area": "execution_shadow",
        "message": "A14 wrote conservative no_order/not_sent/qty=0 execution_shadow_candidate rows from risk_outputs_candidate when schema-safe."
    })
else:
    findings.append({
        "severity": "WARN",
        "area": "execution_shadow",
        "message": "execution_shadow_candidate.csv was not written because schema safety checks did not pass."
    })

findings.append({
    "severity": "INFO",
    "area": "engine_readiness",
    "message": "Replay engine execution remains intentionally disabled; no execution parity is claimed."
})

proof = {
    "batch": BATCH,
    "title": TITLE,
    "created_at_utc": started_at,
    "verdict": "PASS_NEXT_SELECTOR_ONLY_SURFACE_PROBE" if candidate_written else "NEEDS_REVIEW_EXECUTION_SHADOW_NOT_WRITTEN",
    "canonical_root": canonical_root,
    "source_date": source_date,
    "dataset_id": proof_in.get("dataset_id"),
    "input_proof": rel(LATEST_PROOF),
    "input_risk_outputs_candidate": rel(risk_abs) if risk_abs else None,
    "risk_outputs_candidate_sha256": risk_sha256,
    "risk_schema": {
        "columns": risk_header,
        "sample_rows": risk_sample_rows,
        "row_count_observed": risk_row_count_observed,
        "has_timestamp_column": has_ts,
        "has_symbol_or_token_column": has_symbol_or_token,
        "schema_safe_for_conservative_execution_shadow": schema_safe,
    },
    "execution_expectation_inspection": {
        "read_only_sources": expectation_sources,
        "candidate_policy": "conservative no_order/not_sent/qty=0 rows unless proven otherwise",
    },
    "summary": {
        "candidate_path": rel(candidate_abs) if candidate_abs and candidate_written else None,
        "candidate_sha256": candidate_sha,
        "execution_shadow_candidate_written": candidate_written,
        "row_count": row_count,
        "source_risk_row_count": risk_row_count_observed,
        "engine_execution_performed": False,
        "engine_ready": False,
        "next_batch": NEXT_BATCH,
    },
    "selector_probe": {},
    "findings": findings + errors,
    "safety": {
        "SCALPX_OBSERVE_ONLY": os.environ.get("SCALPX_OBSERVE_ONLY"),
        "app_main_runtime_started": False,
        "bin_replay_run_patched": False,
        "broker_calls_executed": False,
        "code_patched": False,
        "engine_execution_performed": False,
        "execution_shadow_candidate_only": True,
        "execution_shadow_candidate_written": candidate_written,
        "full_replay_engine_run": False,
        "live_redis_writes_executed": False,
        "orders_sent": False,
        "paper_or_live_enabled": False,
        "services_started": False,
        "strategy_risk_execution_parity_claimed": False,
    },
}

proof_path = PROJECT / "run/proofs" / f"proof_replay_data_a14_execution_shadow_{stamp}.json"
write_json(proof_path, proof)

milestone_path = PROJECT / "docs/milestones" / f"replay_data_a14_execution_shadow_{stamp}.md"
milestone_path.parent.mkdir(parents=True, exist_ok=True)
milestone = f"""# {BATCH} — {TITLE}

- Input proof: `{rel(LATEST_PROOF)}`
- Canonical root: `{canonical_root}`
- Source date: `{source_date}`
- Risk input: `{rel(risk_abs) if risk_abs else None}`
- Execution candidate: `{rel(candidate_abs) if candidate_abs and candidate_written else None}`
- Risk rows observed: `{risk_row_count_observed}`
- Execution rows written: `{row_count}`
- Engine execution performed: `false`
- Engine ready: `false`

## Audit result

A14 inspected the risk output candidate schema and read-only execution expectations from replay contracts/reports and `app/mme_scalpx/services/execution.py`.

The candidate, when written, is sandbox-only and conservative:
- `execution_action=no_order`
- `status=not_sent`
- `execution_status=not_sent`
- `qty=0`
- `quantity=0`
- `filled_qty=0`
- `order_sent=false`
- no order IDs

No broker calls, order placement, service runtime, live/paper enablement, Redis mutation, production code patching, or full replay engine execution was performed.

## Final summary

execution_shadow_candidate_written={str(candidate_written).lower()}
row_count={row_count}
engine_ready=false
next_batch={NEXT_BATCH}
"""
milestone_path.write_text(milestone, encoding="utf-8")

print(json.dumps({
    "batch": BATCH,
    "proof": rel(proof_path),
    "milestone": rel(milestone_path),
    "execution_shadow_candidate_written": candidate_written,
    "row_count": row_count,
    "engine_ready": False,
    "next_batch": NEXT_BATCH,
}, indent=2, sort_keys=True))
PY

.venv/bin/python /tmp/mme_replay_data_a14_execution_shadow.py
