# Asteria 历史总账与增量构建协议 v1

日期：2026-04-28

状态：active / architecture-protocol

## 1. 目标

本协议把 Asteria 的多 DuckDB 拓扑统一为一个逻辑历史总账。

```text
physical DBs stay modular
logical history is connected by source manifest, run ledger, checkpoint, audit
```

它不合并模块 DB，不改变主线依赖方向，也不授权下游模块越过当前门禁施工。

机器可读治理入口：

```text
governance/historical_ledger_registry.toml
governance/database_topology_registry.toml
governance/module_api_contracts/*.toml
```

这些 registry 是本协议的执行面。文档说明原则，registry 负责让
`check_project_governance.py` 能够阻断错误数据源、未登记 DB、缺少 checkpoint
策略和越权主线穿透。

## 2. 当前数据来源

| 来源 | 路径 | 用途 |
|---|---|---|
| TDX 离线原始行情 | `H:\tdx_offline_Data` | Data Foundation raw bootstrap 的优先输入 |
| 老 raw/base 库 | `H:\Lifespan-data\raw\raw_market.duckdb`、`H:\Lifespan-data\base\market_base.duckdb` | 只读覆盖率、字段映射、行数和缺口对账 |
| 老下游库 | `H:\Lifespan-data\astock_lifespan_alpha\...` | 历史旁证、回归样本、工程经验，不直接迁入新主线 |

正式 Asteria DuckDB 仍只能写入：

```text
H:\Asteria-data
```

## 3. Data bootstrap 路径

```mermaid
flowchart TD
    TDX[H:\tdx_offline_Data txt] --> RAW[raw_market.duckdb]
    RAW --> BASE[market_base_day.duckdb]
    LEGACY[H:\Lifespan-data raw/base] -.read-only audit.-> RAW
    LEGACY -.read-only audit.-> BASE
    BASE --> MALF[MALF day bounded proof]
```

首轮 MALF day 默认只消费：

```text
stock-day\Backward-Adjusted -> analysis_price_line
```

`Non-Adjusted` 保留给未来 Trade execution price line，`Forward-Adjusted` 暂作审计备用价格线。

## 4. 分批初始化

初始化必须支持两类分片：

| 分片 | 用途 |
|---|---|
| 日期窗口 | 一批处理几年，例如 `2010-01-01` 到 `2013-12-31` |
| symbol batch | 一批处理几百只标的 |

默认策略：

```text
time-window first
symbol bucket second
```

也就是说，全量初始化优先按 2-3 年日期窗口切批；若单批仍然过重，再在该日期窗口内按
symbol bucket 分桶。这样历史重放、断点续跑和每日增量都可以沿用同一套
`checkpoint + replay_scope` 语义。

每个 batch 必须产生：

```text
run ledger
source manifest
checkpoint
dirty or replay scope
audit summary
```

## 5. 每日增量

每日增量统一按以下顺序穿透：

```mermaid
flowchart TD
    A[scan TDX mtime/hash] --> B[raw source registry]
    B --> C[raw_market_bar]
    C --> D[market_base_dirty_scope]
    D --> E[market_base_day affected rebuild]
    E --> F[MALF day replay scope]
    F --> G[released downstream modules]
    G --> H[pipeline manifest]
```

Pipeline 只能记录 run、step、manifest 和 gate snapshot，不得定义业务字段或绕过模块门禁。

每日增量的治理边界：

| 事项 | 裁决 |
|---|---|
| 数据入口 | 只能从 TDX source scan/hash 进入新 `raw_market` |
| 旧 raw/base | 只读覆盖率、字段映射、行数和缺口对账 |
| 旧下游库 | 只做旁证和回归样本，不得作为 official input |
| mock 数据 | 只能用于单测和 contract test，不得进入 `H:\Asteria-data` |
| 穿透范围 | 只能穿透已 released 或当前 active-allowed 的模块 |
| Pipeline | 当前只定义协议；runtime 必须等 MALF bounded proof gate 后再冻结 |

## 6. 最小可执行入口

当前落地的最小入口是：

```powershell
H:\Asteria\.venv\Scripts\python.exe scripts\data\run_data_bootstrap.py `
  --source-root H:\tdx_offline_Data `
  --asset-type stock `
  --adj-mode backward `
  --mode bounded `
  --run-id data-bootstrap-bounded-001 `
  --symbol-limit 10
```

测试和排练可显式把 `--target-root` 指向 `H:\Asteria-temp\...`。正式构建才使用默认 `H:\Asteria-data`。

## 7. 禁止项

| 禁止项 | 裁决 |
|---|---|
| 把 `H:\Lifespan-data\astock_lifespan_alpha` 直接复制成新正式库 | 禁止 |
| MALF runner 直接读取 TDX txt 或旧 `malf_day.duckdb` | 禁止 |
| Alpha / Signal / Position / Portfolio / Trade / System 写回 MALF | 禁止 |
| Pipeline 定义业务语义 | 禁止 |
| 临时 DB、checkpoint、报告写入 repo 根目录 | 禁止 |

## 8. 总账接入硬要求

每个正式 DuckDB 必须在 `governance/database_topology_registry.toml` 中声明：

```text
db_name
module_id
grain
ledger_role
writer
allowed_modes
checkpoint_policy
checkpoint_key
replay_scope
promote_rule
```

每个模块必须在 `governance/module_api_contracts/` 中声明 official inputs、official
outputs、public fields、natural keys、version fields、forbidden inputs 和 forbidden outputs。
下游只能消费 official outputs，不得读取内部表重建上游语义。
