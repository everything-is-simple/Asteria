from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.position.bootstrap import run_position_bounded_proof
from asteria.position.contracts import POSITION_RULE_VERSION, POSITION_SCHEMA_VERSION


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Position bounded proof.")
    parser.add_argument("--source-signal-db", default="H:/Asteria-data/signal.duckdb")
    parser.add_argument("--target-position-db", default="H:/Asteria-data/position.duckdb")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--validated-root", default="H:/Asteria-Validated")
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument("--mode", choices=["bounded", "resume"], default="bounded")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--start-dt")
    parser.add_argument("--end-dt")
    parser.add_argument("--symbol-limit", type=int)
    parser.add_argument("--schema-version", default=POSITION_SCHEMA_VERSION)
    parser.add_argument("--position-rule-version", default=POSITION_RULE_VERSION)
    parser.add_argument("--source-signal-release-version", required=True)
    parser.add_argument("--source-signal-run-id")
    args = parser.parse_args()
    summary = run_position_bounded_proof(
        source_signal_db=Path(args.source_signal_db),
        target_position_db=Path(args.target_position_db),
        report_root=Path(args.report_root),
        validated_root=Path(args.validated_root),
        temp_root=Path(args.temp_root),
        run_id=args.run_id,
        mode=args.mode,
        source_signal_release_version=args.source_signal_release_version,
        source_signal_run_id=args.source_signal_run_id,
        start_dt=args.start_dt,
        end_dt=args.end_dt,
        symbol_limit=args.symbol_limit,
        schema_version=args.schema_version,
        position_rule_version=args.position_rule_version,
    )
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0 if summary.hard_fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
