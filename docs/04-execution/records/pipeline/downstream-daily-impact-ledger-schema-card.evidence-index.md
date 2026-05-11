# Downstream Daily Impact Ledger Schema Card Evidence Index

日期：2026-05-11

## 1. Repo Evidence

| file | role |
|---|---|
| `governance/module_gate_registry.toml` | live next-card truth after schema freeze |
| `governance/module_api_contracts/position.toml` | Position Stage 11 writer contract |
| `governance/module_api_contracts/portfolio_plan.toml` | Portfolio Plan Stage 11 writer contract |
| `governance/module_api_contracts/trade.toml` | Trade Stage 11 writer contract |
| `governance/module_api_contracts/system_readout.toml` | System Readout read-only Stage 11 contract |
| `governance/module_api_contracts/pipeline.toml` | pipeline next-action truth after schema freeze |
| `governance/database_topology_registry.toml` | downstream replay/checkpoint protocol freeze |
| `tests/unit/governance/test_downstream_daily_impact_ledger_schema_gate_transition.py` | gate transition and contract/topology coverage |
| `docs/02-modules/position/02-database-schema-spec-v1.md` | Position impact map documentation |
| `docs/02-modules/portfolio_plan/02-database-schema-spec-v1.md` | Portfolio Plan impact map documentation |
| `docs/02-modules/trade/02-database-schema-spec-v1.md` | Trade impact map documentation |
| `docs/02-modules/system_readout/02-database-schema-spec-v1.md` | System Readout impact map documentation |
| `docs/04-execution/records/pipeline/downstream-daily-incremental-runner-build-card.card.md` | prepared next card |

## 2. External Evidence

- none; this card is contract / governance / design freeze only
