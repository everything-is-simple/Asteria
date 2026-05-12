from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.pipeline.formal_release_proof import (
    FORMAL_RELEASE_PROOF_CARD,
    FormalReleaseProofRequest,
    run_formal_release_proof,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the formal full rebuild and daily incremental release proof."
    )
    parser.add_argument("--source-root", default="H:/tdx_offline_Data")
    parser.add_argument("--formal-data-root", default="H:/Asteria-data")
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--validated-root", default="H:/Asteria-Validated")
    parser.add_argument("--run-id", default=FORMAL_RELEASE_PROOF_CARD)
    parser.add_argument(
        "--mode",
        choices=["release-proof", "resume", "audit-only"],
        default="audit-only",
    )
    parser.add_argument("--allow-formal-data-write", action="store_true")
    return parser


def _request_from_args(args: argparse.Namespace) -> FormalReleaseProofRequest:
    return FormalReleaseProofRequest(
        source_root=Path(args.source_root),
        formal_data_root=Path(args.formal_data_root),
        temp_root=Path(args.temp_root),
        report_root=Path(args.report_root),
        validated_root=Path(args.validated_root),
        run_id=args.run_id,
        mode=args.mode,
        allow_formal_data_write=args.allow_formal_data_write,
    )


def main() -> int:
    args = build_parser().parse_args()
    summary = run_formal_release_proof(_request_from_args(args))
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0 if summary.status.startswith("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
