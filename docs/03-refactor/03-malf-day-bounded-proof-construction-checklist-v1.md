# MALF Day Bounded Proof Construction Checklist v1

日期：2026-04-28

状态：active

## 1. 目标

本清单用于承接已经落地的 hard governance 与 MALF bounded proof scaffold，把下一阶段施工收敛到真实可放行的 day 级 MALF bounded proof。

## 2. 已完成

| 项 | 状态 |
|---|---|
| MALF 六件套冻结 | 完成 |
| Data bounded bootstrap support | 完成 |
| 机器可读治理 registry / API contract / gate checker | 完成 |
| MALF day core / lifespan / service / audit scaffold | 完成 |

## 3. 下一阶段施工项

| 顺序 | 项 | 当前状态 | 验收口径 |
|---:|---|---|---|
| 1 | 选定 bounded sample scope | 待做 | 覆盖 alive 推进、停滞、transition、同向 new wave、反向 new wave |
| 2 | 实现 Core pivot / structure primitive | 待做 | `malf_pivot_ledger`、`malf_structure_ledger` 出现真实记录 |
| 3 | 实现 wave / break / transition / candidate | 待做 | `malf_wave_ledger`、`malf_break_ledger`、`malf_transition_ledger`、`malf_candidate_ledger` 出现真实记录 |
| 4 | 实现 Lifespan snapshot / profile | 待做 | `new_count`、`no_new_span`、`transition_span`、`life_state`、`position_quadrant` 可从真实 wave 派生 |
| 5 | 实现 Service WavePosition 发布 | 待做 | `malf_wave_position` 与 `malf_wave_position_latest` 发布真实记录 |
| 6 | 实现硬审计 SQL 与裁决 | 待做 | Core / Lifespan / Service hard audit 全部可执行 |
| 7 | 形成 report / closeout / evidence | 待做 | `H:\Asteria-report` 与 `H:\Asteria-Validated` 中有正式证据资产 |
| 8 | 通过 MALF day bounded proof gate | 待做 | 门禁账本可支持进入 Alpha freeze review |

## 4. 施工纪律

| 规则 | 裁决 |
|---|---|
| 一次只动 MALF 主线模块 | 必须 |
| Data 只作为输入地基 | 必须 |
| 不提前进入 Alpha / Signal / Position / Portfolio / Trade / System | 必须 |
| 不建立 pipeline 全链路业务运行 | 必须 |
| 每一层先 staging，再审计，再 promote | 必须 |

## 5. 当前最短路径

```text
选样本
-> 实现 Core 真实结构事实
-> 基于 Core 实现 Lifespan
-> 发布真实 WavePosition
-> 跑 hard audit
-> 落 report / evidence
```
