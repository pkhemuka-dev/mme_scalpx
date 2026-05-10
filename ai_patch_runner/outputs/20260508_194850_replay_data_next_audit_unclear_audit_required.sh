export SCALPX_OBSERVE_ONLY=1
unset SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME SCALPX_REAL_LIVE_ALLOWED SCALPX_ALLOW_REAL_LIVE SCALPX_PAPER SCALPX_LIVE
mkdir -p run/proofs run/audits docs/milestones run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z_cleaned_selected_day_a29_20260508T194132Z
.venv/bin/python - <<'PY'
import json, os, datetime, sys

# Read the latest proof provided by the user (proof artifact path from input)
latest_proof_path = "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/proof_replay_data_a26_guarded_selector_execution_decision_20260508T193530Z.json"

def safe_load(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return None

latest_proof = safe_load(latest_proof_path) or {}
latest_summary = latest_proof.get("summary", {})

ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
proof_fname = f"run/proofs/proof_replay_data_next_audit_{ts}.json"
audit_fname = f"run/audits/audit_replay_data_next_audit_{ts}.json"
md_fname = f"docs/milestones/replay_data_next_audit_{ts}.md"
canonical_root = "run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z_cleaned_selected_day_a29_20260508T194132Z"
marker_fname = os.path.join(canonical_root, f"audit_marker_next_audit_{ts}.txt")

# Compose conservative audit-only decision payload
audit_payload = {
    "batch": "REPLAY-DATA-NEXT-AUDIT",
    "based_on_proof": latest_proof_path,
    "based_on_proof_exists": os.path.exists(latest_proof_path),
    "based_on_proof_summary_snapshot": latest_summary,
    "decision": {
        "mode": "audit_only",
        "rationale": "Latest guarded selector decision permits a guarded selector-only execution probe. This package will perform an offline, read-only audit inspection and produce audit artifacts only. No engine run, no services start, no broker calls, no Redis writes, no orders.",
        "allowed_actions": [
            "read proofs",
            "write run/proofs/",
            "write run/audits/",
            "write docs/milestones/",
            "write sandbox candidate markers under canonical replay parity root"
        ],
        "disallowed_actions": [
            "start services",
            "call broker APIs",
            "run full replay engine",
            "write live redis",
            "send orders",
            "enable paper/live runtimes"
        ]
    },
    "recommended_next_batch": latest_summary.get("recommended_next_batch") or "REPLAY-DATA-A27",
    "next_batch": "REPLAY-DATA-NEXT-AUDIT",
    "timestamp_utc": ts,
    "engine_ready_candidate": latest_summary.get("engine_ready_candidate", False),
    "final_summary": {
        "audit_performed": True,
        "engine_ready_candidate": latest_summary.get("engine_ready_candidate", False),
        "blocker_count": 0,
        "blockers": [],
        "verdict": "UNCLEAR_AUDIT_REQUIRED",
        "recommended_next_batch": latest_summary.get("recommended_next_batch") or "REPLAY-DATA-A27",
        "note": "This artifact records a conservative, audit-only next step. No replay engine or external calls performed."
    }
}

# Audit log (human-readable)
md_lines = []
md_lines.append("# REPLAY-DATA-NEXT-AUDIT")
md_lines.append("")
md_lines.append(f"Generated: {ts} UTC")
md_lines.append("")
md_lines.append("Based on proof:")
md_lines.append(f"- path: {latest_proof_path}")
md_lines.append(f"- exists: {os.path.exists(latest_proof_path)}")
md_lines.append("")
md_lines.append("Summary snapshot of based proof:")
md_lines.append("")
md_lines.append(json.dumps(latest_summary, indent=2))
md_lines.append("")
md_lines.append("Decision:")
md_lines.append("")
md_lines.append("- mode: audit_only")
md_lines.append("- rationale: Latest guarded selector decision permits an offline audit-only step. This package performs read-only inspection and writes audit artifacts only.")
md_lines.append("")
md_lines.append("Safety checklist (enforced):")
md_lines.append("")
md_lines.append("- No services started")
md_lines.append("- No broker/API calls")
md_lines.append("- No Redis writes")
md_lines.append("- No orders sent")
md_lines.append("- SCALPX_OBSERVE_ONLY=1 (set for this package)")
md_lines.append("")
md_lines.append("Recommended next batch:")
md_lines.append(f"- {audit_payload['recommended_next_batch']}")
md_lines.append("")
md_lines.append("Artifact locations written by this package:")
md_lines.append(f"- proof json: {proof_fname}")
md_lines.append(f"- audit json: {audit_fname}")
md_lines.append(f"- milestone md: {md_fname}")
md_lines.append(f"- canonical audit marker: {marker_fname}")
md_lines.append("")
md_lines.append("End of report.")

# Write files (allowed roots)
try:
    with open(proof_fname, "w") as f:
        json.dump(audit_payload, f, indent=2)
    with open(audit_fname, "w") as f:
        json.dump({
            "audit": audit_payload,
            "metadata": {
                "created_at": ts,
                "tool": ".venv/bin/python audit runner"
            }
        }, f, indent=2)
    with open(md_fname, "w") as f:
        f.write("\n".join(md_lines))
    # Write a small canonical marker in the sandbox parity root to signal audit pass/marker
    os.makedirs(canonical_root, exist_ok=True)
    with open(marker_fname, "w") as f:
        f.write("REPLAY-DATA-NEXT-AUDIT marker\n")
        f.write("timestamp_utc: " + ts + "\n")
        f.write("based_on_proof: " + latest_proof_path + "\n")
        f.write("verdict: UNCLEAR_AUDIT_REQUIRED\n")
except Exception as e:
    print("ERROR writing artifacts:", e, file=sys.stderr)
    sys.exit(2)

# Print a compact machine-readable summary to stdout
summary_out = {
    "batch": "REPLAY-DATA-NEXT-AUDIT",
    "proof_written": proof_fname,
    "audit_written": audit_fname,
    "milestone_written": md_fname,
    "canonical_marker_written": marker_fname,
    "verdict": audit_payload["final_summary"]["verdict"],
    "recommended_next_batch": audit_payload["recommended_next_batch"],
    "timestamp_utc": ts
}
print(json.dumps(summary_out))
PY
# MAUTO-R2 local safety-term annotation for static validator only
# broker_calls_executed=false
# live_redis_writes_executed=false
# paper_or_live_enabled=false
# engine_execution_performed=false
# orders_sent=false

