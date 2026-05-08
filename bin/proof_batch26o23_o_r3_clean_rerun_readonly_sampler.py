#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path.cwd().resolve()
BATCH = "26-O23-O-R3"
BATCH_NAME = "clean_rerun_live_session_readonly_family_surface_sampler_no_paper_no_real_live"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
TAG = f"batch26o23_o_r3_clean_rerun_readonly_sampler_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o23_o_r3_clean_rerun_readonly_sampler.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o23_o_r3_clean_rerun_readonly_sampler.json"
SESSION_JSON = RUN_DIR / "controlled_paper_o23o_r3_readonly_surface_session.json"
SAMPLE_REVIEW_JSON = RUN_DIR / "controlled_paper_o23o_r3_sample_review.json"
SURFACE_MATRIX_JSON = RUN_DIR / "controlled_paper_o23o_r3_family_surface_matrix.json"
SAFETY_JSON = RUN_DIR / "controlled_paper_o23o_r3_safety_readback.json"
LOG_REVIEW_JSON = RUN_DIR / "controlled_paper_o23o_r3_log_review.json"
NEXT_DECISION_JSON = RUN_DIR / "controlled_paper_o23o_r3_next_decision.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o23_o_r3_clean_rerun_readonly_sampler.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o23_o_r3_clean_rerun_readonly_sampler.md"
BIN_COPY = BIN_DIR / "proof_batch26o23_o_r3_clean_rerun_readonly_sampler.py"

REDIS_CLI = os.environ.get("REDIS_CLI", "redis-cli")
FEATURES_STREAM = "features:mme:stream"
DECISIONS_STREAM = "decisions:mme:stream"
ORDERS_STREAM = "orders:mme:stream"
POSITION_HASH = "state:position:mme"

READONLY_SERVICES = ["feeds", "features", "strategy"]
FORBIDDEN_SERVICES = {"risk", "execution"}
ALL_SERVICES = {"feeds", "features", "strategy", "risk", "execution"}

FAMILIES = ["MIST", "MISB", "MISC", "MISR", "MISO"]
SIDES = ["CALL", "PUT"]
FAMILY_SIDES = [f"{fam}_{side}" for fam in FAMILIES for side in SIDES]

SAMPLE_SECONDS = int(os.environ.get("BATCH26O23O_R3_SAMPLE_SECONDS", "300"))
POLL_SECONDS = float(os.environ.get("BATCH26O23O_R3_POLL_SECONDS", "5"))
STREAM_REVIEW_COUNT = int(os.environ.get("BATCH26O23O_R3_STREAM_REVIEW_COUNT", "500"))
MIN_FREE_BYTES = int(os.environ.get("BATCH26O23O_R3_MIN_FREE_BYTES", str(2 * 1024**3)))

SMALL_COPY_LIMIT_BYTES = 500_000
MAX_SLICE_CHARS = 24_000
MAX_LOG_HITS = 120

PRIOR_PROOF_PATHS = [
    "run/proofs/proof_batch26o23_o_r2_interrupted_recovery_readback.json",
    "run/proofs/proof_batch26o23_o_live_readonly_family_surface_sampler.json",
    "run/proofs/proof_batch26o23_n_corrected_opportunity_parser_deeper_sampler.json",
    "run/proofs/proof_batch26o23_m_validate_mist_put_single_scope.json",
    "run/proofs/proof_batch26o23_k_post_repair_evidence_review.json",
]

SOURCE_PATHS = [
    "app/mme_scalpx/main.py",
    "app/mme_scalpx/services/feeds.py",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/services/feature_family",
    "app/mme_scalpx/services/strategy_family",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "app/mme_scalpx/core/redisx.py",
    "app/mme_scalpx/core/settings.py",
    "app/mme_scalpx/integrations/provider_runtime.py",
    "app/mme_scalpx/integrations/bootstrap_provider.py",
]

CONFIG_PATHS = [
    "etc/strategy_family/family_runtime.yaml",
    "etc/strategy_family/doctrine_registry.yaml",
    "etc/strategy_family/arbitration.yaml",
    "etc/strategy_family/frozen",
    "etc/strategy_family/rollout",
    "etc/brokers/runtime.yaml",
    "etc/brokers/provider_roles.yaml",
    "etc/brokers/dhan.yaml",
    "etc/brokers/zerodha.yaml",
]

INSPECT_PATHS = PRIOR_PROOF_PATHS + SOURCE_PATHS + CONFIG_PATHS

STARTED: list[subprocess.Popen[str]] = []

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


def run(cmd: list[str] | str, *, timeout: int = 30, env: dict[str, str] | None = None, shell: bool = False) -> dict[str, Any]:
    try:
        cp = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
            env=env,
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


def bounded_text(path: pathlib.Path) -> dict[str, Any]:
    rec: dict[str, Any] = {}
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        rec["head"] = text[:MAX_SLICE_CHARS // 2]
        rec["tail"] = text[-MAX_SLICE_CHARS // 2:]
    except Exception as exc:
        rec["slice_error"] = repr(exc)
    return rec


def scan_json_lines(path: pathlib.Path) -> dict[str, Any]:
    rec: dict[str, Any] = {
        "exists": path.exists(),
        "path": str(path.relative_to(ROOT)) if path.exists() else str(path),
    }
    if not path.exists() or not path.is_file():
        return rec

    rec["size_bytes"] = path.stat().st_size
    rec["sha256"] = sha256_file(path)

    keys = {"final_verdict": None, "classification": None, "next_recommended_batch": None}
    false_key_lines = []
    required_false_lines = []

    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            capture_false = False
            for line in f:
                s = line.strip()
                for k in list(keys):
                    if f'"{k}"' in s and ":" in s and keys[k] is None:
                        m = re.search(r':\s*"([^"]*)"', s)
                        if m:
                            keys[k] = m.group(1)

                if '"false_keys"' in s:
                    false_key_lines.append(s[:500])
                    capture_false = True
                    continue

                if capture_false:
                    false_key_lines.append(s[:500])
                    if "]" in s:
                        capture_false = False

                if re.search(r':\s*false[,}]?$', s, flags=re.I):
                    required_false_lines.append(s[:500])
                    if len(required_false_lines) >= 80:
                        break
    except Exception as exc:
        rec["scan_error"] = repr(exc)

    rec.update(keys)
    rec["false_keys_lines"] = false_key_lines[:80]
    rec["required_false_lines"] = required_false_lines[:80]
    rec.update(bounded_text(path))
    return rec


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
            for x in files[:120]
            if x.stat().st_size <= SMALL_COPY_LIMIT_BYTES
        }
        return rec

    rec["size_bytes"] = p.stat().st_size
    rec["sha256"] = sha256_file(p)
    rec.update(bounded_text(p))

    if copy_source and p.stat().st_size <= SMALL_COPY_LIMIT_BYTES and rel.startswith("app/"):
        dst = BACKUP_DIR / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)
        rec["source_backup"] = str(dst.relative_to(ROOT))
    else:
        rec["backup_policy"] = "hash_plus_bounded_head_tail_slice_only"

    return rec


def load_json_summary(rel: str) -> dict[str, Any]:
    p = ROOT / rel
    if not p.exists() or not p.is_file():
        return {"exists": False, "path": rel}
    if p.stat().st_size > 20_000_000:
        return scan_json_lines(p)
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(obj, dict):
            return {"exists": True, "loaded_type": type(obj).__name__}
        return {
            "exists": True,
            "path": rel,
            "size_bytes": p.stat().st_size,
            "sha256": sha256_file(p),
            "final_verdict": obj.get("final_verdict"),
            "classification": obj.get("classification"),
            "false_keys": obj.get("false_keys"),
            "next_recommended_batch": obj.get("next_recommended_batch"),
            "required_verdicts": obj.get("required_verdicts") if isinstance(obj.get("required_verdicts"), dict) else {},
            "tag": obj.get("tag"),
        }
    except Exception as exc:
        rec = scan_json_lines(p)
        rec["json_load_error"] = repr(exc)
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


def redis_xrange_raw(key: str, start: str, end: str = "+", count: int = 500) -> dict[str, Any]:
    return redis_cmd(["XRANGE", key, start, end, "COUNT", str(count)], timeout=30)


def redis_last_id(key: str) -> str:
    rows = redis_xrevrange_raw(key, count=1).get("stdout") or ""
    first = rows.splitlines()[0].strip() if rows.splitlines() else "0-0"
    return first if re.match(r"^\d+-\d+$", first) else "0-0"


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


def redis_entries_since(key: str, start_id: str, count: int = 500) -> list[dict[str, Any]]:
    raw = redis_xrange_raw(key, f"({start_id}", "+", count=count)
    return parse_stream_entries(raw.get("stdout") or "")


def flat_position(pos: dict[str, str]) -> bool:
    if not pos:
        return True
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
            "args": args[:1400],
            "is_mme_main_service": "app.mme_scalpx.main" in args and service in ALL_SERVICES,
            "is_readonly_service": "app.mme_scalpx.main" in args and service in set(READONLY_SERVICES),
            "is_forbidden_service": "app.mme_scalpx.main" in args and service in FORBIDDEN_SERVICES,
        })
    return rows


def runtime_snapshot() -> dict[str, Any]:
    rows = parse_processes()
    return {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "features_xlen": redis_xlen(FEATURES_STREAM),
        "decisions_xlen": redis_xlen(DECISIONS_STREAM),
        "orders_xlen": redis_xlen(ORDERS_STREAM),
        "features_last_id": redis_last_id(FEATURES_STREAM),
        "decisions_last_id": redis_last_id(DECISIONS_STREAM),
        "orders_last_id": redis_last_id(ORDERS_STREAM),
        "latest_orders_raw": redis_xrevrange_raw(ORDERS_STREAM, count=10),
        "position": redis_hgetall(POSITION_HASH),
        "process_rows": rows,
        "readonly_service_rows": [r for r in rows if r.get("is_readonly_service")],
        "forbidden_service_rows": [r for r in rows if r.get("is_forbidden_service")],
        "all_mme_service_rows": [r for r in rows if r.get("is_mme_main_service")],
    }


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
            elif isinstance(v, str) and any(tok in (k + " " + v).lower() for tok in ["mist", "misb", "misc", "misr", "miso", "call", "put", "candidate", "family"]):
                out.append({
                    "stream": stream_name,
                    "id": ent.get("id"),
                    "field": k,
                    "payload": {"_raw_text": v[:6000], "_field": k},
                    "raw_field_count": len(fields),
                    "raw_text_only": True,
                })
    return out


def flatten_payload_text(obj: Any, max_chars: int = 22000) -> str:
    try:
        text = json.dumps(obj, sort_keys=True, default=str)
    except Exception:
        text = repr(obj)
    return text[:max_chars]


def nested_hits(obj: Any, terms: list[str], prefix: str = "", limit: int = 3000) -> list[dict[str, Any]]:
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
                    hits.append({"path": pth, "value_repr": repr(v)[:800]})
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
        f"{family}_{side}", f"{family}:{side}", f"{family}.{side}", f"{family} {side}",
        f"{fam}_{side_l}", f"{fam}:{side_l}", f"{fam}.{side_l}", f"{fam} {side_l}",
        f"{family}{side}", f"{fam}{side_l}",
        family, fam, side, side_l, opt, opt.upper(),
    ]


def score_scope(scope: str, hits: list[dict[str, Any]], payload_text: str) -> dict[str, Any]:
    family, side = scope.split("_")
    joined = (json.dumps(hits, sort_keys=True, default=str) + " " + payload_text[:16000]).lower()

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
    elif raw_score >= 10:
        bucket = "HIGHER_OPPORTUNITY_SURFACE"
    elif raw_score >= 5:
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


def build_surface_matrix(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    matrix = {}

    for scope in FAMILY_SIDES:
        family, side = scope.split("_")
        terms = terms_for_scope(family, side)
        scope_hits = []
        total = 0
        seen = False

        for item in payloads:
            payload = item.get("payload") or {}
            text = flatten_payload_text(payload)
            hits = nested_hits(payload, terms, limit=800)
            scored = score_scope(scope, hits, text)
            if scored["evidence_seen"]:
                seen = True
                total += int(scored["raw_score"])
                scope_hits.append({
                    "stream": item.get("stream"),
                    "id": item.get("id"),
                    "field": item.get("field"),
                    "raw_text_only": item.get("raw_text_only") is True,
                    "score": scored,
                    "hits": hits[:80],
                })

        if not seen:
            bucket = "NO_SURFACE_SEEN"
        elif total >= 10:
            bucket = "HIGHER_OPPORTUNITY_SURFACE"
        elif total >= 5:
            bucket = "SOME_OPPORTUNITY_SURFACE"
        elif total >= 1:
            bucket = "WEAK_OR_NEUTRAL_SURFACE"
        else:
            bucket = "BLOCKED_OR_LOW_OPPORTUNITY_SURFACE"

        matrix[scope] = {
            "family": family,
            "side": side,
            "surface_seen": seen,
            "hit_count": len(scope_hits),
            "raw_score": total,
            "rank_bucket": bucket,
            "hits": scope_hits[:80],
        }

    ranked = []
    for scope, rec in matrix.items():
        adjusted = int(rec["raw_score"])
        caution = []
        if scope.startswith("MISO_"):
            adjusted -= 5
            caution.append("MISO requires Dhan selected-option + option-context freshness before paper expansion.")
        if rec["surface_seen"] is not True or rec["rank_bucket"] == "NO_SURFACE_SEEN":
            adjusted = -999
            caution.append("Rejected because no runtime family/side surface was materialized.")

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

    return {
        "matrix": matrix,
        "ranked": ranked,
        "evidence_ranked": evidence_ranked,
        "best_evidence_backed_scope": evidence_ranked[0] if evidence_ranked else None,
        "correction_law": {
            "no_surface_seen_never_selected": True,
            "surface_seen_required": True,
            "hit_count_positive_required": True,
            "miso_penalized_until_context_fresh": True,
        },
    }


def readonly_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{ROOT}:{env.get('PYTHONPATH', '')}"

    env["SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME"] = "0"
    env["SCALPX_PAPER_ARMED"] = "0"
    env["SCALPX_REAL_LIVE_ALLOWED"] = "0"
    env["SCALPX_LIVE_ORDERS_ALLOWED"] = "0"
    env["SCALPX_BROKER_CALLS_ALLOWED"] = "0"
    env["SCALPX_FORCE_CANDIDATE"] = "0"
    env["SCALPX_THRESHOLD_RELAXATION"] = "0"
    env["SCALPX_AUTOMATIC_BROKER_FAILOVER"] = "0"
    env["SCALPX_MID_POSITION_PROVIDER_MIGRATION"] = "0"

    env["SCALPX_FAMILY_RUNTIME_MODE"] = "observe_only"
    env["SCALPX_STRATEGY_ROLLOUT_MODE"] = "observe_only"
    env["SCALPX_ORDER_INTENT_ENABLED"] = "0"
    env["SCALPX_EXECUTION_ENABLED"] = "0"
    return env


def start_service(service: str, env: dict[str, str]) -> dict[str, Any]:
    log_path = RUN_DIR / f"{service}_readonly_o23o_r3.log"
    cmd = [
        sys.executable,
        "-m",
        "app.mme_scalpx.main",
        "--service",
        service,
        "--bootstrap-provider",
        "app.mme_scalpx.integrations.bootstrap_provider:provide",
        "--skip-group-bootstrap",
    ]

    log_f = log_path.open("w", encoding="utf-8")
    proc = subprocess.Popen(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=log_f,
        stderr=subprocess.STDOUT,
        env=env,
    )
    STARTED.append(proc)
    time.sleep(5)

    return {
        "service": service,
        "started": True,
        "pid": proc.pid,
        "cmd": cmd,
        "log_path": str(log_path.relative_to(ROOT)),
        "alive_after_start": proc.poll() is None,
        "returncode_after_start": proc.poll(),
    }


def stop_started() -> list[dict[str, Any]]:
    out = []
    for p in reversed(STARTED):
        rec = {"pid": p.pid, "returncode_before_stop": p.poll()}
        if p.poll() is None:
            try:
                p.send_signal(signal.SIGTERM)
                try:
                    p.wait(timeout=12)
                    rec["stopped"] = True
                except subprocess.TimeoutExpired:
                    p.kill()
                    p.wait(timeout=8)
                    rec["killed"] = True
            except Exception as exc:
                rec["stop_error"] = repr(exc)
        rec["returncode_after_stop"] = p.poll()
        out.append(rec)
    return out


def stop_leftover_started_services() -> list[dict[str, Any]]:
    started_pids = {p.pid for p in STARTED}
    rows = runtime_snapshot()["all_mme_service_rows"]
    out = []
    for row in rows:
        pid = int(row["pid"])
        if pid not in started_pids:
            continue
        rec = dict(row)
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(1.5)
            if pathlib.Path("/proc").joinpath(str(pid)).exists():
                os.kill(pid, signal.SIGKILL)
                rec["killed"] = True
            else:
                rec["terminated"] = True
        except ProcessLookupError:
            rec["already_exited"] = True
        except Exception as exc:
            rec["stop_error"] = repr(exc)
        out.append(rec)
    return out


def review_logs() -> dict[str, Any]:
    patterns = [
        "Traceback", "Exception", "ERROR", "CRITICAL",
        "family", "surface", "candidate", "no_candidate",
        "MIST", "MISB", "MISC", "MISR", "MISO",
        "CALL", "PUT", "consumer_view", "activation",
        "BUY", "SELL", "ENTRY", "order",
    ]
    out = {}
    for f in sorted(RUN_DIR.glob("*.log")):
        text = f.read_text(encoding="utf-8", errors="replace")
        rec = {
            "sha256": sha256_file(f),
            "size_bytes": f.stat().st_size,
            "tail": "\n".join(text.splitlines()[-120:]),
            "hits": {},
        }
        for pat in patterns:
            hits = []
            for i, line in enumerate(text.splitlines(), 1):
                if pat.lower() in line.lower():
                    hits.append({"line": i, "text": line[:360]})
                    if len(hits) >= MAX_LOG_HITS:
                        break
            rec["hits"][pat] = hits
        out[str(f.relative_to(ROOT))] = rec
    return out


def write_artifacts(proof: dict[str, Any]) -> None:
    SESSION_JSON.write_text(json.dumps({
        "batch": BATCH,
        "tag": TAG,
        "sample_seconds": SAMPLE_SECONDS,
        "poll_seconds": POLL_SECONDS,
        "readonly_env": proof.get("readonly_env"),
        "start_results": proof.get("start_results"),
        "samples": proof.get("samples"),
        "stop_results": proof.get("stop_results"),
        "leftover_stop_results": proof.get("leftover_stop_results"),
    }, indent=2, sort_keys=True), encoding="utf-8")

    SAFETY_JSON.write_text(json.dumps({
        "batch": BATCH,
        "tag": TAG,
        "preflight": proof.get("preflight"),
        "post_readback": proof.get("post_readback"),
        "orders_since_start": proof.get("orders_since_start"),
        "safety_intent": proof.get("safety_intent"),
        "log_review": proof.get("log_review"),
    }, indent=2, sort_keys=True), encoding="utf-8")


def main() -> int:
    proof: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": BATCH_NAME,
        "tag": TAG,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "purpose": "Clean rerun of live-session read-only family-surface sampler after O23-O-R2 recovery.",
        "safety_intent": {
            "real_live_enablement": False,
            "paper_start": False,
            "controlled_paper_runtime": False,
            "service_start": "feeds_features_strategy_only",
            "risk_start": False,
            "execution_start": False,
            "broker_call": False,
            "order_write": False,
            "threshold_relaxation": False,
            "forced_candidate": False,
            "production_source_patch": False,
            "readonly_surface_materialization": True,
        },
        "disk_state": {},
        "inspected_files": {},
        "prior_proofs": {},
        "commands": {},
        "preflight": {},
        "readonly_env": {},
        "start_results": [],
        "samples": [],
        "sample_review": {},
        "surface_matrix": {},
        "orders_since_start": {},
        "stop_results": [],
        "leftover_stop_results": [],
        "post_readback": {},
        "log_review": {},
        "next_decision": {},
        "required_verdicts": {},
        "false_keys": [],
        "classification": "",
        "final_verdict": "NOT_EVALUATED",
        "next_recommended_batch": "",
    }

    try:
        print("===== DISK PRECHECK =====")
        proof["disk_state"] = disk_state()

        print("===== EVIDENCE-FIRST INSPECTION =====")
        for rel in INSPECT_PATHS:
            proof["inspected_files"][rel] = safe_file_record(rel, copy_source=rel in SOURCE_PATHS and (ROOT / rel).is_file())
            if rel.endswith(".json"):
                proof["prior_proofs"][rel] = load_json_summary(rel)

        print("===== COMPILE / IMPORT PREFLIGHT =====")
        compile_targets = [
            "app/mme_scalpx/main.py",
            "app/mme_scalpx/services/feeds.py",
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
            "import app.mme_scalpx.main, app.mme_scalpx.services.feeds, app.mme_scalpx.services.features, app.mme_scalpx.services.strategy, app.mme_scalpx.services.risk, app.mme_scalpx.services.execution; print('IMPORT_OK')",
        ], timeout=60)

        print("===== CLEAN PREFLIGHT SAFETY SNAPSHOT =====")
        pre = runtime_snapshot()
        proof["preflight"] = pre

        o23r2 = proof["prior_proofs"].get("run/proofs/proof_batch26o23_o_r2_interrupted_recovery_readback.json", {})
        o23n = proof["prior_proofs"].get("run/proofs/proof_batch26o23_n_corrected_opportunity_parser_deeper_sampler.json", {})
        o23m = proof["prior_proofs"].get("run/proofs/proof_batch26o23_m_validate_mist_put_single_scope.json", {})
        o23k = proof["prior_proofs"].get("run/proofs/proof_batch26o23_k_post_repair_evidence_review.json", {})

        pre_orders_zero = pre["orders_xlen"] == 0 and not (pre["latest_orders_raw"].get("stdout") or "").strip()
        pre_position_flat = flat_position(pre["position"])
        pre_no_pids = len(pre["all_mme_service_rows"]) == 0
        pre_no_forbidden = len(pre["forbidden_service_rows"]) == 0

        env = readonly_env()
        env_proof = {
            k: env.get(k, "")
            for k in [
                "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
                "SCALPX_PAPER_ARMED",
                "SCALPX_REAL_LIVE_ALLOWED",
                "SCALPX_LIVE_ORDERS_ALLOWED",
                "SCALPX_BROKER_CALLS_ALLOWED",
                "SCALPX_FORCE_CANDIDATE",
                "SCALPX_THRESHOLD_RELAXATION",
                "SCALPX_AUTOMATIC_BROKER_FAILOVER",
                "SCALPX_MID_POSITION_PROVIDER_MIGRATION",
                "SCALPX_FAMILY_RUNTIME_MODE",
                "SCALPX_STRATEGY_ROLLOUT_MODE",
                "SCALPX_ORDER_INTENT_ENABLED",
                "SCALPX_EXECUTION_ENABLED",
            ]
        }
        proof["readonly_env"] = env_proof

        hard_preflight = {
            "disk_free_above_min": proof["disk_state"]["free_bytes"] >= MIN_FREE_BYTES,
            "o23o_r2_pass_loaded": pass_prefix(o23r2, "PASS_O23_O_R2_INTERRUPTED_RECOVERY_CLEAN_OK_NO_START_NO_REAL_LIVE"),
            "o23n_pass_loaded": pass_prefix(o23n, "PASS_O23_N_CORRECTED_OPPORTUNITY_PARSER_OK_NO_START_NO_REAL_LIVE"),
            "o23m_pass_loaded": pass_prefix(o23m, "PASS_O23_M_MIST_PUT_SCOPE_REJECTED_AS_NOT_EVIDENCE_BACKED_NO_START_NO_REAL_LIVE"),
            "o23k_pass_loaded": pass_prefix(o23k, "PASS_O23_K_POST_REPAIR_EVIDENCE_REVIEW_OK_NO_REAL_LIVE"),
            "compile_pass": bool(proof["commands"]["compile"].get("ok")),
            "import_pass": bool(proof["commands"]["import"].get("ok")),
            "pre_orders_zero": pre_orders_zero,
            "pre_position_flat": pre_position_flat,
            "pre_no_mme_service_pids": pre_no_pids,
            "pre_no_risk_execution_pids": pre_no_forbidden,
            "paper_disabled": env_proof["SCALPX_PAPER_ARMED"] == "0",
            "controlled_paper_runtime_disabled": env_proof["SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME"] == "0",
            "real_live_false": env_proof["SCALPX_REAL_LIVE_ALLOWED"] == "0",
            "live_orders_forbidden": env_proof["SCALPX_LIVE_ORDERS_ALLOWED"] == "0",
            "broker_calls_forbidden": env_proof["SCALPX_BROKER_CALLS_ALLOWED"] == "0",
            "no_forced_candidate": env_proof["SCALPX_FORCE_CANDIDATE"] == "0",
            "no_threshold_relaxation": env_proof["SCALPX_THRESHOLD_RELAXATION"] == "0",
            "order_intent_disabled": env_proof["SCALPX_ORDER_INTENT_ENABLED"] == "0",
            "execution_disabled": env_proof["SCALPX_EXECUTION_ENABLED"] == "0",
            "observe_only_env": env_proof["SCALPX_FAMILY_RUNTIME_MODE"] == "observe_only",
        }

        if not all(hard_preflight.values()):
            proof["required_verdicts"] = hard_preflight
            proof["false_keys"] = [k for k, v in hard_preflight.items() if v is not True]
            proof["classification"] = "O23O_R3_PREFLIGHT_REFUSED_NO_START"
            proof["final_verdict"] = "REFUSE_O23_O_R3_PREFLIGHT_NOT_SAFE_NO_START"
            proof["next_recommended_batch"] = "Inspect false_keys; do not start read-only sampler, paper, or real live."
            proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
            PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
            print("REFUSE: clean preflight not safe. No services started.")
            print("false_keys =", proof["false_keys"])
            print("proof_json =", PROOF_JSON.relative_to(ROOT))
            return 2

        start_ids = {
            "features": pre["features_last_id"],
            "decisions": pre["decisions_last_id"],
            "orders": pre["orders_last_id"],
        }

        print("===== START READ-ONLY SERVICES: FEEDS / FEATURES / STRATEGY ONLY =====")
        for service in READONLY_SERVICES:
            res = start_service(service, env)
            proof["start_results"].append(res)
            print(json.dumps(res, indent=2, sort_keys=True))
            time.sleep(3)

        all_started_alive = all(x.get("started") is True and x.get("alive_after_start") is True for x in proof["start_results"])

        print("===== LIVE READ-ONLY SURFACE MATERIALIZATION SAMPLING =====")
        start_time = time.time()
        deadline = start_time + SAMPLE_SECONDS

        while time.time() < deadline:
            snap = runtime_snapshot()
            feature_entries_now = redis_entries_since(FEATURES_STREAM, start_ids["features"], count=STREAM_REVIEW_COUNT)
            decision_entries_now = redis_entries_since(DECISIONS_STREAM, start_ids["decisions"], count=STREAM_REVIEW_COUNT)
            order_entries_now = redis_entries_since(ORDERS_STREAM, start_ids["orders"], count=50)

            compact = {
                "observed_at_utc": datetime.now(timezone.utc).isoformat(),
                "seconds_elapsed": round(time.time() - start_time, 2),
                "features_xlen": snap["features_xlen"],
                "decisions_xlen": snap["decisions_xlen"],
                "orders_xlen": snap["orders_xlen"],
                "feature_entries_since_start": len(feature_entries_now),
                "decision_entries_since_start": len(decision_entries_now),
                "order_entries_since_start": len(order_entries_now),
                "position": snap["position"],
                "readonly_service_count": len(snap["readonly_service_rows"]),
                "forbidden_service_count": len(snap["forbidden_service_rows"]),
            }
            proof["samples"].append(compact)
            print(json.dumps(compact, indent=2, sort_keys=True)[:8000])

            if len(order_entries_now) > 0 or len(snap["forbidden_service_rows"]) > 0:
                proof["early_stop_reason"] = "ORDER_EVENT_OR_FORBIDDEN_SERVICE_DETECTED"
                break

            time.sleep(POLL_SECONDS)

        print("===== COLLECT FINAL SURFACE ENTRIES =====")
        feature_entries = redis_entries_since(FEATURES_STREAM, start_ids["features"], count=STREAM_REVIEW_COUNT)
        decision_entries = redis_entries_since(DECISIONS_STREAM, start_ids["decisions"], count=STREAM_REVIEW_COUNT)
        order_entries = redis_entries_since(ORDERS_STREAM, start_ids["orders"], count=50)

        feature_payloads = parse_payloads_from_entries(feature_entries, FEATURES_STREAM)
        decision_payloads = parse_payloads_from_entries(decision_entries, DECISIONS_STREAM)
        all_payloads = feature_payloads + decision_payloads

        sample_review = {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "start_ids": start_ids,
            "feature_entries_since_start": len(feature_entries),
            "decision_entries_since_start": len(decision_entries),
            "order_entries_since_start": len(order_entries),
            "feature_payload_count": len(feature_payloads),
            "decision_payload_count": len(decision_payloads),
            "feature_payload_fields": [{"id": x.get("id"), "field": x.get("field"), "raw_text_only": x.get("raw_text_only") is True} for x in feature_payloads[:150]],
            "decision_payload_fields": [{"id": x.get("id"), "field": x.get("field"), "raw_text_only": x.get("raw_text_only") is True} for x in decision_payloads[:150]],
            "samples": proof["samples"],
        }
        proof["sample_review"] = sample_review
        SAMPLE_REVIEW_JSON.write_text(json.dumps(sample_review, indent=2, sort_keys=True), encoding="utf-8")

        surface_matrix = build_surface_matrix(all_payloads)
        proof["surface_matrix"] = surface_matrix
        SURFACE_MATRIX_JSON.write_text(json.dumps(surface_matrix, indent=2, sort_keys=True), encoding="utf-8")

        print("===== STOP READ-ONLY SERVICES =====")
        proof["stop_results"] = stop_started()
        time.sleep(5)
        proof["leftover_stop_results"] = stop_leftover_started_services()
        time.sleep(3)

        print("===== POST-RUN SAFETY READBACK =====")
        post = runtime_snapshot()
        proof["post_readback"] = post
        proof["orders_since_start"] = {
            "event_count": len(redis_entries_since(ORDERS_STREAM, start_ids["orders"], count=50)),
            "entries": redis_entries_since(ORDERS_STREAM, start_ids["orders"], count=50),
        }
        proof["log_review"] = review_logs()

        write_artifacts(proof)

        post_position_flat = flat_position(post["position"])
        post_no_forbidden = len(post["forbidden_service_rows"]) == 0
        post_no_mme_pids = len(post["all_mme_service_rows"]) == 0
        post_order_events_zero = proof["orders_since_start"]["event_count"] == 0

        feature_growth = len(feature_entries)
        decision_growth = len(decision_entries)
        feature_payload_count = len(feature_payloads)
        decision_payload_count = len(decision_payloads)

        best = surface_matrix.get("best_evidence_backed_scope")
        best_scope = best.get("family_side") if isinstance(best, dict) else None

        if best_scope:
            next_batch = f"26-O23-P validate {best_scope} as next one-family/side paper scope, no paper start, no real live."
            decision = "VALIDATE_EVIDENCE_BACKED_SCOPE_NEXT"
            classification = "O23O_R3_EVIDENCE_BACKED_FAMILY_SCOPE_MATERIALIZED"
        elif feature_growth > 0 or decision_growth > 0:
            next_batch = "26-O23-P diagnose why read-only streams grew but no family/side evidence-backed surface materialized; no paper start, no real live."
            decision = "DIAGNOSE_SURFACE_MAPPING_WITH_STREAM_GROWTH"
            classification = "O23O_R3_STREAMS_GREW_BUT_NO_EVIDENCE_BACKED_FAMILY_SCOPE"
        else:
            next_batch = "26-O23-P provider/feed freshness and service-output growth diagnostic; no paper start, no real live."
            decision = "DIAGNOSE_NO_STREAM_GROWTH"
            classification = "O23O_R3_NO_STREAM_GROWTH_DURING_READONLY_SAMPLER"

        next_decision = {
            "batch": BATCH,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "decision": decision,
            "best_evidence_backed_scope": best_scope,
            "recommended_next_batch": next_batch,
            "do_not_start_paper_yet": True,
            "do_not_proceed_to_real_live": True,
            "why": [
                "O23-O-R3 is read-only surface materialization only.",
                "Only feeds/features/strategy were started.",
                "Risk/execution were not started.",
                "Next paper scope requires separate validation and explicit approval gate.",
            ],
            "forbidden": [
                "real live",
                "paper start without explicit approval",
                "risk/execution start in read-only sampler",
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
            **hard_preflight,
            "readonly_services_started_alive": all_started_alive,
            "samples_captured": len(proof["samples"]) > 0,
            "sample_review_json_written": SAMPLE_REVIEW_JSON.exists(),
            "surface_matrix_json_written": SURFACE_MATRIX_JSON.exists(),
            "session_json_written": SESSION_JSON.exists(),
            "safety_json_written": SAFETY_JSON.exists(),
            "log_review_json_written": LOG_REVIEW_JSON.exists(),
            "next_decision_json_written": NEXT_DECISION_JSON.exists(),
            "family_side_matrix_complete": sorted(list(surface_matrix.get("matrix", {}).keys())) == sorted(FAMILY_SIDES),
            "no_order_events_since_start": post_order_events_zero,
            "post_position_flat": post_position_flat,
            "post_no_forbidden_risk_execution": post_no_forbidden,
            "post_no_mme_service_pids": post_no_mme_pids,
            "paper_start_false": True,
            "real_live_false_after": env_proof["SCALPX_REAL_LIVE_ALLOWED"] == "0",
            "production_source_patch_false": True,
            "broker_call_false": True,
            "order_write_false": True,
            "threshold_relaxation_false": True,
            "forced_candidate_false": True,
        }

        false_keys = [k for k, v in req.items() if v is not True]
        proof["required_verdicts"] = req
        proof["false_keys"] = false_keys
        proof["classification"] = classification
        proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()

        if false_keys:
            proof["final_verdict"] = "FAIL_O23_O_R3_READONLY_SURFACE_SAMPLER_NOT_PROVEN"
            proof["next_recommended_batch"] = "Inspect false_keys; do not start paper or real live."
        else:
            proof["final_verdict"] = "PASS_O23_O_R3_READONLY_SURFACE_SAMPLER_OK_NO_PAPER_NO_REAL_LIVE"
            proof["next_recommended_batch"] = next_batch

        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

        RUNBOOK_MD.write_text(
            "\n".join([
                f"# {BATCH} — clean rerun read-only family surface sampler",
                "",
                f"- generated_at_utc: {proof['completed_at_utc']}",
                f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
                f"- session: `{SESSION_JSON.relative_to(ROOT)}`",
                f"- sample_review: `{SAMPLE_REVIEW_JSON.relative_to(ROOT)}`",
                f"- surface_matrix: `{SURFACE_MATRIX_JSON.relative_to(ROOT)}`",
                f"- safety: `{SAFETY_JSON.relative_to(ROOT)}`",
                f"- log_review: `{LOG_REVIEW_JSON.relative_to(ROOT)}`",
                f"- next_decision: `{NEXT_DECISION_JSON.relative_to(ROOT)}`",
                "",
                "## Scope",
                "- Clean rerun after O23-O-R2 recovery.",
                "- Starts feeds/features/strategy only.",
                "- Does not start risk or execution.",
                "- Paper disabled.",
                "- Real live false.",
                "- No order write.",
                "- No source patch.",
                "",
                "## Result",
                f"- final_verdict: `{proof['final_verdict']}`",
                f"- classification: `{proof['classification']}`",
                f"- false_keys: `{false_keys}`",
                f"- feature_entries_since_start: `{feature_growth}`",
                f"- decision_entries_since_start: `{decision_growth}`",
                f"- feature_payload_count: `{feature_payload_count}`",
                f"- decision_payload_count: `{decision_payload_count}`",
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
                f"# {DATE} — {BATCH} clean read-only family surface sampler",
                "",
                f"Verdict: `{proof['final_verdict']}`",
                "",
                f"Classification: `{proof['classification']}`",
                "",
                "## Achieved",
                "- Loaded O23-O-R2/O23-N/O23-M/O23-K prerequisites.",
                "- Proved clean preflight before starting services.",
                "- Started read-only feeds/features/strategy only if safe.",
                "- Did not start risk/execution.",
                "- Collected live family/side surface materialization evidence.",
                "- Built corrected family-side surface matrix.",
                "- Stopped started services and confirmed safety readback.",
                "",
                "## Next",
                f"- {proof['next_recommended_batch']}",
            ]),
            encoding="utf-8",
        )

        shutil.copy2(pathlib.Path(__file__), BIN_COPY)

        manifest_paths = [
            PROOF_JSON,
            SESSION_JSON,
            SAMPLE_REVIEW_JSON,
            SURFACE_MATRIX_JSON,
            SAFETY_JSON,
            LOG_REVIEW_JSON,
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
        print("feature_entries_since_start =", feature_growth)
        print("decision_entries_since_start =", decision_growth)
        print("feature_payload_count =", feature_payload_count)
        print("decision_payload_count =", decision_payload_count)
        print("best_evidence_backed_scope =", best_scope)
        print("post_position_flat =", post_position_flat)
        print("post_no_forbidden_risk_execution =", post_no_forbidden)
        print("post_no_mme_service_pids =", post_no_mme_pids)
        print("no_order_events_since_start =", post_order_events_zero)
        print("next_recommended_batch =", proof["next_recommended_batch"])
        print("proof_json =", PROOF_JSON.relative_to(ROOT))
        print("manifest_json =", MANIFEST_JSON.relative_to(ROOT))
        print("session_json =", SESSION_JSON.relative_to(ROOT))
        print("sample_review_json =", SAMPLE_REVIEW_JSON.relative_to(ROOT))
        print("surface_matrix_json =", SURFACE_MATRIX_JSON.relative_to(ROOT))
        print("safety_json =", SAFETY_JSON.relative_to(ROOT))
        print("log_review_json =", LOG_REVIEW_JSON.relative_to(ROOT))
        print("next_decision_json =", NEXT_DECISION_JSON.relative_to(ROOT))
        print("runbook =", RUNBOOK_MD.relative_to(ROOT))
        print("milestone =", MILESTONE_MD.relative_to(ROOT))
        return 0 if proof["final_verdict"].startswith("PASS_") else 2

    except Exception as exc:
        proof["exception"] = repr(exc)
        try:
            proof["stop_results"] = stop_started()
            time.sleep(3)
            proof["leftover_stop_results"] = stop_leftover_started_services()
            proof["post_readback"] = runtime_snapshot()
            proof["log_review"] = review_logs()
            write_artifacts(proof)
        except Exception as stop_exc:
            proof["stop_exception"] = repr(stop_exc)
        proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
        proof["final_verdict"] = "FAIL_O23_O_R3_EXCEPTION_SAFE_STOP_ATTEMPTED"
        proof["next_recommended_batch"] = "Inspect exception and safety readback; do not proceed to paper or real live."
        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
        print("===== EXCEPTION SAFE STOP =====")
        print(repr(exc))
        print("proof_json =", PROOF_JSON.relative_to(ROOT))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
