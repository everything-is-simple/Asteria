from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.pipeline.alpha_signal_2024_coverage_repair import (
    AlphaSignalCoverageRepairRequest,
    run_alpha_signal_2024_coverage_repair,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the Alpha/Signal 2024 coverage repair card orchestration."
    )
    parser.add_argument("--repo-root", default="H:/Asteria")
    parser.add_argument("--source-system-db", default="H:/Asteria-data/system.duckdb")
    parser.add_argument(
        "--baseline-malf-service-db", default="H:/Asteria-data/malf_service_day.duckdb"
    )
    parser.add_argument(
        "--repaired-malf-service-db", default="H:/Asteria-data/malf_service_day.duckdb"
    )
    parser.add_argument("--target-data-root", default="H:/Asteria-data")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--validated-root", default="H:/Asteria-Validated")
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument("--run-id", required=True)
    parser.add_argument(
        "--baseline-malf-run-id",
        default="malf-v1-4-core-runtime-sync-implementation-20260505-01",
    )
    parser.add_argument(
        "--repaired-malf-run-id",
        default="malf-2024-natural-year-coverage-repair-card-20260509-01-batch-0001",
    )
    parser.add_argument(
        "--released-alpha-run-id",
        default="alpha-production-builder-hardening-20260506-01",
    )
    parser.add_argument(
        "--released-signal-run-id",
        default="signal-production-builder-hardening-20260506-01",
    )
    parser.add_argument(
        "--source-chain-release-version",
        default="system-readout-bounded-proof-build-card-20260508-01",
    )
    parser.add_argument("--malf-service-version", default="malf-wave-position-dense-v1")
    parser.add_argument("--target-year", type=int, default=2024)
    parser.add_argument("--skip-followup-checks", action="store_true")
    args = parser.parse_args()

    summary = run_alpha_signal_2024_coverage_repair(
        AlphaSignalCoverageRepairRequest(
            repo_root=Path(args.repo_root),
            source_system_db=Path(args.source_system_db),
            baseline_malf_service_db=Path(args.baseline_malf_service_db),
            repaired_malf_service_db=Path(args.repaired_malf_service_db),
            target_data_root=Path(args.target_data_root),
            report_root=Path(args.report_root),
            validated_root=Path(args.validated_root),
            temp_root=Path(args.temp_root),
            run_id=args.run_id,
            baseline_malf_run_id=args.baseline_malf_run_id,
            repaired_malf_run_id=args.repaired_malf_run_id,
            released_alpha_run_id=args.released_alpha_run_id,
            released_signal_run_id=args.released_signal_run_id,
            source_chain_release_version=args.source_chain_release_version,
            malf_service_version=args.malf_service_version,
            target_year=args.target_year,
            run_followup_checks=not args.skip_followup_checks,
        )
    )
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0 if summary.status == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
