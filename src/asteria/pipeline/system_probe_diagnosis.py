from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import duckdb

from asteria.pipeline.year_replay_coverage_gap_diagnosis import (
    YearReplayCoverageGapDiagnosisRequest,
    YearReplayCoverageGapDiagnosisSummary,
    run_year_replay_coverage_gap_diagnosis,
)
from asteria.system_readout.bootstrap import run_system_readout_build
from asteria.system_readout.contracts import SystemReadoutBuildRequest


@dataclass(frozen=True)
class SystemProbeDiagnosisSummary:
    probe_root: str
    probe_system_db: str
    system_probe_run_id: str
    diagnosis_summary: YearReplayCoverageGapDiagnosisSummary

    def as_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["diagnosis_summary"] = self.diagnosis_summary.as_dict()
        return payload


def run_system_probe_diagnosis(
    *,
    probe_root: Path,
    repo_root: Path,
    data_root: Path,
    run_id_prefix: str,
    target_year: int,
) -> SystemProbeDiagnosisSummary:
    probe_report_root = probe_root / "report"
    probe_validated_root = probe_root / "validated"
    probe_temp_root = probe_root / "temp"
    probe_system_db = probe_root / "system-probe.duckdb"
    probe_run_id = f"{run_id_prefix}-system-probe"
    probe_diagnosis_run_id = f"{probe_run_id}-diagnosis"

    if probe_system_db.exists():
        probe_system_db.unlink()

    run_system_readout_build(
        SystemReadoutBuildRequest(
            source_malf_service_db=data_root / "malf_service_day.duckdb",
            source_alpha_root=data_root,
            source_signal_db=data_root / "signal.duckdb",
            source_position_db=data_root / "position.duckdb",
            source_portfolio_plan_db=data_root / "portfolio_plan.duckdb",
            source_trade_db=data_root / "trade.duckdb",
            target_system_db=probe_system_db,
            report_root=probe_report_root,
            validated_root=probe_validated_root,
            temp_root=probe_temp_root,
            run_id=probe_run_id,
            mode="bounded",
            source_chain_release_version=_load_latest_completed_run_id(
                data_root / "trade.duckdb",
                "trade_run",
            ),
            start_dt=f"{target_year}-01-01",
            end_dt=f"{target_year}-12-31",
            symbol_limit=1_000_000,
        )
    )
    diagnosis_summary = run_year_replay_coverage_gap_diagnosis(
        YearReplayCoverageGapDiagnosisRequest(
            repo_root=repo_root,
            source_system_db=probe_system_db,
            report_root=probe_report_root,
            validated_root=probe_validated_root,
            run_id=probe_diagnosis_run_id,
            target_year=target_year,
            data_root=data_root,
        )
    )
    return SystemProbeDiagnosisSummary(
        probe_root=str(probe_root),
        probe_system_db=str(probe_system_db),
        system_probe_run_id=probe_run_id,
        diagnosis_summary=diagnosis_summary,
    )


def _load_latest_completed_run_id(db_path: Path, run_table: str) -> str:
    with duckdb.connect(str(db_path), read_only=True) as con:
        row = con.execute(
            f"""
            select run_id
            from {run_table}
            where status = 'completed'
            order by created_at desc
            limit 1
            """
        ).fetchone()
    if row is None or row[0] is None:
        raise ValueError(f"missing completed run_id in {run_table}: {db_path}")
    return str(row[0])
