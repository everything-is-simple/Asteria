# Pipeline Runner Contract v1

日期：2026-04-29

状态：frozen / freeze review passed / single-module orchestration build prepared / build not executed

## 1. Runner 目标

Pipeline runner 的未来职责是在已完成 Pipeline freeze review 且后续有明确 Pipeline build/runtime card 之后，
记录单模块或受限范围内的编排运行、步骤记录、门禁快照和构建 manifest。

`pipeline-freeze-review-20260508-01` 已将本合同冻结为文档表面；本轮仍不要求创建代码文件。

## 2. 前置门槛

所有未来 Pipeline runner 必须在运行前验证：

```text
Pipeline freeze review passed
explicit Pipeline build/runtime card opened
```

缺少门禁账本、缺少最小模块运行证据、或当前施工位不允许该模块进入时，runner 必须拒绝推进编排。

当前已准备但未执行的下一张卡是 `pipeline-single-module-orchestration-build-card-20260508-01`；
除该卡未来执行外，Pipeline runner 仍不得创建。

## 3. Runner 列表

| Runner | 职责 |
|---|---|
| `scripts/pipeline/run_pipeline_record.py` | 记录 pipeline_run / pipeline_step_run / gate snapshot / manifest |
| `scripts/pipeline/run_pipeline_audit.py` | 执行 Pipeline 只编排、不定义业务语义的审计 |
| `scripts/pipeline/run_pipeline_bounded_proof.py` | 编排受限范围的 Pipeline bounded proof |

这些 runner 当前仍只保留合同占位；freeze review 不创建正式代码文件。

## 4. 构建顺序

```mermaid
flowchart TD
    A[Validate module gate and active construction slot] --> B[Create pipeline run]
    B --> C[Record module gate snapshot]
    C --> D[Record step runs]
    D --> E[Write build manifest]
    E --> F[Run pipeline audit]
    F --> G[Promote pipeline DB]
    G --> H[Write Pipeline bounded proof evidence]
```

## 5. 运行模式

| 模式 | 要求 |
|---|---|
| `bounded` | 必须限制在单模块或单批次范围 |
| `segmented` | 必须传 step range、batch id 或 module scope |
| `full` | 只能在未来独立 full-chain 授权卡通过后开启 |
| `resume` | 必须读取 checkpoint |
| `audit-only` | 不写业务表，只写 audit 或报告 |
| `daily_incremental` | 未来只记录 Data/module incremental manifest，不定义业务语义 |

## 6. 公共参数

| 参数 | 要求 |
|---|---|
| `--module-scope` | 必填，例如 `malf` |
| `--mode` | `bounded / segmented / full / resume / audit-only` |
| `--run-id` | 可传入；未传入时由 runner 生成 |
| `--gate-ledger` | 门禁账本路径 |
| `--target-pipeline-db` | Pipeline 目标 DB 路径 |
| `--step-limit` | bounded / segmented 可选条件 |
| `--schema-version` | 必填 |
| `--pipeline-version` | 必填 |
| `--gate-registry-version` | 必填 |
| `--manifest-version` | 必填 |

## 7. 幂等与断点

| 规则 | 裁决 |
|---|---|
| 同一 run 重跑 | 必须可识别并拒绝重复 promote |
| bounded 重算 | 允许覆盖同 scope staging |
| promote | 只能在审计通过后执行 |
| checkpoint | 存放在 `H:\Asteria-temp\pipeline\<run_id>\` |
| 失败恢复 | resume 必须从 checkpoint 或 staging 状态恢复 |
| active module lock | 必须验证当前施工位只允许一个主线模块 |

当前 Data Foundation 已支持自身 daily incremental 与 resume；Pipeline 仍只登记未来
编排合同，不得因此创建 `pipeline.duckdb`、single-module orchestration runtime 或全链路 runtime。

## 8. 输出证据

每个 runner 必须产生：

| 证据 | 位置 |
|---|---|
| run ledger | `pipeline.duckdb` |
| gate snapshot | `pipeline.duckdb` |
| audit report | `H:\Asteria-report\pipeline\<date>\` |
| release evidence | `H:\Asteria-Validated\` |

正式证据不得写入 repo 根目录。

## 9. 禁止行为

| 行为 | 裁决 |
|---|---|
| 绕过模块冻结直接推进下游模块 | 禁止 |
| 修改任何业务模块输出 | 禁止 |
| 在 Pipeline 中定义业务字段 | 禁止 |
| 合并模块 DB | 禁止 |
| 让一个 run 同时施工多个主线模块 | 禁止 |
