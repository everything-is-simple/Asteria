from __future__ import annotations

from asteria.pipeline.downstream_coverage_gap_closeout import (
    resolve_downstream_closeout_decision,
)
from asteria.pipeline.year_replay_coverage_gap_contracts import (
    EVIDENCE_INCOMPLETE_CARD,
    PORTFOLIO_PLAN_REPAIR_CARD,
    POSITION_REPAIR_CARD,
    TRADE_REPAIR_CARD,
)


def test_returns_position_repair_when_position_is_first_downstream_break() -> None:
    decision = resolve_downstream_closeout_decision(
        layer_statuses={
            "position": False,
            "portfolio_plan": False,
            "trade": False,
        },
        evidence_issues=[],
    )

    assert decision.next_card == POSITION_REPAIR_CARD
    assert decision.attribution == "downstream_surface_gap:position"


def test_returns_portfolio_plan_repair_when_position_is_covered_but_portfolio_plan_breaks() -> None:
    decision = resolve_downstream_closeout_decision(
        layer_statuses={
            "position": True,
            "portfolio_plan": False,
            "trade": False,
        },
        evidence_issues=[],
    )

    assert decision.next_card == PORTFOLIO_PLAN_REPAIR_CARD
    assert decision.attribution == "downstream_surface_gap:portfolio_plan"


def test_returns_trade_repair_when_trade_is_first_remaining_break() -> None:
    decision = resolve_downstream_closeout_decision(
        layer_statuses={
            "position": True,
            "portfolio_plan": True,
            "trade": False,
        },
        evidence_issues=[],
    )

    assert decision.next_card == TRADE_REPAIR_CARD
    assert decision.attribution == "downstream_surface_gap:trade"


def test_retains_evidence_incomplete_when_probe_evidence_is_not_unique() -> None:
    decision = resolve_downstream_closeout_decision(
        layer_statuses={
            "position": False,
            "portfolio_plan": False,
            "trade": False,
        },
        evidence_issues=["system_source_manifest is missing signal entry"],
    )

    assert decision.next_card == EVIDENCE_INCOMPLETE_CARD
    assert decision.attribution == "evidence_incomplete"
