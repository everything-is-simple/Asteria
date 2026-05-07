from __future__ import annotations

import argparse
import json

from asteria.portfolio_plan.bootstrap import run_portfolio_plan_audit
from scripts.portfolio_plan.run_portfolio_plan_build import (
    _add_common_args,
    _request_from_args,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Portfolio Plan audit.")
    _add_common_args(parser)
    args = parser.parse_args()
    summary = run_portfolio_plan_audit(_request_from_args(args))
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0 if summary.hard_fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
