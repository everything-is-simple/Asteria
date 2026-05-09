# Asteria 星脉系统

**Asteria Market Lifespan Framework** 是一个以市场结构为骨架、以波段生命为核心、以 Alpha 解释和组合执行为外部行为的系统化交易研究框架。

内部核心名：

```text
MALF = Market Lifespan Framework
```

## 五根目录

| 路径 | 职责 |
|---|---|
| `H:\Asteria` | 代码、文档、测试、治理入口 |
| `H:\Asteria-data` | 正式 DuckDB 数据资产与长期中间库 |
| `H:\Asteria-report` | 人读报告、图表、导出结果 |
| `H:\Asteria-Validated` | 已验证设计、历史快照、正式证据资产 |
| `H:\Asteria-temp` | working DB、pytest、缓存、临时重建产物 |

`H:\Asteria-temp` 也是 Codex / 本地治理检查 / 临时 scratch 的唯一落位；repo 根目录不得新增
`.codex-tmp/`、`tmp/`、`temp/`、`reports/`、`artifacts/` 这类临时目录。

## 当前重构原则

1. 先有权威设计，再有实现。
2. 一次只允许一个模块进入主线施工。
3. 未经验证的模块不得上线主线。
4. `data` 是基础建设层，不是策略主线层。
5. 主线从 `MALF` 开始，经 `Alpha -> Signal -> Position -> Portfolio Plan -> Trade -> System` 向外展开。
6. DuckDB 采用空间换时间：模块分库、时间级别分库、冷热事实分库。

## 当前权威状态

当前权威资产：

```text
H:\Asteria-Validated\Asteria-deep-research-report-重构系统最新剖切面研究报告-20260428.md
H:\Asteria-Validated\Asteria-docs-code-20260502-104932.zip
H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4
H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4.zip
H:\Asteria-Validated\Asteria-data-formal-promotion-evidence-20260502-01.zip
H:\Asteria-Validated\Asteria-malf-v1-3-formal-rebuild-closeout-20260502-01.zip
H:\Asteria-Validated\Asteria-malf-v1-4-core-runtime-sync-implementation-20260505-01.zip
H:\Asteria-Validated\Asteria-data-production-release-closeout-20260502-01.zip
H:\Asteria-Validated\Asteria-data-execution-price-line-materialization-20260502-01.zip
H:\Asteria-Validated\Asteria-data-market-meta-formalization-20260502-01.zip
H:\Asteria-Validated\Asteria-data-market-meta-sw-industry-snapshot-20260502-01.zip
H:\Asteria-Validated\Asteria-data-foundation-production-baseline-seal-20260502-01.zip
H:\Asteria-Validated\Asteria-data-reference-target-maintenance-closeout-20260506-01.zip
H:\Asteria-Validated\Asteria-malf-week-bounded-proof-build-20260506-01.zip
H:\Asteria-Validated\Asteria-malf-month-bounded-proof-build-20260506-01.zip
H:\Asteria-Validated\Asteria-alpha-production-builder-hardening-20260506-01.zip
H:\Asteria-Validated\Asteria-signal-production-builder-hardening-20260506-01.zip
H:\Asteria-Validated\Asteria-position-bounded-proof-build-card-20260506-01.zip
H:\Asteria-Validated\Asteria-portfolio-plan-freeze-review-20260507-01.zip
H:\Asteria-Validated\Asteria-portfolio-plan-bounded-proof-build-card-20260507-01.zip
H:\Asteria-Validated\Asteria-trade-freeze-review-20260507-01.zip
H:\Asteria-Validated\Asteria-trade-bounded-proof-build-card-20260507-01.zip
H:\Asteria-Validated\Asteria-system-readout-freeze-review-20260507-01.zip
H:\Asteria-Validated\Asteria-pipeline-full-chain-bounded-proof-authorization-scope-freeze-20260508-01.zip
```

当前门禁状态：

```text
MALF day bounded proof 已通过 -> Alpha freeze review 已通过 -> Alpha bounded proof 已通过 -> Signal freeze review 已通过 -> Signal bounded proof 已通过 -> Position freeze review 已阻塞
-> Data legacy formal promotion 已通过 -> MALF v1.4 day runtime sync implementation 已通过 -> Position freeze review reentry 已通过 -> upstream pre-position completeness synthesis 已完成
-> data reference target maintenance scope 已通过 -> data reference target maintenance closeout 已通过 -> MALF week bounded proof build 已通过 -> MALF month bounded proof build 已通过 -> Alpha production builder hardening 已通过 -> Signal production builder hardening 已通过 -> upstream pre-position release decision 已通过 -> Position bounded proof 已通过 -> Portfolio Plan freeze review 已通过 -> Portfolio Plan bounded proof 已通过 -> Trade freeze review 已通过 -> Trade bounded proof build 已通过 -> System Readout freeze review 已通过 -> System Readout bounded proof build 已通过 -> Pipeline freeze review 已通过 -> Pipeline full-chain bounded proof authorization scope freeze 已通过
```

Data Foundation 已完成首轮 `stock / backward / day-week-month` legacy formal promotion，
并完成 Data 生产级地基闭环：四个正式库作为本版全量底座，`analysis_price_line=backward`
用于结构分析，`execution_price_line=none` 已在 `market_base_day.duckdb` 中正式物化，
用于未来成交/现金语义；`market_meta.duckdb` 已完成最小可审计正式化，覆盖交易日历、
标的主数据、源代码别名、观测宇宙、执行价线可交易事实，并已部分释放可匹配正式
Data 标的的申万 2021 当前行业快照；`data-foundation-production-baseline-seal-20260502-01`
已将 Data 标为主线输入底座封版，后续 Data 只能通过 maintenance card 扩展；ST、停牌、
真实上市/退市状态与历史行业沿革仍是参考源缺口；
MALF v1.4 authority package 已形成，补足 Core operational boundary rules；
当前 runtime evidence 已升级为 MALF v1.4 day runtime sync implementation closeout。
MALF day 只消费 `analysis_price_line=backward` 的正式 Data 输入；`execution_price_line=none`
仍保留给未来成交/现金语义，不得混入 MALF day Core。Data reference target maintenance
scope 已冻结并已由 closeout 闭环：ST、停牌、真实上市/退市生命周期、历史行业 coverage decision 与
index/block source inventory 均已完成 source inventory 裁决；由于无 approved source manifest，本轮不释放新增
reference facts，缺口显式 retained。week/month execution price line
不作为 MALF week/month 前置必补，继续保留给未来执行语义卡。MALF week/month bounded proof
和 Alpha / Signal production builder hardening 已通过，upstream pre-position release decision 与
Position bounded proof 已通过；Portfolio Plan freeze review 与 Portfolio Plan bounded proof 已通过；
Trade freeze review 与 Trade bounded proof build 已通过，Trade 六件套已冻结；System Readout freeze review
与 System Readout bounded proof build 也已通过，System Readout 六件套已落为只读 bounded proof 表面；
Pipeline build/runtime authorization scope freeze、
`pipeline-single-module-orchestration-build-card-20260508-01` 与
`pipeline-full-chain-dry-run-authorization-scope-freeze-20260508-01` 与
`pipeline-full-chain-dry-run-card-20260508-01` 已通过；`pipeline.duckdb`、
`src\asteria\pipeline` 与 `scripts\pipeline` 已创建，并已记录 `system_readout` 单模块 orchestration
surface 与 full-chain day dry-run orchestration ledger；但这仍不授权 Trade full build、
Portfolio Plan full build、Position full build、System full build 或 full-chain bounded proof。
MALF month bounded proof 只放行 month Core/Lifespan/Service 三个 bounded runtime proof 正式库，不等于 MALF full build。
Signal production builder hardening 只放行 day/week/month formal signal ledger 的 production builder 表面。
Position bounded proof 只放行 day bounded position candidate / entry plan / exit plan 表面。
Portfolio Plan bounded proof 只放行 day portfolio admission / target exposure / trim 表面。
Trade freeze review 与 Trade bounded proof build 已放行 Trade design / schema / runner / audit / bounded proof
表面，`trade.duckdb` 已创建并保留 `fill_ledger` retained gap；真实 fill rows 仍必须等待 evidence-backed
execution / fill source。System Readout freeze review 与 System Readout bounded proof build 已放行
System Readout design / schema / runner / audit / bounded proof 表面，`system.duckdb`、
`src\asteria\system_readout` 与 `scripts\system_readout` 已创建；但这仍只覆盖 day bounded proof，
不等于 System full build。Pipeline freeze review 只冻结了文档合同面；随后
`pipeline-single-module-orchestration-build-card-20260508-01` 已补齐最小 runtime 证据，
`pipeline-full-chain-dry-run-card-20260508-01` 也已补齐 full-chain day dry-run runtime 证据；
`pipeline-full-chain-bounded-proof-build-card-20260508-01` 与其 closeout 已证明 full-chain day bounded proof passed；
`pipeline-one-year-strategy-behavior-replay-build-card-20260508-01` 已真实执行但因 `2024` 完整自然年覆盖不足
truthful blocked。随后 `pipeline-year-replay-coverage-gap-diagnosis-and-repair-scope-freeze-20260509-01`
已完成 formal read-only diagnosis，确认最早 released surface break 在 MALF；当前唯一 prepared next card 是
`malf-2024-natural-year-coverage-repair-card-20260509-01`，只允许最小 MALF released day surface repair，
不得解释成 year replay rerun、full rebuild、daily incremental、resume/idempotence 或 `v1 complete` 授权。
仍不能宣称全主线数据已经齐全或完整证券主数据已齐。

## 阅读入口

1. [重构总纲](docs/00-governance/00-asteria-refactor-charter-v1.md)
2. [重构来路与决策链](docs/00-governance/01-asteria-refactor-origin-trace-v1.md)
3. [当前系统清单](docs/00-governance/02-current-system-inventory-v1.md)
4. [Data 卡后 MALF 重跑判定口径](docs/00-governance/03-data-to-malf-rerun-decision-rule-v1.md)
5. [数据库分批补数与断点构建准则](docs/00-governance/04-database-build-runner-standard-v1.md)
6. [主线模块完成度缺口审计](docs/00-governance/05-mainline-module-completion-gap-audit-v1.md)
7. [主线模块权威图](docs/01-architecture/00-mainline-authoritative-map-v1.md)
8. [数据库拓扑](docs/01-architecture/01-database-topology-v1.md)
9. [模块设计文档标准](docs/02-modules/00-module-design-document-standard-v1.md)
10. [模块门禁账本](docs/03-refactor/00-module-gate-ledger-v1.md)
11. [全系统路线图 / 后半场修补阶段](docs/03-refactor/04-asteria-full-system-roadmap-v1.md)
12. [执行卡记录区](docs/04-execution/README.md)

## Python 环境

首选本地虚拟环境：

```powershell
D:\miniconda\py310\python.exe -m venv H:\Asteria\.venv
H:\Asteria\.venv\Scripts\python.exe -m pip install --upgrade pip
H:\Asteria\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

可选 conda 环境：

```powershell
D:\miniconda\py310\Scripts\conda.exe env create -f environment.yml
```

## 开发检查

```powershell
H:\Asteria\.venv\Scripts\python.exe scripts\dev\doctor.py
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py
H:\Asteria\.venv\Scripts\ruff.exe check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\ruff.exe format --check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\mypy.exe src --cache-dir H:\Asteria-temp\mypy-cache
H:\Asteria\.venv\Scripts\pytest.exe --basetemp=H:/Asteria-temp/pytest-tmp-<run_id> -o cache_dir=H:/Asteria-temp/pytest-cache-<run_id>
```
