from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.pipeline.v1_usage_value_decision import run_v1_usage_value_decision
from asteria.pipeline.v1_usage_value_decision_contracts import (
    DEFAULT_DOWNSTREAM_REFERENCE_MANIFEST_PATH,
    DEFAULT_USAGE_READOUT_MANIFEST_PATH,
    V1_USAGE_VALUE_DECISION_RUN_ID,
    UsageValueDecisionRequest,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the read-only v1 usage value decision.")
    parser.add_argument("--repo-root", default="H:/Asteria")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--validated-root", default="H:/Asteria-Validated")
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument(
        "--usage-readout-manifest-path",
        default=DEFAULT_USAGE_READOUT_MANIFEST_PATH,
    )
    parser.add_argument(
        "--downstream-reference-manifest-path",
        default=DEFAULT_DOWNSTREAM_REFERENCE_MANIFEST_PATH,
    )
    parser.add_argument("--run-id", default=V1_USAGE_VALUE_DECISION_RUN_ID)
    args = parser.parse_args()

    summary = run_v1_usage_value_decision(
        UsageValueDecisionRequest(
            repo_root=Path(args.repo_root),
            report_root=Path(args.report_root),
            validated_root=Path(args.validated_root),
            temp_root=Path(args.temp_root),
            usage_readout_manifest_path=Path(args.usage_readout_manifest_path),
            downstream_reference_manifest_path=Path(args.downstream_reference_manifest_path),
            run_id=args.run_id,
        )
    )
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0 if summary.status.startswith("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
