from __future__ import annotations

from asteria.pipeline.stage11_daily_protocol_contracts import (
    Stage11DailyProtocolSpec,
    build_stage11_daily_protocol_spec,
    validate_stage11_daily_protocol_spec,
)


def test_stage11_protocol_freezes_day_only_dirty_and_impact_scope() -> None:
    spec = build_stage11_daily_protocol_spec()

    assert spec.timeframe == "day"
    assert spec.module_chain == (
        "data",
        "malf",
        "alpha",
        "signal",
        "position",
        "portfolio_plan",
        "trade",
        "system_readout",
        "pipeline",
    )
    assert spec.daily_dirty_scope_fields == (
        "symbol",
        "trade_date",
        "timeframe",
        "source_run_id",
    )
    assert spec.daily_impact_scope_fields == (
        "symbol",
        "trade_date",
        "timeframe",
        "upstream_module",
        "source_run_id",
    )
    assert spec.checkpoint_fields == (
        "module_scope",
        "timeframe",
        "trade_date",
        "symbol",
        "source_run_id",
    )
    assert spec.lineage_fields == ("source_run_id", "target_run_id")
    assert spec.writer_modules == (
        "data",
        "malf",
        "alpha",
        "signal",
        "position",
        "portfolio_plan",
        "trade",
    )
    assert spec.read_only_modules == ("system_readout", "pipeline")
    assert validate_stage11_daily_protocol_spec(spec) == []


def test_stage11_protocol_validator_rejects_read_only_module_as_writer() -> None:
    spec = Stage11DailyProtocolSpec(
        protocol_run_id="system-wide-daily-dirty-scope-protocol-card",
        protocol_action="system_wide_daily_dirty_scope_protocol_card",
        next_run_id="data-ledger-daily-incremental-hardening-card",
        next_action="data_ledger_daily_incremental_hardening_card",
        timeframe="day",
        module_chain=(
            "data",
            "malf",
            "alpha",
            "signal",
            "position",
            "portfolio_plan",
            "trade",
            "system_readout",
            "pipeline",
        ),
        daily_dirty_scope_fields=("symbol", "trade_date", "timeframe", "source_run_id"),
        daily_impact_scope_fields=(
            "symbol",
            "trade_date",
            "timeframe",
            "upstream_module",
            "source_run_id",
        ),
        checkpoint_fields=(
            "module_scope",
            "timeframe",
            "trade_date",
            "symbol",
            "source_run_id",
        ),
        lineage_fields=("source_run_id", "target_run_id"),
        writer_modules=("data", "system_readout"),
        read_only_modules=("system_readout", "pipeline"),
    )

    assert validate_stage11_daily_protocol_spec(spec) == [
        "read-only modules must not appear in writer_modules"
    ]
