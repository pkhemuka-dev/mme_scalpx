from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _read_ndjson(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows


def build_daily_summary(day: str) -> dict[str, Any]:
    base = Path("run/paper_shadow_lifecycle")
    entries = _read_ndjson(base / f"entries_{day}.ndjson")
    exits = _read_ndjson(base / f"exits_{day}.ndjson")

    pnl = [float(x.get("pnl_rupees_net_proxy") or 0.0) for x in exits]
    wins = [x for x in pnl if x > 0]
    losses = [x for x in pnl if x <= 0]

    by_family: dict[str, dict[str, Any]] = {}
    for x in exits:
        fam = str(x.get("family_id") or "UNKNOWN")
        by_family.setdefault(fam, {"count": 0, "pnl_rupees_net_proxy": 0.0})
        by_family[fam]["count"] += 1
        by_family[fam]["pnl_rupees_net_proxy"] += float(x.get("pnl_rupees_net_proxy") or 0.0)

    return {
        "day": day,
        "entries_count": len(entries),
        "exits_count": len(exits),
        "closed_pnl_rupees_net_proxy": round(sum(pnl), 2),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": round((len(wins) / len(pnl)) if pnl else 0.0, 4),
        "by_family": by_family,
        "entries": entries[-20:],
        "exits": exits[-20:],
        "broker_order": 0,
        "paper_engine_order": 0,
        "risk_started": 0,
        "execution_started": 0,
    }


def write_daily_summary(day: str) -> Path:
    base = Path("run/paper_shadow_lifecycle")
    base.mkdir(parents=True, exist_ok=True)
    path = base / f"summary_{day}.json"
    path.write_text(json.dumps(build_daily_summary(day), indent=2, sort_keys=True), encoding="utf-8")
    return path
