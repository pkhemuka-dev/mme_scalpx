cd /home/Lenovo/scalpx/projects/mme_scalpx && export SCALPX_OBSERVE_ONLY=1 && unset SCALPX_LIVE_ENABLED SCALPX_PAPER_ENABLED MME_SCALPX_LIVE_ENABLED MME_SCALPX_PAPER_ENABLED ENABLE_LIVE ENABLE_PAPER PAPER_TRADING LIVE_TRADING TRADING_MODE LIVE_MODE PAPER_MODE ALPACA_LIVE ALPACA_PAPER && cat > /tmp/replay_data_a11_features_rows_reconstruction.py <<'PY'
import csv
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

os.environ["SCALPX_OBSERVE_ONLY"] = "1"
for _k in [
    "SCALPX_LIVE_ENABLED",
    "SCALPX_PAPER_ENABLED",
    "MME_SCALPX_LIVE_ENABLED",
    "MME_SCALPX_PAPER_ENABLED",
    "ENABLE_LIVE",
    "ENABLE_PAPER",
    "PAPER_TRADING",
    "LIVE_TRADING",
    "TRADING_MODE",
    "LIVE_MODE",
    "PAPER_MODE",
    "ALPACA_LIVE",
    "ALPACA_PAPER",
]:
    os.environ.pop(_k, None)

REPO = Path.cwd().resolve()
PROOF_A10 = Path("/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/proof_replay_data_a10_selector_only_cli_dry_probe_20260508T175024Z.json")
TS = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
PROOFS_DIR = REPO / "run" / "proofs"
AUDITS_DIR = REPO / "run" / "audits"
MILESTONES_DIR = REPO / "docs" / "milestones"
PROOF_OUT = PROOFS_DIR / f"proof_replay_data_a11_features_rows_reconstruction_{TS}.json"
AUDIT_OUT = AUDITS_DIR / f"audit_replay_data_a11_features_rows_reconstruction_{TS}.json"
MILESTONE_OUT = MILESTONES_DIR / f"replay_data_a11_features_rows_reconstruction_{TS}.md"

def sha256_bytes(data):
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()

def sha256_file(path, limit=None):
    h = hashlib.sha256()
    total = 0
    with path.open("rb") as f:
        while True:
            n = 1024 * 1024
            if limit is not None:
                remaining = limit - total
                if remaining <= 0:
                    break
                n = min(n, remaining)
            b = f.read(n)
            if not b:
                break
            total += len(b)
            h.update(b)
    return h.hexdigest()

def rel(path):
    try:
        return str(path.resolve().relative_to(REPO))
    except Exception:
        return str(path)

def norm_name(s):
    return re.sub(r"[^a-z0-9]+", "", str(s or "").lower())

def first_existing(row, aliases, colmap):
    for a in aliases:
        c = colmap.get(norm_name(a))
        if c is not None:
            v = row.get(c, "")
            if v is not None and str(v).strip() != "":
                return str(v).strip()
    return ""

def to_decimal(v):
    if v is None:
        return None
    s = str(v).strip()
    if not s:
        return None
    s = s.replace(",", "")
    try:
        return Decimal(s)
    except InvalidOperation:
        return None

def dec_out(v):
    if v is None:
        return ""
    try:
        return format(v.normalize(), "f")
    except Exception:
        return str(v)

def read_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def read_text_limited(path, limit=750000):
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            return f.read(limit)
    except Exception as e:
        return f"<<READ_ERROR: {type(e).__name__}: {e}>>"

def safe_under(path, parent):
    rp = path.resolve()
    pp = parent.resolve()
    try:
        rp.relative_to(pp)
        return True
    except Exception:
        return False

def find_quote_file(root, stem, source_date):
    matches = sorted(root.rglob(stem + ".csv"))
    if not matches:
        return None, []
    preferred = [p for p in matches if source_date in str(p)]
    return (preferred[0] if preferred else matches[0]), matches

def csv_header_and_count(path, sample_limit=5):
    samples = []
    count = 0
    header = []
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        header = list(r.fieldnames or [])
        for row in r:
            count += 1
            if len(samples) < sample_limit:
                samples.append({k: row.get(k, "") for k in header[:25]})
    return header, count, samples

def inspect_python_expectations():
    targets = []
    for name in ("dataset.py", "contracts.py", "reports.py"):
        for p in sorted(REPO.rglob(name)):
            parts = set(p.parts)
            if ".venv" in parts or "__pycache__" in parts:
                continue
            s = str(p)
            if "mme_scalpx" in s or "/replay" in s or "\\replay" in s:
                targets.append(p)
    dedup = []
    seen = set()
    for p in targets:
        if p.resolve() not in seen:
            seen.add(p.resolve())
            dedup.append(p)
    inspections = []
    for p in dedup:
        text = read_text_limited(p)
        lines = text.splitlines()
        hits = []
        for i, line in enumerate(lines, 1):
            if "features_rows" in line or "feature" in line.lower() or "required_file_stems" in line:
                hits.append({"line": i, "text": line.strip()[:260]})
        inspections.append({
            "path": rel(p),
            "sha256_prefix": sha256_file(p, limit=750000),
            "features_rows_hits": hits[:80],
            "hit_count": len(hits),
        })
    features_py = REPO / "app" / "mme_scalpx" / "services" / "features.py"
    features_inspection = {"path": rel(features_py), "exists": features_py.exists()}
    if features_py.exists():
        text = read_text_limited(features_py)
        string_literals = sorted(set(re.findall(r"""['"]([A-Za-z_][A-Za-z0-9_]{1,80})['"]""", text)))
        likely_names = [x for x in string_literals if any(tok in x.lower() for tok in ("bid", "ask", "ltp", "mid", "spread", "feature", "symbol", "token", "provider"))]
        defs = re.findall(r"^\s*(?:async\s+def|def|class)\s+([A-Za-z_][A-Za-z0-9_]*)", text, flags=re.MULTILINE)
        features_inspection.update({
            "sha256_prefix": sha256_file(features_py, limit=750000),
            "function_or_class_names": defs[:80],
            "likely_output_or_field_names": likely_names[:120],
            "read_only": True,
        })
    return inspections, features_inspection

def build_candidate(paths, candidate_path, source_date):
    output_cols = [
        "ts_event",
        "symbol",
        "side",
        "source_stream",
        "bid",
        "ask",
        "ltp",
        "mid",
        "spread",
        "provider",
        "instrument_token",
        "source_file",
        "source_row_number",
        "source_date",
    ]
    aliases = {
        "ts_event": ["ts_event", "event_ts", "timestamp", "ts", "time", "datetime", "exchange_timestamp", "exchange_ts", "received_ts", "created_at"],
        "symbol": ["symbol", "tradingsymbol", "trading_symbol", "instrument", "instrument_symbol", "ticker", "name"],
        "side": ["side", "quote_side", "book_side"],
        "bid": ["bid", "bid_price", "best_bid", "best_bid_price", "bid_px", "bp", "buy_price", "bidprice"],
        "ask": ["ask", "ask_price", "best_ask", "best_ask_price", "ask_px", "ap", "sell_price", "askprice", "offer", "offer_price"],
        "ltp": ["ltp", "last_price", "last", "price", "trade_price", "last_traded_price", "lastprice"],
        "provider": ["provider", "data_provider", "source", "feed_provider", "vendor"],
        "instrument_token": ["instrument_token", "token", "instrumenttoken", "instrument_id", "instrumentid", "exchange_token"],
    }

    schema_maps = {}
    blockers = []
    for stream_name, p in paths:
        with p.open("r", encoding="utf-8", newline="") as f:
            r = csv.DictReader(f)
            header = list(r.fieldnames or [])
        colmap = {norm_name(c): c for c in header}
        mapped = {k: colmap.get(norm_name(a)) for k, vals in aliases.items() for a in vals if colmap.get(norm_name(a))}
        needed_missing = []
        for required in ("ts_event", "symbol", "bid", "ask"):
            if not any(norm_name(a) in colmap for a in aliases[required]):
                needed_missing.append(required)
        if needed_missing:
            blockers.append({"path": rel(p), "missing_required_mappings": needed_missing, "header": header})
        schema_maps[str(p)] = {"header": header, "mapped_any": mapped}
    if blockers:
        return False, 0, None, blockers, schema_maps

    tmp_path = candidate_path.with_name(f".{candidate_path.name}.tmp_a11_{TS}")
    row_count = 0
    per_source = []
    with tmp_path.open("w", encoding="utf-8", newline="") as out:
        w = csv.DictWriter(out, fieldnames=output_cols, extrasaction="ignore")
        w.writeheader()
        for stream_name, p in paths:
            source_rows = 0
            with p.open("r", encoding="utf-8", newline="") as f:
                r = csv.DictReader(f)
                header = list(r.fieldnames or [])
                colmap = {norm_name(c): c for c in header}
                for n, row in enumerate(r, 1):
                    ts_event = first_existing(row, aliases["ts_event"], colmap)
                    symbol = first_existing(row, aliases["symbol"], colmap)
                    bid_s = first_existing(row, aliases["bid"], colmap)
                    ask_s = first_existing(row, aliases["ask"], colmap)
                    bid_d = to_decimal(bid_s)
                    ask_d = to_decimal(ask_s)
                    if not ts_event or not symbol or bid_d is None or ask_d is None:
                        continue
                    ltp_s = first_existing(row, aliases["ltp"], colmap)
                    mid_d = (bid_d + ask_d) / Decimal("2")
                    spread_d = ask_d - bid_d
                    provider = first_existing(row, aliases["provider"], colmap) or "mme_quote_feed"
                    out_row = {
                        "ts_event": ts_event,
                        "symbol": symbol,
                        "side": first_existing(row, aliases["side"], colmap),
                        "source_stream": stream_name,
                        "bid": dec_out(bid_d),
                        "ask": dec_out(ask_d),
                        "ltp": ltp_s,
                        "mid": dec_out(mid_d),
                        "spread": dec_out(spread_d),
                        "provider": provider,
                        "instrument_token": first_existing(row, aliases["instrument_token"], colmap),
                        "source_file": rel(p),
                        "source_row_number": str(n),
                        "source_date": source_date,
                    }
                    w.writerow(out_row)
                    row_count += 1
                    source_rows += 1
            per_source.append({"source_stream": stream_name, "path": rel(p), "candidate_rows": source_rows})
    if row_count <= 0:
        try:
            tmp_path.unlink()
        except Exception:
            pass
        return False, 0, None, [{"reason": "no_rows_after_required_field_filter"}], schema_maps
    os.replace(tmp_path, candidate_path)
    return True, row_count, per_source, [], schema_maps

def main():
    PROOFS_DIR.mkdir(parents=True, exist_ok=True)
    AUDITS_DIR.mkdir(parents=True, exist_ok=True)
    MILESTONES_DIR.mkdir(parents=True, exist_ok=True)

    findings = []
    proof_a10 = read_json(PROOF_A10)
    summary_a10 = proof_a10.get("summary", {})
    canonical_root_s = proof_a10.get("canonical_root") or summary_a10.get("canonical_root")
    source_date = proof_a10.get("source_date") or summary_a10.get("source_date")
    dataset_id = proof_a10.get("dataset_id") or summary_a10.get("dataset_id") or (Path(canonical_root_s).name if canonical_root_s else "")

    if not canonical_root_s or not source_date:
        raise SystemExit("A10 proof missing canonical_root or source_date")

    canonical_root = Path(canonical_root_s)
    if not canonical_root.is_absolute():
        canonical_root = REPO / canonical_root
    canonical_root = canonical_root.resolve()
    allowed_base = (REPO / "run" / "replay" / "parity" / "offline_materialization").resolve()
    if not canonical_root.exists():
        raise SystemExit(f"canonical_root does not exist: {canonical_root}")
    if not safe_under(canonical_root, allowed_base):
        raise SystemExit(f"canonical_root outside allowed replay materialization base: {canonical_root}")

    code_inspections, features_py_inspection = inspect_python_expectations()

    fut_path, fut_matches = find_quote_file(canonical_root, "quote_ticks_mme_fut_stream", source_date)
    opt_path, opt_matches = find_quote_file(canonical_root, "quote_ticks_mme_opt_stream", source_date)

    quote_inspections = []
    for stem, p, matches in [
        ("quote_ticks_mme_fut_stream", fut_path, fut_matches),
        ("quote_ticks_mme_opt_stream", opt_path, opt_matches),
    ]:
        info = {"stem": stem, "found": p is not None, "match_count": len(matches), "matches": [rel(x) for x in matches[:20]]}
        if p is not None:
            header, count, samples = csv_header_and_count(p)
            info.update({
                "selected_path": rel(p),
                "sha256": sha256_file(p),
                "header": header,
                "row_count": count,
                "sample_rows": samples,
            })
        quote_inspections.append(info)

    candidate_written = False
    row_count = 0
    candidate_path = None
    candidate_sha256 = None
    per_source = None
    schema_blockers = []
    schema_maps = {}
    candidate_parent_reason = ""

    if fut_path and opt_path:
        parents = {fut_path.parent.resolve(), opt_path.parent.resolve()}
        if len(parents) == 1:
            candidate_parent = fut_path.parent.resolve()
            candidate_parent_reason = "same_parent_as_selected_quote_csv_files"
        elif (canonical_root / source_date).exists() and (canonical_root / source_date).is_dir():
            candidate_parent = (canonical_root / source_date).resolve()
            candidate_parent_reason = "source_date_directory_under_canonical_root"
        else:
            candidate_parent = canonical_root
            candidate_parent_reason = "canonical_root_fallback_for_multi_parent_quotes"
        candidate_path = candidate_parent / "features_rows_candidate.csv"
        if not safe_under(candidate_path, canonical_root):
            raise SystemExit(f"candidate path outside canonical dataset root: {candidate_path}")
        candidate_written, row_count, per_source, schema_blockers, schema_maps = build_candidate(
            [
                ("quote_ticks_mme_fut_stream", fut_path),
                ("quote_ticks_mme_opt_stream", opt_path),
            ],
            candidate_path,
            source_date,
        )
        if candidate_written:
            candidate_sha256 = sha256_file(candidate_path)
        else:
            candidate_path = None
    else:
        schema_blockers.append({"reason": "missing_required_quote_csv", "fut_found": fut_path is not None, "opt_found": opt_path is not None})

    found_stems = {}
    for p in canonical_root.rglob("*"):
        if p.is_file() and p.suffix.lower() in (".csv", ".json", ".jsonl"):
            found_stems.setdefault(p.stem, []).append(rel(p))
    required_stems = ["quote_ticks_mme_fut_stream", "quote_ticks_mme_opt_stream"]
    if candidate_written:
        required_stems.append("features_rows_candidate")
    available_dates = sorted(set(re.findall(r"\d{4}-\d{2}-\d{2}", "\n".join(found_stems.get("quote_ticks_mme_fut_stream", []) + found_stems.get("quote_ticks_mme_opt_stream", [])))))
    if source_date not in available_dates:
        available_dates.append(source_date)
        available_dates = sorted(set(available_dates))
    selector_plan_ok = all(stem in found_stems for stem in required_stems) and (source_date in available_dates) and candidate_written
    fingerprint_payload = json.dumps({
        "dataset_id": dataset_id,
        "canonical_root": rel(canonical_root),
        "source_date": source_date,
        "required_stems": required_stems,
        "candidate_path": rel(candidate_path) if candidate_path else None,
        "candidate_sha256": candidate_sha256,
        "row_count": row_count,
    }, sort_keys=True).encode("utf-8")
    selection_fingerprint = sha256_bytes(fingerprint_payload)

    if not candidate_written:
        findings.append({
            "severity": "BLOCKED",
            "area": "features_rows_candidate",
            "message": "features_rows_candidate.csv was not written because schema-safe reconstruction criteria were not met.",
            "blockers": schema_blockers,
        })
    if not selector_plan_ok:
        findings.append({
            "severity": "BLOCKED",
            "area": "selector_only_probe",
            "message": "Selector-only filesystem probe did not validate all required stems including the candidate.",
        })
    findings.append({
        "severity": "INFO",
        "area": "engine_readiness",
        "message": "A11 reconstructs a quote-derived features_rows candidate only; replay engine execution remains intentionally disabled.",
    })

    proof = {
        "batch": "REPLAY-DATA-A11",
        "title": "Reconstruct features_rows candidate from quote feeds",
        "proof_source": rel(PROOF_A10),
        "a10_verdict": summary_a10.get("overall_verdict") or proof_a10.get("verdict"),
        "canonical_root": rel(canonical_root),
        "dataset_id": dataset_id,
        "source_date": source_date,
        "summary": {
            "features_rows_candidate_written": candidate_written,
            "row_count": row_count,
            "selector_plan_ok": selector_plan_ok,
            "engine_ready": False,
            "engine_execution_performed": False,
            "next_batch": "REPLAY-DATA-A12 strategy_decisions shadow reconstruction audit",
            "candidate_path": rel(candidate_path) if candidate_path else None,
            "candidate_sha256": candidate_sha256,
            "candidate_parent_reason": candidate_parent_reason,
            "selection_fingerprint": selection_fingerprint,
        },
        "quote_feed_inspection": quote_inspections,
        "python_schema_inspection": {
            "replay_dataset_contracts_reports": code_inspections,
            "features_service_read_only": features_py_inspection,
        },
        "candidate_schema": {
            "output_columns": [
                "ts_event",
                "symbol",
                "side",
                "source_stream",
                "bid",
                "ask",
                "ltp",
                "mid",
                "spread",
                "provider",
                "instrument_token",
                "source_file",
                "source_row_number",
                "source_date",
            ],
            "simple_derived_fields": ["mid", "spread", "source_stream", "source_file", "source_row_number", "source_date"],
            "source_fields_preserved": ["ts_event", "symbol", "side", "bid", "ask", "ltp", "provider", "instrument_token"],
            "per_source": per_source,
            "schema_maps": schema_maps,
            "schema_blockers": schema_blockers,
        },
        "selector_only_probe": {
            "performed_by": "filesystem_selector_only_no_replay_engine",
            "available_dates": available_dates,
            "selected_dates": [source_date] if source_date in available_dates else [],
            "required_file_stems": required_stems,
            "found_required_stems": {k: found_stems.get(k, []) for k in required_stems},
            "selector_plan_ok": selector_plan_ok,
            "selection_fingerprint": selection_fingerprint,
        },
        "findings": findings,
        "safety": {
            "SCALPX_OBSERVE_ONLY": os.environ.get("SCALPX_OBSERVE_ONLY"),
            "services_started": False,
            "orders_sent": False,
            "paper_or_live_enabled": False,
            "broker_calls_executed": False,
            "live_redis_writes_executed": False,
            "engine_execution_performed": False,
            "app_main_runtime_started": False,
            "code_patched": False,
            "bin_replay_run_patched": False,
            "strategy_decisions_created": False,
            "risk_outputs_created": False,
            "execution_shadow_created": False,
        },
        "verdict": "PASS_FEATURES_ROWS_CANDIDATE_WRITTEN" if candidate_written and selector_plan_ok else "BLOCKED_FEATURES_ROWS_CANDIDATE_NOT_SCHEMA_SAFE",
    }

    PROOF_OUT.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    AUDIT_OUT.write_text(json.dumps({
        "batch": "REPLAY-DATA-A11",
        "proof": rel(PROOF_OUT),
        "candidate_path": rel(candidate_path) if candidate_path else None,
        "candidate_written": candidate_written,
        "row_count": row_count,
        "selector_plan_ok": selector_plan_ok,
        "engine_ready": False,
        "next_batch": "REPLAY-DATA-A12 strategy_decisions shadow reconstruction audit",
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    milestone = "\n".join([
        f"# REPLAY-DATA-A11 features_rows reconstruction {TS}",
        "",
        f"- canonical_root: `{rel(canonical_root)}`",
        f"- source_date: `{source_date}`",
        f"- features_rows_candidate_written: `{str(candidate_written).lower()}`",
        f"- row_count: `{row_count}`",
        f"- selector_plan_ok: `{str(selector_plan_ok).lower()}`",
        "- engine_ready: `false`",
        "- replay_engine_execution: `false`",
        f"- candidate_path: `{rel(candidate_path) if candidate_path else ''}`",
        f"- proof: `{rel(PROOF_OUT)}`",
        f"- next_batch: `REPLAY-DATA-A12 strategy_decisions shadow reconstruction audit`",
        "",
        "A11 only materialized a conservative quote-derived features_rows candidate and ran a selector-only filesystem validation. It did not create strategy_decisions, risk_outputs, or execution_shadow.",
        "",
    ])
    MILESTONE_OUT.write_text(milestone, encoding="utf-8")

    print(f"features_rows_candidate_written={str(candidate_written).lower()}")
    print(f"row_count={row_count}")
    print(f"selector_plan_ok={str(selector_plan_ok).lower()}")
    print("engine_ready=false")
    print("next_batch=REPLAY-DATA-A12 strategy_decisions shadow reconstruction audit")
    print(f"proof_path={rel(PROOF_OUT)}")
    print(f"milestone_path={rel(MILESTONE_OUT)}")

if __name__ == "__main__":
    main()
PY
.venv/bin/python /tmp/replay_data_a11_features_rows_reconstruction.py
