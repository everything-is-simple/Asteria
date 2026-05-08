# System Readout Audit Spec v1

日期：2026-04-27

状态：frozen / freeze review passed / bounded proof passed / full build not executed

## 1. 审计目标

System Readout 审计用于证明 System Readout 只读消费全链路正式账本，输出仅限 readout、summary 和 audit snapshot，并且没有越界写入任何上游业务模块或触发业务重算。

## 2. 前置审计

| 检查 | 失败裁决 |
|---|---|
| Trade released | hard fail |
| 全链路 release evidence 完整 | hard fail |
| 上游 hard audit 全通过 | hard fail |
| source chain release version 已记录 | hard fail |
| System Readout 不触发上游业务重算 | hard fail |

## 3. 输入边界硬审计

| 检查 | 失败裁决 |
|---|---|
| System Readout 不得修改任一上游 DB | hard fail |
| 每个 readout 行必须能追溯到 source manifest | hard fail |
| 缺少上游来源时必须标记 `source_gap` 或 `audit_gap` | hard fail |
| System Readout 不得伪造上游正式账本行 | hard fail |
| source manifest 必须记录 schema / run / release version | hard fail |

## 4. 输出语义硬审计

| 检查 | 失败裁决 |
|---|---|
| `system_chain_readout` 自然键唯一 | hard fail |
| `system_summary_snapshot` 自然键唯一 | hard fail |
| `system_audit_snapshot` 自然键唯一 | hard fail |
| summary payload 不得作为业务权威表回写上游 | hard fail |
| readout 不得包含业务 mutation 指令 | hard fail |
| System Readout 输出不得包含新的 execution / fill | hard fail |

## 5. 状态边界硬审计

| 检查 | 失败裁决 |
|---|---|
| `wave_core_state` 与 `system_state` 不得合并 | hard fail |
| MALF 状态字段只能只读展示 | hard fail |
| Alpha / Signal / Position / Portfolio / Trade 字段含义不得重定义 | hard fail |
| partial readout 必须明确缺口原因 | hard fail |

## 6. 软观察

| 检查 | 裁决 |
|---|---|
| partial readout 占比异常 | observe |
| audit_gap 占比异常 | observe |
| 某模块 source release 落后 | observe |
| summary payload 体积异常 | observe |

软观察只形成报告，不自动放行或阻塞。是否阻塞由 System Readout freeze review、bounded
proof review 或后续 release review 决定。

## 7. 审计输出

审计写入：

```text
system_readout_audit
```

最小字段：

| 字段 | 说明 |
|---|---|
| `audit_id` | 审计 id |
| `run_id` | System Readout run |
| `check_name` | 检查项 |
| `severity` | `hard / soft` |
| `status` | `pass / fail / observe` |
| `failed_count` | 失败行数 |
| `sample_payload` | 样例 |

## 8. 审计裁决

| 结果 | 裁决 |
|---|---|
| hard fail > 0 | System Readout 不得放行 |
| hard 全 pass，soft 有 observe | 可进入人工复核 |
| hard 全 pass，soft 无阻塞 | 可通过 System Readout bounded proof gate |

## 9. 验收样本

首轮 bounded proof 样本必须覆盖：

| 场景 | 要求 |
|---|---|
| complete readout | 必须 |
| partial readout | 必须 |
| source_gap | 必须 |
| audit_gap | 必须 |
| MALF `system_state` 和 `wave_core_state` 同时展示但不合并 | 必须 |
| Trade fill / rejection 只读汇总 | 必须 |

若真实样本不足，必须补人工 fixture，但 fixture 不得改变任何上游业务语义。
