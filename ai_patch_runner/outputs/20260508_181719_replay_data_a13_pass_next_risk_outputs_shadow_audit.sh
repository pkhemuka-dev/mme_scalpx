set -euo pipefail
export SCALPX_OBSERVE_ONLY=1
unset SCALPX_LIVE SCALPX_PAPER SCALPX_ENABLE_LIVE SCALPX_ENABLE_PAPER MME_SCALPX_LIVE MME_SCALPX_PAPER LIVE_TRADING PAPER_TRADING ENABLE_LIVE ENABLE_PAPER BROKER_LOGIN BROKER_TOKEN API_KEY API_SECRET REDIS_URL

.venv/bin/python - <<'PY'
import csv
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
PROOF_IN = Path("/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/proof_replay_data_a12_strategy_decisions_shadow_20260508T181220Z.json")
BATCH = "REPLAY-DATA-A13"
TITLE = "risk_outputs shadow reconstruction audit"

def utc_stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def rel(p):
    try:
        return str(Path(p).resolve().relative_to(ROOT.resolve()))
    except Exception:
        return str(p)

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def safe_path_under(path, parent):
    try:
        Path(path).resolve().relative_to(Path(parent).resolve())
        return True
    except Exception:
        return False

def read_csv_header_and_samples(path, sample_limit=5):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        rdr = csv.DictReader(f)
        header = list(rdr.fieldnames or [])
        samples = []
        for i, row in enumerate(rdr):
            if i < sample_limit:
                samples.append(dict(row))
            else:
                break
    return header, samples

def count_csv_rows(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        rdr = csv.reader(f)
        try:
            next(rdr)
        except StopIteration:
            return 0
        return sum(1 for _ in rdr)

def first_present(row, names, default=""):
    lower = {str(k).lower(): k for k in row.keys()}
    for name in names:
        k = lower.get(name.lower())
        if k is not None:
            v = row.get(k, "")
            if v is not None and str(v) != "":
                return str(v)
    return default

def bool_text(v):
    return "false" if not v else "true"

def read_text_limited(path, limit=750000):
    try:
        data = Path(path).read_text(encoding="utf-8", errors="replace")
        return data[:limit]
    except Exception as e:
        return f"__READ_ERROR__ {type(e).__name__}: {e}"

def inspect_readonly_files():
    candidates = []
    explicit = [
        "app/mme_scalpx/replay/contracts.py",
        "app/mme_scalpx/replay/reports.py",
        "app/mme_scalpx/replay/dataset.py",
        "app/mme_scalpx/services/risk.py",
        "services/risk.py",
    ]
    for e in explicit:
        p = ROOT / e
        if p.exists() and p.is_file():
            candidates.append(p)
    for pat in [
        "app/**/contracts.py",
        "app/**/reports.py",
        "app/**/dataset.py",
        "app/**/risk.py",
        "services/**/risk.py",
    ]:
        for p in ROOT.glob(pat):
            if p.is_file() and p not in candidates:
                candidates.append(p)
    findings = []
    risk_column_hints = set()
    risk_filename_mentions = []
    for p in candidates[:80]:
        text = read_text_limited(p)
        digest = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()
        lines = text.splitlines()
        hit_lines = []
        for idx, line in enumerate(lines, start=1):
            low = line.lower()
            if "risk_output" in low or "risk outputs" in low or "risk_outputs" in low or "allow" in low or "blocked" in low or "no_order" in low:
                hit_lines.append({"line": idx, "text": line.strip()[:220]})
                if len(hit_lines) >= 30:
                    break
        for m in re.finditer(r"risk_outputs(?:_candidate)?\.csv|risk_outputs", text, flags=re.IGNORECASE):
            risk_filename_mentions.append({"file": rel(p), "match": m.group(0)})
        for m in re.finditer(r"""['"]([A-Za-z_][A-Za-z0-9_]{1,48})['"]""", text):
            token = m.group(1)
            low = token.lower()
            if any(x in low for x in ["risk", "allow", "allowed", "block", "qty", "order", "reason", "decision", "symbol", "ts_event", "timestamp", "side", "action"]):
                risk_column_hints.add(token)
        findings.append({
            "path": rel(p),
            "sha256_text_limited": digest,
            "bytes_inspected_limited": len(text.encode("utf-8", errors="replace")),
            "risk_related_line_hits": hit_lines,
        })
    return findings, sorted(risk_column_hints), risk_filename_mentions

def canonicalize_path(p):
    pp = Path(p)
    if pp.is_absolute():
        return pp
    return ROOT / pp

def make_candidate(strategy_path, out_path, input_header):
    base_cols = [
        "ts_event",
        "symbol",
        "source_strategy_action",
        "source_strategy_decision",
        "source_strategy_side",
        "source_strategy_signal",
        "source_strategy_reason",
        "requested_qty",
        "approved_qty",
        "qty",
        "allow",
        "allowed",
        "risk_pass",
        "risk_blocked",
        "risk_action",
        "risk_decision",
        "order_action",
        "block_reason",
        "reason",
        "source_strategy_row_index",
        "provider",
        "instrument_token",
    ]
    cols = []
    for c in base_cols:
        if c not in cols:
            cols.append(c)

    row_count = 0
    with open(strategy_path, "r", encoding="utf-8-sig", newline="") as src, open(out_path, "w", encoding="utf-8", newline="") as dst:
        rdr = csv.DictReader(src)
        w = csv.DictWriter(dst, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for idx, row in enumerate(rdr):
            ts = first_present(row, ["ts_event", "timestamp", "ts", "time", "datetime"], "")
            symbol = first_present(row, ["symbol", "tradingsymbol", "instrument", "instrument_symbol"], "")
            action = first_present(row, ["action", "strategy_action", "decision", "signal_action"], "HOLD")
            decision = first_present(row, ["decision", "strategy_decision", "trade_decision"], "NO_TRADE")
            side = first_present(row, ["side", "intent_side", "trade_side", "order_side"], "")
            signal = first_present(row, ["signal", "strategy_signal", "signal_name"], "")
            src_reason = first_present(row, ["reason", "strategy_reason", "note", "notes"], "")
            provider = first_present(row, ["provider", "source_provider"], "")
            token = first_present(row, ["instrument_token", "token"], "")
            requested_qty = first_present(row, ["qty", "quantity", "order_qty", "requested_qty", "target_qty"], "0")
            out = {
                "ts_event": ts,
                "symbol": symbol,
                "source_strategy_action": action,
                "source_strategy_decision": decision,
                "source_strategy_side": side,
                "source_strategy_signal": signal,
                "source_strategy_reason": src_reason,
                "requested_qty": requested_qty if requested_qty else "0",
                "approved_qty": "0",
                "qty": "0",
                "allow": "false",
                "allowed": "false",
                "risk_pass": "false",
                "risk_blocked": "true",
                "risk_action": "NO_ORDER",
                "risk_decision": "RISK_BLOCKED",
                "order_action": "NO_ORDER",
                "block_reason": "A13 conservative shadow reconstruction: no live risk proof; no order allowed",
                "reason": "conservative_no_order_risk_shadow",
                "source_strategy_row_index": str(idx),
                "provider": provider,
                "instrument_token": token,
            }
            w.writerow(out)
            row_count += 1
    return row_count, cols

stamp = utc_stamp()
proof_dir = ROOT / "run" / "proofs"
audit_dir = ROOT / "run" / "audits"
docs_dir = ROOT / "docs" / "milestones"
proof_dir.mkdir(parents=True, exist_ok=True)
audit_dir.mkdir(parents=True, exist_ok=True)
docs_dir.mkdir(parents=True, exist_ok=True)

findings = []
errors = []
candidate_written = False
candidate_path = None
candidate_sha = None
row_count = 0
output_cols = []
engine_ready = False
next_batch = "REPLAY-DATA-A14 execution shadow reconstruction audit"

if not PROOF_IN.exists():
    errors.append(f"A12 proof not found: {PROOF_IN}")
else:
    prev = read_json(PROOF_IN)
    prev_batch = prev.get("batch")
    if prev_batch != "REPLAY-DATA-A12":
        errors.append(f"Input proof batch is {prev_batch}, expected REPLAY-DATA-A12")
    prev_summary = prev.get("summary") or {}
    canonical_root_raw = prev.get("canonical_root") or prev_summary.get("canonical_root")
    source_date = prev.get("source_date") or prev_summary.get("source_date")
    strategy_candidate_raw = prev_summary.get("candidate_path") or prev.get("strategy_decisions_candidate") or prev_summary.get("strategy_decisions_candidate_path")

    if not canonical_root_raw:
        errors.append("canonical_root missing from A12 proof")
    if not source_date:
        errors.append("source_date missing from A12 proof")
    if not strategy_candidate_raw:
        errors.append("strategy_decisions_candidate path missing from A12 proof summary")

    if not errors:
        canonical_root = canonicalize_path(canonical_root_raw)
        source_dir = canonical_root / source_date
        strategy_path = canonicalize_path(strategy_candidate_raw)
        if not canonical_root.exists() or not canonical_root.is_dir():
            errors.append(f"canonical_root does not exist or is not a directory: {canonical_root}")
        if not source_dir.exists() or not source_dir.is_dir():
            errors.append(f"source_date directory does not exist: {source_dir}")
        if not strategy_path.exists() or not strategy_path.is_file():
            errors.append(f"strategy_decisions_candidate.csv not found: {strategy_path}")
        if not safe_path_under(strategy_path, canonical_root):
            errors.append("strategy_decisions_candidate is not under canonical_root")
        if strategy_path.name != "strategy_decisions_candidate.csv":
            findings.append({
                "severity": "WARN",
                "area": "strategy_input",
                "message": f"Strategy candidate filename is {strategy_path.name}; proceeding only as candidate under canonical root."
            })

    readonly_inspections, risk_column_hints, risk_filename_mentions = inspect_readonly_files()

    if not errors:
        strategy_header, strategy_samples = read_csv_header_and_samples(strategy_path)
        strategy_rows = count_csv_rows(strategy_path)
        required_any_ts = any(c.lower() in {"ts_event", "timestamp", "ts", "time", "datetime"} for c in strategy_header)
        required_any_symbol = any(c.lower() in {"symbol", "tradingsymbol", "instrument", "instrument_symbol"} for c in strategy_header)
        schema_safe = required_any_ts and required_any_symbol and strategy_rows > 0
        findings.append({
            "severity": "INFO",
            "area": "strategy_decisions_candidate",
            "message": "Inspected strategy_decisions_candidate schema/sample rows read-only.",
            "header": strategy_header,
            "sample_rows": strategy_samples,
            "row_count": strategy_rows,
            "has_time_column": required_any_ts,
            "has_symbol_column": required_any_symbol,
        })
        findings.append({
            "severity": "INFO",
            "area": "risk_expectations_readonly",
            "message": "Inspected replay contracts/reports/dataset and risk.py read-only for risk output expectations; no imports or service runtime starts performed.",
            "files_inspected": readonly_inspections,
            "risk_column_hints": risk_column_hints[:200],
            "risk_filename_mentions": risk_filename_mentions[:100],
        })
        if schema_safe:
            candidate_path = source_dir / "risk_outputs_candidate.csv"
            if not safe_path_under(candidate_path, canonical_root):
                errors.append("Refusing to write risk_outputs_candidate outside canonical_root")
            else:
                row_count, output_cols = make_candidate(strategy_path, candidate_path, strategy_header)
                candidate_written = True
                candidate_sha = sha256_file(candidate_path)
                findings.append({
                    "severity": "INFO",
                    "area": "risk_shadow",
                    "message": "Wrote conservative candidate-only risk_outputs shadow rows with allow=false, risk_blocked=true, NO_ORDER. No execution shadow created."
                })
        else:
            findings.append({
                "severity": "WARN",
                "area": "schema_safety",
                "message": "Did not write risk_outputs_candidate because strategy candidate lacked minimum ts/symbol columns or rows."
            })

summary = {
    "risk_outputs_candidate_written": candidate_written,
    "candidate_path": rel(candidate_path) if candidate_path else None,
    "candidate_sha256": candidate_sha,
    "row_count": row_count,
    "engine_ready": False,
    "engine_execution_performed": False,
    "next_batch": next_batch,
}

proof = {
    "batch": BATCH,
    "title": TITLE,
    "verdict": "PASS_NEXT_EXECUTION_SHADOW_AUDIT" if candidate_written and not errors else "BLOCKED_SCHEMA_OR_INPUT",
    "created_at": stamp,
    "input_proof_path": str(PROOF_IN),
    "canonical_root": prev.get("canonical_root") if PROOF_IN.exists() else None,
    "source_date": prev.get("source_date") if PROOF_IN.exists() else None,
    "summary": summary,
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
        "risk_outputs_candidate_only": candidate_written,
        "risk_outputs_created": candidate_written,
        "services_started": False,
        "strategy_risk_execution_parity_claimed": False,
    },
}

proof_path = proof_dir / f"proof_replay_data_a13_risk_outputs_shadow_{stamp}.json"
audit_path = audit_dir / f"audit_replay_data_a13_risk_outputs_shadow_{stamp}.json"
md_path = docs_dir / f"replay_data_a13_risk_outputs_shadow_{stamp}.md"

with open(proof_path, "w", encoding="utf-8") as f:
    json.dump(proof, f, indent=2, sort_keys=True)
with open(audit_path, "w", encoding="utf-8") as f:
    json.dump({
        "batch": BATCH,
        "title": TITLE,
        "proof_path": rel(proof_path),
        "input_proof_path": str(PROOF_IN),
        "summary": summary,
        "errors": errors,
        "safety": proof["safety"],
    }, f, indent=2, sort_keys=True)

md = []
md.append(f"# {BATCH} — {TITLE}")
md.append("")
md.append(f"- proof: `{rel(proof_path)}`")
md.append(f"- input_proof: `{PROOF_IN}`")
md.append(f"- risk_outputs_candidate_written: `{candidate_written}`")
md.append(f"- row_count: `{row_count}`")
md.append("- engine_ready: `false`")
md.append(f"- next_batch: `{next_batch}`")
md.append("")
md.append("Safety: observe-only; no broker/login/API calls; no Redis writes; no order placement; no services or full replay engine started; no app/bin/service patches.")
if errors:
    md.append("")
    md.append("Errors:")
    for e in errors:
        md.append(f"- {e}")
with open(md_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md) + "\n")

print(json.dumps({
    "batch": BATCH,
    "proof_path": rel(proof_path),
    "milestone_path": rel(md_path),
    "risk_outputs_candidate_written": candidate_written,
    "row_count": row_count,
    "engine_ready": False,
    "next_batch": next_batch,
}, indent=2, sort_keys=True))

if errors:
    raise SystemExit(2)
PY
