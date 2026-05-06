# Data Reference Target Maintenance Scope Record

日期：2026-05-06

## 1. 卡信息

| 项 | 值 |
|---|---|
| module | `data` |
| run_id | `data-reference-target-maintenance-scope-20260506-01` |
| result | `passed / scope frozen` |

## 2. 执行内容

1. 重读 Asteria 必读治理文件、Data 六件套、Data target completeness review、upstream synthesis 与当前修补队列。
2. 使用 `codebase-retrieval` 定位第一张修补卡、gate registry、Data 文档、governance checks 与受影响执行索引。
3. 使用 `sequential-thinking` 拆分 `bounded mainline input sufficient` 与 `final target complete`，只冻结 Data reference maintenance 范围。
4. 未修改 `H:\Asteria-data` 正式 DB，未创建 Data runner、Position runner、Position DB 或 Pipeline runtime。

## 3. Scope Freeze Matrix

| reference gap | closeout card scope | acceptance contract |
|---|---|---|
| ST 标记 | 必补，前提是存在可审计参考源 | 只能来自 approved source manifest；按 `instrument_id + trade_date + fact_name` 写入客观事实；无源则显式 blocker，不得 synthetic fill |
| 停牌 / 可交易状态 | 必补，前提是存在可审计参考源 | `has_execution_bar` 继续保留；新增停牌事实必须与交易日历、日线 execution bar 和 source manifest 可追溯 |
| 真实上市 / 退市生命周期 | 必补，前提是存在可审计参考源 | `instrument_master` 或生命周期事实必须区分 `observed in bar data` 与 `official listed/delisted truth`；未知状态保留 unknown |
| 历史行业沿革 | 必补为 source-backed coverage decision，不要求伪造全量历史 | 当前 SW2021 snapshot 继续有效；历史沿革只能从 approved source 导入；无可靠源时 closeout 需登记 retained gap |
| index / block / universe membership | 必补为 source inventory + release decision | 能证明来源和自然键的 membership 可释放；来源不明或无法追溯的 block 只能进入 audit/non-release |
| week/month execution price line | 本轮不作为 MALF week/month 前置必补；保留为 Trade/Position 执行语义前置 | MALF week/month 只消费 `analysis_price_line=backward`；week/month `execution_price_line=none` 若无正式源，不得伪造，也不得阻塞 MALF week/month bounded proof |

## 4. 硬边界

| 项 | 裁决 |
|---|---|
| Data 角色 | source facts only / not strategy module |
| Formal DB mutation | not executed by this scope card |
| Position construction | suspended |
| Pipeline runtime | not opened |
| next allowed card | `data_reference_target_maintenance_closeout` |

## 5. 验收口径

`data-reference-target-maintenance-closeout-20260506-01` 只能补本记录冻结的 reference facts、source manifest、schema/audit/tests/report evidence。若参考源缺失，closeout 必须以 blocker 或 retained gap 形式登记，不能用推断值填充正式事实。
