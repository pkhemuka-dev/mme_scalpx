set -euo pipefail; export SCALPX_OBSERVE_ONLY=1; unset SCALPX_LIVE SCALPX_PAPER SCALPX_ENABLE_LIVE SCALPX_ENABLE_PAPER PAPER_TRADING LIVE_TRADING BROKER_LOGIN BROKER_API_KEY BROKER_API_SECRET REDIS_URL; mkdir -p /tmp run/proofs run/audits docs/milestones; cat > /tmp/replay_data_a13_risk_outputs_shadow.py <<'PY'
import csv, json, os, re, hashlib
from pathlib import Path
from datetime import datetime, timezone

BATCH = "REPLAY-DATA-A13"
TITLE = "risk_outputs shadow reconstruction audit"
LATEST_PROOF = Path("/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/proof_replay_data_a12_strategy_decisions_shadow_20260508T181220Z.json")
PROJECT_ROOT = Path.cwd().resolve()
RUN_PROOFS = PROJECT_ROOT / "run" / "proofs"
RUN_AUDITS = PROJECT_ROOT / "run" / "audits"
DOCS = PROJECT_ROOT / "docs" / "milestones"
NOW = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def rel(p: Path) -> str:
    try:
        return str(p.resolve().relative_to(PROJECT_ROOT))
    except Exception:
        return str(p)

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def is_under(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except Exception:
        return False

def safe_read_text(path: Path, limit=300000):
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")[:limit]

def inspect_text_expectations():
    targets = []
    for p in [
        PROJECT_ROOT / "app" / "mme_scalpx" / "replay" / "contracts.py",
        PROJECT_ROOT / "app" / "mme_scalpx" / "replay" / "reports.py",
        PROJECT_ROOT / "app" / "mme_scalpx" / "replay" / "dataset.py",
        PROJECT_ROOT / "app" / "mme_scalpx" / "services" / "risk.py",
        PROJECT_ROOT / "services" / "risk.py",
    ]:
        if p.exists():
            txt = safe_read_text(p)
            lines = txt.splitlines()
            hits = []
            for i, line in enumerate(lines):
                if re.search(r"risk_outputs|risk output|risk_result|risk_allowed|risk_status|risk|allow|approved|blocked|no_order", line, re.I):
                    lo, hi = max(0, i - 2), min(len(lines), i + 3)
                    hits.append({"line": i + 1, "context": "\n".join(lines[lo:hi])[:1600]})
                    if len(hits) >= 20:
                        break
            keys = sorted(set(re.findall(r"""["']([A-Za-z_][A-Za-z0-9_]{1,60})["']\s*:""", txt)))
            risk_keys = [k for k in keys if re.search(r"risk|allow|approved|block|reason|order|qty|decision|signal|side|symbol|ts|time|price", k, re.I)]
            targets.append({"path": rel(p), "exists": True, "risk_related_context_count": len(hits), "risk_related_context": hits[:8], "dict_key_hints": risk_keys[:80]})
        else:
            targets.append({"path": rel(p), "exists": False})
    return targets

def read_csv_schema_sample(path: Path, n=5):
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for _, row in zip(range(n), reader):
            rows.append(row)
        return {"fieldnames": reader.fieldnames or [], "sample_rows": rows}

def count_csv_rows(path: Path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return max(0, sum(1 for _ in f) - 1)

def first_present(row, names, default=""):
    for name in names:
        if name in row and row.get(name) not in (None, ""):
            return row.get(name, "")
    return default

def bool_false_string():
    return "false"

RUN_PROOFS.mkdir(parents=True, exist_ok=True)
RUN_AUDITS.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

findings = []
errors = []
risk_outputs_candidate_written = False
risk_candidate_path = None
risk_candidate_sha = None
row_count = 0
source_strategy_row_count = 0

proof_in = read_json(LATEST_PROOF)
canonical_root_raw = proof_in.get("canonical_root") or proof_in.get("summary", {}).get("canonical_root")
source_date = proof_in.get("source_date") or proof_in.get("summary", {}).get("source_date")
strategy_candidate_raw = proof_in.get("summary", {}).get("candidate_path") or proof_in.get("strategy_decisions_candidate_path")

if not canonical_root_raw:
    errors.append("missing canonical_root in A12 proof")
if not source_date:
    errors.append("missing source_date in A12 proof")
if not strategy_candidate_raw:
    errors.append("missing strategy_decisions_candidate.csv path in A12 proof")

canonical_root = (PROJECT_ROOT / canonical_root_raw).resolve() if canonical_root_raw and not Path(canonical_root_raw).is_absolute() else Path(canonical_root_raw).resolve() if canonical_root_raw else None
strategy_candidate = (PROJECT_ROOT / strategy_candidate_raw).resolve() if strategy_candidate_raw and not Path(strategy_candidate_raw).is_absolute() else Path(strategy_candidate_raw).resolve() if strategy_candidate_raw else None
date_root = (canonical_root / source_date).resolve() if canonical_root and source_date else None

strategy_schema = {}
strategy_sha = None
expectations = inspect_text_expectations()

if canonical_root and not is_under(canonical_root, PROJECT_ROOT / "run" / "replay" / "parity" / "offline_materialization"):
    errors.append(f"canonical_root outside allowed offline_materialization root: {canonical_root}")
if date_root and not is_under(date_root, canonical_root):
    errors.append(f"date root not under canonical root: {date_root}")
if strategy_candidate and date_root and not is_under(strategy_candidate, date_root):
    errors.append(f"strategy_decisions_candidate not under canonical date root: {strategy_candidate}")
if strategy_candidate and strategy_candidate.name != "strategy_decisions_candidate.csv":
    findings.append({"severity": "WARN", "area": "input", "message": f"strategy candidate filename is {strategy_candidate.name}, expected strategy_decisions_candidate.csv"})
if strategy_candidate and not strategy_candidate.exists():
    errors.append(f"strategy_decisions_candidate missing: {strategy_candidate}")

if not errors and strategy_candidate:
    strategy_schema = read_csv_schema_sample(strategy_candidate, 8)
    strategy_sha = sha256_file(strategy_candidate)
    source_strategy_row_count = count_csv_rows(strategy_candidate)
    fields = strategy_schema.get("fieldnames", [])
    minimal_any_ts = any(c in fields for c in ["ts_event", "timestamp", "ts", "time", "event_time"])
    minimal_any_symbol = any(c in fields for c in ["symbol", "tradingsymbol", "instrument", "instrument_symbol"])
    if not minimal_any_ts:
        errors.append("strategy_decisions_candidate schema lacks a recognizable timestamp column")
    if not minimal_any_symbol:
        errors.append("strategy_decisions_candidate schema lacks a recognizable symbol column")
    if source_strategy_row_count <= 0:
        errors.append("strategy_decisions_candidate has no data rows")

if not errors and date_root:
    risk_candidate_path = (date_root / "risk_outputs_candidate.csv").resolve()
    if not is_under(risk_candidate_path, date_root):
        errors.append("risk_outputs_candidate path failed sandbox containment check")
    elif risk_candidate_path.exists() and not risk_candidate_path.is_file():
        errors.append("risk_outputs_candidate path exists but is not a file")

if not errors and strategy_candidate and risk_candidate_path:
    input_fields = strategy_schema.get("fieldnames", [])
    passthrough_cols = [c for c in [
        "ts_event", "timestamp", "ts", "time", "event_time",
        "symbol", "tradingsymbol", "instrument", "instrument_symbol",
        "side", "action", "decision", "signal", "strategy_action", "intent",
        "ltp", "price", "mid", "bid", "ask", "qty", "quantity",
        "provider", "instrument_token", "source_stream"
    ] if c in input_fields]
    out_fields = []
    for c in passthrough_cols:
        if c not in out_fields:
            out_fields.append(c)
    conservative_fields = [
        "risk_allowed",
        "allow",
        "approved",
        "risk_status",
        "risk_decision",
        "risk_reason",
        "order_intent",
        "order_qty",
        "max_qty",
        "risk_rule",
        "source_strategy_row_index",
        "source_strategy_sha256",
        "shadow_reconstruction",
    ]
    for c in conservative_fields:
        if c not in out_fields:
            out_fields.append(c)
    with strategy_candidate.open("r", encoding="utf-8", newline="") as f_in, risk_candidate_path.open("w", encoding="utf-8", newline="") as f_out:
        reader = csv.DictReader(f_in)
        writer = csv.DictWriter(f_out, fieldnames=out_fields, extrasaction="ignore")
        writer.writeheader()
        for idx, row in enumerate(reader):
            out = {}
            for c in passthrough_cols:
                out[c] = row.get(c, "")
            out["risk_allowed"] = bool_false_string()
            out["allow"] = bool_false_string()
            out["approved"] = bool_false_string()
            out["risk_status"] = "risk_blocked"
            out["risk_decision"] = "no_order"
            out["risk_reason"] = "shadow_conservative_no_order_reconstruction"
            out["order_intent"] = "no_order"
            out["order_qty"] = "0"
            out["max_qty"] = "0"
            out["risk_rule"] = "conservative_shadow_default"
            out["source_strategy_row_index"] = str(idx)
            out["source_strategy_sha256"] = strategy_sha or ""
            out["shadow_reconstruction"] = "true"
            writer.writerow(out)
            row_count += 1
    risk_outputs_candidate_written = True
    risk_candidate_sha = sha256_file(risk_candidate_path)
    findings.append({"severity": "INFO", "area": "risk_shadow", "message": "A13 wrote only conservative allow=false/no_order/risk_blocked risk_outputs_candidate rows from strategy_decisions_candidate when schema-safe."})
    findings.append({"severity": "INFO", "area": "engine_readiness", "message": "Replay engine execution remains intentionally disabled; execution_shadow is not created; no strategy/risk/execution parity is claimed."})

proof = {
    "batch": BATCH,
    "title": TITLE,
    "verdict": "PASS_NEXT_EXECUTION_SHADOW_AUDIT" if risk_outputs_candidate_written and not errors else "FAIL_RISK_OUTPUTS_SHADOW_AUDIT",
    "created_at": NOW,
    "canonical_root": rel(canonical_root) if canonical_root else None,
    "source_date": source_date,
    "summary": {
        "risk_outputs_candidate_written": risk_outputs_candidate_written,
        "candidate_path": rel(risk_candidate_path) if risk_candidate_path else None,
        "candidate_sha256": risk_candidate_sha,
        "row_count": row_count,
        "source_strategy_row_count": source_strategy_row_count,
        "engine_ready": False,
        "engine_execution_performed": False,
        "next_batch": "REPLAY-DATA-A14 execution shadow reconstruction audit" if risk_outputs_candidate_written and not errors else "REPLAY-DATA-A13 retry risk_outputs shadow reconstruction audit",
    },
    "input_a12_proof": rel(LATEST_PROOF),
    "strategy_decisions_candidate": {
        "path": rel(strategy_candidate) if strategy_candidate else None,
        "sha256": strategy_sha,
        "schema": strategy_schema,
    },
    "risk_expectations_read_only": expectations,
    "selector_probe": {},
    "findings": findings,
    "errors": errors,
    "safety": {
        "SCALPX_OBSERVE_ONLY": os.environ.get("SCALPX_OBSERVE_ONLY"),
        "app_main_runtime_started": False,
        "bin_replay_run_patched": False,
        "broker_calls_executed": False,
        "code_patched": False,
        "engine_execution_performed": False,
        "execution_shadow_created": False,
        "full_replay_engine_run": False,
        "live_redis_writes_executed": False,
        "orders_sent": False,
        "paper_or_live_enabled": False,
        "risk_outputs_candidate_only": risk_outputs_candidate_written,
        "risk_outputs_created": risk_outputs_candidate_written,
        "services_started": False,
        "strategy_risk_execution_parity_claimed": False,
    },
}

proof_path = RUN_PROOFS / f"proof_replay_data_a13_risk_outputs_shadow_{NOW}.json"
audit_path = RUN_AUDITS / f"audit_replay_data_a13_risk_outputs_shadow_{NOW}.json"
doc_path = DOCS / f"replay_data_a13_risk_outputs_shadow_{NOW}.md"

proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
audit_path.write_text(json.dumps({
    "batch": BATCH,
    "created_at": NOW,
    "read_only_inputs": {
        "a12_proof": rel(LATEST_PROOF),
        "strategy_decisions_candidate": rel(strategy_candidate) if strategy_candidate else None,
        "risk_expectation_sources": [x.get("path") for x in expectations if x.get("exists")],
    },
    "written_outputs": {
        "proof": rel(proof_path),
        "milestone": rel(doc_path),
        "risk_outputs_candidate": rel(risk_candidate_path) if risk_outputs_candidate_written else None,
    },
    "safety": proof["safety"],
}, indent=2, sort_keys=True), encoding="utf-8")

doc = []
doc.append(f"# {BATCH} — {TITLE}")
doc.append("")
doc.append(f"- created_at: {NOW}")
doc.append(f"- canonical_root: {proof.get('canonical_root')}")
doc.append(f"- source_date: {source_date}")
doc.append(f"- strategy_decisions_candidate: {rel(strategy_candidate) if strategy_candidate else None}")
doc.append(f"- risk_outputs_candidate_written: {str(risk_outputs_candidate_written).lower()}")
doc.append(f"- row_count: {row_count}")
doc.append("- engine_ready: false")
doc.append("- engine_execution_performed: false")
doc.append("- execution_shadow_created: false")
doc.append(f"- next_batch: {proof['summary']['next_batch']}")
doc.append("")
doc.append("Conservative risk shadow reconstruction uses allow=false / no_order / risk_blocked rows only. No full replay engine, services, broker/API, Redis writes, paper/live enablement, or source code patches were performed.")
if errors:
    doc.append("")
    doc.append("## Errors")
    for e in errors:
        doc.append(f"- {e}")
doc_path.write_text("\n".join(doc) + "\n", encoding="utf-8")

print(json.dumps({
    "batch": BATCH,
    "proof": rel(proof_path),
    "milestone": rel(doc_path),
    "risk_outputs_candidate_written": risk_outputs_candidate_written,
    "row_count": row_count,
    "engine_ready": False,
    "next_batch": proof["summary"]["next_batch"],
}, sort_keys=True))
if errors:
    raise SystemExit(2)
PY
.venv/bin/python /tmp/replay_data_a13_risk_outputs_shadow.py
