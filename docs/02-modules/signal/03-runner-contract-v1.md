# Signal Runner Contract v1

日期：2026-04-27

状态：draft / pre-gate / not frozen

## 1. Runner 目标

Signal runner 负责在 Alpha released 之后，读取 Alpha family candidate，构建 formal signal ledger，并执行边界与一致性审计。

在 Signal 设计冻结前，本文件只冻结草案方向，不要求创建代码文件。

## 2. 前置门槛

所有 Signal runner 必须在运行前验证：

```text
Alpha released
```

缺少 Alpha release evidence、缺少 alpha family 输出、或 Alpha hard audit 未通过时，runner 必须拒绝正式 build。

## 3. Runner 列表

| Runner | 职责 |
|---|---|
| `scripts/signal/run_signal_build.py` | 构建 input snapshot / formal signal / component ledger |
| `scripts/signal/run_signal_audit.py` | 执行 Signal 输入、输出、边界审计 |
| `scripts/signal/run_signal_bounded_proof.py` | 编排 Signal bounded proof |

这些 runner 在 pre-gate draft 阶段不创建代码文件。

## 4. 构建顺序

```mermaid
flowchart TD
    A[Validate Alpha release] --> B[Load bounded alpha candidates]
    B --> C[Write signal input snapshot]
    C --> D[Run signal aggregation]
    D --> E[Write staging formal signal]
    E --> F[Run signal audit]
    F --> G[Promote signal DB]
    G --> H[Write Signal bounded proof evidence]
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
| `--source-alpha-root` | Alpha DB 根路径或 manifest |
| `--target-signal-db` | Signal 目标 DB 路径 |
| `--start-dt` | bounded 可选条件 |
| `--end-dt` | bounded 可选条件 |
| `--symbol-limit` | bounded 可选条件 |
| `--schema-version` | 必填 |
| `--signal-rule-version` | 必填 |
| `--source-alpha-release-version` | 必填 |

## 7. 幂等与断点

| 规则 | 裁决 |
|---|---|
| 同一 run 重跑 | 必须可识别并拒绝重复 promote |
| bounded 重算 | 允许覆盖同 scope staging |
| promote | 只能在审计通过后执行 |
| checkpoint | 存放在 `H:\Asteria-temp\signal\<run_id>\` |
| 失败恢复 | resume 必须从 checkpoint 或 staging 状态恢复 |
| source lock | 必须记录 source Alpha release version |

## 8. 输出证据

每个 runner 必须产生：

| 证据 | 位置 |
|---|---|
| run ledger | `signal.duckdb` |
| input snapshot | `signal.duckdb` |
| audit report | `H:\Asteria-report\signal\<date>\` |
| release evidence | `H:\Asteria-Validated\` |

正式证据不得写入 repo 根目录。

## 9. 禁止行为

| 行为 | 裁决 |
|---|---|
| 修改 Alpha DB | 禁止 |
| 直接读取 MALF 形成 formal signal | 禁止 |
| 创建 Position DB | 禁止 |
| 写入 position / portfolio / trade 字段 | 禁止 |
| 绕过 Alpha release gate 启动 full build | 禁止 |
