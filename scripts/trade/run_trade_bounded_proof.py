from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.trade.bootstrap import run_trade_bounded_proof
from asteria.trade.contracts import TRADE_RULE_VERSION, TRADE_SCHEMA_VERSION


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Trade bounded proof.")
    parser.add_argument(
        "--source-portfolio-plan-db", default="H:/Asteria-data/portfolio_plan.duckdb"
    )
    parser.add_argument("--target-trade-db", default="H:/Asteria-data/trade.duckdb")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--validated-root", default="H:/Asteria-Validated")
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument("--mode", choices=["bounded", "resume"], default="bounded")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--timeframe", choices=["day"], default="day")
    parser.add_argument("--start-dt")
    parser.add_argument("--end-dt")
    parser.add_argument("--symbol-limit", type=int)
    parser.add_argument("--schema-version", default=TRADE_SCHEMA_VERSION)
    parser.add_argument("--trade-rule-version", default=TRADE_RULE_VERSION)
    parser.add_argument("--source-portfolio-plan-release-version", required=True)
    parser.add_argument("--source-portfolio-plan-run-id")
    args = parser.parse_args()
    summary = run_trade_bounded_proof(
        source_portfolio_plan_db=Path(args.source_portfolio_plan_db),
        target_trade_db=Path(args.target_trade_db),
        report_root=Path(args.report_root),
        validated_root=Path(args.validated_root),
        temp_root=Path(args.temp_root),
        run_id=args.run_id,
        source_portfolio_plan_release_version=args.source_portfolio_plan_release_version,
        source_portfolio_plan_run_id=args.source_portfolio_plan_run_id,
        start_dt=args.start_dt,
        end_dt=args.end_dt,
        symbol_limit=args.symbol_limit,
        schema_version=args.schema_version,
        trade_rule_version=args.trade_rule_version,
        mode=args.mode,
    )
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0 if summary.hard_fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
