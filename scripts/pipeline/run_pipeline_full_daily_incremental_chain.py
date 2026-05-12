from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.pipeline.full_daily_incremental_chain import (
    PipelineFullDailyIncrementalChainRequest,
    run_pipeline_full_daily_incremental_chain,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the Pipeline full day daily incremental chain proof."
    )
    parser.add_argument("--source-root", default="H:/tdx_offline_Data")
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--run-id", default="pipeline-full-daily-incremental-chain-build-card")
    parser.add_argument(
        "--mode",
        choices=["daily_incremental", "resume", "audit-only"],
        default="daily_incremental",
    )
    parser.add_argument("--start-dt")
    parser.add_argument("--end-dt")
    parser.add_argument("--symbol-limit", type=int)
    args = parser.parse_args()

    summary = run_pipeline_full_daily_incremental_chain(
        PipelineFullDailyIncrementalChainRequest(
            source_root=Path(args.source_root),
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
