from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.malf.bootstrap import run_malf_day_service_build
from asteria.malf.contracts import MALF_SCHEMA_VERSION, MalfDayRequest


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Asteria MALF day service bounded-proof scaffold."
    )
    parser.add_argument("--core-db", required=True)
    parser.add_argument("--lifespan-db", required=True)
    parser.add_argument("--target-db", required=True)
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--validated-root", default="H:/Asteria-Validated")
    parser.add_argument("--mode", choices=["bounded", "segmented", "full", "resume"], required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--schema-version", default=MALF_SCHEMA_VERSION)
    parser.add_argument("--service-version", required=True)
    parser.add_argument("--start-dt")
    parser.add_argument("--end-dt")
    parser.add_argument("--symbol-limit", type=int)
    args = parser.parse_args()

    summary = run_malf_day_service_build(
        MalfDayRequest(
            source_db=Path("NUL"),
            core_db=Path(args.core_db),
            lifespan_db=Path(args.lifespan_db),
            service_db=Path(args.target_db),
            report_root=Path(args.report_root),
            validated_root=Path(args.validated_root),
            temp_root=Path(args.temp_root),
            run_id=args.run_id,
            mode=args.mode,
            schema_version=args.schema_version,
            service_version=args.service_version,
            start_dt=args.start_dt,
            end_dt=args.end_dt,
            symbol_limit=args.symbol_limit,
        )
    )
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
