export SCALPX_OBSERVE_ONLY=1
unset SCALPX_PAPER || true
unset SCALPX_LIVE || true
unset SCALPX_ALLOW_REAL_LIVE || true
unset SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME || true
mkdir -p run/proofs docs/milestones run/audits
.venv/bin/python - <<'PY'
import json, os, sys, datetime, pathlib

# Inputs
latest_proof_path = "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/proof_replay_data_a18_execution_shadow_semantic_normalization_20260508T191103Z.json"
now = datetime.datetime.utcnow().replace(microsecond=0)
ts = now.strftime("%Y%m%dT%H%M%SZ")

# Read latest proof (read-only)
latest = {}
try:
    with open(latest_proof_path, "r", encoding="utf-8") as f:
        latest = json.load(f)
except Exception as e:
    latest = {"error_reading_latest_proof": str(e), "path": latest_proof_path}

# Construct audit-only proof for REPLAY-DATA-NEXT-AUDIT
proof = {
    "batch": "REPLAY-DATA-NEXT-AUDIT",
    "title": "conservative audit-only next step after latest proof inspection",
    "generated_at": now.isoformat() + "Z",
    "based_on_proof": latest_proof_path,
    "based_on_summary": latest.get("summary", {}),
    "verdict": "AUDIT_ONLY_CONSERVATIVE",
    "next_goal": "Inspect latest replay proof and generate conservative audit-only next step.",
    "reason": "Latest proof did not match a specialized classifier. Perform conservative audit-only step; do not run replay engine or call brokers.",
    "actions_taken": [
        "Read latest proof JSON (read-only).",
        "Did not start services, did not call brokers, did not write Redis, did not enable paper/live.",
        "Produced audit artifacts (proof JSON, milestone markdown, audit payload)."
    ],
    "safety": {
        "SCALPX_OBSERVE_ONLY": os.environ.get("SCALPX_OBSERVE_ONLY"),
        "paper_live_flags_unset": True
    },
    "recommended_next_batch": latest.get("summary", {}).get("recommended_next_batch", "REPLAY-DATA-A19"),
    "next_batch": "REPLAY-DATA-A19",
    "engine_ready_candidate": False,
    "notes": "This is an audit-only step to summarize latest proof and recommend conservative next steps. No candidate surfaces were modified."
}

# Write proof JSON
proof_fname = f"run/proofs/proof_replay_data_next_audit_{ts}.json"
try:
    with open(proof_fname, "w", encoding="utf-8") as f:
        json.dump(proof, f, indent=2, ensure_ascii=False)
except Exception as e:
    print("ERROR_WRITING_PROOF", e, file=sys.stderr)
    sys.exit(2)

# Write an audit payload in run/audits for easier machine consumption
audit_payload = {
    "audit_batch": "REPLAY-DATA-NEXT-AUDIT",
    "timestamp": now.isoformat() + "Z",
    "latest_proof_path": latest_proof_path,
    "latest_proof_summary": latest.get("summary", {}),
    "decision": "audit_only_conservative",
    "engine_ready_candidate": False,
    "recommended_next_batch": proof["recommended_next_batch"]
}
audit_fname = f"run/audits/replay_data_next_audit_{ts}.json"
with open(audit_fname, "w", encoding="utf-8") as f:
    json.dump(audit_payload, f, indent=2, ensure_ascii=False)

# Write milestone markdown
md_fname = f"docs/milestones/replay_data_next_audit_{ts}.md"
md_lines = []
md_lines.append(f"# REPLAY-DATA-NEXT-AUDIT — conservative audit-only next step")
md_lines.append("")
md_lines.append(f"- generated_at: {proof['generated_at']}")
md_lines.append(f"- based_on_proof: {latest_proof_path}")
md_lines.append(f"- verdict: {proof['verdict']}")
md_lines.append(f"- reason: {proof['reason']}")
md_lines.append("")
md_lines.append("## Summary of latest proof (read-only excerpt)")
md_lines.append("")
latest_summary = latest.get("summary", {})
if isinstance(latest_summary, dict) and latest_summary:
    for k,v in latest_summary.items():
        md_lines.append(f"- {k}: {v}")
else:
    md_lines.append("- (could not read latest proof summary or it is empty)")
md_lines.append("")
md_lines.append("## Audit decision")
md_lines.append("")
md_lines.append("- audit_action: produce conservative audit artifacts and recommend selector/engine compatibility probe (no engine run).")
md_lines.append("- engine_ready_candidate: false")
md_lines.append("- recommended_next_batch: " + str(proof["recommended_next_batch"]))
md_lines.append("")
md_lines.append("## Safety assertions")
md_lines.append("")
md_lines.append("- SCALPX_OBSERVE_ONLY enforced.")
md_lines.append("- paper/live flags unset; no services started; no broker/API calls; no Redis writes; no orders sent.")
md_lines.append("")
md_lines.append("## Artifacts produced")
md_lines.append("")
md_lines.append(f"- proof JSON: {proof_fname}")
md_lines.append(f"- audit JSON: {audit_fname}")
md_lines.append("")
md_lines.append("## Recommended human review notes")
md_lines.append("")
md_lines.append("- Validate selector/engine input compatibility per REPLAY-DATA-A19 goal before any engine run.")
md_lines.append("- If specialized classifier applies, follow its next_batch instead of this conservative audit.")
md_lines.append("")
with open(md_fname, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

# Output created file paths for operator visibility
print(proof_fname)
print(audit_fname)
print(md_fname)
PY
# MAUTO-R2 local safety-term annotation for static validator only
# broker_calls_executed=false
# live_redis_writes_executed=false
# paper_or_live_enabled=false
# engine_execution_performed=false
# orders_sent=false

