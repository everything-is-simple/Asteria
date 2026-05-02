from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.data.bootstrap import run_data_bootstrap
from asteria.data.contracts import DataBootstrapRequest


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap Asteria Data Foundation from TDX txt.")
    parser.add_argument("--source-root", default="H:/tdx_offline_Data")
    parser.add_argument("--target-root", default="H:/Asteria-data")
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument("--asset-type", choices=["stock", "index", "block"], required=True)
    parser.add_argument("--adj-mode", choices=["backward", "forward", "none", "all"], required=True)
    parser.add_argument(
        "--mode",
        choices=["bounded", "segmented", "full", "resume", "audit-only", "daily_incremental"],
        required=True,
    )
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--start-dt")
    parser.add_argument("--end-dt")
    parser.add_argument("--symbol-limit", type=int)
    args = parser.parse_args()

    summary = run_data_bootstrap(
        DataBootstrapRequest(
            source_root=Path(args.source_root),
            target_root=Path(args.target_root),
            temp_root=Path(args.temp_root),
            asset_type=args.asset_type,
            adj_mode=args.adj_mode,
            mode=args.mode,
            run_id=args.run_id,
            start_dt=args.start_dt,
            end_dt=args.end_dt,
            symbol_limit=args.symbol_limit,
        )
    )
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
