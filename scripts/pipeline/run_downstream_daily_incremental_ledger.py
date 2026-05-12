from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.portfolio_plan.contracts import PortfolioPlanDailyIncrementalLedgerRequest
from asteria.portfolio_plan.daily_incremental_ledger import (
    run_portfolio_plan_daily_incremental_ledger,
)
from asteria.position.contracts import PositionDailyIncrementalLedgerRequest
from asteria.position.daily_incremental_ledger import run_position_daily_incremental_ledger
from asteria.system_readout.contracts import SystemReadoutDailyIncrementalLedgerRequest
from asteria.system_readout.daily_incremental_ledger import (
    run_system_readout_daily_incremental_ledger,
)
from asteria.trade.contracts import TradeDailyIncrementalLedgerRequest
from asteria.trade.daily_incremental_ledger import run_trade_daily_incremental_ledger

REPORT_DATE = "2026-05-12"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the downstream day daily incremental sample chain."
    )
    parser.add_argument(
        "--malf-service-db", default="H:/Asteria-temp/malf-target/malf_service_day.duckdb"
    )
    parser.add_argument("--alpha-root", default="H:/Asteria-temp/alpha-target")
    parser.add_argument("--signal-db", default="H:/Asteria-temp/signal-target/signal.duckdb")
    parser.add_argument("--position-db", default="H:/Asteria-temp/position-target/position.duckdb")
    parser.add_argument(
        "--portfolio-plan-db",
        default="H:/Asteria-temp/portfolio-plan-target/portfolio_plan.duckdb",
    )
    parser.add_argument("--trade-db", default="H:/Asteria-temp/trade-target/trade.duckdb")
    parser.add_argument("--system-db", default="H:/Asteria-temp/system-target/system.duckdb")
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--run-id", default="downstream-daily-incremental-runner-build-card")
    parser.add_argument(
        "--mode",
        choices=["daily_incremental", "resume", "audit-only"],
        default="daily_incremental",
    )
    parser.add_argument(
        "--signal-daily-impact-scope-path",
        default="H:/Asteria-temp/signal/alpha-signal-daily-incremental-ledger-build-card/daily-impact-scope.json",
    )
    parser.add_argument(
        "--signal-lineage-path",
        default="H:/Asteria-temp/signal/alpha-signal-daily-incremental-ledger-build-card/lineage.json",
    )
    parser.add_argument(
        "--signal-checkpoint-path",
        default="H:/Asteria-temp/signal/alpha-signal-daily-incremental-ledger-build-card/checkpoint.json",
    )
    args = parser.parse_args()

    position_summary = run_position_daily_incremental_ledger(
        PositionDailyIncrementalLedgerRequest(
            source_signal_db=Path(args.signal_db),
            target_position_db=Path(args.position_db),
            temp_root=Path(args.temp_root),
            report_root=Path(args.report_root),
            run_id=args.run_id,
            mode=args.mode,
            signal_daily_impact_scope_path=Path(args.signal_daily_impact_scope_path),
            signal_lineage_path=Path(args.signal_lineage_path),
            signal_checkpoint_path=Path(args.signal_checkpoint_path),
        )
    )
    portfolio_plan_summary = run_portfolio_plan_daily_incremental_ledger(
        PortfolioPlanDailyIncrementalLedgerRequest(
            source_position_db=Path(args.position_db),
            target_portfolio_plan_db=Path(args.portfolio_plan_db),
            temp_root=Path(args.temp_root),
            report_root=Path(args.report_root),
            run_id=args.run_id,
            mode=args.mode,
            position_daily_impact_scope_path=Path(position_summary.daily_impact_scope_path),
            position_lineage_path=Path(position_summary.lineage_path),
            position_checkpoint_path=Path(position_summary.checkpoint_path),
        )
    )
    trade_summary = run_trade_daily_incremental_ledger(
        TradeDailyIncrementalLedgerRequest(
            source_portfolio_plan_db=Path(args.portfolio_plan_db),
            target_trade_db=Path(args.trade_db),
            temp_root=Path(args.temp_root),
            report_root=Path(args.report_root),
            run_id=args.run_id,
            mode=args.mode,
            portfolio_plan_daily_impact_scope_path=Path(
                portfolio_plan_summary.daily_impact_scope_path
            ),
            portfolio_plan_lineage_path=Path(portfolio_plan_summary.lineage_path),
            portfolio_plan_checkpoint_path=Path(portfolio_plan_summary.checkpoint_path),
        )
    )
    system_summary = run_system_readout_daily_incremental_ledger(
        SystemReadoutDailyIncrementalLedgerRequest(
            source_malf_service_db=Path(args.malf_service_db),
            source_alpha_root=Path(args.alpha_root),
            source_signal_db=Path(args.signal_db),
            source_position_db=Path(args.position_db),
            source_portfolio_plan_db=Path(args.portfolio_plan_db),
            source_trade_db=Path(args.trade_db),
            target_system_db=Path(args.system_db),
            temp_root=Path(args.temp_root),
            report_root=Path(args.report_root),
            run_id=args.run_id,
            mode=args.mode,
            trade_daily_impact_scope_path=Path(trade_summary.daily_impact_scope_path),
            trade_lineage_path=Path(trade_summary.lineage_path),
            trade_checkpoint_path=Path(trade_summary.checkpoint_path),
        )
    )

    report_dir = Path(args.report_root) / "pipeline" / REPORT_DATE / args.run_id
    report_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": args.run_id,
        "mode": args.mode,
        "status": _status(
            position_summary.status,
            portfolio_plan_summary.status,
            trade_summary.status,
            system_summary.status,
        ),
        "boundaries": {
            "day_only": True,
            "formal_data_mutation": False,
            "pipeline_full_daily_chain_opened": False,
        },
        "position": position_summary.as_dict(),
        "portfolio_plan": portfolio_plan_summary.as_dict(),
        "trade": trade_summary.as_dict(),
        "system_readout": system_summary.as_dict(),
    }
    summary_path = report_dir / "summary.json"
    closeout_path = report_dir / "closeout.md"
    summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    closeout_path.write_text(_closeout_text(payload), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "passed" else 1


def _status(*statuses: str) -> str:
    return "passed" if all(status == "passed" for status in statuses) else "failed"


def _closeout_text(payload: dict[str, object]) -> str:
    lines = [
        f"# Downstream daily incremental closeout: {payload['run_id']}",
        "",
        f"- status: {payload['status']}",
        "- boundaries: day-only / temp-only / no formal H:/Asteria-data mutation",
        "- pipeline full daily chain: not opened",
        "- next allowed action: pipeline_full_daily_incremental_chain_build_card",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
