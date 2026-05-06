# Data Reference Target Maintenance Closeout Record

日期：2026-05-06

## 1. 卡信息

| 项 | 值 |
|---|---|
| module | `data` |
| run_id | `data-reference-target-maintenance-closeout-20260506-01` |
| result | `passed / source inventory closed / gaps retained` |

## 2. 执行内容

1. 重读 Asteria 必读治理文件、Data 六件套、Data reference scope card 与当前 Pre-Position 修补队列。
2. 使用 `codebase-retrieval` 定位 Data closeout card、scope record、`market_meta` runner/schema/audit、gate registry 与 governance tests。
3. 审阅正式 `H:\Asteria-data\market_meta.duckdb` 表面，确认当前 released source manifest 与 row counts。
4. 执行 Data production audit 与 `market_meta` audit-only；两项均 `passed / hard_fail_count=0`。
5. 清点 `H:\Asteria-Validated\Market-Average-Lifespan-reference` 中可用 reference 资产，裁定哪些能释放、哪些必须 retained。
6. 未修改 `H:\Asteria-data` 正式 DB，未创建 Data runner、Position runner、Position DB 或 Pipeline runtime。

## 3. Formal DB Audit

| audit | result |
|---|---|
| `scripts\data\run_data_production_audit.py --data-root H:\Asteria-data --run-id data-reference-target-maintenance-closeout-20260506-01` | `passed`; `hard_fail_count=0` |
| `scripts\data\run_market_meta_build.py --data-root H:\Asteria-data --temp-root H:\Asteria-temp --mode audit-only --run-id data-reference-target-maintenance-closeout-20260506-01` | `passed`; `hard_fail_count=0`; `promoted=false` |

Current `market_meta.duckdb` row counts:

| table | rows |
|---|---:|
| `trade_calendar` | 8684 |
| `instrument_master` | 5503 |
| `instrument_alias` | 16513 |
| `universe_membership` | 5503 |
| `tradability_fact` | 16376944 |
| `industry_classification` | 4237 |
| `meta_run` | 1 |
| `meta_schema_version` | 1 |
| `meta_source_manifest` | 4 |

## 4. Source Inventory Decision

| reference gap | inventory result | release decision |
|---|---|---|
| ST 标记 | 只有交易规则参考文档提到 ST 规则；没有 approved per-instrument/per-date source manifest | `retained_gap`; no synthetic facts |
| 停牌 / 可交易状态 | `has_execution_bar` 已释放；没有官方停复牌 source manifest | `has_execution_bar` remains released; official suspension retained |
| 真实上市 / 退市生命周期 | `instrument_master.list_status=observed` 仅来自 raw/base 观测；没有官方 lifecycle source | `observed` remains released; official listed/delisted retained |
| 历史行业沿革 | 已释放 SW2021 current snapshot；其他行业文件未形成 approved historical lineage import manifest | current snapshot remains released; history retained |
| index / block / universe membership | 参考目录有行业指数说明文档，但没有可审计 membership dataset manifest | `stock_observed` remains released; index/block membership retained |
| week/month execution price line | scope card 已裁定不是 MALF week/month 前置必补 | retained for future Trade/Position execution semantics |

## 5. 硬边界

| 项 | 裁决 |
|---|---|
| Data 角色 | source facts only / not strategy module |
| Formal DB mutation | not executed by this closeout |
| New Data reference facts | none released |
| Position construction | suspended |
| Pipeline runtime | not opened |
| next allowed card | `malf_week_bounded_proof_build` |

## 6. 验收结论

本卡满足上一张 scope card 的验收口径：有 approved source 的事实保持 released；无 approved source
manifest 的事实明确登记为 retained gap，不以推断值或规则文档填充正式 DB。该结论不声明 Data final target
complete，只关闭本轮 Data reference target maintenance closeout，并把下一步切到 MALF week bounded proof build。
