from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.alpha.bootstrap import ALPHA_FAMILY_DATABASES, run_alpha_family_audit
from asteria.alpha.contracts import (
    ALPHA_RULE_VERSION,
    ALPHA_SCHEMA_VERSION,
    VALID_ALPHA_RUN_MODES,
    VALID_ALPHA_TIMEFRAMES,
    AlphaFamilyRequest,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one Alpha family hard audit.")
    parser.add_argument("--alpha-family", required=True, choices=sorted(ALPHA_FAMILY_DATABASES))
    parser.add_argument("--timeframe", choices=sorted(VALID_ALPHA_TIMEFRAMES), default="day")
    parser.add_argument("--mode", choices=sorted(VALID_ALPHA_RUN_MODES), default="audit-only")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--source-malf-db", required=True)
    parser.add_argument("--target-alpha-db")
    parser.add_argument("--target-data-root", default="H:/Asteria-data")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--validated-root", default="H:/Asteria-Validated")
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument("--start-dt")
    parser.add_argument("--end-dt")
    parser.add_argument("--symbol-limit", type=int)
    parser.add_argument("--schema-version", default=ALPHA_SCHEMA_VERSION)
    parser.add_argument("--alpha-rule-version", default=ALPHA_RULE_VERSION)
    parser.add_argument("--source-malf-service-version", required=True)
    parser.add_argument("--source-malf-run-id")
    parser.add_argument("--source-malf-sample-version")
    args = parser.parse_args()

    target_db = (
        Path(args.target_alpha_db)
        if args.target_alpha_db
        else (Path(args.target_data_root) / ALPHA_FAMILY_DATABASES[args.alpha_family])
    )
    summary = run_alpha_family_audit(
        AlphaFamilyRequest(
            source_malf_db=Path(args.source_malf_db),
            target_alpha_db=target_db,
            report_root=Path(args.report_root),
            validated_root=Path(args.validated_root),
            temp_root=Path(args.temp_root),
            run_id=args.run_id,
            mode=args.mode,
            alpha_family=args.alpha_family,
            source_malf_service_version=args.source_malf_service_version,
            source_malf_run_id=args.source_malf_run_id,
            source_malf_sample_version=args.source_malf_sample_version,
            schema_version=args.schema_version,
            alpha_rule_version=args.alpha_rule_version,
            timeframe=args.timeframe,
            start_dt=args.start_dt,
            end_dt=args.end_dt,
            symbol_limit=args.symbol_limit,
        )
    )
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0 if summary.hard_fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
