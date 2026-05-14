from __future__ import annotations

import argparse
from pathlib import Path

from asteria.pipeline.v1_vectorbt_portfolio_analytics_proof import (
    run_v1_vectorbt_portfolio_analytics_proof,
)
from asteria.pipeline.v1_vectorbt_portfolio_analytics_proof_contracts import (
    DEFAULT_SCOPE_MANIFEST_PATH,
    VectorbtPortfolioAnalyticsProofRequest,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Asteria v1 vectorbt portfolio proof.")
    parser.add_argument("--repo-root", default="H:/Asteria")
    parser.add_argument("--formal-data-root", default="H:/Asteria-data")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--validated-root", default="H:/Asteria-Validated")
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument("--scope-manifest-path", default=DEFAULT_SCOPE_MANIFEST_PATH)
    args = parser.parse_args()

    summary = run_v1_vectorbt_portfolio_analytics_proof(
        VectorbtPortfolioAnalyticsProofRequest(
            repo_root=Path(args.repo_root),
            formal_data_root=Path(args.formal_data_root),
            report_root=Path(args.report_root),
            validated_root=Path(args.validated_root),
            temp_root=Path(args.temp_root),
            scope_manifest_path=Path(args.scope_manifest_path),
        )
    )
    print(summary.as_dict())


if __name__ == "__main__":
    main()
