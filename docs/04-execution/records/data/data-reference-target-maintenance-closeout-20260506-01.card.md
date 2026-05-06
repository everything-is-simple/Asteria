# Data Reference Target Maintenance Closeout Card

日期：2026-05-06

状态：`passed / source inventory closed / gaps retained`

## 1. 背景

本卡承接 `data-reference-target-maintenance-scope-20260506-01`。只有范围卡明确允许
进入 Data maintenance 施工后，本卡才可执行。目标是补齐已冻结范围内的 Data reference
facts、DB 表面、审计和证据链。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `data` |
| run_id | `data-reference-target-maintenance-closeout-20260506-01` |
| stage | `maintenance-closeout / passed / no DB mutation` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| prerequisite card | `data-reference-target-maintenance-scope-20260506-01` |
| source docs | `docs/02-modules/data` |
| formal DB path | `H:\Asteria-data\market_meta.duckdb`; scoped Data DBs from the scope card |
| report path | `H:\Asteria-report\data\2026-05-06\<run_id>\` |
| temp path | `H:\Asteria-temp\data\<run_id>\` |

## 4. 权威边界

| 项 | 值 |
|---|---|
| upstream semantics | `source facts only; no Alpha/Signal/Position semantics` |
| formal DB permission | `allowed only if scope card explicitly opens maintenance build` |
| allowed next action before card | `data_reference_target_maintenance_closeout` |

## 5. 允许动作

- 按范围卡冻结的 reference facts 扩展 Data schema、runner、audit 和测试。
- 使用 staging、audit、promote、checkpoint/resume 和 source manifest 形成正式证据。
- 生成 card、record、evidence-index、conclusion、report closeout 和 validated evidence。
- 执行完成后明确是否打开 MALF week bounded proof build。

## 5.1 执行裁决

本卡已执行为 source inventory closeout。当前 repo 与正式库只证明：

- `market_meta.duckdb` 现有 released 表面 audit-only 通过。
- `meta_source_manifest` 仅覆盖 `raw_market.duckdb` 与 `market_base_day/week/month.duckdb`。
- 已批准且已导入的外部 reference source 只有申万 2021 当前行业快照。
- ST、官方停牌、真实上市/退市生命周期、历史行业沿革、index/block membership 仍无 approved source manifest。

因此本卡不修改正式 Data DB，不新增 schema、runner 或 promoted reference facts；以显式 retained gap
完成 closeout，并放行下一张 `malf-week-bounded-proof-build-20260506-01`。

## 6. 禁止动作

- 不把 Data 变成策略模块。
- 不向 MALF、Alpha、Signal 或 Position 写入业务语义。
- 不绕过 `docs/00-governance/04-database-build-runner-standard-v1.md` 手工改正式库。
- 不创建 Position、Portfolio、Trade、System 或 Pipeline 正式库。

## 7. 后续门禁

本卡通过后，才允许按顺序进入：

```text
malf-week-bounded-proof-build-20260506-01
```

## 8. 关联入口

- [Data scope card](data-reference-target-maintenance-scope-20260506-01.card.md)
- [database build runner standard](../../../00-governance/04-database-build-runner-standard-v1.md)
- [gate ledger](../../../03-refactor/00-module-gate-ledger-v1.md)
