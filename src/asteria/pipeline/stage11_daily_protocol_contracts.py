from __future__ import annotations

from dataclasses import dataclass

PIPELINE_STAGE11_PROTOCOL_CARD = "system-wide-daily-dirty-scope-protocol-card"
PIPELINE_STAGE11_PROTOCOL_ACTION = "system_wide_daily_dirty_scope_protocol_card"
DATA_DAILY_HARDENING_CARD = "data-ledger-daily-incremental-hardening-card"
DATA_DAILY_HARDENING_ACTION = "data_ledger_daily_incremental_hardening_card"


@dataclass(frozen=True)
class Stage11DailyProtocolSpec:
    protocol_run_id: str
    protocol_action: str
    next_run_id: str
    next_action: str
    timeframe: str
    module_chain: tuple[str, ...]
    daily_dirty_scope_fields: tuple[str, ...]
    daily_impact_scope_fields: tuple[str, ...]
    checkpoint_fields: tuple[str, ...]
    lineage_fields: tuple[str, ...]
    writer_modules: tuple[str, ...]
    read_only_modules: tuple[str, ...]


def build_stage11_daily_protocol_spec() -> Stage11DailyProtocolSpec:
    return Stage11DailyProtocolSpec(
        protocol_run_id=PIPELINE_STAGE11_PROTOCOL_CARD,
        protocol_action=PIPELINE_STAGE11_PROTOCOL_ACTION,
        next_run_id=DATA_DAILY_HARDENING_CARD,
        next_action=DATA_DAILY_HARDENING_ACTION,
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
        writer_modules=(
            "data",
            "malf",
            "alpha",
            "signal",
            "position",
            "portfolio_plan",
            "trade",
        ),
        read_only_modules=("system_readout", "pipeline"),
    )


def validate_stage11_daily_protocol_spec(spec: Stage11DailyProtocolSpec) -> list[str]:
    findings: list[str] = []
    if spec.timeframe != "day":
        findings.append("Stage 11 protocol must stay day-only")
    if spec.lineage_fields != ("source_run_id", "target_run_id"):
        findings.append("Stage 11 protocol lineage_fields must be source_run_id -> target_run_id")
    if set(spec.read_only_modules).intersection(spec.writer_modules):
        findings.append("read-only modules must not appear in writer_modules")
    if spec.read_only_modules != ("system_readout", "pipeline"):
        findings.append("Stage 11 protocol read_only_modules must stay system_readout + pipeline")
    if spec.module_chain[-2:] != ("system_readout", "pipeline"):
        findings.append("Stage 11 protocol must end with system_readout -> pipeline")
    return findings
