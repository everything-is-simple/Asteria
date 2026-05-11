# System-Wide Daily Dirty Scope Protocol Evidence Index

日期：2026-05-11

run_id：`system-wide-daily-dirty-scope-protocol-card`

## 1. Repo Evidence

| file | role |
|---|---|
| `src/asteria/pipeline/stage11_daily_protocol_contracts.py` | Stage 11 day-only protocol contract skeleton |
| `tests/unit/pipeline/test_stage11_daily_dirty_scope_protocol_contracts.py` | protocol object and validator coverage |
| `tests/unit/governance/test_stage11_daily_dirty_scope_protocol_gate_transition.py` | live next-card transition coverage |
| `governance/module_gate_registry.toml` | live next-card / active foundation card truth |
| `governance/module_api_contracts/pipeline.toml` | Pipeline Stage 11 protocol fields and next action |
| `governance/module_api_contracts/system_readout.toml` | System Readout read-only Stage 11 contract role |
| `docs/03-refactor/00-module-gate-ledger-v1.md` | current gate summary and allowed next action |
| `docs/03-refactor/04-asteria-full-system-roadmap-v1.md` | Stage 11 queue authority |
| `docs/04-execution/00-conclusion-index-v1.md` | protocol conclusion row and live next card index |
| `docs/04-execution/records/data/data-ledger-daily-incremental-hardening-card.card.md` | newly prepared follow-up card |

## 2. Non-Evidence

本卡不提供新的 `pipeline.duckdb`、`system.duckdb`、daily runtime closeout、validated runtime evidence、
full rebuild evidence 或 daily incremental evidence。

## 3. Protocol Evidence

本卡只证明 Stage 11 day 主链协议已经冻结，并把唯一 live next card 切到
`data-ledger-daily-incremental-hardening-card`。真正的 daily incremental / resume / audit 运行证据，
必须由后续 Data / MALF / Alpha-Signal / downstream 独立卡继续证明。
