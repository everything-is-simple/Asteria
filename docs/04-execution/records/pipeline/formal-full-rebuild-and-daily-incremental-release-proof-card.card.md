# Formal Full Rebuild And Daily Incremental Release Proof Card

日期：2026-05-12

状态：`blocked / runner surface missing`

## 1. 目标

接住 `full-rebuild-and-daily-incremental-release-closeout-card` 的 blocked 结论，补齐正式 release 证据面。

本卡只允许证明四类事实：

- formal full rebuild proof
- daily incremental release proof
- resume/idempotence proof
- final release evidence

## 2. 允许动作

- 允许在显式 `--allow-formal-data-write` 下通过 staging、backup、audit、promote 路径写入 `H:\Asteria-data`。
- 允许生成 DB manifest、schema versions、rule versions、row counts、audit summaries、known limits。
- 允许在 proof surface 缺失时 truthful blocked。

## 3. 仍然禁止

| forbidden | decision |
|---|---|
| 无显式 allow flag 写 `H:\Asteria-data` | 禁止 |
| 用 Pipeline orchestration/sample proof 替代 formal rebuild proof | 禁止 |
| 做 Pipeline semantic repair | 禁止 |
| 重定义 Data/MALF/Alpha/Signal/Position/Portfolio Plan/Trade/System 语义 | 禁止 |
| 宣称 System full build 或 `v1 complete` | 禁止 |

## 4. 当前执行结果

本卡的 guarded proof runner 与 CLI 已落地，但当前正式 release-grade full rebuild / daily incremental runner surface 尚未全部形成。

因此本卡当前结论保持 `blocked / runner surface missing`。只有四类证据全部真实通过后，下一张才可能进入 final release closeout / `v1 complete` 裁决。
