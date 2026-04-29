# MALF Authority Compatibility Audit Card

日期：2026-04-29

## 1. 背景

`H:\Asteria-Validated\Asteria-docs-code-20260429-130309.zip` 是三天重构成果的当前
系统 docs/code 快照。该快照需要和 MALF 终稿目录、MALF 终稿 zip 做一次不偏移审计：
确认 Asteria 只是实现和追踪 MALF 权威语义，没有改写 MALF 定义、定理或接口边界。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `governance` |
| run_id | `malf-authority-compatibility-audit-20260429-01` |
| stage | `malf-authority-compatibility-audit` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| current docs/code snapshot | `H:\Asteria-Validated\Asteria-docs-code-20260429-130309.zip` |
| MALF authority directory | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2` |
| MALF authority zip | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2.zip` |
| MALF implementation annex | `docs/02-modules/malf/06-implementation-traceability-annex-v1.md` |

## 4. 允许动作

- 登记 `Asteria-docs-code-20260429-130309.zip` 到 Validated manifest 和 repo 资产清单。
- 新增 Asteria-specific MALF implementation traceability annex。
- 记录 MALF authority compatibility audit 四件套。
- 生成 `H:\Asteria-report` closeout / manifest / compatibility summary。
- 生成 `H:\Asteria-Validated\Asteria-malf-authority-compatibility-audit-20260429-01.zip`。
- 收紧 Alpha pre-gate 文档里可能误读为当前事实的 future prerequisite wording。

## 5. 禁止动作

- 不修改 `MALF_Three_Part_Design_Set_v1_2` 目录或同名 zip 内的 MALF 终稿。
- 不打开 Alpha 代码施工，不创建 Alpha 正式 DB。
- 不新增 Signal / Position / Portfolio Plan / Trade / System / Pipeline 施工。
- 不让 Alpha 或任何下游模块写回 MALF。
- 不把本审计结论解释为 Alpha freeze review 已通过。

## 6. 兼容检查项

| 检查项 | 裁决标准 |
|---|---|
| MALF authority zip 与目录 | 四份终稿文件一致 |
| 当前 docs/code 快照 | governance / docs sync 检查可通过 |
| MALF schema 映射 | Core / Lifespan / Service / WavePosition 都有 Asteria 表字段和 runner 追踪 |
| MALF audit 映射 | transition、old_direction、no_new_span、transition_span、WavePosition 唯一性都有硬审计 |
| Alpha 边界 | Alpha 仍为 pending freeze review，不得出现正式 runner 或正式 DB create 脚本 |
| 门禁状态 | 下一动作仍为 `Alpha freeze review` |
