#!/usr/bin/env python3
"""RAW replay artifact enrichment CLI.

RAW-AA7B-R2 thin CLI wrapper -- replay/research only.

This wrapper is intentionally thin. It exposes the existing
app.mme_scalpx.replay.raw_artifact_enricher.enrich_replay_artifacts function
without changing enrichment logic.

Safety:
- no broker IO
- no live Redis writes
- no order sending
- no strategy/risk/execution mutation
- no paper/live enablement
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.replay.raw_artifact_enricher import enrich_replay_artifacts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Replay/research-only RAW artifact enrichment wrapper."
    )
    parser.add_argument(
        "--project-root",
        default=str(PROJECT_ROOT),
        help="Project root to inspect for replay artifacts. Default: repository root.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Output directory for enriched RAW replay artifacts.",
    )
    parser.add_argument(
        "--run-id",
        required=True,
        help="Stable run id for the enrichment output.",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=100,
        help="Maximum source files to inspect.",
    )
    parser.add_argument(
        "--max-rows-per-file",
        type=int,
        default=5000,
        help="Maximum rows per source file.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned call only; do not execute enrichment.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    payload: dict[str, Any] = {
        "entrypoint": "bin/raw_replay_artifact_enrich.py",
        "mode": "dry_run" if args.dry_run else "execute",
        "project_root": str(Path(args.project_root)),
        "output_dir": str(Path(args.output_dir)),
        "run_id": args.run_id,
        "max_files": args.max_files,
        "max_rows_per_file": args.max_rows_per_file,
        "safety": {
            "broker_io_added": False,
            "redis_live_writer_added": False,
            "order_sending_added": False,
            "strategy_mutation_added": False,
            "risk_mutation_added": False,
            "execution_mutation_added": False,
            "paper_live_allowed": False,
            "promotion_allowed": False,
        },
    }

    if args.dry_run:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    result = enrich_replay_artifacts(
        project_root=Path(args.project_root),
        output_dir=Path(args.output_dir),
        run_id=args.run_id,
        max_files=args.max_files,
        max_rows_per_file=args.max_rows_per_file,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
