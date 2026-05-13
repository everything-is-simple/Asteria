from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.pipeline.v1_usage_readout_report import run_v1_usage_readout_report
from asteria.pipeline.v1_usage_readout_report_contracts import (
    DEFAULT_SCOPE_MANIFEST_PATH,
    V1_USAGE_READOUT_REPORT_RUN_ID,
    UsageReadoutReportRequest,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate the post-terminal v1 usage readout report from formal DBs."
    )
    parser.add_argument("--repo-root", default="H:/Asteria")
    parser.add_argument("--formal-data-root", default="H:/Asteria-data")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--validated-root", default="H:/Asteria-Validated")
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument("--scope-manifest-path", default=DEFAULT_SCOPE_MANIFEST_PATH)
    parser.add_argument("--run-id", default=V1_USAGE_READOUT_REPORT_RUN_ID)
    args = parser.parse_args()

    summary = run_v1_usage_readout_report(
        UsageReadoutReportRequest(
            repo_root=Path(args.repo_root),
            formal_data_root=Path(args.formal_data_root),
            report_root=Path(args.report_root),
            validated_root=Path(args.validated_root),
            temp_root=Path(args.temp_root),
            scope_manifest_path=Path(args.scope_manifest_path),
            run_id=args.run_id,
        )
    )
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0 if summary.status.startswith("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
