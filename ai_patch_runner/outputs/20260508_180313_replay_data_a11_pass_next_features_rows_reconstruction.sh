set -euo pipefail
cd /home/Lenovo/scalpx/projects/mme_scalpx
export SCALPX_OBSERVE_ONLY=1
export LATEST_A10_PROOF="/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/proof_replay_data_a10_selector_only_cli_dry_probe_20260508T175024Z.json"
unset SCALPX_PAPER_MODE SCALPX_LIVE_MODE SCALPX_ENABLE_PAPER SCALPX_ENABLE_LIVE SCALPX_PAPER_TRADING SCALPX_LIVE_TRADING PAPER_TRADING LIVE_TRADING MME_PAPER_TRADING MME_LIVE_TRADING ENABLE_PAPER ENABLE_LIVE TRADING_MODE SCALPX_TRADING_MODE
cat > /tmp/replay_data_a11_features_rows_reconstruction.py <<'PY'
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

BATCH = "REPLAY-DATA-A11"
TITLE = "features_rows reconstruction candidate from quote feeds"
NEXT_BATCH = "REPLAY-DATA-A12 strategy_decisions shadow reconstruction audit"

REQUIRED_ENV_FALSEY = (
    "SCALPX_PAPER_MODE",
    "SCALPX_LIVE_MODE",
    "SCALPX_ENABLE_PAPER",
    "SCALPX_ENABLE_LIVE",
    "SCALPX_PAPER_TRADING",
    "SCALPX_LIVE_TRADING",
    "PAPER_TRADING",
    "LIVE_TRADING",
    "MME_PAPER_TRADING",
    "MME_LIVE_TRADING",
    "ENABLE_PAPER",
    "ENABLE_LIVE",
    "TRADING_MODE",
    "SCALPX_TRADING_MODE",
)

OUTPUT_FIELDS = [
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
    "source_row",
]

ALIASES = {
    "ts_event": [
        "ts_event", "event_ts", "timestamp", "ts", "time", "datetime", "date_time",
        "exchange_timestamp", "exchange_ts", "recv_ts", "received_ts", "created_at",
    ],
    "symbol": [
        "symbol", "tradingsymbol", "trading_symbol", "instrument", "instrument_symbol",
        "name", "ticker", "contract", "security_id",
    ],
    "side": ["side", "quote_side", "book_side"],
    "bid": [
        "bid", "best_bid", "best_bid_price", "bid_price", "bid_px", "bbo_bid",
        "buy_price", "buy_px", "bid1", "bid_price_1", "bp1",
    ],
    "ask": [
        "ask", "best_ask", "best_ask_price", "ask_price", "ask_px", "bbo_ask",
        "sell_price", "sell_px", "ask1", "ask_price_1", "ap1", "offer", "offer_price",
    ],
    "ltp": [
        "ltp", "last", "last_price", "last_traded_price", "price", "trade_price",
        "close", "last_px",
    ],
    "provider": ["provider", "source", "vendor", "feed", "data_provider"],
    "instrument_token": [
        "instrument_token", "token", "instrument_id", "security_token", "security_id",
        "exchange_token", "exchange_instrument_token",
    ],
}

def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def norm_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).strip().lower())

def row_lookup(row: Dict[str, Any]) -> Dict[str, str]:
    return {norm_key(k): k for k in row.keys()}

def pick(row: Dict[str, Any], aliases: Iterable[str]) -> str:
    lookup = row_lookup(row)
    for alias in aliases:
        key = lookup.get(norm_key(alias))
        if key is not None:
            value = row.get(key, "")
            if value is None:
                return ""
            return str(value).strip()
    return ""

def to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    s = str(value).strip().replace(",", "")
    if not s:
        return None
    try:
        return float(s)
    except Exception:
        return None

def fmt_num(value: Optional[float]) -> str:
    if value is None:
        return ""
    return ("%.12g" % value)

def detect_dialect(path: Path) -> csv.Dialect:
    try:
        sample = path.read_text(encoding="utf-8-sig", errors="replace")[:8192]
        if sample.strip():
            return csv.Sniffer().sniff(sample, delimiters=",\t;|")
    except Exception:
        pass
    return csv.excel

def read_header(path: Path) -> List[str]:
    dialect = detect_dialect(path)
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, dialect=dialect)
        return list(reader.fieldnames or [])

def has_alias(header: List[str], logical: str) -> bool:
    normalized = {norm_key(h) for h in header}
    return any(norm_key(a) in normalized for a in ALIASES[logical])

def code_read(path: Path) -> Dict[str, Any]:
    rec: Dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "sha256": None,
        "features_rows_mentions": [],
        "candidate_name_mentions": [],
    }
    if not path.exists() or not path.is_file():
        return rec
    data = path.read_text(encoding="utf-8", errors="replace")
    rec["sha256"] = hashlib.sha256(data.encode("utf-8", errors="replace")).hexdigest()
    for idx, line in enumerate(data.splitlines(), start=1):
        lower = line.lower()
        if "features_rows" in lower or "feature_rows" in lower:
            rec["features_rows_mentions"].append({"line": idx, "text": line.strip()[:240]})
        if "features_rows.csv" in lower or "features_rows_candidate.csv" in lower:
            rec["candidate_name_mentions"].append({"line": idx, "text": line.strip()[:240]})
    return rec

def find_one(root: Path, stem: str) -> Optional[Path]:
    direct = root / f"{stem}.csv"
    if direct.exists():
        return direct
    matches = sorted([p for p in root.rglob(f"{stem}.csv") if p.is_file()])
    return matches[0] if matches else None

def summarize_csv(path: Path) -> Dict[str, Any]:
    header = read_header(path)
    sample_rows = 0
    dialect = detect_dialect(path)
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, dialect=dialect)
        for _ in reader:
            sample_rows += 1
            if sample_rows >= 5:
                break
    return {
        "path": str(path),
        "exists": path.exists(),
        "sha256": sha256_file(path) if path.exists() else None,
        "header": header,
        "sample_row_count_observed": sample_rows,
        "schema_has_ts_event_alias": has_alias(header, "ts_event"),
        "schema_has_symbol_alias": has_alias(header, "symbol"),
        "schema_has_bid_alias": has_alias(header, "bid"),
        "schema_has_ask_alias": has_alias(header, "ask"),
        "schema_has_ltp_alias": has_alias(header, "ltp"),
        "schema_safe_for_conservative_features_rows": (
            has_alias(header, "ts_event")
            and has_alias(header, "symbol")
            and ((has_alias(header, "bid") and has_alias(header, "ask")) or has_alias(header, "ltp"))
        ),
    }

def reconstruct_rows(quote_files: List[Tuple[str, Path]], target: Path) -> Dict[str, Any]:
    tmp = target.with_name(f".{target.name}.a11_tmp_{utc_stamp()}")
    rows_written = 0
    rows_skipped_schema = 0
    rows_seen = 0
    stream_counts: Dict[str, int] = {}
    try:
        with tmp.open("w", encoding="utf-8", newline="") as out:
            writer = csv.DictWriter(out, fieldnames=OUTPUT_FIELDS, extrasaction="ignore")
            writer.writeheader()
            for source_stream, path in quote_files:
                dialect = detect_dialect(path)
                with path.open("r", encoding="utf-8-sig", newline="") as f:
                    reader = csv.DictReader(f, dialect=dialect)
                    for source_row, row in enumerate(reader, start=2):
                        rows_seen += 1
                        ts_event = pick(row, ALIASES["ts_event"])
                        symbol = pick(row, ALIASES["symbol"])
                        if not ts_event or not symbol:
                            rows_skipped_schema += 1
                            continue

                        bid = to_float(pick(row, ALIASES["bid"]))
                        ask = to_float(pick(row, ALIASES["ask"]))
                        ltp = to_float(pick(row, ALIASES["ltp"]))

                        mid: Optional[float] = None
                        spread: Optional[float] = None
                        if bid is not None and ask is not None:
                            mid = (bid + ask) / 2.0
                            spread = ask - bid
                        elif ltp is not None:
                            mid = ltp

                        provider = pick(row, ALIASES["provider"]) or "mme"
                        instrument_token = pick(row, ALIASES["instrument_token"])
                        side = pick(row, ALIASES["side"])

                        writer.writerow({
                            "ts_event": ts_event,
                            "symbol": symbol,
                            "side": side,
                            "source_stream": source_stream,
                            "bid": fmt_num(bid),
                            "ask": fmt_num(ask),
                            "ltp": fmt_num(ltp),
                            "mid": fmt_num(mid),
                            "spread": fmt_num(spread),
                            "provider": provider,
                            "instrument_token": instrument_token,
                            "source_file": str(path),
                            "source_row": str(source_row),
                        })
                        rows_written += 1
                        stream_counts[source_stream] = stream_counts.get(source_stream, 0) + 1

        if rows_written <= 0:
            try:
                tmp.unlink()
            except FileNotFoundError:
                pass
            return {
                "written": False,
                "target": str(target),
                "row_count": 0,
                "rows_seen": rows_seen,
                "rows_skipped_schema": rows_skipped_schema,
                "stream_counts": stream_counts,
                "reason": "zero_rows_written",
            }

        tmp.replace(target)
        return {
            "written": True,
            "target": str(target),
            "row_count": rows_written,
            "rows_seen": rows_seen,
            "rows_skipped_schema": rows_skipped_schema,
            "stream_counts": stream_counts,
            "sha256": sha256_file(target),
            "columns": OUTPUT_FIELDS,
        }
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except Exception:
                pass

def main() -> int:
    stamp = utc_stamp()
    repo_root = Path.cwd().resolve()
    proof_dir = repo_root / "run" / "proofs"
    audit_dir = repo_root / "run" / "audits"
    milestone_dir = repo_root / "docs" / "milestones"
    proof_dir.mkdir(parents=True, exist_ok=True)
    audit_dir.mkdir(parents=True, exist_ok=True)
    milestone_dir.mkdir(parents=True, exist_ok=True)

    findings: List[Dict[str, str]] = []
    safety = {
        "observe_only": os.environ.get("SCALPX_OBSERVE_ONLY") == "1",
        "paper_or_live_enabled": False,
        "services_started": False,
        "broker_calls_executed": False,
        "login_calls_executed": False,
        "external_api_calls_executed": False,
        "redis_writes_executed": False,
        "orders_sent": False,
        "code_patched": False,
        "engine_execution_performed": False,
        "strategy_decisions_created": False,
        "risk_outputs_created": False,
        "execution_shadow_created": False,
    }

    bad_env = {k: os.environ.get(k) for k in REQUIRED_ENV_FALSEY if os.environ.get(k)}
    if bad_env:
        safety["paper_or_live_enabled"] = True
        findings.append({"severity": "FAIL", "area": "environment", "message": f"paper/live env flags are set: {bad_env}"})

    latest_proof = Path(os.environ.get("LATEST_A10_PROOF", "")).expanduser()
    if not latest_proof.exists():
        raise FileNotFoundError(f"LATEST_A10_PROOF not found: {latest_proof}")

    a10 = json.loads(latest_proof.read_text(encoding="utf-8"))
    a10_summary = a10.get("summary", {})
    canonical_root_raw = a10.get("canonical_root") or a10_summary.get("canonical_root")
    source_date = a10.get("source_date") or a10_summary.get("source_date")
    dataset_id = a10.get("dataset_id") or a10_summary.get("dataset_id")
    a10_pass = (
        a10.get("batch") == "REPLAY-DATA-A10"
        and str(a10_summary.get("overall_verdict", "")).upper() == "PASS"
        and bool(a10_summary.get("selector_plan_ok"))
        and bool(canonical_root_raw)
        and bool(source_date)
    )

    if not a10_pass:
        findings.append({"severity": "FAIL", "area": "a10_proof", "message": "latest proof is not a REPLAY-DATA-A10 PASS selector proof"})

    canonical_root = Path(str(canonical_root_raw))
    if not canonical_root.is_absolute():
        canonical_root = (repo_root / canonical_root).resolve()
    offline_root = (repo_root / "run" / "replay" / "parity" / "offline_materialization").resolve()
    canonical_allowed = canonical_root.exists() and canonical_root.is_dir() and offline_root in canonical_root.parents

    if not canonical_allowed:
        findings.append({"severity": "FAIL", "area": "canonical_root", "message": f"canonical root is not an existing dataset under offline materialization: {canonical_root}"})

    fut_path = find_one(canonical_root, "quote_ticks_mme_fut_stream") if canonical_allowed else None
    opt_path = find_one(canonical_root, "quote_ticks_mme_opt_stream") if canonical_allowed else None
    quote_file_pairs: List[Tuple[str, Path]] = []
    if fut_path:
        quote_file_pairs.append(("fut", fut_path))
    else:
        findings.append({"severity": "FAIL", "area": "quote_feeds", "message": "missing quote_ticks_mme_fut_stream.csv"})
    if opt_path:
        quote_file_pairs.append(("opt", opt_path))
    else:
        findings.append({"severity": "FAIL", "area": "quote_feeds", "message": "missing quote_ticks_mme_opt_stream.csv"})

    quote_summaries = [summarize_csv(path) for _, path in quote_file_pairs]
    all_quote_schema_safe = bool(quote_summaries) and all(q["schema_safe_for_conservative_features_rows"] for q in quote_summaries)
    if not all_quote_schema_safe:
        findings.append({"severity": "FAIL", "area": "quote_schema", "message": "quote feeds do not expose conservative ts_event/symbol/(bid+ask or ltp) aliases"})

    inspect_paths = [
        repo_root / "app" / "mme_scalpx" / "replay" / "dataset.py",
        repo_root / "app" / "mme_scalpx" / "replay" / "contracts.py",
        repo_root / "app" / "mme_scalpx" / "replay" / "reports.py",
        repo_root / "app" / "mme_scalpx" / "services" / "features.py",
        repo_root / "bin" / "replay_run.py",
    ]
    code_inspection = [code_read(p) for p in inspect_paths]
    corpus_mentions = []
    for rec in code_inspection:
        corpus_mentions.extend(rec.get("features_rows_mentions") or [])
        corpus_mentions.extend(rec.get("candidate_name_mentions") or [])

    code_texts = []
    for p in inspect_paths:
        if p.exists() and p.is_file():
            code_texts.append(p.read_text(encoding="utf-8", errors="replace").lower())
    corpus = "\n".join(code_texts)

    features_rows_stem_accepted = "features_rows" in corpus or "feature_rows" in corpus
    features_rows_csv_accepted = "features_rows.csv" in corpus or features_rows_stem_accepted
    features_rows_candidate_accepted = "features_rows_candidate.csv" in corpus

    target_name: Optional[str] = None
    if features_rows_csv_accepted:
        target_name = "features_rows.csv"
    elif features_rows_candidate_accepted:
        target_name = "features_rows_candidate.csv"

    if not target_name:
        findings.append({"severity": "FAIL", "area": "replay_discovery", "message": "features_rows candidate filename is not clearly accepted by inspected replay discovery files"})

    reconstruction = {
        "written": False,
        "target": None,
        "row_count": 0,
        "reason": "not_attempted",
    }

    existing_target = None
    if target_name and canonical_allowed:
        existing_target = canonical_root / target_name

    schema_safe = bool(a10_pass and canonical_allowed and target_name and all_quote_schema_safe and quote_file_pairs)
    if schema_safe and existing_target is not None:
        if existing_target.exists():
            reconstruction = {
                "written": False,
                "target": str(existing_target),
                "row_count": sum(1 for _ in existing_target.open("r", encoding="utf-8", errors="replace")) - 1,
                "reason": "target_already_exists_not_overwritten",
                "sha256": sha256_file(existing_target),
                "columns": read_header(existing_target),
            }
            findings.append({"severity": "INFO", "area": "features_rows", "message": f"existing {target_name} was not overwritten"})
        else:
            reconstruction = reconstruct_rows(quote_file_pairs, existing_target)
            if not reconstruction.get("written"):
                findings.append({"severity": "FAIL", "area": "features_rows", "message": f"candidate reconstruction did not write rows: {reconstruction.get('reason')}"})
    else:
        findings.append({"severity": "FAIL", "area": "features_rows", "message": "schema-safe reconstruction preconditions were not satisfied"})

    selector_required_stems = [
        "quote_ticks_mme_fut_stream",
        "quote_ticks_mme_opt_stream",
    ]
    selector_optional_stems = [
        "ticks_mme_fut_stream",
        "ticks_mme_opt_stream",
        "health_features",
        "source_manifest",
        "reconstruction_todo",
        "quote_transform_manifest",
        "features_rows",
    ]
    selected_date_ok = bool(source_date)
    selector_plan_ok = bool(
        a10_pass
        and canonical_allowed
        and fut_path
        and opt_path
        and selected_date_ok
        and (reconstruction.get("written") or (existing_target is not None and existing_target.exists()))
    )

    if not selector_plan_ok:
        findings.append({"severity": "FAIL", "area": "selector_only_probe", "message": "selector-only plan did not validate required quote feeds plus features_rows candidate availability"})

    fail_count = sum(1 for f in findings if f.get("severity") == "FAIL")
    unclear_count = sum(1 for f in findings if f.get("severity") == "UNCLEAR")
    verdict = "PASS" if fail_count == 0 and selector_plan_ok else "BLOCKED"

    proof = {
        "batch": BATCH,
        "title": TITLE,
        "created_at": stamp,
        "latest_a10_proof": str(latest_proof),
        "canonical_root": str(canonical_root.relative_to(repo_root)) if canonical_allowed else str(canonical_root),
        "source_date": source_date,
        "dataset_id": dataset_id,
        "summary": {
            "features_rows_candidate_written": bool(reconstruction.get("written")),
            "features_rows_target": reconstruction.get("target"),
            "row_count": int(reconstruction.get("row_count") or 0),
            "selector_plan_ok": selector_plan_ok,
            "engine_ready": False,
            "next_batch": NEXT_BATCH,
            "overall_verdict": verdict,
            "fail_count": fail_count,
            "unclear_count": unclear_count,
        },
        "a10_validation": {
            "a10_pass": a10_pass,
            "a10_batch": a10.get("batch"),
            "a10_verdict": a10_summary.get("overall_verdict"),
            "a10_selector_plan_ok": a10_summary.get("selector_plan_ok"),
        },
        "quote_feed_inspection": quote_summaries,
        "code_inspection": code_inspection,
        "replay_discovery": {
            "features_rows_stem_accepted": features_rows_stem_accepted,
            "features_rows_csv_accepted": features_rows_csv_accepted,
            "features_rows_candidate_csv_accepted": features_rows_candidate_accepted,
            "selected_target_name": target_name,
            "inspected_read_only": [str(p) for p in inspect_paths],
        },
        "reconstruction": reconstruction,
        "selector_only_probe": {
            "performed_without_engine_execution": True,
            "dataset_root": str(offline_root.relative_to(repo_root)),
            "dataset_id": dataset_id,
            "source_date": source_date,
            "required_file_stems": selector_required_stems,
            "optional_file_stems": selector_optional_stems,
            "selected_dates": [source_date] if source_date else [],
            "selector_plan_ok": selector_plan_ok,
        },
        "findings": findings,
        "safety": safety,
    }

    proof_path = proof_dir / f"proof_replay_data_a11_features_rows_reconstruction_{stamp}.json"
    proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    audit_path = audit_dir / f"audit_replay_data_a11_features_rows_reconstruction_{stamp}.json"
    audit_path.write_text(json.dumps({
        "batch": BATCH,
        "proof_path": str(proof_path),
        "canonical_root": proof["canonical_root"],
        "source_date": source_date,
        "safety": safety,
        "selector_plan_ok": selector_plan_ok,
        "engine_execution_performed": False,
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    milestone_path = milestone_dir / f"replay_data_a11_features_rows_reconstruction_{stamp}.md"
    milestone_path.write_text(
        "\n".join([
            f"# {BATCH} — features_rows reconstruction",
            "",
            f"- proof: `{proof_path}`",
            f"- canonical_root: `{proof['canonical_root']}`",
            f"- source_date: `{source_date}`",
            f"- features_rows_candidate_written: {str(bool(reconstruction.get('written'))).lower()}",
            f"- row_count: {int(reconstruction.get('row_count') or 0)}",
            f"- selector_plan_ok: {str(selector_plan_ok).lower()}",
            "- engine_ready: false",
            f"- next_batch: {NEXT_BATCH}",
            "",
            "Safety: selector-only validation; no replay engine execution; no strategy_decisions/risk_outputs/execution_shadow creation.",
            "",
        ]) + "\n",
        encoding="utf-8",
    )

    final_summary = {
        "features_rows_candidate_written": bool(reconstruction.get("written")),
        "row_count": int(reconstruction.get("row_count") or 0),
        "selector_plan_ok": selector_plan_ok,
        "engine_ready": False,
        "next_batch": NEXT_BATCH,
        "proof_path": str(proof_path),
        "milestone_path": str(milestone_path),
        "verdict": verdict,
    }
    print(json.dumps(final_summary, indent=2, sort_keys=True))
    return 0 if verdict == "PASS" else 2

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        stamp = utc_stamp()
        repo_root = Path.cwd().resolve()
        proof_dir = repo_root / "run" / "proofs"
        milestone_dir = repo_root / "docs" / "milestones"
        proof_dir.mkdir(parents=True, exist_ok=True)
        milestone_dir.mkdir(parents=True, exist_ok=True)
        err = {
            "batch": BATCH,
            "title": TITLE,
            "created_at": stamp,
            "summary": {
                "features_rows_candidate_written": False,
                "row_count": 0,
                "selector_plan_ok": False,
                "engine_ready": False,
                "next_batch": NEXT_BATCH,
                "overall_verdict": "ERROR",
            },
            "error": str(exc),
            "traceback": traceback.format_exc(),
            "safety": {
                "observe_only": os.environ.get("SCALPX_OBSERVE_ONLY") == "1",
                "paper_or_live_enabled": False,
                "services_started": False,
                "broker_calls_executed": False,
                "login_calls_executed": False,
                "external_api_calls_executed": False,
                "redis_writes_executed": False,
                "orders_sent": False,
                "code_patched": False,
                "engine_execution_performed": False,
            },
        }
        proof_path = proof_dir / f"proof_replay_data_a11_features_rows_reconstruction_{stamp}.json"
        proof_path.write_text(json.dumps(err, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        milestone_path = milestone_dir / f"replay_data_a11_features_rows_reconstruction_{stamp}.md"
        milestone_path.write_text(
            "\n".join([
                f"# {BATCH} — features_rows reconstruction ERROR",
                "",
                f"- proof: `{proof_path}`",
                "- features_rows_candidate_written: false",
                "- row_count: 0",
                "- selector_plan_ok: false",
                "- engine_ready: false",
                f"- next_batch: {NEXT_BATCH}",
                "",
            ]) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(err["summary"], indent=2, sort_keys=True), file=sys.stderr)
        raise SystemExit(1)
PY
.venv/bin/python /tmp/replay_data_a11_features_rows_reconstruction.py
