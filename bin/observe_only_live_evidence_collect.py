#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path.cwd()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.mme_scalpx.replay.live_evidence import (
    collect_observe_only_live_evidence_from_files,
    materialize_observe_only_live_evidence_contract,
)


def read_mapping(path_text: str) -> dict[str, str]:
    if not path_text:
        return {}
    path = Path(path_text)
    if not path.exists():
        raise SystemExit(f"evidence map does not exist: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("evidence map must be a JSON object")
    return {str(k): str(v) for k, v in data.items()}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Observe-only live evidence file collector. Does not start services, read Redis, or call brokers."
    )
    parser.add_argument("--capture-id", default="batch28b_contract_only")
    parser.add_argument("--root", default="")
    parser.add_argument("--evidence-map", default="")
    parser.add_argument("--contract-only", action="store_true")
    args = parser.parse_args()

    root = args.root or ("run/replay/parity/live_evidence/" + args.capture_id)

    if args.contract_only or not args.evidence_map:
        result = materialize_observe_only_live_evidence_contract(capture_id=args.capture_id, root=root)
    else:
        mapping = read_mapping(args.evidence_map)
        result = collect_observe_only_live_evidence_from_files(
            capture_id=args.capture_id,
            root=root,
            evidence_paths=mapping,
        )

    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
