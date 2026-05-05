from __future__ import annotations

from datetime import date

import pytest

from asteria.build_orchestration.batching import build_symbol_batches
from asteria.build_orchestration.scope import resolve_target_scope


def test_resolve_year_scope() -> None:
    scope = resolve_target_scope(year=2024)

    assert scope.target_start_dt == date(2024, 1, 1)
    assert scope.target_end_dt == date(2024, 12, 31)


def test_resolve_leap_month_scope() -> None:
    scope = resolve_target_scope(year=2024, month=2)

    assert scope.target_start_dt == date(2024, 2, 1)
    assert scope.target_end_dt == date(2024, 2, 29)


def test_resolve_single_day_scope() -> None:
    scope = resolve_target_scope(day="2024-01-15")

    assert scope.target_start_dt == date(2024, 1, 15)
    assert scope.target_end_dt == date(2024, 1, 15)


def test_resolve_conflicting_date_scope_fails() -> None:
    with pytest.raises(ValueError, match="exactly one date scope"):
        resolve_target_scope(year=2024, start_dt="2024-01-01", end_dt="2024-01-31")


def test_symbol_batches_are_stable_and_sized() -> None:
    universe = tuple(f"{index:06d}.SZ" for index in range(250))

    batches = build_symbol_batches(universe, batch_size=100)

    assert len(batches) == 3
    assert len(batches[0].symbols) == 100
    assert len(batches[1].symbols) == 100
    assert len(batches[2].symbols) == 50
    assert batches[0].batch_id == "batch-0001"


def test_symbol_range_selects_closed_interval() -> None:
    universe = ("000001.SZ", "000002.SZ", "000003.SZ", "000004.SZ")

    batches = build_symbol_batches(
        universe,
        batch_size=10,
        symbol_start="000002.SZ",
        symbol_end="000003.SZ",
    )

    assert batches[0].symbols == ("000002.SZ", "000003.SZ")
