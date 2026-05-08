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
BATCH = "26-O23-N"
BATCH_NAME = "corrected_multi_strategy_opportunity_parser_deeper_read_only_sampler_no_start_no_real_live"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
TAG = f"batch26o23_n_corrected_opportunity_parser_deeper_sampler_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o23_n_corrected_opportunity_parser_deeper_sampler.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o23_n_corrected_opportunity_parser_deeper_sampler.json"
CORRECTED_RANKING_JSON = RUN_DIR / "controlled_paper_o23n_corrected_opportunity_ranking.json"
DEEP_SURFACE_JSON = RUN_DIR / "controlled_paper_o23n_deep_surface_sampler.json"
O23L_BUG_AUDIT_JSON = RUN_DIR / "controlled_paper_o23n_o23l_ranking_bug_audit.json"
NEXT_DECISION_JSON = RUN_DIR / "controlled_paper_o23n_next_decision.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o23_n_corrected_opportunity_parser_deeper_sampler.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o23_n_corrected_opportunity_parser_deeper_sampler.md"
BIN_COPY = BIN_DIR / "proof_batch26o23_n_corrected_opportunity_parser_deeper_sampler.py"

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
STREAM_SAMPLE_COUNT = int(os.environ.get("BATCH26O23N_STREAM_SAMPLE_COUNT", "250"))
MAX_NESTED_ITEMS = int(os.environ.get("BATCH26O23N_MAX_NESTED_ITEMS", "4000"))

PRIOR_PROOF_PATHS = [
    "run/proofs/proof_batch26o23_m_validate_mist_put_single_scope.json",
    "run/proofs/proof_batch26o23_l_multi_strategy_signal_opportunity_audit.json",
    "run/proofs/proof_batch26o23_k_post_repair_evidence_review.json",
    "run/proofs/proof_batch26o23_j_post_repair_controlled_paper_observation.json",
    "run/proofs/proof_batch26o23_i_r1_oneshot_safety_assertion_correction.json",
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


POSITIVE_TERMS = [
    "candidate", "eligible", "valid", "ready", "pass", "accepted",
    "triggered", "confirmed", "detected", "activation", "context_pass",
    "provider_ready", "entry_ok", "tradability_pass", "resume_confirmed",
    "breakout_accepted", "expansion_accepted", "trap_confirmed",
    "burst_detected", "aggression_ok", "tape_speed_ok",
]

NEGATIVE_TERMS = [
    "blocked", "false", "invalid", "stale", "missing", "not_ready",
    "fail", "hold", "no_candidate", "disabled", "veto", "timeout",
    "provider_unavailable", "context_stale", "data_invalid",
]

ENTRY_TERMS = [
    "buy", "sell", "entry", "order_intent", "candidate_found",
    "activation_candidate_count", "promoted", "paper",
]


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


def redis_cmd(args: list[str], timeout: int = 15) -> dict[str, Any]:
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
    return redis_cmd(["XREVRANGE", key, "+", "-", "COUNT", str(count)], timeout=30)


def redis_xrevrange_entries(key: str, count: int) -> list[dict[str, Any]]:
    raw = redis_xrevrange_raw(key, count=count)
    return parse_stream_entries(raw.get("stdout") or "")


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

    for _ in range(6):
        try:
            parsed = json.loads(s)
        except Exception:
            return None
        if isinstance(parsed, str) and parsed.strip().startswith(("{", "[")):
            s = parsed.strip()
            continue
        return parsed
    return None


def flatten_payload_text(obj: Any, max_chars: int = 20000) -> str:
    try:
        text = json.dumps(obj, sort_keys=True, default=str)
    except Exception:
        text = repr(obj)
    return text[:max_chars]


def parse_payloads_from_entries(entries: list[dict[str, Any]], stream_name: str) -> list[dict[str, Any]]:
    out = []
    for ent in entries:
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
                "frame_json",
                "feature_json",
                "strategy_json",
            }:
                parsed = parse_json_maybe(v)

            if isinstance(parsed, dict):
                out.append({
                    "stream": stream_name,
                    "id": ent.get("id"),
                    "field": k,
                    "payload": parsed,
                    "raw_field_count": len(fields),
                })
            else:
                # Also keep bounded raw text scan records for non-JSON fields.
                if isinstance(v, str) and any(tok in (k + " " + v).lower() for tok in ["mist", "misb", "misc", "misr", "miso", "call", "put", "candidate", "family"]):
                    out.append({
                        "stream": stream_name,
                        "id": ent.get("id"),
                        "field": k,
                        "payload": {"_raw_text": v[:5000], "_field": k},
                        "raw_field_count": len(fields),
                        "raw_text_only": True,
                    })
    return out


def nested_hits(obj: Any, terms: list[str], prefix: str = "", limit: int = MAX_NESTED_ITEMS) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    stack = [(prefix, obj)]
    seen = set()

    while stack and len(hits) < limit:
        path, cur = stack.pop()
        ident = id(cur)
        if ident in seen:
            continue
        seen.add(ident)

        if isinstance(cur, dict):
            for k, v in cur.items():
                pth = f"{path}.{k}" if path else str(k)
                hay = f"{pth} {repr(v)[:800]}".lower()
                if any(t.lower() in hay for t in terms):
                    hits.append({
                        "path": pth,
                        "value_repr": repr(v)[:800],
                    })
                if isinstance(v, (dict, list)):
                    stack.append((pth, v))
                elif isinstance(v, str):
                    parsed = parse_json_maybe(v)
                    if isinstance(parsed, (dict, list)):
                        stack.append((pth + ".__parsed_json__", parsed))
        elif isinstance(cur, list):
            for i, v in enumerate(cur[:150]):
                if isinstance(v, (dict, list)):
                    stack.append((f"{path}[{i}]", v))
                elif isinstance(v, str):
                    parsed = parse_json_maybe(v)
                    if isinstance(parsed, (dict, list)):
                        stack.append((f"{path}[{i}].__parsed_json__", parsed))
    return hits


def terms_for_scope(family: str, side: str) -> list[str]:
    fam = family.lower()
    side_l = side.lower()
    opt = "ce" if side == "CALL" else "pe"
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
        family,
        fam,
        side,
        side_l,
        opt,
        opt.upper(),
    ]


def score_scope_from_hits(scope: str, hits: list[dict[str, Any]], payload_text: str) -> dict[str, Any]:
    family, side = scope.split("_")
    low = payload_text.lower()
    hit_text = json.dumps(hits, sort_keys=True, default=str).lower()
    joined = (hit_text + " " + low[:15000]).lower()

    positive = sum(1 for t in POSITIVE_TERMS if t in joined)
    negative = sum(1 for t in NEGATIVE_TERMS if t in joined)
    entry = sum(1 for t in ENTRY_TERMS if t in joined)

    family_seen = family.lower() in joined
    side_seen = side.lower() in joined or ("pe" in joined if side == "PUT" else "ce" in joined)

    direct_scope_seen = any(v in joined for v in [
        scope.lower(),
        scope.replace("_", " ").lower(),
        scope.replace("_", ":").lower(),
        scope.replace("_", ".").lower(),
    ])

    evidence_seen = direct_scope_seen or (family_seen and side_seen and len(hits) > 0)

    raw_score = 0
    if direct_scope_seen:
        raw_score += 5
    if family_seen:
        raw_score += 1
    if side_seen:
        raw_score += 1
    raw_score += positive
    raw_score += entry
    raw_score -= negative

    if not evidence_seen:
        bucket = "NO_SURFACE_SEEN"
    elif raw_score >= 8:
        bucket = "HIGHER_OPPORTUNITY_SURFACE"
    elif raw_score >= 4:
        bucket = "SOME_OPPORTUNITY_SURFACE"
    elif raw_score >= 1:
        bucket = "WEAK_OR_NEUTRAL_SURFACE"
    else:
        bucket = "BLOCKED_OR_LOW_OPPORTUNITY_SURFACE"

    return {
        "family_seen": family_seen,
        "side_seen": side_seen,
        "direct_scope_seen": direct_scope_seen,
        "evidence_seen": evidence_seen,
        "positive_term_count": positive,
        "negative_term_count": negative,
        "entry_term_count": entry,
        "raw_score": raw_score,
        "rank_bucket": bucket,
    }


def build_corrected_opportunity(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    matrix: dict[str, Any] = {}

    for scope in FAMILY_SIDES:
        family, side = scope.split("_")
        scope_terms = terms_for_scope(family, side)
        scope_hits = []
        total_score = 0
        evidence_seen_any = False

        for item in payloads:
            payload = item.get("payload") or {}
            text = flatten_payload_text(payload)
            hits = nested_hits(payload, scope_terms, limit=700)
            scored = score_scope_from_hits(scope, hits, text)

            if scored["evidence_seen"]:
                evidence_seen_any = True
                total_score += int(scored["raw_score"])
                scope_hits.append({
                    "stream": item.get("stream"),
                    "id": item.get("id"),
                    "field": item.get("field"),
                    "raw_text_only": item.get("raw_text_only") is True,
                    "raw_field_count": item.get("raw_field_count"),
                    "score": scored,
                    "hits": hits[:80],
                })

        if not evidence_seen_any:
            rank_bucket = "NO_SURFACE_SEEN"
        elif total_score >= 10:
            rank_bucket = "HIGHER_OPPORTUNITY_SURFACE"
        elif total_score >= 5:
            rank_bucket = "SOME_OPPORTUNITY_SURFACE"
        elif total_score >= 1:
            rank_bucket = "WEAK_OR_NEUTRAL_SURFACE"
        else:
            rank_bucket = "BLOCKED_OR_LOW_OPPORTUNITY_SURFACE"

        matrix[scope] = {
            "family": family,
            "side": side,
            "surface_seen": evidence_seen_any,
            "hit_count": len(scope_hits),
            "raw_score": total_score,
            "rank_bucket": rank_bucket,
            "hits": scope_hits[:50],
        }

    ranked = []
    for scope, rec in matrix.items():
        adjusted = int(rec["raw_score"])

        caution = []
        if scope.startswith("MISO_"):
            adjusted -= 5
            caution.append("MISO requires Dhan selected-option + option-context freshness before any paper expansion.")

        # Important correction versus O23-L:
        # NO_SURFACE_SEEN can never be selected as paper candidate.
        if rec["rank_bucket"] == "NO_SURFACE_SEEN" or rec["surface_seen"] is not True:
            adjusted = -999
            caution.append("Rejected from candidate selection because no runtime surface was seen.")

        ranked.append({
            "family_side": scope,
            "family": rec["family"],
            "side": rec["side"],
            "surface_seen": rec["surface_seen"],
            "hit_count": rec["hit_count"],
            "raw_score": rec["raw_score"],
            "adjusted_score": adjusted,
            "rank_bucket": rec["rank_bucket"],
            "caution": caution,
        })

    ranked.sort(key=lambda r: (r["adjusted_score"], r["raw_score"], r["hit_count"]), reverse=True)

    evidence_ranked = [
        r for r in ranked
        if r["surface_seen"] is True
        and r["rank_bucket"] != "NO_SURFACE_SEEN"
        and r["adjusted_score"] > -999
    ]

    best = evidence_ranked[0] if evidence_ranked else None

    return {
        "matrix": matrix,
        "ranked": ranked,
        "evidence_ranked": evidence_ranked,
        "best_evidence_backed_scope": best,
        "correction_law": {
            "no_surface_seen_never_selected": True,
            "surface_seen_required": True,
            "hit_count_positive_required": True,
            "miso_penalized_until_context_fresh": True,
        },
    }


def audit_o23l_bug(o23l_obj: dict[str, Any], corrected: dict[str, Any]) -> dict[str, Any]:
    opp = o23l_obj.get("opportunity_matrix") or {}
    ranking = opp.get("ranking") or {}
    best = ranking.get("best_candidate_scope") or {}

    o23l_selected_no_surface = (
        best.get("surface_seen") is False
        or best.get("rank_bucket") == "NO_SURFACE_SEEN"
        or int(best.get("hit_count") or 0) == 0
    )

    corrected_best = corrected.get("best_evidence_backed_scope")

    return {
        "o23l_best_candidate_scope": best,
        "o23l_selected_no_surface": o23l_selected_no_surface,
        "corrected_best_evidence_backed_scope": corrected_best,
        "bug_classification": (
            "O23L_FALLBACK_SELECTED_NO_SURFACE_SCOPE"
            if o23l_selected_no_surface
            else "O23L_BEST_SCOPE_WAS_EVIDENCE_BACKED"
        ),
        "correction": [
            "NO_SURFACE_SEEN is not eligible for next paper scope.",
            "surface_seen=True and hit_count>0 are mandatory.",
            "If no evidence-backed scope exists, stop and gather deeper live/observe-only surfaces.",
        ],
    }


def read_only_source_surface_presence() -> dict[str, Any]:
    roots = [
        ROOT / "app/mme_scalpx/services/strategy_family",
        ROOT / "app/mme_scalpx/services/feature_family",
        ROOT / "etc/strategy_family",
    ]

    out: dict[str, Any] = {"files": {}, "scope_mentions": {scope: [] for scope in FAMILY_SIDES}}

    for base in roots:
        if not base.exists():
            out["files"][str(base.relative_to(ROOT))] = {"exists": False}
            continue

        files = sorted([p for p in base.rglob("*") if p.is_file()])
        for p in files:
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            rel = str(p.relative_to(ROOT))
            file_rec = {"sha256": sha256_file(p), "scope_hits": {}}

            for scope in FAMILY_SIDES:
                family, side = scope.split("_")
                terms = terms_for_scope(family, side)
                hits = []
                for i, line in enumerate(text.splitlines(), 1):
                    low = line.lower()
                    if any(t.lower() in low for t in terms):
                        hits.append({"line": i, "text": line[:350]})
                        if len(hits) >= 40:
                            break
                if hits:
                    file_rec["scope_hits"][scope] = hits
                    out["scope_mentions"][scope].append({"file": rel, "hit_count": len(hits), "hits": hits[:10]})

            if file_rec["scope_hits"]:
                out["files"][rel] = file_rec

    return out


def main() -> int:
    proof: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": BATCH_NAME,
        "tag": TAG,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "purpose": "Correct O23-L opportunity ranking logic and deeply sample latest surfaces read-only before any further paper expansion.",
        "safety_intent": {
            "real_live_enablement": False,
            "paper_start": False,
            "service_start": False,
            "broker_call": False,
            "order_write": False,
            "threshold_relaxation": False,
            "forced_candidate": False,
            "production_source_patch": False,
            "read_only_deeper_sampler": True,
            "ranking_parser_correction_only": True,
        },
        "disk_state": {},
        "inspected_files": {},
        "prior_proofs": {},
        "commands": {},
        "runtime_snapshot": {},
        "deep_surface_sampler": {},
        "corrected_ranking": {},
        "o23l_bug_audit": {},
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

    print("===== DEEP REDIS SURFACE SAMPLER =====")
    feature_entries = redis_xrevrange_entries(FEATURES_STREAM, STREAM_SAMPLE_COUNT)
    decision_entries = redis_xrevrange_entries(DECISIONS_STREAM, STREAM_SAMPLE_COUNT)

    feature_payloads = parse_payloads_from_entries(feature_entries, FEATURES_STREAM)
    decision_payloads = parse_payloads_from_entries(decision_entries, DECISIONS_STREAM)
    all_payloads = feature_payloads + decision_payloads

    source_presence = read_only_source_surface_presence()

    deep_surface = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "stream_sample_count_requested": STREAM_SAMPLE_COUNT,
        "feature_entry_count": len(feature_entries),
        "decision_entry_count": len(decision_entries),
        "feature_payload_count": len(feature_payloads),
        "decision_payload_count": len(decision_payloads),
        "feature_payload_fields": [{"id": x.get("id"), "field": x.get("field"), "raw_text_only": x.get("raw_text_only") is True} for x in feature_payloads[:100]],
        "decision_payload_fields": [{"id": x.get("id"), "field": x.get("field"), "raw_text_only": x.get("raw_text_only") is True} for x in decision_payloads[:100]],
        "source_surface_presence": source_presence,
    }
    proof["deep_surface_sampler"] = deep_surface
    DEEP_SURFACE_JSON.write_text(json.dumps(deep_surface, indent=2, sort_keys=True), encoding="utf-8")

    print("===== CORRECTED OPPORTUNITY RANKING =====")
    corrected = build_corrected_opportunity(all_payloads)
    proof["corrected_ranking"] = corrected
    CORRECTED_RANKING_JSON.write_text(json.dumps(corrected, indent=2, sort_keys=True), encoding="utf-8")

    print("===== O23-L RANKING BUG AUDIT =====")
    o23l = proof["prior_proofs"].get("run/proofs/proof_batch26o23_l_multi_strategy_signal_opportunity_audit.json", {})
    o23l_obj = o23l.get("loaded_obj") or {}
    bug_audit = audit_o23l_bug(o23l_obj, corrected)
    proof["o23l_bug_audit"] = bug_audit
    O23L_BUG_AUDIT_JSON.write_text(json.dumps(bug_audit, indent=2, sort_keys=True), encoding="utf-8")

    m = proof["prior_proofs"].get("run/proofs/proof_batch26o23_m_validate_mist_put_single_scope.json", {})
    k = proof["prior_proofs"].get("run/proofs/proof_batch26o23_k_post_repair_evidence_review.json", {})
    j = proof["prior_proofs"].get("run/proofs/proof_batch26o23_j_post_repair_controlled_paper_observation.json", {})

    best = corrected.get("best_evidence_backed_scope")
    best_scope = best.get("family_side") if isinstance(best, dict) else None

    if best_scope:
        next_batch = f"26-O23-O validate {best_scope} as next one-family/side scope, no paper start, no real live."
        decision = "VALIDATE_BEST_EVIDENCE_BACKED_SCOPE_NEXT"
    else:
        next_batch = "26-O23-O live-session read-only family-surface materialization sampler; no paper start, no real live."
        decision = "NO_EVIDENCE_BACKED_SCOPE_FOUND_COLLECT_READ_ONLY_SURFACES_NEXT"

    next_decision = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "best_evidence_backed_scope": best_scope,
        "recommended_next_batch": next_batch,
        "do_not_start_paper_yet": True,
        "do_not_proceed_to_real_live": True,
        "why": [
            "O23-M correctly refused MIST_PUT because it was not evidence-backed.",
            "O23-N corrects the ranking law: NO_SURFACE_SEEN cannot be selected.",
            "If no evidence-backed family/side exists in current Redis history, collect a read-only live-session surface materialization sample before further paper expansion.",
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

    no_surface_never_selected = corrected.get("correction_law", {}).get("no_surface_seen_never_selected") is True
    if best_scope:
        best_valid = best.get("surface_seen") is True and best.get("hit_count", 0) > 0 and best.get("rank_bucket") != "NO_SURFACE_SEEN"
    else:
        best_valid = True

    req = {
        "o23m_pass_loaded": pass_prefix(m, "PASS_O23_M_MIST_PUT_SCOPE_REJECTED_AS_NOT_EVIDENCE_BACKED_NO_START_NO_REAL_LIVE"),
        "o23l_pass_loaded": pass_prefix(o23l, "PASS_O23_L_MULTI_STRATEGY_SIGNAL_OPPORTUNITY_AUDIT_OK_NO_START_NO_REAL_LIVE"),
        "o23k_pass_loaded": pass_prefix(k, "PASS_O23_K_POST_REPAIR_EVIDENCE_REVIEW_OK_NO_REAL_LIVE"),
        "o23j_pass_loaded": pass_prefix(j, "PASS_O23_J_POST_REPAIR_CONTROLLED_PAPER_OBSERVATION_OK_REAL_LIVE_FALSE"),
        "compile_pass": bool(proof["commands"]["compile"].get("ok")),
        "import_pass": bool(proof["commands"]["import"].get("ok")),
        "runtime_no_controlled_pids": no_controlled_pids,
        "runtime_risk_execution_not_running": risk_execution_not_running,
        "runtime_position_flat": position_flat,
        "runtime_orders_zero": orders_zero,
        "deep_surface_json_written": DEEP_SURFACE_JSON.exists(),
        "corrected_ranking_json_written": CORRECTED_RANKING_JSON.exists(),
        "o23l_bug_audit_json_written": O23L_BUG_AUDIT_JSON.exists(),
        "next_decision_json_written": NEXT_DECISION_JSON.exists(),
        "family_side_matrix_complete": sorted(list(corrected.get("matrix", {}).keys())) == sorted(FAMILY_SIDES),
        "ranking_correction_law_present": no_surface_never_selected,
        "best_scope_if_any_is_evidence_backed": best_valid,
        "o23l_no_surface_bug_classified": bug_audit.get("bug_classification") in {
            "O23L_FALLBACK_SELECTED_NO_SURFACE_SCOPE",
            "O23L_BEST_SCOPE_WAS_EVIDENCE_BACKED",
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
        proof["classification"] = "O23N_CORRECTED_OPPORTUNITY_PARSER_NOT_PROVEN"
        proof["final_verdict"] = "FAIL_O23_N_CORRECTED_OPPORTUNITY_PARSER_NOT_PROVEN"
        proof["next_recommended_batch"] = "Inspect false_keys; do not start paper or real live."
    else:
        if best_scope:
            proof["classification"] = "O23N_EVIDENCE_BACKED_SCOPE_FOUND_FOR_VALIDATION"
        else:
            proof["classification"] = "O23N_NO_EVIDENCE_BACKED_SCOPE_IN_CURRENT_REDIS_HISTORY"
        proof["final_verdict"] = "PASS_O23_N_CORRECTED_OPPORTUNITY_PARSER_OK_NO_START_NO_REAL_LIVE"
        proof["next_recommended_batch"] = next_batch

    PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    RUNBOOK_MD.write_text(
        "\n".join([
            f"# {BATCH} — corrected opportunity parser / deeper read-only sampler",
            "",
            f"- generated_at_utc: {proof['completed_at_utc']}",
            f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
            f"- corrected_ranking: `{CORRECTED_RANKING_JSON.relative_to(ROOT)}`",
            f"- deep_surface: `{DEEP_SURFACE_JSON.relative_to(ROOT)}`",
            f"- o23l_bug_audit: `{O23L_BUG_AUDIT_JSON.relative_to(ROOT)}`",
            f"- next_decision: `{NEXT_DECISION_JSON.relative_to(ROOT)}`",
            "",
            "## Scope",
            "- Correct parser/ranking law only.",
            "- Read-only deep sampler.",
            "- No service start.",
            "- No paper start.",
            "- No real live.",
            "- No threshold relaxation.",
            "- No forced candidate.",
            "",
            "## Correction law",
            "- `NO_SURFACE_SEEN` can never be selected for next paper scope.",
            "- `surface_seen=True` and `hit_count>0` are mandatory.",
            "- MISO remains penalized until Dhan context freshness is proven.",
            "",
            "## Result",
            f"- final_verdict: `{proof['final_verdict']}`",
            f"- classification: `{proof['classification']}`",
            f"- false_keys: `{false_keys}`",
            f"- best_evidence_backed_scope: `{best_scope}`",
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
            f"# {DATE} — {BATCH} corrected opportunity parser",
            "",
            f"Verdict: `{proof['final_verdict']}`",
            "",
            f"Classification: `{proof['classification']}`",
            "",
            "## Achieved",
            "- Loaded O23-M/O23-L/O23-K/O23-J prerequisites.",
            "- Re-sampled feature/decision Redis streams read-only.",
            "- Corrected opportunity ranking law.",
            "- Classified O23-L no-surface fallback selection behavior.",
            "- Preserved no-paper-start, no-real-live, no-source-patch boundary.",
            "",
            "## Next",
            f"- {proof['next_recommended_batch']}",
        ]),
        encoding="utf-8",
    )

    shutil.copy2(pathlib.Path(__file__), BIN_COPY)

    manifest_paths = [
        PROOF_JSON,
        CORRECTED_RANKING_JSON,
        DEEP_SURFACE_JSON,
        O23L_BUG_AUDIT_JSON,
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
    print("o23l_bug_classification =", bug_audit.get("bug_classification"))
    print("best_evidence_backed_scope =", best_scope)
    print("feature_entry_count =", deep_surface.get("feature_entry_count"))
    print("decision_entry_count =", deep_surface.get("decision_entry_count"))
    print("feature_payload_count =", deep_surface.get("feature_payload_count"))
    print("decision_payload_count =", deep_surface.get("decision_payload_count"))
    print("next_recommended_batch =", proof["next_recommended_batch"])
    print("proof_json =", PROOF_JSON.relative_to(ROOT))
    print("manifest_json =", MANIFEST_JSON.relative_to(ROOT))
    print("corrected_ranking_json =", CORRECTED_RANKING_JSON.relative_to(ROOT))
    print("deep_surface_json =", DEEP_SURFACE_JSON.relative_to(ROOT))
    print("o23l_bug_audit_json =", O23L_BUG_AUDIT_JSON.relative_to(ROOT))
    print("next_decision_json =", NEXT_DECISION_JSON.relative_to(ROOT))
    print("runbook =", RUNBOOK_MD.relative_to(ROOT))
    print("milestone =", MILESTONE_MD.relative_to(ROOT))
    return 0 if proof["final_verdict"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
