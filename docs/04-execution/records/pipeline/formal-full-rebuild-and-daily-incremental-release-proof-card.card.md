# Formal Full Rebuild And Daily Incremental Release Proof Card

日期：2026-05-12

状态：`passed / formal release evidence complete`

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

本卡已完成 source surface audit、source proof、guarded release proof 与 resume/idempotence 复跑。三项 source proof surface 指向同一个正式 DB source root，生成 `formal-release-proof-manifest.json`，并通过显式 `--allow-formal-data-write` 走完 staging rebuild、formal DB backup、audit、promote 到 `H:\Asteria-data` 的 guarded 路径。

因此本卡结论为 `passed / formal release evidence complete`。下一张只允许进入 `final_release_closeout_card` 做最终 release closeout / `v1 complete` 裁决；本卡本身仍不宣称 System full build 或 `v1 complete`。
