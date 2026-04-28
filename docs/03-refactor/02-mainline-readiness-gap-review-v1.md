# Asteria 主线准备度缺口审查 v1

日期：2026-04-27

## 1. 审查目的

本审查文档用于把当前 Asteria 从 `Data Foundation` 到 `System Readout`，以及 `Pipeline` 编排层的准备度一次性拉平，回答以下四个问题：

```text
文档是否齐
正式 DB 是否存在
是否允许施工
下一步是否与主线一致
```

本文件是审查产物，不改写门禁状态，不替代：

```text
docs/03-refactor/00-module-gate-ledger-v1.md
docs/02-modules/04-mainline-module-delivery-index-v1.md
```

## 2. 审查口径

本轮审查只引用当前仓库与正式目录中的现存事实：

| 证据来源 | 用途 |
|---|---|
| `docs/03-refactor/00-module-gate-ledger-v1.md` | 模块状态、施工许可、下一张施工卡 |
| `docs/02-modules/04-mainline-module-delivery-index-v1.md` | 文档交付状态与等待条件 |
| `docs/02-modules/data/` 与各模块六件套 | 判断文档是否达到当前 gate level |
| `docs/01-architecture/01-database-topology-v1.md` | 目标 DuckDB 拓扑 |
| `H:\Asteria-data` 实际目录 | 判断正式 DuckDB 是否已建 |

当前 `H:\Asteria-data` 下未发现任何 `.duckdb` 正式库，因此本审查中的 DB 状态均以本轮现场核查为准，而不是继承旧判断。

## 3. 开场判断

当前最强的一段已经很明确：`MALF` 六件套已冻结，且是唯一允许进入下一施工卡的主线模块。`Data Foundation` 已补齐 foundation six-doc draft；`Alpha / Signal / Position / Portfolio Plan / Trade / System Readout / Pipeline` 也都已经达到各自当前 gate level 所要求的 draft 文档齐套状态。

与 2026-04-27 相比，当前还有一个积极变化已经发生：机器可读治理已经落地，仓库中已存在 `governance/*.toml` registry、模块 API contract 和增强版 `check_project_governance.py`。这意味着“谁能施工、谁不能施工、哪些 DB 合法、哪些 source 合法”已经不再只是文档约束，而是脚本可检。

当前最明显的共同缺口也很明确：`H:\Asteria-data` 中还没有任何正式 DuckDB。这意味着不仅 25 个目标库未建，连 `MALF day bounded proof` 所依赖的首批正式库也尚未物理落地；同时，MALF 虽然已经出现 bounded proof scaffold，但正式结构语义和 release evidence 仍未形成。

因此本系统当前仍然被锁定在：

```text
MALF day bounded proof
```

这不是因为下游文档缺页，而是因为正式 DB、runner、bounded proof、审计证据与 release evidence 还没有发生。

## 4. 主矩阵

| 模块 | 角色定位 | 文档状态 | 文档缺口 | 目标DB | 当前DB状态 | 关键阻塞 | 下一步 |
|---|---|---|---|---|---|---|---|
| Data Foundation | 地基层 / source-fact 服务 / 非策略主线 | foundation six-doc draft / not frozen | 缺 freeze review、formal schema gate、runner 落地、build evidence。<br/>简评：当前文档齐到了 foundation draft 级别，不是“文档不全”，而是还没有进入实现与放行。 | `raw_market.duckdb`<br/>`market_meta.duckdb`<br/>`market_base_day.duckdb`<br/>`market_base_week.duckdb`<br/>`market_base_month.duckdb` | 未建 | 无正式 Data DuckDB；且当前总施工锁仍指向 MALF 主线推进。 | 保持文档为 foundation contract；等待与 `MALF day bounded proof` 直接相关的 Data 输入库进入最小建库实施。 |
| MALF | 主线结构事实 / lifespan / WavePosition 服务 | frozen | 缺 formal DB promote、正式结构语义、硬审计 evidence、release evidence。<br/>简评：runner scaffold 已出现，缺口已进一步收缩到“真正的 MALF 语义实现与放行证据”。 | `malf_core_day.duckdb`<br/>`malf_lifespan_day.duckdb`<br/>`malf_service_day.duckdb`<br/>`malf_core_week.duckdb`<br/>`malf_lifespan_week.duckdb`<br/>`malf_service_week.duckdb`<br/>`malf_core_month.duckdb`<br/>`malf_lifespan_month.duckdb`<br/>`malf_service_month.duckdb` | 未建 | `MALF day bounded proof` 仅完成 scaffold；WavePosition service 尚未 released。 | 继续 `MALF day bounded proof`：先以真实 sample scope 跑通 day 三库，再补 Core / Lifespan / Service 的正式语义与硬审计。 |
| Alpha | 机会解释层 | pre-gate six-doc draft / not frozen | 缺 design freeze review、formal schema gate、runner 落地、bounded proof、release evidence。<br/>简评：Alpha 不是文档缺页，而是被明确卡在 `MALF WavePosition service released` 之后。 | `alpha_bof.duckdb`<br/>`alpha_tst.duckdb`<br/>`alpha_pb.duckdb`<br/>`alpha_cpb.duckdb`<br/>`alpha_bpb.duckdb` | 未建 | MALF Service 未 released；Alpha 不允许提前创建正式 DB。 | 保持 pre-gate draft；等待 MALF WavePosition service released 后再做 Alpha freeze review。 |
| Signal | 正式 signal 聚合层 | pre-gate six-doc draft / not frozen | 缺 design freeze review、formal schema gate、runner 落地、bounded proof、release evidence。<br/>简评：Signal 的文档边界已经在，但其输入前提是 Alpha released，不是当前施工对象。 | `signal.duckdb` | 未建 | Alpha 未 released；Signal 不能越过上游 release 链。 | 保持 pre-gate draft；等待 Alpha released 后重审并冻结。 |
| Position | 持仓候选 / 进出场计划层 | pre-gate six-doc draft / not frozen | 缺 design freeze review、formal schema gate、runner 落地、bounded proof、release evidence。<br/>简评：Position 的职责边界已经清楚，但正式输入 `formal signal` 还不存在。 | `position.duckdb` | 未建 | Signal 未 released；Position 不允许提前建正式库。 | 保持 pre-gate draft；等待 Signal released 后重审并冻结。 |
| Portfolio Plan | 组合约束 / 准入 / 目标暴露层 | pre-gate six-doc draft / not frozen | 缺 design freeze review、formal schema gate、runner 落地、bounded proof、release evidence。<br/>简评：组合层语义已被锁在草案里，但没有上游 Position released 就不该进入实现。 | `portfolio_plan.duckdb` | 未建 | Position 未 released；当前主线不允许下游越级施工。 | 保持 pre-gate draft；等待 Position released 后重审并冻结。 |
| Trade | 订单意图 / 执行 / 成交账本层 | pre-gate six-doc draft / not frozen | 缺 design freeze review、formal schema gate、runner 落地、bounded proof、release evidence。<br/>简评：Trade 的执行边界已明确，但它必须消费已放行的 Portfolio Plan，而不是反向定义上游。 | `trade.duckdb` | 未建 | Portfolio Plan 未 released；Trade 不能提前落正式执行库。 | 保持 pre-gate draft；等待 Portfolio Plan released 后重审并冻结。 |
| System Readout | 全链路只读汇总 / 运行读出 / 审计快照层 | pre-gate six-doc draft / not frozen | 缺 design freeze review、formal schema gate、runner 落地、bounded proof、release evidence。<br/>简评：System Readout 已有完整草案，但它是读出末端，必须在 Trade released 后才有正式消费面。 | `system.duckdb` | 未建 | Trade 未 released；System Readout 不应提前建读出正式库。 | 保持 pre-gate draft；等待 Trade released 后重审并冻结。 |
| Pipeline | 编排层 / 运行记录层 / 非业务语义模块 | pre-gate six-doc draft / not frozen | 缺 design freeze review、formal schema gate、runner 落地、bounded proof、release evidence。<br/>简评：Pipeline 文档已经齐到 pre-gate，但它只负责编排与记录，不能被当作绕开主线门禁的捷径。 | `pipeline.duckdb` | 未建 | `MALF bounded proof gate` 未发生；且当前禁止建立 pipeline 全链路。 | 保持 pre-gate draft；等待 MALF bounded proof gate 后只就编排记录能力重审，不抢业务施工位。 |

## 5. 结论

### 5.1 文档准备度

从“是否已有当前 gate level 所需文档”这个角度看，当前文档准备度已经明显改善：

| 结论 | 说明 |
|---|---|
| MALF | 已冻结，可施工 |
| Data Foundation | foundation six-doc draft 已齐 |
| Alpha -> System Readout | pre-gate six-doc draft 已齐 |
| Pipeline | pre-gate six-doc draft 已齐 |

也就是说，当前主线的核心矛盾不再是“文档到处缺页”，而是“只有 MALF 到了可以从文档迈向实现的阶段”。

### 5.1.1 治理准备度

从“门禁是否机器可读”这个角度看，当前状态也已经发生变化：

| 结论 | 说明 |
|---|---|
| module gate registry | 已落地 |
| database topology registry | 已落地 |
| module API contracts | 已落地 |
| enhanced governance checker | 已落地 |

这意味着 Asteria 当前的第一主矛盾，已经从“治理有没有写出来”转成了“治理已经到位，MALF 语义 runtime 什么时候接上”。

### 5.2 数据库准备度

从“正式 DuckDB 是否已物理存在”这个角度看，当前数据库准备度仍然是：

```text
整体未建
```

`H:\Asteria-data` 本轮现场核查未发现任何正式 `.duckdb`。因此当前并不存在：

```text
Data Foundation 正式库
MALF day 三库
Alpha / Signal 正式库
Downstream 正式库
pipeline.duckdb
```

### 5.3 真实下一张施工卡

当前唯一与门禁账本、交付索引、数据库拓扑和现场目录状态同时一致的下一步仍然是：

```text
MALF day bounded proof
```

它应先解决：

| 优先项 | 内容 |
|---|---|
| 正式输入 | `market_meta.duckdb` 与 `market_base_day.duckdb` 的最小输入契约落地 |
| MALF day 三库 | `malf_core_day` / `malf_lifespan_day` / `malf_service_day` |
| runner | Core / Lifespan / Service / Audit 的最小 bounded proof runner |
| evidence | 审计与运行证据落入 `H:\Asteria-report` 或 `H:\Asteria-Validated` |

在这一步完成前，继续向 Alpha、Signal、Position、Portfolio Plan、Trade、System Readout 或 Pipeline 的正式 DB 和代码实现推进，都会与当前治理口径冲突。
