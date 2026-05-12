from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.pipeline.full_rebuild_daily_incremental_release_closeout import (
    FULL_REBUILD_DAILY_INCREMENTAL_RELEASE_CLOSEOUT_CARD,
    FullRebuildDailyIncrementalReleaseCloseoutRequest,
    run_full_rebuild_daily_incremental_release_closeout,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the full rebuild and daily incremental release closeout."
    )
    parser.add_argument("--repo-root", default="H:/Asteria")
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--validated-root", default="H:/Asteria-Validated")
    parser.add_argument("--run-id", default=FULL_REBUILD_DAILY_INCREMENTAL_RELEASE_CLOSEOUT_CARD)
    parser.add_argument("--mode", choices=["audit-only", "closeout"], default="audit-only")
    return parser


def _request_from_args(
    args: argparse.Namespace,
) -> FullRebuildDailyIncrementalReleaseCloseoutRequest:
    return FullRebuildDailyIncrementalReleaseCloseoutRequest(
        repo_root=Path(args.repo_root),
        temp_root=Path(args.temp_root),
        report_root=Path(args.report_root),
        validated_root=Path(args.validated_root),
        run_id=args.run_id,
        mode=args.mode,
    )


def main() -> int:
    args = build_parser().parse_args()
    summary = run_full_rebuild_daily_incremental_release_closeout(_request_from_args(args))
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0 if not summary.status.startswith("failed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
