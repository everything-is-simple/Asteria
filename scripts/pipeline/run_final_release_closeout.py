from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.pipeline.final_release_closeout import (
    FINAL_RELEASE_CLOSEOUT_CARD,
    FINAL_RELEASE_PROOF_CARD,
    FinalReleaseCloseoutRequest,
    run_final_release_closeout,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the final release closeout.")
    parser.add_argument("--formal-data-root", default="H:/Asteria-data")
    parser.add_argument(
        "--source-proof-root",
        default="H:/Asteria-temp/formal-release-source-proof/"
        "formal-release-source-proof-20260512-01",
    )
    parser.add_argument(
        "--proof-run-root",
        default=f"H:/Asteria-temp/formal-release-proof/{FINAL_RELEASE_PROOF_CARD}",
    )
    parser.add_argument(
        "--proof-report-dir",
        default=f"H:/Asteria-report/pipeline/2026-05-12/{FINAL_RELEASE_PROOF_CARD}",
    )
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--validated-root", default="H:/Asteria-Validated")
    parser.add_argument("--run-id", default=FINAL_RELEASE_CLOSEOUT_CARD)
    parser.add_argument("--mode", choices=["audit-only", "closeout"], default="audit-only")
    return parser


def _request_from_args(args: argparse.Namespace) -> FinalReleaseCloseoutRequest:
    return FinalReleaseCloseoutRequest(
        formal_data_root=Path(args.formal_data_root),
        source_proof_root=Path(args.source_proof_root),
        proof_run_root=Path(args.proof_run_root),
        proof_report_dir=Path(args.proof_report_dir),
        report_root=Path(args.report_root),
        validated_root=Path(args.validated_root),
        run_id=args.run_id,
        mode=args.mode,
    )


def main() -> int:
    args = build_parser().parse_args()
    summary = run_final_release_closeout(_request_from_args(args))
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0 if summary.status.startswith("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
