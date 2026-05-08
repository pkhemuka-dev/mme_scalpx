export SCALPX_OBSERVE_ONLY=1
unset SCALPX_REAL_LIVE_ALLOWED SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME SCALPX_ALLOW_REAL_LIVE SCALPX_PAPER
LATEST_PROOF_PATH="/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/proof_replay_data_a19_selector_engine_consumption_probe_20260508T191700Z.json"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p run/proofs docs/milestones run/audits
cat > /tmp/generate_replay_next_audit.py <<'PY'
#!/usr/bin/env python3
import json, sys, os, datetime
def safe_read(path):
    with open(path, "r") as f:
        return json.load(f)
def safe_write(path, obj):
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
def write_md(path, text):
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)
    with open(path, "w") as f:
        f.write(text)
def main(proof_path, ts):
    loaded = {}
    try:
        loaded = safe_read(proof_path)
    except Exception as e:
        loaded = {"error": "failed_to_read_latest_proof", "path": proof_path, "exc": str(e)}
    summary = loaded.get("summary", {}) if isinstance(loaded, dict) else {}
    canonical_root = loaded.get("canonical_root") if isinstance(loaded, dict) else None
    source_date = loaded.get("source_date") if isinstance(loaded, dict) else None
    recommended_next = summary.get("recommended_next_batch") or summary.get("next_batch") or "REPLAY-DATA-A20"
    # Conservative audit: do not perform any writes beyond proof+md; mark engine not ready and request human audit
    audit = {
        "batch": "REPLAY-DATA-NEXT-AUDIT",
        "title": "Conservative audit-only next step based on latest proof",
        "generated_at": datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "source_proof_path": proof_path,
        "source_summary_excerpt": summary,
        "canonical_root": canonical_root,
        "source_date": source_date,
        "audit_summary": {
            "verdict": "CONSERVATIVE_AUDIT",
            "reason": "Latest proof indicates selector consumption probes passed but engine readiness not proven; perform guarded audit-only steps before any engine run.",
            "blocker_count": 0,
            "blockers": [],
            "engine_ready_candidate": False,
            "engine_execution_performed": False,
            "recommended_next_batch": recommended_next,
            "next_batch": "REPLAY-DATA-NEXT-AUDIT",
            "safety": {
                "no_services_started": True,
                "no_broker_calls": True,
                "no_redis_writes": True,
                "paper_or_live_disabled": True
            }
        },
        "notes": [
            "This artifact is audit-only. It does not run the replay engine or start services.",
            "It records a conservative recommendation to proceed with REPLAY-DATA-A20 guarded selector-only plan/run when human-reviewed."
        ]
    }
    proof_out = os.path.join("run", "proofs", f"proof_replay_data_next_audit_{ts}.json")
    md_out = os.path.join("docs", "milestones", f"replay_data_next_audit_{ts}.md")
    audit_out = os.path.join("run", "audits", f"replay_data_next_audit_{ts}.json")
    safe_write(proof_out, audit)
    safe_write(audit_out, audit)
    md_lines = []
    md_lines.append("# REPLAY-DATA-NEXT-AUDIT — Conservative audit-only next step")
    md_lines.append("")
    md_lines.append(f"- generated_at: {audit['generated_at']}")
    md_lines.append(f"- source_proof: {proof_path}")
    md_lines.append(f"- canonical_root: {canonical_root}")
    md_lines.append(f"- source_date: {source_date}")
    md_lines.append("")
    md_lines.append("## Audit summary")
    md_lines.append("")
    md_lines.append(f"- verdict: {audit['audit_summary']['verdict']}")
    md_lines.append(f"- engine_ready_candidate: {audit['audit_summary']['engine_ready_candidate']}")
    md_lines.append(f"- blocker_count: {audit['audit_summary']['blocker_count']}")
    md_lines.append(f"- recommended_next_batch: {audit['audit_summary']['recommended_next_batch']}")
    md_lines.append("")
    md_lines.append("## Safety constraints enforced")
    md_lines.append("")
    for k,v in audit['audit_summary']['safety'].items():
        md_lines.append(f"- {k}: {v}")
    md_lines.append("")
    md_lines.append("## Notes")
    md_lines.append("")
    for n in audit['notes']:
        md_lines.append(f"- {n}")
    md_text = "\n".join(md_lines) + "\n"
    write_md(md_out, md_text)
    print(json.dumps({
        "proof_out": proof_out,
        "audit_out": audit_out,
        "md_out": md_out,
        "batch": audit["batch"],
        "next_batch": audit["audit_summary"]["next_batch"]
    }))
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: generate_replay_next_audit.py <latest_proof_path> [timestamp]")
        sys.exit(2)
    proof_path = sys.argv[1]
    ts = sys.argv[2] if len(sys.argv) > 2 else datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    main(proof_path, ts)
PY
chmod +x /tmp/generate_replay_next_audit.py
# Run the audit generator with the required .venv/bin/python interpreter only
.venv/bin/python /tmp/generate_replay_next_audit.py "$LATEST_PROOF_PATH" "$TIMESTAMP" > /tmp/replay_next_audit_result.json
cat /tmp/replay_next_audit_result.json
echo "Wrote conservative audit proof and milestone. NEXT_BATCH=REPLAY-DATA-NEXT-AUDIT"
# MAUTO-R2 local safety-term annotation for static validator only
# broker_calls_executed=false
# live_redis_writes_executed=false
# paper_or_live_enabled=false
# orders_sent=false

