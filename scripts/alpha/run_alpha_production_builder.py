from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.alpha.bootstrap import ALPHA_PRODUCTION_SOURCES, run_alpha_production_builder
from asteria.alpha.contracts import ALPHA_RULE_VERSION, ALPHA_SCHEMA_VERSION


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Alpha production builder hardening across released MALF timeframes."
    )
    parser.add_argument("--target-data-root", default="H:/Asteria-data")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--validated-root", default="H:/Asteria-Validated")
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument(
        "--mode", choices=["segmented", "full", "resume", "audit-only"], required=True
    )
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--timeframe", action="append", choices=sorted(ALPHA_PRODUCTION_SOURCES))
    parser.add_argument("--start-dt")
    parser.add_argument("--end-dt")
    parser.add_argument("--symbol-limit", type=int)
    parser.add_argument("--schema-version", default=ALPHA_SCHEMA_VERSION)
    parser.add_argument("--alpha-rule-version", default=ALPHA_RULE_VERSION)
    parser.add_argument("--source-malf-day-db")
    parser.add_argument("--source-malf-week-db")
    parser.add_argument("--source-malf-month-db")
    parser.add_argument("--source-malf-day-service-version")
    parser.add_argument("--source-malf-week-service-version")
    parser.add_argument("--source-malf-month-service-version")
    parser.add_argument("--source-malf-day-run-id")
    parser.add_argument("--source-malf-week-run-id")
    parser.add_argument("--source-malf-month-run-id")
    parser.add_argument("--source-malf-day-sample-version")
    parser.add_argument("--source-malf-week-sample-version")
    parser.add_argument("--source-malf-month-sample-version")
    args = parser.parse_args()

    source_malf_dbs = _path_mapping(
        {
            "day": args.source_malf_day_db,
            "week": args.source_malf_week_db,
            "month": args.source_malf_month_db,
        }
    )
    service_versions = _str_mapping(
        {
            "day": args.source_malf_day_service_version,
            "week": args.source_malf_week_service_version,
            "month": args.source_malf_month_service_version,
        }
    )
    source_run_ids = _str_mapping(
        {
            "day": args.source_malf_day_run_id,
            "week": args.source_malf_week_run_id,
            "month": args.source_malf_month_run_id,
        }
    )
    sample_versions = _str_mapping(
        {
            "day": args.source_malf_day_sample_version,
            "week": args.source_malf_week_sample_version,
            "month": args.source_malf_month_sample_version,
        }
    )
    summaries = run_alpha_production_builder(
        source_malf_dbs=source_malf_dbs,
        source_malf_service_versions=service_versions,
        target_data_root=Path(args.target_data_root),
        report_root=Path(args.report_root),
        validated_root=Path(args.validated_root),
        temp_root=Path(args.temp_root),
        run_id=args.run_id,
        mode=args.mode,
        source_malf_run_ids=source_run_ids,
        source_malf_sample_versions=sample_versions,
        start_dt=args.start_dt,
        end_dt=args.end_dt,
        symbol_limit=args.symbol_limit,
        schema_version=args.schema_version,
        alpha_rule_version=args.alpha_rule_version,
        timeframes=tuple(args.timeframe or ("day", "week", "month")),
    )
    payload = [summary.as_dict() for summary in summaries]
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if sum(summary.hard_fail_count for summary in summaries) == 0 else 1


def _path_mapping(values: dict[str, str | None]) -> dict[str, Path] | None:
    mapping = {key: Path(value) for key, value in values.items() if value}
    return mapping or None


def _str_mapping(values: dict[str, str | None]) -> dict[str, str] | None:
    mapping = {key: value for key, value in values.items() if value}
    return mapping or None


if __name__ == "__main__":
    raise SystemExit(main())
