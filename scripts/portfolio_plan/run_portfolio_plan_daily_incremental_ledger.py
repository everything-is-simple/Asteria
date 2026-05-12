from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.portfolio_plan.contracts import PortfolioPlanDailyIncrementalLedgerRequest
from asteria.portfolio_plan.daily_incremental_ledger import (
    run_portfolio_plan_daily_incremental_ledger,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the Portfolio Plan day daily incremental sample ledger."
    )
    parser.add_argument(
        "--source-position-db", default="H:/Asteria-temp/position-target/position.duckdb"
    )
    parser.add_argument(
        "--target-portfolio-plan-db",
        default="H:/Asteria-temp/portfolio-plan-target/portfolio_plan.duckdb",
    )
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--run-id", default="downstream-daily-incremental-runner-build-card")
    parser.add_argument(
        "--mode", choices=["daily_incremental", "resume", "audit-only"], default="daily_incremental"
    )
    parser.add_argument(
        "--position-daily-impact-scope-path",
        default="H:/Asteria-temp/position/downstream-daily-incremental-runner-build-card/daily-impact-scope.json",
    )
    parser.add_argument(
        "--position-lineage-path",
        default="H:/Asteria-temp/position/downstream-daily-incremental-runner-build-card/lineage.json",
    )
    parser.add_argument(
        "--position-checkpoint-path",
        default="H:/Asteria-temp/position/downstream-daily-incremental-runner-build-card/checkpoint.json",
    )
    args = parser.parse_args()
    summary = run_portfolio_plan_daily_incremental_ledger(
        PortfolioPlanDailyIncrementalLedgerRequest(
            source_position_db=Path(args.source_position_db),
            target_portfolio_plan_db=Path(args.target_portfolio_plan_db),
            temp_root=Path(args.temp_root),
            report_root=Path(args.report_root),
            run_id=args.run_id,
            mode=args.mode,
            position_daily_impact_scope_path=Path(args.position_daily_impact_scope_path),
            position_lineage_path=Path(args.position_lineage_path),
            position_checkpoint_path=Path(args.position_checkpoint_path),
        )
    )
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0 if summary.status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
