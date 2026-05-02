from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.data.contracts import SwIndustrySnapshotImportRequest
from asteria.data.sw_industry import (
    EXPECTED_SW_INDUSTRY_SOURCE_SHA256,
    run_sw_industry_snapshot_import,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import the approved SW industry snapshot into market_meta.duckdb.",
    )
    parser.add_argument("--data-root", type=Path, default=Path("H:/Asteria-data"))
    parser.add_argument("--temp-root", type=Path, default=Path("H:/Asteria-temp"))
    parser.add_argument(
        "--source-path",
        type=Path,
        default=Path(
            "H:/Asteria-Validated/Market-Average-Lifespan-reference/"
            "申万行业分类/最新个股申万行业分类(完整版-截至7月末).xlsx"
        ),
    )
    parser.add_argument("--mode", choices=("full", "audit-only"), required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    summary = run_sw_industry_snapshot_import(
        SwIndustrySnapshotImportRequest(
            data_root=args.data_root,
            temp_root=args.temp_root,
            source_path=args.source_path,
            mode=args.mode,
            run_id=args.run_id,
            expected_source_sha256=EXPECTED_SW_INDUSTRY_SOURCE_SHA256,
        )
    )
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2, default=str))
    return 0 if summary.status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
