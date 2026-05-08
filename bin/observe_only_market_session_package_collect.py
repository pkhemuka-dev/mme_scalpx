#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path.cwd()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.mme_scalpx.replay.live_package_collector import collect_actual_observe_only_evidence_package


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Collect observe_only evidence package from an actual generated evidence map. Copies files only."
    )
    parser.add_argument("--capture-id", required=True)
    parser.add_argument("--evidence-map", required=True)
    parser.add_argument("--root", required=True)
    parser.add_argument("--allow-deferred", action="store_true")
    args = parser.parse_args()

    result = collect_actual_observe_only_evidence_package(
        capture_id=args.capture_id,
        evidence_map=args.evidence_map,
        root=args.root,
        require_actual_map=not args.allow_deferred,
    )
    print(json.dumps(result, indent=2, sort_keys=True, default=str))

    if result.get("collection_deferred") and not args.allow_deferred:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
