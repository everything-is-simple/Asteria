from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.data.daily_incremental_hardening import (
    DataDailyIncrementalHardeningRequest,
    run_data_daily_incremental_hardening,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Data Foundation daily incremental hardening sample proof."
    )
    parser.add_argument("--source-root", default="H:/tdx_offline_Data")
    parser.add_argument("--target-root", default="H:/Asteria-data")
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--run-id", required=True)
    parser.add_argument(
        "--mode",
        choices=["daily_incremental", "resume", "audit-only"],
        required=True,
    )
    parser.add_argument("--start-dt")
    parser.add_argument("--end-dt")
    parser.add_argument("--symbol-limit", type=int)
    args = parser.parse_args()

    summary = run_data_daily_incremental_hardening(
        DataDailyIncrementalHardeningRequest(
            source_root=Path(args.source_root),
            target_root=Path(args.target_root),
            temp_root=Path(args.temp_root),
            report_root=Path(args.report_root),
            run_id=args.run_id,
            mode=args.mode,
            start_dt=args.start_dt,
            end_dt=args.end_dt,
            symbol_limit=args.symbol_limit,
        )
    )
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0 if summary.status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
