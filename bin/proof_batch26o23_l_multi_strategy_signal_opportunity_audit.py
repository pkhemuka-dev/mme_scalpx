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
BATCH = "26-O23-L"
BATCH_NAME = "multi_strategy_signal_opportunity_audit_read_only_paper_disabled_no_real_live"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
TAG = f"batch26o23_l_multi_strategy_signal_opportunity_audit_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o23_l_multi_strategy_signal_opportunity_audit.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o23_l_multi_strategy_signal_opportunity_audit.json"
OPPORTUNITY_JSON = RUN_DIR / "controlled_paper_o23l_multi_strategy_opportunity_matrix.json"
SURFACE_REVIEW_JSON = RUN_DIR / "controlled_paper_o23l_family_surface_review.json"
REDIS_REVIEW_JSON = RUN_DIR / "controlled_paper_o23l_redis_latest_surface_review.json"
NEXT_DECISION_JSON = RUN_DIR / "controlled_paper_o23l_next_decision.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o23_l_multi_strategy_signal_opportunity_audit.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o23_l_multi_strategy_signal_opportunity_audit.md"
BIN_COPY = BIN_DIR / "proof_batch26o23_l_multi_strategy_signal_opportunity_audit.py"

REDIS_CLI = os.environ.get("REDIS_CLI", "redis-cli")
FEATURES_STREAM = "features:mme:stream"
DECISIONS_STREAM = "decisions:mme:stream"
ORDERS_STREAM = "orders:mme:stream"
POSITION_HASH = "state:position:mme"

CONTROLLED_SERVICES = {"feeds", "features", "strategy", "risk", "execution"}

FAMILIES = ["MIST", "MISB", "MISC", "MISR", "MISO"]
SIDES = ["CALL", "PUT"]
FAMILY_SIDES = [f"{fam}_{side}" for fam in FAMILIES for side in SIDES]

SMALL_COPY_LIMIT_BYTES = 500_000
MAX_SLICE_CHARS = 24_000

PRIOR_PROOF_PATHS = [
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
        rec["sample_files"] = [str(x.relative_to(ROOT)) for x in files[:200]]
        rec["hash_sample"] = {
            str(x.relative_to(ROOT)): sha256_file(x)
            for x in files[:80]
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
    rec["sample_count"] = len(obj.get("samples") or []) if isinstance(obj.get("samples"), list) else obj.get("sample_count")
    rec["required_verdicts"] = obj.get("required_verdicts") if isinstance(obj.get("required_verdicts"), dict) else {}
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


def nested_walk(obj: Any, prefix: str = "", max_items: int = 2000) -> list[dict[str, Any]]:
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
                lk = str(k).lower()
                if any(tok in lk for tok in [
                    "mist", "misb", "misc", "misr", "miso", "call", "put",
                    "candidate", "eligible", "valid", "ready", "blocked",
                    "reason", "score", "confidence", "activation", "surface",
                    "family", "branch", "gate", "provider", "dhan",
                    "consumer_view", "data_valid", "safe_to_consume", "structural_valid",
                ]):
                    hits.append({"path": pth, "value_repr": repr(v)[:500]})
                if isinstance(v, (dict, list)):
                    stack.append((pth, v))
        elif isinstance(cur, list):
            for i, v in enumerate(cur[:80]):
                if isinstance(v, (dict, list)):
                    stack.append((f"{path}[{i}]", v))
    return hits


def family_key_variants(family: str, side: str) -> list[str]:
    fam = family.lower()
    side_l = side.lower()
    return [
        f"{family}_{side}",
        f"{family}:{side}",
        f"{family}.{side}",
        f"{family} {side}",
        f"{fam}_{side_l}",
        f"{fam}:{side_l}",
        f"{fam}.{side_l}",
        f"{fam} {side_l}",
        f"{family}{side}",
        f"{fam}{side_l}",
    ]


def extract_family_side_surface(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    surface: dict[str, Any] = {fs: {"hits": [], "score": 0, "status": "NOT_SEEN"} for fs in FAMILY_SIDES}

    for item in payloads:
        payload = item.get("payload") or {}
        flat = json.dumps(payload, sort_keys=True, default=str).lower()
        nested_hits = nested_walk(payload, max_items=500)

        for family in FAMILIES:
            for side in SIDES:
                fs = f"{family}_{side}"
                variants = family_key_variants(family, side)
                text_present = any(v.lower() in flat for v in variants)

                relevant_nested = [
                    h for h in nested_hits
                    if family.lower() in h["path"].lower() or family.lower() in h["value_repr"].lower()
                    or side.lower() in h["path"].lower() or side.lower() in h["value_repr"].lower()
                ][:80]

                if text_present or relevant_nested:
                    score = 0
                    joined = json.dumps(relevant_nested, sort_keys=True).lower() + " " + flat[:5000]

                    positive_terms = [
                        "candidate", "eligible", "valid", "ready", "pass", "accepted",
                        "triggered", "confirmed", "detected", "activation", "score",
                        "confidence", "context_pass", "provider_ready"
                    ]
                    negative_terms = [
                        "blocked", "false", "invalid", "stale", "missing", "not_ready",
                        "fail", "hold", "no_candidate", "disabled"
                    ]

                    for t in positive_terms:
                        if t in joined:
                            score += 1
                    for t in negative_terms:
                        if t in joined:
                            score -= 1

                    surface[fs]["hits"].append({
                        "stream_id": item.get("id"),
                        "field": item.get("field"),
                        "text_present": text_present,
                        "score_delta": score,
                        "nested_hits": relevant_nested[:40],
                    })
                    surface[fs]["score"] += score
                    surface[fs]["status"] = "SEEN"

    for fs, rec in surface.items():
        if rec["status"] != "SEEN":
            rec["rank_bucket"] = "NO_SURFACE_SEEN"
        elif rec["score"] >= 3:
            rec["rank_bucket"] = "HIGHER_OPPORTUNITY_SURFACE"
        elif rec["score"] >= 1:
            rec["rank_bucket"] = "SOME_OPPORTUNITY_SURFACE"
        elif rec["score"] == 0:
            rec["rank_bucket"] = "NEUTRAL_SURFACE"
        else:
            rec["rank_bucket"] = "BLOCKED_OR_LOW_OPPORTUNITY_SURFACE"

    return surface


def source_family_surface_review() -> dict[str, Any]:
    review: dict[str, Any] = {
        "source_presence": {},
        "family_side_mentions": {},
        "strategy_family_files": [],
        "feature_family_files": [],
        "config_files": [],
    }

    for base_rel in ["app/mme_scalpx/services/strategy_family", "app/mme_scalpx/services/feature_family"]:
        base = ROOT / base_rel
        if not base.exists():
            review["source_presence"][base_rel] = {"exists": False}
            continue

        files = sorted([p for p in base.rglob("*.py") if p.is_file()])
        key = "strategy_family_files" if "strategy_family" in base_rel else "feature_family_files"
        review[key] = [str(p.relative_to(ROOT)) for p in files]

        for p in files:
            text = p.read_text(encoding="utf-8", errors="replace")
            rel = str(p.relative_to(ROOT))
            review["family_side_mentions"][rel] = {}
            for fs in FAMILY_SIDES:
                family, side = fs.split("_")
                hits = []
                for i, line in enumerate(text.splitlines(), 1):
                    low = line.lower()
                    if family.lower() in low or side.lower() in low:
                        hits.append({"line": i, "text": line[:280]})
                        if len(hits) >= 40:
                            break
                review["family_side_mentions"][rel][fs] = hits

    config_base = ROOT / "etc" / "strategy_family"
    if config_base.exists():
        files = sorted([p for p in config_base.rglob("*") if p.is_file()])
        review["config_files"] = [str(p.relative_to(ROOT)) for p in files]
        for p in files[:80]:
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            rel = str(p.relative_to(ROOT))
            review["family_side_mentions"][rel] = {}
            for fs in FAMILY_SIDES:
                family, side = fs.split("_")
                hits = []
                for i, line in enumerate(text.splitlines(), 1):
                    low = line.lower()
                    if family.lower() in low or side.lower() in low:
                        hits.append({"line": i, "text": line[:280]})
                        if len(hits) >= 40:
                            break
                review["family_side_mentions"][rel][fs] = hits

    return review


def rank_next_family_side(surface: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for fs, rec in surface.items():
        family, side = fs.split("_")
        score = int(rec.get("score") or 0)

        # Keep MISO conservative until Dhan context readiness is explicitly proven fresh.
        conservative_penalty = 0
        caution = []
        if family == "MISO":
            conservative_penalty -= 3
            caution.append("MISO requires Dhan selected-option + Dhan option-context freshness before paper expansion.")

        # Prefer next single-scope controlled paper that is not already the current tested MIST_CALL.
        already_current = fs == "MIST_CALL"
        if already_current:
            conservative_penalty -= 2
            caution.append("MIST_CALL already tested in O23-J; prefer another family/side only after evidence.")

        total = score + conservative_penalty

        rows.append({
            "family_side": fs,
            "family": family,
            "side": side,
            "raw_score": score,
            "adjusted_score": total,
            "rank_bucket": rec.get("rank_bucket"),
            "surface_seen": rec.get("status") == "SEEN",
            "hit_count": len(rec.get("hits") or []),
            "caution": caution,
        })

    rows.sort(key=lambda r: (r["adjusted_score"], r["raw_score"], r["hit_count"]), reverse=True)

    best = rows[0] if rows else None
    return {
        "ranked": rows,
        "best_candidate_scope": best,
        "recommendation": (
            "Use O23-M to validate exact next one-family/side scope before any paper start."
            if best else
            "No family/side opportunity surface found; inspect feature/strategy publisher first."
        ),
    }


def main() -> int:
    proof: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": BATCH_NAME,
        "tag": TAG,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "purpose": "Read-only multi-strategy signal-opportunity audit after safe no-trade O23-J/O23-K.",
        "safety_intent": {
            "real_live_enablement": False,
            "paper_restart": False,
            "service_start": False,
            "broker_call": False,
            "order_write": False,
            "threshold_relaxation": False,
            "forced_candidate": False,
            "production_source_patch": False,
            "read_only_opportunity_audit": True,
        },
        "disk_state": {},
        "inspected_files": {},
        "prior_proofs": {},
        "commands": {},
        "runtime_snapshot": {},
        "redis_review": {},
        "surface_review": {},
        "opportunity_matrix": {},
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

    print("===== REDIS LATEST SURFACE REVIEW =====")
    feature_payloads = parse_payloads_from_raw((runtime.get("latest_features_raw") or {}).get("stdout") or "")
    decision_payloads = parse_payloads_from_raw((runtime.get("latest_decisions_raw") or {}).get("stdout") or "")
    all_payloads = feature_payloads + decision_payloads

    redis_review = {
        "features_xlen": runtime["features_xlen"],
        "decisions_xlen": runtime["decisions_xlen"],
        "orders_xlen": runtime["orders_xlen"],
        "feature_payload_count": len(feature_payloads),
        "decision_payload_count": len(decision_payloads),
        "feature_payload_fields": [{"id": x.get("id"), "field": x.get("field")} for x in feature_payloads[:20]],
        "decision_payload_fields": [{"id": x.get("id"), "field": x.get("field")} for x in decision_payloads[:20]],
        "nested_family_hits": nested_walk([x.get("payload") for x in all_payloads], max_items=2500),
    }
    proof["redis_review"] = redis_review
    REDIS_REVIEW_JSON.write_text(json.dumps(redis_review, indent=2, sort_keys=True), encoding="utf-8")

    print("===== SOURCE / CONFIG FAMILY SURFACE REVIEW =====")
    surface_review = source_family_surface_review()
    proof["surface_review"] = surface_review
    SURFACE_REVIEW_JSON.write_text(json.dumps(surface_review, indent=2, sort_keys=True), encoding="utf-8")

    print("===== OPPORTUNITY MATRIX =====")
    family_surface = extract_family_side_surface(all_payloads)
    ranking = rank_next_family_side(family_surface)
    opportunity = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "family_surface": family_surface,
        "ranking": ranking,
        "interpretation": [
            "This is read-only and paper-disabled.",
            "No service was started.",
            "No order was written.",
            "Ranking is advisory only; it does not approve paper expansion.",
            "Next batch must validate one chosen family/side before any controlled-paper start.",
        ],
    }
    proof["opportunity_matrix"] = opportunity
    OPPORTUNITY_JSON.write_text(json.dumps(opportunity, indent=2, sort_keys=True), encoding="utf-8")

    k = proof["prior_proofs"].get("run/proofs/proof_batch26o23_k_post_repair_evidence_review.json", {})
    j = proof["prior_proofs"].get("run/proofs/proof_batch26o23_j_post_repair_controlled_paper_observation.json", {})

    best = (ranking.get("best_candidate_scope") or {}).get("family_side")
    next_batch = "26-O23-M validate next single-family/side paper scope, still no paper start, no real live."
    if best:
        next_batch = f"26-O23-M validate {best} as next single-family/side paper scope, still no paper start, no real live."

    next_decision = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": "RUN_O23_M_SINGLE_SCOPE_VALIDATION_NEXT",
        "recommended_next_batch": next_batch,
        "best_candidate_scope_from_readonly_audit": best,
        "do_not_start_paper_yet": True,
        "do_not_proceed_to_real_live": True,
        "why": [
            "O23-L is read-only and paper-disabled.",
            "It ranks possible family/side scopes from existing latest surfaces.",
            "Before paper-running another strategy, validate exactly one scope and its safety gates.",
        ],
        "forbidden": [
            "real live",
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
        "o23k_pass_loaded": pass_prefix(k, "PASS_O23_K_POST_REPAIR_EVIDENCE_REVIEW_OK_NO_REAL_LIVE"),
        "o23j_pass_loaded": pass_prefix(j, "PASS_O23_J_POST_REPAIR_CONTROLLED_PAPER_OBSERVATION_OK_REAL_LIVE_FALSE"),
        "compile_pass": bool(proof["commands"]["compile"].get("ok")),
        "import_pass": bool(proof["commands"]["import"].get("ok")),
        "runtime_no_controlled_pids": no_controlled_pids,
        "runtime_risk_execution_not_running": risk_execution_not_running,
        "runtime_position_flat": position_flat,
        "runtime_orders_zero": orders_zero,
        "redis_review_json_written": REDIS_REVIEW_JSON.exists(),
        "surface_review_json_written": SURFACE_REVIEW_JSON.exists(),
        "opportunity_json_written": OPPORTUNITY_JSON.exists(),
        "next_decision_json_written": NEXT_DECISION_JSON.exists(),
        "family_side_matrix_complete": sorted(list(family_surface.keys())) == sorted(FAMILY_SIDES),
        "ranking_written": isinstance(ranking.get("ranked"), list),
        "real_live_false": True,
        "paper_start_false": True,
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
        proof["classification"] = "O23L_MULTI_STRATEGY_OPPORTUNITY_AUDIT_NOT_PROVEN"
        proof["final_verdict"] = "FAIL_O23_L_MULTI_STRATEGY_SIGNAL_OPPORTUNITY_AUDIT_NOT_PROVEN"
        proof["next_recommended_batch"] = "Inspect false_keys; do not start paper or real live."
    else:
        proof["classification"] = "O23L_READ_ONLY_MULTI_STRATEGY_OPPORTUNITY_AUDIT_COMPLETE"
        proof["final_verdict"] = "PASS_O23_L_MULTI_STRATEGY_SIGNAL_OPPORTUNITY_AUDIT_OK_NO_START_NO_REAL_LIVE"
        proof["next_recommended_batch"] = next_batch

    PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    RUNBOOK_MD.write_text(
        "\n".join([
            f"# {BATCH} — multi-strategy signal-opportunity audit",
            "",
            f"- generated_at_utc: {proof['completed_at_utc']}",
            f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
            f"- opportunity_matrix: `{OPPORTUNITY_JSON.relative_to(ROOT)}`",
            f"- surface_review: `{SURFACE_REVIEW_JSON.relative_to(ROOT)}`",
            f"- redis_review: `{REDIS_REVIEW_JSON.relative_to(ROOT)}`",
            f"- next_decision: `{NEXT_DECISION_JSON.relative_to(ROOT)}`",
            "",
            "## Scope",
            "- Read-only.",
            "- Paper-disabled.",
            "- No service start.",
            "- No real live.",
            "- No order write.",
            "- No threshold relaxation.",
            "- No forced candidate.",
            "",
            "## Result",
            f"- final_verdict: `{proof['final_verdict']}`",
            f"- classification: `{proof['classification']}`",
            f"- false_keys: `{false_keys}`",
            f"- best_candidate_scope: `{best}`",
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
            f"# {DATE} — {BATCH} multi-strategy signal-opportunity audit",
            "",
            f"Verdict: `{proof['final_verdict']}`",
            "",
            f"Classification: `{proof['classification']}`",
            "",
            "## Achieved",
            "- Loaded O23-K and O23-J prerequisites.",
            "- Confirmed runtime safety state.",
            "- Reviewed latest Redis feature/decision payload surfaces.",
            "- Reviewed strategy-family / feature-family source/config surfaces.",
            "- Built advisory family/side opportunity matrix.",
            "- Preserved no-real-live, no-service-start, no-paper-start, no-source-patch boundary.",
            "",
            "## Next",
            f"- {proof['next_recommended_batch']}",
        ]),
        encoding="utf-8",
    )

    shutil.copy2(pathlib.Path(__file__), BIN_COPY)

    manifest_paths = [
        PROOF_JSON,
        OPPORTUNITY_JSON,
        SURFACE_REVIEW_JSON,
        REDIS_REVIEW_JSON,
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
    print("best_candidate_scope =", best)
    print("runtime_no_controlled_pids =", no_controlled_pids)
    print("runtime_position_flat =", position_flat)
    print("runtime_orders_zero =", orders_zero)
    print("next_recommended_batch =", proof["next_recommended_batch"])
    print("proof_json =", PROOF_JSON.relative_to(ROOT))
    print("manifest_json =", MANIFEST_JSON.relative_to(ROOT))
    print("opportunity_json =", OPPORTUNITY_JSON.relative_to(ROOT))
    print("surface_review_json =", SURFACE_REVIEW_JSON.relative_to(ROOT))
    print("redis_review_json =", REDIS_REVIEW_JSON.relative_to(ROOT))
    print("next_decision_json =", NEXT_DECISION_JSON.relative_to(ROOT))
    print("runbook =", RUNBOOK_MD.relative_to(ROOT))
    print("milestone =", MILESTONE_MD.relative_to(ROOT))
    return 0 if proof["final_verdict"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
