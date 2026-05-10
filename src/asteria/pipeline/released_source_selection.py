from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import duckdb

from asteria.pipeline.contracts import PIPELINE_YEAR_REPLAY_RERUN_REQUIRED_MALF_RUN_ID


@dataclass(frozen=True)
class ReleasedSourceEntry:
    module_name: str
    source_db: str
    source_run_id: str
    source_release_version: str

    def as_dict(self) -> dict[str, str]:
        return {
            "module_name": self.module_name,
            "source_db": self.source_db,
            "source_run_id": self.source_run_id,
            "source_release_version": self.source_release_version,
        }


@dataclass(frozen=True)
class ReleasedYearReplaySourceSelection:
    released_system_run_id: str
    observed_start: str | None
    observed_end: str | None
    year_observed_start: str | None
    year_observed_end: str | None
    manifest: dict[str, ReleasedSourceEntry]
    source_lock_clean: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "released_system_run_id": self.released_system_run_id,
            "observed_start": self.observed_start,
            "observed_end": self.observed_end,
            "year_observed_start": self.year_observed_start,
            "year_observed_end": self.year_observed_end,
            "source_lock_clean": self.source_lock_clean,
            "manifest": {
                module_name: entry.as_dict() for module_name, entry in self.manifest.items()
            },
        }


def resolve_released_year_replay_source_selection(
    system_db: Path,
    *,
    target_year: int | None = None,
) -> ReleasedYearReplaySourceSelection:
    released_system_run_id = _load_latest_completed_system_run(system_db)
    manifest = _load_system_source_manifest(system_db, released_system_run_id)
    observed_start, observed_end, year_observed_start, year_observed_end = _load_coverage_window(
        system_db,
        released_system_run_id,
        target_year=target_year,
    )
    malf_entry = manifest.get("malf")
    source_lock_clean = (
        malf_entry is not None
        and malf_entry.source_run_id == PIPELINE_YEAR_REPLAY_RERUN_REQUIRED_MALF_RUN_ID
    )
    return ReleasedYearReplaySourceSelection(
        released_system_run_id=released_system_run_id,
        observed_start=observed_start,
        observed_end=observed_end,
        year_observed_start=year_observed_start,
        year_observed_end=year_observed_end,
        manifest=manifest,
        source_lock_clean=source_lock_clean,
    )


def _load_latest_completed_system_run(system_db: Path) -> str:
    with duckdb.connect(str(system_db), read_only=True) as con:
        row = con.execute(
            """
            select run_id
            from system_readout_run
            where status = 'completed'
            order by created_at desc
            limit 1
            """
        ).fetchone()
    if row is None or row[0] is None:
        raise ValueError("missing completed system_readout_run row")
    return str(row[0])


def _load_system_source_manifest(
    system_db: Path,
    released_system_run_id: str,
) -> dict[str, ReleasedSourceEntry]:
    with duckdb.connect(str(system_db), read_only=True) as con:
        rows = con.execute(
            """
            select module_name, source_db, source_run_id, source_release_version
            from system_source_manifest
            where system_readout_run_id = ?
            """,
            [released_system_run_id],
        ).fetchall()
    return {
        str(module_name): ReleasedSourceEntry(
            module_name=str(module_name),
            source_db=str(source_db),
            source_run_id=str(source_run_id),
            source_release_version=str(source_release_version),
        )
        for module_name, source_db, source_run_id, source_release_version in rows
    }


def _load_coverage_window(
    system_db: Path,
    released_system_run_id: str,
    *,
    target_year: int | None,
) -> tuple[str | None, str | None, str | None, str | None]:
    with duckdb.connect(str(system_db), read_only=True) as con:
        overall_row = con.execute(
            """
            select min(readout_dt), max(readout_dt)
            from system_chain_readout
            where system_readout_run_id = ?
            """,
            [released_system_run_id],
        ).fetchone()
        if target_year is None:
            year_row = overall_row
        else:
            year_row = con.execute(
                """
                select min(readout_dt), max(readout_dt)
                from system_chain_readout
                where system_readout_run_id = ?
                  and readout_dt >= ?
                  and readout_dt <= ?
                """,
                [
                    released_system_run_id,
                    f"{target_year}-01-01",
                    f"{target_year}-12-31",
                ],
            ).fetchone()
    return (
        _coerce_optional_date(overall_row, 0),
        _coerce_optional_date(overall_row, 1),
        _coerce_optional_date(year_row, 0),
        _coerce_optional_date(year_row, 1),
    )


def _coerce_optional_date(row: tuple[object, ...] | None, index: int) -> str | None:
    if row is None or row[index] is None:
        return None
    return str(row[index])
