# Position Pending Module Gate v1

日期：2026-04-29

状态：superseded by freeze review reentry / build not executed

## 1. 当前裁决

Position 是 Signal 之后的主线模块。本目录曾用于登记 pre-gate 六件套 draft。当前已通过
Signal bounded proof，且 `position-freeze-review-reentry-20260430-01` 已完成 review-only
审查并通过；下一步只允许 Position bounded proof build card。

截至 2026-05-06，Position 六件套已冻结为文档合同表面，但 Position runner、正式 DB、
bounded proof 和下游施工仍未执行。Position 不得绕过 Signal 直接消费 Alpha 草案或
MALF WavePosition。

## 2. 等待条件

Position bounded proof 施工必须等待：

```text
Position bounded proof build card
```

Position bounded proof build card 执行前，不得创建 Position runner、正式 DB 或 bounded
proof 产物。

## 3. 上游依赖

Position 只能消费正式 Signal 账本，不得直接用 Alpha 草案或 MALF 字段绕过 Signal。

## 4. 禁止项

| 禁止项 | 原因 |
|---|---|
| 修改 Signal | 下游不得回写上游 |
| 重新计算 Alpha 机会 | 归属 Alpha |
| 重新解释 WavePosition | 归属 MALF |
| 决定组合资金分配 | 归属 Portfolio Plan |
| 生成实际订单 | 归属 Trade |

## 5. 已冻结的文档合同

以下文档已通过 freeze review re-entry，但只表示文档和合同冻结，不表示施工许可：

| 文档 | 状态 |
|---|---|
| `00-authority-design-v1.md` | freeze review passed / design contract frozen / build not executed |
| `01-semantic-contract-v1.md` | freeze review passed / design contract frozen / build not executed |
| `02-database-schema-spec-v1.md` | freeze review passed / design contract frozen / build not executed |
| `03-runner-contract-v1.md` | freeze review passed / design contract frozen / build not executed |
| `04-audit-spec-v1.md` | freeze review passed / design contract frozen / build not executed |
| `05-build-card-v1.md` | freeze review passed / bounded-proof card specification frozen / build not executed |

下一步只能进入 Position bounded proof build card。任何 Position full daily mainline 声明，
仍必须等待 bounded proof 和后续 release gate。
