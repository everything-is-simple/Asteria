# Data Foundation Target Completeness Review Evidence Index

日期：2026-05-06

## 1. Repo Evidence

| 资产 | 用途 |
|---|---|
| `docs/02-modules/data/` | Data 六件套与 seal 口径 |
| `docs/04-execution/records/data/data-foundation-production-baseline-seal-20260502-01.conclusion.md` | 当前 Data baseline seal 结论 |
| `governance/module_gate_registry.toml` | Data gate 状态 |
| `governance/database_topology_registry.toml` | Data DB topology |
| `src/asteria/data` | Data 实现入口 |
| `scripts/data` | Data runner 入口 |
| `tests/unit/data` | Data 测试入口 |

## 2. Live DB Evidence

| DB | 只读证据 |
|---|---|
| `H:\Asteria-data\raw_market.duckdb` | raw source fact exists; logical duplicate groups `0` |
| `H:\Asteria-data\market_base_day.duckdb` | day analysis/execution price lines exist |
| `H:\Asteria-data\market_base_week.duckdb` | week analysis line exists |
| `H:\Asteria-data\market_base_month.duckdb` | month analysis line exists |
| `H:\Asteria-data\market_meta.duckdb` | minimal metadata facts exist; reference gaps retained |

## 3. Non-Evidence

本卡不提供新 DB、runner、validated zip、Data maintenance extension 或下游施工证据。
