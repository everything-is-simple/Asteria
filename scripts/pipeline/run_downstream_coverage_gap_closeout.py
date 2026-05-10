from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.pipeline.downstream_coverage_gap_closeout import (
    run_downstream_coverage_gap_closeout,
)
from asteria.pipeline.downstream_coverage_gap_closeout_contracts import (
    DownstreamCoverageGapCloseoutRequest,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the downstream coverage gap evidence closeout."
    )
    parser.add_argument("--repo-root", default="H:/Asteria")
    parser.add_argument("--source-system-db", default="H:/Asteria-data/system.duckdb")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--validated-root", default="H:/Asteria-Validated")
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--target-year", type=int, required=True)
    args = parser.parse_args()
    summary = run_downstream_coverage_gap_closeout(
        DownstreamCoverageGapCloseoutRequest(
            repo_root=Path(args.repo_root),
            source_system_db=Path(args.source_system_db),
            report_root=Path(args.report_root),
            validated_root=Path(args.validated_root),
            temp_root=Path(args.temp_root),
            run_id=args.run_id,
            target_year=args.target_year,
        )
    )
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
