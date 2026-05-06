from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.signal.bootstrap import (
    SIGNAL_PRODUCTION_SOURCE_ALPHA_RUN_ID,
    run_signal_production_builder,
)
from asteria.signal.contracts import SIGNAL_RULE_VERSION, SIGNAL_SCHEMA_VERSION


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Signal production builder hardening across released Alpha timeframes."
    )
    parser.add_argument("--source-alpha-root", default="H:/Asteria-data")
    parser.add_argument("--target-signal-db", default="H:/Asteria-data/signal.duckdb")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--validated-root", default="H:/Asteria-Validated")
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument(
        "--mode", choices=["segmented", "full", "resume", "audit-only"], required=True
    )
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--timeframe", action="append", choices=["day", "week", "month"])
    parser.add_argument("--start-dt")
    parser.add_argument("--end-dt")
    parser.add_argument("--symbol-limit", type=int)
    parser.add_argument("--schema-version", default=SIGNAL_SCHEMA_VERSION)
    parser.add_argument("--signal-rule-version", default=SIGNAL_RULE_VERSION)
    parser.add_argument(
        "--source-alpha-release-version",
        default=SIGNAL_PRODUCTION_SOURCE_ALPHA_RUN_ID,
    )
    parser.add_argument("--source-alpha-run-id", default=SIGNAL_PRODUCTION_SOURCE_ALPHA_RUN_ID)
    args = parser.parse_args()

    summaries = run_signal_production_builder(
        source_alpha_root=Path(args.source_alpha_root),
        target_signal_db=Path(args.target_signal_db),
        report_root=Path(args.report_root),
        validated_root=Path(args.validated_root),
        temp_root=Path(args.temp_root),
        run_id=args.run_id,
        mode=args.mode,
        source_alpha_release_version=args.source_alpha_release_version,
        source_alpha_run_id=args.source_alpha_run_id,
        start_dt=args.start_dt,
        end_dt=args.end_dt,
        symbol_limit=args.symbol_limit,
        schema_version=args.schema_version,
        signal_rule_version=args.signal_rule_version,
        timeframes=tuple(args.timeframe or ("day", "week", "month")),
    )
    payload = [summary.as_dict() for summary in summaries]
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if sum(summary.hard_fail_count for summary in summaries) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
