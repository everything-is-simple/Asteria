from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.system_readout.bootstrap import run_system_readout_audit
from asteria.system_readout.contracts import SystemReadoutBuildRequest


def main() -> int:
    parser = argparse.ArgumentParser(description="Run System Readout audit.")
    parser.add_argument(
        "--source-malf-service-db",
        default="H:/Asteria-data/malf_service_day.duckdb",
    )
    parser.add_argument("--source-alpha-root", default="H:/Asteria-data")
    parser.add_argument("--source-signal-db", default="H:/Asteria-data/signal.duckdb")
    parser.add_argument("--source-position-db", default="H:/Asteria-data/position.duckdb")
    parser.add_argument(
        "--source-portfolio-plan-db",
        default="H:/Asteria-data/portfolio_plan.duckdb",
    )
    parser.add_argument("--source-trade-db", default="H:/Asteria-data/trade.duckdb")
    parser.add_argument("--target-system-db", default="H:/Asteria-data/system.duckdb")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--validated-root", default="H:/Asteria-Validated")
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--source-chain-release-version", required=True)
    args = parser.parse_args()
    summary = run_system_readout_audit(
        SystemReadoutBuildRequest(
            source_malf_service_db=Path(args.source_malf_service_db),
            source_alpha_root=Path(args.source_alpha_root),
            source_signal_db=Path(args.source_signal_db),
            source_position_db=Path(args.source_position_db),
            source_portfolio_plan_db=Path(args.source_portfolio_plan_db),
            source_trade_db=Path(args.source_trade_db),
            target_system_db=Path(args.target_system_db),
            report_root=Path(args.report_root),
            validated_root=Path(args.validated_root),
            temp_root=Path(args.temp_root),
            run_id=args.run_id,
            mode="audit-only",
            source_chain_release_version=args.source_chain_release_version,
            symbol_limit=1,
        )
    )
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0 if summary.hard_fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
