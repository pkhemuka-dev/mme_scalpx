cd /home/Lenovo/scalpx/projects/mme_scalpx && export SCALPX_OBSERVE_ONLY=1 && unset SCALPX_PAPER_ENABLED SCALPX_LIVE_ENABLED PAPER_TRADING LIVE_TRADING ENABLE_PAPER_TRADING ENABLE_LIVE_TRADING MME_SCALPX_PAPER MME_SCALPX_LIVE SCALPX_ENABLE_ORDERS SCALPX_ENABLE_BROKER SCALPX_REDIS_WRITES REDIS_URL BROKER_API_KEY BROKER_ACCESS_TOKEN KITE_API_KEY KITE_ACCESS_TOKEN && cat > /tmp/replay_data_a12_strategy_decisions_shadow.py <<'PY'
import csv
import datetime as dt
import hashlib
import json
import os
import re
from collections import Counter
from pathlib import Path

PROJECT = Path("/home/Lenovo/scalpx/projects/mme_scalpx").resolve()
PREV_PROOF = PROJECT / "run/proofs/proof_replay_data_a11_features_rows_reconstruction_20260508T180133Z.json"
BATCH = "REPLAY-DATA-A12"
TITLE = "strategy_decisions shadow reconstruction audit"
OFFLINE_ROOT = (PROJECT / "run/replay/parity/offline_materialization").resolve()
PROOFS_DIR = PROJECT / "run/proofs"
MILESTONES_DIR = PROJECT / "docs/milestones"

def utc_stamp():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

STAMP = utc_stamp()

def rel(p):
    p = Path(p).resolve()
    try:
        return str(p.relative_to(PROJECT))
    except Exception:
        return str(p)

def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def read_text_limited(path, limit=300000):
    try:
        with Path(path).open("r", encoding="utf-8", errors="replace") as f:
            return f.read(limit)
    except Exception as exc:
        return ""

def safe_under(child, parent):
    try:
        Path(child).resolve().relative_to(Path(parent).resolve())
        return True
    except Exception:
        return False

def load_json(path):
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)

def csv_header_and_samples(path, sample_n=8):
    with Path(path).open("r", encoding="utf-8", newline="") as f:
        rdr = csv.DictReader(f)
        header = list(rdr.fieldnames or [])
        samples = []
        for i, row in enumerate(rdr):
            if i >= sample_n:
                break
            samples.append({k: row.get(k, "") for k in header[:40]})
    return header, samples

def count_csv_rows(path):
    n = 0
    with Path(path).open("r", encoding="utf-8", newline="") as f:
        rdr = csv.reader(f)
        try:
            next(rdr)
        except StopIteration:
            return 0
        for _ in rdr:
            n += 1
    return n

def inspect_source_file(path):
    p = PROJECT / path
    info = {
        "path": str(path),
        "exists": p.exists(),
        "size_bytes": p.stat().st_size if p.exists() else None,
        "sha256": sha256_file(p) if p.exists() and p.is_file() else None,
        "strategy_decisions_mentions": 0,
        "hold_mentions": 0,
        "no_trade_mentions": 0,
        "candidate_column_literals": [],
    }
    if p.exists() and p.is_file():
        text = read_text_limited(p)
        low = text.lower()
        info["strategy_decisions_mentions"] = low.count("strategy_decisions")
        info["hold_mentions"] = text.count("HOLD") + low.count("hold")
        info["no_trade_mentions"] = text.count("NO_TRADE") + low.count("no_trade")
        literals = []
        for m in re.finditer(r"['\"]([A-Za-z_][A-Za-z0-9_]{1,50})['\"]", text):
            s = m.group(1)
            sl = s.lower()
            if any(tok in sl for tok in ("strategy", "decision", "signal", "action", "confidence", "reason", "symbol", "timestamp", "ts_event")):
                literals.append(s)
        info["candidate_column_literals"] = sorted(set(literals))[:80]
    return info

def find_existing_strategy_headers():
    headers = []
    if OFFLINE_ROOT.exists():
        for p in OFFLINE_ROOT.rglob("strategy_decisions*.csv"):
            if not p.is_file():
                continue
            if not safe_under(p, OFFLINE_ROOT):
                continue
            try:
                with p.open("r", encoding="utf-8", newline="") as f:
                    rdr = csv.reader(f)
                    h = next(rdr, [])
                headers.append({"path": rel(p), "header": h, "sha256": sha256_file(p), "size_bytes": p.stat().st_size})
            except Exception as exc:
                headers.append({"path": rel(p), "error": repr(exc)})
    return headers[:25]

def choose_header(existing_headers):
    valid = []
    for item in existing_headers:
        h = item.get("header") or []
        low = {c.lower() for c in h}
        if ("symbol" in low or "instrument_token" in low) and any(c in low for c in ("ts_event", "timestamp", "ts", "time")) and any(c in low for c in ("decision", "action", "signal", "strategy_action", "trade_action")):
            valid.append(h)
    if valid:
        return valid[0], "adopted_existing_strategy_decisions_header"
    return [
        "ts_event",
        "symbol",
        "strategy",
        "decision",
        "action",
        "signal",
        "side",
        "confidence",
        "reason",
        "source_stream",
        "source_provider",
        "instrument_token",
        "source_bid",
        "source_ask",
        "source_ltp",
        "source_mid",
        "source_spread",
        "source_feature_row_index",
        "source_features_sha256",
    ], "shadow_schema_v1_conservative_hold_no_trade"

def first_present(row, names, default=""):
    for name in names:
        if name in row and row.get(name, "") not in (None, ""):
            return row.get(name, "")
    return default

def fill_value(col, row, idx, features_sha):
    c = col.lower()
    if c in ("ts_event", "timestamp", "ts", "time", "event_time"):
        return first_present(row, ("ts_event", "timestamp", "ts", "time", "event_time"))
    if c == "symbol" or c == "tradingsymbol":
        return first_present(row, ("symbol", "tradingsymbol", "instrument", "name"))
    if c == "instrument_token":
        return first_present(row, ("instrument_token", "token"))
    if c in ("strategy", "strategy_name", "source"):
        return "A12_SHADOW_CONSERVATIVE"
    if c in ("decision", "strategy_decision"):
        return "HOLD"
    if c in ("action", "strategy_action", "trade_action"):
        return "NO_TRADE"
    if c in ("signal", "signal_name"):
        return "HOLD"
    if c in ("side", "direction"):
        return first_present(row, ("side", "source_stream", "stream"), "NONE")
    if c in ("qty", "quantity", "order_qty", "target_qty", "position_delta"):
        return "0"
    if c in ("confidence", "score", "probability"):
        return "0.0"
    if c in ("reason", "notes", "comment"):
        return "A12 conservative shadow reconstruction from features_rows_candidate; no strategy/risk/execution parity claimed"
    if c in ("source_stream", "stream"):
        return first_present(row, ("source_stream", "stream", "side"))
    if c in ("source_provider", "provider"):
        return first_present(row, ("provider", "source_provider"))
    if c in ("source_bid", "bid"):
        return first_present(row, ("bid", "source_bid"))
    if c in ("source_ask", "ask"):
        return first_present(row, ("ask", "source_ask"))
    if c in ("source_ltp", "ltp", "last_price"):
        return first_present(row, ("ltp", "last_price", "source_ltp"))
    if c in ("source_mid", "mid"):
        return first_present(row, ("mid", "source_mid"))
    if c in ("source_spread", "spread"):
        return first_present(row, ("spread", "source_spread"))
    if c in ("source_feature_row_index", "feature_row_index", "row_index"):
        return str(idx)
    if c in ("source_features_sha256", "features_sha256"):
        return features_sha
    return ""

def write_strategy_candidate(features_path, out_path, header, features_sha):
    row_count = 0
    tmp = out_path.with_suffix(out_path.suffix + ".tmp")
    with features_path.open("r", encoding="utf-8", newline="") as fin, tmp.open("w", encoding="utf-8", newline="") as fout:
        rdr = csv.DictReader(fin)
        w = csv.DictWriter(fout, fieldnames=header, extrasaction="ignore")
        w.writeheader()
        for idx, row in enumerate(rdr, start=1):
            out = {col: fill_value(col, row, idx, features_sha) for col in header}
            w.writerow(out)
            row_count += 1
    os.replace(tmp, out_path)
    return row_count

def main():
    if os.environ.get("SCALPX_OBSERVE_ONLY") != "1":
        raise SystemExit("SCALPX_OBSERVE_ONLY must be 1")
    forbidden_truthy = []
    for k in ("SCALPX_PAPER_ENABLED", "SCALPX_LIVE_ENABLED", "PAPER_TRADING", "LIVE_TRADING", "ENABLE_PAPER_TRADING", "ENABLE_LIVE_TRADING", "MME_SCALPX_PAPER", "MME_SCALPX_LIVE", "SCALPX_ENABLE_ORDERS", "SCALPX_ENABLE_BROKER", "SCALPX_REDIS_WRITES"):
        v = os.environ.get(k)
        if v and v.strip().lower() not in ("0", "false", "no", "off", ""):
            forbidden_truthy.append({k: v})
    if forbidden_truthy:
        raise SystemExit("paper/live/order/broker/write env flags must be unset or false: " + repr(forbidden_truthy))

    prev = load_json(PREV_PROOF)
    if prev.get("batch") != "REPLAY-DATA-A11":
        raise SystemExit("previous proof is not REPLAY-DATA-A11")
    prev_summary = prev.get("summary", {})
    if not prev_summary.get("features_rows_candidate_written"):
        raise SystemExit("previous proof did not write features_rows_candidate")
    if prev_summary.get("engine_execution_performed") is not False:
        raise SystemExit("previous proof unexpectedly reports engine execution")

    canonical_root_raw = prev.get("canonical_root")
    source_date = prev.get("source_date")
    if not canonical_root_raw or not source_date:
        raise SystemExit("missing canonical_root/source_date in previous proof")

    canonical_root = (PROJECT / canonical_root_raw).resolve() if not Path(canonical_root_raw).is_absolute() else Path(canonical_root_raw).resolve()
    if not safe_under(canonical_root, OFFLINE_ROOT):
        raise SystemExit("canonical_root is outside offline materialization root")
    if not canonical_root.exists():
        raise SystemExit("canonical_root does not exist")

    date_root = (canonical_root / source_date).resolve()
    if not safe_under(date_root, canonical_root):
        raise SystemExit("date root escapes canonical_root")
    if not date_root.exists():
        raise SystemExit("source date root does not exist")

    candidate_raw = prev_summary.get("candidate_path") or str(Path(canonical_root_raw) / source_date / "features_rows_candidate.csv")
    features_path = (PROJECT / candidate_raw).resolve() if not Path(candidate_raw).is_absolute() else Path(candidate_raw).resolve()
    if not safe_under(features_path, date_root):
        raise SystemExit("features_rows_candidate path is outside canonical date root")
    if not features_path.exists():
        raise SystemExit("features_rows_candidate does not exist")

    PROOFS_DIR.mkdir(parents=True, exist_ok=True)
    MILESTONES_DIR.mkdir(parents=True, exist_ok=True)

    features_sha = sha256_file(features_path)
    features_header, features_samples = csv_header_and_samples(features_path, 8)
    features_row_count = count_csv_rows(features_path)
    low_header = {h.lower() for h in features_header}
    required_feature_ok = ("ts_event" in low_header or "timestamp" in low_header or "ts" in low_header) and ("symbol" in low_header or "instrument_token" in low_header)
    price_feature_ok = any(c in low_header for c in ("bid", "ask", "ltp", "mid", "last_price"))

    inspections = {
        "features_rows_candidate": {
            "path": rel(features_path),
            "sha256": features_sha,
            "row_count": features_row_count,
            "header": features_header,
            "sample_rows": features_samples,
            "required_feature_ok": required_feature_ok,
            "price_feature_ok": price_feature_ok,
        },
        "read_only_source_inspection": [
            inspect_source_file("app/mme_scalpx/replay/dataset.py"),
            inspect_source_file("app/mme_scalpx/replay/contracts.py"),
            inspect_source_file("app/mme_scalpx/replay/reports.py"),
            inspect_source_file("app/mme_scalpx/services/strategy.py"),
            inspect_source_file("services/strategy.py"),
        ],
        "existing_strategy_decisions_headers": find_existing_strategy_headers(),
    }

    header, header_reason = choose_header(inspections["existing_strategy_decisions_headers"])
    schema_safe = bool(required_feature_ok and price_feature_ok and features_row_count > 0 and header)
    out_path = (date_root / "strategy_decisions_candidate.csv").resolve()
    if not safe_under(out_path, date_root):
        raise SystemExit("strategy_decisions_candidate path escapes date root")

    strategy_decisions_candidate_written = False
    row_count = 0
    candidate_sha = None
    write_reason = "not_written_schema_safety_failed"
    if schema_safe:
        row_count = write_strategy_candidate(features_path, out_path, header, features_sha)
        candidate_sha = sha256_file(out_path)
        strategy_decisions_candidate_written = True
        write_reason = header_reason

    proof = {
        "batch": BATCH,
        "title": TITLE,
        "timestamp_utc": STAMP,
        "previous_proof": rel(PREV_PROOF),
        "canonical_root": rel(canonical_root),
        "source_date": source_date,
        "features_rows_candidate": rel(features_path),
        "inspections": inspections,
        "schema_decision": {
            "schema_safe": schema_safe,
            "header_reason": header_reason,
            "selected_header": header,
            "write_reason": write_reason,
            "conservative_policy": "HOLD/NO_TRADE shadow rows only; no strategy parity claimed",
        },
        "summary": {
            "strategy_decisions_candidate_written": strategy_decisions_candidate_written,
            "candidate_path": rel(out_path) if strategy_decisions_candidate_written else None,
            "candidate_sha256": candidate_sha,
            "row_count": row_count,
            "source_features_row_count": features_row_count,
            "engine_ready": False,
            "engine_execution_performed": False,
            "next_batch": "REPLAY-DATA-A13 risk_outputs shadow reconstruction audit",
        },
        "findings": [
            {
                "severity": "INFO",
                "area": "strategy_shadow",
                "message": "A12 writes only conservative HOLD/NO_TRADE strategy_decisions_candidate rows from features_rows_candidate when schema-safe."
            },
            {
                "severity": "INFO",
                "area": "engine_readiness",
                "message": "Replay engine execution remains intentionally disabled; no strategy/risk/execution parity is claimed."
            },
        ],
        "safety": {
            "SCALPX_OBSERVE_ONLY": os.environ.get("SCALPX_OBSERVE_ONLY"),
            "app_main_runtime_started": False,
            "bin_replay_run_patched": False,
            "broker_calls_executed": False,
            "code_patched": False,
            "engine_execution_performed": False,
            "execution_shadow_created": False,
            "live_redis_writes_executed": False,
            "orders_sent": False,
            "paper_or_live_enabled": False,
            "risk_outputs_created": False,
            "services_started": False,
            "strategy_decisions_created": strategy_decisions_candidate_written,
            "strategy_decisions_candidate_only": True,
            "full_replay_engine_run": False,
        },
    }

    proof_path = PROOFS_DIR / f"proof_replay_data_a12_strategy_decisions_shadow_{STAMP}.json"
    with proof_path.open("w", encoding="utf-8") as f:
        json.dump(proof, f, indent=2, sort_keys=True)
        f.write("\n")

    md_path = MILESTONES_DIR / f"replay_data_a12_strategy_decisions_shadow_{STAMP}.md"
    md = []
    md.append(f"# {BATCH} — {TITLE}\n")
    md.append(f"- previous_proof: `{rel(PREV_PROOF)}`")
    md.append(f"- canonical_root: `{rel(canonical_root)}`")
    md.append(f"- source_date: `{source_date}`")
    md.append(f"- features_rows_candidate: `{rel(features_path)}`")
    md.append(f"- features_rows_sha256: `{features_sha}`")
    md.append(f"- source_features_row_count: `{features_row_count}`")
    md.append(f"- strategy_decisions_candidate_written: `{strategy_decisions_candidate_written}`")
    md.append(f"- row_count: `{row_count}`")
    md.append(f"- candidate_path: `{rel(out_path) if strategy_decisions_candidate_written else ''}`")
    md.append(f"- candidate_sha256: `{candidate_sha or ''}`")
    md.append(f"- schema_safe: `{schema_safe}`")
    md.append(f"- header_reason: `{header_reason}`")
    md.append("- policy: conservative `HOLD` / `NO_TRADE` shadow reconstruction only")
    md.append("- engine_ready: `false`")
    md.append("- engine_execution_performed: `false`")
    md.append("- risk_outputs_created: `false`")
    md.append("- execution_shadow_created: `false`")
    md.append("- strategy/risk/execution parity claimed: `false`")
    md.append("- next_batch: `REPLAY-DATA-A13 risk_outputs shadow reconstruction audit`")
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    final_summary = {
        "batch": BATCH,
        "proof_path": rel(proof_path),
        "milestone_path": rel(md_path),
        "strategy_decisions_candidate_written": strategy_decisions_candidate_written,
        "row_count": row_count,
        "engine_ready": False,
        "next_batch": "REPLAY-DATA-A13 risk_outputs shadow reconstruction audit",
    }
    print(json.dumps(final_summary, sort_keys=True))

if __name__ == "__main__":
    main()
PY
.venv/bin/python /tmp/replay_data_a12_strategy_decisions_shadow.py
