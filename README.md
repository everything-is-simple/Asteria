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
H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_3
H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_3.zip
H:\Asteria-Validated\Asteria-data-formal-promotion-evidence-20260502-01.zip
H:\Asteria-Validated\Asteria-malf-v1-3-formal-rebuild-closeout-20260502-01.zip
H:\Asteria-Validated\Asteria-data-production-release-closeout-20260502-01.zip
H:\Asteria-Validated\Asteria-data-execution-price-line-materialization-20260502-01.zip
H:\Asteria-Validated\Asteria-data-market-meta-formalization-20260502-01.zip
H:\Asteria-Validated\Asteria-data-market-meta-sw-industry-snapshot-20260502-01.zip
H:\Asteria-Validated\Asteria-data-foundation-production-baseline-seal-20260502-01.zip
```

当前门禁状态：

```text
MALF day bounded proof 已通过 -> Alpha freeze review 已通过 -> Alpha bounded proof 已通过 -> Signal freeze review 已通过 -> Signal bounded proof 已通过 -> Position freeze review 已阻塞
-> Data legacy formal promotion 已通过 -> MALF v1.3 formal-data bounded closeout 已通过 -> Position freeze review reentry card
```

Data Foundation 已完成首轮 `stock / backward / day-week-month` legacy formal promotion，
并完成 Data 生产级地基闭环：四个正式库作为本版全量底座，`analysis_price_line=backward`
用于结构分析，`execution_price_line=none` 已在 `market_base_day.duckdb` 中正式物化，
用于未来成交/现金语义；`market_meta.duckdb` 已完成最小可审计正式化，覆盖交易日历、
标的主数据、源代码别名、观测宇宙、执行价线可交易事实，并已部分释放可匹配正式
Data 标的的申万 2021 当前行业快照；`data-foundation-production-baseline-seal-20260502-01`
已将 Data 标为主线输入底座封版，后续 Data 只能通过 maintenance card 扩展；ST、停牌、
真实上市/退市状态与历史行业沿革仍是参考源缺口；
MALF v1.3 已用正式 Data day 输入完成 bounded formal-data closeout。当前只授权
Position freeze review reentry 的只读评审（review-only），不授权 Alpha full build、Signal
full build、Position 施工、下游施工或全链路 pipeline。MALF week/month 证明尚未执行。
仍不能宣称全主线数据已经齐全或完整证券主数据已齐。

## 阅读入口

1. [重构总纲](docs/00-governance/00-asteria-refactor-charter-v1.md)
2. [重构来路与决策链](docs/00-governance/01-asteria-refactor-origin-trace-v1.md)
3. [当前系统清单](docs/00-governance/02-current-system-inventory-v1.md)
4. [主线模块权威图](docs/01-architecture/00-mainline-authoritative-map-v1.md)
5. [数据库拓扑](docs/01-architecture/01-database-topology-v1.md)
6. [模块设计文档标准](docs/02-modules/00-module-design-document-standard-v1.md)
7. [模块门禁账本](docs/03-refactor/00-module-gate-ledger-v1.md)
8. [执行卡记录区](docs/04-execution/README.md)

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
