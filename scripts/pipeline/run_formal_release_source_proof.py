from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.pipeline.formal_release_source_proof import (
    FORMAL_RELEASE_SOURCE_PROOF_CARD,
    FormalReleaseSourceProofRequest,
    run_formal_release_source_proof,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit formal release source proof surfaces without formal data promotion."
    )
    parser.add_argument("--repo-root", default="H:/Asteria")
    parser.add_argument(
        "--source-root",
        default="H:/Asteria-temp/formal-release-source-proof-input",
    )
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--run-id", default=FORMAL_RELEASE_SOURCE_PROOF_CARD)
    parser.add_argument(
        "--mode",
        choices=["audit-only", "source-proof", "resume"],
        default="audit-only",
    )
    return parser


def _request_from_args(args: argparse.Namespace) -> FormalReleaseSourceProofRequest:
    return FormalReleaseSourceProofRequest(
        repo_root=Path(args.repo_root),
        source_root=Path(args.source_root),
        temp_root=Path(args.temp_root),
        report_root=Path(args.report_root),
        run_id=args.run_id,
        mode=args.mode,
    )


def main() -> int:
    args = build_parser().parse_args()
    summary = run_formal_release_source_proof(_request_from_args(args))
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0 if summary.status.startswith("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
