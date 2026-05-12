# Asteria Agent 规则

本仓库是 Asteria 新重构主线工作区。

修改代码前，每个 agent 必须先读：

1. `README.md`
2. `docs/00-governance/00-asteria-refactor-charter-v1.md`
3. `docs/01-architecture/00-mainline-authoritative-map-v1.md`
4. `docs/01-architecture/01-database-topology-v1.md`
5. `docs/03-refactor/00-module-gate-ledger-v1.md`
6. `docs/04-execution/00-conclusion-index-v1.md`

当前权威资产：

- `H:\Asteria-Validated\Asteria-deep-research-report-重构系统最新剖切面研究报告-20260428.md`
- `H:\Asteria-Validated\Asteria-docs-code-20260502-104932.zip`
- `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4`
- `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4.zip`
- `H:\Asteria-Validated\Asteria-data-formal-promotion-evidence-20260502-01.zip`
- `H:\Asteria-Validated\Asteria-malf-v1-3-formal-rebuild-closeout-20260502-01.zip`
- `H:\Asteria-Validated\Asteria-data-production-release-closeout-20260502-01.zip`
- `H:\Asteria-Validated\Asteria-data-execution-price-line-materialization-20260502-01.zip`
- `H:\Asteria-Validated\Asteria-data-market-meta-formalization-20260502-01.zip`
- `H:\Asteria-Validated\Asteria-data-market-meta-sw-industry-snapshot-20260502-01.zip`
- `H:\Asteria-Validated\Asteria-data-foundation-production-baseline-seal-20260502-01.zip`
- `H:\Asteria-Validated\Asteria-data-reference-target-maintenance-closeout-20260506-01.zip`
- `H:\Asteria-Validated\Asteria-malf-week-bounded-proof-build-20260506-01.zip`
- `H:\Asteria-Validated\Asteria-malf-month-bounded-proof-build-20260506-01.zip`
- `H:\Asteria-Validated\Asteria-alpha-production-builder-hardening-20260506-01.zip`
- `H:\Asteria-Validated\Asteria-signal-production-builder-hardening-20260506-01.zip`
- `H:\Asteria-Validated\Asteria-position-bounded-proof-build-card-20260506-01.zip`
- `H:\Asteria-Validated\Asteria-portfolio-plan-freeze-review-20260507-01.zip`
- `H:\Asteria-Validated\Asteria-data-ledger-daily-incremental-hardening-card-20260511-01.zip`

当前门禁：

- `MALF day bounded proof passed`
- `Alpha freeze review passed`
- `Alpha bounded proof passed`
- `Signal freeze review passed`
- `Signal bounded proof passed`
- `Position freeze review blocked`
- `MALF Lifespan dense bar snapshot resolution passed`
- `MALF complete alignment closeout passed`
- `Data legacy formal promotion passed`
- `MALF v1.3 formal-data bounded closeout passed`
- `MALF v1.4 Core operational boundary authority sync passed`
- `Data production foundation closeout passed`
- `Data execution price line materialization passed`
- `Data market meta formalization passed`
- `Data market meta SW industry snapshot passed`
- `Data foundation production baseline sealed`
- `MALF week bounded proof build passed`
- `MALF month bounded proof build passed`
- `Alpha production builder hardening passed`
- `Signal production builder hardening passed`
- `Upstream pre-position release decision passed`
- `Position bounded proof passed`
- `Portfolio Plan freeze review passed`
- `Portfolio Plan bounded proof passed`
- `Data ledger daily incremental hardening sample passed`
- `MALF daily incremental sample hardened`
- `Alpha/Signal daily incremental sample hardened`
- `Downstream daily impact schema frozen`
- `Downstream daily incremental sample hardened`
- `Pipeline full daily incremental chain proof passed`
- `Full rebuild and daily incremental release closeout blocked`
- 当前 release closeout 状态：`full_rebuild_and_daily_incremental_release_closeout_card` blocked / formal release evidence incomplete
- Data 已封为主线输入底座；后续 Data 只能通过明确 maintenance card 扩展。
- `market_meta.duckdb` 已放行最小客观事实与可匹配正式 Data 标的的申万 2021 当前行业快照；Data reference target maintenance closeout 已完成 source inventory 裁决；ST、停牌、真实上市/退市状态、历史行业沿革和 index/block membership 仍因无 approved source manifest 而 retained。
- MALF v1.4 是 Core operational boundary 权威定义升级；不等于 runtime proof passed。
- MALF v1.3 closeout 仍只放行 day Core/Lifespan/Service 的 formal-data bounded 表面；MALF week/month bounded proof、Alpha production builder hardening、Signal production builder hardening、upstream pre-position release decision、Position bounded proof、Portfolio Plan freeze review、Portfolio Plan bounded proof、Trade/System bounded proof、Pipeline year replay closeout、Stage 11 protocol、Data/MALF/Alpha/Signal/downstream daily incremental samples 与 Pipeline full daily incremental chain proof 已通过。
- Full rebuild and daily incremental release closeout 已执行但 blocked：formal full rebuild proof、daily incremental release proof、resume/idempotence release proof 与 final release evidence 尚未形成；不得宣称 full rebuild passed、daily incremental release passed、System full build 或 `v1 complete`。

硬规则：

- 目标模块设计文档冻结前，不得把 legacy code 迁入主线。
- 一次 construction turn 不得编辑多个主线模块。
- 下游模块不得重定义上游模块语义。
- 不得把 `data` 当成策略模块；它是 foundation infrastructure 和 source-fact service。
- 不得合并 `wave_core_state` 与 `system_state`。
- Alpha、Signal、Portfolio、Trade、System 不得写回 MALF。
- 正式数据库放在 `H:\Asteria-data`。
- 临时构建产物放在 `H:\Asteria-temp`。
- `H:\Asteria-Validated` 只作为 validated input/output assets，不作临时 scratch 目录。

Python 环境：

- 使用 `D:\miniconda\py310` 作为基础 Python provider。
- 优先使用 repo-local virtualenv `H:\Asteria\.venv`。
- 用 `H:\Asteria\.venv\Scripts\python.exe -m pip install -e ".[dev]"` 安装项目。
- 不得把 pytest cache、临时 DB 或 report artifacts 放在 repo root。

治理检查：

- 提交结构性变更前运行 `python scripts\governance\check_project_governance.py`。
- release gate 前运行 `ruff check . --cache-dir H:\Asteria-temp\ruff-cache`、`ruff format --check . --cache-dir H:\Asteria-temp\ruff-cache`、`mypy src --cache-dir H:\Asteria-temp\mypy-cache`，以及使用 run-scoped `H:\Asteria-temp` cache/temp 路径的 pytest。
- Python 文件应保持在 500 行以内；脚本 wrapper 应保持在 240 行以内。
- Markdown design/spec 文件应保持在 1200 行以内；超过时按模块拆分。
- 注释应解释意图、边界和不明显的不变量，避免复述代码。
