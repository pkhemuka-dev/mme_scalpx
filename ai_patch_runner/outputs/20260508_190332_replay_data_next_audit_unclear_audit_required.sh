SCALPX_OBSERVE_ONLY=1 env -u SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME -u SCALPX_REAL_LIVE_ALLOWED .venv/bin/python - <<'PY'
import os, json, csv, re
from pathlib import Path
from datetime import datetime

# Inputs (from user)
latest_proof_path = Path("/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/proof_replay_data_a16_contract_shape_audit_20260508T190013Z.json")

# Outputs
ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
proof_out_dir = Path("run/proofs")
md_out_dir = Path("docs/milestones")
proof_out_dir.mkdir(parents=True, exist_ok=True)
md_out_dir.mkdir(parents=True, exist_ok=True)

proof_filename = proof_out_dir / f"proof_replay_data_next_audit_{ts}.json"
md_filename = md_out_dir / f"replay_data_next_audit_{ts}.md"

# Allowed candidate surfaces to inspect
expected_surfaces = [
    "quote_ticks_mme_fut_stream.csv",
    "quote_ticks_mme_opt_stream.csv",
    "features_rows_candidate.csv",
    "strategy_decisions_candidate.csv",
    "risk_outputs_candidate.csv",
    "execution_shadow_candidate.csv",
]

# Blocker categories
blocker_categories = [
    "dataset_layout_blocker",
    "selector_contract_blocker",
    "schema_header_blocker",
    "engine_input_blocker",
    "artifact_manifest_blocker",
    "candidate_surface_quality_blocker",
    "unknown_blocker"
]

def safe_load_json(p: Path):
    try:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"_load_error": str(e)}

# Read latest proof to obtain canonical_root and source_date if present
latest_proof = safe_load_json(latest_proof_path) if latest_proof_path.exists() else {"_missing_proof": True}
canonical_root = latest_proof.get("canonical_root") or latest_proof.get("summary", {}).get("canonical_root") or latest_proof.get("canonical_root_path")
source_date = latest_proof.get("source_date") or latest_proof.get("summary", {}).get("source_date")

# Defensive resolution of canonical root
canonical_dir = Path(canonical_root) if canonical_root else None
if canonical_dir and not canonical_dir.exists():
    # try relative to project root
    alt = Path("run/replay/parity/offline_materialization") / canonical_dir.name if canonical_dir else None
    if alt and alt.exists():
        canonical_dir = alt

found_surfaces = {}
headers = {}
row_counts = {}
read_errors = {}

# Search locations to look for candidate surfaces
candidate_search_paths = []
if canonical_dir:
    candidate_search_paths.append(canonical_dir)
    if source_date:
        candidate_search_paths.append(canonical_dir / source_date)
candidate_search_paths.append(Path("run/replay/parity/offline_materialization"))
candidate_search_paths.append(Path("."))

# gather files
for surf in expected_surfaces:
    found = None
    for root in candidate_search_paths:
        p = root / surf
        if p.exists():
            found = p
            break
    if found:
        found_surfaces[surf] = str(found)
        # attempt to read header and small row count sample safely
        try:
            with found.open("r", encoding="utf-8", errors="replace") as f:
                rdr = csv.reader(f)
                first = next(rdr, None)
                headers[surf] = first if first is not None else []
                # count up to 5 rows to estimate quality
                cnt = 0
                for _ in range(5):
                    r = next(rdr, None)
                    if r is None:
                        break
                    cnt += 1
                row_counts[surf] = cnt
        except Exception as e:
            read_errors[surf] = str(e)
    else:
        found_surfaces[surf] = None

# Inspect replay python contract files lightly (read-only)
repo_files = [
    Path("app/mme_scalpx/replay/dataset.py"),
    Path("app/mme_scalpx/replay/contracts.py"),
    Path("app/mme_scalpx/replay/selectors.py"),
    Path("app/mme_scalpx/replay/engine.py"),
    Path("app/mme_scalpx/replay/runner.py"),
    Path("bin/replay_run.py"),
]
repo_contents = {}
for rf in repo_files:
    try:
        repo_contents[str(rf)] = rf.read_text(encoding="utf-8")
    except Exception as e:
        repo_contents[str(rf)] = f"<unreadable: {e}>"

# Heuristic: discover accepted stems in contracts.py by searching for common stems
accepted_stems = set()
contracts_text = repo_contents.get("app/mme_scalpx/replay/contracts.py","")
for stem in expected_surfaces:
    name = stem.replace(".csv","")
    if re.search(re.escape(name), contracts_text):
        accepted_stems.add(stem)

# Classify blockers
blockers = []

# artifact_manifest_blocker: missing canonical_root or proof lacking canonical_root
if not canonical_root:
    blockers.append({
        "type": "artifact_manifest_blocker",
        "reason": "latest proof missing canonical_root/source_date",
        "evidence": {"latest_proof_path": str(latest_proof_path), "latest_proof_contents_snippet": (str(latest_proof)[:400])}
    })

# dataset_layout_blocker: canonical dir absent or none of expected surfaces present under it
if canonical_dir is None or not canonical_dir.exists():
    blockers.append({
        "type": "dataset_layout_blocker",
        "reason": "canonical_root directory not found or inaccessible",
        "evidence": {"canonical_root": canonical_root}
    })
else:
    any_present = any(v for v in found_surfaces.values())
    if not any_present:
        blockers.append({
            "type": "dataset_layout_blocker",
            "reason": "no expected candidate surfaces found under canonical_root or search paths",
            "evidence": {"searched_paths": [str(p) for p in candidate_search_paths]}
        })

# engine_input_blocker: any mandatory surface missing
missing_required = [s for s, p in found_surfaces.items() if p is None]
if missing_required:
    blockers.append({
        "type": "engine_input_blocker",
        "reason": "missing required replay input surfaces",
        "evidence": {"missing_surfaces": missing_required}
    })

# selector_contract_blocker: surfaces present but contracts.py does not mention matching stems
if any(found_surfaces[s] for s in expected_surfaces):
    if accepted_stems:
        # check if all present files are accepted
        unaccepted = [s for s, p in found_surfaces.items() if p and s not in accepted_stems]
        if unaccepted:
            blockers.append({
                "type": "selector_contract_blocker",
                "reason": "some present candidate surfaces do not match accepted stems discovered in contracts.py",
                "evidence": {"unaccepted_surfaces": unaccepted, "accepted_stems_sample": list(accepted_stems)[:10]}
            })
    else:
        blockers.append({
            "type": "selector_contract_blocker",
            "reason": "no accepted stems discovered in contracts.py (heuristic); cannot confirm selector contract compatibility",
            "evidence": {"contracts_path": "app/mme_scalpx/replay/contracts.py"}
        })

# schema_header_blocker: present files with empty/no headers or obviously malformed header
bad_headers = {}
for s,p in found_surfaces.items():
    if p:
        h = headers.get(s)
        if not h:
            bad_headers[s] = "missing_or_empty_header"
        else:
            # basic sanity: header should be list of strings and length > 1
            if not isinstance(h, list) or len(h) < 2:
                bad_headers[s] = {"header_sample": h}
if bad_headers:
    blockers.append({
        "type": "schema_header_blocker",
        "reason": "some candidate surfaces have missing or suspicious CSV headers",
        "evidence": {"bad_headers": bad_headers, "read_errors": read_errors}
    })

# candidate_surface_quality_blocker: very small sample rows across surfaces
low_quality = {s: rc for s, rc in row_counts.items() if rc is not None and rc < 1}
if low_quality:
    blockers.append({
        "type": "candidate_surface_quality_blocker",
        "reason": "some candidate surfaces have very few sample rows indicating low-quality/empty datasets",
        "evidence": {"low_sample_row_counts": low_quality}
    })

# If no blockers yet, mark blocker_diagnosis_ok True; otherwise include unknown_blocker if nothing matched
if not blockers:
    blocker_diagnosis_ok = True
else:
    blocker_diagnosis_ok = True  # diagnosis performed; may include blockers

# If nothing matched but engine inputs seem present, still verify presence -> engine_ready_candidate
engine_ready_candidate = False
if not any(b["type"] in ("engine_input_blocker","dataset_layout_blocker","artifact_manifest_blocker") for b in blockers):
    # require all expected surfaces present and reasonable headers
    all_present = all(found_surfaces[s] for s in expected_surfaces)
    headers_ok = all((s not in headers) or (isinstance(headers.get(s), list) and len(headers.get(s))>=2) for s in expected_surfaces if found_surfaces[s])
    if all_present and headers_ok:
        engine_ready_candidate = True

# Compose final summary
final_summary = {
    "batch": "REPLAY-DATA-NEXT-AUDIT",
    "timestamp_utc": ts,
    "latest_proof_path": str(latest_proof_path),
    "canonical_root": str(canonical_dir) if canonical_dir else None,
    "source_date": source_date,
    "accepted_file_stems_discovered": sorted(list(accepted_stems)) if accepted_stems else [],
    "found_surfaces": found_surfaces,
    "headers_sample": headers,
    "row_counts_sample": row_counts,
    "read_errors": read_errors,
    "repo_files_inspected": list(repo_contents.keys()),
    "blockers": blockers,
    "blocker_diagnosis_ok": blocker_diagnosis_ok,
    "engine_ready_candidate": engine_ready_candidate,
    "blocker_count": len(blockers),
    "recommended_next_batch": "REPLAY-DATA-A17 engine_readiness_blocker_diagnosis" if True else None,
    "next_batch": "REPLAY-DATA-NEXT-AUDIT"
}

# Write proof JSON
try:
    with proof_filename.open("w", encoding="utf-8") as f:
        json.dump(final_summary, f, indent=2)
except Exception as e:
    print("ERROR writing proof JSON:", e)

# Write markdown milestone with human-readable summary
md_lines = []
md_lines.append(f"# REPLAY-DATA-NEXT-AUDIT — Conservative Audit Output")
md_lines.append("")
md_lines.append(f"- generated_at_utc: {ts}")
md_lines.append(f"- latest_proof_inspected: {latest_proof_path}")
md_lines.append(f"- canonical_root: {final_summary['canonical_root']}")
md_lines.append(f"- source_date: {source_date}")
md_lines.append("")
md_lines.append("## Quick Findings")
md_lines.append("")
md_lines.append(f"- blocker_diagnosis_ok: {blocker_diagnosis_ok}")
md_lines.append(f"- engine_ready_candidate: {engine_ready_candidate}")
md_lines.append(f"- blocker_count: {len(blockers)}")
md_lines.append("")
md_lines.append("## Blockers (detailed)")
if blockers:
    for b in blockers:
        md_lines.append("")
        md_lines.append(f"- type: {b.get('type')}")
        md_lines.append(f"  - reason: {b.get('reason')}")
        md_lines.append(f"  - evidence: {json.dumps(b.get('evidence'), default=str)[:1000]}")
else:
    md_lines.append("- none identified by heuristic audit")
md_lines.append("")
md_lines.append("## Found candidate surfaces (paths or null)")
for s,p in found_surfaces.items():
    md_lines.append(f"- {s}: {p}")
md_lines.append("")
md_lines.append("## Headers sample (first-row) for present files")
for s,h in headers.items():
    md_lines.append(f"- {s}: {h}")
md_lines.append("")
md_lines.append("## Recommended next batch")
md_lines.append(f"- recommended_next_batch: {final_summary['recommended_next_batch']}")
md_lines.append(f"- next_batch: {final_summary['next_batch']}")
md_text = "\n".join(md_lines)

try:
    with md_filename.open("w", encoding="utf-8") as f:
        f.write(md_text)
except Exception as e:
    print("ERROR writing milestone md:", e)

# Print minimal confirmation to stdout (safe)
print(json.dumps({
    "proof_written": str(proof_filename),
    "md_written": str(md_filename),
    "engine_ready_candidate": engine_ready_candidate,
    "blocker_count": len(blockers),
    "next_batch": final_summary["next_batch"]
}))
PY
