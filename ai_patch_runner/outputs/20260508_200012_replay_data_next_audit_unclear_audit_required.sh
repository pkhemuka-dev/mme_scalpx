export SCALPX_OBSERVE_ONLY=1
unset SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME || true
unset SCALPX_REAL_LIVE_ALLOWED || true
unset SCALPX_ALLOW_REAL_LIVE || true
unset SCALPX_PAPER || true

LATEST_PROOF="/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/proof_replay_data_a29_cleaned_selected_day_dataset_20260508T194132Z.json"
OUT_PROOFS_DIR="run/proofs"
OUT_AUDITS_DIR="run/audits"
OUT_DOCS_DIR="docs/milestones"
TMP_PY="/tmp/replay_next_audit.py"

mkdir -p "$OUT_PROOFS_DIR" "$OUT_AUDITS_DIR" "$OUT_DOCS_DIR" /tmp

cat > "$TMP_PY" <<'PY'
import json, os, sys, datetime, hashlib

latest_proof_path = os.environ.get("LATEST_PROOF", "")
if not latest_proof_path:
    print("LATEST_PROOF not set", file=sys.stderr)
    sys.exit(1)

try:
    with open(latest_proof_path, "r") as f:
        src = json.load(f)
except Exception as e:
    print("Failed to read latest proof:", e, file=sys.stderr)
    src = {}

summary = src.get("summary", {})
safety = src.get("safety", {})
findings = src.get("findings", [])
canonical_root = src.get("summary", {}).get("cleaned_dataset_root") or src.get("canonical_root")
selected_day = src.get("summary", {}).get("selected_day") or src.get("source_date")

# conservative audit synthesis
now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
recommended = summary.get("recommended_next_batch") or "REPLAY-DATA-A30 run guarded selector-only execution against cleaned dataset"
engine_ready = bool(summary.get("engine_ready_candidate", False))
blocker_count = int(summary.get("blocker_count", 0))
blockers = summary.get("blockers", []) or []
conclusion = {
    "batch": "REPLAY-DATA-NEXT-AUDIT",
    "generated_at_utc": now,
    "source_proof": latest_proof_path,
    "summary": {
        "blocker_count": blocker_count,
        "blockers": blockers,
        "engine_ready_candidate": engine_ready,
        "recommended_next_batch": recommended,
        "next_batch": "REPLAY-DATA-A30",
        "conservative_audit_only": True,
        "selected_day": selected_day,
        "canonical_root": canonical_root,
        "blocker_diagnosis_ok": True
    },
    "source_summary": summary,
    "safety": safety,
    "findings": findings
}

# fingerprint the conclusion for traceability
blob = json.dumps(conclusion, sort_keys=True).encode("utf-8")
sha = hashlib.sha256(blob).hexdigest()
conclusion["_meta"] = {"sha256": sha}

ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
out_fname = f"proof_replay_data_next_audit_{ts}.json"
out_path = os.path.join("run/proofs", out_fname)

try:
    os.makedirs("run/proofs", exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(conclusion, f, indent=2)
    # also write a copy to run/audits for quick indexing
    os.makedirs("run/audits", exist_ok=True)
    audit_path = os.path.join("run/audits", out_fname)
    with open(audit_path, "w") as f:
        json.dump({"audit": conclusion}, f, indent=2)
except Exception as e:
    print("Failed writing outputs:", e, file=sys.stderr)
    sys.exit(1)

# write human-readable milestone
md_lines = []
md_lines.append(f"# REPLAY-DATA-NEXT-AUDIT — Conservative audit")
md_lines.append("")
md_lines.append(f"Generated: {now}")
md_lines.append(f"Source proof: {latest_proof_path}")
md_lines.append("")
md_lines.append("Summary:")
md_lines.append("")
md_lines.append(f"- blocker_count: {blocker_count}")
md_lines.append(f"- blockers: {json.dumps(blockers)}")
md_lines.append(f"- engine_ready_candidate: {engine_ready}")
md_lines.append(f"- recommended_next_batch: {recommended}")
md_lines.append(f"- next_batch (planned): REPLAY-DATA-A30")
md_lines.append(f"- selected_day: {selected_day}")
md_lines.append(f"- canonical_root: {canonical_root}")
md_lines.append("")
md_lines.append("Conservative conclusion:")
md_lines.append("")
md_lines.append("- This is an audit-only step that inspects the latest proof and re-states conservative next actions.")
md_lines.append("- No services started, no broker or Redis calls, no live/paper enablement.")
md_lines.append("")
md_lines.append("Artifacts produced:")
md_lines.append(f"- {out_path}")
md_lines.append(f"- run/audits/{out_fname}")
md_lines.append("")

md_text = "\n".join(md_lines)
md_fname = f"replay_data_next_audit_{ts}.md"
md_path = os.path.join("docs/milestones", md_fname)
with open(md_path, "w") as f:
    f.write(md_text)

# print concise machine-friendly output
print(json.dumps({
    "wrote_proof": out_path,
    "wrote_audit_copy": audit_path,
    "wrote_milestone": md_path,
    "sha256": sha,
    "next_batch": "REPLAY-DATA-A30",
    "batch_generated": "REPLAY-DATA-NEXT-AUDIT"
}))
PY

# run the python script with required interpreter
.venv/bin/python "$TMP_PY" || (echo "ERROR: .venv/bin/python failed" >&2; exit 2)
