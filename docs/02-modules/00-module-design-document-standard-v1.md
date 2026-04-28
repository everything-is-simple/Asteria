# Asteria 模块设计文档标准 v1

日期：2026-04-27

## 1. 目的

本标准规定：任何模块进入 `src/` 或正式 DuckDB 实现之前，必须先拥有可审阅、可冻结、可测试的权威设计文档。

## 2. 每个模块必须有的文档

| 顺序 | 文档 | 作用 |
|---:|---|---|
| 1 | Authority Design | 模块定义、职责边界、依赖方向、状态机 |
| 2 | Semantic Contract | 输入输出语义、字段含义、禁止表达 |
| 3 | Database Schema Spec | DB 名称、表族、自然键、索引、版本字段 |
| 4 | Runner Contract | CLI/API、build mode、checkpoint、replay、幂等 |
| 5 | Audit Spec | 硬规则、软观察、抽样查询、失败裁决 |
| 6 | Build Card | 本轮只动什么、不动什么、验收命令 |
| 7 | Evidence / Record / Conclusion | 执行证据、运行记录、放行或待修结论，统一归档到 `docs/04-execution/` |

机器可读治理层还必须为每个模块维护：

```text
governance/module_api_contracts/<module_id>.toml
```

该合同规定 official inputs、official outputs、public fields、natural keys、version
fields、run modes、resume behavior、source manifest fields、forbidden inputs 和
forbidden outputs。Markdown 六件套负责解释语义，TOML 合同负责让门禁脚本可执行。

## 3. 模块文档模板

每个模块 Authority Design 至少包含：

```text
1. 模块定义
2. 模块只回答什么
3. 模块不回答什么
4. 输入
5. 输出
6. 状态机或数据流图
7. 核心表族
8. 自然键
9. 版本字段
10. 上游依赖
11. 下游消费者
12. 不变量检查
13. 上线门禁
```

## 4. 必须画图的地方

以下内容必须有 Mermaid 图：

| 内容 | 图类型 |
|---|---|
| 模块上下游 | flowchart |
| 状态转换 | stateDiagram |
| 表关系 | erDiagram |
| 构建顺序 | flowchart |

## 5. 字段标准

正式表默认包含：

| 字段 | 要求 |
|---|---|
| `run_id` | 审计字段，不得作为业务主键唯一含义 |
| `schema_version` | 必填 |
| `rule_version` | 语义规则模块必填 |
| `sample_version` | 统计 rank/sample 模块必填 |
| `created_at` | 批量写入审计 |
| `source_*` | 跨库输入必须可追溯 |

## 5.1 总账接入标准

每个正式 DuckDB 必须在 `governance/database_topology_registry.toml` 中登记：

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

这些字段让多 DuckDB 拓扑在治理上形成一个逻辑历史总账，而不是一组不可追溯的散库。

## 6. 自然键标准

业务事实必须定义自然键。

示例：

| 模块 | 典型自然键 |
|---|---|
| market_base | `symbol + timeframe + bar_dt + price_line` |
| MALF WavePosition | `symbol + timeframe + bar_dt + service_version` |
| Alpha event | `alpha_family + symbol + timeframe + bar_dt + alpha_rule_version` |
| Signal | `symbol + signal_date + signal_rule_version` |
| Position | `symbol + signal_id + position_rule_version` |
| Trade | `order_intent_id + execution_trade_date` |

## 7. 单模块施工规则

同一轮施工只能修改：

```text
one module source
one module tests
one module docs
```

允许同时修改：

```text
shared contract tests
pipeline gate registry
README/index docs
```

但必须说明原因。

## 8. 模块放行定义

模块 `放行` 不等于永久冻结。

| 状态 | 含义 |
|---|---|
| `draft` | 设计未冻结 |
| `frozen` | 设计冻结，允许施工 |
| `building` | 正在实现 |
| `verifying` | 正在验收 |
| `released` | 本模块放行 |
| `integrated` | 下游消费已证明不破坏 |
| `blocked` | 存在阻塞 |

## 9. 执行记录归档要求

模块进入正式执行后，repo 内必须能形成可追溯的执行闭环。

正式执行记录统一放在：

```text
docs/04-execution/
```

最小闭环必须包含四类文档：

| 文档 | 作用 |
|---|---|
| `card` | 说明本次为什么开工、只动什么、不动什么 |
| `evidence-index` | 索引外部证据、关键计数、路径入口 |
| `record` | 按顺序记录本次执行经过与关键动作 |
| `conclusion` | 给出 passed / blocked / superseded / failed 结论 |

`H:\Asteria-report` 与 `H:\Asteria-Validated` 继续承载真实证据资产；repo 内执行区只负责索引、摘要、记录与结论。
