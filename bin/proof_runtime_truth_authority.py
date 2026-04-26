#!/usr/bin/env python3
from __future__ import annotations

"""
Batch 21 proof: runtime/config truth authority.

Purpose
-------
This proof does not change runtime behavior.
It inspects config/env/systemd/settings/proof artifacts and determines whether
paper_armed can be allowed from configuration truth alone.

It is intentionally conservative:
- any runtime-mode disagreement blocks paper_armed
- any live-orders/trading-enabled ambiguity blocks paper_armed
- absence of config evidence creates WARN/blocked, not PASS
"""

import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "run" / "proofs" / "proof_runtime_truth_authority.json"

MODE_KEYS = {
    "MME_RUNTIME_MODE",
    "SCALPX_RUNTIME_MODE",
    "RUNTIME_MODE",
    "MODE",
}
ORDER_KEYS = {
    "ALLOW_LIVE_ORDERS",
    "MME_ALLOW_LIVE_ORDERS",
    "TRADING_ENABLED",
    "MME_TRADING_ENABLED",
    "ENABLE_LIVE_ORDERS",
    "LIVE_ORDERS_ENABLED",
}
SECRET_HINTS = ("TOKEN", "SECRET", "PASSWORD", "API_KEY", "ACCESS_KEY", "PRIVATE_KEY", "CLIENT_SECRET")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except Exception:
        return ""


def run_cmd(args: list[str], timeout: int = 15) -> dict[str, Any]:
    try:
        p = subprocess.run(
            args,
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "cmd": args,
            "returncode": p.returncode,
            "stdout": p.stdout[-8000:],
            "stderr": p.stderr[-8000:],
        }
    except Exception as exc:
        return {"cmd": args, "error": repr(exc)}


def parse_env_lines(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip("'").strip('"')
        if k:
            out[k] = v
    return out


def extract_systemd_env(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    # Handles: Environment="A=B" A=B
    for m in re.finditer(r"Environment=(.*)", text):
        value = m.group(1).strip()
        parts = re.findall(r'"([^"]+)"|(\S+)', value)
        for a, b in parts:
            item = a or b
            if "=" in item:
                k, v = item.split("=", 1)
                out[k.strip()] = v.strip().strip("'").strip('"')
    return out


def extract_environment_files(systemd_text: str) -> list[str]:
    files: list[str] = []
    for m in re.finditer(r"EnvironmentFile=([^\n]+)", systemd_text):
        raw = m.group(1).strip()
        raw = raw.lstrip("-").strip().strip('"').strip("'")
        if raw:
            files.append(raw)
    return files


def collect_mode_lines(path: Path) -> list[dict[str, Any]]:
    text = read_text(path)
    hits = []
    for idx, line in enumerate(text.splitlines(), 1):
        low = line.lower()
        if "runtime" in low or "mode" in low or "paper" in low or "live" in low:
            if re.search(r"\b(mode|runtime_mode|runtime\.mode|allowed_modes|allow_live_orders|trading_enabled)\b", low):
                safe_line = line
                for hint in SECRET_HINTS:
                    if hint.lower() in low:
                        safe_line = re.sub(r"(:|=)\s*.+", r"\1 <REDACTED>", line)
                        break
                hits.append({"line": idx, "text": safe_line[:500]})
    return hits[:80]


def normalize_mode(v: str | None) -> str | None:
    if v is None:
        return None
    s = str(v).strip().strip("'").strip('"').lower()
    if not s:
        return None
    aliases = {
        "prod": "live",
        "production": "live",
        "paper_trading": "paper",
        "paper-armed": "paper_armed",
        "paperarmed": "paper_armed",
        "report": "report_only",
        "report-only": "report_only",
        "hold": "report_only",
        "hold_only": "report_only",
    }
    return aliases.get(s, s)


def truthy_falsey(v: str | None) -> str | None:
    if v is None:
        return None
    s = str(v).strip().strip("'").strip('"').lower()
    if s in {"1", "true", "yes", "y", "on", "enabled"}:
        return "true"
    if s in {"0", "false", "no", "n", "off", "disabled"}:
        return "false"
    return s or None


def add_signal(signals: list[dict[str, Any]], source: str, key: str, value: Any, path: str | None = None) -> None:
    if value is None:
        return
    signals.append({"source": source, "key": key, "value": str(value), "path": path})


def main() -> int:
    findings: list[dict[str, Any]] = []
    mode_signals: list[dict[str, Any]] = []
    order_signals: list[dict[str, Any]] = []

    # Process env
    for k in sorted(MODE_KEYS):
        if k in os.environ:
            add_signal(mode_signals, "process_env", k, os.environ.get(k))
    for k in sorted(ORDER_KEYS):
        if k in os.environ:
            add_signal(order_signals, "process_env", k, os.environ.get(k))

    # Project env files
    env_paths = [
        ROOT / "etc" / "project.env",
        ROOT / ".env",
        ROOT / "etc" / "runtime.env",
    ]
    env_values_by_path: dict[str, dict[str, str]] = {}
    for p in env_paths:
        if p.exists():
            vals = parse_env_lines(read_text(p))
            env_values_by_path[str(p.relative_to(ROOT))] = {
                k: ("<REDACTED>" if any(h in k.upper() for h in SECRET_HINTS) else v)
                for k, v in vals.items()
            }
            for k in MODE_KEYS:
                add_signal(mode_signals, "env_file", k, vals.get(k), str(p.relative_to(ROOT)))
            for k in ORDER_KEYS:
                add_signal(order_signals, "env_file", k, vals.get(k), str(p.relative_to(ROOT)))

    # runtime.yaml surface scan
    config_paths = [
        ROOT / "etc" / "runtime.yaml",
        ROOT / "etc" / "config_registry.yaml",
        ROOT / "etc" / "proof_registry.yaml",
        ROOT / "app" / "mme_scalpx" / "core" / "settings.py",
        ROOT / "app" / "mme_scalpx" / "main.py",
    ]
    config_evidence = {}
    for p in config_paths:
        config_evidence[str(p.relative_to(ROOT))] = {
            "exists": p.exists(),
            "mode_related_lines": collect_mode_lines(p) if p.exists() else [],
        }

    # Direct regex extraction from runtime.yaml for common mode keys.
    runtime_yaml = ROOT / "etc" / "runtime.yaml"
    if runtime_yaml.exists():
        txt = read_text(runtime_yaml)
        for idx, line in enumerate(txt.splitlines(), 1):
            m = re.match(r"^\s*(mode|runtime_mode|runtime_mode_name|allow_live_orders|trading_enabled)\s*:\s*['\"]?([^'\"\s#]+)", line)
            if m:
                k, v = m.group(1), m.group(2)
                if "mode" in k:
                    add_signal(mode_signals, "runtime_yaml", k, v, f"etc/runtime.yaml:{idx}")
                else:
                    add_signal(order_signals, "runtime_yaml", k, v, f"etc/runtime.yaml:{idx}")

    # Existing runtime proof artifacts, if present.
    existing_runtime_proofs = {}
    for rel in [
        "run/proofs/runtime_effective_config.json",
        "run/proofs/proof_config_runtime_truth.json",
    ]:
        p = ROOT / rel
        if p.exists():
            try:
                data = json.loads(read_text(p))
            except Exception as exc:
                data = {"parse_error": repr(exc)}
            existing_runtime_proofs[rel] = data

            # Pull known fields from prior proof formats.
            if isinstance(data, dict):
                for k, v in data.items():
                    lk = str(k).lower()
                    if "mode" in lk and isinstance(v, (str, int, float, bool)):
                        add_signal(mode_signals, rel, str(k), v, rel)
                    if ("allow_live_orders" in lk or "trading_enabled" in lk) and isinstance(v, (str, int, float, bool)):
                        add_signal(order_signals, rel, str(k), v, rel)

    # systemd evidence
    systemd_cat = run_cmd(["systemctl", "cat", "scalpx-mme.service"])
    systemd_show = run_cmd(["systemctl", "show", "scalpx-mme.service", "--property=Environment", "--property=FragmentPath", "--property=DropInPaths"])
    systemd_text = ""
    if systemd_cat.get("returncode") == 0:
        systemd_text += str(systemd_cat.get("stdout", ""))
    if systemd_show.get("returncode") == 0:
        systemd_text += "\n" + str(systemd_show.get("stdout", ""))

    systemd_env = extract_systemd_env(systemd_text)
    for k in MODE_KEYS:
        add_signal(mode_signals, "systemd", k, systemd_env.get(k))
    for k in ORDER_KEYS:
        add_signal(order_signals, "systemd", k, systemd_env.get(k))

    for env_file in extract_environment_files(systemd_text):
        p = Path(env_file)
        if p.exists():
            vals = parse_env_lines(read_text(p))
            for k in MODE_KEYS:
                add_signal(mode_signals, "systemd_environment_file", k, vals.get(k), env_file)
            for k in ORDER_KEYS:
                add_signal(order_signals, "systemd_environment_file", k, vals.get(k), env_file)

    normalized_modes = sorted({
        m for m in (normalize_mode(s.get("value")) for s in mode_signals)
        if m is not None and m not in {"", "none", "null"}
    })

    normalized_order_values = [
        {**s, "normalized": truthy_falsey(s.get("value"))}
        for s in order_signals
    ]

    has_live_enabled_signal = any(s.get("normalized") == "true" for s in normalized_order_values)
    has_order_ambiguity = len(normalized_order_values) == 0

    if len(normalized_modes) == 0:
        findings.append({
            "severity": "P0",
            "owner": "config/runtime",
            "finding": "No runtime mode signal could be established from env/runtime.yaml/systemd/settings/proofs.",
        })
    elif len(normalized_modes) > 1:
        findings.append({
            "severity": "P0",
            "owner": "config/runtime",
            "finding": "Runtime mode sources disagree.",
            "normalized_modes": normalized_modes,
        })

    if has_live_enabled_signal:
        findings.append({
            "severity": "P0",
            "owner": "config/runtime",
            "finding": "At least one live-order/trading-enabled signal is true.",
        })
    elif has_order_ambiguity:
        findings.append({
            "severity": "P1",
            "owner": "config/runtime",
            "finding": "No explicit allow_live_orders/trading_enabled signal was found; paper_armed remains blocked until explicit false/controlled setting is proven.",
        })

    # Conservative gate: paper_armed only if exactly one runtime truth exists and no live orders true.
    paper_armed_allowed = (
        len(normalized_modes) == 1
        and normalized_modes[0] in {"paper", "paper_armed"}
        and not has_live_enabled_signal
        and not has_order_ambiguity
    )

    status = "PASS" if paper_armed_allowed else ("FAIL" if any(f["severity"] == "P0" for f in findings) else "WARN")

    result = {
        "proof": "proof_runtime_truth_authority",
        "generated_at": now_iso(),
        "project_root": str(ROOT),
        "status": status,
        "paper_armed_allowed": paper_armed_allowed,
        "normalized_runtime_modes": normalized_modes,
        "mode_signals": mode_signals,
        "order_signals": normalized_order_values,
        "findings": findings,
        "config_evidence": config_evidence,
        "env_values_by_path_redacted": env_values_by_path,
        "systemd": {
            "cat_returncode": systemd_cat.get("returncode"),
            "show_returncode": systemd_show.get("returncode"),
            "environment_files": extract_environment_files(systemd_text),
            "env_keys_found": sorted(systemd_env.keys()),
            "cat_error": systemd_cat.get("stderr", "")[-1000:],
            "show_error": systemd_show.get("stderr", "")[-1000:],
        },
        "existing_runtime_proofs_present": sorted(existing_runtime_proofs.keys()),
        "notes": [
            "This proof is read-only.",
            "This proof intentionally blocks paper_armed if runtime truth is ambiguous.",
            "A PASS here is necessary but not sufficient for paper_armed; provider/replay/risk/execution proofs must also pass.",
        ],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps({
        "status": status,
        "paper_armed_allowed": paper_armed_allowed,
        "normalized_runtime_modes": normalized_modes,
        "findings": findings,
        "out": str(OUT.relative_to(ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
