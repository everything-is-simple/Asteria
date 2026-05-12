from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.position.contracts import PositionDailyIncrementalLedgerRequest
from asteria.position.daily_incremental_ledger import run_position_daily_incremental_ledger


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the Position day daily incremental sample ledger."
    )
    parser.add_argument("--source-signal-db", default="H:/Asteria-temp/signal-target/signal.duckdb")
    parser.add_argument(
        "--target-position-db", default="H:/Asteria-temp/position-target/position.duckdb"
    )
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--run-id", default="downstream-daily-incremental-runner-build-card")
    parser.add_argument(
        "--mode", choices=["daily_incremental", "resume", "audit-only"], default="daily_incremental"
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
    summary = run_position_daily_incremental_ledger(
        PositionDailyIncrementalLedgerRequest(
            source_signal_db=Path(args.source_signal_db),
            target_position_db=Path(args.target_position_db),
            temp_root=Path(args.temp_root),
            report_root=Path(args.report_root),
            run_id=args.run_id,
            mode=args.mode,
            signal_daily_impact_scope_path=Path(args.signal_daily_impact_scope_path),
            signal_lineage_path=Path(args.signal_lineage_path),
            signal_checkpoint_path=Path(args.signal_checkpoint_path),
        )
    )
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0 if summary.status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
