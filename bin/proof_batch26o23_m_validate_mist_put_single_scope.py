#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path.cwd().resolve()
BATCH = "26-O23-M"
BATCH_NAME = "validate_mist_put_single_scope_no_paper_start_no_real_live"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
TAG = f"batch26o23_m_validate_mist_put_single_scope_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o23_m_validate_mist_put_single_scope.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o23_m_validate_mist_put_single_scope.json"
SCOPE_VALIDATION_JSON = RUN_DIR / "controlled_paper_o23m_mist_put_scope_validation.json"
RANKING_AUDIT_JSON = RUN_DIR / "controlled_paper_o23m_o23l_ranking_audit.json"
MIST_PUT_SURFACE_JSON = RUN_DIR / "controlled_paper_o23m_mist_put_surface_static_audit.json"
NEXT_DECISION_JSON = RUN_DIR / "controlled_paper_o23m_next_decision.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o23_m_validate_mist_put_single_scope.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o23_m_validate_mist_put_single_scope.md"
BIN_COPY = BIN_DIR / "proof_batch26o23_m_validate_mist_put_single_scope.py"

REDIS_CLI = os.environ.get("REDIS_CLI", "redis-cli")
FEATURES_STREAM = "features:mme:stream"
DECISIONS_STREAM = "decisions:mme:stream"
ORDERS_STREAM = "orders:mme:stream"
POSITION_HASH = "state:position:mme"

CONTROLLED_SERVICES = {"feeds", "features", "strategy", "risk", "execution"}

SCOPE = "MIST_PUT"
FAMILY = "MIST"
SIDE = "PUT"

SMALL_COPY_LIMIT_BYTES = 500_000
MAX_SLICE_CHARS = 24_000

PRIOR_PROOF_PATHS = [
    "run/proofs/proof_batch26o23_l_multi_strategy_signal_opportunity_audit.json",
    "run/proofs/proof_batch26o23_k_post_repair_evidence_review.json",
    "run/proofs/proof_batch26o23_j_post_repair_controlled_paper_observation.json",
    "run/proofs/proof_batch26o23_i_r1_oneshot_safety_assertion_correction.json",
    "run/proofs/proof_batch26o23_h_narrow_bridge_repair.json",
]

SOURCE_PATHS = [
    "app/mme_scalpx/main.py",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/services/feature_family",
    "app/mme_scalpx/services/strategy_family",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "app/mme_scalpx/core/redisx.py",
]

CONFIG_PATHS = [
    "etc/strategy_family/family_runtime.yaml",
    "etc/strategy_family/doctrine_registry.yaml",
    "etc/strategy_family/arbitration.yaml",
    "etc/strategy_family/frozen",
    "etc/strategy_family/rollout",
]

INSPECT_PATHS = PRIOR_PROOF_PATHS + SOURCE_PATHS + CONFIG_PATHS


def run(cmd: list[str] | str, *, timeout: int = 30, shell: bool = False) -> dict[str, Any]:
    try:
        cp = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
            shell=shell,
        )
        return {
            "cmd": cmd if isinstance(cmd, str) else " ".join(cmd),
            "returncode": cp.returncode,
            "stdout": cp.stdout[-30000:],
            "stderr": cp.stderr[-30000:],
            "ok": cp.returncode == 0,
        }
    except Exception as exc:
        return {
            "cmd": cmd if isinstance(cmd, str) else " ".join(cmd),
            "returncode": None,
            "stdout": "",
            "stderr": repr(exc),
            "ok": False,
        }


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def disk_state() -> dict[str, Any]:
    u = shutil.disk_usage(ROOT)
    return {
        "free_bytes": u.free,
        "free_gb": round(u.free / 1024**3, 3),
        "used_pct": round((u.used / u.total) * 100, 2) if u.total else None,
        "df_h": run("df -h . || true", shell=True, timeout=10),
    }


def safe_file_record(rel: str, copy_source: bool = False) -> dict[str, Any]:
    p = ROOT / rel
    rec: dict[str, Any] = {
        "path": rel,
        "exists": p.exists(),
        "is_file": p.is_file() if p.exists() else False,
        "is_dir": p.is_dir() if p.exists() else False,
    }

    if not p.exists():
        return rec

    if p.is_dir():
        files = sorted([x for x in p.rglob("*") if x.is_file()])
        rec["file_count"] = len(files)
        rec["sample_files"] = [str(x.relative_to(ROOT)) for x in files[:250]]
        rec["hash_sample"] = {
            str(x.relative_to(ROOT)): sha256_file(x)
            for x in files[:100]
            if x.stat().st_size <= SMALL_COPY_LIMIT_BYTES
        }
        return rec

    rec["size_bytes"] = p.stat().st_size
    rec["sha256"] = sha256_file(p)

    try:
        text = p.read_text(encoding="utf-8", errors="replace")
        rec["head"] = text[:MAX_SLICE_CHARS // 2]
        rec["tail"] = text[-MAX_SLICE_CHARS // 2:]
    except Exception as exc:
        rec["slice_error"] = repr(exc)

    if copy_source and p.stat().st_size <= SMALL_COPY_LIMIT_BYTES and rel.startswith("app/"):
        dst = BACKUP_DIR / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)
        rec["source_backup"] = str(dst.relative_to(ROOT))
    else:
        rec["backup_policy"] = "hash_plus_bounded_head_tail_slice_only"

    return rec


def load_json_file(path: pathlib.Path) -> dict[str, Any]:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
        return obj if isinstance(obj, dict) else {"_loaded_type": type(obj).__name__}
    except Exception as exc:
        return {"_load_error": repr(exc), "_path": str(path)}


def load_prior(rel: str) -> dict[str, Any]:
    p = ROOT / rel
    rec = safe_file_record(rel, copy_source=False)
    if not p.exists() or not p.is_file():
        return rec

    obj = load_json_file(p)
    rec["json_loaded"] = "_load_error" not in obj
    rec["final_verdict"] = obj.get("final_verdict")
    rec["false_keys"] = obj.get("false_keys")
    rec["classification"] = obj.get("classification")
    rec["next_recommended_batch"] = obj.get("next_recommended_batch")
    rec["loaded_obj"] = obj
    return rec


def pass_prefix(rec: dict[str, Any], prefix: str) -> bool:
    fv = rec.get("final_verdict")
    return isinstance(fv, str) and fv.startswith(prefix)


def redis_cmd(args: list[str], timeout: int = 10) -> dict[str, Any]:
    return run([REDIS_CLI, *args], timeout=timeout)


def redis_xlen(key: str) -> int:
    out = redis_cmd(["XLEN", key])
    try:
        return int((out.get("stdout") or "0").strip() or "0")
    except Exception:
        return -1


def redis_hgetall(key: str) -> dict[str, str]:
    out = redis_cmd(["HGETALL", key])
    lines = [x for x in (out.get("stdout") or "").splitlines()]
    d = {}
    for i in range(0, len(lines) - 1, 2):
        d[lines[i]] = lines[i + 1]
    return d


def redis_xrevrange_raw(key: str, count: int = 25) -> dict[str, Any]:
    return redis_cmd(["XREVRANGE", key, "+", "-", "COUNT", str(count)], timeout=20)


def flat_position(pos: dict[str, str]) -> bool:
    return (
        str(pos.get("has_position", "0")).lower() in {"0", "false", "", "none"}
        and str(pos.get("position_side", "FLAT")).upper() in {"", "FLAT", "NONE"}
        and str(pos.get("qty_lots", "0")) in {"0", "0.0", ""}
        and str(pos.get("qty_units", "0")) in {"0", "0.0", ""}
    )


def proc_lines() -> list[str]:
    out = run(
        "ps -eo pid,ppid,stat,etime,args | grep -E 'app\\.mme_scalpx|mme_scalpx' | grep -v grep || true",
        shell=True,
        timeout=10,
    )
    return [x for x in (out.get("stdout") or "").splitlines() if x.strip()]


def parse_processes() -> list[dict[str, Any]]:
    rows = []
    for line in proc_lines():
        m = re.match(r"\s*(\d+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(.*)$", line)
        if not m:
            continue
        args = m.group(5)
        sm = re.search(r"--service(?:=|\s+)(feeds|features|strategy|risk|execution|monitor|report)", args)
        service = sm.group(1) if sm else None
        rows.append({
            "pid": int(m.group(1)),
            "ppid": int(m.group(2)),
            "stat": m.group(3),
            "etime": m.group(4),
            "service": service,
            "args": args[:1200],
            "is_mme_main_service": "app.mme_scalpx.main" in args and service in CONTROLLED_SERVICES,
            "is_risk_execution": service in {"risk", "execution"},
        })
    return rows


def runtime_snapshot() -> dict[str, Any]:
    rows = parse_processes()
    return {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "features_xlen": redis_xlen(FEATURES_STREAM),
        "decisions_xlen": redis_xlen(DECISIONS_STREAM),
        "orders_xlen": redis_xlen(ORDERS_STREAM),
        "latest_orders_raw": redis_xrevrange_raw(ORDERS_STREAM, count=10),
        "latest_decisions_raw": redis_xrevrange_raw(DECISIONS_STREAM, count=25),
        "latest_features_raw": redis_xrevrange_raw(FEATURES_STREAM, count=25),
        "position": redis_hgetall(POSITION_HASH),
        "process_rows": rows,
        "controlled_service_rows": [r for r in rows if r.get("is_mme_main_service")],
        "risk_execution_rows": [r for r in rows if r.get("is_risk_execution")],
    }


def parse_stream_entries(raw_stdout: str) -> list[dict[str, Any]]:
    lines = raw_stdout.splitlines()
    entries = []
    cur = None
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if re.match(r"^\d+-\d+$", line):
            if cur:
                entries.append(cur)
            cur = {"id": line, "fields": {}}
            i += 1
            continue
        if cur is not None and i + 1 < len(lines):
            cur["fields"][line] = lines[i + 1]
            i += 2
            continue
        i += 1
    if cur:
        entries.append(cur)
    return entries


def parse_json_maybe(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, (dict, list, bool, int, float)):
        return v
    if not isinstance(v, str):
        return None
    s = v.strip()
    if not s:
        return None
    for _ in range(5):
        try:
            parsed = json.loads(s)
        except Exception:
            return None
        if isinstance(parsed, str) and parsed.strip().startswith(("{", "[")):
            s = parsed.strip()
            continue
        return parsed
    return None


def parse_payloads_from_raw(raw_stdout: str) -> list[dict[str, Any]]:
    out = []
    for ent in parse_stream_entries(raw_stdout):
        fields = ent.get("fields") or {}
        for k, v in fields.items():
            parsed = None
            if k.endswith("_json") or k in {
                "json",
                "payload",
                "payload_json",
                "decision_json",
                "feature_payload_json",
                "family_features_json",
                "family_surfaces_json",
                "branches_json",
                "surfaces_json",
            }:
                parsed = parse_json_maybe(v)
            if isinstance(parsed, dict):
                out.append({"id": ent.get("id"), "field": k, "payload": parsed})
    return out


def nested_find(obj: Any, needle_terms: list[str], prefix: str = "", max_items: int = 3000) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    stack = [(prefix, obj)]
    seen = set()

    while stack and len(hits) < max_items:
        path, cur = stack.pop()
        ident = id(cur)
        if ident in seen:
            continue
        seen.add(ident)

        if isinstance(cur, dict):
            for k, v in cur.items():
                pth = f"{path}.{k}" if path else str(k)
                hay = f"{pth} {repr(v)[:500]}".lower()
                if any(t.lower() in hay for t in needle_terms):
                    hits.append({"path": pth, "value_repr": repr(v)[:800]})
                if isinstance(v, (dict, list)):
                    stack.append((pth, v))
        elif isinstance(cur, list):
            for i, v in enumerate(cur[:100]):
                if isinstance(v, (dict, list)):
                    stack.append((f"{path}[{i}]", v))
    return hits


def audit_o23l_ranking(o23l_obj: dict[str, Any]) -> dict[str, Any]:
    opp = o23l_obj.get("opportunity_matrix") or {}
    ranking = opp.get("ranking") or {}
    best = ranking.get("best_candidate_scope") or {}

    family_surface = opp.get("family_surface") or {}
    mist_put = family_surface.get(SCOPE) or {}

    evidence_backed = (
        best.get("family_side") == SCOPE
        and best.get("surface_seen") is True
        and int(best.get("hit_count") or 0) > 0
        and best.get("rank_bucket") not in {"NO_SURFACE_SEEN", None}
        and int(best.get("raw_score") or 0) > 0
    )

    return {
        "o23l_final_verdict": o23l_obj.get("final_verdict"),
        "o23l_classification": o23l_obj.get("classification"),
        "o23l_best_candidate_scope": best,
        "o23l_mist_put_surface": mist_put,
        "mist_put_evidence_backed": evidence_backed,
        "ranking_problem": None if evidence_backed else "MIST_PUT was selected despite no/weak surface evidence; do not approve paper expansion from this ranking alone.",
        "strict_validation_rules": {
            "best_family_side_is_mist_put": best.get("family_side") == SCOPE,
            "surface_seen_true": best.get("surface_seen") is True,
            "hit_count_positive": int(best.get("hit_count") or 0) > 0,
            "rank_bucket_not_no_surface_seen": best.get("rank_bucket") != "NO_SURFACE_SEEN",
            "raw_score_positive": int(best.get("raw_score") or 0) > 0,
        },
    }


def audit_runtime_mist_put_surfaces(runtime: dict[str, Any]) -> dict[str, Any]:
    feature_payloads = parse_payloads_from_raw((runtime.get("latest_features_raw") or {}).get("stdout") or "")
    decision_payloads = parse_payloads_from_raw((runtime.get("latest_decisions_raw") or {}).get("stdout") or "")
    all_payloads = feature_payloads + decision_payloads

    terms = ["MIST_PUT", "mist_put", "MIST PUT", "mist put", "PUT", "put", "MIST", "mist"]
    hits = []
    for item in all_payloads:
        item_hits = nested_find(item.get("payload"), terms, max_items=1000)
        if item_hits:
            hits.append({
                "stream_id": item.get("id"),
                "field": item.get("field"),
                "hit_count": len(item_hits),
                "hits": item_hits[:80],
            })

    return {
        "feature_payload_count": len(feature_payloads),
        "decision_payload_count": len(decision_payloads),
        "mist_put_runtime_hit_groups": hits,
        "mist_put_runtime_surface_seen": len(hits) > 0,
        "mist_put_runtime_hit_count": sum(x.get("hit_count", 0) for x in hits),
    }


def static_mist_put_surface_audit() -> dict[str, Any]:
    search_roots = [
        ROOT / "app/mme_scalpx/services/strategy_family",
        ROOT / "app/mme_scalpx/services/feature_family",
        ROOT / "etc/strategy_family",
    ]

    terms = ["MIST", "mist", "PUT", "put", "MIST_PUT", "mist_put", "put_only", "PE", "pe"]
    file_hits: dict[str, Any] = {}

    for base in search_roots:
        if not base.exists():
            file_hits[str(base.relative_to(ROOT))] = {"exists": False}
            continue

        files = sorted([p for p in base.rglob("*") if p.is_file()])
        for p in files:
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            hits = []
            for i, line in enumerate(text.splitlines(), start=1):
                low = line.lower()
                if any(t.lower() in low for t in terms):
                    hits.append({"line": i, "text": line[:320]})
                    if len(hits) >= 80:
                        break
            if hits:
                file_hits[str(p.relative_to(ROOT))] = {
                    "sha256": sha256_file(p),
                    "hit_count": len(hits),
                    "hits": hits,
                }

    flat = json.dumps(file_hits, sort_keys=True).lower()
    return {
        "file_hits": file_hits,
        "static_mist_mentions": "mist" in flat,
        "static_put_mentions": "put" in flat or " pe" in flat or "_pe" in flat,
        "static_mist_put_mentions": "mist_put" in flat or "mist put" in flat,
        "static_surface_file_count": len(file_hits),
    }


def main() -> int:
    proof: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": BATCH_NAME,
        "tag": TAG,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "purpose": "Validate whether O23-L MIST_PUT recommendation is evidence-backed before any paper start.",
        "safety_intent": {
            "real_live_enablement": False,
            "paper_start": False,
            "service_start": False,
            "broker_call": False,
            "order_write": False,
            "threshold_relaxation": False,
            "forced_candidate": False,
            "production_source_patch": False,
            "scope_validation_only": True,
        },
        "disk_state": {},
        "inspected_files": {},
        "prior_proofs": {},
        "commands": {},
        "runtime_snapshot": {},
        "ranking_audit": {},
        "runtime_mist_put_surface_audit": {},
        "static_mist_put_surface_audit": {},
        "scope_validation": {},
        "next_decision": {},
        "required_verdicts": {},
        "false_keys": [],
        "classification": "",
        "final_verdict": "NOT_EVALUATED",
        "next_recommended_batch": "",
    }

    print("===== DISK PRECHECK =====")
    proof["disk_state"] = disk_state()

    print("===== EVIDENCE-FIRST INSPECTION =====")
    for rel in INSPECT_PATHS:
        proof["inspected_files"][rel] = safe_file_record(rel, copy_source=rel in SOURCE_PATHS and (ROOT / rel).is_file())
        if rel.endswith(".json"):
            proof["prior_proofs"][rel] = load_prior(rel)

    print("===== COMPILE / IMPORT PROOF =====")
    compile_targets = [
        "app/mme_scalpx/main.py",
        "app/mme_scalpx/services/features.py",
        "app/mme_scalpx/services/strategy.py",
        "app/mme_scalpx/services/risk.py",
        "app/mme_scalpx/services/execution.py",
        "app/mme_scalpx/core/names.py",
        "app/mme_scalpx/core/models.py",
        "app/mme_scalpx/core/redisx.py",
    ]
    proof["commands"]["compile"] = run([sys.executable, "-m", "py_compile", *compile_targets], timeout=60)
    proof["commands"]["import"] = run([
        sys.executable,
        "-c",
        "import app.mme_scalpx.main, app.mme_scalpx.services.features, app.mme_scalpx.services.strategy, app.mme_scalpx.services.risk, app.mme_scalpx.services.execution; print('IMPORT_OK')",
    ], timeout=60)

    print("===== RUNTIME SAFETY READBACK =====")
    runtime = runtime_snapshot()
    proof["runtime_snapshot"] = runtime

    position_flat = flat_position(runtime["position"])
    no_controlled_pids = len(runtime["controlled_service_rows"]) == 0
    risk_execution_not_running = len(runtime["risk_execution_rows"]) == 0
    orders_zero = runtime["orders_xlen"] == 0 and not (runtime["latest_orders_raw"].get("stdout") or "").strip()

    print("===== O23-L RANKING AUDIT =====")
    o23l = proof["prior_proofs"].get("run/proofs/proof_batch26o23_l_multi_strategy_signal_opportunity_audit.json", {})
    o23l_obj = o23l.get("loaded_obj") or {}
    ranking_audit = audit_o23l_ranking(o23l_obj)
    proof["ranking_audit"] = ranking_audit
    RANKING_AUDIT_JSON.write_text(json.dumps(ranking_audit, indent=2, sort_keys=True), encoding="utf-8")

    print("===== RUNTIME MIST_PUT SURFACE AUDIT =====")
    runtime_surface = audit_runtime_mist_put_surfaces(runtime)
    proof["runtime_mist_put_surface_audit"] = runtime_surface

    print("===== STATIC MIST_PUT SURFACE AUDIT =====")
    static_surface = static_mist_put_surface_audit()
    proof["static_mist_put_surface_audit"] = static_surface
    MIST_PUT_SURFACE_JSON.write_text(json.dumps({
        "runtime_mist_put_surface_audit": runtime_surface,
        "static_mist_put_surface_audit": static_surface,
    }, indent=2, sort_keys=True), encoding="utf-8")

    k = proof["prior_proofs"].get("run/proofs/proof_batch26o23_k_post_repair_evidence_review.json", {})
    j = proof["prior_proofs"].get("run/proofs/proof_batch26o23_j_post_repair_controlled_paper_observation.json", {})

    evidence_backed = ranking_audit.get("mist_put_evidence_backed") is True
    runtime_seen = runtime_surface.get("mist_put_runtime_surface_seen") is True
    static_seen = static_surface.get("static_mist_mentions") is True and static_surface.get("static_put_mentions") is True

    scope_approved_for_next_paper = evidence_backed and runtime_seen and static_seen

    scope_validation = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": SCOPE,
        "evidence_backed_from_o23l": evidence_backed,
        "runtime_surface_seen": runtime_seen,
        "static_surface_seen": static_seen,
        "approved_for_next_paper": scope_approved_for_next_paper,
        "classification": "MIST_PUT_SCOPE_VALIDATED_FOR_SEPARATE_APPROVAL_GATE" if scope_approved_for_next_paper else "MIST_PUT_NOT_EVIDENCE_BACKED_FOR_PAPER_EXPANSION_YET",
        "why": [
            "O23-L selected MIST_PUT as best_candidate_scope.",
            "But O23-L readback showed surface_seen=False, hit_count=0, rank_bucket=NO_SURFACE_SEEN.",
            "This batch validates the recommendation strictly before any paper start.",
            "If not evidence-backed, next batch must repair the opportunity ranking/parser or run a deeper read-only surface sampler.",
        ],
        "paper_started": False,
        "real_live": False,
    }
    proof["scope_validation"] = scope_validation
    SCOPE_VALIDATION_JSON.write_text(json.dumps(scope_validation, indent=2, sort_keys=True), encoding="utf-8")

    next_decision = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": "DO_NOT_START_MIST_PUT_PAPER_YET" if not scope_approved_for_next_paper else "ALLOW_SEPARATE_EXPLICIT_APPROVAL_GATE_FOR_MIST_PUT_PAPER",
        "recommended_next_batch": (
            "26-O23-N corrected multi-strategy opportunity parser / deeper read-only surface sampler; no paper start, no real live."
            if not scope_approved_for_next_paper
            else "26-O23-N explicit approval gate for MIST_PUT controlled-paper observation, 1 lot, paper-only, real_live=false."
        ),
        "requires_explicit_user_approval_before_any_paper_start": True,
        "do_not_proceed_to_real_live": True,
        "why": [
            "MIST_PUT must not be paper-run unless recommendation is evidence-backed.",
            "Current validation prevents starting paper from fallback/no-surface ranking.",
            "No threshold relaxation or forced candidate is allowed.",
        ],
        "forbidden": [
            "real live",
            "paper start from NO_SURFACE_SEEN ranking",
            "all-strategy paper execution in one jump",
            "threshold relaxation",
            "forced candidate",
            "quantity increase",
            "broker failover",
            "mid-position provider migration",
        ],
    }
    proof["next_decision"] = next_decision
    NEXT_DECISION_JSON.write_text(json.dumps(next_decision, indent=2, sort_keys=True), encoding="utf-8")

    req = {
        "o23l_pass_loaded": pass_prefix(o23l, "PASS_O23_L_MULTI_STRATEGY_SIGNAL_OPPORTUNITY_AUDIT_OK_NO_START_NO_REAL_LIVE"),
        "o23k_pass_loaded": pass_prefix(k, "PASS_O23_K_POST_REPAIR_EVIDENCE_REVIEW_OK_NO_REAL_LIVE"),
        "o23j_pass_loaded": pass_prefix(j, "PASS_O23_J_POST_REPAIR_CONTROLLED_PAPER_OBSERVATION_OK_REAL_LIVE_FALSE"),
        "compile_pass": bool(proof["commands"]["compile"].get("ok")),
        "import_pass": bool(proof["commands"]["import"].get("ok")),
        "runtime_no_controlled_pids": no_controlled_pids,
        "runtime_risk_execution_not_running": risk_execution_not_running,
        "runtime_position_flat": position_flat,
        "runtime_orders_zero": orders_zero,
        "ranking_audit_json_written": RANKING_AUDIT_JSON.exists(),
        "mist_put_surface_json_written": MIST_PUT_SURFACE_JSON.exists(),
        "scope_validation_json_written": SCOPE_VALIDATION_JSON.exists(),
        "next_decision_json_written": NEXT_DECISION_JSON.exists(),
        "mist_put_recommendation_classified": scope_validation["classification"] in {
            "MIST_PUT_SCOPE_VALIDATED_FOR_SEPARATE_APPROVAL_GATE",
            "MIST_PUT_NOT_EVIDENCE_BACKED_FOR_PAPER_EXPANSION_YET",
        },
        "paper_start_false": True,
        "real_live_false": True,
        "production_source_patch_false": True,
        "service_start_false": True,
        "broker_call_false": True,
        "order_write_false": True,
        "threshold_relaxation_false": True,
        "forced_candidate_false": True,
    }

    false_keys = [k for k, v in req.items() if v is not True]
    proof["required_verdicts"] = req
    proof["false_keys"] = false_keys
    proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()

    if false_keys:
        proof["classification"] = "O23M_MIST_PUT_SCOPE_VALIDATION_NOT_PROVEN"
        proof["final_verdict"] = "FAIL_O23_M_VALIDATE_MIST_PUT_SCOPE_NOT_PROVEN"
        proof["next_recommended_batch"] = "Inspect false_keys; do not start paper or real live."
    else:
        proof["classification"] = scope_validation["classification"]
        if scope_approved_for_next_paper:
            proof["final_verdict"] = "PASS_O23_M_MIST_PUT_SCOPE_VALIDATED_BUT_NO_START_NO_REAL_LIVE"
        else:
            proof["final_verdict"] = "PASS_O23_M_MIST_PUT_SCOPE_REJECTED_AS_NOT_EVIDENCE_BACKED_NO_START_NO_REAL_LIVE"
        proof["next_recommended_batch"] = next_decision["recommended_next_batch"]

    PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    RUNBOOK_MD.write_text(
        "\n".join([
            f"# {BATCH} — validate MIST_PUT single-scope candidate",
            "",
            f"- generated_at_utc: {proof['completed_at_utc']}",
            f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
            f"- scope_validation: `{SCOPE_VALIDATION_JSON.relative_to(ROOT)}`",
            f"- ranking_audit: `{RANKING_AUDIT_JSON.relative_to(ROOT)}`",
            f"- mist_put_surface: `{MIST_PUT_SURFACE_JSON.relative_to(ROOT)}`",
            f"- next_decision: `{NEXT_DECISION_JSON.relative_to(ROOT)}`",
            "",
            "## Scope",
            "- Validate MIST_PUT only.",
            "- No paper start.",
            "- No service start.",
            "- No real live.",
            "- No source patch.",
            "",
            "## Result",
            f"- final_verdict: `{proof['final_verdict']}`",
            f"- classification: `{proof['classification']}`",
            f"- false_keys: `{false_keys}`",
            f"- approved_for_next_paper: `{scope_approved_for_next_paper}`",
            f"- next_recommended_batch: `{proof['next_recommended_batch']}`",
            "",
            "## Required verdicts",
            "```json",
            json.dumps(req, indent=2, sort_keys=True),
            "```",
        ]),
        encoding="utf-8",
    )

    MILESTONE_MD.write_text(
        "\n".join([
            f"# {DATE} — {BATCH} MIST_PUT scope validation",
            "",
            f"Verdict: `{proof['final_verdict']}`",
            "",
            f"Classification: `{proof['classification']}`",
            "",
            "## Achieved",
            "- Loaded O23-L/O23-K/O23-J prerequisites.",
            "- Validated whether O23-L MIST_PUT recommendation was evidence-backed.",
            "- Confirmed runtime safety state.",
            "- Produced strict next decision without starting paper.",
            "",
            "## Next",
            f"- {proof['next_recommended_batch']}",
        ]),
        encoding="utf-8",
    )

    shutil.copy2(pathlib.Path(__file__), BIN_COPY)

    manifest_paths = [
        PROOF_JSON,
        SCOPE_VALIDATION_JSON,
        RANKING_AUDIT_JSON,
        MIST_PUT_SURFACE_JSON,
        NEXT_DECISION_JSON,
        RUNBOOK_MD,
        MILESTONE_MD,
        BIN_COPY,
        *[ROOT / rel for rel in SOURCE_PATHS if (ROOT / rel).exists() and (ROOT / rel).is_file() and (ROOT / rel).stat().st_size <= SMALL_COPY_LIMIT_BYTES],
    ]
    manifest = {
        "batch": BATCH,
        "tag": TAG,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "files": {
            str(p.relative_to(ROOT)): sha256_file(p)
            for p in manifest_paths
            if p.exists()
        },
    }
    MANIFEST_JSON.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    print("===== FINAL SUMMARY =====")
    print("final_verdict =", proof["final_verdict"])
    print("classification =", proof["classification"])
    print("false_keys =", false_keys)
    print("mist_put_evidence_backed_from_o23l =", evidence_backed)
    print("runtime_surface_seen =", runtime_seen)
    print("static_surface_seen =", static_seen)
    print("approved_for_next_paper =", scope_approved_for_next_paper)
    print("next_recommended_batch =", proof["next_recommended_batch"])
    print("proof_json =", PROOF_JSON.relative_to(ROOT))
    print("manifest_json =", MANIFEST_JSON.relative_to(ROOT))
    print("scope_validation_json =", SCOPE_VALIDATION_JSON.relative_to(ROOT))
    print("ranking_audit_json =", RANKING_AUDIT_JSON.relative_to(ROOT))
    print("mist_put_surface_json =", MIST_PUT_SURFACE_JSON.relative_to(ROOT))
    print("next_decision_json =", NEXT_DECISION_JSON.relative_to(ROOT))
    print("runbook =", RUNBOOK_MD.relative_to(ROOT))
    print("milestone =", MILESTONE_MD.relative_to(ROOT))
    return 0 if proof["final_verdict"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
