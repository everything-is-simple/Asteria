from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.alpha.pas_bounded_proof import (
    PasBoundedProofRequest,
    run_alpha_pas_bounded_proof,
)
from asteria.alpha.pas_contracts import ALPHA_PAS_RULE_VERSION, ALPHA_PAS_SCHEMA_VERSION


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Alpha/PAS v1.0 bounded proof.")
    parser.add_argument("--source-malf-db", default="H:/Asteria-data/malf_service_day.duckdb")
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--validated-root", default="H:/Asteria-Validated")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--source-malf-service-version", required=True)
    parser.add_argument("--source-malf-run-id")
    parser.add_argument("--start-dt")
    parser.add_argument("--end-dt")
    parser.add_argument("--symbol-limit", type=int)
    parser.add_argument("--schema-version", default=ALPHA_PAS_SCHEMA_VERSION)
    parser.add_argument("--rule-version", default=ALPHA_PAS_RULE_VERSION)
    parser.add_argument("--mode", choices=["bounded"], default="bounded")
    parser.add_argument("--timeframe", choices=["day"], default="day")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    request = PasBoundedProofRequest(
        source_malf_db=Path(args.source_malf_db),
        temp_root=Path(args.temp_root),
        report_root=Path(args.report_root),
        validated_root=Path(args.validated_root),
        run_id=args.run_id,
        source_malf_service_version=args.source_malf_service_version,
        source_malf_run_id=args.source_malf_run_id,
        start_dt=args.start_dt,
        end_dt=args.end_dt,
        symbol_limit=args.symbol_limit,
        mode=args.mode,
        timeframe=args.timeframe,
        schema_version=args.schema_version,
        rule_version=args.rule_version,
    )
    summary = run_alpha_pas_bounded_proof(request)
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0 if summary.hard_fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
