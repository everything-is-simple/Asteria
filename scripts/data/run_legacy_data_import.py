from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.data.contracts import LegacyImportRequest
from asteria.data.legacy_import import run_legacy_data_import


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import legacy Lifespan raw/base DuckDB facts into Asteria working DBs."
    )
    parser.add_argument("--raw-root", default="H:/Lifespan-data/raw")
    parser.add_argument("--base-root", default="H:/Lifespan-data/base")
    parser.add_argument("--target-root", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--asset-type", default="stock", choices=["stock"])
    parser.add_argument("--adj-mode", default="backward", choices=["backward"])
    parser.add_argument(
        "--timeframe",
        action="append",
        choices=["day", "week", "month"],
        dest="timeframes",
        help="Repeat to import a subset. Defaults to day, week, and month.",
    )
    args = parser.parse_args()

    summary = run_legacy_data_import(
        LegacyImportRequest(
            raw_root=Path(args.raw_root),
            base_root=Path(args.base_root),
            target_root=Path(args.target_root),
            run_id=args.run_id,
            asset_type=args.asset_type,
            adj_mode=args.adj_mode,
            timeframes=tuple(args.timeframes or ("day", "week", "month")),
        )
    )
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
