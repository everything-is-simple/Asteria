from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from asteria.pipeline.v1_usage_validation_scope import run_v1_usage_validation_scope
from asteria.pipeline.v1_usage_validation_scope_contracts import (
    UsageValidationScopeRequest,
)


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Freeze the post-terminal v1 usage validation scope without mutating live gate truth."
        )
    )
    parser.add_argument("--repo-root", default="H:/Asteria")
    parser.add_argument("--market-meta-db", default="H:/Asteria-data/market_meta.duckdb")
    parser.add_argument("--market-base-day-db", default="H:/Asteria-data/market_base_day.duckdb")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--validated-root", default="H:/Asteria-Validated")
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--start-date", default="2024-01-02", type=_parse_date)
    parser.add_argument("--end-date", default="2024-12-31", type=_parse_date)
    parser.add_argument(
        "--research-question",
        default="Asteria 当前链路能否给出可解释、可审计的结构-信号-持仓-交易意图读出",
    )
    parser.add_argument("--report-shape", default="双层输出")
    parser.add_argument("--manual-override-path")
    args = parser.parse_args()

    summary = run_v1_usage_validation_scope(
        UsageValidationScopeRequest(
            repo_root=Path(args.repo_root),
            market_meta_db=Path(args.market_meta_db),
            market_base_day_db=Path(args.market_base_day_db),
            report_root=Path(args.report_root),
            validated_root=Path(args.validated_root),
            temp_root=Path(args.temp_root),
            run_id=args.run_id,
            start_date=args.start_date,
            end_date=args.end_date,
            research_question=args.research_question,
            report_shape=args.report_shape,
            manual_override_path=(
                None if args.manual_override_path is None else Path(args.manual_override_path)
            ),
        )
    )
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0 if summary.status == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
