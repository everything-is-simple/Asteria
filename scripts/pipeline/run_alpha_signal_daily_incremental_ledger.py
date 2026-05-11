from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

from asteria.alpha.contracts import AlphaDailyIncrementalLedgerRequest
from asteria.alpha.daily_incremental_ledger import run_alpha_daily_incremental_ledger
from asteria.signal.contracts import SignalDailyIncrementalLedgerRequest
from asteria.signal.daily_incremental_ledger import run_signal_daily_incremental_ledger

REPORT_DATE = "2026-05-11"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the Alpha/Signal day daily incremental sample ledger."
    )
    parser.add_argument("--malf-root", default="H:/Asteria-temp/malf-target")
    parser.add_argument("--alpha-root", default="H:/Asteria-temp/alpha-target")
    parser.add_argument("--signal-db", default="H:/Asteria-temp/signal-target/signal.duckdb")
    parser.add_argument("--temp-root", default="H:/Asteria-temp")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--validated-root", default="H:/Asteria-Validated")
    parser.add_argument("--run-id", default="alpha-signal-daily-incremental-ledger-build-card")
    parser.add_argument(
        "--mode",
        choices=["daily_incremental", "resume", "audit-only"],
        default="daily_incremental",
    )
    parser.add_argument(
        "--malf-daily-impact-scope-path",
        default="H:/Asteria-temp/malf/malf-daily-incremental-ledger-build-card/daily-impact-scope.json",
    )
    parser.add_argument(
        "--malf-lineage-path",
        default="H:/Asteria-temp/malf/malf-daily-incremental-ledger-build-card/lineage.json",
    )
    parser.add_argument(
        "--malf-checkpoint-path",
        default="H:/Asteria-temp/malf/malf-daily-incremental-ledger-build-card/checkpoint.json",
    )
    args = parser.parse_args()

    alpha_summary = run_alpha_daily_incremental_ledger(
        AlphaDailyIncrementalLedgerRequest(
            source_malf_root=Path(args.malf_root),
            target_root=Path(args.alpha_root),
            temp_root=Path(args.temp_root),
            report_root=Path(args.report_root),
            run_id=args.run_id,
            mode=args.mode,
            malf_daily_impact_scope_path=Path(args.malf_daily_impact_scope_path),
            malf_lineage_path=Path(args.malf_lineage_path),
            malf_checkpoint_path=Path(args.malf_checkpoint_path),
        )
    )
    signal_summary = run_signal_daily_incremental_ledger(
        SignalDailyIncrementalLedgerRequest(
            source_alpha_root=Path(args.alpha_root),
            target_signal_db=Path(args.signal_db),
            temp_root=Path(args.temp_root),
            report_root=Path(args.report_root),
            run_id=args.run_id,
            mode=args.mode,
            alpha_daily_impact_scope_path=Path(alpha_summary.daily_impact_scope_path),
            alpha_lineage_path=Path(alpha_summary.lineage_path),
            alpha_checkpoint_path=Path(alpha_summary.checkpoint_path),
        )
    )

    report_dir = Path(args.report_root) / "pipeline" / REPORT_DATE / args.run_id
    report_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": args.run_id,
        "mode": args.mode,
        "status": "passed"
        if alpha_summary.status == "passed" and signal_summary.status == "passed"
        else "failed",
        "boundaries": {
            "day_only": True,
            "formal_data_mutation": False,
            "downstream_runtime_opened": False,
        },
        "alpha": alpha_summary.as_dict(),
        "signal": signal_summary.as_dict(),
    }
    summary_path = report_dir / "summary.json"
    closeout_path = report_dir / "closeout.md"
    validated_zip = Path(args.validated_root) / f"Asteria-{args.run_id}-20260511-01.zip"
    summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    closeout_path.write_text(_closeout_text(payload), encoding="utf-8")
    validated_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(validated_zip, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(summary_path, summary_path.name)
        archive.write(closeout_path, closeout_path.name)
        archive.write(
            Path(alpha_summary.audit_summary_path),
            f"alpha/{Path(alpha_summary.audit_summary_path).name}",
        )
        archive.write(
            Path(signal_summary.audit_summary_path),
            f"signal/{Path(signal_summary.audit_summary_path).name}",
        )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "passed" else 1


def _closeout_text(payload: dict[str, object]) -> str:
    lines = [
        f"# Alpha/Signal daily incremental closeout: {payload['run_id']}",
        "",
        f"- status: {payload['status']}",
        "- boundaries: day-only / temp-only / no formal H:/Asteria-data mutation",
        "- downstream daily runtime: not opened",
        "- next allowed action: downstream_daily_impact_ledger_schema_card",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
