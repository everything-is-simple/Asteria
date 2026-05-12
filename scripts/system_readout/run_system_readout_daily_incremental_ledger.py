from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.system_readout.contracts import SystemReadoutDailyIncrementalLedgerRequest
from asteria.system_readout.daily_incremental_ledger import (
    run_system_readout_daily_incremental_ledger,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the System Readout day daily incremental sample ledger."
    )
    parser.add_argument(
        "--source-malf-service-db", default="H:/Asteria-temp/malf-target/malf_service_day.duckdb"
    )
    parser.add_argument("--source-alpha-root", default="H:/Asteria-temp/alpha-target")
    parser.add_argument("--source-signal-db", default="H:/Asteria-temp/signal-target/signal.duckdb")
    parser.add_argument(
        "--source-position-db", default="H:/Asteria-temp/position-target/position.duckdb"
    )
    parser.add_argument(
        "--source-portfolio-plan-db",
        default="H:/Asteria-temp/portfolio-plan-target/portfolio_plan.duckdb",
    )
    parser.add_argument("--source-trade-db", default="H:/Asteria-temp/trade-target/trade.duckdb")
    parser.add_argument("--target-system-db", default="H:/Asteria-temp/system-target/system.duckdb")
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--run-id", default="downstream-daily-incremental-runner-build-card")
    parser.add_argument(
        "--mode", choices=["daily_incremental", "resume", "audit-only"], default="daily_incremental"
    )
    parser.add_argument(
        "--trade-daily-impact-scope-path",
        default="H:/Asteria-temp/trade/downstream-daily-incremental-runner-build-card/daily-impact-scope.json",
    )
    parser.add_argument(
        "--trade-lineage-path",
        default="H:/Asteria-temp/trade/downstream-daily-incremental-runner-build-card/lineage.json",
    )
    parser.add_argument(
        "--trade-checkpoint-path",
        default="H:/Asteria-temp/trade/downstream-daily-incremental-runner-build-card/checkpoint.json",
    )
    args = parser.parse_args()
    summary = run_system_readout_daily_incremental_ledger(
        SystemReadoutDailyIncrementalLedgerRequest(
            source_malf_service_db=Path(args.source_malf_service_db),
            source_alpha_root=Path(args.source_alpha_root),
            source_signal_db=Path(args.source_signal_db),
            source_position_db=Path(args.source_position_db),
            source_portfolio_plan_db=Path(args.source_portfolio_plan_db),
            source_trade_db=Path(args.source_trade_db),
            target_system_db=Path(args.target_system_db),
            temp_root=Path(args.temp_root),
            report_root=Path(args.report_root),
            run_id=args.run_id,
            mode=args.mode,
            trade_daily_impact_scope_path=Path(args.trade_daily_impact_scope_path),
            trade_lineage_path=Path(args.trade_lineage_path),
            trade_checkpoint_path=Path(args.trade_checkpoint_path),
        )
    )
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0 if summary.status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
