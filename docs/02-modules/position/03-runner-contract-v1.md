# Position Runner Contract v1

日期：2026-04-27

状态：freeze review passed / design contract frozen / build not executed

## 1. Runner 目标

Position runner 负责在 Signal released 之后，读取 formal signal，构建 position candidate / entry plan / exit plan，并执行边界与一致性审计。

本文件已由 `position-freeze-review-reentry-20260430-01` 只读评审冻结为未来
Position bounded proof runner 合同。本次不创建任何代码文件。

## 2. 前置门槛

所有 Position runner 必须在运行前验证：

```text
Signal released
```

缺少 Signal release evidence、缺少 formal signal 输出、或 Signal hard audit 未通过时，runner 必须拒绝正式 build。

## 3. Runner 列表

| Runner | 职责 |
|---|---|
| `scripts/position/run_position_build.py` | 构建 signal snapshot / candidate / entry plan / exit plan |
| `scripts/position/run_position_audit.py` | 执行 Position 输入、输出、边界审计 |
| `scripts/position/run_position_bounded_proof.py` | 编排 Position bounded proof |

这些 runner 在本次 freeze review re-entry 中不创建代码文件；只有后续 bounded proof
build card 明确执行时才可创建。

## 4. 构建顺序

```mermaid
flowchart TD
    A[Validate Signal release] --> B[Load bounded formal signals]
    B --> C[Write position signal snapshot]
    C --> D[Run position interpretation]
    D --> E[Write staging candidate / entry / exit]
    E --> F[Run position audit]
    F --> G[Promote position DB]
    G --> H[Write Position bounded proof evidence]
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
| `--source-signal-db` | Signal DB 路径 |
| `--target-position-db` | Position 目标 DB 路径 |
| `--start-dt` | bounded 可选条件 |
| `--end-dt` | bounded 可选条件 |
| `--symbol-limit` | bounded 可选条件 |
| `--schema-version` | 必填 |
| `--position-rule-version` | 必填 |
| `--source-signal-release-version` | 必填 |

## 7. 幂等与断点

| 规则 | 裁决 |
|---|---|
| 同一 run 重跑 | 必须可识别并拒绝重复 promote |
| bounded 重算 | 允许覆盖同 scope staging |
| promote | 只能在审计通过后执行 |
| checkpoint | 存放在 `H:\Asteria-temp\position\<run_id>\` |
| 失败恢复 | resume 必须从 checkpoint 或 staging 状态恢复 |
| source lock | 必须记录 source Signal release version |

## 8. 输出证据

每个 runner 必须产生：

| 证据 | 位置 |
|---|---|
| run ledger | `position.duckdb` |
| input snapshot | `position.duckdb` |
| audit report | `H:\Asteria-report\position\<date>\` |
| release evidence | `H:\Asteria-Validated\` |

正式证据不得写入 repo 根目录。

## 9. 禁止行为

| 行为 | 裁决 |
|---|---|
| 修改 Signal DB | 禁止 |
| 直接读取 Alpha 或 MALF 形成 position | 禁止 |
| 创建 Portfolio Plan DB | 禁止 |
| 写入 portfolio / trade 字段 | 禁止 |
| 绕过 Signal release gate 启动 full build | 禁止 |
