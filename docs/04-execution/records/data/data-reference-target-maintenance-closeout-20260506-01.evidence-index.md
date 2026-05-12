# Data Reference Target Maintenance Closeout Evidence Index

日期：2026-05-06

## 1. Repo Evidence

| 资产 | 用途 |
|---|---|
| `docs/04-execution/records/data/data-reference-target-maintenance-scope-20260506-01.record.md` | 本卡冻结范围与验收合同 |
| `docs/04-execution/records/data/data-reference-target-maintenance-closeout-20260506-01.card.md` | 本执行卡 |
| `docs/04-execution/records/data/data-reference-target-maintenance-closeout-20260506-01.record.md` | 执行记录与 source inventory decision |
| `docs/04-execution/records/data/data-reference-target-maintenance-closeout-20260506-01.conclusion.md` | 本卡结论 |
| `docs/02-modules/data/03-runner-contract-v1.md` | `market_meta` runner contract 与 reference source gap 边界 |
| `docs/02-modules/data/04-audit-spec-v1.md` | `market_meta` audit 与 retained reference gap 边界 |
| `governance/module_gate_registry.toml` | 下一张允许卡切到 `malf_week_bounded_proof_build` |

## 2. Formal DB Evidence

| 资产 | 用途 |
|---|---|
| `H:\Asteria-data\market_meta.duckdb` | audit-only source fact surface; no mutation by this card |
| `H:\Asteria-data\raw_market.duckdb` | current `meta_source_manifest` upstream source |
| `H:\Asteria-data\market_base_day.duckdb` | current `tradability_fact.has_execution_bar` upstream source |
| `H:\Asteria-data\market_base_week.duckdb` | current `meta_source_manifest` upstream source |
| `H:\Asteria-data\market_base_month.duckdb` | current `meta_source_manifest` upstream source |

## 3. Reference Inventory

| 资产 | sha256 | closeout decision |
|---|---|---|
| `H:\Asteria-Validated\MALF-reference\申万行业分类\最新个股申万行业分类(完整版-截至7月末).xlsx` | `B242AB04E0F68357CF90772E3F15367644D3E74C08A767EB9C5EDCF21467FCBB` | already released as current SW2021 snapshot |
| `H:\Asteria-Validated\MALF-reference\申万行业分类\StockClassifyUse_stock.xls` | `15979D9CF8A3B83CCC8DADC967DE52F35E667B4F4DA5E4E4E3DD5A8BB1F17402` | inventory only; no approved import manifest in this card |
| `H:\Asteria-Validated\MALF-reference\申万行业分类\SwClassCode_2021.xls` | `923492F4BCF3C7056904385A0769E4DDA561904A29ECD9243F942680CEF68C81` | inventory only; no approved import manifest in this card |
| `H:\Asteria-Validated\MALF-reference\申万行业分类\SwClass.7z` | `9DD2D2C502045634974183A4E4061A1CC8B82FC292AFCAA3596FDC1EA0D8DF05` | inventory only; no approved import manifest in this card |
| `H:\Asteria-Validated\MALF-reference\A股市场\A股市场交易规则-tushare版.md` | `EE342CF401F24200B42FFE401675B3314FEF3A1454AB6B0D394D5C311900E874` | rules reference only; not per-instrument source facts |
| `H:\Asteria-Validated\MALF-reference\A股市场\A股申万行业指数-tushare版.md` | `033334ADC37F172D9BEA08485C1F619CCFF2B9475C9B1D633F0731D632B249CF` | API/reference note only; not released membership facts |
| `H:\Asteria-Validated\MALF-reference\A股市场\A股涨跌停板制度-tushare版.md` | `893B9F1883FA9FF4B88990D9F63B50B1C2248B4379A29491C88D25862B854872` | rules reference only; no ST status fact release |
| `H:\Asteria-Validated\MALF-reference\tushare\tushare-5000积分-官方-兜底号.md` | `4CFDD5BE1CA8632F7863F2BCC3A3DD24C18F048AC7E9384EBF40AEC41CE807DD` | credential note only; not used as data source |

## 4. External Evidence

| 资产 | 用途 |
|---|---|
| `H:\Asteria-report\data\2026-05-06\data-reference-target-maintenance-closeout-20260506-01\closeout-report.md` | 人读 closeout report |
| `H:\Asteria-report\data\2026-05-06\data-reference-target-maintenance-closeout-20260506-01\manifest.json` | report manifest |
| `H:\Asteria-Validated\Asteria-data-reference-target-maintenance-closeout-20260506-01.zip` | validated closeout evidence archive |

## 5. Non-Evidence

本卡不提供新 Data DB、schema migration、runner implementation、ST/停牌/官方上市退市/历史行业/index-block
正式事实，也不提供 MALF week/month、Alpha/Signal full build、Position construction 或 Pipeline runtime 证据。
