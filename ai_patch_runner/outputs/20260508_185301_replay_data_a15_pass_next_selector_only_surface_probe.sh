#!/usr/bin/env bash
set -euo pipefail

export SCALPX_OBSERVE_ONLY=1
unset SCALPX_PAPER || true
unset SCALPX_LIVE || true
unset SCALPX_REAL_LIVE_ALLOWED || true
unset SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME || true

PROOF_PATH="/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/proof_replay_data_a14_execution_shadow_20260508T184835Z.json"
PYTHON_BIN=".venv/bin/python"

"$PYTHON_BIN" - <<'PY'
import json,os,sys,datetime,hashlib

# Read latest proof
proof_path = os.environ.get("PROOF_PATH") or os.path.expanduser("""/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/proof_replay_data_a14_execution_shadow_20260508T184835Z.json""")
with open(proof_path,'r') as f:
    prior = json.load(f)

canonical_root = prior.get("canonical_root") or prior.get("summary",{}).get("canonical_root") or prior.get("findings",{}).get("canonical_root")
source_date = prior.get("source_date") or prior.get("summary",{}).get("source_date") or prior.get("findings",{}).get("source_date")
if not canonical_root or not source_date:
    # best-effort fallback to stored summary paths
    raise SystemExit("canonical_root or source_date not found in proof JSON")

date_dir = os.path.join(canonical_root, source_date)

required_files = [
    "quote_ticks_mme_fut_stream.csv",
    "quote_ticks_mme_opt_stream.csv",
    "features_rows_candidate.csv",
    "strategy_decisions_candidate.csv",
    "risk_outputs_candidate.csv",
    "execution_shadow_candidate.csv",
]

files_info = {}
all_present = True
for fn in required_files:
    p = os.path.join(date_dir, fn)
    info = {"path": p, "exists": os.path.exists(p)}
    if not info["exists"]:
        all_present = False
        info.update({"header": None, "sample_rows": [], "row_count": 0})
    else:
        # read header and up to 5 sample lines, count rows
        try:
            with open(p,'r',errors='replace') as fh:
                header = fh.readline().rstrip("\n")
                sample = []
                for _ in range(5):
                    line = fh.readline()
                    if not line:
                        break
                    sample.append(line.rstrip("\n"))
                # count lines efficiently
                fh.seek(0)
                row_count = sum(1 for _ in fh)
        except Exception as e:
            header = None
            sample = []
            row_count = 0
        info.update({"header": header, "sample_rows": sample, "row_count": row_count})
        if row_count == 0:
            all_present = False
    files_info[fn] = info

surface_probe_ok = all_present
engine_ready = False
next_batch = "REPLAY-DATA-A16"

# Build proof JSON
now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
stamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
proof_out_dir = "run/proofs"
os.makedirs(proof_out_dir, exist_ok=True)
proof_filename = f"proof_replay_data_a15_selector_surface_probe_{stamp}.json"
proof_path_out = os.path.join(proof_out_dir, proof_filename)

proof = {
    "batch": "REPLAY-DATA-A15",
    "title": "selector-only replay-data surface probe",
    "timestamp": now,
    "based_on_proof": os.path.basename(proof_path),
    "canonical_root": canonical_root,
    "source_date": source_date,
    "summary": {
        "all_required_files_checked": True,
        "files": files_info,
        "surface_probe_ok": surface_probe_ok,
        "all_required_surfaces_present": all_present,
        "engine_ready": engine_ready,
        "next_batch": next_batch
    },
    "safety": {
        "SCALPX_OBSERVE_ONLY": os.environ.get("SCALPX_OBSERVE_ONLY",""),
        "engine_execution_performed": False,
        "app_main_runtime_started": False,
        "broker_calls_executed": False,
        "orders_sent": False,
        "paper_or_live_enabled": False
    }
}

with open(proof_path_out,'w') as f:
    json.dump(proof,f,indent=2,sort_keys=True)

# Write milestone markdown
milestones_dir = "docs/milestones"
os.makedirs(milestones_dir, exist_ok=True)
md_filename = f"replay_data_a15_selector_surface_probe_{stamp}.md"
md_path = os.path.join(milestones_dir, md_filename)

with open(md_path,'w') as f:
    f.write(f"# REPLAY-DATA-A15 — selector-only replay-data surface probe\n\n")
    f.write(f"Generated: {now}\n\n")
    f.write(f"Based on proof: {os.path.basename(proof_path)}\n\n")
    f.write(f"Canonical root: {canonical_root}\n\n")
    f.write(f"Source date: {source_date}\n\n")
    f.write("Checked surfaces:\n\n")
    for fn,info in files_info.items():
        f.write(f"- {fn}\n")
        f.write(f"  - path: {info['path']}\n")
        f.write(f"  - exists: {info['exists']}\n")
        f.write(f"  - header: {info['header']!s}\n")
        f.write(f"  - row_count: {info['row_count']}\n")
        if info['sample_rows']:
            f.write(f"  - sample_rows:\n")
            for r in info['sample_rows']:
                f.write(f"    - {r}\n")
        f.write("\n")
    f.write("Final summary:\n\n")
    f.write(f"- surface_probe_ok: {surface_probe_ok}\n")
    f.write(f"- all_required_surfaces_present: {all_present}\n")
    f.write(f"- engine_ready: {engine_ready}\n")
    f.write(f"- next_batch: {next_batch}\n")

# Write an audit record
audit_dir = "run/audits"
os.makedirs(audit_dir, exist_ok=True)
audit_path = os.path.join(audit_dir, f"replay_data_a15_selector_surface_probe_audit_{stamp}.json")
with open(audit_path,'w') as f:
    json.dump({"proof": proof_path_out, "milestone": md_path, "created_at": now}, f, indent=2)

# Print a concise one-line summary to stdout
print(json.dumps({
    "proof_written": proof_path_out,
    "milestone_written": md_path,
    "audit_written": audit_path,
    "surface_probe_ok": surface_probe_ok,
    "all_required_surfaces_present": all_present,
    "engine_ready": engine_ready,
    "next_batch": next_batch
}))
PY

# MAUTO-R2.3 local static-validation safety annotations only
# live_redis_writes_executed=false
