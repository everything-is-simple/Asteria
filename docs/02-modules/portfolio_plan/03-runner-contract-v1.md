# Portfolio Plan Runner Contract v1

日期：2026-04-27

状态：frozen / freeze review passed / build not executed

## 1. Runner 目标

Portfolio Plan runner 负责在 Position released 之后，读取 position candidate / entry plan / exit plan，构建组合准入、约束、目标暴露和裁剪账本，并执行边界与一致性审计。

本文件已冻结 runner contract；本次 freeze review 不创建代码文件。

## 2. 前置门槛

所有 Portfolio Plan runner 必须在运行前验证：

```text
Position bounded proof passed
```

缺少 Position release evidence、缺少 position 输出、或 Position hard audit 未通过时，runner 必须拒绝正式 build。

## 3. Runner 列表

| Runner | 职责 |
|---|---|
| `scripts/portfolio_plan/run_portfolio_plan_build.py` | 构建 position snapshot / constraints / admission / target exposure / trim |
| `scripts/portfolio_plan/run_portfolio_plan_audit.py` | 执行 Portfolio Plan 输入、输出、边界审计 |
| `scripts/portfolio_plan/run_portfolio_plan_bounded_proof.py` | 编排 Portfolio Plan bounded proof |

这些 runner 在本次 freeze review 中不创建代码文件；后续 bounded proof build card
执行时才允许创建最小 runner 表面。

## 4. 构建顺序

```mermaid
flowchart TD
    A[Validate Position release] --> B[Load bounded position candidates]
    B --> C[Write portfolio position snapshot]
    C --> D[Load portfolio constraints]
    D --> E[Run admission and exposure planning]
    E --> F[Write staging admission / target / trim]
    F --> G[Run portfolio plan audit]
    G --> H[Promote portfolio plan DB]
    H --> I[Write Portfolio Plan bounded proof evidence]
```

## 5. 运行模式

| 模式 | 要求 |
|---|---|
| `bounded` | 必须传 `start_dt / end_dt` 或 `symbol_limit` |
| `segmented` | 必须传 symbol range、batch id 或 timeframe |
| `full` | 只能在 bounded proof 通过后开启 |
| `resume` | 必须读取 checkpoint |
| `audit-only` | 不写业务表，只写 audit 或报告 |

## 6. 公共参数

| 参数 | 要求 |
|---|---|
| `--timeframe` | 第一阶段固定为 `day` |
| `--mode` | `bounded / segmented / full / resume / audit-only` |
| `--run-id` | 可传入；未传入时由 runner 生成 |
| `--source-position-db` | Position DB 路径 |
| `--target-portfolio-plan-db` | Portfolio Plan 目标 DB 路径 |
| `--start-dt` | bounded 可选条件 |
| `--end-dt` | bounded 可选条件 |
| `--symbol-limit` | bounded 可选条件 |
| `--schema-version` | 必填 |
| `--portfolio-plan-rule-version` | 必填 |
| `--source-position-release-version` | 必填 |

## 7. 幂等与断点

| 规则 | 裁决 |
|---|---|
| 同一 run 重跑 | 必须可识别并拒绝重复 promote |
| bounded 重算 | 允许覆盖同 scope staging |
| promote | 只能在审计通过后执行 |
| checkpoint | 存放在 `H:\Asteria-temp\portfolio_plan\<run_id>\` |
| 失败恢复 | resume 必须从 checkpoint 或 staging 状态恢复 |
| source lock | 必须记录 source Position release version |

## 8. 输出证据

每个 runner 必须产生：

| 证据 | 位置 |
|---|---|
| run ledger | `portfolio_plan.duckdb` |
| input snapshot | `portfolio_plan.duckdb` |
| audit report | `H:\Asteria-report\portfolio_plan\<date>\` |
| release evidence | `H:\Asteria-Validated\` |

正式证据不得写入 repo 根目录。

## 9. 禁止行为

| 行为 | 裁决 |
|---|---|
| 修改 Position DB | 禁止 |
| 直接读取 Signal / Alpha / MALF 形成 portfolio plan | 禁止 |
| 创建 Trade DB | 禁止 |
| 写入 order / execution / fill 字段 | 禁止 |
| 绕过 Position release gate 启动 full build | 禁止 |
