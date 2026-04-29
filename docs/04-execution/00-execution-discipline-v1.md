# Asteria 执行卡记录纪律 v1

日期：2026-04-29

## 1. 目的

本纪律规定 Asteria 正式执行卡在 repo 内如何形成可追溯闭环。

目标不是重复外部报告，而是让任何人只看仓库就能找到：

- 开工原因
- 执行边界
- 证据入口
- 最终结论

## 1.1 权威依据

本纪律承接以下权威资产：

- `H:\Asteria-Validated\Asteria-deep-research-report-重构系统最新剖切面研究报告-20260428.md`
- `H:\Asteria-Validated\Asteria-docs-code-20260428-214427.zip`
- `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2`
- `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2.zip`

深度研究报告要求 release evidence、manifest、checkpoint、audit、closeout 进入可恢复、
可审计链条；因此执行记录不是旁路说明，而是门禁状态的一部分。

## 2. 闭环顺序

正式执行闭环顺序固定为：

```text
card -> evidence-index -> record -> conclusion
```

顺序含义：

| 文档 | 回答的问题 |
|---|---|
| `card` | 这次为什么开工，只允许做什么 |
| `evidence-index` | 证据资产在哪，关键结果是什么 |
| `record` | 这次实际怎么执行，顺序如何 |
| `conclusion` | 最后是否通过，对门禁有什么影响 |

## 3. 完成定义

一张执行卡只有在以下条件同时满足时，才算 repo 内闭环完成：

1. 四类文档全部存在。
2. 四类文档都能追到同一个 `run_id`。
3. `evidence-index` 能指向真实存在的 `H:\Asteria-report` 或 `H:\Asteria-Validated` 资产。
4. `conclusion` 给出明确状态：`passed`、`blocked`、`superseded`、`failed` 四选一。
5. `00-conclusion-index-v1.md` 已登记该卡的结论入口。
6. 若本卡生成或引用 closeout、manifest、gate snapshot、run manifest、source manifest、
   Validated zip、正式 DB，`evidence-index` 必须登记路径；若不适用，必须写明 `not applicable`。
7. 若本卡改变门禁状态，`docs/03-refactor/00-module-gate-ledger-v1.md` 与相关 registry
   必须能反向指到本卡的 `conclusion` 和 `evidence-index`。

## 4. 组织规则

| 规则 | 要求 |
|---|---|
| 目录 | 使用 `docs/04-execution/records/<module_id>/` |
| 文件名 | 使用 `<run_id>.<doc-kind>.md` |
| 样板 | 后续卡优先复用 `templates/` |
| 资产归属 | 大资产留在仓库外；repo 内只放索引和摘要 |

## 5. 内容边界

### 5.1 `card`

必须写清：

- 背景
- `run_id`
- 输入范围
- 允许动作
- 禁止动作
- 对应的上游设计/门禁入口

### 5.2 `evidence-index`

必须写清：

- report 目录
- closeout 与 manifest
- gate snapshot / run manifest / source manifest 等 release evidence；当前卡未产出时写 `not applicable`
- validated 资产或明确未产出
- 正式 DB 路径或明确未创建
- 关键表计数
- 关键审计结果
- 本卡是否打开下一模块施工

不得把大报告全文复制进 repo。

### 5.3 `record`

必须按顺序记录：

- 执行前约束
- 关键运行步骤
- 审计结果
- promote / release 动作
- 最终验证
- 文档更新动作

### 5.4 `conclusion`

必须写清：

- 当前结论状态
- 放行范围
- 不放行范围
- 对下一张卡的影响
- 是否已经登记到 conclusion index
- 是否仍保持上游语义只读边界

## 5.5 Release Evidence 最小清单

正式 release / proof / governance closure 卡优先形成以下证据链：

| 证据 | 要求 |
|---|---|
| `report_dir` | `H:\Asteria-report\<module>\<date>\<run_id>` |
| `closeout.md` | 人类可读 closeout |
| `manifest.json` | 本轮证据资产清单 |
| `gate_snapshot` | 门禁状态快照；未产出时写 `not applicable` |
| `run_manifest` | 执行参数与输入范围；未产出时写 `not applicable` |
| `source_manifest` | 输入源与版本锚点；未产出时写 `not applicable` |
| `validated_zip` | 需要归档时放入 `H:\Asteria-Validated` |
| formal DB | 只有被门禁授权的模块可写入 `H:\Asteria-data` |

## 6. 禁止事项

| 禁止项 | 原因 |
|---|---|
| 用 `docs/03-refactor` 代替执行记录 | 门禁和执行闭环不是一回事 |
| 只贴仓库外路径，不写摘要 | 新同事无法快速判断结果 |
| 只有 record 没有 conclusion | 无法形成正式裁决 |
| 在 repo 内塞大二进制资产 | 会污染版本库 |
| 一个执行卡写多个正式结论页 | 入口会分叉 |

## 7. 与门禁关系

`docs/03-refactor/00-module-gate-ledger-v1.md` 仍然是门禁权威入口。

但任何声称“已通过 bounded proof”或“已放行”的门禁项，都必须能反向指到：

1. 对应 `conclusion`
2. 对应 `evidence-index`

否则门禁只能算“口头状态”，不能算正式可追溯状态。
