from __future__ import annotations

from pathlib import Path

import duckdb

from asteria.pipeline.year_replay_coverage_gap_contracts import CoverageMatrixRow
from asteria.pipeline.year_replay_portfolio_plan_semantics import (
    evaluate_portfolio_plan_focus_window,
)

RUN_ID = "portfolio-plan-bounded-proof-build-card-20260507-01"
FOCUS_DATES = ["2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]


def test_accepts_missing_exposure_on_rejected_or_expired_focus_dates(tmp_path: Path) -> None:
    portfolio_db = tmp_path / "portfolio_plan.duckdb"
    _seed_portfolio_db(
        portfolio_db,
        admissions=[
            ("2024-01-02", "rejected"),
            ("2024-01-03", "rejected"),
            ("2024-01-04", "expired"),
            ("2024-01-05", "admitted"),
        ],
        exposure_dates=["2024-01-05"],
    )

    ok = evaluate_portfolio_plan_focus_window(
        portfolio_rows=[
            _row("portfolio_admission_ledger", "2024-01-02", "2024-12-31", ()),
            _row(
                "portfolio_target_exposure",
                "2024-01-05",
                "2024-12-31",
                ("2024-01-02", "2024-01-03", "2024-01-04"),
            ),
        ],
        portfolio_db=portfolio_db,
        portfolio_run_id=RUN_ID,
        focus_dates=FOCUS_DATES,
    )

    assert ok is True


def test_rejects_missing_exposure_for_admitted_or_trimmed_focus_dates(tmp_path: Path) -> None:
    portfolio_db = tmp_path / "portfolio_plan.duckdb"
    _seed_portfolio_db(
        portfolio_db,
        admissions=[
            ("2024-01-02", "rejected"),
            ("2024-01-03", "rejected"),
            ("2024-01-04", "trimmed"),
            ("2024-01-05", "admitted"),
        ],
        exposure_dates=["2024-01-05"],
    )

    ok = evaluate_portfolio_plan_focus_window(
        portfolio_rows=[
            _row("portfolio_admission_ledger", "2024-01-02", "2024-12-31", ()),
            _row(
                "portfolio_target_exposure",
                "2024-01-05",
                "2024-12-31",
                ("2024-01-02", "2024-01-03", "2024-01-04"),
            ),
        ],
        portfolio_db=portfolio_db,
        portfolio_run_id=RUN_ID,
        focus_dates=FOCUS_DATES,
    )

    assert ok is False


def _seed_portfolio_db(
    path: Path,
    *,
    admissions: list[tuple[str, str]],
    exposure_dates: list[str],
) -> None:
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table portfolio_admission_ledger (
                portfolio_admission_id varchar,
                plan_dt date,
                admission_state varchar,
                run_id varchar
            )
            """
        )
        con.execute(
            """
            create table portfolio_target_exposure (
                target_exposure_id varchar,
                exposure_valid_from date,
                run_id varchar
            )
            """
        )
        con.executemany(
            "insert into portfolio_admission_ledger values (?, ?, ?, ?)",
            [
                [f"adm-{index}", plan_dt, state, RUN_ID]
                for index, (plan_dt, state) in enumerate(admissions, start=1)
            ],
        )
        con.executemany(
            "insert into portfolio_target_exposure values (?, ?, ?)",
            [
                [f"exp-{index}", exposure_dt, RUN_ID]
                for index, exposure_dt in enumerate(exposure_dates, start=1)
            ],
        )


def _row(
    surface_name: str,
    observed_start: str,
    observed_end: str,
    missing_focus_dates: tuple[str, ...],
) -> CoverageMatrixRow:
    return CoverageMatrixRow(
        layer="portfolio_plan",
        surface_name=surface_name,
        db_path="portfolio_plan.duckdb",
        table_name=surface_name,
        run_selector=f"run_id = '{RUN_ID}'",
        date_column=(
            "plan_dt" if surface_name == "portfolio_admission_ledger" else "exposure_valid_from"
        ),
        observed_start=observed_start,
        observed_end=observed_end,
        row_count_2024=1,
        missing_focus_dates=missing_focus_dates,
        notes="unit-test",
    )
