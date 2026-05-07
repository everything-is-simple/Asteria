from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.portfolio_plan.bootstrap import run_portfolio_plan_bounded_proof
from asteria.portfolio_plan.contracts import (
    PORTFOLIO_PLAN_RULE_VERSION,
    PORTFOLIO_PLAN_SCHEMA_VERSION,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Portfolio Plan bounded proof.")
    parser.add_argument("--source-position-db", default="H:/Asteria-data/position.duckdb")
    parser.add_argument(
        "--target-portfolio-plan-db",
        default="H:/Asteria-data/portfolio_plan.duckdb",
    )
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--validated-root", default="H:/Asteria-Validated")
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument("--mode", choices=["bounded", "resume"], default="bounded")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--start-dt")
    parser.add_argument("--end-dt")
    parser.add_argument("--symbol-limit", type=int)
    parser.add_argument("--schema-version", default=PORTFOLIO_PLAN_SCHEMA_VERSION)
    parser.add_argument("--portfolio-plan-rule-version", default=PORTFOLIO_PLAN_RULE_VERSION)
    parser.add_argument("--source-position-release-version", required=True)
    parser.add_argument("--source-position-run-id")
    args = parser.parse_args()
    summary = run_portfolio_plan_bounded_proof(
        source_position_db=Path(args.source_position_db),
        target_portfolio_plan_db=Path(args.target_portfolio_plan_db),
        report_root=Path(args.report_root),
        validated_root=Path(args.validated_root),
        temp_root=Path(args.temp_root),
        run_id=args.run_id,
        mode=args.mode,
        source_position_release_version=args.source_position_release_version,
        source_position_run_id=args.source_position_run_id,
        start_dt=args.start_dt,
        end_dt=args.end_dt,
        symbol_limit=args.symbol_limit,
        schema_version=args.schema_version,
        portfolio_plan_rule_version=args.portfolio_plan_rule_version,
    )
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0 if summary.hard_fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
