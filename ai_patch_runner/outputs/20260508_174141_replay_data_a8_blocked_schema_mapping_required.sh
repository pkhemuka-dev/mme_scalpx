set -Eeuo pipefail
cd /home/Lenovo/scalpx/projects/mme_scalpx
export SCALPX_OBSERVE_ONLY=1
unset SCALPX_LIVE SCALPX_LIVE_TRADING SCALPX_ENABLE_LIVE SCALPX_ENABLE_PAPER SCALPX_PAPER SCALPX_PAPER_TRADING LIVE_TRADING PAPER_TRADING ENABLE_LIVE ENABLE_PAPER TRADING_MODE ORDER_PLACEMENT_ENABLED
cat > /tmp/replay_data_a8_quote_schema_mapping.py <<'PY'
import csv
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

BATCH = "REPLAY-DATA-A8"
TITLE = "quote_only_recorded schema mapping audit"
REPO = Path.cwd()
A7_PROOF = Path("/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/proof_replay_data_a7_sandbox_canonical_day_dataset_20260508T173739Z.json")

def utc_stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def read_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def safe_rel(path):
    try:
        return str(Path(path).resolve().relative_to(REPO.resolve()))
    except Exception:
        return str(path)

def normalize_col(name):
    return re.sub(r"[^a-z0-9]+", "", str(name).strip().lower())

def truncate_value(v, limit=160):
    if v is None:
        return None
    s = str(v)
    if len(s) > limit:
        return s[:limit] + "...<truncated>"
    return s

def inspect_csv(path, sample_limit=8):
    info = {
        "path": safe_rel(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else None,
        "headers": [],
        "normalized_headers": {},
        "sample_rows": [],
        "sample_non_empty_counts": {},
        "read_error": None,
    }
    if not path.exists():
        info["read_error"] = "file_missing"
        return info
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            info["headers"] = list(reader.fieldnames or [])
            info["normalized_headers"] = {h: normalize_col(h) for h in info["headers"]}
            counts = {h: 0 for h in info["headers"]}
            for idx, row in enumerate(reader):
                if idx >= sample_limit:
                    break
                clean = {h: truncate_value(row.get(h)) for h in info["headers"]}
                info["sample_rows"].append(clean)
                for h in info["headers"]:
                    val = row.get(h)
                    if val is not None and str(val).strip() != "":
                        counts[h] += 1
            info["sample_non_empty_counts"] = counts
    except Exception as exc:
        info["read_error"] = repr(exc)
    return info

TARGET_SYNONYMS = {
    "ts_event": [
        "tsevent", "eventts", "eventtime", "timestamp", "ts", "time", "datetime", "date_time",
        "exchangetimestamp", "exchangets", "exchtime", "exchange_time", "receivedts", "recvts",
        "recordedts", "recordedtime", "ticktime", "ticktimestamp", "updatetime", "update_time"
    ],
    "symbol": [
        "symbol", "tradingsymbol", "trading_symbol", "instrument", "instrumentname", "contract",
        "ticker", "security", "name", "scrip", "token_symbol"
    ],
    "bid": [
        "bid", "bidprice", "bestbid", "bestbidprice", "bidpx", "bid_px", "buyprice", "buy_price",
        "bprice", "bp", "bid1", "bidprice1", "buyprice1", "level1bid", "level1bidprice"
    ],
    "ask": [
        "ask", "askprice", "bestask", "bestaskprice", "askpx", "ask_px", "offer", "offerprice",
        "sellprice", "sell_price", "ap", "ask1", "askprice1", "sellprice1", "level1ask",
        "level1askprice"
    ],
    "ltp": [
        "ltp", "last", "lastprice", "lasttradedprice", "last_traded_price", "tradedprice",
        "price", "close", "lastpx", "last_px"
    ],
    "last": [
        "last", "lastprice", "lasttradedprice", "ltp", "price", "lastpx", "last_px"
    ],
    "price": [
        "price", "ltp", "last", "lastprice", "lasttradedprice", "tradedprice"
    ],
    "bid_qty": [
        "bidqty", "bidquantity", "bestbidqty", "bestbidquantity", "bidq", "bid_qty",
        "buyqty", "buyquantity", "bqty", "bid1qty", "bidquantity1"
    ],
    "ask_qty": [
        "askqty", "askquantity", "bestaskqty", "bestaskquantity", "askq", "ask_qty",
        "sellqty", "sellquantity", "aqty", "ask1qty", "askquantity1", "offerqty"
    ],
    "volume": [
        "volume", "vol", "tradedvolume", "totaltradedvolume", "dayvolume", "cumvolume",
        "cumulativevolume", "qty", "quantity"
    ],
    "oi": [
        "oi", "openinterest", "open_interest"
    ],
    "provider": [
        "provider", "source", "datasource", "feed", "feedprovider", "vendor"
    ],
    "instrument_token": [
        "instrumenttoken", "instrument_token", "token", "instrumentid", "instrument_id",
        "securityid", "security_id", "exchange_token", "exchangetoken"
    ],
}

REQUIRED_FIELDS = ["ts_event", "symbol", "bid", "ask"]
OPTIONAL_FIELDS = ["ltp", "last", "price", "bid_qty", "ask_qty", "volume", "oi", "provider", "instrument_token"]

def find_mapping(headers):
    normalized_to_headers = {}
    for h in headers:
        normalized_to_headers.setdefault(normalize_col(h), []).append(h)
    plan = {}
    for target, synonyms in TARGET_SYNONYMS.items():
        candidates = []
        normalized_synonyms = [normalize_col(s) for s in synonyms]
        for syn in normalized_synonyms:
            for h in normalized_to_headers.get(syn, []):
                candidates.append({
                    "column": h,
                    "match_type": "exact_normalized_synonym",
                    "matched_synonym": syn,
                    "confidence": "high",
                })
        if not candidates:
            for h in headers:
                nh = normalize_col(h)
                for syn in normalized_synonyms:
                    if syn and (nh.endswith(syn) or nh.startswith(syn)):
                        candidates.append({
                            "column": h,
                            "match_type": "prefix_or_suffix_normalized_synonym",
                            "matched_synonym": syn,
                            "confidence": "medium",
                        })
                        break
        if not candidates:
            for h in headers:
                nh = normalize_col(h)
                for syn in normalized_synonyms:
                    if len(syn) >= 4 and syn in nh:
                        candidates.append({
                            "column": h,
                            "match_type": "contains_normalized_synonym",
                            "matched_synonym": syn,
                            "confidence": "low",
                        })
                        break
        chosen = candidates[0]["column"] if candidates else None
        plan[target] = {
            "mapped": chosen is not None,
            "chosen_column": chosen,
            "candidates": candidates,
        }
    return plan

def inspect_quote_source():
    source_roots = ["bin", "scripts", "tools", "tests", "app", "services", "integrations", "replay", "src"]
    suffixes = {".py", ".md", ".txt", ".yaml", ".yml", ".json", ".toml"}
    skip_parts = {".git", ".venv", "__pycache__", ".pytest_cache", "run", "data", "logs"}
    occurrences = []
    required_from_source = []
    for root_name in source_roots:
        root = REPO / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in suffixes:
                continue
            if any(part in skip_parts for part in path.parts):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            if "quote_only_recorded" not in text:
                continue
            lines = text.splitlines()
            for i, line in enumerate(lines):
                if "quote_only_recorded" in line:
                    start = max(0, i - 12)
                    end = min(len(lines), i + 18)
                    context = "\n".join(lines[start:end])
                    occurrences.append({
                        "path": safe_rel(path),
                        "line": i + 1,
                        "text": line.strip()[:240],
                        "context": context[:4000],
                    })
                    for field in REQUIRED_FIELDS:
                        if re.search(r"['\"]" + re.escape(field) + r"['\"]", context):
                            if field not in required_from_source:
                                required_from_source.append(field)
    return {
        "occurrence_count": len(occurrences),
        "occurrences": occurrences[:20],
        "required_fields_detected_in_source_context": required_from_source,
    }

def source_required_fields(source_scan, a7):
    detected = source_scan.get("required_fields_detected_in_source_context") or []
    if all(f in detected for f in REQUIRED_FIELDS):
        return REQUIRED_FIELDS
    selector_error = str(((a7.get("selector_probe") or {}).get("selector_error")) or "")
    fallback = []
    for f in REQUIRED_FIELDS:
        if f in selector_error:
            fallback.append(f)
    if all(f in fallback for f in REQUIRED_FIELDS):
        return REQUIRED_FIELDS
    return REQUIRED_FIELDS

def main():
    if not A7_PROOF.exists():
        raise SystemExit(f"A7 proof missing: {A7_PROOF}")
    a7 = read_json(A7_PROOF)
    canonical_root_value = (
        (a7.get("selector_probe") or {}).get("repo_root")
        or a7.get("canonical_root")
        or (a7.get("summary") or {}).get("canonical_root")
    )
    if not canonical_root_value:
        raise SystemExit("canonical_root not found in A7 proof")
    canonical_root = Path(canonical_root_value)
    if not canonical_root.is_absolute():
        canonical_root = REPO / canonical_root

    fut_path = canonical_root / "ticks_mme_fut_stream.csv"
    opt_path = canonical_root / "ticks_mme_opt_stream.csv"

    csv_inspections = {
        "ticks_mme_fut_stream": inspect_csv(fut_path),
        "ticks_mme_opt_stream": inspect_csv(opt_path),
    }

    source_scan = inspect_quote_source()
    required_fields = source_required_fields(source_scan, a7)

    per_file_mapping = {}
    missing_required_by_file = {}
    for stem, info in csv_inspections.items():
        mapping = find_mapping(info.get("headers") or [])
        per_file_mapping[stem] = {
            "required": {k: mapping[k] for k in REQUIRED_FIELDS},
            "optional": {k: mapping[k] for k in OPTIONAL_FIELDS},
            "all_required_mapped": all(mapping[k]["mapped"] for k in REQUIRED_FIELDS),
        }
        missing_required_by_file[stem] = [
            k for k in REQUIRED_FIELDS if not mapping[k]["mapped"]
        ]

    adapter_mapping_possible = (
        canonical_root.exists()
        and all(info.get("exists") for info in csv_inspections.values())
        and all(per_file_mapping[stem]["all_required_mapped"] for stem in per_file_mapping)
    )
    missing_required_union = sorted({f for vals in missing_required_by_file.values() for f in vals})

    verdict = "PASS_MAPPING_POSSIBLE" if adapter_mapping_possible else "BLOCKED_MISSING_REQUIRED_FIELDS"

    stamp = utc_stamp()
    proof_dir = REPO / "run" / "proofs"
    milestone_dir = REPO / "docs" / "milestones"
    proof_dir.mkdir(parents=True, exist_ok=True)
    milestone_dir.mkdir(parents=True, exist_ok=True)
    proof_path = proof_dir / f"proof_replay_data_a8_quote_schema_mapping_{stamp}.json"
    milestone_path = milestone_dir / f"replay_data_a8_quote_schema_mapping_{stamp}.md"

    proof = {
        "batch": BATCH,
        "title": TITLE,
        "created_at_utc": stamp,
        "repo_root": str(REPO),
        "input_proof": str(A7_PROOF),
        "canonical_root": str(canonical_root),
        "source_date": a7.get("source_date") or (a7.get("selector_probe") or {}).get("source_date"),
        "observe_only": os.environ.get("SCALPX_OBSERVE_ONLY") == "1",
        "actions_performed": [
            "read_latest_REPLAY_DATA_A7_proof",
            "inspected_canonical_dataset_root",
            "inspected_tick_csv_headers_and_sample_rows",
            "searched_replay_source_text_for_quote_only_recorded_required_fields",
            "produced_schema_adapter_plan_only",
        ],
        "actions_not_performed": [
            "no_data_transformation",
            "no_replay_engine_run",
            "no_replay_code_patch",
            "no_bin_replay_run_patch",
            "no_trading_code_mutation",
            "no_live_data_mutation",
            "no_order_placement",
        ],
        "source_scan": source_scan,
        "quote_only_recorded_required_fields": required_fields,
        "quote_only_recorded_optional_fields_considered": OPTIONAL_FIELDS,
        "csv_inspections": csv_inspections,
        "schema_adapter_plan": {
            "plan_type": "audit_only_no_transform",
            "target_source_mode": "quote_only_recorded",
            "required_targets": REQUIRED_FIELDS,
            "optional_targets": OPTIONAL_FIELDS,
            "per_file_mapping": per_file_mapping,
            "adapter_mapping_possible": adapter_mapping_possible,
            "missing_required_by_file": missing_required_by_file,
            "missing_required_union": missing_required_union,
            "implementation_note": "If approved in a later batch, add a read-only adapter/reconstruction step that renames mapped source columns to ts_event,symbol,bid,ask and carries optional mapped columns without changing raw exports.",
        },
        "summary": {
            "verdict": verdict,
            "adapter_mapping_possible": adapter_mapping_possible,
            "missing_required_fields": missing_required_union,
            "missing_required_by_file": missing_required_by_file,
            "canonical_root_exists": canonical_root.exists(),
            "files_checked": list(csv_inspections.keys()),
        },
        "safety": {
            "services_started": False,
            "paper_or_live_enabled": False,
            "orders_sent": False,
            "broker_calls_executed": False,
            "live_redis_writes_executed": False,
            "engine_execution_performed": False,
            "trading_code_patched": False,
            "raw_data_mutated": False,
        },
    }

    proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    md_lines = [
        f"# {BATCH} — {TITLE}",
        "",
        f"- Created UTC: `{stamp}`",
        f"- Input A7 proof: `{A7_PROOF}`",
        f"- Canonical root: `{canonical_root}`",
        f"- Verdict: `{verdict}`",
        f"- Adapter mapping possible: `{adapter_mapping_possible}`",
        f"- Missing required fields: `{', '.join(missing_required_union) if missing_required_union else 'none'}`",
        "",
        "## Required quote_only_recorded fields",
        "",
        ", ".join(required_fields),
        "",
        "## Per-file missing required fields",
        "",
    ]
    for stem, missing in missing_required_by_file.items():
        md_lines.append(f"- `{stem}`: `{', '.join(missing) if missing else 'none'}`")
    md_lines.extend([
        "",
        "## Mapping plan",
        "",
    ])
    for stem, mapping_info in per_file_mapping.items():
        md_lines.append(f"### {stem}")
        for field in REQUIRED_FIELDS + OPTIONAL_FIELDS:
            group = "required" if field in REQUIRED_FIELDS else "optional"
            entry = mapping_info[group][field]
            md_lines.append(f"- `{field}` -> `{entry['chosen_column'] if entry['chosen_column'] else 'UNMAPPED'}`")
        md_lines.append("")
    md_lines.extend([
        "## Safety",
        "",
        "- Audit only.",
        "- No data transformation.",
        "- No replay engine run.",
        "- No replay code patch.",
        "- No order placement or paper/live enablement.",
        "",
        f"Proof JSON: `{proof_path}`",
        "",
    ])
    milestone_path.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"{BATCH} summary: adapter_mapping_possible={adapter_mapping_possible}; missing_required_fields={missing_required_union if missing_required_union else []}; proof={proof_path}; milestone={milestone_path}")

if __name__ == "__main__":
    main()
PY
.venv/bin/python /tmp/replay_data_a8_quote_schema_mapping.py
