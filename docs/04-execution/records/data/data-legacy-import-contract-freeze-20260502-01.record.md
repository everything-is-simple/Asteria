# Data Legacy Import Contract Freeze Record

日期：2026-05-02

run_id：`data-legacy-import-contract-freeze-20260502-01`

## 1. Inputs

- `docs/04-execution/records/data/data-legacy-source-audit-20260502-01.conclusion.md`
- `H:\Asteria-report\data\2026-05-02\data-legacy-source-audit-20260502-01\legacy-source-audit.md`
- `H:\Lifespan-data\raw`
- `H:\Lifespan-data\base`

## 2. Changes

更新 Data 六件套：

- `docs/02-modules/data/00-authority-design-v1.md`
- `docs/02-modules/data/01-semantic-contract-v1.md`
- `docs/02-modules/data/02-database-schema-spec-v1.md`
- `docs/02-modules/data/03-runner-contract-v1.md`
- `docs/02-modules/data/04-audit-spec-v1.md`
- `docs/02-modules/data/05-build-card-v1.md`

更新治理面：

- `docs/03-refactor/00-module-gate-ledger-v1.md`
- `docs/04-execution/00-conclusion-index-v1.md`
- `governance/module_gate_registry.toml`

## 3. Frozen Contract

| 项 | 结论 |
|---|---|
| source kind | legacy Lifespan raw/base DuckDB |
| asset type | `stock` |
| timeframe | `day / week / month` |
| adjustment | `backward` |
| raw target | `H:\Asteria-data\raw_market.duckdb` after promotion |
| base target | `H:\Asteria-data\market_base_day/week/month.duckdb` after promotion |
| index/block | sidecar availability only |

## 4. Boundary

本卡不执行导入，不写正式 DB，不声明 Data full build released。下一步只允许
`data-legacy-import-runner-working-build-20260502-01`。
