from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.pipeline.bootstrap import run_pipeline_bounded_proof


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Pipeline bounded proof or year replay.")
    parser.add_argument("--repo-root", default="H:/Asteria")
    parser.add_argument("--source-system-db", default="H:/Asteria-data/system.duckdb")
    parser.add_argument("--target-pipeline-db", default="H:/Asteria-data/pipeline.duckdb")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--validated-root", default="H:/Asteria-Validated")
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument("--mode", choices=["bounded", "resume"], default="bounded")
    parser.add_argument(
        "--module-scope",
        choices=["system_readout", "full_chain_day", "year_replay", "year_replay_rerun"],
        default="system_readout",
    )
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--source-chain-release-version", required=True)
    parser.add_argument("--target-year", type=int)
    args = parser.parse_args()
    summary = run_pipeline_bounded_proof(
        repo_root=Path(args.repo_root),
        source_system_db=Path(args.source_system_db),
        target_pipeline_db=Path(args.target_pipeline_db),
        report_root=Path(args.report_root),
        validated_root=Path(args.validated_root),
        temp_root=Path(args.temp_root),
        run_id=args.run_id,
        source_chain_release_version=args.source_chain_release_version,
        module_scope=args.module_scope,
        mode=args.mode,
        target_year=args.target_year,
    )
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0 if summary.hard_fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
