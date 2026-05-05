from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.malf.supplemental import (
    MalfSupplementalBuildRequest,
    make_scope,
    run_malf_day_supplemental_build,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run MALF day supplemental batch build.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--source-db", default=r"H:\Asteria-data\market_base_day.duckdb")
    parser.add_argument("--core-db", default=r"H:\Asteria-data\malf_core_day.duckdb")
    parser.add_argument("--lifespan-db", default=r"H:\Asteria-data\malf_lifespan_day.duckdb")
    parser.add_argument("--service-db", default=r"H:\Asteria-data\malf_service_day.duckdb")
    parser.add_argument("--report-root", default=r"H:\Asteria-report")
    parser.add_argument("--validated-root", default=r"H:\Asteria-Validated")
    parser.add_argument("--temp-root", default=r"H:\Asteria-temp")
    parser.add_argument(
        "--mode",
        choices=["segmented", "resume", "audit-only"],
        default="segmented",
    )
    parser.add_argument("--year", type=int)
    parser.add_argument("--month", type=int)
    parser.add_argument("--date")
    parser.add_argument("--start-dt")
    parser.add_argument("--end-dt")
    parser.add_argument("--symbols-file")
    parser.add_argument("--symbol-start")
    parser.add_argument("--symbol-end")
    parser.add_argument("--batch-size", type=int, default=100)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scope = make_scope(
        year=args.year,
        month=args.month,
        day=args.date,
        start_dt=args.start_dt,
        end_dt=args.end_dt,
    )
    request = MalfSupplementalBuildRequest(
        source_db=Path(args.source_db),
        core_db=Path(args.core_db),
        lifespan_db=Path(args.lifespan_db),
        service_db=Path(args.service_db),
        report_root=Path(args.report_root),
        validated_root=Path(args.validated_root),
        temp_root=Path(args.temp_root),
        run_id=args.run_id,
        mode=args.mode,
        scope=scope,
        batch_size=args.batch_size,
        symbols_file=Path(args.symbols_file) if args.symbols_file else None,
        symbol_start=args.symbol_start,
        symbol_end=args.symbol_end,
    )
    summary = run_malf_day_supplemental_build(request)
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
