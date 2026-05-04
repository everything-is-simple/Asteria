from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Bar:
    symbol: str
    bar_dt: date
    high: float
    low: float


@dataclass
class Pivot:
    pivot_id: str
    symbol: str
    pivot_dt: date
    confirmed_dt: date
    pivot_type: str
    pivot_price: float
    pivot_seq_in_bar: int


@dataclass
class Wave:
    wave_id: str
    symbol: str
    wave_seq: int
    direction: str
    birth_type: str
    start_pivot_id: str
    candidate_guard_pivot_id: str
    confirm_pivot_id: str
    confirm_dt: date
    wave_core_state: str
    final_progress: Pivot
    final_guard: Pivot
    terminated_dt: date | None = None
    terminated_by_break_id: str | None = None


@dataclass
class Transition:
    transition_id: str
    old_wave_id: str
    break_id: str
    old_direction: str
    old_progress: Pivot
    old_guard: Pivot
    break_dt: date
    transition_boundary_high: float
    transition_boundary_low: float
    state: str = "open"
    confirmed_dt: date | None = None
    new_wave_id: str | None = None
    span: int = 0

    @property
    def boundary_high_pivot(self) -> Pivot:
        return (
            self.old_progress
            if self.old_progress.pivot_price >= self.old_guard.pivot_price
            else self.old_guard
        )

    @property
    def boundary_low_pivot(self) -> Pivot:
        return (
            self.old_progress
            if self.old_progress.pivot_price <= self.old_guard.pivot_price
            else self.old_guard
        )


@dataclass
class Candidate:
    candidate_id: str
    transition_id: str
    guard: Pivot
    direction: str
    reference_price: float
    is_active_at_close: bool = True
    invalidated_by_candidate_id: str | None = None
    confirmed_by_pivot_id: str | None = None
    confirmed_wave_id: str | None = None
    event_type: str = "candidate_created"

    @property
    def status(self) -> str:
        if self.confirmed_wave_id is not None:
            return "confirmed"
        if self.invalidated_by_candidate_id is not None:
            return "invalidated"
        return "active"


@dataclass(frozen=True)
class CoreBuildRows:
    pivots: list[Pivot]
    structures: list[tuple[object, ...]]
    waves: list[Wave]
    breaks: list[tuple[object, ...]]
    transitions: list[Transition]
    candidates: list[Candidate]
    snapshots: list[tuple[object, ...]]
