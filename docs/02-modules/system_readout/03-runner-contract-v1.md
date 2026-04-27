# System Readout Runner Contract v1

日期：2026-04-27

状态：draft / pre-gate / not frozen

## 1. Runner 目标

System Readout runner 负责在 Trade released 之后，只读全链路正式账本，构建 source manifest、module status snapshot、chain readout、summary snapshot 和 audit snapshot。

在 System Readout 设计冻结前，本文件只冻结草案方向，不要求创建代码文件。

## 2. 前置门槛

所有 System Readout runner 必须在运行前验证：

```text
Trade released
```

缺少 Trade release evidence、缺少任一上游 release evidence、或上游 hard audit 未通过时，runner 必须拒绝正式 build。

## 3. Runner 列表

| Runner | 职责 |
|---|---|
| `scripts/system_readout/run_system_readout_build.py` | 构建 source manifest / status snapshot / readout / summary |
| `scripts/system_readout/run_system_readout_audit.py` | 执行只读边界、source trace、状态边界审计 |
| `scripts/system_readout/run_system_readout_bounded_proof.py` | 编排 System Readout bounded proof |

这些 runner 在 pre-gate draft 阶段不创建代码文件。

## 4. 构建顺序

```mermaid
flowchart TD
    A[Validate Trade and chain release] --> B[Load source manifests]
    B --> C[Write system source manifest]
    C --> D[Write module status snapshot]
    D --> E[Build chain readout]
    E --> F[Build summary and audit snapshots]
    F --> G[Run system readout audit]
    G --> H[Promote system DB]
    H --> I[Write System Readout bounded proof evidence]
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
| `--source-chain-manifest` | 全链路 source manifest |
| `--target-system-db` | System Readout 目标 DB 路径 |
| `--start-dt` | bounded 可选条件 |
| `--end-dt` | bounded 可选条件 |
| `--symbol-limit` | bounded 可选条件 |
| `--schema-version` | 必填 |
| `--system-readout-version` | 必填 |
| `--source-chain-release-version` | 必填 |

## 7. 幂等与断点

| 规则 | 裁决 |
|---|---|
| 同一 run 重跑 | 必须可识别并拒绝重复 promote |
| bounded 重算 | 允许覆盖同 scope staging |
| promote | 只能在审计通过后执行 |
| checkpoint | 存放在 `H:\Asteria-temp\system_readout\<run_id>\` |
| 失败恢复 | resume 必须从 checkpoint 或 staging 状态恢复 |
| source lock | 必须记录 source chain release version |

## 8. 输出证据

每个 runner 必须产生：

| 证据 | 位置 |
|---|---|
| run ledger | `system.duckdb` |
| source manifest | `system.duckdb` |
| audit report | `H:\Asteria-report\system_readout\<date>\` |
| release evidence | `H:\Asteria-Validated\` |

正式证据不得写入 repo 根目录。

## 9. 禁止行为

| 行为 | 裁决 |
|---|---|
| 修改任一上游业务 DB | 禁止 |
| 触发上游业务重算 | 禁止 |
| 合并 `wave_core_state` 与 `system_state` | 禁止 |
| 创建新的业务裁决表 | 禁止 |
| 绕过 Trade release gate 启动 full build | 禁止 |
