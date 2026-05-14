from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.signal.pas_alignment import (
    SignalPasAlignmentRequest,
    run_signal_pas_alignment,
)
from asteria.signal.pas_contracts import (
    SIGNAL_PAS_RULE_VERSION,
    SIGNAL_PAS_SCHEMA_VERSION,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Signal/PAS alignment proof.")
    parser.add_argument("--source-pas-db", required=True)
    parser.add_argument("--source-pas-run-id", required=True)
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--validated-root", default="H:/Asteria-Validated")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--schema-version", default=SIGNAL_PAS_SCHEMA_VERSION)
    parser.add_argument("--signal-rule-version", default=SIGNAL_PAS_RULE_VERSION)
    parser.add_argument("--mode", choices=["bounded"], default="bounded")
    parser.add_argument("--timeframe", choices=["day"], default="day")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    request = SignalPasAlignmentRequest(
        source_pas_db=Path(args.source_pas_db),
        temp_root=Path(args.temp_root),
        report_root=Path(args.report_root),
        validated_root=Path(args.validated_root),
        run_id=args.run_id,
        source_pas_run_id=args.source_pas_run_id,
        mode=args.mode,
        timeframe=args.timeframe,
        schema_version=args.schema_version,
        signal_rule_version=args.signal_rule_version,
    )
    summary = run_signal_pas_alignment(request)
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0 if summary.hard_fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
