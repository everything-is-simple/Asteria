# Data Foundation Build Card v1

日期：2026-05-02

状态：data-market-meta-formalization passed / reference gaps retained

## 1. 本轮目标

原 bounded bootstrap 已证明最小 TDX 输入可服务 MALF day proof。legacy formal
promotion 已把四个正式 Data DB 建成首轮全量底座，生产级六卡已补齐 execution
price line。本卡把 `market_meta.duckdb` 推进为最小正式 Data metadata fact：

```text
raw/base formal DB -> market_meta staging build -> hard audit -> formal promote -> release evidence
```

该链路只放行 Data Foundation，不占用 Alpha / Signal / Position / Portfolio / Trade /
System 的主线施工位，也不创建 Pipeline runtime。

## 2. 本轮允许修改

```text
docs/02-modules/data/
docs/02-modules/01-data-foundation-design-v1.md
docs/02-modules/04-mainline-module-delivery-index-v1.md
docs/03-refactor/00-module-gate-ledger-v1.md
src/asteria/data/
scripts/data/run_data_bootstrap.py
tests/unit/data/
```

## 3. 本轮禁止修改

| 禁止项 | 原因 |
|---|---|
| 伪造行业、ST、停牌或真实上市/退市事实 | 当前没有可靠 reference source |
| 迁移旧下游 runner 代码 | 旧代码只能做参考，新实现必须遵守 Asteria contract |
| 修改 MALF 及下游语义 | Data 不能重定义主线业务语义 |
| 建立全链路 pipeline | 当前主线仍锁定 MALF day bounded proof |
| 复制旧下游 DuckDB 为正式库 | 旧下游只读旁证，不是新主线语义权威 |

## 4. 本轮交付物

本轮交付：

```text
00-authority-design-v1.md
01-semantic-contract-v1.md
02-database-schema-spec-v1.md
03-runner-contract-v1.md
04-audit-spec-v1.md
05-build-card-v1.md
```

以及一个稳定入口文档：

```text
docs/02-modules/01-data-foundation-design-v1.md
```

以及最小实现：

```text
src/asteria/data/contracts.py
src/asteria/data/tdx_text.py
src/asteria/data/schema.py
src/asteria/data/bootstrap.py
src/asteria/data/market_meta.py
src/asteria/data/legacy_audit.py
scripts/data/run_data_bootstrap.py
scripts/data/run_market_meta_build.py
```

## 5. 验收命令

本轮至少执行：

```powershell
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py
H:\Asteria\.venv\Scripts\pytest.exe tests\unit\data -q
H:\Asteria\.venv\Scripts\python.exe scripts\data\run_market_meta_build.py --data-root H:\Asteria-data --temp-root H:\Asteria-temp --mode full --run-id data-market-meta-formalization-20260502-01
H:\Asteria\.venv\Scripts\python.exe scripts\data\run_data_production_audit.py --data-root H:\Asteria-data --run-id data-market-meta-formalization-20260502-01
git diff --check
```

## 6. Legacy intake 五卡

| 卡 | run_id | 范围 |
|---|---|---|
| Card 1 | `data-legacy-source-audit-20260502-01` | 只读审计旧 raw/base day/week/month |
| Card 2 | `data-legacy-import-contract-freeze-20260502-01` | 冻结 `stock-only + day/week/month + backward adjusted base` 导入合同 |
| Card 3 | `data-legacy-import-runner-working-build-20260502-01` | 实现旧库到 working DB 的导入 runner |
| Card 4 | `data-formal-promotion-evidence-20260502-01` | 审计并 promote 正式 Data DB |
| Card 5 | `malf-v1-3-formal-rebuild-closeout-20260502-01` | 用正式 Data 输入重建 MALF v1.3 evidence |

## 7. 下一轮建议

Data formal promotion 通过后，下一步回到：

```text
MALF v1.3 formal rebuild closeout
```

Position/downstream 仍按门禁决定，不因 Data 地基卡自动打开。

## 8. 生产级闭环六卡

| 卡 | run_id / 名称 | 状态 |
|---|---|---|
| 1 | `data-system-input-contract-freeze` | passed |
| 2 | `data-raw-market-full-build-formalization` | passed |
| 3 | `data-market-base-full-build-formalization` | passed |
| 4 | `data-execution-price-line-build` | passed |
| 5 | `data-daily-incremental-and-resume` | passed |
| 6 | `data-production-release-closeout-20260502-01` | passed |

六卡完成后，当前四个正式库仍是本版 Data 全量底座；新增的日更、断点续传与
执行价线能力只服务 Data Foundation，不自动打开下游施工。

## 9. Market meta 最小正式化卡

| 项 | 裁决 |
|---|---|
| run_id | `data-market-meta-formalization-20260502-01` |
| 状态 | passed |
| 放行表面 | `trade_calendar`、`instrument_master`、`instrument_alias`、`universe_membership`、`tradability_fact` |
| 保留缺口 | `industry_classification` 为空；行业、ST、停牌、真实上市/退市状态后续另开参考源卡 |
| allowed next action | `Position freeze review reentry` |
