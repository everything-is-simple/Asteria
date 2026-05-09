# Pipeline Year Replay Coverage Gap Diagnosis and Repair Scope Freeze Card

日期：2026-05-09

状态：`passed`

## 1. 目标

本卡只诊断 `pipeline-one-year-strategy-behavior-replay-build-card-20260508-01`
的 `2024-01-01..2024-01-07` coverage gap 归属，并冻结下一张最小 repair card 的授权边界。

## 2. 范围

| 项 | 裁决 |
|---|---|
| card type | `diagnosis / repair scope freeze` |
| target blocker | `2024 natural year coverage gap` |
| target year | `2024` |
| read mode | `read-only audit` |
| allowed output | coverage matrix / attribution / one next-card recommendation |

## 3. 必查 coverage matrix

| 层 | 必查内容 |
|---|---|
| Data | `raw_market`、`market_base_day`、`market_meta` 是否覆盖 `2024-01-01..2024-01-07` |
| MALF | released MALF day surface 是否覆盖 `2024-01-01..2024-01-07` |
| Alpha | released Alpha day/week/month production surface 是否覆盖目标窗口 |
| Signal | released signal surface 是否覆盖目标窗口 |
| Position | position candidate / entry / exit surface 是否覆盖目标窗口 |
| Portfolio Plan | admission / target exposure / trim surface 是否覆盖目标窗口 |
| Trade | order intent / execution plan / rejection surface 是否覆盖目标窗口 |
| System Readout | `system_chain_readout` 为什么从 `2024-01-08` 开始 |
| Pipeline | replay source selection 是否正确读取 released System Readout |

## 4. 禁止扩权

| 禁止项 | 裁决 |
|---|---|
| 写 `H:\Asteria-data` | 禁止 |
| rebuild Data | 禁止 |
| rebuild MALF/Alpha/Signal/System | 禁止 |
| rerun year replay | 禁止 |
| 修改 Pipeline 业务语义 | 禁止 |
| 宣称 full build passed | 禁止 |
| 开 daily incremental / resume / v1 complete | 禁止 |

## 5. 允许的 conclusion 形态

本卡 conclusion 必须只给出一个下一步：

| 诊断结果 | 下一张卡 |
|---|---|
| Data 缺覆盖 | `data-2024-natural-year-coverage-maintenance-card-20260509-01` |
| Data 有、MALF 缺 | `malf-2024-natural-year-coverage-repair-card-20260509-01` |
| MALF 有、Alpha/Signal 缺 | `alpha-signal-2024-coverage-repair-card-20260509-01` |
| 上游都有、System Readout 缺 | `system-readout-2024-coverage-repair-card-20260509-01` |
| System 有、Pipeline 取数错 | `pipeline-year-replay-source-selection-repair-card-20260509-01` |
| 证据不足无法归因 | `coverage-gap-evidence-incomplete-closeout-card-20260509-01` |

## 6. 实际结果

本卡已正式执行，当前实际结论为：

```text
Data 2024-01-02..2024-01-05 covered
released MALF day surface starts at 2024-01-08
recommended next card = malf-2024-natural-year-coverage-repair-card-20260509-01
```
