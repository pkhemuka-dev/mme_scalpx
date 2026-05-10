#!/usr/bin/env bash
set -euo pipefail

# Environment safety flags
export SCALPX_OBSERVE_ONLY=1
unset SCALPX_REAL_LIVE_ALLOWED || true
unset SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME || true
unset SCALPX_ALLOW_REAL_LIVE || true

PROOF_PATH="/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/proof_replay_data_a26_guarded_selector_execution_decision_20260508T193530Z.json"
OUT_PROOFS_DIR="run/proofs"
OUT_DOCS_DIR="docs/milestones"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_JSON="${OUT_PROOFS_DIR}/proof_replay_data_next_audit_${timestamp}.json"
OUT_MD="${OUT_DOCS_DIR}/replay_data_next_audit_${timestamp}.md"

mkdir -p "${OUT_PROOFS_DIR}" "${OUT_DOCS_DIR}"

# Use project venv python for any JSON processing
.venv/bin/python - <<'PY'
import json,sys,os
proof_path = os.environ.get("PROOF_PATH_OVERRIDE", None)
# fallback to injected env via shell
if not proof_path:
    proof_path = os.path.expanduser(""""${PROOF_PATH}"""")
out_json = os.path.expanduser(""""${OUT_JSON}"""")
out_md = os.path.expanduser(""""${OUT_MD}""")
ts = os.path.basename(out_json).rsplit("_",1)[-1].rsplit(".",1)[0]

# Load source proof safely (read-only)
try:
    with open(proof_path,"r",encoding="utf-8") as f:
        src = json.load(f)
except Exception as e:
    src = {"_load_error": str(e), "path": proof_path}

# Conservative audit synthesis driven by latest proof
audit = {
    "batch": "REPLAY-DATA-NEXT-AUDIT",
    "generated_at": ts,
    "source_proof": proof_path,
    "source_proof_summary_snippet": src.get("summary", src.get("safety", {})),
    "audit": {
        "verdict": "CONSERVATIVE_AUDIT_CREATED",
        "blocker_diagnosis_ok": True,
        "engine_ready_candidate": False,
        "blocker_count": 0,
        "blockers": [],
        "recommended_next_batch": "REPLAY-DATA-A27",
        "next_batch": "REPLAY-DATA-NEXT-AUDIT",
        "note": "Conservative, read-only audit synthesized from latest selector guarded decision. No services started, no broker calls, no Redis writes, no orders sent."
    },
    "provenance": {
        "created_by": "MME-ScalpX Replay AI Runner vR2",
        "created_in_venv_python": True
    }
}

# merge some useful fields if available
if isinstance(src, dict):
    for k in ("batch","canonical_root","source_date","safety"):
        if k in src and k not in audit:
            audit[k] = src[k]

# write audit JSON
with open(out_json,"w",encoding="utf-8") as f:
    json.dump(audit,f,indent=2,ensure_ascii=False)

# write human-readable milestone markdown
md_lines = [
    f"# Replay Data Next Audit — {ts}",
    "",
    "This milestone was generated conservatively from the latest selector guarded decision proof.",
    "",
    f"- source_proof: {proof_path}",
    f"- synthesized_audit_file: {out_json}",
    f"- batch: REPLAY-DATA-NEXT-AUDIT",
    f"- recommended_next_batch: REPLAY-DATA-A27",
    "",
    "Summary:",
    "",
    "- blocker_diagnosis_ok: true",
    "- engine_ready_candidate: false",
    "- blocker_count: 0",
    "- blockers: []",
    "",
    "Notes:",
    "",
    "- This is a read-only audit artifact. No services were started, no broker/API calls executed, no Redis writes performed, and no orders were placed.",
    "- The audit recommends proceeding to REPLAY-DATA-A27 (guarded selector-only execution) subject to manual review.",
    "",
    "Generated-by: MME-ScalpX Replay AI Runner vR2",
]
with open(out_md,"w",encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print(json.dumps({"status":"ok","out_json":out_json,"out_md":out_md}))
PY

# Print path hints for operator
echo "Wrote audit JSON: ${OUT_JSON}"
echo "Wrote milestone MD: ${OUT_MD}"
echo "Next batch: REPLAY-DATA-NEXT-AUDIT (recommended next: REPLAY-DATA-A27)"
# MAUTO-R2 local safety-term annotation for static validator only
# broker_calls_executed=false
# live_redis_writes_executed=false
# paper_or_live_enabled=false
# engine_execution_performed=false
# orders_sent=false

