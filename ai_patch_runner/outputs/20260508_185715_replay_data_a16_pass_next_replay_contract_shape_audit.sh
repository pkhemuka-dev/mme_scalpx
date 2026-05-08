export SCALPX_OBSERVE_ONLY=1
unset SCALPX_PAPER || true
unset SCALPX_LIVE || true
unset SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME || true
unset SCALPX_REAL_LIVE_ALLOWED || true
.venv/bin/python - <<'PY'
import os, json, re, sys, datetime

# Inputs (latest proof)
latest_proof_path = "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/proof_replay_data_a15_selector_surface_probe_20260508T185521Z.json"

# Targets to audit
expected_files = [
    "quote_ticks_mme_fut_stream.csv",
    "quote_ticks_mme_opt_stream.csv",
    "features_rows_candidate.csv",
    "strategy_decisions_candidate.csv",
    "risk_outputs_candidate.csv",
    "execution_shadow_candidate.csv",
]

# Read latest proof
try:
    with open(latest_proof_path, "r") as f:
        proof = json.load(f)
except Exception as e:
    print("ERROR: cannot read latest proof:", e, file=sys.stderr)
    sys.exit(2)

canonical_root = proof.get("canonical_root") or proof.get("summary", {}).get("canonical_root") or ""
source_date = proof.get("source_date") or proof.get("summary", {}).get("source_date") or ""
if not canonical_root or not source_date:
    print("ERROR: canonical_root or source_date missing in proof JSON", file=sys.stderr)
    sys.exit(3)

date_dir = os.path.join(canonical_root, source_date)
# Normalize path relative to project root if needed
date_dir = os.path.normpath(date_dir)

# Read replay contract/source hints
contract_files = [
    "app/mme_scalpx/replay/dataset.py",
    "app/mme_scalpx/replay/contracts.py",
    "bin/replay_run.py",
]
contract_text = ""
for p in contract_files:
    try:
        with open(p, "r", encoding="utf-8") as f:
            contract_text += "\n\n### FILE: " + p + "\n" + f.read()
    except FileNotFoundError:
        # allowed to be missing; continue
        pass
    except Exception:
        pass

# Heuristics: extract accepted stems from contract_text: any csv-like token occurrences
accepted_file_stems = set()
for m in re.finditer(r"([a-zA-Z0-9_]+\.csv)", contract_text):
    accepted_file_stems.add(m.group(1))

# If contract files didn't list any, fall back to expected_files as accepted stems
if not accepted_file_stems:
    accepted_file_stems = set(expected_files)

# Attempt to extract expected header strings from contracts/dataset text using heuristics
expected_headers_map = {}  # filename -> expected header string (comma-separated)
# Patterns: "filename.csv": "col1,col2,..." or filename_HEADER = "a,b,c"
for fn in list(accepted_file_stems):
    # look for mapping "filename.csv" : "a,b,c"
    pat1 = re.compile(r"['\"]" + re.escape(fn) + r"['\"]\s*[:=]\s*['\"]([^'\"]+)['\"]")
    m1 = pat1.search(contract_text)
    if m1:
        expected_headers_map[fn] = m1.group(1).strip()
        continue
    # look for var like FILENAME_HEADERS = "a,b,c" where FILENAME contains stem
    name_no_ext = fn.replace(".csv", "")
    pat2 = re.compile(re.escape(name_no_ext) + r".{0,30}=\s*['\"]([^'\"]+)['\"]", re.IGNORECASE)
    m2 = pat2.search(contract_text)
    if m2:
        expected_headers_map[fn] = m2.group(1).strip()
        continue
    # look for header lists: ['a','b'] or ("a","b")
    pat3 = re.compile(r"['\"]" + re.escape(name_no_ext) + r"['\"]\s*:\s*\[\s*([^\]]+)\]", re.IGNORECASE)
    m3 = pat3.search(contract_text)
    if m3:
        # extract items
        items = re.findall(r"['\"]([^'\"]+)['\"]", m3.group(1))
        if items:
            expected_headers_map[fn] = ",".join(items)
            continue

# Prepare per-file report
file_reports = []
missing_expected = []
incompatible = []

for fn in expected_files:
    path = os.path.join(date_dir, fn)
    report = {"filename": fn, "path": path, "exists": False, "header": None, "row_count": 0, "sample_rows": []}
    if os.path.exists(path):
        report["exists"] = True
        try:
            with open(path, "r", encoding="utf-8") as f:
                # read header line (first non-empty)
                header = None
                sample = []
                for line in f:
                    if header is None:
                        if line.strip() == "":
                            continue
                        header = line.rstrip("\n")
                        continue
                    if len(sample) < 5:
                        sample.append(line.rstrip("\n"))
                report["header"] = header or ""
            # count rows excluding header
            row_count = 0
            with open(path, "r", encoding="utf-8") as f:
                first = True
                for line in f:
                    if first:
                        first = False
                        continue
                    row_count += 1 if line.strip() != "" else 0
            report["row_count"] = row_count
            report["sample_rows"] = sample
        except Exception as e:
            report["error"] = str(e)
    else:
        missing_expected.append(fn)
    # Compare header with expected if we have expected header for this filename
    if report["exists"]:
        expected_header = expected_headers_map.get(fn)
        if expected_header:
            # compare sets of column names (split by comma and strip)
            actual_cols = [c.strip() for c in (report["header"] or "").split(",") if c.strip()]
            expected_cols = [c.strip() for c in expected_header.split(",") if c.strip()]
            if actual_cols != expected_cols:
                incompatible.append({
                    "filename": fn,
                    "expected_header": expected_header,
                    "actual_header": report["header"],
                    "expected_cols": expected_cols,
                    "actual_cols": actual_cols
                })
    file_reports.append(report)

contract_shape_ok = (len(missing_expected) == 0 and len(incompatible) == 0)

# Compose proof JSON
now = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
proof_out = {
    "batch": "REPLAY-DATA-A16",
    "timestamp_utc": now,
    "title": "replay dataset contract/shape compatibility audit",
    "canonical_root": canonical_root,
    "source_date": source_date,
    "date_dir": date_dir,
    "accepted_file_stems": sorted(list(accepted_file_stems)),
    "expected_files_checked": expected_files,
    "file_reports": file_reports,
    "missing_expected_surfaces": missing_expected,
    "incompatible_surfaces": incompatible,
    "contract_shape_ok": contract_shape_ok,
    "engine_ready_candidate": False,
    "next_batch": "REPLAY-DATA-A17",
    "notes": "Automated conservative audit. No replay engine executed. SCALPX_OBSERVE_ONLY enforced in runtime env."
}

os.makedirs("run/proofs", exist_ok=True)
proof_filename = os.path.join("run/proofs", f"proof_replay_data_a16_contract_shape_audit_{now}.json")
with open(proof_filename, "w", encoding="utf-8") as f:
    json.dump(proof_out, f, indent=2, sort_keys=True)

# Write milestone markdown
os.makedirs("docs/milestones", exist_ok=True)
md_lines = []
md_lines.append(f"# REPLAY-DATA-A16 — contract/shape compatibility audit")
md_lines.append("")
md_lines.append(f"- timestamp_utc: {now}")
md_lines.append(f"- canonical_root: {canonical_root}")
md_lines.append(f"- source_date: {source_date}")
md_lines.append(f"- date_dir: {date_dir}")
md_lines.append(f"- contract_shape_ok: {contract_shape_ok}")
md_lines.append(f"- engine_ready_candidate: False")
md_lines.append(f"- next_batch: REPLAY-DATA-A17")
md_lines.append("")
md_lines.append("## Accepted file stems discovered in replay code (heuristic)")
for s in sorted(list(accepted_file_stems)):
    md_lines.append(f"- {s}")
md_lines.append("")
md_lines.append("## Missing expected surfaces")
if missing_expected:
    for s in missing_expected:
        md_lines.append(f"- {s}")
else:
    md_lines.append("- none")
md_lines.append("")
md_lines.append("## Incompatible surfaces (header mismatch)")
if incompatible:
    for it in incompatible:
        md_lines.append(f"- {it['filename']}")
        md_lines.append(f"  - expected_header: {it['expected_header']}")
        md_lines.append(f"  - actual_header: {it['actual_header']}")
else:
    md_lines.append("- none detected (or expected header not available for comparison)")
md_lines.append("")
md_lines.append("## Per-file quick report")
for r in file_reports:
    md_lines.append(f"- {r['filename']}: exists={r['exists']}, row_count={r.get('row_count')}, header={r.get('header')!r}")
md_lines.append("")
md_lines.append("## Notes")
md_lines.append("- This audit did not run the replay engine nor start any services.")
md_lines.append("- SCALPX_OBSERVE_ONLY was set for the runtime of this package.")
md_lines.append("- If contract_shape_ok == True then candidate surfaces match expectations; proceed with caution to the next batch.")
md_text = "\n".join(md_lines)

md_filename = os.path.join("docs/milestones", f"replay_data_a16_contract_shape_audit_{now}.md")
with open(md_filename, "w", encoding="utf-8") as f:
    f.write(md_text)

# Also write a compact audit summary to run/audits
os.makedirs("run/audits", exist_ok=True)
audit_summary = {
    "proof_path_written": proof_filename,
    "md_path_written": md_filename,
    "contract_shape_ok": contract_shape_ok,
    "missing_expected_surfaces": missing_expected,
    "incompatible_surfaces_count": len(incompatible),
    "engine_ready_candidate": False,
    "next_batch": "REPLAY-DATA-A17",
    "timestamp_utc": now
}
with open(os.path.join("run/audits", f"replay_data_a16_contract_shape_audit_{now}.json"), "w", encoding="utf-8") as f:
    json.dump(audit_summary, f, indent=2)

# Print short summary to stdout for operator
print(json.dumps({
    "proof_written": proof_filename,
    "md_written": md_filename,
    "contract_shape_ok": contract_shape_ok,
    "accepted_file_stems": sorted(list(accepted_file_stems)),
    "missing_expected_surfaces": missing_expected,
    "incompatible_surfaces": incompatible,
    "engine_ready_candidate": False,
    "next_batch": "REPLAY-DATA-A17"
}, indent=2))

PY

# MAUTO-R2.5 local static-validation safety annotations only
# engine_execution_performed=false
# broker_calls_executed=false
# live_redis_writes_executed=false
# paper_or_live_enabled=false
# orders_sent=false
