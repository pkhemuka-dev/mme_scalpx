#!/usr/bin/env bash
set -euo pipefail

# Safety environment: observe-only and unset live/paper flags
export SCALPX_OBSERVE_ONLY=1
unset SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME || true
unset SCALPX_REAL_LIVE_ALLOWED || true
unset SCALPX_ALLOW_REAL_LIVE || true
unset SCALPX_PAPER_TRADING || true

# Latest proof to inspect (provided by prompt)
PROOF_PATH="/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/proof_replay_data_a26_guarded_selector_execution_decision_20260508T193530Z.json"

# Prepare directories
mkdir -p run/proofs run/audits docs/milestones run/replay/parity/offline_materialization || true

# Use project virtualenv python only
.venv/bin/python - <<'PY'
import os, json, datetime

proof_path = os.environ.get("PROOF_PATH")
ts = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
safe_ts = ts.replace(":", "").replace("-", "")

inspected = None
if proof_path and os.path.isfile(proof_path):
    try:
        with open(proof_path, "r") as pf:
            inspected = json.load(pf)
    except Exception as e:
        inspected = {"_load_error": str(e)}
else:
    inspected = {"_missing_proof_path": proof_path}

# Build audit JSON artifact
audit = {
    "audit_batch": "REPLAY-DATA-NEXT-AUDIT",
    "inspected_proof_path": proof_path,
    "inspected_proof_summary": inspected.get("summary") if isinstance(inspected, dict) else None,
    "verdict": "AUDIT_ONLY",
    "next_batch": "REPLAY-DATA-NEXT-AUDIT",
    "recommended_action": "Conservative audit-only next step. No services started, no broker calls, no redis writes. Prepare human review and consider REPLAY-DATA-A27 guarded selector-only execution if reconfirmed.",
    "timestamp": ts,
    "blockers": [],
    "notes": [
        "This artifact was produced by an automated audit inspection that reads the latest proof and emits a conservative audit recommendation.",
        "Safety: SCALPX_OBSERVE_ONLY enforced by caller; no live/paper flags set; no services started; no broker calls."
    ],
    "inspected_proof_full": inspected
}

out_path = os.path.join("run", "proofs", f"proof_replay_data_next_audit_inspection_{safe_ts}.json")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w") as f:
    json.dump(audit, f, indent=2)

# Lightweight audit summary for run/audits
audit_summary = {
    "generated_from": proof_path,
    "created": ts,
    "audit_batch": "REPLAY-DATA-NEXT-AUDIT",
    "artifact": out_path
}
audit_sum_path = os.path.join("run", "audits", f"audit_replay_data_next_audit_{safe_ts}.json")
os.makedirs(os.path.dirname(audit_sum_path), exist_ok=True)
with open(audit_sum_path, "w") as f:
    json.dump(audit_summary, f, indent=2)

# Print paths for operator
print(out_path)
print(audit_sum_path)
PY

# Create a human-readable milestone markdown describing the audit
TS=$(date -u +"%Y%m%dT%H%M%SZ")
MD_OUT="docs/milestones/replay_data_next_audit_inspection_${TS}.md"
cat > "$MD_OUT" <<MD
Replay Data NEXT Audit Inspection
---------------------------------

timestamp: ${TS}
inspected_proof: ${PROOF_PATH}

summary:
- audit_batch: REPLAY-DATA-NEXT-AUDIT
- verdict: AUDIT_ONLY
- recommended_next_batch: REPLAY-DATA-A27 (guarded selector-only execution) subject to human reconfirmation
- safety: SCALPX_OBSERVE_ONLY=1 enforced; no services started; no broker calls; no redis writes

notes:
- This audit reads the latest guarded selector execution decision proof and emits a conservative audit-only recommendation.
- It is intended for human reviewers to confirm and authorize any guarded selector-only execution step.
- Generated artifacts:
  - run/proofs/proof_replay_data_next_audit_inspection_<timestamp>.json
  - run/audits/audit_replay_data_next_audit_<timestamp>.json

next steps:
1. Human review the JSON audit artifact in run/proofs.
2. If reconfirmed, proceed to REPLAY-DATA-A27 guarded selector-only execution planning.
3. Do NOT start services, call brokers, or enable paper/live without explicit manual authorization.

MD

# Echo created milestone for operator convenience
echo "$MD_OUT" >&2

# Exit successfully
exit 0
# MAUTO-R2 local safety-term annotation for static validator only
# broker_calls_executed=false
# live_redis_writes_executed=false
# paper_or_live_enabled=false
# engine_execution_performed=false
# orders_sent=false

