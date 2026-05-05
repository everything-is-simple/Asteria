# Asteria Database Build Runner Standard v1

日期：2026-05-06

状态：project-level build runner standard / MALF day sample implementation

## 1. Purpose

本准则定义 Asteria 所有正式 DuckDB 建库、补数、增量更新和断点续跑工具必须遵守的项目级规则。

核心裁决：

```text
正式库不能靠一次性全量豪赌维护。
所有正式 DB builder 都必须支持分批、可恢复、可审计、可重放。
```

本准则不打开任何尚未通过门禁的模块施工，也不打开 Pipeline runtime。

## 2. Required Modes

所有正式 DB builder 必须支持：

| mode | 要求 |
|---|---|
| `bounded` | 小范围样本构建，用于 proof 和回归验证 |
| `segmented` | 按日期、symbol、batch 或模块 scope 分批构建 |
| `full` | 全量构建，只能在对应 gate 允许后执行 |
| `resume` | 从 checkpoint 或 batch ledger 继续未完成批次 |
| `audit-only` | 只读审计，不写业务事实 |

Data/MALF 这类事实库还必须支持：

| mode | 要求 |
|---|---|
| `daily_incremental` | 根据 source manifest、dirty scope 或 replay scope 识别需要重算的范围 |

## 3. Scope Rules

所有 builder 必须区分：

| scope | 含义 |
|---|---|
| `target_scope` | 用户要求补齐或发布的日期范围，例如 year/month/day |
| `compute_scope` | 为了正确计算 target 输出所需读取和重放的范围 |

用户可以指定：

```text
--year
--year --month
--date
--start-dt --end-dt
```

对 MALF、Alpha、Signal、Position 等依赖历史状态的模块，不得把 `target_scope.start_dt`
直接当成语义计算起点。除非存在已审计的状态 checkpoint，否则 `compute_scope` 必须覆盖足够历史，
再只把 `target_scope` 内的正式结果 promote。

## 4. Batch Rules

所有 builder 必须支持至少一种 symbol 或业务 scope 分批方式：

```text
--symbols-file
--symbol-start / --symbol-end
--batch-size
```

推荐默认：

```text
batch_size = 100
```

全市场长任务可以调小到 `20` 或 `50`，以降低单批失败和重跑成本。

## 5. Staging And Promote

正式写入必须遵守：

```text
stage -> audit -> promote
```

路径固定：

| 用途 | 路径 |
|---|---|
| formal DB | `H:\Asteria-data\*.duckdb` |
| staging DB | `H:\Asteria-temp\<module>\<run_id>\<batch_id>\*.duckdb` |
| report | `H:\Asteria-report\<module>\<date>\...` |
| validated evidence | `H:\Asteria-Validated\...` |

禁止：

```text
直接把半成品 batch 写入 formal DB。
失败 batch 污染 formal DB。
把 H:\Asteria-Validated 当 scratch/temp 目录。
```

Promote 只能在 hard audit 通过后执行。正式替换必须按模块登记的 natural key 或 replay scope
删除再插入。`run_id` 只用于审计、血缘和 checkpoint，不得成为业务事实主键。

## 6. Required Artifacts

每次分批构建必须生成：

| artifact | 位置 |
|---|---|
| `build-manifest.json` | `H:\Asteria-temp\<module>\<run_id>\` |
| `batch-ledger.jsonl` | `H:\Asteria-temp\<module>\<run_id>\` |
| `checkpoint.json` | `H:\Asteria-temp\<module>\<run_id>\` |
| audit summary | `H:\Asteria-report\<module>\<date>\` |

`batch-ledger` 的状态至少包括：

```text
running
failed
promoted
```

`resume` 必须跳过 `promoted` batch，重跑 `failed` 或未完成 batch。

## 7. MALF Day Sample Implementation

当前样板实现：

```text
scripts/malf/run_malf_day_supplemental_build.py
```

该工具只覆盖 MALF day，不打开 week/month。它按 symbol batch 创建 staging 三库，顺序执行：

```text
core -> lifespan -> service -> audit -> promote
```

MALF day 读取面保持：

```text
market_base_day.market_base_bar
timeframe = day
price_line = analysis_price_line
adj_mode = backward
```

MALF 特别规则：

```text
target_scope = 用户要求补的 year/month/day/date range
compute_scope = 默认从该 symbol 可用最早 day bar 算到 target_scope.end_dt
```

未来只有在出现已审计的 `malf_core_state_checkpoint` 后，才允许从 checkpoint 之后计算。

## 8. Non-Goals

本准则不声明：

```text
Pipeline runtime 已打开
MALF week/month proof 已执行
Alpha/Signal full build 已打开
Position 或下游施工已授权
所有 25 个 DB builder 已一次性实现完成
```

它只把所有未来 DB builder 必须遵守的建库纪律钉住，并用 MALF day 提供第一套可执行样板。
