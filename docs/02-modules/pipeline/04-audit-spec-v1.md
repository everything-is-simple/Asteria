# Pipeline Audit Spec v1

日期：2026-04-29

状态：frozen / freeze review passed / single-module orchestration build passed / full-chain dry-run prepared

## 1. 审计目标

Pipeline 审计用于证明 Pipeline 只做编排和记录，不定义业务语义，不回写任何业务模块，并且遵守单模块施工门禁。

## 2. 当前硬审计

当前 released 审计必须覆盖：

| 检查 | 失败裁决 |
|---|---|
| `pipeline_run_mode_authorized` | hard fail |
| `pipeline_single_module_scope_only` | hard fail |
| `pipeline_gate_snapshot_traceability` | hard fail |
| `pipeline_manifest_traceability` | hard fail |
| `pipeline_required_checkpoint_present` | hard fail |
| `pipeline_only_allowed_tables_present` | hard fail |
| `pipeline_source_release_locked` | hard fail |

## 3. 边界硬规则

| 检查 | 失败裁决 |
|---|---|
| module scope 不是 `system_readout` | hard fail |
| 一个 run 同时出现多个业务模块 | hard fail |
| 试图使用 `full / segmented / daily_incremental` | hard fail |
| 缺少 required checkpoint 或 runtime manifest | hard fail |
| Pipeline 表面出现未授权表 | hard fail |

## 4. 输出语义硬规则

| 检查 | 失败裁决 |
|---|---|
| `pipeline_run` 自然键唯一 | hard fail |
| `pipeline_step_run` 自然键唯一 | hard fail |
| `module_gate_snapshot` 自然键唯一 | hard fail |
| `build_manifest` 自然键唯一 | hard fail |
| step status 冒充业务 release status | hard fail |
| gate snapshot 覆盖业务正式结论 | hard fail |

## 5. 当前裁决

当前 released 证据仍只证明 `single-module orchestration build passed`。`pipeline-full-chain-dry-run-card-20260508-01`
只是 prepared next card；任何把 prepared 状态冒充为 dry-run passed，或直接扩成 full-chain bounded proof 的行为，都应直接计为 hard fail。
