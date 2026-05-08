# Pipeline Database Schema Spec v1

日期：2026-04-29

状态：frozen / freeze review passed / single-module orchestration build passed / full-chain dry-run passed / full-chain bounded proof authorization scope freeze passed / bounded proof prepared

## 1. 规格范围

当前正式 schema 已落地到：

```text
H:\Asteria-data\pipeline.duckdb
```

当前覆盖 `system_readout` 单模块编排元数据与 full-chain day dry-run 编排元数据。

## 2. 表族

| 表 | 自然键 | 说明 |
|---|---|---|
| `pipeline_run` | `pipeline_run_id` | 编排运行记录 |
| `pipeline_step_run` | `pipeline_run_id + step_seq` | 单步运行记录 |
| `module_gate_snapshot` | `pipeline_run_id + module_name + gate_name` | 门禁快照 |
| `build_manifest` | `pipeline_run_id + artifact_name + artifact_role` | 构建清单 |
| `pipeline_audit` | `audit_id` | Pipeline 审计 |

## 3. pipeline_run

| 字段 | 说明 |
|---|---|
| `pipeline_run_id` | 主体 id |
| `runner_name` | runner 标识 |
| `module_scope` | 当前允许 `system_readout` 或 `full_chain_day` |
| `run_mode` | 当前允许 `bounded / dry-run / resume / audit-only`，并受 scope 约束 |
| `run_status` | `staged / completed / failed` |
| `source_module` | 当前为 `system_readout` |
| `source_release_version` | 来源 release run id |
| `source_db` | 来源 DB 路径 |
| `step_count` | 步骤数 |
| `gate_snapshot_count` | 快照行数 |
| `manifest_count` | manifest 行数 |
| `audit_count` | 审计行数 |
| `schema_version` | schema 版本 |
| `pipeline_version` | runner 版本 |
| `gate_registry_version` | 门禁版本 |
| `created_at` | 创建时间 |

## 4. pipeline_step_run

| 字段 | 说明 |
|---|---|
| `pipeline_step_run_id` | 主体 id |
| `pipeline_run_id` | run id |
| `step_seq` | 单模块为 `1`；full-chain dry-run 为 `1..7` |
| `module_name` | 单模块为 `system_readout`；full-chain 为主线模块顺序名 |
| `step_name` | 单模块为 `single_module_orchestration`；full-chain 为 `full_chain_dry_run` |
| `step_status` | `staged / promoted` |
| `source_db` | 来源 DB |
| `source_run_id` | 来源 system run id |
| `source_release_version` | release run id |
| `started_at` | 开始时间 |
| `completed_at` | 完成时间 |
| `created_at` | 创建时间 |

## 5. module_gate_snapshot

| 字段 | 说明 |
|---|---|
| `gate_snapshot_id` | 主体 id |
| `pipeline_run_id` | run id |
| `module_name` | `registry / pipeline / released chain modules` |
| `gate_name` | 快照字段名 |
| `gate_value` | 快照字段值 |
| `source_registry_version` | registry 版本 |
| `created_at` | 创建时间 |

## 6. build_manifest

| 字段 | 说明 |
|---|---|
| `manifest_entry_id` | 主体 id |
| `pipeline_run_id` | run id |
| `artifact_name` | artifact 名 |
| `artifact_role` | `source_db / target_db / gate_registry / runtime_manifest / step_checkpoint` |
| `artifact_path` | artifact 路径 |
| `source_ref` | 来源引用 |
| `source_type` | `database / toml / json` |
| `checksum_hint` | 当前保留为空字符串 |
| `created_at` | 创建时间 |

## 7. pipeline_audit

| 字段 | 说明 |
|---|---|
| `audit_id` | 审计 id |
| `run_id` | Pipeline run |
| `check_name` | 检查项 |
| `severity` | 当前为 `hard` |
| `status` | `pass / fail` |
| `failed_count` | 失败行数 |
| `sample_payload` | 样例 |
| `created_at` | 创建时间 |

## 8. 写入裁决

| 规则 | 裁决 |
|---|---|
| 正式 DB 路径 | `H:\Asteria-data` |
| working DB 路径 | `H:\Asteria-temp\pipeline\<run_id>\` |
| promote | staging 审计通过后执行 |
| current released scope | `system_readout` single-module orchestration + `full_chain_day` dry-run |
| full-chain bounded proof 扩权 | 已准备独立 build card / 仍未执行 |
