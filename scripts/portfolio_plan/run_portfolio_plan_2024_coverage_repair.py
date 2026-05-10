from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.portfolio_plan.coverage_repair import (
    run_portfolio_plan_2024_coverage_repair,
)
from asteria.portfolio_plan.coverage_repair_contracts import (
    PortfolioPlan2024CoverageRepairRequest,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the Portfolio Plan 2024 coverage repair card."
    )
    parser.add_argument("--repo-root", default="H:/Asteria")
    parser.add_argument("--source-system-db", default="H:/Asteria-data/system.duckdb")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--validated-root", default="H:/Asteria-Validated")
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--target-year", type=int, default=2024)
    args = parser.parse_args()

    summary = run_portfolio_plan_2024_coverage_repair(
        PortfolioPlan2024CoverageRepairRequest(
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
    return 0 if summary.status == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
