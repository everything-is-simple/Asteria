from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.pipeline.v1_t_plus_one_open_backtesting_py_proof import (
    run_v1_t_plus_one_open_backtesting_py_proof,
)
from asteria.pipeline.v1_t_plus_one_open_backtesting_py_proof_contracts import (
    DEFAULT_SCOPE_MANIFEST_PATH,
    V1_T_PLUS_ONE_OPEN_BACKTESTING_PY_PROOF_RUN_ID,
    TPlusOneOpenBacktestingPyProofRequest,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the post-terminal v1 T+1 open backtesting.py proof."
    )
    parser.add_argument("--repo-root", default="H:/Asteria")
    parser.add_argument("--formal-data-root", default="H:/Asteria-data")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--validated-root", default="H:/Asteria-Validated")
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument("--scope-manifest-path", default=DEFAULT_SCOPE_MANIFEST_PATH)
    parser.add_argument("--run-id", default=V1_T_PLUS_ONE_OPEN_BACKTESTING_PY_PROOF_RUN_ID)
    parser.add_argument("--initial-cash", type=float, default=100_000.0)
    parser.add_argument("--commission", type=float, default=0.001)
    parser.add_argument("--position-fraction", type=float, default=0.95)
    args = parser.parse_args()

    summary = run_v1_t_plus_one_open_backtesting_py_proof(
        TPlusOneOpenBacktestingPyProofRequest(
            repo_root=Path(args.repo_root),
            formal_data_root=Path(args.formal_data_root),
            report_root=Path(args.report_root),
            validated_root=Path(args.validated_root),
            temp_root=Path(args.temp_root),
            scope_manifest_path=Path(args.scope_manifest_path),
            run_id=args.run_id,
            initial_cash=args.initial_cash,
            commission=args.commission,
            position_fraction=args.position_fraction,
        )
    )
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0 if summary.status.startswith("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
