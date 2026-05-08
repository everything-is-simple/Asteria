# Pipeline Audit Spec v1

日期：2026-04-29

状态：frozen / freeze review passed / single-module orchestration build prepared / build not executed

## 1. 审计目标

Pipeline 审计用于证明 Pipeline 只做编排和记录，不定义业务语义，不回写任何业务模块，并且遵守单模块施工门禁。

## 2. 前置审计

| 检查 | 失败裁决 |
|---|---|
| Pipeline freeze review 已通过并可追溯 | hard fail |
| explicit Pipeline build/runtime card 已打开 | hard fail |
| 当前 card scope 若不是 `single-module orchestration build` | hard fail |
| 当前 active construction slot 可验证 | hard fail |
| 门禁账本可读取 | hard fail |
| Pipeline 不读取业务字段定义业务语义 | hard fail |

## 3. 编排边界硬审计

| 检查 | 失败裁决 |
|---|---|
| Pipeline 不得修改任何业务 DB | hard fail |
| Pipeline 不得把 gate 状态当作策略信号 | hard fail |
| Pipeline 不得绕过冻结直接推进下游模块 | hard fail |
| 同一 run 不得同时施工多个主线模块 | hard fail |
| build manifest 必须可追溯到 source / target | hard fail |

## 4. 输出语义硬审计

| 检查 | 失败裁决 |
|---|---|
| `pipeline_run` 自然键唯一 | hard fail |
| `pipeline_step_run` 自然键唯一 | hard fail |
| `module_gate_snapshot` 自然键唯一 | hard fail |
| `build_manifest` 自然键唯一 | hard fail |
| step status 不得冒充 module release status | hard fail |
| gate snapshot 不得覆盖业务模块正式结论 | hard fail |

## 5. 规则硬审计

| 检查 | 失败裁决 |
|---|---|
| active module lock 必须可审计 | hard fail |
| gate registry version 必须可追溯 | hard fail |
| manifest version 必须可追溯 | hard fail |
| skipped / failed step 必须记录原因 | hard fail |
| full mode 未获治理许可时不得运行 | hard fail |

当前第一张允许执行的 Pipeline card 仅限
`pipeline-single-module-orchestration-build-card-20260508-01`。任何试图把它扩成
full-chain dry-run 或 full-chain bounded run 的行为，都应直接计为 hard fail。

## 6. 软观察

| 检查 | 裁决 |
|---|---|
| skipped step 占比异常 | observe |
| failed step 占比异常 | observe |
| manifest 体积异常 | observe |
| gate snapshot 变更过于频繁 | observe |

软观察只形成报告，不自动放行或阻塞。是否阻塞由 Pipeline release review 决定。

## 7. 审计输出

审计写入：

```text
pipeline_audit
```

最小字段：

| 字段 | 说明 |
|---|---|
| `audit_id` | 审计 id |
| `run_id` | Pipeline run |
| `check_name` | 检查项 |
| `severity` | `hard / soft` |
| `status` | `pass / fail / observe` |
| `failed_count` | 失败行数 |
| `sample_payload` | 样例 |

## 8. 审计裁决

| 结果 | 裁决 |
|---|---|
| hard fail > 0 | Pipeline 不得放行 |
| hard 全 pass，soft 有 observe | 可进入人工复核 |
| hard 全 pass，soft 无阻塞 | 可形成 bounded proof evidence |

## 9. 验收样本

首轮 bounded proof 样本必须覆盖：

| 场景 | 要求 |
|---|---|
| 单模块 bounded run | 必须 |
| gate snapshot 记录 | 必须 |
| manifest 写入 | 必须 |
| skipped step | 必须 |
| failed step | 必须 |
| active module lock 检查 | 必须 |

若真实样本不足，必须补人工 fixture，但 fixture 不得引入业务语义。
