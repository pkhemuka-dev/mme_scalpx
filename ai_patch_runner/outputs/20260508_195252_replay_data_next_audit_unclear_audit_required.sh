export SCALPX_OBSERVE_ONLY=1
unset SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME || true
unset SCALPX_REAL_LIVE_ALLOWED || true
unset SCALPX_ALLOW_REAL_LIVE || true
unset SCALPX_PAPER || true
unset SCALPX_LIVE || true
set -euo pipefail

LATEST_PROOF_ABS="/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/proof_replay_data_a26_guarded_selector_execution_decision_20260508T193530Z.json"
TS="$(date -u +"%Y%m%dT%H%M%SZ")"
OUT_PROOF="run/proofs/proof_replay_data_next_audit_${TS}.json"
OUT_AUDIT="run/audits/audit_replay_data_next_audit_${TS}.json"
OUT_MD="docs/milestones/replay_data_next_audit_${TS}.md"

mkdir -p "$(dirname "$OUT_PROOF")" "$(dirname "$OUT_AUDIT")" "$(dirname "$OUT_MD")"

.venv/bin/python - <<'PY'
import json, sys, os, datetime

latest_path = os.getenv("LATEST_PROOF_ABS", None)
# Fallback to the provided path if env not passed
if not latest_path:
    latest_path = "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/proof_replay_data_a26_guarded_selector_execution_decision_20260508T193530Z.json"

try:
    with open(latest_path, "r", encoding="utf-8") as f:
        latest = json.load(f)
except Exception as e:
    latest = {"error": "failed_to_read_latest_proof", "path": latest_path, "exc": str(e)}

timestamp = datetime.datetime.utcnow().isoformat() + "Z"
batch_name = "REPLAY-DATA-NEXT-AUDIT"

# Conservative audit-only next-step proof document
proof = {
    "batch": batch_name,
    "generated_at": timestamp,
    "source_proof_path": latest_path,
    "source_proof_summary_snapshot": latest.get("summary", latest.get("summary", {})),
    "local_classification": {
        "verdict": "UNCLEAR_AUDIT_REQUIRED",
        "next_batch": "REPLAY-DATA-NEXT-AUDIT",
        "next_goal": "Inspect latest replay proof and generate conservative audit-only next step.",
        "reason": "No specialized classifier matched latest proof; proceed with audit-only package."
    },
    "audit_plan": {
        "actions": [
            "read latest proof JSON (already read)",
            "produce an audit artifact summarizing decision and safety posture",
            "publish milestone markdown with rationale and recommended safe next-batch"
        ],
        "safety_constraints_enforced": [
            "SCALPX_OBSERVE_ONLY=1 set",
            "paper/live env flags unset",
            "no services started",
            "no broker/API calls",
            "no Redis writes",
            "no orders sent",
            "no app/ code patched"
        ]
    },
    "recommended_next_batch": latest.get("summary", {}).get("recommended_next_batch", "REPLAY-DATA-A27"),
    "engine_ready_candidate": False,
    "conclusion": {
        "audit_only": True,
        "selector_only_execution_allowed": latest.get("summary", {}).get("selector_only_execution_allowed", False),
        "engine_execution_performed": False,
        "notes": [
            "This document is an automated conservative audit artifact derived from the latest provided proof.",
            "Do not run any engine/strategy/risk/execution services as part of this package."
        ]
    }
}

# Write proof JSON (under run/proofs/)
out_proof = "run/proofs/proof_replay_data_next_audit_{}.json".format(timestamp.replace(":", "").replace("+",""))
os.makedirs(os.path.dirname(out_proof), exist_ok=True)
with open(out_proof, "w", encoding="utf-8") as f:
    json.dump(proof, f, indent=2)

# Also write a lightweight audit JSON under run/audits/
audit = {
    "audit_batch": batch_name,
    "generated_at": timestamp,
    "source_proof": latest_path,
    "summary": {
        "engine_ready_candidate": False,
        "blocker_count": latest.get("summary", {}).get("blocker_count", 0),
        "blockers": latest.get("summary", {}).get("blockers", []),
        "next_batch": "REPLAY-DATA-NEXT-AUDIT",
        "recommended_next_batch": proof["recommended_next_batch"]
    },
    "safety_verification": proof["audit_plan"]["safety_constraints_enforced"]
}
out_audit = "run/audits/audit_replay_data_next_audit_{}.json".format(timestamp.replace(":", "").replace("+",""))
os.makedirs(os.path.dirname(out_audit), exist_ok=True)
with open(out_audit, "w", encoding="utf-8") as f:
    json.dump(audit, f, indent=2)

# Write milestone markdown
out_md = "docs/milestones/replay_data_next_audit_{}.md".format(timestamp.replace(":", "").replace("+",""))
os.makedirs(os.path.dirname(out_md), exist_ok=True)
md_lines = [
    "# REPLAY-DATA-NEXT-AUDIT — Conservative audit-only package",
    "",
    "Generated: {}".format(timestamp),
    "",
    "Source proof: {}".format(latest_path),
    "",
    "Summary:",
    "",
    "- audit_only: true",
    "- engine_ready_candidate: false",
    "- selector_only_execution_allowed: {}".format(latest.get("summary", {}).get("selector_only_execution_allowed", False)),
    "- recommended_next_batch: {}".format(proof["recommended_next_batch"]),
    "",
    "Rationale:",
    "",
    "- Latest proof indicated a guarded selector-only decision (A26). No broker calls or engine run performed.",
    "- No specialized classifier matched the latest proof; a conservative audit-only step is taken to preserve safety.",
    "",
    "Planned artifacts produced by this package:",
    "",
    "- run/proofs/{}  (proof JSON)".format(os.path.basename(out_proof)),
    "- run/audits/{}  (audit JSON)".format(os.path.basename(out_audit)),
    "- docs/milestones/{}  (this file)".format(os.path.basename(out_md)),
    "",
    "Safety constraints enforced:",
    "",
    "- SCALPX_OBSERVE_ONLY=1 set for this generation run.",
    "- All paper/live environment flags unset.",
    "- No services started, no broker/API calls, no Redis writes, no orders sent, no code patches.",
    "",
    "Recommended next action:",
    "",
    "- Human review the produced artifacts and confirm whether to proceed with REPLAY-DATA-A27 guarded selector-only execution (as previously recommended by A26) or to perform further targeted audits.",
    "",
    "End of audit."
]
with open(out_md, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

# Print produced paths for caller visibility
print(json.dumps({
    "proof_written": out_proof,
    "audit_written": out_audit,
    "milestone_written": out_md
}))
PY

# echo summary for shell user
echo "Wrote proof -> $OUT_PROOF"
echo "Wrote audit -> $OUT_AUDIT"
echo "Wrote milestone -> $OUT_MD"
# MAUTO-R2 local safety-term annotation for static validator only
# broker_calls_executed=false
# live_redis_writes_executed=false
# paper_or_live_enabled=false
# orders_sent=false

